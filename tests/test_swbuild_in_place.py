"""W9c package A (ISSUE-1-PLAN K6, §2.4; W9C-INTERFACES.md): Update adds, removes and re-mates in place. This file
holds the shapes' and the pure judgements' tests; the worker's steps are tested beside them as they land."""

import pytest

from gear_generator import findings, swbuild
from gear_generator.gears import base
from gear_generator.swbuild import (PROBLEM_REFERENCES, PROBLEM_REMOVED, PROBLEM_UNREAD, PROBLEM_UNSETTLED, InPlace,
                                    RemovedGear, UserComponent, UserMate, UserWork)

GATES = ("UPDATE_INSERTS_A_GEAR", "UPDATE_MAKES_MATES_WITH_MODES", "UPDATE_BANDS_IN_PLACE", "UPDATE_ADDS_A_MODE",
         "UPDATE_REMOVES_A_MODE", "UPDATE_MAKES_A_NEW_COUPLING", "UPDATE_SUPPRESSES_THE_RELIEF")
Y26, Y24 = (34, 1, 1), (32, 5, 0)


def _all_measured(monkeypatch, year=2026):
    for name in GATES:
        monkeypatch.setattr(findings, f"{name}_ON_{year}", True, raising=False)


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
        (swbuild.STEP_COUPLING, "UPDATE_MAKES_A_NEW_COUPLING_ON_2026"),
        (swbuild.STEP_BANDS, "UPDATE_BANDS_IN_PLACE_ON_2026"),
        (swbuild.STEP_MODE_ADD, "UPDATE_ADDS_A_MODE_ON_2026"),
        (swbuild.STEP_MODE_REMOVE, "UPDATE_REMOVES_A_MODE_ON_2026")]       # the delete route is set on 2026
    assert [f for _, f in swbuild.in_place_gates(every, Y24, modes=True)] == [
        "UPDATE_INSERTS_A_GEAR_ON_2024", "UPDATE_MAKES_A_NEW_COUPLING_ON_2024", "UPDATE_BANDS_IN_PLACE_ON_2024",
        "UPDATE_ADDS_A_MODE_ON_2024", "UPDATE_REMOVES_A_MODE_ON_2024"]         # the delete route is set on 2024 too
    # The demonstration's ruling: each gate covers only what it measures.
    assert swbuild.in_place_gates(every, Y26, modes=True, remakes=True)[2] == (
        swbuild.STEP_MATES, "UPDATE_MAKES_MATES_WITH_MODES_ON_2026")             # the remake with modes, apart
    taken = swbuild.BandChange("RangeSlv", "C:\\W\\Sleeve.SLDPRT", False, (), ("Relief",))
    back = swbuild.BandChange("RangeSlv", "C:\\W\\Sleeve.SLDPRT", True, (ops_global(),), ("Relief",), back=True)
    for band in (taken, back):
        assert swbuild.in_place_gates(InPlace(bands=(band,)), Y26) == [
            (swbuild.STEP_RELIEF, "UPDATE_SUPPRESSES_THE_RELIEF_ON_2026")]
    assert [f for _, f in swbuild.in_place_gates(InPlace(added=(swbuild.AddedGear("Hub", "gear9", "C:\\W\\Hub.SLDPRT",
        ops=(base.Mate("m", "gear", "gear9:Gear Axis", "gear2:Gear Axis"),)),)), Y26, modes=True)] == [
        "UPDATE_INSERTS_A_GEAR_ON_2026"]                                          # an added gear's own mates
    assert all(f.endswith("_ON_?") for _, f in swbuild.in_place_gates(every, ()))


def test_a_removal_reads_the_delete_findings_as_measured(monkeypatch):
    monkeypatch.setattr(findings, "COMPONENT_DELETE_ROUTE_ON_2024", None)
    monkeypatch.setattr(findings, "COMPONENT_DELETE_DIALOG_ON_2024", True)
    assert swbuild.in_place_gates(InPlace(removed=(REMOVE_G4,)), Y24, modes=True) == [
        (swbuild.STEP_REMOVE, "COMPONENT_DELETE_ROUTE_ON_2024"),
        (swbuild.STEP_REMOVE, "COMPONENT_DELETE_DIALOG_ON_2024")]
    assert swbuild.in_place_gates(InPlace(removed=(REMOVE_G4,)), Y26, modes=True) == []


def ops_global():
    return base.AddGlobal("Start Band", "5")


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
                          _built_train, _key, _motion, _tc_motion, _train_frames, _train_placements,
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
G5_OPS = (ops.AddComponent("gear5", P17, G5_AT), ops.Place("gear5", IDENTITY9, G5_AT), ops.Fix("gear5"),
          ops.Unfix("gear5"), ops.Mate("lock5", "lock", "gear4", "gear5", name="G5 locked to G4"))
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
    assert "gear5-1" not in fake.fixed                       # fixed as placed, then let go, as the build's plan has it


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


TC_HUB = "C:\\TC\\Hub_m1.5_N30.SLDPRT"
HUB_OPS = (ops.AddComponent("gear10", TC_HUB, (0.0, 0.0, 30.0)), ops.Place("gear10", IDENTITY9, (0.0, 0.0, 30.0)),
           ops.Mate("axis10", "coincident", "gear10:Gear Axis", "layout:Rear Axis", name="Hub on Rear Axis"),
           ops.Mate("along10", "point distance", "gear10:origin", "layout:plane1", 30.0, name="Hub along Rear"),
           ops.Mate("spline10", "gear", "gear7:Gear Axis", "gear10:Gear Axis", name="RangeSlv splined to Hub"))
HUB_REFS = (MateRef("Hub on Rear Axis", "axis", ("Hub",), "Rear"), MateRef("Hub along Rear", "along", ("Hub",), "Rear"),
            MateRef("RangeSlv splined to Hub", "spline", ("RangeSlv", "Hub")))


def _with_hub(built):
    """The worker's side of a hub that becomes its shaft's anchor (J9, motion._sliding_shaft): its part new, its axis
    and along, and RangeSlv's spline to it, on in every mode."""
    from test_swbuild import plan
    motion, placements = _tc_motion(built, "2H")
    hub = Placement("Hub", "", IDENTITY9, (0.0, 0.0, 30.0), 12.0)
    added = AddedGear("Hub", "gear10", TC_HUB, build=plan(path=TC_HUB), ops=HUB_OPS,
                      handles=(("layout", "layout-1"), ("gear7", "gear7-1")),
                      senses=(("RangeSlv splined to Hub", True),), refs=HUB_REFS)
    changes = dict(locks=motion.locks + (LockLink("Hub", "RangeSlv", 12.0),),
                   mode_placements=tuple((m, frames + (hub,)) for m, frames in motion.mode_placements))
    return added, list(placements) + [hub], changes


