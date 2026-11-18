"""Package B of F2 (PLAN-PRINTED §3.1.3, §3.1.4; docs/notes-printed/F2-INTERFACES.md §2): the planners, the press's
folder, the file read back as text and the print list, all pure. Every F2 finding is None on both versions until the
probe's reviewed run sets it, so each test that plans a press patches the gate open (``gate_open``, made-up values) and
says so; the tests that leave the findings as committed show every press refused by name. No test reads a word."""

import os
import time

import pytest

from gear_generator import findings, printout, store, swbuild
from gear_generator.gears.base import Diagnostic
from gear_generator.printout import (CHANGES_ON_UPDATE, FOREIGN_RECORD, GATE, GATE_COPY, MISMATCHED_MARK,
                                     NEW_REVISION, NO_FOLDER, NO_PART, NO_RECORD, NOT_A_PART, UNSAVED_MARK,
                                     WORKBOOK_ERROR, PrintResult, Refusal)
from gear_generator.spec import GearSpec
from gear_generator.workbook.assess import Assessment
from gear_generator.workbook.model import Box, Gear, GearboxSpec, Shaft
from gear_generator.workbook.update import PartUpdate, UpdatePlan

V2026 = (34, 1, 1)
V2024 = (32, 5, 0)
NOW = time.mktime((2026, 11, 18, 14, 32, 5, 0, 0, -1))      # the press's time, local: "2026-11-18 14.32.05"
STAMP = "2026-11-18 14.32.05"
SPUR = GearSpec(module="1.5", teeth="20", face_width="8", bore="", process="printed")


@pytest.fixture
def gate_open(monkeypatch):
    """The gate as a reviewed probe run might open it on 2026 (made up: every F2 finding is None in findings.py)."""
    monkeypatch.setattr(findings, "SAVE_AS_COPY", 2)
    monkeypatch.setattr(findings, "STEP_EXPORT_ON_2026", True)


def nothing_exists(_path):
    return False


def is_dir(path):
    """Every Output folder a test names (under /) is a folder on disk."""
    return path.startswith("/")


# -- the gate ------------------------------------------------------------------------------------------------------------


def test_with_every_f2_finding_unset_both_planners_refuse_with_gate_copy_on_both_versions(f2_unmeasured):
    for version in (V2026, V2024, ()):
        assert printout.gate(version) == Refusal(GATE_COPY)
        assert printout.form_print(None, r"C:\G\Gear.SLDPRT", r"C:\Out", version).refusal == Refusal(GATE_COPY)
        plan = printout.workbook_print(None, None, None, r"C:\Out", version)
        assert plan.refusal == Refusal(GATE_COPY) and plan.parts == () and plan.folder == ""
        assert plan.revision == tuple(version)


def test_with_save_as_copy_set_a_version_whose_step_export_is_unset_is_gate_by_year_and_revision(f2_unmeasured,
                                                                                                  monkeypatch):
    monkeypatch.setattr(findings, "SAVE_AS_COPY", 2)
    monkeypatch.setattr(findings, "STEP_EXPORT_ON_2026", True)
    assert printout.gate(V2026) is None
    assert printout.gate(V2024) == Refusal(GATE, (), {"year": "2024", "revision": "32.5.0"})
    assert printout.gate((35, 0, 0)) == Refusal(GATE, (), {"year": "2027", "revision": "35.0.0"})   # no finding at all
    assert printout.gate(()) == Refusal(GATE)                                                    # none connected
    monkeypatch.setattr(findings, "STEP_EXPORT_ON_2026", False)
    assert printout.gate(V2026).code == GATE


def test_the_planners_answer_the_gate_before_anything_else(f2_unmeasured, monkeypatch):
    monkeypatch.setattr(findings, "SAVE_AS_COPY", 2)
    plan = printout.form_print(None, "", "", V2024)              # nothing active, no record: the gate still first
    assert plan.refusal == Refusal(GATE, (), {"year": "2024", "revision": "32.5.0"})
    assert printout.workbook_print(None, None, None, "", ()).refusal == Refusal(GATE)


# -- the form ------------------------------------------------------------------------------------------------------------


def sidecar_for(path, spec=SPUR, variables=(("No. of Teeth", "20"),), features=("Blank", "Teeth")):
    record = store.GearRecord(spec=spec.to_dict(), variables=[list(v) for v in variables], features=list(features))
    return store.Sidecar(part_path=path, record=record)


@pytest.mark.parametrize("path,parts", [("", ()), (r"C:\G\RangeBox.SLDASM", ("RangeBox.SLDASM",))])
def test_the_form_refuses_not_a_part_when_nothing_or_no_part_is_active(gate_open, path, parts):
    plan = printout.form_print(None, path, r"C:\Out", V2026, now=NOW, exists=nothing_exists)
    assert plan.refusal == Refusal(NOT_A_PART, parts) and plan.folder == "" and plan.parts == ()


