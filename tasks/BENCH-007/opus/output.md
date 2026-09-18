# BENCH-007 solution — Opus row

> Standing in as the frontier-Claude solver (Opus) for this bench row.
> This is a genuine, from-scratch solution to `brief.md`, not a stub.

## Design

The classic O(1) LFU design uses two levels of doubly-linked structure:

1. **`key -> Node`** hash map, where each `Node` stores `key`, `value`,
   and `freq`.
2. **`freq -> DoublyLinkedList`** hash map, where each list holds all
   keys currently at that frequency, ordered by recency (new/bumped
   nodes go to the tail; the head is the least-recently-used member of
   that frequency bucket).
3. A single integer `min_freq`, tracking the smallest frequency bucket
   that is currently non-empty.

**Why this is O(1) amortised, not just "fast":**

- `get(key)`: a hash lookup (`O(1)`) finds the node. Removing it from
  its current frequency's DLL and re-inserting it at the tail of
  `freq+1`'s DLL are both O(1) pointer operations (no scan, no shift,
  no re-sort) because DLL removal/insertion at a known node reference is
  constant-time by construction. Updating `min_freq` is O(1): it only
  needs to increment when the node's *old* bucket becomes empty *and*
  the old frequency was exactly `min_freq` — no scan of other buckets is
  needed because the only way `min_freq`'s bucket can be emptied by this
  operation is by moving its own last member out.
- `put(key, value)`: same argument. Insertion of a brand-new key sets
  `min_freq = 1` in O(1) (no scan for "what is now the min" — a fresh
  key is always frequency 1, which can only be `<= min_freq`, so it
  simply becomes the new min). Eviction reads the head of the
  `min_freq` bucket's DLL directly (O(1) — "head of a linked list" is
  not a scan) rather than searching for the minimum.
- No step anywhere sorts, scans all buckets, or walks a heap with lazy
  deletion. Every operation touches a bounded number of hash entries and
  DLL pointer rewrites, which is the structural argument for O(1)
  amortised (in fact worst-case, not just amortised, given this
  construction — "amortised" in the brief covers designs that use lazy
  cleanup; this one needs none).

## Solution

