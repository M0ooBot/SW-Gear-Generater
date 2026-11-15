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


def lower_4l(spec):
    """Parallel with its last mode spelled ``4l`` and RangeSlv's pick ``l`` where Slides says ``L`` (§9.6)."""
    modes = list(spec.modes)
    modes[3] = replace(modes[3], positions=(("RangeSlv", "l"), ("ModeSlv", "4wd")))
    return replace(spec, modes=tuple(modes[:3]) + (replace(modes[3], name="4l"),))


def test_names_written_in_another_case_read_as_the_same_and_the_record_keeps_the_workbooks_spelling(tmp_path):
    """W8-INTERFACES §9.6: a pick and a mode name compare ignoring case; the record keeps the workbook's spelling,
    and every name a mate's on-set or a slide's values hold is one of ``GearboxRecord.modes``, read back clean."""
    path = str(tmp_path / "TransferCase.xlsx")
    xlsx.write_new(path, model.to_sheets(lower_4l(transfer_case_parallel())))
    spec, problems = model.from_book(xlsx.read(path))
    assert [d.message for d in problems if d.is_error] == []
    a = assess.assess(replace(spec, source_path=BOOK), problems, "C:\\Out\\")
    assert a.lay_out_refusal() == ""
    assert {m.name: m.positions["RangeSlv"] for m in a.report.modes}["4l"] == ("L", 10.0)
    disk = Disk()
    plan = gearbox.plan_gearbox(a, None, exists=disk.exists, read_sidecar=disk.read_sidecar)
    done = gearbox.finish_build(plan, run_modes(plan, disk), None, workbook=BOOK, digest="d1", written_by="test",
                                read_sidecar=disk.read_sidecar, exists=disk.exists, stamp="2026-11-14T00:00:00Z")
    box = store.link_record_from_json(store.link_record_to_json(done.record)).gearbox
    assert box.modes == ["2H", "4H", "N", "4l"]
    mates = {m.name: m for m in box.mates}
    assert mates["RangeSlv along Rear"].values == {"2H": 46.0, "4H": 46.0, "N": 56.0, "4l": 66.0}
    assert mates["RangeSlv engages LoDog"].modes == ["4l"]
    assert all(set(m.modes) <= set(box.modes) and set(m.values) <= set(box.modes) for m in box.mates)
    assert all(set(c.frames) == set(box.modes) for c in box.components)


def test_a_mode_named_twice_in_another_case_and_a_position_named_twice_are_errors(tmp_path):
    spec = transfer_case_parallel()
    twice = replace(spec, modes=spec.modes + (replace(spec.modes[0], name="2h", row=6),),
                    gears=tuple(replace(g, slides="2WD=0, 4wd=+10, 4WD=+10") if g.id == "ModeSlv" else g
                                for g in spec.gears))
    path = str(tmp_path / "Twice.xlsx")
    xlsx.write_new(path, model.to_sheets(twice))
    _, problems = model.from_book(xlsx.read(path))
    said = [d.message for d in problems if d.is_error]
    assert "Modes!A6: the mode 2h is also at Modes!A2 (2H), as mode names are compared ignoring case." in said
    assert any("The position 4WD is named twice." in m for m in said)


# -- Update SolidWorks with modes: classify and finish (W8-PLAN §1.10, J14; W8-INTERFACES §9.1, §9.6, §9.9) ----------

from gear_generator.swbuild import GearboxUpdate, LockLink, MeshLink, UpdateResult  # noqa: E402
from gear_generator.workbook import update  # noqa: E402
from gear_generator.workbook import modes  # noqa: E402
from gear_generator.workbook.model import Box, Gear, GearboxSpec, Mesh, Mode, Shaft  # noqa: E402


def built_record(make=transfer_case_parallel, spec=None):
    """The record a first Build leaves, read back from its JSON."""
    disk = Disk()
    a = assessed(spec or make())
    plan = gearbox.plan_gearbox(a, None, exists=disk.exists, read_sidecar=disk.read_sidecar)
    assert plan.refusal == ""
    done = gearbox.finish_build(plan, run_modes(plan, disk), None, workbook=BOOK, digest="d1", written_by="test",
                                read_sidecar=disk.read_sidecar, exists=disk.exists, stamp="2026-11-14T00:00:00Z")
    return store.link_record_from_json(store.link_record_to_json(done.record))


