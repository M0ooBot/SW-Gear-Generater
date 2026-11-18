"""What the user sees of the bore as cut on the strip's form (PLAN-PRINTED §4.1, §4.1.1, §4.2, §4.6 package C;
docs/notes-printed/F3-INTERFACES.md §5, §9, §14): the Bore allowance, Drive and Flat rows under Bore, what a blank
allowance means as each placeholder says it, the Derived panel's Bore as cut, the three cards, and the strip's own path
through spec.as_built while a record is open (its derive, Update values, the count of what that would change, and a
Build, which keeps the opened part's as-built allowance by the coordinator's ruling on F3-0's decision 11).

Needs Tk and a display, as ``test_workbook_window`` does, whose desk (a Tk root, a fake worker on the fake SolidWorks)
these tests borrow; skipped where there is none. The figures are package A's (``spur.bore_allowance_of``); the tests
that mean the printed default set A's switch on (F3-INTERFACES §13), as it will be once B and C are in.

S4 of F3-0-REVIEW: the strip's real path on every printed part F1 and F2 built from the form
(``tests/fixtures/printed/F2_built.json``), not test_printed_rule.py's stand-in: Bore as cut says the Bore, the derived
gear's allowance is 0, nothing for Update values; Update values after a change writes no "Bore Allowance" and no derived
allowance, its .gear.json staying at sidecar 3; and a Build from it makes a part with none (S2).
"""

import json
from types import SimpleNamespace

import pytest

from gear_generator import store, swbuild, ui_text
from gear_generator.gears import kind_for, spur
from gear_generator.spec import PROCESS_MACHINED, PROCESS_PRINTED, GearSpec
from test_printed_rule import F2_BUILT
from test_workbook_window import built, desk, w5_findings  # noqa: F401 - fixtures

tk = pytest.importorskip("tkinter")


@pytest.fixture
def default_on(monkeypatch):
    """A printed gear's blank Bore allowance on a part not on record plans the printed default (F3-INTERFACES §13)."""
    monkeypatch.setattr(spur, "PRINTED_DEFAULT_IN_PLANS", True, raising=False)


@pytest.fixture
def app(desk):
    from gear_generator import gui
    app = gui.GearApp(desk.root)
    app._worker = None              # no SolidWorks unless a test gives the form one
    return app


def shown(widget) -> bool:
    return bool(widget.winfo_manager())


def row_shown(app, name, side="a"):
    return all(shown(w) for w in app.kind_rows[side][name])


def form(app, side="a", **values):
    for key, value in values.items():
        app.gear_vars[side][key].set(value)
    app._show_helix_rows()
    app._derive_now()


def drive(app, word, side="a"):
    """Choosing a Drive segment, as its command does."""
    app.gear_vars[side]["drive"].set(word)
    app._show_card(side, "drive")
    app._show_helix_rows()
    app._derive_now()


def derived_table(app):
    """The Derived panel's rows as the window lays them: {label: [value per column]}."""
    cells = {}
    for widget in app.derived_rows.grid_slaves():
        if isinstance(widget, tk.Label):
            info = widget.grid_info()
            cells[(int(info["row"]), int(info["column"]))] = widget.cget("text")
    rows = {}
    for (row, column), text in sorted(cells.items()):
        if column == 0:
            rows[text] = [cells[(row, c)] for c in range(1, 3) if (row, c) in cells]
    return rows


def placeholder(app, side="a"):
    return app._side_fields(side)["bore_allowance"]._placeholder.cget("text")


def card(app, side="a"):
    c = app.cards[side]
    return c.name.cget("text"), c.what.cget("text"), c.worked.cget("text")


def warnings(app):
    return [w.cget("text") for w in app._warning_widgets if isinstance(w, tk.Label)]


# -- the rows ----------------------------------------------------------------------------------------------------------


def test_the_bore_rows_sit_under_bore_and_flat_shows_only_while_drive_is_flat(app):
    """G3: Bore allowance, Drive and Flat under Bore, before Backlash; Flat only while Drive is flat, and a Flat left
    typed goes across blank with Drive round, as a hidden row does."""
    rows = app.kind_rows["a"]
    body = rows["bore"][0].master
    labels = {w.cget("text"): int(w.grid_info()["row"]) for w in body.grid_slaves(column=0) if isinstance(w, tk.Label)}
    assert [labels[t] for t in ("Face width", "Bore", "Bore allowance", "Drive", "Backlash")] == [3, 4, 5, 6, 8]
    assert "Flat" not in labels                                     # removed from the grid while Drive is round
    assert [rows[name][0].cget("text") for name in ("bore_allowance", "drive", "flat")] == [
        "Bore allowance", "Drive", "Flat"]
    assert row_shown(app, "bore_allowance") and row_shown(app, "drive") and not row_shown(app, "flat")
    assert app.gear_vars["a"]["drive"].get() == "round"
    drive(app, "flat")
    assert row_shown(app, "flat") and int(app.kind_rows["a"]["flat"][0].grid_info()["row"]) == 7
    form(app, flat="7")
    spec = app._gear_spec("a")
    assert (spec.drive, spec.flat) == ("flat", "7")
    drive(app, "round")
    assert not row_shown(app, "flat")
    spec = app._gear_spec("a")
    assert (spec.drive, spec.flat) == ("round", "") and not {"drive", "flat"} & set(spec.to_dict())
    assert app.gear_vars["a"]["flat"].get() == "7"                  # still typed, for when Drive is flat again


