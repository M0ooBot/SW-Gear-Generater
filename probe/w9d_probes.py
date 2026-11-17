r"""W9d's probes on SolidWorks: the readings W9D-INTERFACES.md §11 owes before W9d's packages rely on them, and the calls
it adds that the app has never made and that could raise a dialog or change a document (ISSUE-1-PLAN §2.5, §4 S5,
the last section's "Owed before W9d is designed"). Nothing of W9d exists in the app: these measure the calls its
packages would make, and propose findings in the log without setting any. The note is
``docs/notes-workbook/W9D-PROBES.md``; revised to the review ``W9D-INTERFACES-REVIEW.md`` (P1-P13).

python.exe probe/w9d_probes.py <repo src> <output folder under C:\> --pid PID [--log FILE]
                               [--sections faces,state,sub|all] [--user-master DIR] [--master DIR] [--redo]
python probe/w9d_probes.py --self-check      (no SolidWorks: the pure judgements, on made-up readings)
python probe/w9d_probes.py --help

``--user-master``: W9a's ``setup.master`` for this SolidWorks version (RangeBox with the user's work); ``--master``:
S0's ``rangebox.master`` (needed only when setup.master must be built here first, by W9a's own builders).

Sections, in this order (each runs alone; ``sub``, whose insert of a read-only document is the likeliest to raise a
dialog, goes last):

- ``faces``  a face's and an edge's persistent reference (W9D-INTERFACES §11.4): on a copy of setup.master, three more
             sprockets and four mates on faces and an edge (a concentric on a bore face, a coincident face to face, a
             concentric on a circular edge, a parallel to a face of Sun), the copy then saved so the reads start
             unmarked (P1); (b) each entity's ReferenceType2 and kind, its component, its coaxial read, and two routes
             to the part-level reference, each resolved and carried back and compared, with each user component's
             referenced configuration, IsVirtual and IsPatternInstance; (c) the four made again in a second assembly,
             the route per entity kind (P10), the copy's documents' flags read around the inserts; (d) the copy
             closed, the parts opened alone and every reference resolved again (the reload, P12).
- ``state``  a component's state per configuration without marking the assembly (§11.1), the file's last saved
             version read closed, and the read-only open of an assembly whose documents are open (§11.2): on a copy of
             setup.master, Housing-1 suppressed in H and Sprocket-4 in L, saved (the probe's own copy); three candidate
             routes read with nothing shown, GetSaveFlag around each, judged only from an unmarked start (P4); the
             truth by showing; an unsaved change read (P6); the root read with a lightweight component, as facts (P7);
             then the copy closed, VersionHistory read, a sprocket part opened and changed and the housing part opened
             unchanged (P2), the assembly opened read-only beside them, read, its modes shown, and closed unsaved under
             the watch, what it loaded checked gone (P3).
- ``sub``    whether opening a healthy user sub-assembly marks it (§11.3): not loaded, opened read-only then inserted,
             and loaded as a component of an open assembly; each step's dialog caught and said (P9); the host made by
             the app's own save route only (P8).

**A dialog is a finding, not a failure.** Every call that may raise one runs under W9c's watch (W9c probes'
``watched``: logs class, caption, buttons and texts, never SolidWorks' frame title, never answers). A job that does
not return, or a dialog that stays, ends the run with nothing closed or saved. Nothing of the user's is touched: every
document here is a copy in this run's folder, closed unsaved at the end; the only saves are of the probe's own copies
(``Save3``, as W9c's s5 (e) did, so the reads start unmarked) and of assemblies this script makes (``save_as``, the
app's own route). No document title but the run's own is logged.
"""

import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SELF_CHECK = "--self-check" in sys.argv

if "--help" in sys.argv or "-h" in sys.argv:
    print(__doc__)
    raise SystemExit(0)


# -- pure judgements (no SolidWorks; --self-check runs them) --------------------------------------------------------

FRAME_TOL = 1e-6           # mm and rotation entries
AREA_TOL = 1e-12           # m²: a face carried back is the face read
AXIS_TOL = 1e-9            # m and direction components: a cylinder's axis on the part's Z axis
SAME = "swObjectSame"      # swObjectEquality's member for "the same object" (read from swconst.tlb at run time)


def flags_changed(before, after):
    """Documents (by file name) whose GetSaveFlag turned on between two reads."""
    return sorted(n for n, f in after.items() if f and not before.get(n))


def marked_at_start(before):
    """Documents already marked when a bracket began: a bracket that starts with any cannot see a mark on them."""
    return sorted(n for n, f in before.items() if f)


def first_marking(steps):
    """The first step of a sequence whose read turned a document's flag on: ``steps`` is ``[(label, before, after)]``
    (flags dicts); ``(label, documents)`` or None when no step marked anything."""
    for label, before, after in steps:
        marked = flags_changed(before, after)
        if marked:
            return label, marked
    return None


def state_verdict(candidate, truth):
    """A candidate's per-mode reads against the shown truth, both ``{component: {mode: suppressed bool}}``: the
    (component, mode) pairs that differ or were not read, and whether it agrees everywhere."""
    differ = {}
    for name, modes in truth.items():
        for mode, value in modes.items():
            got = (candidate.get(name) or {}).get(mode, "unread")
            if got != value:
                differ[f"{name} in {mode}"] = (got, value)
    return {"agrees": not differ and bool(truth), "differ": differ}


def route_proposal(verdicts, marks, labels, clean_start=True):
    """The first candidate (in ``labels`` order) that agrees with the truth and marked nothing, or None; None too when
    the bracket did not start unmarked (P4: a mark could not have shown)."""
    if not clean_start:
        return None
    for label in labels:
        if (verdicts.get(label) or {}).get("agrees") and not marks.get(label):
            return label
    return None


def entity_kind(answers):
    """A mate entity's kind from which members its reference answered: ``{"surface": bool, "curve": bool, "point":
    bool}`` -> face, edge, vertex, or unread (none, or more than one)."""
    kinds = [k for k, member in (("face", "surface"), ("edge", "curve"), ("vertex", "point")) if answers.get(member)]
    return kinds[0] if len(kinds) == 1 else "unread"


def kind_of_select_type(value, select_enum):
    """W9D-INTERFACES §2.2's classification by ReferenceType2 (swSelectType_e read from swconst.tlb)."""
    names = {v: k for k, v in (select_enum or {}).items()}
    return {"swSelFACES": "face", "swSelEDGES": "edge", "swSelVERTICES": "vertex", "swSelDATUMAXES": "feature",
            "swSelDATUMPLANES": "feature", "swSelCOMPONENTS": "whole", "swSelDATUMPOINTS": "origin",
            "swSelEXTSKETCHPOINTS": "origin"}.get(names.get(value), "whole" if value == 0 else "unread")


def coaxial(params):
    """A cylinder's ``CylinderParams`` (origin x, y, z, axis x, y, z, radius; part coordinates, metres): whether its
    axis is the line through the origin along Z, which every recipe's Gear Axis is. None when not seven numbers."""
    if not params or len(params) < 7:
        return None
    ox, oy, _, ax, ay, az = (float(v) for v in params[:6])
    return abs(ox) <= AXIS_TOL and abs(oy) <= AXIS_TOL and abs(ax) <= AXIS_TOL and abs(ay) <= AXIS_TOL \
        and abs(abs(az) - 1.0) <= AXIS_TOL


def persist_verdict(route):
    """One route's read of one geometry entity: ``{"read": bool, "resolved_kind": str, "kind": str, "same": int|None,
    "same_value": int, "area": (a, b) or None, "error": str}``. Clean when the reference was read, resolved to the
    entity's own kind, and the round trip is the same object (IsSame) or, where IsSame did not answer, the same area."""
    if not route or route.get("error") or not route.get("read"):
        return False, (route or {}).get("error") or "no reference read"
    if route.get("resolved_kind") != route.get("kind"):
        return False, f"resolved to a {route.get('resolved_kind')} where a {route.get('kind')} was read (§0.3 STOP)"
    same = route.get("same")
    if same is not None and route.get("same_value") is not None:
        return (same == route.get("same_value"), f"IsSame {same}")
    area = route.get("area")
    if area and None not in area:
        return (abs(area[0] - area[1]) <= AREA_TOL, f"areas {area}")
    return False, "neither IsSame nor an area answered"


def route_for(entities, kind, routes):
    """The first route (in ``routes`` order) clean on every entity of ``kind``, or None (also when none was read)."""
    of_kind = [e for e in entities if e.get("kind") == kind]
    if not of_kind:
        return None
    for route in routes:
        if all(persist_verdict((e.get("routes") or {}).get(route))[0] for e in of_kind):
            return route
    return None


def persist_proposal(entities, kind, routes, start_marked):
    """``route_for``, but None when the read's bracket started with a document marked (P1)."""
    return None if start_marked else route_for(entities, kind, routes)


def reload_verdict(entities):
    """P12: every face and edge reference resolved again after the copy was closed and its parts opened alone, to its
    own kind (and a face to its own area). ``entities``: each with ``kind``, ``area`` and ``reload`` (``{"kind",
    "area", "error"}``)."""
    bad = []
    for e in entities:
        r = e.get("reload") or {}
        if r.get("error") or r.get("kind") != e.get("kind"):
            bad.append((e.get("component"), e.get("kind"), r))
        elif e.get("kind") == "face" and (r.get("area") is None or e.get("area") is None
                                          or abs(r["area"] - e["area"]) > AREA_TOL):
            bad.append((e.get("component"), "face area", r.get("area"), e.get("area")))
    return bool(entities) and not bad, bad


def same_definition(read, remade, tol=1e-9):
    """What differs between a mate's definition as read and as remade (W9c probes' rule)."""
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


