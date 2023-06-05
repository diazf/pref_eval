#!/usr/bin/env python3.9
import sys
import argparse
import aggregation.rank_aggregation as rank_aggregation
from measures.measures import is_metric
import json
import random
from util.pref_io import read_metrics
from util.pref_io import read_all_measure_names
from util.pref_io import read_prefs
from util.pref_io import read_qids
from util.pref_io import get_query_rankings_from_preferences
from util.pref_io import get_query_rankings_from_metrics
from util.pref_io import Preferences
from util.pref_io import Metrics
from util.pref_io import Rankings

if __name__ == '__main__':

    parser:argparse.ArgumentParser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument("--prefs", "-P", dest="prefs", help="prefs path", required=True)
    parser.add_argument("--query_eval_wanted", "-q", dest='query_eval_wanted', help="generate per-query results", action='store_true', default=False)
    parser.add_argument("--nosummary", "-n", dest='nosummary', help="suppress the summary", action='store_true', default=False)
    parser.add_argument("--query_fraction", dest='query_fraction', help="fraction of queries to preserve (default = 1.0)", type=float, default=1.0)
    parser.add_argument('--num_samples', type=int, default=1)
    parser.add_argument('--measure', "-m", action='append', help="metric or preference name to aggregate (default: all measures in the preferences file)")
    args = parser.parse_args()
    measures = []
    if args.measure is not None:
        measures+=args.measure

    qids = read_qids(args.prefs) if (args.query_fraction < 1.0) else None
    sample_size = max(1,int(len(qids)*args.query_fraction)) if (args.query_fraction < 1.0) else None

    for sample in range(args.num_samples):
        
        sample_qids = None if qids is None else random.sample(qids,sample_size)
        
        src_sample = 0 if (args.query_fraction < 1.0) else sample

        if len(measures) == 0:
            measures = read_all_measure_names(args.prefs)

        prefs:Preferences = read_prefs(args.prefs,measures,src_sample,sample_qids)
        metrics:Metrics = read_metrics(args.prefs,measures,src_sample,sample_qids)
        if sample_qids is None:
            sample_qids = list(prefs.keys())

        p_rankings:Rankings = get_query_rankings_from_preferences(prefs)
        m_rankings:Rankings = get_query_rankings_from_metrics(metrics)
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
            for measure in measures:
                output_object[measure] = {}
                if is_metric(measure):
                    output_object[measure]["type"] = "metric"
                    avgmeasure = {}
                    numq = float(len(metrics))
                    for qid,v in metrics.items():
                        for run,value in v[measure].items():
                            if run not in avgmeasure:
                                avgmeasure[run] = 0.0
                            avgmeasure[run] += value / numq
                    ranking = [x[1] for x in sorted([[v,k] for k,v in avgmeasure.items()],reverse=True)]
                    output_object[measure]["mean"] = ranking
                else:
                    output_object[measure]["type"] = "preference"
                    rankings_metric:list[list[str]] = []
                    for qid,v in p_rankings.items():
                        rankings_metric.append(v[measure])
                    output_object[measure]["mc4"] = rank_aggregation.mc4(rankings_metric)
                    output_object[measure]["borda"] = rank_aggregation.borda(rankings_metric)
            print(json.dumps(output_object))
