"""Variable types and constraint types for cnfgen."""


class VarType:
    BOOL = 0
    ENUM = 1


class ConstraintType:
    DIFFERENT = 0
    OR = 1
    ATMOST = 2
    AND = 3
    NAND = 4
