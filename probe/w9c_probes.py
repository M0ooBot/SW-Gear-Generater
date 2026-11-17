r"""W9c's first step on SolidWorks: the probes ISSUE-1-PLAN §4 puts ahead of W9c's and W9d's packages (rows P1, M1's
leftovers, S5 and P2; §5 "W9c" and "W9d"; §2.1 and §2.5 for what they serve; §0.3 for STOP). Nothing of W9c or W9d
exists in the app yet: these measure the calls those packages would make, and propose findings in the log without
setting any. The note is ``docs/notes-workbook/W9C-PROBES.md``.

python.exe probe/w9c_probes.py <repo src> <output folder under C:\> --pid PID [--log FILE]
                               [--sections p1,m1,s5,p2|all] [--master DIR] [--user-master DIR]
                               [--reducer-master DIR] [--redo]
python probe/w9c_probes.py --self-check      (no SolidWorks: the pure judgements, on made-up readings)
python probe/w9c_probes.py --help

``--master``: S0's kept ``rangebox.master`` for this version; ``--user-master``: W9a's ``setup.master`` (RangeBox with
the user's work); ``--reducer-master``: W9a's ``reducer.master``. Each is built here first, through W9a's own builders,
when not given and not in <out>.

Sections, in this order (each runs alone; a dialog probe goes first in its session, so a dialog costs nothing else):

- ``p1``  deleting a component from an assembly (W9c's removal): three candidate routes, each on its own fresh copy of
          the 12 : 1 reducer, deleting G4 with its app mates, and the first route again on a copy of RangeBox, deleting
          HighDog, so there are mode configurations and per-mode flags. Read after each: the component gone from every
          configuration, its mates gone or left (named, with codes), anything else moved, the document dirty, the
          handles of the other components held across the delete.
- ``m1``  the user-mate kinds W9a left unread: concentric, limit distance, limit angle, width, a user gear mate on an
          app gear (path is not made: below), each on its own user component in a copy of RangeBox; read by the app's
          ``mate_info``, its flags per mode, its definition; GetSaveFlag before and after the reads; then a quiet press
          and the footer's judgement. The mate to a leaf inside a user sub-assembly is in ``p2``, which inserts one.
- ``s5``  W9d's spike: (a) every user mate's definition read and (b, c) each remade by AddMate5 in a second assembly,
          its entities found by a part-level persistent reference (user parts), by name (the layout's axes), by tree
          order (the assembly's own plane), or as whole components (locks), then compared, definition and frames;
          (e) a component's state per configuration read without showing, by two candidate routes, against the shown
          truth; (d) the assembly opened read-only when already open and when not; (f) GetSaveFlag before and after
          every read.
- ``p2``  a user sub-assembly inserted by its file (opened first, ``API-LEDGER.md:531``) and a mate made to a leaf
          inside it (M1's last item, ``ReferenceComponent`` giving the leaf's path); then a sub-assembly with a missing
          reference among its own files opened and inserted: a "find file" dialog is the finding. Last, because it may
          leave the session unusable.

**A dialog is a finding, not a failure.** Every call that may raise one runs under a watch that logs it (class,
caption, buttons and texts; never SolidWorks' frame title) and does not answer it. A dialog seen ends that case (each
p1 route is a case on its own copy); if the job returned and the dialog went, the next case starts from a fresh copy;
if the job did not return within the wait, or the dialog stays up, the session cannot go on: the script says so and
ends the run cleanly, nothing closed or saved (W9a's hung-worker close).

Calls new to the app are said so at each use ("NEW"), with what the macro database says of them; nothing new is
presented as known. Everything W9a's script does for a run is done here by running its ``main`` with these sections.
"""

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SELF_CHECK = "--self-check" in sys.argv

if "--help" in sys.argv or "-h" in sys.argv:
    print(__doc__)
    raise SystemExit(0)


# -- pure judgements ------------------------------------------------------------------------------------------------------

FRAME_TOL = 1e-6           # mm and rotation entries: a body that did not move
VALUE_TOL = 1e-9           # m or rad: a remade mate's value against the read one


def frame_gap(a, b):
    """The largest difference between two frames ``(rotation 9, origin mm)``: rotation entries and mm alike."""
    if a is None or b is None or isinstance(a, str) or isinstance(b, str):
        return float("inf")
    return max([abs(x - y) for x, y in zip(a[0], b[0])] + [abs(x - y) for x, y in zip(a[1], b[1])])


def p1_verdict(out, target):
    """A delete read: whether ``target`` is gone from every configuration, what became of the mates that touched it,
    whether anything else moved (held handles, then fresh finds), the document marked, and the other handles held
    across the delete answering."""
    per_config = out.get("components_by_configuration", {})
    gone = bool(per_config) and all(target not in names for names in per_config.values()) \
        and target not in out.get("components_after", [target])
    after = out.get("mates_after", {})
    touching = out.get("touching", [])
    left = {m: after[m] for m in touching if m in after}
    stale = sorted(n for n, f in out.get("held_after", {}).items() if isinstance(f, str) or f is None)
    moved = {n: frame_gap(f, out["frames_after"].get(n)) for n, f in out.get("frames_before", {}).items()
             if frame_gap(f, out.get("frames_after", {}).get(n)) > FRAME_TOL}
    errors = {m: c for m, (c, sup) in after.items() if c and not sup}
    return {"gone_everywhere": gone, "mates_removed": sorted(set(touching) - set(after)), "mates_left": left,
            "dangling": {m: out.get("info_after", {}).get(m) for m in left}, "errors_after": errors,
            "others_moved": moved, "handles_stale": stale, "dirty": out.get("flag_after_delete"),
            "clean": gone and not left and not moved and not stale and not errors}


def same_definition(read, remade, tol=VALUE_TOL):
    """What differs between a mate's definition as read and as remade: type and type name, alignment, flip, and every
    value both give."""
    out = []
    for key in ("type_name", "type", "alignment", "flipped"):
        if read.get(key) != remade.get(key):
            out.append(f"{key} {read.get(key)!r} -> {remade.get(key)!r}")
    for key, value in (read.get("values") or {}).items():
        other = (remade.get("values") or {}).get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if not isinstance(other, (int, float)) or abs(value - other) > tol:
                out.append(f"{key} {value!r} -> {other!r}")
    return out


def state_agrees(candidate, truth):
    """A candidate route's per-configuration reads against the truth shown: the configurations where they differ, and
    whether every one was read."""
    differ = {c: (candidate.get(c), t) for c, t in truth.items() if candidate.get(c) != t}
    return {"agrees": not differ and set(candidate) >= set(truth), "differ": differ}


def flags_changed(before, after):
    """Documents whose GetSaveFlag a read turned on."""
    return sorted(n for n, f in after.items() if f and not before.get(n))


def propose(name, value, evidence):
    """A finding proposed in ``findings.py``'s style, never set: its name, value and what bears it out."""
    return f"propose {name} = {value!r}  # {evidence}"


