"""W9c's demonstration (ISSUE-1-PLAN §5 "W9c", §2.1's W9c text, §2.4 "In place", §4 M4, M5, M6, M8, M10; the
interface W9C-INTERFACES.md §4-§8): Update adds, removes and re-mates in place, and adds and removes modes, on
SolidWorks, through the Workbook window's own path (W9a's Desk9: the window's planning, footer, press and finish).

    python w9c_demonstration.py <src> <out> --pid PID [--log FILE] [--sections fixed,modes,...] [--redo]
        [--master <S0's rangebox.master>] [--user-master <W9a's setup.master>]
        [--reducer-master <W9a's reducer.master>] [--fixed-master <this script's fixed-updated.master>]
        [--m4-part <a part with an in-context reference, made by hand>]
    python w9c_demonstration.py --self-check      (no SolidWorks, no Excel)

Every new kind of write is behind a per-version finding that is None (``UPDATE_INSERTS_A_GEAR``,
``UPDATE_MAKES_MATES_WITH_MODES``, ``UPDATE_BANDS_IN_PLACE``, ``UPDATE_ADDS_A_MODE``, ``UPDATE_REMOVES_A_MODE``,
``EXTERNAL_REFERENCES_READ``, and since 957b7c0 ``UPDATE_MAKES_A_NEW_COUPLING`` and ``UPDATE_SUPPRESSES_THE_RELIEF``,
each ``_ON_<year>``). As W9a's ``nocarrier`` did, each section first shows the app's
refusal with the finding as it stands (the footer's sentence before the press; the press refused before any write,
judged by its traced calls, the reads before and after, every document's save flag and every file's time), then
patches the finding True in this process only, says so (``PATCH``), and measures. Each section proposes its finding
from what it read (``propose``); none is set here.

Sections (each can run alone from a kept master; ``fixed`` keeps ``fixed-updated.master`` for the next four).
``ring`` and ``landing`` run by name only (``--sections landing``), outside the default order and its time:

- ``ring``      a diagnostic, facts only: why the ring's part from S0's master does not rebuild set from 55 to 54 teeth
                (code 72 on Tooth Space, 2026's fifth run; run 6 confirmed the cause). On fresh copies, nothing saved:
                the Tooth Space sketch's segments, dimensions and relation kinds as built at 55, set to 54, and built
                from scratch at 54, the last two compared; routes to 54 (a forced rebuild after; through 56; through
                53; 54 then 55) and 56 then 55, each clean or not and the volume; Sun 29 -> 30 for comparison. 2 min.
- ``landing``   A's fix (63bbc33) measured: twelve parts built from scratch and fifteen cases on fresh copies, nothing
                saved, every document closed. Changes the app foresees landing a sketch line on itself, routed by its
                own update_variables (by way of the count it names, two rebuilds, clean, the volume of the target
                built from scratch); the same and two external gears set straight (LANDING_STEPS patched to ()), the
                threshold's facts beside the foresight's fraction; changes that land nothing, one rebuild; a module
                change with a tooth change; the straight failure's file reopened, clean at 55; the fixes review's
                cases (c997e85): just above 0.2, the old end past the new start, recipe B never routed, a module-only
                landing, a user's own feature in error on a routed part; each straight case's short line read before
                and after. About 9 min.
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
- ``remake``    Sun 29 -> 28, Planet 13 -> 14, Ring 55 -> 56 (not 30/12/54: the ring's part does not rebuild set to 54,
                which ``ring`` reads; then the fixes review's M3 on its own copy: a press stopped in the ring, pressed
                again without closing, then after closing without saving) on a copy of ``setup.master`` (RangeBox with the user's
                work; it needs nothing of ``fixed``'s; the centre distance and the planets' even spacing kept): four
                gear mates of a gearbox with modes made again (ruling 9.16 lifted), flags and senses read in every
                mode, the user's mates unchanged.
- ``bands-off`` no legal edit takes the bands off RangeBox_Fixed's sleeve in place (the self-check searches): the
                refusals said, nothing written; then, script-side only, the app's ``Session.suppress_feature`` on the
                copy's Relief read back with the sleeve's mates per mode, and turned back on.
- ``m4``        a probe (no app code makes it yet): the external-references reads the installed API help documents,
                on the user's parts (none has a reference; one with an in-context reference cannot be made by proven
                calls), with a positive control and GetSaveFlag around each. ``--m4-part <path>``: also on a part the
                user made by hand with an in-context reference to an app gear (W9C-DEMONSTRATION.md, m4), read-only,
                and the route proposed from it.
- ``w9b-part``  W9b's ``part`` section again (88 s on 2026), so its step-face read runs on SolidWorks in this session.

Time on 2026 (fixed and modes as run 5 measured): fixed 20 min, modes 48, remove 15, remake 30, bands-off 8, m4 5, w9b-part 2: about 2 h 10
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
GEARS_TEETH = {"Sun": "28", "Planet": "14", "Ring": "56"}   # remake: m(28 + 14)/2 = 26.25 as before; 28 + 2 × 14 = 56;
REMAKE_RATIO_L = 1.0 + 56.0 / 28.0                         # (28 + 56)/3 = 28 (three planets evenly); L 1 + 56/28 = 3
M3_STAGE = {"Sun": "30", "Planet": "12", "Ring": "54"}     # remake's M3 step: the ring 55 -> 54: a landing (the stage kept, as ring_partners)
# Not 30/12/54: the ring's part from S0's master does not rebuild when set from 55 to 54 teeth (its Tooth Space cut
# reads swFeatureErrorSketchContainsSelfIntersectingContour, run 5's ring section), while 56 does, as does a 54-tooth
# ring built from scratch; that is a part-level fault older than W9c, which the ring section reads on its own.
REMOVED_SETUP, REMOVED_REDUCER = "HighDog", "G4"
GROOVE = {"name": "User Groove", "at": (14.25, 0.0), "radius": 1.0}   # an axial Ø2 cut through the sleeve's wall
GROOVE_TOL = 1e-6          # mm
TOL = 1e-6                 # mm, rotation entries: a frame against another
RESOLVED = (2, 3)          # GetSuppression2: swComponentFullyResolved, swComponentResolved (W9a's setup reads these)
GATES = {"fixed": ("UPDATE_INSERTS_A_GEAR", "UPDATE_BANDS_IN_PLACE"), "add": ("UPDATE_ADDS_A_MODE",),
         "remove a mode": ("UPDATE_REMOVES_A_MODE",), "remake": ("UPDATE_MAKES_MATES_WITH_MODES",),
         # 957b7c0 split these two off: no legal edit of the plan's fixtures reaches either through the window
         "relief": ("UPDATE_SUPPRESSES_THE_RELIEF",), "coupling": ("UPDATE_MAKES_A_NEW_COUPLING",)}
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


M4_ORDER = ("IModelDocExtension.ListExternalFileReferences", "IModelDocExtension.ListExternalFileReferencesCount",
            "ISldWorks.GetDocumentDependencies2")


def m4_route(reads, own):
    """The first of ``M4_ORDER`` whose answer names a reference: a count above 0, or a SolidWorks file other than the
    part itself among what it gave; None when none does."""
    own_name = os.path.basename(str(own).replace("\\", "/")).lower()

    def names_one(answer):
        if isinstance(answer, int) and not isinstance(answer, bool):
            return answer > 0
        found = []

        def walk(v):
            if isinstance(v, (list, tuple)):
                for x in v:
                    walk(x)
            elif isinstance(v, dict):
                for x in v.values():
                    walk(x)
            elif isinstance(v, str) and v.lower().endswith((".sldprt", ".sldasm")):
                found.append(os.path.basename(v.replace("\\", "/")).lower())
        walk(answer)
        return any(n != own_name for n in found)
    return next((label for label in M4_ORDER if label in reads and names_one(reads[label]["answer"])), None)


def headers_to_insert(heads, titles, bands):
    """Where a person inserts the columns an edit needs and a workbook lacks (row 1's ``heads``; a header found by its
    start, as W8's ``cell`` finds it): only the band columns (``bands``, the app's titles in its order), just after
    Slides, where the app's ``write_new`` puts them. Returns ``(the first new column, 1-based; the titles in order)``,
    ``(None, [])`` with nothing missing; raises ValueError naming any other header missing."""
    missing = [t for t in dict.fromkeys(titles) if not any(str(h).startswith(t) for h in heads)]
    if not missing:
        return None, []
    if any(t not in bands for t in missing) or "Slides" not in heads:
        raise ValueError(missing)
    return list(heads).index("Slides") + 2, [t for t in bands if t in missing]


def insert_columns(rows, at, titles):
    """``rows`` (a sheet's, row 1 its headers) with empty columns inserted at ``at`` (1-based), headed ``titles``."""
    return [list(r[:at - 1]) + (list(titles) if i == 0 else [""] * len(titles)) + list(r[at - 1:])
            for i, r in enumerate(rows)]


def record_changes(before, after, revision):
    """What differs between two records (JSON, the inventory left out) across a refused press: ``allowed``, the
    gearbox's ``solidworks`` written from none to the press's ``revision`` (``update.refused_update`` writes the version
    it read, by design: a record from before schema 9 has none), and ``other``, every other difference by its path,
    with its value before and after."""
    out = []

    def walk(a, b, where):
        if isinstance(a, dict) and isinstance(b, dict):
            for k in sorted(set(a) | set(b), key=str):
                walk(a.get(k), b.get(k), f"{where}.{k}")
        elif a != b:
            out.append((where, a, b))
    walk(before, after, "record")
    allowed = [(w, a, b) for w, a, b in out if w == "record.gearbox.solidworks" and not a and list(b or []) ==
               list(revision)]
    return ([b for _, _, b in allowed][0] if allowed else None), [x for x in out if x not in allowed]


RING_COUNTS = (54, 56)        # ring: the failing count (55 -> 54) and remake's (55 -> 56); 53, 50, 60 rebuilt (run 5)
RING_ROUTES = {"54, then a forced rebuild": (54, "force"), "56, then 54": (56, 54), "53, then 54": (53, 54),
               "54, then 55 again": (54, 55),
               "56, then 55 (the hypothesis's test: one tooth down from another count)": (56, 55)}


def line_gap(before, after):
    """By the sketches' own maths (``internal.involute_flank``, ``spur.involute_flank``, not ``gears.landing``), a gear
    set from the GearSpec ``before`` to ``after``: how far the new flank start (``I+.start``) lands from where the
    short solved line ends now, and that line's new length (mm) (``short_line``)."""
    (_, old_end), (new_start, new_end) = short_line(before), short_line(after)
    return math.dist(old_end, new_start), math.dist(new_start, new_end)


def plain_spec(gear, module, teeth):
    """A gear of the strip's defaults (face width, backlash, fillet), as A's tests make one: ``gear`` "ring" or
    "spur", or "ringB" a ring of recipe B (arcs)."""
    from gear_generator.spec import GearSpec
    extra = {"recipe": "B"} if gear == "ringB" else {}
    return GearSpec().with_values(teeth=str(teeth), module=str(module),
                                  teeth_side="external" if gear == "spur" else "internal", **extra)


def short_line(spec):
    """The short solved line of a gear's involute tooth-space sketch, ``(I+.start, its other end)`` in sketch
    coordinates (mm), by the sketch's own maths: the ring's ``Li+`` to the tip cap, the external gear's ``L+`` to the
    root fillet. A recipe B sketch draws no such line: the points are still the maths', and the dump finds none."""
    from gear_generator.gears import internal, kind_for, spur
    kind = kind_for(spec)
    ring = getattr(kind, "internal", False)
    f = (internal.involute_flank if ring else spur.involute_flank)(kind.derive(spec))
    return f.start, (f.cap if ring else f.line_inner)


def line_in_dump(segments, start, end, tol=1e-3):
    """The index of the line segment of a sketch dump whose ends are ``start`` and ``end`` (either way round, within
    ``tol`` mm), and whether it runs the other way round; ``(None, None)`` when no line is there."""
    for i, seg in enumerate(segments or []):
        a, b = seg.get("start"), seg.get("end")
        if not (isinstance(a, tuple) and isinstance(b, tuple)) or seg.get("centre") is not None:
            continue
        if math.dist(a, start) < tol and math.dist(b, end) < tol:
            return i, False
        if math.dist(b, start) < tol and math.dist(a, end) < tol:
            return i, True
    return None, None


def far_side(start, end):
    """Whether a radial line's ``end`` lies past the origin from its ``start`` (the far solution of "on a line through
    the origin"), by the sign of their dot product."""
    return start[0] * end[0] + start[1] * end[1] < 0.0


def start_lands_on_cap(before, after, module=1.25):
    """The ring's involute Tooth Space sketch (gears.internal._space_ops_involute) set from ``before`` to ``after``
    teeth: how far the new flank start (``I+.start``, where ``Li+`` must begin) lands from where ``Li+`` ends now (on
    the old tip-cap circle), against ``Li+``'s length (mm), by the app's own maths. For n >= 51 at these sizes, n's
    tip cap (nm - 4m) is (n - 1)'s flank start (da - m), so one tooth down puts the new start 0.024 mm from the old
    end and ``Li+`` nearly collapses: run 6 confirmed it."""
    return line_gap(plain_spec("ring", module, before), plain_spec("ring", module, after))


# landing (A's 63bbc33: gears.landing foresees, swbuild.update_variables routes by way of a safe count). Each case:
# (id, gear, (module, teeth) before, (module, teeth) after, how, the foresight's fraction as A gave it, the count it
# goes by way of, group). gear: "fixture" is RangeBox's Ring and "sun" its Sun (their parts copied from S0's master);
# "ring" and "spur" the strip's defaults, built from scratch. how: "routed" by update_variables as it stands;
# "straight" with swbuild.LANDING_STEPS patched to () in this process (the threshold's facts). Groups as A's list:
# 1 routed, 2 the threshold, 3 unhazardous, 4 a module change with a tooth change, 5 (the leftover) rides on the
# first straight case.
LANDING_CASES = (
    ("ring-55-54", "fixture", ("1.25", 55), ("1.25", 54), "routed", 0.038, 53, 1),
    ("ring-56-55", "fixture", ("1.25", 56), ("1.25", 55), "routed", 0.038, 54, 1),
    ("ring-m1-30-28", "ring", ("1", 30), ("1", 28), "routed", 0.144, 27, 1),
    ("ring-55-54-straight", "fixture", ("1.25", 55), ("1.25", 54), "straight", 0.038, 53, 2),
    ("ring-56-55-straight", "fixture", ("1.25", 56), ("1.25", 55), "straight", 0.038, 54, 2),
    ("ring-m1-30-28-straight", "ring", ("1", 30), ("1", 28), "straight", 0.144, 27, 2),
    ("spur-m1-18-17-straight", "spur", ("1", 18), ("1", 17), "straight", 0.10, 16, 2),
    ("spur-m1-17-16-straight", "spur", ("1", 17), ("1", 16), "straight", 0.128, 15, 2),
    ("spur-m1-18-17", "spur", ("1", 18), ("1", 17), "routed", 0.10, 16, 2),
    ("spur-m1-17-16", "spur", ("1", 17), ("1", 16), "routed", 0.128, 15, 2),
    ("ring-55-53", "fixture", ("1.25", 55), ("1.25", 53), "routed", None, None, 3),
    ("ring-55-56", "fixture", ("1.25", 55), ("1.25", 56), "routed", None, None, 3),
    ("sun-29-30", "sun", ("1.25", 29), ("1.25", 30), "routed", None, None, 3),
    ("ring-m1.25-40-m1.5-32", "ring", ("1.25", 40), ("1.5", 32), "routed", 0.173, 31, 4),
    ("ring-m1.25-40-m1.5-32-straight", "ring", ("1.25", 40), ("1.5", 32), "straight", 0.173, 31, 4),
    # The fixes review (W9C-FIXES-REVIEW.md, 8407159): just above 0.2, unrouted by the app and clean as it stands;
    ("ring-m1-27-25", "ring", ("1", 27), ("1", 25), "routed", 0.204, None, 6),
    ("spur-m1-15-14", "spur", ("1", 15), ("1", 14), "routed", 0.203, None, 6),
    ("spur-m1-14-13", "spur", ("1", 14), ("1", 13), "routed", 0.239, None, 6),
    # a short landing with the old end past the new start, away from the cap; and one well clear;
    ("ring-m1-36-34-straight", "ring", ("1", 36), ("1", 34), "straight", 0.056, 33, 7),
    ("ring-m1-36-34", "ring", ("1", 36), ("1", 34), "routed", 0.056, 33, 7),
    ("ring-m1-44-42", "ring", ("1", 44), ("1", 42), "routed", 0.367, None, 7),
    # a ring of recipe B (arcs, no Li+ in its sketch; c997e85 tells it by its sketch's dimension links and never
    # routes it): set straight as a fact, and by the app as it stands, checked one rebuild, no route, clean;
    ("ringB-55-54-straight", "ringB", ("1.25", 55), ("1.25", 54), "straight", 0.038, None, 8),
    ("ringB-55-54", "ringB", ("1.25", 55), ("1.25", 54), "routed", 0.038, None, 8),
    # a landing with no tooth change (c997e85: by way of 54 and back, the count not listed as changed);
    ("ring-55-m1.225-straight", "fixture", ("1.25", 55), ("1.225", 55), "straight", 0.04, 54, 9),
    ("ring-55-m1.225", "fixture", ("1.25", 55), ("1.225", 55), "routed", 0.04, 54, 9),
    # a user's own feature in error on a routed part (the review's M1; c997e85: the count is set after leg one
    # whatever its rebuild read).
    ("ring-55-54-user-error", "fixture", ("1.25", 55), ("1.25", 54), "user-error", 0.038, 53, 10),
)
# Cases checked clean with no target built (no volume held to one): the review's unrouted ones, to keep the time.
LANDING_NO_TARGET = {"ring-m1-27-25", "spur-m1-15-14", "spur-m1-14-13", "ring-m1-44-42", "ringB-55-54"}
# The user's feature put in error (the review's M1). The eighth run (64bec58) found that SolidWorks will not make a cut
# that removes nothing: FeatureCut4 on a Ø3 circle at x = 200 mm handed back no feature. So the cut is made as W9a's
# keyway was, valid when made and put in error after: a circle on the ring's centre, Ø69 when cut (it takes the m1.25
# 55's tooth tips, Ø66.25, short of its root, Ø71.9), its diameter dimension then linked to Ø3 by an equation (the
# app's own Dimension and LinkDimension calls), which leaves it wholly in the ring's hollow centre: it removes nothing
# and reads in error, as W9a's keyway did inside its Bore 14. The link is a user's dimension equation, not a global,
# and none of recipe B's names, so the app's foresight leaves it out.
USER_CUT = "User Cut In Bore"
USER_CUT_MADE_D, USER_CUT_D = 69.0, 3.0   # mm: its diameter when cut, and as the user's equation then sets it
USER_CUT_DIM = "UserCutD"
LANDING_LEFTOVER = "ring-55-54-straight"      # 5: closed unsaved after its failure, reopened: clean at 55
LANDING_MASTER_FILES = {("fixture", "1.25", 55): "Ring_m1.25_N55.SLDPRT", ("sun", "1.25", 29): "Gear_m1.25_N29.SLDPRT"}
def landing_builds():
    """The parts the landing section builds from scratch, ``(gear, module, teeth)``, each once: every start not in S0's
    master, and every routed case's target (its volume the routed result is held to), in the cases' order."""
    out = []
    for case_id, gear, before, after, how, _, _, _ in LANDING_CASES:
        wanted = [] if (gear, *before) in LANDING_MASTER_FILES else [(gear, *before)]
        wanted += [(gear, *after)] if how == "routed" and case_id not in LANDING_NO_TARGET else []
        out += [k for k in wanted if k not in out]
    return out


LANDING_VOLUME_TOL = 1e-4     # relative: W9b's volume floor (VOLUME_FLOOR); one part routed against it built from scratch


def landing_spec(gear, module, teeth, rb):
    """The GearSpec of one side of a landing case (``rb``: RangeBox as the fixtures hold it)."""
    if gear in ("fixture", "sun"):
        gid = "Ring" if gear == "fixture" else "Sun"
        spec = dataclasses.replace(rb, gears=tuple(dataclasses.replace(g, teeth=str(teeth), module=str(module))
                                                   if g.id == gid else g for g in rb.gears))
        return spec.gear(gid).gear_spec(spec.box)
    return plain_spec(gear, module, teeth)


def landing_variables(spec):
    from gear_generator.gears import kind_for
    kind = kind_for(spec)
    return kind.variables(spec, kind.derive(spec))


def landing_foresight(before, after):
    """What ``swbuild.update_variables`` will foresee for a part built from ``before`` set to ``after`` (GearSpecs):
    ``(landings, the count it goes by way of or None, the fraction)``, by the app's own ``_landing_route`` on the
    equations the part holds (written as SolidWorks gives them back) and ``gears.landing.line_landings`` with no
    threshold for the fraction (None where the globals are no involute tooth space's)."""
    from gear_generator import swbuild
    from gear_generator.gears import kind_for, plan_for
    from gear_generator.gears.base import LinkDimension
    from gear_generator.gears.equations import DEGREES, evaluate_all
    from gear_generator.gears.landing import line_landings
    held = [(f'"{v.name}" = {v.expression_for(DEGREES)}', 0.0) for v in landing_variables(before)]
    # and the dimensions the part's sketches link, as the part holds them (c997e85 tells recipe B by these)
    plan = plan_for(before, kind_for(before).derive(before), "", "C:\\P\\plan.SLDPRT")
    links = [(f'"{op.dimension}" = {op.expression_for(DEGREES)}', 0.0) for op in plan.ops
             if isinstance(op, LinkDimension)]
    wanted = landing_variables(after)
    landing, way = swbuild._landing_route(held + links, wanted, DEGREES)  # noqa: SLF001
    every = line_landings(evaluate_all([(t.split('" = ')[0][1:], t.split('" = ', 1)[1]) for t, _ in held], DEGREES),
                          evaluate_all([(v.name, v.expression_for(DEGREES)) for v in wanted], DEGREES),
                          fraction=float("inf"))
    fraction = every[0][1] / every[0][2] if every else None
    return landing, (int(way[1].expression) if way else None), fraction


SKETCH_TOL = 1e-6             # mm: a sketch point or radius the same in two states


def arc_sweep(centre, start, end, direction):
    """An arc's sweep in degrees, from its start to its end about its centre, counter-clockwise for direction 1 (and
    clockwise for -1), in [0, 360)."""
    a0 = math.atan2(start[1] - centre[1], start[0] - centre[0])
    a1 = math.atan2(end[1] - centre[1], end[0] - centre[0])
    sweep = (a1 - a0) if direction >= 0 else (a0 - a1)
    return math.degrees(sweep % (2.0 * math.pi))


def sketch_diff(a, b, tol=SKETCH_TOL):
    """Two dumps of one sketch (``segments``: each ``{"type", "construction", "start", "end", "centre", "radius",
    "direction", "sweep"}`` in creation order; ``dimensions``; ``relations``), segment by segment: every segment that
    differs, with what differs and by how much (points and radii in mm, sweep in degrees), and the dimensions (SI,
    compared to ``tol`` × 1e-3) and the relation kinds that differ. Points read None compare as differing."""
    out = {"segments": [], "dimensions": [], "relations": None, "count": None}
    sa, sb = a.get("segments") or [], b.get("segments") or []
    if len(sa) != len(sb):
        out["count"] = (len(sa), len(sb))
    for i, (x, y) in enumerate(zip(sa, sb)):
        what = {}
        for key in ("type", "construction", "direction"):
            if x.get(key) != y.get(key):
                what[key] = (x.get(key), y.get(key))
        for key in ("start", "end", "centre"):
            p, q = x.get(key), y.get(key)
            if p is None and q is None:
                continue
            if p is None or q is None:
                what[key] = (p, q)
                continue
            gap = max(abs(u - v) for u, v in zip(p, q))
            if gap > tol:
                what[key] = round(gap, 6)
        for key in ("radius", "sweep"):
            p, q = x.get(key), y.get(key)
            if p is not None and q is not None and abs(p - q) > (tol if key == "radius" else 1e-6):
                what[key] = (round(p, 6), round(q, 6))
        if what:
            out["segments"].append((i, x.get("type"), what))
    da, db = dict(a.get("dimensions") or []), dict(b.get("dimensions") or [])
    out["dimensions"] = [(n, da.get(n), db.get(n)) for n in sorted(set(da) | set(db))
                         if da.get(n) is None or db.get(n) is None or abs(da[n] - db[n]) > tol * 1e-3]
    if sorted(a.get("relations") or []) != sorted(b.get("relations") or []):
        out["relations"] = (sorted(a.get("relations") or []), sorted(b.get("relations") or []))
    return out


def ring_partners(ring):
    """The Sun and Planet that keep RangeBox's planet stage with a ring of ``ring`` teeth: the centre distance
    m(S + P)/2 = 26.25 (S + P = 42) and S + 2P = ring, so S = 84 − ring and P = ring − 42; three planets evenly spaced
    need (S + ring)/3 whole, and S + ring = 84 always."""
    sun, planet = 84 - ring, ring - 42
    return sun, planet, (sun + ring) % 3 == 0


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


STEP_TOL_ = 1e-4          # relative: W9b's step-face landing (its STEP_TOL)
W9B_F0 = 440.547728       # mm²: the unbanded sleeve's front end face (GetArea), W9b's part on 2026 (final run, and this
# demonstration's w9b-part); 2024 read 440.548068. The section without the user's groove, which pierces the in-place
# sleeve's own end face (by π × 1² = 3.1416 mm²), so the in-place sleeve's end face is not F0.
CLASH_TOL = 1e-3           # relative: SolidWorks' volumes summed per pair against the app's, a fact


def clash_pairs(read, gear_of):
    """SolidWorks' interferences in one mode, ``[(Name2s, volume)]``, as pairs by the names the app's result uses (a
    gear id for an app body, the Name2 for the user's), each pair's volumes summed."""
    out = {}
    for names, volume in read:
        key = tuple(sorted(gear_of.get(n, n) for n in names))
        out[key] = out.get(key, 0.0) + float(volume)
    return out


def interference_judged(read_by_mode, app_by_mode, gear_of, users):
    """The interference judgement for a gearbox with the user's components (the coordinator's ruling on W9c's third
    run): (a) ``app_app``, an interference between two app bodies in any mode (a FAIL and a STOP); (b) in each mode
    the app checked (``app_by_mode``: mode -> the result's clashes, ``[(gears, volume)]``), ``unnamed``, an
    interference with a user's component SolidWorks reports and the result does not name, and ``unseen``, a clash the
    result names that SolidWorks does not report; (c) ``unchecked``, the user clashes in modes the app did not check,
    and ``volumes``, each pair's summed volume read against the app's."""
    users = set(users)
    out = {"app_app": {}, "unnamed": {}, "unseen": {}, "unchecked": {}, "volumes": {}}
    for mode, read in read_by_mode.items():
        pairs = clash_pairs(read, gear_of)
        mine = {p: v for p, v in pairs.items() if set(p) & users}
        theirs = [p for p in pairs if not set(p) & users]
        if theirs:
            out["app_app"][mode] = theirs
        if mode not in app_by_mode:
            if mine:
                out["unchecked"][mode] = sorted(mine)
            continue
        named = {tuple(sorted(g)): float(v) for g, v in app_by_mode[mode]}
        missing = sorted(p for p in mine if p not in named)
        extra = sorted(p for p in named if p not in pairs)
        if missing:
            out["unnamed"][mode] = missing
        if extra:
            out["unseen"][mode] = extra
        out["volumes"][mode] = {" & ".join(p): (round(v, 3), round(named[p], 3) if p in named else None)
                                for p, v in mine.items()}
    return out


def propose(name, value, evidence):
    return f"propose {name} = {value!r}  # {evidence}"


# remake's M3 step 2 (the fixes review's addendum §6, 3a6013d): with the ring still open in error, the press stops after
# its check phase and before any write. The parts step 1 changed, and so the only documents it leaves modified:
M3_CHANGED_BY_STEP_1 = ("Sun", "Planet", "Ring")


def footer_says_close(text, stem):
    """§6.1: the footer after step 2 says to close the part without saving, by either sentence. The script's footer
    carries the press's note, which is now the still-in-error sentence alone, and never offers to keep anything."""
    return (stem in text and "without saving" in text
            and ("left in error when it stopped" in text or "still open in SolidWorks" in text) and "to keep" not in text)


def status_alone(text):
    """The status after step 2 is the still-in-error sentence alone: no offer to save what the press did."""
    return "to keep" not in text and "save it in SolidWorks" not in text


def wrote_nothing(changing, globals_before, globals_after, states_before, states_after, result, ring_file, ring,
                  mates_written, ratios_before, ratios_after, step_1_files):
    """§6.2: what step 2 wrote, as sentences (empty: nothing). ``changing``: its traced calls that change or show
    anything (``nothing_changed_calls``, ``AddComponent5``, ``SaveAs3``); each part's globals before and after (equation
    writes are not traced); ``states_*``: ``{"flags": {file: GetSaveFlag}, "times": {file: mtime}}`` of every document
    of the copy just before and after; ``result``: the GearboxUpdate's ``changed``, ``mates_made``,
    ``remade_in_modes``, ``placed``, ``skipped`` and ``failures``; ``ring``: the ring's ``landing_state`` after;
    ``mates_written``: W9a's ``written`` of ``read_now`` before and after; each gear mate's ratio before and after;
    ``step_1_files``: the parts step 1 changed, the only documents that may read modified."""
    out = []
    if changing:
        out.append(f"calls that change or show {changing}")
    if globals_before != globals_after:
        out.append(f"globals {[(n, globals_before.get(n), v) for n, v in globals_after.items() if globals_before.get(n) != v]}")
    for key in ("flags", "times"):
        b, a = states_before.get(key) or {}, states_after.get(key) or {}
        if a != b:
            out.append(f"{key} {[(n, b.get(n), v) for n, v in a.items() if b.get(n) != v]}")
    beyond = sorted(n for n, f in (states_after.get("flags") or {}).items() if f and n not in step_1_files)
    if beyond:
        out.append(f"modified beyond step 1's parts {beyond}")
    for key in ("changed", "mates_made", "remade_in_modes", "placed"):
        if result.get(key):
            out.append(f"{key} {result[key]}")
    if not result.get("skipped"):
        out.append("nothing said skipped")
    if [w for w, _ in result.get("failures") or []] != [ring_file]:
        out.append(f"failures name {[w for w, _ in result.get('failures') or []]}, not the ring's file alone")
    codes = dict((ring or {}).get("in_error") or [])
    if codes.get("Tooth Space") != 72 or (ring or {}).get("teeth") != 54.0:
        out.append(f"the ring reads {ring}, not Tooth Space at 72 and 54 teeth")
    if mates_written:
        out.append(f"the assembly's read {mates_written}")
    if ratios_before != ratios_after:
        out.append(f"ratios {ratios_before} -> {ratios_after}")
    return out


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


FIRST_CONTACT = "probe/results/w9c-demo-sw2026-20261117-1-first-contact.log"
THIRD_RUN = ("probe/results/w9c-demo-20261117-083343.json",
             "probe/results/w9c-demo-sw2026-20261117-3-fixed-updated-in-place.log")


def replay_third_run(ok, b9):
    """W9c's third run on 2026 (the Done-when's Update through; ``fixed`` cut on the script's interference judgement):
    SolidWorks' interferences per mode (JSON) against the clashes the app's post-checks named per mode (log), by the
    new judgement; and the step faces against W9b's unbanded F0 in place of the grooved end face."""
    import ast
    import json
    import re
    paths = [os.path.join(REPO, p) for p in THIRD_RUN]
    if not all(os.path.isfile(p) for p in paths):
        print(f"skip    the third run's readings are not here: {THIRD_RUN}")
        return
    fixed = json.load(open(paths[0], encoding="utf-8"))["sections"]["fixed"]
    log = open(paths[1], encoding="utf-8").read()
    named = {m: [(tuple(g), v) for g, v in ast.literal_eval(c)] for m, c in
             re.findall(r"post-check of (\w+): .*?clashes (\[.*?\]); interference error", log)}
    gear_of = {n: g for g, n in fixed["in_place"]["inserted"]}
    gear_of[re.search(r"RangeSlv keeps its component (\S+) and", log).group(1)] = "RangeSlv"
    users = ["Sprocket-1", "Sprocket-2", "Sprocket-3", "Sprocket-4", "Housing-1"]
    read = {m: v["interferences"] for m, v in fixed["modes"].items()}
    judged = interference_judged(read, named, gear_of, users)
    close = all(app is not None and abs(r - app) <= CLASH_TOL * app for v in judged["volumes"].values()
                for r, app in v.values())
    ok(set(named) == {"H", "N", "L"} and not judged["app_app"] and not judged["unnamed"] and not judged["unseen"]
       and close and any(read.values()),
       f"replay third run: SolidWorks reported interferences in every mode ({ {m: len(v) for m, v in read.items()} }), "
       f"none between two app bodies, each with Sprocket-4 named by the app's post-check of that mode, none named that "
       f"SolidWorks did not report, the volumes summed as the app's: {judged['volumes']}")
    outer = b9.outer_radius(fixed["sleeve_after"]["faces"], 26.0)
    want = b9.step_area(W9B_F0, outer, b9.RELIEF_D / 2)
    face0 = b9.end_areas(fixed["sleeve_after"]["faces"], 26.0).get(0.0)
    old = b9.step_area(face0, outer, b9.RELIEF_D / 2)
    got = {r["z"]: (r["integrated"], r["area"]) for r in fixed["step_faces"]}
    ok(all(abs(i - want) <= STEP_TOL_ * want for i, _ in got.values()) and abs(old - 111.41681) < 1e-4,
       f"replay third run: the step faces integrated {got} land on W9b's F0 − π(Ro² − r²) = {want:.6f} to "
       f"{STEP_TOL_:g}; the grooved end face's ({face0}) gave {old:.6f}, which is why it is not the reference")


def replay_first_contact(ok):
    """The first 2026 run's footer before HighDog's removal on setup (e47d114), against the window's W9c rule the
    script now holds it to: the C4 stop foreseen is said, red, in place of W9a's prediction, which the script's old
    check wanted in the footer (its FAIL there was the script's, not the window's)."""
    path = os.path.join(REPO, FIRST_CONTACT)
    if not os.path.isfile(path):
        print(f"skip    the first run's log is not here: {FIRST_CONTACT}")
        return
    lines = open(path, encoding="utf-8").read().splitlines()
    tag = "footer  (remove, HighDog, the user's components there) "
    at = next((i for i, x in enumerate(lines) if x.startswith(tag)), None)
    if at is None:
        ok(False, "replay first contact: the footer line is in the log")
        return
    footer = lines[at][len(tag):]
    line = next(x for x in lines[at:] if x.startswith("line    "))[len("line    [green] "):]
    stop = next(x for x in lines[at:] if x.startswith("        foreseen references")).split("]: ", 1)[1]
    head = stop.split(" whether your ")[0]
    ok(footer.startswith("[red]") and line not in footer and head in footer,
       "replay first contact: the footer is red and says the foreseen C4 stop, not W9a's prediction "
       f"(the window is right; the old expectation was stale): {head[:70]!r}")


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
        teeth = rb
        for gear, n in GEARS_TEETH.items():
            teeth = with_gear(teeth, gear, teeth=n)
        (spec, _), = _offline(rb, [row_edits(rb, teeth)], folder)
        a, up, errors = classify(records["rb"], spec)
        ratio = next((m.ratio for m in a.report.modes if m.name == "L"), None)
        ok(up is not None and not up.structural and not up.in_place and len(up.ratios) == 4
           and gates(swbuild.InPlace(), modes=True, remakes=True) == [f"UPDATE_MAKES_MATES_WITH_MODES_ON_{year_}"]
           and ratio is not None and abs(ratio - REMAKE_RATIO_L) < 1e-9,
           f"remake: on RangeBox, Sun 28, Planet 14, Ring 56 legal, four gear mates remade, gated on UPDATE_MAKES_MATES_WITH_MODES, "
           f"L's ratio {ratio} (1 + 56/28): {errors or (up and (list(up.structural), list(up.ratios)))}")

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

    # a workbook written before W9b: no band columns; inserted where the app's writer puts them
    from gear_generator.workbook import schema
    bands = [c.title for c in schema.GEARS.columns if c.key in ("start_band", "end_band")]
    full = sheet_rows(rb)["Gears"]
    keep = [i for i, t in enumerate(full[0]) if t not in bands]
    old_rows = [[r[i] for i in keep] for r in full]
    at, titles = headers_to_insert(old_rows[0], [t for _, t, _, _ in row_edits(rb, fx)], bands)
    ok(titles == bands and insert_columns(old_rows, at, titles) == full,
       f"pre-W9b workbook: the two band columns inserted after Slides, headed as write_new heads them, give the app's "
       f"own layout: at {at}, {titles}")
    try:
        headers_to_insert(old_rows[0], ["Groove (mm)", "Nonesuch"], bands)
        ok(False, "pre-W9b workbook: a missing header other than the bands is refused")
    except ValueError as exc:
        ok(str(exc) == "['Nonesuch']", f"pre-W9b workbook: a missing header other than the bands is named: {exc}")
    replay_first_contact(ok)
    for n in RING_COUNTS:
        sun, planet, even = ring_partners(n)
        spec = with_gear(with_gear(with_gear(rb, "Sun", teeth=str(sun)), "Planet", teeth=str(planet)), "Ring",
                         teeth=str(n))
        a = _assessed(spec)
        errors = [d.message for d in a.diagnostics if d.is_error]
        ring_said = [d.message for d in a.diagnostics if "Ring" in d.message]
        print(f"fact    ring {n}: with Sun {sun} and Planet {planet} (three planets evenly spaced: {even}) the fixture "
              f"reads {'legal' if not errors else 'illegal: ' + str(errors[:2])}; of the ring it says {ring_said}")
    ok((M3_STAGE["Sun"], M3_STAGE["Planet"]) == tuple(str(n) for n in ring_partners(int(M3_STAGE["Ring"]))[:2]),
       f"remake, M3: its stage {M3_STAGE} keeps the centre distance and the planets' spacing")
    ok(ring_partners(54) == (30, 12, True) and ring_partners(56) == (28, 14, True)
       and (GEARS_TEETH["Sun"], GEARS_TEETH["Planet"], GEARS_TEETH["Ring"]) == ("28", "14", "56"),
       "ring: 54 goes with Sun 30 and Planet 12; remake's edit is 56 with Sun 28 and Planet 14")
    gaps = {(a, b): start_lands_on_cap(a, b) for a, b in ((55, 54), (56, 55), (55, 53), (55, 56), (53, 54))}
    ok(all(gaps[k][0] < 0.03 for k in ((55, 54), (56, 55))) and all(gaps[k][0] > 0.6 for k in ((55, 53), (55, 56),
                                                                                            (53, 54)))
       and all(abs(v[1] - 0.625) < 1e-9 for v in gaps.values()),
       f"ring: one tooth down (55 -> 54, 56 -> 55) puts the new flank start within 0.03 mm of where Li+ ends now, "
       f"Li+ 0.625 mm long; 55 -> 53, 55 -> 56, 53 -> 54 do not: "
       f"{ {k: (round(v[0], 4), round(v[1], 4)) for k, v in gaps.items()} }")
    for case_id, gear, (m0, n0), (m1, n1), how, said, via, group in LANDING_CASES:
        before, after = landing_spec(gear, m0, n0, rb), landing_spec(gear, m1, n1, rb)
        landing, way, fraction = landing_foresight(before, after)
        gap, length = line_gap(before, after)
        same = fraction is not None and abs(fraction - gap / length) < 1e-9
        if gear == "ringB":
            ok(same and not landing and way is None,
               f"landing plan {case_id} ({how}): recipe B's globals alone give {fraction:.4f}, as the involute's maths "
               f"would ({gap / length:.4f}); with the dimension links its plan makes, the app foresees nothing and "
               f"routes nothing (c997e85: its sketch has no Li+)")
        elif via is None:
            ok(not landing and way is None and same and fraction >= 0.2
               and (said is None or abs(fraction - said) < 0.0015),
               f"landing plan {case_id}: nothing foreseen, no route (fraction {fraction:.4f}"
               f"{'' if said is None else f', the review gave {said}'}; the sketch's maths {gap / length:.4f})")
        else:
            ok(bool(landing) and way == via and same and abs(fraction - said) < 0.0015,
               f"landing plan {case_id} ({how}): foreseen at {fraction:.4f} (A's {said}; the sketch's maths "
               f"{gap:.4f} of {length:.4f} mm = {gap / length:.4f}), by way of {way} (planned {via})")
    line = [(round(x, 4), round(y, 4)) for x, y in short_line(plain_spec("ring", "1.25", 55))]
    segs = [{"start": (0.0, 0.0), "end": (1.0, 0.0)}, {"start": (31.837569, 1.544294), "end": (32.461835, 1.574575)},
            {"start": (31.0, 1.0), "end": (32.0, 1.0), "centre": (0.0, 0.0)}]
    ok(line == [(32.4618, 1.5746), (31.8376, 1.5443)]
       and line_in_dump(segs, (32.461835, 1.574575), (31.837569, 1.544294)) == (1, True)
       and line_in_dump(segs, (5.0, 5.0), (6.0, 6.0)) == (None, None)
       and far_side((32.46, 1.57), (-31.2, -1.5)) and not far_side((32.46, 1.57), (31.84, 1.54)),
       f"landing: Li+ of the 55-tooth ring by the sketch's maths {line} (run 6's dump read line #5's mirror at "
       "(32.461835, -1.574575) -> (31.837569, -1.544294)); found in a dump either way round, arcs passed over; an end "
       "past the origin reads as the far side")
    ok([c[0] for c in LANDING_CASES if c[0] == LANDING_LEFTOVER and c[4] == "straight"] == [LANDING_LEFTOVER]
       and [(c[1], c[2][0], c[2][1]) in LANDING_MASTER_FILES for c in LANDING_CASES if c[0] == LANDING_LEFTOVER]
       == [True] and len({c[0] for c in LANDING_CASES}) == len(LANDING_CASES)
       and sorted(landing_builds()) == sorted(set(landing_builds())),
       f"landing plan: the leftover rides on a straight case from S0's master's 55-tooth ring; ids unique; built from "
       f"scratch: {landing_builds()}")
    ok(abs(arc_sweep((0, 0), (1, 0), (0, 1), 1) - 90.0) < 1e-9 and abs(arc_sweep((0, 0), (1, 0), (0, 1), -1) - 270.0)
       < 1e-9 and abs(arc_sweep((0, 0), (0, 1), (1, 0), 1) - 270.0) < 1e-9,
       "ring: an arc's sweep runs from its start to its end, counter-clockwise for direction 1, clockwise for -1")
    arc = {"type": "swSketchARC", "construction": False, "start": (1.0, 0.0), "end": (0.0, 1.0), "centre": (0.0, 0.0),
           "radius": 1.0, "direction": 1, "sweep": 90.0}
    line = {"type": "swSketchLINE", "construction": False, "start": (0.0, 0.0), "end": (2.0, 0.0)}
    same = sketch_diff({"segments": [line, arc], "dimensions": [("Root", 0.0355)], "relations": ["a", "b"]},
                       {"segments": [line, dict(arc, start=(1.0, 4e-7))], "dimensions": [("Root", 0.0355 + 4e-10)],
                        "relations": ["b", "a"]})
    flipped = sketch_diff({"segments": [line, arc], "dimensions": [("Root", 0.0355)], "relations": ["a"]},
                          {"segments": [line, dict(arc, start=(0.0, 1.0), end=(1.0, 0.0), sweep=270.0)],
                           "dimensions": [("Root", 0.0356)], "relations": ["a", "c"]})
    ok(same == {"segments": [], "dimensions": [], "relations": None, "count": None}
       and [i for i, _, _ in flipped["segments"]] == [1] and set(flipped["segments"][0][2]) == {"start", "end", "sweep"}
       and flipped["segments"][0][2]["sweep"] == (90.0, 270.0) and flipped["dimensions"] == [("Root", 0.0355, 0.0356)]
       and flipped["relations"] == (["a"], ["a", "c"]),
       f"ring: the sketch difference keeps points within 1e-6 mm and SI dimensions within 1e-9 as the same, and names "
       f"an arc whose ends swapped (its sweep 90 -> 270), a changed dimension and an added relation: {flipped}")
    before = {"gearbox": {"solidworks": [], "modes": ["H"]}, "parts": [{"path": "a"}]}
    allowed, other = record_changes(before, {"gearbox": {"solidworks": [34, 1, 1], "modes": ["H"]},
                                             "parts": [{"path": "a"}]}, [34, 1, 1])
    ok(allowed == [34, 1, 1] and not other, "record: a refused press writing the SolidWorks it read onto a record with "
                                            "none is allowed, and said")
    allowed, other = record_changes(before, {"gearbox": {"solidworks": [34, 1, 1], "modes": ["H", "L"]},
                                             "parts": [{"path": "a"}]}, [34, 1, 1])
    ok(other == [("record.gearbox.modes", ["H"], ["H", "L"])],
       f"record: any other change across a refused press is named with its value before and after: {other}")
    allowed, other = record_changes({"gearbox": {"solidworks": [32, 5, 0]}}, {"gearbox": {"solidworks": [34, 1, 1]}},
                                    [34, 1, 1])
    ok(allowed is None and other, "record: a version written over another one is not the allowed change")
    replay_third_run(ok, b9)
    gear_of = {"Hub_m1.25_N17-1": "Hub", "Sleeve_m1.25_N17-1": "RangeSlv", "Gear_m1.25_N29-1": "Sun"}
    read = {"H": [(["Sprocket-4", "Hub_m1.25_N17-1"], 1.0), (["Sleeve_m1.25_N17-1", "Gear_m1.25_N29-1"], 0.5)],
            "N": [(["Sprocket-4", "Hub_m1.25_N17-1"], 1.0)], "L": [(["Sprocket-1", "Hub_m1.25_N17-1"], 2.0)]}
    j = interference_judged(read, {"H": [(("Sprocket-4", "Hub"), 1.0)], "N": [(("Hub", "Sprocket-4"), 1.0),
                                                                              (("RangeSlv", "Sprocket-2"), 3.0)]},
                            gear_of, ["Sprocket-1", "Sprocket-2", "Sprocket-4"])
    ok(j["app_app"] == {"H": [("RangeSlv", "Sun")]} and j["unseen"] == {"N": [("RangeSlv", "Sprocket-2")]}
       and j["unchecked"] == {"L": [("Hub", "Sprocket-1")]} and not j["unnamed"],
       f"interference: two app bodies, a clash the app named that SolidWorks did not report, and one in a mode the app "
       f"did not check are told apart: {j}")
    j = interference_judged({"H": [(["Sprocket-4", "Hub_m1.25_N17-1"], 1.0)]}, {"H": []}, gear_of, ["Sprocket-4"])
    ok(j["unnamed"] == {"H": [("Hub", "Sprocket-4")]}, "interference: a user clash the app did not name is said")
    reads = {"IModelDocExtension.ListExternalFileReferences": {"answer": {"returned": None, "outs": [
                 ["C:\\U\\Bracket.SLDPRT"], ["Assem1.SLDASM"], ["Sketch1"], [], [0], [], [], 0, ""]}},
             "ISldWorks.GetDocumentDependencies2": {"answer": ["Bracket", "C:\\U\\Bracket.SLDPRT"]}}
    ok(m4_route(reads, "C:\\U\\Bracket.SLDPRT") == "IModelDocExtension.ListExternalFileReferences"
       and m4_route({"ISldWorks.GetDocumentDependencies2": {"answer": ["Bracket", "C:\\U\\Bracket.SLDPRT"]}},
                    "C:\\U\\Bracket.SLDPRT") is None
       and m4_route({"IModelDocExtension.ListExternalFileReferencesCount": {"answer": 0}}, "x.SLDPRT") is None,
       "m4: a route names another document, never the part itself or a count of 0")

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
    still = ("Ring_m1.25_N55 is still open in SolidWorks as an earlier Update SolidWorks left it, in error and holding "
             "the new values, so this press set nothing in it: close it in SolidWorks without saving (the file on disk "
             "is as before that Update), then press Update SolidWorks again.")
    run8 = ("Update SolidWorks stopped. RangeBox.SLDASM: SolidWorks reported an error rebuilding RangeBox. It had "
            "already changed RangeBox, not saved: press Update SolidWorks again once that is put right, or save it in "
            "SolidWorks to keep what it did.")
    ok(footer_says_close(still, "Ring_m1.25_N55") and footer_says_close(
        "Ring_m1.25_N55 was left in error when it stopped: close it without saving", "Ring_m1.25_N55"),
       "M3 step 2's footer: either sentence, the stem and without saving")
    ok(not footer_says_close(run8, "Ring_m1.25_N55") and not footer_says_close(
        still + " Or save it in SolidWorks to keep what it did.", "Ring_m1.25_N55"),
       "M3 step 2's footer: run 8's, or one offering to keep, is not")
    ok(status_alone(still) and not status_alone(run8), "M3 step 2's status: the sentence alone, never a save offer")
    from gear_generator import ui_text
    apps = ui_text.still_in_error_sentence([r"C:\copy\Ring_m1.25_N55.SLDPRT"])
    ok(footer_says_close(apps, "Ring_m1.25_N55") and status_alone(apps) and "set nothing" in apps,
       f"M3 step 2: the app's own still-in-error sentence meets the checks: {apps!r}")
    ring_file = "Ring_m1.25_N55.SLDPRT"
    files = ("Gear_m1.25_N29.SLDPRT", "Gear_m1.25_N13.SLDPRT", ring_file)
    flags = {"RangeBox.SLDASM": False, "Dog_m1.25_N17.SLDPRT": False, **{n: True for n in files}}
    states = {"flags": flags, "times": {n: 1.0 for n in flags}}
    result = {"changed": [], "mates_made": [], "remade_in_modes": [], "placed": [], "skipped": "every step after",
              "failures": [(ring_file, "SolidWorks reads Tooth Space and Teeth in error")]}
    ring = {"in_error": [("Tooth Space", 72), ("Teeth", 1)], "teeth": 54.0}
    glb = {ring_file: {"No. of Teeth": 54.0}}
    ratios = {"Sun meshes Planet copy 1": (30, 12)}

    def wrote(**kw):
        args = dict(changing=[], globals_before=glb, globals_after=glb, states_before=states, states_after=states,
                    result=result, ring_file=ring_file, ring=ring, mates_written=[], ratios_before=ratios,
                    ratios_after=ratios, step_1_files=files)
        args.update(kw)
        return wrote_nothing(**args)
    ok(wrote() == [], "M3 step 2: a press that stopped before any write wrote nothing")
    ok(wrote(changing=[("AddMate5",), ("ForceRebuild3",)]) != [], "M3 step 2: run 8's AddMate5 and rebuild are said")
    ok(wrote(globals_after={ring_file: {"No. of Teeth": 53.0}}) != [], "M3 step 2: a global set (untraced) is said")
    ok(wrote(states_after=dict(states, flags=dict(flags, **{"RangeBox.SLDASM": True}))) != [],
       "M3 step 2: the assembly newly modified is said")
    ok(wrote(states_before=dict(states, flags=dict(flags, **{"RangeBox.SLDASM": True})),
             states_after=dict(states, flags=dict(flags, **{"RangeBox.SLDASM": True}))) != [],
       "M3 step 2: the assembly modified at all (only step 1's parts may be) is said")
    ok(wrote(states_after=dict(states, times=dict(states["times"], **{ring_file: 2.0}))) != [],
       "M3 step 2: a file written is said")
    ok(all(wrote(result=dict(result, **{k: ["x"]})) != [] for k in ("changed", "mates_made", "remade_in_modes",
                                                                       "placed")),
       "M3 step 2: anything changed, made, remade or placed is said")
    ok(wrote(result=dict(result, skipped="")) != [] and wrote(result=dict(
        result, failures=[("RangeBox.SLDASM", "rebuild")])) != [] and wrote(result=dict(
            result, failures=result["failures"] + [("RangeBox.SLDASM", "rebuild")])) != [],
       "M3 step 2: nothing skipped, or a failure not the ring's alone, is said")
    ok(wrote(ring={"in_error": [], "teeth": 54.0}) != [] and wrote(ring=dict(ring, teeth=53.0)) != [],
       "M3 step 2: the ring mended or moved is said")
    ok(wrote(mates_written=["flags [...]"]) != [] and wrote(ratios_after={"Sun meshes Planet copy 1": (29, 13)}) != [],
       "M3 step 2: a mate or a gear mate's ratio changed is said")
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
from gear_generator.workbook import schema as wb_schema  # noqa: E402
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
    check(True, f"{label}: the copy's workbook holds the fixture's Gears, Meshes and Modes rows (as the app reads them)")


def headers_fact(label, book):
    """Which of the app's Gears columns the workbook's own header row lacks (a workbook written before W9b has no band
    columns): said, so an edit that needs one shows why it types it."""
    heads = headers_of(book, "Gears")
    lacking = [c.title for c in wb_schema.GEARS.columns if not any(h.startswith(c.title) for h in heads)]
    say(f"fact    {label}: the workbook's Gears headers lack {lacking or 'nothing'} of the app's")
    return lacking


def record_json(desk):
    import json
    text = store.link_record_to_json(desk.record)
    return json.loads(text) if isinstance(text, str) else text


def record_on_disk(desk):
    """The record's file as written (the link schema it carries)."""
    import json
    with open(store.link_record_path(desk.path), encoding="utf-8") as handle:
        return json.load(handle)


def record_brought_forward(label, desk):
    """After the window's first finish on a copy of a master written by an earlier app: the record on disk at this
    app's link schema."""
    got = record_on_disk(desk).get(store.LINK_SCHEMA_KEY)
    check(got == store.LINK_SCHEMA_VERSION, f"{label}: the record on disk now at link schema {got} "
                                            f"(this app's {store.LINK_SCHEMA_VERSION})")


def without_user_work(record):
    box = dict(record.get("gearbox") or {})
    box.pop("user_work", None)
    return dict(record, gearbox=box)


def footer_ahead(desk, label):
    """The footer before a press, held to the window's W9c rule (``ui_text.workbook_footer``): where an in-place stop
    is foreseen and no refusal is on record, the stop is said in place of W9a's prediction of what the press does
    with the user's work (a press that changes nothing does nothing with it); otherwise W9a's ``ahead_of``."""
    ahead = wb_update.user_work_ahead(desk.update, desk.record, desk.reading.digest)
    recorded = ahead is not None and bool(ahead.refused)
    stops = () if recorded else wb_update.in_place_ahead(desk.update, desk.record)
    if not stops:
        return A.ahead_of(desk, label)
    f = desk.say_footer(label)
    line, _ = ui_text.user_work_line(ahead)
    stop, _ = ui_text.in_place_line(stops, desk.record, known=line,
                                    on_disk=getattr(desk.update, "new_parts_on_disk", ()))
    say(f"line    (W9a's prediction, not said beside a foreseen stop) {line or '(none)'}")
    check(bool(stop) and stop in f.text and not f.ok and (not line or line not in f.text),
          f"{label}: the footer says the foreseen stop, red, in place of W9a's prediction: {stop[:120]!r}…")
    return ahead


def foresight_unmasked(desk):
    """What the footer foresees would stop the press now, with any refusal the record holds set aside (a recorded
    refusal is said in place of the prediction until the workbook changes, so it would hide one): the user-work
    problems ``user_work_ahead`` predicts on a copy of the record whose inventory holds no refusal, and the in-place
    stops ``in_place_ahead`` foresees with the findings as they stand in this process. ``[(kind, names, sentence)]``."""
    import copy
    record = desk.record
    entry = record.gearbox.user_work if record is not None and record.gearbox is not None else None
    if entry is not None and entry.problems:
        record = copy.deepcopy(record)
        record.gearbox.user_work.problems = []
        record.gearbox.user_work.refused_at = ""
    ahead = wb_update.user_work_ahead(desk.update, record, desk.reading.digest)
    stops = wb_update.in_place_ahead(desk.update, desk.record)
    return [(p.kind, list(getattr(p, "mates", ()) or ()) + list(getattr(p, "subjects", ()) or ()), p.sentence)
            for p in list(getattr(ahead, "problems", ()) or ()) + list(stops or ())]


def press(desk, label):
    """W9a's ``press``, and the runs review's rule: where the press then goes through, any problem the footer foresaw
    for it (``foresight_unmasked``, read just before) is one it did not meet, a FAIL. A press that refuses is judged
    by its section, as before."""
    foreseen = foresight_unmasked(desk)
    result, calls = A.press(desk, label)
    if result is not None:
        check(not foreseen, f"{label}: the press went through, and the footer foresaw no problem it did not meet: "
                            f"{[(k, n) for k, n, _ in foreseen] or 'none'}")
        for kind, names, sentence in foreseen:
            say(f"        foreseen and not met: {kind} {names}: {sentence}")
    return result, calls


def band_titles():
    """The two band columns' headers exactly as the app's own ``write_new`` heads them (``schema.GEARS``)."""
    return [c.title for c in wb_schema.GEARS.columns if c.key in ("start_band", "end_band")]


def headers_of(book, sheet):
    ws = book.wb.Worksheets(sheet)
    return [str(ws.Cells(1, c).Value or "") for c in range(1, 60)]


def ensure_headers(book, sheet, titles, label):
    """The headers an edit types under, each found in row 1 (as W8's ``cell`` finds it, by its start). A workbook
    written before W9b has no band columns: a person inserts the two after Slides and types their headers exactly as
    the app's ``write_new`` heads them, saved, and it is said. Any other header missing is a sentence naming it."""
    heads = headers_of(book, sheet)
    try:
        at, inserted = headers_to_insert(heads, titles, band_titles() if sheet == "Gears" else [])
    except ValueError as exc:
        raise AssertionError(f"{label}: the workbook's {sheet} sheet has no column headed {exc} (its headers "
                             f"{[h for h in heads if h]}), so the edit cannot be typed") from None
    if not inserted:
        return []
    ws = book.wb.Worksheets(sheet)
    typed = []
    for i, title in enumerate(inserted):
        ws.Columns(at + i).Insert()
        book.set(sheet, f"{column_letter(at + i)}1", title)
        typed.append(f"{column_letter(at + i)}1 {title!r}")
    book.save()
    say(f"person  {label}: the workbook was written before W9b and has no band columns; two columns inserted after "
        f"Slides and headed as the app's write_new heads them: {typed}")
    return typed


def edit_live(desk, book, edits, label, cells=()):
    """A person's edit in Excel: each ``(sheet, title, key, value)`` at its cell (W8's ``cell``, every address found
    before anything is written; a header the workbook lacks put in first by ``ensure_headers``) and ``cells`` at
    known addresses, saved; the window's poll reads, plans and classifies (W8's ``edit``). Returns the cells
    written."""
    for sheet in dict.fromkeys(s_ for s_, _, _, _ in edits):
        ensure_headers(book, sheet, [t for s_, t, _, _ in edits if s_ == sheet], label)
    found = []
    for sheet, title, key, value in edits:
        try:
            found.append((sheet, W.cell(book, sheet, title, key), value))
        except StopIteration:
            raise AssertionError(f"{label}: no cell for {title!r} in {sheet}'s row {key or '(the first empty)'}: "
                                 f"the headers are {[h for h in headers_of(book, sheet) if h]}") from None
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


def app_clashes(result):
    """The clashes the app's result names, by mode: each post-check's (``GearboxUpdate.modes``), else the result's
    own for a gearbox without modes, ``[(gears, volume)]`` as the result words them."""
    if result is None:
        return {}
    if result.modes:
        return {m.name: [(tuple(c.gears), float(c.volume)) for c in m.clashes] for m in result.modes}
    return {result.configuration or "": [(tuple(c.gears), float(c.volume)) for c in result.clashes]}


def interference_said(label, desk, every, result, users, out):
    """The ruling on W9c's third run: no interference between two app bodies in any mode (judged by W9b's
    ``judge_every`` with the user's components left out, a STOP there); every interference SolidWorks reports with a
    user's component is one the app's result named, by pair, in each mode the app checked, and the app names none
    SolidWorks does not report (a check); what the result's status and the footer say of it, and which modes the
    app checked, said as facts."""
    box = desk.record.gearbox
    gear_of = {n: g for g, n in W.bodies(box)}
    named = app_clashes(result)
    judged = interference_judged(every["interferences"], named, gear_of, users)
    out["interference"] = dict(judged, app=named)
    checked = sorted(named)
    say(f"fact    {label}: the app checked interference in {checked or 'no mode'} of {list(box.modes) or ['(one)']}"
        f"{' (every mode)' if set(checked) >= set(box.modes) else ''}; its log's CHECK lines carry "
        f"{result.configuration or 'the one configuration'!r}'s clashes "
        f"{[(list(c.gears), round(c.volume, 3)) for c in result.clashes]}; each pair with the user's, SolidWorks' "
        f"volumes summed against the app's: {judged['volumes']}")
    status = desk.note[0] if desk.note else ""
    said = status[status.find("Check:"):].split(" It worked")[0] if "Check:" in status else ""
    say(f"fact    {label}: the result's status says of it: {said or '(nothing)'}")
    desk.say_footer(f"{label}, after the press, with the user's interference")
    if judged["unchecked"]:
        say(f"fact    {label}: interferences with the user's components in modes the app did not check: "
            f"{judged['unchecked']}")
    off = {m: v for m, v in judged["volumes"].items()
           if any(app is not None and abs(r - app) > CLASH_TOL * max(app, 1.0) for r, app in v.values())}
    if off:
        say(f"fact    {label}: summed volumes differ from the app's by more than {CLASH_TOL:g}: {off}")
    check(not judged["unnamed"] and not judged["unseen"],
          f"{label}: every interference SolidWorks reports with the user's components is one the app's result named, in "
          f"each mode it checked, and it named none SolidWorks did not report: unnamed {judged['unnamed'] or 'none'}, "
          f"unseen {judged['unseen'] or 'none'}")
    return judged


def judged_modes(label, desk, out, section3=True, against=None, banded=True, engaged=None, result=None, users=None):
    """W9b's per-mode read and judgement on the gearbox as recorded now (frames, flags, slide values, interference
    between app bodies, every gear free, the bands and dogs where the app's read puts them; §3's table where
    ``section3``), and each mode of ``against`` (mode -> §3's row to hold it to) by W9b's ``judge_mode``. ``banded``
    False: a sleeve without bands (RangeBox as built), each mode held to ``engaged`` (mode -> the dogs engaged)
    instead of §3's RangeBox_Fixed rows. An interference with one of ``users`` (the user's components) is held to the
    app's ``result`` (``interference_said``), not to §3. A mode reading other than the record and §3 say, or two app
    bodies interfering, is a STOP."""
    users = list(A.rb_users() if users is None else users)
    globals_ = B.part_globals(desk, ("RangeSlv", "HighDog", "LowDog", "Hub"))
    every = B.mode_read(label, desk)
    clean = B.judge_every(label, desk, every, globals_, banded=banded, against_section3=section3, out=out,
                          users=users)
    if result is not None:
        interference_said(label, desk, every, result, users, out)
    differ = {}
    for mode, row in (against or {}).items():
        bands, dogs, _ = B.measured(every["frames"][mode], globals_)
        judged = B.judge_mode(bands, dogs)
        wrong = B.section3_of(judged, bands, row)
        if wrong:
            differ[mode] = wrong
        check(not wrong, f"{label}, {mode}: as §3's {row} row: {wrong or 'the bands, the relief, engaged '}"
                         f"{judged['engaged']}")
    for mode, dogs_engaged in (engaged or {}).items():
        bands, dogs, _ = B.measured(every["frames"][mode], globals_, banded=banded)
        judged = B.judge_mode(bands, dogs)
        if judged["engaged"] != dogs_engaged:
            differ[mode] = f"engaged {judged['engaged']}, not {dogs_engaged}"
        check(judged["engaged"] == dogs_engaged, f"{label}, {mode}: engaged {judged['engaged']} as §3's RangeBox "
                                                 f"({dogs_engaged}); least running gap {judged['least']}")
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
    footer_ahead(desk, f"{label}, the findings as they stand {standing}")
    foreseen = foreseen_names(desk)
    said = " ".join(p.sentence + " " + " ".join(p.subjects) for p in foreseen)
    check(any(p.kind == swbuild.PROBLEM_UNSETTLED for p in foreseen) and all(n in said for n in unsettled),
          f"{label}: the footer foresees the press refused, naming {unsettled}: "
          f"{[(p.kind, list(p.subjects)) for p in foreseen]}")
    A.save_user(folder, f"before {label}")
    files = B.documents_state(label, desk, folder)
    rest = without_user_work(record_json(desk))
    problems = A.refuse_press(label, desk, folder, {swbuild.PROBLEM_UNSETTLED}, (), tuple(unsettled), users=users,
                              part=part, save=False)
    B.nothing_written(f"{label}, by file times and save flags", files, B.documents_state(label, desk, folder))
    refusal_on_record(label, desk, rest, {swbuild.PROBLEM_UNSETTLED: unsettled})
    return {"findings": standing, "refusal": [p.sentence for p in problems]}


def refusal_on_record(label, desk, rest, subjects):
    """W9C-INTERFACES §11 (B's second joining round): after a refusal before any write, the record's inventory holds
    the press's workbook digest and SolidWorks and every problem with its subjects (``subjects``: kind -> the names
    each must carry), and nothing else on the record changed (``rest``: the record without its inventory before)."""
    entry = desk.record.gearbox.user_work
    kept = {}          # every problem of one kind adds its subjects: two gates refused in one press are two "unsettled"
    for p in (entry.problems if entry is not None else []):
        kept.setdefault(p.kind, []).extend(getattr(p, "subjects", []) or [])
    missing = {k: [n for n in names if n not in kept.get(k, [])] for k, names in subjects.items()}
    missing = {k: v for k, v in missing.items() if v or k not in kept}
    after = without_user_work(record_json(desk))
    allowed, other = record_changes(rest, after, list(W.TAG["revision"]))
    if allowed:
        say(f"fact    {label}: the refused press wrote the SolidWorks it read onto a record that had none "
            f"(gearbox.solidworks {allowed}; refused_update does so by design, schema 9): allowed")
    check(entry is not None and not missing and not other and list(entry.revision) == list(W.TAG["revision"])
          and entry.digest == desk.reading.digest,
          f"{label}: the record keeps the refusal with its subjects {kept}, the press's digest and SolidWorks "
          f"{list(entry.revision) if entry is not None else None}, and nothing else on it changed: "
          f"{other or 'nothing'}; missing {missing or 'none'}")


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
    result, calls = press(desk, label)
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
                                            "senses_unread", "turned_round", "failures", "skipped")} | {
        "clashes_by_mode": app_clashes(result)}


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
        quiet, _ = press(desk, "fixed: a quiet press (the inventory read again, the groove in it)")
        check(quiet is not None and quiet.placed == [] and any(f.name == GROOVE["name"] for f in (
            desk.record.gearbox.user_work.features if desk.record.gearbox.user_work is not None else ())),
            f"fixed: the quiet press recorded the user's groove: {desk.error if quiet is None else 'ok'}")
        record_brought_forward("fixed, after the quiet press", desk)
        A.save_user(folder, "after the quiet press")

        say("-- fixed  the workbook edited to RangeBox_Fixed in Excel: RangeSlv's cells and Hub's row, the fixture's own")
        headers_fact("fixed", book)
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
            footer_ahead(desk, "fixed, the findings patched, before the press")
            foreseen = foreseen_names(desk)
            check(not foreseen, f"fixed: with the findings patched the footer foresees nothing stopping the press: "
                                f"{[(p.kind, list(p.subjects)) for p in foreseen]}")
            before = every_mode("fixed, before the press", desk, users)
            shown = active_now(desk)            # after the every-mode read, which leaves the first mode showing
            files = B.documents_state("fixed", desk, folder)
            result, calls = press(desk, "fixed: RangeBox -> RangeBox_Fixed, one Update")
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
            hub_entry = next((p for p in desk.record.parts if "Hub" in p.gears), None)
            check(hub_entry is not None and store.same_path(hub_entry.path, hub_part)
                  and store.read_sidecar(store.sidecar_path(hub_part)) is not None and not pressed.left,
                  f"fixed: the record holds Hub's part ({hub_entry and os.path.basename(hub_entry.path)}) with its "
                  f".gear.json, and nothing left over (left {pressed.left})")
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
            face0 = B.end_areas(faces, 26.0).get(0.0)
            outer = B.outer_radius(faces, 26.0)
            groove_hole = math.pi * GROOVE["radius"] ** 2
            say(f"fact    fixed: the in-place sleeve's front end face reads {face0} mm², the user's groove through it "
                f"(π × {GROOVE['radius']:g}² = {groove_hole:.4f}): {face0 + groove_hole if face0 else None} with the "
                f"hole, against W9b's unbanded section {W9B_F0}; so the step faces are held to W9b's F0, not this face")
            if outer:
                B.step_report(out, sleeve_after.get("steps"), B.step_area(W9B_F0, outer, B.RELIEF_D / 2))
                outline = [(r["z"], round(r["loop_areas"][0] - sum(r["loop_areas"][1:]), 6))
                           for r in (sleeve_after.get("steps") or []) if isinstance(r, dict) and r.get("loop_areas")]
                say(f"fact    fixed: the tooth outline's own loops, outer less inner, per step face: {outline}")
            else:
                say("fact    fixed: the step faces not judged: Ro not read from the faces")

            say("-- fixed  M5: Hub's state in every mode; every user item; each mode as §3")
            states = out["hub_states"] = states_by_mode("fixed", desk, [hub])
            clean["m5"] = check(all(states[m].get(hub) in RESOLVED for m in modes),
                                f"fixed: Hub ({hub}) reads resolved in every mode (M5): {states}")
            after = every_mode("fixed, after the press", desk, users)
            users_unchanged("fixed", before, after, users, mates)
            judged_modes("fixed", desk, out, result=result)
            B.nothing_written("fixed: nothing of the user's own files (Sprocket, Housing) written", {
                "flags": {}, "times": {n: t for n, t in files["times"].items() if n in ("Sprocket.SLDPRT",
                                                                                         "Housing.SLDPRT")}},
                {"flags": {}, "times": {n: t for n, t in B.documents_state("fixed", desk, folder)["times"].items()
                                        if n in ("Sprocket.SLDPRT", "Housing.SLDPRT")}})
            footer_ahead(desk, "fixed, after the press")
            check(not foreseen_names(desk), "fixed: after the press the footer foresees nothing in place")

            say("-- fixed  saved and closed as the user would; a second press, which loads every document from its "
                "file, is quiet and its finish clears the record's unsaved marks, so the master's record holds none")
            frames_before = W.gear_frames(CTX["worker"], desk)
            A.save_user(folder, "the Update's result")
            flags_before = W.gearbox_flags(CTX["worker"], desk)
            marks = store.read_link_record(desk.path)
            say(f"fact    fixed: the record on disk before the second press: unsaved "
                f"{[os.path.basename(p) for p in marks.unsaved]}, mismatched "
                f"{[os.path.basename(p) for p in marks.mismatched]}")
            left_open = run("fixed: closed as the user closes it", W.quit_in(folder))
            check(not left_open, f"fixed: everything of the copy closed after the save: left {left_open}")
            desk.plan_solidworks()
            second, _ = press(desk, "fixed: a second press")
            clean["quiet"] = check(second is not None and second.placed == [] and not second.changed and second.ok
                                   and not second.inserted and not second.bands_added,
                                   f"fixed: the second press does nothing: {desk.error if second is None else 'ok'}")
            if second is not None:
                W.check_quiet_update(CTX["worker"], desk, second, "fixed: the second press", frames_before,
                                     flags_before)
            marks = store.read_link_record(desk.path)
            clean["marks"] = check(not marks.unsaved and not marks.mismatched,
                                   f"fixed: the record on disk after the second press holds no unsaved or mismatched "
                                   f"document, so a copy of the master reads valid: unsaved "
                                   f"{[os.path.basename(p) for p in marks.unsaved]}, mismatched "
                                   f"{[os.path.basename(p) for p in marks.mismatched]}")
        kept = A.w8_step(W.keep_master, CTX["worker"], folder, "fixed-updated")
        MASTERS["fixed"] = kept
        check(bool(kept), f"fixed: kept as fixed-updated.master: {kept}")
    finally:
        if not kept and not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], folder, "fixed-updated")
        out["clean"] = clean
        insert_ok = bool(clean) and all(clean.get(k) for k in ("insert", "m5", "quiet", "marks"))
        proposed(finding_name("UPDATE_INSERTS_A_GEAR"), True if insert_ok else None,
                 f"fixed: Hub built, inserted, mated and resolved in every mode, every user item kept, each mode "
                 f"§3's, the second press quiet: {clean}")
        proposed(finding_name("UPDATE_BANDS_IN_PLACE"), True if bool(clean) and all(
            clean.get(k) for k in ("bands", "m8", "quiet")) else None,
            f"fixed: bands given in place (the gate gives only; taking away is UPDATE_SUPPRESSES_THE_RELIEF, see "
            f"bands-off): {clean}")


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


