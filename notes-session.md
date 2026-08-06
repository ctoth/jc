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

## Rungs 2+3 (after commit d9bfb56 = Jelonek locus)
- Jelonek: x-eliminant = -C*x^9*(D*x^3+(4-3BC)*x-2C), D = 27A^2C^2-18ABC+16A+B^3C-B^2. Fiber x-coords = roots of cubic G; escapes iff D=0 (x-dir) or C=0 (y-dir, LC_y=-2C^2). Rational on-locus family (B=0): (-16/(27c^2), 0, c). src/jc/jelonek.py + tests 6/6 green, committed.
- Char p (src/jc/charp.py): det J = -2 => 0 mod 2 (map dies in char 2 — motivates search); unit mod odd p; Gaussian witness reduces mod p≡1(4) (i=sqrt(-1), e.g. p=5: collision verified). Census mod 5: 3-to-1 confirmed on F_5^3.
- Char-2 finder (src/jc/char2.py): GF(2)[x,y,z] as frozensets of exponent triples (XOR arithmetic), exact det_j; GF(2^k) mul tables k<=4; fiber_census; tame_score (fibers {0,1,3} good, size 2/4 = wild AS signature penalized); random z-linear candidates (P(x,y)z+Q(x,y) per component, pools deg<=3 z-part / deg<=4 free part); search() = det filter -> F_4 screen -> F_8 confirm.
- Key math note: naive separable JC in char 2 already false via Artin–Schreier x^2+x (Jacobian 1, separable, wild). Open target = TAME (degree coprime to 2, e.g. 3-to-1) unit-Jacobian noninjective map. AS test case correctly scored 0 (wild).
- Test suite tests/test_charp.py: 10/11 passed; one fix just applied (sympy modulus= returns symmetric rep -2, compare % p). RERUN NEXT, then: bounded real search run (~50k candidates, timed), README update, commit rung 3.
- No blockers.

## Char-2 search results (rung 3 complete)
- BCW-form sampling (identity+H): det-pass ~13% (vs 0% for generic z-linear).
- 400k run: 51347 det-unit, 1 census-flagged: (x+x², y+y²+xz²+x², z+xz²+xy²), F8 census {1:128, 3:128} — PERFECT tame camouflage.
- Unmasked: y-eliminant deg 8, IRREDUCIBLE at target (1,1,0) ⇒ genuine 8-to-1 wild cover (2 from AS x-part × 4 Bezout). Rational fibers only show {1,3}; 5 points/fiber hide in extensions. KEY LESSON: censuses cannot certify tameness; symbolic elimination stage (degree_verdict) is mandatory. Baked into char2.py + regression tests.
- Ground truth scoring validated: Alpöge map mod 5/13 censuses show sizes {1,3} ONLY (no 2s) — size-2 penalty correct.
- sympy gotchas: modulus= gives symmetric reps (-2 not 3); multivariate factor over GF(p) NotImplemented (specialize→univariate); resultant chains inflate degree by multiplicities (spurious x⁹/-C factors char-0; here 8 was genuine, certified via irreducible specialization).
- Suite: 28 passed + 1 xfailed. README updated. Next: commit rung 3. n=2 left alone per user.

## State / next
- Just addressed user's 3 review points (exact membership; is_generic instead of assume(n!=1); Groebner certificate).
- BLOCKER (trivial): test_conjecture.py line 62 uses fiber_certificate without importing it — fix import, then run full suite.
- Then: git init already done (empty repo, branch master); create .gitignore, commit.
- User also asked: does this generalize / is Hypothesis the right tool? Answer in final message: Hypothesis wins here only because failure is GENERIC (every random point witnesses it once you can count fibers exactly); for typical open conjectures counterexamples are thin sets, so PBT is a sanity-checker, not an oracle. Exact arithmetic (sympy over Q) was the real enabler.
