---
vendor: virtru
slug: what-is
source_url: https://support.virtru.com/hc/en-us/articles/360039055854-How-Virtru-keeps-files-and-data-secure
title: How Virtru keeps files and data secure
captured: 2026-06-01
topics: [overview, security model, encryption, zero trust, TDF, access control, compliance]
---

# Coverage notes (paraphrased)

Virtru does not maintain a single canonical "What is Virtru?" article in its support center; the closest thing is this security-overview piece, which doubles as a concept primer. The article explains the product through its security model rather than through user tasks, which is unusual compared to Egnyte/DocSend/HubSpot.

Sections (in rough order): the zero-trust architecture premise; how AES-256 encryption is applied to data in transit and at rest; the split-knowledge key approach; persistent file protection (PFP) and what a portable secure link buys you; integration with existing identity (no new passwords or installs); compliance regimes addressed (CMMC, ITAR, CJIS).

Concepts introduced for a brand-new reader: zero-trust, AES-256, Trusted Data Format (TDF) as a "wrapper" around content, Persistent File Protection (PFP), access revocation after send, expiration dates, watermarking, open-access analytics ("did the recipient open it"). These are introduced in passing, with links to deeper articles per concept (notably a dedicated "What is TDF?" page).

Problem framing: organizations need to share email and files externally without losing control of the content once it leaves the perimeter; existing email/file tools do not enforce this. The article does not explicitly state what Virtru is NOT, but it implicitly contrasts itself with "other encryption providers" that demand new passwords or software.

Reader framing: a mix of admin and security-conscious end user; assumes some familiarity with encryption terminology. Tone is technical, confident, slightly marketing-adjacent. Estimated 500-800 words. Screenshots are sparse to absent (maybe 0-1); the article leans on diagrams and prose.
