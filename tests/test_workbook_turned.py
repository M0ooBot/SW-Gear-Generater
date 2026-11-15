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


# -- the Checks panel, the header and the turned refusal (W6-PLAN §2.5, §2.6, §2.9, §5; INTERFACES §7.12) -----

from gear_generator import findings  # noqa: E402
from gear_generator.workbook import assess, checks, model, motion, xlsx  # noqa: E402
from gear_generator.workbook.model import replace  # noqa: E402
from test_workbook_model import write  # noqa: E402


def assessed(tmp_path, spec, name="W.xlsx"):
    read, diagnostics = model.from_book(xlsx.read(write(tmp_path, spec, name)))
    return assess.assess(read, diagnostics, "C:\\Out\\")


@pytest.fixture
def turned_findings(monkeypatch):
    monkeypatch.setattr(findings, "TURNED_GEAR_MATE_SENSE_READ_BACK", "entity senses", raising=False)
    monkeypatch.setattr(findings, "TURNED_GEAR_MATE_SENSE_ANGLES", (30.0, 150.0), raising=False)
    monkeypatch.setattr(findings, "TURNED_GEAR_MATE_SENSE_ANGLES_SKEW", (60.0, 120.0), raising=False)


def test_fixture_as_checks_panel_is_the_strips_own_three_warnings(tmp_path, turned_findings):
    a = assessed(tmp_path, bevel_reducer())
    assert [d.message for d in a.diagnostics] == [
        "Gears!F2: G1: The tooth tip is 0.722 mm thick, under 0.3 × module (0.9 mm).",
        "Gears!Q2: G1: The involute starts at 65.444 mm, above the form diameter of 63.267 mm, so the bottom of the "
        "working flank is a straight line.",
        "Gears!Q5: G4: The involute starts at 99.28 mm, above the form diameter of 98.614 mm, so the bottom of the "
        "working flank is a straight line."]
    assert a.report.worked_out_as == "Bevel and parallel train · 2 meshes · 6.000 : 1 · output at 90° to the input"
    assert a.lay_out_refusal() == ""


def test_fixture_bs_checks_panel_is_the_strips_own_six_warnings(tmp_path, turned_findings):
    a = assessed(tmp_path, crossed_slant())
    flank = "above the form diameter of {} mm, so the bottom of the working flank is a straight line."
    assert [d.message for d in a.diagnostics] == [
        "Gears!Q2: G1: The involute starts at 53.849 mm, " + flank.format("53.14"),
        "Gears!L2: G1: A helix angle of 45° is outside the usual 8–30° for a helical gear.",
        "Gears!Q3: G2: The involute starts at 110.417 mm, " + flank.format("109.413"),
        "Gears!L3: G2: A helix angle of 45° is outside the usual 8–30° for a helical gear.",
        "Gears!F4: G3: The tooth tip is 0.664 mm thick, under 0.3 × module (0.75 mm).",
        "Gears!Q4: G3: The involute starts at 64.97 mm, " + flank.format("62.668")]
    assert all(d.level == "warning" for d in a.diagnostics)
    assert a.report.worked_out_as == "Crossed and bevel train · 2 meshes · 3.000 : 1 · output at 90° to the input"
    assert a.lay_out_refusal() == ""


def test_a_turned_mesh_waits_for_the_read_back_finding_and_its_classs_range(tmp_path, turned_findings, monkeypatch):
    a, b = assessed(tmp_path, bevel_reducer(), "A.xlsx"), assessed(tmp_path, crossed_slant(), "B.xlsx")
    monkeypatch.setattr(findings, "TURNED_GEAR_MATE_SENSE_READ_BACK", None)
    assert motion.turned_refusal(a.report) == (
        "G1 and G2 mesh across shafts at 90°, and which way a gear mate turns gears on shafts at an angle is not "
        "settled by the probes for this version (findings.TURNED_GEAR_MATE_SENSE_READ_BACK), so the gearbox is not "
        "built.")
    assert a.lay_out_refusal() == motion.turned_refusal(a.report)
    monkeypatch.setattr(findings, "TURNED_GEAR_MATE_SENSE_READ_BACK", "entity senses")
    monkeypatch.delattr(findings, "TURNED_GEAR_MATE_SENSE_ANGLES_SKEW")
    assert motion.turned_refusal(a.report) == ""                       # a bevel pair's axes meet
    assert motion.turned_refusal(b.report) == (
        "G1 and G2 mesh across shafts at 90°, and the angles at which a gear mate on crossed shafts turns right are "
        "not settled by the probes for this version (findings.TURNED_GEAR_MATE_SENSE_ANGLES_SKEW), so the gearbox "
        "is not built.")
    monkeypatch.setattr(findings, "TURNED_GEAR_MATE_SENSE_ANGLES_SKEW", (60.0, 120.0), raising=False)
    monkeypatch.setattr(findings, "TURNED_GEAR_MATE_SENSE_ANGLES", (30.0, 110.0))
    assert motion.turned_refusal(b.report) == (
        "G3 and G4 mesh across shafts at 120°, outside the 30°–110° the probes showed a gear mate on shafts that "
        "meet turning right at (findings.TURNED_GEAR_MATE_SENSE_ANGLES), so the gearbox is not built.")


