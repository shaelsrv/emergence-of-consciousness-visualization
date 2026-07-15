"""
Deeper analysis: render a spectrogram + energy timeline + structural segments
as PNG so we can SEE the track's shape, then dump an event timeline as JSON
the visualization can play back in sync.
"""
import sys
import wave
import json
import numpy as np
from scipy.signal import stft
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PATH     = sys.argv[1] if len(sys.argv) > 1 else "track.wav"
OUT_PNG  = sys.argv[2] if len(sys.argv) > 2 else "track_overview.png"
OUT_JSON = sys.argv[3] if len(sys.argv) > 3 else "track_events.json"

# ---- load WAV ----
with wave.open(PATH, "rb") as w:
    n_channels = w.getnchannels()
    sample_width = w.getsampwidth()
    sr = w.getframerate()
    n_frames = w.getnframes()
    raw = w.readframes(n_frames)

# 24-bit decode
n = len(raw) // 3
a = np.frombuffer(raw, dtype=np.uint8).reshape(n, 3)
samples = a[:, 0].astype(np.int32) | (a[:, 1].astype(np.int32) << 8) | (a[:, 2].astype(np.int32) << 16)
samples = np.where(samples >= 0x800000, samples - 0x1000000, samples)
arr = samples.astype(np.float32) / 8388608.0
if n_channels == 2:
    arr = arr.reshape(-1, 2)
    mono = arr.mean(axis=1)
else:
    mono = arr
duration_s = mono.shape[0] / sr
print(f"track: {duration_s:.1f}s, sr={sr}")

# ---- STFT (covers the whole track at coarse resolution) ----
nperseg = 4096
hop = 1024
f, t, Z = stft(mono, fs=sr, nperseg=nperseg, noverlap=nperseg - hop)
spec = np.abs(Z)
log_spec = np.log1p(spec * 20)
print(f"stft: {log_spec.shape[1]} frames, hop={hop} ({hop/sr*1000:.1f} ms)")

# ---- structural segmentation: detect sections via energy + spectral change ----
# Per-second energy envelope (rms)
sec_block = int(sr * 1.0)
n_secs = mono.shape[0] // sec_block
rms_per_sec = np.array([np.sqrt(np.mean(mono[i*sec_block:(i+1)*sec_block]**2))
                         for i in range(n_secs)])
# Spectral centroid per second (brightness)
freqs_full = np.fft.rfftfreq(sec_block, 1/sr)
centroid_per_sec = []
for i in range(n_secs):
    seg = mono[i*sec_block:(i+1)*sec_block]
    spec_seg = np.abs(np.fft.rfft(seg))
    if spec_seg.sum() > 1e-8:
        centroid_per_sec.append(np.sum(spec_seg * freqs_full) / spec_seg.sum())
    else:
        centroid_per_sec.append(0)
centroid_per_sec = np.array(centroid_per_sec)

# ---- per-band energy over time (for sectioning + visualisation) ----
bands = [
    ("sub",     20,    60,   "#3a2a1a"),
    ("kick",    40,    120,  "#c9844a"),
    ("bass",    60,    250,  "#e8c4a0"),
    ("low_mid", 250,   800,  "#a89878"),
    ("snare",   200,   3000, "#e8e1d4"),
    ("perc",    1000,  5000, "#948876"),
    ("hat",     5000,  12000,"#6b8a8f"),
]
band_energy_t = {}
for name, lo, hi, _ in bands:
    mask = (f >= lo) & (f < hi)
    if not np.any(mask):
        band_energy_t[name] = np.zeros(spec.shape[1])
        continue
    band_energy_t[name] = spec[mask, :].mean(axis=0)

# ---- onset times per band (for the JSON event timeline) ----
events = {}
print("\n=== per-band onset extraction ===")
for name, lo, hi, _ in bands:
    mask = (f >= lo) & (f < hi)
    if not np.any(mask):
        events[name] = []
        continue
    band = spec[mask, :]
    diff = np.maximum(0, band[:, 1:] - band[:, :-1])
    flux = diff.sum(axis=0)
    med = np.median(flux) + 1e-8

    # Adaptive threshold per band, picked from the analysis we did:
    # 2.4x median for high-onset bands, 2.0x for slower bands
    multiplier = {"sub":2.6, "kick":2.6, "bass":2.4, "low_mid":2.0, "snare":2.0, "perc":1.9, "hat":1.6}.get(name, 2.0)
    threshold = multiplier * med
    # debounce in stft frames
    debounce_frames = {"sub":3, "kick":3, "bass":4, "low_mid":8, "snare":15, "perc":4, "hat":3}.get(name, 4)
    above = np.where(flux > threshold)[0]
    onsets = []
    last = -999
    for idx in above:
        if idx - last >= debounce_frames:
            onset_t = (idx + 1) * hop / sr   # absolute time in seconds
            strength = float(min(1.0, (flux[idx] - threshold) / max(threshold, 1e-4)))
            onsets.append([round(onset_t, 4), round(strength, 3)])
            last = idx
    events[name] = onsets
    print(f"  {name:8s}  {len(onsets):>4d} onsets")

