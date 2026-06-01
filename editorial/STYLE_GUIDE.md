# SpecterX KB — Writing Style Guide

*Draft style guide for SpecterX knowledge-base articles. This guide should be treated as the starting editorial canon until enough approved articles exist to extract stronger evidence from real usage.*

---

## 1. North star

SpecterX KB articles should read like verified product instructions, not marketing copy.

The article should feel like a competent support person wrote it while looking at the product: clear, grounded, direct, and specific. Do not try to make articles sound “more human” by adding jokes, typos, casual filler, or fake personality. Human writing in documentation comes from judgment: knowing what matters, what can be omitted, and what must be verified.

Good SpecterX documentation is:

- Product-grounded
- Short where possible
- Specific where useful
- Honest about prerequisites and limitations
- Written for the user’s task, not for brand polish

Avoid writing that feels like a generic SaaS help-center article generated from a prompt.

---

## 2. Voice and tone

### Person

Use second person: **you**.

Good:

> Enter your work email address.

Avoid:

> The user should enter their work email address.

Use “administrator” only when the action is outside the reader’s control.

Good:

> If your account has not been created yet, contact your administrator.

### Tense

Use present tense for product behavior.

Good:

> SpecterX opens the My Files page.

Use future tense only when describing what happens after the user takes an action.

Good:

> After you enter your email address, SpecterX will show the login methods available for your account.

### Tone

The tone should be:

- Calm
- Practical
- Direct
- Slightly dry
- Product-specific
- Low-marketing

Do not over-reassure the user. Do not use motivational article intros.

Avoid:

> By the end of this article, you’ll be ready to upload, share, and manage protected files.

Prefer:

> Use this article to sign in to SpecterX from a browser.

### Contractions

Use contractions naturally in end-user articles.

Good:

> If you don’t know which login method to use, check the sign-in page.

Avoid contractions in:

- Legal notes
- Security warnings
- Formal admin documentation
- Error-message explanations where precision matters

---

## 3. Article openings

Most procedural articles should start with one short paragraph, usually 25–60 words.

The intro should answer:

- What task is this article for?
- Who is it for?
- What must be true before the user can do it?

Good:

> Use this article to sign in to SpecterX from a browser. Your administrator must create your account before you can sign in.

Good:

> Use this article to reset your SpecterX password if you forgot it or need to create one for the first time.

Avoid:

> This article walks you through the process of signing in to SpecterX. By the end, you’ll have an active session and be ready to upload, share, and manage protected files.

Do not start routine procedural articles with:

- “By the end of this article…”
- “This guide will walk you through…”
- “In this article, we’ll show you how to…”
- “You can easily…”
- “SpecterX makes it simple to…”

These phrases are not always wrong, but they often create generic, AI-polished prose.

---

## 4. Structure

### Default procedural structure

Use this structure for most how-to articles:

```md
# Article title

Short intro.

## Before you start

Prerequisites, only if needed.

## Steps

Numbered steps.

## Troubleshooting

Only if common failure cases exist.

## Related articles

Short list of relevant articles.
```

Not every article needs every section.

### When to use “Before you start”

Use **Before you start** when the user needs something before the task can succeed.

Examples:

- An administrator must create the account.
- The user needs a tenant-specific URL.
- The user needs a specific permission.
- The user needs an integration installed.
- The user needs access to a specific file, workspace, or policy.

Do not use **Before you start** for obvious facts.

Avoid:

> Before you start, make sure you have an internet connection.

Unless connectivity is a known issue for the task.

### When to use “What this article doesn’t cover”

Avoid this section by default.

Prefer **Related articles**.

Use “What this article doesn’t cover” only when the boundary prevents real confusion.

Good:

> This article is for end users signing in from a browser. Administrator setup for SSO is covered in the admin documentation.

Avoid:

> This article doesn’t cover creating your first password, resetting a forgotten one, a high-level overview of SpecterX, administrator-side user provisioning, SSO configuration, and IdP setup.

That reads like a generated checklist.

---

## 5. Step format

### General rule

Use one primary action per step.

Good:

> 1. Go to your SpecterX sign-in page.
> 2. Enter your work email address.
> 3. Click **Continue**.

Avoid combining unrelated actions:

> 1. Go to the sign-in page, enter your email, choose your login method, and confirm that the dashboard opens.

### Step length

Steps should usually be one sentence.

Add a second sentence only when it prevents confusion.

Good:

