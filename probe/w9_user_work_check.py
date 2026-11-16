r"""W9's S0 on SolidWorks (ISSUE-1-PLAN §4, *S0, W9a's first step, precisely*, with review 2's S5): a user's component
mated to an app gear while the app puts the train back to its built frames, and the What's Wrong probe P0.

python.exe probe/w9_user_work_check.py <repo src> <output folder under C:\> --pid PID [--log FILE]
                                       [--cases 0,A-a,A-b,B-a,B-b,C,C2] [--master DIR] [--skip-p0]

It imports ``probe/workbook_assembly_check.py`` (the W8 demonstration) for everything it can: the attach, the dialog
watch, the log, ``write_fixture`` and ``build_turning`` (the app's own Build), ``keep_master`` and ``copy_built`` (J24's
copy scheme), ``s7_drive_job`` (the drive's +37°) and ``s7_put_job`` (the put by the app's route: the app's locks, gear
mates and couplings on in the mode suppressed there, ``place_component`` per body, turned back on). That module
parses the same arguments; nothing in it is changed.

In this order, in one session:

1. **P0** (a probe ahead, alone, first): a scratch part built by the strip (a 20-tooth spur), SolidWorks' "show
   errors every rebuild" (``swUserPreferenceToggle_e`` 77, read from swconst.tlb) read and, if off, turned on for the
   probe and set back, read back. A user feature (a keyway: a Ø3 cut through the bore's edge, made by the session's
   own sketch and cut calls); then the app's ``Bore Diameter`` 10 -> 14, which leaves the keyway inside the bore, and,
   if no feature reports an error, -> 500 (the failing bore cut the macro database's rebuild-scope entry used). After
   each rebuild: its return, every feature's ``GetErrorCode2``, ``GetWhatsWrongCount``, and every visible window of
   SolidWorks' process listed and compared with the list before (What's Wrong opening or not). A window that is not
   SolidWorks' exempt notification box is a STOP (plan §0.3: any dialog) and nothing more runs. The part is closed
   unsaved.
2. **The master**: ``tests/workbook_fixtures.range_box`` (plan §3) written by the app's ``write_new``, saved once by
   Excel, built through the app's own Build (``build_turning``: the read, the plan, ``build_gearbox``, the finish and
   the record), kept as ``rangebox.master`` for W9a's demonstration.
3. **The user's parts**, built by the strip as a person would (``plan_for`` then ``swbuild.build``): ``Sprocket``
   (spur, 20 teeth, module 1.25, face 6, bore 10) and ``Housing`` (spur, 40 teeth, module 1.25, face 4, bore 30,
   standing in for a housing).
4. **The cases**, each on its own ``copy_built`` of the master: the sprocket inserted twice and the housing once by
   ``AddComponent5`` into the reopened assembly with its configurations (the first use of that context, ahead of
   W9c's M5, said in the log), each put at an identity frame (sprocket 1 at z 30 in front of Sun on Input's axis,
   sprocket 2 at z -70 behind RangeSlv's travel on Output's axis, the housing at z 60) and the housing fixed. Mated by
   the parts' named axes and planes (``Gear Axis`` to the layout's ``Input Axis`` / ``Output Axis``, ``Top Plane`` to
   ``Top Plane``) and the lock by components, through the app's own ``add_mate``; findings.py records the axes
   selected alike by FeatureByName + Select2, SelectByID2 by name and GetCorresponding + Select4 (shaft_axis_mates),
   and no face is picked. Every new mate's flag read in every configuration as made, then set on (C2's tie suppressed
   in H and N) and read back; each new component's state and the housing's IsFixed read in every configuration shown.
   Saved by the app's ``save_as`` under a new name, closed unsaved, reopened.

   - ``0``, the control: both sprockets on their layout axes only, nothing of the user's on a gear;
   - ``A-a`` / ``A-b``: sprocket 1 also locked to Sun (``UserLock1``), route (a) / route (b);
   - ``B-a`` / ``B-b``: sprocket 2 also locked to RangeSlv (``UserLock2``, the sliding train), route (a) / (b);
   - ``C``: A plus sprocket 1's Top plane coincident with the fixed housing's (``UserTie``, the grounded tie);
   - ``C2`` (the plan's C′): C with ``UserTie`` suppressed in H and N, on in L.

   Before any put, in the mode the copy opens in and with nothing shown: every body's and user component's frame,
   ``GetConstrainedStatus``, every mate's error code and its flag in every configuration, ``GetSaveFlag`` of every
   document before and after (the tie read; a read that marks a document is a STOP). Then in H, then in L, each shown
   and rebuilt: the same read (the tie read in that mode); the drive's +37° (``s7_drive_job``); the read; where the
   tie is on, a moving put against it (Sun alone turned +37° by the app's put route), the read; the put back to the
   mode's built frames by ``s7_put_job`` — route (a) with the user's mates as they are, route (b) with the user's lock
   on the put train added to the mates it suppresses in that mode and turned back on, its flags read in every
   configuration; the read. After the last put every mode shown, rebuilt, and every body read (s7's discipline).

Judged, per case and mode: the drive turned Sun +37° and each locked sprocket by the same angle (its pose relative to
its gear unchanged); the put took every body to its target to 1e-6 with the app's mates back on; each sprocket's pose
relative to its gear afterwards as it was before the drive (it went with its gear); every mate's code 0 and flag as
set in every configuration; the tie read 2 (free) for every mated body in 0, A and B and in C2's H, not free in C and
C2's L. Proposed findings at the end: ``USER_MATE_PUT_ROUTE`` ("carried" when route (a) held in A and B in both modes,
"suppress around" when only route (b) came back clean; neither is a STOP), ``USER_TIE_READ`` and the What's Wrong
reading. STOPs (plan §0.3 and §4): any dialog; a read marking a document; a put SolidWorks accepts that leaves a gear
off its frame with no error code; a user mate route (b) cannot turn back on; a new component or mate whose state per
configuration does not read back as set; a mode put earlier found off its built frames in the last read; a put that
holds in neither route. The readings go to ``w9-s0-<ts>.json`` beside the log.
"""

import dataclasses
import json
import math
import os
import shutil
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import workbook_assembly_check as W  # noqa: E402  (parses <src> <out> --pid PID [--log FILE])

import win32gui  # noqa: E402
import win32process  # noqa: E402
import xlhelp  # noqa: E402

from gear_generator import findings, swbuild, swcom  # noqa: E402
from gear_generator.gears import plan_for, kind_for  # noqa: E402
from gear_generator.spec import GearSpec  # noqa: E402
from gear_generator.workbook import layout as wb_layout  # noqa: E402

