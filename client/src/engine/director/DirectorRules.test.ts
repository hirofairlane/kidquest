import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import {
  FailedConcept,
  ReinforceConcept,
  nextDifficulty,
  shouldSpawnArtifact,
  updateReinforce,
} from "./DirectorRules";

interface Cases {
  feedback_loop: Array<{
    name: string;
    input: { reinforce: Array<Record<string, unknown>>; failed: Array<Record<string, unknown>> };
    expected: Array<{ concept_id: string; subject: string; failures: number }>;
  }>;
  anti_frustration: Array<{
    name: string;
    input: { defeat_streak: number; elapsed_seconds: number; time_limit_seconds: number };
    expected: { spawn_artifact: boolean };
  }>;
  dynamic_difficulty: Array<{
    name: string;
    input: { difficulty_modifier: number; result: "cleared" | "defeated"; hp_pct: number };
    expected: { difficulty_modifier: number };
  }>;
}

const casesPath = fileURLToPath(new URL("../../../../shared/fixtures/director/cases.json", import.meta.url));
const cases: Cases = JSON.parse(readFileSync(casesPath, "utf8"));

function toReinforce(rows: Array<Record<string, unknown>>): ReinforceConcept[] {
  return rows.map((r) => ({
    conceptId: r.concept_id as string,
    subject: r.subject as string,
    failures: r.failures as number,
  }));
}
function toFailed(rows: Array<Record<string, unknown>>): FailedConcept[] {
  return rows.map((r) => ({ conceptId: r.concept_id as string, subject: r.subject as string }));
}

describe("Director parity — feedback loop", () => {
  for (const c of cases.feedback_loop) {
    it(c.name, () => {
      const out = updateReinforce(toReinforce(c.input.reinforce), toFailed(c.input.failed));
      expect(out).toEqual(toReinforce(c.expected));
    });
  }
});

describe("Director parity — anti-frustration", () => {
  for (const c of cases.anti_frustration) {
    it(c.name, () => {
      expect(
        shouldSpawnArtifact({
          defeatStreak: c.input.defeat_streak,
          elapsedSeconds: c.input.elapsed_seconds,
          timeLimitSeconds: c.input.time_limit_seconds,
        }),
      ).toBe(c.expected.spawn_artifact);
    });
  }
});

describe("Director parity — dynamic difficulty", () => {
  for (const c of cases.dynamic_difficulty) {
    it(c.name, () => {
      expect(nextDifficulty(c.input.difficulty_modifier, c.input.result, c.input.hp_pct)).toBe(
        c.expected.difficulty_modifier,
      );
    });
  }
});
