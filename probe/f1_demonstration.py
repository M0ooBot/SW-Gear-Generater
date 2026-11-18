r"""F1's demonstration on SolidWorks (PLAN-PRINTED §2.8, *Done when*; F1-REVIEW §4 and §8): a printed spur gear and a
printed pair built through the strip's own build path as its form builds them, each beside a machined one of the same
sizes; and, on a copy of W9a's setup.master (RangeBox with the user's work, built before F1), the gearbox opened as built
(Machined, nothing written, D11's answer (B)), then Printed typed on its Box sheet and one Update SolidWorks, read back as
W9a reads its own Update. The sections, what each line bears out, the masters, the command lines and the times are in
``docs/notes-printed/F1-DEMONSTRATION.md``.

python.exe probe/f1_demonstration.py <repo src> <output folder under C:\> --pid PID [--log FILE]
                                     [--sections spur,pair,rangebox|all] [--user-master <W9a's setup.master>]
                                     [--redo] [--close-outlived-whats-wrong]
python probe/f1_demonstration.py --self-check     (no SolidWorks, no Excel: every judgement below on made-up readings
                                                   and on the app's own figures, each failing way shown; the strip's
                                                   form needs Tk)
python probe/f1_demonstration.py --help

Sections (each runs alone; none needs another's folder):

- ``spur``      the strip's own form (``gui.GearApp``, its link to SolidWorks not started: this run's worker attaches by
                PID) as it opens, Printed, Gear_m1.5_N25_P; then Machined beside it, Gear_m1.5_N25; then both again at
                module 0.8. Each built by the form's own ``_plan_single`` and its job, its record written by the form's
                own ``_finish_single``, then read back from SolidWorks: the file name (_P printed only); the Backlash
                global's text and SolidWorks' value against the app's figure (0.3 above module 1, 0.3 × module at or
                under it); the tooth as small_pinion_check measures it (the volume within 0.1 % of the app's outline,
                the tip corners on the outer radius); at module 1.5 the printed volume told from the machined outline's
                and the other way round, at 0.8 the two volumes equal; the .gear.json at sidecar 3 printed, and the
                machined one as W9 records a machined part (sidecar 1, no process or nozzle, 0.3 * "Module").
- ``pair``      the form's pair (25 / 50, module 1.5, motion "gear mate"), Printed, then Machined: both parts and the
                assembly named with _P (printed only), built by the form's ``_plan_pair`` and ``_finish_pair``; gear A
                driven 10 -> 40 degrees by gear_pairs_check's own ``drive``: gear A turns 30 degrees, gear B -0.5 of it,
                no interference at either end, for both; each part's Backlash as in spur; the sidecars.
- ``rangebox``  a copy of ``--user-master`` (required: W9a's setup.master, built before F1; the script refuses a master
                whose record already says a Process). Opened as built: the blank Process (no row) reads Machined, every
                gear plans machined with no _P, Update has nothing to do, the footer says W9's words for it and nothing
                of Process, the Workbook panel's Process line says to add the row, and nothing is written (the record,
                the .gear.json files, the workbook and every SolidWorks file the same bytes after the open). Then a
                person adds a row labelled Process with Printed beside it, in Excel: the line reads Printed, and
                classify plans one Update in place in which every part changes its Backlash alone (0.3 * "Module" to the
                printed IIF), no structural change, no new part. One Update SolidWorks through the window's own path:
                each part's result changed Backlash alone, nothing made new or inserted, what was carried is what the
                footer foresaw, every put an app body or a sprocket locked to one, nothing of the user's in error, no
                SolidWorks file saved by the app; every part's Backlash read back as the printed IIF evaluating to the
                app's value; every user component, mate and the User Keyway as W9a's go reads them (entities, every mode,
                the locked sprockets on their gears, the keyway's code); the record's parts printed under their old
                names, each .gear.json at sidecar 3; the result's sentence holding, once, package C's sentence about
                the file names keeping no _P. Then saved and closed as the user would, and a second Update with nothing
                changed is quiet (W8's check_quiet_update), without that sentence.

Everything W9a's script does for a run is done here by running its ``main`` with these sections (as W9b's and W9c's
do): the attach by PID and its check, the dialog watch with the What's Wrong rule per version, keep-awake, the JSON
after every section, APPDATA in the run folder, the guarded close, ``--sections`` and ``--redo``. W9c's
``--close-outlived-whats-wrong`` (the coordinator's ruling of 2026-11-18, SolidWorks 2024 only) is W9c's own path,
put in when the flag is given. The rangebox section reads the workbook through ``DeskF1``: W9a's Desk9 with the
Workbook window's own ``_assess`` and ``_blank_process`` (W8's Desk assesses without the window's resolution of a blank
Process, which would read a W9 master Printed). No document title but the run's own is logged.

SolidWorks calls: none new to the repo. The parts are built by ``swbuild.build`` and ``build_pair`` and the gearbox
updated by ``update_gearbox`` as the app does; the reads are W9a's, W9b's (``Session.equations``), small_pinion_check's
(``readings``: the volume, the bodies' vertices, every feature's error code) and gear_pairs_check's (``drive``: an angle
mate on a global, its indexed put, ``interference_count``). Of those, small_pinion_check's readings have a committed
log on SolidWorks 2026 only.
"""

import dataclasses
import hashlib
import json
import math
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SELF_CHECK = "--self-check" in sys.argv

if "--help" in sys.argv or "-h" in sys.argv:
    print(__doc__)
    raise SystemExit(0)

# -- what the plan says, pinned (PLAN-PRINTED §2.1, D10, D11; F1-PACKAGE-B and -C) ------------------------------------

PRINTED_TEXT = 'IIF ( "Module" <= 1 , 0.3 * "Module" , 0.3 )'     # §2.1, spur.printed_backlash_expression()
MACHINED_TEXT = '0.3 * "Module"'                                    # the user's own rule, as every gear before F1
PRINTED_SCHEMA, MACHINED_SCHEMA, LINK_SCHEMA = 3, 1, 11             # §1.2: sidecar 3 printed, 1 machined; link 11
NOZZLE = 0.4
VALUE_TOL = 1e-9           # mm: a global's value against the figure (W9a's go holds Sun's Backlash to 1e-9)
SAME_VOLUME = 1e-6         # relative: two parts of the same geometry (printed and machined at module 0.8)
TURN_TOL = 1e-6            # relative: gear_pairs_check's tolerance on the turn and the ratio
# A machined part's spec in its .gear.json as W9 wrote one (an unbanded part: the bands left out while blank, and
# since F1 the process and nozzle left out while not printed; test_printed_rule pins the bytes on the fake).
W9_SPEC_KEYS = ("kind", "recipe", "module", "teeth", "pressure_angle", "face_width", "bore", "backlash", "fillet",
                "profile_shift", "helix_angle", "hand", "groove", "teeth_side", "rim", "shaft_angle", "mate_teeth",
                "name")
SPUR_MODULES = ("1.5", "0.8")      # one above module 1, one under it (the IIF's two branches; at 1 both give 0.3)
PROCESSES = ("printed", "machined")
PAIR_MOTION = "gear mate"          # spec.MOTION_GEAR_MATE: the form's choice that makes a pair turn
# RangeBox's five parts, as S0's master (and W9's snapshot on the fake, tests/fixtures/printed) names them.
RANGEBOX_PARTS = ("Gear_m1.25_N29", "Gear_m1.25_N13", "Ring_m1.25_N55", "Dog_m1.25_N17", "Sleeve_m1.25_N17")
# W9's footer for a built gearbox opened with nothing changed (W9a's setup, w9a-final-sw2026-20261117.log:241).
FOOTER_AS_BUILT = "SolidWorks already matches the workbook on record"
# The footer before the press, Printed typed (package B's test on W9's snapshot, test_printed_workbook).
FOOTER_PRINTED = ("Update SolidWorks will change the values in Gear_m1.25_N29 (Sun), Gear_m1.25_N13 (Planet), "
                  "Ring_m1.25_N55 (Ring), Dog_m1.25_N17 (HighDog, LowDog) and Sleeve_m1.25_N17 (RangeSlv).")
NOT_IN_FOOTER = ("Process", "printed", "Printed", "_P")
# The Workbook panel's Process line (F1-PACKAGE-C; ui_text.workbook_process_line).
LINE_AS_BUILT = ("Machined, as built: type Printed beside Process on the Box sheet to print it (add a row labelled "
                 "Process)")
LINE_PRINTED = "Printed, 0.4 mm nozzle"
# The per-part clause C took out for Process alone (bc6ec8f): it must not come back on this Update.
STALE_CLAUSE = "which no longer says what it holds"
PROCESS_LABEL, PRINTED_WORD = "Process", "Printed"     # what the person types on the Box sheet
PRESS_FREE_GB = 6.0        # GB free before the rangebox press: 2024's first press costs 3.3 to 4 GB, over the 2 GB floor


