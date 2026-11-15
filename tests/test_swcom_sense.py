"""W6's read-back of a gear mate's sense, ``swcom.sense_reading`` (rule H, W6-PLAN §2.6).

Written at W6's interface commit: package A's ``Session.gear_mate_sense`` and the fake both rest on it. The proof
that H is W5's rule on parallel axes runs over every parallel case the probes recorded
(``findings.GEAR_MATE_FLIP_NEEDED_*`` and ``GEAR_MATE_FLIP_NEEDED_MORE_*``, both versions), every Reverse, every
entity sense and both entity orders.
"""

import itertools
import math
import re

import pytest

from gear_generator import findings
from gear_generator.swcom import SolidWorksError, sense_reading

CASE_TABLES = ("GEAR_MATE_FLIP_NEEDED_ON_2026", "GEAR_MATE_FLIP_NEEDED_ON_2024", "GEAR_MATE_FLIP_NEEDED_MORE_ON_2026",
               "GEAR_MATE_FLIP_NEEDED_MORE_ON_2024")
FACINGS = ((1, 1), (1, -1), (-1, 1), (-1, -1))


def recorded_cases():
    """(table, case, internal, (σ pinion, σ partner)) for every recorded case: a ring or the plain annulus is
    inside, anything else outside; the shaft senses are the case's own ``++`` / ``+-`` …, or every facing when the
    case does not say (the plain annulus)."""
    out = []
    for table in CASE_TABLES:
        cases = getattr(findings, table, None)
        assert cases, f"findings.{table} is gone: the proof below has nothing to run on"
        for name in cases:
            internal = "ring" in name or "annulus" in name
            match = re.search(r"([+-])([+-])$", name)
            facings = [tuple(1 if c == "+" else -1 for c in match.groups())] if match else list(FACINGS)
            for facing in facings:
                out.append((table, name, internal, facing))
    return out


def w5_rule(reverse, directions, internal):
    """``findings.GEAR_MATE_SENSE_READ_BACK``: ``(Reverse == entities parallel) == internal``."""
    parallel = sum(p * q for p, q in zip(*directions)) > 0
    return (reverse == parallel) == internal


def k_positive(internal, sigma_a, sigma_b):
    """``k = −c·za/zb`` with ``c = a·a`` outside and ``−a·a`` inside a ring (W6-PLAN §2.4)."""
    c = (-1 if internal else 1) * sigma_a * sigma_b
    return -c > 0


@pytest.mark.parametrize("table, name, internal, facing", recorded_cases(),
                         ids=lambda v: v if isinstance(v, str) else repr(v))
def test_h_is_w5s_rule_on_every_recorded_parallel_case_in_either_entity_order(table, name, internal, facing):
    sigma_a, sigma_b = facing
    axes = ((0.0, 0.0, float(sigma_a)), (0.0, 0.0, float(sigma_b)))
    for reverse, tau_a, tau_b, swapped in itertools.product((True, False), (1, -1), (1, -1), (False, True)):
        d_a = tuple(tau_a * v for v in axes[0])
        d_b = tuple(tau_b * v for v in axes[1])
        directions = (d_b, d_a) if swapped else (d_a, d_b)
        right, taus = sense_reading(reverse, directions, axes, k_positive(internal, sigma_a, sigma_b))
        assert right == w5_rule(reverse, (d_a, d_b), internal), (reverse, tau_a, tau_b, swapped)
        if sigma_a == sigma_b or not swapped:
            # On parallel axes either pairing is valid and the first is taken: τa·τb is the same either way.
            assert taus[0] * taus[1] == tau_a * tau_b


def test_every_recorded_case_is_read():
    cases = recorded_cases()
    assert len({(t, n) for t, n, _, _ in cases}) == sum(len(getattr(findings, t)) for t in CASE_TABLES)
    assert any(internal for _, _, internal, _ in cases) and any(not internal for _, _, internal, _ in cases)


@pytest.mark.parametrize("direction", [(1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.6, 0.0, 0.8),
                                       (-0.5, 0.8660254037844386, 0.0)])
