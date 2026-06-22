/**
 * Tolerant answer checking for puzzles.
 *
 * Children type imperfectly and the content is bilingual, so we normalize accents,
 * case and whitespace, and compare numbers by value (so "1/2" matches "0.5"). A
 * puzzle accepts its canonical answer plus an optional list of accepted variants.
 */

/** Lowercase, trim, collapse whitespace, and strip diacritics ("León" → "leon"). */
export function normalizeAnswer(s: string): string {
  return s
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/\s+/g, " ");
}

/** Parse a number, supporting simple fractions like "3/4"; null if not numeric. */
export function numericValue(s: string): number | null {
  const t = s.trim();
  const frac = /^(-?\d+)\s*\/\s*(\d+)$/.exec(t);
  if (frac) {
    const denom = Number(frac[2]);
    if (denom === 0) return null;
    return Number(frac[1]) / denom;
  }
  if (/^-?\d+(\.\d+)?$/.test(t)) return Number(t);
  return null;
}

/** True if `answer` matches the canonical answer or any accepted variant. */
export function isCorrect(answer: string, canonical: string, accepted: readonly string[] = []): boolean {
  const candidates = [canonical, ...accepted];
  const normAnswer = normalizeAnswer(answer);
  const answerNum = numericValue(answer);

  return candidates.some((candidate) => {
    if (normAnswer === normalizeAnswer(candidate)) return true;
    const candidateNum = numericValue(candidate);
    return answerNum !== null && candidateNum !== null && answerNum === candidateNum;
  });
}
