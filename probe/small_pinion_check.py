r"""Six- and seven-tooth pinions on SolidWorks, through the app's own build path (the small-pinion tip cap, 0.3.2).

python.exe probe/small_pinion_check.py <repo src> <output folder under C:\> --pid PID [--log FILE] [--step N ...]

The branch fix/small-pinion-cap (a84523a, merged in 0f5a121) closes a 6- or 7-tooth pinion's tooth space with an
arc on the tip cap (``spur.caps_with_arc``: centre on the origin, ends on the two fixed involute ends, no radius
dimension) and was built on SolidWorks 2024 only. This runs it on the session given, every part through
``kind.plan`` and ``swbuild.build`` as the strip builds one, every change through ``swbuild.update_variables`` as
the strip's Update does, every pair through ``pair.assembly_plan`` and ``swbuild.build_pair``:

1. Spur, module 0.5, 6 teeth, 20°, face 5, bore 1, Recipe A: built and saved; every sketch fully defined (the
   build's own check); every feature's ``GetErrorCode2`` 0; each global read back against the maths (the build's
   own check); the volume against the outline's (``outline`` area less the bore, times the face; within 0.1 %);
   one solid body, and the largest radius of any vertex equal to the outer radius (no sliver or notch at a tip).
2. The same part through its values 6 -> 7 -> 12 -> 6 (``update_variables``; ``structural_change``'s answer
   for each step logged, as the strip would ask it with the record holding the previous values): each rebuild
   clean and the volume right. A 12-tooth part built with a chord, asked for 6: ``structural_change`` refuses
   with its sentence, so the strip sends nothing and the part is unchanged (its file's sha256 and mtime).
3. Helical, 6 teeth, 15° helix, the same module: built clean.
4. A pair of each pinion (6, 7, and 17 as the clean control) with a 24-tooth external mate, motion "gear mate",
   at the standard centre distance (``pair.assembly_plan``): the app's interference result as built, then the
   pinion driven by an angle mate on a global (as ``probe/gear_pairs_check.py`` drives one) to 10° and on by a
   quarter, a half and three quarters of its pitch, the mate following by its gear mate, and
   ``interference_count`` read at each. Undercut is warned about and not modelled, so a small pinion's root may
   clash with the mate's tips: the volumes are facts, not verdicts; only the 17-tooth control must be clean.

Only documents this run made (under its output folder) are saved and closed; refuses to start unless the session
is the PID given and no other document is open.
"""

import hashlib
import math
import os
import sys
import time
import traceback

sys.path.insert(0, sys.argv[1])
OUT = sys.argv[2]
PID = int(sys.argv[sys.argv.index("--pid") + 1])
LOG_PATH = sys.argv[sys.argv.index("--log") + 1] if "--log" in sys.argv else os.path.join(OUT, "small-pinion.log")
STEPS = [sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == "--step"] or ["1", "2", "3", "4"]

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

from gear_generator import __version__, findings, swbuild, swcom  # noqa: E402
from gear_generator.gears import kind_for, pair, spur  # noqa: E402
from gear_generator.spec import GearSpec  # noqa: E402
from gear_generator.store import same_path  # noqa: E402
from gear_generator.swcom import call  # noqa: E402

LOG, FAILS = [], []
VOLUME_TOLERANCE = 1e-3          # relative
TIP_TOLERANCE = 0.005            # mm, 1 % of the module, on a tip corner's radius against the outer radius
DRIVE_FROM = 10.0                # degrees, as gear_pairs_check
MATE_ANGLE, ALIGN_CLOSEST = findings.MATE_ANGLE, 2


def say(line=""):
    print(line, flush=True)
    LOG.append(line)


def check(ok, what):
    say(("ok      " if ok else "FAIL    ") + what)
    if not ok:
        FAILS.append(what)
    return ok


def run(worker, fn, timeout=1800):
    value, error = worker.submit(fn).wait(timeout=timeout)
    if error is not None:
        raise error
    return value


def documents(app):
    out, doc = [], call(app, "GetFirstDocument")
    while doc is not None:
        out.append(doc)
        doc = call(doc, "GetNext")
    return out


