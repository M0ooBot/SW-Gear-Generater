"""Package B of stage F3 (PLAN-PRINTED §4.1.1, §4.4, §4.6; docs/notes-printed/F3-INTERFACES.md §6, §7, §14): the
record's comparisons, the workbook, Update and Print files read a blank Bore allowance on record as built
(``spec.as_built``), each through its own path, against the fake.

Most tests here turn package A's switch on (``spur.PRINTED_DEFAULT_IN_PLANS``, F3-INTERFACES §13), since a printed gear
not on record plans the 0.2 default only then, and that default is what each path must not lay on a part built before
F3. A "pre-F3" gearbox is built with the switch off, where a printed blank plans no allowance, which is what every part F1
and F2 built holds (no ``"Bore Allowance"`` global: tests/fixtures/printed/F2_built.json)."""

from dataclasses import replace

import pytest

from gear_generator import printout, store, swbuild
from gear_generator.gears import kind_for, plan_for, spur
from gear_generator.spec import GearSpec
from gear_generator.store import UnknownSchema
from gear_generator.swcom import DocInfo
from gear_generator.swbuild import (AS_BUILT_WORDS, APP, ENTITY_FACE, ENTITY_PLANE, USER, CarryBody, Carry,
                                    UserWorkRefused, ValueEdit)
from gear_generator.workbook import assess, build, gearbox, update
from gear_generator.workbook.build import PartJob

from test_printed_rule import _f2_bored, _f2_boxed
from test_swbuild import FakeSolidWorks
from test_swbuild_carry import every_gate  # noqa: F401  (the fixture, for W9d's carry below)
from test_swbuild_user_work import _edit
from test_workbook_in_place_round_trip import BOOK, Desk
from workbook_fixtures import range_box_fixed

OUT = "C:\\Out\\"
TEMPLATE = "C:\\T\\Part.prtdot"


@pytest.fixture
def default_on(monkeypatch):
    """A's switch on, as the coordinator's last commit will have it: a printed blank not on record plans 0.2."""
    monkeypatch.setattr(spur, "PRINTED_DEFAULT_IN_PLANS", True)


def fixed(process="printed", **rows):
    """RangeBox_Fixed with its Sun, Planet, dogs and Hub bored (as F2_built.json's), its Process, and any row's cells."""
    spec = _f2_boxed(_f2_bored(range_box_fixed()), process)
    spec = replace(spec, box=replace(spec.box, name="RangeBox"))
    return replace(spec, gears=tuple(replace(g, **rows.get(g.id, {})) for g in spec.gears))


def pre_f3_desk(process="printed"):
    """RangeBox_Fixed built on the fake with the switch off, as F2's code built it: every printed part as F1 and F2 left
    it, no allowance. The switch is turned off for the build alone and put back as it was (F3-REVIEW M1), so the tests
    hold whether the switch is committed on or off."""
    was = spur.PRINTED_DEFAULT_IN_PLANS
    spur.PRINTED_DEFAULT_IN_PLANS = False
    try:
        desk = Desk()
        desk.build(fixed(process))
    finally:
        spur.PRINTED_DEFAULT_IN_PLANS = was
    for part in desk.record.current_parts():
        assert "Bore Allowance" not in dict(part.variables)
    return desk


def globals_of(variables):
    return {v.name: v.expression_for("degrees") for v in variables} if variables and not isinstance(
        variables[0], (list, tuple)) else {str(p[0]): str(p[1]) for p in variables}


def entry_of(record, gear):
    return next(p for p in record.current_parts() if gear in p.gears)


def stem_of(record, gear):
    return gearbox._stem_of(entry_of(record, gear).path)


def sidecar_of(desk, gear):
    return desk.disk.read_sidecar(store.sidecar_path(entry_of(desk.record, gear).path))


def job_of(spec=None, path="C:\\Out\\Gear_m1.5_N25_P.SLDPRT"):
    spec = spec or GearSpec(process="printed", bore="8")
    kind = kind_for(spec)
    derived = kind.derive(spec)
    return PartJob("Gear_m1.5_N25_P", path, ("G1",), spec, derived, plan_for(spec, derived, TEMPLATE, path))


PRE_F3 = [["No. of Teeth", "25"], ["Module", "1.5"], ["Bore Diameter", "8"]]


# -- as_built_job (§4.1.1, F3-0-REVIEW S5) -----------------------------------------------------------------------------


