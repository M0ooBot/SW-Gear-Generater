r"""F2's demonstration on SolidWorks (PLAN-PRINTED §3.3, *Done when*; F2-PROBES-REVIEW §4): Print files, on the form
and in the Workbook window, through the app's own paths. The STEP files the app writes are read back by the app's own
check and by this script's own reading of them; the documents SolidWorks holds open, their save flags and the active
document are read before and after every press; every refusal is said word for word as package C's tests pin it. The
sections, what each line bears out, the masters, the command lines and the times are in
``docs/notes-printed/F2-DEMONSTRATION.md``.

python.exe probe/f2_demonstration.py <repo src> <output folder under C:\> --pid PID [--log FILE]
                                     [--sections gates,form,workbook,refusals,userwork|all]
                                     [--user-master <W9a's setup.master>]
                                     [--printed-reducer-master <this script's f2-reducer.master>]
                                     [--redo] [--close-outlived-whats-wrong]
python probe/f2_demonstration.py --self-check     (no SolidWorks, no Excel: every judgement below on made-up readings
                                                   and on the app's own figures, each failing way shown; the strip's
                                                   form needs Tk)
python probe/f2_demonstration.py --help

Sections (each runs alone; ``workbook`` and ``refusals`` share the printed 12 : 1, built here once a run and kept as
``f2-reducer.master``, or given by ``--printed-reducer-master``; ``userwork`` needs ``--user-master``):

- ``gates``     the six F2 findings and printout.EXTENT_MEASURED read as they stand and held to the review's values (facts);
                a printed coupon built by the strip's own form, and the 12 : 1 written (not built) for the Workbook
                window; Print files pressed on both with the findings as they stand: refused by the gate in its words
                with nothing submitted, or (the gate open) the form's coupon written and the window's NO_PART; then, in
                this process only, SAVE_AS_COPY None (GATE_COPY) and STEP_EXPORT_ON_<year> None (GATE, by year), on both;
                then the job's own gate: a plan read for the other version handed to the job, refused before any
                SolidWorks call.
- ``form``      the coupon of PLAN-PRINTED §3.2 (printed spur, module 1.5, 20 teeth, face 8, bore 8, Coupon_A) built by
                the form, the user's part open behind it; the span row on the form against this script's own figure;
                the bar's line; Print files pressed twice: each press its own new folder in the Output folder's print
                folder named by its date and time, the STEP file by the app's check and by this script's reading (frame,
                schema, one closed solid, millimetres, the outer radius and the face against the gear's own figures),
                the print list, the status; the part and SolidWorks as they were (no save, every flag, the active
                document, nothing opened or closed), only SaveAs called; the first folder untouched by the second, the
                two files the same part by their vertices. Then a printed helical and a printed herringbone gear the
                same way (the herringbone's size reading a fact for the reviewer: the size check is measured on spur and
                helical gears only).
- ``workbook``  the printed 12 : 1 (W9's fixture with Printed on its Box) copied, its assembly open, its parts loaded
                only as components, the user's part active: Print files from the Workbook window's own press: every part
                written by the job's own handle with nothing opened or activated, each passing the size check, the list
                naming every part with its rows, count and span. The job's reads on parts that are not the active
                document: a global changed and saved in a part loaded only as a component (GLOBALS_DIFFER), one changed
                and left unsaved in a part open behind the user's (MODIFIED), then saved (GLOBALS_DIFFER), each put back.
                The job opening parts itself (the assembly closed): opened, written, closed. The open-beside fallback,
                STEP_EXPORT_FROM_COMPONENT patched False in this process only: each component opened beside the assembly,
                written, closed, the assembly unmarked and every component resolved after.
- ``refusals``  each refusal shown by making its state, nothing written, the words exact, the user's document active
                and untouched: on the form, a global changed and left unsaved (MODIFIED), then saved (GLOBALS_DIFFER), the
                user's keyway in the coupon (written, its size check skipped on the job's live read), a part with no
                .gear.json (NO_RECORD); in the window, on a copy of the printed 12 : 1: a component set lightweight
                (LIGHTWEIGHT), a component suppressed (the same words, which name that case), the user's keyway in
                G1's part recorded by a quiet press and the set written, G1's Bore typed in Excel (CHANGES_ON_UPDATE),
                Update SolidWorks rebuilding the keyway into error (UNSAVED_MARK), saved (FEATURE_IN_ERROR, the part
                not active); then the reducer closed and an unrelated assembly of the user's open (LIGHTWEIGHT again, a
                part simply closed), and the form pressed with that assembly active (NOT_A_PART, naming it). On the
                form, after GLOBALS_DIFFER, the value is put back by the form's own Update values, saved, and a press
                writes a folder of its own.
- ``userwork``  a copy of W9a's setup.master (RangeBox with the user's work): Print files as built (Machined, E4); then
                Printed typed on the Box sheet and one Update SolidWorks, as F1's demonstration did; Print files before
                the save (UNSAVED_MARK), then after the person's save: the five parts written, none of the user's
                components, the part holding the User Keyway (Sun) written with its size check skipped as ruled and said
                in the list; the user's components, mates and keyway as before; nothing saved, the record unchanged.

Everything W9a's script does for a run is done here by running its ``main`` with these sections (as W9b's, W9c's,
W9d's and F1's scripts do): the attach by PID and its check, the dialog watch with the What's Wrong rule per version,
keep-awake, the JSON after every section, APPDATA in the run folder, the guarded close, ``--sections`` and ``--redo``.
W9c's ``--close-outlived-whats-wrong`` (SolidWorks 2024 only) is W9c's own path, put in when the flag is given. The
strip's form is the real ``gui.GearApp`` (its own link not started); the Workbook window's press is
``WorkbookWindow.press_print`` with its ``_submit``, ``_collect_job`` and ``_finish_print``, run on W9a's Desk9. Only the
worker each hands its job to is this run's: each job runs under W9a's watch (an app job, under the What's Wrong rule),
its SolidWorks calls counted by member. No document title but the run's own is logged, no path but under the run
folder, and never a STEP file's header (its FILE_NAME holds an author and an organisation).

SolidWorks calls: none new to the repo (the note lists each with the script that made it first).
"""

import dataclasses
import hashlib
import json
import math
import os
import re
import sys
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SELF_CHECK = "--self-check" in sys.argv

if "--help" in sys.argv or "-h" in sys.argv:
    print(__doc__)
    raise SystemExit(0)

# -- what the plan and the reviews say, pinned ------------------------------------------------------------------------

# The six findings F2's probe proposed and its review (F2-PROBES-REVIEW §2) says may be set alike on both versions.
F2_NAMES = ("SAVE_AS_COPY", "STEP_EXPORT", "STEP_EXPORT_NEEDS_ACTIVE", "STEP_EXPORT_FROM_COMPONENT",
            "OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN", "PART_WINDOW_READ")
REVIEWED = {"SAVE_AS_COPY": 2, "STEP_EXPORT": True, "STEP_EXPORT_NEEDS_ACTIVE": False,
            "STEP_EXPORT_FROM_COMPONENT": True, "OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN": True, "PART_WINDOW_READ": "Visible"}
ALPHA = 20.0               # degrees: every gear here has the default pressure angle
PRINTED_CAP = 0.3          # mm: a printed gear's backlash, 0.3 x module at or under module 1 (§2.1)
EXTENT_TOL = 0.01          # mm: the outer radius and the face against the gear's (§3.1.4)
SPAN_SHOWN = 0.0005        # mm: the form and the list show the span to three places
SPAN_TOL = 1e-4            # mm: this script's span against §3.0's table and against package A's figure
SAME_POINT = 1e-4          # mm: two exports of one document hold the same vertices (the probe's GEOMETRY_TOL)
SCHEMA_PREFIXES = ("CONFIG_CONTROL_DESIGN", "AP203_CONFIGURATION_CONTROLLED_3D_DESIGN", "AUTOMOTIVE_DESIGN",
                   "AP242_MANAGED_MODEL_BASED_3D_ENGINEERING")      # AP203 (both editions), AP214, AP242 (§3.1.4)
PRESS_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}\.\d{2}\.\d{2})(?: \((\d+)\))?$")   # §3.1.3, M3
PRESS_TIME = "%Y-%m-%d %H.%M.%S"
LIST_NAME = "print list.txt"
SETTINGS_HEAD = "Settings for every part above"          # the print list's settings block opens so, once
PRESS_FREE_GB = 6.0        # GB free before userwork's copy and its Update (F1's floor: 2024's first RangeBox press)
PRESS_WAIT = 900           # s: a press's job

# The parts each section makes, as the form or the workbook names them (held to the app in the self-check).
COUPON = dict(module="1.5", teeth="20", face_width="8", bore="8")                 # §3.2, named per section
HELICAL = dict(kind="helical", module="2", teeth="20", helix_angle="15", face_width="10", bore="")   # the probe's
HERRINGBONE = dict(kind="herringbone", module="2", teeth="20", helix_angle="15", face_width="20", bore="")
# §3.0's table: (module, teeth, helix, shift, backlash) -> (k, W_n), each to 1e-4 mm.
SPAN_TABLE = (((1.5, 20, 0.0, 0.0, 0.3), (3, 11.2088)), ((1.5, 20, 0.0, 0.0, 0.45), (3, 11.0678)),
              ((1.0, 12, 0.0, 0.0, 0.3), (2, 4.3144)), ((2.0, 30, 0.0, 0.0, 0.3), (4, 21.2233)),
              ((1.5, 15, 0.0, 0.3, 0.3), (3, 11.4115)), ((1.25, 29, 0.0, 0.0, 0.3), (4, 13.1414)),
              ((1.25, 13, 0.0, 0.0, 0.3), (2, 5.4809)), ((2.0, 20, 15.0, 0.0, 0.3), (3, 15.0972)),
              ((1.5, 25, 20.0, 0.0, 0.3), (4, 15.8438)), ((2.0, 20, 30.0, 0.0, 0.3), (4, 21.2255)))
# The printed 12 : 1 (W9's fixture with Printed on its Box): gear -> (stem, module, teeth, face).
REDUCER = {"G1": ("Gear_m1.5_N17_P", 1.5, 17, 15.0), "G2": ("Gear_m1.5_N68_P", 1.5, 68, 15.0),
           "G3": ("Gear_m2_N17_P", 2.0, 17, 20.0), "G4": ("OutputGear", 2.0, 51, 20.0)}
REDUCER_BOOK = "Reducer_12to1.xlsx"
REDUCER_MASTER = "f2-reducer"
FACE_WIDTH = "Face Width"
# RangeBox's five parts (W9a's setup.master; F1's RANGEBOX_PARTS): stem -> (rows, count, the size check as ruled).
RANGEBOX = {"Gear_m1.25_N29": (("Sun",), 1, "skipped: user features"),
            "Gear_m1.25_N13": (("Planet",), 3, "checked"),
            "Ring_m1.25_N55": (("Ring",), 1, "skipped: ring"),
            "Dog_m1.25_N17": (("HighDog", "LowDog"), 2, "skipped: dog"),
            "Sleeve_m1.25_N17": (("RangeSlv",), 1, "skipped: sleeve")}
RANGEBOX_SPANS = {"Gear_m1.25_N29": (1.25, 29), "Gear_m1.25_N13": (1.25, 13)}   # §3.0's rows for Sun and Planet
INTERNAL_SPAN = "  No span: internal teeth are measured over pins, not jaws."
MACHINED_SPAN = "  Machined: its backlash is a cutter's, not a printer's; no span."
SIZE_WORDS = {"bevel": "a bevel gear", "ring": "a ring", "sleeve": "a sleeve", "dog": "a dog", "hub": "a hub",
              "user features": "your features in it",
              "not measured": "not yet shown on SolidWorks"}      # C's PRINT_SIZE_SKIPPED, held to it
# SolidWorks members a press's job may call that open, activate, close, save or write (counted while a job runs).
WATCHED = ("ActivateDoc3", "OpenDoc6", "CloseDoc", "QuitDoc", "SaveAs", "SaveAs3", "Save3", "ForceRebuild3",
           "EditRebuild3", "SetSuppression2", "GetOpenDocumentByName")


# -- package C's sentences, written out here so a change to them is seen (test_ui_text.py's REFUSALS) ----------------


def names(items):
    """C's join: A, A and B, A, B and C."""
    items = [str(i) for i in items if str(i)]
    return "".join(items) if len(items) <= 1 else ", ".join(items[:-1]) + " and " + items[-1]


def _one(items):
    return len(list(items)) == 1


def said_gate_copy():
    return "Print files waits until writing a STEP file is measured on this SolidWorks; nothing was written."


def said_gate(year, revision):
    return (f"Print files waits until writing a STEP file is measured on SolidWorks {year} ({revision}); nothing was "
            "written.")


def said_changed(then_year, then_revision, now_year, now_revision):
    return (f"SolidWorks changed since Print files was pressed ({then_year} ({then_revision}) then, {now_year} "
            f"({now_revision}) now): press it again. Nothing was written.")


def said_no_part(rows):
    one = _one(rows)
    return (f"Print files wrote nothing: {names(rows)} {'has' if one else 'have'} no part yet; build "
            f"{'it' if one else 'them'} first, then print.")


def said_unsaved(stems):
    one = _one(stems)
    return (f"Print files wrote nothing: {names(stems)} {'has' if one else 'have'} changes from Update SolidWorks that "
            f"are not saved; save {'it' if one else 'them'} in SolidWorks, then print.")


def said_values(stems):
    return (f"Print files wrote nothing: Update SolidWorks would change the values in {names(stems)}; press Update "
            "SolidWorks and save, then print.")


def said_new_revision(stems):
    return (f"Print files wrote nothing: the workbook's changes to {names(stems)} need a new revision, which Update "
            "SolidWorks cannot make; press Build again…, then print the new revision.")


def said_no_folder(shown):
    """NO_FOLDER: the folder as the app shows it (shortened to 48 characters), or none chosen."""
    if not shown:
        return "Print files wrote nothing: choose an output folder; it writes into a print folder there."
    return (f"Print files wrote nothing: the output folder {shown} does not exist; make it, or choose another, then "
            "print.")


def said_modified(stems):
    one = _one(stems)
    them = "it" if one else "them"
    return (f"Print files wrote nothing: {names(stems)} {'is' if one else 'are'} changed in SolidWorks and not saved; "
            f"save {them}, or close {them} without saving, then print.")


def said_globals(stem, name, live, recorded):
    return (f'Print files wrote nothing: in {stem}, "{name}" is {live} where its record says {recorded}; press Update '
            "values (Update SolidWorks in the Workbook window), or put it back, then print.")


def said_feature(stem, features):
    one = _one(features)
    return (f"Print files wrote nothing: in {stem}, {names(features)} {'is' if one else 'are'} in error in SolidWorks; "
            f"fix {'it' if one else 'them'} there, then print.")


def said_lightweight(stems, assembly):
    """LIGHTWEIGHT as C words it since 567773c: true of each case B's job folds into it (a lightweight or a suppressed
    component, or a part simply closed, while an assembly is open)."""
    one = _one(stems)
    opened = f"{assembly} is open" if assembly else "an assembly is open"
    return (f"Print files wrote nothing: {names(stems)} {'is' if one else 'are'} not open where Print files can reach "
            f"{'it' if one else 'them'} while {opened}: {'it' if one else 'they'} may be "
            f"{'a lightweight or suppressed component' if one else 'lightweight or suppressed components'} of it, or "
            f"simply closed; resolve {'it' if one else 'them'} there, or open "
            f"{'the part itself' if one else 'the parts themselves'}, then print again.")


def said_not_a_part(file_name=""):
    what = f", and {file_name} is not a part" if file_name else ""
    return f"Print files prints the part active in SolidWorks{what}: make a gear part active there; nothing was written."


def said_no_record(file_name):
    return (f"Print files prints a part Gear Generator built: {file_name} has no .gear.json beside it, so nothing was "
            "written.")


def said_wrote(files, folder_shown):
    if len(files) == 1:
        return f"Print files wrote {files[0]} and its print list in {folder_shown}."
    return f"Print files wrote {len(files)} STEP files and their print list in {folder_shown}."


def said_bar(stem):
    return f"Print files will write {stem}.step from the active part."


# -- the judgements: plain data in, a list of what is wrong out (empty: it holds) ------------------------------------


def file_of(path):
    return str(path).replace("/", "\\").rsplit("\\", 1)[-1]


def stem_of(path):
    base = file_of(path)
    return base.rsplit(".", 1)[0] if "." in base else base


def path_key(path):
    return str(path).replace("/", "\\").lower()


def printed_backlash(module):
    """§2.1 worked here: 0.3 x module at or under module 1, else 0.3 mm."""
    m = float(module)
    return PRINTED_CAP * m if m <= 1.0 else PRINTED_CAP


def inv(a):
    return math.tan(a) - a


def span_expected(module, teeth, helix=0.0, shift=0.0, backlash=PRINTED_CAP, alpha=ALPHA):
    """§3.0 worked here, not by the app: W_n = m_n cos a_n [(k - 0.5) pi + z inv a_t] + 2 x m_n sin a_n - j_n cos a_n,
    with the k whose contact radius sqrt(r_b^2 + (W_n cos b_b / 2)^2) lies nearest r + x m_n. Returns (k, W_n, W_t, the
    contact diameter). The contact bounds are not worked: no gear here comes near them (§3.0)."""
    m, z = float(module), int(teeth)
    an, b = math.radians(alpha), math.radians(float(helix))
    at = math.atan(math.tan(an) / math.cos(b))
    d = m * z / math.cos(b)
    rb = d * math.cos(at) / 2.0
    bb = math.asin(math.sin(b) * math.cos(an))
    target = d / 2.0 + float(shift) * m
    best = None
    for k in range(1, z):
        wn = (m * math.cos(an) * ((k - 0.5) * math.pi + z * inv(at)) + 2.0 * float(shift) * m * math.sin(an)
              - float(backlash) * math.cos(an))
        rc = math.hypot(rb, wn * math.cos(bb) / 2.0)
        if best is None or abs(rc - target) < abs(best[3] / 2.0 - target):
            best = (k, wn, wn / math.cos(bb), 2.0 * rc)
    return best


def outer_radius(module, teeth, helix=0.0, shift=0.0):
    """d_a / 2 of an external gear with the app's addendum of one module, worked here."""
    m = float(module)
    return (m * int(teeth) / math.cos(math.radians(float(helix))) + 2.0 * m * (1.0 + float(shift))) / 2.0