def keep_record(out, when, desk):
    """The link record's JSON as the store wrote it to disk, kept in the run JSON (``records``: [when, record]) so a
    later replay can stand on the real record; said in one line."""
    try:
        got = record_on_disk(desk)
    except (OSError, ValueError) as exc:
        got = f"unread: {type(exc).__name__}: {exc}"
    out.setdefault("records", []).append([when, got])
    entry = (got.get("gearbox") or {}).get("user_work") if isinstance(got, dict) else None
    say(f"fact    modes: the record on disk {when} kept in the run JSON; its inventory covers "
        f"{entry.get('modes') if isinstance(entry, dict) else entry}")


def inventory_follows_add(label, desk, mode, suppressed, out):
    """B's 0eb0768 (the runs review's must-fix 1): after a press that added ``mode``, the record's inventory, in memory
    and on disk, names ``mode`` in its ``modes``, and in each user mate's on-list exactly where SolidWorks' own flag
    there (``suppressed``: name -> True for suppressed, read unshown) reads on. A FAIL otherwise."""
    entry = desk.record.gearbox.user_work
    disk = record_on_disk(desk)
    on_disk = (disk.get("gearbox") or {}).get("user_work") or {}
    held = {m.name: list(m.on) for m in (entry.mates if entry is not None else [])}
    held_disk = {m.get("name"): list(m.get("on") or []) for m in on_disk.get("mates") or []}
    read = [n for n in suppressed if n in held]
    wrong = {n: {"SolidWorks": "suppressed" if suppressed[n] else "on", "record": held[n], "on disk": held_disk.get(n)}
             for n in read if (mode in held[n]) == suppressed[n] or (mode in (held_disk.get(n) or [])) == suppressed[n]}
    covers = list(entry.modes) if entry is not None else None
    out["inventory_after_add"] = {"modes": covers, "modes_on_disk": on_disk.get("modes"), "on": held,
                                  "suppressed_read": suppressed, "wrong": wrong}
    say(f"fact    {label}: the inventory after {mode}'s add covers {covers} (on disk {on_disk.get('modes')}); each "
        f"user mate's on-list {held}; SolidWorks reads suppressed in {mode} {suppressed}; user mates not in the "
        f"inventory {[n for n in suppressed if n not in held]}")
    return check(entry is not None and mode in covers and mode in (on_disk.get("modes") or []) and bool(read)
                 and not wrong,
                 f"{label}: the record's inventory names {mode} in its modes and in every user mate's on-list where "
                 f"SolidWorks reads it on there, and nowhere it reads suppressed ({len(read)} mates): {wrong or 'yes'}")


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
        keep_record(out, f"after the refusal of {ADDED_MODE}'s add", desk)
        with patched(add_stems):
            desk.plan_solidworks()
            footer_ahead(desk, f"modes, {ADDED_MODE}, the finding patched")
            before = every_mode(f"modes, before {ADDED_MODE}", desk, users)
            shown = active_now(desk)
            result, _ = press(desk, f"modes: {ADDED_MODE} added")
            out["add"] = in_place_fact(result)
            keep_record(out, "after the add", desk)
            if result is None:
                A.section_stop(f"modes: the press adding {ADDED_MODE} raised: {desk.error}")
            ok = done_said(result, f"modes, {ADDED_MODE}")
            after_shown = active_now(desk)
            names = configurations_now(desk)
            flags, states = took_active_read("modes", desk, ADDED_MODE, mates, users)
            differ = took_active_differs(result.took_active_state, ADDED_MODE, flags, states, swbuild._STATE_WORDS)  # noqa: SLF001
            inventory_follows_add("modes", desk, ADDED_MODE, flags, out)
            clean["add"] = check(ok and result.modes_added == [ADDED_MODE] and ADDED_MODE in names
                                 and not desk.record.gearbox.left
                                 and after_shown == shown and not differ
                                 and list(desk.record.gearbox.modes) == list(MODES) + [ADDED_MODE],
                                 f"modes: {ADDED_MODE} made ({names}), the record's modes "
                                 f"{list(desk.record.gearbox.modes)}, {shown} showing before and after "
                                 f"({after_shown}); each user item said as read there: {differ or 'yes'}")
            after = every_mode(f"modes, after {ADDED_MODE}", desk, users)
            users_unchanged(f"modes, {ADDED_MODE}", before, after, users, mates)
            judged_modes(f"modes, {ADDED_MODE}", desk, out.setdefault("judged_add", {}), section3=False,
                         against={"H": "H", "N": "N", "L": "L", ADDED_MODE: ADDED_AT}, result=result)
        proposed(finding_name("UPDATE_ADDS_A_MODE"), True if clean.get("add") else None,
                 f"modes: {ADDED_MODE} added from the mode showing, every flag and slide value read back as the record, "
                 f"the user's items there said as read: {clean.get('add')}")

        say(f"-- modes  {REMOVED_MODE} removed while {shown} shows, the user's {USER_OFF_IN_N} suppressed there first")
        person_flags(desk, folder, USER_OFF_IN_N, True, [REMOVED_MODE])
        edit_live(desk, book, row_edits(fx_h2, hlh2), f"Modes row {REMOVED_MODE} cleared")
        u = desk.update
        check(u is not None and not u.structural and u.in_place.modes_removed == (REMOVED_MODE,),
              f"modes: classify removes {REMOVED_MODE} in place: {u and (list(u.structural), u.in_place.modes_removed)}")
        with patched(rm_stems):
            # The runs review's must-fix 1 (B's 0eb0768): the footer for this edit, read with the gate patched and
            # before its refusal is on record (either would hide the prediction), foresees nothing of the user's.
            desk.plan_solidworks()
            footer_ahead(desk, f"modes, {REMOVED_MODE} removed, the gate patched, before its refusal (must-fix 1)")
            foreseen_n = foresight_unmasked(desk)
            in_added = [(k, n) for k, n, text in foreseen_n if ADDED_MODE in n or ADDED_MODE in text]
            check(not in_added, f"modes: after {ADDED_MODE}'s add, the footer for the next edit names no user mate as "
                                f"suppressed in {ADDED_MODE} (the runs review's must-fix 1): {in_added or 'none'}")
            out["foreseen_before_n"] = foreseen_n
        desk.plan_solidworks()
        out["remove_refusal"] = gated_refusal(f"modes, {REMOVED_MODE} removed, the gate as it stands", desk, folder,
                                              rm_stems, sleeve)
        keep_record(out, f"after the refusal of {REMOVED_MODE}'s removal", desk)
        with patched(rm_stems):
            desk.plan_solidworks()
            footer_ahead(desk, f"modes, {REMOVED_MODE} removed, the finding patched")
            before = every_mode(f"modes, before {REMOVED_MODE} goes", desk, users)
            every_before = B.mode_read(f"modes, before {REMOVED_MODE} goes", desk)
            shown = active_now(desk)
            lost = flags_lost_expected(before["by_mode"], mates, shown, REMOVED_MODE)
            say(f"fact    modes: the user's flags in {REMOVED_MODE} that differ from {shown}'s, read before: {lost}")
            result, _ = press(desk, f"modes: {REMOVED_MODE} removed")
            out["remove"] = in_place_fact(result)
            keep_record(out, f"after {REMOVED_MODE}'s removal", desk)
            if result is None:
                A.section_stop(f"modes: the press removing {REMOVED_MODE} raised: {desk.error}")
            check(not foreseen_n, f"modes: the press removing {REMOVED_MODE} went through, and the footer read before "
                                  f"the gate's refusal foresaw nothing it did not meet: "
                                  f"{[(k, n) for k, n, _ in foreseen_n] or 'none'}")
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
                and not desk.record.gearbox.left
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
            held = desk.record.gearbox.user_work
            held = None if held is None else {k: [dict(vars(x)) if hasattr(x, "__dict__") else x
                                                  for x in getattr(held, k)]
                                              for k in ("components", "mates", "features", "carried")}
            error = refused_without_writing(f"modes, {ADDED_MODE} removed while it shows", desk, folder, sleeve,
                                            showing)
            entry = desk.record.gearbox.user_work
            now = None if entry is None else {k: [dict(vars(x)) if hasattr(x, "__dict__") else x
                                                  for x in getattr(entry, k)]
                                              for k in ("components", "mates", "features", "carried")}
            problems = list(entry.problems) if entry is not None else []
            check(entry is not None and now == held and [p.kind for p in problems] == [swbuild.PROBLEM_MODE_SHOWING]
                  and list(getattr(problems[0], "subjects", []) or []) == [ADDED_MODE]
                  and list(entry.revision) == list(W.TAG["revision"]),
                  f"modes: the record keeps the inventory as it was ({now == held}) and the refusal, one problem "
                  f"{[(p.kind, list(getattr(p, 'subjects', []) or [])) for p in problems]}, read at {entry and entry.read_at} "
                  "(W9C-INTERFACES §11)")
            out["showing_refusal"] = str(error)
            keep_record(out, f"after the refusal of {ADDED_MODE}'s removal while it shows", desk)
            clean["showing"] = isinstance(error, swbuild.UserWorkRefused)

            say(f"-- modes  {ADDED_MODE}'s row put back, the first mode {FIRST_MODE} removed while {ADDED_MODE} shows")
            back = put_back(cleared, sheet_rows(fx_h2)["Modes"][-1])
            edit_live(desk, book, row_edits(hlh2, lh2), f"{ADDED_MODE} put back, {FIRST_MODE} cleared", cells=back)
            u = desk.update
            check(u is not None and not u.structural and u.in_place.modes_removed == (FIRST_MODE,)
                  and u.in_place.first_mode == NEXT_FIRST,
                  f"modes: classify removes {FIRST_MODE}, {NEXT_FIRST} the record's first: "
                  f"{u and (list(u.structural), u.in_place.modes_removed, u.in_place.first_mode)}")
            footer_ahead(desk, f"modes, {FIRST_MODE} removed")
            before = every_mode(f"modes, before {FIRST_MODE} goes", desk, users)
            person_shows(desk, folder, ADDED_MODE)       # the every-mode read leaves the first mode showing
            result, _ = press(desk, f"modes: {FIRST_MODE} removed")
            out["remove_first"] = in_place_fact(result)
            keep_record(out, f"after {FIRST_MODE}'s removal", desk)
            if result is None:
                A.section_stop(f"modes: the press removing {FIRST_MODE} raised: {desk.error}")
            ok = done_said(result, f"modes, {FIRST_MODE}")
            after_shown = active_now(desk)
            names = configurations_now(desk)
            clean["first"] = check(
                ok and result.modes_removed == [FIRST_MODE] and FIRST_MODE not in names
                and not desk.record.gearbox.left
                and list(desk.record.gearbox.modes) == [NEXT_FIRST, ADDED_MODE] and after_shown == ADDED_MODE,
                f"modes: {FIRST_MODE} deleted ({names}); the record's modes {list(desk.record.gearbox.modes)}, "
                f"{NEXT_FIRST} first; {ADDED_MODE} showing before and after")
            after = every_mode(f"modes, after {FIRST_MODE} went", desk, users)
            users_unchanged(f"modes, {FIRST_MODE} gone", before, after, users, mates)
            judged_modes(f"modes, {FIRST_MODE} gone", desk, out.setdefault("judged_first", {}), section3=False,
                         against={NEXT_FIRST: NEXT_FIRST, ADDED_MODE: ADDED_AT}, result=result)
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
        footer_ahead(desk, f"remove, {REMOVED_REDUCER}")
        foreseen = foreseen_names(desk)
        check(not foreseen, f"remove: the footer foresees nothing stopping it: {[(p.kind, list(p.subjects)) for p in foreseen]}")
        before = A.read_now(f"remove, before {REMOVED_REDUCER} goes", box.assembly, folder, others, [])
        result, _ = press(desk, f"remove: {REMOVED_REDUCER} taken out")
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
        part_kept = [os.path.basename(p.path) for p in desk.record.parts if store.same_path(p.path, gone.part)]
        others_use = [c.gear for c in rec.components if store.same_path(c.part, gone.part)]
        check(bool(others_use) or not part_kept, f"remove: {REMOVED_REDUCER}'s part entry left the record's parts, no "
                                                 f"gear using its file now (C6; the file stays on disk): kept "
                                                 f"{part_kept or 'none'}, other gears on it {others_use or 'none'}")
        check(not rec.left, f"remove: nothing left over on the record (left {rec.left})")
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
        footer_ahead(desk, f"remove, {gear}, the user's components there")
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
        footer_ahead(desk, f"remove, {gear}, with the user's lock on it")
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


