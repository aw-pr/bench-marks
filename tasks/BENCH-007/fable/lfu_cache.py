"""
lfu_cache.py -- O(1) amortised LFU (Least Frequently Used) cache.

Structure
---------
Three hash maps plus one integer:

  _values : key -> value
  _freqs  : key -> current use-frequency of that key
  _buckets: freq -> OrderedDict of keys at that frequency
            (insertion order == recency order; the FIRST entry is the
            least-recently-used key at that frequency, the LAST is the
            most-recently-used)
  _min_freq: the smallest frequency whose bucket is non-empty

O(1) amortised argument (structural, not empirical)
---------------------------------------------------
Every public operation decomposes into a constant number of primitive
steps, each of which is itself O(1) on the underlying structures:

1. Hash-map get/set/delete on _values, _freqs, _buckets: O(1) amortised
   by the standard hash-table argument (Python dict).

2. Moving a key between frequency buckets on a use-bump: delete the key
   from bucket f (OrderedDict deletion by key -- an O(1) hash lookup
   plus an O(1) doubly-linked-list unlink, which is exactly how CPython
   implements OrderedDict) and append it to bucket f+1 (O(1) tail
   insertion). No bucket is ever scanned or sorted; we always address
   entries directly by key or by list end.

3. Maintaining _min_freq WITHOUT scanning: the pointer only ever needs
   two kinds of update, both O(1) decisions --
     (a) inserting a brand-new key: its frequency is 1, and 1 is <= any
         possible existing frequency, so _min_freq := 1 unconditionally;
     (b) bumping a key from f to f+1: the only bucket that can have
         been emptied by this operation is bucket f itself, so
         _min_freq needs adjusting only if f == _min_freq and bucket f
         is now empty -- in which case the unique candidate for the new
         minimum is f+1 (the bumped key itself now lives there, and no
         bucket strictly between f and f+1 exists). So _min_freq := f+1.
   In neither case do we search over buckets for a minimum. This is the
   step that a heap (O(log n)) or a min-scan (O(n)) would otherwise pay
   for; the invariant above eliminates it.

4. Eviction: read the first (LRU) entry of _buckets[_min_freq] via
   next(iter(...)) -- the head of the OrderedDict's internal linked
   list, an O(1) access, not an iteration -- and delete it from the
   three maps.

Hence get and put each perform O(1) hash operations plus O(1) linked-
list splices, giving O(1) amortised overall (worst-case constant apart
from the hash-table amortisation itself).
"""

from __future__ import annotations

from collections import OrderedDict
from typing import Any, Hashable


class LFUCache:
    """LFU cache with LRU tie-breaking inside each frequency class.

    - get(key) returns the value or None; a hit bumps the key's
      frequency and marks it most-recently-used within its new bucket.
    - put(key, value) inserts or updates; updating an existing key
      counts as a use (frequency bump) but not as a new insertion.
      Inserting into a full cache evicts the least-frequently-used key,
      breaking frequency ties by least-recent use.
    - capacity == 0 is valid: the cache never stores anything.
    """

    def __init__(self, capacity: int):
        if capacity < 0:
            raise ValueError("capacity must be >= 0")
        self._capacity = capacity
        self._values: dict[Hashable, Any] = {}
        self._freqs: dict[Hashable, int] = {}
        self._buckets: dict[int, OrderedDict[Hashable, None]] = {}
        self._min_freq = 0

    def _bump(self, key: Hashable) -> None:
        """Move `key` from bucket f to bucket f+1, MRU position. O(1)."""
        f = self._freqs[key]
        bucket = self._buckets[f]
        del bucket[key]                       # O(1) unlink by key
        if not bucket:
            del self._buckets[f]
            if self._min_freq == f:
                self._min_freq = f + 1        # sole candidate; no scan
        self._freqs[key] = f + 1
        self._buckets.setdefault(f + 1, OrderedDict())[key] = None

    def get(self, key: Hashable) -> Any | None:
        if key not in self._values:
            return None
        self._bump(key)
        return self._values[key]

    def put(self, key: Hashable, value: Any) -> None:
        if self._capacity == 0:
            return

        if key in self._values:               # update: a use, not an insert
            self._values[key] = value
            self._bump(key)
            return

        if len(self._values) >= self._capacity:
            victim_bucket = self._buckets[self._min_freq]
            victim = next(iter(victim_bucket))  # LRU head of min bucket, O(1)
            del victim_bucket[victim]
            if not victim_bucket:
                del self._buckets[self._min_freq]
            del self._values[victim]
            del self._freqs[victim]

        self._values[key] = value
        self._freqs[key] = 1
        self._buckets.setdefault(1, OrderedDict())[key] = None
        self._min_freq = 1                    # 1 <= every existing freq

    def __len__(self) -> int:
        return len(self._values)

    def __contains__(self, key: Hashable) -> bool:
        return key in self._values