def test_as_built_job_replans_spec_derived_and_plan_from_the_parts_globals(default_on):
    job = job_of()
    assert globals_of(gearbox._variables_of(job))["Bore Allowance"] == "0.2"        # not on record: the default
    assert gearbox.as_built_job(job, None) is job
    before = gearbox.as_built_job(job, PRE_F3)                                       # a part built before F3
    assert before.spec.built_allowance == "0" and before.derived.bore_allowance == 0.0
    assert "Bore Allowance" not in globals_of(gearbox._variables_of(before))
    links = [op.expression for op in before.plan.ops if type(op).__name__ == "LinkDimension"
             and op.dimension.startswith("Bore@")]
    assert links == ['"Bore Diameter"']
    held = gearbox.as_built_job(job, PRE_F3 + [["Bore Allowance", " 0.3 "]])         # cut at 0.3 by F3
    assert held.derived.bore_allowance == 0.3 and globals_of(gearbox._variables_of(held))["Bore Allowance"] == "0.3"
    assert (held.path, held.stem, held.gear_ids) == (job.path, job.stem, job.gear_ids)
    assert held.spec.to_dict() == job.spec.to_dict()                                 # never written: as recorded
    typed = job_of(GearSpec(process="printed", bore="8", bore_allowance="0.1"))
    assert gearbox.as_built_job(typed, PRE_F3) is typed                             # a typed figure is what it says


# -- reuse per candidate entry, Update, Print files: a gearbox built before F3 (rows 1, 2, 5 of §4.1.1's table) ----------


def test_a_gearbox_built_before_f3_is_reused_unchanged_and_printable_with_the_default_on(monkeypatch):
    desk = pre_f3_desk()
    monkeypatch.setattr(spur, "PRINTED_DEFAULT_IN_PLANS", True)
    a = desk.a(fixed())
    planned = {j.gear_ids[0]: globals_of(gearbox._variables_of(j)) for j in a.parts.jobs}
    assert planned["Sun"]["Bore Allowance"] == "0.2"                     # the row alone, with no record, plans 0.2
    again = gearbox.plan_gearbox(a, desk.record, exists=desk.disk.exists, read_sidecar=desk.disk.read_sidecar)
    assert again.refusal == "" and again.build == () and len(again.reuse) == len(desk.record.current_parts())
    for reuse in again.reuse:                       # the live check holds each part to what it holds: no allowance
        assert "Bore Allowance" not in globals_of(reuse.variables) and reuse.spec.built_allowance == "0"
    up = update.classify(desk.record, a, exists=desk.disk.exists, read_sidecar=desk.disk.read_sidecar)
    assert (up.refusal, up.structural, [p.changed for p in up.parts]) == ("", (), [False] * len(up.parts))
    assert all("Bore Allowance" not in globals_of(p.variables) for p in up.parts)
    printed = printout.workbook_print(desk.record, a, up, OUT, (34, 1, 1), now=0.0, exists=desk.disk.exists,
                                      isdir=lambda p: True)
    assert printed.refusal is None
    figures = {p.stem: printout.bore_figures(p) for p in printed.parts}
    assert figures[stem_of(desk.record, "Sun")] == printout.BoreFigures(bore=8.0, allowance=0.0, flat=None)
    assert figures[stem_of(desk.record, "Hub")] == printout.BoreFigures(bore=8.0, allowance=0.0, flat=None)


def test_a_value_update_on_a_part_built_before_f3_leaves_it_with_no_allowance_at_sidecar_3(monkeypatch):
    """S2 (B's owed test): a Backlash change carried by Update to a printed part built before F3 writes no "Bore
    Allowance", keeps its .gear.json at sidecar 3, and its derived with no bore_allowance."""
    desk = pre_f3_desk()
    monkeypatch.setattr(spur, "PRINTED_DEFAULT_IN_PLANS", True)
    press = desk.press(fixed(Sun=dict(backlash="0.25")))
    assert press.up.structural == () and press.result is not None and press.result.ok
    written = [(n, a) for n, a in desk.sw.calls[press.mark:] if n in ("set_global_variable", "add_global_variable")]
    assert written == [("set_global_variable", ("Backlash", "0.25"))]
    assert "Bore Allowance" not in dict(entry_of(desk.record, "Sun").variables)
    car = sidecar_of(desk, "Sun")
    assert car.schema_version == 3 and "bore_allowance" not in car.record.derived
    assert "Bore Allowance" not in dict(car.record.variables) and car.record.spec.get("backlash") == "0.25"


