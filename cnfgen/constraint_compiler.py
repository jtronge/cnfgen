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
    def model(self):
        return self.solver.get_model()

class Bool:
    def __init__(self, formula):
        self.vars_ = [formula.add_var()]
    def eval(self, formula):
        if formula.model == None:
            raise VarEvalError("formula is unknown or unsatisfiable")
        return formula.model[self.vars_[0]]

class ConstraintCompiler:
    """Base CNF compiler code."""

    def __init__(self):
        #TODO
        self.formula = Formula()
        self.vars_ = []

    def create_vars(self, num, type_, values=None):
        #TODO
        if type_ == VarType.BOOL:
            new_vars = []
            for i in range(num):
                new_vars.append(Bool(self.formula))
            self.vars_ = self.vars_ + new_vars
            return new_vars

    def add_constraint(self, vars_: list, type_, k=None):
        # TODO
        if type_ == ConstraintType.OR:
            clause = []
            for var in vars_:
                clause.append(var.vars_[0])
            self.formula.add_clause(clause)
        elif type_ == ConstraintType.ATMOST:
            literals = [var.vars_[0] for var in vars_]
            self.formula.solver.add_atmost(literals, k)



    def output(self, fname):
        # TODO
        pass

    def solve(self):
        """Run solver."""
        self.solver.solve()
