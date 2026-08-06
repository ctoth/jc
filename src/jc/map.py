"""The Alpöge–Fable counterexample to the Jacobian conjecture (announced 2026-07-20).

F: C^3 -> C^3, F(x, y, z) = (a, b, c) with constant Jacobian determinant -2,
yet generically 3-to-1. Geometrically it factors through
P^1 x Sym^2(P^1) -> Sym^3(P^1): a point (linear factor, quadratic factor)
maps to the product cubic, and a generic cubic has three such factorizations.
"""

import sympy as sp

x, y, z = sp.symbols("x y z")

a = (1 + x * y) ** 3 * z + y**2 * (1 + x * y) * (4 + 3 * x * y)
b = y + 3 * x * (1 + x * y) ** 2 * z + 3 * x * y**2 * (4 + 3 * x * y)
c = 2 * x - 3 * x**2 * y - x**3 * z

F = (a, b, c)

JACOBIAN = sp.Matrix([[sp.diff(comp, v) for v in (x, y, z)] for comp in F])


def jacobian_det():
    """The Jacobian determinant of F as a fully expanded polynomial."""
    return sp.expand(JACOBIAN.det())


def evaluate(point):
    """Evaluate F at a point, exactly (accepts ints/Fractions/sympy Rationals)."""
    subs = {x: sp.nsimplify(point[0]), y: sp.nsimplify(point[1]), z: sp.nsimplify(point[2])}
    return tuple(sp.expand(comp.subs(subs)) for comp in F)
