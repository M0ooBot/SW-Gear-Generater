r"""The Workbook window against real SolidWorks and Excel: Build, Update SolidWorks, Build again (W4, and W5's footers).

python.exe probe/workbook_window_check.py <repo src> <scratch folder under C:\> --pid PID [--log FILE]
                                          [--w4-static FOLDER] [--only w8]

The window is opened the way Import workbook… opens it (``workbook_gui.open_workbook`` with the path) under a
unique title, in a Tk process of its own, with the strip's real SolidWorks worker: nothing is patched but
``workbook_gui.ask_yes_no`` (the Build again? question, answered Yes and logged), APPDATA (the recent list goes
into the scratch folder, not the user's) and, for stage 5 only, ``workbook_gui.wb_gearbox.plan_gearbox`` for that
one folder. The strip attaches to the newest SolidWorks, so this refuses to start unless the newest reachable
session is the PID given. An Excel of its own, on its own thread, makes every edit; the buttons are pressed by
invoking their commands. Each stage is captured from the window's own handle with PrintWindow into <scratch>\shots,
and the footer, read line and gear table are logged.

1. The 12 : 1 fixture, its Output folder cell set to the scratch folder in Excel; the window opened; Build. Since
   W5 the gearbox is built to turn: the sentence and the footer say how ("drag G1 in SolidWorks and the rest of its
   train follow"), shot as 03-built.
2. The demonstration edit in Excel (S2 X 64.5, G2 Teeth 69): the summary (since W5 it sets the gear mate G1 meshes
   G2 to 17 : 69 by the remake), then Update SolidWorks. The header then says "updated from this version, not yet
   saved", never "built from this version".
3. G1's bore cleared in Excel. Since the W4 review (B2) nothing waits for a save: Build again… and Update
   SolidWorks are both enabled, and the footer gives the structural reason, asks once for the save of
   Gear_m1.5_N68, Reducer_12to1_Layout and Reducer_12to1 (since the second review, adding "If SolidWorks closed
   them without saving, those changes are gone."), and says that while Gear_m1.5_N68's changes are not saved
   the new revision makes G2's part new, as Gear_m1.5_N69. The three are then saved in SolidWorks, as a person
   would (by this driver, through COM, on its own thread), so G2's part is reused; then Update SolidWorks asks
   Build again? and the answer is Yes, and the record ends at revision 2 with N68 reused, its journal taken
   out, and the header "built from this version".
4. ``--w4-static FOLDER``: a W4-built gearbox's workbook, opened IN PLACE (its schema-2 record names that very
   workbook, so a copy would read as another's): the footer of a static record — "It was built static, before
   gears could be mated to turn: Build again… makes a new revision whose gears turn." — shot as 09; nothing is
   pressed, and every file in that folder keeps its sha256. Skipped, and said, without the option.
5. The refused state (W5-DECISIONS answer 1): the 12 : 1 in a folder of its own, its plan given one more mate by
   this script (G3, the follower locked to G2, also on S2 Axis and along S2: over-defined, as probe compound_lock
   found); Build stops at the mate check: the sentence names the mate problems, says the assembly is left open
   and that Build is available again once the workbook changes, Build is greyed, the record holds the problems
   and their digest, and no assembly file is written. Shot as 10. The refused document is then closed by its
   title (this run's modified documents saved first, as W4's close_ours does on 2024), any dialog it raises answered
   "Don't Save" and logged: no probe closed a never-saved refused assembly on 2024 under a watch.
6. W6 (W6-PLAN §2.10, §6.1 rw), board WorkbookRightAngle: fixture A, Bevel_Reducer (§5.1), written by the app's own
   ``write_new`` with its Output folder blank and saved once by Excel; the strip's Output folder set to its folder;
   read (shot 11: the header "Bevel and parallel train · 2 meshes · 6.000 : 1 · output at 90° to the input" and the
   Speeds lines of §5.1, S1 seen from +X), then built: the footer says "drag G1" (shot 12).
7. Board WorkbookCrossed: fixture B, Crossed_Slant (§5.2), read only (shot 13): the end view with the crossed and
   slanted stages, the Speeds lines "…500.0 rpm anticlockwise seen from … +X …" and "…333.3 rpm anticlockwise seen
   from … (0.5, −0.866, 0) …"; nothing built.
8. W7 (W7-PLAN §2.12, §6 window), board WorkbookPlanetary: Planetary_4to1 (§4.1), written by ``write_new`` with its
   Output folder blank, saved once by Excel; read (shot 14: the ready footer naming the carrier part and what it
   turns with, the header, the Speeds lines with the planet's speed on its carrier, the end view with the carrier's
   dashed circle through every copy), then built (shot 15: "drag Sun …", the carrier part's axes-and-planes clause).
9. Board WorkbookPlanetaryCopies: Copies 5 typed in Excel (shot 16): the assembly-condition error at Shafts!H4,
   Build not offered.
10. W8 (W8-PLAN §5 window): the E4 transfer case (tests/workbook_fixtures.e4_transfer_case), written by ``write_new``
   with its Output folder blank and saved once by Excel; read (shot 17); the Speeds panel with the mode chooser on 4L
   (shot 18) and on N (shot 19), each panel cut out; then built (shot 20): the built footer's sentences logged
   verbatim (their turn sentence is not asserted: it may change after s7), the footer whole, the window 1080 px wide
   in every state. ``--only w8`` runs this stage alone. Since W9a (K12, ISSUE-1-PLAN §2.6; W9A-REVIEW-B point 2), read
   and built: the footer measured on its box (``_status_box``), not its label; the window frame's bottom
   (``GetWindowRect``) inside the screen's work area; the window's real height as Windows has it; the footer and
   every button whole; the body's last line scrolled into view (``_page`` to its end); and, built, a sentence set by
   ``_set_status`` alone shown whole.

Afterwards the window is closed, Excel quit, and this run's SolidWorks documents saved and closed. Any exception in a
Tk callback ends the run as failed (``report_callback_exception``), a watchdog ends it when no step has completed for
15 minutes, and the log is written line by line as it goes, so a run that stalls or is stopped keeps it.

Run on SolidWorks 2026 on 2026-11-13 (w4-window-20261113-195843.log) before the W4 review's fixes, and again on
2026 and 2024 on 2026-11-14 (w4-window-20261114-055011.log, sw2024/w4-window-20261114-061023.log) for stages 1-3.
"""

import ctypes
import dataclasses
import json
import os
import queue
import shutil
import sys
import threading
import time

