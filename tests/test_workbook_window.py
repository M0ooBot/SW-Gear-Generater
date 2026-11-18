"""The Workbook window's W4 and W5 wiring, through the real window (docs/PLAN-WORKBOOK.md §4.2–§4.5, §5).

Build makes the parts, the layout part and the assembly, whose gears are mated so the train turns (W5); Update
SolidWorks carries a later edit of the workbook into them, putting a train the user turned back only when it must
move a gear; Build again… makes the next revision. Each press goes through a fake worker whose job runs against the
fake SolidWorks of ``test_swbuild`` — saving real (empty) files, so the window's own planning, which looks at the
disk, sees what a job left — and the finishes write real sidecars and a real record beside the workbook. Needs Tk
and a display (run on Windows: ``python.exe -m pytest tests/test_workbook_window.py``); skipped where there is
none.

The W5 findings the plans read are pinned here (``w5_findings``), so no test hangs on what the probes have
committed today: a test that needs the other branch of one says so. Tests of W4's own static gearbox (its Update of
a tooth count among them) build it with :func:`built_w4`, as a gearbox built before W5 stays static (D5).
"""

import hashlib
import math
import json
import os
import pathlib

import pytest

from gear_generator import findings, store, swbuild, ui_text
from gear_generator.swcom import DocInfo
from gear_generator.workbook import model, motion, xlsx
from gear_generator.workbook.gearbox import LayoutReuse
from gear_generator.workbook.model import Gear
from test_swbuild import FakeSolidWorks
from test_workbook_build import a_later_kind  # noqa: F401 - a fixture: a dog ring made a later phase's (W99)
from test_swbuild import mode_findings  # noqa: F401 - a fixture: the findings a build with modes reads (A's)
from test_workbook_model import reducer, write

tk = pytest.importorskip("tkinter")

NAME = "Reducer_12to1"
PARTS = ("Gear_m1.5_N17", "Gear_m1.5_N68", "Gear_m2_N17", "OutputGear")


class DiskSolidWorks(FakeSolidWorks):
    """The fake SolidWorks, leaving a real file wherever it saves a document, and keeping each component's
    frame under the Name2 it was inserted as, so a reopened assembly reads back where the build put it."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.names = {}

    def save_as(self, path):
        kept = super().save_as(path)
        pathlib.Path(path).write_bytes(b"saved by the fake SolidWorks")
        return kept

    def add_component(self, handle, path, at):
        name = super().add_component(handle, path, at)
        self.names[handle] = name
        return name

    def place_component(self, handle, rotation, at, kind=None):
        super().place_component(handle, rotation, at, kind)
        if handle in self.names:
            self.frames[self.names[handle]] = (tuple(rotation), tuple(at))

    def saved_in(self, start):
        """The paths saved since call ``start``."""
        return [args[0] for name, args in self.calls[start:] if name == "save_as"]


class FakeCall:
    """A submitted job: answered only when the worker runs, so a test sees the window while it is in flight."""

    def __init__(self, work, sw):
        self.work, self.sw, self.answer = work, sw, None

    def run(self):
        try:
            self.answer = (self.work(self.sw), None)
        except BaseException as exc:  # noqa: BLE001 - the real worker hands every raise back the same way
            self.answer = (None, exc)

    def poll(self):
        return self.answer


class FakeWorker:
    def __init__(self, sw):
        self.sw = sw
        self.calls = []

    def submit(self, work):
        call = FakeCall(work, self.sw)
        self.calls.append(call)
        return call

    def run(self):
        for call in self.calls:
            if call.answer is None:
                call.run()


class Desk:
    """A Tk root, the strip's stand-in, a fake worker on the fake SolidWorks, and the windows opened."""

    def __init__(self, root, tmp_path):
        self.root, self.tmp = root, tmp_path
        self.folder = tmp_path / "parts"
        self.folder.mkdir()
        self.sw = DiskSolidWorks()
        self.worker = FakeWorker(self.sw)
        self.windows = []

        class App:
            out_folder = tk.StringVar(root, "")
            part_template = tk.StringVar(root, "")
            assembly_template = tk.StringVar(root, "")
            _worker = self.worker
            _pending_build = None
            recent = store.Recent()

        self.app = App()

    def spec(self, spec=None):
        spec = spec or reducer()
        return model.replace(spec, box=model.replace(spec.box, output_folder=str(self.folder)))

    def open(self, spec=None, name=f"{NAME}.xlsx", path=None):
        from gear_generator import workbook_gui
        path = path or write(self.tmp, self.spec(spec), name)
        window = workbook_gui.WorkbookWindow(self.root, self.app, str(path), poll_ms=10 ** 6)
        window.withdraw()
        self.windows.append(window)
        return window

    def finish(self, window):
        """The worker answers, and the window's poll collects it."""
        self.worker.run()
        window._tick()

    def part(self, stem, ext=".SLDPRT"):
        return str(self.folder / f"{stem}{ext}")


def unexpected_question(parent, title, text):
    """Every test that expects a question answers it itself; any other question fails the test at once, where a
    real dialog would wait for a click that never comes."""
    raise AssertionError(f"a question the test did not expect: {title}: {text}")


# The W5 findings the plans and the worker read, as the probes left them by tier 8 and P0 (W5-DECISIONS), but with
# no route to change a gear mate's ratio: a tooth change of a turning gearbox needs Build again… unless a test sets
# GEAR_MATE_RATIO_ROUTE to "remake" itself (both branches are tested below).
W5_FINDINGS = {"GEAR_MATE_RATIO_ROUTE": None, "GEAR_MATE_RATIO_REMAKE_WORKS": True, "LOCK_RETAKES_AN_OFFSET": True,
               "MATED_ASSEMBLY_REBUILD_ROUTE": "ForceRebuild3(True)",
               "MATED_BUILD_REBUILD_ROUTE": "ForceRebuild3(True)",
               "GEAR_MATE_DEFINITION_READ_MARKS": "nothing", "MATES_UNDER_COMMAND_IN_PROGRESS": True,
               "MATE_RENAME_AT_ONCE": True, "IDLER_UPDATE_HOLDS": True,
               "GEAR_MATE_SENSE_READ_BACK": "(Reverse == entities parallel) == internal",
               "GEAR_MATE_READ_BACK_TELLS_SENSE": True, "GEAR_MATE_CHECK_AND_REMAKE_HOLDS": True,
               "GEAR_MATE_SENSE_READ_MARKS": "nothing", "GEAR_MATE_SENSE_READ_POINTS_AGREE": True,
               "CROSS_VERSION_READ_BACK_TELLS_SENSE": True, "GEAR_MATE_SENSE_READ_UNDER_COMMAND_IN_PROGRESS": True,
               "GEAR_MATE_REMAKE_UNDER_COMMAND_IN_PROGRESS": True, "GEAR_MATE_READ_BACK_HOLDS_AFTER_A_RATIO_REMAKE": True}
# W6: the turned gear mate's sense as probe tier 9 found it, and the angles it covers for each class of mesh (axes that
# meet: bevel; axes that pass each other: crossed). A test of the turned refusal takes the read-back away itself.
W5_FINDINGS.update({"TURNED_GEAR_MATE_SENSE_READ_BACK": "entity senses",
                    "TURNED_GEAR_MATE_SENSE_ANGLES": (30.0, 150.0),
                    "TURNED_GEAR_MATE_SENSE_ANGLES_SKEW": (60.0, 120.0)})


@pytest.fixture(autouse=True)
def w5_findings(monkeypatch):
    for name, value in W5_FINDINGS.items():
        monkeypatch.setattr(findings, name, value, raising=False)


@pytest.fixture
def desk(tmp_path, monkeypatch):
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("no display for Tk")
    root.withdraw()
    from gear_generator import theme
    theme.setup(root)
    monkeypatch.setattr(store, "save_recent", lambda recent, path=None: True)    # never the user's own list
    from gear_generator import workbook_gui
    monkeypatch.setattr(workbook_gui, "_VERDICTS", {})          # this session's move-or-copy answers: none yet
    monkeypatch.setattr(workbook_gui, "_ASKED", set())
    monkeypatch.setattr(workbook_gui, "_UNOWNED", [])           # no job a closed window left running
    monkeypatch.setattr(workbook_gui, "ask_yes_no", unexpected_question)    # a real dialog would hang the test
    d = Desk(root, tmp_path)
    try:
        yield d
    finally:
        for window in d.windows:
            if not window._closed():
                window._pending = window._job = None
                window.close()
        root.destroy()


def touch_later(path, seconds=2):
    info = os.stat(path)
    os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns + seconds * 1_000_000_000))


def save_in_excel(window, cells, seconds=2):
    """Cells changed and saved as Excel would, then the window's poll."""
    xlsx.write_cells(window.link.path, cells)
    touch_later(window.link.path, seconds)
    window._tick()


def record_of(window):
    return store.read_link_record(window.link.path)


def record_bytes(window):
    return pathlib.Path(store.link_record_path(window.link.path)).read_bytes()


def gear_states(window):
    """The Gears table's last column, by gear: what the dot says."""
    out = {}
    for cell in window.table.grid_slaves(column=7):
        if not isinstance(cell, tk.Frame):
            continue
        row = int(cell.grid_info()["row"])
        gear = window.table.grid_slaves(row=row, column=0)[0].cget("text")
        out[gear] = [w.cget("text") for w in cell.winfo_children() if isinstance(w, tk.Label)][0]
    return out


def built(desk, spec=None):
    """A window whose workbook is built once: the four parts, the layout part and the assembly."""
    window = desk.open(spec)
    window.press_build()
    desk.finish(window)
    assert record_of(window).gearbox.assembly
    return window


def built_w4(desk, monkeypatch, spec=None):
    """A window whose workbook was built by W4: a static assembly, its record as a W4 record reads (kind static, no
    mates, no reason it is static: ``static_reason`` is only W5's static by necessity). Built here with a W5 finding
    missing (``motion.motion_reason`` says a sentence, as B keeps its W4 tests static), then the finding back and the
    reason cleared, so from then on the window plans as W5 does for a gearbox built before it."""
    real = motion.motion_reason
    monkeypatch.setattr(motion, "motion_reason", lambda: "This test builds phase W4's static assembly.")
    window = built(desk, spec)
    monkeypatch.setattr(motion, "motion_reason", real)
    record = store.open_link_record(window.link.path)
    assert record.gearbox.kind == store.GEARBOX_STATIC and record.gearbox.mates == []
    record.gearbox.static_reason = ""
    store.save_link_record(record, store.link_record_path(window.link.path))
    window.note = None
    window._plan()
    window._paint()
    return window


def name2(window, gear):
    return next(c.name for c in record_of(window).gearbox.components if c.gear == gear)


def turn_train(desk, window, degrees):
    """The user drags the 12 : 1's input in SolidWorks: each gear turns degrees·ω_i/ω_in about its own axis."""
    for gear, k in {"G1": 1.0, "G2": -0.25, "G3": -0.25, "G4": 1 / 12}.items():
        desk.sw.turn(name2(window, gear), degrees * k)


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


# -- Build ----------------------------------------------------------------------------------------------------------


def test_build_makes_the_parts_the_layout_and_the_assembly_and_records_them(desk):
    window = desk.open()
    footer = window.footer()
    assert (footer.build_action, footer.build_label, footer.build_enabled, footer.update_shown) == (
        ui_text.BUILD, "Build", True, False)
    assert window.status.get() == (f"Ready: Build makes 4 parts, {NAME}_Layout and {NAME}.SLDASM in "
                                   f"{ui_text.short_path(str(desk.folder), 48)}. Its gears are mated to their shafts "
                                   "and to each other, so they turn together in SolidWorks.")
    assert window.build_button._primary and not window.update_button.winfo_manager()
    assert gear_states(window) == {"G1": "to build", "G2": "to build", "G3": "to build", "G4": "to build"}

    window.press_build()
    # In flight: the worker's last step in the footer, every button held, the window still answering.
    assert window._pending is not None and window.status.get() == "Building in SolidWorks…"
    window._job.progress.say(swbuild.Step(swbuild.STAGE_PART, "Gear_m1.5_N68", 2, 4))
    window._tick()
    assert window.status.get() == "Building in SolidWorks: part 2 of 4, Gear_m1.5_N68…"
    assert not window.build_button._enabled and not window.export_button._enabled
    window.press_build()                                       # a second press while it runs does nothing
    assert len(desk.worker.calls) == 1

    desk.finish(window)
    assert window._pending is None
    assert window.status.get() == (f"Built 4 parts, {NAME}_Layout and {NAME}.SLDASM; no interference between the "
                                   "gears where they stand. Its gears are mated to turn together, and SolidWorks "
                                   "reports no mate in error: drag G1 in SolidWorks and the rest of its train follow. "
                                   "1 thing to do by hand: Assign a material to each of the 4 parts; the build leaves "
                                   "it unset.")
    assert [os.path.basename(p) for p in desk.sw.saved_in(0)] == [
        "Gear_m1.5_N17.SLDPRT", "Gear_m1.5_N68.SLDPRT", "Gear_m2_N17.SLDPRT", "OutputGear.SLDPRT",
        f"{NAME}_Layout.SLDPRT", f"{NAME}.SLDASM"]
    for stem in PARTS:                                         # each part's .gear.json names the workbook
        sidecar = store.read_sidecar(desk.part(stem))
        assert sidecar is not None and store.same_path(sidecar.record.workbook, window.link.path)
    raw = json.loads(record_bytes(window))
    assert raw["link_schema_version"] == store.LINK_SCHEMA_VERSION == 10
    record = record_of(window)
    assert record.gearbox.revision == 0 and store.same_path(record.gearbox.assembly, desk.part(NAME, ".SLDASM"))
    assert store.same_path(record.assembly, record.gearbox.assembly)
    assert [c.gear for c in record.gearbox.components] == ["G1", "G2", "G3", "G4"]
    assert all(c.name for c in record.gearbox.components) and record.gearbox.layout_component
    assert record.digest == window.reading.digest and len(record.parts) == 4
    assert (record.gearbox.kind, record.gearbox.drag, record.gearbox.mate_problems) == (store.GEARBOX_MOTION, ["G1"],
                                                                                        [])
    assert [m.name for m in record.gearbox.mates] == [
        "G1 on S1 Axis", "G1 along S1", "G2 on S2 Axis", "G2 along S2", "G3 locked to G2", "G4 on S3 Axis",
        "G4 along S3", "G1 meshes G2", "G3 meshes G4"]

    footer = window.footer()
    assert (footer.build_action, footer.build_label, footer.build_enabled) == (
        ui_text.BUILD_AGAIN, "Build again…", True)
    assert (footer.update_shown, footer.update_enabled, footer.update_primary) == (True, True, True)
    assert not window.build_button._primary and window.update_button._primary
    assert window.update_button.winfo_manager() and window.build_button.label.cget("text") == "Build again…"
    assert window.read_line.get().endswith(" · built from this version")
    assert set(gear_states(window).values()) == {"built"} and window.parts_readout.get() == "4 parts built"
    window.note = None                                         # the state's own sentence, once the job's has gone
    window._refresh_state()
    assert window.status.get() == ("SolidWorks already matches the workbook on record; Update SolidWorks checks it "
                                   "live and puts right anything changed there; gears turned in SolidWorks stay where "
                                   "they are unless something must move. It was built with its gears mated to turn: "
                                   "drag G1 in SolidWorks and the rest of its train follow.")


def test_a_build_the_worker_refuses_says_so_and_records_nothing(desk):
    window = desk.open()
    elsewhere = str(desk.tmp / "elsewhere" / "Gear_m1.5_N17.SLDPRT")
    desk.sw.open_docs = [DocInfo(title="Gear_m1.5_N17.SLDPRT", path=elsewhere, doc_type=1)]
    window.press_build()
    desk.finish(window)
    assert window.status.get().startswith(f"{elsewhere} is open in SolidWorks, and it has the same file name as ")
    assert window.status_label.cget("fg") == __import__("gear_generator.theme", fromlist=["x"]).ERROR
    assert desk.sw.saved_in(0) == []
    # The journal written before the job is taken out again: nothing is on record (second review N4).
    record = record_of(window)
    assert record.parts == [] and record.gearbox is None and record.pending == []
    assert window.footer().build_enabled                      # close the other document and press again


def test_without_solidworks_nothing_is_submitted(desk):
    window = desk.open()
    desk.app._worker = None
    window.press_build()
    assert window.status.get().startswith("SolidWorks cannot be reached from here, so nothing was built.")
    desk.app._worker = desk.worker
    desk.app._pending_build = object()                        # the strip is building
    window.press_build()
    assert window.status.get() == ui_text.strip_busy()
    assert desk.worker.calls == []


# -- what a failure leaves, and what the next press does ---------------------------------------------------------


def test_a_part_that_fails_mid_batch_is_recorded_and_the_next_build_carries_on(desk):
    window = desk.open()
    desk.sw.fail_on = {"save_as": (desk.part("Gear_m2_N17"), "The disk is full.")}
    window.press_build()
    desk.finish(window)
    text = window.status.get()
    assert text.startswith("2 parts built before it; ") and "Press Build to carry on: what was built is reused." in text
    record = record_of(window)
    assert [os.path.basename(p.path) for p in record.parts] == ["Gear_m1.5_N17.SLDPRT", "Gear_m1.5_N68.SLDPRT"]
    assert record.gearbox is None
    assert window.footer().build_label == "Build" and [r.stem for r in window.plan.reuse] == list(PARTS[:2])

    desk.sw.fail_on = {}
    start = len(desk.sw.calls)
    window.press_build()
    desk.finish(window)
    assert [os.path.basename(p) for p in desk.sw.saved_in(start)] == [
        "Gear_m2_N17.SLDPRT", "OutputGear.SLDPRT", f"{NAME}_Layout.SLDPRT", f"{NAME}.SLDASM"]
    assert len(record_of(window).parts) == 4                  # merged, never replaced by the second batch
    assert window.status.get().startswith(f"Built 2 parts, {NAME}_Layout and {NAME}.SLDASM, reusing the 2 parts "
                                          "already built")


def test_a_failed_assembly_leaves_a_record_the_next_build_continues_from(desk):
    window = desk.open()
    desk.sw.fail_on = {"save_as": (desk.part(NAME, ".SLDASM"), "The disk is full.")}
    window.press_build()
    desk.finish(window)
    assert ("the assembly Assem1 was left open, unsaved, since it would not save: The disk is full. Press Build to try "
            "the assembly again: the parts and layout are reused.") in window.status.get()
    record = record_of(window)
    assert record.gearbox.layout and not record.gearbox.assembly and len(record.parts) == 4
    footer = window.footer()
    assert (footer.build_label, footer.build_enabled) == ("Build", True)
    assert isinstance(window.plan.layout, LayoutReuse) and len(window.plan.reuse) == 4 and not window.plan.build

    desk.sw.fail_on = {}
    start = len(desk.sw.calls)
    window.press_build()
    desk.finish(window)
    assert [os.path.basename(p) for p in desk.sw.saved_in(start)] == [f"{NAME}.SLDASM"]
    assert window.status.get().startswith(f"Built {NAME}.SLDASM, reusing {NAME}_Layout and the 4 parts already "
                                          "built; no interference between the gears where they stand.")
    assert record_of(window).gearbox.assembly and window.footer().build_label == "Build again…"


# -- Update SolidWorks -------------------------------------------------------------------------------------------


DEMONSTRATION = {"Shafts": {"C3": 64.5, "C4": 132.5}, "Gears": {"F3": 69}}    # S3 X follows S2 by its formula
TURNS = "It was built with its gears mated to turn: drag G1 in SolidWorks and the rest of its train follow."


def test_the_demonstration_edit_is_summed_up_and_update_carries_it_unsaved(desk, monkeypatch):
    """W4's demonstration on a gearbox W4 built: static, so a tooth change is still an Update (D5)."""
    window = built_w4(desk, monkeypatch)
    before = record_of(window)
    save_in_excel(window, DEMONSTRATION)
    assert window.status.get() == ("Update SolidWorks will change G2's values (Gear_m1.5_N68), move S2 and S3 in "
                                   f"{NAME}_Layout, and re-place G2, G3 and G4. It was built static, before gears could "
                                   "be mated to turn: Build again… makes a new revision whose gears turn.")
    assert window.read_line.get().endswith(" · changed since it was built")
    assert gear_states(window)["G2"] == "changes on Update" and gear_states(window)["G1"] == "built"
    assert window.update_button._enabled and window.update_button._primary

    window.press_update()
    assert window.status.get() == "Updating SolidWorks…" and not window.update_button._enabled
    start = len(desk.sw.calls)
    desk.finish(window)
    text = window.status.get()
    save = f"Save Gear_m1.5_N68, {NAME}_Layout and {NAME} in SolidWorks to keep them."     # once, naming them
    assert text.startswith("Updated SolidWorks: changed ") and text.endswith(
        f"; no interference between the gears. {save}")
    # Build again… never waits for a save (W4 review B2): a part Update changed and that is not saved is made new
    # by the next build instead of reused.
    assert window.build_button._enabled and text.count("Save ") == 1 and "waits" not in text
    assert "Gear_m1.5_N68 (it now has 69 teeth; its file keeps its name)" in text
    assert f"moved S2 and S3 in {NAME}_Layout" in text and "re-placed G2, G3 and G4" in text
    sets = [args for name, args in desk.sw.calls[start:] if name == "set_global_variable"]
    assert ("S2 X", "64.5") in sets and ("S3 X", "132.5") in sets and ("No. of Teeth", "69") in sets
    assert desk.sw.saved_in(start) == []                       # Update SolidWorks saves nothing

    record = record_of(window)
    assert {os.path.basename(p) for p in record.unsaved} == {"Gear_m1.5_N68.SLDPRT", f"{NAME}_Layout.SLDPRT",
                                                             f"{NAME}.SLDASM"}
    assert record.digest == window.reading.digest and record.digest != before.digest
    assert [s.x for s in record.gearbox.shafts if s.shaft == "S2"] == [64.5]
    assert store.read_sidecar(desk.part("Gear_m1.5_N68")).record.spec["teeth"] == "69"
    # Built from this version is not said while the update is in SolidWorks only (W4 review S4.7).
    assert window.read_line.get().endswith(" · updated from this version, not yet saved")

    # Until those documents are saved in SolidWorks the footer asks for it; Build again… would make G2's part new.
    window.note = None
    window._refresh_state()
    assert window.status.get().endswith("have changes from Update SolidWorks that are not saved: save them in "
                                        "SolidWorks to keep them. If SolidWorks closed them without saving, press "
                                        "Update SolidWorks to make them again.")
    assert window.footer().build_enabled and window.plan.refusal == ""
    assert [(m.gear_ids, os.path.basename(m.old), os.path.basename(m.new)) for m in window.plan.unsaved_made_new] == [
        (("G2",), "Gear_m1.5_N68.SLDPRT", "Gear_m1.5_N69.SLDPRT")]
    for path in record.unsaved:
        touch_later(path)                                      # saved in SolidWorks
    window._tick()
    assert "not saved" not in window.status.get() and "waits" not in window.status.get()
    assert window.read_line.get().endswith(" · built from this version")
    assert window.footer().build_enabled and window.plan.unsaved_made_new == ()
    assert "Gear_m1.5_N68" in [r.stem for r in window.plan.reuse]


