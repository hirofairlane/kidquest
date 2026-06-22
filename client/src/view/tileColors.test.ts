import { describe, expect, it } from "vitest";

import { tileColor } from "./tileColors";

describe("tileColor", () => {
  it("maps known kinds to distinct colours", () => {
    expect(tileColor("grass")).not.toBe(tileColor("water"));
    expect(tileColor("wall")).toBe(0x444444);
  });

  it("falls back for unknown kinds", () => {
    expect(tileColor("lava")).toBe(0x000000);
  });
});