def self_check():
    bad = []

    def ok(cond, what):
        print(("ok      " if cond else "FAIL    ") + what)
        if not cond:
            bad.append(what)

    rot = (1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0)
    clean = {"components_by_configuration": {"H": ["A-1", "B-1"], "N": ["A-1", "B-1"]}, "components_after": ["A-1",
             "B-1"], "touching": ["G on S", "G meshes"], "mates_after": {"A on S": (0, False)},
             "frames_before": {"A-1": (rot, (0, 0, 1.0))}, "frames_after": {"A-1": (rot, (0, 0, 1.0))},
             "held_after": {"A-1": (rot, (0, 0, 1.0))}, "flag_after_delete": True}
    v = p1_verdict(clean, "G-1")
    ok(v["clean"] and v["mates_removed"] == ["G meshes", "G on S"], f"p1: a clean delete reads clean: {v}")
    left = dict(clean, mates_after={"G meshes": (51, False)}, info_after={"G meshes": ["", "B-1"]},
                held_after={"A-1": "stale: ComError"})
    v = p1_verdict(left, "G-1")
    ok(not v["clean"] and v["mates_left"] == {"G meshes": (51, False)} and v["handles_stale"] == ["A-1"]
       and v["errors_after"] == {"G meshes": 51}, f"p1: a dangling mate and a stale handle are said: {v}")
    still = dict(clean, components_by_configuration={"H": ["A-1"], "N": ["A-1", "G-1"]})
    ok(not p1_verdict(still, "G-1")["gone_everywhere"], "p1: a component left in one configuration is not gone")
    moved = dict(clean, frames_after={"A-1": (rot, (0, 0, 1.5))})
    ok(p1_verdict(moved, "G-1")["others_moved"] == {"A-1": 0.5}, "p1: another body moved is said")
    read = {"type_name": "MateDistanceDim", "type": 5, "alignment": 2, "flipped": False, "values": {"Distance": 0.09}}
    ok(same_definition(read, dict(read)) == [], "s5: a definition remade the same compares equal")
    ok(same_definition(read, dict(read, flipped=True, values={"Distance": 0.0901})) ==
       ["flipped False -> True", "Distance 0.09 -> 0.0901"], "s5: a flip and a value remade otherwise are said")
    ok(state_agrees({"H": 2, "N": 2, "L": 0}, {"H": 2, "N": 2, "L": 0})["agrees"], "s5: a route agreeing everywhere")
    ok(not state_agrees({"H": 2, "N": 2}, {"H": 2, "N": 2, "L": 0})["agrees"], "s5: a route that missed a "
                                                                                "configuration does not agree")
    ok(flags_changed({"A": False, "B": True}, {"A": True, "B": True}) == ["A"], "f: a read that marked A is said")
    ok(propose("X_ROUTE", "a b", "line") == "propose X_ROUTE = 'a b'  # line", "propose's form")
    print(f"done    {len(bad)} failed")
    return 0 if not bad else 1


if SELF_CHECK:
    raise SystemExit(self_check())


# -- the live run: W9a's harness ------------------------------------------------------------------------------------

sys.path.insert(0, HERE)
import w9a_demonstration as A  # noqa: E402  (W8's and S0's scripts, the watch, the What's Wrong rule, Desk9, main)

W, S0 = A.W, A.S0
from gear_generator import findings, swcom  # noqa: E402
from gear_generator.swcom import call  # noqa: E402

say, check = W.say, W.check
OUT = W.OUT
CTX, RESULT, run, job = A.CTX, A.RESULT, A.run, A.job
DIALOG_WAIT = 120.0        # s: a call that may raise a dialog is waited for this long, then the session is given up
ENUMS = {}


class CaseStop(Exception):
    """A dialog ended this case (one copy); the job returned and the dialog went, so the next case may go on."""


def raw(obj, name, *args):
    """``call``, and a member late binding hands back uncalled (a bound method: GOTCHAS §55, 843e9e4) called."""
    value = call(obj, name, *args)
    return swcom._guarded(name, value) if type(value).__name__ == "method" else value  # noqa: SLF001


def new(what):
    say(f"NEW     {what}")


def in_build(work):
    """A worker job that is not in an assembly opened by ``job``: the app's build state around it (``begin_build``
    keeps the handles add_component and the selections need), ended whatever happens."""
    def wrapped(s):
        s.begin_build()
        try:
            return work(s)
        finally:
            s.end_build()
    return wrapped


# -- swconst, read from the running install ---------------------------------------------------------------------------


def swconst(names):
    """The named enumerations of the running SolidWorks' ``swconst.tlb`` (beside its ``sldworks.exe``, found from the
    attached PID), checked against the mate types the app already verified."""
    if ENUMS:
        return ENUMS
    import pythoncom
    import win32api
    import win32con
    import win32process
    handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, W.PID)
    try:
        exe = win32process.GetModuleFileNameEx(handle, 0)
    finally:
        win32api.CloseHandle(handle)
    path = os.path.join(os.path.dirname(exe), "swconst.tlb")
    lib = pythoncom.LoadTypeLib(path)
    for index in range(lib.GetTypeInfoCount()):
        enum = lib.GetDocumentation(index)[0]
        if enum in names:
            info = lib.GetTypeInfo(index)
            values = {}
            for i in range(info.GetTypeAttr().cVars):
                desc = info.GetVarDesc(i)
                values[str(info.GetNames(desc.memid)[0])] = int(desc.value)
            ENUMS[enum] = values
    mates = ENUMS.get("swMateType_e", {})
    control = {"swMateCOINCIDENT": findings.MATE_COINCIDENT, "swMateDISTANCE": findings.MATE_DISTANCE,
               "swMateANGLE": findings.MATE_ANGLE, "swMateGEAR": findings.MATE_GEAR,
               "swMateLOCK": findings.MATE_LOCK, "swMateCONCENTRIC": findings.MATE_CONCENTRIC}
    wrong = {k: (mates.get(k), v) for k, v in control.items() if mates.get(k) != v}
    say(f"fact    swconst.tlb beside the running sldworks.exe; read {sorted(ENUMS)}; the positive control (mate types "
        f"findings.py holds) {'agrees' if not wrong else 'DISAGREES: ' + str(wrong)}")
    if wrong or set(names) - set(ENUMS):
        raise AssertionError(f"swconst.tlb did not give what the probes need: missing {sorted(set(names) - set(ENUMS))}"
                             f", control {wrong}")
    return ENUMS


def enum(name, member):
    return swconst(ENUM_NAMES)[name][member]


ENUM_NAMES = ("swMateType_e", "swMateAlign_e", "swMateWidthOptions_e", "swOpenDocOptions_e",
              "swDeleteSelectionOptions_e", "swComponentSuppressionState_e", "swInConfigurationOpts_e",
              "swSelectType_e", "swDocumentTypes_e")


# -- the dialog watch for a call that may raise one -------------------------------------------------------------------


def watched(label, fn, wait=DIALOG_WAIT):
    """A job that may raise a dialog, waited for under W9a's box watch (it logs, it never answers): every dialog of
    SolidWorks' process that comes up is recorded (class, caption, buttons, style, owner by class), never answered.
    Returns ``(value, dialogs)``. A dialog seen with the job returned and the dialog gone raises CaseStop; a job that
    does not return, or a dialog that stays, ends the run (A.BoxSeen), nothing more asked of SolidWorks."""
    skip = set(A.box_windows(set()))
    frame = A.sw_frame()
    dialogs = []

    def tick(elapsed, returned):
        for h in A.box_windows(skip | {d["hwnd"] for d in dialogs}):
            facts = A.window_facts(h, frame)
            facts.update(seconds=round(elapsed, 2), call_in_progress=W.CALLS["now"] or None)
            dialogs.append(facts)
            say(f"DIALOG  {label}: {facts}")
    A.BOX.update(on=True, tick=tick, timeout=wait)
    value, hung = None, None
    try:
        value = run(label, fn, wait)
    except W.WorkerHung as exc:
        hung = exc
    finally:
        A.BOX.update(on=False, tick=None)
    if hung is not None or (dialogs and A.visible_now([d["hwnd"] for d in dialogs])):
        W.HUNG["on"] = True
        RESULT["stops"].append(f"{label}: a dialog held the session")
        raise A.BoxSeen(f"{label}: {'the job did not return in ' + str(wait) + ' s' if hung else 'a dialog stays up'}"
                        f" ({len(dialogs)} dialog(s) recorded): the session cannot go on; nothing more is asked of "
                        "SolidWorks, nothing closed or saved. Start a fresh SolidWorks and run the remaining sections.")
    if dialogs:
        raise CaseStop(f"{label}: {len(dialogs)} dialog(s) came and went, the job returned: {dialogs}")
    return value, dialogs


def end(folder, name):
    """A copy's end, unsaved: nothing of a probe's is kept."""
    if not W.HUNG["on"]:
        A.w8_step(W.end_copy, CTX["worker"], folder, name, save=False)


# -- p1: deleting a component ---------------------------------------------------------------------------------------

P1_ROUTES = {
    "select4-editdelete": "IComponent2.Select4(False, null, False), then IModelDoc2.EditDelete()",
    "feature-editdelete": "the component's feature (IAssemblyDoc.FeatureByName(Name2)) Select2(False, 0), then "
                          "EditDelete(): MATE_DELETE_ROUTE's form, used by the app for a mate",
    "deleteselection2": "IComponent2.Select4(False, null, False), then IModelDocExtension.DeleteSelection2(0)",
}
P1_CASES = [("reducer", "G4", route) for route in P1_ROUTES] + [("rangebox", "HighDog", "select4-editdelete")]


