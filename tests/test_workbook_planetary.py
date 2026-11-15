"""A workbook's planetary stage (W7, ``workbook/planetary.py``): the pieces W7's interface commit wrote — copy names,
copy offsets, the carrier's id and stem, mesh links measured against a carrier. Agent B adds the planning tests
(W7-PLAN §5.5)."""

import math

import pytest

from gear_generator import swbuild
from gear_generator.workbook import layout, motion, planetary
from gear_generator.workbook.planetary import copy_id, copy_of, copy_offsets


@pytest.mark.parametrize("name, k, copies, expected", [("Planet", 1, 1, "Planet"), ("Planet", 2, 3, "Planet copy 2"),
                                                       ("P", 3, 3, "P copy 3"), ("P-2_b", 1, 4, "P-2_b copy 1")])
def test_a_copy_is_named_for_its_row_and_its_number(name, k, copies, expected):
    assert copy_id(name, k, copies) == expected
    assert copy_of(expected) == ((name, k) if copies > 1 else (name, 0))


@pytest.mark.parametrize("name, k, copies", [("Planet", 0, 3), ("Planet", 4, 3), ("Planet", 1, 0), ("", 1, 1)])
def test_a_copy_that_does_not_exist_is_refused(name, k, copies):
    with pytest.raises(ValueError, match=r"\.$"):
        copy_id(name, k, copies)


def test_copy_offsets_stand_evenly_round_the_carriers_own_axis():
    """W7-PLAN §4.1: (18, 0, 0) in 3 gives (18, 0), (−9, 15.588457268), (−9, −15.588457268) in the carrier's frame."""
    assert copy_offsets(18.0, 0.0, 0.0, 3) == ((18.0, 0.0, 0.0), (-9.0, 15.58845726812, 0.0),
                                                (-9.0, -15.58845726812, 0.0))
    four = copy_offsets(18.0, 0.0, 0.0, 4)
    assert four == ((18.0, 0.0, 0.0), (0.0, 18.0, 0.0), (-18.0, 0.0, 0.0), (0.0, -18.0, 0.0))
    assert all(math.copysign(1.0, v) > 0 for point in four for v in point if v == 0)        # no -0.0
    assert copy_offsets(18.0, -3.0, 2.5, 1) == ((18.0, -3.0, 2.5),)
    p3 = copy_offsets(19.5, 0.0, 0.0, 3)
    assert p3[1] == pytest.approx((-9.75, 16.887495374, 0.0)) and p3[2] == pytest.approx((-9.75, -16.887495374, 0.0))
    with pytest.raises(ValueError):
        copy_offsets(18.0, 0.0, 0.0, 0)


def test_a_carrier_goes_by_its_shaft_and_its_part_by_the_gearbox_name():
    assert layout.carrier_id("C") == "C carrier"
    assert layout.carrier_stem("Planetary_4to1", 0, "C") == "Planetary_4to1_C_Carrier"
    assert layout.carrier_stem("Planetary_4to1", 2, "C") == "Planetary_4to1_r2_C_Carrier"
    assert motion.mate_name(motion.AXIS, ("C carrier",), "C") == "C carrier on C Axis"
    assert motion.mate_name(motion.LOCK, ("C carrier", "CarrierGear")) == "CarrierGear locked to C carrier"
    assert motion.mate_name(motion.AXIS, ("Planet copy 2",), "P copy 2") == "Planet copy 2 on P copy 2 Axis"
    with pytest.raises(ValueError):
        layout.carrier_id("")


def test_mesh_links_carry_the_carrier_a_mesh_is_measured_against():
    """The fixture's sun mesh (c = +1, k = −1) and ring mesh (c = −1, k = +1/3), relative to C."""
    teeth = {"Sun": 18, "Planet copy 1": 18, "Ring": 54}
    meshes = [("Sun", "Planet copy 1"), ("Planet copy 1", "Ring")]
    sense = {("Sun", "Planet copy 1"): 1, ("Planet copy 1", "Ring"): -1}
    links = motion.mesh_links(meshes, teeth, sense, carrier_of={m: "C carrier" for m in meshes})
    assert links == (swbuild.MeshLink("Sun", "Planet copy 1", -1.0, 20.0, "C carrier"),
                     swbuild.MeshLink("Planet copy 1", "Ring", 1 / 3, 360 / 54, "C carrier"))
    assert motion.mesh_links(meshes[:1], teeth, sense)[0].carrier == ""


def test_the_stage_is_a_frozen_record_of_its_members():
    stage = planetary.Stage("C", "Sun", "Ring", "Planet", "P", 3, "R")
    assert (stage.carrier, stage.copies, stage.held) == ("C", 3, "R")


# -- W7-PLAN §4's fixtures, as specs (E commits §4.1 as Excel saved it) -------------------------------------------

import hashlib  # noqa: E402
import os  # noqa: E402
from fractions import Fraction  # noqa: E402

from gear_generator import findings  # noqa: E402
from gear_generator.workbook import assess, build, checks, geometry, gearbox, kinematics, model, xlsx  # noqa: E402
from gear_generator.workbook.model import Box, Gear, GearboxSpec, Mesh, Shaft, replace  # noqa: E402

BOOK = "C:\\Books\\Planetary_4to1.xlsx"
OUT = "C:\\Out\\"


def planetary_4to1():
    """W7-PLAN §4.1: the ring held, sun in at 1000 rpm and 2 N·m, the carrier out, three planets, CarrierGear on C."""
    return GearboxSpec(
        box=Box(name="Planetary_4to1", pressure_angle="20", efficiency="98"),
        shafts=(Shaft("S", "frame", "0", "0", "0", "Z+", "input", "", "1000", "2", row=2),
                Shaft("C", "frame", "0", "0", "0", "Z+", "output", row=3),
                Shaft("P", "C", "18", "0", "0", "", "", "3", row=4),
                Shaft("R", "frame", "0", "0", "0", "Z+", "fixed", row=5)),
        gears=(Gear("Sun", "S", "10", "spur", "external", "18", "1", "", "10", "6", part_name="Sun", row=2),
               Gear("Planet", "P", "10", "spur", "external", "18", "1", "", "10", "8", part_name="Planet", row=3),
               Gear("Ring", "R", "10", "spur", "internal", "54", "1", "", "10", "", row=4),
               Gear("CarrierGear", "C", "30", "spur", "external", "20", "1", "", "6", "10", part_name="CarrierGear",
                    row=5)),
        meshes=(Mesh("Sun", "Planet", row=2), Mesh("Planet", "Ring", row=3)))


def edited(spec, shafts=None, gears=None):
    shafts, gears = shafts or {}, gears or {}
    return replace(spec, shafts=tuple(replace(s, **shafts.get(s.id, {})) for s in spec.shafts),
                   gears=tuple(replace(g, **gears.get(g.id, {})) for g in spec.gears))


