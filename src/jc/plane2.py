"""Plane (n = 2) analogues of the char-2 machinery, for parity evidence.

The Parity Conjecture this project formulates: in characteristic 2 every
polynomial self-map of affine n-space with det J = 1 has generic degree
1 or even — so Adjamagbo's tame Jacobian problem is vacuously true for
p = 2. In dimension 1 this is elementary (f' = 1 forces f = x + g(x^2),
of even degree unless linear). This module supplies the dimension-2
evidence: exhaustive classification of the stratum (x + H1, y + H2)
with Hi spanned by the degree-2 and degree-3 monomials.
"""

import itertools

import sympy as sp

x, y, A, B = sp.symbols("x y A B")

#: Monomials available to H1 and H2.
POOL = (x**2, x * y, y**2, x**3, x**2 * y, x * y**2, y**3)

_DOM = sp.GF(2).frac_field(A, B)


def det_j(f1, f2):
    """det of the Jacobian over GF(2), exact."""
    jac = sp.Matrix(
        [[sp.diff(f1, x), sp.diff(f1, y)], [sp.diff(f2, x), sp.diff(f2, y)]]
    )
    return sp.Poly(sp.expand(jac.det()), x, y, modulus=2).as_expr()


def generic_degree(f1, f2):
    """Exact generic degree over F_2-bar, via the Groebner staircase over
    GF(2)(A, B). The domain goes to groebner directly (see jc.char2)."""
    basis = sp.groebner([f1 - A, f2 - B], x, y, order="grevlex", domain=_DOM)
    lead = [sp.Poly(g, x, y).monoms(order="grevlex")[0] for g in basis.polys]
    bound = []
    for i in range(2):
        powers = [e[i] for e in lead if all(v == 0 for j, v in enumerate(e) if j != i)]
        if not powers:
            return None
        bound.append(min(powers))
    return sum(
        1
        for i in range(bound[0])
        for j in range(bound[1])
        if not any(li <= i and lj <= j for (li, lj) in lead)
    )


def det_unit_maps():
    """All maps of the stratum with det J = 1 (160 of 16,384)."""
    subs = [sum(c) for n in range(8) for c in itertools.combinations(POOL, n)]
    units = []
    for h1 in subs:
        f1 = x + h1
        for h2 in subs:
            f2 = y + h2
            if det_j(f1, f2) == 1:
                units.append((f1, f2))
    return units