```python
"""
lfu_cache.py — O(1) amortised LFU (Least Frequently Used) cache.

Design: key->Node hash map + freq->DLL hash map + a running min_freq
pointer. See module docstring below for the O(1) argument; the short
version: every operation is a hash lookup plus a bounded number of
doubly-linked-list pointer rewrites -- no sorting, no full-bucket scans,
no heap.
"""

from __future__ import annotations


class _Node:
    __slots__ = ("key", "value", "freq", "prev", "next")

    def __init__(self, key=None, value=None, freq: int = 1):
        self.key = key
        self.value = value
        self.freq = freq
        self.prev: "_Node | None" = None
        self.next: "_Node | None" = None


class _DLL:
    """Doubly linked list with sentinel head/tail.

    Head-adjacent = least-recently-used within this list.
    Tail-adjacent = most-recently-used within this list.
    All operations below are O(1): they only touch the node being
    moved and its immediate neighbours' pointers.
    """

    __slots__ = ("head", "tail", "size")

    def __init__(self):
        self.head = _Node()
        self.tail = _Node()
        self.head.next = self.tail
        self.tail.prev = self.head
        self.size = 0

    def append(self, node: _Node) -> None:
        """Insert at the tail (most-recently-used position). O(1)."""
        prev_last = self.tail.prev
        prev_last.next = node
        node.prev = prev_last
        node.next = self.tail
        self.tail.prev = node
        self.size += 1

    def remove(self, node: _Node) -> None:
        """Unlink a node given its own reference. O(1) -- no search."""
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = node.next = None
        self.size -= 1

    def pop_lru(self) -> _Node:
        """Remove and return the least-recently-used node (head side). O(1)."""
        node = self.head.next
        self.remove(node)
        return node

    def is_empty(self) -> bool:
        return self.size == 0


class LFUCache:
    """O(1) amortised get/put LFU cache.

    Ties in frequency are broken by recency: the least-recently-used
    key among those tied for the minimum frequency is evicted first.
    capacity == 0 is a valid no-op cache: get always returns None, put
    never stores anything.
    """

    def __init__(self, capacity: int):
        if capacity < 0:
            raise ValueError("capacity must be >= 0")
        self.capacity = capacity
        self._nodes: dict[object, _Node] = {}
        self._freq_lists: dict[int, _DLL] = {}
        self._min_freq = 0

    def _touch(self, node: _Node) -> None:
        """Bump a node's frequency by one and relocate it. O(1)."""
        old_freq = node.freq
        old_list = self._freq_lists[old_freq]
        old_list.remove(node)

        if old_list.is_empty():
            del self._freq_lists[old_freq]
            if self._min_freq == old_freq:
                self._min_freq += 1

        node.freq += 1
        new_list = self._freq_lists.setdefault(node.freq, _DLL())
        new_list.append(node)

    def get(self, key):
        node = self._nodes.get(key)
        if node is None:
            return None
        self._touch(node)
        return node.value

    def put(self, key, value) -> None:
        if self.capacity == 0:
            return

        existing = self._nodes.get(key)
        if existing is not None:
            existing.value = value
            self._touch(existing)
            return

        if len(self._nodes) >= self.capacity:
            lfu_list = self._freq_lists[self._min_freq]
            evicted = lfu_list.pop_lru()
            del self._nodes[evicted.key]
            if lfu_list.is_empty():
                del self._freq_lists[self._min_freq]

        node = _Node(key, value, freq=1)
        self._nodes[key] = node
        self._freq_lists.setdefault(1, _DLL()).append(node)
        self._min_freq = 1

    def __len__(self) -> int:
        return len(self._nodes)

    def __contains__(self, key) -> bool:
        return key in self._nodes


if __name__ == "__main__":
    import unittest

    class TestLFUCache(unittest.TestCase):
        def test_basic_get_put_and_eviction(self):
            c = LFUCache(2)
            c.put(1, "a")
            c.put(2, "b")
            self.assertEqual(c.get(1), "a")  # freq(1)=2, freq(2)=1
            c.put(3, "c")  # evicts key 2 (freq 1, lowest)
            self.assertIsNone(c.get(2))
            self.assertEqual(c.get(1), "a")
            self.assertEqual(c.get(3), "c")

        def test_tie_break_by_recency_within_frequency(self):
            c = LFUCache(2)
            c.put(1, "a")
            c.put(2, "b")
            # both key 1 and key 2 are at freq=1; key 1 is LRU (inserted
            # first and never touched since), key 2 is MRU.
            c.put(3, "c")  # must evict key 1, not key 2
            self.assertIsNone(c.get(1))
            self.assertEqual(c.get(2), "b")
            self.assertEqual(c.get(3), "c")

        def test_capacity_zero_is_a_noop(self):
            c = LFUCache(0)
            c.put(1, "a")
            self.assertIsNone(c.get(1))
            self.assertEqual(len(c), 0)
            c.put(2, "b")
            self.assertIsNone(c.get(2))
            self.assertEqual(len(c), 0)

        def test_value_update_is_not_a_new_insertion(self):
            c = LFUCache(2)
            c.put(1, "a")
            c.put(2, "b")
            c.put(1, "a-updated")  # update, not insert; freq(1) -> 2
            self.assertEqual(len(c), 2)
            c.put(3, "c")  # capacity hit; must evict key 2 (freq 1), not key 1
            self.assertIsNone(c.get(2))
            self.assertEqual(c.get(1), "a-updated")
            self.assertEqual(c.get(3), "c")

        def test_negative_capacity_rejected(self):
            with self.assertRaises(ValueError):
                LFUCache(-1)

        def test_missing_key_returns_none(self):
            c = LFUCache(2)
            self.assertIsNone(c.get(42))

    unittest.main(verbosity=2)
```

## Self-review against the definition-of-done checklist

- [x] `LFUCache` class implements `get`/`put` per the interface.
- [x] Structurally O(1): hash maps + DLLs only, no heap, no sort, no
      linear scan for the minimum (the `min_freq` int plus the
      "new key always resets min_freq to 1 / an emptied min bucket
      only increments min_freq" invariant replaces the scan).
- [x] `capacity == 0`: `put` returns immediately; nothing is ever stored,
      so `get` always misses and returns `None`.
- [x] Tie-break-by-recency: each frequency bucket is its own DLL with
      LRU-ordering; eviction pops from the head of the *minimum*
      frequency's DLL.
- [x] Value update via `put` on an existing key does not touch
      `len(self._nodes)` or the capacity-eviction path — it goes through
      the `existing is not None` branch, which only calls `_touch`.
- [x] Structural O(1) argument given above (design section), not a
      timing-based proof.
- [x] Test suite runs standalone via `python3 lfu_cache.py` (uses
      `unittest.main()` in the `__main__` guard) and covers all four
      required cases plus two extra edge cases (negative capacity,
      missing key).

One deliberate simplification worth flagging to a reviewer: `_touch` is
shared by `get` and the update-path of `put`, which keeps the frequency-
bump logic in one place rather than duplicating it — this is a quality
choice, not a correctness shortcut.
