package lru

import (
	"math"
	"testing"

	"hegel.dev/go/hegel"
)

// ANCHOR: test
func TestRespectsLRUCapacity(t *testing.T) {
	hegel.Test(t, func(ht *hegel.T) {
		capacity := hegel.Draw(ht, hegel.Integers(0, math.MaxInt))
		cache := NewMyLRUCache[string, int](capacity)

		keys := hegel.Draw(ht, hegel.Lists(hegel.Text()))
		for _, key := range keys {
			value := hegel.Draw(ht, hegel.Integers(math.MinInt, math.MaxInt))
			cache.Put(key, value)
		}

		if cache.Size() > capacity {
			ht.Fatalf("cache size exceeds capacity")
		}
	})
}
// ANCHOR_END: test