def test_build_again_keeps_the_as_built_allowance_of_a_part_made_new_and_a_row_with_no_part_takes_the_default(
        monkeypatch):
    """Ruling 1: Sun made new by a Face width change keeps the allowance its part was cut with (none, built before F3),
    as the same change carried by Update would; the same row with no record takes the default."""
    desk = pre_f3_desk()
    monkeypatch.setattr(spur, "PRINTED_DEFAULT_IN_PLANS", True)
    a = desk.a(fixed(Sun=dict(face_width="12")))
    again = gearbox.plan_gearbox(a, desk.record, exists=desk.disk.exists, read_sidecar=desk.disk.read_sidecar)
    (sun,) = [j for j in again.build if "Sun" in j.gear_ids]
    assert sun.spec.built_allowance == "0" and sun.derived.bore_allowance == 0.0
    assert "Bore Allowance" not in globals_of(gearbox._variables_of(sun))
    assert [m.why for m in again.made_new if "Sun" in m.gear_ids] == [gearbox.STALE]   # beside it, as _r2
    parts = gearbox._Parts(desk.record, BOOK, desk.disk.exists, desk.disk.read_sidecar, lambda p: 0.0)
    assert sun.path == parts.free_name(sun, []) and parts.occupant(entry_of(desk.record, "Sun").path) == (
        gearbox.STALE, "")                    # its own name taken by the part made before, itself a stale part of ours
    fresh = gearbox.plan_gearbox(a, None, exists=lambda p: False, read_sidecar=lambda p: None)
    (new,) = [j for j in fresh.build if "Sun" in j.gear_ids]
    assert globals_of(gearbox._variables_of(new))["Bore Allowance"] == "0.2"
    # W9d's carry reads the jobs the plan holds: why Sun is new, and its old part's hole as cut.
    old = update.old_assembly(desk.record, again)
    carry = update.carry_for(desk.record, again, old, read_sidecar=desk.disk.read_sidecar)
    body = next(b for b in carry.bodies if b.old == "Sun")
    assert body.why_new == "its Face width changed" and body.bore_mm == 8.0


def test_a_process_change_keeps_the_figure_as_built_either_way(monkeypatch):
    """§4.1.1's two cases said for the user: a part built machined (none) made printed keeps none; a printed part built
    at F3 (0.2) made machined keeps 0.2. Each is a value update, never an allowance added or taken away."""
    desk = pre_f3_desk("machined")
    monkeypatch.setattr(spur, "PRINTED_DEFAULT_IN_PLANS", True)
    up = update.classify(desk.record, desk.a(fixed("printed")), exists=desk.disk.exists)
    assert up.structural == () and all("Bore Allowance" not in globals_of(p.variables) for p in up.parts)
    sun = entry_of(desk.record, "Sun")
    job = next(j for j in desk.a(fixed("printed")).parts.jobs if "Sun" in j.gear_ids)
    assert update._changed_columns(sun.spec, job.spec.to_dict()) == ["Process"]
    f3 = Desk()
    f3.build(fixed("printed"))
    assert dict(entry_of(f3.record, "Sun").variables)["Bore Allowance"] == "0.2"
    up = update.classify(f3.record, f3.a(fixed("machined")), exists=f3.disk.exists)
    assert up.structural == ()
    assert globals_of(next(p for p in up.parts if "Sun" in p.gear_ids).variables)["Bore Allowance"] == "0.2"


# -- Update after an allowance or a flat is typed (§4.4), K11 (§4.4, §9), the hub (W9b) -----------------------------


def test_an_allowance_typed_on_a_part_without_the_global_is_structural_and_on_one_with_it_a_value(monkeypatch):
    desk = pre_f3_desk()
    monkeypatch.setattr(spur, "PRINTED_DEFAULT_IN_PLANS", True)
    up = update.classify(desk.record, desk.a(fixed(Sun=dict(bore_allowance="0.3"))), exists=desk.disk.exists)
    stem = stem_of(desk.record, "Sun")
    assert up.structural == (f"{stem} (Sun): A bore allowance cannot be added to or taken out of a built part through "
                             "its values; build it again as a new part.",)
    assert update.classify(desk.record, desk.a(fixed(Sun=dict(bore_allowance="0"))),
                           exists=desk.disk.exists).structural == ()                     # typed 0 on none: nothing
    f3 = Desk()
    f3.build(fixed())
    press = f3.press(fixed(Sun=dict(bore_allowance="0.3")))
    assert press.up.structural == () and press.result.ok
    assert [(n, a) for n, a in f3.sw.calls[press.mark:] if n == "set_global_variable"] == [
        ("set_global_variable", ("Bore Allowance", "0.3"))]
    assert dict(entry_of(f3.record, "Sun").variables)["Bore Allowance"] == "0.3"
    some_to_none = update.classify(f3.record, f3.a(fixed(Sun=dict(bore_allowance="0"))), exists=f3.disk.exists)
    assert some_to_none.structural == (f"{stem} (Sun): A bore allowance cannot be added to or taken out of a built "
                                       "part through its values; build it again as a new part.",)
    cleared = update.classify(f3.record, f3.a(fixed()), exists=f3.disk.exists)          # cleared: kept as built
    assert cleared.structural == () and not any(p.changed for p in cleared.parts)


