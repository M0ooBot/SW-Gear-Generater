"""W9c's demonstration (ISSUE-1-PLAN §5 "W9c", §2.1's W9c text, §2.4 "In place", §4 M4, M5, M6, M8, M10; the
interface W9C-INTERFACES.md §4-§8): Update adds, removes and re-mates in place, and adds and removes modes, on
SolidWorks, through the Workbook window's own path (W9a's Desk9: the window's planning, footer, press and finish).

    python w9c_demonstration.py <src> <out> --pid PID [--log FILE] [--sections fixed,modes,...] [--redo]
        [--master <S0's rangebox.master>] [--user-master <W9a's setup.master>]
        [--reducer-master <W9a's reducer.master>] [--fixed-master <this script's fixed-updated.master>]
    python w9c_demonstration.py --self-check      (no SolidWorks, no Excel)

Every new kind of write is behind a per-version finding that is None (``UPDATE_INSERTS_A_GEAR``,
``UPDATE_MAKES_MATES_WITH_MODES``, ``UPDATE_BANDS_IN_PLACE``, ``UPDATE_ADDS_A_MODE``, ``UPDATE_REMOVES_A_MODE``,
``EXTERNAL_REFERENCES_READ``, each ``_ON_<year>``). As W9a's ``nocarrier`` did, each section first shows the app's
refusal with the finding as it stands (the footer's sentence before the press; the press refused before any write,
judged by its traced calls, the reads before and after, every document's save flag and every file's time), then
patches the finding True in this process only, says so (``PATCH``), and measures. Each section proposes its finding
from what it read (``propose``); none is set here.

Sections (each can run alone from a kept master; ``fixed`` keeps ``fixed-updated.master`` for the next four):

- ``fixed``     the plan's Done-when. A copy of ``setup.master`` (RangeBox with the user's work: the sprockets locked to
                Sun and RangeSlv, the housing, their mates, the keyway in Sun's part), with a user groove cut in
                RangeSlv's part; a quiet press records it; the workbook edited in Excel to RangeBox_Fixed (the
                fixture's own rows); the gates' refusal; one Update: Hub built, inserted and resolved in every mode
                (M5), its mates made and flagged in every mode (M6), RangeSlv given its bands in place after the
                groove (M8); every user item as it was; each mode as §3's table (W9b's per-mode judgement); the
                record; a second press quiet; W9b's step-face read on the in-place sleeve.
- ``modes``     M10 on a copy of ``fixed-updated.master``: a Modes row H2 (RangeSlv at H) added; N removed while not
                showing, with a user mate suppressed there; removing the mode showing refused by name; the first mode
                H removed (H2 keeps HighDog's coupling on), L becoming the record's first.
- ``remove``    G4 taken out of a copy of the 12 : 1 (no user component); HighDog taken out of a copy of
                ``setup.master`` refused before any write (C4: the external-references read is unmeasured), then
                with a user lock on HighDog refused naming that lock too.
- ``remake``    Sun 29 -> 30, Planet 13 -> 12, Ring 55 -> 54 on a copy of ``fixed-updated.master`` (the centre distance
                and the planets' even spacing kept): four gear mates of a gearbox with modes made again (ruling 9.16
                lifted), flags and senses read in every mode, the user's mates unchanged.
- ``bands-off`` no legal edit takes the bands off RangeBox_Fixed's sleeve in place (the self-check searches): the
                refusals said, nothing written; then, script-side only, the app's ``Session.suppress_feature`` on the
                copy's Relief read back with the sleeve's mates per mode, and turned back on.
- ``m4``        a probe (no app code makes it yet): the external-references reads the installed API help documents,
                on the user's parts (none has a reference; one with an in-context reference cannot be made by proven
                calls), with a positive control and GetSaveFlag around each.
- ``w9b-part``  W9b's ``part`` section again (88 s on 2026), so its step-face read runs on SolidWorks in this session.

Time on 2026, estimated: fixed 30 min, modes 30, remove 15, remake 15, bands-off 8, m4 5, w9b-part 2: about 1 h 45
min (the plan's budget 2 h 20 min); add 5 min if setup.master and 4 if the 12 : 1's master must be built first.
"""

import dataclasses
import math
import os
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SELF_CHECK = "--self-check" in sys.argv

if "--help" in sys.argv or "-h" in sys.argv:
    print(__doc__)
    raise SystemExit(0)

# -- the plan's numbers --------------------------------------------------------------------------------------------------

MODES = ("H", "N", "L")
ADDED_MODE, ADDED_AT = "H2", "H"       # modes: a Modes row added, RangeSlv at H (a copy of H's position)
REMOVED_MODE = "N"                     # modes: removed while another shows; the user's UserAngle4 suppressed there first
FIRST_MODE = "H"                       # modes: the record's first, removed last (H2 keeps HighDog's coupling on)
NEXT_FIRST = "L"                       # ... and the record's first after it (H, L, H2 less H)
USER_OFF_IN_N = "UserAngle4"           # a user mate the user suppresses in N alone before N goes (flags_lost)
GEARS_TEETH = {"Sun": "30", "Planet": "12", "Ring": "54"}   # remake: m(30 + 12)/2 = 26.25 as before; 30 + 2 × 12 = 54;
REMAKE_RATIO_L = 1.0 + 54.0 / 30.0                         # (30 + 54)/3 = 28 (three planets evenly); L 1 + 54/30
REMOVED_SETUP, REMOVED_REDUCER = "HighDog", "G4"
GROOVE = {"name": "User Groove", "at": (14.25, 0.0), "radius": 1.0}   # an axial Ø2 cut through the sleeve's wall
GROOVE_TOL = 1e-6          # mm
TOL = 1e-6                 # mm, rotation entries: a frame against another
RESOLVED = (2, 3)          # GetSuppression2: swComponentFullyResolved, swComponentResolved (W9a's setup reads these)
GATES = {"fixed": ("UPDATE_INSERTS_A_GEAR", "UPDATE_BANDS_IN_PLACE"), "add": ("UPDATE_ADDS_A_MODE",),
         "remove a mode": ("UPDATE_REMOVES_A_MODE",), "remake": ("UPDATE_MAKES_MATES_WITH_MODES",)}
SHEETS = ("Gears", "Meshes", "Modes")
HUB_OPS = ("Hub on Output Axis", "Hub along Output", "RangeSlv splined to Hub")
RELIEF_FEATURES = ("Relief Start Plane", "Relief End Plane", "Relief Start Sketch", "Relief End Sketch", "Relief")


# -- pure: the edits as the fixture's own rows --------------------------------------------------------------------------


def sheet_rows(spec):
    """The Gears, Meshes and Modes sheets' rows as the app's own writer lays them out (``model.to_sheets``): row 1 the
    titles, each value as a cell holds it."""
    from gear_generator.workbook import model
    return {s.name: [list(r) for r in s.rows] for s in model.to_sheets(spec) if s.name in SHEETS}


def _blank(value):
    return value is None or value == ""


def row_edits(old, new):
    """The cells a person types to turn the workbook ``old`` into ``new``, as ``(sheet, title, key, value)``: ``key`` the
    row's first cell (the gear, the mode, a mesh's Gear A), ``""`` a new row (the first empty one), ``value`` None to
    empty a cell. A changed row writes the cells that differ; a row gone empties every cell it had; a new row writes
    every cell it has. At most one new row per sheet, and a key must name one row."""
    before, after = sheet_rows(old), sheet_rows(new)
    out = []
    for sheet in SHEETS:
        titles = after[sheet][0]
        if before[sheet][0] != titles:
            raise ValueError(f"{sheet}: the two workbooks' columns differ: {before[sheet][0]} / {titles}")
        was = {r[0]: r for r in before[sheet][1:]}
        now = {r[0]: r for r in after[sheet][1:]}
        for rows in (before[sheet][1:], after[sheet][1:]):
            keys = [r[0] for r in rows]
            if len(keys) != len(set(keys)):
                raise ValueError(f"{sheet}: a key names more than one row: {keys}")
        added = [k for k in now if k not in was]
        if len(added) > 1:
            raise ValueError(f"{sheet}: more than one new row in one edit: {added}")
        for key, row in was.items():
            if key not in now:
                out += [(sheet, t, key, None) for t, v in zip(titles, row) if not _blank(v)]
            else:
                out += [(sheet, t, key, None if _blank(b) else b) for t, a, b in zip(titles, row, now[key])
                        if a != b and not (_blank(a) and _blank(b))]
        for key in added:
            out += [(sheet, t, "", v) for t, v in zip(titles, now[key]) if not _blank(v)]
    return out


def column_letter(col):
    out = ""
    while col:
        col, rem = divmod(col - 1, 26)
        out = chr(65 + rem) + out
    return out


def edit_refs(rows, edits):
    """Each edit's A1 address in sheets laid out as ``rows`` (W8's ``cell``: the column whose title starts with the
    edit's, the row whose first cell is its key, ``""`` the first row with an empty first cell), and ``rows`` carrying
    the edits, so a later edit sees the earlier. Returns ``[(sheet, ref, value)]``."""
    cells = []
    for sheet, title, key, value in edits:
        table = rows[sheet]
        col = next(i for i, t in enumerate(table[0]) if str(t).startswith(title))
        if key == "":
            row = next((i for i in range(1, len(table)) if _blank(table[i][0])), len(table))
        else:
            row = next(i for i in range(1, len(table)) if str(table[i][0]).strip() == key)
        cells.append((sheet, f"{column_letter(col + 1)}{row + 1}", value))
    for sheet, ref, value in cells:
        put_cell(rows, sheet, ref, value)
    return cells


def put_cell(rows, sheet, ref, value):
    """``rows`` with one cell written, at an A1 address (rows grown as needed)."""
    letters = "".join(c for c in ref if c.isalpha())
    row = int(ref[len(letters):]) - 1
    col = 0
    for c in letters:
        col = col * 26 + ord(c) - 64
    table = rows[sheet]
    while len(table) <= row:
        table.append([""] * len(table[0]))
    table[row][col - 1] = "" if value is None else value


def put_back(cleared, row):
    """The cells a row's clearing emptied, written back with the row's values (``row``: the sheet's row as it was, its
    blank cells left out, in the order ``row_edits`` cleared them)."""
    return [(sheet, ref, value) for (sheet, ref, _), value in zip(cleared, [v for v in row if not _blank(v)])]


def gap_of(a, b):
    """The largest difference between two frames (rotation 9, origin mm), or inf for a frame not read."""
    if a is None or b is None or isinstance(a, str) or isinstance(b, str):
        return float("inf")
    return max([abs(x - y) for x, y in zip(a[0], b[0])] + [abs(x - y) for x, y in zip(a[1], b[1])])


def user_items_judged(before, after, locked, still, user_mates, relative, tol=TOL):
    """What of the user's moved or changed between two every-mode reads (W9a's ``read_every``: frames, mates and flags
    per mode), in the modes both hold: each locked component's frame relative to its gear (``locked``: component ->
    gear; carried by route (c1) is allowed, nothing else), each of ``still``'s frames, each user mate's flag in every
    mode and its error code where it is on. ``relative(frame_of_gear, frame_of_component)``. A list of sentences,
    empty when nothing of the user's moved or changed."""
    out = []
    common = [m for m in before["frames"] if m in after["frames"]]
    for mode in common:
        fb, fa = before["frames"][mode], after["frames"][mode]
        for u, g in locked.items():
            if not all(n in f for n in (u, g) for f in (fb, fa)):
                out.append(f"{mode}: {u} or {g} not read")
                continue
            moved = gap_of(relative(fb[g], fb[u]), relative(fa[g], fa[u]))
            if moved > tol:
                out.append(f"{mode}: {u} moved {moved:.1e} against {g}")
        for u in still:
            moved = gap_of(fb.get(u), fa.get(u))
            if moved > tol:
                out.append(f"{mode}: {u} moved {moved:.1e}")
        for m in user_mates:
            code, suppressed = (after["mates"].get(mode) or {}).get(m, (None, None))
            if code is None:
                out.append(f"{mode}: {m} not found")
            elif code and not suppressed:
                out.append(f"{mode}: {m} in error ({code})")
    for m in user_mates:
        was = {c: v for c, v in (before["by_mode"].get(m) or {}).items() if c in common}
        now = {c: v for c, v in (after["by_mode"].get(m) or {}).items() if c in common}
        if was != now:
            out.append(f"{m}'s flags {was} -> {now}")
    return out