RANGEBOX_ENGAGED = {"H": ["HighDog"], "N": [], "L": ["LowDog"]}   # §3, RangeBox before W9b: what each mode engages


def section_remake(out):
    stems = GATES["remake"]
    say(f"== remake  Sun 29 -> {GEARS_TEETH['Sun']}, Planet 13 -> {GEARS_TEETH['Planet']}, Ring 55 -> "
        f"{GEARS_TEETH['Ring']} (not 30/12/54: the ring's part does not rebuild set from 55 to 54, a part-level fault "
        "the ring section reads; 56 rebuilds) on a copy of setup.master, RangeBox with the user's work (the centre "
        "distance and the "
        "planets' spacing kept; it needs nothing of fixed's): the gear mates of a gearbox with modes made again "
        f"(ruling 9.16 lifted), first refused with findings.{finding_name(stems[0])} as it stands")
    rb, _, _ = specs()
    teeth = with_teeth(rb)
    folder, path, book, desk = A.copy_desk(A.user_master(), "remake", "RangeBox.xlsx")
    clean = False
    try:
        same_sheets("remake", desk, rb)
        headers_fact("remake", book)
        box = desk.record.gearbox
        users, mates = A.rb_users(), list(A.RB_USER_MATES)
        sun = gear_entry(box, "Sun").part
        edit_live(desk, book, row_edits(rb, teeth), "the teeth")
        u = desk.update
        ratios = list(u.ratios) if u is not None else []
        check(u is not None and not u.structural and not u.needs_new_revision and not u.in_place and ratios,
              f"remake: classify makes it a value Update remaking {ratios}: {u and list(u.structural)}")
        out["refusal"] = gated_refusal("remake, the gate as it stands", desk, folder, stems, sun)
        with patched(stems):
            desk.plan_solidworks()
            footer_ahead(desk, "remake, the finding patched")
            before = every_mode("remake, before", desk, users)
            result, _ = press(desk, "remake: the teeth")
            out["press"], out["in_place"] = A._update_fact(desk, result), in_place_fact(result)  # noqa: SLF001
            if result is None:
                A.section_stop(f"remake: the press with the finding patched raised: {desk.error}")
            ok = done_said(result, "remake")
            record_brought_forward("remake", desk)
            remade = set(result.remade_in_modes)
            clean = check(ok and set(ratios) <= set(result.ratios) and set(ratios) <= remade
                          and not (remade & set(result.senses_unread)) and not result.user_features_in_error
                          and not desk.record.gearbox.left,
                          f"remake: every gear mate {ratios} made again with modes ({sorted(remade)}), each one's sense "
                          f"read (unread {result.senses_unread}), the user's keyway in Sun's part not in error "
                          f"{[f.name for f in result.user_features_in_error]}, nothing left over on the record")
            if not ok:
                say(f"fact    remake: the press stopped in a part: {result.failures}; it said what it had changed and that "
                    f"nothing was saved ({result.skipped!r}); the section `ring` reads that part on its own copies")
                A.section_stop(f"remake: the Update stopped in a part ({result.failures}), so no gear mate was remade "
                               "and its modes are not judged on a half-done change")
            after = every_mode("remake, after", desk, users)
            users_unchanged("remake", before, after, users, mates)
            judged_modes("remake", desk, out.setdefault("judged", {}), section3=False, banded=False,
                         engaged=RANGEBOX_ENGAGED, result=result)
            l_ratio = next((m.ratio for m in desk.a.report.modes if m.name == "L"), None)
            check(l_ratio is not None and abs(l_ratio - REMAKE_RATIO_L) < 1e-9,
                  f"remake: the app's read gives L {l_ratio} (1 + 56/28 = {REMAKE_RATIO_L})")
    finally:
        if not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], folder, "remake")
        proposed(finding_name("UPDATE_MAKES_MATES_WITH_MODES"), True if clean else None,
                 f"remake: gear mates of a gearbox with modes remade, flags and senses read in every mode: {clean}")
    remake_again(out.setdefault("again", {}))




