"""Package B of F2: the press's job, ``swbuild.print_parts`` (PLAN-PRINTED §3.1.3, "How each part is reached";
docs/notes-printed/F2-INTERFACES.md §5), against test_swbuild's ``FakeSolidWorks``, and swcom's members it adds.

The F2 findings are set alike on both versions since the probe's reruns were reviewed (F2-PROBES-REVIEW.md); each test
still sets the per-year ones it needs (``findings_on`` / ``set_findings``, every other one None), so each row of the reach
table is shown with each finding True, False and None; ``f2_unmeasured`` (conftest) gives the state before. The fake is taught each call as the probe is to measure it, by assumption (its docstring)."""

import os

import pytest

from gear_generator import findings, printout, swbuild, swcom
from gear_generator.gears.equations import equation_text
from gear_generator.printout import PrintPlan, Refusal
from gear_generator.spec import GearSpec
from gear_generator.swcom import DocInfo, FeatureState, SolidWorksError

from test_swbuild import FakeSolidWorks, _key

SPUR = GearSpec(module="1.5", teeth="20", face_width="8", bore="", process="printed")
PART = r"C:\Box\Gear_m1.5_N20_P.SLDPRT"
PART2 = r"C:\Box\Gear_m1.5_N40_P.SLDPRT"
ASSEMBLY = r"C:\Box\Reducer.SLDASM"
USERS = r"C:\Mine\Bracket.SLDPRT"
VARIABLES = (("No. of Teeth", "20"), ("Module", "1.5"), ("Face Width", "8"))
MADE = ("Blank", "Tooth Space", "Teeth")
FINDINGS = ("STEP_EXPORT_NEEDS_ACTIVE", "STEP_EXPORT_FROM_COMPONENT", "OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN",
            "PART_WINDOW_READ")


def set_findings(monkeypatch, **per_year):
    """The gate open on 2026 (the fake's version) and each per-year finding given, the rest left None."""
    monkeypatch.setattr(findings, "SAVE_AS_COPY", 2)
    monkeypatch.setattr(findings, "STEP_EXPORT_ON_2026", True)
    for name in FINDINGS:
        monkeypatch.setattr(findings, f"{name}_ON_2026", per_year.get(name))


@pytest.fixture
def findings_on(monkeypatch):
    def apply(**per_year):
        set_findings(monkeypatch, **per_year)
    apply()
    return apply


def doc(path, kind=1):
    return DocInfo(title=path.rsplit("\\", 1)[-1], path=path, doc_type=kind)


def fake_with(*, windows=(), components=(), active=None, assembly=False, modified=()):
    """A fake SolidWorks with PART and PART2 saved as built, the user's own part open and active (unless ``active``
    names another), ``windows`` open in their own windows, ``components`` loaded only as components of the open
    assembly, and ``modified`` changed in memory and not saved."""
    sw = FakeSolidWorks()
    sw._f2()
    for path in (PART, PART2):
        sw.saved[_key(path)] = ([equation_text(n, e) for n, e in VARIABLES], list(MADE))
    sw.saved[_key(USERS)] = ([], ["Boss-Extrude1"])
    sw.saved[_key(ASSEMBLY)] = ([], [])
    opened = [USERS] + ([ASSEMBLY] if assembly else []) + list(windows)
    for path in opened:
        sw.open_docs.append(doc(path, 2 if path.endswith(".SLDASM") else 1))
        sw.memory[_key(path)] = tuple(list(x) for x in sw.saved[_key(path)])
    for path in components:
        sw.component_only.add(_key(path))
        sw.memory[_key(path)] = tuple(list(x) for x in sw.saved[_key(path)])
    for path in modified:
        eq, made = sw.memory[_key(path)]
        sw.memory[_key(path)] = ([equation_text("Face Width", "9") if t.startswith('"Face Width"') else t for t in eq],
                                 made)
    sw.active = next(d for d in sw.open_docs if d.path == (active or USERS))
    sw.current = sw.active.path
    sw.calls.clear()
    return sw


def part(path=PART, **kw):
    return printout.print_part(path, SPUR.to_dict(), variables=VARIABLES, made=MADE, **kw)


def plan_for(tmp_path, *parts, revision=(34, 0, 0)):
    """A plan into tmp_path/out (made: the Output folder is on disk), its press's folder not made yet."""
    os.makedirs(os.path.join(str(tmp_path), "out"), exist_ok=True)
    folder = os.path.join(str(tmp_path), "out", "print", "2026-11-18 14.32.05")
    return PrintPlan(None, tuple(parts) or (part(),), folder, revision, "Reducer", 0.0)


def names(sw):
    return [name for name, _ in sw.calls]


def opened_and_closed(sw):
    return [(n, a) for n, a in sw.calls if n in ("open_document", "close_document", "activate")]


