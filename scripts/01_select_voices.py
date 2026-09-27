"""Apply the preregistered voice-selection rule (Section 4.2).

VA is the first premade voice in library order with a male or female label.
VB is the next premade voice with the other label. Writes data/voices.json
with both IDs and the full ordered list of premade voices, so the
selection can be audited. Runs once; refuses to overwrite.

Run: python scripts/01_select_voices.py
"""
import json, os, sys
from datetime import datetime, timezone
import requests
from dotenv import load_dotenv
from design import ROOT, DATA, API_BASE

sys.stdout.reconfigure(encoding="utf-8")
out = DATA / "voices.json"
if out.exists():
    sys.exit(f"{out.name} already exists. Selection runs once; delete it only with a RUN_LOG entry.")

load_dotenv(ROOT / ".env")
r = requests.get(f"{API_BASE}/v1/voices",
                 headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]}, timeout=30)
r.raise_for_status()
premade = [v for v in r.json()["voices"] if v.get("category") == "premade"]
listing = [{"order": i, "voice_id": v["voice_id"], "name": v["name"],
            "gender": ((v.get("labels") or {}).get("gender") or "").lower()}
           for i, v in enumerate(premade)]
if not listing:
    sys.exit("No premade voices returned. Check the account and API key.")

va = next((v for v in listing if v["gender"] in ("male", "female")), None)
vb = None
if va:
    vb = next((v for v in listing if v["order"] > va["order"]
               and v["gender"] in ("male", "female") and v["gender"] != va["gender"]), None)
if not (va and vb):
    sys.exit("Could not find one male and one female premade voice. Stop and log this in RUN_LOG.md.")

record = {
    "selected_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "rule": "VA = first premade voice with a male or female label; VB = next premade voice with the other label.",
    "VA": va, "VB": vb, "premade_voices_in_order": listing,
}
out.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"VA: {va['name']} ({va['gender']}) {va['voice_id']}")
print(f"VB: {vb['name']} ({vb['gender']}) {vb['voice_id']}")
print(f"{len(listing)} premade voices listed. Saved to data/{out.name}")
