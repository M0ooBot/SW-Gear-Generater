r"""W9a's demonstration on SolidWorks (ISSUE-1-PLAN §5, W9a's *Done when*; W9A-INTERFACES, W9A-PACKAGE-B, W9A-REVIEW-A
and W9A-REVIEW-B): the user's own components, mates and features in a built assembly, through the app's own Update and
Build again… as the Workbook window runs them. The sections, their order and times are in
``docs/notes-workbook/W9A-DEMONSTRATION.md``.

python.exe probe/w9a_demonstration.py <repo src> <output folder under C:\> --pid PID [--log FILE]
                                      [--sections m3,setup,go,...|all|confirm] [--master DIR]
                                      [--user-master DIR] [--reducer-master DIR] [--redo] [--box-wait SECONDS]

``--master``: S0's kept ``rangebox.master`` for this SolidWorks version (``probe/w9_user_work_check.py`` built it);
without it a section that needs RangeBox builds it here first through S0's own ``build_master``.
``--user-master``: a ``setup.master`` an earlier run kept (RangeBox with the user's work, its record holding the
inventory); without it, and with none in this <out>, the section that needs it runs ``setup`` first.
``--reducer-master``: a ``reducer.master`` (the 12 : 1 built to turn) an earlier run kept; likewise.
A section this <out> already holds (its folder, or a builder's master) is skipped, so a run can be resumed into the
same <out>; ``--redo`` sets the earlier folder aside (``<name>.prev-<time>``) and runs it again.

It imports ``probe/workbook_assembly_check.py`` (W8's demonstration: the attach, the dialog watch, the log, Excel, the
fixtures written and built through the app's own Build, ``keep_master`` / ``copy_built`` / ``end_copy``, the drive,
the user's turn and the call trace) and ``probe/w9_user_work_check.py`` (S0: the user's parts, the relative pose, the
window list, the request to stay awake). Nothing in either is changed. ``Desk9`` carries the Workbook window's own
code: its ``_plan_solidworks_pass``, ``_open_record``, ``_write``, ``_finish_update``, ``_finish_build``,
``_record_refusal`` and ``_mark_not_as_built`` are the functions of ``WorkbookWindow`` themselves, run on Desk9;
only ``press_update``'s job (the session's revision, then ``update_gearbox``) and ``_start_build``'s (``old_assembly``
as ``before``) are restated, and every press first asserts the footer offers it. The app's Recent list (APPDATA) is
pointed into <out> before anything of the app is imported, and checked.

Sections (each runs alone by name; each copy section starts from a kept master and ends with its copy closed):

- ``m3``      M3, first, under the dialog watch: a user mate in error, then a user feature in error in the user's own
              part; the app's assembly rebuild and its value Update with each, the footer first, each Update judged by
              the M3 findings (go ahead naming the item as in error before, or today's stop); then the same sprocket,
              its part in error, locked to Sun: the press refuses before any write. Any window is a STOP of the run.
- ``setup``   RangeBox with the user's work, saved in place, reopened; M1 and M2 by the app's own reads; a quiet Update
              records the inventory (the keyway listed: M2); the unmeasured branches shown refusing (pure); kept as
              ``setup.master``.
- ``m1``      a user gear mate, and a mate suppressed in the active mode but on in the others.
- ``go``      a value Update and a slide-offset Update after the user's turns: the carry foreseen and done, every put an
              app body or a locked sprocket, every user mate's flags, codes and entities as before, the keyway rebuilt.
- ``refuse``  each refusal step under its own net: the lock to the fixed housing (foreseen; then, the workbook changed,
              "has changed since" and the same refusal foreseen), a mate of another kind on Sun, the solver's tie,
              two app bodies, the Bore typed in SolidWorks, and all at once; each judged by its traced calls and reads.
- ``lightweight`` a carried sprocket set lightweight, every instance's state read raw before, after and after the
              reset: recorded by a quiet press, foreseen, refused by a press on the assembly as it stands naming exactly
              the carried instances read lightweight, never saved while lightweight; resolved before the close.
- ``again``, ``again-dirty``, ``again-closed``  Build again…: the old assembly open behind another document (and,
              dirty, needing a rebuild): the app's ``read_old_assembly`` run alone, then the build; its front-document
              state, save flag, rebuild state, configuration, mates and frames before and after (a change ends the
              section only); once more with it closed.
- ``reducer`` the 12 : 1, kept as ``reducer.master``.
- ``k3``      K3 and M3 in an app part: a user keyway in G1's part, G1's Bore 8 -> 14 in the workbook, the Update
              rebuilding the keyway into error, judged by the M3 findings and the sentence (named as the user's, newly in
              error), every component's code read; a window ends this section only.
- ``nocarrier`` the no-carrier branch of route (c1) measured, its finding patched for the measurement only; proposed.
- ``box``, ``box-k3`` (by name only, never in ``all`` or ``confirm``; each last in a fresh session) SolidWorks 2024's
              What's Wrong box measured: m3's set-up to its mate Update, or k3's to its bore Update, then the press
              waited for up to ``--box-wait`` s (1800 by default) under a watch that only logs: when the box came, at
              which call, SolidWorks' frame enabled or not, the box's class, style and owner, whether a raw read
              answers with it up, the call in progress and the calls made every 10 s, when the box went, whether the
              job returns, what was written, "show errors every rebuild" read before and after, and, if the job
              returned with no box up, the user's mates, components and the app bodies read as the other sections
              read them. Nothing is set, answered, closed or saved once a box is seen; the run then ends, SolidWorks
              left as it stands. SolidWorks' frame and any owner are logged by class, and their titles only as present
              or not and holding the document's name or not (a frame's title can hold the licence edition).

``--sections confirm`` is SolidWorks 2024's confirming set: m3, setup, go, reducer, k3, nocarrier (``refuse`` by name).

What's Wrong (the coordinator's rulings after ``box`` and after m3's confirming run): where
``swbuild.whats_wrong_shows_in_update`` (read by ``getattr``) says True for the version, a What's Wrong box owned by
SolidWorks' frame during any job the script waits on (an app Update or Build, the script's own steps, W8's helpers
through ``w8_step``) is a fact, not a STOP; at the job's end it must go within 60 s and the frame be enabled.
Elsewhere it is a STOP, as any dialog. The log's ``rule`` line says which rule is in force.

Robustness (as S0's at d086705): Windows is asked to keep the display and system awake; the JSON is written after
every section and first in the ``finally``; any exception around the close is caught; the head logs SolidWorks'
revision and the snapshot; a document of the user's is ``<user document N>`` (W8's ``open_titles``). A STOP of the
plan's §0.3 or §4 (a dialog, a read marking a document, a stray put) ends the run; a change to the old assembly in an
again section and a window in k3 end their section only; any other raise of the script's own fails its section.
Under 2 GB of free memory, on any version, the run stops before the next section.
"""

import calendar
import copy as _copy
import dataclasses
import json
import queue
import re
import os
import shutil
import sys
import threading
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# Before anything of the app is imported or called: the app's own settings and Recent list (``store.recent_path``,
# the one file the app keeps outside a gearbox's folder) go into this run's output folder, never the user's
# (the coordinator's ruling 2 on the review; ``workbook_window_check.py`` does the same).
APPDATA_HERE = os.path.join(os.path.abspath(sys.argv[2]), "appdata") if len(sys.argv) > 2 else ""
if APPDATA_HERE:
    os.makedirs(APPDATA_HERE, exist_ok=True)
    os.environ["APPDATA"] = APPDATA_HERE

import workbook_assembly_check as W  # noqa: E402  (parses <src> <out> --pid PID [--log FILE])
import w9_user_work_check as S0  # noqa: E402  (its own options are absent here and so at their defaults)

from gear_generator import findings, store, swbuild, swcom, ui_text  # noqa: E402
from gear_generator.gears import spur  # noqa: E402
from gear_generator.swcom import call  # noqa: E402
from gear_generator.gears.equations import split_equation  # noqa: E402
from gear_generator.workbook import layout as wb_layout  # noqa: E402
from gear_generator.workbook import link as wb_link  # noqa: E402
from gear_generator.workbook import update as wb_update  # noqa: E402
from gear_generator import workbook_gui  # noqa: E402  (the window's own code, called on Desk9)

say, check, note = W.say, W.check, W.note
OUT, PID = W.OUT, W.PID
ARGS = sys.argv


def _arg(name):
    return ARGS[ARGS.index(name) + 1] if name in ARGS else ""


ORDER = ["m3", "setup", "go", "m1", "refuse", "lightweight", "again", "again-dirty", "again-closed", "reducer", "k3", "nocarrier"]
# SolidWorks 2024's confirming set (HANDOFF, Rules carried over; the coordinator's ruling 4): the turning build with its
# edits (setup, go), the rebuilds that can raise a dialog there (m3, k3), and the user-lock put (reducer, nocarrier).
# refuse runs on 2024 by name.
CONFIRM = ["m3", "setup", "go", "reducer", "k3", "nocarrier"]
_given = _arg("--sections")
CHOSEN = (ORDER if _given in ("", "all") else CONFIRM if _given == "confirm"
          else [s.strip() for s in _given.split(",") if s.strip()])
MASTER = {"rangebox": _arg("--master"), "setup": _arg("--user-master"), "reducer": _arg("--reducer-master")}
BOX_WAIT = float(_arg("--box-wait") or 1800)   # box, box-k3: how long the press is waited for, in seconds
REDO = "--redo" in ARGS     # a section whose folder this <out> already holds is run again (its folder set aside)

TOL = 1e-6                 # rotation entries and origin coordinates (mm), as S0
SAME = 1e-9                # a read twice of what nothing moved
TURN = 37.0
IDENTITY = S0.IDENTITY
SUN_PART_NAME = "SunGear"  # the again sections' Part name for Sun: its file must change, so Build again…

# RangeBox's user work (setup), each inserted at an identity frame at these places (mm); Name2 by insert order.
RB_INSERTS = (("u1", "Sprocket.SLDPRT", (0.0, 0.0, 30.0), "Sprocket-1"),
              ("u2", "Sprocket.SLDPRT", (0.0, 0.0, -70.0), "Sprocket-2"),
              ("u3", "Sprocket.SLDPRT", (0.0, 0.0, 40.0), "Sprocket-3"),
              ("u4", "Sprocket.SLDPRT", (0.0, 0.0, 130.0), "Sprocket-4"),
              ("uh", "Housing.SLDPRT", (0.0, 0.0, 60.0), "Housing-1"))
RB_LOCKED = {"Sprocket-1": "Sun", "Sprocket-3": "Sun", "Sprocket-2": "RangeSlv"}   # each locked sprocket's gear
# Sprocket-4's Front plane from Sprocket-3's (UserDist4). A plane-to-plane distance mate's side is AddMate5's Flip,
# which the app's "distance" leaves False and no finding settles (m3's first run, 2920a09), so Sprocket-4 may stand at
# 40 + 90 = 130, where it is inserted, or at 40 - 90 = -50: both are clear of every body on the axis (Sun 5.5 to 15.5,
# RangeSlv and the dogs -34.5 to -14.5, Sprocket-2 about -76 to -64). setup reads which, and go holds it to that.
RB_GAP = 90.0

RESULT = {"sections": {}, "stops": [], "proposal": {}}
# What ``main`` calls this run in its log and its JSON's name; W9b's demonstration (``w9b_demonstration.py``) runs
# this ``main`` with its own sections and sets these to its own.
RUN_TITLE, JSON_STEM = "W9a demonstration", "w9a-demo"
CTX = {"worker": None, "excel": None, "parts": ""}


class DemoStop(Exception):
    """A STOP of ISSUE-1-PLAN §0.3 or §4: the run ends there, what was read kept."""


class SectionStop(Exception):
    """A STOP that ends its section only, never the run: a change to the old assembly in an again section, a window
    in k3 (the coordinator's rulings 1 and 3 on the review)."""


class BoxSeen(DemoStop):
    """``box`` / ``box-k3`` saw a SolidWorks box during the press: the run ends there by design, SolidWorks left as it
    stands with the box up, nothing closed or saved, for the coordinator to end the session. Not a failure."""


RUN_ENDERS = (DemoStop, W.WorkerHung, swcom.NotRunning, W.Stopped, W.Halt)   # what one section may not swallow
# ``box`` and ``box-k3`` only: while "on", ``watched_wait`` logs a window instead of stopping on it, calls ``tick``
# (seconds since the job began, whether it has returned) every poll, and gives the job ``timeout`` seconds.
BOX = {"on": False, "tick": None, "timeout": BOX_WAIT}
# The coordinator's rulings after box and box-k3 on 2024 (d7cbcda) and after m3's confirming run (0a60fd3): on a
# version where swbuild.whats_wrong_shows_in_update(revision) is True, SolidWorks' What's Wrong box owned by its frame,
# during ANY job the script waits on, is a fact, not a STOP: under an app job (an Update or a Build) "as the app's
# Update shows it"; under the script's own job, or a W8 helper, "as SolidWorks shows it when a person does this" (on
# 2024 activating an assembly with something in error raises it too). The job is waited for; at its end the box must
# go within WW_ALLOWANCE s and the frame be enabled, else the STOP. "rule": that helper's answer (None until read, or
# when the helper is not in this source); "job": a ruled job in progress; "last": the last app job's record (only these
# feed whats_wrong_showed); "job_last": the last ruled job's record, of either kind.
WHATS_WRONG = "What's Wrong"
WW_ALLOWANCE = 60.0          # box stayed 22 s after it came (box: 97.45 -> 120.08 s); the end check allows 60
WW = {"rule": None, "read": False, "job": False, "last": None, "job_last": None}
WW_WORDS = {"app": "as the app's Update shows it", "script": "as SolidWorks shows it when a person does this"}
WW_STALL = 120.0             # a box up this long with no SolidWorks call made since it came is taken as blocking
# Every SolidWorks call any job makes, counted (W8's TRACE counts only while an Update is traced): the stall test's
# measure of the worker going on while a box is up. A one-line wrapper over swcom.call as W8 left it.
CALLS_MADE = {"n": 0}
_TRACED_CALL = swcom.call


def _counted_call(obj, name, *args):
    CALLS_MADE["n"] += 1
    return _TRACED_CALL(obj, name, *args)


swcom.call = _counted_call


class _WhatsWrongTolerated(set):
    """W8's STARTUP_BOXES, which its watch consults before calling a window during a configuration call its FAIL and
    STOP: while a ruled job runs (an app job, the script's own, or a W8 helper's), a What's Wrong box counts as known,
    so W8 logs it as a NOTE and this script judges it (W8's file is not changed; only the set it reads is wrapped)."""

    def __contains__(self, box):
        if WW["job"] and WW["rule"] is True and isinstance(box, tuple) and box and box[0] == WHATS_WRONG:
            return True
        return set.__contains__(self, box)


SEEN = {"notes": 0}          # W8's watch notes already judged: a section-only window is not judged again by the run


def stop(what):
    W.stop_check(False, what)
    RESULT["stops"].append(what)
    raise DemoStop(what)


def section_stop(what):
    """A failed check and the JSON's stops, never ``W.STOPS`` (which ends the run at the next watch_check)."""
    check(False, f"STOP (this section only): {what}")
    RESULT["stops"].append(f"(section) {what}")
    raise SectionStop(what)


def watch_windows():
    """The windows W8's watch logged since the last judgement (a #32770 or a titled window outside a progress box)."""
    windows = [n for n in W.NOTES[SEEN["notes"]:] if n.startswith("a SolidWorks window")]
    SEEN["notes"] = len(W.NOTES)
    return windows


def watch_check(where):
    """Plan §0.3, any dialog: a window W8's watch logged, or a STOP its helpers raised, ends the run. SolidWorks'
    notification box and its balloon tips are not dialogs (the coordinator's ruling)."""
    windows = watch_windows()
    if windows or W.STOPS:
        stop(f"{where}: {windows or W.STOPS}")


def guard(where):
    W.guard()
    free = W.free_gb()
    if free < 2.0:
        stop(f"{where}: {W.memory()}: under 2 GB of free memory (HANDOFF, Rules carried over)")


def whats_wrong_rule():
    """``swbuild.whats_wrong_shows_in_update(revision)`` read once by ``getattr`` (None when the helper is not in this
    source, or answers None), said in the log with the rule it puts in force."""
    if not WW["read"]:
        helper = getattr(swbuild, "whats_wrong_shows_in_update", None)
        WW["rule"] = None if helper is None else helper(tuple(W.TAG["revision"]))
        WW["read"] = True
        say(f"rule    What's Wrong: swbuild.whats_wrong_shows_in_update "
            f"{'is not in this source' if helper is None else 'reads ' + repr(WW['rule'])}; "
            + ("a What's Wrong box owned by SolidWorks' frame during any job the script waits on is logged as a fact "
               "(under an app Update or Build, as the app's Update shows it; under the script's own steps and W8's "
               "helpers, as SolidWorks shows it when a person does this), the job waited for, and at its end the box "
               f"must go within {WW_ALLOWANCE:g} s and the frame be enabled (else a STOP)"
               if WW["rule"] is True else "What's Wrong during a job is a STOP, as any dialog"))
        RESULT["whats_wrong_rule"] = {"helper_present": helper is not None, "shows_in_update": WW["rule"],
                                      "allowance_seconds": WW_ALLOWANCE}
    return WW["rule"]


def whats_wrong_boxes(frame):
    """SolidWorks' visible What's Wrong boxes (#32770 titled "What's Wrong"), each with whether SolidWorks' frame owns
    it: [(hwnd, owned)]."""
    win32con, win32gui, win32process = _win32()
    found = []

    def each(h, _):
        try:
            if (win32gui.IsWindowVisible(h) and win32gui.GetClassName(h) == "#32770"
                    and win32process.GetWindowThreadProcessId(h)[1] == W.PID
                    and win32gui.GetWindowText(h) == WHATS_WRONG):
                found.append((h, bool(frame) and win32gui.GetWindow(h, win32con.GW_OWNER) == frame["hwnd"]))
        except Exception:  # noqa: BLE001
            pass
        return True
    win32gui.EnumWindows(each, None)
    return found


def ww_record(what, kind):
    """A ruled job's What's Wrong record, kept as the last of its kind."""
    record = {"what": what, "kind": kind, "seen": [], "gone": [], "unowned": []}
    WW["job_last"] = record
    if kind == "app":
        WW["last"] = record
    return record


def ww_poll(record, frame, began):
    """One look for What's Wrong during a ruled job: each box owned by the frame when it came (the call in progress,
    the calls made so far), each when it went and how long it stayed; a What's Wrong not owned by the frame kept for
    the STOP. While a box is up, a blocking one is named at once (W9A-CLOSE-2024-REVIEW finding 5) in
    ``record["blocking"]``: SolidWorks' frame disabled, or the box up longer than WW_STALL s with no SolidWorks call made
    since it came. Returns the boxes up."""
    elapsed = round(time.monotonic() - began, 2)
    now = whats_wrong_boxes(frame)
    words = WW_WORDS[record["kind"]]
    for h, owned in now:
        if owned and h not in [e["hwnd"] for e in record["seen"]]:
            record["seen"].append({"hwnd": h, "seconds": elapsed, "call_in_progress": W.CALLS["now"] or None,
                                   "calls_made": CALLS_MADE["n"]})
            say(f"fact    {record['what']}: What's Wrong came up {elapsed:.2f} s into the job, the worker in "
                f"{W.CALLS['now'] or None}, owned by SolidWorks' frame: {words} (the ruling: a fact, not a STOP)")
        elif not owned and h not in record["unowned"]:
            record["unowned"].append(h)
            say(f"fact    {record['what']}: a What's Wrong not owned by SolidWorks' frame came up {elapsed:.2f} s in")
    up = {h for h, _ in now}
    for e in record["seen"]:
        if e["hwnd"] not in up and e["hwnd"] not in [g["hwnd"] for g in record["gone"]]:
            stayed = round(elapsed - e["seconds"], 2)
            record["gone"].append({"hwnd": e["hwnd"], "seconds": elapsed, "stayed": stayed,
                                   "call_in_progress": W.CALLS["now"] or None})
            say(f"fact    {record['what']}: What's Wrong gone {elapsed:.2f} s into the job after staying {stayed:.2f} s, "
                f"the worker in {W.CALLS['now'] or None}; nothing here closed it")
    standing = [e for e in record["seen"] if e["hwnd"] in up]
    if standing and not record.get("blocking"):
        enabled = frame_enabled(frame)
        stalled = [e for e in standing if elapsed - e["seconds"] > WW_STALL and CALLS_MADE["n"] == e["calls_made"]]
        if enabled is False or stalled:
            record["blocking"] = (
                f"{record['what']}: What's Wrong is up and "
                + ("SolidWorks' frame is disabled (a modal box)" if enabled is False else
                   f"has stood {elapsed - stalled[0]['seconds']:.0f} s with no SolidWorks call made since it came")
                + f", {elapsed:.2f} s into the job: the ruling allows only a box that blocks nothing")
    return [h for h, _ in now]


def ww_blocked(record):
    """A blocking What's Wrong named by ``ww_poll``: the STOP at once, the worker marked hung and left alone."""
    if record.get("blocking"):
        W.HUNG["on"] = True
        SEEN["dialog_at"] = time.monotonic()
        stop(record["blocking"])


def whats_wrong_end(record, frame, began):
    """At a ruled job's end: every What's Wrong box owned by the frame must go within WW_ALLOWANCE s (how long it took
    is logged), none may be unowned, and SolidWorks' frame must be enabled; W8's notes of the box are then the
    ruling's fact (a What's Wrong W8 noted that this watch never read as owned by the frame stays the STOP). Else the
    STOP. The record said as a fact."""
    ended = time.monotonic()
    up = ww_poll(record, frame, began)
    ww_blocked(record)
    while up and time.monotonic() - ended < WW_ALLOWANCE:
        time.sleep(0.25)
        up = ww_poll(record, frame, began)
        ww_blocked(record)
    waited_for = round(time.monotonic() - ended, 2)
    enabled = frame_enabled(frame)
    record.update(up_at_the_end=len(up), frame_enabled_at_the_end=enabled, waited_after_the_job=waited_for)
    what = record["what"]
    if record["seen"]:
        record["lifetimes"] = [g["stayed"] for g in record["gone"]]
        RESULT.setdefault("whats_wrong_lifetimes", []).append(
            {"job": what, "kind": record["kind"], "came": [e["seconds"] for e in record["seen"]],
             "stayed": record["lifetimes"], "still_up": len(up)})
        say(f"fact    {what}: What's Wrong showed during the job, {WW_WORDS[record['kind']]}: came at "
            f"{[e['seconds'] for e in record['seen']]} s, stayed {record['lifetimes']} s; after the job it took "
            f"{waited_for:.2f} s to go (allowed {WW_ALLOWANCE:g}); {len(up)} up at the end, SolidWorks' frame enabled "
            f"{enabled}")
    if up or enabled is False or record["unowned"]:
        W.HUNG["on"] = True
        stop(f"{what}: at the job's end What's Wrong is still up after {WW_ALLOWANCE:g} s ({len(up)}), or SolidWorks' "
             f"frame is disabled ({enabled}), or a What's Wrong was not owned by the frame ({len(record['unowned'])}): "
             "the ruling allows only the frame's box, going by itself")
    notes = [n for n in W.NOTES[SEEN["notes"]:] if n.startswith("a SolidWorks window")]
    ww = [n for n in notes if n.startswith(f"a SolidWorks window {WHATS_WRONG!r}")]
    if ww and not record["seen"]:
        W.HUNG["on"] = True
        stop(f"{what}: What's Wrong was noted but never read here as owned by SolidWorks' frame: {ww}")
    if ww and len(ww) == len(notes):
        SEEN["notes"] = len(W.NOTES)