def last_saved(history):
    """``ISldWorks.VersionHistory``'s answer (a list of ``"14000[2021/85]"``, or one string joined by ``|``), oldest
    first: ``(file version, release year)`` of its last entry, or None."""
    items = list(history) if isinstance(history, (list, tuple)) else str(history or "").split("|")
    items = [str(i).strip() for i in items if str(i).strip()]
    if not items:
        return None
    m = re.match(r"(\d+)\s*\[(\d{4})", items[-1])
    return (int(m.group(1)), int(m.group(2))) if m else None


def read_only_close_verdict(d):
    """The not-open path (§11.1, §11.2): the job's read-only document shown mode by mode and closed unsaved. Clean when
    no dialog came, the document is gone after the close, every document it loaded is gone too (P3), every file's time
    is as before, and every document that was open before it is as it was: the changed part still open, changed and
    not read-only, the unchanged part still open, unmarked and not read-only (P2)."""
    why = []
    if d.get("dialogs"):
        why.append(f"dialogs {d['dialogs']}")
    if d.get("left_open"):
        why.append("the read-only document is still open after QuitDoc")
    if d.get("loaded_left"):
        why.append(f"documents it loaded still open {d['loaded_left']}")
    if d.get("times_changed"):
        why.append(f"file times changed {d['times_changed']}")
    for name, (want, state) in (d.get("others") or {}).items():
        if state != want:
            why.append(f"{name}: {state}, where {want}")
    return not why, why


def keeps_open_documents(before, after):
    """§11.2: each document open before the read-only open (``{name: {"open", "flag", "read_only"}}``) is as it was."""
    changed = {n: (s, after.get(n)) for n, s in before.items() if after.get(n) != s}
    return not changed, changed


def sub_marks(flag_before, flag_after):
    """A sub-assembly's open or insert: True when it turned the sub-assembly's flag on, False when it stayed off, None
    when it was already on or was not read (nothing can be said)."""
    if flag_before or flag_after is None:
        return None
    return bool(flag_after)


def propose(name, value, evidence):
    """A finding proposed in ``findings.py``'s style, never set."""
    return f"propose {name} = {value!r}  # {evidence}"


def self_check():
    bad = []

    def ok(cond, what):
        print(("ok      " if cond else "FAIL    ") + what)
        if not cond:
            bad.append(what)

    ok(flags_changed({"A": False, "B": True}, {"A": True, "B": True}) == ["A"], "a read that marked A is said")
    ok(marked_at_start({"A": False, "B": True}) == ["B"], "a bracket starting with B marked is said")
    steps = [("GetConfigurationByName", {"X": False}, {"X": False}), ("GetRootComponent3(True)", {"X": False},
                                                                       {"X": True}), ("GetChildren", {"X": True}, {"X": True})]
    ok(first_marking(steps) == ("GetRootComponent3(True)", ["X"]), "the first call that marks is named")
    ok(first_marking(steps[:1]) is None, "no call marked: None")
    truth = {"Housing-1": {"H": True, "N": False, "L": False}, "Sprocket-4": {"H": False, "N": False, "L": True}}
    ok(state_verdict(truth, truth)["agrees"], "a route reading the truth agrees")
    v = state_verdict({"Housing-1": {"H": True, "N": False, "L": False}, "Sprocket-4": {"H": False, "N": False}}, truth)
    ok(not v["agrees"] and "Sprocket-4 in L" in v["differ"], "a mode not read is a difference")
    v = state_verdict({"Housing-1": {"H": False, "N": False, "L": False}, "Sprocket-4": truth["Sprocket-4"]}, truth)
    ok(not v["agrees"] and v["differ"] == {"Housing-1 in H": (False, True)}, "the mode showing read wrong is said")
    ok(not state_verdict({}, {})["agrees"], "no truth: no agreement")
    verdicts = {"a": {"agrees": True}, "b": {"agrees": True}, "c": {"agrees": False}}
    ok(route_proposal(verdicts, {"a": ["RangeBox.SLDASM"], "b": []}, ["a", "b", "c"]) == "b",
       "a route that marked is passed over for the next clean one")
    ok(route_proposal(verdicts, {"a": ["x"], "b": ["x"]}, ["a", "b", "c"]) is None, "no clean route: None")
    ok(route_proposal(verdicts, {}, ["a"], clean_start=False) is None, "P4: a marked start proposes nothing")
    ok(entity_kind({"surface": True}) == "face" and entity_kind({"curve": True}) == "edge"
       and entity_kind({"point": True}) == "vertex", "entity kinds from the members that answered")
    ok(entity_kind({}) == "unread" and entity_kind({"surface": True, "curve": True}) == "unread",
       "nothing, or two members answering, is unread")
    sel = {"swSelFACES": 2, "swSelEDGES": 1, "swSelVERTICES": 3, "swSelDATUMAXES": 5, "swSelDATUMPLANES": 4,
           "swSelCOMPONENTS": 20}
    ok([kind_of_select_type(t, sel) for t in (2, 1, 3, 5, 4, 20, 0, 99)] ==
       ["face", "edge", "vertex", "feature", "feature", "whole", "whole", "unread"], "ReferenceType2 classifies")
    ok(coaxial([0, 0, 0.003, 0, 0, 1, 0.005]) is True and coaxial([0.005, 0, 0, 0, 0, 1, 0.0015]) is False
       and coaxial([0, 0, 0, 1, 0, 0, 0.005]) is False and coaxial([]) is None,
       "coaxial: a bore on Z yes, an off-axis hole or another axis no, nothing read None")
    good = {"read": True, "kind": "face", "resolved_kind": "face", "same": 1, "same_value": 1}
    ok(persist_verdict(good)[0], "a reference read, resolved to a face and IsSame: clean")
    ok(not persist_verdict(dict(good, resolved_kind="edge"))[0] and "STOP" in persist_verdict(
        dict(good, resolved_kind="edge"))[1], "a face resolving to an edge is the §0.3 STOP")
    ok(not persist_verdict(dict(good, same=0))[0], "IsSame answering not the same: not clean")
    ok(persist_verdict(dict(good, same=None, area=(1e-4, 1e-4)))[0], "IsSame unanswered, the same area: clean")
    ok(persist_verdict(dict(good, same_value=None, area=(1e-4, 1e-4)))[0],
       "swObjectEquality unread: the area decides")
    ok(not persist_verdict(dict(good, same=None, area=(1e-4, 2e-4)))[0], "IsSame unanswered, another area: not clean")
    ok(not persist_verdict({"error": "ComError"})[0] and not persist_verdict(None)[0], "an error or nothing: not clean")
    edge = dict(good, kind="edge", resolved_kind="edge")
    entities = [{"kind": "face", "routes": {"r1": good, "r2": dict(good, read=False)}},
                {"kind": "face", "routes": {"r1": good, "r2": good}},
                {"kind": "edge", "routes": {"r1": dict(edge, read=False), "r2": edge}}]
    ok(route_for(entities, "face", ["r2", "r1"]) == "r1", "a route clean on every face is proposed")
    ok(route_for(entities, "edge", ["r1", "r2"]) == "r2", "P10: the edge's route is its own")
    ok(route_for(entities, "vertex", ["r1"]) is None, "no vertex read: None")
    ok(persist_proposal(entities, "face", ["r1"], start_marked=True) is None, "P1: a marked start proposes nothing")
    rel = [{"component": "S-5", "kind": "face", "area": 1e-4, "reload": {"kind": "face", "area": 1e-4}},
           {"component": "S-6", "kind": "edge", "reload": {"kind": "edge"}}]
    ok(reload_verdict(rel)[0], "P12: references resolved again after a reload")
    ok(not reload_verdict([dict(rel[0], reload={"error": "None"})])[0] and not reload_verdict([])[0],
       "P12: one not resolved, or nothing read, is not clean")
    read = {"type_name": "MateConcentric", "type": 1, "alignment": 0, "flipped": False, "values": {"MateAlignment": 0}}
    ok(same_definition(read, dict(read)) == [], "a definition remade the same compares equal")
    ok(same_definition(read, dict(read, flipped=True)) == ["flipped False -> True"], "a flip remade otherwise is said")
    ok(last_saved(["11000[2018/134]", "14000[2021/85]"]) == (14000, 2021), "VersionHistory: the last entry")
    ok(last_saved("11000[2018/134] | 14000[2021/85]") == (14000, 2021) and last_saved([]) is None,
       "VersionHistory: one joined string, and nothing")
    housing = {"open": True, "flag": False, "read_only": False}
    sprocket = {"open": True, "flag": True, "read_only": False}
    clean = {"dialogs": [], "left_open": False, "loaded_left": [], "times_changed": {},
             "others": {"Sprocket.SLDPRT": (sprocket, sprocket), "Housing.SLDPRT": (housing, housing)}}
    ok(read_only_close_verdict(clean)[0], "a clean close of the read-only document")
    ok(not read_only_close_verdict(dict(clean, dialogs=["Save changes?"]))[0], "a dialog on the close is not clean")
    ok(not read_only_close_verdict(dict(clean, others={"Housing.SLDPRT": (housing, dict(housing, flag=True))}))[0],
       "P2: the unchanged part marked is not clean")
    ok(not read_only_close_verdict(dict(clean, loaded_left=["Gear_m1.25_N29.SLDPRT"]))[0],
       "P3: a document the open loaded and the close left is not clean")
    ok(not read_only_close_verdict(dict(clean, times_changed={"RangeBox.SLDASM": (1.0, 2.0)}))[0],
       "a file time changed is not clean")
    ok(keeps_open_documents({"H": housing}, {"H": dict(housing)})[0], "documents open before are as they were")
    ok(not keeps_open_documents({"H": housing}, {"H": dict(housing, read_only=True)})[0],
       "a document made read-only by the open is said")
    ok(sub_marks(False, True) is True and sub_marks(False, False) is False and sub_marks(True, True) is None
       and sub_marks(False, None) is None, "a sub-assembly's open: marks, does not, or cannot be told")
    ok(propose("X_ROUTE", "a b", "line") == "propose X_ROUTE = 'a b'  # line", "propose's form")
    print(f"done    {len(bad)} failed")
    return 0 if not bad else 1


