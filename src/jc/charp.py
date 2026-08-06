"""The counterexample map in characteristic p.

det J = -2, so reduction mod an odd prime keeps the Jacobian a unit and
(for p = 1 mod 4, where sqrt(-1) exists) the Gaussian witness collision
survives: the map refutes the separable Jacobian conjecture in odd
characteristic. Mod 2 the determinant vanishes — the map is not even a
candidate there, which is exactly why characteristic 2 calls for a search
(see jc.char2).
"""

import sympy as sp

from jc.map import F, x, y, z


def monomials():
    """The map as integer monomial data: three lists of ((i,j,k), coeff)."""
    out = []
    for comp in F:
        poly = sp.Poly(sp.expand(comp), x, y, z)
        out.append([(exps, int(c)) for exps, c in sorted(poly.terms())])
    return out


def det_j_mod(p):
    """det J of the reduced map over GF(p) — always the constant -2 mod p."""
    jac = sp.Matrix([[sp.diff(comp, v) for v in (x, y, z)] for comp in F])
    det = sp.expand(jac.det())
    return sp.Poly(det, x, y, z, modulus=p).as_expr()


def evaluate_mod(point, p):
    """Evaluate the reduced map at a point of GF(p)^3."""
    result = []
    for comp in monomials():
        acc = 0
        for (i, j, k), coeff in comp:
            acc += coeff * pow(point[0], i, p) * pow(point[1], j, p) * pow(point[2], k, p)
        result.append(acc % p)
    return tuple(result)


def sqrt_minus_one(p):
    """An i with i^2 = -1 in GF(p), for p = 1 mod 4."""
    if p % 4 != 1:
        raise ValueError(f"-1 is not a square mod {p}")
    for g in range(2, p):
        i = pow(g, (p - 1) // 4, p)
        if (i * i) % p == p - 1:
            return i
    raise AssertionError("unreachable for prime p = 1 mod 4")


def witness_mod(p):
    """The reduced Gaussian witness pair (P1, P2) in GF(p)^3, p = 1 mod 4.

    P1 = (0, 0, 1) and P2 = (i/2, 3i, -26) mod p; both map to (1, 0, 0).
    """
    i = sqrt_minus_one(p)
    inv2 = pow(2, -1, p)
    return (0, 0, 1), ((i * inv2) % p, (3 * i) % p, (-26) % p)
