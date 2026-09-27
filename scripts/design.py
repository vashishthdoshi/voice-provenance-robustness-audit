"""Study design constants shared by all scripts.

Script texts are read directly from protocol/PREREGISTRATION.md (Section 4.1)
so the generated audio always matches the registered protocol.
Nothing in this file should change after registration without a RUN_LOG entry.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREREG = ROOT / "protocol" / "PREREGISTRATION.md"
DATA = ROOT / "data"
RAW = DATA / "raw"
CONTROLS = DATA / "controls"
DEGRADED = DATA / "degraded"
RESULTS = ROOT / "results"

API_BASE = "https://api.elevenlabs.io"
OUTPUT_FORMAT = "mp3_44100_128"

# Model short code -> API model ID (Sections 4.2 and 4.5)
MODELS = {"v2": "eleven_multilingual_v2", "fl": "eleven_flash_v2_5", "v3": "eleven_v3"}
LANGS = ["EN", "HI", "ES"]
LANG_COLUMN = {"EN": 2, "HI": 3, "ES": 4}  # column index in the Section 4.1 table

# Script assignment (Section 4.2): voice -> language -> script
ASSIGNMENT = {
    "VA": {"EN": "S1", "HI": "S2", "ES": "S3"},
    "VB": {"EN": "S2", "HI": "S3", "ES": "S1"},
}

# Author proficiency per language (Section 4.3)
PROFICIENCY = {"EN": "professional", "HI": "fluent", "ES": "conversational"}

CONDITIONS = ["C0", "C1", "C2", "C3"]

# Fixed seeds. Values are recorded in RUN_LOG.md before use.
NOISE_SEED = 20260926
QUERY_ORDER_SEED = 20260927
RETEST_SEED = 20260928
RETEST_N = 12
SNR_DB = 10.0


def load_scripts():
    """Return {script_id: {lang: text}} parsed from the preregistration table."""
    scripts = {}
    for line in PREREG.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 5 and cells[0] in ("S1", "S2", "S3"):
            scripts[cells[0]] = {lang: cells[i] for lang, i in LANG_COLUMN.items()}
    if set(scripts) != {"S1", "S2", "S3"}:
        raise RuntimeError("Could not find S1-S3 in the Section 4.1 table of PREREGISTRATION.md")
    return scripts


def ai_jobs():
    """All 18 AI source clips, in a fixed order."""
    jobs = []
    for code, model_id in MODELS.items():
        for voice, row in ASSIGNMENT.items():
            for lang in LANGS:
                script = row[lang]
                jobs.append({
                    "clip_id": f"AI_{code}_{lang}_{voice}_{script}",
                    "model_code": code, "model_id": model_id,
                    "voice": voice, "lang": lang, "script": script,
                })
    return jobs


def control_cells():
    """The six human control cells, matching the AI language-script cells."""
    return [f"HUM_{lang}_{row[lang]}" for row in ASSIGNMENT.values() for lang in LANGS]
