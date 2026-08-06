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


def test_plane_stratum_sample_has_no_tame_map():
    """Dimension-2 parity evidence, sampled. (The exhaustive run over all
    16,384 plane maps with H of degree <= 3 found 160 unit-Jacobian maps
    with histogram {1: 10, 2: 54, 4: 48, 6: 48} — all automorphisms or
    wild; the slow test repeats it in full.)"""
    from jc import plane2

    units = plane2.det_unit_maps()
    assert len(units) == 160
    rng = random.Random(2026)
    for f1, f2 in rng.sample(units, 12):
        d = plane2.generic_degree(f1, f2)
        assert d is not None
        assert d == 1 or d % 2 == 0


@pytest.mark.slow
def test_plane_stratum_full_classification():
    from collections import Counter

    from jc import plane2

    hist = Counter()
    for f1, f2 in plane2.det_unit_maps():
        d = plane2.generic_degree(f1, f2)
        assert d is not None
        assert d == 1 or d % 2 == 0, f"tame counterexample?! {(f1, f2)} degree {d}"
        hist[d] += 1
    assert dict(hist) == {1: 10, 2: 54, 4: 48, 6: 48}


def test_plane_quadratic_unit_jacobian_forces_frobenius_affine():
    """The proved slice of the parity conjecture: in dimension 2 with H
    purely quadratic, char 2 kills every square's derivative, so
    det J = 1 + b*y + e*x — a unit iff the cross terms b, e vanish. The
    surviving maps are v -> v + M v^(2): additive group homomorphisms,
    whose generic degree is their kernel size, a power of 2."""
    import sympy as sp

    xx, yy, a, b, c, d, e, f = sp.symbols("x y a b c d e f")
    f1 = xx + a * xx**2 + b * xx * yy + c * yy**2
    f2 = yy + d * xx**2 + e * xx * yy + f * yy**2
    jac = sp.Matrix(
        [[sp.diff(f1, xx), sp.diff(f1, yy)], [sp.diff(f2, xx), sp.diff(f2, yy)]]
    )
    det = sp.Poly(sp.expand(jac.det()), xx, yy, a, b, c, d, e, f, modulus=2)
    assert det == sp.Poly(1 + b * yy + e * xx, xx, yy, a, b, c, d, e, f, modulus=2)


def test_3d_quadratic_det_units_are_classified_by_three_bits():
    """Solving det J = 1 symbolically over GF(2) for the full 18-coefficient
    quadratic family: square coefficients never appear (char 2 kills their
    derivatives), and the nine cross coefficients reduce to three free bits
    d = c0yz, e = c1xz, f = c2xy with c0xy = df, c2yz = df, c0xz = de,
    c1yz = de, c1xy = ef, c2xz = ef. Hence exactly 8 cross-patterns times
    2^9 free Frobenius parts = 4096 det-unit maps — matching the
    exhaustive enumeration."""
    import itertools as it

    import sympy as sp

    xx, yy, zz = sp.symbols("x y z")
    s = sp.symbols("s1:10")  # arbitrary Frobenius (square) coefficients
    count = 0
    for d, e, f in it.product((0, 1), repeat=3):
        h1 = d * (yy + e * xx) * (zz + f * xx) + s[0] * xx**2 + s[1] * yy**2 + s[2] * zz**2
        h2 = e * (xx + d * yy) * (zz + f * yy) + s[3] * xx**2 + s[4] * yy**2 + s[5] * zz**2
        h3 = f * (xx + d * zz) * (yy + e * zz) + s[6] * xx**2 + s[7] * yy**2 + s[8] * zz**2
        jac = sp.Matrix(
            [
                [sp.diff(g, v) for v in (xx, yy, zz)]
                for g in (xx + h1, yy + h2, zz + h3)
            ]
        )
        det = sp.Poly(sp.expand(jac.det()), xx, yy, zz, *s, modulus=2)
        assert det == sp.Poly(1, xx, yy, zz, *s, modulus=2), (d, e, f)
        count += 1
    assert count == 8
    # and 8 cross-patterns x 2^9 square choices = the enumerated 4096
    assert 8 * 2**9 == len(quadratic_det_units())


CUBIC_FREE = [
    [(0, 3, 0), (0, 0, 3), (2, 1, 0), (2, 0, 1), (0, 2, 1), (0, 1, 2)],
    [(3, 0, 0), (0, 0, 3), (2, 0, 1), (1, 2, 0), (1, 0, 2), (0, 2, 1)],
    [(3, 0, 0), (0, 3, 0), (2, 1, 0), (1, 2, 0), (1, 0, 2), (0, 1, 2)],
]


def cubic_block_det_units():
    """det-unit maps in the all-even-parity block of the cubic stratum
    (Hi cubic homogeneous, no xyz, no constrained monomials)."""
    subs = [
        [frozenset(c) for n in range(7) for c in itertools.combinations(pool, n)]
        for pool in CUBIC_FREE
    ]
    units = []
    for h1 in subs[0]:
        c1 = VARS[0] ^ h1
        for h2 in subs[1]:
            c2 = VARS[1] ^ h2
            for h3 in subs[2]:
                comps = (c1, c2, VARS[2] ^ h3)
                if det_j(comps) == ONE:
                    units.append(comps)
    return units


def test_cubic_stratum_block_counts_and_parity_sample():
    """Fast layer of the cubic-homogeneous theorem: the all-even-parity
    block holds 3004 of the stratum's 10,144 det-unit maps, and a seeded
    sample classifies to degree 1 or even."""
    units = cubic_block_det_units()
    assert len(units) == 3004
    rng = random.Random(2026)
    for comps in rng.sample(units, 16):
        d = generic_degree(comps)
        assert d is not None
        assert d == 1 or d % 2 == 0


def test_census_screen_finds_no_tame_pattern_in_quadratic_stratum():
    f4 = GF2k(2)
    for comps in quadratic_det_units():
        census = fiber_census(comps, f4)
        tame_looking = (
            census.get(3, 0) and not census.get(2, 0) and not census.get(4, 0)
        )
        assert not tame_looking