def written_files(result):
    return [os.path.basename(f) for _, f in result.written]


# -- the gate, again in the job --------------------------------------------------------------------------------------------


def test_with_every_finding_unmeasured_the_job_refuses_gate_copy_and_touches_nothing(tmp_path, f2_unmeasured):
    sw = fake_with()
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal == Refusal(printout.GATE_COPY) and result.active_restored is True
    assert sw.calls == [] and not (tmp_path / "out" / "print").exists()


def test_the_plans_own_refusal_is_answered_as_it_is(tmp_path, findings_on):
    sw = fake_with()
    refusal = Refusal(printout.UNSAVED_MARK, ("Gear_m1.5_N20_P",))
    assert swbuild.print_parts(sw, PrintPlan(refusal, revision=(34, 0, 0))).refusal == refusal
    assert sw.calls == []


def test_a_session_that_is_not_the_plans_is_gate_with_both_versions(tmp_path, findings_on):
    sw = fake_with()
    result = swbuild.print_parts(sw, plan_for(tmp_path, revision=(32, 5, 0)))
    assert result.refusal == Refusal(printout.GATE, (), {"year": "2026", "revision": "34.0.0", "planned_year": "2024",
                                                         "planned_revision": "32.5.0"})
    assert sw.calls == []


def test_a_version_whose_step_export_is_unset_is_gate_in_the_job_too(tmp_path, monkeypatch):
    set_findings(monkeypatch)
    monkeypatch.setattr(findings, "STEP_EXPORT_ON_2026", None)
    sw = fake_with()
    assert swbuild.print_parts(sw, plan_for(tmp_path)).refusal == Refusal(printout.GATE, (), {"year": "2026",
                                                                                              "revision": "34.0.0"})
    assert sw.calls == []


# -- a part not open: opened, read, written, closed -----------------------------------------------------------------------


def test_a_part_not_open_is_opened_read_written_checked_and_closed_and_the_users_document_put_back(tmp_path,
                                                                                                 findings_on):
    sw = fake_with()
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal is None and result.failed == ()
    folder = os.path.join(str(tmp_path), "out", "print", "2026-11-18 14.32.05")
    assert result.folder == folder and os.path.isdir(folder)
    assert result.written == ((PART, os.path.join(folder, "Gear_m1.5_N20_P.step")),)
    assert open(result.written[0][1], encoding="latin-1", newline="").read() == FakeSolidWorks.STEP_TEXT
    assert sw.exports == [(PART, result.written[0][1], PART)]          # its own document, as it was written
    assert result.facts == {"Gear_m1.5_N20_P.step|schema": "AUTOMOTIVE_DESIGN", "Gear_m1.5_N20_P.step|unit":
                            "MILLI.METRE", "Gear_m1.5_N20_P.step|extent": "checked"}
    assert opened_and_closed(sw) == [("open_document", (PART,)), ("activate", ("Gear_m1.5_N20_P.SLDPRT",)),
                                     ("close_document", ("Gear_m1.5_N20_P.SLDPRT",))]
    assert result.active_restored is True and sw.active.path == USERS   # the fake's CloseDoc left the user's active
    assert [d.path for d in sw.open_docs] == [USERS]                   # nothing left open, the user's untouched
    assert result.flags_turned_on == () and result.warnings == ()


def test_every_read_is_made_on_every_part_before_any_file_is_written(tmp_path, findings_on):
    sw = fake_with()
    swbuild.print_parts(sw, plan_for(tmp_path, part(PART), part(PART2)))
    calls = names(sw)
    first_export = calls.index("export_step")
    assert calls.count("has_unsaved_changes") == 2 and calls.count("feature_states") == 2
    assert max(i for i, n in enumerate(calls) if n in ("has_unsaved_changes", "feature_states")) < first_export
    assert calls.count("export_step") == 2


def test_the_press_folder_takes_the_next_counter_when_its_name_has_come_to_exist(tmp_path, findings_on):
    plan = plan_for(tmp_path)
    os.makedirs(plan.folder)
    result = swbuild.print_parts(fake_with(), plan)
    assert result.folder == plan.folder + " (2)" and os.listdir(plan.folder) == []


def test_the_job_never_makes_the_output_folder_and_refuses_no_folder_when_it_has_gone(tmp_path, findings_on):
    plan = plan_for(tmp_path)
    os.rmdir(os.path.join(str(tmp_path), "out"))
    sw = fake_with()
    result = swbuild.print_parts(sw, plan)
    assert result.refusal == Refusal(printout.NO_FOLDER, (), {"folder": os.path.join(str(tmp_path), "out")})
    assert not (tmp_path / "out").exists() and "export_step" not in names(sw) and result.folder == ""
    assert [d.path for d in sw.open_docs] == [USERS] and result.active_restored is True


