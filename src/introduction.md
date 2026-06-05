# Introduction

**Property-based testing with Hegel** is a book about [Hegel](https://hegel.dev), a
universal property-based testing protocol and family of libraries, built on
[Hypothesis](https://github.com/hypothesisworks/hypothesis).

Hegel is several things at once:

- A **protocol** for communication between a property-based testing server
  (written once) and a property-based testing library (written for each
  language).
- An **implementation** of that server, [hegel-core](https://github.com/hegeldev/hegel-core),
  built on Hypothesis.
- A **family of libraries** — [Rust](https://github.com/hegeldev/hegel-rust),
  [Go](https://github.com/hegeldev/hegel-go), [C++](https://github.com/hegeldev/hegel-cpp),
  and [TypeScript](https://github.com/hegeldev/hegel-typescript) — that act as
  thin, idiomatic frontends to that core.

The idea is to do the unreasonable amount of work required to build a
world-class property-based testing library *once*, rather than once per
language, and so make great property-based testing available everywhere.

## How this book is organised

- **[Getting started](./intro/getting-started.md)** orients first-time users and
  points you to next steps.
- **Explanation** covers [how Hegel works](./explanation/how-hegel-works.md) and
  [why Hegel exists](./explanation/why-hegel.md).
- **Reference** documents [installation](./reference/installation.md), the
  [protocol](./reference/protocol.md), and the available
  [libraries](./reference/libraries.md).
- **Project** describes the [community](./project/community.md) and Hegel's
  [compatibility and stability](./project/compatibility.md) guarantees.

> This book is currently a structural scaffold. Content will be filled in over
> time; for now, the canonical documentation lives at
> [hegel.dev](https://hegel.dev).
