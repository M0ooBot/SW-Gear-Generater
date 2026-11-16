r"""W9's S0 on SolidWorks (ISSUE-1-PLAN §4, *S0, W9a's first step, precisely*, with review 2's S5): a user's component
mated to an app gear while the app puts the train back to its built frames, and the What's Wrong probe P0.

python.exe probe/w9_user_work_check.py <repo src> <output folder under C:\> --pid PID [--log FILE]
                                       [--cases 0,A-a,A-b,A-c1,...,D,C,C2] [--master DIR] [--skip-p0]

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
4. **The cases**, each on its own ``copy_built`` of the master: the sprocket inserted twice (three times in E, the
   third at z 40) and the housing once by ``AddComponent5`` into the reopened assembly with its configurations (the
   first use of that context, ahead of W9c's M5, said in the log), each put at an identity frame (sprocket 1 at z 30 in front of Sun on Input's axis,
   sprocket 2 at z -70 behind RangeSlv's travel on Output's axis, the housing at z 60) and the housing fixed. Mated by
   the parts' named axes and planes (``Gear Axis`` to the layout's ``Input Axis`` / ``Output Axis``, ``Top Plane`` to
   ``Top Plane``) and the lock by components, through the app's own ``add_mate``; findings.py records the axes
   selected alike by FeatureByName + Select2, SelectByID2 by name and GetCorresponding + Select4 (shaft_axis_mates),
   and no face is picked. Every new mate's flag read in every configuration as made, then set on (C2's tie suppressed
   in H and N) and read back; each new component's state and the housing's IsFixed read in every configuration shown.
   Saved by the app's ``save_as`` under a new name, closed unsaved, reopened.

   The 2026 run at 55a82c1 found that neither route keeps a locked sprocket on its gear: the user's lock re-takes
   the put's offset (findings.LOCK_RETAKES_AN_OFFSET). The coordinator's ruling added route (c): every user component
   rigid to an app gear through the user's locks (directly or through another user component) is put with the gear by
   the gear's rigid motion, U_target = G_target · inv(G_before) · U_before, in the configuration shown, as
   ``swbuild._put_train`` puts the app's own locked pairs (``put_c_job``). (c1) leaves the user's locks on; (c2)
   suppresses them in the mode around the puts and turns them back on, each flag read back.

   - ``0``, the control: both sprockets on their layout axes only; L shown and read after H's drive and before H's put
     (whether the drive's turn reaches another mode);
   - ``A-*``: Sprocket-1 also locked to Sun (``UserLock1``); ``B-*``: Sprocket-2 locked to RangeSlv (``UserLock2``,
     the sliding train); ``E-*``: A plus a third sprocket locked to Sprocket-1 (``UserLock3``, a chain); each under
     route ``a``, ``b``, ``c1`` or ``c2``;
   - ``D``: no lock: Sprocket-2 on Output Axis and its Front plane coincident with RangeSlv's, which slides between
     modes; nothing of the user's moved by the put;
   - ``C``: A plus Sprocket-1's Top plane coincident with the fixed housing's (``UserTie``, the grounded tie), route
     (c1); ``C2`` (the plan's C′): C with ``UserTie`` suppressed in H and N, on in L.

   By default the cases 0, A-c1, A-c2, B-c1, B-c2, E-c1, E-c2, D, C and C2 run (``--cases`` picks others).

   Before any put, in the mode the copy opens in and with nothing shown: every body's and user component's frame,
   ``GetConstrainedStatus``, every mate's error code and its flag in every configuration, ``GetSaveFlag`` of every
   document before and after (the tie read; a read that marks a document is a STOP). Then in H, then in L, each shown
   and rebuilt: the same read; the drive's +37° (``s7_drive_job``); the read; the put back to the mode's built frames
   by the case's route; the read. Under route (c) then a further rebuild, a second drive and a second put, each read.
   After the last put every mode shown, rebuilt, and every body read (s7's discipline).

Judged against each sprocket's pose in its gear's frame as set up (the first read), to 1e-6 on every rotation entry
(about 6e-5°) and every origin coordinate (mm): the drive carries a locked sprocket exactly; a put is clean when every
body put (the user's included) reads at its target to 1e-6 with the mates back on, each locked sprocket at its pose
of the setup, no mate in error and the user's flags back on in every configuration. D: Sprocket-2's z less RangeSlv's
as set up in each mode. Proposed: ``USER_MATE_PUT_ROUTE`` (the (c) variant clean in A, B and E, c1 preferred, writing
least of the user's), ``USER_TIE_READ``, D's reading and the What's Wrong reading. STOPs (plan §0.3 and §4): any
dialog; a read marking a document; a put SolidWorks accepts that leaves a body off its target with no error code; a
user mate that cannot be turned back on; a new component or mate whose state per configuration does not read back as
set; the last put's mode found off its built frames in the last read; route (c) holding in neither variant. The
readings go to ``w9-s0-<ts>.json`` beside the log.
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
S1_AT, S2_AT, S3_AT, HOUSING_AT = (0.0, 0.0, 30.0), (0.0, 0.0, -70.0), (0.0, 0.0, 40.0), (0.0, 0.0, 60.0)
# Each sprocket's gear, for its pose in that gear's frame: Sprocket-3 is locked to Sprocket-1, so rigid to Sun.
GEAR_OF = {"Sprocket-1": "Sun", "Sprocket-2": "RangeSlv", "Sprocket-3": "Sun"}
ROUTE_MODES = ("H", "L")
ROUTES = {"a": "route (a): the user's mates left on, nothing of the user's moved",
          "b": "route (b): the user's locks suppressed in the mode around the put and turned back on",
          "c1": "route (c1): the user's locked components put with their gears by the gear's rigid motion, the user's "
                "locks left on",
          "c2": "route (c2): the user's locked components put with their gears, the user's locks suppressed in the "
                "mode around the puts and turned back on, as _put_train does with the app's locks"}


def case(key, sub, title, mates, route, tie=None, twice=False, l_probe=False):
    """A case: its key, folder, title, the user's mates it makes (axis1, axis2, lock1, lock2, lock3: Sprocket-3 locked
    to Sprocket-1, tie, slide2: Sprocket-2's Front plane coincident with RangeSlv's), the route, the modes the tie is
    on in, ``twice``: a rebuild, a second drive and a second put after the first put in each mode; ``l_probe``: L
    shown and read after H's drive and before H's put."""
    return {"key": key, "sub": sub, "title": title, "mates": tuple(mates), "route": route, "tie": tie,
            "twice": twice, "l_probe": l_probe}


A_MATES, B_MATES = ("axis1", "axis2", "lock1"), ("axis1", "axis2", "lock2")
E_MATES = ("axis1", "axis2", "lock1", "lock3")
CASES = (
    case("0", "c0", "the control: both sprockets on their layout axes only, nothing of the user's on a gear; L read "
                    "after H's drive and before H's put", ("axis1", "axis2"), "a", l_probe=True),
    case("A-a", "cAa", "Sprocket-1 on Input Axis and locked to Sun", A_MATES, "a"),
    case("A-b", "cAb", "Sprocket-1 on Input Axis and locked to Sun", A_MATES, "b"),
    case("A-c1", "cAc1", "Sprocket-1 on Input Axis and locked to Sun", A_MATES, "c1", twice=True),
    case("A-c2", "cAc2", "Sprocket-1 on Input Axis and locked to Sun", A_MATES, "c2", twice=True),
    case("B-a", "cBa", "Sprocket-2 on Output Axis and locked to RangeSlv", B_MATES, "a"),
    case("B-b", "cBb", "Sprocket-2 on Output Axis and locked to RangeSlv", B_MATES, "b"),
    case("B-c1", "cBc1", "Sprocket-2 on Output Axis and locked to RangeSlv", B_MATES, "c1", twice=True),
    case("B-c2", "cBc2", "Sprocket-2 on Output Axis and locked to RangeSlv", B_MATES, "c2", twice=True),
    case("E-c1", "cEc1", "A plus Sprocket-3 locked to Sprocket-1 (a chain of user locks rigid to Sun)", E_MATES, "c1",
         twice=True),
    case("E-c2", "cEc2", "A plus Sprocket-3 locked to Sprocket-1 (a chain of user locks rigid to Sun)", E_MATES, "c2",
         twice=True),
    case("D", "cD", "no lock: Sprocket-2 on Output Axis and its Front plane coincident with RangeSlv's (which slides "
                    "between modes); nothing of the user's moved by the put", ("axis1", "axis2", "slide2"), "a"),
    case("C", "cC", "A plus Sprocket-1's Top plane coincident with the fixed housing's (the grounded tie)",
         A_MATES + ("tie",), "c1", tie=("H", "N", "L")),
    case("C2", "cC2", "C with the tie suppressed in H and N, on in L (C' of the plan: a user mate whose flag differs "
                      "by mode)", A_MATES + ("tie",), "c1", tie=("L",)),
)
DEFAULT_CASES = ("0", "A-c1", "A-c2", "B-c1", "B-c2", "E-c1", "E-c2", "D", "C", "C2")
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
    out["windows_before"] = sorted(c for _, c, _ in windows_before)    # classes only: the main window's title names
    say(f"fact    P0: SolidWorks' visible windows before, by class: {out['windows_before']}")   # the licence

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


def fmt(gaps):
    return {k: f"{v:.1e}" for k, v in gaps.items()}


def carry(gear_before, gear_target, user_before):
    """Route (c): the user's component moved by its gear's rigid motion, U_target = G_target · inv(G_before) ·
    U_before (rotations by rows, origins in mm)."""
    (rb, pb), (rt, pt), (ru, pu) = gear_before, gear_target, user_before
    m = [[sum(float(rt[i * 3 + k]) * float(rb[j * 3 + k]) for k in range(3)) for j in range(3)] for i in range(3)]
    rot = tuple(sum(m[i][k] * float(ru[k * 3 + j]) for k in range(3)) for i in range(3) for j in range(3))
    d = [float(pu[k]) - float(pb[k]) for k in range(3)]
    at = tuple(sum(m[i][k] * d[k] for k in range(3)) + float(pt[i]) for i in range(3))
    return rot, at


def put_c_job(box, mode, built, ties, user_off, users):
    """Route (c) in ``mode``, as ``swbuild._put_train`` puts the app's own locked pairs: ``mode`` shown and rebuilt;
    every app lock, gear mate and coupling on in ``mode`` (``s7_route_mates``) and, for (c2), the user's locks
    ``user_off`` suppressed in ``mode`` alone and rebuilt; every frame read; each app body put to ``built`` (carriers
    first), then each user component in ``ties`` (component -> its gear) put by its gear's rigid motion from the frames
    just read, each by ``place_component`` (read back); rebuilt; every frame read; every mate suppressed here read and
    turned back on in ``mode`` where it reads suppressed, whatever happened; rebuilt; every frame read; their flags in
    every configuration."""
    pairs = W.bodies(box) + [(u, u) for u in users]
    name_of = dict(pairs)
    off = W.s7_route_mates(box, mode) + list(user_off)

    def work(s):
        out = {"errors": [], "cleanup": [], "puts": {}, "off": off}
        s.show_configuration(mode)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        out["active"] = s.active_configuration()

        def frames(prefix):
            got = {}
            for i, (g, n) in enumerate(pairs):
                s.find_component(f"{prefix}{i}", n)
                got[g] = s.component_frame(f"{prefix}{i}")
            return got
        held = []
        try:
            for i, name in enumerate(off):
                s.find_mate(f"cm{i}", name)
                held.append(i)
                s.set_mate_suppressed_in(f"cm{i}", True, [mode])
            if off:
                s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            out["before"] = frames("cb")
            targets = dict(built)
            for u, g in ties.items():
                targets[u] = carry(out["before"][g], built[g], out["before"][u])
            for i, (g, frame) in enumerate(targets.items()):
                s.find_component(f"cp{i}", name_of[g])
                s.place_component(f"cp{i}", frame[0], frame[1], kind=swcom.ASSEMBLY_TRAIN)
                out["puts"][g] = frame
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            out["mates_off"] = frames("co")
        except Exception as exc:  # noqa: BLE001 - said; the mates still go back on below
            out["errors"].append(f"{type(exc).__name__}: {exc}")
        finally:
            for i in held:
                try:
                    if s.mate_suppression(f"cm{i}", [mode])[mode]:
                        s.set_mate_suppressed_in(f"cm{i}", False, [mode])
                except Exception as exc:  # noqa: BLE001
                    out["cleanup"].append(f"{off[i]} back on: {type(exc).__name__}: {exc}")
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        out["mates_on"] = frames("cn")
        out["flags"] = {off[i]: s.mate_suppression(f"cm{i}", list(box.modes)) for i in held}
        return out
    return job_in(box.assembly, work)


class Case:
    def __init__(self, worker, master, parts, spec):
        self.worker, self.spec = worker, spec
        self.key, self.title, self.route, self.tie = spec["key"], spec["title"], spec["route"], spec["tie"]
        self.mates = spec["mates"]
        say(f"-- S0 case {self.key}: {self.title}; {ROUTES[self.route]}")
        try:
            self.folder = W.copy_built(master, spec["sub"])
        except W.CopyStop as exc:
            stop(f"S0 {self.key}: the copy of the master stopped: {exc}")
        for name in ("Sprocket.SLDPRT", "Housing.SLDPRT"):
            shutil.copy2(os.path.join(parts, name), os.path.join(self.folder, name))
        path = os.path.join(self.folder, "RangeBox.xlsx")
        self.desk = W.Desk(path, worker, strip=self.folder)
        self.desk.read()
        self.box0 = self.desk.record.gearbox
        check(W.under(self.box0.assembly, self.folder) and list(self.box0.modes) == ["H", "N", "L"],
              f"S0 {self.key}: the copy reads as built, its assembly in the copy: {os.path.basename(self.box0.assembly)}")
        self.box = self.box0
        self.modes = list(self.box0.modes)
        self.names = dict(W.bodies(self.box0))
        self.users = []
        self.json = {"case": self.key, "title": self.title, "route": self.route, "mates": list(self.mates),
                     "tie": list(self.tie) if self.tie else None, "copy": os.path.basename(self.folder), "steps": []}
        RESULT["cases"][self.key] = self.json
        self.rel_orig = {}        # each sprocket's pose in its gear's frame as set up (the first read)
        self.dz_orig = None       # D: Sprocket-2's origin z less RangeSlv's, per mode, as set up
        self.rel0 = {}            # mode -> sprocket -> its pose before that mode's first drive

    # the user's work ---------------------------------------------------------------------------------------------

    def ties(self):
        """Each user component rigid to an app gear through the user's locks (directly or through another user
        component), in the order put: component -> its gear."""
        out = {}
        if "lock1" in self.mates:
            out["Sprocket-1"] = "Sun"
        if "lock2" in self.mates:
            out["Sprocket-2"] = "RangeSlv"
        if "lock3" in self.mates and "lock1" in self.mates:
            out["Sprocket-3"] = "Sun"
        return out

    def user_locks(self):
        return [n for n, k in (("UserLock1", "lock1"), ("UserLock2", "lock2"), ("UserLock3", "lock3")) if k in self.mates]

    def user_mates(self):
        """(handle, kind, a, b, name) of the case's mates, in the order made."""
        axes = {s.shaft: s.axis_name for s in wb_layout.shaft_layouts(self.desk.a.spec)}
        made = {"axis1": ("ua1", "coincident", "u1:Gear Axis", f"lay:{axes['Input']}", "UserAxis1"),
                "axis2": ("ua2", "coincident", "u2:Gear Axis", f"lay:{axes['Output']}", "UserAxis2"),
                "lock1": ("ul1", "lock", "sun", "u1", "UserLock1"),
                "lock2": ("ul2", "lock", "slv", "u2", "UserLock2"),
                "lock3": ("ul3", "lock", "u1", "u3", "UserLock3"),
                "slide2": ("us2", "coincident", "u2:plane1", "slv:plane1", "UserSlide2"),
                "tie": ("ut", "coincident", "u1:plane2", "uh:plane2", "UserTie")}
        return [made[k] for k in ("axis1", "axis2", "lock1", "lock2", "lock3", "slide2", "tie") if k in self.mates]

    def setup(self):
        say(f"step    S0 {self.key}: the user's work added by AddComponent5 into the reopened assembly with its "
            "configurations (H, N, L), ahead of W9c's M5")
        asm = self.box0.assembly
        spr, hou = os.path.join(self.folder, "Sprocket.SLDPRT"), os.path.join(self.folder, "Housing.SLDPRT")
        mates = self.user_mates()
        modes = self.modes
        tie_off = [m for m in modes if self.tie and m not in self.tie]
        inserts = [("u1", spr, S1_AT), ("u2", spr, S2_AT)] + ([("u3", spr, S3_AT)] if "lock3" in self.mates else []) \
            + [("uh", hou, HOUSING_AT)]

        def work(s):
            out = {"components": {}, "mates": {}}
            s.open_document(spr)
            s.open_document(hou)
            s.open_document(asm)
            out["active"] = s.active_configuration()
            out["configurations"] = s.configurations()
            for handle, path, at in inserts:
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
        self.users = [got["components"][h] for h, _, _ in inserts]
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
        expected = ["Sprocket-1", "Sprocket-2"] + (["Sprocket-3"] if "lock3" in self.mates else []) + ["Housing-1"]
        stop_check(not wrong and self.users == expected,
                   f"S0 {self.key}: every new mate reads back as set in every configuration (wrong {wrong}); the "
                   f"components are {self.users}")
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
                s.find_component(f"pmh{mode}", "Housing-1")
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
        except (W.WorkerHung, S0Stop):
            raise
        except Exception as exc:  # noqa: BLE001
            text = f"{type(exc).__name__}: {exc}"
            W.frame_none_stop([text], f"S0 {self.key} {what}")
            raise AssertionError(f"S0 {self.key} {what}: {text}") from None

    def rel_of(self, frames):
        return {u: relative(frames[g], frames[u]) for u, g in GEAR_OF.items() if u in frames}

    def rel_gaps(self, rel, against):
        return {u: W.frame_gap(rel[u], against[u]) for u in rel if u in against}

    def dz(self, frames):
        return float(frames["Sprocket-2"][1][2]) - float(frames["RangeSlv"][1][2])

    def read(self, label):
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
        rel = self.rel_of(got["frames"])
        if not self.rel_orig:
            self.rel_orig = rel
        angles = {g: W.turn_degrees(IDENTITY, got["frames"][g][0]) for g in ("Sun", "RangeSlv") + tuple(GEAR_OF)
                  if g in got["frames"]}
        gaps = self.rel_gaps(rel, self.rel_orig)
        extra = ""
        if "slide2" in self.mates:
            dz = self.dz(got["frames"])
            extra = f"; Sprocket-2 z less RangeSlv's {dz:+.9f} mm"
            got["dz"] = dz
        say(f"read    S0 {self.key} {label} (active {got['active']}): train not free {tie or 'none'} (every other mated "
            f"body 2); user components {users}; mates in error {errors or 'none'}; turns from identity "
            f"{({g: None if a is None else round(a, 6) for g, a in angles.items()})}; sprockets' poses in their "
            f"gears' frames against the setup {({u: f'{v:.1e}' for u, v in gaps.items()})}{extra}")
        got.update(tie=tie, errors=errors, rel=rel, rel_gap=gaps, angles=angles)
        self.json["steps"].append({"step": label, "active": got["active"], "flags_before": got["flags_before"],
                                   "flags_after": got["flags_after"], "status": got["status"], "mates": got["mates"],
                                   "by_mode": got["by_mode"], "tie": tie, "angles": angles, "rel_gap": gaps,
                                   "dz": got.get("dz"), "frames": frames_text(got["frames"])})
        return got

    def show(self, mode):
        def work(s):
            s.show_configuration(mode)
            return bool(s.rebuild(kind=swcom.ASSEMBLY_TRAIN)), s.active_configuration()
        got = self.run(f"show {mode}", job_in(self.box.assembly, work), 300)
        check(swbuild.on_in((mode,), got[1]), f"S0 {self.key}: {mode} shown and rebuilt (rebuild {got[0]})")

    def rebuild_read(self, mode, label):
        """A further rebuild in ``mode`` (shown again and rebuilt), then the read."""
        self.show(mode)
        return self.read(label)

    # the steps ---------------------------------------------------------------------------------------------------

    def tie_on(self, mode):
        return bool(self.tie) and mode in self.tie

    def targets(self, mode):
        record = W.mode_record_frames(self.desk, mode)
        carriers = [g for g in record if g.endswith(wb_layout.CARRIER_ID_SUFFIX)]
        return {g: record[g] for g in carriers + [g for g in record if g not in carriers] if g not in self.box.fixed}

    def drive(self, mode, plane, built_sun, label):
        before = self.read(f"before {label}")
        self.rel0.setdefault(mode, before["rel"])
        out = self.run(label, W.s7_drive_job(self.box, mode, TURN, plane, built_sun),
                       300 if self.tie_on(mode) else 600)
        after = self.read(f"after {label}")
        sun = self.box.drag[0]
        turned = W.turn_degrees(before["frames"][sun][0], after["frames"][sun][0])
        turns = {u: W.turn_degrees(before["frames"][u][0], after["frames"][u][0]) for u in GEAR_OF if u in self.users}
        carried = self.rel_gaps(after["rel"], before["rel"])
        say(f"step    S0 {self.key} {label}: errors {out['errors']} cleanup {out['cleanup']}; {sun} turned {turned}; "
            f"sprockets turned {turns}; each sprocket's pose in its gear's frame against before the drive "
            f"{({u: f'{v:.1e}' for u, v in carried.items()})}")
        tied = list(self.ties())
        self.json["steps"][-1].update(drive={"mode": mode, "label": label, "errors": out["errors"],
                                             "cleanup": out["cleanup"], "sun_turned": turned, "sprocket_turns": turns,
                                             "carried_gap": carried})
        if self.tie_on(mode):
            say(f"fact    S0 {self.key}: the tie is on in {mode}: the drive's turn against it is read as a fact "
                f"({sun} turned {turned})")
            return after
        check(not out["errors"] and not out["cleanup"] and turned is not None and abs(turned - TURN) <= 1e-6 * TURN,
              f"S0 {self.key} {label}: {sun} turned {turned}° for {TURN:g}° and the drive was deleted")
        loose = [u for u in turns if u not in tied and not (u == "Sprocket-2" and "slide2" in self.mates)]
        check(all(carried[u] <= TOL for u in tied) and all(turns[u] is not None and abs(turns[u]) <= 1e-6
                                                            for u in loose),
              f"S0 {self.key} {label}: each locked sprocket carried exactly by its gear (its pose in the gear's frame "
              f"unchanged to {TOL:g}) and each sprocket not locked stood still: locked {tied}, turns {turns}")
        if self.route in ("c1", "c2"):
            check(all(after["rel_gap"][u] <= TOL for u in tied),
                  f"S0 {self.key} {label}: under route (c) each locked sprocket stands at its pose of the setup in its "
                  f"gear's frame (no offset re-taken): {fmt({u: after['rel_gap'][u] for u in tied})}")
        return after

    def put(self, mode, label):
        """The put back to ``mode``'s built frames by the case's route."""
        built = self.targets(mode)
        tied = self.ties()
        if self.route in ("a", "b"):
            user_off = self.user_locks() if self.route == "b" else []
            off = W.s7_route_mates(self.box, mode) + user_off
            out = self.run(label, W.s7_put_job(self.box, mode, lambda before, b=built: dict(b), off), 900)
        else:
            user_off = self.user_locks() if self.route == "c2" else []
            out = self.run(label, put_c_job(self.box, mode, built, tied, user_off, self.users), 900)
            off = out["off"]
        after = self.read(f"after {label}")
        put = out["puts"]
        gap_on, at_on = W.frames_gap(out.get("mates_on", {}), put) if put else (None, "")
        gap_off, at_off = W.frames_gap(out.get("mates_off", {}), put) if put and "mates_off" in out else (None, "")
        gap_read, at_read = W.frames_gap(after["frames"], put) if put else (None, "")
        user_flags = {n: out["flags"].get(n) for n in user_off}
        say(f"step    S0 {self.key} {label}: {ROUTES[self.route][:10]}, suppressed in {mode} around the put {off}; "
            f"errors {out['errors']} cleanup {out['cleanup']}; bodies put {list(put)}; against their targets with the "
            f"mates off {gap_off if gap_off is None else f'{gap_off:.1e}'} at {at_off or '-'}, back on "
            f"{gap_on if gap_on is None else f'{gap_on:.1e}'} at {at_on or '-'}, read after "
            f"{gap_read if gap_read is None else f'{gap_read:.1e}'} at {at_read or '-'}; the user's mates suppressed "
            f"for it, flags after {user_flags}")
        user_errors = {n: c for n, c in after["errors"].items() if n.startswith("User")}
        app_errors = {n: c for n, c in after["errors"].items() if not n.startswith("User")}
        held = (not out["errors"] and not out["cleanup"] and gap_read is not None and gap_read <= TOL
                and gap_on is not None and gap_on <= TOL)
        with_gear = all(after["rel_gap"].get(u, 1.0) <= TOL for u in tied)
        flags_back = all(f is not None and not any(f.values()) for f in user_flags.values()) if user_off else True
        on_slide = True
        if "slide2" in self.mates:
            on_slide = abs(after["dz"] - self.dz_orig[mode]) <= TOL if mode in self.dz_orig else True
            check(on_slide, f"S0 {self.key} {label}: Sprocket-2 stays on RangeSlv's Front plane, z less RangeSlv's "
                            f"{after['dz']:+.9f} against the setup's {self.dz_orig.get(mode)} in {mode}")
        clean = held and with_gear and not after["errors"] and flags_back and on_slide
        say(f"        {label}: held {held}; each locked sprocket at its pose of the setup in its gear's frame "
            f"{with_gear} ({fmt({u: after['rel_gap'].get(u, 0.0) for u in tied})}); mates in error "
            f"{after['errors'] or 'none'}; the user's flags back {flags_back}: clean {clean}")
        self.json["steps"][-1].update(put={"mode": mode, "label": label, "route": self.route, "off": off,
                                           "errors": out["errors"], "cleanup": out["cleanup"], "bodies": list(put),
                                           "gap_mates_off": gap_off, "gap_mates_on": gap_on, "gap_read": gap_read,
                                           "at": at_read, "user_flags": user_flags, "user_errors": user_errors,
                                           "app_errors": app_errors, "held": held, "with_gear": with_gear,
                                           "flags_back": flags_back, "on_slide": on_slide, "clean": clean})
        if put and not held and not out["errors"] and not after["errors"]:
            stop(f"S0 {self.key} {label}: SolidWorks took the put and left a body off its target "
                 f"({gap_read if gap_read is None else f'{gap_read:.1e}'} at {at_read}) with no error code "
                 "(plan §0.3)")
        if user_off and not flags_back:
            stop(f"S0 {self.key} {label}: a user mate suppressed around the put did not come back on in every "
                 f"configuration: {user_flags} (plan §0.3)")
        return {"held": held, "with_gear": with_gear, "clean": clean, "errors": out["errors"],
                "user_errors": user_errors, "app_errors": app_errors, "flags_back": flags_back, "on_slide": on_slide}

    def final(self):
        """Every mode shown and rebuilt, every body and user component read, each mode's mates' codes and the train's
        constrained status; the first mode shown last."""
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
        tied = list(self.ties())
        for mode in modes:
            frames = got["frames"][mode]
            built = W.mode_record_frames(self.desk, mode)
            gap, at = W.frames_gap(frames, built)
            gaps = self.rel_gaps(self.rel_of(frames), self.rel_orig)
            errors = {n: c for n, (c, sup) in got["mates"][mode].items() if c and not sup}
            sun = W.turn_degrees(built[self.box.drag[0]][0], frames[self.box.drag[0]][0])
            free = {g: st for g, st in got["status"][mode].items()
                    if g in self.names and g not in self.box.fixed and st != findings.COMPONENT_UNDER_DEFINED}
            dz = self.dz(frames) if "slide2" in self.mates else None
            summary[mode] = {"gap": gap, "at": at, "rel_gap": gaps, "errors": errors, "sun_from_built": sun,
                             "not_free": free, "dz": dz, "tied_home": all(gaps.get(u, 1.0) <= TOL for u in tied)}
            say(f"read    S0 {self.key} the last read, {mode} shown: every body against its built frame, largest "
                f"{gap:.1e} at {at or '-'} ({self.box.drag[0]} at {sun}° from built); sprockets' poses in their gears' "
                f"frames against the setup {({u: f'{v:.1e}' for u, v in gaps.items()})}; mates in error "
                f"{errors or 'none'}; train not free {free or 'none'}"
                + (f"; Sprocket-2 z less RangeSlv's {dz:+.9f} (setup {self.dz_orig.get(mode)})" if dz is not None else ""))
        self.json["last"] = {"summary": summary, "frames": {m: frames_text(f) for m, f in got["frames"].items()},
                             "status": got["status"], "mates": got["mates"]}
        return summary

    def end(self):
        W.end_copy(self.worker, self.folder, f"S0 {self.key}")


