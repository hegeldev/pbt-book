# Lifecycle of a Property-Based Test

In the [previous chapter](./what-is-pbt.md) we wrote a property-based test for an
LRU cache. In this chapter we'll go through it in more detail, and what happens
when we run it.

In order to do this, let's run it against a real, buggy, implementation of MyLRUCache.
We'll start with one that simply never evicts:

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```rust,ignore
{{#include ../../examples/rust/src/lib.rs:impl}}
```
{{#endtab }}
{{#tab name="Go" }}
```go
{{#include ../../examples/go/cache.go:impl}}
```
{{#endtab }}
{{#tab name="C++" }}
```cpp
{{#include ../../examples/cpp/cache.hpp:impl}}
```
{{#endtab }}
{{#tab name="TypeScript" }}
```typescript
{{#include ../../examples/typescript/src/cache.ts:impl}}
```
{{#endtab }}
{{#endtabs }}

And here is the property-based test from the previous chapter, which we'll run
against it:

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```rust,ignore
{{#include ../../examples/rust/tests/lru.rs:test}}
```
{{#endtab }}
{{#tab name="Go" }}
```go
{{#include ../../examples/go/lru_test.go:test}}
```
{{#endtab }}
{{#tab name="C++" }}
```cpp
{{#include ../../examples/cpp/lru_test.cpp:test}}
```
{{#endtab }}
{{#tab name="TypeScript" }}
```typescript
{{#include ../../examples/typescript/test/lru.test.ts:test}}
```
{{#endtab }}
{{#endtabs }}

Because the cache never evicts, its size grows without bound, so the property is
false: as soon as we insert more distinct keys than the capacity, the cache is
too big. As a result, the test fails:

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

The reported failure is very straightforward: We set the capacity to zero,
then we insert a single key (an empty string, with inserted value 0),
and then check that the cache has at most zero elements in it, which it does
not so the test fails.

We might reasonably think that this is a bug with the capacity zero case,
and maybe we're not interested in capacity zero caches, so we could modify
the test as follows:

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```rust,ignore
{{#include ../../examples/rust/tests/lru_nonzero.rs:test}}
```
{{#endtab }}
{{#tab name="Go" }}
```go
{{#include ../../examples/go/nonzero/lru_nonzero_test.go:test}}
```
{{#endtab }}
{{#tab name="C++" }}
```cpp
{{#include ../../examples/cpp/lru_nonzero_test.cpp:test}}
```
{{#endtab }}
{{#tab name="TypeScript" }}
```typescript
{{#include ../../examples/typescript/test/lru_nonzero.test.ts:test}}
```
{{#endtab }}
{{#endtabs }}

All we've changed is that the capacity is now at least one. This doesn't help,
though: the cache still never evicts, so the property is still false, and Hegel
just finds the next-smallest failure instead:

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```text
{{#include ../../examples/expected-output/rust-nonzero.txt}}
```
{{#endtab }}
{{#tab name="Go" }}
```text
{{#include ../../examples/expected-output/go-nonzero.txt}}
```
{{#endtab }}
{{#tab name="C++" }}
```text
{{#include ../../examples/expected-output/cpp-nonzero.txt}}
```
{{#endtab }}
{{#tab name="TypeScript" }}
```text
{{#include ../../examples/expected-output/typescript-nonzero.txt}}
```
{{#endtab }}
{{#endtabs }}

This time the capacity is one, and we insert two distinct keys — the empty
string and the string `"0"` — giving a cache of size two, which is larger than
one. The bug was never really about capacity zero at all.
