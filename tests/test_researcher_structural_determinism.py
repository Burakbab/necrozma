"""Locks in a property `Researcher.propose`'s own docstring already claims but
nothing tested directly: `from_diagnosis` and `structural` are driven purely by
the champion genome and the diagnostics dict, never by `self.rng`, so they
return the identical proposal set regardless of RNG seed. Only `perturb`
(blind search) varies with the seed.

This matters beyond the docstring: the 2026-09-02/09-03 4h-shadow-evolution
thread (AGENTS.md item 2) ran five *fresh* `EvolutionRun`s (seeds
9101/9102/9104/9105, each starting from an empty `researcher_memory`) against
the same unpatched `x6` seed champion, and generation 1 of three of them
produced what run notes called "the exact same candidate" (a `remove_agent`
patch disabling `consult_moderate`) clearing the fold gate with identical
fold fitness to four decimal places. That was read as suggestive, not
confirmed, evidence that the recurrence was structural rather than a
genuinely fresh independent finding. It is exactly `structural()`'s
documented behavior: given the same starting champion, `structural()`
proposes `remove_agent` for `consult_moderate` on every call regardless of
seed, so a fresh `EvolutionRun` (empty exclude set) is *guaranteed*, not
merely likely, to re-propose it at generation 1 -- three "independent"
fold-clears of the same candidate are one deterministic proposal recurring
by construction, not three separate discoveries.
"""
from core.genome import Genome
from agents.researcher import Researcher

# Diagnostics dict shaped to trigger none of from_diagnosis's own conditions,
# so the test isolates structural()'s contribution to propose()'s determinism
# from from_diagnosis's (also-deterministic, but separately reasoned) one.
_NEUTRAL_DIAGNOSTICS = {
    "stop_share": 0.0,
    "stop_pnl": 0.0,
    "time_share": 0.0,
    "pnl_by_entry": {},
    "n_by_entry": {},
    "superior_overrides": 0,
    "trades": 100,
    "halt_count": 0,
}


def _keys(mutations):
    return {Researcher.key(m) for m in mutations}


def test_structural_is_independent_of_rng_seed():
    g = Genome()
    proposals_a = Researcher(seed=1).structural(g)
    proposals_b = Researcher(seed=999999).structural(g)
    assert _keys(proposals_a) == _keys(proposals_b)
    assert [m.patch for m in proposals_a] == [m.patch for m in proposals_b]


def test_structural_always_proposes_removing_each_enabled_consult():
    g = Genome()
    proposals = Researcher(seed=42).structural(g)
    removed = {m.target for m in proposals if m.kind == "remove_agent"}
    assert removed == {"consult_risky", "consult_moderate", "consult_conservative"}


def test_from_diagnosis_is_independent_of_rng_seed():
    g = Genome()
    proposals_a = Researcher(seed=1).from_diagnosis(g, _NEUTRAL_DIAGNOSTICS)
    proposals_b = Researcher(seed=999999).from_diagnosis(g, _NEUTRAL_DIAGNOSTICS)
    assert _keys(proposals_a) == _keys(proposals_b)


def test_propose_non_blind_proposals_are_seed_independent_only_perturb_varies():
    g = Genome()
    props_a = Researcher(seed=1).propose(g, _NEUTRAL_DIAGNOSTICS, n_blind=10)
    props_b = Researcher(seed=2).propose(g, _NEUTRAL_DIAGNOSTICS, n_blind=10)

    non_blind_a = {Researcher.key(m) for m in props_a
                   if m.kind in ("remove_agent", "add_agent") or "blind search" not in m.hypothesis}
    non_blind_b = {Researcher.key(m) for m in props_b
                   if m.kind in ("remove_agent", "add_agent") or "blind search" not in m.hypothesis}
    assert non_blind_a == non_blind_b

    blind_a = {Researcher.key(m) for m in props_a if "blind search" in m.hypothesis}
    blind_b = {Researcher.key(m) for m in props_b if "blind search" in m.hypothesis}
    assert blind_a != blind_b, "different seeds should draw different blind-search proposals"


def test_fresh_run_always_reproposes_remove_consult_moderate_at_generation_one():
    """The specific recurring candidate from the shadow-4h thread: with no
    exclude set (a brand-new EvolutionRun/researcher_memory, as every fresh
    shadow seed used), removing consult_moderate is proposed every time,
    regardless of seed -- confirming it is not a coincidence that seeds
    9102/9104/9105 all hit it at generation 1."""
    g = Genome()
    for seed in (9102, 9104, 9105, 1234):
        proposals = Researcher(seed=seed).propose(g, _NEUTRAL_DIAGNOSTICS, n_blind=6, exclude=None)
        keys = {Researcher.key(m): m for m in proposals}
        remove_moderate = [m for m in proposals
                            if m.kind == "remove_agent" and m.target == "consult_moderate"]
        assert len(remove_moderate) == 1
        assert remove_moderate[0].patch == {"agents.consult_moderate.enabled": False}


def test_exclude_set_removes_the_repeat_candidate():
    """This is the actual fix already in the codebase (propose()'s docstring):
    once a proposal's key is in `exclude`, it stops recurring. Confirms the
    thread's five fresh-seed sessions could have avoided re-testing the same
    candidate by carrying `researcher_memory`/exclude forward across seeds
    instead of starting each shadow session from an empty one."""
    g = Genome()
    r = Researcher(seed=9106)
    baseline = r.propose(g, _NEUTRAL_DIAGNOSTICS, n_blind=0)
    remove_moderate_key = next(
        Researcher.key(m) for m in baseline
        if m.kind == "remove_agent" and m.target == "consult_moderate"
    )

    excluded = r.propose(g, _NEUTRAL_DIAGNOSTICS, n_blind=0, exclude={remove_moderate_key})
    assert remove_moderate_key not in {Researcher.key(m) for m in excluded}
    assert len(excluded) == len(baseline) - 1