if __name__ == "__main__":
    import unittest

    class TestLFUCache(unittest.TestCase):
        def test_basic_get_put_and_eviction(self):
            c = LFUCache(2)
            c.put("a", 1)
            c.put("b", 2)
            self.assertEqual(c.get("a"), 1)   # freq(a)=2, freq(b)=1
            c.put("c", 3)                     # evicts b: lowest frequency
            self.assertIsNone(c.get("b"))
            self.assertEqual(c.get("a"), 1)
            self.assertEqual(c.get("c"), 3)
            self.assertEqual(len(c), 2)

        def test_frequency_tie_broken_by_recency(self):
            c = LFUCache(3)
            c.put("x", 1)
            c.put("y", 2)
            c.put("z", 3)
            # All start at freq 1; bump all three to freq 2 in the
            # order x, z, y so they stay tied on frequency but have a
            # known recency order (LRU -> MRU): x, z, y.
            c.get("x")
            c.get("z")
            c.get("y")
            # All tied at freq 2; LRU among them is x.
            c.put("w", 4)                     # must evict x
            self.assertIsNone(c.get("x"))
            self.assertEqual(c.get("z"), 3)
            self.assertEqual(c.get("y"), 2)
            self.assertEqual(c.get("w"), 4)

        def test_get_marks_mru_within_bucket(self):
            c = LFUCache(2)
            c.put("a", 1)
            c.put("b", 2)
            c.get("a")
            c.get("b")
            c.get("a")                        # a: freq 3, b: freq 2
            c.put("d", 4)                     # evicts b (lower freq)
            self.assertIsNone(c.get("b"))
            self.assertEqual(c.get("a"), 1)

        def test_capacity_zero_is_a_noop(self):
            c = LFUCache(0)
            self.assertIsNone(c.get("a"))
            c.put("a", 1)
            self.assertIsNone(c.get("a"))
            self.assertEqual(len(c), 0)
            self.assertNotIn("a", c)

        def test_value_update_is_use_not_insertion(self):
            c = LFUCache(2)
            c.put("a", 1)
            c.put("b", 2)
            c.put("a", 10)                    # update: freq(a)=2, len stays 2
            self.assertEqual(len(c), 2)
            c.put("c", 3)                     # full: evict b (freq 1), not a
            self.assertIsNone(c.get("b"))
            self.assertEqual(c.get("a"), 10)
            self.assertEqual(c.get("c"), 3)

        def test_min_freq_resets_on_new_insert_after_bumps(self):
            c = LFUCache(2)
            c.put("a", 1)
            c.get("a")
            c.get("a")                        # freq(a)=3, min_freq tracked up
            c.put("b", 2)                     # fresh key at freq 1
            c.put("c", 3)                     # full: b (freq 1) evicted, not a
            self.assertIsNone(c.get("b"))
            self.assertEqual(c.get("a"), 1)
            self.assertEqual(c.get("c"), 3)

        def test_missing_key_returns_none(self):
            self.assertIsNone(LFUCache(3).get("nope"))

        def test_negative_capacity_rejected(self):
            with self.assertRaises(ValueError):
                LFUCache(-1)

        def test_none_values_are_storable(self):
            # get() returning None is ambiguous by API design; storing
            # None must still bump frequency and count as present.
            c = LFUCache(2)
            c.put("a", None)
            self.assertIn("a", c)
            self.assertIsNone(c.get("a"))     # hit, freq(a)=2
            c.put("b", 2)
            c.put("c", 3)                     # evicts b (freq 1 < freq 2)
            self.assertIn("a", c)
            self.assertNotIn("b", c)

    unittest.main(verbosity=2)