def names_sentence(stems):
    """Package C's sentence (bc6ec8f, F1-PACKAGE-C) for default-named parts this Update made printed, as the plan's
    *Done when* asks it be said once: the words written out here, so a change to them in ui_text is seen."""
    stems = list(stems)
    if len(stems) == 1:
        subject, parts = f"{stems[0]}, now printed, keeps its file name", "a new part"
    else:
        subject, parts = f"The {len(stems)} parts now printed keep their file names", "new parts"
    return (f"{subject}, without the _P a part built printed is named with: Update SolidWorks never renames a file, and "
            f"Build again… makes {parts} named with _P if you want the mark.")


# -- the judgements: plain data in, a list of what is wrong out (empty: it holds) ------------------------------------


def squash(text):
    return "".join(str(text).split())


def stem_of(path):
    base = str(path).replace("/", "\\").rsplit("\\", 1)[-1]
    return base.rsplit(".", 1)[0] if "." in base else base


def path_key(path):
    return str(path).replace("/", "\\").lower()


def backlash_wanted(module, printed):
    """§2.1 worked here, not by the app: printed, 0.3 × module at or under module 1, else 0.3; machined, 0.3 × module."""
    m = float(module)
    return (0.3 * m if m <= 1.0 else 0.3) if printed else 0.3 * m


def backlash_judged(equations, module, printed, derived=None):
    """A part's Backlash global as SolidWorks holds it (``Session.equations``: (text, value)): one equation, its text the
    printed IIF or the machined rule (spaces aside, as K11 compares), its value the figure; with ``derived`` (the
    app's own figure), that too."""
    found = [(t, v) for t, v in equations if squash(t).startswith('"Backlash"=')]
    if len(found) != 1:
        return [f"{len(found)} Backlash equations in the part, not one: {found}"]
    text, value = found[0]
    want_text = PRINTED_TEXT if printed else MACHINED_TEXT
    want = backlash_wanted(module, printed)
    out = []
    if squash(text) != squash(f'"Backlash"= {want_text}'):
        out.append(f"its text is {text!r}, not \"Backlash\"= {want_text}")
    if value is None or not abs(float(value) - want) <= VALUE_TOL:
        out.append(f"SolidWorks evaluates it to {value}, not {want:g}")
    if derived is not None and not abs(float(derived) - want) <= VALUE_TOL:
        out.append(f"the app derives {derived}, not {want:g}")
    return out


def stem_judged(path, printed):
    stem = stem_of(path)
    return [] if stem.endswith("_P") == printed else [f"{stem} {'lacks' if printed else 'has'} the _P mark"]


def sidecar_judged(schema, spec, derived, variables, printed):
    """A .gear.json as read (its schema number, spec, derived and variables): printed at sidecar 3 with the process,
    the 0.4 nozzle and the IIF; machined as W9 records a machined part: sidecar 1, the spec's keys W9's, no nozzle."""
    out = []
    want = PRINTED_SCHEMA if printed else MACHINED_SCHEMA
    if schema != want:
        out.append(f"sidecar schema {schema}, not {want}")
    spec, derived, variables = dict(spec or {}), dict(derived or {}), dict(variables or {})
    if printed:
        if spec.get("process") != "printed" or derived.get("nozzle") != NOZZLE:
            out.append(f"spec process {spec.get('process')!r}, derived nozzle {derived.get('nozzle')!r}")
    else:
        if sorted(spec) != sorted(W9_SPEC_KEYS):
            out.append(f"spec keys {sorted(set(spec) ^ set(W9_SPEC_KEYS))} differ from W9's")
        if "nozzle" in derived:
            out.append("derived holds a nozzle")
    if squash(variables.get("Backlash", "")) != squash(PRINTED_TEXT if printed else MACHINED_TEXT):
        out.append(f"its Backlash variable is {variables.get('Backlash')!r}")
    return out


def volume_judged(measured, own, other, tol):
    """The tooth told by its volume: within ``tol`` of the app's outline for its own process, and, where the two
    outlines lie more than twice ``tol`` apart, not within ``tol`` of the other's (else the reading cannot tell them)."""
    out = []
    if not abs(measured - own) <= tol * own:
        out.append(f"{measured:.4f} mm³ is {(measured - own) / own:+.3%} off its own outline's {own:.4f}")
    if abs(own - other) <= 2 * tol * own:
        out.append(f"the two outlines ({own:.4f}, {other:.4f}) lie within twice the tolerance: no telling them apart")
    elif abs(measured - other) <= tol * other:
        out.append(f"{measured:.4f} mm³ is also within {tol:g} of the other process's outline {other:.4f}")
    return out


def same_volume_judged(a, b, tol=SAME_VOLUME):
    return [] if abs(a - b) <= tol * max(abs(a), abs(b)) else [f"{a:.6f} and {b:.6f} mm³ differ by {(a - b) / b:+.2e}"]


def turn_judged(seen, ratio, span):
    """gear_pairs_check's ``drive`` answer: gear 1 turned ``span`` degrees, gear 2 by ``ratio`` of it, no interference
    at either end, gear 1 not fixed."""
    out = []
    t1, t2 = seen["turn"]["gear1"], seen["turn"]["gear2"]
    if not abs(abs(t1) - span) <= TURN_TOL * span:
        out.append(f"gear 1 turned {t1:.6f}°, not {span:g}°")
    got = t2 / t1 if t1 else float("nan")
    if not abs(got - ratio) <= TURN_TOL * abs(ratio):
        out.append(f"gear 2 turned {got:.6f} of gear 1, not {ratio:g}")
    for where in ("interference_at_drive_from", "interference_at_drive_to"):
        count = seen[where][0] if isinstance(seen[where], (list, tuple)) else seen[where]
        if count != 0:
            out.append(f"{where.replace('_', ' ')}: {seen[where]}")
    if seen.get("gear1_fixed"):
        out.append("gear 1 is fixed")
    return out


def as_built_judged(read_process, read_cell, resolved, job_stems, printed_jobs, update):
    """D11 (B), a W9 master opened: the blank Process as read (no row), resolved machined, no gear planned printed or
    named _P, and Update with nothing to do."""
    out = []
    if read_process != "" or read_cell != "":
        out.append(f"the workbook's Process reads {read_process!r} at {read_cell!r}, not blank with no row")
    if resolved != "machined":
        out.append(f"the blank resolves {resolved!r}, not machined")
    marked = [s for s in job_stems if s.endswith("_P")]
    if marked or printed_jobs:
        out.append(f"gears planned printed {printed_jobs} or named _P {marked}")
    if update is None:
        out.append("no Update planned")
    else:
        busy = {k: getattr(update, k) for k in ("refusal", "structural", "missing", "replaced", "moved_shafts")
                if getattr(update, k)}
        changed = [stem_of(p.path) for p in update.changed_parts]
        if busy or changed or not update.record_matches:
            out.append(f"Update has something to do: {busy} changed {changed} matches {update.record_matches}")
    return out


def footer_as_built_judged(text):
    out = [] if text.startswith(FOOTER_AS_BUILT) else [f"the footer begins {text[:80]!r}, not W9's {FOOTER_AS_BUILT!r}"]
    said = [w for w in NOT_IN_FOOTER if w in text]
    if said:
        out.append(f"the footer says {said}")
    return out


def backlash_only_judged(update, entries, expected):
    """Printed typed on a gearbox built machined (§1.3, §6): one Update in place, no structural change or new part,
    every expected part changed, and in each its Backlash alone, from the machined rule to the printed IIF, its file
    keeping its name. ``entries``: the record's current parts, as ``update.parts`` was planned from."""
    if update is None:
        return ["no Update planned"]
    out = []
    busy = {k: getattr(update, k) for k in ("refusal", "structural", "missing", "replaced", "moved_shafts")
            if getattr(update, k)}
    if busy or update.needs_new_revision or bool(getattr(update, "in_place", None)):
        out.append(f"not a plain Update in place: {busy}, in place {getattr(update, 'in_place', None)}")
    changed = sorted(stem_of(p.path) for p in update.changed_parts)
    if changed != sorted(expected):
        out.append(f"the parts changed are {changed}, not {sorted(expected)}")
    by_path = {path_key(e.path): e for e in entries}
    for p in update.parts:
        e = by_path.get(path_key(p.path))
        if e is None:
            out.append(f"{stem_of(p.path)} is not on record")
            continue
        was = {str(n): str(v) for n, v in e.variables}
        now = {v.name: v.expression_for(getattr(e, "trig", "") or "degrees") for v in p.variables}
        diff = [n for n in now if squash(was.get(n, "")) != squash(now[n])]
        if diff != ["Backlash"]:
            out.append(f"{stem_of(p.path)} changes {diff}, not Backlash alone")
        elif squash(was["Backlash"]) != squash(MACHINED_TEXT) or squash(now["Backlash"]) != squash(PRINTED_TEXT):
            out.append(f"{stem_of(p.path)}'s Backlash goes {was['Backlash']!r} -> {now['Backlash']!r}")
        if not p.spec.is_printed() or stem_of(p.path).endswith("_P"):
            out.append(f"{stem_of(p.path)} planned printed {p.spec.is_printed()}, its file renamed")
    return out


