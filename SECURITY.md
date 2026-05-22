# Security Policy

## Supported Versions

This repository is pre-1.0 proposal research software. Only the default branch receives security attention.

## Reporting a Vulnerability

Do not open a public issue for security problems. Report privately to Techman Studios using the security contact designated for the project.

Include:

- A short description and potential impact.
- Steps to reproduce or a minimal proof of concept.
- Affected commit or file path.
- Whether any secret, CUI, export-controlled material, or third-party proprietary data may be involved.

## Handling Rules

- Do not commit secrets, tokens, credentials, or `.env` files.
- Do not commit classified information or CUI.
- Treat DON26BZ01-NV023 work as ITAR/EAR-sensitive until reviewed.
- Keep generated artifacts under `artifacts/` unless they are intentionally curated and reviewed for inclusion.