if SELF_CHECK:
    raise SystemExit(self_check())


# -- the live run: W9a's harness, through W9c's probes ------------------------------------------------------------

sys.path.insert(0, HERE)
import w9c_probes as C  # noqa: E402  (W9a's harness, the watch, swconst, mate_definition, select_face, raw_mate)

A, W = C.A, C.W
from gear_generator import findings, swcom  # noqa: E402
from gear_generator.swcom import call  # noqa: E402

say, check = W.say, W.check
OUT = W.OUT
run, job, raw, _try, _plain, part, new = C.run, C.job, C.raw, C._try, C._plain, C.part, C.new  # noqa: SLF001
EXTRA = {}                 # enumerations beyond the W9c probes' set, each optional


def enums():
    """W9c's enumerations (positive control included), then this probe's own, each optional: one swconst.tlb lacks
    is said and its reads fall back."""
    got = C.swconst(C.ENUM_NAMES)
    if EXTRA:
        return got
    import pythoncom
    import win32api
    import win32con
    import win32process
    handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, W.PID)
    try:
        exe = win32process.GetModuleFileNameEx(handle, 0)
    finally:
        win32api.CloseHandle(handle)
    lib = pythoncom.LoadTypeLib(os.path.join(os.path.dirname(exe), "swconst.tlb"))
    wanted = ("swObjectEquality", "swPersistReferencedObjectStates_e")
    for index in range(lib.GetTypeInfoCount()):
        name = lib.GetDocumentation(index)[0]
        if name in wanted:
            info = lib.GetTypeInfo(index)
            EXTRA[name] = {str(info.GetNames(info.GetVarDesc(i).memid)[0]): int(info.GetVarDesc(i).value)
                           for i in range(info.GetTypeAttr().cVars)}
    say(f"fact    swconst.tlb: this probe's own enumerations read {sorted(EXTRA)}; missing "
        f"{sorted(set(wanted) - set(EXTRA)) or 'none'}")
    EXTRA.setdefault("_read", {})
    return got


def comp(doc, name):
    return swcom.Session._component_by(findings.COMPONENT_FIND_ROUTE, doc, name)  # noqa: SLF001


def by_ref(value):
    try:
        return int(getattr(value, "value", value))
    except (TypeError, ValueError):
        return None


def doc_states(s, folder):
    """Every open document under ``folder``, by file name: open, its save flag, whether opened read-only."""
    out = {}
    for d in W.documents(s._app):  # noqa: SLF001
        path = str(call(d, "GetPathName") or "")
        if W.under(path, folder):
            out[os.path.basename(path)] = {"open": True, "flag": bool(call(d, "GetSaveFlag")),
                                           "read_only": bool(_try(d, "IsOpenedReadOnly"))}
    return out


def file_times(folder):
    return {n: os.path.getmtime(os.path.join(folder, n)) for n in sorted(os.listdir(folder))
            if os.path.isfile(os.path.join(folder, n)) and n.upper().endswith((".SLDPRT", ".SLDASM"))}


def save_copy(s, folder):
    """The probe's own copy saved in place (``Save3`` silent, as W9c's s5 (e)), so a bracket after it starts unmarked;
    every document of the copy's flags after."""
    call(s._doc(), "Save3", 1, swcom._out_long(), swcom._out_long())  # noqa: SLF001
    return W.folder_flags(s, folder)


def part_edges_of(component):
    """The circular edges of a component's part, each with its radius and centre z (mm, part coordinates)."""
    part_doc = call(component, "GetModelDoc2")
    out = []
    for body in list(raw(part_doc, "GetBodies2", 0, True) or []):
        for edge in list(raw(body, "GetEdges") or []):
            curve = raw(edge, "GetCurve")
            if curve is not None and raw(curve, "IsCircle"):
                p = [float(v) for v in raw(curve, "CircleParams")]
                out.append((round(p[6] * 1000.0, 6), round(p[2] * 1000.0, 6), edge))
    return out


def kind_of(obj):
    return entity_kind({"surface": _try(obj, "GetSurface") is not None, "curve": _try(obj, "GetCurve") is not None,
                        "point": _try(obj, "GetPoint") is not None})


# -- faces: a face's and an edge's persistent reference (§11.4), the referenced configuration, the reload --------------

FACE_INSERTS = (("f5", "Sprocket.SLDPRT", (0.0, 0.0, 200.0), "Sprocket-5"),
                ("f6", "Sprocket.SLDPRT", (0.0, 0.0, 206.0), "Sprocket-6"),
                ("f7", "Sprocket.SLDPRT", (0.0, 0.0, 230.0), "Sprocket-7"))
FACE_MATES = ("UserFaceConc", "UserFaceCoin", "UserEdgeConc", "UserSunPar")
ROUTES = {"r1": "IModelDocExtension.GetCorrespondingEntity2 on the mate's entity in the assembly, then the part's "
                "GetPersistReference3 (NEW)",
          "r2": "the mate's entity handed straight to the part's GetPersistReference3 (NEW)"}


def faces_make(modes, folder):
    """The four mates on faces and an edge, made by AddMate5 on selections through GetCorresponding (m1's route),
    each set on in every mode and read back; then the copy saved (P1)."""
    def work(s):
        mt = C.ENUMS["swMateType_e"]
        c = {h: s._component(h) for h in ("f5", "f6", "f7", "sun")}  # noqa: SLF001
        faces = {h: C.part_faces_of(c[h]) for h in ("f5", "f6", "f7", "sun")}
        edges = part_edges_of(c["f6"])
        bore5 = next(f for k, r, f in faces["f5"] if k == "cylinder" and abs(r - 5.0) < 1e-6)
        ends = {h: sorted(((z, f) for k, z, f in faces[h] if k == "plane" and z is not None), key=lambda t: t[0])
                for h in faces}
        edge6 = max((e for e in edges if abs(e[0] - 5.0) < 1e-6), key=lambda e: e[1])[2]
        made, tries = {}, {}

        def attempt(name, fn):
            try:
                made[name] = fn()
                tries[name] = "made"
            except Exception as exc:  # noqa: BLE001 - what SolidWorks answered is the reading
                tries[name] = f"{type(exc).__name__}: {exc}"
                call(s._doc(), "ClearSelection2", True)  # noqa: SLF001
        attempt("UserFaceConc", lambda: C.raw_mate(s, "UserFaceConc", mt["swMateCONCENTRIC"], (
            lambda: C.select_face(s, c["f5"], bore5, False, 1),
            lambda: s._component_ref("lay:Input Axis", True))))  # noqa: SLF001
        attempt("UserFaceCoin", lambda: C.raw_mate(s, "UserFaceCoin", mt["swMateCOINCIDENT"], (
            lambda: C.select_face(s, c["f5"], ends["f5"][-1][1], False, 1),
            lambda: C.select_face(s, c["f6"], ends["f6"][0][1], True, 1))))
        attempt("UserEdgeConc", lambda: C.raw_mate(s, "UserEdgeConc", mt["swMateCONCENTRIC"], (
            lambda: C.select_face(s, c["f6"], edge6, False, 1),
            lambda: s._component_ref("lay:Input Axis", True))))  # noqa: SLF001
        attempt("UserSunPar", lambda: C.raw_mate(s, "UserSunPar", mt["swMatePARALLEL"], (
            lambda: C.select_face(s, c["f7"], ends["f7"][-1][1], False, 1),
            lambda: C.select_face(s, c["sun"], ends["sun"][-1][1], True, 1))))
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        flags = {}
        for i, name in enumerate(made):
            s.find_mate(f"fm{i}", name)
            if modes:
                s.set_mate_suppressed_in(f"fm{i}", False, modes)
                flags[name] = s.mate_suppression(f"fm{i}", modes)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        states = {m.name: (m.code, m.suppressed) for m in s.mate_states()}
        saved = save_copy(s, folder)
        return {"tries": tries, "flags": flags, "states": {n: states.get(n) for n in made}, "after_save": saved}
    return work