def result_parts_judged(parts, expected, layout=None, carriers=()):
    """What the Update wrote, by its own result per document (``UpdateResult.changed``): Backlash alone in each expected
    part, nothing in any other document, the layout or a carrier."""
    out = []
    got = {stem_of(r.document): list(r.changed) for r in parts}
    for stem in expected:
        if got.get(stem) != ["Backlash"]:
            out.append(f"{stem} changed {got.get(stem)}, not ['Backlash']")
    out += [f"{s} changed {c}" for s, c in got.items() if s not in expected and c]
    for r in [layout] + list(carriers):
        if r is not None and list(r.changed):
            out.append(f"{stem_of(r.document)} changed {list(r.changed)}")
    return out


def sentence_judged(text, sentence, absent=()):
    out = []
    count = text.count(sentence)
    if count != 1:
        out.append(f"the sentence is said {count} times, not once: {sentence!r}")
    out += [f"it says {a!r}" for a in absent if a in text]
    return out


def record_judged(schema, entries, before, sidecars):
    """The record after the Update, read from its file: at link 11, the same part files as before (no _P), each part's
    spec printed and its Backlash the IIF; each .gear.json (``sidecars``: stem -> (schema, spec)) at sidecar 3,
    printed."""
    out = []
    if schema != LINK_SCHEMA:
        out.append(f"link schema {schema}, not {LINK_SCHEMA}")
    paths = sorted(path_key(e.path) for e in entries)
    if paths != sorted(path_key(p) for p in before):
        out.append(f"the record's parts {[stem_of(p) for p in paths]} are not the ones before")
    for e in entries:
        stem = stem_of(e.path)
        spec = dict(e.spec or {})
        backlash = dict((str(n), str(v)) for n, v in e.variables).get("Backlash", "")
        if spec.get("process") != "printed" or squash(backlash) != squash(PRINTED_TEXT):
            out.append(f"{stem} on record: process {spec.get('process')!r}, Backlash {backlash!r}")
        car = sidecars.get(stem)
        if car is None or car[0] != PRINTED_SCHEMA or dict(car[1] or {}).get("process") != "printed":
            out.append(f"{stem}.gear.json: {car and (car[0], dict(car[1] or {}).get('process'))}")
    return out


def files_changed(before, after):
    """Two snapshots of a folder's files ({name: (size, mtime_ns, sha256)}): what differs, by name."""
    return sorted(n for n in set(before) | set(after) if before.get(n) != after.get(n))


def snapshot(folder, kinds=(".sldprt", ".sldasm", ".xlsx", ".json")):
    """Every file of ``folder`` of those kinds (Excel's lock files aside): size, mtime and sha256."""
    out = {}
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if name.startswith("~$") or not os.path.isfile(path) or not name.lower().endswith(kinds):
            continue
        with open(path, "rb") as handle:
            digest = hashlib.sha256(handle.read()).hexdigest()
        info = os.stat(path)
        out[name] = (info.st_size, info.st_mtime_ns, digest)
    return out


# -- --self-check -------------------------------------------------------------------------------------------------------


def self_check():
    import shutil
    import tempfile
    scratch = tempfile.mkdtemp(prefix="f1-self-check-")
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


