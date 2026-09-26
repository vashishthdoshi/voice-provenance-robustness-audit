# Preregistration

**Study:** Voice Provenance Robustness Audit (pilot)
**Status:** Registered before any audio was generated or any classifier query was made. The Git commit timestamp of this file is the record of registration. Any later change to this file is visible in the commit history and is also logged in `RUN\\\_LOG.md` as a deviation.

## 1\. Objective

To measure how the detection performance of the ElevenLabs AI Speech Classifier changes when ElevenLabs-generated speech is modified in ways common to real-world distribution, and to compare the results with the performance the classifier's documentation reports for unmodified audio.

## 2\. System under test

* **Tool:** ElevenLabs AI Speech Classifier, public web interface.
* **Documented behaviour at time of registration:** The tool returns the probability that a sample was generated with ElevenLabs technology and analyses the first minute of each sample. The public page states that it does not reliably classify audio generated with the Eleven v3 model and cannot detect audio from other providers.
* **Previously published performance:** An earlier version of the ElevenLabs documentation reported 99% precision and 80% recall on unmodified ElevenLabs audio. That documentation page is no longer live, and no current page publishes a performance figure. The figure is taken from a wayback machine archived page.
* **Sources:** https://elevenlabs.io/ai-speech-classifier (live) and https://web.archive.org/web/20250909200109/https://elevenlabs.io/docs/product-guides/audio-tools/ai-speech-classifier (archived). Access dates are recorded in `RUN\\\_LOG.md`, and screenshots of both are stored in `evidence/screenshots/`.
* **Scope:** ElevenLabs now describes this classifier as a legacy tool and recommends the Audio Detector, which checks for an audio watermark and falls back to the classifier when none is found. The Audio Detector requires sign-in and is out of scope. This study tests the standalone public classifier only, because it is the tool available without an account to anyone checking a suspicious recording.
* The classifier is treated as a black box. Its version cannot be observed, so all queries are completed within as short a window as practical, and query dates are recorded.

## 3\. Hypotheses

* **H1 (baseline):** Recall on clean audio from Multilingual v2 and Flash v2.5 is consistent with the previously published 80%, meaning the 95% confidence interval includes 0.80.
* **H2 (telephone channel):** Recall under the telephone condition (C2) is lower than recall on clean audio (C0), and lower than recall under compression (C1).
* **H3 (model):** Recall on clean Eleven v3 audio is lower than recall on clean Multilingual v2 and Flash v2.5 audio.
* **H4 (false positives):** Human-recorded control audio is rarely flagged. The expectation is no more than 1 of 24 control queries at or above the decision threshold.

Differences by language and the effect of added noise (C3) are exploratory and are not tested as hypotheses.

## 4\. Design

### 4.1 Scripts

Three benign scripts, each about 130 to 160 characters in English, translated into Hindi and Spanish. No script names a real person or organisation, requests money or requests credentials.

|ID|Type|English|Hindi|Spanish|
|-|-|-|-|-|
|S1|Narration|The library opens at nine on weekdays and closes early on Sundays. Please return borrowed books to the front desk before leaving.|पुस्तकालय सप्ताह के दिनों में सुबह नौ बजे खुलता है और रविवार को जल्दी बंद हो जाता है। कृपया जाने से पहले उधार ली गई किताबें सामने की डेस्क पर लौटा दें।|La biblioteca abre a las nueve entre semana y cierra temprano los domingos. Por favor, devuelva los libros prestados en el mostrador antes de salir.|
|S2|Customer service|Thank you for calling. Your order has been shipped and should arrive within three business days. Is there anything else I can help with?|कॉल करने के लिए धन्यवाद। आपका ऑर्डर भेज दिया गया है और तीन चालू दिन के भीतर पहुँच जाना चाहिए। क्या आपको किसी और चीज़ में मदद चाहिए?|Gracias por llamar. Su pedido ha sido enviado y debería llegar en un plazo de tres días hábiles. ¿Hay algo más en lo que pueda ayudarle?|
|S3|Account notice|Hello, this is a call from your bank's support team. We noticed a recent login from a new device and want to confirm it was you.|नमस्ते, यह आपके बैंक की सहायता टीम की ओर से कॉल है। हमने एक नए डिवाइस से हाल ही में हुआ लॉगिन देखा है और पुष्टि करना चाहते हैं कि वह आप ही थे।|Hola, le llamamos del equipo de soporte de su banco. Detectamos un inicio de sesión reciente desde un dispositivo nuevo y queremos confirmar que fue usted.|

### 4.2 AI-generated audio (positive class)

* **Models (3):** `eleven\\\_multilingual\\\_v2`, `eleven\\\_flash\\\_v2\\\_5`, `eleven\\\_v3`.
* **Languages (3):** English (EN), Hindi (HI), Spanish (ES).
* **Voices (2):** Two premade voices from the ElevenLabs default library, labelled VA and VB. Selection rule: the first two premade voices, in library order, that are available for all three models and all three languages, with one male-presenting and one female-presenting voice. Voice IDs are recorded in `data/MANIFEST.csv`.
* **Script assignment:** Each voice reads one script per language, balanced so every script appears twice per model. The same assignment is used for every model, so model comparisons are paired on identical text, voice and language.