def test_the_form_refuses_no_record_for_a_part_without_a_gear_json(gate_open):
    plan = printout.form_print(None, r"C:\G\Part1.SLDPRT", r"C:\Out", V2026, now=NOW, exists=nothing_exists)
    assert plan.refusal == Refusal(NO_RECORD, ("Part1.SLDPRT",), {"record": "missing"})


def test_the_form_refuses_no_record_telling_a_gear_json_that_does_not_read_from_one_missing(gate_open):
    """F2-REVIEW S5: the form hands None for both; the planner tells them apart by the file beside the part."""
    beside = {r"C:\G\Part1.gear.json"}
    plan = printout.form_print(None, r"C:\G\Part1.SLDPRT", r"C:\Out", V2026, now=NOW, exists=beside.__contains__)
    assert plan.refusal == Refusal(NO_RECORD, ("Part1.SLDPRT",), {"record": "unreadable"})


def test_the_forms_plan_is_the_active_part_into_a_folder_named_by_the_press(gate_open):
    path = r"C:\G\Gear_m1.5_N20_P.SLDPRT"
    plan = printout.form_print(sidecar_for(path), path, "/out", V2026, now=NOW, exists=nothing_exists, isdir=is_dir)
    assert plan.refusal is None
    assert plan.folder == os.path.join("/out", "print", STAMP)
    assert (plan.revision, plan.name, plan.pressed) == (V2026, "Gear_m1.5_N20_P", NOW)
    (part,) = plan.parts
    assert (part.path, part.stem, part.rows, part.count, part.process) == (path, "Gear_m1.5_N20_P", (), 1, "printed")
    assert part.spec == SPUR and part.user_features == ()
    assert part.variables == (("No. of Teeth", "20"),) and part.made == ("Blank", "Teeth")
    assert printout.step_name(part) == "Gear_m1.5_N20_P.step"


def test_each_parts_span_is_package_as_span_of_its_derived_gear_and_recipe(gate_open, monkeypatch):
    seen = []

    def fake_span(derived, recipe):
        seen.append((type(derived).__name__, recipe))
        return printout.SpanReading("span", 3, 11.2, 11.2, 31.0)

    monkeypatch.setattr(printout, "span", fake_span)
    path = r"C:\G\Gear_m1.5_N20_P.SLDPRT"
    (part,) = printout.form_print(sidecar_for(path), path, "/out", V2026, now=NOW, exists=nothing_exists, isdir=is_dir).parts
    assert seen == [("SpurDerived", "A")] and part.span.k == 3


def test_a_parts_r2_revision_prints_as_r2_and_nothing_else_gains_r2(gate_open):
    path = r"C:\G\Gear_m1.5_N20_P_r2.SLDPRT"
    taken = {os.path.join("/out", "print", STAMP)}
    plan = printout.form_print(sidecar_for(path), path, "/out", V2026, now=NOW, exists=taken.__contains__, isdir=is_dir)
    assert printout.step_name(plan.parts[0]) == "Gear_m1.5_N20_P_r2.step"
    assert plan.folder == os.path.join("/out", "print", STAMP + " (2)")        # the folder counts, the file does not
    assert "_r2" not in plan.folder


def test_the_folder_counts_on_past_every_name_taken():
    base = os.path.join("/out", "print", STAMP)
    taken = {base, base + " (2)", base + " (3)"}
    assert printout.press_folder("/out", NOW, taken.__contains__) == base + " (4)"
    assert printout.free_folder(base + " (2)", taken.__contains__) == base + " (4)"    # never "... (2) (2)"
    assert printout.free_folder(base + " (9)", taken.__contains__) == base + " (9)"


@pytest.mark.parametrize("folder", ["", r"C:\Gone"])
def test_the_form_refuses_no_folder_for_an_output_folder_empty_or_not_on_disk(gate_open, folder):
    """F2-REVIEW S4 (B's fallback to the part's own folder rejected): NO_FOLDER, naming the folder."""
    path = "/g/Gear_m1.5_N20_P.SLDPRT"
    plan = printout.form_print(sidecar_for(path), path, folder, V2026, now=NOW, exists=nothing_exists, isdir=is_dir)
    assert plan.refusal == Refusal(NO_FOLDER, (), {"folder": folder}) and plan.folder == "" and plan.parts == ()


def test_the_form_checks_the_output_folder_on_disk_by_default(gate_open, tmp_path):
    path = str(tmp_path / "Gear_m1.5_N20_P.SLDPRT")
    assert printout.form_print(sidecar_for(path), path, str(tmp_path), V2026, now=NOW).refusal is None
    assert printout.form_print(sidecar_for(path), path, str(tmp_path / "gone"), V2026, now=NOW).refusal.code == NO_FOLDER


# -- the Workbook window --------------------------------------------------------------------------------------------------