def faces_read(folder, app_names, users):
    """Each mate's definition; each geometry entity's ReferenceType2 and kind, what its reference names as its
    component, its coaxial read (a cylinder's CylinderParams on the part-level face), and each route to the part-level
    reference, resolved in the part, carried back through the component and compared (IsSame, the area); the
    assembly-context reference's length beside it (read only); each user component's ReferencedConfiguration, its
    document's active configuration, IsVirtual and IsPatternInstance (NEW gets); GetSaveFlag of every document
    around, and which were already marked at the start (P1)."""
    def work(s):
        doc = s._doc()  # noqa: SLF001
        app = s._app  # noqa: SLF001
        before = W.folder_flags(s, folder)
        same_value = (EXTRA.get("swObjectEquality") or {}).get(SAME)
        select_enum = C.ENUMS.get("swSelectType_e", {})
        mates = {}
        for name in FACE_MATES:
            try:
                feature = s._mate_feature(name)  # noqa: SLF001
            except Exception as exc:  # noqa: BLE001 - a mate not made is said; the others still read
                mates[name] = {"error": f"{type(exc).__name__}: {exc}"}
                continue
            d = C.mate_definition(s, feature)
            mate = _try(feature, "GetSpecificFeature2")
            for i, e in enumerate(d.get("entities", [])):
                e["select_kind"] = kind_of_select_type(e.get("reference_type"), select_enum)
                if e.get("reference") != "geometry":
                    continue
                entity = call(mate, "MateEntity", i)
                ref = _try(entity, "Reference")
                e["kind"] = kind_of(ref)
                owner = _try(ref, "GetComponent")
                e["entity_component"] = _plain(_try(owner, "Name2")) if owner is not None else None
                e["area"] = _plain(_try(ref, "GetArea")) if e["kind"] == "face" else None
                component = comp(doc, e["component"])
                part_doc = call(component, "GetModelDoc2") if component is not None else None
                e["routes"] = {}
                if part_doc is None:
                    e["routes"]["error"] = f"{e['component']} has no document loaded"
                    continue
                ext = call(part_doc, "Extension")
                try:
                    part_entity = raw(call(doc, "Extension"), "GetCorrespondingEntity2", ref)
                    surface = _try(part_entity, "GetSurface") if e["kind"] == "face" else None
                    if surface is not None and raw(surface, "IsCylinder"):
                        e["coaxial"] = coaxial([float(v) for v in raw(surface, "CylinderParams")])
                    elif surface is not None:
                        e["coaxial"] = False
                except Exception as exc:  # noqa: BLE001 - the coaxial read's failure is its reading
                    e["coaxial"] = f"{type(exc).__name__}: {exc}"

                def route(get_ref):
                    out = {"kind": e["kind"], "same_value": same_value}
                    try:
                        r = bytes(get_ref())
                        out.update(read=True, length=len(r), reference=r.hex())
                    except Exception as exc:  # noqa: BLE001 - this route's failure is its reading
                        out.update(read=False, error=f"{type(exc).__name__}: {exc}")
                        return out
                    try:
                        code = swcom._out_long()  # noqa: SLF001
                        got = raw(ext, "GetObjectByPersistReference3", r, code)
                        if isinstance(got, tuple):
                            got, code = got[0], (got[1] if len(got) > 1 else code)
                        out["resolve_code"] = by_ref(code)
                        out["resolved_kind"] = kind_of(got)
                        back = call(component, "GetCorresponding", got)
                        try:
                            out["same"] = int(raw(app, "IsSame", ref, back))
                        except Exception as exc:  # noqa: BLE001 - IsSame unanswered: the area decides
                            out["same"], out["same_error"] = None, f"{type(exc).__name__}: {exc}"
                        if e["kind"] == "face":
                            out["area"] = (_plain(_try(ref, "GetArea")), _plain(_try(back, "GetArea")))
                    except Exception as exc:  # noqa: BLE001
                        out["error"] = f"resolving: {type(exc).__name__}: {exc}"
                    return out
                e["routes"]["r1"] = route(lambda: raw(ext, "GetPersistReference3",
                                                      raw(call(doc, "Extension"), "GetCorrespondingEntity2", ref)))
                e["routes"]["r2"] = route(lambda: raw(ext, "GetPersistReference3", ref))
                try:
                    e["assembly_context_length"] = len(bytes(raw(call(doc, "Extension"), "GetPersistReference3", ref)))
                except Exception as exc:  # noqa: BLE001
                    e["assembly_context_length"] = f"{type(exc).__name__}: {exc}"
            mates[name] = d
        components = {}
        for n in users:
            c = comp(doc, n)
            if c is None:
                components[n] = "not found"
                continue
            model = _try(c, "GetModelDoc2")
            active = _try(_try(model, "GetActiveConfiguration"), "Name") if model is not None else None
            components[n] = {"referenced": _plain(_try(c, "ReferencedConfiguration")), "active": _plain(active),
                             "virtual": _plain(_try(c, "IsVirtual")), "pattern": _plain(_try(c, "IsPatternInstance")),
                             "path": os.path.basename(str(_try(c, "GetPathName") or ""))}
        frames, paths = {}, {}
        for i, n in enumerate(app_names + [w for _, _, _, w in FACE_INSERTS]):
            s.find_component(f"t{i}", n)
            frames[n] = s.component_frame(f"t{i}")
            paths[n] = s.component_path(f"t{i}")
        return {"mates": mates, "components": components, "frames": frames, "paths": paths, "flags_before": before,
                "flags_after": W.folder_flags(s, folder)}
    return work


def faces_remake(read, second, folder, layout, sun, routes):
    """The four mates made again in a second assembly (S5 (c)'s way): the layout, Sun and the three sprockets inserted
    from the same files at their frames, the layout and Sun fixed; each geometry entity found by its kind's route
    (``routes``: kind -> route, P10), resolved in the new instance's part and carried through GetCorresponding; the
    layout's axis by name. GetSaveFlag of every document under the copy's folder read before the inserts, after them
    and after the mates."""
    def work(s):
        flags_before = W.folder_flags(s, folder)
        s.new_assembly()
        s.save_as(second)
        doc = s._doc()  # noqa: SLF001
        handles = {}
        for i, n in enumerate([layout, sun] + [w for _, _, _, w in FACE_INSERTS]):
            path = read["paths"][n]
            s.open_document(path)
            call(s._app, "ActivateDoc3", call(doc, "GetTitle"), False, 0, swcom._out_long())  # noqa: SLF001
            s._build_doc = doc  # noqa: SLF001
            s.add_component(f"c{i}", path, tuple(read["frames"][n][1]))
            s.place_component(f"c{i}", tuple(read["frames"][n][0]), tuple(read["frames"][n][1]),
                              kind=swcom.ASSEMBLY_TRAIN)
            if n in (layout, sun):
                s.fix_component(f"c{i}")
            handles[n] = f"c{i}"
        flags_inserted = W.folder_flags(s, folder)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        results = {}
        for name, d in read["mates"].items():
            if d.get("error"):
                results[name] = {"error": f"not made: {d['error']}"}
                continue
            try:
                call(doc, "ClearSelection2", True)
                for position, e in enumerate(d.get("entities", [])):
                    append = position > 0
                    if e.get("reference") == "feature" and e.get("component") == layout:
                        s._component_ref(f"{handles[layout]}:{e['feature']}", append)  # noqa: SLF001
                        continue
                    route = routes.get(e.get("kind"))
                    r = ((e.get("routes") or {}).get(route) or {}).get("reference") if route else None
                    if not r:
                        raise swcom.SolidWorksError(f"no clean route for {e.get('component')}'s {e.get('kind')}")
                    component = s._component(handles[e["component"]])  # noqa: SLF001
                    part_doc = call(component, "GetModelDoc2")
                    got = raw(call(part_doc, "Extension"), "GetObjectByPersistReference3", bytes.fromhex(r),
                              swcom._out_long())  # noqa: SLF001
                    got = got[0] if isinstance(got, tuple) else got
                    if got is None:
                        raise swcom.SolidWorksError(f"the {route} reference resolved to nothing")
                    C.select_face(s, component, got, append, 1)
                before = s._mate_names()  # noqa: SLF001
                made, status = s._add_mate5(d.get("type"), d.get("alignment") or 0, bool(d.get("flipped")),  # noqa: SLF001
                                            0.0, 0.0, 0.0, 1, 1, 0.0, 0.0, 0.0, False, False, 0)
                call(doc, "ClearSelection2", True)
                new_names = [n for n in s._mate_names() if n not in before]  # noqa: SLF001
                if made is None or len(new_names) != 1:
                    raise swcom.SolidWorksError(f"AddMate5 made no mate (status {status})")
                results[name] = {"status": status, "kept": s._rename(s._mate_feature(new_names[0]), name)}  # noqa: SLF001
            except Exception as exc:  # noqa: BLE001 - what failed is the reading
                call(doc, "ClearSelection2", True)
                results[name] = {"error": f"{type(exc).__name__}: {exc}"}
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        remade = {n: C.mate_definition(s, s._mate_feature(n)) for n, r in results.items() if "kept" in r}  # noqa: SLF001
        frames = {}
        for n, h in handles.items():
            s.find_component(f"g{h}", call(s._component(h), "Name2"))  # noqa: SLF001
            frames[n] = s.component_frame(f"g{h}")
        states = {m.name: (m.code, m.suppressed) for m in s.mate_states()}
        return {"results": results, "remade": remade, "frames": frames, "states": states,
                "flags_before": flags_before, "flags_inserted": flags_inserted,
                "flags_after": W.folder_flags(s, folder)}
    return work


def faces_reload(entities, paths):
    """P12: the copy closed; each part an entity is on opened alone (its own document, freshly loaded) and each face
    and edge reference resolved there again: its kind and a face's area."""
    def work(s):
        out = {}
        for e in entities:
            r = None
            for route in ("r1", "r2"):
                got = (e.get("routes") or {}).get(route) or {}
                if got.get("read") and got.get("reference"):
                    r = got["reference"]
                    break
            key = f"{e.get('component')}:{e.get('kind')}:{(r or '')[:16]}"
            if not r:
                out[key] = {"error": "no reference read in (b)"}
                continue
            try:
                s.open_document(paths[e["component"]])
                ext = call(s._doc(), "Extension")  # noqa: SLF001
                got = raw(ext, "GetObjectByPersistReference3", bytes.fromhex(r), swcom._out_long())  # noqa: SLF001
                got = got[0] if isinstance(got, tuple) else got
                out[key] = {"error": "resolved to nothing"} if got is None else {
                    "kind": kind_of(got), "area": _plain(_try(got, "GetArea")) if e.get("kind") == "face" else None}
            except Exception as exc:  # noqa: BLE001
                out[key] = {"error": f"{type(exc).__name__}: {exc}"}
            e["reload"] = out[key]
        return out
    return work


