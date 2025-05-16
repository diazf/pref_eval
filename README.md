preference-based evaluation
=====
## Introduction
Preference-based evaluation is a method for comparing rankings from multiple systems that is substantially more sensitive that existing metric-based approaches.  This makes it particularly appropriate in situations where existing metric-based evaluation results in a number per-query ties as a result of, for example, properties of the evaluation metric, the evaluation data, or systems themselves.  The theory behind our version of preference-based relies on modeling possible sub-populations of users issuing the same request, allowing us to connect it to work in fairness and robustness. We summarize the approach below but details are more fully presented in our [publications](#citation).  Or, you can skip to [code usage](#usage).  

### Motivation

In order to understand the intuition behind preference-based evaluation, we first need to understand the implicit sub-populations behind traditional evaluation metrics like average precision.  For a fixed ranked list, traditional evaluation metrics compute the performance of a system according to the expected behavior over distribution of possible user behavior \[[Robertson 2008](https://doi.org/10.1145/1390334.1390453); [Sakai and Robertson 2008](https://research.nii.ac.jp/ntcir/workshop/OnlineProceedings7/pdf/EVIA2008/07-EVIA2008-SakaiT.pdf); [Carterette 2011](https://doi.org/10.1145/2009916.2010037)\].  Interpreting evaluation metrics in this way allows us to disaggregate these metrics and look at the performance for specific types of users.  For example, we can disaggregate average precision into the utility for sub-populations of users associated with each recall level (i.e., the sub-population interested in exactly one relevant item, the sub-population interested in exactly two relevant items, ...).  

### Preference-Based Evaluation

We can use the decomposed evaluation metrics in order to compare two rankings for the same query for each implicit sub-population.  For example, we can ask for users interested in exactly one relevant item, which ranking would be preferred?  Or, for users interested in exactly two relevant items, which ranking would be preferred?  And so forth.  These preferences can be easily computed by adopting the principle that inspecting fewer items to satisfy a sub-population's recall requirements is preferable.  This is a relatively weak assumption and underlies most existing evaluation metrics.  

We can then aggregate the collection of sub-population preferences in order to compute a final preference between the rankings. How we aggregate preferences for two rankings depends on what we want to measure.  We can simply look at the average preference across sub-populations and recover a preference-based analog to average precision.  Comparing the worst off sub-population in both rankings recovers a preference-based analog to recall, robustness, and certain fairness metrics. Comparing the best off sub-population in both rankings recovers a preference-based analog to precision metrics.  We summary these correspondences in the table below.

<table>
  <tr>
      <td rowspan="2">Aggregation</td>
      <td rowspan="2">Preference</td>
      <td colspan="2", align="center">Metric-Based Analog</td>
      <td rowspan="2">Other Related Metrics</td>
  </tr>
  <tr>
    <td>Utility-Based</td>
    <td>Position-Based</td>
  </tr>
  <tr>
    <td>Average Case</td>
    <td><a href="https://841.io/doc/rpp.pdf">Recall-Paired Preference</a></td>
    <td>Average Precision</td>
    <td><a href="https://sigir.org/files/museum/pub-07/III-1.pdf">Recall Error</a></td>
    <td><a href="https://doi.org/10.1145/582415.582418">Normalized Discounted Cumulative Gain</a></td>
  </tr>
  <tr>
    <td>Worst Case</td>
    <td><a href="https://arxiv.org/abs/2302.11370">Lexicographic Recall</a></td>
    <td><a href="https://arxiv.org/abs/2302.11370">Total Search Efficiency</a></td>
    <td><a href="https://doi.org/10.1002/asi.5090190108">Type 3 Expected Search Length</a></td>
    <td>Recall@k, R-Precision</td>
  </tr>
  <tr>
    <td>Best Case</td>
    <td><a href="https://arxiv.org/abs/2306.07908">Lexicographic Precision</a></td>
    <td>Reciprocal Rank</td>
    <td><a href="https://doi.org/10.1002/asi.5090190108">Type 1 Expected Search Length</a></td>
    <td>Precision@k, Success@k</td>
  </tr>
</table>


The diagram below summarizes the sub-population preferences considered for each method.  We compare non-lexicographic best case (reciprocal rank, Type 1 Expected Search Length) and worst case (Type 3 Expected Search Length\]) with their lexicographic counterparts, demonstrating how they break ties.
<p align="center">
<img src="https://github.com/diazf/pref_eval/assets/75877/b0255084-538a-453f-9a18-5a654866d18c" alt="diagram of rank positions considered for preference-based evaluation" width="600"/></p>

### Evaluating More Than One System
If we are only evaluating a pair of systems over multiple queries, we can average the per-query preferences to compute a final ordering.  If we are evaluating multiple systems over one query and our preference-based evaluation is transitive (e.g., lexicographic preferences), then we compute a simple sort; if our preference-based evaluation is not transitive (e.g., RPP), then we can compute the win-rate as a simple aggregation.  If we are evaluating multiple systems over multiple queries, we need to aggregate preferences using methods from rank aggregation \[[Dwork et al. 2001](https://doi.org/10.1145/371920.372165)\].  

### When and How to Use Preference-Based Evaluation
Empirical evidence suggests that preference-based evaluation is substantially more sensitive than traditional metric-based evaluation.  So, preference-based evaluation can adopted when metrics are saturated (e.g., \[[Voorhees et al. 2022](https://doi.org/10.1145/3477495.3531728)\]).  However, we recommend complementing multiple evaluations to assess systems.  

Preference-based evaluation works particularly well with deep rankings, so that it can better compare positions of relevant items.  The exact depth depends on context but, in general, the closer you can get to knowing the positions of all relevant items, the better. 

Lexicographic evaluation assumes binary relevance, which may not be appropriate for your context.  This code supports the discretization of relevance grades into binary relevance but, in these cases, we strongly recommend complementing our lexicographic evaluation with graded metrics.  

## Usage

### Data
Ground truth relevance information (i.e., "qrels") is assumed to be in standard four-column trec_eval format,
```
   <query id><subtopic id><document id><relevance grade>
```
where subtopic id is a base 1 identifier (or "0"/"Q0" if there are no subtopic labels); if you are using this outside of the TREC context, you can just use "0" for the second column.  The relevance grade is ordinal with <=0 indicating nonrelevance.  If a query has no documents with relevance grade >0, it is removed from the evaluation.

System runs are assumed to be in standard six-column trec_eval format, with one system per file,
```
   <query id><iteration><document id><rank><score>[<run id>]   
```
where iteration, rank, and run id are ignored (rank is computed from the score); if you are using this outside of the TREC context, you can put "0" in each of these columns.  The run id used for output is the basename of the system run file, removing "input." and ".gz".  Any missing queries in a run file are assumed to be worst-case performance.  Any additional queries in a run file are ignored.

### Computing Preferences
In order to generate all pairs of preferences between runs, use `pref_eval.py`,
```
./pref_eval.py [-h] --qrels QRELS [--measure MEASURES] [--measure_set MEASURE_SET] [--binary_relevance INT] [--query_eval_wanted] [--nosummary] RUNFILE_0 RUNFILE_1 ...

optional arguments:
  -h, --help            show this help message and exit
  --qrels QRELS, -R QRELS
                        qrels path
  --measure MEASURES, -m MEASURES
                        preference-based evaluation: rpp, invrpp, dcgrpp, lexirecall, lexiprecision, rrlexiprecision
                        metric-based evaluation: ap, rbp, rr, ndcg, rp, p@k, r@k
  --measure_set MEASURE_SET, -M MEASURE_SET
                        preferences, all, none (default: all)
  --binary_relevance INT, -b INT
                        item is discretized to 1 (relevant) if it's grade >= GRADE; 0 otherwise (default: use original grades)
  --query_eval_wanted, -q
                        generate per-query results
  --nosummary, -n       suppress the summary
```

This will generate a JSON file with each line containing either the measured preference value(s) between a pair of runs or the metric value(s) for a run.  Any summary lines (qid="all") will contain the mean measured preference between a pair of runs.  

### Aggregating Preferences
In order to aggregate preferences into an ordering of systems, use `pref_aggregate.py`,
```
./pref_aggregate.py [-h] [--prefs PREFS] [--query_eval_wanted] [--nosummary]

optional arguments:
  -h, --help            show this help message and exit
  --prefs PREFS, -P PREFS
                        path to preferences file generated by pref_eval.py
  --query_eval_wanted, -q
                        generate per-query results
  --measure MEASURE, -m MEASURE
                        metric or preference name to aggregate (default: all measures in the preferences file)
  --nosummary, -n       suppress the summary
```

This will generate an ordering of runs using [MC4](https://dl.acm.org/doi/10.1145/371920.372165) or [Borda count](https://en.wikipedia.org/wiki/Borda_count) (for preference-based evaluation) or mean metric value (for metric-based evaluation).  

## Citation
For [Recall-Paired Preference](https://841.io/doc/rpp.pdf),
```
@inproceedings{diaz:rpp,
      author = {Diaz, Fernando and Ferraro, Andres},
      title = {Offline Retrieval Evaluation Without Evaluation Metrics},
      year = {2022},
      isbn = {9781450387323},
      publisher = {Association for Computing Machinery},
      address = {New York, NY, USA},
      url = {https://doi.org/10.1145/3477495.3532033},
      doi = {10.1145/3477495.3532033},
      booktitle = {Proceedings of the 45th International ACM SIGIR Conference on Research and Development in Information Retrieval},
      pages = {599–609},
      numpages = {11},
      location = {Madrid, Spain},
      series = {SIGIR '22}
}
```
For [Lexicographic Recall](https://arxiv.org/abs/2302.11370),
```
@misc{diaz:lexirecall,
author = {Diaz, Fernando and Ekstrand, Michael D. and Mitra, Bhaskar},
title = {Recall, Robustness, and Lexicographic Evaluation},
year = {2025},
journal = {ACM Trans. Recomm. Syst.},
month = apr
}
```
For [Lexicographic Precision](https://arxiv.org/abs/2306.07908),
```
@inproceedings{diaz:lexiprecision,
      author = {Diaz, Fernando},
      title = {Best-Case Retrieval Evaluation: Improving the Sensitivity of Reciprocal Rank with Lexicographic Precision},
      year = {2023},
      url = {https://doi.org/10.20736/0002001353},
      doi = {10.20736/0002001353},
      booktitle = {Proceedings of the Tenth International Workshop on Evaluating Information Access (EVIA 2023)},
      location = {Tokyo, Japan}
}

```

## Contact
[Fernando Diaz](mailto:diazf@acm.org)
