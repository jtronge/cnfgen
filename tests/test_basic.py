import pytest
import cnfgen

@pytest.mark.parametrize("var_count", [1, 10, 100, 200])
def test_or_simple(var_count):
    cnf = cnfgen.ConstraintCompiler()
    vars_ = cnf.create_vars(var_count, cnfgen.VarType.BOOL)
    cnf.add_constraint(vars_, cnfgen.ConstraintType.OR)
    assert cnf.formula.solve()

@pytest.mark.parametrize("var_count", [1, 10, 100, 200])
def test_and_simple(var_count):
    cnf = cnfgen.ConstraintCompiler()
    vars_ = cnf.create_vars(var_count, cnfgen.VarType.BOOL)
    cnf.add_constraint(vars_, cnfgen.ConstraintType.AND)
    assert cnf.formula.solve()

@pytest.mark.parametrize("var_count", [1, 10, 100, 200])
def test_nand_simple(var_count):
    cnf = cnfgen.ConstraintCompiler()
    vars_ = cnf.create_vars(var_count, cnfgen.VarType.BOOL)
    cnf.add_constraint(vars_, cnfgen.ConstraintType.NAND)
    assert cnf.formula.solve()

@pytest.mark.parametrize("var_count,k", [(1, 1), (10, 5), (100, 10), (200, 100)])
def test_atmost_simple(var_count, k):
    cnf = cnfgen.ConstraintCompiler()
    vars_ = cnf.create_vars(var_count, cnfgen.VarType.BOOL)
    cnf.add_constraint(vars_, cnfgen.ConstraintType.ATMOST, k=k)
    assert cnf.formula.solve()
