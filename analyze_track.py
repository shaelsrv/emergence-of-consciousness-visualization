"""
Analyse the user's WAV: spectral content, dynamic range, onset density per band,
estimated BPM. Output a JSON-ish report we'll use to tune the visualization.
"""
import sys
import wave
import numpy as np
from scipy.signal import stft

PATH = sys.argv[1] if len(sys.argv) > 1 else "track.wav"

with wave.open(PATH, "rb") as w:
    n_channels = w.getnchannels()
    sample_width = w.getsampwidth()
    sr = w.getframerate()
    n_frames = w.getnframes()
    raw = w.readframes(n_frames)

print(f"channels: {n_channels}")
print(f"sample rate: {sr} Hz")
print(f"sample width: {sample_width} bytes")
print(f"frames: {n_frames}")
print(f"duration: {n_frames / sr:.2f} s")

# decode samples
if sample_width == 2:
    dtype = np.int16
    scale = 1 / 32768.0
elif sample_width == 3:
    dtype = None  # special-case 24-bit
    scale = 1 / 8388608.0
elif sample_width == 4:
    dtype = np.int32
    scale = 1 / 2147483648.0
else:
    raise SystemExit(f"unsupported sample width: {sample_width}")

if dtype is not None:
    arr = np.frombuffer(raw, dtype=dtype).astype(np.float32) * scale
else:
    # 24-bit decode
    n = len(raw) // 3
    a = np.frombuffer(raw, dtype=np.uint8).reshape(n, 3)
    samples = a[:, 0].astype(np.int32) | (a[:, 1].astype(np.int32) << 8) | (a[:, 2].astype(np.int32) << 16)
    samples = np.where(samples >= 0x800000, samples - 0x1000000, samples)
    arr = samples.astype(np.float32) * scale

if n_channels == 2:
    arr = arr.reshape(-1, 2)
    mono = arr.mean(axis=1)
else:
    mono = arr

# Use a 30-second window for analysis (whole file is too big to print)
window_s = 30.0
start_s = min(20.0, mono.shape[0] / sr / 4)  # skip intro
end_s = min(start_s + window_s, mono.shape[0] / sr)
i0 = int(start_s * sr); i1 = int(end_s * sr)
x = mono[i0:i1]
print(f"\nanalysing window {start_s:.1f}–{end_s:.1f}s ({x.shape[0]} samples)")

# Overall stats
peak = np.max(np.abs(x))
rms = np.sqrt(np.mean(x ** 2))
print(f"peak: {peak:.3f}")
print(f"rms: {rms:.3f}")
print(f"crest factor: {peak / max(rms, 1e-8):.2f}  (high = transient-heavy, low = compressed)")

# STFT for spectral content
nperseg = 2048
hop = 512
f, t, Z = stft(x, fs=sr, nperseg=nperseg, noverlap=nperseg - hop)
spec = np.abs(Z)
print(f"\nstft: {spec.shape[1]} frames, {spec.shape[0]} bins, hop={hop} samples ({hop/sr*1000:.1f} ms)")

# Per-band energy distribution
bands = {
    "sub": (20, 60),
    "kick": (40, 120),
    "bass": (60, 250),
    "low_mid": (250, 800),
    "snare/clap": (200, 3000),
    "perc": (1000, 5000),
    "hat": (5000, 12000),
    "air": (10000, 20000),
}
print("\nper-band energy (mean of |X(f)| over the window):")
for name, (lo, hi) in bands.items():
    mask = (f >= lo) & (f < hi)
    if not np.any(mask):
        continue
    band_energy = spec[mask, :].mean()
    print(f"  {name:12s}  {lo:>5}–{hi:>5} Hz  mean={band_energy:.4f}")

# Onset detection per band via spectral flux
def spectral_flux(spec, mask):
    band = spec[mask, :]
    diff = np.maximum(0, band[:, 1:] - band[:, :-1])
    flux = diff.sum(axis=0)
    return flux

print("\nonset density per band (spectral flux peaks above 2x median):")
for name, (lo, hi) in bands.items():
    mask = (f >= lo) & (f < hi)
    if not np.any(mask):
        continue
    flux = spectral_flux(spec, mask)
    med = np.median(flux) + 1e-8
    peaks = np.sum(flux > 2.0 * med)
    rate = peaks / (end_s - start_s)
    print(f"  {name:12s}  {peaks:>4d} peaks  ({rate:.2f}/sec)  median_flux={med:.4f}")

# Estimate BPM from broadband onset envelope autocorrelation
flux_all = spectral_flux(spec, np.ones_like(f, dtype=bool))
# normalise + autocorrelate
fa = flux_all - flux_all.mean()
ac = np.correlate(fa, fa, mode="full")
ac = ac[len(ac) // 2:]
# convert STFT-frame index to seconds
frame_dt = hop / sr
# look at lags 0.3 .. 1.0 seconds (60 .. 200 BPM)
lag_min = int(0.3 / frame_dt); lag_max = int(1.0 / frame_dt)
peak_lag = int(np.argmax(ac[lag_min:lag_max]) + lag_min)
period_s = peak_lag * frame_dt
print(f"\nestimated tempo period: {period_s*1000:.0f} ms -> {60/period_s:.1f} BPM")

# Beat-strength: look at flux at 1/2, 1/4, 1/8 of estimated period
print(f"beat subdivisions (relative to flux at beat period):")
base = ac[peak_lag]
for sub_name, factor in [("beat", 1.0), ("half", 0.5), ("quarter", 0.25), ("eighth", 0.125)]:
    lag = int(round(peak_lag * factor))
    if lag > 0 and lag < len(ac):
        print(f"  {sub_name:10s}  lag={lag*frame_dt*1000:.0f}ms  strength={ac[lag]/base:+.3f}")

# Dynamic range across window
env = np.abs(x)
env_smoothed = np.convolve(env, np.ones(int(sr * 0.05)) / int(sr * 0.05), mode='same')
print(f"\nenvelope min/max/mean: {env_smoothed.min():.3f} / {env_smoothed.max():.3f} / {env_smoothed.mean():.3f}")

# Loudness over time — find quiet vs loud sections
window_block = int(sr * 1.0)  # 1-second blocks
n_blocks = mono.shape[0] // window_block
loudness_per_sec = np.array([np.sqrt(np.mean(mono[i*window_block:(i+1)*window_block]**2))
                              for i in range(n_blocks)])
print(f"\nloudness per second (full file): min={loudness_per_sec.min():.3f} max={loudness_per_sec.max():.3f}")
print(f"quiet sections (rms<{loudness_per_sec.min()*1.3:.3f}): {int(np.sum(loudness_per_sec < loudness_per_sec.min()*1.3))} of {n_blocks} seconds")
print(f"loud sections (rms>{loudness_per_sec.max()*0.85:.3f}): {int(np.sum(loudness_per_sec > loudness_per_sec.max()*0.85))} of {n_blocks} seconds")