> Enter your password in the **Password** field. You can click the eye icon to show the password before you submit it.

Avoid long explanatory steps that contain multiple branches.

### Step names

Prefer direct imperative steps.

Good:

> Click **Sign In**.

Acceptable for longer procedures:

> ### 1. Open the sign-in page

Then provide the action below.

### Sub-steps

Use sub-steps when one step has a small set of related actions under the same goal.

Good:

```md
1. Open the sign-in page.
2. Sign in using one of the available methods:
   - Click **Sign in with Google** if your organization uses Google SSO.
   - Enter your email and password if your organization uses password login.
```

Avoid deep nesting. If a step has more than 3–4 sub-steps, split it into separate top-level steps.

---

## 6. Canonical UI verbs

Use consistent verbs for UI actions.

| Action type | Canonical verb | Example |
|---|---|---|
| Open a URL | Go to | Go to `https://app.specterx.com/signIn`. |
| Button or link | Click | Click **Sign In**. |
| Text field | Enter | Enter your email address in the **Email** field. |
| Dropdown, menu, list, radio option | Select | Select **Viewer** from the **Role** menu. |
| Checkbox | Select / Clear | Select **Remember me**. Clear **Require login**. |
| Toggle | Turn on / Turn off | Turn on **Require authentication**. |
| Page, dialog, drawer, file, menu | Open | Open the **Settings** page. |
| Drag interaction | Drag | Drag the file into the upload area. |
| File upload | Upload | Upload the file you want to share. |
| Authentication | Sign in / Sign out | Sign in to SpecterX. |
| Account creation | Create | Create a new user. |
| Saving changes | Click / Save | Click **Save**. |

### “Sign in” vs “login”

Use **sign in** as the verb.

Good:

> Sign in to SpecterX.

Avoid:

> Login to SpecterX.

Use **login** only as a noun or adjective when needed.

Good:

> The login page opens.

---

## 7. Product specificity and verification

Specificity makes documentation trustworthy, but only when verified.

### Use exact UI labels

Use exact labels for:

- Buttons
- Fields
- Page names
- Menu items
- Error messages
- URLs
- Permission names
- Integration names

Good:

> Click **Reset password**.

Good:

> Open **My Files**.

### Do not invent exact behavior

Do not write exact URLs, page titles, redirects, or error strings unless they were verified in the product.

Risky:

> After a successful sign-in, SpecterX loads your dashboard at `https://app.specterx.com/my-files`.

Better:

> After a successful sign-in, SpecterX opens your default page. For most users, this is **My Files**.

### Quote error messages only when verified

If the product says:

> Invalid email or password

Use the exact message.

If you are not sure, do not quote it.

Good:

> If you see an error that says your email or password is invalid, check that you entered the email address your administrator registered.

Avoid:

> If you see “Invalid email or password,” check your email address.

Unless that exact string is confirmed.

---

## 8. Handling variations and tenant-specific behavior

Many SpecterX flows vary by tenant, role, policy, or integration. Explain variations without turning the main path into a list of every possible configuration.

### Write the common path first

Good:

> Enter your email address. SpecterX shows the login methods available for your account.

Then explain the variation:

> If your organization uses SSO, follow the redirect to your identity provider.

Avoid starting with every possible path:

> Some organizations use the shared URL, others use a tenant-specific subdomain, some use Google, others use Entra ID, Okta, or another IdP, and a smaller number use email and password.

### Keep edge cases out of the main flow

Put edge cases in:

- Notes
- Troubleshooting
- Related articles
- Admin documentation

The main flow should stay readable.

### Use examples sparingly

Good:

> Your organization may use SSO, such as Google, Microsoft Entra ID, or Okta.

Avoid:

> Your organization may use Microsoft Entra ID, Okta, Google Cloud Identity, Ping Identity, OneLogin, or another enterprise identity provider.

Unless the list is important to the task.

---

## 9. Screenshots

### When to use screenshots

Use screenshots when they help the user recognize:

- A page
- A dialog
- A button or menu that may be hard to find
- A successful final state
- A configuration state with several fields

Do not add screenshots for every single click if the text is enough.

### What to include in a screenshot

**Rule:** Every screenshot committed to an article must be cropped to the relevant region. Full-page or full-viewport captures are not acceptable in published articles — they force the reader to hunt for the element the step is about and they pollute the page with chrome, footers, and empty whitespace. If the capture step produced a full-viewport image, crop it before committing the article. See **Cropping** below for the mechanics.

