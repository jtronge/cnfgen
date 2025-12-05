import pytest
import cnfgen

def test_knapsack_unsatisfiable():
    
    values = [5,4,3,1]
    weights = [4,3,2,1]

    val_cutoff = 7
    weight_cutoff = 6

    cnf = cnfgen.ConstraintCompiler()

    includes = cnf.create_vars(len(values), cnfgen.VarType.BOOL)
    
    var_weights = cnf.create_vars(len(values), cnfgen.VarType.INT, 4)
    var_values = cnf.create_vars(len(values), cnfgen.VarType.INT, 4)
    var_wcut = cnf.create_vars(1, cnfgen.VarType.INT, 4)
    var_vcut = cnf.create_vars(1, cnfgen.VarType.INT, 4)

    inc_weights = cnf.create_vars(len(values), cnfgen.VarType.INT, 4)
    inc_values = cnf.create_vars(len(values), cnfgen.VarType.INT, 4)

    sum_weights = cnf.create_vars(len(values)-1, cnfgen.VarType.INT, 4)
    sum_values = cnf.create_vars(len(values)-1, cnfgen.VarType.INT, 4)
    
    var_vcut[0].assign(cnf.handle, val_cutoff)
    var_wcut[0].assign(cnf.handle, weight_cutoff)

    for idx in range(len(values)):
        var_values[idx].assign(cnf.handle, values[idx])
        var_weights[idx].assign(cnf.handle, weights[idx])
    
    for idx in range(len(values)):
        cnf.add_constraint([var_values[idx], includes[idx], inc_values[idx]], cnfgen.ConstraintType.BIT_AND)
        cnf.add_constraint([var_weights[idx], includes[idx], inc_weights[idx]], cnfgen.ConstraintType.BIT_AND)

    cnf.add_constraint([inc_values[0], inc_values[1], sum_values[0]], cnfgen.ConstraintType.SUM)
    cnf.add_constraint([inc_weights[0], inc_weights[1], sum_weights[0]], cnfgen.ConstraintType.SUM)

    for idx in range(len(values)-2):
        cnf.add_constraint([inc_weights[idx+2], sum_weights[idx], sum_weights[idx+1]], cnfgen.ConstraintType.SUM)
        cnf.add_constraint([inc_values[idx+2], sum_values[idx], sum_values[idx+1]], cnfgen.ConstraintType.SUM)

    cnf.add_constraint([sum_weights[-1], var_wcut[0]], cnfgen.ConstraintType.LT)
    cnf.add_constraint([var_vcut[0], sum_values[-1]], cnfgen.ConstraintType.LT)

    res = cnf.solve()
    assert res == False


def test_knapsack_satisfiable():
    
    values = [5,4,3,1]
    weights = [4,3,2,1]

    val_cutoff = 6
    weight_cutoff = 6

    cnf = cnfgen.ConstraintCompiler()

    includes = cnf.create_vars(len(values), cnfgen.VarType.BOOL)
    
    var_weights = cnf.create_vars(len(values), cnfgen.VarType.INT, 4)
    var_values = cnf.create_vars(len(values), cnfgen.VarType.INT, 4)
    var_wcut = cnf.create_vars(1, cnfgen.VarType.INT, 4)
    var_vcut = cnf.create_vars(1, cnfgen.VarType.INT, 4)

    inc_weights = cnf.create_vars(len(values), cnfgen.VarType.INT, 4)
    inc_values = cnf.create_vars(len(values), cnfgen.VarType.INT, 4)

    sum_weights = cnf.create_vars(len(values)-1, cnfgen.VarType.INT, 4)
    sum_values = cnf.create_vars(len(values)-1, cnfgen.VarType.INT, 4)
    
    var_vcut[0].assign(cnf.handle, val_cutoff)
    var_wcut[0].assign(cnf.handle, weight_cutoff)

    for idx in range(len(values)):
        var_values[idx].assign(cnf.handle, values[idx])
        var_weights[idx].assign(cnf.handle, weights[idx])
    
    for idx in range(len(values)):
        cnf.add_constraint([var_values[idx], includes[idx], inc_values[idx]], cnfgen.ConstraintType.BIT_AND)
        cnf.add_constraint([var_weights[idx], includes[idx], inc_weights[idx]], cnfgen.ConstraintType.BIT_AND)

    cnf.add_constraint([inc_values[0], inc_values[1], sum_values[0]], cnfgen.ConstraintType.SUM)
    cnf.add_constraint([inc_weights[0], inc_weights[1], sum_weights[0]], cnfgen.ConstraintType.SUM)

    for idx in range(len(values)-2):
        cnf.add_constraint([inc_weights[idx+2], sum_weights[idx], sum_weights[idx+1]], cnfgen.ConstraintType.SUM)
        cnf.add_constraint([inc_values[idx+2], sum_values[idx], sum_values[idx+1]], cnfgen.ConstraintType.SUM)

    cnf.add_constraint([sum_weights[-1], var_wcut[0]], cnfgen.ConstraintType.LT)
    cnf.add_constraint([var_vcut[0], sum_values[-1]], cnfgen.ConstraintType.LT)

    res = cnf.solve()
    assert res == True
    print([w.eval(cnf.handle) for w in inc_weights])

