"""W6 (right-angle): turned axes, bevel and crossed meshes, planned (docs/notes-workbook/W6-PLAN.md §2, §5).

The two fixtures of W6-PLAN §5 are written here as specs (E commits them as Excel saved them); every number pinned
is recomputed from the kinds' own code (gears/bevel.py, crossed.py) and agrees with the plan's.
"""

import math
from fractions import Fraction

import pytest

from gear_generator.gears import crossed, pair
from gear_generator.workbook import geometry, kinematics
from gear_generator.workbook.model import Box, Gear, GearboxSpec, Mesh, Shaft


def bevel_reducer():
    """Fixture A, W6-PLAN §5.1: a bevel stage (S1 along X+ into S2 along Z+) feeding a parallel stage."""
    return GearboxSpec(
        box=Box(name="Bevel_Reducer", pressure_angle="20", efficiency="98"),
        shafts=(Shaft("S1", "frame", "0", "0", "60", "X+", "input", "", "1500", "10"),
                Shaft("S2", "frame", "0", "0", "0", "Z+", ""),
                Shaft("S3", "frame", "-68", "0", "0", "Z+", "output")),
        gears=(Gear("G1", "S1", "0", "bevel", "external", "20", "3", "", "20", "10"),
               Gear("G2", "S2", "60", "bevel", "external", "40", "3", "", "20", "10"),
               Gear("G3", "S2", "5", "spur", "external", "17", "2", "", "10", "8"),
               Gear("G4", "S3", "5", "spur", "external", "51", "2", "", "10", "8")),
        meshes=(Mesh("G1", "G2"), Mesh("G3", "G4")))


def crossed_slant():
    """Fixture B, W6-PLAN §5.2: a crossed helical stage, then a bevel stage at 120° onto a slanted shaft."""
    helix = dict(helix_angle="45", hand="right")
    return GearboxSpec(
        box=Box(name="Crossed_Slant", pressure_angle="20", efficiency="98"),
        shafts=(Shaft("S1", "frame", "0", "0", "0", "Z+", "input", "", "1000", "5"),
                Shaft("S2", "frame", "0", "84.852814", "8", "X+", ""),
                Shaft("S3", "frame", "-110", "84.852814", "8", "-1, 1.732050807569, 0", "output")),
        gears=(Gear("G1", "S1", "10", "helical", "external", "20", "2", "", "16", "6", **helix),
               Gear("G2", "S2", "0", "helical", "external", "40", "2", "", "16", "8", **helix),
               Gear("G3", "S2", "-110", "bevel", "external", "20", "2.5", "", "10", "8"),
               Gear("G4", "S3", "0", "bevel", "external", "30", "2.5", "", "10", "8")),
        meshes=(Mesh("G1", "G2"), Mesh("G3", "G4")))


def laid(spec):
    placed = geometry.layout(spec).placed
    meshes = {(m.a, m.b): geometry.mesh_geometry(placed[m.a], placed[m.b]) for m in spec.meshes}
    return placed, meshes


# -- placement, cuts and the meshes' geometry ------------------------------------------------------------------


def test_fixture_a_places_the_bevel_pair_apex_to_apex_and_cuts_each_for_the_other():
    cuts = geometry.bevel_cuts(bevel_reducer())
    assert cuts == {"G1": geometry.BevelCut(40, 90.0, ("G2",)), "G2": geometry.BevelCut(20, 90.0, ("G1",))}
    placed, meshes = laid(bevel_reducer())
    assert placed["G1"].centre == (0.0, 0.0, 60.0) == placed["G2"].centre and placed["G1"].axis == (1.0, 0.0, 0.0)
    assert placed["G1"].derived.delta == pytest.approx(26.565051, abs=1e-6)
    assert placed["G2"].derived.delta == pytest.approx(63.434949, abs=1e-6)
    assert placed["G1"].derived.cone_distance == pytest.approx(67.082039, abs=1e-6)
    assert placed["G1"].derived.da == pytest.approx(67.218027, abs=1e-6)
    assert placed["G2"].derived.da == pytest.approx(121.757549, abs=1e-6)
    bevel, spur = meshes[("G1", "G2")], meshes[("G3", "G4")]
    assert (bevel.kind, bevel.sense, bevel.shaft_angle, bevel.placed) == (geometry.BEVEL, 1, 90.0, 0.0)
    assert bevel.contact == pytest.approx((60.0, 0.0, 90.0))                 # the heel pitch point, from either gear
    assert (spur.kind, spur.sense, spur.placed) == (geometry.PARALLEL, 1, 68.0)


