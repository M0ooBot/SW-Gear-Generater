"""What the user reads of F4 on the strip's form (PLAN-PRINTED §5.4, §5.6; F4-INTERFACES §5 and §6.2; package C of
stage F4): the Derived panel's *Holds once* row for a printed spur, helical, herringbone or ring gear, the line under
the rows for a ring past YS's range or not rated, no row for a machined gear, a bevel gear or a crossed pair's gears, each
column of a pair its own, and the README's section.

The figures are §5.3's (A1, A4, A5, A6, A9, A10), rounded by `gears.strength`'s one home; every sentence is pinned on
its exact string. The ring not rated quotes package A's clause (`ToothRating.why`), which is A's to word: its line is
pinned as *Holds once: not rated: * + that clause + *.*. The window's tests need Tk and a display, as
``test_print_form`` does, whose desk they borrow; skipped where there is none.
"""

import pathlib

import pytest

from gear_generator import ui_text
from gear_generator.gears import kind_for, strength
from gear_generator.spec import PROCESS_MACHINED, GearSpec

ROOT = pathlib.Path(__file__).resolve().parents[1]

A1 = dict(module="1.5", teeth="20", face_width="10")
A4 = dict(kind="helical", module="1.5", teeth="20", helix_angle="20", face_width="12")
A5 = dict(kind="herringbone", module="1.5", teeth="20", helix_angle="20", face_width="12", groove="4")
A6 = dict(module="1", teeth="54", face_width="10", teeth_side="internal")
A9 = dict(kind="helical", module="2", teeth="36", helix_angle="20", face_width="10", teeth_side="internal")
A10 = dict(module="1", teeth="33", face_width="10", teeth_side="internal")


def worked(process="printed", **fields):
    spec = GearSpec(process=process, **fields)
    kind = kind_for(spec)
    derived = kind.derive(spec)
    return spec, derived, kind.recipe_for(spec)


def rating(process="printed", crossed=False, **fields):
    spec, derived, recipe = worked(process, **fields)
    return ui_text.holds_rating(spec, derived, recipe, crossed=crossed)


# -- the words, without a window ----------------------------------------------------------------------------------

@pytest.mark.parametrize("fields, value", [
    (A1, "about 0.58 N·m · 39 N at 17 MPa"),
    (A4, "about 0.78 N·m · 49 N at 17 MPa"),
    (A5, "about 0.52 N·m · 33 N at 17 MPa"),
    (A6, "about 0.80 N·m · 29 N at 17 MPa · stress factor past its range"),
    (A9, "about 2.37 N·m · 62 N at 17 MPa · stress factor past its range"),
    (A10, "not rated: tips inside the base circle"),
], ids=["A1 spur", "A4 helical", "A5 herringbone", "A6 ring", "A9 helical ring", "A10 ring not rated"])
def test_a_printed_gear_shows_what_one_tooth_is_rated_to_take_once(fields, value):
    assert ui_text.holds_row(rating(**fields)) == ("Holds once", value)
    assert ui_text.HOLDS_LABEL == "Holds once"


@pytest.mark.parametrize("fields, newtons, metres", [(A1, 38.61, 0.5792), (A4, 49.06, 0.7831), (A5, 32.71, 0.5221),
                                                     (A6, 29.49, 0.7963), (A9, 61.823, 2.3685)])
def test_the_figures_are_gears_strengths_at_17_mpa_at_the_gears_own_width_rounded_by_its_one_home(fields, newtons,
                                                                                                  metres):
    r = rating(**fields)
    force = strength.holds(r)
    assert force == pytest.approx(newtons, abs=0.01) and strength.torque_held(r, force) == pytest.approx(metres, abs=1e-4)
    value = ui_text.holds_row(r)[1]
    assert value.startswith(f"about {strength.newton_metres(strength.torque_held(r, force))} N·m · "
                            f"{strength.newtons(force)} N at 17 MPa")