def ours(path):
    root = os.path.normcase(os.path.abspath(OUT)).rstrip("\\/") + os.sep
    return bool(path) and os.path.normcase(os.path.abspath(path)).startswith(root)


def spec_of(teeth, **extra):
    fields = dict(module="0.5", teeth=str(teeth), pressure_angle="20", face_width="5", bore="1",
                  recipe=spur.RECIPE_INVOLUTE)
    fields.update(extra)
    return GearSpec(**fields)


def expected_volume(spec):
    kind = kind_for(spec)
    derived = kind.derive(spec)
    outline = kind.outline(spec, derived, kind.recipe_for(spec))
    bore = float(spec.bore) if spec.bore else 0.0
    return (spur.signed_area(outline[:-1]) - math.pi * (bore / 2) ** 2) * float(spec.face_width)


def readings(session):
    """The build document as SolidWorks holds it now: volume, solid bodies, every feature's error code, the largest
    and the tip-band vertex radii (mm), and the Equation Manager's Status (logged, not judged)."""
    doc = session._doc()  # noqa: SLF001
    errors = []
    feature = call(doc, "FirstFeature")
    while feature is not None:
        answer = call(feature, "GetErrorCode2", swcom._out_bool())  # noqa: SLF001
        code = swcom._by_ref(answer[0] if isinstance(answer, tuple) else answer)  # noqa: SLF001
        if code:
            errors.append((str(call(feature, "Name")), code))
        feature = call(feature, "GetNextFeature")
    bodies = call(doc, "GetBodies2", 0, True) or ()
    radii = []
    for body in bodies:
        for vertex in swcom._read(body, "GetVertices") or ():  # noqa: SLF001 - a method late binding hands back
            point = swcom._read(vertex, "GetPoint")  # noqa: SLF001
            radii.append(math.hypot(float(point[0]), float(point[1])) * 1000.0)
    try:
        status = swcom._read(call(doc, "GetEquationMgr"), "Status")  # noqa: SLF001
    except Exception as exc:  # noqa: BLE001 - logged only
        status = f"raised {exc}"
    return {"volume": session.volume_mm3(), "bodies": len(bodies), "errors": errors,
            "radii": sorted(radii), "equation_status": status}


def judge_part(label, spec, read, rebuilt=True):
    kind = kind_for(spec)
    derived = kind.derive(spec)
    want = expected_volume(spec)
    off = (read["volume"] - want) / want
    ra = getattr(derived, "ra", None) or getattr(derived, "section").ra
    top = read["radii"][-1] if read["radii"] else float("nan")
    near = [r for r in read["radii"] if ra - 0.1 * float(spec.module) < r < ra - 1e-6]
    tips = [r for r in read["radii"] if r >= ra - 1e-6]
    say(f"        {label}: volume {read['volume']:.5f} mm³ (outline's {want:.5f}, off {off * 100:+.4f} %); bodies "
        f"{read['bodies']}; feature errors {read['errors']}; Equation Manager Status {read['equation_status']!r}; "
        f"largest vertex radius {top:.6f} for an outer radius {ra:.6f}; vertices just inside the tips {len(near)}")
    check(rebuilt and not read["errors"], f"{label}: the rebuild is clean, no feature in error: {read['errors']}")
    check(abs(off) <= VOLUME_TOLERANCE, f"{label}: the volume within 0.1 % of the outline's ({off * 100:+.4f} %)")
    # A tip corner of an extruded cut sits where the flank meets the outer cylinder at a shallow angle; SolidWorks
    # places that vertex a few microns out on a 6-tooth spur (2.5 µm on SolidWorks 2026; 0.5 µm on a chord-built
    # 12, the design before the arc), so the tips are judged by their corners: four per tooth (two per face), all
    # on the outer radius to within TIP_TOLERANCE, and no vertex just inside it.
    teeth = int(spec.teeth)
    check(read["bodies"] == 1 and len(tips) == 4 * teeth and all(r - ra <= TIP_TOLERANCE for r in tips) and not near,
          f"{label}: one solid body, the tips intact: {len(tips)} tip corners for {teeth} teeth (4 each), the "
          f"farthest {top - ra:.2e} mm beyond the outer radius {ra:.6f} (within {TIP_TOLERANCE:g}), no vertex just "
          f"inside it: {[round(r, 6) for r in near][:6]}")


