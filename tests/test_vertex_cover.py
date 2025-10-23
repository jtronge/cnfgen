import cnfgen

def test_vertex_cover():
    graph = [[0,1], [0,2], [0,3], [1,2], [1,3], [2,3]]
    nnodes = 4
    nedges = len(graph)

    cnf = cnfgen.ConstraintCompiler()
    nodes = cnf.create_vars(nnodes, cnfgen.VarType.BOOL)

    for i in range(nedges):
        vars = [nodes[graph[i][0]], nodes[graph[i][1]]]
        cnf.add_constraint(vars, cnfgen.ConstraintType.OR)

    cnf.add_constraint(nodes, cnfgen.ConstraintType.ATMOST, 2)
    
    result = cnf.formula.solve()
    assert not result

    graph = [[0,1], [0,2], [0,3], [1,2], [1,3], [2,3]]
    nnodes = 4
    nedges = len(graph)

    cnf = cnfgen.ConstraintCompiler()
    nodes = cnf.create_vars(nnodes, cnfgen.VarType.BOOL)

    for i in range(nedges):
        vars = [nodes[graph[i][0]], nodes[graph[i][1]]]
        cnf.add_constraint(vars, cnfgen.ConstraintType.OR)

    cnf.add_constraint(nodes, cnfgen.ConstraintType.ATMOST, 3)
    
    result = cnf.formula.solve()
    print(cnf.formula.model())
    assert result