def test_a_hub_with_its_new_part_is_built_first_inserted_in_the_active_mode_and_on_in_every_mode(tc_built, measured):
    fake, built = tc_built
    added, placements, changes = _with_hub(built)
    motion, _ = _tc_motion(built, "2H")
    result = swbuild.update_gearbox(fake, assembly=TC_ASM, placements=placements,
                                    motion=replace(motion, layout_component="layout-1", **changes), exists=fake.exists,
                                    mtime=lambda _p: 0.0, in_place=InPlace(added=(added,)))
    assert result.ok, (result.failures, result.skipped)
    assert [b.saved for b in result.built] == [TC_HUB] and result.inserted == [("Hub", "gear10-1")]
    assert result.mates_made == [(name, TC_MODES) for name in ("Hub on Rear Axis", "Hub along Rear",
                                                                "RangeSlv splined to Hub")]
    assert all(not f for f in fake.mate("RangeSlv splined to Hub", TC_ASM).flags.values())
    assert result.not_resolved == [] and [m.name for m in result.modes] == ["4H", "N", "4L", "2H"]
    called = names(fake)
    assert called.index("save_as") < called.index("add_component")      # built and saved before the insert
    opened = [a[0] for n, a in fake.calls[:called.index("add_component")] if n == "open_document"]
    assert opened[-2:] == [TC_HUB, TC_ASM]           # the part open, as an insert takes it, then the assembly again


def test_a_component_inserted_that_reads_lightweight_in_a_mode_is_a_failure_with_its_facts(tc_built, measured):
    fake, built = tc_built
    added, placements, changes = _with_hub(built)
    fake.component_states["gear10-1"] = 1
    motion, _ = _tc_motion(built, "2H")
    result = swbuild.update_gearbox(fake, assembly=TC_ASM, placements=placements,
                                    motion=replace(motion, layout_component="layout-1", **changes), exists=fake.exists,
                                    mtime=lambda _p: 0.0, in_place=InPlace(added=(added,)))
    assert not result.ok and result.not_resolved == [("Hub", "2H", 1)]
    assert result.inserted == [("Hub", "gear10-1")]                       # done, and said
    assert "making the mate" not in result.skipped and "putting the gears back" in result.skipped


ENGAGE = NewMate(ops.Mate("c9", "gear", "gear8:Gear Axis", "gear2:Gear Axis", name="ModeSlv engages InDog"),
                 (("gear8", "gear8-1"), ("gear2", "gear2-1")), ("N",), True,
                 MateRef("ModeSlv engages InDog", "couple", ("ModeSlv", "InDog"), modes=("N",)))


def test_a_new_coupling_is_made_in_the_first_mode_it_is_on_in_with_its_flag_set_in_every_mode(tc_built, measured):
    fake, built = tc_built
    motion, _ = _tc_motion(built, "2H")
    link = swbuild.MeshLink("ModeSlv", "InDog", 1.0, 12.0, modes=("N",))
    result = _tc_in_place(fake, built, InPlace(new_mates=(ENGAGE,)), meshes=motion.meshes + (link,))
    assert result.ok, (result.failures, result.skipped)
    assert result.mates_made == [("ModeSlv engages InDog", ("N",))]
    assert fake.mate("ModeSlv engages InDog", TC_ASM).flags == {"2H": True, "4H": True, "N": False, "4L": True}
    called = fake.calls
    made = next(i for i, (n, _) in enumerate(called) if n == "add_mate")
    shown = [a[0] for n, a in called[:made] if n == "show_configuration"]
    assert shown == ["N"] and fake.config == "2H"


# -- a tooth change on a gearbox with modes (lifting ruling 9.16 behind its gate) -------------------------------------

@pytest.fixture
def t_with_modes(mode_findings, monkeypatch):
    """The 12 : 1 with a second configuration L beside Default, both modes, the remake's findings as measured."""
    for name, value in (("GEAR_MATE_RATIO_ROUTE", "remake"), ("GEAR_MATE_RATIO_REMAKE_WORKS", True),
                        ("GEAR_MATE_DEFINITION_READS_NUMERATOR_SECOND", True)):
        monkeypatch.setattr(findings, name, value, raising=False)
    fake = _built_train()
    fake.open_document(T_ASM)
    fake.add_configuration("L")
    fake.rebuild(kind=swcom.ASSEMBLY_TRAIN)
    fake.show_configuration("Default")
    fake.calls.clear()
    return fake


def test_a_tooth_change_with_modes_is_refused_by_name_until_its_gate_is_measured(t_with_modes):
    """As every gate: a UserWorkRefused with the finding as its subject, the user's work read, so the refusal is
    recorded and said after the press as the footer foresaw it (B's second joining round)."""
    fake = t_with_modes
    with pytest.raises(UserWorkRefused) as raised:
        _update_train(fake, motion=_motion(configurations=("Default", "L"), ratios=(("G3 meshes G4", 18, 50),)))
    (problem,) = raised.value.problems
    assert problem.kind == PROBLEM_UNSETTLED and problem.subjects == ("UPDATE_MAKES_MATES_WITH_MODES_ON_2026",)
    assert problem.sentence == ("Update SolidWorks would make a gear mate of a gearbox with modes again and set its "
                                "flag in each mode, which has not been measured on this SolidWorks (findings."
                                "UPDATE_MAKES_MATES_WITH_MODES_ON_2026 is None), so nothing is changed; build the "
                                "gearbox again instead.")
    assert raised.value.user_work is not None and _writes(fake) == []
    assert swbuild.in_place_gates(InPlace(), Y26, modes=True, remakes=True)[0][1] == \
        "UPDATE_MAKES_MATES_WITH_MODES_ON_2026"                         # the footer foresees it the same way


def test_a_tooth_change_with_modes_is_remade_in_a_mode_and_read_back_in_every_configuration(t_with_modes, measured):
    fake = t_with_modes
    result = _update_train(fake, motion=_motion(configurations=("Default", "L"), ratios=(("G3 meshes G4", 18, 50),)))
    assert result.ok, (result.failures, result.skipped)
    assert result.remade_in_modes == ["G3 meshes G4"] and result.ratios == ["G3 meshes G4"]
    mate = fake.mate("G3 meshes G4", T_ASM)
    assert mate.ratio == (18.0, 50.0) and mate.flags == {"Default": False, "L": False}
    assert [m.name for m in result.modes] == ["L", "Default"] and result.senses_unread == []


