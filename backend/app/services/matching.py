# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
import uuid


def compute_affinity(
    user_answers: dict[uuid.UUID, int | None],
    candidate_positions: dict[uuid.UUID, int],
    statement_weights: dict[uuid.UUID, int],
) -> float:
    """
    Compute affinity between a user's answers and a candidate's positions.

    user_answers: {statement_id: -2..+2 or None (skipped)}
    candidate_positions: {statement_id: -2..+2}
    statement_weights: {statement_id: 1..3}
    Returns: 0.0..100.0 affinity percentage.
    """
    total_weight = 0
    weighted_distance = 0
    for sid, user_v in user_answers.items():
        if user_v is None:
            continue
        if sid not in candidate_positions:
            continue
        cand_v = candidate_positions[sid]
        w = statement_weights.get(sid, 1)
        distance = abs(user_v - cand_v)
        weighted_distance += distance * w
        total_weight += 4 * w
    if total_weight == 0:
        return 0.0
    return round((1 - weighted_distance / total_weight) * 100, 1)


def compute_affinity_high_confidence(
    user_answers: dict[uuid.UUID, int | None],
    candidate_positions: dict[uuid.UUID, int],
    high_confidence_sids: set[uuid.UUID],
    statement_weights: dict[uuid.UUID, int],
) -> float | None:
    """
    Compute affinity using ONLY positions with confidence='high'.

    Returns None if candidate has no high-confidence positions that overlap
    with the user's answered statements.
    """
    total_weight = 0
    weighted_distance = 0
    for sid, user_v in user_answers.items():
        if user_v is None:
            continue
        if sid not in candidate_positions:
            continue
        if sid not in high_confidence_sids:
            continue
        cand_v = candidate_positions[sid]
        w = statement_weights.get(sid, 1)
        distance = abs(user_v - cand_v)
        weighted_distance += distance * w
        total_weight += 4 * w
    if total_weight == 0:
        return None
    return round((1 - weighted_distance / total_weight) * 100, 1)