SRC, ROOT = sys.argv[1], sys.argv[2]
PID = int(sys.argv[sys.argv.index("--pid") + 1])
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FIXTURE = os.path.join(REPO, "tests", "fixtures", "excel-windows", "Reducer_12to1.xlsx")
os.environ["APPDATA"] = os.path.join(ROOT, "appdata")
os.environ["GG_SRC"] = SRC
os.environ["GG_EXCEL_SCRATCH"] = ROOT
os.makedirs(os.environ["APPDATA"], exist_ok=True)
sys.path.insert(0, SRC)
sys.path.insert(1, os.path.join(HERE, "excel"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
LOG_PATH = sys.argv[sys.argv.index("--log") + 1] if "--log" in sys.argv else os.path.join(ROOT, "window.log")
W4_STATIC = sys.argv[sys.argv.index("--w4-static") + 1] if "--w4-static" in sys.argv else ""
open(LOG_PATH, "w", encoding="utf-8").close()       # log() appends each line as it goes

import tkinter as tk  # noqa: E402

import pythoncom  # noqa: E402
import win32api  # noqa: E402
import win32gui  # noqa: E402
import win32ui  # noqa: E402
from PIL import Image  # noqa: E402

from gear_generator import gui, store, swcom, theme, ui_text, workbook_gui  # noqa: E402
from gear_generator.gears import base  # noqa: E402
from gear_generator.swcom import call  # noqa: E402
from gear_generator.workbook import layout as wb_layout  # noqa: E402

UNIQUE = "GG workbook W4 check 5c21"
SHOTS = os.path.join(ROOT, "shots")
os.makedirs(SHOTS, exist_ok=True)
FOLDER = os.path.join(ROOT, "window")
os.makedirs(FOLDER)
PATH = os.path.join(FOLDER, "Reducer_12to1.xlsx")
shutil.copy(FIXTURE, PATH)
REFUSED_FOLDER = os.path.join(ROOT, "refused")
os.makedirs(REFUSED_FOLDER)
REFUSED_PATH = os.path.join(REFUSED_FOLDER, "Reducer_12to1.xlsx")
shutil.copy(FIXTURE, REFUSED_PATH)
W6A_FOLDER = os.path.join(ROOT, "right-angle")
W6B_FOLDER = os.path.join(ROOT, "crossed")
W7_FOLDER = os.path.join(ROOT, "planetary")
W8_FOLDER = os.path.join(ROOT, "transfer-case")
ONLY = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else ""
LINES = []
FAILS = []


def log(kind, **kw):
    text = time.strftime("%H:%M:%S") + " " + kind + " " + json.dumps(kw, ensure_ascii=False, default=str)
    print(text, flush=True)
    LINES.append(text)
    # Written as it goes (a run that hangs or is stopped keeps its log), and again whole at the end.
    try:
        with open(LOG_PATH, "a", encoding="utf-8", newline="\n") as handle:
            handle.write(text + "\n")
    except OSError:
        pass


def check(ok, what):
    log("ok" if ok else "FAIL", what=what)
    if not ok:
        FAILS.append(what)


# -- Excel on its own thread -------------------------------------------------------------------------------

jobs: "queue.Queue" = queue.Queue()
done: "queue.Queue" = queue.Queue()


def excel_thread():
    from xlhelp import Excel, Watcher
    xl = Excel(visible=True)
    watcher = Watcher(xl.pid, "w4-window", xl.hwnd)
    watcher.start()
    wb = None
    try:
        while True:
            job = jobs.get()
            if job is None:
                break
            what, args = job
            try:
                if what == "open":
                    wb, rep = xl.open(args[0] if args else PATH, "w4-window")
                    result = rep["repaired"]
                elif what == "set-save":
                    for sheet, ref, value in args:
                        cell = wb.Worksheets(sheet).Range(ref)
                        if value is None:
                            cell.ClearContents()
                        else:
                            cell.Value = value
                    wb.Save()
                    result = "saved"
                elif what == "close":
                    wb.Close(SaveChanges=False)
                    wb = None
                    result = "closed"
                done.put((what, time.time(), result, ""))
            except Exception as exc:  # noqa: BLE001
                done.put((what, time.time(), None, f"{type(exc).__name__}: {exc}"))
    finally:
        watcher.stop.set()
        watcher.join()
        log("excel dialogs", seen=watcher.seen)
        if wb is not None:
            try:
                wb.Close(SaveChanges=False)
            except Exception:  # noqa: BLE001
                pass
        xl.quit()


# -- SolidWorks for what a person does there (saving), on its own thread --------------------------------------


def in_solidworks(work):
    """Run ``work(app)`` against the session with PID on a thread of its own; returns its value."""
    out = {}

    def body():
        pythoncom.CoInitialize()
        try:
            found = [c for c in swcom.find_candidates() if c.pid == PID]
            out["value"] = work(found[0].app)
        except Exception as exc:  # noqa: BLE001
            out["error"] = f"{type(exc).__name__}: {exc}"
        finally:
            pythoncom.CoUninitialize()
    t = threading.Thread(target=body)
    t.start()
    t.join(600)
    return out


def _docs(app):
    out, doc = [], call(app, "GetFirstDocument")
    while doc is not None:
        out.append(doc)
        doc = call(doc, "GetNext")
    return out


def _ours(path):
    return bool(path) and any(os.path.normcase(path).startswith(os.path.normcase(f) + os.sep)
                              for f in (FOLDER, REFUSED_FOLDER, W6A_FOLDER, W6B_FOLDER, W7_FOLDER, W8_FOLDER))


BEFORE_TITLES = set()        # the untitled documents open before this run: never ours to close


def save_paths(paths):
    def work(app):
        saved = []
        for doc in _docs(app):
            path = str(call(doc, "GetPathName") or "")
            if any(store.same_path(path, p) for p in paths):
                ok = call(call(doc, "Extension"), "SaveAs3", path, 0, 1, swcom._null_dispatch(),  # noqa: SLF001
                          swcom._null_dispatch(), swcom._out_long(), swcom._out_long())  # noqa: SLF001
                saved.append((os.path.basename(path), bool(ok)))
        return saved
    return in_solidworks(work)


def close_ours():
    def work(app):
        for doc in _docs(app):
            path = str(call(doc, "GetPathName") or "")
            if _ours(path) and call(doc, "GetSaveFlag"):
                call(call(doc, "Extension"), "SaveAs3", path, 0, 1, swcom._null_dispatch(),  # noqa: SLF001
                     swcom._null_dispatch(), swcom._out_long(), swcom._out_long())  # noqa: SLF001
        for kind in (2, 1):
            for doc in _docs(app):
                if _ours(str(call(doc, "GetPathName") or "")) and int(call(doc, "GetType")) == kind:
                    call(app, "CloseDoc", str(call(doc, "GetTitle")))
        return [str(call(d, "GetTitle")) for d in _docs(app) if _ours(str(call(d, "GetPathName") or ""))]
    return in_solidworks(work)


DONT_SAVE = ("&No", "No", "Do&n't Save", "Don't Save", "&Don't Save", "Don't save")


def answer_dont_save(stop, pressed, cam_only=False):
    """While the refused assembly is closed: any SolidWorks dialog (#32770) of the PID gets its No / Don't Save
    button pressed (BM_CLICK), as a person closing a never-saved assembly unsaved would; each is logged. No probe
    closed one on 2024 under a watch, so this is what keeps a "save changes?" box from holding the close."""
    import win32process
    seen = set()
    while not stop.is_set():
        found = []

        def each(hwnd, _):
            if (win32gui.IsWindowVisible(hwnd) and win32gui.GetClassName(hwnd) == "#32770"
                    and win32process.GetWindowThreadProcessId(hwnd)[1] == PID):
                found.append(hwnd)
            return True
        try:
            win32gui.EnumWindows(each, None)
        except Exception:  # noqa: BLE001
            pass
        for hwnd in found:
            buttons = []
            win32gui.EnumChildWindows(hwnd, lambda c, _: buttons.append(c) or True, None)
            key = (hwnd, win32gui.GetWindowText(hwnd), tuple(win32gui.GetWindowText(c) for c in buttons))
            if key in seen:               # handle, title and texts together: a reused handle is still answered
                continue
            seen.add(key)
            hit = [c for c in buttons if win32gui.GetWindowText(c) in DONT_SAVE]
            if cam_only and not ("SOLIDWORKS CAM" in win32gui.GetWindowText(hwnd) and any(
                    win32gui.GetWindowText(c).startswith("Save changes to") for c in buttons)):
                continue
            pressed.append((win32gui.GetWindowText(hwnd), win32gui.GetWindowText(hit[0]) if hit else ""))
            if hit:
                win32gui.PostMessage(hit[0], 0x00F5, 0, 0)
        time.sleep(0.5)


def close_refused():
    """The refused assembly the build left open (an untitled assembly that was not open before the run): this run's
    modified documents saved first, then ``CloseDoc`` by its title, as W4's close_ours closes on 2024, with any
    dialog answered "Don't Save" and logged (``answer_dont_save``)."""
    stop, pressed = threading.Event(), []
    watcher = threading.Thread(target=answer_dont_save, args=(stop, pressed), daemon=True)
    watcher.start()
    try:
        out = _close_refused()
    finally:
        stop.set()
        watcher.join(5)
    out["dialogs"] = pressed
    return out


def _close_refused():
    def work(app):
        for doc in _docs(app):
            path = str(call(doc, "GetPathName") or "")
            if _ours(path) and call(doc, "GetSaveFlag"):
                call(call(doc, "Extension"), "SaveAs3", path, 0, 1, swcom._null_dispatch(),  # noqa: SLF001
                     swcom._null_dispatch(), swcom._out_long(), swcom._out_long())  # noqa: SLF001
        closed = []
        for doc in _docs(app):
            title = str(call(doc, "GetTitle"))
            if not str(call(doc, "GetPathName") or "") and int(call(doc, "GetType")) == 2 and title not in BEFORE_TITLES:
                call(app, "CloseDoc", title)
                closed.append(title)
        left = [str(call(d, "GetTitle")) for d in _docs(app) if not str(call(d, "GetPathName") or "")
                and str(call(d, "GetTitle")) not in BEFORE_TITLES]
        return {"closed": closed, "left": left}
    return in_solidworks(work)


try:
    with open(os.path.join(os.path.dirname(os.path.abspath(SRC)), "SNAPSHOT_COMMIT"), encoding="utf-8") as _handle:
        log("run", src=SRC, snapshot=_handle.read().strip())
except OSError:
    log("run", src=SRC)
newest = in_solidworks(lambda app: swcom.choose(swcom.find_candidates()).pid)
log("newest session", pid=newest)
if newest.get("value") != PID:
    print("STOP: the strip would attach to", newest, "not", PID)
    raise SystemExit(2)
BEFORE_TITLES.update(in_solidworks(lambda app: [str(call(d, "GetTitle")) for d in _docs(app)
                                                if not str(call(d, "GetPathName") or "")]).get("value", []))

XT = threading.Thread(target=excel_thread, daemon=True)
XT.start()
# For the whole run, SOLIDWORKS CAM's Yes/No "Save changes to …?" box — raised by closing a changed 2024-era assembly
# in 2026, deaf to WM_CLOSE and Escape — is answered No, as a person would (every close here saves first or means to
# discard); each press is logged at the end.
CAM_STOP, CAM_PRESSED = threading.Event(), []
threading.Thread(target=answer_dont_save, args=(CAM_STOP, CAM_PRESSED, True), daemon=True).start()

# -- the app --------------------------------------------------------------------------------------------------

gui._declare_dpi_aware()
theme.register_bundled_fonts()
root = tk.Tk()
root.title(UNIQUE + " strip")
scale = gui._scale_to_dpi(root)
app = gui.GearApp(root, scale=scale)
root.withdraw()
win = None
QUESTIONS = []


def answer_yes(parent, title, question):
    QUESTIONS.append(question)
    log("asked", title=title, question=question)
    return True


workbook_gui.ask_yes_no = answer_yes

# Stage 5: the plan of the refused folder's workbook given one more mate, as probe/workbook_assembly_check.py's m4
# does (W5-PLAN §4.3 m4). Only while INJECT is on, and only for that folder; every other plan is the app's own.
INJECT = {"on": False, "done": []}
_plan_gearbox = workbook_gui.wb_gearbox.plan_gearbox


def _injected(plan):
    handle_of = {g: h for h, g in plan.handles.items()}
    h3 = handle_of["G3"]
    z = plan.frames["G3"].at[2]
    ops, done = [], False
    for op in plan.assembly.ops:
        ops.append(op)
        if not done and isinstance(op, base.Mate) and op.kind == "lock" and op.b == h3:
            ops.append(base.Mate("inject1", "coincident", f"{h3}:Gear Axis", f"{wb_layout.LAYOUT_HANDLE}:S2 Axis",
                                 name="G3 on S2 Axis"))
            ops.append(base.Mate("inject2", "point distance", f"{h3}:origin", f"{wb_layout.LAYOUT_HANDLE}:plane1", z,
                                 name="G3 along S2"))
            done = True
    if not done:
        return plan
    return dataclasses.replace(plan, assembly=dataclasses.replace(plan.assembly, ops=tuple(ops)))


def plan_gearbox(*args, **kwargs):
    plan = _plan_gearbox(*args, **kwargs)
    if (INJECT["on"] and plan is not None and not plan.refusal and plan.assembly is not None
            and store.same_path(os.path.dirname(plan.assembly_path), REFUSED_FOLDER)):
        plan = _injected(plan)
        INJECT["done"].append(plan.assembly_path)
    return plan


workbook_gui.wb_gearbox.plan_gearbox = plan_gearbox

# -- W6's two fixtures (W6-PLAN §5), as probe/workbook_assembly_check.py's r1 and r5 write them --------------------

from gear_generator.workbook import model as wb_model, xlsx  # noqa: E402
from gear_generator.workbook.model import Box, Gear, GearboxSpec, Mesh, Shaft  # noqa: E402

W6A = GearboxSpec(
    box=Box(name="Bevel_Reducer"),
    shafts=(Shaft("S1", "frame", "0", "0", "60", "X+", "input", speed="1500", torque="10"),
            Shaft("S2", "frame", "0", "0", "0", "Z+"),
            Shaft("S3", "frame", "-68", "0", "0", "Z+", "output")),
    gears=(Gear("G1", "S1", "0", "bevel", "external", "20", "3", face_width="20", bore="10"),
           Gear("G2", "S2", "60", "bevel", "external", "40", "3", face_width="20", bore="10"),
           Gear("G3", "S2", "5", "spur", "external", "17", "2", face_width="10", bore="8"),
           Gear("G4", "S3", "5", "spur", "external", "51", "2", face_width="10", bore="8")),
    meshes=(Mesh("G1", "G2"), Mesh("G3", "G4")))
W6B = GearboxSpec(
    box=Box(name="Crossed_Slant"),
    shafts=(Shaft("S1", "frame", "0", "0", "0", "Z+", "input", speed="1000", torque="5"),
            Shaft("S2", "frame", "0", "84.852814", "8", "X+"),
            Shaft("S3", "frame", "-110", "84.852814", "8", "-1, 1.732050807569, 0", "output")),
    gears=(Gear("G1", "S1", "10", "helical", "external", "20", "2", face_width="16", bore="6", helix_angle="45",
                hand="right"),
           Gear("G2", "S2", "0", "helical", "external", "40", "2", face_width="16", bore="8", helix_angle="45",
                hand="right"),
           Gear("G3", "S2", "-110", "bevel", "external", "20", "2.5", face_width="10", bore="8"),
           Gear("G4", "S3", "0", "bevel", "external", "30", "2.5", face_width="10", bore="8")),
    meshes=(Mesh("G1", "G2"), Mesh("G3", "G4")))
# The Speeds lines exactly, C's wording (W6-INTERFACES §7.19): "seen from the +X end", a no-break space joining each
# number to its unit and holding the vector together.
NB = "\u00a0"
W6_EXPECT = {
    "A": ("Bevel and parallel train · 2 meshes · 6.000 : 1 · output at 90° to the input",
          [f"S1    1500.0{NB}rpm anticlockwise seen from the +X end · 10.00{NB}N·m",
           f"S2    750.0{NB}rpm clockwise seen from the +Z end · 19.60{NB}N·m",
           f"S3    250.0{NB}rpm anticlockwise seen from the +Z end · 57.62{NB}N·m"]),
    "B": ("Crossed and bevel train · 2 meshes · 3.000 : 1 · output at 90° to the input",
          [f"S1    1000.0{NB}rpm anticlockwise seen from the +Z end · 5.00{NB}N·m",
           f"S2    500.0{NB}rpm anticlockwise seen from the +X end · 9.80{NB}N·m",
           f"S3    333.3{NB}rpm anticlockwise seen from the (0.5,{NB}−0.866,{NB}0) end · 14.41{NB}N·m"])}
# W7's fixture, as probe/workbook_assembly_check.py's p1 writes it (W7-PLAN §4.1), and what D's tests pin for it.
W7 = GearboxSpec(
    box=Box(name="Planetary_4to1", pressure_angle="20", efficiency="98"),
    shafts=(Shaft("S", "frame", "0", "0", "0", "Z+", "input", "", "1000", "2"),
            Shaft("C", "frame", "0", "0", "0", "Z+", "output"),
            Shaft("P", "C", "18", "0", "0", "", "", "3"),
            Shaft("R", "frame", "0", "0", "0", "Z+", "fixed")),
    gears=(Gear("Sun", "S", "10", "spur", "external", "18", "1", "", "10", "6", part_name="Sun"),
           Gear("Planet", "P", "10", "spur", "external", "18", "1", "", "10", "8", part_name="Planet"),
           Gear("Ring", "R", "10", "spur", "internal", "54", "1", "", "10", ""),
           Gear("CarrierGear", "C", "30", "spur", "external", "20", "1", "", "6", "10", part_name="CarrierGear")),
    meshes=(Mesh("Sun", "Planet"), Mesh("Planet", "Ring")))
W7_EXPECT = {
    "header": "Planetary, R fixed · 3 planets · 4.000 : 1 · output turns the same way",
    "lines": ["S     1000.0 rpm anticlockwise · 2.00 N·m", "C     250.0 rpm anticlockwise · 7.76 N·m",
              "P     500.0 rpm clockwise, 750.0 rpm clockwise relative to C · 3 copies", "R     held still · 5.76 N·m"],
    "ready": "C is built as a carrier of axes and planes only, turning with the 3 copies of Planet on it. Ring stays "
             "fixed where it is placed: its shaft does not turn.",
    "built": "drag Sun in SolidWorks and the rest of its train follow. The 3 copies of Planet turn on C, and "
             "Planetary_4to1_C_Carrier holds C's axes and planes only: a plate and pins are yours to add.",
    "copies5": "5 copies of Planet cannot all mesh with Sun and Ring at once"}
W6_PATHS = {}
for _which, _spec, _folder in (("A", W6A, W6A_FOLDER), ("B", W6B, W6B_FOLDER), ("P", W7, W7_FOLDER)):
    os.makedirs(_folder)
    W6_PATHS[_which] = os.path.join(_folder, _spec.box.name + ".xlsx")
    xlsx.write_new(W6_PATHS[_which], wb_model.to_sheets(_spec))     # the Output folder blank: the strip's is used

# W8's E4 transfer case, as probe/workbook_assembly_check.py's s1 writes it (W8-PLAN §2.1).
import importlib.util  # noqa: E402
_fixtures = importlib.util.spec_from_file_location("workbook_fixtures", os.path.join(REPO, "tests", "workbook_fixtures.py"))
workbook_fixtures = importlib.util.module_from_spec(_fixtures)
_fixtures.loader.exec_module(workbook_fixtures)
W8 = workbook_fixtures.e4_transfer_case()
os.makedirs(W8_FOLDER)
W6_PATHS["E4"] = os.path.join(W8_FOLDER, W8.box.name + ".xlsx")
xlsx.write_new(W6_PATHS["E4"], wb_model.to_sheets(W8))


def shoot(name):
    # Tk's own update(): the window's UpdatePlan is update_plan since the W4 review, so nothing hides it now.
    win.update_idletasks()
    win.update()
    hwnd = int(win.wm_frame(), 16)
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    w, h = right - left, bottom - top
    wdc = win32gui.GetWindowDC(hwnd)
    dc = win32ui.CreateDCFromHandle(wdc)
    mem = dc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(dc, w, h)
    mem.SelectObject(bmp)
    ctypes.windll.user32.PrintWindow(hwnd, mem.GetSafeHdc(), 2)
    info = bmp.GetInfo()
    img = Image.frombuffer("RGB", (info["bmWidth"], info["bmHeight"]), bmp.GetBitmapBits(True), "raw", "BGRX",
                           0, 1)
    path = os.path.join(SHOTS, name + ".png")
    img.save(path)
    win32gui.DeleteObject(bmp.GetHandle())
    mem.DeleteDC()
    dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, wdc)
    state(name, path=path)


def state(name, **kw):
    footer = win.footer()
    log("state", name=name, status=win.status.get(), read_line=win.read_line.get(),
        build=(footer.build_label, footer.build_enabled, footer.build_primary),
        update=(footer.update_shown, footer.update_enabled, footer.update_primary),
        parts=win.parts_readout.get(), changes=win.changes_readout.get(), **kw)


def excel(what, *args):
    jobs.put((what, args))


LAST = {}


def excel_done(what):
    def ok():
        try:
            item = done.get_nowait()
        except queue.Empty:
            return False
        log("excel", what=item[0], at=item[1], result=item[2], error=item[3])
        LAST["excel"] = item
        return True
    return ok


def open_window(path=PATH, title=UNIQUE):
    global win
    if win is not None and not win._closed():  # noqa: SLF001
        win.close()
    win = workbook_gui.open_workbook(app, path)
    win.title(title)


def idle():
    return win._pending is None and win._job is None  # noqa: SLF001


def status_starts(*heads):
    return lambda: idle() and win.status.get().startswith(heads)


def speeds_labels():
    return [w for w in win.speeds_body.winfo_children() if isinstance(w, tk.Label)]


def speeds_lines():
    """The Speeds panel's lines as the window shows them (its labels' text, exactly)."""
    return [str(w.cget("text")) for w in speeds_labels()]


def speeds_panel(name):
    """The Speeds panel cut from shot ``name`` and doubled (``<name>-speeds.png``), and how many lines Tk drew each
    label on (its height over its font's line spacing): a wrapped line is there to LOOK at, whether each number
    stays with its unit (W6-INTERFACES §7.19)."""
    import tkinter.font as tkfont
    hwnd = int(win.wm_frame(), 16)
    left, top, _, _ = win32gui.GetWindowRect(hwnd)
    body = win.speeds_body
    x0, y0 = body.winfo_rootx() - left, body.winfo_rooty() - top
    img = Image.open(os.path.join(SHOTS, name + ".png"))
    crop = img.crop((max(0, x0 - 8), max(0, y0 - 8), x0 + body.winfo_width() + 8, y0 + body.winfo_height() + 8))
    crop = crop.resize((crop.width * 2, crop.height * 2), Image.LANCZOS)
    path = os.path.join(SHOTS, name + "-speeds.png")
    crop.save(path)
    rows = []
    for w in speeds_labels():
        font = tkfont.Font(root=win, font=w.cget("font"))
        rows.append({"text": str(w.cget("text")), "drawn_on_lines": round(w.winfo_height() / font.metrics("linespace")),
                     "wraplength": str(w.cget("wraplength")), "width_needed": font.measure(str(w.cget("text")))})
    log("speeds panel", shot=path, labels=rows)


def w6_read_check(which):
    header, wanted = W6_EXPECT[which]
    lines, shown = speeds_lines(), win.box_values["type"].cget("text")
    log("W6 read", board=which, header=shown, speeds=lines, speeds_readout=win.speeds_readout.get(),
        end_view=win.view_readout.get())
    check(shown == header, f"W6 {which}: the header {shown!r}")
    check(lines == wanted, f"W6 {which}: the Speeds lines are C's exactly (no-break spaces included): "
          f"{[(got, want) for got, want in zip(lines, wanted) if got != want] or (lines if len(lines) != len(wanted) else 'equal')}")


def w7_read_check():
    text, shown = win.status.get(), win.box_values["type"].cget("text")
    lines = [line.replace("\u00a0", " ") for line in speeds_lines()]
    log("W7 read", header=shown, speeds=lines, status=text, end_view=win.view_readout.get())
    check(shown == W7_EXPECT["header"], f"W7: the header {shown!r}")
    check(lines == W7_EXPECT["lines"], f"W7: the Speeds lines are D's tests' (no-break spaces as spaces): {lines}")
    check(text.endswith(W7_EXPECT["ready"]), "W7: the ready footer says what the carrier is and what stays fixed")


def w7_built_check():
    record = store.read_link_record(W6_PATHS["P"])
    box = record.gearbox
    text = win.status.get()
    check(box.kind == store.GEARBOX_MOTION and box.assembly and [os.path.basename(c.path) for c in box.carriers]
          == ["Planetary_4to1_C_Carrier.SLDPRT"], f"W7: built to turn with its carrier part: {box.kind!r}, "
          f"{[os.path.basename(c.path) for c in box.carriers]}")
    check(W7_EXPECT["built"] in text, "W7: the built footer says to drag Sun and what the carrier part holds")


def w7_copies_check():
    text, footer = win.status.get(), win.footer()
    check(text.startswith("Fix the workbook before building:") and W7_EXPECT["copies5"] in text
          and not footer.build_enabled, f"W7: Copies 5 is the assembly-condition error, Build not offered: {text!r}")


def w8_width(name):
    """The window's width against WINDOW_WIDTH (W3: two columns at 1080 px, scaled as the window scales it)."""
    want = theme.px(workbook_gui.WINDOW_WIDTH)
    hwnd = int(win.wm_frame(), 16)
    left, _, right, _ = win32gui.GetWindowRect(hwnd)
    check(win.winfo_width() == want, f"W8 {name}: the window is {win.winfo_width()} px wide inside "
          f"(frame {right - left}), WINDOW_WIDTH {workbook_gui.WINDOW_WIDTH} scaled {want}")


def w8_footer_whole(name):
    """The footer whole (K12, W9A-REVIEW-B point 2): since W9a the sentence's label sits in a canvas, the box
    ``_status_box``, and a label in a canvas is always drawn at its asked size however little the box shows, so the
    BOX is measured: as tall as the label asks (the sentence whole), or, when the sentence scrolls in itself above the
    footer's ceiling (``_status_scrolls``), at the ceiling with its bar ``_status_bar`` mapped; the box's bottom inside
    the window either way."""
    win.update_idletasks()
    win.update()
    label, box = win.status_label, win._status_box  # noqa: SLF001 - the K12 box (W9A-PACKAGE-B)
    text = win.status.get()
    scrolls = bool(getattr(win, "_status_scrolls", False))
    ceiling = workbook_gui.work_area(win)[2] // workbook_gui.FOOTER_SHARE
    bottom = box.winfo_rooty() + box.winfo_height() - win.winfo_rooty()
    if scrolls:
        whole = (win._status_bar.winfo_ismapped() and box.winfo_height() >= min(ceiling, label.winfo_reqheight()) - 1  # noqa: SLF001
                 and label.winfo_reqheight() > ceiling)
    else:
        whole = box.winfo_height() >= label.winfo_reqheight() and box.winfo_width() >= label.winfo_reqwidth()
    check(bool(text) and whole and bottom <= win.winfo_height(),
          f"W8 {name}: the footer whole, its box {box.winfo_width()} × {box.winfo_height()} px for the label's "
          f"{label.winfo_reqwidth()} × {label.winfo_reqheight()}, {'scrolling at the ceiling ' + str(ceiling) if scrolls else 'not scrolling'}"
          f", its bottom at {bottom} of {win.winfo_height()}")
    log("W8 footer sentences", state=name, sentences=[t.strip() + "." for t in text.split(". ") if t.strip()])


def _rect(hwnd):
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    return {"left": left, "top": top, "right": right, "bottom": bottom, "height": bottom - top}


def w8_k12(name):
    """K12 (ISSUE-1-PLAN §2.6 *Done when*; W9A-REVIEW-B point 2 and the coordinator's additions), on the real screen:

    - the window's frame (``GetWindowRect`` of ``wm_frame``) inside the primary screen's work area, as the app reads it
      (``workbook_gui.work_area``: ``SPI_GETWORKAREA``) and as Windows' monitor reports it (``GetMonitorInfo``);
    - the window's REAL height, read from Windows (the client window's ``GetWindowRect``), not what was asked
      (a Tk test under Windows Python saw the window keep its requested height after a shorter geometry): the client
      bottom inside the frame and the work area, and Tk's own height agreeing with it;
    - the footer frame and every footer button whole and inside the real client area;
    - the body's last line reachable: the page (``_page``) scrolled to its end, the lowest label of the body
      (``_body``) inside the page, then the page put back at its top."""
    win.update_idletasks()
    win.update()
    frame = int(win.wm_frame(), 16)
    client = int(win.winfo_id())
    outer, inner = _rect(frame), _rect(client)
    left, top, height = workbook_gui.work_area(win)
    try:
        monitor = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0, 0), 1))     # the primary monitor
        work = monitor["Work"]
    except Exception as exc:  # noqa: BLE001
        work = None
        log("W8 K12", what=f"GetMonitorInfo unread: {type(exc).__name__}: {exc}")
    log("W8 K12 geometry", state=name, frame=outer, client=inner, tk_height=win.winfo_height(),
        tk_reqheight=win.winfo_reqheight(), geometry=win.geometry(), app_work_area=(left, top, height),
        monitor_work=work, page_scrolls=bool(win._page_bar.winfo_manager()),  # noqa: SLF001
        status_scrolls=bool(getattr(win, "_status_scrolls", False)))
    check(outer["top"] >= top and outer["bottom"] <= top + height,
          f"W8 {name}: the window's frame {outer['top']}…{outer['bottom']} is inside the work area {top}…{top + height}")
    if work is not None:
        check(outer["top"] >= work[1] and outer["bottom"] <= work[3],
              f"W8 {name}: the frame inside Windows' own work area {work[1]}…{work[3]}")
    check(inner["top"] >= outer["top"] and inner["bottom"] <= outer["bottom"] and abs(inner["height"]
                                                                                       - win.winfo_height()) <= 2,
          f"W8 {name}: the window's real height {inner['height']} px (Windows) is what Tk says it is "
          f"({win.winfo_height()}), its client {inner['top']}…{inner['bottom']} inside the frame")
    foot = win._foot  # noqa: SLF001
    parts = [("footer", foot)] + [(n, getattr(win, n)) for n in ("export_button", "export_as_button", "build_button",
                                                                 "update_button") if getattr(win, n).winfo_manager()]
    cut = []
    for label, w in parts:
        bottom = w.winfo_rooty() + w.winfo_height()
        if not w.winfo_ismapped() or w.winfo_height() < w.winfo_reqheight() or bottom > inner["bottom"]:
            cut.append((label, w.winfo_height(), w.winfo_reqheight(), bottom))
    check(not cut, f"W8 {name}: the footer and every button whole inside the real window (bottom {inner['bottom']}): "
                   f"{cut or [n for n, _ in parts]}")
    page, body = win._page, win._body  # noqa: SLF001
    page.yview_moveto(1.0)
    win.update_idletasks()
    win.update()
    labels, stack = [], list(body.winfo_children())
    while stack:
        w = stack.pop()
        stack.extend(w.winfo_children())
        if isinstance(w, tk.Label) and w.winfo_ismapped() and str(w.cget("text")).strip():
            labels.append((w.winfo_rooty() + w.winfo_height(), str(w.cget("text"))[:40]))
    last = max(labels) if labels else (None, "")
    shown = (page.winfo_rooty(), page.winfo_rooty() + page.winfo_height())
    check(last[0] is not None and shown[0] <= last[0] <= shown[1] + 1 and shown[1] <= inner["bottom"],
          f"W8 {name}: the body's last line ({last[1]!r}, its bottom at {last[0]}) scrolled into view in the page "
          f"{shown[0]}…{shown[1]}")
    page.yview_moveto(0.0)
    win.update_idletasks()