say, check, note, call = W.say, W.check, W.note, W.call
OUT, PID = W.OUT, W.PID
ARGS = sys.argv
CHOSEN = ARGS[ARGS.index("--cases") + 1].split(",") if "--cases" in ARGS else None
MASTER_GIVEN = ARGS[ARGS.index("--master") + 1] if "--master" in ARGS else ""
SKIP_P0 = "--skip-p0" in ARGS

SHOW_ERRORS_EVERY_REBUILD = 77          # swUserPreferenceToggle_e.swShowErrorsEveryRebuild (swconst.tlb, 34.1 and 32.5)
COMPONENT_FULLY_RESOLVED = 2            # swComponentSuppressionState_e
IDENTITY = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
TURN = 37.0
TOL = 1e-6
SPROCKET = GearSpec(kind="spur", module="1.25", teeth="20", face_width="6", bore="10", name="Sprocket")
HOUSING = GearSpec(kind="spur", module="1.25", teeth="40", face_width="4", bore="30", name="Housing")
P0_PART = GearSpec(kind="spur", module="1.25", teeth="20", face_width="6", bore="10", name="P0_Scratch")
S1_AT, S2_AT, HOUSING_AT = (0.0, 0.0, 30.0), (0.0, 0.0, -70.0), (0.0, 0.0, 60.0)
SPROCKET_OF = {"Sprocket-1": "Sun", "Sprocket-2": "RangeSlv"}
ROUTE_MODES = ("H", "L")

# key -> (folder, title, lock1, lock2, tie modes (None: no tie), route)
CASES = (
    ("0", "c0", "the control: both sprockets on their layout axes only, nothing of the user's on a gear",
     False, False, None, "a"),
    ("A-a", "cAa", "sprocket 1 on Input Axis and locked to Sun; route (a), the user's mates left on", True, False, None,
     "a"),
    ("A-b", "cAb", "sprocket 1 on Input Axis and locked to Sun; route (b), UserLock1 suppressed around the put", True,
     False, None, "b"),
    ("B-a", "cBa", "sprocket 2 on Output Axis and locked to RangeSlv; route (a)", False, True, None, "a"),
    ("B-b", "cBb", "sprocket 2 on Output Axis and locked to RangeSlv; route (b), UserLock2 suppressed around the put",
     False, True, None, "b"),
    ("C", "cC", "A plus sprocket 1's Top plane coincident with the fixed housing's (the grounded tie); route (a)",
     True, False, ("H", "N", "L"), "a"),
    ("C2", "cC2", "C with the tie suppressed in H and N, on in L (C' of the plan: a user mate whose flag differs by "
                  "mode); route (a)", True, False, ("L",), "a"),
)
RESULT = {"cases": {}, "p0": {}, "master": "", "stops": []}


class S0Stop(Exception):
    """A STOP of plan §0.3 or §4: the run ends there, what was read kept."""


def stop(what):
    """A STOP: a FAIL, listed with W8's STOPs and in the JSON, and the run ends."""
    W.stop_check(False, what)
    RESULT["stops"].append(what)
    raise S0Stop(what)


def stop_check(ok, what):
    if not ok:
        stop(what)
    check(True, what)
    return True


def watch_check(where):
    """Plan §0.3, any dialog: a window the watch logged (W8's watch notes one outside a configuration call and makes
    one during it a STOP) ends the run here, as does any STOP W8's helpers raised. SolidWorks' notification box and
    its balloon tips are not dialogs (the coordinator's ruling)."""
    windows = [n for n in W.NOTES if n.startswith("a SolidWorks window")]
    if windows or W.STOPS:
        stop(f"{where}: {windows or W.STOPS}")


# -- small helpers ------------------------------------------------------------------------------------------------


def job_in(asm, work):
    """A worker job on ``asm`` (``W.in_assembly``: the app's open, the build ended whatever happened)."""
    return W.in_assembly(asm, work)


def relative(gear, other):
    """``other``'s frame in ``gear``'s: (R_gᵀ R_o, R_gᵀ (p_o − p_g)), rotations by rows."""
    r, p = gear
    s, q = other
    rt_s = tuple(sum(float(r[k * 3 + i]) * float(s[k * 3 + j]) for k in range(3)) for i in range(3) for j in range(3))
    d = [float(q[k]) - float(p[k]) for k in range(3)]
    return rt_s, tuple(sum(float(r[k * 3 + i]) * d[k] for k in range(3)) for i in range(3))


def sw_windows():
    """Every visible top-level window of SolidWorks' process: (class, title), any class."""
    found = []

    def each(hwnd, _):
        try:
            if win32gui.IsWindowVisible(hwnd) and win32process.GetWindowThreadProcessId(hwnd)[1] == PID:
                found.append((hwnd, win32gui.GetClassName(hwnd), win32gui.GetWindowText(hwnd)))
        except Exception:  # noqa: BLE001
            pass
        return True
    try:
        win32gui.EnumWindows(each, None)
    except Exception:  # noqa: BLE001
        pass
    return found


def feature_errors(doc):
    """Every feature of a part, in tree order: (name, type, GetErrorCode2 code, warning)."""
    out = []
    feature = call(doc, "FirstFeature")
    while feature is not None:
        flag = swcom._out_bool()  # noqa: SLF001
        answer = call(feature, "GetErrorCode2", flag)
        if isinstance(answer, tuple):
            code = answer[0] if answer else 0
            warning = answer[1] if len(answer) > 1 else getattr(flag, "value", None)
        else:
            code, warning = answer, getattr(flag, "value", None)
        out.append((str(call(feature, "Name")), swcom._type_name(feature), swcom._by_ref(code),  # noqa: SLF001
                    bool(warning) if warning is not None else None))
        feature = call(feature, "GetNextFeature")
    return out


def frames_text(frames):
    return {g: [list(map(lambda v: round(float(v), 9), f[0])), list(map(lambda v: round(float(v), 6), f[1]))]
            for g, f in frames.items()}


# -- P0: does a failing rebuild open What's Wrong ----------------------------------------------------------------


