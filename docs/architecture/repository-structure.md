# Repository Structure

This layout applies Microsoft Learn and Azure Well-Architected Framework guidance to make the project easier to read, test, and change.

References:

- Microsoft Learn, Azure Repos: https://learn.microsoft.com/en-us/azure/devops/repos/git/git-branching-guidance
- Microsoft Learn, Azure Well-Architected Framework operational excellence principles: https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/principles
- Microsoft Learn, standardizing tools and processes: https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/tools-processes
- Microsoft Learn, formalizing development practices: https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/formalize-development-practices
- Microsoft Learn, MLOps v2 architecture: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/machine-learning-operations-v2

## Applied Principles

- Keep source-controlled artifacts organized by responsibility so reviews can focus on the files that actually changed.
- Keep code, scripts, tests, docs, and historical artifacts in predictable places.
- Keep a small number of root compatibility entrypoints for existing commands, but put implementation code under an importable package.
- Keep current guidance in docs instead of scattered notes at the repository root.
- Keep the public workflow auditable through tests, PR descriptions, and repeatable verification commands.

## Current Layout

```text
.
├── README.md
├── api_server_real_data.py              # root compatibility entrypoint
├── enhanced_scraper_simple.py           # root compatibility entrypoint
├── improved_ensemble_model.py           # root compatibility import wrapper
├── run_live_model.py                    # root compatibility entrypoint
├── carry_model*.py                      # historical compatibility entrypoints
├── src/carry_trade/
│   ├── api/                             # Flask API implementation
│   ├── dashboard/                       # API/model dashboard integration
│   ├── data/
│   │   ├── collectors/                  # local collection scripts
│   │   ├── providers/                   # optional premium provider clients
│   │   ├── runtime/                     # long-running data-engine components
│   │   └── sources/                     # shared source clients
│   ├── modeling/
│   │   ├── backtests/                   # historical backtests
│   │   ├── experiments/                 # research model experiments
│   │   └── runners/                     # runnable dashboard/model workflows
│   ├── trading/                         # paper-only trading research scaffold
│   └── paths.py                         # shared repo-root and logs paths
├── frontend/                            # React/Vite dashboard
├── tests/                               # public-readiness, structure, model checks
├── docs/
│   ├── architecture/repository-structure.md
│   ├── dashboard.md
│   ├── process/branching-strategy.md
│   └── reports/                         # historical reports and summaries
├── scripts/                             # local validation and utility scripts
├── archive/legacy/                      # preserved historical experiments
└── logs/                                # local runtime data, ignored by git
```

## Package Boundaries

`src/carry_trade/api` owns the maintained Flask API. It should not contain data-collection scheduling or model-training logic beyond calling packaged interfaces.

`src/carry_trade/data/collectors` owns local data collection scripts. `src/carry_trade/data/sources` owns shared low-level source clients. `src/carry_trade/data/providers` owns optional premium clients. `src/carry_trade/data/runtime` owns longer-running data-engine code. Optional API keys remain environment-driven.

`src/carry_trade/modeling/experiments` owns feature engineering and model experiments. `src/carry_trade/modeling/runners` owns deterministic dashboard outputs. `src/carry_trade/modeling/backtests` owns historical backtests.

`src/carry_trade/dashboard` owns the integration layer that updates dashboard-facing logs.

`src/carry_trade/trading` stays paper-only research scaffolding unless the README and tests are deliberately changed.

## Root Compatibility Entrypoints

The root compatibility entrypoints exist so older commands and README examples continue to work. They should stay thin: add `src/` to `sys.path`, import the packaged function, and call it. New implementation code belongs under `src/carry_trade`.

## Documentation Placement

Architecture and process docs live under `docs/`. Branch rules live at `docs/process/branching-strategy.md`. Historical evaluation notes live under `docs/reports/` so the root README remains the public entrypoint instead of an inventory of every old experiment.
