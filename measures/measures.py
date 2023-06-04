import math
from pickle import NONE
from util.relevance_vector import RelevanceVector
from enum import Enum
from measures.rpp import recall_paired_preference
from measures.lexicographic import *
from measures.metric import *
from measures.util import PositionWeighting
from measures.util import GradeType

def compare(x: RelevanceVector,y: RelevanceVector,measure: str) -> float:
    xx: list[int] = x.vector()
    yy: list[int] = y.vector()
    if measure == "lexirecall" or measure == "LR" or measure == "sgnLR":
        return lexirecall(xx,yy)
    if measure == "lexiprecision" or measure == "sgnLP":
        return lexiprecision(xx,yy)
    if measure == "softlexiprecision" or measure == "rrLP":
        return softlexiprecision(xx,yy)
    if measure == "rpp":
        return recall_paired_preference(x,y,PositionWeighting.UNIFORM)
    if measure == "invrpp":
        return recall_paired_preference(x,y,PositionWeighting.INVERSE)
    if measure == "dcgrpp":
        return recall_paired_preference(x,y,PositionWeighting.DCG)
    if measure == "ap":
        return d_average_precision(xx,yy)
    if measure[:3] == "ap@":
        k:int = int(measure.split("@")[-1])
        return d_average_precision(xx,yy,k)
    if measure == "rbp":
        return d_rank_biased_precision(xx,yy)
    if measure[:4] == "rbp@":
        params = measure.split("@")[-1].split(",")
        gamma:float = float(params[0])
        k:int = int(params[1]) if len(params) > 1 else 0
        return d_rank_biased_precision(xx,yy,k,gamma)
    if measure == "rr":
        return d_reciprocal_rank(xx,yy)
    if measure == "ndcg":
        return d_ndcg(x,y)
    if measure[:5] == "ndcg@":
        k:int = int(measure.split("@")[-1])
        return d_ndcg(x,y,k)
    if measure == "rp":
        return d_r_precision(xx,yy)
    if measure[:2] == "p@":
        k:int = int(measure.split("@")[-1])
        return d_precision_at_k(xx,yy,k)
    if measure[:2] == "r@":
        k:int = int(measure.split("@")[-1])
        return d_recall_at_k(xx,yy,k)
    return 0.0

measure_labels=set(["ap","rbp","rr","ndcg","rp","p","r"])
def is_measure(measure) -> bool:
    measure_prefix = measure.split("@")[0]
    return measure_prefix in measure_labels

def measure(x: RelevanceVector,measure: str) -> float:
    xx: list[int] = x.vector()
    if measure == "ap":
        return average_precision(xx)
    if measure == "rbp":
        return rank_biased_precision(xx)
    if measure == "rr":
        return reciprocal_rank(xx)
    if measure == "ndcg":
        return ndcg(x)
    if measure == "rp":
        return r_precision(xx)
    if measure[:4] == "rbp@":
        params = measure.split("@")[-1].split(",")
        gamma:float = float(params[0])
        k:int = int(params[1]) if len(params) > 1 else 0
        return rank_biased_precision(xx,k,gamma)
    if measure[:3] == "ap@":
        k:int = int(measure.split("@")[-1])
        return average_precision(xx,k)
    if measure[:3] == "rr@":
        k:int = int(measure.split("@")[-1])
        return reciprocal_rank(xx,k)
    if measure[:5] == "ndcg@":
        k:int = int(measure.split("@")[-1])
        return ndcg(x,k)
    if measure[:2] == "p@":
        k:int = int(measure.split("@")[-1])
        return precision_at_k(xx,k)
    if measure[:2] == "r@":
        k:int = int(measure.split("@")[-1])
        return recall_at_k(xx,k)
    return 0.0