def section_p0(worker):
    say("== P0  a rebuild that fails on a user feature, with \"show errors every rebuild\" as found (read; turned on "
        "for the probe if off, set back, read back): does What's Wrong open? Alone, first, under the dialog watch and "
        "a 240 s watchdog")
    folder = W.fresh_folder("p0")
    path = os.path.join(folder, P0_PART.stem() + ".SLDPRT")
    kind = kind_for(P0_PART)
    plan = plan_for(P0_PART, kind.derive(P0_PART), "", path)
    result = W.run(worker, lambda s: swbuild.build(s, plan), 600)
    check(result.ok and bool(result.saved), f"P0: the scratch part built by the strip and saved: ok {result.ok}, "
                                            f"saved {result.saved!r}, failures {list(result.failures)}")
    out = RESULT["p0"]
    windows_before = sw_windows()
    out["windows_before"] = [(c, t) for _, c, t in windows_before]
    say(f"fact    P0: SolidWorks' visible windows before: {out['windows_before']}")

    def work(s):
        got = {"steps": []}
        app = s._app  # noqa: SLF001
        got["toggle_found"] = bool(call(app, "GetUserPreferenceToggle", SHOW_ERRORS_EVERY_REBUILD))
        if not got["toggle_found"]:
            call(app, "SetUserPreferenceToggle", SHOW_ERRORS_EVERY_REBUILD, True)
        got["toggle_for_probe"] = bool(call(app, "GetUserPreferenceToggle", SHOW_ERRORS_EVERY_REBUILD))
        try:
            doc = s._doc()  # noqa: SLF001
            s.open_sketch("p0k", 1)
            s.sketch_circle("p0c", (5.0, 0.0), 1.5)
            s.close_sketch("p0k", "User Keyway Sketch")
            s.cut_extrude("p0cut", "p0k", "User Keyway")
            got["made_rebuild"] = bool(s.rebuild())
            got["made_errors"] = [e for e in feature_errors(doc) if e[2]]
            for value in ("14", "500"):
                s.set_global_variable("Bore Diameter", value)
                rebuilt = bool(s.rebuild())
                errors = [e for e in feature_errors(doc) if e[2]]
                count = call(call(doc, "Extension"), "GetWhatsWrongCount")
                got["steps"].append({"bore": value, "rebuild": rebuilt, "errors": errors,
                                     "whats_wrong_count": swcom._by_ref(count)})  # noqa: SLF001
                if errors or not rebuilt:
                    break
        finally:
            if not got["toggle_found"]:
                call(app, "SetUserPreferenceToggle", SHOW_ERRORS_EVERY_REBUILD, False)
            got["toggle_after"] = bool(call(app, "GetUserPreferenceToggle", SHOW_ERRORS_EVERY_REBUILD))
        return got
    started = time.monotonic()
    try:
        got = W.run(worker, job_in(path, work), 240)
    except W.WorkerHung as exc:
        out["hung"] = str(exc)
        stop(f"P0: the failing rebuild did not answer in 240 s ({exc}): a modal window is likely up")
    out.update(got)
    out["seconds"] = round(time.monotonic() - started, 1)
    time.sleep(1.0)
    new, seen = [], {x[0] for x in windows_before}
    for _ in range(8):                                   # What's Wrong would come up as SolidWorks' UI catches up
        for h, c, t in sw_windows():
            if h not in seen:
                seen.add(h)
                texts = tuple(xlhelp.child_texts(h)[:8])
                new.append((c, t, texts))
        time.sleep(1.0)
    out["windows_new"] = new
    say(f"fact    P0: \"show errors every rebuild\" found {got['toggle_found']}, for the probe "
        f"{got['toggle_for_probe']}, after {got['toggle_after']}; the keyway made (rebuild {got['made_rebuild']}, "
        f"features in error {got['made_errors']})")
    for step in got["steps"]:
        say(f"fact    P0: Bore Diameter -> {step['bore']}: rebuild returned {step['rebuild']}; features in error "
            f"{step['errors']}; GetWhatsWrongCount {step['whats_wrong_count']}")
    say(f"fact    P0: windows of SolidWorks' process new after the failing rebuild: {new or 'none'} "
        f"({out['seconds']} s)")
    check(got["toggle_after"] == got["toggle_found"], "P0: \"show errors every rebuild\" is back as found")
    failed = any(step["errors"] or not step["rebuild"] for step in got["steps"])
    user = any(any(e[0].startswith("User Keyway") for e in step["errors"]) for step in got["steps"])
    out["failed"], out["user_feature_failed"] = failed, user
    check(failed, f"P0: a rebuild failed (the user's keyway in error: {user}), so the reading answers the question")
    left = W.run(worker, W.quit_in(folder))
    check(not left, f"P0: the scratch part closed unsaved: left {left}")
    # A window that counts: a dialog (#32770) or any titled one; SolidWorks' untitled notification box (the
    # coordinator's ruling) and an untitled balloon or tooltip do not.
    counted = [w for w in new if (w[0] == "#32770" or w[1]) and not (not w[1] and w[2] == W.NOTIFICATION_TEXTS)]
    out["whats_wrong_opened"] = any("wrong" in w[1].lower() for w in counted)
    out["windows_counted"] = counted
    if counted:
        stop(f"P0: a window came up after the failing rebuild: {counted} (plan §0.3: any dialog, What's Wrong "
             f"among them)")
    return out


# -- the master and the user's parts -----------------------------------------------------------------------------


def spec_range_box(folder=""):
    made = W.w8_fixtures().range_box()
    return dataclasses.replace(made, box=dataclasses.replace(made.box, output_folder=folder))


def build_master(worker, excel):
    say("== master  RangeBox (ISSUE-1-PLAN §3) through the app's own Build, kept as rangebox.master: S0's master and "
        "W9a's demonstration's")
    folder, path, book, desk = W.write_fixture(worker, excel, "rangebox", spec_range_box)
    a = desk.a
    modes = {m.name: m for m in a.report.modes}
    warnings = [d.message for d in a.diagnostics if d.level == "warning"]
    check(len(warnings) == 4 and list(modes) == ["H", "N", "L"]
          and modes["H"].engaged == (("RangeSlv", "HighDog"),) and modes["N"].engaged == ()
          and modes["L"].engaged == (("RangeSlv", "LowDog"),)
          and abs(modes["L"].ratio - (1 + 55 / 29)) < 1e-9 and abs(modes["H"].ratio - 1.0) < 1e-9,
          f"master: the read is §3's: {len(warnings)} warnings, modes {list(modes)}, engaged "
          f"{[(n, m.engaged) for n, m in modes.items()]}, ratios {[(n, m.ratio) for n, m in modes.items()]}")
    plan, result = W.build_turning(worker, desk, "master", None, None)
    box = desk.record.gearbox
    check(list(box.modes) == ["H", "N", "L"] and bool(box.assembly) and os.path.isfile(box.assembly),
          f"master: the record holds the turning RangeBox with the modes {list(box.modes)}: {box.assembly}")
    say(f"fact    master: bodies {W.bodies(box)}; fixed {list(box.fixed)}; drag {list(box.drag)}; mates "
        f"{[(m.name, m.kind, list(m.gears), list(m.modes or [])) for m in box.mates]}")
    say(f"fact    master: the build's per-mode checks {getattr(result, 'modes', None)}")
    kept = W.keep_master(worker, folder, "rangebox")
    if not kept:
        stop("master: rangebox could not be kept as rangebox.master")
    RESULT["master"] = kept
    return kept


