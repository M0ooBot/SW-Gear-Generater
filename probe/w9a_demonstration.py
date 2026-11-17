r"""W9a's demonstration on SolidWorks (ISSUE-1-PLAN §5, W9a's *Done when*; W9A-INTERFACES, W9A-PACKAGE-B, W9A-REVIEW-A
and W9A-REVIEW-B): the user's own components, mates and features in a built assembly, through the app's own Update and
Build again… as the Workbook window runs them. The sections, their order and times are in
``docs/notes-workbook/W9A-DEMONSTRATION.md``.

python.exe probe/w9a_demonstration.py <repo src> <output folder under C:\> --pid PID [--log FILE]
                                      [--sections m3,setup,go,...|all|confirm] [--master DIR]
                                      [--user-master DIR] [--reducer-master DIR]

``--master``: S0's kept ``rangebox.master`` for this SolidWorks version (``probe/w9_user_work_check.py`` built it);
without it a section that needs RangeBox builds it here first through S0's own ``build_master``.
``--user-master``: a ``setup.master`` an earlier run of this script kept (RangeBox with the user's work, its record
holding the inventory); without it, and with none in this run's folder, the section that needs it runs ``setup``
first. ``--reducer-master``: a ``reducer.master`` (the 12 : 1 built to turn) an earlier run kept; likewise.

It imports ``probe/workbook_assembly_check.py`` (W8's demonstration: the attach, the dialog watch, the log, Excel, the
fixtures written and built through the app's own Build, ``keep_master`` / ``copy_built`` / ``end_copy``, the drive
and the user's turn) and ``probe/w9_user_work_check.py`` (S0: the user's parts, the relative pose, the window list,
the request to stay awake). Nothing in either is changed. The Workbook window's own W9a path (``_plan_solidworks_pass``
with ``classify(..., read_sidecar=...)``, ``press_update`` with the session's revision and ``_record_refusal``,
``_start_build`` with ``before=`` and ``_finish_build`` with the stayed-behind sentence) is played by ``Desk9``, W8's
``Desk`` with those calls as the window now makes them; every Update and Build is the app's own
``swbuild.update_gearbox`` / ``build_gearbox``, never a re-implementation.

Sections (each runs alone by name; each copy section starts from a kept master and ends with its copy closed):

- ``m3``      ISSUE-1-PLAN §4 M3, first, under the dialog watch: a copy of RangeBox with a user sprocket and housing; an
              assembly rebuild with a user mate in error, and the app's value Update with it; then a user feature in
              error (in the user's own part) and the same. Any window is a STOP.
- ``setup``   RangeBox with the user's work (Sprocket-1 on Input Axis locked to Sun, Sprocket-2 on Output Axis locked
              to RangeSlv, Sprocket-3 locked to Sprocket-1, Sprocket-4 on Input Axis held by a distance to Sprocket-3
              and an angle to the layout, Housing-1 fixed, a keyway in Sun's part), saved in place as a person would;
              closed and reopened; M1's and M2's reads by the app's own calls with GetSaveFlag around them; a quiet
              Update that records the inventory (the footer before and after); the pure judgement shown refusing the
              branches not measured; kept as ``setup.master``.
- ``m1``      a copy of setup.master: a user gear mate and a distance mate suppressed in the active mode but on in the
              others, read by ``mate_info`` and by a quiet Update's inventory.
- ``go``      a copy of setup.master: the user's turn in H, a value Update (Sun's Backlash) and, after a turn in L, a
              slide-offset Update (RangeSlv L=+5.5): before each, the footer's prediction; after, every mode shown:
              each app body at its frame on record, each locked sprocket at its pose on its gear, every user mate on
              in the modes it was on in and in no error, the keyway rebuilt, the record's inventory and revision; the
              prediction against what the press did.
- ``refuse``  a copy of setup.master: Sprocket-1 lightweight (refused, foreseen), a lock to the fixed Housing-1
              (refused naming it, foreseen, then green once the workbook changes), the solver's tie, two app bodies
              locked together, a Bore Diameter typed in SolidWorks (refused naming the cell), and all at once; each
              press checked to have written nothing.
- ``again``, ``again-dirty``, ``again-closed``  a copy of setup.master, Sun's Part name changed so Build again…:
              the question names what stays behind with its time; the build job's read of the old assembly open (and,
              in ``again-dirty``, open and needing a rebuild): its save flag, active configuration, rebuild state,
              mates' flags and codes and components' frames before and after, and no dialog (a change is a STOP of
              the section); once more with it closed.
- ``reducer`` the 12 : 1 written by the app's write_new and built to turn, kept as ``reducer.master``.
- ``nocarrier`` a copy of reducer.master: the no-carrier branch of route (c1), the coordinator's measurement. Sprockets
              locked to G1 (driving), to G4 (driven) and one to the other (a chain); the user's turn; G4 At 27 -> 30:
              the app's default refusal with ``findings.USER_MATE_PUT_NO_CARRIER_ON_<year>`` None (foreseen by the
              footer), then the finding patched True in this process only, the press, the reads; a further rebuild;
              a second turn and G4 At 30 -> 27; proposed from what was read.

``--sections confirm`` is SolidWorks 2024's confirming set: m3, setup, go, refuse, reducer, nocarrier.

Robustness (as S0's at d086705): Windows is asked to keep the display and system awake; the JSON is written after
every section and first in the ``finally``; any exception around the close is caught; the head logs SolidWorks'
revision and the snapshot; a document of the user's is ``<user document N>`` (W8's ``open_titles``). A STOP of the
plan's §0.3 or §4 ends the run; a change to the old assembly in an ``again`` section ends that section only (the
coordinator's ruling, W9A-REVIEW-B). Under 2 GB of free memory, on any version, the run stops before the next section.
"""

import copy as _copy
import dataclasses
import json
import os
import shutil
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import workbook_assembly_check as W  # noqa: E402  (parses <src> <out> --pid PID [--log FILE])
import w9_user_work_check as S0  # noqa: E402  (its own options are absent here and so at their defaults)

from gear_generator import findings, store, swbuild, swcom, ui_text  # noqa: E402
from gear_generator.gears import spur  # noqa: E402
from gear_generator.swcom import call  # noqa: E402
from gear_generator.workbook import gearbox as wb_gearbox  # noqa: E402
from gear_generator.workbook import layout as wb_layout  # noqa: E402
from gear_generator.workbook import link as wb_link  # noqa: E402
from gear_generator.workbook import update as wb_update  # noqa: E402
from gear_generator.workbook_gui import _had_assembly, _update_gate  # noqa: E402  (the window's own helpers)

