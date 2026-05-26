---
title: Log in to the SpecterX web platform
audience: end-user
estimated-reading-time: 3 min
prerequisites:
  - A SpecterX account (provisioned by your organisation's administrator)
  - Your organisation's SpecterX URL (either app.specterx.com or a tenant-specific subdomain such as yourorg.specterx.com)
  - The login method your organisation uses (single sign-on through Entra ID, Okta, or Google Cloud Identity; or email and password)
---

# Log in to the SpecterX web platform

This article walks you through signing in to SpecterX from a web
browser. By the end you'll have an active session and be on your
SpecterX dashboard, ready to upload, share, and manage protected
files.

## Before you start

Your administrator provisions SpecterX accounts. Before you can sign
in you need three things:

- **An account.** If you haven't received a welcome email from
  SpecterX (or from your IT team) confirming that your account has
  been created, contact your administrator. Self-service sign-up is
  not available.
- **Your sign-in URL.** Some organisations use the shared
  `https://app.specterx.com` URL; others use a tenant-specific
  subdomain like `https://yourorg.specterx.com` (replace `yourorg`
  with your organisation's name). If your administrator hasn't told
  you which to use, start with `https://app.specterx.com` — you'll be
  redirected to the right place if your organisation has a separate
  tenant URL. <!-- coverage decision: yes, plan entry calls out URL format -->
- **Your login method.** Most organisations use single sign-on (SSO)
  through Microsoft Entra ID, Okta, or Google Cloud Identity. A
  smaller number use email and password. If you're not sure which your
  organisation uses, ask your administrator or skip ahead — the
  sign-in page makes the available options visible.

## Steps

### 1. Open the SpecterX sign-in page

In your browser, navigate to your organisation's SpecterX URL (the
one from the prerequisites above). If you typed
`https://app.specterx.com`, the app redirects you automatically to
`https://app.specterx.com/signIn`.

> Screenshot: the SpecterX sign-in page, showing the "Sign in with
> Google" button at the top, the "or sign in with" divider, the email
> and password fields, and the greyed-out "Sign In" button.

### 2. Choose your sign-in method

Look at the sign-in page and pick the method that matches your
organisation:

- **Single sign-on (Google).** If your organisation uses Google Cloud
  Identity, click **Sign in with Google** at the top of the page.
  Continue with step 3a.
- **Single sign-on (Entra ID, Okta, or other corporate IdP).** If
  your organisation uses Microsoft Entra ID, Okta, or another
  enterprise identity provider, you should land on a sign-in page
  that's already redirecting you to your IdP, or that shows a button
  for your IdP instead of (or in addition to) the email and password
  form. [verify in test — confirm what an Entra/Okta-bound tenant
  actually shows on its sign-in page]
- **Email and password.** If your organisation doesn't use SSO, use
  the email field and password field on the sign-in page. Continue
  with step 3b.

### 3a. Sign in through your identity provider (SSO users)

Click your organisation's SSO button — for example, **Sign in with
Google** — and complete the prompts your identity provider shows
(typing your work email, approving an MFA challenge, or whatever your
IT team has configured).

> Screenshot: the identity-provider sign-in screen (Google account
> picker, Entra ID prompt, or Okta tile), opened from the SpecterX
> sign-in page.

After the identity provider accepts your sign-in it redirects you
back to SpecterX. Skip to step 4.

### 3b. Sign in with email and password (non-SSO users)

Click the **Enter your email** field and type the email address your
administrator registered for you. Then click **Enter your password**
and type your password. Use the eye icon at the right edge of the
password field to reveal what you've typed if you need to check it.

Click **Sign In**. The button is greyed out until both fields contain
text, then activates.

> Screenshot: the sign-in page with the email field filled in, the
> password field filled in (characters masked), and the Sign In
> button now active.

### 4. Confirm you've reached your dashboard

After a successful sign-in, SpecterX loads your dashboard at
`https://app.specterx.com/my-files`. The browser tab title becomes
**My Files - SpecterX**, the main content area heading reads
**My Files**, and your signed-in email address appears in the
top-right of the page header. [verify in test — confirm whether all
tenants land at `/my-files` or whether the landing page varies]

> Screenshot: the My Files dashboard, with the "My Files" heading
> visible and the signed-in email address visible in the top-right.

## Troubleshooting

**"Invalid email or password" error.** Double-check the email
address — use the one your administrator registered, not a personal
address. Passwords are case-sensitive. If you've forgotten your
password, click **Reset password** below the Sign In button. See the
*Set or reset your password* article for the full reset flow.

**SSO says "access denied" or "not authorised".** Your identity
provider authenticated you, but SpecterX hasn't been told to let your
account in. This usually means your administrator hasn't finished
provisioning your account in SpecterX (even if your IdP account
exists). Contact your administrator and ask them to confirm that
your SpecterX account is active and that your email address matches
what's in the identity provider.

**"This account hasn't been set up yet" or your email isn't
recognised.** Your account hasn't been provisioned in SpecterX.
Sign-up is administrator-driven, not self-service. Contact your IT
team or whoever manages SpecterX at your organisation.

**Sign-in page won't load.** Confirm you typed the URL correctly. If
your organisation uses a tenant-specific subdomain, you need that
exact URL — `https://app.specterx.com` will not show your
organisation's branded sign-in page or SSO button. If the URL is
right and the page still won't load, check your internet connection
or try a different browser.

**Signed in but redirected straight back to the sign-in page.** Your
browser may be blocking cookies for `app.specterx.com` (or your
tenant subdomain). Enable cookies for that host and try again.

## What this article doesn't cover

- Creating your first password or resetting a forgotten one — see
  *Set or reset your password*.
- A high-level overview of what SpecterX does — see *What is
  SpecterX?*.
- Administrator-side user provisioning, SSO configuration, and IdP
  setup — those are covered in the SpecterX admin documentation.

## Related articles

- *Set or reset your password*
- *What is SpecterX?*