def _self_check(ok, scratch):
    import copy
    from dataclasses import replace
    from gear_generator import store, ui_text
    from gear_generator.gears import kind_for, spur
    from gear_generator.gears.base import GlobalVariable
    from gear_generator.spec import GearSpec
    from gear_generator.workbook import assess, gearbox, model, update, xlsx

    ok(squash(spur.printed_backlash_expression()) == squash(PRINTED_TEXT) and spur.BACKLASH_FACTOR == 0.3,
       f"the pinned IIF is the app's: {spur.printed_backlash_expression()!r}")
    ok((store.PRINTED_SCHEMA, store.LINK_SCHEMA_VERSION) == (PRINTED_SCHEMA, LINK_SCHEMA),
       f"the pinned schemas are the app's: sidecar {store.PRINTED_SCHEMA}, link {store.LINK_SCHEMA_VERSION}")
    ok(sorted(GearSpec().to_dict()) == sorted(W9_SPEC_KEYS), "a machined GearSpec's to_dict keys are W9's")

    # backlash_judged: the app's own figures pass; each wrong way fails.
    for module in SPUR_MODULES:
        for process in PROCESSES:
            spec = GearSpec(module=module, process=process)
            kind = kind_for(spec)
            derived = kind.derive(spec)
            text = next(v.expression for v in kind.variables(spec, derived) if v.name == "Backlash")
            eq = [(f'"Module"= {module}', float(module)), (f'"Backlash"= {text}', derived.backlash)]
            ok(backlash_judged(eq, module, process == "printed", derived.backlash) == [],
               f"backlash: the app's {process} gear at module {module}: {text!r} = {derived.backlash:g}")
    eq = [('"Backlash"= ' + PRINTED_TEXT, 0.3)]
    ok(backlash_judged(eq, "1.5", True) == [] and backlash_judged(eq, "1.5", False) != []
       and backlash_judged([('"Backlash"= ' + PRINTED_TEXT, 0.45)], "1.5", True) != []
       and backlash_judged([('"Backlash"= 0.3', 0.3)], "1.5", True) != []
       and backlash_judged([], "1.5", True) != [] and backlash_judged(eq + eq, "1.5", True) != []
       and backlash_judged(eq, "1.5", True, derived=0.45) != []
       and backlash_judged([('"Backlash"=IIF("Module"<=1,0.3*"Module",0.3)', 0.24)], "0.8", True) == [],
       "backlash: fails on the printed IIF read machined, a wrong value, a literal, none, two, the app's figure off; "
       "spaces aside it holds")

    ok(stem_judged("C:\\o\\Gear_m1.5_N25_P.SLDPRT", True) == [] and stem_judged("C:\\o\\Gear_m1.5_N25.SLDPRT", True)
       and stem_judged("C:\\o\\Gear_m1.5_N25.SLDPRT", False) == []
       and stem_judged("C:\\o\\Gear_m1.5_N25_P.SLDPRT", False),
       "stem: _P printed only")

    # sidecar_judged on the app's own records, then broken.
    for spec, printed in ((GearSpec(process="printed"), True), (GearSpec(), False)):
        kind = kind_for(spec)
        derived = kind.derive(spec)
        variables = {v.name: v.expression for v in kind.variables(spec, derived)}
        schema = store.sidecar_schema(spec.to_dict())
        ok(sidecar_judged(schema, spec.to_dict(), derived.to_dict(), variables, printed) == [],
           f"sidecar: the app's {'printed' if printed else 'machined'} record (schema {schema}) holds")
        ok(sidecar_judged(schema, spec.to_dict(), derived.to_dict(), variables, not printed) != [],
           f"sidecar: the {'printed' if printed else 'machined'} record fails read as the other")
    mspec = GearSpec()
    mk = kind_for(mspec)
    md = mk.derive(mspec)
    mv = {v.name: v.expression for v in mk.variables(mspec, md)}
    ok(sidecar_judged(1, dict(mspec.to_dict(), process="machined"), md.to_dict(), mv, False) != []
       and sidecar_judged(1, mspec.to_dict(), dict(md.to_dict(), nozzle=0.4), mv, False) != []
       and sidecar_judged(2, mspec.to_dict(), md.to_dict(), mv, False) != [],
       "sidecar: a machined record with a process key, a nozzle, or at schema 2 is not W9's")

    # volume_judged on the app's own outlines (small_pinion_check's expected_volume, restated: outline less bore).
    def outline_volume(spec):
        kind = kind_for(spec)
        derived = kind.derive(spec)
        outline = kind.outline(spec, derived, kind.recipe_for(spec))
        bore = float(spec.bore) if spec.bore else 0.0
        return (spur.signed_area(outline[:-1]) - math.pi * (bore / 2) ** 2) * float(spec.face_width)
    vols = {(m, p): outline_volume(GearSpec(module=m, process=p)) for m in SPUR_MODULES for p in PROCESSES}
    print(f"fact    the app's outline volumes (mm³): { {f'{p} m{m}': round(v, 4) for (m, p), v in vols.items()} }")
    hi_p, hi_m = vols[("1.5", "printed")], vols[("1.5", "machined")]
    ok(volume_judged(hi_p, hi_p, hi_m, 1e-3) == [] and volume_judged(hi_m, hi_m, hi_p, 1e-3) == [],
       f"volume: at module 1.5 each outline is told from the other ({(hi_p - hi_m) / hi_m:+.3%} apart, the tolerance "
       "0.1 %)")
    ok(volume_judged(hi_m, hi_p, hi_m, 1e-3) != [] and volume_judged(hi_p * 1.002, hi_p, hi_m, 1e-3) != []
       and volume_judged(hi_p, hi_p, hi_p * 1.0015, 1e-3) != [],
       "volume: a printed reading of the machined volume, one 0.2 % off, and two outlines too near to tell all fail")
    lo_p, lo_m = vols[("0.8", "printed")], vols[("0.8", "machined")]
    ok(same_volume_judged(lo_p, lo_m) == [] and same_volume_judged(lo_p, lo_p * (1 + 2e-6)) != [],
       f"volume: at module 0.8 the two outlines are one ({lo_p:.4f}); a reading 2e-6 apart fails")

    seen = {"turn": {"gear1": 30.0, "gear2": -15.0}, "interference_at_drive_from": (0, 0.0),
            "interference_at_drive_to": (0, 0.0), "gear1_fixed": False}
    ok(turn_judged(seen, -0.5, 30.0) == [], "turn: 30° and -15° with no interference holds")
    ok(turn_judged(dict(seen, turn={"gear1": 30.0, "gear2": 15.0}), -0.5, 30.0) != []
       and turn_judged(dict(seen, turn={"gear1": 29.0, "gear2": -14.5}), -0.5, 30.0) != []
       and turn_judged(dict(seen, interference_at_drive_to=(1, 0.2)), -0.5, 30.0) != []
       and turn_judged(dict(seen, interference_at_drive_from=(2, 0.1)), -0.5, 30.0) != []
       and turn_judged(dict(seen, gear1_fixed=True), -0.5, 30.0) != []
       and turn_judged(dict(seen, turn={"gear1": 0.0, "gear2": 0.0}), -0.5, 30.0) != [],
       "turn: the wrong sense, a short turn, an interference at either end, gear 1 fixed and no turn each fail")

    # The rangebox judgements on W9's own record (tests/fixtures/printed: RangeBox as W9's code built it on the fake,
    # with W9a's user work on its record), read and planned through the app as the window does.
    fixtures = os.path.join(REPO, "tests", "fixtures", "printed")
    with open(os.path.join(fixtures, "RangeBox_W9_record.json"), encoding="utf-8") as handle:
        snap = json.load(handle)
    files, sidecars = set(snap["files"]), dict(snap["sidecars"])

    def exists(p):
        return path_key(p) in files

    def read_sidecar(p):
        text = sidecars.get(path_key(p))
        return store.from_json(text) if text is not None and exists(p) else None
    read_spec, diagnostics = model.from_book(xlsx.read(os.path.join(fixtures, "RangeBox_W9.xlsx")))
    ok(diagnostics == [], f"W9's workbook reads with no diagnostic: {diagnostics}")

    def opened(spec_read, process, cell=""):
        record = store.link_record_from_json(snap["record"])
        spec = replace(spec_read, box=replace(spec_read.box, process=process, process_cell=cell))
        a = assess.assess(replace(spec, source_path=snap["workbook"]), [], "C:\\Out\\",
                          blank_process=assess.blank_process(record))
        up = update.classify(record, a, exists=exists, read_sidecar=read_sidecar)
        again = gearbox.plan_gearbox(a, record, exists=exists, read_sidecar=read_sidecar)
        footer = ui_text.workbook_footer(a, record=record, plan=again, update=up, digest=record.digest,
                                         folder="C:\\Out\\")
        return spec, a, record, up, footer

    def as_built(spec, a, up):
        return as_built_judged(spec.box.process, spec.box.process_cell, a.spec.box.process,
                               [j.stem for j in a.parts.jobs], [j.stem for j in a.parts.jobs if j.spec.is_printed()],
                               up)
    spec0, a0, rec0, up0, foot0 = opened(read_spec, "")
    ok(as_built(spec0, a0, up0) == [], f"as built: W9's gearbox opened with no Process row reads Machined, nothing to "
                                       f"do: {as_built(spec0, a0, up0)}")
    ok(footer_as_built_judged(foot0.text) == [], f"as built: the footer is W9's, nothing of Process: "
                                                 f"{foot0.text[:90]!r}…")
    ok(footer_as_built_judged("Update SolidWorks will change Sun's values (Gear_m1.25_N29).") != []
       and footer_as_built_judged(FOOTER_AS_BUILT + "; type Printed beside Process.") != [],
       "as built: a footer with something to do, or one naming Process, fails")
    line0 = ui_text.workbook_process_line(spec0.box, a0.spec.box)
    ok(line0 == LINE_AS_BUILT, f"as built: the Process line is the pinned one: {line0!r}")
    spec1, a1, rec1, up1, foot1 = opened(read_spec, "printed", "Box!B10")
    ok(as_built(spec1, a1, up1) != [], "as built: the same gearbox with Printed typed fails it")
    ok(as_built_judged("", "", "machined", ["Gear_m1.5_N25_P"], [], up0) != []
       and as_built_judged("", "Box!B10", "machined", [], [], up0) != []
       and as_built_judged("", "", "printed", [], [], up0) != []
       and as_built_judged("", "", "machined", [], [], None) != [],
       "as built: a _P name, a Process row, a blank read printed and no plan each fail")
    line1 = ui_text.workbook_process_line(spec1.box, a1.spec.box)
    ok(line1 == LINE_PRINTED, f"printed: the Process line is the pinned one: {line1!r}")
    entries = rec1.current_parts()
    ok(backlash_only_judged(up1, entries, RANGEBOX_PARTS) == [],
       f"printed: every part of W9's gearbox changes its Backlash alone, in place: "
       f"{backlash_only_judged(up1, entries, RANGEBOX_PARTS)}")
    ok(backlash_only_judged(up0, rec0.current_parts(), RANGEBOX_PARTS) != [],
       "printed: the plan of the gearbox as built (nothing changed) fails it")
    ok(foot1.text.startswith(FOOTER_PRINTED), f"printed: the footer before the press begins with the pinned sentence: "
                                              f"{foot1.text[:120]!r}…")
    wider = replace(read_spec, gears=tuple(replace(g, face_width="11") if g.id == "Sun" else g
                                           for g in read_spec.gears))
    _, _, rec2, up2, _ = opened(wider, "printed", "Box!B10")
    ok(any("Face Width" in p for p in backlash_only_judged(up2, rec2.current_parts(), RANGEBOX_PARTS)),
       f"printed: a part that also changes its face width fails it, naming the global: "
       f"{backlash_only_judged(up2, rec2.current_parts(), RANGEBOX_PARTS)}")
    ok(backlash_only_judged(up1, entries, RANGEBOX_PARTS[:4]) != [] and backlash_only_judged(None, entries, ()) != [],
       "printed: one part more than expected, or no plan, fails it")
    first = up1.parts[0]
    kept = replace(up1, parts=(replace(first, variables=tuple(
        GlobalVariable(v.name, MACHINED_TEXT) if v.name == "Backlash" else v for v in first.variables)),)
        + tuple(up1.parts[1:]))
    ok(any("Gear_m1.25_N29" in p for p in backlash_only_judged(kept, entries, RANGEBOX_PARTS)),
       "printed: a part whose Backlash stays the machined rule fails it, naming the part")

    # The Update's sentence: package C's once, against C's code; not again once the record says printed (the S2 fix).
    pressed = types.SimpleNamespace(parts=[types.SimpleNamespace(changed=True) for _ in up1.parts])
    said = ui_text._process_names_kept(up1, pressed, rec1)  # noqa: SLF001
    want = names_sentence(RANGEBOX_PARTS)
    ok(said == want, f"names: package C's code says the pinned sentence for RangeBox's five parts: {said!r}")
    printed_record = copy.deepcopy(rec1)
    for e in printed_record.parts:
        e.spec = dict(e.spec, process="printed")
    ok(ui_text._process_names_kept(up1, pressed, printed_record) == "",  # noqa: SLF001
       "names: once the record holds the parts printed, the sentence is not said again")
    one = names_sentence(["Gear_m1.5_N17"])
    ok(one.startswith("Gear_m1.5_N17, now printed, keeps its file name, without the _P")
       and "makes a new part named with _P" in one, "names: one part is said in the singular, as C wrote it")
    text = "Updated SolidWorks: changed it. " + want
    ok(sentence_judged(text, want, (STALE_CLAUSE,)) == [] and sentence_judged(text + " " + want, want) != []
       and sentence_judged("Updated SolidWorks.", want) != []
       and sentence_judged(text + " (its file keeps its name, which no longer says what it holds)", want,
                           (STALE_CLAUSE,)) != [],
       "sentence: once holds; twice, never, and the stale clause beside it fail")

    def result_part(doc, changed):
        return types.SimpleNamespace(document=doc + ".SLDPRT", changed=list(changed))
    good = [result_part(s, ["Backlash"]) for s in RANGEBOX_PARTS]
    lay = types.SimpleNamespace(document="RangeBox_Layout.SLDPRT", changed=[])
    ok(result_parts_judged(good, RANGEBOX_PARTS, lay) == [], "result: Backlash alone in each part holds")
    ok(result_parts_judged(good[:4] + [result_part(RANGEBOX_PARTS[4], [])], RANGEBOX_PARTS) != []
       and result_parts_judged(good[:4] + [result_part(RANGEBOX_PARTS[4], ["Backlash", "Face Width"])],
                               RANGEBOX_PARTS) != []
       and result_parts_judged(good, RANGEBOX_PARTS, types.SimpleNamespace(document="L.SLDPRT", changed=["S2 X"])) != []
       and result_parts_judged(good, RANGEBOX_PARTS, None,
                               [types.SimpleNamespace(document="C.SLDPRT", changed=["P X"])]) != []
       and result_parts_judged(good + [result_part("Other", ["Backlash"])], RANGEBOX_PARTS) != [],
       "result: a part left unchanged, a second global, the layout or a carrier changed, another document changed "
       "each fail")

    # record_judged on the fake's record made printed, as the press's finish writes it.
    before = [e.path for e in entries]
    rec_after = copy.deepcopy(rec1)
    for e, p in zip(rec_after.current_parts(), up1.parts):
        e.spec = p.spec.to_dict()
        e.variables = [[v.name, v.expression] for v in p.variables]
    cars = {stem_of(e.path): (PRINTED_SCHEMA, e.spec) for e in rec_after.current_parts()}
    ok(record_judged(LINK_SCHEMA, rec_after.current_parts(), before, cars) == [],
       f"record: the parts printed under their old names at link 11, sidecars at 3, holds: "
       f"{record_judged(LINK_SCHEMA, rec_after.current_parts(), before, cars)}")
    ok(record_judged(10, rec_after.current_parts(), before, cars) != []
       and record_judged(LINK_SCHEMA, rec1.current_parts(), before, cars) != []
       and record_judged(LINK_SCHEMA, rec_after.current_parts(), before[:4] + ["C:\\Out\\X_P.SLDPRT"], cars) != []
       and record_judged(LINK_SCHEMA, rec_after.current_parts(), before,
                         dict(cars, **{RANGEBOX_PARTS[0]: (1, {})})) != [],
       "record: link 10, the parts still machined, a renamed part and a sidecar at 1 each fail")

    # files_changed and snapshot on a scratch folder.
    folder = os.path.join(scratch, "files")
    os.makedirs(folder)
    for name in ("A.SLDPRT", "B.gear.json", "~$W.xlsx", "W.xlsx", "notes.txt"):
        with open(os.path.join(folder, name), "w", encoding="utf-8") as handle:
            handle.write(name)
    s1 = snapshot(folder)
    ok(sorted(s1) == ["A.SLDPRT", "B.gear.json", "W.xlsx"] and files_changed(s1, snapshot(folder)) == [],
       "files: Excel's lock file aside, a second read of an untouched folder finds nothing changed")
    with open(os.path.join(folder, "B.gear.json"), "w", encoding="utf-8") as handle:
        handle.write("b")
    os.remove(os.path.join(folder, "A.SLDPRT"))
    ok(files_changed(s1, snapshot(folder)) == ["A.SLDPRT", "B.gear.json"], "files: a file rewritten or gone is found")

    _self_check_form(ok, scratch)