def section_faces(out):
    say("== faces  a face's and an edge's persistent reference (W9D-INTERFACES §11.4): four mates on faces and an "
        "edge on a copy of setup.master, saved; each entity read by two routes to its part-level reference, resolved "
        "and carried back; each user component's referenced configuration; then made again in a second assembly; "
        "then every reference resolved after a reload; GetSaveFlag around every read and the inserts")
    C.swconst(C.ENUM_NAMES)
    enums()
    new("IModelDocExtension.GetCorrespondingEntity2 (the API help: the entity in the underlying part for one in the "
        "assembly, SOLIDWORKS 2018 on; never called by the app or the macro database); GetPersistReference3 and "
        "GetObjectByPersistReference3 on a face and an edge, and after a reload (the ledger: verified on a part's own "
        "feature only; the W9c probes on reference features through a component, in session); IEntity.GetComponent, "
        "ISldWorks.IsSame, ISurface.CylinderParams on a mate's face, IComponent2.ReferencedConfiguration (a get), "
        "IsVirtual and IsPatternInstance (no entry); AddMate5 swMatePARALLEL (never made or read by the app or a "
        "probe); Save3 on the probe's own copy (as W9c's s5 (e))")
    folder, path, book, desk = A.copy_desk(A.user_master(), "d-faces", "RangeBox.xlsx")
    second_folder = os.path.join(OUT, "d-faces-second")
    try:
        box = desk.record.gearbox
        modes = list(box.modes)
        sun = dict(W.bodies(box))["Sun"]
        refs = {"lay": box.layout_component, "sun": sun}
        users = [w for _, _, _, w in A.RB_INSERTS] + [w for _, _, _, w in FACE_INSERTS]
        A.add_user_work("faces", desk, folder, FACE_INSERTS, (), refs=refs)

        def make_part():
            def made(s):
                for h, _, _, n in FACE_INSERTS:
                    s.find_component(h, n)
                for h, n in refs.items():
                    s.find_component(h, n)
                return faces_make(modes, folder)(s)
            got = run("faces (a): the mates on faces and an edge, the copy saved", job(box.assembly, made), 900)
            for name, answer in got["tries"].items():
                say(f"fact    faces {name}: {answer}; flags {got['flags'].get(name)}; code {got['states'].get(name)}")
            bad = {n: st for n, st in got["states"].items() if st is None or (st[0] and not st[1])}
            check(not bad and len(got["states"]) == len(FACE_MATES),
                  f"faces: all four mates made, on in every mode and in no error: {bad or 'ok'}")
            still = marked_at_start(got["after_save"])
            check(not still, f"faces (a): the copy reads unmarked after its save: {still or 'every document'}")
            return got
        part(out, "made", "faces (a) the mates made", make_part)

        def read_part():
            read = run("faces (b): the entities read",
                       job(box.assembly, faces_read(folder, [box.layout_component, sun], users)), 900)
            start = marked_at_start(read["flags_before"])
            entities = []
            for name, d in read["mates"].items():
                if d.get("error"):
                    say(f"fact    faces (b) {name}: not read: {d['error']}")
                    continue
                say(f"fact    faces (b) {name}: {d.get('type_name')} type {d.get('type')} alignment {d.get('alignment')}"
                    f" flipped {d.get('flipped')} values {d.get('values')}")
                for i, e in enumerate(d.get("entities", [])):
                    if e.get("reference") != "geometry":
                        say(f"        entity {i}: {e.get('reference')} {e.get('feature')!r} on {e.get('component')!r}"
                            f" (ReferenceType2 {e.get('reference_type')} -> {e.get('select_kind')})")
                        continue
                    entities.append(e)
                    say(f"        entity {i}: {e.get('kind')} on {e.get('component')!r} (ReferenceType2 "
                        f"{e.get('reference_type')} -> {e.get('select_kind')}); its reference names "
                        f"{e.get('entity_component')!r}; area {e.get('area')}; coaxial {e.get('coaxial')}; "
                        f"assembly-context reference {e.get('assembly_context_length')}")
                    for label, r in (e.get("routes") or {}).items():
                        verdict = persist_verdict(r) if isinstance(r, dict) else (False, r)
                        say(f"          {label}: {verdict[0]} ({verdict[1]}): "
                            f"{ {k: v for k, v in r.items() if k != 'reference'} if isinstance(r, dict) else r}")
            say(f"fact    faces (b) the user's components: {read['components']}")
            marked = flags_changed(read["flags_before"], read["flags_after"])
            check(not marked, f"faces (b): the reads marked no document: {marked or 'none'}; already marked at the "
                              f"start {start or 'none'}")
            for kind, finding in (("face", "PERSIST_REFERENCE_ROUTE_FOR_FACES"),
                                  ("edge", "PERSIST_REFERENCE_ROUTE_FOR_EDGES")):
                chosen = persist_proposal(entities, kind, ["r1", "r2"], bool(start)) if not marked else None
                say(propose(finding, ROUTES[chosen] if chosen else None,
                            f"faces (b): {sum(1 for e in entities if e.get('kind') == kind)} {kind} entities; clean by "
                            f"{chosen or 'no route'}; marked {marked or 'nothing'}; marked at the start "
                            f"{start or 'nothing'}"))
            kinds_agree = all(e.get("select_kind") == e.get("kind") for e in entities)
            say(f"fact    faces (b): ReferenceType2's kind agrees with the members' on every geometry entity: "
                f"{kinds_agree}")
            faces = [e for e in entities if e.get("kind") == "face"]
            bore = [e.get("coaxial") for e in faces if e.get("component") == "Sprocket-5"]
            others = [e.get("coaxial") for e in faces if e.get("component") != "Sprocket-5"]
            say(propose("COAXIAL_FACE_READ", (True in bore and all(c is False for c in others))
                        if not (marked or start) else None,
                        f"faces (b): the bore read coaxial {bore}, the end faces {others}; marked "
                        f"{marked or 'nothing'}"))
            comps = [v for v in read["components"].values() if isinstance(v, dict)]
            say(propose("REFERENCED_CONFIGURATION_READ",
                        bool(comps) and all(isinstance(v["referenced"], str) and v["referenced"] for v in comps)
                        and not (marked or start) or None,
                        f"faces (b): each user component's referenced and active configuration "
                        f"{ {n: (v['referenced'], v['active']) for n, v in read['components'].items() if isinstance(v, dict)} }"))
            say(f"fact    faces (b): IsVirtual and IsPatternInstance answered on non-virtual, non-pattern components "
                f"only: { {n: (v['virtual'], v['pattern']) for n, v in read['components'].items() if isinstance(v, dict)} }"
                "; VIRTUAL_READ and PATTERN_INSTANCE_READ stay None until a run meets a positive case")
            read["entities"] = entities
            read["start_marked"] = start
            return read
        read = part(out, "read", "faces (b) the entities read", read_part, needs=("made",))

        os.makedirs(second_folder, exist_ok=True)
        second = os.path.join(second_folder, "D9Second.SLDASM")

        def remake_part():
            routes = {k: route_for(read["entities"], k, ["r1", "r2"]) for k in ("face", "edge")}
            if not any(routes.values()):
                raise AssertionError("no route read any face or edge clean, so nothing is made again")
            remade = run("faces (c): made again in a second assembly",
                         C.in_build(faces_remake(read, second, folder, box.layout_component, sun, routes)), 900)
            equal = []
            for name, r in remade["results"].items():
                if "kept" not in r:
                    say(f"fact    faces (c) {name}: not made again: {r['error']}")
                    continue
                differ = same_definition(read["mates"][name], remade["remade"][name])
                equal += [] if differ else [name]
                say(f"fact    faces (c) {name}: made again by {routes}, status {r['status']}, code "
                    f"{remade['states'].get(name)}; definition differs {differ or 'nowhere'}")
            moved = {n: C.frame_gap(f, remade["frames"].get(n)) for n, f in read["frames"].items()}
            say(f"fact    faces (c): each component against where it stood: { {n: round(v, 9) for n, v in moved.items()} }")
            start = marked_at_start(remade["flags_before"])
            inserted = flags_changed(remade["flags_before"], remade["flags_inserted"])
            after = flags_changed(remade["flags_before"], remade["flags_after"])
            say(f"fact    faces (c): the copy's documents marked by the inserts {inserted or 'none'}, by the mates "
                f"too {after or 'none'}; already marked before {start or 'none'}; remade equal {equal} of "
                f"{list(FACE_MATES)} (a fact: the remake's gate is CARRY_REMAKE_KINDS, M9's)")
            say(propose("CARRY_INSERT_MARKS_USER_DOCUMENTS", None if start else bool(inserted),
                        f"faces (c): a user part loaded as a component of the open assembly, inserted into another: "
                        f"marked {inserted or 'nothing'}; already marked before {start or 'nothing'}"))
            return remade
        part(out, "remade", "faces (c) made again", remake_part, needs=("read",))

        def reload_part():
            left = []
            if os.path.isdir(second_folder):          # first: it holds the copy's parts as its components
                left += run("faces (d): the second assembly closed unsaved", W.quit_in(second_folder))
            left += run("faces (d): the copy closed unsaved", W.quit_in(folder))
            if left:
                raise AssertionError(f"the copy did not close: left {left}")
            paths = {n: read["paths"].get(n) for n in {e.get("component") for e in read["entities"]}}
            got = run("faces (d): the references resolved after a reload", C.in_build(faces_reload(read["entities"],
                                                                                                paths)), 600)
            verdict = reload_verdict(read["entities"])
            say(f"fact    faces (d): resolved again in freshly loaded parts: {got}; {verdict}")
            say(propose("PERSIST_REFERENCE_SURVIVES_RELOAD", verdict[0] or None,
                        f"faces (d): {len(read['entities'])} face and edge references; not resolved {verdict[1] or 'none'}"))
            run("faces (d): the parts closed", W.quit_in(folder))
            return got
        part(out, "reload", "faces (d) the reload", reload_part, needs=("read",))
    finally:
        C.end(folder, "d-faces")
        if os.path.isdir(second_folder) and not W.HUNG["on"]:
            run("faces: the second assembly closed unsaved", W.quit_in(second_folder))