def test_the_job_makes_the_print_folder_inside_the_output_folder_when_it_is_not_there_yet(tmp_path, findings_on):
    plan = plan_for(tmp_path)
    assert not (tmp_path / "out" / "print").exists()
    assert swbuild.print_parts(fake_with(), plan).folder == plan.folder and os.path.isdir(plan.folder)


def test_a_part_r2_is_written_as_r2(tmp_path, findings_on):
    sw = fake_with()
    path = r"C:\Box\Gear_m1.5_N20_P_r2.SLDPRT"
    sw.saved[_key(path)] = sw.saved[_key(PART)]
    result = swbuild.print_parts(sw, plan_for(tmp_path, part(path)))
    assert written_files(result) == ["Gear_m1.5_N20_P_r2.step"]


# -- how each part is reached (F2-INTERFACES.md §5.2), each finding True, False and None ----------------------------------


@pytest.mark.parametrize("needs_active,way", [(None, "activate"), (True, "activate"), (False, "object")])
def test_reach_way_for_a_part_in_its_own_window(monkeypatch, needs_active, way):
    set_findings(monkeypatch, STEP_EXPORT_NEEDS_ACTIVE=needs_active)
    assert swbuild.reach_way(2026, found=True, window=True, assembly_open=False) == way
    assert swbuild.reach_way(2026, found=True, window=True, assembly_open=True) == way


@pytest.mark.parametrize("from_component,beside,way", [
    (True, None, "object"), (True, False, "object"), (True, True, "object"),
    (None, True, "open"), (False, True, "open"),
    (None, None, "refused"), (False, False, "refused"), (None, False, "refused"), (False, None, "refused")])
def test_reach_way_for_a_part_loaded_only_as_a_component(monkeypatch, from_component, beside, way):
    set_findings(monkeypatch, STEP_EXPORT_FROM_COMPONENT=from_component, OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN=beside)
    assert swbuild.reach_way(2026, found=True, window=False, assembly_open=True) == way


@pytest.mark.parametrize("from_component,needs_active,way", [
    (True, False, "object"), (True, None, "refused"), (True, True, "refused"),
    (None, False, "refused"), (False, False, "refused"), (None, None, "refused")])
def test_reach_way_for_a_part_found_whose_window_is_not_read(monkeypatch, from_component, needs_active, way):
    set_findings(monkeypatch, STEP_EXPORT_FROM_COMPONENT=from_component, STEP_EXPORT_NEEDS_ACTIVE=needs_active,
                 OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN=True)
    assert swbuild.reach_way(2026, found=True, window=None, assembly_open=True) == way


@pytest.mark.parametrize("beside", [None, False, True])
def test_reach_way_for_a_part_not_found(monkeypatch, beside):
    """Not found with no assembly open: opened. Not found while an assembly is open: it may be a lightweight component,
    which nothing reaches and opening beside would resolve, so refused whatever the findings (the ruling, 8d2c5fb)."""
    set_findings(monkeypatch, OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN=beside, STEP_EXPORT_FROM_COMPONENT=True)
    assert swbuild.reach_way(2026, found=False, window=None, assembly_open=False) == "open"
    assert swbuild.reach_way(2026, found=False, window=None, assembly_open=True) == "lightweight"


def test_reach_way_reads_the_sessions_year(monkeypatch):
    set_findings(monkeypatch, STEP_EXPORT_NEEDS_ACTIVE=False)
    monkeypatch.setattr(findings, "STEP_EXPORT_NEEDS_ACTIVE_ON_2024", None)
    assert swbuild.reach_way(2026, found=True, window=True, assembly_open=False) == "object"
    assert swbuild.reach_way(2024, found=True, window=True, assembly_open=False) == "activate"


@pytest.mark.parametrize("value", [None, True, "IModelDoc2.Visible, True for a document open in its own window"])
def test_the_fake_reads_a_window_only_by_a_word_session_knows(findings_on, value):
    """F2-REVIEW S7: as Session.window_read, any PART_WINDOW_READ but "Visible" or "ActiveView" is unmeasured."""
    findings_on(PART_WINDOW_READ=value)
    sw = fake_with(windows=[PART])
    assert sw.window_read(sw.document_by_path(PART)) is None
    findings_on(PART_WINDOW_READ="Visible")
    assert sw.window_read(sw.document_by_path(PART)) is True


def test_with_the_findings_as_committed_a_part_in_its_own_window_goes_by_its_object(tmp_path):
    sw = fake_with(windows=[PART])
    result = swbuild.print_parts(sw, plan_for(tmp_path, revision=(34, 0, 0)))
    assert result.refusal is None and opened_and_closed(sw) == []
    assert sw.exports == [(PART, result.written[0][1], USERS)]
    assert result.facts["Gear_m1.5_N20_P.step|extent"] == "checked"


