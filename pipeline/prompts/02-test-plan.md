# Prompt: 02-test-plan

You convert `draft-1.md` into a machine-executable test plan.

## What you read

- `articles/<NN-slug>/draft-1.md`

**Do not read any existing `test-plan.json`.** If one already exists in
the article directory, ignore it completely and generate from scratch
using only `draft-1.md`.

## What you produce

A file at `articles/<NN-slug>/test-plan.json`. The tester reads this and
executes each step against the live system.

## Schema

```json
{
  "article_id": "NN-slug",
  "preconditions": [
    {
      "kind": "browser_login",
      "url": "https://app.specterx.com",
      "credential": "SPECTERX_USERNAME / SPECTERX_PASSWORD"
    },
    {
      "kind": "desktop_app_running",
      "app": "Outlook"
    }
  ],
  "steps": [
    {
      "id": "01",
      "description": "Click the Share button on the file row",
      "backend": "browser",
      "action": {
        "type": "click",
        "role": "button",
        "name": "Share"
      },
      "screenshot": {
        "after": true,
        "filename": "01-share-button.png",
        "focus": "the Share dialog that appeared"
      },
      "verify": "A dialog titled 'Share' is visible"
    },
    {
      "id": "02",
      "description": "Drag report.pdf from desktop to the upload area",
      "backend": "desktop",
      "action": {
        "type": "drag",
        "from": "C:\\Users\\Administrator\\Desktop\\report.pdf",
        "to_hint": "the upload drop area in the SpecterX web UI"
      },
      "screenshot": {
        "after": true,
        "filename": "02-uploaded.png",
        "focus": "the file showing in the uploads list"
      },
      "verify": "report.pdf appears in the file list"
    }
  ],
  "postconditions": [
    {
      "kind": "cleanup",
      "description": "Remove report.pdf from SpecterX to leave tenant clean"
    }
  ]
}
```

## Backend selection rules

Classify each step. If you're unsure, pick `desktop`.

`browser` when the step happens entirely inside the SpecterX web UI at
app.specterx.com.

`desktop` when the step involves:
- Outlook, Word, Excel, PowerPoint
- File Explorer, drag-drop from the OS
- Adobe Acrobat
- The SpecterX desktop client
- Right-click context menus from the desktop
- Any taskbar/system tray interaction

## Browser action types

Each browser step has an `action` object with a `type`. Use one of:

- `goto` — `url` (+ optional `wait_until`). Navigate to a URL.
- `click` — locator. Click an element.
- `fill` — locator + `value` or `value_env`. Type into an input
  (clears first). Use `value_env` to read a secret from an env var
  (e.g. `"value_env": "SPECTERX_PASSWORD"`); never inline secrets.
- `type` — locator + `value` + optional `"confirm": "Enter"`. Same as
  `fill`; with `confirm` it presses Enter afterward.
- `select` — locator + `value`. Choose from a dropdown (native
  `<select>` or a custom one).
- `file_upload` — locator + one of:
  - `filename` — a single file under `tester/fixtures/`.
  - `filenames` — a list of files under `tester/fixtures/` (multi-select).
  - `folder` — a subdirectory under `tester/fixtures/`; uploads every
    file inside it (whole-folder upload).
  Available fixtures: `test-document.pdf`, `test-document-2.pdf`,
  `test-document-3.pdf`, `test-report.txt`, `test-image.png`, and the
  folder `sample-folder/`.
- `clear` — locator. Clear an input field.
- `hover` — locator. Hover over an element.
- `navigate` — `url` OR a locator. Goto a URL, or click a close/back
  element when no URL is given.
- `press` — `key`, e.g. `"Enter"`. Press a keyboard key.
- `wait_for` — locator + optional `state` (default `"visible"`). Wait
  for an element to reach a state.
- `download` — locator + optional `save_as`. Click a download trigger
  and save the resulting file.

## Locators

Every action that targets an element (everything except `goto`,
`press`, and URL-based `navigate`) needs a locator. Provide exactly one,
in this order of preference:

1. `"role"` + `"name"` — most reliable:
   `{"role": "button", "name": "Share files"}`.
