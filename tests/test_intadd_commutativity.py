import pytest
import cnfgen

def setup_intcomm_problem(cc, bitwidth):
    ints = cc.create_vars(4, cnfgen.VarType.INT, values = bitwidth)
    cc.add_constraint([ints[0], ints[1], ints[2]], cnfgen.ConstraintType.SUM)
    cc.add_constraint([ints[1], ints[0], ints[3]], cnfgen.ConstraintType.SUM)
    cc.add_constraint([ints[2], ints[3]], cnfgen.ConstraintType.NEQ)

@pytest.mark.parametrize("bitwidth,exp_result", [
    (4, False),
    (8, False),
    (16, False),
    (32, False),
    (64, False),
    (128, False),
    (256, False),
])
def test_intadd_commutativity(bitwidth, exp_result):
    cc = cnfgen.ConstraintCompiler()
    setup_intcomm_problem(cc, bitwidth)

    result = cc.solve()
    assert result == exp_result