def classify(record, spec):
    a = assessed(spec)
    assert a.lay_out_refusal() == ""
    return update.classify(record, a, exists=lambda p: True)


def with_mode(spec, index, **changes):
    modes = list(spec.modes)
    modes[index] = replace(modes[index], **changes)
    return replace(spec, modes=tuple(modes))


def with_gear(spec, gear, **changes):
    return replace(spec, gears=tuple(replace(g, **changes) if g.id == gear else g for g in spec.gears))


def finished(up, record, **result):
    """finish_update on a whole Update (every part reached unchanged), read back from its JSON."""
    base = dict(parts=[UpdateResult(unchanged=["x"]) for _ in up.parts], layout=UpdateResult(unchanged=["x"]),
                carriers=[UpdateResult(unchanged=["x"]) for _ in up.carriers])
    base.update(result)
    done = update.finish_update(up, GearboxUpdate(**base), record, digest="d2", read_sidecar=lambda p: None,
                                mtime=lambda p: 5.0)
    return store.link_record_from_json(store.link_record_to_json(done.record))


@pytest.mark.parametrize("make", [transfer_case_parallel, e4_transfer_case])
def test_an_unchanged_gearbox_with_modes_is_an_update_with_nothing_to_do_and_carries_every_mode(make):
    record = built_record(make)
    up = classify(record, make())
    assert (up.refusal, up.structural, up.replaced, up.modes_changed) == ("", (), (), ())
    assert up.record_matches and up.drag == tuple(record.gearbox.drag)
    m = up.motion
    assert m.configurations == ("2H", "4H", "N", "4L")
    assert m.slide_values == tuple((n, c, v) for n, vals in (
        ("RangeSlv along Rear", (46.0, 46.0, 56.0, 66.0)), ("ModeSlv along Rear", (96.0, 106.0, 96.0, 106.0)))
        for c, v in zip(("2H", "4H", "N", "4L"), vals))
    assert m.on_sets == (("RangeSlv engages InDog", ("2H", "4H")), ("RangeSlv engages LoDog", ("4L",)),
                         ("ModeSlv engages FrontDog", ("4H", "4L")))
    couples = {(l.a, l.b): (l.k, l.modes) for l in m.meshes if l.a.endswith("Slv")}
    assert couples == {("RangeSlv", "InDog"): (1.0, ("2H", "4H")), ("RangeSlv", "LoDog"): (1.0, ("4L",)),
                       ("ModeSlv", "FrontDog"): (1.0, ("4H", "4L"))}                    # §9.3: k = σ_S·σ_D
    assert LockLink("RangeSlv", "ModeSlv", 12.0) in m.locks                             # the spline, every mode
    by_mode = dict(m.mode_placements)
    assert [next(p.at for p in by_mode[c] if p.gear == "RangeSlv") for c in m.configurations] == [
        (0.0, 0.0, z) for z in (46.0, 46.0, 56.0, 66.0)]
    assert dict(m.recorded_by_mode).keys() == by_mode.keys()
    assert up.update_kwargs()["motion"] is m


def test_a_pick_changed_between_positions_on_record_is_an_update_of_one_value_and_two_flags():
    """J14's example: 4H's ModeSlv pick 4WD → 2WD sets 4H's value to 96 and takes FrontDog's coupling off in 4H."""
    record = built_record()
    spec = with_mode(transfer_case_parallel(), 1, positions=(("RangeSlv", "H"), ("ModeSlv", "2WD")))
    up = classify(record, spec)
    assert up.structural == () and up.replaced == ()
    assert up.modes_changed == ("ModeSlv engages FrontDog", "ModeSlv along Rear") and not up.record_matches
    assert ("ModeSlv along Rear", "4H", 96.0) in up.motion.slide_values
    assert dict(up.motion.on_sets)["ModeSlv engages FrontDog"] == ("4L",)
    box = finished(up, record, placed=[p.gear for p in up.placements]).gearbox
    mates = {m.name: m for m in box.mates}
    assert mates["ModeSlv along Rear"].values == {"2H": 96.0, "4H": 96.0, "N": 96.0, "4L": 106.0}
    assert mates["ModeSlv engages FrontDog"].modes == ["4L"]
    assert {c.gear: c.frames for c in box.components}["ModeSlv"]["4H"]["at"] == [0.0, 0.0, 96.0]
    again = classify(finished(up, record), spec)
    assert again.modes_changed == () and again.record_matches