def test_an_allowable_given_is_the_one_said_and_the_figure_scales_with_it():
    r = rating(**A1)
    assert ui_text.holds_row(r, 34.0) == ("Holds once", "about 1.16 N·m · 77 N at 34 MPa")
    assert ui_text.holds_row(r, 12.5) == ("Holds once", "about 0.43 N·m · 28 N at 12.5 MPa")
    assert ui_text.holds_row(r, None) == ui_text.holds_row(r) == ui_text.holds_row(r, strength.ALLOWABLE_DEFAULT)


def test_the_line_under_the_rows_says_why_a_ring_is_past_the_stress_factors_range_or_not_rated():
    assert ui_text.holds_line(rating(**A1)) == "" and ui_text.holds_line(None) == ""
    assert ui_text.holds_line(rating(**A6)) == (
        "Holds once: the ring's 0.15 mm fillet is sharper than the stress factor's range, which is carried past it.")
    assert ui_text.holds_line(rating(**A9)) == (
        "Holds once: the ring's 0.3 mm fillet is sharper than the stress factor's range, which is carried past it.")
    ring = rating(**A10)
    assert not ring.rated and ring.short == "tips inside the base circle"
    assert ui_text.holds_line(ring) == f"Holds once: not rated: {ring.why}."
    assert ui_text.holds_line(ring) == (     # F4-REVIEW S1: the sentence as the user reads it, pinned whole
        "Holds once: not rated: its tips lie inside its base circle (31.000 mm against 31.010), where its teeth cannot "
        "be involute, and the rating needs an involute tip to load.")


def test_an_outside_gear_with_a_fillet_typed_that_sharp_says_its_own_past_the_range():
    """Past the plan's rings: a Fillet typed 0.1 mm on A1 gives qs 11.2, so the outside gear says it, as the gear's."""
    r = rating(fillet="0.1", **A1)
    assert r.past_range
    assert ui_text.holds_row(r) == ("Holds once", "about 0.33 N·m · 22 N at 17 MPa · stress factor past its range")
    assert ui_text.holds_line(r) == (
        "Holds once: the gear's 0.1 mm fillet is sharper than the stress factor's range, which is carried past it.")


@pytest.mark.parametrize("process, fields, crossed", [
    (PROCESS_MACHINED, A1, False), (PROCESS_MACHINED, A6, False), (PROCESS_MACHINED, A10, False),
    ("printed", dict(kind="bevel", module="1.5", teeth="20", mate_teeth="30", face_width="10"), False),
    ("printed", A4, True),
], ids=["machined spur", "machined ring", "machined ring tips inside", "printed bevel", "crossed pair's gear"])
def test_no_row_for_a_machined_gear_a_bevel_gear_or_a_crossed_pairs_gear(process, fields, crossed):
    r = rating(process, crossed=crossed, **fields)
    assert r is None and ui_text.holds_row(r) is None and ui_text.holds_line(r) == ""


def test_no_row_for_a_dog_or_a_hub_nor_for_a_gear_not_rated_for_any_other_reason():
    spec, derived, recipe = worked(**A1)
    for kind in ("dog", "hub", "sleeve"):
        assert ui_text.holds_rating(GearSpec(kind=kind, process="printed"), derived, recipe) is None
    assert ui_text.holds_rating(spec, None, recipe) is None
    for short, why in ((strength.SHORT_BEVEL, strength.WHY_BEVEL), (strength.SHORT_POINTED, strength.WHY_POINTED),
                       (strength.SHORT_NOT_DRAWN, "its tooth could not be drawn")):
        unrated = strength.ToothRating(rated=False, why=why, short=short)
        assert ui_text.holds_row(unrated) is None and ui_text.holds_line(unrated) == ""


def test_a_machined_gears_rows_are_exactly_derived_rows_as_before():
    spec, derived, recipe = worked(PROCESS_MACHINED, **A1)
    assert all(label != "Holds once" for label, _ in ui_text.derived_rows(derived))


