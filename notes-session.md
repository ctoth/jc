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

## Goal-mode: breakthrough hunt (/goal active: don't stop until our own breakthrough)
- Defined breakthrough: exhaustive certified strata theorems in char 2 (or actual tame counterexample).
- QUADRATIC STRATUM (2^18 = 262144 maps id+H, H quadratic): 4096 det-unit. Census screen: 0 tame survivors.
- CUBIC-HOMOGENEOUS STRATUM: e1=0 linear reduction (xyz banned + 3 parity triples) → 16.7M enumerated in 371s: 10144 det-unit, 336 census-tame survivors, 624 injective-at-F4. Results: scratchpad/cubic_results.json.
- TOOL SAGA (critical): (1) resultant-chain degree_verdict fragile (z-free assumptions, squaring artifacts) — REMOVED. (2) Built generic_degree: Groebner staircase over GF(2)(A,B,C) = exact generic degree. (3) TRAP FOUND: sp.groebner(Polys, gens, order=) IGNORES Poly domains — computed over QQ(A,B,C) (char 0!), yielding 174 phantom odd-degree 'unicorns' in quadratic stratum. Diagnosed via hand-check of (x+y², y+xz+xy, z+xz+xy): char-2 cancellation F2+F3=y+z ⇒ degree 2 (tool said 3 = char-0 degree). FIX: pass domain=GF(2).frac_field(A,B,C) directly to sp.groebner(...). Regression test added (test_generic_degree_is_char_2_not_char_0).
- Corrected quadratic classification running (bf3gypfxc → quadratic_exact2.json): so far ONLY even degrees + degree-1 automorphisms. Zero unicorns at 1280/4096.
- NEXT: finish quadratic → run classify_cubic_exact.py on cubic det-units (script ready in scratchpad) → if zero odd ≥3: two certified finite theorems = the breakthrough deliverable (plus tooling). Then bake theorems as tests + README + commit.

