import { describe, expect, it } from "vitest";

import { Grid, TileLegend } from "./Grid";
import { OverworldEntity, resolveStep } from "./Movement";

const LEGEND: TileLegend = {
  0: { name: "Meadow", walkable: true, kind: "grass" },
  1: { name: "Wall", walkable: false, kind: "wall" },
};

function grid(): Grid {
  return new Grid(3, 1, [[0, 0, 1]], LEGEND);
}

const ENTITIES: OverworldEntity[] = [
  { id: "chest_1", type: "chest", pos: { x: 1, y: 0 } },
  { id: "npc_1", type: "npc", pos: { x: 0, y: 0 } },
];

describe("resolveStep", () => {
  it("moves into an empty walkable tile", () => {
    const r = resolveStep(grid(), [], { x: 0, y: 0 }, { dx: 1, dy: 0 });
    expect(r.moved).toBe(true);
    expect(r.to).toEqual({ x: 1, y: 0 });
    expect(r.collision).toBe("none");
  });

  it("is blocked by a non-walkable tile and does not move", () => {
    const r = resolveStep(grid(), [], { x: 1, y: 0 }, { dx: 1, dy: 0 }); // into wall
    expect(r.moved).toBe(false);
    expect(r.collision).toBe("blocked");
    expect(r.to).toEqual({ x: 1, y: 0 });
  });

  it("is blocked at the map edge", () => {
    const r = resolveStep(grid(), [], { x: 0, y: 0 }, { dx: -1, dy: 0 });
    expect(r.moved).toBe(false);
    expect(r.collision).toBe("blocked");
  });

  it("maps a chest into a puzzle intent without moving onto it", () => {
    const r = resolveStep(grid(), ENTITIES, { x: 0, y: 0 }, { dx: 1, dy: 0 }); // chest at (1,0)
    expect(r.collision).toBe("puzzle");
    expect(r.entityId).toBe("chest_1");
    expect(r.moved).toBe(false);
  });

  it("maps an npc into a dialogue intent and a monster into combat", () => {
    const monsterGrid = new Grid(2, 1, [[0, 0]], LEGEND);
    const npc = resolveStep(monsterGrid, [{ id: "n", type: "npc", pos: { x: 1, y: 0 } }], { x: 0, y: 0 }, { dx: 1, dy: 0 });
    expect(npc.collision).toBe("dialogue");
    const mon = resolveStep(monsterGrid, [{ id: "m", type: "monster", pos: { x: 1, y: 0 } }], { x: 0, y: 0 }, { dx: 1, dy: 0 });
    expect(mon.collision).toBe("combat");
  });
});
