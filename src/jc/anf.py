"""Polynomials over GF(2) with unknown Boolean coefficients, in ANF.

A `CoefANF` is a set of frozensets of variable names: the XOR of AND-terms
(algebraic normal form over GF(2)). A `SymPoly` maps exponent triples
(i, j, k) to CoefANFs: a polynomial in x, y, z whose coefficients are
unknown bits (or fixed 0/1). Supports +, *, formal derivatives, and 3x3
determinants — enough to express "det J = 1" for a family of maps with
unknown F_2 coefficients as a system of ANF equations, which sat.py
compiles to CNF.

ONE = frozenset() is the constant-true AND-term; the empty CoefANF is 0.
"""

TRUE = frozenset()  # the AND of nothing: constant 1


def anf_xor(a, b):
    return a ^ b


def anf_and(a, b):
    out = set()
    for t1 in a:
        for t2 in b:
            out ^= {t1 | t2}
    return frozenset(out)


ANF_ONE = frozenset({TRUE})
ANF_ZERO = frozenset()


def var(name):
    """A SymPoly-free ANF consisting of the single unknown bit `name`."""
    return frozenset({frozenset({name})})


class SymPoly:
    """dict[(i, j, k)] -> CoefANF, zero coefficients omitted."""

    __slots__ = ("terms",)

    def __init__(self, terms=None):
        self.terms = {e: c for e, c in (terms or {}).items() if c}

    @classmethod
    def constant(cls, anf):
        return cls({(0, 0, 0): anf})

    @classmethod
    def monomial(cls, exps, coef=ANF_ONE):
        return cls({tuple(exps): coef})

    def __add__(self, other):
        out = dict(self.terms)
        for e, c in other.terms.items():
            out[e] = anf_xor(out.get(e, ANF_ZERO), c)
        return SymPoly(out)

    def __mul__(self, other):
        out = {}
        for e1, c1 in self.terms.items():
            for e2, c2 in other.terms.items():
                e = (e1[0] + e2[0], e1[1] + e2[1], e1[2] + e2[2])
                prod = anf_and(c1, c2)
                out[e] = anf_xor(out.get(e, ANF_ZERO), prod)
        return SymPoly(out)

    def deriv(self, axis):
        out = {}
        for e, c in self.terms.items():
            if e[axis] % 2 == 1:
                m = list(e)
                m[axis] -= 1
                out[tuple(m)] = anf_xor(out.get(tuple(m), ANF_ZERO), c)
        return SymPoly(out)

    def __repr__(self):
        return f"SymPoly({self.terms!r})"


def det3(m):
    """Determinant of a 3x3 matrix of SymPolys (char 2: + is -)."""
    a, b, c = m[0]
    d, e, f = m[1]
    g, h, i = m[2]
    return a * (e * i + f * h) + b * (d * i + f * g) + c * (d * h + e * g)


def jacobian(components):
    return [[comp.deriv(axis) for axis in range(3)] for comp in components]


def unit_det_conditions(components):
    """The system of ANF equations expressing det J(components) = 1.

    Returns a list of (anf, rhs) pairs: each coefficient of a nonconstant
    monomial must be 0, the constant coefficient must be 1.
    """
    det = det3(jacobian(components))
    conditions = []
    seen_const = False
    for e, c in det.terms.items():
        if e == (0, 0, 0):
            conditions.append((c, 1))
            seen_const = True
        else:
            conditions.append((c, 0))
    if not seen_const:
        conditions.append((ANF_ZERO, 1))  # constant term 0: unsatisfiable
    return conditions