def test_an_update_that_stops_part_way_records_what_it_changed_and_the_next_press_finishes(desk, monkeypatch):
    window = built_w4(desk, monkeypatch)
    save_in_excel(window, DEMONSTRATION)
    desk.sw.fail_on = {"set_global_variable": ("S2 X", "The equation would not take.")}
    window.press_update()
    desk.finish(window)
    text = window.status.get()
    assert text.startswith("Update SolidWorks stopped. ") and "It had already changed Gear_m1.5_N68" in text
    record = record_of(window)
    unsaved = {os.path.basename(p) for p in record.unsaved}
    assert "Gear_m1.5_N68.SLDPRT" in unsaved and f"{NAME}.SLDASM" not in unsaved     # the gears were not moved
    # What is left is still offered: the part's values are on record now, the moves are not.
    window.note = None
    window._refresh_state()
    assert window.status.get().startswith(f"Update SolidWorks will move S2 and S3 in {NAME}_Layout, and re-place "
                                          "G2, G3 and G4.")

    desk.sw.fail_on = {}
    start = len(desk.sw.calls)
    window.press_update()
    desk.finish(window)
    sets = [args[0] for name, args in desk.sw.calls[start:] if name == "set_global_variable"]
    assert "No. of Teeth" not in sets and "S2 X" in sets       # compared live: the part already holds 69
    assert record_of(window).digest == window.reading.digest


def test_a_structural_edit_asks_and_no_changes_nothing(desk, monkeypatch):
    from gear_generator import workbook_gui
    window = built(desk)
    save_in_excel(window, {"Gears": {"K2": "arcs"}})           # G1's flank: a new recipe, a new part
    assert window.status.get().endswith(f"Update SolidWorks offers to build again as {NAME}_r2. {TURNS}")
    assert gear_states(window)["G1"] == "needs a new part" and gear_states(window)["G2"] == "built"
    asked = []
    monkeypatch.setattr(workbook_gui, "ask_yes_no", lambda parent, title, text: asked.append((title, text)) or False)
    on_record, calls = record_bytes(window), len(desk.worker.calls)
    window.press_update()
    (title, question), = asked
    assert title == "Build again?" and f"Build again as {NAME}_r2?" in question
    assert "reuses 3 parts that have not changed" in question and f"{NAME}.SLDASM stays as it is on disk" in question
    # After No the reason stays on screen, joined plainly (W4 review nit: it read the answer alone).
    assert window.status.get() == (f"{ui_text.NOTHING_CHANGED} Gear_m1.5_N17 (G1): Flank changed from involute to "
                                   "arcs, which its values cannot carry, so it needs a new part. Update SolidWorks "
                                   f"offers to build again as {NAME}_r2. {TURNS}")
    assert len(desk.worker.calls) == calls and record_bytes(window) == on_record
    window.press_build()                                       # Build again… asks the same question
    assert len(asked) == 2 and asked[1] == asked[0] and len(desk.worker.calls) == calls


def test_a_structural_edit_answered_yes_builds_the_next_revision_beside_the_first(desk, monkeypatch):
    from gear_generator import workbook_gui
    window = built(desk)
    first = {p: sha(p) for p in desk.sw.saved_in(0)}
    times = {p: os.stat(p).st_mtime_ns for p in first}
    save_in_excel(window, {"Gears": {"K2": "arcs"}})
    monkeypatch.setattr(workbook_gui, "ask_yes_no", lambda parent, title, text: True)
    start = len(desk.sw.calls)
    window.press_update()
    desk.finish(window)
    made = [os.path.basename(p) for p in desk.sw.saved_in(start)]
    assert made[1:] == [f"{NAME}_r2_Layout.SLDPRT", f"{NAME}_r2.SLDASM"] and made[0].endswith("_r2.SLDPRT")
    assert window.status.get().startswith(f"Built 1 part, {NAME}_r2_Layout and {NAME}_r2.SLDASM, reusing the 3 "
                                          "parts already built")
    record = record_of(window)
    assert (record.gearbox.revision, record.gearbox.name) == (2, f"{NAME}_r2")
    (earlier,) = record.earlier
    assert earlier.revision == 0 and store.same_path(earlier.assembly, desk.part(NAME, ".SLDASM"))
    assert [os.path.basename(p) for p in earlier.parts] == ["Gear_m1.5_N17.SLDPRT"]
    assert {os.path.basename(c.part) for c in record.gearbox.components} == {
        made[0], "Gear_m1.5_N68.SLDPRT", "Gear_m2_N17.SLDPRT", "OutputGear.SLDPRT"}
    assert {p: sha(p) for p in first} == first and {p: os.stat(p).st_mtime_ns for p in first} == times
    assert window.footer().build_label == "Build again…" and window.update_plan.record_matches


def test_a_question_left_open_while_the_workbook_changes_builds_nothing(desk, monkeypatch):
    from gear_generator import workbook_gui
    window = built(desk)
    save_in_excel(window, {"Gears": {"K2": "arcs"}})

    def saved_meanwhile(parent, title, text):
        save_in_excel(window, {"Gears": {"K3": "arcs"}}, seconds=4)
        return True

    monkeypatch.setattr(workbook_gui, "ask_yes_no", saved_meanwhile)
    calls = len(desk.worker.calls)
    window.press_update()
    # The answer, then the state it answered, which still stands (the question's own "build again" said once).
    assert window.status.get().startswith(ui_text.ASKED_TOO_LATE + " Gear_m1.5_N17 (G1): ")
    assert len(desk.worker.calls) == calls


# -- the record --------------------------------------------------------------------------------------------------


def test_a_newer_record_holds_build_and_update_and_is_left_byte_identical(desk):
    path = write(desk.tmp, desk.spec())
    target = pathlib.Path(store.link_record_path(str(path)))
    target.write_bytes(json.dumps({"link_schema_version": store.LINK_SCHEMA_VERSION + 1, "schema_version": 1,
                                   "workbook": str(path)}).encode())
    before = target.read_bytes()
    window = desk.open(path=path)
    footer = window.footer()
    assert window.status.get().endswith(store.LINK_WAITS) and not footer.ok
    assert not footer.build_enabled and not footer.update_shown
    window.press_build()
    window.press_update()
    assert desk.worker.calls == [] and target.read_bytes() == before


def test_a_record_that_turns_newer_during_a_build_is_left_alone_and_said(desk):
    window = desk.open()
    window.press_build()
    target = pathlib.Path(store.link_record_path(window.link.path))
    target.write_bytes(json.dumps({"link_schema_version": store.LINK_SCHEMA_VERSION + 1,
                                   "workbook": window.link.path}).encode())
    before = target.read_bytes()
    desk.finish(window)
    assert target.read_bytes() == before and window.status.get().endswith(store.LINK_WAITS)
    assert store.read_sidecar(desk.part("Gear_m1.5_N17")) is not None     # the parts' own records are written


def test_a_broken_record_is_set_aside_on_the_next_write(desk):
    path = write(desk.tmp, desk.spec())
    target = pathlib.Path(store.link_record_path(str(path)))
    target.write_text("not json")
    window = desk.open(path=path)
    assert "The next Build sets it aside and starts a new one." in window.status.get()
    assert window.footer().build_enabled and target.read_text() == "not json"     # planning never moves it
    window.press_build()
    desk.finish(window)
    aside = [p for p in desk.tmp.iterdir() if p.name.startswith(target.name + ".bad-")]
    assert len(aside) == 1 and aside[0].read_text() == "not json"
    assert record_of(window).gearbox.assembly
    assert f"so it was moved to {aside[0].name} and a new one is started." in window.status.get()


def test_locate_carries_the_record_to_the_workbooks_new_place(desk, monkeypatch):
    from gear_generator import workbook_gui
    window = built(desk)
    old_record = record_bytes(window)
    moved = desk.tmp / "Moved.xlsx"
    os.replace(window.link.path, moved)
    monkeypatch.setattr(workbook_gui.filedialog, "askopenfilename", lambda **kwargs: str(moved))
    window.locate()
    carried = store.read_link_record(str(moved))
    assert carried is not None and store.same_path(carried.workbook, str(moved))
    assert carried.gearbox.assembly and pathlib.Path(store.link_record_path(str(desk.tmp / f"{NAME}.xlsx"))
                                                     ).read_bytes() == old_record
    assert window.footer().build_label == "Build again…" and window.read_line.get().endswith(
        " · built from this version")


# -- Build parts, and the states that hold everything -------------------------------------------------------------


def with_later_row():
    """The reducer and a dog ring on S3: a later phase's row while ``a_later_kind`` makes the dog ring one. After W8
    no real kind waits for a later phase; the channel, and Build parts with it, are what these tests keep showing."""
    spec = reducer()
    return model.replace(spec, gears=spec.gears + (Gear("G7", "S3", "60", "dog", "external", "30", "1.5", "", "6",
                                                        ""),))


def test_build_parts_falls_back_while_a_later_row_holds_the_layout_back(desk, a_later_kind):
    window = desk.open(with_later_row())
    footer = window.footer()
    assert (footer.build_action, footer.build_label, footer.build_primary) == (ui_text.BUILD_PARTS, "Build parts",
                                                                               True)
    assert window.status.get().startswith("Ready: Build parts makes 4 parts in ") and window.status.get().endswith(
        "; the layout and assembly are not built: Gears!A6: G7 is a dog ring: dog rings are built in phase W99.")
    desk.sw.fail_on = {"save_as": (desk.part("OutputGear"), "The disk is full.")}
    window.press_build()
    desk.finish(window)
    assert len(record_of(window).parts) == 3 and record_of(window).gearbox is None
    desk.sw.fail_on = {}
    start = len(desk.sw.calls)
    window.press_build()
    desk.finish(window)
    assert [os.path.basename(p) for p in desk.sw.saved_in(start)] == ["OutputGear.SLDPRT"]   # the rest reused
    record = record_of(window)
    assert len(record.parts) == 4 and record.gearbox is None                 # merged; no layout, no assembly
    assert window.read_line.get().endswith(" · parts built from this version")
    footer = window.footer()
    assert footer.build_label == "Build parts" and not footer.build_enabled and footer.update_shown
    assert not footer.update_primary


def test_a_chosen_fix_and_a_provisional_read_hold_both_buttons(desk):
    window = built(desk)
    save_in_excel(window, {"Shafts": {"C3": 64, "C4": 132}})              # G1–G2 0.25 mm off its centres
    assert not window.footer().build_enabled and not window.footer().update_enabled
    window.choose(window.report.fixes["Meshes!A2"][0])
    footer = window.footer()
    assert footer.text.startswith("1 fix chosen: Export writes it into the workbook, and Build and Update "
                                  "SolidWorks wait for that")
    assert not footer.build_enabled and not footer.update_enabled and footer.update_shown
    window.press_build()
    window.press_update()
    window.unchoose(window.chosen[0])
    save_in_excel(window, {"Shafts": {"C3": 63.75, "C4": 131.75}}, seconds=4)
    assert window.footer().update_enabled
    window.recalc = True                                                      # an Export Excel has yet to save
    window._plan()
    window._paint()
    footer = window.footer()
    assert footer.text == ui_text.RECALC_WAIT_UPDATE and not footer.build_enabled and not footer.update_enabled
    window.press_build()
    window.press_update()
    assert len(desk.worker.calls) == 1                                        # only the first build


# -- closing while a job runs -------------------------------------------------------------------------------------


def test_closing_mid_build_records_what_it_saved_then_closes(desk):
    window = desk.open()
    window.press_build()
    window.close()
    assert not window._closed() and window.status.get().endswith(ui_text.closes_when_done())
    desk.worker.run()
    window._tick()
    assert window._closed()
    assert store.read_link_record(str(desk.tmp / f"{NAME}.xlsx")).gearbox.assembly


def test_closing_mid_build_that_fails_stays_open_to_say_why(desk):
    window = desk.open()
    desk.sw.fail_on = {"save_as": (desk.part(NAME, ".SLDASM"), "The disk is full.")}
    window.press_build()
    window.close()
    desk.finish(window)
    assert not window._closed() and "The disk is full." in window.status.get()
    assert record_of(window).gearbox.layout


def test_a_clash_beside_a_mesh_is_said_where_they_meet_and_stands_out(desk):
    window = desk.open()
    desk.sw.clashes = [(("gear1-1", "gear4-1"), 2.0)]           # G1 and G4: on different shafts, not a mesh
    window.press_build()
    desk.finish(window)
    assert f"Check: G1 and G4 interfere, 2 mm³; look where they meet in {NAME}.SLDASM." in window.status.get()
    assert window.status_label.cget("fg") == __import__("gear_generator.theme", fromlist=["x"]).ERROR


# -- the window keeps its width whatever the footer holds ------------------------------------------------------


LONG = ("Updated SolidWorks: changed 1 variable in Gear_m1.5_N68 (it now has 69 teeth; its file keeps its name), "
        "moved S2 and S3 in Reducer_12to1_Layout, re-placed G2, G3 and G4. Check: G1 and G4 interfere, 2 mm³; "
        "G2 and G3 interfere, 0.5 mm³; look where they meet in Reducer_12to1.SLDASM. Save in SolidWorks to keep it.")


# W9a (the coordinator's ruling 4 on package B's review): the Build again? question's clause on the user's work when
# the record holds no inventory of the assembly it leaves behind (ui_text.stays_behind_sentence); W9d (W9D-INTERFACES
# §9.1): led, while CARRY_INSERTS is unset, by that finding on the SolidWorks the record last saw (the fake's 2026, or
# not known on a record no job of this app wrote).
def timeless(year="2026"):
    on = (f"SolidWorks {year} (findings.CARRY_INSERTS_ON_{year})" if year != "?"
          else "the SolidWorks it runs on (findings.CARRY_INSERTS_ON_<year>)")
    return (f"Gear Generator has not yet been shown to carry your work into a new revision on {on}, so anything you "
            f"added to {NAME}.SLDASM in SolidWorks (components, mates, and features in parts this revision makes new) "
            f"stays there, and {NAME}_r2 has none of it.")


TIMELESS = timeless()


def width_and_height(window):
    """The size :meth:`WorkbookWindow._fit` gives the window (a withdrawn window does not report one back)."""
    asked = []
    real = window.geometry
    window.geometry = lambda spec=None: asked.append(spec) if spec else real()
    try:
        window._fit()
    finally:
        del window.geometry
    w, h = (int(v) for v in asked[-1].split("+")[0].split("x"))
    return w, h


def test_the_window_keeps_its_width_with_update_shown_and_a_long_sentence(desk):
    from gear_generator import workbook_gui
    from gear_generator.theme import px
    fresh = desk.open(name="Fresh.xlsx")
    fresh.note = (LONG, False)
    fresh._refresh_state()
    assert not fresh.update_button.winfo_manager()
    fresh_size = width_and_height(fresh)

    window = built(desk)                                       # Export, Export as…, Build again…, Update SolidWorks
    window.note = ("Built.", True)
    window._refresh_state()
    short_height = width_and_height(window)[1]
    window.note = (LONG, False)
    window._refresh_state()
    assert window.update_button.winfo_manager() and window.build_button.label.cget("text") == "Build again…"
    size = width_and_height(window)

    assert fresh_size[0] == size[0] == px(workbook_gui.WINDOW_WIDTH)
    assert window.winfo_reqwidth() <= px(workbook_gui.WINDOW_WIDTH)
    # With less room beside the buttons the sentence wraps sooner, and the window grows taller to hold it all — up
    # to the screen's work area less its frame (K12, ISSUE-1-PLAN §2.6: rewritten from "height == reqheight").
    assert int(str(window.status_label.cget("wraplength"))) < int(str(fresh.status_label.cget("wraplength")))
    lines = window.status_label.winfo_reqheight() // window.fonts.label.metrics("linespace")
    assert lines >= 3                                          # the long update-and-clash sentence, wrapped
    cap = workbook_gui.work_area(window)[2] - px(workbook_gui.FRAME)
    assert size[1] == min(window.winfo_reqheight(), cap) and size[1] > short_height


def _short_screen(monkeypatch, height):
    """A primary screen whose work area is ``height`` px tall (K12's test forces one)."""
    from gear_generator import workbook_gui
    monkeypatch.setattr(workbook_gui, "work_area", lambda widget: (0, 0, height))


def _shown(window, width, height):
    """The window mapped at the size ``_fit`` gave it, as a user sees it. Tk on Windows keeps a withdrawn toplevel at
    its requested size whatever geometry it is given, until it is mapped (Linux applies it at once), so the geometry
    of a short screen is measured on the window shown, then withdrawn again."""
    window.geometry(f"{width}x{height}+0+0")
    window.deiconify()
    window.update()


def _box_whole(window):
    """The footer's sentence as the user sees it: the box that shows it as tall and as wide as the sentence asks,
    and no bar (package B's review, point 2: the label is always drawn whole inside its box, so it shows nothing)."""
    box, label = window._status_box, window.status_label
    return ((box.winfo_height(), box.winfo_width()) == (label.winfo_reqheight(), label.winfo_reqwidth())
            and not window._status_bar.winfo_manager())


def test_on_a_short_screen_the_window_stops_at_the_work_area_the_footer_whole_and_the_body_scrolls(desk, mode_findings,
                                                                                                   monkeypatch):
    """K12 (ISSUE-1-PLAN §2.6): the built E4 transfer case on a screen whose work area is shorter than the window
    asks (as on a 2560 × 1600 screen at 150 %, where W8's window check found the footer cut): the window stops at the
    work area less its frame, inside it; the header and footer stay whole, with every button and the sentence's box
    as tall as the sentence; the two columns scroll as one page between them, its scroll bar in the lane the body's
    right padding keeps, so the columns keep their width; and the page's last line can be scrolled into view, by its
    bar and by the wheel, which acts only for this window."""
    from gear_generator import workbook_gui
    from gear_generator.theme import px
    from workbook_fixtures import e4_transfer_case
    window = desk.open(e4_transfer_case(), name="TransferCase_E4.xlsx")
    window.press_build()
    desk.finish(window)
    status = window.status.get()
    assert status.startswith("Built 6 parts") and status.endswith("the build leaves it unset.")
    tall = window.winfo_reqheight()
    area = tall - px(200)                                       # a work area 200 px shorter than the window asks
    _short_screen(monkeypatch, area)
    width, height = width_and_height(window)
    cap = area - px(workbook_gui.FRAME)
    assert height <= cap and width == px(workbook_gui.WINDOW_WIDTH) and window.winfo_reqheight() <= cap
    _shown(window, width, height)
    try:
        assert window.winfo_height() == height
        outer = window._foot.master
        foot_bottom = outer.winfo_y() + window._foot.winfo_y() + window._foot.winfo_height()
        assert window._foot.winfo_height() == window._foot.winfo_reqheight() and foot_bottom <= height
        assert _box_whole(window)                                # the sentence whole, in its box
        for button in (window.export_button, window.export_as_button, window.build_button, window.update_button):
            assert button.winfo_height() == button.winfo_reqheight()
        page, body = window._page, window._body
        assert page.winfo_height() < body.winfo_reqheight() and window._page_bar.winfo_ismapped()
        assert page.winfo_height() >= px(workbook_gui.BODY_LEAST)
        lane = window._page_bar.master
        assert lane.winfo_width() == px(workbook_gui.SCROLL_LANE)    # the bar never widens the window or narrows
        page.yview_moveto(1.0)
        window.update_idletasks()
        assert page.canvasy(page.winfo_height()) >= body.winfo_reqheight() - 1        # the last line reachable
        page.yview_moveto(0.0)

        class Wheel:
            x_root, y_root, delta, num = page.winfo_rootx() + 20, page.winfo_rooty() + 20, -120, 5
        other = tk.Toplevel(desk.root)                          # another window under the pointer: not this one's
        try:
            monkeypatch.setattr(window, "winfo_containing", lambda x, y: other)
            window._on_wheel(Wheel())
            monkeypatch.setattr(window, "winfo_containing", lambda x, y: None)
            window._on_wheel(Wheel())
            assert page.yview()[0] == 0.0
        finally:
            other.destroy()
        monkeypatch.setattr(window, "winfo_containing", lambda x, y: body)
        window._on_wheel(Wheel())
        assert page.yview()[0] > 0
    finally:
        window.withdraw()