def span_row_judged(rows, k, w):
    """The Derived panel's rows as the form shows them ({label: value}): exactly one span row, *Span over k teeth*, its
    figure W to three places."""
    found = {label: value for label, value in rows.items() if str(label).startswith("Span over")}
    want = f"Span over {k} teeth"
    if list(found) != [want]:
        return [f"the span rows shown are {found}, not one {want!r}"]
    try:
        shown = float(found[want])
    except ValueError:
        return [f"{want} shows {found[want]!r}, not a figure"]
    return [] if abs(shown - w) <= SPAN_SHOWN else [f"{want} shows {shown}, not {w:.4f}"]


# A STEP file read as text, written here apart from printout's and the probe's readers: the statements split at each
# semicolon outside a quoted string ('' inside one reads as two strings side by side, which is the same here).
_STATEMENT = re.compile(r"(?:[^;']|'[^']*')*;")


def _entity_names(body):
    plain = re.sub(r"'[^']*'", "''", body).strip()
    if plain.startswith("("):
        return [n.upper() for n in re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(", plain[1:])]
    m = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(", plain)
    return [m.group(1).upper()] if m else []


def step_read(text):
    """What this script reads in a STEP file: its frame, FILE_SCHEMA, the solid, closed shell, open shell and surface
    model instances, every length unit (SI_UNIT prefix and name, or a conversion's name), and every VERTEX_POINT's
    coordinates in the file's unit. Nothing of the header but the schema is kept (FILE_NAME holds an author)."""
    matches = list(_STATEMENT.finditer(text or ""))
    stmts = [m.group(0)[:-1].replace("\r", "").replace("\n", "").strip() for m in matches]
    tail = (text[matches[-1].end():] if matches else (text or "")).strip()
    frame = bool(stmts) and stmts[0] == "ISO-10303-21" and stmts[-1] == "END-ISO-10303-21" and not tail
    header, data, where = [], {}, None
    for s in stmts:
        if s in ("HEADER", "DATA"):
            where = s
        elif s == "ENDSEC":
            where = None
        elif where == "HEADER":
            header.append(s)
        elif where == "DATA":
            m = re.match(r"#(\d+)\s*=\s*(.*)$", s, re.S)
            if m:
                data[int(m.group(1))] = m.group(2).strip()
    schema = ""
    for s in header:
        if s.upper().startswith("FILE_SCHEMA"):
            m = re.search(r"'([^']*)'", s)
            schema = m.group(1).strip() if m else ""
    counts, units, vertices = {}, [], []
    for body in data.values():
        found = _entity_names(body)
        for n in found:
            counts[n] = counts.get(n, 0) + 1
        if "LENGTH_UNIT" in found:
            si = re.search(r"SI_UNIT\s*\(\s*(\$|\.(\w+)\.)\s*,\s*\.(\w+)\.\s*\)", body, re.I)
            conv = re.search(r"CONVERSION_BASED_UNIT\s*\(\s*'([^']*)'", body, re.I)
            units.append(((si.group(2) + "." if si.group(2) else "") + si.group(3)).upper() if si
                         else (conv.group(1).strip().upper() if conv else "?"))
        if found == ["VERTEX_POINT"]:
            ref = re.search(r"#(\d+)\s*\)\s*$", body)
            point = data.get(int(ref.group(1)), "") if ref else ""
            p = re.match(r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(([^)]*)\)\s*\)$", point, re.I)
            if p:
                try:
                    vertices.append(tuple(float(v) for v in p.group(1).split(",")))
                except ValueError:
                    pass
    return {"frame": frame, "schema": schema, "solids": counts.get("MANIFOLD_SOLID_BREP", 0),
            "closed": counts.get("CLOSED_SHELL", 0), "open": counts.get("OPEN_SHELL", 0),
            "surface": counts.get("SHELL_BASED_SURFACE_MODEL", 0), "units": units, "vertices": vertices}


def extent_of(read):
    """(the largest radius from Z, the axial extent) of the vertices, in the file's unit; (None, None) with none."""
    points = [p for p in read["vertices"] if len(p) == 3]
    if not points:
        return None, None
    zs = [p[2] for p in points]
    return max(math.hypot(p[0], p[1]) for p in points), max(zs) - min(zs)


def step_judged(read, radius=None, face=None, tol=EXTENT_TOL):
    """A file as this script reads it: framed, an AP203, AP214 or AP242 schema, one solid in at least one closed shell,
    no open shell or surface model, every length unit millimetres (this machine's export settings), vertices read; with
    a radius and a face, the largest vertex radius and the axial extent each within the tolerance of them."""
    out = []
    if not read["frame"]:
        out.append("it is not framed ISO-10303-21; ... END-ISO-10303-21;")
    if not any(read["schema"].upper().startswith(p) for p in SCHEMA_PREFIXES):
        out.append(f"its FILE_SCHEMA {read['schema']!r} is none of AP203, AP214, AP242")
    if read["solids"] != 1 or read["closed"] < 1:
        out.append(f"{read['solids']} solid(s) and {read['closed']} closed shell(s), not one solid")
    if read["open"] or read["surface"]:
        out.append(f"{read['open']} open shell(s) and {read['surface']} surface model(s)")
    if not read["units"] or set(read["units"]) != {"MILLI.METRE"}:
        out.append(f"its length units {read['units']} are not millimetres")
    r, h = extent_of(read)
    if r is None:
        out.append("no vertex was read")
    elif radius is not None and (abs(r - radius) > tol or abs(h - face) > tol):
        out.append(f"its vertices reach radius {r:.6f} and span {h:.6f} along Z, not {radius:.6f} and {face:.6f} "
                   f"(to {tol:g})")
    return out


def same_vertices(a, b, tol=SAME_POINT):
    """Two files' vertices the same set, one to one, each coordinate within the tolerance (two exports of one document)."""
    if not a or len(a) != len(b):
        return False
    cell = tol * 10.0
    grid = {}
    for i, p in enumerate(b):
        grid.setdefault(tuple(int(math.floor(c / cell)) for c in p), []).append(i)
    used = set()
    for p in a:
        key = tuple(int(math.floor(c / cell)) for c in p)
        near = [i for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1)
                for i in grid.get((key[0] + dx, key[1] + dy, key[2] + dz), ())]
        found = next((i for i in near if i not in used and all(abs(p[j] - b[i][j]) <= tol for j in range(3))), None)
        if found is None:
            return False
        used.add(found)
    return True


def press_folder_judged(name, began, ended):
    """A press's folder named by its date and time (§3.1.3, M3; a counter when the second was taken), and that time
    the press's own (local, to the second)."""
    m = PRESS_NAME.match(name)
    if not m:
        return [f"{name!r} is not named by a date and time ({PRESS_TIME})"]
    at = time.mktime(time.strptime(m.group(1), PRESS_TIME))
    if not math.floor(began) - 1 <= at <= ended + 1:
        return [f"{name!r} is not the press's time ({time.strftime(PRESS_TIME, time.localtime(began))} to "
                f"{time.strftime(PRESS_TIME, time.localtime(ended))})"]
    return []


def new_folders_judged(before, after, want):
    """Two listings of a print folder ({press folder: {file: (size, sha256)}}): so many new press folders, and every
    earlier one as it was (nothing overwritten, nothing removed). Returns (what is wrong, the new folders)."""
    new = sorted(set(after) - set(before))
    out = []
    if len(new) != want:
        out.append(f"{len(new)} new press folder(s) {new}, not {want}")
    gone = sorted(set(before) - set(after))
    changed = sorted(n for n in before if n in after and after[n] != before[n])
    if gone or changed:
        out.append(f"earlier press folders removed {gone} or changed {changed}")
    return out, new


def docs_judged(before, after, user=None):
    """Two reads of SolidWorks' documents ({"active": title, "docs": {key: {"title", "type", "flag", "visible"}}}):
    nothing opened or closed, no title changed (a save-as renames), no save flag changed, every window as it was, the
    same document active; with the user's document's key, that document open and active after. A read of no document
    cannot show anything kept, and fails."""
    out = []
    b, a = before["docs"], after["docs"]
    if not b:
        out.append("no document was read before")
    if sorted(b) != sorted(a):
        out.append(f"opened {[a[k]['title'] for k in sorted(set(a) - set(b))]}, closed "
                   f"{[b[k]['title'] for k in sorted(set(b) - set(a))]}")
    for k in sorted(set(a) & set(b)):
        for what in ("title", "flag", "visible"):
            if b[k].get(what) != a[k].get(what):
                out.append(f"{b[k]['title']}: {what} {b[k].get(what)!r} -> {a[k].get(what)!r}")
    if before["active"] != after["active"]:
        out.append(f"the active document {before['active']!r} -> {after['active']!r}")
    if user is not None and (user not in a or a[user]["title"] != after["active"]):
        out.append(f"the user's document is not open and active after: active {after['active']!r}")
    return out


def calls_judged(calls, expected):
    """The SolidWorks members a job called (counted while it ran) against what is expected ({member: count}, None for
    any count): every WATCHED member not named called no time at all."""
    out = []
    for member in WATCHED:
        want = expected.get(member, 0)
        got = list(calls).count(member)
        if want is not None and got != want:
            out.append(f"{member} called {got} time(s), not {want}")
    return out


def list_blocks(text):
    """The print list's part blocks: {file: its lines}."""
    blocks = {}
    for chunk in text.split("\n\n"):
        lines = chunk.split("\n")
        if lines and lines[0].endswith(".step") and not lines[0].startswith(" "):
            blocks[lines[0]] = lines[1:]
    return blocks


def list_judged(text, name, expected, process="Process: Printed, 0.4 mm nozzle"):
    """print list.txt against what this script expects of it: headed by the press's name, its process line, not headed
    DO NOT PRINT, the settings said once, and a block for exactly the expected files, each with its rows and count
    (*For G2 · print 1*), its span (("span", k, W, helical) to three places, or a line), what the check read (the size
    check made, or skipped and why) and the user's features by name. Expected: {file: {rows, count, span, size,
    features}}."""
    out = []
    lines = text.split("\n")
    if not lines or lines[0] != f"Print list: {name}":
        out.append(f"the list opens {lines[0] if lines else ''!r}, not 'Print list: {name}'")
    if any(line.startswith("DO NOT PRINT") for line in lines):
        out.append("the list says DO NOT PRINT THIS SET")
    if process not in lines:
        out.append(f"the list does not say {process!r}")
    if sum(1 for line in lines if line.startswith(SETTINGS_HEAD)) != 1:
        out.append("the settings are not said exactly once")
    blocks = list_blocks(text)
    if not expected or sorted(blocks) != sorted(expected):
        out.append(f"the list's parts {sorted(blocks)} are not {sorted(expected)}")
    for file_, want in expected.items():
        got = blocks.get(file_, [])
        count = ("  For " + names(want["rows"]) + " · " if want["rows"] else "  ") + f"print {want['count']}"
        if count not in got:
            out.append(f"{file_}: no line {count!r}")
        span = want["span"]
        if isinstance(span, tuple):
            _, k, w, helical = span
            lead = f"  Span over {k} teeth: "
            tail = (" mm across the teeth (the calipers tilted with them, at mid-face)." if helical
                    else " mm (the calipers square to the axis, at mid-face).")
            line = next((x for x in got if x.startswith(lead)), None)
            shown = None
            if line is not None and line.endswith(tail):
                try:
                    shown = float(line[len(lead):-len(tail)])
                except ValueError:
                    shown = None
            if shown is None or abs(shown - w) > SPAN_SHOWN:
                out.append(f"{file_}: its span line is {line!r}, not over {k} teeth {w:.4f}")
        elif span is not None and span not in got:
            out.append(f"{file_}: no line {span!r}")
        size = want["size"]
        tail = ("; outer diameter and face width match the gear." if size == "checked"
                else f"; size not checked ({SIZE_WORDS.get(size.split(': ', 1)[-1], size)}).")
        checked = next((x for x in got if x.startswith("  Checked: one closed solid")), None)
        if checked is None or not checked.endswith(tail):
            out.append(f"{file_}: its check line is {checked!r}, not ending {tail!r}")
        said = [x for x in got if x.startswith("  Your features left in it:")]
        line = f"  Your features left in it: {names(want.get('features') or ())}."
        if (said != [line]) if want.get("features") else said:
            out.append(f"{file_}: the user's features said {said}, not {[line] if want.get('features') else 'none'}")
    return out


def finding_name(name, year):
    return name if name == "SAVE_AS_COPY" else f"{name}_ON_{year}"


def standing_of(module, year):
    """The six findings as a findings module holds them for that year."""
    return {n: getattr(module, finding_name(n, year), None) for n in F2_NAMES}


def findings_judged(values):
    """The findings as they stand against the review's values (type and value: True is not 1)."""
    out = []
    for name, want in REVIEWED.items():
        got = values.get(name)
        if type(got) is not type(want) or got != want:
            out.append(f"{name} is {got!r}, not the reviewed {want!r}")
    return out


def gate_expected(values, version, year):
    """The gate of F2-INTERFACES §3, worked here: (code, detail) it refuses with, or None when a press goes on."""
    if values.get("SAVE_AS_COPY") is None:
        return ("GATE_COPY", {})
    if not version:
        return ("GATE", {})
    if values.get("STEP_EXPORT") is not True:
        return ("GATE", {"year": str(year), "revision": ".".join(str(n) for n in version)})
    return None


def gate_said(expected):
    code, detail = expected
    if code == "GATE_COPY":
        return said_gate_copy()
    if not detail:
        return "Print files needs SolidWorks running and connected; nothing was written."
    return said_gate(detail["year"], detail["revision"])


def copies_of(spec, row):
    """How many of a Gears row's gear stand in the gearbox, worked here: its shaft's Copies, else 1."""
    gear = next((g for g in spec.gears if g.id == row), None)
    shaft = next((s for s in spec.shafts if gear is not None and s.id == gear.shaft), None)
    text = str(getattr(shaft, "copies", "") or "").strip()
    return int(float(text)) if text else 1


def herringbone_judged(reach, along, radius, face, tol=EXTENT_TOL):
    """The herringbone's verdict (F2-PROBES-REVIEW §2): its vertices' largest radius and axial extent against d_a / 2
    and the face, to the size check's tolerance; what does not hold, or nothing."""
    if reach is None or along is None:
        return ["no vertex was read"]
    out = []
    if abs(reach - radius) > tol:
        out.append(f"radius {reach:.6f} against {radius:.6f}")
    if abs(along - face) > tol:
        out.append(f"along Z {along:.6f} against {face:.6f}")
    return out


def resolved_judged(states, components):
    """Components' states as read ({Name2: GetSuppression2}) against the assembly's own: exactly those components, each
    resolved (2). A read of none, or of other components, fails."""
    if not states or not components or set(states) != set(components):
        return [f"the components read {sorted(states or {})} are not the assembly's {sorted(components)}"]
    return [f"{n} reads {v}, not resolved (2)" for n, v in sorted(states.items()) if v != 2]


def stem_lists_judged(what, got, want):
    """Two lists of names the same, none missing, none more, and not empty."""
    if not want or sorted(got) != sorted(want):
        return [f"{what}: {sorted(got)}, not {sorted(want)}"]
    return []



# -- the strip's own form and the presses' worker (shared by the self-check and the live run) ---------------------------


class Answered:
    """A job's answer, ready: what the form's _collect_build and the window's _collect_job poll."""

    def __init__(self, value, error):
        self._answer = (value, error)

    def poll(self):
        return self._answer


class Strand:
    """The strip's worker as Print files hands its job over (submit): the job runs at once through the runner (in the
    live run, on this run's worker under W9a's watch as an app job, its SolidWorks calls counted by member), and its
    answer is handed back ready, for the form's own _collect_build or the window's own _collect_job to finish. Every
    job is kept: its value, its raise and its calls."""

    def __init__(self, runner):
        self.runner, self.jobs = runner, []

    def submit(self, fn):
        value, error, calls = self.runner(fn)
        self.jobs.append({"value": value, "error": error, "calls": list(calls)})
        return Answered(value, error)


def _no_link(self):
    """GearApp._start_link replaced for this run: the form's own worker would attach to the newest SolidWorks, a
    second driver; this run's worker runs the form's jobs."""


def make_form(root, strand):
    from gear_generator import gui
    gui.GearApp._start_link = _no_link
    app = gui.GearApp(root)
    app._worker = strand  # noqa: SLF001 - the press's worker: this run's, by the Strand
    return app


def form_gear(app, folder, name, fields):
    """The form as a person sets it for one printed gear (Single gear, Printed, the kind, the fields typed, the Name),
    worked out by its own _derive_now: (spec, derived)."""
    from gear_generator.spec import MODE_SINGLE, PROCESS_PRINTED
    app.mode.set(MODE_SINGLE)
    app._on_mode_changed()  # noqa: SLF001
    app.out_folder.set(folder)
    app.process.set(PROCESS_PRINTED)
    app.kind.set(fields.get("kind", "spur"))
    app._on_kind_changed()  # noqa: SLF001
    for attr in ("module", "teeth", "face_width", "bore", "helix_angle"):
        if attr in fields:
            app.gear_vars["a"][attr].set(fields[attr])
    app.gear_vars["a"]["name"].set(name)
    app._derive_now()  # noqa: SLF001
    return app._gear_spec("a"), app._derived["a"]  # noqa: SLF001


def shown_rows(app):
    """The Derived panel's rows as the form draws them, read from its own labels: {label: the first gear's value}."""
    cells = {}
    for widget in app.derived_rows.grid_slaves():
        try:
            text = widget.cget("text")
        except Exception:  # noqa: BLE001 - an entry field, not a label
            continue
        info = widget.grid_info()
        cells[(int(info["row"]), int(info["column"]))] = text
    return {text: cells.get((row, 1), "") for (row, column), text in cells.items() if column == 0 and row > 0}


def form_press(app, strand, snapshot):
    """Print files pressed on the strip's form, the bar having read the snapshot (the strip's own _read_snapshot of
    the session): the form's own _print_files and, the job having answered, its own _collect_build. What the bar and
    the status said, the job (None when nothing was submitted), and the press's start and end."""
    app._snapshot = snapshot  # noqa: SLF001
    app._derive_now()  # noqa: SLF001
    bar, shown = app.print_line.get(), bool(app.print_label.winfo_manager())
    jobs, began = len(strand.jobs), time.time()
    app._print_files()  # noqa: SLF001
    if app._pending_build is not None:  # noqa: SLF001
        app._collect_build()  # noqa: SLF001
    ended = time.time()
    job = strand.jobs[-1] if len(strand.jobs) > jobs else None
    return {"bar": bar, "bar_shown": shown, "status": app.status.get(), "job": job, "began": began, "ended": ended}


# The Workbook window's methods DeskP runs as themselves (its press and what the press reaches). The self-check holds
# what they read on the window and on its strip to what DeskP, W9a's Desk9 and W8's Desk give, each read from its source
# (DeskP is not importable off Windows), so a read the window comes to make that the stand-in lacks is seen before a run.
WINDOW_PRESS = ("press_print", "_submit", "_collect_job", "_finish_print", "_worker_free", "_foreign_record", "_folder")


def _class_body(path, name):
    src = open(path, encoding="utf-8").read()
    m = re.search(r"\nclass " + name + r"\b[\s\S]*?(?=\n\S)", src)
    return m.group(0) if m else ""


def desk_provides(bodies=None):
    """What DeskP gives the window's press, read from the sources of DeskP (here), W9a's Desk9 and W8's Desk: their
    methods and class attributes, every self.x assigned, and on the strip every self.app.x assigned (Desk9's strip
    holds recent). (on itself, on its strip, the window's methods DeskP binds)."""
    if bodies is None:
        bodies = [_class_body(os.path.abspath(__file__), "DeskP"),
                  _class_body(os.path.join(HERE, "w9a_demonstration.py"), "Desk9"),
                  _class_body(os.path.join(HERE, "workbook_assembly_check.py"), "Desk")]
    own, app, bound = set(), {"recent"}, set()
    for body in bodies:
        own |= set(re.findall(r"\n    def (\w+)\(", body)) | set(re.findall(r"\n    (\w+) = ", body))
        own |= set(re.findall(r"self\.(\w+)\s*=(?!=)", body))
        for targets in re.findall(r"\n\s+((?:self\.\w+\s*,\s*)+self\.\w+)\s*=(?!=)", body):
            own |= set(re.findall(r"self\.(\w+)", targets))
        app |= set(re.findall(r"self\.app\.(\w+)\s*=(?!=)", body))
        bound |= {a for a, b in re.findall(r"\n    (\w+) = _WINDOW\.(\w+)", body) if a == b}
    return own, app, bound


def window_reads():
    """What the window's press reads on itself and on its strip, from workbook_gui.py's source: (self.x, self.app.x)."""
    src = open(os.path.join(REPO, "src", "gear_generator", "workbook_gui.py"), encoding="utf-8").read()
    own, app = set(), set()
    for name in WINDOW_PRESS:
        m = re.search(r"\n    def " + name + r"\(self[\s\S]*?(?=\n    def |\n\S)", src)
        body = m.group(0) if m else ""
        own |= set(re.findall(r"self\.(\w+)", body))
        app |= set(re.findall(r"self\.app\.(\w+)", body)) | set(re.findall(r"getattr\(self\.app, \"(\w+)\"", body))
    return own, app



# -- --self-check -------------------------------------------------------------------------------------------------------


def made_step(radius=16.5, face=8.0, schema="CONFIG_CONTROL_DESIGN { 1 0 10303 203 1 1 4 }", solids=1, closed=1,
              open_shells=0, surface=0, unit="( LENGTH_UNIT ( ) NAMED_UNIT ( * ) SI_UNIT ( .MILLI., .METRE. ) )",
              frame=True, vertices=True):
    """A made-up STEP file of the shape SolidWorks writes, for the self-check: vertices on the outer radius at both
    faces and on a bore, a quoted name holding a semicolon and a doubled quote."""
    lines = ["ISO-10303-21;", "HEADER;", "FILE_DESCRIPTION (( 'SolidWorks' ), '2;1' );",
             "FILE_NAME ('X.STEP', '2026-11-18T10:00:00', ( 'A;B' ), ( 'it''s' ), 'SwSTEP 2.0', 'SolidWorks', '' );",
             f"FILE_SCHEMA (( '{schema}' ));", "ENDSEC;", "DATA;"]
    number = [10]

    def add(body):
        number[0] += 1
        lines.append(f"#{number[0]} = {body} ;")
        return number[0]
    unit_ref = add(unit)
    add(f"( GEOMETRIC_REPRESENTATION_CONTEXT ( 3 ) GLOBAL_UNIT_ASSIGNED_CONTEXT ( ( #{unit_ref} ) ) "
        "REPRESENTATION_CONTEXT ( 'NONE', 'WORKASPACE' ) )")
    add("PRODUCT ( 'it''s; a name', 'x', '', ( #1 ) )")
    if vertices:
        for x, y, z in ((radius, 0.0, 0.0), (0.0, radius, face), (-4.0, 0.0, 0.0), (0.0, -4.0, face)):
            p = add(f"CARTESIAN_POINT ( 'NONE',  ( {x:.12f}, {y:.12f}, {z:.12f} ) )")
            add(f"VERTEX_POINT ( 'NONE', #{p} )")
    for _ in range(closed):
        add("CLOSED_SHELL ( 'NONE', ( #1 ) )")
    for _ in range(solids):
        add("MANIFOLD_SOLID_BREP ( 'Part', #1 )")
    for _ in range(open_shells):
        add("OPEN_SHELL ( 'NONE', ( #1 ) )")
    for _ in range(surface):
        add("SHELL_BASED_SURFACE_MODEL ( 'NONE', ( #1 ) )")
    lines += ["ENDSEC;"] + (["END-ISO-10303-21;"] if frame else [])
    return "\n".join(lines) + "\n"


def self_check():
    import shutil
    import tempfile
    scratch = tempfile.mkdtemp(prefix="f2-self-check-")
    os.environ["APPDATA"] = scratch            # the strip reads its Recent list from here, never the user's
    sys.path.insert(0, os.path.join(REPO, "src"))
    bad = []

    def ok(cond, what):
        print(("ok      " if cond else "FAIL    ") + what)
        if not cond:
            bad.append(what)

    try:
        _self_check(ok, scratch)
    except Exception as exc:  # noqa: BLE001 - a fault of the self-check is a failure, said
        import traceback
        ok(False, f"the self-check raised {type(exc).__name__}: {exc}")
        traceback.print_exc()
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print(f"done    {len(bad)} failed")
    return 0 if not bad else 1


class patched:
    """Findings (or printout's EXTENT_MEASURED) set in this process only, put back after: the self-check's states, and
    the live gates section's (said in its log)."""

    def __init__(self, module, values, say=None):
        self.module, self.values, self.say, self.kept = module, dict(values), say, {}

    def __enter__(self):
        for name, value in self.values.items():
            self.kept[name] = getattr(self.module, name, None)
            setattr(self.module, name, value)
        if self.say:
            self.say(f"patch   in this process only: {self.values} (as committed: {self.kept})")
        return self

    def __exit__(self, *exc):
        for name, value in self.kept.items():
            setattr(self.module, name, value)
        if self.say:
            self.say(f"patch   put back: {self.kept}")
        return False


def _self_check(ok, scratch):
    from gear_generator import findings, printout as po, store, ui_text
    from gear_generator.gears import kind_for, span as spans
    from gear_generator.spec import GearSpec

    # 1. C's sentences, as this script writes them out, against C's own code.
    R = po.Refusal
    stems4 = [v[0] for v in REDUCER.values()]
    pairs = [
        (R(po.GATE_COPY), said_gate_copy()),
        (R(po.GATE, (), {"year": "2024", "revision": "32.5.0"}), said_gate("2024", "32.5.0")),
        (R(po.GATE, (), {"year": "2026", "revision": "34.1.1", "planned_year": "2024", "planned_revision": "32.5.0"}),
         said_changed("2024", "32.5.0", "2026", "34.1.1")),
        (R(po.NO_PART, ("G1",), {"G1": "no part"}), said_no_part(["G1"])),
        (R(po.NO_PART, tuple(REDUCER), {g: "no part" for g in REDUCER}), said_no_part(list(REDUCER))),
        (R(po.UNSAVED_MARK, ("Gear_m1.5_N17_P",)), said_unsaved(["Gear_m1.5_N17_P"])),
        (R(po.UNSAVED_MARK, tuple(RANGEBOX)), said_unsaved(list(RANGEBOX))),
        (R(po.CHANGES_ON_UPDATE, ("Gear_m1.5_N17_P",), {"Gear_m1.5_N17_P": "values"}), said_values(["Gear_m1.5_N17_P"])),
        (R(po.MODIFIED, ("Gear_m1.5_N17_P",)), said_modified(["Gear_m1.5_N17_P"])),
        (R(po.NEW_REVISION, ("OutputGear",), {"OutputGear": "new part"}), said_new_revision(["OutputGear"])),
        (R(po.NEW_REVISION, ("A", "B"), {"A": "values", "B": "new part"}), said_new_revision(["A", "B"])),
        (R(po.NO_FOLDER, (), {"folder": ""}), said_no_folder("")),
        (R(po.NO_FOLDER, (), {"folder": "C:\\Gears\\Out"}), said_no_folder("C:\\Gears\\Out")),
        (R(po.GLOBALS_DIFFER, ("Coupon_R",), {"name": FACE_WIDTH, "live": "9", "recorded": "8"}),
         said_globals("Coupon_R", FACE_WIDTH, "9", "8")),
        (R(po.FEATURE_IN_ERROR, ("Gear_m1.5_N17_P",), {"Gear_m1.5_N17_P": "User Keyway"}),
         said_feature("Gear_m1.5_N17_P", ["User Keyway"])),
        (R(po.FEATURE_IN_ERROR, ("Gear_m1.5_N17_P",), {"Gear_m1.5_N17_P": "User Keyway, User Keyway Sketch"}),
         said_feature("Gear_m1.5_N17_P", ["User Keyway", "User Keyway Sketch"])),
        (R(po.LIGHTWEIGHT, ("OutputGear",), {"OutputGear": "Reducer_12to1.SLDASM"}),
         said_lightweight(["OutputGear"], "Reducer_12to1")),
        (R(po.LIGHTWEIGHT, tuple(stems4), {s: "Pair_m1.5_25T_50T.SLDASM" for s in stems4}),
         said_lightweight(stems4, "Pair_m1.5_25T_50T")),
        (R(po.LIGHTWEIGHT, ("A", "B"), {"A": "", "B": ""}), said_lightweight(["A", "B"], "")),
        (R(po.NOT_A_PART, ("Pair_m1.5_25T_50T.SLDASM",)), said_not_a_part("Pair_m1.5_25T_50T.SLDASM")),
        (R(po.NOT_A_PART), said_not_a_part()),
        (R(po.NO_RECORD, ("Sprocket.SLDPRT",)), said_no_record("Sprocket.SLDPRT")),
    ]
    wrong = [(r.code, ui_text.print_refusal(r), s) for r, s in pairs if ui_text.print_refusal(r) != s]
    ok(not wrong, f"words: this script's {len(pairs)} refusal sentences are C's own (print_refusal), singular and "
                  f"plural: {wrong or 'the same'}")
    folder = "C:\\Users\\x\\Documents\\GearGeneratorProbe\\f2-demo-sw2026-20261118-000000\\out\\form\\print\\2026-11-18 10.05.12"
    listed = ({"list_path": folder + "\\" + LIST_NAME}
              if "list_path" in {f.name for f in dataclasses.fields(po.PrintResult)} else {})
    one = po.PrintResult(written=(("C:\\a\\Coupon_A.SLDPRT", folder + "\\Coupon_A.step"),), folder=folder,
                         active_restored=True, **listed)
    four = po.PrintResult(written=tuple((f"C:\\a\\{s}.SLDPRT", f"{folder}\\{s}.step") for s in stems4), folder=folder,
                          active_restored=True, **listed)
    shown = ui_text.short_path(folder, 64)
    ok(ui_text.print_result(one) == said_wrote(["Coupon_A.step"], shown)
       and ui_text.print_result(four) == said_wrote([s + ".step" for s in stems4], shown),
       f"words: the status after a clean press is C's (print_result), one file and four, the folder as shown: "
       f"{ui_text.print_result(one)!r}")
    refused = po.PrintResult(refusal=R(po.MODIFIED, ("X",)), active_restored=True)
    ok(ui_text.print_result(refused) == said_modified(["X"]),
       "words: a refusal in the job is said by print_result in the refusal's own words, nothing added")
    coupon_part = po.print_part("C:\\a\\Coupon_A.SLDPRT", GearSpec(process="printed", name="Coupon_A", **COUPON).to_dict())
    ok(ui_text.print_bar_line(po.PrintPlan(None, (coupon_part,), folder="F")) == said_bar("Coupon_A"),
       f"words: the bar's line is C's: {said_bar('Coupon_A')!r}")
    ok(SIZE_WORDS == getattr(ui_text, "PRINT_SIZE_SKIPPED", None) and set(SIZE_WORDS) == set(po.EXTENT_SKIPPED),
       "words: why a size check was skipped, as the list says it, is C's PRINT_SIZE_SKIPPED for every reason of "
       "printout.EXTENT_SKIPPED")

    # 2. The span: §3.0's table worked here, and package A's figures.
    off = []
    for (m, z, b, x, j), (k, w) in SPAN_TABLE:
        got = span_expected(m, z, b, x, j)
        if got[0] != k or abs(got[1] - w) > SPAN_TOL:
            off.append(((m, z, b, x, j), got[:2], (k, w)))
    ok(not off, f"span: this script's W_n and k hold every row of §3.0's table to {SPAN_TOL:g} mm: {off or 'all 10'}")
    gears = {"coupon": GearSpec(process="printed", **COUPON),
             "helical": GearSpec(process="printed", **HELICAL),
             "herringbone": GearSpec(process="printed", **HERRINGBONE)}
    gears.update({g: GearSpec(module=str(m), teeth=str(z), face_width=str(f), process="printed")
                  for g, (_, m, z, f) in REDUCER.items()})
    gears.update({s: GearSpec(module=str(m), teeth=str(z), process="printed") for s, (m, z) in RANGEBOX_SPANS.items()})
    off = []
    for label, spec in gears.items():
        kind = kind_for(spec)
        derived = kind.derive(spec)
        a = spans.span(derived, kind.recipe_for(spec))
        mine = span_expected(spec.module, spec.teeth, float(spec.helix_angle or 0) if spec.kind != "spur" else 0.0,
                             backlash=printed_backlash(spec.module))
        if a.kind != "span" or a.k != mine[0] or abs(a.w_mm - mine[1]) > SPAN_TOL or abs(a.w_t_mm - mine[2]) > SPAN_TOL:
            off.append((label, (a.kind, a.k, a.w_mm), mine[:3]))
        r = outer_radius(spec.module, spec.teeth, float(spec.helix_angle or 0) if spec.kind != "spur" else 0.0)
        if abs(derived.da / 2.0 - r) > 1e-9:
            off.append((label, "d_a / 2", derived.da / 2.0, r))
    ok(not off, f"span and size: package A's span and the app's d_a / 2 agree with this script's on the coupon, the "
                f"helical, the herringbone, the four parts of the 12 : 1 and RangeBox's Sun and Planet: {off or 'all'}")
    k, w = span_expected(1.5, 20)[:2]
    ok(span_row_judged({"Tooth at pitch": "2.2", "Span over 3 teeth": "11.209"}, k, w) == []
       and span_row_judged({"Span over 4 teeth": "11.209"}, k, w) != []
       and span_row_judged({"Span over 3 teeth": "11.21"}, k, w) != []
       and span_row_judged({"Tooth at pitch": "2.2"}, k, w) != []
       and span_row_judged({"Span over 3 teeth": "11.209", "Span over k teeth": "x"}, k, w) != []
       and span_row_judged({"Span over 3 teeth": "—"}, k, w) != [],
       "span row: 11.209 over 3 holds; another k, 0.001 off, no row, two rows and no figure each fail")

    # 3. The STEP reader, on made-up files of each kind, against printout's own reader on the same texts.
    good = made_step()
    ok(step_judged(step_read(good), 16.5, 8.0) == [] and extent_of(step_read(good)) == (16.5, 8.0)
       and step_read(good)["schema"].startswith("CONFIG_CONTROL_DESIGN"),
       "step: a framed AP203 file of one solid in millimetres, its vertices at radius 16.5 over 8 mm, holds (a ';' and "
       "a doubled quote inside names read through)")
    faults = {"frame cut": made_step(frame=False), "AP209": made_step(schema="STRUCTURAL_ANALYSIS_DESIGN { 1 }"),
              "two solids": made_step(solids=2), "no closed shell": made_step(closed=0),
              "an open shell": made_step(open_shells=1), "a surface model": made_step(surface=1),
              "inches": made_step(unit="( CONVERSION_BASED_UNIT ( 'INCH', #9 ) LENGTH_UNIT ( ) NAMED_UNIT ( #8 ) )"),
              "radius 0.02 over": made_step(radius=16.52), "face 0.02 short": made_step(face=7.98),
              "no vertex": made_step(vertices=False)}
    held = [f for f, text in faults.items() if not step_judged(step_read(text), 16.5, 8.0)]
    ok(not held, f"step: each fault fails alone ({', '.join(faults)}): held {held or 'none'}")
    with patched(findings, {"EXTENT_MEASURED": True}):
        app_good = po.check_step(good, coupon_part)
        app_bad = {f: po.check_step(t, coupon_part) for f, t in faults.items() if f not in ("inches",)}
    ok(app_good is None and all(v is not None for v in app_bad.values()),
       f"step: printout's own check agrees on the same texts (passes the good file, refuses each fault but inches, "
       f"which the app reads and this script, expecting millimetres, does not): {app_bad}")

    # 4. Two exports of one document: the same vertices.
    pts = [(16.5 * math.cos(i / 7.0), 16.5 * math.sin(i / 7.0), (i % 2) * 8.0) for i in range(60)]
    noisy = [(x + 1e-6, y - 1e-6, z) for x, y, z in reversed(pts)]
    moved = pts[:-1] + [(pts[-1][0] + 1e-3, pts[-1][1], pts[-1][2])]
    ok(same_vertices(pts, noisy) and not same_vertices(pts, moved) and not same_vertices(pts, pts[:-1])
       and not same_vertices([], []),
       "vertices: the same set reordered within 1e-6 holds; one point 1e-3 off, one fewer, and none each fail")

    # 5. The press's folder.
    now = time.time()
    name = time.strftime(PRESS_TIME, time.localtime(now))
    ok(press_folder_judged(name, now, now + 2) == [] and press_folder_judged(name + " (2)", now, now + 2) == []
       and press_folder_judged("2026-11-18 10-05-12", now, now) != []
       and press_folder_judged(time.strftime(PRESS_TIME, time.localtime(now - 3600)), now, now + 2) != [],
       "folder: named by the press's own time (with a counter too) holds; another format and an hour off fail")
    a = {"x": {"a.step": (1, "h")}}
    ok(new_folders_judged(a, dict(a, y={"b": 1}), 1) == ([], ["y"]) and new_folders_judged(a, a, 1)[0]
       and new_folders_judged(a, dict(a, y={}, z={}), 1)[0] and new_folders_judged(a, {"x": {"a.step": (2, "h")},
                                                                                        "y": {}}, 1)[0]
       and new_folders_judged(a, {"y": {}}, 1)[0],
       "folder: one new press folder holds; none, two, an earlier one changed and one removed each fail")

    # 6. SolidWorks' documents before and after, and the calls a job made.
    d0 = {"active": "Housing.SLDPRT", "docs": {
        "h": {"title": "Housing.SLDPRT", "type": 1, "flag": False, "visible": True},
        "g": {"title": "Gear_m1.5_N17_P.SLDPRT", "type": 1, "flag": False, "visible": False}}}

    def changed(**edit):
        out = json.loads(json.dumps(d0))
        for key, (what, value) in edit.items():
            if key == "active":
                out["active"] = value
            elif what is None:
                out["docs"].pop(key)
            else:
                out["docs"].setdefault(key, dict(out["docs"]["g"]))[what] = value
        return out
    ok(docs_judged(d0, json.loads(json.dumps(d0)), "h") == []
       and docs_judged(d0, changed(active=(None, "Gear_m1.5_N17_P.SLDPRT")), "h") != []
       and docs_judged(d0, changed(g=("flag", True))) != [] and docs_judged(d0, changed(n=("title", "New"))) != []
       and docs_judged(d0, changed(g=(None, None))) != [] and docs_judged(d0, changed(g=("title", "Other"))) != []
       and docs_judged(d0, changed(g=("visible", True))) != []
       and docs_judged({"active": None, "docs": {}}, {"active": None, "docs": {}}) != []
       and docs_judged(d0, changed(h=(None, None), active=(None, None)), "h") != [],
       "documents: the same read holds; the active one changed, a flag turned on, one opened, one closed, one renamed, "
       "a window shown, an empty read and the user's document gone each fail")
    ok(calls_judged(["SaveAs"] * 4, {"SaveAs": 4}) == [] and calls_judged(["SaveAs"] * 4 + ["ActivateDoc3"],
                                                                          {"SaveAs": 4}) != []
       and calls_judged(["SaveAs"] * 4 + ["OpenDoc6"], {"SaveAs": 4}) != []
       and calls_judged(["SaveAs"] * 3, {"SaveAs": 4}) != [] and calls_judged(["SaveAs3"], {}) != []
       and calls_judged(["SaveAs"], {}) != [] and calls_judged(["ActivateDoc3"] * 5, {"ActivateDoc3": None}) == [],
       "calls: four SaveAs alone hold; an activation, an open, one SaveAs short, a SaveAs3, a SaveAs in a refusal each "
       "fail; a member allowed any count is not held")

    # 7. The print list, as C's code writes it for B's plans.
    plan = po.PrintPlan(None, (coupon_part,), folder=folder, revision=(34, 1, 1), name="Coupon_A", pressed=now)
    facts = {"Coupon_A.step|schema": "CONFIG_CONTROL_DESIGN", "Coupon_A.step|unit": "MILLI.METRE",
             "Coupon_A.step|extent": "checked"}
    result = po.PrintResult(written=((coupon_part.path, folder + "\\Coupon_A.step"),), folder=folder, facts=facts,
                            active_restored=True)
    text = ui_text.print_list_text(plan, result, "0.9")
    k, w = span_expected(1.5, 20)[:2]
    want = {"Coupon_A.step": {"rows": (), "count": 1, "span": ("span", k, w, False), "size": "checked"}}
    ok(list_judged(text, "Coupon_A", want) == [], f"list: C's list of one coupon holds: {list_judged(text, 'Coupon_A', want)}")
    failed = po.PrintResult(written=result.written, folder=folder, failed=((folder + "\\Coupon_A.step", po.SOLIDS),),
                            refusal=R(po.FILE_CHECK, ("Coupon_A",), {"file": "Coupon_A.step", "reason": po.SOLIDS}),
                            facts=facts, active_restored=True)
    ok(list_judged(text, "Coupon_A", dict(want, **{"X.step": want["Coupon_A.step"]})) != []
       and list_judged(text, "Coupon_A", {"Coupon_A.step": dict(want["Coupon_A.step"], count=2)}) != []
       and list_judged(text, "Coupon_A", {"Coupon_A.step": dict(want["Coupon_A.step"],
                                                                span=("span", k, w + 0.002, False))}) != []
       and list_judged(text, "Coupon_A", {"Coupon_A.step": dict(want["Coupon_A.step"], size="skipped: dog")}) != []
       and list_judged(text, "Coupon_A", {"Coupon_A.step": dict(want["Coupon_A.step"], features=("User Keyway",))}) != []
       and list_judged(ui_text.print_list_text(plan, failed, "0.9"), "Coupon_A", want) != []
       and list_judged(text, "Coupon_B", want) != [] and list_judged(text, "Coupon_A", {}) != []
       and list_judged(text + "\n" + text, "Coupon_A", want) != []
       and list_judged(ui_text.print_list_text(plan, dataclasses.replace(result, live_features=(
           (coupon_part.path, ("User Keyway",)),)), "0.9"), "Coupon_A", want) != []
       and list_judged(ui_text.print_list_text(plan, dataclasses.replace(result, live_features=(
           (coupon_part.path, ("User Keyway",)),)), "0.9"), "Coupon_A",
           {"Coupon_A.step": dict(want["Coupon_A.step"], features=("User Keyway",), size="checked")}) == [],
       "list: a part missing, a count off, the span 0.002 off, the size check said otherwise, a feature not named, a "
       "set headed DO NOT PRINT, another name, nothing expected and the settings twice each fail")

    ok(herringbone_judged(22.7055, 20.0, 22.70552, 20.0) == [] and herringbone_judged(22.72, 20.0, 22.70552, 20.0) != []
       and herringbone_judged(22.7055, 19.98, 22.70552, 20.0) != [] and herringbone_judged(None, None, 22.7, 20.0) != [],
       "herringbone: the size reading holds within 0.01 mm; the radius off, the face off and no vertex each give a "
       "verdict that it does not")
    comps = {"Gear_m1.5_N17_P-1", "OutputGear-1", "Reducer_12to1_Layout-1"}
    ok(resolved_judged({c: 2 for c in comps}, comps) == [] and resolved_judged({}, comps) != []
       and resolved_judged(None, comps) != [] and resolved_judged(dict({c: 2 for c in comps}, **{"OutputGear-1": 1}),
                                                                  comps) != []
       and resolved_judged({"Other-1": 2}, comps) != [] and resolved_judged({c: 2 for c in comps}, set()) != [],
       "components: the assembly's own components each resolved holds; none read, a read of other components, one "
       "lightweight and nothing expected each fail")
    ring = GearSpec(module="1.25", teeth="55", teeth_side="internal", process="printed")
    sun = GearSpec(module="1.25", teeth="29")
    mplan = po.PrintPlan(None, (po.print_part("C:\\a\\Gear_m1.25_N29.SLDPRT", sun.to_dict(), rows=("Sun",),
                                              user_features=("User Keyway",)),), folder="F", name="RangeBox", pressed=now)
    mres = po.PrintResult(written=(("C:\\a\\Gear_m1.25_N29.SLDPRT", "F\\Gear_m1.25_N29.step"),), folder="F",
                          facts={"Gear_m1.25_N29.step|extent": "skipped: user features"}, active_restored=True,
                          live_features=(("C:\\a\\Gear_m1.25_N29.SLDPRT", ("User Keyway",)),))
    mwant = {"Gear_m1.25_N29.step": {"rows": ("Sun",), "count": 1, "span": MACHINED_SPAN, "size": "skipped: user features",
                                     "features": ("User Keyway",)}}
    rplan2 = po.PrintPlan(None, (po.print_part("C:\\a\\Ring.SLDPRT", ring.to_dict(), rows=("Ring",)),), folder="F",
                          name="RangeBox", pressed=now)
    rres = po.PrintResult(written=(("C:\\a\\Ring.SLDPRT", "F\\Ring.step"),), folder="F",
                          facts={"Ring.step|extent": "skipped: ring"}, active_restored=True)
    rwant = {"Ring.step": {"rows": ("Ring",), "count": 1, "span": INTERNAL_SPAN, "size": "skipped: ring"}}
    mtext = ui_text.print_list_text(mplan, mres, "0.9")
    ok(list_judged(mtext, "RangeBox", mwant, process="Process: Machined") == []
       and list_judged(ui_text.print_list_text(rplan2, rres, "0.9"), "RangeBox", rwant) == []
       and list_judged(mtext, "RangeBox", mwant) != [],
       f"list: C's list of a machined part (Process: Machined, no span, the user's feature named) and of a printed ring "
       f"(over pins) holds as userwork expects it; the machined list read as printed fails: "
       f"{list_judged(mtext, 'RangeBox', mwant, process='Process: Machined')}")

    # 8. The findings and the gate.
    ok(findings_judged(REVIEWED) == [] and all(findings_judged(dict(REVIEWED, **{n: None})) for n in REVIEWED)
       and findings_judged(dict(REVIEWED, STEP_EXPORT=1)) != []
       and findings_judged(dict(REVIEWED, PART_WINDOW_READ="IModelDoc2.Visible, True for a document open in its own "
                                                          "window")) != [],
       "findings: the review's six hold; each one unset, a 1 for True and the probe's prose for Visible each fail")
    agree = []
    for copy, export in ((None, None), (2, None), (2, True), (None, True)):
        values = dict(REVIEWED, SAVE_AS_COPY=copy, STEP_EXPORT=export)
        with patched(findings, {"SAVE_AS_COPY": copy, "STEP_EXPORT_ON_2026": export}):
            for version in ((34, 1, 1), ()):
                got = po.gate(version)
                mine = gate_expected(values, version, 2026)
                agree.append((got is None and mine is None) or (got is not None and mine is not None and
                                                                (got.code, dict(got.detail)) == mine
                                                                and ui_text.print_refusal(got) == gate_said(mine)))
    ok(all(agree) and len(agree) == 8, f"gate: this script's reading of the gate is printout.gate's, code, detail and "
                                       f"words, for both findings unset, one, both set, and none connected: {agree}")

    # 9. The 12 : 1 printed, and RangeBox's parts as the window plans them (W9's record of RangeBox, on the fake).
    from gear_generator.workbook import assess, link, model, update, xlsx
    made = link.Link(os.path.join(REPO, "tests", "fixtures", "excel-windows", REDUCER_BOOK)).read().spec
    printed = spec_printed_reducer(made, "")
    a = assess.assess(printed, [], "C:\\Out\\")
    jobs = {j.gear_ids[0]: (j.stem, j.spec.process) for j in a.parts.jobs}
    ok(not [d for d in a.diagnostics if d.is_error] and printed.box.process == "printed"
       and jobs == {g: (s, "printed") for g, (s, _, _, _) in REDUCER.items()},
       f"reducer: W9's 12 : 1 with Printed on its Box plans the four parts named here, each printed: {jobs}")
    fixtures = os.path.join(REPO, "tests", "fixtures", "printed")
    with open(os.path.join(fixtures, "RangeBox_W9_record.json"), encoding="utf-8") as handle:
        snap = json.load(handle)
    files, sidecars = set(snap["files"]), dict(snap["sidecars"])
    record = store.link_record_from_json(snap["record"])
    spec, _ = model.from_book(xlsx.read(os.path.join(fixtures, "RangeBox_W9.xlsx")))
    spec = dataclasses.replace(spec, source_path=snap["workbook"])
    rb = assess.assess(spec, [], "C:\\Out\\", blank_process=assess.blank_process(record))
    up = update.classify(record, rb, exists=lambda p: path_key(p) in files,
                         read_sidecar=lambda p: store.from_json(sidecars[path_key(p)]) if path_key(p) in sidecars else None)
    with patched(findings, {"SAVE_AS_COPY": 2, "STEP_EXPORT_ON_2026": True}):
        rplan = po.workbook_print(record, rb, up, "C:\\Out", (34, 1, 1), now=now, exists=lambda p: path_key(p) in files,
                                  isdir=lambda p: True)
    got = {p.stem: (p.rows, p.count) for p in rplan.parts}
    mine = {stem_of(e.path): (tuple(r for r in [g.id for g in spec.gears] if r in e.gears),
                              sum(copies_of(spec, r) for r in e.gears)) for e in record.current_parts()}
    ok(rplan.refusal is None and got == {s: (r, c) for s, (r, c, _) in RANGEBOX.items()} == mine,
       f"rangebox: the window's planner, on W9's record as built, plans the five parts with the rows and counts named "
       f"here, and so does this script's count from the Shafts' Copies: {got}")
    with patched(findings, {"EXTENT_MEASURED": True}):
        why = {p.stem: (po.extent_skipped(p) or "checked") for p in rplan.parts}
    ok({s: ("checked" if w == "checked" else "skipped: " + w) for s, w in why.items()}
       == {s: v for s, (_, _, v) in RANGEBOX.items()} and bool(dict((p.stem, p.user_features) for p in rplan.parts)[
           "Gear_m1.25_N29"]),
       f"rangebox: the size check as ruled (Sun holds a feature of the user's on record; a ring, a dog and a sleeve skipped; the "
       f"Planet checked) is printout's own: {why}; the user's features on record {[(p.stem, p.user_features) for p in rplan.parts if p.user_features]}")

    # 10. The window's press, read as source: what it reads on itself and on its strip is what DeskP gives it.
    own, app_reads = window_reads()
    has, has_app, bound = desk_provides()
    from gear_generator import workbook_gui
    ok(own and has and set(own) <= has and set(app_reads) <= has_app and set(WINDOW_PRESS) <= bound
       and all(hasattr(workbook_gui.WorkbookWindow, n) for n in WINDOW_PRESS),
       f"window: every attribute the window's press reads on itself ({len(own)}) and on its strip ({sorted(app_reads)}) "
       f"DeskP, Desk9 or W8's Desk gives, read from their sources, and DeskP binds the seven methods themselves: "
       f"missing {sorted(set(own) - has)} {sorted(set(app_reads) - has_app)} {sorted(set(WINDOW_PRESS) - bound)}")
    bare, bare_app, bare_bound = desk_provides([_class_body(os.path.join(HERE, "w9a_demonstration.py"), "Desk9"),
                                                _class_body(os.path.join(HERE, "workbook_assembly_check.py"), "Desk")])
    ok(not set(own) <= bare and not set(app_reads) <= bare_app and not set(WINDOW_PRESS) <= bare_bound,
       f"window: without DeskP's own body the check fails (Desk9 and W8's Desk lack {sorted(set(own) - bare)} and on "
       f"the strip {sorted(set(app_reads) - bare_app)})")

    _self_check_form(ok, scratch)


def _self_check_form(ok, scratch):
    """The strip's own form, as the live sections press it, with the gate patched each way and a job answered here."""
    from gear_generator import findings, printout as po, ui_text
    try:
        import tkinter as tk
        root = tk.Tk()
    except Exception as exc:  # noqa: BLE001 - said: the live sections need the form, so its check is a failure
        ok(False, f"form: the strip's form cannot be made here ({type(exc).__name__}: {exc}); the live sections need "
                  "Tk, as python.exe on Windows has it")
        return
    root.withdraw()
    answers = []
    strand = Strand(lambda fn: answers.pop(0))
    try:
        app = make_form(root, strand)
        folder = os.path.join(scratch, "form")
        os.makedirs(folder)
        spec, derived = form_gear(app, folder, "Coupon_A", COUPON)
        k, w = span_expected(1.5, 20)[:2]
        ok(spec.stem() == "Coupon_A" and spec.is_printed() and span_row_judged(shown_rows(app), k, w) == [],
           f"form: the coupon on the form is Coupon_A, printed, its span row drawn as {shown_rows(app).get('Span over 3 teeth')}")
        context = app._plan_single(folder)  # noqa: SLF001
        path = context["paths"][0]
        fake = types.SimpleNamespace(saved=path, trig="degrees", features=[], dimensions={}, manual=[])
        note, sidecar, _ = app._write_sidecar(spec, derived, context["plans"][0], fake)  # noqa: SLF001
        ok(sidecar is not None, f"form: the form's own _write_sidecar wrote the coupon's record ({note or 'no note'})")
        snapshot = {"key": (1, "Coupon_A.SLDPRT", path), "version": "SolidWorks 2026", "newer_than_tested": False,
                    "title": "Coupon_A.SLDPRT", "path": path, "doc_type": 1, "is_part": True, "revision": (34, 1, 1)}
        with patched(findings, {"SAVE_AS_COPY": None}):
            seen = form_press(app, strand, snapshot)
        ok(seen["status"] == said_gate_copy() and seen["job"] is None and not seen["bar_shown"],
           f"form: with SAVE_AS_COPY None the press says GATE_COPY's words, submits nothing, and the bar says nothing: "
           f"{seen['status']!r}")
        with patched(findings, {"SAVE_AS_COPY": 2, "STEP_EXPORT_ON_2026": None}):
            seen = form_press(app, strand, snapshot)
        ok(seen["status"] == said_gate("2026", "34.1.1") and seen["job"] is None,
           f"form: with STEP_EXPORT_ON_2026 None the press says GATE's words by year, submits nothing: {seen['status']!r}")
        with patched(findings, {"SAVE_AS_COPY": 2, "STEP_EXPORT_ON_2026": True}):
            press = os.path.join(folder, "print", "2026-11-18 10.05.12")
            os.makedirs(press)
            result = po.PrintResult(written=((path, os.path.join(press, "Coupon_A.step")),), folder=press,
                                    facts={"Coupon_A.step|schema": "CONFIG_CONTROL_DESIGN",
                                           "Coupon_A.step|unit": "MILLI.METRE", "Coupon_A.step|extent": "checked"},
                                    active_restored=True)
            answers.append((result, None, ["SaveAs"]))
            seen = form_press(app, strand, snapshot)
            listed = open(os.path.join(press, LIST_NAME), encoding="utf-8").read() if os.path.exists(
                os.path.join(press, LIST_NAME)) else ""
            ok(seen["bar"] == said_bar("Coupon_A") and seen["bar_shown"] and seen["job"] is not None
               and seen["status"] == said_wrote(["Coupon_A.step"], ui_text.short_path(press, 64))
               and list_judged(listed, "Coupon_A", {"Coupon_A.step": {"rows": (), "count": 1, "span": ("span", k, w, False),
                                                                      "size": "checked"}}) == [],
               f"form: the gate open, the bar names the file, the press submits one job, its answer is finished by the "
               f"form's own _collect_build: the status in C's words and the list written by the form: {seen['status']!r}")
            seen = form_press(app, strand, dict(snapshot, path=os.path.join(folder, "Sprocket.SLDPRT")))
            ok(seen["status"] == said_no_record("Sprocket.SLDPRT") and seen["job"] is None,
               f"form: a part with no .gear.json: NO_RECORD's words, nothing submitted: {seen['status']!r}")
            seen = form_press(app, strand, dict(snapshot, path=os.path.join(folder, "Pair.SLDASM"), is_part=False,
                                                doc_type=2))
            ok(seen["status"] == said_not_a_part("Pair.SLDASM") and seen["job"] is None,
               f"form: an assembly active: NOT_A_PART's words naming it, nothing submitted: {seen['status']!r}")
    finally:
        root.destroy()


def spec_printed_reducer(made, folder=""):
    """W9's 12 : 1 (the fixture W4 to W9 build) with its Output folder blank (W6-PLAN §5, so a copy stands on its own)
    and Printed on its Box sheet: the gearbox F2 prints."""
    return dataclasses.replace(made, box=dataclasses.replace(made.box, output_folder=folder, process="printed"))


if SELF_CHECK:
    raise SystemExit(self_check())



# -- the live run: W9a's harness ----------------------------------------------------------------------------------------

sys.path.insert(0, HERE)
import w9a_demonstration as A  # noqa: E402  (W8's and S0's scripts, the watch, the What's Wrong rule, Desk9, main)

W = A.W
from gear_generator import findings, gui, printout, store, swbuild, swcom, ui_text, workbook_gui  # noqa: E402
from gear_generator.gears import kind_for, plan_for  # noqa: E402
from gear_generator.gears import pair as pairs  # noqa: E402
from gear_generator.spec import MODE_PAIR, GearSpec, PairSpec, pair_stems  # noqa: E402
from gear_generator.swcom import call  # noqa: E402
from gear_generator.workbook import link as wb_link  # noqa: E402

say, check, note = W.say, W.check, W.note
OUT = W.OUT
CTX, RESULT, run, job = A.CTX, A.RESULT, A.run, A.job
WW_CLOSE_FLAG = "--close-outlived-whats-wrong"      # W9c's flag, its own path (w9c_demonstration.close_outlived_on)
PRINTED_REDUCER_MASTER = A._arg("--printed-reducer-master")  # noqa: SLF001

# Every SolidWorks call a press's job makes, by member, while it runs (over W9a's counted call; nothing else changes).
CALLS = {"on": False, "log": []}
_PREV_CALL = swcom.call


def _press_call(obj, name, *args):
    if CALLS["on"]:
        CALLS["log"].append(name)
    return _PREV_CALL(obj, name, *args)


swcom.call = _press_call


def press_runner(fn):
    """A press's job on this run's worker, watched by W9a's watched_wait as an app job (the What's Wrong rule applying),
    its SolidWorks calls counted by member: (value, raise, calls). A hung worker or a STOP is not caught here."""
    CALLS.update(on=True, log=[])
    try:
        value, error = A.watched_wait(CTX["worker"].submit(fn), PRESS_WAIT, "Print files", app_job=True)
    finally:
        CALLS["on"] = False
    calls = list(CALLS["log"])
    say(f"        the job's calls by member {dict((m, calls.count(m)) for m in sorted(set(calls)))}")
    return value, error, calls


def year():
    return swcom.release_year(W.TAG["major"])


def revision():
    return tuple(W.TAG["revision"])


def dotted(version):
    return ".".join(str(n) for n in version)


def extent_on():
    """Whether the app makes the size check: findings.EXTENT_MEASURED (printout's own constant before ae42722)."""
    return getattr(findings, "EXTENT_MEASURED", getattr(printout, "EXTENT_MEASURED", None)) is True


def standing():
    return standing_of(findings, year())


def require_findings(section):
    """The export sections measure the press as the reviewed findings set it: with the gate shut, or a finding not the
    review's value, the section ends here, said (the gates section shows the findings as they stand)."""
    values = standing()
    gate = gate_expected(values, revision(), year())
    wrong = findings_judged(values)
    say(f"findings {section}: {values}; EXTENT_MEASURED {extent_on()}; document route {swcom.DOCUMENT_BY_PATH_ROUTE!r}")
    if gate is not None or wrong:
        A.section_stop(f"{section}: the F2 findings as they stand are not the reviewed ones ({wrong or gate_said(gate)}); "
                       "this section measures Print files as the review's values set it (the gates section shows "
                       "them as they stand)")


def extent_want(plain=True):
    """The size-check fact the app should give a printed or machined external spur or helical gear with nothing of the
    user's in it: checked, while EXTENT_MEASURED is True."""
    return "checked" if extent_on() else "skipped: not measured"


# -- what SolidWorks holds, read without changing anything ------------------------------------------------------------


def label_of(path, title):
    """A document's name for the log: its title when the run made it, else <user document N> (W8's open_titles)."""
    if W.ours(path):
        return title
    return W.USERS.setdefault(path or title, f"<user document {len(W.USERS) + 1}>")


def docs_now(s):
    """Every open document (its title, type, save flag and Visible: whether it has a window of its own) and the active
    one, read by the walk; nothing activated or set."""
    app = s._app  # noqa: SLF001
    out = {}
    for d in W.documents(app):
        path, title = str(call(d, "GetPathName") or ""), str(call(d, "GetTitle"))
        try:
            visible = bool(swcom._read(d, "Visible"))  # noqa: SLF001
        except Exception:  # noqa: BLE001 - unread is said as None, never taken as either
            visible = None
        name = label_of(path, title)
        out[path_key(path) if path else name] = {"title": name, "type": int(swcom._read(d, "GetType")),  # noqa: SLF001
                                                 "flag": bool(call(d, "GetSaveFlag")), "visible": visible}
    active = call(app, "ActiveDoc")
    return {"active": None if active is None else label_of(str(call(active, "GetPathName") or ""),
                                                           str(call(active, "GetTitle"))), "docs": out}


def docs(label):
    return run(f"{label}: SolidWorks' documents read", docs_now)


def sha(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def sw_files(*folders):
    """Every .SLDPRT and .SLDASM of the folders: size, mtime and sha256 (a save shows in all three)."""
    out = {}
    for folder in folders:
        for name in sorted(os.listdir(folder)):
            path = os.path.join(folder, name)
            if os.path.isfile(path) and name.lower().endswith((".sldprt", ".sldasm")):
                out[path_key(path)] = (os.path.getsize(path), os.stat(path).st_mtime_ns, sha(path))
    return out


def prints_of(folder):
    """The Output folder's print folder: {press folder: {file: (size, sha256)}}."""
    root = os.path.join(folder, printout.PRINT_FOLDER)
    if not os.path.isdir(root):
        return {}
    out = {}
    for name in sorted(os.listdir(root)):
        where = os.path.join(root, name)
        if os.path.isdir(where):
            out[name] = {f: (os.path.getsize(os.path.join(where, f)), sha(os.path.join(where, f)))
                         for f in sorted(os.listdir(where))}
    return out


def open_doc(label, path):
    """A document opened as the app opens one (Session.open_document: OpenDoc6, then ActivateDoc3), as a person
    opens it; its title."""
    def work(s):
        s.begin_build()
        try:
            return s.open_document(path).title
        finally:
            s.end_build()
    return run(label, work)


def activate(label, path):
    """The person brings an open document to the front (ActivateDoc3, the app's Session.activate); read back."""
    def work(s):
        doc = next((d for d in W.documents(s._app)  # noqa: SLF001
                    if store.same_path(str(call(d, "GetPathName") or ""), path)), None)
        if doc is None:
            return None, None
        title = str(call(doc, "GetTitle"))
        s.activate(title)
        active = call(s._app, "ActiveDoc")  # noqa: SLF001
        return title, (None if active is None else str(call(active, "GetTitle")))
    title, active = run(f"{label}: {file_of(path)} brought to the front", work)
    if title is None or active != title:
        raise AssertionError(f"{label}: {file_of(path)} could not be made the active document (open {title}, active "
                             f"{active})")
    return title


def user_document(section):
    """The user's own part (S0's Housing, built by the strip once a run: W9a's user_parts) open in its own window and
    active, as a person leaves their work; its path."""
    path = os.path.join(A.user_parts(), "Housing.SLDPRT")
    open_doc(f"{section}: the user's own part opened", path)
    activate(f"{section}: the user's own part", path)
    say(f"user    {section}: the user's own document is {file_of(path)}, open in its own window and active")
    return path


def set_global(label, path, value, save=False, close=False, name=FACE_WIDTH):
    """The person changes one global in a part in SolidWorks: the part opened in its own window and active (the app's
    open_document; a put on a document not active did not take on 2026, F2's probe run 1), the global set and the part
    rebuilt (the app's set_global_variable, read back, and rebuild); then saved as a person saves (W8's save_docs), and
    its own window closed (CloseDoc) when asked, leaving it loaded only as the open assembly's component."""
    def work(s):
        s.begin_build()
        try:
            s.open_document(path)
            s.set_global_variable(name, value)
            rebuilt = bool(s.rebuild())
            saved = W.save_docs(s, [path]) if save else []
            title = s.document_title()
            if close:
                s.close_document(title)
            return rebuilt, saved, title
        finally:
            s.end_build()
    rebuilt, saved, title = run(label, work)
    say(f"person  {label}: \"{name}\"= {value} in {title}; rebuilt {rebuilt}; saved {saved or 'nothing'}; its window "
        f"{'closed' if close else 'left open'}")
    check(rebuilt and (not save or saved == [(file_of(path), True)]), f"{label}: made as a person makes it")


def close_window(label, path):
    """A document's own window closed by CloseDoc on its title as SolidWorks gives it (read by the walk), as a person
    closes it; a part an open assembly holds stays loaded as its component."""
    def work(s):
        doc = next((d for d in W.documents(s._app)  # noqa: SLF001
                    if store.same_path(str(call(d, "GetPathName") or ""), path)), None)
        if doc is None:
            return False
        s.close_document(str(call(doc, "GetTitle")))
        return True
    check(run(label, work), f"{label}: {file_of(path)} was open and its window was closed")


def save_one(label, path):
    saved = run(label, lambda s: W.save_docs(s, [path]))
    check(saved == [(file_of(path), True)], f"{label}: {file_of(path)} saved as a person saves it: {saved}")


def open_assembly(label, asm):
    """The assembly opened as the app opens one (its parts loaded only as its components)."""
    return run(label, job(asm, lambda s: s.document_title()))


def component_states(label, asm):
    """Each top-level component's GetSuppression2 in the open assembly (Session.components), the assembly made the
    build document by use_open_document: nothing activated or set."""
    def work(s):
        if s.use_open_document(asm) is None:
            return None
        return {c.name: c.state for c in s.components()}
    got = run(label, work)
    say(f"fact    {label}: {got}")
    return got


def set_component(label, asm, name, state):
    """The person sets a component's state in the active configuration (SetSuppression2: 0 suppressed, 1 lightweight,
    2 resolved), the assembly activated as W9a's set_state does; read back."""
    def work(s):
        route = findings.COMPONENT_FIND_ROUTE
        comp = swcom.Session._component_by(route, s._doc(), name)  # noqa: SLF001
        call(comp, "SetSuppression2", state)
        comp = swcom.Session._component_by(route, s._doc(), name)  # noqa: SLF001
        return int(swcom._read(comp, "GetSuppression2"))  # noqa: SLF001
    got = run(label, job(asm, work))
    say(f"person  {label}: {name} set to {state}, reads {got}")
    return got


def features_of(label, path):
    """A part's features with their error codes (Session.feature_states), the part made the build document by
    use_open_document: nothing activated (on 2024 activating a part in error can raise What's Wrong). None when the
    part is not open."""
    def work(s):
        if s.use_open_document(path) is None:
            return None
        return [(f.name, f.code, f.warning) for f in s.feature_states()]
    return run(label, work)


def user_features_read(label, path):
    """The user's features in a part as this script reads them: the top-level features named User… (every feature of
    the user's here is W9a's keyway, "User Keyway", and its sketch where SolidWorks keeps it top-level; no app feature
    is so named), in tree order, read without activation. () when the part is not open."""
    found = features_of(label, path) or []
    return tuple(n for n, _, _ in found if str(n).startswith("User "))


def read_text(path):
    with open(path, encoding="latin-1") as handle:
        return handle.read()


# -- the presses -----------------------------------------------------------------------------------------------------


def press_form(app, strand, label):
    """Print files pressed on the strip's form, its bar having read the session (the strip's own _read_snapshot)."""
    snapshot = run(f"{label}: the strip's bar reads SolidWorks", gui._read_snapshot)  # noqa: SLF001
    seen = form_press(app, strand, snapshot)
    say(f"bar     {label}: {seen['bar']!r} ({'shown' if seen['bar_shown'] else 'not shown'})")
    say(f"status  {label}: {seen['status']}")
    return seen


_WINDOW = workbook_gui.WorkbookWindow


class DeskP(A.Desk9):
    """W9a's Desk9 with the Workbook window's own Print files: press_print, _submit, _collect_job, _finish_print,
    _worker_free, _foreign_record and _folder are WorkbookWindow's functions themselves, run here. The strip it reads is
    the stand-in Desk9 already has, given the bar's snapshot (the strip's own _read_snapshot of the session), its
    Output folder (the section's) and the worker, a Strand that hands each job to this run's worker. _plan is the
    window's planning pass (Desk9's plan_solidworks, the window's _plan_solidworks_pass); painting is not done."""

    press_print = _WINDOW.press_print
    _submit = _WINDOW._submit
    _collect_job = _WINDOW._collect_job
    _finish_print = _WINDOW._finish_print
    _worker_free = _WINDOW._worker_free
    _foreign_record = _WINDOW._foreign_record
    _folder = _WINDOW._folder

    def __init__(self, path, worker, strip=""):
        super().__init__(path, worker, strip)
        self._pending = self._job = None
        self._close_when_done = False
        self.strand = Strand(press_runner)
        self.said = []
        self.app._worker = self.strand  # noqa: SLF001
        self.app._pending_build = None  # noqa: SLF001
        self.app._snapshot = {}  # noqa: SLF001
        self.app.out_folder = types.SimpleNamespace(get=lambda: strip)

    def _plan(self):
        self.plan_solidworks()

    def _refresh_state(self):
        pass

    def _refresh_read_line(self):
        pass

    def _paint(self):
        pass

    def _set_status(self, text, ok=True):
        self.said.append((text, ok))
        say(f"status  [{'green' if ok else 'red'}] {text}")

    def _settle_journal(self):
        raise AssertionError("a build's journal was asked of a Print files press")

    def close(self):
        raise AssertionError("the window was asked to close")


def window_press(desk, label):
    """Print files pressed in the Workbook window: the window's own press_print on DeskP (planned again first, as the
    window does), the job (if any) finished by the window's own _collect_job. What it said, the job, start and end."""
    desk.app._snapshot = run(f"{label}: the strip's bar reads SolidWorks", gui._read_snapshot)  # noqa: SLF001
    folder = desk._folder(desk.reading.spec)  # noqa: SLF001
    if not (folder and (W.under(folder, OUT) or path_key(folder).rstrip("\\") == path_key(OUT))):
        A.section_stop(f"{label}: the window's Output folder {folder!r} is not under this run's folder")
    if desk.error is not None:
        say(f"fact    {label}: W8's Desk held the last job's raise where the window keeps a failed read; cleared before "
            f"the press: {desk.error}")
        desk.error = None
    desk.note, desk.said = None, []              # nothing of an earlier press can be read as this one's
    jobs, began = len(desk.strand.jobs), time.time()
    desk.press_print()
    if desk._pending is not None:  # noqa: SLF001
        desk._collect_job()  # noqa: SLF001
    ended = time.time()
    n = desk.note
    if n is not None and not isinstance(n, tuple):
        text, ok = n.text, n.ok
        desk.note = (n.text, n.ok)              # W8's Desk keeps a note as (text, ok)
    elif n is not None:
        text, ok = n
    else:
        text, ok = (desk.said[-1] if desk.said else ("", False))
    say(f"window  {label}: [{'green' if ok else 'red'}] {text}")
    return {"status": text, "ok": ok, "job": desk.strand.jobs[-1] if len(desk.strand.jobs) > jobs else None,
            "began": began, "ended": ended}


def refused(label, seen, said, before, after, prints, files, user=None, in_job=True):
    """A press refused: its words exact, no press folder made and no SolidWorks file changed, SolidWorks' documents as
    they were (the user's still active), and the job, when the refusal is the job's, calling nothing that opens,
    activates, saves or writes."""
    check(seen["status"] == said, f"{label}: said word for word: {said!r}"
          + ("" if seen["status"] == said else f" (said {seen['status']!r})"))
    made, _ = new_folders_judged(prints[0], prints[1], 0)
    changed = sorted(k for k in set(files[0]) | set(files[1]) if files[0].get(k) != files[1].get(k))
    check(not made and not changed, f"{label}: nothing written: {made or 'no press folder'}; SolidWorks files "
                                    f"{changed or 'as they were'}")
    wrong = docs_judged(before, after, user)
    check(not wrong, f"{label}: SolidWorks' documents as they were (none opened or closed, every flag and window, the "
                     f"active one): {wrong or 'the same'}")
    j = seen["job"]
    if in_job:
        value = j["value"] if j else None
        ok_ = j is not None and j["error"] is None and value is not None and not value.written and not value.folder
        wrong = calls_judged(j["calls"] if j else [], {"GetOpenDocumentByName": None})
        check(ok_ and not wrong, f"{label}: refused in the job, before any file, calling nothing that opens, activates, "
                                 f"saves or writes: {wrong or (j and j['error']) or 'as said'}")
    else:
        check(j is None, f"{label}: refused at planning, nothing submitted to SolidWorks")


def written(label, seen, folder, expect, before, after, prints, files, *, name, calls, user=None,
            process="Process: Printed, 0.4 mm nozzle"):
    """A press that wrote its set, judged whole. Expected per stem: its path, the gear's outer radius and face (None
    for no size reading of this script's), the app's size fact (None: a fact only), the list's rows, count, span and the
    user's features. The job's answer (every part written and checked by the app, nothing failed, the active document
    put back, no flag turned on); one new press folder named by the press's date and time holding the files and the
    list alone, every earlier one as it was; the status in C's words; each file by this script's reading and the app's
    facts; the list; SolidWorks' documents and files as they were; the job's calls. Returns what was read."""
    j = seen["job"]
    result = j["value"] if j else None
    if j is None or j["error"] is not None or result is None:
        check(False, f"{label}: the press wrote nothing: {seen['status']!r}; the job {j and j['error']}")
        return None
    stems = sorted(expect)
    got = sorted(stem_of(p) for p, _ in result.written)
    check(result.refusal is None and not result.failed and result.active_restored and not result.flags_turned_on
          and not stem_lists_judged("written", got, stems),
          f"{label}: every part written and checked by the app, none failed, the active document as it was, no save "
          f"flag turned on: written {got}, refusal {result.refusal}, failed {list(result.failed)}, active restored "
          f"{result.active_restored}, flags turned on {list(result.flags_turned_on)}")
    wrong, new = new_folders_judged(prints[0], prints[1], 1)
    press = new[0] if len(new) == 1 else ""
    where = os.path.join(folder, printout.PRINT_FOLDER, press)
    held = sorted(prints[1].get(press, {}))
    wrong += press_folder_judged(press, seen["began"], seen["ended"]) if press else []
    wrong += [] if held == sorted([s + ".step" for s in stems] + [LIST_NAME]) else [f"it holds {held}"]
    wrong += [] if store.same_path(result.folder, where) else [f"the job wrote into {result.folder!r}"]
    check(not wrong, f"{label}: a new folder of its own in the Output folder's print folder, named by the press's date "
                     f"and time, holding the STEP files and print list.txt alone, every earlier folder as it was: "
                     f"{press!r} {held}: {wrong or 'as said'}")
    said = said_wrote([s + ".step" for s in stems], ui_text.short_path(where, 64))
    check(seen["status"] == said, f"{label}: the status is C's: {said!r}"
          + ("" if seen["status"] == said else f" (said {seen['status']!r})"))
    reads, facts = {}, dict(result.facts)
    for stem, e in expect.items():
        file_ = stem + ".step"
        app = {w: str(facts.get(f"{file_}|{w}", "")) for w in ("schema", "unit", "extent")}
        try:
            text = read_text(os.path.join(where, file_))
        except OSError as exc:
            check(False, f"{label}: {file_} could not be read: {exc}")
            continue
        r = step_read(text)
        reach, along = extent_of(r)
        reads[stem] = {"characters": len(text), "schema": r["schema"].split(" ")[0], "units": sorted(set(r["units"])),
                       "vertices": len(r["vertices"]), "radius": reach, "along_z": along, "app": app,
                       "points": r["vertices"]}
        say(f"fact    {label}: {file_}: {len(text)} characters, schema {r['schema'].split(' ')[0]}, units "
            f"{sorted(set(r['units']))}, {len(r['vertices'])} vertices reaching radius "
            f"{'none' if reach is None else f'{reach:.6f}'} over {'none' if along is None else f'{along:.6f}'} along Z "
            f"(the gear's {e['radius']} and {e['face']}); the app read {app}")
        mine = step_judged(r, e["radius"], e["face"])
        app_wrong = ([] if app["unit"] == "MILLI.METRE" else [f"the app read the unit {app['unit']!r}"]) + (
            [] if any(app["schema"].upper().startswith(p) for p in SCHEMA_PREFIXES) else
            [f"the app read the schema {app['schema']!r}"]) + (
            [] if e["extent"] is None or app["extent"] == e["extent"] else
            [f"the app's size check {app['extent']!r}, not {e['extent']!r}"])
        check(not mine and not app_wrong,
              f"{label}: {file_} by this script's reading (framed, AP203/214/242, one closed solid, millimetres"
              f"{', the outer radius and face to 0.01 mm' if e['radius'] is not None else ''}) and by the app's check "
              f"(size {app['extent']!r}): {mine + app_wrong or 'holds'}")
    list_path = os.path.join(where, LIST_NAME)
    text = open(list_path, encoding="utf-8").read() if os.path.isfile(list_path) else ""
    want = {s + ".step": {"rows": e["rows"], "count": e["count"], "span": e["span"],
                          "size": e["extent"] if e["extent"] is not None else str(facts.get(f"{s}.step|extent", "")),
                          "features": e.get("features", ())} for s, e in expect.items()}
    wrong = list_judged(text, name, want, process)
    check(not wrong, f"{label}: print list.txt names every part with its rows, how many to print, its span, what the "
                     f"check read and the user's features, the settings once: {wrong or 'as said'}")
    wrong = docs_judged(before, after, user)
    changed = sorted(k for k in set(files[0]) | set(files[1]) if files[0].get(k) != files[1].get(k))
    check(not wrong and not changed, f"{label}: SolidWorks as it was: no document opened, closed, renamed or marked, every "
                                     f"window and the active document as they were{', the user’s active' if user else ''}"
                                     f"; no SolidWorks file saved: {wrong or 'the same'}; {changed or 'no file changed'}")
    wrong = calls_judged(j["calls"], calls)
    check(not wrong, f"{label}: the job called {dict((m, j['calls'].count(m)) for m in WATCHED if m in j['calls'])}, "
                     f"as its way of reaching each part says: {wrong or 'as expected'}")
    return {"folder": press, "where": where, "reads": reads, "list": text}


def snap_all(label, folders):
    """Before or after a press: SolidWorks' documents, the print folder, every SolidWorks file of the folders."""
    return docs(label), prints_of(folders[0]), sw_files(*folders)


# -- the strip's form, built as a person builds a gear ---------------------------------------------------------------


def tk_root():
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    return root


def form_build(label, app, folder, name, fields):
    """One printed gear built by the form's own plan, job (on this run's worker) and finish (its .gear.json); the part
    left open and made active, as the form leaves it. (spec, derived, path)."""
    spec, derived = form_gear(app, folder, name, fields)
    context = app._plan_single(folder)  # noqa: SLF001
    path = context["paths"][0]
    check(spec.is_printed() and derived is not None and not os.path.exists(path),
          f"{label}: the form plans {file_of(path)}, printed, a new file")
    result = run(f"{label}: built", context.pop("job"), 900)
    for line in result.log_lines():
        say("        " + line)
    app._finish_single(context, result)  # noqa: SLF001 - the form's own finish: the status and the .gear.json
    say(f"status  {label}: {app.status.get()}")
    check(result.ok and bool(result.saved) and os.path.isfile(store.sidecar_path(path)),
          f"{label}: built and saved by the form's job, its .gear.json written by the form: ok {result.ok}, failures "
          f"{list(result.failures)}")
    activate(label, path)
    return spec, derived, path


def span_on_form(label, app, fields):
    """The form's span row against this script's figure and package A's."""
    helix = float(fields.get("helix_angle") or 0) if fields.get("kind", "spur") != "spur" else 0.0
    k, w, wt, contact = span_expected(fields["module"], fields["teeth"], helix, backlash=printed_backlash(fields["module"]))
    rows = shown_rows(app)
    reading = app._spans["a"]  # noqa: SLF001
    wrong = span_row_judged(rows, k, w)
    agree = reading.kind == "span" and reading.k == k and abs(reading.w_mm - w) <= SPAN_TOL
    check(not wrong and agree, f"{label}: the form's Derived panel shows Span over {k} teeth "
                               f"{rows.get(f'Span over {k} teeth')!r}; this script works W {w:.4f} (W_t {wt:.4f}, the jaws "
                               f"at diameter {contact:.3f}), package A {reading.w_mm:.4f} over {reading.k}: "
                               f"{wrong or ('as said' if agree else 'A differs')}")
    return ("span", k, w, helix != 0.0)


# -- gates ------------------------------------------------------------------------------------------------------------


def section_gates(out):
    say("== gates  the six F2 findings and EXTENT_MEASURED as they stand; Print files on the form and in the Workbook "
        "window with them as they stand, then with SAVE_AS_COPY None and with STEP_EXPORT_ON_<year> None in this "
        "process only; then the job's own gate on a plan read for the other version")
    values = standing()
    out["findings"] = {k: repr(v) for k, v in values.items()}
    out["extent_measured"] = extent_on()
    for name, want in REVIEWED.items():
        got = values[name]
        say(f"finding {finding_name(name, year())} = {got!r}: "
            + ("the review's value" if type(got) is type(want) and got == want else f"NOT the review's {want!r}"))
    say(f"finding EXTENT_MEASURED = {extent_on()}; swcom.DOCUMENT_BY_PATH_ROUTE = {swcom.DOCUMENT_BY_PATH_ROUTE!r}")
    if not extent_on():
        note("gates: EXTENT_MEASURED is not True, so the app skips the size check on every part (this script's own size "
             "reading still runs)")
    expected = gate_expected(values, revision(), year())
    say(f"fact    gates: as they stand the gate {'refuses: ' + gate_said(expected) if expected else 'lets a press go on'}")
    folder = W.fresh_folder("gates")
    user = user_document("gates")
    root, strand = tk_root(), Strand(press_runner)
    book = None
    try:
        app = make_form(root, strand)
        _, _, coupon = form_build("gates: Coupon_G", app, folder, "Coupon_G", COUPON)
        made = wb_link.Link(W.FIXTURE_12).read().spec
        wfolder, _, book, _ = A.w8_step(W.write_fixture, CTX["worker"], CTX["excel"], "gates-window",
                                        lambda f: spec_printed_reducer(made, f))
        desk = DeskP(os.path.join(wfolder, REDUCER_BOOK), CTX["worker"], strip=wfolder)
        desk.read()
        check(desk.reading.spec.box.process == "printed" and desk.record is None,
              f"gates: the 12 : 1 written for the window with Printed on its Box, nothing built ({desk.reading.spec.box.process!r})")

        def presses(tag, want):
            for where, press in (("form", lambda: press_form(app, strand, f"gates, {tag}: the form")),
                                 ("window", lambda: window_press(desk, f"gates, {tag}: the window"))):
                at = folder if where == "form" else wfolder
                before = (docs(f"gates, {tag}"), prints_of(at), sw_files(folder))
                seen = press()
                after = (docs(f"gates, {tag}"), prints_of(at), sw_files(folder))
                if want is not None:
                    refused(f"gates, {tag}: the {where}", seen, gate_said(want), before[0], after[0],
                            (before[1], after[1]), (before[2], after[2]), in_job=False)
                    if where == "form":
                        check(not seen["bar_shown"], f"gates, {tag}: the bar names no file while the gate is shut")
                elif where == "window":
                    refused(f"gates, {tag}: the window (the gate open, nothing built)", seen,
                            said_no_part(list(REDUCER)), before[0], after[0], (before[1], after[1]),
                            (before[2], after[2]), in_job=False)
                else:
                    result = seen["job"]["value"] if seen["job"] else None
                    check(result is not None and result.refusal is None and len(result.written) == 1,
                          f"gates, {tag}: the gate open, the form's press wrote {[file_of(f) for _, f in result.written] if result else None} "
                          f"(the form section judges such a press whole): {seen['status']!r}")
            return True
        say("-- gates  as the findings stand")
        presses("as they stand", expected)
        say("-- gates  SAVE_AS_COPY None, in this process only")
        with patched(findings, {"SAVE_AS_COPY": None}, say=say):
            presses("SAVE_AS_COPY None", ("GATE_COPY", {}))
        say(f"-- gates  STEP_EXPORT_ON_{year()} None, SAVE_AS_COPY the review's, in this process only")
        with patched(findings, {"SAVE_AS_COPY": REVIEWED["SAVE_AS_COPY"], finding_name("STEP_EXPORT", year()): None},
                     say=say):
            presses(f"STEP_EXPORT_ON_{year()} None", ("GATE", {"year": str(year()), "revision": dotted(revision())}))
        say("-- gates  the job's own gate: the form's plan, read for the other version, handed to the job")
        other = (32, 5, 0) if year() == 2026 else (34, 1, 1)
        opened = {} if expected is None else {"SAVE_AS_COPY": REVIEWED["SAVE_AS_COPY"],
                                              finding_name("STEP_EXPORT", year()): True}
        with patched(findings, opened, say=say if opened else None):
            app._snapshot = run("gates: the strip's bar reads SolidWorks", gui._read_snapshot)  # noqa: SLF001
            plan = app._form_print_plan()  # noqa: SLF001
            check(plan.refusal is None and [p.stem for p in plan.parts] == ["Coupon_G"],
                  f"gates: the form's plan for Coupon_G, the gate {'patched open (no SolidWorks call follows)' if opened else 'open'}: {plan.refusal}")
            prints_before = prints_of(folder)
            value, error, calls = press_runner(lambda s: swbuild.print_parts(s, dataclasses.replace(plan, revision=other)))
        said = said_changed(str(swcom.release_year(other[0])), dotted(other), str(year()), dotted(revision()))
        got = ui_text.print_refusal(value.refusal) if value is not None and value.refusal is not None else repr(error)
        check(error is None and got == said and not calls and not value.written and not value.folder
              and prints_of(folder) == prints_before,
              f"gates: the job refuses a plan read for SolidWorks {dotted(other)} before any SolidWorks call, nothing "
              f"written: {got!r}; calls {calls or 'none'}")
        out["job_gate"] = got
    finally:
        root.destroy()
        if book is not None:
            book.close()
        for f in (folder, os.path.dirname(user)):
            left = run(f"gates: {os.path.basename(f)} closed", W.quit_in(f))
            check(not left, f"gates: {os.path.basename(f)}'s documents closed unsaved: left {left}")



# -- form -------------------------------------------------------------------------------------------------------------


def section_form(out):
    say("== form  §3.2's coupon (Coupon_A) built by the strip's form, the user's part open behind it; its span on the "
        "form; Print files twice; then a printed helical and a printed herringbone gear the same way")
    require_findings("form")
    folder = W.fresh_folder("form")
    user = user_document("form")
    root, strand = tk_root(), Strand(press_runner)
    try:
        app = make_form(root, strand)
        first = None
        for tag, name, fields in (("coupon", "Coupon_A", COUPON), ("helical", "", HELICAL),
                                  ("herringbone", "", HERRINGBONE)):
            label = f"form, {tag}"
            spec, derived, path = form_build(label, app, folder, name, fields)
            stem = stem_of(path)
            span = span_on_form(label, app, fields)
            helix = span[3] and float(fields["helix_angle"]) or 0.0
            radius = outer_radius(fields["module"], fields["teeth"], helix)
            face = float(fields["face_width"])
            herringbone = fields.get("kind") == "herringbone"
            expect = {stem: {"radius": None if herringbone else radius, "face": face,
                             "extent": None if herringbone else extent_want(), "rows": (), "count": 1, "span": span}}
            for press in ((1, 2) if tag == "coupon" else (1,)):
                say(f"-- form  {tag}: Print files, press {press}")
                before = snap_all(label, (folder,))
                seen = press_form(app, strand, f"{label}, press {press}")
                after = snap_all(label, (folder,))
                check(seen["bar"] == said_bar(stem) and seen["bar_shown"],
                      f"{label}: before the press the SolidWorks bar says {said_bar(stem)!r}: {seen['bar']!r}")
                j = seen["job"]
                result = j["value"] if j else None
                if herringbone and result is not None and result.refusal is not None:
                    # The size check is measured on spur and helical gears only (F2-PROBES-REVIEW §2): a herringbone the
                    # app checked and refused is a fact, held to this script's own reading of the file it left.
                    file_ = os.path.join(result.folder, stem + ".step") if result.folder else ""
                    r = step_read(read_text(file_)) if file_ and os.path.isfile(file_) else None
                    reach, along = extent_of(r) if r else (None, None)
                    say(f"fact    {label}: the app refused it: {seen['status']!r}; this script reads radius {reach} over "
                        f"{along} (the gear's {radius:.6f} and {face})")
                    off = reach is None or abs(reach - radius) > EXTENT_TOL or abs(along - face) > EXTENT_TOL
                    check(result.refusal.code == printout.FILE_CHECK and dict(result.refusal.detail).get("reason") == "EXTENT"
                          and off, f"{label}: the app's size refusal agrees with this script's reading of the file")
                    continue
                got = written(f"{label}, press {press}", seen, folder, expect, before[0], after[0],
                              (before[1], after[1]), (before[2], after[2]), name=stem,
                              calls={"SaveAs": 1, "GetOpenDocumentByName": None})
                if got is None:
                    continue
                reach = got["reads"].get(stem, {})
                out.setdefault("presses", {})[f"{tag} {press}"] = {
                    "folder": got["folder"], "app": reach.get("app"), "radius": reach.get("radius"),
                    "along_z": reach.get("along_z"), "vertices": reach.get("vertices")}
                if herringbone:
                    app_extent = reach.get("app", {}).get("extent")
                    say(f"fact    {label}: a herringbone (the size check measured on spur and helical gears only): the "
                        f"app's size check {app_extent!r}; this script reads radius {reach.get('radius')} over "
                        f"{reach.get('along_z')} along Z, against d_a / 2 {radius:.6f} and the face {face}")
                    holds = herringbone_judged(reach.get("radius"), reach.get("along_z"), radius, face)
                    out["herringbone"] = {"holds": not holds, "radius": reach.get("radius"),
                                          "along_z": reach.get("along_z"), "d_a/2": radius, "face": face,
                                          "app": app_extent}
                    note(f"{label}: the herringbone's size reading {'holds' if not holds else 'does not hold'} against "
                         f"d_a / 2 and the face to {EXTENT_TOL:g} mm ({holds or 'within'}): a fact for the ruling on "
                         "\"herringbone\" in printout.EXTENT_SKIPPED")
                    if app_extent == "checked":
                        check(not holds, f"{label}: the app checked the herringbone's size and passed it, as this "
                                         "script's reading does")
                if press == 1:
                    first = reach
                elif first is not None:
                    check(same_vertices(first.get("points"), reach.get("points")),
                          f"{label}: the second press's file is the first's part (the same {reach.get('vertices')} "
                          f"vertices, one to one, within {SAME_POINT:g} mm), in a folder of its own")
    finally:
        root.destroy()
        for f in (folder, os.path.dirname(user)):
            left = run(f"form: {os.path.basename(f)} closed", W.quit_in(f))
            check(not left, f"form: {os.path.basename(f)}'s documents closed unsaved: left {left}")


# -- the printed 12 : 1 --------------------------------------------------------------------------------------------


def printed_reducer_master():
    """The printed 12 : 1, built once a run through the app's own Build (W8's write_fixture and build_turning) and kept
    as f2-reducer.master, or given by --printed-reducer-master."""
    if PRINTED_REDUCER_MASTER:
        return PRINTED_REDUCER_MASTER
    here = os.path.join(OUT, REDUCER_MASTER + W.MASTER_SUFFIX)
    if os.path.isdir(here):
        say(f"fact    the printed 12 : 1 kept earlier in this <out> is copied: {os.path.basename(here)}")
        return here
    if os.path.exists(os.path.join(OUT, REDUCER_MASTER)):
        raise AssertionError("an earlier build of the printed 12 : 1 in this <out> kept no master; give "
                             "--printed-reducer-master or a fresh <out>")
    say("-- the printed 12 : 1 (W9's fixture with Printed on its Box) written by the app's write_new and built to turn "
        "through the app's own Build, kept as f2-reducer.master")
    made = wb_link.Link(W.FIXTURE_12).read().spec
    folder, _, _, wdesk = A.w8_step(W.write_fixture, CTX["worker"], CTX["excel"], REDUCER_MASTER,
                                    lambda f: spec_printed_reducer(made, f))
    try:
        jobs = {j.gear_ids[0]: (j.stem, j.spec.process) for j in wdesk.a.parts.jobs}
        check(wdesk.reading.spec.box.process == "printed"
              and jobs == {g: (s, "printed") for g, (s, _, _, _) in REDUCER.items()},
              f"f2-reducer: the Box reads Printed and the four parts plan printed under the names here: {jobs}")
        A.w8_step(W.build_turning, CTX["worker"], wdesk, REDUCER_MASTER, 4)
    except (AssertionError, W.Halt):
        A.w8_step(W.end_copy, CTX["worker"], folder, REDUCER_MASTER)
        raise
    kept = A.w8_step(W.keep_master, CTX["worker"], folder, REDUCER_MASTER)
    if not kept:
        raise AssertionError("the printed 12 : 1 was not kept as a master")
    return kept


def copy_deskp(master, section):
    """A copy of a kept master (W8's copy_built) read through the window's path on DeskP, its workbook open in this
    run's Excel."""
    try:
        folder = A.w8_step(W.copy_built, master, section)
    except W.CopyStop as exc:
        raise AssertionError(f"{section}: the copy of {os.path.basename(master)} stopped: {exc}") from None
    book_name = next(n for n in sorted(os.listdir(folder)) if n.lower().endswith(".xlsx") and not n.startswith("~$")
                     and os.path.exists(store.link_record_path(os.path.join(folder, n))))
    path = os.path.join(folder, book_name)
    desk = DeskP(path, CTX["worker"], strip=folder)
    desk.read()
    box = desk.record.gearbox if desk.record is not None else None
    check(W.turning(desk) and box is not None and W.under(box.assembly, folder)
          and desk.record.digest == desk.reading.digest,
          f"{section}: the copy reads as built from this workbook, its assembly in the copy")
    book = W.Workbook(CTX["excel"], path, section)
    return folder, path, book, desk


def reducer_parts(desk):
    """The record's current parts: {gear: path}, held to the names here, each printed."""
    box = desk.record.gearbox
    parts = {g: next(c.part for c in box.components if c.gear == g) for g in REDUCER}
    specs = {stem_of(e.path): dict(e.spec or {}) for e in desk.record.current_parts()}
    check(sorted(stem_of(p) for p in parts.values()) == sorted(s for s, _, _, _ in REDUCER.values())
          and all(specs.get(stem_of(p), {}).get("process") == "printed" for p in parts.values()),
          f"the record's parts are the printed 12 : 1's: {sorted(specs)}")
    return parts


def reducer_expect(desk, sizes=None, features=None):
    """What a press of the whole 12 : 1 writes, part by part, worked here: the outer radius and face of each gear, the
    size fact, the row and count (one each: no Copies), the span, the user's features."""
    parts = reducer_parts(desk)
    out = {}
    for g, (stem, m, z, face) in REDUCER.items():
        k, w = span_expected(m, z, backlash=printed_backlash(m))[:2]
        size = (sizes or {}).get(g, extent_want())
        out[stem] = {"path": parts[g], "radius": outer_radius(m, z), "face": face, "extent": size, "rows": (g,),
                     "count": 1, "span": ("span", k, w, False), "features": (features or {}).get(g, ())}
    return out


def recorded(desk, path, name=FACE_WIDTH):
    """A global's expression as the record holds it for a part."""
    entry = next(e for e in desk.record.current_parts() if store.same_path(e.path, path))
    return dict((str(n), str(v)) for n, v in entry.variables)[name]


def judged_refusal(label, desk_or_app, press, said, folders, user, in_job=True):
    before = snap_all(label, folders)
    seen = press()
    after = snap_all(label, folders)
    refused(label, seen, said, before[0], after[0], (before[1], after[1]), (before[2], after[2]), user, in_job)
    return seen


def judged_written(label, press, folders, expect, user, calls, name, process="Process: Printed, 0.4 mm nozzle"):
    before = snap_all(label, folders)
    seen = press()
    after = snap_all(label, folders)
    return written(label, seen, folders[0], expect, before[0], after[0], (before[1], after[1]), (before[2], after[2]),
                   name=name, calls=calls, user=user, process=process)


# -- workbook ---------------------------------------------------------------------------------------------------------


def section_workbook(out):
    say("== workbook  the printed 12 : 1, its assembly open and its parts loaded only as components, the user's part "
        "active: Print files from the Workbook window; the job's reads on parts not active (a component, a part behind "
        "the user's); the job opening parts itself; the open-beside fallback, its finding patched")
    require_findings("workbook")
    master = printed_reducer_master()
    folder, _, _, desk = copy_deskp(master, "workbook")
    user = None
    try:
        box = desk.record.gearbox
        asm = box.assembly
        parts = reducer_parts(desk)
        user = user_document("workbook")
        uk = path_key(user)
        folders = (folder, os.path.dirname(user))
        open_assembly("workbook: the assembly opened (its parts loaded as its components only)", asm)
        activate("workbook", user)
        now = docs("workbook: before")
        windows = {g: now["docs"].get(path_key(p), {}).get("visible") for g, p in parts.items()}
        check(all(v is False for v in windows.values()) and now["docs"].get(path_key(asm), {}).get("visible") is True
              and now["active"] == file_of(user),
              f"workbook: every part loaded only as a component (Visible False, the read PART_WINDOW_READ names): "
              f"{windows}; the assembly in its own window; the user's part active ({now['active']})")
        stems = [stem_of(e.path) for e in desk.record.current_parts()]
        name = desk.reading.spec.box.name

        def press(tag):
            return lambda: window_press(desk, f"workbook: {tag}")

        say("-- workbook  every part loaded only as a component: written by the job's own handle, nothing activated")
        got = judged_written("workbook: component-only", press("component-only"), folders, reducer_expect(desk), uk,
                             {"SaveAs": 4, "GetOpenDocumentByName": None}, name)
        components = {n for _, n in W.bodies(box)} | {box.layout_component}
        states = component_states("workbook: the components after the press", asm)
        check(resolved_judged(states, components) == [],
              f"workbook: every component of the assembly read, each still resolved after the press: "
              f"{resolved_judged(states, components) or states}")
        out["component_only"] = got and {s: {k: v for k, v in r.items() if k != "points"}
                                         for s, r in got["reads"].items()}

        say("-- workbook  a global changed and saved in a part loaded only as a component (G2): GLOBALS_DIFFER")
        g2, was = parts["G2"], recorded(desk, parts["G2"])
        set_global("workbook: G2's Face Width 16, saved, its window closed", g2, "16", save=True, close=True)
        activate("workbook", user)
        now = docs("workbook: G2 a component only again")
        check(now["docs"].get(path_key(g2), {}).get("visible") is False,
              f"workbook: G2 loaded only as a component again: {now['docs'].get(path_key(g2))}")
        judged_refusal("workbook: G2's global, a component only", desk, press("G2 changed"),
                       said_globals(stem_of(g2), FACE_WIDTH, "16", was), folders, uk)
        set_global(f"workbook: G2's Face Width put back to {was}, saved, its window closed", g2, was, save=True,
                   close=True)
        activate("workbook", user)

        say("-- workbook  a global changed in a part open behind the user's (G1), not saved: MODIFIED; then saved: "
            "GLOBALS_DIFFER")
        g1, was = parts["G1"], recorded(desk, parts["G1"])
        set_global("workbook: G1's Face Width 16, not saved, its window left open", g1, "16")
        activate("workbook", user)
        now = docs("workbook: G1 behind the user's part")
        g1_now = now["docs"].get(path_key(g1), {})
        check(g1_now.get("visible") is True and g1_now.get("flag") is True and now["active"] == file_of(user),
              f"workbook: G1 open in its own window, changed and not saved, not active: {g1_now}")
        judged_refusal("workbook: G1 changed, not saved, behind the user's part", desk, press("G1 changed"),
                       said_modified([stem_of(g1)]), folders, uk)
        save_one("workbook: G1 saved", g1)
        judged_refusal("workbook: G1's global, saved, behind the user's part", desk, press("G1 saved"),
                       said_globals(stem_of(g1), FACE_WIDTH, "16", was), folders, uk)
        set_global(f"workbook: G1's Face Width put back to {was}, saved, its window left open", g1, was, save=True)
        activate("workbook", user)
        say("-- workbook  G1 open in its own window behind the user's part, as recorded: written by its object, not "
            "activated")
        judged_written("workbook: G1 behind the user's part", press("G1 behind"), folders, reducer_expect(desk), uk,
                       {"SaveAs": 4, "GetOpenDocumentByName": None}, name)
        close_window("workbook: G1's own window closed", g1)
        activate("workbook", user)

        say("-- workbook  the assembly and its parts closed, no assembly open: the job opens each part, writes it, "
            "closes it")
        left = run("workbook: the copy's documents closed unsaved", W.quit_in(folder))
        check(not left, f"workbook: nothing of the copy open: left {left}")
        activate("workbook", user)
        n = len(REDUCER)
        judged_written("workbook: the job opens the parts", press("parts closed"), folders, reducer_expect(desk), uk,
                       {"SaveAs": n, "OpenDoc6": n, "CloseDoc": n, "ActivateDoc3": None,
                        "GetOpenDocumentByName": None}, name)

        say(f"-- workbook  the open-beside fallback: STEP_EXPORT_FROM_COMPONENT_ON_{year()} False in this process only, "
            "the assembly open, its parts loaded only as components")
        open_assembly("workbook: the assembly opened again", asm)
        activate("workbook", user)
        with patched(findings, {finding_name("STEP_EXPORT_FROM_COMPONENT", year()): False}, say=say):
            judged_written("workbook: opened beside the assembly", press("open beside"), folders, reducer_expect(desk),
                           uk, {"SaveAs": n, "OpenDoc6": n, "CloseDoc": n, "ActivateDoc3": None,
                                "GetOpenDocumentByName": None}, name)
        states = component_states("workbook: the components after the fallback", asm)
        check(resolved_judged(states, components) == [],
              f"workbook: after the fallback's closes every component of the assembly read and still resolved: "
              f"{resolved_judged(states, components) or states}")
        check(sorted(stems) == sorted(s for s, _, _, _ in REDUCER.values()),
              f"workbook: the record's parts throughout: {stems}")
    finally:
        if user is not None:
            run("workbook: the user's part closed", W.quit_in(os.path.dirname(user)))
        if not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], folder, "workbook", save=False)