def run_case(worker, master, parts, spec):
    c = Case(worker, master, parts, spec)
    outcome = {"modes": {}}
    c.json["outcome"] = outcome
    try:
        c.setup()
        first = c.read("the tie read, before any put, in the mode the copy opens in, nothing shown")
        outcome["tie_unshown"] = {"active": first["active"], "tie": first["tie"]}
        if "slide2" in c.mates:
            c.dz_orig = {}
        sun = c.box.drag[0]
        plane, _ = W.drive_assumptions(c.desk, sun, f"S0 {c.key}")
        built_sun = W.wanted(c.desk)[sun]
        if "slide2" in c.mates:          # D: Sprocket-2's place on RangeSlv in every mode as set up
            for mode in c.modes:
                c.show(mode)
                c.dz_orig[mode] = c.read(f"D's setup in {mode}")["dz"]
            say(f"fact    S0 {c.key}: Sprocket-2's z less RangeSlv's as set up, by mode: {c.dz_orig}")
        for mode in ROUTE_MODES:
            W.guard()
            c.show(mode)
            shown = c.read(f"the tie read in {mode}, shown, before its put")
            expect_tie = c.tie_on(mode)
            check(bool(shown["tie"]) == expect_tie,
                  f"S0 {c.key}: in {mode} the train reads {'not free (a tie)' if shown['tie'] else 'free'}, as "
                  f"{'the tie on there' if expect_tie else 'no tie'} wants: {shown['tie'] or 'every mated body 2'}")
            if mode != ROUTE_MODES[0] and c.ties() and c.route in ("c1", "c2"):
                check(all(shown["rel_gap"].get(u, 1.0) <= TOL for u in c.ties()),
                      f"S0 {c.key}: {mode} shown after {ROUTE_MODES[0]}'s put: each locked sprocket at its pose of the "
                      f"setup in its gear's frame there ({ROUTE_MODES[0]}'s put moved nothing of {mode} wrongly)")
            here = {"tie": shown["tie"], "user_status": {u: shown["status"][u] for u in c.users},
                    "sun_before_drive": shown["angles"].get("Sun")}
            c.drive(mode, plane, built_sun, f"drive +{TURN:g} in {mode}")
            if c.spec["l_probe"] and mode == ROUTE_MODES[0]:
                other = ROUTE_MODES[-1]
                c.show(other)
                probe = c.read(f"{other} shown after {mode}'s drive, before {mode}'s put")
                here["l_after_drive"] = probe["angles"]
                say(f"fact    S0 {c.key}: {other} shown after {mode}'s drive and before {mode}'s put: Sun at "
                    f"{probe['angles'].get('Sun')}° from identity (Sun's built turn is 0): the drive's turn "
                    f"{'reached' if abs(probe['angles'].get('Sun') or 0) > 1e-6 else 'did not reach'} {other}")
                c.show(mode)
            here["put"] = c.put(mode, f"the put back to the built frames in {mode}")
            if c.spec["twice"]:
                again = c.rebuild_read(mode, f"a further rebuild in {mode} after the put")
                check(all(again["rel_gap"].get(u, 1.0) <= TOL for u in c.ties()),
                      f"S0 {c.key}: after a further rebuild in {mode} each locked sprocket still at its pose of the "
                      "setup in its gear's frame")
                c.drive(mode, plane, built_sun, f"a second drive +{TURN:g} in {mode}")
                here["put2"] = c.put(mode, f"the second put back to the built frames in {mode}")
            outcome["modes"][mode] = here
        outcome["last"] = c.final()
        last = ROUTE_MODES[-1]
        s = outcome["last"][last]
        if s["gap"] > TOL:
            stop(f"S0 {c.key}: in the last read {last}, put last, stands off its built frames ({s['gap']:.1e} at "
                 f"{s['at']}): a mode found moved after the every-mode read (plan §4)")
        check(True, f"S0 {c.key}: in the last read {last}, put last, every body at its built frame ({s['gap']:.1e})")
        for mode in c.modes:
            m = outcome["last"][mode]
            if c.ties():
                say(f"fact    S0 {c.key}: in the last read {mode}, each locked sprocket at its pose of the setup: "
                    f"{m['tied_home']} ({({u: f'{v:.1e}' for u, v in m['rel_gap'].items()})})")
        if c.route in ("c1", "c2"):
            check(all(outcome["last"][m]["tied_home"] for m in c.modes),
                  f"S0 {c.key}: in the last read every locked sprocket stands at its pose of the setup in its gear's "
                  "frame in every mode")
        if "slide2" in c.mates:
            ok = all(abs(outcome["last"][m]["dz"] - c.dz_orig[m]) <= TOL for m in c.modes)
            check(ok, f"S0 {c.key}: in the last read Sprocket-2 stays on RangeSlv's Front plane in every mode: "
                      f"{({m: outcome['last'][m]['dz'] for m in c.modes})} against {c.dz_orig}")
            outcome["d_on_slide"] = ok
    finally:
        c.end()
    return c


