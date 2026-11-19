"""What the user sees of Printed and Machined (PLAN-PRINTED §1.3, §2.1, §6; package C of stage F1): the strip's
Process row and what it does to each gear, its Backlash hint and its card; and the Workbook window's Process line, with
how it resolves a blank Process (D11, ruled (B): as built, by the record beside the workbook).

Needs Tk and a display, as ``test_workbook_window`` does, whose desk (a Tk root, a fake worker on the fake SolidWorks)
these tests borrow; skipped where there is none.

Until package B reads the Box's Process and Nozzle (``model._read_box``), every workbook reads Machined, so the
window tests here read the Box as B will hand it over (F1-INTERFACES §5): :func:`box_read_as` sets the read's
``process``, ``nozzle`` and ``process_cell`` on every read the window makes, as ``workbook_fixtures.machined_reads`` marks
them. What a real cell reads as is B's to test.
"""

import json
import pathlib
import shutil
from dataclasses import replace

import pytest

from gear_generator import store, ui_text
from gear_generator.spec import PROCESS_MACHINED, PROCESS_PRINTED, GearSpec
from test_workbook_window import NAME, built, desk, gear_states, record_bytes, w5_findings  # noqa: F401 - fixtures

tk = pytest.importorskip("tkinter")

AS_BUILT = ("Machined, as built: type Printed beside Process on the Box sheet to print it")
NO_ROW = " (add a row labelled Process)"


# -- the strip ------------------------------------------------------------------------------------------------------


@pytest.fixture
def app(desk):
    from gear_generator import gui
    return gui.GearApp(desk.root)


def shown(widget) -> bool:
    return bool(widget.winfo_manager())


def backlash_says(app, side="a"):
    return app._side_fields(side)["backlash"]._placeholder.cget("text"), app.backlash_hints[side].cget("text")


def test_the_form_starts_printed_and_a_blank_form_gives_printed_gears(app):
    """§1.3: the row starts at Printed, not at GearSpec()'s machined; Nozzle shows under it, blank meaning 0.4 mm."""
    assert app.process.get() == PROCESS_PRINTED and app.nozzle.get() == ""
    assert all(shown(w) for w in app.nozzle_row)
    assert app.nozzle_field._placeholder.cget("text") == "0.4"
    spec = app._gear_spec("a")
    assert spec.is_printed() and spec.nozzle == "" and spec.nozzle_mm() == 0.4
    assert spec.stem() == "Gear_m1.5_N25_P"
    assert backlash_says(app) == ("0.3 · printed", "0.3 × m below m1")


def test_one_process_covers_both_gears_of_a_pair_and_a_solve_applied_keeps_it(app):
    """§1.3: Process and Nozzle are the pair's, as Kind and Flank are; Solve reads them through the pair's gears, and
    a candidate applied leaves them as the form had them."""
    app.mode.set("pair")
    app._on_mode_changed()
    app.nozzle.set("0.6")
    pair = app._pair_spec()
    assert pair.gear_a.is_printed() and pair.gear_b.is_printed()
    assert pair.gear_a.nozzle == pair.gear_b.nozzle == "0.6"
    for side in ("a", "b"):
        assert backlash_says(app, side) == ("0.3 · printed", "0.3 × m below m1")
    app.centre_distance.set("60")
    app.ratio.set("3")
    app._solve()
    assert app._candidates
    app.candidate_tree.selection_set("0")
    app._on_candidate_selected()
    for side in ("a", "b"):
        spec = app._gear_spec(side)
        assert spec.is_printed() and spec.nozzle == "0.6", side
    assert app._pair_spec().gear_a.process == app._pair_spec().gear_b.process == PROCESS_PRINTED
    app.nozzle.set("")                                            # §2.5: a row too thin for the nozzle says so
    app.centre_distance.set("30")
    app.series.set("1+2+fine")
    app._solve()
    thin = next(i for i, c in enumerate(app._candidates) if c.mark)
    app.candidate_tree.selection_set(str(thin))
    app._on_candidate_selected()
    assert app.card_detail.get().endswith(" · thin for a 0.4 nozzle")
    assert app.candidate_tree.item(str(thin), "values")[2].endswith("thin for a 0.4 nozzle")