def w8_step(fn, *args, _label=None, **kwargs):
    """A W8 helper the script calls with W8's own unwatched wait (``end_copy``, ``copy_built``, ``keep_master``,
    ``write_fixture``, ``build_turning``, ``close_ours``): under the What's Wrong rule a thread looks for the box while
    it runs, W8's watch is kept from calling it its FAIL (STARTUP_BOXES), and the end check follows, as for any job."""
    if W.HUNG["on"] or BOX["on"] or WW["job"] or whats_wrong_rule() is not True:
        return fn(*args, **kwargs)
    record = ww_record(f"W8's {_label or getattr(fn, '__name__', 'step')}", "script")
    frame, began, done = sw_frame(), time.monotonic(), threading.Event()

    def look():
        while not done.is_set():
            try:
                ww_poll(record, frame, began)
            except Exception:  # noqa: BLE001 - a look that failed is retried; the end check reads again
                pass
            if record.get("blocking") and not record.get("said"):
                # Named at once from here; the main thread is inside W8's own wait, which raises at its timeout, and
                # the STOP is raised when it returns. The worker is marked hung so nothing more is asked of it.
                record["said"] = True
                W.HUNG["on"] = True
                RESULT["stops"].append(record["blocking"])
                say(f"STOP    {record['blocking']}; the worker is left alone (W8's own wait ends this step)")
            done.wait(0.25)
    looker = threading.Thread(target=look, daemon=True)
    WW["job"] = True
    looker.start()
    try:
        value = fn(*args, **kwargs)
    except BaseException:
        done.set()
        WW["job"] = False
        raise
    done.set()
    looker.join(2.0)
    try:
        if record.get("blocking"):
            raise DemoStop(record["blocking"])
        if not W.HUNG["on"]:
            whats_wrong_end(record, frame, began)
    finally:
        WW["job"] = False
    return value


def watched_wait(pending, timeout, what, app_job=False):
    """W8's ``wait_job``, watching while the job runs: a SolidWorks window W8's watch logs (a dialog with buttons
    that is not the notification box, a balloon or a progress box) is a §0.3 STOP at once, the dialog named, the
    worker marked hung and left alone (nothing is asked of SolidWorks after it) — never a NOTE the run waits behind
    until the job's timeout (refuse's lightweight step at 9dded70: SOLIDWORKS CAM's Yes/No warning under SaveAs3).
    The exception is What's Wrong under the rule (``whats_wrong_rule``): for every job, ``app_job`` (an Update or a
    Build) or the script's own, the frame's box is a fact and the end check judges it (``whats_wrong_end``)."""
    if W.HUNG["on"]:
        raise W.WorkerHung("the SolidWorks worker is hung from an earlier job, so nothing more is asked of it")
    began = time.monotonic()
    deadline = began + (min(timeout, BOX["timeout"]) if BOX["on"] else timeout)
    ruled = not BOX["on"] and whats_wrong_rule() is True
    frame = sw_frame() if ruled else None
    record = ww_record(what, "app" if app_job else "script") if ruled else None
    WW["job"] = ruled
    try:
        while True:
            answer = pending.poll()
            if BOX["on"] and BOX["tick"] is not None:
                BOX["tick"](time.monotonic() - began, answer is not None)
            if ruled:
                ww_poll(record, frame, began)
                ww_blocked(record)
            if answer is not None:
                if ruled:
                    whats_wrong_end(record, frame, began)
                return answer
            windows = [n for n in W.NOTES[SEEN["notes"]:] if n.startswith("a SolidWorks window")]
            if windows and BOX["on"]:
                SEEN["notes"] = len(W.NOTES)
                say(f"fact    {what}: W8's watch logged {windows} (box mode: logged, not a STOP; the job is waited for)")
                windows = []
            if windows and ruled:
                # W8's note of a What's Wrong box is the ruling's fact once this watch has seen one owned by the
                # frame; an unowned one, or any other window, stays the STOP.
                ww = [n for n in windows if n.startswith(f"a SolidWorks window {WHATS_WRONG!r}")]
                if ww and record["seen"] and not record["unowned"] and len(ww) == len(windows):
                    SEEN["notes"] = len(W.NOTES)
                    windows = []
                elif ww and not record["seen"] and not record["unowned"] and len(ww) == len(windows):
                    windows = []          # W8 saw it first: judged on the next poll, once this watch has read it
            if windows:
                W.HUNG["on"] = True
                SEEN["notes"] = len(W.NOTES)
                SEEN["dialog_at"] = time.monotonic()        # the section's time line ends here, no wait behind it
                stop(f"{what}: a SolidWorks dialog came up while it ran, and nothing here answers it: {windows} "
                     "(§0.3: any dialog); the worker is left alone and nothing more is asked of SolidWorks")
            if time.monotonic() > deadline:
                W.HUNG["on"] = True
                raise W.WorkerHung(f"{what} did not answer in {timeout:g} s")
            time.sleep(0.05 if time.monotonic() - began < 2.0 else 0.5)      # short jobs are not slowed
    finally:
        WW["job"] = False


def run(what, fn, timeout=900):
    """A worker job, watched (``watched_wait``); a raise other than a hung worker or a STOP fails the section with
    its sentence."""
    try:
        value, error = watched_wait(CTX["worker"].submit(fn), timeout, what)
        if error is not None:
            raise error
        return value
    except (W.WorkerHung, DemoStop, SectionStop, swcom.NotRunning):
        raise
    except Exception as exc:  # noqa: BLE001
        text = f"{type(exc).__name__}: {exc}"
        W.frame_none_stop([text], what)
        raise AssertionError(f"{what}: {text}") from None


def job(path, work):
    return W.in_assembly(path, work)


def fmt(gaps):
    return {k: f"{v:.1e}" for k, v in gaps.items()}


# -- the Workbook window's W9a path, without Tk ---------------------------------------------------------------------


_WINDOW = workbook_gui.WorkbookWindow


class Desk9(W.Desk):
    """W8's Desk carrying the Workbook window's OWN code (the coordinator's ruling 2 on the review): the window's
    ``_plan_solidworks_pass``, ``_settled``, ``_strip``, ``_open_record``, ``_write``, ``_finish_update``,
    ``_finish_build``, ``_record_refusal`` and ``_mark_not_as_built`` are its methods here, the functions themselves
    taken from ``WorkbookWindow``, run on this stand-in, which has what they read (``link``, ``state``, ``app``,
    ``recalc``, ``record``, ``update_plan``…). Copied are only ``press_update``'s two-line job (the session's revision
    taken in it, then ``update_gearbox``) and ``_start_build``'s three (``old_assembly`` as ``before``), with
    ``_collect_job``'s dispatch of a raise; the footer gate is asserted before every press, as ``press_update`` makes
    it. The app's Recent list is written into this run's folder (APPDATA, set before any import)."""

    _plan_solidworks_pass = _WINDOW._plan_solidworks_pass
    _settled = _WINDOW._settled
    _strip = _WINDOW._strip
    _open_record = _WINDOW._open_record
    _write = _WINDOW._write
    _finish_update = _WINDOW._finish_update
    _finish_build = _WINDOW._finish_build
    _record_refusal = _WINDOW._record_refusal
    _mark_not_as_built = _WINDOW._mark_not_as_built

    def __init__(self, path, worker, strip=""):
        self.update_plan = None
        self.plan_trouble = ""
        self.recalc = False
        # The strip as the window reads it: its Recent list (in this run's APPDATA), no templates set.
        self.app = type("Strip", (), {"recent": store.load_recent()})()
        super().__init__(path, worker, strip)
        self.revision = ()
        self.before = None

    # W8's Desk says ``update`` and ``a`` where the window says ``update_plan`` and ``state``.
    @property
    def update(self):
        return self.update_plan

    @update.setter
    def update(self, value):
        self.update_plan = value

    @property
    def state(self):
        return self.a

    def after(self, _ms, _fn, *args):
        """The window's ``after``: called by its planning only for a record whose workbook is gone, never here."""
        check(False, f"the window's planning asked whether this workbook was moved ({args}): a copy's record must be "
                     "its own")

    def plan_solidworks(self):
        """``WorkbookWindow._plan_solidworks`` itself: its pass inside ``store.one_pass()``."""
        with store.one_pass():
            self._plan_solidworks_pass()
        if self.plan_trouble:
            check(False, f"the window's planning raised: {self.plan_trouble}")

    def _note(self, note):
        """The window's Note kept as W8's Desk keeps it, ``(text, ok)``."""
        self.note = (note.text, note.ok)
        say(f"status  [{'green' if note.ok else 'red'}] {note.text}")

    def update_solidworks(self):
        """``press_update``'s job (the session's revision taken in it), then ``_collect_job``: the window's own
        ``_finish_update``, or ``job_failed`` and, for a refusal over the user's work, its own ``_record_refusal``
        (``_mark_not_as_built`` for a part not as built)."""
        update = self.update_plan
        if update is None:
            raise AssertionError("Update SolidWorks pressed with nothing to update (the window would not offer it)")
        job = workbook_gui.Job(workbook_gui.JOB_UPDATE, self.reading.digest, update=update, record=self.record)
        kwargs = update.update_kwargs()
        steps = []

        def work(s):
            job.revision = tuple(getattr(s, "revision", ()) or ())
            return swbuild.update_gearbox(s, **kwargs, progress=steps.append)
        started = time.monotonic()
        say(f"update  {W.memory()}")
        result, self.error = watched_wait(self.worker.submit(work), 2400, "Update SolidWorks", app_job=True)
        self.revision = job.revision
        seconds = time.monotonic() - started
        if self.error is not None:
            say(f"        raised {type(self.error).__name__} in {seconds:.1f} s: {self.error}")
            self._note(ui_text.Note(ui_text.job_failed(self.error, True), False))
            if isinstance(self.error, swbuild.NotAsBuilt):
                self._mark_not_as_built(self.error)
            elif isinstance(self.error, swbuild.UserWorkRefused):
                self._record_refusal(job, self.error)
                say("record  the window's _record_refusal ran")
            self.plan_solidworks()
            return update, None, None
        self.positions_per_configuration = getattr(result, "positions_per_configuration", None)
        say(f"        in {seconds:.1f} s; {W.memory()}; loaded from disk {[os.path.basename(p) for p in result.opened]}")
        say(f"        W9a: carried {result.carried}; renamed {result.renamed}; user in error {result.user_in_error}; "
            f"user features in error {[(f.name, os.path.basename(f.path), f.code) for f in result.user_features_in_error]}"
            f"; inventory read {'yes' if result.user_work is not None else 'no'}; failures {result.failures}")
        wrong = list(getattr(result, "sense_found_wrong", []) or [])
        check(not wrong, f"the Update's check phase found no gear mate turning against its mesh: {wrong}")
        self._note(self._finish_update(job, result))
        self.plan_solidworks()
        return update, result, None

    def build(self, plan=None):
        """``_start_build``'s job (``old_assembly`` given as ``before`` for a Build again…, its journal first), then the
        window's own ``_finish_build``."""
        plan = plan or self.plan
        job = workbook_gui.Job(workbook_gui.JOB_BUILD, self.reading.digest, plan=plan, record=self.record)
        kwargs = plan.build_kwargs()
        job.before = self.before = wb_update.old_assembly(self.record, plan)
        if job.before is not None:
            kwargs["before"] = job.before
        job.journaled = self.write_journal(plan)
        steps = self.steps = []
        say(f"journal {'written' if job.journaled else 'NOT written'}; the old assembly read first: "
            f"{os.path.basename(job.before.path) if job.before is not None else 'none'}")
        started = time.monotonic()
        result, self.error = watched_wait(self.worker.submit(
            lambda s: swbuild.build_gearbox(s, **kwargs, progress=steps.append)), 2400, "the build", app_job=True)
        if self.error is not None:
            say(f"        raised {type(self.error).__name__}: {self.error}")
            self._note(ui_text.Note(ui_text.job_failed(self.error, False), False))
            self.plan_solidworks()
            return plan, None
        self.positions_per_configuration = getattr(result, "positions_per_configuration", None)
        for line in result.log_lines():
            say("        " + line)
        work = getattr(result, "old_user_work", None)
        say(f"        in {time.monotonic() - started:.1f} s; {W.memory()}; old read {getattr(result, 'old_read', '')!r}; "
            f"old user work {None if work is None else ([c.name for c in work.components], [m.name for m in work.mates])}")
        self._note(self._finish_build(job, result))
        self.plan_solidworks()
        return plan, result


def ahead_of(desk, label):
    """The footer before a press, as the window shows it, and the prediction under it (``user_work_ahead``)."""
    ahead = wb_update.user_work_ahead(desk.update, desk.record, desk.reading.digest)
    line, ok = ui_text.user_work_line(ahead)
    f = desk.say_footer(label)
    say(f"line    [{'green' if ok else 'red'}] {line or '(nothing of the user’s on record)'}")
    if ahead is not None:
        say(f"        predicted: carried {[(g, list(h)) for g, h in ahead.carried]}; problems "
            f"{[(p.kind, list(p.mates)) for p in ahead.problems]}; refused (recorded) "
            f"{[(p.kind, list(p.mates)) for p in ahead.refused]}; changed since {ahead.changed_since}; unread ties "
            f"{list(ahead.unread_ties)}")
    if line and desk.note is None:
        check(line in f.text, f"{label}: the footer says the user-work line as the window would: {line[:80]!r}…")
    return ahead


def predicted_carry(ahead):
    return {(c, g) for g, held in (ahead.carried if ahead is not None else ()) for c, _ in held}


def press(desk, label):
    """Update SolidWorks pressed as the window would: the footer must offer it (``update_shown`` and
    ``update_enabled``, ``press_update``'s gate) and it must be an Update, not Build again…; then W8's traced press
    through Desk9. Returns (the result, or None and ``desk.error``; the traced calls)."""
    f = desk.footer()
    offered = f.update_shown and f.update_enabled and desk.update is not None and not desk.update.needs_new_revision
    check(offered, f"{label}: the footer offers Update SolidWorks (shown {f.update_shown}, enabled {f.update_enabled}, "
                   f"Build again… needed {desk.update is not None and desk.update.needs_new_revision})")
    if not offered:
        raise AssertionError(f"{label}: the window would not run this press")
    result, calls, seconds = W.w8_update(CTX["worker"], desk, label)
    say(f"fact    {label}: the press took {seconds:.0f} s")
    return result, calls


# -- reads ---------------------------------------------------------------------------------------------------------


def use_open(s, path):
    """The document made the build document WITHOUT opening or activating it: the app's own
    ``Session.use_open_document`` (package B)."""
    return s.use_open_document(path)


def read_now(label, asm, folder, pairs, modes, *, activate=True, entities=()):
    """In the active configuration, nothing shown or rebuilt: each body's frame and GetConstrainedStatus (a user's
    component found with ``lightweight_ok``, so one the user set lightweight is still read), every mate's code and flag
    in every mode, each of ``entities``' mates' entities (``Session.mate_info``: §0.3 compares every user item's
    entities before and after), the active document, the documents' GetSaveFlag before and after (a read marking one
    is a STOP, §0.3). ``activate`` False: the assembly is read where it stands without being opened or activated
    (the old assembly, through the app's ``use_open_document``)."""
    def work(s):
        active_doc = s.active_document()
        if not activate:
            if use_open(s, asm) is None:
                raise swcom.SolidWorksError(f"{os.path.basename(asm)} is not open")
        out = {"flags_before": W.folder_flags(s, folder), "active": s.active_configuration(), "frames": {},
               "status": {}, "mates": {}, "by_mode": {}, "entities": {},
               "active_doc": os.path.basename(active_doc.path or active_doc.title) if active_doc else ""}
        try:            # IModelDocExtension.NeedsRebuild2 (swModelRebuildStatus_e), a read new to this repo: a fact
            out["needs_rebuild"] = int(swcom._read(call(s._doc(), "Extension"), "NeedsRebuild2"))  # noqa: SLF001
        except Exception as exc:  # noqa: BLE001 - a fact, read for the again sections
            out["needs_rebuild"] = f"unread: {type(exc).__name__}"
        for i, (g, n) in enumerate(pairs):
            s.find_component(f"rn{i}", n, lightweight_ok=(g == n))      # (g, g): a user's component
            out["frames"][g] = s.component_frame(f"rn{i}")
            out["status"][g] = s.constrained_status(f"rn{i}")
        for i, m in enumerate(s.mate_states()):
            out["mates"][m.name] = (m.code, m.suppressed)
            if modes or m.name in entities:
                s.find_mate(f"rm{i}", m.name)
            if modes:
                out["by_mode"][m.name] = s.mate_suppression(f"rm{i}", modes)
            if m.name in entities:
                info = s.mate_info(f"rm{i}")
                out["entities"][m.name] = (info.type, sorted(str(c) for c in info.components), info.whole)
        out["flags_after"] = W.folder_flags(s, folder)
        after_doc = s.active_document()
        out["active_doc_after"] = os.path.basename(after_doc.path or after_doc.title) if after_doc else ""
        return out
    if activate:
        got = run(f"read {label}", job(asm, work))
    else:
        def bare(s):
            s.begin_build()
            try:
                return work(s)
            finally:
                s.end_build()
        got = run(f"read {label}", bare)
    dirtied = sorted(n for n, v in got["flags_after"].items() if v and not got["flags_before"].get(n))
    if dirtied:
        stop(f"{label}: a read marked {dirtied} modified (ISSUE-1-PLAN §0.3)")
    errors = {n: c for n, (c, sup) in got["mates"].items() if c and not sup}
    say(f"read    {label} (active {got['active']}; front document {got['active_doc']}): mates in error "
        f"{errors or 'none'}; not free "
        f"{ {g: v for g, v in got['status'].items() if v != findings.COMPONENT_UNDER_DEFINED} or 'none'}; "
        f"marked {W.marked(got['flags_after']) or 'none'}; rebuild state {got['needs_rebuild']}")
    got["errors"] = errors
    return got


def read_every(label, asm, pairs, modes):
    """Every mode shown in turn and rebuilt (S0's last read): each body's frame and status, each mode's mate codes;
    every mate's flag per mode; the first mode shown last. A gearbox with no modes: one rebuild and the read."""
    def work(s):
        out = {"frames": {}, "status": {}, "mates": {}, "by_mode": {}}
        for mode in (modes or [""]):
            if mode:
                s.show_configuration(mode)
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            here, status = {}, {}
            for i, (g, n) in enumerate(pairs):
                s.find_component(f"re{i}", n, lightweight_ok=(g == n))
                here[g] = s.component_frame(f"re{i}")
                status[g] = s.constrained_status(f"re{i}")
            out["frames"][mode], out["status"][mode] = here, status
            out["mates"][mode] = {m.name: (m.code, m.suppressed) for m in s.mate_states()}
        if modes:
            s.show_configuration(modes[0])
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            for i, m in enumerate(s.mate_states()):
                s.find_mate(f"rf{i}", m.name)
                out["by_mode"][m.name] = s.mate_suppression(f"rf{i}", modes)
        return out
    return run(f"every mode {label}", job(asm, work), 1200)


def rel_of(frames, locked):
    return {u: S0.relative(frames[g], frames[u]) for u, g in locked.items() if u in frames and g in frames}


def rel_gaps(rel, against):
    return {u: W.frame_gap(rel[u], against[u]) for u in rel if u in against}


def written(before, after, marks_of=None):
    """What differs between two ``read_now`` reads: frames, mate codes and flags, documents newly marked (only those
    named in ``marks_of`` when given: a Build again… saves and reads its new revision, which marks it)."""
    out = []
    gap, at = W.frames_gap(after["frames"], before["frames"])
    if gap > SAME:
        out.append(f"{at} moved {gap:.1e}")
    if after["mates"] != before["mates"]:
        out.append(f"mates {[(n, before['mates'].get(n), v) for n, v in after['mates'].items() if before['mates'].get(n) != v]}")
    if after["by_mode"] != before["by_mode"]:
        out.append(f"flags {[(n, before['by_mode'].get(n), v) for n, v in after['by_mode'].items() if before['by_mode'].get(n) != v]}")
    marked = sorted(n for n, v in after["flags_after"].items() if v and not before["flags_after"].get(n)
                    and (marks_of is None or n in marks_of))
    if marked:
        out.append(f"marked {marked}")
    if after["active"] != before["active"]:
        out.append(f"active {before['active']} -> {after['active']}")
    if after.get("entities") != before.get("entities"):
        out.append(f"entities {[(n, before['entities'].get(n), v) for n, v in after['entities'].items() if before['entities'].get(n) != v]}")
    return out


def feature_list(path):
    """Every top-level feature of a part (``Session.feature_states``): (name, type, code)."""
    return run(f"features of {os.path.basename(path)}",
               job(path, lambda s: [(f.name, f.type_name, f.code) for f in s.feature_states()]))


def windows_new(before, seconds=8):
    """S0's P0 watch: the windows of SolidWorks' process new since ``before``, polled ``seconds`` s; those that count
    (a #32770 or a titled window), less what the note exempts, each said as a fact: SolidWorks' notification box, its
    balloon tips (class ``swBalloonTip``, the "Over Defined" one m3 brings, titled or not) and its progress boxes that
    close themselves (W8's ``PROGRESS`` titles, an "Elapsed time" box)."""
    seen, new, handles = {h for h, _, _ in before}, [], []
    for _ in range(seconds):
        for h, c, t in S0.sw_windows():
            if h not in seen:
                seen.add(h)
                # A box's own title is SolidWorks' words; any other window's title (a frame's can hold the licence
                # edition, kept out of this repo's logs) is said only as present or not.
                new.append((c, t if c == "#32770" else ("<titled>" if t else ""),
                            tuple(S0.xlhelp.child_texts(h)[:8])))
                handles.append(h)
        time.sleep(1.0)
    if WW["rule"] is True:
        # Under the What's Wrong rule a What's Wrong box that came and went is a fact, not a window left standing;
        # one still up at the end of the read is what counts.
        kept = []
        for h, w in zip(handles, new):
            if w[0] == "#32770" and w[1] == WHATS_WRONG and not visible_now([h]):
                say(f"fact    What's Wrong came and went within the read after the step (the ruling: a fact); not "
                    "counted as a window left standing")
            else:
                kept.append(w)
        new = kept
    def exempt(w):
        return (w[0] == "swBalloonTip" or (not w[1] and w[2] == W.NOTIFICATION_TEXTS) or w[1] in W.PROGRESS
                or any(str(t).startswith("Elapsed time") for t in w[2]))
    for w in new:
        if exempt(w):
            say(f"fact    a window of SolidWorks' process came and is exempt (balloon, notification or progress): {w}")
    counted = [w for w in new if (w[0] == "#32770" or w[1]) and not exempt(w)]
    return new, counted


def save_user(folder, why):
    """The person saves in SolidWorks every modified document of the copy (W8's save_modified_in)."""
    saved = run("save", W.save_modified_in(folder), 600)
    say(f"person  saved in SolidWorks ({why}): {saved}")


# -- the user's work -------------------------------------------------------------------------------------------------