def sun_held():
    """§4.2: S fixed, R the input at 1000 rpm and 2 N·m."""
    return edited(planetary_4to1(), shafts={"S": dict(role="fixed", speed="", torque=""),
                                            "R": dict(role="input", speed="1000", torque="2")})


def on_z_minus():
    """§4.3: S, C and R on Z-, P blank (it faces C's way), every At turned to keep the faces 5 from the origin."""
    return edited(planetary_4to1(), shafts={x: dict(axis="Z-") for x in ("S", "C", "R")})


def carrier_held():
    """§4.4: C fixed and R the output (S in at 1000)."""
    return edited(planetary_4to1(), shafts={"C": dict(role="fixed"), "R": dict(role="output")})


def direct(spec):
    return assess.assess(replace(spec, source_path=BOOK), [], OUT)


def laid(spec):
    return geometry.layout(spec).placed


# -- placing copies, the meshes copy by copy, the stage ----------------------------------------------------------

def test_the_planet_is_placed_once_per_copy_in_its_carriers_frame():
    placed = laid(planetary_4to1())
    assert list(placed) == ["Sun", "Planet copy 1", "Planet copy 2", "Planet copy 3", "Ring", "CarrierGear"]
    copy2 = placed["Planet copy 2"]
    assert (copy2.gear, copy2.shaft, copy2.row, copy2.copy, copy2.carrier) == ("Planet copy 2", "P copy 2", "Planet",
                                                                                2, "C")
    centres = {g: p.centre for g, p in placed.items()}
    assert centres["Planet copy 1"] == (18.0, 0.0, 10.0)
    assert centres["Planet copy 2"] == pytest.approx((-9.0, 15.588457268, 10.0))
    assert centres["Planet copy 3"] == pytest.approx((-9.0, -15.588457268, 10.0))
    assert centres["Sun"] == centres["Ring"] == (0.0, 0.0, 10.0) and centres["CarrierGear"] == (0.0, 0.0, 30.0)
    assert {g: p.origin[2] for g, p in placed.items()} == {"Sun": 5.0, "Planet copy 1": 5.0, "Planet copy 2": 5.0,
                                                            "Planet copy 3": 5.0, "Ring": 5.0, "CarrierGear": 27.0}
    assert all(p.row == g for g, p in placed.items() if not p.carrier)          # a frame gear is its own row


def test_on_a_z_minus_carrier_the_offsets_are_composed_in_its_frame():
    """§4.3 (review M4): copy 2 lands at (−9, −15.588…), copy 3 at (−9, 15.588…); mid-faces at z −10."""
    placed = laid(on_z_minus())
    assert placed["Planet copy 1"].centre == (18.0, 0.0, -10.0)
    assert placed["Planet copy 2"].centre == pytest.approx((-9.0, -15.588457268, -10.0))
    assert placed["Planet copy 3"].centre == pytest.approx((-9.0, 15.588457268, -10.0))
    assert placed["Planet copy 2"].axis == (0.0, 0.0, -1.0) and placed["Sun"].origin[2] == -5.0


def test_the_meshes_are_listed_copy_by_copy_in_sheet_order():
    spec = planetary_4to1()
    assert geometry.expand_meshes(spec, laid(spec)) == (
        ("Sun", "Planet copy 1"), ("Sun", "Planet copy 2"), ("Sun", "Planet copy 3"),
        ("Planet copy 1", "Ring"), ("Planet copy 2", "Ring"), ("Planet copy 3", "Ring"))
    assert planetary.stages(spec) == (planetary.Stage("C", "Sun", "Ring", "Planet", "P", 3, "R"),)
    assert [planetary.stages(f())[0].held for f in (sun_held, carrier_held, on_z_minus)] == ["S", "C", "R"]
    assert planetary.mesh_carrier(spec, "Sun", "Planet copy 2") == "C" == planetary.mesh_carrier(spec, "Planet", "Ring")
    assert planetary.mesh_carrier(spec, "Sun", "Ring") == "frame"
    off = edited(spec, shafts={"R": dict(x="5")})
    assert planetary.mesh_carrier(off, "Planet", "Ring") is None


def test_how_many_copies_fit_and_mesh():
    """§4.1: up to 5 fit (21.16 mm apart at 5, 18 at 6, against 20.5); of those 1, 2, 3, 4 divide 72."""
    assert planetary.most_that_fit(18.0, 20.0, 1.0) == 5
    assert 2 * 18 * math.sin(math.pi / 5) == pytest.approx(21.1603, abs=1e-4)
    assert planetary.assembly_counts(18, 54, 5) == (1, 2, 3, 4)
    assert planetary.assembly_counts(21, 57, 5) == (1, 2, 3)


# -- kinematics with the carrier term (§2.5, §4) --------------------------------------------------------------------

@pytest.mark.parametrize("make, speeds, relative, torques, held, ratio", [
    (planetary_4to1, {"S": 1000, "C": 250, "P": -500, "R": 0}, {"P": -750}, {"S": 2.0, "C": 7.7624, "P": 0.0},
     {"R": 5.7624}, 4.0),
    (sun_held, {"S": 0, "C": 750, "P": 1500, "R": 1000}, {"P": 750}, {"R": 2.0, "C": 2.6403, "P": 0.0},
     {"S": 0.6403}, 4 / 3),
    (on_z_minus, {"S": 1000, "C": 250, "P": -500, "R": 0}, {"P": -750}, {"S": 2.0, "C": 7.7624, "P": 0.0},
     {"R": 5.7624}, 4.0),
    (carrier_held, {"S": 1000, "C": 0, "P": -1000, "R": Fraction(-1000, 3)}, {"P": -1000},
     {"S": 2.0, "R": 5.7624, "P": 0.0}, {"C": 7.7624}, 3.0),
])
def test_speeds_and_torques_through_the_stage_are_willis_and_the_basic_train(make, speeds, relative, torques, held,
                                                                             ratio):
    motion = kinematics.solve(make())
    assert motion.speeds == {k: Fraction(v) for k, v in speeds.items()} and not motion.free and not motion.jammed
    assert motion.relative == {k: Fraction(v) for k, v in relative.items()}
    assert motion.torques == pytest.approx(torques, abs=5e-5) and motion.held == pytest.approx(held, abs=5e-5)
    a = direct(make())
    assert checks.overall_ratio(a.spec, a.report)[0] == pytest.approx(ratio)


