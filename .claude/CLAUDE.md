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
