/**
 * Combat unit model. Mirrors the `encounters[].units[]` shape in
 * `daily_level.schema.json`, plus a runtime `hp` (current hit points).
 */
import { Axial } from "../hex/Axial";

export type Team = "player" | "enemy";

export interface UnitStats {
  hp: number;
  atk: number;
  def: number;
  speed: number;
  range: number;
}

export interface Unit {
  id: string;
  team: Team;
  name: string;
  axial: Axial;
  initiative: number;
  stats: UnitStats;
  /** Current hit points; starts equal to `stats.hp`. */
  hp: number;
}

export interface UnitSpec {
  id: string;
  team: Team;
  name: string;
  axial: Axial;
  initiative: number;
  stats: UnitStats;
}

/** Create a runtime unit from a spec, starting at full health. */
export function spawnUnit(spec: UnitSpec): Unit {
  return { ...spec, axial: { ...spec.axial }, stats: { ...spec.stats }, hp: spec.stats.hp };
}

export function isAlive(unit: Unit): boolean {
  return unit.hp > 0;
}
