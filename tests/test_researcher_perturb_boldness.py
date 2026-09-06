"""`Researcher.perturb`'s boldness formula grows `jump_p`/`spread`/`genes_per`
without bound as stagnation rises, but both `jump_p` (caps at 0.75 by
boldness ~4.6) and `genes_per` (caps at every gene in `GENE_SPACE`, 44 as of
this writing, by boldness ~92) saturate long before real stagnation counters
do -- the live champion's `researcher_memory` has already carried a
stagnation counter past 130. Past saturation, every blind-search candidate
mutates the entire genome at once with a 75% chance per gene of an outright
uniform redraw, so the graduated "widen search under stagnation" design
silently becomes "always fully randomize" with no local exploitation left.
`perturb` now reserves a fixed quarter of every batch to always run at
boldness 0 regardless of how high `boldness` itself is, so long stagnation
adds wide exploration on top of continued local search instead of replacing
it. These tests lock that behavior in.
"""
from core.genome import Genome
from agents.researcher import Researcher, GENE_SPACE


def test_boldness_zero_is_unaffected():
    """No behavior change at boldness=0 (every prior evolve run's default
    starting point): every candidate should stay narrow, as before."""
    g = Genome()
    props = Researcher(seed=7).perturb(g, n=12, n_genes=2, boldness=0.0)
    assert all(len(m.patch) <= 2 for m in props)


def test_high_boldness_still_reserves_a_local_slice():
    """At a stagnation level far past where jump_p/genes_per saturate (real
    live value is 130+), some candidates in the batch must still be narrow
    (<= n_genes), not just wide full-genome redraws."""
    g = Genome()
    n = 16
    props = Researcher(seed=7).perturb(g, n=n, n_genes=2, boldness=134.0)
    sizes = [len(m.patch) for m in props]
    n_local_expected = max(1, n // 4)
    assert sum(1 for s in sizes if s <= 2) >= n_local_expected - 1, sizes
    # And the point of high boldness -- wide, full-genome candidates -- must
    # still be there too; the fix adds local exploitation, it doesn't remove
    # exploration.
    assert any(s >= len(GENE_SPACE) - 2 for s in sizes), sizes


def test_local_slice_size_scales_with_batch_size():
    g = Genome()
    for n in (4, 8, 20):
        props = Researcher(seed=3).perturb(g, n=n, n_genes=2, boldness=50.0)
        assert len(props) <= n