def p1_delete(target, route, modes):
    """The job: everything read before, the component deleted by ``route``, the other components' handles read across
    it, then every configuration shown and read."""
    def work(s):
        doc = s._doc()  # noqa: SLF001
        out = {"active": s.active_configuration(), "flag_before": bool(call(doc, "GetSaveFlag"))}
        names = [c.name for c in s.components()]
        out["components_before"] = names
        others = [n for n in names if n != target]
        for i, n in enumerate(others):
            s.find_component(f"o{i}", n)
        out["frames_before"] = {n: s.component_frame(f"o{i}") for i, n in enumerate(others)}
        mates = s.mate_states()
        out["mates_before"] = {m.name: (m.code, m.suppressed) for m in mates}
        touching = []
        for i, m in enumerate(mates):
            s.find_mate(f"m{i}", m.name)
            if target in s.mate_info(f"m{i}").components:
                touching.append(m.name)
        out["touching"] = touching
        component = swcom.Session._component_by(findings.COMPONENT_FIND_ROUTE, doc, target)  # noqa: SLF001
        call(doc, "ClearSelection2", True)
        if route == "feature-editdelete":
            selected = call(call(doc, "FeatureByName", target), "Select2", False, 0)
        else:
            selected = call(component, "Select4", False, swcom._null_dispatch(), False)  # noqa: SLF001
        out["selected"] = [bool(selected), s._selected()]  # noqa: SLF001
        if route == "deleteselection2":
            out["returned"] = repr(raw(call(doc, "Extension"), "DeleteSelection2", 0))
        else:
            out["returned"] = repr(swcom._guarded("EditDelete", lambda: doc.EditDelete()))  # noqa: SLF001
        call(doc, "ClearSelection2", True)
        out["flag_after_delete"] = bool(call(doc, "GetSaveFlag"))
        held = {}
        for i, n in enumerate(others):
            try:
                held[n] = s.component_frame(f"o{i}")
            except Exception as exc:  # noqa: BLE001 - a stale handle is the answer
                held[n] = f"stale: {type(exc).__name__}: {exc}"
        out["held_after"] = held
        out["rebuilt"] = bool(s.rebuild(kind=swcom.ASSEMBLY_TRAIN))
        out["components_after"] = [c.name for c in s.components()]
        after = s.mate_states()
        out["mates_after"] = {m.name: (m.code, m.suppressed) for m in after}
        info = {}
        for i, m in enumerate(after):
            if m.name in touching:
                s.find_mate(f"a{i}", m.name)
                info[m.name] = list(s.mate_info(f"a{i}").components)
        out["info_after"] = info
        by_config = {}
        for mode in (modes or [""]):
            if mode:
                s.show_configuration(mode)
                s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            by_config[mode or "(one)"] = [c.name for c in s.components()]
        if modes:
            s.show_configuration(out["active"])
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        out["components_by_configuration"] = by_config
        frames = {}
        for i, n in enumerate(others):
            try:
                s.find_component(f"f{i}", n)
                frames[n] = s.component_frame(f"f{i}")
            except Exception as exc:  # noqa: BLE001
                frames[n] = f"unread: {type(exc).__name__}: {exc}"
        out["frames_after"] = frames
        return out
    return work


def section_p1(out):
    say("== p1  deleting a component from an assembly (W9c's removal; plan §4 P1): each route on its own fresh copy, "
        "under a watch that logs a dialog and answers none")
    new("deleting a component: no route is in the app or verified in the macro database for a component. The ledger "
        "has EditDelete on a mate (MATE_DELETE_ROUTE, verified 2026 and 2024) and DeleteSelection2(options) 'verified, "
        "SW 2026' on a folder only")
    out["cases"] = {}
    for index, (box, target, route) in enumerate(P1_CASES, 1):
        name = f"p1-{index}-{route}"
        master, workbook = ((A.reducer_master(), "Reducer_12to1.xlsx") if box == "reducer"
                            else (A.rangebox_master(), "RangeBox.xlsx"))
        say(f"-- p1  case {index}: {target} out of a copy of {os.path.basename(master)} by {P1_ROUTES[route]}")
        folder, path, book, desk = A.copy_desk(master, name, workbook)
        case = out["cases"][name] = {"box": box, "route": route}
        try:
            gearbox = desk.record.gearbox
            component = dict(W.bodies(gearbox))[target]
            got, _ = watched(f"p1 case {index} ({route})",
                             job(gearbox.assembly, p1_delete(component, route, list(gearbox.modes))))
            verdict = p1_verdict(got, component)
            case.update(read=got, verdict=verdict)
            say(f"fact    p1 case {index}: selected {got['selected']}; the call returned {got['returned']}; the "
                f"assembly marked {got['flag_after_delete']} (before {got['flag_before']}); rebuilt {got['rebuilt']}")
            say(f"fact    p1 case {index}: {verdict}")
            check(True, f"p1 case {index} ({route}): measured, no dialog; clean {verdict['clean']}")
        except CaseStop as exc:
            case["dialog"] = str(exc)
            say(f"STOP    p1 case {index}: {exc} (the finding; the next case starts from a fresh copy)")
        finally:
            end(folder, name)
    clean = [c["route"] for c in out["cases"].values() if c.get("verdict", {}).get("clean")]
    dialogs = [c["route"] for c in out["cases"].values() if c.get("dialog")]
    say(propose("COMPONENT_DELETE_ROUTE", clean[0] if clean else None,
                f"p1: clean on {clean}, a dialog on {dialogs or 'none'}; the first clean route, if any"))
    rangebox = next((c for c in out["cases"].values() if c["box"] == "rangebox"), {})
    say(propose("COMPONENT_DELETE_IN_EVERY_CONFIGURATION",
                rangebox.get("verdict", {}).get("gone_everywhere"), "p1's RangeBox case, every mode shown"))
    say(propose("COMPONENT_DELETE_TAKES_ITS_MATES",
                all(not c.get("verdict", {}).get("mates_left") for c in out["cases"].values() if c.get("verdict"))
                if any(c.get("verdict") for c in out["cases"].values()) else None, "p1: every case's mates_left"))
    say(propose("COMPONENT_DELETE_KEEPS_OTHER_HANDLES",
                all(not c["verdict"]["handles_stale"] for c in out["cases"].values() if c.get("verdict"))
                if any(c.get("verdict") for c in out["cases"].values()) else None, "p1: every case's handles_stale"))
    say(propose("COMPONENT_DELETE_DIALOG", bool(dialogs), f"p1: a dialog on {dialogs or 'no route'}"))


# -- reading a mate whole (m1, s5) ------------------------------------------------------------------------------------

IMATE_FIELDS = ("Type", "Alignment", "Flipped", "MaximumVariation", "MinimumVariation")
DEFINITION_FIELDS = ("Distance", "Angle", "MateAlignment", "GearRatioNumerator", "GearRatioDenominator", "Reverse",
                     "FlipDimension", "MaximumDistance", "MinimumDistance", "MaximumAngle", "MinimumAngle")


def _try(obj, name):
    try:
        return swcom._read(obj, name)  # noqa: SLF001
    except Exception:  # noqa: BLE001 - a member a mate kind does not have is skipped (macro database assemblies/06)
        return None


def _plain(value):
    if isinstance(value, (bool, int, float, str)) or value is None:
        return value
    if isinstance(value, (tuple, list)):
        return [_plain(v) for v in value]
    return repr(value)


