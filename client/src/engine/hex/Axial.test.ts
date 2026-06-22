import { describe, expect, it } from "vitest";

import {
  axialAdd,
  axialDistance,
  axialEquals,
  axialLine,
  axialNeighbors,
  axialRange,
} from "./Axial";

describe("axial coordinate math", () => {
  it("distance is 0 to itself", () => {
    expect(axialDistance({ q: 0, r: 0 }, { q: 0, r: 0 })).toBe(0);
  });

  it("distance between two cells", () => {
    expect(axialDistance({ q: 0, r: 0 }, { q: 2, r: -1 })).toBe(2);
    expect(axialDistance({ q: -1, r: 0 }, { q: 1, r: 0 })).toBe(2);
  });

  it("distance is symmetric", () => {
    const a = { q: 1, r: 2 };
    const b = { q: -2, r: 3 };
    expect(axialDistance(a, b)).toBe(axialDistance(b, a));
  });

  it("has exactly 6 neighbors, all at distance 1", () => {
    const c = { q: 3, r: -1 };
    const ns = axialNeighbors(c);
    expect(ns).toHaveLength(6);
    for (const n of ns) {
      expect(axialDistance(c, n)).toBe(1);
    }
    // neighbors are unique
    const keys = new Set(ns.map((n) => `${n.q},${n.r}`));
    expect(keys.size).toBe(6);
  });

  it("range(c, 1) yields the center plus its 6 neighbors (7 cells)", () => {
    const cells = axialRange({ q: 0, r: 0 }, 1);
    expect(cells).toHaveLength(7);
  });

  it("range(c, 2) yields 19 cells (1 + 6 + 12)", () => {
    expect(axialRange({ q: 0, r: 0 }, 2)).toHaveLength(19);
  });

  it("range never includes cells beyond the radius", () => {
    const center = { q: 0, r: 0 };
    for (const cell of axialRange(center, 2)) {
      expect(axialDistance(center, cell)).toBeLessThanOrEqual(2);
    }
  });

  it("adds coordinates", () => {
    expect(axialAdd({ q: 1, r: 2 }, { q: -3, r: 4 })).toEqual({ q: -2, r: 6 });
  });

  it("compares coordinates by value", () => {
    expect(axialEquals({ q: 1, r: 1 }, { q: 1, r: 1 })).toBe(true);
    expect(axialEquals({ q: 1, r: 1 }, { q: 1, r: 2 })).toBe(false);
  });

  it("draws a straight line between two cells (inclusive endpoints)", () => {
    const line = axialLine({ q: 0, r: 0 }, { q: 3, r: 0 });
    expect(line[0]).toEqual({ q: 0, r: 0 });
    expect(line[line.length - 1]).toEqual({ q: 3, r: 0 });
    expect(line).toHaveLength(4);
    // consecutive cells on the line are adjacent
    for (let i = 1; i < line.length; i++) {
      expect(axialDistance(line[i - 1], line[i])).toBe(1);
    }
  });
});
