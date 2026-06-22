import Phaser from "phaser";

import { TodayResponse } from "../api/client";

interface DialogueData {
  dialogueId: string;
}

/** Shows an NPC's lines and plays the pre-rendered TTS audio for the first line.
 *  Click to dismiss and return to the overworld. */
export class DialogueScene extends Phaser.Scene {
  constructor() {
    super("Dialogue");
  }

  create(data: DialogueData): void {
    const today = this.registry.get("today") as TodayResponse;
    const apiBase = this.registry.get("apiBase") as string;
    const dialogue = today.level.dialogues.find((d) => d.id === data.dialogueId);

    this.add.rectangle(400, 480, 760, 200, 0x000000, 0.8).setDepth(20);
    const speaker = dialogue?.speaker ?? "???";
    const text = dialogue?.lines.map((l) => l.text).join("\n") ?? "...";
    this.add
      .text(40, 400, `${speaker}:\n${text}\n\n(click to continue)`, { color: "#ffffff", fontSize: "16px", wordWrap: { width: 720 } })
      .setDepth(21);

    if (dialogue && dialogue.lines.length > 0) {
      const url = `${apiBase.replace(/\/$/, "")}/static/${today.profile_id}/${today.date}/audio/${dialogue.id}_0.wav`;
      try {
        const audio = new Audio(url);
        void audio.play().catch(() => undefined);
      } catch {
        // audio is best-effort; ignore if unavailable
      }
    }

    this.input.once("pointerdown", () => {
      this.scene.stop();
      this.scene.resume("Overworld");
    });
  }
}
