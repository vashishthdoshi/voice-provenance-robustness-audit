# Results

| File | Contents |
|---|---|
| `query_order.csv` | Upload order, randomised with a fixed seed and committed before querying |
| `labels.csv` | One row per query with the raw score and the detected label (score of 50% or higher) |
| `retest.csv` | Second-run scores for the 12 reliability files |
| `summary_recall.csv` | Recall by condition and model, with 95% Wilson intervals and mean scores |
| `summary_fpr.csv` | False-positive rate on human controls by condition, with 95% Wilson intervals |
| `hypothesis_tests.csv` | Exact McNemar tests for H2 and H3, with Holm correction for H2, and exploratory condition comparisons |
| `retest_agreement.csv` | Agreement between first and second runs |
| `retest_comparison.csv` | First and second-run scores for each retested file |
| `recall_by_condition.png` | Recall by condition and model |
| `scores_by_condition.png` | Every raw score by condition, with the decision threshold marked |

All summary files are produced by `scripts/07_analyse.py` from `labels.csv` and `retest.csv`.
