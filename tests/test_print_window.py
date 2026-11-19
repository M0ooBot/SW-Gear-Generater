"""What the user sees of Print files in the Workbook window (PLAN-PRINTED §3.1.3; package C of stage F2): the footer's
fifth button, named and placed as UI-DESIGN says, with the window keeping its 1080 px and the sentence its 400; the
press, planned from the window's planning read and refused by name before any job; the job, its footer and its
finish with the print list written; a close while it runs.

Needs Tk and a display, as ``test_workbook_window`` does, whose desk (a Tk root, the strip's stand-in, a fake worker on
the fake SolidWorks) these tests borrow; skipped where there is none. Every F2 finding is None until the probe's
reviewed run sets them, so package B's planner refuses every press with GATE_COPY; the tests that show a press going
through replace B's planner, job and list writer with stand-ins answering B's structures (F2-INTERFACES §2), not B's
fake, as the F2-0 review's S5 asks.
"""

import os
import pathlib
import shutil

import pytest

from gear_generator import printout as po, store, swbuild, ui_text
from gear_generator.gears import span as sp
from gear_generator.spec import GearSpec
from test_workbook_window import (LONG, NAME, PARTS, built, desk, record_of, w5_findings,  # noqa: F401 - fixtures
                                  width_and_height)

tk = pytest.importorskip("tkinter")


def footer_order(window):
    return [w.label.cget("text") for w in sorted(
        (w for w in window._foot.grid_slaves(row=0) if hasattr(w, "label")),
        key=lambda w: int(w.grid_info()["column"]))]


def test_print_files_is_the_footers_fifth_button_and_the_window_keeps_its_width(desk):
    from gear_generator import workbook_gui
    from gear_generator.theme import px
    fresh = desk.open(name="Fresh.xlsx")
    assert footer_order(fresh) == ["Export", "Export as…", "Print files", "Build"]
    assert fresh.print_button._enabled
    window = built(desk)
    window.note = (LONG, False)
    window._refresh_state()
    assert footer_order(window) == ["Export", "Export as…", "Print files", "Build again…", "Update SolidWorks"]
    assert width_and_height(window)[0] == px(workbook_gui.WINDOW_WIDTH)
    assert window.winfo_reqwidth() <= px(workbook_gui.WINDOW_WIDTH)
    assert int(str(window.status_label.cget("wraplength"))) >= px(workbook_gui.STATUS_MIN_WRAP)


def test_while_the_findings_are_unset_a_press_is_refused_by_name_and_nothing_is_submitted(desk, f2_unmeasured):
    window = built(desk)
    calls = len(desk.worker.calls)
    window.press_print()
    assert window.status.get().startswith("Print files waits until writing a STEP file is measured on this "
                                          "SolidWorks; nothing was written.")
    assert len(desk.worker.calls) == calls and window._pending is None


class Planned:
    """Stand-ins for B's planner, job and list writer, answering B's structures; ``calls`` keeps what the planner was
    handed."""

    def __init__(self, monkeypatch, desk, refusal=None, result=None, block=False):
        self.calls, self.lists = [], []
        self.folder = str(desk.folder / "print" / "2026-11-19 10.05.12")
        spec = GearSpec(module="1.5", teeth="17", process="printed")
        self.parts = (po.PrintPart(path=desk.part("Gear_m1.5_N17"), stem="Gear_m1.5_N17", rows=("G1",), spec=spec,
                                   span=sp.SpanReading("span", 2, 6.9, 6.9, 25.0)),
                      po.PrintPart(path=desk.part("OutputGear"), stem="OutputGear", rows=("G4",), count=2,
                                   spec=spec, user_features=("User Keyway",)))
        self.plan = (po.PrintPlan(refusal, revision=(34, 1, 1)) if refusal else
                     po.PrintPlan(None, self.parts, folder=self.folder, revision=(34, 1, 1), name=NAME,
                                  pressed=1795600000.0))
        self.result = result or po.PrintResult(
            written=tuple((p.path, self.folder + os.sep + p.stem + ".step") for p in self.parts), folder=self.folder,
            live_features=((self.parts[1].path, ("User Keyway",)),), active_restored=True)
        test = self

        def workbook_print(record, assessment, update_plan, output_folder, version, **kw):
            test.calls.append((record, assessment, update_plan, output_folder, version))
            test.keywords = kw
            return test.plan

        def print_parts(sw, plan):
            assert plan is test.plan
            return test.result

        def write_list(result, text):
            path = pathlib.Path(result.folder) / po.LIST_NAME
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            test.lists.append(text)
            return str(path)

        monkeypatch.setattr(po, "workbook_print", workbook_print)
        monkeypatch.setattr(swbuild, "print_parts", print_parts)
        monkeypatch.setattr(po, "write_list", write_list)


