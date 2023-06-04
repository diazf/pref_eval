import os
from util.relevance_vector import RelevanceVector
import gzip

QRels = dict[str,dict[str,dict[int,float]]]
QRelsPoolFrequency = dict[str,dict[str,int]]
Run = dict[str,RelevanceVector]

def read_qrels(path:str,binary_relevance,relevance_floor,full:bool=False) -> QRels:
    retval:QRels = {}
    with open(path, "r") as f:
        for line in f:
            qid:str = ""
            st_str:str = ""
            did:str = ""
            rel_str = ""
            qid,st_str,did,rel_str = line.strip().split()
            rel:float = float(rel_str)
            if (binary_relevance is not None):
                rel = float(rel >= binary_relevance)
            if (relevance_floor is not None) and (rel < relevance_floor):
                rel = 0.0
            st:int = 0 if st_str == "Q0" else int(st_str)
            if rel > 0.0 or full:
                if not qid in retval:
                    retval[qid] = {}
                if did in retval[qid]:
                    #
                    # general relevance is the max over subtopics
                    #
                    curret_rel:float = retval[qid][did][0]
                    retval[qid][did][0] = curret_rel if (curret_rel > rel) else rel
                else:
                    retval[qid][did] = {}
                    retval[qid][did][0] = rel
                if (st != 0):
                    retval[qid][did][st] = rel
    return retval

class ScoredDocument:
    did:str
    score:float
    rel = None
    def __init__(self,did:str,score:float,rel):
        self.did = did if did is not None else None
        self.score = score if score is not None else None
        self.rel = rel if rel is not None else None
    def __eq__(self,other):
        return (self.score == other.score) and (self.did == other.did)
    def __ne__(self,other):
        return (self.score != other.score) or (self.did != other.did)
    def __lt__(self,other):
        return (self.score < other.score) or ((self.score == other.score) and (self.did < other.did))
    def __le__(self,other):
        return not self.__gt__( other)
    def __gt__(self,other):
        return (self.score > other.score) or ((self.score == other.score) and (self.did > other.did))
    def __ge__(self,other):
        return not self.__lt__( other)

def read_run_line(line:str,qrels:QRels) -> tuple[str,ScoredDocument]:
    fields:list[str] = line.strip().split()
    qid:str = fields[0]
    did:str = fields[2]
    score_str:str = fields[4]
    score_str = score_str.replace(",",".")
    if score_str.lower() == "nan":
        return None,None
    score:float = float(score_str)
    if qid in qrels:
        rel = qrels[qid][did] if did in qrels[qid] else None
        return qid,ScoredDocument(did,score,rel)
    else:
        return None,None

def is_gz_file(path:str):
    with open(path, 'rb') as f:
        return f.read(2) == b'\x1f\x8b'

def read_run(path:str,qrels:QRels,topk) -> Run:
    run: dict[str,list[ScoredDocument]] = {}
    runid:str = os.path.basename(path)
    runid = runid.replace("input.","")
    runid = runid.replace(".gz","")
    if is_gz_file(path):
        with gzip.open(path,"rt") as f:
            for line in f:
                qid, scored_document = read_run_line(line,qrels)
                if qid is not None:
                    if qid not in run:
                        run[qid] = []
                    run[qid].append(scored_document)
    else:
        with open(path,"rt") as f:
            for line in f:
                qid, scored_document = read_run_line(line,qrels)
                if qid is not None:
                    if qid not in run:
                        run[qid] = []
                    run[qid].append(scored_document)
    retval:Run = {}
    for qid in qrels.keys():
        if qid in run:
            scores:list[ScoredDocument] = run[qid]
            scores.sort(reverse=True)
            if (topk is not None) and (len(scores) > topk):
                scores = scores[:topk]
            num_retrieved = len(scores)
            rv = RelevanceVector(qid,num_retrieved)
            reldocs = set(qrels[qid].keys())
            for i in range(len(scores)):
                rank = i + 1
                did:str = scores[i].did
                score:float = scores[i].score
                rel = scores[i].rel
                if (rel is not None):
                    rv.append(rank,did,rel)
                    reldocs.remove(did)
            for did in reldocs:
                rv.append(None,did,qrels[qid][did])
            retval[qid] = rv
        else:
            rv = RelevanceVector(qid,0)
            for did,rel in qrels[qid].items():
                rv.append(None,did,rel)
            retval[qid] = rv
    return runid, retval

def compute_qrel_pool_frequencies(paths,qrels) -> QRelsPoolFrequency:
    qrelspf = {}
    for qid,v in qrels.items():
        qrelspf[qid] = {}
        for did,vv in v.items():
            qrelspf[qid][did] = 0
    for path in paths:
        if is_gz_file(path):
            with gzip.open(path,"rt") as f:
                for line in f:
                    qid, scored_document = read_run_line(line,qrels)
                    if scored_document is not None:
                        did = scored_document.did
                        if (qid is not None) and (qid in qrelspf):
                            if did in qrelspf[qid]:
                                qrelspf[qid][did] = qrelspf[qid][did] + 1
        else:
            with open(path,"rt") as f:
                for line in f:
                    qid, scored_document = read_run_line(line,qrels)
                    if scored_document is not None:
                        did = scored_document.did
                        if (qid is not None) and (qid in qrelspf):
                            if did in qrelspf[qid]:
                                qrelspf[qid][did] = qrelspf[qid][did] + 1
    retval = {}
    for qid,v in qrelspf.items():
        dfs = []
        for did,vv in v.items():
            dfs.append([vv,did])
        dfs.sort(reverse=True)
        retval[qid] = [x[1] for x in dfs]
    return retval