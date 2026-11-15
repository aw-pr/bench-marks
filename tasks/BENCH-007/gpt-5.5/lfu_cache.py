"""O(1)-amortised LFU cache with recency tie-breaking.

The cache keeps three pieces of state:

* ``_items`` maps each key directly to its ``_Entry``.
* ``_freqs`` maps a frequency to an ``OrderedDict`` of entries at that
  frequency. Inside one frequency bucket, insertion order is LRU -> MRU.
* ``_min_freq`` records the smallest frequency currently present.

``get`` and ``put`` never search for a key, a frequency, or an eviction
candidate. A hit removes the key from exactly one frequency bucket and appends
it to exactly one other bucket. Eviction pops the oldest key from the bucket
named by ``_min_freq``. Python dictionaries and ``OrderedDict`` operations used
here are O(1) amortised, so both public operations are O(1) amortised. Frequency
values may grow over time, but moving from f to f + 1 is still a constant number
of hash-table and linked-list updates, not a scan or sort over frequencies.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class _Entry:
    key: Any
    value: Any
    freq: int = 1


class LFUCache:
    """Least Frequently Used cache with LRU eviction among frequency ties."""

    def __init__(self, capacity: int):
        if capacity < 0:
            raise ValueError("capacity must be non-negative")

        self.capacity = capacity
        self._items: dict[Any, _Entry] = {}
        self._freqs: dict[int, OrderedDict[Any, _Entry]] = {}
        self._min_freq = 0

    def get(self, key: Any) -> Any | None:
        entry = self._items.get(key)
        if entry is None:
            return None

        self._promote(entry)
        return entry.value

    def put(self, key: Any, value: Any) -> None:
        if self.capacity == 0:
            return

        entry = self._items.get(key)
        if entry is not None:
            entry.value = value
            self._promote(entry)
            return

        if len(self._items) == self.capacity:
            self._evict_lfu()

        entry = _Entry(key=key, value=value)
        self._items[key] = entry
        self._freqs.setdefault(1, OrderedDict())[key] = entry
        self._min_freq = 1

    def _promote(self, entry: _Entry) -> None:
        old_freq = entry.freq
        old_bucket = self._freqs[old_freq]
        del old_bucket[entry.key]

        if not old_bucket:
            del self._freqs[old_freq]
            if self._min_freq == old_freq:
                self._min_freq = old_freq + 1

        entry.freq += 1
        self._freqs.setdefault(entry.freq, OrderedDict())[entry.key] = entry

    def _evict_lfu(self) -> None:
        bucket = self._freqs[self._min_freq]
        key, _ = bucket.popitem(last=False)
        del self._items[key]

        if not bucket:
            del self._freqs[self._min_freq]
            self._min_freq = 0


def _run_tests() -> None:
    import sys
    import unittest

    class LFUCacheTests(unittest.TestCase):
        def test_basic_get_put_and_eviction_on_capacity(self) -> None:
            cache = LFUCache(2)

            cache.put("a", 1)
            cache.put("b", 2)

            self.assertEqual(cache.get("a"), 1)
            cache.put("c", 3)

            self.assertEqual(cache.get("b"), None)
            self.assertEqual(cache.get("a"), 1)
            self.assertEqual(cache.get("c"), 3)

        def test_frequency_tie_breaks_by_recency(self) -> None:
            cache = LFUCache(2)

            cache.put("a", 1)
            cache.put("b", 2)
            self.assertEqual(cache.get("a"), 1)
            self.assertEqual(cache.get("b"), 2)

            cache.put("c", 3)

            self.assertEqual(cache.get("a"), None)
            self.assertEqual(cache.get("b"), 2)
            self.assertEqual(cache.get("c"), 3)

        def test_capacity_zero_never_stores(self) -> None:
            cache = LFUCache(0)

            cache.put("a", 1)
            cache.put("b", 2)

            self.assertEqual(cache.get("a"), None)
            self.assertEqual(cache.get("b"), None)
            self.assertEqual(len(cache._items), 0)

        def test_value_update_counts_as_use_not_insertion(self) -> None:
            cache = LFUCache(2)

            cache.put("a", 1)
            cache.put("b", 2)
            cache.put("a", 10)
            cache.put("c", 3)

            self.assertEqual(cache.get("a"), 10)
            self.assertEqual(cache.get("b"), None)
            self.assertEqual(cache.get("c"), 3)

        def test_update_changes_recency_within_new_frequency(self) -> None:
            cache = LFUCache(2)

            cache.put("a", 1)
            cache.put("b", 2)
            cache.get("a")
            cache.get("b")
            cache.put("a", 10)
            cache.get("b")
            cache.put("c", 3)

            self.assertEqual(cache.get("a"), None)
            self.assertEqual(cache.get("b"), 2)
            self.assertEqual(cache.get("c"), 3)

        def test_negative_capacity_is_rejected(self) -> None:
            with self.assertRaises(ValueError):
                LFUCache(-1)

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(LFUCacheTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    _run_tests()
