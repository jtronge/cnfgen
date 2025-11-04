import cnfgen

def test_graph_coloring_unsatisfiable():
    colors = ["red", "green", "blue"]
    graph = [[0,1], [0,2], [0,3], [1,2], [1,3], [2,3]]
    nnodes = 4

    cnf = cnfgen.ConstraintCompiler()
    nodes = cnf.create_vars(nnodes, cnfgen.VarType.ENUM, values = colors)

    for edge in graph:
        vars = [nodes[edge[0]], nodes[edge[1]]]
        cnf.add_constraint(vars, cnfgen.ConstraintType.DIFFERENT)

    cnf.output("test_graph_coloring.cnf")
    result = cnf.formula.solve()
    assert not result

def test_graph_coloring_satisfiable():
    colors = ["red", "green", "blue", "cyan"]
    graph = [[0,1], [0,2], [0,3], [1,2], [1,3], [2,3]]
    nnodes = 4

    cnf = cnfgen.ConstraintCompiler()
    nodes = cnf.create_vars(nnodes, cnfgen.VarType.ENUM, values = colors)

    for edge in graph:
        vars = [nodes[edge[0]], nodes[edge[1]]]
        cnf.add_constraint(vars, cnfgen.ConstraintType.DIFFERENT)

    cnf.output("test_graph_coloring.cnf")
    result = cnf.formula.solve()

    colors = set(node.eval(cnf.formula) for node in nodes)
    assert len(colors) == nnodes

    assert result
