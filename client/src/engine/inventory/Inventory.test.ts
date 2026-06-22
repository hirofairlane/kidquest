import { describe, expect, it } from "vitest";

import { Inventory, applyArtifact } from "./Inventory";
import { Unit, spawnUnit } from "../combat/Unit";

function hero(hp: number): Unit {
  const u = spawnUnit({
    id: "hero",
    team: "player",
    name: "Hero",
    axial: { q: 0, r: 0 },
    initiative: 5,
    stats: { hp: 20, atk: 5, def: 2, speed: 3, range: 1 },
  });
  u.hp = hp;
  return u;
}

describe("Inventory", () => {
  it("adds, finds and removes items", () => {
    const inv = new Inventory();
    inv.add({ id: "art1", kind: "magic_artifact", name: "Sunstone" });
    expect(inv.has("art1")).toBe(true);
    expect(inv.size).toBe(1);
    expect(inv.remove("art1")).toBe(true);
    expect(inv.has("art1")).toBe(false);
  });
});

describe("applyArtifact", () => {
  it("full-heals the unit without mutating the original", () => {
    const wounded = hero(5);
    const { unit } = applyArtifact(wounded, { fullHeal: true });
    expect(unit.hp).toBe(20);
    expect(wounded.hp).toBe(5); // original untouched
  });

  it("flags a combat advantage", () => {
    const { advantage } = applyArtifact(hero(20), { advantage: true });
    expect(advantage).toBe(true);
  });

  it("leaves hp unchanged when the effect does not heal", () => {
    const { unit } = applyArtifact(hero(7), { advantage: true });
    expect(unit.hp).toBe(7);
  });
});