def mate_definition(s, feature):
    """A mate as assemblies/06 reads it: its type name; IMate2's Type, Alignment, Flipped and variations; whatever
    its definition answers; its dimensions (m or rad); each entity's component, reference type, parameters and, for a
    reference feature, its name."""
    out = {"type_name": _try(feature, "GetTypeName2"), "suppressed": _try(feature, "IsSuppressed")}
    mate = _try(feature, "GetSpecificFeature2")
    if mate is not None:
        fields = {k: _plain(_try(mate, k)) for k in IMATE_FIELDS}
        out.update(type=fields["Type"], alignment=fields["Alignment"], flipped=fields["Flipped"],
                   variation=(fields["MaximumVariation"], fields["MinimumVariation"]))
        entities = []
        count = _try(mate, "GetMateEntityCount")
        for i in range(int(count) if isinstance(count, int) else 0):
            entity = call(mate, "MateEntity", i)
            component = _try(entity, "ReferenceComponent")
            reference = _try(entity, "Reference")
            entities.append({"component": str(call(component, "Name2")) if component is not None else "",
                             "reference_type": _plain(_try(entity, "ReferenceType2")),
                             "params": _plain(_try(entity, "EntityParams")),
                             "feature": _plain(_try(reference, "Name")) if reference is not None else None})
        out["entities"] = entities
    definition = _try(feature, "GetDefinition")
    values = {}
    if definition is not None:
        for k in DEFINITION_FIELDS:
            v = _try(definition, k)
            if v is not None and not callable(v):
                values[k] = _plain(v)
    out["values"] = values
    out["dimensions"] = [(str(call(d, "Name")), float(call(d, "SystemValue")))
                         for d in swcom.Session._dimensions(feature)]  # noqa: SLF001
    return out


# -- m1: the user-mate kinds W9a left unread ----------------------------------------------------------------------------

M1_INSERTS = (("ua", "Sprocket.SLDPRT", (0.0, 0.0, 60.0), "Sprocket-1"),
              ("ub", "Sprocket.SLDPRT", (0.0, 0.0, 80.0), "Sprocket-2"),
              ("uc", "Sprocket.SLDPRT", (0.0, 0.0, 100.0), "Sprocket-3"),
              ("ud", "Sprocket.SLDPRT", (0.0, 0.0, 120.0), "Sprocket-4"),
              ("ue", "Sprocket.SLDPRT", (0.0, 0.0, 160.0), "Sprocket-5"),
              ("uh", "Housing.SLDPRT", (0.0, 0.0, 120.0), "Housing-1"))


def part_faces_of(component):
    """The faces of a component's part, each with its surface kind, a cylinder's radius (mm) and a plane's z (mm)."""
    part = call(component, "GetModelDoc2")
    out = []
    for body in list(raw(part, "GetBodies2", 0, True) or []):
        for face in list(raw(body, "GetFaces") or []):
            surface = raw(face, "GetSurface")
            if raw(surface, "IsCylinder"):
                p = [float(v) for v in raw(surface, "CylinderParams")]
                out.append(("cylinder", round(p[6] * 1000.0, 6), face))
            elif raw(surface, "IsPlane"):
                p = [float(v) for v in raw(surface, "PlaneParams")]
                out.append(("plane", round(p[5] * 1000.0, 6) if abs(abs(p[2]) - 1.0) < 1e-9 else None, face))
    return out


def select_face(s, component, face, append, mark):
    """A part's face selected in the assembly through its component: ``IComponent2.GetCorresponding(face)`` (verified
    in the ledger for a feature only: NEW for a face), then ``Select4(append, data, False)`` with ``data.Mark``."""
    doc = s._doc()  # noqa: SLF001
    target = call(component, "GetCorresponding", face)
    if target is None:
        raise swcom.SolidWorksError("GetCorresponding gave no assembly face")
    data = call(call(doc, "SelectionManager"), "CreateSelectData")
    swcom._put(data, "Mark", mark)  # noqa: SLF001
    before = s._selected()  # noqa: SLF001
    call(target, "Select4", append, data)
    if s._selected() <= before:  # noqa: SLF001
        raise swcom.SolidWorksError("the face did not select")


def raw_mate(s, name, mtype, picks, *, dist=(0.0, 0.0, 0.0), angle=(0.0, 0.0, 0.0), width_option=0, flip=False):
    """``AddMate5`` on selections ``picks`` (each a callable selecting one entity), the mate renamed ``name``.
    Returns ``(name or what SolidWorks named it, status)`` or raises with what SolidWorks answered."""
    doc = s._doc()  # noqa: SLF001
    call(doc, "ClearSelection2", True)
    for pick in picks:
        pick()
    before = s._mate_names()  # noqa: SLF001
    mate, status = s._add_mate5(mtype, findings.MATE_ALIGN_CLOSEST, flip, dist[0], dist[1], dist[2], 1, 1,  # noqa: SLF001
                                angle[0], angle[1], angle[2], False, False, width_option)
    call(doc, "ClearSelection2", True)
    made = [n for n in s._mate_names() if n not in before]  # noqa: SLF001
    if mate is None or len(made) != 1:
        raise swcom.SolidWorksError(f"AddMate5 made no mate (status {status}, {len(made)} new)")
    kept = s._rename(s._mate_feature(made[0]), name)  # noqa: SLF001
    return kept, status


def m1_mates(modes):
    """The job: each kind made on its own user component, every new mate set on in every mode, then read."""
    def work(s):
        mt = ENUMS["swMateType_e"]
        width_centred = next((v for k, v in ENUMS["swMateWidthOptions_e"].items() if "Center" in k), 0)
        comp = {h: s._component(h) for h in ("ua", "ub", "uc", "ud", "ue", "uh")}  # noqa: SLF001
        faces = {h: part_faces_of(comp[h]) for h in ("ua", "ud", "uh")}
        made, tries = {}, {}

        def attempt(kind, fn):
            try:
                made[kind] = fn()
                tries[kind] = "made"
            except Exception as exc:  # noqa: BLE001 - what SolidWorks answered is the finding
                tries[kind] = f"{type(exc).__name__}: {exc}"
                call(s._doc(), "ClearSelection2", True)  # noqa: SLF001

        bore = next((f for k, r, f in faces["ua"] if k == "cylinder" and abs(r - 5.0) < 1e-6), None)
        attempt("concentric", lambda: raw_mate(s, "UserConcentric", mt["swMateCONCENTRIC"], (
            lambda: select_face(s, comp["ua"], bore, False, 1),
            lambda: s._component_ref("lay:Input Axis", True))))  # noqa: SLF001
        for h, n in (("ub", "UserAxisB"), ("uc", "UserAxisC"), ("ud", "UserAxisD"), ("ue", "UserAxisE")):
            s.add_mate(f"x{h}", "coincident", f"{h}:Gear Axis", "lay:Input Axis", 0.0, n)
        attempt("limit distance", lambda: raw_mate(s, "UserLimitDistance", mt["swMateDISTANCE"], (
            lambda: s._component_ref("ub:plane1", False), lambda: s._component_ref("lay:plane1", True)),  # noqa: SLF001
            dist=(0.080, 0.085, 0.075)))
        attempt("limit angle", lambda: raw_mate(s, "UserLimitAngle", mt["swMateANGLE"], (
            lambda: s._component_ref("uc:plane2", False), lambda: s._component_ref("lay:plane2", True)),  # noqa: SLF001
            angle=(math.radians(10.0), math.radians(40.0), math.radians(0.0))))
        ends = {h: sorted((z, f) for k, z, f in faces[h] if k == "plane" and z is not None) for h in ("ud", "uh")}
        for label, marks in (("width faces mark 1, tab faces mark 2", (1, 1, 2, 2)),
                             ("all four at mark 1", (1, 1, 1, 1))):
            if "width" in made:
                break
            attempt("width", lambda m=marks: raw_mate(s, "UserWidth", mt["swMateWIDTH"], (
                lambda: select_face(s, comp["ud"], ends["ud"][0][1], False, m[0]),
                lambda: select_face(s, comp["ud"], ends["ud"][-1][1], True, m[1]),
                lambda: select_face(s, comp["uh"], ends["uh"][0][1], True, m[2]),
                lambda: select_face(s, comp["uh"], ends["uh"][-1][1], True, m[3])), width_option=width_centred))
            tries[f"width ({label})"] = tries.pop("width")
            if "width" in made:
                made["width"] = made["width"] + (label,)
        attempt("gear on an app gear", lambda: (lambda k: (k, s.mate_status(k)))(
            s.add_mate("ge", "gear", "ue:Gear Axis", "sun:Gear Axis", 0.0, "UserGearOnSun", ratio=(20.0, 29.0))[0]))
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        names = [v[0] for v in made.values()] + ["UserAxisB", "UserAxisC", "UserAxisD", "UserAxisE"]
        for i, n in enumerate(names):
            s.find_mate(f"n{i}", n)
            if modes:
                s.set_mate_suppressed_in(f"n{i}", False, modes)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        return {"made": {k: list(v) for k, v in made.items()}, "tries": tries,
                "faces": {h: [(k, r) for k, r, _ in fs] for h, fs in faces.items()}}
    return work


