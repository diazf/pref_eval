import json
from measures.measures import is_metric
import sys
import gzip

Preferences = dict[str,dict[str,dict[str,float]]] # qid x pref x pair_tag 
Metrics = dict[str,dict[str,dict[str,float]]] # qid x metric x runid 
Rankings = dict[str,dict[str,list[str]]] # qid x metric x run x score

def read_pp_line(line):
    return json.loads(line)

def is_gz_file(path:str) -> bool:
    with open(path, 'rb') as f:
        return f.read(2) == b'\x1f\x8b'

def read_qids(path:str):
    retval = set()
    if is_gz_file(path):
        with gzip.open(path,"rt") as f:
            for line in f:
                obj = read_pp_line(line)
                sample = obj["sample"]
                if sample > 0:
                    break
                qid:str = obj["qid"]
                linetype = obj["type"]
                if (linetype == "metric") and (qid != "all"):
                    retval.add(qid)
    else:
        with open(path, "r") as f:
            for line in f:
                obj = read_pp_line(line)
                sample = obj["sample"]
                if sample > 0:
                    break
                qid:str = obj["qid"]
                linetype = obj["type"]
                if (linetype == "metric") and (qid != "all"):
                    retval.add(qid)
    return list(retval)


def read_prefs(path:str,metrics,current_sample,qids=None) -> Preferences:
    retval:Preferences = {}
    if is_gz_file(path):
        with gzip.open(path,"rt") as f:
            for line in f:
                obj = read_pp_line(line)
                qid:str = obj["qid"]
                sample = obj["sample"]
                linetype = obj["type"] if qid != "all" else None
                if (linetype == "metric") or (qid == "all") or (sample != current_sample) or ((qids is not None) and (qid not in qids)):
                    continue
                if qid not in retval:
                    retval[qid] = {}
                pair_tag=f"{obj['runi']}:{obj['runj']}"
                for metric in metrics:
                    if not is_metric(metric):
                        preference:float = obj[metric]                
                        if metric not in retval[qid]:
                            retval[qid][metric] = {}
                        retval[qid][metric][pair_tag] = preference
    else:
        with open(path, "r") as f:
            for line in f:
                obj = read_pp_line(line)
                qid:str = obj["qid"]
                sample = obj["sample"]
                linetype = obj["type"] if qid != "all" else None
                if (linetype == "metric") or (qid == "all") or (sample != current_sample) or ((qids is not None) and (qid not in qids)):
                    continue
                if qid not in retval:
                    retval[qid] = {}
                pair_tag=f"{obj['runi']}:{obj['runj']}"
                for metric in metrics:
                    if not is_metric(metric):
                        preference:float = obj[metric]                
                        if metric not in retval[qid]:
                            retval[qid][metric] = {}
                        retval[qid][metric][pair_tag] = preference                        
    qids_read:list[str] = list(retval.keys())
    if (len(qids_read)==0):
        sys.stderr.write("no queries with preference information found\n")
        sys.exit()
    return retval

def read_metrics(path:str,metrics,current_sample,qids=None) -> Metrics:
    retval:Metrics = {}
    if is_gz_file(path):
        with gzip.open(path,"rt") as f:
            for line in f:
                obj = read_pp_line(line)
                qid:str = obj["qid"]
                sample = obj["sample"]
                linetype = obj["type"] if qid != "all" else None
                if (linetype == "preference") or (qid == "all") or (sample != current_sample) or ((qids is not None) and (qid not in qids)):
                    continue
                run=obj["run"]
                if qid not in retval:
                    retval[qid] = {}
                for metric in metrics:
                    if is_metric(metric):
                        meas:float = obj[metric]                
                        if metric not in retval[qid]:
                            retval[qid][metric] = {}
                        retval[qid][metric][run] = meas
    else:
        with open(path, "r") as f:
            for line in f:
                obj = read_pp_line(line)
                qid:str = obj["qid"]
                sample = obj["sample"]
                linetype = obj["type"] if qid != "all" else None
                if (linetype == "preference") or (qid == "all") or (sample != current_sample) or ((qids is not None) and (qid not in qids)):
                    continue
                run=obj["run"]
                if qid not in retval:
                    retval[qid] = {}
                for metric in metrics:
                    if is_metric(metric):
                        meas:float = obj[metric]                
                        if metric not in retval[qid]:
                            retval[qid][metric] = {}
                        retval[qid][metric][run] = meas
    qids_read:list[str] = list(retval.keys())
    if (len(qids_read)==0):
        sys.stderr.write("no queries with metric information found\n")
        sys.exit()
    return retval

def read_all_measure_names(path:str):
    measures=set()
    lines=0
    if is_gz_file(path):
        with gzip.open(path,"rt") as f:
            for line in f:
                obj = read_pp_line(line)
                for k in obj.keys():
                    if k not in ["qid","sample","type","runi","runj","run"]:
                        measures.add(k)
                lines = lines + 1
                if lines >= 10:
                    break
    else:
        with open(path, "r") as f:
            for line in f:
                obj = read_pp_line(line)
                for k in obj.keys():
                    if k not in ["qid","sample","type","runi","runj","run"]:
                        measures.add(k)
                lines = lines + 1
                if lines >= 10:
                    break
    return list(measures)

def get_query_rankings_from_preferences(prefs:Preferences) -> Rankings:
    retval:Rankings = {}
    for qid,v in prefs.items():
        for metric,vv in v.items():
            winrates: dict[str,float] = {}
            for pair_tag,preference in vv.items():
                runid_i,runid_j = pair_tag.split(":")
                if runid_i not in winrates:
                    winrates[runid_i] = 0.0
                if runid_j not in winrates:
                    winrates[runid_j] = 0.0
                winrates[runid_i] = winrates[runid_i] + preference
                winrates[runid_j] = winrates[runid_j] - preference
            # print(winrates)
            ranking = [x[1] for x in sorted([[v,k] for k,v in winrates.items()],reverse=True)]
            # print(ranking)
            if qid not in retval:
                retval[qid] = {}
            retval[qid][metric] = ranking
    return retval

def get_query_rankings_from_metrics(metrics:Metrics) -> Rankings:
    retval:Rankings = {}
    for qid,v in metrics.items():
        for metric,vv in v.items():
            winrates: dict[str,float] = vv
            # print(winrates)
            ranking = [x[1] for x in sorted([[v,k] for k,v in winrates.items()],reverse=True)]
            # print(ranking)
            if qid not in retval:
                retval[qid] = {}
            retval[qid][metric] = ranking
    return retval