# -- refusals ---------------------------------------------------------------------------------------------------------


def user_pair(folder):
    """An assembly of the user's own, unrelated to the gearbox: a 25 / 50 pair at module 1.5, machined, built by the
    app's own pair route (as F2's probe built its pair) and left open; its path."""
    spec_a = GearSpec(module="1.5", teeth="25", face_width="8", bore="")
    spec_b = GearSpec(module="1.5", teeth="50", face_width="8", bore="")
    stems = pair_stems(PairSpec(mode=MODE_PAIR, gear_a=spec_a, gear_b=spec_b))
    pin, gear = (os.path.join(folder, s + ".SLDPRT") for s in stems[:2])
    asm = os.path.join(folder, stems[2] + ".SLDASM")
    plans = [plan_for(spec, kind_for(spec).derive(spec), "", p) for spec, p in ((spec_a, pin), (spec_b, gear))]
    assembly = pairs.assembly_plan(spec_a, spec_b, pin, gear, "", asm)
    result = run("refusals: the user's own assembly built", lambda s: swbuild.build_pair(s, plans[0], plans[1], assembly),
                 1800)
    check(bool(result.ok and result.assembly is not None and result.assembly.ok) and os.path.isfile(asm),
          f"refusals: the user's own assembly {file_of(asm)} built and saved: ok {result.ok}")
    return asm


