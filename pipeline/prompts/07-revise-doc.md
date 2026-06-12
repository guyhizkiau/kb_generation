# Revise a knowledge doc from Ghostwriter annotations

You are revising a single background knowledge document from inline reviewer annotations.

## Target document

Edit **only** the file named in the run header. Do not modify any other files.

## Instructions

1. Read the current document content and the annotation list provided in the run header.
2. Apply each annotation comment to the relevant passage in the document.
3. Preserve all headings, section order, and content not referenced by an annotation.
4. Do not add research, testing, or article pipeline artifacts.
5. When finished, save the updated markdown to the same file path.
6. Commit with message `docs(<area>): revise <doc-id> from feedback` where `<area>` and `<doc-id>` match the run header.

## Do not

- Touch `articles/` directories or any `STATE` file.
- Rewrite unrelated sections for style unless an annotation asks for it.
- Delete annotations — the operator dismisses them in the UI after review.