# -- bands in place (§2.4; ruling C8) ---------------------------------------------------------------------------------

from gear_generator.gears import clutch  # noqa: E402

RELIEF_FEATURES = (clutch.RELIEF_START_PLANE, clutch.RELIEF_END_PLANE, clutch.RELIEF_START_SKETCH,
                   clutch.RELIEF_END_SKETCH, clutch.RELIEF)


def _p17(made_extra=()):
    from test_swbuild import S17, _values, plan
    made = tuple(swbuild.plan_features(plan(S17, path=P17))) + tuple(made_extra)
    return swbuild.DocumentValues(P17, _values(S17), made=made)


def _bands_given():
    globals_ = [ops.AddGlobal(v.name, v.expression) for v in clutch.relief_globals((3.0, 2.0))]
    return swbuild.BandChange("G3", P17, True, tuple(globals_) + tuple(clutch.relief_ops(10.0, (3.0, 2.0), 28.5)),
                              RELIEF_FEATURES)


def test_bands_given_in_place_land_after_the_users_feature_which_is_kept(measured):
    fake = _built_train()
    fake.user_feature(P17, "Groove")
    result = _update_train(fake, parts=[_p17(RELIEF_FEATURES)], in_place=InPlace(bands=(_bands_given(),)))
    assert result.ok, (result.failures, result.skipped)
    assert result.bands_added == ["G3"] and P17 in result.changed
    assert result.globals_added == [(P17, "Start Band"), (P17, "End Band"), (P17, "Relief Diameter")]   # for left
    held = fake.memory[_key(P17)][1]
    assert held[-len(RELIEF_FEATURES):] == list(RELIEF_FEATURES)
    assert [f.name for f in result.user_work.features] == ["Groove"] and fake.user_features[_key(P17)] == [
        ("Groove", "ICE")]
    assert any(v.startswith('"Start Band"') for v in fake.memory[_key(P17)][0])
    called = names(fake)
    assert called.index("loft_cut") < called.index("open_document", called.index("loft_cut"))   # before the assembly
    assert "save_as" not in called                                      # an Update saves nothing


def test_bands_taken_away_in_place_suppress_the_relief_and_keep_the_users_feature(measured):
    fake = _built_train()
    for kept in (fake.saved, fake.memory):                     # bands given before, so the relief is in the part
        kept[_key(P17)][1].extend(f for f in RELIEF_FEATURES if f not in kept[_key(P17)][1])
    fake.user_feature(P17, "Groove")
    taken = swbuild.BandChange("G3", P17, False, (), (clutch.RELIEF,))
    result = _update_train(fake, parts=[_p17(RELIEF_FEATURES)], in_place=InPlace(bands=(taken,)))
    assert result.ok, (result.failures, result.skipped)
    assert result.bands_removed == ["G3"] and fake.suppressed_features == {(_key(P17), clutch.RELIEF): True}
    assert fake.user_features[_key(P17)] == [("Groove", "ICE")]


def test_bands_on_a_part_that_fails_stop_the_job_before_the_assembly_saying_so(measured):
    fake = _built_train(fail_on={"loft_cut": "SolidWorks would not make the loft cut Relief."})
    result = _update_train(fake, parts=[_p17(RELIEF_FEATURES)], in_place=InPlace(bands=(_bands_given(),)))
    assert not result.ok and result.bands_added == []
    assert result.failures[0][0] == "Gear_m1.5_N17.SLDPRT" and "Relief" in result.failures[0][1]
    assert result.skipped == "the assembly, because Gear_m1.5_N17.SLDPRT failed"
    assert "add_component" not in names(fake) and T_ASM not in result.changed


# -- every gate None refuses before any write, by name ---------------------------------------------------------------

@pytest.mark.parametrize("gate, step", [("UPDATE_ADDS_A_MODE", "add"), ("UPDATE_REMOVES_A_MODE", "remove"),
                                         ("UPDATE_MAKES_A_NEW_COUPLING", "mate")])
def test_with_modes_each_gate_not_measured_refuses_before_any_write_naming_its_finding(tc_built, measured, monkeypatch,
                                                                                      gate, step):
    monkeypatch.setattr(findings, f"{gate}_ON_2026", None)
    fake, built = tc_built
    motion, _ = _tc_motion(built, "2H")
    if step == "add":
        in_place, changes = InPlace(modes_added=("2L",)), _with_2l(built)
    elif step == "remove":
        in_place, changes = InPlace(modes_removed=("N",)), _without_n(built)
    else:
        link = swbuild.MeshLink("ModeSlv", "InDog", 1.0, 12.0, modes=("N",))
        in_place, changes = InPlace(new_mates=(ENGAGE,)), dict(meshes=motion.meshes + (link,))
    with pytest.raises(UserWorkRefused) as raised:
        _tc_in_place(fake, built, in_place, **changes)
    assert [(p.kind, p.subjects) for p in raised.value.problems] == [(PROBLEM_UNSETTLED, (f"{gate}_ON_2026",))]
    assert f"(findings.{gate}_ON_2026 is None)" in raised.value.problems[0].sentence
    assert _writes(fake) == []


def test_bands_refuse_before_any_write_while_their_gate_is_not_measured():
    fake = _built_train()
    with pytest.raises(UserWorkRefused) as raised:
        _update_train(fake, parts=[_p17(RELIEF_FEATURES)], in_place=InPlace(bands=(_bands_given(),)))
    assert [p.subjects for p in raised.value.problems] == [("UPDATE_BANDS_IN_PLACE_ON_2026",)]
    assert _writes(fake) == []


def test_on_2024_a_removal_reads_only_its_update_gates_none_while_the_delete_route_is_set(measured, monkeypatch):
    fake = _built_train()
    fake.revision = (32, 5, 0)
    monkeypatch.setattr(findings, "EXTERNAL_REFERENCES_READ_ON_2024", True)
    result = _update_train(fake, in_place=InPlace(removed=(REMOVE_T_G4,)), **_without_g4())
    assert result.ok and result.deleted == [("G4", "gear4-1")]                  # P1 read the same on 2024