PART_A = r"C:\Box\Gear_m1.5_N20_P.SLDPRT"
PART_B = r"C:\Box\Gear_m1.5_N40_P.SLDPRT"
PART_PLANET = r"C:\Box\Gear_m1_N12_P.SLDPRT"


def gearbox_spec(planet_copies="3"):
    shafts = (Shaft("S1"), Shaft("S2"), Shaft("P", mounted_on="S1", copies=planet_copies))
    gears = (Gear("G1", shaft="S1"), Gear("G2", shaft="S2"), Gear("G3", shaft="S2"), Gear("Planet", shaft="P"))
    return GearboxSpec(box=Box(name="Reducer"), shafts=shafts, gears=gears, source_path=r"C:\Box\Reducer.xlsx")


def assessment(spec=None, **kw):
    spec = spec or gearbox_spec()
    return Assessment(read=spec, read_diagnostics=[], spec=spec, **kw)


def entry(path, gears, spec=SPUR, variables=(("No. of Teeth", "20"),)):
    return store.PartEntry(path=path, gears=list(gears), spec=spec.to_dict(), variables=[list(v) for v in variables])


def record(entries=None, **kw):
    entries = entries if entries is not None else [entry(PART_A, ["G1"]), entry(PART_B, ["G2", "G3"]),
                                                   entry(PART_PLANET, ["Planet"])]
    return store.LinkRecord(workbook=r"C:\Box\Reducer.xlsx", parts=entries, **kw)


def update_for(rec, changed=(), made=("Blank", "Teeth"), **kw):
    parts = tuple(PartUpdate(e.path, tuple(e.gears), SPUR, None, (), changed=e.path in changed, made=tuple(made))
                  for e in rec.current_parts())
    return UpdatePlan(parts=parts, **kw)


def on_disk(path):
    """The parts (Windows paths) are on disk; no press folder (under /) is there yet."""
    return not path.startswith("/")


def plan_window(rec, a=None, update=None, *, exists=on_disk, version=V2026, folder="/out", **kw):
    a = a if a is not None else assessment()
    update = update if update is not None else update_for(rec)
    return printout.workbook_print(rec, a, update, folder, version, now=NOW, exists=exists, isdir=is_dir, **kw)


def test_the_window_plans_every_current_part_once_with_its_rows_and_counts(gate_open):
    plan = plan_window(record())
    assert plan.refusal is None
    assert plan.name == "Reducer" and plan.folder == os.path.join("/out", "print", STAMP)
    assert [(p.stem, p.rows, p.count) for p in plan.parts] == [
        ("Gear_m1.5_N20_P", ("G1",), 1), ("Gear_m1.5_N40_P", ("G2", "G3"), 2), ("Gear_m1_N12_P", ("Planet",), 3)]
    assert all(p.made == ("Blank", "Teeth") and p.variables == (("No. of Teeth", "20"),) for p in plan.parts)


def test_a_planets_count_is_its_shafts_copies(gate_open):
    rec = record([entry(PART_PLANET, ["Planet"]), entry(PART_A, ["G1", "G2", "G3"])])
    plan = plan_window(rec, assessment(gearbox_spec(planet_copies="4")))
    assert [(p.stem, p.count) for p in plan.parts] == [("Gear_m1_N12_P", 4), ("Gear_m1.5_N20_P", 3)]


def test_hubs_dogs_and_sleeves_are_parts_like_any_other_and_only_current_parts_print(gate_open):
    hub = r"C:\Box\Hub_S1.SLDPRT"
    rec = record([entry(PART_A, ["G1", "G2", "G3", "Planet"]), entry(hub, ["G1"], GearSpec(kind="hub"))])
    rec.gearbox = store.GearboxRecord(name="Reducer", assembly=r"C:\Box\Reducer.SLDASM",
                                      components=[store.ComponentEntry("G1", PART_A, "a-1"),
                                                  store.ComponentEntry("H", hub, "h-1")])
    rec.parts.append(entry(r"C:\Box\Old.SLDPRT", ["G1"]))        # on record, no component names it: not current
    plan = plan_window(rec)
    assert [p.stem for p in plan.parts] == ["Gear_m1.5_N20_P", "Hub_S1"]
    assert plan.parts[1].spec.kind == "hub"


def test_the_users_features_on_record_are_named_per_part(gate_open):
    rec = record()
    rec.gearbox = store.GearboxRecord(name="Reducer", user_work=store.UserWorkEntry(features=[
        store.UserFeatureEntry(PART_B, "User Keyway"), store.UserFeatureEntry(PART_B, "User Keyway"),
        store.UserFeatureEntry(r"C:\Box\Reducer.SLDASM", "Cut-Extrude1")]))
    plan = plan_window(rec)
    assert [p.user_features for p in plan.parts] == [(), ("User Keyway",), ()]


def test_foreign_record(gate_open):
    plan = plan_window(record(), update=UpdatePlan(refusal="another's", foreign_record=r"C:\Other\Box.xlsx"))
    assert plan.refusal == Refusal(FOREIGN_RECORD)


