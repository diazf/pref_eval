#!/usr/bin/env python3.9
import sys
import argparse
import random
from measures.measures import compute_preference
from measures.measures import compute_metric
from measures.measures import is_metric
from util.relevance_vector import RelevanceVector
import util.trec_io 
from argparse import RawTextHelpFormatter
import json

def get_prefs(sample:int, runs: dict[str,util.trec_io.Run],measures:list[str],per_query:bool) -> dict[str,dict[str,float]]:
    runids:list[str] = list(runs.keys())
    qids:list[str] = list(runs[runids[0]].keys())
    numq:int = len(qids)
    retval:dict[str,dict[str,float]] = {}
    for qid in qids:
        for i in range(len(runids)):
            runid_i:str = runids[i]
            rv_i:RelevanceVector = runs[runid_i][qid]
            for j in range(i+1,len(runids)):
                runid_j:str = runids[j]
                rv_j:RelevanceVector = runs[runid_j][qid]
                pair_tag = f"{runid_i}:{runid_j}"
                if pair_tag not in retval:
                    retval[pair_tag] = {}
                output_object={}
                output_object["qid"] = qid
                output_object["runi"] = runid_i
                output_object["runj"] = runid_j
                output_object["sample"] = sample
                output_object["type"] = "preference"
                for m in measures:
                    pref:float = compute_preference(rv_i,rv_j,m)
                    if pref is None:
                        sys.stderr.write(f"ERROR: qid:{qid} runi:{runid_i} runj:{runid_j} sample:{sample} measure:{m}\n")
                        u = rv_i.vector()
                        for k in range(len(u)):
                            sys.stderr.write(f"u[{k}]={u[k]}\n")
                        for k in range(len(rv_i.positions)):
                            sys.stderr.write(f"rv_i[{k}].position={rv_i.positions[k].position}\n")
                            sys.stderr.write(f"rv_i[{k}].did={rv_i.positions[k].did}\n")
                            sys.stderr.write(f"rv_i[{k}].grades[0]={rv_i.positions[k].grades[0]}\n")
                        v = rv_j.vector()
                        for k in range(len(v)):
                            sys.stderr.write(f"v[{k}]={v[k]}\n")
                        for k in range(len(rv_j.positions)):
                            sys.stderr.write(f"rv_j[{k}].position={rv_j.positions[k].position}\n")
                            sys.stderr.write(f"rv_j[{k}].did={rv_j.positions[k].did}\n")
                            sys.stderr.write(f"rv_j[{k}].grades[0]={rv_j.positions[k].grades[0]}\n")
                        sys.exit()
                    output_object[m] = pref
                    if m not in retval[pair_tag]:
                        retval[pair_tag][m] = 0.0
                    retval[pair_tag][m] = retval[pair_tag][m] + pref / float(numq)
                if per_query:
                    print(json.dumps(output_object))
            if per_query:
                output_object=None
                rv:RelevanceVector = runs[runid_i][qid]
                for m in measures:
                    if is_metric(m):
                        if output_object is None:
                            output_object={}
                            output_object["qid"] = qid
                            output_object["run"] = runid_i
                            output_object["sample"] = sample
                            output_object["type"] = "metric"
                        meas:float = compute_metric(rv,m)
                        output_object[m] = meas
                if output_object is not None:
                    print(json.dumps(output_object))



    return retval


def get_measures(m,ms):
    preference_measures = ["rpp","invrpp","dcgrpp","lexirecall","lexiprecision","rrlexiprecision"]
    all_measures = ["rpp","invrpp","dcgrpp","lexirecall","lexiprecision","rrlexiprecision","ap","rbp","rr","ndcg","rp","p@1","p@10","r@1","r@10"]

    measures:list[str] = m if m is not None else []
    measure_set:str = (ms if ms != "none" else "all") if len(measures)==0 else ""
    
    if measure_set == "preferences":
        if len(measures) == 0:
            measures = preference_measures
        else:
            for m in preference_measures:
                if m not in measures:
                    measures.append(m)
    elif measure_set == "all":
        if len(measures) == 0:
            measures = all_measures
        else:
            for m in all_measures:
                if m not in measures:
                    measures.append(m)
    return measures