# -- a failure half-way says exactly what was and was not done -------------------------------------------------------

def test_a_failure_half_way_says_what_was_done_and_what_was_not(tc_built, measured):
    fake, built = tc_built
    fake.raises = {"add_configuration": (fake.counts.get("add_configuration", 0) + 1,
                                         swcom.SolidWorksError("SolidWorks would not add the configuration 2L."))}
    changes = _with_2l(built)
    changes["configurations"] = tuple(m for m in changes["configurations"] if m != "N")
    changes["mode_placements"] = tuple(x for x in changes["mode_placements"] if x[0] != "N")
    result = _tc_in_place(fake, built, InPlace(modes_removed=("N",), modes_added=("2L",)), **changes)
    assert not result.ok
    assert result.modes_removed == ["N"] and result.modes_added == []
    assert result.failures == [("TransferCase.SLDASM", "SolidWorks would not add the configuration 2L.")]
    assert result.skipped == ("adding the configuration 2L and putting the gears back and checking the assembly, "
                              "because the job stopped in TransferCase.SLDASM")
    assert TC_ASM in result.changed and fake.config == "2H"


# -- nothing of the user's is written (W9a's fake fails a test on any write to a user item) ----------------------------

def test_nothing_of_the_users_is_written_while_a_gear_is_inserted_and_a_mode_added(tc_built, measured):
    fake, built = tc_built
    _housing(fake)
    fake.user_component(TC_ASM, "Sprocket-9", "C:\\U\\Sprocket.SLDPRT", (IDENTITY9, (0.0, 0.0, 200.0)))
    fake.user_lock(TC_ASM, "UserLock9", "Housing-1", "Sprocket-9")
    added, placements, changes = _with_hub(built)
    two_l = _with_2l(built)
    hub = placements[-1]
    two_l["mode_placements"] = tuple((m, frames + ((hub,) if m == "2L" else ()))
                                     for m, frames in two_l["mode_placements"])
    changes.update(configurations=two_l["configurations"], slide_values=two_l["slide_values"],
                   mode_placements=tuple((m, f + ((hub,) if m != "2L" else ())) for m, f in two_l["mode_placements"]))
    motion, _ = _tc_motion(built, "2H")
    result = swbuild.update_gearbox(fake, assembly=TC_ASM, placements=placements,
                                    motion=replace(motion, layout_component="layout-1", **changes), exists=fake.exists,
                                    mtime=lambda _p: 0.0, in_place=InPlace(added=(added,), modes_added=("2L",)))
    assert result.ok, (result.failures, result.skipped)
    assert fake.user_puts == [] and {"UserFlush", "UserLock9"} <= {m.name for m in fake.memory_mates[_key(TC_ASM)]}
    assert result.mates_made == [(name, TC_MODES + ("2L",)) for name in ("Hub on Rear Axis", "Hub along Rear",
                                                                          "RangeSlv splined to Hub")]


def test_a_failure_in_another_mode_shows_the_active_mode_again(tc_built, measured):
    fake, built = tc_built
    motion, _ = _tc_motion(built, "2H")
    link = swbuild.MeshLink("ModeSlv", "InDog", 1.0, 12.0, modes=("N",))
    fake.fail_on = {"add_mate": "SolidWorks would not make the mate ModeSlv engages InDog."}
    result = _tc_in_place(fake, built, InPlace(new_mates=(ENGAGE,)), meshes=motion.meshes + (link,))
    assert result.failures == [("TransferCase.SLDASM", "SolidWorks would not make the mate ModeSlv engages InDog.")]
    assert result.mates_made == [] and fake.config == "2H"
    assert result.skipped.startswith("making the mate ModeSlv engages InDog and putting the gears back")


def test_the_log_says_what_was_made_and_taken_away_in_place(tc_built, measured):
    fake, built = tc_built
    _housing(fake, flags={"N": True})
    result = _tc_in_place(fake, built, InPlace(modes_removed=("N",)), **_without_n(built))
    lines = result.log_lines()
    assert "ok      configurations deleted: N" in lines
    assert "CHECK   your UserFlush was suppressed in N, deleted with it" in lines
    fake = _built_train()
    lines = _update_train(fake, in_place=InPlace(added=(ADD_G5,)), **_with_g5()).log_lines()
    assert "ok      inserted G5 as gear5-1" in lines and "ok      made G5 locked to G4" in lines


def test_with_modes_a_gear_taken_out_is_gone_from_every_mode_with_its_per_mode_coupling(tc_built, measured):
    fake, built = tc_built
    motion, placements = _tc_motion(built, "2H")
    gone = RemovedGear("FrontDog", "gear9-1", "C:\\TC\\Dog_m1.5_N30.SLDPRT",
                       ("FrontDog on Rear Axis", "FrontDog along Rear", "ModeSlv engages FrontDog"))
    keep = lambda frames: tuple(p for p in frames if p.gear != "FrontDog")         # noqa: E731
    result = swbuild.update_gearbox(
        fake, assembly=TC_ASM, placements=list(keep(placements)), exists=fake.exists, mtime=lambda _p: 0.0,
        motion=replace(motion, layout_component="layout-1", mates=tuple(m for m in motion.mates
                                                                        if m.name not in gone.mates),
                       meshes=tuple(m for m in motion.meshes if "FrontDog" not in (m.a, m.b)),
                       recorded_meshes=tuple(m for m in motion.recorded_meshes if "FrontDog" not in (m.a, m.b)),
                       recorded=keep(motion.recorded),
                       mode_placements=tuple((m, keep(f)) for m, f in motion.mode_placements),
                       recorded_by_mode=tuple((m, keep(f)) for m, f in motion.recorded_by_mode)),
        in_place=InPlace(removed=(gone,)))
    assert result.ok, (result.failures, result.skipped)
    assert result.deleted == [("FrontDog", "gear9-1")] and result.mates_deleted == list(gone.mates)
    assert [m.name for m in result.modes] == ["4H", "N", "4L", "2H"]
    for mode in TC_MODES:
        fake.show_configuration(mode)
        assert "gear9-1" not in fake.frames and fake.mate("ModeSlv engages FrontDog", TC_ASM) is None


# -- the joining round's faults (W9C-INTERFACES §11, From B): F2 the puts judged, F1 what a stopped press left, F3 ----

from test_swbuild import _drag  # noqa: E402
from test_swbuild_user_work import _tc_sprocket  # noqa: E402

SPROCKET = "C:\\U\\Sprocket.SLDPRT"