def w8_set_status_whole():
    """W9A-REVIEW-B point 1: a sentence set by ``_set_status`` alone (here the one for SolidWorks out of reach), after
    the footer's own, shown whole in its box; then the footer's state put back."""
    win._set_status(ui_text.job_unreachable("No SolidWorks session is running on this computer that Gear Generator can "
                                             "reach; start SolidWorks, wait for it to finish loading, and press again.",
                                             False), ok=False)  # noqa: SLF001
    w8_footer_whole("a sentence set alone (SolidWorks out of reach)")
    w8_k12("a sentence set alone (SolidWorks out of reach)")     # the buttons beside it whole too (review 15)
    win._refresh_state()  # noqa: SLF001


def w8_choose(name):
    """The mode chosen as a click on its segment does it (``Segmented._choose``: the variable set, then the window's
    ``_mode_chosen``)."""
    chooser = next((c for c in win.mode_choosers if name in getattr(c, "_values", ())), None)
    check(chooser is not None, f"W8: a segment {name} in the mode chooser: "
          f"{[getattr(c, '_values', ()) for c in win.mode_choosers]}")
    if chooser is not None:
        chooser._choose(name)  # noqa: SLF001 - the click's own handler


# Review S6: each mode's head lines held to W8-PLAN §2.3's key (In at 1500 rpm; 2H and 4H 1 : 1, 4L the 4 : 1 low range,
# N neutral) and the couplings it engages; the rest of the panel logged.
W8_HEAD = {"2H": ["2H: Rear 1500 rpm · Front not driven · 1.000 : 1", "In 2H, RangeSlv engages InDog."],
           "4H": ["4H: Rear 1500 rpm · Front 1500 rpm · 1.000 : 1",
                  "In 4H, RangeSlv engages InDog and ModeSlv engages FrontDog."],
           "N": ["N: neutral — Rear, FrontDrv, Idler and Front turn freely.", "In N, no sleeve engages a dog."],
           "4L": ["4L: Rear 375 rpm · Front 375 rpm · 4.000 : 1",
                  "In 4L, RangeSlv engages LoDog and ModeSlv engages FrontDog."]}
