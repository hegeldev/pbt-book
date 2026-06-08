# What happens when you run a Hegel test

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

There are a couple of things worth observing about this test:

1. It does, correctly, fail, in a way that demonstrates the problem. Given that the thing it is testing is completely broken, this is a pretty low bar to clear, but it's worth noting explicitly.[^flaky]
2. When it fails it *prints the failing test case*. This is a big difference between property-based tests and typical example-based tests: Because the test involves generated data, you need to be able to show the actual concrete values that were chosen.
3. The printed test case is quite simple. In this case it's the simplest it could possibly be (according to some specific notion of "simplest"), but in general it will only be simplified.

[^flaky]: It's also not completely true! If you run these tests yourself, they will only fail *most* of the time. More on that in a second.

These come from the basic lifecycle of a property-based test:

1. We run the test function multiple times (in Hegel, 100 times by default), with different generated values.
2. If any of them fail, we pick a failing test case and *shrink* it - running the test function many more times, with simpler variations of our current simplest failing test case.
3. Finally, we print it.

## Shrinking in action

In order to see shrinking at work, we can use the `verbosity` setting to print every test case tried as we run:[^rust-only-verbosity]

[^rust-only-verbosity]: Or we can in languages that support this, which turns out to only be our rust implementation right now. Sorry, we're on it.

</div>

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```rust,ignore
#[hegel::test(verbosity = Verbosity::Verbose)]
fn test_respects_lru_capacity(tc: TestCase) {
    let capacity = tc.draw(gs::integers::<usize>().min_value(1));
    let mut cache = MyLRUCache::<String, i64>::new(capacity);

    let entries = tc.draw(gs::vecs(gs::tuples!(gs::text(), gs::integers::<i64>())));
    for (key, value) in entries {
        cache.put(key, value);
    }

    assert!(cache.size() <= capacity);
}
```
{{#endtab }}
{{#tab name="Go" }}
```text
TODO: the Go library (v0.5.3) does not yet expose a verbosity setting — its
`go test` integration always runs at "normal" verbosity.
```
{{#endtab }}
{{#tab name="C++" }}
```text
TODO: the C++ library (v0.3.9) prints only the final counterexample, not the
intermediate test cases, so it cannot yet show the full verbose lifecycle.
```
{{#endtab }}
{{#tab name="TypeScript" }}
```text
TODO: the TypeScript library prints only the final counterexample, not the
intermediate test cases, so it cannot yet show the full verbose lifecycle.
```
{{#endtab }}
{{#endtabs }}

This prints all intermediate test cases rather than just the final failing one.
Here's an excerpt of the most interesting bits:

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```text
{{#include ../../examples/expected-output/rust-verbose.txt}}
```
{{#endtab }}
{{#tab name="Go" }}
```text
TODO
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

You can see both the generation and the shrinking at play here. Initially, Hegel tries a variety of different test cases, with various different capacities and entries, until it finds one that fails (e.g. capacity = 1, with more than one entry). Then it switches to a shrink mode, where it tries deleting those entries, simplifying keys and values within them, etc.
Once it can no longer shrink any further it replays the final shrunk example one last time and lets the shrunk failure that we saw propagate to the test runner.

</div>

## Replaying a saved failure

We'll now see one other piece of the property-based testing lifecycle: Replay.
Once Hegel has found this failure, subsequent runs will start from there (until the bug is fixed).
So if we run the verbose test a second time without changing anything, we don't
see the long search and shrink from before:

</div>

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```text
{{#include ../../examples/expected-output/rust-verbose-replay.txt}}
```
{{#endtab }}
{{#tab name="Go" }}
```text
TODO
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

As well as significantly speeding up the test, this feature is an important part of making Hegel part of your development loop. Although a Hegel test may sometimes pass erroneously (because it failed to find the bug in its 100 test case budget), once it has found a bug, you may reliably use it as part of your development process because the test will keep failing until the bug is fixed.
