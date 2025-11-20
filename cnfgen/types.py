"""Variable types and constraint types for cnfgen."""


class VarType:
    BOOL = 0
    ENUM = 1
    INT = 2

class ConstraintType:
    OR = 0
    ATMOST = 1
    AND = 2
    NAND = 3
    
    DIFFERENT = 10
    SAME = 11
   
    EQ = 20
    NEQ = 21
    SUM = 22
