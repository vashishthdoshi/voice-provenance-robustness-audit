"""Check the environment is ready before any generation.

Checks ffmpeg and ffprobe, the API key, API access, the three model IDs,
remaining character quota, and that the scripts can be read from the
preregistration. Makes no generation calls and uses no characters.

Run: python scripts/00_check_setup.py
"""
import os, shutil, sys
import requests
from dotenv import load_dotenv
from design import ROOT, API_BASE, MODELS, load_scripts, ai_jobs

sys.stdout.reconfigure(encoding="utf-8")
ok = True


def report(label, passed, detail=""):
    global ok
    ok &= passed
    print(f"[{'OK' if passed else 'FAIL'}] {label}{': ' + detail if detail else ''}")


for tool in ("ffmpeg", "ffprobe"):
    report(f"{tool} on PATH", shutil.which(tool) is not None)

scripts = load_scripts()
report("Scripts read from preregistration", True,
       "; ".join(f"{s} {len(t['EN'])}/{len(t['HI'])}/{len(t['ES'])} chars EN/HI/ES" for s, t in scripts.items()))
chars_needed = sum(len(scripts[j["script"]][j["lang"]]) for j in ai_jobs())

load_dotenv(ROOT / ".env")
key = os.getenv("ELEVENLABS_API_KEY", "")
report("API key found in .env", bool(key) and key != "your_api_key_here")
if not ok:
    sys.exit(1)

h = {"xi-api-key": key}
r = requests.get(f"{API_BASE}/v1/models", headers=h, timeout=30)
report("API reachable", r.status_code == 200, f"HTTP {r.status_code}")
if r.status_code == 200:
    available = {m["model_id"]: m for m in r.json()}
    for mid in MODELS.values():
        m = available.get(mid)
        langs = {l.get("language_id") for l in (m or {}).get("languages", [])}
        detail = "not listed" if m is None else f"en={'en' in langs}, hi={'hi' in langs}, es={'es' in langs}"
        report(f"Model {mid}", m is not None, detail)

r = requests.get(f"{API_BASE}/v1/user/subscription", headers=h, timeout=30)
if r.status_code == 200:
    s = r.json()
    left = s.get("character_limit", 0) - s.get("character_count", 0)
    report("Character quota", left >= chars_needed * 2,
           f"{left} left; about {chars_needed} needed, checked at 2x to allow regenerations")
else:
    print(f"[WARN] Could not read quota (HTTP {r.status_code}). Check it in the dashboard.")

print("\nReady." if ok else "\nFix the FAIL items above before continuing.")
sys.exit(0 if ok else 1)