def _self_check_form(ok, scratch):
    """The strip's own form, as the live sections drive it, read without SolidWorks: the names and specs each case
    builds from, the plans' paths."""
    try:
        import tkinter as tk
        root = tk.Tk()
    except Exception as exc:  # noqa: BLE001 - said: the live sections need the form, so its check is a failure
        ok(False, f"form: the strip's form cannot be made here ({type(exc).__name__}: {exc}); the live sections need "
                  "Tk, as python.exe on Windows has it")
        return
    root.withdraw()
    try:
        app = make_form(root)
        ok(app._worker is None, "form: made with no link to SolidWorks (its worker none)")  # noqa: SLF001
        ok(app.process.get() == "printed" and app._gear_spec("a").stem() == "Gear_m1.5_N25_P",  # noqa: SLF001
           "form: it opens Printed, its gear Gear_m1.5_N25_P")
        for module in SPUR_MODULES:
            for process in PROCESSES:
                folder = os.path.join(scratch, f"spur-{module}-{process}")
                spec, derived, context = form_single(app, folder, module, process)
                want = f"Gear_m{module}_N25" + ("_P" if process == "printed" else "")
                ok(spec.process == process and stem_of(context["paths"][0]) == want and derived is not None
                   and abs(backlash_wanted(module, process == "printed") - derived.backlash) <= VALUE_TOL
                   and stem_judged(context["paths"][0], process == "printed") == [],
                   f"form: {process} at module {module} plans {stem_of(context['paths'][0])} with Backlash "
                   f"{derived.backlash:g}")
        for process in PROCESSES:
            pair, context = form_pair(app, os.path.join(scratch, f"pair-{process}"), process)
            stems = [stem_of(p) for p in context["paths"]]
            mark = "_P" if process == "printed" else ""
            ok(stems == [f"Pinion_m1.5_N25{mark}", f"Gear_m1.5_N50{mark}", f"Pair_m1.5_25T_50T{mark}"]
               and pair.motion == PAIR_MOTION and pair.gear_a.process == pair.gear_b.process == process,
               f"form: the {process} pair plans {stems}, motion {pair.motion!r}")
    finally:
        root.destroy()


# -- the strip's own form (``gui.GearApp``), with no link of its own ------------------------------------------------------


def _no_link(self):
    """``GearApp._start_link`` replaced for this run: the form's own worker would attach to the newest SolidWorks, a
    second driver; this run's worker attaches by PID and runs the form's jobs."""


def make_form(root):
    from gear_generator import gui
    gui.GearApp._start_link = _no_link
    return gui.GearApp(root)


def form_single(app, folder, module, process):
    """The form as a person sets it for one gear (Single gear, the Process row, Module), worked out by the form's own
    ``_derive_now``, and its own ``_plan_single``: (spec, derived, context)."""
    from gear_generator.spec import MODE_SINGLE
    app.mode.set(MODE_SINGLE)
    app._on_mode_changed()  # noqa: SLF001
    app.out_folder.set(folder)
    app.process.set(process)
    app.gear_vars["a"]["module"].set(module)
    app._derive_now()  # noqa: SLF001
    return app._gear_spec("a"), app._derived["a"], app._plan_single(folder)  # noqa: SLF001


def form_pair(app, folder, process):
    """The form's pair as it opens (25 / 50), module 1.5 on both gears, its motion set to gear mate and its Process
    row set: (pair spec, context)."""
    from gear_generator.spec import MODE_PAIR
    app.mode.set(MODE_PAIR)
    app._on_mode_changed()  # noqa: SLF001
    app.out_folder.set(folder)
    app.motion.set(PAIR_MOTION)
    app.process.set(process)
    for side in ("a", "b"):
        app.gear_vars[side]["module"].set("1.5")
    app._derive_now()  # noqa: SLF001
    return app._pair_spec(), app._plan_pair(folder)  # noqa: SLF001


if SELF_CHECK:
    raise SystemExit(self_check())


# -- the live run: W9a's harness ------------------------------------------------------------------------------------------

sys.path.insert(0, HERE)
import w9a_demonstration as A  # noqa: E402  (W8's and S0's scripts, the watch, the What's Wrong rule, Desk9, main)

W = A.W
from gear_generator import store, ui_text  # noqa: E402
import gear_pairs_check as GP  # noqa: E402  (its drive; its own options are absent here and so at their defaults)
import small_pinion_check as SP  # noqa: E402  (its readings, expected_volume and judge_part; --pid is this run's)

say, check = W.say, W.check
OUT = W.OUT
CTX, RESULT, run, job = A.CTX, A.RESULT, A.run, A.job
# small_pinion_check's judge_part says and checks through its own module's say and check; they are this run's here, so
# its lines go into this log and its failures into this run's count (its file is not changed).
SP.say, SP.check = say, check
WW_CLOSE_FLAG = "--close-outlived-whats-wrong"      # W9c's flag, its own path (w9c_demonstration.close_outlived_on)


def tk_root():
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    return root


def read_part(label, path):
    """A part read back: its equations (text and value) and small_pinion_check's readings (volume, bodies, feature
    errors, vertex radii)."""
    return run(f"{label}: read", job(path, lambda s: {"equations": s.equations(), "readings": SP.readings(s)}), 600)


