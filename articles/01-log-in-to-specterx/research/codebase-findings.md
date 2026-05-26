# Codebase findings — Log in to the SpecterX web platform

Bitbucket access not yet configured. Codebase recon pending SSH key setup.

The two repos called out in `WORKFLOW.md` section 3.1
(`bitbucket.org:specterx/web-client.git` and
`bitbucket.org:specterx/admin-web-client.git`) are not yet cloned on
this VM — deploy keys still need to be generated and registered. Until
that happens, any UI labels and error strings in the draft must come
from the live UI capture (see `research/ui-snapshot/ui-glossary.md`),
not from the codebase.

Next steps (out of scope for article 01):

1. Generate the two ed25519 keypairs per `WORKFLOW.md` section 3.1.
2. Ask Guy to register both public keys as read-only Bitbucket Access
   Keys.
3. Clone both repos to `~/specterx-codebase/`.
4. Re-run codebase recon for any subsequent article that touches a
   feature where UI strings or feature flags would inform the draft.
