# Security Policy

This project handles pharmacy workflow messages, so privacy and operational safety are part of the security boundary.

## Supported Scope

The current MVP is local-first, with a documented VPS dry-run and internal LLM shadow operation. It is not yet production-hardened or clinically validated. See [the current handoff](docs/agents/HANDOFF.md) for deployment boundaries.

## Reporting Security Issues

Do not open public GitHub issues with secrets, tokens, private webhook URLs, raw payloads, chat ids, patient details, or screenshots that expose sensitive data.

For now, report security concerns privately to the repository owner. Include:

1. What happened.
2. Which file, endpoint, or command is involved.
3. Whether any secret or sensitive data may have been exposed.
4. The smallest safe reproduction steps using fake data.

## Secret Handling

- Never commit `.env`.
- Never commit Bale bot tokens, webhook secrets, private keys, cookies, or service credentials.
- Use `.env.example` for placeholder variable names only.
- Keep `BALE_ENABLE_SENDING=false` until real sending is explicitly approved.

## Sensitive Data Handling

- Do not log raw webhook payloads by default.
- Do not log full message text, chat ids, tokens, or webhook secrets.
- Store only what is required for auditability and workflow continuity.
- Define retention and deletion rules before broad patient-facing use.

## Deployment Security Gates

Before public exposure:

1. Confirm exact Bale webhook and send-message schemas.
2. Confirm whether Bale supports webhook signature or header authentication.
3. Use HTTPS through a reverse proxy.
4. Use a strong `BALE_WEBHOOK_SECRET`.
5. Verify backup and restore for SQLite data.
6. Verify logs remain sanitized.