A screenshot should show only the part of the UI the step refers to, plus just enough surrounding context for the reader to locate it on the real page.

Include:

- The UI element the step is about (button, field, dialog, menu, table, etc.).
- Enough adjacent context that the reader can place it — typically the page heading, the section heading, or the panel the element lives in.
- For a "successful final state" screenshot, include the cues that prove success: the page heading, the signed-in identity, or the row/item that confirms the action completed.

Exclude:

- Empty whitespace above, below, or beside the relevant region.
- Browser chrome (address bar, tabs, bookmarks bar). Capture the rendered page, not the browser window.
- The OS taskbar, dock, or desktop.
- Unrelated navigation, footers, language pickers, support widgets, cookie banners, and other chrome that is not part of the step.
- Anything outside the article's scope — do not capture three features in one screenshot just because they were visible on screen.

If the relevant region is only a small part of the page, crop tightly to that region. The reader should not have to hunt across a full-page screenshot to find the element the step mentions.

### How to capture a screenshot

- Capture at a desktop viewport width of 1280 px or larger. Use the same width across screenshots in the same article so the UI scale is consistent.
- Use the default product theme unless the article is specifically about a theme variation.
- Use a clean test tenant. The visible data must not contain real customer names, real file names, real email addresses other than the test account, or any other PII. See the sensitive-terms list under `tester/sensitive-terms.txt` and the rule in `CLAUDE.md` about `screenshots/_flagged/`.
- Sign in as the role the article is written for (end user, administrator, etc.). Do not capture an admin view to illustrate an end-user step.
- Dismiss unrelated overlays (tour bubbles, "what's new" popups, cookie banners, browser notification prompts) before capturing, unless the overlay is the subject of the step.
- Save as PNG. Use the file name pattern `NN-short-description.png` (for example `01-login-page.png`, `02-dashboard.png`) and store under `workspace/articles/NN-slug/screenshots/`.

#### Pre-capture cleanup checklist

Before pressing the shutter on any screenshot, walk through this list. The goal is a frame that contains only the UI the step refers to — not the chrome of the surrounding app or third-party host (Gmail, Outlook, etc.).

- **Dismiss promotional / onboarding popups.** Examples seen in practice: Gmail's "Start a chat" tour bubble (close with the **X** in the top-right corner of the bubble), Google Workspace "what's new" cards, browser update banners. None of these are part of the SpecterX flow and they cover the area the reader needs to see.
- **Clear "this message is spam" / "Report not spam" banners.** If the verification email landed in spam and Gmail (or any other mail client) is showing a yellow/grey "Why is this message in spam?" banner with a **Report not spam** / **Not spam** button, click that button before capturing. The banner moves the email back to the inbox and disappears, leaving a clean message body.
- **Avoid thread collation in mailbox screenshots.** Mail clients group messages with the same subject into a single thread. If a previous test run already left a verification or reset email in the mailbox, the new email collates with it and the screenshot shows two stacked rows instead of one. Before triggering a new email, delete (or permanently delete from Spam) any prior emails from the same sender / with the same subject, so the new capture shows a single, fresh row.
- **Close any unrelated browser dialogs.** Password-save prompts, translate-this-page bars, autofill prompts.

If any of these are still visible when you press the shutter, recapture — do not commit the dirty frame.

### Cropping

After capture, crop to the relevant region:

- For a single dialog or form, crop to the dialog or form plus a thin margin (roughly 20–40 px of surrounding whitespace).
- For a page-level "you are now here" screenshot, keep the page header (so the page name and signed-in account are visible) and the top of the main content area. Drop the footer and any long scroll region below the fold.
- For a table or list, keep the column headers and the first few rows. Do not include the entire list unless the length itself is the point.
- Do not stretch or rescale the cropped image to fill a larger frame. Save the crop at its natural pixel dimensions.

**Special cases — screenshots that almost always need a tight crop:**

- **Email inbox listings (Gmail, Outlook, etc.).** Crop to the row(s) of interest plus the column headers / "1 of N" counter that places them on the page. Drop the left-hand label nav, the right-hand Google-Apps sidebar, the footer, and any empty space below the rows.
- **Email message bodies.** Crop to the sender line, the subject, and the message body itself. Drop everything outside the open-message panel (label nav, sidebars, the empty area below the message).
- **Toast / banner notifications.** These appear briefly at the top or corner of the screen. Crop to the toast plus enough of the surrounding page to identify *where* the toast appeared (e.g., for a post-reset confirmation, keep enough of the sign-in page header to show the user is back on the sign-in page). A toast floating on top of an otherwise full-viewport screenshot is not acceptable — the reader's eye has to hunt for a 36 px-tall element in a 900 px frame.

