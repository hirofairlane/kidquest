/**
 * Map a tile kind to a flat fill colour for the placeholder renderer (used until
 * generated sprites land in M7+). Pure, so it is unit-testable.
 */
const TILE_COLORS: Record<string, number> = {
  grass: 0x4f9d4f,
  forest: 0x2f6f3f,
  water: 0x3a6ea5,
  mountain: 0x8a7a6a,
  wall: 0x444444,
  road: 0xc2a76a,
  sand: 0xd8c98a,
};

const FALLBACK = 0x000000;

export function tileColor(kind: string): number {
  return TILE_COLORS[kind] ?? FALLBACK;
}