def test_the_torque_numbers_are_the_plans_worked_by_hand():
    """§2.5: η₀ = 0.98 · 0.98; ring held T_c = T_s(1 + η₀·z_r/z_s) = 2(1 + 0.9604·3) = 7.7624, the ring 5.7624, the
    stage T_c / (4·T_s) = 97.03 %; sun held T_s = η₀·2/3 = 0.64027, T_c = 2.64027 (stage 99.01 %)."""
    motion = kinematics.solve(planetary_4to1())
    assert motion.torques["C"] == pytest.approx(2 * (1 + 0.9604 * 3)) and motion.held["R"] == pytest.approx(6 * 0.9604)
    assert motion.torques["C"] / 8 == pytest.approx(0.9703, abs=5e-5)
    held = kinematics.solve(sun_held())
    assert held.held["S"] == pytest.approx(0.9604 * 2 / 3) and held.torques["C"] / (2 * 4 / 3) == pytest.approx(0.9901,
                                                                                                                abs=5e-5)


# -- checks (§2.3) ------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("make, worked, held", [
    (planetary_4to1, "Planetary, R fixed · 3 planets · 4.000 : 1 · output turns the same way", "R"),
    (sun_held, "Planetary, S fixed · 3 planets · 1.333 : 1 · output turns the same way", "S"),
    (on_z_minus, "Planetary, R fixed · 3 planets · 4.000 : 1 · output turns the same way", "R"),
    (carrier_held, "Planetary, C fixed · 3 planets · 3.000 : 1 · output turns the other way", "C"),
])
def test_each_fixture_checks_clean_and_says_its_stage(make, worked, held):
    a = direct(make())
    assert a.diagnostics == [] and a.report.diagnostics == []
    assert a.report.worked_out_as == worked and a.report.stages[0].held == held
    assert a.lay_out_refusal() == "" and a.build_refusal() == ""


@pytest.mark.parametrize("make", [planetary_4to1, sun_held, on_z_minus, carrier_held])
def test_every_copy_meshes_at_ten_degrees_and_the_ring_at_a_whole_pitch(make):
    """§2.4, §4: every copy θ 10° (``2ψ_k + 170° ≡ 10° mod 20°``), Sun 0, the ring 0 modulo its pitch from every copy;
    the carrier gear, reached by no mesh, 0."""
    theta = {g: math.degrees(t) for g, t in direct(make()).report.theta.items()}
    for k in (1, 2, 3):
        assert (theta[f"Planet copy {k}"] - 10.0) % 20.0 == pytest.approx(0.0, abs=1e-9) or \
            (theta[f"Planet copy {k}"] - 10.0) % 20.0 == pytest.approx(20.0, abs=1e-9)
    ring = theta["Ring"] % (360 / 54)
    assert min(ring, 360 / 54 - ring) == pytest.approx(0.0, abs=1e-9)
    assert theta["Sun"] % 20.0 == pytest.approx(0.0, abs=1e-9) and theta["CarrierGear"] == 0.0


def messages(spec):
    a = direct(spec)
    return [d.message for d in a.report.diagnostics], a.report.fixes


def test_five_copies_fail_the_assembly_condition_and_six_do_not_fit():
    said, fixes = messages(edited(planetary_4to1(), shafts={"P": dict(copies="5")}))
    assert said == ["Shafts row 4: 5 copies of Planet cannot all mesh with Sun and Ring at once: (18 + 54) / 5 = 14.4 "
                    "is not a whole number. With these teeth the copies can be 1, 2, 3 or 4; more would not fit round "
                    "C."] and fixes == {}
    said, fixes = messages(edited(planetary_4to1(), shafts={"P": dict(copies="6")}))
    assert said == ["Shafts row 4: 6 copies of Planet stand 18 mm apart round C, and their tips need 20.5 mm: 5 is the "
                    "most that fit round C, and of those 1, 2, 3 and 4 also mesh with Sun and Ring."] and fixes == {}


def test_a_ring_with_the_wrong_teeth_is_said_once_in_place_of_its_centre_error_and_no_fix_is_offered():
    said, fixes = messages(edited(planetary_4to1(), gears={"Ring": dict(teeth="56")}))
    assert said == ["Gears row 4: Ring has 56 teeth, and a ring around Sun (18) and Planet (18) needs 18 + 2 × 18 = 54: "
                    "with 56 the planets cannot mesh with both at once."] and fixes == {}


def test_a_planetary_centre_error_offers_no_fix():
    said, fixes = messages(edited(planetary_4to1(), shafts={"P": dict(x="18.5")}))
    tail = ("a shaft at an angle is best placed by formula; no fix is offered for a planetary stage, whose three gears "
            "and copies must change together.")
    assert said == [f"Meshes row 2: Sun and Planet are 18.5 apart; their teeth make 18 (+0.5 mm). Check the X and Y of S "
                    f"and P (Shafts rows 2 and 4); {tail}",
                    f"Meshes row 3: Planet and Ring are 18.5 apart; their teeth make 18 (+0.5 mm). Check the X and Y of "
                    f"P and R (Shafts rows 4 and 5); {tail}"]
    assert fixes == {}


def test_a_shifted_sun_takes_the_planet_at_its_working_distance_and_the_ring_is_checked_plain():
    """§2.3 (review M2): the existing working-centre checks apply; with a shift the z_r sentence is not said."""
    from gear_generator.gears import pair as pairs
    shifted = edited(planetary_4to1(), gears={"Sun": dict(profile_shift="0.3")})
    needed = pairs.describe(1.0, 18, 18, 20.0, 0.0, shift_1=0.3, shift_2=0.0)[0]
    said, fixes = messages(edited(shifted, shafts={"P": dict(x=repr(round(needed, 6)))}))
    assert len(said) == 1 and said[0].startswith(f"Meshes row 3: Planet and Ring are {checks._n(needed)} apart; "
                                                 "their teeth make 18 (") and fixes == {}


def test_a_small_sun_below_the_undercut_limit_is_warned_of():
    spec = edited(planetary_4to1(), shafts={"P": dict(x="13", copies="2")},
                  gears={"Sun": dict(teeth="7", bore="2"), "Planet": dict(teeth="19"), "Ring": dict(teeth="45")})
    said, _ = messages(spec)
    assert ("Gears row 2: Sun (7 teeth) is below the undercut limit, which is not modelled, and meshes Planet (19 "
            "teeth): the build checks interference only where the gears stand, so check Sun with Planet turning in "
            "SolidWorks.") in said


def test_a_planet_meshing_a_gear_off_its_carriers_axis_is_an_error():
    spec = planetary_4to1()
    spec = replace(spec, shafts=spec.shafts + (Shaft("Q", "frame", "60", "0", "0", "Z+", "", row=6),),
                   gears=spec.gears + (Gear("G9", "Q", "10", "spur", "external", "24", "1", "", "10", "8", row=6),),
                   meshes=spec.meshes + (Mesh("Planet", "G9", row=4),))
    said, _ = messages(spec)
    assert ("Meshes row 4: Planet rides C and meshes G9, whose shaft Q is not on C's axis: a gear on a carrier meshes "
            "only a gear on a shaft along its carrier's axis.") in said


