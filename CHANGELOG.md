# Changelog

Notable user-visible, compatibility, security, and release changes are recorded
here.

## Unreleased

- Stop returning internal exception and model-runner error details in API responses;
  structured model-update failures now return HTTP 500. Diagnostics stay in server logs.
- Refresh compatible dashboard dependencies to remove known npm advisories.
- Use Node 24 in CI and releases, with Node 22.12 as the supported local minimum.
- Fetch research news feeds over HTTPS, refuse redirects, and parse fetched
  content without allowing secondary URL or local-file reads.
- Exclude generated frontend dependencies and bundles from Python source
  distributions while retaining authored frontend configuration files.

## 0.1.0 - 2026-08-23

- Added installable API and model-runner commands and distribution validation.
- Added bounded Python dependencies and optional data/boosted-model extras.
- Raised the Python minimum to 3.11 because Python 3.9 is end-of-life and the
  maintained scientific stack now targets supported interpreter releases.
- Expanded CI to cover the declared Python baseline and full frontend audits.
- Updated the frontend lockfile to a patched `nanoid` release.
- Added standard open-source governance, support, security, and contribution
  documentation.

- Organized the maintained Python implementation under `src/carry_trade`.
- Added the Flask API, React dashboard, deterministic system evaluation, model
  validation tests, and explicit research/data-provenance boundaries.
