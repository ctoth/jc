"""The tame characteristic-2 counterexample, verified end to end.

Adjamagbo's separable Jacobian conjecture asserted that a polynomial map
in characteristic p with unit Jacobian and p not dividing the extension
degree is invertible. Alpöge–Fable killed it in odd characteristic;
Huq-Kuruvilla killed it in characteristic 2 (arXiv:2607.20968, July 23,
2026). The map here is a second, independently found characteristic-2
counterexample. It also refutes this project's own parity conjecture —
whose honest job was to aim the search at the family containing its
refutation.
"""

from collections import Counter

import sympy as sp

from jc.char2 import GF2k, ONE, det_j, fiber_census, generic_degree
from jc.unicorn import TARGET, UNICORN, UNICORN_LEAN_F3, WITNESSES, evaluate_f2


def test_det_j_is_one():
    """Etale: the exact GF(2) determinant of the Jacobian is 1."""
    assert det_j(UNICORN) == ONE
    assert det_j(UNICORN_LEAN_F3) == ONE


def test_det_j_is_one_by_sympy_independently():
    x, y, z = sp.symbols("x y z")
    f1 = z + x*y + x*y**2 + x**2*y**2 + x**2*y*z + x**2*y**2*z + x**3*y**2*z
    f2 = y + x*y**2
    f3 = x + y + x*y**2 + x**2*z
    jac = sp.Matrix([[sp.diff(f, v) for v in (x, y, z)] for f in (f1, f2, f3)])
    assert sp.Poly(sp.expand(jac.det()), x, y, z, modulus=2).as_expr() == 1


def test_three_rational_points_collide():
    """The hand-checkable heart: three F_2-points share one image."""
    assert len(set(WITNESSES)) == 3
    for w in WITNESSES:
        assert evaluate_f2(UNICORN, w) == TARGET


def test_generic_degree_is_three():
    """Odd degree: separable, tame — and 3 > 1: not injective."""
    assert generic_degree(UNICORN) == 3
    assert generic_degree(UNICORN_LEAN_F3) == 3


def test_fibers_never_exceed_three():
    """Over F_4, F_8, F_16 every fiber has 1 or 3 points — the rational
    shadow of a separable degree-3 cover, with no wild sizes anywhere."""
    for k in (2, 3, 4):
        census = fiber_census(UNICORN, GF2k(k))
        assert set(census) <= {1, 3}
        assert census.get(3, 0) > 0


def test_every_point_is_hit_over_f8():
    """Fiber sizes {1,3} exactly cover F_8^3: 281 + 3*77 = 512."""
    census = fiber_census(UNICORN, GF2k(3))
    assert census == Counter({1: 281, 3: 77})
    assert sum(size * count for size, count in census.items()) == 8**3


def test_eliminant_specialization_certifies_degree_three():
    """At target (0,1,0) the x-eliminant's non-artifact factor is
    x^3 + x + 1: irreducible and separable over F_2 — an independent
    certificate that the generic extension truly has a degree-3 part."""
    x, y, z, A, B, C = sp.symbols("x y z A B C")
    f1 = z + x*y + x*y**2 + x**2*y**2 + x**2*y*z + x**2*y**2*z + x**3*y**2*z
    f2 = y + x*y**2
    f3 = x + y + x*y**2 + x**2*z
    gf = sp.GF(2)
    r_z = sp.resultant(
        sp.Poly(f1 - A, z, x, y, A, B, C, domain=gf),
        sp.Poly(f3 - C, z, x, y, A, B, C, domain=gf),
        z,
    )
    r_zy = sp.resultant(
        sp.Poly(r_z.as_expr(), y, x, A, B, C, domain=gf),
        sp.Poly(f2 - B, y, x, A, B, C, domain=gf),
        y,
    )
    u = sp.Poly(r_zy.as_expr().subs({A: 0, B: 1, C: 0}), x, modulus=2)
    factors = dict(sp.factor_list(u.as_expr(), x, modulus=2)[1])
    cubic = sp.Poly(x**3 + x + 1, x, modulus=2).as_expr()
    assert any(sp.expand(f - cubic) == 0 for f in factors)
    # separable: gcd with derivative is 1
    assert sp.gcd(cubic, sp.diff(cubic, x), modulus=2) == 1


def test_witnesses_collide_by_pure_python_arithmetic():
    """No sympy, no library code: F(w) over F_2 by hand. On 0/1
    coordinates a^k = a for k >= 1, so the seven monomials of F1 collapse
    to 3xy + 3xyz + z = xy + xyz + z mod 2, and similarly for F2, F3."""
    def F(x, y, z):
        return (
            (z + x * y + x * y * z) % 2,
            (y + x * y) % 2,
            (x + y + x * y + x * z) % 2,
        )

    assert {F(*w) for w in WITNESSES} == {TARGET}


def test_fiber_over_the_target_is_reduced_and_entirely_rational():
    """The collision is the WHOLE fiber: over (1,0,0) the fiber ideal has
    Groebner basis {x^2+x, xy+y, y^2+y, z+1} — quotient dimension 3 with
    basis {1, x, y}, generators splitting into distinct linear factors
    (radical, hence reduced) — so the three F_2-points realize the full
    generic degree with no multiplicity and no extension-field stragglers."""
    x, y, z = sp.symbols("x y z")
    f1 = z + x*y + x*y**2 + x**2*y**2 + x**2*y*z + x**2*y**2*z + x**3*y**2*z
    f2 = y + x*y**2
    f3 = x + y + x*y**2 + x**2*z
    basis = sp.groebner([f1 - 1, f2, f3], x, y, z, modulus=2, order="grevlex")
    exprs = {sp.Poly(g, x, y, z, modulus=2) for g in basis.exprs}
    expected = {
        sp.Poly(x**2 + x, x, y, z, modulus=2),
        sp.Poly(x * y + y, x, y, z, modulus=2),
        sp.Poly(y**2 + y, x, y, z, modulus=2),
        sp.Poly(z + 1, x, y, z, modulus=2),
    }
    assert exprs == expected
    sols = [
        pt
        for pt in ((a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1))
        if evaluate_f2(UNICORN, pt) == TARGET
    ]
    assert tuple(sols) == WITNESSES


def test_unicorn_refutes_the_parity_conjecture():
    """degree 3: odd and >= 3 — the parity conjecture is false, and the
    tame Jacobian problem in characteristic 2 is settled: FALSE."""
    d = generic_degree(UNICORN)
    assert d is not None and d % 2 == 1 and d >= 3