def m1_read(modes, folder, names):
    """The reads, each between two GetSaveFlag reads of every document of the copy: mate_info, flags per mode, the
    definition, the codes."""
    def work(s):
        before = W.folder_flags(s, folder)
        states = {m.name: (m.code, m.suppressed) for m in s.mate_states()}
        out = {}
        for i, n in enumerate(names):
            s.find_mate(f"r{i}", n)
            info = s.mate_info(f"r{i}")
            out[n] = {"mate_info": {"type": info.type, "components": list(info.components), "whole": info.counted},
                      "flags": s.mate_suppression(f"r{i}", modes) if modes else {}, "code": states.get(n),
                      "definition": mate_definition(s, s._mate_feature(n))}  # noqa: SLF001
        after = W.folder_flags(s, folder)
        return {"mates": out, "flags_before": before, "flags_after": after}
    return work


def section_m1(out):
    say("== m1  the user-mate kinds W9a left unread (plan, Changes after W9a's demonstration): concentric, limit "
        "distance, limit angle, width and a user gear mate on an app gear, each on its own user component in a copy "
        "of RangeBox; read by the app's mate_info and a quiet press; GetSaveFlag around every read. Path is not made "
        "(it needs a sketch path the app has no route for); the sub-assembly leaf is p2's")
    swconst(ENUM_NAMES)
    new("AddMate5 with swMateCONCENTRIC on a face and an axis (the ledger: face-to-axis concentric verified for "
        "MateEntity order on 2026 and 2024, made by a probe, not the app), swMateWIDTH (no entry; the selection marks "
        "are tried two ways and said), limit distance and limit angle (AddMate5's upper and lower values; the ledger "
        "reads a limit's range back on IMate2, 'an inference from a handful of mates'), and a part face selected "
        "through IComponent2.GetCorresponding (verified for a feature only)")
    parts = A.user_parts()
    folder, path, book, desk = A.copy_desk(A.rangebox_master(), "m1", "RangeBox.xlsx")
    try:
        import shutil
        for name in ("Sprocket.SLDPRT", "Housing.SLDPRT"):
            shutil.copy2(os.path.join(parts, name), os.path.join(folder, name))
        box = desk.record.gearbox
        modes = list(box.modes)
        refs = {"lay": box.layout_component, "sun": dict(W.bodies(box))["Sun"]}
        A.add_user_work("m1", desk, folder, M1_INSERTS, (), fixed=("uh",), refs=refs)

        def make(s):
            for h, _, _, n in M1_INSERTS:
                s.find_component(h, n)
            for h, n in refs.items():
                s.find_component(h, n)
            return m1_mates(modes)(s)
        made = out["made"] = run("m1: the mates made", job(box.assembly, make), 900)
        for kind, answer in made["tries"].items():
            say(f"fact    m1 {kind}: {answer}")
        names = [v[0] for v in made["made"].values()]
        read = out["read"] = run("m1: the reads", job(box.assembly, m1_read(modes, folder, names)), 600)
        marked = flags_changed(read["flags_before"], read["flags_after"])
        check(not marked, f"m1: the reads (mate_info, flags, definition, codes) marked no document: {marked or 'none'}")
        for kind, (name, status, *rest) in made["made"].items():
            m = read["mates"][name]
            say(f"fact    m1 {kind} ({name}, AddMate5 status {status}{', ' + rest[0] if rest and rest[0] else ''}): "
                f"mate_info {m['mate_info']}; flags {m['flags']}; code {m['code']}; definition "
                f"{ {k: v for k, v in m['definition'].items() if k != 'entities'} }; entities "
                f"{m['definition'].get('entities')}")
        say("-- m1  a quiet press records the inventory; then Sun's Backlash typed, and the footer's judgement")
        ahead = A.quiet_then_edit("m1", desk, book, 0.4)
        entry = desk.record.gearbox.user_work
        inventory = {m.name: m for m in (entry.mates if entry is not None else [])}
        problems = [p.sentence for p in (ahead.problems if ahead is not None else [])]
        out["judged"] = {}
        for kind, (name, *_rest) in made["made"].items():
            named = [p for p in problems if name in p]
            out["judged"][kind] = {"in_inventory": name in inventory, "named_by_judgement": named}
            say(f"fact    m1 {kind}: in the recorded inventory {name in inventory}"
                f"{' as ' + repr(inventory[name]) if name in inventory else ''}; named by the footer's judgement "
                f"{named or 'no'}")
        for kind, (name, *_rest) in made["made"].items():
            m = read["mates"][name]
            say(propose(f"M1_READS_{kind.upper().replace(' ', '_')}",
                        bool(m["mate_info"]["whole"]) and all(c is not None for c in m["mate_info"]["components"]),
                        f"m1: mate_info {m['mate_info']}, no document marked {not marked}"))
        for kind in ("concentric", "limit distance", "limit angle", "width", "gear on an app gear"):
            if kind not in made["made"]:
                say(propose(f"M1_READS_{kind.upper().replace(' ', '_')}", None,
                            f"m1: not made: {[v for k, v in made['tries'].items() if k.startswith(kind)]}"))
    finally:
        end(folder, "m1")


# -- s5: W9d's spike ---------------------------------------------------------------------------------------------------


def s5_read(folder, user_names):
    """(a, b, c) Every user mate's definition, and for each entity on a part's feature its part-level persistent
    reference (read in the component's part, resolved there again) and the assembly-context route tried beside it;
    the assembly's own planes by tree order; frames of every component a user mate touches; GetSaveFlag around."""
    def work(s):
        doc = s._doc()  # noqa: SLF001
        before = W.folder_flags(s, folder)
        planes = [str(call(p, "Name")) for p in s._planes(doc)]  # noqa: SLF001
        mates = {}
        touched = set()
        for name in user_names:
            d = mate_definition(s, s._mate_feature(name))  # noqa: SLF001
            whole = {0, ENUMS["swSelectType_e"].get("swSelCOMPONENTS", -1)}
            for e in d.get("entities", []):
                touched.add(e["component"])
                e["whole"] = e["reference_type"] in whole
                if e["whole"]:
                    e["feature"] = None
                    continue
                if not e["component"]:
                    e["tree_order"] = planes.index(e["feature"]) + 1 if e["feature"] in planes else None
                    continue
                if not e["feature"]:
                    continue
                component = swcom.Session._component_by(findings.COMPONENT_FIND_ROUTE, doc, e["component"])  # noqa: SLF001
                part = call(component, "GetModelDoc2")
                feature = call(part, "FeatureByName", e["feature"])
                try:
                    ref = bytes(raw(call(part, "Extension"), "GetPersistReference3", feature))
                    back = raw(call(part, "Extension"), "GetObjectByPersistReference3", ref,
                               swcom._out_long())  # noqa: SLF001
                    back = back[0] if isinstance(back, tuple) else back
                    e["persist"] = {"part_level": ref.hex(), "length": len(ref),
                                    "resolves_to": str(call(back, "Name")) if back is not None else None}
                except Exception as exc:  # noqa: BLE001
                    e["persist"] = {"part_level": None, "error": f"{type(exc).__name__}: {exc}"}
                try:        # the route the plan calls unverified: the assembly-context feature, in the assembly
                    asm_ref = bytes(raw(call(doc, "Extension"), "GetPersistReference3",
                                        call(component, "FeatureByName", e["feature"])))
                    e["persist"]["assembly_context_length"] = len(asm_ref)
                except Exception as exc:  # noqa: BLE001
                    e["persist"]["assembly_context"] = f"{type(exc).__name__}: {exc}"
            mates[name] = d
        frames = {}
        for i, n in enumerate(sorted(c for c in touched if c)):
            s.find_component(f"t{i}", n)
            frames[n] = s.component_frame(f"t{i}")
        after = W.folder_flags(s, folder)
        return {"mates": mates, "frames": frames, "planes": planes, "flags_before": before, "flags_after": after,
                "paths": {n: swcom.Session._component_path(swcom.Session._component_by(  # noqa: SLF001
                    findings.COMPONENT_FIND_ROUTE, doc, n)) for n in frames}}
    return work