def test_the_value_is_laid_into_its_column_whole_phrases_first():
    width = len
    assert ui_text.holds_value_lines("about 0.58 N·m · 39 N at 17 MPa", 40, width) == "about 0.58 N·m · 39 N at 17 MPa"
    assert ui_text.holds_value_lines("about 0.58 N·m · 39 N at 17 MPa", 20, width) == "about 0.58 N·m\n· 39 N at 17 MPa"
    assert ui_text.holds_value_lines("about 0.80 N·m · 29 N at 17 MPa · stress factor past its range", 32, width) == (
        "about 0.80 N·m · 29 N at 17 MPa\n· stress factor past its range")
    assert ui_text.holds_value_lines("about 0.80 N·m · 29 N at 17 MPa · stress factor past its range", 18, width) == (
        "about 0.80 N·m\n· 29 N at 17 MPa\n· stress factor\npast its range")
    assert ui_text.holds_value_lines("not rated: tips inside the base circle", 24, width) == (
        "not rated: tips inside\nthe base circle")


# -- the README --------------------------------------------------------------------------------------------------

def readme_section():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    head = "\n#### What a tooth is rated to take\n"
    assert text.count(head) == 1 and text.index(head) > text.index("\n### Printed gears\n")
    section = text.split(head, 1)[1]
    return section.split("\n#", 1)[0]


def test_the_readme_says_what_the_figure_is_and_is_not():
    section = " ".join(readme_section().split()).lower()
    for said in (
        "Holds once", "about 0.58 N·m · 39 N at 17 MPa", "ISO 6336-3", "the tooth as the app draws it",
        "the whole load on one tooth's tip", "an estimate of a single load", "not a life", "not a running rating",
        "far lower", "17 MPa is provisional", "35 MPa", "Allowable stress", "Box", "a printed tooth broken in a jig",
        "1.25", "0.7", "not rated", "stress factor past its range", "bevel", "crossed", "steel",
        "6 to 23 times", "heat", "wear", "creep", "fatigue", "layers",
        "so printed as typed they would break, or would not run.",
    ):
        assert said.lower() in section, said


# -- the window ------------------------------------------------------------------------------------------------------

tk = pytest.importorskip("tkinter")
from test_workbook_window import desk, w5_findings  # noqa: E402,F401 - fixtures


@pytest.fixture
def app(desk):
    from gear_generator import gui
    app = gui.GearApp(desk.root)
    app._worker = None              # no SolidWorks unless a test gives the form one
    return app


def form(app, side="a", **fields):
    for key, value in fields.items():
        app.gear_vars[side][key].set(value)


def table(app):
    """The Derived panel as the window lays it: [(label, [value per column])], in order."""
    cells = {}
    for widget in app.derived_rows.grid_slaves():
        if isinstance(widget, tk.Label):
            info = widget.grid_info()
            cells[(int(info["row"]), int(info["column"]))] = widget.cget("text")
    return [(text, [cells[(row, c)] for c in (1, 2) if (row, c) in cells])
            for (row, column), text in sorted(cells.items()) if column == 0]


def holds_cells(app):
    return next((values for label, values in table(app) if label == "Holds once"), None)


def joined(text):
    return text.replace("\n", " ")


def test_a_printed_spur_gear_shows_the_row_after_every_derived_row_and_before_the_measured_entry(app):
    """Last of the rows (after F2's span row and F3's Bore as cut), with F2's Measured entry still the panel's foot."""
    form(app, **A1)
    app._derive_now()
    labels = [label for label, _ in table(app)]
    assert labels[-2:] == ["Holds once", "Measured"]
    assert holds_cells(app) == ["about 0.58 N·m · 39 N at 17 MPa"]
    rows = app._rows_with_span("a")
    assert rows[-1] == ("Holds once", "about 0.58 N·m · 39 N at 17 MPa")
    assert labels[:-2] == [label for label, _ in rows[:-1]]
    assert app.measured_text.get() == ""


@pytest.mark.parametrize("fields, value", [(A4, "about 0.78 N·m · 49 N at 17 MPa"),
                                           (A5, "about 0.52 N·m · 33 N at 17 MPa")], ids=["A4", "A5"])
