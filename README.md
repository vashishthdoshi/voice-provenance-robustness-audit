# Voice Provenance Robustness Audit

**Status:** Pilot study, complete. Findings were shared with the ElevenLabs safety team as this repository was made public.

## Research question

How robust is a production AI-voice provenance classifier when AI-generated audio is modified in ways that commonly occur in real-world distribution related safety-failure-modes that can be exploited by bad actors, such as compression, telephone transmission and background noise?

## Background

The ElevenLabs AI Speech Classifier is a free public tool. It estimates the probability that an audio sample was generated with ElevenLabs technology, and it needs no account. That makes it the tool most likely to be used by someone checking a suspicious voicemail or call recording.

An earlier version of the ElevenLabs documentation reported 99% precision and 80% recall on unmodified ElevenLabs audio. That page is no longer live, and the figure is cited from an archived copy. The current public page states that audio from the Eleven v3 model is not reliably classified. ElevenLabs now describes the classifier as a legacy tool and recommends its Audio Detector for signed-in users. The Audio Detector checks for a watermark first and falls back to the classifier. It is out of scope here.

Recorded audio rarely reaches a listener unmodified. Calls pass through telephone codecs, clips are recompressed when shared, and recordings pick up background noise. This study measures how the classifier performs under those conditions.

## Design

The full design was registered in `protocol/PREREGISTRATION.md` before any audio was generated or any query was made.

**AI-generated audio.** Three ElevenLabs models (Multilingual v2, Flash v2.5 and Eleven v3) generated three benign scripts in English, Hindi and Spanish, using two premade library voices. Scripts were assigned to voices so that every model read identical text in the same voice and language. This gave 18 source clips and allows paired comparisons between models.

**Human controls.** The study author recorded the same six language and script combinations. The author speaks English professionally, Hindi fluently and Spanish conversationally, so the Spanish controls test non-native speech. Non-native speech is a known source of false positives in synthetic-speech detection.

**Conditions.** Every clip was tested in four versions produced by a deterministic script.

|ID|Condition|Processing|
|-|-|-|
|C0|Clean|Original file|
|C1|Compression|MP3 at 64 kbps|
|C2|Telephone|8 kHz mono, 300 to 3400 Hz band-pass, G.711 μ-law|
|C3|Noise|Pink noise at 10 dB signal-to-noise ratio, fixed seed|

**Querying.** All 96 files were uploaded to the public web interface in a single session on 26 and 27 September 2026, in an order randomised with a fixed seed and committed beforehand. A file counted as detected if the classifier's score was 50% or higher. Twelve files chosen by seed were queried a second time to check reliability.

**Analysis.** Recall and false-positive rates are reported with 95% Wilson intervals. Paired comparisons use exact McNemar tests, with Holm correction across the preregistered telephone tests.

## Results

The classifier gave identical scores on all 12 retested files, so the results below reflect stable outputs.

**Detection of AI-generated audio (clips detected out of 6)**

|Model|Clean|MP3 64 kbps|Telephone|Noise 10 dB|
|-|-|-|-|-|
|Multilingual v2|6|6|6|6|
|Flash v2.5|6|6|6|6|
|Eleven v3|5|5|4|0|
|Eleven v3 mean score|79%|75%|53%|18%|

**Human controls.** None of the 24 control queries was flagged. Every control scored 2%, the lowest value the tool displays. This held for the non-native Spanish recordings.

!\[Recall by condition and model](results/recall\_by\_condition.png)

!\[Raw scores by condition](results/scores\_by\_condition.png)

**Hypotheses**

||Hypothesis|Result|
|-|-|-|
|H1|Clean recall for v2 and Flash is consistent with the published 80%|Supported. 12 of 12 detected (95% CI 0.76 to 1.00), which includes 0.80.|
|H2|Telephone audio lowers recall compared with clean and compressed audio|Not supported. Recall for v2 and Flash was unchanged. Eleven v3 scores fell from a mean of 79% to 53%, but only three clips changed label, in both directions (Holm-adjusted p = 1.0).|
|H3|Clean Eleven v3 audio is detected less often than v2 and Flash|Consistent in direction. 5 of 6 against 12 of 12, with one discordant pair (p = 1.0).|
|H4|No more than 1 of 24 controls is flagged|Supported. 0 of 24 (95% CI 0 to 0.14).|

