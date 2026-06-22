/**
 * Rectangular tile grid for overworld exploration.
 *
 * Built from the validated `overworld` block of a daily level (width, height,
 * tile legend, and a height×width matrix of legend ids). Pure data + queries;
 * no rendering. Walkability and opacity are derived from the legend.
 */
export interface GridPos {
  x: number;
  y: number;
}

export interface TileDef {
  name: string;
  walkable: boolean;
  kind: string;
}

export type TileLegend = Record<number, TileDef>;

/** Tile kinds that block both movement and line of sight. */
const OPAQUE_KINDS = new Set(["wall", "mountain"]);

export class Grid {
  readonly width: number;
  readonly height: number;
  private readonly matrix: number[][];
  private readonly legend: TileLegend;

  constructor(width: number, height: number, matrix: number[][], legend: TileLegend) {
    if (matrix.length !== height) {
      throw new Error(`matrix has ${matrix.length} rows, expected height ${height}`);
    }
    for (const [y, row] of matrix.entries()) {
      if (row.length !== width) {
        throw new Error(`matrix row ${y} has ${row.length} cols, expected width ${width}`);
      }
      for (const id of row) {
        if (!(id in legend)) {
          throw new Error(`tile id ${id} is not defined in the legend`);
        }
      }
    }
    this.width = width;
    this.height = height;
    this.matrix = matrix;
    this.legend = legend;
  }

  inBounds(pos: GridPos): boolean {
    return pos.x >= 0 && pos.x < this.width && pos.y >= 0 && pos.y < this.height;
  }

  tileIdAt(pos: GridPos): number {
    return this.matrix[pos.y][pos.x];
  }

  tileAt(pos: GridPos): TileDef {
    if (!this.inBounds(pos)) {
      throw new Error(`tileAt out of bounds: ${pos.x},${pos.y}`);
    }
    return this.legend[this.tileIdAt(pos)];
  }

  isWalkable(pos: GridPos): boolean {
    return this.inBounds(pos) && this.legend[this.tileIdAt(pos)].walkable;
  }

  /** Out-of-bounds counts as opaque so sight stops at the map edge. */
  isOpaque(pos: GridPos): boolean {
    if (!this.inBounds(pos)) return true;
    return OPAQUE_KINDS.has(this.legend[this.tileIdAt(pos)].kind);
  }
}