def test_the_build_is_told_each_turned_gear_mates_sense(tmp_path, turned_findings):
    from gear_generator.workbook import gearbox
    a = assessed(tmp_path, bevel_reducer())
    plan = gearbox.plan_gearbox(a, None, exists=lambda p: False, read_sidecar=lambda p: None)
    assert plan.refusal == "" and plan.build_kwargs()["senses"] == {"G1 meshes G2": False, "G3 meshes G4": False}
    b = assessed(tmp_path, crossed_slant(), "B.xlsx")
    plan = gearbox.plan_gearbox(b, None, exists=lambda p: False, read_sidecar=lambda p: None)
    assert plan.build_kwargs()["senses"] == {"G1 meshes G2": True, "G3 meshes G4": False}   # crossed c = −1
    along = {m.gears[0]: (m.plane, m.face_global, round(m.z_front, 6)) for m in plan.motion.mates if m.kind == "along"}
    assert along == {"G1": ("front", "G1 Face Z", 2.0), "G2": ("right", "G2 Face X", -8.0),
                     "G4": ("top", "G4 Apex Y", 84.852814)}
    assert plan.assembly.check() == []


@pytest.mark.parametrize("change, said", [
    (lambda s: replace(s, gears=(replace(s.gears[0], at="0.4"),) + s.gears[1:]),
     "Meshes!A2: G1 and G2 are bevel gears whose cone tips are 0.4 mm apart; they mesh only with their tips "
     "together. G2's At would be 60 to put its tip on G1's."),
    (lambda s: replace(s, shafts=(replace(s.shafts[0], y="3.2"),) + s.shafts[1:]),
     "Meshes!A2: G1 and G2 are bevel gears whose cone tips are 3.2 mm apart; they mesh only with their tips "
     "together, and their shafts do not meet: they pass 3.2 mm apart."),
    (lambda s: replace(s, gears=(replace(s.gears[0], kind="spur", bore="8"), replace(s.gears[1], kind="spur",
                                                                                   bore="8")) + s.gears[2:]),
     "Meshes!A2: G1 and G2 are spur gears on shafts at 90°; across an angle only bevel gears (on shafts that meet) "
     "and helical gears (on crossed shafts) mesh."),
])
def test_what_a_bevel_stage_cannot_be_is_said_at_its_mesh(tmp_path, turned_findings, change, said):
    a = assessed(tmp_path, change(bevel_reducer()))
    assert said in [d.message for d in a.report.diagnostics]


def test_a_crossed_pair_off_its_distance_or_its_crossing_says_so(tmp_path, turned_findings):
    spec = crossed_slant()
    far = replace(spec, shafts=(spec.shafts[0], replace(spec.shafts[1], y="84.9")) + spec.shafts[2:])
    said = [d.message for d in assessed(tmp_path, far, "F.xlsx").report.diagnostics if d.is_error]
    assert ("Meshes!A2: G1 and G2 are 84.9 mm apart where their shafts pass closest; their teeth make 84.853 "
            "(+0.047 mm). Check the place of S2 (Shafts row 3); a shaft at an angle is best placed by formula.") in said
    left = replace(spec, gears=(spec.gears[0], replace(spec.gears[1], hand="left")) + spec.gears[2:])
    said = [d.message for d in assessed(tmp_path, left, "L.xlsx").report.diagnostics if d.is_error]
    assert any("right- and left-handed at 45° and 45°, so their shafts must cross at 0°" in m for m in said)
    two = replace(spec, gears=(spec.gears[0], replace(spec.gears[1], profile_shift="0.2")) + spec.gears[2:])
    said = [d.message for d in assessed(tmp_path, two, "S.xlsx").report.diagnostics if d.is_error]
    assert ("Meshes!A2: G1 and G2 are crossed helical gears with profile shift; crossed gears are built without it: "
            "set both shifts to 0.") in said


