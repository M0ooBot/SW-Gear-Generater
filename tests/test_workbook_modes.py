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



# -- B's planning: the fixtures per mode (W8-PLAN §2.2, §2.3) -------------------------------------------------------

import math  # noqa: E402
from fractions import Fraction  # noqa: E402

from gear_generator import findings  # noqa: E402
from gear_generator.workbook import assess, model, xlsx  # noqa: E402
from workbook_fixtures import e4_transfer_case, transfer_case_parallel  # noqa: E402

BOOK = "C:\\Books\\TransferCase.xlsx"


def assessed(spec):
    return assess.assess(replace(spec, source_path=BOOK), [], "C:\\Out\\")


def modes_of(spec):
    return {m.name: m for m in assessed(spec).report.modes}


@pytest.mark.parametrize("make", [transfer_case_parallel, e4_transfer_case])
def test_each_mode_engages_what_the_answer_key_says_and_turns_as_it_says(make):
    """§2.3, worked by hand: Rear 1500 / 1500 / free / 375, FrontDrv free / 1500 / free / 375, Idler −FrontDrv·30/20,
    Front −Idler·20/30; In +1500 always."""
    modes = modes_of(make())
    assert list(modes) == ["2H", "4H", "N", "4L"]
    assert {n: m.engaged for n, m in modes.items()} == {
        "2H": (("RangeSlv", "InDog"),), "4H": (("RangeSlv", "InDog"), ("ModeSlv", "FrontDog")), "N": (),
        "4L": (("RangeSlv", "LoDog"), ("ModeSlv", "FrontDog"))}
    expected = {"2H": {"Rear": 1500}, "4H": {"Rear": 1500, "FrontDrv": 1500, "Idler": -2250, "Front": 1500},
                "N": {}, "4L": {"Rear": 375, "FrontDrv": 375, "Idler": Fraction(-1125, 2), "Front": 375}}
    for name, m in modes.items():
        got = {s: m.motion.speeds[s] for s in ("Rear", "FrontDrv", "Idler", "Front") if s in m.motion.speeds}
        assert got == expected[name] and m.motion.speeds["In"] == 1500 and not m.motion.jammed
        assert set(m.motion.free) == {"Rear", "FrontDrv", "Idler", "Front"} - set(expected[name])
    positions = {n: m.positions for n, m in modes.items()}
    assert positions["4L"] == {"RangeSlv": ("L", 10.0), "ModeSlv": ("4WD", 10.0)}
    assert positions["N"] == {"RangeSlv": ("N", 0.0), "ModeSlv": ("2WD", 0.0)}
    assert modes["4L"].placed["RangeSlv"].z_range == (66.0, 74.0) and modes["2H"].placed["ModeSlv"].z_range == (96, 104)


@pytest.mark.parametrize("make", [transfer_case_parallel, e4_transfer_case])
def test_each_modes_ratio_has_one_home(make):
    """The Speeds line and Export read ``ModeReport.ratio`` / ``ends`` / ``ratio_why`` / ``driven``: In : Rear
    1.000, 1.000, neutral, 4.000; In : Front not driven (None), 1.000, None, 4.000."""
    modes = modes_of(make())
    assert {n: (m.ratio, m.ends, m.ratio_why) for n, m in modes.items()} == {
        "2H": (1.0, ("In", "Rear"), ""), "4H": (1.0, ("In", "Rear"), ""), "N": (None, ("", ""), "neutral"),
        "4L": (4.0, ("In", "Rear"), "")}
    assert {n: m.driven for n, m in modes.items()} == {
        "2H": {"Rear": 1.0, "Front": None}, "4H": {"Rear": 1.0, "Front": 1.0}, "N": {"Rear": None, "Front": None},
        "4L": {"Rear": 4.0, "Front": 4.0}}
    a = assessed(make())
    assert checks.overall_ratio(a.spec, a.report) == (1.0, "In to Rear", "")          # the first mode's
    assert a.report.motion is a.report.modes[0].motion


