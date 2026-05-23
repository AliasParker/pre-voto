// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 Equipo pre.voto
/**
 * Compute affinity between a user's answers and a candidate's positions.
 *
 * Must produce identical results to backend/app/services/matching.py.
 *
 * @param userAnswers - Map of statement_id to user value (-2..+2) or null (skipped)
 * @param candidatePositions - Map of statement_id to candidate value (-2..+2)
 * @param statementWeights - Map of statement_id to weight (1..3)
 * @returns Affinity percentage 0.0..100.0
 */
export function computeAffinity(
  userAnswers: Record<string, number | null>,
  candidatePositions: Record<string, number>,
  statementWeights: Record<string, number>,
): number {
  let totalWeight = 0;
  let weightedDistance = 0;

  for (const [sid, userV] of Object.entries(userAnswers)) {
    if (userV === null || userV === undefined) {
      continue;
    }
    if (!(sid in candidatePositions)) {
      continue;
    }
    const candV = candidatePositions[sid];
    const w = statementWeights[sid] ?? 1;
    const distance = Math.abs(userV - candV);
    weightedDistance += distance * w;
    totalWeight += 4 * w;
  }

  if (totalWeight === 0) {
    return 0.0;
  }

  // Math.round(x * 1000) / 10 is equivalent to Python's round(x * 100, 1)
  return Math.round((1 - weightedDistance / totalWeight) * 1000) / 10;
}
