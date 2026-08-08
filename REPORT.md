# A second counterexample to the separable Jacobian conjecture in characteristic 2

*jc project report, August 2026.*

**Priority note.** The theorem that the separable Jacobian conjecture is
false in characteristic 2 is due to Irit Huq-Kuruvilla
([arXiv:2607.20968](https://arxiv.org/abs/2607.20968), submitted July 23,
2026), via the simpler map (x+x²y, y+xz+x²yz, z+x²z²). Our search ran
independently and we learned of that paper afterwards; we have verified
their map with our own tooling (det J = 1, generic degree 3). What follows
is a second, structurally different explicit counterexample together with
the methodology and certificates.

## The result

**Theorem (second example; the statement is Huq-Kuruvilla's).** Over F₂
(hence over every field of characteristic 2), the map

    F1 = z + xy + xy² + x²y² + x²yz + x²y²z + x³y²z
    F2 = y + xy²                        (= y(1+xy))
    F3 = x + y + xy² + x²z

has Jacobian determinant identically 1, generic degree 3, and is not
injective: (0,0,1), (1,0,1) and (1,1,1) all map to (1,0,0). The
inseparable degree of a finite extension in characteristic 2 is a power of
2 dividing the total degree, so degree 3 forces separability and
Adjamagbo's prime-to-p hypothesis holds. We make no claim about tame
ramification at valuations at infinity: F is a nonproper generically
étale map, not a finite covering, and odd total degree alone does not
imply tameness of every branch at infinity. (The unit Jacobian rules out
ramification at affine points; the classical wild failures like
x ↦ x + x² are excluded by the degree hypothesis, not by a ramification
claim.)

**The collision is the whole fiber.** Over the target (1,0,0) the fiber
ideal has Gröbner basis {x²+x, xy+y, y²+y, z+1}. The geometric fiber has
length 3 and is the disjoint union of the three reduced F₂-rational points
above — no multiplicity, no points in extension fields.

*Verification* (the Gröbner staircase over the function field is the
degree proof; the censuses and specializations corroborate): det J = 1 by three separate
implementations, including a Lean-kernel certificate
(`lean_export/JcChar2.lean`: no imports, no axioms, no `sorry`) that also
certifies the three-point collision — and a collision of rational points
persists over every field extension. Generic degree 3 by Gröbner staircase
over the function field GF(2)(A,B,C), corroborated by exhaustive censuses
over F₈, F₁₆, F₃₂, F₆₄ (every fiber has 1 or 3 points; the sizes account
for every point of the space), and by the x-eliminant specialization at
target (0,1,0), whose non-artifact factor is the irreducible separable
cubic x³ + x + 1. The hand check: on 0/1 coordinates aᵏ = a, so F collapses
to (z+xy+xyz, y+xy, x+y+xy+xz) — one minute with pencil and paper.

*How it was found.* The parity conjecture below — formulated from
exhaustive stratum classifications — implied that no counterexample lives
in Bass–Connell–Wright form, which redirected the search to z-linear maps
(P·z+Q, R·z+S, T·z+U): the shape of the original char-0 counterexample.
The condition det J = 1 over unknown F₂ coefficients was compiled to CNF
(XOR-of-AND algebraic normal form, Tseitin encoding, CaDiCaL model
enumeration with blocking clauses), every unit-Jacobian member of a
2⁵⁸-map family with the original's mod-2 monomial supports was enumerated,
fiber censuses sieved for the pure {1,3} tame signature, and the survivor
was classified exactly. The map surfaced within the first 3,000 models.
The same sweep of a lower-degree z-linear family (2⁴⁵ maps, 400k+ members
enumerated) found nothing — the Sym-mirror structure mattered.

## Context

The Alpöge–Fable counterexample (July 2026) killed the Jacobian conjecture in
characteristic 0 and, by reduction mod p ≡ 1 (mod 4), Adjamagbo's *separable
Jacobian conjecture* in odd characteristic: its map has det J = −2 and is
generically 3-to-1, and 3 is coprime to every odd p ≥ 5. Characteristic 2 is
different — det J = −2 ≡ 0 — and the Secret Blogging Seminar thread asked
whether anyone had looked there (answered by Huq-Kuruvilla on July 23; see
the priority note above). A char-2 counterexample must have generic degree
odd and ≥ 3, with det J = 1 — odd degree forces inseparable degree 1, i.e.
separability. The classic char-2 failures (Artin–Schreier maps like
x ↦ x + x²) have degree divisible by 2 and do not qualify.

## The BCW parity question

The counterexample has degree 3, so no global parity law holds. What
survives is sharper and stranger:

**Open question (BCW-form parity).** *Does every map of
identity-plus-higher-degree form — the shape of the cubic-homogeneous
Bass–Connell–Wright normal form, though we claim no characteristic-2
reduction theorem — with det J = 1 in characteristic 2 have generic
degree 1 or even?*

Every stratum below answers yes, exhaustively. If the answer is yes in
general, something is wrong with the characteristic-2 BCW reduction: in
characteristic 0, BCW says any Jacobian counterexample transports into
cubic-homogeneous identity-plus-H form (in more variables), so a char-2
counterexample of degree 3 coexisting with an all-even BCW region means
the reduction must lose the odd part — plausibly through divisions by 2
or degree-doubling steps that break mod 2 (van den Essen's account of the
reduction is the place to check exactly where characteristic 0 enters).
Either resolution is interesting: a BCW-form odd-degree map (a second,
structurally different counterexample), or a proof that char-2 BCW
reduction is lossy, which would be a theorem about the reduction itself.
This tension, not the histograms, is the mathematical content of the
strata below; the histograms are the evidence that forced the question.

## Evidence

All claims below are machine-checked, exhaustive within their stratum, and
reproducible from this repository (`tests/test_strata.py`; the full
classifications run under `pytest -m slow`). "Generic degree" is computed
exactly as the dimension of GF(2)(A,B,C)[x,y,z]/(F − (A,B,C)) from the
Gröbner staircase over the function field of the target — no point counting,
no resultants, no specialization.

**Dimension 1 (elementary, full proof).** f' = 1 in char 2 forces
f = x + g(x²), whose degree is 1 or even. No tame example exists.

**Proposition (Frobenius-affine maps, full proof).** In the plane stratum
(x + H₁, y + H₂) with H quadratic, char 2 kills every square's derivative,
so det J = 1 + b·y + e·x where b, e are the xy-coefficients: a unit iff
b = e = 0. The surviving maps are v ↦ v + M·v⁽²⁾ — additive group
homomorphisms — whose generic degree is their kernel size, a power of 2.
Parity holds *conceptually* in this substratum, in every dimension where
det J = 1 forces additivity.

**Proposition (structure of the 3D quadratic det-units, full proof).**
Solving det J = 1 symbolically for the full 18-coefficient quadratic family
over GF(2): the square coefficients never enter the determinant, and the
nine cross coefficients admit exactly 8 solutions, parametrized by three
free bits (d, e, f):

    F1 = x + d(y+ex)(z+fx) + (any x², y², z² terms)
    F2 = y + e(x+dy)(z+fy) + (any squares)
    F3 = z + f(x+dz)(y+ez) + (any squares)

— which is 8 × 2⁹ = 4096, matching the enumeration. With d = e = f = 0
these are the Frobenius-affine maps (degree a power of 2, proved). The
nonzero patterns produce the degree-6 maps: covers with a genuine *tame
degree-3 part* — but in every one of the 4096 cases the odd part arrives
multiplied by at least one wild factor of 2. The conjecture's real content
is exactly this: **the odd part never travels alone.**

**Theorem 1 (plane stratum, exhaustive).** Among all 16,384 maps
(x + H₁, y + H₂) over F₂ with H spanned by degree-2 and degree-3 monomials,
exactly 160 have det J = 1. Their exact generic degrees:

| degree | 1 | 2 | 4 | 6 |
|--------|---|---|---|---|
| count  | 10 | 54 | 48 | 48 |

No odd degree ≥ 3 occurs.

**Theorem 2 (3-dimensional quadratic stratum, exhaustive).** Among all
262,144 maps (x + H₁, y + H₂, z + H₃) over F₂ with Hᵢ quadratic, exactly
4096 have det J = 1. Their exact generic degrees:

| degree | 1 | 2 | 4 | 6 | 8 |
|--------|---|---|---|---|---|
| count  | 176 | 728 | 1176 | 672 | 1344 |

No odd degree ≥ 3 occurs.

**Computation, 99.8% complete (3-dimensional cubic-homogeneous stratum).**
Not a full theorem. det J = 1 forces e₁ = e₂ = e₃ = 0 separately; the
e₁-kernel (xyz banned, three parity triples) holds 16,777,216 maps, of
which 10,144 have unit Jacobian. 10,124 are exactly classified:
degree 1 (400), 2 (2,184), 4 (3,696), 6 (3,172), 10 (672) — no odd
degree ≥ 3 anywhere. The remaining 20 maps defeated every method tried
(all generator/monomial orders, monic-linear substitution, Rabinowitsch
rational elimination, hours of CPU each); they are published in
`data/cubic_holdouts.json` as a benchmark family for function-field
Gröbner computation in characteristic 2. All 20 have a size-2 rational
fiber over F₄, which no étale degree-3 cover admits (fibers carry 0, 1,
or 3 rational points), so none is a degree-3 counterexample; odd
degrees ≥ 5 are not excluded by censuses alone.

## Methodological findings

1. **Rational-point censuses cannot certify tameness.** The map
   (x + x², y + y² + xz² + x², z + xz² + xy²) has det J = 1 and shows fiber
   sizes {1, 3} only over F₈ — a perfect tame signature — yet is a wild
   8-to-1 cover; five points of each generic fiber live in extension fields.
   Fiber statistics over any fixed finite field are camouflage.

2. **The characteristic must be carried by the Gröbner engine, not the
   inputs.** sympy's `groebner`, handed `Poly` objects with a GF(2) fraction
   field domain plus explicit generators, silently rebuilds them over
   ℚ(A,B,C) and computes characteristic-0 answers. This manufactured 174
   phantom odd-degree "counterexamples" in the quadratic stratum, diagnosed
   by hand-solving (x + y², y + xz + xy, z + xz + xy): in char 2 the last
   two components collapse (F₂ + F₃ = y + z) and the true degree is 2, not
   the char-0 degree 3. Passing `domain=` to `groebner` directly fixes it;
   a regression test pins the trap.

3. **Wild maps dominate overwhelmingly.** In 400k random
   Bass–Connell–Wright-form samples plus both exhaustive strata, every
   single non-automorphism with det J = 1 had even degree. The parity
   pattern was not designed into the search; it emerged from it.

## Reproduction

```
uv run pytest tests/ -q          # fast layers of everything
uv run pytest -m slow -q         # full exhaustive classifications
```