say, check, note = W.say, W.check, W.note
OUT, PID = W.OUT, W.PID
ARGS = sys.argv


def _arg(name):
    return ARGS[ARGS.index(name) + 1] if name in ARGS else ""


ORDER = ["m3", "setup", "m1", "go", "refuse", "again", "again-dirty", "again-closed", "reducer", "nocarrier"]
CONFIRM = ["m3", "setup", "go", "refuse", "reducer", "nocarrier"]
_given = _arg("--sections")
CHOSEN = (ORDER if _given in ("", "all") else CONFIRM if _given == "confirm"
          else [s.strip() for s in _given.split(",") if s.strip()])
MASTER = {"rangebox": _arg("--master"), "setup": _arg("--user-master"), "reducer": _arg("--reducer-master")}

TOL = 1e-6                 # rotation entries and origin coordinates (mm), as S0
SAME = 1e-9                # a read twice of what nothing moved
TURN = 37.0
IDENTITY = S0.IDENTITY
SUN_PART_NAME = "SunGear"  # the again sections' Part name for Sun: its file must change, so Build again…

# RangeBox's user work (setup), each inserted at an identity frame at these places (mm); Name2 by insert order.
RB_INSERTS = (("u1", "Sprocket.SLDPRT", (0.0, 0.0, 30.0), "Sprocket-1"),
              ("u2", "Sprocket.SLDPRT", (0.0, 0.0, -70.0), "Sprocket-2"),
              ("u3", "Sprocket.SLDPRT", (0.0, 0.0, 40.0), "Sprocket-3"),
              ("u4", "Sprocket.SLDPRT", (0.0, 0.0, 80.0), "Sprocket-4"),
              ("uh", "Housing.SLDPRT", (0.0, 0.0, 60.0), "Housing-1"))
RB_LOCKED = {"Sprocket-1": "Sun", "Sprocket-3": "Sun", "Sprocket-2": "RangeSlv"}   # each locked sprocket's gear
RB_GAP = 40.0              # Sprocket-4's Front plane from Sprocket-3's (UserDist4)

RESULT = {"sections": {}, "stops": [], "proposal": {}}
CTX = {"worker": None, "excel": None, "parts": ""}


class DemoStop(Exception):
    """A STOP of ISSUE-1-PLAN §0.3 or §4: the run ends there, what was read kept."""


class SectionStop(Exception):
    """A STOP that ends its section only (a change to the old assembly during a Build again…, W9A-REVIEW-B)."""


def stop(what):
    W.stop_check(False, what)
    RESULT["stops"].append(what)
    raise DemoStop(what)


def section_stop(what):
    W.stop_check(False, what)
    RESULT["stops"].append(f"(section) {what}")
    raise SectionStop(what)


def watch_check(where):
    """Plan §0.3, any dialog: a window W8's watch logged, or a STOP its helpers raised, ends the run. SolidWorks'
    notification box and its balloon tips are not dialogs (the coordinator's ruling)."""
    windows = [n for n in W.NOTES if n.startswith("a SolidWorks window")]
    if windows or W.STOPS:
        stop(f"{where}: {windows or W.STOPS}")


def guard(where):
    W.guard()
    free = W.free_gb()
    if free < 2.0:
        stop(f"{where}: {W.memory()}: under 2 GB of free memory (HANDOFF, Rules carried over)")


def run(what, fn, timeout=900):
    """A worker job; a raise other than a hung worker or a STOP fails the section with its sentence."""
    try:
        return W.run(CTX["worker"], fn, timeout)
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