def test_coaxial_members_and_a_bare_carrier_are_not_warned_of():
    spec = replace(planetary_4to1(), gears=planetary_4to1().gears[:3])           # no CarrierGear: C carries no gear
    assert messages(spec)[0] == []


# -- what W7 does not build (§1.2), each a warning at its cell ------------------------------------------------------

def refused(spec):
    """W7's refusals are errors of the workbook, said by the checks at their cells (the orchestrator's ruling), never
    rows waiting for a later phase."""
    assert not any("not built by this version" in d.message for d in build.later_rows(spec))
    return [d.message for d in checks.check(spec).errors]


def test_the_fixtures_are_not_refused():
    assert all(refused(f()) == [] for f in (planetary_4to1, sun_held, on_z_minus, carrier_held))


@pytest.mark.parametrize("change, sentence", [
    (lambda s: replace(s, shafts=s.shafts + (Shaft("P2", "P", "5", "0", "0", "", "", row=6),)),
     "Shafts row 6: P2 is mounted on P, which is itself mounted on C: a carrier riding another carrier is not built by "
     "this version; a planet shaft is built mounted on a frame shaft."),
    (lambda s: edited(s, shafts={x: dict(axis="X+") for x in ("S", "C", "R")}),
     "Shafts row 3: C's axis is X+: a planetary stage is built only on an axis along Z+ or Z- by this version."),
    (lambda s: edited(s, shafts={"P": dict(axis="Z-")}),
     "Shafts row 4: P faces Z- on C, the other way from its carrier: a planet that faces away from its carrier is not "
     "built by this version; leave its Axis blank to face its carrier's way."),
    (lambda s: edited(s, shafts={"P": dict(axis="X+")}),
     "Shafts row 4: P's axis is X+ on C: a planet turns about an axis parallel to its carrier's, so this is not built "
     "by this version; leave its Axis blank to turn on its carrier's."),
    (lambda s: edited(s, shafts={"S": dict(axis="Z-")}, gears={"Sun": dict(at="-10")}),
     "Shafts row 2: S faces Z- and C faces Z+: a planetary stage whose shafts face different ways is not built by "
     "this version; give S the Axis of C."),
    (lambda s: edited(s, shafts={"R": dict(role="")}),
     "Shafts row 3: S, C and R form a planetary stage with no member held: a differential is not built by this "
     "version; set one of them to Role fixed."),
    (lambda s: replace(s, gears=s.gears + (Gear("Planet2", "P", "20", "spur", "external", "12", "1", "", "6", "6",
                                                row=6),)),
     "Shafts row 4: P carries Planet and Planet2: a compound planet is not built by this version; a planet shaft is "
     "built with one gear."),
    (lambda s: replace(s, shafts=s.shafts + (Shaft("PB", "C", "-18", "0", "0", "", "", row=6),),
                       gears=s.gears + (Gear("PlanetB", "PB", "10", "spur", "external", "18", "1", "", "10", "8",
                                             row=6),),
                       meshes=s.meshes + (Mesh("Planet", "PlanetB", row=4),)),
     "Meshes row 4: Planet meshes PlanetB on the same carrier: a double planet is not built by this version; a planet "
     "is built meshing a sun and a ring on its carrier's axis."),
    (lambda s: replace(s, meshes=s.meshes + (Mesh("CarrierGear", "Sun", row=4),)),
     "Meshes row 4: CarrierGear is on C, the carrier, and meshes Sun: a gear on the carrier that meshes another gear "
     "is not built by this version; it is built locked to the carrier when it meshes nothing."),
    (lambda s: edited(s, gears={"Planet": dict(kind="helical", helix_angle="20")}),
     "Gears row 3: Planet is helical: a planetary stage is built with spur gears only by this version."),
    (lambda s: replace(s, shafts=s.shafts + (Shaft("C2", "frame", "100", "0", "0", "Z+", "", row=6),
                                             Shaft("P9", "C2", "10", "0", "0", "", "", row=7))),
     "Shafts row 6: C2 is a second carrier: one planetary stage per workbook is built by this version."),
])
def test_what_w7_does_not_build_is_refused_at_its_cell(change, sentence):
    assert sentence in refused(change(planetary_4to1()))


def test_a_mount_that_loops_and_copies_below_one_are_the_reads_errors(tmp_path):
    from test_workbook_model import write
    spec = edited(planetary_4to1(), shafts={"C": dict(mounted_on="P"), "P": dict(copies="0")})
    _, diagnostics = model.from_book(xlsx.read(write(tmp_path, spec)))
    said = [d.message for d in diagnostics]
    assert any("C is mounted on P, and following the mounts from P comes back to C: a chain of mounts must end on the "
               "frame." in m for m in said)
    assert any("P has 0 copies; a shaft has at least one." in m for m in said)


# -- every workbook before W7 plans bit for bit as it did (D7's rule, carried over) ---------------------------------

def _fingerprint(a):
    r = a.report
    out = [repr([d.message for d in a.diagnostics]), r.worked_out_as, r.unchecked]
    out.append(repr({k: v.hex() for k, v in sorted(r.theta.items())}))
    m = r.motion
    out.append(repr({k: str(v) for k, v in m.speeds.items()}))
    out.append(repr({k: float(v).hex() for k, v in m.torques.items()}))
    out.append(repr((m.free, m.jammed, m.later)))
    out.append(repr({k: (v[0].hex(), v[1].hex()) for k, v in r.centres.items()}))
    out.append(repr({g: (p.x.hex(), p.y.hex(), p.z.hex(), [c.hex() for c in p.centre], p.axis, p.sigma)
                     for g, p in r.layout.placed.items()}))
    plan = gearbox.plan_gearbox(a, None, exists=lambda p: False, read_sidecar=lambda p: None)
    out.append(plan.refusal)
    if not plan.refusal:
        out.append(repr(plan.build_kwargs()))
    return hashlib.sha256("\n".join(out).encode()).hexdigest()


# Taken at 5d5d51d (W7's interface commit, before any of B's W7 code), with the turned read-back finding set.
BEFORE_W7 = {
    "Reducer_12to1.xlsx": "41da0447e37015088d223b107ff53ebe82c983ebb38b5e6a1860b402cfd2c490",
    "Arc_Move.xlsx": "e6f8658f8d42437042b541d0e5a45fc7157caa5972fe044bc51b24f545d78b1e",
    "Risky_Placements.xlsx": "c221e0fd722e27e6562ec8e72c53a933d4e2b10ceb5de99a132377004d464c65",
    "bevel_reducer": "a881d20f11e59002d24c44d9c355646c95236a65a507449711a2055b1a709b92",
    "crossed_slant": "5401c79bb142cb17e3954ec0689413e779ed05450e3d314891f785ad6ac76d04",
}