@pytest.fixture
def carry(monkeypatch):
    """Route (c1) on a train with no carrier, with modes and without, as if read clean (as W9a's tests set it)."""
    for year in (2026, 2024):
        monkeypatch.setattr(findings, f"USER_MATE_PUT_NO_CARRIER_ON_{year}", True, raising=False)
        monkeypatch.setattr(findings, f"USER_MATE_PUT_NO_CARRIER_MODES_ON_{year}", True, raising=False)


@pytest.mark.parametrize("change", ["added", "removed"])
def test_f2_a_mode_added_or_removed_carries_the_users_locked_component_in_every_mode_put(tc_built, measured, carry,
                                                                                       change):
    """F2: only modes change, so the check sees nothing moved, yet the change phase puts every train in every mode:
    the check judges those puts, and the user's sprocket locked to RangeSlv goes with it in each, the added mode too
    (judged as the mode it copies), never stopped half way."""
    fake, built = tc_built
    _tc_sprocket(fake)
    if change == "added":
        result = _tc_in_place(fake, built, InPlace(modes_added=("2L",)), **_with_2l(built))
        modes = ["4H", "N", "4L", "2L", "2H"]
    else:
        result = _tc_in_place(fake, built, InPlace(modes_removed=("N",)), **_without_n(built))
        modes = ["4H", "4L", "2H"]
    assert result.ok, (result.failures, result.skipped)
    assert [(c, g, m) for c, g, m in result.carried] == [("Sprocket-2", "RangeSlv", m) for m in modes]


def test_f2_a_users_mate_on_a_body_a_mode_change_will_put_refuses_before_any_write(tc_built, measured, carry):
    fake, built = tc_built
    fake.user_component(TC_ASM, "Sprocket-2", SPROCKET, (IDENTITY9, (0.0, 0.0, 300.0)))
    fake.user_mate(TC_ASM, "UserAngle", kind="angle", a=("gear7-1", "plane2"), b=("Sprocket-2", "Front Plane"))
    with pytest.raises(UserWorkRefused) as raised:
        _tc_in_place(fake, built, InPlace(modes_added=("2L",)), **_with_2l(built))
    assert [p.mates for p in raised.value.problems] == [("UserAngle",)]
    assert _writes(fake) == [] and "2L" not in fake.configs


def test_f2_a_mode_added_is_judged_as_the_mode_it_copies(tc_built):
    lock = UserMate("UserLock2", swbuild.USER_LOCK, 16, (("app", "RangeSlv"), ("user", "Sprocket-2")), ("2H", "4H"))
    work = swbuild.work_in_added_modes(UserWork(mates=[lock]), ("2L",), "2H")
    assert work.mates[0].on == ("2H", "4H", "2L") and lock.on == ("2H", "4H")
    assert swbuild.work_in_added_modes(UserWork(mates=[lock]), ("2L",), "N").mates[0].on == ("2H", "4H")


def test_f2_without_modes_a_train_that_gains_a_gear_out_of_step_is_judged_put_and_carries_the_users_part(measured,
                                                                                                        carry):
    """The user turned the 12 : 1 in step; G5 goes in at its built turn, so G4's train is out of step once it is in
    and is put whole: the check judges that put, and the sprocket locked to G4 goes with it."""
    fake = _built_train()
    _drag(fake, 10.0)
    fake.user_component(T_ASM, "Sprocket-1", SPROCKET, (fake.frames["gear4-1"][0], (63.75, 51.0, 60.0)))
    fake.user_lock(T_ASM, "UserLock1", "gear4-1", "Sprocket-1")
    result = _update_train(fake, in_place=InPlace(added=(ADD_G5,)), **_with_g5())
    assert result.ok, (result.failures, result.skipped)
    assert "G4" in result.placed and [c for c, _, _ in result.carried] == ["Sprocket-1"]


def test_f2_without_modes_a_users_mate_on_a_train_that_gains_a_gear_refuses_before_any_write(measured, carry):
    fake = _built_train()
    _drag(fake, 10.0)
    fake.user_component(T_ASM, "Sprocket-1", SPROCKET, (IDENTITY9, (63.75, 51.0, 60.0)))
    fake.user_mate(T_ASM, "UserAngle", kind="angle", a=("gear4-1", "plane2"), b=("Sprocket-1", "Front Plane"))
    with pytest.raises(UserWorkRefused) as raised:
        _update_train(fake, in_place=InPlace(added=(ADD_G5,)), **_with_g5())
    assert [p.mates for p in raised.value.problems] == [("UserAngle",)]
    assert _writes(fake) == []


G5_FACE = ops.AddGlobal("G5 Face Z", "40")
ADD_G5_FACE = replace(ADD_G5, ops=(G5_FACE,) + G5_OPS)


def _t_global(fake, expression):
    fake.open_document(T_ASM)
    fake.add_global_variable("G5 Face Z", expression)
    fake.calls.clear()


@pytest.mark.parametrize("held, left, done", [(None, (), "added"), ("40", (), "done"), ("35", ("G5 Face Z",), "set")])
def test_f1_an_assembly_global_a_stopped_press_left_is_taken_as_done_or_set(measured, held, left, done):
    fake = _built_train()
    if held is not None:
        _t_global(fake, held)
    result = _update_train(fake, in_place=InPlace(added=(ADD_G5_FACE,), left=left), **_with_g5())
    assert result.ok, (result.failures, result.skipped)
    called = [(n, a) for n, a in fake.calls if n in ("add_global_variable", "set_global_variable")]
    assert called == {"added": [("add_global_variable", ("G5 Face Z", "40"))], "done": [],
                      "set": [("set_global_variable", ("G5 Face Z", "40"))]}[done]
    assert result.globals_added == ([(T_ASM, "G5 Face Z")] if done == "added" else [])


def test_f1_a_global_of_the_users_by_that_name_refuses_by_name_before_any_write(measured):
    fake = _built_train()
    _t_global(fake, "35")
    with pytest.raises(UserWorkRefused) as raised:
        _update_train(fake, in_place=InPlace(added=(ADD_G5_FACE,)), **_with_g5())
    (problem,) = raised.value.problems
    assert problem.kind == swbuild.PROBLEM_GLOBAL and problem.subjects == ("G5 Face Z", "T.SLDASM")
    assert problem.sentence == ('T.SLDASM already holds a global "G5 Face Z" = 35 that Gear Generator did not add, '
                                'where Update SolidWorks would add it as 40, so nothing is changed; rename or delete '
                                '"G5 Face Z" in SolidWorks and press Update SolidWorks again.')
    assert _writes(fake) == []


