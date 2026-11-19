"""Package B of PLAN-PRINTED's stage F4 (§5.2, §5.4, §5.6; F4-INTERFACES §4, §6.1, §6.3): what each Meshes row's teeth
take, mode by mode, against what they are rated to take, through the workbook's own `workbook/strength.py`, the
warning at a Meshes row and the Results sheet's block.

§5.3's mesh rows B1 to B8 are pinned here through `mesh_strengths` (F4-0's `test_strength.py` works the same rows out
by hand from `checks.check`'s torques; these hold that B's module gives them). Forces to 1e-3 N, shares to 0.1 %."""

from dataclasses import replace
from pathlib import Path

import pytest

from gear_generator.workbook import assess, checks, export, model, strength as mesh, update, xlsx
from gear_generator.workbook.model import Box, Gear, GearboxSpec, Mesh, Shaft
from test_printed_workbook import crossed_pair, printed_desk
from test_strength import idler_train
from test_workbook_planetary import edited, planetary_4to1
from test_workbook_turned import bevel_reducer
from workbook_fixtures import range_box, transfer_case_parallel

FIXTURES = Path(__file__).resolve().parent / "fixtures"
BOOK = "C:\\B\\W.xlsx"
OUT = "C:\\Out\\"
PROVISIONAL = "17 MPa (provisional: type your own in the Box's Allowable stress)"
REMEDY = (" Use a larger module, a wider face, less torque, or your own tested allowable. An estimate for teeth printed "
          "flat, with the whole load on one tooth's tip: not a running rating; heat, wear and creep are not worked out.")


def assessed(spec, process="printed", **box):
    a = assess.assess(replace(spec, box=replace(spec.box, process=process, **box), source_path=BOOK), [], OUT)
    assert [d.message for d in a.diagnostics if d.is_error] == []
    return a


def risky():
    spec, _ = model.from_book(xlsx.read(str(FIXTURES / "excel-windows" / "Risky_Placements.xlsx")))
    return spec


def rows_of(a, name=None, mode=None):
    return [r for r in a.report.strength if (name is None or r.name == name) and (mode is None or r.mode == mode)]


def one(a, name, mode=""):
    found = rows_of(a, name, mode)
    assert len(found) == 1, found
    return found[0]


def held(r, gear):
    return round(r.side(gear).held, 3)


def said(a, kind="Printed, "):
    return [d.message for d in a.report.diagnostics if kind in d.message]


def block(a):
    """The Results sheet's Tooth strength block, from its head to the note."""
    rows = export.results_sheet(a.spec, a.report, when="2026-11-19 00:00").rows
    start = next((i for i, r in enumerate(rows) if r[:1] == ["Tooth strength (printed)"]), None)
    return [] if start is None else rows[start:]


# -- B1 to B8 (§5.3) -------------------------------------------------------------------------------------------------

def test_b1_b2_planetary_4to1_the_members_torque_over_three_planets_with_1_25_the_planet_two_way():
    a = assessed(planetary_4to1())
    sun_planet, planet_ring = one(a, "Sun–Planet"), one(a, "Planet–Ring")
    assert (round(sun_planet.force, 3), round(planet_ring.force, 3)) == (92.593, 88.926)
    assert (held(sun_planet, "Sun"), held(sun_planet, "Planet"), held(planet_ring, "Ring")) == (20.620, 14.434, 29.492)
    assert sun_planet.side("Planet").two_way and not sun_planet.side("Sun").two_way
    assert not planet_ring.side("Ring").two_way                    # held, not a shaft torque of exactly 0
    assert (sun_planet.weaker, planet_ring.weaker, sun_planet.planets) == ("Planet", "Planet", 3)
    assert (round(100 * sun_planet.share, 1), round(100 * planet_ring.share, 1)) == (641.5, 616.1)
    assert sun_planet.width == planet_ring.width == 10.0