@pytest.mark.parametrize("kw", [dict(provisional=True), dict(chosen=("a fix",))])
def test_workbook_error_for_a_provisional_read_or_a_fix_not_exported(gate_open, kw):
    assert plan_window(record(), assessment(**kw)).refusal == Refusal(WORKBOOK_ERROR)


def test_workbook_error_for_an_error_or_no_assessment(gate_open):
    a = assessment()
    a.diagnostics.append(Diagnostic("error", "Gears!F3 is not a number."))
    assert a.errors
    assert plan_window(record(), a).refusal == Refusal(WORKBOOK_ERROR)
    assert printout.workbook_print(record(), None, None, "/out", V2026).refusal == Refusal(WORKBOOK_ERROR)


def test_workbook_error_when_update_cannot_say_what_it_would_change(gate_open):
    rec = record()
    assert printout.workbook_print(rec, assessment(), None, "/out", V2026, exists=on_disk).refusal == \
        Refusal(WORKBOOK_ERROR)
    assert plan_window(rec, update=UpdatePlan(refusal="the assembly is not made yet")).refusal == \
        Refusal(WORKBOOK_ERROR)


def test_no_part_names_each_row_without_one_and_each_part_not_on_disk(gate_open):
    rec = record([entry(PART_A, ["G1"]), entry(PART_B, ["G2"])])
    plan = plan_window(rec, exists=lambda p: on_disk(p) and p != PART_B)
    assert plan.refusal == Refusal(NO_PART, ("G3", "Planet", "Gear_m1.5_N40_P"),
                                   {"G3": "no part", "Planet": "no part", "Gear_m1.5_N40_P": "not on disk"})


def test_nothing_built_is_no_part_for_every_row(gate_open):
    plan = printout.workbook_print(None, assessment(), None, "/out", V2026, exists=on_disk)
    assert plan.refusal.code == NO_PART and plan.refusal.parts == ("G1", "G2", "G3", "Planet")


@pytest.mark.parametrize("field,code", [("unsaved", UNSAVED_MARK), ("mismatched", MISMATCHED_MARK)])
def test_the_records_marks_refuse_naming_each_part(gate_open, field, code):
    rec = record(**{field: {PART_B.lower(): 1.0, r"C:\Box\Reducer.SLDASM": 2.0}})
    assert plan_window(rec).refusal == Refusal(code, ("Gear_m1.5_N40_P",))


def test_unsaved_comes_before_mismatched(gate_open):
    rec = record(unsaved={PART_B: 1.0}, mismatched={PART_A: 1.0})
    assert plan_window(rec).refusal.code == UNSAVED_MARK


def test_a_mark_on_the_layout_or_the_assembly_alone_does_not_refuse(gate_open):
    rec = record(unsaved={r"C:\Box\Reducer_Layout.SLDPRT": 1.0}, mismatched={r"C:\Box\Reducer.SLDASM": 1.0})
    assert plan_window(rec).refusal is None


def test_changes_on_update_for_values_update_would_carry(gate_open):
    rec = record()
    plan = plan_window(rec, update=update_for(rec, changed=(PART_A, PART_B)))
    assert plan.refusal == Refusal(CHANGES_ON_UPDATE, ("Gear_m1.5_N20_P", "Gear_m1.5_N40_P"),
                                   {"Gear_m1.5_N20_P": "values", "Gear_m1.5_N40_P": "values"})


def test_a_part_that_needs_a_new_revision_is_new_revision_not_changes_on_update(gate_open):
    """F2-REVIEW M1: with a structural change Update is never run (UpdatePlan.needs_new_revision), so a part it would
    change, whether its values or a new part, is NEW_REVISION: the user is told to use Build again…."""
    rec = record()
    structural = ("Gear_m1.5_N40_P (G2 and G3): its Part name now makes X.SLDPRT, and a built part's file is never "
                  "renamed, so it needs a new part.",)
    update = update_for(rec, changed=(PART_A, PART_B), structural=structural)
    assert update.needs_new_revision
    plan = plan_window(rec, update=update)
    assert plan.refusal == Refusal(NEW_REVISION, ("Gear_m1.5_N20_P", "Gear_m1.5_N40_P"),
                                   {"Gear_m1.5_N20_P": "values", "Gear_m1.5_N40_P": "new part"})


def test_values_update_would_change_while_a_part_file_is_missing_are_new_revision(gate_open):
    rec = record()
    update = update_for(rec, changed=(PART_A,), missing=(r"C:\Box\Reducer.SLDASM",))
    assert plan_window(rec, update=update).refusal == Refusal(NEW_REVISION, ("Gear_m1.5_N20_P",),
                                                              {"Gear_m1.5_N20_P": "values"})


