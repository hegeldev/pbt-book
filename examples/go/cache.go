package lru

// ANCHOR: impl
// MyLRUCache pretends to be an LRU cache but never evicts anything: it stores
// every entry in a map, so its size grows without bound.
type MyLRUCache[K comparable, V any] struct {
	capacity int
	entries  map[K]V
}

func NewMyLRUCache[K comparable, V any](capacity int) *MyLRUCache[K, V] {
	return &MyLRUCache[K, V]{capacity: capacity, entries: make(map[K]V)}
}

func (c *MyLRUCache[K, V]) Put(key K, value V) {
	// BUG: a real LRU cache would evict the least-recently-used entry once it
	// reached c.capacity. This one never does.
	c.entries[key] = value
}

func (c *MyLRUCache[K, V]) Size() int {
	return len(c.entries)
}

func (c *MyLRUCache[K, V]) Capacity() int {
	return c.capacity
}

// ANCHOR_END: impl