@pytest.mark.parametrize("name", sorted(BEFORE_W7))
def test_every_workbook_before_w7_plans_bit_for_bit_as_it_did(name, monkeypatch):
    monkeypatch.setattr(findings, "TURNED_GEAR_MATE_SENSE_READ_BACK", "entity senses", raising=False)
    if name.endswith(".xlsx"):
        here = os.path.join(os.path.dirname(__file__), "fixtures", "excel-windows")
        spec, diagnostics = model.from_book(xlsx.read(os.path.join(here, name)))
        a = assess.assess(spec, diagnostics, OUT)
    else:
        import test_workbook_turned as turned
        a = assess.assess(replace(getattr(turned, name)(), source_path="C:\\B\\W.xlsx"), [], OUT)
    assert _fingerprint(a) == BEFORE_W7[name]


# -- the carrier part, the mates and the build plan (§2.6, §2.7, §4.1) -----------------------------------------------

from gear_generator import store, swbuild  # noqa: E402
from gear_generator.gears.base import AddComponent, AddGlobal, BuildPlan, GlobalVariable, Mate  # noqa: E402
from gear_generator.workbook import layout as layout_mod  # noqa: E402
from gear_generator.workbook import motion as motion_mod  # noqa: E402
from test_workbook_gearbox import Disk, built, failed, norm, stem  # noqa: E402


def test_the_carrier_part_holds_each_copys_axis_in_its_own_coordinates():
    """§4.1: C Axis; copy 1's X plane 18 from Right with Top as its other plane; copies 2 and 3 at (−9, ±15.588…)."""
    a = direct(planetary_4to1())
    carrier, = layout_mod.carrier_layouts(a.spec, a.report)
    drawn = layout_mod.carrier_shafts(carrier)
    assert [g.name for g in layout_mod.layout_globals(drawn)] == ["P copy 1 X", "P copy 2 X", "P copy 2 Y",
                                                                  "P copy 3 X", "P copy 3 Y"]
    assert [g.expression for g in layout_mod.layout_globals(drawn)] == ["18", "-9", "15.588457268", "-9",
                                                                        "-15.588457268"]
    assert layout_mod.layout_features(drawn) == ("C Axis", "P copy 1 X Plane", "P copy 1 Axis", "P copy 2 X Plane",
                                                 "P copy 2 Y Plane", "P copy 2 Axis", "P copy 3 X Plane",
                                                 "P copy 3 Y Plane", "P copy 3 Axis")
    plan = layout_mod.carrier_plan(carrier, "", "C:\\Out\\Planetary_4to1_C_Carrier.SLDPRT")
    assert plan.kind == layout_mod.CARRIER_KIND and plan.check() == []
    assert layout_mod.carrier_frame(carrier) == layout_mod.Frame((1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0),
                                                                 (0.0, 0.0, 0.0))
    z_minus, = layout_mod.carrier_layouts(on_z_minus(), None)
    assert z_minus.axes == carrier.axes and z_minus.direction == (0.0, 0.0, -1.0)      # review M4: the same axes
    assert layout_mod.carrier_frame(z_minus).rotation == (1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, -1.0)
    assert [s.shaft for s in layout_mod.shaft_layouts(a.spec)] == ["S", "C", "R"]    # P is in the carrier part


FIXTURE_MATES = [
    ("Sun on S Axis", "axis", ("Sun",), "S", ""), ("Sun along S", "along", ("Sun",), "S", ""),
    ("C carrier on C Axis", "axis", ("C carrier",), "C", ""), ("C carrier along C", "along", ("C carrier",), "C", ""),
    ("CarrierGear locked to C carrier", "lock", ("C carrier", "CarrierGear"), "", ""),
    ("Planet copy 1 on P copy 1 Axis", "axis", ("Planet copy 1",), "P copy 1", "C carrier"),
    ("Planet copy 1 along P copy 1", "along", ("Planet copy 1",), "P copy 1", ""),
    ("Planet copy 2 on P copy 2 Axis", "axis", ("Planet copy 2",), "P copy 2", "C carrier"),
    ("Planet copy 2 along P copy 2", "along", ("Planet copy 2",), "P copy 2", ""),
    ("Planet copy 3 on P copy 3 Axis", "axis", ("Planet copy 3",), "P copy 3", "C carrier"),
    ("Planet copy 3 along P copy 3", "along", ("Planet copy 3",), "P copy 3", ""),
    ("Sun meshes Planet copy 1", "mesh", ("Sun", "Planet copy 1"), "", ""),
    ("Sun meshes Planet copy 2", "mesh", ("Sun", "Planet copy 2"), "", ""),
    ("Sun meshes Planet copy 3", "mesh", ("Sun", "Planet copy 3"), "", ""),
    ("Planet copy 1 meshes Ring", "mesh", ("Planet copy 1", "Ring"), "", ""),
]


def plan_of(spec):
    a = direct(spec)
    return a, motion_mod.motion_plan(a.spec, a.report, layout_mod.frames(a.report))


def test_the_mates_of_the_fixture_are_the_spikes_set_chosen_by_rank():
    """§4.1 (J5, measured by the spike): fifteen mates; N sun mates and ONE ring mate; the other two ring meshes
    unmated; the ring fixed; one shared Planet Face Z (§6.7); along mates on the layout's Front plane (§6.8)."""
    _, plan = plan_of(planetary_4to1())
    assert [(m.name, m.kind, m.gears, m.shaft, m.on) for m in plan.mates] == FIXTURE_MATES
    assert plan.unmated == (("Planet copy 2", "Ring"), ("Planet copy 3", "Ring")) and plan.fixed == ("Ring",)
    assert plan.carriers == ("C carrier",) and plan.drag == ("Sun",)
    along = {m.name: (m.face_global, m.z_front, m.plane) for m in plan.mates if m.kind == "along"}
    assert along["Planet copy 2 along P copy 2"] == ("Planet Face Z", 5.0, "front")
    assert along["C carrier along C"] == ("", 0.0, "front")