@pytest.mark.parametrize("torque, force, share", [("1", 66.667, 230.0), ("0.25", 16.667, 57.5)])
def test_b3_to_b5_the_idler_passes_on_g1s_force_and_is_two_way(torque, force, share):
    a = assessed(idler_train(torque))
    g1_gi, gi_g3 = one(a, "G1–GI"), one(a, "GI–G3")
    assert round(g1_gi.force, 3) == round(gi_g3.force, 3) == force         # B4: G3's own 64.027 is the smaller
    assert (held(g1_gi, "G1"), held(g1_gi, "GI"), held(gi_g3, "G3")) == (38.614, 28.984, 44.485)
    assert g1_gi.side("GI").two_way and gi_g3.weaker == g1_gi.weaker == "GI"
    assert round(100 * g1_gi.share, 1) == round(100 * gi_g3.share, 1) == share
    if torque == "0.25":
        assert said(a) == []                                                # B5: no warning under 100 %


def test_b3_b4_the_idlers_warning_in_full():
    a = assessed(idler_train())
    tail = (f"2.3 times the 29 N GI's teeth are rated to take at {PROVISIONAL}: 41 N once, with an allowance of 0.7 "
            f"because an idler's teeth are loaded in both directions as the gearbox runs.{REMEDY}")
    assert said(a) == [f"Meshes row 2: G1 and GI: Printed, these teeth take about 67 N at the pitch circle, {tail}",
                       f"Meshes row 3: GI and G3: Printed, these teeth take about 67 N at the pitch circle, {tail}"]


def test_b6_b7_rangebox_is_worked_out_in_l_and_turns_unloaded_in_h_and_n():
    a = assessed(range_box())
    low = one(a, "Sun–Planet", "L"), one(a, "Planet–Ring", "L")
    assert [round(r.force, 3) for r in low] == [229.885, 220.782]
    assert (held(low[0], "Sun"), held(low[0], "Planet"), held(low[1], "Ring")) == (32.982, 16.851, 37.989)
    assert round(mesh.once(low[0], low[0].side("Planet"), 17.0), 3) == 24.072
    assert [round(100 * r.share, 1) for r in low] == [1364.3, 1310.2]
    for mode in ("H", "N"):
        assert [r.state for r in rows_of(a, mode=mode)] == [mesh.UNLOADED, mesh.UNLOADED]
        assert all(r.force is None and r.share is None for r in rows_of(a, mode=mode))
    assert [r.mode for r in rows_of(a, "Sun–Planet")] == ["H", "N", "L"]          # each mode's order
    assert said(a)[0] == (
        "Meshes row 2: Sun and Planet: Printed, these teeth take about 230 N at the pitch circle in L, 13.6 times the "
        f"17 N Planet's teeth are rated to take at {PROVISIONAL}: 24 N once, with an allowance of 0.7 because a "
        "planet's teeth are loaded in both directions as the gearbox runs; the load is shared by 3 planets, one taking "
        f"1.25 of an even share.{REMEDY}")


def test_b8_risky_placements_at_the_helical_rings_transverse_diameter_and_the_herringbones_overlap():
    a = assessed(risky())
    want = {"G1–G2": (335.605, 10.0, "G1", 50.670, 56.971, 662.3),
            "G3–G4": (453.154, 12.0, "G3", 62.836, 71.137, 721.2),
            "G5–G6": (723.563, 10.0, "G5", 50.670, 61.823, 1428.0)}
    for name, (force, width, weaker, held_a, held_b, share) in want.items():
        r = one(a, name)
        assert (round(r.force, 3), r.width, r.weaker) == (force, width, weaker)
        assert (round(r.sides[0].held, 3), round(r.sides[1].held, 3)) == (held_a, held_b)
        assert round(100 * r.share, 1) == share
    g6 = one(a, "G5–G6").side("G6").rating
    assert round(g6.d, 4) == 76.6208 and g6.ring and g6.past_range
    placed = a.report.layout.placed["G6"]
    torque = a.report.motion.torques[placed.shaft]
    assert round(2000 * torque / placed.derived.d, 3) == 709.092                   # G6's own side, at d 76.6208
    assert round(2000 * torque / 72.0, 3) != 709.092                               # never at z mn (M2)
    assert "times the 51 N G5's teeth are rated to take once at" in said(a)[2] and " 14.3 times " in said(a)[2]