def test_the_strips_wheel_never_scrolls_its_page_from_a_workbook_window(desk, monkeypatch):
    """§2.6 item 5: the strip's wheel handler acts only for the strip's own toplevel."""
    from gear_generator import gui
    app = gui.GearApp(desk.root)
    window = desk.open()
    scrolled = []
    monkeypatch.setattr(app._page_bar, "winfo_ismapped", lambda: True)
    monkeypatch.setattr(app._page, "yview_scroll", lambda *a: scrolled.append(a))

    class Wheel:
        x_root, y_root, delta = 10, 10, -120
    monkeypatch.setattr(app, "winfo_containing", lambda x, y: window._body)
    app._on_wheel(Wheel())
    assert scrolled == []
    monkeypatch.setattr(app, "winfo_containing", lambda x, y: app._page)
    app._on_wheel(Wheel())
    assert scrolled == [(1, "units")]


def test_a_footer_above_its_ceiling_scrolls_its_sentence_and_keeps_its_buttons_whole(desk, monkeypatch):
    """K12: the footer takes at most a third of the work area; a longer sentence scrolls in a box of its own, at the
    ceiling, with its bar beside it, and wraps in the room the bar leaves; the buttons stay whole. Under the ceiling
    it is shown whole, with no bar."""
    from gear_generator import workbook_gui
    from gear_generator.theme import px
    window = built(desk)
    _short_screen(monkeypatch, px(600))
    window.note = (" ".join([LONG] * 6), False)
    window._refresh_state()
    width, height = width_and_height(window)
    _shown(window, width, height)
    try:
        ceiling = px(600) // workbook_gui.FOOTER_SHARE
        assert window._status_scrolls and window._status_bar.winfo_ismapped()
        assert window._status_box.winfo_height() == ceiling < window.status_label.winfo_reqheight()
        assert width == px(workbook_gui.WINDOW_WIDTH) and window.winfo_reqwidth() <= px(workbook_gui.WINDOW_WIDTH)
        for button in (window.export_button, window.export_as_button, window.build_button, window.update_button):
            assert button.winfo_height() == button.winfo_reqheight()
        window.note = ("Built.", True)
        window._refresh_state()
        window.update()
        assert not window._status_scrolls and _box_whole(window)
    finally:
        window.withdraw()


def test_a_sentence_set_alone_after_a_short_one_is_shown_whole(desk, monkeypatch):
    """Package B's review, point 1: every sentence the window sets outside its refresh — SolidWorks unreachable, the
    strip busy, a job left running, a poll that failed, an Export refused, a workbook that would not open — is shown
    in a box as big as it asks, not the box the short sentence before it left."""
    from gear_generator import workbook_gui
    window = built(desk)
    sentences = [ui_text.job_unreachable("SolidWorks is not running on this computer.", True),
                 ui_text.strip_busy(True), ui_text.unowned_job_busy(True),
                 ui_text.collect_failed(RuntimeError("the poll failed"), True),
                 "Nothing was exported: the workbook's formulas still hold Excel's old values; open and save it in "
                 "Excel first, so what is exported is worked out from what they now give.",
                 "The workbook could not be opened: " + "it is not a workbook this version reads. " * 3]
    width, height = width_and_height(window)
    _shown(window, width, height)
    try:
        for sentence in sentences:
            window.note = ("Built.", True)
            window._refresh_state()
            window.update()
            short = window._status_box.winfo_height()
            window._set_status(sentence, ok=False)
            window.update()
            assert window.status.get() == sentence and _box_whole(window), sentence
            assert window._status_box.winfo_width() > workbook_gui.px(60) and window._status_box.winfo_height() >= short
    finally:
        window.withdraw()


# -- notes that answer rather than report a job join the state plainly ---------------------------------------------


def test_a_fix_set_aside_by_a_save_is_joined_plainly_to_what_the_save_left(desk):
    window = desk.open()
    save_in_excel(window, {"Shafts": {"C3": 64, "C4": 132}})
    window.choose(window.report.fixes["Meshes!A2"][0])
    save_in_excel(window, {"Shafts": {"C3": 64.5, "C4": 132.5}}, seconds=4)   # the move chosen no longer fits
    assert window.chosen == [] and window.note.kind == ui_text.NOTE_STANDING
    text = window.status.get()
    assert text.startswith(ui_text.FIX_SET_ASIDE + " Fix the workbook before building: Meshes!A2:")
    assert "Since then" not in text


def test_a_record_locate_could_not_carry_is_joined_plainly_to_the_state(desk, monkeypatch):
    from gear_generator import workbook_gui
    window = desk.open()
    old_record = pathlib.Path(store.link_record_path(window.link.path))
    old_record.write_text(json.dumps({"link_schema_version": store.LINK_SCHEMA_VERSION + 1,
                                      "workbook": window.link.path}))
    moved = desk.tmp / "Moved.xlsx"
    os.replace(window.link.path, moved)
    desk.folder.rmdir()                                        # and the output folder is gone too
    monkeypatch.setattr(workbook_gui.filedialog, "askopenfilename", lambda **kwargs: str(moved))
    window.locate()
    text = window.status.get()
    assert window.note.kind == ui_text.NOTE_STANDING and "Since then" not in text
    assert text.startswith("The record of what was built stays beside the workbook's old place: The record of what "
                           "was built, Reducer_12to1.workbook.json, cannot be read: it was written by a newer Gear "
                           "Generator")
    assert text.endswith("does not exist; make it, or change it on the Box sheet.")
    assert not os.path.exists(store.link_record_path(str(moved)))


# -- W4 review S1: a copied workbook ---------------------------------------------------------------------------


def test_a_copied_workbook_builds_its_own_gearbox_and_leaves_the_originals_record_alone(desk):
    import shutil
    window = built(desk)
    original = window.link.path
    before = record_bytes(window)
    folder = desk.tmp / "copy"
    folder.mkdir()
    copy_path = folder / f"{NAME}.xlsx"
    shutil.copy2(original, copy_path)
    shutil.copy2(store.link_record_path(original), store.link_record_path(str(copy_path)))
    copy = desk.open(path=copy_path)
    assert copy.record is None and copy.update_plan is None and copy.plan.foreign_record == original
    footer = copy.footer()
    assert footer.build_label == "Build" and footer.build_enabled and not footer.update_shown and footer.ok
    # Said once, in green: Build goes ahead with a gearbox of its own; no part-by-part "built from …" sentences.
    assert copy.status.get() == (
        f"Ready: Build makes 4 parts, {NAME}_r2_Layout and {NAME}_r2.SLDASM in "
        f"{ui_text.short_path(str(desk.folder), 48)}. Its gears are mated to their shafts and to each other, so they "
        "turn together in SolidWorks. This workbook is a copy of "
        f"{ui_text.short_path(original, 48)}, which is still there, so the record that came with it is that "
        "workbook's, and so are the SolidWorks files it lists: Build makes this workbook's own gearbox beside them, "
        "sharing and overwriting nothing.")
    assert "built" not in copy.read_line.get()                 # nothing is said to be built from the copy
    copy.press_build()
    desk.finish(copy)
    record = record_of(copy)
    assert store.same_path(record.workbook, str(copy_path)) and record.gearbox.revision == 2
    assert record.earlier == [] and all("_r2" in os.path.basename(p.path) for p in record.parts)
    assert record_bytes(window) == before                     # the original's record, byte for byte


# -- W4 review, pass 2 ---------------------------------------------------------------------------------------------


def test_closing_the_strips_window_mid_job_waits_for_the_record_then_closes(desk):
    """W4 review B1, the window's half: the strip's root had no WM_DELETE_WINDOW handler and the worker is a
    daemon thread, so closing it mid-job ended the process before the finish wrote anything."""
    from gear_generator import gui
    said, quit = [], []
    guard = gui.CloseGuard(desk.root, lambda text, ok=True: said.append((text, ok)), poll_ms=10 ** 6,
                           quit=lambda: quit.append(True))
    idle = desk.open(name="Idle.xlsx")
    window = desk.open()
    window.press_build()
    guard.request()
    assert quit == [] and said == [(ui_text.app_closes_when_done(1), True)]
    assert not window._closed() and window.status.get().endswith(ui_text.closes_when_done())
    guard.check()                                              # still running: it waits
    assert quit == [] and not window._closed()
    desk.worker.run()
    window._tick()                                             # collected, written, closed
    assert window._closed() and record_of_path(desk.tmp / f"{NAME}.xlsx").gearbox.assembly
    guard.check()
    assert quit == [True] and not idle._closed()               # the root goes, and every window with it


def record_of_path(path):
    return store.read_link_record(str(path))


def record_bytes_of(path):
    return pathlib.Path(store.link_record_path(str(path))).read_bytes()


def test_closing_the_strips_window_stays_open_when_the_job_has_something_to_say(desk):
    from gear_generator import gui
    said, quit = [], []
    guard = gui.CloseGuard(desk.root, lambda text, ok=True: said.append((text, ok)), poll_ms=10 ** 6,
                           quit=lambda: quit.append(True))
    window = desk.open()
    desk.sw.fail_on = {"save_as": (desk.part(NAME, ".SLDASM"), "The disk is full.")}
    window.press_build()
    guard.request()
    desk.finish(window)
    guard.check()
    assert quit == [] and said[-1] == (ui_text.APP_STAYED_OPEN, False)
    assert not window._closed() and "The disk is full." in window.status.get()
    assert record_of(window).gearbox.layout                   # what it saved is on record
    guard.request()                                            # closed again: nothing pending, so it quits
    assert quit == [True]


def test_closing_the_strips_window_with_nothing_running_closes_at_once(desk):
    from gear_generator import gui
    quit = []
    desk.open()
    gui.CloseGuard(desk.root, lambda text, ok=True: None, quit=lambda: quit.append(True)).request()
    assert quit == [True]


def test_a_sidecar_that_cannot_be_written_never_stops_the_record_nor_the_reverse(desk, monkeypatch):
    window = desk.open()
    real = store.save

    def refuse_one(path, sidecar):
        if os.path.basename(path).startswith("Gear_m1.5_N68"):
            raise PermissionError("denied")
        return real(path, sidecar)

    monkeypatch.setattr(store, "save", refuse_one)
    window.press_build()
    desk.finish(window)
    text = window.status.get()
    assert "Gear_m1.5_N68.gear.json could not be written beside it: denied." in text
    assert record_of(window).gearbox.assembly and store.read_sidecar(desk.part("Gear_m1.5_N17")) is not None
    monkeypatch.setattr(store, "save", real)

    other = desk.open(name="Other.xlsx", spec=desk.spec(model.replace(
        reducer(), box=model.replace(reducer().box, name="Other"))))

    def no_record(record, path=None):
        raise RuntimeError("the disk went away")

    monkeypatch.setattr(store, "save_link_record", no_record)
    other.press_build()
    desk.finish(other)
    assert "Other.workbook.json, could not be written: the disk went away." in other.status.get()
    assert store.same_path(store.read_sidecar(desk.part("Gear_m1.5_N17_r2")).record.workbook, other.link.path)
    assert other._pending is None and not os.path.exists(store.link_record_path(other.link.path))


def test_a_finish_that_raises_still_answers_and_frees_the_window(desk, monkeypatch):
    from gear_generator.workbook import gearbox as wb_gearbox
    window = desk.open()

    def broken(*args, **kwargs):
        raise KeyError("parts")

    monkeypatch.setattr(wb_gearbox, "finish_build", broken)
    window.press_build()
    desk.finish(window)
    assert window._pending is None and window._job is None
    assert "What the build saved could not all be put on record — KeyError: 'parts'." in window.status.get()
    assert window.status.get().startswith(f"Built 4 parts, {NAME}_Layout and {NAME}.SLDASM")
    # Nothing of the finish was written, but the journal written before the build was (second review N4.2): the
    # next Build reuses what SolidWorks saved, once checked, rather than go beside it.
    assert window.status.get().endswith("the next Build finds it from the journal written before the build, checks "
                                        "it in SolidWorks and reuses what it can.")
    assert [r.stem for r in window.plan.reuse] == list(PARTS) and not isinstance(window.plan.layout, LayoutReuse)
    assert window.plan.revision == 2 and window.plan.build == ()


def test_an_update_lost_with_solidworks_and_its_file_saved_unchanged_is_made_new_by_the_next_press(desk, monkeypatch):
    """Review B2's last corner, through the window, on a gearbox W4 built (where a tooth change is an Update): Update set N68 to 69 teeth; SolidWorks was closed without saving,
    and later the unchanged 68-tooth file was opened and saved, so its time moved on and the unsaved mark cleared
    while the record still says 69. Build again… then failed the live check on every press; now the first press
    says what it found and records it, and the next makes G2's part new."""
    from gear_generator import workbook_gui
    from test_swbuild import _key
    monkeypatch.setattr(workbook_gui, "ask_yes_no", lambda parent, title, text: True)
    window = built_w4(desk, monkeypatch)
    n68 = desk.part("Gear_m1.5_N68")
    as_built = tuple(list(held) for held in desk.sw.saved[_key(n68)])
    save_in_excel(window, DEMONSTRATION)
    window.press_update()
    desk.finish(window)
    assert store.same_path(next(iter(p for p in record_of(window).unsaved if p.endswith("N68.SLDPRT"))), n68)

    desk.sw.close_all()                                        # SolidWorks closed without saving ...
    assert desk.sw.saved[_key(n68)] == as_built
    for path in record_of(window).unsaved:
        touch_later(path)                                      # ... and the files saved later, unchanged
    save_in_excel(window, {"Gears": {"J2": ""}}, seconds=4)    # G1's bore cleared: a new revision
    assert n68 in [r.path for r in window.plan.reuse]

    start = len(desk.sw.calls)
    window.press_build()
    desk.finish(window)
    text = window.status.get()
    assert text == ('Nothing was built. Gear_m1.5_N68.SLDPRT does not hold what the workbook asks of it, so it cannot '
                    'be reused: "No. of Teeth" is 68 there and 69 here. The next press of Build again… makes G2\'s '
                    "part new rather than reuse Gear_m1.5_N68; nothing is overwritten.")
    assert desk.sw.saved_in(start) == []
    assert list(record_of(window).mismatched) and store.same_path(list(record_of(window).mismatched)[0], n68)
    assert [(m.why, os.path.basename(m.new)) for m in window.plan.made_new if m.old == n68] == [
        ("mismatched", "Gear_m1.5_N69.SLDPRT")]
    assert window.footer().build_enabled

    start = len(desk.sw.calls)
    window.press_build()
    desk.finish(window)
    made = [os.path.basename(p) for p in desk.sw.saved_in(start)]
    assert "Gear_m1.5_N69.SLDPRT" in made and f"{NAME}_r2.SLDASM" in made
    assert record_of(window).gearbox.revision == 2 and window.status.get().startswith("Built 2 parts")


def test_a_component_deleted_in_solidworks_says_the_way_on(desk):
    """W4 review S4.6: find_component's refusal was shown verbatim, with no pointer to Build again…."""
    window = built(desk)
    g2 = next(c.name for c in record_of(window).gearbox.components if c.gear == "G2")
    desk.sw.missing_components = {g2}
    window.press_update()
    desk.finish(window)
    assert window.status.get() == (
        f"{g2} is not in {NAME}.SLDASM any more: it was renamed or deleted in SolidWorks. Update SolidWorks cannot put "
        "that back; Build again… builds the next revision beside it, with an assembly of its own, and leaves this "
        "one as it is.")
    assert window.footer().build_enabled


def test_a_global_deleted_from_a_part_marks_it_so_build_again_makes_it_new(desk):
    from test_swbuild import _key
    window = built(desk)
    n68 = desk.part("Gear_m1.5_N68")
    equations, made = desk.sw.memory[_key(n68)]                # open in SolidWorks since the build
    desk.sw.memory[_key(n68)] = ([e for e in equations if not e.startswith('"No. of Teeth"')], made)
    window.press_update()
    desk.finish(window)
    assert "Update SolidWorks cannot put that back; Build again… builds the next revision" in window.status.get()
    assert store.same_path(list(record_of(window).mismatched)[0], n68)
    assert [m.why for m in window.plan.made_new if store.same_path(m.old, n68)] == ["mismatched"]


def test_a_part_file_that_appears_while_the_question_is_open_builds_nothing(desk, monkeypatch):
    """W4 review nit: _build_again compared only the digest and the name, so a file appearing meanwhile changed
    what was built from what the question described."""
    from gear_generator import workbook_gui
    window = built(desk)
    save_in_excel(window, {"Gears": {"K2": "arcs"}})
    new_part = window.plan.build[0].path

    def a_file_meanwhile(parent, title, text):
        pathlib.Path(new_part).write_bytes(b"made by someone else")
        return True

    monkeypatch.setattr(workbook_gui, "ask_yes_no", a_file_meanwhile)
    calls = len(desk.worker.calls)
    window.press_build()
    assert window.status.get().startswith(ui_text.ASKED_TOO_LATE) and len(desk.worker.calls) == calls


def test_parts_built_by_build_parts_and_a_change_they_cannot_take_hold_update_with_the_reason(desk, a_later_kind):
    window = desk.open(with_later_row())
    window.press_build()
    desk.finish(window)
    save_in_excel(window, {"Gears": {"K2": "arcs"}})
    footer = window.footer()
    assert footer.build_label == "Build parts" and footer.build_enabled
    assert footer.update_shown and not footer.update_enabled
    assert footer.text.endswith("so it needs a new part. Update SolidWorks waits until Build has made what that needs.")
    calls = len(desk.worker.calls)
    window.press_update()
    assert len(desk.worker.calls) == calls


def test_update_greyed_after_a_failed_assembly_says_why(desk):
    window = desk.open()
    desk.sw.fail_on = {"save_as": (desk.part(NAME, ".SLDASM"), "The disk is full.")}
    window.press_build()
    desk.finish(window)
    footer = window.footer()
    assert footer.update_shown and not footer.update_enabled
    assert window.status.get().endswith("was saved but its assembly was not made: Build carries on with it, and Update "
                                        "SolidWorks waits until it has.")


def test_update_plan_is_what_update_would_do_and_tk_update_is_tks(desk):
    """W4 review nit: WorkbookWindow.update held the UpdatePlan and hid Tk's own update()."""
    window = built(desk)
    assert window.update_plan.record_matches
    window.update()                                            # Tk's: processes events, raises nothing


def test_the_demonstrations_structural_step_with_update_unsaved_asks_for_the_save_once(desk, monkeypatch):
    """The demonstration's state 06 (w4-window-20261113-195843.log; review S4.1): after Update, unsaved, G1's bore
    cleared. It asked for the save twice, offered Update while greyed, named one of three unsaved documents and said
    "build again" three times. On a gearbox W4 built, where the tooth change is an Update."""
    window = built_w4(desk, monkeypatch)
    save_in_excel(window, DEMONSTRATION)
    window.press_update()
    desk.finish(window)
    save_in_excel(window, {"Gears": {"J2": ""}}, seconds=4)
    text = window.status.get()
    assert text.endswith(f"Gear_m1.5_N68, {NAME}_Layout and {NAME} have changes from Update SolidWorks that are not "
                         "saved: save them in SolidWorks to keep them. If SolidWorks closed them without saving, those "
                         "changes are gone. While Gear_m1.5_N68's changes are not saved, the new revision makes G2's "
                         "part new, as Gear_m1.5_N69, rather than reuse it.")
    assert text.startswith(f"Gear_m1.5_N17 (G1): A bore cannot be added to or removed from a built part through its "
                           f"values, so it needs a new part. Update SolidWorks offers to build again as {NAME}_r2; it "
                           "was built static, before gears could be mated to turn, and the new revision's gears "
                           "turn.")
    # The offer once, with what W5 adds to it for a gearbox W4 built (D5) said inside it.
    assert text.count("save them") == 1 and text.lower().count("build again") == 1
    footer = window.footer()
    assert footer.ok and footer.build_enabled and footer.update_enabled
    assert window.read_line.get().endswith(" · changed since it was built")
    # The table agrees with the footer (the W4 rerun on SolidWorks 2026, state 06: G2 read "built" while the footer
    # made its part new): G1 needs a new part, G2's part is made new by the build, G3 and G4 are reused as built.
    assert gear_states(window) == {"G1": "needs a new part", "G2": "new part on Build", "G3": "built",
                                   "G4": "built"}


# -- the second W4 review ------------------------------------------------------------------------------------------


def _moved_away(desk, window):
    """The built workbook moved to another folder by hand, its record with it (naming the old path, now gone)."""
    import shutil
    old = window.link.path
    window._pending = window._job = None
    window.close()
    folder = desk.tmp / "moved"
    folder.mkdir(exist_ok=True)
    new = folder / f"{NAME}.xlsx"
    shutil.move(old, new)
    shutil.move(store.link_record_path(old), store.link_record_path(str(new)))
    return old, new


def test_a_record_whose_workbook_is_gone_is_asked_about_once_and_yes_adopts_it(desk, monkeypatch):
    """Second W4 review N1c: a record written for a workbook that is gone was adopted silently and for good — and
    two copies of one deleted original both adopted it. Now the window asks once (default No); until the answer
    the record is not taken as this workbook's; Yes adopts it, and the answer is kept in the record."""
    from gear_generator import workbook_gui
    asked = []
    monkeypatch.setattr(workbook_gui, "ask_yes_no", lambda parent, title, text: asked.append((title, text)) or True)
    old, new = _moved_away(desk, built(desk))
    window = desk.open(path=new)
    assert asked == [] and window.record is None and window.plan.foreign_gone      # not from inside planning
    assert window.status.get().endswith(
        f"The record that came with this workbook was written for {ui_text.short_path(old, 48)}, which is not there "
        "any more: until you say whether this workbook was moved or renamed from it, Build makes this workbook's own "
        "gearbox beside the files it lists, sharing and overwriting nothing.")
    window.update()                                            # the question, once the plan is painted
    assert asked == [(ui_text.MOVED_TITLE, ui_text.moved_question(str(new), old))]
    assert asked[0][1] == (
        f"The record of what was built beside this workbook was written for {ui_text.short_path(old, 60)}, which is "
        "not there any more. Was this workbook moved or renamed from it? Yes: the record is this workbook's, and "
        "Update SolidWorks and Build carry on from what it lists; the answer is kept in the record. No: this workbook "
        "is a copy, so Build makes its own gearbox beside those files, sharing and overwriting nothing; until it has, "
        "you are asked again the next time Gear Generator opens this workbook. If that workbook may be on a drive "
        "that is not connected now, answer No: nothing is shared or overwritten.")
    record = record_of(window)
    assert store.same_path(record.workbook, str(new)) and record.moved_from == [old] and record.copy_of == ""
    assert window.record is not None and window.read_line.get().endswith(" · built from this version")
    window.reread()
    window.update()
    assert len(asked) == 1                                     # never asked again


