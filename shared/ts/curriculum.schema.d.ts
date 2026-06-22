// AUTO-GENERATED from shared/schemas. Do not edit by hand. Run: pnpm codegen:ts

/**
 * Data-driven pedagogy binding a profile to subjects and concepts. Adding a profile is adding one of these.
 */
export interface Curriculum {
  curriculum_ref: string;
  title?: string;
  /**
   * @minItems 1
   */
  subjects: [
    {
      subject: "math" | "spanish" | "science" | "history" | "geography" | "english" | "electronics";
      /**
       * Language puzzles for this subject must be presented in.
       */
      language: "es" | "en";
      /**
       * Relative emphasis when generating the daily level.
       */
      weight?: number;
      /**
       * @minItems 1
       */
      concepts: [
        {
          concept_id: string;
          label: string;
          difficulty: number;
        },
        ...{
          concept_id: string;
          label: string;
          difficulty: number;
        }[]
      ];
    },
    ...{
      subject: "math" | "spanish" | "science" | "history" | "geography" | "english" | "electronics";
      /**
       * Language puzzles for this subject must be presented in.
       */
      language: "es" | "en";
      /**
       * Relative emphasis when generating the daily level.
       */
      weight?: number;
      /**
       * @minItems 1
       */
      concepts: [
        {
          concept_id: string;
          label: string;
          difficulty: number;
        },
        ...{
          concept_id: string;
          label: string;
          difficulty: number;
        }[]
      ];
    }[]
  ];
}
