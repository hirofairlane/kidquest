// AUTO-GENERATED from shared/schemas. Do not edit by hand. Run: pnpm codegen:ts

export type Subject = "math" | "spanish" | "science_en" | "history" | "geography" | "english" | "electronics";

/**
 * Per-player learning and progress profile. Real instances are private (gitignored); only generic examples are committed.
 */
export interface PlayerProfile {
  /**
   * Stable key, e.g. 'youth_10yo'. Binds to a curriculum.
   */
  profile_id: string;
  /**
   * Human name. Present only in private live profiles, never in committed examples.
   */
  display_name?: string;
  age: number;
  /**
   * Curriculum file id under curricula/profiles, e.g. 'youth_10yo'.
   */
  curriculum_ref: string;
  /**
   * Global difficulty multiplier. 1.0 = baseline; ×1.10 on strong clears.
   */
  difficulty_modifier: number;
  /**
   * Consecutive defeats; >= 2 triggers anti-frustration.
   */
  defeat_streak: number;
  /**
   * ISO-8601 timestamp when the current level started, for the time-over-limit trigger.
   */
  last_level_started_at?: string | null;
  /**
   * Concepts the player failed and should be re-taught next.
   */
  reinforce_concepts?: {
    concept_id: string;
    subject: Subject;
    failures: number;
    added_at?: string | null;
  }[];
  mastered_concepts?: string[];
  history?: {
    date: string;
    result: "cleared" | "defeated";
    hp_pct: number;
  }[];
}
