"""What the user sees of the span over k teeth and of Print files on the strip's form (PLAN-PRINTED §3.0, §3.1.3;
package C of stage F2): the span row after Tooth at pitch, the Measured entry and its line, the span's card, the
SolidWorks bar's line naming the file Print files would write, and the footer's Print files button with its press and
its finish.

Needs Tk and a display, as ``test_workbook_window`` does, whose desk (a Tk root and a fake worker) these tests borrow;
skipped where there is none. The span is package A's (``gears.span``, committed). The plan and the job are package B's
(``printout.form_print``, ``swbuild.print_parts``, ``printout.write_list``): every F2 finding is None until the probe's
reviewed run sets them, so B's planner refuses every press with GATE_COPY; the tests that show a press going through
replace the planner, the job and the list's writer with stand-ins that answer B's structures (F2-INTERFACES §2), as the
review's S5 asks, and never B's fake while B is changing it.
"""

import os
import pathlib

import pytest

from gear_generator import printout as po, store, swcom, ui_text
from gear_generator.gears import span as sp
from gear_generator.spec import PROCESS_MACHINED, RECIPE_ARCS, GearSpec
from test_workbook_window import desk, w5_findings  # noqa: F401 - fixtures

tk = pytest.importorskip("tkinter")


@pytest.fixture
def app(desk):
    from gear_generator import gui
    app = gui.GearApp(desk.root)
    app._worker = None              # no SolidWorks unless a test gives the form one
    return app


def coupon(app, **fields):
    values = dict(module="1.5", teeth="20", face_width="8", bore="8", name="Coupon_A")
    values.update(fields)
    for key, value in values.items():
        app.gear_vars["a"][key].set(value)
    app._derive_now()


def shown(widget):
    return bool(widget.winfo_manager())


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


def labels_in_order(app):
    cells = [(int(w.grid_info()["row"]), w.cget("text")) for w in app.derived_rows.grid_slaves(column=0)
             if isinstance(w, tk.Label)]
    return [text for _, text in sorted(cells)]


# -- the span over k teeth -----------------------------------------------------------------------------------------


def test_a_printed_coupon_shows_its_span_after_tooth_at_pitch_and_a_measured_entry(app):
    coupon(app)
    rows = derived_table(app)
    assert rows["Span over 3 teeth"] == ["11.209"]
    order = labels_in_order(app)
    assert order[order.index("Tooth at pitch") + 1] == "Span over 3 teeth"
    assert order[-1] == "Measured" and shown(app.measured_fields["a"]) and not shown(app.measured_fields["b"])
    assert app.measured_text.get() == "" and not shown(app.measured_label)


def test_a_machined_gear_shows_no_span_and_no_measured_entry(app):
    app.process.set(PROCESS_MACHINED)
    app._on_process_changed()
    coupon(app)
    assert not any(label.startswith("Span") for label in labels_in_order(app))
    assert "Measured" not in labels_in_order(app) and not shown(app.measured_fields["a"])
    assert app.measured_text.get() == ""


def test_a_reading_typed_says_what_the_printer_adds_and_nothing_else_changes(app):
    coupon(app)
    before = derived_table(app)
    app.measured["a"].set("11.291")
    assert app.measured_text.get() == ("Your printer adds 0.041 mm a flank: a backlash of 0.173 mm a gear keeps 0.04 mm "
                                       "of play a flank.")
    assert shown(app.measured_label) and derived_table(app) == before
    app.measured["a"].set("11.17")
    assert app.measured_text.get() == ("Your printer takes 0.019 mm off a flank: a backlash of 0.1 mm a gear, the least "
                                       "proposed (0.04 mm of play a flank alone would ask less).")
    app.measured["a"].set("11,2x")
    assert app.measured_text.get() == "Measured: type the calipers' reading in mm, a number such as 11.25."
    app.measured["a"].set("")
    assert app.measured_text.get() == "" and not shown(app.measured_label)


def test_the_measured_line_uses_the_gears_own_normal_pressure_angle(app):
    coupon(app, pressure_angle="25")
    reading = app._spans["a"]
    value = round(reading.w_mm + 0.2, 4)
    app.measured["a"].set(str(value))
    told = sp.measured(reading, value, 25.0, 1.5)
    assert f"a backlash of {ui_text._n(told.backlash_mm)} mm a gear" in app.measured_text.get()


