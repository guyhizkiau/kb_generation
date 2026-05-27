# Codebase findings — Log in to the SpecterX web platform

Sourced from `~/specterx-codebase/web-client` (cloned 2026-05-27).
File references are relative to `web-client/src/`.

---

## Auth architecture

The web client uses **AWS Amplify + Amazon Cognito** for authentication
(`components/AppAuthenticator/SignIn/index.tsx`, `stores/AuthSettingsStore/index.ts`).
Each tenant has its own Cognito User Pool and domain. There is also a WSO2 OIDC
path (`IS_WSO` flag) used for on-premises / enterprise deployments — the login
flow is different but the article's scope is the standard cloud login.

## Login URL pattern

Each tenant gets its own subdomain or custom domain. Observed patterns in env.ts:

- Cloud (SaaS): `https://<tenant>-app.specterx.com`
- Production default: `https://app.specterx.com`
- Shared portal: `https://share.specterx.com`
- Staging: `https://staging-app.specterx.com`
- Custom domain (enterprise): org-provided (e.g. `https://specterx.example.com`)

**Article implication:** tell the user "navigate to the URL your IT team or
SpecterX provided" — do not hardcode a single URL.

## SSO provider types

Supported federated providers (`config/env.ts` `SSOTypes` enum):

| Code | Provider |
|---|---|
| `cognito` | Amazon Cognito hosted UI (standard) |
| `google` | Google Workspace SSO |
| `microsoft` | Microsoft / Azure AD SSO |
| `okta` | Okta SSO |

Enterprise WSO2 / Kerberos deployments use a separate OIDC flow and are
out of scope for this end-user article.

## Exact UI error strings

Source: `content/general.json` → `auth.errors.*`

| Scenario | UI message |
|---|---|
| Account not yet provisioned | "You must be invited before you can sign in" |
| Invited to org but need admin contact | "You need to be invited to SpecterX to use the app. Please contact {{admin}} to request an invitation." |
| SSO / OAuth denied by provider | "Your auth provider doesn't allow you to sign in in our app" |
| Email not confirmed | "Please Confirm your email. Resend Confirmation Code if you haven't got one" |
| Admin trying to use OTP | "Administrators are not allowed to use OTP for login." |
| Collaborator trying to use OTP | "To complete your login, please use available options." |
| Generic server error | "We have had an error, please try again." |

**Article implication:** the article's error-state section should match
these exact strings. "You must be invited before you can sign in" is the
message for an unprovisioned account — not "account not found" or similar.

## Login components

| Component | Role |
|---|---|
| `AppAuthenticator/SignIn/` | Email + password form |
| `AppAuthenticator/FederatedButton/` | SSO provider buttons (Google, Microsoft, Okta) |
| `AppAuthenticator/OTPSignIn/` | One-time password flow (email-based) |
| `AppAuthenticator/ForgotPassword/` | Password reset entry point |
| `AppAuthenticator/MfaComp/` | MFA code entry (TOTP) |

## Feature flags relevant to login

From `stores/AuthSettingsStore/index.ts` and `config/env.ts`:

- `DISABLE_MFA_BEHIND_PROXY` — skips MFA step for API-proxy (NAS storage) deployments
- `DISABLE_OTP_BEHIND_PROXY` — skips OTP for the same deployments
- `IS_WSO` — WSO2 enterprise path (different login UI, out of scope)

## What this changes in the article

1. **Error state section**: use the exact strings above in the
   "What to do if..." callouts — already partially covered in the draft;
   confirm wording matches `content/general.json`.
2. **URL guidance**: "your organisation's SpecterX URL" is the right
   framing; no single canonical URL.
3. **No new steps needed**: the article's login flow (navigate → enter
   email → SSO redirect OR password) matches the component structure
   confirmed here.
