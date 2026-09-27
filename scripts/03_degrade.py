"""Produce the four test conditions for every source and control clip (Section 4.4).

Inputs:  data/raw/AI_<model>_<lang>_<voice>_<script>.mp3   (18 files)
         data/controls/HUM_<lang>_<script>.<any audio ext> (6 files)
Outputs: data/degraded/<clip_id>_<condition>.<ext>          (96 files)

C0  Clean       byte-for-byte copy of the original
C1  Compression re-encoded to MP3 at 64 kbps
C2  Telephone   resampled to 8 kHz mono, band-pass 300-3400 Hz, encoded with
                G.711 mu-law, then decoded to 16-bit PCM WAV
C3  Noise       pink noise added at 10 dB SNR with a fixed seed, written as
                44.1 kHz mono 16-bit WAV. SNR uses mean power over the whole clip.

Existing outputs are never overwritten. Run: python scripts/03_degrade.py
"""
import shutil, subprocess, sys, tempfile, wave
from pathlib import Path
import numpy as np
from design import RAW, CONTROLS, DEGRADED, NOISE_SEED, SNR_DB, ai_jobs, control_cells

sys.stdout.reconfigure(encoding="utf-8")
BITEXACT = ["-fflags", "+bitexact", "-flags:a", "+bitexact", "-map_metadata", "-1"]
SR_C3 = 44100


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def decode_mono(src, sr):
    """Decode any audio file to a mono float32 array at sample rate sr."""
    out = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(src),
                          "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(out, dtype=np.float32).astype(np.float64)


def pink_noise(n, seed):
    """Pink (1/f power) noise via spectral shaping of seeded white noise, unit RMS."""
    rng = np.random.default_rng(seed)
    spec = np.fft.rfft(rng.standard_normal(n))
    f = np.arange(len(spec), dtype=np.float64)
    f[0] = 1.0
    x = np.fft.irfft(spec / np.sqrt(f), n)
    return x / np.sqrt(np.mean(x ** 2))


def write_wav16(path, x, sr):
    pcm = (np.clip(x, -1.0, 1.0) * 32767).round().astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def make(cond, src, stem):
    if cond == "C0":
        dst = DEGRADED / f"{stem}_C0{src.suffix.lower()}"
        if not dst.exists():
            shutil.copyfile(src, dst)
        return dst, ""
    if cond == "C1":
        dst = DEGRADED / f"{stem}_C1.mp3"
        if not dst.exists():
            ffmpeg("-i", str(src), "-vn", "-c:a", "libmp3lame", "-b:a", "64k", *BITEXACT, str(dst))
        return dst, ""
    if cond == "C2":
        dst = DEGRADED / f"{stem}_C2.wav"
        if not dst.exists():
            with tempfile.TemporaryDirectory() as td:
                mulaw = Path(td) / "mulaw.wav"
                ffmpeg("-i", str(src), "-vn", "-ac", "1",
                       "-af", "aresample=8000,highpass=f=300,lowpass=f=3400",
                       "-ar", "8000", "-c:a", "pcm_mulaw", *BITEXACT, str(mulaw))
                ffmpeg("-i", str(mulaw), "-c:a", "pcm_s16le", *BITEXACT, str(dst))
        return dst, ""
    if cond == "C3":
        dst = DEGRADED / f"{stem}_C3.wav"
        note = ""
        if not dst.exists():
            s = decode_mono(src, SR_C3)
            ps = np.mean(s ** 2)
            noise = pink_noise(len(s), NOISE_SEED) * np.sqrt(ps / 10 ** (SNR_DB / 10))
            mix = s + noise
            peak = np.max(np.abs(mix))
            if peak > 0.999:  # scale the whole mix down; SNR is unchanged
                mix *= 0.999 / peak
                note = f"mix scaled by {0.999 / peak:.4f} to avoid clipping"
            write_wav16(dst, mix, SR_C3)
            achieved = 10 * np.log10(ps / np.mean(noise ** 2))
            note = f"SNR {achieved:.2f} dB" + (f"; {note}" if note else "")
        return dst, note


def main():
    DEGRADED.mkdir(parents=True, exist_ok=True)
    sources = [(RAW / f"{j['clip_id']}.mp3", j["clip_id"]) for j in ai_jobs()]
    for cell in control_cells():
        found = sorted(p for p in CONTROLS.glob(f"{cell}.*") if p.suffix.lower() != ".md")
        sources.append((found[0] if found else CONTROLS / f"{cell}.MISSING", cell))

    missing = [stem for src, stem in sources if not src.exists()]
    if missing:
        print("Missing source files (skipped):\n  " + "\n  ".join(missing))

    made = 0
    for src, stem in sources:
        if not src.exists():
            continue
        for cond in ("C0", "C1", "C2", "C3"):
            dst, note = make(cond, src, stem)
            made += 1
            print(f"{dst.name}{'  (' + note + ')' if note else ''}")
    print(f"\n{made} condition files present from {len(sources) - len(missing)} sources.")


if __name__ == "__main__":
    main()