def s5_remake(read, second, layout_name):
    """The second assembly: a new one from the default template, saved as ``second``; every component a user mate
    touches inserted from the same file at the frame it stood at and the app's fixed; each user mate made again by
    AddMate5 from its read definition on entities found by the part-level reference (user and app parts alike, the
    same files), by name (the layout's axes), by tree order (the assembly's own planes) or whole (a lock)."""
    def work(s):
        s.new_assembly()
        s.save_as(second)
        doc = s._doc()  # noqa: SLF001
        names = {}
        order = sorted(read["frames"], key=lambda n: (n != layout_name, n))
        for i, n in enumerate(order):
            path = read["paths"][n]
            s.open_document(path)
            call(s._app, "ActivateDoc3", call(doc, "GetTitle"), False, 0, swcom._out_long())  # noqa: SLF001
            s._build_doc = doc  # noqa: SLF001
            kept = s.add_component(f"c{i}", path, tuple(read["frames"][n][1]))
            s.place_component(f"c{i}", tuple(read["frames"][n][0]), tuple(read["frames"][n][1]),
                              kind=swcom.ASSEMBLY_TRAIN)
            names[n] = (f"c{i}", kept)
            if not n.startswith("Sprocket"):          # the layout, the app's gears and the user's housing, fixed
                s.fix_component(f"c{i}")             # as they stand (the housing is fixed in setup.master too)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        results = {}
        for mate, d in read["mates"].items():
            picks, why = [], []
            for position, e in enumerate(d.get("entities", [])):
                append = position > 0
                if not e["component"]:
                    order_ = e.get("tree_order")
                    picks.append(lambda o=order_, a=append: s._component_ref(f"asm:plane{o}", a))  # noqa: SLF001
                    why.append(f"the assembly's plane {order_} by tree order")
                elif not e["feature"]:
                    handle = names[e["component"]][0]

                    def whole(h=handle, a=append):
                        data = call(call(doc, "SelectionManager"), "CreateSelectData")
                        swcom._put(data, "Mark", 1)  # noqa: SLF001
                        call(s._component(h), "Select4", a, data, False)  # noqa: SLF001
                    picks.append(whole)
                    why.append(f"{e['component']} whole")
                elif e["component"] == layout_name:
                    handle = names[e["component"]][0]
                    picks.append(lambda h=handle, f=e["feature"], a=append: s._component_ref(f"{h}:{f}", a))  # noqa: SLF001
                    why.append(f"the layout's {e['feature']} by name")
                else:
                    handle = names[e["component"]][0]

                    def by_reference(h=handle, e_=e, a=append):
                        r = bytes.fromhex((e_.get("persist") or {}).get("part_level") or "")
                        if not r:
                            raise swcom.SolidWorksError(f"no part-level reference was read for {e_['feature']}")
                        component = s._component(h)  # noqa: SLF001
                        part = call(component, "GetModelDoc2")
                        got = raw(call(part, "Extension"), "GetObjectByPersistReference3", r,
                                  swcom._out_long())  # noqa: SLF001
                        got = got[0] if isinstance(got, tuple) else got
                        target = call(component, "GetCorresponding", got)
                        data = call(call(doc, "SelectionManager"), "CreateSelectData")
                        swcom._put(data, "Mark", 1)  # noqa: SLF001
                        call(target, "Select4", a, data)
                    picks.append(by_reference)
                    why.append(f"{e['component']}'s {e['feature']} by its part-level reference")
            values = d.get("values") or {}
            distance = float(values.get("Distance") or next((v for n, v in d["dimensions"]), 0.0) or 0.0) \
                if d.get("type") == findings.MATE_DISTANCE else 0.0
            angle = float(values.get("Angle") or next((v for n, v in d["dimensions"]), 0.0) or 0.0) \
                if d.get("type") == findings.MATE_ANGLE else 0.0
            try:
                call(doc, "ClearSelection2", True)
                for pick in picks:
                    pick()
                before = s._mate_names()  # noqa: SLF001
                made, status = s._add_mate5(d.get("type"), d.get("alignment") or 0, bool(d.get("flipped")),  # noqa: SLF001
                                            distance, distance, distance, 1, 1, angle, angle, angle, False, False, 0)
                call(doc, "ClearSelection2", True)
                new_names = [n for n in s._mate_names() if n not in before]  # noqa: SLF001
                if made is None or len(new_names) != 1:
                    raise swcom.SolidWorksError(f"AddMate5 made no mate (status {status})")
                kept = s._rename(s._mate_feature(new_names[0]), mate)  # noqa: SLF001
                results[mate] = {"status": status, "how": why, "kept": kept}
            except Exception as exc:  # noqa: BLE001 - what failed is the finding
                call(doc, "ClearSelection2", True)
                results[mate] = {"error": f"{type(exc).__name__}: {exc}", "how": why}
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        remade = {m: mate_definition(s, s._mate_feature(m)) for m, r in results.items() if "kept" in r}  # noqa: SLF001
        frames = {}
        for n, (handle, kept) in names.items():
            s.find_component(f"g{handle}", kept)
            frames[n] = s.component_frame(f"g{handle}")
        states = {m.name: (m.code, m.suppressed) for m in s.mate_states()}
        return {"results": results, "remade": remade, "frames": frames, "names": {n: k for n, (_, k) in names.items()},
                "states": states}
    return work


def s5_states(folder, target, modes, suppressed_in):
    """(e) ``target`` suppressed in ``suppressed_in`` (shown there, SetSuppression2, rebuilt, the first mode shown
    again); then, nothing shown, each candidate route read, GetSaveFlag around each; then the truth, each mode shown
    and its fresh component's GetSuppression2 read."""
    def work(s):
        doc = s._doc()  # noqa: SLF001
        st = ENUMS["swComponentSuppressionState_e"]
        suppressed = next(v for k, v in st.items() if k.endswith("Suppressed"))
        first = s.active_configuration()
        s.show_configuration(suppressed_in)
        component = swcom.Session._component_by(findings.COMPONENT_FIND_ROUTE, doc, target)  # noqa: SLF001
        set_to = call(component, "SetSuppression2", suppressed)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        s.show_configuration(first)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        call(doc, "Save3", 1, swcom._out_long(), swcom._out_long())  # noqa: SLF001 - the probe's own copy, so the
        # candidates start from an unmarked document
        out = {"set": repr(set_to), "candidates": {}, "flags": {}}
        specify = ENUMS["swInConfigurationOpts_e"].get("swSpecifyConfiguration", 3)

        def candidate(label, fn):
            before = W.folder_flags(s, folder)
            try:
                out["candidates"][label] = fn()
            except Exception as exc:  # noqa: BLE001
                out["candidates"][label] = f"{type(exc).__name__}: {exc}"
            out["flags"][label] = flags_changed(before, W.folder_flags(s, folder))

        def feature_route():
            feature = call(doc, "FeatureByName", target)
            answers = raw(feature, "IsSuppressed2", specify, swcom.Session._names(modes))  # noqa: SLF001
            return dict(zip(modes, [bool(a) for a in swcom._per_name(answers)]))  # noqa: SLF001

        def configuration_route():
            out_ = {}
            for mode in modes:
                configuration = call(doc, "GetConfigurationByName", mode)
                root = raw(configuration, "GetRootComponent3", True)
                children = list(raw(root, "GetChildren") or [])
                found = next((c for c in children if str(call(c, "Name2")) == target), None)
                out_[mode] = None if found is None else int(raw(found, "GetSuppression2"))
            return out_
        candidate("component feature IsSuppressed2(swSpecifyConfiguration, names)", feature_route)
        candidate("IConfiguration.GetRootComponent3(True) per configuration, GetSuppression2", configuration_route)
        truth, shown_flags = {}, {}
        for mode in modes:
            s.show_configuration(mode)
            fresh = swcom.Session._component_by(findings.COMPONENT_FIND_ROUTE, doc, target)  # noqa: SLF001
            truth[mode] = int(raw(fresh, "GetSuppression2"))
        s.show_configuration(first)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        out["truth"] = truth
        return out
    return work