def test_a_slide_offset_moves_the_value_in_every_mode_that_picks_it_and_finish_writes_every_mode():
    record = built_record()
    spec = with_gear(transfer_case_parallel(), "RangeSlv", slides="H=-10, N=0, L=+10.5")
    up = classify(record, spec)
    assert up.structural == () and up.modes_changed == ("RangeSlv along Rear",)
    assert ("RangeSlv along Rear", "4L", 66.5) in up.motion.slide_values
    stopped = finished(up, record, failures=[("x", "it would not")], slid=[("RangeSlv along Rear", "4l", 66.5)])
    values = {m.name: m.values for m in stopped.gearbox.mates if m.kind == SLIDE}
    assert values["RangeSlv along Rear"] == {"2H": 46.0, "4H": 46.0, "N": 56.0, "4L": 66.5}   # the record's keys
    for record_ in (stopped, finished(up, record)):         # never partial: a value for every mode (§1.11)
        box = record_.gearbox
        assert all(set(m.values) == set(box.modes) for m in box.mates if m.kind == SLIDE)


def test_modes_reordered_change_nothing_and_the_record_keeps_its_order():
    """§9.9."""
    record = built_record()
    spec = transfer_case_parallel()
    turned = replace(spec, modes=tuple(reversed(spec.modes)))
    up = classify(record, turned)
    assert (up.structural, up.replaced, up.modes_changed) == ((), (), ()) and up.record_matches
    assert up.motion.configurations == ("2H", "4H", "N", "4L")
    assert finished(up, record).gearbox.modes == ["2H", "4H", "N", "4L"]


def test_a_mode_renamed_by_case_only_is_the_same_configuration():
    """§9.6: the record keeps 4L; the workbook's 4l is the same configuration, so nothing changes."""
    record = built_record()
    up = classify(record, lower_4l(transfer_case_parallel()))
    assert (up.structural, up.replaced, up.modes_changed) == ((), (), ())
    box = finished(up, record).gearbox
    assert box.modes == ["2H", "4H", "N", "4L"] and {m.name: m.modes for m in box.mates}[
        "RangeSlv engages LoDog"] == ["4L"]


def test_a_record_spelt_in_another_case_than_the_workbook_updates_and_reads_back_clean(tmp_path):
    """The coordinator's end to end case: the workbook says 4l and l, the record keeps them; an Update after it
    whose edit moves 4l's place writes under the record's own spelling, and the record reads back clean."""
    record = built_record(spec=lower_4l(transfer_case_parallel()))
    spec = with_gear(lower_4l(transfer_case_parallel()), "RangeSlv", slides="H=-10, N=0, L=+10.5")
    up = classify(record, with_mode(spec, 3, name="4L"))
    assert up.structural == () and ("RangeSlv along Rear", "4l", 66.5) in up.motion.slide_values
    box = finished(up, record).gearbox
    assert box.modes == ["2H", "4H", "N", "4l"]
    assert {m.name: m.values for m in box.mates}["RangeSlv along Rear"]["4l"] == 66.5
    assert all(set(m.modes) <= set(box.modes) for m in box.mates)


