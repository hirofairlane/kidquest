// AUTO-GENERATED from shared/schemas. Do not edit by hand. Run: pnpm codegen:ts

export type Language = "es" | "en";
export type Subject = "math" | "spanish" | "science_en" | "history" | "geography" | "english" | "electronics";

/**
 * The strict contract the local LLM must return for one day's level. Cross-field invariants (matrix dims, ref resolution, axial-in-radius, >=1 player unit) are enforced by schema_validator.py and the client LevelLoader.
 */
export interface DailyLevel {
  schema_version: "1";
  profile_id: string;
  language_default: Language;
  overworld: {
    width: number;
    height: number;
    /**
     * Map from stringified integer tile id to its definition.
     */
    tile_legend: {
      [k: string]: {
        name: string;
        walkable: boolean;
        kind: "grass" | "water" | "mountain" | "wall" | "road" | "forest" | "sand";
      };
    };
    /**
     * height rows of width tile ids; ids must exist in tile_legend.
     */
    matrix: number[][];
    start: GridPos;
  };
  entities: {
    id: string;
    type: "chest" | "npc" | "monster";
    pos: GridPos;
    puzzle_ref?: string | null;
    dialogue_ref?: string | null;
    encounter_ref?: string | null;
    /**
     * Lore tag, e.g. 'gamusino', 'cuelebre', 'artificer_device'.
     */
    lore?: string | null;
  }[];
  puzzles: {
    id: string;
    /**
     * @minItems 1
     */
    concept_tags: [string, ...string[]];
    subject: Subject;
    prompt: LocalizedText;
    kind: "multiple_choice" | "free_text" | "i_spy_shape" | "name_in_english" | "circuit";
    options?: string[] | null;
    /**
     * Canonical answer.
     */
    answer: string;
    /**
     * Additional accepted forms (normalized client-side).
     */
    accepted_answers?: string[] | null;
    hint?: LocalizedText | null;
  }[];
  dialogues: {
    id: string;
    speaker: string;
    /**
     * @minItems 1
     */
    lines: [
      {
        text: string;
        language: Language;
        /**
         * Piper voice id mapped server-side.
         */
        voice: string;
      },
      ...{
        text: string;
        language: Language;
        /**
         * Piper voice id mapped server-side.
         */
        voice: string;
      }[]
    ];
  }[];
  encounters: {
    id: string;
    hex_radius: number;
    /**
     * @minItems 2
     */
    units: [
      {
        id: string;
        team: "player" | "enemy";
        name: string;
        axial: AxialCoord;
        initiative: number;
        stats: {
          hp: number;
          atk: number;
          def: number;
          speed: number;
          range: number;
        };
        lore?: string | null;
      },
      {
        id: string;
        team: "player" | "enemy";
        name: string;
        axial: AxialCoord;
        initiative: number;
        stats: {
          hp: number;
          atk: number;
          def: number;
          speed: number;
          range: number;
        };
        lore?: string | null;
      },
      ...{
        id: string;
        team: "player" | "enemy";
        name: string;
        axial: AxialCoord;
        initiative: number;
        stats: {
          hp: number;
          atk: number;
          def: number;
          speed: number;
          range: number;
        };
        lore?: string | null;
      }[]
    ];
  }[];
}
export interface GridPos {
  x: number;
  y: number;
}
export interface LocalizedText {
  text: string;
  language: Language;
}
export interface AxialCoord {
  q: number;
  r: number;
}
