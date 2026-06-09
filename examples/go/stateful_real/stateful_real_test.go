package statefulreal

import (
	"fmt"
	"math"
	"testing"

	. "lru-example"

	"hegel.dev/go/hegel"
)

// The same state machine as stateful/stateful_test.go, but driving LRUCache (an
// actual LRU cache) instead of the broken MyLRUCache. With a correct
// implementation the model and the cache should agree no matter what we run.
type cacheModel struct {
	cache    *LRUCache[string, int]
	capacity int
	store    map[string]int
	recency  map[string]int
	clock    int
	keys     []string
}

func (m *cacheModel) RulePut(tc hegel.TestCase) {
	key := hegel.Draw(tc, hegel.Text())
	value := hegel.Draw(tc, hegel.Integers(math.MinInt, math.MaxInt))

	m.cache.Put(key, value)

	m.store[key] = value
	m.recency[key] = m.clock
	m.clock++
	if len(m.store) > m.capacity {
		lru, oldest := "", math.MaxInt
		for k, used := range m.recency {
			if used < oldest {
				lru, oldest = k, used
			}
		}
		delete(m.store, lru)
		delete(m.recency, lru)
	}

	m.keys = append(m.keys, key)
}

func (m *cacheModel) RuleGet(tc hegel.TestCase) {
	tc.Assume(len(m.keys) > 0)
	key := hegel.Draw(tc, hegel.SampledFrom(m.keys))
	if _, ok := m.store[key]; ok {
		m.recency[key] = m.clock
		m.clock++
	}
	got, gotOK := m.cache.Get(key)
	want, wantOK := m.store[key]
	if gotOK != wantOK || got != want {
		panic(fmt.Sprintf("get(%q): cache has (%v, %v), model has (%v, %v)",
			key, got, gotOK, want, wantOK))
	}
}

func (m *cacheModel) InvariantSameSize(_ hegel.TestCase) {
	if m.cache.Size() != len(m.store) {
		panic(fmt.Sprintf("cache size %d != model size %d",
			m.cache.Size(), len(m.store)))
	}
}

func TestCacheMatchesModel(t *testing.T) {
	hegel.Test(t, func(ht *hegel.T) {
		capacity := hegel.Draw(ht, hegel.Integers(1, math.MaxInt))
		m := &cacheModel{
			cache:    NewLRUCache[string, int](capacity),
			capacity: capacity,
			store:    make(map[string]int),
			recency:  make(map[string]int),
		}
		hegel.RunStateful(ht, m)
	})
}
