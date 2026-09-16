"""AGENTS.md item 12: `researcher_memory["tested"]` used to persist one *full*
gene patch per candidate ever tried against an unbeaten champion, uncapped —
17,710 such entries had grown `live_state.json` to 57.2MB and counting, on
track to hit GitHub's 100MB push limit within about a week. The fix is in
`agents/researcher.py`: `Researcher.key()` now returns a 16-hex-char sha256
hash of the sorted patch instead of the patch itself, and
`Researcher.migrate_tested_entry()` normalizes an old full-patch entry to that
same hash so a mixed old/new list round-trips with identical membership.

This locks in three things a hash-based identity could get wrong quietly:
(1) the hash is genuinely stable — same patch always hashes the same, (2) a
migrated old-format entry hashes to the *same* value `key()` would produce
for the identical patch today, so exclude/dedup behavior does not change
across the migration, and (3) the size win is real on a synthetic set shaped
like the live account's.
"""
import hashlib

from agents.researcher import Researcher
from core.types import Mutation


def _mutation(patch: dict) -> Mutation:
    return Mutation(kind="tune", target="+".join(sorted(patch)), patch=patch,
                    hypothesis="test")


def test_key_is_a_short_stable_string():
    m = _mutation({"risk.stop_loss": -0.12, "risk.take_profit": 0.30})
    k1 = Researcher.key(m)
    k2 = Researcher.key(m)
    assert isinstance(k1, str)
    assert k1 == k2
    assert len(k1) == 16


def test_key_differs_for_different_patches_and_ignores_dict_order():
    m1 = _mutation({"risk.stop_loss": -0.12, "risk.take_profit": 0.30})
    m2 = _mutation({"risk.take_profit": 0.30, "risk.stop_loss": -0.12})  # same, reordered
    m3 = _mutation({"risk.stop_loss": -0.13, "risk.take_profit": 0.30})  # different value

    assert Researcher.key(m1) == Researcher.key(m2)
    assert Researcher.key(m1) != Researcher.key(m3)


def test_migrate_tested_entry_is_identity_on_new_format():
    m = _mutation({"risk.stop_loss": -0.12})
    h = Researcher.key(m)
    assert Researcher.migrate_tested_entry(h) == h


def test_migrate_tested_entry_matches_key_for_the_same_patch():
    """The actual migration correctness property: rehashing an old-format
    entry (the JSON round-trip of the pre-fix tuple-of-tuples `key()` used to
    return) must land on the exact same hash a fresh `key()` call on the
    identical patch produces today -- otherwise the migration would silently
    forget every candidate tried before this fix and let the Researcher
    re-test them for free."""
    m = _mutation({"risk.trailing_stop": -0.20, "risk.max_bars_held": 90})
    new_key = Researcher.key(m)

    # Old persisted shape: JSON has no tuples, so a `tuple[tuple[str, str]]`
    # round-trips through save/load as `list[list[str]]` -- exactly what
    # `[[list(pair) for pair in k] for k in run.tested]` used to write.
    old_sorted_patch = tuple((k, str(v)) for k, v in
                             sorted(m.patch.items(), key=lambda kv: kv[0]))
    old_format_entry = [list(pair) for pair in old_sorted_patch]

    assert Researcher.migrate_tested_entry(old_format_entry) == new_key


def test_migrated_mixed_list_has_no_spurious_duplicates_or_losses():
    """A realistic mixed `tested` list -- some entries still old-format
    (persisted before the fix), some already hashes (persisted by a session
    that already had it) -- must migrate to exactly one hash per distinct
    patch, matching what a fresh `key()` call on each patch would give."""
    patches = [{"risk.stop_loss": -0.10 - i * 0.01} for i in range(5)]
    mutations = [_mutation(p) for p in patches]
    fresh_keys = {Researcher.key(m) for m in mutations}

    mixed_list = []
    for i, m in enumerate(mutations):
        if i % 2 == 0:
            sorted_patch = tuple((k, str(v)) for k, v in
                                 sorted(m.patch.items(), key=lambda kv: kv[0]))
            mixed_list.append([list(pair) for pair in sorted_patch])  # old format
        else:
            mixed_list.append(Researcher.key(m))  # already new format

    migrated = {Researcher.migrate_tested_entry(e) for e in mixed_list}
    assert migrated == fresh_keys
    assert len(migrated) == len(patches)


def test_hash_based_tested_list_is_much_smaller_than_full_patch_list():
    """Reproduces the actual failure mode at realistic scale: a blind
    perturbation can touch ~38 genes at once (AGENTS.md item 12's own
    figure), and this account had 17,710 of them with no cap. Confirms the
    hash-based `tested` list this fix now persists is at least an order of
    magnitude smaller for the same candidate count."""
    import json
    import random

    rng = random.Random(0)
    gene_paths = [f"agents.consult_risky.genes.gene_{i}" for i in range(38)]

    old_format_list = []
    new_format_list = []
    for _ in range(2000):
        patch = {p: rng.uniform(-1, 1) for p in gene_paths}
        m = _mutation(patch)
        sorted_patch = tuple((k, str(v)) for k, v in
                             sorted(patch.items(), key=lambda kv: kv[0]))
        old_format_list.append([list(pair) for pair in sorted_patch])
        new_format_list.append(Researcher.key(m))

    old_size = len(json.dumps(old_format_list))
    new_size = len(json.dumps(new_format_list))
    assert new_size * 20 < old_size


def test_patch_key_uses_sha256_of_the_sorted_repr():
    """Pins the exact hash construction so a future refactor that changes it
    is a deliberate, reviewed decision -- not an accident that silently
    invalidates every already-persisted hash in the live account."""
    items = (("a", "1"), ("b", "2"))
    expected = hashlib.sha256(repr(items).encode()).hexdigest()[:16]
    assert Researcher.patch_key(items) == expected