if __name__ == '__main__':

    parser:argparse.ArgumentParser = argparse.ArgumentParser(sys.argv[0], formatter_class=RawTextHelpFormatter)
    parser.add_argument("--qrels", "-R", dest="qrels", help="qrels path", required=True)
    parser.add_argument("--measure", "-m", dest='measures', help="preference-based evaluation: rpp, invrpp, dcgrpp, lexirecall, lexiprecision, rrlexiprecision\nmetric-based evaluation: ap, rbp, rr, ndcg, rp, p@k, r@k", action='append')
    parser.add_argument("--measure_set", "-M", dest='measure_set', help="preferences, all, none", default='none')
    parser.add_argument("--binary_relevance", "-b", dest='binary_relevance', help="minimum relevance grade to generate binary labels")
    parser.add_argument("--relevance_floor", "-f", dest='relevance_floor', help="any below this value is 0")
    parser.add_argument("--query_eval_wanted", "-q", dest='query_eval_wanted', help="generate per-query results", action='store_true', default=False)
    parser.add_argument("--nosummary", "-n", dest='nosummary', help="suppress the summary", action='store_true', default=False)
    parser.add_argument("--query_fraction", dest='query_fraction', help="fraction of queries to preserve (default = 1.0)", type=float, default=1.0)
    parser.add_argument("--label_fraction", dest='label_fraction', help="fraction of labels to preserve (default = 1.0)", type=float, default=1.0)
    parser.add_argument("--label_fraction_policy", dest='label_fraction_policy', help="how to sample labels (random, pool; default=random)", type=str, default="random")
    parser.add_argument("--samples", dest='samples', help="number of samples", type=int, default=1)
    parser.add_argument("--topk", dest='topk', help="truncate run to topk", type=int)

    parser.add_argument('runfiles',nargs=argparse.REMAINDER, metavar='runfiles')
    args = parser.parse_args()

    if (len(args.runfiles) < 2):
        print("need at least two runs for comparison")
        parser.print_usage()
        sys.exit()
    
    measures = get_measures(args.measures,args.measure_set)

    binary_relevance = None if args.binary_relevance is None else float(args.binary_relevance)
    relevance_floor = None if args.relevance_floor is None else float(args.relevance_floor)
    topk = None if args.topk is None else args.topk

    for sample in range(args.samples):
        qrels:util.trec_io.QRels = util.trec_io.read_qrels(args.qrels,binary_relevance,relevance_floor)

        if args.query_fraction < 1.0:
            qids = list(qrels.keys())
            num_sample = max(int(len(qids) * args.query_fraction),1)
            if num_sample < len(qids):
                qids_to_remove = random.sample(qids,len(qids)-num_sample)
                for qid in qids_to_remove:
                    qrels.pop(qid,None)
        if args.label_fraction < 1.0:
            if (args.label_fraction_policy == "pool"):
                qrels_pool_frequencies = util.trec_io.compute_qrel_pool_frequencies(args.runfiles,qrels)
            for qid in qrels.keys():
                dids = list(qrels[qid].keys())
                num_sample = max(int(len(dids) * args.label_fraction),1)
                if num_sample < len(dids):
                    if (args.label_fraction_policy == "pool"):
                        dids_to_remove = qrels_pool_frequencies[qid][num_sample:]
                    else:
                        dids_to_remove = random.sample(dids,len(dids)-num_sample)
                    for did in dids_to_remove:
                        qrels[qid].pop(did,None)



        runs:dict[str,util.trec_io.Run] = {}

        for runfile in args.runfiles:
            runid,run = util.trec_io.read_run(runfile,qrels,topk)
            runs[runid] = run

        summary = get_prefs(sample,runs,measures,args.query_eval_wanted)

        if not args.nosummary:
            for pair_tag,m_prefs in summary.items():
                output_object={}
                output_object["qid"] = "all"
                output_object["runi"] = pair_tag.split(":")[0]
                output_object["runj"] = pair_tag.split(":")[1]
                output_object["sample"] = sample
                for measure,pref in m_prefs.items():
                    output_object[measure] = pref
                print(json.dumps(output_object))