def test_machined_hides_the_nozzle_sends_it_blank_and_says_the_machined_backlash(app):
    app.nozzle.set("0.6")
    app.process.set(PROCESS_MACHINED)
    app._on_process_changed()
    assert not any(shown(w) for w in app.nozzle_row)
    spec = app._gear_spec("a")
    assert not spec.is_printed() and spec.process == PROCESS_MACHINED and spec.nozzle == ""
    assert "process" not in spec.to_dict() and "nozzle" not in spec.to_dict()
    assert spec.stem() == "Gear_m1.5_N25"
    assert backlash_says(app) == ("0.3 × module", "ISO: 0.02–0.05 × m")
    app.process.set(PROCESS_PRINTED)                              # back: the nozzle typed is still there
    app._on_process_changed()
    assert all(shown(w) for w in app.nozzle_row) and app._gear_spec("a").nozzle == "0.6"


def test_the_backlash_card_and_derived_row_follow_the_process(app):
    """§2.1: a printed gear's blank Backlash is the printed default on the card and in the Derived rows."""
    app._derive_now()
    app._show_card("a", "backlash")
    card = app.cards["a"]
    assert card.what.cget("text") == ui_text._PRINTED_BACKLASH_COPY
    assert card.worked.cget("text") == ("blank → 0.3 mm · printed default · tooth 2.056 · space 2.656 · play in the "
                                        "mesh 0.6")
    assert dict(ui_text.derived_rows(app._derived["a"]))["Backlash"] == "0.3 · printed default"
    app.process.set(PROCESS_MACHINED)
    app._on_process_changed()
    app._derive_now()
    assert card.what.cget("text").startswith("How much each tooth is thinned") and "Blank uses 0.3 × module" in \
        card.what.cget("text")
    assert card.worked.cget("text").startswith("blank → 0.45 mm (0.3 m) · tooth ")
    app.process.set(PROCESS_PRINTED)                              # a gear that does not work out keeps the printed copy
    app._on_process_changed()
    app.gear_vars["a"]["teeth"].set("x")
    app._derive_now()
    assert app._derived["a"] is None
    assert card.what.cget("text") == ui_text._PRINTED_BACKLASH_COPY and card.worked.cget("text") == "check the fields"


def warnings_shown(app):
    return [w.cget("text") for w in app._warning_widgets]


RING_SAID = "Printed, the tip clearance is 0.2 mm, under the 0.3 mm two printed surfaces take; use a larger module."
BEVEL_SAID = ("Printed, the tip clearance is 0.282 mm, under the 0.3 mm two printed surfaces take; use a larger "
              "module.")


def test_a_printed_ring_pair_and_bevel_pair_are_told_their_clearance_on_the_form(app):
    """§2.2: the strip says package A's pair clearance for a pinion in a ring and a bevel pair when printed; machined,
    neither is told anything new, as before F1."""
    app.mode.set("pair")
    app._on_mode_changed()
    app.mesh.set("internal")
    for side, teeth in (("a", "20"), ("b", "60")):
        app.gear_vars[side]["module"].set("0.5")
        app.gear_vars[side]["teeth"].set(teeth)
        app.gear_vars[side]["bore"].set("")
    app._show_helix_rows()
    app._derive_now()
    assert ui_text.is_ring(app._derived["b"]) and app._derived["b"].printed
    assert RING_SAID in warnings_shown(app)
    app.process.set(PROCESS_MACHINED)
    app._on_process_changed()
    app._derive_now()
    assert not any("tip clearance" in w for w in warnings_shown(app))

    app.process.set(PROCESS_PRINTED)
    app._on_process_changed()
    app.mesh.set("external")
    app.kind.set("bevel")
    app._on_kind_changed()
    for side, teeth in (("a", "20"), ("b", "40")):
        app.gear_vars[side]["module"].set("1.5")
        app.gear_vars[side]["teeth"].set(teeth)
    app._derive_now()
    assert ui_text.is_bevel(app._derived["a"]) and app._derived["a"].printed
    assert BEVEL_SAID in warnings_shown(app)
    app.process.set(PROCESS_MACHINED)
    app._on_process_changed()
    app._derive_now()
    assert not any("tip clearance" in w for w in warnings_shown(app))


