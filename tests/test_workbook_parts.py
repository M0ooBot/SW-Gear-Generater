"""W6: the bevel rows of ``build.plan_parts`` (W6-PLAN §2.5.1, D9). Each bevel gear is cut for the one gear it
meshes with and the one shaft angle it meets it at (``geometry.bevel_cuts``); a bevel row that cannot say which is
an error at its cell and is not planned, while every other row still is. (plan_parts' W2 tests are in
test_workbook_build.py.)"""

from gear_generator.workbook import build
from gear_generator.workbook.model import Gear, Mesh, Shaft, replace
from test_workbook_turned import bevel_reducer, crossed_slant

FOLDER = "C:\\Out"


def test_each_bevel_part_is_cut_for_its_partner_and_their_shaft_angle():
    plan = build.plan_parts(bevel_reducer(), FOLDER)
    assert plan.errors == [] and plan.refused == [] and plan.later == []
    jobs = {job.gear_ids: job for job in plan.jobs}
    assert set(jobs) == {("G1",), ("G2",), ("G3",), ("G4",)}
    g1, g2 = jobs[("G1",)].spec, jobs[("G2",)].spec
    assert (g1.mate_teeth, g1.shaft_angle, g2.mate_teeth, g2.shaft_angle) == ("40", "90", "20", "90")
    assert (jobs[("G1",)].stem, jobs[("G2",)].stem) == ("Bevel_m3_N20_M40", "Bevel_m3_N40_M20")
    assert abs(jobs[("G1",)].derived.delta + jobs[("G2",)].derived.delta - 90.0) < 1e-9


def test_a_bevel_pair_at_another_angle_carries_it_in_its_stem():
    plan = build.plan_parts(crossed_slant(), FOLDER)
    jobs = {job.gear_ids: job for job in plan.jobs}
    assert (jobs[("G3",)].spec.mate_teeth, jobs[("G3",)].spec.shaft_angle) == ("30", "120")
    assert jobs[("G3",)].stem.endswith("_M30_S120") and jobs[("G4",)].stem.endswith("_M20_S120")


def test_a_bevel_gear_that_meshes_nothing_or_two_gears_is_an_error_at_its_cell_and_the_rest_are_planned():
    lone = replace(bevel_reducer(), meshes=(Mesh("G3", "G4"),))
    plan = build.plan_parts(lone, FOLDER)
    assert [d.message for d in plan.errors] == [
        "Gears row 0: G1 is a bevel gear that meshes nothing; its shape depends on the gear it meshes with, so list "
        "its mesh on the Meshes sheet.",
        "Gears row 0: G2 is a bevel gear that meshes nothing; its shape depends on the gear it meshes with, so list "
        "its mesh on the Meshes sheet."]
    assert [job.gear_ids for job in plan.jobs] == [("G3",), ("G4",)]

    spec = bevel_reducer()
    two = replace(spec, shafts=spec.shafts + (Shaft("S4", "frame", "0", "60", "60", "Y-", ""),),
                  gears=spec.gears + (Gear("G5", "S4", "0", "bevel", "external", "18", "3", "", "20", "10"),),
                  meshes=spec.meshes + (Mesh("G2", "G5"),))
    plan = build.plan_parts(two, FOLDER)
    messages = [d.message for d in plan.errors]
    assert ("Gears row 0: G2 is a bevel gear listed with G1 (20 teeth) and G5 (18 teeth); a bevel gear is cut for "
            "one mate's tooth count.") in messages
    assert ("G2",) not in [job.gear_ids for job in plan.jobs] and ("G3",) in [job.gear_ids for job in plan.jobs]


def test_the_window_sees_the_same_bevel_checks_without_plans():
    lone = replace(bevel_reducer(), meshes=(Mesh("G3", "G4"),))
    assert [d.message for d in build.gear_diagnostics(lone) if d.is_error] == [
        d.message for d in build.plan_parts(lone, FOLDER).errors]
