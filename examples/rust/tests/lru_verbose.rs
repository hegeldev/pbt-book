use hegel::generators as gs;
use hegel::{TestCase, Verbosity};
use lru_example::MyLRUCache;

// Same property as lru_nonzero.rs, but run with verbose output. The `seed` makes
// the captured run reproducible; the book shows this test *without* it (inline,
// not via {{#include}}), since the seed is only a capture detail.
#[hegel::test(verbosity = Verbosity::Verbose, seed = Some(8))]
fn test_respects_lru_capacity(tc: TestCase) {
    let capacity = tc.draw(gs::integers::<usize>().min_value(1));
    let mut cache = MyLRUCache::<String, i64>::new(capacity);

    let entries = tc.draw(gs::vecs(gs::tuples!(gs::text(), gs::integers::<i64>())));
    for (key, value) in entries {
        cache.put(key, value);
    }

    assert!(cache.size() <= capacity);
}
