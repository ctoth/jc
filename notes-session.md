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

## Lean phase (started after commit 5b59c9f)
- User roadmap: (1) Lean the certificate, (2) properness locus as computation, (3) char 2 search (finder not checker!), (4) BCW minimality gap. n=2 left alone.
- Toolchain: elan 4.2.3, Lake 5.0.0, Lean 4.32.2. Pattern to copy: ~/code/cold_start (scout dispatched).
- Proof design: (a) F_not_injective over C: witness F(0,0,1) = F(I/2, 3*I, -26) = (1,0,0); hand-checked (1+xy=-1/2, all three coords verified). Tactic: simp [Complex.ext_iff] + norm_num, or linear_combination with I_sq. (b) det J = -2 as MvPolynomial Q (Fin 3) identity: Matrix.det_fin_three + pderiv simp lemmas + ring.

## Lean phase — findings
- cold-start pattern (per scout): NO Lake/mathlib — codegen ONE self-contained Lean file, compile with bare lean; pytest gates: freshness (file == regeneration), toolchain discovery via elan w/ skip, compile check, corrupt-file NEGATIVE control; root lean-toolchain pin; CI lean-action@v1 auto-config:false + git diff --exit-code.
- Adopted design (better than mathlib plan): kernel-computable certificate. Sparse Poly = List ((Nat×Nat×Nat)×Int) w/ insertion-sort norm; formal pderiv in-file; det3 cofactor; witness eval in DYADIC Gaussian rationals GRat=⟨a,b,k⟩=(a+bi)/2^k with parity-based reduce (core Rat gets STUCK in kernel decide due to gcd; dyadic canonical form decides fine).
- Toolchain gotchas: choco Lean 3.4.2 shadows PATH `lean`; elan offline (release.lean-lang.org unreachable); installed toolchain is named `lean4-manual` = 4.32.2. Compile via `elan run lean4-manual lean`. lean-toolchain file keeps canonical pin leanprover/lean4:v4.32.2 for CI.
- STATUS: lean_export/Jc.lean generated (src/jc/lean_export.py) and COMPILES (LEAN_OK): jacobian_det_eq_neg_two, collision F(P1)=F(P2), P1_ne_P2, F_not_injective — all kernel decide, zero imports/axioms/sorry/native_decide.
- Just wrote tests/test_lean.py (freshness, no-escape-hatches, compile, corrupt negative control). NOT YET RUN — that's the next step, then commit #2.

## State / next
- Just addressed user's 3 review points (exact membership; is_generic instead of assume(n!=1); Groebner certificate).
- BLOCKER (trivial): test_conjecture.py line 62 uses fiber_certificate without importing it — fix import, then run full suite.
- Then: git init already done (empty repo, branch master); create .gitignore, commit.
- User also asked: does this generalize / is Hypothesis the right tool? Answer in final message: Hypothesis wins here only because failure is GENERIC (every random point witnesses it once you can count fibers exactly); for typical open conjectures counterexamples are thin sets, so PBT is a sanity-checker, not an oracle. Exact arithmetic (sympy over Q) was the real enabler.