def test_a_printed_crossed_pair_is_told_its_clearance_on_the_form_as_in_a_workbook(app):
    """The coordinator's ruling 2 on the F1 review: the form judges a printed crossed pair as the workbook does
    (unshifted, the depth less two addenda), in the same sentence; machined, as before, nothing."""
    app.mode.set("pair")
    app._on_mode_changed()
    app.kind.set("helical")
    app.shafts.set("crossed")
    app.pair_shaft_angle.set("90")
    app.hands.set("same")
    app._on_kind_changed()
    for side, teeth in (("a", "20"), ("b", "40")):
        for field, value in (("module", "0.5"), ("teeth", teeth), ("helix_angle", "45"), ("bore", "")):
            app.gear_vars[side][field].set(value)
    app._show_helix_rows()
    app._derive_now()
    assert app._crossed() and app._derived["a"] is not None and app._derived["b"] is not None
    assert RING_SAID in warnings_shown(app)                       # 0.2 mm at module 0.5, the same words
    app.process.set(PROCESS_MACHINED)
    app._on_process_changed()
    app._derive_now()
    assert not any("tip clearance" in w for w in warnings_shown(app))


def _record(tmp_path, spec, stem):
    part = str(tmp_path / f"{stem}.SLDPRT")
    store.save(store.sidecar_path(part), store.Sidecar(part_path=part, record=store.GearRecord(kind=spec.kind,
                                                                                              spec=spec.to_dict())))
    return store.sidecar_path(part)


def test_a_record_from_before_f1_opens_machined_and_builds_machined(app, tmp_path):
    """§1.3: a .gear.json with no process is what was built, Machined; the form says so, and a part built from it
    afterwards is machined unless the row is changed. A printed one opens Printed with its nozzle."""
    path = _record(tmp_path, GearSpec(module="2", teeth="40", face_width="10"), "Gear_m2_N40")
    raw = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    assert "process" not in raw["gear"]["spec"]                    # as W9 and every app before F1 wrote it
    app._load_record(path)
    assert app.process.get() == PROCESS_MACHINED and not any(shown(w) for w in app.nozzle_row)
    spec = app._gear_spec("a")
    assert not spec.is_printed() and spec.stem() == "Gear_m2_N40"
    assert backlash_says(app) == ("0.3 × module", "ISO: 0.02–0.05 × m")

    printed = GearSpec(module="2", teeth="30", face_width="10", process="printed", nozzle="0.6")
    app._load_record(_record(tmp_path, printed, "Gear_m2_N30_P"))
    assert app.process.get() == PROCESS_PRINTED and app.nozzle.get() == "0.6"
    assert all(shown(w) for w in app.nozzle_row)
    spec = app._gear_spec("a")
    assert spec.stem() == "Gear_m2_N30_P" and (spec.process, spec.nozzle) == (PROCESS_PRINTED, "0.6")


def test_an_old_records_form_changed_to_printed_is_one_global_for_update_values():
    """§1.3: an old .gear.json opened Machined and its row changed to Printed is a change of one global's text, the
    blank Backlash's equation, which Update values carries in place."""
    from test_printed_rule import RECORDED, sidecar_text, strip_form
    from gear_generator import gui
    for name in RECORDED:
        sidecar = store.from_json(sidecar_text(name))
        form = replace(GearSpec.from_dict(sidecar.record.spec), process=PROCESS_PRINTED)
        assert gui.GearApp._update_target(strip_form(sidecar, form))[0] == 1, name


# -- the Workbook window --------------------------------------------------------------------------------------------


def box_read_as(monkeypatch, process, cell="Box!B9", nozzle=""):
    """Every read the window makes hands over a Box as package B's ``_read_box`` will: ``process`` as typed (``""`` for
    a blank cell or no row), ``nozzle`` as typed, and ``process_cell`` where Process was read, ``""`` with no row."""
    from gear_generator.workbook import link
    from_book = link.from_book

    def read(book):
        spec, diagnostics = from_book(book)
        if spec is not None:
            spec = replace(spec, box=replace(spec.box, process=process, nozzle=nozzle, process_cell=cell))
        return spec, diagnostics

    monkeypatch.setattr(link, "from_book", read)


def process_line(window):
    return window.box_values["process"].cget("text")


def built_before_f1(desk):
    """The reducer built machined, its record then made to read as W9 wrote it (link schema 10; its parts hold no
    process, as an F1 machined part's do not either)."""
    window = built(desk)
    path = pathlib.Path(store.link_record_path(window.link.path))
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert all("process" not in part["spec"] for part in raw["parts"])
    raw["link_schema_version"] = 10
    path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
    return window


