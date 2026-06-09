# Carry Trade Research Model

A Python and React research project for exploring currency carry trade signals, FX data collection, macro indicators, news sentiment, and dashboard-driven analysis.

This repository is intentionally framed as a research and engineering project, not a trading product. The current public-facing flow favors traceable data, explicit fallbacks, and honest labels over inflated claims.

## Why This Project Exists

I started this project in college as a finance major, before dedicated coding assistants such as Codex, Claude Code, or similar agentic tools existed. It began as a simple attempt to write code with early ChatGPT help for a carry trade idea. Over time, as my engineering skills improved, I kept expanding it into a broader system with data collection, model experimentation, API endpoints, and a React dashboard.

That history is part of the value proposition: this is a finance-origin project that grew into a practical software engineering artifact. It shows the progression from quantitative curiosity to a more disciplined system with tests, docs, data provenance, and public-release hygiene.

## What It Does

- Collects FX data for carry trade research using Yahoo Finance and optional API integrations.
- Reads macro and news sentiment logs when available.
- Provides a Flask API for dashboard consumption.
- Displays FX rates, sentiment, macro data, model outputs, signals, and performance metrics in a React dashboard.
- Includes improved model experiments using time-series validation and optional boosted-tree models.
- Keeps older exploratory scripts for historical context while documenting the current canonical path.

## Data Provenance

Data provenance is explicit in the public-facing flow. The repository separates real inputs from derived or unavailable outputs:

- FX rates: pulled from Yahoo Finance where available, with optional API fallbacks in the data collection scripts.
- News sentiment: computed from local news logs and optional NewsAPI collection when `NEWS_API_KEY` is configured.
- Macro data: read from local macro logs where available; optional FRED usage is supported by separate scripts.
- Predictions and signals: research heuristics unless you add trained model outputs to the expected log files.
- Performance metrics: shown only when a `logs/performance_log.csv` file exists. The API no longer invents portfolio performance numbers when no performance data is available.

### Data Source Tiers

Free/no-key data is enough to run the project for fun, demos, and local research:

- Yahoo Finance via `yfinance` for FX rates where available.
- ExchangeRate-API public endpoint for basic FX fallback data.
- RSS feeds for broad financial headlines.
- Local CSV logs that you create by running the collectors.

Optional free API keys improve coverage without requiring paid plans:

- `NEWS_API_KEY` enables richer headline collection from NewsAPI.
- `FRED_API_KEY` enables official macro series from FRED.
- `ALPHA_VANTAGE_API_KEY` enables another FX source.
- `CURRENCY_API_KEY` enables CurrencyAPI as an additional FX source.

Paid or premium data is not required, but it is better for serious research:

- `FIXER_API_KEY` or other paid FX providers can improve reliability, quotas, and coverage.
- Professional macro/news/market-data feeds usually have cleaner licensing, better uptime, and better historical depth.
- Higher-quality data usually comes from paid providers; free sources are good enough to explore the system but should not be treated as institutional-grade inputs.

If a source is unavailable or a key is missing, the public API returns empty or `null` data for that slice instead of making up values.

Not financial advice. This software is for research, education, and portfolio demonstration only.

## Current Public-Ready Entry Points

Use these files first:

- `api_server_real_data.py` - Flask API for the dashboard.
- `frontend/` - React TypeScript dashboard.
- `enhanced_scraper_simple.py` - practical data collection script with optional NewsAPI usage.
- `improved_ensemble_model.py` - improved model experiment with time-series validation and optional XGBoost/LightGBM support.
- `tests/test_public_readiness.py` - release hygiene checks for secrets, dashboard data wiring, env docs, and README positioning.
- `tests/test_model_validation.py` - model-theory checks: forward-looking target construction, no-skill-on-noise leakage detection, and planted-signal recovery.

Several older scripts remain in the repo to show project history. Treat them as exploratory unless the README calls them out above.

## Quick Start

### Prerequisites

- Python 3.9 or newer. Python 3.11 is recommended.
- Node.js 20.19 or newer for the Vite dashboard.
- Git.
- macOS only, for XGBoost/LightGBM: `brew install libomp` if you want boosted-tree models. Without `libomp`, the improved model falls back to scikit-learn estimators.

### Backend Setup

```bash
git clone https://github.com/Aidan2111/carry-trade-model.git
cd carry-trade-model

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

Optional API keys:

```bash
cp .env.example .env
# Fill in optional keys only for the providers you want to use.
```

### Run The API

```bash
source .venv/bin/activate
python api_server_real_data.py
```

The API runs at `http://127.0.0.1:8000` by default. Use `FLASK_HOST`, `FLASK_PORT`, and `CORS_ORIGINS` if you intentionally expose it elsewhere.

Useful endpoints:

- `GET /health`
- `GET /api/dashboard`
- `GET /api/fx-rates`
- `GET /api/predictions`
- `GET /api/performance`

### Run The Dashboard

```bash
cd frontend
npm install
npm start
```

The dashboard runs at `http://127.0.0.1:5173` and requests the backend at `http://localhost:8000` by default.

To use another backend URL:

```bash
VITE_API_URL=http://localhost:8000 npm start
```

## Verification

Run the public-readiness and model-validation checks:

```bash
source .venv/bin/activate
python -m unittest discover -s tests -v
```

Run Python compile checks:

```bash
find . -path './.venv' -prune -o -path './frontend/node_modules' -prune -o -path './frontend/dist' -prune -o -path './frontend/build' -prune -o -name '*.py' -print0 | xargs -0 python -m py_compile
```

Run the frontend production build:

```bash
cd frontend
npm run build
```

Run npm audit:

```bash
cd frontend
npm audit --omit=dev
```

The frontend uses Vite and commits `frontend/package-lock.json` for reproducible installs.

## Repository Hygiene

- API keys are read from `.env` and environment variables, not committed source.
- `.env.example` documents optional keys.
- Runtime logs, CSVs, model binaries, virtual environments, node modules, and build output are ignored.
- If this repository was previously private and contained committed keys in old history, rotate those keys before making the repository public.

## Suggested Project Narrative

This is a good recruiter-facing story:

> I started this as a finance-major carry trade model in college before modern coding assistants existed. It began as a rough early-ChatGPT coding experiment and became a more mature engineering project as I learned to build data pipelines, model validation, APIs, and frontend dashboards. The public version is intentionally honest about provenance, limitations, and what is research-grade versus production-grade.

## Limitations

- This is not a live trading system.
- Predictions and signals should be treated as research outputs.
- Some older files are preserved as project history and are not the recommended entry point.
- External data availability depends on providers, API keys, quotas, and local logs.

## License

MIT. See `LICENSE`.