def test_a_press_is_planned_from_the_windows_read_and_the_strips_solidworks(desk, monkeypatch):
    window = built(desk)
    planned = Planned(monkeypatch, desk)
    desk.app._snapshot = {"revision": (32, 5, 0)}
    try:
        window.press_print()
    finally:
        del desk.app._snapshot
    record, assessment, update_plan, folder, version = planned.calls[-1]
    assert record is window.record and assessment is window.state and update_plan is window.update_plan
    assert folder == str(desk.folder) and version == (32, 5, 0)


def test_a_press_runs_one_job_holds_the_buttons_and_writes_the_files_and_the_list(desk, monkeypatch):
    from gear_generator import __version__
    window = built(desk)
    planned = Planned(monkeypatch, desk)
    before = record_of(window)
    window.press_print()
    assert window._job is not None and window._job.printing
    assert window.status.get() == "Print files is writing STEP files from SolidWorks…"
    assert not window.build_button._enabled and not window.update_button._enabled
    assert not window.print_button._enabled and not window.export_button._enabled
    desk.finish(window)
    assert window.status.get().startswith(f"Print files wrote 2 STEP files and their print list in "
                                          f"{ui_text.short_path(planned.folder, 64)}.")
    text = (pathlib.Path(planned.folder) / po.LIST_NAME).read_text(encoding="utf-8")
    assert text == ui_text.print_list_text(planned.plan, planned.result, __version__)
    assert "OutputGear.step\n  For G4 · print 2\n" in text and "Your features left in it: User Keyway." in text
    assert record_of(window) == before                       # Print files writes no record
    assert window.print_button._enabled and window.build_button._enabled


def test_a_refusal_the_plan_gives_is_said_by_name_and_nothing_is_submitted(desk, monkeypatch):
    window = built(desk)
    Planned(monkeypatch, desk, refusal=po.Refusal(po.UNSAVED_MARK, ("Gear_m1.5_N17", "OutputGear")))
    calls = len(desk.worker.calls)
    window.press_print()
    assert window.status.get().startswith("Print files wrote nothing: Gear_m1.5_N17 and OutputGear have changes from "
                                          "Update SolidWorks that are not saved; save them in SolidWorks, then print.")
    assert str(window.status_label.cget("foreground")) == ui_text_error()
    assert len(desk.worker.calls) == calls


def ui_text_error():
    from gear_generator import theme
    return theme.ERROR


def test_a_stop_in_the_job_is_said_with_where_the_files_are_and_the_list_heads_the_set(desk, monkeypatch):
    stop = po.Refusal(po.FILE_CHECK, ("OutputGear",), {"file": "OutputGear.step", "reason": po.OPEN_SHELL})
    window = built(desk)
    planned = Planned(monkeypatch, desk)
    planned.result = po.PrintResult(written=((planned.parts[0].path, planned.folder + os.sep + "Gear_m1.5_N17.step"),
                                             (planned.parts[1].path, planned.folder + os.sep + "OutputGear.step")),
                                    folder=planned.folder, failed=((planned.folder + os.sep + "OutputGear.step",
                                                                    po.OPEN_SHELL),),
                                    refusal=stop, active_restored=True)
    window.press_print()
    desk.finish(window)
    assert window.status.get().startswith(
        f"Print files stopped: OutputGear.step is not fit to print: it holds an open surface. What was written is in "
        f"{ui_text.short_path(planned.folder, 64)}, and its print list says not to print this set.")
    assert planned.lists[-1].startswith("DO NOT PRINT THIS SET: OutputGear.step is not fit to print: it holds an open "
                                        "surface.\n")


