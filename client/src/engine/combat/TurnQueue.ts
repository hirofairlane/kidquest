/**
 * Initiative turn order for a combat encounter.
 *
 * Units act from highest initiative to lowest; ties break by unit id (ascending)
 * for determinism. The queue cycles round-robin and supports removing a unit that
 * dies mid-round without disturbing whose turn it is.
 */
import { Unit } from "./Unit";

export class TurnQueue {
  private order: string[];
  private idx = 0;

  constructor(units: Unit[]) {
    this.order = [...units]
      .sort((a, b) => b.initiative - a.initiative || (a.id < b.id ? -1 : a.id > b.id ? 1 : 0))
      .map((u) => u.id);
  }

  /** Turn order as unit ids, highest initiative first. */
  ids(): string[] {
    return [...this.order];
  }

  get size(): number {
    return this.order.length;
  }

  isEmpty(): boolean {
    return this.order.length === 0;
  }

  /** The unit whose turn it currently is, or undefined if the queue is empty. */
  current(): string | undefined {
    return this.order[this.idx];
  }

  /** Advance to the next unit (wraps around). */
  advance(): void {
    if (this.order.length === 0) return;
    this.idx = (this.idx + 1) % this.order.length;
  }

  /** Return the current unit id, then advance the turn. */
  next(): string | undefined {
    const cur = this.current();
    this.advance();
    return cur;
  }

  /** Remove a unit from the rotation, keeping the current turn pointer valid. */
  remove(id: string): void {
    const pos = this.order.indexOf(id);
    if (pos === -1) return;
    this.order.splice(pos, 1);
    if (this.order.length === 0) {
      this.idx = 0;
      return;
    }
    if (pos < this.idx) {
      this.idx -= 1;
    }
    this.idx %= this.order.length;
  }
}
