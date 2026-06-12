
## 2026-06-12T14:26:55Z
After step 00-signin (click submit), the page URL remained https://app.specterx.com/signIn at the time 00-dashboard ran — the login redirect had not completed yet. Fix: insert a wait_for_url step between 00-signin and 00-dashboard that waits for the URL to no longer contain /signIn (or to contain /files or /dashboard), with a 30-second timeout. This will ensure the browser has actually navigated to the app before we look for the My Files element.
<!-- applied 2026-06-12 -->