def build_part(worker, spec, path, label):
    kind = kind_for(spec)
    derived = kind.derive(spec)
    recipe = kind.recipe_for(spec)
    say(f"part    {label}: {spec.kind} {spec.teeth} teeth, module {spec.module}, recipe {recipe}, arc on the tip cap "
        f"{spur.caps_with_arc(getattr(derived, 'section', derived), recipe)}")
    for d in kind.validate(spec, derived):
        say(f"        {d.level:7} {d.message}")
    plan = kind.plan(spec, derived, recipe, "", path)
    started = time.monotonic()

    def job(session):
        result = swbuild.build(session, plan)
        return result, (readings(session) if result.ok else None)
    result, read = run(worker, job)
    for line in result.log_lines():
        LOG.append("        " + line)
    say(f"        built in {time.monotonic() - started:.1f} s: ok {result.ok}, saved {result.saved!r}, checks "
        f"{result.checks}")
    sketches = [d for d in result.done if d.endswith("is fully defined")]
    check(result.ok and bool(result.saved) and not result.checks,
          f"{label}: built and saved, every sketch fully defined ({sketches}), the globals read back against the maths")
    if read is not None:
        judge_part(label, spec, read)
    return result


def update_part(worker, path, old, new, label):
    reason = swbuild.structural_change(old.to_dict(), new.to_dict())
    say(f"update  {label}: {old.teeth} -> {new.teeth} teeth; structural_change with the record holding "
        f"{old.teeth}: {reason!r}")
    kind = kind_for(new)
    variables = kind.variables(new, kind.derive(new))

    def job(session):
        session.begin_build()
        try:
            session.open_document(path)
        finally:
            session.end_build()
        result = swbuild.update_variables(session, variables, path)
        return result, readings(session)
    result, read = run(worker, job)
    say(f"        changed {result.changed}; rebuilt {result.rebuilt}; failures {result.failures}")
    check(result.rebuilt and not result.failures, f"{label}: the values set and the part rebuilt clean")
    judge_part(label, new, read, result.rebuilt)


def drive_phases(session, asm_path, pinion_path, mate_path, pitch):
    """Interference as built, then the pinion driven to DRIVE_FROM and on by a quarter, a half and three quarters
    of its pitch by an angle mate on a global (gear_pairs_check's route), the mate following by its gear mate."""
    app = session._app  # noqa: SLF001
    asm = next(d for d in documents(app) if same_path(str(call(d, "GetPathName") or ""), asm_path))
    components = list(call(asm, "GetComponents", True) or ())
    first = next(c for c in components if same_path(str(call(c, "GetPathName")), pinion_path))
    second = next(c for c in components if same_path(str(call(c, "GetPathName")), mate_path))

    def turn(component):
        data = call(call(component, "Transform2"), "ArrayData")
        return math.degrees(math.atan2(float(data[1]), float(data[0])))
    session._build_doc = asm  # noqa: SLF001 - interference_count reads the build's document
    out = [("as built", turn(first), turn(second), session.interference_count())]

    def planes(doc):
        found, feature = [], call(doc, "FirstFeature")
        while feature is not None:
            if str(call(feature, "GetTypeName2")) == "RefPlane":
                found.append(feature)
            feature = call(feature, "GetNextFeature")
        return found

    def mates():
        found, feature = [], call(asm, "FirstFeature")
        while feature is not None:
            if str(call(feature, "GetTypeName2")) == "MateGroup":
                child = call(feature, "GetFirstSubFeature")
                while child is not None:
                    found.append(child)
                    child = call(child, "GetNextSubFeature")
            feature = call(feature, "GetNextFeature")
        return found
    top = str(call(planes(call(first, "GetModelDoc2"))[1], "Name"))
    call(asm, "ClearSelection2", True)
    if not (call(call(first, "FeatureByName", top), "Select2", False, 1) and call(planes(asm)[1], "Select2", True, 1)):
        raise RuntimeError("the pinion's Top plane and the assembly's could not both be selected")
    before = [str(call(m, "Name")) for m in mates()]
    call(asm, "AddMate5", MATE_ANGLE, ALIGN_CLOSEST, False, 0.0, 0.0, 0.0, 1.0, 1.0, math.radians(DRIVE_FROM),
         math.radians(DRIVE_FROM), math.radians(DRIVE_FROM), False, False, 0, swcom._out_long())  # noqa: SLF001
    call(asm, "ClearSelection2", True)
    made = [m for m in mates() if str(call(m, "Name")) not in before]
    if len(made) != 1:
        raise RuntimeError(f"the drive angle mate made {len(made)} mates")
    made[0].Name = "Drive"
    dims = []
    display = call(made[0], "GetFirstDisplayDimension")
    while display is not None:
        dims.append(call(display, "GetDimension2", 0))
        display = call(made[0], "GetNextDisplayDimension", display)
    dim = next(d for d in dims if abs(float(call(d, "SystemValue")) - math.radians(DRIVE_FROM)) < 1e-9)
    eqm = call(asm, "GetEquationMgr")
    index = int(call(eqm, "Add2", -1, f'"Drive"= {DRIVE_FROM:g}', True))
    link = int(call(eqm, "Add2", -1, f'"{call(dim, "Name")}@Drive"= "Drive"', True))
    if index < 0 or link < 0:
        raise RuntimeError(f"the drive global or its link was refused ({index}, {link})")
    for k in range(4):
        angle = DRIVE_FROM + k * pitch / 4
        swcom._put_indexed(eqm, "Equation", index, f'"Drive"= {angle:.9f}')  # noqa: SLF001
        call(asm, "ForceRebuild3", False)
        out.append((f"driven to {angle:.4f}° (+{k}/4 pitch)", turn(first), turn(second), session.interference_count()))
    return out