class Desk9(W.Desk):
    """W8's Desk with the calls the Workbook window makes since W9a (``workbook_gui``): ``classify`` given the
    sidecar reader; Update with the session's revision for the record, a ``UserWorkRefused`` kept in the record
    (``_record_refusal``); a Build again… that reads the old assembly first (``before=``) and says what stayed behind."""

    def __init__(self, path, worker, strip=""):
        super().__init__(path, worker, strip)
        self.revision = ()
        self.before = None

    def plan_solidworks(self):
        """``WorkbookWindow._plan_solidworks_pass`` inside ``store.one_pass()``; the record is this workbook's."""
        with store.one_pass():
            newer = False
            try:
                record, problem = store.read_link_record(self.path), ""
            except store.UnknownSchema as exc:
                record, problem, newer = None, str(exc), True
            except store.StoreError as exc:
                record, problem = None, str(exc)
            if record is not None:
                store.clear_saved(record)
            self.record, self.record_problem = record, problem
            self.plan = self.update = None
            a = self.a
            if a is None or newer:
                return
            gearbox = record.gearbox if record is not None else None
            has_assembly = gearbox is not None and bool(gearbox.assembly)
            parts_only = not has_assembly and bool(a.parts.refused or a.turned_refusal())
            gate = a.build_refusal() if parts_only else a.lay_out_refusal()
            if not gate:
                self.plan = wb_gearbox.plan_gearbox(a, record, parts_only=parts_only)
            if record is not None and (record.parts or gearbox is not None) and not _update_gate(a, record):
                self.update = wb_update.classify(record, a, read_sidecar=store.read_sidecar)

    def update_solidworks(self):
        """``press_update`` (the session's revision taken in the job, as ``Job.revision``) and ``_collect_job``:
        ``_finish_update`` with that revision, or ``job_failed`` and, for a refusal over the user's work,
        ``_record_refusal``."""
        update = self.update
        steps, held = [], {"revision": ()}
        kwargs = update.update_kwargs()

        def work(s):
            held["revision"] = tuple(getattr(s, "revision", ()) or ())
            return swbuild.update_gearbox(s, **kwargs, progress=steps.append)
        started = time.monotonic()
        say(f"update  {W.memory()}")
        result, self.error = W.wait_job(self.worker.submit(work), 2400, "Update SolidWorks")
        self.revision = held["revision"]
        seconds = time.monotonic() - started
        if self.error is not None:
            say(f"        raised {type(self.error).__name__} in {seconds:.1f} s: {self.error}")
            self.note = (ui_text.job_failed(self.error, True), False)
            say(f"status  [red] {self.note[0]}")
            if isinstance(self.error, swbuild.UserWorkRefused):
                self._record_refusal(update, self.error)
            self.plan_solidworks()
            return update, None, None
        self.positions_per_configuration = getattr(result, "positions_per_configuration", None)
        for line in result.log_lines():
            say("        " + line)
        say(f"        in {seconds:.1f} s; {W.memory()}; loaded from disk {[os.path.basename(p) for p in result.opened]}")
        say(f"        W9a: carried {result.carried}; renamed {result.renamed}; user in error {result.user_in_error}; "
            f"user features in error {[(f.name, os.path.basename(f.path), f.code) for f in result.user_features_in_error]}"
            f"; inventory read {'yes' if result.user_work is not None else 'no'}")
        wrong = list(getattr(result, "sense_found_wrong", []) or [])
        check(not wrong, f"the Update's check phase found no gear mate turning against its mesh: {wrong}")
        record, may_write, notes = self._open_record()
        base = record if record is not None else self.record
        finished = wb_update.finish_update(update, result, base, digest=self.reading.digest, workbook=self.path,
                                           revision=self.revision)
        gearbox = self.record.gearbox if self.record is not None else None
        text, ok = ui_text.gearbox_update_status(update, result, finished.dragged,
                                                 meshes=gearbox.meshes if gearbox is not None else None,
                                                 finished=finished)
        faults = self._write(finished, may_write)
        if not may_write:
            faults, notes = notes + faults, []
        self.note = (" ".join([text] + notes + faults), ok and not faults)
        say(f"status  [{'green' if self.note[1] else 'red'}] {self.note[0]}")
        self.plan_solidworks()
        return update, result, finished

    def _record_refusal(self, update, error):
        """``WorkbookWindow._record_refusal``: the record keeps what the refused press read and every problem said."""
        try:
            record = store.open_link_record(self.path)
        except (store.StoreError, OSError) as exc:
            say(f"record  the refusal not kept: {exc}")
            return
        if record is None:
            return
        try:
            refused = wb_update.refused_update(record, update, error, digest=self.reading.digest,
                                               revision=self.revision)
            if refused.gearbox is not None and refused.gearbox.user_work != getattr(record.gearbox, "user_work", None):
                store.save_link_record(refused, store.link_record_path(self.path))
                say(f"record  the refusal kept with the inventory read ({len(error.problems)} problem(s))")
        except (store.StoreError, OSError) as exc:
            say(f"record  the refusal not kept: {exc}")

    def build(self, plan=None):
        """``_start_build`` (the old assembly given as ``before`` for a Build again…, its journal first) and
        ``_finish_build`` with the stayed-behind sentence."""
        plan = plan or self.plan
        before_record = self.record
        steps = self.steps = []
        kwargs = plan.build_kwargs()
        self.before = wb_update.old_assembly(self.record, plan)
        if self.before is not None:
            kwargs["before"] = self.before
        say(f"journal {'written' if self.write_journal(plan) else 'NOT written'}; the old assembly read first: "
            f"{os.path.basename(self.before.path) if self.before is not None else 'none'}")
        started = time.monotonic()
        result, self.error = W.wait_job(self.worker.submit(
            lambda s: swbuild.build_gearbox(s, **kwargs, progress=steps.append)), 2400, "the build")
        if self.error is not None:
            say(f"        raised {type(self.error).__name__}: {self.error}")
            self.note = (ui_text.job_failed(self.error, False), False)
            say(f"status  [red] {self.note[0]}")
            self.plan_solidworks()
            return plan, None
        for line in result.log_lines():
            say("        " + line)
        work = getattr(result, "old_user_work", None)
        say(f"        in {time.monotonic() - started:.1f} s; {W.memory()}; old read {getattr(result, 'old_read', '')!r}; "
            f"old user work {None if work is None else ([c.name for c in work.components], [m.name for m in work.mates])}")
        text, ok = ui_text.gearbox_status(plan, result, again=_had_assembly(before_record))
        if self.before is not None:
            behind = ui_text.stayed_behind_status(wb_update.stays_behind(before_record, plan), result, plan)
            if behind:
                text = f"{text} {behind}"
        record, may_write, notes = self._open_record()
        finished = wb_gearbox.finish_build(plan, result, record, workbook=self.path, digest=self.reading.digest,
                                           written_by=W.WRITTEN_BY)
        faults = self._write(finished, may_write)
        if not may_write:
            faults, notes = notes + faults, []
        self.note = (" ".join([text] + notes + faults), ok and not faults)
        say(f"status  [{'green' if self.note[1] else 'red'}] {self.note[0]}")
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
            f"{[(p.kind, list(p.mates)) for p in ahead.refused]}; unread ties {list(ahead.unread_ties)}")
    if line and desk.note is None:
        check(line in f.text, f"{label}: the footer says the user-work line as the window would: {line[:80]!r}…")
    return ahead


def predicted_carry(ahead):
    return {(c, g) for g, held in (ahead.carried if ahead is not None else ()) for c, _ in held}


def press(desk, label):
    """Update SolidWorks pressed (W8's traced press, through Desk9): the result, or None and ``desk.error``."""
    result, _, seconds = W.w8_update(CTX["worker"], desk, label)
    say(f"fact    {label}: the press took {seconds:.0f} s")
    return result


# -- reads ---------------------------------------------------------------------------------------------------------


def use_open(s, path):
    """The document made the build document WITHOUT opening or activating it (package B's ``use_open_document``
    when the source has it; else the same: found in SolidWorks' list, kept as the build document)."""
    if hasattr(s, "use_open_document"):
        return s.use_open_document(path)
    for doc in W.documents(s._app):  # noqa: SLF001
        if store.same_path(str(call(doc, "GetPathName") or ""), path):
            s._build_doc = doc  # noqa: SLF001
            s._raise_epoch()  # noqa: SLF001
            return True
    return None


