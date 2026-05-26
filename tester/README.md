# tester/

Executes a `test-plan.json` against the live SpecterX system. Two
backends:

- **Browser** (`browser_runner.py`): Playwright over CDP. Connects to a
  Chromium with `--remote-debugging-port=9222`.
- **Desktop** (`desktop_runner.py`): Anthropic API with the
  `computer_20250124` tool, talking to a small Windows-side action
  server.

`step_classifier.py` picks the backend for each step (keyword-based).
`runner.py` ties them together and writes `test-notes.md`.

`sensitive-terms.txt` — names/phrases to avoid in committed screenshots
(PII checklist; populate as needed).

## CDP connection

Per the architecture doc, the browser backend was designed to connect
to a Chromium running on the Windows host of an EC2 Windows VM, from a
WSL2 Ubuntu environment. In environments where there is no Windows
host (e.g. a plain Linux EC2), `browser_runner.py` will fall back to
launching its own headed/headless Chromium locally. See
`browser_runner.py` for the selection logic.
