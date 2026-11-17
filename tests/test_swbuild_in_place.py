"""W9c package A (ISSUE-1-PLAN K6, §2.4; W9C-INTERFACES.md): Update adds, removes and re-mates in place. This file
holds the shapes' and the pure judgements' tests; the worker's steps are tested beside them as they land."""

import pytest

from gear_generator import findings, swbuild
from gear_generator.gears import base
from gear_generator.swbuild import (PROBLEM_REFERENCES, PROBLEM_REMOVED, PROBLEM_UNREAD, PROBLEM_UNSETTLED, InPlace,
                                    RemovedGear, UserComponent, UserMate, UserWork)

GATES = ("UPDATE_INSERTS_A_GEAR", "UPDATE_MAKES_MATES_WITH_MODES", "UPDATE_BANDS_IN_PLACE", "UPDATE_ADDS_A_MODE",
         "UPDATE_REMOVES_A_MODE")
Y26, Y24 = (34, 1, 1), (32, 5, 0)


def _all_measured(monkeypatch, year=2026):
    for name in GATES:
        monkeypatch.setattr(findings, f"{name}_ON_{year}", True, raising=False)


def _in_place(**kwargs):
    return InPlace(**kwargs)


REMOVE_G4 = RemovedGear("G4", "gear4-1", "C:\\W\\Gear_m1.5_N51.SLDPRT", ("G3 meshes G4", "G4 on S3 Axis",
                                                                        "G4 along S3"))


def test_an_empty_in_place_is_nothing_to_do_and_gates_nothing():
    assert not InPlace() and swbuild.in_place_gates(InPlace(), Y26) == []
    assert swbuild.judge_in_place(UserWork(), InPlace(), revision=Y26) == []
    assert InPlace(modes_removed=("L",))


def test_each_step_reads_its_own_gate_none_on_both_versions_as_committed():
    every = InPlace(added=(swbuild.AddedGear("Hub", "gear9", "C:\\W\\Hub.SLDPRT"),), removed=(REMOVE_G4,),
                    new_mates=(swbuild.NewMate(base.Mate("m1", "gear", "gear7:Gear Axis", "gear2:Gear Axis"),
                                               on=("H",)),),
                    bands=(swbuild.BandChange("RangeSlv", "C:\\W\\Sleeve.SLDPRT", True),),
                    modes_added=("X",), modes_removed=("L",))
    assert swbuild.in_place_gates(every, Y26, modes=True) == [
        (swbuild.STEP_ADD, "UPDATE_INSERTS_A_GEAR_ON_2026"),
        (swbuild.STEP_MATES, "UPDATE_MAKES_MATES_WITH_MODES_ON_2026"),
        (swbuild.STEP_BANDS, "UPDATE_BANDS_IN_PLACE_ON_2026"),
        (swbuild.STEP_MODE_ADD, "UPDATE_ADDS_A_MODE_ON_2026"),
        (swbuild.STEP_MODE_REMOVE, "UPDATE_REMOVES_A_MODE_ON_2026")]       # the delete route is set on 2026
    assert [f for _, f in swbuild.in_place_gates(every, Y24, modes=True)] == [
        "UPDATE_INSERTS_A_GEAR_ON_2024", "UPDATE_MAKES_MATES_WITH_MODES_ON_2024", "UPDATE_BANDS_IN_PLACE_ON_2024",
        "UPDATE_ADDS_A_MODE_ON_2024", "UPDATE_REMOVES_A_MODE_ON_2024"]         # the delete route is set on 2024 too
    assert all(f.endswith("_ON_?") for _, f in swbuild.in_place_gates(every, ()))


def test_a_removal_reads_the_delete_findings_as_measured(monkeypatch):
    monkeypatch.setattr(findings, "COMPONENT_DELETE_ROUTE_ON_2024", None)
    monkeypatch.setattr(findings, "COMPONENT_DELETE_DIALOG_ON_2024", True)
    assert swbuild.in_place_gates(InPlace(removed=(REMOVE_G4,)), Y24, modes=True) == [
        (swbuild.STEP_REMOVE, "COMPONENT_DELETE_ROUTE_ON_2024"), (swbuild.STEP_REMOVE, "COMPONENT_DELETE_DIALOG_ON_2024")]
    assert swbuild.in_place_gates(InPlace(removed=(REMOVE_G4,)), Y26, modes=True) == []