# The built footer's sentences that do not depend on the turn wording (being reworded, 5989c7d): held exactly.
W8_BUILT = ["Its turning gears are mated to turn in each of its 4 modes, one configuration each (2H, 4H, N and 4L), and "
            "SolidWorks reports no mate in error in any of them: it opens in 2H; to switch mode, double-click another "
            "mode's configuration in SolidWorks' ConfigurationManager.",
            "Drag Sun in SolidWorks to turn one train and FrontDog to turn the other.",
            "RangeSlv and ModeSlv slide along Rear, each to its place in each mode.",
            "The 3 copies of Pl turn on Carrier, and TransferCase_E4_Carrier_Carrier holds Carrier's axes and planes only: "
            "a plate and pins are yours to add.",
            "Ring stays fixed where it is placed: its shaft does not turn."]


def w8_mode_check(name):
    lines = speeds_lines()
    head = [line.replace("\u00a0", " ") for line in lines[:2]]
    check(head == W8_HEAD.get(name), f"W8 {name}: the Speeds panel's head lines are §2.3's: {head}")
    log("W8 mode", chosen=win.mode.get(), header=win.box_values["type"].cget("text"), speeds=lines,
        speeds_readout=win.speeds_readout.get(), end_view=win.view_readout.get(), status=win.status.get(),
        choosers=[getattr(c, "_values", ()) for c in win.mode_choosers])
    check(win.mode.get() == name and lines, f"W8: the chooser on {name} and the Speeds panel drawn for it "
          f"({len(lines)} lines)")
    w8_width(f"chooser on {name}")


