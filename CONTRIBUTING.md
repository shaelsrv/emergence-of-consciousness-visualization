# Contributing

Read `CLAUDE.md` in full before adding a visualization. It is the
authoritative spec — aesthetic tokens, substrate library, file naming,
quality checklist. The short version:

## Adding a visualization

1. Pick a substrate from the §5 library that is **not already in the repo**.
   Check `substrates/INVENTORY.md` to see what's taken.
2. Follow the filename convention: `emergence_<substrate>_<modulation>.html`
3. Fill in the mandatory header block (§7.2) at the top of the file.
4. Apply the canonical tokens from §3. No Inter, no purple/cyan gradients,
   no neon. Warm dark palette only.
5. Route all modulation through substrate parameters — never directly to
   visible output (radius, alpha, position).
6. Run the falsifiability test (§1): can a competent observer predict the
   screen from the rules alone? If yes, redesign.
7. Update `substrates/INVENTORY.md`.
8. Add a 3–5 line README entry for your visualization.

## Analysis scripts

The Python scripts (`analyze_*.py`, `build_scored.py`, `sample_logo.py`)
accept their input paths as positional CLI arguments — no hardcoded paths.

```sh
python analyze_deep.py track.wav track_overview.png track_events.json
python analyze_advanced.py track.wav track_events.json
python build_scored.py emergence_scored.html track_events.json logo_targets.json
python sample_logo.py logo.png logo_targets.json
```

**Do not commit audio files or logo source images.** They are in `.gitignore`
and should stay local. The pre-extracted `track_events.json` and
`logo_targets.json` are committed because the standalone HTML files embed
them; the raw audio is not.

## Code style

- Single-file HTML artifacts only. No build step, no npm, no external JS
  dependencies beyond Google Fonts and (where unavoidable) one versioned CDN
  script.
- Canvas 2D for < 8k agents; WebGL fragment shaders for grid-based substrates
  at scale. See §8 of CLAUDE.md for the decision guide.
- No Tailwind, no CSS-in-JS, no frameworks.

## Running locally

Non-standalone HTML files use `fetch()` for JSON data and require a local
HTTP server (browsers block `fetch` from `file://`):

```sh
python -m http.server 8000
# then open http://localhost:8000/emergence_scored.html
```

Standalone (`*_standalone.html`) files work by double-clicking — JSON is
inlined. Build them with `build_scored.py`.