def s5_read_only(path, docs_type, options):
    """(d) ``OpenDoc6(path, assembly, Silent | ReadOnly)``: what it returns, its errors and warnings, whether the
    document says it is read-only, its GetSaveFlag."""
    def work(s):
        got = call(s._app, "OpenDoc6", path, docs_type, options, "", swcom._out_long(), swcom._out_long())  # noqa: SLF001
        doc = got[0] if isinstance(got, tuple) else got
        out = {"returned": "a document" if doc is not None else None,
               "extra": [_plain(v) for v in got[1:]] if isinstance(got, tuple) else None}
        if doc is not None:
            out.update(read_only=_plain(_try(doc, "IsOpenedReadOnly")), save_flag=bool(call(doc, "GetSaveFlag")),
                       title_is_the_runs=True)
        return out
    return work


def section_s5(out):
    say("== s5  W9d's spike (plan §4 S5): (a) every user mate's definition read and (b, c) remade by AddMate5 in a "
        "second assembly on entities found by reference, name, tree order or whole component, then compared; (e) a "
        "component's state per configuration read unshown; (d) the assembly opened read-only; (f) GetSaveFlag "
        "around every read")
    swconst(ENUM_NAMES)
    new("IModelDocExtension.GetPersistReference3 on a part-level feature reached through a component, and "
        "GetObjectByPersistReference3 in that part (the ledger: both 'verified, SW 2026' on a part's own feature, "
        "curves/10; never through a component, never on 2024); IComponent2.GetCorresponding on the resolved feature "
        "(verified for a feature, tier 7/8); OpenDoc6 with swOpenDocOptions_ReadOnly (no entry; reading/08 advises "
        "it, unmeasured); IFeature.IsSuppressed2 on a component's feature and IConfiguration.GetRootComponent3 per "
        "configuration (no entry for either use)")
    folder, path, book, desk = A.copy_desk(A.user_master(), "s5", "RangeBox.xlsx")
    second_folder = os.path.join(OUT, "s5-second")
    try:
        box = desk.record.gearbox
        modes = list(box.modes)
        # (c)'s tree-order case needs a user mate to the assembly's own plane: one more sprocket, its axis on the
        # layout's and its Front plane 200 mm from the assembly's first base plane.
        refs = {"lay": box.layout_component}
        A.add_user_work("s5", desk, folder, (("u6", "Sprocket.SLDPRT", (0.0, 0.0, 200.0), "Sprocket-5"),),
                        (("x6", "coincident", "u6:Gear Axis", "lay:Input Axis", 0.0, "UserAxis6", {}),
                         ("d6", "distance", "u6:plane1", "asm:plane1", 200.0, "UserAsm6", {})), refs=refs)
        users = list(A.RB_USER_MATES) + ["UserAxis6", "UserAsm6"]
        read = out["read"] = run("s5 (a-c): the user mates read", job(box.assembly, s5_read(folder, users)), 900)
        marked = flags_changed(read["flags_before"], read["flags_after"])
        check(not marked, f"s5 (f): the definitions and persistent references read marked no document: "
                          f"{marked or 'none'}")
        for name, d in read["mates"].items():
            say(f"fact    s5 (a) {name}: {d['type_name']} type {d.get('type')} alignment {d.get('alignment')} flipped "
                f"{d.get('flipped')} variation {d.get('variation')} values {d.get('values')} dimensions "
                f"{d.get('dimensions')}; entities {d.get('entities')}")
        os.makedirs(second_folder, exist_ok=True)
        second = os.path.join(second_folder, "S5Second.SLDASM")
        remade = out["remade"] = run("s5 (a-c): the mates made again in a second assembly",
                                     in_build(s5_remake(read, second, box.layout_component)), 900)
        for name, r in remade["results"].items():
            if "kept" not in r:
                say(f"fact    s5 {name}: not made again ({r['error']}); entities by {r['how']}")
                continue
            differ = same_definition(read["mates"][name], remade["remade"][name])
            say(f"fact    s5 {name}: made again, AddMate5 status {r['status']}, entities by {r['how']}; code "
                f"{remade['states'].get(name)}; definition differs {differ or 'nowhere'}")
        moved = {n: frame_gap(read["frames"][n], remade["frames"].get(n)) for n in read["frames"]}
        say(f"fact    s5: each component in the second assembly against where it stood in the first: "
            f"{ {n: round(v, 9) for n, v in moved.items()} }")
        ok = [n for n, r in remade["results"].items() if "kept" in r
              and not same_definition(read["mates"][n], remade["remade"][n])]
        say(propose("MATE_REMAKE_FROM_DEFINITION_ROUTE", "AddMate5 from IMate2 Type, Alignment, Flipped and the "
                    "definition's values" if len(ok) == len(remade["results"]) else None,
                    f"s5: remade equal {ok} of {sorted(remade['results'])}"))
        persisted = [e.get("persist", {}) for d in read["mates"].values() for e in d.get("entities", [])
                     if e.get("persist")]
        say(propose("PERSIST_REFERENCE_ROUTE", "GetPersistReference3 on the part-level feature, through the "
                    "component's GetModelDoc2" if persisted and all(p.get("part_level") for p in persisted) else None,
                    f"s5 (b): {len(persisted)} entities read, resolved in their part {[p.get('resolves_to') for p in persisted]}"))

        say("-- s5 (e)  a component's state per configuration, read without showing")
        target = "Sprocket-4"
        states = out["states"] = run("s5 (e)", job(box.assembly, s5_states(folder, target, modes, modes[-1])), 900)
        for label, value in states["candidates"].items():
            truth = {m: v for m, v in states["truth"].items()}
            if label.startswith("component feature"):
                suppressed = next(v for k, v in ENUMS["swComponentSuppressionState_e"].items()
                                  if k.endswith("Suppressed"))
                truth = {m: v == suppressed for m, v in truth.items()}
            verdict = state_agrees(value, truth) if isinstance(value, dict) else {"agrees": False, "differ": value}
            say(f"fact    s5 (e) {label}: {value}; against the truth shown {states['truth']}: {verdict}; marked "
                f"{states['flags'][label] or 'nothing'}")
            states.setdefault("verdicts", {})[label] = verdict
        agreeing = [label for label, v in states["verdicts"].items() if v["agrees"]
                    and not states["flags"][label]]
        say(propose("COMPONENT_STATE_PER_CONFIGURATION_ROUTE", agreeing[0] if agreeing else None,
                    f"s5 (e): agreeing and marking nothing: {agreeing or 'none'}"))

        left = run("s5: the second assembly closed unsaved", W.quit_in(second_folder))
        say(f"fact    s5: the second assembly closed unsaved before (d): left {left}")
        say("-- s5 (d)  the assembly opened read-only, already open and then not open")
        options = ENUMS["swOpenDocOptions_e"]["swOpenDocOptions_Silent"] | ENUMS["swOpenDocOptions_e"][
            "swOpenDocOptions_ReadOnly"]
        doc_type = ENUMS["swDocumentTypes_e"]["swDocASSEMBLY"]
        new(f"OpenDoc6 with swOpenDocOptions_ReadOnly (options {options})")
        try:
            opened, _ = watched("s5 (d) read-only, already open", s5_read_only(box.assembly, doc_type, options))
            say(f"fact    s5 (d) already open: {opened}")
            left = run("s5 (d): closed unsaved", W.quit_in(folder))
            say(f"fact    s5 (d): the copy closed without saving to open it again: left {left}")
            opened2, _ = watched("s5 (d) read-only, not open", s5_read_only(box.assembly, doc_type, options))
            say(f"fact    s5 (d) not open: {opened2}")
            out["read_only"] = {"already_open": opened, "not_open": opened2}
            say(propose("OPEN_READ_ONLY_ROUTE", "OpenDoc6(path, assembly, Silent | ReadOnly)"
                        if opened2.get("read_only") is True and not opened2.get("save_flag") else None,
                        f"s5 (d): not open {opened2}, already open {opened}"))
        except CaseStop as exc:
            out["read_only"] = {"dialog": str(exc)}
            say(f"STOP    s5 (d): {exc}")
            say(propose("OPEN_READ_ONLY_DIALOG", True, "s5 (d)"))
    finally:
        end(folder, "s5")
        if os.path.isdir(second_folder) and not W.HUNG["on"]:
            run("s5: the second assembly closed unsaved", W.quit_in(second_folder))


