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

## Runnable examples

Code samples that show Hegel's actual output (e.g. in the *Lifecycle* chapter)
are backed by real, runnable projects under [`examples/`](./examples), one per
language. The book includes their source and their captured output via mdBook's
`{{#include}}`, so what you read is what actually runs.

* Run them and regenerate the captured output: `just examples` (or
  `just examples rust` for a single language).

This needs the Rust, Go, C++ (CMake) and Node toolchains; each example
auto-downloads the `hegel-core` server via `uv` on first run. See
[`examples/README.md`](./examples/README.md) for details.
