"""The Jacobian conjecture, stated as a Hypothesis property — and falsified.

Conjecture (Keller, 1939): a polynomial map F: C^n -> C^n whose Jacobian
determinant is a nonzero constant is invertible (in particular, injective).

Our F has det J = -2, so the conjecture asserts every point of the image has
exactly one preimage. Hypothesis finds points where that fails.
"""

from fractions import Fraction

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from jc.fibers import distinct, fiber_certificate, preimages, verify_preimage
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


@given(points)
@fiber_settings
def jacobian_conjecture_says(p):
    """The property the conjecture asserts about F. It is false."""
    target = evaluate(p)
    fiber = preimages(target)
    assert distinct(fiber) <= 1, (
        f"Jacobian conjecture violated: det J = {jacobian_det()} is a nonzero "
        f"constant, yet F{p} = {target} has {distinct(fiber)} distinct "
        f"preimages: {fiber}"
    )


@pytest.mark.xfail(
    strict=True,
    reason="The Jacobian conjecture is false (Alpöge–Fable counterexample, 2026)",
)
def test_jacobian_conjecture():
    jacobian_conjecture_says()


def test_hypothesis_disproves_the_jacobian_conjecture():
    """Run the conjecture-property and demand that Hypothesis refute it."""
    with pytest.raises(AssertionError) as excinfo:
        jacobian_conjecture_says()
    print(f"\n{excinfo.value}\n")

    # The refutation must be witnessed by a genuine collision, not a solver
    # artifact: re-verify one falsifying fiber end to end, exactly, against
    # the quotient-ring dimension certificate.
    target = evaluate((1, 2, 3))
    fiber = preimages(target)
    assert fiber_certificate(target) == 3
    assert distinct(fiber) == 3
    assert all(verify_preimage(q, target) for q in fiber)
