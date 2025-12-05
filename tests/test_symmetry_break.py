import pytest
import cnfgen
from scipy.io import mmread

def setup_coloring_problem(cnf, nnodes, graph, colors):
    """Setup a graph coloring problem."""
    nodes = cnf.create_vars(nnodes, cnfgen.VarType.ENUM, values = colors)
    for i, j in graph:
        vars_ = [nodes[i], nodes[j]]
        cnf.add_constraint(vars_, cnfgen.ConstraintType.DIFFERENT)
    return nodes

def test_graph_coloring_satisfiable():
    colors = ["red", "green", "blue"]
    graph = [[0,1], [0,2], [1,2], [0,3]]
    nnodes = 4

    cnf = cnfgen.ConstraintCompiler()
    nodes = setup_coloring_problem(cnf, nnodes, graph, colors)
    stack = cnf.add_symmetry(nodes[0:3], cnfgen.VarType.ENUM, k = colors)
    
    result = cnf.solve()

    assert result