def test_a_printed_helical_and_herringbone_gear_show_theirs(app, fields, value):
    app.kind.set(fields["kind"])
    form(app, **{k: v for k, v in fields.items() if k != "kind"})
    app._derive_now()
    assert app._rows_with_span("a")[-1] == ("Holds once", value) and joined(holds_cells(app)[0]) == value


def test_a_printed_ring_past_the_range_says_so_in_its_row_and_on_a_line_under_the_rows(app):
    form(app, **A6)
    app._derive_now()
    assert app._rows_with_span("a")[-1] == (
        "Holds once", "about 0.80 N·m · 29 N at 17 MPa · stress factor past its range")
    assert holds_cells(app) == ["about 0.80 N·m · 29 N at 17 MPa\n· stress factor past its range"]
    assert app.measured_text.get() == (
        "Holds once: the ring's 0.15 mm fillet is sharper than the stress factor's range, which is carried past it.")


def test_a_ring_with_its_tips_inside_its_base_circle_reads_not_rated_and_says_why(app):
    form(app, **A10)
    app._derive_now()
    assert holds_cells(app) == ["not rated: tips inside the base circle"]
    assert app.measured_text.get() == f"Holds once: not rated: {app._ratings['a'].why}."
    assert app.measured_text.get() == (
        "Holds once: not rated: its tips lie inside its base circle (31.000 mm against 31.010), where its teeth cannot "
        "be involute, and the rating needs an involute tip to load.")


def test_a_recipe_b_ring_with_its_tips_inside_its_base_circle_reads_not_rated_on_the_form(app):
    """F4-REVIEW S4: a ring drawn by Arcs (recipe B), z 30, whose flank arc runs on to its tip, is not rated on the form
    itself, its row and its line the same as recipe A's, with its own diameters."""
    from gear_generator.spec import RECIPE_ARCS
    app.recipe.set(RECIPE_ARCS)
    form(app, **{**A10, "teeth": "30"})
    app._derive_now()
    assert app._held_spec("a").recipe == RECIPE_ARCS
    derived = app._derived["a"]
    assert derived is not None and app._ratings["a"] is not None
    assert (round(derived.da, 3), round(derived.db, 3)) == (28.0, 28.191)
    assert holds_cells(app) == ["not rated: tips inside the base circle"]
    assert app.measured_text.get() == (
        "Holds once: not rated: its tips lie inside its base circle (28.000 mm against 28.191), where its teeth cannot "
        "be involute, and the rating needs an involute tip to load.")


def test_a_machined_gear_shows_no_row_and_its_rows_are_derived_rows_as_before(app):
    app.process.set(PROCESS_MACHINED)
    app._on_process_changed()
    for fields in (A1, A6, A10):
        form(app, **fields)
        app._derive_now()
        assert holds_cells(app) is None
        assert app._rows_with_span("a") == ui_text.derived_rows(app._derived["a"])
        assert app.measured_text.get() == ""


def test_a_printed_bevel_gear_shows_no_row(app):
    app.kind.set("bevel")
    form(app, module="1.5", teeth="20", mate_teeth="30", face_width="10")
    app._derive_now()
    assert app._derived["a"] is not None and holds_cells(app) is None


def test_in_a_pair_each_column_has_its_own_and_the_line_says_which(app):
    app.mode.set("pair")
    app._on_mode_changed()
    app.mesh.set("internal")
    for side, teeth in (("a", "20"), ("b", "54")):
        form(app, side, module="1", teeth=teeth, face_width="10")
    app._derive_now()
    a, b = holds_cells(app)
    assert joined(a) == "about 0.22 N·m · 22 N at 17 MPa"
    assert joined(b) == "about 0.80 N·m · 29 N at 17 MPa · stress factor past its range"
    assert app.measured_text.get() == (
        "B: Holds once: the ring's 0.15 mm fillet is sharper than the stress factor's range, which is carried past it.")
    form(app, "b", teeth="33")
    app._derive_now()
    cell = holds_cells(app)[1]
    # Where the line breaks is the platform's font's (Linux's Tk breaks it once, Windows' twice); that it breaks, and
    # says the whole value, holds on both.
    assert joined(cell) == "not rated: tips inside the base circle" and "\n" in cell
    assert app.measured_text.get() == f"B: Holds once: not rated: {app._ratings['b'].why}."


