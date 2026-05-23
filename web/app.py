"""FastAPI application — serves both the API and the HTML frontend on one port."""

import json
from datetime import date
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from tradingagents.llm_clients.model_catalog import MODEL_OPTIONS

from .auth import SESSION_COOKIE, get_session, make_session_token
from .database import (
    add_news_event,
    create_analysis,
    create_news_analysis,
    get_all_analyses,
    get_all_news_analyses,
    get_analysis,
    get_events,
    get_news_analysis,
    get_news_events,
    get_user,
    get_user_by_id,
    init_db,
    new_analysis_id,
    update_password,
    verify_password,
)
from .runner import submit_analysis
from newsagent.llm import check_llm_connection
from newsagent.runner import submit_news_analysis

_HERE = Path(__file__).parent

app = FastAPI(title="HillTrade", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=str(_HERE / "static")), name="static")
templates = Jinja2Templates(directory=str(_HERE / "templates"))


# ── startup ───────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def _startup() -> None:
    init_db()
    import asyncio
    import logging
    log = logging.getLogger("hilltrade")
    try:
        provider = await asyncio.get_event_loop().run_in_executor(None, check_llm_connection)
        log.info("LLM connection OK — provider: %s", provider)
    except RuntimeError as exc:
        log.error("STARTUP FAILED — %s", exc)
        raise SystemExit(f"\n\n  ✗ {exc}\n") from exc


# ── auth middleware ───────────────────────────────────────────────────────────

_PUBLIC = {"/login", "/logout"}


@app.middleware("http")
async def _auth_guard(request: Request, call_next):
    path = request.url.path
    if path in _PUBLIC or path.startswith("/static"):
        return await call_next(request)
    if not get_session(request):
        return RedirectResponse(url=f"/login?next={path}", status_code=303)
    return await call_next(request)


# ── helpers ───────────────────────────────────────────────────────────────────

def _r(url: str) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=303)


def _tmpl(request: Request, name: str, ctx: dict | None = None, status_code: int = 200):
    """TemplateResponse wrapper for Starlette >= 1.0 (request is first positional arg)."""
    return templates.TemplateResponse(request, name, ctx or {}, status_code=status_code)


def _today() -> str:
    return date.today().isoformat()


_PROVIDERS = [
    ("openai",     "OpenAI"),
    ("anthropic",  "Anthropic"),
    ("google",     "Google"),
    ("xai",        "xAI"),
    ("deepseek",   "DeepSeek"),
    ("qwen",       "Qwen"),
    ("glm",        "GLM"),
    ("minimax",    "MiniMax"),
    ("openrouter", "OpenRouter"),
    ("ollama",     "Ollama"),
]
_PROVIDER_KEYS = {k for k, _ in _PROVIDERS}
_MODEL_CATALOG = {k: v for k, v in MODEL_OPTIONS.items() if k in _PROVIDER_KEYS}


# ── login / logout ────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return _r("/news")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = "", next: str = "/news"):
    if get_session(request):
        return _r("/dashboard")
    return _tmpl(request, "login.html", {"error": error, "next": next})


@app.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form(default="/news"),
):
    user = get_user(username)
    if not user or not verify_password(password, user["password_hash"]):
        return _tmpl(
            request, "login.html",
            {"error": "Invalid username or password.", "next": next},
            status_code=401,
        )
    token = make_session_token(user["id"], user["username"])
    resp  = _r(next)
    resp.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="lax", max_age=8 * 3600)
    return resp


@app.get("/logout")
@app.post("/logout")
async def logout(request: Request):
    resp = _r("/login")
    resp.delete_cookie(SESSION_COOKIE)
    return resp


# ── dashboard ─────────────────────────────────────────────────────────────────

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, msg: str = ""):
    session = get_session(request)
    return _tmpl(request, "dashboard.html", {
        "session":            session,
        "recent_analyses":    get_all_analyses(limit=8),
        "providers":          _PROVIDERS,
        "model_catalog_json": json.dumps(_MODEL_CATALOG),
        "msg":                msg,
        "today":              _today(),
    })


# ── analysis start ────────────────────────────────────────────────────────────

@app.post("/analysis/start")
async def analysis_start(request: Request):
    session = get_session(request)
    form    = await request.form()

    ticker          = (form.get("ticker") or "SPY").strip().upper()
    analysis_date   = form.get("analysis_date", _today())
    provider        = form.get("provider", "openai")
    deep_model      = form.get("deep_model", "")
    quick_model     = form.get("quick_model", "")
    research_depth  = int(form.get("research_depth", 1))
    output_language = form.get("output_language", "English")
    analysts        = form.getlist("analysts") or ["market", "social", "news", "fundamentals"]

    settings = {
        "ticker":          ticker,
        "analysis_date":   analysis_date,
        "analysts":        analysts,
        "provider":        provider,
        "deep_model":      deep_model,
        "quick_model":     quick_model,
        "research_depth":  research_depth,
        "output_language": output_language,
    }

    aid = new_analysis_id()
    create_analysis(
        analysis_id=aid,
        user_id=session["uid"],
        username=session["uname"],
        ticker=ticker,
        analysis_date=analysis_date,
        settings=settings,
    )
    submit_analysis(aid, settings)
    return _r(f"/analysis/{aid}")


