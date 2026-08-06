"""Characteristic-p behaviour of the counterexample, and the char-2 finder."""

from collections import Counter

from jc.char2 import (
    GF2k,
    ONE,
    det_j,
    generic_degree,
    fiber_census,
    is_injective_census,
    search,
    tame_score,
)
from jc.charp import det_j_mod, evaluate_mod, sqrt_minus_one, witness_mod


def test_det_j_vanishes_mod_2():
    """-2 = 0 in F_2: the map is not even a Jacobian candidate there."""
    assert det_j_mod(2) == 0


def test_det_j_is_a_unit_mod_odd_primes():
    for p in (3, 5, 7, 11, 13):
        # sympy's modulus= uses the symmetric representative, so reduce again
        assert det_j_mod(p).is_number and det_j_mod(p) % p == (-2) % p


def test_witness_collision_survives_mod_5():
    """i = sqrt(-1) exists mod 5, so the Gaussian witness reduces: the map
    refutes injectivity over F_5 as well."""
    p1, p2 = witness_mod(5)
    assert p1 != p2
    assert evaluate_mod(p1, 5) == evaluate_mod(p2, 5) == (1, 0, 0)


def test_witness_collision_mod_13():
    p1, p2 = witness_mod(13)
    assert p1 != p2
    assert evaluate_mod(p1, 13) == evaluate_mod(p2, 13)


def test_sqrt_minus_one():
    for p in (5, 13, 17, 29):
        i = sqrt_minus_one(p)
        assert (i * i) % p == p - 1


def test_map_is_generically_three_to_one_mod_5():
    """Rational fiber sizes over F_5^3 behave like a degree-3 cover:
    size 3 occurs, and no fiber exceeds 3."""
    images = Counter()
    for a in range(5):
        for b in range(5):
            for c in range(5):
                images[evaluate_mod((a, b, c), 5)] += 1
    sizes = Counter(images.values())
    assert sizes.get(3, 0) > 0
    assert max(sizes) == 3


# --- char-2 machinery ------------------------------------------------------


def test_gf4_multiplication():
    f = GF2k(2)
    # x * x = x + 1 mod x^2 + x + 1: 2 * 2 = 3
    assert f.mul_table[2][2] == 3
    assert f.mul_table[3][3] == 2
    for a in range(1, 4):
        assert sorted(f.mul_table[a][b] for b in range(4)) == [0, 1, 2, 3]


def test_det_j_of_artin_schreier_is_one():
    x2x = frozenset({(2, 0, 0), (1, 0, 0)})
    y_ = frozenset({(0, 1, 0)})
    z_ = frozenset({(0, 0, 1)})
    assert det_j((x2x, y_, z_)) == ONE


def test_artin_schreier_is_wild_not_tame():
    """The classic char-2 non-injective unit-Jacobian map must be caught
    as wild (fibers of size 2), scoring zero on tameness."""
    x2x = frozenset({(2, 0, 0), (1, 0, 0)})
    y_ = frozenset({(0, 1, 0)})
    z_ = frozenset({(0, 0, 1)})
    census = fiber_census((x2x, y_, z_), GF2k(2))
    assert not is_injective_census(census)
    assert set(census) == {2}
    assert tame_score(census) == 0.0


def test_identity_map_census_is_injective():
    comps = (
        frozenset({(1, 0, 0)}),
        frozenset({(0, 1, 0)}),
        frozenset({(0, 0, 1)}),
    )
    assert det_j(comps) == ONE
    assert is_injective_census(fiber_census(comps, GF2k(2)))


def test_census_camouflage_is_unmasked_by_the_symbolic_stage():
    """The first candidate this search ever flagged: rational fibers of
    sizes {1, 3} only over F_8 — tame-looking — yet a wild 8-to-1 cover.
    The exact generic degree (Groebner over GF(2)(A,B,C)) must say so."""
    comps = (
        frozenset({(1, 0, 0), (2, 0, 0)}),
        frozenset({(0, 1, 0), (0, 2, 0), (1, 0, 2), (2, 0, 0)}),
        frozenset({(0, 0, 1), (1, 0, 2), (1, 2, 0)}),
    )
    assert det_j(comps) == ONE
    census = fiber_census(comps, GF2k(3))
    assert set(census) == {1, 3}
    assert tame_score(census) > 0  # the census alone is fooled
    assert generic_degree(comps) == 8  # ... the function-field count is not


def test_generic_degree_is_char_2_not_char_0():
    """F = (x + y^2, y + xz + xy, z + xz + xy) has det J = 1 and generic
    degree 3 in characteristic 0 — but in char 2 the cross terms of the
    last two components cancel (F2 + F3 = y + z), reducing the fiber to a
    quadratic in x: degree 2, wild. A tool that leaks characteristic 0
    reports 3 and hallucinates a tame counterexample here."""
    comps = (
        frozenset({(1, 0, 0), (0, 2, 0)}),
        frozenset({(0, 1, 0), (1, 0, 1), (1, 1, 0)}),
        frozenset({(0, 0, 1), (1, 0, 1), (1, 1, 0)}),
    )
    assert det_j(comps) == ONE
    assert generic_degree(comps) == 2


def test_generic_degree_on_known_maps():
    a_s = (
        frozenset({(2, 0, 0), (1, 0, 0)}),
        frozenset({(0, 1, 0)}),
        frozenset({(0, 0, 1)}),
    )
    assert generic_degree(a_s) == 2  # wild, as the classic example must be
    identity = (
        frozenset({(1, 0, 0)}),
        frozenset({(0, 1, 0)}),
        frozenset({(0, 0, 1)}),
    )
    assert generic_degree(identity) == 1


def test_search_runs_and_reports():
    flagged, stats = search(200, seed=42)
    assert stats.get("det_rejected", 0) + stats.get("det_unit", 0) == 200
    for comps, _screen, confirm, score in flagged:
        assert det_j(comps) == ONE
        assert score == tame_score(confirm)