def read_now(label, asm, folder, pairs, modes, *, activate=True):
    """In the active configuration, nothing shown or rebuilt: each body's frame and GetConstrainedStatus, every mate's
    code and flag in every mode, the documents' GetSaveFlag before and after (a read marking one is a STOP, §0.3).
    ``activate`` False: the assembly is read where it stands without being opened or activated (the old assembly)."""
    def work(s):
        if not activate:
            if use_open(s, asm) is None:
                raise swcom.SolidWorksError(f"{os.path.basename(asm)} is not open")
        out = {"flags_before": W.folder_flags(s, folder), "active": s.active_configuration(), "frames": {},
               "status": {}, "mates": {}, "by_mode": {}}
        try:            # IModelDocExtension.NeedsRebuild2 (swModelRebuildStatus_e), a read new to this repo: a fact
            out["needs_rebuild"] = int(swcom._read(call(s._doc(), "Extension"), "NeedsRebuild2"))  # noqa: SLF001
        except Exception as exc:  # noqa: BLE001 - a fact, read for the again sections
            out["needs_rebuild"] = f"unread: {type(exc).__name__}"
        for i, (g, n) in enumerate(pairs):
            s.find_component(f"rn{i}", n)
            out["frames"][g] = s.component_frame(f"rn{i}")
            out["status"][g] = s.constrained_status(f"rn{i}")
        for i, m in enumerate(s.mate_states()):
            out["mates"][m.name] = (m.code, m.suppressed)
            if modes:
                s.find_mate(f"rm{i}", m.name)
                out["by_mode"][m.name] = s.mate_suppression(f"rm{i}", modes)
        out["flags_after"] = W.folder_flags(s, folder)
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
    say(f"read    {label} (active {got['active']}): mates in error {errors or 'none'}; not free "
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
                s.find_component(f"re{i}", n)
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
    return out


def feature_list(path):
    """Every top-level feature of a part (``Session.feature_states``): (name, type, code)."""
    return run(f"features of {os.path.basename(path)}",
               job(path, lambda s: [(f.name, f.type_name, f.code) for f in s.feature_states()]))


def windows_new(before, seconds=8):
    """S0's P0 watch: the windows of SolidWorks' process new since ``before``, polled ``seconds`` s; those that count
    (a #32770 or a titled window, not the exempt notification box)."""
    seen, new = {h for h, _, _ in before}, []
    for _ in range(seconds):
        for h, c, t in S0.sw_windows():
            if h not in seen:
                seen.add(h)
                new.append((c, t, tuple(S0.xlhelp.child_texts(h)[:8])))
        time.sleep(1.0)
    counted = [w for w in new if (w[0] == "#32770" or w[1]) and not (not w[1] and w[2] == W.NOTIFICATION_TEXTS)]
    return new, counted


def save_user(folder, why):
    """The person saves in SolidWorks every modified document of the copy (W8's save_modified_in)."""
    saved = run("save", W.save_modified_in(folder), 600)
    say(f"person  saved in SolidWorks ({why}): {saved}")


# -- the user's work -------------------------------------------------------------------------------------------------


def user_parts():
    """S0's Sprocket and Housing, built by the strip once a run."""
    if not CTX["parts"]:
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


def rangebox_master():
    if MASTER["rangebox"]:
        return MASTER["rangebox"]
    here = os.path.join(OUT, "rangebox" + W.MASTER_SUFFIX)
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
        folder = W.copy_built(master, section)
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


def section_m3(out):
    say("== m3  ISSUE-1-PLAN §4 M3: an assembly rebuild, and the app's Update, with only a user mate and then only a "
        "user feature in error, under the dialog watch, ahead of anything that depends on it")
    parts = user_parts()
    folder, path, book, desk = copy_desk(rangebox_master(), "m3", "RangeBox.xlsx")
    try:
        for name in ("Sprocket.SLDPRT", "Housing.SLDPRT"):
            shutil.copy2(os.path.join(parts, name), os.path.join(folder, name))
        box = desk.record.gearbox
        asm, modes = box.assembly, list(box.modes)
        axes = {s.shaft: s.axis_name for s in wb_layout.shaft_layouts(desk.a.spec)}
        inserts = (("u1", "Sprocket.SLDPRT", (0.0, 0.0, 100.0), "Sprocket-1"),
                   ("uh", "Housing.SLDPRT", (0.0, 0.0, 60.0), "Housing-1"))
        mates = (("ua", "coincident", "u1:Gear Axis", f"lay:{axes['Input']}", 0.0, "UserAxis", {}),
                 ("uf", "distance", "u1:plane1", "lay:plane1", 100.0, "UserFront", {}),
                 ("ug", "distance", "u1:plane1", "uh:plane1", 40.0, "UserGap", {}))
        add_user_work("m3", desk, folder, inserts, mates, fixed=("uh",), refs={"lay": box.layout_component})
        save_user(folder, "the user's sprocket and housing")
        out["baseline"] = assembly_rebuild("m3 baseline", asm, folder)
        check(out["baseline"]["rebuilt"] and not any(c for c, sup in out["baseline"]["mates"].values() if not sup),
              "m3: with nothing in error the assembly rebuild returns True and no mate is in error")

        say("-- m3  a user mate in error: UserGap 40 -> 41 mm in every mode, which UserFront contradicts")

        def gap(value):
            def work(s):
                s.find_mate("ug", "UserGap")
                s.set_dimension_in("ug", value, modes)
                return True
            return work
        run("m3: UserGap 41", job(asm, gap(41.0)))
        got = out["mate_error"] = assembly_rebuild("m3 a user mate in error", asm, folder)
        users_bad = {n for n, (c, sup) in got["mates"].items() if c and not sup and n.startswith("User")}
        app_bad = {n for n, (c, sup) in got["mates"].items() if c and not sup and not n.startswith("User")}
        check(bool(users_bad), f"m3: a user mate reads in error, so the reading answers M3: user {sorted(users_bad)}, "
                               f"the app's {sorted(app_bad)}")
        say(f"answer  M3 (assembly, a user mate in error): the rebuild returned {got['rebuilt']}, What's Wrong "
            f"{got['whats_wrong']}, no window; the app's mates also read in error: {sorted(app_bad) or 'none'}")
        save_user(folder, "the mate in error, as the user leaves it")

        say("-- m3  the app's value Update (Sun's Backlash 0.4) with only that user mate in error")
        W.edit(desk, book, ("Gears", W.cell(book, "Gears", "Backlash", "Sun"), 0.4))
        before = S0.sw_windows()
        result = press(desk, "m3 Update with a user mate in error")
        new, counted = windows_new(before)
        watch_check("m3 Update with a user mate in error")
        if counted:
            stop(f"m3: a window came up during the Update with a user mate in error: {counted}")
        out["update_mate_error"] = _update_fact(desk, result)
        if result is not None:
            named = "UserGap" in desk.note[0]
            check(result.ok or named, f"m3: an Update that fails with only the user's mate in error names it as the "
                                      f"user's (ok {result.ok}; UserGap named {named}; failures {result.failures})")
            check(any(n == "UserGap" for _, n in result.user_in_error) or (result.user_work is not None and
                                                                          "UserGap" in result.user_work.in_error),
                  f"m3: the Update lists UserGap among the user's items in error: {result.user_in_error}")

        say("-- m3  UserGap back to 40: nothing in error again")
        run("m3: UserGap 40", job(asm, gap(40.0)))
        got = assembly_rebuild("m3 the mate set back", asm, folder)
        check(not any(c for n, (c, sup) in got["mates"].items() if not sup and n.startswith("User")),
              "m3: with UserGap back at 40 no user mate is in error")

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
            f"{got['rebuilt']}, What's Wrong {got['whats_wrong']}, no window")
        save_user(folder, "the user's part in error, as the user leaves it")

        say("-- m3  the app's value Update (Sun's Backlash 0.42) with only the user's feature in error")
        W.edit(desk, book, ("Gears", W.cell(book, "Gears", "Backlash", "Sun"), 0.42))
        before = S0.sw_windows()
        result = press(desk, "m3 Update with a user feature in error")
        new, counted = windows_new(before)
        watch_check("m3 Update with a user feature in error")
        if counted:
            stop(f"m3: a window came up during the Update with a user feature in error: {counted}")
        out["update_feature_error"] = _update_fact(desk, result)
        if result is not None:
            check(result.ok or "Sprocket" in desk.note[0],
                  f"m3: an Update that fails with only the user's part in error says it is the user's (ok {result.ok}; "
                  f"failures {result.failures})")
        RESULT["proposal"]["M3"] = {
            "assembly_rebuild_with_user_mate_in_error": out["mate_error"]["rebuilt"],
            "assembly_rebuild_with_user_feature_in_error": out["feature_error"]["rebuilt"],
            "part_rebuild_with_user_feature_in_error": out["part_rebuild"]["rebuilt"],
            "whats_wrong_window": False,
            "update_ok_with_user_mate_in_error": (out["update_mate_error"] or {}).get("ok"),
            "update_ok_with_user_feature_in_error": (out["update_feature_error"] or {}).get("ok")}
        say(f"propose M3: {RESULT['proposal']['M3']}")
    finally:
        W.end_copy(CTX["worker"], folder, "m3")


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
        W.end_copy(CTX["worker"], folder, "setup")
        raise
    MASTER["setup"] = W.keep_master(CTX["worker"], folder, "setup")
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
    result = press(desk, "setup quiet press")
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
        check(all(f.name.startswith("User") for f in work.features),
              f"{label}: every feature listed as the user's is the user's (M2): {[f.name for f in work.features]}")
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
                     ("ud5", "distance", "u5:plane1", "u4:plane1", 30.0, "UserDist5", {})):
            first = not made
            inserts = (("u5", "Sprocket.SLDPRT", (0.0, 0.0, 110.0), "Sprocket-5"),) if first else ()
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
                    "UserDist5": {"Sprocket-5", "Sprocket-4"}}

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
        for name, want in expected.items():
            info = r["mates"].get(name)
            say(f"answer  M1 {name} with {r['active']} active: {info}")
            if name == "UserDist5":
                continue                     # suppressed in the active mode: what it reads is the answer, not a check
            check(info is not None and info["whole"] and set(info["components"]) == want,
                  f"m1: {name} read whole as joining {sorted(want)}")
        result = press(desk, "m1 quiet press")
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
        W.end_copy(CTX["worker"], folder, "m1")


