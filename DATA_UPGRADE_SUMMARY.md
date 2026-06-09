# Data Collection Notes

This repository now treats market and macro data as provider-backed or unavailable. Missing sources should return empty, `None`, or skipped results instead of fabricated values.

## What Works Without Paid Keys

- Yahoo Finance through `yfinance` for FX pairs and market proxies.
- Public RSS feeds for business and market headlines.
- Local CSV/log files under `logs/` when users create or import their own research data.

These free sources are enough for experimentation, demos, and learning. They are not guaranteed to be complete, timely, or suitable for trading decisions.

## Optional Free Keys

Some providers offer free tiers with quotas or rate limits:

- `NEWS_API_KEY` for NewsAPI headlines.
- `FRED_API_KEY` for macroeconomic series.
- `ALPHA_VANTAGE_API_KEY` for market/fundamental data experiments.
- `CURRENCY_API_KEY` or `FXRATES_API_KEY` for alternate FX endpoints.

Copy `.env.example` or `.env.template` to `.env` and fill only the providers you want to use.

## Paid Or Premium Data

Higher-quality data usually comes from paid providers. Paid FX, macro, news, and broker data can improve coverage, freshness, licensing clarity, and historical depth. This project keeps those integrations optional so the open-source version still runs for learning and portfolio review.

## Current Public-Release Behavior

- Data collectors try configured real sources and skip unavailable sources.
- Historical random extrapolation fallbacks were removed from public collection paths.
- Dashboard integrations read local logs where present and otherwise return unavailable data.
- `live_trading_deployment.py` is paper-only research scaffolding; broker execution is intentionally not implemented.
- The Flask API is local-first by default and binds to `127.0.0.1` unless explicitly overridden.

## Practical Usage

Run the lightweight scraper once:

```bash
python enhanced_scraper_simple.py --once
```

Run continuous local collection:

```bash
python enhanced_scraper_simple.py --auto
```

Start the local API:

```bash
python api_server_real_data.py
```

The important rule for public usage is simple: if a source is not configured or available, the project should say so rather than making up data.
