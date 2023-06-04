#!/usr/bin/env python3.9
import sys
import argparse
import aggregation.rank_aggregation as rank_aggregation
from measures.measures import is_measure
import json
import random
from util.pref_io import read_measures
from util.pref_io import read_prefs
from util.pref_io import read_qids
from util.pref_io import get_query_rankings_from_preferences
from util.pref_io import get_query_rankings_from_measures
from util.pref_io import Preferences
from util.pref_io import Measures
from util.pref_io import Rankings

if __name__ == '__main__':

    parser:argparse.ArgumentParser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument("--prefs", "-P", dest="prefs", help="prefs path", required=True)
    parser.add_argument("--query_eval_wanted", "-q", dest='query_eval_wanted', help="generate per-query results", action='store_true', default=False)
    parser.add_argument("--nosummary", "-n", dest='nosummary', help="suppress the summary", action='store_true', default=False)
    parser.add_argument("--query_fraction", dest='query_fraction', help="fraction of queries to preserve (default = 1.0)", type=float, default=1.0)
    parser.add_argument('--num_samples', type=int, default=1)
    parser.add_argument('--metric', "-m", action='append', required=True)
    args = parser.parse_args()
    metrics = []
    metrics+=args.metric

    qids = read_qids(args.prefs) if (args.query_fraction < 1.0) else None
    sample_size = max(1,int(len(qids)*args.query_fraction)) if (args.query_fraction < 1.0) else None

    for sample in range(args.num_samples):
        
        sample_qids = None if qids is None else random.sample(qids,sample_size)
        
        src_sample = 0 if (args.query_fraction < 1.0) else sample

        prefs:Preferences = read_prefs(args.prefs,metrics,src_sample,sample_qids)
        measures:Measures = read_measures(args.prefs,metrics,src_sample,sample_qids)
        if sample_qids is None:
            sample_qids = list(prefs.keys())

        p_rankings:Rankings = get_query_rankings_from_preferences(prefs)
        m_rankings:Rankings = get_query_rankings_from_measures(measures)
        if args.query_eval_wanted:
            for qid in sample_qids:
                output_object = {}
                output_object["qid"] = qid
                output_object["sample"] = sample
                for kk,vv in p_rankings[qid].items():
                    output_object[kk]=vv
                for kk,vv in m_rankings[qid].items():
                    output_object[kk]=vv
                print(json.dumps(output_object))

        if not args.nosummary:
            output_object={}
            output_object["qid"] = "all"
            output_object["sample"] = sample
            for metric in metrics:
                output_object[metric] = {}
                if is_measure(metric):
                    output_object[metric]["type"] = "metric"
                    avgmetric = {}
                    numq = float(len(measures))
                    for qid,v in measures.items():
                        for run,value in v[metric].items():
                            if run not in avgmetric:
                                avgmetric[run] = 0.0
                            avgmetric[run] += value / numq
                    ranking = [x[1] for x in sorted([[v,k] for k,v in avgmetric.items()],reverse=True)]
                    output_object[metric]["mean"] = ranking
                else:
                    output_object[metric]["type"] = "preference"
                    rankings_metric:list[list[str]] = []
                    for qid,v in p_rankings.items():
                        rankings_metric.append(v[metric])
                    output_object[metric]["mc4"] = rank_aggregation.mc4(rankings_metric)
                    output_object[metric]["borda"] = rank_aggregation.borda(rankings_metric)
            print(json.dumps(output_object))
