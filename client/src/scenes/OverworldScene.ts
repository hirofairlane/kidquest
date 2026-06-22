import Phaser from "phaser";

import { TodayResponse } from "../api/client";
import { LoadedLevel } from "../engine/level/LevelLoader";
import { computeFov } from "../engine/overworld/Fov";
import { FogOfWar } from "../engine/overworld/FogOfWar";
import { resolveStep } from "../engine/overworld/Movement";
import { tileColor } from "../view/tileColors";

const TILE = 40;
const FOV_RADIUS = 4;

/** Grid exploration view: renders tiles, fog of war, the player and entities,
 *  and routes collisions to the puzzle/dialogue/combat scenes. No game logic
 *  lives here — it only drives the pure engine. */
export class OverworldScene extends Phaser.Scene {
  private level!: LoadedLevel;
  private today!: TodayResponse;
  private player = { x: 0, y: 0 };
  private fog!: FogOfWar;
  private marker!: Phaser.GameObjects.Arc;
  private fogCells: Phaser.GameObjects.Rectangle[][] = [];

  constructor() {
    super("Overworld");
  }

  create(): void {
    this.level = this.registry.get("level") as LoadedLevel;
    this.today = this.registry.get("today") as TodayResponse;
    this.player = { ...this.level.start };
    this.fog = new FogOfWar(this.level.grid.width, this.level.grid.height);

    this.drawTiles();
    this.drawEntities();
    this.marker = this.add.circle(0, 0, TILE * 0.35, 0xffe14a).setDepth(5);
    this.placeMarker();
    this.refreshFog();
    this.bindInput();

    this.add
      .text(8, this.scale.height - 22, this.today.stale ? "(yesterday's quest)" : `quest ${this.today.date}`, {
        color: "#cccccc",
        fontSize: "12px",
      })
      .setDepth(10);
  }

  private drawTiles(): void {
    for (let y = 0; y < this.level.grid.height; y++) {
      this.fogCells[y] = [];
      for (let x = 0; x < this.level.grid.width; x++) {
        const kind = this.level.grid.tileAt({ x, y }).kind;
        this.add.rectangle(x * TILE + TILE / 2, y * TILE + TILE / 2, TILE - 1, TILE - 1, tileColor(kind));
        const fogRect = this.add
          .rectangle(x * TILE + TILE / 2, y * TILE + TILE / 2, TILE, TILE, 0x000000)
          .setDepth(8);
        this.fogCells[y][x] = fogRect;
      }
    }
  }

  private drawEntities(): void {
    const glyphs: Record<string, string> = { chest: "📦", npc: "🧝", monster: "🐉" };
    for (const e of this.level.entities) {
      this.add
        .text(e.pos.x * TILE + TILE / 2, e.pos.y * TILE + TILE / 2, glyphs[e.type] ?? "?", {
          fontSize: "20px",
        })
        .setOrigin(0.5)
        .setDepth(4);
    }
  }

  private placeMarker(): void {
    this.marker.setPosition(this.player.x * TILE + TILE / 2, this.player.y * TILE + TILE / 2);
  }

  private bindInput(): void {
    const kb = this.input.keyboard;
    if (!kb) return;
    kb.on("keydown-LEFT", () => this.tryMove(-1, 0));
    kb.on("keydown-RIGHT", () => this.tryMove(1, 0));
    kb.on("keydown-UP", () => this.tryMove(0, -1));
    kb.on("keydown-DOWN", () => this.tryMove(0, 1));
  }

  private tryMove(dx: number, dy: number): void {
    const step = resolveStep(this.level.grid, this.level.entities, this.player, { dx, dy });
    if (step.moved) {
      this.player = step.to;
      this.placeMarker();
      this.refreshFog();
      return;
    }
    if (step.entityId) {
      this.interact(step.entityId, step.collision);
    }
  }

  private interact(entityId: string, collision: string): void {
    const raw = this.today.level.entities.find((e) => e.id === entityId);
    if (!raw) return;
    if (collision === "puzzle" && raw.puzzle_ref) {
      this.scene.pause();
      this.scene.launch("Puzzle", { puzzleId: raw.puzzle_ref });
    } else if (collision === "dialogue" && raw.dialogue_ref) {
      this.scene.pause();
      this.scene.launch("Dialogue", { dialogueId: raw.dialogue_ref });
    } else if (collision === "combat" && raw.encounter_ref) {
      this.scene.pause();
      this.scene.launch("Combat", { encounterId: raw.encounter_ref });
    }
  }

  private refreshFog(): void {
    const visible = computeFov(this.level.grid, this.player, FOV_RADIUS);
    this.fog.update(
      [...visible].map((key) => {
        const [x, y] = key.split(",").map(Number);
        return { x, y };
      }),
    );
    for (let y = 0; y < this.level.grid.height; y++) {
      for (let x = 0; x < this.level.grid.width; x++) {
        const state = this.fog.get({ x, y });
        const alpha = state === "visible" ? 0 : state === "seen" ? 0.5 : 1;
        this.fogCells[y][x].setAlpha(alpha);
      }
    }
  }
}
