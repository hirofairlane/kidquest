# KidQuest

An adaptive, **educational turn-based RPG** in the style of *Heroes of Might & Magic*:
overworld exploration on a grid with fog of war, plus tactical **hexagonal** combat.

The twist: the game's daily content — maps, puzzles, dialogues, enemies — is **generated
by a local LLM** and adapted to each player's learning profile. It is built to run fully
on a home lab (no cloud dependency) and to teach real curriculum while playing.

> Status: **early development (M0 — scaffolding & contract)**. See [ROADMAP.md](ROADMAP.md).

## Why

A privacy-respecting game for a family that turns daily practice (maths, reading, English,
science, history, geography, even electronics) into an RPG adventure. Content is fresh every
day and follows each player where they struggle.

## Players (data-driven profiles)

Profiles and their curricula are **data**, not code — adding a profile is adding a YAML file.

| Profile | Focus |
|---|---|
| `child_6yo` | Basic maths, Spanish reading, **Natural Science in English**; mythic monsters (Gamusinos, Anjanas/Xanas, Basilisco Pipón) |
| `youth_10yo` | Medieval history, Iberian geography, fractions & Roman numerals, **advanced English reading**; El Cuélebre, La Santa Compaña, recruitable troops |
| `adult_artificer` | Technical English + **electronics** (Ohm's law, components, logic gates) framed as an Artificer's arcane devices |

The game **narrative is bilingual (Spanish/English)** by design; the codebase and docs are
in English.

## Architecture (short)

```
[Phaser3 + TS client] ──HTTP──▶ [FastAPI server (24/7 Proxmox LXC)] ──reads──▶ content-store
                                                                                      ▲
        Daily batch (manual, on a GPU box): profile → prompt → local LLM (strict JSON)
        → validate → Piper TTS → optional sprites → publish
```

The live server does **no inference** — it only serves pre-generated content. Generation runs
on demand on a separate GPU machine. Full design in [ARCHITECTURE.md](ARCHITECTURE.md).

## Tech stack

| Layer | Tech |
|---|---|
| Client | Phaser 3, TypeScript, Vite, **Vitest** (pure-logic engine, fully decoupled from Phaser) |
| Server | Python, FastAPI, **pytest** |
| Content pipeline | Ollama (structured outputs), Piper TTS, ComfyUI (optional sprites) |
| Contract | JSON Schema → codegen to TS types + Pydantic models (single source of truth) |
| CI/QA | GitHub Actions, ruff, TDD |

## Development

This is a pnpm + uv monorepo.

```bash
# JS/TS side
pnpm install
pnpm codegen            # regenerate shared TS types from JSON Schema
pnpm -C client test     # Vitest engine tests

# Python side
uv sync                 # create env + install dev deps
uv run pytest           # server + content tests
uv run ruff check .
```

TDD is mandatory: write the failing test first, implement the minimum to pass, refactor green.
Every bug gets a regression test before the fix.

## License

MIT for the code. Bundled assets keep their own licenses — see [CREDITS.md](CREDITS.md) and
[LICENSE](LICENSE).