# -- go: the value and slide-offset Updates ---------------------------------------------------------------------------


def go_judge(label, desk, every, rel_orig, flags_set, out):
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
        ok = gap <= TOL and all(v <= TOL for v in gaps.values()) and not errors and abs(dz - RB_GAP) <= TOL and not free
        clean = clean and ok
        check(ok, f"{label}, {mode} shown: every app body at its frame on record ({gap:.1e} at {at or '-'}); each locked "
                  f"sprocket on its gear as set up {fmt(gaps)}; mates in error {errors or 'none'}; Sprocket-4 "
                  f"{dz:.9f} mm from Sprocket-3 (set {RB_GAP:g}); the train free {not free}")
    flags = {n: f for n, f in every["by_mode"].items() if n in flags_set}
    check(flags == flags_set, f"{label}: every user mate is on in the modes it was on in: "
                              f"{ {n: (flags_set[n], flags.get(n)) for n in flags_set if flags.get(n) != flags_set[n]} or 'as set'}")
    out.setdefault("judged", []).append({"label": label, "clean": clean and flags == flags_set})
    return clean


def go_press(label, desk, book, cells, out, rel_orig, flags_set):
    W.edit(desk, book, *cells)
    u = desk.update
    check(u is not None and not u.needs_new_revision and not u.refusal,
          f"{label}: classify makes it an Update: structural {u and list(u.structural)}")
    ahead = ahead_of(desk, f"{label}, before the press")
    want = set(RB_LOCKED.items())
    check(predicted_carry(ahead) == want and ahead is not None and not ahead.problems,
          f"{label}: the footer foresees each locked sprocket put with its gear and no refusal: "
          f"{sorted(predicted_carry(ahead))}")
    result = press(desk, label)
    if result is None:
        raise AssertionError(f"{label}: the press refused: {desk.error}")
    done = {(c, g) for c, g, _ in result.carried}
    check(result.ok and done == want and {m for _, _, m in result.carried} == set(result.put_in),
          f"{label}: the Update went ahead and put each locked sprocket with its gear in every mode it put "
          f"({result.put_in}): ok {result.ok}, carried {result.carried}, failures {result.failures}")
    check(done == predicted_carry(ahead), f"{label}: what the footer said before the press is what the press carried "
                                          f"(said {sorted(predicted_carry(ahead))}, did {sorted(done)})")
    check(not result.user_in_error and not result.user_features_in_error,
          f"{label}: nothing of the user's in error after: {result.user_in_error} "
          f"{[f.name for f in result.user_features_in_error]}")
    check(all(c in desk.note[0] for c in ("Sprocket-1", "Sprocket-2")),
          f"{label}: the Update's sentence names the sprockets it put with their gears")
    entry = desk.record.gearbox.user_work
    check(entry is not None and {(c.component, c.gear) for c in entry.carried} == want
          and list(entry.revision) == list(W.TAG["revision"]),
          f"{label}: the record's inventory holds the carried sprockets and revision "
          f"{list(entry.revision) if entry else None}, read at {entry.read_at if entry else None}")
    ahead_of(desk, f"{label}, after the press")
    box = desk.record.gearbox
    every = read_every(f"{label}, after", box.assembly, pairs_of(box, rb_users()), list(box.modes))
    go_judge(label, desk, every, rel_orig, flags_set, out)
    feats = feature_list(sun_part(box))
    key = [f for f in feats if f[0] == "User Keyway"]
    check(bool(key) and not key[0][2], f"{label}: the user's keyway rebuilt in Sun's part after the app's features, code "
                                       f"{key[0][2] if key else None}")
    return result