def section_refusals(out):
    say("== refusals  each refusal made and read: on the form MODIFIED, GLOBALS_DIFFER, the user's keyway written with "
        "its size check skipped, NO_RECORD; in the window on the printed 12 : 1 LIGHTWEIGHT (a lightweight component, "
        "then a suppressed one), the keyway recorded and the set written, CHANGES_ON_UPDATE, UNSAVED_MARK, "
        "FEATURE_IN_ERROR; then the reducer closed and an unrelated assembly of the user's open: LIGHTWEIGHT, and the "
        "form's NOT_A_PART")
    require_findings("refusals")
    folder = W.fresh_folder("refusals")
    user = user_document("refusals")
    uk = path_key(user)
    root, strand = tk_root(), Strand(press_runner)
    copy = pair_folder = None
    try:
        app = make_form(root, strand)
        _, _, coupon = form_build("refusals, the form: Coupon_R", app, folder, "Coupon_R", COUPON)
        stem = stem_of(coupon)
        car = store.read_sidecar(store.sidecar_path(coupon))
        was = dict((str(n), str(v)) for n, v in car.record.variables)[FACE_WIDTH]
        folders = (folder, os.path.dirname(user))

        def form(tag):
            return lambda: press_form(app, strand, f"refusals, the form: {tag}")
        say("-- refusals  the form: a global changed in SolidWorks and not saved, then saved")
        set_global("refusals, the form: Coupon_R's Face Width 9, not saved", coupon, "9")
        judged_refusal("refusals, the form: MODIFIED", app, form("changed"), said_modified([stem]), folders, None)
        save_one("refusals, the form: Coupon_R saved", coupon)
        judged_refusal("refusals, the form: GLOBALS_DIFFER", app, form("saved"),
                       said_globals(stem, FACE_WIDTH, "9", was), folders, None)
        say("-- refusals  the form: Face Width put back by the form's own Update values (the form still says the "
            "record's value), saved as the person saves; then a press writes into a folder of its own")
        jobs = len(strand.jobs)
        app._derive_now()  # noqa: SLF001
        app._update_values()  # noqa: SLF001 - the form's own: its record loaded by the build's finish
        if app._pending_build is not None:  # noqa: SLF001
            app._collect_build()  # noqa: SLF001 - its own finish: the status and the record
        done = strand.jobs[-1]["value"] if len(strand.jobs) > jobs else None
        say(f"status  refusals, the form: Update values: {app.status.get()}")
        check(done is not None and done.ok and FACE_WIDTH in list(done.changed) and done.rebuilt,
              f"refusals, the form: Update values set \"{FACE_WIDTH}\" back to {was} and rebuilt Coupon_R: "
              f"{app.status.get()!r}")
        save_one("refusals, the form: Coupon_R saved after Update values", coupon)
        k, w = span_expected(1.5, 20)[:2]
        judged_written("refusals, the form: after Update values", form("after Update values"), folders,
                       {stem: {"radius": outer_radius(1.5, 20), "face": 8.0, "extent": extent_want(), "rows": (),
                               "count": 1, "span": ("span", k, w, False)}}, None,
                       {"SaveAs": 1, "GetOpenDocumentByName": None}, stem)

        say("-- refusals  the form: the user's keyway cut in the coupon and saved: written, its size check skipped on "
            "the job's own read of the part")
        A.keyway("refusals, the form: the user's keyway in Coupon_R", coupon)
        save_one("refusals, the form: Coupon_R saved with the keyway", coupon)
        theirs = user_features_read("refusals, the form: Coupon_R's features", coupon)
        check("User Keyway" in theirs, f"refusals, the form: the script reads the user's keyway in Coupon_R: {theirs}")
        judged_written("refusals, the form: the user's keyway", form("keyway"), folders,
                       {stem: {"radius": None, "face": 8.0, "extent": "skipped: user features", "rows": (), "count": 1,
                               "span": ("span", k, w, False), "features": theirs}}, None,
                       {"SaveAs": 1, "GetOpenDocumentByName": None}, stem)
        say("-- refusals  the form: an Output folder that does not exist")
        missing = os.path.join(folder, "no such folder")
        app.out_folder.set(missing)
        judged_refusal("refusals, the form: NO_FOLDER", app, form("no folder"),
                       said_no_folder(ui_text.short_path(missing, 48)), folders, None, in_job=False)
        check(not os.path.exists(missing), "refusals, the form: the missing Output folder was not made")
        app.out_folder.set(folder)
        say("-- refusals  the form: a part with no .gear.json active (the user's Sprocket)")
        sprocket = os.path.join(os.path.dirname(user), "Sprocket.SLDPRT")
        if os.path.exists(store.sidecar_path(sprocket)):
            say(f"fact    refusals: {file_of(sprocket)} has a .gear.json beside it, so NO_RECORD is not shown here")
        else:
            open_doc("refusals, the form: the user's Sprocket opened", sprocket)
            judged_refusal("refusals, the form: NO_RECORD", app, form("no record"), said_no_record(file_of(sprocket)),
                           folders, None, in_job=False)
            close_window("refusals: the user's Sprocket closed", sprocket)
        activate("refusals", user)

        say("-- refusals  the window, on a copy of the printed 12 : 1, its assembly open, the user's part active")
        copy, _, book, desk = copy_deskp(printed_reducer_master(), "refusals-reducer")
        box = desk.record.gearbox
        asm, assembly = box.assembly, stem_of(box.assembly)
        parts = reducer_parts(desk)
        g4_name = dict(W.bodies(box))["G4"]
        g4 = stem_of(parts["G4"])
        folders = (copy, os.path.dirname(user))

        def window(tag):
            return lambda: window_press(desk, f"refusals, the window: {tag}")
        open_assembly("refusals: the assembly opened", asm)
        activate("refusals", user)
        state = set_component("refusals: G4's component set lightweight", asm, g4_name, 1)
        activate("refusals", user)
        check(state in (1, 4), f"refusals: {g4_name} reads lightweight: {state}")
        judged_refusal("refusals, the window: a lightweight component", desk, window("lightweight"),
                       said_lightweight([g4], assembly), folders, uk)
        states = component_states("refusals: after the press", asm)
        check(states is not None and states.get(g4_name) in (1, 4),
              f"refusals: {g4_name} still lightweight after the press (the job read it, set nothing): {states}")
        set_component("refusals: G4's component resolved again", asm, g4_name, 2)
        activate("refusals", user)

        say("-- refusals  the window: a component suppressed, the sentence's other case")
        state = set_component("refusals: G4's component suppressed", asm, g4_name, 0)
        activate("refusals", user)
        before = snap_all("refusals: suppressed", folders)
        seen = window_press(desk, "refusals, the window: suppressed")
        after = snap_all("refusals: suppressed", folders)
        value = seen["job"]["value"] if seen["job"] else None
        out["suppressed"] = {"state": state, "said": seen["status"],
                             "written": [file_of(f) for _, f in value.written] if value else None}
        if value is not None and value.refusal is not None:
            say(f"fact    refusals: with {g4_name} suppressed (state {state}) the app meets it with LIGHTWEIGHT's "
                "sentence, which names a suppressed component among its cases since 567773c")
            refused("refusals, the window: suppressed", seen, said_lightweight([g4], assembly), before[0], after[0],
                    (before[1], after[1]), (before[2], after[2]), uk)
        else:
            say(f"fact    refusals: with {g4_name} suppressed (state {state}) SolidWorks still held its part, and the "
                f"app wrote the set: {seen['status']!r}")
            written("refusals, the window: suppressed", seen, copy, reducer_expect(desk), before[0], after[0],
                    (before[1], after[1]), (before[2], after[2]), name=desk.reading.spec.box.name, user=uk,
                    calls={"SaveAs": len(REDUCER), "GetOpenDocumentByName": None})
        set_component("refusals: G4's component resolved again", asm, g4_name, 2)
        left = run("refusals: the copy closed unsaved (the states set back) and opened again",
                   W.quit_in(copy))
        check(not left, f"refusals: nothing of the copy left open: {left}")
        open_assembly("refusals: the assembly opened again", asm)
        activate("refusals", user)

        say("-- refusals  the window: the user's keyway in G1's part, recorded by a quiet press; the set written")
        g1 = parts["G1"]
        A.keyway("refusals: the user's keyway in G1's part", g1)
        A.save_user(copy, "the user's keyway in G1's part")
        activate("refusals", user)
        quiet, _ = A.press(desk, "refusals: a quiet Update SolidWorks (the keyway recorded)")
        work = desk.record.gearbox.user_work if desk.record is not None else None
        listed = [(f.name, file_of(f.path)) for f in (work.features if work else [])]
        check(quiet is not None and ("User Keyway", file_of(g1)) in listed,
              f"refusals: the record lists the User Keyway in G1's part: {listed}")
        # The names the list gives are those the job reads live in the part written (5e45718), which may hold the
        # keyway's sketch beside it, as W9a allows the inventory: this script reads them itself.
        g1_features = user_features_read("refusals: G1's features as written", g1)
        activate("refusals", user)
        judged_written("refusals, the window: the set with the user's keyway", window("keyway on record"), folders,
                       reducer_expect(desk, sizes={"G1": "skipped: user features"}, features={"G1": g1_features}),
                       uk, {"SaveAs": len(REDUCER), "GetOpenDocumentByName": None}, desk.reading.spec.box.name)

        say("-- refusals  the window: G4's Flank typed arcs in Excel, a change Update cannot carry (G4's part made new, "
            "as W9d's Sun): NEW_REVISION; then the cell cleared again")
        flank = W.cell(book, "Gears", "Flank", "G4")
        W.edit(desk, book, ("Gears", flank, "arcs"))
        check(desk.update is not None and desk.update.needs_new_revision,
              f"refusals: Update needs a new revision for G4's Flank: {desk.update and list(desk.update.structural)}")
        judged_refusal("refusals, the window: NEW_REVISION", desk, window("G4 arcs"), said_new_revision([g4]), folders,
                       uk, in_job=False)
        W.edit(desk, book, ("Gears", flank, None))
        check(desk.update is not None and desk.update.record_matches and not desk.update.changed_parts,
              "refusals: with the Flank cleared, Update plans nothing changed again")
        say("-- refusals  the window: G1's Bore typed 14 in Excel (the keyway falls inside the bore)")
        W.edit(desk, book, ("Gears", W.cell(book, "Gears", "Bore", "G1"), 14))
        judged_refusal("refusals, the window: CHANGES_ON_UPDATE", desk, window("Bore 14"), said_values([stem_of(g1)]),
                       folders, uk, in_job=False)
        say("-- refusals  the window: Update SolidWorks (the keyway rebuilt into error), not saved")
        result, _ = A.press(desk, "refusals: Update SolidWorks, G1's Bore 14")
        check(result is not None, f"refusals: the Update ran: {desk.error}")
        if result is not None:
            say(f"fact    refusals: the Update: ok {result.ok}; failures {result.failures}; the user's features in "
                f"error {[(f.name, file_of(f.path)) for f in result.user_features_in_error]}")
        activate("refusals", user)
        marked = [stem_of(e.path) for e in desk.record.current_parts()
                  if any(store.same_path(e.path, m) for m in desk.record.unsaved)]
        check(marked == [stem_of(g1)], f"refusals: the record marks G1's part alone unsaved: {marked}")
        judged_refusal("refusals, the window: UNSAVED_MARK", desk, window("updated, not saved"), said_unsaved(marked),
                       folders, uk, in_job=False)
        say("-- refusals  the window: saved as the person saves; G1's keyway in error, G1 not active")
        A.save_user(copy, "the Update's result")
        desk.plan_solidworks()
        activate("refusals", user)
        features = features_of("refusals: G1's features", g1)
        errors = [n for n, c, warning in (features or []) if c and c != swcom.UNREAD and not warning]
        check("User Keyway" in errors, f"refusals: G1's part holds the User Keyway in error: {errors}")
        judged_refusal("refusals, the window: FEATURE_IN_ERROR", desk, window("keyway in error"),
                       said_feature(stem_of(g1), errors), folders, uk)

        say("-- refusals  the reducer closed, an unrelated assembly of the user's open and active")
        left = run("refusals: the copy closed", W.quit_in(copy))
        check(not left, f"refusals: nothing of the copy open: {left}")
        pair_folder = W.fresh_folder("refusals-pair")
        pair = user_pair(pair_folder)
        activate("refusals: the user's assembly", pair)
        stems = [stem_of(e.path) for e in desk.record.current_parts()]
        judged_refusal("refusals, the window: parts closed, the user's assembly open", desk, window("parts closed"),
                       said_lightweight(stems, stem_of(pair)), (copy, os.path.dirname(user), pair_folder),
                       path_key(pair))
        say("fact    refusals: the parts are closed and in no assembly; the sentence names that case among the three it "
            "stands for (LIGHTWEIGHT is inferred, not read: F2-PROBES-REVIEW §3.3)")
        judged_refusal("refusals, the form: NOT_A_PART", app, form("an assembly active"), said_not_a_part(file_of(pair)),
                       (folder, os.path.dirname(user), pair_folder), path_key(pair), in_job=False)
    finally:
        root.destroy()
        for f in [x for x in (pair_folder, folder, os.path.dirname(user)) if x]:
            run(f"refusals: {os.path.basename(f)} closed unsaved", W.quit_in(f))
        if copy is not None and not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], copy, "refusals-reducer", save=False)