def test_a_shared_part_whose_rows_now_differ_needs_a_new_revision(gate_open):
    rec = record()
    update = UpdatePlan(parts=tuple(p for p in update_for(rec).parts if p.path != PART_B),   # classify leaves it out
                        structural=("G2 and G3 share Gear_m1.5_N40_P.SLDPRT, but G3 now differs from G2, so they need "
                                    "parts of their own.",))
    assert plan_window(rec, update=update).refusal == Refusal(NEW_REVISION, ("Gear_m1.5_N40_P",),
                                                              {"Gear_m1.5_N40_P": "new part"})


def test_a_gear_update_would_add_in_place_is_changes_on_update_not_no_part(gate_open):
    rec = record([entry(PART_A, ["G1"]), entry(PART_B, ["G2"]), entry(PART_PLANET, ["Planet"])])
    added = swbuild.AddedGear("G3", "g3", r"C:\Box\Gear_m1.5_N13_P.SLDPRT", build=object())
    update = update_for(rec, in_place=swbuild.InPlace(added=(added,)))
    assert plan_window(rec, update=update).refusal == Refusal(CHANGES_ON_UPDATE, ("Gear_m1.5_N13_P",),
                                                              {"Gear_m1.5_N13_P": "new part"})


def test_e3_a_change_only_to_the_layout_or_the_assembly_does_not_refuse(gate_open):
    rec = record()
    update = update_for(rec, moved_shafts=("S2",), replaced=("G2",), modes_changed=("slide",),
                        structural=("Shaft S9 is new, and the layout part has no axis for it.",),
                        missing=(r"C:\Box\Reducer.SLDASM",))
    plan = plan_window(rec, update=update)
    assert plan.refusal is None and len(plan.parts) == 3


def test_a_part_whose_rows_have_all_gone_from_the_workbook_is_left_out_not_refused(gate_open):
    rec = record([entry(PART_A, ["G1", "G2", "G3", "Planet"]), entry(r"C:\Box\Gone.SLDPRT", ["G9"])])
    plan = plan_window(rec)
    assert plan.refusal is None and [p.stem for p in plan.parts] == ["Gear_m1.5_N20_P"]


@pytest.mark.parametrize("folder", ["", r"C:\Gone"])
def test_the_window_refuses_no_folder_last_for_an_output_folder_empty_or_not_on_disk(gate_open, folder):
    """F2-REVIEW S4 (B's fallbacks to the assessment's and the workbook's folders rejected)."""
    rec = record()
    assert plan_window(rec, assessment(folder="/box"), folder=folder).refusal == Refusal(NO_FOLDER, (),
                                                                                          {"folder": folder})
    assert plan_window(rec, update=update_for(rec, changed=(PART_A,)), folder=folder).refusal.code == \
        CHANGES_ON_UPDATE                                                       # every other refusal first


def test_foreign_record_from_what_the_window_knows(gate_open):
    """F2-REVIEW S8: the window makes no Update plan for another workbook's record and passes the other workbook."""
    plan = plan_window(record(), update=update_for(record()), foreign_record=r"C:\Other\Box.xlsx")
    assert plan.refusal == Refusal(FOREIGN_RECORD)
    assert printout.workbook_print(None, None, None, "/out", V2026, foreign_record=r"C:\Other\Box.xlsx",
                                   isdir=is_dir).refusal == Refusal(FOREIGN_RECORD)


# -- the file read back as text (§3.1.4) ----------------------------------------------------------------------------------

MM = "( LENGTH_UNIT ( ) NAMED_UNIT ( * ) SI_UNIT ( .MILLI., .METRE. ) )"