# ---- look for the BREAKDOWN / DROP structure ----
# A "drop" is a moment where bass suddenly comes in after low-energy section.
# Detect by looking at the bass band energy timeline.
bass_energy = band_energy_t["bass"]
# Smooth over ~1 second
smooth_n = int(1.0 / (hop / sr))
kernel = np.ones(smooth_n) / smooth_n
bass_smooth = np.convolve(bass_energy, kernel, mode="same")
# Per-second downsample
sec_per_frame = hop / sr
seconds_axis = np.arange(len(bass_smooth)) * sec_per_frame

# Detect rising edges in bass energy (drops)
norm_bass = bass_smooth / (bass_smooth.max() + 1e-8)
drops = []
for i in range(1, len(norm_bass) - 1):
    if norm_bass[i] > 0.5 and norm_bass[i-1] < 0.25:
        # Found a drop
        drops.append(round(i * sec_per_frame, 2))

# Detect falling edges (breakdowns)
breakdowns = []
for i in range(1, len(norm_bass) - 1):
    if norm_bass[i] < 0.20 and norm_bass[i-1] > 0.45:
        breakdowns.append(round(i * sec_per_frame, 2))

print(f"\ndrops (bass enters): {drops}")
print(f"breakdowns (bass leaves): {breakdowns}")

# ---- write JSON event timeline ----
out = {
    "duration": round(duration_s, 3),
    "bpm": 184.6,
    "beat_period_s": 60.0 / 184.6,
    "sample_rate": sr,
    "drops": drops,
    "breakdowns": breakdowns,
    "events": events,
    "loudness_per_sec": [round(float(r), 4) for r in rms_per_sec],
    "centroid_per_sec": [round(float(c), 1) for c in centroid_per_sec],
}
with open(OUT_JSON, "w") as fh:
    json.dump(out, fh, separators=(",", ":"))
print(f"\nwrote: {OUT_JSON}  ({sum(len(v) for v in events.values())} total onsets)")

# ---- render the overview PNG ----
fig, axes = plt.subplots(4, 1, figsize=(20, 12), gridspec_kw={"height_ratios":[3, 1, 1, 1]})
ax = axes[0]
# Log-spectrogram, capped at 15 kHz for readability
fmask = f < 15000
ax.imshow(log_spec[fmask], aspect="auto", origin="lower",
          extent=[0, duration_s, 0, f[fmask][-1] / 1000],
          cmap="magma", vmin=0, vmax=log_spec.max() * 0.85)
ax.set_ylabel("freq (kHz)")
ax.set_title("spectrogram (log magnitude, 0–15 kHz)")
# Overlay drop / breakdown markers
for d in drops:
    ax.axvline(d, color="cyan", alpha=0.6, lw=1.0)
for b in breakdowns:
    ax.axvline(b, color="yellow", alpha=0.6, lw=1.0, linestyle="--")

ax = axes[1]
ax.plot(seconds_axis, bass_smooth / (bass_smooth.max() + 1e-8), label="bass", color="#c9844a")
ax.plot(seconds_axis, band_energy_t["low_mid"] / (band_energy_t["low_mid"].max() + 1e-8), label="low-mid", color="#a89878", alpha=0.8)
ax.plot(seconds_axis, band_energy_t["snare"] / (band_energy_t["snare"].max() + 1e-8), label="snare", color="#e8e1d4", alpha=0.7)
ax.set_xlim(0, duration_s); ax.set_ylim(0, 1.05)
ax.legend(loc="upper right", fontsize=8)
ax.set_ylabel("normalised energy")
ax.set_title("band energy over time")

ax = axes[2]
ax.plot(np.arange(n_secs), rms_per_sec, color="#e8e1d4")
ax.fill_between(np.arange(n_secs), rms_per_sec, alpha=0.2, color="#c9844a")
ax.set_xlim(0, n_secs); ax.set_ylabel("rms")
ax.set_title("loudness envelope (per second)")

ax = axes[3]
ax.plot(np.arange(n_secs), centroid_per_sec, color="#6b8a8f")
ax.set_xlim(0, n_secs); ax.set_ylabel("centroid (Hz)")
ax.set_title("spectral centroid (brightness) per second")

plt.tight_layout()
plt.savefig(OUT_PNG, dpi=80, facecolor="#0a0907")
print(f"wrote: {OUT_PNG}")
