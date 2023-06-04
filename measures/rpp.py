import math
import sys
from pickle import NONE
from util.relevance_vector import RelevanceVector
from measures.util import PositionWeighting

def recall_paired_preference(u: RelevanceVector,v: RelevanceVector, weighting:PositionWeighting) -> float:
    retval:float = 0.0
    m_grade_total:int = 0
    for grade in u.grades:
        uu:list[int] = u.vector(grade)
        vv:list[int] = v.vector(grade)
        m_grade:int = len(uu)
        m_grade_total = m_grade_total + m_grade
        rpp_grade:float = rpp(uu,vv,weighting)
        if rpp_grade is None:
            sys.stderr.write(f"qid: {u.qid}\n")
            return None
        retval = retval + float(m_grade) * rpp_grade
    return retval / float(m_grade_total)

def get_weights(m:int, weighting:PositionWeighting) -> list[float]:
    retval:list[float] = []
    mass:float = 0.0
    for i in range(m):
        v:float = 1.0
        if weighting == PositionWeighting.DCG:
            v = 1.0 / math.log2(i+2)
        if weighting == PositionWeighting.INVERSE:
            v = 1.0 / float(i+1)
        retval.append(v)
        mass = mass + v
    return [x/mass for x in retval]

#
# Recall-Paired Preference (RPP)
#
def rpp(x: list[int],y: list[int],weighting:PositionWeighting):
    retval:float = 0.0
    mx:int = len(x)
    my:int = len(y)
    if mx != my:
        sys.stderr.write("rpp: relevant document length mismatch\n")
        sys.stderr.write(f"mx={mx}\n")
        sys.stderr.write(f"my={my}\n")
        return None
    m = mx
    weights:list[float] = get_weights(m,weighting)
    for i in range(m):
        if (x[i] is None) and (y[i] is None):
            break
        elif (x[i] is None):
            retval = retval - weights[i]
        elif (y[i] is None):
            retval = retval + weights[i]
        elif (x[i] < y[i]):
            retval = retval + weights[i]
        elif (x[i] > y[i]):
            retval = retval - weights[i]
    return float(retval) 

