r"""F2's probe on SolidWorks (PLAN-PRINTED §3.1.2; F2-0, §3.3): writing a part to a STEP file for the slicer, the one
call Print files adds that the app has never made, which writes a file and could raise a dialog or rename a document.
Nothing of F2's export exists in the app yet: this measures the calls package B's job would make, and proposes the
findings ``findings.py`` holds as None (F2-INTERFACES.md §7) in the log, setting none. The note is
``docs/notes-printed/F2-PROBES.md``: what each step asks, which answer proposes which finding, the command lines and times.

python.exe probe/f2_probes.py <repo src> <output folder under C:\> --pid PID [--log FILE]
                              [--sections export,component|all] [--redo] [--close-outlived-whats-wrong]
python probe/f2_probes.py --self-check      (no SolidWorks: every judgement below on made-up readings and made-up STEP
                                             texts, each failing way shown)
python probe/f2_probes.py --help

No master is needed: every part is built in this run's folder by the app's own routes (``gears.plan_for`` and
``swbuild.build``, as the strip builds one gear; ``pair.assembly_plan`` and ``swbuild.build_pair``, as the form builds a
pair) and saved there, so every read starts from a document saved and unmarked.

Sections, in this order (each runs alone and builds what it needs; "component" is the likelier to meet a dialog):

- ``export``     a printed spur gear (m 1.5, z 20, face 8, no bore) and a printed helical gear (m_n 2, z 20, beta 15,
               face 10, no bore), built and saved in ``f2-export``. (1) ``swSaveAsOptions_e``'s Silent and Copy read from
               the running install's swconst.tlb, Silent held to ``findings.SAVE_AS_SILENT``. (2) The spur, active,
               exported by ``IModelDocExtension.SaveAs(<path>.step, 0, Silent | Copy, null, out errors, out warnings)``:
               what it answers, both codes, the file on disk, the time, any window, and the document's path, title and
               save flag, the active document, every document of the folder and the user's documents' save flags read
               before and after. (3) The file read as text (never opened in SolidWorks, GOTCHAS §20): the frame, the
               FILE_SCHEMA (matched by prefix), the solid, shell and surface-model instances counted as instances, the
               length unit, and from the VERTEX_POINTs the largest radius from Z and the axial extent against the app's
               d_a / 2 and face width. (4) The helical part, the same. (5) A second export onto (2)'s file: a fact, and
               the text compared with (2)'s, the control that the comparison of (6) can be made at all. (6) The spur open
               in its own window, the helical active, the spur exported by its own document object (the app's
               ``use_open_document``, no activation): its file against (2)'s and (4)'s. (8) One global of the spur
               changed and rebuilt, not saved, the spur activated and exported: whether the file holds the changed solid
               and the save flag stays on. (9) Everything of the folder closed unsaved (``QuitDoc``) under the watch, and
               the user's documents compared with the section's start.
- ``component``  a printed pair, 25 / 50 at module 1.5, fixed, built by the form's pair route in ``f2-component``,
               closed, and its assembly opened alone, so both parts are loaded only as its components. Every open
               document's window read (``IModelDoc2.Visible``, ``ActiveView``) and ``ISldWorks.GetOpenDocumentByName``
               (unverified in the macro database, new to the app) read for each part, by its path and by its file name.
               (7a) The 50-tooth gear reached by ``GetOpenDocumentByName`` and exported by that object with no
               activation; the assembly's title and save flag, the active document, the component's state and every
               flag read before and after. (7b) The fallback: the same part opened in its own window by
               ``Session.open_document`` (which activates), exported, closed by ``CloseDoc`` on its title; whether the
               assembly is still open and unmarked, its component loaded and resolved, which document is active, and any
               window; then the assembly activated again, as the job puts the user's document back. (7d) Everything
               closed; the gear opened alone and exported twice (the reference and its determinism control), then the
               pinion opened and exported once (the file that must differ), the gear's window read while it is open
               but not active (F2-0-REVIEW's M1: the case PART_WINDOW_READ is for; step 6 reads the spur the same way);
               ``GetOpenDocumentByName`` on the gear open alone (it must answer) and closed (it must not). The files of
               (7a) and (7b) are held to the reference and PART_WINDOW_READ is proposed here, before (7c), so a hang
               there cannot void them (S2). (7c), last: the assembly opened again, the gear's component set
               lightweight (a fact: that marks the assembly); whether the walk and ``GetOpenDocumentByName`` still
               reach a document; if one, its export; then the not-open path (opened beside, exported, closed) and the
               component's state after; then resolved again; its files held to the reference.

**A dialog is a finding, not a failure.** Every call that may raise one runs under W9c's watch (``w9c_probes.watched``:
logs class, caption, buttons and texts, never SolidWorks' frame title, never answers). A dialog that came and went ends
that step with a STOP line and its findings proposed None; a job that does not return in 120 s, or a dialog that
stays, ends the run with nothing closed or saved. Everything W9a's script does for a run is done here by running its
``main`` with these sections (as W9c's and W9d's probes do): the attach by PID and its check, the dialog watch with the
What's Wrong rule per version, keep-awake, the JSON after every section, APPDATA in the run folder, the guarded close,
``--sections`` and ``--redo``; W9c's ``--close-outlived-whats-wrong`` (SolidWorks 2024 only) is W9c's own path, put in when
the flag is given, as F1's demonstration puts it. W9a's main starts its own Excel and quits it at the end; this probe
asks nothing of it.

**Nothing of the user's is touched, and nothing is written outside this run's folder.** Every document is built here,
closed unsaved at its section's end; the only saves are the builds' own (``swbuild``'s save to a new path); every STEP
file goes into the section's ``print`` folder. A document not made by this run is logged as ``<user document N>`` (W8's
``open_titles``), its save flag read at each section's start and end and never changed. No path is logged but relative to
the run's output folder, and no STEP header (its FILE_NAME holds an author and an organisation) is ever logged: the
STEP files themselves stay in the run folder and are not to be committed.
"""

import math
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

EXTENT_TOL = 0.01          # mm: the largest radius and the axial extent against the app's (printout.EXTENT_TOL)
GEOMETRY_TOL = 1e-6        # mm: two files' vertices the same point
# The schemas a file may declare, matched by the FILE_SCHEMA name's prefix (printout.STEP_SCHEMAS; the self-check holds
# the two the same when the app's source is importable).
STEP_SCHEMAS = (
    ("AP203", ("CONFIG_CONTROL_DESIGN", "AP203_CONFIGURATION_CONTROLLED_3D_DESIGN")),
    ("AP214", ("AUTOMOTIVE_DESIGN",)),
    ("AP242", ("AP242_MANAGED_MODEL_BASED_3D_ENGINEERING",)),
)
SI_PREFIX_MM = {None: 1000.0, "MILLI": 1.0, "CENTI": 10.0, "DECI": 100.0, "MICRO": 0.001, "KILO": 1.0e6}
CONVERSION_MM = {"INCH": 25.4, "FOOT": 304.8}
SAVE_AS_ENUM = "swSaveAsOptions_e"
WINDOW_READS = ("Visible", "ActiveView")     # PART_WINDOW_READ's candidates, in this order


def statements(text):
    """A STEP file's statements in order, each stripped, split at every semicolon outside a quoted string ('' is a quote
    inside one) and outside a comment; line breaks dropped, since a Part 21 file's line breaks mean nothing."""
    out, cur, i, n = _Statements(), [], 0, len(text)
    in_string = False
    while i < n:
        c = text[i]
        if in_string:
            cur.append(c)
            if c == "'":
                if i + 1 < n and text[i + 1] == "'":
                    cur.append("'")
                    i += 1
                else:
                    in_string = False
        elif c == "'":
            in_string = True
            cur.append(c)
        elif c == "/" and text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = n if end < 0 else end + 2
            continue
        elif c == ";":
            out.append("".join(cur).replace("\r", "").replace("\n", "").strip())
            cur = []
        else:
            cur.append(c)
        i += 1
    tail = "".join(cur).replace("\r", "").replace("\n", "").strip()
    if tail:
        out = _Statements(out + [tail])
        out.unterminated = True                  # the file stops inside a statement: its frame is broken
    return out


class _Statements(list):
    """A file's statements, marked when the file ends without its last semicolon."""

    unterminated = False


def sections_of(parts):
    """``(frame_ok, header, data)``: whether the statements open ISO-10303-21 and close END-ISO-10303-21; the HEADER
    section's statements; the DATA section's, as {instance number: body}."""
    frame = bool(parts) and parts[0] == "ISO-10303-21" and parts[-1] == "END-ISO-10303-21" and not getattr(
        parts, "unterminated", False)
    header, data, where = [], {}, None
    for s in parts:
        if s in ("HEADER", "DATA"):
            where = s
            continue
        if s == "ENDSEC":
            where = None
            continue
        if where == "HEADER":
            header.append(s)
        elif where == "DATA":
            m = re.match(r"#(\d+)\s*=\s*(.*)$", s, re.S)
            if m:
                data[int(m.group(1))] = m.group(2).strip()
    return frame, header, data


def _unquoted(body):
    """The body with every quoted string emptied, so a name written inside a string is never read as an entity."""
    return re.sub(r"'(?:[^']|'')*'", "''", body)


