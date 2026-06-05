use hegel::generators as gs;
use hegel::TestCase;
use lru_example::MyLRUCache;

// ANCHOR: test
#[hegel::test]
fn test_respects_lru_capacity(tc: TestCase) {
    let capacity = tc.draw(gs::integers::<usize>().min_value(0));
    let mut cache = MyLRUCache::<String, i64>::new(capacity);

    let entries = tc.draw(gs::vecs(gs::tuples!(gs::text(), gs::integers::<i64>())));
    for (key, value) in entries {
        cache.put(key, value);
    }

    assert!(cache.size() <= capacity);
}
// ANCHOR_END: test