@pytest.mark.parametrize("internal", [False, True])
def test_h_is_w5s_rule_on_parallel_axes_in_any_family(direction, internal):
    for sigma_a, sigma_b in FACINGS:
        axes = (tuple(sigma_a * v for v in direction), tuple(sigma_b * v for v in direction))
        for reverse, tau_a, tau_b, swapped in itertools.product((True, False), (1, -1), (1, -1), (False, True)):
            d_a, d_b = (tuple(tau_a * v for v in axes[0]), tuple(tau_b * v for v in axes[1]))
            directions = (d_b, d_a) if swapped else (d_a, d_b)
            right, _ = sense_reading(reverse, directions, axes, k_positive(internal, sigma_a, sigma_b))
            assert right == w5_rule(reverse, (d_a, d_b), internal)


def turned(degrees):
    return (math.sin(math.radians(degrees)), 0.0, math.cos(math.radians(degrees)))


@pytest.mark.parametrize("angle", [30, 60, 90, 120, 150])
def test_on_axes_at_an_angle_each_entity_is_matched_to_its_gear_whatever_the_order(angle):
    """H: Reverse is True exactly when the mate turns its gears the same way about its entities' own directions."""
    axes = ((0.0, 0.0, 1.0), turned(angle))
    for reverse, tau_a, tau_b, same_sense in itertools.product((True, False), (1, -1), (1, -1), (True, False)):
        d_a, d_b = tuple(tau_a * v for v in axes[0]), tuple(tau_b * v for v in axes[1])
        expected = reverse == ((1 if same_sense else -1) * tau_a * tau_b > 0)
        assert sense_reading(reverse, (d_a, d_b), axes, same_sense) == (expected, (tau_a, tau_b))
        assert sense_reading(reverse, (d_b, d_a), axes, same_sense) == (expected, (tau_a, tau_b))


def test_a_bevel_pair_at_right_angles_reads_right_when_reverse_says_its_gears_turn_opposite_ways():
    """Fixture A's bevel mesh: G1 on X+, G2 on Z+, c = +1 so k = −0.5 (opposite turns about the own axes); with
    both entities along their gears, the mate is right exactly when Reverse is False."""
    axes = ((1.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    assert sense_reading(False, axes, axes, False) == (True, (1, 1))
    assert sense_reading(True, axes, axes, False) == (False, (1, 1))
    assert sense_reading(True, ((0.0, 0.0, 1.0), (-1.0, 0.0, 0.0)), axes, False) == (True, (-1, 1))


@pytest.mark.parametrize("directions, words", [
    (((0.0, 0.0, 1.0), (0.0, 1.0, 0.0)), "as pointing (0, 1, 0), which is not along either gear's axis "
                                         "((1, 0, 0) or (0, 0, 1))"),
    (((0.0, 0.0, 1.0), (0.0, 0.0, -2.0)), "as pointing (0, 0, 1) and (0, 0, -1), both along one gear's axis"),
    (((1.0, 0.0, 0.0), (0.0, 0.2, 0.98)), "as pointing (0, 0.2, 0.98), which is not along either"),
])
def test_entities_not_one_along_each_gear_are_refused_with_a_sentence(directions, words):
    axes = ((1.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    with pytest.raises(SolidWorksError) as raised:
        sense_reading(True, directions, axes, False, mate="G1 meshes G2 in R.SLDASM")
    text = str(raised.value)
    assert text.startswith("SolidWorks reads the axes of the gear mate G1 meshes G2 in R.SLDASM ") and words in text
    assert text.endswith("so the mate does not hold the axes the gears were placed on, and nothing is guessed.")


@pytest.mark.parametrize("reverse, directions, axes, words", [
    (None, ((0, 0, 1.0), (0, 0, 1.0)), ((0, 0, 1.0), (0, 0, 1.0)), "which is not yes or no"),
    (True, ((0, 0, 1.0),), ((0, 0, 1.0), (0, 0, 1.0)), "did not say how it holds its two gear axes"),
    (True, ((0, 0, 0.0), (0, 0, 1.0)), ((0, 0, 1.0), (0, 0, 1.0)), "holds a gear axis with no direction"),
    (True, ((0, 0, 1.0), (0, 0, 1.0)), ((0, 0, 1.0), (0, 0, float("nan"))), "was placed with no axis"),
])
def test_a_reading_that_cannot_be_judged_is_refused_with_a_sentence(reverse, directions, axes, words):
    with pytest.raises(SolidWorksError, match=re.escape(words)):
        sense_reading(reverse, directions, axes, True)
