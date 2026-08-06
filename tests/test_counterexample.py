"""Verify the counterexample map's credentials, exactly."""

from fractions import Fraction

from hypothesis import HealthCheck, assume, example, given, settings, strategies as st

from jc.fibers import (
    contains_exactly,
    distinct,
    fiber_certificate,
    is_generic,
    preimages,
    verify_preimage,
)
from jc.map import evaluate, jacobian_det

small_rationals = st.fractions(
    min_value=Fraction(-4), max_value=Fraction(4), max_denominator=3
)
points = st.tuples(small_rationals, small_rationals, small_rationals)

fiber_settings = settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)


def test_jacobian_determinant_is_constant_minus_two():
    """det J = -2 identically — F satisfies the conjecture's hypothesis."""
    assert jacobian_det() == -2


@given(points)
@example((1, 2, 3))
@fiber_settings
def test_fibers_are_complete_and_genuine(p):
    """The extracted roots exactly exhaust the quotient-ring dimension,
    contain the sampled point, and all map back to the target."""
    target = evaluate(p)
    fiber = preimages(target)
    certificate = fiber_certificate(target)
    assert len(fiber) == certificate  # completeness: no root lost or invented
    assert distinct(fiber) == certificate  # radical ideal: no repeats either
    assert contains_exactly(fiber, p)  # p itself found, exactly
    assert all(verify_preimage(q, target) for q in fiber)
    assert 1 <= certificate <= 3  # the 3-to-1 covering geometry caps fibers


@given(points)
@example((1, 2, 3))
@fiber_settings
def test_generic_fiber_has_exactly_three_points(p):
    """Where the eliminant certifies genericity (degree 3, squarefree),
    the fiber has exactly three distinct points — a solver that silently
    lost roots would fail here rather than be assumed away."""
    target = evaluate(p)
    assume(is_generic(target))
    fiber = preimages(target)
    assert fiber_certificate(target) == 3
    assert distinct(fiber) == 3
    assert all(verify_preimage(q, target) for q in fiber)


def test_taos_point_shows_f_is_not_proper():
    """Tao's digestion post highlights the fiber through (-1/4, 0, 0).

    Since det J = -2 vanishes nowhere, F is etale: sheets of the 3-to-1
    cover can never merge at a finite point. Yet this fiber has a single
    point — the other two preimages have escaped to infinity, and the
    eliminant's degree drop certifies that. Etale but not proper is
    precisely how the Jacobian conjecture fails.
    """
    p = (Fraction(-1, 4), 0, 0)
    target = evaluate(p)
    assert not is_generic(target)
    fiber = preimages(target)
    assert fiber_certificate(target) == 1
    assert distinct(fiber) == 1
    assert contains_exactly(fiber, p)
    assert all(verify_preimage(q, target) for q in fiber)
