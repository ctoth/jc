"""Compile det J = 1 over unknown F_2 coefficients to CNF; enumerate models.

Each ANF condition (XOR of AND-terms = rhs) becomes CNF via one Tseitin
auxiliary per distinct AND-term plus a chained XOR encoding. Models are
enumerated with blocking clauses, so an entire structured family (2^40+
maps) is swept exactly: every unit-Jacobian member is produced, none twice.
"""

from pysat.solvers import Cadical195

from jc.anf import TRUE, unit_det_conditions


class Compiler:
    def __init__(self):
        self.ids = {}
        self.clauses = []
        self.term_aux = {}

    def bit(self, name):
        if name not in self.ids:
            self.ids[name] = len(self.ids) + 1
        return self.ids[name]

    def and_term(self, term):
        """Tseitin variable equivalent to the AND of the term's bits."""
        if len(term) == 1:
            return self.bit(next(iter(term)))
        if term not in self.term_aux:
            aux = self.bit(("aux_and", term))
            lits = [self.bit(b) for b in sorted(term)]
            for lit in lits:
                self.clauses.append([-aux, lit])
            self.clauses.append([aux] + [-lit for lit in lits])
            self.term_aux[term] = aux
        return self.term_aux[term]

    def xor_equals(self, lits, rhs):
        """CNF for XOR(lits) = rhs, chained with auxiliaries."""
        if not lits:
            if rhs:
                self.clauses.append([])  # unsatisfiable
            return
        acc = lits[0]
        for lit in lits[1:]:
            aux = self.bit(("aux_xor", len(self.ids)))
            # aux <-> acc XOR lit
            self.clauses.append([-aux, acc, lit])
            self.clauses.append([-aux, -acc, -lit])
            self.clauses.append([aux, -acc, lit])
            self.clauses.append([aux, acc, -lit])
            acc = aux
        self.clauses.append([acc] if rhs else [-acc])

    def add_condition(self, anf, rhs):
        rhs = rhs % 2
        lits = []
        for term in anf:
            if term == TRUE:
                rhs ^= 1
            else:
                lits.append(self.and_term(term))
        self.xor_equals(lits, rhs)


def unconstrained_bits(components, free_bits):
    """Bits that appear in no det-condition (pure Frobenius directions):
    their values never affect det J, so the solver should not enumerate
    over them — sweep them separately after instantiation."""
    used = set()
    for anf, _rhs in unit_det_conditions(components):
        for term in anf:
            used |= term
    return [b for b in free_bits if b not in used]


def enumerate_unit_jacobians(components, free_bits, limit=None, fix_zero=()):
    """Yield assignments (dict bit -> 0/1) making det J(components) = 1.

    `components` are SymPolys over the unknown bits; `free_bits` lists the
    real coefficient bits (auxiliaries are projected out, and blocking
    clauses range over free bits only, so each *map* appears once).
    Bits in `fix_zero` are pinned to 0 (use with unconstrained_bits to
    avoid enumerating det-irrelevant directions).
    """
    comp = Compiler()
    for bit in free_bits:
        comp.bit(bit)
    for anf, rhs in unit_det_conditions(components):
        comp.add_condition(anf, rhs)
    for bit in fix_zero:
        comp.clauses.append([-comp.bit(bit)])

    free_ids = {bit: comp.ids[bit] for bit in free_bits}
    with Cadical195(bootstrap_with=comp.clauses) as solver:
        count = 0
        while solver.solve():
            model = set(solver.get_model())
            assignment = {
                bit: int(free_ids[bit] in model) for bit in free_bits
            }
            yield assignment
            count += 1
            if limit is not None and count >= limit:
                return
            solver.add_clause(
                [(-vid if vid in model else vid) for vid in free_ids.values()]
            )


def instantiate(components, assignment):
    """Fix an assignment: SymPolys -> frozenset-of-exponents maps (jc.char2)."""
    out = []
    for comp in components:
        mono = set()
        for e, anf in comp.terms.items():
            val = 0
            for term in anf:
                val ^= all(assignment.get(b, 0) for b in term)
            if val:
                mono.add(e)
        out.append(frozenset(mono))
    return tuple(out)