@pytest.mark.parametrize("change, said", [
    (lambda s: replace(s, modes=s.modes + (Mode("4X", (("RangeSlv", "L"), ("ModeSlv", "2WD")), row=6),)),
     "The Modes sheet has a new mode, 4X, and each mode's configuration is made when the assembly is built, so it "
     "needs a new revision."),
    (lambda s: replace(s, modes=s.modes[:3]),
     "The mode 4L is no longer on the Modes sheet, and a configuration is not taken out of the assembly that was "
     "built, so it needs a new revision."),
    (lambda s: with_mode(s, 3, positions=(("RangeSlv", "N"), ("ModeSlv", "4WD"))),
     "No mode engages LoDog with RangeSlv now, and the mate RangeSlv engages LoDog, made to be on in some modes, is "
     "never left on in none, so it needs a new revision."),
    (lambda s: with_mode(with_gear(s, "ModeSlv", slides="2WD=0, 4WD=+10, X=-30"), 0,
                         positions=(("RangeSlv", "N"), ("ModeSlv", "X"))),
     "In 2H ModeSlv would now cover LoDog, which no mode engaged when the assembly was built, so it needs a new "
     "revision."),
    (lambda s: with_gear(with_gear(with_gear(s, "InPin", at="-20"), "LayGear", at="-20"), "RangeSlv",
                         slides="H=-56, N=0, L=+10"),
     "RangeSlv at its position H (-56 mm) in 2H would stand with its front face onto the Front plane (z 46 → 0), "
     "from which the slide mate RangeSlv along Rear is measured, so it needs a new revision."),
])
def test_what_an_update_cannot_carry_is_said_once_naming_the_edit(change, said):
    """J14's structural cases, §9.1's exact edit among them (LoDog engaged in no mode: its coupling would be on in
    none, and finish_update would otherwise write [] — on in every mode, both dogs engaged in 2H)."""
    record = built_record()
    up = classify(record, change(transfer_case_parallel()))
    assert said in up.structural, up.structural
    assert up.needs_new_revision


def test_a_bad_slide_spline_or_coupling_on_record_is_refused_with_a_sentence():
    record = built_record()
    for kind, field_, value, part in (("slide", "shaft", "", "with no shaft"),
                                      ("slide", "values", {"2H": 0.0}, "holds a distance other than 0"),
                                      ("couple", "gears", ["RangeSlv"], "with 1 gear where a couple mate holds 2"),
                                      ("spline", "sense", 2, "with the sense 2")):
        broken = store.link_record_from_json(store.link_record_to_json(record))
        entry = next(m for m in broken.gearbox.mates if m.kind == kind)
        setattr(entry, field_, value)
        assert part in update._bad_mates(broken.gearbox), (kind, field_)
    assert update._bad_mates(record.gearbox) == ""


def test_a_static_record_meeting_modes_is_built_again():
    a = assessed(transfer_case_parallel())
    record = built_record()
    record.gearbox.kind = motion.STATIC
    up = update.classify(record, a, exists=lambda p: True)
    assert update._STATIC_MODES in up.structural


# -- the drives on package A's fake, in every mode (B's lessons: drive each fixture in every mode after each build;
# run the mutations; pin what reaches SolidWorks). Every turn below is worked by hand from §2.3, never the code's:
# In +30° → Rear 30° in 2H and 4H (the sleeves turn with In), free in N, 7.5° in 4L (4 : 1); Front 30° in 4H, 7.5° in
# 4L, free in 2H and N; FIdler −45° for FDrive +30° (30 : 20); the low range always turns with In (LoDog 7.5°).

from test_swbuild import mode_findings  # noqa: E402,F401 - the fixture, pinned at the W8 spike's findings

ON_FAKE = {   # mode -> the gears checked: their turn, or None for free (left out of the drive)
    "2H": {"RangeSlv": 30.0, "ModeSlv": 30.0, "FrontDog": None, "FOut": None, "LoDog": 7.5},
    "4H": {"RangeSlv": 30.0, "ModeSlv": 30.0, "FrontDog": 30.0, "FOut": 30.0, "LoDog": 7.5},
    "N": {"RangeSlv": None, "ModeSlv": None, "FrontDog": None, "FOut": None, "LoDog": 7.5},
    "4L": {"RangeSlv": 7.5, "ModeSlv": 7.5, "FrontDog": 7.5, "FOut": 7.5, "LoDog": 7.5},
}
FIRST = {transfer_case_parallel: "InPin", e4_transfer_case: "Sun"}
SLIDES_ON_FAKE = {"RangeSlv along Rear": {"2H": 46.0, "4H": 46.0, "N": 56.0, "4L": 66.0},
                  "ModeSlv along Rear": {"2H": 96.0, "4H": 106.0, "N": 96.0, "4L": 106.0}}