def test_k11_says_a_blank_allowance_as_built_and_sets_it_back_to_its_literal(default_on):
    desk = Desk()
    desk.build(fixed())
    sun = entry_of(desk.record, "Sun").path
    up = update.classify(desk.record, desk.a(fixed()), exists=desk.disk.exists)
    doc = next(p for p in up.parts if "Sun" in p.gear_ids)
    assert doc.blank_cells == ("Bore Allowance",)
    assert dict(doc.cells)["Bore Allowance"] == "Gears row 2" and "Bore Flat" in dict(doc.cells)
    typed = next(p for p in update.classify(desk.record, desk.a(fixed(Sun=dict(bore_allowance="0.2"))),
                                            exists=desk.disk.exists).parts if "Sun" in p.gear_ids)
    assert typed.blank_cells == ()
    _edit(desk.sw, sun, "Bore Allowance", "0.3")
    press = desk.press(fixed())
    assert isinstance(press.refused, UserWorkRefused)
    (problem,) = press.refused.problems
    stem = gearbox._stem_of(sun)
    assert problem.values[0].blank == AS_BUILT_WORDS
    assert problem.sentence == (
        f"Bore Allowance in {stem} is 0.3 in SolidWorks and 0.2 (from its blank cell, the allowance as built) in the "
        "workbook: type 0.3 in Gears row 2, or set it back to 0.2 in SolidWorks, and press Update SolidWorks again.")
    assert [n for n, _ in desk.sw.calls[press.mark:] if n == "set_global_variable"] == []


def test_k11s_words_for_a_blank_allowance_with_and_without_a_cell():
    edit = ValueEdit("Gear_m1.5_N25_P.SLDPRT", "Bore Allowance", "0.3", "0.2", "0.2", cell="Gears!V2",
                     blank=AS_BUILT_WORDS)
    assert swbuild._value_sentence(edit) == (
        "Bore Allowance in Gear_m1.5_N25_P is 0.3 in SolidWorks and 0.2 (from its blank cell, the allowance as built) "
        "in the workbook: type 0.3 in Gears!V2, or set it back to 0.2 in SolidWorks, and press Update SolidWorks "
        "again.")
    assert swbuild._value_sentence(replace(edit, cell="")).endswith(
        "and no cell of the workbook sets it alone: set it back to 0.2 in SolidWorks and press Update SolidWorks again.")
    assert update._GLOBAL_COLUMN["Bore Allowance"] == "bore_allowance" and update._GLOBAL_COLUMN["Bore Flat"] == "flat"


HUB = dict(bore_allowance="0.3", drive="flat", flat="7")


def test_the_hub_row_takes_bore_allowance_drive_and_flat_as_any_gear(default_on):
    """§4.4: the hub (W9b) through clutch._as_spur: its allowance and its D built, a Flat changed is a value set in
    place, and a Drive changed is structural, in the workbook's words."""
    desk = Desk()
    desk.build(fixed(Hub=HUB))
    hub = entry_of(desk.record, "Hub")
    assert {k: v for k, v in dict(hub.variables).items() if k.startswith("Bore")} == {
        "Bore Diameter": "8", "Bore Allowance": "0.3", "Bore Flat": "7"}
    car = sidecar_of(desk, "Hub")
    assert car.schema_version == 4 and (car.record.derived["bore_allowance"], car.record.derived["bore_flat"]) == (
        0.3, 7.0)
    press = desk.press(fixed(Hub=dict(HUB, flat="6.8")))
    assert press.up.structural == () and press.result.ok
    assert [(n, a) for n, a in desk.sw.calls[press.mark:] if n == "set_global_variable"] == [
        ("set_global_variable", ("Bore Flat", "6.8"))]
    up = update.classify(desk.record, desk.a(fixed(Hub=dict(HUB, flat="6.8", drive="round"))), exists=desk.disk.exists)
    stem = gearbox._stem_of(hub.path)
    assert up.structural == (f"{stem} (Hub): Drive changed from flat to round, which its values cannot carry; build it "
                             "again as a new part.",)


# -- swbuild.structural_change and its workbook words (§4.1.1 row 3, G4) -------------------------------------------------