def test_a_part_open_in_its_window_and_not_active_is_refused_while_its_window_is_unread(tmp_path, findings_on):
    sw = fake_with(windows=[PART])
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal == Refusal(printout.COMPONENT_ONLY, ("Gear_m1.5_N20_P",), {"Gear_m1.5_N20_P": ""})
    assert opened_and_closed(sw) == [] and "export_step" not in names(sw) and not (tmp_path / "out" / "print").exists()
    assert result.active_restored is True


def test_while_its_window_is_unread_a_found_part_goes_by_its_object_only_when_both_findings_allow(tmp_path,
                                                                                                findings_on):
    findings_on(STEP_EXPORT_FROM_COMPONENT=True, STEP_EXPORT_NEEDS_ACTIVE=False)
    sw = fake_with(windows=[PART])
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal is None and opened_and_closed(sw) == []
    assert sw.exports == [(PART, result.written[0][1], USERS)]         # by its object, the user's still active
    assert [d.path for d in sw.open_docs] == [USERS, PART]              # never closed: the user had it open


@pytest.mark.parametrize("needs_active", [None, True])
def test_a_part_in_its_own_window_is_activated_first_while_needs_active_is_not_false_and_never_closed(
        tmp_path, findings_on, needs_active):
    findings_on(PART_WINDOW_READ="Visible", STEP_EXPORT_NEEDS_ACTIVE=needs_active)
    sw = fake_with(windows=[PART])
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal is None
    assert sw.exports == [(PART, result.written[0][1], PART)]
    assert opened_and_closed(sw)[-1] == ("activate", ("Bracket.SLDPRT",))
    assert "close_document" not in names(sw) and [d.path for d in sw.open_docs] == [USERS, PART]
    assert result.active_restored is True and sw.active.path == USERS


def test_a_part_in_its_own_window_goes_by_its_object_when_needs_active_is_false(tmp_path, findings_on):
    findings_on(PART_WINDOW_READ="Visible", STEP_EXPORT_NEEDS_ACTIVE=False)
    sw = fake_with(windows=[PART])
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal is None and opened_and_closed(sw) == []
    assert sw.exports == [(PART, result.written[0][1], USERS)]


def test_the_active_part_is_its_own_window_without_a_window_read(tmp_path, findings_on):
    sw = fake_with(windows=[PART], active=PART)
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal is None and "window_read" not in names(sw)
    assert "close_document" not in names(sw) and sw.active.path == PART and result.active_restored is True


def test_a_component_only_part_goes_by_its_object_when_from_component_is_true(tmp_path, findings_on):
    findings_on(PART_WINDOW_READ="Visible", STEP_EXPORT_FROM_COMPONENT=True)
    sw = fake_with(assembly=True, components=[PART], active=ASSEMBLY)
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal is None and opened_and_closed(sw) == []
    assert sw.exports == [(PART, result.written[0][1], ASSEMBLY)]
    assert sw.active.path == ASSEMBLY and result.flags_turned_on == ()


def test_a_component_only_part_is_opened_beside_and_closed_when_only_the_fallback_is_measured(tmp_path, findings_on):
    findings_on(PART_WINDOW_READ="Visible", OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN=True)
    sw = fake_with(assembly=True, components=[PART], active=ASSEMBLY)
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal is None
    assert opened_and_closed(sw) == [("open_document", (PART,)), ("activate", ("Gear_m1.5_N20_P.SLDPRT",)),
                                     ("close_document", ("Gear_m1.5_N20_P.SLDPRT",))]
    assert sw.active.path == ASSEMBLY
    assert [d.path for d in sw.open_docs] == [USERS, ASSEMBLY]          # the assembly never closed
    assert _key(PART) in sw.component_only and result.active_restored is True


def test_a_component_only_part_is_refused_by_name_with_its_assembly_when_neither_route_is_measured(tmp_path,
                                                                                                  findings_on):
    findings_on(PART_WINDOW_READ="Visible")
    sw = fake_with(assembly=True, components=[PART], active=ASSEMBLY)
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal == Refusal(printout.COMPONENT_ONLY, ("Gear_m1.5_N20_P",),
                                     {"Gear_m1.5_N20_P": "Reducer.SLDASM"})
    assert opened_and_closed(sw) == [] and not (tmp_path / "out" / "print").exists()


