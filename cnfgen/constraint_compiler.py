"""Base CNF compiler code."""

from pysat.solvers import Solver
from cnfgen.types import *

class Formula:
    def __init__(self):
        self.num_vars = 0
        self.solver = Solver(name='cadical195')
        self.solver.activate_atmost()
    def add_var(self):
        self.num_vars += 1
        return self.num_vars
    def add_clause(self, clause):
        self.solver.add_clause(clause)
    def solve(self):
        return self.solver.solve()
    @property
    def model(self):
        """Returns negative if False, positive if True."""
        return self.solver.get_model()

class Bool:
    def __init__(self, formula):
        self.vars_ = [formula.add_var()]
    def eval(self, formula):
        if formula.model is None:
            raise VarEvalError("formula is unknown or unsatisfiable")
        return formula.model[self.vars_[0] - 1]

class Enum:
    def __init__(self, formula, values):
        self.values = values
        self.vars_ = [formula.add_var() for _ in values]
        # For each combo of vars, only one can be true
        # At least one is true
        formula.add_clause(self.vars_)
        # At most one is true
        clauses = set()
        for var_i in self.vars_:
            for var_j in self.vars_:
                # TODO: Remove redundant clauses
                if var_i == var_j:
                    continue
                clauses.add((var_i, var_j))
                formula.add_clause([-var_i, -var_j])
    def eval(self, formula):
        assert formula.model is not None
        print(self.vars_)
        for var, value in zip(self.vars_, self.values):
            if formula.model[var - 1] > 0:
                return value
        return None

class ConstraintCompiler:
    """Base CNF compiler code."""

    def __init__(self):
        #TODO
        self.formula = Formula()
        self.vars_ = []

    def create_vars(self, num, type_, values=None):
        match type_:
            case VarType.BOOL:
                new_vars = []
                for i in range(num):
                    new_vars.append(Bool(self.formula))
                self.vars_.extend(new_vars)
                return new_vars
            case VarType.ENUM:
                assert values is not None
                new_vars = []
                for i in range(num):
                    new_vars.append(Enum(self.formula, values))
                self.vars_.extend(new_vars)
                return new_vars

    def add_constraint(self, vars_: list, type_, k=None):
        assert all(type(var) == type(vars_[0]) for var in vars_), "all vars must be same type"
        match type_:
            case ConstraintType.OR:
                clause = []
                for var in vars_:
                    clause.append(var.vars_[0])
                self.formula.add_clause(clause)
            case ConstraintType.ATMOST:
                literals = [var.vars_[0] for var in vars_]
                self.formula.solver.add_atmost(literals, k)
            case ConstraintType.DIFFERENT:
                assert all(var.values == vars_[0].values for var in vars_), "all values must be same enum type"
                for var_i in vars_:
                    for var_j in vars_:
                        if var_i == var_j:
                            continue
                        for intl_var_a, intl_var_b in zip(var_i.vars_, var_j.vars_):
                            # not(A) OR not(B)
                            self.formula.add_clause([-intl_var_a, -intl_var_b])
            case ConstraintType.OR:
                # Assumes we have a binary type
                clause = []
                for var in vars_:
                    clause.extend(var.vars_)
                self.formula.add_clause(clause)
            case ConstraintType.AND:
                clause = []
                for var in vars_:
                    for intl_var in var.vars_:
                        self.formula.add_clause([intl_var])

    def output(self, fname):
        # TODO
        pass

    def solve(self):
        """Run solver."""
        self.solver.solve()