def test_structural_change_reads_the_built_allowance_from_its_globals_and_a_blank_as_built():
    bored = {"kind": "spur", "bore": "8"}
    some = [["Bore Diameter", "8"], ["Bore Allowance", "0.2"]]
    none = [["Bore Diameter", "8"]]
    added = ("A bore allowance cannot be added to or taken out of a built part through its values; build it again as "
             "a new part.")
    assert swbuild.structural_change(bored, bored, built_variables=some) == ""          # blank: as built, either way
    assert swbuild.structural_change(bored, bored, built_variables=none) == ""
    assert swbuild.structural_change(bored, dict(bored, bore_allowance="0.3"), built_variables=some) == ""
    assert swbuild.structural_change(bored, dict(bored, bore_allowance="0.3"), built_variables=none) == added
    assert swbuild.structural_change(bored, dict(bored, bore_allowance="0"), built_variables=some) == added
    assert swbuild.structural_change(bored, dict(bored, bore_allowance="0"), built_variables=none) == ""
    assert swbuild.structural_change(bored, dict(bored, bore_allowance="0.3")) == added  # None: as none, the safe side
    assert swbuild.structural_change(dict(bored, bore_allowance="0.2"), dict(bored, bore_allowance="0.3")) == ""
    assert swbuild.structural_change({"kind": "spur"}, {"kind": "spur", "bore_allowance": "0.3"},
                                     built_variables=none) == ""                       # no bore: nothing to cut
    assert swbuild.structural_change(bored, dict(bored, drive="flat", flat="7"), built_variables=none) == (
        "The drive changed from 'round' to 'flat'; build it again as a new part.")
    assert swbuild.structural_change(dict(bored, drive="Flat"), dict(bored, drive="flat", flat="6"),
                                     built_variables=none + [["Bore Flat", "7"]]) == ""
    assert "drive" in swbuild.STRUCTURAL


def test_the_workbooks_drive_sentence_and_a_missing_drive_read_as_round():
    built = {"kind": "spur", "bore": "8"}
    assert update._structural(built, dict(built, drive="flat"), [["Bore Diameter", "8"]]) == (
        "Drive changed from round to flat, which its values cannot carry; build it again as a new part.")
    assert update._structural(built, dict(built, drive="ROUND"), []) == ""
    assert update._changed_columns(dict(built, drive="flat", flat="7"), dict(built, drive="Flat", flat="6.5")) == [
        "Flat"]
    assert update._changed_columns(built, dict(built, bore_allowance="0.3", drive="flat", flat="7")) == [
        "Bore allowance", "Drive", "Flat"]


# -- the journal (F3-0-REVIEW B1) -------------------------------------------------------------------------------------


def test_the_journal_keeps_each_jobs_globals_and_a_part_cut_at_one_allowance_is_never_reused_at_another(default_on):
    from test_workbook_gearbox import Disk, WORKBOOK, assessed
    from test_workbook_model import reducer
    printed = replace(reducer(), box=replace(reducer().box, process="printed"))
    printed = replace(printed, gears=tuple(replace(g, bore=g.bore or "8") for g in printed.gears))
    disk, sw = Disk(), FakeSolidWorks()
    plan = gearbox.plan_gearbox(assessed(printed), None, exists=disk.exists, read_sidecar=disk.read_sidecar)
    journal = gearbox.journal(plan)
    first = journal[0]
    assert first.trig == "degrees" and dict(first.variables)["Bore Allowance"] == "0.2"
    assert dict(first.variables) == {v.name: v.expression_for("degrees") for v in gearbox._variables_of(plan.build[0])}
    record = store.LinkRecord(workbook=WORKBOOK, pending=journal, pending_for=WORKBOOK)
    record = store.link_record_from_json(store.link_record_to_json(record))
    assert record.pending[0].variables == first.variables
    swbuild.build_many(sw, [plan.build[0].plan], sw.exists)                  # interrupted after its first part
    disk.add(*sw.saved)

    def reused(spec, rec):
        again = gearbox.plan_gearbox(assessed(spec), rec, exists=disk.exists, read_sidecar=disk.read_sidecar)
        return {r.stem: r for r in again.reuse}, again

    same, _ = reused(printed, record)
    assert set(same) == {plan.build[0].stem} and same[plan.build[0].stem].journaled
    assert globals_of(same[plan.build[0].stem].variables)["Bore Allowance"] == "0.2"
    row = plan.build[0].gear_ids[0]
    none = replace(printed, gears=tuple(replace(g, bore_allowance="0") if g.id == row else g for g in printed.gears))
    other, again = reused(none, record)
    assert plan.build[0].stem not in other                                   # cut at 0.2: not reused as one at 0
    assert [m.why for m in again.made_new if row in m.gear_ids] == [gearbox.STALE]
    old = replace(record, pending=[replace(e, variables=[], trig="") for e in record.pending])
    old_journal, _ = reused(none, old)                                       # an older journal reads as built with none
    assert set(old_journal) == {plan.build[0].stem}
    assert "Bore Allowance" not in globals_of(old_journal[plan.build[0].stem].variables)