def w8_built_check():
    record = store.read_link_record(W6_PATHS["E4"])
    box = record.gearbox if record is not None else None
    text = win.status.get()
    log("W8 built", status=text, box_kind=box.kind if box else None, modes=list(box.modes) if box else None,
        positions_per_configuration=win.positions_per_configuration)
    check(box is not None and box.kind == store.GEARBOX_MOTION and box.assembly and tuple(box.modes) ==
          ("2H", "4H", "N", "4L"), f"W8: built to turn with a configuration per mode: {box and box.kind!r} "
          f"{box and box.modes}")
    for sentence in W8_BUILT:
        check(sentence in text, f"W8 built: the footer says {sentence!r}")
    w8_footer_whole("built")
    w8_k12("built")
    w8_set_status_whole()
    w8_width("built")


def w6_built_check():
    record = store.read_link_record(W6_PATHS["A"])
    box = record.gearbox
    drag = ui_text.drag_phrase(list(box.drag))
    check(box.kind == store.GEARBOX_MOTION and box.assembly, f"W6 A: built to turn: kind {box.kind!r}")
    check("drag G1" in win.status.get() and drag in win.status.get(), f"W6 A: the built footer says how to turn it: "
          f"{drag!r}")
    log("W6 built", speeds=speeds_lines())