def user_parts():
    """S0's Sprocket and Housing, built by the strip once a run."""
    if not CTX["parts"]:
        kept = os.path.join(OUT, "user-parts")
        if all(os.path.isfile(os.path.join(kept, n)) for n in ("Sprocket.SLDPRT", "Housing.SLDPRT")):
            say(f"fact    the user's parts built earlier into this <out> are used: {kept}")
            CTX["parts"] = kept
        else:
            CTX["parts"] = S0.build_user_parts(CTX["worker"])
    return CTX["parts"]


def add_user_work(label, desk, folder, inserts, mates, fixed=(), refs=None, off=None):
    """The user's components inserted by AddComponent5 into the open assembly (identity frames, the given places),
    some fixed; mates made by the app's own add_mate, by named axes and planes or by components, never a face; every
    new mate's flag set on in every mode (``off``: mate -> the modes it is suppressed in) and read back. Returns the
    components' Name2s and the mates' AddMate5 statuses."""
    box = desk.record.gearbox
    asm, modes = box.assembly, list(box.modes)
    paths = sorted({os.path.join(folder, part) for _, part, _, _ in inserts})
    off = dict(off or {})

    def work(s):
        out = {"components": {}, "mates": {}}
        for path in paths:
            s.open_document(path)
        s.open_document(asm)
        out["active"] = s.active_configuration()
        for handle, part, at, _ in inserts:
            out["components"][handle] = s.add_component(handle, os.path.join(folder, part), at)
            s.place_component(handle, IDENTITY, at, kind=swcom.ASSEMBLY_TRAIN)
        for handle in fixed:
            s.fix_component(handle)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        for handle, name in (refs or {}).items():
            s.find_component(handle, name)
        made = []
        for handle, kind, a, b, value, name, extra in mates:
            if kind == "lock":
                kept, _ = s.add_mate(handle, "lock", a, b, name=name)
            else:
                kept, _ = s.add_mate(handle, kind, a, b, value, name, **extra)
            made.append((handle, kept))
            out["mates"][kept] = {"status": s.mate_status(kept)}
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        if modes:
            for handle, kept in made:
                out["mates"][kept]["as_made"] = s.mate_suppression(handle, modes)
            for handle, kept in made:
                s.set_mate_suppressed_in(handle, False, modes)
                if off.get(kept):
                    s.set_mate_suppressed_in(handle, True, off[kept])
                out["mates"][kept]["set"] = s.mate_suppression(handle, modes)
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        out["states"] = [(m.name, m.code, m.suppressed) for m in s.mate_states()]
        return out
    got = run(f"{label}: the user's work", job(asm, work), 900)
    names = [got["components"][h] for h, _, _, _ in inserts]
    say(f"fact    {label}: inserted {names} with {got['active']} active; mates "
        f"{ {n: m.get('status') for n, m in got['mates'].items()} } (AddMate5 status)")
    for name, m in got["mates"].items():
        if "set" in m:
            say(f"        {name}: as made {m['as_made']}; set {m['set']}")
    wrong = {n: m["set"] for n, m in got["mates"].items()
             if "set" in m and m["set"] != {c: c in off.get(n, ()) for c in modes}}
    check(names == [want for _, _, _, want in inserts], f"{label}: the components are named {names}")
    if wrong:
        stop(f"{label}: a new mate's flag did not read back as set in every mode: {wrong} (§0.3)")
    check(True, f"{label}: every new mate's flag reads back as set in every mode")
    bad = [(n, c) for n, c, sup in got["states"] if c and not sup]
    check(not bad, f"{label}: every mate on in {got['active']} reads error code 0 after the user's work: {bad}")
    return names, got


def keyway(label, part, name="User Keyway", at=(5.0, 0.0), radius=1.5):
    """The user's keyway in a part: a Ø3 cut through the part, by the session's own sketch and cut calls (S0's P0)."""
    def work(s):
        s.open_sketch("uk", 1)
        s.sketch_circle("ukc", at, radius)
        s.close_sketch("uk", f"{name} Sketch")
        s.cut_extrude("ukcut", "uk", name)
        return bool(s.rebuild()), [(f.name, f.type_name, f.code) for f in s.feature_states()]
    rebuilt, features = run(f"{label}: {name}", job(part, work))
    mine = [f for f in features if f[0] == name]
    check(rebuilt and mine and not mine[0][2], f"{label}: {name} made in {os.path.basename(part)}, rebuilt "
          f"{rebuilt}, its code {mine[0][2] if mine else None}")
    return features


def rb_refs(box):
    names = dict(W.bodies(box))
    return {"lay": box.layout_component, "sun": names["Sun"], "slv": names["RangeSlv"]}


def rb_mates(desk):
    """setup's mates: the axes on the layout, the locks to Sun and RangeSlv and between two sprockets, Sprocket-4 held
    by a distance to Sprocket-3 (user–user) and an angle to the layout."""
    axes = {s.shaft: s.axis_name for s in wb_layout.shaft_layouts(desk.a.spec)}
    return (("ua1", "coincident", "u1:Gear Axis", f"lay:{axes['Input']}", 0.0, "UserAxis1", {}),
            ("ua2", "coincident", "u2:Gear Axis", f"lay:{axes['Output']}", 0.0, "UserAxis2", {}),
            ("ul1", "lock", "sun", "u1", 0.0, "UserLock1", {}),
            ("ul2", "lock", "slv", "u2", 0.0, "UserLock2", {}),
            ("ul3", "lock", "u1", "u3", 0.0, "UserLock3", {}),
            ("ua4", "coincident", "u4:Gear Axis", f"lay:{axes['Input']}", 0.0, "UserAxis4", {}),
            ("ud4", "distance", "u4:plane1", "u3:plane1", RB_GAP, "UserDist4", {}),
            ("ug4", "angle", "u4:plane2", "lay:plane3", 90.0, "UserAngle4", {}))


def rb_expected(box):
    """What each of setup's mates joins, by Name2 (M1)."""
    names = dict(W.bodies(box))
    lay = box.layout_component
    return {"UserAxis1": {"Sprocket-1", lay}, "UserAxis2": {"Sprocket-2", lay}, "UserLock1": {names["Sun"], "Sprocket-1"},
            "UserLock2": {names["RangeSlv"], "Sprocket-2"}, "UserLock3": {"Sprocket-1", "Sprocket-3"},
            "UserAxis4": {"Sprocket-4", lay}, "UserDist4": {"Sprocket-4", "Sprocket-3"},
            "UserAngle4": {"Sprocket-4", lay}}


def sun_part(box):
    return next(c.part for c in box.components if c.gear == "Sun")


def rb_users():
    return [want for _, _, _, want in RB_INSERTS]


def pairs_of(box, users):
    return W.bodies(box) + [(u, u) for u in users]


# -- masters ---------------------------------------------------------------------------------------------------------


def done_here(name):
    """What of a section this <out> holds already: its copy folder, and a builder's master."""
    paths = [os.path.join(OUT, name)] + ([os.path.join(OUT, name + W.MASTER_SUFFIX)] if name in ("setup", "reducer")
                                         else [])
    return [p for p in paths if os.path.exists(p)]


def rangebox_master():
    if MASTER["rangebox"]:
        return MASTER["rangebox"]
    here = os.path.join(OUT, "rangebox" + W.MASTER_SUFFIX)
    if not os.path.isdir(here) and os.path.exists(os.path.join(OUT, "rangebox")):
        raise AssertionError("a RangeBox build earlier into this <out> kept no master; give --master")
    if not os.path.isdir(here):
        say("fresh   no --master: RangeBox built here through S0's own build_master (the app's own Build)")
        try:
            S0.build_master(CTX["worker"], CTX["excel"])
        except S0.S0Stop as exc:
            stop(f"the RangeBox master: {exc}")
    MASTER["rangebox"] = here
    return here


def user_master():
    if MASTER["setup"]:
        return MASTER["setup"]
    here = os.path.join(OUT, "setup" + W.MASTER_SUFFIX)
    if not os.path.isdir(here) and os.path.exists(os.path.join(OUT, "setup")):
        raise AssertionError("setup ran earlier in this run and kept no setup.master; give --user-master")
    if not os.path.isdir(here):
        say("fresh   no --user-master and none in this run: setup runs first")
        section_setup(RESULT["sections"].setdefault("setup", {}))
    if not os.path.isdir(here):
        raise AssertionError("setup kept no setup.master")
    MASTER["setup"] = here
    return here


def reducer_master():
    if MASTER["reducer"]:
        return MASTER["reducer"]
    here = os.path.join(OUT, "reducer" + W.MASTER_SUFFIX)
    if not os.path.isdir(here) and os.path.exists(os.path.join(OUT, "reducer")):
        raise AssertionError("reducer ran earlier in this run and kept no reducer.master; give --reducer-master")
    if not os.path.isdir(here):
        say("fresh   no --reducer-master and none in this run: reducer runs first")
        section_reducer(RESULT["sections"].setdefault("reducer", {}))
    if not os.path.isdir(here):
        raise AssertionError("reducer kept no reducer.master")
    MASTER["reducer"] = here
    return here


def copy_desk(master, section, workbook):
    """``copy_built`` of a kept master read through the window's W9a path, its workbook open in this run's Excel."""
    try:
        folder = w8_step(W.copy_built, master, section)
    except W.CopyStop as exc:
        raise AssertionError(f"{section}: the copy of {os.path.basename(master)} stopped: {exc}") from None
    path = os.path.join(folder, workbook)
    desk = Desk9(path, CTX["worker"], strip=folder)
    desk.read()
    box = desk.record.gearbox if desk.record is not None else None
    check(W.turning(desk) and W.under(box.assembly, folder) and desk.record.digest == desk.reading.digest,
          f"{section}: the copy reads as built from this workbook, its assembly in the copy")
    book = W.Workbook(CTX["excel"], path, section)
    return folder, path, book, desk


def users_in_copy(section, desk, folder, users):
    """The user's components found in the copy, each loaded from the copy's folder (``Session.components``)."""
    got = run(f"{section}: components", job(desk.record.gearbox.assembly,
                                             lambda s: [(c.name, c.path, c.fixed, c.state, c.code)
                                                        for c in s.components()]))
    mine = {n: p for n, p, _, _, _ in got if n in users}
    check(set(mine) == set(users) and all(W.under(p, folder) for p in mine.values()),
          f"{section}: the user's components {sorted(mine)} are there, each loaded from the copy "
          f"({ {n: os.path.basename(p) for n, p in mine.items()} })")
    return got


# -- M3 ------------------------------------------------------------------------------------------------------------


def assembly_rebuild(label, asm, folder):
    """The app's assembly rebuild (``Session.rebuild``, ASSEMBLY_TRAIN: ``findings.MATED_ASSEMBLY_REBUILD_ROUTE``)
    under the watch: its return, every mate's code, each component's code, GetWhatsWrongCount, and every window of
    SolidWorks' process new in the 8 s after (S0's P0). A window that counts is a STOP (§0.3: any dialog)."""
    before = S0.sw_windows()

    def work(s):
        rebuilt = bool(s.rebuild(kind=swcom.ASSEMBLY_TRAIN))
        count = swcom._by_ref(call(call(s._doc(), "Extension"), "GetWhatsWrongCount"))  # noqa: SLF001
        return {"rebuilt": rebuilt, "whats_wrong": count, "mates": {m.name: (m.code, m.suppressed) for m in s.mate_states()},
                "components": {c.name: c.code for c in s.components()}, "flags": W.folder_flags(s, folder)}
    got = run(f"{label}: the assembly rebuild", job(asm, work), 300)
    box = WW["job_last"] if WW["rule"] is True and WW["job_last"] and WW["job_last"]["what"].startswith(label) else None
    got["whats_wrong_box"] = [] if box is None else [e["call_in_progress"] for e in box["seen"]]
    if got["whats_wrong_box"]:
        say(f"fact    {label}: What's Wrong showed during this step (the assembly activated and rebuilt), as SolidWorks "
            f"shows it when a person does this, the worker in {got['whats_wrong_box']}; it went by itself")
    new, counted = windows_new(before)
    got["windows_new"], got["windows_counted"] = new, counted
    say(f"fact    {label}: ForceRebuild (the app's train route) returned {got['rebuilt']}; GetWhatsWrongCount "
        f"{got['whats_wrong']}; mates in error { {n: c for n, (c, sup) in got['mates'].items() if c and not sup} or 'none'}"
        f"; components in error { {n: c for n, c in got['components'].items() if c} or 'none'}; windows new "
        f"{new or 'none'}")
    watch_check(label)
    if counted:
        stop(f"{label}: a window came up after the assembly rebuild: {counted} (§0.3: any dialog, What's Wrong among them)")
    return got


def m3_findings():
    """The M3 findings the app's gate reads after an assembly rebuild that returned False, by ``getattr`` (a check
    fails, naming it, when one is not in this source), and the gate itself as the app holds it,
    ``swbuild.assembly_rebuild_settled(revision)``, followed as it stands (the coordinator's ruling: it stays right
    when the gate changes, as it did for 2024): ``(the app's settled answer or None, the findings' values)``."""
    revision = tuple(W.TAG["revision"])
    year = swcom.release_year(int(revision[0]))
    names = {"mate": f"ASSEMBLY_REBUILD_WITH_USER_MATE_IN_ERROR_ON_{year}",
             "feature": f"ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_{year}",
             "whats_wrong": f"WHATS_WRONG_OPENS_ON_ASSEMBLY_REBUILD_ON_{year}"}
    missing = [n for n in names.values() if not hasattr(findings, n)]
    check(not missing, f"the M3 findings the app reads are in findings.py: missing {missing or 'none'}")
    values = {k: getattr(findings, n, None) for k, n in names.items()}
    app = getattr(swbuild, "assembly_rebuild_settled", None)
    if app is None:
        check(False, "swbuild.assembly_rebuild_settled is not in this source: the app's rule on a False rebuild with "
                     "only the user's work in error is not there to demonstrate")
        settled = None
    else:
        settled = app(revision)
    say(f"fact    the M3 findings for {year}: { {names[k]: v for k, v in values.items()} }; the app's gate "
        f"(swbuild.assembly_rebuild_settled) answers {settled}")
    return settled, values


def ahead_after_false(settled, kind):
    """Whether, on this version, an Update whose assembly rebuild returns False with only the user's ``kind``
    ("mate" or "feature") in error goes ahead, as the app's gate answers (``settled``, from
    ``swbuild.assembly_rebuild_settled``): ``swbuild._rebuild_laid_to_user`` lays a False rebuild to the user only
    where the gate is settled (what the box does is the gate's own business: What's Wrong not opening on the rebuild
    at 6f3d6fb, the box not blocking an Update since 2024's ruling), a part's feature in error makes the rebuild False,
    and, for a mate alone, a mate in error makes it False too."""
    if not settled:
        return False
    return settled.get("feature") is False and (kind == "feature" or settled.get("mate") is False)


def whats_wrong_expected(kind):
    """``findings.WHATS_WRONG_OPENS_IN_UPDATE_WITH_{USER_MATE|PART_FEATURE}_IN_ERROR_ON_<year>`` by ``getattr``
    (None when not in this source or not measured), for ``kind`` "mate" or "feature"."""
    year = swcom.release_year(int(W.TAG["revision"][0]))
    name = f"WHATS_WRONG_OPENS_IN_UPDATE_WITH_{'USER_MATE' if kind == 'mate' else 'PART_FEATURE'}_IN_ERROR_ON_{year}"
    return name, getattr(findings, name, None)


def whats_wrong_showed(label, kind):
    """After an app Update with the user's ``kind`` in error: where this version's finding says What's Wrong opens in
    such an Update (and the rule lets it), the last job's record must show it came and went: a fact a user will see,
    asserted, not a failure of the app. Elsewhere what the watch saw is said."""
    name, expected = whats_wrong_expected(kind)
    record = WW["last"] or {}
    seen, gone = record.get("seen", []), record.get("gone", [])
    went = bool(seen) and len(gone) >= len(seen) and not record.get("up_at_the_end")
    if expected is True and WW["rule"] is True:
        check(went, f"{label}: What's Wrong showed during the Update and went by itself, as {name} says it does on "
                    f"this version (seen {seen}; gone {gone}; frame enabled at the end "
                    f"{record.get('frame_enabled_at_the_end')})")
    else:
        say(f"fact    {label}: {name} {expected!r}, the What's Wrong rule {WW['rule']!r}; the watch saw What's Wrong "
            f"{len(seen)} time(s)")
    return {"finding": name, "expected": expected, "seen": seen, "gone": gone}


def said_of(sentence, name):
    """The sentences of ``sentence`` that name ``name``."""
    return [f for f in re.split(r"(?<=[.!?])\s+", sentence or "") if name in f]


def judge_user_error_update(label, desk, result, name, rebuilt, settled, kind, before):
    """An Update pressed with only the user's ``name`` in error (``before``: already before the press, else newly
    by it): on a version whose findings let it, or when the assembly rebuild returned True anyway, it goes ahead and
    its result AND its sentence name ``name`` as the user's, before or newly as it was; otherwise today's stop, its
    sentence naming ``name``. ``rebuilt``: what the assembly's rebuild returned with it in error (None: not read)."""
    expected = bool(rebuilt) or ahead_after_false(settled, kind)
    if result is None:
        check(False, f"{label}: the press raised where an Update was expected: {desk.error}")
        return expected
    sentence = desk.note[0]
    frags = said_of(sentence, name)
    # "were in error in SolidWorks before this Update", "was in error before this Update"; not the stop's "It had
    # already changed …", nor "is in error after the rebuild".
    before_said = any(re.search(r"in error\b[^.]*\bbefore\b", f) for f in frags)
    in_before = result.user_work is not None and any(name in n for n in result.user_work.in_error)
    in_after = (any(name in n for _, n in result.user_in_error) or any(name in f"{f.name} in {os.path.basename(f.path)}"
                                                                         for f in result.user_features_in_error))
    say(f"fact    {label}: ok {result.ok}; failures {result.failures}; laid to the user's work alone "
        f"{getattr(result, 'rebuild_from_user_alone', None)}; {name} in error before {in_before}, after {in_after}; "
        f"the sentence's words on it {frags}")
    if expected:
        check(result.ok and bool(frags) and before_said == before and in_before == before,
              f"{label}: the Update went ahead (rebuild {rebuilt}, findings {settled}) and its result and sentence name "
              f"{name} as the user's, {'already in error before' if before else 'newly in error'} the Update")
    else:
        check(not result.ok and bool(frags) and before_said == before,
              f"{label}: on this version (findings {settled}) the Update stops as it did before the change, its "
              f"sentence naming {name} as the user's, {'in error before' if before else 'newly in error'}")
    return expected


def m3_mate_in_error(out, tag, folder, desk):
    """m3's set-up up to the app's first value Update (shared with ``box``): the toggle and the M3 findings read, the
    user's sprocket and housing, the clean baseline, and UserGap made over-defining and read, saved as the user
    leaves it. Returns (settled findings, the record's gearbox, its assembly, its modes)."""
    parts = user_parts()
    settled, _ = m3_findings()
    toggle = run(f"{tag}: show errors every rebuild", lambda s: bool(call(s._app, "GetUserPreferenceToggle",  # noqa: SLF001
                                                                      S0.SHOW_ERRORS_EVERY_REBUILD)))
    out["show_errors_every_rebuild"] = toggle
    say(f"fact    {tag}: SolidWorks' \"show errors every rebuild\" (toggle {S0.SHOW_ERRORS_EVERY_REBUILD}) reads {toggle}")
    for name in ("Sprocket.SLDPRT", "Housing.SLDPRT"):
        shutil.copy2(os.path.join(parts, name), os.path.join(folder, name))
    box = desk.record.gearbox
    asm, modes = box.assembly, list(box.modes)
    axes = {s.shaft: s.axis_name for s in wb_layout.shaft_layouts(desk.a.spec)}
    # The first run (2920a09) made two distance mates agree in value only: UserFront 100 to the layout's Front and
    # UserGap 40 to the housing's. A plane-to-plane distance mate's side is AddMate5's Flip, which the app's
    # "distance" leaves False and no finding says which side that is, so UserGap came back over-defining (status
    # 5, codes 46 and 47, findings.MATE_ERROR_OVER_DEFINED / ILL_DEFINED) before anything was meant to be wrong.
    # Now the baseline holds one axial mate only, clean by construction whichever side SolidWorks takes, and the
    # distance it leaves is read, not assumed; the contradiction is then a second mate to the housing at that
    # distance plus 1 mm, which no side can satisfy. (The value change through set_dimension_in, every mode in one
    # call, also read 0 in N and L: the app sets one configuration per call, and a configuration never set reads
    # 0, findings.VALUE_UNSET_READS_ZERO; nothing here sets a distance any more.)
    inserts = (("u1", "Sprocket.SLDPRT", (0.0, 0.0, 100.0), "Sprocket-1"),
               ("uh", "Housing.SLDPRT", (0.0, 0.0, 60.0), "Housing-1"))
    mates = (("ua", "coincident", "u1:Gear Axis", f"lay:{axes['Input']}", 0.0, "UserAxis", {}),
             ("uf", "distance", "u1:plane1", "lay:plane1", 100.0, "UserFront", {}))
    _, made = add_user_work(tag, desk, folder, inserts, mates, fixed=("uh",), refs={"lay": box.layout_component})
    check(all(m.get("status") == findings.ADD_MATE_NO_ERROR for m in made["mates"].values()),
          f"{tag}: the baseline's mates were made sound (AddMate5 status {findings.ADD_MATE_NO_ERROR}): "
          f"{ {n: m.get('status') for n, m in made['mates'].items()} }")

    def where(s):
        s.find_component("u1", "Sprocket-1")
        s.find_component("uh", "Housing-1")
        return s.component_frame("u1"), s.component_frame("uh")
    sprocket_at, housing_at = run(f"{tag}: where the sprocket stands", job(asm, where))
    z_s, z_h = float(sprocket_at[1][2]), float(housing_at[1][2])
    gap = abs(z_s - z_h)
    out["placed"] = {"sprocket_z": z_s, "housing_z": z_h, "gap": gap}
    say(f"fact    {tag}: UserFront left Sprocket-1's origin at z {z_s:.6f} (inserted at 100: the side AddMate5's "
        f"Flip False took); Housing-1 at z {z_h:.6f}; their Front planes {gap:.6f} mm apart")
    save_user(folder, "the user's sprocket and housing")
    out["baseline"] = assembly_rebuild(f"{tag} baseline", asm, folder)
    if not out["baseline"]["rebuilt"] or any(c for c, sup in out["baseline"]["mates"].values() if not sup):
        raise AssertionError(f"{tag}: the baseline is not clean, so nothing after it would answer M3: rebuild "
                             f"{out['baseline']['rebuilt']}, mates {out['baseline']['mates']}")
    check(True, f"{tag}: with nothing in error the assembly rebuild returns True and no mate is in error")

    say(f"-- {tag}  a user mate in error: UserGap, Sprocket-1's Front plane {gap + 1.0:.6f} mm from Housing-1's (the "
        f"distance read plus 1 mm), which UserFront contradicts on either side")

    def contradiction(s):
        s.find_component("u1", "Sprocket-1")
        s.find_component("uh", "Housing-1")
        kept, _ = s.add_mate("ug", "distance", "u1:plane1", "uh:plane1", gap + 1.0, "UserGap")
        status = s.mate_status(kept)
        flags = s.mate_suppression("ug", modes)
        return kept, status, flags
    before = S0.sw_windows()
    kept, status, flags = run(f"{tag}: UserGap made", job(asm, contradiction))
    new, counted = windows_new(before)
    watch_check(f"{tag}: UserGap made")
    if counted:
        stop(f"{tag}: a window came up when the over-defining mate was made: {counted} (§0.3: any dialog)")
    say(f"fact    {tag}: {kept} made: AddMate5 status {status} (over-defining is {findings.ADD_MATE_OVER_DEFINED}); "
        f"flags {flags}")
    got = out["mate_error"] = assembly_rebuild(f"{tag} a user mate in error", asm, folder)
    got["add_mate_status"] = status
    users_bad = {n: c for n, (c, sup) in got["mates"].items() if c and not sup and n.startswith("User")}
    app_bad = {n: c for n, (c, sup) in got["mates"].items() if c and not sup and not n.startswith("User")}
    check(bool(users_bad) and not app_bad,
          f"{tag}: only the user's mates read in error, so the reading answers M3: user {users_bad} "
          f"(codes as read, not read for meaning: findings.MATE_ERROR_2024), the app's {app_bad or 'none'}")
    say(f"answer  M3 (assembly, a user mate in error): the rebuild returned {got['rebuilt']}, What's Wrong "
        f"{got['whats_wrong']}, codes {users_bad}, What's Wrong box during the step "
        f"{got.get('whats_wrong_box') or 'none'}, windows left standing {got['windows_counted'] or 'none'}")
    save_user(folder, "the mate in error, as the user leaves it")
    return settled, box, asm, modes


