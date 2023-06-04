from pickle import NONE
from enum import Enum

class PositionWeighting(Enum):
    NONE = 0
    UNIFORM = 1
    INVERSE = 2
    DCG = 3
    GEOMETRIC = 4
    EXPONENTIAL = 5

class GradeType(Enum):
    INTERVAL = 0
    ORDINAL = 1
    RATIO = 2

def clamp(n, lb, ub):
    return max(min(ub, n), lb)