# -- a ring whose tips lie inside its base circle (M1) ---------------------------------------------------------------

def ring_pair(torque="0.05", ring_teeth="33"):
    """A pinion of 15 teeth in a ring of 33 (module 1, face 10): the ring's tips lie inside its base circle."""
    centre = (int(ring_teeth) - 15) / 2.0
    return GearboxSpec(
        box=Box(name="Ring_Pair", pressure_angle="20", efficiency="98"),
        shafts=(Shaft("In", "frame", f"{centre:g}", "0", "0", "Z+", "input", "", "1000", torque, row=2),
                Shaft("Out", "frame", "0", "0", "0", "Z+", "output", row=3)),
        gears=(Gear("Pin", "In", "0", "spur", "external", "15", "1", "", "10", "", row=2),
               Gear("Ring", "Out", "0", "spur", "internal", ring_teeth, "1", "", "10", "", row=3)),
        meshes=(Mesh("Pin", "Ring", row=2),))


def ring_said():
    """M1's sentence at the row: the ring named, its reason as gears.strength words it (A's, one home), the share
    over Pin alone."""
    from gear_generator.gears import kind_for, strength
    from gear_generator.spec import GearSpec
    ring = GearSpec(kind="spur", teeth_side="internal", teeth="33", module="1", face_width="10", process="printed")
    rating = strength.rate(kind_for(ring).derive(ring))
    assert not rating.rated and "(31.000 mm against 31.010)" in rating.why
    return f"Ring is not rated: {rating.why}; the share counts Pin alone."


def test_a_ring_not_rated_is_named_at_its_meshes_row_with_its_reason_under_100_percent():
    a = assessed(ring_pair())
    r = one(a, "Pin–Ring")
    assert (r.state, r.unrated, r.weaker, r.side("Ring").held) == (mesh.RATED, ("Ring",), "Pin", None)
    assert r.share < 1.0 and round(r.share, 9) == round(r.force / r.side("Pin").held, 9)     # the pinion alone
    assert said(a) == [f"Meshes row 2: Pin and Ring: Printed, {ring_said()}"]
    assert said(a) == [   # F4-REVIEW S1: the sentence as the user reads it, pinned whole
        "Meshes row 2: Pin and Ring: Printed, Ring is not rated: its tips lie inside its base circle (31.000 mm against "
        "31.010), where its teeth cannot be involute, and the rating needs an involute tip to load; the share counts "
        "Pin alone."]


def test_a_ring_not_rated_and_the_pinions_share_past_100_percent_are_one_warning():
    a = assessed(ring_pair("2"))
    r = one(a, "Pin–Ring")
    assert r.share > 1.0
    (sentence,) = said(a)
    assert sentence.startswith("Meshes row 2: Pin and Ring: Printed, these teeth take about ")
    assert sentence.endswith(f"times the {mesh.strength.newtons(r.side('Pin').held)} N Pin's teeth are rated to take "
                             f"once at {PROVISIONAL}. {ring_said()}{REMEDY}")


def test_the_results_name_the_ring_not_rated_and_the_worst_share_row_lists_it():
    a = assessed(ring_pair("2"))
    r = one(a, "Pin–Ring")
    rows = block(a)
    assert rows[1] == ["Pin–Ring", "", round(r.force, 3), "Pin (Ring not rated)", round(r.side("Pin").held, 3),
                       round(100 * r.share, 1)]
    assert rows[2] == ["Worst share", f"Pin–Ring, {100 * r.share:.1f} % (Ring not rated)",
                       "not rated: Ring (tips inside the base circle)"]


def test_a_ring_of_34_teeth_is_rated():
    a = assessed(ring_pair("0.05", "34"))
    r = one(a, "Pin–Ring")
    assert r.unrated == () and r.side("Ring").held is not None and said(a) == []


# -- not worked out: the two wordings, the shared output, a split (S3; the re-check's should-fix) --------------------

