# Glossary

*Populated as articles are approved.*

## Tenant URLs

Every SpecterX tenant has its own URL on the `specterx.com` domain. The
canonical form is `https://<tenant>.specterx.com` (for example,
`https://yourorg.specterx.com`).

There is **no shared default URL** that all users go to. In particular:

- `https://app.specterx.com` is **the URL for one specific tenant**
  (SpecterX's own production tenant), not a shared sign-in page.
- Do not write that "most users go to `app.specterx.com`" or describe
  it as the default. That framing is incorrect.
- When documenting a sign-in URL, instruct readers to use the URL their
  administrator gave them. Use `https://yourorg.specterx.com` as the
  example placeholder.

The KB pipeline often validates articles against `app.specterx.com`
because that is the tenant the test account lives in. That is a
testing artifact, not a documentation default.
