# Stateful testing in Hegel

We'll continue with our running example of an LRU cache. In this chapter we'll show how to use *stateful testing* to completely specify the behaviour of the cache, and how this can help us develop it.

In classic property-based testing you have something that looks like a normal test, just with some parametrized sources of data. Stateful testing takes this up a notch by letting the property-based testing library assemble whole tests for you out of component parts.

The basic idea of stateful testing is that you have some sort of system under test (which might be e.g. a database, a data structure, the API for your site...) and you want to perform operations against it and assert that no matter what operations you perform, nothing breaks.

Hegel represents this with two basic components: *rules*, which are things you can do against the system under test, and *invariants*, which are things that should always be true.

Here is an example of how to use it with our running example of an LRUCache:

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```rust,ignore
{{#include ../../examples/rust/tests/stateful.rs:test}}
```
{{#endtab }}
{{#tab name="Go" }}
```go
{{#include ../../examples/go/stateful/stateful_test.go:test}}
```
{{#endtab }}
{{#tab name="C++" }}
```text
TODO: stateful testing is not yet available in hegel-cpp (v0.3.9). It is
planned for a future release.
```
{{#endtab }}
{{#tab name="TypeScript" }}
```text
TODO: stateful testing is not yet available in hegel-typescript. It is
planned for a future release.
```
{{#endtab }}
{{#endtabs }}

In this stateful test we are defining a model - essentially a bad implementation of the same API in this case - alongside our LRUCache, and asserting that the two always agree in their behaviour.

We define rules `put` and `get`. `put` puts keys into both the cache and the model, while `get` looks up a key in each and asserts that you get the same result (both present or both absent, and if both present then with the same value). The `same_size` invariant checks that they always have the same number of keys.

One thing worth noting is the `keys` object. This stores keys we've previously used for reuse in future rules. This is useful because it allows us to ensure that keys we check in `get` are ones we've previously used in `put` - if we just checked random keys there, `get` would typically be fairly trivial because we'd usually get cache misses in each.

## Running it

We can run our stateful test inside a normal Hegel test:

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```text
{{#include ../../examples/expected-output/rust-stateful.txt}}
```
{{#endtab }}
{{#tab name="Go" }}
```text
{{#include ../../examples/expected-output/go-stateful.txt}}
```
{{#endtab }}
{{#tab name="C++" }}
```text
TODO
```
{{#endtab }}
{{#tab name="TypeScript" }}
```text
TODO
```
{{#endtab }}
{{#endtabs }}

This is the same bug we found in the previous chapter — the cache never evicts, so after we've put two keys into a cache of size one, the model and the cache disagree.
Suppose we "fix" this bug by just stopping cache writes when the cache gets too big:

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```rust,ignore
{{#include ../../examples/rust/src/lib.rs:capped-put}}
```
{{#endtab }}
{{#tab name="Go" }}
```go
{{#include ../../examples/go/cache.go:capped-put}}
```
{{#endtab }}
{{#tab name="C++" }}
```text
TODO: stateful testing is not yet available in hegel-cpp (v0.3.9).
```
{{#endtab }}
{{#tab name="TypeScript" }}
```text
TODO: stateful testing is not yet available in hegel-typescript.
```
{{#endtab }}
{{#endtabs }}

The `same_size` invariant will no longer fail, but now the `get` rule does:

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```text
{{#include ../../examples/expected-output/rust-stateful-capped.txt}}
```
{{#endtab }}
{{#tab name="Go" }}
```text
{{#include ../../examples/expected-output/go-stateful-capped.txt}}
```
{{#endtab }}
{{#tab name="C++" }}
```text
TODO
```
{{#endtab }}
{{#tab name="TypeScript" }}
```text
TODO
```
{{#endtab }}
{{#endtabs }}

This is the flexibility of stateful testing. Unlike our previous property-based test, which captures a single property of the system, this test asserts that under any sequence of operations, the behaviour of the real implementation agrees with the model.

In some sense, any implementation that passes this test "has" to be correct, because the model fully specifies the range of allowed behaviours. The reality is a little weaker than that, because you're limited by what sequences of operations Hegel will generate (e.g. in normal operation this will not find any bugs that require thousands of operations to trigger), and of course this doesn't test any nonfunctional requirements like performance (you could pass it by replicating the same inefficient implementation that is in the model), but in practice we've found it's often quite effective at flushing out problems in implementations.