def remake_again(out):
    """The fixes review's M3 (B's ff98d5a), on its own copy of setup.master: Sun 30, Planet 12, Ring 54 pressed with
    swbuild.LANDING_STEPS patched to () for that press only, so it stops in the ring; pressed again without closing:
    the still-open sentence, the record's in-error mark kept, nothing set in a part, the footer's sentence kept; then
    every document of the copy closed without saving (as the sentences say), the patch restored, pressed again: routed
    by way of 53, the mark gone, the footer quiet, the ring at 54 clean, the stage's gear mates remade. Sentences matched
    by their distinctive parts."""
    stems = GATES["remake"]
    say("-- remake  the fixes review's M3: a press stopped in the ring, pressed again without closing, then after "
        "closing without saving (Sun 30, Planet 12, Ring 55 -> 54 on its own copy of setup.master)")
    rb, _, _ = specs()
    stage = dataclasses.replace(rb, gears=tuple(dataclasses.replace(g, teeth=M3_STAGE[g.id]) if g.id in M3_STAGE else g
                                                for g in rb.gears))
    folder, path, book, desk = A.copy_desk(A.user_master(), "remake-again", "RangeBox.xlsx")
    try:
        same_sheets("remake, M3", desk, rb)
        ring_part = gear_entry(desk.record.gearbox, "Ring").part
        stem = os.path.splitext(os.path.basename(ring_part))[0]
        edit_live(desk, book, row_edits(rb, stage), "Sun 30, Planet 12, Ring 54")
        u = desk.update
        ratios = list(u.ratios) if u is not None else []

        def marked():
            return any(store.same_path(p, ring_part) for p in desk.record.unsaved_in_error)

        def note():
            return desk.note[0] if getattr(desk, "note", None) else ""
        with patched(stems):
            desk.plan_solidworks()
            steps = swbuild.LANDING_STEPS
            swbuild.LANDING_STEPS = ()
            say("PATCH   swbuild.LANDING_STEPS = () in this process, for the first press only (was "
                f"{steps}): the ring's change set straight, as before 63bbc33")
            try:
                first, _ = press(desk, "remake, M3: the first press, set straight")
            finally:
                swbuild.LANDING_STEPS = steps
            done_said(first, "remake, M3, first")
            text = note()
            out["first"] = {"status": text, "failures": list(first.failures) if first else None,
                            "marked": list(desk.record.unsaved_in_error)}
            check(first is not None and bool(first.failures) and stem in text and "left in error" in text
                  and "without saving" in text and marked() and swbuild.LANDING_STEPS == steps,
                  f"remake, M3: the press set straight stops in {stem}, the status says it is left in error and to "
                  f"close without saving, the record marks it ({list(desk.record.unsaved_in_error)}); the patch "
                  "restored")

            # Step 2 (the fixes review's addendum §6): the app now stops after its check phase and before any write.
            # Read, just before and just after it: every document's save flag and file time, every part's globals
            # (equation writes are not traced), the assembly as W9a reads it (frames, mates' codes and flags per mode),
            # the stage's gear mates' ratios, and the ring's features. None of these reads may mark anything (read_now
            # STOPs on one that does; the flags bracket all of them).
            box = desk.record.gearbox
            pairs = A.pairs_of(box, A.rb_users())
            parts = sorted({c.part for c in box.components} | {box.layout} | {c.path for c in box.carriers})
            ring_file = os.path.basename(ring_part)
            step_1_files = tuple(os.path.basename(gear_entry(box, g).part) for g in M3_CHANGED_BY_STEP_1)

            def gear_ratios(s):
                got = {}
                for i, name in enumerate(ratios):
                    s.find_mate(f"m3r{i}", name)
                    got[name] = tuple(s.gear_mate_ratio(f"m3r{i}"))
                return got

            def read_all(when):
                """The reads; the save flags and file times taken last before the press and first after it, so their
                bracket holds the press alone (a read that marked would show there too, as a FAIL)."""
                states = B.documents_state(f"remake, M3: {when} step 2", desk, folder) if when == "after" else None
                now = A.read_now(f"remake, M3: {when} step 2", box.assembly, folder, pairs, list(box.modes))
                globals_ = {os.path.basename(p): run(f"remake, M3: {os.path.basename(p)}'s globals {when} step 2",
                                                     lambda s, p=p: W.live_globals(s, p)) for p in parts}
                ratios_ = run(f"remake, M3: the gear mates' ratios {when} step 2", job(box.assembly, gear_ratios))
                ring = run(f"remake, M3: the ring's features {when} step 2", job(ring_part, landing_state))
                if states is None:
                    states = B.documents_state(f"remake, M3: {when} step 2", desk, folder)
                return states, now, globals_, ratios_, ring
            s_before, now_before, globals_before, ratios_before, ring_before = read_all("before")
            say(f"fact    remake, M3: before step 2, modified {sorted(n for n, f in s_before['flags'].items() if f)} "
                f"(step 1 changed {list(step_1_files)}); the ring {ring_before}; ratios {ratios_before}")

            desk.plan_solidworks()
            second, calls = press(desk, "remake, M3: pressed again without closing")
            done_said(second, "remake, M3, second")
            text = note()
            set_in = [(p.document, list(p.changed)) for p in (second.parts if second else []) if p.changed]
            changing = W.nothing_changed_calls(calls) + [c for c in calls if c[0] in ("AddComponent5", "SaveAs3")]
            s_after, now_after, globals_after, ratios_after, ring_after = read_all("after")
            summary = {k: list(getattr(second, k, []) or []) for k in ("changed", "mates_made", "remade_in_modes",
                                                                        "placed", "failures")}
            summary["skipped"] = getattr(second, "skipped", "") if second else ""
            wrote = wrote_nothing(changing, globals_before, globals_after, s_before, s_after, summary, ring_file,
                                  ring_after, A.written(now_before, now_after), ratios_before, ratios_after,
                                  step_1_files) if second is not None else ["no result"]
            out["second"] = {"status": text, "set_in_parts": set_in, "marked": list(desk.record.unsaved_in_error),
                             "remade_in_modes": summary["remade_in_modes"], "result": summary,
                             "changing_calls": [list(c) for c in changing], "ring_before": ring_before,
                             "ring_after": ring_after, "ratios": [ratios_before, ratios_after],
                             "flags": [s_before["flags"], s_after["flags"]], "wrote": wrote}
            say(f"fact    remake, M3: pressed again without closing: status {text!r}; parts set {set_in}; result "
                f"{summary}; calls that change or show {changing or 'none'}; the ring after {ring_after}")
            check(second is not None and "still open in SolidWorks" in text and stem in text and "set nothing" in text
                  and "without saving" in text and "already matches" not in text and status_alone(text) and marked()
                  and not set_in,
                  f"remake, M3: pressed again without closing, the status says {stem} is still open in error and to "
                  "close it without saving, alone (never that SolidWorks already matches, no offer to save), the record "
                  "keeps its mark, nothing set in a part")
            check(not wrote,
                  f"remake, M3: step 2 stopped before any write: no call that changes or shows anything, every part's "
                  f"globals, every document's save flag and file time as before (only {list(step_1_files)} modified, "
                  f"from step 1), nothing changed, made, remade or placed, its stop said skipped and named {ring_file} "
                  f"alone, the ring still at Tooth Space 72 and 54 teeth, the assembly's frames, mates and flags and "
                  f"the gear mates' ratios as before: {wrote or 'nothing written'}")
            f = desk.say_footer("remake, M3: the footer after the second press")
            check(footer_says_close(f.text, stem),
                  f"remake, M3: the footer says {stem} is to be closed without saving (left in error when it stopped, "
                  "or still open in SolidWorks), and offers to keep nothing")

            left = run("remake, M3: every document of the copy closed without saving", W.quit_in(folder))
            say(f"person  remake, M3: closed every document of the copy without saving, as the sentences say; left "
                f"{left}")
            desk.plan_solidworks()
            third, _ = press(desk, "remake, M3: pressed again after closing, the patch restored")
            ok = done_said(third, "remake, M3, third")
            text = note()
            ring = next((p for p in (third.parts if third else []) if stem.casefold() in str(p.document).casefold()),
                        None)
            read = run("remake, M3: the ring's features", job(ring_part, landing_state))
            states = read["in_error"]
            remade = set(third.remade_in_modes) if third else set()
            f = desk.say_footer("remake, M3: the footer after the third press")
            out["third"] = {"status": text, "ring_by_way_of": getattr(ring, "by_way_of", None),
                            "in_error": states, "remade_in_modes": sorted(remade),
                            "marked": list(desk.record.unsaved_in_error), "footer": f.text}
            out["third"]["teeth"] = read.get("teeth")
            check(ok and ring is not None and tuple(ring.by_way_of) == (TEETH_NAME, "53") and ring.rebuilt
                  and not states and read.get("teeth") == 54.0 and not marked() and set(ratios) <= remade and "left in error" not in f.text
                  and f.ok,
                  f"remake, M3: after closing without saving, the press goes through routed by way of 53 "
                  f"({getattr(ring, 'by_way_of', None)}), the ring at 54 with nothing in error ({states}), the mark "
                  f"gone ({list(desk.record.unsaved_in_error)}), the stage's gear mates {ratios} remade "
                  f"({sorted(remade)}), the footer quiet ({f.ok})")
    finally:
        if not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], folder, "remake-again")


