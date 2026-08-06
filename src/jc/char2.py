"""A finder for tame Jacobian-conjecture counterexamples in characteristic 2.

The Alpöge–Fable map has det J = -2, which vanishes mod 2, and the classic
char-2 failures of the naive statement are Artin–Schreier maps like
x -> x^2 + x: Jacobian 1 but *wild* (degree divisible by p). The open
question is tame: is there a map over F_2 with constant unit Jacobian that
is generically finite of degree coprime to 2 (e.g. 3-to-1) and not
injective? Here the methodology flips from checker to finder: the search
space is finite and layered — exact symbolic det J over GF(2), then
exhaustive fiber censuses over F_4, F_8, F_16.

Candidate maps mirror the counterexample's shape: each component is
P(x,y)*z + Q(x,y), linear in z, with P, Q drawn from a monomial pool.

GF(2) polynomials are sets of exponent triples (coefficients are 0/1, so
addition is symmetric difference); an étale degree-3 cover would show
rational fiber sizes in {0, 1, 3} (Galois orbits), while wild Artin–
Schreier behaviour shows fibers of size 2 — the census separates them.
"""

import itertools
import random
from collections import Counter

# --- GF(2)[x, y, z] as sets of exponent triples ---------------------------


def padd(a, b):
    return a ^ b


def pmul(a, b):
    acc = set()
    for e1 in a:
        for e2 in b:
            m = (e1[0] + e2[0], e1[1] + e2[1], e1[2] + e2[2])
            acc.symmetric_difference_update({m})
    return frozenset(acc)


def pderiv(p, var):
    out = set()
    for e in p:
        if e[var] % 2 == 1:
            m = list(e)
            m[var] -= 1
            out.symmetric_difference_update({tuple(m)})
    return frozenset(out)


ONE = frozenset({(0, 0, 0)})
ZERO = frozenset()


def det_j(components):
    """det of the Jacobian of three GF(2) polynomials, exactly."""
    rows = [[pderiv(c, v) for v in range(3)] for c in components]
    ((a, b, c), (d, e, f), (g, h, i)) = rows
    return padd(
        padd(pmul(a, padd(pmul(e, i), pmul(f, h))),
             pmul(b, padd(pmul(d, i), pmul(f, g)))),
        pmul(c, padd(pmul(d, h), pmul(e, g))),
    )


# --- GF(2^k) arithmetic ----------------------------------------------------

_IRREDUCIBLE = {1: 0b10, 2: 0b111, 3: 0b1011, 4: 0b10011}


class GF2k:
    def __init__(self, k):
        self.k = k
        self.q = 1 << k
        poly = _IRREDUCIBLE[k]
        self.mul_table = [
            [self._slow_mul(a, b, poly, k) for b in range(self.q)]
            for a in range(self.q)
        ]

    @staticmethod
    def _slow_mul(a, b, poly, k):
        acc = 0
        while b:
            if b & 1:
                acc ^= a
            b >>= 1
            a <<= 1
            if a >> k:
                a ^= poly
        return acc

    def pow(self, a, n):
        acc, base = 1, a
        while n:
            if n & 1:
                acc = self.mul_table[acc][base]
            base = self.mul_table[base][base]
            n >>= 1
        return acc

    def eval_poly(self, p, point):
        acc = 0
        for i, j, k in p:
            term = self.mul_table[self.pow(point[0], i)][
                self.mul_table[self.pow(point[1], j)][self.pow(point[2], k)]
            ]
            acc ^= term
        return acc


def fiber_census(components, field):
    """Histogram of rational fiber sizes of the map over GF(2^k)^3."""
    images = Counter()
    for point in itertools.product(range(field.q), repeat=3):
        images[tuple(field.eval_poly(c, point) for c in components)] += 1
    return Counter(images.values())


def is_injective_census(census):
    return set(census) <= {1}


# --- candidate generation --------------------------------------------------

# A generic map essentially never has constant Jacobian, so sampling is done
# in Bass–Connell–Wright normal form, F = identity + H with H of degree >= 2:
# there det J = 1 + (corrections), and small supports for H pass the exact
# det filter at a workable rate.

_VARS = (
    frozenset({(1, 0, 0)}),
    frozenset({(0, 1, 0)}),
    frozenset({(0, 0, 1)}),
)

#: Monomials of degree 2 and 3 in x, y, z for the higher-order part H.
H_POOL = [
    (i, j, k)
    for i in range(4)
    for j in range(4)
    for k in range(4)
    if 2 <= i + j + k <= 3
]


def random_candidate(rng, max_terms=3):
    """A random map x + H1, y + H2, z + H3 with each Hi drawn from H_POOL."""
    comps = []
    for v in _VARS:
        n = rng.randint(0, max_terms)
        h = frozenset(rng.sample(H_POOL, n)) if n else ZERO
        comps.append(v ^ h)
    return tuple(comps)


