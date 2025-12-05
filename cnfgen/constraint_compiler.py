"""Base CNF compiler code."""

from pysat.solvers import Solver
from pysat.formula import PYSAT_FALSE
from pysat.formula import Atom, Or, And, Neg, Equals, XOr, Implies, CNF
from pysat.process import Processor
from cnfgen.types import *
from cnfgen import sbva

class ConstraintHandle:
    """Class for storing constraints and creating new variables."""

    def __init__(self):
        self.num_vars = 0
        # List of formulas that will be and'd together in the end
        self.formulas = []
        self.solver = Solver(name='Minisat22')
        self.processor = Processor()
        self.cnf = None
        self.preprocessed = False
        self.solution = None

    def add_var(self):
        self.num_vars += 1
        new_var = Atom(f"var-{self.num_vars}")
        # The atom needs to be clausified so that we can access the name
        # property which gives the integer value
        new_var.clausify()
        return new_var

    def add_formula(self, formula):
        """Add a formula (higher level than a clause)."""
        self.formulas.append(formula)

    def solve(self):
        if self.cnf is None:
            self.get_cnf()
        self.solver.append_formula(self.cnf)
        return self.solver.solve()

    @property
    def model(self):
        """Returns negative if False, positive if True."""
        if not self.preprocessed:
            return self.solver.get_model()
        else:
            return processor.restore(self.solver.get_model())
        
    def get_cnf(self):
        """Get a CNF formula for the saved constraints."""
        cnf = CNF()
        for formula in self.formulas:
            formula.clausify()
            for clause in formula:
                cnf.append(clause)
        self.cnf = cnf
        return cnf

    def sbva(self):
        """Apply an optimization produced by SBVA."""
        cnf = self.get_cnf()

    def save(self, fname):
        """Save the CNF data in DIMACS format."""
        cnf = self.get_cnf()
        cnf.to_file(fname)

    def preprocess(self, rounds = 1, block = False, cover = False, condition = False, 
            decompose = True, elim = True, probe = True, probehbr = True,
            subsume = True, vivify = True, freeze = []):
        self.processor.append_formula(self.cnf)
        self.processor.process(rounds, block, cover, condition, decompose, elim,
                probe, probehbr, subsume, vivify, freeze)


class Bool:
    def __init__(self, handle):
        self.var = handle.add_var()

    def eval(self, handle):
        assert handle.model is not None
        return handle.model[self.var.name - 1]
    def is_assigned(self, literals):
        if self.var.name in literals or -self.var.name in literals:
            return True
        else:
            return False

class Enum:
    def __init__(self, handle, values):
        self.values = values
        self.vars_ = [handle.add_var() for _ in values]
        # For each combo of vars, only one can be true
        # At least one is true
        at_least_one = Or(*self.vars_)
        # At most one is true
        clauses = []
        for var_i in self.vars_:
            for var_j in self.vars_:
                # TODO: Remove redundant clauses
                if var_i == var_j:
                    continue
                clauses.append(Or(Neg(var_i), Neg(var_j)))
        handle.add_formula(And(at_least_one, *clauses))

    def eval(self, handle):
        assert handle.model is not None
        for var, value in zip(self.vars_, self.values):
            if handle.model[var.name - 1] > 0:
                return value
        return None

    def is_assigned(self, literals):
        for lit in self.vars_:
            if lit.name in literals:
                return True
        return False

class INT:
    def __init__(self, handle, bitwidth):
        # add 32 variables for each bit
        self.bitwidth = bitwidth
        self.vars_ = [handle.add_var() for _ in range(bitwidth)]
        self.forced = False
    def assign(self, handle, value):
        for i, var in enumerate(self.vars_):
            bitval = (value >> i) % 2
            if bitval == 0:
                handle.add_formula(Neg(var))
            else:
                handle.add_formula(var)
        self.forced = True
    def eval(self, handle):
        assert handle.model is not None
        res = 0
        for i, var in enumerate(self.vars_):
            if handle.model[var.name - 1] > 0:
                res = res + (1 << i)
        return res

