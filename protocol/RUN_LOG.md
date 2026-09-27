# Run Log

Dated record of every action taken in this study, in chronological order. Entries are appended and never edited. Corrections are made as new entries that reference the original.

|Date (UTC)|Action|Details|Commit|
|-|-|-|-|
|2026-09-26|Repository initialised|Folder structure, data policy, .gitignore and license|126bba2|
|2026-09-26|Live classifier page accessed|https://elevenlabs.io/ai-speech-classifier. Eleven v3 and other-provider limitations recorded. Screenshot: evidence/screenshots/live\_classifier\_page.png|1ff8491|
|2026-09-26|Former documentation page checked|No current page publishes a precision or recall figure|1ff8491|
|2026-09-26|Archived documentation accessed|Snapshot dated 2026-09-26 reports 99% precision and 80% recall on unmodified audio. Source: https://web.archive.org/web/20250909200109/https://elevenlabs.io/docs/product-guides/audio-tools/ai-speech-classifier<br />Screenshot: evidence/screenshots/archived\_docs\_faq.png|1ff8491|
|2026-09-26|Protocol registered|PREREGISTRATION.md committed before any data generation|1ff8491|
|2026-09-26|Seeds fixed|Noise 20260926, query order 20260927, retest 20260928|e2f9245|
|2026-09-26|Implementation specified|Voice rule applied as: VA = first premade voice with a male or female label, VB = next premade voice with the other label. C2 resamples before band-pass. C3 SNR uses whole-clip mean power; output 44.1 kHz mono WAV. Retest sample drawn before querying with the fixed seed|e2f9245|
|2026-09-26|Voices selected|Rule applied to 21 premade voices. VA: Roger (male), CwhRBWXzGAHq8TQ4Fs17. VB: Sarah (female), EXAVITQu4vr4xnSDxMaL. Full ordered list in data/voices.json|e2f9245|
|2026-09-26|Regenerated "AI\_fl\_HI\_VA\_S2.mp3" and "AI\_v3\_HI\_VB\_S3.mp3". Wrong language corrected for the latter with the second generation.|"order (English = 'order')" and "oar se (English = 'from')" is mis-pronounced as "oren-der" and "orus-ae" respectively \|  First attempts kept as AI\_fl\_HI\_VA\_S2.attempt1.mp3 and AI\_v3\_HI\_VB\_S3.attempt1.mp3 respectively|930d64f|
|2026-09-26|All controls generated|Best take of 3 used. No copies kept of failed takes for easier management|100644|
|2026-09-26|Degradation run|96 condition files produced from 24 sources. Seven C3 files scaled down to prevent clipping, SNR unchanged: AI\_fl\_EN\_VB\_S2 (0.9650), AI\_fl\_HI\_VB\_S3 (0.9248), AI\_v3\_EN\_VB\_S2 (0.9084), AI\_v3\_HI\_VB\_S3 (0.9183), AI\_v3\_ES\_VB\_S1 (0.9140), HUM\_ES\_S1 (0.8339). Manifest: 20 raw including 2 kept attempts, 6 controls, 96 degraded|(this commit)|