def build_user_parts(worker):
    say("== user parts  Sprocket (spur 20 teeth, module 1.25, face 6, bore 10) and Housing (spur 40, module 1.25, face 4, "
        "bore 30, standing in) built by the strip's own plan_for and swbuild.build")
    folder = W.fresh_folder("user-parts")
    paths = []
    for spec in (SPROCKET, HOUSING):
        path = os.path.join(folder, spec.stem() + ".SLDPRT")
        kind = kind_for(spec)
        plan = plan_for(spec, kind.derive(spec), "", path)
        result = W.run(worker, lambda s, p=plan: swbuild.build(s, p), 600)
        check(result.ok and bool(result.saved), f"user parts: {os.path.basename(path)} built and saved: ok "
                                                f"{result.ok}, failures {list(result.failures)}")
        paths.append(path)
    left = W.run(worker, W.quit_in(folder))
    check(not left, f"user parts: closed: left {left}")
    return folder


# -- the jobs of a case --------------------------------------------------------------------------------------------


class Case:
    def __init__(self, worker, master, parts, key, sub, title, lock1, lock2, tie, route):
        self.worker, self.key, self.title = worker, key, title
        self.lock1, self.lock2, self.tie, self.route = lock1, lock2, tie, route
        say(f"-- S0 case {key}: {title}")
        try:
            self.folder = W.copy_built(master, sub)
        except W.CopyStop as exc:
            stop(f"S0 {key}: the copy of the master stopped: {exc}")
        for name in ("Sprocket.SLDPRT", "Housing.SLDPRT"):
            shutil.copy2(os.path.join(parts, name), os.path.join(self.folder, name))
        path = os.path.join(self.folder, "RangeBox.xlsx")
        self.desk = W.Desk(path, worker, strip=self.folder)
        self.desk.read()
        self.box0 = self.desk.record.gearbox
        check(W.under(self.box0.assembly, self.folder) and list(self.box0.modes) == ["H", "N", "L"],
              f"S0 {key}: the copy reads as built, its assembly in the copy: {os.path.basename(self.box0.assembly)}")
        self.box = self.box0
        self.modes = list(self.box0.modes)
        self.names = dict(W.bodies(self.box0))
        self.users = []
        self.json = {"case": key, "title": title, "route": route, "tie": list(tie) if tie else None,
                     "copy": os.path.basename(self.folder), "steps": []}
        RESULT["cases"][key] = self.json
        self.rel0 = {}            # mode -> sprocket -> its pose in its gear's frame, before the drive

    # the setup ---------------------------------------------------------------------------------------------------

    def user_mates(self):
        """(handle, kind, a, b, name) of the case's mates, in the order made."""
        axes = {s.shaft: s.axis_name for s in wb_layout.shaft_layouts(self.desk.a.spec)}
        out = [("ua1", "coincident", "u1:Gear Axis", f"lay:{axes['Input']}", "UserAxis1"),
               ("ua2", "coincident", "u2:Gear Axis", f"lay:{axes['Output']}", "UserAxis2")]
        if self.lock1:
            out.append(("ul1", "lock", "sun", "u1", "UserLock1"))
        if self.lock2:
            out.append(("ul2", "lock", "slv", "u2", "UserLock2"))
        if self.tie:
            out.append(("ut", "coincident", "u1:plane2", "uh:plane2", "UserTie"))
        return out

    def setup(self):
        say(f"step    S0 {self.key}: the user's work added. AddComponent5 into the reopened assembly with its "
            "configurations (H, N, L) is used here first, ahead of W9c's M5")
        asm = self.box0.assembly
        spr, hou = os.path.join(self.folder, "Sprocket.SLDPRT"), os.path.join(self.folder, "Housing.SLDPRT")
        mates = self.user_mates()
        modes = self.modes
        tie_off = [m for m in modes if self.tie and m not in self.tie]

        def work(s):
            out = {"components": {}, "mates": {}}
            s.open_document(spr)
            s.open_document(hou)
            s.open_document(asm)
            out["active"] = s.active_configuration()
            out["configurations"] = s.configurations()
            for handle, path, at in (("u1", spr, S1_AT), ("u2", spr, S2_AT), ("uh", hou, HOUSING_AT)):
                name = s.add_component(handle, path, at)
                s.place_component(handle, IDENTITY, at, kind=swcom.ASSEMBLY_TRAIN)
                out["components"][handle] = name
            s.fix_component("uh")
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            s.find_component("lay", self.box0.layout_component)
            s.find_component("sun", self.names["Sun"])
            s.find_component("slv", self.names["RangeSlv"])
            made = []
            for handle, kind, a, b, name in mates:
                if kind == "lock":
                    kept, _ = s.add_mate(handle, "lock", a, b, name=name)
                else:
                    kept, _ = s.add_mate(handle, kind, a, b, 0.0, name)
                made.append((handle, kept))
                out["mates"][kept] = {"status": s.mate_status(kept)}
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            for handle, kept in made:
                out["mates"][kept]["as_made"] = s.mate_suppression(handle, modes)
            for handle, kept in made:
                s.set_mate_suppressed_in(handle, False, modes)
                if kept == "UserTie" and tie_off:
                    s.set_mate_suppressed_in(handle, True, tie_off)
                out["mates"][kept]["set"] = s.mate_suppression(handle, modes)
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            out["states"] = [(m.name, m.code, m.suppressed) for m in s.mate_states()]
            return out
        got = self.run("setup", job_in(asm, work), 900)
        self.users = [got["components"]["u1"], got["components"]["u2"], got["components"]["uh"]]
        say(f"fact    S0 {self.key}: inserted {got['components']} with {got['active']} active "
            f"(configurations {got['configurations']})")
        for name, m in got["mates"].items():
            say(f"fact    S0 {self.key}: {name}: AddMate5 status {m['status']}; flags as made {m['as_made']}; set "
                f"{m['set']}")
        wrong = {}
        for name, m in got["mates"].items():
            want = {c: bool(name == "UserTie" and c in tie_off) for c in modes}
            if m["set"] != want:
                wrong[name] = (m["set"], want)
        stop_check(not wrong and self.users[:2] == ["Sprocket-1", "Sprocket-2"],
                   f"S0 {self.key}: every new mate reads back as set in every configuration (wrong {wrong}); the "
                   f"sprocket inserted twice is {self.users[:2]}")
        bad = [(n, c) for n, c, sup in got["states"] if c and not sup]
        check(not bad, f"S0 {self.key}: every mate on in {got['active']} reads error code 0 after the setup: {bad}")
        self.json["setup"] = got
        self.per_mode_states()
        self.save_and_reopen()

    def per_mode_states(self):
        """Each mode shown and rebuilt: each new component's GetSuppression2 (a suppressed one set resolved there, the
        set read back) and the housing's IsFixed (fixed there when floating, read back)."""
        users = self.users
        modes = self.modes

        def work(s):
            out = {}
            route = findings.COMPONENT_FIND_ROUTE
            for mode in modes:
                s.show_configuration(mode)
                s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
                here = {}
                for name in users:
                    comp = swcom.Session._component_by(route, s._doc(), name)  # noqa: SLF001
                    state = None if comp is None else int(swcom._read(comp, "GetSuppression2"))  # noqa: SLF001
                    here[name] = {"state": state}
                    if state == 0:
                        call(comp, "SetSuppression2", COMPONENT_FULLY_RESOLVED)
                        comp = swcom.Session._component_by(route, s._doc(), name)  # noqa: SLF001
                        here[name]["set"] = int(swcom._read(comp, "GetSuppression2"))  # noqa: SLF001
                        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
                s.find_component(f"pmh{mode}", users[2])
                fixed = s.is_fixed(f"pmh{mode}")
                here["housing_fixed"] = fixed
                if not fixed:
                    s.fix_component(f"pmh{mode}")
                    here["housing_fixed_after"] = s.is_fixed(f"pmh{mode}")
                here["mates"] = [(m.name, m.code, m.suppressed) for m in s.mate_states()]
                out[mode] = here
            s.show_configuration(modes[0])
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            out["active_after"] = s.active_configuration()
            return out
        got = self.run("per-mode states", job_in(self.box0.assembly, work), 600)
        for mode in modes:
            here = got[mode]
            say(f"fact    S0 {self.key}: in {mode} (shown): component states "
                f"{({n: here[n] for n in users})}; housing fixed {here['housing_fixed']}"
                + (f" -> fixed there, reads {here.get('housing_fixed_after')}" if not here["housing_fixed"] else ""))
            bad = [(n, c) for n, c, sup in here["mates"] if c and not sup]
            check(not bad, f"S0 {self.key}: in {mode} every mate on there reads error code 0: {bad}")
        unresolved = [(m, n) for m in modes for n in users
                      if got[m][n]["state"] not in (2, 3) and got[m][n].get("set") not in (2, 3)]
        unfixed = [m for m in modes if not got[m]["housing_fixed"] and not got[m].get("housing_fixed_after")]
        stop_check(not unresolved and not unfixed, f"S0 {self.key}: every new component resolved in every configuration "
                   f"(not: {unresolved}) and the housing fixed in each (not: {unfixed}), as set")
        self.json["per_mode_setup"] = got

    def save_and_reopen(self):
        new = os.path.join(self.folder, f"RangeBox_S0_{self.key.replace('-', '_')}.SLDASM")

        def work(s):
            active = s.active_configuration()
            kept = s.save_as(new)
            return active, kept, W.folder_flags(s, self.folder)
        active, kept, flags = self.run("save_as", job_in(self.box0.assembly, work), 300)
        check(W.store.same_path(kept, new),
              f"S0 {self.key}: saved by the app's save_as under a new name with {active} active: "
              f"{os.path.basename(kept)}; marked after {W.marked(flags) or 'none'}")
        if W.TAG["major"] == 32:          # as W8's end_clean: 2024 asks about modified documents in a modal box
            saved = W.run(self.worker, W.save_modified_in(self.folder))
            say(f"        S0 {self.key}: SolidWorks 2024, the copy's modified documents saved before the close: {saved}")
        left = W.run(self.worker, W.quit_in(self.folder))
        check(not left, f"S0 {self.key}: the copy's documents closed after the save_as: left {left}")
        self.box = dataclasses.replace(self.box0, assembly=new)
        got = self.run("reopen", job_in(new, lambda s: (s.active_configuration(), W.folder_flags(s, self.folder))), 300)
        say(f"fact    S0 {self.key}: reopened {os.path.basename(new)} in {got[0]}; marked straight after the open: "
            f"{W.marked(got[1]) or 'none'}")
        self.json["saved_as"] = os.path.basename(new)
        self.json["reopened_in"] = got[0]

    # reads -------------------------------------------------------------------------------------------------------

    def run(self, what, job, timeout=600):
        try:
            return W.run(self.worker, job, timeout)
        except W.WorkerHung:
            raise
        except S0Stop:
            raise
        except Exception as exc:  # noqa: BLE001
            text = f"{type(exc).__name__}: {exc}"
            W.frame_none_stop([text], f"S0 {self.key} {what}")
            raise AssertionError(f"S0 {self.key} {what}: {text}") from None

    def read(self, label, flags_matter=False):
        """In the active configuration, nothing shown or rebuilt: every body's and user component's frame and
        GetConstrainedStatus, every mate's error code and its flag in every configuration; GetSaveFlag of every
        document of the copy before and after."""
        pairs = W.bodies(self.box) + [(u, u) for u in self.users]
        modes = self.modes

        def work(s):
            out = {"flags_before": W.folder_flags(s, self.folder), "active": s.active_configuration(),
                   "frames": {}, "status": {}, "mates": {}, "by_mode": {}}
            for i, (g, n) in enumerate(pairs):
                s.find_component(f"rd{i}", n)
                out["frames"][g] = s.component_frame(f"rd{i}")
                out["status"][g] = s.constrained_status(f"rd{i}")
            for i, m in enumerate(s.mate_states()):
                out["mates"][m.name] = (m.code, m.suppressed)
                s.find_mate(f"rm{i}", m.name)
                out["by_mode"][m.name] = s.mate_suppression(f"rm{i}", modes)
            out["flags_after"] = W.folder_flags(s, self.folder)
            return out
        got = self.run(f"read {label}", job_in(self.box.assembly, work))
        dirtied = sorted(n for n, v in got["flags_after"].items() if v and not got["flags_before"].get(n))
        stop_check(not dirtied, f"S0 {self.key} {label}: the read marks no document modified (GetSaveFlag before "
                                f"{W.marked(got['flags_before']) or 'none'}, after {W.marked(got['flags_after']) or 'none'})")
        train = [g for g, _ in W.bodies(self.box) if g not in self.box.fixed]
        tie = {g: got["status"][g] for g in train if got["status"][g] != findings.COMPONENT_UNDER_DEFINED}
        users = {u: got["status"][u] for u in self.users}
        errors = {n: c for n, (c, sup) in got["mates"].items() if c and not sup}
        rel = {u: relative(got["frames"][g], got["frames"][u]) for u, g in SPROCKET_OF.items()}
        say(f"read    S0 {self.key} {label} (active {got['active']}): train not free {tie or 'none'} (every other mated "
            f"body 2); user components {users}; mates in error {errors or 'none'}; user mates' flags "
            f"{({n: f for n, f in got['by_mode'].items() if n.startswith('User')})}")
        got["tie"] = tie
        got["errors"] = errors
        got["rel"] = rel
        self.json["steps"].append({"step": label, "active": got["active"], "flags_before": got["flags_before"],
                                   "flags_after": got["flags_after"], "status": got["status"], "mates": got["mates"],
                                   "by_mode": got["by_mode"], "tie": tie, "frames": frames_text(got["frames"])})
        return got

    def show(self, mode):
        def work(s):
            s.show_configuration(mode)
            return bool(s.rebuild(kind=swcom.ASSEMBLY_TRAIN)), s.active_configuration()
        got = self.run(f"show {mode}", job_in(self.box.assembly, work), 300)
        check(swbuild.on_in((mode,), got[1]), f"S0 {self.key}: {mode} shown and rebuilt (rebuild {got[0]})")

    # the steps ---------------------------------------------------------------------------------------------------

    def user_locks(self):
        return [n for n, on in (("UserLock1", self.lock1), ("UserLock2", self.lock2)) if on]

    def tie_on(self, mode):
        return bool(self.tie) and mode in self.tie

    def targets(self, mode):
        record = W.mode_record_frames(self.desk, mode)
        carriers = [g for g in record if g.endswith(wb_layout.CARRIER_ID_SUFFIX)]
        built = {g: record[g] for g in carriers + [g for g in record if g not in carriers] if g not in self.box.fixed}
        return built

    def judge_rel(self, label, mode, got, want_with):
        """Each sprocket's pose relative to its gear against the one before the drive in ``mode``: same (it went with
        its gear) or not; ``want_with`` the sprockets that are locked."""
        out = {}
        for u, g in SPROCKET_OF.items():
            gap = W.frame_gap(got["rel"][u], self.rel0[mode][u])
            out[u] = gap
        say(f"        {label}: each sprocket's pose in its gear's frame against before the drive: "
            f"{({u: f'{v:.1e}' for u, v in out.items()})} (locked: {want_with or 'none'})")
        return out

    def drive(self, mode, plane, built_sun):
        label = f"drive +{TURN:g} in {mode}"
        before = self.read(f"before the drive in {mode}")
        self.rel0[mode] = before["rel"]
        out = self.run(label, W.s7_drive_job(self.box, mode, TURN, plane, built_sun), 300 if self.tie_on(mode) else 600)
        after = self.read(f"after the drive in {mode}")
        sun = self.box.drag[0]
        turned = W.turn_degrees(before["frames"][sun][0], after["frames"][sun][0])
        turns = {u: W.turn_degrees(before["frames"][u][0], after["frames"][u][0]) for u in SPROCKET_OF}
        gear_turns = {u: W.turn_degrees(before["frames"][g][0], after["frames"][g][0]) for u, g in SPROCKET_OF.items()}
        made_gap = max(W.frame_gap(out["before"][g], out["made"][g]) for g in out["before"]) if "made" in out else None
        say(f"step    S0 {self.key} {label}: errors {out['errors']} cleanup {out['cleanup']}; making the drive moved "
            f"{made_gap if made_gap is None else f'{made_gap:.1e}'}; {sun} turned {turned}; sprockets turned {turns}, "
            f"their gears {gear_turns}")
        locked = [u for u, on in (("Sprocket-1", self.lock1), ("Sprocket-2", self.lock2)) if on]
        rel = self.judge_rel(label, mode, after, locked)
        step = {"drive": {"mode": mode, "errors": out["errors"], "cleanup": out["cleanup"], "sun_turned": turned,
                          "sprocket_turns": turns, "gear_turns": gear_turns, "rel_gap": rel,
                          "mates_left": out.get("mates")}}
        self.json["steps"][-1].update(step)
        if self.tie_on(mode):
            say(f"fact    S0 {self.key}: the tie is on in {mode}: the drive's turn against it is read as a fact "
                f"({sun} turned {turned})")
        else:
            check(not out["errors"] and not out["cleanup"] and turned is not None and abs(turned - TURN) <= 1e-6 * TURN,
                  f"S0 {self.key} {label}: {sun} turned {turned}° for {TURN:g}° and the drive was deleted")
            moved_with = all(rel[u] <= TOL for u in locked)
            free_still = all(turns[u] is not None and abs(turns[u]) <= 1e-6 for u in SPROCKET_OF if u not in locked)
            check(moved_with and free_still, f"S0 {self.key} {label}: each locked sprocket turned with its gear (its "
                  f"pose in the gear's frame unchanged) and each sprocket not locked stood still: locked {locked}, "
                  f"turns {turns}")
        return after

    def put(self, mode, label, targets, route, user_off, control=False):
        """``s7_put_job`` in ``mode``: the app's route mates there, plus ``user_off`` (route b) suppressed in ``mode``
        around the put and turned back on. ``control``: the moving put against a tie, whose target is off the built
        frames on purpose (plan §0.3's silent-put STOP is for a put back to them)."""
        off = W.s7_route_mates(self.box, mode) + list(user_off)
        out = self.run(label, W.s7_put_job(self.box, mode, targets, off), 900)
        after = self.read(f"after {label}")
        put = out["puts"]
        gap_on, at_on = W.frames_gap(out.get("mates_on", {}), put) if put else (None, "")
        gap_off, at_off = W.frames_gap(out.get("mates_off", {}), put) if put and "mates_off" in out else (None, "")
        gap_read, at_read = W.frames_gap(after["frames"], put) if put else (None, "")
        user_flags = {n: out["flags"].get(n) for n in user_off}
        say(f"step    S0 {self.key} {label}: route ({route}), suppressed in {mode} around the put {off}; errors "
            f"{out['errors']} cleanup {out['cleanup']}; bodies put {list(put)}; against their targets with the mates "
            f"off {gap_off if gap_off is None else f'{gap_off:.1e}'} at {at_off or '-'}, back on "
            f"{gap_on if gap_on is None else f'{gap_on:.1e}'} at {at_on or '-'}, read after "
            f"{gap_read if gap_read is None else f'{gap_read:.1e}'} at {at_read or '-'}; the user's mates suppressed "
            f"for it, flags after {user_flags}")
        locked = [u for u, on in (("Sprocket-1", self.lock1), ("Sprocket-2", self.lock2)) if on]
        rel = self.judge_rel(label, mode, after, locked)
        user_errors = {n: c for n, c in after["errors"].items() if n.startswith("User")}
        app_errors = {n: c for n, c in after["errors"].items() if not n.startswith("User")}
        held = (not out["errors"] and not out["cleanup"] and gap_read is not None and gap_read <= TOL
                and gap_on is not None and gap_on <= TOL)
        with_gear = all(rel[u] <= TOL for u in locked)
        flags_back = all(f is not None and not any(f.values()) for f in user_flags.values()) if user_off else True
        everything = held and with_gear and not after["errors"] and flags_back
        self.json["steps"][-1].update(put={"mode": mode, "label": label, "route": route, "off": off,
                                           "errors": out["errors"], "cleanup": out["cleanup"], "bodies": list(put),
                                           "gap_mates_off": gap_off, "gap_mates_on": gap_on, "gap_read": gap_read,
                                           "at": at_read, "rel_gap": rel, "user_flags": user_flags,
                                           "user_errors": user_errors, "app_errors": app_errors, "held": held,
                                           "with_gear": with_gear, "flags_back": flags_back, "clean": everything})
        if put and not control and not held and not out["errors"] and not after["errors"]:
            stop(f"S0 {self.key} {label}: SolidWorks took the put and left a body off its target "
                 f"({gap_read if gap_read is None else f'{gap_read:.1e}'} at {at_read}) with no error code "
                 "(plan §0.3)")
        if user_off and not flags_back:
            stop(f"S0 {self.key} {label}: a user mate route (b) suppressed did not come back on in every configuration: "
                 f"{user_flags} (plan §0.3)")
        return {"held": held, "with_gear": with_gear, "clean": everything, "errors": out["errors"],
                "user_errors": user_errors, "app_errors": app_errors, "flags_back": flags_back}

    def final(self):
        """Every mode shown and rebuilt, every body and user component read, each mode's mates' codes; the first mode
        shown last."""
        pairs = W.bodies(self.box) + [(u, u) for u in self.users]
        modes = self.modes

        def work(s):
            out = {"frames": {}, "mates": {}, "status": {}}
            for mode in modes:
                s.show_configuration(mode)
                s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
                here, status = {}, {}
                for i, (g, n) in enumerate(pairs):
                    s.find_component(f"fn{i}", n)
                    here[g] = s.component_frame(f"fn{i}")
                    status[g] = s.constrained_status(f"fn{i}")
                out["frames"][mode] = here
                out["status"][mode] = status
                out["mates"][mode] = {m.name: (m.code, m.suppressed) for m in s.mate_states()}
            s.show_configuration(modes[0])
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            return out
        got = self.run("the last read", job_in(self.box.assembly, work), 900)
        summary = {}
        for mode in modes:
            frames = got["frames"][mode]
            built = W.mode_record_frames(self.desk, mode)
            gap, at = W.frames_gap(frames, {g: f for g, f in built.items()})
            rel = {u: W.frame_gap(relative(frames[g], frames[u]), self.rel0.get(mode, self.rel0.get("H", {})).get(u,
                   relative(frames[g], frames[u]))) for u, g in SPROCKET_OF.items()}
            errors = {n: c for n, (c, sup) in got["mates"][mode].items() if c and not sup}
            sun = W.turn_degrees(built[self.box.drag[0]][0], frames[self.box.drag[0]][0])
            summary[mode] = {"gap": gap, "at": at, "rel": rel, "errors": errors, "sun_from_built": sun}
            say(f"read    S0 {self.key} the last read, {mode} shown: every body against its built frame, largest "
                f"{gap:.1e} at {at or '-'} ({self.box.drag[0]} at {sun}° from built); sprockets in their gears' frames "
                f"against before the drive {({u: f'{v:.1e}' for u, v in rel.items()})}; mates in error {errors or 'none'}")
        self.json["last"] = {"summary": summary, "frames": {m: frames_text(f) for m, f in got["frames"].items()},
                             "status": got["status"], "mates": got["mates"]}
        return summary

    def end(self):
        W.end_copy(self.worker, self.folder, f"S0 {self.key}")


