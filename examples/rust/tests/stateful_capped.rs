use hegel::generators as gs;
use hegel::stateful::{variables, Variables};
use hegel::TestCase;
use lru_example::CappedCache;
use std::collections::HashMap;

// The same state machine as stateful.rs, but driving CappedCache (which stops
// accepting new keys once it is full) instead of MyLRUCache.
struct CacheModel {
    cache: CappedCache<String, i64>,
    capacity: usize,
    store: HashMap<String, i64>,
    recency: HashMap<String, u64>,
    clock: u64,
    keys: Variables<String>,
}

#[hegel::state_machine]
impl CacheModel {
    #[rule]
    fn put(&mut self, tc: TestCase) {
        let key = tc.draw(gs::text());
        let value = tc.draw(gs::integers::<i64>());

        self.cache.put(key.clone(), value);

        self.store.insert(key.clone(), value);
        self.recency.insert(key.clone(), self.clock);
        self.clock += 1;
        if self.store.len() > self.capacity {
            let lru = self
                .recency
                .iter()
                .min_by_key(|(_, &used)| used)
                .map(|(k, _)| k.clone())
                .unwrap();
            self.store.remove(&lru);
            self.recency.remove(&lru);
        }

        self.keys.add(key);
    }

    #[rule]
    fn get(&mut self, _tc: TestCase) {
        let key = self.keys.draw().clone();
        if self.store.contains_key(&key) {
            self.recency.insert(key.clone(), self.clock);
            self.clock += 1;
        }
        assert!(
            self.cache.get(&key) == self.store.get(&key),
            "get({:?}): cache has {:?}, model has {:?}",
            key,
            self.cache.get(&key),
            self.store.get(&key)
        );
    }

    #[invariant]
    fn same_size(&mut self, _tc: TestCase) {
        assert!(
            self.cache.size() == self.store.len(),
            "cache size {} != model size {}",
            self.cache.size(),
            self.store.len()
        );
    }
}

#[hegel::test]
fn test_cache_matches_model(tc: TestCase) {
    let capacity = tc.draw(gs::integers::<usize>().min_value(1));
    let machine = CacheModel {
        cache: CappedCache::new(capacity),
        capacity,
        store: HashMap::new(),
        recency: HashMap::new(),
        clock: 0,
        keys: variables(&tc),
    };
    hegel::stateful::run(machine, tc);
}