def save_unsaved():
    record = store.read_link_record(PATH)
    paths = list(record.unsaved) if record is not None else []
    log("person saves in SolidWorks", paths=[os.path.basename(p) for p in paths], result=save_paths(paths))


def built_turning_check():
    record = store.read_link_record(PATH)
    box = record.gearbox
    drag = ui_text.drag_phrase(list(box.drag))
    check(box.kind == store.GEARBOX_MOTION, f"built to turn: kind {box.kind!r}")
    check(drag in win.status.get(), f"the built footer says how to turn it: {drag!r}")


def _folder_stamps(folder):
    import hashlib
    out = {}
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if os.path.isfile(path):
            with open(path, "rb") as handle:
                out[name] = (hashlib.sha256(handle.read()).hexdigest(), os.stat(path).st_mtime_ns)
    return out


STATIC = {}


def open_static():
    workbook = next((os.path.join(W4_STATIC, n) for n in sorted(os.listdir(W4_STATIC)) if n.endswith(".xlsx")
                     and not n.startswith("~$")), "")
    STATIC["path"], STATIC["before"] = workbook, _folder_stamps(W4_STATIC)
    raw = json.load(open(store.link_record_path(workbook), encoding="utf-8"))
    log("the W4 static record's source", folder=W4_STATIC, workbook=os.path.basename(workbook),
        schema=raw.get("schema"), built=(raw.get("gearbox") or {}).get("built"),
        gearbox_kind=(raw.get("gearbox") or {}).get("kind", "(none: schema 2)"), written_by=raw.get("written_by"))
    open_window(workbook, UNIQUE + " static")


def static_check():
    text = win.status.get()
    check("It was built static, before gears could be mated to turn: Build again… makes a new revision whose gears "
          "turn." in text, "the W4 static record's footer says it was built static and Build again… turns")
    win.close()
    after = _folder_stamps(W4_STATIC)
    check(after == STATIC["before"], f"nothing in the W4 folder changed: "
          f"{[n for n in after if after.get(n) != STATIC['before'].get(n)]}")


