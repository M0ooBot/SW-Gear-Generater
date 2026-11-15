"""W8's planning-side shapes, written at W8's interface commit (W8-INTERFACES.md §4, §5, §7): the three mate kinds and
their names, the record entry a mate makes and the reference Update takes back, the plan and report fields with
their defaults, ``build_kwargs``' ``modes`` key, and the turning sentence's switch. Package B adds the planning
tests (both fixtures) here."""

from dataclasses import replace

import pytest

from gear_generator import store, ui_text
from gear_generator.swbuild import MateRef, ModesPlan, ModeStep
from gear_generator.workbook import checks, gearbox, motion
from gear_generator.workbook.motion import COUPLE, SLIDE, SPLINE, MatePlan, mate_entry, mate_name, mate_ref

from test_workbook_planetary import direct, planetary_4to1


# -- the three kinds and their names (J23) -------------------------------------------------------------------------

def test_the_three_kinds_join_w5s_four_in_the_order_the_store_keeps():
    assert (SLIDE, SPLINE, COUPLE) == ("slide", "spline", "couple")
    assert motion.MATE_KINDS == ("axis", "along", "lock", "mesh", "slide", "spline", "couple")
    assert tuple(store._MATE_GEARS) == motion.MATE_KINDS


def test_the_fixtures_mate_names_are_the_plans():
    assert mate_name(SLIDE, ("RangeSlv",), "Rear") == "RangeSlv along Rear"
    assert mate_name(SPLINE, ("RangeSlv", "ModeSlv")) == "ModeSlv splined to RangeSlv"     # (anchor, slider)
    assert mate_name(COUPLE, ("RangeSlv", "InDog")) == "RangeSlv engages InDog"            # (sleeve, dog)
    assert mate_name(motion.AXIS, ("RangeSlv",), "Rear") == "RangeSlv on Rear Axis"        # W5's, unchanged


@pytest.mark.parametrize("kind,gears,shaft,match", [
    (SLIDE, ("RangeSlv", "ModeSlv"), "Rear", r"^A slide mate holds 1 gear, not"),
    (SLIDE, ("RangeSlv",), "", r"^A slide mate needs shaft, and was given ''\.$"),
    (SPLINE, ("RangeSlv",), "", r"^A spline mate holds 2 gears, not"),
    (SPLINE, ("RangeSlv", "ModeSlv"), "Rear", r"^A spline mate takes no shaft, and was given 'Rear'\.$"),
    (COUPLE, ("RangeSlv", ""), "", r"^A couple mate holds 2 gears, not"),
    ("slip", ("RangeSlv",), "Rear", r"is not a kind of mate the turning assembly makes \(axis, along, lock, mesh, "
                                    r"slide, spline, couple\)\.$"),
])
def test_a_w8_mate_name_with_the_wrong_gears_or_shaft_is_refused_with_a_sentence(kind, gears, shaft, match):
    with pytest.raises(ValueError, match=match):
        mate_name(kind, gears, shaft)


# -- MatePlan -> MateEntry -> MateRef carry the values and the on-set ------------------------------------------------

SLIDE_PLAN = MatePlan(name="ModeSlv along Rear", kind=SLIDE, gears=("ModeSlv",), shaft="Rear", z_front=96.0,
                      values=(("2H", 96.0), ("4H", 106.0), ("N", 96.0), ("4L", 106.0)))
COUPLE_PLAN = MatePlan(name="ModeSlv engages FrontDog", kind=COUPLE, gears=("ModeSlv", "FrontDog"), ratio=(1, 1),
                       sense=-1, modes=("4H", "4L"))


def test_a_slides_values_and_a_couplings_modes_reach_the_record_and_come_back_for_update():
    entry = mate_entry(SLIDE_PLAN)
    assert entry.values == {"2H": 96.0, "4H": 106.0, "N": 96.0, "4L": 106.0} and entry.modes == []
    assert (entry.kind, entry.plane, entry.face_global, entry.z_front) == ("slide", "front", "", 96.0)
    ref = mate_ref(entry)
    assert ref == MateRef("ModeSlv along Rear", "slide", ("ModeSlv",), "Rear",
                          values=(("2H", 96.0), ("4H", 106.0), ("N", 96.0), ("4L", 106.0)))
    couple = mate_entry(COUPLE_PLAN)
    assert couple.modes == ["4H", "4L"] and couple.values == {} and couple.ratio == [1, 1] and couple.sense == -1
    assert mate_ref(couple).modes == ("4H", "4L")