def test_f1_a_configuration_a_stopped_press_added_is_gone_on_from(tc_built, measured):
    fake, built = tc_built
    fake.add_configuration("2L")
    fake.rebuild(kind=swcom.ASSEMBLY_TRAIN)
    fake.show_configuration("2H")
    fake.calls.clear()
    result = _tc_in_place(fake, built, InPlace(modes_added=("2L",), left=("2L",)), **_with_2l(built))
    assert result.ok, (result.failures, result.skipped)
    assert "add_configuration" not in names(fake) and result.modes_added == ["2L"]
    assert ("RangeSlv along Rear", "2L", 66.0) in result.slid


def test_f1_band_globals_left_at_their_values_are_done_and_a_relief_left_refuses_by_name(measured):
    fake = _built_train()
    fake.open_document(P17)
    for v in clutch.relief_globals((3.0, 2.0)):
        fake.add_global_variable(v.name, v.expression)
    fake.calls.clear()
    result = _update_train(fake, parts=[_p17(RELIEF_FEATURES)], in_place=InPlace(bands=(_bands_given(),)))
    assert result.ok, (result.failures, result.skipped)
    assert "add_global_variable" not in names(fake) and result.bands_added == ["G3"]
    fake = _built_train()
    fake.open_document(P17)
    fake.made.append(clutch.RELIEF_START_PLANE)
    fake.calls.clear()
    with pytest.raises(swbuild.BuildError, match="already holds Relief Start Plane, the relief of bands an Update"):
        _update_train(fake, parts=[_p17(RELIEF_FEATURES)], in_place=InPlace(bands=(_bands_given(),)))
    assert _writes(fake) == []


def test_f3_skipped_names_only_what_was_not_done_at_the_results_grain(tc_built, measured):
    fake, built = tc_built
    added, placements, changes = _with_hub(built)
    motion, _ = _tc_motion(built, "2H")
    fake.fail_on = {"add_mate": "SolidWorks would not make the mate Hub on Rear Axis."}
    result = swbuild.update_gearbox(fake, assembly=TC_ASM, placements=placements,
                                    motion=replace(motion, layout_component="layout-1", **changes), exists=fake.exists,
                                    mtime=lambda _p: 0.0, in_place=InPlace(added=(added,)))
    assert result.inserted == [("Hub", "gear10-1")]
    assert result.skipped == ("making Hub's mates and putting the gears back and checking the assembly, because the "
                              "job stopped in TransferCase.SLDASM")


def test_f3_a_flag_that_fails_after_the_mates_are_made_names_what_is_left(tc_built, measured):
    fake, built = tc_built
    added, placements, changes = _with_hub(built)
    motion, _ = _tc_motion(built, "2H")
    added = replace(added, on_sets=(("RangeSlv splined to Hub", ("2H", "4H")),))     # so a flag must be set
    fake.fail_on = {"set_mate_suppressed_in": "SolidWorks would not set the flag."}
    result = swbuild.update_gearbox(fake, assembly=TC_ASM, placements=placements,
                                    motion=replace(motion, layout_component="layout-1", **changes), exists=fake.exists,
                                    mtime=lambda _p: 0.0, in_place=InPlace(added=(added,)))
    assert not result.ok and "inserting Hub" not in result.skipped and "making Hub's mates" not in result.skipped
    assert result.skipped.startswith("setting Hub's mates on in their modes and reading Hub back and putting")
    assert {n for n, _ in result.mates_made} == {"Hub on Rear Axis", "Hub along Rear", "RangeSlv splined to Hub"}


# -- the demonstration's ruling: the relief's suppression has its own gate; bands given back turn it back on ----------

def test_bands_taken_away_refuse_by_their_own_gate_while_bands_given_are_measured(measured, monkeypatch):
    monkeypatch.setattr(findings, "UPDATE_SUPPRESSES_THE_RELIEF_ON_2026", None)
    fake = _built_train()
    for kept in (fake.saved, fake.memory):
        kept[_key(P17)][1].extend(f for f in RELIEF_FEATURES if f not in kept[_key(P17)][1])
    taken = swbuild.BandChange("G3", P17, False, (), (clutch.RELIEF,))
    with pytest.raises(UserWorkRefused) as raised:
        _update_train(fake, parts=[_p17(RELIEF_FEATURES)], in_place=InPlace(bands=(taken,)))
    assert [p.subjects for p in raised.value.problems] == [("UPDATE_SUPPRESSES_THE_RELIEF_ON_2026",)]
    assert _writes(fake) == []


def test_bands_given_back_turn_the_relief_back_on_and_set_the_globals_making_no_second_relief(measured):
    fake = _built_train()
    fake.open_document(P17)
    fake.made.extend(RELIEF_FEATURES)
    for v in clutch.relief_globals((4.0, 4.0)):                      # the first bands' values, before they were taken
        fake.add_global_variable(v.name, v.expression)
    fake.suppressed_features[(_key(P17), clutch.RELIEF)] = True
    fake.calls.clear()
    back = replace(_bands_given(), back=True)
    result = _update_train(fake, parts=[_p17(RELIEF_FEATURES)], in_place=InPlace(bands=(back,)))
    assert result.ok, (result.failures, result.skipped)
    assert result.bands_added == ["G3"] and fake.suppressed_features[(_key(P17), clutch.RELIEF)] is False
    called = names(fake)
    assert "loft_cut" not in called and "ref_plane" not in called and "add_global_variable" not in called
    assert [a[0] for n, a in fake.calls if n == "set_global_variable"] == ["Start Band", "End Band"]
    assert fake.memory[_key(P17)][1].count(clutch.RELIEF) == 1


def test_bands_given_back_where_the_relief_is_gone_refuse_by_name(measured):
    fake = _built_train()
    with pytest.raises(swbuild.BuildError, match="no longer holds Relief Start Plane, .*the relief an earlier Update"):
        _update_train(fake, parts=[_p17(RELIEF_FEATURES)],
                      in_place=InPlace(bands=(replace(_bands_given(), back=True),)))
    assert _writes(fake) == []


# -- the review's should-fix 6: a failure at each write not yet pinned, and what the next press finds ---------------

def _fail_next(fake, call, sentence):
    fake.raises = {call: (fake.counts.get(call, 0) + 1, swcom.SolidWorksError(sentence))}


