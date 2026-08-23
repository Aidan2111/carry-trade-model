# Security Policy

## Supported versions

Security fixes target the latest code on `main` while the project is in alpha.

## Reporting a vulnerability

Do not open a public issue for an unpatched vulnerability or exposed secret.
Use GitHub's private vulnerability reporting feature when available, or contact
the maintainer through the private contact channel on
[aidanmarshall.ai](https://aidanmarshall.ai).

Include affected versions, reproduction steps, impact, and any suggested
mitigation. Do not include real API keys, account data, or proprietary market
data. The maintainer will acknowledge a complete report, investigate it, and
coordinate disclosure when a fix is available.

## Scope

Relevant reports include credential disclosure, unsafe default network
exposure, dependency compromise, path or command injection, fabricated data
presented as live data, and a path from research code to unintended live trades.
Model inaccuracy and market losses are generally methodology risks rather than
software vulnerabilities unless caused by a concrete integrity or security
failure.