def judged_sidecar(label, path, printed):
    car = store.read_sidecar(store.sidecar_path(path))
    if car is None:
        return check(False, f"{label}: no .gear.json beside {os.path.basename(path)}")
    variables = dict((str(n), str(v)) for n, v in car.record.variables)
    wrong = sidecar_judged(car.schema_version, car.record.spec, car.record.derived, variables, printed)
    return check(not wrong, f"{label}: its .gear.json at sidecar {car.schema_version} "
                            + ("printed, its process, its 0.4 nozzle and the IIF" if printed
                               else "as W9 records a machined part (no process, no nozzle, 0.3 * \"Module\")")
                            + f": {wrong or 'holds'}")


def judged_backlash(label, equations, module, printed, derived):
    wrong = backlash_judged(equations, module, printed, derived)
    found = [(t, v) for t, v in equations if squash(t).startswith('"Backlash"=')]
    text, value = found[0] if found else (None, None)
    return check(not wrong, f"{label}: Backlash reads {text!r} and SolidWorks evaluates it to {value}, the app's "
                            f"{backlash_wanted(module, printed):g} at module {module}: {wrong or 'holds'}")


# -- spur ---------------------------------------------------------------------------------------------------------------


def spur_case(label, app, folder, module, process, out):
    os.makedirs(folder)
    printed = process == "printed"
    spec, derived, context = form_single(app, folder, module, process)
    path = context["paths"][0]
    say(f"form    {label}: Process {app.process.get()}, Module {module}: the form plans {os.path.basename(path)}; its "
        f"diagnostics {[d.message for d in app._diagnostics['a']] or 'none'}")  # noqa: SLF001
    check(not stem_judged(path, printed) and not os.path.exists(path),
          f"{label}: the form names it {os.path.basename(path)} ({'_P' if printed else 'no _P'}), a new file")
    result = run(f"{label}: built", context.pop("job"), 900)
    for line in result.log_lines():
        say("        " + line)
    app._finish_single(context, result)  # noqa: SLF001 - the form's own finish: the status and the .gear.json
    say(f"status  {label}: {app.status.get()}")
    check(result.ok and bool(result.saved) and W.under(result.saved, folder),
          f"{label}: built and saved by the form's job ({os.path.basename(result.saved or '')}): ok {result.ok}, "
          f"failures {list(result.failures)}")
    got = read_part(label, path)
    case = out.setdefault("cases", {})[label] = {"path": os.path.basename(path), "volume": got["readings"]["volume"],
                                                 "equations": got["equations"], "errors": got["readings"]["errors"]}
    judged_backlash(label, got["equations"], module, printed, derived.backlash)
    SP.judge_part(label, spec, got["readings"])          # the volume within 0.1 % of the outline, the tips (its checks)
    judged_sidecar(label, path, printed)
    other = dataclasses.replace(spec, process="machined" if printed else "printed")
    case.update(own=SP.expected_volume(spec), other=SP.expected_volume(other))
    left = run(f"{label}: closed", W.quit_in(folder))
    check(not left, f"{label}: closed, nothing left open under its folder: {left}")
    return case


def section_spur(out):
    say("== spur  the strip's form as it opens (Printed, Gear_m1.5_N25_P), then Machined beside it, then both at "
        "module 0.8: built by the form's own plan and job, its record by its own finish; each read back: the name, "
        "Backlash's text and value, the tooth (small_pinion_check), the .gear.json")
    root_folder = W.fresh_folder("spur")
    root = tk_root()
    try:
        app = make_form(root)
        say("form    the strip's GearApp made with its link to SolidWorks not started: this run's worker runs its jobs")
        check(app.process.get() == "printed" and app._gear_spec("a").stem() == "Gear_m1.5_N25_P",  # noqa: SLF001
              f"spur: the form opens Printed and names its gear Gear_m1.5_N25_P ({app.process.get()!r})")
        cases = {}
        for module in SPUR_MODULES:
            for process in PROCESSES:
                label = f"spur {process} m{module}"
                cases[(module, process)] = spur_case(label, app, os.path.join(root_folder, f"{process}-m{module}"),
                                                     module, process, out)
        p, m = cases[("1.5", "printed")], cases[("1.5", "machined")]
        for label, case in (("printed", p), ("machined", m)):
            wrong = volume_judged(case["volume"], case["own"], case["other"], SP.VOLUME_TOLERANCE)
            check(not wrong, f"spur m1.5 {label}: its volume {case['volume']:.4f} mm³ is its own outline's "
                             f"({case['own']:.4f}) and not the other process's ({case['other']:.4f}), to "
                             f"{SP.VOLUME_TOLERANCE:g}: {wrong or 'told apart'}")
        say(f"fact    spur m1.5: printed less machined {p['volume'] - m['volume']:+.4f} mm³ measured, "
            f"{p['own'] - m['own']:+.4f} by the app's outlines")
        p, m = cases[("0.8", "printed")], cases[("0.8", "machined")]
        wrong = same_volume_judged(p["volume"], m["volume"])
        check(not wrong, f"spur m0.8: printed and machined are the same solid ({p['volume']:.6f}, {m['volume']:.6f} "
                         f"mm³), as the two backlashes are one value there: {wrong or 'the same'}")
    finally:
        root.destroy()


# -- pair ---------------------------------------------------------------------------------------------------------------


def pair_case(label, app, folder, process, out):
    os.makedirs(folder)
    printed = process == "printed"
    pair, context = form_pair(app, folder, process)
    paths = list(context["paths"])
    say(f"form    {label}: Process {app.process.get()}, motion {pair.motion}: the form plans "
        f"{[os.path.basename(p) for p in paths]}")
    check(all(not stem_judged(p, printed) for p in paths) and not any(os.path.exists(p) for p in paths),
          f"{label}: both parts and the assembly named {'with' if printed else 'without'} _P, new files: "
          f"{[stem_of(p) for p in paths]}")
    result = run(f"{label}: built", context.pop("job"), 1800)
    for line in result.log_lines():
        say("        " + line)
    app._finish_pair(context, result)  # noqa: SLF001 - the form's own finish: the status and both .gear.json
    say(f"status  {label}: {app.status.get()}")
    built = bool(result.ok and result.assembly is not None and result.assembly.ok)
    check(built, f"{label}: the pair built by the form's job: ok {result.ok}, skipped {result.skipped!r}")
    case = out.setdefault("cases", {})[label] = {"paths": [os.path.basename(p) for p in paths]}
    if not built:
        return case
    seen = run(f"{label}: driven", job(paths[2], lambda s: GP.drive(s, paths[2], paths[0], paths[1])), 600)
    ratio = -int(pair.gear_a.teeth) / int(pair.gear_b.teeth)
    span = GP.DRIVE_TO - GP.DRIVE_FROM
    case["drive"] = seen
    wrong = turn_judged(seen, ratio, span)
    say(f"fact    {label}: {seen['gear1']} turned {seen['turn']['gear1']:.6f}°, {seen['gear2']} "
        f"{seen['turn']['gear2']:.6f}°; interference at {GP.DRIVE_FROM:g}° {seen['interference_at_drive_from']}, at "
        f"{GP.DRIVE_TO:g}° {seen['interference_at_drive_to']}")
    check(not wrong, f"{label}: driven by gear_pairs_check's drive, gear A turns {span:g}° and gear B {ratio:g} of it, "
                     f"no interference at either end: {wrong or 'holds'}")
    for side, path in (("a", paths[0]), ("b", paths[1])):
        spec = getattr(pair, f"gear_{side}")
        eqs = run(f"{label} {stem_of(path)}: globals", job(path, lambda s: s.equations()), 300)
        judged_backlash(f"{label} {stem_of(path)}", eqs, spec.module, printed, app._derived[side].backlash)  # noqa: SLF001
        judged_sidecar(f"{label} {stem_of(path)}", path, printed)
    left = run(f"{label}: closed", W.quit_in(folder))
    check(not left, f"{label}: closed without saving the drive, nothing left open under its folder: {left}")
    case["clean"] = not wrong
    return case


def section_pair(out):
    say("== pair  the strip's form as a pair (25 / 50, module 1.5, motion gear mate), Printed then Machined, built by the "
        "form's own plan and job; each driven by gear_pairs_check's drive; each part's Backlash and .gear.json")
    root_folder = W.fresh_folder("pair")
    root = tk_root()
    try:
        app = make_form(root)
        cases = {p: pair_case(f"pair {p}", app, os.path.join(root_folder, p), p, out) for p in PROCESSES}
        check(all(c.get("clean") for c in cases.values()),
              "pair: the printed pair turns as the machined pair does (each by the same judgement)")
        say("fact    pair: the backlash in the mesh is not measured in SolidWorks (no script measures it); the "
            "parts' Backlash globals are what is read")
    finally:
        root.destroy()


# -- rangebox -----------------------------------------------------------------------------------------------------------