def test_a_configuration_that_will_not_delete_says_so_and_the_next_press_deletes_it(tc_built, measured):
    fake, built = tc_built
    _fail_next(fake, "delete_configuration", "SolidWorks would not delete the configuration N.")
    result = _tc_in_place(fake, built, InPlace(modes_removed=("N",)), **_without_n(built))
    assert result.failures == [("TransferCase.SLDASM", "SolidWorks would not delete the configuration N.")]
    assert result.modes_removed == [] and result.globals_added == [] and "N" in fake.configs
    assert result.skipped == ("deleting the configuration N and putting the gears back and checking the assembly, "
                              "because the job stopped in TransferCase.SLDASM")
    assert fake.config == "2H"
    again = _tc_in_place(fake, built, InPlace(modes_removed=("N",)), **_without_n(built))
    assert again.ok and again.modes_removed == ["N"] and "N" not in fake.configs


def _without_front_dog(built, **more):
    motion, placements = _tc_motion(built, "2H")
    gone = RemovedGear("FrontDog", "gear9-1", "C:\\TC\\Dog_m1.5_N30.SLDPRT",
                       ("FrontDog on Rear Axis", "FrontDog along Rear", "ModeSlv engages FrontDog"))
    keep = lambda frames: tuple(p for p in frames if p.gear != "FrontDog")         # noqa: E731
    motion = replace(motion, layout_component="layout-1",
                     mates=tuple(m for m in motion.mates if m.name not in gone.mates),
                     meshes=tuple(m for m in motion.meshes if "FrontDog" not in (m.a, m.b)),
                     recorded_meshes=tuple(m for m in motion.recorded_meshes if "FrontDog" not in (m.a, m.b)),
                     recorded=keep(motion.recorded),
                     mode_placements=tuple((m, keep(f)) for m, f in motion.mode_placements),
                     recorded_by_mode=tuple((m, keep(f)) for m, f in motion.recorded_by_mode))
    motion = replace(motion, **{k: tuple(x for x in getattr(motion, k) if x[0] in more.get("modes", TC_MODES))
                                for k in ("mode_placements", "recorded_by_mode")},
                     configurations=tuple(m for m in TC_MODES if m in more.get("modes", TC_MODES)))
    return gone, list(keep(placements)), motion


def test_a_mode_and_a_gear_removed_with_the_delete_failing_says_the_mode_done_and_the_next_press_takes_the_gear(
        tc_built, measured):
    """The reviewer's probe, pinned: N deleted, FrontDog's delete failing; the next press takes FrontDog out alone."""
    fake, built = tc_built
    gone, placements, motion = _without_front_dog(built, modes=("2H", "4H", "4L"))
    _fail_next(fake, "delete_component", "SolidWorks would not delete gear9-1.")
    result = swbuild.update_gearbox(fake, assembly=TC_ASM, placements=placements, motion=motion, exists=fake.exists,
                                    mtime=lambda _p: 0.0, in_place=InPlace(removed=(gone,), modes_removed=("N",)))
    assert result.modes_removed == ["N"] and result.deleted == [] and result.mates_deleted == []
    assert result.failures == [("TransferCase.SLDASM", "SolidWorks would not delete gear9-1.")]
    assert result.skipped == ("taking FrontDog out and putting the gears back and checking the assembly, because the "
                              "job stopped in TransferCase.SLDASM")
    assert "N" not in fake.configs and "gear9-1" in fake.assembly_names[_key(TC_ASM)] and fake.config == "2H"
    again = swbuild.update_gearbox(fake, assembly=TC_ASM, placements=placements, motion=motion, exists=fake.exists,
                                   mtime=lambda _p: 0.0, in_place=InPlace(removed=(gone,)))
    assert again.ok, (again.failures, again.skipped)
    assert again.deleted == [("FrontDog", "gear9-1")] and again.modes_removed == []


def test_a_component_deleted_raises_the_epoch_and_answers_no_more_as_the_session_does(tc_built, measured):
    fake, built = tc_built
    gone, placements, motion = _without_front_dog(built)
    epoch = fake.epoch
    result = swbuild.update_gearbox(fake, assembly=TC_ASM, placements=placements, motion=motion, exists=fake.exists,
                                    mtime=lambda _p: 0.0, in_place=InPlace(removed=(gone,)))
    assert result.ok and fake.epoch > epoch and "gear9-1" in fake.missing_components
    with pytest.raises(swbuild.ComponentGone):
        fake.find_component("again", "gear9-1")


def test_a_relief_that_will_not_suppress_stops_before_the_assembly_and_the_next_press_takes_the_bands(measured):
    fake = _built_train()
    for kept in (fake.saved, fake.memory):
        kept[_key(P17)][1].extend(f for f in RELIEF_FEATURES if f not in kept[_key(P17)][1])
    taken = swbuild.BandChange("G3", P17, False, (), (clutch.RELIEF,))
    _fail_next(fake, "suppress_feature", "SolidWorks would not suppress Relief in Gear_m1.5_N17.")
    result = _update_train(fake, parts=[_p17(RELIEF_FEATURES)], in_place=InPlace(bands=(taken,)))
    assert result.failures == [("Gear_m1.5_N17.SLDPRT", "SolidWorks would not suppress Relief in Gear_m1.5_N17.")]
    assert result.bands_removed == [] and result.skipped == "the assembly, because Gear_m1.5_N17.SLDPRT failed"
    assert T_ASM not in result.changed and fake.suppressed_features == {}
    again = _update_train(fake, parts=[_p17(RELIEF_FEATURES)], in_place=InPlace(bands=(taken,)))
    assert again.ok and again.bands_removed == ["G3"]


def test_a_remake_with_modes_that_fails_says_what_is_left_and_the_next_press_remakes_it(t_with_modes, measured):
    fake = t_with_modes
    motion = _motion(configurations=("Default", "L"), ratios=(("G3 meshes G4", 18, 50),))
    _fail_next(fake, "set_gear_ratio", "SolidWorks would not make the gear mate G3 meshes G4 again.")
    result = _update_train(fake, motion=motion)
    assert result.failures == [("T.SLDASM", "SolidWorks would not make the gear mate G3 meshes G4 again.")]
    assert result.remade_in_modes == [] and result.ratios == []
    assert result.skipped == ("making the gear mate G3 meshes G4 again and putting the gears back and checking the "
                              "assembly, because the job stopped in T.SLDASM")
    again = _update_train(fake, motion=motion)
    assert again.ok and again.remade_in_modes == ["G3 meshes G4"]
    assert fake.mate("G3 meshes G4", T_ASM).ratio == (18.0, 50.0)