class ConstraintCompiler:
    """Base CNF compiler code."""

    def __init__(self):
        self.handle = ConstraintHandle()

    def create_vars(self, num, type_, values=None):
        match type_:
            case VarType.BOOL:
                new_vars = []
                for i in range(num):
                    new_vars.append(Bool(self.handle))
                return new_vars
            case VarType.ENUM:
                assert values is not None
                new_vars = []
                for i in range(num):
                    new_vars.append(Enum(self.handle, values))
                return new_vars
            case VarType.INT:
                assert type(values) is int
                new_vars = []
                for i in range(num):
                    new_vars.append(INT(self.handle, values))
                return new_vars

    def add_constraint(self, vars_: list, type_, k=None):
        #assert all(type(var) == type(vars_[0]) for var in vars_), "all vars must be same type"
        match type_:
            case ConstraintType.OR:
                self.handle.add_formula(Or(*[var.var for var in vars_]))
            case ConstraintType.DIFFERENT:
                assert all(var.values == vars_[0].values for var in vars_), "all values must be same enum type"
                for var_i in vars_:
                    for var_j in vars_:
                        if var_i == var_j:
                            continue
                        for intl_var_a, intl_var_b in zip(var_i.vars_, var_j.vars_):
                            # not(A) OR not(B)
                            self.handle.add_formula(Or(Neg(intl_var_a), Neg(intl_var_b)))
            case ConstraintType.AND:
                self.handle.add_formula(Or(*[var.var for var in vars_]))
            case ConstraintType.NAND:
                self.handle.add_formula(Or(*[Neg(var.var) for var in vars_]))
            case ConstraintType.ATMOST:
                assert k is not None
                # degenerate case
                if k < len(vars_):
                    # Naive approach to implementing at-most-k
                    used = set()
                    # Current k variable indices
                    cur_vars = list(range(k + 1))
                    formulas = []
                    for pos in range(k + 1):
                        for i in range(len(vars_)):
                            tmp_vars = cur_vars[:]
                            tmp_vars[pos] = i
                            tmp_vars.sort()
                            if tuple(tmp_vars) in used or len(set(tmp_vars)) != (k + 1):
                                continue
                            used.add(tuple(tmp_vars))
                            # If variable in this set are true, then all others must be false
                            self.handle.add_formula(Neg(And(*[vars_[j].var for j in tmp_vars])))
                            cur_vars = tmp_vars
            # INT contraints
            case ConstraintType.BIT_AND:
                assert len(vars_) == 3
                bi = vars_[1].var
                for ai, ci in zip(vars_[0].vars_, vars_[2].vars_):
                    self.handle.add_formula(Equals(And(ai, bi), ci))
            case ConstraintType.EQ:
                # TODO
                # check for int type
                biteq = []
                for i, var_i in enumerate(vars_):
                    for j, var_j in enumerate(vars_):
                        if i >= j:
                            continue
                        for intl_var_a, intl_var_b in zip(var_i.vars_, var_j.vars_):
                            if intl_var_a.name > intl_var_b.name:
                                continue
                            biteq.append(Equals(intl_var_a, intl_var_b))
                self.handle.add_formula(And(*biteq))
            case ConstraintType.NEQ:
                # check for int type
                bitneq = []
                for i, var_i in enumerate(vars_):
                    for j, var_j in enumerate(vars_):
                        if i >= j:
                            continue
                        for intl_var_a, intl_var_b in zip(var_i.vars_, var_j.vars_):
                            if intl_var_a.name > intl_var_b.name:
                                continue
                            bitneq.append(Neg(Equals(intl_var_a, intl_var_b)))
                self.handle.add_formula(Or(*bitneq))
            case ConstraintType.SUM:
                # TODO extend to more than 2 summands
                # must have 3 operands
                # enforce same bitwidth
                assert len(vars_) == 3
                # implement ripple carry adder
                carry = [PYSAT_FALSE]
                sums = []
                
                # c = a + b
                for ai, bi, ci in zip(vars_[0].vars_, vars_[1].vars_, vars_[2].vars_):
                    sums.append(Equals(ci, XOr(XOr(ai, bi), carry[-1])))
                    carry.append(Or(And(ai, bi), And(XOr(ai, bi), carry[-1])))
                self.handle.add_formula(And(*sums))
            case ConstraintType.LT:
                assert len(vars_) == 2
                # implement ripple comparator
                carry = [PYSAT_FALSE]

                for ai, bi, in zip(vars_[0].vars_, vars_[1].vars_):
                    carry.append(Or(And(Neg(ai), bi), And(carry[-1], Neg(XOr(ai,bi)))))
                print(carry[-1])
                self.handle.add_formula(carry[-1])

    def add_symmetry(self, vars_: list, type_, k=None):
        assert all(type(var) == type(vars_[0]) for var in vars_), "all vars must be same type"
        match type_:
            case VarType.BOOL:
                # assign variables and propagate until all are assigned
                stack = []
                tried = []
                res, propagated = self.handle.solver.propagate(assumptions=stack)
                if not res:
                    return False

                for idx, var in enumerate(vars_):
                    if not var.is_assigned(propagated):
                        tried.append([var, 0])
                        break

                while tried:
                    var = tried[-1][0]
                    lit_idx = tried[-1][1]

                    if lit_idx >= 2:
                        tried.pop(-1)
                        stack.pop(-1)
                        continue
                    
                    res, propagated = self.handle.solver.propagate(assumptions=stack)
                    allassigned = False

                    # find next untried assignment
                    for i in range(lit_idx, 2):
                        tried[-1][1] = tried[-1][1] + 1
                        if lit_idx < 2:
                            if lit_idx == 0:
                                if -(var.var.name) not in propagated:
                                    stack.append(-var.var.name)
                            elif lit_idx == 1:
                                if (var.var.name) not in propagated:
                                    stack.append(var.var.name)

                            res, propagated = self.handle.solver.propagate(assumptions=stack)
                            if not res:
                                stack.pop(-1)
                                continue
                            for idx, var_ in enumerate(vars_):
                                if not var_.is_assigned(propagated):
                                    tried.append([var_, 0])
                                    break
                            allassigned = True
                            break
                    if allassigned:
                        for lit in stack:
                            self.handle.solver.add_clause([lit])
                        return True
                return False

            case VarType.ENUM:
                # assign variables and propagate until all are assigned
                stack = []
                tried = []
                res, propagated = self.handle.solver.propagate(assumptions=stack)
                if not res:
                    return False

                for idx, var in enumerate(vars_):
                    if not var.is_assigned(propagated):
                        tried.append([var, 0])
                        break
                    
                while tried:
                    var = tried[-1][0]
                    lit_idx = tried[-1][1]
                    
                    if lit_idx >= len(k):
                        tried.pop(-1)
                        stack.pop(-1)
                        continue

                    res, propagated = self.handle.solver.propagate(assumptions=stack)
                    allassigned = False

                    # find next untried assignment
                    for i in range(lit_idx, len(k)):
                        tried[-1][1] = tried[-1][1] + 1
                        if -(var.vars_[i].name) not in propagated:
                            stack.append(var.vars_[i].name)
                            res, propagated = self.handle.solver.propagate(assumptions=stack)
                            if not res:
                                stack.pop(-1)
                                continue
                            for idx, var_ in enumerate(vars_):
                                if not var_.is_assigned(propagated):
                                    tried.append([var_, 0])
                                    break
                            allassigned = True
                            break

                    if allassigned:
                        for lit in stack:
                            self.handle.solver.add_clause([lit])
                        return True
                return False

    def eval(self, var):
        return var.eval(self.handle)

    def solve(self):
        return self.handle.solve()

    def output(self, fname):
        self.handle.save(fname)
