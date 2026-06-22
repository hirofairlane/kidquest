/**
 * A hexagonal combat board of a given radius, in axial coordinates.
 *
 * Pure geometry/topology only: which cells exist and how they connect. Occupancy,
 * units and turns live in the combat module. No Phaser, no rendering.
 */
import { Axial, axialDistance, axialNeighbors, axialRange } from "./Axial";

export class HexGrid {
  readonly radius: number;

  constructor(radius: number) {
    if (!Number.isInteger(radius) || radius < 1) {
      throw new Error(`HexGrid radius must be a positive integer, got ${radius}`);
    }
    this.radius = radius;
  }

  /** True when the cell lies on the board (within radius of the center). */
  contains(cell: Axial): boolean {
    return axialDistance({ q: 0, r: 0 }, cell) <= this.radius;
  }

  /** Every cell of the board. */
  cells(): Axial[] {
    return axialRange({ q: 0, r: 0 }, this.radius);
  }

  /** Adjacent cells that are still on the board (edge-clipped). */
  neighbors(cell: Axial): Axial[] {
    return axialNeighbors(cell).filter((n) => this.contains(n));
  }

  /** Hex distance between two cells (does not require them to be in-board). */
  distance(a: Axial, b: Axial): number {
    return axialDistance(a, b);
  }
}