def run_case(worker, master, parts, spec):
    key, sub, title, lock1, lock2, tie, route = spec
    c = Case(worker, master, parts, key, sub, title, lock1, lock2, tie, route)
    outcome = {"modes": {}}
    c.json["outcome"] = outcome
    try:
        c.setup()
        first = c.read(f"the tie read, before any put, in the mode the copy opens in, nothing shown")
        outcome["tie_unshown"] = {"active": first["active"], "tie": first["tie"]}
        sun = c.box.drag[0]
        plane, _ = W.drive_assumptions(c.desk, sun, f"S0 {key}")
        built_sun = W.wanted(c.desk)[sun]
        for mode in ROUTE_MODES:
            W.guard()
            c.show(mode)
            shown = c.read(f"the tie read in {mode}, shown, before its put")
            expect_tie = c.tie_on(mode)
            check(bool(shown["tie"]) == expect_tie,
                  f"S0 {key}: in {mode} the train reads {'not free (a tie)' if shown['tie'] else 'free'}, as "
                  f"{'the tie on there' if expect_tie else 'no tie'} wants: {shown['tie'] or 'every mated body 2'}")
            here = {"tie": shown["tie"], "user_status": {u: shown["status"][u] for u in c.users}}
            c.drive(mode, plane, built_sun)
            if expect_tie:
                spin = c.put(mode, f"the moving put against the tie in {mode} (Sun alone +{TURN:g}°)",
                             W.s7_spin(sun, TURN), "a", [], control=True)
                here["against_tie"] = spin
                say(f"fact    S0 {key}: a put of Sun +{TURN:g}° against the tie in {mode}: errors {spin['errors']}; "
                    f"held {spin['held']}; user mates in error {spin['user_errors']}")
            built = c.targets(mode)
            user_off = c.user_locks() if route == "b" else []
            p = c.put(mode, f"the put back to the built frames in {mode}", lambda before, b=built: dict(b), route,
                      user_off)
            here["put"] = p
            outcome["modes"][mode] = here
        outcome["last"] = c.final()
        # The last put's mode must still stand at its built frames once every mode has been shown and rebuilt (a put
        # that holds only until the solver next runs, plan §4's STOP). An earlier mode is read as a fact: W8 measured
        # a turn reaching every mode and a put holding in its own (findings TURN_PER_CONFIGURATION_ON_* False,
        # POSITIONS_PER_CONFIGURATION_ON_* True), so H stands turned by L's drive unless an Update puts it again.
        last = ROUTE_MODES[-1]
        s = outcome["last"][last]
        if s["gap"] > TOL:
            stop(f"S0 {key}: in the last read {last}, put last, stands off its built frames ({s['gap']:.1e} at "
                 f"{s['at']}): a mode found moved after the every-mode read (plan §4)")
        check(True, f"S0 {key}: in the last read {last}, put last, every body at its built frame ({s['gap']:.1e})")
        for mode in ROUTE_MODES[:-1]:
            say(f"fact    S0 {key}: in the last read {mode}, put before {last}'s drive, {sun} stands "
                f"{outcome['last'][mode]['sun_from_built']}° from built (largest gap {outcome['last'][mode]['gap']:.1e} "
                f"at {outcome['last'][mode]['at'] or '-'}); W8's findings have a turn reach every mode")
    finally:
        c.end()
    return c