@pytest.mark.parametrize("make, name", [(bevel_reducer, "A.xlsx"), (crossed_slant, "B.xlsx")])
def test_a_turned_build_on_the_fake_writes_a_record_that_reads_with_each_meshs_sense(tmp_path, turned_findings,
                                                                                      make, name):
    """plan -> swbuild.build_gearbox on the fake -> finish_build -> the record written and read back: it reads, and
    every gear mate holds the sense planned for it, never 0 (W6-INTERFACES §7.1, §7.3)."""
    from gear_generator import store, swbuild
    from gear_generator.workbook import gearbox
    from test_swbuild import FakeSolidWorks, never_exists
    plan = gearbox.plan_gearbox(assessed(tmp_path, make(), name), None, exists=lambda p: False,
                                read_sidecar=lambda p: None)
    assert plan.refusal == "" and plan.motion is not None
    result = swbuild.build_gearbox(FakeSolidWorks(), **plan.build_kwargs(), exists=never_exists)
    assert result.ok, result.log_lines()
    done = gearbox.finish_build(plan, result, None, workbook=str(tmp_path / name), digest="d1", written_by="test",
                                read_sidecar=lambda p: None)
    read = store.link_record_from_json(store.link_record_to_json(done.record))
    assert read == done.record
    planned = {m.name: m.sense for m in plan.motion.mates if m.kind == motion.MESH}
    held = {m.name: m.sense for m in read.gearbox.mates if m.kind == motion.MESH}
    assert held == planned and set(held) == {"G1 meshes G2", "G3 meshes G4"} and 0 not in held.values()


# -- Update's classification and the turning round trip on the fake (W6-PLAN §2.7, §2.8, §2.9) ------------------

BOOK = "C:\\Books\\W.xlsx"
REBUILD = "so the gearbox needs building again."


def direct(spec):
    return assess.assess(replace(spec, source_path=BOOK), [], "C:\\Out\\")


def edited(spec, shafts=None, gears=None):
    shafts, gears = shafts or {}, gears or {}
    return replace(spec, shafts=tuple(replace(s, **shafts.get(s.id, {})) for s in spec.shafts),
                   gears=tuple(replace(g, **gears.get(g.id, {})) for g in spec.gears))


def crossed_off_base():
    """Fixture B moved 10 mm up, so S1 can pass to the other side of S2 without crossing the Top plane (the plan's
    review M4 move: the checks pass both sides, and the crossed mesh's sense flips)."""
    return edited(crossed_slant(), shafts={"S1": dict(y="10"), "S2": dict(y="94.852814"), "S3": dict(y="94.852814")})


def fake_turned_build(spec):
    """plan -> build_gearbox on the fake -> finish_build -> the record written and read back: (sw, record)."""
    from gear_generator import store, swbuild
    from gear_generator.workbook import gearbox
    from test_swbuild import FakeSolidWorks
    sw = FakeSolidWorks()
    plan = gearbox.plan_gearbox(direct(spec), None, exists=sw.exists, read_sidecar=lambda p: None)
    assert plan.refusal == "" and plan.motion is not None, plan.refusal
    result = swbuild.build_gearbox(sw, **plan.build_kwargs(), exists=sw.exists)
    assert result.ok, result.log_lines()
    done = gearbox.finish_build(plan, result, None, workbook=BOOK, digest="d1", written_by="test",
                                read_sidecar=lambda p: None, exists=sw.exists)
    return sw, store.link_record_from_json(store.link_record_to_json(done.record))


def fake_press(sw, record, spec):
    """classify -> update_gearbox on the fake -> finish_update -> the record written and read back."""
    from gear_generator import store, swbuild
    from gear_generator.workbook import update
    a = direct(spec)
    assert a.lay_out_refusal() == ""
    plan = update.classify(record, a, exists=lambda p: True)
    assert plan.refusal == "" and not plan.needs_new_revision, (plan.refusal, plan.structural)
    result = swbuild.update_gearbox(sw, **plan.update_kwargs(), exists=lambda p: True, mtime=lambda p: 5.0)
    assert result.failures == [], result.failures
    done = update.finish_update(plan, result, record, digest="d2", read_sidecar=lambda p: None, mtime=lambda p: 5.0)
    return plan, result, store.link_record_from_json(store.link_record_to_json(done.record))


def senses_of(record):
    return {m.name: m.sense for m in record.gearbox.mates if m.kind == motion.MESH}


def nothing_to_do(record, spec):
    from gear_generator.workbook import update
    plan = update.classify(record, direct(spec), exists=lambda p: True)
    return (plan.refusal, plan.structural, plan.resensed, plan.ratios, plan.axial, plan.replaced, plan.moved_shafts)


def driven(sw, record, gear, degrees):
    """Drive one gear on the fake (its solver: each gear mate as made, judged against the true sense the fake works
    out from where the gears stand) and give every gear's turn by gear id, rounded to 1e-6."""
    names = {c.name: c.gear for c in record.gearbox.components}
    turns = sw.drive(next(n for n, g in names.items() if g == gear), float(degrees))
    return {names[n]: round(t, 6) for n, t in turns.items() if n in names}


