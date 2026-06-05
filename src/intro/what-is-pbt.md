# What is property-based testing?

Property-based testing is just a generalisation of the sort of testing you're already useful.[^verification]

[^verification]: This is not how it's usually presented though. Property-based testing is often sold as "lightweight formal verification" and as if it was a very different thing from normal testing and there were these profound mathematical properties of your software that you pluck out of the platonic realm and place within your test suite. I think this is an extremely unhelpful way to look at it.

You can think of a test as consisting of two parts:

1. A scenario
2. A set of checks

The scenario is "I did a thing", and the checks are "here is what should have happened when I did that thing".

Each of these can vary in how specific they are.

1. Here is the exact thing I did, and here is the exact thing that should have happened.
2. Here is the exact thing I did, and here are some things that should be true about the result.
3. I did something like this, and this is the exact thing that should have happened.
4. I did something like this, and here are some things that should be true about the result.

Concretely:

1. Here is a series of interactions with my web-application, and here's what the screenshot of the final result should look like.
2. Here is a series of interactions with my web-application, and every fetch should have returned a 200 or a redirect.
3. I inserted three unique keys into my dictionary, and the result should be that the dictionary should have this exact structure.
4. I inserted three unique keys into my dictionary, and the dictionary should now have size 3.

These four categories roughly correspond to:

1. Snapshot testing (AKA golden master testing AKA expect testing)
2. Example-based testing (what you probably think of as "normal software testing")
3. Differential testing (comparing two implementations of the same API and asserting that they get the same result)[^differential]
4. Property-based testing (what this book is about)

[^differential]: Arguably differential testing is a type of property-based testing, and certainly you can and sometimes should use a property-based testing library to do differential testing, but it's a bit of a special category.

None of these are truly distinct categories, and all of them are great in some contexts. This is important to remember: When learning about property-based testing, it's easy to get excited and think all of your tests should be property-based tests. Resist that urge. Property-based tests are part of a complete ~breakfast~ test suite, not the whole of it.

## An example

Suppose we have an LRU cache, and we want to check that it never exceeds its
configured capacity. We might write the following example-based test:

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```rust,ignore
#[test]
fn test_respects_lru_capacity() {
	let mut cache = MyLRUCache::<String, i64>::new(2);

	cache.put("a".to_string(), 1);
	cache.put("b".to_string(), 2);
	cache.put("c".to_string(), 3);

	assert!(cache.size() <= 2);
}
```
{{#endtab }}
{{#tab name="Go" }}
```go
import "testing"

func TestRespectsLRUCapacity(t *testing.T) {
	cache := NewMyLRUCache[string, int](2)

	cache.Put("a", 1)
	cache.Put("b", 2)
	cache.Put("c", 3)

	if cache.Size() > 2 {
		t.Fatalf("cache size exceeds capacity")
	}
}
```
{{#endtab }}
{{#tab name="C++" }}
```cpp
#include <gtest/gtest.h>
#include <string>

TEST(MyLRUCache, RespectsCapacity) {
	MyLRUCache<std::string, int> cache(2);

	cache.put("a", 1);
	cache.put("b", 2);
	cache.put("c", 3);

	EXPECT_LE(cache.size(), 2);
}
```
{{#endtab }}
{{#tab name="TypeScript" }}
```typescript
import { test, expect } from "vitest";

test("MyLRUCache respects capacity", () => {
	const cache = new MyLRUCache<string, number>(2);

	cache.put("a", 1);
	cache.put("b", 2);
	cache.put("c", 3);

	expect(cache.size()).toBeLessThanOrEqual(2);
});
```
{{#endtab }}
{{#endtabs }}

This is a perfectly reasonable test, but notice the difference between what
it promises and what it actually does. The claim of the test is that the cache
*never* exceeds its capacity, but the test actually only shows that after one
very specific sequence of operations the cache has not exceeded its capacity.

In contrast, we might write the following property-based test:

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```rust,ignore
use hegel::generators as gs;
use hegel::TestCase;

#[hegel::test]
fn test_respects_lru_capacity(tc: TestCase) {
	let capacity = tc.draw(gs::integers::<usize>().min_value(0));
	let mut cache = MyLRUCache::<String, i64>::new(capacity);

	let entries = tc.draw(
	    gs::vecs(gs::tuples!(gs::text(), gs::integers::<i64>()))
	);
	for (key, value) in entries {
		cache.put(key, value);
	}

	assert!(cache.size() <= capacity);
}
```
{{#endtab }}
{{#tab name="Go" }}
```go
import (
  "math"
  "testing"
  "hegel.dev/go/hegel"
)

func TestRespectsLRUCapacity(t *testing.T) {
	t.Run("MyLRUCache respects capacity", hegel.Case(func(ht *hegel.T) {
		capacity := hegel.Draw(ht, hegel.Integers(0, math.MaxInt))
		cache := NewMyLRUCache[string, int](capacity)

		keys := hegel.Draw(ht, hegel.Lists(hegel.Text(0, math.MaxInt)))
		for _, key := range keys {
			value := hegel.Draw(ht, hegel.Integers(math.MinInt, math.MaxInt))
			cache.Put(key, value)
		}

		if cache.Size() > capacity {
			ht.Fatalf("cache size exceeds capacity")
		}
	}))
}
```
{{#endtab }}
{{#tab name="C++" }}
```cpp
#include <gtest/gtest.h>
#include <hegel/hegel.h>
#include <stdexcept>
namespace gs = hegel::generators;

TEST(MyLRUCache, RespectsCapacity) {
	hegel::test([](hegel::TestCase& tc) {
		auto capacity = tc.draw(gs::integers<size_t>({.min_value = 0}));
		MyLRUCache<std::string, int> cache(capacity);

		auto entries = tc.draw(
		  gs::vectors(gs::tuples(gs::text(), gs::integers<int>()))
		);
		for (const auto& [key, value] : entries) {
			cache.put(key, value);
		}

		// Hegel detects failures via thrown exceptions, so the property
		// throws rather than using a (non-throwing) gtest assertion.
		if (cache.size() > capacity) {
			throw std::runtime_error("cache size exceeds capacity");
		}
	});
}
```
{{#endtab }}
{{#tab name="TypeScript" }}
```typescript
import { test, expect } from "vitest";
import * as hegel from "@hegeldev/hegel";
import * as gs from "@hegeldev/hegel/generators";

test(
	"MyLRUCache respects capacity",
	hegel.test((tc) => {
		const capacity = tc.draw(gs.integers({ minValue: 0 }));
		const cache = new MyLRUCache<string, number>(capacity);

		const entries = tc.draw(
		    gs.arrays(gs.tuples(gs.text(), gs.integers())),
		);
		for (const [key, value] of entries) {
		    cache.put(key, value);
		}

		expect(cache.size()).toBeLessThanOrEqual(capacity);
	}),
);
```
{{#endtab }}
{{#endtabs }}

This test generates a fully general series of put operations against the cache, and asserts that the capacity is still respected at the end.

Now, this still doesn't actually guarantee that the cache never exceeds its capacity. For starters (more on this problem later), this is only performing put operations. More importantly though, although the space this test applies to is *logically* infinite, in practice this test will run some number of test cases, mostly small, and will pass if each of those test cases pass. To learn more, read [Lifecycle of a Property-Based Test](./lifecycle.md)