def test_a_ring_shows_none_of_the_bores_rows_and_a_bevel_gear_no_drive(app):
    """§4.1 and G5, G9: a ring has no bore, so none of the three (its typed fields go across blank, so a ring is never
    refused for a field it does not show); a bevel gear takes an allowance but no D, so no Drive and no Flat."""
    form(app, bore_allowance="0.3", flat="7")
    drive(app, "flat")
    app.gear_vars["a"]["teeth_side"].set("internal")
    app._show_helix_rows()
    assert not any(row_shown(app, name) for name in ("bore", "bore_allowance", "drive", "flat"))
    spec = app._gear_spec("a")
    assert (spec.bore_allowance, spec.drive, spec.flat) == ("", "round", "")
    app.gear_vars["a"]["teeth_side"].set("external")
    app.kind.set("bevel")
    app._on_kind_changed()
    assert row_shown(app, "bore_allowance") and not row_shown(app, "drive") and not row_shown(app, "flat")
    spec = app._gear_spec("a")
    assert (spec.bore_allowance, spec.drive, spec.flat) == ("0.3", "round", "")


def test_the_allowance_placeholder_says_what_a_blank_means(app, default_on):
    form(app, bore="8")
    assert app._printed() and placeholder(app) == "0.2 · printed"
    app.process.set(PROCESS_MACHINED)
    app._on_process_changed()
    app._derive_now()
    assert placeholder(app) == "0"


# -- the Derived panel and the cards --------------------------------------------------------------------------------


def test_bore_as_cut_is_shown_for_a_printed_gear_and_not_for_a_plain_machined_one(app, default_on):
    form(app, bore="8")
    assert derived_table(app)["Bore as cut"] == ["8.2 · 8 + 0.2"]
    form(app, bore_allowance="0")
    assert derived_table(app)["Bore as cut"] == ["8"]
    drive(app, "flat")
    form(app, bore_allowance="", flat="7")
    rows = derived_table(app)
    assert (rows["Bore as cut"], rows["Flat as cut"]) == (["8.2 · 8 + 0.2"], ["7.2 · 7 + 0.2"])
    drive(app, "round")
    app.process.set(PROCESS_MACHINED)
    app._on_process_changed()
    app._derive_now()
    assert "Bore as cut" not in derived_table(app) and "Flat as cut" not in derived_table(app)
    form(app, bore_allowance="0.3")
    assert derived_table(app)["Bore as cut"] == ["8.3 · 8 + 0.3"]


def test_each_bore_fields_card_follows_the_caret_and_drive_brings_up_its_own(app, default_on):
    form(app, bore="8")
    app._show_card("a", "bore_allowance")
    name, what, worked = card(app)
    assert name == "Bore allowance" and what.startswith("Added to Bore when the hole is cut, on the diameter")
    assert worked == "blank → 0.2 mm, the printed default → a hole of 8.2 mm"
    assert app.cards["a"].field == ui_text.BORE_DIAGRAM                       # Bore's diagram, borrowed
    drive(app, "flat")
    form(app, flat="7")
    name, what, worked = card(app)
    assert name == "Drive" and "phased by their flats in your machine and by their meshes in the assembly" in what
    assert worked == "flat → a D 8.2 mm across its round and 7.2 across its flat, its flat 3.1 mm from the axis on +X"
    app._show_card("a", "flat")
    assert card(app)[2] == "7 mm → the hole 7.2 mm across its flat, 3.1 from the axis · 1 mm deep on the shaft"