# -- ring: why the ring's part did not rebuild at 54 teeth (a diagnostic, facts only) ------------------------------------

RING_ENUMS = ("swMateType_e", "swFeatureError_e", "swConstrainedStatus_e", "swSketchRelationFilterType_e")


def part_diagnosis(path, variables, enums):
    """One part, opened from its file: its features and equations before; ``variables`` set by the app's own
    ``swbuild.update_variables`` (its rebuild), unless None; then every feature's error code (``feature_states``),
    each one in error with its ``swFeatureError_e`` name and what ``IFeature.GetErrorCode2`` returns beside the code;
    each sketch's ``GetConstrainedStatus`` and its relations counted by every ``swSketchRelationFilterType_e`` filter;
    every equation's text, value and ``IEquationMgr.Status`` after reading it; ``IModelDocExtension.GetWhatsWrong``
    (NEW); the globals; the bodies and the volume where a body exists. Nothing saved. Each read guarded."""
    import pythoncom
    from win32com.client import VARIANT
    words = {v: k for k, v in enums.get("swFeatureError_e", {}).items()}
    constrained = {v: k for k, v in enums.get("swConstrainedStatus_e", {}).items()}
    filters = enums.get("swSketchRelationFilterType_e", {})

    def guarded(fn):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - what will not read is said in its place
            return f"unread: {type(exc).__name__}: {exc}"

    def work(s):
        s.open_document(path)
        doc = s._doc()  # noqa: SLF001
        out = {"before": {"features": [(f.name, f.type_name, f.code) for f in s.feature_states()],
                          "equations": guarded(s.equations)}}
        if variables is not None:
            def setting():
                done = swbuild.update_variables(s, variables, path)
                return {"changed": list(done.changed), "rebuilt": done.rebuilt, "failures": list(done.failures)}
            out["set"] = guarded(setting)
        states = s.feature_states()
        out["features"] = [(f.name, f.type_name, f.code, f.warning) for f in states]
        out["in_error"] = []
        for f in states:
            if not f.code:
                continue
            feature = call(doc, "FeatureByName", f.name)

            def raw_code(feature=feature):
                holder = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
                back = call(feature, "GetErrorCode2", holder)
                return {"returned": plain(back), "is_warning": plain(holder)}
            out["in_error"].append({"name": f.name, "type": f.type_name, "code": f.code,
                                    "word": words.get(f.code, "?"), "warning": f.warning,
                                    "GetErrorCode2": guarded(raw_code) if feature is not None else "no feature"})
        sketches = {}
        for f in states:
            if f.type_name != "ProfileFeature":
                continue
            feature = call(doc, "FeatureByName", f.name)

            def sketch_read(feature=feature):
                sketch = call(feature, "GetSpecificFeature2")
                status = member(sketch, "GetConstrainedStatus")
                manager = call(sketch, "RelationManager")
                counts = {k: guarded(lambda v=v: plain(call(manager, "GetRelationsCount", v)))
                          for k, v in filters.items()}
                return {"status": constrained.get(status, status), "relations": counts}
            sketches[f.name] = guarded(sketch_read)
        out["sketches"] = sketches

        def equations_read():
            manager = s._equation_manager()  # noqa: SLF001
            rows = []
            for i in range(int(call(manager, "GetCount"))):
                text = str(call(manager, "Equation", i))
                value = guarded(lambda i=i: float(call(manager, "Value", i)))
                rows.append((text, value, guarded(lambda: plain(member(manager, "Status")))))
            return rows
        out["equations"] = guarded(equations_read)

        def whats_wrong():
            holders = outs("vvv")
            back = call(call(doc, "Extension"), "GetWhatsWrong", *holders)
            found = getattr(holders[0], "value", None) or []
            names = [guarded(lambda f=f: str(call(f, "Name"))) for f in list(found)]
            return {"returned": plain(back), "features": names, "codes": plain(holders[1]),
                    "warnings": plain(holders[2])}
        out["whats_wrong"] = guarded(whats_wrong)
        out["globals"] = guarded(s.equation_values)
        out["bodies"] = guarded(lambda: len(list(member(doc, "GetBodies2", 0, True) or [])))
        out["volume"] = guarded(s.volume_mm3) if out["bodies"] else None
        out["flag"] = bool(call(doc, "GetSaveFlag"))
        return out
    return work