def test_a_printed_gearbox_says_its_nozzle(desk, monkeypatch):
    box_read_as(monkeypatch, "printed")
    window = desk.open()
    assert window.state.read.box.process == window.state.spec.box.process == PROCESS_PRINTED
    assert process_line(window) == "Printed, 0.4 mm nozzle"
    box_read_as(monkeypatch, "printed", nozzle="0.6")
    window = desk.open(name="Nozzle.xlsx")
    assert process_line(window) == "Printed, 0.6 mm nozzle"


def test_a_new_gearbox_left_blank_is_printed(desk, monkeypatch):
    """D2: with no record beside it, a blank Process is Printed, row or no row."""
    for cell in ("Box!B9", ""):
        box_read_as(monkeypatch, "", cell)
        window = desk.open(name=f"Blank{len(cell)}.xlsx")
        assert window.record is None
        assert window.state.read.box.process == window.state.spec.box.process == PROCESS_PRINTED, cell
        assert process_line(window) == "Printed, 0.4 mm nozzle", cell


def test_machined_typed_says_so(desk, monkeypatch):
    box_read_as(monkeypatch, "machined")
    window = desk.open()
    assert process_line(window) == ("Machined, as the Box sheet says: type Printed beside Process to print it")


def test_a_gearbox_built_before_f1_opens_machined_as_built_and_unchanged(desk, monkeypatch):
    """D11 (B): a gearbox built before F1, its workbook without a Process row, opens exactly as it does today: blank
    reads Machined as built, every gear built and nothing to update, the footer as with Machined typed, and nothing
    written. The panel's line says how to print it, and to add the row. Then Printed typed: every gear changes."""
    window = built_before_f1(desk)
    box_read_as(monkeypatch, "machined")
    said_machined = desk.open(path=window.link.path)
    typed_footer, typed_states = said_machined.status.get(), gear_states(said_machined)
    before = record_bytes(window)

    box_read_as(monkeypatch, "", cell="")
    reopened = desk.open(path=window.link.path)
    assert reopened.state.read.box.process == reopened.state.spec.box.process == PROCESS_MACHINED
    assert process_line(reopened) == AS_BUILT + NO_ROW
    assert gear_states(reopened) == typed_states == {"G1": "built", "G2": "built", "G3": "built", "G4": "built"}
    assert reopened.status.get() == typed_footer
    assert record_bytes(reopened) == before                       # nothing written

    box_read_as(monkeypatch, "", cell="Box!B9")                   # a blank cell in a row the user added
    assert process_line(desk.open(path=window.link.path)) == AS_BUILT

    box_read_as(monkeypatch, "printed")
    printed = desk.open(path=window.link.path)
    assert process_line(printed) == "Printed, 0.4 mm nozzle"
    assert gear_states(printed) == {g: "changes on Update" for g in ("G1", "G2", "G3", "G4")}


def test_end_to_end_a_workbook_with_no_process_row_beside_a_machined_gearbox_reads_machined_as_built(desk):
    """With package B's read, no stand-in: the reducer built Machined, then its workbook saved again with no Process or
    Nozzle row on its Box sheet, as every workbook written before F1 is. The window reads the blank as built, says to
    add the row, and every gear is as built. Then a new workbook with no row and no record reads Printed."""
    from gear_generator.workbook import model, xlsx
    from test_workbook_model import reducer

    def rowless(path, spec):
        sheets = [replace(s, rows=[r for r in s.rows if not (r and r[0] in ("Process", "Nozzle"))])
                  if s.name == "Box" else s for s in model.to_sheets(spec)]
        pathlib.Path(path).unlink(missing_ok=True)
        xlsx.write_new(str(path), sheets)

    window = built(desk)
    rowless(window.link.path, desk.spec())
    reopened = desk.open(path=window.link.path)
    assert reopened.reading.spec.box.process == "" and reopened.reading.spec.box.process_cell == ""
    assert reopened.state.read.box.process == PROCESS_MACHINED
    assert process_line(reopened) == AS_BUILT + NO_ROW
    assert gear_states(reopened) == {"G1": "built", "G2": "built", "G3": "built", "G4": "built"}

    fresh = desk.tmp / "fresh"
    fresh.mkdir()
    rowless(fresh / f"{NAME}.xlsx", desk.spec(reducer()))
    new = desk.open(path=fresh / f"{NAME}.xlsx")
    assert new.record is None and new.state.read.box.process == PROCESS_PRINTED
    assert process_line(new) == "Printed, 0.4 mm nozzle"


