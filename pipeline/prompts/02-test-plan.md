# Prompt: 02-test-plan

You convert `draft-1.md` into a machine-executable test plan.

## What you read

- `articles/<NN-slug>/draft-1.md`

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
        "selector_hint": "Share button in file row for example.pdf"
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

## Rules

- One step per JSON entry; do not bundle.
- `selector_hint` is a natural-language description, not a CSS
  selector. The browser backend uses Playwright accessibility tree +
  the hint to find the element. Be descriptive: "the blue Share button
  in the top-right of the file detail panel", not just "Share".
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
