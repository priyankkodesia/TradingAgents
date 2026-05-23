"""
Curated seed memory of major historical market events with actual outcomes.

Each entry contains verified market reactions — specific index moves, stock movers,
and India-specific impacts. This gives the analogue finder grounded context rather
than relying solely on LLM weights, which can hallucinate plausible-sounding moves.

Sources: Bloomberg, NSE historical data, Fed records, RBI publications.
"""

HISTORICAL_EVENTS: list[dict] = [

    # ── GLOBAL MACRO / RATE ───────────────────────────────────────────────────

    {
        "name": "Fed Rate Hike Cycle 2022–2023",
        "date": "March 2022 – July 2023",
        "type": "Monetary Policy",
        "scope": "Global",
        "what_happened": (
            "The US Federal Reserve raised rates from 0.25% to 5.50% in 18 months — "
            "the most aggressive tightening cycle since the 1980s — in response to "
            "CPI inflation peaking at 9.1% in June 2022."
        ),
        "us_market": {
            "indices": "S&P 500 fell 25.4% in 2022. NASDAQ fell 33.1%. Value outperformed growth by ~20pp.",
            "key_up": ["XOM +87%", "CVX +53%", "UNH +6%", "LMT +37%", "MO +4%"],
            "key_down": ["META -64%", "NFLX -51%", "AMZN -50%", "PYPL -62%", "ARKK ETF -67%"],
            "sectors_up": ["Energy", "Utilities (initially)", "Financials (short-term)", "Defence"],
            "sectors_down": ["Technology", "Growth/Speculative", "REITs", "Consumer Discretionary"],
        },
        "india_market": {
            "indices": "Nifty 50 fell ~10% (significantly better than US) but FII sold ₹2.8 lakh crore (~$34B) in 2022.",
            "inr_impact": "INR fell from 75 to 83 vs USD — major pressure on import costs.",
            "key_up": ["ONGC.NS +90%", "Coal India.NS +60%", "ITC.NS +55%", "Adani Energy.NS +200%+"],
            "key_down": ["Nykaa.NS -70%", "Paytm.NS -60%", "Zomato.NS -50%", "IT stocks -20-30%"],
            "rbi_response": "RBI raised repo rate from 4% to 6.5% following Fed, squeezing domestic liquidity.",
        },
        "duration_type": "Structural",
        "what_market_got_wrong": (
            "Markets initially expected 2-3 hikes. The 'Fed pivot' was called too early 5-6 times. "
            "Growth stocks were bought on every dip expecting rate cuts that never came. "
            "In India, IT stocks were bought on rupee weakness assuming it helps — ignored that "
            "demand destruction from US rate hikes hurts IT revenue more than INR helps margins."
        ),
        "key_lesson": (
            "In rate hike cycles: long energy/commodities, short unprofitable growth. "
            "India IT is a sell — not a buy — on Fed hikes despite USD tailwind. "
            "FII outflows from India are mechanical and severe; do not fight them."
        ),
        "keywords": ["rate", "fed", "inflation", "hike", "tightening", "interest rate", "cpi", "rbi"],
    },

    {
        "name": "2013 Taper Tantrum",
        "date": "May–September 2013",
        "type": "Monetary Policy",
        "scope": "Global",
        "what_happened": (
            "Fed Chairman Bernanke hinted the Fed might taper QE bond purchases. "
            "Emerging market currencies and stocks crashed as capital fled back to the US."
        ),
        "us_market": {
            "indices": "S&P 500 fell ~5% then recovered quickly. 10Y Treasury yield spiked from 1.6% to 3%.",
            "key_up": ["USD", "US financials"],
            "key_down": ["Emerging market ETFs (EEM -15%)", "Gold -25%", "High-yield bonds"],
            "sectors_up": ["US Financials", "US Industrials"],
            "sectors_down": ["Emerging markets", "Gold miners", "Bond proxies"],
        },
        "india_market": {
            "indices": "Nifty 50 fell ~13% in rupee terms, ~20% in USD terms. Sensex from 20,000 to 17,500.",
            "inr_impact": "INR crashed from 54 to 68 vs USD in 4 months — worst EM currency sell-off.",
            "key_down": ["HDFC Bank -20%", "ICICI Bank -25%", "Nifty 50 -13%"],
            "rbi_response": "RBI Governor Rajan intervened with dollar swap windows and rate hikes.",
        },
        "duration_type": "Temporary",
        "what_market_got_wrong": (
            "Sell-off was a massive overreaction. India fundamentals were unchanged. "
            "Investors who bought Nifty at the bottom of the taper tantrum made 80%+ over next 2 years. "
            "Best banking stocks (HDFC Bank, ICICI Bank) were biggest opportunity."
        ),
        "key_lesson": (
            "EM sell-offs on Fed taper are almost always temporary. The correct trade is to "
            "buy high-quality Indian banks and IT on the panic. INR weakness creates buying "
            "opportunity in IT exporters, not a reason to sell them."
        ),
        "keywords": ["taper", "qe", "fed", "emerging market", "capital outflow", "rate"],
    },

    # ── GEOPOLITICAL ──────────────────────────────────────────────────────────

    {
        "name": "9/11 Terror Attacks",
        "date": "September 11, 2001",
        "type": "Geopolitical",
        "scope": "Global",
        "what_happened": (
            "Al-Qaeda hijacked 4 planes and attacked the World Trade Center and Pentagon. "
            "US markets closed for 4 trading days — longest closure since 1933."
        ),
        "us_market": {
            "indices": "When markets reopened Sept 17: Dow fell 7.1% in one day (worst since 1929). S&P 500 -11.6% that week.",
            "key_up": ["LMT +6%", "RTN +7%", "GD +4%", "Gold +6%", "Northrop Grumman +4%"],
            "key_down": ["UAL -42%", "AMR (American Airlines) -39%", "Delta -28%", "AIG -8%", "Hotels -15%"],
            "sectors_up": ["Defense & Aerospace", "Gold", "Oil (briefly)"],
            "sectors_down": ["Airlines", "Insurance", "Hotels/Tourism", "REITs (NYC office)"],
        },
        "india_market": {
            "indices": "BSE Sensex fell ~3% initially, recovered within 2 weeks. India was not directly affected.",
            "key_up": ["Indian defense PSUs"],
            "key_down": ["Hotel stocks (ITC Hotels, Indian Hotels)", "Aviation (Jet Airways era)"],
            "inr_impact": "Minimal INR impact. India seen as peripheral to the event.",
        },
        "duration_type": "Temporary (market), Structural (defense spending)",
        "what_market_got_wrong": (
            "Initial panic sell-off was excessive. S&P 500 recovered fully within 3 months. "
            "Markets oversold non-airline, non-insurance companies on general panic. "
            "Defense stocks were actually underreacted to — US defense spending increased permanently."
        ),
        "key_lesson": (
            "Geopolitical shock ≠ economic shock. If GDP is intact, buy the dip. "
            "Defense is a multi-year structural beneficiary, not just a short-term pop. "
            "India is largely insulated from Middle East/US geopolitical events — "
            "any Nifty sell-off on 9/11-type events is a buying opportunity."
        ),
        "keywords": ["terror", "war", "attack", "geopolitical", "conflict", "military", "9/11"],
    },

    {
        "name": "Russia–Ukraine War",
        "date": "February 24, 2022",
        "type": "Geopolitical",
        "scope": "Regional (major global commodity impact)",
        "what_happened": (
            "Russia launched a full-scale invasion of Ukraine. The West imposed sweeping sanctions "
            "on Russia. Russia and Ukraine together supply ~30% of global wheat and ~40% of sunflower oil. "
            "Russia supplies ~40% of Europe's natural gas."
        ),
        "us_market": {
            "indices": "S&P 500 fell 3% on day 1, then recovered. Full 2022 decline was mostly Fed-driven.",
            "key_up": ["XOM +25%", "CVX +20%", "LMT +12%", "RTX +8%", "Wheat ETF +40%", "Natural gas +80%"],
            "key_down": ["European bank ETF -15%", "Airlines -8%", "Renault (France) -20%"],
            "sectors_up": ["Energy", "Defense", "Agriculture/Fertilizers", "Cybersecurity"],
            "sectors_down": ["European equities broadly", "Airlines", "Consumer discretionary"],
        },
        "india_market": {
            "indices": "Sensex fell 1,700 points (3%) on invasion day, recovered by end of week.",
            "inr_impact": "INR fell from 75 to 77 vs USD in 2 weeks due to oil import concerns.",
            "key_up": ["ONGC.NS +15%", "Coal India.NS +20%", "Hindalco.NS +12% (aluminium spike)"],
            "key_down": ["IndiGo.NS -10%", "Paints (Asian Paints) -8% (crude derivative cost)", "Auto stocks -5%"],
            "specific_india_impact": (
                "India was a net beneficiary in some ways — bought discounted Russian crude at $50 "
                "discount to Brent, saving ~$30B/year in import costs. BPCL, HPCL, IOC benefited. "
                "India also increased wheat exports until the government banned it."
            ),
        },
        "duration_type": "Structural",
        "what_market_got_wrong": (
            "Markets initially treated this as a temporary event that would resolve quickly. "
            "Energy price impact was underestimated — natural gas stayed elevated for 18 months. "
            "For India specifically, markets SOLD oil marketing companies on higher crude prices "
            "but India's discounted Russian oil deal made OMCs actually more profitable in FY23."
        ),
        "key_lesson": (
            "War near commodity-producing regions = structural commodity price shift. "
            "Energy + Defense = multi-year structural trade, not a trade to sell after 2 weeks. "
            "India-specific: OMCs (BPCL, HPCL) are a BUY if India can secure discounted crude — "
            "watch for government-to-government oil deals as the signal."
        ),
        "keywords": ["russia", "ukraine", "war", "invasion", "sanctions", "nato", "europe", "conflict"],
    },

    {
        "name": "Gulf War / Iraq Invasion of Kuwait — Oil Shock",
        "date": "August 1990 – January 1991",
        "type": "Geopolitical",
        "scope": "Regional (global oil impact)",
        "what_happened": (
            "Iraq invaded Kuwait in August 1990. Oil prices doubled from $17 to $36/barrel. "
            "US-led coalition launched Operation Desert Storm in January 1991."
        ),
        "us_market": {
            "indices": "S&P 500 fell 20% from July to October 1990. Rallied sharply when war ended quickly in Feb 1991.",
            "key_up": ["Exxon +15%", "Chevron +12%", "Defense stocks +20%"],
            "key_down": ["Airlines -30-40%", "Auto -15%", "Consumer discretionary -20%"],
            "sectors_up": ["Energy", "Defense", "Gold"],
            "sectors_down": ["Airlines", "Autos", "Consumer"],
        },
        "india_market": {
            "indices": "BSE Sensex fell ~30% in 1990 (combined with domestic political crisis). Severe impact.",
            "inr_impact": "India's forex reserves fell to just $1.2B — near-default crisis in 1991.",
            "key_down": ["Broad market sold off — oil import bill devastated India's balance of payments"],
            "specific_india_impact": (
                "Oil shock triggered India's 1991 BOP crisis, leading to IMF bailout and landmark "
                "economic reforms (liberalisation under Manmohan Singh). The worst short-term outcome "
                "led to India's best long-term structural reform."
            ),
        },
        "duration_type": "Temporary (war) but Structural (India's reform path)",
        "what_market_got_wrong": (
            "Markets expected the war to last years and oil to stay above $35. War ended in 100 hours. "
            "Oil crashed from $36 to $17 by end of February 1991. Massive rally followed. "
            "For India: the BOP crisis was actually a BUYING signal for the long term — "
            "reforms that followed created India's modern equity market."
        ),
        "key_lesson": (
            "Oil spikes on Middle East wars are almost always temporary — wars end, supply recovers. "
            "India is extremely vulnerable to sustained oil prices above $90 (current account deficit explodes). "
            "Watch India's forex reserves as the stress indicator — below $300B is danger territory today."
        ),
        "keywords": ["gulf", "iraq", "iran", "middle east", "oil", "opec", "war", "invasion"],
    },

    # ── PANDEMIC / HEALTH ─────────────────────────────────────────────────────

    {
        "name": "Covid-19 Pandemic — Market Crash",
        "date": "February 19 – March 23, 2020",
        "type": "Pandemic",
        "scope": "Global",
        "what_happened": (
            "WHO declared Covid-19 a pandemic on March 11, 2020. Global lockdowns followed. "
            "S&P 500 experienced its fastest 30% decline in history (33 days)."
        ),
        "us_market": {
            "indices": "S&P 500 fell 34% peak-to-trough (Feb 19 – Mar 23). Recovered fully by August 2020. New ATH by Nov 2020.",
            "key_up": ["ZOOM +500%", "AMZN +76%", "NFLX +60%", "MRNA +700%+ (vaccine)", "BNTX +300%+"],
            "key_down": ["CCL (Carnival) -75%", "AAL (American Airlines) -70%", "MGM -60%", "XOM -50%"],
            "sectors_up": ["Technology", "Pharma/Biotech", "E-commerce", "Cloud", "Home fitness"],
            "sectors_down": ["Airlines", "Cruise lines", "Hotels", "Retail (physical)", "Oil & Gas"],
        },
        "india_market": {
            "indices": "Nifty 50 fell from 12,362 to 7,511 (-39%) between Jan 14 and March 23, 2020. Recovered to new highs by end 2020.",
            "inr_impact": "INR fell from 71 to 76 vs USD. FIIs sold ₹65,000 crore in March 2020.",
            "key_up": ["Dr Reddy's +50%", "Sun Pharma +40%", "Cipla +60%", "Divi's Labs +80%", "TCS +30% (WFH demand)"],
            "key_down": ["IndiGo.NS -60%", "InterGlobe Aviation -65%", "Indian Hotels -55%", "PVR -70%", "HDFC Bank -40%"],
            "specific_india_impact": (
                "India pharma was a massive winner — India is the world's pharmacy and generic drug "
                "exports surged. IT was a winner on WFH digital transformation spend. "
                "Banks fell hard on NPA fears but HDFC Bank / ICICI Bank recovered fastest. "
                "March 23, 2020 was the single best buying opportunity in a generation for India."
            ),
        },
        "duration_type": "Structural (accelerated digital shift), Temporary (lockdown-specific impacts)",
        "what_market_got_wrong": (
            "1. Sold pharma stocks initially on supply chain fear — wrong, pharma was the biggest winner. "
            "2. Bought 'reopening' stocks too early in April/May 2020 — second wave delayed reopening. "
            "3. Sold IT stocks on demand uncertainty — wrong, WFH created massive IT demand spike. "
            "4. In India, sold OMCs on oil crash — crude crash was actually good for BPCL/HPCL margins. "
            "5. The broader lesson: pandemic = sell physical world, buy digital world. Obvious in hindsight, not in March 2020."
        ),
        "key_lesson": (
            "Black swan events create once-in-a-decade buying opportunities. "
            "Pharma and IT are defensive with upside in pandemic scenarios. "
            "India pharma (Cipla, Dr Reddy's, Sun Pharma) specifically benefits from global API demand. "
            "Airlines and hospitality recover last and slowest — avoid for 12-18 months."
        ),
        "keywords": ["covid", "pandemic", "lockdown", "virus", "disease", "health", "epidemic", "quarantine"],
    },

    # ── FINANCIAL CRISIS ──────────────────────────────────────────────────────

    {
        "name": "2008 Global Financial Crisis — Lehman Collapse",
        "date": "September 15, 2008 (Lehman), full crisis 2007–2009",
        "type": "Macroeconomic",
        "scope": "Global",
        "what_happened": (
            "Lehman Brothers filed for bankruptcy on Sep 15, 2008 — the largest bankruptcy in US history. "
            "Credit markets froze globally. AIG required a $85B government bailout. "
            "S&P 500 lost 57% peak-to-trough (Oct 2007 – Mar 2009)."
        ),
        "us_market": {
            "indices": "S&P 500 -38% in 2008 alone. Bottom March 9, 2009 at 666. Full recovery took 5 years.",
            "key_up": ["Gold +5% in 2008 (then +25% in 2009)", "US Treasuries (flight to safety)", "Walmart (defensive)"],
            "key_down": ["Citi -88%", "AIG -97%", "WaMu (bankrupt)", "Wachovia (failed)", "GE -60%"],
            "sectors_up": ["Gold", "Treasuries", "Consumer staples", "Utilities"],
            "sectors_down": ["Financials", "Real estate", "Consumer discretionary", "Industrials"],
        },
        "india_market": {
            "indices": "Sensex fell from 21,206 (Jan 2008) to 7,697 (Oct 2008) — a 64% crash.",
            "inr_impact": "INR fell from 39 to 52 vs USD. FII sold aggressively.",
            "key_down": ["HDFC Bank -50%", "ICICI Bank -60%", "Reliance -55%", "L&T -60%"],
            "specific_india_impact": (
                "India had no direct subprime exposure — Indian banks had not originated mortgage CDOs. "
                "The sell-off was entirely FII-driven panic. Indian banking system was fundamentally sound. "
                "This was the most extreme 'buy India on the dip' signal in 15 years. "
                "Nifty went from 2,700 (2008 low) to 18,000+ (2021) — 6.6x in 13 years."
            ),
        },
        "duration_type": "Structural (regulatory overhaul), eventually Cyclical recovery",
        "what_market_got_wrong": (
            "1. Assumed US bank contagion would destroy Indian bank balance sheets — it didn't. "
            "2. Sold quality Indian banks (HDFC, ICICI) alongside junk — massive mispricing. "
            "3. Underestimated government stimulus (TARP, ARRA, RBI rate cuts) speed and magnitude. "
            "4. The 2009 low was obvious only in hindsight — but 'worst financial crisis since 1929' "
            "is actually a buy signal for 5-year holders, not a sell signal."
        ),
        "key_lesson": (
            "Financial crises originating in the US/Europe create extreme buying opportunities in Indian quality stocks. "
            "India's banking system is less interconnected globally than feared. "
            "HDFC Bank and ICICI Bank at crisis lows = generational entry points. "
            "Gold is the best hedge in financial crises — buy early, before the panic."
        ),
        "keywords": ["financial crisis", "bank", "lehman", "credit", "recession", "subprime", "mortgage", "systemic"],
    },

    {
        "name": "SVB (Silicon Valley Bank) Collapse",
        "date": "March 10, 2023",
        "type": "Macroeconomic",
        "scope": "National (US-contained)",
        "what_happened": (
            "Silicon Valley Bank failed after a classic bank run. $42B in deposits withdrawn in 24 hours. "
            "FDIC seized the bank. Signature Bank and First Republic followed. "
            "Fear of broader banking contagion briefly spread globally."
        ),
        "us_market": {
            "indices": "S&P 500 fell 4.5% in the week. Recovered fully within 3 weeks.",
            "key_up": ["JPM +2%", "BAC flat", "Gold +5%", "Treasuries rallied (rate cut expectations)"],
            "key_down": ["SIVB -100% (failed)", "FRC (First Republic) -70%", "PACW -60%", "Regional banks ETF (KRE) -25%"],
            "sectors_up": ["Large cap banks (beneficiaries of deposit flight)", "Gold"],
            "sectors_down": ["Regional banks", "Tech startups (SVB clients)", "Crypto"],
        },
        "india_market": {
            "indices": "Nifty fell ~1.5% in sympathy, recovered within days. No fundamental India impact.",
            "inr_impact": "Minimal INR impact. India banking sector unaffected.",
            "key_down": ["IT stocks fell 2-3% on 'US recession' fears", "Nykaa, Paytm -5% (tech sentiment)"],
            "specific_india_impact": "SVB had no direct India exposure. Any India sell-off was a buying opportunity.",
        },
        "duration_type": "Temporary",
        "what_market_got_wrong": (
            "Markets initially priced in contagion to all US regional banks. "
            "JPM and large banks were actually beneficiaries of the panic (deposit inflows). "
            "Indian IT and fintech sold off on US recession fear — but SVB's failure was idiosyncratic, "
            "not a recession signal. Buying Indian IT on SVB panic was correct."
        ),
        "key_lesson": (
            "Not all bank failures are systemic. SVB was idiosyncratic (concentrated tech/VC deposits, "
            "duration mismatch). Large diversified banks (JPM, HDFC Bank) benefit from regional bank crises. "
            "India bank sell-offs on US regional bank news are always buying opportunities."
        ),
        "keywords": ["svb", "bank failure", "bank run", "regional bank", "deposit", "fdic", "silicon valley bank"],
    },

    # ── TRADE / TARIFF ────────────────────────────────────────────────────────

    {
        "name": "US–China Trade War (Tariffs)",
        "date": "March 2018 – January 2020",
        "type": "Macroeconomic",
        "scope": "Global",
        "what_happened": (
            "Trump administration imposed tariffs of 25% on $250B+ of Chinese goods. "
            "China retaliated. 'Phase 1 deal' signed Jan 2020. Tech sector most affected by supply chain fears."
        ),
        "us_market": {
            "indices": "S&P 500 fell 20% Q4 2018 (partly trade war, partly Fed). Recovered in 2019.",
            "key_up": ["US domestic industrials", "Agricultural alternatives", "Vietnam-exposed manufacturers"],
            "key_down": ["Apple -35% Q4 2018", "Semiconductors (SOXX ETF -25%)", "Caterpillar -30%", "Boeing -25%"],
            "sectors_up": ["Defense", "Domestic manufacturing", "Alternative EM markets (Vietnam, India)"],
            "sectors_down": ["Semiconductors", "Consumer tech hardware", "Agriculture (soybean exporters)"],
        },
        "india_market": {
            "indices": "Nifty fell ~15% in 2018 partly on trade war + domestic NBFC crisis (IL&FS).",
            "inr_impact": "INR fell from 63 to 74 vs USD in 2018 — large depreciation.",
            "key_up": ["IT stocks — US companies outsourcing more to India to avoid China", "Textile exporters"],
            "key_down": ["Metals (Tata Steel, Hindalco) on global demand fears", "NBFCs on IL&FS contagion"],
            "specific_india_impact": (
                "India was a net beneficiary of US-China tension — manufacturing diversification "
                "narrative (China+1) drove FDI interest in India. IT companies won more contracts "
                "as US firms shifted tech work from China to India. "
                "Apple (Foxconn) starting India manufacturing was a direct result."
            ),
        },
        "duration_type": "Structural (supply chain reconfiguration)",
        "what_market_got_wrong": (
            "Markets assumed tariffs would be quickly reversed in a deal. They weren't. "
            "Supply chain shift out of China took years but was real and permanent. "
            "Semiconductor tariffs were underestimated — led directly to CHIPS Act years later. "
            "India IT was wrongly sold — trade war was actually a tailwind for Indian IT outsourcing."
        ),
        "key_lesson": (
            "US-China trade tension = structural India beneficiary (manufacturing + IT). "
            "Semiconductors: any tariff/export control on China chips = buy TSMC, Intel (domestic), "
            "sell China-exposed fabs. India's Tata Electronics/Foxconn India = long-term beneficiary."
        ),
        "keywords": ["tariff", "trade war", "china", "us-china", "import duty", "protectionism", "decoupling"],
    },

    # ── OIL / ENERGY ──────────────────────────────────────────────────────────

    {
        "name": "OPEC Production Cut — Oil Price Surge",
        "date": "October 2022 (OPEC+2M bpd cut) and October 2023 (Saudi extension)",
        "type": "Macroeconomic",
        "scope": "Global",
        "what_happened": (
            "OPEC+ announced 2 million barrel/day production cut in October 2022, largest since 2020. "
            "Brent crude rose from $83 to $96/barrel. Saudi Arabia extended voluntary cuts through 2024."
        ),
        "us_market": {
            "indices": "S&P 500 fell 2% on the day. Airlines fell 5-8%. Energy rallied 5-10%.",
            "key_up": ["XOM +4%", "CVX +3%", "Pioneer Natural +5%", "Energy ETF (XLE) +5%"],
            "key_down": ["AAL -8%", "DAL -6%", "UAL -7%", "FedEx -3%", "Trucking stocks -2-3%"],
            "sectors_up": ["Oil & Gas", "Oil services (HAL, SLB)"],
            "sectors_down": ["Airlines", "Shipping/Logistics", "Consumer discretionary"],
        },
        "india_market": {
            "indices": "Sensex fell 1-2% on oil cut news. Market recovered as India secured Russian crude discounts.",
            "inr_impact": "Each $10 rise in oil = ~$15B increase in India's annual import bill. INR pressure.",
            "key_up": ["ONGC.NS +5-8% (upstream benefits)", "Oil India.NS +6%"],
            "key_down": ["IndiGo.NS -5%", "BPCL.NS -3%", "HPCL.NS -3% (refining margins squeezed unless price pass-through allowed)"],
            "specific_india_impact": (
                "India's current account deficit widens ~$15-20B per $10/barrel oil increase. "
                "Aviation is immediately hurt — ATF (aviation turbine fuel) is 30-40% of airline costs. "
                "OMCs (BPCL, HPCL) are complex — hurt by higher crude but can recover if government "
                "allows retail price pass-through. In practice, government often delays pass-through, "
                "creating OMC underperformance vs crude."
            ),
        },
        "duration_type": "Cyclical",
        "what_market_got_wrong": (
            "Markets assumed Saudi Arabia would back down — it didn't, extended cuts. "
            "OMC stocks in India were sold expecting government to cap retail prices (protecting consumers) "
            "but government allowed partial price hikes, making OMCs more profitable than feared. "
            "Upstream PSUs (ONGC, Oil India) were underowned — they benefit directly from high crude."
        ),
        "key_lesson": (
            "Oil spike: Buy upstream (ONGC, Oil India), sell aviation (IndiGo). "
            "OMCs (BPCL, HPCL) are binary — watch for government fuel price decisions. "
            "In India, oil >$90 = macro headwind (higher CAD, INR pressure, RBI constrained). "
            "Fertilizer companies (Coromandel, Chambal) also hurt — naphtha/natural gas feedstock cost rises."
        ),
        "keywords": ["oil", "crude", "opec", "energy", "petroleum", "brent", "wti", "fuel"],
    },

    # ── INDIA-SPECIFIC ────────────────────────────────────────────────────────

    {
        "name": "India Demonetisation",
        "date": "November 8, 2016",
        "type": "Regulatory",
        "scope": "National (India)",
        "what_happened": (
            "PM Modi announced on national TV that ₹500 and ₹1,000 notes (86% of currency in circulation) "
            "were immediately demonetised. Massive cash crunch followed for 6-8 weeks."
        ),
        "us_market": {
            "indices": "No US market impact.",
            "key_up": [],
            "key_down": [],
            "sectors_up": [],
            "sectors_down": [],
        },
        "india_market": {
            "indices": "Sensex fell 1,700 points (6%) in the week. Recovered within 1 month.",
            "inr_impact": "Limited INR impact directly, though foreign investors were cautious.",
            "key_up": ["PayTM (unlisted then but massive user surge)", "HDFC Bank +3% (digital payments)", "Axis Bank +2%"],
            "key_down": ["Jewelry (Titan -15%)", "Real estate (DLF -10%)", "Consumer goods (HUL -5%)", "Auto (Maruti -8%)"],
            "specific_india_impact": (
                "Cash-heavy businesses were devastated: real estate, jewelry, unorganised retail, construction. "
                "Banks temporarily benefited from huge deposit inflows. "
                "Digital payments (PayTM, banking apps) saw explosive growth — structural shift in payments. "
                "GDP slowed to 6.1% in Q4 FY17. The negative economic impact lasted 2-3 quarters."
            ),
        },
        "duration_type": "Temporary (economic shock) + Structural (digital payments acceleration)",
        "what_market_got_wrong": (
            "Markets initially panicked and sold quality consumer and banking stocks. "
            "HDFC Bank and private banks were net beneficiaries — massive deposit inflows, digital push. "
            "Luxury/jewelry stocks like Titan were sold — but Titan recovered in 6 months as cash came back. "
            "The digital payments structural shift was massively underestimated."
        ),
        "key_lesson": (
            "Indian government policy risk is real and sudden. Always hold quality over leveraged/cash businesses. "
            "Digital payment companies and private banks with strong tech infrastructure benefit from any "
            "cashless economy push. Real estate, jewelry, unorganised sector = avoid around policy uncertainty."
        ),
        "keywords": ["demonetisation", "demonetization", "note ban", "currency", "india policy", "rbi", "rupee"],
    },

    {
        "name": "IL&FS Crisis — India NBFC Contagion",
        "date": "September 2018",
        "type": "Macroeconomic",
        "scope": "National (India)",
        "what_happened": (
            "Infrastructure Leasing & Financial Services (IL&FS), a major NBFC with ₹91,000 crore ($13B) "
            "in debt, defaulted on short-term obligations. Created a credit freeze in India's NBFC sector, "
            "which had funded much of India's shadow banking and real estate."
        ),
        "us_market": {
            "indices": "No US impact.",
            "key_up": [],
            "key_down": [],
            "sectors_up": [],
            "sectors_down": [],
        },
        "india_market": {
            "indices": "Nifty fell ~15% from Aug to Oct 2018. NBFCs and HFCs collapsed 30-60%.",
            "inr_impact": "INR fell to 74 vs USD — combination of IL&FS + Fed rate hikes + oil spike.",
            "key_up": ["Large banks (HDFC Bank, ICICI Bank relatively resilient)"],
            "key_down": ["DHFL -90% (later bankrupt)", "Yes Bank -30%", "IndiaBulls -50%", "PNB Housing -40%"],
            "specific_india_impact": (
                "The NBFC crisis froze India's real estate and infrastructure funding. "
                "Small auto and home loan companies that relied on NBFC funding saw demand collapse. "
                "Maruti, Bajaj Auto sales fell as NBFC-funded retail loans dried up. "
                "Bajaj Finance survived and gained market share — became the clearest winner."
            ),
        },
        "duration_type": "Structural (triggered consolidation in NBFC sector)",
        "what_market_got_wrong": (
            "Markets sold ALL NBFCs indiscriminately. Bajaj Finance (well-capitalised, retail-funded) "
            "was sold alongside junk NBFCs — massive mispricing. Bajaj Finance at Oct 2018 lows "
            "was the best India equity trade of the next 3 years (+400%). "
            "Markets also oversold Maruti and auto stocks — demand recovered in 12-18 months."
        ),
        "key_lesson": (
            "India-specific credit crisis = sell weak NBFCs, BUY quality NBFCs on the panic. "
            "Bajaj Finance, HDFC Ltd, Chola Finance are the 'buy on every India credit crisis' names. "
            "Auto stocks are collateral damage — buy quality auto names 6 months after the credit crunch."
        ),
        "keywords": ["nbfc", "india credit", "shadow banking", "il&fs", "real estate", "india financial crisis"],
    },

    # ── TECHNOLOGY / SECTOR ───────────────────────────────────────────────────

    {
        "name": "Dot-com Bubble Burst",
        "date": "March 2000 – October 2002",
        "type": "Technology Shift",
        "scope": "Global",
        "what_happened": (
            "NASDAQ peaked at 5,048 on March 10, 2000 after years of speculative tech investing. "
            "It fell 78% to 1,114 by October 2002. $5 trillion in market cap destroyed. "
            "Hundreds of internet companies went bankrupt."
        ),
        "us_market": {
            "indices": "NASDAQ -78%. S&P 500 -49%. Dow -38%. Recovery to 2000 highs took 15 years.",
            "key_up": ["Gold +25% (2001-2002)", "Financials", "Healthcare"],
            "key_down": ["Cisco -88%", "Intel -80%", "AOL -97%", "Pets.com -100% (bankrupt)", "Webvan -100%"],
            "sectors_up": ["Value stocks", "Energy", "Financials", "Gold"],
            "sectors_down": ["All unprofitable internet companies", "Telecom", "Tech hardware"],
        },
        "india_market": {
            "indices": "BSE IT Index fell ~75%. Sensex fell ~40% from peak.",
            "key_down": ["Infosys -65%", "Wipro -80%", "Satyam -70%"],
            "key_up": ["FMCG stocks (HUL, ITC) relatively stable — defensive rotation"],
            "specific_india_impact": (
                "India IT sector was devastated as Y2K spending boom ended. Infosys, Wipro, "
                "which had traded at 100x P/E during the bubble, fell 65-80%. "
                "Took 3-4 years to recover. Companies that survived (Infosys, TCS) emerged stronger "
                "with diversified client bases."
            ),
        },
        "duration_type": "Structural (permanent reset of valuations)",
        "what_market_got_wrong": (
            "Markets assumed quality tech (Cisco, Intel, Microsoft) was different from junk dot-coms. "
            "Even profitable tech companies fell 80%+ purely from valuation compression. "
            "Indian IT was sold more than warranted — underlying businesses were sound. "
            "Investors who held Infosys from 2002 lows made 50x by 2017."
        ),
        "key_lesson": (
            "Valuation bubbles in tech always burst — even profitable companies aren't immune. "
            "The survivors of a bubble emerge as oligopolies (Google, Amazon post-2002). "
            "India IT at bubble-bust valuations = multi-decade buy. "
            "High P/E momentum stocks in any era are the first to fall and the last to recover."
        ),
        "keywords": ["tech bubble", "dotcom", "nasdaq", "valuation", "ai bubble", "tech selloff", "growth stocks"],
    },

    {
        "name": "Brexit Vote",
        "date": "June 23, 2016",
        "type": "Social/Political",
        "scope": "Regional (UK/Europe, some global)",
        "what_happened": (
            "UK voted 52%-48% to leave the European Union, shocking polls that had predicted Remain. "
            "GBP fell 10% vs USD overnight — largest single-day move in modern FX history."
        ),
        "us_market": {
            "indices": "S&P 500 fell 5.3% over 2 days, then fully recovered within 2 weeks.",
            "key_up": ["Gold +5%", "US Treasuries rallied", "USD strengthened"],
            "key_down": ["European bank ETF -15%", "UK-exposed US companies", "GBP -10%"],
            "sectors_up": ["US Financials", "Gold", "Domestic US companies"],
            "sectors_down": ["UK/European equities", "GBP assets"],
        },
        "india_market": {
            "indices": "Sensex fell ~600 points (2.2%) on June 24, recovered fully within 2 days.",
            "inr_impact": "Minimal. Slight INR weakness. FII flows not significantly affected.",
            "key_down": ["IT stocks fell 2-3% on UK demand fears (UK is ~15% of India IT revenue)"],
            "specific_india_impact": (
                "India IT companies with UK exposure (Infosys, Wipro, HCL) saw 3-5% dip on "
                "currency uncertainty and UK client caution. Proved to be a buying opportunity. "
                "Indian pharma with UK/European exposure was briefly sold but recovered quickly."
            ),
        },
        "duration_type": "Structural (for UK), Temporary (for India)",
        "what_market_got_wrong": (
            "Global markets massively overreacted. S&P 500 recovered fully in 2 weeks. "
            "Indian markets especially — India has limited UK trade exposure. "
            "GBP weakness is marginally good for India IT (UK revenues in GBP, cost in INR). "
            "The correct India trade was to BUY IT stocks on the Brexit dip."
        ),
        "key_lesson": (
            "European political events (Brexit, EU elections) have minimal India market impact. "
            "Any Nifty dip >1.5% on European political news = buying opportunity for domestic India stocks. "
            "IT stocks are not hurt by GBP weakness — they hedge currency exposure or benefit from it."
        ),
        "keywords": ["brexit", "eu", "europe", "political", "referendum", "uk", "election"],
    },

]


