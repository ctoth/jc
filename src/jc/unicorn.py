"""The tame characteristic-2 counterexample (the unicorn), August 2026.

    F1 = z + xy + xy^2 + x^2y^2 + x^2yz + x^2y^2z + x^3y^2z
    F2 = y + xy^2                                  = y(1 + xy)
    F3 = x + y + xy^2 + x^2z

over F_2. Its Jacobian determinant is identically 1 (the map is etale),
its generic degree is 3 — odd, so the inseparable degree (a power of 2
dividing 3) is 1: the extension is separable — and it is not injective:
the three F_2-rational points (0,0,1), (1,0,1), (1,1,1) all map to
(1,0,0), and they are the entire (reduced) fiber. A second
counterexample to Adjamagbo's separable Jacobian conjecture in
characteristic 2: the theorem is due to Huq-Kuruvilla (arXiv:2607.20968,
July 23, 2026, via the simpler map (x+x^2y, y+xz+x^2yz, z+x^2z^2));
this map was found independently, before we learned of that paper. It
also refutes this project's parity conjecture — which earned its keep by
pointing the search at the z-linear Sym-mirror family where this map
lives. Found by SAT-sweeping det J = 1 over that family and sieving
fiber censuses; verified by sympy determinants, brute censuses over
F_8..F_64 (fiber sizes always in {1, 3}), function-field Groebner degree
(the proof), and a corroborating irreducible separable cubic eliminant
specialization (x^3 + x + 1 at target (0,1,0)).
"""

UNICORN = (
    frozenset({(0, 0, 1), (1, 1, 0), (1, 2, 0), (2, 2, 0), (2, 1, 1), (2, 2, 1), (3, 2, 1)}),
    frozenset({(0, 1, 0), (1, 2, 0)}),
    frozenset({(1, 0, 0), (0, 1, 0), (1, 2, 0), (2, 0, 1)}),
)

#: The F_2-rational witness collision: all three map to (1, 0, 0).
WITNESSES = ((0, 0, 1), (1, 0, 1), (1, 1, 1))
TARGET = (1, 0, 0)

#: A cleaner Frobenius-variant with F3 = x + x^2 z (same base family).
UNICORN_LEAN_F3 = (
    UNICORN[0],
    UNICORN[1],
    frozenset({(1, 0, 0), (2, 0, 1)}),
)


def evaluate_f2(comps, point):
    """Evaluate a monomial-set map at a point of F_2^3."""
    out = []
    for comp in comps:
        acc = 0
        for i, j, k in comp:
            acc ^= (point[0] ** i * point[1] ** j * point[2] ** k) % 2
        out.append(acc)
    return tuple(out)
