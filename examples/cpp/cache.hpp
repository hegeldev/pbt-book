#pragma once

#include <cstddef>
#include <unordered_map>

// ANCHOR: impl
// MyLRUCache pretends to be an LRU cache but never evicts anything: it stores
// every entry in a map, so its size grows without bound.
template <typename K, typename V>
class MyLRUCache {
public:
	explicit MyLRUCache(std::size_t capacity) : capacity_(capacity) {}

	void put(const K& key, const V& value) {
		// BUG: a real LRU cache would evict the least-recently-used entry once
		// it reached capacity_. This one never does.
		entries_[key] = value;
	}

	std::size_t size() const { return entries_.size(); }
	std::size_t capacity() const { return capacity_; }

private:
	std::size_t capacity_;
	std::unordered_map<K, V> entries_;
};
// ANCHOR_END: impl