def step(schema="AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }", unit=MM, solids=1, closed=1, open_shells=0, surface=0,
         points=((16.5, 0.0, 0.0), (0.0, -16.5, 8.0), (3.0, 4.0, 4.0)), end="END-ISO-10303-21;", extra=(),
         context=True):
    """A small made-up STEP file of SolidWorks' shape: FILE_NAME over two lines, strings holding a semicolon and entity
    names, the unit a complex instance assigned by the representation context; ``extra`` whole numbered instances."""
    lines = ["ISO-10303-21;", "HEADER;", "FILE_DESCRIPTION (( 'STEP AP214' ),", "    '1' );",
             "FILE_NAME ('Gear.STEP',", "    '2026-11-18T22:10:05', ( 'an author' ), ( 'an org; MANIFOLD_SOLID_BREP(' ),",
             "    'SwSTEP 2.0', 'SolidWorks 2026', '' );", f"FILE_SCHEMA (( '{schema}' ));", "ENDSEC;", "", "DATA;",
             "#1 = PRODUCT ( 'MANIFOLD_SOLID_BREP( in a name; OPEN_SHELL(', 'x', '', ( #2 ) ) ;",
             f"#2 = {unit} ;",
             "#3 = ( NAMED_UNIT ( * ) PLANE_ANGLE_UNIT ( ) SI_UNIT ( $, .RADIAN. ) ) ;"]
    if context:
        lines.append("#4 = ( GEOMETRIC_REPRESENTATION_CONTEXT ( 3 ) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT ( ( #5 ) ) "
                     "GLOBAL_UNIT_ASSIGNED_CONTEXT ( ( #2, #3 ) ) REPRESENTATION_CONTEXT ( 'NONE', 'WORKASPACE' ) ) ;")
    n = 10
    for _ in range(solids):
        lines.append(f"#{n} = MANIFOLD_SOLID_BREP ( 'Body', #{n + 1} ) ;")
        lines.append(f"#{n + 1} = CLOSED_SHELL ( 'NONE', ( #1 ) ) ;")
        n += 2
    for kind, many in (("CLOSED_SHELL", max(0, closed - solids)), ("OPEN_SHELL", open_shells),
                       ("SHELL_BASED_SURFACE_MODEL", surface)):
        for _ in range(many):
            lines.append(f"#{n} = {kind} ( 'NONE', ( #1 ) ) ;")
            n += 1
    for x, y, z in points:
        lines += [f"#{n} = CARTESIAN_POINT ( 'NONE',  ( {x!r}, {y!r},", f"  {z!r} ) ) ;",
                  f"#{n + 1} = VERTEX_POINT ( 'NONE', #{n} ) ;"]
        n += 2
    lines += [f"{line} ;" for line in extra]
    lines += ["ENDSEC;", end]
    return "\r\n".join(lines) + "\r\n"


GEAR = printout.print_part(r"C:\G\Gear_m1.5_N20_P.SLDPRT", SPUR.to_dict())     # d_a 33, face 8


@pytest.mark.parametrize("schema,ap", [
    ("CONFIG_CONTROL_DESIGN", "AP203"),
    ("AP203_CONFIGURATION_CONTROLLED_3D_DESIGN_OF_MECHANICAL_PARTS_AND_ASSEMBLIES_MIM_LF { 1 0 10303 403 1 1 4 }",
     "AP203"),
    ("AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }", "AP214"),
    ("AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF { 1 0 10303 442 1 1 4 }", "AP242"),
    ("automotive_design", "AP214"),
])
def test_each_accepted_schema_passes_matched_by_its_names_prefix(schema, ap):
    reading = printout.read_step(step(schema=schema), GEAR)
    assert reading.reason is None and reading.ap == ap
    assert reading.schema == schema.split(" ")[0].upper()
    assert printout.check_step(step(schema=schema), GEAR) is None


@pytest.mark.parametrize("schema", ["STRUCTURAL_ANALYSIS_DESIGN { 1 0 10303 209 }", "IGES_IN_STEP", "", "MY_DESIGN"])
def test_any_other_schema_is_refused(schema):
    assert printout.check_step(step(schema=schema), GEAR) == printout.SCHEMA


@pytest.mark.parametrize("unit,label,per_mm", [
    (MM, "MILLI.METRE", 1.0),
    ("( LENGTH_UNIT ( ) NAMED_UNIT ( * ) SI_UNIT ( $, .METRE. ) )", "METRE", 0.001),
    ("( LENGTH_UNIT ( ) NAMED_UNIT ( * ) SI_UNIT ( .CENTI., .METRE. ) )", "CENTI.METRE", 0.1),
])
def test_an_si_length_unit_with_or_without_a_prefix_reads_and_scales_the_vertices(unit, label, per_mm):
    points = ((16.5 * per_mm, 0.0, 0.0), (0.0, 0.0, 8.0 * per_mm))
    reading = printout.read_step(step(unit=unit, points=points), GEAR)
    assert (reading.reason, reading.unit, reading.extent) == (None, label, "checked")


def test_an_inch_file_reads_its_unit_from_the_context_though_it_also_holds_the_si_millimetre(monkeypatch):
    """An inch file as SolidWorks writes one holds the inch, the SI millimetre its conversion refers to, and the context
    assigning the inch (F2-0-REVIEW S3)."""
    inch = "( CONVERSION_BASED_UNIT ( 'INCH', #90 ) LENGTH_UNIT ( ) NAMED_UNIT ( #91 ) )"
    extra = ("#90 = LENGTH_MEASURE_WITH_UNIT ( LENGTH_MEASURE ( 25.4 ), #92 )",
             "#91 = DIMENSIONAL_EXPONENTS ( 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 )", f"#92 = {MM}")
    text = step(unit=inch, extra=extra, points=((16.5 / 25.4, 0.0, 0.0), (0.0, 0.0, 8.0 / 25.4)))
    reading = printout.read_step(text, GEAR)
    assert (reading.reason, reading.unit) == (None, "INCH")
    monkeypatch.setattr(findings, "EXTENT_MEASURED", True)
    assert printout.read_step(text, GEAR).extent == "checked"               # the vertices read in inches
    # Without the context every LENGTH_UNIT is read, the inch and the millimetre differ, and the unit cannot be read:
    # the reason the context is the one read.
    assert printout.check_step(text.replace("GLOBAL_UNIT_ASSIGNED_CONTEXT", "OTHER_CONTEXT"), GEAR) == printout.UNIT


