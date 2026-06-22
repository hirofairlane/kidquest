import { describe, expect, it } from "vitest";

import { HexGrid } from "./HexGrid";

describe("HexGrid (hexagonal board of a given radius)", () => {
  it("contains the center and rejects cells outside the radius", () => {
    const grid = new HexGrid(2);
    expect(grid.contains({ q: 0, r: 0 })).toBe(true);
    expect(grid.contains({ q: 2, r: 0 })).toBe(true);
    expect(grid.contains({ q: 3, r: 0 })).toBe(false);
  });

  it("radius-1 board has 7 cells, radius-2 has 19", () => {
    expect(new HexGrid(1).cells()).toHaveLength(7);
    expect(new HexGrid(2).cells()).toHaveLength(19);
  });

  it("clips neighbors to the board edge", () => {
    const grid = new HexGrid(1);
    // a corner of the radius-1 board has fewer in-board neighbors
    const corner = { q: 1, r: 0 };
    const ns = grid.neighbors(corner);
    expect(ns.length).toBeLessThan(6);
    for (const n of ns) {
      expect(grid.contains(n)).toBe(true);
    }
  });

  it("reports distance between two in-board cells", () => {
    const grid = new HexGrid(3);
    expect(grid.distance({ q: 0, r: 0 }, { q: 2, r: -1 })).toBe(2);
  });
});
