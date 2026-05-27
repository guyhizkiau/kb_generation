# Codebase findings — Set or reset your password

Sourced from `~/specterx-codebase/web-client` and
`~/specterx-codebase/admin-web-client` (cloned 2026-05-27).
File references are relative to each repo's `src/`.

---

## Auth architecture (web-client)

The end-user web app uses **AWS Amplify + Amazon Cognito**
(`components/AppAuthenticator/ForgotPassword/index.tsx`). The reset
flow is two Cognito calls:

1. `Auth.forgotPassword(email)` — Cognito sends a verification code by
   email.
2. `Auth.forgotPasswordSubmit(email, code, newPassword)` — Cognito
   validates the code and sets the new password.

On success, the user is redirected to `/signIn`.

## Reset entry point (web-client)

`components/AppAuthenticator/SignIn/index.tsx:257-258` renders a link
on the sign-in page:

```
<BaseAuthLink href="/forgotPassword">
    {i18n.t('signIn.forgotPassword')}
```

The translation key resolves to **"Reset password"** (not "Forgot
password?") — `content/general.json:1068`.

## Reset flow page (`/forgotPassword`)

`components/AppAuthenticator/ForgotPassword/index.tsx` defines a
three-state finite state machine:

| Step | UI title | UI subtitle | Submit button |
|---|---|---|---|
| `enterEmail` | "Reset password" | (no subtitle: the `firstStep.title` key in `content/general.json` is unused for this flow) | **Reset** |
| `createNewPassword` | "Create New Password" | "We've sent a code to your email address.\nEnter the code and your new password" | **Change Password** |
| `done` | (none; redirects to /signIn) | Success toast "Your password has been successfully changed" | — |

Source: `content/general.json:1089-1130`, verified against live UI on
2026-05-27 (see `research/ui-snapshot/`).

## Verification-code mechanics

- The code is **6 digits** (`ConfirmUser/index.tsx:74` validates
  `codeValue.length === 6`; the OTP input has 6 cells).
- Three failed code attempts ends the flow:
  `ConfirmUser/index.tsx:33,46-49,68-73`. The user is bounced back to
  `/signIn` and must request a fresh code.
- Resend has a 60-second cooldown (`ConfirmUser/index.tsx:22`:
  `RESEND_TIMEOUT_DEFAULT = 60`). A countdown timer is visible.
- Cognito default code expiry is 1 hour (no override in the codebase).

## Password rules (web-client)

`components/Common/PasswordValidation/index.tsx:12-19` defines five
mandatory rules:

| Rule | Regex |
|---|---|
| At least 8 characters | `(?=.{8,})` |
| At least 1 number | `(?=.*[0-9])` |
| At least 1 uppercase letter | `(?=.*[A-Z])` |
| At least 1 lowercase letter | `(?=.*[a-z])` |
| At least 1 special character | `(?=.*[!@#$%^&*()_~-])` |

The exact list of allowed special characters is `! @ # $ % ^ & * ( )
_ ~ -`. UI labels come from `content/general.json:22-29`:

```json
"passwordValidation": {
  "length": "At least 8 characters",
  "chars": "At least 1 special character",
  "numbers": "At least 1 number",
  "uppercase": "At least 1 uppercase letter",
  "lowercase": "At least 1 lowercase letter",
  "placeholder": "Create your password"
}
```

Each rule turns from grey to green as the user types
(`PasswordValidation.module.scss` -> `password-strength-good`).
**Change Password** stays disabled until all five turn green.

## Exact UI strings the article should match

Source: `content/general.json` and React components above.

| Where | UI string |
|---|---|
| Sign-in page link | "Reset password" |
| `/forgotPassword` page title (step 1) | "Reset password" |
| Email field placeholder | "Enter your email" |
| Step-1 submit button | "Reset" |
| Step-1 above-form button (if OTP allowed) | "Sign in with One Time Code" |
| Step-1 separator | "or create a new password" |
| Step-2 page title | "Create New Password" |
| Step-2 subtitle | "We've sent a code to your email address. Enter the code and your new password" |
| Code field placeholder | "Enter the code" |
| Resend link | "Didn't get the code? Resend Code" |
| Back link | "Back to the previous step" |
| Step-2 submit button | "Change Password" |
| Success toast (8 s) | "Your password has been successfully changed" |
| Page-level back link | "Back to Sign In" |
| Sign-in error for unprovisioned account | "You must be invited before you can sign in" |

The "Sign in with One Time Code" link above the form
(`ForgotPassword/index.tsx:84-90`) only appears for IP addresses
allowed to use OTP. For IPs behind the customer proxy
(`DISABLE_OTP_BEHIND_PROXY`), the link is hidden. The article should
not depend on the OTP link being visible.

## Routes

`components/AppAuthenticator/AuthContainer/AuthContainer.tsx:199-217`:

- `/signIn` — sign-in page
- `/forgotPassword` — reset flow (this article)
- `/signUp` — self-service registration (gated by `signUpForbidden`
  error for most tenants)
- `/confirmUser` — code confirmation reused for invitation flows
- `/OTPSignIn` — one-time-code sign-in

The reset flow is reachable directly at
`https://<tenant>.specterx.com/forgotPassword` but the documented
entry point is the **Reset password** link on the sign-in page. Don't
publish the direct URL.

## SSO behaviour

`config/env.ts` defines an `SSOTypes` enum:

| Code | Provider |
|---|---|
| `cognito` | Cognito hosted UI (email + password) |
| `google` | Google Workspace SSO |
| `microsoft` | Microsoft / Azure AD / Entra ID SSO |
| `okta` | Okta SSO |

For organizations where `SSOTypes.cognito` is **not** in the enabled
SSO list, the sign-in page omits the email/password fields and the
"Reset password" link, leaving only federated buttons (Google /
Microsoft / Okta). In that case the user's password is owned by the
identity provider, not by SpecterX, and the SpecterX reset flow does
nothing for them. The article calls this out explicitly.

## First-time password (admin-invited users)

Self-service sign-up is blocked for most tenants by Cognito's
`UserLambdaValidationException`, which the UI maps to
"You must be invited before you can sign in"
(`content/general.json:443,456`).

Admin-driven invitation paths are owned by the admin portal
(`admin-web-client`). When an admin creates a user, Cognito triggers
an invitation email containing a code. The same `Auth.forgotPassword`
+ `Auth.forgotPasswordSubmit` calls back the new user uses to set
their first password — i.e. the activation flow and the reset flow
share the same React components and the same email template
shape. The article documents this as a single procedure with two
entry points (admin invitation vs. user-initiated reset).

## Feature flags affecting the reset flow

From `config/env.ts`:

- `DISABLE_OTP_BEHIND_PROXY` — when true, hides the "Sign in with One
  Time Code" link on the reset page. Article-level note: the OTP link
  may or may not appear depending on the network.
- `DISABLE_MFA_BEHIND_PROXY` — relevant to login MFA, not reset.
- `IS_WSO` — WSO2 / on-prem path. Different reset UI; out of scope.

## Admin portal vs. end-user reset

`admin-web-client/client/src/pages/ForgotPassword.tsx` implements a
**separate** reset flow for `admin.specterx.com` (the admin portal).
Key differences from the end-user flow:

| Aspect | End-user (`app.specterx.com`) | Admin portal (`admin.specterx.com`) |
|---|---|---|
| Step-1 title | "Reset password" | "Forgot Password?" |
| Step-2 title | "Create New Password" | "Check your email" + "Create New Password" |
| Step-2 button | "Change Password" | "Save new password" |
| Done state | Success toast + redirect | Dedicated "Password Reset Successful" screen |
| Special chars allowed | `! @ # $ % ^ & * ( ) _ ~ -` | Broader set (`!@#$%^&*()_+\-=[]{};':"\|,.<>/?`) |

The article is for end users (`app.specterx.com`); it does not
document the admin portal flow.

## Recently modified files (last 90 days)

`git log --since="3 months ago" --name-only` against
`web-client/src/components/AppAuthenticator/ForgotPassword/`:

```
(no commits in window)
```

The end-user reset components are stable. UI drift risk is low. Same
check against `Common/PasswordValidation/` returns no recent commits.

## What this changes in the article

1. **Exact strings**: use "Reset password" (lower-case `p`) and
   "Change Password" verbatim. Do not write "Forgot password?" (that's
   the admin-portal copy) or "Reset Password" (wrong casing).
2. **Code length**: 6 digits, three attempts, 60-second resend cooldown.
3. **Password rules**: list all five rules explicitly. The special-char
   list is finite — include it.
4. **SSO branch**: name Google, Microsoft / Entra ID, Okta as the three
   SSO providers; their users do not use this flow.
5. **Activation flow**: same UI as reset, triggered by an admin
   invitation rather than a user click. Document both entry points.