def test_no_keeps_a_record_whose_workbook_is_gone_another_workbooks_and_builds_beside_it(desk, monkeypatch):
    """No holds for the session, and is never written (third W4 review: the way back from a mistaken No): another
    window in this session is not asked again, a new session is — until this workbook's first build replaces the
    record with its own. Nothing says the gone original "is still there" (item 4)."""
    from gear_generator import workbook_gui
    asked = []
    monkeypatch.setattr(workbook_gui, "ask_yes_no", lambda parent, title, text: asked.append(title) or False)
    old, new = _moved_away(desk, built(desk))
    before = record_bytes_of(new)
    window = desk.open(path=new)
    window.update()
    assert asked == [ui_text.MOVED_TITLE]
    assert record_bytes_of(new) == before                       # nothing written: the record as it came
    assert window.record is None and not window.footer().update_shown
    assert window.plan.foreign_record == old and not window.plan.foreign_gone and window.plan.foreign_said
    footer = window.status.get()
    assert "still there" not in footer and footer.endswith(
        f"The record that came with this workbook was written for {ui_text.short_path(old, 48)}, which you said this "
        "workbook is a copy of, so that record, and the SolidWorks files it lists, are that workbook's: Build makes "
        "this workbook's own gearbox beside them, sharing and overwriting nothing. If this workbook was in fact moved "
        "or renamed from it, quit Gear Generator and open this workbook again before you build, and you are asked "
        "again.")
    # Another window on it in this session is not asked again.
    window._pending = window._job = None
    window.close()
    again = desk.open(path=new)
    again.update()
    assert asked == [ui_text.MOVED_TITLE] and again.record is None and again.plan.foreign_said
    # A new session is, while nothing has been built.
    workbook_gui._VERDICTS.clear()
    workbook_gui._ASKED.clear()
    again._pending = again._job = None
    again.close()
    again = desk.open(path=new)
    again.update()
    assert asked == [ui_text.MOVED_TITLE] * 2 and again.record is None
    again.press_build()
    desk.finish(again)
    built_now = record_of(again)
    assert store.same_path(built_now.workbook, str(new)) and built_now.gearbox.revision == 2


def test_two_copies_of_one_deleted_original_are_each_asked_never_adopt_silently(desk, monkeypatch):
    import shutil
    from gear_generator import workbook_gui
    asked = []
    monkeypatch.setattr(workbook_gui, "ask_yes_no", lambda parent, title, text: asked.append(title) or False)
    window = built(desk)
    original = window.link.path
    copies = []
    for name in ("a", "b"):
        folder = desk.tmp / name
        folder.mkdir()
        copy = folder / f"{NAME}.xlsx"
        shutil.copy2(original, copy)
        shutil.copy2(store.link_record_path(original), store.link_record_path(str(copy)))
        copies.append(copy)
    window._pending = window._job = None
    window.close()
    os.remove(original)                                        # the original deleted
    for copy in copies:
        w = desk.open(path=copy)
        w.update()
        assert w.record is None
    assert asked == [ui_text.MOVED_TITLE, ui_text.MOVED_TITLE]
    assert all(record_of_path(c).workbook == original and record_of_path(c).moved_from == [] for c in copies)


def test_locate_on_a_copy_never_takes_the_originals_record_for_its_own(desk, monkeypatch):
    """Second W4 review N1b (w4v_locate_launders_copy): a copy renamed while open, then Locate…, adopted the
    original's record, and the copy's Update then drove the original's files."""
    import shutil
    from gear_generator import workbook_gui
    window = built(desk)
    original = window.link.path
    folder = desk.tmp / "copy"
    folder.mkdir()
    copy = folder / f"{NAME}.xlsx"
    shutil.copy2(original, copy)
    shutil.copy2(store.link_record_path(original), store.link_record_path(str(copy)))
    opened = desk.open(path=copy)
    assert opened.record is None and opened.plan.foreign_record == original
    renamed = folder / f"{NAME} v2.xlsx"
    os.rename(copy, renamed)
    monkeypatch.setattr(workbook_gui.filedialog, "askopenfilename", lambda **kw: str(renamed))
    opened.locate()
    assert not os.path.exists(store.link_record_path(str(renamed)))
    assert opened.record is None and opened.update_plan is None and not opened.footer().update_shown
    assert ("The record of what was built stays beside the workbook's old place: it was written for "
            f"{original}, so it is that workbook's record and lists that workbook's files, not this one's.") \
        in opened.status.get()


def test_closing_a_window_twice_while_solidworks_does_not_answer_offers_to_close_anyway_and_the_journal_reuses(
        desk, monkeypatch):
    """Second W4 review N4.3: with SolidWorks held by a dialog the window could not be closed at all, and killing the
    app lost the record. A second close asks (default No); Yes closes, leaving the job's files to the journal: the
    next window plans them for reuse, checked live, and writes their .gear.json."""
    from gear_generator import workbook_gui
    answers, asked = [False, True], []
    monkeypatch.setattr(workbook_gui, "ask_yes_no",
                        lambda parent, title, text: asked.append((title, text)) or answers.pop(0))
    window = desk.open()
    path = window.link.path
    window.press_build()
    journal = record_of(window).pending
    assert [os.path.basename(e.path) for e in journal] == [f"{s}.SLDPRT" for s in PARTS] + [
        f"{NAME}_Layout.SLDPRT", f"{NAME}.SLDASM"]
    window.close()                                             # first: it stays, and closes once on record
    assert asked == [] and not window._closed()
    window.close()                                             # second: asks; No keeps waiting
    assert asked == [(ui_text.CLOSE_ANYWAY_TITLE, ui_text.close_anyway_question(journaled=True))]
    assert not window._closed()
    assert asked[0][1] == (
        "SolidWorks has not answered yet: the build is still running there, perhaps held up by a dialog open in "
        "SolidWorks. Close this window anyway? Nothing the build saves is put on record by this window, and nothing "
        "will be overwritten: the build listed what it is about to make in the record before it began, so the next "
        "Build finds those files, checks them in SolidWorks and reuses what it can.")
    window.close()                                             # again: Yes closes; the job goes on
    assert window._closed()
    # While that job runs, no Workbook window starts another, and says why (third W4 review).
    meanwhile = desk.open(path=path)
    calls = len(desk.worker.calls)
    meanwhile.press_build()
    assert len(desk.worker.calls) == calls and meanwhile._pending is None
    assert meanwhile.status.get() == ui_text.unowned_job_busy()
    assert record_of_path(path).pending == journal
    meanwhile.close()
    desk.worker.run()                                          # SolidWorks answers at last: nobody collects it
    assert all(store.read_sidecar(desk.part(s)) is None for s in PARTS)
    assert record_of_path(path).pending == journal and record_of_path(path).parts == []
    # The parts are reused once checked; the assembly SolidWorks saved is in the way of revision 0, so the build
    # goes beside it as revision 2, saying why, with a layout part of its own.
    again = desk.open(path=path)
    assert [r.stem for r in again.plan.reuse] == list(PARTS) and all(r.journaled for r in again.plan.reuse)
    assert again.plan.revision == 2 and again.plan.build == () and not isinstance(again.plan.layout, LayoutReuse)
    assert again.plan.revision_reason.startswith(f"{NAME}.SLDASM was saved by a build that was interrupted before it "
                                                 "was put on record")
    again.press_build()
    desk.finish(again)
    record = record_of(again)
    assert record.gearbox.revision == 2 and len(record.parts) == 4
    assert all(store.read_sidecar(desk.part(s)).record.workbook == path for s in PARTS)
    # The parts are on record now and left the journal; the layout part and assembly the abandoned job saved at
    # revision 0 are on disk and on no record, so they stay this workbook's in the journal (third W4 review: an
    # entry leaves only once on record or gone).
    assert sorted(os.path.basename(e.path) for e in record.pending) == [f"{NAME}.SLDASM", f"{NAME}_Layout.SLDPRT"]


def test_a_question_open_over_a_window_keeps_it_and_the_app_until_it_is_answered(desk, monkeypatch):
    """Second W4 review N4.4: CloseGuard destroyed the root with Build again? still open, and its answer then ran on
    destroyed widgets."""
    from gear_generator import gui, workbook_gui
    said, quit = [], []
    guard = gui.CloseGuard(desk.root, lambda text, ok=True: said.append((text, ok)), poll_ms=10 ** 6,
                           quit=lambda: quit.append(True))
    window = built(desk)
    save_in_excel(window, {"Gears": {"J2": ""}})                # a change that asks Build again?

    def close_the_app_meanwhile(parent, title, text):
        guard.request()                                        # the strip's close clicked while the question is open
        assert quit == [] and said[-1] == (ui_text.APP_CLOSES_AFTER_QUESTION, True)
        return False

    monkeypatch.setattr(workbook_gui, "ask_yes_no", close_the_app_meanwhile)
    window.press_update()
    assert window._closed()                                    # answered: then closed, as asked
    guard.check()
    assert quit == [True]


def test_closing_the_strips_window_twice_while_a_job_has_not_answered_offers_to_quit_anyway(desk):
    from gear_generator import gui
    said, quit, asked = [], [], []
    answers = [False, True]
    guard = gui.CloseGuard(desk.root, lambda text, ok=True: said.append((text, ok)), poll_ms=10 ** 6,
                           quit=lambda: quit.append(True),
                           ask=lambda title, text: asked.append((title, text)) or answers.pop(0))
    window = desk.open()
    window.press_build()
    guard.request()
    assert asked == [] and quit == []
    guard.request()
    assert asked == [(ui_text.QUIT_ANYWAY_TITLE, ui_text.quit_anyway_question(True))] and quit == []
    assert asked[0][1] == (
        "SolidWorks has not answered yet: a job is still running there, perhaps held up by a dialog open in "
        "SolidWorks. Quit anyway? Nothing that job saves or changes is put on record by this session, and nothing "
        "will be overwritten. A workbook's build lists what it is about to make in that workbook's record before it "
        "begins, unless the record cannot be written, so the workbook's next Build finds the files it saved, checks "
        "them in SolidWorks and reuses what it can.")
    guard.request()
    assert quit == [True]


def test_closing_the_strips_window_waits_for_the_strips_own_build(desk):
    """Second W4 review N4.5: the strip's own build was not guarded: closing mid-build lost the part's .gear.json."""
    from gear_generator import gui
    said, quit = [], []
    guard = gui.CloseGuard(desk.root, lambda text, ok=True: said.append((text, ok)), poll_ms=10 ** 6,
                           quit=lambda: quit.append(True), strip=desk.app)
    desk.app._pending_build = object()                         # the strip building a part of its own
    guard.request()
    assert quit == [] and said == [(ui_text.app_closes_when_done(0, strip=True), True)]
    assert said[0][0] == ("Gear Generator closes once the strip's job in SolidWorks has finished and the strip has "
                          "collected it.")
    guard.check()
    assert quit == []
    desk.app._pending_build = None                             # the strip's poll collected it, its record written
    guard.check()
    assert quit == [True]


# -- the third W4 review -------------------------------------------------------------------------------------------


def test_a_build_refused_after_an_interrupted_one_keeps_what_that_build_saved_in_the_journal(desk):
    """Third W4 review item 3 (w4x_clear_journal_orphans): a build interrupted after two parts saved; the next Build's
    job refused at its pre-flight; the window cleared the whole journal, and the plan after went beside the two
    files as _r2. Only what is not on disk, or on record, leaves the journal now."""
    window = desk.open()
    path = window.link.path
    plan = window.plan
    window._write_journal(plan)
    from gear_generator import swbuild
    swbuild.build_many(desk.sw, [j.plan for j in plan.build[:2]], desk.sw.exists)   # two saved, then the app gone
    window._pending = window._job = None
    window.close()
    again = desk.open(path=path)
    assert [r.stem for r in again.plan.reuse] == list(PARTS[:2]) and all(r.journaled for r in again.plan.reuse)
    elsewhere = str(desk.tmp / "elsewhere" / f"{PARTS[2]}.SLDPRT")
    desk.sw.open_docs = [DocInfo(title=f"{PARTS[2]}.SLDPRT", path=elsewhere, doc_type=1)]
    again.press_build()
    desk.finish(again)
    assert again.status.get().startswith(f"{elsewhere} is open in SolidWorks")
    assert sorted(os.path.basename(e.path) for e in record_of(again).pending) == [f"{s}.SLDPRT" for s in PARTS[:2]]
    assert [r.stem for r in again.plan.reuse] == list(PARTS[:2]) and again.plan.made_new == ()
    desk.sw.open_docs = []                                         # the other document closed: Build again
    again.press_build()
    desk.finish(again)
    record = record_of(again)
    assert record.pending == [] and record.gearbox.revision == 0 and len(record.parts) == 4


def test_a_finish_that_raises_after_an_update_that_changed_nothing_never_says_its_changes_are_in_solidworks(
        desk, monkeypatch):
    """Third W4 review (ride-along): "Its changes are in SolidWorks, not saved" was said even when the update had
    changed nothing (every document found holding the values already)."""
    from gear_generator import swbuild, workbook_gui
    from gear_generator.workbook import update as wb_update
    window = built(desk)
    save_in_excel(window, DEMONSTRATION)
    assert window.update_plan is not None

    def broken(*args, **kwargs):
        raise KeyError("parts")
    monkeypatch.setattr(wb_update, "finish_update", broken)
    job = workbook_gui.Job(workbook_gui.JOB_UPDATE, window.reading.digest, update=window.update_plan,
                           record=window.record)
    nothing = window._finish_update(job, swbuild.GearboxUpdate())
    assert "Its changes are in SolidWorks" not in nothing.text and "It changed nothing in SolidWorks." in nothing.text
    changed = window._finish_update(job, swbuild.GearboxUpdate(changed=[desk.part(PARTS[1])]))
    assert "Its changes are in SolidWorks, not saved" in changed.text


# -- W5: the gearbox that turns ----------------------------------------------------------------------------------
#
# Every sentence below is ui_text's for that state, written out whole as the window shows it.

TURNING_EDIT = {"Shafts": {"C4": 148.75}, "Gears": {"G4": 2.5, "G5": 2.5, "C5": 30}}
"""An Update of a turning gearbox (the demonstration's, in place of W4's G2 68 → 69, which changes a gear mate's
ratio): G3 and G4 to module 2.5 with S3 moved out to their new centre (no ratio changes), and G4's At 27 → 30, which
moves S3's anchor along its shaft (its Face Z)."""


def test_a_refused_mate_greys_build_for_that_read_and_a_changed_workbook_offers_it_again(desk):
    """W5-DECISIONS answer 1: a refused mate stops the build and says why; the parts and the layout part are kept;
    Build waits for a changed workbook, since the same one would make the same mates."""
    desk.sw.mate_codes = {"G3 locked to G2": (46, False)}     # the fake flags the lock, as SolidWorks may
    window = desk.open()
    window.press_build()
    desk.finish(window)
    assert window.status.get() == (
        f"Built 4 parts and {NAME}_Layout; no assembly was saved, because SolidWorks found a problem with its mates. "
        "The mate G3 locked to G2 is in error in SolidWorks. The parts and the layout part are kept. The assembly is "
        "left open in SolidWorks as Assem1, not saved; its parts are the saved ones. Build is available again once the "
        "workbook changes: the same workbook would make the same mates. Update SolidWorks waits until Build has made "
        "the assembly.")
    footer = window.footer()
    assert (footer.build_label, footer.build_enabled, footer.update_shown, footer.update_enabled, footer.ok) == (
        "Build", False, True, False, False)
    assert not window.build_button._enabled and not window.update_button._enabled
    record = record_of(window)
    assert record.gearbox.layout and not record.gearbox.assembly and len(record.parts) == 4
    assert record.gearbox.mate_problems == ["The mate G3 locked to G2 is in error in SolidWorks."]
    assert record.gearbox.mate_problems_digest == window.reading.digest
    assert window.read_line.get().endswith(" · its assembly was refused for this version")
    calls = len(desk.worker.calls)
    window.press_build()                                       # greyed: a press does nothing
    assert len(desk.worker.calls) == calls

    window.note = None                                         # the state's own sentence says the same
    window._refresh_state()
    assert window.status.get() == (
        f"{NAME}.SLDASM was not saved, because SolidWorks found a problem with its mates. The mate G3 locked to G2 is "
        "in error in SolidWorks. Build is available again once the workbook changes: the same workbook would make the "
        "same mates. Update SolidWorks waits until Build has made the assembly.")
    assert not window.footer().build_enabled

    save_in_excel(window, {"Gears": {"W2": "pinion, checked"}})    # any save (Notes, W since W9b)
    footer = window.footer()
    assert footer.build_enabled and footer.ok and not footer.update_enabled
    assert window.read_line.get().endswith(" · changed since its assembly was refused")
    assert window.status.get() == (
        f"Ready: Build makes {NAME}.SLDASM in {ui_text.short_path(str(desk.folder), 48)}, reusing {NAME}_Layout and "
        "the 4 parts already built. Its gears are mated to their shafts and to each other, so they turn together in "
        f"SolidWorks. {NAME}.SLDASM was not saved, because SolidWorks found a problem with its mates. The mate G3 "
        "locked to G2 is in error in SolidWorks. The workbook has changed since, so Build tries the assembly again. "
        f"{NAME}_Layout.SLDPRT was saved but its assembly was not made: Build carries on with it, and Update "
        "SolidWorks waits until it has.")

    desk.sw.mate_codes = {}
    start = len(desk.sw.calls)
    window.press_build()
    desk.finish(window)
    assert [os.path.basename(p) for p in desk.sw.saved_in(start)] == [f"{NAME}.SLDASM"]
    assert window.status.get() == (
        f"Built {NAME}.SLDASM, reusing {NAME}_Layout and the 4 parts already built; no interference between the gears "
        "where they stand. Its gears are mated to turn together, and SolidWorks reports no mate in error: drag G1 in "
        "SolidWorks and the rest of its train follow.")
    box = record_of(window).gearbox
    assert box.kind == store.GEARBOX_MOTION and box.assembly and (box.mate_problems, box.mate_problems_digest) == (
        [], "")


def test_update_on_a_turned_train_with_nothing_to_put_leaves_it_where_it_was_turned_and_says_so(desk):
    """W5-DECISIONS answer 2: with nothing to put, the train stays where the user turned it, said plainly."""
    window = built(desk)
    turn_train(desk, window, 30.0)
    turned = {g: desk.sw.frames[name2(window, g)] for g in ("G1", "G2", "G3", "G4")}
    start = len(desk.sw.calls)
    window.press_update()
    desk.finish(window)
    assert window.status.get() == ("SolidWorks already matches the workbook: nothing was changed. The gears stand "
                                   "where they were turned in SolidWorks.")
    assert window.status_label.cget("fg") == __import__("gear_generator.theme", fromlist=["x"]).OK
    assert {g: desk.sw.frames[name2(window, g)] for g in turned} == turned
    assert not [c for c in desk.sw.calls[start:] if c[0] == "place_component"]
    assert record_of(window).unsaved == {}


def test_the_turning_demonstration_edit_is_an_update_and_puts_a_turned_train_back_at_its_built_turn(desk):
    """W5-DECISIONS answer 2: Update returns a turned train to its built position when it must move a gear, and says
    so for that train."""
    window = built(desk)
    turn_train(desk, window, 30.0)
    save_in_excel(window, TURNING_EDIT)
    assert window.status.get() == (f"Update SolidWorks will change the values in Gear_m2_N17 (G3) and OutputGear (G4), "
                                   f"move S3 in {NAME}_Layout, move G4 along S3, and re-place G1, G2, G3 and G4. {TURNS}")
    assert window.update_button._enabled and window.update_button._primary
    window.press_update()
    desk.finish(window)
    assert window.status.get() == (
        "Updated SolidWorks: changed 1 variable in Gear_m2_N17 (it is now module 2.5; its file keeps its name), "
        f"changed 1 variable in OutputGear, moved S3 in {NAME}_Layout, moved G4 along S3, re-placed G1, G2, G3 and G4; "
        "no interference between the gears where they stand. G1, G2, G3 and G4 had been turned in SolidWorks; their "
        "train is back at the turn it was built at. Save Gear_m2_N17, OutputGear, Reducer_12to1_Layout and "
        "Reducer_12to1 in SolidWorks to keep them.")
    assert desk.sw.locked_puts == []                           # every put made with the train's lock off
    record = record_of(window)
    assert {m.name: m.z_front for m in record.gearbox.mates if m.kind == motion.ALONG}["G4 along S3"] == 20.0
    window.note = None
    window._refresh_state()
    assert window.update_plan.record_matches and window.status.get().startswith(
        "SolidWorks already matches the workbook on record; Update SolidWorks checks it live and puts right anything "
        "changed there; gears turned in SolidWorks stay where they are unless something must move. " + TURNS)


