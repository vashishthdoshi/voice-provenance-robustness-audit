"""Write data/MANIFEST.csv: one row per audio file with its SHA-256 hash.

Covers data/raw, data/controls and data/degraded. Adds generation settings
for AI clips (from data/voices.json) and recording details for controls
(from data/controls_meta.csv, filled in by hand). The manifest is tracked
in Git; the audio is not. Safe to re-run: it is rebuilt from the files.

Run: python scripts/04_manifest.py
"""
import csv, hashlib, json, subprocess, sys
from design import DATA, RAW, CONTROLS, DEGRADED, MODELS, OUTPUT_FORMAT, PROFICIENCY

sys.stdout.reconfigure(encoding="utf-8")
AUDIO = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac", ".webm", ".mp4"}
FIELDS = ["file", "folder", "clip_id", "attempt_kept", "condition", "class", "model_code", "model_id",
          "lang", "voice", "voice_id", "script", "output_format", "speaker_proficiency",
          "device", "app", "native_format", "duration_s", "sample_rate", "channels",
          "bytes", "sha256"]


def sha256(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0",
                          "-show_entries", "stream=sample_rate,channels:format=duration",
                          "-of", "json", str(p)], capture_output=True, text=True).stdout
    d = json.loads(out or "{}")
    s = (d.get("streams") or [{}])[0]
    return (round(float(d.get("format", {}).get("duration", 0)), 3),
            s.get("sample_rate", ""), s.get("channels", ""))


voices_path = DATA / "voices.json"
voices = json.loads(voices_path.read_text(encoding="utf-8")) if voices_path.exists() else {}
meta = {}
meta_path = DATA / "controls_meta.csv"
if meta_path.exists():
    with meta_path.open(encoding="utf-8") as f:
        meta = {r["clip_id"]: r for r in csv.DictReader(f)}

rows = []
for folder in (RAW, CONTROLS, DEGRADED):
    for p in sorted(folder.iterdir()):
        if p.suffix.lower() not in AUDIO:
            continue
        stem, _, kept = p.stem.partition(".attempt")  # earlier generation attempts kept on regeneration
        cond = stem.rsplit("_", 1)[1] if stem.rsplit("_", 1)[-1] in ("C0", "C1", "C2", "C3") else ""
        clip = stem[: -len(cond) - 1] if cond else stem
        parts = clip.split("_")
        r = {k: "" for k in FIELDS}
        r.update(file=p.name, folder=folder.name, clip_id=clip, attempt_kept=kept, condition=cond,
                 bytes=p.stat().st_size, sha256=sha256(p))
        r["duration_s"], r["sample_rate"], r["channels"] = probe(p)
        if parts[0] == "AI" and len(parts) == 5:
            _, code, lang, voice, script = parts
            r.update({"class": "AI", "model_code": code, "model_id": MODELS.get(code, ""),
                      "lang": lang, "voice": voice, "script": script,
                      "voice_id": voices.get(voice, {}).get("voice_id", ""),
                      "output_format": OUTPUT_FORMAT})
        elif parts[0] == "HUM" and len(parts) == 3:
            _, lang, script = parts
            m = meta.get(clip, {})
            r.update({"class": "HUM", "lang": lang, "script": script,
                      "speaker_proficiency": PROFICIENCY.get(lang, ""),
                      "device": m.get("device", ""), "app": m.get("app", ""),
                      "native_format": m.get("native_format", "")})
        rows.append(r)

with (DATA / "MANIFEST.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(rows)

counts = {k: sum(r["folder"] == k for r in rows) for k in ("raw", "controls", "degraded")}
print(f"MANIFEST.csv written: {len(rows)} files {counts}")
print("Expected: raw 18 (plus any kept earlier attempts), controls 6, degraded 96.")
