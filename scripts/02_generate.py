"""Generate the 18 AI source clips (Section 4.2).

Default voice settings, output format mp3_44100_128, one generation per clip.
Existing files are never overwritten. Every attempt is appended to
data/generation_log.csv. Per Section 7, each clip may be attempted twice at most.

Run:               python scripts/02_generate.py
Preview (free):    python scripts/02_generate.py --dry-run
Second attempt for one clip (only after listening and logging the reason):
                   python scripts/02_generate.py --regenerate AI_v2_EN_VA_S1
"""
import argparse, csv, json, os, sys, time
from datetime import datetime, timezone
import requests
from dotenv import load_dotenv
from design import ROOT, DATA, RAW, API_BASE, OUTPUT_FORMAT, load_scripts, ai_jobs

sys.stdout.reconfigure(encoding="utf-8")
p = argparse.ArgumentParser()
p.add_argument("--dry-run", action="store_true")
p.add_argument("--regenerate", metavar="CLIP_ID")
args = p.parse_args()

LOG = DATA / "generation_log.csv"
FIELDS = ["timestamp_utc", "clip_id", "attempt", "model_id", "voice_label", "voice_id",
          "lang", "script", "chars", "output_format", "http_status", "request_id",
          "bytes", "outcome", "file"]

voices = json.loads((DATA / "voices.json").read_text(encoding="utf-8"))
scripts = load_scripts()
load_dotenv(ROOT / ".env")
key = os.environ.get("ELEVENLABS_API_KEY", "")

attempts = {}
if LOG.exists():
    with LOG.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            attempts[row["clip_id"]] = attempts.get(row["clip_id"], 0) + 1


def log(row):
    new = not LOG.exists()
    with LOG.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)


jobs = ai_jobs()
if args.regenerate:
    jobs = [j for j in jobs if j["clip_id"] == args.regenerate]
    if not jobs:
        sys.exit(f"Unknown clip ID {args.regenerate}")

RAW.mkdir(parents=True, exist_ok=True)
for j in jobs:
    cid, n_prev = j["clip_id"], attempts.get(j["clip_id"], 0)
    path = RAW / f"{cid}.mp3"
    if args.regenerate:
        if n_prev >= 2:
            print(f"SKIP {cid}: already attempted twice (Section 7 limit)")
            continue
        if path.exists():
            kept = path.with_name(f"{cid}.attempt{n_prev}.mp3")
            path.rename(kept)  # the earlier attempt is kept, never overwritten
            print(f"Kept earlier attempt as {kept.name}")
    elif path.exists():
        print(f"SKIP {cid}: file exists")
        continue

    text = scripts[j["script"]][j["lang"]]
    vid = voices[j["voice"]]["voice_id"]
    if args.dry_run:
        print(f"DRY  {cid}: {j['model_id']}, voice {j['voice']}, {len(text)} chars")
        continue

    r = requests.post(f"{API_BASE}/v1/text-to-speech/{vid}",
                      params={"output_format": OUTPUT_FORMAT},
                      headers={"xi-api-key": key, "Content-Type": "application/json"},
                      json={"text": text, "model_id": j["model_id"]}, timeout=180)
    good = r.status_code == 200 and r.headers.get("content-type", "").startswith("audio")
    if good:
        path.write_bytes(r.content)
    log({"timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
         "clip_id": cid, "attempt": n_prev + 1, "model_id": j["model_id"],
         "voice_label": j["voice"], "voice_id": vid, "lang": j["lang"], "script": j["script"],
         "chars": len(text), "output_format": OUTPUT_FORMAT, "http_status": r.status_code,
         "request_id": r.headers.get("request-id", ""),
         "bytes": len(r.content) if good else 0,
         "outcome": "ok" if good else r.text[:200].replace("\n", " "),
         "file": path.name if good else ""})
    print(f"{'OK  ' if good else 'FAIL'} {cid} (HTTP {r.status_code})")
    time.sleep(1)