def build_on_fake(spec, mutate=None):
    from test_swbuild import FakeSolidWorks
    sw = FakeSolidWorks()
    a = assessed(spec)
    plan = gearbox.plan_gearbox(a, None, exists=sw.exists, read_sidecar=lambda p: None)
    assert plan.refusal == "", plan.refusal
    if mutate is not None:
        plan = mutate(plan)
    result = swbuild.build_gearbox(sw, **plan.build_kwargs(), exists=sw.exists)
    done = gearbox.finish_build(plan, result, None, workbook=BOOK, digest="d1", written_by="test",
                                read_sidecar=lambda p: None, exists=sw.exists)
    return sw, result, store.link_record_from_json(store.link_record_to_json(done.record))


def wrong_on_fake(sw, record, first):
    """Every way the fake disagrees with the hand working: the turns per mode, the slide values each configuration
    holds, and each coupling's flags."""
    names = {c.name: c.gear for c in record.gearbox.components}
    driver = next(n for n, g in names.items() if g == first)
    wrong = []
    for mode, wanted in ON_FAKE.items():
        sw.show_configuration(mode)
        turns = {names[n]: round(t, 6) for n, t in sw.drive(driver, 30.0).items() if n in names}
        got = {g: turns.get(g) for g in wanted}
        if got != wanted:
            wrong.append(f"{mode}: {got}")
        sw.drive(driver, -30.0)
    for name, values in SLIDES_ON_FAKE.items():
        if sw.mate(name).own != values:
            wrong.append(f"{name}: {sw.mate(name).own}")
    for name, on in (("RangeSlv engages InDog", {"2H", "4H"}), ("RangeSlv engages LoDog", {"4L"}),
                     ("ModeSlv engages FrontDog", {"4H", "4L"})):
        flags = sw.mate(name).flags
        if flags != {m: m not in on for m in ON_FAKE}:
            wrong.append(f"{name}: {flags}")
    return wrong


@pytest.mark.parametrize("make", [transfer_case_parallel, e4_transfer_case])
def test_each_fixture_builds_on_the_fake_and_turns_in_every_mode_as_worked_by_hand(make, mode_findings):
    sw, result, record = build_on_fake(make())
    assert result.ok, result.log_lines()
    assert wrong_on_fake(sw, record, FIRST[make]) == []
    assert sw.configs == ["2H", "4H", "N", "4L"] and record.gearbox.modes == sw.configs
    assert {c.gear: c.frames["4L"]["at"][2] for c in record.gearbox.components}["RangeSlv"] == 66.0


def _invert_a_coupling(plan):
    """The coupling's sense the other way: out of ``same_way``, so its gear mate is made turning the dog against
    the sleeve."""
    mp = plan.modes_plan
    return replace(plan, modes_plan=replace(mp, same_way=tuple(n for n in mp.same_way
                                                               if n != "RangeSlv engages InDog")))


def _wrong_dog_in_2h(plan):
    """2H engaging LoDog where it should engage InDog."""
    steps = list(plan.modes_plan.steps)
    s = steps[0]
    steps[0] = replace(s, on=tuple("RangeSlv engages LoDog" if n == "RangeSlv engages InDog" else n for n in s.on),
                       off=tuple("RangeSlv engages InDog" if n == "RangeSlv engages LoDog" else n for n in s.off))
    return replace(plan, modes_plan=replace(plan.modes_plan, steps=tuple(steps)))


def _4l_value_in_2h(plan):
    steps = list(plan.modes_plan.steps)
    steps[0] = replace(steps[0], values=dict(steps[0].values, **{"RangeSlv along Rear": 66.0}))
    return replace(plan, modes_plan=replace(plan.modes_plan, steps=tuple(steps)))


@pytest.mark.parametrize("mutate, caught", [
    (_invert_a_coupling, "the coupling RangeSlv engages InDog turns its two gears the same way, and it is not listed"),
    (_wrong_dog_in_2h, "The mate RangeSlv engages LoDog is made in mode 4L, not in 2H"),
    (_4l_value_in_2h, "stands at (0, 0, 66) where the mode places it at (0, 0, 46)"),
])
def test_each_mutation_of_the_plan_is_caught(mutate, caught, mode_findings):
    """The lessons' mutations: each is refused before anything is made (A's ModesPlan.check) or fails the build's
    own mate check in the mode it touches — never a clean pass; with a clean build the drives above would differ."""
    try:
        sw, result, record = build_on_fake(transfer_case_parallel(), mutate)
    except swbuild.BuildError as exc:
        assert caught in str(exc)
        return
    assert not result.ok and any(caught in line for line in result.log_lines()), result.log_lines()