# -- the record (M2) and Print files' figures (§4.1.1 row 5, F3-INTERFACES §7) -----------------------------------------


def test_a_part_built_at_f3_with_a_blank_allowance_is_at_sidecar_4_and_an_f2_reader_leaves_it_alone(default_on,
                                                                                                    tmp_path,
                                                                                                    monkeypatch):
    desk = Desk()
    desk.build(fixed())
    car = sidecar_of(desk, "Sun")
    assert car.schema_version == 4 and "bore_allowance" not in car.record.spec        # the blank stays blank
    assert dict(car.record.variables)["Bore Allowance"] == "0.2" and car.record.derived["bore_allowance"] == 0.2
    target = tmp_path / "Sun.gear.json"
    store.save(str(target), car)
    before = target.read_bytes()
    monkeypatch.setattr(store, "SCHEMA_VERSION", 3)                                   # an F2-era reader
    with pytest.raises(UnknownSchema, match=r"schema 4, this one reads 3"):
        store.load(str(target))
    assert target.read_bytes() == before


@pytest.mark.parametrize("spec, variables, figures", [
    (dict(bore="8"), [["Bore Diameter", "8"]], (8.0, 0.0, None)),                                  # built before F3
    (dict(bore="8"), [["Bore Diameter", "8"], ["Bore Allowance", "0.2"]], (8.0, 0.2, None)),     # blank, as built
    (dict(bore="8", bore_allowance="0.3", drive="flat", flat="7"),
     [["Bore Diameter", "8"], ["Bore Allowance", "0.3"], ["Bore Flat", "7"]], (8.0, 0.3, 7.0)),
    (dict(bore="8", bore_allowance="0"), [["Bore Diameter", "8"]], (8.0, 0.0, None)),            # typed 0
    (dict(bore=""), [], (0.0, 0.0, None)),
    (dict(bore="", bore_allowance="0.3"), [], (0.0, 0.0, None)),                                   # no bore: no hole
], ids=["before F3", "blank at 0.2", "typed with a D", "typed 0", "no bore", "allowance with no bore"])
def test_print_files_says_the_hole_the_part_holds(spec, variables, figures):
    part = printout.print_part("C:\\Out\\G.SLDPRT", GearSpec(process="printed", **spec).to_dict(),
                               variables=variables)
    assert printout.bore_figures(part) == printout.BoreFigures(*figures)


# -- W9d's carry (§4.4, §4.1.1 row 6) ------------------------------------------------------------------------------------


def test_w9ds_bore_is_the_hole_as_cut_as_built():
    entry = store.PartEntry(path="C:\\P\\Sun.SLDPRT", gears=["Sun"], spec={"bore": "8", "drive": "flat", "flat": "7"},
                            variables=[["Bore Diameter", "8"], ["Bore Allowance", "0.2"], ["Bore Flat", "7"]])
    assert update._bore_mm(entry) == pytest.approx(8.2)                                   # blank: the global as built
    assert update._bore_mm(replace(entry, variables=[["Bore Diameter", "8"]], spec={"bore": "8"})) == 8.0
    assert update._bore_mm(replace(entry, spec={"bore": "8", "bore_allowance": "-0.1"})) == pytest.approx(7.9)
    assert update._bore_mm(replace(entry, spec={"bore": ""})) is None
    assert update._bore_mm(replace(entry, spec={"bore": "8", "bore_allowance": "x"})) is None


def test_a_ds_arc_face_is_the_bore_and_its_flat_is_a_face(every_gate):
    from test_swbuild_carry import GEAR_NAMES, OLD, REVISION, _bodies, comp, ent, mate, work
    every_gate()
    entry = store.PartEntry(path="C:\\P\\Sun.SLDPRT", gears=["Sun"], spec={"bore": "8", "drive": "flat", "flat": "7"},
                            variables=[["Bore Diameter", "8"], ["Bore Allowance", "0.2"], ["Bore Flat", "7"]])
    sun = CarryBody("Sun", "gear1-1", "gear1", False, "its Drive changed", GEAR_NAMES, GEAR_NAMES,
                    bore_mm=update._bore_mm(entry))
    carry = Carry(OLD, _bodies()[:2] + (sun,) + _bodies()[3:], ("H", "L"), "H")
    w = work([comp()], [mate("Arc", 0, ent(APP, "Sun", ENTITY_FACE, radius_mm=4.1, coaxial=True),
                             ent(USER, "Sprocket-1", ENTITY_PLANE, "plane1")),
                        mate("Round", 0, ent(APP, "Sun", ENTITY_FACE, radius_mm=4.0, coaxial=True),
                             ent(USER, "Sprocket-1", ENTITY_PLANE, "plane1")),
                        mate("Flat", 0, ent(APP, "Sun", ENTITY_FACE, coaxial=False),
                             ent(USER, "Sprocket-1", ENTITY_PLANE, "plane1"))])
    named = {n.item: n.subjects for n in swbuild.plan_carry(w, carry, REVISION).named}
    assert {k: v[3] for k, v in named.items()} == {"Arc": "bore", "Round": "axis", "Flat": ""}
    assert named["Arc"][:2] == ("Sun", "its Drive changed")