def test_the_transfer_case_front_branch_is_not_shared_out_in_4h_and_4l_and_not_driven_in_2h_and_n():
    """F4-REVIEW S2, ruled: the front branch is a free member in 2H and N (its shafts are not in Motion.speeds), so it
    is *not driven here*, never *turns unloaded here*, which is kept for a branch that turns with no load."""
    a = assessed(transfer_case_parallel())
    for name in ("FDrive–FIdler", "FIdler–FOut"):
        assert [(r.mode, r.state) for r in rows_of(a, name)] == [
            ("2H", mesh.UNDRIVEN), ("4H", mesh.NOT_SHARED), ("N", mesh.UNDRIVEN), ("4L", mesh.NOT_SHARED)]    # the low range in 2H, 4H and N: a branch reaching no output (J17's pruning) turns unloaded
    assert [r.state for r in rows_of(a, "LayPin–LoGear")] == [mesh.UNLOADED] * 3 + [mesh.RATED]
    rows = block(a)
    assert ["FDrive–FIdler", "4H", "—", "", "", "the torque past a shared output is not shared out (not worked out)"] \
        in rows
    assert ["FDrive–FIdler", "2H", "—", "", "", "not driven here"] in rows
    assert ["FIdler–FOut", "N", "—", "", "", "not driven here"] in rows
    assert not any(row[0] in ("FDrive–FIdler", "FIdler–FOut") and "turns unloaded here" in row for row in rows)
    assert ["Worst share", "LayPin–LoGear in 4L, 2258.1 %",
            "not worked out: FDrive–FIdler, FIdler–FOut in 4H and 4L (past a shared output)"] in rows
    assert not any("no torque here" in str(cell) for row in rows for cell in row)
    assert [m.split(":")[0] for m in said(a)] == ["Meshes row 2", "Meshes row 3"]  # nothing said of the front branch


def test_rangebox_turns_unloaded_in_h_and_n_on_results():
    rows = block(assessed(range_box()))
    assert rows[1:4] == [["Sun–Planet", "H", "—", "", "", "turns unloaded here"],
                         ["Sun–Planet", "N", "—", "", "", "turns unloaded here"],
                         ["Sun–Planet", "L", 229.885, "Planet", "16.851 (0.7)", 1364.3]]
    assert rows[7] == ["Worst share", "Sun–Planet in L, 1364.3 %"]


def split():
    """W3's split, no modes: In drives G2 on A and G3 on B, both outputs, so kinematics gives no torque past In."""
    return GearboxSpec(
        box=Box(name="Split", pressure_angle="20", efficiency="98"),
        shafts=(Shaft("In", "frame", "0", "0", "0", "Z+", "input", "", "1000", "1", row=2),
                Shaft("A", "frame", "45", "0", "0", "Z+", "output", row=3),
                Shaft("B", "frame", "-45", "0", "0", "Z+", "output", row=4)),
        gears=(Gear("G1", "In", "0", "spur", "external", "20", "1.5", "", "10", "", row=2),
               Gear("G2", "A", "0", "spur", "external", "40", "1.5", "", "10", "", row=3),
               Gear("G3", "B", "0", "spur", "external", "40", "1.5", "", "10", "", row=4)),
        meshes=(Mesh("G1", "G2", row=2), Mesh("G1", "G3", row=3)))


def test_a_shaft_past_a_split_with_no_modes_is_not_worked_out_never_turns_unloaded():
    a = assessed(split())
    assert "A" not in a.report.motion.torques and "A" in a.report.motion.speeds
    assert [r.state for r in a.report.strength] == [mesh.UNWORKED, mesh.UNWORKED]
    rows = block(a)
    assert rows[1] == ["G1–G2", "", "—", "", "", "the torque here is not given (past a split, not worked out)"]
    assert rows[3] == ["Worst share", "—", "not worked out: G1–G2, G1–G3 (its torque is not given)"]
    assert said(a) == []


# -- machined, and no torque: told nothing ---------------------------------------------------------------------------