def test_a_gear_drawn_with_arcs_says_why_it_shows_no_figure(app):
    app.recipe.set(RECIPE_ARCS)
    coupon(app)
    assert not any(label.startswith("Span") for label in labels_in_order(app))
    assert "Measured" not in labels_in_order(app)
    assert app.measured_text.get() == "Span over k teeth: not one figure on arcs; choose Involute to measure"


def test_in_a_pair_each_gear_has_its_own_span_and_entry_and_lines_say_which(app):
    app.mode.set("pair")
    app._on_mode_changed()
    for side, teeth in (("a", "20"), ("b", "50")):
        app.gear_vars[side]["module"].set("1.5")
        app.gear_vars[side]["teeth"].set(teeth)
    app._derive_now()
    rows = derived_table(app)
    assert rows["Span over 3 teeth"] == ["11.209", "—"]
    k_b = app._spans["b"].k
    assert rows[f"Span over {k_b} teeth"] == ["—", ui_text._n(app._spans["b"].w_mm)]
    assert shown(app.measured_fields["a"]) and shown(app.measured_fields["b"])
    app.measured["b"].set(str(round(app._spans["b"].w_mm + 0.1, 3)))
    assert app.measured_text.get().startswith("B: Your printer adds 0.05 mm a flank")


def test_the_measured_entry_brings_up_the_spans_card(app):
    coupon(app)
    app._show_card("a", "span")
    card = app.cards["a"]
    assert shown(card)
    assert card.name.cget("text") == "Span over k teeth"
    assert card.what.cget("text") == ui_text.SPAN_CARD_COPY
    assert card.worked.cget("text").startswith("k 3 · W 11.209 mm · jaws touch at Ø ")
    app.gear_vars["a"]["teeth"].set("30")
    app.gear_vars["a"]["module"].set("2")
    app._derive_now()
    assert card.worked.cget("text").startswith("k 4 · W 21.223 mm")


# -- Print files ---------------------------------------------------------------------------------------------------


def footer_order(app):
    return [w.label.cget("text") for w in sorted(
        (w for w in app._footer.grid_slaves(row=0) if hasattr(w, "label")),
        key=lambda w: int(w.grid_info()["column"]))]


def test_print_files_sits_in_the_footer_between_update_values_and_build_and_keeps_the_strips_width(app):
    from gear_generator import gui
    from gear_generator.theme import px
    coupon(app)
    assert footer_order(app) == ["Print files", "Build"]
    assert app.print_button._enabled
    app.update_button.grid()
    app._wrap_footer()
    app._set_status("A long sentence to wrap. " * 12)
    app.update_idletasks()
    assert footer_order(app) == ["Update values", "Print files", "Build"]
    assert app._footer.winfo_reqwidth() <= px(gui.STRIP_WIDTH)
    app.update_button.grid_remove()
    app._wrap_footer()
    assert int(str(app.status_label.cget("wraplength"))) >= px(250)      # about the 260 px it always had


def test_without_solidworks_print_files_says_so_and_submits_nothing(app):
    app._print_files()
    assert app.status.get() == ("SolidWorks cannot be reached from here, so Print files wrote nothing. "
                                + swcom.unavailable_reason()).strip()
    assert app._pending_build is None


def test_while_the_findings_are_unset_a_press_is_refused_by_name_and_nothing_is_submitted(app, desk):
    """Every F2 finding is None: B's planner refuses with GATE_COPY, said, and no job reaches the worker."""
    app._worker = desk.worker
    app._snapshot = {"key": (1, "", ""), "path": "", "is_part": False, "title": "", "revision": (34, 1, 1)}
    coupon(app)
    app._print_files()
    assert app.status.get() == ("Print files waits until writing a STEP file is measured on this SolidWorks; nothing "
                                "was written.")
    assert desk.worker.calls == [] and app._pending_build is None
    assert app.print_line.get() == "" and not shown(app.print_label)


def test_the_snapshot_carries_the_revision_for_the_gate():
    from gear_generator import gui

    class Session:
        pid, label, revision = 7, "SolidWorks 2026 (revision 34.1.1)", (34, 1, 1)

        def active_document(self):
            return None
    assert gui._read_snapshot(Session())["revision"] == (34, 1, 1)