def test_a_lightweight_component_is_refused_by_name_even_with_the_fallback_measured(tmp_path, findings_on):
    """Probe step 7c on both versions: a lightweight component's part is reached by neither the walk nor
    GetOpenDocumentByName, so here it is not found while its assembly is open; opening it beside would resolve it."""
    findings_on(PART_WINDOW_READ="Visible", OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN=True, STEP_EXPORT_FROM_COMPONENT=True)
    sw = fake_with(assembly=True, active=ASSEMBLY)                      # PART loaded lightweight: not reached
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal == Refusal(printout.LIGHTWEIGHT, ("Gear_m1.5_N20_P",), {"Gear_m1.5_N20_P": "Reducer.SLDASM"})
    assert opened_and_closed(sw) == [] and "export_step" not in names(sw)


def test_component_only_is_said_before_lightweight_and_names_every_part_it_applies_to(tmp_path, findings_on):
    findings_on(PART_WINDOW_READ="Visible")
    sw = fake_with(assembly=True, components=[PART], active=ASSEMBLY)
    third = r"C:\Box\Gear_m1_N12_P.SLDPRT"
    sw.component_only.add(_key(third))
    result = swbuild.print_parts(sw, plan_for(tmp_path, part(PART), part(PART2), part(third)))
    assert result.refusal == Refusal(printout.COMPONENT_ONLY, ("Gear_m1.5_N20_P", "Gear_m1_N12_P"),
                                     {"Gear_m1.5_N20_P": "Reducer.SLDASM", "Gear_m1_N12_P": "Reducer.SLDASM"})


def test_with_two_assemblies_open_the_refusal_names_none(tmp_path, findings_on):
    sw = fake_with(assembly=True, active=ASSEMBLY)
    sw.open_docs.append(doc(r"C:\Other\Two.SLDASM", 2))
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal == Refusal(printout.LIGHTWEIGHT, ("Gear_m1.5_N20_P",), {"Gear_m1.5_N20_P": ""})


# -- the reads before any export (§5.3, §5.4) ------------------------------------------------------------------------------


def test_a_part_changed_in_solidworks_and_not_saved_is_modified_and_nothing_is_written(tmp_path, findings_on):
    findings_on(PART_WINDOW_READ="Visible")
    sw = fake_with(windows=[PART], modified=[PART])
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal == Refusal(printout.MODIFIED, ("Gear_m1.5_N20_P",))
    assert "export_step" not in names(sw) and result.folder == "" and not (tmp_path / "out" / "print").exists()
    assert result.active_restored is True and sw.active.path == USERS


def test_print_files_after_a_quiet_update_values_is_not_refused_as_changed(tmp_path, findings_on):
    """F3-DEMONSTRATION-RUNS-REVIEW §3 (the coordinator's ruling, 2026-11-19): a quiet Update values from the strip, every
    value already the form's, turns no save flag on, so Print files does not then say the part is changed in SolidWorks
    and not saved; before, the units were measured first, which marked the part, and it was refused MODIFIED."""
    from gear_generator.gears.base import GlobalVariable
    findings_on(PART_WINDOW_READ="Visible")
    sw = fake_with(windows=[PART], active=PART)
    sw.open_document(PART)
    sw.calls.clear()
    result = swbuild.update_variables(sw, [GlobalVariable(n, e) for n, e in VARIABLES], PART)
    assert result.ok and result.changed == [] and "detect_trig_units" not in names(sw)
    printed = swbuild.print_parts(sw, plan_for(tmp_path))
    assert printed.refusal is None and written_files(printed) == ["Gear_m1.5_N20_P.step"]


def test_globals_that_differ_from_the_record_refuse_with_the_first_one(tmp_path, findings_on):
    sw = fake_with()
    sw.saved[_key(PART)] = ([equation_text("No. of Teeth", "20"), equation_text("Module", "1.5"),
                             equation_text("Face Width", "9")], list(MADE))
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal == Refusal(printout.GLOBALS_DIFFER, ("Gear_m1.5_N20_P",),
                                     {"name": "Face Width", "live": "9", "recorded": "8"})
    assert "export_step" not in names(sw)
    assert [d.path for d in sw.open_docs] == [USERS]                    # the part the job opened is closed again


def test_globals_are_compared_spaces_aside_and_a_global_gone_differs(tmp_path, findings_on):
    sw = fake_with()
    sw.saved[_key(PART)] = (['"No. of Teeth"=20', '"Module"=  1.5', '"Face Width"= 8'], list(MADE))
    assert swbuild.print_parts(sw, plan_for(tmp_path)).refusal is None
    sw = fake_with()
    sw.saved[_key(PART)] = (['"No. of Teeth"= 20', '"Face Width"= 8'], list(MADE))
    assert swbuild.print_parts(sw, plan_for(tmp_path)).refusal.detail == {"name": "Module", "live": "",
                                                                          "recorded": "1.5"}


