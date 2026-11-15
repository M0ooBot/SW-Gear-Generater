"""Probe tier 9's pure part (W6-PLAN §7.2): geometry, the rule H, the virtual crossed pair, the judgement."""

import math

import pytest

from gear_generator import findings
from gear_generator.probe import __main__ as probe_main
from gear_generator.probe import decide, harness
from gear_generator.probe import p9_turned as p9


def test_the_case_table_is_section_7_2s():
    turned = sum(len(f) * 2 for c, _s, _side, f in p9.GEOMETRIES if c != "P")
    controls = sum(len(f) * 2 for c, _s, _side, f in p9.GEOMETRIES if c == "P")
    assert (turned, controls) == (40, 4)
    assert len([g for g in p9.GEOMETRIES for _f in g[3]]) == 22


def test_the_probe_is_registered_as_tier_nine():
    probe_main.load_probes()
    found = [p for p in harness.REGISTRY if p.name == "turned_gear_mate_sense"]
    assert len(found) == 1 and found[0].tier == 9


def test_each_cylinder_stands_on_its_own_plus_z_side_along_its_frame_axis():
    for cls, sigma_f, side, facings in p9.GEOMETRIES:
        geo = p9.lines(cls, sigma_f, side)
        for facing in facings:
            placed = p9.frames(cls, sigma_f, side, facing)
            for key, (point, direction), sigma, distance in (("A", geo["a"], facing[0], p9.FROM_A),
                                                             ("B", geo["b"], facing[1], p9.FROM_B)):
                m, at = placed[key]
                g = p9.own_axis(m)
                assert p9._dot(g, direction) == pytest.approx(sigma)
                foot = geo["foot_a" if key == "A" else "foot_b"]
                assert at == pytest.approx(p9._add(foot, p9._scale(g, distance)))
            angle = p9.own_angle(p9.own_axis(placed["A"][0]), p9.own_axis(placed["B"][0]))
            assert angle == pytest.approx(sigma_f if facing[0] * facing[1] > 0 else 180.0 - sigma_f)


def test_entities_are_matched_by_axis_never_by_order():
    ga, gb = (0.0, 0.0, 1.0), (math.sin(math.radians(30)), 0.0, math.cos(math.radians(30)))
    m = p9.match_entities([p9._scale(gb, -1.0), ga], (ga, gb))
    assert m["tau"] == (1, -1) and m["first_is_a"] is False
    with pytest.raises(ValueError):
        p9.match_entities([ga, ga], (ga, gb))
    assert p9.h_says(True, (1, -1)) == -1 and p9.h_says(False, (1, 1)) == -1 and p9.h_says(True, (-1, -1)) == 1


def test_the_virtual_crossed_pair_takes_the_hand_of_the_crossing():
    b60 = (math.sin(math.radians(60)), 0.0, math.cos(math.radians(60)))
    plus = p9.skew_right((0.0, 0.0, 1.0), b60, (0.0, 1.0, 0.0), b60)
    minus = p9.skew_right((0.0, 0.0, 1.0), b60, (0.0, -1.0, 0.0), b60)
    assert {plus["hand"], minus["hand"]} == {"left", "right"} and plus["sigma_l"] == pytest.approx(60.0)
    b90 = (1.0, 0.0, 0.0)
    assert p9.skew_right((0.0, 0.0, 1.0), b90, (0.0, 1.0, 0.0), b90)["hand"] == "right"   # either fits; right taken
    # A gear facing the other way turns the other way: the sense flips with one facing.
    flipped = p9.skew_right((0.0, 0.0, 1.0), p9._scale(b60, -1.0), (0.0, 1.0, 0.0), b60)
    assert flipped["m"] == -plus["m"]


def test_right_is_opposite_for_meeting_and_w5s_for_the_controls():
    z = (0.0, 0.0, 1.0)
    assert p9.right_m("M", z, (1.0, 0.0, 0.0), None, (1.0, 0.0, 0.0)) == -1
    assert p9.right_m("P", z, z, None, z) == -1 and p9.right_m("P", z, (0.0, 0.0, -1.0), None, z) == 1
    # W5's rule on the parallel pair: right exactly when Reverse differs from "the entities point the same way".
    assert p9.w5_says_right(False, [z, z]) is True and p9.w5_says_right(True, [z, z]) is False


def _consistent_cases(break_one: bool = False):
    """Every case as H would have it, with the drive agreeing."""
    cases = []
    for cls, sigma_f, side, facings in p9.GEOMETRIES:
        geo = p9.lines(cls, sigma_f, side)
        for facing in facings:
            placed = p9.frames(cls, sigma_f, side, facing)
            ga, gb = p9.own_axis(placed["A"][0]), p9.own_axis(placed["B"][0])
            want = p9.right_m(cls, ga, gb, geo["e"], geo["b"][1])
            for flip in (False, True):
                directions = [ga, gb]
                tau = (1, 1)
                # Flip False turns right here; Reverse is what H needs for each Flip's sense.
                m = want if not flip else -want
                reverse = (m * tau[0] * tau[1]) > 0
                case = {"cls": cls, "sigma_f": sigma_f, "side": side, "geometry": p9.geometry_name(cls, sigma_f, side),
                        "facing": list(facing), "flip": flip, "status": findings.ADD_MATE_NO_ERROR, "reverse": reverse,
                        "directions": directions, "tau": list(tau), "own_angle": p9.own_angle(ga, gb),
                        "moved_on_make": False, "delta_a": 30.0, "delta_b": 15.0 * m, "right_m": want}
                cases.append(case)
    if break_one:
        cases[0]["reverse"] = not cases[0]["reverse"]
    return cases


def test_the_verdict_holds_only_when_h_tells_every_case():
    cases = _consistent_cases()
    verdict = p9.read_back_verdict(cases, [])
    assert verdict["value"] == "entity senses", verdict["problems"][:3]
    assert p9.angles_verdict(cases, verdict["value"]) == (30.0, 150.0)
    broken = p9.read_back_verdict(_consistent_cases(break_one=True), [])
    assert broken["value"] != "entity senses" and broken["problems"]
    assert p9.angles_verdict(cases, None) is None


def test_decide_reads_the_verdict_off_a_pass_only():
    cases = _consistent_cases()
    records = {"turned_gear_mate_sense": {"status": "pass", "facts": {
        "turned_sense_cases": cases, "turned_sense_reopened": [], "turned_gear_mate_moves_on_make": False,
        "gear_mate_entity_order": "first selection first"}}}
    decided = decide.decide(records)
    assert decided["turned_sense_read_back"] == "entity senses" and decided["turned_sense_angles"] == (30.0, 150.0)
    records["turned_gear_mate_sense"]["status"] = "fail"
    decided = decide.decide(records)
    assert decided["turned_sense_read_back"] is None and decided["turned_sense_angles"] is None


def test_parallel_entities_are_paired_by_order_since_either_pairing_gives_one_product():
    z, mz = (0.0, 0.0, 1.0), (0.0, 0.0, -1.0)
    m = p9.match_entities([z, mz], (z, mz))
    assert m["parallel"] and m["tau"][0] * m["tau"][1] == 1
    assert p9.match_entities([mz, z], (z, mz))["tau"][0] * p9.match_entities([mz, z], (z, mz))["tau"][1] == 1
    # A case recorded without τ is matched again from its directions and axes.
    case = {"reverse": False, "directions": [z, z], "own_axes": [z, z], "delta_a": 30.0, "delta_b": -15.0,
            "right_m": -1}
    assert p9.judge(case)["m_h"] == -1 and p9.judge(case)["h_tells"]