def test_a_foot_reads_and_an_unknown_conversion_does_not():
    foot = "( CONVERSION_BASED_UNIT ( 'FOOT', #3 ) LENGTH_UNIT ( ) NAMED_UNIT ( * ) )"
    assert printout.read_step(step(unit=foot), GEAR).unit == "FOOT"
    cubit = "( CONVERSION_BASED_UNIT ( 'CUBIT', #3 ) LENGTH_UNIT ( ) NAMED_UNIT ( * ) )"
    assert printout.check_step(step(unit=cubit), GEAR) == printout.UNIT


@pytest.mark.parametrize("text,reason", [
    (step(end="ENDSEC;"), printout.FRAME),
    (step()[:-40], printout.FRAME),                                        # cut short inside a statement
    ("", printout.FRAME),
    ("<html>not a STEP file</html>", printout.FRAME),
    (step(solids=0, closed=1), printout.SOLIDS),
    (step(solids=2, closed=2), printout.SOLIDS),
    (step().replace("#11 = CLOSED_SHELL", "#11 = CONNECTED_FACE_SET"), printout.SOLIDS),
    (step(open_shells=1), printout.OPEN_SHELL),
    (step(surface=1), printout.SURFACE_MODEL),
    (step(unit="( LENGTH_UNIT ( ) NAMED_UNIT ( * ) SI_UNIT ( .MILLI., .GRAM. ) )"), printout.UNIT),
    (step(unit="( NAMED_UNIT ( * ) PLANE_ANGLE_UNIT ( ) SI_UNIT ( $, .RADIAN. ) )", context=False), printout.UNIT),
    (step(unit="( LENGTH_UNIT ( ) NAMED_UNIT ( * ) SI_UNIT ( .NANO., .METRE. ) )"), printout.UNIT),
])
def test_each_fault_is_refused_by_its_reason(text, reason):
    assert printout.check_step(text, GEAR) == reason


def test_the_first_reason_in_order_is_the_one_given():
    assert printout.check_step(step(schema="IGES_IN_STEP", solids=0, open_shells=1, end="ENDSEC;"), GEAR) == \
        printout.FRAME
    assert printout.check_step(step(schema="X", solids=2, surface=1), GEAR) == printout.SCHEMA
    assert printout.check_step(step(solids=2, open_shells=1), GEAR) == printout.SOLIDS


def test_a_name_inside_a_quoted_string_or_a_comment_is_never_an_instance():
    text = step().replace("DATA;", "DATA;\r\n/* #99 = MANIFOLD_SOLID_BREP ( 'x', #11 ) ; */")
    assert printout.check_step(text, GEAR) is None


def test_the_extent_is_a_fact_skipped_while_not_measured(f2_unmeasured):
    reading = printout.read_step(step(points=((99.0, 0.0, 0.0),)), GEAR)
    assert (reading.reason, reading.extent) == (None, "skipped: not measured")


def test_with_the_findings_as_committed_the_gate_is_open_on_both_versions_and_the_size_is_checked():
    assert printout.gate(V2026) is None and printout.gate(V2024) is None
    assert printout.read_step(step(), GEAR).extent == "checked"
    assert printout.check_step(step(points=((17.0, 0.0, 0.0), (0.0, 0.0, 8.0))), GEAR) == printout.EXTENT


def test_the_extent_once_measured_checks_d_a_over_2_and_the_face(monkeypatch):
    monkeypatch.setattr(findings, "EXTENT_MEASURED", True)
    assert printout.read_step(step(), GEAR) == printout.StepReading(None, "AUTOMOTIVE_DESIGN", "AP214",
                                                                    "MILLI.METRE", "checked")
    assert printout.check_step(step(points=((16.5, 0.0, 0.0), (0.0, 0.0, 8.009))), GEAR) is None
    assert printout.check_step(step(points=((16.52, 0.0, 0.0), (0.0, 0.0, 8.0))), GEAR) == printout.EXTENT
    assert printout.check_step(step(points=((16.5, 0.0, 0.0), (0.0, 0.0, 9.0))), GEAR) == printout.EXTENT
    assert printout.check_step(step(points=((0.0165, 0.0, 0.0), (0.0, 0.0, 0.008)),
                                    unit="( LENGTH_UNIT ( ) NAMED_UNIT ( * ) SI_UNIT ( $, .METRE. ) )"), GEAR) is None
    assert printout.check_step(step(points=()), GEAR) == printout.EXTENT                  # no vertex: cannot hold


