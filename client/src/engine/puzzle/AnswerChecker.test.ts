import { describe, expect, it } from "vitest";

import { isCorrect, normalizeAnswer, numericValue } from "./AnswerChecker";

describe("normalizeAnswer", () => {
  it("strips accents, case and extra whitespace", () => {
    expect(normalizeAnswer("  León ")).toBe("leon");
    expect(normalizeAnswer("EL   Cid")).toBe("el cid");
  });
});

describe("numericValue", () => {
  it("parses integers, decimals and fractions", () => {
    expect(numericValue("3")).toBe(3);
    expect(numericValue("0.5")).toBe(0.5);
    expect(numericValue("1/2")).toBe(0.5);
    expect(numericValue("3 / 4")).toBe(0.75);
  });

  it("returns null for non-numbers and division by zero", () => {
    expect(numericValue("cat")).toBeNull();
    expect(numericValue("1/0")).toBeNull();
  });
});

describe("isCorrect", () => {
  it("matches the canonical answer ignoring accents/case", () => {
    expect(isCorrect("leon", "León")).toBe(true);
    expect(isCorrect("madrid", "León")).toBe(false);
  });

  it("matches accepted variants", () => {
    expect(isCorrect("four", "4", ["four"])).toBe(true);
  });

  it("matches numbers by value across notations", () => {
    expect(isCorrect("1/2", "0.5")).toBe(true);
    expect(isCorrect("0.50", "1/2")).toBe(true);
  });
});