def flags_lost_expected(by_mode, user_mates, active, removed):
    """``(removed, mate, "suppressed" | "on")`` for each user mate whose flag in ``removed`` differs from ``active``'s,
    as the worker must say them (W9C-INTERFACES §6 ``flags_lost``)."""
    out = []
    for m in user_mates:
        flags = by_mode.get(m) or {}
        if removed in flags and active in flags and bool(flags[removed]) != bool(flags[active]):
            out.append((removed, m, "suppressed" if flags[removed] else "on"))
    return sorted(out)


def took_active_differs(said, mode, mate_flags, component_states, state_words):
    """The result's ``took_active_state`` for ``mode`` against a read in it: each user mate's flag (``mate_flags``:
    name -> suppressed) and each user component's state (``component_states``: name -> GetSuppression2), worded by
    ``state_words``. Every item read must be said, as read. A list of what differs."""
    told = {item: state for m, item, state in said if m == mode}
    out = []
    for name, off in mate_flags.items():
        want = "suppressed" if off else "on"
        if told.get(name) != want:
            out.append(f"{name}: said {told.get(name)!r}, read {want!r}")
    for name, state in component_states.items():
        want = state_words.get(state, str(state))
        if told.get(name) != want:
            out.append(f"{name}: said {told.get(name)!r}, read {want!r}")
    return out


def groove_faces(faces, groove=GROOVE, tol=GROOVE_TOL):
    """The cylinders the user's groove cut (W9b's ``part_faces``): radius ``groove``'s, the axis along z, at its
    distance from the part's axis."""
    x, y = groove["at"]
    return [f for f in faces if f.get("kind") == "cylinder" and abs(f["r"] - groove["radius"]) <= tol
            and abs(abs(f["axis"][2]) - 1.0) <= 1e-9
            and abs(math.hypot(f["point"][0], f["point"][1]) - math.hypot(x, y)) <= tol]


def groove_kept(before, after, groove=GROOVE):
    """The user's groove in the sleeve's part before and after bands in place: its feature present, in no error, before
    the relief's first feature; its sketch's and its feature's dimensions as before; the faces it cut still there
    (as many). A list of what differs."""
    out = []
    names = [n for n, _, _ in after["features"]]
    mine = [(n, t, c) for n, t, c in after["features"] if n == groove["name"]]
    if not mine:
        return [f"{groove['name']} is gone"]
    if mine[0][2]:
        out.append(f"{groove['name']} in error ({mine[0][2]})")
    relief = [names.index(n) for n in RELIEF_FEATURES if n in names]
    if relief and names.index(groove["name"]) > min(relief):
        out.append(f"{groove['name']} stands after the relief's first feature")
    if before["dims"] != after["dims"]:
        out.append(f"its dimensions {before['dims']} -> {after['dims']}")
    if len(groove_faces(before["faces"], groove)) != len(groove_faces(after["faces"], groove)) or not \
            groove_faces(after["faces"], groove):
        out.append(f"its faces {len(groove_faces(before['faces'], groove))} -> {len(groove_faces(after['faces'], groove))}")
    return out


def propose(name, value, evidence):
    return f"propose {name} = {value!r}  # {evidence}"


# -- --self-check: the edits through the app's own read and classify, on the fake ------------------------------------------


def _fake():
    """``FakeSolidWorks`` from the suite's ``test_swbuild`` (pytest is only its decorators at import: a stand-in is
    used where pytest is not installed, so the self-check runs where the suite does not)."""
    sys.path[:0] = [os.path.join(REPO, "src"), os.path.join(REPO, "tests")]
    try:
        import pytest  # noqa: F401
    except ImportError:
        def deco(*a, **k):
            return a[0] if len(a) == 1 and callable(a[0]) and not k else (lambda f: f)

        class Mark:
            def __getattr__(self, _name):
                return deco
        stand_in = types.ModuleType("pytest")
        stand_in.fixture, stand_in.mark, stand_in.param = deco, Mark(), lambda *a, **k: a
        sys.modules["pytest"] = stand_in
    from test_swbuild import FakeSolidWorks
    return FakeSolidWorks


BOOK, STRIP = "C:\\B\\RangeBox.xlsx", "C:\\Out\\"


def _assessed(spec):
    from gear_generator.workbook import assess
    return assess.assess(dataclasses.replace(spec, source_path=BOOK), [], STRIP)


def _built(spec, fake):
    """A first Build of ``spec`` on the fake, its record read back from its JSON (the suite's ``built``)."""
    from gear_generator import store, swbuild
    from gear_generator.workbook import gearbox
    sw = fake()
    a = _assessed(spec)
    plan = gearbox.plan_gearbox(a, None, exists=sw.exists, read_sidecar=lambda p: None)
    if plan.refusal:
        raise AssertionError(plan.refusal)
    result = swbuild.build_gearbox(sw, **plan.build_kwargs(), exists=sw.exists)
    if not result.ok:
        raise AssertionError(result.failures)
    done = gearbox.finish_build(plan, result, None, workbook=BOOK, digest="d1", written_by="self-check",
                                read_sidecar=lambda p: None, exists=sw.exists)
    return store.link_record_from_json(store.link_record_to_json(done.record))


def _offline(old, steps, folder):
    """``old``'s workbook written by the app's own writer, each step's cells (``(sheet, title, key, value)`` edits, or
    ``{"cells": [(sheet, ref, value)], "edits": [...]}``) written by the app's own ``write_cells`` into a new file, each read back by
    the app's own reader. Returns ``[(the read's spec, the cells written)]``."""
    from gear_generator.workbook import link, model, xlsx
    folder = tempfile.mkdtemp(dir=folder)
    path = os.path.join(folder, "step0.xlsx")
    xlsx.write_new(path, model.to_sheets(old))
    rows = sheet_rows(old)
    out = []
    for i, step in enumerate(steps, 1):
        if isinstance(step, dict):          # cells at known addresses, and edits resolved before they are written
            cells = edit_refs(rows, step["edits"])
            for sheet, ref, value in step["cells"]:
                put_cell(rows, sheet, ref, value)
            cells = list(step["cells"]) + cells
        else:
            cells = edit_refs(rows, step)
        changes = {}
        for sheet, ref, value in cells:
            changes.setdefault(sheet, {})[ref] = value
        nxt = os.path.join(folder, f"step{i}.xlsx")
        done = xlsx.write_cells(path, changes, out_path=nxt)
        if done.refused:
            raise AssertionError(f"write_cells refused {done.refused}")
        path = nxt
        out.append((link.Link(path).read().spec, cells))
    return out


def _w9b_pure():
    """W9b's pure judgements (``judge_mode``, ``section3_of``, ``app_spans``, §3's table): its source up to its own
    self-check, run as a module (importing it would run its self-check, or its live part)."""
    path = os.path.join(HERE, "w9b_demonstration.py")
    with open(path, encoding="utf-8") as handle:
        head = handle.read().split("\nif SELF_CHECK:\n", 1)[0]
    module = types.ModuleType("w9b_pure")
    module.__file__ = path
    exec(compile(head, path, "exec"), module.__dict__)  # noqa: S102 - the repo's own script
    return module