def test_a_read_excel_has_yet_to_recalculate_waits(desk, monkeypatch):
    window = built(desk)
    planned = Planned(monkeypatch, desk)
    window.recalc = True
    window.press_print()
    assert window.status.get().startswith(ui_text.PRINT_WAITS_FOR_RECALC)
    assert planned.calls == []


def test_a_missing_output_folder_is_said(desk, monkeypatch):
    """B's own planner, the findings as committed: the window's Output folder not on disk (the parts still are) is
    NO_FOLDER, said, nothing submitted."""
    window = built(desk)
    desk.app._snapshot = {"revision": tuple(desk.sw.revision)}        # the strip's SolidWorks, for B's gate
    gone = str(desk.tmp / "gone")
    monkeypatch.setattr(window, "_folder", lambda spec: gone)
    calls = len(desk.worker.calls)
    window.press_print()
    assert window.status.get().startswith(f"Print files wrote nothing: the output folder {ui_text.short_path(gone, 48)} "
                                          "does not exist; make it, or choose another, then print.")
    assert len(desk.worker.calls) == calls


def test_a_copy_of_a_workbook_is_refused_as_another_workbooks_record(desk, monkeypatch):
    window = built(desk)
    folder = desk.tmp / "copy"
    folder.mkdir()
    copy_path = folder / f"{NAME}.xlsx"
    shutil.copy2(window.link.path, copy_path)
    shutil.copy2(store.link_record_path(window.link.path), store.link_record_path(str(copy_path)))
    copy = desk.open(path=copy_path)
    desk.app._snapshot = {"revision": tuple(desk.sw.revision)}        # the strip's SolidWorks, for B's gate
    calls = len(desk.worker.calls)
    copy.press_print()                                       # B's own planner, handed the window's verdict (S8)
    assert copy.status.get().startswith(ui_text.print_refusal(po.Refusal(po.FOREIGN_RECORD)))
    assert len(desk.worker.calls) == calls
    planned = Planned(monkeypatch, desk)
    copy.press_print()
    assert planned.calls[-1][0] is None and store.same_path(planned.keywords["foreign_record"], window.link.path)
    window.press_print()
    assert planned.keywords["foreign_record"] == ""


def test_closing_mid_print_says_it_closes_once_the_list_is_written_then_closes(desk, monkeypatch):
    window = built(desk)
    planned = Planned(monkeypatch, desk)
    window.press_print()
    window.close()
    assert not window._closed() and window.status.get().endswith(ui_text.PRINT_CLOSES_WHEN_DONE)
    desk.worker.run()
    window._tick()
    assert window._closed() and planned.lists


def test_closing_twice_mid_print_asks_in_print_files_words(desk, monkeypatch):
    from gear_generator import workbook_gui
    window = built(desk)
    Planned(monkeypatch, desk)
    window.press_print()
    window.close()
    asked = []
    monkeypatch.setattr(workbook_gui, "ask_yes_no", lambda parent, title, text: asked.append((title, text)) or False)
    window.close()
    assert asked == [(ui_text.CLOSE_ANYWAY_TITLE, ui_text.PRINT_CLOSE_ANYWAY)]
    desk.worker.run()
    window._tick()


def test_a_job_that_raises_is_said_and_frees_the_window(desk, monkeypatch):
    window = built(desk)
    Planned(monkeypatch, desk)

    def broken(sw, plan):
        raise RuntimeError("the worker fell over")
    monkeypatch.setattr(swbuild, "print_parts", broken)
    window.press_print()
    desk.finish(window)
    assert window.status.get().startswith("Print files stopped — RuntimeError: the worker fell over")
    assert window._pending is None and window.print_button._enabled


