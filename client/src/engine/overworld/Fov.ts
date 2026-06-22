/**
 * Field-of-view computation for the overworld.
 *
 * For each candidate cell within `radius` (Chebyshev) of the origin, a line of
 * sight is traced; the cell is visible unless an opaque tile lies strictly
 * between the origin and it. The blocking tile itself remains visible. This is a
 * simple, symmetric LOS model — good enough for a kid-friendly explorer and easy
 * to reason about; it can be swapped for shadowcasting later without API change.
 */
import { Grid, GridPos } from "./Grid";

export function fovKey(pos: GridPos): string {
  return `${pos.x},${pos.y}`;
}

export function computeFov(grid: Grid, origin: GridPos, radius: number): Set<string> {
  const visible = new Set<string>();
  visible.add(fovKey(origin));

  for (let dy = -radius; dy <= radius; dy++) {
    for (let dx = -radius; dx <= radius; dx++) {
      const target: GridPos = { x: origin.x + dx, y: origin.y + dy };
      if (!grid.inBounds(target)) continue;
      if (hasLineOfSight(grid, origin, target)) {
        visible.add(fovKey(target));
      }
    }
  }
  return visible;
}

/** True if no opaque tile lies strictly between origin and target. */
function hasLineOfSight(grid: Grid, origin: GridPos, target: GridPos): boolean {
  for (const cell of bresenham(origin, target)) {
    if (cell.x === origin.x && cell.y === origin.y) continue;
    if (cell.x === target.x && cell.y === target.y) continue;
    if (grid.isOpaque(cell)) return false;
  }
  return true;
}

/** Integer line from a to b inclusive (Bresenham). */
function bresenham(a: GridPos, b: GridPos): GridPos[] {
  const points: GridPos[] = [];
  let x0 = a.x;
  let y0 = a.y;
  const dx = Math.abs(b.x - x0);
  const dy = Math.abs(b.y - y0);
  const sx = x0 < b.x ? 1 : -1;
  const sy = y0 < b.y ? 1 : -1;
  let err = dx - dy;

  for (;;) {
    points.push({ x: x0, y: y0 });
    if (x0 === b.x && y0 === b.y) break;
    const e2 = 2 * err;
    if (e2 > -dy) {
      err -= dy;
      x0 += sx;
    }
    if (e2 < dx) {
      err += dx;
      y0 += sy;
    }
  }
  return points;
}
