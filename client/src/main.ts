/**
 * Client entry point: build the Phaser game and wire the scenes. All game logic
 * lives in `engine/` (pure, Vitest-tested); these scenes are only the view.
 *
 * Configure via URL: `?profile=child_6yo`. The content server base URL comes from
 * the `VITE_API_BASE` build env (empty = same origin).
 */
import Phaser from "phaser";

import { BootScene } from "./scenes/BootScene";
import { CombatScene } from "./scenes/CombatScene";
import { DialogueScene } from "./scenes/DialogueScene";
import { OverworldScene } from "./scenes/OverworldScene";
import { PuzzleScene } from "./scenes/PuzzleScene";

const params = new URLSearchParams(window.location.search);
const profileId = params.get("profile") ?? "youth_10yo";
const apiBase = (import.meta as unknown as { env?: { VITE_API_BASE?: string } }).env?.VITE_API_BASE ?? "";

const game = new Phaser.Game({
  type: Phaser.AUTO,
  width: 800,
  height: 600,
  parent: "game",
  backgroundColor: "#1d1d1d",
  scene: [BootScene, OverworldScene, CombatScene, DialogueScene, PuzzleScene],
});

game.registry.set("apiBase", apiBase);
game.registry.set("profileId", profileId);
