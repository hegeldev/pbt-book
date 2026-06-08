# Data generation cookbook

<div class="ai-written">

This chapter is a grab-bag of recipes for generating the shapes of data that
come up again and again when you write property-based tests: numbers inside a
range, strings that look like identifiers, collections that are never empty,
records whose fields depend on one another, and so on. Each recipe states the
goal in one line and then shows the same generator in Rust, Go, C++, and
TypeScript.

The recipes assume you are inside a test body and already have a handle on the
current test case — `tc` in Rust, C++, and TypeScript, and `ht` in Go — so the
snippets show only the `draw` itself. They also assume the conventional imports:

- **Rust:** `use hegel::generators as gs;` (and `use hegel::generators::Generator;` for the `.map`/`.filter` combinators).
- **Go:** `import "hegel.dev/go/hegel"` (plus `math` wherever a full-range bound is needed).
- **C++:** `namespace gs = hegel::generators;`
- **TypeScript:** `import * as gs from "@hegeldev/hegel/generators";`

</div>

## Numbers in a range

<div class="ai-written">

The most common constraint of all: an integer or float that has to stay between
two bounds. Reach for the bounds on the generator itself rather than generating
a wider value and throwing some away — a bounded generator always produces a
usable value, and it shrinks toward the *low end of the range* rather than
toward zero.