def section_m3(out):
    say("== m3  ISSUE-1-PLAN §4 M3: an assembly rebuild, and the app's Update, with only a user mate and then only a "
        "user feature in error, under the dialog watch, ahead of anything that depends on it")
    folder, path, book, desk = copy_desk(rangebox_master(), "m3", "RangeBox.xlsx")
    try:
        settled, box, asm, modes = m3_mate_in_error(out, "m3", folder, desk)

        say("-- m3  the app's value Update (Sun's Backlash 0.4) with only that user mate in error; a quiet press first "
            "records the inventory, so the footer can say before the press what of the user's is in error")
        ahead = quiet_then_edit("m3 mate in error", desk, book, 0.4)
        line = ui_text.user_work_line(ahead)[0] if ahead is not None else ""
        check("UserGap" in line, f"m3: the footer says before the press that UserGap is in error: {line[:160]!r}")
        before = S0.sw_windows()
        result, _ = press(desk, "m3 Update with a user mate in error")
        new, counted = windows_new(before)
        watch_check("m3 Update with a user mate in error")
        if counted:
            stop(f"m3: a window came up during the Update with a user mate in error: {counted}")
        out["update_mate_error"] = _update_fact(desk, result)
        out["update_mate_error"]["windows_new"] = new
        out["update_mate_error"]["whats_wrong"] = whats_wrong_showed("m3 Update with a user mate in error", "mate")
        judge_user_error_update("m3 Update with a user mate in error", desk, result, "UserGap",
                                out["mate_error"]["rebuilt"], settled, "mate", before=True)

        say("-- m3  UserGap suppressed in every mode, as the user would: nothing in error again")

        def suppress(s):
            s.find_mate("ug", "UserGap")
            s.set_mate_suppressed_in("ug", True, modes)
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            return s.mate_suppression("ug", modes)
        flags = run("m3: UserGap suppressed", job(asm, suppress))
        if not all(flags.values()):
            stop(f"m3: UserGap did not read back suppressed in every mode: {flags} (§0.3)")
        got = assembly_rebuild("m3 the mate suppressed", asm, folder)
        check(not any(c for n, (c, sup) in got["mates"].items() if not sup),
              f"m3: with UserGap suppressed no mate is in error: {got['mates']}")

        say("-- m3  a user feature in error: a keyway in the user's Sprocket part, then its own Bore Diameter 10 -> 14 "
            "(S0's P0 mechanism: the keyway left inside the bore)")
        sprocket = os.path.join(folder, "Sprocket.SLDPRT")
        keyway("m3", sprocket)

        def bore(s):
            s.set_global_variable(spur.BORE, "14")
            rebuilt = bool(s.rebuild())
            count = swcom._by_ref(call(call(s._doc(), "Extension"), "GetWhatsWrongCount"))  # noqa: SLF001
            return rebuilt, count, [(f.name, f.code) for f in s.feature_states() if f.code]
        before = S0.sw_windows()
        rebuilt, count, errors = run("m3: Sprocket's bore 14", job(sprocket, bore))
        new, counted = windows_new(before)
        out["part_rebuild"] = {"rebuilt": rebuilt, "whats_wrong": count, "errors": errors, "windows_new": new}
        say(f"fact    m3: the Sprocket part's rebuild returned {rebuilt}; What's Wrong {count}; features in error "
            f"{errors}; windows new {new or 'none'}")
        if counted:
            stop(f"m3: a window came up after the part's rebuild: {counted}")
        check(any(n == "User Keyway" for n, _ in errors) and all(n.startswith("User") for n, _ in errors),
              f"m3: only the user's keyway is in error in the user's part: {errors}")
        got = out["feature_error"] = assembly_rebuild("m3 a user feature in error", asm, folder)
        say(f"answer  M3 (assembly, a user feature in error in a component's part): the rebuild returned "
            f"{got['rebuilt']}, What's Wrong {got['whats_wrong']}, What's Wrong box during the step "
            f"{got.get('whats_wrong_box') or 'none'}, windows left standing {got['windows_counted'] or 'none'}")
        save_user(folder, "the user's part in error, as the user leaves it")

        say("-- m3  the app's value Update (Sun's Backlash 0.42) with only the user's feature in error, in the part of "
            "Sprocket-1, which nothing would carry (no lock); the footer first, from a quiet press's inventory")
        ahead = quiet_then_edit("m3 feature in error", desk, book, 0.42)
        line = ui_text.user_work_line(ahead)[0] if ahead is not None else ""
        check("Sprocket-1" in line, f"m3: the footer says before the press that Sprocket-1 is in error: {line[:160]!r}")
        before = S0.sw_windows()
        result, _ = press(desk, "m3 Update with a user feature in error")
        new, counted = windows_new(before)
        watch_check("m3 Update with a user feature in error")
        if counted:
            stop(f"m3: a window came up during the Update with a user feature in error: {counted}")
        out["update_feature_error"] = _update_fact(desk, result)
        out["update_feature_error"]["windows_new"] = new
        out["update_feature_error"]["whats_wrong"] = whats_wrong_showed("m3 Update with a user feature in error",
                                                                        "feature")
        judge_user_error_update("m3 Update with a user feature in error", desk, result, "Sprocket-1",
                                out["feature_error"]["rebuilt"], settled, "feature", before=True)

        say("-- m3  the same Sprocket-1, its part still in error, now carried: UserFront suppressed, a user lock to Sun "
            "(the app's new rule: a press that would put, by route (c1), a component whose own part has a feature in "
            "error refuses before any write)")

        def carried(s):
            s.find_component("u1", "Sprocket-1")
            s.find_component("sun", dict(W.bodies(box))["Sun"])
            s.find_mate("uf", "UserFront")
            s.set_mate_suppressed_in("uf", True, modes)
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            kept, _ = s.add_mate("ul", "lock", "sun", "u1", name="UserLockSun")
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            s.set_mate_suppressed_in("ul", False, modes)
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            return s.mate_status(kept), s.mate_suppression("uf", modes), s.mate_suppression("ul", modes)
        status, front, lock = run("m3: Sprocket-1 locked to Sun", job(asm, carried))
        say(f"person  m3: UserFront suppressed {front}; UserLockSun made (AddMate5 status {status}), flags {lock}")
        if not all(front.values()) or any(lock.values()):
            stop(f"m3: the user's mates did not read back as set: UserFront {front}, UserLockSun {lock} (§0.3)")
        save_user(folder, "the lock made")
        # A quiet press first, so the record holds UserLockSun (a quiet press carries nothing, so it does not refuse),
        # then the footer must foresee the refusal (W9A-CLOSE-2026-REVIEW finding 5: at 6f3d6fb the footer was green,
        # its inventory older than the lock).
        ahead = quiet_then_edit("m3 carried in error", desk, book, 0.44)
        foreseen = [p for p in (ahead.problems if ahead is not None else ())
                    if p.kind == swbuild.PROBLEM_COMPONENT and "Sprocket-1" in p.sentence]
        check(bool(foreseen), f"m3: the footer foresees the refusal of Sprocket-1, carried and in error: "
                              f"{[(p.kind, p.sentence[:120]) for p in (ahead.problems if ahead else ())]}")
        problems = refuse_press("m3 carried component with its part in error", desk, folder,
                                {swbuild.PROBLEM_COMPONENT}, ("UserLockSun",), ("Sprocket-1",), ahead=ahead,
                                users=["Sprocket-1", "Housing-1"])
        out["carried_in_error"] = [(p.kind, p.sentence) for p in problems]
        RESULT["proposal"]["M3"] = {
            "assembly_rebuild_with_user_mate_in_error": out["mate_error"]["rebuilt"],
            "whats_wrong_count_with_user_mate_in_error": out["mate_error"]["whats_wrong"],
            "user_mate_codes": {n: c for n, (c, sup) in out["mate_error"]["mates"].items()
                                if c and not sup and n.startswith("User")},
            "over_defining_mate_made_with_status": out["mate_error"].get("add_mate_status"),
            "whats_wrong_count_with_user_feature_in_error": out["feature_error"]["whats_wrong"],
            "assembly_rebuild_with_user_feature_in_error": out["feature_error"]["rebuilt"],
            "part_rebuild_with_user_feature_in_error": out["part_rebuild"]["rebuilt"],
            "windows_new_after_each": {k: (out.get(k) or {}).get("windows_new") for k in
                                       ("baseline", "mate_error", "feature_error", "update_mate_error",
                                        "update_feature_error")},
            "show_errors_every_rebuild": out.get("show_errors_every_rebuild"),
            "update_ok_with_user_mate_in_error": (out["update_mate_error"] or {}).get("ok"),
            "update_ok_with_user_feature_in_error": (out["update_feature_error"] or {}).get("ok")}
        say(f"propose M3: {RESULT['proposal']['M3']}")
    finally:
        w8_step(W.end_copy, CTX["worker"], folder, "m3")


def _update_fact(desk, result):
    if result is None:
        say(f"fact    the press raised: {desk.error}")
        return {"raised": f"{type(desk.error).__name__}: {desk.error}"}
    return {"ok": result.ok, "failures": [list(f) for f in result.failures], "user_in_error": result.user_in_error,
            "user_features_in_error": [(f.name, os.path.basename(f.path), f.code) for f in result.user_features_in_error],
            "in_error_before": result.user_work.in_error if result.user_work is not None else None,
            "sentence": desk.note[0]}


# -- setup: RangeBox with the user's work ----------------------------------------------------------------------------


def section_setup(out):
    say("== setup  RangeBox with the user's work, saved in place as a person would, reopened; M1 and M2 by the app's "
        "own reads; a quiet Update records the inventory; kept as setup.master")
    parts = user_parts()
    folder, path, book, desk = copy_desk(rangebox_master(), "setup", "RangeBox.xlsx")
    try:
        _setup(out, parts, folder, desk)
    except (AssertionError, W.Halt):
        w8_step(W.end_copy, CTX["worker"], folder, "setup")
        raise
    MASTER["setup"] = w8_step(W.keep_master, CTX["worker"], folder, "setup")
    if not MASTER["setup"]:
        raise AssertionError("setup: setup.master was not kept")


def _setup(out, parts, folder, desk):
    for name in ("Sprocket.SLDPRT", "Housing.SLDPRT"):
        shutil.copy2(os.path.join(parts, name), os.path.join(folder, name))
    box = desk.record.gearbox
    asm, modes = box.assembly, list(box.modes)
    ahead_of(desk, "setup, before the user's work (nothing of the user's on record)")
    say("step    setup: the user's components go in by AddComponent5 into the reopened assembly with H, N and L")
    names, got = add_user_work("setup", desk, folder, RB_INSERTS, rb_mates(desk), fixed=("uh",), refs=rb_refs(box))
    out["made"] = got
    keyway("setup", sun_part(box))
    pairs = pairs_of(box, rb_users())
    every = read_every("setup, as made", asm, pairs, modes)
    for mode in modes:
        bad = {n: c for n, (c, sup) in every["mates"][mode].items() if c and not sup}
        check(not bad, f"setup: in {mode} (shown) every mate on there reads error code 0: {bad or 'none'}")
        frames = every["frames"][mode]
        dz = float(frames["Sprocket-4"][1][2]) - float(frames["Sprocket-3"][1][2])
        out.setdefault("sprocket4_dz", {})[mode] = dz
        check(abs(abs(dz) - RB_GAP) <= TOL, f"setup: in {mode} Sprocket-4 stands {dz:+.6f} mm from Sprocket-3 along the "
                                            f"axis, UserDist4's {RB_GAP:g} on the side AddMate5 took (a fact)")
    clashes = run("setup: interference", lambda s: W.live_interferences(s, asm))
    users = set(rb_users())
    ours = [(names, round(volume, 3)) for names, volume in clashes if set(names) & users]
    out["user_clashes"] = ours
    check(not ours, f"setup: no component of the user's interferes with anything: {ours or 'none'} (all: {clashes})")
    save_user(folder, "the user's work")
    left = run("close", W.quit_in(folder))
    check(not left, f"setup: closed after the save: left {left}")

    say("-- setup  M1 and M2: reopened from its file; every user mate's entities by Session.mate_info, the components "
        "by Session.components, Sun's part's features by Session.feature_states; GetSaveFlag around each read")
    expected = rb_expected(box)

    def m1(s):
        r = {"flags_before": W.folder_flags(s, folder),
             "components": [(c.name, os.path.basename(c.path), c.fixed, c.state, c.code) for c in s.components()],
             "mates": {}}
        for i, m in enumerate(s.mate_states()):
            if m.name not in expected:
                continue
            s.find_mate(f"mi{i}", m.name)
            info = s.mate_info(f"mi{i}")
            r["mates"][m.name] = {"type": info.type, "components": list(info.components), "whole": info.whole,
                                  "code": m.code}
        r["flags_after"] = W.folder_flags(s, folder)
        return r
    m1_read = out["m1"] = run("setup: M1", job(asm, m1))
    _no_new_marks(m1_read, "setup M1 read")
    for name, want in expected.items():
        info = m1_read["mates"].get(name)
        check(info is not None and info["whole"] and set(info["components"]) == want and not info["code"],
              f"setup M1: {name} read whole as joining {sorted(want)}: {info}")
    comps = {n: (p, fx, st, c) for n, p, fx, st, c in m1_read["components"]}
    check(all(n in comps and comps[n][2] in (2, 3) for n in rb_users()) and comps.get("Housing-1", (0, False))[1],
          f"setup: reopened, each user component resolved and Housing-1 fixed: "
          f"{ {n: comps.get(n) for n in rb_users()} }")

    def m2(s):
        r = {"flags_before": W.folder_flags(s, folder)}
        r["features"] = [(f.name, f.type_name, f.code) for f in s.feature_states()]
        r["flags_after"] = W.folder_flags(s, folder)
        return r
    m2_read = out["m2"] = run("setup: M2", job(sun_part(box), m2))
    _no_new_marks(m2_read, "setup M2 read")
    say(f"fact    setup M2: Sun's part's features in tree order {[(n, t, c) for n, t, c in m2_read['features']]}")
    check(any(n == "User Keyway" and not c for n, _, c in m2_read["features"]),
          "setup M2: the user's keyway is in Sun's part, code 0")

    say("-- setup  a quiet Update: the inventory read and recorded (K4); the footer before and after")
    desk.plan_solidworks()
    ahead_of(desk, "setup, before the quiet press")
    frames_before, flags_before = W.gear_frames(CTX["worker"], desk), W.gearbox_flags(CTX["worker"], desk)
    result, _ = press(desk, "setup quiet press")
    if result is None:
        raise AssertionError(f"setup: the quiet press refused: {desk.error}")
    W.check_quiet_update(CTX["worker"], desk, result, "setup quiet press", frames_before, flags_before)
    out["inventory"] = _inventory_checks("setup", desk, result, expected, box)
    ahead_of(desk, "setup, after the quiet press")
    branches_judged(out, desk)


def _no_new_marks(r, label):
    marked = sorted(n for n, v in r["flags_after"].items() if v and not r["flags_before"].get(n))
    if marked:
        stop(f"{label}: the read marked {marked} modified (ISSUE-1-PLAN §0.3)")
    check(True, f"{label}: marked nothing (before {W.marked(r['flags_before']) or 'none'})")


def _inventory_checks(label, desk, result, expected, box):
    """The press's inventory (``GearboxUpdate.user_work``) and the record's (schema 7) against what the user made."""
    work = result.user_work
    entry = desk.record.gearbox.user_work if desk.record is not None and desk.record.gearbox is not None else None
    say(f"fact    {label}: inventory read at {work.read_at if work else None}: components "
        f"{[(c.name, os.path.basename(c.path), c.fixed, c.state, c.code) for c in work.components] if work else None}")
    for m in (work.mates if work else []):
        say(f"        mate {m.name}: {m.kind} type {m.type} touches {list(m.touches)} on {list(m.on)} code {m.code} "
            f"whole {m.whole}")
    say(f"        features {[(f.name, os.path.basename(f.path), f.type_name, f.code) for f in work.features] if work else None}")
    check(work is not None and {c.name for c in work.components} == set(rb_users()),
          f"{label}: the inventory names exactly the user's components: {[c.name for c in work.components] if work else None}")
    if work is not None:
        names = dict(W.bodies(box))
        by_name = {v: k for k, v in names.items()}
        for m in work.mates:
            want = expected.get(m.name)
            if want is None:
                continue
            got = {names.get(n, n) if w == swbuild.APP else box.layout_component if w == swbuild.LAYOUT else n
                   for w, n in m.touches}
            check(got == want and m.whole, f"{label}: the inventory's {m.name} touches {sorted(got)}: "
                                           f"{list(m.touches)} ({'whole' if m.whole else 'NOT whole'})")
        check(not any(c.name in by_name or c.name == box.layout_component for c in work.components),
              f"{label}: no app component listed as the user's")
        # M2 (review point 7): the keyway must be listed, in Sun's part, and nothing of the app's. Its sketch is listed
        # too only when SolidWorks keeps it top-level (an absorbed sketch is a sub-feature of the cut): either is right.
        sun = sun_part(box)
        keyway = [f for f in work.features if f.name == "User Keyway" and store.same_path(f.path, sun)]
        names_listed = sorted(f.name for f in work.features)
        check(bool(keyway) and set(names_listed) <= {"User Keyway", "User Keyway Sketch"},
              f"{label}: M2: the app tells its features from the user's: the inventory lists the User Keyway in Sun's "
              f"part and nothing else: {[(f.name, os.path.basename(f.path)) for f in work.features]}")
    check(entry is not None and list(entry.revision) == list(W.TAG["revision"]) and bool(entry.read_at),
          f"{label}: the record's user_work holds the inventory with revision {list(entry.revision) if entry else None} "
          f"(this SolidWorks {list(W.TAG['revision'])}) read at {entry.read_at if entry else None}")
    return {"read_at": work.read_at if work else None, "components": [c.name for c in work.components] if work else [],
            "mates": {m.name: {"kind": m.kind, "type": m.type, "touches": list(m.touches), "on": list(m.on),
                               "code": m.code, "whole": m.whole} for m in (work.mates if work else [])},
            "features": [(f.name, os.path.basename(f.path), f.code) for f in (work.features if work else [])]}


def branches_judged(out, desk):
    """The branches of route (c1) S0 did not measure, shown refusing by the worker's own pure judgement on the
    inventory just read (``swbuild.judge_user_work``, as the press and the footer call it). Nothing is measured: each
    gear is relabelled to the branch, or Sprocket-1's file to a sub-assembly's; no SolidWorks call."""
    plan = desk.update
    if plan is None or plan.motion is None or desk.record.gearbox.user_work is None:
        check(False, "setup: the branches cannot be judged: no plan or no inventory on record")
        return
    revision = tuple(W.TAG["revision"])
    year = swcom.release_year(int(revision[0]))
    real = swbuild.user_carry_branches(plan.motion, plan.placements)
    say(f"fact    setup: route (c1)'s branches on RangeBox as the app labels them: {real or 'every body on S0s branch'}")
    work = wb_update.recorded_user_work(desk.record.gearbox.user_work)
    mated, trains = wb_update._judged_trains(plan)  # noqa: SLF001 - the trains the footer judges on
    modes = tuple(plan.motion.configurations) or ("",)

    def judge(w, branches):
        return swbuild.judge_user_work(w, modes, set(mated), file="RangeBox.SLDASM", trains=trains, mated=mated,
                                       read_tie=None, branches=branches, revision=revision)
    base = judge(work, real)
    out["branches"] = {"real": dict(real), "S0": [(k, [c for c, _ in v]) for k, v in base.carried.items()]}
    check(not base.problems and {(c, g) for g, v in base.carried.items() for c, _ in v} == set(
        (c, g) for c, g in RB_LOCKED.items()), f"setup: on S0's branch the judgement carries every locked sprocket "
                                               f"with its gear and refuses nothing: {base.carried} {base.problems}")
    for branch in (swbuild.BRANCH_HELD, swbuild.BRANCH_FIXED, swbuild.BRANCH_NO_CARRIER):
        relabelled = dict(real, Sun=branch, RangeSlv=branch)
        j = judge(work, relabelled)
        name = f"USER_MATE_PUT_{branch}_ON_{year}"
        hit = [p for p in j.problems if p.kind == swbuild.PROBLEM_UNSETTLED and name in p.sentence]
        out["branches"][branch] = [p.sentence for p in j.problems]
        settled = getattr(findings, name, None) is True
        check(bool(hit) != settled, f"setup: a lock on a gear put by the {branch} branch refuses while findings.{name} "
                                    f"is {getattr(findings, name, None)!r}: {[p.sentence[:120] for p in hit]}")
    sub = _copy.deepcopy(work)
    sub.components = [dataclasses.replace(c, path=c.path[:-7] + ".SLDASM") if c.name == "Sprocket-1" else c
                      for c in sub.components]
    j = judge(sub, real)
    name = f"USER_MATE_PUT_{swbuild.BRANCH_SUBASSEMBLY}_ON_{year}"
    hit = [p for p in j.problems if p.kind == swbuild.PROBLEM_UNSETTLED and name in p.sentence]
    out["branches"]["SUBASSEMBLY"] = [p.sentence for p in j.problems]
    check(bool(hit), f"setup: Sprocket-1 taken for a sub-assembly refuses while findings.{name} is "
                     f"{getattr(findings, name, None)!r}: {[p.sentence[:120] for p in hit]}")


# -- m1: the rest of M1 ----------------------------------------------------------------------------------------------


