import { test, expect } from "vitest";
import * as hegel from "@hegeldev/hegel";
import * as gs from "@hegeldev/hegel/generators";
import { MyLRUCache } from "../src/cache";

// ANCHOR: test
test(
	"MyLRUCache respects capacity",
	hegel.test((tc) => {
		const capacity = tc.draw(gs.integers({ minValue: 0 }));
		const cache = new MyLRUCache<string, number>(capacity);

		const entries = tc.draw(gs.arrays(gs.tuples(gs.text(), gs.integers())));
		for (const [key, value] of entries) {
			cache.put(key, value);
		}

		expect(cache.size()).toBeLessThanOrEqual(capacity);
	}),
);
// ANCHOR_END: test