# -- the proposal ----------------------------------------------------------------------------------------------------


def case_clean(key):
    """Every put of the case clean (held, each locked sprocket at its pose of the setup in its gear's frame, no mate in
    error, the user's flags back) and, in the last read, every locked sprocket at that pose in every mode."""
    c = RESULT["cases"].get(key, {})
    o = c.get("outcome", {})
    modes = o.get("modes", {})
    if len(modes) != len(ROUTE_MODES) or "last" not in o:
        return False
    puts = [modes[m].get(p) for m in ROUTE_MODES for p in ("put", "put2") if modes[m].get(p) is not None]
    return all(p["clean"] for p in puts) and all(v["tied_home"] for v in o["last"].values())


def propose():
    cases = RESULT["cases"]
    verdict = {}
    for route in ("a", "b", "c1", "c2"):
        keys = [k for k in cases if cases[k]["route"] == route and k[0] in "ABE"]
        if keys:
            verdict[route] = {"cases": keys, "clean": {k: case_clean(k) for k in keys}}
    say(f"propose each route's cases and whether every put came back clean: {verdict}")
    held = [r for r in ("c1", "c2") if r in verdict and {"A", "B", "E"} <= {k[0] for k in verdict[r]["cases"]}
            and all(verdict[r]["clean"].values())]
    proposal = {"c1": "put along, the user's locks left on", "c2": "put along, the user's locks suppressed around"}.get(
        held[0]) if held else None
    say(f"propose USER_MATE_PUT_ROUTE: {proposal!r} (route (c) variants clean in A, B and E: {held})")
    ran_c = all(r in verdict for r in ("c1", "c2"))
    if ran_c and not held:
        RESULT["stops"].append("route (c) holds in neither variant")
        W.stop_check(False, "S0: route (c) holds in neither variant (the coordinator's stop)")
    tie = {}
    for key in ("C", "C2"):
        o = cases.get(key, {}).get("outcome", {})
        if o:
            tie[key] = {"unshown": o.get("tie_unshown"), "shown": {m: o.get("modes", {}).get(m, {}).get("tie")
                                                                    for m in ROUTE_MODES}}
    say(f"propose USER_TIE_READ: {tie}")
    d = cases.get("D", {}).get("outcome", {})
    say(f"propose D (no lock, plane to plane with RangeSlv): stays on RangeSlv in every mode {d.get('d_on_slide')}; "
        f"puts {[d.get('modes', {}).get(m, {}).get('put') for m in ROUTE_MODES]}")
    RESULT["proposal"] = {"USER_MATE_PUT_ROUTE": proposal, "routes": verdict, "USER_TIE_READ": tie,
                          "D_on_slide": d.get("d_on_slide"), "WHATS_WRONG_OPENED": RESULT["p0"].get("whats_wrong_opened")}