### Annotations and redaction

- Use annotations only when necessary (see "Annotations" below).
- If a screenshot must include data that could identify a real customer, user, or file, redact it before committing. Solid-fill redaction boxes are preferred over blur. If redaction would obscure most of the screenshot, recapture in the clean test tenant instead.

### Screenshot density

For a short procedural article, 1–3 screenshots is usually enough.

Use more screenshots for:

- Integration setup
- Admin configuration
- Multi-screen flows
- Permission or policy setup
- Troubleshooting where visual recognition matters

### Screenshot captions

Captions should be short labels.

Good:

> SpecterX sign-in page

Good:

> Reset password link

Good:

> My Files page

Avoid visible captions that describe every UI element:

> Sign-in page showing the SpecterX header, a Welcome to SpecterX heading, a Sign in with Google button, an email field, a password field, a greyed-out Sign In button, and a Reset password link.

That may be useful as alt text, but it should not be visible article prose.

### Do not duplicate screenshot content in prose

Bad:

> The sign-in page shows a Welcome heading, a Google button, an email field, a password field, and a Reset password link.
>
> Screenshot: Sign-in page showing the Welcome heading, Google button, email field, password field, and Reset password link.

Better:

> The sign-in page shows the login options available for your organization.
>
> Screenshot: SpecterX sign-in page

### Annotations

Use annotations only when necessary.

Avoid default red boxes and arrows unless the approved screenshot style establishes them.

If screenshots are annotated, keep them consistent across the KB.

---

## 10. Troubleshooting

Use symptom-based troubleshooting.

Each troubleshooting item should follow this shape:

```md
### Symptom or error

Likely cause. Action to fix it.
```

Good:

```md
### You cannot sign in with SSO

Your identity provider accepted your login, but your SpecterX account may not be active. Contact your administrator and ask them to confirm that your SpecterX user exists and matches your identity provider email address.
```

Good:

```md
### The sign-in page keeps reloading

Your browser may be blocking cookies for SpecterX. Allow cookies for your SpecterX domain and try again.
```

Avoid long paragraphs that mix multiple symptoms, causes, and fixes.

### Troubleshooting tone

Be direct. Do not blame the user.

Good:

> Check that you are using the email address your administrator registered.

Avoid:

> Make sure you did not accidentally use the wrong email address.

### Admin escalation

When the user cannot fix the issue, say exactly what to ask the administrator to check.

Good:

> Contact your administrator and ask them to confirm that your SpecterX account is active and that your email address matches your identity provider email address.

Avoid:

> Contact your administrator for help.

That is too vague.

---

## 11. Related articles

Use related articles to move secondary topics out of the main article.

Good related articles for a sign-in article:

- Set or reset your password
- Troubleshoot sign-in issues
- What is SpecterX?
- Configure SSO for SpecterX

Keep related articles short and relevant. Do not include broad or loosely related links just to fill the section.

---

## 12. Vocabulary

### Preferred terms

| Preferred term | Avoid | Notes |
|---|---|---|
| sign in | login as a verb | Use “login” only as a noun/adjective. |
| sign out | logout as a verb | Use “logout” only as a noun/adjective if needed. |
| administrator | admin, IT guy | Use “admin” only if the product UI uses it. |
| organization | organisation | Use American English unless the company chooses otherwise. |
| email address | email | Use “email” as shorthand only when natural. |
| identity provider | IdP | Spell out on first use. |
| single sign-on | SSO | Spell out on first use. |
| Microsoft Entra ID | Azure AD | Use current Microsoft naming unless referring to legacy UI. |
| Google Workspace / Google Cloud Identity | Google SSO | Use the product-specific term when known. |
| tenant-specific URL | branded URL | Use “branded” only if branding is the point. |
| My Files | my files | Match UI capitalization. |

### Capitalization

Match the product UI for labels and page names.

Good:

> Open **My Files**.

Use sentence case for headings unless the UI label requires otherwise.

---

## 13. Words and phrases to avoid

Avoid generic AI-polish words unless they are necessary and accurate.