def test_fixture_b_measures_its_crossed_pair_on_the_common_perpendicular_and_its_bevel_pair_at_120():
    cuts = geometry.bevel_cuts(crossed_slant())
    assert cuts["G3"].mate_teeth == 30 and cuts["G4"].mate_teeth == 20
    assert cuts["G3"].shaft_angle == pytest.approx(120.0, abs=1e-9)
    placed, meshes = laid(crossed_slant())
    assert placed["G3"].derived.delta == pytest.approx(40.893395, abs=1e-6)
    assert placed["G4"].derived.delta == pytest.approx(79.106605, abs=1e-6)
    assert placed["G3"].derived.cone_distance == pytest.approx(38.188131, abs=1e-6)
    assert placed["G3"].centre == pytest.approx(placed["G4"].centre)
    cross = meshes[("G1", "G2")]
    assert (cross.kind, cross.sense, cross.shaft_angle) == (geometry.CROSSED, -1, 90.0)
    assert cross.needed == pytest.approx(84.852814, abs=1e-6) and cross.placed == pytest.approx(84.852814)
    assert cross.contact == pytest.approx((0.0, 28.284271, 8.0), abs=1e-6)
    assert meshes[("G3", "G4")].kind == geometry.BEVEL and meshes[("G3", "G4")].shaft_angle == pytest.approx(120.0)


@pytest.mark.parametrize("make, gaps", [
    (bevel_reducer, {("G1", "G3"): 27.37, ("G1", "G4"): 58.27}),
    (crossed_slant, {("G1", "G3"): 66.18, ("G1", "G4"): 103.38, ("G2", "G4"): 71.44}),
])
def test_the_true_cylinder_clearances_are_the_plans_to_a_tenth(make, gaps):
    placed, _ = laid(make())
    for (a, b), gap in gaps.items():
        assert geometry.cylinder_gap(placed[a], placed[b]) == pytest.approx(gap, abs=0.1), (a, b)


@pytest.mark.parametrize("make, spans", [
    (bevel_reducer, {("S1", "G3"): 54.59, ("S1", "G4"): 75.01, ("S3", "G1"): 110.15, ("S3", "G2"): 70.33}),
    (crossed_slant, {("S1", "G2"): 26.28, ("S1", "G3"): 96.47, ("S1", "G4"): 133.66, ("S2", "G1"): 54.57,
                     ("S3", "G1"): 112.65, ("S3", "G2"): 104.17}),
])
def test_a_shaft_is_the_span_of_its_gears(make, spans):
    placed, _ = laid(make())
    for (shaft, gear), gap in spans.items():
        span = geometry.shaft_span(placed, shaft)
        assert geometry.solid_gap(span, geometry.bounding_cylinder(placed[gear])) == pytest.approx(gap, abs=0.1)


def test_cylinder_gap_agrees_with_dense_sampling():
    placed, _ = laid(crossed_slant())
    a, b = geometry.bounding_cylinder(placed["G1"]), geometry.bounding_cylinder(placed["G4"])

    def samples(c, n=36, m=8):
        axis = [e - s for s, e in zip(c.start, c.end)]
        length = math.sqrt(sum(v * v for v in axis))
        u = [v / length for v in axis]
        seed = [1.0, 0.0, 0.0] if abs(u[0]) < 0.9 else [0.0, 1.0, 0.0]
        dot = sum(x * y for x, y in zip(seed, u))
        p = [x - dot * y for x, y in zip(seed, u)]
        np_ = math.sqrt(sum(v * v for v in p))
        p = [v / np_ for v in p]
        q = [u[1] * p[2] - u[2] * p[1], u[2] * p[0] - u[0] * p[2], u[0] * p[1] - u[1] * p[0]]
        for i in range(m + 1):
            t = length * i / m
            for j in range(n):
                ang = 2 * math.pi * j / n
                for r in (c.radius,):
                    yield [c.start[k] + u[k] * t + r * (math.cos(ang) * p[k] + math.sin(ang) * q[k]) for k in range(3)]
    sampled = min(math.dist(x, y) for x in samples(a) for y in samples(b))
    assert geometry.solid_gap(a, b) <= sampled + 1e-9 and sampled - geometry.solid_gap(a, b) < 1.0