# The drives worked by hand in W6-PLAN §5 (never from the code): a sign slip in planning's senses on a turned mesh
# alone reaches the fake's solver as a mate made with the wrong Flip, and turns a gear the wrong way here.
DRIVE_A = {"G1": 30.0, "G2": -15.0, "G3": -15.0, "G4": 5.0}           # §5.1: +30° on G1
DRIVE_B = {"G1": 30.0, "G2": 15.0, "G3": 15.0, "G4": -10.0}           # §5.2: +30° on G1


@pytest.mark.parametrize("make, senses, drive", [
    (bevel_reducer, {"G1 meshes G2": 1, "G3 meshes G4": 1}, DRIVE_A),
    (crossed_slant, {"G1 meshes G2": -1, "G3 meshes G4": 1}, DRIVE_B)])
def test_a_turned_gearbox_built_on_the_fake_reads_back_with_nothing_to_update(turned_findings, make, senses, drive):
    sw, record = fake_turned_build(make())
    assert senses_of(record) == senses
    assert nothing_to_do(record, make()) == ("", (), (), (), (), (), ())
    plan, result, after = fake_press(sw, record, make())        # pressed anyway: SolidWorks holds it already
    assert result.placed == [] and result.resensed == [] and senses_of(after) == senses
    assert driven(sw, after, "G1", 30.0) == drive


@pytest.mark.parametrize("make, teeth, mate, drive", [
    (bevel_reducer, {"G1": dict(teeth="21")}, "G1 meshes G2", {"G1": 30.0, "G2": -15.75, "G3": -15.75, "G4": 5.25}),
    (crossed_slant, {"G4": dict(teeth="31")}, "G3 meshes G4", {"G1": 30.0, "G2": 15.0, "G3": 15.0,
                                                                "G4": round(-15 * 20 / 31, 6)}),
])
def test_a_tooth_change_on_a_turned_stage_remakes_its_mate_and_the_train_turns_as_worked_by_hand(
        turned_findings, make, teeth, mate, drive):
    """W6-PLAN §5.1 (G1 20 → 21: G2 −15.75°, G4 +5.25°) and §5.2 (G4 30 → 31: G4 −9.677419°)."""
    sw, record = fake_turned_build(make())
    spec = edited(make(), gears=teeth)
    plan, result, after = fake_press(sw, record, spec)
    assert plan.ratios == (mate,) and result.ratios == [mate] and plan.resensed == ()
    assert driven(sw, after, "G1", 30.0) == drive
    assert nothing_to_do(after, spec) == ("", (), (), (), (), (), ())


def test_a_crossed_shaft_moved_to_the_other_side_remakes_its_gear_mate_for_the_new_sense(turned_findings):
    spec = crossed_off_base()
    sw, record = fake_turned_build(spec)
    assert senses_of(record) == {"G1 meshes G2": -1, "G3 meshes G4": 1}
    moved = edited(spec, shafts={"S1": dict(y="179.705628")})
    plan, result, after = fake_press(sw, record, moved)
    assert (plan.resensed, plan.ratios, plan.structural, plan.moved_shafts) == (("G1 meshes G2",), (), (), ("S1",))
    assert plan.motion.ratios == (("G1 meshes G2", 20, 40),)       # the motion gate sees it (§7.14)
    assert [(m.a, m.b, m.k) for m in plan.motion.meshes][0] == ("G1", "G2", -0.5)
    assert [(m.a, m.b, m.k) for m in plan.motion.recorded_meshes][0] == ("G1", "G2", 0.5)
    assert result.resensed == ["G1 meshes G2"] and result.ratios == [] and result.sense_found_wrong == []
    assert senses_of(after) == {"G1 meshes G2": 1, "G3 meshes G4": 1}
    assert nothing_to_do(after, moved) == ("", (), (), (), (), (), ())
    # The outcome, by the fake's own judgement (it works a turned mesh's sense out from where the gears stand, A's
    # 293fdee): the remade mate turns right, the fake's default Flip being the one it needs, so it was not turned
    # round; and driving G1 turns G2 by the new k, -0.5 (the reviewer's contact-velocity derivation).
    asm = after.gearbox.assembly
    assert sw.turns_right("G1 meshes G2", asm) and result.turned_round == []
    assert driven(sw, after, "G1", 10.0) == {"G1": 10.0, "G2": -5.0, "G3": -5.0, "G4": round(5 * 20 / 30, 6)}


def name_of(record, gear):
    return next(c.name for c in record.gearbox.components if c.gear == gear)