# -- the window's checks (F3-INTERFACES §14, S3) -------------------------------------------------------------------------


def test_the_windows_checks_read_a_row_on_record_as_built_and_its_job_is_planned_as_typed(monkeypatch):
    """S3, as the coordinator ruled on F3-REVIEW M2: given the record, a row on record is checked as built and its job
    planned as typed; reuse, Update and ruling 1 read each part as built from its own entry."""
    desk = pre_f3_desk()
    monkeypatch.setattr(spur, "PRINTED_DEFAULT_IN_PLANS", True)
    spec = replace(fixed(), source_path=BOOK)
    plain = assess.assess(spec, [], OUT)
    held = assess.assess(spec, [], OUT, record=desk.record)
    sun = lambda a: next(j for j in a.parts.jobs if "Sun" in j.gear_ids)                  # noqa: E731
    assert globals_of(gearbox._variables_of(sun(plain)))["Bore Allowance"] == "0.2"
    assert sun(held).spec == sun(plain).spec and sun(held).plan == sun(plain).plan      # the job as typed
    assert [d.message for d in held.diagnostics if d.is_error] == [] and held.lay_out_refusal() == ""
    again = gearbox.plan_gearbox(held, desk.record, exists=desk.disk.exists, read_sidecar=desk.disk.read_sidecar)
    assert again.build == () and all("Bore Allowance" not in globals_of(r.variables) for r in again.reuse)
    assert build.built_globals(desk.record)["Sun"] == entry_of(desk.record, "Sun").variables
    assert build.built_globals(None) == {}
    # One row's checks, as built and not: a bore whose 0.2 default would reach the root diameter, held at 0 by its part.
    root = sun(plain).derived.df
    close = replace(spec, gears=tuple(replace(g, bore=str(round(root - 0.1, 3))) if g.id == "Sun" else g
                                      for g in spec.gears))
    gear = next(g for g in close.gears if g.id == "Sun")
    errors = lambda d: [x.message for x in d if x.is_error]                              # noqa: E731
    assert any("reaches the root diameter" in m for m in errors(build.check_gear(close, gear)[2]))
    assert errors(build.check_gear(close, gear, variables=[["Bore Diameter", "8"]])[2]) == []
    # Such a row's typed job does not work out, so its job is the part it has, as built.
    parts = build.plan_parts(close, OUT, built={"Sun": [["Bore Diameter", gear.bore]]})
    assert errors(parts.diagnostics) == []
    (job,) = [j for j in parts.jobs if "Sun" in j.gear_ids]
    assert job.spec.built_allowance == "0" and "Bore Allowance" not in globals_of(gearbox._variables_of(job))


def _with_sun2(spec, **changes):
    sun = next(g for g in spec.gears if g.id == "Sun")
    row = max(g.row for g in spec.gears) + 1
    return replace(spec, gears=spec.gears + (replace(sun, id="Sun2", row=row, **changes),))


def test_a_new_row_identical_to_a_row_on_record_shares_its_part_with_the_default_on(monkeypatch):
    """F3-REVIEW M2: a row typed the same as a row whose part was built before F3 is the same gear, as before F3: one
    job for both, no "not the same gear", and Build again… reuses the old part for both, as built."""
    desk = pre_f3_desk()
    monkeypatch.setattr(spur, "PRINTED_DEFAULT_IN_PLANS", True)
    spec = replace(_with_sun2(fixed()), source_path=BOOK)
    parts = build.plan_parts(spec, OUT, built=build.built_globals(desk.record))
    assert [d.message for d in parts.diagnostics if d.is_error] == []
    (job,) = [j for j in parts.jobs if "Sun" in j.gear_ids]
    assert job.gear_ids == ("Sun", "Sun2")
    a = assess.assess(spec, [], OUT, record=desk.record)
    assert [d.message for d in a.diagnostics if d.is_error] == []
    again = gearbox.plan_gearbox(a, desk.record, exists=desk.disk.exists, read_sidecar=desk.disk.read_sidecar)
    (reused,) = [r for r in again.reuse if "Sun" in r.gear_ids]
    assert reused.gear_ids == ("Sun", "Sun2") and reused.path == entry_of(desk.record, "Sun").path
    assert "Bore Allowance" not in globals_of(reused.variables)


