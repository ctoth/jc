"""Exhaustive stratum theorems for characteristic 2.

Theorem (quadratic stratum). Among all 262,144 maps (x+H1, y+H2, z+H3)
with Hi quadratic over F_2, exactly 4096 have det J = 1, and none is a
tame counterexample: every generic degree is 1 (automorphism) or even
(wild). Verified exhaustively; the full exact classification is the
slow test, a seeded sample runs by default.

Theorem (cubic-homogeneous stratum). Among all 2^30 maps with Hi cubic
homogeneous, det J = 1 forces e1 = e2 = e3 = 0; the e1-kernel (xyz
banned, three parity triples) has 16,777,216 maps, of which 10,144 have
det J = 1. The census and exact-degree layers found no tame
counterexample (see notes in the repository).
"""

import itertools
import random

import pytest

from jc.char2 import ONE, GF2k, det_j, fiber_census, generic_degree

QUAD = [(2, 0, 0), (0, 2, 0), (0, 0, 2), (1, 1, 0), (1, 0, 1), (0, 1, 1)]
VARS = (frozenset({(1, 0, 0)}), frozenset({(0, 1, 0)}), frozenset({(0, 0, 1)}))


def quadratic_det_units():
    subsets = [
        frozenset(c) for n in range(7) for c in itertools.combinations(QUAD, n)
    ]
    units = []
    for h1 in subsets:
        c1 = VARS[0] ^ h1
        for h2 in subsets:
            c2 = VARS[1] ^ h2
            for h3 in subsets:
                comps = (c1, c2, VARS[2] ^ h3)
                if det_j(comps) == ONE:
                    units.append(comps)
    return units


def test_quadratic_stratum_has_4096_unit_jacobian_maps():
    assert len(quadratic_det_units()) == 4096


def test_quadratic_stratum_sample_has_no_tame_map():
    """Seeded sample of the full classification: every generic degree is
    1 or even. (The exhaustive run over all 4096 maps found histogram
    {1: 176, 2: 728, 4: 1176, 6: 672, 8: 1344} — zero odd degrees >= 3 —
    and is repeatable via the slow test below.)"""
    units = quadratic_det_units()
    rng = random.Random(2026)
    for comps in rng.sample(units, 24):
        d = generic_degree(comps)
        assert d is not None
        assert d == 1 or d % 2 == 0


@pytest.mark.slow
def test_quadratic_stratum_full_classification():
    """The exhaustive theorem: all 4096 det-unit maps classified exactly."""
    from collections import Counter

    hist = Counter()
    for comps in quadratic_det_units():
        d = generic_degree(comps)
        assert d is not None
        assert d == 1 or d % 2 == 0, f"tame counterexample?! {comps} degree {d}"
        hist[d] += 1
    assert dict(hist) == {1: 176, 2: 728, 4: 1176, 6: 672, 8: 1344}


def test_census_screen_finds_no_tame_pattern_in_quadratic_stratum():
    f4 = GF2k(2)
    for comps in quadratic_det_units():
        census = fiber_census(comps, f4)
        tame_looking = (
            census.get(3, 0) and not census.get(2, 0) and not census.get(4, 0)
        )
        assert not tame_looking