def test_quitting_the_app_mid_print_asks_without_a_builds_journal(desk, monkeypatch):
    """gui.CloseGuard: a Workbook window's Print files job is not a build, so the quit question says no journal."""
    from gear_generator import gui
    window = built(desk)
    Planned(monkeypatch, desk)
    window.press_print()
    asked, said = [], []
    guard = gui.CloseGuard(desk.root, lambda text, ok=True: said.append(text), quit=lambda: None,
                           ask=lambda title, text: asked.append(text) or False)
    guard.request()
    guard.request()
    assert asked == [ui_text.quit_anyway_question(False)]
    desk.worker.run()
    window._tick()


# -- end to end on package B's planner, job and list writer, against the fake, the findings patched ------------------

def test_end_to_end_the_built_reducer_is_printed_whole_with_its_list(desk):
    """B's workbook_print, print_parts and write_list on the fake SolidWorks, the findings as committed (set on both
    versions by the probes' review) and nothing patched: every part once, its list beside them; nothing on record
    changes."""
    window = built(desk)
    before = record_of(window)
    desk.app._snapshot = {"revision": tuple(desk.sw.revision)}
    try:
        window.press_print()
        desk.finish(window)
    finally:
        del desk.app._snapshot
    folders = list((desk.folder / "print").iterdir())
    assert len(folders) == 1
    assert sorted(p.name for p in folders[0].iterdir()) == sorted([f"{stem}.step" for stem in PARTS] + [po.LIST_NAME])
    assert window.status.get().startswith(f"Print files wrote 4 STEP files and their print list in "
                                          f"{ui_text.short_path(str(folders[0]), 64)}.")
    text = (folders[0] / po.LIST_NAME).read_text(encoding="utf-8")
    assert text.startswith(f"Print list: {NAME}\n") and "Process: Machined\n" in text
    assert text.count("Machined: its backlash is a cutter's, not a printer's; no span.") == 4
    assert record_of(window) == before


def test_end_to_end_while_a_part_window_cannot_be_read_the_job_refuses_by_name(desk, monkeypatch, f2_unmeasured):
    """The same with only the gate measured (f2_unmeasured, then SAVE_AS_COPY and STEP_EXPORT_ON_2026) and
    PART_WINDOW_READ still None: the parts the build left open but not active are refused, named, and nothing is
    written."""
    from gear_generator import findings
    monkeypatch.setattr(findings, "SAVE_AS_COPY", 2)
    monkeypatch.setattr(findings, "STEP_EXPORT_ON_2026", True)
    window = built(desk)
    desk.app._snapshot = {"revision": tuple(desk.sw.revision)}
    try:
        window.press_print()
        desk.finish(window)
    finally:
        del desk.app._snapshot
    assert window.status.get().startswith(
        "Print files wrote nothing: Gear_m1.5_N17, Gear_m1.5_N68, Gear_m2_N17 and OutputGear are open in SolidWorks but "
        "not as the active document; close them, then print.")
    assert not (desk.folder / "print").exists() or not list((desk.folder / "print").iterdir())


def test_end_to_end_a_change_that_needs_a_new_revision_says_build_again(desk):
    """F2-REVIEW M1, on B's own planner with the findings as committed: a structural edit (G1's flank to arcs) needs a
    new revision, so Update SolidWorks is not run, and the press says Build again…, never Update SolidWorks."""
    from test_workbook_window import save_in_excel
    window = built(desk)
    save_in_excel(window, {"Gears": {"K2": "arcs"}})
    desk.app._snapshot = {"revision": tuple(desk.sw.revision)}        # the strip's SolidWorks, for B's gate
    calls = len(desk.worker.calls)
    window.press_print()
    said = window.status.get()
    assert said.startswith("Print files wrote nothing: the workbook's changes to Gear_m1.5_N17 need a new revision, "
                           "which Update SolidWorks cannot make; press Build again…, then print the new revision.")
    assert len(desk.worker.calls) == calls