def test_the_senses_of_the_fixtures_gear_mates_are_their_contacts():
    """W7-INTERFACES §6.10 / W6's identity ``mate_senses[name] = (sense == −1)``. By hand, at the contact: a sun and a
    planet touch outside, so in the carrier's frame (both axes +Z) their pitch points move together only if they
    turn opposite ways — ``z_s·ω_s + z_p·ω_p = 0``, c = +1, k = −18/18 = −1 < 0: False. A planet inside the ring
    touches it from within, so their pitch points move together when both turn the same way — ``z_p·ω_p − z_r·ω_r =
    0``, c = −1, k = +18/54 > 0: True (the spike's ring mate read wrong with the first Flip)."""
    a = direct(planetary_4to1())
    plan = gearbox.plan_gearbox(a, None, exists=lambda p: False, read_sidecar=lambda p: None)
    assert plan.mate_senses == {"Sun meshes Planet copy 1": False, "Sun meshes Planet copy 2": False,
                                "Sun meshes Planet copy 3": False, "Planet copy 1 meshes Ring": True}
    assert plan.build_kwargs()["senses"] == plan.mate_senses


@pytest.mark.parametrize("make, held, fixed, axes", [
    (sun_held, "S", ("Sun",), ["Ring on R Axis"]),
    (carrier_held, "C", ("CarrierGear", "C carrier"), ["Sun on S Axis", "Ring on R Axis"]),
])
def test_with_another_member_held_the_same_four_gear_mates_are_made(make, held, fixed, axes):
    _, plan = plan_of(make())
    meshes = [m.name for m in plan.mates if m.kind == "mesh"]
    assert meshes == ["Sun meshes Planet copy 1", "Sun meshes Planet copy 2", "Sun meshes Planet copy 3",
                      "Planet copy 1 meshes Ring"]
    assert plan.unmated == (("Planet copy 2", "Ring"), ("Planet copy 3", "Ring")) and plan.fixed == fixed
    names = [m.name for m in plan.mates]
    assert all(n in names for n in axes)
    assert ("C carrier on C Axis" in names) == (held != "C")
    assert ("CarrierGear locked to C carrier" in names) == (held != "C")


def test_the_fixtures_build_plan_inserts_the_carrier_and_each_copy_of_one_part():
    a = direct(planetary_4to1())
    plan = gearbox.plan_gearbox(a, None, exists=lambda p: False, read_sidecar=lambda p: None)
    assert plan.refusal == ""
    assert plan.handles == {"gear1": "Sun", "gear2c1": "Planet copy 1", "gear2c2": "Planet copy 2",
                            "gear2c3": "Planet copy 3", "gear3": "Ring", "gear4": "CarrierGear"}
    assert plan.carrier_handles == {"carrier1": "C carrier"}
    assert stem(plan.carrier_paths["C"]) == "Planetary_4to1_C_Carrier"
    assert [stem(j.path) for j in plan.build] == ["Sun", "Planet", "Ring_m1_N54", "CarrierGear"]
    kwargs = plan.build_kwargs()
    assert kwargs["gears"] == dict(plan.handles, carrier1="C carrier")                # §6.2
    assert kwargs["carriers"] == list(plan.carriers) and plan.carriers[0].kind == layout_mod.CARRIER_KIND
    ops = plan.assembly.ops
    assert plan.assembly.check() == []
    assert [op.id for op in ops if isinstance(op, AddComponent)] == ["layout", "carrier1", "gear1", "gear2c1",
                                                                      "gear2c2", "gear2c3", "gear3", "gear4"]
    assert [stem(op.path) for op in ops if isinstance(op, AddComponent)][3:6] == ["Planet"] * 3
    assert [op.name for op in ops if isinstance(op, AddGlobal)] == ["Sun Face Z", "Planet Face Z"]   # once: S5
    mates = {op.name: (op.kind, op.a, op.b) for op in ops if isinstance(op, Mate)}
    assert list(mates) == [m[0] for m in FIXTURE_MATES]
    assert mates["C carrier on C Axis"] == ("coincident", "carrier1:C Axis", "layout:C Axis")
    assert mates["C carrier along C"] == ("point", "carrier1:origin", "layout:plane1")
    assert mates["CarrierGear locked to C carrier"] == ("lock", "carrier1", "gear4")
    assert mates["Planet copy 2 on P copy 2 Axis"] == ("coincident", "gear2c2:Gear Axis", "carrier1:P copy 2 Axis")
    assert mates["Planet copy 2 along P copy 2"] == ("point distance", "gear2c2:origin", "layout:plane1")
    assert mates["Planet copy 1 meshes Ring"] == ("gear", "gear2c1:Gear Axis", "gear3:Gear Axis")
    unfixed = [op.component for op in ops if type(op).__name__ == "Unfix"]
    assert "gear3" not in unfixed and unfixed[:2] == ["gear1", "carrier1"]
    frames = {h: plan.frames[g] for h, g in plan.handles.items()}
    assert frames["gear2c2"].at == pytest.approx((-9.0, 15.588457268, 5.0)) and frames["gear4"].at == (0.0, 0.0, 27.0)
    assert [e.kind for e in gearbox.journal(plan)][-2:] == ["carrier", "assembly"]


def test_a_held_carrier_is_inserted_fixed_and_its_planets_are_still_mated_to_its_axes():
    a = direct(carrier_held())
    plan = gearbox.plan_gearbox(a, None, exists=lambda p: False, read_sidecar=lambda p: None)
    ops = plan.assembly.ops
    assert plan.assembly.check() == []
    unfixed = [op.component for op in ops if type(op).__name__ == "Unfix"]
    assert "carrier1" not in unfixed and "gear4" not in unfixed
    mates = {op.name: (op.a, op.b) for op in ops if isinstance(op, Mate)}
    assert mates["Planet copy 3 on P copy 3 Axis"] == ("gear2c3:Gear Axis", "carrier1:P copy 3 Axis")


# -- finishing a build: the record's carriers, copies and mates (§2.11; W7-INTERFACES §6.1, §6.2) ------------------

def run_planetary(plan, disk, fail_assembly=False):
    """What build_gearbox will answer for a planetary plan, by its pinned fields (until A's fake builds carriers)."""
    result = swbuild.GearboxResult()
    for job in plan.build:
        result.parts.built.append(built(job.path, job.spec.kind))
        disk.add(job.path)
    result.checked = [r.path for r in plan.reuse]
    if isinstance(plan.layout, gearbox.LayoutReuse):
        result.layout_reused = plan.layout.path
        result.checked.append(plan.layout.path)
    else:
        result.layout = built(plan.layout_path, "layout")
        disk.add(plan.layout_path)
    for item in plan.carriers:
        if isinstance(item, gearbox.CarrierReuse):
            result.carriers_reused.append(item.path)
            result.checked.append(item.path)
        else:
            result.carriers.append(built(item.path, "carrier"))
            disk.add(item.path)
    if fail_assembly:
        result.assembly = failed(plan.assembly_path)
        return result
    result.assembly = built(plan.assembly_path, "assembly")
    disk.add(plan.assembly_path)
    names = {layout_mod.LAYOUT_HANDLE: stem(plan.layout_path) + "-1"}
    counts = {}
    for handle, gear in list(plan.handles.items()) + list(plan.carrier_handles.items()):
        part = stem(plan.part_of[gear]) if gear in plan.part_of else stem(plan.carrier_paths["C"])
        counts[part] = counts.get(part, 0) + 1
        names[handle] = f"{part}-{counts[part]}"
    result.components = names
    result.assembly.components = dict(names)
    return result