def section_m1(out):
    say("== m1  ISSUE-1-PLAN §4 M1's remaining kinds: a user gear mate (user–user) and a distance mate suppressed in "
        "the active mode but on in the others, read by mate_info and by a quiet Update's inventory")
    folder, path, book, desk = copy_desk(user_master(), "m1", "RangeBox.xlsx")
    try:
        box = desk.record.gearbox
        asm, modes = box.assembly, list(box.modes)
        users_in_copy("m1", desk, folder, rb_users())
        axes = {s.shaft: s.axis_name for s in wb_layout.shaft_layouts(desk.a.spec)}
        made = {}
        for mate in (("ua5", "coincident", "u5:Gear Axis", f"lay:{axes['Input']}", 0.0, "UserAxis5", {}),
                     ("ug5", "gear", "u5:Gear Axis", "u4:Gear Axis", 0.0, "UserGear5", {"ratio": (20.0, 20.0)}),
                     # to the layout's Front, so either side AddMate5's Flip takes (+-160) is clear of every body
                     ("ud5", "distance", "u5:plane1", "lay:plane1", 160.0, "UserDist5", {})):
            first = not made
            inserts = (("u5", "Sprocket.SLDPRT", (0.0, 0.0, 160.0), "Sprocket-5"),) if first else ()
            try:
                if first:
                    _, got = add_user_work("m1", desk, folder, inserts, (mate,),
                                           refs={"lay": box.layout_component, "u4": "Sprocket-4"})
                else:
                    _, got = add_user_work("m1", desk, folder, (), (mate,),
                                           refs={"lay": box.layout_component, "u4": "Sprocket-4", "u5": "Sprocket-5"},
                                           off={"UserDist5": [modes[0]]} if mate[5] == "UserDist5" else None)
                made[mate[5]] = got["mates"].get(mate[5])
            except AssertionError as exc:
                check(False, f"m1: {mate[5]} could not be made: {exc}")
        save_user(folder, "the user's gear and per-mode mates")
        expected = {"UserAxis5": {"Sprocket-5", box.layout_component}, "UserGear5": {"Sprocket-5", "Sprocket-4"},
                    "UserDist5": {"Sprocket-5", box.layout_component}}

        def m1(s):
            r = {"flags_before": W.folder_flags(s, folder), "active": s.active_configuration(), "mates": {}}
            for i, m in enumerate(s.mate_states()):
                if m.name in expected:
                    s.find_mate(f"mi{i}", m.name)
                    info = s.mate_info(f"mi{i}")
                    r["mates"][m.name] = {"type": info.type, "components": list(info.components), "whole": info.whole,
                                          "suppressed_here": m.suppressed}
            r["flags_after"] = W.folder_flags(s, folder)
            return r
        r = out["m1"] = run("m1: the reads", job(asm, m1))
        _no_new_marks(r, "m1 read")
        check(r["active"] == modes[0], f"m1: the mode active at the read is {r['active']}, the one UserDist5 is "
                                       f"suppressed in ({modes[0]})")
        for name, want in expected.items():
            info = r["mates"].get(name)
            say(f"answer  M1 {name} with {r['active']} active: {info}")
            if name == "UserDist5":
                continue                     # suppressed in the active mode: what it reads is the answer, not a check
            check(info is not None and info["whole"] and set(info["components"]) == want,
                  f"m1: {name} read whole as joining {sorted(want)}")
        result, _ = press(desk, "m1 quiet press")
        if result is not None and result.user_work is not None:
            for m in result.user_work.mates:
                if m.name in expected:
                    say(f"answer  M1 inventory {m.name}: {m.kind} type {m.type} touches {list(m.touches)} on {list(m.on)} "
                        f"whole {m.whole}")
            gear = next((m for m in result.user_work.mates if m.name == "UserGear5"), None)
            dist = next((m for m in result.user_work.mates if m.name == "UserDist5"), None)
            check(gear is not None and gear.kind == swbuild.USER_GEAR, f"m1: the user's gear mate is judged a gear mate: "
                                                                       f"{gear and gear.kind}")
            check(dist is not None and list(dist.on) == modes[1:], f"m1: UserDist5 is on in {modes[1:]} only: "
                                                                   f"{dist and list(dist.on)}")
            RESULT["proposal"]["M1_suppressed_in_active_read_whole"] = None if dist is None else dist.whole
        else:
            check(False, f"m1: the quiet press gave no inventory: {desk.error}")
    finally:
        w8_step(W.end_copy, CTX["worker"], folder, "m1")


# -- go: the value and slide-offset Updates ---------------------------------------------------------------------------

RB_USER_MATES = ("UserAxis1", "UserAxis2", "UserLock1", "UserLock2", "UserLock3", "UserAxis4", "UserDist4", "UserAngle4")


def go_judge(label, desk, every, rel_orig, flags_set, out, dz_set):
    """After a press, every mode shown: each app body at its frame on record, each locked sprocket at its pose on its
    gear as set up, every user mate on where it was and in no error, Sprocket-4 at its distance from Sprocket-3."""
    box = desk.record.gearbox
    modes = list(box.modes)
    clean = True
    for mode in modes:
        frames = every["frames"][mode]
        gap, at = W.frames_gap(frames, W.mode_record_frames(desk, mode))
        gaps = rel_gaps(rel_of(frames, RB_LOCKED), rel_orig)
        errors = {n: c for n, (c, sup) in every["mates"][mode].items() if c and not sup}
        dz = float(frames["Sprocket-4"][1][2]) - float(frames["Sprocket-3"][1][2])
        free = {g: v for g, v in every["status"][mode].items()
                if g in dict(W.bodies(box)) and g not in box.fixed and v != findings.COMPONENT_UNDER_DEFINED}
        ok = gap <= TOL and all(v <= TOL for v in gaps.values()) and not errors and abs(dz - dz_set[mode]) <= TOL \
            and not free
        clean = clean and ok
        check(ok, f"{label}, {mode} shown: every app body at its frame on record ({gap:.1e} at {at or '-'}); each locked "
                  f"sprocket on its gear as set up {fmt(gaps)}; mates in error {errors or 'none'}; Sprocket-4 "
                  f"{dz:.9f} mm from Sprocket-3 (as set up {dz_set[mode]:.9f}); the train free {not free}")
    flags = {n: f for n, f in every["by_mode"].items() if n in flags_set}
    check(flags == flags_set, f"{label}: every user mate is on in the modes it was on in: "
                              f"{ {n: (flags_set[n], flags.get(n)) for n in flags_set if flags.get(n) != flags_set[n]} or 'as set'}")
    out.setdefault("judged", []).append({"label": label, "clean": clean and flags == flags_set})
    return clean


def entities_of(label, desk, folder):
    """Every user mate's entities (``Session.mate_info``), read in the active mode with nothing shown (§0.3)."""
    box = desk.record.gearbox
    return read_now(f"{label}: the user's mates' entities", box.assembly, folder, pairs_of(box, rb_users()),
                    list(box.modes), entities=RB_USER_MATES)["entities"]


def go_press(label, desk, folder, book, cells, out, rel_orig, flags_set, dz_set):
    W.edit(desk, book, *cells)
    u = desk.update
    check(u is not None and not u.needs_new_revision and not u.refusal,
          f"{label}: classify makes it an Update: structural {u and list(u.structural)}")
    ahead = ahead_of(desk, f"{label}, before the press")
    want = set(RB_LOCKED.items())
    check(predicted_carry(ahead) == want and ahead is not None and not ahead.problems,
          f"{label}: the footer foresees each locked sprocket put with its gear and no refusal: "
          f"{sorted(predicted_carry(ahead))}")
    entities_before = entities_of(f"{label}, before", desk, folder)
    result, calls = press(desk, label)
    if result is None:
        raise AssertionError(f"{label}: the press refused: {desk.error}")
    done = {(c, g) for c, g, _ in result.carried}
    check(result.ok and done == want and {m for _, _, m in result.carried} == set(result.put_in),
          f"{label}: the Update went ahead and put each locked sprocket with its gear in every mode it put "
          f"({result.put_in}): ok {result.ok}, carried {result.carried}, failures {result.failures}")
    check(done == predicted_carry(ahead), f"{label}: what the footer said before the press is what the press carried "
                                          f"(said {sorted(predicted_carry(ahead))}, did {sorted(done)})")
    box = desk.record.gearbox
    allowed = {n for _, n in W.bodies(box)} | set(RB_LOCKED)
    stray = sorted({c[1] for c in calls if c[0] == "put" and c[1] not in allowed})
    if stray:
        stop(f"{label}: the Update put {stray}, which is neither an app body nor a sprocket locked to one (§0.3)")
    check(True, f"{label}: every put the press made was an app body or a locked sprocket: "
                f"{sorted({c[1] for c in calls if c[0] == 'put'})}")
    check(not result.user_in_error and not result.user_features_in_error,
          f"{label}: nothing of the user's in error after: {result.user_in_error} "
          f"{[f.name for f in result.user_features_in_error]}")
    check(all(c in desk.note[0] for c in ("Sprocket-1", "Sprocket-2")),
          f"{label}: the Update's sentence names the sprockets it put with their gears")
    entry = box.user_work
    check(entry is not None and {(c.component, c.gear) for c in entry.carried} == want
          and list(entry.revision) == list(W.TAG["revision"])
          and any(f.name == "User Keyway" and store.same_path(f.path, sun_part(box)) for f in entry.features),
          f"{label}: the record's inventory holds the carried sprockets, the keyway in Sun's part and revision "
          f"{list(entry.revision) if entry else None}, read at {entry.read_at if entry else None}")
    ahead_of(desk, f"{label}, after the press")
    entities_after = entities_of(f"{label}, after", desk, folder)
    check(entities_after == entities_before, f"{label}: every user mate joins what it joined before the press (§0.3): "
          f"{ {n: (entities_before.get(n), v) for n, v in entities_after.items() if entities_before.get(n) != v} or 'the same'}")
    every = read_every(f"{label}, after", box.assembly, pairs_of(box, rb_users()), list(box.modes))
    go_judge(label, desk, every, rel_orig, flags_set, out, dz_set)
    feats = feature_list(sun_part(box))
    key = [f for f in feats if f[0] == "User Keyway"]
    check(bool(key) and not key[0][2], f"{label}: the user's keyway rebuilt in Sun's part after the app's features, code "
                                       f"{key[0][2] if key else None}")
    return result


def go_turn(label, desk, mode):
    """The user's turn in ``mode`` (W8 s7's drive): Sun's turn from the drive job's own reads, both made with ``mode``
    shown; each locked sprocket's pose on its gear from reads in ``mode`` before and after."""
    box = desk.record.gearbox
    sun = box.drag[0]
    plane, _ = W.drive_assumptions(desk, sun, label)
    built_sun = W.wanted(desk)[sun]
    pairs = pairs_of(box, rb_users())
    folder = os.path.dirname(box.assembly)

    def show(s):
        s.show_configuration(mode)
        return bool(s.rebuild(kind=swcom.ASSEMBLY_TRAIN))
    run(f"{mode} shown", job(box.assembly, show))
    before = read_now(f"before {label}", box.assembly, folder, pairs, list(box.modes))
    got = run(label, W.s7_drive_job(box, mode, TURN, plane, built_sun), 600)
    after = read_now(f"after {label}", box.assembly, folder, pairs, list(box.modes))
    turned = (W.turn_degrees(got["before"][sun][0], got["after"][sun][0])
              if "before" in got and "after" in got else None)
    carried = rel_gaps(rel_of(after["frames"], RB_LOCKED), rel_of(before["frames"], RB_LOCKED))
    check(before["active"] == after["active"] == mode and not got["errors"] and not got["cleanup"]
          and turned is not None and abs(turned - TURN) <= 1e-6 * TURN and all(v <= TOL for v in carried.values()),
          f"{label}: the user's turn in {mode}: {sun} turned {turned}° and each locked sprocket went with its gear "
          f"{fmt(carried)}")


def section_go(out):
    say("== go  W9a's Done when: on a copy of S0's master with the user's work, a value Update and a slide-offset "
        "Update go ahead; the sprockets found on their gears; every user mate on where it was, in no error; the keyway "
        "rebuilt; the footer's line and the record before and after")
    folder, path, book, desk = copy_desk(user_master(), "go", "RangeBox.xlsx")
    try:
        box = desk.record.gearbox
        modes = list(box.modes)
        users_in_copy("go", desk, folder, rb_users())
        check(desk.record.gearbox.user_work is not None, "go: the record holds setup's inventory")
        every = read_every("go, as copied", box.assembly, pairs_of(box, rb_users()), modes)
        rel_orig = rel_of(every["frames"][modes[0]], RB_LOCKED)
        flags_set = {n: f for n, f in every["by_mode"].items() if n in RB_USER_MATES}
        check(all(not any(f.values()) for f in flags_set.values()) and set(flags_set) == set(RB_USER_MATES),
              f"go: the user's 8 mates on in every mode as set up: {sorted(flags_set)}")
        dz_set = {m: float(every["frames"][m]["Sprocket-4"][1][2]) - float(every["frames"][m]["Sprocket-3"][1][2])
                  for m in modes}
        check(all(abs(abs(v) - abs(dz_set[modes[0]])) <= TOL for v in dz_set.values()),
              f"go: Sprocket-4 stands the same distance from Sprocket-3 in every mode as copied: {dz_set}")
        go_judge("go as copied", desk, every, rel_orig, flags_set, out, dz_set)
        go_turn("the user's turn +37° in H", desk, modes[0])
        out["value"] = bool(go_press("go value Update (Sun's Backlash 0.4)", desk, folder, book,
                                     [("Gears", W.cell(book, "Gears", "Backlash", "Sun"), 0.4)], out, rel_orig, flags_set,
                                     dz_set))
        live = run("Sun's globals", lambda s: W.live_globals(s, sun_part(desk.record.gearbox)))
        check(abs(float(live.get(spur.BACKLASH, 0.0)) - 0.4) < 1e-9, f"go: Sun's Backlash reads {live.get(spur.BACKLASH)}")
        go_turn("the user's turn +37° in L", desk, modes[-1])
        out["slide"] = bool(go_press("go slide-offset Update (RangeSlv L=+5.5)", desk, folder, book,
                                     [("Gears", W.cell(book, "Gears", "Slides", "RangeSlv"), "H=-5, N=0, L=+5.5")],
                                     out, rel_orig, flags_set, dz_set))
    finally:
        w8_step(W.end_copy, CTX["worker"], folder, "go")


# -- refuse ----------------------------------------------------------------------------------------------------------


def refuse_press(label, desk, folder, kinds, mates_named=(), text=(), ahead=None, users=None, part=None,
                 save=True):
    """The user saves, every user item and document read, Update pressed: it must refuse before any write with
    ``kinds`` among its problems, naming ``mates_named`` and saying ``text``. Judged by the press's own traced calls
    (W8 s3's ``nothing_changed_calls``: no show, flag, value, rebuild, put or mate made), then read again: frames,
    mates' codes, flags and entities, and ``part``'s globals (Sun's by default) as before; a document marked by the
    refused press is a STOP (§0.3). ``ahead``: the footer's prediction before the press, held against the refusal.
    ``save`` False: pressed on the assembly as it stands, unsaved (an assembly holding a lightweight component is never
    saved: with SOLIDWORKS CAM loaded the save raises a modal Yes/No box, found at 9dded70)."""
    if save:
        save_user(folder, f"before {label}")
    else:
        say(f"person  {label}: nothing saved first; the press reads the assembly as it stands in the session")
    box = desk.record.gearbox
    pairs = pairs_of(box, rb_users() if users is None else users)
    mates = RB_USER_MATES if users is None else ()
    before = read_now(f"before {label}", box.assembly, folder, pairs, list(box.modes), entities=mates)
    blind = W.marked(before["flags_after"])
    if blind:
        # A document already marked before the press: its mark check cannot see the press mark it again. What is
        # still compared for it: frames, mates' codes, flags and entities, and the part's globals.
        say(f"fact    {label}: already marked before the press, so the check of a new mark is blind for {blind}; "
            "frames, mates, flags, entities and the part's globals are still compared")
    sun = part or sun_part(box)
    globals_before = run("the part's globals", lambda s: W.live_globals(s, sun))
    result, calls = press(desk, label)
    error = desk.error
    problems = list(getattr(error, "problems", ()) or ())
    say(f"fact    {label}: problems {[(p.kind, list(p.mates)) for p in problems]}")
    for p in problems:
        say(f"        {p.kind}: {p.sentence}")
    changing = W.nothing_changed_calls(calls)
    after = read_now(f"after {label}", box.assembly, folder, pairs, list(box.modes), entities=mates)
    globals_after = run("the part's globals", lambda s: W.live_globals(s, sun))
    marked = sorted(n for n, v in after["flags_after"].items() if v and not before["flags_after"].get(n))
    if marked:
        stop(f"{label}: the refused press left {marked} marked modified (§0.3: a read W9 adds marking a document)")
    diff = written(before, after) + ([f"the part's globals {globals_before} -> {globals_after}"]
                                     if globals_after != globals_before else [])
    got = {p.kind for p in problems}
    named = {m for p in problems for m in p.mates}
    said = " ".join(p.sentence for p in problems)
    check(result is None and isinstance(error, swbuild.UserWorkRefused) and set(kinds) <= got
          and set(mates_named) <= named and all(t in said for t in text),
          f"{label}: refused before any write as {sorted(kinds)}, naming {sorted(mates_named)} and saying {list(text)}: "
          f"got {sorted(got)}, named {sorted(named)}")
    check(not changing, f"{label}: the refused press made no call that changes or shows anything (its trace): "
                        f"{changing or 'none'}")
    check(not diff, f"{label}: nothing written: {diff or 'frames, mates, flags, entities, marks and globals as before'}")
    entry = desk.record.gearbox.user_work
    check(entry is not None and {p.kind for p in entry.problems} == got,
          f"{label}: the record keeps the refusal with its time {entry.read_at if entry else None}: "
          f"{[p.kind for p in entry.problems] if entry else None}")
    f = ahead_of(desk, f"{label}, after the refusal")
    if f is not None:
        check(bool(f.refused) and not f.changed_since and not ui_text.user_work_line(f)[1],
              f"{label}: the footer says the refusal as recorded, red, until the workbook changes")
    if ahead is not None:
        foreseen = {p.kind for p in ahead.problems}
        foreseen_mates = {m for p in ahead.problems for m in p.mates}
        check(foreseen == got and foreseen_mates == named,
              f"{label}: what the footer foresaw before the press is what the press refused: foreseen "
              f"{sorted(foreseen)} {sorted(foreseen_mates)}, refused {sorted(got)} {sorted(named)}")
    return problems


def mates_job(desk, changes):
    """The user, in SolidWorks: mates made (``("add", handle, kind, a, b, value, name)``), or suppressed / turned on
    in every mode (``("off"|"on", name)``); read back."""
    box = desk.record.gearbox
    modes = list(box.modes)
    refs = dict(rb_refs(box), u1="Sprocket-1", u4="Sprocket-4", uh="Housing-1")
    want = {change[-1]: change[0] == "off" for change in changes}

    def work(s):
        out = {"status": {}, "flags": {}}
        for handle, name in refs.items():
            s.find_component(handle, name, lightweight_ok=handle.startswith("u"))
        for change in changes:
            if change[0] == "add":
                _, handle, kind, a, b, value, name = change
                kept, _ = (s.add_mate(handle, "lock", a, b, name=name) if kind == "lock"
                           else s.add_mate(handle, kind, a, b, value, name))
                s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
                s.set_mate_suppressed_in(handle, False, modes)
                out["status"][kept] = s.mate_status(kept)
            else:
                verb, name = change
                s.find_mate(f"mj{name}", name)
                s.set_mate_suppressed_in(f"mj{name}", verb == "off", modes)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        for name in want:
            s.find_mate(f"mr{name}", name)
            out["flags"][name] = s.mate_suppression(f"mr{name}", modes)
        out["states"] = {m.name: (m.code, m.suppressed) for m in s.mate_states() if m.name in want}
        return out
    got = run(f"the user's mates {changes}", job(box.assembly, work))
    say(f"person  {changes}: AddMate5 status {got['status']}; flags {got['flags']}; codes here {got['states']}")
    wrong = {n: f for n, f in got["flags"].items() if any(v != want[n] for v in f.values())}
    if wrong:
        stop(f"a mate the user set did not read back as set in every mode: {wrong} (§0.3)")
    check(True, f"the user's mates read back as set in every mode: {sorted(want)}")
    return got


def set_state(desk, name, state):
    """The user sets a component lightweight (1) or resolved (2) in the active configuration (``SetSuppression2``);
    read back."""
    box = desk.record.gearbox

    def work(s):
        route = findings.COMPONENT_FIND_ROUTE
        comp = swcom.Session._component_by(route, s._doc(), name)  # noqa: SLF001
        call(comp, "SetSuppression2", state)
        comp = swcom.Session._component_by(route, s._doc(), name)  # noqa: SLF001
        return int(swcom._read(comp, "GetSuppression2"))  # noqa: SLF001
    got = run(f"{name} state {state}", job(box.assembly, work))
    say(f"person  {name} set to state {state}: reads {got}")
    return got


def quiet_then_edit(label, desk, book, backlash):
    """The workbook put back as recorded, a quiet press (the inventory read again and recorded), then Sun's Backlash
    typed: the footer's prediction from what the record now holds."""
    ref = W.cell(book, "Gears", "Backlash", "Sun")
    if desk.update is not None and not desk.update.record_matches:
        W.edit(desk, book, ("Gears", ref, None))
    result, _ = press(desk, f"{label}: the quiet press")
    check(result is not None and result.placed == [] and result.changed == [],
          f"{label}: the quiet press read the user's work and changed nothing: {desk.error if result is None else 'ok'}")
    W.edit(desk, book, ("Gears", ref, backlash))
    return ahead_of(desk, f"{label}, before the press")


def refuse_step(out, name, steps):
    """One refusal step under its own net: a failed check or a raise of the script's own is said and the next step
    runs; a STOP or a lost session ends as everywhere."""
    say(f"-- refuse  {name}")
    try:
        steps()
    except RUN_ENDERS + (SectionStop,):
        raise
    except Exception as exc:  # noqa: BLE001 - one step's surprise must not take the rest
        check(False, f"refuse {name}: {type(exc).__name__}: {exc}")
        for line in traceback.format_exc().splitlines()[-6:]:
            say("        " + line)
        out.setdefault("steps_failed", []).append(name)


