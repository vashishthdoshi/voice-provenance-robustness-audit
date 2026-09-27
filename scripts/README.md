# Scripts

Run in order from the repository root. Each file describes its inputs and outputs at the top.

| Script | Purpose | Uses API credits |
|---|---|---|
| `design.py` | Models, voice and script assignment, and seeds. Reads script texts from the preregistration | No |
| `00_check_setup.py` | Checks ffmpeg, the API key, model availability and character quota | No |
| `01_select_voices.py` | Applies the preregistered voice-selection rule and writes `data/voices.json` | No |
| `02_generate.py` | Generates the 18 AI clips and logs every attempt | Yes |
| `03_degrade.py` | Produces conditions C0 to C3 for all 24 source clips | No |
| `04_manifest.py` | Writes the SHA-256 hash of every audio file to `data/MANIFEST.csv` | No |
| `05_query_order.py` | Fixes the upload order, labelling sheet and retest sample | No |
| `06_label.py` | Records scores and applies the decision rule during manual querying | No |
| `07_analyse.py` | Computes recall, false-positive rates, tests, retest agreement and charts | No |