def diagnosis_said(label, got):
    say(f"fact    {label}: set {got.get('set', '(nothing set)')}; bodies {got.get('bodies')}, volume {got.get('volume')}; "
        f"globals {got.get('globals')}")
    if not got.get("in_error"):
        say(f"fact    {label}: no feature in error")
    for e in got.get("in_error", []):
        say(f"fact    {label}: in error: {e['name']} ({e['type']}) code {e['code']} {e['word']}, warning {e['warning']}; "
            f"GetErrorCode2 {e['GetErrorCode2']}")
    odd = {n: v for n, v in (got.get("sketches") or {}).items() if not isinstance(v, dict)
           or v.get("status") not in ("swFullyConstrained",)}
    say(f"fact    {label}: sketches not fully defined, or unread: {odd or 'none'}")
    eq = got.get("equations")
    bad = [r for r in eq if isinstance(r[1], str) or r[2] == -1] if isinstance(eq, list) else eq
    say(f"fact    {label}: equations reading in error or unread: {bad or 'none'}; What's Wrong {got.get('whats_wrong')}")


SPACE_SKETCH_NAME = "Tooth Space Sketch"   # gears.spur.SPACE_SKETCH: the ring's tooth-space sketch, as the app names it


def sketch_dump(s, enums, name=SPACE_SKETCH_NAME, segments_only=False):
    """The sketch ``name`` of the build part as SolidWorks holds it, in sketch coordinates (mm, to 1e-6): every
    segment in ``GetSketchSegments`` order, its type (``swSketchSegments_e``), its construction flag, its end points,
    and for an arc its centre, radius, direction (``GetRotationDir``) and sweep; a spline or equation curve its point
    count, its ends its first and last points (``GetPoints2``: sketch point objects); the dimensions (``Session.feature_dimensions``: names and SystemValue, in
    metres or radians as SolidWorks holds them, so 1e-9 there is 1e-6 mm); the
    relations' kinds (``swConstraintType_e``). Every member that returns an array is called if late binding hands it
    back uncalled (``member``); each read guarded."""
    seg_words = {v: k for k, v in enums.get("swSketchSegments_e", {}).items()}
    rel_words = {v: k for k, v in enums.get("swConstraintType_e", {}).items()}
    doc = s._doc()  # noqa: SLF001

    def mm(point):
        if point is None:
            return None
        return (round(float(call(point, "X")) * 1000.0, 6), round(float(call(point, "Y")) * 1000.0, 6))

    def guarded(fn):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            return f"unread: {type(exc).__name__}: {exc}"

    feature = call(doc, "FeatureByName", name)
    if feature is None:
        return {"error": f"no feature {name}"}
    sketch = call(feature, "GetSpecificFeature2")
    segments = []
    for seg in list(member(sketch, "GetSketchSegments") or []):
        kind = guarded(lambda: int(member(seg, "GetType")))
        row = {"type": seg_words.get(kind, kind), "construction": guarded(lambda: bool(call(seg, "ConstructionGeometry")))}
        is_spline = row["type"] in ("swSketchSPLINE",) or kind == 3
        for key, getter in () if is_spline else (("start", "GetStartPoint2"), ("end", "GetEndPoint2")):
            got = guarded(lambda g=getter: mm(member(seg, g)))
            row[key] = got if isinstance(got, tuple) else None
            if not isinstance(got, tuple):
                row[f"{key}_read"] = got
        if row["type"] in ("swSketchARC",) or kind == 1:
            centre = guarded(lambda: mm(member(seg, "GetCenterPoint2")))
            row["centre"] = centre if isinstance(centre, tuple) else None
            radius = guarded(lambda: float(member(seg, "GetRadius")) * 1000.0)
            row["radius"] = round(radius, 6) if isinstance(radius, float) else None
            direction = guarded(lambda: int(member(seg, "GetRotationDir")))
            row["direction"] = direction if isinstance(direction, int) else None
            if row["centre"] and row["start"] and row["end"] and row["direction"] is not None:
                row["sweep"] = round(arc_sweep(row["centre"], row["start"], row["end"], row["direction"]), 6)
        if is_spline:
            # ISketchSpline.GetPoints2 hands back sketch point objects (API-LEDGER, ISketchSegment: verified 2026), and
            # a spline has no GetStartPoint2 (run 6: AttributeError): its ends are its first and last points.
            def spline_points():
                pts = [mm(p) for p in list(member(seg, "GetPoints2") or [])]
                return {"count": len(pts), "first": pts[0] if pts else None, "last": pts[-1] if pts else None}
            got = guarded(spline_points)
            row["points"] = got if isinstance(got, dict) else None
            if isinstance(got, dict):
                row["start"], row["end"] = got["first"], got["last"]
            else:
                row["start"] = row["end"] = None
                row["points_read"] = got
        segments.append(row)

    if segments_only:
        return {"segments": segments}

    def relations():
        manager = call(sketch, "RelationManager")
        everything = enums.get("swSketchRelationFilterType_e", {}).get("swAll", 0)
        found = list(member(manager, "GetRelations", everything) or [])
        return sorted(rel_words.get(int(member(r, "GetRelationType")), "?") for r in found)
    dims = guarded(lambda: [(n, round(v, 12)) for n, v in s.feature_dimensions(name)])   # SystemValue: m, rad
    return {"segments": segments, "dimensions": dims if isinstance(dims, list) else [],
            "dimensions_read": None if isinstance(dims, list) else dims, "relations": guarded(relations)}