# -- state: a component's state per configuration, the file's version, the read-only open (§11.1, §11.2, §11.5) -------

STATE_TARGETS = {"Housing-1": "first", "Sprocket-4": "last"}   # suppressed in the first mode (showing) / the last


def suppress_in(doc, s, mode, name, suppressed_value):
    s.show_configuration(mode)
    c = comp(doc, name)
    if c is None:
        raise swcom.SolidWorksError(f"{name} was not found in {mode}")
    call(c, "SetSuppression2", suppressed_value)
    s.rebuild(kind=swcom.ASSEMBLY_TRAIN)


def truth_of(s, doc, modes, names, state_enum):
    """Each mode shown, each component found afresh and its GetSuppression2 read: {name: {mode: suppressed}}; the first
    mode shown again."""
    suppressed = next(v for k, v in state_enum.items() if k.endswith("Suppressed"))
    first = s.active_configuration()
    out = {n: {} for n in names}
    for mode in modes:
        s.show_configuration(mode)
        for n in names:
            c = comp(doc, n)
            out[n][mode] = None if c is None else int(raw(c, "GetSuppression2")) == suppressed
    s.show_configuration(first)
    s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
    return out


def candidate_1(doc, modes, names):
    """IConfiguration.GetComponentSuppressionState(Name2) per mode, nothing shown (NEW)."""
    out = {n: {} for n in names}
    for mode in modes:
        configuration = call(doc, "GetConfigurationByName", mode)
        for n in names:
            try:
                out[n][mode] = bool(raw(configuration, "GetComponentSuppressionState", n))
            except Exception as exc:  # noqa: BLE001 - one that will not answer is its reading
                out[n][mode] = f"{type(exc).__name__}: {exc}"
    return out


def candidate_2(doc, modes, names, state_enum):
    """IConfiguration.GetRootComponent3(False) per mode (the help: None for a configuration not active), and where a
    root answers, each child's GetSuppression2 (NEW with False)."""
    suppressed = next(v for k, v in state_enum.items() if k.endswith("Suppressed"))
    out = {n: {} for n in names}
    roots = {}
    for mode in modes:
        root = raw(call(doc, "GetConfigurationByName", mode), "GetRootComponent3", False)
        roots[mode] = None if root is None else _plain(_try(root, "Name2"))
        children = {str(call(c, "Name2")): c for c in list(raw(root, "GetChildren") or [])} if root is not None else {}
        for n in names:
            out[n][mode] = (int(raw(children[n], "GetSuppression2")) == suppressed) if n in children else "no root"
    return out, roots


def state_prepare(modes, folder):
    """Housing-1 suppressed in the first mode, Sprocket-4 in the last; the first shown again; the copy saved (the
    probe's own, so the reads start unmarked); Sprocket-4's mates' flags read unshown (§11.5's fact)."""
    def work(s):
        doc = s._doc()  # noqa: SLF001
        st = C.ENUMS["swComponentSuppressionState_e"]
        suppressed = next(v for k, v in st.items() if k.endswith("Suppressed"))
        first = s.active_configuration()
        suppress_in(doc, s, modes[0], "Housing-1", suppressed)
        suppress_in(doc, s, modes[-1], "Sprocket-4", suppressed)
        s.show_configuration(first)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        mates = {}
        for i, name in enumerate(("UserAxis4", "UserDist4", "UserAngle4")):
            s.find_mate(f"sm{i}", name)
            mates[name] = s.mate_suppression(f"sm{i}", modes)
        flags = save_copy(s, folder)
        return {"first": first, "mates_of_sprocket4": mates, "flags_after_save": flags}
    return work


def state_candidates(folder, modes, names):
    """Nothing shown: candidate 1, candidate 2, then candidate 3 (route 2 taken apart, call by call, for each mode not
    showing), each with every document's flag read before and after; the flags at the very start kept (P4); then the
    truth by showing."""
    def work(s):
        doc = s._doc()  # noqa: SLF001
        st = C.ENUMS["swComponentSuppressionState_e"]
        out = {"candidates": {}, "marks": {}, "steps": [], "first_marking": None,
               "start": W.folder_flags(s, folder)}

        def candidate(label, fn):
            before = W.folder_flags(s, folder)
            try:
                out["candidates"][label] = fn()
            except Exception as exc:  # noqa: BLE001
                out["candidates"][label] = f"{type(exc).__name__}: {exc}"
            out["marks"][label] = flags_changed(before, W.folder_flags(s, folder))
        candidate("GetComponentSuppressionState", lambda: candidate_1(doc, modes, names))
        candidate("GetRootComponent3(False)", lambda: candidate_2(doc, modes, names, st))
        active = s.active_configuration()
        for mode in [m for m in modes if m != active]:
            steps = []
            flags = W.folder_flags(s, folder)

            def step(label, fn):
                nonlocal flags
                value = fn()
                after = W.folder_flags(s, folder)
                steps.append((f"{mode}: {label}", flags, after))
                flags = after
                return value
            try:
                configuration = step("GetConfigurationByName", lambda: call(doc, "GetConfigurationByName", mode))
                root = step("GetRootComponent3(True)", lambda: raw(configuration, "GetRootComponent3", True))
                children = step("GetChildren", lambda: list(raw(root, "GetChildren") or []))
                named = step("Name2", lambda: {str(call(c, "Name2")): c for c in children})
                step("GetSuppression2", lambda: {n: int(raw(named[n], "GetSuppression2")) for n in names if n in named})
            except Exception as exc:  # noqa: BLE001
                steps.append((f"{mode}: raised {type(exc).__name__}: {exc}", flags, flags))
            out["steps"] += [(label, flags_changed(b, a)) for label, b, a in steps]
            if out["first_marking"] is None:                   # P5: kept only once one is found
                out["first_marking"] = first_marking(steps)
        out["truth"] = truth_of(s, doc, modes, names, st)
        return out
    return work


