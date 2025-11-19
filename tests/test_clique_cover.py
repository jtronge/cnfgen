from cnfgen import ConstraintCompiler, VarType, ConstraintType

def test_clique_cover_satisfiable():
    nnodes = 5
    # Edges of an undirected graph (only includes one direction here)
    edges = [(0, 1), (1, 2), (0, 2), (2, 3), (2, 4), (3, 4)]
    # Form the complement of the graph
    complement_edges = []
    for i in range(nnodes):
        for j in range(nnodes):
            # Include only edges (i, j) where i < j
            if i >= j:
                continue
            if (i, j) in edges:
                continue
            complement_edges.append((i, j))
    # Doing clique-cover for k=2
    k = 2
    colors = list(range(k))

    # Use the k-coloring problem to solve the clique cover problem
    cnf = ConstraintCompiler()
    nodes = cnf.create_vars(nnodes, VarType.ENUM, values=colors)
    for i, j in complement_edges:
        cnf.add_constraint([nodes[i], nodes[j]], ConstraintType.DIFFERENT)

    cnf.output("test_clique_cover.cnf")
    assert cnf.solve()