def self_check():
    import time as _time
    fake = _fake()
    from gear_generator import swbuild
    from gear_generator.workbook import link, update
    from workbook_fixtures import Mode, range_box, range_box_fixed
    b9 = _w9b_pure()
    bad = []

    def ok(cond, what):
        print(("ok      " if cond else "FAIL    ") + what)
        if not cond:
            bad.append(what)

    def renamed(spec):
        return dataclasses.replace(spec, box=dataclasses.replace(spec.box, name="RangeBox"))

    def with_gear(spec, gid, **changes):
        return dataclasses.replace(spec, gears=tuple(dataclasses.replace(g, **changes) if g.id == gid else g
                                                     for g in spec.gears))

    def classify(record, spec):
        a = _assessed(spec)
        errors = [d.message for d in a.diagnostics if d.is_error]
        if errors or a.lay_out_refusal():
            return a, None, errors or [a.lay_out_refusal()]
        on_disk = {p.path.lower() for p in record.parts} | {c.path.lower() for c in record.gearbox.carriers} | {
            record.gearbox.layout.lower(), record.gearbox.assembly.lower()}
        return a, update.classify(record, a, exists=lambda p: p.lower() in on_disk), []

    def modes_of(spec, names):
        by = {m.name: m for m in spec.modes}
        return dataclasses.replace(spec, modes=tuple(by[n] for n in names))

    started = _time.monotonic()
    rb, fx = renamed(range_box()), renamed(range_box_fixed())
    h2 = Mode(ADDED_MODE, (("RangeSlv", ADDED_AT),), "", row=5)
    fx_h2 = dataclasses.replace(fx, modes=fx.modes + (h2,))
    reducer = link.Link(os.path.join(REPO, "tests", "fixtures", "excel", "Reducer_12to1.xlsx")).read().spec
    records = {"rb": _built(rb, fake), "fx": _built(fx, fake), "hnlh2": _built(fx_h2, fake),
               "hlh2": _built(modes_of(fx_h2, ("H", "L", ADDED_MODE)), fake), "reducer": _built(reducer, fake)}
    print(f"fact    five first Builds on the fake in {_time.monotonic() - started:.0f} s")
    year_ = 2026
    rev = (34, 1, 1)

    def gates(ip, modes=False, remakes=False):
        return sorted(f for _, f in swbuild.in_place_gates(ip, rev, modes=modes, remakes=remakes))

    with tempfile.TemporaryDirectory() as folder:
        # fixed: RangeBox -> RangeBox_Fixed, the fixture's own rows typed into the workbook
        edits = row_edits(rb, fx)
        print(f"fact    fixed's edit: {edits}")
        ok(all(s == "Gears" for s, _, _, _ in edits) and {k for _, _, k, _ in edits} == {"RangeSlv", ""}
           and sum(1 for _, _, k, _ in edits if k == "") == len([v for v in sheet_rows(fx)["Gears"][-1] if not _blank(v)]),
           "fixed: RangeSlv's cells changed and Hub's row typed in, nothing else")
        (spec, _), = _offline(rb, [edits], folder)
        a, up, errors = classify(records["rb"], spec)
        ok(not errors and b9.warnings_of(a) == b9.warnings_of(_assessed(fx)),
           f"fixed: the workbook read back is legal with RangeBox_Fixed's own warnings: {errors}")
        if up is not None:
            ip = up.in_place
            ok(not up.structural and not up.needs_new_revision and [g.gear for g in ip.added] == ["Hub"]
               and [(b.gear, b.add) for b in ip.bands] == [("RangeSlv", True)]
               and [op.name for op in ip.added[0].ops if type(op).__name__ == "Mate"] == list(HUB_OPS),
               f"fixed: one Update in place: Hub added with {HUB_OPS}, RangeSlv given bands: structural "
               f"{list(up.structural)}")
            ok(gates(ip, modes=True) == [f"UPDATE_BANDS_IN_PLACE_ON_{year_}", f"UPDATE_INSERTS_A_GEAR_ON_{year_}"],
               f"fixed: its gates on 2026 are the insert's and the bands': {gates(ip, modes=True)}")
            foreseen = update.in_place_ahead(up, records["rb"])
            ok({p.kind for p in foreseen} == {swbuild.PROBLEM_UNSETTLED},
               f"fixed: the footer foresees the unsettled gates alone: {[(p.kind, p.subjects) for p in foreseen]}")
            for mode in MODES:
                bands, dogs, hub = b9.app_spans(a, mode)
                judged = b9.judge_mode(bands, dogs)
                ok(b9.section3_of(judged, bands, mode) == [] and hub == b9.HUB,
                   f"fixed, {mode}: the read after the edit is §3's row: {b9.section3_of(judged, bands, mode)}")

        # modes: H2 added; N removed; H2 removed (refused live: it is showing); H2 restored and H removed
        add = row_edits(fx, fx_h2)
        rm_n = row_edits(fx_h2, modes_of(fx_h2, ("H", "L", ADDED_MODE)))
        rm_h2 = row_edits(modes_of(fx_h2, ("H", "L", ADDED_MODE)), modes_of(fx_h2, ("H", "L")))
        steps = _offline(fx, [add, rm_n, rm_h2], folder)
        restore = put_back(steps[2][1], sheet_rows(fx_h2)["Modes"][-1])
        rm_h = row_edits(modes_of(fx_h2, ("H", "L", ADDED_MODE)), modes_of(fx_h2, ("L", ADDED_MODE)))
        last, rm_h_cells = _offline(fx, [add, rm_n, rm_h2, {"cells": restore, "edits": rm_h}], folder)[-1]
        for label, spec, record, want in (
                ("H2 added", steps[0][0], records["fx"], {"added": (ADDED_MODE,)}),
                ("N removed", steps[1][0], records["hnlh2"], {"removed": (REMOVED_MODE,)}),
                ("H2 removed (refused live, showing)", steps[2][0], records["hlh2"], {"removed": (ADDED_MODE,)}),
                ("H2 put back and H removed", last, records["hlh2"], {"removed": (FIRST_MODE,), "first": NEXT_FIRST})):
            _, up, errors = classify(record, spec)
            ip = up.in_place if up is not None else None
            ok(up is not None and not up.structural and ip.modes_added == want.get("added", ())
               and ip.modes_removed == want.get("removed", ()) and ip.first_mode == want.get("first", "")
               and not ip.added and not ip.removed and not ip.bands,
               f"modes, {label}: in place, {want}: {errors or (list(up.structural), ip and (ip.modes_added, ip.modes_removed, ip.first_mode))}")
        print(f"fact    modes' edits: add {add}; N {rm_n}; H2 {rm_h2}; put back {restore}; H {rm_h_cells}")
        ok(sorted(f for _, f in swbuild.in_place_gates(swbuild.InPlace(modes_added=(ADDED_MODE,)), rev)) ==
           [f"UPDATE_ADDS_A_MODE_ON_{year_}"] and sorted(f for _, f in swbuild.in_place_gates(
               swbuild.InPlace(modes_removed=(REMOVED_MODE,)), rev)) == [f"UPDATE_REMOVES_A_MODE_ON_{year_}"],
           "modes: a mode added reads UPDATE_ADDS_A_MODE, one removed UPDATE_REMOVES_A_MODE")

        # remove: G4 out of the 12 : 1; HighDog out of RangeBox
        for label, old, gear, record in (("the 12 : 1", reducer, REMOVED_REDUCER, records["reducer"]),
                                         ("RangeBox", rb, REMOVED_SETUP, records["rb"])):
            new = dataclasses.replace(old, gears=tuple(g for g in old.gears if g.id != gear),
                                      meshes=tuple(m for m in old.meshes if gear not in (m.a, m.b)))
            edits = row_edits(old, new)
            (spec, _), = _offline(old, [edits], folder)
            _, up, errors = classify(record, spec)
            ip = up.in_place if up is not None else None
            ok(up is not None and not up.structural and [r.gear for r in ip.removed] == [gear],
               f"remove, {label}: {gear} taken out in place with {ip and [r.mates for r in ip.removed]}: "
               f"{errors or (up and list(up.structural))}; edit {edits}")
            if ip is not None:
                ok(gates(ip, modes=bool(old.modes)) == [],
                   f"remove, {label}: no gate unsettled on 2026 (P1's findings set): {gates(ip, modes=bool(old.modes))}")

        # remake: a tooth change of three gears with modes
        teeth = fx
        for gear, n in GEARS_TEETH.items():
            teeth = with_gear(teeth, gear, teeth=n)
        (spec, _), = _offline(fx, [row_edits(fx, teeth)], folder)
        a, up, errors = classify(records["fx"], spec)
        ratio = next((m.ratio for m in a.report.modes if m.name == "L"), None)
        ok(up is not None and not up.structural and not up.in_place and len(up.ratios) == 4
           and gates(swbuild.InPlace(), modes=True, remakes=True) == [f"UPDATE_MAKES_MATES_WITH_MODES_ON_{year_}"]
           and ratio is not None and abs(ratio - REMAKE_RATIO_L) < 1e-9,
           f"remake: Sun 30, Planet 12, Ring 54 legal, four gear mates remade, gated on UPDATE_MAKES_MATES_WITH_MODES, "
           f"L's ratio {ratio} (1 + 54/30): {errors or (up and (list(up.structural), list(up.ratios)))}")

        # bands-off: every candidate edit illegal, or Build again
        candidates = {
            "the bands alone": with_gear(fx, "RangeSlv", start_band="", end_band=""),
            "as RangeBox's sleeve, Hub kept": with_gear(fx, "RangeSlv", start_band="", end_band="", at="-24.5",
                                                        face_width="10", slides="H=-5, N=0, L=+5"),
            "as RangeBox's sleeve, Hub over the dogs": with_gear(with_gear(
                fx, "RangeSlv", start_band="", end_band="", at="-24.5", face_width="10", slides="H=-5, N=0, L=+5"),
                "Hub", at="-24.5", face_width="20"),
            "as RangeBox's sleeve, Hub's row cleared": dataclasses.replace(
                with_gear(fx, "RangeSlv", start_band="", end_band="", at="-24.5", face_width="10",
                          slides="H=-5, N=0, L=+5"), gears=tuple(g for g in with_gear(
                              fx, "RangeSlv", start_band="", end_band="", at="-24.5", face_width="10",
                              slides="H=-5, N=0, L=+5").gears if g.id != "Hub"))}
        legal_in_place = []
        for label, spec in candidates.items():
            _, up, errors = classify(records["fx"], spec)
            said = errors[:1] if errors else list(up.structural)[:1]
            if up is not None and not up.needs_new_revision and up.in_place.bands:
                legal_in_place.append(label)
            print(f"fact    bands-off, {label}: {'illegal' if errors else 'Build again' if up.needs_new_revision else 'in place'}"
                  f": {said}")
        ok(not legal_in_place, f"bands-off: no candidate takes the bands off in place, so the section is a refusal "
                               f"check and the take-away is measured script-side: {legal_in_place or 'none'}")

    # the pure judgements on made-up readings
    rot = (1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0)

    def rel(g, u):
        return (u[0], tuple(b - a for a, b in zip(g[1], u[1])))
    before = {"frames": {"H": {"Sun": (rot, (0, 0, 0)), "Sprocket-1": (rot, (0, 0, 30)), "Housing-1": (rot, (0, 0, 60))}},
              "mates": {"H": {"UserLock1": (0, False)}}, "by_mode": {"UserLock1": {"H": False}}}
    carried = {"frames": {"H": {"Sun": (rot, (0, 0, 5)), "Sprocket-1": (rot, (0, 0, 35)), "Housing-1": (rot, (0, 0, 60))}},
               "mates": {"H": {"UserLock1": (0, False)}}, "by_mode": {"UserLock1": {"H": False}}}
    ok(user_items_judged(before, carried, {"Sprocket-1": "Sun"}, ["Housing-1"], ["UserLock1"], rel) == [],
       "user items: a component carried with its gear and the housing still is no change")
    moved = dict(carried, frames={"H": dict(carried["frames"]["H"], **{"Housing-1": (rot, (0, 0, 61))})})
    off = dict(carried, by_mode={"UserLock1": {"H": True}}, mates={"H": {"UserLock1": (51, False)}})
    ok(len(user_items_judged(before, moved, {"Sprocket-1": "Sun"}, ["Housing-1"], ["UserLock1"], rel)) == 1
       and len(user_items_judged(before, off, {"Sprocket-1": "Sun"}, ["Housing-1"], ["UserLock1"], rel)) == 2,
       "user items: a still component moved, and a mate's flag and error changed, are said")
    ok(flags_lost_expected({"UserAngle4": {"H": False, "N": True}, "UserLock1": {"H": False, "N": False}},
                           ["UserAngle4", "UserLock1"], "H", "N") == [("N", "UserAngle4", "suppressed")],
       "modes: the flags lost with N are the user's mates whose flag there differs from the active mode's")
    words = {2: "resolved", 0: "suppressed"}
    said = [("H2", "UserLock1", "on"), ("H2", "Sprocket-1", "resolved")]
    ok(took_active_differs(said, "H2", {"UserLock1": False}, {"Sprocket-1": 2}, words) == []
       and took_active_differs(said, "H2", {"UserLock1": True}, {"Sprocket-1": 2}, words) != [],
       "modes: took_active_state held to a read in the new mode")
    faces = [{"kind": "cylinder", "r": 1.0, "axis": [0, 0, 1.0], "point": [14.25, 0.0, 0.0]},
             {"kind": "cylinder", "r": 1.0, "axis": [0, 0, -1.0], "point": [0.0, -14.25, 3.0]},
             {"kind": "cylinder", "r": 12.5, "axis": [0, 0, 1.0], "point": [0, 0, 0]}]
    feats = [("Teeth", "Cut", 0), (GROOVE["name"], "Cut", 0)] + [(n, "x", 0) for n in RELIEF_FEATURES]
    was = {"features": feats[:2], "dims": [("D1", 2.0)], "faces": faces[:1]}
    now = {"features": feats, "dims": [("D1", 2.0)], "faces": faces[:1]}
    ok(len(groove_faces(faces)) == 2 and groove_kept(was, now) == [], "groove: kept before the relief, its faces there")
    late = dict(now, features=feats[:1] + [(n, "x", 0) for n in RELIEF_FEATURES] + [(GROOVE["name"], "Cut", 0)])
    ok(groove_kept(was, late) != [] and groove_kept(was, dict(now, faces=faces[2:])) != [],
       "groove: one after the relief, or its faces gone, is said")
    ok(propose("X", True, "e") == "propose X = True  # e", "propose's form")
    print(f"done    {len(bad)} failed")
    return 0 if not bad else 1


if SELF_CHECK:
    raise SystemExit(self_check())


# -- the live run: W9a's harness, W9b's per-mode judgement ----------------------------------------------------------------

sys.path.insert(0, HERE)
import w9a_demonstration as A  # noqa: E402  (W8's and S0's scripts, the watch, the What's Wrong rule, Desk9, main)
import w9b_demonstration as B  # noqa: E402  (§3's table, the per-mode read and judgement, the part's faces)

W, S0 = A.W, A.S0
from gear_generator import findings, store, swbuild, swcom, ui_text  # noqa: E402
from gear_generator.swcom import call  # noqa: E402
from gear_generator.workbook import update as wb_update  # noqa: E402
from gear_generator.workbook.model import Mode  # noqa: E402

say, check = W.say, W.check
OUT = W.OUT
CTX, RESULT, run, job = A.CTX, A.RESULT, A.run, A.job
EZ = findings.EXTRUDE_Z_SIGN
W.TRACED = tuple(W.TRACED) + ("AddComponent5",)    # an insert in a refused press's trace is a write too
MASTERS = {"fixed": A._arg("--fixed-master")}  # noqa: SLF001
STILL = ("Sprocket-4", "Housing-1")    # the user's components no lock carries: they stand still through every press
CHANGING = ("ShowConfiguration2", "SetSuppression2", "SetSystemValue3", "ForceRebuild3", "EditRebuild3", "put",
            "AddMate5", "AddConfiguration2", "DeleteConfiguration2", "AddComponent5")


def year():
    return swcom.release_year(int(W.TAG["revision"][0]))


def finding_name(stem):
    return f"{stem}_ON_{year()}"


def renamed(spec):
    return dataclasses.replace(spec, box=dataclasses.replace(spec.box, name="RangeBox"))


def modes_of(spec, names):
    by = {m.name: m for m in spec.modes}
    return dataclasses.replace(spec, modes=tuple(by[n] for n in names))


def specs():
    """The fixtures as this script edits them (their Box name RangeBox, as setup.master's workbook has it): RangeBox,
    RangeBox_Fixed, and RangeBox_Fixed with the Modes row H2."""
    fx = W.w8_fixtures()
    rb, fixed = renamed(fx.range_box()), renamed(fx.range_box_fixed())
    h2 = Mode(ADDED_MODE, (("RangeSlv", ADDED_AT),), "", row=5)
    return rb, fixed, dataclasses.replace(fixed, modes=fixed.modes + (h2,))


