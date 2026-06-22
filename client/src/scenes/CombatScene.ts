import Phaser from "phaser";

import { CombatEncounter } from "../engine/combat/CombatEncounter";
import { canAttack } from "../engine/combat/DamageResolver";
import { Unit, UnitSpec, spawnUnit } from "../engine/combat/Unit";
import { TodayResponse } from "../api/client";

interface CombatData {
  encounterId: string;
}

const HEX = 34;
const ORIGIN_X = 400;
const ORIGIN_Y = 280;

/** Hex combat view. Press SPACE to advance a turn: the active unit attacks the
 *  nearest opposing unit in range, otherwise passes. All resolution is done by
 *  the pure CombatEncounter engine. */
export class CombatScene extends Phaser.Scene {
  private encounter!: CombatEncounter;
  private status!: Phaser.GameObjects.Text;
  private labels: Phaser.GameObjects.Text[] = [];

  constructor() {
    super("Combat");
  }

  init(data: CombatData): void {
    const today = this.registry.get("today") as TodayResponse;
    const enc = today.level.encounters.find((e) => e.id === data.encounterId);
    const units: UnitSpec[] = (enc?.units ?? []) as unknown as UnitSpec[];
    this.encounter = new CombatEncounter(units.map(spawnUnit));
  }

  create(): void {
    this.add.rectangle(400, 300, 800, 600, 0x101018).setDepth(-1);
    this.add.text(20, 16, "Combat — press SPACE to fight, ESC to flee", { color: "#ffffff", fontSize: "14px" });
    this.status = this.add.text(20, 560, "", { color: "#ffd76a", fontSize: "14px" });
    this.render();
    this.input.keyboard?.on("keydown-SPACE", () => this.step());
    this.input.keyboard?.on("keydown-ESC", () => this.finish());
  }

  private hexToPixel(q: number, r: number): { x: number; y: number } {
    return {
      x: ORIGIN_X + HEX * Math.sqrt(3) * (q + r / 2),
      y: ORIGIN_Y + HEX * 1.5 * r,
    };
  }

  private render(): void {
    for (const label of this.labels) label.destroy();
    this.labels = [];
    for (const unit of this.encounter.aliveUnits()) {
      const { x, y } = this.hexToPixel(unit.axial.q, unit.axial.r);
      const color = unit.team === "player" ? "#6cf" : "#f87";
      this.labels.push(
        this.add
          .text(x, y, `${unit.name}\n${unit.hp}hp`, { color, align: "center", fontSize: "13px" })
          .setOrigin(0.5),
      );
    }
    const winner = this.encounter.winner();
    this.status.setText(winner ? `${winner} wins! (ESC to continue)` : `Turn: ${this.encounter.currentUnitId() ?? "-"}`);
  }

  private step(): void {
    if (this.encounter.winner()) return;
    const current = this.encounter.currentUnit();
    if (!current) return;
    const target = this.firstTargetInRange(current);
    if (target) {
      this.encounter.attack(target.id);
    } else {
      this.encounter.pass();
    }
    this.render();
  }

  private firstTargetInRange(current: Unit): Unit | undefined {
    return this.encounter
      .aliveUnits()
      .find((u) => u.team !== current.team && canAttack(current, u));
  }

  private finish(): void {
    this.scene.stop();
    this.scene.resume("Overworld");
  }
}