def section_refuse(out):
    say("== refuse  W9a's Done when: a lock to a fixed housing refuses naming it, a Bore Diameter typed in SolidWorks "
        "refuses naming the cell; with them a mate of another kind on Sun, the solver's tie, two app bodies locked "
        "together, and all at once; each foreseen or recorded in the footer, each writing nothing (the lightweight "
        "carried sprocket is its own section, lightweight)")
    folder, path, book, desk = copy_desk(user_master(), "refuse", "RangeBox.xlsx")
    says = out.setdefault("problems", {})
    backlash = W.cell(book, "Gears", "Backlash", "Sun")
    cell = "Gears!" + W.cell(book, "Gears", "Bore", "Sun")
    try:
        box = desk.record.gearbox
        users_in_copy("refuse", desk, folder, rb_users())

        def housing():
            mates_job(desk, [("add", "uhl", "lock", "uh", "u1", 0.0, "UserHousingLock")])
            ahead = quiet_then_edit("refuse housing lock", desk, book, 0.4)
            says["housing lock"] = [p.sentence for p in refuse_press(
                "refuse housing lock", desk, folder, {swbuild.PROBLEM_TIE}, ("UserHousingLock",), ("Housing-1",),
                ahead=ahead)]
            # Ruling 5 on package B's review: once the workbook changes, the recorded refusal is said with "has changed
            # since" and the prediction runs again on the inventory as last read, which still holds the lock: red.
            W.edit(desk, book, ("Gears", backlash, 0.41))
            a = ahead_of(desk, "refuse, the workbook changed since the refusal")
            line, ok = ui_text.user_work_line(a)
            ties = [p for p in (a.problems if a is not None else ()) if p.kind == swbuild.PROBLEM_TIE]
            check(a is not None and "has changed since" in line and not ok and len(a.problems) == 1 and len(ties) == 1
                  and "UserHousingLock" in ties[0].mates and "Housing-1" in ties[0].sentence,
                  f"refuse: once the workbook changed, the footer says the refusal \"has changed since\" and foresees "
                  f"the same refusal, red, naming the lock: ok {ok}; foreseen "
                  f"{[(p.kind, list(p.mates)) for p in (a.problems if a else ())]}")
        refuse_step(out, "a user lock from Sprocket-1 to the fixed Housing-1", housing)

        def other():
            mates_job(desk, [("off", "UserHousingLock"),
                             ("add", "uo", "coincident", "u4:Gear Axis", "sun:Gear Axis", 0.0, "UserOnSun")])
            says["other kind"] = [p.sentence for p in refuse_press(
                "refuse other kind", desk, folder, {swbuild.PROBLEM_OTHER_KIND}, ("UserOnSun",), ("UserOnSun",))]
            mates_job(desk, [("off", "UserOnSun")])
        refuse_step(out, "a mate of another kind on Sun: Sprocket-4's axis on Sun's own axis", other)

        def tie():
            mates_job(desk, [("off", "UserHousingLock"),
                             ("add", "ut", "coincident", "u1:plane2", "uh:plane2", 0.0, "UserTie")])
            says["tie"] = [p.sentence for p in refuse_press(
                "refuse tie read", desk, folder, {swbuild.PROBLEM_TIE}, ("UserTie",), ("unable to turn",))]
        refuse_step(out, "the solver's tie: Sprocket-1's Top plane on Housing-1's", tie)

        def two():
            mates_job(desk, [("off", "UserTie"), ("add", "u2b", "lock", "sun", "slv", 0.0, "UserTwoBodies")])
            says["two bodies"] = [p.sentence for p in refuse_press(
                "refuse two bodies", desk, folder, {swbuild.PROBLEM_TWO_BODIES}, ("UserTwoBodies",))]
        refuse_step(out, "two app bodies locked together: a user lock from Sun to RangeSlv", two)

        def bore():
            mates_job(desk, [("off", "UserTwoBodies")])
            run("Sun's bore 12", job(sun_part(box), lambda s: (s.set_global_variable(spur.BORE, "12"),
                                                               bool(s.rebuild()))))
            # W9A-RUN-2026-REVIEW finding 6: at 9dded70 SolidWorks updated the assembly after the person's save
            # ("Component(s) have been modified"), so the assembly was marked before the press and its mark check was
            # blind. The assembly is rebuilt first, as the person would, so the save leaves every document clean.
            run("the assembly rebuilt after Sun's change", job(box.assembly, lambda s: bool(
                s.rebuild(kind=swcom.ASSEMBLY_TRAIN))))
            problems = refuse_press("refuse bore typed", desk, folder, {swbuild.PROBLEM_VALUE}, (), (cell,))
            says["bore"] = [p.sentence for p in problems]
            values = [v for p in problems for v in p.values]
            check(any(v.name == spur.BORE and v.cell == cell and float(v.live) == 12.0 for v in values),
                  f"refuse bore typed: the value named with its cell {cell}: "
                  f"{[(v.name, v.live, v.wanted, v.cell) for v in values]}")
        refuse_step(out, "a Bore Diameter typed in SolidWorks: Sun's Bore Diameter 12", bore)

        def together():
            mates_job(desk, [("on", "UserHousingLock"), ("on", "UserTwoBodies")])
            # One cluster then holds Sun, RangeSlv and the housing: judge_user_work refuses it as two bodies (naming
            # both locks) and reads no ground for it; whether the solver's tie is read and said beside it is logged.
            problems = refuse_press("refuse all at once", desk, folder,
                                    {swbuild.PROBLEM_VALUE, swbuild.PROBLEM_TWO_BODIES},
                                    ("UserHousingLock", "UserTwoBodies"), (cell,))
            says["all"] = [p.sentence for p in problems]
            check(bool(problems) and problems[0].kind == swbuild.PROBLEM_VALUE,
                  f"refuse all at once: every problem in one press, the values first: {[p.kind for p in problems]}")
            mates_job(desk, [("off", "UserHousingLock"), ("off", "UserTwoBodies")])
            run("Sun's bore back to 0", job(sun_part(box), lambda s: (s.set_global_variable(spur.BORE, "0"),
                                                                       bool(s.rebuild()))))
        refuse_step(out, "all at once: the housing lock and the two-body lock on again, the bore still 12", together)

    finally:
        w8_step(W.end_copy, CTX["worker"], folder, "refuse")


def section_lightweight(out):
    say("== lightweight  a carried user component loaded lightweight refuses (W9A-REVIEW-B 3; the coordinator's item "
        "4): on a copy of setup.master, Sprocket-1 set lightweight, a quiet press records it from the live session, "
        "the footer foresees the refusal, and the press refuses, all on the assembly as it stands, never saved while "
        "a component is lightweight (SOLIDWORKS CAM's modal box under SaveAs3, found at 9dded70); Sprocket-1 resolved "
        "again before anything is saved or closed")
    folder, path, book, desk = copy_desk(user_master(), "lightweight", "RangeBox.xlsx")
    light = []
    try:
        users_in_copy("lightweight", desk, folder, rb_users())
        out["states_before"] = raw_states(desk, "before the set")
        state = set_state(desk, "Sprocket-1", 1)
        out["state"] = state
        after_set = out["states_after_set"] = raw_states(desk, "after Sprocket-1 alone was set lightweight")
        light = [n for n, v in after_set.items() if v in (1, 4)]
        say(f"fact    lightweight: SetSuppression2(1) on Sprocket-1 alone; SolidWorks then reports lightweight, by the "
            f"script's own GetSuppression2, {light} (the same member the app reads, so this shows the app reads what "
            "SolidWorks reports, not that SolidWorks made each instance so: W9A-CLOSE-2026-REVIEW finding 8)")
        if "Sprocket-1" not in light:
            raise AssertionError(f"lightweight: Sprocket-1 did not read lightweight after SetSuppression2(1): {state}")
        ahead = quiet_then_edit("lightweight", desk, book, 0.4)
        entry = desk.record.gearbox.user_work
        say(f"fact    lightweight: the app's inventory reads the states { {c.name: c.state for c in entry.components} }"
            if entry is not None else "fact    lightweight: no inventory on record")
        check(ahead is not None and any(p.kind == swbuild.PROBLEM_COMPONENT for p in ahead.problems),
              "lightweight: the footer foresees the refusal of a carried component loaded lightweight")
        problems = refuse_press("lightweight", desk, folder, {swbuild.PROBLEM_COMPONENT}, (), ("Sprocket-1",),
                                ahead=ahead, save=False)
        out["problems"] = [p.sentence for p in problems]
        named = {c for c in RB_LOCKED if any(re.search(rf"\b{re.escape(c)}\b", p.sentence) for p in problems
                                               if p.kind == swbuild.PROBLEM_COMPONENT)}
        expected = {c for c in RB_LOCKED if c in light}
        check(named == expected, f"lightweight: the refusal names exactly the carried instances the raw read shows "
                                 f"lightweight: named {sorted(named)}, lightweight and carried {sorted(expected)}")
    finally:
        reset = None if W.HUNG["on"] else True
        # Sprocket-1 first, alone, then every instance read: whether resolving one is reported as resolving the others
        # (W9A-CLOSE-2026-REVIEW finding 8); then whatever still reads lightweight, one by one.
        order = sorted(light, key=lambda n: n != "Sprocket-1")
        for index, name in enumerate(order if not W.HUNG["on"] else []):
            try:
                if index > 0 and out.get("states_after_first_reset", {}).get(name) not in (1, 4):
                    continue
                back = set_state(desk, name, 2)
                check(back in (2, 3), f"lightweight: {name} resolved again before anything is saved or closed: {back}")
                if index == 0:
                    first = out["states_after_first_reset"] = raw_states(desk, f"after {name} alone was set back to 2")
                    still = [n for n in light if n != name and first.get(n) in (1, 4)]
                    say(f"fact    lightweight: with {name} alone set back to resolved, SolidWorks reports "
                        f"{'still lightweight ' + str(still) if still else 'every other instance resolved too'}")
            except Exception as exc:  # noqa: BLE001 - said; the copy is then closed unsaved on every version
                check(False, f"lightweight: {name} could not be resolved again: {type(exc).__name__}: {exc}")
                reset = False
        if reset is not None:
            try:
                left = raw_states(desk, "after the reset")
                out["states_after_reset"] = left
                if any(v in (1, 4) for v in left.values()):
                    reset = False
            except Exception as exc:  # noqa: BLE001
                say(f"fact    lightweight: the states after the reset were not read: {exc}")
                reset = False
            # Saved before the close only on 2024 (W8's end_clean), and only once nothing reads lightweight.
            w8_step(W.end_copy, CTX["worker"], folder, "lightweight", save=bool(reset))


def raw_states(desk, when):
    """Each user component's ``GetSuppression2``, read by the script's own raw call, nothing set."""
    box = desk.record.gearbox

    def work(s):
        route = findings.COMPONENT_FIND_ROUTE
        out = {}
        for name in rb_users():
            comp = swcom.Session._component_by(route, s._doc(), name)  # noqa: SLF001
            out[name] = None if comp is None else int(swcom._read(comp, "GetSuppression2"))  # noqa: SLF001
        return out
    got = run(f"states {when}", job(box.assembly, work))
    say(f"fact    lightweight: GetSuppression2 {when}: {got}")
    return got


# -- again: the Build again… job's read of the old assembly ------------------------------------------------------------


def stamps_of(paths):
    return {os.path.basename(p): os.path.getmtime(p) for p in paths if os.path.exists(p)}


def old_changes(before, after, mine):
    """What differs on the old assembly between two reads made without activating it: frames, mate codes, flags and
    entities, its active configuration, its rebuild state, its own save flag and the user's files' marks."""
    changes = written(before, after, marks_of=mine)
    flips = {n: (before["flags_after"].get(n), after["flags_after"].get(n)) for n in mine
             if before["flags_after"].get(n) != after["flags_after"].get(n)}
    if flips:
        changes.append(f"save flags {flips}")
    if after["needs_rebuild"] != before["needs_rebuild"]:
        changes.append(f"rebuild state {before['needs_rebuild']} -> {after['needs_rebuild']}")
    return changes


