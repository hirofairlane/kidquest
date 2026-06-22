# KidQuest — Architecture

## Overview

KidQuest separates **content generation** (heavy, GPU-bound, run on demand) from **content
serving** (light, always-on) and from **game logic** (pure, fully tested, runs in the browser).

```
                         ┌──────────────────────────────────────────────┐
                         │  GENERATION (on demand, GPU box "blackwell")   │
   curricula/ + profile  │                                                │
        │                │  prompt_builder → llm_client (Ollama,          │
        ▼                │     format=daily_level.schema) → validate      │
  daily batch (manual) ──▶     → tts_piper (audio) → comfy_driver (sprite)│
                         │     → publisher → content-store/<profile>/<date>
                         └───────────────────────────┬────────────────────┘
                                                     │ writes
                                                     ▼
                                          content-store (on NAS)
                                                     ▲
                                                     │ reads (no inference)
        ┌────────────────────────────┐   HTTP   ┌────┴───────────────────────┐
        │  CLIENT (Phaser 3 + TS)    │ ───────▶ │  SERVER (FastAPI, 24/7 LXC) │
        │  engine/ (pure, Vitest)    │ ◀─────── │  profile store + director   │
        │  scenes/ (Phaser view)     │  level   │  static content + audio     │
        └────────────────────────────┘  + audio └─────────────────────────────┘
```

**Key property:** the always-on server performs **no LLM/GPU inference**. It serves
pre-generated, validated content. Generation is a manual daily batch on a separate machine.

## Components

### Client (`client/`)
- `src/engine/` — **pure TypeScript**, zero Phaser imports. All game rules live here and are
  unit-tested with Vitest: hex grid & combat, overworld movement, fog of war, puzzles,
  inventory, and the Game Director rules. This is the REQ-CLI-01 "decoupled core".
- `src/scenes/` — Phaser scenes. A thin view/input layer wired to the engine **after** the
  engine is green. No game logic here.

### Server (`server/`)
- `profile/` — load/update `player_profile` (defeat streak, difficulty modifier, the
  `reinforce_concepts` array driving the feedback loop).
- `director/` — authoritative implementation of the adaptive rules (mirrors the client's
  advisory copy; parity guaranteed by shared golden-vector fixtures).
- `api/` — read endpoints (`GET /content/today/{profile}`) + static mounts for level JSON and
  audio. Graceful fallback when today's batch has not run yet.

### Content pipeline (`content/`)
Runs on the GPU box, on demand. Pure, testable parts (`prompt_builder`, `schema_validator`,
`safety`, `publisher`) are unit-tested with mocks; only the optional smoke test touches live
Ollama/ComfyUI/Piper.

### Shared contract (`shared/`)
`shared/schemas/*.json` (JSON Schema, draft 2020-12) is the **single source of truth**:
- → `shared/ts/*.ts` via `json-schema-to-typescript` (client types)
- → `shared/py/models.py` via `datamodel-code-generator` (server/content Pydantic)
- → passed verbatim to Ollama as `format=` for structured outputs.

CI regenerates and diffs to detect drift. Cross-field invariants that JSON Schema cannot
express (matrix dimensions, reference resolution, axial-in-radius, ≥1 player unit) are enforced
by `schema_validator.py` and re-checked client-side in `LevelLoader`.

### Curricula (`curricula/`)
Pedagogy as data: `profiles/*.yaml` bind a profile to subjects; `concepts/*.yaml` list concepts
with difficulty bands and language. Adding a profile = adding YAML, no code change.

## Data model (summary)

- **player_profile** — `profile_id`, `display_name` (live-only, gitignored), `age`,
  `curriculum_ref`, `difficulty_modifier`, `defeat_streak`, `last_level_started_at`,
  `reinforce_concepts[]`, `history[]`.
- **daily_level** — `overworld` (width/height/tile_legend/matrix/start), `entities[]`
  (chest|npc|monster + pos + refs + lore), `puzzles[]` (concept_tags, subject, prompt, kind,
  options, answer, accepted_answers, hint), `dialogues[]` (speaker, lines[text/language/voice]),
  `encounters[]` (hex_radius, units[team/axial/initiative/stats/lore]).
- **curriculum** — `profile_id` → subjects → concepts (difficulty band + language).

## Adaptive mechanics (Game Director)

| Rule | Trigger | Effect |
|---|---|---|
| Feedback loop (REQ-GAM-01) | puzzle failed | concept added to `reinforce_concepts`; next prompt prioritizes it |
| Anti-frustration (REQ-GAM-02) | 2 consecutive defeats OR level time over limit | spawn NPC/chest with a "Magic Artifact" (massive advantage / full heal) |
| Dynamic difficulty (REQ-GAM-03) | cleared with > 80% HP/resources | global difficulty modifier ×1.10 next level |

The **server is authoritative** for profile mutation; the client may recompute advisory
previews. A shared golden-vector fixture keeps the two implementations in parity.

## Deployment

- **Server:** Proxmox LXC **CT 110** on host `zeratul` (24/7). Docker-compose: FastAPI + static
  content. CPU-only — **no GPU passthrough** (the host GPU is reserved for another service).
  Piper TTS runs on CPU. The content-store is mounted from the NAS.
- **Generation:** manual daily batch on the GPU box (`blackwell`), via the `content/` CLI.

## Decisions

| Date | Decision | Rationale |
|---|---|---|
| 2026-06-22 | Split generation (GPU, on demand) from serving (24/7, no inference) | GPU box is not always on; live game must stay responsive and simple |
| 2026-06-22 | JSON Schema as single source of truth + codegen | One contract enforced by client, server, and the LLM's structured output |
| 2026-06-22 | Pure-TS engine decoupled from Phaser, tested first | REQ-CLI-01; testability and determinism |
| 2026-06-22 | Profiles/curricula are data | Extensible to new learners without code changes |
| 2026-06-22 | Primary model `qwen3-coder:30b` | Better adherence to a complex JSON schema; speed is acceptable for a daily batch |