|Voice|EN|HI|ES|
|-|-|-|-|
|VA|S1|S2|S3|
|VB|S2|S3|S1|

* **Total:** 3 models × 6 voice-language cells = **18 source clips**.
* **Generation settings:** default voice settings for each model, output format `mp3\\\_44100\\\_128`, one generation per clip. Request parameters are recorded in the manifest.

### 4.3 Human-recorded audio (negative controls)

* The study author records the same six language-script cells used above (EN-S1, HI-S2, ES-S3, EN-S2, HI-S3, ES-S1). That gives **6 control clips**.
* The author's proficiency differs by language: English (professional), Hindi (fluent), Spanish (conversational). Spanish controls are therefore read by a non-native speaker, and proficiency is recorded for every control clip in the manifest. Accented and non-native speech is a known source of false positives in synthetic-speech detection, so this is reported as part of the exploratory analysis.
* Each script is read from text at a natural pace. Up to three takes are allowed per cell, and the first take without a reading error is used. All takes are logged.
* Recording device, app and native format are recorded in the manifest. No other person's voice is recorded.

### 4.4 Audio conditions

Every source clip and every control clip is tested under four conditions, produced by a scripted, deterministic pipeline.

|ID|Condition|Processing|
|-|-|-|
|C0|Clean|Original file, unmodified|
|C1|Compression|Re-encoded to MP3 at 64 kbps|
|C2|Telephone channel|Resampled to 8 kHz mono, band-pass filtered 300 to 3400 Hz, encoded with G.711 μ-law, decoded to WAV|
|C3|Background noise|Pink noise added at 10 dB signal-to-noise ratio, fixed random seed|

**Total classifier queries:** (18 + 6) × 4 = **96**, plus the reliability check in Section 5.3.

### 4.5 File naming

* AI clips: `AI\\\_<model>\\\_<lang>\\\_<voice>\\\_<script>\\\_<condition>`, for example `AI\\\_v2\\\_HI\\\_VA\\\_S2\\\_C1`.
* Controls: `HUM\\\_<lang>\\\_<script>\\\_<condition>`, for example `HUM\\\_EN\\\_S1\\\_C2`.

Model short codes are `v2` (Multilingual v2), `fl` (Flash v2.5) and `v3` (Eleven v3).

## 5\. Procedure

### 5.1 Querying

1. Each file is uploaded once to the classifier web interface.
2. For each query, the following are recorded in `results/labels.csv`: file ID, class (AI or HUM), model, language, voice, script, condition, raw score, binary label and timestamp.
3. Upload order is randomised with a fixed seed. The seed and the resulting order are committed before querying begins.
4. Screenshots are taken for a subset of queries that includes at least one example from each condition and each class.

### 5.2 Decision rule

* A file is labelled **detected** if the classifier's reported probability is **50% or higher**.
* The raw score is always recorded so results can be recomputed at other thresholds.
* If the classifier reports a categorical result without a probability, the category is recorded verbatim and mapped to detected or not detected using the tool's own wording. The mapping is logged.

### 5.3 Reliability check

After all 96 queries, 12 files are selected with a fixed seed and queried a second time. Agreement between the two runs is reported. First-run results are used for all primary analyses.

## 6\. Analysis plan

* **Primary metric:** recall, the proportion of AI clips labelled detected, reported by condition and by model within each condition, with 95% Wilson confidence intervals.
* **False-positive rate:** the proportion of control clips labelled detected, reported by condition and overall, with 95% Wilson intervals.
* **H1:** compare the C0 recall interval for Multilingual v2 and Flash v2.5 clips (n = 12) with the previously published 0.80.
* **H2:** exact McNemar tests on paired clips, C0 vs C2 and C1 vs C2 (n = 18 pairs each). Holm correction is applied across all paired tests in this section.
* **H3:** C0 detection for v3 clips compared with the matched v2 and Flash clips, reported descriptively and with an exact McNemar test on matched pairs.
* **H4:** count of control queries labelled detected, out of 24.
* **Exploratory:** recall by language and under C3; the distribution of raw scores by condition; control scores by speaker proficiency (native or fluent vs non-native).
* **Sample size:** this is a pilot. Intervals will be wide, and results are reported as indicative. No claim of statistical significance is made without the correction above.

## 7\. Exclusions and deviations

* **Generation failure:** a clip that fails to generate, or that is audibly truncated or garbled, is regenerated once. Both attempts are logged.
* **Classifier error:** a failed query is retried up to two times. A file with no valid result after three attempts is excluded, and the exclusion is reported.
* **Deviations:** any change to this protocol after registration is logged in `RUN\\\_LOG.md` with the date, the change and the reason, and is reported in the final write-up. Recorded data is never overwritten.

## 8\. Ethics and responsible disclosure

* Only premade library voices and the study author's own voice are used. No third-party voice is cloned or recorded.
* Scripts are benign and contain no deceptive request for money or credentials.
* Generation complies with the ElevenLabs Terms of Service and Prohibited Use Policy.
* Results are shared with the ElevenLabs safety team before the repository is made public.
* Audio files are not published. The repository publishes code, file hashes, labelled scores and aggregate results only.

