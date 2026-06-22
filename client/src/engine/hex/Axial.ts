/**
 * Axial hex-coordinate math (pointy-top, axial q/r).
 *
 * Pure functions, no rendering and no Phaser. This is the geometric foundation of
 * the tactical combat board. Axial coordinates map to cube coordinates via
 * `s = -q - r`, which is how distance is computed. See
 * https://www.redblobgames.com/grids/hexagons/ for the reference model.
 *
 * The shape `{ q, r }` matches `daily_level.schema.json` (encounter unit `axial`).
 */
export interface Axial {
  q: number;
  r: number;
}

/** The six axial direction vectors, in clockwise order. */
const DIRECTIONS: readonly Axial[] = [
  { q: 1, r: 0 },
  { q: 1, r: -1 },
  { q: 0, r: -1 },
  { q: -1, r: 0 },
  { q: -1, r: 1 },
  { q: 0, r: 1 },
];

export function axialEquals(a: Axial, b: Axial): boolean {
  return a.q === b.q && a.r === b.r;
}

export function axialAdd(a: Axial, b: Axial): Axial {
  return { q: a.q + b.q, r: a.r + b.r };
}

export function axialSubtract(a: Axial, b: Axial): Axial {
  return { q: a.q - b.q, r: a.r - b.r };
}

/** Distance in hex steps between two cells (cube distance over axial coords). */
export function axialDistance(a: Axial, b: Axial): number {
  const dq = a.q - b.q;
  const dr = a.r - b.r;
  const ds = dq + dr; // -(q+r) difference, i.e. cube s axis
  return (Math.abs(dq) + Math.abs(dr) + Math.abs(ds)) / 2;
}

/** The (up to) six adjacent cells. */
export function axialNeighbors(c: Axial): Axial[] {
  return DIRECTIONS.map((d) => axialAdd(c, d));
}

/** All cells within `radius` steps of the center, inclusive (a filled hexagon). */
export function axialRange(center: Axial, radius: number): Axial[] {
  const cells: Axial[] = [];
  for (let dq = -radius; dq <= radius; dq++) {
    const lo = Math.max(-radius, -dq - radius);
    const hi = Math.min(radius, -dq + radius);
    for (let dr = lo; dr <= hi; dr++) {
      cells.push({ q: center.q + dq, r: center.r + dr });
    }
  }
  return cells;
}

/** Straight line of cells from `a` to `b`, inclusive of both endpoints. */
export function axialLine(a: Axial, b: Axial): Axial[] {
  const n = axialDistance(a, b);
  if (n === 0) return [{ q: a.q, r: a.r }];
  const line: Axial[] = [];
  for (let i = 0; i <= n; i++) {
    line.push(axialRound(axialLerp(a, b, i / n)));
  }
  return line;
}

interface FractionalAxial {
  q: number;
  r: number;
}

function axialLerp(a: Axial, b: Axial, t: number): FractionalAxial {
  return { q: a.q + (b.q - a.q) * t, r: a.r + (b.r - a.r) * t };
}

/** Round a fractional axial coordinate to the nearest hex (via cube rounding). */
function axialRound(f: FractionalAxial): Axial {
  const s = -f.q - f.r;
  let rq = Math.round(f.q);
  let rr = Math.round(f.r);
  const rs = Math.round(s);

  const dq = Math.abs(rq - f.q);
  const dr = Math.abs(rr - f.r);
  const ds = Math.abs(rs - s);

  if (dq > dr && dq > ds) {
    rq = -rr - rs;
  } else if (dr > ds) {
    rr = -rq - rs;
  }
  return { q: rq, r: rr };
}
