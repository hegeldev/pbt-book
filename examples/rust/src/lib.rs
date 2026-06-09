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

    pub fn get(&self, key: &K) -> Option<&V> {
        self.entries.get(key)
    }

    pub fn size(&self) -> usize {
        self.entries.len()
    }
}
// ANCHOR_END: impl

/// A second attempt: instead of growing without bound, this cache simply stops
/// accepting new keys once it is full. Its size stays within the capacity, but
/// it still never evicts, so it keeps the *oldest* entries rather than the
/// most-recently-used ones.
pub struct CappedCache<K, V> {
    capacity: usize,
    entries: HashMap<K, V>,
}

impl<K: Hash + Eq, V> CappedCache<K, V> {
    pub fn new(capacity: usize) -> Self {
        Self {
            capacity,
            entries: HashMap::new(),
        }
    }

    // ANCHOR: capped-put
    pub fn put(&mut self, key: K, value: V) {
        // BUG: once we are full we drop the write entirely, rather than evicting
        // the least-recently-used entry to make room for the new one.
        if self.entries.len() >= self.capacity && !self.entries.contains_key(&key) {
            return;
        }
        self.entries.insert(key, value);
    }
    // ANCHOR_END: capped-put

    pub fn get(&self, key: &K) -> Option<&V> {
        self.entries.get(key)
    }

    pub fn size(&self) -> usize {
        self.entries.len()
    }
}

// ANCHOR: real-impl
/// An LRU cache with O(1) `get` and `put`. Entries live in an arena (`nodes`)
/// and are threaded into a doubly-linked list ordered by recency: `head` is the
/// most-recently-used entry, `tail` the least-recently-used. A map from key to
/// arena index lets us find and re-link any entry in constant time, and evicting
/// is just dropping the tail. Freed slots are recycled via `free`.
pub struct LRUCache<K, V> {
    capacity: usize,
    map: HashMap<K, usize>,
    nodes: Vec<Node<K, V>>,
    free: Vec<usize>,
    head: Option<usize>,
    tail: Option<usize>,
}

struct Node<K, V> {
    key: K,
    value: V,
    prev: Option<usize>,
    next: Option<usize>,
}

impl<K: Hash + Eq + Clone, V> LRUCache<K, V> {
    pub fn new(capacity: usize) -> Self {
        Self {
            capacity,
            map: HashMap::new(),
            nodes: Vec::new(),
            free: Vec::new(),
            head: None,
            tail: None,
        }
    }

    // Detach node `i` from the list, leaving it in the arena.
    fn unlink(&mut self, i: usize) {
        let (prev, next) = (self.nodes[i].prev, self.nodes[i].next);
        match prev {
            Some(p) => self.nodes[p].next = next,
            None => self.head = next,
        }
        match next {
            Some(n) => self.nodes[n].prev = prev,
            None => self.tail = prev,
        }
    }

    // Link node `i` in at the head (most-recently-used) position.
    fn push_front(&mut self, i: usize) {
        self.nodes[i].prev = None;
        self.nodes[i].next = self.head;
        if let Some(h) = self.head {
            self.nodes[h].prev = Some(i);
        }
        self.head = Some(i);
        if self.tail.is_none() {
            self.tail = Some(i);
        }
    }

    fn move_to_front(&mut self, i: usize) {
        self.unlink(i);
        self.push_front(i);
    }

    pub fn put(&mut self, key: K, value: V) {
        if let Some(&i) = self.map.get(&key) {
            self.nodes[i].value = value;
            self.move_to_front(i);
            return;
        }

        let node = Node {
            key: key.clone(),
            value,
            prev: None,
            next: None,
        };
        let i = match self.free.pop() {
            Some(i) => {
                self.nodes[i] = node;
                i
            }
            None => {
                self.nodes.push(node);
                self.nodes.len() - 1
            }
        };
        self.map.insert(key, i);
        self.push_front(i);

        if self.map.len() > self.capacity {
            if let Some(t) = self.tail {
                self.unlink(t);
                let evicted = self.nodes[t].key.clone();
                self.map.remove(&evicted);
                self.free.push(t);
            }
        }
    }

    pub fn get(&mut self, key: &K) -> Option<&V> {
        let i = *self.map.get(key)?;
        self.move_to_front(i);
        Some(&self.nodes[i].value)
    }

    pub fn size(&self) -> usize {
        self.map.len()
    }
}
// ANCHOR_END: real-impl
