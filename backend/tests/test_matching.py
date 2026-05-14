import uuid

from app.services.matching import compute_affinity


def _uuid(n: int) -> uuid.UUID:
    return uuid.UUID(f"00000000-0000-0000-0000-{n:012d}")


class TestComputeAffinity:
    """Tests for the matching algorithm — must match SPEC 3.4 byte-for-byte."""

    def test_neutral_user_vs_extreme_candidate(self):
        """User all 0 vs candidate all +2 → 50.0%."""
        sids = [_uuid(i) for i in range(1, 4)]
        user = {sid: 0 for sid in sids}
        cand = {sid: 2 for sid in sids}
        weights = {sid: 1 for sid in sids}
        assert compute_affinity(user, cand, weights) == 50.0

    def test_perfect_agreement(self):
        """Identical answers → 100.0%."""
        sids = [_uuid(i) for i in range(1, 6)]
        answers = {sids[0]: 2, sids[1]: -1, sids[2]: 0, sids[3]: 1, sids[4]: -2}
        weights = {sid: 1 for sid in sids}
        assert compute_affinity(answers, answers, weights) == 100.0

    def test_perfect_disagreement(self):
        """User +2 everywhere, candidate -2 everywhere → 0.0%."""
        sids = [_uuid(i) for i in range(1, 4)]
        user = {sid: 2 for sid in sids}
        cand = {sid: -2 for sid in sids}
        weights = {sid: 1 for sid in sids}
        assert compute_affinity(user, cand, weights) == 0.0

    def test_mixed_answers(self):
        """Manually calculated mixed case."""
        s1, s2, s3 = _uuid(1), _uuid(2), _uuid(3)
        user = {s1: 2, s2: -1, s3: 0}
        cand = {s1: 1, s2: 1, s3: -1}
        weights = {s1: 1, s2: 1, s3: 1}
        # distances: |2-1|=1, |-1-1|=2, |0-(-1)|=1 → total_dist=4
        # total_weight = 4*3 = 12
        # affinity = (1 - 4/12) * 100 = 66.66... → round to 66.7
        assert compute_affinity(user, cand, weights) == 66.7

    def test_all_skipped(self):
        """All answers None → 0.0%."""
        sids = [_uuid(i) for i in range(1, 4)]
        user = {sid: None for sid in sids}
        cand = {sid: 1 for sid in sids}
        weights = {sid: 1 for sid in sids}
        assert compute_affinity(user, cand, weights) == 0.0

    def test_some_skipped(self):
        """Some answers skipped — only answered ones count."""
        s1, s2, s3 = _uuid(1), _uuid(2), _uuid(3)
        user = {s1: 2, s2: None, s3: -2}
        cand = {s1: 2, s2: 1, s3: -2}
        weights = {s1: 1, s2: 1, s3: 1}
        # Only s1 and s3 count. distance=0+0=0, weight=4*2=8
        assert compute_affinity(user, cand, weights) == 100.0

    def test_candidate_missing_positions(self):
        """Candidate doesn't have position for some statements — skip those."""
        s1, s2, s3 = _uuid(1), _uuid(2), _uuid(3)
        user = {s1: 2, s2: 1, s3: -1}
        cand = {s1: 2}  # Only has position for s1
        weights = {s1: 1, s2: 1, s3: 1}
        # Only s1 counts: dist=0, weight=4*1=4
        assert compute_affinity(user, cand, weights) == 100.0

    def test_single_statement_weight_1(self):
        """Single statement, weight 1."""
        s = _uuid(1)
        user = {s: 2}
        cand = {s: 0}
        weights = {s: 1}
        # dist=2, weight=4*1=4, affinity=(1-2/4)*100=50.0
        assert compute_affinity(user, cand, weights) == 50.0

    def test_single_statement_weight_3(self):
        """Single statement, weight 3 — weight scales distance and total."""
        s = _uuid(1)
        user = {s: 2}
        cand = {s: 0}
        weights = {s: 3}
        # dist=2*3=6, weight=4*3=12, affinity=(1-6/12)*100=50.0
        assert compute_affinity(user, cand, weights) == 50.0

    def test_empty_answers(self):
        """Empty answers dict → 0.0%."""
        cand = {_uuid(1): 1}
        weights = {_uuid(1): 1}
        assert compute_affinity({}, cand, weights) == 0.0

    def test_weights_affect_result(self):
        """Different weights for same distances produce different results."""
        s1, s2 = _uuid(1), _uuid(2)
        user = {s1: 2, s2: 2}
        cand = {s1: 0, s2: 0}

        # Equal weights: dist=2*1+2*1=4, total=4*2=8, aff=50.0
        assert compute_affinity(user, cand, {s1: 1, s2: 1}) == 50.0

        # Heavy weight on s1: dist=2*3+2*1=8, total=4*3+4*1=16, aff=(1-8/16)*100=50.0
        # Still 50% because distances are same — let's make distances different
        cand2 = {s1: 1, s2: -2}
        # w=1,1: dist=|2-1|*1+|2-(-2)|*1=1+4=5, total=4+4=8, aff=(1-5/8)*100=37.5
        assert compute_affinity(user, cand2, {s1: 1, s2: 1}) == 37.5

        # w=3,1: dist=|2-1|*3+|2-(-2)|*1=3+4=7, total=12+4=16, aff=(1-7/16)*100=56.2
        assert compute_affinity(user, cand2, {s1: 3, s2: 1}) == 56.2

    def test_cross_validation_fixtures(self):
        """Fixtures that can be shared with TypeScript tests for bit-exact comparison."""
        # Case 1: Balanced scenario
        s1, s2, s3 = _uuid(1), _uuid(2), _uuid(3)
        user = {s1: 1, s2: -1, s3: 2}
        cand = {s1: 2, s2: -2, s3: 0}
        weights = {s1: 2, s2: 1, s3: 3}
        # dist=|1-2|*2+|-1-(-2)|*1+|2-0|*3=2+1+6=9
        # total=4*2+4*1+4*3=8+4+12=24
        # aff=(1-9/24)*100=62.5
        assert compute_affinity(user, cand, weights) == 62.5

        # Case 2: Near-match
        user2 = {s1: 2, s2: -2, s3: 1}
        cand2 = {s1: 2, s2: -1, s3: 1}
        # dist=0+|(-2)-(-1)|*1+0=1
        # total=8+4+12=24
        # aff=(1-1/24)*100=95.8333...→95.8
        assert compute_affinity(user2, cand2, weights) == 95.8
