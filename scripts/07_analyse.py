"""Analysis plan from Section 6 of the preregistration.

Reads results/labels.csv, applies the decision rule (score >= 50 is detected)
and writes:
  results/summary_recall.csv    recall by condition and model, 95% Wilson intervals
  results/summary_fpr.csv       false-positive rate by condition, 95% Wilson intervals
  results/hypothesis_tests.csv  exact McNemar tests with Holm correction
  results/retest_agreement.csv  first vs second run on the 12 retest files (Section 5.3)
  results/retest_comparison.csv per-file scores from both runs
  results/recall_by_condition.png
  results/scores_by_condition.png

Run: python scripts/07_analyse.py
"""
import sys
from math import comb, sqrt
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from design import RESULTS

sys.stdout.reconfigure(encoding="utf-8")
THRESHOLD = 50
CONDS = ["C0", "C1", "C2", "C3"]
COND_NAMES = {"C0": "Clean", "C1": "MP3 64 kbps", "C2": "Telephone", "C3": "Noise 10 dB"}
MODEL_NAMES = {"v2": "Multilingual v2", "fl": "Flash v2.5", "v3": "Eleven v3"}


def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def mcnemar_exact(b, c):
    """Two-sided exact McNemar p-value from discordant counts b and c."""
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, running = [0.0] * len(ps), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = running
    return adj


d = pd.read_csv(RESULTS / "labels.csv", dtype=str)
excluded = d[d["detected"].fillna("").str.lower() == "excluded"]
d = d.drop(excluded.index)
d["score"] = d["raw_score_pct"].str.rstrip("%").astype(float)
d["det"] = (d["score"] >= THRESHOLD).astype(int)
d["clip"] = d["file_id"].str.rsplit("_", n=1).str[0]
ai, hum = d[d["class"] == "AI"], d[d["class"] == "HUM"]
print(f"{len(d)} valid queries ({len(ai)} AI, {len(hum)} control); {len(excluded)} excluded.")
print(f"Score range shown by the tool: {d['score'].min():g} to {d['score'].max():g}. "
      f"{(ai['score'] == ai['score'].max()).sum()} of {len(ai)} AI queries at the maximum.\n")

# Recall by condition and model
rows = []
for cond in CONDS:
    for model in ["all", "v2", "fl", "v3", "v2+fl"]:
        sub = ai[ai["condition"] == cond]
        if model == "v2+fl":
            sub = sub[sub["model"].isin(["v2", "fl"])]
        elif model != "all":
            sub = sub[sub["model"] == model]
        k, n = int(sub["det"].sum()), len(sub)
        lo, hi = wilson(k, n)
        rows.append({"condition": cond, "model": model, "detected": k, "n": n,
                     "recall": round(k / n, 3), "ci_low": round(lo, 3), "ci_high": round(hi, 3),
                     "mean_score": round(sub["score"].mean(), 1)})
recall = pd.DataFrame(rows)
recall.to_csv(RESULTS / "summary_recall.csv", index=False)

# False-positive rate
rows = []
for cond in CONDS + ["all"]:
    sub = hum if cond == "all" else hum[hum["condition"] == cond]
    k, n = int(sub["det"].sum()), len(sub)
    lo, hi = wilson(k, n)
    rows.append({"condition": cond, "flagged": k, "n": n, "fpr": round(k / n, 3),
                 "ci_low": round(lo, 3), "ci_high": round(hi, 3), "max_score": sub["score"].max()})
fpr = pd.DataFrame(rows)
fpr.to_csv(RESULTS / "summary_fpr.csv", index=False)

# Paired tests
wide = ai.pivot_table(index="clip", columns="condition", values="det")
meta = ai.drop_duplicates("clip").set_index("clip")[["model", "lang", "voice", "script"]]
wide = wide.join(meta)


def paired(a, b, frame):
    b10 = int(((frame[a] == 1) & (frame[b] == 0)).sum())
    b01 = int(((frame[a] == 0) & (frame[b] == 1)).sum())
    return b10, b01, mcnemar_exact(b10, b01)


tests = []
for a, b in [("C0", "C2"), ("C1", "C2")]:
    x, y, p = paired(a, b, wide)
    tests.append({"test": f"H2 {a} vs {b}", "pairs": len(wide), f"det_first_only": x,
                  "det_second_only": y, "p_exact": p})
h2_adj = holm([t["p_exact"] for t in tests])
for t, p in zip(tests, h2_adj):
    t["p_holm"] = p

v3 = wide[wide["model"] == "v3"]["C0"].rename("v3")
for other in ["v2", "fl"]:
    o = wide[wide["model"] == other][["lang", "voice", "script", "C0"]]
    key = lambda f: f["lang"] + f["voice"] + f["script"]
    m = pd.DataFrame({"v3": v3.values}, index=key(wide[wide["model"] == "v3"]).values)
    m[other] = pd.Series(o["C0"].values, index=key(o).values)
    x, y, p = paired(other, "v3", m)
    tests.append({"test": f"H3 {other} vs v3 (C0)", "pairs": len(m), "det_first_only": x,
                  "det_second_only": y, "p_exact": p, "p_holm": ""})

