import { describe, expect, it } from "vitest";

import { LevelLoadError, RawDailyLevel, loadLevel } from "./LevelLoader";

function rawLevel(): RawDailyLevel {
  return {
    schema_version: "1",
    profile_id: "youth_10yo",
    language_default: "es",
    overworld: {
      width: 2,
      height: 1,
      tile_legend: {
        "0": { name: "Meadow", walkable: true, kind: "grass" },
        "1": { name: "Wall", walkable: false, kind: "wall" },
      },
      matrix: [[0, 1]],
      start: { x: 0, y: 0 },
    },
    entities: [{ id: "chest", type: "chest", pos: { x: 1, y: 0 }, puzzle_ref: "p1" }],
    puzzles: [{ id: "p1", concept_tags: ["fractions_halves"], answer: "4", accepted_answers: ["four"] }],
    dialogues: [{ id: "d1", speaker: "Xana", lines: [{ text: "Hi", language: "en", voice: "en_GB" }] }],
    encounters: [
      {
        id: "e1",
        hex_radius: 2,
        units: [
          { id: "hero", team: "player", name: "Hero", axial: { q: -1, r: 0 }, initiative: 10, stats: { hp: 20, atk: 6, def: 3, speed: 4, range: 1 } },
          { id: "foe", team: "enemy", name: "Foe", axial: { q: 1, r: 0 }, initiative: 8, stats: { hp: 30, atk: 5, def: 4, speed: 2, range: 2 } },
        ],
      },
    ],
  };
}

describe("loadLevel", () => {
  it("loads a valid level into engine structures", () => {
    const level = loadLevel(rawLevel());
    expect(level.profileId).toBe("youth_10yo");
    expect(level.grid.width).toBe(2);
    expect(level.puzzles.get("p1")?.conceptTags).toEqual(["fractions_halves"]);
    expect(level.encounters.get("e1")).toHaveLength(2);
    expect(level.entities[0]).toMatchObject({ id: "chest", type: "chest" });
  });

  it("rejects an unsupported schema version", () => {
    const raw = rawLevel();
    raw.schema_version = "999";
    expect(() => loadLevel(raw)).toThrow(LevelLoadError);
  });

  it("rejects a start tile that is not walkable", () => {
    const raw = rawLevel();
    raw.overworld.start = { x: 1, y: 0 }; // the wall
    expect(() => loadLevel(raw)).toThrow(/not walkable/);
  });

  it("rejects a dangling entity reference", () => {
    const raw = rawLevel();
    raw.entities[0].puzzle_ref = "does_not_exist";
    expect(() => loadLevel(raw)).toThrow(/unknown puzzle/);
  });

  it("rejects an encounter with no player unit", () => {
    const raw = rawLevel();
    raw.encounters[0].units[0].team = "enemy";
    expect(() => loadLevel(raw)).toThrow(/no player unit/);
  });

  it("rejects a unit placed outside the encounter radius", () => {
    const raw = rawLevel();
    raw.encounters[0].units[1].axial = { q: 5, r: 0 };
    expect(() => loadLevel(raw)).toThrow(/outside encounter/);
  });
});