def close_ours(session):
    app = session._app  # noqa: SLF001
    for doc in documents(app):
        path = str(call(doc, "GetPathName") or "")
        if ours(path) and call(doc, "GetSaveFlag") and int(call(doc, "GetType")) == 1:
            call(call(doc, "Extension"), "SaveAs3", path, 0, 1, swcom._null_dispatch(),  # noqa: SLF001
                 swcom._null_dispatch(), swcom._out_long(), swcom._out_long())  # noqa: SLF001
    for kind in (2, 1):
        for doc in documents(app):
            if ours(str(call(doc, "GetPathName") or "")) and int(call(doc, "GetType")) == kind:
                call(app, "QuitDoc" if kind == 2 else "CloseDoc", str(call(doc, "GetTitle")))
    return [str(call(d, "GetTitle")) for d in documents(app) if ours(str(call(d, "GetPathName") or ""))]


def stamp(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest(), os.stat(path).st_mtime_ns


def pair_case(worker, teeth, label):
    pinion, mate = spec_of(teeth), spec_of(24, bore="2")
    folder = os.path.join(OUT, f"pair-{teeth}")
    os.makedirs(folder)
    paths = [os.path.join(folder, f"pinion {teeth}.SLDPRT"), os.path.join(folder, "gear 24.SLDPRT")]
    path_pair = os.path.join(folder, f"pair {teeth}-24.SLDASM")
    plans = []
    for s, p in zip((pinion, mate), paths):
        k = kind_for(s)
        plans.append(k.plan(s, k.derive(s), k.recipe_for(s), "", p))
    assembly = pair.assembly_plan(pinion, mate, paths[0], paths[1], "", path_pair, motion="gear mate")
    centre = next((op.at for op in assembly.ops if getattr(op, "at", None) and abs(op.at[0]) > 1e-9), None)
    say(f"pair    {label}: {teeth} / 24, module 0.5, gear mate; centre distance {0.5 * (teeth + 24) / 2:g} mm "
        f"(the plan places the mate at {centre})")
    started = time.monotonic()
    result = run(worker, lambda s: swbuild.build_pair(s, plans[0], plans[1], assembly))
    for line in result.log_lines():
        LOG.append("        " + line)
    say(f"        built in {time.monotonic() - started:.1f} s: ok {result.ok}; the app's interference result: "
        f"{[d for d in (result.assembly.done if result.assembly else []) if 'interfer' in d]} "
        f"{result.assembly.checks if result.assembly else None}")
    if not (result.ok and result.assembly is not None and result.assembly.ok):
        check(False, f"{label}: the pair built: {result.skipped!r}")
        return
    phases = run(worker, lambda s: drive_phases(s, path_pair, paths[0], paths[1], 360.0 / teeth), 900)
    for what, a, b, (count, volume) in phases:
        say(f"fact    {label}, {what}: pinion at {a:.4f}°, gear at {b:.4f}°; interference {count} place(s), "
            f"{volume:.6f} mm³")
    if teeth == 17:
        check(all(c == 0 for _, _, _, (c, _) in phases), f"{label}: the 17-tooth control is clean at every phase")
    left = run(worker, close_ours, 600)
    say(f"        closed: left {left}")


def main():
    os.makedirs(OUT, exist_ok=True)
    say(f"run     {time.strftime('%Y-%m-%d %H:%M:%S')}; app gear-generator {__version__} from {sys.argv[1]}")

    def connect():
        found = [c for c in swcom.find_candidates() if c.pid == PID]
        if not found:
            raise swcom.NotRunning(f"No SolidWorks session with PID {PID} is reachable.")
        return swcom.Session(found[0].app, found[0].revision, found[0].pid)
    worker = swcom.Worker(connect)
    try:
        label, pid = run(worker, lambda s: (s.label, s.pid), 120)
        say(f"attach  {label}, PID {pid}")
        before = run(worker, lambda s: len(documents(s._app)), 120)  # noqa: SLF001
        if pid != PID or before:
            say(f"STOP    PID {pid} for {PID}, {before} document(s) open: nothing is touched")
            return 2
        steps = [("1", lambda: step1(worker)), ("2", lambda: step2(worker)), ("3", lambda: step3(worker)),
                 ("4", lambda: [pair_case(worker, z, f"pair {z}/24") for z in (6, 7, 17)])]
        for name, fn in steps:
            if name not in STEPS:
                continue
            try:
                fn()
            except Exception as exc:  # noqa: BLE001 - logged, and the next step still runs
                check(False, f"step {name} raised {type(exc).__name__}: {exc}")
                for line in traceback.format_exc().splitlines():
                    say("        " + line)
            finally:
                left = run(worker, close_ours, 600)
                say(f"close   after step {name}: left of ours {left}")
    finally:
        worker.shutdown()
    say(f"done    {len(FAILS)} failed: {FAILS}")
    return 0 if not FAILS else 1


def step1(worker):
    say("== 1   spur, module 0.5, 6 teeth, 20°, face 5, bore 1, Recipe A")
    build_part(worker, spec_of(6), os.path.join(OUT, "spur 6.SLDPRT"), "spur 6")


def step2(worker):
    say("== 2   the same part through its values 6 -> 7 -> 12 -> 6; a chord-built 12 asked for 6")
    path = os.path.join(OUT, "spur 6.SLDPRT")
    teeth = [6, 7, 12, 6]
    for old, new in zip(teeth, teeth[1:]):
        update_part(worker, path, spec_of(old), spec_of(new), f"spur {old} -> {new}")
    chord = os.path.join(OUT, "spur 12 chord.SLDPRT")
    build_part(worker, spec_of(12), chord, "spur 12 (chord)")
    run(worker, close_ours, 600)
    before = stamp(chord)
    reason = swbuild.structural_change(spec_of(12).to_dict(), spec_of(6).to_dict())
    say(f"        structural_change, a chord-built 12 asked for 6: {reason!r}")
    check(reason.startswith("At these values the tooth space needs an arc on the tip cap"),
          "the chord-built 12 asked for 6 is refused with structural_change's sentence, so nothing is sent")
    check(stamp(chord) == before, "the chord-built part's file is unchanged (sha256 and mtime)")


def step3(worker):
    say("== 3   helical, 6 teeth, 15° helix, module 0.5")
    build_part(worker, spec_of(6, kind="helical", helix_angle="15"), os.path.join(OUT, "helical 6.SLDPRT"),
               "helical 6")


if __name__ == "__main__":
    code = 1
    try:
        code = main()
    finally:
        with open(LOG_PATH, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(LOG) + "\n")
    raise SystemExit(code)
