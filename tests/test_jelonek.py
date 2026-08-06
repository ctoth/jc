"""The non-properness locus: where and only where fibers lose points."""

from fractions import Fraction

import sympy as sp
from hypothesis import HealthCheck, assume, example, given, settings, strategies as st

from jc.fibers import fiber_certificate
from jc.jelonek import A, B, C, D, fiber_cubic, may_be_improper, on_locus_family, x_eliminant, y_eliminant
from jc.map import evaluate, x

small_rationals = st.fractions(
    min_value=Fraction(-4), max_value=Fraction(4), max_denominator=3
)
targets = st.tuples(small_rationals, small_rationals, small_rationals)

fiber_settings = settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)


def test_eliminant_structure():
    """The x-eliminant recomputed from the map factors as -C * x^9 * G,
    and the y-eliminant has leading coefficient -2*C^2."""
    g = fiber_cubic.as_expr()
    assert sp.expand(x_eliminant() - (-C) * x**9 * g) == 0
    y_lead = sp.Poly(y_eliminant(), sp.Symbol("y")).LC()
    assert sp.expand(y_lead + 2 * C**2) == 0


def test_fiber_cubic_degree_drop_is_exactly_d():
    assert fiber_cubic.LC() == D


@given(targets)
@example((1, 1, 1))
@fiber_settings
def test_off_locus_fibers_are_full(t):
    """D*C != 0 guarantees three preimages — over arbitrary rational
    targets, not just images of sampled points."""
    assume(not may_be_improper(t))
    assert fiber_certificate(t) == 3


@given(targets)
@fiber_settings
def test_small_fibers_only_on_the_locus(t):
    """Contrapositive, sampled independently: a fiber below 3 points
    forces D*C = 0."""
    if fiber_certificate(t) < 3:
        assert may_be_improper(t)


@given(small_rationals)
@example(Fraction(1))
@fiber_settings
def test_on_locus_family_loses_preimages(c_value):
    """Along the rational family (-16/(27c^2), 0, c) inside {D = 0},
    at least one preimage has escaped to infinity."""
    assume(c_value != 0)
    t = on_locus_family(c_value)
    assert sp.simplify(D.subs({A: t[0], B: t[1], C: t[2]})) == 0
    assert fiber_certificate(t) < 3


def test_taos_target_is_on_the_locus():
    """F(-1/4, 0, 0) = (0, 0, -1/2): the very point where we first saw a
    fiber collapse sits on {D = 0}."""
    t = evaluate((sp.Rational(-1, 4), 0, 0))
    assert t == (0, 0, sp.Rational(-1, 2))
    assert may_be_improper(t)
    assert fiber_certificate(t) == 1