# -- the proposal ----------------------------------------------------------------------------------------------------


def propose():
    cases = RESULT["cases"]

    def clean(key):
        o = cases.get(key, {}).get("outcome", {}).get("modes", {})
        return all(o.get(m, {}).get("put", {}).get("clean") for m in ROUTE_MODES) and len(o) == len(ROUTE_MODES)
    have = [k for k in ("A-a", "A-b", "B-a", "B-b") if k in cases]
    route_a = all(clean(k) for k in ("A-a", "B-a") if k in cases) and {"A-a", "B-a"} <= set(have)
    route_b = all(clean(k) for k in ("A-b", "B-b") if k in cases) and {"A-b", "B-b"} <= set(have)
    proposal = "carried" if route_a else "suppress around" if route_b else None
    say(f"propose USER_MATE_PUT_ROUTE: {proposal!r} (route (a) held clean in A and B in H and L: {route_a}; route (b) "
        f"came back clean: {route_b}; cases run {have})")
    if have and {"A-a", "A-b", "B-a", "B-b"} <= set(have) and proposal is None:
        RESULT["stops"].append("a put that holds in neither route")
        W.stop_check(False, "S0: a put holds in neither route (plan §4's STOP)")
    tie = {}
    for key in ("C", "C2"):
        o = cases.get(key, {}).get("outcome", {})
        if o:
            tie[key] = {"unshown": o.get("tie_unshown"), "shown": {m: o.get("modes", {}).get(m, {}).get("tie")
                                                                    for m in ROUTE_MODES}}
    say(f"propose USER_TIE_READ: {tie}")
    RESULT["proposal"] = {"USER_MATE_PUT_ROUTE": proposal, "route_a_clean": route_a, "route_b_clean": route_b,
                          "USER_TIE_READ": tie, "WHATS_WRONG": RESULT["p0"].get("whats_wrong_opened")}


