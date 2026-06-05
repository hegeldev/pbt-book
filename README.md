# Property-based testing with Hegel

Source for the [_Property-based testing with Hegel_](https://hegel.dev) book, an
[mdBook](https://rust-lang.github.io/mdBook/) about [Hegel](https://github.com/hegeldev).

## Developing

This project uses [`just`](https://github.com/casey/just),
[`mdbook`](https://rust-lang.github.io/mdBook/), and the
[`mdbook-tabs`](https://crates.io/crates/mdbook-tabs) preprocessor for the
multi-language code switcher.

* Install the preprocessors: `just setup`
* Serve locally with live reload: `just serve`
* Build into `./book`: `just build`
* List all tasks: `just`

The tab styling lives in `theme/tabs.css` and `theme/tabs.js`; these are
committed and wired up in `book.toml`.
