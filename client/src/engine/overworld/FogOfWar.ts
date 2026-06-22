/**
 * Fog of war state for the overworld: each cell is unseen (never observed),
 * seen (observed before, now remembered/dimmed), or visible (in view right now).
 * Pure; the renderer reads `get` to tint tiles.
 */
import { GridPos } from "./Grid";

export type Visibility = "unseen" | "seen" | "visible";

export class FogOfWar {
  readonly width: number;
  readonly height: number;
  private readonly state: Visibility[][];

  constructor(width: number, height: number) {
    this.width = width;
    this.height = height;
    this.state = Array.from({ length: height }, () =>
      Array.from({ length: width }, () => "unseen" as Visibility),
    );
  }

  get(pos: GridPos): Visibility {
    return this.state[pos.y][pos.x];
  }

  /**
   * Update the field of view: every currently-visible cell drops to "seen", then
   * the supplied cells become "visible".
   */
  update(visibleCells: Iterable<GridPos>): void {
    for (let y = 0; y < this.height; y++) {
      for (let x = 0; x < this.width; x++) {
        if (this.state[y][x] === "visible") this.state[y][x] = "seen";
      }
    }
    for (const c of visibleCells) {
      if (c.y >= 0 && c.y < this.height && c.x >= 0 && c.x < this.width) {
        this.state[c.y][c.x] = "visible";
      }
    }
  }
}
