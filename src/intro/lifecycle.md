# Lifecycle of a Property-Based Test

In the [previous chapter](./what-is-pbt.md) we wrote a property-based test for an
LRU cache. Let's run one for real, against a deliberately broken implementation,
and watch what Hegel does with it.

Here is a cache that claims to be an LRU cache but never evicts anything — it
just stores every entry in a dictionary — together with the property test from
before:

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```rust,ignore
{{#include ../../examples/rust/src/lib.rs:impl}}

{{#include ../../examples/rust/tests/lru.rs:test}}
```
{{#endtab }}
{{#tab name="Go" }}
```go
{{#include ../../examples/go/cache.go:impl}}

{{#include ../../examples/go/lru_test.go:test}}
```
{{#endtab }}
{{#tab name="C++" }}
```cpp
{{#include ../../examples/cpp/cache.hpp:impl}}

{{#include ../../examples/cpp/lru_test.cpp:test}}
```
{{#endtab }}
{{#tab name="TypeScript" }}
```typescript
{{#include ../../examples/typescript/src/cache.ts:impl}}

{{#include ../../examples/typescript/test/lru.test.ts:test}}
```
{{#endtab }}
{{#endtabs }}

Because the cache never evicts, its size grows without bound, so the property is
false: as soon as we insert more distinct keys than the capacity, the cache is
too big. When we run the test, Hegel finds a failing example and then *shrinks*
it down to the simplest one that still fails — a cache of capacity 0 with a
single entry:

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```text
{{#include ../../examples/expected-output/rust.txt}}
```
{{#endtab }}
{{#tab name="Go" }}
```text
{{#include ../../examples/expected-output/go.txt}}
```
{{#endtab }}
{{#tab name="C++" }}
```text
{{#include ../../examples/expected-output/cpp.txt}}
```
{{#endtab }}
{{#tab name="TypeScript" }}
```text
{{#include ../../examples/expected-output/typescript.txt}}
```
{{#endtab }}
{{#endtabs }}

However Hegel surfaces it, the reported example is the same in every language:
capacity 0, with a single entry whose key is the empty string. That minimal
example is no accident — it's the result of the shrinking process, and
understanding how Hegel gets there is what the rest of this chapter is about.

> These outputs are produced by really running the examples under `examples/`
> (see `examples/run.py`), not hand-written.