**Exploratory.** Added noise produced the largest change. All five Eleven v3 clips detected in their clean form fell below the threshold with noise added, and no clip moved in the reverse direction of analyses (exact p = 0.06, uncorrected). For v2 and Flash, noise lowered some scores from 98% to between 82% and 93%, even as every clip stayed above the threshold. Eleven v3 clips in English held higher scores than Hindi and Spanish under clean, compressed and telephone conditions. The sample is too small to separate language from script or voice.

## Takeaways

For Multilingual v2 and Flash v2.5 audio, the classifier held up under every condition tested. Clean-audio recall in this sample was 12 of 12, consistent with the previously published figure.

Eleven v3 is where detection is fragile. ElevenLabs already flags this model as a limitation, and this study measures how that limitation grows under ordinary conditions. Telephone transmission pulled v3 scores toward the threshold. Pink noise at 10 dB signal-to-noise ratio worsened v3 scores to less than the threshold (50%).

This matters for how results are read. A user who uploads a noisy v3 clip sees a low score, with a label between "Uncertain" and "Very unlikely." The v3 warning is visible with the result on the upload page of the classifier itself. Showing the model limitation alongside low-scoring results, and publishing recall by model and by audio condition, would help users read any low score better.

The false-positive result is reassuring for this sample. No human recording was flagged, including non-native speech. This doesn't come as a surprise, given the lack of polish that generally comes with AI generated audio.

## Limitations

* Each model and condition cell contains six clips, so intervals are wide. The results are indicative.
* The tool displays scores between 2% and 98%. Forty-seven of the 72 AI queries sat at 98%, so small effects on v2 and Flash audio would not be visible.
* Each condition was tested at one setting. Other bitrates, noise levels and codecs may behave differently.
* The clips are short, with two voices and three scripts. All controls come from one speaker. The coverage of linguistic diversity will require significantly larger samples.
* The classifier is a black box and may change. Results describe its behaviour on 26 and 27 September 2026.
* The study covers the standalone classifier. It does not test the watermark-based Audio Detector.

## Deviations from the protocol

Deviations are recorded with dates in `protocol/RUN\_LOG.md`.

## Repository structure

|Path|Contents|
|-|-|
|`protocol/`|Preregistration and dated run log|
|`scripts/`|Generation, audio processing, hashing, query ordering, labelling and analysis|
|`data/MANIFEST.csv`|SHA-256 hash and settings for every audio file|
|`data/voices.json`|Voice selection record|
|`data/generation\_log.csv`|Every generation request|
|`data/controls\_meta.csv`|Recording details for the human controls|
|`results/`|Classifier scores, summary tables, test results and charts|
|`evidence/screenshots/`|Captures of the classifier documentation|

## Data policy

Audio files are not published. The repository includes the full pipeline, a hash of every audio file, all classifier scores and the aggregate results. The analysis can be verified from these files without releasing audio that could be used to test ways of evading detection. Screen recordings of the query session are held by the author, with their hashes recorded in the run log.

## Reproducing this study

Requirements: Python 3.10 or later, ffmpeg and an ElevenLabs account. Add your API key to `.env` after copying it from `.env.example`.

```
conda create -n vpra -c conda-forge python=3.12 ffmpeg -y
conda activate vpra
pip install -r requirements.txt
copy .env.example .env

python scripts/00\_check\_setup.py
python scripts/01\_select\_voices.py
python scripts/02\_generate.py
# record the six human controls into data/controls/
python scripts/03\_degrade.py
python scripts/04\_manifest.py
python scripts/05\_query\_order.py
python scripts/06\_label.py            # manual upload to the web classifier
python scripts/06\_label.py --retest
python scripts/07\_analyse.py
```

The analysis can be rerun from `results/labels.csv` alone with `python scripts/07\_analyse.py`. Regenerated audio may not match the published hashes, because generation is not guaranteed to be deterministic.

## License

Code is released under the MIT License. Results and documentation are released under CC BY 4.0.