def test_a_new_row_that_truly_differs_from_a_row_on_record_is_still_not_the_same_gear(monkeypatch):
    desk = pre_f3_desk()
    monkeypatch.setattr(spur, "PRINTED_DEFAULT_IN_PLANS", True)
    for changes in (dict(face_width="12"), dict(bore_allowance="0.3")):
        spec = replace(_with_sun2(fixed(), **changes), source_path=BOOK)
        parts = build.plan_parts(spec, OUT, built=build.built_globals(desk.record))
        said = [d.message for d in parts.diagnostics if d.is_error]
        assert len(said) == 1 and "Sun2 and Sun would both be" in said[0] and "not the same gear" in said[0], said


def test_w9ds_columns_compare_the_allowance_as_built_as_a_number():
    """F3-REVIEW S3, ruled: a typed 0.3 cleared on a part made new for another reason keeps 0.3 (ruling 1), so its Bore
    allowance did not change; 0 typed where the part holds none did not either; 0.3 typed there did."""
    built = {"kind": "spur", "bore": "8", "bore_allowance": "0.3"}
    held = [["Bore Diameter", "8"], ["Bore Allowance", "0.3"]]
    assert update._changed_columns(built, {"kind": "spur", "bore": "8"}, held) == []
    assert update._changed_columns(built, dict(built, bore_allowance="0.30"), held) == []
    assert update._changed_columns({"kind": "spur", "bore": "8"}, {"kind": "spur", "bore": "8", "bore_allowance": "0"}) == []
    assert update._changed_columns({"kind": "spur", "bore": "8"},
                                   {"kind": "spur", "bore": "8", "bore_allowance": "0.3"}) == ["Bore allowance"]
    assert update._changed_columns(built, {"kind": "spur", "bore": "8"}) == ["Bore allowance"]   # no globals: none


# -- the build and its Update against the fake: a D bore takes only calls the app makes (§4.2) ------------------------


def test_a_d_bore_is_built_and_updated_through_the_calls_the_app_already_makes(default_on):
    spec = GearSpec(process="printed", module="1.5", teeth="20", bore="8", drive="flat", flat="7")
    kind = kind_for(spec)
    path = "C:\\Out\\Gear_m1.5_N20_P.SLDPRT"
    plan = plan_for(spec, kind.derive(spec), TEMPLATE, path)
    fake = FakeSolidWorks()
    result = swbuild.build(fake, plan, lambda p: False)
    assert result.ok and result.saved, result.failures
    opened = fake.calls.index(("open_sketch", ("bore", 1)))
    closed = next(i for i, (n, a) in enumerate(fake.calls) if n == "close_sketch" and a[0] == "bore")
    assert [n for n, _ in fake.calls[opened:closed + 1]] == [
        "open_sketch", "sketch_arc", "sketch_line", "add_relation", "add_relation", "add_relation", "add_relation",
        "dimension", "dimension", "close_sketch"]
    names = {n for n, _ in fake.calls}
    assert {"sketch_arc", "sketch_line", "add_relation", "dimension", "cut_extrude", "link_dimension",
            "add_global_variable"} <= names
    relations = [a[0] for n, a in fake.calls if n == "add_relation" and any("bore_" in str(r) for r in a[1:])]
    assert relations == ["coincident", "coincident", "coincident", "vertical"]
    assert ("dimension", ("Bore",)) in fake.calls and ("dimension", ("Flat",)) in fake.calls
    links = dict(a for n, a in fake.calls if n == "link_dimension")
    assert links["Bore@Bore Sketch"] == '( "Bore Diameter" + "Bore Allowance" ) / 2'
    assert "^ 0.5" in links["Flat@Bore Sketch"] and "sqr" not in links["Flat@Bore Sketch"]
    added = [a for n, a in fake.calls if n == "add_global_variable"]
    assert ("Bore Allowance", "0.2") in added and ("Bore Flat", "7") in added
    # Update: a Flat changed is one global set in place, no sketch or feature made.
    fake.active = DocInfo(title="Gear_m1.5_N20_P.SLDPRT", path=path, doc_type=1)
    since = len(fake.calls)
    wanted = spec.with_values(flat="6.5")
    variables = kind.variables(wanted, kind.derive(wanted))
    updated = swbuild.update_variables(fake, variables, path)
    assert updated.ok, updated.failures
    assert [(n, a) for n, a in fake.calls[since:] if n == "set_global_variable"] == [
        ("set_global_variable", ("Bore Flat", "6.5"))]
    assert not {n for n, _ in fake.calls[since:]} & {"sketch_arc", "sketch_line", "add_relation", "dimension",
                                                     "cut_extrude", "add_global_variable", "link_dimension"}
