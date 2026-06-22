import { describe, expect, it } from "vitest";

import { computeFov, fovKey } from "./Fov";
import { Grid, TileLegend } from "./Grid";

const LEGEND: TileLegend = {
  0: { name: "Meadow", walkable: true, kind: "grass" },
  1: { name: "Wall", walkable: false, kind: "wall" },
};

function openField(size: number): Grid {
  const row = new Array(size).fill(0);
  const matrix = new Array(size).fill(null).map(() => [...row]);
  return new Grid(size, size, matrix, LEGEND);
}

describe("computeFov", () => {
  it("always sees the origin", () => {
    const fov = computeFov(openField(5), { x: 2, y: 2 }, 2);
    expect(fov.has(fovKey({ x: 2, y: 2 }))).toBe(true);
  });

  it("on an open field, sees every cell within the radius", () => {
    const fov = computeFov(openField(7), { x: 3, y: 3 }, 2);
    // a filled diamond/disc of Chebyshev radius 2 within bounds: count cells within range
    expect(fov.has(fovKey({ x: 5, y: 3 }))).toBe(true);
    expect(fov.has(fovKey({ x: 3, y: 5 }))).toBe(true);
    expect(fov.has(fovKey({ x: 6, y: 3 }))).toBe(false); // beyond radius 2
  });

  it("a wall blocks the cell directly behind it", () => {
    // origin at (0,0); wall at (1,0); target (2,0) must be hidden
    const g = new Grid(3, 1, [[0, 1, 0]], LEGEND);
    const fov = computeFov(g, { x: 0, y: 0 }, 5);
    expect(fov.has(fovKey({ x: 1, y: 0 }))).toBe(true); // the wall itself is seen
    expect(fov.has(fovKey({ x: 2, y: 0 }))).toBe(false); // behind the wall is hidden
  });
});
