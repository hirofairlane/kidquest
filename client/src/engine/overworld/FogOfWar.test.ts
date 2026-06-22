import { describe, expect, it } from "vitest";

import { FogOfWar } from "./FogOfWar";

describe("FogOfWar", () => {
  it("starts fully unseen", () => {
    const fog = new FogOfWar(3, 3);
    expect(fog.get({ x: 0, y: 0 })).toBe("unseen");
    expect(fog.get({ x: 2, y: 2 })).toBe("unseen");
  });

  it("marks revealed cells visible", () => {
    const fog = new FogOfWar(3, 3);
    fog.update([{ x: 1, y: 1 }, { x: 1, y: 2 }]);
    expect(fog.get({ x: 1, y: 1 })).toBe("visible");
    expect(fog.get({ x: 0, y: 0 })).toBe("unseen");
  });

  it("demotes previously-visible cells to seen when they leave the view", () => {
    const fog = new FogOfWar(3, 3);
    fog.update([{ x: 1, y: 1 }]);
    fog.update([{ x: 2, y: 2 }]);
    expect(fog.get({ x: 1, y: 1 })).toBe("seen");
    expect(fog.get({ x: 2, y: 2 })).toBe("visible");
  });

  it("a seen cell becomes visible again when re-entered", () => {
    const fog = new FogOfWar(2, 1);
    fog.update([{ x: 0, y: 0 }]);
    fog.update([{ x: 1, y: 0 }]);
    fog.update([{ x: 0, y: 0 }]);
    expect(fog.get({ x: 0, y: 0 })).toBe("visible");
    expect(fog.get({ x: 1, y: 0 })).toBe("seen");
  });
});
