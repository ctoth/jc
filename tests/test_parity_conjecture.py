"""Where the parity pattern holds — and where it broke.

This project first conjectured: over F_2, every unit-Jacobian polynomial
self-map of A^3 has generic degree 1 or even. The conjecture was TRUE
across every Bass–Connell–Wright stratum tested (exhaustively — see
test_strata.py) and 400k+ random BCW samples, and then did its real job:
it aimed the search at the z-linear Sym-mirror family, where it is FALSE
— jc.unicorn refutes it, and with it the tame Jacobian problem in
characteristic 2 (see test_unicorn.py).

This property is kept as a standing observation on the BCW-form region,
where parity empirically holds; a failure here would be a second, BCW-
form counterexample, which would be independently interesting.
"""

from hypothesis import HealthCheck, assume, given, settings, strategies as st

from jc.char2 import H_POOL, ONE, _VARS, det_j, generic_degree

component_h = st.lists(
    st.sampled_from(sorted(H_POOL)), min_size=0, max_size=2, unique=True
)


@given(component_h, component_h, component_h)
@settings(
    max_examples=30,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
)
def test_parity_holds_in_the_bcw_form_region(h1, h2, h3):
    comps = tuple(v ^ frozenset(h) for v, h in zip(_VARS, (h1, h2, h3)))
    assume(det_j(comps) == ONE)
    d = generic_degree(comps)
    assert d is not None
    assert d == 1 or d % 2 == 0, (
        f"BCW-form tame counterexample?! {comps} degree {d} — "
        "a second unicorn, in the region where parity held"
    )