# -- main ------------------------------------------------------------------------------------------------------------


def keep_awake(on):
    """Ask Windows to keep the display and the system awake while this process runs (``SetThreadExecutionState``;
    nothing of the user's power settings is changed, and the request ends with the process). On this device the
    display's idle timeout puts the whole machine into Modern Standby, which freezes SolidWorks and this script.
    A closed lid still does: run 3 lost its session 30 s after the lid closed (Windows' event log, 2026-11-16 08:52)."""
    try:
        import ctypes
        continuous, system, display = 0x80000000, 0x00000001, 0x00000002
        previous = ctypes.windll.kernel32.SetThreadExecutionState(continuous | (system | display if on else 0))
        return f"display and system {'held awake for the run' if on else 'released'} (previous state {previous:#x})"
    except Exception as exc:  # noqa: BLE001
        return f"not asked: {type(exc).__name__}: {exc}"


def main():
    os.makedirs(OUT, exist_ok=True)
    started = time.strftime("%Y%m%d-%H%M%S")
    json_path = os.path.join(os.path.dirname(os.path.abspath(W.LOG_PATH)), f"w9-s0-{started}.json")

    def write_json():
        # After every case and first in the finally: run 3 (2024) lost its session in its last case and left no JSON,
        # since the close raised before the one write at the end (W9-S0-REVIEW S1).
        RESULT["fails"], RESULT["notes"] = list(W.FAILS), list(W.NOTES)
        with open(json_path, "w", encoding="utf-8") as handle:
            json.dump(RESULT, handle, indent=1, default=str)

    say(f"awake   {keep_awake(True)}")
    say(f"run     {time.strftime('%Y-%m-%d %H:%M:%S')}; W9 S0 (ISSUE-1-PLAN §4) from {W.SRC}{W.snapshot()}; cases "
        f"{list(CHOSEN or DEFAULT_CASES)}; master {MASTER_GIVEN or 'built here'}; P0 {'skipped' if SKIP_P0 else 'first'}")
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
                if spec["key"] not in (CHOSEN or DEFAULT_CASES):
                    continue
                W.guard()
                started_case = time.monotonic()
                try:
                    run_case(worker, master, parts, spec)
                except AssertionError as exc:
                    check(False, f"S0 {spec['key']}: {exc}")
                    for line in traceback.format_exc().splitlines()[-6:]:
                        say("        " + line)
                say(f"time    S0 {spec['key']}: {time.monotonic() - started_case:.0f} s; {W.memory()}")
                write_json()
                watch_check(f"S0 {spec['key']}")
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
        if "proposal" not in RESULT:
            try:
                propose()          # from what was read, whatever ended the run; it asks nothing of SolidWorks
            except Exception as exc:  # noqa: BLE001
                say(f"propose not made: {type(exc).__name__}: {exc}")
        write_json()
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
            except Exception as exc:  # noqa: BLE001  (a session that is gone raises NotRunning, not WorkerHung)
                say(f"close   not closed: {type(exc).__name__}: {exc}")
        watch.stop.set()
        say(f"dialogs progress boxes seen {W.PROGRESS}; other windows the watch logged: {W.WINDOWS['count']}")
        worker.shutdown()
        write_json()
        say(f"awake   {keep_awake(False)}")
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