@pytest.mark.parametrize("flip", [False, True])
def test_a_spline_and_a_coupling_are_made_with_every_gear_mates_flip_and_told_only_which_way_to_turn(flip,
                                                                                                    monkeypatch):
    """W8-SPIKE.md, "SolidWorks 2024": the collinear spline's right Flip was True on 2024 and False on 2026 (the
    coupling's False on both), and the read-back named each correctly. So planning assumes no Flip for either: both
    are made with findings.GEAR_MATE_FLIP, as every gear mate is, and ``mate_senses`` / ``same_way`` say only which
    way they must turn — the same on either version."""
    monkeypatch.setattr(findings, "GEAR_MATE_FLIP", flip)
    _, plan = plan_of(transfer_case_parallel())
    made = [op for op in plan.assembly.ops if isinstance(op, Mate) and op.kind == "gear"]
    made += [op for step in plan.modes_plan.steps for op in step.ops]
    assert {op.name for op in made} >= {"ModeSlv splined to RangeSlv", "RangeSlv engages InDog",
                                        "RangeSlv engages LoDog", "ModeSlv engages FrontDog"}
    assert {op.flip for op in made} == {flip}
    assert plan.mate_senses["ModeSlv splined to RangeSlv"] is True
    assert set(plan.modes_plan.same_way) == {"RangeSlv engages InDog", "RangeSlv engages LoDog",
                                             "ModeSlv engages FrontDog"}


# -- the checks across modes (W8-PLAN §1.5, J22) --------------------------------------------------------------------

def said(spec):
    return [(d.is_error, d.message) for d in assessed(spec).report.diagnostics]


def all_modes(spec, **picks):
    return replace(spec, modes=tuple(replace(m, positions=tuple((s, picks.get(s, p)) for s, p in m.positions))
                                     for m in spec.modes))


def sliding_spur():
    """A spur that slides into mesh: S1 on In (Slides A=0, B=+20) and G2 on Out, 10 wide each."""
    shafts = (Shaft("In", "frame", "0", "0", "0", "Z+", "input", "", "1000", "1", row=2),
              Shaft("Out", "frame", "40", "0", "0", "Z+", "output", row=3))
    gears = (Gear("S1", "In", "10", "spur", "", "20", "2", "", "10", "", slides="A=+30, B=+50", row=2),
             Gear("G2", "Out", "10", "spur", "", "20", "2", "", "10", "", row=3))
    return GearboxSpec(box=Box(name="Slide", pressure_angle="20", efficiency="98"), shafts=shafts, gears=gears,
                       meshes=(Mesh("S1", "G2", row=2),), modes=(Mode("One", (("S1", "A"),), row=2),
                                                                 Mode("Two", (("S1", "B"),), row=3)),
                       sliders=("S1",))


@pytest.mark.parametrize("spec, error, sentence", [
    (with_gear(transfer_case_parallel(), "ModeSlv", slides="2WD=-38, 4WD=+10"), True,
     "Modes row 4: in N RangeSlv and ModeSlv overlap by 6 mm on Rear: two sliders on one shaft must stay clear of "
     "each other."),
    (with_mode(transfer_case_parallel(), 3, positions=(("RangeSlv", "N"), ("ModeSlv", "4WD"))), False,
     "Gears row 7: no mode engages LoDog: no sleeve covers its face in any mode."),
    (with_gear(transfer_case_parallel(), "RangeSlv", face_width="16"), False,
     "Gears row 8: RangeSlv is 16 mm long and InDog and LoDog are 14 mm apart: on its way from H to L it would hold "
     "both at once."),
    (replace(transfer_case_parallel(), modes=transfer_case_parallel().modes + (
        Mode("4X", (("RangeSlv", "H"), ("ModeSlv", "4WD")), row=6),)), False,
     "Modes row 6: 4H and 4X engage the same: they are one mode twice."),
    (all_modes(transfer_case_parallel(), ModeSlv="2WD"), True,                 # an output that turns in no mode
     "Shafts row 8: nothing settles Front's speed in any mode: no input reaches it through the meshes and couplings, "
     "so the box needs another input (or a fixed shaft) to be driven."),
    (all_modes(transfer_case_parallel(), ModeSlv="2WD"), True,
     "Shafts row 6: nothing settles FrontDrv's speed in any mode: no input reaches it through the meshes and "
     "couplings, so the box needs another input (or a fixed shaft) to be driven."),
    (sliding_spur(), False, "Meshes row 2: S1 and G2 are in mesh in no mode: no position of S1 brings it over G2."),
])
def test_each_check_across_modes_is_said_at_its_cell(spec, error, sentence):
    assert (error, sentence) in said(spec), said(spec)