## Breakthrough status (goal mode)
- THEOREM 1 (committed 4b7092c): quadratic 3D stratum, 262144 maps, 4096 det-unit, exact degrees {1:176, 2:728, 4:1176, 6:672, 8:1344} — zero odd ≥3. No tame counterexample.
- THEOREM 2 (just computed, being baked into tests): plane stratum (x+H1,y+H2), H deg≤3, 16384 maps, 160 det-unit, {1:10, 2:54, 4:48, 6:48} — zero odd. src/jc/plane2.py added; tests/test_strata.py has sampled + slow-full layers (slow layer asserts exact histograms).
- 1D: trivial proof (f'=1 ⇒ f = x+g(x²) ⇒ even degree or linear).
- PARITY CONJECTURE (our formulation): char 2, det J = 1 ⇒ generic degree 1 or even. If true, Adjamagbo's tame/separable JC is VACUOUSLY true for p=2. Lit check (websearch): Adjamagbo's separable JC has hypothesis p ∤ degree; char-2 case flagged unexplored in SBS thread; no parity statement found → plausibly novel observation/conjecture.
- IN FLIGHT: cubic-homogeneous 3D classification (task bv2npofv2 → cubic_exact.json): 10144 det-units at ~3/s ≈ 55min; so far all even. Will be THEOREM 3.
- Current work: finish test_strata.py plane tests (Pyright noise on 'from jc import plane2' — likely stale venv index; verify by running pytest), then README/REPORT writeup + commit. Blocker: none; waiting on cubic task.

## Cubic classification saga
- v1 (classify_cubic_exact.py, task bv2npofv2) WEDGED at ~map 1000-1200: sympy Buchberger over GF(2)(A,B,C) can hang on specific cubic systems; no per-map timeout. Killed.
- v2 (classify_cubic_v2.py, task b71oxw1up → cubic_exact.jsonl): batch subprocesses (40 maps/batch, hard subprocess.run timeout, split-on-timeout down to single maps → deferred list). Resumable via JSONL. Monitor bwudbosvo watches. ~1000 maps had been classified by v1 (all even: {1:79, 2:306, 4:360, 6:256} at map 1000) — v2 redoes them.
- Frobenius-affine PROPOSITION (proved, in tests + REPORT): 2D quadratic-only + det J=1 ⇒ H additive (v ↦ v+Mv^(2)) ⇒ degree = |kernel| = 2^k. Conceptual parity proof for that slice.
- REPORT.md drafted: context, Parity Conjecture, Theorems 1 (plane 16384/160/{1:10,2:54,4:48,6:48}) + 2 (3D quadratic 262144/4096/{1:176,2:728,4:1176,6:672,8:1344}), methodology (census camouflage, char-0 groebner trap, wild dominance). Theorem 3 section = placeholder pending cubic_exact.jsonl → MUST fill before committing REPORT.
- Commits so far: 5b59c9f, 04ddf51, d9bfb56, 3923b2f, 4b7092c (theorem: 3D quadratic), 2e8b8c0 (theorem: plane).
- NEXT on cubic completion: histogram from JSONL (+ handle deferred maps manually via alternative methods), fill REPORT theorem 3, README pointer to REPORT, add cubic theorem test (sampled + slow-full from det_units regeneration — note: cubic det_units enumeration takes 371s; slow test should re-derive), final commit, then declare breakthrough & stop.

## Latest state (goal mode, cubic pending)
- Commits now: ...4b7092c (thm 3D-quad), 2e8b8c0 (thm plane), 3a21127 (structure proposition tests).
- 3D quadratic det-unit STRUCTURE PROVED: F_i = id + d(y+ex)(z+fx)(+cyclic) + free Frobenius squares; 8 patterns × 512. Degree-6 entries show odd tame factors exist but always ×2 — "odd part never travels alone" = real content of conjecture.
- REPORT.md drafted (theorem 3 section = explicit in-progress placeholder — DO NOT COMMIT until filled). README updated with parity-conjecture section (references REPORT).
- test_strata.py: 7 fast tests green (incl. cubic all-even-parity block: 3004 det-units pinned, seeded degree sample; plane + 3D-quad exhaustive counts; Frobenius-affine + 8-pattern symbolic proofs). Slow tests: full classifications.
- Cubic classification v2 RESUMED as task bcf3v3sqx (monitor b1lo80800): resumes cubic_exact.jsonl (1000/10144 done, all even so far {1:79,2:306,4:360,6:256}). Retuned: batch timeout 30+3n s, first-missing-map isolation (worker sequential ⇒ first missing = wedged), singles deferred at 45s. Expect DEFERRED for the v1-wedge map (~idx 1000-1040).
- On DONE: build histogram from JSONL (incl. deferred count), handle deferred maps (try higher timeout retry or lex order or report as deferred-with-bound), fill REPORT thm 3 + slow-test histogram assert, commit REPORT+README+tests, summarize breakthrough, allow stop.
- Breakthrough claim when done: Parity Conjecture + 3 exhaustive theorems + 2 conceptual proofs (Frobenius-affine; 2D-quadratic forced additivity) + structure classification + validated tooling; positioned vs Adjamagbo separable JC (vacuous for p=2 if conjecture holds).

## Cubic run live status
- Pipeline fully automated: main sweep (bcf3v3sqx) + auto-crack loop (bjmbgazhu, runs crack_deferred.py every 60s until main prints DONE) + monitor (b1lo80800).
- Wedge maps so far: 1036 (deg 6), 1041 (deg 6), 1203 (deg 6, auto-cracked ✓), 1480 (deferred, auto-crack next pass). ALL crack instantly with generator order (x,z,y) = perm (0,2,1); all are y³-heavy family; all degree 6 = even ⇒ parity intact.
- ~1519 maps classified (grep '"d"' cubic_exact.jsonl), all degree 1 or even.
- On main DONE + final auto-crack pass: build histogram from JSONL (watch duplicate i records — dedupe by i, prefer records with 'd'), check count == 10144, fill REPORT.md theorem 3 + slow-test histogram, commit, declare breakthrough.
- No blockers; pure compute wait (~est 30-60 min remaining given wedge overhead).

## GO-HARD phase (user raised bar: push ONLY if breakthrough equivalent to Alpöge's)
- Bar: (a) actual tame char-2 counterexample (answers SBS open question — the true equivalent), or (b) proof-grade parity theorem. Strata theorems alone insufficient → NO git push yet.
- Key insight: original counterexample is Z-LINEAR (Pz+Q shape), NOT BCW id+H — our exhausted strata were the wrong neighborhood!
- NEW MACHINERY (committed? not yet): src/jc/anf.py (SymPoly: GF(2)[x,y,z] with unknown Boolean coefficient bits in ANF) + src/jc/satfinder.py (det J = 1 → CNF via Tseitin AND-aux + chained XOR; Cadical195 model enumeration w/ blocking clauses over free bits; instantiate()). python-sat added to deps.
- VALIDATED: SAT sweep of quadratic stratum → exactly 4096 unit-Jacobian maps in 0.0s (matches brute-force theorem 1 count). instantiate → det_j check ✓.
- RUNNING: zlinear_hunt.py mode A (task bxotr04xj, monitor bmvyof6ob): P,R,T deg≤2 (w/ const), Q,S,U deg≤3 nonconst = 45 bits = 2^45 family; SAT-enumerates ALL det-unit members; census triage → exact generic_degree (order (0,2,1)) for interesting + 1-in-50 systematic sample. Mode B ready (deg 4 pools) after A.
- Risk: det-unit model count in family A could be astronomically large (blocking-clause enumeration one at a time). If >500k models, restructure (add constraints: require nonconstant z-part, symmetry breaking, or cluster by z-part pattern).
- STILL RUNNING: 3 parallel cubic classification workers (b8gewu3b5/b6amybjfn/bi32cbskn, stride 3, worker order (0,2,1)) + auto-crack loop (bjyrpzfx1) + quiet monitor (bzaxjj1hg). Theorem 3 completes on their DONE.
- Wedge maps resolved so far: 1036→6, 1041→6, 1203→6 (all (0,2,1)-cracked). 1480, 1554, 1581, 1703 deferred → auto-crack.

## Hunt engineering log (latest)
- Z3 question answered: NOT using/needing Z3 — pure GF(2) XOR/AND ⇒ plain SAT (CaDiCaL via python-sat); CryptoMiniSat (native XOR) is the upgrade lever if encoding strains. Validated: SAT reproduces quadratic stratum's 4096 exactly in 0.0s.
- zlinear_hunt redesigned twice: (1) phase-1-only (enumerate + census triage → JSONL; NO in-process Groebner — wedge-proof; phase 2 = hardened batch classifier). (2) F8 tame-signature sieve ({1,3}-only fibers) — of ~30k F4-interesting maps, ZERO passed F8 sieve so far: camouflage-grade rarity confirmed, phase 2 will be cheap.
- Orphan lesson: TaskStop kills pwsh wrapper, NOT python child — must Stop-Process via Win32_Process CommandLine match. (One orphan produced mixed-criteria zlinear_interesting.jsonl — deleted.)
- Frobenius quotient optimization (just implemented, restart pending): bits absent from all det conditions (Q,S,U monomials with all-even exponents: x², y² per component = 6 bits in mode A) are det-irrelevant ⇒ SAT enumerated each base model 64×. New: satfinder.unconstrained_bits + fix_zero param; hunt expands frobenius_variants(base) explicitly. 64× fewer SAT models. Also removed seen-dedupe (bit↔monomial bijection ⇒ no dups; memory).
- Current hunt task bps1ge05j (monitor boopn24bh) still running OLD code at ~50k models — KILL & RESTART with quotient next step (kill python child properly!).
- Cubic aggregate: 2624/10144, hist {1:150, 2:667, 4:967, 6:758, 10:67, deferred:15}, odd≥3 NONE. New degree 10 appeared (even ✓). Watch: earlier live-print showed 'None: 2' — investigate at end. ETA ~1.5h.
- Family A too low-degree to contain the original's analogue (P deg≤2 vs (1+xy)³ deg 6) — mode B (deg 4) and mode C (Sym-mirror supports) queued after A.

## *** THE UNICORN — BREAKTHROUGH FOUND AND VERIFIED (pre-commit state) ***
- MAP (over F₂): F1 = z + xy + xy² + x²y² + x²yz + x²y²z + x³y²z; F2 = y + xy² = y(1+xy); F3 = x + y + xy² + x²z. Variant with F3 = x + x²z also valid. Found by SAT-sweep of Sym-mirror z-linear family (mode C) within 3000 models; 6 family members total so far (all census {1:281, 3:77} at F₈).
- VERIFIED (all independent): det J ≡ 1 (sympy + ANF + Lean kernel); generic degree 3 (function-field Gröbner + irreducible separable cubic x³+x+1 eliminant specialization at target (0,1,0)); fibers ∈ {1,3} over F₈/F₁₆/F₃₂/F₆₄ covering every point; HAND-CHECKABLE F₂-rational collision (0,0,1),(1,0,1),(1,1,1) ↦ (1,0,0) (on 0/1 points F1 collapses to z+xy+xyz, F2=y+xy, F3=x+y+xy+xz).
- MEANING: refutes Adjamagbo separable/tame JC in char 2 (the case Alpöge–Fable couldn't touch, SBS open question) AND refutes our own parity conjecture (which aimed the search — honest science). Alpöge-equivalent breakthrough per user's bar ⇒ PUSH authorized after commit.
- ARTIFACTS DONE: src/jc/unicorn.py; tests/test_unicorn.py (9/9 green: det, sympy-independent det, collisions, degree 3, censuses, eliminant certificate, pure-python hand check, parity refutation); src/jc/lean_export2.py → lean_export/JcChar2.lean COMPILES (LEAN_OK: kernel-checked det J=1 + collision + non-injectivity; degree-3 NOT formalized, documented); tests/test_lean.py parameterized over both certs (just edited, NOT yet run).
- REMAINING before commit+push: (1) run full suite; (2) reframe tests/test_parity_conjecture.py (conjecture refuted — keep as BCW-strata-parity observation + note); (3) README + REPORT rewrite (unicorn front and center; parity conj → refuted; strata theorems stand as "where parity holds"); (4) commit; (5) git remote missing — need gh repo create (private first?) or ask; user said "push when committed" + equivalence met.
- Background: hunt A 400k models 0 tame (family A clean); hunt C still collecting family; cubic workers ~3900/10144 all even + 10s; auto-crack running. These finish on their own; results folded into REPORT numbers as available.

## Post-review pass (user verified independently — directives in flight)
- User's independent verification AGREES: det J ≡ 1; three points → (1,0,0); staircase basis {1,y,z} degree 3 (their gens order); fiber ideal over (1,0,0) GB = {x²+x, xy+y, y²+y, z+1}, dim 3, radical. I re-verified fiber claim myself: same GB, staircase {1,x,y}, brute F₂ scan = exactly the 3 witnesses. STRONGER STATEMENT now in REPORT/README/tests: collision is the WHOLE fiber — reduced, entirely F₂-rational, no multiplicity, no extension stragglers.
- DONE this pass: (1) fiber test added (test_fiber_over_the_target_is_reduced_and_entirely_rational) — NOT YET RUN; (2) retitle "tame"→"separable" (REPORT title, README headline; tame/wild reserved for ramification discussion inside, per Shestakov–Umirbaev collision concern); (3) parity section restructured as OPEN "BCW parity question" + the reduction-tension paragraph (char-2 BCW reduction must be lossy if parity holds in BCW form — check van den Essen for where char 0 enters); (4) "Theorem 3" → "Computation in progress" (verification-hygiene fix).
- REMAINING: (a) run suite; (b) write 4-page LaTeX note (title: "The separable Jacobian conjecture is false in characteristic 2") in paper/ — sections: statement+verification (incl. fiber-is-whole-fiber, Lean cert), discovery method (SAT/ANF), remarks (Speyer char-2 geometric question: strange conics/inseparable Gauss maps/biduality failure — does the mechanism transport?; BCW parity question), refs (Alpöge announcement, SBS thread, Tao digestion, Adjamagbo, BCW, van den Essen, Speyer tangent-sweep). Check pdflatex availability; ship .tex regardless; (c) draft SBS comment text for user; (d) commit + push. arXiv submission itself = user's hand (their account).
- Background: cubic ~4k/10144 (all even+1); hunt A 500k models 0 tame; hunt C collecting family. Fold into future commit.

## SCOOP + math-error correction pass (second reviewer, verified real)
- SCOOPED: Huq-Kuruvilla, arXiv:2607.20968, submitted July 23 2026 — "An Explicit Characteristic-2 Counterexample to the Separable Jacobian Conjecture". CONFIRMED via WebFetch (title/author/date/result) AND by running their map (x+x²y, y+xz+x²yz, z+x²z²) through OUR tooling: det J = 1 mod 2, generic degree 3 ✓. Our theorem is a REdiscovery (13 days late); our map is distinct (different supports; automorphism-equivalence unknown — noted as open in paper).
- MATH ERROR fixed: "degree prime to p ⇒ tame" is FALSE (deg-3 non-Galois ext can have e=2 wild branch, 2+1=3; also F nonproper — no ramification claims at infinity possible from unit Jacobian alone). All tame claims replaced with: insep degree = 2-power dividing 3 ⇒ 1 ⇒ separable; explicit no-claim-about-tameness-at-infinity language; nonproper-étale-not-covering phrasing.
- Other reviewer fixes applied: fiber statement scheme-theoretic (length 3, disjoint union of 3 reduced rational points); specialization = corroboration not independent proof (function-field staircase IS the proof); "strata modeled on cubic-homogeneous BCW normal form" (no char-2 reduction theorem claimed); "Theorem 3"→"Computation in progress" (done earlier).
- REWRITTEN: paper/note.tex (new title "A second counterexample... found by SAT search"; HK credited in abstract+statement+bib incl. arXiv:2608.00222 dims>2 ref); README headline + body; REPORT priority note + result section + context + BCW-parity question wording; unicorn.py + test_unicorn.py docstrings.
- Earlier this pass: fiber-is-whole-fiber verified + tested (10/10, then 51 passed full suite); note.tex first draft; retitle tame→separable.
- REMAINING: run full suite; commit; push (authorized); tell user: scoop confirmed + corrections done + note repositioned; SBS comment draft should now credit HK. No pdflatex locally — .tex ships source-only.
- Background: hunt A 600k+ models 0 tame; hunt C collecting; cubic ~4k/10144 all even.

## Inequivalence program (user directive: 1 week, then post regardless)
- CENSUS INVARIANT EXHAUSTED: ours vs HK IDENTICAL over F₄ (37/9), F₈ (281/77), F₁₆ (2161/645), F₃₂ (16865/5301). Both consistent with S₃ monodromy (3-fiber fraction → ~1/6 Chebotarev) ⇒ censuses likely CANNOT separate any two S₃ degree-3 maps — need finer invariants.
- NORMAL FORM DISCOVERED (verified symbolically): target shear (a,b,c)→(a,b,c+b) puts OUR map into N = (z + xy(1+y+xy)(1+xz), y(1+xy), x(1+xz)) — det 1, degree 3 ✓. HK in same grammar: (x(1+xy), y+xz(1+xy), z(1+x²z)). Both in (1+·)-unit-product grammar of Alpöge construction. Equivalence question now a matching problem between two small normal forms.
- Week plan: (1) finer invariants: Jelonek locus (symbolic eliminant LC mod 2) degree/components/point-counts per map; geometric-fiber-drop locus counts via staircase (F₂ targets + w-adjunction for F₄); (2) SAT search for bounded-degree automorphism pair β∘HK∘α = ours (ANF composition; enumerate GL₃(F₂)=168 linear parts × triangular elementaries); (3) Lean upgrade: kernel-certify fiber-ideal equality via explicit cofactor identities (sympy computes cofactors, Lean checks polynomial identities) — moves certificate onto load-bearing claim; (4) if cubic 16.7M finishes clean → restructure note around parity phenomenon per user (paper not note).
- User decisions pending: authorship line in note.tex (comment must be resolved deliberately before posting); exact Gao initial (TODO in bib); SBS comment posting (their account).
- note.tex updated: normal form + census-agreement paragraph, Alpöge date July 19–20, Gao cite w/ TODO.
- Background: hunt A 800k/0 tame; cubic ~4k+/10144 all even; hunt C collecting.

## Inequivalence attempt: all invariants AGREE (equivalence now leading hypothesis)
- Censuses: identical F₄..F₃₂ (both S₃ monodromy, Chebotarev 1/6 split fraction — censuses can't separate such maps in principle).
- Jelonek/geometric stratification (w-adjunction staircase, per rational target): identical F₂ ({0:1,1:3,3:4}), F₄ ({0:3,1:13,3:48}), F₈ ({0:7,1:57,3:448}). BOTH maps: drop locus has exactly q² points = (q−1) empty fibers + (q²−q+1) singletons. Eerily clean shared fine structure.
- Eliminant LCs differ ((A+BC)² vs B²) but NOT invariant (both surfaces are automorphism-equivalent graphs ≅ A²) — no distinction.
- note.tex updated: honest "attempted and failed to distinguish on every invariant tried; consistent with equivalence, not established; explicit search in progress."
- NEXT (decisive): meet-in-the-middle BFS/SAT search for automorphism pair β∘HK∘α = N. Generators: GL₃(F₂) (168) + translations (8) + single-monomial elementary shears (xᵢ += monomial in other vars, deg ≤ 3, self-inverse in char 2). States = canonical comps tuples; prune degree > 6; expand balls from both normal forms, intersect. If found ⇒ equivalent (methodology note); if exhausted at depth d ⇒ 'not equivalent by compositions of ≤ d generators' (publishable partial).
- Background: cubic classification still going (~4k+/10144 all even); hunt A ~900k+/0 tame; hunt C collecting.
- Pending user decisions: authorship line, Gao initial (my 'H.' is a GUESS — flagged TODO), SBS comment.

## Equivalence search results (exact, complete at their depths)
- Level 0: NOT affinely equivalent (all 1344² pairs via meet-in-middle: hash {β∘N}, probe {H∘α}).
- Level 1: NOT equivalent w/ one shear per side (29,568 rhs states, 0 hits).
- Level 2: NOT equivalent by words of length ≤ 2 per side over G = 1344 affines + 27 monomial shears (deg ≤ 3). rhs 53,529 distinct states (from 1.9M words — massive collapse), 1.9M probes, 0 possible hits (64-bit digest matching, verify-on-hit protocol, none to verify).
- Combined picture: ALL invariants agree (censuses F₄–F₃₂; geometric fiber stratification F₂–F₈ incl. shared q²-point drop locus = (q−1) empty + rest singleton) YET no low-complexity equivalence. Note updated with exact quantified statement. Depth 3 naive = 2.6e9/side — infeasible; smarter targeted methods (stabilizer chains, invariant-guided) possible later.
- Note's equivalence paragraph now the honest both-ways statement the user asked for. Ready for their 1-week window decision.
- Background: hunt A 1M+ models 0 tame (monitor re-armed bmt2sl0nx); cubic classification ongoing; hunt C collecting.

## Landscape update + paper restructure (user directives, both executed)
- NEW SCOOP LAYER: Mondello, arXiv:2608.02634, July 29 2026 — DIMENSION-TWO char-2 counterexample (x + x²y + x⁴ + x⁶y², y + x⁵ + x⁶y + x⁷y² + x⁸y³), witnesses (0,1),(1,0),(1,1) → (0,1), Lean/Mathlib formalized + Aristotle replay (per aimath.robertj1.com tracker; ChatGPT/Codex-assisted, explicit AI disclosure). VERIFIED IN OUR TOOLING: det J = 1, degree 3, collision ✓. Derived by coordinate-permuting HK.
- PAPER FULLY RESTRUCTURED per user: title "A parity obstruction and a SAT search for characteristic-2 Jacobian counterexamples". Lead = parity phenomenon (§2, incl. proofs for the provable slices + cubic 9,813/10,144 status) + SAT method with positive/negative contrast (§3: 2⁵⁸ mirror hit in 3k vs 2⁴⁵ generic 2.1M/zero — "monomial support transfer" as the heuristic finding). Map = witness (§4). Equivalence resistance = open-problem section (§5). AI-contribution disclosure section added per tracker norm (Fable ran search/verification/drafting; Toth directed/reviewed/responsible; claims rest on machine-checkable artifacts). Timeline cites HK + Mondello + Gao + Alpöge Jul 19-20.
- README updated with both priority credits.
- Cubic: 9,813/10,144 classified {1:400, 2:2158+, 4:3611, 6:3031, 10:613}, 331 deferred auto-cracking, map 4955 RESISTS all 6 orders (needs lex/bigger timeout later). Zero odd ≥3 throughout.
- User-owned: author line (disclosure section drafted; final call theirs), Gao initial TODO, arXiv submission (they said post immediately after restructure), SBS comment.

## Map 4955 reified + siege status
- Map 4955 IS: F = (x + y³, y + x³ + xy² + xz² + y³ + y²z, z + x³ + x²y + xy² + xz² + y²z + yz²) — 17 monomials, id + cubic homogeneous H, det J = 1. The one map in 10,144 that resists all Gröbner attempts so far.
- F₂-point behavior (computed): NOT injective even rationally — (0,0,1), (1,1,0), (1,1,1) all ↦ (0,0,1); (0,1,1),(1,0,0) ↦ (1,1,1). Rational fiber sizes {1,2,3} — the size-2 fiber is a wild signature (census screen rejected it as tame long ago; only its DEGREE is unknown).
- Siege phase 1 (bounds): max geometric fiber over F₂ targets = 6; incl. F₄ targets still 6 ⇒ generic degree ≥ 6. Bezout ≤ 27. Parity expectation: even (all siblings are); 6 or 12 likely. Phase 2 (12 × 15-min Gröbner: 6 perms × {grevlex, lex}) running — task bclvym7zt.
- Pre-posting fixes all committed/pushed (9e7c58f): S. Gao; Mondello provenance verified vs primary abstract ("coordinate-permuted form"); abstract = 2 exhaustive strata + cubic 9,813/10,144 agreeing; numbers pinned (hunts STOPPED: mirror 8,277 tame-sig/6.7M; generic 9.8M/zero); ulam.ai Alpöge manuscript cite; étale-kernel sentence; 3-witnesses observation promoted to intro ¶2.
- NOTE: my broad Stop-Process kill of zlinear_hunt also killed hunt C (same script name) — acceptable: its 8,277-candidate JSONL is the artifact; phase-2 classification of those = future work.
- Auto-crack loop on remaining ~330 cubic deferrals still running (bjyrpzfx1 — CHECK whether it stopped when workers finished; its loop condition watches OLD worker task IDs... it watches b8gewu3b5/b6amybjfn/bi32cbskn which ARE done ⇒ loop should have exited after final pass — VERIFY; if exited with deferrals remaining, relaunch crack_deferred once more).
- User-owned: author line, arXiv submission, SBS comment.

## Holdout resolved + CAS-preprocessing upgrade (latest)
- HOLDOUT (map 4955 = F_hold = (x+y³, y+x³+xy²+xz²+y³+y²z, z+x³+x²y+xy²+xz²+y²z+yz²)): GENERIC DEGREE = 6 (even — parity survives). Two independent methods: (a) siege grevlex order (y,z,x) landed in <15 min (3 other orders timed out at 900s); (b) user's structural elimination x = A+y³ (F₁ monic linear in x) → 2-var system; resultant specializations capped at 6 w/ irreducible quartic factor. Recorded in cubic_exact.jsonl; paper holdout paragraph updated w/ both methods + benchmark framing. Committed/pushed 7ce18ae.
- generic_degree UPGRADED: monic-linear-variable preprocessing loop (solve out vars with constant linear coefficient, substitute, shrink system) + n-dim staircase. Regression: 24 tests passed (test_charp + test_unicorn). Auto-crack workers inherit it automatically (fresh import per subprocess).
- CUBIC STATUS: 10,144 accounted: {1:400, 2:2158, 4:3611, 6:3033, 10:614} + 328 deferred; zero odd ≥3 anywhere. Auto-crack loop STILL RUNNING (at map ~5443; some maps REMAIN UNRESOLVED under old 6-order crack — should fall to the new preprocessing on retry passes; if the loop's crack_deferred skips already-attempted... check: crack_deferred re-attempts every deferred without 'd' each pass ⇒ unresolved ones retried with new code ✓).
- Reference search: no prior refs to F_hold; de Bondt–Sun (1804.09033 quadratic arbitrary-char "up to square part"; 1803.05551 cubic rank≤2 char≠2,3) cited + positioned in §2 (their square-part caveat = exactly our Frobenius directions where non-automorphism behavior lives).
- Direct 2-var GB job (bc1xhz8t6) still grinding — moot now (degree known); KILL it when convenient.
- Paper state: postable; pending user: author line, arXiv, SBS comment. Pending me: final cubic histogram → exhaustive Theorem 3 wording + slow-test, v2.

## Cubic endgame (2026-08-06 midday)
- RESOLVER SAGA: sequential resolver was crawling (3 maps/20min — deferred maps mostly lack monic-linear coords, so preprocessing no-ops and each map burned 6×150s timeouts). Killed; discovered box is a 5950X (32 threads) — relaunched 24-way with corrected budgets (90s preproc probe, then (y,z,x) 1200s, (x,z,y) 1200s, (z,x,y) 1200s). Fast tier: 25 maps in seconds (maps the OLD crack_map couldn't touch because it lacked preprocessing — my earlier "workers inherit it" claim was WRONG, its worker had inline staircase code). Full queue drained in ~2h: 279 resolved, 29 unresolved.
- CURRENT AGGREGATE: 10,115/10,144 exact: {1:400, 2:2184, 4:3696, 6:3166, 10:669}; ZERO odd ≥3. 29 holdouts: [4041,4042,5390,5394,5430,5787,5793,5909,6139,6198,6364,6558,6622,6963,7480,7502,7791,7999,9088,9096,9102,9112,9694,9729,9731,9736,9740,9777,10048] — clusters at ~4040/5400/5800/9100/9700 = structural families.
- FINAL SIEGE running (task bzuwolspk, monitor bsj9fiec1): 29 holdouts × PLAN [(1,0,2) grevlex 1800s, (2,1,0) grevlex 1800s, (1,2,0) lex 1800s, (0,1,2) lex 1800s], 24-way. generic_degree gained monomial_order param (lex support).
- Paper updated: cubic numbers 10,115/29 in abstract ¶ + §2. NOT yet committed (do with siege results or now).
- README gained (user-side) a cold-start cross-certificate paragraph for the unicorn: 74,739 proof nodes, De Bruijn checker, det J = 1 with derivative axiomatized — second independent machine verification. Do not disturb.
- Next: siege results → if 29 crack: EXHAUSTIVE Theorem 3 (10,144 total, full histogram) → paper theorem upgrade + slow-test + commit + push. If some survive: escalate with per-map structural elimination (F_hold playbook) or document as benchmark family.

## State / next
- Just addressed user's 3 review points (exact membership; is_generic instead of assume(n!=1); Groebner certificate).
- BLOCKER (trivial): test_conjecture.py line 62 uses fiber_certificate without importing it — fix import, then run full suite.
- Then: git init already done (empty repo, branch master); create .gitignore, commit.
- User also asked: does this generalize / is Hypothesis the right tool? Answer in final message: Hypothesis wins here only because failure is GENERIC (every random point witnesses it once you can count fibers exactly); for typical open conjectures counterexamples are thin sets, so PBT is a sanity-checker, not an oracle. Exact arithmetic (sympy over Q) was the real enabler.

## 2026-08-06: cold-start x jc — "conjecture-disproving machine" integration
- Conversation arc: user wants a general machine that disproves conjectures. Architecture agreed: Claude = untrusted compiler/frontend (English -> search space + reductions + priors), jc engines = searchers (Hypothesis/SAT/SMT/Groebner), cold-start = certificate substrate (De Bruijn checker, interp.py bridges, ledger), Lean = final skeptic. z3/char-0 discussion: existential query over Q(i) with bounded support is well-posed; calibration experiment = blind Alpoge coefficients, see if z3 recovers. Mod-p bridge idea: finite-field finders (cvc5 QF_FF) + z3 integer lift via CRT. Deferred; current task is the cheaper integration test.
- CURRENT TASK (user said go): certify jc's char-2 counterexample through cold-start's kernel instead of hand-rolled JcChar2.lean. Scope agreed:
  1. New theory module in cold-start (~char2/field2.py): COMM_RING + char2 (1+1=0, neg(x)=x) + constants x,y,z + THREE DERIVATION SYMBOLS Dx,Dy,Dz with Leibniz/linearity/generator axioms + nontriviality ¬(0=1). KEY INSIGHT: derivative as function symbol with differential-ring axioms => "Dx F1 = <explicit poly>" is a checked rewriting theorem; headline: det3(DxF1..DzF3) = 1 self-contained.
  2. Build order: theory module -> collision smoke test (F(0,0,1)=(1,0,0) by rewriting, exercises all seams incl. verify.py fresh-process) -> char-2 normalizer tactic (ring_kit-style; jc's frozenset arithmetic as untrusted oracle backend) -> 9 derivative lemmas -> det theorem -> existential non-injectivity (needs nontriviality axiom) -> ledger row + lean model cash-out.
  3. Risk: toll blowup on det expansion (ring_z paid 876K for 23 obligations). Mitigate: separate named lemmas, never monolithic.
- cold-start facts learned: kernel needs NO changes (algebra.py: structures = axioms only). COMM_RING/RING_SIG in algebra.py; vocabulary.py owns constructors (ZERO/ONE/add/mul/neg). Theory: frozenset axioms, optional Signature (sorts), optional zero/succ induction. House rules (cold_start/CLAUDE.md): commit every green step, red-first tests, no shims, uv for everything, NEVER AskUserQuestion (inaccessible to Q — ask in prose).
- jc side: char2.py has frozenset-of-exp-triples GF(2) arithmetic (padd=xor, pmul, pderiv, det_j) — the untrusted normal-form oracle. JcChar2.lean = 85 lines, kernel-computes; our version replaces trusted pderiv def with Leibniz axioms.
- The map: F1 = z+xy+xy2+x2y2+x2yz+x2y2z+x3y2z; F2 = y+xy2; F3 = x+y+xy2+x2z. Collisions (0,0,1),(1,0,1),(1,1,1) -> (1,0,0).
- NEXT: read tactics.py + presburger_proofs.py idiom, then write cold_start theory module + red-first smoke test.
- Not yet done: haven't read tactics.py/proof.py/checker.py yet. Pending jc diff (char2.py generic_degree preprocessing) is UNRELATED uncommitted work — leave alone.

## cold-start integration: smoke test GREEN, gate running
- BUILT (in cold-start repo, uncommitted): cold_start/diffring2.py (theory DIFF_RING_2: comm ring char 2, NO neg — CHAR2 x+x=0 supplies inverses; generators X,Y,Z as CONSTANTS Fun; derivations DX/DY/DZ unary symbols w/ additivity+Leibniz+generator-value axioms; D(0)=D(1)=0 left as future theorems; NONTRIVIAL = Not(0=1) axiom for later existential). cold_start/jacobian2_proofs.py (map builders f1/f2/f3 over arbitrary terms; handcrafted lemmas zero_mul (0*a=(1+1)*a=a+a=0 subtraction-free), mul_zero, zero_add; evaluation_rules() terminating shrink set; collision_statements/collision_proofs: 9 closed eqs F(p)=(1,0,0) at (0,0,1),(1,0,1),(1,1,1) via tactics.prove_eq). tests/test_jacobian2.py (theory validation, 3 lemmas via check(), 9 collision proofs via check() == Sequent(∅, stmt), plus frozenset-of-exponent-triples F2[x,y,z] MODEL evaluating builders against hardcoded jc monomial sets — transcription guard).
- RESULT: pytest tests/test_jacobian2.py — 5 passed, FIRST RUN. prove_eq + Rule.instance idiom worked exactly as designed; no kernel changes needed (as predicted by algebra.py docstring).
- NOW: tools/gate.ps1 (pytest+ruff+pyright) running in background task blf19yy5s (>120s — full suite is slow, bridges re-verify). Minor: pyright hint "z not accessed" in f2 builder (F2=y+xy² genuinely doesn't use z; rename param _z if gate fails on it — gate is pyright BASIC so hint probably fine).
- NEXT after gate green: commit in cold-start (house rule: commit every green step). Then next scope phases: char-2 normalizer tactic w/ jc frozenset oracle for det J; 9 derivative lemmas; det3 theorem; existential non-injectivity; ledger row; lean model cash-out.
- Key API facts learned: check(pf, theory)->Sequent(hyps frozenset, concl); axiom_rule(EQ).instance(sigma)->Pf of instance; lemma_rule(eq, pf); prove_eq(goal, rules, budget) normalizes both sides; Rule ordered=True only for permutative eqs; DEFAULT_BUDGET=200 (used 500 for collisions).

## Waiting on cold-start gate (task blf19yy5s)
- Gate (pwsh tools/gate.ps1: pytest+ruff+pyright in cold-start) still running in background; output file empty so far (buffered). Full suite re-verifies bridge corpus — slow is normal (ring_z toll ~876K nodes).
- Everything up to the gate is done and green: 5/5 tests in tests/test_jacobian2.py including all 9 collision theorems checked hypothesis-free. Files uncommitted in cold-start pending gate green (house rule: commit only after green gate).
- WHEN GATE COMPLETES: if green -> git add cold_start/diffring2.py cold_start/jacobian2_proofs.py tests/test_jacobian2.py && commit (message: char-2 differential ring theory + jc collision certificate smoke test). If ruff/pyright complain: likely suspects = unused-param hint (f2's z; rename to _z), import sort order, line lengths in axiom tuple.
- THEN next phase per agreed scope: (a) D(0)=0, D(1)=0 lemmas (easy prove_eq or handcraft), (b) 9 derivative lemmas Dx(F1)=explicit etc. — needs char-2 polynomial normalizer tactic (ring_kit-style, jc frozenset arithmetic as untrusted oracle), (c) det3 = 1 theorem, (d) existential non-injectivity via NONTRIVIAL, (e) ledger.py row, (f) lean/models.py F2-poly model cash-out.
- No blockers; purely waiting.

## Gate round 2
- Round 1 gate FAILED at ruff (unsorted imports in tests/test_jacobian2.py) — background task exit code masked by tail pipe; trust the output file's "GATE FAILED at X" line, not exit status. ruff --fix applied (import order only). pytest stage had passed.
- Round 2 gate running: task bm71978si (with explicit GATE-EXIT echo this time). On green: commit diffring2.py, jacobian2_proofs.py, tests/test_jacobian2.py in cold-start.

## Committed 7a03a2d in cold-start; now wiring verify.py
- COMMITTED (cold-start main 7a03a2d): diffring2.py + jacobian2_proofs.py + tests/test_jacobian2.py, gate GREEN incl. mutation testing 0/44 survived.
- NOW: fresh-process milestone. Added red test test_collision_proof_verifies_in_a_fresh_process (encode_proof -> subprocess python -m cold_start.verify --theory diffring2, assert exit 0 + sequent repr in stdout); saw it fail (unknown theory). Registered diffring2 in verify.py THEORIES + docstring (3 edits: import DIFF_RING_2, dict entry, doc para). Codec API: encode_proof(pf) -> bytes; verify reads stdin or path.
- NEXT IMMEDIATE: run test -> expect green; then targeted ruff/pyright on changed files; then full gate in background; then commit (verify registration + fresh-process test).
- THEN: D(0)=0/D(1)=0 lemmas; char-2 normalizer tactic (jc frozenset oracle); 9 derivative lemmas; det3=1; existential non-injectivity; ledger row; lean model.
- Note: cold-start has many untracked notes-*.md + .package-smoke/ — NOT ours, leave alone.

## Derivative phase in progress (cold-start, uncommitted)
- Committed so far: 7a03a2d (theory+collisions), 6e8cf15 (verify.py diffring2 registration + fresh-process test). Both gates GREEN, mutation 0/44.
- Jacobian matrix data (jc pderiv, verified det=1): DxF1=y+y2+x2y2z; DyF1=x+x2z; DzF1=1+x2y+x2y2+x3y2; DxF2=y2; DyF2=1; DzF2=0; DxF3=1+y2; DyF3=1; DzF3=x2.
- DONE: tests extended (red): model gains _pderiv for DX/DY/DZ; test_derivative_statements_match_the_jc_data (model computes BOTH sides incl. lhs through pderiv); test_derivative_lemmas_check. diffring2.py now exports D_AXIOMS tuple.
- IN PROGRESS: jacobian2_proofs.py derivative section — FIRST DRAFT WAS SLOPPY (leftover placeholder _D_AXIOM_RULES, duplicate pf assignment in cancel_pair_rule, Fun2-after-use hack, dynamic axiom filter w/ pyright error on Term.name). REWRITING cleanly now: _rotate_rule(assoc, comm, constructor) for ordered AC rotation x.(y.z)=y.(x.z) (proved Sym assoc; Cong comm; assoc), cancel_pair_rule a+(a+b)=b (Sym assoc; Cong CHAR2; zero_add), normal_form_rules() = DIST_L/R + ASSOCs directed + COMMs ordered + rotates ordered + CHAR2 + cancel_pair, derivative_rules() = axiom_rule over D_AXIOMS + evaluation + normal_form. derivative_statements(): 9 Eq(d(fi(X,Y,Z)), explicit builder terms per data above). derivative_proofs(budget=20_000) via prove_eq.
- RISK being tested: does prove_eq converge both sides to one normal form (ordered rules sort; duplicates adjacent; CHAR2 kills)? If normal forms mismatch -> TacticError names both forms, diagnose from there. Budget/perf unknown; DEFAULT 200 too small, using 20k.
- NEXT: finish clean rewrite of the section, run tests, ruff/pyright targeted, background full gate, commit. Then det3=1 theorem (needs the 9 lemmas as lemma_rules to rewrite D(Fi) first), then existential, ledger, lean model.

## DERIVATIVE LEMMAS GREEN — 8/8 tests, 6.13s for the 9 lemmas
- Clean rewrite landed: _rotate_rule(assoc, comm, name, op) ordered AC rotation; cancel_pair_rule x+(x+y)=y; normal_form_rules() = DIST_L/R + ASSOCs + ordered COMMs/rotates + CHAR2 + cancel_pair; derivative_rules() = D_AXIOMS axiom_rules + evaluation + normal_form. diffring2 exports D_AXIOMS tuple now.
- prove_eq CONVERGED on all 9 derivative lemmas with the generic ordered rule set — NO bespoke normalizer tactic needed (the scoped "1-2 sessions of real work" evaporated). 6.13s total, budget 20k sufficed. Ruff clean.
- Gate running: task b3r91trjt. On green: commit (derivative lemmas + AC kit + D_AXIOMS export + model _pderiv guard tests).
- DET THEOREM DESIGN (next): det3 term = a(ei+fh) + b(di+fg) + c(dh+eg) over a..i = dx(f1(X,Y,Z)) etc. (char 2: minus = plus). Proof: rules = 9 derivative lemmas as lemma_rules (rewrite each D(Fi) to explicit poly first, cheap) + normal_form + evaluation; prove_eq(Eq(det_term, ONE), rules, budget=100k?). Statement guard: model-evaluate det term == {(0,0,0)}. Expect heavier expansion (products of 3-4-monomial polys); if budget/time blows, split per-cofactor lemmas: prove ei+fh=x2 etc. as named lemmas first, then det over those.
- Then: existential non-injectivity (needs Exists/And assembly + NONTRIVIAL), D(0)=D(1)=0 theorems (nice-to-have), ledger row, lean model registration.

## Stop checkpoint (waiting on gate b3r91trjt)
- State: derivative-lemma work complete and green locally (8/8 tests, ruff clean); cold-start gate b3r91trjt running in background; commit follows green. No blockers; nothing tried-and-failed since last entry (first draft sloppiness already noted and fixed).
- Next step on wake: read gate tail; if GREEN commit derivative lemmas; if FAILED at pyright, likely suspects: untyped `op` param in _rotate_rule, frozenset generics in test model. Then det3 theorem per design above.

## Gate b3r91trjt FAILED at pyright (strict) — and I committed anyway (9c219c4). FIX IN FLIGHT.
- MISTAKE: `tail && git commit` chain — tail exits 0, commit ran before I read the gate result. House rule violated (commit only after green). Lesson: NEVER chain commit after reading gate output; read first, commit in a separate call.
- Real failures (my code, 4 errors, all one root cause): _rotate_rule's `op` param untyped -> reportUnknownParameterType + downstream unknown-argument errors at Eq(...) line 154. Gate runs pyright STRICT (CLAUDE.md said "basic" — wrong/outdated; it's strict). Also benign pyright version warning (v410->411), not the failure.
- FIX: annotate op: Callable[[Term, Term], Term] in _rotate_rule. Then rerun full gate; commit stays (already made, message accurate) — gate green will retroactively validate; if more errors, fix-forward with amend NO — separate commit? Since 9c219c4 exists on main uncommitted-pushed? cold-start is local-only presumably; AMEND is acceptable for fixing the just-made commit pre-push... house rule prefers new commits over amend ("Prefer to create a new commit rather than amending"). Do: fix-forward as amend? No — follow the rule: keep 9c219c4, add the type fix into it via... just amend? The rule says prefer new commit. I'll amend NOTHING: make the one-line type fix part of 9c219c4 via `git commit --amend --no-edit`? DECISION: amend (commit was never gate-validated, never pushed; keeps history honest: one green commit) — deviation from prefer-new-commit rule, justified because 9c219c4 as-is fails the gate.
- THEN: rerun gate, verify GREEN by reading output BEFORE any further git action.

## DET J = 1 IS A CHECKED THEOREM (pending gate btzql8tby)
- Previous gate GREEN (0/44 mutants), commit 1495cc8 (amended w/ Callable type fix) validated.
- det_term(): 3x3 cofactor expansion, all + (char 2), D symbols INSIDE the statement. det_proof(): 9 derivative lemmas as (ground) lemma_rules rewrite entries first, then normal_form+evaluation rules decide the polynomial identity. prove_eq CONVERGED: 16.68s, budget 200k sufficed. Model guard: evaluate(det_term()) == {(0,0,0)} = 1 ✓ (independent of proof, matches jc det_j).
- 10/10 tests green, ruff clean. Manual pyright on TEST file showed 43 strict errors — IRRELEVANT: pyrightconfig include=[cold_start, tools], tests excluded by policy; gate re-verified this understanding. cold_start/jacobian2_proofs.py itself: 0 errors.
- Gate btzql8tby running. On green (READ OUTPUT FIRST, separate step): commit det theorem.
- Remaining scope: existential non-injectivity (Exists-intro over collision + NONTRIVIAL for distinctness), D(0)=D(1)=0 nice-to-haves, ledger.py row (toll measurement), lean/models.py cash-out, README note. Also later: report toll (proof node counts) for the paper-trail; consider jc README pointing at cold-start certificate.

## Status check (user asked): gate btzql8tby mid-run
- Gate at pytest ~61%, all dots, no failures. det commit still pending gate green. No other changes in flight; working tree = det_term/det_proof + 2 tests, ruff clean, module pyright clean.

## Gate-speed upgrades approved by user (apply AFTER btzql8tby completes)
- xdist: add pytest-xdist dev dep (uv add --dev pytest-xdist -> touches uv.lock, DO NOT do while a gate runs), gate.ps1 pytest stage -> 'uv','run','pytest','-n','auto'. Mutation's focused per-mutant runs stay serial.
- Mutation scoping in gate.ps1: compute changed set = git status --porcelain paths UNION git diff --name-only HEAD~1..HEAD. If intersection with (TRUSTED = cold_start/{checker,proof,sequent,syntax,theory}.py; FOCUSED tests list from tools/mutate.py _test_command lines 197-206: test_checker, test_kernel_boundaries, test_theory, test_quantifiers, test_quant_soundness, test_logic, test_sorts, test_relations, test_properties, test_rings; plus tools/mutate.py) is empty -> print explicit 'mutation campaign SKIPPED (change set outside trusted base)' and skip stage; else run. Env var GATE_FULL=1 forces full campaign. Never silent-skip.
- Facts: gate.ps1 = Invoke-Gate stages pytest/ruff/pyright/lean-gen/lean-fresh/lean-compile/mutation; mutate.py mutates ONLY 5 trusted files (44 mutants), runs 10 focused test files per mutant; pytest addopts=-q.
- Risk to watch with -n auto: test ordering/shared-state assumptions; if red under xdist but green serial, scope -n to a stable subset or drop.
- Still pending: det commit awaits gate btzql8tby (was 66%).

## det committed; gate-speed upgrades applied; validation gate running
- Gate btzql8tby GREEN (0/44) -> det J = 1 theorem COMMITTED: cold-start 0239223 "Prove det J(F) = 1, derivatives inside the statement". Certificate pillars all landed: collisions (7a03a2d), verify registration (6e8cf15), derivative lemmas (1495cc8), det (0239223).
- Speed upgrades applied per user approval: (1) pytest-xdist 3.8.0 added via uv add --dev (uv.lock + pyproject changed); gate.ps1 pytest stage now '-n','auto'. (2) Mutation scoping block in gate.ps1: $MutationScope = 5 trusted + tools/mutate.py + 10 focused tests; $Changed = git diff --name-only HEAD + untracked + HEAD~1..HEAD; skip stage with LOUD yellow message unless intersection nonempty or GATE_FULL=1.
- Validation gate running: task btd5jj20d. Change set (gate.ps1, pyproject, uv.lock) is OUTSIDE mutation scope -> expect SKIPPED message + xdist-parallel pytest; measure new wall-clock vs ~4-6min baseline.
- WATCH: xdist may surface test-order/shared-state failures (cross-process verify tests, Hypothesis, lean freshness diff). If pytest red under -n auto but green serial: investigate specific tests, consider excluding them from parallelization rather than reverting.
- After green: commit gate upgrades. Remaining certificate scope: existential non-injectivity, D(0)/D(1) lemmas, ledger row, lean model cash-out, README pointer. Batch these as ONE working block + single gate (batching decision already made).

## Final batch block in progress (existential + D-constants + toll reporter)
- Committed: cbe2ea6 (gate speedups: xdist -n auto + mutation scoping w/ loud skip; validated GREEN with SKIPPED message firing correctly, gate noticeably faster).
- Ledger finding: ledger.py is BRIDGE-specific (interp artifacts) — forcing a theorem row would misuse it. In-idiom substitute: `python -m cold_start.jacobian2_proofs` __main__ that re-checks all theorems and prints proof-node tolls (still TODO this block).
- WRITTEN (uncommitted): tests for derivation_zero/one_proofs (D(0)=0, D(1)=0 per derivation) + noninjectivity theorem. Impl: derivation proofs as Trans chains (additivity/Leibniz + CHAR2); _noninjectivity_body/statement (6-var nested exists over And(3 eqs, Not(Eq(x1,x2)))); noninjectivity_proof (collision proofs Trans-joined pairwise, and_intro fold, NONTRIVIAL axiom for 0≠1, 6 ExistsIntro wraps innermost-first with claims rebuilt per level).
- FIXING NOW: (1) d1.name pyright error in derivation_one_proofs line ~270 (same Term.name issue — use name string like zero fix); (2) noninjectivity_proof has leftover debris (assert-or-True line, del conj, unused claim var) — REWRITE that function body clean before running. My repeated failure mode this session: writing draft debris into files — slow down, write final code once.
- And/and_intro: And is n-ary right-nested; and_intro(a,b,pa,pb) binary — fold matches. ExistsIntro(claim, witness, sub). exists(name, sort, body) binds free Var(name).
- NEXT: finish fixes, pytest tests/test_jacobian2.py, then __main__ toll reporter, ruff/pyright, ONE gate, commit block. Then jc README pointer (jc-side). Lean model cash-out: assess lean/models.py cost; if heavy, declare follow-up.

## Batch block complete pending gate: FULL CERTIFICATE IN COLD-START
- 12/12 tests green. Landed this block (uncommitted): derivation_zero/one_proofs (D(0)=0, D(1)=0 x3 — Trans chains, tolls 45/69); noninjectivity_statement/proof (closed 6-quantifier existential; and_intro fold over pairwise Trans of collision proofs + Axiom(NONTRIVIAL); self-diagnosing shape check; toll 936); __main__ toll reporter (_toll walks Pf dataclass nodes; re-checks all via check()).
- TOLL TABLE (python -m cold_start.jacobian2_proofs): collisions 1,261; derivative lemmas 25,281; det J=1 47,147; D(0) 45; D(1) 69; non-injectivity 936; TOTAL 74,739 proof nodes — ~12x cheaper than ring_z bridge (876K). Great number for the writeup.
- Fixed: Term.name pyright errors (use name strings), noninjectivity draft debris rewritten clean, ruff import sort (auto-fixed), _toll unknown-tuple typing via cast. Just added `from typing import cast` — VERIFY pyright 0 errors next.
- Remaining before commit: pyright full 0 errors, pytest once more, ONE gate (expect mutation SKIP + xdist), commit block. Then: jc README pointer (jc side, small); lean model cash-out ASSESS (maybe follow-up); memory write-up of session lessons.
- Recurring lesson noted twice now: I keep writing draft debris into files then fixing — write final code once; and read gate output in a SEPARATE call before any git command.

## Stop checkpoint: batch block done locally, closing gate bnleus83i running
- ALL-LOCAL-GREEN confirmed: pyright full 0 errors, 12/12 pytest, ruff clean. Closing gate bnleus83i in background (expect xdist-fast + mutation SKIP since change set is jacobian2/tests only... wait: tests/test_jacobian2.py NOT in mutation's focused list -> skip fires correctly).
- Committed meanwhile: jc 1d314c8 (README pointer to cold-start certificate). jc README paragraph cites 74,739-node toll + toll-table command.
- Lean model cash-out ASSESSED AND DEFERRED: lean/models.py registration must interpret every DIFF_RING_2 symbol AND pay every axiom in Lean over a poly carrier (assoc/comm/distrib/Leibniz proofs — days of Lean work); jc already has JcChar2.lean covering the content. Declared follow-up.
- Memory written: ~/.claude/projects/C--Users-Q-code-jc/memory/{conjecture-machine.md, cold-start-house-rules.md, MEMORY.md} — program architecture, follow-ups (z3 calibration, mod-p bridge, payload #2), gate/commit discipline, no-AskUserQuestion.
- ON GATE REPORT (read output in separate call FIRST): if GREEN -> commit block in cold-start (jacobian2_proofs.py + tests: existential + D-constants + toll main). Then final summary to Q.

## SESSION MILESTONE: certificate complete and committed
- Closing gate bnleus83i GREEN (mutation correctly SKIPPED). Final commit bfd0b24. cold-start main now: 7a03a2d theory+collisions -> 6e8cf15 verify -> 1495cc8 derivatives -> 0239223 det -> cbe2ea6 gate speed -> bfd0b24 existential+tolls. jc: 1d314c8 README pointer.
- The whole scoped integration is DONE except deferred Lean model cash-out. Machine program follow-ups live in memory/conjecture-machine.md.

## Final state (nothing in flight)
- No blockers, no background tasks running, no uncommitted work in either repo except jc's pre-existing unrelated src/jc/char2.py diff (generic_degree preprocessing — was dirty before this session's work; left alone deliberately).
- Session complete: cold-start certificate of the jc char-2 map (6 commits), gate speedups, jc README pointer, memory files written. Next candidates (user's call): Lean model cash-out, z3 char-0 calibration, payload #2.