WIDTH_CASES = {
    "single A1": ("single", "", dict(A1)), "single A6": ("single", "", dict(A6)),
    "single A10": ("single", "", dict(A10)), "single A1 sharp fillet": ("single", "", dict(A1, fillet="0.1")),
    "pair outside": ("pair", "external", dict(module="1", face_width="10")),
    "pair ring": ("pair", "internal", dict(module="1", face_width="10")),
    "pair ring unrated": ("pair", "internal", dict(module="1", face_width="10", b_teeth="33")),
}


def lay_out(app, case):
    mode, mesh_, fields = WIDTH_CASES[case]
    fields = dict(fields)
    b_teeth = fields.pop("b_teeth", "54")
    if mode == "pair":
        app.mode.set("pair")
        app._on_mode_changed()
        app.mesh.set(mesh_)
        form(app, "a", teeth="20", **fields)
        form(app, "b", teeth=b_teeth, **fields)
    else:
        form(app, **fields)
    app._derive_now()
    app.update_idletasks()
    return app.derived_panel.winfo_reqwidth(), app.derived_rows.winfo_reqwidth()


@pytest.mark.parametrize("process", ["printed", PROCESS_MACHINED])
@pytest.mark.parametrize("case", list(WIDTH_CASES))
def test_the_row_and_its_line_keep_the_strip_as_wide_as_it_is_without_them(app, monkeypatch, case, process):
    """The requirement, on whichever platform runs it: the Derived panel with the Holds once row and its line is no
    wider than the same form without them, and no wider than the strip's 460 px (gui.STRIP_WIDTH); the rows keep to
    the panel body's 434 (gui.DERIVED_ROWS_WIDTH). Windows' Tk measures the same text wider than Linux's, and gives a
    label a 2 px border where Linux gives 1, so a pixel count taken on one is not asserted on the other."""
    from gear_generator import gui, theme
    app.process.set(process)
    app._on_process_changed()
    panel, rows = lay_out(app, case)
    assert panel <= theme.px(gui.STRIP_WIDTH) and rows <= theme.px(gui.DERIVED_ROWS_WIDTH)
    if process == "printed":
        assert holds_cells(app) is not None
    monkeypatch.setattr(ui_text, "holds_row", lambda *_a, **_k: None)
    monkeypatch.setattr(ui_text, "holds_line", lambda *_a, **_k: "")
    app._derive_now()
    app.update_idletasks()
    assert holds_cells(app) is None
    assert panel <= app.derived_panel.winfo_reqwidth()


def test_a_long_warning_and_the_line_under_the_rows_wrap_inside_the_panel_body(app):
    """A ring of 33 teeth's own warning (older than F4, machined too) wrapped at 430 px came to 435 with a label's 6 px
    of chrome on Windows, a pixel past the body; each such line now wraps at the body's width less its own chrome."""
    from gear_generator import gui, theme
    form(app, **A10)
    app._derive_now()
    app.update_idletasks()
    body = theme.px(gui.DERIVED_ROWS_WIDTH)
    labels = app.warning_frame.winfo_children() + [app.measured_label]
    assert any("inside the base circle" in w.cget("text") for w in app.warning_frame.winfo_children())
    for label in labels:
        assert int(float(str(label.cget("wraplength")))) + gui.GearApp._chrome(label) == body
        assert label.winfo_reqwidth() <= body


def test_a_crossed_pairs_gears_show_no_row_and_a_parallel_pair_of_them_does(app):
    app.kind.set("helical")
    app.mode.set("pair")
    app._on_mode_changed()
    for side, teeth in (("a", "20"), ("b", "30")):
        form(app, side, module="1.5", teeth=teeth, helix_angle="20", face_width="12")
    app._derive_now()
    assert holds_cells(app) is not None and all(v.startswith("about ") for v in holds_cells(app))
    app.shafts.set("crossed")
    app._derive_now()
    assert app._derived["a"] is not None and holds_cells(app) is None and app.measured_text.get() == ""
