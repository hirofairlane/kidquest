/**
 * Overworld movement resolution: turn a movement intent into a result that is
 * either a move, a wall bump, or an interaction with an entity (chest → puzzle,
 * npc → dialogue, monster → combat). Pure; no rendering or input.
 */
import { Grid, GridPos } from "./Grid";

export type EntityType = "chest" | "npc" | "monster";

export interface OverworldEntity {
  id: string;
  type: EntityType;
  pos: GridPos;
}

export type CollisionKind = "none" | "blocked" | "puzzle" | "dialogue" | "combat";

export interface Delta {
  dx: number;
  dy: number;
}

export interface StepResult {
  from: GridPos;
  to: GridPos;
  moved: boolean;
  collision: CollisionKind;
  entityId?: string;
}

const ENTITY_INTENT: Record<EntityType, CollisionKind> = {
  chest: "puzzle",
  npc: "dialogue",
  monster: "combat",
};

/**
 * Resolve a single step from `from` by `delta`. The player interacts with an
 * entity by stepping into it (without occupying its tile); an impassable tile or
 * the map edge blocks the move.
 */
export function resolveStep(
  grid: Grid,
  entities: readonly OverworldEntity[],
  from: GridPos,
  delta: Delta,
): StepResult {
  const target: GridPos = { x: from.x + delta.dx, y: from.y + delta.dy };

  const entity = entities.find((e) => e.pos.x === target.x && e.pos.y === target.y);
  if (entity) {
    return { from, to: from, moved: false, collision: ENTITY_INTENT[entity.type], entityId: entity.id };
  }

  if (!grid.isWalkable(target)) {
    return { from, to: from, moved: false, collision: "blocked" };
  }

  return { from, to: target, moved: true, collision: "none" };
}