def refused_check():
    text, footer = win.status.get(), win.footer()
    record = store.read_link_record(REFUSED_PATH)
    box = record.gearbox
    check(bool(INJECT["done"]), f"the plan was given the extra mates: {INJECT['done']}")
    check(box is not None and not box.assembly and box.mate_problems and box.mate_problems_digest
          == win.reading.digest, f"the record: no assembly, the mate problems and their digest: "
          f"{box and box.mate_problems}")
    check(not os.path.exists(os.path.join(REFUSED_FOLDER, "Reducer_12to1.SLDASM")), "no assembly file")
    check("no assembly was saved" in text and "Build is available again once the workbook changes" in text,
          "the sentence: no assembly saved, and Build waits for a changed workbook")
    check(any(p in text for p in box.mate_problems), "the sentence names the mate problems")
    check("left open in SolidWorks as" in text, "the sentence names the document left open")
    check(not footer.build_enabled, "Build greyed for the unchanged workbook")
    INJECT["on"] = False


def record_check():
    record = store.read_link_record(PATH)
    check(record.gearbox.revision == 2 and [e.revision for e in record.earlier] == [0],
          f"the record: revision {record.gearbox.revision}, earlier {[e.revision for e in record.earlier]}")
    check(record.pending == [], f"the build's journal taken out: {[os.path.basename(e.path) for e in record.pending]}")
    check(win.read_line.get().endswith(" · built from this version"), f"the header: {win.read_line.get()!r}")
    parts = sorted(os.path.basename(c.part) for c in record.gearbox.components)
    check("Gear_m1.5_N68.SLDPRT" in parts and "Gear_m1.5_N69.SLDPRT" not in parts,
          f"G2's part reused once saved: {parts}")


def updated_check():
    check(win.read_line.get().endswith(" · updated from this version, not yet saved"),
          f"the header after Update: {win.read_line.get()!r}")


def structural_unsaved_check():
    text, footer = win.status.get(), win.footer()
    check(footer.build_enabled and footer.update_enabled, "both buttons on with Update's changes unsaved")
    check(text.count("save them in SolidWorks") == 1 and text.lower().count("build again") == 1,
          "the save asked once, and build again said once")
    check("Gear_m1.5_N68, Reducer_12to1_Layout and Reducer_12to1 have changes from Update SolidWorks" in text,
          "the three unsaved documents named")
    check("While Gear_m1.5_N68's changes are not saved, the new revision makes G2's part new, as Gear_m1.5_N69"
          in text, "the part made new while unsaved said")
    check("If SolidWorks closed them without saving, those changes are gone." in text,
          "the save asked as what may no longer be possible (second review N2)")


STEPS = [
    ("do", lambda: excel("open")),
    ("wait", excel_done("open")),
    ("do", lambda: excel("set-save", ("Box", "B4", FOLDER + "\\"))),
    ("wait", excel_done("set-save")),
    ("do", open_window),
    ("wait", lambda: win.reading is not None and win.reading.ok and win.footer().build_enabled),
    ("pause", 1.0),
    ("do", lambda: shoot("01-ready")),
    ("do", lambda: win.build_button.command()),
    ("pause", 2.0),
    ("do", lambda: shoot("02-building")),
    ("wait", status_starts("Built", "Check", "Update SolidWorks stopped", "SolidWorks cannot")),
    ("pause", 1.5),
    ("do", lambda: shoot("03-built")),
    ("do", built_turning_check),
    ("do", lambda: excel("set-save", ("Shafts", "C3", 64.5), ("Gears", "F3", 69))),
    ("wait", excel_done("set-save")),
    ("wait", status_starts("Update SolidWorks will")),
    ("pause", 1.0),
    ("do", lambda: shoot("04-demonstration-edit")),
    ("do", lambda: win.update_button.command()),
    ("wait", status_starts("Updated SolidWorks", "Update SolidWorks stopped", "SolidWorks already")),
    ("pause", 1.5),
    ("do", lambda: shoot("05-updated")),
    ("do", updated_check),
    ("do", lambda: excel("set-save", ("Gears", "J2", None))),
    ("wait", excel_done("set-save")),
    ("wait", lambda: idle() and "build again" in win.status.get().lower()),
    ("pause", 1.0),
    ("do", lambda: shoot("06-structural-unsaved")),
    ("do", structural_unsaved_check),
    ("do", save_unsaved),
    ("wait", lambda: idle() and "not saved" not in win.status.get() and win.footer().build_enabled),
    ("pause", 1.0),
    ("do", lambda: shoot("07-structural-saved")),
    ("do", lambda: win.update_button.command()),
    ("wait", lambda: bool(QUESTIONS) and idle() and win.status.get().startswith(("Built", "Check"))),
    ("pause", 1.5),
    ("do", lambda: shoot("08-built-again")),
    ("do", record_check),
] + ([
    ("do", open_static),
    ("wait", lambda: win.reading is not None and win.reading.ok and idle()),
    ("pause", 1.5),
    ("do", lambda: shoot("09-w4-static-record")),
    ("do", static_check),
] if W4_STATIC else [("do", lambda: log("skipped", what="the W4 static record's footer: no --w4-static folder"))]) + [
    # The refused folder's parts have the main flow's file names, and SolidWorks keeps one document per file name
    # (the app refuses a build beside them): the main flow's documents are saved and closed first, as a person would.
    ("do", lambda: log("closed the first workbook's documents in SolidWorks", left=close_ours())),
    ("do", lambda: excel("close")),
    ("wait", excel_done("close")),
    ("do", lambda: excel("open", REFUSED_PATH)),
    ("wait", excel_done("open")),
    ("do", lambda: excel("set-save", ("Box", "B4", REFUSED_FOLDER + "\\"))),
    ("wait", excel_done("set-save")),
    ("do", lambda: INJECT.update(on=True)),
    ("do", lambda: open_window(REFUSED_PATH, UNIQUE + " refused")),
    ("wait", lambda: win.reading is not None and win.reading.ok and win.footer().build_enabled),
    ("do", lambda: win.build_button.command()),
    ("wait", status_starts("Built", "No assembly", "Check", "SolidWorks cannot")),
    ("pause", 1.5),
    ("do", lambda: shoot("10-refused")),
    ("do", refused_check),
    ("do", lambda: log("refused document", result=close_refused())),
    # 6. W6, board WorkbookRightAngle: fixture A read and built. The refused stage's parts have fixture A's spur file
    # names (Gear_m2_N17), and SolidWorks keeps one document per file name: they are saved and closed first.
    ("do", lambda: log("closed the refused stage's documents in SolidWorks", left=close_ours())),
    ("do", lambda: excel("close")),
    ("wait", excel_done("close")),
    ("do", lambda: excel("open", W6_PATHS["A"])),
    ("wait", excel_done("open")),
    ("do", lambda: excel("set-save")),              # saved once by Excel (W6-PLAN §5)
    ("wait", excel_done("set-save")),
    ("do", lambda: app.out_folder.set(W6A_FOLDER)),  # the Box's Output folder is blank: the strip's is used
    ("do", lambda: open_window(W6_PATHS["A"], UNIQUE + " right angle")),
    ("wait", lambda: win.reading is not None and win.reading.ok and idle() and win.footer().build_enabled),
    ("pause", 1.0),
    ("do", lambda: shoot("11-right-angle-read")),
    ("do", lambda: speeds_panel("11-right-angle-read")),
    ("do", lambda: w6_read_check("A")),
    ("do", lambda: win.build_button.command()),
    ("wait", status_starts("Built", "Check", "SolidWorks cannot", "No assembly", "The gearbox")),
    ("pause", 1.5),
    ("do", lambda: shoot("12-right-angle-built")),
    ("do", w6_built_check),
    # 7. Board WorkbookCrossed: fixture B read; nothing built.
    ("do", lambda: log("closed the right-angle gearbox's documents in SolidWorks", left=close_ours())),
    ("do", lambda: excel("close")),
    ("wait", excel_done("close")),
    ("do", lambda: excel("open", W6_PATHS["B"])),
    ("wait", excel_done("open")),
    ("do", lambda: excel("set-save")),
    ("wait", excel_done("set-save")),
    ("do", lambda: app.out_folder.set(W6B_FOLDER)),
    ("do", lambda: open_window(W6_PATHS["B"], UNIQUE + " crossed")),
    ("wait", lambda: win.reading is not None and win.reading.ok and idle()),
    ("pause", 1.5),
    ("do", lambda: shoot("13-crossed-read")),
    ("do", lambda: speeds_panel("13-crossed-read")),
    ("do", lambda: w6_read_check("B")),
    # 8. W7, board WorkbookPlanetary: the 4 : 1 read and built.
    ("do", lambda: log("closed the crossed board's documents in SolidWorks", left=close_ours())),
    ("do", lambda: excel("close")),
    ("wait", excel_done("close")),
    ("do", lambda: excel("open", W6_PATHS["P"])),
    ("wait", excel_done("open")),
    ("do", lambda: excel("set-save")),
    ("wait", excel_done("set-save")),
    ("do", lambda: app.out_folder.set(W7_FOLDER)),
    ("do", lambda: open_window(W6_PATHS["P"], UNIQUE + " planetary")),
    ("wait", lambda: win.reading is not None and win.reading.ok and idle() and win.footer().build_enabled),
    ("pause", 1.5),
    ("do", lambda: shoot("14-planetary-read")),
    ("do", lambda: speeds_panel("14-planetary-read")),
    ("do", w7_read_check),
    ("do", lambda: win.build_button.command()),
    ("wait", status_starts("Built", "Check", "SolidWorks cannot", "No assembly", "The gearbox")),
    ("pause", 1.5),
    ("do", lambda: shoot("15-planetary-built")),
    ("do", w7_built_check),
    # 9. Board WorkbookPlanetaryCopies: Copies 5 typed in Excel.
    ("do", lambda: excel("set-save", ("Shafts", "H4", 5))),
    ("wait", excel_done("set-save")),
    ("wait", lambda: idle() and win.status.get().startswith("Fix the workbook")),
    ("pause", 1.5),
    ("do", lambda: shoot("16-planetary-copies-5")),
    ("do", w7_copies_check),
]
# 10. W8, the E4 transfer case: read, the chooser on 4L and on N, built.
W8_STEPS = ([] if ONLY == "w8" else [
    ("do", lambda: log("closed the planetary's documents in SolidWorks", left=close_ours())),
    ("do", lambda: excel("close")),
    ("wait", excel_done("close"))]) + [
    ("do", lambda: excel("open", W6_PATHS["E4"])),
    ("wait", excel_done("open")),
    ("do", lambda: excel("set-save")),
    ("wait", excel_done("set-save")),
    ("do", lambda: app.out_folder.set(W8_FOLDER)),
    ("do", lambda: open_window(W6_PATHS["E4"], UNIQUE + " transfer case")),
    ("wait", lambda: win.reading is not None and win.reading.ok and idle() and win.footer().build_enabled),
    ("pause", 1.5),
    ("do", lambda: shoot("17-transfer-case-read")),
    ("do", lambda: speeds_panel("17-transfer-case-read")),
    ("do", lambda: w8_mode_check(win.mode.get() or "2H")),
    ("do", lambda: w8_footer_whole("read")),
    ("do", lambda: w8_k12("read")),
    ("do", lambda: w8_choose("4L")),
    ("pause", 1.0),
    ("do", lambda: shoot("18-transfer-case-4L")),
    ("do", lambda: speeds_panel("18-transfer-case-4L")),
    ("do", lambda: w8_mode_check("4L")),
    ("do", lambda: w8_choose("N")),
    ("pause", 1.0),
    ("do", lambda: shoot("19-transfer-case-N")),
    ("do", lambda: speeds_panel("19-transfer-case-N")),
    ("do", lambda: w8_mode_check("N")),
    ("do", lambda: win.build_button.command()),
    ("wait", status_starts("Built", "Check", "SolidWorks cannot", "No assembly", "The gearbox")),
    ("pause", 1.5),
    ("do", lambda: shoot("20-transfer-case-built")),
    ("do", w8_built_check),
]
STEPS = W8_STEPS if ONLY == "w8" else STEPS + W8_STEPS
T0 = time.time()
DEADLINE = T0 + 2400
STALL = 900                  # s: a run in which no step completes for this long is hung (a build takes some minutes)
PROGRESS = {"at": time.time(), "finished": False}


