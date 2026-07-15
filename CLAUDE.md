# CLAUDE.md — Emergent Visualization Generator

You are operating inside the **Emergence Machine** visualization repository
(emergencemachine.com). Your job in this repo is to generate single-file,
production-ready procedural visualizations that demonstrate emergence — local
rules producing global pattern — and that aesthetically belong to the site.

Read this file in full before any generation task. Do not skim.

---

## 1.  The thesis you are illustrating

The site argues that complexity is not designed; it crystallizes when simple
local rules are coupled to a substrate. Every visualization in this repo must
embody that thesis literally, not metaphorically.

**Operational test (apply before shipping any output):**

> Could a competent observer, given only the rules, predict what the screen
> will look like ten seconds in?

- **Yes** → it is animation, not emergence. Reject and redesign.
- **No, but the rules clearly produce the pattern when run** → emergence. Ship.

If you find yourself drawing shapes, easing curves, or scripting motion paths,
stop. You are authoring. Author the *substrate and the rules*. The pattern is
not yours to draw.

---

## 2.  Anti-patterns — never generate these

Anything matching the description below is off-brand and structurally wrong,
regardless of how visually pleasant it looks.

- Bars, rings, or radial spectrums that pulse with bass.
  *(This is reactive decoration, not emergence.)*
- Purple/cyan gradients, neon palettes, glow-everywhere bloom.
- Particles spawning at click position with rainbow hue cycling.
- Lottie-style hand-keyframed motion masquerading as generative.
- Lorem-ipsum "data viz" with no actual data source.
- Anything that looks like a 2007 Winamp visualizer or a Codepen front page.
- More than three curl-noise flow-field variants in the repo. The substrate
  library is wide; lean on it. *(See §5.)*

If a request implicitly points at one of these, satisfy the *underlying goal*
with a different substrate, and note the substitution in the response.

---

## 3.  Aesthetic tokens (canonical)

These are the site's house tokens. Use them by default. Deviate only when a
specific brief calls for it, and document the deviation in the file header.

```css
:root {
  /* surface */
  --ink:        #0a0907;   /* near-black with warmth */
  --ink-2:      #14110d;   /* one step up for layered surfaces */
  --paper:      #e8e1d4;   /* warm off-white, primary mark */
  --paper-dim:  #948876;   /* muted, secondary mark */

  /* accent — used sparingly, on transients or to mark important state */
  --ember:      #c9844a;   /* warm amber */
  --slate:      #6b8a8f;   /* cool counter-accent (use only when needed) */

  /* rules / dividers */
  --rule:       rgba(232, 225, 212, 0.12);
}
```

**Typography**

- Display / italic emphasis: **Cormorant Garamond** (serif, weights 300–500,
  italic legitimate). This is the scholarly voice.
- Mono / HUD / metadata: **JetBrains Mono** (weights 300/400 only, lowercase,
  wide letter-spacing 0.18em–0.32em).
- Body when needed: Cormorant Garamond 400, 1.05rem, line-height 1.6.

Never use: Inter, Roboto, Space Grotesk, system-ui, Arial. They flatten the
voice into generic-tech.

**Compositional rules**

- Dark surface dominates. Marks are sparse.
- One accent color per visualization. Two if there is a clear pairing
  (substrate/agent, prediction/observation, etc.). Never three.
- Use hairline rules (1px, var(--rule)) instead of boxes/borders.
- Whitespace is structural, not decorative.
- HUD text in lowercase mono with `letter-spacing` reads as scientific notation,
  not chrome.

---

## 4.  What a "substrate" is in this repo

A substrate is the medium on which local rules act. The audio (or data, or
time) does not draw — it **modulates the substrate's parameters**, and the
particles/agents/cells follow their local rules over that modulated substrate.
The visible pattern is what falls out of that coupling.

Schematic for any file in this repo:

```
[ modulation source ]  →  [ substrate parameters ]  →  [ local rules ]  →  pattern
   audio / time / data       field scale, gain,           per-agent step
                             diffusion rate, threshold
```

