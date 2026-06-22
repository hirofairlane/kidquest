import { describe, expect, it } from "vitest";

import { Grid, TileLegend } from "./Grid";

const LEGEND: TileLegend = {
  0: { name: "Meadow", walkable: true, kind: "grass" },
  1: { name: "Mountain", walkable: false, kind: "mountain" },
  2: { name: "Road", walkable: true, kind: "road" },
  3: { name: "Wall", walkable: false, kind: "wall" },
};

function grid(): Grid {
  // 3 wide x 2 tall
  return new Grid(3, 2, [
    [0, 2, 1],
    [3, 0, 0],
  ], LEGEND);
}

describe("Grid", () => {
  it("knows its bounds", () => {
    const g = grid();
    expect(g.inBounds({ x: 0, y: 0 })).toBe(true);
    expect(g.inBounds({ x: 2, y: 1 })).toBe(true);
    expect(g.inBounds({ x: 3, y: 0 })).toBe(false);
    expect(g.inBounds({ x: 0, y: -1 })).toBe(false);
  });

  it("resolves the tile under a cell", () => {
    expect(grid().tileAt({ x: 1, y: 0 }).kind).toBe("road");
    expect(grid().tileAt({ x: 0, y: 1 }).kind).toBe("wall");
  });

  it("reports walkability from the legend", () => {
    const g = grid();
    expect(g.isWalkable({ x: 0, y: 0 })).toBe(true); // grass
    expect(g.isWalkable({ x: 2, y: 0 })).toBe(false); // mountain
    expect(g.isWalkable({ x: 0, y: 1 })).toBe(false); // wall
  });

  it("treats walls and mountains as opaque, ground as transparent", () => {
    const g = grid();
    expect(g.isOpaque({ x: 2, y: 0 })).toBe(true); // mountain
    expect(g.isOpaque({ x: 0, y: 1 })).toBe(true); // wall
    expect(g.isOpaque({ x: 1, y: 0 })).toBe(false); // road
  });

  it("out-of-bounds cells are not walkable", () => {
    expect(grid().isWalkable({ x: 9, y: 9 })).toBe(false);
  });

  it("rejects a matrix whose dimensions disagree with width/height", () => {
    expect(() => new Grid(3, 2, [[0, 0, 0]], LEGEND)).toThrow();
    expect(() => new Grid(2, 1, [[0, 0, 0]], LEGEND)).toThrow();
  });

  it("rejects a tile id missing from the legend", () => {
    expect(() => new Grid(1, 1, [[7]], LEGEND)).toThrow();
  });
});
