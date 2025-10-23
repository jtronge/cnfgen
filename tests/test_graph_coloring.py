import cnfgen

def test_graph_coloring():
    return
    colors = ["red", "green", "blue"]
    graph = [[0,0], [0,1], [0,2], [0,3], [1,2], [1,3], [2,3]]
    nnodes = 4

    cnf = cnfgen.ConstraintCompiler()
    nodes = cnf.create_vars(nnodes, cnfgen.VarType.ENUM, values = colors)

    for edge in graph:
        vars = [nodes[edge[0]], nodes[edge[1]]]
        cnf.add_constraint(vars, cnfgen.ConstraintType.DIFFERENT)

    cnf.output("test_graph_coloring.cnf")
    result = cnf.solve()
    assert result == "UNSATISFIABLE"