# -- userwork ---------------------------------------------------------------------------------------------------------


def box_process_row(book):
    """The Box sheet's row labelled Process (any case), and its first row with an empty label (F1's)."""
    ws = book.wb.Worksheets("Box")
    labels = {r: str(ws.Cells(r, 1).Value or "").strip() for r in range(2, 80)}
    found = next((r for r, t in labels.items() if t.lower() == "process"), None)
    empty = next(r for r, t in labels.items() if not t)
    return found, empty


def rangebox_expect(desk, process, live=None):
    """RangeBox's five parts as a press writes them, worked here: rows and counts from the workbook's Gears and Shafts
    (Copies), the size check as ruled, the span (§3.0's rows for Sun and Planet, pins for the ring and the sleeve,
    none for a machined part), the user's features from the record's inventory."""
    spec = desk.reading.spec
    work = desk.record.gearbox.user_work
    out = {}
    for e in desk.record.current_parts():
        stem = stem_of(e.path)
        rows = tuple(g.id for g in spec.gears if g.id in e.gears)
        if process == "machined":
            span = MACHINED_SPAN
        elif stem in RANGEBOX_SPANS:
            m, z = RANGEBOX_SPANS[stem]
            k, w = span_expected(m, z, backlash=printed_backlash(m))[:2]
            span = ("span", k, w, False)
        elif RANGEBOX.get(stem, ((), 0, ""))[2] in ("skipped: ring", "skipped: sleeve"):
            span = INTERNAL_SPAN
        else:
            span = None                       # the dog's span: package A's, not worked here
        size = RANGEBOX.get(stem, ((), 0, "?"))[2]
        if size == "checked" and not extent_on():
            size = "skipped: not measured"
        planet = stem == "Gear_m1.25_N13"
        out[stem] = {"path": e.path, "radius": outer_radius(1.25, 13) if planet else None, "face": 10.0,
                     "extent": size, "rows": rows, "count": sum(copies_of(spec, r) for r in rows), "span": span,
                     "features": (live.get(stem, ()) if live is not None else
                                  tuple(dict.fromkeys(f.name for f in (work.features if work else [])
                                                      if store.same_path(f.path, e.path))))}
    return out


