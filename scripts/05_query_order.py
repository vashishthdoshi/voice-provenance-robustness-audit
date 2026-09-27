"""Fix the classifier upload order and the retest sample before querying (Sections 5.1, 5.3).

Writes:
  results/query_order.csv  the 96 files in randomised upload order (fixed seed)
  results/labels.csv       blank labelling sheet in that order, to fill in while querying
  results/retest.csv       the 12 files to query a second time (fixed seed)

Commit all three before the first upload. Refuses to overwrite.
Run: python scripts/05_query_order.py
"""
import csv, random, sys
from design import DEGRADED, RESULTS, QUERY_ORDER_SEED, RETEST_SEED, RETEST_N, CONDITIONS

sys.stdout.reconfigure(encoding="utf-8")
outs = [RESULTS / n for n in ("query_order.csv", "labels.csv", "retest.csv")]
if any(p.exists() for p in outs):
    sys.exit("Output already exists. The order is fixed once; do not regenerate it.")

files = sorted(p.name for p in DEGRADED.iterdir()
               if p.stem.rsplit("_", 1)[-1] in CONDITIONS)
if len(files) != 96:
    sys.exit(f"Found {len(files)} condition files, expected 96. Run 03_degrade.py first.")

order = files[:]
random.Random(QUERY_ORDER_SEED).shuffle(order)
retest = sorted(random.Random(RETEST_SEED).sample(files, RETEST_N))

RESULTS.mkdir(exist_ok=True)
with outs[0].open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["position", "file"])
    w.writerows(enumerate(order, 1))

cols = ["position", "file", "file_id", "class", "model", "lang", "voice", "script",
        "condition", "raw_score_pct", "result_text", "detected", "attempts",
        "query_timestamp_utc", "screenshot", "notes"]
with outs[1].open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for i, name in enumerate(order, 1):
        stem = name.rsplit(".", 1)[0]
        clip, cond = stem.rsplit("_", 1)
        parts = clip.split("_")
        row = {c: "" for c in cols}
        row.update(position=i, file=name, file_id=stem, condition=cond, **{"class": parts[0]})
        if parts[0] == "AI":
            row.update(model=parts[1], lang=parts[2], voice=parts[3], script=parts[4])
        else:
            row.update(lang=parts[1], script=parts[2])
        w.writerow(row)

with outs[2].open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["file", "raw_score_pct", "result_text", "detected", "query_timestamp_utc"])
    w.writerows([[n, "", "", "", ""] for n in retest])

print(f"Upload order, labelling sheet and {RETEST_N}-file retest sample written to results/.")
print(f"Seeds: order {QUERY_ORDER_SEED}, retest {RETEST_SEED}. Commit these files before querying.")
