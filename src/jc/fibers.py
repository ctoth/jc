"""Exact fiber computation for the counterexample map, with certificates.

Given a target t in Q^3, the fiber F^{-1}(t) is the vanishing locus of the
zero-dimensional ideal I_t = (a - t1, b - t2, c - t3) in Q[x, y, z]. Because
det J = -2 vanishes nowhere, F is etale, so I_t is radical and

    #F^{-1}(t)  =  dim_Q  Q[x, y, z] / I_t,

which we compute exactly by counting standard monomials under the Groebner
staircase. That count is the completeness certificate against which the
root-finding step is checked: solutions are extracted with sp.solve seeded
by the Groebner basis, and callers assert len(solutions) == certificate.

All arithmetic is exact. Individual coordinates may be algebraic numbers
(RootOf/radicals); comparisons on those avoid sp.simplify (which can hang)
in favour of 50-digit interval-style numeric checks.
"""

from functools import lru_cache

import sympy as sp

from jc.map import F, x, y, z


@lru_cache(maxsize=None)
def _bases(target):
    system = [sp.expand(comp - v) for comp, v in zip(F, target)]
    grevlex = sp.groebner(system, x, y, z, order="grevlex")
    # Direct lex Groebner computation blows up at some targets; FGLM
    # conversion from grevlex is fast because the ideal is zero-dimensional
    # (F is etale with finite fibers, so it always is).
    lex = grevlex.fglm("lex")
    return grevlex, lex


def _exact_target(target):
    return tuple(sp.nsimplify(v) for v in target)


def fiber_certificate(target):
    """#F^{-1}(target) over C, as dim of the quotient ring (staircase count).

    Etale-ness makes I_t radical, so this dimension counts geometric points
    exactly, independent of any root-finding.
    """
    grevlex, _ = _bases(_exact_target(target))
    lead = [sp.Poly(g, x, y, z).monoms(order="grevlex")[0] for g in grevlex.exprs]
    # Zero-dimensionality means each variable has a pure power among the
    # leading monomials; those powers box in the staircase.
    bound = []
    for i in range(3):
        powers = [
            exps[i]
            for exps in lead
            if all(e == 0 for j, e in enumerate(exps) if j != i)
        ]
        if not powers:
            raise ValueError(f"ideal for target {target} is not zero-dimensional")
        bound.append(min(powers))
    count = 0
    for i in range(bound[0]):
        for j in range(bound[1]):
            for k in range(bound[2]):
                if not any(
                    li <= i and lj <= j and lk <= k for (li, lj, lk) in lead
                ):
                    count += 1
    return count


def eliminant(target):
    """The univariate polynomial in z generating I_t ∩ Q[z] (from the lex basis).

    Its roots are the z-coordinates of the fiber. Its degree dropping below 3
    is exactly a preimage escaping to infinity; a repeated root marks targets
    where distinct fiber points share a z-coordinate. Away from both, the
    fiber is unambiguously three distinct points.
    """
    _, lex = _bases(_exact_target(target))
    for g in reversed(lex.exprs):
        if g.free_symbols <= {z}:
            return sp.Poly(g, z)
    raise ValueError(f"no univariate eliminant for target {target}")


def is_generic(target):
    """True when the eliminant certifies a full, unambiguous fiber of 3."""
    u = eliminant(target)
    return u.degree() == 3 and sp.discriminant(u.as_expr(), z) != 0


def preimages(target):
    """All complex preimages of `target` under F, as exact sympy triples."""
    t = _exact_target(target)
    _, lex = _bases(t)
    solutions = sp.solve(list(lex.exprs), [x, y, z], dict=True)
    return [(s[x], s[y], s[z]) for s in solutions]


def contains_exactly(fiber, point):
    """Exact (symbolic, no-numerics) membership test for a rational point."""
    p = _exact_target(point)
    return any(
        all(sp.expand(u - v) == 0 for u, v in zip(q, p)) for q in fiber
    )


def verify_preimage(point, target, digits=50):
    """Check F(point) == target: exact where cheap, else 50-digit numeric.

    The numeric path only covers algebraic (RootOf/radical) coordinates,
    where full symbolic simplification is prohibitively slow.
    """
    subs = dict(zip((x, y, z), point))
    for comp, t_val in zip(F, target):
        diff = sp.expand(comp.subs(subs) - t_val)
        if diff == 0:
            continue
        if not _is_numerically_zero(diff, digits):
            return False
    return True


def distinct(points, digits=50):
    """Number of pairwise-distinct points among exact sympy triples."""
    remaining = list(points)
    count = 0
    while remaining:
        p = remaining.pop()
        count += 1
        remaining = [q for q in remaining if not _same(p, q, digits)]
    return count


def _same(p, q, digits):
    return all(_is_numerically_zero(sp.expand(u - v), digits) for u, v in zip(p, q))


def _is_numerically_zero(expr, digits):
    val = expr.evalf(digits, chop=True)
    return abs(val) <= sp.Float(10) ** (-digits + 10)