def state_unsaved(modes, name):
    """An unsaved change: ``name`` suppressed in the middle mode, not saved; candidate 1 read for it, then the truth."""
    def work(s):
        doc = s._doc()  # noqa: SLF001
        st = C.ENUMS["swComponentSuppressionState_e"]
        suppressed = next(v for k, v in st.items() if k.endswith("Suppressed"))
        first = s.active_configuration()
        middle = modes[len(modes) // 2]
        suppress_in(doc, s, middle, name, suppressed)
        s.show_configuration(first)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        return {"mode": middle, "read": candidate_1(doc, modes, [name]), "truth": truth_of(s, doc, modes, [name], st)}
    return work


def state_lightweight(name):
    """``name`` set lightweight in the mode showing (as W9a's ``lightweight`` did); candidate 1 read; then the active
    configuration's GetRootComponent3(False) and (True), every component's state read after each (facts only: the copy
    is marked by then, so no mark can show, P7); everything set resolved again before anything else."""
    def work(s):
        doc = s._doc()  # noqa: SLF001
        st = C.ENUMS["swComponentSuppressionState_e"]
        light = next(v for k, v in st.items() if k.endswith("Lightweight") and "Fully" not in k)
        resolved = next(v for k, v in st.items() if k.endswith("FullyResolved"))

        def states():
            return {c.name: c.state for c in s.components()}
        call(comp(doc, name), "SetSuppression2", light)
        out = {"set": states()}
        modes = [s.active_configuration()]
        out["candidate_1"] = candidate_1(doc, modes, [name])
        out["after_candidate_1"] = states()
        for resolve in (False, True):
            try:
                root = raw(raw(doc, "GetActiveConfiguration"), "GetRootComponent3", resolve)
                out[f"root({resolve})"] = None if root is None else _plain(_try(root, "Name2"))
            except Exception as exc:  # noqa: BLE001
                out[f"root({resolve})"] = f"{type(exc).__name__}: {exc}"
            out[f"after_root({resolve})"] = states()
        for n, state in states().items():
            if state in (1, 4):
                call(comp(doc, n), "SetSuppression2", resolved)
        out["resolved_again"] = states()
        return out
    return work


def state_version(path):
    """The closed assembly's ``ISldWorks.VersionHistory`` (the ledger: verified on 2026 SP1.1 for a closed file, never
    by the app) and ``GetLatestSupportedFileVersion``: what last saved it, against what this SolidWorks writes."""
    def work(s):
        history = raw(s._app, "VersionHistory", path)  # noqa: SLF001
        latest = raw(s._app, "GetLatestSupportedFileVersion")  # noqa: SLF001
        return {"history": _plain(history), "latest": _plain(latest), "revision": list(s.revision)}
    return work


def state_read_only(path, folder, modes, names):
    """The not-open path (§11.1, §11.2): the copy's Sprocket part opened on its own and changed (a global added), its
    Housing part opened unchanged (P2), the assembly opened read-only beside them, under the watch; what came back and
    what became of each part (the sprocket's global read back); candidate 1 there with the flags around; then each
    mode shown and read; every file's time before."""
    def work(s):
        out = {"times_before": file_times(folder)}
        sprocket, housing = os.path.join(folder, "Sprocket.SLDPRT"), os.path.join(folder, "Housing.SLDPRT")
        s.open_document(housing)
        s.open_document(sprocket)
        s.add_global_variable("W9dProbe", "1")
        out["before_open"] = doc_states(s, folder)
        opts = C.ENUMS["swOpenDocOptions_e"]
        doc, opened = C.open_doc6(s, path, C.ENUMS["swDocumentTypes_e"]["swDocASSEMBLY"],
                                  opts["swOpenDocOptions_Silent"] | opts["swOpenDocOptions_ReadOnly"])
        out["opened"] = opened
        if doc is None:
            return out
        out["after_open"] = doc_states(s, folder)
        s.use_open_document(sprocket)
        out["global_kept"] = "W9dProbe" in s.equation_values()
        s._build_doc = doc  # noqa: SLF001
        s._raise_epoch()  # noqa: SLF001
        before = W.folder_flags(s, folder)
        out["candidate_1"] = candidate_1(doc, modes, names)
        out["candidate_1_marked"] = flags_changed(before, W.folder_flags(s, folder))
        out["truth"] = truth_of(s, doc, modes, names, C.ENUMS["swComponentSuppressionState_e"])
        out["after_shows"] = doc_states(s, folder)
        return out
    return work


def state_close(path, folder):
    """The read-only document closed unsaved (QuitDoc by its title, the run's own), 3 s waited under the watch, then
    what is open under the folder."""
    def work(s):
        title = None
        for d in W.documents(s._app):  # noqa: SLF001
            if os.path.normcase(str(call(d, "GetPathName") or "")) == os.path.normcase(path):
                title = str(call(d, "GetTitle"))
        if title is not None:
            call(s._app, "QuitDoc", title)  # noqa: SLF001
        time.sleep(3.0)
        return {"closed": title is not None, "after": doc_states(s, folder)}
    return work


def section_state(out):
    say("== state  a component's state per configuration without marking the assembly (W9D-INTERFACES §11.1), the "
        "root read with a lightweight component as facts (§11.5), the closed file's last saved version, and the "
        "read-only open beside open documents, shown and closed (§11.2): on a copy of setup.master")
    C.swconst(C.ENUM_NAMES)
    enums()
    new("IConfiguration.GetComponentSuppressionState (the API help; never called by the app or the macro database); "
        "IConfiguration.GetRootComponent3(False) (never called); ISldWorks.VersionHistory and "
        "GetLatestSupportedFileVersion (the ledger: verified on 2026 SP1.1 for a closed file; never by the app); "
        "OpenDoc6 Silent | ReadOnly with documents of the assembly already open, one changed, ShowConfiguration2 in a "
        "read-only document, and QuitDoc of it after (none measured)")
    folder, path, book, desk = A.copy_desk(A.user_master(), "d-state", "RangeBox.xlsx")
    try:
        box = desk.record.gearbox
        modes = list(box.modes)
        if len(modes) < 3:
            raise AssertionError(f"state needs three modes; the copy has {modes}")
        names = list(STATE_TARGETS) + ["Sprocket-2"]
        asm = os.path.basename(box.assembly)

        def prepare():
            got = run("state (a): prepared and saved", job(box.assembly, state_prepare(modes, folder)), 600)
            still = marked_at_start(got["flags_after_save"])
            say(f"fact    state (a): Housing-1 suppressed in {modes[0]}, Sprocket-4 in {modes[-1]}, {got['first']} "
                f"shown, saved: still marked {still or 'nothing'}; Sprocket-4's mates' flags read unshown (suppressed "
                f"True) {got['mates_of_sprocket4']}")
            if still:
                raise AssertionError("the copy reads modified after its save, so the reads cannot start unmarked")
            return got
        part(out, "prepared", "state (a)", prepare)

        def candidates():
            got = run("state (b-d): the candidates, nothing shown", job(box.assembly, state_candidates(folder, modes,
                                                                                                         names)), 900)
            truth = got["truth"]
            clean_start = not got["start"].get(asm)
            say(f"fact    state truth, each mode shown: {truth}; the bracket started with {asm} "
                f"{'unmarked' if clean_start else 'MARKED (P4: no proposal)'}")
            verdicts = {}
            for label, value in got["candidates"].items():
                read = value[0] if isinstance(value, tuple) else value
                verdicts[label] = state_verdict(read, truth) if isinstance(read, dict) else {"agrees": False,
                                                                                             "differ": read}
                say(f"fact    state {label}: {value}; against the truth {verdicts[label]}; marked "
                    f"{got['marks'][label] or 'nothing'}")
            say(f"fact    state route 2 taken apart: {got['steps']}; the first call that marked {got['first_marking']}")
            chosen = route_proposal(verdicts, got["marks"], ["GetComponentSuppressionState", "GetRootComponent3(False)"],
                                    clean_start)
            say(propose("COMPONENT_STATE_PER_CONFIGURATION_ROUTE", f"IConfiguration.{chosen}(Name2)" if chosen ==
                        "GetComponentSuppressionState" else chosen,
                        f"state (b-c): agreeing with the truth and marking nothing from an unmarked start: "
                        f"{chosen or 'none'}"))
            got["chosen"] = chosen
            return got
        cands = part(out, "candidates", "state (b-d)", candidates, needs=("prepared",))

        def unsaved():
            got = run("state (e): an unsaved change read", job(box.assembly, state_unsaved(modes, "Sprocket-2")), 600)
            verdict = state_verdict(got["read"], got["truth"])
            say(f"fact    state (e): Sprocket-2 suppressed in {got['mode']}, not saved: GetComponentSuppressionState "
                f"{got['read']}; truth {got['truth']}; {verdict}")
            chosen = (cands or {}).get("chosen")
            if chosen == "GetComponentSuppressionState":           # P6
                say(propose("COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED", verdict["agrees"],
                            f"state (e): the unsaved suppression read {got['read']}"))
            else:
                say(f"fact    state (e): not proposed: candidate 1 was not the route chosen ({chosen})")
            return got
        part(out, "unsaved", "state (e)", unsaved, needs=("prepared",))

        def lightweight():
            got = run("state (f): a lightweight component", job(box.assembly, state_lightweight("Sprocket-1")), 600)
            say(f"fact    state (f): Sprocket-1 set lightweight: states {got['set']}; GetComponentSuppressionState "
                f"{got['candidate_1']}, states after {got['after_candidate_1']}; root(False) {got['root(False)']!r}, "
                f"states after {got['after_root(False)']}; root(True) {got['root(True)']!r}, states after "
                f"{got['after_root(True)']}; resolved again {got['resolved_again']}. Facts only: whether either root "
                "read marks cannot show on a copy already marked (P7, the review's should-fix 12)")
            return got
        part(out, "lightweight", "state (f)", lightweight, needs=("prepared",))

        def close_copy():
            left = run("state: the copy closed unsaved", W.quit_in(folder))
            if left:
                raise AssertionError(f"the copy did not close: left {left}")
            return {"left": left}
        part(out, "closed", "state: the copy closed", close_copy)

        def version():
            got = run("state (v): the closed file's last saved version", C.in_build(state_version(box.assembly)), 120)
            last = last_saved(got.get("history"))
            agrees = last is not None and last[0] == got.get("latest")
            say(f"fact    state (v): VersionHistory {got.get('history')}, last {last}; GetLatestSupportedFileVersion "
                f"{got.get('latest')}; the copy was last saved by this SolidWorks in (a): {agrees}")
            say(propose("FILE_VERSION_READ", "ISldWorks.VersionHistory(path), its last entry against "
                        "GetLatestSupportedFileVersion" if agrees else None,
                        f"state (v): the closed copy, saved in (a) by this SolidWorks, reads last {last}"))
            return got
        part(out, "version", "state (v)", version, needs=("closed",))

        def read_only():
            try:
                got, _ = C.watched("state (g): the read-only open beside two parts, one changed",
                                   C.in_build(state_read_only(box.assembly, folder, modes, names)))
            except C.CaseStop as exc:
                say(f"STOP    state (g): {exc}")
                say(propose("OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS", None, f"state (g): a dialog: {exc}"))
                return {"dialog": str(exc)}
            before = got.get("before_open", {})
            housing_ok = (before.get("Housing.SLDPRT") or {}).get("flag") is False
            keeps = keeps_open_documents(before, {n: v for n, v in got.get("after_open", {}).items() if n in before})
            say(f"fact    state (g): before the open {before}; OpenDoc6 {got.get('opened')}; after {got.get('after_open')}"
                f"; the sprocket's global kept {got.get('global_kept')}; GetComponentSuppressionState there "
                f"{got.get('candidate_1')}, marked {got.get('candidate_1_marked') or 'nothing'}; shown "
                f"{got.get('truth')}; after the shows {got.get('after_shows')}")
            say(propose("OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS",
                        (keeps[0] and bool(got.get("global_kept"))) if housing_ok else None,
                        f"state (g): changed {keeps[1] or 'nothing'}; the unchanged Housing part unmarked before "
                        f"{housing_ok}; the sprocket's global kept {got.get('global_kept')}"))
            return got
        ro = part(out, "read_only", "state (g)", read_only, needs=("closed",))

        def close_read_only():
            if ro.get("dialog") or ro.get("after_open") is None:
                raise AssertionError("no read-only document to close")
            try:
                got, dialogs = C.watched("state (h): the read-only document closed unsaved",
                                         C.in_build(state_close(box.assembly, folder)))
            except C.CaseStop as exc:
                got, dialogs = {"closed": None, "after": {}}, [str(exc)]
            times = file_times(folder)
            changed = {n: (t, times.get(n)) for n, t in ro.get("times_before", {}).items() if times.get(n) != t}
            before = ro.get("before_open", {})
            loaded = [n for n in ro.get("after_open", {}) if n not in before and n != asm]
            after = got.get("after", {})
            others = {n: (dict(before[n]), after.get(n, {"open": False})) for n in before}
            for n in ("after_open", "after_shows"):
                for name, want in before.items():
                    if (ro.get(n) or {}).get(name) != want:
                        others[f"{name} ({n})"] = (want, (ro.get(n) or {}).get(name))
            verdict = read_only_close_verdict({"dialogs": dialogs, "left_open": asm in after, "loaded_left":
                                               [n for n in loaded if n in after], "times_changed": changed,
                                               "others": others})
            say(f"fact    state (h): QuitDoc of the read-only {asm} after its modes were shown: {got}; dialogs "
                f"{dialogs or 'none'}; documents it loaded {loaded}; file times changed {changed or 'none'}; {verdict}")
            say(propose("OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN", verdict[0], f"state (h): {verdict[1] or 'clean'}"))
            return got
        part(out, "read_only_closed", "state (h)", close_read_only, needs=("read_only",))
        if cands is not None:
            out["chosen"] = cands.get("chosen")
    finally:
        C.end(folder, "d-state")


# -- sub: a healthy user sub-assembly's open (§11.3) --------------------------------------------------------------


def sub_open(sub, folder, options_key, settle=5.0):
    """``sub`` not loaded: OpenDoc6 with ``options``; the flags of every document under ``folder`` straight after and
    after ``settle`` seconds, inside the job (the watch still running)."""
    def work(s):
        opts = C.ENUMS["swOpenDocOptions_e"]
        options = sum(opts[k] for k in options_key)
        doc, got = C.open_doc6(s, sub, C.ENUMS["swDocumentTypes_e"]["swDocASSEMBLY"], options)
        got["after"] = doc_states(s, folder)
        time.sleep(settle)
        got["settled"] = doc_states(s, folder)
        return got
    return work


def sub_insert_read_only(sub, host, folder):
    """``sub`` opened read-only, a new assembly saved as ``host`` (this run's own, by the app's save route), the
    sub-assembly inserted (AddComponent5 of a read-only document: NEW); the flags and read-only states after each."""
    def work(s):
        opts = C.ENUMS["swOpenDocOptions_e"]
        doc, got = C.open_doc6(s, sub, C.ENUMS["swDocumentTypes_e"]["swDocASSEMBLY"],
                               opts["swOpenDocOptions_Silent"] | opts["swOpenDocOptions_ReadOnly"])
        got["after_open"] = doc_states(s, folder)
        s.new_assembly()
        s.save_as(host)
        got["inserted"] = s.add_component("sub", sub, (0.0, 0.0, 0.0))
        got["children"] = [str(call(c, "Name2")) for c in list(raw(s._component("sub"), "GetChildren") or [])]  # noqa: SLF001
        got["after_insert"] = doc_states(s, folder)
        return got
    return work


def sub_make_host(sub, host):
    """P8: a host this run makes in the order ``p2_make_sub`` makes one: ``sub`` opened, a new assembly, ``sub``
    inserted, then ``save_as(host)`` (the app's measured SaveAs3, option 1, which saves no referenced document), so
    that reopening the host loads ``sub`` as a component only. No Save3."""
    def work(s):
        s.open_document(sub)
        s.new_assembly()
        s.add_component("sub", sub, (0.0, 0.0, 0.0))
        s.save_as(host)
        return bool(call(s._doc(), "GetSaveFlag"))  # noqa: SLF001
    return work


def sub_when_loaded(sub, host, host2, folder):
    """``host`` opened (``sub`` loaded as its component); then OpenDoc6 of ``sub`` (Silent); then a new assembly saved
    as ``host2`` and ``sub`` inserted into it: the flags after each."""
    def work(s):
        s.open_document(host)
        got = {"host_open": doc_states(s, folder)}
        opts = C.ENUMS["swOpenDocOptions_e"]
        doc, opened = C.open_doc6(s, sub, C.ENUMS["swDocumentTypes_e"]["swDocASSEMBLY"], opts["swOpenDocOptions_Silent"])
        got.update(opened=opened, after_open=doc_states(s, folder))
        s.new_assembly()
        s.save_as(host2)
        got["inserted"] = s.add_component("sub2", sub, (0.0, 0.0, 0.0))
        got["after_insert"] = doc_states(s, folder)
        return got
    return work


def section_sub(out):
    say("== sub  whether opening a healthy user sub-assembly marks it (W9D-INTERFACES §11.3): not loaded, opened "
        "read-only then inserted, and loaded as a component of an open assembly; every step under the watch")
    C.swconst(C.ENUM_NAMES)
    enums()
    new("OpenDoc6 of a healthy sub-assembly with its save flag read (the W9c probes read it only for one with a "
        "missing part); AddComponent5 of a sub-assembly opened read-only (no entry); OpenDoc6 of a sub-assembly loaded "
        "as a component (the ledger's warning 128 is for a part)")
    import shutil
    folder = W.fresh_folder("d-sub")
    part_path, sub = os.path.join(folder, "DSubPart.SLDPRT"), os.path.join(folder, "DSub.SLDASM")
    shutil.copy2(os.path.join(A.user_master(), "Sprocket.SLDPRT"), part_path)
    sub_name = os.path.basename(sub)

    def watched_or_none(label, work, finding):
        """P9: a dialog that comes and goes ends this step with a STOP line and its finding proposed None."""
        try:
            got, _ = C.watched(label, work)
            return got
        except C.CaseStop as exc:
            say(f"STOP    {label}: {exc}")
            say(propose(finding, None, f"{label}: a dialog: {exc}"))
            return None
    try:
        left = run("sub: the sub-assembly made", C.in_build(C.p2_make_sub(folder, part_path, sub)), 600)
        say(f"fact    sub: DSub.SLDASM made from DSubPart.SLDPRT and closed (left {left})")

        def not_loaded():
            got = watched_or_none("sub (a): not loaded, opened",
                                  C.in_build(sub_open(sub, folder, ("swOpenDocOptions_Silent",))), "SUBASSEMBLY_OPEN_MARKS")
            if got is not None:
                marks = sub_marks(False, (got["after"].get(sub_name) or {}).get("flag"))
                later = sub_marks(False, (got["settled"].get(sub_name) or {}).get("flag"))
                say(f"fact    sub (a): {got}")
                say(propose("SUBASSEMBLY_OPEN_MARKS", marks if marks == later else True,
                            f"sub (a): flag straight after {marks}, after the settle {later}"))
            run("sub: closed", W.quit_in(folder))
            return got or {"dialog": True}
        part(out, "not_loaded", "sub (a)", not_loaded)

        def read_only():
            host = os.path.join(folder, "DSubHost1.SLDASM")
            got = watched_or_none("sub (b): opened read-only, then inserted",
                                  C.in_build(sub_insert_read_only(sub, host, folder)), "SUBASSEMBLY_READ_ONLY_INSERT")
            if got is not None:
                say(f"fact    sub (b): {got}")
                after = got["after_insert"].get(sub_name) or {}
                say(propose("SUBASSEMBLY_READ_ONLY_INSERT", bool(got.get("inserted") and got.get("children")
                                                                 and after.get("flag") is False),
                            f"sub (b): inserted {got.get('inserted')}, children {got.get('children')}, the "
                            f"sub-assembly after {after}"))
            run("sub: closed", W.quit_in(folder))
            return got or {"dialog": True}
        part(out, "read_only", "sub (b)", read_only)

        def when_loaded():
            host, host2 = os.path.join(folder, "DSubHost2.SLDASM"), os.path.join(folder, "DSubHost3.SLDASM")
            flag = watched_or_none("sub (c): a host holding it, saved", C.in_build(sub_make_host(sub, host)),
                                   "SUBASSEMBLY_OPEN_MARKS_WHEN_LOADED")
            run("sub: closed", W.quit_in(folder))
            if flag is None and not os.path.exists(host):
                return {"dialog": True}
            got = watched_or_none("sub (c): loaded as a component, opened, inserted",
                                  C.in_build(sub_when_loaded(sub, host, host2, folder)),
                                  "SUBASSEMBLY_OPEN_MARKS_WHEN_LOADED")
            if got is not None:
                say(f"fact    sub (c): the host saved, its flag after {flag}; {got}")
                before = (got["host_open"].get(sub_name) or {}).get("flag")
                say(propose("SUBASSEMBLY_OPEN_MARKS_WHEN_LOADED",
                            sub_marks(before, (got["after_open"].get(sub_name) or {}).get("flag")),
                            f"sub (c): OpenDoc6 {got['opened']}; flag before {before}, after the open "
                            f"{got['after_open'].get(sub_name)}, after the insert {got['after_insert'].get(sub_name)}"))
            return got or {"dialog": True}
        part(out, "when_loaded", "sub (c)", when_loaded)
    finally:
        if not W.HUNG["on"]:
            run("sub: everything closed", W.quit_in(folder))


# -- the run ---------------------------------------------------------------------------------------------------------

ORDER = ["faces", "state", "sub"]
SECTIONS = {"faces": section_faces, "state": section_state, "sub": section_sub}
FOLDERS = {"faces": ["d-faces", "d-faces-second"], "state": ["d-state"], "sub": ["d-sub"]}


def done_here(name):
    return [p for p in (os.path.join(OUT, f) for f in FOLDERS.get(name, [name])) if os.path.exists(p)]


def main():
    A.SECTIONS.clear()
    A.SECTIONS.update(SECTIONS)
    if A._given in ("", "all"):                    # noqa: SLF001
        A.CHOSEN = list(ORDER)
    A.done_here = done_here
    A.RUN_TITLE, A.JSON_STEM = "W9d probes", "w9d-probes"
    return A.main()


if __name__ == "__main__":
    code = 1
    try:
        code = main()
    finally:
        with open(W.LOG_PATH, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(W.LOG) + "\n")
    raise SystemExit(code)