def step():
    if PROGRESS["finished"]:
        return
    if time.time() > DEADLINE:
        log("TIMEOUT", left=[s[0] for s in STEPS][:3])
        FAILS.append("timeout")
        finish()
        return
    if not STEPS:
        finish()
        return
    current = STEPS[0]
    kind, arg = current
    try:
        if kind == "do":
            STEPS.pop(0)
            PROGRESS["at"] = time.time()
            arg()
            if win is not None:
                log("status", now=win.status.get())
        elif kind == "wait":
            if arg():
                STEPS.pop(0)
                PROGRESS["at"] = time.time()
                log("waited", status=win.status.get() if win is not None else "")
            elif win is not None and time.time() - LAST.get("said", 0) > 15:
                LAST["said"] = time.time()
                log("waiting", status=win.status.get())
        elif kind == "pause":
            STEPS.pop(0)
            PROGRESS["at"] = time.time()
            root.after(int(arg * 1000), step)
            return
    except Exception:  # noqa: BLE001
        import traceback
        log("STEP FAILED", step=kind, error=traceback.format_exc())
        FAILS.append("step failed")
        if STEPS and STEPS[0] is current:     # a "do" has already left the list; a failing "wait" has not
            STEPS.pop(0)
    root.after(200, step)


def callback_failed(exc, value, tb):
    """Tk's report_callback_exception: any exception in a Tk callback (a step, the window's own poll) is logged and
    ENDS the run as failed, never leaving the mainloop idle."""
    import traceback
    log("CALLBACK FAILED", error="".join(traceback.format_exception(exc, value, tb)))
    FAILS.append(f"a Tk callback raised {exc.__name__}")
    finish()


def watchdog():
    """Fails and closes the run if no step has completed for STALL seconds, or the deadline has passed."""
    if PROGRESS["finished"]:
        return
    if time.time() - PROGRESS["at"] > STALL or time.time() > DEADLINE + 60:
        log("WATCHDOG", what=f"no step completed for {time.time() - PROGRESS['at']:.0f} s",
            next=[s[0] for s in STEPS][:3], status=win.status.get() if win is not None else "")
        FAILS.append("watchdog: the run stalled")
        finish()
        return
    root.after(5000, watchdog)


def finish():
    if PROGRESS["finished"]:
        return
    PROGRESS["finished"] = True
    jobs.put(None)
    try:
        if win is not None:
            state("final")
            win.close()
    finally:
        end = time.time() + 40

        def later():
            if XT.is_alive() and time.time() < end:
                root.after(250, later)
            else:
                log("excel thread", alive=XT.is_alive())
                root.destroy()
        root.after(250, later)


root.report_callback_exception = callback_failed
root.after(500, step)
root.after(5000, watchdog)
root.mainloop()
log("closed in SolidWorks", left=close_ours())
CAM_STOP.set()
log("SOLIDWORKS CAM save questions answered No", pressed=CAM_PRESSED)
log("done", fails=FAILS)
with open(LOG_PATH, "w", encoding="utf-8", newline="\n") as handle:
    handle.write("\n".join(LINES) + "\n")
raise SystemExit(1 if FAILS else 0)
