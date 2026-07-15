"""
Advanced analysis on top of analyze_deep.py:
  - stereo panning per second (L-vs-R energy)
  - downbeats (which kick is the "1" of every 4-beat bar)
  - section boundaries (novelty curve over an 8-band self-similarity matrix)

Appends pan_per_sec, downbeats, and sections to the existing track_events.json.
"""
import sys
import wave
import json
import numpy as np
from scipy.signal import stft

PATH      = sys.argv[1] if len(sys.argv) > 1 else "track.wav"
JSON_PATH = sys.argv[2] if len(sys.argv) > 2 else "track_events.json"

# ---- load WAV (24-bit stereo) ----
with wave.open(PATH, "rb") as w:
    n_channels = w.getnchannels()
    sr = w.getframerate()
    n_frames = w.getnframes()
    raw = w.readframes(n_frames)

n = len(raw) // 3
a = np.frombuffer(raw, dtype=np.uint8).reshape(n, 3)
samples = a[:, 0].astype(np.int32) | (a[:, 1].astype(np.int32) << 8) | (a[:, 2].astype(np.int32) << 16)
samples = np.where(samples >= 0x800000, samples - 0x1000000, samples)
arr = samples.astype(np.float32) / 8388608.0
if n_channels == 2:
    arr = arr.reshape(-1, 2)
    L = arr[:, 0]
    R = arr[:, 1]
    mono = arr.mean(axis=1)
else:
    L = R = arr
    mono = arr
duration_s = mono.shape[0] / sr
print(f"track: {duration_s:.1f}s, sr={sr}, channels={n_channels}")

# ---- load existing JSON ----
with open(JSON_PATH, "r", encoding="utf-8") as fh:
    score = json.load(fh)

# =====================================================================
# 1. STEREO PANNING — per second
# =====================================================================
sec_block = int(sr * 1.0)
n_secs = mono.shape[0] // sec_block
pan_per_sec = []
for i in range(n_secs):
    Lrms = np.sqrt(np.mean(L[i*sec_block:(i+1)*sec_block]**2))
    Rrms = np.sqrt(np.mean(R[i*sec_block:(i+1)*sec_block]**2))
    total = Lrms + Rrms + 1e-8
    pan = (Rrms - Lrms) / total      # -1 = full left, +1 = full right
    pan_per_sec.append(round(float(pan), 4))
print(f"pan: min={min(pan_per_sec):+.3f} max={max(pan_per_sec):+.3f} mean={np.mean(pan_per_sec):+.4f}")

# =====================================================================
# 2. DOWNBEATS — find phase of the 4-beat bar grid via kick alignment
# =====================================================================
bpm = score.get("bpm", 184.6)
# Beat period (we'll search over both the bpm and bpm/2 — common ambiguity)
candidates = [bpm, bpm / 2.0]
kicks = score["events"].get("kick", [])
kick_times = np.array([k[0] for k in kicks])
kick_strengths = np.array([k[1] for k in kicks])

best_overall = None
for trial_bpm in candidates:
    beat_period = 60.0 / trial_bpm
    bar_period = beat_period * 4
    if bar_period > duration_s * 0.5:
        continue
    best_phase = 0
    best_score = -1
    # Search 1/8-beat phase grid
    for phase in np.arange(0, bar_period, beat_period / 8):
        # For each kick, compute distance to nearest bar start; reward kicks near a bar start
        nearest = ((kick_times - phase) / bar_period).round() * bar_period + phase
        dist = np.abs(kick_times - nearest)
        within = dist < beat_period * 0.15      # within 15% of beat
        score_v = float(kick_strengths[within].sum())
        if score_v > best_score:
            best_score = score_v
            best_phase = phase
    cand_info = (trial_bpm, best_phase, best_score, bar_period)
    if best_overall is None or best_score > best_overall[2]:
        best_overall = cand_info
    print(f"  bpm={trial_bpm:6.1f}  phase={best_phase:.3f}s  alignment_score={best_score:.2f}")

best_bpm, best_phase, _, bar_period = best_overall
beat_period = 60.0 / best_bpm
downbeats = list(np.arange(best_phase, duration_s, bar_period))
print(f"chosen bpm={best_bpm}, bar_period={bar_period:.3f}s, {len(downbeats)} downbeats")

# =====================================================================
# 3. SECTION BOUNDARIES — novelty curve on 8-band feature self-similarity
# =====================================================================
# Build feature vector per second: log-band energies (6 bands)
band_edges = [(20, 60), (60, 250), (250, 800), (800, 2200), (2200, 5000), (5000, 12000)]
freqs_full = np.fft.rfftfreq(sec_block, 1/sr)
features = []
for i in range(n_secs):
    seg = mono[i*sec_block:(i+1)*sec_block]
    spec = np.abs(np.fft.rfft(seg))
    fv = []
    for lo, hi in band_edges:
        mask = (freqs_full >= lo) & (freqs_full < hi)
        fv.append(np.log1p(spec[mask].sum()))
    features.append(fv)
features = np.array(features)
# Normalize per-feature (z-score)
features = (features - features.mean(axis=0)) / (features.std(axis=0) + 1e-8)

# Self-similarity matrix (cosine similarity)
def cosine_matrix(F):
    norms = np.linalg.norm(F, axis=1, keepdims=True) + 1e-8
    Fn = F / norms
    return Fn @ Fn.T
sim = cosine_matrix(features)

# Novelty: checkerboard correlation. K = 8 seconds.
K = 8
size = 2 * K
kernel = np.zeros((size, size))
for ii in range(size):
    for jj in range(size):
        s_i = 1 if ii < K else -1
        s_j = 1 if jj < K else -1
        kernel[ii, jj] = s_i * s_j

novelty = np.zeros(n_secs)
for t in range(K, n_secs - K):
    novelty[t] = np.sum(sim[t-K:t+K, t-K:t+K] * kernel)

# Find peaks above a robust threshold
threshold = np.median(novelty) + 1.5 * np.std(novelty)
min_gap = 12  # at least 12 seconds between section boundaries
peaks = []
last = -999
for t in range(K + 1, n_secs - K - 1):
    if novelty[t] > novelty[t-1] and novelty[t] > novelty[t+1] and novelty[t] > threshold:
        if t - last >= min_gap:
            peaks.append(t)
            last = t
# always start at 0 and append final boundary
sections = [0] + peaks + [n_secs]
print(f"sections: {sections}  (count = {len(sections)-1})")

# =====================================================================
# write back
# =====================================================================
score["pan_per_sec"] = pan_per_sec
score["downbeats"]   = [round(float(d), 3) for d in downbeats]
score["bar_period"]  = round(float(bar_period), 4)
score["sections"]    = [int(s) for s in sections]
score["bpm_chosen"]  = round(float(best_bpm), 2)

with open(JSON_PATH, "w", encoding="utf-8") as fh:
    json.dump(score, fh, separators=(",", ":"))
print(f"updated: {JSON_PATH}")
print(f"  + pan_per_sec ({len(pan_per_sec)} values)")
print(f"  + downbeats ({len(downbeats)} bars)")
print(f"  + sections ({len(sections)-1} segments)")