2. `"placeholder"` — for text inputs: `{"placeholder": "Enter your email"}`.
3. `"label"` — for labelled inputs: `{"label": "Recipient"}`.
4. `"selector"` — a CSS/XPath selector, as a last resort.
5. `"selector_hint"` — **only when none of the above apply**. It must be
   the exact element label in quotes, e.g. `"'Share files'"`. Never a
   prose description sentence.

## Login precondition

Every test plan that uses the `browser` backend **must** begin with
explicit login steps — do not rely on the `browser_login` precondition
alone, the runner does not execute preconditions. Always prepend these
four steps before any article-specific steps:

```json
{"id": "00-goto", "description": "Navigate to SpecterX", "backend": "browser",
 "action": {"type": "goto", "url": "https://app.specterx.com", "wait_until": "domcontentloaded"},
 "screenshot": {"after": false}, "verify": ""},
{"id": "00-email", "description": "Fill email", "backend": "browser",
 "action": {"type": "fill", "placeholder": "Enter your email", "value_env": "SPECTERX_USERNAME"},
 "screenshot": {"after": false}, "verify": ""},
{"id": "00-password", "description": "Fill password", "backend": "browser",
 "action": {"type": "fill", "placeholder": "Enter your password", "value_env": "SPECTERX_PASSWORD"},
 "screenshot": {"after": false}, "verify": ""},
{"id": "00-signin", "description": "Click Sign In", "backend": "browser",
 "action": {"type": "click", "selector": "button[type='submit']"},
 "screenshot": {"after": false}, "verify": ""},
{"id": "00-dashboard", "description": "Wait for My Files", "backend": "browser",
 "action": {"type": "wait_for", "name": "My Files", "state": "visible"},
 "screenshot": {"after": true, "filename": "00-dashboard.png", "focus": "My Files dashboard"},
 "verify": "My Files"}
```

## Locator rules

Every action that targets an element needs a locator. Use this priority order — stop at the first that applies:

1. **`"role"` + `"name"`** — always preferred:
   `{"role": "button", "name": "Share files"}`.
   When the article says a label is unconfirmed, **make your best guess
   and commit to it** — a wrong-but-specific name produces a useful
   timeout error; a vague prose hint silently always fails.
2. **`"placeholder"`** — for text inputs: `{"placeholder": "Enter your email"}`.
3. **`"label"`** — for labelled inputs: `{"label": "Recipient"}`.
4. **`"selector"`** — CSS/XPath as last resort.
5. **`"selector_hint"`** — only when none of the above apply. Must be the
   **exact quoted label**, e.g. `"'Share files'"`. Never a prose
   sentence. If you find yourself writing a sentence, use `role`+`name`
   with your best-guess label instead.

## SpecterX-specific locators (sourced from web-client codebase)

These are confirmed from `web-client/src/components/` — use them exactly, do not guess:

| UI element | Correct locator |
|-----------|----------------|
| Sign In form submit button | `"selector": "button[type='submit']"` |
| Share Files drawer file upload input | `"selector": "input[data-testid='uploadDrawer_dragdropArea']"` |

**File upload note**: The Share Files drawer uses Ant Design's `<Dragger>` with
`openFileDialogOnClick={false}`, so clicking the drag area does NOT open a file picker.
The hidden `input[type='file']` has `data-testid="uploadDrawer_dragdropArea"`. Always use
`"selector": "input[data-testid='uploadDrawer_dragdropArea']"` for file uploads in this drawer.
The visible text "Choose a file or drag it here" is in a `div`, not the `input` — do not
use `selector_hint` for file uploads.

**Before writing any test-plan step that interacts with a SpecterX UI element**, grep the
codebase first:
```bash
grep -rn 'data-testid\|aria-label\|placeholder' ~/specterx-codebase/web-client/src/ | grep -i '<relevant-keyword>'
```

## Rules

- One step per JSON entry; do not bundle.
- `verify` is a checkable condition the tester will assert. Be
  concrete: "A dialog titled 'Share' is visible", not "the share
  thing happens".
- Cleanup steps are mandatory if the article creates new state
  (uploaded files, sent emails, created users). Be a good tenant.

## When you're done

Save `test-plan.json`. Update STATE:

```
PHASE=TESTING
LAST_UPDATE=<ISO>
NEXT_ACTION=tester executes test-plan.json
```
