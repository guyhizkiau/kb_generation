# Cross-linking opportunities — back-links to article 04 from approved articles

Scanned: `articles/01-log-in-to-specterx/final.md`,
`articles/02-set-or-reset-password/final.md`,
`articles/03-what-is-specterx/final.md`.

## Article 01 (Sign in to SpecterX)

No mentions of sharing or recipients. No back-link opportunity.

## Article 02 (Set or reset your password)

Tangential mention only ("when someone shares data with you" — line 17). Not a candidate for hyperlink; the context is account creation, not the share flow.

## Article 03 (What is SpecterX?)

**Two back-link opportunities:**

1. **Line 22** — the bullet describes the exact task this article documents:

   > "- **Files shared from the web.** Upload or select a file in the SpecterX web platform, pick a policy, add recipients, and click Share. See [Sign in to SpecterX](../01-log-in-to-specterx/01-log-in-to-specterx.html) for how to reach the web platform."

   Convert "Files shared from the web" (the bullet's lead phrase, bolded) to a hyperlink targeting `../04-share-a-file/04-share-a-file.html`. The existing inline link to article 01 stays; we add the new one in the bullet's lead phrase.

2. **Related articles section** (lines 60–64). Currently lists articles 01 and 02. Add article 04 so a reader who lands on the overview can move directly to the share-a-file procedural article.

## Action plan

Apply both edits to `articles/03-what-is-specterx/final.md` after the new article's `final.md` is produced, then re-render its HTML and commit alongside the new article in the same PR under the `cross-link:` prefix as per WORKFLOW.md §7.2.