def tame_score(census):
    """Fraction of occupied fibers of size 3, penalized by any size-2 or
    size-4 fibers (wild/Artin–Schreier signature)."""
    total = sum(census.values())
    if total == 0 or census.get(2, 0) or census.get(4, 0):
        return 0.0
    return census.get(3, 0) / total


# --- symbolic verification stage ------------------------------------------

# Rational-point censuses cannot see geometric degree: the first flagged
# candidate of this search, (x + x^2, y + y^2 + xz^2 + x^2, z + xz^2 + xy^2),
# shows fibers of sizes {1, 3} only over F_8 yet is a wild 8-to-1 cover —
# five points of each generic fiber live in extension fields. Tameness
# verdicts therefore come from elimination over GF(2), not from counting.


def generic_degree(comps, gens_order=(0, 1, 2)):
    """The exact generic degree of the map over F_2-bar: the dimension of
    GF(2)(A,B,C)[x,y,z] / (F - (A,B,C)) computed from the Groebner
    staircase over the function field of the target.

    For a unit-Jacobian (etale) map this equals the generic fiber
    cardinality with no multiplicity: odd >= 3 means tame non-injective —
    the char-2 unicorn — while even means wild. Returns None if the
    generic fiber is not finite (the map is not dominant-with-finite-fibers).

    gens_order permutes the Groebner generators; the dimension is
    order-invariant but Buchberger's running time is not — maps that wedge
    under one order often finish instantly under another.
    """
    import sympy as sp

    x, y, z, A, B, C = sp.symbols("x y z A B C")
    dom = sp.GF(2).frac_field(A, B, C)
    f1, f2, f3 = (_to_expr(c) for c in comps)
    system = [f1 - A, f2 - B, f3 - C]
    gens = [(x, y, z)[i] for i in gens_order]

    # Preprocessing a good CAS would do automatically: while some equation
    # is monic-linear in a variable (coefficient a nonzero constant), solve
    # it out and substitute. This is exact (the substitution is a ring
    # isomorphism of the quotient) and turns triangular maps like
    # (x + y^3, ...) from Buchberger-killers into small systems.
    changed = True
    while changed and len(gens) > 1:
        changed = False
        for eq_i, eq in enumerate(system):
            for v in list(gens):
                p = sp.Poly(eq, v)
                if p.degree() != 1:
                    continue
                lead = p.all_coeffs()[0]
                if lead.free_symbols & set(gens):
                    continue  # non-constant coefficient: not safe to invert
                if sp.simplify(lead) == 0:
                    continue
                # v = -(rest)/lead; char-agnostic via solve of linear poly
                rest = eq - lead * v * 1
                sol = sp.expand(-rest / lead)
                system = [
                    sp.expand(other.subs(v, sol))
                    for j, other in enumerate(system)
                    if j != eq_i
                ]
                gens.remove(v)
                changed = True
                break
            if changed:
                break

    if not gens:
        return 1  # fully triangular: the map is an automorphism-like solve

    # The domain MUST go to groebner itself: given Poly inputs and explicit
    # gens it silently rebuilds them over QQ(A,B,C), i.e. characteristic 0,
    # and every degree that differs between char 0 and char 2 comes out
    # wrong (this produced 174 phantom "tame counterexamples" once).
    basis = sp.groebner(system, *gens, order="grevlex", domain=dom)
    lead = [g.monoms(order="grevlex")[0] for g in basis.polys]
    n = len(gens)
    bound = []
    for i in range(n):
        powers = [e[i] for e in lead if all(v == 0 for j, v in enumerate(e) if j != i)]
        if not powers:
            return None
        bound.append(min(powers))
    import itertools as it

    return sum(
        1
        for combo in it.product(*(range(b) for b in bound))
        if not any(all(l <= c for l, c in zip(le, combo)) for le in lead)
    )


def _to_expr(component):
    import sympy as sp

    x, y, z = sp.symbols("x y z")
    return sp.Add(*(x**i * y**j * z**k for (i, j, k) in component))


def search(n_candidates, seed=0, screen_k=2, confirm_k=3):
    """Sample candidates; keep unit-Jacobian, non-injective, tame-looking maps.

    Returns a list of (components, screen_census, confirm_census, score),
    best score first.
    """
    rng = random.Random(seed)
    screen, confirm = GF2k(screen_k), GF2k(confirm_k)
    flagged = []
    stats = Counter()
    for _ in range(n_candidates):
        comps = random_candidate(rng)
        if det_j(comps) != ONE:
            stats["det_rejected"] += 1
            continue
        stats["det_unit"] += 1
        census = fiber_census(comps, screen)
        if is_injective_census(census) or not census.get(3, 0):
            stats["screen_rejected"] += 1
            continue
        confirm_census = fiber_census(comps, confirm)
        score = tame_score(confirm_census)
        stats["confirmed" if score > 0 else "confirm_rejected"] += 1
        if score > 0:
            flagged.append((comps, census, confirm_census, score))
    flagged.sort(key=lambda item: -item[3])
    return flagged, stats