def test_a_resense_remake_on_a_solidworks_that_wants_the_other_flip_is_turned_round_and_turns_right(turned_findings):
    """The fake told (made up, as A's tests do) that a turned mate needs the other Flip: the build turns its mates
    round, and the Update's remake reads wrong first, is turned round, and then turns G2 by the new k."""
    from gear_generator import store, swbuild
    from gear_generator.workbook import gearbox, update
    from test_swbuild import FakeSolidWorks
    spec = crossed_off_base()
    sw = FakeSolidWorks()
    sw.turned_flip_needed = True
    plan = gearbox.plan_gearbox(direct(spec), None, exists=sw.exists, read_sidecar=lambda p: None)
    built = swbuild.build_gearbox(sw, **plan.build_kwargs(), exists=sw.exists)
    assert built.ok and built.assembly.turned_round == ["G1 meshes G2", "G3 meshes G4"], built.log_lines()
    record = gearbox.finish_build(plan, built, None, workbook=BOOK, digest="d1", written_by="test",
                                  read_sidecar=lambda p: None, exists=sw.exists).record
    record = store.link_record_from_json(store.link_record_to_json(record))
    moved = edited(spec, shafts={"S1": dict(y="179.705628")})
    up, result, after = fake_press(sw, record, moved)
    assert (result.resensed, result.turned_round, result.sense_found_wrong) == (
        ["G1 meshes G2"], ["G1 meshes G2"], [])
    assert sw.turns_right("G1 meshes G2", after.gearbox.assembly) and senses_of(after)["G1 meshes G2"] == 1
    assert driven(sw, after, "G1", 10.0) == {"G1": 10.0, "G2": -5.0, "G3": -5.0, "G4": round(5 * 20 / 30, 6)}
    assert update.classify(after, direct(moved), exists=lambda p: True).resensed == ()


def test_a_failed_update_after_a_resense_remake_keeps_the_sense_on_record_until_a_press_heals_it(turned_findings):
    """As the ratios (7c0eecc): on a failed or skipped Update no mesh's sense on record changes; the next press
    finds the mate to remake again, and only then is the new sense recorded."""
    from gear_generator import store, swbuild
    from gear_generator.workbook import update
    spec = crossed_off_base()
    sw, record = fake_turned_build(spec)
    moved = edited(spec, shafts={"S1": dict(y="179.705628")})
    real_remake, real_rebuild, state = sw.set_gear_ratio, sw.rebuild, {"remade": False, "failed": False}

    def remake(*args, **kwargs):
        state["remade"] = True
        return real_remake(*args, **kwargs)

    def rebuild(kind=None):
        done = real_rebuild(kind)
        if state["remade"] and not state["failed"]:
            state["failed"] = True
            return False
        return done
    sw.set_gear_ratio, sw.rebuild = remake, rebuild
    plan = update.classify(record, direct(moved), exists=lambda p: True)
    result = swbuild.update_gearbox(sw, **plan.update_kwargs(), exists=lambda p: True, mtime=lambda p: 5.0)
    assert state["failed"] and (result.failures or result.skipped), result.log_lines()
    done = update.finish_update(plan, result, record, digest="d2", read_sidecar=lambda p: None, mtime=lambda p: 5.0)
    kept = store.link_record_from_json(store.link_record_to_json(done.record))
    assert senses_of(kept) == {"G1 meshes G2": -1, "G3 meshes G4": 1}
    again, healed, after = fake_press(sw, kept, moved)
    assert again.resensed == ("G1 meshes G2",) and healed.resensed == ["G1 meshes G2"]
    assert senses_of(after) == {"G1 meshes G2": 1, "G3 meshes G4": 1}
    assert sw.turns_right("G1 meshes G2", after.gearbox.assembly)
    assert driven(sw, after, "G1", 10.0) == {"G1": 10.0, "G2": -5.0, "G3": -5.0, "G4": round(5 * 20 / 30, 6)}
    assert nothing_to_do(after, moved) == ("", (), (), (), (), (), ())


def test_a_tooth_change_across_the_parallel_stage_of_fixture_a_remakes_only_that_mate(turned_findings):
    sw, record = fake_turned_build(bevel_reducer())
    spec = edited(bevel_reducer(), gears={"G3": dict(teeth="16"), "G4": dict(teeth="52")})
    plan, result, after = fake_press(sw, record, spec)
    assert (plan.ratios, plan.resensed, result.ratios) == (("G3 meshes G4",), (), ["G3 meshes G4"])
    held = {m.name: (m.ratio, m.sense) for m in after.gearbox.mates if m.kind == motion.MESH}
    assert held == {"G1 meshes G2": ([20, 40], 1), "G3 meshes G4": ([16, 52], 1)}
    assert nothing_to_do(after, spec) == ("", (), (), (), (), (), ())


def test_a_v3_mesh_entry_takes_its_sense_from_the_read_and_is_written_real_when_rewritten(turned_findings):
    """W6-INTERFACES §7.1: sense 0 on a parallel mesh entry is "parallel, take it from the read"; the finisher writes
    the real sense when it rewrites the entry."""
    sw, record = fake_turned_build(bevel_reducer())
    for entry in record.gearbox.mates:
        if entry.name == "G3 meshes G4":
            entry.sense = 0
    assert nothing_to_do(record, bevel_reducer()) == ("", (), (), (), (), (), ())
    teeth = edited(bevel_reducer(), gears={"G3": dict(teeth="16"), "G4": dict(teeth="52")})
    _, _, after = fake_press(sw, record, teeth)
    assert senses_of(after) == {"G1 meshes G2": 1, "G3 meshes G4": 1}