def with_teeth(spec):
    return dataclasses.replace(spec, gears=tuple(dataclasses.replace(g, teeth=GEARS_TEETH[g.id]) if g.id in GEARS_TEETH
                                                 else g for g in spec.gears))


def same_sheets(label, desk, spec):
    """The copy's workbook as the window reads it holds ``spec``'s Gears, Meshes and Modes rows, so the edits made from
    the fixture's rows are the ones the plan names; a section stops otherwise."""
    got, want = sheet_rows(desk.a.spec), sheet_rows(spec)
    differ = {s: [r for r in got[s] if r not in want[s]] + [r for r in want[s] if r not in got[s]] for s in SHEETS
              if got[s] != want[s]}
    if differ:
        A.section_stop(f"{label}: the copy's workbook is not the fixture's: {differ}")
    check(True, f"{label}: the copy's workbook holds the fixture's Gears, Meshes and Modes rows")


def edit_live(desk, book, edits, label, cells=()):
    """A person's edit in Excel: each ``(sheet, title, key, value)`` at its cell (W8's ``cell``, every address found
    before anything is written) and ``cells`` at known addresses, saved; the window's poll reads, plans and
    classifies (W8's ``edit``). Returns the cells written."""
    found = [(sheet, W.cell(book, sheet, title, key), value) for sheet, title, key, value in edits]
    written = list(cells) + found
    say(f"edit    {label}: {written}")
    W.edit(desk, book, *written)
    return written


def gear_entry(box, gear):
    return next((c for c in box.components if c.gear == gear), None)


def active_now(desk):
    return run("the mode showing", job(desk.record.gearbox.assembly, lambda s: s.active_configuration()), 300)


def person_shows(desk, folder, mode):
    """The user shows a mode in SolidWorks and saves."""
    run(f"the user shows {mode}", job(desk.record.gearbox.assembly, lambda s: s.show_configuration(mode)), 300)
    A.save_user(folder, f"{mode} shown")
    check(active_now(desk) == mode, f"{mode} is the mode showing")


def every_mode(label, desk, users):
    """W9a's every-mode read: each mode shown and rebuilt, the app's bodies and ``users``' frames, every mate's code per
    mode and flag in every mode."""
    box = desk.record.gearbox
    return A.read_every(label, box.assembly, A.pairs_of(box, users), list(box.modes))


def users_unchanged(label, before, after, users, mates, locked=None):
    """§0.3: nothing of the user's moved or changed but by the measured carry (a locked component with its gear): a STOP
    otherwise."""
    locked = dict(A.RB_LOCKED if locked is None else locked)
    still = [u for u in users if u not in locked]
    diff = user_items_judged(before, after, locked, still, mates, S0.relative)
    if diff:
        A.stop(f"{label}: the user's work moved or changed by something other than the measured carry: {diff} (§0.3)")
    check(True, f"{label}: every user component where it was ({sorted(locked)} relative to their gears, {still} still), "
                f"every user mate on in the modes it was on in and in no error ({len(mates)} mates)")


def states_by_mode(label, desk, names):
    """M5: each mode shown, the named components' GetSuppression2 (``Session.components``); the mode showing before
    shown again."""
    box = desk.record.gearbox

    def work(s):
        first, out = s.active_configuration(), {}
        for mode in box.modes:
            s.show_configuration(mode)
            out[mode] = {c.name: c.state for c in s.components() if c.name in names}
        s.show_configuration(first)
        return out
    return run(f"{label}: the components' states per mode", job(box.assembly, work), 900)


def judged_modes(label, desk, out, section3=True, against=None):
    """W9b's per-mode read and judgement on the gearbox as recorded now (frames, flags, slide values, interference,
    every gear free, the bands and dogs where the app's read puts them; §3's table where ``section3``), and each mode
    of ``against`` (mode -> §3's row to hold it to) by W9b's ``judge_mode``. A mode reading other than §3's is a
    STOP."""
    gears = ("RangeSlv", "HighDog", "LowDog", "Hub")
    globals_ = B.part_globals(desk, gears)
    every = B.mode_read(label, desk)
    clean = B.judge_every(label, desk, every, globals_, against_section3=section3, out=out)
    differ = {}
    for mode, row in (against or {}).items():
        bands, dogs, _ = B.measured(every["frames"][mode], globals_)
        judged = B.judge_mode(bands, dogs)
        wrong = B.section3_of(judged, bands, row)
        if wrong:
            differ[mode] = wrong
        check(not wrong, f"{label}, {mode}: as §3's {row} row: {wrong or 'the bands, the relief, engaged '}"
                         f"{judged['engaged']}")
    if not clean or differ:
        A.stop(f"{label}: a mode reads other than the record and §3 say: {differ or 'see the FAILs above'} (§0.3)")
    return every, globals_


class patched:
    """The named findings set True in this process only, for one measurement, said; put back on the way out."""

    def __init__(self, stems):
        self.names = [finding_name(s) for s in stems]
        self.was = {}

    def __enter__(self):
        for name in self.names:
            self.was[name] = getattr(findings, name, None)
            setattr(findings, name, True)
            say(f"PATCH   findings.{name} = True in this process, for this measurement only (was {self.was[name]!r})")
        return self

    def __exit__(self, *_exc):
        for name, value in self.was.items():
            setattr(findings, name, value)
            say(f"PATCH   findings.{name} back to {value!r}")
        return False


def foreseen_names(desk):
    """What the footer foresees of the in-place change (``update.in_place_ahead``, K4), said."""
    problems = wb_update.in_place_ahead(desk.update, desk.record)
    for p in problems:
        say(f"        foreseen {p.kind} {list(p.subjects)} {list(p.mates)}: {p.sentence}")
    return problems


def gated_refusal(label, desk, folder, stems, part, users=None):
    """The app's refusal with the findings as they stand (W9a's ``nocarrier`` way): the footer foresees each gate
    unsettled, by name; the user saves; the press refuses before any write (W9a's ``refuse_press``: its traced calls,
    the frames, mates, flags, entities and ``part``'s globals read before and after, the record keeping the refusal),
    and no file's time and no document's save flag changes. Nothing to show where every finding is already True."""
    standing = {finding_name(s): getattr(findings, finding_name(s), None) for s in stems}
    if all(v is True for v in standing.values()):
        say(f"fact    {label}: {standing} already True in findings.py, so the app refuses nothing here")
        return {"findings": standing}
    unsettled = [n for n, v in standing.items() if v is not True]
    A.ahead_of(desk, f"{label}, the findings as they stand {standing}")
    foreseen = foreseen_names(desk)
    said = " ".join(p.sentence + " " + " ".join(p.subjects) for p in foreseen)
    check(any(p.kind == swbuild.PROBLEM_UNSETTLED for p in foreseen) and all(n in said for n in unsettled),
          f"{label}: the footer foresees the press refused, naming {unsettled}: "
          f"{[(p.kind, list(p.subjects)) for p in foreseen]}")
    A.save_user(folder, f"before {label}")
    files = B.documents_state(label, desk, folder)
    problems = A.refuse_press(label, desk, folder, {swbuild.PROBLEM_UNSETTLED}, (), tuple(unsettled), users=users,
                              part=part, save=False)
    B.nothing_written(f"{label}, by file times and save flags", files, B.documents_state(label, desk, folder))
    return {"findings": standing, "refusal": [p.sentence for p in problems]}


def refused_without_writing(label, desk, folder, part, judge, users=None):
    """A press that must refuse before any write, judged by ``judge(result, error) -> (ok, sentence)``: its traced calls
    change or show nothing, the frames, mates and flags read the same before and after, no file's time and no save
    flag changes. For refusals W9a's ``refuse_press`` does not hold to its record rule (a BuildError; the mode
    showing, read before the user's work). Returns the error."""
    A.save_user(folder, f"before {label}")
    box = desk.record.gearbox
    pairs = A.pairs_of(box, A.rb_users() if users is None else users)
    files = B.documents_state(label, desk, folder)
    before = A.read_now(f"before {label}", box.assembly, folder, pairs, list(box.modes))
    globals_before = run("the part's globals", lambda s: W.live_globals(s, part))
    result, calls = A.press(desk, label)
    error = desk.error
    ok, sentence = judge(result, error)
    check(ok, f"{label}: {sentence}")
    changing = [c for c in calls if c[0] in CHANGING]
    check(not changing, f"{label}: the refused press made no call that changes or shows anything: {changing or 'none'}")
    after = A.read_now(f"after {label}", box.assembly, folder, pairs, list(box.modes))
    globals_after = run("the part's globals", lambda s: W.live_globals(s, part))
    diff = A.written(before, after) + ([f"the part's globals {globals_before} -> {globals_after}"]
                                       if globals_after != globals_before else [])
    check(not diff, f"{label}: nothing written: {diff or 'frames, mates, flags and globals as before'}")
    B.nothing_written(f"{label}, by file times and save flags", files, B.documents_state(label, desk, folder))
    entry = desk.record.gearbox.user_work
    say(f"fact    {label}: the record's inventory after it: problems "
        f"{[(p.kind, list(p.mates)) for p in entry.problems] if entry is not None else None}")
    return error


def done_said(result, label):
    """A press that went ahead: every failure said, and a half-change said by the result (``skipped``); a failure the
    result does not say is a STOP (§0.3's half-change)."""
    if result is None:
        return False
    for line in result.log_lines():
        say("        " + line)
    say(f"        W9c: built {[os.path.basename(b.saved or b.path) for b in result.built]}; inserted {result.inserted}; "
        f"deleted {result.deleted}; mates deleted {result.mates_deleted}; mates made {result.mates_made}; remade in "
        f"modes {result.remade_in_modes}; bands added {result.bands_added}, removed {result.bands_removed}; modes "
        f"added {result.modes_added}, removed {result.modes_removed}; took the active mode's state "
        f"{result.took_active_state}; flags lost {result.flags_lost}; not resolved {result.not_resolved}")
    if result.failures and not result.skipped:
        A.stop(f"{label}: the press failed with {result.failures} and the result says nothing of what it left undone "
               "(§0.3: a half-change the result does not say)")
    return result.ok


def in_place_fact(result):
    if result is None:
        return None
    return {k: getattr(result, k) for k in ("inserted", "deleted", "mates_deleted", "mates_made", "remade_in_modes",
                                            "bands_added", "bands_removed", "modes_added", "modes_removed",
                                            "took_active_state", "flags_lost", "not_resolved", "ratios",
                                            "senses_unread", "turned_round", "failures", "skipped")}


def sleeve_read(label, path, steps=()):
    """RangeSlv's part read: its globals, every feature (name, type, code), the user's groove's dimensions (its sketch's
    and its cut's), every face (W9b's ``part_faces``) and, given ``steps`` (the step planes' z), W9b's step-face read;
    GetSaveFlag before and after."""
    def work(s):
        doc = s._doc()  # noqa: SLF001
        out = {"flag_before": bool(call(doc, "GetSaveFlag")), "globals": s.equation_values(),
               "features": [(f.name, f.type_name, f.code) for f in s.feature_states()], "dims": []}
        for name in (f"{GROOVE['name']} Sketch", GROOVE["name"]):
            try:
                out["dims"] += [(n, round(v * 1000.0, 9)) for n, v in s.feature_dimensions(name)]
            except Exception as exc:  # noqa: BLE001 - said, and compared as said
                out["dims"].append((name, f"unread: {type(exc).__name__}"))
        out["faces"] = B.part_faces(s)
        if steps:
            try:
                out["steps"] = B.step_faces(s, steps)
            except Exception as exc:  # noqa: BLE001 - a fact; it never fails the part
                out["steps"] = f"unread: {type(exc).__name__}: {exc}"
        out["flag_after"] = bool(call(doc, "GetSaveFlag"))
        return out
    got = run(f"{label}: RangeSlv's part", job(path, work), 600)
    if got["flag_after"] and not got["flag_before"]:
        A.stop(f"{label}: reading RangeSlv's part marked it modified (§0.3)")
    return got


