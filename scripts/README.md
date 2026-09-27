# Scripts

Run in order from the repository root, inside the project environment (`conda activate vpra`).

| Script | What it does | Uses API characters |
|---|---|---|
| `design.py` | Shared constants: models, voice-script assignment, seeds. Reads script texts from `protocol/PREREGISTRATION.md` | No |
| `00_check_setup.py` | Checks ffmpeg, API key, model availability and character quota | No |
| `01_select_voices.py` | Applies the preregistered voice-selection rule and writes `data/voices.json` | No |
| `02_generate.py` | Generates the 18 AI clips into `data/raw/`, logging every attempt to `data/generation_log.csv` | Yes |
| `03_degrade.py` | Produces conditions C0 to C3 for all 24 source clips into `data/degraded/` | No |
| `04_manifest.py` | Hashes every audio file into `data/MANIFEST.csv` | No |
| `05_query_order.py` | Fixes the randomised upload order, labelling sheet and retest sample in `results/` | No |

Seeds are fixed in `design.py` and recorded in `protocol/RUN_LOG.md` before use.
