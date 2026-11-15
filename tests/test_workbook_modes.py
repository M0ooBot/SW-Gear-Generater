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


def test_modes_reason_names_the_version_independent_finding_and_a_plan_without_modes_is_none(monkeypatch):
    """§9.5: modes_reason covers the version-independent finding only; the per-version ones are the worker's."""
    from gear_generator import findings
    assert motion.modes_plan(motion.MotionPlan(), {}, {}) is None
    monkeypatch.setattr(findings, "COMPONENT_FIND_ROUTE", None, raising=False)
    reason = motion.modes_reason()
    assert reason.startswith("A gearbox with modes is not built") and "COMPONENT_FIND_ROUTE" in reason
    _, plan = plan_of(transfer_case_parallel())
    assert plan.refusal == reason and plan.modes_plan is None
    monkeypatch.setattr(findings, "COMPONENT_FIND_ROUTE", "by name")
    assert motion.modes_reason() == ""


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


# -- the mates, the configurations' plan and the record (W8-PLAN §1.7-§1.8, §1.11; W8-INTERFACES §7, §9) ----------

from gear_generator.gears.base import Mate  # noqa: E402
from gear_generator.workbook import layout  # noqa: E402

W8_MATES = [  # (name, kind, values, modes, sense), §2.3's table
    ("RangeSlv on Rear Axis", "axis", (), (), 0),
    ("RangeSlv along Rear", "slide", (("2H", 46.0), ("4H", 46.0), ("N", 56.0), ("4L", 66.0)), (), 0),
    ("ModeSlv on Rear Axis", "axis", (), (), 0),
    ("ModeSlv along Rear", "slide", (("2H", 96.0), ("4H", 106.0), ("N", 96.0), ("4L", 106.0)), (), 0),
    ("ModeSlv splined to RangeSlv", "spline", (), (), -1),
    ("RangeSlv engages InDog", "couple", (), ("2H", "4H"), -1),
    ("RangeSlv engages LoDog", "couple", (), ("4L",), -1),
    ("ModeSlv engages FrontDog", "couple", (), ("4H", "4L"), -1),
]


def plan_of(spec):
    a = assessed(spec)
    return a, gearbox.plan_gearbox(a, None, exists=lambda p: False, read_sidecar=lambda p: None)


@pytest.mark.parametrize("make", [transfer_case_parallel, e4_transfer_case])
def test_the_mates_w8_adds_are_the_answer_keys(make):
    a, plan = plan_of(make())
    assert plan.refusal == ""
    added = [(m.name, m.kind, m.values, m.modes, m.sense) for m in plan.motion.mates
             if m.kind in ("slide", "spline", "couple") or m.name.startswith(("RangeSlv on", "ModeSlv on"))]
    assert added == W8_MATES
    assert plan.motion.modes == ("2H", "4H", "N", "4L")
    assert not any(m.name.startswith(("RangeSlv locked", "ModeSlv locked", "RangeSlv along Rear Axis"))
                   for m in plan.motion.mates)
    assert {m.name: m.z_front for m in plan.motion.mates if m.kind == "slide"} == {"RangeSlv along Rear": 46.0,
                                                                                   "ModeSlv along Rear": 96.0}


def test_a_couplings_sense_is_worked_by_hand():
    """§9.3: about each gear's own axis a sleeve and the dog it engages turn by k = σ_S·σ_D — both on Z+ shafts
    here, so k = +1, the same way: sense = −σ_S·σ_D = −1 and the coupling is in ``same_way``; the spline turns its
    slider with the anchor, sense −1, so ``mate_senses`` holds it True (W6 §7.2's identity)."""
    _, plan = plan_of(transfer_case_parallel())
    assert set(plan.modes_plan.same_way) == {"RangeSlv engages InDog", "RangeSlv engages LoDog",
                                             "ModeSlv engages FrontDog"}
    assert plan.mate_senses["ModeSlv splined to RangeSlv"] is True
    assert not any(name in plan.mate_senses for name in plan.modes_plan.same_way)     # one home per gear mate
    spec = transfer_case_parallel()
    flipped = replace(spec, shafts=tuple(replace(s, axis="Z-") if s.id == "Lo" else s for s in spec.shafts),
                      gears=tuple(replace(g, at=str(-float(g.at))) if g.shaft == "Lo" else g for g in spec.gears))
    _, refused = plan_of(flipped)
    assert refused.refusal == (
        "RangeSlv and LoDog face opposite ways along their shaft line, and a coupling between shafts facing opposite "
        "ways has not been shown on SolidWorks, so it is not built: give Rear and Lo the same Axis.")