def master_of(key, section, builder):
    """A kept master: the path given, this <out>'s, or built here first by its section."""
    if MASTERS.get(key):
        return MASTERS[key]
    here = os.path.join(OUT, section + W.MASTER_SUFFIX)
    if not os.path.isdir(here):
        if os.path.exists(os.path.join(OUT, section)):
            raise AssertionError(f"{section} ran earlier in this <out> and kept no master")
        say(f"fresh   no {section}{W.MASTER_SUFFIX} in this <out>: {key} runs first")
        builder(RESULT["sections"].setdefault(key, {}))
    if not os.path.isdir(here):
        raise AssertionError(f"{key} kept no {section}{W.MASTER_SUFFIX}")
    MASTERS[key] = here
    return here


def fixed_master():
    return master_of("fixed", "fixed-updated", section_fixed)


def proposed(name, value, evidence):
    RESULT["proposal"][name] = value
    RESULT["proposal"][f"{name}_evidence"] = evidence
    say(propose(name, value, evidence))


# -- fixed: the plan's Done-when ------------------------------------------------------------------------------------------


def section_fixed(out):
    stems = GATES["fixed"]
    say("== fixed  the plan's Done-when (§5 W9c): a copy of setup.master (RangeBox with the user's work and the keyway "
        "in Sun's part) with a user groove cut in RangeSlv's part; the workbook edited in Excel to RangeBox_Fixed; the "
        f"gates' refusal with findings {[finding_name(s) for s in stems]} as they stand, then patched True in this "
        "process; one Update: Hub built, inserted and mated (M5, M6), RangeSlv's bands given in place (M8); every user "
        "item as it was; each mode as §3; the record; a second press quiet")
    rb, fx, _ = specs()
    folder, path, book, desk = A.copy_desk(A.user_master(), "fixed-updated", "RangeBox.xlsx")
    kept = ""
    clean = {}
    try:
        same_sheets("fixed", desk, rb)
        box = desk.record.gearbox
        modes, users, mates = list(box.modes), A.rb_users(), list(A.RB_USER_MATES)
        sleeve, sun = gear_entry(box, "RangeSlv"), gear_entry(box, "Sun")
        sun_features = run("fixed: Sun's part", job(sun.part, lambda s: [(f.name, f.code) for f in s.feature_states()]))
        check(("User Keyway", 0) in sun_features, f"fixed: the user's keyway is in Sun's part (setup made it), code 0: "
                                                  f"{[f for f in sun_features if f[0].startswith('User')]}")
        say("step    fixed: the user's groove in RangeSlv's part (an axial Ø2 cut through the sleeve's wall, by the "
            "session's own sketch and cut calls, as W9a's keyway; a ring groove would need a revolve cut, not proven)")
        A.keyway("fixed", sleeve.part, name=GROOVE["name"], at=GROOVE["at"], radius=GROOVE["radius"])
        A.save_user(folder, "the user's groove in RangeSlv's part")
        groove_before = out["groove_before"] = sleeve_read("fixed, the groove made", sleeve.part)
        check(bool(groove_faces(groove_before["faces"])), f"fixed: the groove's faces are in RangeSlv's part: "
                                                          f"{groove_faces(groove_before['faces'])}")
        quiet, _ = A.press(desk, "fixed: a quiet press (the inventory read again, the groove in it)")
        check(quiet is not None and quiet.placed == [] and any(f.name == GROOVE["name"] for f in (
            desk.record.gearbox.user_work.features if desk.record.gearbox.user_work is not None else ())),
            f"fixed: the quiet press recorded the user's groove: {desk.error if quiet is None else 'ok'}")
        A.save_user(folder, "after the quiet press")

        say("-- fixed  the workbook edited to RangeBox_Fixed in Excel: RangeSlv's cells and Hub's row, the fixture's own")
        edit_live(desk, book, row_edits(rb, fx), "RangeBox -> RangeBox_Fixed")
        u = desk.update
        ip = u.in_place if u is not None else None
        check(u is not None and not u.structural and not u.needs_new_revision and ip is not None
              and [g.gear for g in ip.added] == ["Hub"] and [(b.gear, b.add) for b in ip.bands] == [("RangeSlv", True)],
              f"fixed: classify makes it one Update in place, Hub added and RangeSlv's bands given: structural "
              f"{u and list(u.structural)}; in place {ip}")
        say(f"summary {ui_text.update_summary(u) if u is not None else ''}")
        B.read_checks("fixed", desk, B.expected_fixed_warnings())
        out["refusal"] = gated_refusal("fixed, the gates as they stand", desk, folder, stems, sleeve.part)

        with patched(stems):
            desk.plan_solidworks()
            A.ahead_of(desk, "fixed, the findings patched, before the press")
            foreseen = foreseen_names(desk)
            check(not foreseen, f"fixed: with the findings patched the footer foresees nothing stopping the press: "
                                f"{[(p.kind, list(p.subjects)) for p in foreseen]}")
            before = every_mode("fixed, before the press", desk, users)
            shown = active_now(desk)            # after the every-mode read, which leaves the first mode showing
            files = B.documents_state("fixed", desk, folder)
            result, calls = A.press(desk, "fixed: RangeBox -> RangeBox_Fixed, one Update")
            out["press"], out["in_place"] = A._update_fact(desk, result), in_place_fact(result)  # noqa: SLF001
            if result is None:
                A.section_stop(f"fixed: the press with the findings patched raised: {desk.error}")
            ok = done_said(result, "fixed")
            check(ok, f"fixed: the Update ended ok: failures {result.failures}, skipped {result.skipped!r}")
            after_shown = active_now(desk)
            check(after_shown == shown, f"fixed: the mode showing before the press ({shown}) shows after it "
                                        f"({after_shown})")
            hub = dict(result.inserted).get("Hub", "")
            hub_part = next((b.saved or b.path for b in result.built if b.ok), "")
            made = dict(result.mates_made)
            clean["insert"] = check(
                [g for g, _ in result.inserted] == ["Hub"] and bool(hub) and len(result.built) == 1
                and bool(hub_part) and W.under(hub_part, folder) and os.path.isfile(hub_part)
                and all(set(made.get(n, ())) == set(modes) for n in HUB_OPS) and not result.not_resolved,
                f"fixed: Hub's part built ({os.path.basename(hub_part)}, in the copy), Hub inserted as {hub!r}, its "
                f"mates {list(HUB_OPS)} made and read on in every mode {modes} (M6): {made}; not resolved "
                f"{result.not_resolved}")
            clean["bands"] = check(result.bands_added == ["RangeSlv"] and not result.bands_removed,
                                   f"fixed: RangeSlv's bands given in place: {result.bands_added}")
            check("RangeSlv splined to Hub" not in result.senses_unread,
                  f"fixed: the spline's sense read (M6): unread {result.senses_unread}; turned round "
                  f"{result.turned_round}")
            pressed = desk.record.gearbox
            entries = {c.gear: c for c in pressed.components}
            check("Hub" in entries and entries["Hub"].name == hub and entries["RangeSlv"].name == sleeve.name
                  and store.same_path(entries["RangeSlv"].part, sleeve.part),
                  f"fixed: the record holds Hub as {entries.get('Hub') and entries['Hub'].name}; RangeSlv keeps its "
                  f"component {sleeve.name} and its file {os.path.basename(sleeve.part)}")
            B.hub_mates("fixed", desk, desk.plan)
            sidecar = store.read_sidecar(store.sidecar_path(sleeve.part))
            check(sidecar is not None and sidecar.schema_version == 2 and "Relief" in sidecar.record.features,
                  f"fixed: the sleeve's sidecar at schema 2 with Relief among its features: "
                  f"{sidecar.schema_version if sidecar else None}")

            say("-- fixed  M8: RangeSlv's part after the bands in place; the user's groove")
            zs = (EZ * B.PLANES[0], EZ * B.PLANES[1])
            sleeve_after = out["sleeve_after"] = sleeve_read("fixed, after the press", sleeve.part, steps=zs)
            g = sleeve_after["globals"]
            kept_groove = groove_kept(groove_before, sleeve_after)
            relief = [(n, c) for n, _, c in sleeve_after["features"] if n in RELIEF_FEATURES]
            bore, held = B.relief_bore(sleeve_after["faces"], min(zs), max(zs), B.RELIEF_D / 2)
            clean["m8"] = check(
                abs(g.get("Start Band", -1) - 5) < 1e-9 and abs(g.get("End Band", -1) - 5) < 1e-9
                and abs(g.get("Relief Diameter", -1) - B.RELIEF_D) < 1e-9 and len(relief) == len(RELIEF_FEATURES)
                and not any(c for _, c in relief) and held and not kept_groove,
                f"fixed: RangeSlv's part holds Start Band 5, End Band 5, Relief Diameter {B.RELIEF_D}, the relief's "
                f"five features in no error {relief}, the bore over the relief {bore}; the user's groove kept before "
                f"them, in no error, its dimensions and faces as before: {kept_groove or 'yes'}")
            if kept_groove:
                A.stop(f"fixed: the user's groove changed: {kept_groove} (§0.3)")
            faces = sleeve_after["faces"]
            f0 = B.end_areas(faces, 26.0).get(0.0)
            outer = B.outer_radius(faces, 26.0)
            if f0 and outer:
                B.step_report(out, sleeve_after.get("steps"), B.step_area(f0, outer, B.RELIEF_D / 2))
            else:
                say(f"fact    fixed: the step faces not judged: F0 {f0}, Ro {outer} not read from the faces")

            say("-- fixed  M5: Hub's state in every mode; every user item; each mode as §3")
            states = out["hub_states"] = states_by_mode("fixed", desk, [hub])
            clean["m5"] = check(all(states[m].get(hub) in RESOLVED for m in modes),
                                f"fixed: Hub ({hub}) reads resolved in every mode (M5): {states}")
            after = every_mode("fixed, after the press", desk, users)
            users_unchanged("fixed", before, after, users, mates)
            judged_modes("fixed", desk, out)
            B.nothing_written("fixed: nothing of the user's own files (Sprocket, Housing) written", {
                "flags": {}, "times": {n: t for n, t in files["times"].items() if n in ("Sprocket.SLDPRT",
                                                                                         "Housing.SLDPRT")}},
                {"flags": {}, "times": {n: t for n, t in B.documents_state("fixed", desk, folder)["times"].items()
                                        if n in ("Sprocket.SLDPRT", "Housing.SLDPRT")}})
            A.ahead_of(desk, "fixed, after the press")
            check(not foreseen_names(desk), "fixed: after the press the footer foresees nothing in place")

            say("-- fixed  saved as the user would; a second press is quiet")
            A.save_user(folder, "the Update's result")
            frames_before, flags_before = W.gear_frames(CTX["worker"], desk), W.gearbox_flags(CTX["worker"], desk)
            second, _ = A.press(desk, "fixed: a second press")
            clean["quiet"] = check(second is not None and second.placed == [] and not second.changed and second.ok
                                   and not second.inserted and not second.bands_added,
                                   f"fixed: the second press does nothing: {desk.error if second is None else 'ok'}")
            if second is not None:
                W.check_quiet_update(CTX["worker"], desk, second, "fixed: the second press", frames_before,
                                     flags_before)
        kept = A.w8_step(W.keep_master, CTX["worker"], folder, "fixed-updated")
        MASTERS["fixed"] = kept
        check(bool(kept), f"fixed: kept as fixed-updated.master: {kept}")
    finally:
        if not kept and not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], folder, "fixed-updated")
        out["clean"] = clean
        insert_ok = bool(clean) and all(clean.get(k) for k in ("insert", "m5", "quiet"))
        proposed(finding_name("UPDATE_INSERTS_A_GEAR"), True if insert_ok else None,
                 f"fixed: Hub built, inserted, mated and resolved in every mode, every user item kept, each mode "
                 f"§3's, the second press quiet: {clean}")
        proposed(finding_name("UPDATE_BANDS_IN_PLACE"), True if bool(clean) and all(
            clean.get(k) for k in ("bands", "m8", "quiet")) else None,
            f"fixed, giving bands only (the taking away has no legal edit on RangeBox_Fixed; see bands-off): {clean}")


# -- modes: M10 -------------------------------------------------------------------------------------------------------


