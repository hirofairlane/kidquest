/**
 * Player inventory and the "Magic Artifact" effect (REQ-GAM-02 anti-frustration
 * reward). Pure; combat/exploration consume the effect via `applyArtifact`.
 */
import { Unit } from "../combat/Unit";

export interface ArtifactEffect {
  /** Restore the holder to full hit points. */
  fullHeal?: boolean;
  /** Grant a massive combat advantage for the next encounter. */
  advantage?: boolean;
}

export type ItemKind = "magic_artifact" | "key" | "trinket";

export interface Item {
  id: string;
  kind: ItemKind;
  name: string;
  effect?: ArtifactEffect;
}

export class Inventory {
  private items = new Map<string, Item>();

  add(item: Item): void {
    this.items.set(item.id, item);
  }

  remove(id: string): boolean {
    return this.items.delete(id);
  }

  has(id: string): boolean {
    return this.items.has(id);
  }

  get size(): number {
    return this.items.size;
  }

  list(): Item[] {
    return [...this.items.values()];
  }
}

export interface ArtifactApplication {
  unit: Unit;
  advantage: boolean;
}

/**
 * Apply an artifact effect to a unit, returning a new unit (no mutation) and
 * whether a combat advantage was granted.
 */
export function applyArtifact(unit: Unit, effect: ArtifactEffect): ArtifactApplication {
  const healed = effect.fullHeal ? unit.stats.hp : unit.hp;
  return {
    unit: { ...unit, axial: { ...unit.axial }, stats: { ...unit.stats }, hp: healed },
    advantage: effect.advantage === true,
  };
}
