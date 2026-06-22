/**
 * Puzzle lifecycle: unanswered → correct | incorrect.
 *
 * On a wrong answer it surfaces the puzzle's concept tags so the Game Director can
 * mark them for reinforcement (REQ-GAM-01). Pure and deterministic.
 */
import { isCorrect } from "./AnswerChecker";

export type PuzzleStatus = "unanswered" | "correct" | "incorrect";

export interface PuzzleDef {
  id: string;
  conceptTags: string[];
  canonicalAnswer: string;
  acceptedAnswers?: string[];
}

export interface SubmitResult {
  correct: boolean;
  status: PuzzleStatus;
  failedConcepts: string[];
}

export class PuzzleStateMachine {
  readonly def: PuzzleDef;
  private _status: PuzzleStatus = "unanswered";
  private _attempts = 0;

  constructor(def: PuzzleDef) {
    this.def = def;
  }

  get status(): PuzzleStatus {
    return this._status;
  }

  get attempts(): number {
    return this._attempts;
  }

  isResolved(): boolean {
    return this._status === "correct";
  }

  /** Submit an answer. Once solved, further submissions are no-ops. */
  submit(answer: string): SubmitResult {
    if (this._status === "correct") {
      return { correct: true, status: "correct", failedConcepts: [] };
    }
    this._attempts += 1;
    if (isCorrect(answer, this.def.canonicalAnswer, this.def.acceptedAnswers)) {
      this._status = "correct";
      return { correct: true, status: "correct", failedConcepts: [] };
    }
    this._status = "incorrect";
    return { correct: false, status: "incorrect", failedConcepts: [...this.def.conceptTags] };
  }
}
