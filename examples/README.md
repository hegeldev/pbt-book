# Runnable examples

Each subdirectory is a small, self-contained project that runs the LRU-cache
property test from the book against a **deliberately broken** cache — one that
stores every entry in a dictionary and never evicts, so it exceeds its capacity.
The book's *Lifecycle* chapter shows both the source and Hegel's failure output
for each.

There are two iterations of the test per language, matching the chapter:

| Language   | Directory     | Implementation | Iteration 1 (`capacity >= 0`) | Iteration 2 (`capacity >= 1`)   |
| ---------- | ------------- | -------------- | ----------------------------- | ------------------------------- |
| Rust       | `rust/`       | `src/lib.rs`   | `tests/lru.rs`                | `tests/lru_nonzero.rs`          |
| Go         | `go/`         | `cache.go`     | `lru_test.go`                 | `nonzero/lru_nonzero_test.go`   |
| C++        | `cpp/`        | `cache.hpp`    | `lru_test.cpp`                | `lru_nonzero_test.cpp`          |
| TypeScript | `typescript/` | `src/cache.ts` | `test/lru.test.ts`            | `test/lru_nonzero.test.ts`      |

Each iteration 2 keeps the same test name as iteration 1; they're kept separate
(a distinct test crate / Go package / gtest executable / vitest file) so each can
be run on its own.

The regions shown in the book are delimited by `ANCHOR: impl` / `ANCHOR: test`
comments and pulled in with mdBook's `{{#include path:anchor}}`.

> **Flakiness is expected.** Iteration 2 (`capacity >= 1`) is only *almost*
> always falsifiable by a random search — you need more distinct keys than the
> capacity, and most randomly drawn capacities are large — so an individual run
> may not find the bug. That's a real property-based-testing phenomenon the book
> discusses; `run.py` simply retries until it gets a failure to capture.

## Regenerating output

```
just examples          # all languages
just examples rust     # just one
```

`run.py` runs each project, writes the full combined output to
`expected-output/<lang>.raw.txt` (gitignored, provenance only), and a trimmed,
path/timing-normalised slice to `expected-output/<lang>.txt`, which the book
includes. The trimming removes only volatile noise (absolute paths, elapsed
times, thread ids) and surrounding framing.

## Prerequisites

The Rust, Go, C++ (CMake ≥ 3.14, a C++20 compiler) and Node (16+) toolchains.
Each Hegel library auto-downloads the `hegel-core` server via `uv` on first run
(see <https://hegel.dev/reference/installation>). These are developer-preview
libraries, so exact output wording may drift between versions — re-run
`just examples` to refresh.
