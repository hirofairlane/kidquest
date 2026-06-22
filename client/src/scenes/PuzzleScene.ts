import Phaser from "phaser";

import { PuzzleStateMachine } from "../engine/puzzle/PuzzleStateMachine";
import { LoadedLevel } from "../engine/level/LevelLoader";
import { TodayResponse } from "../api/client";

interface PuzzleData {
  puzzleId: string;
}

/** Presents a puzzle and checks answers with the pure PuzzleStateMachine.
 *  Multiple-choice answers are buttons; free-text uses a prompt dialog. */
export class PuzzleScene extends Phaser.Scene {
  constructor() {
    super("Puzzle");
  }

  create(data: PuzzleData): void {
    const level = this.registry.get("level") as LoadedLevel;
    const today = this.registry.get("today") as TodayResponse;
    const raw = today.level.puzzles.find((p) => p.id === data.puzzleId);
    const def = level.puzzles.get(data.puzzleId);
    if (!raw || !def) {
      this.close();
      return;
    }
    const machine = new PuzzleStateMachine(def);

    this.add.rectangle(400, 300, 720, 420, 0x14141c, 0.95).setDepth(20);
    this.add
      .text(80, 140, raw.prompt?.text ?? "Solve the riddle", {
        color: "#ffffff",
        fontSize: "20px",
        wordWrap: { width: 620 },
      })
      .setDepth(21);
    const feedback = this.add.text(80, 420, "", { color: "#ffd76a", fontSize: "18px" }).setDepth(21);

    const submit = (answer: string): void => {
      const result = machine.submit(answer);
      if (result.correct) {
        feedback.setColor("#7CFC7C").setText("Correct!");
        this.time.delayedCall(700, () => this.close());
      } else {
        feedback.setColor("#ff8a8a").setText("Try again…");
      }
    };

    const options = raw.options ?? null;
    if (options && options.length > 0) {
      options.forEach((opt, i) => {
        this.add
          .text(80, 240 + i * 40, `▶ ${opt}`, { color: "#9cf", fontSize: "18px" })
          .setDepth(21)
          .setInteractive({ useHandCursor: true })
          .on("pointerdown", () => submit(opt));
      });
    } else {
      this.add
        .text(80, 250, "(click to type your answer)", { color: "#9cf", fontSize: "16px" })
        .setDepth(21)
        .setInteractive({ useHandCursor: true })
        .on("pointerdown", () => {
          const answer = window.prompt(raw.prompt?.text ?? "Your answer:") ?? "";
          if (answer) submit(answer);
        });
    }

    this.input.keyboard?.on("keydown-ESC", () => this.close());
  }

  private close(): void {
    this.scene.stop();
    this.scene.resume("Overworld");
  }
}