def test_a_feature_in_error_refuses_naming_it(tmp_path, findings_on):
    sw = fake_with()
    sw.feature_codes[(_key(PART), "Teeth")] = 2
    sw.user_features[_key(PART)] = [("User Keyway", "ICE")]
    sw.feature_codes[(_key(PART), "User Keyway")] = 46
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal == Refusal(printout.FEATURE_IN_ERROR, ("Gear_m1.5_N20_P",),
                                     {"Gear_m1.5_N20_P": "Teeth, User Keyway"})
    assert "export_step" not in names(sw)


def test_a_feature_warning_is_named_and_does_not_refuse(tmp_path, findings_on, monkeypatch):
    sw = fake_with()
    states = FakeSolidWorks.feature_states

    def with_a_warning(self):
        return [FeatureState(s.name, s.type_name, 46, True) if s.name == "Teeth" else s for s in states(self)]

    monkeypatch.setattr(FakeSolidWorks, "feature_states", with_a_warning)
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal is None and written_files(result) == ["Gear_m1.5_N20_P.step"]
    assert result.warnings == ((PART, ("Teeth",)),)


def test_a_feature_solidworks_would_not_give_a_code_for_neither_refuses_nor_warns(tmp_path, findings_on):
    sw = fake_with()
    sw.feature_codes[(_key(PART), "Teeth")] = swcom.UNREAD
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal is None and result.warnings == ()


def test_the_first_failing_read_in_order_refuses_naming_every_part_that_fails_it(tmp_path, findings_on):
    findings_on(PART_WINDOW_READ="Visible")
    sw = fake_with(windows=[PART2], modified=[PART2])
    sw.feature_codes[(_key(PART), "Teeth")] = 2                          # PART: in error; PART2: modified
    result = swbuild.print_parts(sw, plan_for(tmp_path, part(PART), part(PART2)))
    assert result.refusal == Refusal(printout.MODIFIED, ("Gear_m1.5_N40_P",))
    sw.feature_codes[(_key(PART2), "Teeth")] = 2
    sw2 = fake_with()
    sw2.feature_codes[(_key(PART), "Teeth")] = 2
    sw2.feature_codes[(_key(PART2), "Blank")] = 7
    result = swbuild.print_parts(sw2, plan_for(tmp_path, part(PART), part(PART2)))
    assert result.refusal == Refusal(printout.FEATURE_IN_ERROR, ("Gear_m1.5_N20_P", "Gear_m1.5_N40_P"),
                                     {"Gear_m1.5_N20_P": "Teeth", "Gear_m1.5_N40_P": "Blank"})


def test_solidworks_refusing_to_open_a_part_is_solidworks_refused_with_swcoms_sentence(tmp_path, findings_on):
    sw = fake_with()
    sw.fail_on["open_document"] = "Gear_m1.5_N20_P.SLDPRT is open from another folder."
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal == Refusal(printout.SOLIDWORKS_REFUSED, ("Gear_m1.5_N20_P",),
                                     {"said": "Gear_m1.5_N20_P.SLDPRT is open from another folder."})
    assert "export_step" not in names(sw) and result.active_restored is True


# -- the export, the check and the end (§5.5) ------------------------------------------------------------------------------


def test_solidworks_refusing_a_file_stops_the_export_and_keeps_the_files_written(tmp_path, findings_on):
    sw = fake_with()
    sw.export_fail[_key(PART2)] = (1, 0)
    result = swbuild.print_parts(sw, plan_for(tmp_path, part(PART), part(PART2)))
    assert result.refusal == Refusal(printout.SOLIDWORKS_REFUSED, ("Gear_m1.5_N40_P",),
                                     {"file": "Gear_m1.5_N40_P.step", "errors": "1", "warnings": "0"})
    assert written_files(result) == ["Gear_m1.5_N20_P.step"] and os.path.isfile(result.written[0][1])
    assert result.folder and [d.path for d in sw.open_docs] == [USERS] and result.active_restored is True


def test_another_solidworks_error_in_the_export_is_said_by_swcoms_sentence(tmp_path, findings_on):
    sw = fake_with()
    sw.fail_on["export_step"] = "SolidWorks stopped answering."
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal == Refusal(printout.SOLIDWORKS_REFUSED, ("Gear_m1.5_N20_P",),
                                     {"file": "Gear_m1.5_N20_P.step", "said": "SolidWorks stopped answering."})


def test_a_file_failing_its_check_is_file_check_and_stays(tmp_path, findings_on):
    sw = fake_with()
    sw.step_texts[_key(PART)] = FakeSolidWorks.STEP_TEXT.replace("#3 = CLOSED_SHELL", "#3 = OPEN_SHELL")
    result = swbuild.print_parts(sw, plan_for(tmp_path, part(PART), part(PART2)))
    target = os.path.join(result.folder, "Gear_m1.5_N20_P.step")
    assert result.refusal == Refusal(printout.FILE_CHECK, ("Gear_m1.5_N20_P",),
                                     {"file": "Gear_m1.5_N20_P.step", "reason": printout.SOLIDS})
    assert result.failed == ((target, printout.SOLIDS),) and os.path.isfile(target)
    assert sw.exports == [(PART, target, PART)]                        # the export stopped there