def test_an_anchors_edit_off_the_front_plane_needs_build_again_and_the_sentence_names_the_edit(desk, monkeypatch):
    """W5-DECISIONS answer 3: no datum plane, so an anchor's front face leaving the Front plane is structural, and
    the sentence names the edit, never only the plane."""
    from gear_generator import workbook_gui
    window = built(desk)
    save_in_excel(window, {"Gears": {"C2": 10}})               # G1's At 7.5 → 10
    assert window.status.get() == (
        "G1's At (7.5 → 10) moves its front face off the Front plane (z 0 → 2.5): the mate G1 along S1 holds it on "
        "that plane and cannot take a distance, so the gearbox needs building again. Update SolidWorks offers to build "
        f"again as {NAME}_r2. {TURNS}")
    asked = []
    monkeypatch.setattr(workbook_gui, "ask_yes_no", lambda parent, title, text: asked.append(text) or False)
    window.press_update()
    (question,) = asked
    assert question.startswith("G1's At (7.5 → 10) moves its front face off the Front plane (z 0 → 2.5): the mate G1 "
                               "along S1 holds it on that plane and cannot take a distance, so the gearbox needs "
                               f"building again. Build again as {NAME}_r2? That reuses 4 parts that have not "
                               "changed")
    assert "was built static" not in question                  # a turning record is never told so


def test_a_tooth_change_needs_build_again_until_a_gear_mates_ratio_can_be_changed(desk):
    """D7, without the ratio route (findings.GEAR_MATE_RATIO_ROUTE None): W4's demonstration edit names the gear
    mate it would change and offers Build again…."""
    window = built(desk)
    save_in_excel(window, DEMONSTRATION)
    assert window.status.get() == (
        "G2's teeth (68 → 69) change the gear mate G1 meshes G2 from 17 : 68 to 17 : 69, and a gear mate's ratio cannot "
        "be changed in a built assembly until the probes settle how (findings.GEAR_MATE_RATIO_ROUTE), so the gearbox "
        f"needs building again. Update SolidWorks offers to build again as {NAME}_r2. {TURNS}")
    assert window.update_plan.needs_new_revision and window.footer().update_enabled


def test_a_tooth_change_is_an_update_that_sets_the_gear_mate_once_its_ratio_can_be_remade(desk, monkeypatch):
    """D7 with the remake route: the same edit is an Update, which remakes the gear mate at the new ratio."""
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_ROUTE", "remake")
    window = built(desk)
    save_in_excel(window, DEMONSTRATION)
    assert window.status.get() == (f"Update SolidWorks will change G2's values (Gear_m1.5_N68), move S2 and S3 in "
                                   f"{NAME}_Layout, set the gear mate G1 meshes G2 to 17 : 69, and re-place G1, G2, G3 "
                                   f"and G4. {TURNS}")
    window.press_update()
    desk.finish(window)
    assert window.status.get() == (
        "Updated SolidWorks: changed 1 variable in Gear_m1.5_N68 (it now has 69 teeth; its file keeps its name), moved "
        f"S2 and S3 in {NAME}_Layout, set the gear mate G1 meshes G2 to 17 : 69, re-placed G1, G2, G3 and G4; no "
        "interference between the gears where they stand. Save Gear_m1.5_N68, Reducer_12to1_Layout and Reducer_12to1 "
        "in SolidWorks to keep them.")
    assert {m.name: m.ratio for m in record_of(window).gearbox.mates}["G1 meshes G2"] == [17, 69]


def test_a_gearbox_w4_built_stays_static_and_is_offered_a_turning_revision(desk, monkeypatch, w9d_unmeasured):
    """D5: a W4 static record is never changed into a turning one by Update; the footer and the Build again?
    question say the new revision's gears turn."""
    from gear_generator import workbook_gui
    window = built_w4(desk, monkeypatch)
    assert window.status.get() == ("SolidWorks already matches the workbook on record; Update SolidWorks checks it "
                                   "live and puts right anything changed there. It was built static, before gears "
                                   "could be mated to turn: Build again… makes a new revision whose gears turn.")
    assert window.update_plan.motion is None and window.plan.motion is not None
    asked = []
    monkeypatch.setattr(workbook_gui, "ask_yes_no", lambda parent, title, text: asked.append(text) or False)
    window.press_build()
    assert asked == [
        f"{NAME}.SLDASM was built static; the new revision's gears are mated to turn. Build again as {NAME}_r2? That "
        f"reuses 4 parts that have not changed and makes a new layout part and assembly ({NAME}_r2_Layout and "
        f"{NAME}_r2.SLDASM). Nothing is overwritten, and {NAME}.SLDASM stays as it is on disk, but it shares the 4 "
        f"reused parts: a later Update SolidWorks that changes one of them changes {NAME}.SLDASM too. "
        + TIMELESS]                                            # W9a (ruling 4 on B's review): nothing read is on record
    window.press_update()                                      # Update carries on as W4: nothing differs, no question
    desk.finish(window)
    assert len(asked) == 1 and record_of(window).gearbox.kind == store.GEARBOX_STATIC
    assert window.status.get() == "SolidWorks already matches the workbook: nothing was changed."


def test_a_recorded_mate_update_cannot_read_still_offers_build_again(desk, monkeypatch, w9d_unmeasured):
    """The refusal names Build again…, so the window keeps that button on and its press asks: the person is never
    left with nothing to press."""
    from gear_generator import workbook_gui
    window = built(desk)
    path = pathlib.Path(store.link_record_path(window.link.path))
    raw = json.loads(path.read_text())
    raw["gearbox"]["mates"][0]["name"] = ""                    # hand-edited: a mate Update could not find
    path.write_text(json.dumps(raw))
    window.note = None
    window._plan()
    window._paint()
    refusal = ("The record of what was built lists a mate with no name, and Update SolidWorks finds each mate by its "
               "name, so Update SolidWorks cannot act on the gearbox the record describes: Build again… makes a new "
               "revision from the workbook instead.")
    assert window.status.get() == refusal
    footer = window.footer()
    assert (footer.build_label, footer.build_enabled, footer.update_shown, footer.update_enabled) == (
        "Build again…", True, True, False)
    asked = []
    monkeypatch.setattr(workbook_gui, "ask_yes_no", lambda parent, title, text: asked.append((title, text)) or False)
    window.press_build()
    ((title, question),) = asked
    assert title == "Build again?" and question == (
        f"{refusal} Build again as {NAME}_r2? That reuses 4 parts that have not changed and makes a new layout part "
        f"and assembly ({NAME}_r2_Layout and {NAME}_r2.SLDASM). Nothing is overwritten, and what is already built is "
        "left as it is. " + TIMELESS)                          # W9a (ruling 4 on B's review): nothing read on record
    assert window.status.get() == f"{ui_text.NOTHING_CHANGED} {refusal}"


# -- W5, the W4 review's failure cases on a gearbox that turns -------------------------------------------------------


def test_an_update_of_a_turning_gearbox_lost_with_solidworks_is_made_again_by_the_next_press(desk):
    """SolidWorks closed without saving after Update: the footer still asks for the save and says Update makes the
    changes again; the next press does, from the files, and marks them unsaved again."""
    window = built(desk)
    save_in_excel(window, TURNING_EDIT)
    window.press_update()
    desk.finish(window)
    unsaved = {"Gear_m2_N17.SLDPRT", "OutputGear.SLDPRT", f"{NAME}_Layout.SLDPRT", f"{NAME}.SLDASM"}
    assert {os.path.basename(p) for p in record_of(window).unsaved} == unsaved
    desk.sw.close_all()                                        # SolidWorks closed, nothing saved
    window.note = None
    window._refresh_state()
    assert window.status.get().endswith(
        f"Gear_m2_N17, OutputGear, {NAME}_Layout and {NAME} have changes from Update SolidWorks that are not saved: "
        "save them in SolidWorks to keep them. If SolidWorks closed them without saving, press Update SolidWorks to "
        "make them again.")
    assert window.footer().update_enabled
    start = len(desk.sw.calls)
    window.press_update()
    desk.finish(window)
    text = window.status.get()
    assert text.startswith("Updated SolidWorks: changed 1 variable in Gear_m2_N17 (it is now module 2.5; its file "
                           f"keeps its name), changed 1 variable in OutputGear, moved S3 in {NAME}_Layout, moved G4 "
                           "along S3, re-placed G1, G2")
    assert text.endswith(f"Save Gear_m2_N17, OutputGear, {NAME}_Layout and {NAME} in SolidWorks to keep them.")
    sets = [args for name, args in desk.sw.calls[start:] if name == "set_global_variable"]
    assert ("S3 X", "148.75") in sets and ("G4 Face Z", "20") in sets
    assert {os.path.basename(p) for p in record_of(window).unsaved} == unsaved
    assert desk.sw.locked_puts == [] and window.update_plan.record_matches


def test_a_lost_update_made_again_is_said_so_and_never_said_to_be_a_gear_moved_by_hand(desk):
    """After an Update lost when SolidWorks closed unsaved, the next press finds the gears where the lost Update
    had not yet put them: that is the lost Update's, never the user's doing (B's Finished.earlier_update, which the
    window passes on), on a turning gearbox and on one W4 built alike."""
    window = built(desk)
    save_in_excel(window, TURNING_EDIT)
    window.press_update()
    desk.finish(window)
    desk.sw.close_all()
    window.press_update()
    desk.finish(window)
    assert window.status.get() == (
        "Updated SolidWorks: changed 1 variable in Gear_m2_N17 (it is now module 2.5; its file keeps its name), "
        f"changed 1 variable in OutputGear, moved S3 in {NAME}_Layout, moved G4 along S3, re-placed G1, G2, G3 and G4; "
        f"no interference between the gears where they stand. The last Update SolidWorks was not saved before "
        f"{NAME}.SLDASM was closed, so its changes were made again: G4 is back where the workbook has it. Save "
        f"Gear_m2_N17, OutputGear, {NAME}_Layout and {NAME} in SolidWorks to keep them.")


def test_a_lost_update_on_a_gearbox_w4_built_is_said_so_too(desk, monkeypatch):
    static = built_w4(desk, monkeypatch)
    save_in_excel(static, DEMONSTRATION)
    static.press_update()
    desk.finish(static)
    desk.sw.close_all()
    static.press_update()
    desk.finish(static)
    assert static.status.get() == (
        f"Updated SolidWorks: changed 1 variable in Gear_m1.5_N68 (it now has 69 teeth; its file keeps its name), moved "
        f"S2 and S3 in {NAME}_Layout, re-placed G2, G3 and G4; no interference between the gears. The last Update "
        f"SolidWorks was not saved before {NAME}.SLDASM was closed, so its changes were made again: G2, G3 and G4 are "
        f"back where the workbook has them. Save Gear_m1.5_N68, {NAME}_Layout and {NAME} in SolidWorks to keep them.")


def test_a_gear_dragged_by_hand_with_no_update_unsaved_is_still_said_to_be_moved(desk):
    window = built(desk)
    rotation, at = desk.sw.frames[name2(window, "G4")]
    desk.sw.frames[name2(window, "G4")] = (rotation, (at[0] + 3.0, at[1] - 2.0, at[2]))
    window.press_update()
    desk.finish(window)
    assert window.status.get() == (
        "Updated SolidWorks: re-placed G1, G2 and G3; no interference between the gears where they stand. G4 had been "
        f"moved in SolidWorks; put back where the workbook has it. Save {NAME} in SolidWorks to keep it.")


def test_an_update_of_a_turning_gearbox_that_stops_part_way_turns_the_locks_back_on_and_the_next_press_finishes(
        desk):
    """A put raising part way (the third gear of the train, after a turn by hand): the locks are back on, nothing
    was put with a lock on, the assembly is among what was changed and not saved, every failure is said, and the
    next press puts the rest and leaves nothing on record to do."""
    from gear_generator import swcom
    window = built(desk)
    turn_train(desk, window, 30.0)
    save_in_excel(window, TURNING_EDIT)
    desk.sw.raises = {"place_component": (desk.sw.counts.get("place_component", 0) + 3,
                                          swcom.SolidWorksError("gear3-1 did not take its frame."))}
    window.press_update()
    desk.finish(window)
    assert window.status.get() == (
        f"Update SolidWorks stopped. {NAME}.SLDASM: gear3-1 did not take its frame. It had already changed "
        f"Gear_m2_N17, OutputGear, {NAME}_Layout and {NAME}, not saved: press Update SolidWorks again once that is put "
        "right, or save them in SolidWorks to keep what it did.")
    assert not window.footer().ok
    assert {os.path.basename(p) for p in record_of(window).unsaved} == {
        "Gear_m2_N17.SLDPRT", "OutputGear.SLDPRT", f"{NAME}_Layout.SLDPRT", f"{NAME}.SLDASM"}
    assert desk.sw.locked_puts == [] and not [m.name for m in desk.sw.mates if m.suppressed]
    desk.sw.raises = {}
    window.note = None
    window._refresh_state()
    assert window.status.get().startswith(f"Update SolidWorks will re-place G1, G2, G3 and G4. {TURNS} Gear_m2_N17, "
                                          f"OutputGear, {NAME}_Layout and {NAME} have changes from Update SolidWorks "
                                          "that are not saved")
    window.press_update()
    desk.finish(window)
    # What the stopped job left is never laid to the user (B's Finished.earlier_update, passed on by the window).
    assert window.footer().ok and window.status.get() == (
        "Updated SolidWorks: re-placed G1, G2, G3 and G4; no interference between the gears where they stand. G3 and "
        "G4 were not where the last Update SolidWorks, which is not saved, has them on record; they are in place "
        "again. G2 and G3 were not in step as that Update has them on record either; they are in step again. Save "
        f"{NAME} in SolidWorks to keep it.")
    assert desk.sw.locked_puts == [] and not [m.name for m in desk.sw.mates if m.suppressed]
    assert window.update_plan.record_matches and record_of(window).digest == window.reading.digest


def test_the_structural_step_with_update_unsaved_on_a_turning_gearbox_asks_for_the_save_once(desk):
    """W4's state 06 on a gearbox that turns: after the turning edit's Update, unsaved, G1's bore cleared."""
    window = built(desk)
    save_in_excel(window, TURNING_EDIT)
    window.press_update()
    desk.finish(window)
    save_in_excel(window, {"Gears": {"J2": ""}}, seconds=4)
    text = window.status.get()
    assert text == (
        "Gear_m1.5_N17 (G1): A bore cannot be added to or removed from a built part through its values, so it needs "
        f"a new part. Update SolidWorks offers to build again as {NAME}_r2. {TURNS} Gear_m2_N17, OutputGear, "
        f"{NAME}_Layout and {NAME} have changes from Update SolidWorks that are not saved: save them in SolidWorks to "
        "keep them. If SolidWorks closed them without saving, those changes are gone. While the changes in "
        "Gear_m2_N17 and OutputGear are not saved, the new revision makes the parts for G3 and G4 new, as "
        "Gear_m2.5_N17 and OutputGear_r2, rather than reuse them.")
    assert text.count("save them") == 1 and text.lower().count("build again") == 1
    footer = window.footer()
    assert footer.ok and footer.build_enabled and footer.update_enabled
    assert gear_states(window) == {"G1": "needs a new part", "G2": "built", "G3": "new part on Build",
                                   "G4": "new part on Build"}


# -- W6: turned axes, bevel and crossed meshes ----------------------------------------------------------------------
#
# Fixture A (Bevel_Reducer: a bevel stage from S1 along X+ into S2, then a parallel stage) and the crossed fixture
# moved off the Top plane (Crossed_Slant 10 mm up, so S1 can pass to S2's other side), as B's tests write them.


def preview_gap():
    """A shaft name's gap off its mark, on this screen."""
    from gear_generator import preview
    from gear_generator.theme import px
    return px(preview.LABEL_GAP) * 1.5


def speed_lines(window):
    return [c.cget("text") for c in sorted(window.speeds_body.winfo_children(), key=lambda c: int(c.grid_info()["row"]))]


def end_view_lines(window):
    """The canvas's line items that are not the shafts' crosses nor the origin's arrows: the turned shafts."""
    c = window.canvas
    lines = [i for i in c.find_all() if c.type(i) == "line" and not c.itemcget(i, "arrow") in ("last", "first")]
    return [i for i in lines if abs(c.coords(i)[0] - c.coords(i)[2]) + abs(c.coords(i)[1] - c.coords(i)[3]) > 20]


def shaft_line(window, name):
    """A turned shaft as the window drew it: its line's unit direction on screen (y up), from the end farther from
    its name to the end nearer it, and how far its name is from that nearer end, px. The geometry itself is pinned
    in tests/test_preview.py; this checks the window strokes what preview gives it."""
    import math
    c = window.canvas
    (label,) = [i for i in c.find_all() if c.type(i) == "text" and c.itemcget(i, "text") == name]
    lx, ly = c.coords(label)
    best = None
    for i in end_view_lines(window):
        x0, y0, x1, y1 = c.coords(i)
        for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)), ((x1, y1), (x0, y0))):
            gap = math.hypot(lx - bx, ly - by)
            if best is None or gap < best[0]:
                best = (gap, ax, ay, bx, by)
    gap, ax, ay, bx, by = best
    length = math.hypot(bx - ax, by - ay)
    return ((bx - ax) / length, -(by - ay) / length), gap


def test_a_right_angle_gearbox_is_ready_to_build_and_says_each_shaft_from_its_own_end(desk):
    from test_workbook_turned import bevel_reducer
    window = desk.open(bevel_reducer(), name="Bevel_Reducer.xlsx")
    footer = window.footer()
    assert (footer.build_label, footer.build_enabled, footer.update_shown, footer.ok) == ("Build", True, False, True)
    assert window.status.get() == (
        "Ready: Build makes 4 parts, Bevel_Reducer_Layout and Bevel_Reducer.SLDASM in "
        f"{ui_text.short_path(str(desk.folder), 48)}. Its gears are mated to their shafts and to each other, so they "
        "turn together in SolidWorks.")
    assert window.box_values["type"].cget("text") == ("Bevel and parallel train · 2 meshes · 6.000 : 1 · output at "
                                                       "90° to the input")
    # Each number held to its unit by a no-break space (C's ui_text.NBSP), so a wrapped line never splits them.
    assert speed_lines(window) == ["S1    1500.0\u00a0rpm anticlockwise seen from the +X end · 10.00\u00a0N·m",
                                   "S2    750.0\u00a0rpm clockwise seen from the +Z end · 19.60\u00a0N·m",
                                   "S3    250.0\u00a0rpm anticlockwise seen from the +Z end · 57.62\u00a0N·m"]
    assert window.speeds_readout.get() == "seen from each shaft's + end"
    # The end view: S1 is a line through G1 seen side-on, along +X and named at that end; S2 and S3 crosses; the bevel
    # stage one colour, at z 60.
    assert window.view_readout.get() == "z 5 · z 60 · origin" and len(end_view_lines(window)) == 1
    direction, gap = shaft_line(window, "S1")
    assert direction == pytest.approx((1.0, 0.0), abs=1e-9) and gap < 2 * preview_gap()
    assert gear_states(window) == {"G1": "to build", "G2": "to build", "G3": "to build", "G4": "to build"}


def test_a_right_angle_gearbox_builds_to_turn_and_says_which_gear_to_drag(desk):
    from test_workbook_turned import bevel_reducer
    window = desk.open(bevel_reducer(), name="Bevel_Reducer.xlsx")
    window.press_build()
    desk.finish(window)
    assert window.status.get() == (
        "Built 4 parts, Bevel_Reducer_Layout and Bevel_Reducer.SLDASM; no interference between the gears where they "
        "stand. Its gears are mated to turn together, and SolidWorks reports no mate in error: drag G1 in SolidWorks "
        "and the rest of its train follow. 1 thing to do by hand: Assign a material to each of the 4 parts; the build "
        "leaves it unset.")
    box = record_of(window).gearbox
    assert box.kind == store.GEARBOX_MOTION and box.assembly
    assert {m.name: m.sense for m in box.mates if m.kind == motion.MESH} == {"G1 meshes G2": 1, "G3 meshes G4": 1}
    window.note = None
    window._refresh_state()
    assert window.status.get() == (
        "SolidWorks already matches the workbook on record; Update SolidWorks checks it live and puts right anything "
        "changed there; gears turned in SolidWorks stay where they are unless something must move. It was built with "
        "its gears mated to turn: drag G1 in SolidWorks and the rest of its train follow.")
    footer = window.footer()
    assert (footer.build_label, footer.build_enabled, footer.update_enabled, footer.update_primary) == (
        "Build again…", True, True, True)


TURNED_REFUSAL = ("G1 and G2 mesh across shafts at 90°, and which way a gear mate turns gears on shafts at an angle "
                  "is not settled by the probes for this version (findings.TURNED_GEAR_MATE_SENSE_READ_BACK), so the "
                  "gearbox is not built.")


def test_a_turned_mesh_the_probes_have_not_settled_offers_build_parts_and_nothing_else(desk, monkeypatch):
    """D16: refused before Build, with no static fallback, Build parts still offered — while the parts are not
    built, once they are, and on a gearbox built before the finding went away (Build again… greyed with the reason)."""
    from test_workbook_turned import bevel_reducer
    monkeypatch.setattr(findings, "TURNED_GEAR_MATE_SENSE_READ_BACK", None)
    window = desk.open(bevel_reducer(), name="Bevel_Reducer.xlsx")
    footer = window.footer()
    assert (footer.build_label, footer.build_enabled, footer.update_shown, footer.ok) == (
        "Build parts", True, False, True)
    assert window.status.get() == (f"Ready: Build parts makes 4 parts in {ui_text.short_path(str(desk.folder), 48)}. "
                                   + TURNED_REFUSAL)
    window.press_build()                                       # the window plans what the footer offers
    desk.finish(window)
    assert [os.path.basename(p) for p in desk.sw.saved_in(0)] == [
        "Bevel_m3_N20_M40.SLDPRT", "Bevel_m3_N40_M20.SLDPRT", "Gear_m2_N17.SLDPRT", "Gear_m2_N51.SLDPRT"]
    assert window.status.get() == ("Built 4 parts. 1 thing to do by hand: Assign a material to each of the 4 parts; "
                                   "the build leaves it unset.")
    record = record_of(window)
    assert len(record.parts) == 4 and record.gearbox is None
    window.note = None
    window._refresh_state()
    assert window.status.get() == "The 4 parts are built already, so Build parts has nothing to make. " + TURNED_REFUSAL
    footer = window.footer()
    assert (footer.build_label, footer.build_enabled) == ("Build parts", False)

    monkeypatch.setattr(findings, "TURNED_GEAR_MATE_SENSE_READ_BACK", "entity senses")
    other = desk.open(bevel_reducer(), name="Built.xlsx")    # its own gearbox, built while the finding was set
    other.press_build()
    desk.finish(other)
    assert record_of(other).gearbox.assembly
    monkeypatch.setattr(findings, "TURNED_GEAR_MATE_SENSE_READ_BACK", None)
    other.note = None
    other._plan()
    other._paint()
    footer = other.footer()
    assert other.status.get() == TURNED_REFUSAL and not footer.ok
    assert (footer.build_label, footer.build_enabled, footer.update_shown, footer.update_enabled) == (
        "Build again…", False, True, False)
    calls = len(desk.worker.calls)
    other.press_build()
    other.press_update()
    assert len(desk.worker.calls) == calls