If the modulation source goes directly to the pattern (e.g. "bass → circle
radius"), the file is broken. Route through substrate parameters.

---

## 5.  Substrate library — pick from these; rotate aggressively

Each new generation task should default to a substrate **not yet** in the
repo, unless the brief specifies. Maintain `/substrates/INVENTORY.md` so the
rotation is visible.

| # | Substrate | Mechanism | Visual signature |
|---|-----------|-----------|------------------|
| 1 | **Curl-noise flow field** | divergence-free vector field; particles advect | breathing ribbons, vortices |
| 2 | **Reaction-diffusion (Gray-Scott)** | two chemicals diffuse + react on a grid | spots, stripes, mitotic blobs |
| 3 | **Physarum (slime mold)** | agents deposit + follow pheromone trails | self-organizing networks |
| 4 | **Boids / flocking** | separation + alignment + cohesion per agent | murmuration |
| 5 | **Cellular automata (Wolfram / Lenia / Conway)** | discrete local rules on a grid | crystalline / organic depending on rule |
| 6 | **Diffusion-limited aggregation (DLA)** | random walkers stick on contact | fractal accretion, lightning, coral |
| 7 | **Differential growth / space colonization** | nodes split & repel; attractors guide growth | vascular networks, leaf venation |
| 8 | **Strange attractors (Lorenz, Clifford, de Jong)** | deterministic iterated map | filigree, smoke-like density fields |
| 9 | **Coupled oscillators (Kuramoto)** | phase-coupled oscillator lattice | synchronization waves |
| 10 | **Phase-field / Cahn-Hilliard** | spinodal decomposition | dewetting, marbling |
| 11 | **Wave interference / cymatics** | summed sinusoidal sources on a grid | nodal lines, standing waves |
| 12 | **L-systems / iterated function systems** | recursive rewriting | branching structures |

Stretch substrates (more code, ship when explicitly requested):

- **Coupled fields** (one substrate's output is another's input — closest
  literal match to E-stack composition)
- **Active matter (Vicsek, Toner-Tu)** — directional flocking on a density field
- **Self-organized criticality (sandpile, BTW model)** — avalanche dynamics
- **Reaction-advection-diffusion** — RD on top of a flow field

When a brief says "make an emergence visualization for X article," the right
move is usually to pick the substrate whose *mechanism* matches the article's
subject. Trust article → flock cohesion. Language → L-system or DLA.
Coordination failure → desynchronizing Kuramoto. Etc.

---

## 6.  Modulation sources

Pick the source(s) that make sense for the deliverable. List explicitly in
the file header.

- **Audio**: Web Audio API + AnalyserNode (`fftSize` 1024–4096). Split into 4
  perceptual bands (bass / low-mid / hi-mid / treble). Compute spectral
  centroid for palette temperature and spectral flux for onset detection.
  Always smooth the bands (single-pole IIR, α ≈ 0.15–0.2) before they touch
  the substrate.
- **Time**: autonomous evolution. Useful for ambient backgrounds, social
  posts, article headers.
- **Pointer / scroll**: light coupling — use as a slow modulator, not a
  driver. Never make the pattern chase the cursor; that's a toy.
- **Data**: JSON input (e.g. Lexicon Atlas concept JSON via the `.json`
  endpoint on any concept page). Map concept fields to substrate parameters
  in a documented mapping at the top of the file.
- **None**: pure deterministic evolution from a seed. Good for static-export
  poster images.

Routing constraint: **modulation → substrate parameters → rules → pattern**.
Never modulation → pattern directly.

---

## 7.  Output format

### 7.1  Single-file HTML artifact

Default deliverable. One `.html` file, no build step, no npm, no external JS
deps beyond Google Fonts and (if needed) a single CDN script. Must run by
double-clicking the file.

Structure inside the file, in this order:

1. `<!doctype html>` + meta + Google Fonts links
2. `<style>` block — CSS variables first, then layout, then components, then
   animations. No Tailwind. No CSS-in-JS.
3. `<canvas>` element + minimal HUD markup
4. `<script>` IIFE with sections numbered and commented:
   ```
   /* 1. canvas + DPR */
   /* 2. noise / substrate primitives */
   /* 3. agent state */
   /* 4. modulation source */
   /* 5. render loop */
   /* 6. UI / file handling */
   ```

### 7.2  File header (mandatory)

Every generated file begins with this comment block, filled in:

```html
<!--
  emergence machine · visualization
  substrate:    <name from §5 library>
  modulation:   <audio | time | pointer | data | none>
  mechanism:    <one sentence: what the local rule is>
  source:       <if data-driven, the schema/endpoint>
  fallback:     <what happens with no input>
  notes:        <any deviation from house tokens, with reason>
-->
```

This header is the file's falsifiability statement. If the substrate listed
here is `curl-noise flow field`, and the visible pattern was authored rather
than emergent, the file is honestly wrong and reviewable.

### 7.3  Filename convention

```
emergence_<substrate>_<modulation>[_<variant>].html
```

Examples:
- `emergence_physarum_audio.html`
- `emergence_reaction_diffusion_time.html`
- `emergence_boids_data_trust-article.html`

### 7.4  Performance floor

- 60fps on a 2019 MacBook Pro at 1440×900.
- DPR cap at 2.
- Particle counts: 2k–8k for canvas 2D, up to 100k for WebGL.
- Grid sizes: 256×256 for RD on canvas, 512×512 with WebGL.
- If a substrate cannot hit the floor, downgrade resolution before
  downgrading the mechanism. Visual coarseness is acceptable; mechanism
  compromise is not.

---

## 8.  WebGL vs Canvas 2D — when to pick which

- **Canvas 2D**: agent-based with < 8k agents (boids, flocking, physarum at
  small scale, curl-flow). Easy to ship. Use first.
- **WebGL fragment shader (GLSL)**: grid-based at scale (RD, CA, Lenia,
  wave fields, phase fields). Ping-pong framebuffers. Use when grid > 256.
- **WebGL with transform feedback or compute via texture state**: large-N
  particle systems (> 20k). Use when canvas can't hit the floor.

Don't reach for Three.js for 2D substrates. It's overhead for no gain.
Three.js earns its weight only for genuinely 3D coupled systems.

---

## 9.  Generation protocol — follow this when asked to produce a visualization

1. **Restate the brief in one sentence.** Identify the deliverable (article
   header, embedded interactive, social post, /visualizer page).
2. **Pick the substrate.** Default to the next un-used substrate in the
   inventory unless the brief points elsewhere. If a brief says "for the
   trust article," consult §5's mechanism-match heuristic.
3. **State the local rule in one sentence** in the file header. If you can't
   state it in one sentence, the rule is too complex — split or simplify.
4. **Wire the modulation through substrate parameters, never directly to
   visible output.** If audio is the source, route through field scale, gain,
   diffusion rate, threshold, or coupling strength — not through radius,
   alpha, or position.
5. **Apply tokens from §3** unless the brief authorizes deviation.
6. **Run the §1 falsifiability test mentally.** If the output is predictable
   from the rules alone, redesign.
7. **Render-check.** Open the file, watch it for thirty seconds with and
   without modulation. Confirm the substrate is alive in the absence of
   modulation (autonomous evolution baseline) and visibly responds when
   modulation engages.
8. **Update `/substrates/INVENTORY.md`** with the new file and its substrate.
9. **Write a 3–5 line README entry** explaining the mechanism in plain
   English. This is published; it's reader-facing. Use the Substack voice
   (concrete, noticing, no jargon).

---

## 10.  Repo layout

```
/visualizations/
├── CLAUDE.md                       ← this file
├── README.md                       ← public-facing index
├── tokens/
│   ├── aesthetic.css               ← :root variables, shared
│   └── tokens.json                 ← machine-readable copy
├── lib/                            ← shared primitives (no framework)
│   ├── noise.js                    ← value/perlin/simplex/curl helpers
│   ├── audio.js                    ← Web Audio + band split + onset
│   ├── canvas.js                   ← DPR-aware resize, feedback fade
│   └── glsl/                       ← shader snippets, ping-pong helper
├── substrates/                     ← one file per visualization
│   ├── INVENTORY.md                ← keep current
│   ├── emergence_curl_field_audio.html
│   ├── emergence_reaction_diffusion_time.html
│   └── ...
└── exports/                        ← static poster images / MP4 captures
```

When a single-file artifact would duplicate too much code, you may split
into `<substrate>.html` + `<substrate>.js` + `<substrate>.css` in a
subfolder — but keep the artifact runnable by opening the html directly. No
build step, ever.

---

## 11.  Tying outputs back to the framework

When a visualization is published in an article, the article should name the
substrate, state the local rule, and identify the modulation source. The
visualization is a *figure*, not decoration; readers should be able to
trace which sentence in the article each visual mechanism corresponds to.

When generating an embedded visualization, also produce a 1–2 sentence
caption that:
- Names the substrate.
- States the local rule.
- Identifies what's modulating it.

Example caption:

> *Substrate: agent-deposited pheromone trails (Physarum). Local rule: each
> agent senses three points ahead, turns toward the strongest trail, lays a
> trace. The graph is not drawn; it emerges from the agents.*

This caption is the difference between a figure that earns its place and
decoration that doesn't.

---

## 12.  Quality checks before declaring a task done

- [ ] File runs by double-clicking, no console errors.
- [ ] Header block (§7.2) is filled in honestly.
- [ ] Tokens from §3 are applied; no Inter, no purple gradients, no neon.
- [ ] Substrate is in the §5 library, or a documented stretch substrate.
- [ ] Modulation routes through substrate parameters, not directly to output.
- [ ] Pattern survives the §1 falsifiability test.
- [ ] 60fps confirmed on the performance floor (§7.4).
- [ ] `INVENTORY.md` updated.
- [ ] Caption written.
- [ ] If the substrate is one already in the inventory, deviation is
      justified in the file header.

---

## 13.  When unsure, ask one of these — never guess

- "Which deliverable is this for — article header, embedded figure, social
  post, or standalone page?" (Determines aspect ratio, autoplay,
  interactivity.)
- "Should this be audio-driven, data-driven, or autonomous?"
- "Is there an article it should bind to? If so, which mechanism do you
  want it to echo?"

Do not ask about color palette, typography, or filename. Those are answered
above and in this file.

---

## 14.  Spirit

You are not making music visualizers. You are building proofs. Each file is
a small, self-contained demonstration of the central claim of the site:
that complexity is not authored. It crystallizes when local rules meet a
substrate that can carry them.

The pattern on screen is the *consequence* of the coupling. If the
consequence is interesting, the coupling was honest. If it's boring or
predictable, the coupling was lazy and the rules need rewriting — not the
visuals decorated.

Build patiently. The substrate is the work.