@pytest.mark.parametrize("make", [range_box, planetary_4to1, risky, idler_train, transfer_case_parallel])
def test_a_machined_gearbox_is_told_nothing_and_its_results_have_no_block(make):
    a = assessed(make(), "machined")
    assert a.report.strength == () and block(a) == [] and said(a) == []
    printed = assessed(make())
    assert [d.message for d in printed.report.diagnostics][:len(a.report.diagnostics)] == \
        [d.message for d in a.report.diagnostics]


def test_a_printed_gearbox_whose_input_has_no_torque_is_told_nothing():
    spec = edited(planetary_4to1(), shafts={"S": dict(torque="")})
    a = assessed(spec)
    assert a.report.strength == () and block(a) == [] and said(a) == []


def test_the_results_block_follows_the_box_size():
    rows = export.results_sheet(*(lambda a: (a.spec, a.report))(assessed(planetary_4to1())), when="X").rows
    head = rows.index(list(mesh.RESULTS_HEAD))
    assert rows[head - 1] == [] and rows[head - 2][0] == "Z"
    assert rows[head + 4:] == [["Allowable stress (MPa)", 17, mesh.ALLOWABLE_BLANK], [mesh.RESULTS_NOTE]]


# -- the allowable ---------------------------------------------------------------------------------------------------

def test_a_typed_allowable_of_34_halves_every_share_and_drops_the_provisional_bracket():
    a = assessed(idler_train(), allowable="34")
    assert round(100 * one(a, "G1–GI").share, 1) == 115.0
    assert said(a)[0] == ("Meshes row 2: G1 and GI: Printed, these teeth take about 67 N at the pitch circle, 1.2 times "
                          "the 58 N GI's teeth are rated to take at 34 MPa: 83 N once, with an allowance of 0.7 because an "
                          f"idler's teeth are loaded in both directions as the gearbox runs.{REMEDY}")
    assert block(a)[-2] == ["Allowable stress (MPa)", 34, "the Box's"]


@pytest.mark.parametrize("typed", ["x", "0", "-5"])
def test_an_allowable_that_does_not_read_leaves_17(typed):
    a = assessed(idler_train(), allowable=typed)
    assert round(100 * one(a, "G1–GI").share, 1) == 230.0 and PROVISIONAL in said(a)[0]
    assert block(a)[-2] == ["Allowable stress (MPa)", 17, mesh.ALLOWABLE_UNREAD]


def test_a_typed_fraction_of_an_allowable_is_shown_as_typed():
    assert block(assessed(idler_train(), allowable="12.5"))[-2] == ["Allowable stress (MPa)", 12.5, "the Box's"]


def test_typing_the_allowable_on_a_built_printed_gearbox_changes_no_part():
    desk = printed_desk()
    spec = replace(range_box(), box=replace(range_box().box, process="printed", allowable="34"))
    up = update.classify(desk.record, desk.a(spec), exists=desk.disk.exists, read_sidecar=desk.disk.read_sidecar)
    assert (up.refusal, up.structural, up.missing) == ("", (), ())
    assert [p.changed for p in up.parts] == [False] * len(desk.record.current_parts())
    assert up.replaced == () and up.moved_shafts == ()


# -- what is not rated: bevel, crossed, couplings --------------------------------------------------------------------

def test_a_bevel_mesh_is_not_rated_on_results_and_the_parallel_stage_after_it_is():
    spec = bevel_reducer()
    spec = replace(spec, meshes=tuple(replace(m, row=r) for r, m in enumerate(spec.meshes, start=2)))
    a = assessed(spec)
    assert [(r.name, r.state) for r in a.report.strength] == [("G1–G2", mesh.BEVEL), ("G3–G4", mesh.RATED)]
    rows = block(a)
    assert rows[1] == ["G1–G2", "", "not rated: a bevel pair"]
    assert rows[3][:2] == ["Worst share", f"G3–G4, {100 * one(a, 'G3–G4').share:.1f} %"]
    assert rows[3][2] == "not rated: G1–G2 (a bevel pair)"


def test_a_crossed_mesh_is_not_rated_on_results():
    a = assessed(crossed_pair(2.0))
    assert [(r.name, r.state) for r in a.report.strength] == [("G1–G2", mesh.CROSSED)]
    assert block(a)[1:3] == [["G1–G2", "", "not rated: a crossed pair"],
                             ["Worst share", "—", "not rated: G1–G2 (a crossed pair)"]]
    assert said(a) == []