class Planned:
    """Stand-ins for B's planner, job and list writer, answering B's structures."""

    def __init__(self, monkeypatch, tmp_path, result=None, write=True):
        self.calls, self.lists = [], []
        self.folder = str(tmp_path / "out" / "print" / "2026-11-19 10.05.12")
        part = po.PrintPart(path=str(tmp_path / "out" / "Coupon_A.SLDPRT"), stem="Coupon_A",
                            spec=GearSpec(module="1.5", teeth="20", face_width="8", bore="8", process="printed"),
                            span=sp.SpanReading("span", 3, 11.20875, 11.20875, 30.3374))
        self.plan = po.PrintPlan(None, (part,), folder=self.folder, revision=(34, 1, 1), name="Coupon_A",
                                 pressed=1795600000.0)
        self.result = result or po.PrintResult(written=((part.path, self.folder + os.sep + "Coupon_A.step"),),
                                               folder=self.folder, active_restored=True)
        test = self

        def form_print(sidecar, part_path, output_folder, version, **kw):
            test.calls.append((sidecar, part_path, output_folder, version))
            return test.plan

        def print_parts(sw, plan):
            assert plan is test.plan
            return test.result

        def write_list(result, text):
            if not write:
                raise OSError("the disk is full")
            path = pathlib.Path(result.folder) / po.LIST_NAME
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            test.lists.append(text)
            return str(path)

        from gear_generator import swbuild
        monkeypatch.setattr(po, "form_print", form_print)
        monkeypatch.setattr(swbuild, "print_parts", print_parts)
        monkeypatch.setattr(po, "write_list", write_list)


def active_part(app, tmp_path):
    """The snapshot of SolidWorks with Coupon_A active, its .gear.json beside it (a real record, as Build writes)."""
    folder = tmp_path / "out"
    folder.mkdir(exist_ok=True)
    part = folder / "Coupon_A.SLDPRT"
    part.write_bytes(b"part")
    sidecar = store.built_sidecar(str(part), part.name, kind="spur", recipe="A",
                                  spec=GearSpec(process="printed").to_dict(), derived={}, variables=[], features=[],
                                  dimensions=[], manual_steps=[], template="", trig="degrees", written_by="test")
    store.save(store.sidecar_path(str(part)), sidecar)
    app.out_folder.set(str(folder))
    app._snapshot = {"key": (1, part.name, str(part)), "path": str(part), "is_part": True, "title": part.name,
                     "revision": (34, 1, 1), "version": "SolidWorks 2026", "doc_type": 1}
    return part


def test_the_bar_names_the_file_print_files_would_write(app, desk, monkeypatch, tmp_path):
    planned = Planned(monkeypatch, tmp_path)
    part = active_part(app, tmp_path)
    coupon(app)
    assert app.print_line.get() == "Print files will write Coupon_A.step from the active part."
    assert shown(app.print_label)
    sidecar, path, folder, version = planned.calls[-1]
    assert sidecar is not None and store.same_path(sidecar.part_path, str(part)) and path == str(part)
    assert folder == str(tmp_path / "out") and version == (34, 1, 1)


def test_a_press_writes_the_file_and_its_list_and_says_where(app, desk, monkeypatch, tmp_path):
    from gear_generator import __version__, theme
    planned = Planned(monkeypatch, tmp_path)
    active_part(app, tmp_path)
    app._worker = desk.worker
    coupon(app)
    app._print_files()
    assert app.status.get() == "Print files is writing STEP files from SolidWorks…"
    assert not app.print_button._enabled and not app.build_button._enabled
    desk.worker.run()
    app._collect_build()
    assert app.status.get() == (f"Print files wrote Coupon_A.step and its print list in "
                                f"{ui_text.short_path(planned.folder, 64)}.")
    assert str(app.status_label.cget("foreground")) == theme.OK
    text = (pathlib.Path(planned.folder) / po.LIST_NAME).read_text(encoding="utf-8")
    assert text == ui_text.print_list_text(planned.plan, planned.result, __version__)
    assert app.print_button._enabled


def test_a_press_with_no_output_folder_says_so(app, desk, monkeypatch, tmp_path):
    Planned(monkeypatch, tmp_path)
    active_part(app, tmp_path)
    app._worker = desk.worker
    app.out_folder.set(str(tmp_path / "gone"))
    app._print_files()
    assert app.status.get() == ui_text.PRINT_FORM_NEEDS_FOLDER and desk.worker.calls == []