# ── analysis view + polling ───────────────────────────────────────────────────

@app.get("/analysis/{analysis_id}", response_class=HTMLResponse)
async def analysis_view(request: Request, analysis_id: str):
    session  = get_session(request)
    analysis = get_analysis(analysis_id)
    if not analysis:
        return HTMLResponse("<h1>Analysis not found</h1>", status_code=404)
    return _tmpl(request, "analysis.html", {
        "session":             session,
        "analysis":            analysis,
        "initial_events_json": json.dumps(get_events(analysis_id, since_id=0)),
    })


@app.get("/api/analysis/{analysis_id}/events")
async def events_poll(request: Request, analysis_id: str, since: int = 0):
    analysis = get_analysis(analysis_id)
    if not analysis:
        return JSONResponse({"error": "not found"}, status_code=404)
    return JSONResponse({
        "events":       get_events(analysis_id, since_id=since),
        "status":       analysis["status"],
        "rating":       analysis["rating"],
        "error":        analysis["error"],
        "completed_at": analysis["completed_at"],
    })


# ── re-run ────────────────────────────────────────────────────────────────────

@app.get("/analysis/{analysis_id}/rerun", response_class=HTMLResponse)
async def analysis_rerun(request: Request, analysis_id: str):
    session  = get_session(request)
    analysis = get_analysis(analysis_id)
    if not analysis:
        return _r("/dashboard")
    return _tmpl(request, "dashboard.html", {
        "session":            session,
        "recent_analyses":    get_all_analyses(limit=8),
        "providers":          _PROVIDERS,
        "model_catalog_json": json.dumps(_MODEL_CATALOG),
        "msg":                "",
        "today":              _today(),
        "prefill":            analysis["settings"],
    })


# ── history ───────────────────────────────────────────────────────────────────

@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    session = get_session(request)
    return _tmpl(request, "history.html", {
        "session":  session,
        "analyses": get_all_analyses(limit=200),
    })


# ── profile ───────────────────────────────────────────────────────────────────

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, msg: str = "", error: str = ""):
    session = get_session(request)
    return _tmpl(request, "profile.html", {
        "session": session,
        "user":    get_user_by_id(session["uid"]),
        "msg":     msg,
        "error":   error,
    })


@app.post("/profile/password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str     = Form(...),
    confirm_password: str = Form(...),
):
    session = get_session(request)
    user    = get_user_by_id(session["uid"])
    if not verify_password(current_password, user["password_hash"]):
        return _r("/profile?error=Current+password+is+incorrect")
    if new_password != confirm_password:
        return _r("/profile?error=New+passwords+do+not+match")
    if len(new_password) < 8:
        return _r("/profile?error=Password+must+be+at+least+8+characters")
    update_password(session["uid"], new_password)
    return _r("/profile?msg=Password+updated+successfully")


# ── News Analyser ─────────────────────────────────────────────────────────────

@app.get("/news", response_class=HTMLResponse)
async def news_page(request: Request):
    session = get_session(request)
    return _tmpl(request, "news.html", {
        "session":        session,
        "recent_analyses": get_all_news_analyses(limit=10),
    })


@app.post("/news/analyze")
async def news_analyze(request: Request):
    session   = get_session(request)
    form      = await request.form()
    news_text = (form.get("news_text") or "").strip()
    if not news_text:
        return _r("/news")
    aid = new_analysis_id()
    create_news_analysis(
        analysis_id=aid,
        user_id=session["uid"],
        username=session["uname"],
        news_text=news_text,
    )
    submit_news_analysis(aid, news_text)
    return _r(f"/news/{aid}")


@app.get("/news/{analysis_id}", response_class=HTMLResponse)
async def news_result(request: Request, analysis_id: str):
    session  = get_session(request)
    analysis = get_news_analysis(analysis_id)
    if not analysis:
        return HTMLResponse("<h1>Analysis not found</h1>", status_code=404)
    return _tmpl(request, "news_result.html", {
        "session":             session,
        "analysis":            analysis,
        "initial_events_json": json.dumps(get_news_events(analysis_id, since_id=0)),
    })


@app.get("/api/news/{analysis_id}/events")
async def news_events_poll(request: Request, analysis_id: str, since: int = 0):
    analysis = get_news_analysis(analysis_id)
    if not analysis:
        return JSONResponse({"error": "not found"}, status_code=404)
    return JSONResponse({
        "events": get_news_events(analysis_id, since_id=since),
        "status": analysis["status"],
        "error":  analysis["error"],
    })
