# Session notes — Jacobian conjecture with Hypothesis

## Context
- JC disproved 2026-07-20 (Alpöge + Claude Fable), dimension 3; plane case still open.
- Map over C: a=(1+xy)^3 z + y^2(1+xy)(4+3xy); b=y+3x(1+xy)^2 z+3xy^2(4+3xy); c=2x-3x^2y-x^3 z.
- det J = -2 (verified symbolically). Generically 3-to-1 (P^1 x Sym^2 P^1 -> Sym^3 P^1: cubic = linear x quadratic factorizations).

## Built
- uv project (Python 3.13, sympy/hypothesis/pytest), src/jc/{map.py,fibers.py}, tests/{test_conjecture.py,test_counterexample.py}.
- fibers.py: lru-cached grevlex+lex Groebner bases per target; fiber_certificate = staircase count of dim Q[x,y,z]/I_t (etale => radical => exact fiber cardinality); eliminant = univariate-in-z lex basis element; is_generic = deg 3 + squarefree; preimages via sp.solve seeded with lex basis; exact membership check contains_exactly; numeric-only (50-digit) comparisons — NEVER sp.simplify (it hangs on RootOf).

## Key findings
- Minimal Hypothesis-shrunk witness: F(0,0,1)=(1,0,0) also hit by (±i/2, ±3i, -26).
- F(1,2,3)=(201,203,-7): 3 distinct preimages (one rational, two in Q(sqrt(4281))).
- Tao's point (-1/4,0,0): fiber certificate = 1 — other two preimages escape to INFINITY (etale => sheets never merge; non-properness is how JC fails).
- First suite run hung >10min: cause was sp.simplify in distinct/verify. Fixed. Fiber solves are 0.05–0.3s.

## State / next
- Just addressed user's 3 review points (exact membership; is_generic instead of assume(n!=1); Groebner certificate).
- BLOCKER (trivial): test_conjecture.py line 62 uses fiber_certificate without importing it — fix import, then run full suite.
- Then: git init already done (empty repo, branch master); create .gitignore, commit.
- User also asked: does this generalize / is Hypothesis the right tool? Answer in final message: Hypothesis wins here only because failure is GENERIC (every random point witnesses it once you can count fibers exactly); for typical open conjectures counterexamples are thin sets, so PBT is a sanity-checker, not an oracle. Exact arithmetic (sympy over Q) was the real enabler.
