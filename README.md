# emergence-of-consciousness-visualization

Procedural audio visualizations for emergencemachine.com — local rules on a
substrate, modulated by sound, producing global pattern. Single-file HTML
artifacts following the spec in [CLAUDE.md](CLAUDE.md): substrate + local
rules + audio modulation, warm-dark house aesthetic, no build step.

I created it for my track use it for your own if you like. 
Try it yourself at https://emergencemachine.com/tools/emergence-of-consciousness/
## Pipeline

```
analyze_deep.py        offline FFT + onset extraction → track_events.json + track_overview.png
build_scored.py        inlines track_events.json into any scored HTML → *_standalone.html
emergence_*.html       single-file visualizations (open directly or via local http)
```

The "scored" variants don't run real-time FFT — they replay a pre-extracted
event timeline against `audioEl.currentTime` for perfectly synced visuals.

## Final / recommended

- **`emergence_particle_storm_standalone.html`** — 2200-particle swarm where
  each frequency band applies a different physical force (bass = gravity well,
  snare = explosion, low-mid = swirl, hat = wind, etc.). Timeline inlined.
  Particles are also assigned target positions sampled from `logo.png` and
  pulled toward them with strength `progress^1.8`, so the swarm converges
  to the logo silhouette by the time the track ends. See `sample_logo.py`.
- **`emergence_scored_standalone.html`** — concentric ring model with the
  same scored architecture.
- **`emergence_circle_basic.html`** — minimal ground-truth (single circle with
  18 angular modes driven by FFT). The thing to fall back to when something
  more elaborate isn't reading.

## The iterations

The other `emergence_*.html` files are earlier substrates from the
exploration: physarum, kuramoto coupled oscillators, wave-membrane FDTD,
strange attractor (De Jong), driven harmonic lattice, 1D cellular automaton
on a log-frequency axis, and the tuned-per-instrument constellation. Each
followed the CLAUDE.md spec but ran into different mismatches with the
particular techno track that drove this project — different substrate
timescales, different anti-pattern boundaries. They're kept here as the
record of what *didn't* land and why.

## Local audio

The visualizations expect you to load a WAV/MP3 via the picker in the UI.
The offline analysis scripts accept input paths as CLI arguments — see
`CONTRIBUTING.md` for usage.

## Running non-standalone files

Files without `_standalone` in the name use `fetch()` to load JSON data.
Browsers block `fetch` from `file://`, so open them via a local HTTP server:

```sh
python -m http.server 8000
# then open http://localhost:8000/emergence_scored.html
```

Standalone variants (`*_standalone.html`) have the JSON inlined and work by
double-clicking.