@pytest.mark.parametrize("make, change, said", [
    (bevel_reducer, dict(gears={"G1": dict(at="2")}),
     "G1's At (0 → 2) moves its cone tip off the Right plane (x 0 → 2): the mate G1 along S1 holds it on that "
     f"plane and cannot take a distance, {REBUILD}"),
    (bevel_reducer, dict(shafts={"S1": dict(axis="X-")}),
     "S1's axis is now X- where it was built X+: the layout's axis and the mates on it keep the direction they were "
     f"made with, {REBUILD}"),
    (crossed_off_base, dict(shafts={"S3": dict(z="10")}),
     f"S3's axis slants, and the layout holds a slanted axis as a fixed line: its point moved (Z 8 → 10), {REBUILD}"),
    (crossed_off_base, dict(shafts={"S3": dict(axis="-1, 1.8, 0")}),
     f"S3's axis slants, and the layout holds a slanted axis as a fixed line: its direction changed, {REBUILD}"),
    (crossed_off_base, dict(shafts={"S3": dict(axis="-1, 1.8, 0", x="-111")}),
     "S3's axis slants, and the layout holds a slanted axis as a fixed line: its point moved (X -110 → -111) and "
     f"its direction changed, {REBUILD}"),
    (crossed_off_base, dict(gears={"G4": dict(teeth="40")}),
     "G4's teeth (30 → 40) make it a crown gear where it was built a cone, which its values cannot carry; build it "
     "again as a new part."),
    (crossed_off_base, dict(shafts={"S2": dict(z="-8")}),
     "S2's Z crosses 0 (8 → -8): a layout plane cannot follow a global across its base plane, so it needs a new "
     "layout part."),
])
def test_what_a_turned_gearbox_cannot_take_through_update_is_said_once(turned_findings, make, change, said):
    from gear_generator.workbook import update
    _, record = fake_turned_build(make())
    plan = update.classify(record, direct(edited(make(), **change)), exists=lambda p: True)
    assert plan.structural == (said,)


def test_a_bevel_form_change_is_said_for_its_teeth_mate_teeth_or_shaft_angle():
    from gear_generator.spec import GearSpec
    from gear_generator.store import PartEntry
    from gear_generator.workbook import update
    entry = PartEntry(path="C:\\Out\\G2.SLDPRT", gears=["G2"])
    cone = GearSpec(kind="bevel", teeth="30", mate_teeth="20", shaft_angle="120", module="2.5", face_width="10",
                    bore="8")
    assert update._bevel_form_change(entry, cone, replace(cone, mate_teeth="20")) == ""
    assert update._bevel_form_change(entry, cone, replace(cone, shaft_angle="140")).startswith(
        "The shaft angle (120 → 140) makes it an internal bevel gear where it was built a cone")
    assert update._bevel_form_change(entry, cone, replace(cone, mate_teeth="15")).startswith(
        "Its mate's teeth (20 → 15) make it a crown gear where it was built a cone")


def test_a_static_gearbox_turning_a_shaft_onto_another_axis_needs_a_new_layout_part(turned_findings, monkeypatch):
    from gear_generator import store, swbuild
    from gear_generator.workbook import gearbox, update
    from test_swbuild import FakeSolidWorks
    monkeypatch.setattr(findings, "MOTION_ROUTE", None)
    sw = FakeSolidWorks()
    plan = gearbox.plan_gearbox(direct(bevel_reducer()), None, exists=sw.exists, read_sidecar=lambda p: None)
    assert plan.motion is None and plan.refusal == ""
    result = swbuild.build_gearbox(sw, **plan.build_kwargs(), exists=sw.exists)
    record = gearbox.finish_build(plan, result, None, workbook=BOOK, digest="d1", written_by="test",
                                  read_sidecar=lambda p: None, exists=sw.exists).record
    record = store.link_record_from_json(store.link_record_to_json(record))
    turned = edited(bevel_reducer(), shafts={"S3": dict(axis="X+", x="-68", y="0", z="0")})
    up = update.classify(record, direct(turned), exists=lambda p: True)
    assert "S3's axis is now X+ where it was built Z+: the layout part's planes and axis for it keep the direction " \
           "they were made with, so it needs a new layout part." in up.structural
    flipped = edited(bevel_reducer(), shafts={"S3": dict(axis="Z-")}, gears={"G4": dict(at="-5")})
    assert update.classify(record, direct(flipped), exists=lambda p: True).structural == ()