def took_active_read(label, desk, mode, mates, comps):
    """In ``mode`` (a mode just added): each user mate's flag there, read unshown (``mate_suppression``), and each user
    component's state, read with it shown; the mode showing before shown again."""
    def work(s):
        first = s.active_configuration()
        flags = {}
        for i, name in enumerate(mates):
            s.find_mate(f"ta{i}", name)
            flags[name] = bool(s.mate_suppression(f"ta{i}", [mode]).get(mode))
        s.show_configuration(mode)
        states = {c.name: c.state for c in s.components() if c.name in comps}
        s.show_configuration(first)
        return flags, states
    return run(f"{label}: the user's items in {mode}", job(desk.record.gearbox.assembly, work), 600)


def person_flags(desk, folder, mate, suppressed, modes_):
    """The user suppresses (or turns on) one of their mates in some modes, in SolidWorks, and saves; read back."""
    box = desk.record.gearbox

    def work(s):
        s.find_mate("pf", mate)
        s.set_mate_suppressed_in("pf", suppressed, modes_)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        return s.mate_suppression("pf", list(box.modes))
    got = run(f"the user sets {mate} in {modes_}", job(box.assembly, work), 300)
    A.save_user(folder, f"{mate} {'suppressed' if suppressed else 'on'} in {modes_}")
    want = {m: (suppressed if m in modes_ else got[m]) for m in box.modes}
    if got != want:
        A.stop(f"the user's flag on {mate} did not read back as set: {got} (§0.3)")
    say(f"person  {mate} {'suppressed' if suppressed else 'on'} in {modes_}: flags {got}")
    return got


def configurations_now(desk):
    return run("the configurations", job(desk.record.gearbox.assembly, lambda s: list(s.configurations())), 300)


def section_modes(out):
    add_stems, rm_stems = GATES["add"], GATES["remove a mode"]
    say(f"== modes  M10 on a copy of fixed-updated.master: a Modes row {ADDED_MODE} (RangeSlv at {ADDED_AT}) added; "
        f"{REMOVED_MODE} removed while another shows, after the user suppresses {USER_OFF_IN_N} there; removing the "
        f"mode showing refused by name; the first mode {FIRST_MODE} removed, {NEXT_FIRST} becoming the record's first. "
        f"Each gate's refusal first ({[finding_name(s) for s in add_stems + rm_stems]})")
    _, fx, fx_h2 = specs()
    hlh2, hl, lh2 = (modes_of(fx_h2, ("H", "L", ADDED_MODE)), modes_of(fx_h2, ("H", "L")),
                     modes_of(fx_h2, ("L", ADDED_MODE)))
    folder, path, book, desk = A.copy_desk(fixed_master(), "modes", "RangeBox.xlsx")
    clean = {}
    try:
        same_sheets("modes", desk, fx)
        box = desk.record.gearbox
        users, mates = A.rb_users(), list(A.RB_USER_MATES)
        sleeve = gear_entry(box, "RangeSlv").part
        if active_now(desk) in (REMOVED_MODE, FIRST_MODE):
            person_shows(desk, folder, NEXT_FIRST)

        say(f"-- modes  {ADDED_MODE} added")
        edit_live(desk, book, row_edits(fx, fx_h2), f"a Modes row {ADDED_MODE}")
        u = desk.update
        check(u is not None and not u.structural and u.in_place.modes_added == (ADDED_MODE,),
              f"modes: classify adds {ADDED_MODE} in place: {u and (list(u.structural), u.in_place.modes_added)}")
        out["add_refusal"] = gated_refusal(f"modes, {ADDED_MODE} added, the gate as it stands", desk, folder, add_stems,
                                           sleeve)
        with patched(add_stems):
            desk.plan_solidworks()
            A.ahead_of(desk, f"modes, {ADDED_MODE}, the finding patched")
            before = every_mode(f"modes, before {ADDED_MODE}", desk, users)
            shown = active_now(desk)
            result, _ = A.press(desk, f"modes: {ADDED_MODE} added")
            out["add"] = in_place_fact(result)
            if result is None:
                A.section_stop(f"modes: the press adding {ADDED_MODE} raised: {desk.error}")
            ok = done_said(result, f"modes, {ADDED_MODE}")
            after_shown = active_now(desk)
            names = configurations_now(desk)
            flags, states = took_active_read("modes", desk, ADDED_MODE, mates, users)
            differ = took_active_differs(result.took_active_state, ADDED_MODE, flags, states, swbuild._STATE_WORDS)  # noqa: SLF001
            clean["add"] = check(ok and result.modes_added == [ADDED_MODE] and ADDED_MODE in names
                                 and after_shown == shown and not differ
                                 and list(desk.record.gearbox.modes) == list(MODES) + [ADDED_MODE],
                                 f"modes: {ADDED_MODE} made ({names}), the record's modes "
                                 f"{list(desk.record.gearbox.modes)}, {shown} showing before and after "
                                 f"({after_shown}); each user item said as read there: {differ or 'yes'}")
            after = every_mode(f"modes, after {ADDED_MODE}", desk, users)
            users_unchanged(f"modes, {ADDED_MODE}", before, after, users, mates)
            judged_modes(f"modes, {ADDED_MODE}", desk, out.setdefault("judged_add", {}), section3=False,
                         against={"H": "H", "N": "N", "L": "L", ADDED_MODE: ADDED_AT})
        proposed(finding_name("UPDATE_ADDS_A_MODE"), True if clean.get("add") else None,
                 f"modes: {ADDED_MODE} added from the mode showing, every flag and slide value read back as the record, "
                 f"the user's items there said as read: {clean.get('add')}")

        say(f"-- modes  {REMOVED_MODE} removed while {shown} shows, the user's {USER_OFF_IN_N} suppressed there first")
        person_flags(desk, folder, USER_OFF_IN_N, True, [REMOVED_MODE])
        edit_live(desk, book, row_edits(fx_h2, hlh2), f"Modes row {REMOVED_MODE} cleared")
        u = desk.update
        check(u is not None and not u.structural and u.in_place.modes_removed == (REMOVED_MODE,),
              f"modes: classify removes {REMOVED_MODE} in place: {u and (list(u.structural), u.in_place.modes_removed)}")
        out["remove_refusal"] = gated_refusal(f"modes, {REMOVED_MODE} removed, the gate as it stands", desk, folder,
                                              rm_stems, sleeve)
        with patched(rm_stems):
            desk.plan_solidworks()
            A.ahead_of(desk, f"modes, {REMOVED_MODE} removed, the finding patched")
            before = every_mode(f"modes, before {REMOVED_MODE} goes", desk, users)
            every_before = B.mode_read(f"modes, before {REMOVED_MODE} goes", desk)
            shown = active_now(desk)
            lost = flags_lost_expected(before["by_mode"], mates, shown, REMOVED_MODE)
            say(f"fact    modes: the user's flags in {REMOVED_MODE} that differ from {shown}'s, read before: {lost}")
            result, _ = A.press(desk, f"modes: {REMOVED_MODE} removed")
            out["remove"] = in_place_fact(result)
            if result is None:
                A.section_stop(f"modes: the press removing {REMOVED_MODE} raised: {desk.error}")
            ok = done_said(result, f"modes, {REMOVED_MODE}")
            after_shown = active_now(desk)
            names = configurations_now(desk)
            remaining = [m for m in desk.record.gearbox.modes]
            every_after = B.mode_read(f"modes, after {REMOVED_MODE} went", desk)
            unchanged = {n: (every_before["flags"].get(n), f) for n, f in every_after["flags"].items()
                         if {m: v for m, v in (every_before["flags"].get(n) or {}).items() if m in remaining} != f}
            unchanged.update({n: (every_before["values"].get(n), v) for n, v in every_after["values"].items()
                              if {m: x for m, x in (every_before["values"].get(n) or {}).items() if m in remaining} != v})
            clean["remove"] = check(
                ok and result.modes_removed == [REMOVED_MODE] and REMOVED_MODE not in names
                and remaining == ["H", "L", ADDED_MODE] and sorted(result.flags_lost) == lost and not unchanged
                and after_shown == shown,
                f"modes: {REMOVED_MODE} deleted ({names}), the record's modes {remaining}; the user's flags lost said "
                f"{sorted(result.flags_lost)} as read before {lost}; every other configuration's flags and slide values "
                f"as before: {unchanged or 'yes'}; {shown} showing")
            after = every_mode(f"modes, after {REMOVED_MODE} went", desk, users)
            users_unchanged(f"modes, {REMOVED_MODE} gone", before, after, users, mates)

        say(f"-- modes  removing the mode showing: {ADDED_MODE} shown by the user, its row cleared; refused by name")
        person_shows(desk, folder, ADDED_MODE)
        cleared = edit_live(desk, book, row_edits(hlh2, hl), f"Modes row {ADDED_MODE} cleared while it shows")
        u = desk.update
        check(u is not None and not u.structural and u.in_place.modes_removed == (ADDED_MODE,),
              f"modes: classify removes {ADDED_MODE} in place (the showing is read only at the press): "
              f"{u and (list(u.structural), u.in_place.modes_removed)}")
        foreseen = foreseen_names(desk)
        say(f"fact    modes: the footer cannot foresee the mode showing (C12): foreseen "
            f"{[(p.kind, list(p.subjects)) for p in foreseen]}")
        with patched(rm_stems):
            desk.plan_solidworks()

            def showing(result, error):
                problems = list(getattr(error, "problems", ()) or ())
                for p in problems:
                    say(f"        {p.kind} {list(p.subjects)}: {p.sentence}")
                mine = [p for p in problems if p.kind == swbuild.PROBLEM_MODE_SHOWING]
                return (result is None and isinstance(error, swbuild.UserWorkRefused) and bool(mine)
                        and ADDED_MODE in mine[0].subjects and ADDED_MODE in mine[0].sentence
                        and getattr(error, "user_work", "unread") is None,
                        f"refused before any write as the mode showing, naming {ADDED_MODE}, the user's work unread "
                        f"(C12): {[(p.kind, list(p.subjects)) for p in problems]}")
            error = refused_without_writing(f"modes, {ADDED_MODE} removed while it shows", desk, folder, sleeve,
                                            showing)
            out["showing_refusal"] = str(error)
            clean["showing"] = isinstance(error, swbuild.UserWorkRefused)

            say(f"-- modes  {ADDED_MODE}'s row put back, the first mode {FIRST_MODE} removed while {ADDED_MODE} shows")
            back = put_back(cleared, sheet_rows(fx_h2)["Modes"][-1])
            edit_live(desk, book, row_edits(hlh2, lh2), f"{ADDED_MODE} put back, {FIRST_MODE} cleared", cells=back)
            u = desk.update
            check(u is not None and not u.structural and u.in_place.modes_removed == (FIRST_MODE,)
                  and u.in_place.first_mode == NEXT_FIRST,
                  f"modes: classify removes {FIRST_MODE}, {NEXT_FIRST} the record's first: "
                  f"{u and (list(u.structural), u.in_place.modes_removed, u.in_place.first_mode)}")
            A.ahead_of(desk, f"modes, {FIRST_MODE} removed")
            before = every_mode(f"modes, before {FIRST_MODE} goes", desk, users)
            person_shows(desk, folder, ADDED_MODE)       # the every-mode read leaves the first mode showing
            result, _ = A.press(desk, f"modes: {FIRST_MODE} removed")
            out["remove_first"] = in_place_fact(result)
            if result is None:
                A.section_stop(f"modes: the press removing {FIRST_MODE} raised: {desk.error}")
            ok = done_said(result, f"modes, {FIRST_MODE}")
            after_shown = active_now(desk)
            names = configurations_now(desk)
            clean["first"] = check(
                ok and result.modes_removed == [FIRST_MODE] and FIRST_MODE not in names
                and list(desk.record.gearbox.modes) == [NEXT_FIRST, ADDED_MODE] and after_shown == ADDED_MODE,
                f"modes: {FIRST_MODE} deleted ({names}); the record's modes {list(desk.record.gearbox.modes)}, "
                f"{NEXT_FIRST} first; {ADDED_MODE} showing before and after")
            after = every_mode(f"modes, after {FIRST_MODE} went", desk, users)
            users_unchanged(f"modes, {FIRST_MODE} gone", before, after, users, mates)
            judged_modes(f"modes, {FIRST_MODE} gone", desk, out.setdefault("judged_first", {}), section3=False,
                         against={NEXT_FIRST: NEXT_FIRST, ADDED_MODE: ADDED_AT})
    finally:
        if not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], folder, "modes")
        out["clean"] = clean
        removed_ok = all(clean.get(k) for k in ("remove", "showing", "first"))
        proposed(finding_name("UPDATE_REMOVES_A_MODE"), True if removed_ok else None,
                 f"modes: {REMOVED_MODE} deleted unshown with the user's lost flag said, the mode showing refused, the "
                 f"first mode deleted and the next made the record's first: {clean}")