def test_a_refusal_in_the_job_is_said_and_no_list_is_written_without_a_folder(app, desk, monkeypatch, tmp_path):
    refused = po.PrintResult(refusal=po.Refusal(po.MODIFIED, ("Coupon_A",)), active_restored=True)
    planned = Planned(monkeypatch, tmp_path, result=refused)
    active_part(app, tmp_path)
    app._worker = desk.worker
    app._print_files()
    desk.worker.run()
    app._collect_build()
    assert app.status.get() == ("Print files wrote nothing: Coupon_A is changed in SolidWorks and not saved; save it, "
                                "or close it without saving, then print.")
    assert planned.lists == []


def test_a_list_that_cannot_be_written_is_said(app, desk, monkeypatch, tmp_path):
    from gear_generator import theme
    planned = Planned(monkeypatch, tmp_path, write=False)
    active_part(app, tmp_path)
    app._worker = desk.worker
    app._print_files()
    desk.worker.run()
    app._collect_build()
    assert app.status.get() == (
        f"Print files wrote Coupon_A.step and its print list in {ui_text.short_path(planned.folder, 64)}. Its print "
        "list could not be written (OSError: the disk is full), so nothing in that folder says what each file is or "
        "whether to print it: press Print files again for a set with its list.")
    assert str(app.status_label.cget("foreground")) == theme.ERROR


def test_a_job_that_raises_is_said_as_print_files_stopping(app, desk, monkeypatch, tmp_path):
    Planned(monkeypatch, tmp_path)
    from gear_generator import swbuild

    def broken(sw, plan):
        raise swcom.SolidWorksError("SolidWorks stopped answering")
    monkeypatch.setattr(swbuild, "print_parts", broken)
    active_part(app, tmp_path)
    app._worker = desk.worker
    app._print_files()
    desk.worker.run()
    app._collect_build()
    assert app.status.get() == "Print files stopped: SolidWorks stopped answering."


# -- end to end on package B's planner, job and list writer, against the fake, the findings patched ------------------

MEASURED_ON_2026 = (("SAVE_AS_COPY", 2), ("STEP_EXPORT_ON_2026", True), ("PART_WINDOW_READ_ON_2026", True),
                    ("STEP_EXPORT_NEEDS_ACTIVE_ON_2026", False))


def test_end_to_end_a_built_coupon_is_printed_from_the_form(desk, monkeypatch):
    """B's form_print, print_parts and write_list on the fake SolidWorks, with the findings a reviewed probe run would
    set patched in (every F2 finding is None in findings.py): the bar names the file, the press writes it and its list
    into a folder of the Output folder's print folder, and the status says where."""
    from gear_generator import __version__, findings, gui
    for name, value in MEASURED_ON_2026:
        monkeypatch.setattr(findings, name, value, raising=False)
    app = gui.GearApp(desk.root)
    app._worker = desk.worker
    app.out_folder.set(str(desk.folder))
    coupon(app)
    app._build_gear()
    desk.worker.run()
    app._collect_build()
    part = str(desk.folder / "Coupon_A.SLDPRT")
    desk.sw.open_document(part)
    desk.sw.pid, desk.sw.label = 1, "SolidWorks 2026"
    app._snapshot = gui._read_snapshot(desk.sw)
    app._derive_now()
    assert app.print_line.get() == "Print files will write Coupon_A.step from the active part."
    app._print_files()
    desk.worker.run()
    app._collect_build()
    folders = list((desk.folder / "print").iterdir())
    assert len(folders) == 1 and sorted(p.name for p in folders[0].iterdir()) == ["Coupon_A.step", po.LIST_NAME]
    assert app.status.get() == (f"Print files wrote Coupon_A.step and its print list in "
                                f"{ui_text.short_path(str(folders[0]), 64)}.")
    text = (folders[0] / po.LIST_NAME).read_text(encoding="utf-8")
    assert text.startswith(f"Print list: Coupon_A\nPressed ") and f"Gear Generator {__version__}, on SolidWorks" in text
    assert "  Span over 3 teeth: 11.209 mm (the calipers square to the axis, at mid-face).\n" in text