@pytest.mark.parametrize("make", [transfer_case_parallel, e4_transfer_case])
def test_the_fixtures_draw_none_of_the_checks_across_modes(make):
    a = assessed(make())
    assert modes.mode_checks(a.spec, a.report.layout.placed, a.report.modes) == []


# -- the Results sheet: one block per mode (J17, J19) ---------------------------------------------------------------

def test_the_results_sheet_holds_a_block_per_mode_with_its_speeds_torques_notes_and_ratio():
    from gear_generator.workbook import export
    a = assessed(transfer_case_parallel())
    rows = export.results_sheet(a.spec, a.report, when="T").rows
    heads = [i for i, r in enumerate(rows) if r and r[0] == export.RESULTS_MODE]
    assert [rows[i][1:] for i in heads] == [["2H", "road"], ["4H"], ["N", "towing"], ["4L", "crawl"]]
    block = {rows[i][1]: {r[0]: r[1:] for r in rows[i + 2:i + 9]} for i in heads}
    ratio = {rows[i][1]: rows[i + 9][1:] for i in heads}
    assert block["2H"]["Rear"] == [1500.0, "anticlockwise", 10.0, ""]
    assert block["2H"]["Lay"] == [-750.0, "clockwise", "—", "idles in this mode: it carries no torque"]
    assert block["2H"]["Front"] == ["—", "—", "—", "turns freely in this mode"]
    assert block["4H"]["Rear"][2:] == [10.0, "shared with FrontDrv; the share depends on the loads"]
    assert block["4H"]["Front"] == [1500.0, "anticlockwise", "—", "past a split"]
    assert block["4L"]["Lo"] == [375.0, "anticlockwise", 38.416, ""]
    assert block["4L"]["Rear"] == [375.0, "anticlockwise", 38.416,
                                   "shared with FrontDrv; the share depends on the loads"]
    assert ratio == {"2H": [1.0, "In to Rear"], "4H": [1.0, "In to Rear"], "N": ["—", "neutral"],
                     "4L": [4.0, "In to Rear"]}
    labels = [r[0] if r else "" for r in rows]
    assert rows[labels.index(export.RESULTS_RATIO)][1:] == [1.0, "In to Rear"]          # the first mode's
    assert export.RESULTS_LEFT_OUT not in labels
    z = next(r for r in rows if r and r[0] == "Z")
    assert z[2:] == [5.0, 135.0]        # RangeSlv's whole travel counted (46 at H to 74 at L), inside the box


def test_a_gearbox_without_modes_keeps_w7s_results_sheet():
    from gear_generator.workbook import export
    a = direct(planetary_4to1())
    rows = export.results_sheet(a.spec, a.report, when="T").rows
    assert rows[0] == ["Shaft", "Speed (rpm)", "Turns, seen from +Z", "Torque (N·m)", "On its carrier (rpm)"]
    assert not any(r and r[0] in (export.RESULTS_MODE, export.RESULTS_MODE_RATIO) for r in rows)


def test_finish_update_never_writes_an_empty_on_set():
    """§9.1: a stopped Update whose flags would leave LoDog's coupling on in no mode keeps the on-set it had (``[]``
    reads as every mode: both dogs engaged in 2H)."""
    record = built_record()
    up = classify(record, transfer_case_parallel())
    box = finished(up, record, failures=[("x", "it would not")],
                   suppressed_in=[("RangeSlv engages LoDog", "4l")]).gearbox
    assert {m.name: m.modes for m in box.mates}["RangeSlv engages LoDog"] == ["4L"]
    assert all(m.modes for m in box.mates if m.kind == COUPLE)


