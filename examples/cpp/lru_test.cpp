#include <gtest/gtest.h>
#include <hegel/hegel.h>

#include <stdexcept>
#include <string>

#include "cache.hpp"

namespace gs = hegel::generators;

// ANCHOR: test
TEST(MyLRUCache, RespectsCapacity) {
	hegel::test([](hegel::TestCase& tc) {
		auto capacity = tc.draw(gs::integers<size_t>({.min_value = 0}));
		MyLRUCache<std::string, int> cache(capacity);

		auto entries = tc.draw(
		  gs::vectors(gs::tuples(gs::text(), gs::integers<int>()))
		);
		for (const auto& [key, value] : entries) {
			cache.put(key, value);
		}

		// Hegel detects failures via thrown exceptions, so the property throws
		// rather than using a (non-throwing) gtest assertion.
		if (cache.size() > capacity) {
			throw std::runtime_error("cache size exceeds capacity");
		}
	});
}
// ANCHOR_END: test