def entity_names(body):
    """The entity names of one instance's body: one for a simple instance, NAME(...); each top-level one of a complex
    instance, ( A() B(...) )."""
    body = _unquoted(body).strip()
    if not body.startswith("("):
        m = re.match(r"([A-Z_][A-Z0-9_]*)\s*\(", body, re.I)
        return [m.group(1).upper()] if m else []
    names, depth, i = [], 0, 0
    while i < len(body):
        c = body[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif depth == 1:
            m = re.match(r"([A-Z_][A-Z0-9_]*)\s*\(", body[i:], re.I)
            if m:
                names.append(m.group(1).upper())
                i += len(m.group(1))
                continue
        i += 1
    return names


def count_of(data, name):
    """How many entity instances are of ``name``: counted as instances, never as substrings."""
    return sum(1 for body in data.values() if name in entity_names(body))


def schema_of(header):
    """The FILE_SCHEMA's first name, as written up to its first space or brace, upper case; None when there is none."""
    for s in header:
        if s.upper().startswith("FILE_SCHEMA"):
            m = re.search(r"'((?:[^']|'')*)'", s)
            if m:
                return re.split(r"[\s{]", m.group(1).strip(), maxsplit=1)[0].upper() or None
    return None


def schema_ap(name):
    """Which accepted AP a schema name is, by its prefix: AP203, AP214, AP242, or None."""
    for ap, prefixes in STEP_SCHEMAS:
        if name and any(name.upper().startswith(p) for p in prefixes):
            return ap
    return None


def length_unit(data):
    """The length unit the file declares: ``(label, millimetres per unit)``, or ``(None, None)`` when it declares none
    this can read, or more than one that differ."""
    found = set()
    for body in data.values():
        names = entity_names(body)
        if "LENGTH_UNIT" not in names:
            continue
        plain = _unquoted(body)
        if "SI_UNIT" in names:
            m = re.search(r"SI_UNIT\s*\(\s*(\$|\.(\w+)\.)\s*,\s*\.(\w+)\.\s*\)", plain, re.I)
            if m and m.group(3).upper() == "METRE":
                prefix = m.group(2).upper() if m.group(2) else None
                if prefix in SI_PREFIX_MM:
                    found.add(((prefix + "." if prefix else "") + "METRE", SI_PREFIX_MM[prefix]))
                    continue
            found.add(("unreadable SI unit", None))
        elif "CONVERSION_BASED_UNIT" in names:
            m = re.search(r"CONVERSION_BASED_UNIT\s*\(\s*'((?:[^']|'')*)'", body, re.I)
            name = m.group(1).strip().upper() if m else ""
            found.add((name, CONVERSION_MM.get(name)))
        else:
            found.add(("unreadable length unit", None))
    if len(found) != 1:
        return None, None
    label, mm = next(iter(found))
    return (label, mm) if mm else (None, None)


def vertices(data):
    """Every VERTEX_POINT's CARTESIAN_POINT, in the file's own unit."""
    out = []
    for body in data.values():
        if entity_names(body) != ["VERTEX_POINT"]:
            continue
        m = re.search(r"#(\d+)\s*\)\s*$", body)
        point = data.get(int(m.group(1))) if m else None
        p = re.match(r"CARTESIAN_POINT\s*\(\s*'(?:[^']|'')*'\s*,\s*\(([^)]*)\)\s*\)$", point or "", re.I)
        if p:
            try:
                out.append(tuple(float(v) for v in p.group(1).split(",")))
            except ValueError:
                pass
    return out


def step_facts(text):
    """What §3.1.4's check reads in a file, as facts: the frame, the schema and its AP, the instances counted, the
    length unit, and from the vertices (millimetres, the part's axis on Z) the largest radius and the axial extent."""
    frame, header, data = sections_of(statements(text))
    label, mm = length_unit(data)
    points = vertices(data)
    radius = extent = None
    if points and mm and all(len(p) == 3 for p in points):
        radius = max(math.hypot(x, y) for x, y, _ in points) * mm
        zs = [z for _, _, z in points]
        extent = (max(zs) - min(zs)) * mm
    name = schema_of(header)
    return {"frame": frame, "schema": name, "ap": schema_ap(name),
            "solids": count_of(data, "MANIFOLD_SOLID_BREP"), "closed_shells": count_of(data, "CLOSED_SHELL"),
            "open_shells": count_of(data, "OPEN_SHELL"), "surface_models": count_of(data, "SHELL_BASED_SURFACE_MODEL"),
            "unit": label, "mm_per_unit": mm, "vertices": len(points), "max_radius_mm": radius,
            "axial_extent_mm": extent, "instances": len(data)}


def file_reasons(facts):
    """§3.1.4's check on a file's facts (M2): every reason it would refuse, in printout.REASONS' order (EXTENT apart)."""
    out = []
    if not facts.get("frame"):
        out.append("FRAME")
    if not facts.get("ap"):
        out.append("SCHEMA")
    if facts.get("solids") != 1 or not facts.get("closed_shells"):
        out.append("SOLIDS")
    if facts.get("open_shells"):
        out.append("OPEN_SHELL")
    if facts.get("surface_models"):
        out.append("SURFACE_MODEL")
    if not facts.get("mm_per_unit"):
        out.append("UNIT")
    return out


def extent_reading(facts, outer_radius, face, tol=EXTENT_TOL):
    """The extent check §3.1.4 builds if step 3 bears it out: ``(holds, what)``, the largest radius from Z against
    ``outer_radius`` and the axial extent against ``face``, each to ``tol`` mm; holds is None when nothing was read."""
    r, e = facts.get("max_radius_mm"), facts.get("axial_extent_mm")
    if r is None or e is None:
        return None, "no vertex or no unit read"
    holds = abs(r - outer_radius) <= tol and abs(e - face) <= tol
    return holds, f"largest radius {r:.6f} against {outer_radius:.6f}, axial extent {e:.6f} against {face:.6f} mm"


def without_file_name(text):
    """A file's statements with the header's FILE_NAME left out (it holds the name, the time, an author and an
    organisation): what two exports of the same document must share."""
    return [s for s in statements(text) if not s.upper().startswith("FILE_NAME")]


def same_file(a, b):
    """Whether two STEP texts are the same but for FILE_NAME (step 6's "the file is right", the review's definition)."""
    return without_file_name(a) == without_file_name(b)


def differing(a, b):
    """How many statements differ, FILE_NAME aside (a fact beside same_file)."""
    x, y = without_file_name(a), without_file_name(b)
    return sum(1 for i in range(max(len(x), len(y))) if i >= len(x) or i >= len(y) or x[i] != y[i])


def geometry_of(text):
    """The instances counted by entity name and the vertices in millimetres, rounded to GEOMETRY_TOL: two files of the
    same solid written with other numbering share it."""
    _, _, data = sections_of(statements(text))
    counts = {}
    for body in data.values():
        for name in entity_names(body):
            counts[name] = counts.get(name, 0) + 1
    _, mm = length_unit(data)
    points = sorted(tuple(round(v * (mm or 1.0) / GEOMETRY_TOL) for v in p) for p in vertices(data))
    return counts, points


def rightness(text, own, other, control):
    """Whether ``text`` is the file of the document it was exported from: True when it is ``own`` but for FILE_NAME and
    not ``other``; False when it is ``other``, or not ``own`` and not even its geometry; None when the run cannot tell
    (the control, two exports of one document, differed; or the text differs from ``own`` with the same geometry).
    ``(answer, why)``."""
    if text is None or own is None:
        return None, "a file was not read"
    if control is not None and not control:
        return None, "two exports of one document differ beyond FILE_NAME, so a file cannot be told by its text"
    if other is not None and same_file(text, other):
        return False, "it is the other part's file"
    if same_file(text, own):
        return True, "the same as its own part's file but for FILE_NAME"
    if geometry_of(text) == geometry_of(own):
        return None, f"{differing(text, own)} statements differ from its own part's file, with the same geometry"
    return False, f"{differing(text, own)} statements differ from its own part's file, and the geometry differs"


def flags_turned_on(before, after):
    """Documents (by name) whose save flag is on after and was not before."""
    return sorted(n for n, f in (after or {}).items() if f and not (before or {}).get(n))


def export_reasons(d):
    """Everything wrong with one export as the step read it: ``d`` holds ``read`` (SaveAs's answer: returned, errors,
    warnings, on_disk, size), ``before`` and ``after`` (the bracket: ``doc`` path, title, flag; ``active``; ``folder`` and
    ``users`` flags) and ``dialogs``. An empty list is a clean export."""
    out = []
    read = d.get("read") or {}
    if read.get("returned") is not True:
        out.append(f"SaveAs answered {read.get('returned')!r}")
    for code in ("errors", "warnings"):
        if read.get(code) != 0:
            out.append(f"{code} {read.get(code)!r}")
    if not read.get("on_disk"):
        out.append("no file on disk")
    elif not read.get("size"):
        out.append("the file is empty")
    if d.get("dialogs"):
        out.append(f"{len(d['dialogs'])} window(s) came")
    before, after = d.get("before") or {}, d.get("after") or {}
    b, a = before.get("doc") or {}, after.get("doc") or {}
    if not b or not a:
        out.append("the document was not read before and after")
    else:
        if b.get("flag"):
            out.append("its save flag was on before the export, so a mark could not show")
        for key in ("path", "title", "flag"):
            if b.get(key) != a.get(key):
                out.append(f"its {key} changed: {b.get(key)!r} -> {a.get(key)!r}")
    if before.get("active") != after.get("active"):
        out.append(f"the active document changed: {before.get('active')!r} -> {after.get('active')!r}")
    for what in ("folder", "users"):
        on = flags_turned_on(before.get(what), after.get(what))
        if on:
            out.append(f"the export turned on the save flag of {on}")
        gone = sorted(set(before.get(what) or {}) - set(after.get(what) or {}))
        if gone:
            out.append(f"{gone} no longer open")
    return out


UNKNOWN_MARKS = ("could not show", "not read", "window")     # reasons that leave a judgement unable to tell


def _unknown(reasons):
    return any(any(mark in r for mark in UNKNOWN_MARKS) for r in reasons)


def save_as_copy_proposal(enum, silent):
    """SAVE_AS_COPY from swSaveAsOptions_e: its Copy member, proposed only when its Silent member is the
    SAVE_AS_SILENT the app already holds (the positive control); None otherwise."""
    if not enum or enum.get("swSaveAsOptions_Silent") != silent:
        return None
    value = enum.get("swSaveAsOptions_Copy")
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else None


def step_export_proposal(spur, helical):
    """STEP_EXPORT_ON_<year>: True when both exports (steps 2 and 4) were clean, both files pass §3.1.4's frame check,
    and the spur's file is the spur's size (its largest radius d_a / 2 and its axial extent the face width, each to
    0.01 mm: F2-0-REVIEW's S1; the helical's extent stays a fact); None otherwise (a rename, a marked flag, a window, a
    code, no file, a file that fails, a spur of the wrong size), with why."""
    why = []
    for label, d in (("spur", spur), ("helical", helical)):
        if not d or d.get("stop"):
            why.append(f"{label}: {(d or {}).get('stop') or 'not run'}")
            continue
        why += [f"{label}: {r}" for r in export_reasons(d)]
        why += [f"{label}: the file fails {r}" for r in file_reasons(d.get("facts") or {})]
        if label == "spur" and d.get("extent_holds") is not True:
            why.append(f"spur: its file's size is not the spur's (the extent check read {d.get('extent_holds')!r})")
    return (True if not why else None), why


def needs_active_proposal(d):
    """STEP_EXPORT_NEEDS_ACTIVE_ON_<year> from step 6: False when the file is right and the export was clean (the
    active document, its title, every flag as they were); True when it ran and the file was wrong or something changed;
    None when the run cannot tell. ``(value, why)``."""
    if not d or d.get("stop"):
        return None, (d or {}).get("stop") or "step 6 did not run"
    right, said = d.get("right") or (None, "not compared")
    reasons = export_reasons(d)
    if _unknown(reasons):
        return None, "; ".join(reasons)
    if right is None:
        return None, said
    if right and not reasons:
        return False, said
    return True, "; ".join([said] + reasons)


def from_component_proposal(d):
    """STEP_EXPORT_FROM_COMPONENT_ON_<year> from step 7: True when GetOpenDocumentByName reached the part loaded only as
    a component (and its controls held: a closed file not reached, the part open alone reached), its export was clean
    (the assembly's title and flag, the active document, the component's state and every flag as they were), its file
    is the part's own, and the lightweight component is either not reached or exports its own file too; False when one
    of those was measured wrong; None when the run cannot tell. ``(value, why)``."""
    if not d or d.get("stop"):
        return None, (d or {}).get("stop") or "step 7 (a) did not run"
    if not d.get("controls_ok"):
        return None, f"GetOpenDocumentByName's controls did not hold: {d.get('controls')}"
    if not d.get("found"):
        return False, "GetOpenDocumentByName did not reach the part loaded as a component"
    reasons = export_reasons(d)
    if d.get("state_before") != d.get("state_after"):
        reasons.append(f"the component's state changed: {d.get('state_before')} -> {d.get('state_after')}")
    if (d.get("asm_before") or {}).get("flag"):
        reasons.append("the assembly's save flag was on before the export, so a mark could not show")
    if d.get("asm_before") != d.get("asm_after"):
        reasons.append(f"the assembly changed: {d.get('asm_before')} -> {d.get('asm_after')}")
    if _unknown(reasons):
        return None, "; ".join(reasons)
    right, said = d.get("right") or (None, "not compared")
    light = d.get("light") or {}
    if light.get("stop") or "found" not in light:
        return None, f"the lightweight case: {light.get('stop') or 'not read'}"
    light_right = (light.get("right") or (None, "not compared")) if light.get("found") else (True, "not reached")
    if right is False or light_right[0] is False or reasons:
        return False, "; ".join([said, f"lightweight: {light_right[1]}"] + reasons)
    if right is None or light_right[0] is None:
        return None, f"{said}; lightweight: {light_right[1]}"
    return True, f"{said}; lightweight: {light_right[1]}"


def open_beside_proposal(d):
    """OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN_ON_<year> from step 7 (b) and (c): True when the part opened in its own window
    beside the assembly wrote its own file cleanly and CloseDoc left the assembly open, its flag as it was (from an
    unmarked start), the component in the state it had, under no window; and the not-open path of the lightweight case
    came under no window, left the assembly open and wrote the part's own file. ``(value, why)``."""
    if not d or d.get("stop"):
        return None, (d or {}).get("stop") or "step 7 (b) did not run"
    why, unknown = [], []
    if d.get("assembly_flag_before"):
        unknown.append("the assembly was marked before, so a mark could not show")
    if d.get("dialogs"):
        unknown.append(f"{len(d['dialogs'])} window(s) came")
    if not d.get("opened"):
        why.append("Session.open_document did not give the part")
    why += [r for r in d.get("export_reasons", []) if "active document changed" not in r]   # open_document activates
    if not d.get("assembly_open_after"):
        why.append("the assembly was not open after CloseDoc")
    if d.get("assembly_flag_after") != d.get("assembly_flag_before"):
        why.append(f"the assembly's flag {d.get('assembly_flag_before')} -> {d.get('assembly_flag_after')}")
    if d.get("state_after") != d.get("state_before"):
        why.append(f"the component's state {d.get('state_before')} -> {d.get('state_after')}")
    if d.get("users_turned_on"):
        why.append(f"a user document's flag turned on: {d['users_turned_on']}")
    right, said = d.get("right") or (None, "not compared")
    if right is None:
        unknown.append(said)
    elif not right:
        why.append(said)
    light = d.get("light") or {}
    if not light or light.get("stop"):
        unknown.append(f"the lightweight case: {light.get('stop') or 'not read'}")
    else:
        if light.get("dialogs"):
            unknown.append(f"lightweight: {len(light['dialogs'])} window(s) came")
        if not light.get("assembly_open_after"):
            why.append("lightweight: the assembly was not open after CloseDoc")
        lr, ls = light.get("beside_right") or (None, "not compared")
        if lr is None:
            unknown.append(f"lightweight: {ls}")
        elif not lr:
            why.append(f"lightweight: {ls}")
    if why:
        return False, "; ".join(why + unknown)
    if unknown:
        return None, "; ".join(unknown)
    return True, f"{said}; lightweight: {(light.get('beside_right') or (None, ''))[1]}"


def window_proposal(own, component_only, background):
    """PART_WINDOW_READ_ON_<year>: the first of WINDOW_READS that reads True on every document open in its own window
    (``own``, the active ones among them) and on every **part open in its own window but not active** (``background``,
    the one case the job reads it on: F2-0-REVIEW's M1), and False on every one loaded only as a component (each a
    {read: value} dict); None when neither does, or when any of the three lists is empty."""
    if not own or not component_only or not background:
        return None
    for read in WINDOW_READS:
        if (all(r.get(read) is True for r in list(own) + list(background))
                and all(r.get(read) is False for r in component_only)):
            return read
    return None


WINDOW_ROUTES = {"Visible": "IModelDoc2.Visible, True for a document open in its own window",
                 "ActiveView": "IModelDoc2.ActiveView not None, for a document open in its own window"}


def users_changed(before, after):
    """The user's documents (``<user document N>``: flag) between a section's start and end: any that closed, opened or
    changed its flag."""
    out = []
    for name in sorted(set(before or {}) | set(after or {})):
        if name not in (after or {}):
            out.append(f"{name} closed")
        elif name not in (before or {}):
            out.append(f"{name} opened")
        elif before[name] != after[name]:
            out.append(f"{name} flag {before[name]} -> {after[name]}")
    return out


def propose(name, value, evidence):
    """A finding proposed in ``findings.py``'s style, never set."""
    return f"propose {name} = {value!r}  # {evidence}"



# -- the self-check: made-up STEP texts and readings, each judgement's failing way shown ------------------------------


def _step(schema="AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }", unit="( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) )",
          solids=1, closed=1, open_shells=0, surface=0, points=((16.5, 0.0, 0.0), (0.0, -16.5, 8.0), (3.0, 4.0, 4.0)),
          end="END-ISO-10303-21;", name="Gear.STEP", extra=""):
    """A small made-up STEP file of the shape SolidWorks writes: FILE_NAME wrapped over two lines with an author and an
    organisation, a string holding a semicolon and an entity name, a complex unit instance."""
    lines = ["ISO-10303-21;", "HEADER;", "FILE_DESCRIPTION (( 'STEP AP214' ),", "    '1' );",
             f"FILE_NAME ('{name}',", "    '2026-11-18T22:10:05', ( 'an author' ), ( 'an organisation; with a semicolon' ),",
             "    'SwSTEP 2.0', 'SolidWorks 2026', '' );", f"FILE_SCHEMA (( '{schema}' ));", "ENDSEC;", "", "DATA;"]
    n = 1
    lines.append(f"#{n} = PRODUCT ( 'MANIFOLD_SOLID_BREP( in a name', 'x', '', ( #2 ) ) ;")
    n += 1
    lines.append(f"#{n} = {unit} ;")
    for _ in range(solids):
        n += 1
        lines.append(f"#{n} = MANIFOLD_SOLID_BREP ( 'Body', #{n + 1} ) ;")
        n += 1
        lines.append(f"#{n} = CLOSED_SHELL ( 'NONE', ( #1 ) ) ;")
    for _ in range(max(0, closed - solids)):
        n += 1
        lines.append(f"#{n} = CLOSED_SHELL ( 'NONE', ( #1 ) ) ;")
    for _ in range(open_shells):
        n += 1
        lines.append(f"#{n} = OPEN_SHELL ( 'NONE', ( #1 ) ) ;")
    for _ in range(surface):
        n += 1
        lines.append(f"#{n} = SHELL_BASED_SURFACE_MODEL ( 'NONE', ( #1 ) ) ;")
    for x, y, z in points:
        n += 1
        lines.append(f"#{n} = CARTESIAN_POINT ( 'NONE',  ( {x!r}, {y!r},")
        lines.append(f"  {z!r} ) ) ;")
        n += 1
        lines.append(f"#{n} = VERTEX_POINT ( 'NONE', #{n - 1} ) ;")
    if extra:
        n += 1
        lines.append(f"#{n} = {extra} ;")
    lines += ["ENDSEC;", end]
    return "\r\n".join(lines) + "\r\n"


def self_check():
    bad = []

    def ok(cond, what):
        print(("ok      " if cond else "FAIL    ") + what)
        if not cond:
            bad.append(what)

    good = _step()
    f = step_facts(good)
    ok(f["frame"] and f["schema"] == "AUTOMOTIVE_DESIGN" and f["ap"] == "AP214" and f["solids"] == 1
       and f["closed_shells"] == 1 and not f["open_shells"] and not f["surface_models"], "a good AP214 file reads whole")
    ok(f["unit"] == "MILLI.METRE" and f["mm_per_unit"] == 1.0, "the complex SI unit reads millimetres")
    ok(abs(f["max_radius_mm"] - 16.5) < 1e-12 and abs(f["axial_extent_mm"] - 8.0) < 1e-12 and f["vertices"] == 3,
       "the vertices give the largest radius from Z and the axial extent")
    ok(file_reasons(f) == [], "a good file passes the frame check")
    ok("FRAME" in file_reasons(step_facts(_step(end="END-ISO-10303-21"))), "a file cut before its last semicolon: FRAME")
    ok("FRAME" in file_reasons(step_facts(good[len("ISO-10303-21;"):])), "a file with no opening line: FRAME")
    for schema, ap in (("CONFIG_CONTROL_DESIGN", "AP203"),
                       ("AP203_CONFIGURATION_CONTROLLED_3D_DESIGN_OF_MECHANICAL_PARTS_AND_ASSEMBLIES_MIM_LF "
                        "{ 1 0 10303 403 3 1 4 }", "AP203"),
                       ("AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF { 1 0 10303 442 1 1 4 }", "AP242"),
                       ("automotive_design", "AP214")):
        ok(step_facts(_step(schema=schema))["ap"] == ap, f"the schema {schema.split()[0][:40]} is {ap} by its prefix")
    for schema in ("AP209_MULTIDISCIPLINE_ANALYSIS_AND_DESIGN_MIM_LF", "IGES_SOMETHING", ""):
        ok("SCHEMA" in file_reasons(step_facts(_step(schema=schema))), f"the schema {schema[:30]!r} is refused")
    ok(step_facts(_step())["solids"] == 1, "a name inside a string is not counted as an instance")
    ok("SOLIDS" in file_reasons(step_facts(_step(solids=2))), "two solids: SOLIDS")
    ok("SOLIDS" in file_reasons(step_facts(_step(solids=0, closed=0))), "no solid: SOLIDS")
    ok("SOLIDS" in file_reasons(step_facts(_step(solids=0, closed=1))), "a closed shell with no solid: SOLIDS")
    ok("OPEN_SHELL" in file_reasons(step_facts(_step(open_shells=1))), "an open shell: OPEN_SHELL")
    ok("SURFACE_MODEL" in file_reasons(step_facts(_step(surface=1))), "a surface model: SURFACE_MODEL")
    inch = step_facts(_step(unit="( CONVERSION_BASED_UNIT ( 'INCH', #1 ) LENGTH_UNIT ( ) NAMED_UNIT ( #1 ) )",
                            points=((1.0, 0.0, 0.0), (0.0, 0.5, 0.25))))
    ok(inch["unit"] == "INCH" and abs(inch["max_radius_mm"] - 25.4) < 1e-9 and abs(inch["axial_extent_mm"] - 6.35) < 1e-9
       and file_reasons(inch) == [], "an inch file reads, its extents in millimetres")
    metre = step_facts(_step(unit="( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT($,.METRE.) )", points=((0.0165, 0.0, 0.0),
                                                                                              (0.0, 0.0, 0.008))))
    ok(metre["unit"] == "METRE" and abs(metre["max_radius_mm"] - 16.5) < 1e-9, "a metre file reads, scaled")
    ok("UNIT" in file_reasons(step_facts(_step(unit="( CONVERSION_BASED_UNIT ( 'CUBIT', #1 ) LENGTH_UNIT ( ) "
                                                    "NAMED_UNIT ( #1 ) )"))), "a unit it does not know: UNIT")
    ok("UNIT" in file_reasons(step_facts(_step(unit="PRODUCT ( 'no unit', 'x', '', ( #1 ) )"))), "no length unit: UNIT")
    ok("UNIT" in file_reasons(step_facts(_step(extra="( CONVERSION_BASED_UNIT ( 'INCH', #1 ) LENGTH_UNIT ( ) "
                                                     "NAMED_UNIT ( #1 ) )"))), "two length units that differ: UNIT")
    ok(extent_reading(f, 16.5, 8.0)[0] is True and extent_reading(f, 16.5, 8.02)[0] is False
       and extent_reading(f, 16.48, 8.0)[0] is False, "the extent holds to 0.01 mm and not beyond")
    ok(extent_reading(step_facts(_step(points=())), 16.5, 8.0)[0] is None, "no vertex: the extent unread")
    other_name = _step(name="Other name.STEP")
    ok(same_file(good, other_name) and differing(good, other_name) == 0, "two exports differing in FILE_NAME are the same")
    moved = _step(points=((16.5, 0.0, 0.0), (0.0, -16.5, 9.0), (3.0, 4.0, 4.0)))
    ok(not same_file(good, moved) and differing(good, moved) == 1, "a changed vertex is a different file")
    ok(rightness(other_name, good, moved, True) == (True, "the same as its own part's file but for FILE_NAME"),
       "the file is right: its own part's, not the other's")
    ok(rightness(moved, good, moved, True)[0] is False, "the other part's file is wrong")
    ok(rightness(other_name, good, moved, False)[0] is None, "a failed determinism control: cannot tell")
    renumbered = good.replace("#1 = PRODUCT", "#99 = PRODUCT").replace("( #1 )", "( #99 )")
    ok(rightness(renumbered, good, moved, True)[0] is None, "numbering differs, geometry the same: cannot tell")
    ok(rightness(_step(points=((20.0, 0.0, 0.0),)), good, None, True)[0] is False, "another geometry: wrong")
    ok(rightness(None, good, None, True)[0] is None, "a file not read: cannot tell")
    clean_doc = {"path": "f2-export\\Gear.SLDPRT", "title": "Gear.SLDPRT", "flag": False}
    clean = {"read": {"returned": True, "errors": 0, "warnings": 0, "on_disk": True, "size": 5000},
             "before": {"doc": clean_doc, "active": "Gear.SLDPRT", "folder": {"Gear.SLDPRT": False},
                        "users": {"<user document 1>": True}},
             "after": {"doc": dict(clean_doc), "active": "Gear.SLDPRT", "folder": {"Gear.SLDPRT": False},
                       "users": {"<user document 1>": True}}, "dialogs": [], "facts": f}
    ok(export_reasons(clean) == [], "a clean export has nothing to say")

    def with_(path, value):
        d = {k: (dict(v) if isinstance(v, dict) else v) for k, v in clean.items()}
        d["before"] = {k: (dict(v) if isinstance(v, dict) else v) for k, v in clean["before"].items()}
        d["after"] = {k: (dict(v) if isinstance(v, dict) else v) for k, v in clean["after"].items()}
        target = d
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        return d
    for path, value, said in ((("read", "returned"), False, "SaveAs answered False"),
                              (("read", "returned"), (True, 0, 0), "a tuple answered"),
                              (("read", "errors"), 1, "errors 1"), (("read", "warnings"), 2, "warnings 2"),
                              (("read", "errors"), "unread: x", "an error code not read"),
                              (("read", "on_disk"), False, "no file"), (("read", "size"), 0, "an empty file"),
                              (("dialogs",), [{"caption": "x"}], "a window"),
                              (("after", "doc", "path"), "f2-export\\print\\Gear.step", "a rename (path)"),
                              (("after", "doc", "title"), "Gear.step", "a rename (title)"),
                              (("after", "doc", "flag"), True, "the flag turned on"),
                              (("before", "doc", "flag"), True, "the flag on before: a mark could not show"),
                              (("after", "active"), "Other.SLDPRT", "the active document changed"),
                              (("after", "folder"), {"Gear.SLDPRT": True}, "a folder document marked"),
                              (("after", "users"), {"<user document 1>": True, "<user document 2>": True},
                               "a document come open, marked, during the export"),
                              (("after", "users"), {}, "a user document gone")):
        reasons = export_reasons(with_(path, value))
        ok(bool(reasons), f"an export with {said} is not clean: {reasons}")
    ok(save_as_copy_proposal({"swSaveAsOptions_Silent": 1, "swSaveAsOptions_Copy": 2}, 1) == 2, "Copy 2 proposed")
    ok(save_as_copy_proposal({"swSaveAsOptions_Silent": 4, "swSaveAsOptions_Copy": 2}, 1) is None,
       "Silent not the app's 1: the control fails, nothing proposed")
    ok(save_as_copy_proposal({"swSaveAsOptions_Silent": 1}, 1) is None and save_as_copy_proposal({}, 1) is None,
       "no Copy member, or no enumeration: None")
    spur_ok = dict(clean, extent_holds=True)
    ok(step_export_proposal(spur_ok, clean)[0] is True, "STEP_EXPORT: both clean, the spur's size holding")
    ok(step_export_proposal(spur_ok, dict(clean, extent_holds=False))[0] is True,
       "STEP_EXPORT: the helical's extent is a fact, not a condition")
    ok(step_export_proposal(dict(clean, extent_holds=False), clean)[0] is None,
       "S1: the spur's file of the wrong size: None")
    ok(step_export_proposal(clean, clean)[0] is None, "S1: the spur's size not read: None")
    ok(step_export_proposal(spur_ok, with_(("read", "errors"), 1))[0] is None, "STEP_EXPORT: a code on the helical: None")
    ok(step_export_proposal(spur_ok, dict(clean, facts=step_facts(_step(solids=2))))[0] is None,
       "STEP_EXPORT: a file of two solids: None")
    ok(step_export_proposal(spur_ok, {"stop": "a dialog"})[0] is None and step_export_proposal(None, clean)[0] is None,
       "STEP_EXPORT: a STOP or a step not run: None")
    right = (True, "right")
    ok(needs_active_proposal(dict(clean, right=right)) == (False, "right"), "NEEDS_ACTIVE: right and clean: False")
    ok(needs_active_proposal(dict(clean, right=(False, "it is the other part's file")))[0] is True,
       "NEEDS_ACTIVE: the other part's file: True")
    ok(needs_active_proposal(dict(with_(("after", "active"), "Gear.SLDPRT"), right=right))[0] is False,
       "NEEDS_ACTIVE: the active document as it was")
    ok(needs_active_proposal(dict(with_(("after", "active"), "Other.SLDPRT"), right=right))[0] is True,
       "NEEDS_ACTIVE: the export activated another document: True")
    ok(needs_active_proposal(dict(clean, right=(None, "control")))[0] is None, "NEEDS_ACTIVE: cannot tell: None")
    ok(needs_active_proposal(dict(with_(("dialogs",), [1]), right=right))[0] is None, "NEEDS_ACTIVE: a window: None")
    ok(needs_active_proposal({"stop": "x"})[0] is None, "NEEDS_ACTIVE: a STOP: None")
    asm = {"path": "f2-component\\Pair.SLDASM", "title": "Pair.SLDASM", "flag": False}
    comp = dict(clean, controls_ok=True, found=True, state_before=2, state_after=2, right=right,
                light={"found": False}, asm_before=asm, asm_after=dict(asm))
    ok(from_component_proposal(comp)[0] is True, "FROM_COMPONENT: reached, clean, right, lightweight not reached: True")
    ok(from_component_proposal(dict(comp, light={"found": True, "right": right}))[0] is True,
       "FROM_COMPONENT: the lightweight one reached and right: True")
    ok(from_component_proposal(dict(comp, light={"found": True, "right": (False, "wrong")}))[0] is False,
       "FROM_COMPONENT: the lightweight one reached and wrong: False")
    ok(from_component_proposal(dict(comp, light={"found": True, "right": (None, "?")}))[0] is None,
       "FROM_COMPONENT: the lightweight one reached, cannot tell: None")
    ok(from_component_proposal(dict(comp, light={}))[0] is None, "FROM_COMPONENT: the lightweight case not read: None")
    ok(from_component_proposal(dict(comp, controls_ok=False))[0] is None, "FROM_COMPONENT: controls failed: None")
    ok(from_component_proposal(dict(comp, found=False))[0] is False, "FROM_COMPONENT: not reached: False")
    ok(from_component_proposal(dict(comp, state_after=1))[0] is False, "FROM_COMPONENT: the state changed: False")
    ok(from_component_proposal(dict(comp, right=(False, "x")))[0] is False, "FROM_COMPONENT: the wrong file: False")
    ok(from_component_proposal(dict(comp, asm_after=dict(asm, flag=True)))[0] is False,
       "FROM_COMPONENT: the assembly marked: False")
    ok(from_component_proposal(dict(comp, asm_after=dict(asm, title="Pair2.SLDASM")))[0] is False,
       "FROM_COMPONENT: the assembly renamed: False")
    ok(from_component_proposal(dict(comp, asm_before=dict(asm, flag=True), asm_after=dict(asm, flag=True)))[0] is None,
       "FROM_COMPONENT: the assembly marked before: None")
    ok(from_component_proposal(dict(with_(("after", "doc", "flag"), True), controls_ok=True, found=True,
                                    state_before=2, state_after=2, right=right, light={"found": False}))[0] is False,
       "FROM_COMPONENT: the part marked: False")
    ok(from_component_proposal(dict(with_(("before", "doc", "flag"), True), controls_ok=True, found=True,
                                    state_before=2, state_after=2, right=right, light={"found": False}))[0] is None,
       "FROM_COMPONENT: marked before: None")
    beside = {"opened": True, "export_reasons": ["the active document changed: 'Pair.SLDASM' -> 'Gear.SLDPRT'"],
              "assembly_open_after": True, "assembly_flag_before": False, "assembly_flag_after": False,
              "state_before": 2, "state_after": 2, "dialogs": [], "users_turned_on": [], "right": right,
              "light": {"assembly_open_after": True, "beside_right": right, "dialogs": []}}
    ok(open_beside_proposal(beside)[0] is True, "OPEN_BESIDE: clean (open_document's activation is its own): True")
    for key, value, want, said in (("assembly_open_after", False, False, "the assembly closed"),
                                   ("assembly_flag_after", True, False, "the assembly marked"),
                                   ("state_after", 1, False, "the component's state changed"),
                                   ("opened", False, False, "not opened"),
                                   ("right", (False, "x"), False, "the wrong file"),
                                   ("right", (None, "x"), None, "cannot tell the file"),
                                   ("dialogs", [1], None, "a window"),
                                   ("assembly_flag_before", True, None, "marked before"),
                                   ("users_turned_on", ["<user document 1>"], False, "a user document marked"),
                                   ("export_reasons", ["errors 1"], False, "an export code"),
                                   ("light", {}, None, "the lightweight case not read"),
                                   ("light", {"assembly_open_after": False, "beside_right": right}, False,
                                    "lightweight: the assembly closed"),
                                   ("light", {"assembly_open_after": True, "beside_right": (False, "x")}, False,
                                    "lightweight: the wrong file"),
                                   ("light", {"assembly_open_after": True, "beside_right": right, "dialogs": [1]},
                                    None, "lightweight: a window")):
        changed = dict(beside, **{key: value})
        if key == "assembly_flag_before":
            changed["assembly_flag_after"] = value           # marked before and after: unchanged, but unjudgeable
        got = open_beside_proposal(changed)
        ok(got[0] is want, f"OPEN_BESIDE: {said}: {want} ({got[0]})")
    own = [{"Visible": True, "ActiveView": True}, {"Visible": True, "ActiveView": True}]
    comp_only = [{"Visible": False, "ActiveView": False}]
    back = [{"Visible": True, "ActiveView": True}]
    ok(window_proposal(own, comp_only, back) == "Visible", "the window read: Visible first")
    ok(window_proposal(own, [{"Visible": True, "ActiveView": False}], back) == "ActiveView",
       "the window read: ActiveView when Visible reads True on a component")
    ok(window_proposal(own, [{"Visible": True, "ActiveView": True}], back) is None, "neither tells them apart: None")
    ok(window_proposal(own + [{"Visible": None, "ActiveView": True}], comp_only, back) == "ActiveView",
       "an unread Visible is not True")
    ok(window_proposal([], comp_only, back) is None and window_proposal(own, [], back) is None,
       "a list not read: None")
    ok(window_proposal(own, comp_only, []) is None,
       "M1: no part read in its own window but not active: None, whatever the active ones read")
    ok(window_proposal(own, comp_only, [{"Visible": False, "ActiveView": True}]) == "ActiveView",
       "M1: a background part window reading Visible False rules Visible out")
    ok(window_proposal(own, comp_only, [{"Visible": False, "ActiveView": False}]) is None,
       "M1: a background part window read as a component by both: None")
    ok(users_changed({"<user document 1>": False}, {"<user document 1>": False}) == [], "the user's documents as they were")
    ok(users_changed({"<user document 1>": False}, {"<user document 1>": True}) != []
       and users_changed({"<user document 1>": False}, {}) != []
       and users_changed({}, {"<user document 2>": False}) != [], "a user document marked, closed or opened is said")
    ok(propose("STEP_EXPORT_ON_2026", True, "p:12") == "propose STEP_EXPORT_ON_2026 = True  # p:12", "propose's form")
    try:
        sys.path.insert(0, os.path.join(REPO, "src"))
        from gear_generator import printout
    except Exception as exc:  # noqa: BLE001 - the probe's own copy then stands alone
        print(f"note    the app's source is not importable here ({type(exc).__name__}), so STEP_SCHEMAS is not compared")
    else:
        ok(tuple(STEP_SCHEMAS) == tuple(printout.STEP_SCHEMAS) and EXTENT_TOL == printout.EXTENT_TOL,
           "the probe's schemas and extent tolerance are printout's")
    print(f"done    {len(bad)} failed")
    return 0 if not bad else 1


if SELF_CHECK:
    raise SystemExit(self_check())



# -- the live run: W9a's harness, through W9c's probes ------------------------------------------------------------

sys.path.insert(0, HERE)
import w9c_probes as C  # noqa: E402  (W9a's harness, the watch, swconst, in_build)

A, W = C.A, C.W
from gear_generator import findings, store, swbuild, swcom  # noqa: E402
from gear_generator.gears import kind_for, plan_for  # noqa: E402
from gear_generator.gears import pair as pairs  # noqa: E402
from gear_generator.gears.spur import FACE_WIDTH  # noqa: E402
from gear_generator.spec import MODE_PAIR, GearSpec, PairSpec, pair_stems  # noqa: E402
from gear_generator.swcom import call  # noqa: E402

say, check = W.say, W.check
OUT = W.OUT
run, part, new, _plain = C.run, C.part, C.new, C._plain
WW_CLOSE_FLAG = "--close-outlived-whats-wrong"      # W9c's flag, its own path (w9c_demonstration.close_outlived_on)
BUILD_WAIT = 900.0
CHANGED_FACE = "9"         # step 8: the spur's Face Width global changed from 8, not saved

# The parts, printed, each built by the app's own route into the section's folder (PLAN-PRINTED §3.1.2).
SPUR = GearSpec(kind="spur", module="1.5", teeth="20", face_width="8", bore="", process="printed")
HELICAL = GearSpec(kind="helical", module="2", teeth="20", helix_angle="15", face_width="10", bore="",
                   process="printed")
PINION = GearSpec(kind="spur", module="1.5", teeth="25", face_width="8", bore="", process="printed")
WHEEL = GearSpec(kind="spur", module="1.5", teeth="50", face_width="8", bore="", process="printed")
ENUMS_F2 = {}
BACKGROUND = []            # window reads of a part open in its own window but not active (steps 6 and 7d; M1)


def year():
    return swcom.release_year(W.TAG["major"]) if W.TAG.get("major") else None


def suggest(name, value, evidence, per_version=True):
    """A finding proposed in the log and the JSON (the year of the running SolidWorks on its name), never set."""
    key = f"{name}_ON_{year()}" if per_version else name
    A.RESULT["proposal"][key] = value
    A.RESULT["proposal"][f"{key}_evidence"] = evidence
    say(propose(key, value, evidence))


def rel(path):
    """A path as the log may hold it: relative to this run's output folder, never the account's folders."""
    if not path:
        return ""
    return os.path.relpath(path, OUT) if W.under(path, OUT) else "<elsewhere>"


def clean(text):
    """A sentence of the app's with this run's folder taken out of it."""
    return str(text).replace(OUT, "<out>")


def label_of(doc):
    """This run's document by its file name; any other as W8's open_titles names it, <user document N>."""
    path = str(call(doc, "GetPathName") or "")
    if W.ours(path):
        return os.path.basename(path)
    title = str(call(doc, "GetTitle"))
    return W.USERS.setdefault(path or title, f"<user document {len(W.USERS) + 1}>")


def user_flags(s):
    """Every open document not made by this run: its GetSaveFlag, by its <user document N> name (read only)."""
    return {label_of(d): bool(call(d, "GetSaveFlag")) for d in W.documents(s._app)  # noqa: SLF001
            if not W.ours(str(call(d, "GetPathName") or ""))}


def doc_at(s, path):
    """The open document of ``path`` by the walk ``Session.use_open_document`` makes (GetFirstDocument / GetNext), or
    None."""
    for d in W.documents(s._app):  # noqa: SLF001
        if store.same_path(str(call(d, "GetPathName") or ""), path):
            return d
    return None


def doc_read(doc):
    return None if doc is None else {"path": rel(str(call(doc, "GetPathName") or "")),
                                     "title": str(call(doc, "GetTitle")), "flag": bool(call(doc, "GetSaveFlag"))}


def window_read(doc):
    """PART_WINDOW_READ's candidates on one document: ``Visible`` as read, ``ActiveView`` whether one is there."""
    out = {}
    if doc is None:
        return None
    for name in WINDOW_READS:
        try:
            value = swcom._read(doc, name)  # noqa: SLF001
        except Exception as exc:  # noqa: BLE001 - unread is said, never taken as either answer
            out[name] = f"unread: {type(exc).__name__}"
            continue
        out[name] = _plain(value) if name == "Visible" else value is not None
    return out


def bracket(s, folder, path=None):
    """The reads around a step: the document of ``path`` (its path, title and flag), the active document, every
    document of the folder's flags, the user's documents' flags."""
    active = call(s._app, "ActiveDoc")  # noqa: SLF001
    return {"active": None if active is None else label_of(active), "folder": W.folder_flags(s, folder),
            "users": user_flags(s), "doc": doc_read(doc_at(s, path)) if path else None}


def reached(s, key):
    """``ISldWorks.GetOpenDocumentByName(key)``: the document it gives (path, title, flag, window reads), or None."""
    try:
        doc = call(s._app, "GetOpenDocumentByName", key)  # noqa: SLF001
    except Exception as exc:  # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {clean(exc)}"}
    if doc is None:
        return None
    return dict(doc_read(doc), window=window_read(doc))


def typelib_enums(names):
    """Enumerations of the running install's swconst.tlb (beside its sldworks.exe, found from the attached PID), as
    W9d's probes read theirs; one missing is simply absent."""
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
    out = {}
    for index in range(lib.GetTypeInfoCount()):
        name = lib.GetDocumentation(index)[0]
        if name in names:
            info = lib.GetTypeInfo(index)
            out[name] = {str(info.GetNames(info.GetVarDesc(i).memid)[0]): int(info.GetVarDesc(i).value)
                         for i in range(info.GetTypeAttr().cVars)}
    return out


def code_names(code, enum):
    """A save error or warning code by the members of its enumeration whose bits it holds."""
    if not isinstance(code, int) or not enum:
        return []
    return sorted(n for n, v in enum.items() if v and code & v == v)


def save_as_step(doc, path):
    """The export as package B's ``export_step`` would make it: ``IModelDocExtension.SaveAs(path, 0, Silent | Copy, null,
    out errors, out warnings)`` on ``doc``. What it answered (plainly or as a tuple), both codes (the by-reference
    values, or a tuple's tail), the seconds, and the file on disk."""
    errors, warnings = swcom._out_long(), swcom._out_long()  # noqa: SLF001
    options = ENUMS_F2["silent"] | ENUMS_F2["copy"]
    began = time.monotonic()
    got = call(call(doc, "Extension"), "SaveAs", path, 0, options, swcom._null_dispatch(), errors,  # noqa: SLF001
               warnings)
    seconds = round(time.monotonic() - began, 3)

    def value(v):
        try:
            return int(v.value)
        except Exception as exc:  # noqa: BLE001
            return f"unread: {type(exc).__name__}"
    out = {"options": options, "seconds": seconds, "form": "tuple" if isinstance(got, tuple) else "plain",
           "returned": _plain(got[0] if isinstance(got, tuple) else got), "errors": value(errors),
           "warnings": value(warnings)}
    if isinstance(got, tuple):
        out["tail"] = [_plain(v) for v in got[1:]]
        if len(got) >= 3 and all(isinstance(v, int) and not isinstance(v, bool) for v in got[1:3]):
            out["errors"], out["warnings"] = int(got[1]), int(got[2])
    out["on_disk"] = os.path.isfile(path)
    out["size"] = os.path.getsize(path) if out["on_disk"] else 0
    out["mtime"] = os.path.getmtime(path) if out["on_disk"] else None
    out["error_names"] = code_names(out["errors"], ENUMS_F2.get("errors"))
    out["warning_names"] = code_names(out["warnings"], ENUMS_F2.get("warnings"))
    return out


def read_text(path):
    try:
        with open(path, encoding="latin-1") as handle:
            return handle.read()
    except OSError:
        return None


def components_by_file(s):
    """The build assembly's components, each one's file name to its GetSuppression2 (Session.components)."""
    return {os.path.basename(c.path): c.state for c in s.components()}


def component_name(s, path):
    return next((c.name for c in s.components() if store.same_path(c.path, path)), None)


def say_export(label, d):
    r = d["read"]
    say(f"fact    {label}: SaveAs answered {r['returned']!r} ({r['form']}{', tail ' + str(r['tail']) if 'tail' in r else ''})"
        f", errors {r['errors']!r} {r['error_names']}, warnings {r['warnings']!r} {r['warning_names']}, options "
        f"{r['options']}, in {r['seconds']} s; the file {'on disk, %d bytes' % r['size'] if r['on_disk'] else 'NOT on disk'}"
        f"; windows {len(d.get('dialogs') or [])}")
    say(f"        before {d['before']}")
    say(f"        after  {d['after']}")


def say_facts(label, facts, outer_radius=None, face=None):
    holds, what = extent_reading(facts, outer_radius, face) if outer_radius else (None, "not compared")
    ap = facts.get("ap") or "not an accepted AP"
    say(f"fact    {label}: frame {facts.get('frame')}; FILE_SCHEMA {facts.get('schema')} ({ap}); instances {facts.get('instances')}: MANIFOLD_SOLID_BREP {facts.get('solids')}, CLOSED_SHELL "
        f"{facts.get('closed_shells')}, OPEN_SHELL {facts.get('open_shells')}, SHELL_BASED_SURFACE_MODEL "
        f"{facts.get('surface_models')}; length unit {facts.get('unit')} ({facts.get('mm_per_unit')} mm); "
        f"{facts.get('vertices')} vertices; extent {what}: holds {holds}")
    return holds


def stopped(label, exc):
    say(f"STOP    {label}: {clean(exc)}")
    return {"stop": clean(exc)}


def exported(label, work):
    """One export job under W9c's watch: its reads, or a STOP that came and went."""
    try:
        d, dialogs = C.watched(label, work)
    except C.CaseStop as exc:
        return stopped(label, exc)
    d["dialogs"] = dialogs
    say_export(label, d)
    return d


def build_one(label, spec, path):
    """One part by the strip's own route (plan_for, then swbuild.build), saved at ``path``."""
    derived = kind_for(spec).derive(spec)
    plan = plan_for(spec, derived, "", path)
    result = run(f"{label}: built", lambda s: swbuild.build(s, plan), BUILD_WAIT)
    check(result.ok and bool(result.saved) and store.same_path(result.saved, path),
          f"{label}: built and saved by swbuild.build as {rel(path)}: ok {result.ok}, failures "
          f"{[clean(f) for f in result.failures]}")
    return derived


# -- export ---------------------------------------------------------------------------------------------------------


def export_case(folder, part_path, step_path, reach):
    """The job of one export: the part reached (``"active"``: activated first by Session.activate, ActivateDoc3;
    ``"object"``: made the build document by Session.use_open_document, no activation), its bracket, the export, the
    bracket again."""
    def work(s):
        doc = doc_at(s, part_path)
        if doc is None:
            raise AssertionError(f"{rel(part_path)} is not open, so it was not exported")
        if reach == "active":
            s.activate(str(call(doc, "GetTitle")))
        else:
            s.use_open_document(part_path)
            doc = s._doc()  # noqa: SLF001
        before = bracket(s, folder, part_path)
        read = save_as_step(doc, step_path)
        return {"reach": reach, "before": before, "read": read, "after": bracket(s, folder, part_path)}
    return work


def step_constants():
    C.swconst(C.ENUM_NAMES)          # W9c's enumerations, with their positive control (the mate types findings holds)
    got = typelib_enums(("swSaveAsOptions_e", "swFileSaveError_e", "swFileSaveWarning_e"))
    options = got.get("swSaveAsOptions_e") or {}
    say(f"fact    export (1) swconst.tlb: swSaveAsOptions_e Silent {options.get('swSaveAsOptions_Silent')!r}, Copy "
        f"{options.get('swSaveAsOptions_Copy')!r} ({len(options)} members); swFileSaveError_e "
        f"{len(got.get('swFileSaveError_e') or {})} members, swFileSaveWarning_e "
        f"{len(got.get('swFileSaveWarning_e') or {})}")
    value = save_as_copy_proposal(options, findings.SAVE_AS_SILENT)
    suggest("SAVE_AS_COPY", value, f"swSaveAsOptions_e.swSaveAsOptions_Copy from swconst.tlb, Silent read "
            f"{options.get('swSaveAsOptions_Silent')!r} against findings.SAVE_AS_SILENT {findings.SAVE_AS_SILENT}",
            per_version=False)
    if value is None:
        raise AssertionError("swSaveAsOptions_e's Copy could not be read with Silent as the app holds it, so nothing "
                             "is exported")
    ENUMS_F2.update(silent=options["swSaveAsOptions_Silent"], copy=value,
                    errors=got.get("swFileSaveError_e") or {}, warnings=got.get("swFileSaveWarning_e") or {})
    return {"silent": ENUMS_F2["silent"], "copy": value}


def section_export(out):
    say("== export  a printed spur and a printed helical gear built and saved; swSaveAsOptions_e read; each part "
        "exported to STEP as a copy while active, the files read as text; an export onto an existing file; the spur "
        "exported by its own document object while the helical is active; the spur changed, not saved, and exported; "
        "everything closed unsaved")
    new("IModelDocExtension.SaveAs(path.step, 0, Silent | Copy, null, out errors, out warnings) under this app's "
        "session and builds (the macro database, files/04: verified on SolidWorks 2026 by the Airfoil Converter, on the "
        "active part only; never on 2024, on a part not active, or on a modified one); swSaveAsOptions_e, "
        "swFileSaveError_e and swFileSaveWarning_e read from swconst.tlb")
    folder = W.fresh_folder("f2-export")
    prints = os.path.join(folder, "print")
    os.makedirs(prints)
    paths = {"spur": os.path.join(folder, SPUR.stem() + ".SLDPRT"),
             "helical": os.path.join(folder, HELICAL.stem() + ".SLDPRT")}
    files = {k: os.path.join(prints, n) for k, n in (
        ("spur", SPUR.stem() + ".step"), ("helical", HELICAL.stem() + ".step"),
        ("inactive", SPUR.stem() + " inactive.step"), ("modified", SPUR.stem() + " modified.step"))}
    users_start = run("export: the user's documents", user_flags)
    say(f"open    export: the user's documents at the start {users_start or 'none'}")
    texts = {}
    try:
        def built():
            derived = {"spur": build_one("export spur", SPUR, paths["spur"]),
                       "helical": build_one("export helical", HELICAL, paths["helical"])}
            flags = run("export: the folder's flags", lambda s: W.folder_flags(s, folder))
            check(flags and not any(flags.values()), f"export: both parts saved and unmarked after their builds: {flags}")
            return {k: {"outer_radius": float(d.da) / 2.0, "face": float(d.face_width)} for k, d in derived.items()}
        sizes = part(out, "built", "export: the parts", built)
        part(out, "constants", "export (1) swSaveAsOptions_e", step_constants)

        def one(key, label):
            d = exported(label, export_case(folder, paths[key], files[key], "active"))
            text = read_text(files[key]) if not d.get("stop") else None
            texts[key] = text
            if text is not None:
                d["facts"] = step_facts(text)
                d["extent_holds"] = say_facts(f"{label}, the file", d["facts"], sizes[key]["outer_radius"],
                                              sizes[key]["face"])
            reasons = export_reasons(d) if not d.get("stop") else [d["stop"]]
            say(f"fact    {label}: {'a clean export' if not reasons else 'not clean: ' + '; '.join(reasons)}")
            return d
        spur = part(out, "spur", "export (2, 3) the spur, active", lambda: one("spur", "export (2) the spur"),
                    needs=("built", "constants"))
        helical = part(out, "helical", "export (4) the helical, active", lambda: one("helical", "export (4) the helical"),
                       needs=("built", "constants"))
        value, why = step_export_proposal(spur, helical)
        suggest("STEP_EXPORT", value, "steps 2-4: " + ("both exports clean and both files whole" if value else
                                                       "; ".join(why)))

        def overwrite():
            before = os.path.getmtime(files["spur"]) if os.path.isfile(files["spur"]) else None
            d = exported("export (5) the spur again onto its file", export_case(folder, paths["spur"], files["spur"],
                                                                                   "active"))
            if d.get("stop"):
                return d
            text = read_text(files["spur"])
            texts["again"] = text
            d["overwrote"] = d["read"]["mtime"] is not None and before is not None and d["read"]["mtime"] != before
            d["control"] = text is not None and texts.get("spur") is not None and same_file(text, texts["spur"])
            say(f"fact    export (5): the existing file {'was overwritten' if d['overwrote'] else 'was NOT overwritten'}"
                f" (its time before {before}, after {d['read']['mtime']}); the text the same as (2)'s but for "
                f"FILE_NAME: {d['control']} ({differing(text, texts['spur']) if text and texts.get('spur') else '?'} "
                "statements differ): the control step 6's comparison rests on")
            return d
        again = part(out, "again", "export (5) onto an existing file", overwrite, needs=("spur",))

        def inactive():
            run("export (6): the helical made active", lambda s: s.activate(str(call(doc_at(s, paths["helical"]),
                                                                                      "GetTitle"))))
            seen = run("export (6): the spur's window read, the helical active",
                       lambda s: (window_read(doc_at(s, paths["spur"])), label_of(call(s._app, "ActiveDoc"))))  # noqa: SLF001
            BACKGROUND.append(dict(seen[0] or {}, what=f"the spur in its own window, {seen[1]} active"))
            say(f"fact    export (6): the spur's window read with {seen[1]} active: {seen[0]} (M1)")
            d = exported("export (6) the spur by its own object, the helical active",
                         export_case(folder, paths["spur"], files["inactive"], "object"))
            if d.get("stop"):
                return d
            text = read_text(files["inactive"])
            d["right"] = rightness(text, texts.get("spur"), texts.get("helical"), (again or {}).get("control", False))
            say(f"fact    export (6): the file is the spur's own: {d['right'][0]} ({d['right'][1]})")
            return d
        step6 = part(out, "inactive", "export (6) a part not active", inactive, needs=("spur", "helical"))
        value, why = needs_active_proposal(step6)
        suggest("STEP_EXPORT_NEEDS_ACTIVE", value, f"step 6: {why}")

        def modified():
            def change(s):
                s.use_open_document(paths["spur"])
                s.set_global_variable(FACE_WIDTH, CHANGED_FACE)
                s.rebuild()
                return bool(call(s._doc(), "GetSaveFlag"))  # noqa: SLF001
            flag = run("export (8): the spur's Face Width set to 9 and rebuilt, not saved", C.in_build(change))
            say(f"fact    export (8): the spur's flag after the change {flag}")
            d = exported("export (8) the spur, changed and not saved", export_case(folder, paths["spur"],
                                                                                    files["modified"], "active"))
            if d.get("stop"):
                return d
            text = read_text(files["modified"])
            facts = step_facts(text) if text else {}
            d["facts"] = facts
            b, a = d["before"]["doc"] or {}, d["after"]["doc"] or {}
            d["held"] = {"flag_stays_on": bool(b.get("flag")) and bool(a.get("flag")),
                         "path_unchanged": b.get("path") == a.get("path"),
                         "differs_from_saved": bool(text and texts.get("spur")) and not same_file(text, texts["spur"]),
                         "axial_extent_mm": facts.get("axial_extent_mm")}
            say(f"fact    export (8): {d['held']} (the changed solid's face is {CHANGED_FACE} mm; the app refuses an "
                "unsaved part by ruling, whatever this shows)")
            return d
        part(out, "modified", "export (8) a modified part", modified, needs=("spur",))
    finally:
        closing(out, "export", folder, users_start)


def closing(out, section, folder, users_start):
    """Step 9: everything of the section's folder closed unsaved (QuitDoc) under the watch, then the user's documents
    held to the section's start."""
    if W.HUNG["on"]:
        say(f"close   {section}: the worker is hung; nothing is closed")
        return
    try:
        left, dialogs = C.watched(f"{section} (9) closed unsaved", W.quit_in(folder))
        check(not left, f"{section} (9): every document of its folder closed unsaved, no window: left {left}")
    except C.CaseStop as exc:
        out["close"] = stopped(f"{section} (9)", exc)
    users_end = run(f"{section}: the user's documents", user_flags)
    changed = users_changed(users_start, users_end)
    check(not changed, f"{section}: the user's documents as at the section's start: {changed or 'all'}")



# -- component ------------------------------------------------------------------------------------------------------


def section_component(out):
    say("== component  a printed pair 25 / 50 built fixed by the form's pair route and closed; its assembly opened "
        "alone, so its parts are loaded only as components; GetOpenDocumentByName and the window reads; (7a) the gear "
        "exported by the object GetOpenDocumentByName gives, no activation; (7b) the fallback, opened beside, exported, "
        "closed by CloseDoc; (7c) the same with the gear's component lightweight; (7d) the gear alone, the reference "
        "files; everything closed unsaved")
    new("ISldWorks.GetOpenDocumentByName (the macro database: unverified; never called by the app); IModelDoc2.Visible "
        "and ActiveView on a document loaded only as a component; IModelDocExtension.SaveAs on such a document; "
        "CloseDoc on a part's own window while an open assembly holds it")
    if not ENUMS_F2:
        step_constants()
    folder = W.fresh_folder("f2-component")
    prints = os.path.join(folder, "print")
    os.makedirs(prints)
    stems = pair_stems(PairSpec(mode=MODE_PAIR, gear_a=PINION, gear_b=WHEEL))
    pin_path, gear_path = (os.path.join(folder, s + ".SLDPRT") for s in stems[:2])
    asm_path = os.path.join(folder, stems[2] + ".SLDASM")
    absent = os.path.join(folder, "F2NotOpen.SLDPRT")              # no such file: GetOpenDocumentByName's control
    files = {k: os.path.join(prints, f"{stems[1]} {k}.step") for k in (
        "component", "beside", "light object", "light beside", "alone", "alone again")}
    files["pinion"] = os.path.join(prints, f"{stems[0]} alone.step")
    users_start = run("component: the user's documents", user_flags)
    say(f"open    component: the user's documents at the start {users_start or 'none'}")
    windows = {"own": [], "component_only": []}
    texts = {}
    try:
        def built():
            plans = [plan_for(spec, kind_for(spec).derive(spec), "", p) for spec, p in ((PINION, pin_path),
                                                                                         (WHEEL, gear_path))]
            assembly = pairs.assembly_plan(PINION, WHEEL, pin_path, gear_path, "", asm_path)
            result = run("component: the pair built", lambda s: swbuild.build_pair(s, plans[0], plans[1], assembly),
                         2 * BUILD_WAIT)
            ok = bool(result.ok and result.assembly is not None and result.assembly.ok)
            check(ok and all(os.path.isfile(p) for p in (pin_path, gear_path, asm_path)),
                  f"component: the pair built and saved by swbuild.build_pair ({', '.join(stems)}): ok {result.ok}, "
                  f"skipped {clean(result.skipped)!r}")
            left, _ = C.watched("component: the pair's documents closed (all saved by the build)", W.quit_in(folder))
            check(not left, f"component: the pair's documents closed: left {left}")
            return {"stems": list(stems)}
        part(out, "built", "component: the pair", built)

        def loaded():
            def work(s):
                s.open_document(asm_path)          # the app's route: OpenDoc6, then ActivateDoc3
                asm = doc_at(s, asm_path)
                docs = {rel(p): window_read(doc_at(s, p)) for p in (asm_path, pin_path, gear_path)}
                return {"bracket": bracket(s, folder, asm_path), "components": components_by_file(s),
                        "walk": {rel(p): doc_at(s, p) is not None for p in (pin_path, gear_path)}, "windows": docs,
                        "by_path": {"gear": reached(s, gear_path), "pinion": reached(s, pin_path),
                                    "no such file": reached(s, absent)},
                        "by_file_name": {"gear": reached(s, os.path.basename(gear_path))},
                        "assembly": doc_read(asm)}
            try:
                d, _ = C.watched("component: the assembly opened alone", C.in_build(work))
            except C.CaseStop as exc:                 # the steps after it need the assembly as opened: they are skipped
                stopped("component: the assembly opened alone", exc)
                raise AssertionError("a window came while the assembly opened, so its steps are not run") from None
            say(f"fact    component: the assembly opened: {d['assembly']}; its components' states {d['components']}; "
                f"the document walk reaches {d['walk']}")
            say(f"fact    component: the window reads {d['windows']}")
            say(f"fact    component: GetOpenDocumentByName by path {d['by_path']}; by file name only "
                f"{d['by_file_name']}")
            windows["own"].append(dict(d["windows"][rel(asm_path)] or {}, what="the assembly, active"))
            for p, key in ((pin_path, "pinion"), (gear_path, "gear")):
                seen = d["windows"][rel(p)] or ((d["by_path"].get(key) or {}).get("window") if isinstance(
                    d["by_path"].get(key), dict) else None)     # the walk's document, else GetOpenDocumentByName's
                windows["component_only"].append(dict(seen or {}, what=f"{rel(p)}, a component only"))
            check(not d["assembly"]["flag"], f"component: the assembly opened unmarked: {d['assembly']}")
            return d
        load = part(out, "loaded", "component: the assembly opened alone", loaded, needs=("built",))

        def component():
            def work(s):
                s.use_open_document(asm_path)
                state_before = components_by_file(s).get(os.path.basename(gear_path))
                asm_before = doc_read(doc_at(s, asm_path))
                doc = call(s._app, "GetOpenDocumentByName", gear_path)  # noqa: SLF001
                found = doc is not None and store.same_path(str(call(doc, "GetPathName") or ""), gear_path)
                before = bracket(s, folder, gear_path)
                before["walk_doc"], before["doc"] = before["doc"], doc_read(doc) if found else None
                read = save_as_step(doc, files["component"]) if found else {}
                after = bracket(s, folder, gear_path)
                after["walk_doc"], after["doc"] = after["doc"], doc_read(doc) if found else None
                asm_after = doc_read(doc_at(s, asm_path))
                s.use_open_document(asm_path)
                return {"found": found, "state_before": state_before, "asm_before": asm_before, "before": before,
                        "read": read, "after": after, "asm_after": asm_after,
                        "state_after": components_by_file(s).get(os.path.basename(gear_path))}
            d = exported("component (7a) the gear by GetOpenDocumentByName, no activation", work)
            if not d.get("stop"):
                say(f"fact    component (7a): reached {d['found']}; the assembly {d['asm_before']} -> {d['asm_after']}; "
                    f"the gear's component state {d['state_before']} -> {d['state_after']}")
            return d
        step7a = part(out, "component", "component (7a)", component, needs=("loaded",))

        def beside():
            def work(s):
                s.use_open_document(asm_path)
                state_before = components_by_file(s).get(os.path.basename(gear_path))
                asm_before = doc_read(doc_at(s, asm_path))
                users_before = user_flags(s)
                info = s.open_document(gear_path)            # the fallback: OpenDoc6 (warning 128), then ActivateDoc3
                doc = s._doc()  # noqa: SLF001
                opened = store.same_path(info.path, gear_path)
                win_open = {"gear": window_read(doc), "assembly": window_read(doc_at(s, asm_path))}
                before = bracket(s, folder, gear_path)
                read = save_as_step(doc, files["beside"])
                after = bracket(s, folder, gear_path)
                title = str(call(doc, "GetTitle"))
                s.close_document(title)                       # CloseDoc on the part's own title
                closed = bracket(s, folder, gear_path)
                asm = doc_at(s, asm_path)
                out_ = {"opened": opened, "state_before": state_before, "asm_before": asm_before,
                        "windows_open": win_open, "before": before, "read": read, "after": after, "closed": closed,
                        "assembly_open_after": asm is not None, "asm_after": doc_read(asm),
                        "gear_after_close": {"walk": doc_at(s, gear_path) is not None,
                                             "window": window_read(doc_at(s, gear_path)),
                                             "by_path": reached(s, gear_path)},
                        "users_turned_on": flags_turned_on(users_before, user_flags(s))}
                if asm is not None:
                    s.use_open_document(asm_path)
                    out_["state_after"] = components_by_file(s).get(os.path.basename(gear_path))
                    s.activate(str(call(asm, "GetTitle")))   # the job's put-back: the active document at the start
                    out_["restored"] = bracket(s, folder, asm_path)
                return out_
            d = exported("component (7b) the gear opened beside the assembly, exported, closed", work)
            if d.get("stop"):
                return d
            d["assembly_flag_before"] = (d["asm_before"] or {}).get("flag")
            d["assembly_flag_after"] = (d["asm_after"] or {}).get("flag")
            d["export_reasons"] = export_reasons(d)
            say(f"fact    component (7b): opened {d['opened']}; windows while open {d['windows_open']}; after CloseDoc "
                f"{d['closed']}; the assembly open {d['assembly_open_after']}, {d['asm_before']} -> {d['asm_after']}; "
                f"the component's state {d['state_before']} -> {d.get('state_after')}; the gear after the close "
                f"{d['gear_after_close']}; the assembly activated again {d.get('restored')}")
            windows["own"].append(dict(d["windows_open"]["gear"] or {}, what="the gear opened beside, active"))
            windows["own"].append(dict(d["windows_open"]["assembly"] or {}, what="the assembly, not active"))
            if d["gear_after_close"]["walk"]:
                windows["component_only"].append(dict(d["gear_after_close"]["window"] or {},
                                                      what="the gear after its window closed"))
            return d
        step7b = part(out, "beside", "component (7b)", beside, needs=("loaded",))

        def alone():
            left, _ = C.watched("component (7d) everything closed", W.quit_in(folder))
            check(not left, f"component (7d): the assembly and its parts closed unsaved: left {left}")

            def work(s):
                s.open_document(gear_path)
                doc = s._doc()  # noqa: SLF001
                out_ = {"own": window_read(doc), "by_path_open_alone": reached(s, gear_path),
                        "reads": [save_as_step(doc, files["alone"]), save_as_step(doc, files["alone again"])]}
                s.open_document(pin_path)
                # M1 (F2-0-REVIEW): the gear now open in its own window and not active, the case PART_WINDOW_READ is for
                out_["background"] = window_read(doc_at(s, gear_path))
                out_["active_now"] = label_of(call(s._app, "ActiveDoc"))  # noqa: SLF001
                out_["reads"].append(save_as_step(s._doc(), files["pinion"]))  # noqa: SLF001
                return out_
            d, dialogs = C.watched("component (7d) the gear alone, twice, and the pinion", C.in_build(work))
            left, _ = C.watched("component (7d) closed again", W.quit_in(folder))
            d["by_path_closed"] = run("component (7d) GetOpenDocumentByName on the gear closed",
                                      lambda s: reached(s, gear_path))
            windows["own"].append(dict(d["own"] or {}, what="the gear open alone, active"))
            BACKGROUND.append(dict(d["background"] or {}, what=f"the gear in its own window, {d['active_now']} active"))
            for key in ("alone", "alone again", "pinion", "component", "beside"):
                texts[key] = read_text(files[key]) if os.path.isfile(files[key]) else None
            d["control"] = bool(texts["alone"] and texts["alone again"]) and same_file(texts["alone"],
                                                                                      texts["alone again"])
            facts = step_facts(texts["alone"]) if texts["alone"] else {}
            say_facts("component (7d) the gear alone, the file", facts, float(kind_for(WHEEL).derive(WHEEL).da) / 2.0,
                      float(WHEEL.face_width))
            say(f"fact    component (7d): the gear alone exported twice, the same but for FILE_NAME {d['control']}; "
                f"the pinion's file differs {texts['pinion'] is not None and not same_file(texts['pinion'], texts['alone'] or '')}; "
                f"GetOpenDocumentByName on the gear open alone {d['by_path_open_alone']}, closed {d['by_path_closed']}; "
                f"windows {len(dialogs)}; left {left}")
            return d
        ref = part(out, "alone", "component (7d) the reference files", alone, needs=("built",))
        control = (ref or {}).get("control", False)

        def judged(key):
            return rightness(texts.get(key), texts.get("alone"), texts.get("pinion"), control)
        # 7a's and 7b's own files judged and said before 7c, so a hang there cannot void them (F2-0-REVIEW's S2)
        if step7a and not step7a.get("stop"):
            step7a["right"] = judged("component")
            by = (load or {}).get("by_path") or {}
            step7a["controls"] = {"no such file": by.get("no such file"),
                                  "open alone": (ref or {}).get("by_path_open_alone"),
                                  "closed": (ref or {}).get("by_path_closed")}
            alone_doc = (ref or {}).get("by_path_open_alone") or {}
            step7a["controls_ok"] = (by.get("no such file") is None and (ref or {}).get("by_path_closed") is None
                                     and bool(ref) and alone_doc.get("path") == rel(gear_path))
            say(f"fact    component (7a): the file is the gear's own {step7a['right']}; GetOpenDocumentByName's controls "
                f"{step7a['controls_ok']} {step7a['controls']}; its export {export_reasons(step7a) or 'clean'}")
        if step7b and not step7b.get("stop"):
            step7b["right"] = judged("beside")
            say(f"fact    component (7b): the file is the gear's own {step7b['right']}")
        strip = [{k: v for k, v in w.items() if k != "what"} for w in windows["own"]]
        read = window_proposal(strip, [{k: v for k, v in w.items() if k != "what"} for w in windows["component_only"]],
                               [{k: v for k, v in w.items() if k != "what"} for w in BACKGROUND])
        say(f"fact    component: the window reads, own window {windows['own']}; a part in its own window, not active "
            f"{BACKGROUND}; a component only {windows['component_only']}")
        suggest("PART_WINDOW_READ", WINDOW_ROUTES.get(read), f"steps 6 and 7: {len(windows['own'])} documents in their "
                f"own window, {len(BACKGROUND)} parts in their own window not active, {len(windows['component_only'])} "
                "loaded only as a component; " + (f"{read} tells them apart" if read else
                                                  "neither read tells them apart on every one"))
        out["windows"] = dict(windows, background=list(BACKGROUND))

        def lightweight():
            def work(s):
                s.open_document(asm_path)          # opened again after 7d closed everything (F2-0-REVIEW's S2)
                opened_as = doc_read(doc_at(s, asm_path))
                states = C.swconst(C.ENUM_NAMES)["swComponentSuppressionState_e"]
                light = next(v for k, v in states.items() if k.endswith("Lightweight") and "Fully" not in k)
                resolved = next(v for k, v in states.items() if k.endswith("FullyResolved"))
                name = component_name(s, gear_path)
                comp = swcom.Session._component_by(findings.COMPONENT_FIND_ROUTE, s._doc(), name)  # noqa: SLF001
                call(comp, "SetSuppression2", light)
                out_ = {"opened_as": opened_as, "component": name,
                        "state_set": components_by_file(s).get(os.path.basename(gear_path)),
                        "assembly": doc_read(doc_at(s, asm_path)), "walk": doc_at(s, gear_path) is not None,
                        "by_path": reached(s, gear_path)}
                doc = call(s._app, "GetOpenDocumentByName", gear_path)  # noqa: SLF001
                out_["found"] = doc is not None and store.same_path(str(call(doc, "GetPathName") or ""), gear_path)
                if out_["found"]:
                    out_["object_read"] = save_as_step(doc, files["light object"])
                info = s.open_document(gear_path)            # the not-open path (or the fallback), as the job takes it
                part_doc = s._doc()  # noqa: SLF001
                out_["opened"] = store.same_path(info.path, gear_path)
                out_["beside_read"] = save_as_step(part_doc, files["light beside"])
                s.close_document(str(call(part_doc, "GetTitle")))
                asm = doc_at(s, asm_path)
                out_["assembly_open_after"] = asm is not None
                if asm is not None:
                    s.use_open_document(asm_path)
                    out_["state_after_close"] = components_by_file(s).get(os.path.basename(gear_path))
                    comp = swcom.Session._component_by(findings.COMPONENT_FIND_ROUTE, s._doc(), name)  # noqa: SLF001
                    call(comp, "SetSuppression2", resolved)
                    out_["state_resolved_again"] = components_by_file(s).get(os.path.basename(gear_path))
                    s.activate(str(call(asm, "GetTitle")))
                return out_
            try:
                d, dialogs = C.watched("component (7c) the gear's component lightweight", work)
            except C.CaseStop as exc:
                return stopped("component (7c)", exc)
            d["dialogs"] = dialogs
            say(f"fact    component (7c): the assembly opened again {d['opened_as']}; {d['component']} set lightweight "
                f"reads {d['state_set']}; the assembly then "
                f"{d['assembly']} (marked by the set itself, a fact); the walk reaches it {d['walk']}; "
                f"GetOpenDocumentByName {d['by_path']}; exported by that object {d.get('object_read', 'not reached')}; "
                f"the not-open path: opened {d['opened']}, exported {d['beside_read']}, the assembly open after the "
                f"close {d['assembly_open_after']}, the component's state after {d.get('state_after_close')}, resolved "
                f"again {d.get('state_resolved_again')}; windows {len(dialogs)}")
            return d
        step7c = part(out, "lightweight", "component (7c), last", lightweight, needs=("loaded",))

        for key in ("light object", "light beside"):
            texts[key] = read_text(files[key]) if os.path.isfile(files[key]) else None
        light = step7c or {}
        if step7a and not step7a.get("stop"):
            step7a["light"] = ({"stop": light["stop"]} if light.get("stop") else
                               {"found": light.get("found"), "right": judged("light object")} if light else {})
        value, why = from_component_proposal(step7a)
        suggest("STEP_EXPORT_FROM_COMPONENT", value, f"step 7 (a), (c): {why}")
        if step7b and not step7b.get("stop"):
            step7b["light"] = ({"stop": light["stop"]} if light.get("stop") else
                               {"assembly_open_after": light.get("assembly_open_after"), "dialogs": light.get("dialogs"),
                                "beside_right": judged("light beside")} if light else {})
            say(f"fact    component (7c): beside, the file is the gear's own {step7b['light'].get('beside_right')}")
        value, why = open_beside_proposal(step7b)
        suggest("OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN", value, f"step 7 (b), (c): {why}")
    finally:
        closing(out, "component", folder, users_start)


# -- the run ---------------------------------------------------------------------------------------------------------

ORDER = ["export", "component"]
SECTIONS = {"export": section_export, "component": section_component}
FOLDERS = {"export": ["f2-export"], "component": ["f2-component"]}


def done_here(name):
    """What of a section this <out> holds already (W9a's ``done_here`` for these sections' folders)."""
    return [p for p in (os.path.join(OUT, f) for f in FOLDERS.get(name, [name])) if os.path.exists(p)]


def main():
    A.SECTIONS.clear()
    A.SECTIONS.update(SECTIONS)
    if A._given in ("", "all"):                    # noqa: SLF001
        A.CHOSEN = list(ORDER)
    A.done_here = done_here
    A.RUN_TITLE, A.JSON_STEM = "F2 probes", "f2-probes"
    say(f"findings SAVE_AS_SILENT {findings.SAVE_AS_SILENT}; F2's, each None until a reviewed run sets it: "
        f"{ {n: getattr(findings, n, 'absent') for n in dir(findings) if n == 'SAVE_AS_COPY' or n.startswith(('STEP_EXPORT', 'OPEN_BESIDE', 'PART_WINDOW_READ'))} }")
    if WW_CLOSE_FLAG in A.ARGS:              # off unless the run asks: W9c's own close path, as F1's demonstration
        import w9c_demonstration as WC       # noqa: PLC0415
        WC.close_outlived_on()
    return A.main()


if __name__ == "__main__":
    code = 1
    try:
        code = main()
    finally:
        with open(W.LOG_PATH, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(W.LOG) + "\n")
    raise SystemExit(code)