def test_the_new_warnings_and_refusals_read_on_the_form_word_for_word(app, default_on):
    """What the user reads under Derived for the bore's fields (package A's sentences, said by the strip as they come):
    an allowance with no Bore is a warning, and Build stays enabled (the ruling on F3-0's decision 15); the D's depth
    refusal says it is the shaft's own flat, D less F; its other bound; and Drive flat with no Flat or no Bore."""
    form(app, bore="", bore_allowance="0.2")
    assert warnings(app) == ["There is no Bore, so the Bore allowance is not used."]
    assert app.build_button._enabled
    form(app, bore="8", bore_allowance="")
    drive(app, "flat")
    assert "Drive flat needs a Flat: type your shaft's size across its flat." in warnings(app)
    assert not app.build_button._enabled
    form(app, flat="7.8")
    assert warnings(app) == [
        "Your shaft's flat is 0.2 mm deep (Bore 8 less Flat 7.8), under the 0.3 mm a printed D needs to hold; type a "
        "Flat of at most 7.7 mm, which leaves the flat a little play, or use a round bore."]
    form(app, flat="4.9")
    assert warnings(app) == [
        "The flat is 1 mm from the axis, under a quarter of the hole's radius (1.025 mm); type a Flat of at least "
        "4.925 mm, or use a round bore."]
    form(app, bore="", flat="7")
    assert "Drive flat needs a Bore: type your shaft's diameter in Bore, or choose round." in warnings(app)


# -- a record open: the strip through spec.as_built (S4, S2) ----------------------------------------------------------


def opened(app, tmp_path, name):
    """One of the printed parts F2 built from the form, its .gear.json opened on the strip with its part active in
    SolidWorks. The form's Kind is the record's (Open .gear.json leaves Kind as the form had it, before and after F3).
    The fixture's specs leave the Flank blank (they were planned from GearSpec, not read off the form), where a record
    the strip writes holds the form's, A: it is written A here, or every change would read as a new flank recipe and
    Update values would have nothing to count."""
    raw = json.loads(F2_BUILT["strip"][name]["sidecar"])
    assert raw["gear"]["spec"]["recipe"] == ""
    raw["gear"]["spec"]["recipe"] = "A"
    path = tmp_path / "opened.gear.json"
    path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
    spec = GearSpec.from_dict(raw["gear"]["spec"])
    app.kind.set(spec.kind)
    app._on_kind_changed()
    app._load_record(str(path))
    sidecar = app._loaded
    assert sidecar is not None and sidecar.schema_version == 3
    app._snapshot = {"path": sidecar.part_path, "title": sidecar.part_title, "is_part": True, "revision": ()}
    app._derive_now()
    return path, sidecar, spec


class Capture:
    """A worker that takes the job and never answers: what the press handed it is in the strip's build context."""

    def submit(self, job):
        self.job = job
        return SimpleNamespace(poll=lambda: None)


@pytest.mark.parametrize("name", sorted(F2_BUILT["strip"]))
def test_a_printed_part_built_before_f3_opened_on_the_strip_reads_as_built(app, tmp_path, default_on, name):
    path, sidecar, spec = opened(app, tmp_path, name)
    g = app._derived["a"]
    assert g is not None and g.bore_allowance == 0.0 and g.bore_flat is None
    assert app._held_spec("a").built_allowance == "0" and app._gear_spec("a").built_allowance == ""
    assert derived_table(app)["Bore as cut"] == [ui_text._n(spec.bore_mm())]
    assert app._update_target()[0] == 0 and not shown(app.update_button)
    assert placeholder(app) == "0 · as built"
    stem = sidecar.part_title.rsplit(".", 1)[0]
    assert app.mode_note.get() == (f"Build will make {app._stems()[0]}.SLDPRT with no bore allowance, as {stem} was "
                                   "built, since Bore allowance is blank.")
    app._show_card("a", "bore_allowance")
    assert card(app)[2] == f"blank → 0 mm, as built → a hole of {ui_text._n(spec.bore_mm())} mm"
    # Without the record, the same form is a part not yet built: the printed default.
    app._loaded = None
    app._derive_now()
    assert app._derived["a"].bore_allowance == pytest.approx(0.2) and placeholder(app) == "0.2 · printed"


@pytest.mark.parametrize("name", sorted(F2_BUILT["strip"]))
def test_update_values_on_a_part_built_before_f3_writes_no_allowance(app, tmp_path, default_on, name):
    """S2 for the strip: a value changed on the opened record (its face width) is one Update values carries, and the
    record it writes holds no "Bore Allowance", no derived allowance, and stays at sidecar 3."""
    path, sidecar, spec = opened(app, tmp_path, name)
    form(app, face_width=str(float(spec.face_width) + 2))
    count, document = app._update_target()
    assert count >= 1 and document == sidecar.part_title
    app._worker = Capture()
    app._update_values()
    context = app._build_context
    assert context["job_kind"] == "update" and context["spec"].built_allowance == "0"
    assert "Bore Allowance" not in [v.name for v in context["variables"]]
    app._pending_build = None
    app._finish_update(context, swbuild.UpdateResult(document=sidecar.part_title, changed=["Face Width"],
                                                     trig=sidecar.record.trig or "degrees"))
    written = store.load(str(path))
    assert written.schema_version == 3
    assert "Bore Allowance" not in dict(written.record.variables)
    assert "bore_allowance" not in json.dumps(written.record.derived)
    assert "built_allowance" not in written.record.spec and "bore_allowance" not in written.record.spec
    assert written.record.spec["face_width"] == str(float(spec.face_width) + 2)


