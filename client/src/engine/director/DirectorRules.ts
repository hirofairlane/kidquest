/**
 * Game Director adaptive rules (client-side, advisory copy).
 *
 * These pure functions implement the three adaptive mechanics. The SERVER holds
 * the authoritative implementation (`server/kidquest_server/director/rules.py`);
 * a shared golden-vector fixture (`shared/fixtures/director/cases.json`) is
 * exercised by both test suites to keep them in lockstep.
 */

// ── REQ-GAM-01: educational feedback loop ──────────────────────────────────────

export interface ReinforceConcept {
  conceptId: string;
  subject: string;
  failures: number;
}

export interface FailedConcept {
  conceptId: string;
  subject: string;
}

/**
 * Fold this level's failed concepts into the reinforcement list: increment the
 * count for concepts already tracked, append new ones (first occurrence = 1).
 * Existing entries keep their position; new ones are appended in input order.
 */
export function updateReinforce(
  reinforce: readonly ReinforceConcept[],
  failed: readonly FailedConcept[],
): ReinforceConcept[] {
  const result: ReinforceConcept[] = reinforce.map((r) => ({ ...r }));
  const index = new Map<string, ReinforceConcept>(result.map((r) => [r.conceptId, r]));
  for (const f of failed) {
    const existing = index.get(f.conceptId);
    if (existing) {
      existing.failures += 1;
    } else {
      const entry: ReinforceConcept = { conceptId: f.conceptId, subject: f.subject, failures: 1 };
      result.push(entry);
      index.set(f.conceptId, entry);
    }
  }
  return result;
}

// ── REQ-GAM-02: anti-frustration ───────────────────────────────────────────────

export interface AntiFrustrationInput {
  defeatStreak: number;
  elapsedSeconds: number;
  timeLimitSeconds: number;
}

/** Spawn a Magic Artifact after two straight defeats or when the level drags on. */
export function shouldSpawnArtifact(input: AntiFrustrationInput): boolean {
  return input.defeatStreak >= 2 || input.elapsedSeconds > input.timeLimitSeconds;
}

// ── REQ-GAM-03: dynamic difficulty ─────────────────────────────────────────────

export type LevelResult = "cleared" | "defeated";

const DIFFICULTY_STEP = 1.1;
const STRONG_CLEAR_HP = 0.8;

/** Round to 4 decimals so TS and Python agree on floating-point results. */
function round4(x: number): number {
  return Math.round(x * 1e4) / 1e4;
}

/** A clear with more than 80% HP raises global difficulty by 10%. */
export function nextDifficulty(modifier: number, result: LevelResult, hpPct: number): number {
  if (result === "cleared" && hpPct > STRONG_CLEAR_HP) {
    return round4(modifier * DIFFICULTY_STEP);
  }
  return modifier;
}
