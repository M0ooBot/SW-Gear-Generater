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


def test_changes_in_place_to_a_gearbox_not_built_to_turn_are_a_fault_refused_before_anything():
    with pytest.raises(swbuild.BuildError, match="changes to make in place to a gearbox not built to turn"):
        swbuild.update_gearbox(type("Session", (), {"revision": Y26})(), in_place=InPlace(modes_removed=("L",)))


# -- the worker's steps against the fake (tests/test_swbuild.py's, W9c support: delete_component, suppress_feature,
# an insert into a saved assembly, each open document keeping its own configurations) ---------------------------------

from dataclasses import replace  # noqa: E402

from gear_generator import swcom  # noqa: E402
from gear_generator.gears import base as ops  # noqa: E402
from gear_generator.swbuild import (PROBLEM_CONFIGURATION, PROBLEM_MODE_SHOWING, AddedGear, LockLink,  # noqa: E402
                                    MateRef, NewMate, Placement, UserWorkRefused)

from test_swbuild import (IDENTITY9, LOCKS, MATE_REFS, MESHES, P17, P51, T_ASM, TC_ASM, TC_MODES,  # noqa: E402,F401
                          _built_train, _key, _motion, _rot_z, _tc_motion, _train_frames, _train_placements,
                          _update_train, mode_findings, names, tc_built)

WRITES = ("set_global_variable", "add_global_variable", "place_component", "rebuild", "set_mate_suppressed",
          "set_gear_ratio", "save_as", "add_component", "add_mate", "delete_component", "suppress_feature",
          "add_configuration", "delete_configuration", "set_mate_suppressed_in", "set_dimension_in", "fix_component",
          "unfix_component", "link_dimension", "remake_gear_mate", "show_configuration", "new_part")


def _writes(fake):
    return [n for n, _ in fake.calls if n in WRITES]


@pytest.fixture
def measured(monkeypatch):
    """Every W9c gate as if W9c's full build had read it clean on 2026 (the fake's version), and M4 too."""
    _all_measured(monkeypatch)
    monkeypatch.setattr(findings, "EXTERNAL_REFERENCES_READ_ON_2026", True)


G5_AT = (63.75, 51.0, 40.0)
# As the planner makes a follower (G3 locked to G2): its component, its place, its lock to the anchor.
G5_OPS = (ops.AddComponent("gear5", P17, G5_AT), ops.Place("gear5", IDENTITY9, G5_AT),
          ops.Mate("lock5", "lock", "gear4", "gear5", name="G5 locked to G4"))
G5_REFS = (MateRef("G5 locked to G4", "lock", ("G4", "G5")),)
ADD_G5 = AddedGear("G5", "gear5", P17, ops=G5_OPS, handles=(("gear4", "gear4-1"),), refs=G5_REFS)


def _with_g5(**kwargs):
    """The T train's Update with G5 (17 teeth, P17 on record) added behind G4 on S3, locked to it."""
    frames = _train_frames()
    placements = _train_placements(frames) + [Placement("G5", "", IDENTITY9, G5_AT, 360.0 / 17)]
    motion = _motion(locks=LOCKS + (LockLink("G4", "G5", 360.0 / 51),), layout_component="layout-1")
    return dict(placements=placements, motion=motion, **kwargs)


def test_a_gear_added_on_a_shaft_on_record_is_inserted_mated_and_put_with_its_train(measured):
    fake = _built_train()
    result = _update_train(fake, in_place=InPlace(added=(ADD_G5,)), **_with_g5())
    assert result.ok, (result.failures, result.skipped)
    assert result.inserted == [("G5", "gear5-1")]
    assert result.mates_made == [("G5 locked to G4", ())]
    assert "gear5-1" in fake.assembly_names[_key(T_ASM)] and fake.mate("G5 locked to G4", T_ASM).kind == "lock"
    called = names(fake)
    assert called.index("add_component") > called.index("open_document")
    assert T_ASM in result.changed and result.deleted == [] and result.built == []


def test_a_gear_added_is_refused_by_name_while_its_gate_is_not_measured():
    fake = _built_train()
    with pytest.raises(UserWorkRefused) as raised:
        _update_train(fake, in_place=InPlace(added=(ADD_G5,)), **_with_g5())
    assert [(p.kind, p.subjects) for p in raised.value.problems] == [
        (PROBLEM_UNSETTLED, ("UPDATE_INSERTS_A_GEAR_ON_2026",))]
    assert _writes(fake) == []


REMOVE_T_G4 = RemovedGear("G4", "gear4-1", P51, ("G4 on S3 Axis", "G4 along S3", "G3 meshes G4"))


