/**
 * Pure combat damage resolution. No randomness (deterministic and testable);
 * variance/abilities can layer on later without changing this contract.
 */
import { axialDistance } from "../hex/Axial";
import { Unit } from "./Unit";

export interface AttackResult {
  damage: number;
  defenderHpAfter: number;
  lethal: boolean;
}

/** True when the defender is within the attacker's range. */
export function canAttack(attacker: Unit, defender: Unit): boolean {
  return axialDistance(attacker.axial, defender.axial) <= attacker.stats.range;
}

/**
 * Resolve a single attack. Damage is `max(0, atk - def)`; the defender's hit
 * points never drop below zero. Does not mutate either unit.
 */
export function resolveAttack(attacker: Unit, defender: Unit): AttackResult {
  const damage = Math.max(0, attacker.stats.atk - defender.stats.def);
  const defenderHpAfter = Math.max(0, defender.hp - damage);
  return { damage, defenderHpAfter, lethal: defenderHpAfter === 0 };
}