### Usually avoid

- simply
- easily
- seamlessly
- quickly
- intuitive
- robust
- powerful
- streamlined
- leverage
- utilize
- in order to
- ensure that
- allows you to, when “you can” is better
- ready to, when describing a routine task
- best fits your needs, unless a choice is being explained

### Replacements

| Avoid | Prefer |
|---|---|
| Simply click **Sign In**. | Click **Sign In**. |
| Navigate to the login page. | Go to the login page. |
| Utilize the reset flow. | Reset your password. |
| In order to sign in, enter your email. | To sign in, enter your email. |
| Ensure that cookies are enabled. | Make sure cookies are enabled. / Allow cookies. |
| This allows you to manage files. | You can manage files. |

---

## 13a. Punctuation

### Reduce dashes overall

Dashes of any kind add visual noise and often signal a sentence that should have been split. Reach for a period or a comma first. Reserve dashes for cases where they carry meaning that other punctuation cannot.

### Never use em dashes (long dashes)

Do not use em dashes (`—`, U+2014) anywhere in article prose, headings, captions, alt text, or published HTML. This rule is absolute. There is no acceptable use of an em dash in a SpecterX KB article.

Em dashes are heavy punctuation that reads as informal or rushed. Break the sentence instead.

Avoid:

> Your administrator must create your account — self-service sign-up is not available.

Prefer:

> Your administrator must create your account. Self-service sign-up is not available.

Or restructure:

> Self-service sign-up is not available. Your administrator creates all accounts.

Em dashes are also ambiguous when copied into CMS platforms like ZenDesk, which may render the Unicode character inconsistently.

Before committing, grep the article for `—` (U+2014) and remove every occurrence.

### En dashes and hyphens

Use a hyphen (`-`) for compound modifiers: `tenant-specific URL`, `self-service sign-up`.

Use an en dash (`–`, U+2013) only in numeric ranges in reference tables: `3–5 screenshots`. Not in prose. Prefer the word `to` when a range appears mid-sentence (`3 to 5 screenshots`).

### Other punctuation

- Oxford comma: always use it.
- Parentheses: use sparingly. If the parenthetical matters, make it a sentence.
- Semicolons: avoid in step prose. Use two sentences instead.


## 14. Anti-patterns

### AI-polish anti-patterns

Do not:

- Start routine procedural articles with “By the end of this article…”
- Describe the full UI when a screenshot already shows it.
- Repeat the same explanation in the intro, steps, and troubleshooting.
- Include generic benefit statements unless they help the user make a decision.
- Quote error messages unless verified in the product.
- List every possible tenant configuration in the main flow.
- Add a “What this article doesn’t cover” section unless the boundary prevents real confusion.
- Use long, symmetrical examples that restate the obvious.

Bad:

> If you are set up to log in with a password, you will be directed to enter a password, and if you are set up to log in with SSO, you will be directed to log in using SSO.

Better:

> SpecterX shows the login method configured for your account.

### Over-documentation anti-patterns

Do not explain obvious UI mechanics unless they matter.

Bad:

> Click the email field and type your email address.

Better:

> Enter your email address in the **Email** field.

Do not say a button is greyed out unless the disabled state helps the user.

Good:

> **Sign In** is available only after you enter both your email address and password.

Avoid:

> The Sign In button is greyed out until both fields contain text.

Unless users commonly ask why the button is disabled.

### Marketing anti-patterns

Avoid turning product documentation into product positioning.

Bad:

> SpecterX helps your organization securely collaborate across ecosystems with a seamless protected file experience.

Better:

> Use SpecterX to upload, share, and manage protected files.

Even that may be unnecessary in a procedural article.

---

## 15. Article archetypes

### Procedural how-to

Use for task-based articles.

Examples:

- Log in to SpecterX
- Set or reset your password
- Upload a file
- Share a file
- Revoke access to a file

Skeleton:

```md
# Task title

Short intro.

## Before you start

Prerequisites.

## Steps

1. Action.
2. Action.
3. Confirm result.

## Troubleshooting

Common issues.

## Related articles

Relevant links.
```

### Overview / concept

Use when explaining what something is.

Examples:

- What is SpecterX?
- What are policies?
- What is a workspace?

Skeleton:

```md
# Concept title

Short definition.

## How it works

Plain explanation.

## When to use it

Common use cases.

## Related articles

Relevant task articles.
```

No numbered steps unless the article includes a small task.