def section_userwork(out):
    say("== userwork  a copy of W9a's setup.master (RangeBox with the user's work): Print files as built (Machined); "
        "Printed typed and one Update SolidWorks as F1's demonstration did; Print files before the save, then after "
        "it: the five parts written, none of the user's components, the User Keyway's part with its size check "
        "skipped; the user's work as before; nothing saved")
    require_findings("userwork")
    master = A.MASTER["setup"]
    if not master:
        raise AssertionError("userwork: give --user-master, W9a's setup.master for this SolidWorks version")
    with open(store.link_record_path(os.path.join(master, "RangeBox.xlsx")), encoding="utf-8") as handle:
        raw = json.load(handle)
    said = [p.get("spec", {}).get("process") for p in raw.get("parts", []) if "process" in p.get("spec", {})]
    schema = raw.get(store.LINK_SCHEMA_KEY)
    check(isinstance(schema, int) and schema < store.LINK_SCHEMA_VERSION and not said,
          f"userwork: the master's own record was written before F1: link schema {schema}, no part saying a process")
    if W.free_gb() < PRESS_FREE_GB:
        A.section_stop(f"userwork: {W.memory()}: under {PRESS_FREE_GB:g} GB free before the copy (SolidWorks 2024's "
                       "first press on a freshly opened RangeBox costs 3.3 to 4 GB; run it first, in a fresh session)")
    copy, path, book, desk = copy_deskp(master, "userwork")
    try:
        box = desk.record.gearbox
        asm = box.assembly
        uk = path_key(asm)
        users = A.rb_users()
        name = desk.reading.spec.box.name
        check(desk.a.spec.box.process == "machined" and not desk.reading.spec.box.process,
              f"userwork: as built, no Process row, the blank read Machined: {desk.a.spec.box.process!r}")
        open_assembly("userwork: RangeBox opened, the user's own document", asm)
        A.users_in_copy("userwork, before", desk, copy, users)
        entities_before = A.entities_of("userwork, before", desk, copy)
        sun = A.sun_part(box)
        keyway_before = [f for f in (features_of("userwork: Sun's features", sun) or []) if f[0] == "User Keyway"]
        check(bool(keyway_before) and not keyway_before[0][1], f"userwork: the User Keyway in Sun's part, code "
                                                                f"{keyway_before[0][1] if keyway_before else None}")
        activate("userwork", asm)
        folders = (copy,)
        n = len(desk.record.current_parts())
        calls = {"SaveAs": n, "GetOpenDocumentByName": None}

        def window(tag):
            return lambda: window_press(desk, f"userwork: {tag}")
        say("-- userwork  Print files as built: every part Machined (E4), exported")
        live = {stem_of(e.path): user_features_read(f"userwork: {stem_of(e.path)}'s features", e.path)
                for e in desk.record.current_parts()}
        check("User Keyway" in live.get("Gear_m1.25_N29", ()) and not any(v for s, v in live.items()
                                                                          if s != "Gear_m1.25_N29"),
              f"userwork: the script reads the user's features in the five parts, the User Keyway in Sun's alone: {live}")
        judged_written("userwork: as built, Machined", window("as built"), folders,
                       rangebox_expect(desk, "machined", live), uk, calls, name, process="Process: Machined")

        say("-- userwork  Printed typed on the Box sheet in Excel, in a row labelled Process; one Update SolidWorks")
        found, empty = box_process_row(book)
        row = found or empty
        cells = ([] if found else [("Box", f"A{row}", "Process")]) + [("Box", f"B{row}", "Printed")]
        say(f"person  userwork: {'types Printed beside its Process row' if found else 'adds a row labelled Process'} at "
            f"Box row {row}")
        W.edit(desk, book, *cells)
        u = desk.update
        check(desk.a.spec.box.process == "printed" and u is not None and len(u.changed_parts) == n
              and not u.needs_new_revision, f"userwork: the Box reads Printed; Update plans the {n} parts in place: "
                                            f"{[file_of(p.path) for p in (u.changed_parts if u else [])]}")
        stems = [stem_of(e.path) for e in desk.record.current_parts()]
        judged_refusal("userwork: Printed typed, before the Update", desk, window("Printed typed"), said_values(stems),
                       folders, uk, in_job=False)
        if W.free_gb() < PRESS_FREE_GB:
            A.section_stop(f"userwork: {W.memory()}: under {PRESS_FREE_GB:g} GB free before the press")
        result, _ = A.press(desk, "userwork: Printed, one Update")
        check(result is not None and result.ok and not result.failures and not result.user_in_error
              and not result.user_features_in_error,
              f"userwork: the Update ended ok, nothing of the user's in error: {desk.error if result is None else result.failures}")
        activate("userwork", asm)
        marked = [stem_of(e.path) for e in desk.record.current_parts()
                  if any(store.same_path(e.path, m) for m in desk.record.unsaved)]
        check(len(marked) == n, f"userwork: the record marks the {n} parts unsaved after the Update: {marked}")
        judged_refusal("userwork: before the save", desk, window("before the save"), said_unsaved(marked), folders, uk,
                       in_job=False)

        say("-- userwork  saved as the person saves; Print files: the five parts, none of the user's components")
        A.save_user(copy, "the Update's result")
        desk.plan_solidworks()
        activate("userwork", asm)
        record_file = store.link_record_path(path)
        record_before = sha(record_file)
        expect = rangebox_expect(desk, "printed", live)
        listed = rangebox_expect(desk, "printed")["Gear_m1.25_N29"]["features"]
        check(expect["Gear_m1.25_N29"]["extent"] == "skipped: user features" and "User Keyway" in listed,
              f"userwork: the record's inventory holds the User Keyway in Sun's part: {listed}")
        user_files = {u: sha(os.path.join(copy, u)) for u in ("Sprocket.SLDPRT", "Housing.SLDPRT")
                      if os.path.isfile(os.path.join(copy, u))}
        got = judged_written("userwork: Printed, saved", window("saved"), folders, expect, uk, calls, name)
        if got is not None:
            out["printed"] = {s: r["app"] for s, r in got["reads"].items()}
            check(not [f for f in os.listdir(got["where"]) if f.lower().startswith(("sprocket", "housing"))],
                  "userwork: no file of the user's components in the press's folder")
        check(sha(record_file) == record_before, "userwork: the record is as it was (Print files writes no record)")
        check(user_files and all(sha(os.path.join(copy, u)) == h for u, h in user_files.items()),
              f"userwork: the user's own part files as they were: {sorted(user_files)}")
        A.users_in_copy("userwork, after", desk, copy, users)
        entities_after = A.entities_of("userwork, after", desk, copy)
        moved = {k: (entities_before.get(k), v) for k, v in entities_after.items() if entities_before.get(k) != v}
        check(entities_after == entities_before and sorted(entities_after) == sorted(A.RB_USER_MATES),
              f"userwork: every one of the user's eight mates joins what it joined before: {moved or 'the same'}")
        keyway = [f for f in (features_of("userwork: Sun's features after", sun) or []) if f[0] == "User Keyway"]
        check(bool(keyway) and not keyway[0][1], f"userwork: the User Keyway in Sun's part after, code "
                                                  f"{keyway[0][1] if keyway else None}")
    finally:
        if not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], copy, "userwork", save=False)