# -- p2: a user sub-assembly inserted by its file --------------------------------------------------------------------


def p2_make_sub(folder, part, sub):
    """A user sub-assembly made here: a new assembly, ``part`` (opened first) inserted at the origin and fixed,
    saved as ``sub``, then everything under ``folder`` closed."""
    def work(s):
        s.open_document(part)
        s.new_assembly()
        s.add_component("p", part, (0.0, 0.0, 0.0))
        s.save_as(sub)
        return W.quit_in(folder)(s)
    return work


def p2_insert(host, sub, modes, layout):
    """``sub`` opened (OpenDoc6, as the ledger says a component must be), the host made active, the sub-assembly
    inserted (AddComponent5), its leaf found, a coincident mate made from the leaf's Gear Axis to the layout's Input
    Axis, and read: the leaf's Name2, mate_info, flags."""
    def work(s):
        s.open_document(sub)
        s.open_document(host)
        doc = s._doc()  # noqa: SLF001
        s.find_component("lay", layout)
        kept = s.add_component("sub", sub, (0.0, 0.0, 250.0))
        top = s._component("sub")  # noqa: SLF001
        children = list(raw(top, "GetChildren") or [])
        leaf = children[0] if children else None
        out = {"inserted": kept, "children": [str(call(c, "Name2")) for c in children],
               "flag": bool(call(doc, "GetSaveFlag"))}
        if leaf is None:
            return out
        feature = call(call(leaf, "GetModelDoc2"), "FeatureByName", "Gear Axis")
        target = call(leaf, "GetCorresponding", feature)
        call(doc, "ClearSelection2", True)
        data = call(call(doc, "SelectionManager"), "CreateSelectData")
        swcom._put(data, "Mark", 1)  # noqa: SLF001
        call(target, "Select4", False, data)
        s._component_ref("lay:Input Axis", True)  # noqa: SLF001
        before = s._mate_names()  # noqa: SLF001
        made, status = s._add_mate5(findings.MATE_COINCIDENT, findings.MATE_ALIGN_CLOSEST, False, 0.0, 0.0, 0.0,  # noqa: SLF001
                                    1, 1, 0.0, 0.0, 0.0, False, False, 0)
        call(doc, "ClearSelection2", True)
        new_names = [n for n in s._mate_names() if n not in before]  # noqa: SLF001
        out["mate"] = {"status": status, "made": new_names}
        if new_names:
            name = s._rename(s._mate_feature(new_names[0]), "UserLeafAxis")  # noqa: SLF001
            s.find_mate("leaf", name)
            if modes:
                s.set_mate_suppressed_in("leaf", False, modes)
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            info = s.mate_info("leaf")
            out["mate"].update(info={"type": info.type, "components": list(info.components)},
                               flags=s.mate_suppression("leaf", modes) if modes else {},
                               code={m.name: m.code for m in s.mate_states()}.get(name))
        return out
    return work


def p2_missing(sub):
    def work(s):
        got = call(s._app, "OpenDoc6", sub, ENUMS["swDocumentTypes_e"]["swDocASSEMBLY"],  # noqa: SLF001
                   ENUMS["swOpenDocOptions_e"]["swOpenDocOptions_Silent"], "", swcom._out_long(),  # noqa: SLF001
                   swcom._out_long())  # noqa: SLF001
        doc = got[0] if isinstance(got, tuple) else got
        return {"returned": "a document" if doc is not None else None,
                "extra": [_plain(v) for v in got[1:]] if isinstance(got, tuple) else None}
    return work


def section_p2(out):
    say("== p2  a user sub-assembly inserted by its file (opened first), a mate to its leaf read; then one with a "
        "missing reference among its own files: a 'find file' dialog is the finding. Last: it may leave the session "
        "unusable")
    swconst(ENUM_NAMES)
    new("AddComponent5 of an assembly file (the app inserts parts only; the ledger's 'not open returns None' is for a "
        "part), IComponent2.GetChildren on it, a mate to a leaf through GetCorresponding, and OpenDoc6 of an assembly "
        "whose part file is missing")
    import shutil
    parts = A.user_parts()
    root = W.fresh_folder("p2-parts")
    good, missing = os.path.join(root, "P2Sprocket.SLDPRT"), os.path.join(root, "P2Missing.SLDPRT")
    shutil.copy2(os.path.join(parts, "Sprocket.SLDPRT"), good)
    shutil.copy2(os.path.join(parts, "Sprocket.SLDPRT"), missing)
    sub, sub_missing = os.path.join(root, "UserSub.SLDASM"), os.path.join(root, "UserSubMissing.SLDASM")
    left = run("p2: the user's sub-assembly made", in_build(p2_make_sub(root, good, sub)), 600)
    left2 = run("p2: the sub-assembly whose part will go missing made",
                in_build(p2_make_sub(root, missing, sub_missing)), 600)
    os.remove(missing)
    say(f"fact    p2: UserSub.SLDASM (P2Sprocket) and UserSubMissing.SLDASM made and closed (left {left}, {left2}); "
        "P2Missing.SLDPRT deleted from disk")
    folder, path, book, desk = A.copy_desk(A.rangebox_master(), "p2", "RangeBox.xlsx")
    try:
        box = desk.record.gearbox
        modes = list(box.modes)
        try:
            got, _ = watched("p2 the sub-assembly inserted",
                             in_build(p2_insert(box.assembly, sub, modes, box.layout_component)))
            out["insert"] = got
            say(f"fact    p2 insert: {got}")
            say(propose("SUBASSEMBLY_INSERT_ROUTE", "OpenDoc6 the sub-assembly, then AddComponent5" if got.get(
                "inserted") else None, f"p2: {got.get('inserted')}, children {got.get('children')}"))
            info = (got.get("mate") or {}).get("info") or {}
            say(propose("M1_READS_SUBASSEMBLY_LEAF", any("/" in str(c) for c in info.get("components", []))
                        if info else None, f"p2: the leaf mate's mate_info {info}"))
        except CaseStop as exc:
            out["insert"] = {"dialog": str(exc)}
            say(f"STOP    p2 insert: {exc}")
        try:
            got, dialogs = watched("p2 the sub-assembly with a missing part opened", p2_missing(sub_missing))
            out["missing"] = got
            say(f"fact    p2 missing reference: {got}, no dialog")
            say(propose("SUBASSEMBLY_MISSING_REFERENCE_DIALOG", False, f"p2: OpenDoc6 returned {got}"))
        except CaseStop as exc:
            out["missing"] = {"dialog": str(exc)}
            say(f"STOP    p2 missing reference: {exc}")
            say(propose("SUBASSEMBLY_MISSING_REFERENCE_DIALOG", True, "p2: a dialog came and went"))
    finally:
        end(folder, "p2")
        if not W.HUNG["on"]:
            run("p2: the sub-assemblies closed", W.quit_in(root))


# -- the run -------------------------------------------------------------------------------------------------------------

ORDER = ["p1", "m1", "s5", "p2"]
SECTIONS = {"p1": section_p1, "m1": section_m1, "s5": section_s5, "p2": section_p2}
FOLDERS = {"p1": [f"p1-{i}-{route}" for i, (_, _, route) in enumerate(P1_CASES, 1)], "m1": ["m1"],
           "s5": ["s5", "s5-second"], "p2": ["p2", "p2-parts"]}


def done_here(name):
    return [p for p in (os.path.join(OUT, f) for f in FOLDERS.get(name, [name])) if os.path.exists(p)]


def main():
    A.SECTIONS.clear()
    A.SECTIONS.update(SECTIONS)
    if A._given in ("", "all"):                    # noqa: SLF001
        A.CHOSEN = list(ORDER)
    A.done_here = done_here
    A.RUN_TITLE, A.JSON_STEM = "W9c probes", "w9c-probes"
    return A.main()


if __name__ == "__main__":
    code = 1
    try:
        code = main()
    finally:
        with open(W.LOG_PATH, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(W.LOG) + "\n")
    raise SystemExit(code)