### Troubleshooting article

Use when the article starts from a problem.

Examples:

- Troubleshoot sign-in issues
- Troubleshoot file upload failures
- Troubleshoot missing preview access

Skeleton:

```md
# Troubleshoot <problem>

Short intro.

## Symptoms

What the user may see.

## Common causes and fixes

### Symptom or error

Likely cause. Fix.

## If the issue continues

What information to collect or who to contact.
```

### Reference article

Use for capability matrices, permissions, supported file types, browser support, or limits.

Skeleton:

```md
# Reference title

Short intro.

## Table or list

Reference content.

## Notes

Important clarifications.

## Related articles

Relevant task articles.
```

### Integration setup

Use for admin or multi-step integration configuration.

Examples:

- Configure Google Drive integration
- Configure SharePoint integration
- Configure SSO

Skeleton:

```md
# Configure <integration>

Short intro with scope.

## Before you start

Required permissions, accounts, tenant settings, and prerequisites.

## Step 1: Prepare <system>

Actions in the external system.

## Step 2: Configure SpecterX

Actions in SpecterX.

## Step 3: Test the integration

How to confirm success.

## Troubleshooting

Common setup failures.

## Related articles

Relevant admin and end-user docs.
```

Integration setup articles may be longer and may need more screenshots.

---

## 16. Before / after examples

### Intro

Avoid:

> This article walks you through signing in to SpecterX from a web browser. By the end you'll have an active session and be on your SpecterX dashboard, ready to upload, share, and manage protected files.

Prefer:

> Use this article to sign in to SpecterX from a browser. Your administrator must create your account before you can sign in.

### Screen description

Avoid:

> The sign-in page shows a "Welcome to SpecterX" heading, a primary Sign in with Google button, an "or sign in with" divider, the email and password fields, the Sign In submit button, and a Reset password link at the bottom.

Prefer:

> The sign-in page shows the login options available for your organization.

### SSO variation

Avoid:

> Single sign-on (Entra ID, Okta, or other corporate IdP). If your organisation uses Microsoft Entra ID, Okta, or another enterprise identity provider, your tenant's sign-in page is configured to redirect you to your IdP — or to show an IdP-branded button in place of (or in addition to) the email and password form.

Prefer:

> If your organization uses SSO, enter your email address and follow the redirect to your identity provider.

Or, when the UI shows buttons:

> If your organization uses SSO, click the SSO option shown on the sign-in page and complete the login flow.

### Troubleshooting

Avoid:

> SSO says "access denied" or "not authorised". Your identity provider authenticated you, but SpecterX hasn't been told to let your account in. This usually means your administrator hasn't finished provisioning your account in SpecterX (even if your IdP account exists). Contact your administrator and ask them to confirm that your SpecterX account is active and that your email address matches what's in the identity provider.

Prefer:

> ### Access denied after SSO
>
> Your identity provider accepted your login, but your SpecterX account may not be active. Contact your administrator and ask them to confirm that your SpecterX user exists and matches your identity provider email address.

---

## 17. Review checklist

Before approving an article, check the following:

- The intro is short and task-focused.
- The article uses “you” consistently.
- The article uses present tense for product behavior.
- Each step has one primary action.
- UI labels match the product exactly.
- URLs and redirects are verified.
- Quoted error messages are verified.
- Screenshots are not described twice.
- Screenshot captions are short.
- Edge cases are not overloaded into the main flow.
- Troubleshooting is organized by symptom.
- Related articles are relevant and not used as filler.
- Generic benefit language has been removed.
- The article does not sound like marketing copy.
- The article does not sound like an AI-generated generic SaaS guide.

---

## 18. Things to decide after approved articles exist

The following should be revisited once the KB has enough approved articles:

- Whether to use contractions in all end-user articles or only some.
- Whether admin documentation should be more formal than end-user documentation.
- Whether screenshot captions should be visible or only used as alt text.
- Whether screenshots should be annotated, and in what style.
- Whether article titles should use imperative form or noun phrase form.
- Whether “Before you start” should appear before or after a short “About this task” section.
- Whether troubleshooting belongs in each article or in separate troubleshooting articles.
- Which terms from the product UI should be added to the glossary.

Until these are decided, prefer the simplest consistent option.

---

*This document is the starting style reference for the SpecterX KB. As approved articles accumulate, regenerate this guide from the approved corpus and PR review comments. Do not invent canon from one-off article choices.*