def _without_g4(**kwargs):
    placements = [p for p in _train_placements() if p.gear != "G4"]
    motion = _motion(mates=tuple(m for m in MATE_REFS if "G4" not in m.gears), meshes=MESHES[:1],
                     recorded=tuple(placements), recorded_meshes=MESHES[:1], face_globals=(),
                     layout_component="layout-1")
    return dict(placements=placements, motion=motion, **kwargs)


def test_a_gear_that_anchors_none_is_taken_out_with_its_mates_each_read_gone(measured):
    fake = _built_train()
    result = _update_train(fake, in_place=InPlace(removed=(REMOVE_T_G4,)), **_without_g4())
    assert result.ok, result.log_lines()
    assert result.deleted == [("G4", "gear4-1")] and result.mates_deleted == list(REMOVE_T_G4.mates)
    assert fake.deleted == ["gear4-1"] and not any("G4" in m.name for m in fake.memory_mates[_key(T_ASM)])
    assert T_ASM in result.changed


def test_a_user_mate_on_the_gear_taken_out_refuses_before_any_write(measured):
    fake = _built_train()
    fake.user_component(T_ASM, "Sprocket-1", "C:\\U\\Sprocket.SLDPRT", (IDENTITY9, (63.75, 51.0, 60.0)))
    fake.user_lock(T_ASM, "UserLock1", "gear4-1", "Sprocket-1")
    with pytest.raises(UserWorkRefused) as raised:
        _update_train(fake, in_place=InPlace(removed=(REMOVE_T_G4,)), **_without_g4())
    removed = [p for p in raised.value.problems if p.kind == PROBLEM_REMOVED]
    assert [(p.mates, p.subjects) for p in removed] == [(("UserLock1",), ("G4",))]
    assert _writes(fake) == [] and fake.deleted == []


def test_while_m4_is_unread_any_user_component_refuses_a_removal(measured, monkeypatch):
    monkeypatch.setattr(findings, "EXTERNAL_REFERENCES_READ_ON_2026", None)
    fake = _built_train()
    fake.user_component(T_ASM, "Housing-1", "C:\\U\\Housing.SLDPRT")
    with pytest.raises(UserWorkRefused) as raised:
        _update_train(fake, in_place=InPlace(removed=(REMOVE_T_G4,)), **_without_g4())
    (problem,) = raised.value.problems
    assert problem.kind == PROBLEM_REFERENCES and problem.subjects == ("G4", "Housing-1")
    assert raised.value.user_work.components[0].name == "Housing-1"
    assert _writes(fake) == []


def test_a_gear_that_anchors_another_is_a_fault_never_taken_out(measured):
    fake = _built_train()
    gone = RemovedGear("G2", "gear2-1", "", ("G2 on S2 Axis",))
    with pytest.raises(swbuild.BuildError, match="G2 to take out, which anchors G3"):
        _update_train(fake, in_place=InPlace(removed=(gone,)))
    assert fake.calls == []


# -- with modes: the TransferCase (tests/test_swbuild.py's tc_built, 2H active) ----------------------------------------

HOUSING = "C:\\U\\Housing.SLDPRT"


def _housing(fake, flags=None):
    """The user's housing, held to the layout by a mate of theirs on no app body; ``flags`` per configuration."""
    fake.user_component(TC_ASM, "Housing-1", HOUSING)
    mate = fake.user_mate(TC_ASM, "UserFlush", kind="coincident", a=("Housing-1", "Front Plane"),
                          b=("layout-1", "plane1"))
    if flags:
        mate.flags.update(flags)
        mate.suppressed = mate.flags[fake.config]
    return mate


def _tc_in_place(fake, built, in_place, **changes):
    motion, placements = _tc_motion(built, "2H")
    motion = replace(motion, layout_component="layout-1", **changes)
    return swbuild.update_gearbox(fake, assembly=TC_ASM, placements=placements, motion=motion, exists=fake.exists,
                                  mtime=lambda _p: 0.0, in_place=in_place)


def _with_2l(built):
    """The Modes sheet with a row 2L added after 4L: RangeSlv at 66 (low), ModeSlv at 96 (two-wheel), no coupling
    named for it, so each coupling's on-set leaves it off there."""
    motion, _ = _tc_motion(built, "2H")
    low = dict(motion.mode_placements)["4L"]
    frames = tuple(replace(p, at=(0.0, 0.0, 96.0)) if p.gear == "ModeSlv" else p for p in low)
    return dict(configurations=TC_MODES + ("2L",), mode_placements=motion.mode_placements + (("2L", frames),),
                slide_values=(("RangeSlv along Rear", "2L", 66.0), ("ModeSlv along Rear", "2L", 96.0)))


