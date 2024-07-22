import math
from pickle import NONE
from util.relevance_vector import RelevanceVector
from enum import Enum
from measures.util import PositionWeighting
from measures.util import GradeType

#
# LEXICOGRAPHIC EVALUATION
# 
def lexirecall(x: list[int],y: list[int], x_rr:int, y_rr:int) -> float:
    if x_rr > y_rr:
        return 1
    elif x_rr < y_rr:
        return -1
    m:int = len(x)
    for i in range(x_rr-1,-1,-1):
        if (x[i] is None) and (y[i] is None):
            continue
        if (x[i] is None):
            return -1
        if (y[i] is None):
            return 1
        if (x[i] < y[i]):
            return 1
        if (x[i] > y[i]):
            return -1
    return 0

def lexiprecision(x: list[int],y: list[int]) -> float:
    m:int = len(x)
    for i in range(m):
        if (x[i] is None) and (y[i] is None):
            continue
        if (x[i] is None):
            return -1
        if (y[i] is None):
            return 1
        if (x[i] < y[i]):
            return 1
        if (x[i] > y[i]):
            return -1
    return 0

def rrlexiprecision(x: list[int],y: list[int]) -> float:
    m:int = len(x)
    for i in range(m):
        rrx = 0.0 if x[i] is None else 1.0 / float(x[i])
        rry = 0.0 if y[i] is None else 1.0 / float(y[i])
        if (x[i] is None) and (y[i] is None):
            continue
        if (x[i] is None):
            return -1.0 * rry
        if (y[i] is None):
            return rrx
        if (x[i] != y[i]):
            return rrx - rry
    return 0