def finish(plan, result, record, disk):
    done = gearbox.finish_build(plan, result, record, workbook=BOOK, digest="d1", written_by="test",
                                read_sidecar=disk.read_sidecar, exists=disk.exists, stamp="2026-11-14T00:00:00Z")
    disk.write(done)
    return store.link_record_from_json(store.link_record_to_json(done.record or record))


def test_a_planetary_build_writes_a_record_that_reads_back_with_its_carrier_copies_and_senses():
    disk = Disk()
    a = direct(planetary_4to1())
    plan = gearbox.plan_gearbox(a, None, exists=disk.exists, read_sidecar=disk.read_sidecar)
    record = finish(plan, run_planetary(plan, disk), None, disk)
    box = record.gearbox
    carrier, = box.carriers
    assert (carrier.shaft, norm(carrier.path), carrier.component) == ("C", norm(plan.carrier_paths["C"]),
                                                                      "Planetary_4to1_C_Carrier-1")
    assert carrier.direction == [0.0, 0.0, 1.0] and [x.shaft for x in carrier.axes] == ["P copy 1", "P copy 2",
                                                                                         "P copy 3"]
    assert {c.gear: (c.of, c.name) for c in box.components}["Planet copy 2"] == ("Planet", "Planet-2")
    assert {c.gear: c.of for c in box.components}["Sun"] == ""
    mates = {m.name: (m.on, m.sense) for m in box.mates}
    assert mates["Planet copy 2 on P copy 2 Axis"] == ("C carrier", 0)
    assert mates["Planet copy 1 meshes Ring"] == ("", -1) and mates["Sun meshes Planet copy 3"] == ("", 1)
    assert box.unmated == [["Planet copy 2", "Ring"], ["Planet copy 3", "Ring"]] and box.fixed == ["Ring"]


def test_a_build_that_fails_after_the_carrier_part_is_continued_and_keeps_its_carrier_on_record():
    """W7-INTERFACES §6.1 (a): the carrier part saved, the assembly failed; the next press reuses it (checked live)
    and the finish keeps one CarrierEntry beside mates whose ``on`` names it; the record reads back."""
    disk = Disk()
    a = direct(planetary_4to1())
    plan = gearbox.plan_gearbox(a, None, exists=disk.exists, read_sidecar=disk.read_sidecar)
    record = finish(plan, run_planetary(plan, disk, fail_assembly=True), None, disk)
    assert [c.shaft for c in record.gearbox.carriers] == ["C"] and record.gearbox.mates == []
    again = gearbox.plan_gearbox(a, record, exists=disk.exists, read_sidecar=disk.read_sidecar)
    assert again.refusal == "" and again.revision == 0
    assert isinstance(again.carriers[0], gearbox.CarrierReuse) and isinstance(again.layout, gearbox.LayoutReuse)
    assert "carriers" in again.build_kwargs() and isinstance(again.build_kwargs()["carriers"][0],
                                                             swbuild.DocumentValues)
    record = finish(again, run_planetary(again, disk), record, disk)
    box = record.gearbox
    assert [c.shaft for c in box.carriers] == ["C"] and box.carriers[0].component == "Planetary_4to1_C_Carrier-1"
    assert {m.on for m in box.mates} == {"", "C carrier"}


def test_the_gears_below_the_undercut_limit_are_handed_to_the_builds_wording():
    """W7-PLAN §2.3 item 7: ``Report.undercut`` and ``GearboxPlan.undercut`` name them (row ids) for the interference
    sentence's clause; the fixture has none."""
    spec = edited(planetary_4to1(), shafts={"P": dict(x="13", copies="2")},
                  gears={"Sun": dict(teeth="7", bore="2"), "Planet": dict(teeth="19"), "Ring": dict(teeth="45")})
    assert direct(spec).report.undercut == ("Sun",)
    a = direct(planetary_4to1())
    assert a.report.undercut == () and gearbox.plan_gearbox(a, None, exists=lambda p: False,
                                                            read_sidecar=lambda p: None).undercut == ()


# -- Update's classification of a planetary stage (§2.10; W7-INTERFACES §6.1, §6.3-§6.7) ---------------------------

from gear_generator.workbook import update  # noqa: E402

REBUILD = "so the gearbox needs building again."


def built_record(spec=None):
    disk = Disk()
    a = direct(spec or planetary_4to1())
    plan = gearbox.plan_gearbox(a, None, exists=disk.exists, read_sidecar=disk.read_sidecar)
    return finish(plan, run_planetary(plan, disk), None, disk)


def classify(record, spec):
    return update.classify(record, direct(spec), exists=lambda p: True)


def test_a_planetary_update_always_carries_its_carriers_placements_and_links():
    record = built_record()
    up = classify(record, planetary_4to1())
    assert (up.refusal, up.structural, up.replaced, up.carriers_moved, up.axial, up.ratios) == ("", (), (), (), (), ())
    carrier, = up.carriers                                             # §6.3: always, as the layout is
    assert norm(carrier.path).endswith("planetary_4to1_c_carrier.sldprt")
    assert [g.name for g in carrier.variables][:2] == ["P copy 1 X", "P copy 2 X"] and "C Axis" in carrier.features
    assert up.update_kwargs()["carriers"] == [carrier]
    first = up.placements[0]                                           # §6.4
    assert (first.gear, first.component, first.pitch) == ("C carrier", "Planetary_4to1_C_Carrier-1", 0.0)
    motion = up.motion
    assert motion.recorded[0].gear == "C carrier" and motion.recorded[0].pitch == 0.0
    assert motion.carriers == (swbuild.CarrierLink("C carrier", ("Planet copy 1", "Planet copy 2", "Planet copy 3"),
                                                   (0.0, 0.0, 0.0), (0.0, 0.0, 1.0)),)
    assert motion.held == ("Ring",) and set(motion.held) <= set(motion.fixed)                          # §6.5
    links = {(m.a, m.b): (round(m.k, 9), m.carrier) for m in motion.meshes}                           # §6.6
    assert links == {("Sun", f"Planet copy {k}"): (-1.0, "C carrier") for k in (1, 2, 3)} | {
        (f"Planet copy {k}", "Ring"): (round(1 / 3, 9), "C carrier") for k in (1, 2, 3)}
    assert [m.name for m in record.gearbox.mates if m.kind == "mesh"] == [
        "Sun meshes Planet copy 1", "Sun meshes Planet copy 2", "Sun meshes Planet copy 3", "Planet copy 1 meshes Ring"]
    assert motion.face_globals == (("Sun", GlobalVariable("Sun Face Z", "5")),
                                   ("Planet", GlobalVariable("Planet Face Z", "5")))                   # §6.7, once