def press_on_fake(sw, record, spec):
    a = assessed(spec)
    up = update.classify(record, a, exists=lambda p: True)
    assert up.refusal == "" and not up.needs_new_revision, (up.refusal, up.structural)
    result = swbuild.update_gearbox(sw, **up.update_kwargs(), exists=lambda p: True, mtime=lambda p: 5.0)
    assert result.failures == [], result.failures
    done = update.finish_update(up, result, record, digest="d2", read_sidecar=lambda p: None, mtime=lambda p: 5.0)
    return up, result, store.link_record_from_json(store.link_record_to_json(done.record))


@pytest.mark.parametrize("make", [transfer_case_parallel, e4_transfer_case])
def test_after_an_update_with_nothing_to_do_each_fixture_still_turns_in_every_mode(make, mode_findings):
    sw, _, record = build_on_fake(make())
    up, result, after = press_on_fake(sw, record, make())
    assert result.ok and after.gearbox.modes == ["2H", "4H", "N", "4L"]
    assert wrong_on_fake(sw, after, FIRST[make]) == []
    again = update.classify(after, assessed(make()), exists=lambda p: True)
    assert (again.structural, again.replaced, again.modes_changed) == ((), (), ())


def test_after_j14s_edit_the_fake_holds_the_new_value_and_flags_and_turns_as_worked_by_hand(mode_findings):
    """J14's example on the fake: 4H's ModeSlv pick 4WD → 2WD. 4H then turns as 2H (Front free), ModeSlv stands at
    96 in 4H, and FrontDog's coupling is on in 4L only; every other mode as before."""
    sw, _, record = build_on_fake(transfer_case_parallel())
    spec = with_mode(transfer_case_parallel(), 1, positions=(("RangeSlv", "H"), ("ModeSlv", "2WD")))
    up, result, after = press_on_fake(sw, record, spec)
    assert result.ok
    assert sw.mate("ModeSlv along Rear").own == {"2H": 96.0, "4H": 96.0, "N": 96.0, "4L": 106.0}
    assert sw.mate("ModeSlv engages FrontDog").flags == {"2H": True, "4H": True, "N": True, "4L": False}
    names = {c.name: c.gear for c in after.gearbox.components}
    driver = next(n for n, g in names.items() if g == "InPin")
    sw.show_configuration("4H")
    turns = {names[n]: round(t, 6) for n, t in sw.drive(driver, 30.0).items() if n in names}
    assert (turns.get("RangeSlv"), turns.get("FOut")) == (30.0, None)
    box = after.gearbox
    assert {m.name: m.values for m in box.mates}["ModeSlv along Rear"]["4H"] == 96.0
    assert {m.name: m.modes for m in box.mates}["ModeSlv engages FrontDog"] == ["4L"]
    again = update.classify(after, assessed(spec), exists=lambda p: True)
    assert (again.structural, again.modes_changed) == ((), ())


def test_a_mode_spelt_4l_builds_updates_and_reads_back_clean_on_the_fake(mode_findings):
    """§9.6 end to end on the fake: built from a workbook saying 4l (and the pick l), updated from one saying 4L and
    a moved L — the configuration keeps the name it was built with, and the record reads back clean."""
    sw, result, record = build_on_fake(lower_4l(transfer_case_parallel()))
    assert result.ok and sw.configs == ["2H", "4H", "N", "4l"]
    spec = with_mode(with_gear(lower_4l(transfer_case_parallel()), "RangeSlv", slides="H=-10, N=0, L=+10.5"), 3,
                     name="4L")
    up, result, after = press_on_fake(sw, record, spec)
    assert result.ok and sw.configs == ["2H", "4H", "N", "4l"]
    assert sw.mate("RangeSlv along Rear").own["4l"] == 66.5
    box = after.gearbox
    assert box.modes == ["2H", "4H", "N", "4l"]
    assert {m.name: m.values for m in box.mates}["RangeSlv along Rear"] == {"2H": 46.0, "4H": 46.0, "N": 56.0,
                                                                            "4l": 66.5}
    assert all(set(m.modes) <= set(box.modes) for m in box.mates)
    assert all(set(c.frames) == set(box.modes) for c in box.components)