def test_a_record_read_back_gives_update_the_same_values_whatever_order_the_file_holds_them_in():
    record = store.LinkRecord(workbook="R.xlsx")
    record.gearbox = store.GearboxRecord(kind=store.GEARBOX_MOTION, modes=["2H", "4H", "N", "4L"],
                                         mates=[mate_entry(SLIDE_PLAN), mate_entry(COUPLE_PLAN)])
    again = store.link_record_from_json(store.link_record_to_json(record))
    assert dict(mate_ref(again.gearbox.mates[0]).values) == dict(SLIDE_PLAN.values)
    assert mate_ref(again.gearbox.mates[1]).modes == COUPLE_PLAN.modes


def test_a_w5_mate_carries_no_values_and_no_modes():
    plan = MatePlan(name="G1 meshes G2", kind=motion.MESH, gears=("G1", "G2"), ratio=(17, 68), sense=1)
    entry = mate_entry(plan)
    assert (entry.values, entry.modes) == ({}, [])
    assert (mate_ref(entry).values, mate_ref(entry).modes) == ((), ())


def test_the_senses_identity_holds_for_a_coupling_as_for_a_mesh():
    """W8-INTERFACES §6: a coupling turns its gears the same way (k > 0), so its ``sense`` is −1 and
    ``mate_senses[name] = (sense == −1)`` gives True, the same identity W6 pinned."""
    assert (COUPLE_PLAN.sense == -1) is True


# -- plan and report fields, and the stubs ---------------------------------------------------------------------------

def test_the_w8_fields_default_to_a_gearbox_with_no_modes():
    plan = motion.MotionPlan()
    assert plan.modes == () and dict(plan.drag_by_mode) == {}
    assert checks.Report().modes == ()
    report = checks.ModeReport("4L", 5)
    assert (report.positions, report.engaged, report.out_of_mesh, report.off, report.placed) == ({}, (), (), (), {})


def test_until_b_writes_them_the_modes_plan_refuses_and_modes_reason_says_why():
    with pytest.raises(ValueError, match=r"^Planning an assembly's configurations is not in this version of Gear "
                                         r"Generator yet, so a gearbox with modes cannot be planned\.$"):
        motion.modes_plan(motion.MotionPlan(modes=("2H",)), {}, {})
    reason = motion.modes_reason()
    assert reason.startswith("A gearbox with modes is not built") and reason.endswith(".")


def test_build_kwargs_passes_modes_only_when_the_plan_has_them():
    plan = gearbox.plan_gearbox(direct(planetary_4to1()), None, exists=lambda p: False, read_sidecar=lambda p: None)
    assert plan.refusal == "" and plan.modes_plan is None and "modes" not in plan.build_kwargs()
    modes = ModesPlan((ModeStep("2H"),))
    assert replace(plan, modes_plan=modes).build_kwargs()["modes"] is modes


# -- the sentences: the turning switch is written, the rest refuse until C writes them --------------------------------

def test_the_turning_sentence_is_chosen_by_the_running_versions_finding_and_none_says_neither():
    assert ui_text.turning_note(True) == "A turn you give the gears in one configuration stays in that configuration."
    assert ui_text.turning_note(False) == (
        "A turn you give the gears in one configuration shows in every configuration, so a dog can stand across its "
        "sleeve in another mode until Update SolidWorks puts the gears back.")
    assert ui_text.turning_note(None) == ""


@pytest.mark.parametrize("call", [
    lambda: ui_text.modes_ready_line(None), lambda: ui_text.modes_done_line(None, None),
    lambda: ui_text.mode_problem("In mode 4L, …"), lambda: ui_text.modes_record_line(None),
    lambda: ui_text.mode_update_lines(None, None), lambda: ui_text.mode_speed_lines(None, None, "4L"),
])
def test_each_modes_sentence_refuses_with_a_sentence_until_c_writes_it(call):
    with pytest.raises(ValueError, match=r"^The sentence .+ is not written in this version of Gear Generator yet\.$"):
        call()