@pytest.mark.parametrize("spec,why", [
    (GearSpec(kind="bevel", module="2", teeth="20", mate_teeth="40", face_width="8", bore=""), "bevel"),
    (GearSpec(kind="spur", teeth_side="internal", module="1", teeth="60", face_width="8", bore=""), "ring"),
    (GearSpec(kind="sleeve", module="1", teeth="20", face_width="8", bore=""), "sleeve"),
    (GearSpec(kind="dog", module="1", teeth="20", face_width="8", bore=""), "dog"),
    (GearSpec(kind="hub", module="1", teeth="20", face_width="8", bore=""), "hub"),
    (GearSpec(kind="herringbone", module="2", teeth="20", helix_angle="15", face_width="14", bore=""), "herringbone"),
])
def test_the_extent_is_never_checked_on_a_bevel_ring_sleeve_dog_hub_or_herringbone(monkeypatch, spec, why):
    monkeypatch.setattr(findings, "EXTENT_MEASURED", True)
    part = printout.print_part(r"C:\G\X.SLDPRT", spec.to_dict())
    reading = printout.read_step(step(points=((99.0, 0.0, 0.0),)), part)
    assert (reading.reason, reading.extent) == (None, f"skipped: {why}")


def test_the_extent_is_never_a_refusal_for_a_part_holding_the_users_features(monkeypatch):
    monkeypatch.setattr(findings, "EXTENT_MEASURED", True)
    part = printout.print_part(r"C:\G\Gear.SLDPRT", SPUR.to_dict(), user_features=("Boss-Extrude1",))
    reading = printout.read_step(step(points=((40.0, 0.0, 0.0), (0.0, 0.0, 30.0))), part)
    assert (reading.reason, reading.extent) == (None, "skipped: user features")


def test_the_extent_is_checked_on_a_machined_gear_too(monkeypatch):
    monkeypatch.setattr(findings, "EXTENT_MEASURED", True)
    part = printout.print_part(r"C:\G\Gear.SLDPRT", GearSpec(module="1.5", teeth="20", face_width="8").to_dict())
    assert part.process == "machined"
    assert printout.read_step(step(), part).extent == "checked"


def test_new_revision_and_no_folder_are_planning_codes():
    assert printout.NEW_REVISION == "NEW_REVISION" and printout.NEW_REVISION in printout.PLANNING_CODES
    assert printout.NO_FOLDER == "NO_FOLDER" and printout.NO_FOLDER in printout.PLANNING_CODES


def test_the_codes_and_reasons_are_the_interfaces():
    assert printout.REASONS == (printout.FRAME, printout.SCHEMA, printout.SOLIDS, printout.OPEN_SHELL,
                                printout.SURFACE_MODEL, printout.UNIT, printout.EXTENT)
    assert all(getattr(printout, code) == code for code in printout.CODES)
    assert set(printout.EXTENT_SKIPPED) >= {"bevel", "ring", "sleeve", "dog", "hub", "herringbone", "user features",
                                            "not measured"}


# -- the result and the list ----------------------------------------------------------------------------------------------


def test_a_result_must_say_whether_the_active_document_was_put_back():
    with pytest.raises(TypeError):
        PrintResult(written=(), folder="")                     # no default of True (F2-0-REVIEW S7)
    assert PrintResult(active_restored=False).active_restored is False


def test_the_list_is_written_utf8_into_the_press_folder_and_never_over_a_file(tmp_path):
    result = PrintResult(folder=str(tmp_path), active_restored=True)
    path = printout.write_list(result, "Reducer — span over 3 teeth 11.209\n")
    assert path == os.path.join(str(tmp_path), "print list.txt")
    assert open(path, encoding="utf-8").read() == "Reducer — span over 3 teeth 11.209\n"
    with pytest.raises(FileExistsError):
        printout.write_list(result, "something else")
    assert open(path, encoding="utf-8").read() == "Reducer — span over 3 teeth 11.209\n"


def test_with_list_says_truly_whether_the_list_was_written(tmp_path):
    """F2-REVIEW S2: the result after the write says the list's path, or why it could not be written; never both."""
    result = PrintResult(folder=str(tmp_path), active_restored=True)
    assert (result.list_path, result.list_error) == ("", "")
    done = printout.with_list(result, "the list")
    assert done.list_path == os.path.join(str(tmp_path), "print list.txt") and done.list_error == ""
    again = printout.with_list(result, "another list")                         # a file there already: never over it
    assert again.list_path == "" and again.list_error and "exists" in again.list_error.lower()
    gone = printout.with_list(PrintResult(folder=str(tmp_path / "gone"), active_restored=True), "the list")
    assert gone.list_path == "" and gone.list_error
    assert open(done.list_path, encoding="utf-8").read() == "the list"
    alone = PrintResult(active_restored=True)
    assert printout.with_list(alone, "the list") is alone


def test_the_list_is_not_written_without_a_folder(tmp_path):
    assert printout.write_list(PrintResult(active_restored=True), "text") == ""
    assert list(tmp_path.iterdir()) == []
