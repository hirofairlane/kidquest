import { describe, expect, it } from "vitest";

import { PuzzleStateMachine } from "./PuzzleStateMachine";

function machine() {
  return new PuzzleStateMachine({
    id: "p1",
    conceptTags: ["fractions_halves"],
    canonicalAnswer: "4",
    acceptedAnswers: ["four"],
  });
}

describe("PuzzleStateMachine", () => {
  it("starts unanswered", () => {
    expect(machine().status).toBe("unanswered");
  });

  it("solves on a correct answer", () => {
    const p = machine();
    const r = p.submit("four");
    expect(r.correct).toBe(true);
    expect(p.status).toBe("correct");
    expect(p.isResolved()).toBe(true);
    expect(r.failedConcepts).toEqual([]);
  });

  it("surfaces failed concept tags on a wrong answer", () => {
    const p = machine();
    const r = p.submit("7");
    expect(r.correct).toBe(false);
    expect(p.status).toBe("incorrect");
    expect(r.failedConcepts).toEqual(["fractions_halves"]);
    expect(p.attempts).toBe(1);
  });

  it("can recover after a wrong answer and counts attempts", () => {
    const p = machine();
    p.submit("7");
    const r = p.submit("4");
    expect(r.correct).toBe(true);
    expect(p.attempts).toBe(2);
  });

  it("ignores submissions once solved", () => {
    const p = machine();
    p.submit("4");
    const r = p.submit("nonsense");
    expect(r.correct).toBe(true);
    expect(p.attempts).toBe(1);
  });
});
