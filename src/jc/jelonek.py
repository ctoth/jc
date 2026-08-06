"""The non-properness (Jelonek) locus of the counterexample map, symbolically.

F is etale (det J = -2), so fibers can only shrink below the generic count
of 3 by preimages escaping to infinity. This module computes where, as
polynomial conditions on the *target* (A, B, C):

Eliminating z (all components are linear in it) and then y yields

    R_x(x) = -C * x^9 * G(x),      G(x) = D*x^3 + (4 - 3*B*C)*x - 2*C,

with D = 27*A^2*C^2 - 18*A*B*C + 16*A + B^3*C - B^2. The x-coordinates of
the fiber over (A, B, C) are roots of the cubic G (the -C * x^9 prefactor
is an artifact of clearing the x^3 denominator), so a preimage escapes in
the x-direction exactly when the degree of G drops: on {D = 0}. The
y-eliminant has leading coefficient -2*C^2, so escape in the y-direction
requires C = 0; and with x, y bounded, z = (2x - 3x^2 y - C)/x^3 is bounded
too. Hence fibers of fewer than 3 points only occur on {D * C = 0}.

The locus {D = 0} contains the rational family (A, B, C) = (-16/(27 c^2), 0, c),
which the tests sample directly.
"""

from functools import lru_cache

import sympy as sp

from jc.map import F, x, y, z

A, B, C = sp.symbols("A B C")

#: Degree-drop polynomial for the x-eliminant: escapes in x live on {D = 0}.
D = sp.expand(
    27 * A**2 * C**2 - 18 * A * B * C + 16 * A + B**3 * C - B**2
)

#: The fiber cubic: x-coordinates of F^{-1}(A, B, C) are its roots.
fiber_cubic = sp.Poly(D * x**3 + (4 - 3 * B * C) * x - 2 * C, x)


@lru_cache(maxsize=1)
def _eliminants():
    """Recompute both eliminants from the map itself (no hardcoding)."""
    a, b, c = F
    zsol = sp.solve(sp.Eq(c, C), z)[0]
    p1 = sp.expand(sp.numer(sp.together((a - A).subs(z, zsol))))
    p2 = sp.expand(sp.numer(sp.together((b - B).subs(z, zsol))))
    r_x = sp.expand(sp.resultant(p1, p2, y))
    r_y = sp.expand(sp.resultant(p1, p2, x))
    return r_x, r_y


def x_eliminant():
    return _eliminants()[0]


def y_eliminant():
    return _eliminants()[1]


def d_at(target):
    """D evaluated at a concrete target, exactly."""
    t = [sp.nsimplify(v) for v in target]
    return D.subs({A: t[0], B: t[1], C: t[2]})


def may_be_improper(target):
    """True when `target` satisfies the necessary condition D*C = 0 for a
    fiber of fewer than 3 points. False guarantees the fiber is full."""
    t = [sp.nsimplify(v) for v in target]
    return d_at(target) == 0 or t[2] == 0


def on_locus_family(c_value):
    """A rational point of {D = 0} for any rational c != 0: the B = 0 slice
    reduces D to 27*A^2*C^2 + 16*A, solved by A = -16/(27 c^2)."""
    c_value = sp.nsimplify(c_value)
    if c_value == 0:
        raise ValueError("the family needs c != 0")
    return (sp.Rational(-16) / (27 * c_value**2), sp.Integer(0), c_value)