def local_clock(stamp):
    """A record's UTC stamp (``store.now()``) as the local clock reads it, *HH:MM*, and its local date: what any way
    of saying the time read must hold (the app adds the date on another day: ``ui_text.read_time``)."""
    then = time.localtime(calendar.timegm(time.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")))
    return time.strftime("%H:%M", then), time.strftime("%Y-%m-%d", then)


STAYS_CLAUSE = re.compile(r"\b[Yy]our\s+((?:(?!\.\s)[^;])+?)\s+stays?\s+in\s+([^\s,;]+?)(?=[\s,;]|\.(?:\s|$)|$)")
READ_AT = re.compile(r"\bread at (\d{1,2}:\d{2})(?: on (\d{4}-\d{2}-\d{2}))?")


def stays_clauses(text):
    """Each clause of ``text`` that says what of the user's stays somewhere — *your A, B, 2 other components and 8
    mates stay in RangeBox.SLDASM* — as (the place, its items), the items split at commas and "and"."""
    out = []
    for m in STAYS_CLAUSE.finditer(text or ""):
        items = [t.strip() for t in re.split(r",\s*(?:and\s+)?|\s+and\s+", m.group(1)) if t.strip()]
        out.append((m.group(2), items))
    return out


def stays_said(label, text, components, mates, features, old, stamp=None, since=True):
    """That ``text`` says what of the user's stays behind, held to the clauses that say it (W9A-CLOSE-2026-REVIEW
    finding 6), without pinning the app's wording otherwise (package B names the first components and counts the
    rest, names one mate and counts more):

    - in the clause that says what stays in ``old`` (the old assembly's file name): every component an item by its
      whole name, or covered by an item "N other component(s)" that adds up, and nothing named that is not one; the
      mates an item by name (one) or "N mates" (more);
    - in the clause that says what stays in each feature's part (its file stem): each feature an item by its whole
      name (so "User Keyway" is not found inside "User Keyway Sketch");
    - with ``stamp``, a "read at HH:MM" of the inventory's local time (and its date, if a date is said);
    - with ``since``, "nor anything added since"."""
    text = text or ""
    clauses = stays_clauses(text)
    components = list(dict.fromkeys(components))
    in_old = [items for place, items in clauses if place.lower() == old.lower()]
    items = in_old[0] if len(in_old) == 1 else []
    named = [c for c in components if c in items]
    others = sum(int(m.group(1)) for t in items for m in [re.fullmatch(r"(\d+) other components?", t)] if m)
    strays = [t for t in items if t not in components and t not in mates
              and not re.fullmatch(r"\d+ (?:other )?(?:components?|mates?)", t)]
    comps_ok = (not components and not in_old) or (len(in_old) == 1 and len(named) + others == len(components)
                                                   and bool(named) and not strays)
    if not mates:
        mates_ok = True
    elif len(mates) == 1:
        mates_ok = mates[0] in items
    else:
        mates_ok = f"{len(mates)} mates" in items
    by_stem = {}
    for f in features:
        by_stem.setdefault(os.path.splitext(os.path.basename(f[1]))[0].lower(), []).append(f[0])
    feats_missing = []
    for stem, names in by_stem.items():
        said = [i for place, i in clauses if place.lower() == stem]
        for n in names:
            if len(said) != 1 or n not in said[0]:
                feats_missing.append((n, stem))
    time_ok, when = True, None
    if stamp:
        clock, day = local_clock(stamp)
        reads = READ_AT.findall(text)
        time_ok = bool(reads) and all(t.zfill(5) == clock and (not d or d == day) for t, d in reads)
        when = f"{clock} ({day})"
    since_ok = not since or "nor anything added since" in text
    check(comps_ok and mates_ok and not feats_missing and time_ok and since_ok,
          f"{label}: says what stays behind: in {old} {len(in_old)} clause(s), components {len(components)}, named "
          f"{named} and {others} counted, not one of them {strays or 'none'}; mates {len(mates)} "
          f"{'said' if mates_ok else 'NOT said'}; features not said beside their part {feats_missing or 'none'}; the "
          f"time read {when or 'not asked'} {'said' if time_ok else 'NOT said'}; \"nor anything added since\" "
          f"{'said' if since_ok else 'NOT said'}")
    return comps_ok and mates_ok and not feats_missing and time_ok and since_ok


def section_again(out, variant="open"):
    name = {"open": "again", "dirty": "again-dirty", "closed": "again-closed"}[variant]
    say(f"== {name}  Build again… (Sun's Part name changed): the question names what stays behind with its time; the "
        f"build job reads the old assembly first, which is "
        + {"open": "open in the session, behind another document",
           "dirty": "open, behind another document, and needs a rebuild", "closed": "closed"}[variant])
    folder, path, book, desk = copy_desk(user_master(), name, "RangeBox.xlsx")
    try:
        box = desk.record.gearbox
        old, modes = box.assembly, list(box.modes)
        entry = box.user_work
        check(entry is not None and bool(entry), f"{name}: the record holds the inventory, read at "
                                                 f"{entry.read_at if entry else None}")
        W.edit(desk, book, ("Gears", W.cell(book, "Gears", "Part name", "Sun"), SUN_PART_NAME))
        u, plan = desk.update, desk.plan
        check(u is not None and u.needs_new_revision and plan is not None and not plan.refusal and plan.revision == 2,
              f"{name}: classify sends it to Build again… as RangeBox_r2: structural {u and list(u.structural)}")
        stays = wb_update.stays_behind(desk.record, plan)
        question = ui_text.build_again_question(u, plan, record=desk.record)
        say(f"question {question}")
        check(stays is not None and stays.entry is not None and set(rb_users()) <= set(stays.components)
              and set(RB_USER_MATES) <= set(stays.mates) and any(f == "User Keyway" for f, _, _ in stays.left),
              f"{name}: what stays behind, from the record: components {stays and list(stays.components)}, mates "
              f"{stays and len(stays.mates)}, features left {stays and [(f, os.path.basename(p)) for f, p, _ in stays.left]}")
        if stays is not None:
            stays_said(f"{name}: the question", question, stays.components, stays.mates, stays.left,
                       os.path.basename(old), stamp=entry.read_at)
        f = desk.say_footer(f"{name}, before the build")
        check(f.build_enabled and f.build_action == ui_text.BUILD_AGAIN,
              f"{name}: the footer offers Build again… ({f.build_label!r}, enabled {f.build_enabled})")
        user_files = [old, sun_part(box), os.path.join(folder, "Sprocket.SLDPRT"), os.path.join(folder, "Housing.SLDPRT")]
        mine = {os.path.basename(p) for p in user_files}
        times = stamps_of(user_files)
        pairs = pairs_of(box, rb_users())
        if variant == "closed":
            left = run("close", W.quit_in(folder))
            check(not left, f"{name}: the old assembly closed before the build: left {left}")
        else:
            run(f"{name}: the old assembly opened", job(old, lambda s: s.active_configuration()))
            if variant == "dirty":
                def dirty(s):
                    # The user's edit, not rebuilt: UserDist4 0.5 mm longer in the active mode, one configuration per
                    # call as the app sets a distance (set_dimension_in; m3's first run read 0 in the modes not set
                    # when it was given every mode at once: findings.VALUE_UNSET_READS_ZERO), from the value read.
                    active = s.active_configuration()
                    s.find_mate("ud4", "UserDist4")
                    was = s.dimension_values("ud4", [active])[active]
                    s.set_dimension_in("ud4", was + 0.5, [active])
                    return active, was
                active, was = run(f"{name}: UserDist4 changed, no rebuild", job(old, dirty))
                say(f"person  {name}: UserDist4 {was:.6f} -> {was + 0.5:.6f} mm in {active}, not rebuilt")
            housing = os.path.join(folder, "Housing.SLDPRT")
            front = run(f"{name}: another document brought forward",
                        job(housing, lambda s: os.path.basename((s.active_document() or swcom.DocInfo("", "", 0)).path)))
            check(front == "Housing.SLDPRT", f"{name}: Housing.SLDPRT is the front document, the old assembly behind "
                                             f"it: {front}")
            before = read_now(f"{name} the old assembly before its read", old, folder, pairs, modes, activate=False,
                              entities=RB_USER_MATES)
            out["before"] = {k: v for k, v in before.items() if k != "frames"}
            if variant == "dirty":
                needs = before["needs_rebuild"]
                check(isinstance(needs, int) and needs != 0, f"{name}: the old assembly needs a rebuild before its read "
                                                             f"(NeedsRebuild2 {needs})")

            say(f"-- {name}  the app's own swbuild.read_old_assembly, alone, the old assembly behind Housing.SLDPRT")
            windows = S0.sw_windows()
            old_spec = wb_update.old_assembly(desk.record, plan)
            alone = run(f"{name}: read_old_assembly alone", lambda s: swbuild.read_old_assembly(s, old_spec))
            new, counted = windows_new(windows)
            watch_check(f"{name}: read_old_assembly alone")
            if counted:
                stop(f"{name}: a window came up while the app read the old assembly: {counted} (§0.3: any dialog)")
            after = read_now(f"{name} the old assembly after its read", old, folder, pairs, modes, activate=False,
                             entities=RB_USER_MATES)
            out["read_alone"] = None if alone is None else {
                "components": [c.name for c in alone.components], "mates": [m.name for m in alone.mates]}
            check(alone is not None and {c.name for c in alone.components} == set(rb_users())
                  and set(RB_USER_MATES) <= {m.name for m in alone.mates},
                  f"{name}: the app's read found the user's work in the old assembly behind another document: "
                  f"{out['read_alone']}")
            changes = old_changes(before, after, mine)
            if after["active_doc"] != before["active_doc"]:
                changes.append(f"the front document {before['active_doc']} -> {after['active_doc']} (the old assembly "
                               "brought forward)")
            if changes:
                section_stop(f"{name}: the app's read of the old assembly changed it: {changes} (W9A-REVIEW-B 6)")
            check(True, f"{name}: the read left the old assembly behind ({after['active_doc']} in front), unrebuilt "
                        f"(rebuild state {after['needs_rebuild']}), its save flag, active configuration "
                        f"({after['active']}), mates' codes, flags and entities and components' frames as before; no "
                        "window")
            before = after

        say(f"-- {name}  the build, as the window runs it")
        windows = S0.sw_windows()
        _, result = desk.build()
        new, counted = windows_new(windows)
        watch_check(f"{name} build")
        if counted:
            stop(f"{name}: a window came up during the Build again…: {counted} (§0.3: any dialog)")
        if result is None:
            raise AssertionError(f"{name}: the build refused: {desk.error}")
        check(result.ok and desk.record.gearbox.revision == 2, f"{name}: RangeBox_r2 built: ok {result.ok}")
        work, why = getattr(result, "old_user_work", None), getattr(result, "old_read", "")
        out["old_read"], out["old_user_work"] = why, None if work is None else {
            "components": [c.name for c in work.components], "mates": [m.name for m in work.mates]}
        if variant == "closed":
            check(work is None and why == swbuild.OLD_NOT_OPEN,
                  f"{name}: the old assembly not open, so not read: old_user_work {out['old_user_work']}, old_read "
                  f"{why!r}")
            say(f"status  ({name}, after the build) {desk.note[0]}")
            if stays is not None:
                stays_said(f"{name}: the result's sentence gives the record's inventory", desk.note[0],
                           stays.components, stays.mates, stays.left, os.path.basename(old), stamp=entry.read_at)
            still = run("open names", W.open_names)
            check(os.path.basename(old) not in still, f"{name}: the build did not open the old assembly")
        else:
            check(work is not None and not why and {c.name for c in work.components} == set(rb_users())
                  and set(RB_USER_MATES) <= {m.name for m in work.mates},
                  f"{name}: the build job read the old assembly first: {out['old_user_work']}")
            say(f"status  ({name}, after the build) {desk.note[0]}")
            if work is not None:
                # What the build read is said as read when it began (no time); the features left in a part made new
                # come from the record, with its time and "nor anything added since".
                stays_said(f"{name}: the result's sentence lists what stayed behind, as the build read it",
                           desk.note[0], [c.name for c in work.components], [m.name for m in work.mates],
                           stays.left if stays is not None else (), os.path.basename(old),
                           stamp=entry.read_at if stays is not None and stays.left else None,
                           since=bool(stays is not None and stays.left))
            after = read_now(f"{name} the old assembly after the build", old, folder, pairs, modes, activate=False,
                             entities=RB_USER_MATES)
            say(f"fact    {name}: GetSaveFlag of the folder's documents before the build "
                f"{W.marked(before['flags_after']) or 'none'}, after {W.marked(after['flags_after']) or 'none'} (the "
                "new revision's and the shared parts' as facts; the old assembly's and the user's files judged)")
            changes = old_changes(before, after, mine)
            if changes:
                section_stop(f"{name}: the Build again… changed the old assembly: {changes} (W9A-REVIEW-B 6, §0.3)")
            check(True, f"{name}: after the build the old assembly's save flag, active configuration ({after['active']}),"
                        f" rebuild state, mates' codes, flags and entities and components' frames as before")
        moved = {n: (t, stamps_of(user_files).get(n)) for n, t in times.items() if stamps_of(user_files).get(n) != t}
        if moved:
            section_stop(f"{name}: a user document's file time changed during the Build again…: {moved} (§0.3, W9d's STOP)")
        check(True, f"{name}: no file time of the user's documents changed: {sorted(times)}")
        desk.say_footer(f"{name}, after the build")
    finally:
        w8_step(W.end_copy, CTX["worker"], folder, name)


# -- box, box-k3: SolidWorks 2024's What's Wrong box, measured --------------------------------------------------------
#
# The coordinator's measurement after 2024's m3 stopped at What's Wrong inside the app's own value Update
# (sw2024/w9a-confirm-sw2024-20261117-1-m3-stopped-by-whats-wrong.log; W9A-CLOSE-2026-REVIEW, "The 2024 fact and the
# options"). Run by name only, each as the last thing asked of a fresh session: the press is waited for under a watch
# that only LOGS a box; nothing sets a SolidWorks setting, answers or closes a box, or saves or closes anything once one
# has been seen. Every read here is the script's own raw call (W._RAW_CALL, so nothing it does moves W8's "call in
# progress"), on a second worker connected before the press, so the main worker's job is never waited behind.


def _win32():
    import win32con
    import win32gui
    import win32process
    return win32con, win32gui, win32process


def title_facts(title, document):
    """A SolidWorks window's title said without its text (it can hold the licence edition, which this repo keeps out
    of its logs; S0's P0 lists windows by class only): whether it has one, and whether it holds ``document``."""
    return {"title_present": bool(title), "title_has_document": bool(document) and document.lower() in (title or "").lower()}


def sw_frame(document=""):
    """SolidWorks' main frame: the largest visible unowned top-level window of its process, one whose title holds
    SOLIDWORKS first. ``{"hwnd", "class", "title_present", "title_has_document"}`` (never the title's text), or None."""
    win32con, win32gui, win32process = _win32()
    found = []

    def each(h, _):
        try:
            if (win32gui.IsWindowVisible(h) and win32process.GetWindowThreadProcessId(h)[1] == W.PID
                    and not win32gui.GetWindow(h, win32con.GW_OWNER)):
                left, top, right, bottom = win32gui.GetWindowRect(h)
                found.append(((right - left) * (bottom - top), h, win32gui.GetClassName(h), win32gui.GetWindowText(h)))
        except Exception:  # noqa: BLE001 - a window that went away while listed
            pass
        return True
    win32gui.EnumWindows(each, None)
    titled = [f for f in found if "SOLIDWORKS" in f[3].upper()]
    pick = max(titled or found, default=None)
    return None if pick is None else {"hwnd": pick[1], "class": pick[2], **title_facts(pick[3], document)}


def frame_enabled(frame):
    """``IsWindowEnabled`` on SolidWorks' frame (False: a modal box has disabled its owner); None unread."""
    if frame is None:
        return None
    _, win32gui, _ = _win32()
    try:
        return bool(win32gui.IsWindowEnabled(frame["hwnd"]))
    except Exception:  # noqa: BLE001
        return None


def window_facts(h, frame=None, document=""):
    """A box as Win32 reports it: class, its own title and texts (a box's are SolidWorks' words, not the frame's),
    style and extended style, its owner by class and title facts only (and whether that is SolidWorks' frame),
    visible, enabled."""
    win32con, win32gui, _ = _win32()
    out = {"hwnd": h}
    try:
        style = win32gui.GetWindowLong(h, win32con.GWL_STYLE) & 0xFFFFFFFF
        ex = win32gui.GetWindowLong(h, win32con.GWL_EXSTYLE) & 0xFFFFFFFF
        owner = win32gui.GetWindow(h, win32con.GW_OWNER)
        kind = win32gui.GetClassName(h)
        title = win32gui.GetWindowText(h)
        out.update({
            "class": kind, **({"title": title} if kind == "#32770" else title_facts(title, document)),
            "texts": list(S0.xlhelp.child_texts(h)[:10]), "style": hex(style), "exstyle": hex(ex),
            "popup": bool(style & win32con.WS_POPUP), "child": bool(style & win32con.WS_CHILD),
            "dlg_modal_frame": bool(ex & win32con.WS_EX_DLGMODALFRAME), "topmost": bool(ex & win32con.WS_EX_TOPMOST),
            "owner": owner, "owner_class": win32gui.GetClassName(owner) if owner else None,
            **({f"owner_{k}": v for k, v in title_facts(win32gui.GetWindowText(owner), document).items()}
               if owner else {}),
            "owner_is_frame": bool(frame) and owner == frame["hwnd"],
            "visible": bool(win32gui.IsWindowVisible(h)), "enabled": bool(win32gui.IsWindowEnabled(h))})
    except Exception as exc:  # noqa: BLE001 - a box that closed while read
        out["unread"] = f"{type(exc).__name__}: {exc}"
    return out


def box_windows(skip):
    """SolidWorks' visible top-level dialog boxes (#32770) not in ``skip``, none of the exempt kind: its progress
    boxes, its notification box, a box counting elapsed time, the open-progress box."""
    _, win32gui, win32process = _win32()
    found = []

    def each(h, _):
        try:
            if (h not in skip and win32gui.IsWindowVisible(h) and win32gui.GetClassName(h) == "#32770"
                    and win32process.GetWindowThreadProcessId(h)[1] == W.PID):
                title = win32gui.GetWindowText(h)
                texts = tuple(S0.xlhelp.child_texts(h)[:8])
                exempt = (title in W.PROGRESS or texts == W.NOTIFICATION_TEXTS
                          or any(t.startswith(("Elapsed time", "Opening Component")) for t in texts))
                if not exempt:
                    found.append(h)
        except Exception:  # noqa: BLE001
            pass
        return True
    win32gui.EnumWindows(each, None)
    return found


def visible_now(handles):
    _, win32gui, _ = _win32()
    out = []
    for h in handles:
        try:
            if win32gui.IsWindow(h) and win32gui.IsWindowVisible(h):
                out.append(h)
        except Exception:  # noqa: BLE001
            pass
    return out


def raw_open_names(s):
    """A harmless read by raw calls: the open documents' names (GetFirstDocument / GetNext)."""
    rc, out = W._RAW_CALL, []  # noqa: SLF001
    doc = rc(s._app, "GetFirstDocument")  # noqa: SLF001
    while doc is not None and len(out) < 200:
        path = str(rc(doc, "GetPathName") or "")
        out.append(os.path.basename(path) if path else str(rc(doc, "GetTitle")))
        doc = rc(doc, "GetNext")
    return out


def raw_written(folder, part, value_name):
    """A worker job of raw reads, nothing activated or set: the open documents; GetSaveFlag of each in ``folder``;
    ``value_name``'s equation and value in ``part`` (its Equation Manager, by index); and "show errors every rebuild"
    (toggle 77), read, never set."""
    def work(s):
        rc = W._RAW_CALL  # noqa: SLF001
        names, flags, value = [], {}, None
        doc = rc(s._app, "GetFirstDocument")  # noqa: SLF001
        while doc is not None and len(names) < 200:
            path = str(rc(doc, "GetPathName") or "")
            names.append(os.path.basename(path) if path else str(rc(doc, "GetTitle")))
            if path and W.under(path, folder):
                flags[os.path.basename(path)] = bool(rc(doc, "GetSaveFlag"))
            if path and store.same_path(path, part):
                manager = rc(doc, "GetEquationMgr")
                for i in range(int(rc(manager, "GetCount"))):
                    text = str(rc(manager, "Equation", i))
                    try:
                        name, _ = split_equation(text)
                    except ValueError:
                        continue
                    if name == value_name:
                        value = {"equation": text, "value": float(rc(manager, "Value", i))}
            doc = rc(doc, "GetNext")
        toggle = bool(rc(s._app, "GetUserPreferenceToggle", S0.SHOW_ERRORS_EVERY_REBUILD))  # noqa: SLF001
        return {"open": names, "flags": flags, value_name: value, "show_errors_every_rebuild": toggle}
    return work


def waited(worker, fn, timeout):
    """A raw job on ``worker``, waited for up to ``timeout`` s and never longer: {"answered", "seconds", "value" or
    "error"}; not answering leaves the worker alone."""
    began = time.monotonic()
    try:
        value, error = worker.submit(fn).wait(timeout=timeout)
    except queue.Empty:
        return {"answered": False, "seconds": round(time.monotonic() - began, 1)}
    out = {"answered": True, "seconds": round(time.monotonic() - began, 1)}
    if error is not None:
        out["error"] = f"{type(error).__name__}: {error}"
    else:
        out["value"] = value
    return out


def box_compare(tag, desk, pre, post, users, user_mates):
    """After a press that returned with no box up, against the same read before it, in the active mode, nothing
    shown: every app body at its frame on record; each user component's frame as before; each user mate's code and
    flags as before. Facts, said and returned."""
    box = desk.record.gearbox
    mode = post["active"] if box.modes else ""
    app_gap, app_at = W.frames_gap(post["frames"], W.mode_record_frames(desk, mode))
    user_gap, user_at = W.frames_gap({u: post["frames"][u] for u in users if u in post["frames"]},
                                     {u: pre["frames"][u] for u in users if u in pre["frames"]})
    codes = {n: (pre["mates"].get(n), post["mates"].get(n)) for n in user_mates}
    flags = {n: (pre["by_mode"].get(n), post["by_mode"].get(n)) for n in user_mates
             if pre["by_mode"].get(n) != post["by_mode"].get(n)}
    got = {"mode": mode, "app_bodies_gap_to_record": [app_gap, app_at], "user_components_moved": [user_gap, user_at],
           "user_mates_code_suppressed_before_after": codes, "user_mate_flags_changed": flags,
           "mates_in_error_after": post["errors"]}
    say(f"fact    {tag}: after the press, in {mode or 'its one configuration'}: the app bodies {app_gap:.1e} from their "
        f"frames on record (at {app_at or '-'}); the user's components moved {user_gap:.1e} (at {user_at or '-'}); "
        f"the user's mates (code, suppressed) before -> after {codes}; flags changed {flags or 'none'}; mates in error "
        f"{post['errors'] or 'none'}")
    return got


def box_press(out, tag, desk, folder, part, value_name, label, users=(), user_mates=()):
    """The press waited for under a watch that only logs (``BOX``), up to ``--box-wait`` s (1800 by default); the
    facts the coordinator asked for, recorded as read, with the job's progress sampled every 10 s so a slow job is
    told from a stuck one. Returns whether a box was seen (then SolidWorks is asked nothing that changes it, and
    nothing is closed or saved at the end: W.HUNG is set once the reads are done)."""
    facts = out["box"] = {"wait": BOX_WAIT}
    box = desk.record.gearbox
    asm, modes = box.assembly, list(box.modes)
    document = os.path.splitext(os.path.basename(asm))[0]
    pairs = pairs_of(box, list(users))
    pre = read_now(f"{tag} before the press", asm, folder, pairs, modes, entities=tuple(user_mates))
    side = swcom.Worker(W.connect_pid)
    CTX["side"] = side
    first = waited(side, lambda s: tuple(s.revision), 120)
    if not first["answered"] or "error" in first:
        raise AssertionError(f"{tag}: the second connection did not attach: {first}")
    frame = sw_frame(document)
    facts["frame"] = {k: v for k, v in (frame or {}).items() if k != "hwnd"} or None
    before = waited(side, raw_written(folder, part, value_name), 120)
    facts["before"] = before
    if not before["answered"] or "error" in before:
        raise AssertionError(f"{tag}: the raw read before the press did not answer: {before}")
    say(f"fact    {tag}: before the press, by raw reads on a second connection: {value_name} in "
        f"{os.path.basename(part)} {before['value'][value_name]}; save flags {before['value']['flags']}; "
        f"\"show errors every rebuild\" {before['value']['show_errors_every_rebuild']}; SolidWorks' frame "
        f"{facts['frame']} enabled {frame_enabled(frame)}; the press waited for up to {BOX_WAIT:g} s")
    skip = set(box_windows(set()))
    if skip:
        facts["boxes_before"] = [window_facts(h, frame, document) for h in skip]
        say(f"fact    {tag}: boxes already up before the press, left out of the watch: {facts['boxes_before']}")
    state = {"first": None, "more": [], "pending": None, "read": None, "handles": [], "returned": None,
             "last_seen": None, "gone": None, "progress": [], "sample": -10.0, "count": 0}

    def progress(elapsed):
        now, count, traced = W.CALLS["now"] or None, W.TRACE.get("count", 0), len(W.TRACE["calls"])
        state["count"] = count
        if elapsed - state["sample"] >= 10.0:
            state["sample"] = elapsed
            last = state["progress"][-1] if state["progress"] else None
            if last is None or (last[1], last[2]) != (now, count):
                state["progress"].append((round(elapsed, 1), now, count, traced))
                say(f"        {tag} +{elapsed:7.1f} s: in {now}; {count} calls, {traced} traced")
        return now, count, traced

    def tick(elapsed, returned):
        now, count, traced = progress(elapsed)
        if state["first"] is None:
            boxes = box_windows(skip)
            if boxes:
                calls = W.TRACE["calls"]
                state["handles"] = list(boxes)
                state["last_seen"] = round(elapsed, 2)
                state["first"] = {
                    "seconds": round(elapsed, 2), "call_in_progress": now, "calls_so_far": count,
                    "last_traced_call": list(calls[-1]) if calls else None, "traced_calls_so_far": traced,
                    "frame_enabled": frame_enabled(frame), "boxes": [window_facts(h, frame, document) for h in boxes]}
                say(f"fact    {tag}: a box came up {elapsed:.2f} s into the press, the worker in {now} (last traced "
                    f"{state['first']['last_traced_call']}, {count} calls, {traced} traced so far); SolidWorks' frame "
                    f"enabled {state['first']['frame_enabled']}; the box {state['first']['boxes']}")
                state["pending"] = (side.submit(raw_open_names), time.monotonic())
        else:
            if visible_now(state["handles"]):
                state["last_seen"] = round(elapsed, 2)
            elif state["gone"] is None:
                state["gone"] = {"seconds": round(elapsed, 2), "last_seen": state["last_seen"],
                                 "call_in_progress": now, "calls_so_far": count, "traced_so_far": traced,
                                 "frame_enabled": frame_enabled(frame)}
                say(f"fact    {tag}: the box was gone {elapsed:.2f} s into the press (last seen at {state['last_seen']} "
                    f"s), the worker then in {now}, {count} calls so far; nothing here closed it")
            more = box_windows(skip | set(state["handles"]))
            if more:
                state["handles"] += more
                seen_more = {"seconds": round(elapsed, 2), "call_in_progress": now, "calls_so_far": count,
                             "boxes": [window_facts(h, frame, document) for h in more]}
                state["more"].append(seen_more)
                say(f"fact    {tag}: another box came up {elapsed:.2f} s into the press, the worker in {now}: "
                    f"{seen_more['boxes']}")
        if state["pending"] is not None and state["read"] is None:
            pending, began = state["pending"]
            answer = pending.poll()
            if answer is not None:
                value, error = answer
                state["read"] = {"answered": True, "seconds": round(time.monotonic() - began, 2),
                                 **({"error": f"{type(error).__name__}: {error}"} if error is not None
                                    else {"open": value})}
                say(f"fact    {tag}: the harmless read (the open documents, a second connection) with the box up: "
                    f"{state['read']}")
            elif time.monotonic() - began > 20.0:
                state["read"] = {"answered": False, "waited": 20.0}
                say(f"fact    {tag}: the harmless read with the box up did not answer in 20 s; that connection is left "
                    "alone")
        if returned and state["returned"] is None:
            state["returned"] = {"seconds": round(elapsed, 2), "box_up": bool(visible_now(state["handles"])),
                                 "frame_enabled": frame_enabled(frame), "calls": count}

    fails_before, stops_before = len(W.FAILS), len(W.STOPS)
    BOX.update(on=True, tick=tick, timeout=BOX_WAIT)
    result, raised = None, None
    try:
        result, _ = press(desk, label)
    except W.WorkerHung as exc:
        raised = exc
    finally:
        BOX.update(on=True, tick=None)          # still on: a window logged during the reads below is not a STOP
    seen = state["first"] is not None
    facts["box_seen"] = state["first"]
    facts["more_boxes"] = state["more"]
    facts["box_last_seen"] = state["last_seen"]
    facts["box_gone"] = state["gone"]
    facts["read_with_box_up"] = state["read"]
    facts["returned"] = state["returned"]
    facts["progress"] = state["progress"]
    end_count = state["count"]
    facts["calls_grew"] = {
        "after_the_box_was_seen": None if not seen else end_count > state["first"]["calls_so_far"],
        "after_it_went": None if state["gone"] is None else end_count > state["gone"]["calls_so_far"],
        "calls_at_the_end": end_count}
    calls = W.TRACE["calls"]
    up = visible_now(state["handles"])
    facts["at_the_end"] = {"call_in_progress": W.CALLS["now"] or None,
                           "last_traced_call": list(calls[-1]) if calls else None,
                           "frame_enabled": frame_enabled(frame),
                           "boxes_up": [window_facts(h, frame, document) for h in up]}
    if raised is not None:
        facts["job"] = f"did not return in {BOX_WAIT:g} s ({raised}); the worker is left alone"
        say(f"fact    {tag}: the press did not return in {BOX_WAIT:g} s; the worker is left alone")
    else:
        facts["job"] = "returned"
        facts["result"] = _update_fact(desk, result)
        say(f"fact    {tag}: the press returned after {state['returned'] and state['returned']['seconds']} s, a box "
            f"{'up' if state['returned'] and state['returned']['box_up'] else 'not up'} when it did; ok "
            f"{result.ok if result is not None else None}; the status: {desk.note[0] if desk.note else None}")
    say(f"fact    {tag}: at the end, the worker in {facts['at_the_end']['call_in_progress']}; SolidWorks' frame "
        f"enabled {facts['at_the_end']['frame_enabled']}; boxes still up {len(up)}; calls grew after the box was "
        f"seen {facts['calls_grew']['after_the_box_was_seen']}, after it went {facts['calls_grew']['after_it_went']}")
    # What was written, read raw: on the main worker when its job returned (nothing else waits on it), else on the
    # second connection if its read with the box up answered; never by anything that sets, saves or closes.
    reader = CTX["worker"] if raised is None else (side if not seen or (state["read"] or {}).get("answered") else None)
    if reader is None:
        facts["after"] = {"answered": False, "why": "the press did not return and the second connection did not answer"}
    else:
        facts["after"] = waited(reader, raw_written(folder, part, value_name), 60)
        if not facts["after"]["answered"]:
            W.HUNG["on"] = True
    after = facts["after"].get("value")
    if after is not None:
        was = before["value"]
        facts["written"] = {
            value_name: {"before": was[value_name], "after": after[value_name]},
            "flags_changed": {n: (was["flags"].get(n), f) for n, f in after["flags"].items() if was["flags"].get(n) != f},
            "show_errors_every_rebuild": {"before": was["show_errors_every_rebuild"],
                                          "after": after["show_errors_every_rebuild"]}}
        say(f"fact    {tag}: written, raw reads before and after the press: {facts['written']}")
    else:
        say(f"fact    {tag}: what was written could not be read after the press: {facts['after']}")
    # Whether an Update that ran through the box did its work: the reads the other sections make, in the active mode
    # and nothing shown, only when the job returned and no box is up (else nothing is asked of the main worker).
    if raised is None and not up and not W.HUNG["on"]:
        try:
            post = read_now(f"{tag} after the press", asm, folder, pairs, modes, entities=tuple(user_mates))
            facts["after_reads"] = box_compare(tag, desk, pre, post, list(users), list(user_mates))
        except RUN_ENDERS:
            raise
        except Exception as exc:  # noqa: BLE001 - a fact
            facts["after_reads"] = f"unread: {type(exc).__name__}: {exc}"
            say(f"fact    {tag}: the reads after the press raised: {facts['after_reads']}")
    BOX.update(on=False, tick=None)
    if seen:
        W.HUNG["on"] = True          # nothing more is asked of the main worker, nothing closed or saved at the end
    # W8's own watch keeps its rule (a box during a configuration call is its FAIL and STOP); said here as what it
    # logged during the press, beside the facts.
    facts["w8_watch"] = {"fails_during_the_press": list(W.FAILS[fails_before:]), "stops": list(W.STOPS[stops_before:])}
    RESULT["proposal"][tag] = {"facts_only": True, **{k: facts.get(k) for k in (
        "wait", "box_seen", "more_boxes", "box_last_seen", "box_gone", "read_with_box_up", "returned", "job",
        "calls_grew", "at_the_end", "written", "after_reads")},
        "result_ok": (facts.get("result") or {}).get("ok"), "status": (facts.get("result") or {}).get("sentence")}
    say(f"propose {tag} (facts only, no finding's value): {RESULT['proposal'][tag]}")
    if raised is not None and not seen:
        raise raised                 # hung with no box seen: the run ends as for any hung worker, recorded as cut
    return seen


def section_box(out):
    say("== box  SolidWorks' What's Wrong box in the app's value Update with two user mates in error (2024's m3 STOP), "
        f"measured: m3's set-up to just before that Update, then the press waited for up to {BOX_WAIT:g} s under a watch "
        "that only logs; nothing set, answered, closed or saved once a box is seen. Run by name, last in a fresh session")
    folder, path, book, desk = copy_desk(rangebox_master(), "box", "RangeBox.xlsx")
    seen = False
    try:
        _, box, _, _ = m3_mate_in_error(out, "box", folder, desk)
        say("-- box  a quiet press records the inventory, Sun's Backlash 0.4 typed, then the press under the box watch")
        ahead = quiet_then_edit("box mate in error", desk, book, 0.4)
        line = ui_text.user_work_line(ahead)[0] if ahead is not None else ""
        say(f"fact    box: the footer before the press: {line}")
        seen = box_press(out, "box", desk, folder, sun_part(box), spur.BACKLASH,
                         "box: the app's value Update (Sun's Backlash 0.4) with the user's two mates in error",
                         users=("Sprocket-1", "Housing-1"), user_mates=("UserAxis", "UserFront", "UserGap"))
    finally:
        if not seen and not W.HUNG["on"]:
            w8_step(W.end_copy, CTX["worker"], folder, "box")
    if seen:
        raise BoxSeen("box: a box was seen during the press; SolidWorks is left as it stands, the box up or not, for "
                      "the coordinator to end the session")


def section_box_k3(out):
    say("== box-k3  the same watch around k3's Update on the 12 : 1 (the user's keyway rebuilt into error by G1's Bore "
        "8 -> 14): does a box come up, at which call, and does the job return. Run by name, last in a fresh session, "
        "after reducer")
    folder, path, book, desk = copy_desk(reducer_master(), "box-k3", "Reducer_12to1.xlsx")
    seen = False
    try:
        _, _, g1, _ = k3_keyway_and_bore("box-k3", desk, folder, book)
        seen = box_press(out, "box-k3", desk, folder, g1, spur.BORE,
                         "box-k3: the app's value Update (G1's Bore 14) rebuilding the user's keyway into error")
    finally:
        if not seen and not W.HUNG["on"]:
            w8_step(W.end_copy, CTX["worker"], folder, "box-k3")
    if seen:
        raise BoxSeen("box-k3: a box was seen during the press; SolidWorks is left as it stands for the coordinator "
                      "to end the session")


# -- the 12 : 1 and the no-carrier branch -----------------------------------------------------------------------------


def spec_reducer(folder=""):
    """The 12 : 1 fixture as the W4/W5 demonstrations build it, its Output folder blank (W6-PLAN §5's way, so a copy
    of the built folder stands on its own)."""
    made = wb_link.Link(W.FIXTURE_12).read().spec
    return dataclasses.replace(made, box=dataclasses.replace(made.box, output_folder=folder))


def section_reducer(out):
    say("== reducer  the 12 : 1 (G1 on S1 drives G2, G3 locked to G2 drives G4 on S3; no carrier) written by the app's "
        "write_new and built to turn through the app's own Build; kept as reducer.master")
    folder, path, book, desk = w8_step(W.write_fixture, CTX["worker"], CTX["excel"], "reducer", spec_reducer)
    try:
        w8_step(W.build_turning, CTX["worker"], desk, "reducer", 4)
    except (AssertionError, W.Halt):
        w8_step(W.end_copy, CTX["worker"], folder, "reducer")
        raise
    MASTER["reducer"] = w8_step(W.keep_master, CTX["worker"], folder, "reducer")
    if not MASTER["reducer"]:
        raise AssertionError("reducer: reducer.master was not kept")


def k3_keyway_and_bore(tag, desk, folder, book):
    """k3's set-up up to its press (shared with ``box-k3``): a user keyway in G1's part, saved; a quiet press lists it
    (M2 on the 12 : 1); G1's Bore 8 -> 14 typed; classify makes it an Update of G1's part; the footer says the keyway
    follows. Returns (settled M3 findings, the record's gearbox, G1's part, G1's component)."""
    settled, _ = m3_findings()
    box = desk.record.gearbox
    g1 = next(c.part for c in box.components if c.gear == "G1")
    g1_name = dict(W.bodies(box))["G1"]
    keyway(tag, g1)
    save_user(folder, "the user's keyway in G1's part")
    quiet, _ = press(desk, f"{tag} quiet press (the inventory recorded)")
    work = quiet.user_work if quiet is not None else None
    listed = [(f.name, os.path.basename(f.path), f.code) for f in (work.features if work else [])]
    check(any(f.name == "User Keyway" and store.same_path(f.path, g1) for f in (work.features if work else []))
          and all(n.startswith("User") for n, _, _ in listed),
          f"{tag}: M2 on the 12 : 1: the inventory lists the User Keyway in G1's part and nothing of the app's: {listed}")
    W.edit(desk, book, ("Gears", W.cell(book, "Gears", "Bore", "G1"), 14))
    u = desk.update
    check(u is not None and not u.needs_new_revision and any("G1" in p.gear_ids for p in u.changed_parts),
          f"{tag}: classify makes G1's bore an Update of G1's part: structural {u and list(u.structural)}")
    ahead = ahead_of(desk, f"{tag}, G1 Bore 14, before the press")
    check(ahead is not None and any(f.name == "User Keyway" for f in ahead.followed),
          f"{tag}: the footer says the user's keyway follows the app's features in G1's part: "
          f"{[f.name for f in ahead.followed] if ahead else None}")
    return settled, box, g1, g1_name


def section_k3(out):
    say("== k3  K3 and M3 in an app part (review point 6): on the 12 : 1, a user keyway in G1's part, then G1's Bore "
        "8 -> 14 in the workbook, so an ordinary value Update rebuilds the user's feature into error (S0's P0 failure, "
        "reached through the app). Does the Update's part rebuild report it, does the job go on, is the keyway named as "
        "the user's; a window here ends this section only")
    folder, path, book, desk = copy_desk(reducer_master(), "k3", "Reducer_12to1.xlsx")
    try:
        settled, box, g1, g1_name = k3_keyway_and_bore("k3", desk, folder, book)
        windows = S0.sw_windows()
        result, calls = press(desk, "k3 Update rebuilding the user's keyway into error")
        new, counted = windows_new(windows)
        seen = watch_windows()
        if counted or seen:
            section_stop(f"k3: a window came up during the Update that rebuilt the user's keyway into error: "
                         f"{counted or seen} (§0.3: any dialog; this section only, the coordinator's ruling 3)")
        out["update"] = _update_fact(desk, result)
        out["update"]["whats_wrong"] = whats_wrong_showed("k3 Update rebuilding the user's keyway into error",
                                                          "feature")
        if result is None:
            raise AssertionError(f"k3: the press refused: {desk.error}")
        feats = feature_list(g1)
        mine = [f for f in feats if f[0].startswith("User")]
        theirs = [f for f in feats if not f[0].startswith("User") and f[2]]
        say(f"answer  M3 (an app part's rebuild in the Update, only the user's feature in error): ok {result.ok}; "
            f"failures {result.failures}; user features in error "
            f"{[(f.name, os.path.basename(f.path), f.code) for f in result.user_features_in_error]}; the user's "
            f"features {mine}; the app's in error {theirs or 'none'}")
        check(any(f[0] == "User Keyway" and f[2] for f in mine) and not theirs,
              "k3: the bore change left only the user's keyway in error in G1's part")
        named = [f for f in result.user_features_in_error if f.name == "User Keyway" and store.same_path(f.path, g1)]
        check(bool(named), f"k3: the result lists the keyway among the user's features in error after the rebuild: "
                           f"{[f.name for f in result.user_features_in_error]}")
        # The sentence, not only the field (W9A-RUN-2026-REVIEW finding 9): the keyway named as the user's, newly in
        # error, and the Update gone ahead where this version's findings let it.
        expected = judge_user_error_update("k3 Update rebuilding the user's keyway into error", desk, result,
                                           "User Keyway", None, settled, "feature", before=False)
        components = run("k3: components", job(box.assembly, lambda s: [(c.name, c.code) for c in s.components()]))
        codes = dict(components)
        out["components"] = components
        say(f"fact    k3: component error codes after the Update: { {n: c for n, c in codes.items() if c} or 'none'}; "
            f"G1's component {g1_name} reads {codes.get(g1_name)} (a user's feature in error in its part, not counted "
            "against the app)")
        live = run("G1's globals", lambda s: W.live_globals(s, g1))
        check(abs(float(live.get(spur.BORE, 0.0)) - 14.0) < 1e-9, f"k3: G1's Bore Diameter reads {live.get(spur.BORE)}")
        frags = said_of(desk.note[0], "User Keyway")
        RESULT["proposal"]["M3_app_part"] = {"update_ok": result.ok, "expected_to_go_ahead": expected,
                                             "failures": [list(f) for f in result.failures],
                                             "named_in_result": bool(named), "named_in_sentence": frags,
                                             "g1_component_code": codes.get(g1_name),
                                             "laid_to_user_alone": getattr(result, "rebuild_from_user_alone", None)}
    finally:
        w8_step(W.end_copy, CTX["worker"], folder, "k3")


NC_LOCKED = {"Sprocket-1": "G1", "Sprocket-3": "G1", "Sprocket-2": "G4"}


def nc_read(label, desk, folder, rel_orig, rebuild=False):
    """The no-carrier train read (a rebuild first when asked): every gear at its frame on record, each locked
    sprocket on its gear as set up, no mate in error, every gear free to turn. Returns whether all held."""
    box = desk.record.gearbox
    pairs = pairs_of(box, list(NC_LOCKED))
    if rebuild:
        every = read_every(label, box.assembly, pairs, [])
        frames, status = every["frames"][""], every["status"][""]
        errors = {n: c for n, (c, sup) in every["mates"][""].items() if c and not sup}
    else:
        r = read_now(label, box.assembly, folder, pairs, [])
        frames, status, errors = r["frames"], r["status"], r["errors"]
    gap, at = W.frames_gap(frames, W.mode_record_frames(desk, ""))
    gaps = rel_gaps(rel_of(frames, NC_LOCKED), rel_orig)
    free = {g: v for g, v in status.items() if g in dict(W.bodies(box)) and v != findings.COMPONENT_UNDER_DEFINED}
    ok = gap <= TOL and all(v <= TOL for v in gaps.values()) and not errors and not free
    check(ok, f"nocarrier {label}: every gear at its frame on record ({gap:.1e} at {at or '-'}); each locked sprocket on "
              f"its gear as set up {fmt(gaps)}; mates in error {errors or 'none'}; every gear free {not free}")
    return ok, frames


def section_nocarrier(out):
    revision = tuple(W.TAG["revision"])
    year = swcom.release_year(int(revision[0]))
    finding = f"USER_MATE_PUT_NO_CARRIER_ON_{year}"
    say(f"== nocarrier  the coordinator's measurement: route (c1) on a train with no carrier, put with its gear mates "
        f"on as the app puts such trains: a lock to the driving G1, to the driven G4, and a chain; the app's refusal "
        f"with findings.{finding} {getattr(findings, finding, None)!r}, then the finding patched True for this "
        "measurement only")
    parts = user_parts()
    folder, path, book, desk = copy_desk(reducer_master(), "nocarrier", "Reducer_12to1.xlsx")
    held = {"clean": []}
    was = getattr(findings, finding, None)
    try:
        shutil.copy2(os.path.join(parts, "Sprocket.SLDPRT"), os.path.join(folder, "Sprocket.SLDPRT"))
        box = desk.record.gearbox
        names = dict(W.bodies(box))
        g4 = next(c for c in box.components if c.gear == "G4")
        x4, y4 = float(g4.at[0]), float(g4.at[1])
        axes = {s.shaft: s.axis_name for s in wb_layout.shaft_layouts(desk.a.spec)}
        inserts = (("u1", "Sprocket.SLDPRT", (0.0, 0.0, 30.0), "Sprocket-1"),
                   ("u2", "Sprocket.SLDPRT", (x4, y4, -30.0), "Sprocket-2"),
                   ("u3", "Sprocket.SLDPRT", (0.0, 0.0, 45.0), "Sprocket-3"))
        mates = (("ua1", "coincident", "u1:Gear Axis", f"lay:{axes['S1']}", 0.0, "UserAxis1", {}),
                 ("ul1", "lock", "g1", "u1", 0.0, "UserLock1", {}),
                 ("ua2", "coincident", "u2:Gear Axis", f"lay:{axes['S3']}", 0.0, "UserAxis2", {}),
                 ("ul2", "lock", "g4", "u2", 0.0, "UserLock2", {}),
                 ("ul3", "lock", "u1", "u3", 0.0, "UserLock3", {}))
        add_user_work("nocarrier", desk, folder, inserts, mates,
                      refs={"lay": box.layout_component, "g1": names["G1"], "g4": names["G4"]})
        save_user(folder, "the user's sprockets")
        r = read_now("as set up", box.assembly, folder, pairs_of(box, list(NC_LOCKED)), [])
        rel_orig = rel_of(r["frames"], NC_LOCKED)
        quiet, _ = press(desk, "nocarrier quiet press (the inventory recorded)")
        check(quiet is not None and quiet.placed == [] and desk.record.gearbox.user_work is not None,
              f"nocarrier: the quiet press read and recorded the user's work: {desk.error if quiet is None else 'ok'}")
        out["branches"] = swbuild.user_carry_branches(desk.update.motion, desk.update.placements)
        check(all(out["branches"].get(g) == swbuild.BRANCH_NO_CARRIER for g in ("G1", "G2", "G3", "G4")),
              f"nocarrier: the app labels every gear of the 12 : 1 the no-carrier branch: {out['branches']}")

        W.user_turn(CTX["worker"], desk, "nocarrier", TURN)
        save_user(folder, "after the user's turn")
        W.edit(desk, book, ("Gears", W.cell(book, "Gears", "At", "G4"), 30))
        ahead = ahead_of(desk, f"nocarrier, G4 At 30, findings.{finding} {was!r}")
        if was is not True:
            check(ahead is not None and {p.kind for p in ahead.problems} == {swbuild.PROBLEM_UNSETTLED},
                  "nocarrier: the footer foresees the app's default refusal")
            problems = refuse_like(desk, folder, "nocarrier default refusal", ahead,
                                   {"UserLock1", "UserLock2", "UserLock3"}, finding)
            out["default_refusal"] = [p.sentence for p in problems]
        setattr(findings, finding, True)
        say(f"PATCH   findings.{finding} = True in this process, for this measurement only (was {was!r})")
        desk.plan_solidworks()
        for step, (at, label) in enumerate(((30, "G4 At 27 -> 30"), (27, "G4 At 30 -> 27"))):
            if step:
                W.user_turn(CTX["worker"], desk, f"nocarrier, second turn", TURN)
                W.edit(desk, book, ("Gears", W.cell(book, "Gears", "At", "G4"), at))
            ahead = ahead_of(desk, f"nocarrier {label}, before the press (the finding patched)")
            result, calls = press(desk, f"nocarrier {label}")
            if result is None:
                check(False, f"nocarrier {label}: the press refused with the finding patched: {desk.error}")
                held["clean"].append(False)
                break
            done = {(c, g) for c, g, _ in result.carried}
            allowed = {n for _, n in W.bodies(desk.record.gearbox)} | set(NC_LOCKED)
            stray = sorted({c[1] for c in calls if c[0] == "put" and c[1] not in allowed})
            if stray:
                stop(f"nocarrier {label}: the Update put {stray}, neither an app body nor a locked sprocket (§0.3)")
            ok = result.ok and done == set(NC_LOCKED.items()) and not result.user_in_error
            check(ok, f"nocarrier {label}: the Update went ahead and put each locked sprocket with its gear, its gear "
                      f"mates on: ok {result.ok}, carried {result.carried}, placed {result.placed}, failures "
                      f"{result.failures}")
            if ahead is not None and ahead.refused:
                say(f"fact    nocarrier {label}: the footer said the recorded refusal (the press before, with the "
                    "finding None), so it foresaw no carry; the press reads again")
            else:
                check(done == predicted_carry(ahead), f"nocarrier {label}: what the footer said is what the press "
                                                      f"carried: said {sorted(predicted_carry(ahead))}")
            r1, _ = nc_read(f"after {label}", desk, folder, rel_orig)
            r2, _ = nc_read(f"after {label} and a further rebuild", desk, folder, rel_orig, rebuild=True)
            held["clean"].append(ok and r1 and r2)
        out["clean"] = held["clean"]
    finally:
        setattr(findings, finding, was)
        say(f"PATCH   findings.{finding} back to {was!r}")
        w8_step(W.end_copy, CTX["worker"], folder, "nocarrier")
        clean = len(held["clean"]) == 2 and all(held["clean"])
        RESULT["proposal"][finding] = True if clean else None
        RESULT["proposal"][f"{finding}_evidence"] = {"presses_clean": held["clean"],
                                                     "shapes": "A: lock to the driving G1; B: lock to the driven G4; "
                                                               "E: Sprocket-3 locked to Sprocket-1 (a chain)"}
        say(f"propose {finding}: {RESULT['proposal'][finding]!r} (both presses and their reads clean: {held['clean']})")


def refuse_like(desk, folder, label, ahead, locks, finding):
    """refuse_press on the 12 : 1 (its sprockets, G1's part's globals)."""
    part = next(c.part for c in desk.record.gearbox.components if c.gear == "G1")
    return refuse_press(label, desk, folder, {swbuild.PROBLEM_UNSETTLED}, tuple(sorted(locks)), (finding,),
                        ahead=ahead, users=list(NC_LOCKED), part=part)


# -- main ------------------------------------------------------------------------------------------------------------


SECTIONS = {"m3": section_m3, "setup": section_setup, "m1": section_m1, "go": section_go, "refuse": section_refuse,
            "lightweight": section_lightweight,
            "again": lambda out: section_again(out, "open"), "again-dirty": lambda out: section_again(out, "dirty"),
            "again-closed": lambda out: section_again(out, "closed"), "reducer": section_reducer, "k3": section_k3,
            "nocarrier": section_nocarrier,
            # Run by name only, never in ORDER or CONFIRM: SolidWorks 2024's What's Wrong box measured.
            "box": section_box, "box-k3": section_box_k3}


def main():
    os.makedirs(OUT, exist_ok=True)
    started = time.strftime("%Y%m%d-%H%M%S")
    json_path = os.path.join(os.path.dirname(os.path.abspath(W.LOG_PATH)), f"{JSON_STEM}-{started}.json")

    def write_json():
        RESULT["fails"], RESULT["notes"] = list(W.FAILS), list(W.NOTES)
        with open(json_path, "w", encoding="utf-8") as handle:
            json.dump(RESULT, handle, indent=1, default=str)

    say(f"awake   {S0.keep_awake(True)}")
    say(f"run     {time.strftime('%Y-%m-%d %H:%M:%S')}; {RUN_TITLE} from {W.SRC}{W.snapshot()}; sections "
        f"{CHOSEN}; masters {MASTER}; redo {REDO}")
    recent = store.recent_path()
    if not (APPDATA_HERE and W.under(recent, OUT)):
        say(f"STOP    the app's Recent list would be written outside this run's folder ({recent}), so nothing runs")
        return 2
    check(True, f"the app's settings and Recent list go into this run's folder, not the user's: {recent}")
    unknown = [n for n in CHOSEN if n not in SECTIONS]
    if unknown:
        say(f"STOP    no such section {unknown}; there are {list(SECTIONS)}")
        return 2
    worker = swcom.Worker(W.connect_pid)
    CTX["worker"] = W.CURRENT["worker"] = worker
    label, pid, revision = W.run(worker, lambda s: (s.label, s.pid, s.revision), 120)
    W.TAG.update(major=revision[0], version=".".join(str(v) for v in revision), revision=tuple(revision))
    RESULT.update(revision=list(revision), snapshot=W.snapshot().strip(" ()").replace("snapshot: ", ""))
    say(f"attach  {label} (revision {W.TAG['version']}), PID {pid}; {W.memory()}")
    if pid != PID:
        say(f"STOP    attached to PID {pid}, not {PID}")
        worker.shutdown()
        return 2
    before = W.run(worker, W.open_titles, 120)
    say(f"open    before: {before}")
    say(f"findings USER_MATE_PUT_ROUTE {getattr(findings, 'USER_MATE_PUT_ROUTE', None)!r}, USER_TIE_RULE "
        f"{getattr(findings, 'USER_TIE_RULE', None)!r}, WHATS_WRONG_OPENS_ON_PART_REBUILD "
        f"{getattr(findings, 'WHATS_WRONG_OPENS_ON_PART_REBUILD', None)!r}, the branches "
        f"{ {n: getattr(findings, n, None) for n in dir(findings) if n.startswith('USER_MATE_PUT_') and '_ON_' in n} }")
    whats_wrong_rule()
    W.STARTUP_BOXES = _WhatsWrongTolerated(W.STARTUP_BOXES)   # read by W8's watch at each window, by its module name
    watch = W.DialogWatch()
    watch.start()
    try:
        try:
            CTX["excel"] = S0.xlhelp.Excel(visible=True)
            say(f"excel   started our own Excel, PID {CTX['excel'].pid}, {CTX['excel'].version}")
            for name in CHOSEN:
                guard(f"before {name}")
                out = RESULT["sections"].setdefault(name, {})
                fails = len(W.FAILS)
                began = time.monotonic()
                try:
                    held = done_here(name)
                    if held and not REDO:
                        say(f"skip    {name}: this <out> holds it already ({[os.path.basename(p) for p in held]}); "
                            "--redo runs it again")
                        out["skipped"] = True
                    else:
                        for p in held:
                            aside = f"{p}.prev-{started}"
                            os.rename(p, aside)
                            say(f"redo    {name}: {os.path.basename(p)} set aside as {os.path.basename(aside)}")
                            for key, kept in MASTER.items():
                                if kept and os.path.normcase(os.path.abspath(kept)) == os.path.normcase(os.path.abspath(p)):
                                    MASTER[key] = ""
                        SECTIONS[name](out)
                except SectionStop as exc:
                    out["stop"] = str(exc)
                    say(f"STOP    the section {name} ends at its STOP: {exc}")
                except RUN_ENDERS as exc:
                    # Cut by a run-ender (W9A-RUN-2026-REVIEW finding 5): said in the section's record, not passed.
                    # A box section that saw its box ends the run by design: not a cut.
                    if not isinstance(exc, BoxSeen):
                        out["cut"] = f"{type(exc).__name__}: {exc}"
                    raise
                except Exception as exc:  # noqa: BLE001 - the script's own fault costs its section, not the run
                    check(False, f"{name}: {type(exc).__name__}: {exc}")
                    for line in traceback.format_exc().splitlines()[-8:]:
                        say("        " + line)
                finally:
                    # Up to a dialog, if one came up (W9A-RUN-2026-REVIEW: refuse's 1932 s at 9dded70 held 600 s of
                    # waiting behind SOLIDWORKS CAM's box); nothing after it is the section's work.
                    ended = SEEN.get("dialog_at") if (SEEN.get("dialog_at") or 0) > began else None
                    out["seconds"] = round((ended or time.monotonic()) - began)
                    if ended:
                        out["seconds_after_the_dialog_not_counted"] = round(time.monotonic() - ended)
                    out["failed"] = W.FAILS[fails:] + ([f"cut: {out['cut']}"] if out.get("cut") else [])
                    say(f"time    {name}: {out['seconds']} s; {len(out['failed'])} failed"
                        + (f"; CUT by {out['cut']} (the time is up to the cut)" if out.get("cut") else "")
                        + f"; {W.memory()}")
                    write_json()
                watch_check(name)
        except BoxSeen as exc:
            say(f"end     the run ends here by design: {exc}")
        except DemoStop as exc:
            say(f"STOP    the run ends at its STOP: {exc}")
        except (W.WorkerHung, swcom.NotRunning, W.Stopped, W.Halt) as exc:
            check(False, f"W9a: {type(exc).__name__}: {exc}; the run ends here, nothing more is asked of SolidWorks")
            RESULT["stops"].append(str(exc))
        except Exception as exc:  # noqa: BLE001
            check(False, f"W9a raised {type(exc).__name__}: {exc}")
            for line in traceback.format_exc().splitlines():
                say("        " + line)
    finally:
        write_json()
        try:
            books = W.close_books()
            if books:
                say(f"excel   left open: {books}, closed without saving")
            if CTX["excel"] is not None:
                CTX["excel"].quit()
                say("excel   quit our own Excel")
        except Exception as exc:  # noqa: BLE001
            say(f"excel   quit trouble: {exc}")
        if W.HUNG["on"]:
            say("close   the SolidWorks worker is hung: nothing closed at the end; SolidWorks is left as it is")
        else:
            try:
                left = w8_step(W.run, worker, W.close_ours, 600, _label="close_ours")
                after = W.run(worker, W.open_titles, 120)
                say(f"close   left of ours {left}; stray {[t for t in after if t not in before]}; lost "
                    f"{[t for t in before if t not in after]}; {W.memory()}")
            except Exception as exc:  # noqa: BLE001  (a session that is gone raises NotRunning)
                say(f"close   not closed: {type(exc).__name__}: {exc}")
        watch.stop.set()
        say(f"dialogs progress boxes seen {W.PROGRESS}; other windows the watch logged: {W.WINDOWS['count']}")
        try:
            worker.shutdown()
        except Exception as exc:  # noqa: BLE001
            say(f"close   worker: {exc}")
        write_json()
        say(f"awake   {S0.keep_awake(False)}")
        say(f"result  written to {json_path}; masters kept {MASTER}")
    for line in W.NOTES:
        say(f"noted   {line}")
    for line in W.STOPS:
        say(f"stop    {line}")
    say(f"done    {len(W.FAILS)} failed: {W.FAILS}; {len(W.NOTES)} noted; {len(RESULT['stops'])} STOP(s), a hung worker "
        f"included: {RESULT['stops']}")
    return 0 if not W.FAILS else 1


if __name__ == "__main__":
    code = 1
    try:
        code = main()
    finally:
        with open(W.LOG_PATH, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(W.LOG) + "\n")
    raise SystemExit(code)
