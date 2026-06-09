# Hegel book — working notes

## AI-written prose

All prose written by an AI (including you) **must** be marked with the
`ai-written` style so readers can tell a machine wrote it. Wrap the prose in a
`<div class="ai-written">`, leaving a blank line on each side of the content so
that mdbook still renders the Markdown inside it:

```html
<div class="ai-written">

This paragraph was written by an AI, and **Markdown still works** here.

</div>
```

This requirement applies to prose only — leave code blocks, headings, and the
multi-language `{{#tabs}}` examples outside the wrapper. The style is defined in
`theme/ai-prose.css` (renders the block in Comic Sans with a "Written by AI"
badge) and wired in via `additional-css` in `book.toml`.

## Never commit unreviewed AI-written text

You (an AI agent) must **never** create a git commit while the change still
contains AI-generated text that a human hasn't yet reviewed. Treat any remaining
`ai-written` block as unreviewed AI text: if the change you would be committing
still contains one, **do not commit it**. Finish the work and hand it back, so
the user can review it, rewrite it in their own voice (removing the `ai-written`
wrapper), and commit it themselves.

This restriction applies to **you, not the user**. The user is free to commit
`ai-written` content whenever they like; you are not. When you've finished a task
and the only thing left before a commit is unreviewed AI prose, stop and report
rather than committing.
