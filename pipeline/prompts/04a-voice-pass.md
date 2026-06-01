# Prompt: 04a-voice-pass

You are doing a **voice and tone pass** over an article that has already
been written, tested, and revised. The substance is locked. Your job is
to rewrite the prose so it reads like a competent human support writer
produced it, not like AI output.

## What you read

- `articles/<NN-slug>/final.md` — the current article you will edit.
- `editorial/STYLE_GUIDE.md` — the canon you enforce. Pay particular
  attention to Sections 2.4 (Contractions), 3 (Article openings),
  10 (Troubleshooting — including the "Header rule" sub-section),
  13 (Words and phrases to avoid), 13a (Punctuation), and 14
  (Anti-patterns).

## What you produce

A rewritten `articles/<NN-slug>/final.md`, plus a one-paragraph
self-report appended at the very end of your run (printed to stdout,
NOT written into the article), listing the categories of fix you
applied.

## Hard rules — what you may and may not change

You may change:

- Prose wording, sentence structure, contractions, parenthetical
  asides, and section opening sentences.
- Troubleshooting headers (the phrasing of the heading text), so they
  state the symptom from the user's perspective.

You may NOT change:

- Any factual claim about how the product behaves.
- Any UI label that appears in bold (e.g. **Reset password**).
- Any screenshot path, file name, or alt text.
- The article's section structure (heading hierarchy, order of
  sections, presence/absence of *Before you start*, *Steps*,
  *Troubleshooting*, etc.).
- The numbered procedure in *Steps* — same steps, same order, same
  count. You may rephrase a step's sentence; you may not split, merge,
  add, or remove steps.
- The article's YAML front matter (title, audience, reading time, etc.),
  except that a `last-validated:` or similar QA-metadata field should
  be removed.

If you find yourself wanting to change a fact, stop and emit a
`> ⚠ Voice pass blocked: <one-sentence reason>` line in the article at
the offending location, then leave that part of the prose alone.

## The checklist

Walk the article from top to bottom and apply each of the following
checks. For every change you make, you do not need to leave a comment —
just make the change. The diff is the audit trail.

### 1. Opener

The article's opening paragraph must not start with "Use this article
to…" unless that pattern fits this specific article AND it is not used
by adjacent articles in the KB. Prefer a situational or direct-action
opener (see Style Guide Section 3). Rewrite the opener once if needed.
Keep the same task scope and prerequisites — only the framing changes.

### 2. Meta-commentary

Remove sentences that narrate the article's own structure. Common
offenders:

- "The procedure is the same in both cases…"
- "This article will cover X, then Y, then Z."
- "First we will… then we will…"
- "By the end of this article, you'll…"

If a sentence summarizes the steps that appear below it, delete or
recast it.

### 3. Summary-before-procedure

If the intro lists the procedure in prose and the *Steps* section
lists the same procedure, drop the prose list. Keep one.

### 4. Contractions

Default to contracted forms in end-user articles (don't, can't, isn't,
you'll, you've, we'll, doesn't). Sweep the article for the
uncontracted forms and contract them, EXCEPT in:

- Legal text
- Security warnings
- Formal admin documentation
- Error-message explanations where precision matters

### 5. Parenthetical asides

Long parentheticals (more than a short phrase) read as AI-generated
clarifications. Convert them to follow-up sentences or delete them if
they're not actually helpful. Same for asides set off with em dashes
(which are already banned by Section 13a).

### 6. Troubleshooting headers

For every `### …` header inside the **Troubleshooting** section, check
whether the header states a symptom (what the user sees) or a cause /
fix (an internal diagnosis or action). Headers must state the
symptom. Rewrite cause-phrased or fix-phrased headers. The body of the
item already explains the cause and the fix — that's where they belong.

Examples of the rewrite:

- "Your administrator has disabled self-service reset" →
  "The Reset password link is missing or doesn't respond"
- "Allow cookies for SpecterX" →
  "The sign-in page keeps reloading"
- "You never received the activation email after your account was
  created" →
  "You expected an activation email but it never arrived"

### 7. Internal QA / validation metadata

Remove anything that looks like pipeline metadata leaking into customer
copy:

- "Last validated end-to-end against the live production tenant on
  YYYY-MM-DD" footers.
- Test-recipient email addresses (anything matching `*@specterx.com`
  used as a test account, the `davidch@…` or similar known test
  inboxes).
- Capture-run identifiers like `v13`, `v14`, `e2e-v7`.
- Tenant IDs used for testing.
- `last-validated:` or `specterx-build:` fields in the YAML front
  matter (and any equivalent — strip the QA-provenance fields).

If a stripped item leaves an obviously empty paragraph, delete the
paragraph.

### 8. Words and phrases to avoid

Apply Section 13 of the style guide: rewrite "simply", "easily",
"seamlessly", "utilize", "in order to", "ensure that",
"allows you to" (when "you can" works), and the rest of that list.

### 9. Em dashes

Section 13a bans em dashes (—) in prose. Replace any em dash with
either two sentences or a comma / colon, depending on what the
sentence actually means.

### 10. Hyphens at the start of lines

Some article drafts emit lines that begin with a stray hyphen-space.
Normalize them.

## Voice check at the end

Before you stop, read the rewritten article cold, top to bottom. If the
opening paragraph still triggers the "this was AI-generated" reaction —
because it tells the reader what the article is about instead of
helping them with their problem — rewrite the opener one more time.

## When you're done

1. Save the updated `articles/<NN-slug>/final.md`.
2. Update the article's `STATE` file:
   ```
   PHASE=PR_OPEN
   LAST_UPDATE=<ISO timestamp>
   NEXT_ACTION=push the voice-pass commit and request review
   ```
   (If the article was already in PR_OPEN before this run, keep it
   there.)
3. Print a one-paragraph self-report to stdout summarizing which
   categories from the checklist above you applied changes for, and
   any items where you found nothing to change. Do NOT write the
   self-report into the article — it's pipeline output, not customer
   copy.
4. Exit.
