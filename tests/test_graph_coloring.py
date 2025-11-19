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

def test_graph_coloring_unsatisfiable():
    colors = ["red", "green", "blue"]
    graph = [[0,1], [0,2], [0,3], [1,2], [1,3], [2,3]]
    nnodes = 4

    cnf = cnfgen.ConstraintCompiler()
    setup_coloring_problem(cnf, nnodes, graph, colors)

    cnf.output("test_graph_coloring.cnf")
    result = cnf.solve()
    assert not result

def test_graph_coloring_satisfiable():
    colors = ["red", "green", "blue", "cyan"]
    graph = [[0,1], [0,2], [0,3], [1,2], [1,3], [2,3]]
    nnodes = 4

    cnf = cnfgen.ConstraintCompiler()
    nodes = setup_coloring_problem(cnf, nnodes, graph, colors)

    cnf.output("test_graph_coloring.cnf")
    result = cnf.solve()

    colors = set(cnf.eval(node) for node in nodes)
    assert len(colors) == nnodes

    assert result

# TODO: Read G22 and Cities (cities is two-colorable) graph for another test
@pytest.fixture
def root(request):
    return request.config.rootpath

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

@pytest.mark.parametrize("ncolors,graph_path,exp_result", [
    (1, "data/G12/G12.mtx", False),
    (2, "data/G12/G12.mtx", True),
    (3, "data/G12/G12.mtx", True),
    (4, "data/G12/G12.mtx", True),
    (5, "data/G12/G12.mtx", True),
    (6, "data/G12/G12.mtx", True),
    (7, "data/G12/G12.mtx", True),
    (8, "data/G12/G12.mtx", True),
    (9, "data/G12/G12.mtx", True),
    (10, "data/G12/G12.mtx", True),
])
def test_graph_coloring_file(root, ncolors, graph_path, exp_result):
    colors = [f"color-{i}" for i in range(ncolors)]
    nnodes, graph = load_graph(root / graph_path)

    cnf = cnfgen.ConstraintCompiler()
    setup_coloring_problem(cnf, nnodes, graph, colors)

    result = cnf.solve()
    assert result == exp_result