# -- the review's must-fix 1, the worker's half: the removed modes out of the inventory, and no empty side ------------

def test_work_without_modes_takes_the_removed_modes_out_of_each_mates_on_set_as_a_copy():
    lock = UserMate("Lock3", swbuild.USER_LOCK, 16, (("app", "Sun"), ("user", "Sprocket-1")), ("H", "N", "L"))
    work = UserWork(mates=[lock])
    assert swbuild.work_without_modes(work, ("n",)).mates[0].on == ("H", "L") and work.mates[0].on == ("H", "N", "L")
    assert swbuild.work_without_modes(work, ()).mates[0].on == ("H", "N", "L")


def test_a_lock_on_in_every_mode_left_is_firm_even_with_a_removed_mode_still_in_its_on_set(carry):
    """judge_user_work given a recorded inventory still listing N, over the modes after (H and L): no refusal with an
    empty side; the lock is carried."""
    lock = UserMate("Lock3", swbuild.USER_LOCK, 16, (("app", "Sun"), ("user", "Sprocket-1")), ("H", "N", "L"))
    work = UserWork(components=[UserComponent("Sprocket-1", "C:\\U\\Sprocket.SLDPRT")], mates=[lock])
    for judged in (work, swbuild.work_without_modes(work, ("N",))):
        judgement = swbuild.judge_user_work(judged, ("H", "L"), {"Sun"}, file="RangeBox.SLDASM", trains=[("Sun",)],
                                            mated=["Sun"], branches={"Sun": swbuild.BRANCH_NO_CARRIER_MODES},
                                            revision=Y26)
        assert judgement.problems == [] and [c for c, _ in judgement.carried["Sun"]] == ["Sprocket-1"]


def test_a_leftover_configuration_no_mode_names_is_taken_away_by_the_mode_removal_route(tc_built, measured):
    """B's third ask (§11, the review's round): a configuration a stopped press added (InPlace.left) that the workbook
    no longer wants comes as a mode removed though it is not among the record's modes; it is deleted behind
    UPDATE_REMOVES_A_MODE as any mode removed, the user's flags there said."""
    fake, built = tc_built
    _housing(fake)
    fake.add_configuration("R")
    fake.rebuild(kind=swcom.ASSEMBLY_TRAIN)
    fake.show_configuration("2H")
    fake.calls.clear()
    result = _tc_in_place(fake, built, InPlace(modes_removed=("R",), left=("R",)))
    assert result.ok, (result.failures, result.skipped)
    assert result.modes_removed == ["R"] and "R" not in fake.configs and result.extra_configurations == []
    assert result.flags_lost == []


# -- the demonstration's second run on 2026 (2966516): every in-place step inside the build's bracket ----------------

def test_bands_are_given_inside_the_builds_bracket_and_the_users_dimension_setting_reads_as_it_was(measured):
    """The relief's AddDimension2 ran outside begin_build/end_build and SolidWorks' Modify box came up. The fake now
    starts with swInputDimValOnCreate on, as the user's had it, and fails a test on a dimension made with it on."""
    fake = _built_train()
    assert fake.dim_dialog_on
    result = _update_train(fake, parts=[_p17(RELIEF_FEATURES)], in_place=InPlace(bands=(_bands_given(),)))
    assert result.ok, (result.failures, result.skipped)
    assert fake.dim_dialog_on and fake.dim_dialog_kept is None              # the user's setting put back
    called = names(fake)
    first, last = called.index("dimension"), len(called) - 1 - called[::-1].index("dimension")
    assert called[:first].count("begin_build") == called[:first].count("end_build") + 1
    assert "end_build" in called[last:]


def test_a_band_step_that_fails_still_puts_the_users_dimension_setting_back(measured):
    fake = _built_train(fail_on={"loft_cut": "SolidWorks would not make the loft cut Relief."})
    result = _update_train(fake, parts=[_p17(RELIEF_FEATURES)], in_place=InPlace(bands=(_bands_given(),)))
    assert not result.ok and result.skipped == "the assembly, because Gear_m1.5_N17.SLDPRT failed"
    assert fake.dim_dialog_on and fake.dim_dialog_kept is None


def test_the_fake_raises_the_modify_box_on_a_dimension_made_outside_the_bracket():
    fake = _built_train()
    fake.open_document(P17)
    with pytest.raises(AssertionError, match="Modify box"):
        fake.dimension("D9", ("a",), (0.0, 0.0))
    fake.begin_build()
    fake.dimension("D9", ("a",), (0.0, 0.0))
    fake.end_build()
    assert fake.dim_dialog_on


def test_a_hub_built_and_inserted_in_place_runs_every_op_inside_a_bracket(tc_built, measured):
    """The new part goes through the build's own build() (its own bracket), the assembly's ops through the change
    phase's: no dimension anywhere outside one, and the setting back as it was."""
    fake, built = tc_built
    added, placements, changes = _with_hub(built)
    motion, _ = _tc_motion(built, "2H")
    result = swbuild.update_gearbox(fake, assembly=TC_ASM, placements=placements,
                                    motion=replace(motion, layout_component="layout-1", **changes), exists=fake.exists,
                                    mtime=lambda _p: 0.0, in_place=InPlace(added=(added,)))
    assert result.ok, (result.failures, result.skipped)
    assert fake.dim_dialog_on and fake.dim_dialog_kept is None


def test_two_gates_unmeasured_refuse_as_two_problems_each_with_its_finding_as_its_subject():
    """The demonstration's second run (log line 180) saw one subject kept for two problems of one kind: the worker
    gives each its own; the merging was in the script's check, which keyed the record's problems by kind."""
    fake = _built_train()
    with pytest.raises(UserWorkRefused) as raised:
        _update_train(fake, parts=[_p17(RELIEF_FEATURES)],
                      in_place=InPlace(added=(ADD_G5,), bands=(_bands_given(),)), **_with_g5())
    assert [(p.kind, p.subjects) for p in raised.value.problems] == [
        (PROBLEM_UNSETTLED, ("UPDATE_INSERTS_A_GEAR_ON_2026",)), (PROBLEM_UNSETTLED, ("UPDATE_BANDS_IN_PLACE_ON_2026",))]
    assert _writes(fake) == []