def test_a_slanted_shaft_is_seen_from_its_own_plus_end(desk):
    from test_workbook_turned import crossed_slant
    window = desk.open(crossed_slant(), name="Crossed_Slant.xlsx")
    assert speed_lines(window) == [
        "S1    1000.0\u00a0rpm anticlockwise seen from the +Z end · 5.00\u00a0N·m",
        "S2    500.0\u00a0rpm anticlockwise seen from the +X end · 9.80\u00a0N·m",
        "S3    333.3\u00a0rpm anticlockwise seen from the (0.5,\u00a0−0.866,\u00a00) end · 14.41\u00a0N·m"]
    assert window.speeds_readout.get() == "seen from each shaft's + end"
    assert window.box_values["type"].cget("text") == ("Crossed and bevel train · 2 meshes · 3.000 : 1 · output at 90° "
                                                       "to the input")
    assert len(end_view_lines(window)) == 2                    # S2 along X and S3 slanted; S1 a cross
    direction, gap = shaft_line(window, "S3")                  # named at its plus end, (0.5, −0.866, 0)
    assert direction == pytest.approx((0.5, -math.sqrt(3) / 2), abs=1e-6) and gap < 2 * preview_gap()
    direction, _ = shaft_line(window, "S2")
    assert direction == pytest.approx((1.0, 0.0), abs=1e-9)
    assert window.footer().build_enabled


def test_a_crossed_shaft_moved_to_the_other_side_is_an_update_that_remakes_its_gear_mate(desk, monkeypatch):
    """D17: a move that turns a crossed mesh's sense round is an Update, which makes its gear mate again (with the
    remake route; without it the same edit needs Build again…)."""
    from test_workbook_turned import crossed_off_base
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_ROUTE", "remake")
    window = desk.open(crossed_off_base(), name="Crossed_Slant.xlsx")
    window.press_build()
    desk.finish(window)
    assert {m.name: m.sense for m in record_of(window).gearbox.mates if m.kind == motion.MESH} == {
        "G1 meshes G2": -1, "G3 meshes G4": 1}
    save_in_excel(window, {"Shafts": {"D2": 179.705628}})      # S1 to S2's other side
    assert window.status.get() == (
        "Update SolidWorks will move S1 in Crossed_Slant_Layout, remake the gear mate G1 meshes G2 (since S1 now passes "
        "S2 on its other side, so G1 and G2 turn the other way against each other), and re-place G1, G2, G3 and G4. "
        "It was built with its gears mated to turn: drag G1 in SolidWorks and the rest of its train follow.")
    window.press_update()
    desk.finish(window)
    assert window.status.get() == (
        "Updated SolidWorks: moved S1 in Crossed_Slant_Layout, remade the gear mate G1 meshes G2 (since S1 now passes "
        "S2 on its other side, so G1 and G2 turn the other way against each other), re-placed G1, G2, G3 and G4; no "
        "interference between the gears where they stand. Save Crossed_Slant_Layout and Crossed_Slant in SolidWorks "
        "to keep them.")
    assert {m.name: m.sense for m in record_of(window).gearbox.mates if m.kind == motion.MESH} == {
        "G1 meshes G2": 1, "G3 meshes G4": 1}
    assert window.update_plan.record_matches


def test_the_crossed_move_needs_build_again_while_a_gear_mate_cannot_be_made_again(desk):
    from test_workbook_turned import crossed_off_base
    window = desk.open(crossed_off_base(), name="Crossed_Slant.xlsx")
    window.press_build()
    desk.finish(window)
    save_in_excel(window, {"Shafts": {"D2": 179.705628}})
    assert window.status.get() == (
        "G2 now turns the other way against G1 about its axis, so the gear mate G1 meshes G2 must be made again, and "
        "making a gear mate again in a built assembly is not settled by the probes (findings.GEAR_MATE_RATIO_ROUTE), so "
        "the gearbox needs building again. Update SolidWorks offers to build again as Crossed_Slant_r2. " + TURNS)


def wrapped_lines(widget, text, width):
    """``text`` as Tk wraps it at ``width`` px in ``widget``'s font, line by line: laid out as a canvas text item
    (Tk's one text layout, the one a Label's wraplength uses) and read back a line at a time."""
    canvas = tk.Canvas(widget.master)
    item = canvas.create_text(0, 0, text=text, font=widget.cget("font"), width=width, anchor="nw")
    canvas.update_idletasks()
    height = canvas.bbox(item)[3]
    step = tk.font.Font(font=widget.cget("font")).metrics("linespace")
    starts = sorted({int(canvas.index(item, f"@0,{y + step // 2}")) for y in range(0, height, step)})
    canvas.destroy()
    return [text[a:b].strip() for a, b in zip(starts, starts[1:] + [len(text)])]