def go_turn(label, desk, mode, rel_before):
    box = desk.record.gearbox
    sun = box.drag[0]
    plane, _ = W.drive_assumptions(desk, sun, label)
    built_sun = W.wanted(desk)[sun]
    pairs = pairs_of(box, rb_users())
    before = read_now(f"before {label}", box.assembly, os.path.dirname(box.assembly), pairs, list(box.modes))
    got = run(label, W.s7_drive_job(box, mode, TURN, plane, built_sun), 600)
    after = read_now(f"after {label}", box.assembly, os.path.dirname(box.assembly), pairs, list(box.modes))
    turned = W.turn_degrees(before["frames"][sun][0], after["frames"][sun][0])
    carried = rel_gaps(rel_of(after["frames"], RB_LOCKED), rel_of(before["frames"], RB_LOCKED))
    check(not got["errors"] and not got["cleanup"] and turned is not None and abs(turned - TURN) <= 1e-6 * TURN
          and all(v <= TOL for v in carried.values()),
          f"{label}: the user's turn: {sun} turned {turned}° and each locked sprocket went with its gear {fmt(carried)}")


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
        flags_set = {n: f for n, f in every["by_mode"].items() if n.startswith("User")}
        check(all(not any(f.values()) for f in flags_set.values()) and len(flags_set) == 8,
              f"go: the user's 8 mates on in every mode as set up: {sorted(flags_set)}")
        go_judge("go as copied", desk, every, rel_orig, flags_set, out)
        go_turn("the user's turn +37° in H", desk, modes[0], rel_orig)
        out["value"] = bool(go_press("go value Update (Sun's Backlash 0.4)", desk, book,
                                     [("Gears", W.cell(book, "Gears", "Backlash", "Sun"), 0.4)], out, rel_orig, flags_set))
        live = run("Sun's globals", lambda s: W.live_globals(s, sun_part(desk.record.gearbox)))
        check(abs(float(live.get(spur.BACKLASH, 0.0)) - 0.4) < 1e-9, f"go: Sun's Backlash reads {live.get(spur.BACKLASH)}")
        go_turn("the user's turn +37° in L", desk, modes[-1], rel_orig)
        out["slide"] = bool(go_press("go slide-offset Update (RangeSlv L=+5.5)", desk, book,
                                     [("Gears", W.cell(book, "Gears", "Slides", "RangeSlv"), "H=-5, N=0, L=+5.5")],
                                     out, rel_orig, flags_set))
    finally:
        W.end_copy(CTX["worker"], folder, "go")


# -- refuse ----------------------------------------------------------------------------------------------------------


