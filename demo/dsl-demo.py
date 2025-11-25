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

def load_graph(path):
    mat = mmread(path)
    nnodes = max(mat.shape)
    edges = list(zip(mat.row, mat.col))
    # Remove duplicates
    graph = set()
    for i, j in edges:
        if (i, j) in graph or (j, i) in graph:
            continue
        graph.add((i, j))
    return nnodes, list(graph)

def test_graph_coloring_file(ncolors, graph_path, exp_result):
    colors = [f"color-{i}" for i in range(ncolors)]
    nnodes, graph = load_graph(graph_path)

    cnf = cnfgen.ConstraintCompiler()
    setup_coloring_problem(cnf, nnodes, graph, colors)

    result = cnf.solve()
    assert result == exp_result
    if (exp_result):
        print("Graph G12.mtx is {}-colorable in {}s".format(ncolors, cnf.handle.solver.time()))
    else:
        print("Graph G12.mtx is NOT {}-colorable in {}s".format(ncolors, cnf.handle.solver.time()))

def setup_intcomm_problem(cc, bitwidth):
    ints = cc.create_vars(4, cnfgen.VarType.INT, values = bitwidth)
    cc.add_constraint([ints[0], ints[1], ints[2]], cnfgen.ConstraintType.SUM)
    cc.add_constraint([ints[1], ints[0], ints[3]], cnfgen.ConstraintType.SUM)
    cc.add_constraint([ints[2], ints[3]], cnfgen.ConstraintType.NEQ)

def test_intadd_commutativity(bitwidth, exp_result):
    cc = cnfgen.ConstraintCompiler()
    setup_intcomm_problem(cc, bitwidth)

    result = cc.solve()
    assert result == exp_result
    print('Verified bitwidth {} in {}s'.format(bitwidth, cc.handle.solver.time()))

if __name__ == "__main__":

    print("------ graph coloring ------")

    test_graph_coloring_file(1, "data/G12/G12.mtx", False)
    test_graph_coloring_file(2, "data/G12/G12.mtx", True)
    test_graph_coloring_file(3, "data/G12/G12.mtx", True)
    test_graph_coloring_file(4, "data/G12/G12.mtx", True)
    print()

    print("------ intadd comm -------")

    test_intadd_commutativity(4, False)
    test_intadd_commutativity(8, False)
    test_intadd_commutativity(16, False)
    test_intadd_commutativity(32, False)
    test_intadd_commutativity(64, False)
    test_intadd_commutativity(128, False)