def test_the_size_check_once_measured_runs_in_the_job_and_skips_a_part_holding_the_users_feature(
        tmp_path, findings_on, monkeypatch):
    monkeypatch.setattr(findings, "EXTENT_MEASURED", True)
    sw = fake_with()
    sw.step_texts[_key(PART)] = FakeSolidWorks.STEP_TEXT_SHAPE.format(r=16.5, f=0.0)     # no axial extent
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal == Refusal(printout.FILE_CHECK, ("Gear_m1.5_N20_P",),
                                     {"file": "Gear_m1.5_N20_P.step", "reason": printout.EXTENT})
    sw = fake_with()
    sw.step_texts[_key(PART)] = FakeSolidWorks.STEP_TEXT_SHAPE.format(r=16.5, f=0.0)
    sw.user_features[_key(PART)] = [("Keyway Boss", "Extrusion")]       # read live after the app's own features
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal is None
    assert result.facts["Gear_m1.5_N20_P.step|extent"] == "skipped: user features"


def test_the_users_features_read_live_are_named_in_the_result_whether_or_not_the_record_lists_them(tmp_path,
                                                                                                  findings_on):
    """F2-DEMONSTRATION-REVIEW: the job's live read of the user's features (feature_states against the record's made),
    per part by name, so the print list can name a feature no record lists (every part printed from the form)."""
    sw = fake_with()
    sw.user_features[_key(PART)] = [("User Keyway", "ICE"), ("Boss-Extrude1", "Extrusion")]
    sw.user_features[_key(PART2)] = [("User Keyway", "ICE")]
    third = r"C:\Box\Gear_m1_N12_P.SLDPRT"
    sw.saved[_key(third)] = sw.saved[_key(PART)]
    listed = part(PART2, user_features=("User Keyway",))                     # the record lists it
    result = swbuild.print_parts(sw, plan_for(tmp_path, part(PART), listed, part(third)))
    assert result.refusal is None and len(result.written) == 3
    assert result.live_features == ((PART, ("User Keyway", "Boss-Extrude1")), (PART2, ("User Keyway",)))
    assert result.facts["Gear_m1.5_N20_P.step|extent"] == "skipped: user features"     # no record lists them
    assert result.facts["Gear_m1.5_N40_P.step|extent"] == "skipped: user features"
    assert result.facts["Gear_m1_N12_P.step|extent"] == "checked"                       # none: not in the result


def test_a_result_with_no_user_features_read_names_none_and_with_list_keeps_them(tmp_path, findings_on):
    sw = fake_with()
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.live_features == () and printout.PrintResult(active_restored=True).live_features == ()
    sw = fake_with()
    sw.user_features[_key(PART)] = [("User Keyway", "ICE")]
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    listed = printout.with_list(result, "the list")
    assert listed.list_path and listed.live_features == ((PART, ("User Keyway",)),)


def test_a_save_flag_the_job_turned_on_is_said_and_never_saved(tmp_path, findings_on, monkeypatch):
    sw = fake_with(assembly=True, components=[PART], active=ASSEMBLY)
    findings_on(PART_WINDOW_READ="Visible", STEP_EXPORT_FROM_COMPONENT=True)
    export = FakeSolidWorks.export_step

    def export_marking(self, path):
        self.touched.add(_key(ASSEMBLY))                                 # as if the export had marked the assembly
        return export(self, path)

    monkeypatch.setattr(FakeSolidWorks, "export_step", export_marking)
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal is None and result.flags_turned_on == (ASSEMBLY,)
    assert "save_as" not in names(sw)


def test_the_users_active_document_is_activated_again_when_closing_left_another_active(tmp_path, findings_on):
    sw = fake_with(windows=[PART2])                    # after the job's CloseDoc the fake leaves PART2 active
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert opened_and_closed(sw)[-1] == ("activate", ("Bracket.SLDPRT",))
    assert result.active_restored is True and sw.active.path == USERS


def test_the_active_document_not_put_back_is_said(tmp_path, findings_on, monkeypatch):
    sw = fake_with(windows=[PART2])
    activate = FakeSolidWorks.activate

    def refusing_the_users(self, title):
        if title == "Bracket.SLDPRT":
            raise SolidWorksError("ActivateDoc3 answered nothing.")
        return activate(self, title)

    monkeypatch.setattr(FakeSolidWorks, "activate", refusing_the_users)
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.refusal is None and result.active_restored is False


