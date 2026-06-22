# KidQuest — Roadmap

Milestones are TDD-first (red → green → refactor) and each keeps CI green. Most are verifiable
without the GPU box awake; only the generation/sprite **smoke** tests need it.

## M0 — Scaffold, CI, contract, harness  ✅
- [x] Monorepo tree (pnpm + uv), docs, `.gitignore`, `LICENSE`, `ruff.toml`
- [x] `shared/schemas/*.json` (player_profile, daily_level, curriculum) + generic fixtures
- [x] Codegen wired: TS types + Pydantic models, with CI drift check
- [x] CI (validate / tests-py / tests-ts / build / safety) adapted from `genia-air-ha`
- [x] `tests/validate_repo.py` incl. PII guard (no real profile committed)
- [x] Red→green placeholder tests on both sides; CI green
- [x] Public repo `hirofairlane/kidquest` created and pushed — **CI green**

## M1 — Hex combat engine (pure TS)  ✅
- [x] `Axial`, `HexGrid` (distance, neighbors, range, line)
- [x] `TurnQueue` (initiative ordering, ties, cycling)
- [x] `DamageResolver`, `CombatEncounter` (deterministic resolution)

## M2 — Overworld engine (pure TS)  ✅
- [x] `Grid`, `Movement` (walkability, collision → intent)
- [x] `FogOfWar`, `Fov` (LOS visibility)

## M3 — Puzzles / dialogue / inventory + LevelLoader (pure TS)  ✅
- [x] `PuzzleStateMachine`, `AnswerChecker` (accent/case/number-tolerant)
- [x] `Inventory` (items, Magic Artifact effects)
- [x] `LevelLoader` (validated `daily_level` → engine state)

## M4 — Game Director rules (shared, pure)  ✅
- [x] `FeedbackLoop`, `AntiFrustration`, `DynamicDifficulty` in TS
- [x] `server/director/rules.py` + shared golden-vector parity fixture

## M5 — Backend profile store + API + static content  ✅
- [x] `profile/store.py` (streak, difficulty, reinforce[])
- [x] `api/routes.py` (`GET /content/today/{profile}`, static audio, stale fallback)

## M6 — Content generation pipeline (CLI on GPU box)
- [ ] `prompt_builder` (pure, tested from fixtures)
- [ ] `llm_client` (mocked in units), `schema_validator`, `tts_piper` (mocked)
- [ ] `safety` (LoRA allowlist; banned NSFW LoRA), `publisher`, `orchestrator` CLI
- [ ] `@pytest.mark.smoke` real-Ollama generation test (excluded from cloud CI)

## M7 — Optional sprite/tile generation (ComfyUI)
- [ ] `comfy_driver` (POST /prompt → poll /history → /view) + AssetSpec, allowlist-enforced

## M8 — Phaser wiring (view only)
- [ ] Boot/Overworld/Combat/Dialogue/Puzzle scenes bound to the green engine

## M9 — Deploy to CT 110 on zeratul
- [ ] docker-compose (FastAPI + static, CPU-only), NAS content-store mount, provisioning notes

---

**Legend:** ⏳ in progress. Update checkboxes as work lands. Smoke tests requiring the GPU box
(`blackwell`) are kept out of the cloud CI gate and run manually on the LAN.