def test_a_sleeves_couplings_give_nothing():
    a = assessed(transfer_case_parallel())
    named = {r.name for r in a.report.strength}
    assert named == {"InPin–LayGear", "LayPin–LoGear", "FDrive–FIdler", "FIdler–FOut"}
    assert not any(g in name for name in named for g in ("Slv", "Dog"))


# -- the force rules' other cases -------------------------------------------------------------------------------------

def test_one_planet_takes_the_members_force_whole_with_no_sharing_clause():
    a = assessed(edited(planetary_4to1(), shafts={"P": dict(copies="1")}))
    r = one(a, "Sun–Planet")
    assert r.planets == 1 and round(r.force, 3) == round(2000 * 2 / 18, 3)
    assert "shared by" not in said(a)[0] and "a planet's teeth" in said(a)[0]


def test_a_chain_of_idlers_shares_one_figure():
    """G1 (20) drives GI (25) and GJ (20), two idlers, to G3 (40): every mesh takes G1's 66.667 N."""
    spec = GearboxSpec(
        box=Box(name="Two_Idlers", pressure_angle="20", efficiency="98"),
        shafts=(Shaft("In", "frame", "0", "0", "0", "Z+", "input", "", "1000", "1", row=2),
                Shaft("I1", "frame", "33.75", "0", "0", "Z+", "", row=3),
                Shaft("I2", "frame", "67.5", "0", "0", "Z+", "", row=4),
                Shaft("Out", "frame", "112.5", "0", "0", "Z+", "output", row=5)),
        gears=(Gear("G1", "In", "0", "spur", "external", "20", "1.5", "", "10", "", row=2),
               Gear("GI", "I1", "0", "spur", "external", "25", "1.5", "", "10", "", row=3),
               Gear("GJ", "I2", "0", "spur", "external", "20", "1.5", "", "10", "", row=4),
               Gear("G3", "Out", "0", "spur", "external", "40", "1.5", "", "10", "", row=5)),
        meshes=(Mesh("G1", "GI", row=2), Mesh("GI", "GJ", row=3), Mesh("GJ", "G3", row=4)))
    a = assessed(spec)
    assert a.report.motion.torques["I1"] == a.report.motion.torques["I2"] == 0.0
    assert [round(r.force, 3) for r in a.report.strength] == [66.667] * 3
    middle = one(a, "GI–GJ")
    assert middle.side("GI").two_way and middle.side("GJ").two_way


def test_the_warning_for_a_ring_past_the_stress_factors_range_names_its_fillet():
    from gear_generator.gears import kind_for, strength
    from gear_generator.spec import GearSpec
    ring_spec = GearSpec(kind="spur", teeth_side="internal", teeth="54", module="1", face_width="10",
                         process="printed")
    ring = strength.rate(kind_for(ring_spec).derive(ring_spec))
    assert ring.past_range
    side = mesh.GearSide("Ring", ring, strength.holds(ring, width=10.0))
    row = mesh.MeshStrength("Pin", "Ring", 2, force=100.0, width=10.0, sides=(side,), weaker="Ring",
                            share=100.0 / side.held)
    assert mesh.warning_sentence([row], 17.0, False) == (
        "Printed, these teeth take about 100 N at the pitch circle, 3.4 times the 29 N Ring's teeth (its 0.15 mm fillet "
        "is sharper than the stress factor's range, which is carried past it) are rated to take once at "
        f"{PROVISIONAL}.{REMEDY}")
    assert mesh.results_rows([row], 17.0, False)[1][4] == "29.492 (stress factor past its range)"


def test_nothing_is_said_of_rows_at_or_under_100_percent_and_the_rounding_is_strengths():
    assert mesh.warning_sentence((), 17.0, False) == ""
    a = assessed(idler_train("0.25"))
    assert a.report.strength and said(a) == []
    assert block(a)[1][2] == 16.667 and block(a)[1][5] == 57.5