def refuse_press(label, desk, folder, kinds, mates_named=(), text=(), ahead=None, users=None, part=None):
    """The user saves, every user item and document read, Update pressed: it must refuse before any write with
    ``kinds`` among its problems, naming ``mates_named`` and saying ``text``; read again, nothing written (frames,
    mates' codes and flags, documents' marks, and ``part``'s globals: Sun's by default). ``ahead``: the footer's
    prediction before the press, held against what the press refused."""
    save_user(folder, f"before {label}")
    box = desk.record.gearbox
    pairs = pairs_of(box, rb_users() if users is None else users)
    before = read_now(f"before {label}", box.assembly, folder, pairs, list(box.modes))
    sun = part or sun_part(box)
    globals_before = run("Sun's globals", lambda s: W.live_globals(s, sun))
    result = press(desk, label)
    error = desk.error
    problems = list(getattr(error, "problems", ()) or ())
    say(f"fact    {label}: problems {[(p.kind, list(p.mates)) for p in problems]}")
    for p in problems:
        say(f"        {p.kind}: {p.sentence}")
    after = read_now(f"after {label}", box.assembly, folder, pairs, list(box.modes))
    globals_after = run("Sun's globals", lambda s: W.live_globals(s, sun))
    diff = written(before, after) + ([f"Sun's globals {globals_before} -> {globals_after}"]
                                     if globals_after != globals_before else [])
    got = {p.kind for p in problems}
    named = {m for p in problems for m in p.mates}
    said = " ".join(p.sentence for p in problems)
    check(result is None and isinstance(error, swbuild.UserWorkRefused) and set(kinds) <= got
          and set(mates_named) <= named and all(t in said for t in text),
          f"{label}: refused before any write as {sorted(kinds)}, naming {sorted(mates_named)} and saying {list(text)}: "
          f"got {sorted(got)}, named {sorted(named)}")
    check(not diff, f"{label}: nothing written: {diff or 'frames, mates, flags, marks and Sun globals as before'}")
    entry = desk.record.gearbox.user_work
    check(entry is not None and {p.kind for p in entry.problems} == got,
          f"{label}: the record keeps the refusal with its time {entry.read_at if entry else None}: "
          f"{[p.kind for p in entry.problems] if entry else None}")
    f = ahead_of(desk, f"{label}, after the refusal")
    if f is not None:
        check(bool(f.refused) and not ui_text.user_work_line(f)[1],
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
    refs = dict(rb_refs(box), u1="Sprocket-1", uh="Housing-1")
    want = {change[-1]: change[0] == "off" for change in changes}

    def work(s):
        out = {"status": {}, "flags": {}}
        for handle, name in refs.items():
            s.find_component(handle, name)
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
    result = press(desk, f"{label}: the quiet press")
    check(result is not None and result.placed == [] and result.changed == [],
          f"{label}: the quiet press read the user's work and changed nothing: {desk.error if result is None else 'ok'}")
    W.edit(desk, book, ("Gears", ref, backlash))
    return ahead_of(desk, f"{label}, before the press")


def section_refuse(out):
    say("== refuse  W9a's Done when: a lock to a fixed housing refuses naming it, a Bore Diameter typed in SolidWorks "
        "refuses naming the cell; with them a lightweight carried sprocket, the solver's tie, two app bodies locked "
        "together, and all at once; each foreseen or recorded in the footer, each writing nothing")
    folder, path, book, desk = copy_desk(user_master(), "refuse", "RangeBox.xlsx")
    try:
        box = desk.record.gearbox
        users_in_copy("refuse", desk, folder, rb_users())
        says = out.setdefault("problems", {})

        say("-- refuse  Sprocket-1 loaded lightweight (W9A-REVIEW-B 3 and the coordinator's item 4)")
        state = set_state(desk, "Sprocket-1", 1)
        if state not in (1, 4):
            check(False, f"refuse: Sprocket-1 did not read lightweight after SetSuppression2(1): {state}")
        else:
            ahead = quiet_then_edit("refuse lightweight", desk, book, 0.4)
            check(ahead is not None and any(p.kind == swbuild.PROBLEM_COMPONENT for p in ahead.problems),
                  "refuse lightweight: the footer foresees the refusal of a carried component loaded lightweight")
            says["lightweight"] = [p.sentence for p in refuse_press(
                "refuse lightweight", desk, folder, {swbuild.PROBLEM_COMPONENT}, (), ("Sprocket-1",), ahead=ahead)]
        set_state(desk, "Sprocket-1", 2)

        say("-- refuse  a user lock from Sprocket-1 to the fixed Housing-1")
        mates_job(desk, [("add", "uhl", "lock", "uh", "u1", 0.0, "UserHousingLock")])
        ahead = quiet_then_edit("refuse housing lock", desk, book, 0.4)
        says["housing lock"] = [p.sentence for p in refuse_press(
            "refuse housing lock", desk, folder, {swbuild.PROBLEM_TIE}, ("UserHousingLock",), ("Housing-1",),
            ahead=ahead)]
        W.edit(desk, book, ("Gears", W.cell(book, "Gears", "Backlash", "Sun"), 0.41))
        a = ahead_of(desk, "refuse, the workbook changed since the refusal")
        line, ok = ui_text.user_work_line(a)
        check(ok and "has changed since" in line, f"refuse: once the workbook changed the recorded refusal is said "
                                                  f"green with \"the workbook has changed since\": {line[:100]!r}")

        say("-- refuse  the solver's tie: the lock to the housing off, Sprocket-1's Top plane on Housing-1's")
        mates_job(desk, [("off", "UserHousingLock"), ("add", "ut", "coincident", "u1:plane2", "uh:plane2", 0.0, "UserTie")])
        says["tie"] = [p.sentence for p in refuse_press(
            "refuse tie read", desk, folder, {swbuild.PROBLEM_TIE}, ("UserTie",), ("unable to turn",))]

        say("-- refuse  two app bodies locked together: the tie off, a user lock from Sun to RangeSlv")
        mates_job(desk, [("off", "UserTie"), ("add", "u2b", "lock", "sun", "slv", 0.0, "UserTwoBodies")])
        says["two bodies"] = [p.sentence for p in refuse_press(
            "refuse two bodies", desk, folder, {swbuild.PROBLEM_TWO_BODIES}, ("UserTwoBodies",))]

        say("-- refuse  a Bore Diameter typed in SolidWorks: UserTwoBodies off; Sun's Bore Diameter 12")
        mates_job(desk, [("off", "UserTwoBodies")])
        run("Sun's bore 12", job(sun_part(box), lambda s: (s.set_global_variable(spur.BORE, "12"), bool(s.rebuild()))))
        cell = "Gears!" + W.cell(book, "Gears", "Bore", "Sun")
        problems = refuse_press("refuse bore typed", desk, folder, {swbuild.PROBLEM_VALUE}, (), (cell,))
        says["bore"] = [p.sentence for p in problems]
        values = [v for p in problems for v in p.values]
        check(any(v.name == spur.BORE and v.cell == cell and float(v.live) == 12.0 for v in values),
              f"refuse bore typed: the value named with its cell {cell}: {[(v.name, v.live, v.wanted, v.cell) for v in values]}")

        say("-- refuse  all at once: the housing lock and the two-body lock on again, the bore still 12")
        mates_job(desk, [("on", "UserHousingLock"), ("on", "UserTwoBodies")])
        # One cluster now holds Sun, RangeSlv and the housing: judge_user_work refuses it as two bodies (naming both
        # locks) and reads no ground for it; whether the solver's tie is read and said beside it is logged.
        problems = refuse_press("refuse all at once", desk, folder,
                                {swbuild.PROBLEM_VALUE, swbuild.PROBLEM_TWO_BODIES},
                                ("UserHousingLock", "UserTwoBodies"), (cell,))
        says["all"] = [p.sentence for p in problems]
        check(bool(problems) and problems[0].kind == swbuild.PROBLEM_VALUE,
              f"refuse all at once: every problem in one press, the values first: {[p.kind for p in problems]}")
    finally:
        W.end_copy(CTX["worker"], folder, "refuse")


# -- again: the Build again… job's read of the old assembly ------------------------------------------------------------


def stamps_of(paths):
    return {os.path.basename(p): os.path.getmtime(p) for p in paths if os.path.exists(p)}


def section_again(out, variant="open"):
    name = {"open": "again", "dirty": "again-dirty", "closed": "again-closed"}[variant]
    say(f"== {name}  Build again… (Sun's Part name changed): the question names what stays behind with its time; the "
        f"build job reads the old assembly first, which is "
        + {"open": "open in the session", "dirty": "open and needs a rebuild", "closed": "closed"}[variant])
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
        sentence = ui_text.stays_behind_sentence(stays, plan) if stays is not None else ""
        check(stays is not None and set(rb_users()) <= set(stays.components) and any(f == "User Keyway" for f, _, _ in stays.left)
              and sentence and sentence in question and ui_text.read_time(entry.read_at) in question,
              f"{name}: the question says what stays behind, with the time read ({ui_text.read_time(entry.read_at)}): "
              f"components {stays and list(stays.components)}, features left {stays and list(stays.left)}")
        desk.say_footer(f"{name}, before the build")
        user_files = [old, sun_part(box), os.path.join(folder, "Sprocket.SLDPRT"), os.path.join(folder, "Housing.SLDPRT")]
        times = stamps_of(user_files)
        pairs = pairs_of(box, rb_users())
        state_before = None
        if variant == "closed":
            left = run("close", W.quit_in(folder))
            check(not left, f"{name}: the old assembly closed before the build: left {left}")
        else:
            run(f"{name}: the old assembly opened", job(old, lambda s: s.active_configuration()))
            if variant == "dirty":
                def dirty(s):
                    s.find_mate("ud4", "UserDist4")
                    s.set_dimension_in("ud4", RB_GAP + 0.5, modes)        # the user's edit, not rebuilt yet
                    return True
                run(f"{name}: UserDist4 changed, no rebuild", job(old, dirty))
            state_before = read_now(f"{name} the old assembly before", old, folder, pairs, modes, activate=False)
            out["before"] = {k: v for k, v in state_before.items() if k != "frames"}
            if variant == "dirty":
                needs = state_before["needs_rebuild"]
                check(isinstance(needs, int) and needs != 0, f"{name}: the old assembly needs a rebuild before the "
                                                             f"build (NeedsRebuild2 {needs})")
        windows = S0.sw_windows()
        _, result = desk.build()
        new, counted = windows_new(windows)
        watch_check(f"{name} build")
        if result is None:
            raise AssertionError(f"{name}: the build refused: {desk.error}")
        check(result.ok and desk.record.gearbox.revision == 2, f"{name}: RangeBox_r2 built: ok {result.ok}")
        work, why = getattr(result, "old_user_work", None), getattr(result, "old_read", "")
        out["old_read"], out["old_user_work"] = why, None if work is None else {
            "components": [c.name for c in work.components], "mates": [m.name for m in work.mates]}
        expected = ui_text.stayed_behind_status(stays, result, plan)
        if variant == "closed":
            check(work is None and why == swbuild.OLD_NOT_OPEN and expected and expected in desk.note[0]
                  and "was not open" in desk.note[0],
                  f"{name}: the old assembly not open, so not read; the sentence gives the record's inventory: "
                  f"old_read {why!r}")
            still = run("open names", W.open_names)
            check(os.path.basename(old) not in still, f"{name}: the build did not open the old assembly")
        else:
            check(work is not None and not why and {c.name for c in work.components} == set(rb_users())
                  and {m.name for m in work.mates} >= set(rb_expected(box)) and expected and expected in desk.note[0],
                  f"{name}: the build job read the old assembly first and its sentence lists what stayed behind: "
                  f"{out['old_user_work']}")
            state_after = read_now(f"{name} the old assembly after", old, folder, pairs, modes, activate=False)
            mine = {os.path.basename(p) for p in user_files}
            changes = written(state_before, state_after, marks_of=mine)
            say(f"fact    {name}: GetSaveFlag of the folder's documents before the build "
                f"{W.marked(state_before['flags_after']) or 'none'}, after {W.marked(state_after['flags_after']) or 'none'}"
                " (the new revision's and the shared parts' as facts; the old assembly's and the user's files judged)")
            if state_after["needs_rebuild"] != state_before["needs_rebuild"]:
                changes.append(f"rebuild state {state_before['needs_rebuild']} -> {state_after['needs_rebuild']}")
            if state_after["flags_after"].get(os.path.basename(old)) != state_before["flags_after"].get(os.path.basename(old)):
                changes.append("the old assembly's save flag")
            if counted:
                changes.append(f"a window {counted}")
            if changes:
                section_stop(f"{name}: the build job's read changed the old assembly: {changes} (W9A-REVIEW-B 6)")
            check(True, f"{name}: the old assembly's save flag, active configuration ({state_after['active']}), rebuild "
                        f"state, mates' flags and codes and components' frames as before; no window")
        if counted:
            section_stop(f"{name}: a window came up during the build: {counted}")
        moved = {n: (t, stamps_of(user_files).get(n)) for n, t in times.items() if stamps_of(user_files).get(n) != t}
        if moved:
            section_stop(f"{name}: a user document's file time changed during the Build again…: {moved} (§0.3, W9d's STOP)")
        check(True, f"{name}: no file time of the user's documents changed: {sorted(times)}")
        desk.say_footer(f"{name}, after the build")
    finally:
        W.end_copy(CTX["worker"], folder, name)


# -- the 12 : 1 and the no-carrier branch -----------------------------------------------------------------------------


def spec_reducer(folder=""):
    """The 12 : 1 fixture as the W4/W5 demonstrations build it, its Output folder blank (W6-PLAN §5's way, so a copy
    of the built folder stands on its own)."""
    made = wb_link.Link(W.FIXTURE_12).read().spec
    return dataclasses.replace(made, box=dataclasses.replace(made.box, output_folder=folder))


def section_reducer(out):
    say("== reducer  the 12 : 1 (G1 on S1 drives G2, G3 locked to G2 drives G4 on S3; no carrier) written by the app's "
        "write_new and built to turn through the app's own Build; kept as reducer.master")
    folder, path, book, desk = W.write_fixture(CTX["worker"], CTX["excel"], "reducer", spec_reducer)
    try:
        W.build_turning(CTX["worker"], desk, "reducer", 4)
    except (AssertionError, W.Halt):
        W.end_copy(CTX["worker"], folder, "reducer")
        raise
    MASTER["reducer"] = W.keep_master(CTX["worker"], folder, "reducer")
    if not MASTER["reducer"]:
        raise AssertionError("reducer: reducer.master was not kept")


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
        quiet = press(desk, "nocarrier quiet press (the inventory recorded)")
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
            result = press(desk, f"nocarrier {label}")
            if result is None:
                check(False, f"nocarrier {label}: the press refused with the finding patched: {desk.error}")
                held["clean"].append(False)
                break
            done = {(c, g) for c, g, _ in result.carried}
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
        W.end_copy(CTX["worker"], folder, "nocarrier")
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
            "again": lambda out: section_again(out, "open"), "again-dirty": lambda out: section_again(out, "dirty"),
            "again-closed": lambda out: section_again(out, "closed"), "reducer": section_reducer,
            "nocarrier": section_nocarrier}