# -- remove: a gear that anchors none taken out ---------------------------------------------------------------------


def without_gear(spec, gear):
    return dataclasses.replace(spec, gears=tuple(g for g in spec.gears if g.id != gear),
                               meshes=tuple(m for m in spec.meshes if gear not in (m.a, m.b)))


def remove_reducer(out):
    say(f"-- remove  {REMOVED_REDUCER} out of a copy of the 12 : 1 (no user component, no modes): P1's route, set on "
        "both versions, so no gate to patch")
    spec = A.spec_reducer()
    folder, path, book, desk = A.copy_desk(A.reducer_master(), "remove-reducer", "Reducer_12to1.xlsx")
    ok = False
    try:
        same_sheets("remove, the 12 : 1", desk, spec)
        box = desk.record.gearbox
        gone = gear_entry(box, REMOVED_REDUCER)
        others = [(g, n) for g, n in W.bodies(box) if g != REMOVED_REDUCER]
        edit_live(desk, book, row_edits(spec, without_gear(spec, REMOVED_REDUCER)), f"{REMOVED_REDUCER}'s rows cleared")
        u = desk.update
        removed = u.in_place.removed if u is not None else ()
        check(u is not None and not u.structural and [r.gear for r in removed] == [REMOVED_REDUCER],
              f"remove: classify takes {REMOVED_REDUCER} out in place: {u and (list(u.structural), removed)}")
        A.ahead_of(desk, f"remove, {REMOVED_REDUCER}")
        foreseen = foreseen_names(desk)
        check(not foreseen, f"remove: the footer foresees nothing stopping it: {[(p.kind, list(p.subjects)) for p in foreseen]}")
        before = A.read_now(f"remove, before {REMOVED_REDUCER} goes", box.assembly, folder, others, [])
        result, _ = A.press(desk, f"remove: {REMOVED_REDUCER} taken out")
        out["reducer"] = in_place_fact(result)
        if result is None:
            A.section_stop(f"remove: the press taking {REMOVED_REDUCER} out raised: {desk.error}")
        done = done_said(result, f"remove {REMOVED_REDUCER}")
        after = A.read_now(f"remove, after {REMOVED_REDUCER} went", box.assembly, folder, others, [])
        components = run("remove: components", job(box.assembly, lambda s: [c.name for c in s.components()]))
        wanted_gone = set(removed[0].mates) if removed else set()
        kept_before = set(before["mates"]) - wanted_gone
        moved, at = W.frames_gap(after["frames"], before["frames"])
        rec = desk.record.gearbox
        ok = check(done and result.deleted == [(REMOVED_REDUCER, gone.name)]
                   and set(result.mates_deleted) == wanted_gone and gone.name not in components
                   and not (wanted_gone & set(after["mates"])) and kept_before <= set(after["mates"])
                   and moved <= TOL and gear_entry(rec, REMOVED_REDUCER) is None
                   and not any(wanted_gone & {m.name} for m in rec.mates) and os.path.isfile(gone.part),
                   f"remove: {REMOVED_REDUCER} ({gone.name}) taken out with its mates {sorted(result.mates_deleted)} "
                   f"(each read gone by name), every other mate there, nothing else moved ({moved:.1e} at {at or '-'}), "
                   f"the record without it, its part's file still on disk ({os.path.basename(gone.part)}); record parts "
                   f"{[os.path.basename(p.path) for p in desk.record.parts]}")
    finally:
        if not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], folder, "remove-reducer")
    return ok


def remove_setup(out):
    gear = REMOVED_SETUP
    references = finding_name("EXTERNAL_REFERENCES_READ")
    say(f"-- remove  {gear} out of a copy of setup.master: refused before any write, the user's components there and "
        f"the external-references read unmeasured (C4, findings.{references} {getattr(findings, references, None)!r}); "
        f"then with a user lock on {gear}, refused naming it too")
    rb, _, _ = specs()
    folder, path, book, desk = A.copy_desk(A.user_master(), "remove-setup", "RangeBox.xlsx")
    ok = []
    try:
        same_sheets("remove, setup", desk, rb)
        box = desk.record.gearbox
        hd = gear_entry(box, gear)
        edit_live(desk, book, row_edits(rb, without_gear(rb, gear)), f"{gear}'s row cleared")
        u = desk.update
        check(u is not None and not u.structural and [r.gear for r in u.in_place.removed] == [gear],
              f"remove: classify takes {gear} out in place: {u and (list(u.structural), u.in_place.removed)}")
        A.ahead_of(desk, f"remove, {gear}, the user's components there")
        foreseen = foreseen_names(desk)
        check({p.kind for p in foreseen} == {swbuild.PROBLEM_REFERENCES}, f"remove: the footer foresees the "
              f"references refusal (C4): {[(p.kind, list(p.subjects)) for p in foreseen]}")
        A.save_user(folder, f"before {gear} goes")
        files = B.documents_state("remove", desk, folder)
        problems = A.refuse_press(f"remove {gear}, C4", desk, folder, {swbuild.PROBLEM_REFERENCES}, (),
                                  (references,), part=hd.part, save=False)
        B.nothing_written(f"remove {gear}, C4, by file times and save flags", files,
                          B.documents_state("remove", desk, folder))
        ok.append(any(p.kind == swbuild.PROBLEM_REFERENCES for p in problems))
        out["references"] = [p.sentence for p in problems]

        say(f"-- remove  the user locks a fifth sprocket to {gear}; the press refuses naming that lock")
        axes = {s.shaft: s.axis_name for s in A.wb_layout.shaft_layouts(desk.a.spec)}
        A.add_user_work("remove", desk, folder, (("u5", "Sprocket.SLDPRT", (0.0, 0.0, 100.0), "Sprocket-5"),),
                        (("ua5", "coincident", "u5:Gear Axis", f"lay:{axes['Input']}", 0.0, "UserAxis5", {}),
                         ("ul5", "lock", "hd", "u5", 0.0, "UserLock5", {})),
                        refs={"lay": box.layout_component, "hd": hd.name})
        A.save_user(folder, f"the user's lock on {gear}")
        A.ahead_of(desk, f"remove, {gear}, with the user's lock on it")
        files = B.documents_state("remove", desk, folder)
        problems = A.refuse_press(f"remove {gear}, the user's lock on it", desk, folder,
                                  {swbuild.PROBLEM_REMOVED, swbuild.PROBLEM_REFERENCES}, ("UserLock5",), (references,),
                                  users=A.rb_users() + ["Sprocket-5"], part=hd.part, save=False)
        B.nothing_written(f"remove {gear}, the user's lock, by file times and save flags", files,
                          B.documents_state("remove", desk, folder))
        named = [p for p in problems if p.kind == swbuild.PROBLEM_REMOVED]
        ok.append(bool(named) and "UserLock5" in named[0].mates and gear in " ".join(named[0].subjects))
        out["removed"] = [p.sentence for p in problems]
    finally:
        if not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], folder, "remove-setup")
    return all(ok) and len(ok) == 2


def section_remove(out):
    say("== remove  a gear that anchors none taken out by Update: G4 from the 12 : 1 where nothing of the user's is; "
        "HighDog from RangeBox with the user's work refused before any write (C4), and with a user lock on it, naming "
        "the lock")
    out["reducer_clean"] = remove_reducer(out)
    out["setup_clean"] = remove_setup(out)
    say(f"fact    remove: the removal gates are P1's, set on both versions; {finding_name('EXTERNAL_REFERENCES_READ')} "
        "stays None: a removal with any user component refuses (C4) until m4's read is measured and set")


# -- remake: a tooth change with modes --------------------------------------------------------------------------------


def section_remake(out):
    stems = GATES["remake"]
    say(f"== remake  Sun 29 -> {GEARS_TEETH['Sun']}, Planet 13 -> {GEARS_TEETH['Planet']}, Ring 55 -> "
        f"{GEARS_TEETH['Ring']} on a copy of fixed-updated.master (the centre distance and the planets' spacing kept): "
        "the gear mates of a gearbox with modes made again (ruling 9.16 lifted), first refused with "
        f"findings.{finding_name(stems[0])} as it stands")
    _, fx, _ = specs()
    teeth = with_teeth(fx)
    folder, path, book, desk = A.copy_desk(fixed_master(), "remake", "RangeBox.xlsx")
    clean = False
    try:
        same_sheets("remake", desk, fx)
        box = desk.record.gearbox
        users, mates = A.rb_users(), list(A.RB_USER_MATES)
        sun = gear_entry(box, "Sun").part
        edit_live(desk, book, row_edits(fx, teeth), "the teeth")
        u = desk.update
        ratios = list(u.ratios) if u is not None else []
        check(u is not None and not u.structural and not u.needs_new_revision and not u.in_place and ratios,
              f"remake: classify makes it a value Update remaking {ratios}: {u and list(u.structural)}")
        finding = finding_name(stems[0])
        if getattr(findings, finding, None) is not True:
            A.ahead_of(desk, f"remake, findings.{finding} {getattr(findings, finding, None)!r}")
            foreseen = foreseen_names(desk)
            check(any(finding in " ".join(p.subjects) + p.sentence for p in foreseen),
                  f"remake: the footer foresees the press refused naming {finding}")

            def build_error(result, error):
                return (result is None and isinstance(error, swbuild.BuildError)
                        and not isinstance(error, swbuild.UserWorkRefused) and finding in str(error),
                        f"refused before any write, naming {finding}: {type(error).__name__}: {error}")
            out["refusal"] = str(refused_without_writing("remake, the gate as it stands", desk, folder, sun,
                                                         build_error))
        with patched(stems):
            desk.plan_solidworks()
            A.ahead_of(desk, "remake, the finding patched")
            before = every_mode("remake, before", desk, users)
            result, _ = A.press(desk, "remake: the teeth")
            out["press"], out["in_place"] = A._update_fact(desk, result), in_place_fact(result)  # noqa: SLF001
            if result is None:
                A.section_stop(f"remake: the press with the finding patched raised: {desk.error}")
            ok = done_said(result, "remake")
            remade = set(result.remade_in_modes)
            clean = check(ok and set(ratios) <= set(result.ratios) and set(ratios) <= remade
                          and not (remade & set(result.senses_unread)) and not result.user_features_in_error,
                          f"remake: every gear mate {ratios} made again with modes ({sorted(remade)}), each one's sense "
                          f"read (unread {result.senses_unread}), the user's keyway in Sun's part not in error "
                          f"{[f.name for f in result.user_features_in_error]}")
            after = every_mode("remake, after", desk, users)
            users_unchanged("remake", before, after, users, mates)
            judged_modes("remake", desk, out.setdefault("judged", {}), section3=False,
                         against={m: m for m in MODES})
            l_ratio = next((m.ratio for m in desk.a.report.modes if m.name == "L"), None)
            check(l_ratio is not None and abs(l_ratio - REMAKE_RATIO_L) < 1e-9,
                  f"remake: the app's read gives L {l_ratio} (1 + 54/30 = {REMAKE_RATIO_L})")
    finally:
        if not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], folder, "remake")
        proposed(finding_name("UPDATE_MAKES_MATES_WITH_MODES"), True if clean else None,
                 "remake: gear mates of a gearbox with modes remade, flags and senses read in every mode; a coupling or "
                 f"sliding mesh newly made by Update is not exercised by any legal edit of these fixtures: {clean}")


# -- bands-off: the take-away side ------------------------------------------------------------------------------------