def test_a_mode_added_is_a_copy_of_the_active_one_set_and_read_back_and_the_users_items_said(tc_built, measured):
    fake, built = tc_built
    _housing(fake)
    result = _tc_in_place(fake, built, InPlace(modes_added=("2L",)), **_with_2l(built))
    assert result.ok, (result.failures, result.skipped)
    assert result.modes_added == ["2L"] and "2L" in fake.configs and fake.config == "2H"
    assert ("RangeSlv engages InDog", "2L") in result.suppressed_in            # on in 2H, off in 2L
    assert ("RangeSlv along Rear", "2L", 66.0) in result.slid and ("ModeSlv along Rear", "2L", 96.0) in result.slid
    assert fake.mate("RangeSlv along Rear", TC_ASM).own["2L"] == 66.0
    assert result.took_active_state == [("2L", "UserFlush", "on"), ("2L", "Housing-1", "resolved")]
    assert [m.name for m in result.modes] == ["4H", "N", "4L", "2L", "2H"]   # every mode put and post-checked
    called = names(fake)
    assert called.index("add_configuration") < called.index("set_mate_suppressed_in")
    assert called[called.index("add_configuration") + 1] == "rebuild"     # a rebuild before any flag


def test_a_mode_whose_name_the_user_already_gave_a_configuration_refuses(tc_built, measured):
    fake, built = tc_built
    fake.configs.append("2L")
    with pytest.raises(UserWorkRefused) as raised:
        _tc_in_place(fake, built, InPlace(modes_added=("2L",)), **_with_2l(built))
    (problem,) = raised.value.problems
    assert problem.kind == PROBLEM_CONFIGURATION and problem.subjects == ("2L", "2L")
    assert _writes(fake) == []


def _without_n(built):
    motion, _ = _tc_motion(built, "2H")
    keep = tuple(m for m in TC_MODES if m != "N")
    return dict(configurations=keep, mode_placements=tuple(x for x in motion.mode_placements if x[0] != "N"),
                recorded_by_mode=tuple(x for x in motion.recorded_by_mode if x[0] != "N"))


def test_a_mode_removed_is_deleted_and_each_user_flag_lost_with_it_said(tc_built, measured):
    fake, built = tc_built
    _housing(fake, flags={"N": True})
    result = _tc_in_place(fake, built, InPlace(modes_removed=("N",)), **_without_n(built))
    assert result.ok, (result.failures, result.skipped)
    assert result.modes_removed == ["N"] and "N" not in fake.configs
    assert result.flags_lost == [("N", "UserFlush", "suppressed")]
    assert [m.name for m in result.modes] == ["4H", "4L", "2H"] and fake.config == "2H"
    called = names(fake)
    assert called.index("delete_configuration") < called.index("show_configuration")


def test_the_mode_showing_is_never_removed(tc_built, measured):
    fake, built = tc_built
    motion, _ = _tc_motion(built, "2H")
    keep = tuple(m for m in TC_MODES if m != "2H")
    with pytest.raises(UserWorkRefused) as raised:
        _tc_in_place(fake, built, InPlace(modes_removed=("2H",)), configurations=keep,
                     mode_placements=tuple(x for x in motion.mode_placements if x[0] != "2H"))
    (problem,) = raised.value.problems
    assert problem.kind == PROBLEM_MODE_SHOWING and problem.subjects == ("2H",)
    assert problem.sentence == ("Update SolidWorks would delete the configuration 2H from TransferCase.SLDASM, and it "
                                "is the configuration showing in SolidWorks, so nothing is changed; show another mode "
                                "in SolidWorks and press Update SolidWorks again.")
    assert _writes(fake) == [] and "2H" in fake.configs


def test_ruling_9_1_a_mode_removed_that_leaves_a_coupling_on_in_no_mode_is_a_fault(tc_built, measured):
    fake, built = tc_built
    motion, _ = _tc_motion(built, "2H")
    keep = tuple(m for m in TC_MODES if m != "4L")                # RangeSlv engages LoDog is on in 4L alone
    with pytest.raises(swbuild.BuildError, match=r"RangeSlv engages LoDog to keep on in no mode .*\(ruling 9.1\)"):
        _tc_in_place(fake, built, InPlace(modes_removed=("4L",)), configurations=keep)
    assert fake.calls == []


def test_ruling_9_1_a_new_coupling_on_in_no_mode_is_a_fault(tc_built, measured):
    fake, built = tc_built
    new = NewMate(ops.Mate("c9", "gear", "gear8:Gear Axis", "gear2:Gear Axis", name="ModeSlv engages InDog"),
                  (("gear8", "gear8-1"), ("gear2", "gear2-1")), (), True)
    with pytest.raises(swbuild.BuildError, match=r"on in no configuration \(ruling 9.1\)"):
        _tc_in_place(fake, built, InPlace(new_mates=(new,)))
    assert fake.calls == []