class _Var:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value


_WINDOW = A._WINDOW  # noqa: SLF001


class DeskF1(A.Desk9):
    """W9a's Desk9, reading as the Workbook window reads since F1: its own ``_assess``, which resolves a blank Process
    by ``_blank_process`` (the record beside the workbook, D11's (B)), in place of W8's Desk's bare ``assess``, whose
    default reads a blank Printed. ``_folder`` and ``_template`` are the window's too, the strip's Output folder the
    copy's, as W8's Desk has it."""

    _assess = _WINDOW._assess
    _blank_process = _WINDOW._blank_process
    _folder = _WINDOW._folder
    _template = _WINDOW._template

    def __init__(self, path, worker, strip=""):
        super().__init__(path, worker, strip)
        self.app.out_folder = _Var(strip)
        self.app.part_template = _Var("")
        self.app.assembly_template = _Var("")
        self.process_record = ""

    def _after_read(self):
        """W8's ``Desk._after_read``, the assessment the window's own."""
        r = self.reading
        check(r.ok, f"read {os.path.basename(self.path)}: {r.error or 'ok'}")
        spec = r.spec
        self.a = self._assess(spec, r.diagnostics)
        for d in self.a.diagnostics:
            say(f"        {d.level:7} {d.message}")
        say(f"        {len(spec.shafts)} shafts · {len(spec.gears)} gears · {len(spec.meshes)} meshes; "
            f"gate {self.a.lay_out_refusal()!r}; Process as read {spec.box.process!r} at {spec.box.process_cell!r}, "
            f"resolved {self.a.spec.box.process!r}")
        self.plan_solidworks()

    def process_line(self):
        return ui_text.workbook_process_line(self.reading.spec.box, self.a.spec.box, record=self.process_record)


def raw_record(workbook):
    with open(store.link_record_path(workbook), encoding="utf-8") as handle:
        return json.load(handle)


def master_before_f1(master):
    """The master's own record, read from its file (nothing written): its link schema, and any part's spec saying a
    process. W9a's setup.master was written before F1: none does."""
    raw = raw_record(os.path.join(master, "RangeBox.xlsx"))
    said = [p.get("spec", {}).get("process") for p in raw.get("parts", []) if "process" in p.get("spec", {})]
    return raw.get(store.LINK_SCHEMA_KEY), said


def box_process_row(book):
    """The Box sheet's row labelled Process (any case), and the first row whose label is empty (as W8's ``cell`` finds
    one)."""
    ws = book.wb.Worksheets("Box")
    labels = {r: str(ws.Cells(r, 1).Value or "").strip() for r in range(2, 80)}
    found = next((r for r, t in labels.items() if t.lower() == PROCESS_LABEL.lower()), None)
    empty = next(r for r, t in labels.items() if not t)
    return found, empty


def judged_live_backlash(label, desk):
    """Every part's Backlash read from SolidWorks (``Session.equations``), held to the printed IIF and its value at
    the part's module as the record holds it."""
    clean = True
    for entry in desk.record.current_parts():
        path, module = entry.path, str(dict(entry.spec or {}).get("module", ""))
        eqs = run(f"{label} {stem_of(path)}: globals", job(path, lambda s: s.equations()), 300)
        clean = judged_backlash(f"{label} {stem_of(path)}", eqs, module, True, None) and clean
    return clean


def section_rangebox(out):
    say("== rangebox  a copy of W9a's setup.master (RangeBox with the user's work, built before F1): opened as built "
        "(Machined, nothing written, D11 (B)); then a row labelled Process with Printed typed on its Box sheet; one "
        "Update SolidWorks: every part's Backlash in place, every user item as W9a reads it, nothing saved, the record, "
        "the sentence; saved and closed as the user would, a second Update quiet")
    master = A.MASTER["setup"]
    if not master:
        raise AssertionError("rangebox: give --user-master, W9a's setup.master for this SolidWorks version (it is the "
                             "gearbox built before F1 the plan names; this script does not build one)")
    schema, said = master_before_f1(master)
    out["master_schema"] = schema
    check(isinstance(schema, int) and schema < LINK_SCHEMA and not said,
          f"rangebox: the master's own record was written before F1: link schema {schema}, no part saying a process "
          f"({said or 'none'})")
    if said or not isinstance(schema, int) or schema >= LINK_SCHEMA:
        A.section_stop(f"rangebox: {os.path.basename(master)} is not a gearbox built before F1")
    try:
        folder = A.w8_step(W.copy_built, master, "rangebox")
    except W.CopyStop as exc:
        raise AssertionError(f"rangebox: the copy of {os.path.basename(master)} stopped: {exc}") from None
    path = os.path.join(folder, "RangeBox.xlsx")
    say(f"fact    rangebox: the copy's record now at link schema {raw_record(path).get(store.LINK_SCHEMA_KEY)} "
        "(W8's copy_built writes it forward through store's writer to put its paths onto the copy; the app's own "
        "open below writes nothing)")
    try:
        _rangebox(out, folder, path)
    finally:
        A.w8_step(W.end_copy, CTX["worker"], folder, "rangebox")