def test_a_wrapped_speeds_line_never_splits_a_number_from_its_unit_nor_a_slants_direction(desk):
    """The Speeds lines wrap at the end view's width (a shaft seen from an end other than +Z says so, and is longer
    than that); wrapped at any width down to a third of it, no number is parted from its unit and a slant's
    direction stays whole."""
    import tkinter.font  # noqa: F401 - wrapped_lines measures the label's font
    from gear_generator import workbook_gui
    from gear_generator.theme import px
    from test_workbook_turned import crossed_slant
    window = desk.open(crossed_slant(), name="Crossed_Slant.xlsx")
    labels = sorted(window.speeds_body.winfo_children(), key=lambda c: int(c.grid_info()["row"]))
    assert all(int(float(str(label.cget("wraplength")))) == px(workbook_gui.END_VIEW[0]) for label in labels)
    plain = lambda text: text.replace("\u00a0", " ")          # noqa: E731 - judged by what the eye reads
    whole = ["1000.0 rpm", "5.00 N·m", "500.0 rpm", "9.80 N·m", "333.3 rpm", "(0.5, −0.866, 0)", "14.41 N·m"]
    texts = [plain(label.cget("text")) for label in labels]
    assert all(any(piece in text for text in texts) for piece in whole)
    wrapped = 0
    for label, text in zip(labels, texts):
        for width in range(px(workbook_gui.END_VIEW[0]) // 3, px(workbook_gui.END_VIEW[0]) + 1, 8):
            lines = [plain(line) for line in wrapped_lines(label, label.cget("text"), width)]
            wrapped += len(lines) > 1
            for piece in (w for w in whole if w in text):
                assert any(piece in line for line in lines), (piece, width, lines)
    assert wrapped                                         # the widths tried do wrap the lines


def test_long_part_names_keep_their_cells_apart_and_the_window_its_width(desk):
    """Fixture B's two bevel parts are named for their mates and angle (…_S120), longer than the Part column: the
    table shows each by its head and end (C's ui_text.part_cell), the two apart, and the window keeps its width."""
    from gear_generator import workbook_gui
    from gear_generator.theme import px
    from test_workbook_turned import crossed_slant
    window = desk.open(crossed_slant(), name="Crossed_Slant.xlsx")
    parts = {}
    for cell in window.table.grid_slaves(column=6):
        row = int(cell.grid_info()["row"])
        if row:
            parts[window.table.grid_slaves(row=row, column=0)[0].cget("text")] = cell.cget("text")
    assert parts == {"G1": "Helical_m2_N20_45R", "G2": "Helical_m2_N40_45R", "G3": "Beve…_N20_M30_S120",
                     "G4": "Beve…_N30_M20_S120"}
    assert width_and_height(window)[0] == px(workbook_gui.WINDOW_WIDTH)
    assert window.winfo_reqwidth() <= px(workbook_gui.WINDOW_WIDTH)


def part_cells_drawn(window):
    """The Gears table's Part cells by gear as drawn, after the window has its size: each (text, drawn whole)."""
    width_and_height(window)
    window.update_idletasks()
    out = {}
    for cell in window.table.grid_slaves(column=6):
        row = int(cell.grid_info()["row"])
        if row:
            gear = window.table.grid_slaves(row=row, column=0)[0].cget("text")
            out[gear] = (cell.cget("text"), cell.winfo_width() == cell.winfo_reqwidth())
    return out


def test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left(desk, mode_findings):
    """Review of W8 item 5: a second workbook with the same Box name, built into the same output folder, makes its
    parts <stem>_r2, since the first's files are not its own. Beside TransferCase_Parallel's 8-character gear and
    shaft ids, "Sleeve_m1.5_N30_r2" (18 characters, at PART_CHARS) took the window to 1088 px. The Part column now
    shortens its cells to the room the other columns leave, measured in the table's fonts, by the head-and-tail rule:
    every cell is drawn whole, different parts read apart, and the window keeps its 1080 px."""
    from gear_generator import workbook_gui
    from gear_generator.theme import px
    from workbook_fixtures import transfer_case_parallel
    first = desk.open(transfer_case_parallel(), name="TransferCase_Parallel.xlsx")
    first.press_build()
    desk.finish(first)
    window = desk.open(transfer_case_parallel(), name="Second.xlsx")
    window.press_build()
    desk.finish(window)
    assert {os.path.basename(p.path) for p in record_of(window).parts} >= {
        "Sleeve_m1.5_N30_r2.SLDPRT", "Dog_m1.5_N30_r2.SLDPRT"}
    cells = part_cells_drawn(window)
    assert cells == {"InPin": ("Gear_m2_N17_r2", True), "InDog": ("Dog_m1.5_N30_r2", True),
                     "LayGear": ("Gear_m2_N34_r2", True), "LayPin": ("Gear_m2_N17_r2", True),
                     "LoGear": ("Gear_m2_N34_r2", True), "LoDog": ("Dog_m1.5_N30_r2", True),
                     "RangeSlv": ("Slee…m1.5_N30_r2", True), "FrontDog": ("Dog_m1.5_N30_r2", True),
                     "ModeSlv": ("Slee…m1.5_N30_r2", True), "FDrive": ("Gear_m2_N30_r2", True),
                     "FIdler": ("Gear_m2_N20_r2", True), "FOut": ("Gear_m2_N30_r2", True)}
    assert width_and_height(window)[0] == px(workbook_gui.WINDOW_WIDTH)
    assert window.winfo_reqwidth() <= px(workbook_gui.WINDOW_WIDTH)


def test_a_long_part_name_beside_long_ids_shows_whole_where_it_fits_and_the_window_keeps_its_width(desk):
    """Review of W8 item 5: "Sleeve_m1.25_N100" (17 characters, no revision suffix) beside TransferCase_Parallel's
    8-character ids fits the room the Part column has, so it shows whole, and the window keeps its 1080 px."""
    from gear_generator import workbook_gui
    from gear_generator.theme import px
    from workbook_fixtures import transfer_case_parallel
    spec = transfer_case_parallel()
    spec = model.replace(spec, gears=tuple(model.replace(g, module="1.25", teeth="100")
                                           if g.kind_word() in ("dog", "sleeve") else g for g in spec.gears))
    window = desk.open(spec, name="TransferCase_Parallel.xlsx")
    assert window.footer().ok, window.status.get()
    cells = part_cells_drawn(window)
    assert {g: cells[g] for g in ("RangeSlv", "ModeSlv", "InDog", "LoDog", "FrontDog")} == {
        "RangeSlv": ("Sleeve_m1.25_N100", True), "ModeSlv": ("Sleeve_m1.25_N100", True),
        "InDog": ("Dog_m1.25_N100", True), "LoDog": ("Dog_m1.25_N100", True), "FrontDog": ("Dog_m1.25_N100", True)}
    assert all(whole for _, whole in cells.values())
    assert width_and_height(window)[0] == px(workbook_gui.WINDOW_WIDTH)
    assert window.winfo_reqwidth() <= px(workbook_gui.WINDOW_WIDTH)


def test_short_ids_leave_the_part_cells_as_the_rows_give_them_at_part_chars(desk):
    """Review of W8 item 5: with the reducer's short ids, read and built, the Part column has room for PART_CHARS,
    so every cell is exactly what ui_text.workbook_gear_rows gives at its default, drawn whole, at 1080 px."""
    from gear_generator import workbook_gui
    from gear_generator.theme import px
    for window in (desk.open(name="Fresh.xlsx"), built(desk)):
        rows = ui_text.workbook_gear_rows(window.effective or window.reading.spec, window.parts, window.diagnostics,
                                          record=window.record, update=window.update_plan, plan=window.plan)
        assert part_cells_drawn(window) == {r[0]: (r[6] or "—", True) for r in rows}
        assert width_and_height(window)[0] == px(workbook_gui.WINDOW_WIDTH)
        assert window.winfo_reqwidth() <= px(workbook_gui.WINDOW_WIDTH)


# -- W7: a planetary stage ------------------------------------------------------------------------------------------
#
# W7-PLAN §4's fixtures as B's tests write them: the 4 : 1 with the ring held (sun in, carrier out, three planet
# copies, CarrierGear on the carrier), the sun held, the carrier held.


def carrier_circle(window):
    """The end view as the window drew it: the carrier's dashed circle (centre, radius) and the crosses' centres by
    the name set beside each (a cross shared by coaxial shafts carries every name)."""
    import math
    c = window.canvas
    (circle,) = [i for i in c.find_all() if c.type(i) == "oval" and c.itemcget(i, "dash")]
    x0, y0, x1, y1 = c.coords(circle)
    centre, radius = ((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0) / 2
    crosses = []
    for i in c.find_all():
        if c.type(i) == "line" and not c.itemcget(i, "arrow") in ("last", "first"):
            a, b, d, e = c.coords(i)
            if b == e and 0 < abs(d - a) < 20:                   # a cross's horizontal stroke
                crosses.append(((a + d) / 2, b))
    named = {}
    for i in c.find_all():
        if c.type(i) == "text":
            lx, ly = c.coords(i)
            named[c.itemcget(i, "text")] = min(crosses, key=lambda p: math.hypot(p[0] - lx, p[1] - ly))
    return centre, radius, named


def ring_rim(window):
    """The ring's rim as the window drew it (a plain oval, not the carrier's dashed one nor the origin's dot): its
    centre, and the drawing's scale in px per mm from the ring's outside radius as planning placed it."""
    c = window.canvas
    (rim,) = [i for i in c.find_all() if c.type(i) == "oval" and not c.itemcget(i, "dash")
              and not c.itemcget(i, "fill")]
    x0, y0, x1, y1 = c.coords(rim)
    return ((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0) / 2 / window.report.layout.placed["Ring"].outer_radius


def assert_carrier_round_its_axis(window, planet_x=18.0):
    """The end view's carrier, read off the canvas against the ring's rim (not against the copies it is drawn
    through): its circle about the cross S, C and R share, which is the ring's centre; its radius the workbook's
    planet X in the rim's scale; copy 1 that far to the right of it, as P's X, Y = (18, 0) puts it."""
    import math
    centre, radius, named = carrier_circle(window)
    (rx, ry), scale = ring_rim(window)
    assert named["S, C, R"] == pytest.approx(centre, abs=0.5) and centre == pytest.approx((rx, ry), abs=0.5)
    assert radius == pytest.approx(planet_x * scale, abs=0.5)
    assert named["P copy 1"] == pytest.approx((centre[0] + planet_x * scale, centre[1]), abs=0.5)
    for k in (2, 3):
        x, y = named[f"P copy {k}"]
        assert math.hypot(x - centre[0], y - centre[1]) == pytest.approx(planet_x * scale, abs=0.5)
    return centre, scale


def test_a_planetary_is_ready_to_build_with_its_carrier_drawn_through_its_planets(desk):
    from test_workbook_planetary import planetary_4to1
    window = desk.open(planetary_4to1(), name="Planetary_4to1.xlsx")
    footer = window.footer()
    assert (footer.build_label, footer.build_enabled, footer.update_shown, footer.ok) == ("Build", True, False, True)
    assert window.status.get() == (
        "Ready: Build makes 4 parts, Planetary_4to1_Layout, Planetary_4to1_C_Carrier and Planetary_4to1.SLDASM in "
        f"{ui_text.short_path(str(desk.folder), 48)}. Its turning gears are mated to their shafts and to each other, "
        "so they turn together in SolidWorks. C is built as a carrier of axes and planes only, turning with the 3 "
        "copies of Planet on it. Ring stays fixed where it is placed: its shaft does not turn.")
    assert window.box_values["type"].cget("text") == ("Planetary, R fixed · 3 planets · 4.000 : 1 · output turns the "
                                                       "same way")
    assert speed_lines(window) == [
        "S     1000.0 rpm anticlockwise · 2.00 N·m",
        "C     250.0 rpm anticlockwise · 7.76 N·m",
        "P     500.0 rpm clockwise, 750.0 rpm clockwise relative to C · 3 copies",
        "R     held still · 5.76 N·m"]
    # One row for the planet, its copies one part.
    assert gear_states(window) == {"Sun": "to build", "Planet": "to build", "Ring": "to build",
                                   "CarrierGear": "to build"}
    assert window.parts_readout.get() == "4 parts to build"
    # The end view: the carrier's dashed circle about the shared cross of S, C and R, through every copy's cross.
    assert_carrier_round_its_axis(window)


def test_a_carrier_off_the_origin_is_drawn_round_its_own_axis(desk):
    """S, C and R at (50, 20): the circle stands about their cross, not the origin, which is off the drawing."""
    from test_workbook_planetary import edited, planetary_4to1
    window = desk.open(edited(planetary_4to1(), shafts={k: dict(x="50", y="20") for k in "SCR"}),
                       name="Planetary_4to1.xlsx")
    assert window.footer().ok
    assert_carrier_round_its_axis(window)
    assert window.view_readout.get().endswith("origin off view")


def test_a_planetary_built_says_which_gear_to_drag_and_that_the_carrier_has_none(desk):
    from test_workbook_planetary import planetary_4to1
    window = desk.open(planetary_4to1(), name="Planetary_4to1.xlsx")
    window.press_build()
    desk.finish(window)
    assert [os.path.basename(p) for p in desk.sw.saved_in(0)] == [
        "Sun.SLDPRT", "Planet.SLDPRT", "Ring_m1_N54.SLDPRT", "CarrierGear.SLDPRT", "Planetary_4to1_Layout.SLDPRT",
        "Planetary_4to1_C_Carrier.SLDPRT", "Planetary_4to1.SLDASM"]
    assert window.status.get() == (
        "Built 4 parts, Planetary_4to1_Layout, Planetary_4to1_C_Carrier and Planetary_4to1.SLDASM; no interference "
        "between the gears where they stand. Its turning gears are mated to turn together, and SolidWorks reports no "
        "mate in error: drag Sun in SolidWorks and the rest of its train follow. The 3 copies of Planet turn on C, and "
        "Planetary_4to1_C_Carrier holds C's axes and planes only: a plate and pins are yours to add. Ring stays fixed "
        "where it is placed: its shaft does not turn. 1 thing to do by hand: Assign a material to each of the 4 parts; "
        "the build leaves it unset.")
    window.note = None
    window._refresh_state()
    assert window.status.get() == (
        "SolidWorks already matches the workbook on record; Update SolidWorks checks it live and puts right anything "
        "changed there; gears turned in SolidWorks stay where they are unless something must move. It was built with "
        "its gears mated to turn: drag Sun in SolidWorks and the rest of its train follow. C (the carrier) is axes and "
        "planes only, so it has nothing to drag.")
    assert gear_states(window) == {"Sun": "built", "Planet": "built", "Ring": "built", "CarrierGear": "built"}


@pytest.mark.parametrize("make, held, drag, lines, worked", [
    ("sun_held", "C is built as a carrier of axes and planes only, turning with the 3 copies of Planet on it. Sun "
                 "stays fixed where it is placed: its shaft does not turn.", "Ring",
     ["S     held still · 0.64 N·m", "C     750.0 rpm anticlockwise · 2.64 N·m",
      "P     1500.0 rpm anticlockwise, 750.0 rpm anticlockwise relative to C · 3 copies",
      "R     1000.0 rpm anticlockwise · 2.00 N·m"],
     "Planetary, S fixed · 3 planets · 1.333 : 1 · output turns the same way"),
    ("carrier_held", "C is built as axes and planes only, held fixed; the 3 copies of Planet turn on it. CarrierGear "
                     "stays fixed where it is placed: its shaft does not turn.", "Sun",
     ["S     1000.0 rpm anticlockwise · 2.00 N·m", "C     held still · 7.76 N·m",
      "P     1000.0 rpm clockwise, 1000.0 rpm clockwise relative to C · 3 copies",
      "R     333.3 rpm clockwise · 5.76 N·m"],
     "Planetary, C fixed · 3 planets · 3.000 : 1 · output turns the other way")])
def test_a_held_sun_and_a_held_carrier_say_what_is_held_and_what_to_drag(desk, make, held, drag, lines, worked):
    import test_workbook_planetary
    window = desk.open(getattr(test_workbook_planetary, make)(), name="Planetary_4to1.xlsx")
    assert window.status.get().endswith(". Its turning gears are mated to their shafts and to each other, so they "
                                        f"turn together in SolidWorks. {held}")
    assert_carrier_round_its_axis(window)          # whichever member is held, the carrier is drawn round its axis
    assert speed_lines(window) == lines and window.box_values["type"].cget("text") == worked
    window.press_build()
    desk.finish(window)
    assert f": drag {drag} in SolidWorks and the rest of its train follow." in window.status.get()
    assert record_of(window).gearbox.assembly


def test_what_w7_does_not_build_is_an_error_of_the_workbook_not_a_later_phase(desk):
    """W7-PLAN §1.2, as ruled: a planetary this version does not build is not waiting for a phase. Each arrives as an
    error at its cell (two inputs on a stage too, agreeing or not: W7-INTERFACES §6.15), and Checks shows exactly
    what is wrong and nothing for a later phase; Build waits, and Build parts is not offered for it."""
    from test_workbook_planetary import edited, planetary_4to1
    spec = planetary_4to1()
    cases = {
        "differential": (edited(spec, shafts={"R": dict(role="input", speed="200", torque="")}),
                         "Shafts!A3: S, C and R form a planetary stage with no member held: a differential is not "
                         "built by this version; set one of them to Role fixed."),
        "nested": (model.replace(spec, shafts=spec.shafts + (model.Shaft("Q", "P", "5", "0", row=6),)),
                   "Shafts!A6: Q is mounted on P, which is itself mounted on C: a carrier riding another carrier is "
                   "not built by this version; a planet shaft is built mounted on a frame shaft."),
        "helical": (edited(spec, gears={"Planet": dict(kind="helical", helix_angle="15", hand="left")}),
                    "Gears!A3: Planet is helical: a planetary stage is built with spur gears only by this version.",
                    "Meshes!A2: Sun is spur and Planet is helical; meshing gears are the same kind.",
                    "Meshes!A3: Planet is helical and Ring is spur; meshing gears are the same kind.",
                    "Gears!I3: Planet: The teeth overlap 0.82 of a pitch along the face, under one, which loses most of "
                    "the smoothness helical teeth are for; widen the face or raise the helix angle."),
        "two inputs": (edited(spec, shafts={"C": dict(role="input", speed="250")}),     # agreeing with S, still two
                       "Shafts!G3: C is an input as well as S, and both are members of C's planetary stage: one member "
                       "of a planetary stage is the input; set C's Role to output, or leave it blank."),
    }
    for name, (made, *shown_then) in cases.items():
        window = desk.open(made, name=f"{name}.xlsx")
        footer = window.footer()
        assert (footer.build_label, footer.build_enabled, footer.ok) == ("Build", False, False), name
        assert window.status.get().startswith(f"Fix the workbook before building: {shown_then[0]}"), name
        shown = [w.cget("text") for w in window.checks_body.winfo_children() if isinstance(w, tk.Label)]
        assert shown == shown_then and window.parts.refused == [], name


def test_a_torque_the_stage_does_not_settle_is_said_in_prose_after_the_speeds(desk):
    """C's Motion.torque_note: the last line of the Speeds panel is a sentence, set in prose and wrapped at the end
    view's width, so the right column keeps its width."""
    from gear_generator import workbook_gui
    from gear_generator.theme import px
    from test_workbook_planetary import edited, planetary_4to1
    window = desk.open(edited(planetary_4to1(), shafts={"R": dict(role="input", speed="200", torque="")}),
                       name="Differential.xlsx")
    labels = sorted(window.speeds_body.winfo_children(), key=lambda c: int(c.grid_info()["row"]))
    assert [label.cget("text") for label in labels][-1] == (
        "The torque through C's planetary stage is not worked out: with no member held, how it splits depends on the "
        "loads.")
    last, first = labels[-1], labels[0]
    assert str(last.cget("font")) != str(first.cget("font"))                 # prose, not the lines' mono
    assert int(float(str(last.cget("wraplength")))) == px(workbook_gui.END_VIEW[0])
    assert width_and_height(window)[0] == px(workbook_gui.WINDOW_WIDTH)


def test_an_update_of_a_planetary_re_places_the_ring_the_carrier_and_the_planets(desk):
    from test_workbook_planetary import planetary_4to1
    window = desk.open(planetary_4to1(), name="Planetary_4to1.xlsx")
    window.press_build()
    desk.finish(window)
    save_in_excel(window, {"Gears": {"C4": 12}})                  # Ring's At 10 -> 12: the held member moves
    assert window.status.get() == (
        "Update SolidWorks will re-place Ring, C (the carrier), Sun, Planet (3 copies) and CarrierGear. It was built "
        "with its gears mated to turn: drag Sun in SolidWorks and the rest of its train follow. C (the carrier) is "
        "axes and planes only, so it has nothing to drag.")
    window.press_update()
    desk.finish(window)
    assert window.status.get() == (
        "Updated SolidWorks: re-placed Ring, C (the carrier), Sun, Planet (3 copies) and CarrierGear; no interference "
        "between the gears where they stand. Save Planetary_4to1 in SolidWorks to keep it.")
    assert desk.sw.locked_puts == [] and window.update_plan.record_matches


def test_moving_the_planets_is_an_update_of_the_carrier_part(desk, monkeypatch):
    """W7-PLAN §6 p3's edit: Sun 21, Ring 57 and P's X 19.5, which keep both centres; with the remake route the
    gear mates are set to their new ratios and the carrier part's planet axes move."""
    from test_workbook_planetary import planetary_4to1
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_ROUTE", "remake")
    window = desk.open(planetary_4to1(), name="Planetary_4to1.xlsx")
    window.press_build()
    desk.finish(window)
    save_in_excel(window, {"Gears": {"F2": 21, "F4": 57}, "Shafts": {"C4": 19.5}})
    window.press_update()
    desk.finish(window)
    text = window.status.get()
    assert text.startswith("Updated SolidWorks: changed 1 variable in Sun, changed 1 variable in Ring_m1_N54 (it now "
                           "has 57 teeth; its file keeps its name), moved the planets on C in "
                           "Planetary_4to1_C_Carrier, set the gear mates Sun meshes Planet copy 1 to 21 : 18, ")
    assert text.endswith("Save Sun, Ring_m1_N54, Planetary_4to1_C_Carrier and Planetary_4to1 in SolidWorks to keep "
                         "them.")


# -- W8: a gearbox with modes ---------------------------------------------------------------------------------------


def shifted(spec, dx, dy):
    """``spec`` with every frame shaft moved by (dx, dy) mm, so nothing the end view draws is at the origin."""
    return model.replace(spec, shafts=tuple(
        model.replace(s, x=f"{float(s.x) + dx:g}", y=f"{float(s.y) + dy:g}") if s.mount() == "frame" else s
        for s in spec.shafts))


def chooser_cells(window):
    """The mode chooser's segments as drawn, row by row and left to right: (cell, its label)."""
    out = []
    for segmented in window.mode_choosers:
        cells = sorted(segmented.winfo_children(), key=lambda c: int(c.grid_info()["column"]))
        out += [(c, c.winfo_children()[0]) for c in cells]
    return out


def chooser(window):
    """The Speeds panel's mode chooser as drawn: each segment's text, in order, and which is chosen."""
    if not window.mode_choosers:
        return [], ""
    return [label.cget("text") for _, label in chooser_cells(window)], window.mode.get()


def choose_mode(window, name):
    """A click on the segment ``name`` (the Segmented's own handler, as its <Button-1> binding calls it)."""
    owner = next(s for s in window.mode_choosers if name in s._values)  # noqa: SLF001 - the binding's target
    owner._choose(name)  # noqa: SLF001 - the window is withdrawn, so no click reaches it


def colours_of(window, gear):
    """The outline colours the end view drew ``gear`` in (its outline and, for a ring or sleeve, its rim)."""
    c = window.canvas
    return {c.itemcget(i, "outline") for i in c.find_withtag(gear)}


def rim_centre(window, gear):
    c = window.canvas
    (rim,) = [i for i in c.find_withtag(gear) if c.type(i) == "oval"]
    x0, y0, x1, y1 = c.coords(rim)
    return (x0 + x1) / 2, (y0 + y1) / 2


def crosses_named(window):
    """Each label's text and the centre of the shaft cross nearest it."""
    c = window.canvas
    crosses = []
    for i in c.find_all():
        if c.type(i) == "line" and not c.itemcget(i, "arrow") in ("last", "first"):
            a, b, d, e = c.coords(i)
            if b == e and 0 < abs(d - a) < 20:                   # a cross's horizontal stroke
                crosses.append(((a + d) / 2, b))
    named = {}
    for i in c.find_all():
        if c.type(i) == "text":
            lx, ly = c.coords(i)
            named[c.itemcget(i, "text")] = min(crosses, key=lambda p: math.hypot(p[0] - lx, p[1] - ly))
    return named


PARALLEL_SPEEDS = {
    "2H": ["2H: Rear 1500\u00a0rpm · Front not driven · 1.000 : 1", "In 2H, RangeSlv engages InDog.",
           "In    1500.0\u00a0rpm anticlockwise · 10.00\u00a0N·m", "Lay   750.0\u00a0rpm clockwise",
           "Lo    375.0\u00a0rpm anticlockwise", "Rear  1500.0\u00a0rpm anticlockwise · 10.00\u00a0N·m",
           "FrontDrv  turns freely", "Idler  turns freely", "Front  turns freely"],
    "N": ["N: neutral — Rear, FrontDrv, Idler and Front turn freely.", "In N, no sleeve engages a dog.",
          "In    1500.0\u00a0rpm anticlockwise · 10.00\u00a0N·m", "Lay   750.0\u00a0rpm clockwise",
          "Lo    375.0\u00a0rpm anticlockwise", "Rear  turns freely", "FrontDrv  turns freely", "Idler  turns freely",
          "Front  turns freely"],
    "4L": ["4L: Rear 375\u00a0rpm · Front 375\u00a0rpm · 4.000 : 1",
           "In 4L, RangeSlv engages LoDog and ModeSlv engages FrontDog.",
           "In    1500.0\u00a0rpm anticlockwise · 10.00\u00a0N·m", "Lay   750.0\u00a0rpm clockwise · 19.60\u00a0N·m",
           "Lo    375.0\u00a0rpm anticlockwise · 38.42\u00a0N·m",
           "Rear  375.0\u00a0rpm anticlockwise · 38.42\u00a0N·m, shared with FrontDrv (the share depends on the loads)",
           "FrontDrv  375.0\u00a0rpm anticlockwise · — (past a split)",
           "Idler  562.5\u00a0rpm clockwise · — (past a split)",
           "Front  375.0\u00a0rpm anticlockwise · — (past a split)"]}


def test_a_gearbox_with_modes_has_a_mode_chooser_and_the_speeds_panel_shows_the_chosen_mode(desk):
    """W8-PLAN §1.12 (J21): the Speeds panel's header gets one segment per Modes row, the first chosen; the panel
    shows that mode's speeds, torques and ratio, and a member the mode leaves free turns freely (J16)."""
    from workbook_fixtures import transfer_case_parallel
    window = desk.open(transfer_case_parallel(), name="TransferCase_Parallel.xlsx")
    assert window.footer().ok and window.footer().build_label == "Build"
    assert window.counts.get() == "7 shafts · 12 gears · 4 meshes · 4 modes"
    nb = "\u00a0"                                   # B's no-break spaces hold each mode's ratio together
    assert window.box_values["type"].cget("text") == (f"Parallel train with modes · 4 meshes · 2H{nb}1.000{nb}:{nb}1, "
                                                       f"4H{nb}1.000{nb}:{nb}1, N{nb}neutral, 4L{nb}4.000{nb}:{nb}1")
    assert chooser(window) == (["2H", "4H", "N", "4L"], "2H")
    only_here = "The mode chosen here changes only what this window shows."     # nothing built yet
    assert speed_lines(window) == PARALLEL_SPEEDS["2H"] + [only_here] and window.speeds_readout.get() == "seen from +Z"
    for name in ("N", "4L"):
        choose_mode(window, name)
        assert chooser(window) == (["2H", "4H", "N", "4L"], name)
        assert speed_lines(window) == PARALLEL_SPEEDS[name] + [only_here], name
    # The first two lines and the last are prose (ui_text.speeds_prose_rows), the shafts' lines mono.
    fonts = [str(w.cget("font")) for w in sorted(window.speeds_body.winfo_children(),
                                                 key=lambda c: int(c.grid_info()["row"]))]
    assert fonts[0] == fonts[1] == fonts[-1] == str(window.fonts.hint)
    assert set(fonts[2:-1]) == {str(window.fonts.mono_tiny)}


def test_a_gearbox_with_no_modes_has_no_chooser(desk):
    window = desk.open()
    assert chooser(window) == ([], "") and window.mode_choosers == []


def with_modes(spec, names, extra=()):
    """``spec`` (a transfer case) with its four modes renamed ``names`` and ``extra`` modes ((name, range, mode))
    after them, in Modes-sheet order."""
    from gear_generator.workbook.model import Mode
    modes = [model.replace(m, name=n) for m, n in zip(spec.modes, names)]
    row = len(modes) + 2
    for name, rng, drive in extra:
        modes.append(Mode(name, (("RangeSlv", rng), ("ModeSlv", drive)), "", row=row))
        row += 1
    return model.replace(spec, modes=tuple(modes))


def six_modes():
    from workbook_fixtures import transfer_case_parallel
    return with_modes(transfer_case_parallel(), ("HighRange2WD", "HighRange4WD", "Neutral", "LowRange4WD"),
                      (("Neutral4WD", "N", "4WD"), ("LowRange2WD", "L", "2WD")))


@pytest.mark.parametrize("make", ["reducer", "parallel", "e4", "long_names", "six"])
def test_the_window_keeps_its_width_with_modes_and_every_mode_name_shows_whole(desk, make):
    """W8 review: "Worked out as" names every mode's ratio and wraps in its cell; the Gears table keeps within its
    column; the chooser sizes each segment to the longest name and, when they would not fit the header, goes in
    rows at the Speeds panel's top. So the window keeps its 1080 px, and no segment's name is wider than its cell."""
    from gear_generator import workbook_gui
    from gear_generator.theme import px
    from workbook_fixtures import e4_transfer_case, transfer_case_parallel
    spec = {"reducer": reducer, "parallel": transfer_case_parallel, "e4": e4_transfer_case,
            "long_names": lambda: with_modes(transfer_case_parallel(), ("Road", "AllWheel", "Towing", "CrawlLow")),
            "six": six_modes}[make]()
    window = desk.open(spec, name="Box.xlsx")
    assert window.footer().ok, window.status.get()
    for segmented in window.mode_choosers:          # each segment's share of its row, less the 2 px between
        share = int(segmented.cget("width")) / len(segmented._values) - px(2)  # noqa: SLF001 - its names
        for name in segmented._values:  # noqa: SLF001
            assert window.fonts.mono_bold.measure(name) <= share, name          # chosen: bold, the widest
    assert width_and_height(window)[0] == px(workbook_gui.WINDOW_WIDTH)
    assert window.winfo_reqwidth() <= px(workbook_gui.WINDOW_WIDTH)
    names = [m.name for m in spec.modes]
    assert chooser(window) == (names, names[0] if names else "")


def with_a_turned_shaft(spec):
    """``spec`` with a shaft along X that carries nothing (Checks warn of it, nothing more): the Speeds readout then
    reads *seen from each shaft's + end*, the widest it has."""
    from gear_generator.workbook.model import Shaft
    return model.replace(spec, shafts=spec.shafts + (Shaft("Aux", "frame", "200", "0", "0", "X+", "", row=9),))


@pytest.mark.parametrize("five, turned, in_header", [
    (False, False, True),       # 2H 4H N 4L: 4 × 32 px beside "seen from +Z · provisional"
    (True, False, False),       # five 3-letter names, 5 × 40 = 200 px: no room beside "seen from +Z · provisional"
    (False, True, False),       # 128 px: no room beside "seen from each shaft's + end · provisional"
    (True, True, False)])
def test_the_speeds_readout_is_never_clipped_by_the_mode_chooser(desk, five, turned, in_header):
    """W8 review S2: the Speeds panel's header does not grow, so the chooser takes it only when it fits beside the
    title and the widest readout the panel can show (any mode's, with the provisional tag), as measured in the
    header's own fonts; else it goes in rows. Every mode chosen, with Excel's recalculation pending and not, the
    readout is drawn whole and a chooser in the header ends inside it, and the window keeps its 1080 px."""
    from gear_generator import workbook_gui
    from gear_generator.theme import px
    from workbook_fixtures import transfer_case_parallel
    spec = transfer_case_parallel()
    spec = with_modes(spec, ("2Hi", "4Hi", "Neu", "4Lo"), (("L2W", "L", "2WD"),)) if five else spec
    spec = with_a_turned_shaft(spec) if turned else spec
    window = desk.open(spec, name="Box.xlsx")
    assert window.footer().ok, window.status.get()
    names = [m.name for m in spec.modes]
    header, slot, readout = window._speeds.header, window._mode_slot, window._speeds.readout_label
    widest = "seen from each shaft's + end" if turned else "seen from +Z"
    for recalc in (False, True):
        window.recalc = recalc
        for name in names:
            if name != window.mode.get():
                choose_mode(window, name)
            window._paint()
            window.update_idletasks()
            assert window.speeds_readout.get() == widest + ui_text.provisional_tag(recalc)
            assert readout.winfo_width() == readout.winfo_reqwidth(), (recalc, name)        # drawn whole
            (row,) = window.mode_choosers                                   # one row, in the header or not
            assert (row.master is slot) == in_header and (row.master is window._mode_rows) != in_header
            if in_header:
                assert row.winfo_width() == row.winfo_reqwidth() == px(32 * 4)
                assert readout.winfo_x() + readout.winfo_width() <= slot.winfo_x()
                assert slot.winfo_x() + slot.winfo_width() <= header.winfo_width() - px(12)
    assert width_and_height(window)[0] == px(workbook_gui.WINDOW_WIDTH)
    assert chooser(window) == (names, names[-1])


def test_a_save_that_turns_a_shaft_moves_the_chooser_to_rows_and_back_keeping_the_chosen_mode(
        desk, tk_callback_exceptions):
    """W8 review of the C/D fixes, S2: the chooser is rebuilt when it moves between the header and rows, not only
    when the names change. A shaft saved along X widens the readout to *seen from each shaft's + end*, so the same
    four modes no longer fit beside it and go to rows; the shaft removed again brings them back to the header.
    Each way the chosen mode is kept, the old row's trace goes with it, and the readout is drawn whole."""
    from workbook_fixtures import transfer_case_parallel
    window = desk.open(transfer_case_parallel(), name="TransferCase_Parallel.xlsx")
    names = ["2H", "4H", "N", "4L"]
    readout = window._speeds.readout_label

    def placed(in_header, chosen, widest):
        window.update_idletasks()
        (row,) = window.mode_choosers
        assert (row.master is window._mode_slot) == in_header
        assert (row.master is window._mode_rows) != in_header
        assert chooser(window) == (names, chosen)
        assert len(window.mode.trace_info()) == len(window.mode_choosers)
        assert window.speeds_readout.get() == widest + ui_text.provisional_tag(window.recalc)
        assert readout.winfo_width() == readout.winfo_reqwidth()                 # drawn whole

    placed(True, "2H", "seen from +Z")
    choose_mode(window, "4L")
    save_in_excel(window, {"Shafts": {"A9": "Aux", "B9": "frame", "C9": 200, "D9": 0, "E9": 0, "F9": "X+"}})
    assert window.footer().ok, window.status.get()
    assert [s.id for s in window.reading.spec.shafts][-1] == "Aux"
    placed(False, "4L", "seen from each shaft's + end")
    choose_mode(window, "N")
    save_in_excel(window, {"Shafts": {"A9": None, "B9": None, "C9": None, "D9": None, "E9": None, "F9": None}},
                  seconds=4)
    assert window.footer().ok, window.status.get()
    assert "Aux" not in [s.id for s in window.reading.spec.shafts]
    placed(True, "N", "seen from +Z")
    assert tk_callback_exceptions == []


def test_a_mode_renamed_only_in_case_keeps_its_choice(desk):
    """Mode names compare ignoring case (J6, W8-INTERFACES §9.6): 4L saved as 4l is the same mode, still chosen."""
    from workbook_fixtures import transfer_case_parallel
    window = desk.open(transfer_case_parallel(), name="TransferCase_Parallel.xlsx")
    choose_mode(window, "4L")
    save_in_excel(window, {"Modes": {"A5": "4l"}})
    assert chooser(window) == (["2H", "4H", "N", "4l"], "4l")
    assert speed_lines(window)[0] == "4l: Rear 375\u00a0rpm · Front 375\u00a0rpm · 4.000 : 1"
    assert len(window.mode.trace_info()) == len(window.mode_choosers)   # the old choosers' traces went with them


def test_a_segmented_row_destroyed_takes_its_trace_on_the_variable_with_it(desk, tk_callback_exceptions):
    """W8 review S1: the variable outlives the row (the window's mode chooser is rebuilt over the same ``mode``), so
    the row removes its trace when destroyed; a trace left behind would paint destroyed cells on the next write,
    a TclError reported from the Tk callback."""
    from gear_generator.widgets import Segmented
    variable = tk.StringVar(desk.root, "a")
    row = Segmented(desk.root, variable, ("a", "b"))
    assert len(variable.trace_info()) == 1
    row.destroy()
    assert variable.trace_info() == []
    variable.set("b")
    desk.root.update_idletasks()
    assert tk_callback_exceptions == []


def test_the_end_view_stands_each_sleeve_on_the_face_of_the_dog_its_mode_engages(desk):
    """A slide runs along the view, so the end view shows the chosen mode by each slider's face height, which picks
    its colour: a sleeve over a dog is on that dog's face, in that dog's colour, and over none in a colour of no dog
    it could engage. The fixture is moved off the origin; each sleeve's rim stands on the cross its shaft shares
    with the dogs' shafts."""
    from workbook_fixtures import transfer_case_parallel
    window = desk.open(shifted(transfer_case_parallel(), 150, 120), name="TransferCase_Parallel.xlsx")
    engaged = {"2H": {"RangeSlv": "InDog"}, "4H": {"RangeSlv": "InDog", "ModeSlv": "FrontDog"}, "N": {},
               "4L": {"RangeSlv": "LoDog", "ModeSlv": "FrontDog"}}
    dogs = {"RangeSlv": ("InDog", "LoDog"), "ModeSlv": ("FrontDog",)}
    for mode in ("2H", "4H", "N", "4L"):
        choose_mode(window, mode) if mode != window.mode.get() else None
        for sleeve, its_dogs in dogs.items():
            for dog in its_dogs:
                same = colours_of(window, sleeve) == colours_of(window, dog)
                assert same == (engaged[mode].get(sleeve) == dog), (mode, sleeve, dog)
        named = crosses_named(window)
        for sleeve in ("RangeSlv", "ModeSlv"):
            assert rim_centre(window, sleeve) == pytest.approx(named["In, Lo, Rear,\nFrontDrv"], abs=0.5), mode
    assert window.view_readout.get().endswith("origin off view")


def test_the_chosen_mode_is_kept_across_a_save_while_a_mode_of_that_name_is_there(desk):
    """W8-PLAN §1.12: the choice survives a re-read; a mode renamed away takes the chooser back to the first."""
    from workbook_fixtures import transfer_case_parallel
    window = desk.open(transfer_case_parallel(), name="TransferCase_Parallel.xlsx")
    choose_mode(window, "4L")
    save_in_excel(window, {"Box": {"B8": 97}})                       # the efficiency: a change, the modes the same
    assert chooser(window) == (["2H", "4H", "N", "4L"], "4L")
    assert speed_lines(window)[0] == "4L: Rear 375\u00a0rpm · Front 375\u00a0rpm · 4.000 : 1"
    save_in_excel(window, {"Modes": {"A5": "Low"}}, seconds=4)       # 4L renamed: no mode of that name now
    assert chooser(window) == (["2H", "4H", "N", "Low"], "2H")
    assert speed_lines(window)[0] == "2H: Rear 1500\u00a0rpm · Front not driven · 1.000 : 1"


def test_a_gearbox_with_modes_builds_one_configuration_per_mode_and_says_where_a_turn_shows(desk, mode_findings):
    """W8-PLAN §1.8, §1.12: Build makes the configurations; the footer after it says how to switch mode in
    SolidWorks, and — from the build result's ``positions_per_configuration``, which the window passes on
    (W8-INTERFACES §9.12) — that a turn stays in its configuration. A window opened afresh has no job's answer, so
    it makes neither claim. The chooser is the window's own: choosing a mode presses nothing in SolidWorks."""
    from workbook_fixtures import transfer_case_parallel
    window = desk.open(transfer_case_parallel(), name="TransferCase_Parallel.xlsx")
    window.press_build()
    desk.finish(window)
    assert window.positions_per_configuration is True
    status = window.status.get()
    assert status.startswith("Built 6 parts, TransferCase_Parallel_Layout and TransferCase_Parallel.SLDASM; no "
                             "interference between the gears in any mode, where they stand. Its gears are mated to "
                             "turn in each of its 4 modes, one configuration each (2H, 4H, N and 4L), and SolidWorks "
                             "reports no mate in error in any of them: it opens in 2H; ")
    stays = ui_text.turning_note(True)            # C's one home of the sentence (W8-INTERFACES §6.7)
    assert stays and stays in status
    assert record_of(window).gearbox.modes == ["2H", "4H", "N", "4L"]
    calls = len(desk.sw.calls)
    choose_mode(window, "4L")
    assert len(desk.sw.calls) == calls and chooser(window) == (["2H", "4H", "N", "4L"], "4L")
    assert speed_lines(window)[-1] == ("The mode chosen here changes only what this window shows; it does not switch "
                                       "the mode SolidWorks shows.")
    window.note = None
    window._refresh_state()
    on_record = window.status.get()
    assert stays in on_record
    again = desk.open(path=window.link.path)
    assert again.positions_per_configuration is None
    expected = on_record                          # the same sentence, without either claim about a turn
    for claim in (ui_text.turning_note(True), ui_text.switching_note(True)):
        expected = expected.replace(f" {claim}", "") if claim else expected
    assert again.status.get() == expected and stays not in expected


def test_on_2026_a_built_gearbox_with_modes_says_a_turn_can_show_in_other_modes_and_the_footer_holds_it(
        desk, mode_findings, monkeypatch):
    """W8-INTERFACES §9.18: the twin of the test above with TURN_PER_CONFIGURATION_ON_2026 as committed (False, W8's
    s2 and s7: a turn of the mated train can show in other modes), which ``mode_findings`` pins True. The build's
    answer is False, so the footer says the shared-turn sentence a user on SolidWorks 2026 sees and not the switching
    one; the window keeps its 1080 px and grows taller to hold the sentence whole, its label drawn at the size it
    asks."""
    from gear_generator import workbook_gui
    from gear_generator.theme import px
    from workbook_fixtures import transfer_case_parallel
    monkeypatch.setattr(findings, "TURN_PER_CONFIGURATION_ON_2026", False)
    window = desk.open(transfer_case_parallel(), name="TransferCase_Parallel.xlsx")
    window.press_build()
    desk.finish(window)
    assert window.positions_per_configuration is False
    assert window.status.get() == (
        "Built 6 parts, TransferCase_Parallel_Layout and TransferCase_Parallel.SLDASM; no interference between the "
        "gears in any mode, where they stand. Its gears are mated to turn in each of its 4 modes, one configuration "
        "each (2H, 4H, N and 4L), and SolidWorks reports no mate in error in any of them: it opens in 2H; to switch "
        "mode, double-click another mode's configuration in SolidWorks' ConfigurationManager. Drag InPin in "
        "SolidWorks to turn one train and FrontDog to turn the other. RangeSlv and ModeSlv slide along Rear, each to "
        "its place in each mode. A turn you give the gears in one mode can show in other modes, so a dog can stand "
        "across its sleeve in another; to put the gears back there, press Update SolidWorks with that mode showing. "
        "1 thing to do by hand: Assign a material to each of the 6 parts; the build leaves it unset.")
    assert ui_text.turning_note(False) == ui_text.TURN_CAN_SHOW_ELSEWHERE and ui_text.switching_note(False) == ""
    width, height = width_and_height(window)
    assert width == px(workbook_gui.WINDOW_WIDTH) and window.winfo_reqwidth() <= px(workbook_gui.WINDOW_WIDTH)
    assert height == window.winfo_reqheight()
    window.update_idletasks()
    label = window.status_label
    assert (label.winfo_width(), label.winfo_height()) == (label.winfo_reqwidth(), label.winfo_reqheight())
    assert label.winfo_reqwidth() <= int(str(label.cget("wraplength"))) + px(4)      # wrapped, not widening


def test_on_2026_a_quiet_update_that_finds_the_gears_turned_in_step_warns_of_the_other_modes(desk, mode_findings,
                                                                                            monkeypatch):
    """W8-INTERFACES §9.18 (the review of its commits, point 1) through the window, on the fake's shared variant with
    the turn finding as committed (2026: a turn can show in other modes): the 2H train turned 37°, in step in 2H, and
    Update pressed there puts nothing and shows no other mode. The footer shows its status alone, so the status says
    another mode may stand with a dog across its sleeve; it is shown whole, and the window keeps its 1080 px."""
    from gear_generator import workbook_gui
    from gear_generator.theme import px
    from workbook_fixtures import transfer_case_parallel
    monkeypatch.setattr(findings, "TURN_PER_CONFIGURATION_ON_2026", False)
    desk.sw.shared_positions = True
    window = desk.open(transfer_case_parallel(), name="TransferCase_Parallel.xlsx")
    window.press_build()
    desk.finish(window)
    # The 2H train turned 37° on In, in step: Lay at -1/2, Lo at +1/4 (17 : 34 twice), Rear coupled to In by InDog.
    for gear, k in {"InPin": 1, "InDog": 1, "LayGear": -0.5, "LayPin": -0.5, "LoGear": 0.25, "LoDog": 0.25,
                    "RangeSlv": 1, "ModeSlv": 1}.items():
        desk.sw.turn(name2(window, gear), 37.0 * k)
    window.press_update()
    desk.finish(window)
    assert window.status.get() == (
        "SolidWorks already matches the workbook: nothing was changed. The gears stand where they were turned in "
        "SolidWorks. This version of SolidWorks can show that turn in other modes, so a dog may stand across its "
        "sleeve in another; to put the gears back there, press Update SolidWorks with that mode showing. It worked "
        "in 2H, the configuration that was active; it did not show the other modes, since nothing in 2H needed "
        "changing.")
    width, height = width_and_height(window)
    assert width == px(workbook_gui.WINDOW_WIDTH) and window.winfo_reqwidth() <= px(workbook_gui.WINDOW_WIDTH)
    assert height == window.winfo_reqheight()
    window.update_idletasks()
    label = window.status_label
    assert (label.winfo_width(), label.winfo_height()) == (label.winfo_reqwidth(), label.winfo_reqheight())
    assert label.winfo_reqwidth() <= int(str(label.cget("wraplength"))) + px(4)      # wrapped, not widening


QUIET_UPDATE_WITH_MODES = ("SolidWorks already matches the workbook: nothing was changed. It worked in 2H, the "
                           "configuration that was active; it did not show the other modes, since nothing in 2H "
                           "needed changing.")


@pytest.mark.parametrize("suppressed_read, unread", [
    ("answers, marks nothing", ""),
    (None, " Which way RangeSlv and LoDog, and ModeSlv and FrontDog, turn against each other was not checked this "
           "time: their mates are switched off in 2H, the mode SolidWorks is showing, and are checked when an Update "
           "works in a mode that has them on.")])
def test_a_quiet_update_and_a_modes_pick_changed_update_a_gearbox_with_modes(desk, mode_findings, monkeypatch,
                                                                             suppressed_read, unread):
    """W8-PLAN §1.10 and J14 through the window, on the fake: a quiet Update says which mode it worked in and that
    it did not show the others (W8-INTERFACES §9.11); a Modes pick changed between existing positions (4H's ModeSlv
    4WD → 2WD) is an Update that sets that mode's slide value and switches its coupling off, and the Speeds panel
    reads the new 4H. With a suppressed gear mate's sense readable (findings.SUPPRESSED_GEAR_MATE_SENSE_READ as
    committed) the quiet Update reads every pair's turning and says nothing of it; with the finding unset it names
    the pairs whose mates are off in the mode shown as not checked (W8-INTERFACES §9.16)."""
    from workbook_fixtures import transfer_case_parallel
    monkeypatch.setattr(findings, "SUPPRESSED_GEAR_MATE_SENSE_READ", suppressed_read, raising=False)
    window = desk.open(transfer_case_parallel(), name="TransferCase_Parallel.xlsx")
    window.press_build()
    desk.finish(window)
    window.press_update()
    desk.finish(window)
    assert window.status.get() == QUIET_UPDATE_WITH_MODES + unread
    save_in_excel(window, {"Modes": {"C3": "2WD"}})
    footer = window.footer()
    assert (footer.build_label, footer.update_enabled, footer.update_primary) == ("Build again…", True, True)
    assert window.status.get().startswith("Update SolidWorks will move ModeSlv in 4H to 96 mm along Rear, and switch "
                                          "the mate ModeSlv engages FrontDog off in 4H. ")
    choose_mode(window, "4H")
    assert speed_lines(window)[:2] == ["4H: Rear 1500\u00a0rpm · Front not driven · 1.000 : 1",
                                       "In 4H, RangeSlv engages InDog."]
    window.press_update()
    desk.finish(window)
    assert window.status.get() == (
        "Updated SolidWorks: moved ModeSlv in 4H to 96 mm along Rear, switched the mate ModeSlv engages FrontDog off "
        "in 4H, re-placed InPin, InDog, LayGear, LayPin, LoGear, LoDog, RangeSlv, FrontDog, ModeSlv, FDrive, FIdler "
        "and FOut in every mode; no interference between the gears in any mode, where they stand. It worked in 2H, "
        "the configuration that was active, then showed and checked 4H, N and 4L and left the assembly in 2H. Save "
        "TransferCase_Parallel in SolidWorks to keep it.")
    assert chooser(window) == (["2H", "4H", "N", "4L"], "4H")          # the window's choice, not SolidWorks' mode


def test_the_strip_refuses_a_sleeves_part_record_and_keeps_its_form(desk, tmp_path):
    """W8-PLAN §1.1 (review S9): a sleeve's or dog's .gear.json, opened in the strip, is refused with C's sentence;
    the form keeps what it had and nothing is remembered for Update values. A spur gear's record opens as always."""
    from gear_generator import gui
    from gear_generator.spec import GearSpec
    app = gui.GearApp(desk.root)
    teeth_before = app.gear_vars["a"]["teeth"].get()
    for kind, stem in (("sleeve", "Sleeve_m1.5_N30"), ("dog", "Dog_m1.5_N30")):
        part = str(tmp_path / f"{stem}.SLDPRT")
        spec = GearSpec(module="1.5", teeth="30", face_width="8", kind=kind,
                        teeth_side="internal" if kind == "sleeve" else "external")
        record = store.GearRecord(kind=kind, spec=spec.to_dict())
        store.save(store.sidecar_path(part), store.Sidecar(part_path=part, record=record))
        app._load_record(store.sidecar_path(part))
        assert app.status.get() == f"{stem}.SLDPRT is a {kind} made from a gearbox workbook; open that workbook to " \
                                   "change it.", kind
        assert app._loaded is None and app.gear_vars["a"]["teeth"].get() == teeth_before, kind
    part = str(tmp_path / "Gear_m2_N40.SLDPRT")
    spur = GearSpec(module="2", teeth="40", face_width="10")
    store.save(store.sidecar_path(part), store.Sidecar(part_path=part, record=store.GearRecord(spec=spur.to_dict())))
    app._load_record(store.sidecar_path(part))
    assert app.status.get().startswith("Opened Gear_m2_N40.gear.json.")
    assert app._loaded is not None and app.gear_vars["a"]["teeth"].get() == "40"



# -- W9a package B: the user's work through the window ---------------------------------------------------------------


def test_an_update_refused_over_the_users_work_is_recorded_and_the_footer_says_it_with_its_time(desk, monkeypatch):
    """K4 through the window: a Bore the user typed in SolidWorks refuses the press before anything changes (K11,
    package A); the window records the refusal (schema 7) and, once the job's sentence has gone, the footer says it
    with its time until the workbook changes. The window plans with the parts' .gear.json (read_sidecar)."""
    from gear_generator.workbook import update as wb_update
    from test_workbook_user_work import _edit
    seen = []
    real = wb_update.classify
    monkeypatch.setattr(wb_update, "classify", lambda *a, **k: seen.append(k.get("read_sidecar")) or real(*a, **k))
    window = built(desk)
    _edit(desk.sw, desk.part("Gear_m1.5_N68"), "Bore Diameter", "14")
    window.press_update()
    desk.finish(window)
    assert window.status.get().startswith("Bore Diameter in Gear_m1.5_N68 is 14 in SolidWorks") and not window.footer().ok
    entry = record_of(window).gearbox.user_work
    assert [p.kind for p in entry.problems] == [swbuild.PROBLEM_VALUE] and entry.digest == window.reading.digest
    assert seen and all(r is store.read_sidecar for r in seen)
    window.note = None
    window._refresh_state()
    assert (f"Update SolidWorks refused at {ui_text.read_time(entry.read_at)}, before changing anything: "
            f"{entry.problems[0].sentence}") in window.status.get()
    assert window.footer().update_enabled


# -- W9d: Build again… carries the user's work (W9D-INTERFACES §2.1, §7, §9.2, §9.4; package B) ----------------------


def _users_sprocket(desk, window):
    """A sprocket of the user's locked to G1 in the built assembly, its file on disk (the worker reads it there)."""
    from test_swbuild import IDENTITY9
    record = record_of(window)
    part = desk.tmp / "Sprocket.SLDPRT"
    part.write_bytes(b"the user's part")
    desk.sw.user_component(record.gearbox.assembly, "Sprocket-1", str(part), (IDENTITY9, (0.0, 0.0, 40.0)))
    desk.sw.user_lock(record.gearbox.assembly, "Lock3", name2(window, "G1"), "Sprocket-1")
    return part


def _carrying_findings(monkeypatch, carry=True):
    """Every W9d finding None on the fake's 2026 (today's state), or the write gates a plain carry needs patched in."""
    names = [n for n in dir(findings) if n.endswith("_ON_2026") and any(n.startswith(p) for p in (
        "CARRY_", "REFERENCED_CONFIGURATION_READ", "FILE_VERSION_READ", "DEPENDENCIES_READ", "OPEN_READ_ONLY_SHOWN",
        "OPEN_READ_ONLY_KEEPS", "COMPONENT_STATE_PER_CONFIGURATION"))]
    for name in names:
        monkeypatch.setattr(findings, name, None)
    if carry:
        for name, value in (("CARRY_INSERTS", True), ("CARRY_REMAKE_KINDS", ("lock",)),
                            ("REFERENCED_CONFIGURATION_READ", True), ("CARRY_INSERTS_IN_A_CONFIGURATION", True)):
            monkeypatch.setattr(findings, f"{name}_ON_2026", value)


def test_a_build_again_hands_the_worker_its_carry_says_what_was_carried_and_the_footer_asks_for_the_save(desk,
                                                                                                        monkeypatch):
    """The window's path for a carrying Build again…, on A's worker on the fake: ``_start_build`` passes ``carry``
    (from the very old assembly it passes as ``before``), ``_finish_build`` says ``carried_status`` after the build's
    own sentence and records the carry, and the footer says the new assembly holds it unsaved until its file is
    newer."""
    from gear_generator import workbook_gui
    _carrying_findings(monkeypatch)
    window = built(desk)
    _users_sprocket(desk, window)
    save_in_excel(window, {"Gears": {"K2": "arcs"}})
    monkeypatch.setattr(workbook_gui, "ask_yes_no", lambda parent, title, text: True)
    given = {}
    real = swbuild.build_gearbox

    def build(session, **kwargs):
        given.update(kwargs)
        return real(session, **kwargs)
    monkeypatch.setattr(workbook_gui.swbuild, "build_gearbox", build)
    window.press_update()
    desk.finish(window)
    carry = given.get("carry")
    assert carry is not None and carry.old is given["before"]
    assert [b.old for b in carry.bodies][:1] == ["layout"] and "G1" in [b.old for b in carry.bodies]
    status = window.status.get()
    assert status.startswith(f"Built 1 part, {NAME}_r2_Layout and {NAME}_r2.SLDASM"), status
    assert f"Carried into {NAME}_r2, unsaved: your " in status and "and your Lock3, on in the modes it was on in." \
        in status, status
    assert status.endswith(f"Save {NAME}_r2 in SolidWorks to keep what was carried."), status
    record = record_of(window)
    assert record.gearbox.name == f"{NAME}_r2" and record.unsaved == {}
    assert record.gearbox.carry.unsaved_at == os.path.getmtime(record.gearbox.assembly)
    assert [c.was for c in record.gearbox.carry.components] == ["Sprocket-1"]
    kept = dict(json.loads(record_bytes(window))["gearbox"]["carry"])
    assert store.same_path(kept.pop("assembly"), desk.part(NAME, ".SLDASM"))   # the app's own file, as gearbox's
    assert str(desk.tmp) not in json.dumps(kept) and "Sprocket.SLDPRT" not in json.dumps(kept)   # no user path
    line = f"{NAME}_r2 holds what Build again… carried of yours, not saved: save it in SolidWorks to keep it."
    # Straight after the build the footer is the build's own sentence, which asks the save itself; §9.4's line follows
    # it only when that sentence does not (a stop), and stands alone once the sentence is gone (the workbook's next
    # save, here set aside by hand) — the demonstration's record check reads one or the other.
    after = window.footer().text
    assert after.count(f"Save {NAME}_r2 in SolidWorks to keep what was carried.") == 1 and line not in after, after
    window.note = None
    window._plan()
    assert line in window.footer().text, window.footer().text
    touch_later(record.gearbox.assembly)                       # saved in SolidWorks
    window._tick()
    assert line not in window.footer().text


def test_a_build_again_today_says_what_stays_led_by_the_finding_as_the_question_does(desk, monkeypatch):
    """M1 through the window, on A's worker: with every W9d finding None the result is W9a's sentence of what stays in
    the old assembly, led by the finding that holds the carry back; nothing is recorded unsaved, and no footer line."""
    from gear_generator import workbook_gui
    _carrying_findings(monkeypatch, carry=False)
    window = built(desk)
    _users_sprocket(desk, window)
    save_in_excel(window, {"Gears": {"K2": "arcs"}})
    monkeypatch.setattr(workbook_gui, "ask_yes_no", lambda parent, title, text: True)
    window.press_update()
    desk.finish(window)
    status = window.status.get()
    assert ("Gear Generator has not yet been shown to carry your work into a new revision on SolidWorks 2026 "
            f"(findings.CARRY_INSERTS_ON_2026), so your Sprocket-1 and Lock3 stay in {NAME}.SLDASM, as read when this "
            f"build began; {NAME}_r2 has none of them.") in status, status
    record = record_of(window)
    assert record.gearbox.carry is not None and record.gearbox.carry.unsaved_at == 0.0
    assert record.gearbox.user_work is None and "holds what Build again… carried" not in window.footer().text