def ring_route(path, steps, variables_of):
    """One copy taken through ``steps`` (a tooth count set by the app's ``update_variables``, or ``"force"``, a
    second ``ForceRebuild3(False)``), each step's features in error read after it; at the end whether every feature
    is clean, and the volume. Nothing saved."""
    def work(s):
        s.open_document(path)
        doc = s._doc()  # noqa: SLF001
        out = {"steps": []}
        for step in steps:
            if step == "force":
                done = {"forced": bool(call(doc, "ForceRebuild3", False))}
            else:
                result = swbuild.update_variables(s, variables_of(step), path)
                done = {"set": step, "rebuilt": result.rebuilt, "failures": list(result.failures)}
            done["in_error"] = [(f.name, f.code) for f in s.feature_states() if f.code]
            out["steps"].append(done)
        out["clean"] = not out["steps"][-1]["in_error"]
        out["volume"] = s.volume_mm3()
        return out
    return work


def section_ring(out):
    say("== ring  a diagnostic, script-side and facts only (no proposal): why the ring's part from S0's master does not "
        "rebuild set from 55 to 54 teeth (run 5: its Tooth Space cut reads code 72, a self-intersecting contour; 56, "
        "53, 50 and 60 rebuild, so does a 54-tooth ring from scratch). On fresh copies, nothing saved: the Tooth Space "
        "sketch dumped as built at 55, after the set to 54, and built from scratch at 54, the last two compared; then "
        "routes to 54 (a forced rebuild after; through 56; through 53; and 54 then back to 55) and 56 then 55; Sun at 30 for "
        "comparison. update_variables already runs inside begin_build and end_build, so no bracket is added")
    import shutil
    import w9c_probes as P
    from gear_generator.gears import kind_for, plan_for
    P.ENUMS.clear()
    enums = P.swconst(RING_ENUMS + ("swSketchSegments_e", "swConstraintType_e"))
    say("NEW     ISketch.GetSketchSegments, ISketchSegment.GetType and ConstructionGeometry, GetStartPoint2, "
        "GetEndPoint2, ISketchArc.GetCenterPoint2, GetRadius and GetRotationDir, ISketchSpline.GetPoints2, "
        "ISketchRelationManager.GetRelations(swAll) and ISketchRelation.GetRelationType, each read only")
    gaps = {(a, b): start_lands_on_cap(a, b) for a, b in ((55, 54), (56, 55), (55, 53), (55, 56), (53, 54))}
    say(f"fact    ring: by the app's own maths, the new flank start's distance from where Li+ (0.625 mm, flank start to "
        f"tip cap) ends before the set, mm: { {f'{a} -> {b}': round(v[0], 4) for (a, b), v in gaps.items()} }")
    rb, _, _ = specs()
    master = A.rangebox_master()
    root = W.fresh_folder("ring")
    ring_part = "Ring_m1.25_N55.SLDPRT"           # RangeBox's ring as S0's master holds it

    def variables_of(gear, teeth):
        spec = with_gear_spec(rb, gear, teeth=str(teeth)).gear(gear).gear_spec(rb.box)
        kind = kind_for(spec)
        return kind.variables(spec, kind.derive(spec))

    def copy_of(name, case):
        folder = os.path.join(root, case)
        os.makedirs(folder, exist_ok=True)
        shutil.copy2(os.path.join(master, name), os.path.join(folder, name))
        return folder, os.path.join(folder, name)

    def closed(case, folder):
        left = run(f"ring {case}: closed unsaved", W.quit_in(folder))
        say(f"fact    ring {case}: closed without saving, left {left}")

    def dumped(case, path, variables):
        diagnose = part_diagnosis(path, variables, enums)

        def work(s):
            got = diagnose(s)
            got["sketch"] = sketch_dump(s, enums)
            return got
        return run(f"ring {case}", work, 600)

    def say_dump(case, dump):
        for i, seg in enumerate(dump.get("segments") or []):
            say(f"        {case} #{i}: {seg}")
        say(f"        {case} dimensions {dump.get('dimensions')} {dump.get('dimensions_read') or ''}; relations "
            f"{dump.get('relations')}")

    states = {}
    for case, teeth in (("built-55", None), ("set-54", 54)):
        folder, path = copy_of(ring_part, case)
        try:
            got = dumped(case, path, None if teeth is None else variables_of("Ring", teeth))
        finally:
            closed(case, folder)
        diagnosis_said(f"ring {case}", got)
        say_dump(case, got["sketch"])
        states[case] = got
    say("-- ring  a 54-tooth ring built from scratch by the strip's own plan_for and swbuild.build")
    spec54 = with_gear_spec(rb, "Ring", teeth="54").gear("Ring").gear_spec(rb.box)
    kind = kind_for(spec54)
    folder = os.path.join(root, "build-54")
    os.makedirs(folder, exist_ok=True)
    path54 = os.path.join(folder, spec54.stem() + ".SLDPRT")
    plan = plan_for(spec54, kind.derive(spec54), "", path54)
    say(f"fact    ring build-54: the plan's checks {plan.check()}")
    try:
        built = run("ring build-54", lambda s: swbuild.build(s, plan), 900)
        say(f"fact    ring build-54: built ok {built.ok}, failures {list(built.failures)}")
        if built.ok:
            got = dumped("build-54", path54, None)
            diagnosis_said("ring build-54", got)
            say_dump("build-54", got["sketch"])
            states["build-54"] = got
    finally:
        closed("build-54", folder)
    out["states"] = {k: {"in_error": v.get("in_error"), "volume": v.get("volume"), "sketch": v.get("sketch")}
                     for k, v in states.items()}
    if "set-54" in states and "build-54" in states:
        diff = out["diff_set_vs_scratch"] = sketch_diff(states["set-54"]["sketch"], states["build-54"]["sketch"])
        say(f"fact    ring: the Tooth Space sketch set to 54 against the one built at 54: segments that differ "
            f"{diff['segments'] or 'none'}; dimensions {diff['dimensions'] or 'the same'}; relation kinds "
            f"{'the same' if diff['relations'] is None else diff['relations']}; count {diff['count'] or 'the same'}")
    if "built-55" in states and "set-54" in states:
        moved = out["diff_55_vs_set"] = sketch_diff(states["built-55"]["sketch"], states["set-54"]["sketch"])
        flips = [(i, t, w) for i, t, w in moved["segments"] if "direction" in w or "sweep" in w]
        say(f"fact    ring: from 55 to the set 54, the segments whose direction or sweep changed: {flips or 'none'}")

    say("-- ring  routes to 54 on fresh copies: whether every feature ends clean, and the volume")
    out["routes"] = {}
    for label, steps in RING_ROUTES.items():
        case = "route-" + "-".join(str(x) for x in steps)
        folder, path = copy_of(ring_part, case)
        try:
            got = run(f"ring {case}", ring_route(path, steps, lambda n: variables_of("Ring", n)), 600)
        finally:
            closed(case, folder)
        out["routes"][label] = got
        say(f"fact    ring {label}: each step {got['steps']}; clean at the end {got['clean']}, volume "
            f"{got['volume']:.6f} mm³")
    say("-- ring  for comparison: Sun 29 -> 30 on a copy of Sun's part (it rebuilt in run 4's remake)")
    folder, path = copy_of("Gear_m1.25_N29.SLDPRT", "sun-30")
    try:
        got = run("ring sun-30", part_diagnosis(path, variables_of("Sun", 30), enums), 600)
    finally:
        closed("sun-30", folder)
    diagnosis_said("ring sun-30", got)
    out["sun_30"] = {"in_error": got.get("in_error"), "volume": got.get("volume")}


def landing_case_job(path, variables, straight, line=None, enums=None):
    """One part set to ``variables`` by the app's own ``swbuild.update_variables`` as it stands, or with
    ``swbuild.LANDING_STEPS`` patched to ``()`` (``straight``) and restored in a finally: what the result says
    (``by_way_of``, ``landing``, ``rebuilt``, ``failures``), every rebuild's own return in order (the session's
    ``rebuild`` wrapped on this instance only, and unwrapped after), the features in error after, the tooth count the
    part holds, the volume. With ``line`` (``short_line`` before and after), the short solved line's ends in the Tooth
    Space sketch before the set and after it (``line_ends``). Nothing saved."""
    def work(s):
        s.open_document(path)
        dump0 = sketch_dump(s, enums or {}, segments_only=True) if line else None
        links = sorted({t.split("=", 1)[0].strip().strip('"') for t, _ in s.equations() if "@" in t.split("=", 1)[0]})
        rebuilds = []
        original = s.rebuild

        def counted(*args, **kwargs):
            got = original(*args, **kwargs)
            rebuilds.append(bool(got))
            return got
        steps = swbuild.LANDING_STEPS
        s.rebuild = counted
        try:
            if straight:
                swbuild.LANDING_STEPS = ()
            r = swbuild.update_variables(s, variables, path)
        finally:
            swbuild.LANDING_STEPS = steps
            del s.rebuild
        out = {"by_way_of": tuple(r.by_way_of), "landing": [tuple(x) for x in r.landing], "rebuilt": r.rebuilt,
               "failures": list(r.failures), "changed": list(r.changed), "rebuilds": rebuilds,
               "steps_restored": swbuild.LANDING_STEPS == steps, "unchanged": list(r.unchanged), "links": links}
        out.update(landing_state(s))
        if line:
            out["line"] = line_ends(dump0, sketch_dump(s, enums or {}, segments_only=True), *line)
        return out
    return work


def user_error_job(path, variables):
    """The review's M1: the part opened, the user's own cut made through all on a circle on the ring's centre that
    takes its tooth tips (the session's own sketch, dimension and cut calls, as W9a's keyway), rebuilt clean; then its
    diameter linked by the user's equation to one inside the ring's hollow centre, so it removes nothing and reads in
    error, rebuilt; what is in error then, and the cut sketch's dimensions; then the app's own ``update_variables`` as
    it stands, every rebuild's return counted as in ``landing_case_job``. Nothing saved."""
    sketch = f"{USER_CUT} Sketch"

    def work(s):
        s.begin_build()
        try:
            s.open_document(path)
            s.open_sketch("uc", 1)
            s.sketch_circle("ucc", (0.0, 0.0), USER_CUT_MADE_D / 2.0)
            s.dimension(USER_CUT_DIM, ("ucc",), (USER_CUT_MADE_D * 0.6, USER_CUT_MADE_D * 0.1))
            s.close_sketch("uc", sketch)
            s.cut_extrude("uccut", "uc", USER_CUT)
        finally:
            s.end_build()
        made = bool(s.rebuild())
        made_states = [(f.name, f.code) for f in s.feature_states() if f.code]
        s.link_dimension(f"{USER_CUT_DIM}@{sketch}", f"{USER_CUT_D:g}")
        linked = bool(s.rebuild())
        before = [(f.name, f.code) for f in s.feature_states() if f.code]
        try:
            dims = s.feature_dimensions(sketch)
        except Exception as exc:  # noqa: BLE001 - said in its place
            dims = f"unread: {type(exc).__name__}: {exc}"
        out = landing_case_job(path, variables, False)(_Reopened(s))
        out.update({"made_rebuilt": made, "made_in_error": made_states, "linked_rebuilt": linked,
                    "in_error_before": before, "user_cut_dims": dims})
        return out
    return work


class _Reopened:
    """The session with ``open_document`` a no-op (the part is open and active already, its user cut unsaved)."""

    def __init__(self, s):
        object.__setattr__(self, "_s", s)

    def open_document(self, path):
        return None

    def __getattr__(self, name):
        return getattr(self._s, name)

    def __setattr__(self, name, value):
        setattr(self._s, name, value)

    def __delattr__(self, name):
        delattr(self._s, name)


def line_ends(dump0, dump1, before, after):
    """The short solved line (``Li+`` or ``L+``) found in the dump before the set by its ends as the sketch's maths put
    them (``before``), and the same segment read after: its ends each time (flank start first), the ends the maths
    put it at after, how far the solved end is from there, and whether it went past the origin (``far_side``)."""
    i, swapped = line_in_dump((dump0 or {}).get("segments"), *before)
    if i is None:
        return {"found": False}
    segs = (dump1 or {}).get("segments") or []
    if i >= len(segs):
        return {"found": True, "index": i, "after": "no such segment after"}

    def ends(seg):
        a, b = seg.get("start"), seg.get("end")
        return (b, a) if swapped else (a, b)
    was, now = ends(dump0["segments"][i]), ends(segs[i])
    out = {"found": True, "index": i, "before": was, "after": now,
           "expected": (tuple(round(v, 6) for v in after[0]), tuple(round(v, 6) for v in after[1]))}
    if isinstance(now[0], tuple) and isinstance(now[1], tuple):
        out["end_off_mm"] = round(math.dist(now[1], after[1]), 6)
        out["far_side"] = far_side(now[0], now[1])
    return out


def landing_state(s):
    """The build part's features in error, its tooth count, its volume (guarded: a part in error may have no body)."""
    out = {"in_error": [(f.name, f.code) for f in s.feature_states() if f.code]}
    held = s.equations()
    teeth = [v for t, v in held if t.strip().startswith(f'"{TEETH_NAME}"')]
    module = [v for t, v in held if t.strip().startswith('"Module"')]
    out["teeth"] = teeth[0] if teeth else None
    out["module"] = module[0] if module else None
    try:
        out["volume"] = s.volume_mm3()
    except Exception as exc:  # noqa: BLE001 - no body: said in its place
        out["volume"] = None
        out["volume_read"] = f"{type(exc).__name__}: {exc}"
    return out


TEETH_NAME = "No. of Teeth"     # gears.spur.TEETH, the global LANDING_STEPS moves