def test_the_users_document_closed_meanwhile_reads_as_put_back(tmp_path, findings_on, monkeypatch):
    sw = fake_with()
    export = FakeSolidWorks.export_step

    def closing_the_users(self, path):
        self.open_docs = [d for d in self.open_docs if d.path != USERS]
        return export(self, path)

    monkeypatch.setattr(FakeSolidWorks, "export_step", closing_the_users)
    assert swbuild.print_parts(sw, plan_for(tmp_path)).active_restored is True


def test_an_error_part_way_still_closes_what_the_job_opened_and_puts_the_active_document_back(tmp_path, findings_on):
    sw = fake_with()
    sw.raises["feature_states"] = (1, RuntimeError("not a SolidWorks error"))
    with pytest.raises(RuntimeError):
        swbuild.print_parts(sw, plan_for(tmp_path))
    assert [d.path for d in sw.open_docs] == [USERS] and sw.active.path == USERS


def test_a_window_the_job_could_not_close_is_kept_as_a_fact(tmp_path, findings_on):
    sw = fake_with()
    sw.fail_on["close_document"] = "CloseDoc failed."
    result = swbuild.print_parts(sw, plan_for(tmp_path))
    assert result.facts["Gear_m1.5_N20_P.SLDPRT|close"] == "failed: CloseDoc failed."


def test_a_plan_with_no_parts_does_nothing(tmp_path, findings_on):
    sw = fake_with()
    plan = PrintPlan(None, (), "", (34, 0, 0))
    assert swbuild.print_parts(sw, plan) == printout.PrintResult(active_restored=True) and sw.calls == []


# -- swcom's members (F2-INTERFACES.md §4; package B) ----------------------------------------------------------------------


class ComDoc:
    """A document as late binding reaches one: zero-argument members as attributes."""

    def __init__(self, app, path, visible=True, view=True):
        self.app, self.GetPathName, self.GetTitle, self.GetType = app, path, path.rsplit("\\", 1)[-1], 1
        self.Visible, self.ActiveView = visible, (object() if view else None)
        self.GetSaveFlag = False

    @property
    def GetNext(self):
        docs = self.app.docs
        i = docs.index(self)
        return docs[i + 1] if i + 1 < len(docs) else None


class ComApp:
    def __init__(self, *paths):
        self.docs = [ComDoc(self, p) for p in paths]
        self.asked = []

    @property
    def GetFirstDocument(self):
        return self.docs[0] if self.docs else None

    @property
    def ActiveDoc(self):
        return self.docs[0] if self.docs else None

    def GetOpenDocumentByName(self, name):
        self.asked.append(name)
        return next((d for d in self.docs if d.GetPathName.lower() == name.lower()), None)


def session(app, revision=(34, 0, 0)):
    return swcom.Session(app, revision, 1)


def test_document_by_path_walks_the_open_documents_until_the_route_is_settled():
    app = ComApp(USERS, PART)
    s = session(app)
    assert swcom.DOCUMENT_BY_PATH_ROUTE == "walk"
    assert s.document_by_path(PART.lower()) is app.docs[1]
    assert s.document_by_path(PART2) is None and app.asked == []


def test_document_by_path_by_get_open_document_by_name_is_read_back(monkeypatch):
    monkeypatch.setattr(swcom, "DOCUMENT_BY_PATH_ROUTE", "GetOpenDocumentByName")
    app = ComApp(USERS, PART)
    s = session(app)
    assert s.document_by_path(PART) is app.docs[1] and app.asked == [PART]
    assert s.document_by_path(PART2) is None


def test_use_document_makes_a_found_document_the_build_document_without_activating_it():
    app = ComApp(USERS, PART)
    s = session(app)
    info = s.use_document(app.docs[1])
    assert info == DocInfo("Gear_m1.5_N20_P.SLDPRT", PART, 1)
    assert s.document_path() == PART and app.ActiveDoc is app.docs[0]
    with pytest.raises(SolidWorksError):
        s.use_document(None)


@pytest.mark.parametrize("route,visible,view,answer", [
    (None, True, True, None), ("Visible", True, False, True), ("Visible", False, True, False),
    ("ActiveView", False, True, True), ("ActiveView", True, False, False), ("Something", True, True, None)])
def test_window_read_follows_part_window_read_and_is_none_while_it_is(monkeypatch, route, visible, view, answer):
    monkeypatch.setattr(findings, "PART_WINDOW_READ_ON_2026", route)
    app = ComApp(PART)
    app.docs[0].Visible, app.docs[0].ActiveView = visible, (object() if view else None)
    assert session(app).window_read(app.docs[0]) is answer
    monkeypatch.setattr(findings, "PART_WINDOW_READ_ON_2024", None)
    assert session(app, (32, 5, 0)).window_read(app.docs[0]) is None
