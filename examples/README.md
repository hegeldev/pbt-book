# Runnable examples

Each subdirectory is a small, self-contained project that runs the LRU-cache
property test from the book against a **deliberately broken** cache — one that
stores every entry in a dictionary and never evicts, so it always exceeds its
capacity and the test always fails. The book's *Lifecycle* chapter shows both
the source and Hegel's failure output for each.

| Language   | Directory     | Implementation     | Test                      | Runner            |
| ---------- | ------------- | ------------------ | ------------------------- | ----------------- |
| Rust       | `rust/`       | `src/lib.rs`       | `tests/lru.rs`            | `cargo test`      |
| Go         | `go/`         | `cache.go`         | `lru_test.go`            | `go test ./...`   |
| C++        | `cpp/`        | `cache.hpp`        | `lru_test.cpp`           | CMake + ctest     |
| TypeScript | `typescript/` | `src/cache.ts`     | `test/lru.test.ts`       | `vitest run`      |

The regions shown in the book are delimited by `ANCHOR: impl` / `ANCHOR: test`
comments and pulled in with mdBook's `{{#include path:anchor}}`.

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
