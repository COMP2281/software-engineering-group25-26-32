# Security Policy

## Supported versions

This project is maintained on the `main` branch.

## Reporting a vulnerability

Do not open a public issue for secrets, API keys, authentication bypasses, or data exposure.

Report privately to the maintainers/team members first.

## Secret handling

Never commit:

- `.env` files
- Gemini API keys
- `SECRET_KEY`
- local database files
- generated index files
- credentials or admin passwords

If a secret is committed accidentally:

1. Revoke or rotate the secret immediately.
2. Remove it from the repository.
3. Check the commit history.
4. Notify the team.