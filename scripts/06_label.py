"""Speed up manual querying of the public classifier (Section 5.1).

The classifier has no public API, so each file is uploaded by hand through
the web interface. This helper removes the bookkeeping. For each unlabelled
row of results/labels.csv, in the committed upload order, it:
  1. copies the file's full path to the clipboard (Windows),
  2. waits for you to upload it and type the score shown,
  3. applies the decision rule (>= 50 is detected), stamps the UTC time,
     and saves the sheet immediately.

In the browser's upload dialog, press Ctrl+V in the file-name box, then Enter.

What to type at the prompt:
  98        the percentage shown
  98 s      same, and you saved a screenshot as evidence/screenshots/<file_id>.png
  x         the query failed (error or no result); counts as an attempt
  t <text>  a categorical result with no percentage, recorded verbatim
  q         save and quit; rerun later to continue where you stopped

A file with no valid result after 3 attempts is marked excluded (Section 7).

Run:              python scripts/06_label.py
Retest (5.3):     python scripts/06_label.py --retest
"""
import argparse, csv, subprocess, sys
from datetime import datetime, timezone
from design import DEGRADED, RESULTS

sys.stdout.reconfigure(encoding="utf-8")
p = argparse.ArgumentParser()
p.add_argument("--retest", action="store_true")
args = p.parse_args()

sheet = RESULTS / ("retest.csv" if args.retest else "labels.csv")
with sheet.open(encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    fields, rows = reader.fieldnames, list(reader)
if args.retest:
    first = {r["file"]: r for r in csv.DictReader((RESULTS / "labels.csv").open(encoding="utf-8"))}
    if any(not first[r["file"]]["detected"] for r in rows):
        sys.exit("Finish all 96 first-run queries before the retest.")


def save():
    with sheet.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def to_clipboard(text):
    try:
        subprocess.run("clip", input=text.encode("ascii", "ignore"), check=True, shell=True, capture_output=True)
        return True
    except Exception:
        return False


todo = [r for r in rows if not r["detected"]]
print(f"{len(rows) - len(todo)} of {len(rows)} done. {len(todo)} to go.\n")
for r in todo:
    path = DEGRADED / r["file"]
    tag = f"[{r.get('position', '-')}] {r['file']}"
    copied = to_clipboard(str(path))
    while True:
        attempts = int(r.get("attempts") or 0) if "attempts" in r else 0
        ans = input(f"{tag}{' (path copied)' if copied else ''}\n  score> ").strip()
        if ans.lower() == "q":
            save(); sys.exit("Saved. Rerun to continue.")
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        if ans.lower() == "x":
            if "attempts" in r:
                r["attempts"] = attempts + 1
                if attempts + 1 >= 3:
                    r.update(detected="excluded", query_timestamp_utc=stamp,
                             notes=(r.get("notes", "") + " no valid result after 3 attempts").strip())
                    save(); print("  excluded after 3 attempts\n"); break
            save(); print("  attempt logged, try again"); continue
        if ans.lower().startswith("t "):
            r.update(result_text=ans[2:].strip(), detected="MAP_MANUALLY", query_timestamp_utc=stamp)
            if "attempts" in r:
                r["attempts"] = attempts + 1
            save(); print("  categorical result saved; map it to 1 or 0 by hand and log the mapping\n"); break
        parts = ans.split()
        try:
            score = float(parts[0].rstrip("%"))
            assert 0 <= score <= 100
        except (ValueError, AssertionError, IndexError):
            print("  enter a number 0-100, 'x', 't <text>' or 'q'"); continue
        r.update(raw_score_pct=f"{score:g}", detected="1" if score >= 50 else "0",
                 query_timestamp_utc=stamp)
        if "attempts" in r:
            r["attempts"] = attempts + 1
        if len(parts) > 1 and parts[1].lower() == "s" and "screenshot" in r:
            r["screenshot"] = f"{r['file_id']}.png"
        save(); print(f"  saved: {score:g}% -> {'detected' if score >= 50 else 'not detected'}\n"); break

print("All rows in this sheet are complete.")
