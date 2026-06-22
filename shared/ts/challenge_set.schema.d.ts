// AUTO-GENERATED from shared/schemas. Do not edit by hand. Run: pnpm codegen:ts

export type Language = "es" | "en";
export type Subject = "math" | "spanish" | "science_en" | "history" | "geography" | "english" | "electronics";

/**
 * The educational layer the AI authors for one day's map and learner: curriculum-tagged Sphinx riddles, signs and events to be patched into a fheroes2 .fh2m template. The strict contract for the local LLM (Ollama structured output) and validated server-side.
 */
export interface ChallengeSet {
  schema_version: "1";
  profile_id: string;
  /**
   * Historical era / civilization theme of the map.
   */
  era:
    | "greek_colonies"
    | "phoenician_carthaginian"
    | "roman_hispania"
    | "visigothic"
    | "al_andalus"
    | "christian_kingdoms";
  language_default: Language;
  /**
   * Riddle challenges, one per Sphinx slot in the template.
   *
   * @minItems 1
   */
  sphinxes: [
    {
      subject: Subject;
      /**
       * @minItems 1
       */
      concept_tags: [string, ...string[]];
      riddle: LocalizedText;
      /**
       * All accepted answer strings. fheroes2 matches EXACTLY, so enumerate tolerant variants (case, accents, synonyms, es/en).
       *
       * @minItems 1
       */
      answers: [string, ...string[]];
      hint?: LocalizedText | null;
      reward: Reward;
    },
    ...{
      subject: Subject;
      /**
       * @minItems 1
       */
      concept_tags: [string, ...string[]];
      riddle: LocalizedText;
      /**
       * All accepted answer strings. fheroes2 matches EXACTLY, so enumerate tolerant variants (case, accents, synonyms, es/en).
       *
       * @minItems 1
       */
      answers: [string, ...string[]];
      hint?: LocalizedText | null;
      reward: Reward;
    }[]
  ];
  /**
   * Lore / hint text placed on signs.
   */
  signs?: LocalizedText[];
  /**
   * Adventure-map events: a message plus a reward.
   */
  events?: {
    message: LocalizedText;
    reward: Reward;
  }[];
}
export interface LocalizedText {
  text: string;
  language: Language;
}
/**
 * Resource reward granted on success (fheroes2 Funds).
 */
export interface Reward {
  gold?: number;
  wood?: number;
  ore?: number;
  mercury?: number;
  sulfur?: number;
  crystal?: number;
  gems?: number;
}