</div>

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```rust,ignore
// A dice roll: 1 to 6, inclusive.
let roll = tc.draw(gs::integers::<u32>().min_value(1).max_value(6));

// A probability in the closed unit interval.
let p = tc.draw(gs::floats::<f64>().min_value(0.0).max_value(1.0));
```
{{#endtab }}
{{#tab name="Go" }}
```go
// A dice roll: 1 to 6, inclusive. Go infers the type from the bounds.
roll := hegel.Draw(ht, hegel.Integers(1, 6))

// A probability in the closed unit interval.
p := hegel.Draw(ht, hegel.Floats[float64]().Min(0).Max(1))
```
{{#endtab }}
{{#tab name="C++" }}
```cpp
// A dice roll: 1 to 6, inclusive.
auto roll = tc.draw(gs::integers<int>({.min_value = 1, .max_value = 6}));

// A probability in the closed unit interval.
auto p = tc.draw(gs::floats<double>({.min_value = 0.0, .max_value = 1.0}));
```
{{#endtab }}
{{#tab name="TypeScript" }}
```typescript
// A dice roll: 1 to 6, inclusive.
const roll = tc.draw(gs.integers({ minValue: 1, maxValue: 6 }));

// A probability in the closed unit interval.
const p = tc.draw(gs.floats({ minValue: 0, maxValue: 1 }));
```
{{#endtab }}
{{#endtabs }}

<div class="ai-written">

One subtlety worth knowing: an *unbounded* float generator produces `NaN` and
the infinities by default, because for a lot of code those are exactly the
values that expose bugs. The moment you give a float generator a bound, it stops
producing them — so the unit-interval generators above are already free of
`NaN` and infinity. If you need a finite float across the whole range, ask for
finiteness explicitly rather than narrowing the range.

</div>

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```rust,ignore
let finite = tc.draw(gs::floats::<f64>().allow_nan(false).allow_infinity(false));
```
{{#endtab }}
{{#tab name="Go" }}
```go
finite := hegel.Draw(ht, hegel.Floats[float64]().AllowNaN(false).AllowInfinity(false))
```
{{#endtab }}
{{#tab name="C++" }}
```cpp
auto finite = tc.draw(gs::floats<double>({.allow_nan = false, .allow_infinity = false}));
```
{{#endtab }}
{{#tab name="TypeScript" }}
```typescript
const finite = tc.draw(gs.floats({ allowNan: false, allowInfinity: false }));
```
{{#endtab }}
{{#endtabs }}

## Excluding a value

<div class="ai-written">

Sometimes the constraint isn't a range but a hole — "any integer except zero",
say, for the divisor in a division test. The quickest tool is a filter, which
drops any value the predicate rejects.

A word of caution: Hegel retries a filter only a few times before it gives up
and rejects the whole test case, and too many rejected test cases will fail your
test with a health-check error. A filter that throws away one value in a few
billion (like the zero below) is completely fine; a filter that rejects most of
what it sees is not. When the "good" values are rare, *construct* them directly
instead — for example by drawing the magnitude and the sign separately — rather
than filtering a broad generator.

</div>

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```rust,ignore
// A non-zero divisor. Zero is so rare that filtering it costs nothing.
let divisor = tc.draw(gs::integers::<i64>().filter(|n| *n != 0));
```
{{#endtab }}
{{#tab name="Go" }}
```go
// A non-zero divisor. Zero is so rare that filtering it costs nothing.
divisor := hegel.Draw(ht, hegel.Filter(
    hegel.Integers(math.MinInt64, math.MaxInt64),
    func(n int64) bool { return n != 0 },
))
```
{{#endtab }}
{{#tab name="C++" }}
```cpp
// A non-zero divisor. Zero is so rare that filtering it costs nothing.
auto divisor = tc.draw(gs::integers<int64_t>().filter([](int64_t n) { return n != 0; }));
```
{{#endtab }}
{{#tab name="TypeScript" }}
```typescript
// A non-zero divisor. Zero is so rare that filtering it costs nothing.
const divisor = tc.draw(gs.integers().filter((n) => n !== 0));
```
{{#endtab }}
{{#endtabs }}

## Strings with a specific shape

<div class="ai-written">

Plain text generators produce the full sprawl of Unicode, which is exactly what
you want when you're testing a parser or a serializer and *anything* should be
accepted. But often you need a string of a particular shape: only lowercase
letters, or something that looks like a product code, or a syntactically valid
email address.

For a restricted alphabet, hand the text generator the set of characters it's
allowed to use. For a precise structure, describe it with a regular expression
and let Hegel generate strings that match. And for the handful of well-known
formats that turn up everywhere, there are dedicated generators.

</div>

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```rust,ignore
// Lowercase identifiers of bounded length.
let word = tc.draw(gs::text().min_size(1).max_size(12));

// A product code like "ABC-042" via a regular expression.
let code = tc.draw(gs::from_regex(r"[A-Z]{3}-[0-9]{3}").fullmatch(true));

// Well-known formats.
let email = tc.draw(gs::emails());
let url = tc.draw(gs::urls());
```
{{#endtab }}
{{#tab name="Go" }}
```go
// Lowercase identifiers of bounded length.
word := hegel.Draw(ht, hegel.Text().Alphabet("abcdefghijklmnopqrstuvwxyz").MinSize(1).MaxSize(12))

// A product code like "ABC-042" via a regular expression.
code := hegel.Draw(ht, hegel.FromRegex(`[A-Z]{3}-[0-9]{3}`, true))

// Well-known formats.
email := hegel.Draw(ht, hegel.Emails())
url := hegel.Draw(ht, hegel.URLs())
```
{{#endtab }}
{{#tab name="C++" }}
```cpp
// Lowercase identifiers of bounded length.
auto word = tc.draw(gs::text({.min_size = 1, .max_size = 12,
                              .alphabet = "abcdefghijklmnopqrstuvwxyz"}));

// A product code like "ABC-042" via a regular expression.
auto code = tc.draw(gs::from_regex(R"([A-Z]{3}-[0-9]{3})", /*fullmatch=*/true));

// Well-known formats.
auto email = tc.draw(gs::emails());
auto url = tc.draw(gs::urls());
```
{{#endtab }}
{{#tab name="TypeScript" }}
```typescript
// Lowercase identifiers of bounded length.
const word = tc.draw(gs.text({ alphabet: "abcdefghijklmnopqrstuvwxyz", minSize: 1, maxSize: 12 }));

// A product code like "ABC-042" via a regular expression.
const code = tc.draw(gs.fromRegex("[A-Z]{3}-[0-9]{3}", { fullmatch: true }));

// Well-known formats.
const email = tc.draw(gs.emails());
const url = tc.draw(gs.urls());
```
{{#endtab }}
{{#endtabs }}

<div class="ai-written">

Note that the Rust snippet restricts length but not the alphabet — Rust's text
generator takes its character restrictions through the same builder; the Go,
C++, and TypeScript snippets show the `alphabet` option explicitly. Pick
whichever character controls your library exposes; the idea is the same.

</div>

## Choosing from a fixed set

<div class="ai-written">

When a value has to be one of a small, fixed collection of options — an enum
variant, an HTTP method, a suit in a deck of cards — sample from that collection
directly. This is the natural way to generate enums: list the cases and let
Hegel pick one.

</div>

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```rust,ignore
let suit = tc.draw(gs::sampled_from(vec!["hearts", "diamonds", "clubs", "spades"]));
let method = tc.draw(gs::sampled_from(vec!["GET", "POST", "PUT", "DELETE"]));
```
{{#endtab }}
{{#tab name="Go" }}
```go
suit := hegel.Draw(ht, hegel.SampledFrom([]string{"hearts", "diamonds", "clubs", "spades"}))
method := hegel.Draw(ht, hegel.SampledFrom([]string{"GET", "POST", "PUT", "DELETE"}))
```
{{#endtab }}
{{#tab name="C++" }}
```cpp
auto suit = tc.draw(gs::sampled_from({"hearts", "diamonds", "clubs", "spades"}));
auto method = tc.draw(gs::sampled_from({"GET", "POST", "PUT", "DELETE"}));
```
{{#endtab }}
{{#tab name="TypeScript" }}
```typescript
const suit = tc.draw(gs.sampledFrom(["hearts", "diamonds", "clubs", "spades"]));
const method = tc.draw(gs.sampledFrom(["GET", "POST", "PUT", "DELETE"]));
```
{{#endtab }}
{{#endtabs }}

<div class="ai-written">

If, instead of picking one of several *values*, you need to pick one of several
*generators* — say "either a small number or a large one" — use the
`one_of` family (`hegel::one_of!` in Rust, `hegel.OneOf` in Go, `gs::one_of`
in C++). At the time of writing the TypeScript library has no `oneOf`, so draw a
discriminator with `sampledFrom` and branch on it inside a `composite`
generator (see the records recipe below).

</div>

## Collections that are never empty

<div class="ai-written">

A list, set, or map generator will happily produce an empty collection — and it
*should*, because the empty case is where a surprising number of bugs hide. But
when your property only makes sense for a non-empty collection ("the maximum of
a non-empty list is one of its elements"), set a minimum size. You can cap the
maximum the same way when you want to keep test cases small.

</div>

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```rust,ignore
// At least one element, at most ten.
let xs = tc.draw(gs::vecs(gs::integers::<i32>()).min_size(1).max_size(10));
```
{{#endtab }}
{{#tab name="Go" }}
```go
// At least one element, at most ten.
xs := hegel.Draw(ht, hegel.Lists(hegel.Integers(math.MinInt32, math.MaxInt32)).MinSize(1).MaxSize(10))
```
{{#endtab }}
{{#tab name="C++" }}
```cpp
// At least one element, at most ten.
auto xs = tc.draw(gs::vectors(gs::integers<int>(), {.min_size = 1, .max_size = 10}));
```
{{#endtab }}
{{#tab name="TypeScript" }}
```typescript
// At least one element, at most ten.
const xs = tc.draw(gs.arrays(gs.integers(), { minSize: 1, maxSize: 10 }));
```
{{#endtab }}
{{#endtabs }}

<div class="ai-written">

Two related needs come up constantly. If you want the elements to be *distinct*
— no duplicates — the list/array/vector generators take a uniqueness flag in
Rust, C++, and TypeScript (`.unique()`, `{.unique = true}`, and
`{ unique: true }` respectively). And if you specifically need a large
collection, remember that the default size is small; draw the size yourself and
feed it in as the minimum, so the generator reliably produces something big
enough to stress a tree traversal or a rehash.

</div>

## Dictionaries with unique keys

<div class="ai-written">

A map generator pairs a key generator with a value generator and guarantees the
keys are distinct, which is exactly what you want for testing anything
key-value shaped. Bound the number of entries the same way you bound a list.

</div>

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```rust,ignore
let scores = tc.draw(gs::hashmaps(
    gs::text().min_size(1).max_size(16),
    gs::integers::<i32>().min_value(0).max_value(100),
).max_size(8));
```
{{#endtab }}
{{#tab name="Go" }}
```go
scores := hegel.Draw(ht, hegel.Maps(
    hegel.Text().MinSize(1).MaxSize(16),
    hegel.Integers(0, 100),
).MaxSize(8))
```
{{#endtab }}
{{#tab name="C++" }}
```cpp
auto scores = tc.draw(gs::maps(
    gs::text({.min_size = 1, .max_size = 16}),
    gs::integers<int>({.min_value = 0, .max_value = 100}),
    {.max_size = 8}));
```
{{#endtab }}
{{#tab name="TypeScript" }}
```typescript
const scores = tc.draw(gs.maps(
    gs.text({ minSize: 1, maxSize: 16 }),
    gs.integers({ minValue: 0, maxValue: 100 }),
    { maxSize: 8 },
));
```
{{#endtab }}
{{#endtabs }}

## Optional and nullable values

<div class="ai-written">

To generate "a value or nothing", wrap a generator in `optional`. This is the
right tool for a field that may be absent, a setting that defaults, or any
nullable column. Each language hands the absence back in its own idiomatic way,
which is worth keeping in mind when you consume the result.

</div>

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```rust,ignore
// Option<i32>: Some(n) or None.
let maybe_age = tc.draw(gs::optional(gs::integers::<i32>().min_value(0).max_value(120)));
```
{{#endtab }}
{{#tab name="Go" }}
```go
// *int: a pointer to the value, or nil when absent.
maybeAge := hegel.Draw(ht, hegel.Optional(hegel.Integers(0, 120)))
if maybeAge != nil {
    // use *maybeAge
}
```
{{#endtab }}
{{#tab name="C++" }}
```cpp
// std::optional<int>: has_value() or not.
auto maybe_age = tc.draw(gs::optional(gs::integers<int>({.min_value = 0, .max_value = 120})));
```
{{#endtab }}
{{#tab name="TypeScript" }}
```typescript
// number | null — note null, not undefined.
const maybeAge = tc.draw(gs.optional(gs.integers({ minValue: 0, maxValue: 120 })));
```
{{#endtab }}
{{#endtabs }}

## Records and structs

<div class="ai-written">

For your own structs, the cleanest approach is a *composite* generator: a small
function that draws each field and assembles the result. The big advantage over
wiring up tuples is that later fields can depend on earlier ones — here, only an
adult is allowed to hold a driving licence — and the whole thing becomes a named,
reusable generator you can pass to `optional`, to a list generator, or to
another composite.

</div>

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```rust,ignore
#[hegel::composite]
fn people(tc: hegel::TestCase) -> Person {
    let age = tc.draw(gs::integers::<u32>().min_value(0).max_value(120));
    let name = tc.draw(gs::text().min_size(1).max_size(50));
    let driving_license = if age >= 18 { tc.draw(gs::booleans()) } else { false };
    Person { name, age, driving_license }
}

// elsewhere: let p = tc.draw(people());
```
{{#endtab }}
{{#tab name="Go" }}
```go
personGen := hegel.Composite(func(tc hegel.TestCase) Person {
    age := hegel.Draw(tc, hegel.Integers(0, 120))
    name := hegel.Draw(tc, hegel.Text().MinSize(1).MaxSize(50))
    p := Person{Name: name, Age: age}
    if age >= 18 {
        p.DrivingLicense = hegel.Draw(tc, hegel.Booleans())
    }
    return p
})

// elsewhere: p := hegel.Draw(ht, personGen)
```
{{#endtab }}
{{#tab name="C++" }}
```cpp
auto person_gen = gs::compose([](const hegel::TestCase& tc) {
    auto age = tc.draw(gs::integers<int>({.min_value = 0, .max_value = 120}));
    auto name = tc.draw(gs::text({.min_size = 1, .max_size = 50}));
    bool driving_license = age >= 18 ? tc.draw(gs::booleans()) : false;
    return Person{name, age, driving_license};
});

// elsewhere: auto p = tc.draw(person_gen);
```
{{#endtab }}
{{#tab name="TypeScript" }}
```typescript
const personGen = gs.composite<Person>((tc) => {
    const age = tc.draw(gs.integers({ minValue: 0, maxValue: 120 }));
    const name = tc.draw(gs.text({ minSize: 1, maxSize: 50 }));
    const drivingLicense = age >= 18 ? tc.draw(gs.booleans()) : false;
    return { name, age, drivingLicense };
});

// elsewhere: const p = tc.draw(personGen);
```
{{#endtab }}
{{#endtabs }}

<div class="ai-written">

When every field is independent and you'd just be drawing each one with no
dependencies between them, most libraries can derive the generator for you from
the struct's type — `gs::default::<Person>()` in Rust, `gs::default_generator<Person>()`
in C++, and `gs.record({ ... })` in TypeScript — and let you override individual
fields. Reach for `composite` when fields depend on each other (as above) and for
the derived form when they don't.

</div>

## Values that depend on each other

<div class="ai-written">

The recipe people most often go looking for: two values where the second is
constrained by the first. A classic case is a list together with a *valid index*
into it. Because Hegel generators are drawn imperatively, you don't need any
special combinator — draw the first value, then use it to bound the second. The
result still shrinks correctly.

</div>

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```rust,ignore
let xs = tc.draw(gs::vecs(gs::integers::<i32>()).min_size(1));
let idx = tc.draw(gs::integers::<usize>().min_value(0).max_value(xs.len() - 1));
// xs[idx] is always in bounds.
```
{{#endtab }}
{{#tab name="Go" }}
```go
xs := hegel.Draw(ht, hegel.Lists(hegel.Integers(math.MinInt32, math.MaxInt32)).MinSize(1))
idx := hegel.Draw(ht, hegel.Integers(0, len(xs)-1))
// xs[idx] is always in bounds.
```
{{#endtab }}
{{#tab name="C++" }}
```cpp
auto xs = tc.draw(gs::vectors(gs::integers<int>(), {.min_size = 1}));
auto idx = tc.draw(gs::integers<size_t>({.min_value = 0, .max_value = xs.size() - 1}));
// xs[idx] is always in bounds.
```
{{#endtab }}
{{#tab name="TypeScript" }}
```typescript
const xs = tc.draw(gs.arrays(gs.integers(), { minSize: 1 }));
const idx = tc.draw(gs.integers({ minValue: 0, maxValue: xs.length - 1 }));
// xs[idx] is always in bounds.
```
{{#endtab }}
{{#endtabs }}

<div class="ai-written">

The same pattern produces an *ordered pair* — a low value and a high value with
`low <= high`, handy for generating a valid range. Draw the low bound, then draw
the high bound starting from it.

</div>

{{#tabs global="hegel-lang" }}
{{#tab name="Rust" }}
```rust,ignore
let low = tc.draw(gs::integers::<i32>().min_value(0).max_value(1000));
let high = tc.draw(gs::integers::<i32>().min_value(low).max_value(1000));
// low <= high.
```
{{#endtab }}
{{#tab name="Go" }}
```go
low := hegel.Draw(ht, hegel.Integers(0, 1000))
high := hegel.Draw(ht, hegel.Integers(low, 1000))
// low <= high.
```
{{#endtab }}
{{#tab name="C++" }}
```cpp
auto low = tc.draw(gs::integers<int>({.min_value = 0, .max_value = 1000}));
auto high = tc.draw(gs::integers<int>({.min_value = low, .max_value = 1000}));
// low <= high.
```
{{#endtab }}
{{#tab name="TypeScript" }}
```typescript
const low = tc.draw(gs.integers({ minValue: 0, maxValue: 1000 }));
const high = tc.draw(gs.integers({ minValue: low, maxValue: 1000 }));
// low <= high.
```
{{#endtab }}
{{#endtabs }}

<div class="ai-written">

That covers the patterns you'll reach for most. The throughline of the whole
chapter: prefer to *construct* values that already satisfy your constraints
over generating broad values and filtering them down. Constructed generators
never run out of retries, they shrink toward the simple end of exactly the space
you care about, and they make the intent of the test obvious to the next person
who reads it.

</div>