def test_the_torques_per_mode_follow_j17_and_the_answer_key():
    """§2.3's torque table (η 0.98, 10 N·m in): 2H Rear 10 (the idle layshaft branch pruned); 4H Rear 10, shared
    with FrontDrv, nothing past it; N nothing past In; 4L Lay 19.6, Lo 38.416, Rear 38.416 shared."""
    modes = modes_of(transfer_case_parallel())
    torques = {n: {k: round(v, 6) for k, v in m.motion.torques.items()} for n, m in modes.items()}
    assert torques == {"2H": {"In": 10.0, "Rear": 10.0}, "4H": {"In": 10.0, "Rear": 10.0}, "N": {"In": 10.0},
                       "4L": {"In": 10.0, "Lay": 19.6, "Lo": 38.416, "Rear": 38.416}}
    assert {n: (m.motion.shared, m.motion.past_split) for n, m in modes.items()} == {
        "2H": ({}, ()), "4H": ({"Rear": ("FrontDrv",)}, ("FrontDrv", "Idler", "Front")), "N": ({}, ()),
        "4L": ({"Rear": ("FrontDrv",)}, ("FrontDrv", "Idler", "Front"))}
    e4 = modes_of(e4_transfer_case())
    assert {k: round(v, 6) for k, v in e4["2H"].motion.torques.items()} == {"In": 10.0, "Rear": 10.0}  # not zeroed
    assert e4["4L"].motion.torques["Rear"] == pytest.approx(10 * (1 + 0.9604 * 3))       # W7's rule, then shared
    assert e4["4L"].motion.shared == {"Rear": ("FrontDrv",)}


@pytest.mark.parametrize("make", [transfer_case_parallel, e4_transfer_case])
def test_the_fixtures_check_clean_and_say_their_modes(make):
    a = assessed(make())
    assert a.report.diagnostics == []
    words = {"TransferCase_Parallel": "Parallel train with modes · 4 meshes",
             "TransferCase_E4": "Planetary and parallel with modes, Ring fixed · 3 planets"}[make().box.name]
    assert a.report.worked_out_as == f"{words} · 2H 1.000 : 1, 4H 1.000 : 1, N neutral, 4L 4.000 : 1"


@pytest.mark.parametrize("make", [transfer_case_parallel, e4_transfer_case])
def test_the_phases_put_each_dog_in_its_sleeves_spaces(make):
    """§2.3 (mod 12°): InDog 0, RangeSlv 6°, LoDog 0, FrontDog 0, ModeSlv 6°."""
    theta = {g: math.degrees(t) % 12.0 for g, t in assessed(make()).report.theta.items()}
    got = {g: round(min(theta[g], 12.0 - theta[g]) if theta[g] > 6.0 + 1e-9 else theta[g], 9)
           for g in ("InDog", "RangeSlv", "LoDog", "FrontDog", "ModeSlv")}
    assert got == {"InDog": 0.0, "RangeSlv": 6.0, "LoDog": 0.0, "FrontDog": 0.0, "ModeSlv": 6.0}


# Taken at 120192d (before any of B's W8 planning code), the turned read-back finding set.
BEFORE_W8 = {
    "Reducer_12to1.xlsx": "41da0447e37015088d223b107ff53ebe82c983ebb38b5e6a1860b402cfd2c490",
    "Arc_Move.xlsx": "e6f8658f8d42437042b541d0e5a45fc7157caa5972fe044bc51b24f545d78b1e",
    "Risky_Placements.xlsx": "c221e0fd722e27e6562ec8e72c53a933d4e2b10ceb5de99a132377004d464c65",
    "bevel_reducer": "a881d20f11e59002d24c44d9c355646c95236a65a507449711a2055b1a709b92",
    "crossed_slant": "5401c79bb142cb17e3954ec0689413e779ed05450e3d314891f785ad6ac76d04",
    "planetary_4to1": "c7e45afa64a298687580bc8f58ba77ba139c2c6253e209bf7b4ebd8cc4a6a0a4",
    "sun_held": "ae7b987d760f34333c00c333b4ec39dcc480df3be4f98bb916159abc8476a5e7",
    "on_z_minus": "e318cb99e5480cde17e6391bac59cf0be10c355a13a8b53914a006418b70883c",
    "carrier_held": "b62225940a331243c462fec38ca68a426cc6b2effaaae611e15dfa1a3834a74c",
}


@pytest.mark.parametrize("name", sorted(BEFORE_W8))
def test_every_workbook_before_w8_plans_bit_for_bit_as_it_did(name, monkeypatch):
    import os
    import test_workbook_planetary as planetary_tests
    import test_workbook_turned as turned
    monkeypatch.setattr(findings, "TURNED_GEAR_MATE_SENSE_READ_BACK", "entity senses", raising=False)
    if name.endswith(".xlsx"):
        here = os.path.join(os.path.dirname(__file__), "fixtures", "excel-windows")
        spec, diagnostics = model.from_book(xlsx.read(os.path.join(here, name)))
        a = assess.assess(spec, diagnostics, "C:\\Out\\")
    elif hasattr(turned, name):
        a = assess.assess(replace(getattr(turned, name)(), source_path="C:\\B\\W.xlsx"), [], "C:\\Out\\")
    else:
        a = planetary_tests.direct(getattr(planetary_tests, name)())
    assert planetary_tests._fingerprint(a) == BEFORE_W8[name]