def _rangebox(out, folder, path):
    users = A.rb_users()
    say("-- rangebox  the workbook opened as built: read and planned through the window's own path")
    files_open = snapshot(folder)
    desk = DeskF1(path, CTX["worker"], strip=folder)
    desk.read()
    box = desk.record.gearbox if desk.record is not None else None
    check(W.turning(desk) and box is not None and W.under(box.assembly, folder)
          and desk.record.digest == desk.reading.digest,
          "rangebox: the copy reads as built from this workbook, its assembly in the copy")
    if box is None:
        raise AssertionError("rangebox: the copy's record holds no gearbox")
    a = desk.a
    read_box = desk.reading.spec.box
    jobs = list(a.parts.jobs)
    wrong = as_built_judged(read_box.process, read_box.process_cell, a.spec.box.process, [j.stem for j in jobs],
                            [j.stem for j in jobs if j.spec.is_printed()], desk.update)
    check(not wrong, f"rangebox, as built: no Process row, the blank read {a.spec.box.process!r} (D11 (B)), "
                     f"{len(jobs)} gears planned machined with no _P, Update with nothing to do: {wrong or 'holds'}")
    f = desk.say_footer("rangebox, opened as built")
    wrong = footer_as_built_judged(f.text)
    check(not wrong, f"rangebox, as built: the footer is W9's for a built gearbox with nothing changed, and says "
                     f"nothing of Process: {wrong or 'holds'}")
    line = desk.process_line()
    say(f"panel   Process: {line}")
    check(line == LINE_AS_BUILT, f"rangebox, as built: the Workbook panel's Process line says to add the row: {line!r}")
    changed = files_changed(files_open, snapshot(folder))
    check(not changed, f"rangebox, as built: nothing written by the open and its planning (the record, the .gear.json "
                       f"files, the workbook and every SolidWorks file, by size, time and sha256): {changed or 'none'}")
    out["as_built"] = {"footer": f.text, "line": line, "written": changed}
    book = W.Workbook(CTX["excel"], path, "rangebox")

    say("-- rangebox  the user's work as W9a's go reads it, before")
    A.users_in_copy("rangebox", desk, folder, users)
    check(box.user_work is not None, "rangebox: the record holds setup's inventory of the user's work")
    modes = list(box.modes)
    every = A.read_every("rangebox, as copied", box.assembly, A.pairs_of(box, users), modes)
    rel_orig = A.rel_of(every["frames"][modes[0]], A.RB_LOCKED)
    flags_set = {n: fl for n, fl in every["by_mode"].items() if n in A.RB_USER_MATES}
    dz_set = {m: float(every["frames"][m]["Sprocket-4"][1][2]) - float(every["frames"][m]["Sprocket-3"][1][2])
              for m in modes}
    check(set(flags_set) == set(A.RB_USER_MATES), f"rangebox: the user's 8 mates as set up: {sorted(flags_set)}")
    A.go_judge("rangebox as copied", desk, every, rel_orig, flags_set, out, dz_set)
    entities_before = A.entities_of("rangebox, before", desk, folder)
    keyway = [f_ for f_ in A.feature_list(A.sun_part(box)) if f_[0] == "User Keyway"]
    check(bool(keyway) and not keyway[0][2], f"rangebox: the User Keyway in Sun's part, code "
                                             f"{keyway[0][2] if keyway else None}")

    say("-- rangebox  Printed typed on the Box sheet in Excel, in a row labelled Process (the panel's line asks for it)")
    found, empty = box_process_row(book)
    row = found or empty
    cells = ([] if found else [("Box", f"A{row}", PROCESS_LABEL)]) + [("Box", f"B{row}", PRINTED_WORD)]
    say(f"person  rangebox: {'types Printed beside its Process row' if found else 'adds a row labelled Process'} at "
        f"Box row {row}: {cells}")
    W.edit(desk, book, *cells)
    a = desk.a
    read_box = desk.reading.spec.box
    errors = [d.message for d in a.diagnostics if d.is_error]
    check(read_box.process == "printed" and read_box.process_cell == f"Box!B{row}" and a.spec.box.process == "printed"
          and not errors, f"rangebox, Printed: the Box reads {read_box.process!r} at {read_box.process_cell!r}, "
                          f"resolved {a.spec.box.process!r}, no error {errors or ''}")
    line = desk.process_line()
    say(f"panel   Process: {line}")
    check(line == LINE_PRINTED, f"rangebox, Printed: the Process line reads {line!r}")
    entries = desk.record.current_parts()
    before_paths = [e.path for e in entries]
    wrong = backlash_only_judged(desk.update, entries, RANGEBOX_PARTS)
    check(not wrong, f"rangebox, Printed: classify plans one Update in place, every part changing its Backlash alone "
                     f"({MACHINED_TEXT} to the printed IIF), no structural change, no new part, every file keeping "
                     f"its name: {wrong or 'holds'}")
    ahead = A.ahead_of(desk, "rangebox, Printed, before the press")
    f = desk.footer()
    check(f.text.startswith(FOOTER_PRINTED), f"rangebox, Printed: the footer before the press names every part: "
                                             f"{f.text[:160]!r}…")
    check(ahead is not None and not ahead.problems and not ahead.changed_since,
          f"rangebox, Printed: the footer foresees nothing of the user's stopping the press: "
          f"{[(p.kind, list(p.mates)) for p in (ahead.problems if ahead else [])]}")
    out["foreseen_carry"] = sorted(A.predicted_carry(ahead))

    say("-- rangebox  one Update SolidWorks")
    if W.free_gb() < PRESS_FREE_GB:
        A.section_stop(f"rangebox: {W.memory()}: under {PRESS_FREE_GB:g} GB free before the press (SolidWorks 2024's "
                       "first press on a freshly opened RangeBox costs 3.3 to 4 GB; run it in a fresh session)")
    files_press = snapshot(folder)
    result, calls = A.press(desk, "rangebox: Printed, one Update")
    out["press"] = A._update_fact(desk, result)  # noqa: SLF001
    if result is None:
        A.section_stop(f"rangebox: the press refused: {desk.error}")
    for line_ in result.log_lines():
        say("        " + line_)
    wrong = result_parts_judged(result.parts, RANGEBOX_PARTS, result.layout, result.carriers)
    check(result.ok and not result.failures and not wrong,
          f"rangebox: the Update ended ok and wrote Backlash alone in each of the five parts, nothing in the layout or "
          f"the carrier: failures {result.failures}; {wrong or 'holds'}")
    made = {k: getattr(result, k, None) for k in ("inserted", "built", "deleted", "bands_added", "modes_added")}
    check(not any(made.values()), f"rangebox: nothing made new or inserted in place: {made}")
    done = {(c, g) for c, g, _ in result.carried}
    check(done == A.predicted_carry(ahead), f"rangebox: what the press carried is what the footer foresaw (said "
                                            f"{sorted(A.predicted_carry(ahead))}, did {sorted(done)})")
    allowed = {n for _, n in W.bodies(box)} | set(A.RB_LOCKED)
    puts = sorted({c[1] for c in calls if c[0] == "put"})
    stray = [n for n in puts if n not in allowed]
    if stray:
        A.stop(f"rangebox: the Update put {stray}, which is neither an app body nor a sprocket locked to one (§0.3)")
    say(f"fact    rangebox: the press put {puts or 'nothing'}; carried {sorted(done) or 'nothing'}")
    check(not result.user_in_error and not result.user_features_in_error,
          f"rangebox: nothing of the user's in error after: {result.user_in_error} "
          f"{[f_.name for f_ in result.user_features_in_error]}")
    sw = (".sldprt", ".sldasm")
    saved = files_changed({n: v for n, v in files_press.items() if n.lower().endswith(sw)},
                          {n: v for n, v in snapshot(folder).items() if n.lower().endswith(sw)})
    check(not saved, f"rangebox: no SolidWorks file saved by the app (sizes, times and sha256 of every part and the "
                     f"assembly as before the press): {saved or 'none'}")
    note = desk.note[0] if desk.note else ""
    sentence = names_sentence(RANGEBOX_PARTS)
    wrong = sentence_judged(note, sentence, (STALE_CLAUSE,))
    check(note.startswith("Updated SolidWorks") and not wrong,
          f"rangebox: the result says package C's sentence once, and not the stale name clause: {wrong or 'holds'}")
    out["sentence"] = note

    say("-- rangebox  read back: every part's Backlash, the record, the user's work as W9a's go reads it")
    out["backlash"] = judged_live_backlash("rangebox", desk)
    record = store.read_link_record(path)
    cars = {}
    for e in record.current_parts():
        car = store.read_sidecar(store.sidecar_path(e.path))
        cars[stem_of(e.path)] = (car.schema_version, car.record.spec) if car is not None else None
    wrong = record_judged(raw_record(path).get(store.LINK_SCHEMA_KEY), record.current_parts(), before_paths, cars)
    check(not wrong, f"rangebox: the record on disk at link {LINK_SCHEMA}, the same five part files, each printed with "
                     f"the IIF, each .gear.json at sidecar {PRINTED_SCHEMA}: {wrong or 'holds'}")
    entities_after = A.entities_of("rangebox, after", desk, folder)
    moved = {n: (entities_before.get(n), v) for n, v in entities_after.items() if entities_before.get(n) != v}
    check(entities_after == entities_before, f"rangebox: every user mate joins what it joined before the press: "
                                             f"{moved or 'the same'}")
    every = A.read_every("rangebox, after", box.assembly, A.pairs_of(box, users), modes)
    A.go_judge("rangebox after the press", desk, every, rel_orig, flags_set, out, dz_set)
    keyway = [f_ for f_ in A.feature_list(A.sun_part(box)) if f_[0] == "User Keyway"]
    check(bool(keyway) and not keyway[0][2], f"rangebox: the User Keyway rebuilt in Sun's part after the press, code "
                                             f"{keyway[0][2] if keyway else None}")
    A.users_in_copy("rangebox, after", desk, folder, users)
    A.ahead_of(desk, "rangebox, after the press")

    say("-- rangebox  saved and closed as the user would; a second Update with nothing changed")
    frames_before = W.gear_frames(CTX["worker"], desk)
    A.save_user(folder, "the Update's result")
    flags_before = W.gearbox_flags(CTX["worker"], desk)
    left = run("rangebox: closed as the user closes it", W.quit_in(folder))
    check(not left, f"rangebox: everything of the copy closed after the save: left {left}")
    desk.plan_solidworks()
    u = desk.update
    check(u is not None and u.record_matches and not u.changed_parts,
          f"rangebox: with the record printed and the workbook Printed, Update plans nothing changed: "
          f"{[stem_of(p.path) for p in (u.changed_parts if u is not None else [])]}")
    second, _ = A.press(desk, "rangebox: a second press")
    out["second"] = A._update_fact(desk, second)  # noqa: SLF001
    note = desk.note[0] if desk.note else ""
    check(second is not None and second.ok and not second.changed and second.placed == []
          and note.startswith(ui_text.ALREADY_MATCHES) and sentence not in note,
          f"rangebox: the second press changes nothing and says {ui_text.ALREADY_MATCHES!r}, without the name "
          f"sentence: {desk.error if second is None else repr(note[:160])}")
    if second is not None:
        W.check_quiet_update(CTX["worker"], desk, second, "rangebox: the second press", frames_before, flags_before)
    marks = store.read_link_record(path)
    check(not marks.unsaved and not marks.mismatched,
          f"rangebox: the record on disk after the second press holds no unsaved or mismatched document: unsaved "
          f"{[os.path.basename(p) for p in marks.unsaved]}, mismatched {[os.path.basename(p) for p in marks.mismatched]}")


# -- the run --------------------------------------------------------------------------------------------------------------

ORDER = ["spur", "pair", "rangebox"]
SECTIONS = {"spur": section_spur, "pair": section_pair, "rangebox": section_rangebox}
FOLDERS = {"spur": ["spur"], "pair": ["pair"], "rangebox": ["rangebox"]}


def done_here(name):
    """What of a section this <out> holds already (W9a's ``done_here`` for these sections' folders)."""
    return [p for p in (os.path.join(OUT, f) for f in FOLDERS.get(name, [name])) if os.path.exists(p)]


def main():
    A.SECTIONS.clear()
    A.SECTIONS.update(SECTIONS)
    if A._given in ("", "all"):                    # noqa: SLF001
        A.CHOSEN = list(ORDER)
    A.done_here = done_here
    A.RUN_TITLE, A.JSON_STEM = "F1 demonstration", "f1-demo"
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
