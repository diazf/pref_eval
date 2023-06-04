preference-based evaluation
=====

code to compute preference-based evaluation measures

### [Recall-Paired Preference](https://841.io/doc/rpp.pdf)

implementation of graded rpp as well as top-heavy rpp with inverse or DCG weighting.

### [Lexicographic Recall](https://arxiv.org/abs/2302.11370)

implementation of lexirecall.


## Usage
Input qrels are assumed to be in standard four-column trec_eval format,
```
   <query id><subtopic id><document id><relevance grade>
```
where subtopic id is a base 1 identifier (or "0"/"Q0" if there are no subtopic labels) and relevance grade is ordinal with <=0 indicating nonrelevance.  If a query has no documents with relevance grade >0, it is removed from the evaluation.

Input runs are assumed to be in standard six-column trec_eval format,
```
   <query id><iteration><document id><rank><score>[<run id>]   
```
where iteration, rank, and run id are ignored (rank is computed from the score). Any missing queries in a run file are assumed to be worst-case performance.  Any additional queries in a run file are ignored.

In order to generate all pairs of preferences between runs, use `pref_eval.py`,
```
./pref_eval.py [-h] --qrels QRELS [--measure MEASURES] [--measure_set MEASURE_SET] [--binary_relevance BINARY_RELEVANCE] [--query_eval_wanted] [--nosummary] RUNFILE_0 RUNFILE_1 ...

optional arguments:
  -h, --help            show this help message and exit
  --qrels QRELS, -R QRELS
                        qrels path
  --measure MEASURES, -m MEASURES
                        preference-based evaluation: rpp, invrpp, dcgrpp, lexirecall
                        metric-based evaluation: ap, rbp, rr, ndcg, rp, p@k, r@k
  --measure_set MEASURE_SET, -M MEASURE_SET
                        preferences, all, none (default: all)
  --binary_relevance BINARY_RELEVANCE, -b BINARY_RELEVANCE
                        minimum relevance grade to generate binary labels (default: original grades)
  --relevance_floor RELEVANCE_FLOOR, -f RELEVANCE_FLOOR
                        any below this value is 0 (default: no floor)
  --query_eval_wanted, -q
                        generate per-query results
  --nosummary, -n       suppress the summary
```
In order to aggregate preferences into an ordering of systems, use `pref_aggregate.py`,
```
./pref_aggregate.py [-h] [--prefs PREFS] [--query_eval_wanted] [--nosummary]

optional arguments:
  -h, --help            show this help message and exit
  --prefs PREFS, -P PREFS
                        prefs path
  --query_eval_wanted, -q
                        generate per-query results
  --nosummary, -n       suppress the summary
```