for cond in ["C1", "C2", "C3"]:
    x, y, p = paired("C0", cond, wide)
    tests.append({"test": f"Exploratory C0 vs {cond}", "pairs": len(wide), "det_first_only": x,
                  "det_second_only": y, "p_exact": p, "p_holm": ""})
tests = pd.DataFrame(tests)
tests.to_csv(RESULTS / "hypothesis_tests.csv", index=False)

# Reliability check (Section 5.3): first run vs second run on the retest sample
retest_path = RESULTS / "retest.csv"
retest_summary = None
if retest_path.exists():
    rt = pd.read_csv(retest_path, dtype=str)
    rt = rt[rt["raw_score_pct"].fillna("").str.strip() != ""]
    if len(rt):
        rt["score2"] = rt["raw_score_pct"].str.rstrip("%").astype(float)
        rt["det2"] = (rt["score2"] >= THRESHOLD).astype(int)
        rt = rt.merge(d[["file", "score", "det"]], on="file", how="left")
        rt["score_diff"] = rt["score2"] - rt["score"]
        k, n = int((rt["det"] == rt["det2"]).sum()), len(rt)
        lo, hi = wilson(k, n)
        retest_summary = {"files": n, "label_agreement": k, "agreement_rate": round(k / n, 3),
                          "ci_low": round(lo, 3), "ci_high": round(hi, 3),
                          "identical_scores": int((rt["score_diff"] == 0).sum()),
                          "mean_abs_score_diff": round(rt["score_diff"].abs().mean(), 2),
                          "max_abs_score_diff": rt["score_diff"].abs().max()}
        rt[["file", "score", "score2", "score_diff", "det", "det2"]].to_csv(
            RESULTS / "retest_comparison.csv", index=False)
        pd.DataFrame([retest_summary]).to_csv(RESULTS / "retest_agreement.csv", index=False)

# Charts
fig, ax = plt.subplots(figsize=(8, 4.5))
width = 0.25
for i, model in enumerate(["v2", "fl", "v3"]):
    r = recall[recall["model"] == model].set_index("condition").loc[CONDS]
    xs = [j + (i - 1) * width for j in range(4)]
    ax.bar(xs, r["recall"], width, label=MODEL_NAMES[model],
           yerr=[r["recall"] - r["ci_low"], r["ci_high"] - r["recall"]], capsize=3)
ax.set_xticks(range(4), [COND_NAMES[c] for c in CONDS])
ax.set_ylim(0, 1.05)
ax.set_ylabel("Recall (score at or above 50%)")
ax.set_title("Detection recall by audio condition and model (n = 6 per bar, 95% Wilson CI)")
ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.1))
fig.tight_layout()
fig.savefig(RESULTS / "recall_by_condition.png", dpi=200)

fig, ax = plt.subplots(figsize=(8, 4.5))
groups = [("v2", "Multilingual v2"), ("fl", "Flash v2.5"), ("v3", "Eleven v3"), ("HUM", "Human control")]
for gi, (g, label) in enumerate(groups):
    sub = hum if g == "HUM" else ai[ai["model"] == g]
    for ci, cond in enumerate(CONDS):
        s = sub[sub["condition"] == cond]["score"]
        x = ci + (gi - 1.5) * 0.18
        ax.scatter([x] * len(s), s, s=18, alpha=0.7, label=label if ci == 0 else None,
                   color=f"C{gi}")
ax.axhline(THRESHOLD, ls="--", lw=1, color="grey")
ax.set_xticks(range(4), [COND_NAMES[c] for c in CONDS])
ax.set_ylabel("Classifier score (%)")
ax.set_ylim(-2, 102)
ax.set_title("Raw classifier scores by condition (dashed line: decision threshold)")
ax.legend(frameon=False, ncol=4, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.1))
fig.tight_layout()
fig.savefig(RESULTS / "scores_by_condition.png", dpi=200)

pd.set_option("display.width", 160)
print("RECALL\n", recall.to_string(index=False), "\n")
print("FALSE POSITIVES\n", fpr.to_string(index=False), "\n")
print("TESTS\n", tests.to_string(index=False), "\n")
if retest_summary:
    r = retest_summary
    print(f"RETEST: {r['label_agreement']}/{r['files']} labels agree ({r['agreement_rate']:.0%}, "
          f"95% CI {r['ci_low']:.2f}-{r['ci_high']:.2f}); {r['identical_scores']} identical scores; "
          f"mean absolute score difference {r['mean_abs_score_diff']} points, max {r['max_abs_score_diff']:g}.")
else:
    print("RETEST: results/retest.csv not filled yet; run 06_label.py --retest.")
