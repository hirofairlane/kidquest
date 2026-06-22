/**
 * Turn a validated `daily_level` document into engine-ready structures, and
 * enforce the cross-field invariants that JSON Schema cannot express:
 *   - the engine understands the schema version,
 *   - the player start is in-bounds and walkable,
 *   - every entity reference resolves to a puzzle/dialogue/encounter,
 *   - each encounter's units sit within its hex radius and include >=1 player.
 *
 * Pure: no I/O. The server validates the JSON against the schema first; this is
 * the client-side second line of defence before anything reaches the renderer.
 */
import { axialDistance } from "../hex/Axial";
import { UnitSpec } from "../combat/Unit";
import { isSupportedSchemaVersion } from "../contract";
import { Grid, GridPos, TileLegend } from "../overworld/Grid";
import { OverworldEntity } from "../overworld/Movement";
import { PuzzleDef } from "../puzzle/PuzzleStateMachine";

export class LevelLoadError extends Error {}

export interface DialogueLine {
  text: string;
  language: "es" | "en";
  voice: string;
}

export interface Dialogue {
  id: string;
  speaker: string;
  lines: DialogueLine[];
}

export interface LoadedLevel {
  profileId: string;
  languageDefault: "es" | "en";
  grid: Grid;
  start: GridPos;
  entities: OverworldEntity[];
  puzzles: Map<string, PuzzleDef>;
  dialogues: Map<string, Dialogue>;
  encounters: Map<string, UnitSpec[]>;
}

// Structural view of the validated schema document (snake_case as authored/served).
export interface RawDailyLevel {
  schema_version: string;
  profile_id: string;
  language_default: "es" | "en";
  overworld: {
    width: number;
    height: number;
    tile_legend: Record<string, { name: string; walkable: boolean; kind: string }>;
    matrix: number[][];
    start: GridPos;
  };
  entities: Array<{
    id: string;
    type: "chest" | "npc" | "monster";
    pos: GridPos;
    puzzle_ref?: string | null;
    dialogue_ref?: string | null;
    encounter_ref?: string | null;
  }>;
  puzzles: Array<{
    id: string;
    concept_tags: string[];
    answer: string;
    accepted_answers?: string[] | null;
  }>;
  dialogues: Array<Dialogue>;
  encounters: Array<{
    id: string;
    hex_radius: number;
    units: UnitSpec[];
  }>;
}

export function loadLevel(raw: RawDailyLevel): LoadedLevel {
  if (!isSupportedSchemaVersion(raw.schema_version)) {
    throw new LevelLoadError(`unsupported schema version: ${raw.schema_version}`);
  }

  const legend: TileLegend = {};
  for (const [id, def] of Object.entries(raw.overworld.tile_legend)) {
    legend[Number(id)] = def;
  }
  const grid = new Grid(raw.overworld.width, raw.overworld.height, raw.overworld.matrix, legend);

  if (!grid.isWalkable(raw.overworld.start)) {
    throw new LevelLoadError("start position is not walkable");
  }

  const puzzles = new Map<string, PuzzleDef>(
    raw.puzzles.map((p) => [
      p.id,
      {
        id: p.id,
        conceptTags: p.concept_tags,
        canonicalAnswer: p.answer,
        acceptedAnswers: p.accepted_answers ?? undefined,
      },
    ]),
  );
  const dialogues = new Map<string, Dialogue>(raw.dialogues.map((d) => [d.id, d]));
  const encounters = new Map<string, UnitSpec[]>(raw.encounters.map((e) => [e.id, e.units]));

  for (const e of raw.entities) {
    if (e.puzzle_ref && !puzzles.has(e.puzzle_ref)) {
      throw new LevelLoadError(`entity ${e.id} references unknown puzzle ${e.puzzle_ref}`);
    }
    if (e.dialogue_ref && !dialogues.has(e.dialogue_ref)) {
      throw new LevelLoadError(`entity ${e.id} references unknown dialogue ${e.dialogue_ref}`);
    }
    if (e.encounter_ref && !encounters.has(e.encounter_ref)) {
      throw new LevelLoadError(`entity ${e.id} references unknown encounter ${e.encounter_ref}`);
    }
  }

  for (const e of raw.encounters) {
    if (!e.units.some((u) => u.team === "player")) {
      throw new LevelLoadError(`encounter ${e.id} has no player unit`);
    }
    for (const u of e.units) {
      if (axialDistance({ q: 0, r: 0 }, u.axial) > e.hex_radius) {
        throw new LevelLoadError(`unit ${u.id} is outside encounter ${e.id} radius`);
      }
    }
  }

  const entities: OverworldEntity[] = raw.entities.map((e) => ({ id: e.id, type: e.type, pos: e.pos }));

  return {
    profileId: raw.profile_id,
    languageDefault: raw.language_default,
    grid,
    start: raw.overworld.start,
    entities,
    puzzles,
    dialogues,
    encounters,
  };
}