@pytest.mark.parametrize("make", [transfer_case_parallel, e4_transfer_case])
def test_the_configurations_plan_makes_each_coupling_where_it_is_first_on_and_sets_every_value(make):
    a, plan = plan_of(make())
    mp = plan.modes_plan
    assert mp.check(plan.assembly) == [] and plan.build_kwargs()["modes"] is mp                 # §9.10
    assert [(s.name, [o.name for o in s.ops]) for s in mp.steps] == [
        ("2H", ["RangeSlv engages InDog"]), ("4H", ["ModeSlv engages FrontDog"]), ("N", []),
        ("4L", ["RangeSlv engages LoDog"])]
    assert [s.values for s in mp.steps] == [{"RangeSlv along Rear": 46.0, "ModeSlv along Rear": 96.0},
                                            {"RangeSlv along Rear": 46.0, "ModeSlv along Rear": 106.0},
                                            {"RangeSlv along Rear": 56.0, "ModeSlv along Rear": 96.0},
                                            {"RangeSlv along Rear": 66.0, "ModeSlv along Rear": 106.0}]
    assert mp.steps[2].off == ("RangeSlv engages InDog", "RangeSlv engages LoDog", "ModeSlv engages FrontDog")
    handle = {g: h for h, g in plan.handles.items()}
    for step, z in zip(mp.steps, (46.0, 46.0, 56.0, 66.0)):                 # the frames that reach SolidWorks
        assert step.frames[handle["RangeSlv"]][1] == (0.0, 0.0, z)
        assert step.frames[handle["InDog"]][1] == (0.0, 0.0, 47.0)
    ops = [op for op in plan.assembly.ops if isinstance(op, Mate)]
    slide = next(op for op in ops if op.name == "RangeSlv along Rear")
    assert (slide.kind, slide.b, slide.value) == ("point distance", "layout:plane1", 46.0)
    spline = next(op for op in ops if op.name == "ModeSlv splined to RangeSlv")
    assert (spline.kind, spline.ratio) == ("gear", (1.0, 1.0))
    assert not any(op.name.endswith(("InDog", "LoDog", "FrontDog")) and "engages" in op.name for op in ops)


def test_a_slide_on_the_front_plane_is_refused():
    """J27: RangeSlv at H with At 14 puts its front face at 0."""
    spec = transfer_case_parallel()
    moved = replace(spec, gears=tuple(replace(g, at="14", slides="H=-10, N=0, L=+10") if g.id == "RangeSlv" else g
                                      for g in spec.gears))
    _, plan = plan_of(moved)
    assert plan.refusal == ("RangeSlv's position H puts its front face on the Front plane, from which a slide is "
                            "measured, so it is not built: move the slide off the plane.")


from gear_generator import swbuild  # noqa: E402
from test_workbook_gearbox import Disk, built, stem  # noqa: E402


def run_modes(plan, disk):
    """What build_gearbox answers for a first build, by its pinned fields, carriers included."""
    result = swbuild.GearboxResult()
    for job in plan.build:
        result.parts.built.append(built(job.path, job.spec.kind))
        disk.add(job.path)
    result.layout = built(plan.layout_path, "layout")
    disk.add(plan.layout_path)
    for item in plan.carriers:
        result.carriers.append(built(item.path, "carrier"))
        disk.add(item.path)
    result.assembly = built(plan.assembly_path, "assembly")
    disk.add(plan.assembly_path)
    carrier_part = {h: plan.carrier_paths[c[:-len(" carrier")]] for h, c in plan.carrier_handles.items()}
    names, counts = {layout.LAYOUT_HANDLE: stem(plan.layout_path) + "-1"}, {}
    for handle, gear in list(plan.handles.items()) + list(plan.carrier_handles.items()):
        part = stem(plan.part_of[gear]) if gear in plan.part_of else stem(carrier_part[handle])
        counts[part] = counts.get(part, 0) + 1
        names[handle] = f"{part}-{counts[part]}"
    result.components = names
    result.assembly.components = dict(names)
    return result