@pytest.mark.parametrize("typed, nozzle, line", [
    ("PRINTED", "0.6", "Printed, 0.6 mm nozzle"),
    ("Machined", "", "Machined, as the Box sheet says: type Printed beside Process to print it"),
    ("wood", "", "Process does not read: the Checks panel says why"),
    ("printed", "0", "Printed; its Nozzle does not read: the Checks panel says why"),
])
def test_end_to_end_the_process_line_of_a_typed_box(desk, typed, nozzle, line):
    """With package B's read, no stand-in: what the line says of each word typed on the Box sheet."""
    from test_workbook_model import reducer
    spec = reducer()
    window = desk.open(replace(spec, box=replace(spec.box, process=typed, nozzle=nozzle)))
    assert process_line(window) == line


def test_printed_typed_on_a_built_gearbox_says_the_names_kept_once_and_not_on_the_next_update(desk, monkeypatch):
    """D10 and the F1 review's S2, through the window: the Update that makes the parts printed says once that their
    files keep their names (OutputGear's own Part name is never said); the next Update, which changes only G1's bore,
    does not say it again."""
    from test_workbook_window import save_in_excel
    window = built(desk)
    box_read_as(monkeypatch, "printed")
    printed = desk.open(path=window.link.path)
    printed.press_update()
    desk.finish(printed)
    told = ("The 3 parts now printed keep their file names, without the _P a part built printed is named with: "
            "Update SolidWorks never renames a file, and Build again… makes new parts named with _P if you want the "
            "mark.")
    assert printed.status.get().count(told) == 1, printed.status.get()
    save_in_excel(printed, {"Gears": {"J2": "7"}})
    assert gear_states(printed)["G1"] == "changes on Update", printed.status.get()
    printed.press_update()
    desk.finish(printed)
    assert printed.status.get().startswith("Updated SolidWorks: changed"), printed.status.get()
    assert "now printed" not in printed.status.get(), printed.status.get()


def test_a_blank_process_beside_a_broken_or_newer_record_says_so(desk, monkeypatch):
    """The F1 review's S5, through the window: a record that does not read, and one from a newer app, leave a blank
    Process resolved with no record; the line says what is true of each, not plain Printed."""
    window = built_before_f1(desk)
    path = pathlib.Path(store.link_record_path(window.link.path))
    raw = json.loads(path.read_text(encoding="utf-8"))
    box_read_as(monkeypatch, "", cell="")
    raw["link_schema_version"] = store.LINK_SCHEMA_VERSION + 1
    path.write_text(json.dumps(raw), encoding="utf-8")
    newer = desk.open(path=window.link.path)
    assert newer.process_record == "newer" and not newer.footer().build_enabled
    assert not newer.footer().update_enabled
    assert process_line(newer) == ("Not known: the record beside this workbook is from a newer Gear Generator, so a "
                                   "blank Process is not read as built here")
    path.write_text("{ not json", encoding="utf-8")
    broken = desk.open(path=window.link.path)
    assert broken.process_record == "broken" and broken.state.read.box.process == PROCESS_PRINTED
    assert broken.footer().build_enabled, broken.status.get()                 # Build makes a new gearbox: printed
    assert process_line(broken) == ("Printed, as for a new gearbox: the record of what was built beside this workbook "
                                    "cannot be read, so a blank Process is not read as built; 0.4 mm nozzle")


def test_a_copy_beside_its_originals_record_reads_a_blank_as_a_new_gearbox(desk, monkeypatch):
    """§1.3, the third check's should-fix: the record beside a copied workbook is the original's, so a blank Process
    is resolved with no record, Printed, and not Machined from the original's parts; by both of the window's reads."""
    window = built_before_f1(desk)
    folder = desk.tmp / "copy"
    folder.mkdir()
    copy_path = folder / f"{NAME}.xlsx"
    shutil.copy2(window.link.path, copy_path)
    shutil.copy2(store.link_record_path(window.link.path), store.link_record_path(str(copy_path)))
    box_read_as(monkeypatch, "", cell="")
    copy = desk.open(path=copy_path)
    assert copy.record is None
    assert copy.state.read.box.process == copy.state.spec.box.process == PROCESS_PRINTED
    assert copy._assess(copy.reading.spec, copy.reading.diagnostics).read.box.process == PROCESS_PRINTED
    assert process_line(copy) == "Printed, 0.4 mm nozzle"
    original = desk.open(path=window.link.path)                   # the original, beside its own record: as built
    assert original._assess(original.reading.spec, original.reading.diagnostics).read.box.process == PROCESS_MACHINED