def section_bands_off(out):
    say("== bands-off  no legal edit takes the bands off RangeBox_Fixed's sleeve in place (the self-check searched): "
        "the read's refusal and Build again… said, nothing written; then, script-side only, the app's "
        "Session.suppress_feature on the copy's Relief, read back with the sleeve's mates in every mode, and on again")
    _, fx, _ = specs()
    folder, path, book, desk = A.copy_desk(fixed_master(), "bands-off", "RangeBox.xlsx")
    clean = False
    try:
        same_sheets("bands-off", desk, fx)
        box = desk.record.gearbox
        sleeve = gear_entry(box, "RangeSlv").part
        before = B.documents_state("bands-off", desk, folder)
        alone = dataclasses.replace(fx, gears=tuple(dataclasses.replace(g, start_band="", end_band="")
                                                    if g.id == "RangeSlv" else g for g in fx.gears))
        edit_live(desk, book, row_edits(fx, alone), "the bands taken off alone")
        f = desk.say_footer("bands-off, the bands alone")
        refusal = desk.a.lay_out_refusal()
        check(refusal.startswith("Fix the workbook") and "jammed" in refusal and not f.update_enabled
              and not f.build_enabled, f"bands-off: refused at the workbook, nothing offered: {refusal[:160]!r}")
        as_rb = dataclasses.replace(alone, gears=tuple(
            dataclasses.replace(g, at="-24.5", face_width="10", slides="H=-5, N=0, L=+5") if g.id == "RangeSlv" else g
            for g in alone.gears if g.id != "Hub"))
        edit_live(desk, book, row_edits(alone, as_rb), "RangeSlv as RangeBox has it, Hub's row cleared")
        u = desk.update
        f = desk.say_footer("bands-off, as RangeBox")
        check(u is not None and u.needs_new_revision and any("anchors RangeSlv" in s for s in u.structural)
              and f.build_enabled and f.build_action == ui_text.BUILD_AGAIN,
              f"bands-off: Build again…, Hub named as RangeSlv's anchor: {u and list(u.structural)}")
        B.nothing_written("bands-off, the two edits", before, B.documents_state("bands-off", desk, folder))

        say("-- bands-off  script-side: Session.suppress_feature('Relief') on the copy's sleeve (C8's call, new to the "
            "app on a part's feature), read back; the assembly read in every mode; then turned back on")

        def toggle(on):
            def work(s):
                s.suppress_feature("Relief", not on)
                rebuilt = bool(s.rebuild())
                return {"rebuilt": rebuilt, "volume": s.volume_mm3(),
                        "features": [(n.name, n.code) for n in s.feature_states() if n.name in RELIEF_FEATURES]}
            return work
        pairs = W.bodies(box)
        start = run("bands-off: the sleeve", job(sleeve, lambda s: {"volume": s.volume_mm3(), "features": [
            (n.name, n.code) for n in s.feature_states() if n.name in RELIEF_FEATURES]}))
        off = out["suppressed"] = run("bands-off: Relief suppressed", job(sleeve, toggle(False)))
        every_off = A.read_every("bands-off, Relief suppressed", box.assembly, pairs, list(box.modes))
        on = out["unsuppressed"] = run("bands-off: Relief on again", job(sleeve, toggle(True)))
        every_on = A.read_every("bands-off, Relief on again", box.assembly, pairs, list(box.modes))
        sleeve_mates = [m.name for m in box.mates if "RangeSlv" in m.gears]
        errors = {mode: {n: c for n, (c, sup) in every["mates"][mode].items() if n in sleeve_mates and c and not sup}
                  for every in (every_off, every_on) for mode in box.modes}
        errors = {m: e for m, e in errors.items() if e}
        clean = check(off["rebuilt"] and on["rebuilt"] and off["volume"] > start["volume"] + 1.0
                      and abs(on["volume"] - start["volume"]) <= 1e-6 * start["volume"]
                      and on["features"] == start["features"] and not errors,
                      f"bands-off: Relief suppressed (volume {start['volume']:.3f} -> {off['volume']:.3f} mm³, the teeth "
                      f"back over the relief) and on again ({on['volume']:.3f}), its features {on['features']} as "
                      f"before (no second relief), RangeSlv's mates in no error in any mode: {errors or 'none'}")
    finally:
        if not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], folder, "bands-off", save=False)
        out["clean"] = clean
        RESULT["proposal"]["UPDATE_BANDS_IN_PLACE_taking_away_script_side"] = clean
        say(f"fact    bands-off: the taking away, script-side (not the window's path, no legal edit reaches it): "
            f"{clean}; {finding_name('UPDATE_BANDS_IN_PLACE')} is proposed by fixed from the giving alone")


# -- m4: the external-references read, a probe ------------------------------------------------------------------------

M4_CALLS = ("IComponent2.ListExternalFileReferencesCount() and ListExternalFileReferences2(9 out arrays) on the "
            "component; IModelDocExtension.ListExternalFileReferencesCount() and ListExternalFileReferences(9 out "
            "arrays) on its part (the installed API help's documented forms; the macro database's ledger lists "
            "ListExternalFileReferences on IModelDoc2 and ListExternalFileReferences2 on IFeature as 'Unverified', "
            "the rest has no entry); ISldWorks.GetDocumentDependencies2(path, False, True, False) ('Verified' in the "
            "ledger for a closed file's references), with the assembly's own as its positive control")


def m4_read(folder, targets, asm):
    """Each of ``targets`` (component Name2s) read by every candidate, GetSaveFlag of the copy's documents around each;
    the assembly's dependencies as the control. A candidate that raises is its exact error."""
    import pythoncom
    from win32com.client import VARIANT

    def outs(kinds):
        made = {"v": lambda: VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None),
                "i": lambda: VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0),
                "s": lambda: VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, "")}
        return [made[k]() for k in kinds]

    def plain(v):
        v = getattr(v, "value", v)
        if isinstance(v, (bool, int, float, str)) or v is None:
            return v
        if isinstance(v, (list, tuple)):
            return [plain(x) for x in v]
        return repr(v)

    def member(obj, name, *args):
        value = call(obj, name, *args)
        return swcom._guarded(name, value) if type(value).__name__ == "method" else value  # noqa: SLF001

    def work(s):
        out = {}

        def attempt(where, label, fn):
            before = W.folder_flags(s, folder)
            try:
                value = fn()
            except Exception as exc:  # noqa: BLE001 - the exact error is the finding
                value = f"raised {type(exc).__name__}: {exc}"
            marked = sorted(n for n, f in W.folder_flags(s, folder).items() if f and not before.get(n))
            out.setdefault(where, {})[label] = {"answer": value, "marked": marked}

        app = s._app  # noqa: SLF001
        for i, name in enumerate(targets):
            s.find_component(f"m4{i}", name, lightweight_ok=True)
            comp = s.raw_component(f"m4{i}")
            part = s.component_path(f"m4{i}")
            doc = call(comp, "GetModelDoc2")

            def listed(obj, member_name, kinds):
                holders = outs(kinds)
                back = call(obj, member_name, *holders)
                return {"returned": plain(back), "outs": [plain(h) for h in holders]}
            attempt(name, "IComponent2.ListExternalFileReferencesCount",
                    lambda: plain(member(comp, "ListExternalFileReferencesCount")))
            attempt(name, "IComponent2.ListExternalFileReferences2",
                    lambda: listed(comp, "ListExternalFileReferences2", "vvvvvvvis"))
            attempt(name, "IModelDocExtension.ListExternalFileReferencesCount",
                    lambda: plain(member(call(doc, "Extension"), "ListExternalFileReferencesCount")))
            attempt(name, "IModelDocExtension.ListExternalFileReferences",
                    lambda: listed(call(doc, "Extension"), "ListExternalFileReferences", "vvvvvvvis"))
            attempt(name, "ISldWorks.GetDocumentDependencies2",
                    lambda: plain(member(app, "GetDocumentDependencies2", part, False, True, False)))
        attempt("the assembly (control)", "ISldWorks.GetDocumentDependencies2",
                lambda: plain(member(app, "GetDocumentDependencies2", asm, False, True, False)))
        return out
    return work


def section_m4(out):
    references = finding_name("EXTERNAL_REFERENCES_READ")
    say(f"== m4  a probe (no app code makes this read yet; C4's refusal stands meanwhile): the external-references "
        f"read on the user's parts, none of which holds a reference, and Sun's for comparison; findings.{references} "
        f"{getattr(findings, references, None)!r}")
    say(f"NEW     {M4_CALLS}")
    say("fact    m4: a user part with an in-context reference to an app gear is not made: it needs editing the part in "
        "the assembly's context (IAssemblyDoc.EditPart2) and a sketch converting an app gear's edge, neither a call "
        "the app or the macro database has made, and the edit-in-context mode is a dialog risk; so no read here meets "
        "a positive case, and no route can be held to one")
    folder, path, book, desk = A.copy_desk(A.user_master(), "m4", "RangeBox.xlsx")
    try:
        box = desk.record.gearbox
        targets = A.rb_users() + [gear_entry(box, "Sun").name]
        got = out["reads"] = run("m4: the external-references reads", job(box.assembly, m4_read(
            folder, targets, box.assembly)), 900)
        for where, reads in got.items():
            for label, r in reads.items():
                say(f"fact    m4 {where}: {label}: {r['answer']}; marked {r['marked'] or 'nothing'}")
        marked = {(w, l): r["marked"] for w, reads in got.items() for l, r in reads.items() if r["marked"]}
        if marked:
            A.stop(f"m4: a read marked a document modified: {marked} (§0.3)")
        control = got.get("the assembly (control)", {}).get("ISldWorks.GetDocumentDependencies2", {}).get("answer")
        parts = {os.path.basename(c.part).lower() for c in box.components}
        listed = str(control).lower()
        check(isinstance(control, list) and all(p in listed for p in parts),
              f"m4: the control: the assembly's dependencies list every app part ({len(parts)})")
        clean = [label for label in next(iter(got.values()), {})
                 if all(not str(reads[label]["answer"]).startswith("raised") for w, reads in got.items()
                        if w in targets)]
        out["answered"] = clean
        say(propose(f"EXTERNAL_REFERENCES_READ_ROUTE_CANDIDATES_{year()}", clean,
                    "m4: every candidate that answered on every user part and Sun without an error and marked nothing; "
                    "none is held to a part with a reference, which this probe cannot make"))
        proposed(references, None, "m4: no positive case could be made by proven calls, so the read is not measured; "
                                   f"C4's refusal stands. Answered without error: {clean}")
    finally:
        if not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], folder, "m4")


# -- w9b-part: W9b's part section, for its step-face read on SolidWorks ------------------------------------------------


def section_w9b_part(out):
    say("== w9b-part  W9b's part section run again in this session (88 s on 2026), for its step-face read "
        "(W9B-DEMONSTRATION.md, the step faces) on SolidWorks")
    B.section_part(out)


# -- the run -------------------------------------------------------------------------------------------------------------

ORDER = ["fixed", "modes", "remove", "remake", "bands-off", "m4", "w9b-part"]
SECTIONS = {"fixed": section_fixed, "modes": section_modes, "remove": section_remove, "remake": section_remake,
            "bands-off": section_bands_off, "m4": section_m4, "w9b-part": section_w9b_part}
FOLDERS = {"fixed": ["fixed-updated", "fixed-updated" + W.MASTER_SUFFIX], "modes": ["modes"],
           "remove": ["remove-reducer", "remove-setup"], "remake": ["remake"], "bands-off": ["bands-off"],
           "m4": ["m4"], "w9b-part": ["part"]}


def done_here(name):
    """What of a section this <out> holds already (W9a's ``done_here`` for these sections' folders)."""
    return [p for p in (os.path.join(OUT, f) for f in FOLDERS.get(name, [name])) if os.path.exists(p)]


def main():
    A.SECTIONS.clear()
    A.SECTIONS.update(SECTIONS)
    if A._given in ("", "all"):                    # noqa: SLF001
        A.CHOSEN = list(ORDER)
    A.done_here = done_here
    A.RUN_TITLE, A.JSON_STEM = "W9c demonstration", "w9c-demo"
    return A.main()


if __name__ == "__main__":
    code = 1
    try:
        code = main()
    finally:
        with open(W.LOG_PATH, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(W.LOG) + "\n")
    raise SystemExit(code)