@pytest.mark.parametrize("make", [transfer_case_parallel, e4_transfer_case])
def test_a_build_with_modes_records_the_modes_values_on_sets_and_frames_and_reads_them_back(make):
    """W8-PLAN §1.11 (schema 6): the record keeps the modes as built, each SLIDE's value per mode, each coupling's
    on-set and each component's frame per mode — real values, in the change that lets a modes gearbox through."""
    disk = Disk()
    a = assessed(make())
    plan = gearbox.plan_gearbox(a, None, exists=disk.exists, read_sidecar=disk.read_sidecar)
    assert plan.refusal == ""
    done = gearbox.finish_build(plan, run_modes(plan, disk), None, workbook=BOOK, digest="d1", written_by="test",
                                read_sidecar=disk.read_sidecar, exists=disk.exists, stamp="2026-11-14T00:00:00Z")
    record = store.link_record_from_json(store.link_record_to_json(done.record))
    box = record.gearbox
    assert box.kind == motion.MOTION and box.modes == ["2H", "4H", "N", "4L"]
    mates = {m.name: m for m in box.mates}
    assert mates["RangeSlv along Rear"].values == {"2H": 46.0, "4H": 46.0, "N": 56.0, "4L": 66.0}
    assert mates["ModeSlv along Rear"].values == {"2H": 96.0, "4H": 106.0, "N": 96.0, "4L": 106.0}
    assert {n: m.modes for n, m in mates.items() if m.kind == COUPLE} == {
        "RangeSlv engages InDog": ["2H", "4H"], "RangeSlv engages LoDog": ["4L"],
        "ModeSlv engages FrontDog": ["4H", "4L"]}
    assert {n: m.sense for n, m in mates.items() if m.kind in (COUPLE, SPLINE)} == {
        "RangeSlv engages InDog": -1, "RangeSlv engages LoDog": -1, "ModeSlv engages FrontDog": -1,
        "ModeSlv splined to RangeSlv": -1}
    assert all(m.modes for m in box.mates if m.kind == COUPLE)                          # §9.1: never []
    frames = {c.gear: c.frames for c in box.components}
    assert [frames["RangeSlv"][m]["at"] for m in box.modes] == [[0.0, 0.0, z] for z in (46.0, 46.0, 56.0, 66.0)]
    assert [frames["ModeSlv"][m]["at"] for m in box.modes] == [[0.0, 0.0, z] for z in (96.0, 106.0, 96.0, 106.0)]
    assert {frames["InDog"][m]["at"][2] for m in box.modes} == {47.0}
    first = {c.gear: c.at for c in box.components}
    assert first["RangeSlv"] == [0.0, 0.0, 46.0]                  # the component as saved: the first mode's frame


def test_a_build_without_modes_records_none():
    disk = Disk()
    a = direct(planetary_4to1())
    plan = gearbox.plan_gearbox(a, None, exists=disk.exists, read_sidecar=disk.read_sidecar)
    done = gearbox.finish_build(plan, run_modes(plan, disk), None, workbook=BOOK, digest="d1", written_by="test",
                                read_sidecar=disk.read_sidecar, exists=disk.exists, stamp="2026-11-14T00:00:00Z")
    box = done.record.gearbox
    assert box.modes == [] and all(c.frames == {} for c in box.components)
    assert all(m.values == {} and m.modes == [] for m in box.mates)


@pytest.mark.parametrize("make", [transfer_case_parallel, e4_transfer_case])
def test_the_mates_made_do_not_depend_on_row_order(make):
    """Meshes rows, slider columns and the shafts' blocks of Gears rows reversed: the same mates, the same steps.
    (The order of gears on one shaft picks its anchor, J9, as W5's does, so it is kept.)"""
    spec = make()
    _, plan = plan_of(spec)
    blocks = list(dict.fromkeys(g.shaft for g in spec.gears))[::-1]
    shuffled = replace(spec, gears=tuple(sorted(spec.gears, key=lambda g: blocks.index(g.shaft))),
                       meshes=tuple(reversed(spec.meshes)), sliders=tuple(reversed(spec.sliders)),
                       modes=tuple(replace(m, positions=tuple(reversed(m.positions))) for m in spec.modes))
    _, again = plan_of(shuffled)
    assert again.refusal == ""

    def made(p):
        return {(m.name, m.kind, m.gears, m.values, m.modes, m.sense) for m in p.motion.mates}
    assert made(again) == made(plan)
    assert [(s.name, s.values, sorted(s.on), sorted(s.off)) for s in again.modes_plan.steps] == [
        (s.name, s.values, sorted(s.on), sorted(s.off)) for s in plan.modes_plan.steps]
    assert [sorted(o.name for o in s.ops) for s in again.modes_plan.steps] == [
        sorted(o.name for o in s.ops) for s in plan.modes_plan.steps]


@pytest.mark.parametrize("make", [transfer_case_parallel, e4_transfer_case, planetary_4to1])
def test_a_plan_has_modes_exactly_when_it_has_a_configurations_plan(make):
    """§9.10: MotionPlan.modes is non-empty ⇔ GearboxPlan.modes_plan is set; §9.8: no Modes rows, no values."""
    spec = make()
    for s in (spec, replace(spec, modes=())):
        _, plan = plan_of(s)
        assert plan.refusal == ""
        assert bool(plan.motion.modes) == (plan.modes_plan is not None) == bool(s.modes)
        if not s.modes:
            assert all(m.values == () and m.modes == () for m in plan.motion.mates)


def test_a_row_held_back_says_the_layout_and_assembly_are_not_built_in_cs_words(monkeypatch):
    """W8 is the last phase: nothing waits for one. Should a row ever be held back again, the refusal reads as C's
    footer does (``ui_text._left_for_later``), word for word."""
    from gear_generator.workbook import build
    monkeypatch.setitem(build.LATER, "dog", ("a dog ring", "dog rings are not built by this version of the app"))
    a = assess.assess(replace(transfer_case_parallel(), source_path=BOOK), [], "C:\\Out\\")
    assert a.lay_out_refusal() == ("The layout and assembly are not built: Gears row 3: InDog is a dog ring: dog rings "
                                   "are not built by this version of the app. (2 more under Checks)")
    assert a.lay_out_refusal() == ui_text._left_for_later(a.parts).strip()