def test_update_refuses_a_recorded_mate_whose_plane_or_sense_it_cannot_read(turned_findings):
    from gear_generator.workbook import update
    _, record = fake_turned_build(bevel_reducer())
    along = next(m for m in record.gearbox.mates if m.kind == motion.ALONG)
    along.plane = "side"
    assert "measured from the plane 'side', where an along mate is measured from the Front, Top or Right plane" in \
        update.classify(record, direct(bevel_reducer()), exists=lambda p: True).refusal
    along.plane = "front"
    mesh = next(m for m in record.gearbox.mates if m.kind == motion.MESH)
    mesh.sense = 2
    assert "with the sense 2, where a gear mate's sense is -1 or +1" in \
        update.classify(record, direct(bevel_reducer()), exists=lambda p: True).refusal


def test_the_worker_is_given_each_slanted_line_axis_to_read_back(turned_findings):
    """W6-INTERFACES §7.15: ``lines={axis name: (point, direction)}`` to update_gearbox, and to build_gearbox when the
    layout part is reused; nothing when no shaft slants."""
    from dataclasses import replace as replaced
    from gear_generator.workbook import gearbox, layout, update
    line = ("S3 Axis", (-110.0, 94.852814, 8.0), (-0.5, 0.866025404, 0.0))
    shafts = layout.shaft_layouts(crossed_off_base())
    (name, point, direction), = layout.layout_lines(shafts)
    assert (name, point) == line[:2] and direction == pytest.approx(line[2])
    assert layout.layout_lines(layout.shaft_layouts(bevel_reducer())) == ()
    sw, record = fake_turned_build(crossed_off_base())
    kwargs = update.classify(record, direct(crossed_off_base()), exists=lambda p: True).update_kwargs()
    assert list(kwargs["lines"]) == ["S3 Axis"] and kwargs["lines"]["S3 Axis"][0] == line[1]
    plan = gearbox.plan_gearbox(direct(crossed_off_base()), None, exists=lambda p: False, read_sidecar=lambda p: None)
    assert "lines" not in plan.build_kwargs()                      # a new layout part draws its lines
    reuse = gearbox.LayoutReuse(plan.layout.path if hasattr(plan.layout, "path") else "C:\\Out\\L.SLDPRT",
                                layout.layout_globals(shafts), layout.layout_features(shafts),
                                lines=layout.layout_lines(shafts))
    assert replaced(plan, layout=reuse).build_kwargs()["lines"] == {name: (point, direction)}
    _, _, after = fake_press(sw, record, edited(crossed_off_base(), gears={"G1": dict(at="12")}))
    assert senses_of(after) == {"G1 meshes G2": -1, "G3 meshes G4": 1}


# -- the Results sheet (W6-PLAN §2.4, review S5; D12) -----------------------------------------------------------

def test_the_results_sheet_gives_each_turned_mesh_its_own_figures_and_each_shaft_what_it_is_seen_from():
    from gear_generator.gears import bevel
    from gear_generator.workbook import export
    a = direct(bevel_reducer())
    sheet = export.results_sheet(a.spec, a.report, when="T")
    assert sheet.rows[:4] == [["Shaft", "Speed (rpm)", "Turns", "Torque (N·m)"],
                              ["S1", 1500.0, "anticlockwise, seen from +X", 10.0],
                              ["S2", -750.0, "clockwise, seen from +Z", 19.6],
                              ["S3", 250.0, "anticlockwise, seen from +Z", 57.624]]
    assert sheet.rows[5][6:] == ["Shaft angle (°)", "Cone distance (mm)", "Apex distance (mm)"]
    cone = round(3 * 20 / (2 * math.sin(math.atan2(20, 40))), 6)
    assert sheet.rows[6] == ["G1–G2", 2.0, "", "", "", round(bevel.contact_ratio(a.report.layout.placed["G1"].derived),
                                                              4), 90.0, cone, 0.0] and cone == 67.082039
    assert sheet.rows[7] == ["G3–G4", 3.0, 68.0, 68.0, 0.0, 1.6364, "", "", ""]
    assert "crossed" not in sheet.note
    b = direct(crossed_slant())
    sheet = export.results_sheet(b.spec, b.report, when="T")
    assert sheet.rows[3] == ["S3", -333.333333, "anticlockwise, seen from (0.5, −0.866, 0)", 14.406]
    g1 = b.report.layout.placed["G1"]
    contact = crossed.normal_contact_ratio(2, 20, 40, 45.0, 45.0, 20.0)
    assert sheet.rows[6] == ["G1–G2", 2.0, 84.852814, 84.852814, 0.0, round(contact, 4), 90.0, "", ""]
    assert g1.module == 2 and sheet.rows[7][:2] == ["G3–G4", 1.5] and sheet.rows[7][6:] == [120.0, 38.188131, 0.0]
    assert sheet.note.endswith("The efficiency typed for a crossed helical mesh is the workbook's: a crossed pair "
                               "slides along its teeth, and its real efficiency is far lower.")