def section_landing(out):
    say("== landing  A's fix (63bbc33), measured, facts and checks, no proposal (no gate): gears.landing foresees a "
        "landing from the part's globals before and after, and swbuild.update_variables sets the change by way of the "
        "nearest safe tooth count, two rebuilds. On fresh copies of S0's master's parts or of parts built here from "
        "scratch, nothing saved, every document closed: (1) routed as the app stands; (2) the threshold: the same set "
        "straight (swbuild.LANDING_STEPS patched to () in this process, restored), with two external gears, then the "
        "externals routed; (3) changes that land nothing, one rebuild; (4) a module change with a tooth change; (5) "
        "the straight failure closed unsaved and reopened; and the fixes review's cases (c997e85): (6) just above 0.2, "
        "unrouted and clean; (7) the old end past the new start (ring m1 36 -> 34) and one well clear; (8) recipe B, "
        "never routed, its dimension links read; (9) a module-only landing, by way of 54 and back; (10) a user's own "
        "feature in error on a routed part. Each straight case reads the short solved line's ends before and after. A "
        "FAIL only where a routed result is not clean or not as foreseen, or a document is left open or saved")
    import shutil
    from gear_generator.gears import kind_for, plan_for
    check(TEETH_NAME == swbuild.TEETH_GLOBAL, f"landing: the tooth count's global is {swbuild.TEETH_GLOBAL!r}")
    rb, _, _ = specs()
    master = A.rangebox_master()
    root = W.fresh_folder("landing")

    def label(key):
        gear, module, teeth = key
        return f"{gear}-m{module}-{teeth}"

    say("-- landing  the parts built from scratch: every start not in S0's master and every routed case's target")
    built = {}
    for key in landing_builds():
        spec = landing_spec(*key, rb)
        kind = kind_for(spec)
        folder = os.path.join(root, "built", label(key))
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, spec.stem() + ".SLDPRT")
        plan = plan_for(spec, kind.derive(spec), "", path)
        checks = plan.check()

        def build(s, plan=plan):
            r = swbuild.build(s, plan)
            return r, (landing_state(s) if r.ok else None)
        try:
            result, state = run(f"landing build {label(key)}", build, 900)
        finally:
            left = run(f"landing build {label(key)}: closed", W.quit_in(folder))
        ok_ = result.ok and state is not None and not state["in_error"]
        say(f"fact    landing build {label(key)}: the plan's checks {checks}; built ok {result.ok}, failures "
            f"{list(result.failures)}; {state}; left open {left}")
        check(not left, f"landing build {label(key)}: closed, nothing of it left open")
        if ok_:
            built[key] = (path, state["volume"])

    def source(gear, module, teeth):
        name = LANDING_MASTER_FILES.get((gear, module, teeth))
        if name:
            return os.path.join(master, name)
        got = built.get((gear, module, teeth))
        return got[0] if got else None

    def stamp(path):
        st = os.stat(path)
        return st.st_mtime_ns, st.st_size

    import w9c_probes as P
    P.ENUMS.clear()
    enums = P.swconst(RING_ENUMS + ("swSketchSegments_e", "swConstraintType_e"))
    out["cases"] = {}
    straight_outcomes = []
    for case_id, gear, before, after, how, said, via, group in LANDING_CASES:
        b_spec, a_spec = landing_spec(gear, *before, rb), landing_spec(gear, *after, rb)
        landing, way, fraction = landing_foresight(b_spec, a_spec)
        head = (f"landing {case_id} ({how}, group {group}): {gear} m{before[0]} {before[1]} -> m{after[0]} {after[1]}; "
                f"foreseen at {'%.4f' % fraction if fraction is not None else None} of the line's length "
                f"({'a landing' if landing else 'no landing'}{f', by way of {way}' if way else ''})")
        src = source(gear, *before)
        target = built.get((gear, *after))
        if src is None:
            say(f"fact    {head}: not run, its start did not build")
            out["cases"][case_id] = {"run": False}
            continue
        folder = os.path.join(root, case_id)
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, os.path.basename(src))
        shutil.copy2(src, path)
        before_stamp = stamp(path)
        try:
            variables = landing_variables(a_spec)
            if how == "user-error":
                work = user_error_job(path, variables)
            else:
                line = (short_line(b_spec), short_line(a_spec)) if how == "straight" else None
                work = landing_case_job(path, variables, how == "straight", line=line, enums=enums)
            got = run(f"landing {case_id}", work, 900)
        finally:
            left = run(f"landing {case_id}: closed unsaved", W.quit_in(folder))
        saved = stamp(path) != before_stamp
        clean = got["rebuilt"] and not got["in_error"] and not got["failures"]
        vol, ref = got.get("volume"), (target[1] if target else None)
        rel = abs(vol - ref) / ref if vol is not None and ref else None
        got.update({"foreseen": fraction, "planned_via": via, "target_volume": ref, "volume_rel": rel, "left": left,
                    "saved": saved, "clean": clean})
        out["cases"][case_id] = got
        say(f"fact    {head}: by_way_of {got['by_way_of']}, landing {got['landing']}; rebuilds {got['rebuilds']}; "
            f"rebuilt {got['rebuilt']}, failures {got['failures']}; in error {got['in_error']}; teeth {got['teeth']}; "
            f"volume {vol} against {ref} built from scratch (relative {rel}); left open {left}, saved {saved}")
        check(not left and not saved, f"landing {case_id}: closed without saving, nothing left open")
        check(got["steps_restored"], f"landing {case_id}: swbuild.LANDING_STEPS as it was after the case")
        arc_links = [n for n in got.get("links", []) if n.split("@", 1)[0] in swbuild.ARC_RECIPE_DIMENSIONS]
        if gear == "ringB" or case_id == "ring-55-54":
            say(f"fact    landing {case_id}: the dimension links among the equations as the app reads them "
                f"{got.get('links')}; of recipe B's ({list(swbuild.ARC_RECIPE_DIMENSIONS)}) {arc_links or 'none'}")
        if got.get("line"):
            ln = got["line"]
            say(f"fact    landing {case_id}: the short solved line in Tooth Space Sketch "
                + (f"(segment #{ln.get('index')}): before {ln.get('before')}, after {ln.get('after')}; the maths put it "
                   f"at {ln.get('expected')}; its solved end {ln.get('end_off_mm')} mm from there, past the origin "
                   f"{ln.get('far_side')}" if ln.get("found") else "not found by its ends (recipe B draws none)"))
        if how == "user-error":
            mine = [n for n, _ in got.get("in_error_before", [])]
            after_names = [n for n, _ in got["in_error"]]
            say(f"fact    landing {case_id}: the user's {USER_CUT} made at Ø{USER_CUT_MADE_D:g}, rebuilt "
                f"{got.get('made_rebuilt')}, in error then {got.get('made_in_error')}; its diameter linked to "
                f"Ø{USER_CUT_D:g} by the user's equation, rebuilt {got.get('linked_rebuilt')}, its sketch's dimensions "
                f"{got.get('user_cut_dims')}; in error before the set {got.get('in_error_before')}")
            check(not got.get("made_in_error"), f"landing {case_id}: the user's {USER_CUT} made clean at "
                  f"Ø{USER_CUT_MADE_D:g} ({got.get('made_in_error')}), before its equation puts it in error")
            check(mine == [USER_CUT] and after_names == [USER_CUT] and got["by_way_of"] == (TEETH_NAME, str(via))
                  and len(got["rebuilds"]) == 2 and got["teeth"] is not None and abs(got["teeth"] - after[1]) < 1e-9
                  and not got["failures"],
                  f"landing {case_id} (the review's M1): with the user's own feature in error, routed by way of {via} "
                  f"(both legs: rebuilds {got['rebuilds']}), ends at {after[1]} teeth ({got['teeth']}), Tooth Space and "
                  f"Teeth clean, the user's feature the only one in error before ({mine}) and after ({after_names})")
        elif how == "routed" and via is not None and before[1] == after[1]:
            check(clean and got["by_way_of"] == (TEETH_NAME, str(via)) and bool(got["landing"])
                  and got["rebuilds"] == [True, True] and rel is not None and rel <= LANDING_VOLUME_TOL
                  and got["teeth"] is not None and abs(got["teeth"] - after[1]) < 1e-9
                  and got.get("module") is not None and abs(got["module"] - float(after[0])) < 1e-9
                  and TEETH_NAME not in got["changed"] and TEETH_NAME in got["unchanged"],
                  f"landing {case_id}: a module-only landing routed by way of {via} and back, both rebuilds true, no "
                  f"feature in error, {after[1]} teeth and module {got.get('module')}, the volume within "
                  f"{LANDING_VOLUME_TOL:g} of the from-scratch build's, the count reported unchanged (changed "
                  f"{got['changed']}, unchanged {got['unchanged']})")
        elif how == "routed" and via is not None:
            check(clean and got["by_way_of"] == (TEETH_NAME, str(via)) and bool(got["landing"])
                  and got["rebuilds"] == [True, True] and rel is not None and rel <= LANDING_VOLUME_TOL
                  and got["teeth"] is not None and abs(got["teeth"] - after[1]) < 1e-9,
                  f"landing {case_id}: routed by way of {via} as foreseen, both rebuilds true, no feature in error, "
                  f"{after[1]} teeth, the volume within {LANDING_VOLUME_TOL:g} of the from-scratch build's")
        elif how == "routed":
            held_to = case_id not in LANDING_NO_TARGET
            check(clean and got["by_way_of"] == () and not got["landing"] and got["rebuilds"] == [True]
                  and (not held_to or (rel is not None and rel <= LANDING_VOLUME_TOL)),
                  f"landing {case_id}: nothing foreseen, set straight with one rebuild, no feature in error"
                  + (f", the volume within {LANDING_VOLUME_TOL:g} of the from-scratch build's" if held_to
                     else " (no target built)"))
        else:
            straight_outcomes.append((case_id, round(fraction, 4) if fraction is not None else None, clean,
                                      [c for _, c in got["in_error"]]))
        if case_id == LANDING_LEFTOVER:
            say(f"-- landing  the leftover: {case_id}'s file, closed without saving after the set, reopened")

            def reopened(s, path=path):
                s.open_document(path)
                return landing_state(s)
            try:
                again = run(f"landing {case_id}: reopened", reopened, 600)
            finally:
                left = run(f"landing {case_id}: reopened, closed", W.quit_in(folder))
            ref55 = built.get(("fixture", "1.25", 55))
            rel55 = (abs(again["volume"] - ref55[1]) / ref55[1]) if again.get("volume") is not None and ref55 else None
            again.update({"left": left, "saved": stamp(path) != before_stamp, "volume_rel_55": rel55,
                          "clean": not again["in_error"] and again["teeth"] == 55.0})
            out["leftover"] = again
            say(f"fact    landing leftover: reopened, in error {again['in_error']}, teeth {again['teeth']}, volume "
                f"{again.get('volume')} against 55 built from scratch (relative {rel55}); left open {left}, saved "
                f"{again['saved']}")
            check(not left and not again["saved"], "landing leftover: closed without saving, nothing left open")
    say(f"fact    landing: set straight (the threshold's facts: case, the foresight's fraction, clean, codes in error): "
        f"{straight_outcomes}")
    cases = out["cases"]
    routed_ok = all(cases.get(c[0], {}).get("clean") and cases[c[0]].get("by_way_of") == (TEETH_NAME, str(c[6]))
                    for c in LANDING_CASES if c[4] == "routed" and c[6] is not None)
    plain_ok = all(cases.get(c[0], {}).get("clean") and cases[c[0]].get("by_way_of") == ()
                   for c in LANDING_CASES if c[4] == "routed" and c[6] is None)
    leftover_ok = bool((out.get("leftover") or {}).get("clean"))
    out["shown"] = routed_ok and plain_ok and leftover_ok
    say(f"fact    landing: the fix is {'shown' if out['shown'] else 'NOT shown'}: every foreseen change routed clean "
        f"as foreseen {routed_ok}; every unforeseen one set straight clean {plain_ok}; the straight failure's file "
        f"clean at 55 when reopened {leftover_ok}")


def with_gear_spec(spec, gid, **changes):
    return dataclasses.replace(spec, gears=tuple(dataclasses.replace(g, **changes) if g.id == gid else g
                                                 for g in spec.gears))


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
        facts = {"suppressed": out.get("suppressed"), "on_again": out.get("unsuppressed"), "clean": clean,
                 "route": "Session.suppress_feature('Relief', True/False) on the part, called by the script, not by an "
                          "Update (no legal edit takes bands off RangeBox_Fixed in place)"}
        RESULT["proposal"][f"{finding_name(GATES['relief'][0])}_facts"] = facts
        proposed(finding_name(GATES["relief"][0]), None,
                 f"bands-off: not measured through Update (no legal edit reaches it); the call the worker makes, made "
                 f"script-side on the copy's sleeve, read clean {clean}: the relief suppressed and on again, no second "
                 "relief, RangeSlv's mates in no error in every mode. Its facts are in the JSON under _facts")


# -- m4: the external-references read, a probe ------------------------------------------------------------------------

M4_CALLS = ("IComponent2.ListExternalFileReferencesCount() and ListExternalFileReferences2(9 out arrays) on the "
            "component; IModelDocExtension.ListExternalFileReferencesCount() and ListExternalFileReferences(9 out "
            "arrays) on its part (the installed API help's documented forms; the macro database's ledger lists "
            "ListExternalFileReferences on IModelDoc2 and ListExternalFileReferences2 on IFeature as 'Unverified', "
            "the rest has no entry); ISldWorks.GetDocumentDependencies2(path, False, True, False) ('Verified' in the "
            "ledger for a closed file's references), with the assembly's own as its positive control")


def outs(kinds):
    """By-reference out arguments for late binding: ``v`` a VARIANT, ``i`` a long, ``s`` a string."""
    import pythoncom
    from win32com.client import VARIANT
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
    """``call``, and a member late binding hands back uncalled (a bound method) called."""
    value = call(obj, name, *args)
    return swcom._guarded(name, value) if type(value).__name__ == "method" else value  # noqa: SLF001


def listed(obj, member_name, kinds):
    holders = outs(kinds)
    back = call(obj, member_name, *holders)
    return {"returned": plain(back), "outs": [plain(h) for h in holders]}


def m4_read(folder, targets, asm):
    """Each of ``targets`` (component Name2s) read by every candidate, GetSaveFlag of the copy's documents around each;
    the assembly's dependencies as the control. A candidate that raises is its exact error."""
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


M4_PART = A._arg("--m4-part")  # noqa: SLF001  (a part the user made with an in-context reference to an app gear)


def m4_part_read(path):
    """The candidates that read a part's own document, on a part the user made, read-only: its dependencies first
    (``GetDocumentDependencies2``, closed), then the part opened by ``OpenDoc6(path, part, Silent | ReadOnly)`` (the
    w9c probes' route for an assembly, options 3; NEW for a part) unless it was open already, its
    ``IModelDocExtension`` counts and lists, its GetSaveFlag around each; closed again if this run opened it, never
    saved. Nothing of the part is logged but its file name."""
    def work(s):
        app, out = s._app, {"reads": {}}  # noqa: SLF001
        was_open = any(store.same_path(str(call(d, "GetPathName") or ""), path)
                       for d in s._open_documents())  # noqa: SLF001
        out["was_open"] = was_open

        def attempt(label, fn, doc=None):
            before = bool(call(doc, "GetSaveFlag")) if doc is not None else None
            try:
                value = fn()
            except Exception as exc:  # noqa: BLE001 - the exact error is the finding
                value = f"raised {type(exc).__name__}: {exc}"
            after = bool(call(doc, "GetSaveFlag")) if doc is not None else None
            out["reads"][label] = {"answer": value, "marked": bool(after and not before)}
        if not was_open:
            attempt("ISldWorks.GetDocumentDependencies2",
                    lambda: plain(member(app, "GetDocumentDependencies2", path, False, True, False)))
        errors, warnings = swcom._out_long(), swcom._out_long()  # noqa: SLF001
        got = call(app, "OpenDoc6", path, swcom.DOC_PART, 3, "", errors, warnings)
        doc = got[0] if isinstance(got, tuple) else got
        out["open"] = {"returned": doc is not None, "errors": plain(errors), "warnings": plain(warnings)}
        if doc is None:
            return out
        out["open"].update(read_only=plain(_try_member(doc, "IsOpenedReadOnly")), flag=bool(call(doc, "GetSaveFlag")))
        ext = call(doc, "Extension")
        attempt("IModelDocExtension.ListExternalFileReferencesCount",
                lambda: plain(member(ext, "ListExternalFileReferencesCount")), doc)
        attempt("IModelDocExtension.ListExternalFileReferences",
                lambda: listed(ext, "ListExternalFileReferences", "vvvvvvvis"), doc)
        out["flag_after"] = bool(call(doc, "GetSaveFlag"))
        if not was_open:
            call(app, "CloseDoc", call(doc, "GetTitle"))
            out["closed"] = True
        return out
    return work


def _try_member(obj, name):
    try:
        return member(obj, name)
    except Exception as exc:  # noqa: BLE001
        return f"unread: {type(exc).__name__}"


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
        if not M4_PART:
            proposed(references, None, "m4: no positive case could be made by proven calls, so the read is not "
                                       f"measured; C4's refusal stands. Answered without error: {clean}")
        else:
            say(f"-- m4  the part the user made with an in-context reference: {os.path.basename(M4_PART)}, read-only")
            read = out["user_part"] = run("m4: the user's part", m4_part_read(M4_PART), 600)
            for label, r in read.get("reads", {}).items():
                say(f"fact    m4 {os.path.basename(M4_PART)}: {label}: {r['answer']}; marked {r['marked']}")
            say(f"fact    m4 {os.path.basename(M4_PART)}: opened {read.get('open')}; was open {read.get('was_open')}; "
                f"closed again {read.get('closed', False)}; its flag after {read.get('flag_after')}")
            if any(r["marked"] for r in read.get("reads", {}).values()) or read.get("flag_after"):
                A.stop(f"m4: a read marked the user's part modified (§0.3)")
            route = m4_route(read.get("reads", {}), M4_PART)
            say(propose(f"EXTERNAL_REFERENCES_READ_ROUTE_{year()}", route,
                        f"m4: the first candidate whose answer names another document of the user's part "
                        f"{os.path.basename(M4_PART)} (a count above 0, or a path), read-only, marking nothing"))
            proposed(references, None, f"m4: a route found on the user's part ({route}); the finding gates the app's "
                                       "own read, which is not written yet, so it stays None until it is and is run")
    finally:
        if not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], folder, "m4")


# -- w9b-part: W9b's part section, for its step-face read on SolidWorks ------------------------------------------------


def section_w9b_part(out):
    say("== w9b-part  W9b's part section run again in this session (88 s on 2026), for its step-face read "
        "(W9B-DEMONSTRATION.md, the step faces) on SolidWorks")
    B.section_part(out)


# -- the run -------------------------------------------------------------------------------------------------------------

ORDER = ["fixed", "modes", "remove", "remake", "bands-off", "m4", "w9b-part"]   # ring and landing: by name only
SECTIONS = {"ring": section_ring, "landing": section_landing, "fixed": section_fixed, "modes": section_modes, "remove": section_remove, "remake": section_remake,
            "bands-off": section_bands_off, "m4": section_m4, "w9b-part": section_w9b_part}
FOLDERS = {"ring": ["ring"], "landing": ["landing"], "fixed": ["fixed-updated", "fixed-updated" + W.MASTER_SUFFIX], "modes": ["modes"],
           "remove": ["remove-reducer", "remove-setup"], "remake": ["remake", "remake-again"], "bands-off": ["bands-off"],
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