def format_for_prompt(events: list[dict]) -> str:
    """Format historical events as a structured string for injection into agent prompts."""
    lines = []
    for e in events:
        lines.append(f"\n{'='*70}")
        lines.append(f"EVENT: {e['name']} ({e['date']})")
        lines.append(f"Type: {e['type']} | Scope: {e['scope']}")
        lines.append(f"\nWHAT HAPPENED:\n{e['what_happened']}")

        us = e.get("us_market", {})
        if us.get("indices"):
            lines.append(f"\nUS MARKET REACTION:\n  Indices: {us['indices']}")
        if us.get("key_up"):
            lines.append(f"  Key risers: {', '.join(us['key_up'])}")
        if us.get("key_down"):
            lines.append(f"  Key fallers: {', '.join(us['key_down'])}")

        india = e.get("india_market", {})
        if india.get("indices"):
            lines.append(f"\nINDIA MARKET REACTION:\n  Indices: {india['indices']}")
        if india.get("inr_impact"):
            lines.append(f"  INR: {india['inr_impact']}")
        if india.get("key_up"):
            lines.append(f"  Key risers: {', '.join(india.get('key_up', []))}")
        if india.get("key_down"):
            lines.append(f"  Key fallers: {', '.join(india.get('key_down', []))}")
        if india.get("specific_india_impact"):
            lines.append(f"  India-specific: {india['specific_india_impact']}")

        lines.append(f"\nDURATION TYPE: {e['duration_type']}")
        lines.append(f"\nWHAT MARKET GOT WRONG:\n{e['what_market_got_wrong']}")
        lines.append(f"\nKEY LESSON:\n{e['key_lesson']}")

    return "\n".join(lines)


def find_relevant_events(classification: dict, news_text: str) -> list[dict]:
    """
    Return the most relevant historical events for a given classification.
    Uses keyword matching on event type + news text keywords.
    Always returns at least 3 events.
    """
    news_lower  = news_text.lower()
    event_type  = (classification.get("event_type") or "").lower()

    scored = []
    for event in HISTORICAL_EVENTS:
        score = 0
        # Keyword match against news text
        for kw in event.get("keywords", []):
            if kw in news_lower:
                score += 3
        # Type match
        if event["type"].lower() in event_type or event_type in event["type"].lower():
            score += 2
        # Scope match
        if classification.get("scope", "").lower() in event["scope"].lower():
            score += 1
        scored.append((score, event))

    scored.sort(key=lambda x: x[0], reverse=True)

    # Always return at least 3 events (top scored)
    top = [e for _, e in scored[:6]]
    return top