def main():
    os.makedirs(OUT, exist_ok=True)
    started = time.strftime("%Y%m%d-%H%M%S")
    json_path = os.path.join(os.path.dirname(os.path.abspath(W.LOG_PATH)), f"w9a-demo-{started}.json")

    def write_json():
        RESULT["fails"], RESULT["notes"] = list(W.FAILS), list(W.NOTES)
        with open(json_path, "w", encoding="utf-8") as handle:
            json.dump(RESULT, handle, indent=1, default=str)

    say(f"awake   {S0.keep_awake(True)}")
    say(f"run     {time.strftime('%Y-%m-%d %H:%M:%S')}; W9a demonstration from {W.SRC}{W.snapshot()}; sections "
        f"{CHOSEN}; masters {MASTER}")
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
                    if name in ("setup", "reducer") and os.path.isdir(os.path.join(OUT, name + W.MASTER_SUFFIX)):
                        say(f"skip    {name}: its master was kept earlier in this run")
                    else:
                        SECTIONS[name](out)
                except SectionStop as exc:
                    out["stop"] = str(exc)
                    say(f"STOP    the section {name} ends at its STOP: {exc}")
                except AssertionError as exc:
                    check(False, f"{name}: {exc}")
                    for line in traceback.format_exc().splitlines()[-8:]:
                        say("        " + line)
                finally:
                    out["seconds"] = round(time.monotonic() - began)
                    out["failed"] = W.FAILS[fails:]
                    say(f"time    {name}: {out['seconds']} s; {len(out['failed'])} failed; {W.memory()}")
                    write_json()
                watch_check(name)
        except DemoStop as exc:
            say(f"STOP    the run ends at its STOP: {exc}")
        except W.WorkerHung as exc:
            check(False, f"W9a: {exc}; the run ends here, nothing more is asked of SolidWorks")
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
                left = W.run(worker, W.close_ours, 600)
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
