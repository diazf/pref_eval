import math
from pickle import NONE
from util.relevance_vector import RelevanceVector
from enum import Enum
from measures.rpp import recall_paired_preference
from measures.lexicographic import *
from measures.metric import *
from measures.util import PositionWeighting
from measures.util import GradeType

def compute_preference(x: RelevanceVector,y: RelevanceVector,preference: str) -> float:
    xx: list[int] = x.vector()
    yy: list[int] = y.vector()
    if preference == "lexirecall" or preference == "LR" or preference == "sgnLR":
        return lexirecall(xx,yy)
    if preference == "lexiprecision" or preference == "sgnLP":
        return lexiprecision(xx,yy)
    if preference == "softlexiprecision" or preference == "rrLP":
        return softlexiprecision(xx,yy)
    if preference == "rpp":
        return recall_paired_preference(x,y,PositionWeighting.UNIFORM)
    if preference == "invrpp":
        return recall_paired_preference(x,y,PositionWeighting.INVERSE)
    if preference == "dcgrpp":
        return recall_paired_preference(x,y,PositionWeighting.DCG)
    if preference == "ap":
        return d_average_precision(xx,yy)
    if preference[:3] == "ap@":
        k:int = int(preference.split("@")[-1])
        return d_average_precision(xx,yy,k)
    if preference == "rbp":
        return d_rank_biased_precision(xx,yy)
    if preference[:4] == "rbp@":
        params = preference.split("@")[-1].split(",")
        gamma:float = float(params[0])
        k:int = int(params[1]) if len(params) > 1 else 0
        return d_rank_biased_precision(xx,yy,k,gamma)
    if preference == "rr":
        return d_reciprocal_rank(xx,yy)
    if preference == "ndcg":
        return d_ndcg(x,y)
    if preference[:5] == "ndcg@":
        k:int = int(preference.split("@")[-1])
        return d_ndcg(x,y,k)
    if preference == "rp":
        return d_r_precision(xx,yy)
    if preference[:2] == "p@":
        k:int = int(preference.split("@")[-1])
        return d_precision_at_k(xx,yy,k)
    if preference[:2] == "r@":
        k:int = int(preference.split("@")[-1])
        return d_recall_at_k(xx,yy,k)
    return 0.0

metric_labels=set(["ap","rbp","rr","ndcg","rp","p","r"])
def is_metric(measure) -> bool:
    measure_prefix = measure.split("@")[0]
    return measure_prefix in metric_labels

def compute_metric(x: RelevanceVector,metric: str) -> float:
    xx: list[int] = x.vector()
    if metric == "ap":
        return average_precision(xx)
    if metric == "rbp":
        return rank_biased_precision(xx)
    if metric == "rr":
        return reciprocal_rank(xx)
    if metric == "ndcg":
        return ndcg(x)
    if metric == "rp":
        return r_precision(xx)
    if metric[:4] == "rbp@":
        params = metric.split("@")[-1].split(",")
        gamma:float = float(params[0])
        k:int = int(params[1]) if len(params) > 1 else 0
        return rank_biased_precision(xx,k,gamma)
    if metric[:3] == "ap@":
        k:int = int(metric.split("@")[-1])
        return average_precision(xx,k)
    if metric[:3] == "rr@":
        k:int = int(metric.split("@")[-1])
        return reciprocal_rank(xx,k)
    if metric[:5] == "ndcg@":
        k:int = int(metric.split("@")[-1])
        return ndcg(x,k)
    if metric[:2] == "p@":
        k:int = int(metric.split("@")[-1])
        return precision_at_k(xx,k)
    if metric[:2] == "r@":
        k:int = int(metric.split("@")[-1])
        return recall_at_k(xx,k)
    return 0.0