def test_the_record_s_carrier_is_a_body_its_mates_may_name():
    """§6.1 (b): ``C carrier on C Axis`` and ``CarrierGear locked to C carrier`` name the carrier in ``gears``."""
    record = built_record()
    assert update._bad_mates(record.gearbox) == ""
    record.gearbox.carriers = []
    assert "C carrier, which is not in the assembly on record" in update._bad_mates(record.gearbox)


def test_new_teeth_that_keep_both_centres_move_the_planets_on_the_carrier_part_and_remake_the_gear_mates():
    """§6 p3's edit: Sun 21, Ring 57, P's X 19.5 — two parts' values, the carrier part's globals, four remakes."""
    record = built_record()
    spec = edited(planetary_4to1(), shafts={"P": dict(x="19.5")}, gears={"Sun": dict(teeth="21"),
                                                                        "Ring": dict(teeth="57")})
    assert direct(spec).report.errors == []
    up = classify(record, spec)
    assert (up.structural, up.carriers_moved) == ((), ("C",))
    assert [p.changed for p in up.parts] == [True, False, True, False]
    values = {g.name: g.expression for g in up.carriers[0].variables}
    assert values == {"P copy 1 X": "19.5", "P copy 2 X": "-9.75", "P copy 2 Y": "16.887495374", "P copy 3 X": "-9.75",
                      "P copy 3 Y": "-16.887495374"}
    assert up.ratios == ("Sun meshes Planet copy 1", "Sun meshes Planet copy 2", "Sun meshes Planet copy 3",
                         "Planet copy 1 meshes Ring")
    assert direct(spec).report.motion.torques["C"] == pytest.approx(2 * (1 + 0.9604 * 57 / 21), abs=1e-9)
    assert float(direct(spec).report.motion.speeds["C"]) == pytest.approx(1000 / (1 + 57 / 21))      # 3.714 : 1


def test_a_planets_at_moves_its_one_shared_global_and_a_held_ring_is_re_placed():
    record = built_record()
    up = classify(record, edited(planetary_4to1(), gears={"Planet": dict(at="12")}))
    assert (up.structural, up.axial) == ((), ("Planet",))
    assert dict(up.motion.face_globals)["Planet"] == GlobalVariable("Planet Face Z", "7")
    up = classify(record, edited(planetary_4to1(), gears={"Ring": dict(at="12")}))
    assert (up.structural, up.replaced) == ((), ("Ring",)) and up.motion.held == ("Ring",)


@pytest.mark.parametrize("change, said", [
    (dict(shafts={"P": dict(copies="4")}),
     ("P now has 4 copies where it was built with 3, and Update SolidWorks cannot add or take out a planet, " + REBUILD,)),
    (dict(shafts={"P": dict(copies="5")}),
     ("P now has 5 copies where it was built with 3, and Update SolidWorks cannot add or take out a planet, " + REBUILD,)),
])
def test_the_number_of_planets_changing_needs_a_new_revision(change, said):
    up = classify(built_record(), edited(planetary_4to1(), **change))
    assert up.structural == said and up.needs_new_revision


def test_a_planet_moved_off_its_carrier_or_another_member_held_needs_a_new_revision():
    record = built_record()
    up = classify(record, edited(planetary_4to1(), shafts={"P": dict(mounted_on="frame", copies="")}))
    assert up.structural[:2] == (
        "P is now on the frame where it was built on C, and its mates hold it to C's axes, " + REBUILD,
        "C carries no planet now where it was built as a carrier, and its carrier part cannot be taken out of the "
        "assembly, " + REBUILD)
    up = classify(record, sun_held())
    assert up.structural == ("Ring was built fixed, but R now turns (its Role is not fixed and no fixed shaft holds it "
                             "still), so the gearbox needs building again to mate it to turn.",
                             "S's Role is now fixed, but Sun was built mated to turn, so the gearbox needs building "
                             "again to hold it fixed.")


def test_a_copy_crossing_the_carrier_parts_base_plane_needs_a_new_revision():
    record = built_record(edited(planetary_4to1(), shafts={"P": dict(y="2")}))
    up = classify(record, edited(planetary_4to1(), shafts={"P": dict(y="-2")}))
    assert "P copy 1's Y crosses 0 (2 → -2): a layout plane cannot follow a global across its base plane, so it needs " \
           "a new carrier part for C." in up.structural


def test_finishing_a_planetary_update_records_the_carriers_new_axes_and_the_shared_global():
    from gear_generator.swbuild import GearboxUpdate, UpdateResult
    record = built_record()
    spec = edited(planetary_4to1(), shafts={"P": dict(x="19.5")}, gears={"Sun": dict(teeth="21"),
                                                                        "Ring": dict(teeth="57"),
                                                                        "Planet": dict(at="12")})
    up = classify(record, spec)
    result = GearboxUpdate(parts=[UpdateResult(changed=["x"]) if p.changed else UpdateResult(unchanged=["x"])
                                  for p in up.parts],
                           layout=UpdateResult(unchanged=["x"]), carriers=[UpdateResult(changed=["P copy 1 X"])],
                           placed=[p.gear for p in up.placements], axial=["Planet"], ratios=list(up.ratios),
                           changed=[up.carriers[0].path, up.assembly])
    done = update.finish_update(up, result, record, digest="d2", read_sidecar=lambda p: None, mtime=lambda p: 5.0)
    box = store.link_record_from_json(store.link_record_to_json(done.record)).gearbox
    assert [round(x.x, 6) for x in box.carriers[0].axes] == [19.5, -9.75, -9.75]
    along = {m.name: m.z_front for m in box.mates if m.kind == "along"}
    assert along["Planet copy 3 along P copy 3"] == 7.0 and along["Sun along S"] == 5.0
    ratios = {m.name: (m.ratio, m.sense) for m in box.mates if m.kind == "mesh"}
    assert ratios["Planet copy 1 meshes Ring"] == ([18, 57], -1) and ratios["Sun meshes Planet copy 2"] == ([21, 18], 1)
    failed_ = GearboxUpdate(parts=result.parts, failures=[("x", "it would not")], carriers=result.carriers,
                            axial=["Planet"], ratios=list(up.ratios))
    kept = update.finish_update(up, failed_, record, digest="d2", read_sidecar=lambda p: None, mtime=lambda p: 5.0)
    assert [x.x for x in kept.record.gearbox.carriers[0].axes][0] == 18.0           # what was last known true
