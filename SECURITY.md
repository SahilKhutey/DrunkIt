# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 0.x (MVP) | ✅ Active development |

---

## Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

Report vulnerabilities via **GitHub Security Advisories**:
👉 [Report a vulnerability](../../security/advisories/new)

Alternatively, email the security team directly:
📧 `security@drunkit.in` *(configure this address before going live)*

Please include:
- Description of the vulnerability and its potential impact
- Steps to reproduce the issue
- Affected component(s) and version
- Any proof-of-concept code (responsibly)

---

## Response SLAs

| Severity | Acknowledge | Triage | Patch |
|---|---|---|---|
| Critical (RCE, auth bypass, PII leak) | 24 hours | 48 hours | 7 days |
| High (privilege escalation, data exposure) | 48 hours | 5 days | 14 days |
| Medium (CSRF, rate-limit bypass) | 5 days | 10 days | 30 days |
| Low (info disclosure, best-practice gap) | 10 days | 21 days | 90 days |

---

## Scope

The following are **in scope** for security reports:

- `services/identity-service/` — Authentication, OTP, session management
- `services/payment-service/` — Payment authorization and capture flows
- `services/compliance-service/` — Age/eligibility verification
- `services/audit-service/` — Hash-chained audit trail integrity
- `services/api-gateway/` — Rate limiting, request validation
- `apps/consumer-web/`, `apps/drunkit-web/` — Consumer-facing frontends
- `packages/` — Shared SDK and event contract libraries

The following are **out of scope**:

- Issues in third-party dependencies already reported upstream
- Vulnerabilities in self-hosted infrastructure not managed by this repo
- Social engineering attacks
- Physical access attacks

---

## Secret Handling Policy

1. **No secrets in version control.** All credentials must use environment variables referencing a secrets manager.
2. **Use `.env.example` as the template.** Never commit a populated `.env` file.
3. **Default credentials in `docker-compose.yml` are for local development only.** They must never be used in staging or production. Use secret manager injection (e.g., AWS Secrets Manager, HashiCorp Vault, GitHub Secrets).
4. **Rotate immediately** if a secret is accidentally committed. Treat any committed secret as compromised.

### Credential Rotation Process

```
1. Identify the exposed secret and its scope
2. Rotate the credential in the issuing system immediately
3. Revoke all sessions/tokens issued with the old credential
4. Update the secret manager / GitHub Secrets
5. Redeploy affected services
6. Add a git note documenting the rotation (without the secret value)
7. Perform a post-incident review if the credential was active > 1 hour
```

---

## Security Contacts (CODEOWNERS Mapping)

| Area | Owner |
|---|---|
| Authentication / Identity | `@faccp/security-admin` |
| Payment & PCI concerns | `@faccp/security-admin` |
| Compliance & age verification | `@faccp/compliance-admin` |
| Audit trail integrity | `@faccp/audit-admin` |
| Infrastructure / secrets | `@faccp/platform-admin` |

---

## Responsible Disclosure

We follow a **90-day coordinated disclosure** policy:

1. Researcher reports via the advisory channel above
2. FACCP security team acknowledges within the SLA above
3. A fix is developed and deployed
4. A CVE is requested if applicable
5. A security advisory is published after the fix is live or after 90 days, whichever comes first

We will not take legal action against researchers who act in good faith and follow this policy.

---

## Incident Escalation

For active exploitation or critical production incidents:

1. Immediately isolate the affected service (`docker compose stop <service>`)
2. Notify `@faccp/security-admin` and `@faccp/platform-admin` via the emergency channel
3. Preserve logs and forensic evidence before any remediation
4. Follow the incident runbook: [`runbooks/security-incident.md`](runbooks/security-incident.md)
5. Post a status update to stakeholders within 2 hours of detection

---

*This policy applies to the FACCP / DrunkIt platform and all repositories under this organization.*