# -- main ------------------------------------------------------------------------------------------------------------


def main():
    os.makedirs(OUT, exist_ok=True)
    started = time.strftime("%Y%m%d-%H%M%S")
    json_path = os.path.join(os.path.dirname(os.path.abspath(W.LOG_PATH)), f"w9-s0-{started}.json")
    say(f"run     {time.strftime('%Y-%m-%d %H:%M:%S')}; W9 S0 (ISSUE-1-PLAN §4) from {W.SRC}{W.snapshot()}; cases "
        f"{CHOSEN or [c[0] for c in CASES]}; master {MASTER_GIVEN or 'built here'}; P0 {'skipped' if SKIP_P0 else 'first'}")
    worker = swcom.Worker(W.connect_pid)
    W.CURRENT["worker"] = worker
    label, pid, revision = W.run(worker, lambda s: (s.label, s.pid, s.revision), 120)
    W.TAG.update(major=revision[0], version=".".join(str(v) for v in revision), revision=tuple(revision))
    RESULT.update(revision=list(revision), snapshot=W.snapshot().strip(" ()").replace("snapshot: ", ""))
    say(f"attach  {label}, PID {pid}; {W.memory()}")
    if pid != PID:
        say(f"STOP    attached to PID {pid}, not {PID}")
        worker.shutdown()
        return 2
    before = W.run(worker, W.open_titles, 120)
    say(f"open    before: {before}")
    say(f"findings COMPONENT_FIND_ROUTE {findings.COMPONENT_FIND_ROUTE!r}, AXIS_MATE_ROUTE {findings.AXIS_MATE_ROUTE!r}, "
        f"COMPONENT_UNDER_DEFINED {findings.COMPONENT_UNDER_DEFINED}, swcom.positions_per_configuration here "
        f"{swcom.positions_per_configuration(W.TAG['revision'])}")
    watch = W.DialogWatch()
    watch.start()
    excel = None
    try:
        try:
            if not SKIP_P0:
                section_p0(worker)
                watch_check("P0")
            excel = xlhelp.Excel(visible=True)
            say(f"excel   started our own Excel, PID {excel.pid}, {excel.version}")
            master = MASTER_GIVEN or build_master(worker, excel)
            watch_check("the master's build")
            parts = build_user_parts(worker)
            watch_check("the user's parts")
            for spec in CASES:
                if CHOSEN and spec[0] not in CHOSEN:
                    continue
                W.guard()
                started_case = time.monotonic()
                try:
                    run_case(worker, master, parts, spec)
                except AssertionError as exc:
                    check(False, f"S0 {spec[0]}: {exc}")
                    for line in traceback.format_exc().splitlines()[-6:]:
                        say("        " + line)
                say(f"time    S0 {spec[0]}: {time.monotonic() - started_case:.0f} s; {W.memory()}")
                watch_check(f"S0 {spec[0]}")
            propose()
        except S0Stop as exc:
            say(f"STOP    the run ends at its STOP: {exc}")
        except W.WorkerHung as exc:
            check(False, f"S0: {exc}; the run ends here, nothing more is asked of SolidWorks")
            RESULT["stops"].append(str(exc))
        except Exception as exc:  # noqa: BLE001
            check(False, f"S0 raised {type(exc).__name__}: {exc}")
            for line in traceback.format_exc().splitlines():
                say("        " + line)
    finally:
        books = W.close_books()
        if books:
            say(f"excel   left open: {books}, closed without saving")
        if excel is not None:
            try:
                excel.quit()
                say("excel   quit our own Excel")
            except Exception as exc:  # noqa: BLE001
                say(f"excel   quit trouble: {exc}")
        if W.HUNG["on"]:
            say("close   the SolidWorks worker is hung: nothing closed at the end; SolidWorks is left as it is")
        else:
            try:
                left = W.run(worker, W.close_ours, 600)
                after = W.run(worker, W.open_titles, 120)
                say(f"close   left of ours {left}; stray {[t for t in after if t not in before]}; lost "
                    f"{[t for t in before if t not in after]}; {W.memory()}")
            except W.WorkerHung as exc:
                say(f"close   not closed: {exc}")
        watch.stop.set()
        say(f"dialogs progress boxes seen {W.PROGRESS}; other windows the watch logged: {W.WINDOWS['count']}")
        worker.shutdown()
        RESULT["fails"], RESULT["notes"] = list(W.FAILS), list(W.NOTES)
        with open(json_path, "w", encoding="utf-8") as handle:
            json.dump(RESULT, handle, indent=1, default=str)
        say(f"result  S0's readings written to {json_path}; the master kept at {RESULT['master'] or MASTER_GIVEN}")
    for line in W.NOTES:
        say(f"noted   {line}")
    for line in W.STOPS:
        say(f"stop    {line}")
    say(f"done    {len(W.FAILS)} failed: {W.FAILS}; {len(W.NOTES)} noted; {len(W.STOPS)} STOP(s)")
    return 0 if not W.FAILS else 1


if __name__ == "__main__":
    code = 1
    try:
        code = main()
    finally:
        with open(W.LOG_PATH, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(W.LOG) + "\n")
    raise SystemExit(code)
