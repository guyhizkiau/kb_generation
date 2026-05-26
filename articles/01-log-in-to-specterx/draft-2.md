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
  you which to use, start with `https://app.specterx.com` — typing
  that URL redirects you to `https://app.specterx.com/signIn`, and
  you'll be sent on to your organisation's branded sign-in page if
  your tenant has a separate URL.
- **Your login method.** Most organisations use single sign-on (SSO)
  through Microsoft Entra ID, Okta, or Google Cloud Identity. A
  smaller number use email and password. If you're not sure which
  your organisation uses, look at the sign-in page — the available
  options are visible there.

## Steps

### 1. Open the SpecterX sign-in page

In your browser, navigate to your organisation's SpecterX URL (the
one from the prerequisites above). If you typed
`https://app.specterx.com`, the app redirects you automatically to
`https://app.specterx.com/signIn` and the browser tab title becomes
**Login - SpecterX**.

The sign-in page shows a "Welcome to SpecterX" heading, a primary
**Sign in with Google** button, an *"or sign in with"* divider, the
email and password fields, the **Sign In** submit button, and a
**Reset password** link at the bottom.

![Sign-in page at app.specterx.com/signIn showing the SpecterX header, a "Welcome to SpecterX" heading, the Sign in with Google button, an "or sign in with" divider, an email field placeholder "Enter your email", a password field placeholder "Enter your password" with an eye icon, a greyed-out Sign In button, and a Reset password link.](screenshots/01-login-page.png)

### 2. Choose your sign-in method

Pick the method that matches your organisation:

- **Single sign-on (Google).** If your organisation uses Google Cloud
  Identity, click **Sign in with Google** at the top of the page.
  Continue with step 3a.
- **Single sign-on (Entra ID, Okta, or other corporate IdP).** If
  your organisation uses Microsoft Entra ID, Okta, or another
  enterprise identity provider, your tenant's sign-in page is
  configured to redirect you to your IdP — or to show an IdP-branded
  button in place of (or in addition to) the email and password form.
  Use whatever your tenant's page shows.
- **Email and password.** If your organisation doesn't use SSO, use
  the email and password fields. Continue with step 3b.

> ⚠ Verification incomplete: the screenshot above is from the shared
> `https://app.specterx.com/signIn` page, captured against an account
> not bound to a corporate IdP. The exact appearance of an Entra ID,
> Okta, or other tenant-specific sign-in page wasn't exercised in
> this test pass. Please confirm during review.

### 3a. Sign in through your identity provider (SSO users)

Click your organisation's SSO button — for example, **Sign in with
Google** — and complete the prompts your identity provider shows
(typing your work email, approving an MFA challenge, or whatever
your IT team has configured).

After the identity provider accepts your sign-in it redirects you
back to SpecterX. Skip to step 4.

### 3b. Sign in with email and password (non-SSO users)

Click the **Enter your email** field and type the email address your
administrator registered for you. Then click **Enter your password**
and type your password. You can use the eye icon at the right edge
of the password field to reveal what you've typed if you need to
check it.

Click **Sign In**. The button is greyed out until both fields
contain text, then activates.

### 4. Confirm you've reached your dashboard

After a successful sign-in, SpecterX loads your dashboard at
`https://app.specterx.com/my-files`. You'll see:

- The browser tab title changes to **My Files - SpecterX**.
- The main content area heading reads **My Files**.
- Your signed-in email address appears in the top-right of the page
  header.
- A left-hand navigation rail shows entries like *My files*, *Shared
  with me*, *My workspaces*, *All files*, *Policies*, *Users*,
  *Audit logs*, and *Settings* (the entries you see depend on your
  permissions).

If you see this dashboard, you're signed in.

## Troubleshooting

**"Invalid email or password" error.** Double-check the email
address — use the one your administrator registered, not a personal
address. Passwords are case-sensitive. If you've forgotten your
password, click **Reset password** below the **Sign In** button. See
*Set or reset your password* for the full reset flow.

**SSO says "access denied" or "not authorised".** Your identity
provider authenticated you, but SpecterX hasn't been told to let
your account in. This usually means your administrator hasn't
finished provisioning your account in SpecterX (even if your IdP
account exists). Contact your administrator and ask them to confirm
that your SpecterX account is active and that your email address
matches what's in the identity provider.

**"This account hasn't been set up yet" or your email isn't
recognised.** Your account hasn't been provisioned in SpecterX.
Sign-up is administrator-driven, not self-service. Contact your IT
team or whoever manages SpecterX at your organisation.

**Sign-in page won't load.** Confirm you typed the URL correctly. If
your organisation uses a tenant-specific subdomain, you need that
exact URL — `https://app.specterx.com` won't show your
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
