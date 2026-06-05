use std::collections::HashMap;
use std::hash::Hash;

// ANCHOR: impl
/// An "LRU cache" that never actually evicts anything: it just stores every
/// entry in a map. Because it ignores its capacity, its size grows without
/// bound.
pub struct MyLRUCache<K, V> {
    capacity: usize,
    entries: HashMap<K, V>,
}

impl<K: Hash + Eq, V> MyLRUCache<K, V> {
    pub fn new(capacity: usize) -> Self {
        Self {
            capacity,
            entries: HashMap::new(),
        }
    }

    pub fn capacity(&self) -> usize {
        self.capacity
    }

    pub fn put(&mut self, key: K, value: V) {
        // BUG: a real LRU cache would evict the least-recently-used entry once
        // it reached `self.capacity`. This one never does.
        self.entries.insert(key, value);
    }

    pub fn size(&self) -> usize {
        self.entries.len()
    }
}
// ANCHOR_END: impl