# -- phases ---------------------------------------------------------------------------------------------------


def test_a_bevel_pinion_at_its_built_phase_puts_its_partner_at_the_pairs_mate_angle():
    placed, meshes = laid(bevel_reducer())
    theta = geometry.phases(bevel_reducer(), placed, meshes_=meshes)
    pitch = 360.0 / 40
    off = (math.degrees(theta["G2"]) - pair.mate_angle(40)) % pitch
    assert min(off, pitch - off) < 1e-9


def test_a_crossed_pair_laid_as_crossed_placement_lays_it_takes_its_spin():
    helix = dict(helix_angle="45", hand="right")
    alone = GearboxSpec(box=Box(name="T"), shafts=(Shaft("S1", "frame", "0", "0", "0", "Z+"),),
                        gears=(Gear("G1", "S1", "8", "helical", "external", "20", "2", "", "16", "6", **helix),
                               Gear("G2", "S1", "8", "helical", "external", "40", "2", "", "16", "8", **helix)))
    p0 = geometry.layout(alone).placed
    built = crossed.placement(p0["G1"].derived, p0["G2"].derived, 90.0)
    spec = GearboxSpec(box=Box(name="T"), shafts=(
        Shaft("S1", "frame", "0", "0", "0", "Z+", "input", "", "100"),
        Shaft("S2", "frame", repr(built.centre_distance), "0", repr(built.contact[2]), "Y+")),
        gears=(Gear("G1", "S1", "8", "helical", "external", "20", "2", "", "16", "6", **helix),
               Gear("G2", "S2", "0", "helical", "external", "40", "2", "", "16", "8", **helix)),
        meshes=(Mesh("G1", "G2"),))
    placed, meshes = laid(spec)
    theta = geometry.phases(spec, placed, meshes_=meshes)
    assert placed["G2"].origin == pytest.approx(built.origin)
    pitch = 360.0 / 40
    off = (math.degrees(theta["G2"]) - built.spin) % pitch
    assert min(off, pitch - off) < 1e-9


def test_turning_the_pinion_one_tooth_turns_its_turned_partner_one_tooth():
    placed, meshes = laid(crossed_slant())
    m = meshes[("G3", "G4")]
    one = geometry.turned_against(placed["G3"], 0.0, placed["G4"], m)
    two = geometry.turned_against(placed["G3"], 2 * math.pi / 20, placed["G4"], m)
    step = 2 * math.pi / 30
    off = (two - one) % step
    assert min(off, step - off) < 1e-9


# -- speeds about each shaft's own axis (D7) ------------------------------------------------------------------


def test_fixture_a_speeds_and_torques_are_the_plans():
    spec = bevel_reducer()
    _, meshes = laid(spec)
    motion = kinematics.solve(spec, senses={k: v.sense for k, v in meshes.items()})
    assert motion.speeds == {"S1": 1500, "S2": -750, "S3": 250}
    assert motion.torques == pytest.approx({"S1": 10.0, "S2": 19.6, "S3": 57.624})
    assert motion.seen_from == {"S1": "+X", "S2": "+Z", "S3": "+Z"}
    assert [motion.turns(s) for s in ("S1", "S2", "S3")] == ["anticlockwise", "clockwise", "anticlockwise"]


def test_fixture_b_speeds_torques_and_the_slants_plus_end_are_the_plans():
    spec = crossed_slant()
    _, meshes = laid(spec)
    motion = kinematics.solve(spec, senses={k: v.sense for k, v in meshes.items()})
    assert motion.speeds == {"S1": 1000, "S2": 500, "S3": Fraction(-1000, 3)}
    assert motion.torques == pytest.approx({"S1": 5.0, "S2": 9.8, "S3": 14.406})
    assert motion.seen_from["S3"] == "(0.5, −0.866, 0)"
    assert [motion.turns(s) for s in ("S1", "S2", "S3")] == ["anticlockwise"] * 3


def test_without_senses_a_mesh_across_an_angle_is_left_out_and_parallel_speeds_are_w3s():
    from test_workbook_model import reducer
    assert kinematics.solve(reducer()).speeds == {"S1": 1500, "S2": -375, "S3": 125}
    motion = kinematics.solve(bevel_reducer())
    assert motion.speeds == {"S1": 1500} and set(motion.free) == {"S2", "S3"}