# -- the move fix in any parallel family (W6-PLAN §4.2) ---------------------------------------------------------

def _pair_on(axis, point):
    return GearboxSpec(
        box=Box(name="Pair", pressure_angle="20", efficiency="98"),
        shafts=(Shaft("S1", "frame", "0", "0", "0", axis, "input", "", "1000", "5"),
                Shaft("S2", "frame", *point, axis, "output")),
        gears=(Gear("G1", "S1", "5", "spur", "external", "20", "2", "", "10", "8"),
               Gear("G2", "S2", "5", "spur", "external", "40", "2", "", "10", "8")),
        meshes=(Mesh("G1", "G2"),))


@pytest.mark.parametrize("axis, point, cells, detail, edits", [
    ("X+", ("0", "30", "40"), "Y and Z", "S2 Y 30 → 36, Z 40 → 48", (("y", "36"), ("z", "48"))),
    ("Y-", ("30", "0", "40"), "X and Z", "S2 X 30 → 36, Z 40 → 48", (("x", "36"), ("z", "48"))),
    ("-1, 1.732050807569, 0", ("0", "0", "50"), "X, Y and Z", "S2 Z 50 → 60", (("z", "60"),)),
])
def test_the_move_fix_lies_in_the_familys_plane_and_writes_that_familys_cells(axis, point, cells, detail, edits):
    from gear_generator.workbook import fixes
    a = direct(_pair_on(axis, point))
    (error,) = [d.message for d in a.diagnostics if d.level == "error"]
    assert error.endswith(f"their teeth make 60 (−10 mm). Check the {cells} of S1 and S2 (Shafts rows 0 and 0); a "
                          "shaft at an angle is best placed by formula.")
    (move,) = [f for fx in a.report.fixes.values() for f in fx if f.title.startswith("Move")]
    assert (move.title, move.detail) == ("Move S2 by 10 mm", detail)
    assert [(e.key, e.value) for e in move.edits] == list(edits)
    assert [d for d in direct(fixes.apply(a.spec, move)).diagnostics if d.level == "error"] == []


# -- the one test of "is there a turned mesh, and is it refused" (assess.Assessment.turned_refusal) ---------------

def test_the_turned_refusal_is_asked_of_a_turned_mesh_only_whatever_else_holds_the_layout_back(monkeypatch):
    monkeypatch.delattr(findings, "TURNED_GEAR_MATE_SENSE_READ_BACK", raising=False)
    refused = ("G1 and G2 mesh across shafts at 90°, and which way a gear mate turns gears on shafts at an angle is "
               "not settled by the probes for this version (findings.TURNED_GEAR_MATE_SENSE_READ_BACK), so the "
               "gearbox is not built.")
    a = direct(bevel_reducer())
    assert a.turned_refusal() == refused == a.lay_out_refusal()
    spec = bevel_reducer()
    carrier = direct(replace(spec, shafts=spec.shafts + (Shaft("P1", "S2", "30", "0", "0", "Z+", ""),)))
    assert carrier.turned_refusal() == ""                 # not checked (W7): no mesh laid out, nothing turned known
    assert carrier.lay_out_refusal() == ("The gearbox cannot be laid out yet, since it is not checked: P1 is mounted "
                                         "on S2: carriers are laid out in phase W7.")
    sleeve = direct(replace(spec, gears=spec.gears + (
        Gear("G5", "S3", "20", "sleeve", "external", "20", "2", "", "10", "8"),)))
    assert sleeve.turned_refusal() == refused             # refused all the same, said after the later phase
    assert sleeve.lay_out_refusal() == ("The layout and assembly wait for a later phase: Gears row 0: G5 is a sleeve: "
                                        "sleeves are built in phase W8, with modes.")
    parallel = direct(_pair_on("Z+", ("60", "0", "0")))
    assert parallel.report.meshes and parallel.turned_refusal() == "" == parallel.lay_out_refusal()


def test_only_a_bevel_or_crossed_mesh_counts_as_turned(monkeypatch):
    """A mesh kind a later phase adds is not silently counted as turned (W7 and W8 extend the guard on purpose)."""
    from gear_generator.workbook import assess as assess_
    monkeypatch.delattr(findings, "TURNED_GEAR_MATE_SENSE_READ_BACK", raising=False)
    a = direct(bevel_reducer())
    for key, laid in list(a.report.meshes.items()):
        a.report.meshes[key] = replace(laid, kind="planetary")
    assert assess_.TURNED_KINDS == (geometry.BEVEL, geometry.CROSSED) and a.turned_refusal() == ""
