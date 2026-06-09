package lru

import "container/list"

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

func (c *MyLRUCache[K, V]) Get(key K) (V, bool) {
	value, ok := c.entries[key]
	return value, ok
}

func (c *MyLRUCache[K, V]) Size() int {
	return len(c.entries)
}

func (c *MyLRUCache[K, V]) Capacity() int {
	return c.capacity
}

// ANCHOR_END: impl

// CappedCache is a second attempt: instead of growing without bound, it simply
// stops accepting new keys once it is full. Its size stays within the capacity,
// but it still never evicts, so it keeps the oldest entries rather than the
// most-recently-used ones.
type CappedCache[K comparable, V any] struct {
	capacity int
	entries  map[K]V
}

func NewCappedCache[K comparable, V any](capacity int) *CappedCache[K, V] {
	return &CappedCache[K, V]{capacity: capacity, entries: make(map[K]V)}
}

// ANCHOR: capped-put
func (c *CappedCache[K, V]) Put(key K, value V) {
	// BUG: once we are full we drop the write entirely, rather than evicting the
	// least-recently-used entry to make room for the new one.
	if _, present := c.entries[key]; len(c.entries) >= c.capacity && !present {
		return
	}
	c.entries[key] = value
}

// ANCHOR_END: capped-put

func (c *CappedCache[K, V]) Get(key K) (V, bool) {
	value, ok := c.entries[key]
	return value, ok
}

func (c *CappedCache[K, V]) Size() int {
	return len(c.entries)
}

// LRUCache is an actual LRU cache with O(1) Get and Put. It threads its entries
// onto a doubly-linked list ordered by recency (front = most-recently-used) and
// keeps a map from key to the list element, so any entry can be found and moved
// to the front in constant time, and eviction is just dropping the back element.
type lruEntry[K comparable, V any] struct {
	key   K
	value V
}

type LRUCache[K comparable, V any] struct {
	capacity int
	order    *list.List          // *lruEntry, front = most-recently-used
	items    map[K]*list.Element // key -> its element in order
}

func NewLRUCache[K comparable, V any](capacity int) *LRUCache[K, V] {
	return &LRUCache[K, V]{
		capacity: capacity,
		order:    list.New(),
		items:    make(map[K]*list.Element),
	}
}

func (c *LRUCache[K, V]) Put(key K, value V) {
	if el, ok := c.items[key]; ok {
		el.Value.(*lruEntry[K, V]).value = value
		c.order.MoveToFront(el)
		return
	}
	c.items[key] = c.order.PushFront(&lruEntry[K, V]{key: key, value: value})
	if len(c.items) > c.capacity {
		lru := c.order.Back()
		c.order.Remove(lru)
		delete(c.items, lru.Value.(*lruEntry[K, V]).key)
	}
}

func (c *LRUCache[K, V]) Get(key K) (V, bool) {
	if el, ok := c.items[key]; ok {
		c.order.MoveToFront(el)
		return el.Value.(*lruEntry[K, V]).value, true
	}
	var zero V
	return zero, false
}

func (c *LRUCache[K, V]) Size() int {
	return len(c.items)
}