def test_a_typed_allowance_on_a_part_built_before_f3_is_honoured_and_said(app, tmp_path, default_on):
    """A figure typed is what it says, record open or not: the hole as cut follows it, and the bar does not say the
    as-built figure is kept; Update values refuses it, a part built with none taking one only as a new part."""
    opened(app, tmp_path, "spur")
    form(app, bore_allowance="0.3")
    assert app._held_spec("a").built_allowance == "" and app._derived["a"].bore_allowance == pytest.approx(0.3)
    assert derived_table(app)["Bore as cut"] == ["10.3 · 10 + 0.3"]
    assert "since Bore allowance is blank" not in app.mode_note.get()
    # None to some is a new part (G4; package B's structural_change, given the record's globals): nothing for Update
    # values, and a press says why.
    assert app._update_target()[0] == 0 and not shown(app.update_button)
    app._worker = Capture()
    app._update_values()
    assert app._build_context is None and app.status.get() == (
        "A bore allowance cannot be added to or taken out of a built part through its values; build it again as a new "
        "part.")


def test_a_build_from_a_record_built_before_f3_keeps_its_allowance(desk, tmp_path, default_on):
    """The coordinator's ruling on F3-0's decision 11, through the strip's own Build on the fake SolidWorks: with
    Coupon_C's record open (built before F3, no allowance) and Bore allowance blank, the part built holds no "Bore
    Allowance" and its .gear.json is at sidecar 3; the same form with no record open builds the printed default."""
    from gear_generator import gui
    app = gui.GearApp(desk.root)
    opened(app, tmp_path, "coupon")
    app._worker = desk.worker
    app.out_folder.set(str(desk.folder))
    form(app, name="Coupon_F3")
    assert app.mode_note.get() == ("Build will make Coupon_F3.SLDPRT with no bore allowance, as Coupon_C was built, "
                                   "since Bore allowance is blank.")
    app._build_gear()
    desk.worker.run()
    app._collect_build()
    kept = store.load(store.sidecar_path(str(desk.folder / "Coupon_F3.SLDPRT")))
    assert kept is not None and kept.schema_version == 3
    assert "Bore Allowance" not in dict(kept.record.variables) and "bore_allowance" not in kept.record.spec
    assert app._loaded.part_path == kept.part_path                     # the part just built is the record open now
    app._loaded = None
    form(app, name="Coupon_new")
    assert app.mode_note.get() == "Build will make Coupon_new.SLDPRT."
    app._build_gear()
    desk.worker.run()
    app._collect_build()
    new = store.load(store.sidecar_path(str(desk.folder / "Coupon_new.SLDPRT")))
    assert new.schema_version == 4 and dict(new.record.variables)["Bore Allowance"] == "0.2"


# -- the Workbook window's checks read a part on record as built (F3-INTERFACES §14, S3; the coordinator's ruling) ---


def test_the_windows_warnings_for_a_gearbox_built_before_f3_are_unchanged_with_the_default_on(desk, monkeypatch):
    """WorkbookWindow._assess hands assess the record _blank_process reads, so a row whose part is on record is checked
    as built. The reducer printed, G1's bore 18.7 (rim 1.525 mm to its 21.75 mm root, just over one module), built with
    the switch off as F2 built it; then the switch on: the window says exactly what it said, where G1 read as a part not
    yet built would be cut at 18.9 and warned of a 1.425 mm rim."""
    from dataclasses import replace
    from gear_generator.workbook import assess as wb_assess
    from test_printed_window import box_read_as
    from test_workbook_model import reducer
    monkeypatch.setattr(spur, "PRINTED_DEFAULT_IN_PLANS", False, raising=False)
    box_read_as(monkeypatch, "printed")
    spec = reducer()
    spec = replace(spec, gears=(replace(spec.gears[0], bore="18.7"),) + spec.gears[1:])
    window = built(desk, spec)
    record = store.read_link_record(window.link.path)
    assert all("Bore Allowance" not in dict(p.variables) for p in record.current_parts())
    before = [d.message for d in window.state.diagnostics]
    monkeypatch.setattr(spur, "PRINTED_DEFAULT_IN_PLANS", True, raising=False)
    window._plan()
    window._paint()
    assert [d.message for d in window.state.diagnostics] == before
    assert window.assessed_record is not None
    # Read with no record, the same rows would be warned of the hole a new part is cut with: the wiring is what holds.
    fresh = wb_assess.assess(window.reading.spec, window.reading.diagnostics, str(desk.folder), "",
                             blank_process="printed")
    assert [d.message for d in fresh.diagnostics if d.message not in before] == [
        "Gears!J2: G1: The bore leaves 1.425 mm of rim under the teeth, thinner than one module (1.5 mm)."]
