/**
 * Client entry point. The Phaser view layer is wired here in milestone M8; until
 * then this only proves the build pipeline. All game logic lives in `engine/`
 * (pure TypeScript, no Phaser), tested with Vitest before any scene exists.
 */
import { SUPPORTED_SCHEMA_VERSION } from "./engine/contract";

const root = document.getElementById("game");
if (root) {
  root.textContent = `KidQuest — engine contract v${SUPPORTED_SCHEMA_VERSION} (scaffolding)`;
}