def test_a_remake_reads_the_mates_gate_only_with_modes(monkeypatch):
    assert swbuild.in_place_gates(InPlace(), Y26, modes=True, remakes=True) == [
        (swbuild.STEP_MATES, "UPDATE_MAKES_MATES_WITH_MODES_ON_2026")]
    assert swbuild.in_place_gates(InPlace(), Y26, modes=False, remakes=True) == []
    _all_measured(monkeypatch)
    assert swbuild.in_place_gates(InPlace(), Y26, modes=True, remakes=True) == []


def test_a_gate_not_settled_refuses_by_name():
    (problem,) = swbuild.judge_in_place(UserWork(), InPlace(modes_added=("X",)), file="RangeBox.SLDASM", revision=Y26)
    assert problem.kind == PROBLEM_UNSETTLED and problem.subjects == ("UPDATE_ADDS_A_MODE_ON_2026",)
    assert problem.sentence == ("Update SolidWorks would add a mode's configuration to the assembly, which has not been "
                                "measured on this SolidWorks (findings.UPDATE_ADDS_A_MODE_ON_2026 is None), so nothing "
                                "is changed; build the gearbox again instead.")


def _work(*mates, components=()):
    return UserWork(mates=list(mates), components=list(components))


def test_a_user_mate_on_a_gear_removed_refuses_naming_it_and_the_gear():
    lock = UserMate("UserLock2", swbuild.USER_LOCK, 16, (("app", "G4"), ("user", "Sprocket-2")), ("",))
    other = UserMate("Angle7", swbuild.USER_OTHER, 6, (("app", "G1"), ("layout", "")), ("",))
    off = UserMate("Angle8", swbuild.USER_OTHER, 6, (("app", "G4"), ("layout", "")), ())
    problems = swbuild.judge_in_place(_work(lock, other, off), InPlace(removed=(REMOVE_G4,)),
                                      file="Reducer_12to1.SLDASM", revision=Y26)
    assert [(p.kind, p.mates, p.subjects) for p in problems] == [(PROBLEM_REMOVED, ("UserLock2",), ("G4",))]
    assert problems[0].sentence == (
        "Update SolidWorks would take G4 out of Reducer_12to1.SLDASM, and your UserLock2 is on it, so nothing is "
        "changed; delete or suppress UserLock2 in SolidWorks, or keep G4 in the workbook, and press Update SolidWorks "
        "again.")


def test_while_the_references_read_is_unmeasured_any_user_component_refuses_a_removal(monkeypatch):
    work = _work(components=[UserComponent("Housing-1", "C:\\U\\Housing.SLDPRT"),
                             UserComponent("Sprocket-1", "C:\\U\\Sprocket.SLDPRT")])
    (problem,) = swbuild.judge_in_place(work, InPlace(removed=(REMOVE_G4,)), file="Reducer_12to1.SLDASM",
                                        revision=Y26)
    assert problem.kind == PROBLEM_REFERENCES and problem.subjects == ("G4", "Housing-1", "Sprocket-1")
    assert "(findings.EXTERNAL_REFERENCES_READ_ON_2026 is None)" in problem.sentence
    assert swbuild.judge_in_place(_work(), InPlace(removed=(REMOVE_G4,)), revision=Y26) == []
    monkeypatch.setattr(findings, "EXTERNAL_REFERENCES_READ_ON_2026", True)
    assert swbuild.judge_in_place(work, InPlace(removed=(REMOVE_G4,)), revision=Y26) == []
    assert swbuild.judge_in_place(work, InPlace(modes_added=("X",)), revision=Y24)[0].kind == PROBLEM_UNSETTLED


def test_a_user_mate_not_wholly_read_refuses_a_removal_as_unread():
    unread = UserMate("Mystery1", swbuild.USER_OTHER, 0, (("user", "Sprocket-1"), (swbuild.UNREAD_ENTITY, "")),
                      ("H",), whole=False)
    (problem,) = swbuild.judge_in_place(_work(unread), InPlace(removed=(REMOVE_G4,)), revision=Y26, modes=("H", "L"))
    assert problem.kind == PROBLEM_UNREAD and problem.mates == ("Mystery1",)


def test_the_new_result_fields_start_empty_and_problems_keep_their_subjects():
    result = swbuild.GearboxUpdate()
    for name in ("built", "inserted", "deleted", "mates_deleted", "mates_made", "remade_in_modes", "bands_added",
                 "bands_removed", "modes_added", "modes_removed", "took_active_state", "flags_lost", "not_resolved"):
        assert getattr(result, name) == [], name
    assert swbuild.UserProblem("x", "y").subjects == ()


def test_until_its_steps_land_an_update_given_changes_in_place_refuses_before_anything():
    with pytest.raises(swbuild.BuildError):
        swbuild.update_gearbox(type("Session", (), {"revision": Y26})(), in_place=InPlace(modes_removed=("L",)))