# -- the run ----------------------------------------------------------------------------------------------------------

ORDER = ["gates", "form", "workbook", "refusals", "userwork"]
SECTIONS = {"gates": section_gates, "form": section_form, "workbook": section_workbook, "refusals": section_refusals,
            "userwork": section_userwork}
FOLDERS = {"gates": ["gates", "gates-window"], "form": ["form"], "workbook": ["workbook"],
           "refusals": ["refusals", "refusals-reducer", "refusals-pair"], "userwork": ["userwork"]}


def done_here(name):
    """What of a section this <out> holds already (W9a's done_here for these sections' folders)."""
    return [p for p in (os.path.join(OUT, f) for f in FOLDERS.get(name, [name])) if os.path.exists(p)]


def main():
    A.SECTIONS.clear()
    A.SECTIONS.update(SECTIONS)
    if A._given in ("", "all"):                    # noqa: SLF001
        A.CHOSEN = list(ORDER)
    A.done_here = done_here
    A.RUN_TITLE, A.JSON_STEM = "F2 demonstration", "f2-demo"
    if WW_CLOSE_FLAG in A.ARGS:              # off unless the run asks: W9c's own close path, as W9c puts it in
        import w9c_demonstration as C        # noqa: PLC0415
        C.close_outlived_on()
    return A.main()


if __name__ == "__main__":
    code = 1
    try:
        code = main()
    finally:
        with open(W.LOG_PATH, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(W.LOG) + "\n")
    raise SystemExit(code)
