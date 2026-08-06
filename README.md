# jc — the Jacobian conjecture, disproved by property-based testing

The Jacobian conjecture (Keller, 1939) asserted that a polynomial map
F: ℂⁿ → ℂⁿ with nonzero constant Jacobian determinant is invertible. In July
2026, Levent Alpöge announced a counterexample in dimension 3 (found in
collaboration with Claude Fable):

    a = (1+xy)³z + y²(1+xy)(4+3xy)
    b = y + 3x(1+xy)²z + 3xy²(4+3xy)
    c = 2x − 3x²y − x³z

It has det J ≡ −2, yet is generically 3-to-1: it factors through
P¹ × Sym²(P¹) → Sym³(P¹), sending (linear factor, quadratic factor) to their
product cubic — and a generic cubic factors that way three times.

This repo states the conjecture as a [Hypothesis](https://hypothesis.readthedocs.io/)
property and lets it be falsified mechanically, with exact arithmetic
throughout (sympy over ℚ; no floats anywhere a claim depends on):

- `src/jc/map.py` — the map and its Jacobian.
- `src/jc/fibers.py` — exact fiber computation: grevlex Gröbner basis per
  target, FGLM conversion to lex, and a completeness certificate — since F is
  étale the fiber ideal is radical, so `dim_ℚ ℚ[x,y,z]/I_t` (counted from the
  Gröbner staircase) equals the exact number of complex preimages.
- `tests/test_conjecture.py` — the conjecture as a property, `xfail(strict=True)`,
  plus a meta-test demanding Hypothesis refute it.
- `tests/test_counterexample.py` — the counterexample's credentials: det J = −2
  symbolically, fibers complete against the certificate, generic fibers of
  exactly 3, and Tao's point (−1/4, 0, 0) where two preimages escape to
  infinity (étale but not proper — precisely how the conjecture fails).

Hypothesis's shrunk witness is lovely: **F(0,0,1) = (1,0,0)**, which is also
the image of **(±i/2, ±3i, −26)**.

```
uv run pytest tests/ -v
```

The plane (n = 2) case remains open.
