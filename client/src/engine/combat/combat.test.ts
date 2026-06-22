import { beforeEach, describe, expect, it } from "vitest";

import { CombatEncounter, OutOfRangeError } from "./CombatEncounter";
import { canAttack, resolveAttack } from "./DamageResolver";
import { TurnQueue } from "./TurnQueue";
import { Unit, UnitSpec, spawnUnit } from "./Unit";

function unit(over: Partial<UnitSpec> & Pick<UnitSpec, "id" | "team">): Unit {
  return spawnUnit({
    name: over.id,
    axial: { q: 0, r: 0 },
    initiative: 5,
    stats: { hp: 10, atk: 4, def: 2, speed: 3, range: 1 },
    ...over,
  });
}

describe("TurnQueue", () => {
  it("orders by initiative descending", () => {
    const q = new TurnQueue([
      unit({ id: "slow", team: "enemy", initiative: 2 }),
      unit({ id: "fast", team: "player", initiative: 9 }),
      unit({ id: "mid", team: "enemy", initiative: 5 }),
    ]);
    expect(q.ids()).toEqual(["fast", "mid", "slow"]);
  });

  it("breaks initiative ties by id (ascending), deterministically", () => {
    const q = new TurnQueue([
      unit({ id: "b", team: "player", initiative: 5 }),
      unit({ id: "a", team: "enemy", initiative: 5 }),
    ]);
    expect(q.ids()).toEqual(["a", "b"]);
  });

  it("cycles round-robin via next()", () => {
    const q = new TurnQueue([
      unit({ id: "a", team: "player", initiative: 9 }),
      unit({ id: "b", team: "enemy", initiative: 1 }),
    ]);
    expect(q.next()).toBe("a");
    expect(q.next()).toBe("b");
    expect(q.next()).toBe("a");
  });

  it("removing the upcoming unit keeps the current turn pointer valid", () => {
    const q = new TurnQueue([
      unit({ id: "a", team: "player", initiative: 9 }),
      unit({ id: "b", team: "enemy", initiative: 5 }),
      unit({ id: "c", team: "enemy", initiative: 1 }),
    ]);
    expect(q.current()).toBe("a");
    q.remove("b");
    expect(q.ids()).toEqual(["a", "c"]);
    expect(q.current()).toBe("a");
  });
});

describe("DamageResolver", () => {
  it("deals atk minus def", () => {
    const a = unit({ id: "a", team: "player", stats: { hp: 10, atk: 10, def: 0, speed: 1, range: 1 } });
    const d = unit({ id: "d", team: "enemy", stats: { hp: 20, atk: 1, def: 4, speed: 1, range: 1 } });
    const r = resolveAttack(a, d);
    expect(r.damage).toBe(6);
    expect(r.defenderHpAfter).toBe(14);
    expect(r.lethal).toBe(false);
  });

  it("never deals negative damage when defense exceeds attack", () => {
    const a = unit({ id: "a", team: "player", stats: { hp: 10, atk: 2, def: 0, speed: 1, range: 1 } });
    const d = unit({ id: "d", team: "enemy", stats: { hp: 5, atk: 1, def: 9, speed: 1, range: 1 } });
    expect(resolveAttack(a, d).damage).toBe(0);
  });

  it("reports lethal when hp reaches zero", () => {
    const a = unit({ id: "a", team: "player", stats: { hp: 10, atk: 9, def: 0, speed: 1, range: 1 } });
    const d = unit({ id: "d", team: "enemy", stats: { hp: 3, atk: 1, def: 1, speed: 1, range: 1 } });
    expect(resolveAttack(a, d)).toMatchObject({ defenderHpAfter: 0, lethal: true });
  });

  it("gates attacks by range", () => {
    const melee = unit({ id: "m", team: "player", axial: { q: 0, r: 0 }, stats: { hp: 10, atk: 4, def: 1, speed: 1, range: 1 } });
    const far = unit({ id: "f", team: "enemy", axial: { q: 2, r: 0 }, stats: { hp: 10, atk: 4, def: 1, speed: 1, range: 1 } });
    const near = unit({ id: "n", team: "enemy", axial: { q: 1, r: 0 }, stats: { hp: 10, atk: 4, def: 1, speed: 1, range: 1 } });
    expect(canAttack(melee, far)).toBe(false);
    expect(canAttack(melee, near)).toBe(true);
  });
});

describe("CombatEncounter", () => {
  let hero: Unit;
  let goblin: Unit;

  beforeEach(() => {
    hero = unit({ id: "hero", team: "player", axial: { q: 0, r: 0 }, initiative: 10, stats: { hp: 20, atk: 6, def: 3, speed: 4, range: 1 } });
    goblin = unit({ id: "goblin", team: "enemy", axial: { q: 1, r: 0 }, initiative: 8, stats: { hp: 10, atk: 5, def: 4, speed: 2, range: 1 } });
  });

  it("starts with the highest-initiative unit active", () => {
    const enc = new CombatEncounter([goblin, hero]);
    expect(enc.currentUnitId()).toBe("hero");
    expect(enc.winner()).toBeNull();
  });

  it("rejects attacking a target out of range", () => {
    const far = unit({ id: "far", team: "enemy", axial: { q: 3, r: 0 }, initiative: 1, stats: { hp: 10, atk: 1, def: 0, speed: 1, range: 1 } });
    const enc = new CombatEncounter([hero, far]);
    expect(() => enc.attack("far")).toThrow(OutOfRangeError);
  });

  it("applies damage and passes the turn to the opponent", () => {
    const enc = new CombatEncounter([hero, goblin]);
    const r = enc.attack("goblin"); // 6 atk - 4 def = 2
    expect(r.damage).toBe(2);
    expect(enc.getUnit("goblin")?.hp).toBe(8);
    expect(enc.currentUnitId()).toBe("goblin");
  });

  it("removes a slain unit and declares the winner", () => {
    const weakling = unit({ id: "weakling", team: "enemy", axial: { q: 1, r: 0 }, initiative: 1, stats: { hp: 2, atk: 1, def: 0, speed: 1, range: 1 } });
    const enc = new CombatEncounter([hero, weakling]);
    const r = enc.attack("weakling"); // 6 - 0 = 6 >= 2 hp
    expect(r.lethal).toBe(true);
    expect(enc.getUnit("weakling")).toBeUndefined();
    expect(enc.winner()).toBe("player");
    expect(enc.currentUnitId()).toBe("hero");
  });
});
