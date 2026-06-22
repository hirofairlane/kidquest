import Phaser from "phaser";

import { TodayResponse, fetchTodayLevel } from "../api/client";
import { loadLevel } from "../engine/level/LevelLoader";

/**
 * Loads today's level from the content server, validates it through the engine's
 * LevelLoader, stashes it in the registry, and hands off to the overworld.
 */
export class BootScene extends Phaser.Scene {
  constructor() {
    super("Boot");
  }

  create(): void {
    const apiBase = this.registry.get("apiBase") as string;
    const profileId = this.registry.get("profileId") as string;
    const status = this.add.text(20, 20, "Loading today's quest…", { color: "#ffffff" });

    fetchTodayLevel(apiBase, profileId, (url) => fetch(url))
      .then((res: TodayResponse) => {
        const level = loadLevel(res.level);
        this.registry.set("level", level);
        this.registry.set("today", res);
        this.scene.start("Overworld");
      })
      .catch((err: unknown) => {
        status.setText(`Could not load content:\n${String(err)}`);
      });
  }
}
