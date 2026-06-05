// ANCHOR: impl
// MyLRUCache pretends to be an LRU cache but never evicts anything: it stores
// every entry in a map, so its size grows without bound.
export class MyLRUCache<K, V> {
	private capacity: number;
	private entries = new Map<K, V>();

	constructor(capacity: number) {
		this.capacity = capacity;
	}

	put(key: K, value: V): void {
		// BUG: a real LRU cache would evict the least-recently-used entry once
		// it reached `this.capacity`. This one never does.
		this.entries.set(key, value);
	}

	size(): number {
		return this.entries.size;
	}

	getCapacity(): number {
		return this.capacity;
	}
}
// ANCHOR_END: impl
