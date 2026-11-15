"""The pure parts of probe tier 10's planetary put-back (W7's follow-up), without SolidWorks."""

import math

from gear_generator.probe import __main__ as probe_main
from gear_generator.probe import harness
from gear_generator.probe import p10_planetary as p10


def _rot(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [c, -s, 0.0, s, c, 0.0, 0.0, 0.0, 1.0]


RECORD = {"gearbox": {
    "components": [{"gear": "Sun", "name": "Sun-1", "rotation": _rot(0), "at": [0.0, 0.0, 5.0]},
                   {"gear": "Planet copy 1", "name": "Planet-1", "rotation": _rot(10), "at": [18.0, 0.0, 5.0]},
                   {"gear": "Ring", "name": "Ring-1", "rotation": _rot(0), "at": [0.0, 0.0, 5.0]}],
    "carriers": [{"shaft": "C", "component": "Carrier-1", "rotation": _rot(0), "at": [0.0, 0.0, 0.0]}],
    "mates": [{"name": "Sun meshes Planet copy 1", "kind": "mesh", "gears": ["Sun", "Planet copy 1"], "sense": 1},
              {"name": "CarrierGear locked to C carrier", "kind": "lock", "gears": ["C carrier", "CarrierGear"]}],
    "fixed": ["Ring"], "layout_component": "Layout-1"}}


def test_the_probe_is_registered_in_tier_10():
    probe_main.load_probes()
    found = [p for p in harness.REGISTRY if p.name == "planetary_put_back"]
    assert len(found) == 1 and found[0].tier == 10


def test_wanted_frames_come_from_the_record_and_move_the_copies_along_their_own_axis():
    built = p10.wanted_frames(RECORD)
    assert set(built) == {"Sun", "Planet copy 1", "Ring", "C carrier"}
    moved = p10.wanted_frames(RECORD, 2.0)
    assert moved["Planet copy 1"][1] == [18.0, 0.0, 7.0] and moved["Sun"][1] == [0.0, 0.0, 5.0]
    assert p10.component_names(RECORD)["C carrier"] == "Carrier-1"


def test_frames_are_judged_as_place_component_judges_a_put():
    a = (_rot(0), [0.0, 0.0, 5.0])
    assert p10.frame_off(a, a) == (0.0, 0.0)
    rot, at = p10.frame_off((_rot(6.2), [0.0, 0.0, 5.0]), a)
    assert abs(rot - 0.108) < 1e-3 and at == 0.0          # p3's 6.2° read "rotation off 1.1e-01"
    assert abs(p10.own_turn_deg(_rot(0), _rot(9.25)) - 9.25) < 1e-9


def test_a_drive_is_right_only_when_every_body_turns_as_the_ratios_say():
    good = {"Sun": 20.0, "C carrier": 5.0, "CarrierGear": 5.0, "Ring": 0.0,
            "Planet copy 1": -10.0, "Planet copy 2": -10.0, "Planet copy 3": -10.0}
    assert all(p10.drive_right(good, 20.0).values())
    assert not p10.drive_right(dict(good, **{"C carrier": 0.0}), 20.0)["C carrier"]


def test_a_route_holds_only_with_frames_senses_clearance_and_a_right_drive():
    case = {"frames_off": {"Sun": (0.0, 0.0)}, "senses": {"m": {"right": True}}, "clashes": [],
            "drive": {"right": {"Sun": True}, "clashes": []}, "errors": []}
    assert p10.judge(case)["held"]
    assert not p10.judge(dict(case, drive={"right": {"Sun": False}, "clashes": []}))["held"]
    assert not p10.judge(dict(case, frames_off={"Sun": (0.1, 0.0)}))["held"]
    assert not p10.judge(dict(case, errors=["x"]))["held"]
    assert p10.route_held({"C": case}, "C") and not p10.route_held({}, "C")


def test_a_recorded_mesh_turns_its_gears_the_same_way_when_its_sense_is_minus_one():
    assert p10.same_way({"sense": -1}) and not p10.same_way({"sense": 1}) and not p10.same_way({"sense": 0})
