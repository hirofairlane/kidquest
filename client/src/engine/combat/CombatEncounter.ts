/**
 * Tactical combat encounter: holds the units, drives the initiative turn order,
 * resolves attacks, removes the dead, and reports a winner.
 *
 * Pure state machine — no rendering, no randomness, no input handling. The Phaser
 * combat scene (milestone M8) is a thin view over this.
 */
import { Team, Unit, isAlive } from "./Unit";
import { AttackResult, canAttack, resolveAttack } from "./DamageResolver";
import { TurnQueue } from "./TurnQueue";

export class OutOfRangeError extends Error {}
export class InvalidActionError extends Error {}

export class CombatEncounter {
  private units = new Map<string, Unit>();
  private queue: TurnQueue;

  constructor(units: Unit[]) {
    if (units.length < 2) {
      throw new InvalidActionError("an encounter needs at least two units");
    }
    for (const u of units) {
      this.units.set(u.id, { ...u, axial: { ...u.axial }, stats: { ...u.stats } });
    }
    this.queue = new TurnQueue([...this.units.values()]);
  }

  getUnit(id: string): Unit | undefined {
    return this.units.get(id);
  }

  aliveUnits(): Unit[] {
    return [...this.units.values()].filter(isAlive);
  }

  /** Id of the unit whose turn it is. */
  currentUnitId(): string | undefined {
    return this.queue.current();
  }

  currentUnit(): Unit | undefined {
    const id = this.queue.current();
    return id ? this.units.get(id) : undefined;
  }

  /**
   * The current unit attacks `targetId`. Validates that it is the attacker's turn,
   * that the target is alive and on the opposing team, and that it is in range.
   * Applies damage, removes the target if it dies, and advances the turn.
   */
  attack(targetId: string): AttackResult {
    const attacker = this.currentUnit();
    if (!attacker) throw new InvalidActionError("no unit is active");
    const defender = this.units.get(targetId);
    if (!defender || !isAlive(defender)) {
      throw new InvalidActionError(`invalid target: ${targetId}`);
    }
    if (defender.team === attacker.team) {
      throw new InvalidActionError("cannot attack a friendly unit");
    }
    if (!canAttack(attacker, defender)) {
      throw new OutOfRangeError(`${targetId} is out of range`);
    }

    const result = resolveAttack(attacker, defender);
    defender.hp = result.defenderHpAfter;
    if (result.lethal) {
      this.units.delete(defender.id);
      this.queue.remove(defender.id);
    }
    this.queue.advance();
    return result;
  }

  /** Skip the current unit's turn. */
  pass(): void {
    this.queue.advance();
  }

  /** The winning team once one side is eliminated, otherwise null. */
  winner(): Team | null {
    const alive = this.aliveUnits();
    const players = alive.some((u) => u.team === "player");
    const enemies = alive.some((u) => u.team === "enemy");
    if (players && !enemies) return "player";
    if (enemies && !players) return "enemy";
    return null;
  }
}
