"""One-time migration for AGENTS.md item 12: shrink `live_state.json`'s
`researcher_memory["tested"]` from full gene patches to the 16-hex-char
hashes `agents.researcher.Researcher.key()` now uses as a candidate's
identity.

Every `evolve`-family command already migrates a mixed old/new `tested` list
on read (`Researcher.migrate_tested_entry`) and persists only hashes on
write, so this script is not required for correctness -- the next real
`evolve` invocation does it automatically. It exists to apply the shrink
immediately (57.2MB -> ~28MB measured on the live account 2026-09-16) instead
of waiting out however many more 3-hourly cycles until the next evolve batch,
and to leave a record of exactly how the migration was verified.

Idempotent: a `tested` list that is already all-hashes round-trips unchanged
(`migrate_tested_entry` is the identity on a string entry).

Usage: python3 tools/migrate_tested_memory.py [path-to-live_state.json]
"""
from __future__ import annotations

import json
import sys

sys.path.insert(0, __file__.rsplit("/tools/", 1)[0])

from agents.researcher import Researcher
from core.live import LiveAccount


def migrate(path: str = "live_state.json") -> None:
    with open(path) as f:
        before_raw = json.load(f)

    acct = LiveAccount.load(path)
    mem = dict(acct.researcher_memory or {})
    tested = mem.get("tested", [])
    n_before = len(tested)
    old_json_bytes = len(json.dumps(tested))

    migrated = sorted({Researcher.migrate_tested_entry(e) for e in tested})
    n_after = len(migrated)
    new_json_bytes = len(json.dumps(migrated))

    if n_after != n_before:
        raise SystemExit(
            f"REFUSING to save: migration changed candidate count "
            f"{n_before} -> {n_after} (expected no membership change, "
            f"same-patch hash collisions or a bug). Not touching {path}.")

    mem["tested"] = migrated
    acct.researcher_memory = mem
    acct.save(path)

    with open(path) as f:
        after_raw = json.load(f)
    changed_keys = {k for k in set(before_raw) | set(after_raw)
                    if before_raw.get(k) != after_raw.get(k)}
    unexpected = changed_keys - {"researcher_memory", "updated"}
    if unexpected:
        raise SystemExit(
            f"REFUSING: unexpected top-level keys changed besides "
            f"researcher_memory/updated: {unexpected}. Investigate before "
            f"trusting this save.")

    print(f"[migrate-tested-memory] {path}: tested {n_before} -> {n_after} entries "
          f"(membership unchanged), {old_json_bytes:,} -> {new_json_bytes:,} bytes "
          f"({old_json_bytes / max(new_json_bytes, 1):.1f}x smaller)")


if __name__ == "__main__":
    migrate(sys.argv[1] if len(sys.argv) > 1 else "live_state.json")
