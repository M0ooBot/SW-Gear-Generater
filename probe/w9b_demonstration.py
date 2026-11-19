r"""W9b's demonstration on SolidWorks (ISSUE-1-PLAN §5 W9b, §3 "RangeBox_Fixed", §4 M7; W9B-INTERFACES): the banded
sleeve and the hub as parts, RangeBox_Fixed built from scratch with every mode's engagement, slides and interference as
§3 gives them, a band changed by Update and a structural edit answered with Build again…, and RangeBox (no bands, no
hub) built as before W9b. The sections, what each asserts and their times are in
``docs/notes-workbook/W9B-DEMONSTRATION.md``.

python.exe probe/w9b_demonstration.py <repo src> <output folder under C:\> --pid PID [--log FILE]
                                      [--sections part,build,update,old|all] [--redo]
python probe/w9b_demonstration.py --self-check      (no SolidWorks, no Excel: §3's numbers from the fixture, the pure
                                                     judgements the live sections use, the edits' legality)
python probe/w9b_demonstration.py --help

Sections (each runs alone; ``update`` copies ``fixed.master``, which ``build`` keeps, and builds it first if this
<out> has none):

- ``part``    the banded RangeSlv of RangeBox_Fixed (face 26, bands 5/5, relief 16, Ø 25.0) and the same sleeve
              unbanded, each by the strip's own ``plan_for`` and ``swbuild.build``, read back: the three globals, the
              two planes' offsets (5 and 21) and their links, the Relief feature in no error, the relief sketches'
              diameters linked; the volumes (below); the bore over the relief from the part's faces. A band changed
              through the strip's value route (``swbuild.update_variables``) and read back as the plane's offset.
              Then the Hub part (17 teeth, face 20), built in no error.
- ``build``   RangeBox_Fixed written by the app's ``write_new`` and built from scratch by the app's own Build (W8's
              ``build_turning``, as W9a's reducer); kept as ``fixed.master``. The read's warnings are the fixture's own
              (``assess`` of it in this process, none from W9b's three checks, no stroke warning). Per mode H, N, L,
              shown and rebuilt: every body at its frame on record, the slide's value, every mate's flag (the couplings
              in H and L only), Hub as Output's anchor and RangeSlv splined to it, every app gear free to turn, no mate
              in error, no interference, and the bands, the relief and the dogs measured from the model (frames and the
              parts' own globals) against §3's table, with the least running gaps.
- ``update``  a copy of fixed.master: Start band 5 -> 4 in the workbook, a value Update, read back in the part and per
              mode as ``build``; then the bands taken off alone (refused at the workbook: the long sleeve jams L), then
              the smallest legal edit that takes them off (the workbook made RangeBox again) answered with Build
              again… in a sentence; neither writes anything to SolidWorks.
- ``old``     RangeBox as it is built by today's app: its seven warnings (§3's four and W9b's three), §3's engagement
              and speeds, the unbanded sleeve built as before W9b (sidecar schema 1, no Relief), RangeSlv still
              Output's anchor; per mode as ``build``, without bands.

**The volumes (M7).** The unbanded sleeve is one section along its face, F0 (its front end face's area, else
V / 26); a band keeps it and the relief
leaves the ring π(Ro² − r²) between the bore and the outside, Ro and r read from the part's cylinders. So V(banded) =
F0 × (b1 + b2) + π(Ro² − r²) × (26 − b1 − b2), for 5/5 and for 4/5: a coarse guard against a gross fault, its
allowance from the control in the same session (the unbanded sleeve's own V/26 against its end face's section, factor
1.0, floor 1e-4, cap 5e-4: a control over the cap fails, and with no end face read the floor alone applies). The
step faces' planes are read whole (every planar face in them) and their loops' edges integrated beside GetArea. The
area one more mm of relief removes (a difference of two volumes) is a fact, held to the hard
bounds π(R² − r_root²) and π(R² − r_tip²). The bore is found by its surface (one cylinder, r 12.5), its ends by the
planes of the two step faces (``PlaneParams``), never by ``GetBox``, which SolidWorks pads. A slide's value is read
without a sign: its size against the record's, its side by RangeSlv's own frame.

Everything W9a's script does for a run is done here by running its ``main`` with these sections: the attach, the
dialog watch and the What's Wrong rule, keep-awake, the JSON after every section, the guarded close, APPDATA in the run
folder. No document title but the run's own is logged; SolidWorks' frame is never logged.
"""

import dataclasses
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SELF_CHECK = "--self-check" in sys.argv

# Every line is written in UTF-8, whatever the console's or a pipe's encoding (Windows' python.exe writing to a pipe
# uses cp1252, which has no π or −), as the other probe scripts do.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

if "--help" in sys.argv or "-h" in sys.argv:
    print(__doc__)
    raise SystemExit(0)

# -- §3, as the plan gives it (ISSUE-1-PLAN §3, RangeBox_Fixed's table) -------------------------------------------------

MODES = ("H", "N", "L")
SECTION3 = {   # per mode: slide, the bands' and the relief's spans, what is engaged, the least running gap and where
    "H": {"slide": -7.5, "start": (-55.5, -50.5), "end": (-34.5, -29.5), "relief": (-50.5, -34.5),
          "engaged": ["HighDog"], "least": 10.0, "least_at": [("end", "LowDog")], "ratio": 1.0},
    "N": {"slide": 0.0, "start": (-48.0, -43.0), "end": (-27.0, -22.0), "relief": (-43.0, -27.0),
          "engaged": [], "least": 2.5, "least_at": [("end", "HighDog"), ("end", "LowDog")], "ratio": None},
    "L": {"slide": 7.5, "start": (-40.5, -35.5), "end": (-19.5, -14.5), "relief": (-35.5, -19.5),
          "engaged": ["LowDog"], "least": 1.0, "least_at": [("start", "HighDog")], "ratio": 2.896552},
}
DOGS = {"HighDog": (-34.5, -29.5), "LowDog": (-19.5, -14.5)}
HUB = (-55.5, -35.5)
HUB_TO_HIGHDOG = 1.0
RELIEF_D, RELIEF_LEN, PLANES = 25.0, 16.0, (5.0, 21.0)
SPAN_TOL = 1e-4            # mm: a span measured from a frame and a part's globals against §3 or the app's own
# relative, of the part's volume: SolidWorks' mass-property volume against the exact form below, a coarse guard
# against a gross fault (a relief not cut, a wrong diameter or span: Ø 0.1 mm off is 6.5e-3). Its allowance comes from
# the control in the same session, the unbanded sleeve's own residual against its end face's section (W9B-REVIEW,
# addendum for 2024): factor 1.0, floor 1e-4, cap 5e-4. On 2026 the control read 1.1e-4 and the banded parts 9.0e-5;
# on 2024 2.2e-4 and 1.3e-4 (2024's volumes run high by a constant per body; its faces read as 2026's).
VOLUME_FACTOR, VOLUME_FLOOR, VOLUME_CAP = 1.0, 1e-4, 5e-4
STEP_TOL = 1e-4            # relative: a step face's area by another route that lands on the geometry's figure
BORE_TOL = 1e-6            # mm: the relief bore's radius and its ends against the planes
# relative: two GetArea readings of faces of one section. The final 2026 run (w9b-demo-20261117-051122.json) read the
# sleeve's two end faces 440.547728 and 440.515604 mm², 7.3e-5 apart, and the front one within 5e-7 of the section the
# reviewer worked from the app's geometry (440.54751); 2e-4 holds two such readings with room.
AREA_TOL = 2e-4
# ISSUE-1-PLAN §2.2 and §2.3, word for word without their cells: RangeBox's three W9b warnings.
PLAN_W9B_WARNINGS = (
    "Output cannot reach RangeSlv: Input runs through RangeSlv's travel (from Sun at 10.5 to HighDog at −32), so Output "
    "would have to pass HighDog toward Z− or Sun toward Z+, each on Input.",
    "nothing keys RangeSlv to Output: its whole bore is teeth and no hub row is under it; add a hub on Output that a band "
    "of RangeSlv covers in every mode; as laid out none can, since its 10 mm face slides 10 mm (H −5 to L +5) and its "
    "places share no length.",
    "in N RangeSlv stands 0 mm from HighDog and 0 mm from LowDog, which it does not engage there: leave at least "
    "0.625 mm (0.5 × module) each side.")
TOL = 1e-6                 # mm: a body's frame against its frame on record (W9a's go)
BAND_EDIT = 4              # Start band 5 -> 4: legal, a value Update (the self-check shows it)
# The smallest legal edit that takes the bands off: RangeSlv as RangeBox has it, and Hub's row cleared (a 26 mm sleeve
# with no bands jams L, plan §3; with the hub there every mode must cover it).
AS_RANGEBOX = {"At (mm)": -24.5, "Face width": 10, "Slides": "H=-5, N=0, L=+5", "Start band": None, "End band": None}


def gap(a, b):
    """The axial gap between two spans (lo, hi); a negative number is their overlap."""
    if a[1] <= b[0]:
        return b[0] - a[1]
    if b[1] <= a[0]:
        return a[0] - b[1]
    return -(min(a[1], b[1]) - max(a[0], b[0]))


def covers(outer, inner, tol=SPAN_TOL):
    return outer[0] <= inner[0] + tol and inner[1] <= outer[1] + tol


def judge_mode(bands, dogs, tol=SPAN_TOL):
    """From spans alone: the dogs a band covers whole (engaged), the least gap from a band to a dog it does not engage
    and where, and whether the relief (between the bands) holds each dog."""
    engaged = sorted({d for d, s in dogs.items() for b in bands.values() if covers(b, s, tol)})
    gaps = {(w, d): gap(b, s) for w, b in bands.items() for d, s in dogs.items() if not covers(b, s, tol)}
    least = min(gaps.values()) if gaps else None
    at = sorted(k for k, v in gaps.items() if least is not None and abs(v - least) <= tol)
    relief = (bands["start"][1], bands["end"][0]) if "start" in bands and "end" in bands else None
    holds = sorted(d for d, s in dogs.items() if relief is not None and covers(relief, s, tol))
    return {"engaged": engaged, "least": least, "least_at": at, "relief": relief, "relief_holds": holds,
            "gaps": {f"{w} to {d}": round(v, 9) for (w, d), v in gaps.items()}}


def section3_of(judged, bands, mode, tol=SPAN_TOL):
    """``judge_mode``'s answer and the bands' spans against §3's row for ``mode``: a list of what differs."""
    want = SECTION3[mode]
    out = []
    for word in ("start", "end"):
        if any(abs(x - y) > tol for x, y in zip(bands[word], want[word])):
            out.append(f"{word} band {bands[word]} not {want[word]}")
    if judged["relief"] is None or any(abs(x - y) > tol for x, y in zip(judged["relief"], want["relief"])):
        out.append(f"relief {judged['relief']} not {want['relief']}")
    if judged["engaged"] != want["engaged"]:
        out.append(f"engaged {judged['engaged']} not {want['engaged']}")
    if judged["least"] is None or abs(judged["least"] - want["least"]) > tol or judged["least_at"] != want["least_at"]:
        out.append(f"least gap {judged['least']} at {judged['least_at']} not {want['least']} at {want['least_at']}")
    if mode in ("N", "L") and "HighDog" not in judged["relief_holds"]:
        out.append(f"the relief does not hold HighDog: {judged['relief_holds']}")
    return out


def app_spans(a, mode_name):
    """What the app's own read says stands where in a mode: RangeSlv's bands (``modes.band_spans``), the dogs and the
    hub (their placed z ranges)."""
    from gear_generator.workbook import modes as wm
    m = next(x for x in a.report.modes if x.name == mode_name)
    sleeve = a.spec.gear("RangeSlv")
    placed = dict(a.report.layout.placed)
    placed.update(m.placed)
    bands = {w or "whole": (lo, hi) for w, lo, hi in wm.band_spans(sleeve, placed["RangeSlv"])}
    dogs = {d: tuple(placed[d].z_range) for d in DOGS}
    hub = tuple(placed["Hub"].z_range) if "Hub" in placed else None
    return bands, dogs, hub


def w9b_check_warnings(a):
    """W9b's three checks (reach, hub, running clearance) on a read, as ``checks.check`` calls them."""
    from gear_generator.workbook import modes as wm
    placed = a.report.layout.placed
    return [d.message for d in wm.reach_warnings(a.spec, placed) + wm.hub_warnings(a.spec, placed)
            + wm.clearance_warnings(a.spec, placed, a.report.modes)]


CELL = re.compile(r"^(?:Gears|Shafts|Meshes|Modes|Box)(?:!\$?[A-Z]+\$?\d+| row \d+): ")


def bare(message):
    """A diagnostic without its cell, so a read of the spec (``Gears row 7:``) and of a workbook (``Gears!J7:``)
    compare."""
    return CELL.sub("", message)


def warnings_of(a):
    return sorted(bare(d.message) for d in a.diagnostics if d.level == "warning")


def errors_of(a):
    return [d.message for d in a.diagnostics if d.level == "error"]


def relief_bore(faces, z_lo, z_hi, radius):
    """The bore over the relief from the part's faces, exactly (W9b's first run: ``IFace2.GetBox`` is padded, the bore's
    box read z 4.76…21.24): exactly one cylinder of ``radius`` (to BORE_TOL) with its axis along the part's z, and its
    two ends the two planar step faces whose box is the cylinder's across, each plane's z from ``PlaneParams`` at
    ``z_lo`` and ``z_hi``. Returns the finding and whether it holds."""
    cyl = [f for f in faces if f["kind"] == "cylinder" and abs(f["r"] - radius) <= BORE_TOL
           and abs(abs(f["axis"][2]) - 1.0) <= 1e-9]
    out = {"cylinders": len(cyl), "r": [f["r"] for f in cyl]}
    if len(cyl) != 1:
        return out, False
    box = cyl[0]["box"]
    across = (box[0], box[1], box[3], box[4])
    steps = [f for f in faces if f.get("z") is not None and f.get("normal") is not None
             and abs(abs(f["normal"][2]) - 1.0) <= 1e-9
             and all(abs(a - b) <= 1e-6 for a, b in zip((f["box"][0], f["box"][1], f["box"][3], f["box"][4]), across))]
    steps = sorted(steps, key=lambda f: f["z"])
    ends = [f["z"] for f in steps]
    out.update(ends=ends, step_areas=[f.get("area") for f in steps], box_z=(box[2], box[5]),
               padding=(round(ends[0] - box[2], 6), round(box[5] - ends[-1], 6)) if len(ends) == 2 else None)
    held = len(ends) == 2 and abs(ends[0] - z_lo) <= BORE_TOL and abs(ends[1] - z_hi) <= BORE_TOL
    return out, held


def outer_radius(faces, face):
    """The sleeve's outer cylinder: the largest cylinder whose box runs the whole face (its radius is exact; its box,
    padded or not, is only used to tell it from the short ones)."""
    whole = [f for f in faces if f["kind"] == "cylinder" and f["box"][2] <= 1e-3 and f["box"][5] >= face - 1e-3]
    return max(f["r"] for f in whole) if whole else None


def end_areas(faces, face):
    """The part's two end faces' areas (``IFace2.GetArea``), by their plane's z (0 and ``face``)."""
    return {round(f["z"], 6): f["area"] for f in faces if f["kind"] == "plane" and f.get("z") is not None
            and f.get("area") is not None and (abs(f["z"]) <= 1e-6 or abs(f["z"] - face) <= 1e-6)}


def section_of(v_unbanded, face, areas):
    """The unbanded sleeve's section F0 (Blank, Tooth Space, Teeth: one section along its face): its front end face's
    area where GetArea read it (W9b's closing review: SolidWorks' volume carries 1.1e-4 more than that face's area
    times the face, which reads the true section), else its volume over its face. ``(F0, how)``."""
    front = areas.get(0.0)
    if front:
        return front, "the front end face's area (IFace2.GetArea)"
    return v_unbanded / face, f"the unbanded volume over its face, V/{face:g} (no end face's area read)"


def banded_volume(f0, face, bands, outer, bore):
    """What a banded sleeve's volume must be: each band keeps the section F0, and over the relief the section is the
    ring between the bore and the outside, π(Ro² − r²)."""
    relief = face - bands[0] - bands[1]
    return f0 * (bands[0] + bands[1]) + math.pi * (outer * outer - bore * bore) * relief


def step_area(f0, outer, bore):
    """Each step face at a band's end, by the same geometry: the section less the ring over the relief."""
    return f0 - math.pi * (outer * outer - bore * bore)


def volume_guard(rows, v0, length, f0, from_face, outer, bore):
    """The coarse volume guard, its allowance taken from the control in the same session (W9B-REVIEW, addendum for
    2024): the unbanded sleeve's own residual, |V0/face − F0| / F0, against its end face's section F0. The allowance
    is max(VOLUME_FLOOR, VOLUME_FACTOR × that); a control above VOLUME_CAP means the session's mass properties are
    not fit to judge by, and the guard fails. Where F0 is V0/face itself (no end face read) there is no control and
    the floor alone applies. ``rows``: (label, volume, (start band, end band)). The guard is for gross faults: each
    row also carries what a relief Ø 0.1 mm off would move it by. Returns the control, the allowance, whether the
    control is fit, and each row's expected volume, residual, room left and verdict."""
    control = abs(v0 / length - f0) / f0 if from_face else None
    allowance = VOLUME_FLOOR if control is None else max(VOLUME_FLOOR, VOLUME_FACTOR * control)
    fit = control is None or control <= VOLUME_CAP
    out = {"control": control, "allowance": allowance, "fit": fit, "rows": {}}
    for label, volume, bands in rows:
        want = banded_volume(f0, length, bands, outer, bore)
        res = abs(volume - want) / volume
        gross = abs(banded_volume(f0, length, bands, outer, bore + 0.05) - want) / volume
        out["rows"][label] = {"volume": volume, "want": want, "residual": res, "room": 1 - res / allowance,
                              "gross": gross, "ok": fit and res <= allowance}
    return out


def volume_guard_lines(g, length, f0, how):
    """``volume_guard``'s answer as the log says it: ``[(is a check, holds, sentence)]``: the control first, then
    each row."""
    if g["control"] is None:
        lines = [(False, True, f"the volume guard has no control: F0 {f0:.6f} mm² is {how}, so the floor "
                               f"{VOLUME_FLOOR:g} alone is the allowance")]
    else:
        over = "" if g["fit"] else ": over it, so this session's mass properties are not fit to judge by"
        lines = [(True, g["fit"], f"the volume guard's control, the unbanded sleeve in this session: V/{length:g} "
                                  f"against its end face's section F0 {f0:.6f} mm² reads {g['control']:.1e} (cap "
                                  f"{VOLUME_CAP:g}{over}"
                                  f"); the allowance is max({VOLUME_FLOOR:g}, {VOLUME_FACTOR:g} × {g['control']:.1e}) "
                                  f"= {g['allowance']:.1e}")]
    for label, r in g["rows"].items():
        lines.append((g["fit"], r["ok"], f"the banded part's volume ({label}), a coarse guard: {r['volume']:.6f} against "
                                         f"{r['want']:.6f} mm³ (F0 over the bands, the ring π(Ro² − r²) over the relief)"
                                         f", residual {r['residual']:.1e} against the allowance {g['allowance']:.1e}, "
                                         f"{r['room']:.0%} of it left; the guard is for gross faults: a relief Ø 0.1 mm "
                                         f"off moves it {r['gross']:.1e}"))
    return lines


def faces_in_planes(faces, zs, tol=BORE_TOL):
    """Every planar face whose plane (by ``PlaneParams``: its normal along z, its z) is one of ``zs``: per plane, the
    count, each area and their sum (None where an area did not read)."""
    out = {}
    for z in zs:
        at = [f for f in faces if f["kind"] == "plane" and f.get("z") is not None and f.get("normal") is not None
              and abs(abs(f["normal"][2]) - 1.0) <= 1e-9 and abs(f["z"] - z) <= tol]
        areas = [f.get("area") for f in at]
        out[z] = {"count": len(at), "areas": areas,
                  "sum": round(sum(areas), 9) if at and None not in areas else None}
    return out


def chain_area(edges, tol=1e-6):
    """A closed loop's area from its edges, each a list of (x, y) points along it (mm) in either direction and in any
    order: chained end to start by the nearest free end, then the shoelace. Returns ``(area, largest gap where
    two edges meet)``; the area is unsigned."""
    left = [list(e) for e in edges if len(e) >= 2]
    if not left:
        return 0.0, None
    path, worst = list(left.pop(0)), 0.0
    while left:
        end = path[-1]
        best = min(range(len(left)), key=lambda i: min(math.dist(end, left[i][0]), math.dist(end, left[i][-1])))
        e = left.pop(best)
        if math.dist(end, e[-1]) < math.dist(end, e[0]):
            e.reverse()
        worst = max(worst, math.dist(end, e[0]))
        path.extend(e[1:])
    worst = max(worst, math.dist(path[-1], path[0]))
    area = 0.5 * sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(path, path[1:] + path[:1]))
    return abs(area), worst


def face_area_from_loops(loops):
    """A planar face's area from its loops, each ``{"outer": bool or None, "edges": [[(x, y), ...], ...]}``: the
    outer loop's area less each other loop's. Where no loop says it is outer, the largest is taken as it. Returns
    the area, each loop's area and the largest gap in any loop."""
    areas = [chain_area(lp["edges"]) for lp in loops]
    if not areas:
        return None, [], None
    outer = next((i for i, lp in enumerate(loops) if lp.get("outer")), None)
    if outer is None:
        outer = max(range(len(areas)), key=lambda i: areas[i][0])
    total = areas[outer][0] - sum(a for i, (a, _) in enumerate(areas) if i != outer)
    return total, [a for a, _ in areas], max((g for _, g in areas if g is not None), default=None)


def slide_agrees(value, recorded, origin_z, tol=TOL):
    """A slide read back: SolidWorks gives a distance mate's dimension without a sign, and the record holds the signed
    z_front (the plan sets |z_front| and the mate's Flip carries the side: ``swbuild.ModeStep.values``). So its size
    against the record's, and the sign by the slider's own frame: its origin, its Front plane, at the signed value."""
    return abs(abs(value) - abs(recorded)) <= tol and abs(origin_z - recorded) <= tol


def section_area_bounds(derived, diameter):
    """The hard bounds on the area one more mm of relief removes: the ring between the roots and the relief circle
    (no tooth at all) and the ring between the tips and it (a full ring of teeth), in mm²."""
    r = diameter / 2.0
    return math.pi * (r * r - derived.rf ** 2), math.pi * (r * r - derived.ra ** 2)


# -- --self-check: §3 from the fixture, no SolidWorks ---------------------------------------------------------------


def _fixtures():
    import importlib.util
    spec = importlib.util.spec_from_file_location("workbook_fixtures", os.path.join(REPO, "tests", "workbook_fixtures.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def with_gear(spec, gid, **changes):
    return dataclasses.replace(spec, gears=tuple(dataclasses.replace(g, **changes) if g.id == gid else g
                                                 for g in spec.gears))


def as_rangebox(spec):
    """The workbook edit ``update`` makes in Excel, on a spec: RangeSlv as RangeBox has it and Hub's row gone."""
    spec = with_gear(spec, "RangeSlv", at="-24.5", face_width="10", slides="H=-5, N=0, L=+5", start_band="",
                     end_band="")
    return dataclasses.replace(spec, gears=tuple(g for g in spec.gears if g.id != "Hub"))


FIRST_RUN = ("probe/results/w9b-demo-20261117-045137.json", "probe/results/w9b-demo-sw2026-20261117-1-script-faults.log")


def replay_first_run(ok):
    """The three judgements corrected after W9b's first 2026 run (2ed441b) replayed on what that run read: its faces
    and volumes (JSON) and its slides (log). That run kept no plane's PlaneParams, so a planar face thin in z is given
    the normal z and the z its box centres on, which the padded boxes (4.759716…5.240284) put exactly at the plane."""
    import json
    paths = [os.path.join(REPO, p) for p in FIRST_RUN]
    if not all(os.path.isfile(p) for p in paths):
        print(f"skip    the first run's readings are not here: {FIRST_RUN}")
        return
    part = json.load(open(paths[0], encoding="utf-8"))["sections"]["part"]

    def planes_given(faces):
        out = []
        for f in faces:
            f = dict(f)
            if f["kind"] == "4001" and f["box"][5] - f["box"][2] < 1.0:
                f.update(kind="plane", normal=[0.0, 0.0, 1.0], z=round((f["box"][2] + f["box"][5]) / 2, 9))
            out.append(f)
        return out
    for key, z_lo in (("banded", PLANES[0]), ("band_changed", float(BAND_EDIT))):
        found, held = relief_bore(planes_given(part[key]["faces"]), z_lo, PLANES[1], RELIEF_D / 2)
        ok(held, f"replay {key}: the bore is one cylinder r {RELIEF_D / 2}, its ends at {z_lo} and {PLANES[1]}: {found}")
    faces = part["banded"]["faces"]
    outer, bore = outer_radius(faces, 26.0), RELIEF_D / 2
    v0, v1, v2 = part["unbanded"]["volume"], part["banded"]["volume"], part["band_changed"]["volume"]
    f0, how = section_of(v0, 26.0, {})
    g = volume_guard((("5/5", v1, (5.0, 5.0)), ("4/5", v2, (4.0, 5.0))), v0, 26.0, f0, False, outer, bore)
    for is_check, holds, text in volume_guard_lines(g, 26.0, f0, how):
        if is_check:
            ok(holds, f"replay first: {text}")
        else:
            print(f"fact    replay first: {text}")
    wrong = banded_volume(f0, 26.0, (5.0, 5.0), outer, bore + 0.25)
    ok(abs(v1 - wrong) > VOLUME_CAP * v1, f"replay volume: a relief 0.5 mm wider would fail by "
                                          f"{abs(v1 - wrong) / v1:.1e} of the volume, past even the cap {VOLUME_CAP:g}")
    pattern = re.compile(r"^FAIL    (build|update|old), ([HNL]) shown: .*RangeSlv along Output (-?[\d.]+) mm as on record "
                         r"\((-?[\d.]+)\)")
    origin = re.compile(r"^fact    (build|update|old), ([HNL]): measured bands \{'(?:start|whole)': \((-?[\d.]+),")
    slides, origins = {}, {}
    for line in open(paths[1], encoding="utf-8"):
        m = pattern.match(line)
        if m:
            slides[(m.group(1), m.group(2))] = (float(m.group(3)), float(m.group(4)))
        m = origin.match(line)
        if m:
            origins[(m.group(1), m.group(2))] = float(m.group(3))
    agreed = {k: slide_agrees(v[0], v[1], origins.get(k, float("nan"))) for k, v in slides.items()}
    ok(len(slides) == 9 and all(agreed.values()),
       f"replay slides: the nine readings that failed now agree by size and by RangeSlv's Front plane: {agreed}")
    flipped = all(not slide_agrees(v[0], v[1], -origins[k]) for k, v in slides.items())
    ok(flipped, "replay slides: a frame on the other side of the Front plane would still fail them")


FINAL_RUN = "probe/results/w9b-demo-20261117-051122.json"
FINAL_LOG = "probe/results/w9b-demo-sw2026-20261117-2.log"
RUN_2024 = "probe/results/sw2024/w9b-demo-20261117-063302.json"
F0_IN_LOG = re.compile(r"F0 two ways: .*\(IFace2\.GetArea\) ([\d.]+) mm²")


def replay_guard(ok, label, part, f0, how, from_face):
    """The volume guard and the step faces replayed on one run's readings: the guard from the control in the same
    run (``volume_guard``), and every planar face lying in the step planes, summed (``faces_in_planes``), against
    F0 − π(Ro² − r²). Returns the guard."""
    v0, v1, v2 = part["unbanded"]["volume"], part["banded"]["volume"], part["band_changed"]["volume"]
    outer = outer_radius(part["banded"]["faces"], 26.0)
    g = volume_guard((("5/5", v1, (5.0, 5.0)), ("4/5", v2, (4.0, 5.0))), v0, 26.0, f0, from_face, outer,
                     RELIEF_D / 2)
    for is_check, holds, text in volume_guard_lines(g, 26.0, f0, how):
        if is_check:
            ok(holds, f"replay {label}: {text}")
        else:
            print(f"fact    replay {label}: {text}")
    old = [k for k, r in g["rows"].items() if r["residual"] > VOLUME_FLOOR]
    print(f"fact    replay {label}: against the fixed 1e-4 the guard had before, {old or 'no row'} would fail")
    want = step_area(f0, outer, RELIEF_D / 2)
    for key, zs in (("banded", PLANES), ("band_changed", (float(BAND_EDIT), PLANES[1]))):
        planes = faces_in_planes(part[key]["faces"], zs)
        sums = {z: p["sum"] for z, p in planes.items()}
        print(f"fact    replay {label} {key}: every planar face in the step planes z {zs} (PlaneParams): "
              f"{ {z: (p['count'], p['areas']) for z, p in planes.items()} }; the cap is "
              f"{'one face' if all(p['count'] == 1 for p in planes.values()) else 'several faces'} at each; summed "
              f"against F0 − π(Ro² − r²) = {want:.6f}: "
              f"{ {z: f'{(v - want) / want:+.1e}' if v else None for z, v in sums.items()} }")
    return g


def replay_final_run(ok):
    """The closing review's points replayed on the final 2026 run's readings (its faces carry PlaneParams and GetArea):
    the section from the front end face, the volumes under the guard from the same run's control, the step faces.
    That run's JSON predates the section-level end-face reads, so F0 is the front end face's area as its log gives it
    (``F0 two ways``), as the review's addendum says to take it."""
    import json
    path, log = os.path.join(REPO, FINAL_RUN), os.path.join(REPO, FINAL_LOG)
    if not (os.path.isfile(path) and os.path.isfile(log)):
        print(f"skip    the final run's readings are not here: {FINAL_RUN}, {FINAL_LOG}")
        return
    part = json.load(open(path, encoding="utf-8"))["sections"]["part"]
    logged = [float(m.group(1)) for m in map(F0_IN_LOG.search, open(log, encoding="utf-8")) if m]
    ok(len(logged) == 1, f"replay final: the run's log gives the front end face's area once: {logged}")
    if not logged:
        return
    f0, how = logged[0], f"the front end face's area as the 2026 log gives it ({FINAL_LOG}, 'F0 two ways')"
    v0 = part["unbanded"]["volume"]
    areas = end_areas(part["unbanded"]["faces"], 26.0)
    ok(abs(f0 - 440.54751) <= AREA_TOL * f0 and abs(f0 - areas.get(0.0, 0.0)) <= 1e-6 * f0,
       f"replay final: F0 {f0:.6f} mm² from the log (the review's worked section 440.54751; the JSON's front face "
       f"{areas.get(0.0)}); the back face {areas.get(26.0)}, V/26 {v0 / 26:.6f} ({(v0 / 26 - f0) / f0:+.1e} of it)")
    ok(len(areas) == 2 and abs(areas[0.0] - areas[26.0]) <= AREA_TOL * f0,
       f"replay final: the two end faces of one section agree to {AREA_TOL:g}: {areas}")
    for key, z_lo in (("banded", PLANES[0]), ("band_changed", float(BAND_EDIT))):
        found, held = relief_bore(part[key]["faces"], z_lo, PLANES[1], RELIEF_D / 2)
        ok(held, f"replay final {key}: the bore and its ends, read with PlaneParams: {found}")
    g = replay_guard(ok, "final 2026", part, f0, how, True)
    rows = g["rows"]
    ok(abs(g["control"] - 1.1e-4) < 0.05e-4 and abs(rows["5/5"]["residual"] - 9.0e-5) < 0.05e-5,
       f"replay final 2026: the review's figures, control 1.1e-4 and 5/5 9.0e-5: {g['control']:.2e}, "
       f"{rows['5/5']['residual']:.2e}")
    found, _ = relief_bore(part["banded"]["faces"], PLANES[0], PLANES[1], RELIEF_D / 2)
    steps = found.get("step_areas") or []
    ok(len(steps) == 2 and abs(steps[0] - steps[1]) <= AREA_TOL * steps[0],
       f"replay final: the relief's two step faces read one area to {AREA_TOL:g}: {steps}")


def replay_2024(ok):
    """W9b's 2024 run (9e77303): its two volume FAILs under the fixed 1e-4, replayed under the guard from the same
    session's control; F0 its front end face's area from the JSON."""
    import json
    path = os.path.join(REPO, RUN_2024)
    if not os.path.isfile(path):
        print(f"skip    the 2024 run's readings are not here: {RUN_2024}")
        return
    part = json.load(open(path, encoding="utf-8"))["sections"]["part"]
    v0 = part["unbanded"]["volume"]
    areas = end_areas(part["unbanded"]["faces"], 26.0)
    f0, how = section_of(v0, 26.0, areas)
    ok(how.startswith("the front end face") and abs(f0 - 440.54751) <= AREA_TOL * f0,
       f"replay 2024: F0 from {how} {f0:.6f} mm² (2026's 440.547728; the review's worked section 440.54751)")
    for key, z_lo in (("banded", PLANES[0]), ("band_changed", float(BAND_EDIT))):
        found, held = relief_bore(part[key]["faces"], z_lo, PLANES[1], RELIEF_D / 2)
        ok(held, f"replay 2024 {key}: the bore and its ends, read with PlaneParams: {found}")
    g = replay_guard(ok, "2024", part, f0, how, True)
    rows = g["rows"]
    ok(abs(g["control"] - 2.2e-4) < 0.05e-4 and abs(rows["5/5"]["residual"] - 1.3e-4) < 0.05e-4,
       f"replay 2024: the review's figures, control 2.2e-4 and 5/5 1.3e-4: {g['control']:.2e}, "
       f"{rows['5/5']['residual']:.2e}")


def self_check():
    sys.path.insert(0, os.path.join(REPO, "src"))
    from gear_generator.gears import clutch, kind_for, plan_for
    from gear_generator.workbook import assess
    fx = _fixtures()
    bad = []

    def ok(cond, what):
        print(("ok      " if cond else "FAIL    ") + what)
        if not cond:
            bad.append(what)

    def assessed(spec):
        return assess.assess(dataclasses.replace(spec, source_path="C:\\B\\X.xlsx"), [], "C:\\Out\\")

    fixed, old = fx.range_box_fixed(), fx.range_box()
    a = assessed(fixed)
    ok(errors_of(a) == [] and a.lay_out_refusal() == "", f"RangeBox_Fixed reads with no error: {errors_of(a)}")
    ok(len(warnings_of(a)) == 4 and w9b_check_warnings(a) == []
       and not any("would hold both at once" in m for m in warnings_of(a)),
       f"RangeBox_Fixed: the fixture's own four warnings, none from W9b's checks, no stroke warning: {warnings_of(a)}")
    modes_ = {m.name: m for m in a.report.modes}
    ok(abs(modes_["H"].ratio - 1.0) < 1e-9 and round(modes_["L"].ratio, 6) == 2.896552
       and modes_["N"].ratio_why == "neutral", "ratios: H 1.000, L 2.896552, N neutral")
    for mode in MODES:
        bands, dogs, hub = app_spans(a, mode)
        judged = judge_mode(bands, dogs)
        ok(section3_of(judged, bands, mode) == [] and [g for _, g in modes_[mode].engaged] == SECTION3[mode]["engaged"],
           f"{mode}: the app's spans judged as the live read will judge them are §3's: {section3_of(judged, bands, mode)}"
           f" {judged}")
        ok(hub == HUB and abs(gap(hub, dogs["HighDog"]) - HUB_TO_HIGHDOG) < SPAN_TOL,
           f"{mode}: Hub {hub}, {gap(hub, dogs['HighDog'])} from HighDog")
    sleeve = fixed.gear("RangeSlv").gear_spec(fixed.box)
    kind = kind_for(sleeve)
    derived = kind.derive(sleeve)
    plan = plan_for(sleeve, derived, "", "C:\\Out\\" + sleeve.stem() + ".SLDPRT")
    values = plan.values()
    ok(values["Start Band"] == 5 and values["End Band"] == 5 and abs(values["Relief Diameter"] - RELIEF_D) < 1e-9,
       f"the banded plan's globals: Start Band {values['Start Band']}, End Band {values['End Band']}, Relief Diameter "
       f"{values['Relief Diameter']}")
    planes = [(op.name, op.offset) for op in plan.ops if type(op).__name__ == "RefPlane" and "Relief" in op.name]
    ok([o for _, o in planes] == list(PLANES), f"the relief's planes at {planes}")
    ok(any(type(op).__name__ == "LoftCut" and op.name == clutch.RELIEF for op in plan.ops), "the Relief loft cut")
    low, high = section_area_bounds(derived, RELIEF_D)
    print(f"fact    the area one more mm of relief removes lies between {low:.3f} and {high:.3f} mm² (r_root "
          f"{derived.rf}, r_tip {derived.ra}, R {RELIEF_D / 2}); the removal over 16 mm between {16 * low:.1f} and "
          f"{16 * high:.1f} mm³")
    four = assessed(with_gear(fixed, "RangeSlv", start_band=str(BAND_EDIT)))
    ok(errors_of(four) == [] and warnings_of(four) == warnings_of(a),
       f"Start band {BAND_EDIT}: legal, the same four warnings: {errors_of(four)}")
    bands, dogs, _ = app_spans(four, "L")
    ok(abs(judge_mode(bands, dogs)["least"] - 2.0) < SPAN_TOL, f"Start band {BAND_EDIT}: L's least gap now 2.0 "
                                                                f"{judge_mode(bands, dogs)}")
    off = assessed(with_gear(fixed, "RangeSlv", start_band="", end_band=""))
    ok(any("jammed" in m for m in errors_of(off)), f"the bands off alone are refused at the workbook: {errors_of(off)}")
    rb = assessed(as_rangebox(fixed))
    ok(errors_of(rb) == [] and len(warnings_of(rb)) == 7, f"the bands taken off as RangeBox: legal, seven warnings: "
                                                         f"{errors_of(rb)}")
    ok([dataclasses.replace(g, row=0) for g in as_rangebox(fixed).gears] == [dataclasses.replace(g, row=0)
                                                                            for g in old.gears],
       "that edit's Gears rows are RangeBox's")
    o = assessed(old)
    ok(sorted(bare(m) for m in w9b_check_warnings(o)) == sorted(PLAN_W9B_WARNINGS),
       f"RangeBox's three W9b warnings are §2.2's and §2.3's sentences word for word: "
       f"{sorted(set(bare(m) for m in w9b_check_warnings(o)) ^ set(PLAN_W9B_WARNINGS))}")
    ok(len(warnings_of(o)) == 7 and len(w9b_check_warnings(o)) == 3,
       f"RangeBox: seven warnings, three of them W9b's: {[m[:60] for m in w9b_check_warnings(o)]}")
    speeds = {k: round(float(v), 3) for k, v in o.report.motion.speeds.items()}
    ok(speeds.get("Carrier") == 517.857 and speeds.get("Planet") == -1673.077, f"RangeBox's speeds: {speeds}")
    # the guard's three branches on made-up readings: a fit control, one over the cap, and no control
    g = volume_guard((("5/5", 1000.0 * (1 + 2e-4), (5.0, 5.0)),), 26.0 * 10.0 * (1 + 3e-4), 26.0, 10.0, True, 0.0, 0.0)
    ok(g["fit"] and abs(g["allowance"] - 3e-4) < 1e-9, f"guard: a control of 3e-4 allows 3e-4: {g['allowance']:.2e}")
    g = volume_guard((), 26.0 * 10.0 * (1 + 6e-4), 26.0, 10.0, True, 0.0, 0.0)
    ok(not g["fit"] and not volume_guard_lines(g, 26.0, 10.0, "x")[0][1], "guard: a control over the cap fails")
    g = volume_guard((), 260.0, 26.0, 10.0, False, 0.0, 0.0)
    ok(g["control"] is None and g["allowance"] == VOLUME_FLOOR and not volume_guard_lines(g, 26.0, 10.0, "x")[0][0],
       "guard: no end face, no control: the floor alone, said as a fact")
    g = volume_guard((), 26.0 * 10.0 * (1 + 2e-5), 26.0, 10.0, True, 0.0, 0.0)
    ok(g["allowance"] == VOLUME_FLOOR, "guard: a control under the floor allows the floor")
    # the loop integration: a 10 × 10 square less a 4 × 4 hole, its edges in any order and direction, and a circle of
    # r 12.5 in four arcs of 400 points each (the chord error is far under the 1e-4 the check would use)
    square = [[(0, 0), (10, 0)], [(10, 10), (10, 0)], [(0, 10), (10, 10)], [(0, 0), (0, 10)]]
    hole = [[(3, 3), (3, 7)], [(7, 7), (7, 3)], [(3, 7), (7, 7)], [(3, 3), (7, 3)]]
    area, each, worst = face_area_from_loops([{"outer": None, "edges": hole}, {"outer": None, "edges": square}])
    ok(abs(area - 84.0) < 1e-12 and worst < 1e-12, f"loops: a square less a hole, edges shuffled: {area}, {each}")
    arcs = [[(12.5 * math.cos(t), 12.5 * math.sin(t)) for t in
             (math.pi / 2 * (q + i / 399) for i in range(400))] for q in range(4)]
    area, _, _ = face_area_from_loops([{"outer": True, "edges": arcs[::-1]}])
    ok(abs(area - math.pi * 12.5 ** 2) / (math.pi * 12.5 ** 2) < 1e-5, f"loops: a circle in four arcs: {area:.6f}")
    replay_first_run(ok)
    replay_final_run(ok)
    replay_2024(ok)
    print(f"done    {len(bad)} failed")
    return 0 if not bad else 1


if SELF_CHECK:
    raise SystemExit(self_check())


# -- the live run: W9a's harness ------------------------------------------------------------------------------------

sys.path.insert(0, HERE)
import w9a_demonstration as A  # noqa: E402  (W8's and S0's scripts, the watch, the What's Wrong rule, Desk9, main)

W, S0 = A.W, A.S0
from gear_generator import findings, store, swbuild, swcom, ui_text  # noqa: E402
from gear_generator.gears import kind_for, plan_for  # noqa: E402
from gear_generator.gears import clutch  # noqa: E402
from gear_generator.swcom import call  # noqa: E402

say, check = W.say, W.check
OUT = W.OUT
CTX, RESULT, run, job = A.CTX, A.RESULT, A.run, A.job
EZ = findings.EXTRUDE_Z_SIGN
FIXED_MASTER = {"path": ""}
SLEEVE_GLOBALS = ("Face Width", clutch.START_BAND, clutch.END_BAND, clutch.RELIEF_DIAMETER)


def spec_fixed(folder=""):
    made = W.w8_fixtures().range_box_fixed()
    return dataclasses.replace(made, box=dataclasses.replace(made.box, output_folder=folder))


def spec_old(folder=""):
    made = W.w8_fixtures().range_box()
    return dataclasses.replace(made, box=dataclasses.replace(made.box, output_folder=folder))


# -- part --------------------------------------------------------------------------------------------------------------


def part_faces(s):
    """Every face of the active part, raw: a cylinder's radius, axis and box; any other surface's identity and box
    (mm, the part's frame; macro database reading/15)."""
    def got(obj, name):
        # A member that returns an array comes back from late binding as an uncalled bound method (macro database
        # GOTCHAS: IBody2.GetEdges, "'method' object is not iterable"; the first W9b run met it here). A value never
        # looks like a method, so what came back is tested, not the member's name.
        value = call(obj, name)
        return swcom._guarded(name, value) if type(value).__name__ == "method" else value  # noqa: SLF001

    out = []
    for body in list(call(s._doc(), "GetBodies2", 0, True) or []):  # noqa: SLF001
        for face in list(got(body, "GetFaces") or []):
            surface = got(face, "GetSurface")
            box = [round(float(v) * 1000.0, 6) for v in got(face, "GetBox")]
            if got(surface, "IsCylinder"):
                p = [float(v) for v in got(surface, "CylinderParams")]
                out.append({"kind": "cylinder", "r": round(p[6] * 1000.0, 9), "axis": [round(v, 9) for v in p[3:6]],
                            "point": [round(v * 1000.0, 9) for v in p[0:3]], "box": box})
            elif got(surface, "IsPlane"):
                # PlaneParams: the normal, then a point on the plane (m): its z exact where the box is padded.
                p = [float(v) for v in got(surface, "PlaneParams")]
                try:        # IFace2.GetArea (m²), new to this repo: an area that will not read is None, said, not fatal
                    area = round(float(got(face, "GetArea")) * 1e6, 9)
                except Exception:  # noqa: BLE001
                    area = None
                out.append({"kind": "plane", "normal": [round(v, 9) for v in p[0:3]],
                            "z": round(p[5] * 1000.0, 9) if abs(abs(p[2]) - 1.0) <= 1e-9 else None,
                            "area": area, "box": box})
            else:
                out.append({"kind": str(got(surface, "Identity")), "box": box})
    return out


STEP_CALLS = ("IFace2.GetLoops, ILoop2.IsOuter, ILoop2.GetEdges (no entry in the macro database for any of them); "
              "IEdge.GetCurve, IEdge.GetCurveParams2, ICurve.Identity, ICurve.GetTessPts and ICurve.Evaluate2 "
              "(verified on 2026 for other parts, Airfoil Converter; never on 2024); ICurve.IsCircle and "
              "ICurve.CircleParams (no entry)")


def step_faces(s, zs, chord=1e-8, length=1e-10, samples=200):
    """NEW (``STEP_CALLS``): every planar face of the active part lying in one of the planes ``zs`` (by
    ``PlaneParams``: its normal along z, its z, mm), with ``GetArea``; and of each such face, its loops (``IsOuter``),
    each loop's edges (the curve's ``Identity``, a circle's radius from ``CircleParams``, the ends from
    ``GetCurveParams2``, mm) and the points along each (``GetTessPts`` at a ``chord`` m chord tolerance, else
    ``Evaluate2`` at ``samples`` parameters), from which the face's area is integrated (``face_area_from_loops``).
    Every call is guarded: what will not read is said in its place, never fatal."""
    from win32com.client import VARIANT
    import pythoncom

    def got(obj, name, *args):
        value = call(obj, name, *args)
        return swcom._guarded(name, value) if type(value).__name__ == "method" else value  # noqa: SLF001

    def guarded(fn, default=None):
        try:
            return fn(), None
        except Exception as exc:  # noqa: BLE001
            return default, f"{type(exc).__name__}: {exc}"

    out = []
    for body in list(got(s._doc(), "GetBodies2", 0, True) or []):  # noqa: SLF001
        for face in list(got(body, "GetFaces") or []):
            surface = got(face, "GetSurface")
            if not got(surface, "IsPlane"):
                continue
            p = [float(v) for v in got(surface, "PlaneParams")]
            z = p[5] * 1000.0
            if abs(abs(p[2]) - 1.0) > 1e-9 or not any(abs(z - w) <= BORE_TOL for w in zs):
                continue
            area, area_error = guarded(lambda: round(float(got(face, "GetArea")) * 1e6, 9))
            record = {"z": round(z, 9), "area": area, "area_error": area_error, "loops": []}
            loops, error = guarded(lambda: list(got(face, "GetLoops") or []), [])
            if error:
                record["loops_error"] = error
            shapes = []
            for loop in loops:
                outer, outer_error = guarded(lambda: bool(got(loop, "IsOuter")))
                edges, edges_error = guarded(lambda: list(got(loop, "GetEdges") or []), [])
                lp = {"outer": outer, "outer_error": outer_error, "edges_error": edges_error, "edges": []}
                points = []
                for edge in edges:
                    e = {}
                    curve, e["curve_error"] = guarded(lambda: got(edge, "GetCurve"))
                    params, e["params_error"] = guarded(lambda: [float(v) for v in got(edge, "GetCurveParams2")])
                    if curve is None or params is None:
                        lp["edges"].append(e)
                        continue
                    e["kind"], _ = guarded(lambda: int(got(curve, "Identity")))
                    circle, _ = guarded(lambda: bool(got(curve, "IsCircle")))
                    if circle:
                        e["radius"], _ = guarded(lambda: round(float(list(got(curve, "CircleParams"))[6]) * 1000.0, 9))
                    e["ends"] = [[round(v * 1000.0, 9) for v in params[0:3]], [round(v * 1000.0, 9) for v in params[3:6]]]

                    def tess():
                        start = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, params[0:3])
                        end = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, params[3:6])
                        flat = [float(v) for v in got(curve, "GetTessPts", chord, length, start, end)]
                        return [(flat[i] * 1000.0, flat[i + 1] * 1000.0, flat[i + 2] * 1000.0)
                                for i in range(0, len(flat) - 2, 3)]

                    def evaluated():
                        t0, t1 = params[6], params[7]
                        return [tuple(float(v) * 1000.0 for v in list(got(curve, "Evaluate2", t0 + (t1 - t0) * i
                                                                           / (samples - 1), 0))[0:3])
                                for i in range(samples)]
                    pts, e["tess_error"] = guarded(tess)
                    e["points_by"] = "GetTessPts"
                    if not pts or len(pts) < 2:
                        pts, e["evaluate_error"] = guarded(evaluated)
                        e["points_by"] = "Evaluate2"
                    if pts:
                        e["points"] = len(pts)
                        e["off_plane"] = round(max(abs(q[2] - z) for q in pts), 9)
                        points.append([(q[0], q[1]) for q in pts])
                    lp["edges"].append(e)
                lp["edge_count"] = len(edges)
                record["loops"].append(lp)
                shapes.append({"outer": outer, "edges": points})
            integrated, each, gap_ = face_area_from_loops(shapes) if shapes else (None, [], None)
            record.update(integrated=None if integrated is None else round(integrated, 9),
                          loop_areas=[round(a, 9) for a in each], largest_gap=gap_)
            out.append(record)
    return out


def step_summary(record):
    """One step face's loops as the log says them: per loop, outer or not, its edge count, its curve kinds counted,
    the circles' radii, how its points were read and anything that did not read."""
    loops = []
    for lp in record["loops"]:
        kinds, radii, by, errors = {}, set(), set(), set()
        for e in lp["edges"]:
            kinds[e.get("kind")] = kinds.get(e.get("kind"), 0) + 1
            if e.get("radius") is not None:
                radii.add(e["radius"])
            by.add(e.get("points_by"))
            errors.update(v for k, v in e.items() if k.endswith("_error") and v)
        loops.append({"outer": lp["outer"], "edges": lp.get("edge_count"), "kinds": kinds, "radii": sorted(radii),
                      "points_by": sorted(str(b) for b in by), "errors": sorted(errors) or None})
    return loops


def step_report(out, records, want):
    """The step faces settled by one more read (W9B-REVIEW, addendum: 2.2e-3 under F0 − π(Ro² − r²) on both
    versions): per step plane, every planar face lying in it, its count, each area and the sum; the cap one face or
    several; the sum against the geometry; each face's area integrated from its loops' edges against GetArea and
    against the geometry. Facts, unless the summed or the integrated area lands on the geometry's figure to STEP_TOL:
    then that is the check, and GetArea's reading stays a fact."""
    if not isinstance(records, list):
        say(f"fact    part: the step faces' loops were not read: {records}")
        return
    out["step_faces"] = records
    planes = {}
    for r in records:
        planes.setdefault(r["z"], []).append(r)
    landed = []
    for z, faces in sorted(planes.items()):
        areas = [f["area"] for f in faces]
        total = sum(areas) if None not in areas else None
        off = "" if total is None else f" ({(total - want) / want:+.1e})"
        say(f"fact    part: step plane z {z}: {len(faces)} planar face(s) lie in it (PlaneParams), the cap is "
            f"{'one face' if len(faces) == 1 else 'several faces'}; GetArea {areas}, summed {total} against F0 − "
            f"π(Ro² − r²) = {want:.6f} mm²{off}")
        if total is not None and len(faces) > 1 and abs(total - want) <= STEP_TOL * want:
            landed.append(f"z {z}: {len(faces)} faces summed {total:.6f}")
        integrated = [f.get("integrated") for f in faces]
        for f in faces:
            i, a = f.get("integrated"), f.get("area")
            by_area = "" if i is None or a is None else f" against GetArea {a} ({(a - i) / i:+.1e})"
            by_geometry = "" if i is None else f", against the geometry {(i - want) / want:+.1e}"
            say(f"fact    part: step face at z {f['z']}: loops {step_summary(f)}; largest gap where edges meet "
                f"{f.get('largest_gap')} mm; loop areas {f.get('loop_areas')}; integrated from its edges {i} mm²"
                f"{by_area}{by_geometry}")
        if None not in integrated and integrated:
            whole = sum(integrated)
            if abs(whole - want) <= STEP_TOL * want:
                landed.append(f"z {z}: integrated from the edges {whole:.6f}")
    if landed:
        check(True, f"part: the step faces land on F0 − π(Ro² − r²) = {want:.6f} mm² to {STEP_TOL:g} by {landed} "
                    "(GetArea's own reading kept as a fact above)")
    else:
        say(f"fact    part: neither the summed nor the integrated step area lands on F0 − π(Ro² − r²) to {STEP_TOL:g}; "
            "both said above, not judged")


def part_read(label, path, relief, steps=()):
    """The part read back: its globals, its equations' text, every feature's error code, its volume, its faces; with
    the relief, the dimensions on its planes and sketches (mm)."""
    def work(s):
        out = {"globals": s.equation_values(), "equations": [t for t, _ in s.equations()],
               "features": [(f.name, f.code) for f in s.feature_states()], "volume": s.volume_mm3(),
               "faces": part_faces(s)}
        if relief:
            out["dims"] = {name: [(n, round(v * 1000.0, 9)) for n, v in s.feature_dimensions(name)]
                           for name in (clutch.RELIEF_START_PLANE, clutch.RELIEF_END_PLANE, clutch.RELIEF_START_SKETCH,
                                        clutch.RELIEF_END_SKETCH)}
            try:        # the sketches the loft cut absorbed sit under it in the tree (IFeature.GetFirstSubFeature)
                subs, sub = [], call(s._by_name(clutch.RELIEF), "GetFirstSubFeature")  # noqa: SLF001
                while sub is not None and len(subs) < 50:
                    subs.append(str(call(sub, "Name")))
                    sub = call(sub, "GetNextSubFeature")
                out["relief_subfeatures"] = subs
            except Exception as exc:  # noqa: BLE001 - said as a fact, not judged
                out["relief_subfeatures"] = f"unread: {type(exc).__name__}: {exc}"
        if steps:
            try:
                out["steps"] = step_faces(s, steps)
            except Exception as exc:  # noqa: BLE001 - the step faces' read is a fact; it never fails the part
                out["steps"] = f"unread: {type(exc).__name__}: {exc}"
        return out
    got = run(f"{label}: read", job(path, work), 300)
    bad = [(n, c) for n, c in got["features"] if c]
    say(f"fact    {label}: volume {got['volume']:.6f} mm³; features {len(got['features'])}, in error {bad or 'none'}; "
        f"globals { {k: v for k, v in got['globals'].items() if k in SLEEVE_GLOBALS} }")
    return got


def linked(equations, dimension, expression):
    """Whether the part holds the equation ``"dimension" = expression`` (spaces aside)."""
    want = f'"{dimension}"={expression}'.replace(" ", "")
    return any(t.replace(" ", "") == want for t in equations)


def build_part(label, folder, spec):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, spec.stem() + ".SLDPRT")
    kind = kind_for(spec)
    derived = kind.derive(spec)
    plan = plan_for(spec, derived, "", path)
    check(plan.check() == [], f"{label}: the strip's plan checks clean: {plan.check()}")
    result = run(f"{label}: built", lambda s: swbuild.build(s, plan), 900)
    check(result.ok and bool(result.saved), f"{label}: {os.path.basename(path)} built and saved by swbuild.build: ok "
                                            f"{result.ok}, failures {list(result.failures)}")
    if not result.ok:
        A.stop(f"{label}: the part failed to build (ISSUE-1-PLAN §5 W9b: the relief op failing is a STOP): "
               f"{list(result.failures)}")
    return path, kind, derived


def close_folder(label, folder):
    left = run(f"{label}: closed", W.quit_in(folder))
    check(not left, f"{label}: closed, nothing left open under its folder: {left}")


def section_part(out):
    """The section, and whatever it left open under its folder closed if it failed: the first W9b run stopped in the
    unbanded sleeve's read with the part still open, and its file name then refused the two builds after it."""
    try:
        _section_part(out)
    except BaseException:
        try:
            left = run("part: closed after a failure", W.quit_in(os.path.join(W.OUT, "part")))
            say(f"fact    part: after its failure, closed what it had open; left open under its folder: {left}")
        except Exception as e:  # noqa: BLE001
            say(f"fact    part: after its failure, closing what it had open failed too: {type(e).__name__}: {e}")
        raise


def _section_part(out):
    say("== part  the banded RangeSlv of RangeBox_Fixed and the same sleeve unbanded, by the strip's own plan_for and "
        "swbuild.build, read back from SolidWorks; the volumes; a band changed by the strip's value route; the Hub "
        "part")
    fixed = W.w8_fixtures().range_box_fixed()
    banded = fixed.gear("RangeSlv").gear_spec(fixed.box)
    plain = dataclasses.replace(banded, start_band="", end_band="")
    hub = fixed.gear("Hub").gear_spec(fixed.box)
    root = W.fresh_folder("part")

    # The unbanded sleeve first: same file name as the banded one, so each is closed before the next is built.
    folder = os.path.join(root, "unbanded")
    path, _, _ = build_part("part unbanded", folder, plain)
    got = out["unbanded"] = part_read("part unbanded", path, False)
    check(not any(c for _, c in got["features"]) and not any(n.startswith("Relief") for n, _ in got["features"]),
          f"part unbanded: no feature in error and no relief feature: {[n for n, _ in got['features']]}")
    v0 = got["volume"]
    out["end_areas"] = end_areas(got["faces"], plain.face_width_mm())
    out["end_face_area"] = out["end_areas"].get(0.0)
    close_folder("part unbanded", folder)

    folder = os.path.join(root, "banded")
    path, kind, derived = build_part("part banded", folder, banded)
    say(f"NEW     the step faces' loops and edges read and their area integrated: {STEP_CALLS}")
    got = out["banded"] = part_read("part banded", path, True, steps=(EZ * PLANES[0], EZ * PLANES[1]))
    banded_steps = got.get("steps")
    g, eq, dims = got["globals"], got["equations"], got["dims"]
    check(abs(g.get(clutch.START_BAND, -1) - 5) < 1e-9 and abs(g.get(clutch.END_BAND, -1) - 5) < 1e-9
          and abs(g.get(clutch.RELIEF_DIAMETER, -1) - RELIEF_D) < 1e-9,
          f"part banded: the three globals read Start Band 5, End Band 5, Relief Diameter {RELIEF_D}: "
          f"{ {k: g.get(k) for k in SLEEVE_GLOBALS} }")
    offsets = [[v for _, v in dims[n]] for n in (clutch.RELIEF_START_PLANE, clutch.RELIEF_END_PLANE)]
    check(all(any(abs(v - want) < 1e-6 for v in vs) for vs, want in zip(offsets, PLANES)),
          f"part banded: {clutch.RELIEF_START_PLANE} and {clutch.RELIEF_END_PLANE} offset {PLANES}: {offsets}")
    links = {f"Offset@{clutch.RELIEF_START_PLANE}": f'"{clutch.START_BAND}"',
             f"Offset@{clutch.RELIEF_END_PLANE}": f'"Face Width" - "{clutch.END_BAND}"',
             f"Relief@{clutch.RELIEF_START_SKETCH}": f'"{clutch.RELIEF_DIAMETER}"',
             f"Relief@{clutch.RELIEF_END_SKETCH}": f'"{clutch.RELIEF_DIAMETER}"'}
    unlinked = [d for d, e in links.items() if not linked(eq, d, e)]
    check(not unlinked, f"part banded: each plane's offset and each relief sketch's diameter linked to its globals: "
                        f"not linked {unlinked or 'none'} (equations {[t for t in eq if 'Relief' in t]})")
    sketch = [[v for _, v in dims[n]] for n in (clutch.RELIEF_START_SKETCH, clutch.RELIEF_END_SKETCH)]
    check(all(any(abs(v - RELIEF_D) < 1e-6 for v in vs) for vs in sketch),
          f"part banded: each relief sketch's circle is Ø {RELIEF_D}: {sketch}")
    features = dict(got["features"])
    check(clutch.RELIEF in features and features[clutch.RELIEF] == 0 and not any(features.values()),
          f"part banded: the {clutch.RELIEF} feature present by name and in no error, nothing in error: "
          f"{ {n: c for n, c in features.items() if c or 'Relief' in n} }")
    face, held = relief_bore(got["faces"], min(EZ * PLANES[0], EZ * PLANES[1]), max(EZ * PLANES[0], EZ * PLANES[1]),
                             RELIEF_D / 2)
    out["relief_face"] = face
    check(held, f"part banded: the bore over the relief is one cylinder of radius {RELIEF_D / 2} along the part's axis, "
                f"its ends the two step faces at z {PLANES} to {BORE_TOL:g} mm (PlaneParams): {face}")
    if face.get("padding"):
        say(f"fact    part banded: SolidWorks padded the bore's GetBox by {face['padding']} mm at its two ends (box z "
            f"{face['box_z']}, the planes {face['ends']})")
    subs = got.get("relief_subfeatures")
    if isinstance(subs, list):
        check(clutch.RELIEF_START_SKETCH in subs and clutch.RELIEF_END_SKETCH in subs,
              f"part banded: the two relief sketches sit under {clutch.RELIEF} in the tree, absorbed by the loft cut: "
              f"{subs}")
    else:
        say(f"fact    part banded: {clutch.RELIEF}'s sub-features not read: {subs}")
    outer = outer_radius(got["faces"], derived.face_width)
    banded_ends = end_areas(got["faces"], derived.face_width)
    v1 = got["volume"]

    say(f"-- part  a band changed through the strip's value route: Start Band 5 -> {BAND_EDIT} "
        "(swbuild.update_variables, the part active), read back as the start plane's offset")
    edited = dataclasses.replace(banded, start_band=str(BAND_EDIT))
    variables = kind.variables(edited, kind.derive(edited))

    def change(s):
        s.open_document(path)
        return swbuild.update_variables(s, variables, path)
    done = run("part banded: Start Band changed", change, 300)
    check(done.changed == [clutch.START_BAND] and done.rebuilt and not done.failures,
          f"part banded: the value route set {clutch.START_BAND} alone and rebuilt: changed {done.changed}, rebuilt "
          f"{done.rebuilt}, failures {done.failures}")
    got = out["band_changed"] = part_read("part banded, Start Band 4", path, True)
    offsets = [[v for _, v in got["dims"][n]] for n in (clutch.RELIEF_START_PLANE, clutch.RELIEF_END_PLANE)]
    check(abs(got["globals"].get(clutch.START_BAND, -1) - BAND_EDIT) < 1e-9
          and any(abs(v - BAND_EDIT) < 1e-6 for v in offsets[0]) and any(abs(v - PLANES[1]) < 1e-6 for v in offsets[1])
          and not any(c for _, c in got["features"]),
          f"part banded: Start Band reads {BAND_EDIT}, the planes {offsets}, rebuilt in no error")
    v2 = got["volume"]
    close_folder("part banded", folder)

    area = v1 - v2
    low, high = section_area_bounds(derived, RELIEF_D)
    bore = face["r"][0] if face.get("r") else None
    length = derived.face_width
    f0, how = section_of(v0, length, out.get("end_areas") or {})
    out["volumes"] = {"unbanded": v0, "banded": v1, "banded_start_4": v2, "area_per_mm_measured": area,
                      "bounds_per_mm": [low, high], "outer_radius": outer, "bore_radius": bore, "section": f0,
                      "section_from": how, "end_areas": out.get("end_areas"), "banded_end_areas": banded_ends}
    say(f"fact    part: volumes unbanded {v0:.6f}, banded {v1:.6f}, Start Band {BAND_EDIT} {v2:.6f} mm³; one more mm of "
        f"relief removed {area:.6f} mm³ (a difference of two mass-property volumes, a fact only)")
    say(f"fact    part: the section F0 {f0:.6f} mm² from {how}; the end faces read {out.get('end_areas')} unbanded and "
        f"{banded_ends} banded; V/{length:g} reads {v0 / length:.6f} ({(v0 / length - f0) / f0:+.1e} of F0)")
    if not how.startswith("the front end face"):
        say("fact    part: GetArea gave no end face's area, so F0 is the volume's, which carries SolidWorks' volume "
            "error into every expected volume below")
    check(low < area < high, f"part: the area one more mm of relief removes, {area:.6f} mm², lies between the ring "
                             f"outside the roots ({low:.3f}) and the ring outside the tips ({high:.3f})")
    if outer is None or bore is None:
        check(False, f"part: the outer radius ({outer}) and the bore's ({bore}) were not both read from the faces, so "
                     "the volumes cannot be judged")
    else:
        g = volume_guard((("5/5", v1, (5.0, 5.0)), (f"{BAND_EDIT}/5", v2, (float(BAND_EDIT), 5.0))), v0, length, f0,
                         how.startswith("the front end face"), outer, bore)
        out["volumes"]["guard"] = {k: v for k, v in g.items() if k != "rows"}
        for label, r in g["rows"].items():
            out["volumes"][f"expected_{label}"] = r["want"]
            out["volumes"][f"residual_{label}"] = r["residual"]
        for is_check, holds, text in volume_guard_lines(g, length, f0, how):
            if is_check:
                check(holds, f"part: {text}")
            else:
                say(f"fact    part: {text}")
        steps, want = face.get("step_areas") or [], step_area(f0, outer, bore)
        out["volumes"]["step_areas"], out["volumes"]["step_expected"] = steps, want
        check(len(steps) == 2 and None not in steps and abs(steps[0] - steps[1]) <= AREA_TOL * want,
              f"part: the relief's two step faces read one area to {AREA_TOL:g} (one section at each end of it): {steps}")
        step_report(out, banded_steps, want)

    folder = os.path.join(root, "hub")
    path, _, _ = build_part("part hub", folder, hub)
    got = out["hub"] = part_read("part hub", path, False)
    check(not any(c for _, c in got["features"]) and abs(got["globals"].get("Face Width", -1) - 20) < 1e-9
          and abs(got["globals"].get("No. of Teeth", -1) - 17) < 1e-9,
          f"part hub: Hub_m1.25_N17 built, 17 teeth, face 20, no feature in error")
    close_folder("part hub", folder)
    RESULT["proposal"]["M7_part"] = {"relief_feature": True, "volumes": out["volumes"], "relief_face": face}


# -- build: RangeBox_Fixed from scratch, and the per-mode read ---------------------------------------------------------


def part_globals(desk, gears):
    """Each named gear's part globals as SolidWorks holds them."""
    box = desk.record.gearbox
    paths = {c.gear: c.part for c in box.components if c.gear in gears}
    return run("the parts' globals", lambda s: {g: W.live_globals(s, p) for g, p in paths.items()}, 600)


def mode_read(label, desk):
    """Every mode shown and rebuilt in turn: each body's frame and status, every mate's code, the interferences; then
    the first mode shown, every mate's flag per mode and each slide's value per mode."""
    box = desk.record.gearbox
    modes = list(box.modes)
    pairs = W.bodies(box)
    names = [m.name for m in box.mates]
    slides = [m.name for m in box.mates if m.kind == "slide"]

    def work(s):
        out = {"frames": {}, "status": {}, "mates": {}, "interferences": {}, "flags": {}, "values": {}}
        for mode in modes:
            s.show_configuration(mode)
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            frames, status = {}, {}
            for i, (g, n) in enumerate(pairs):
                s.find_component(f"b{i}", n)
                frames[g], status[g] = s.component_frame(f"b{i}"), s.constrained_status(f"b{i}")
            out["frames"][mode], out["status"][mode] = frames, status
            out["mates"][mode] = {m.name: (m.code, m.suppressed) for m in s.mate_states()}
            out["interferences"][mode] = [(list(n), v) for n, v in s.interferences()]
        s.show_configuration(modes[0])
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        for i, name in enumerate(names):
            s.find_mate(f"f{i}", name)
            out["flags"][name] = s.mate_suppression(f"f{i}", modes)
        for i, name in enumerate(slides):
            s.find_mate(f"v{i}", name)
            out["values"][name] = s.dimension_values(f"v{i}", modes)
        return out
    return run(f"every mode {label}", job(box.assembly, work), 1800)


def span(frame, a, b):
    """A part-local length [a, b] along its face (the part's z, EXTRUDE_Z_SIGN) carried into global z by its frame."""
    rotation, origin = frame
    zs = (origin[2] + rotation[8] * EZ * a, origin[2] + rotation[8] * EZ * b)
    return (min(zs), max(zs))


def measured(frames, globals_, banded=True):
    """From a mode's frames and the parts' own globals: RangeSlv's bands (or its whole face), the dogs, the hub."""
    sg = globals_["RangeSlv"]
    face = sg["Face Width"]
    if banded:
        b1, b2 = sg[clutch.START_BAND], sg[clutch.END_BAND]
        bands = {"start": span(frames["RangeSlv"], 0, b1), "end": span(frames["RangeSlv"], face - b2, face)}
    else:
        bands = {"whole": span(frames["RangeSlv"], 0, face)}
    dogs = {d: span(frames[d], 0, globals_[d]["Face Width"]) for d in DOGS}
    hub = span(frames["Hub"], 0, globals_["Hub"]["Face Width"]) if "Hub" in frames and "Hub" in globals_ else None
    return bands, dogs, hub


def judge_every(label, desk, every, globals_, banded=True, against_section3=True, out=None, users=()):
    """Per mode, the read against the app's record and its own read of the workbook, and (``against_section3``) §3's
    table: the frames on record, the flags, the slide's value, the gears free, no mate in error, no interference
    between two of the app's bodies, the bands and dogs where the app says, what is engaged and the least running
    gaps. ``users``: the user's components (their Name2s): an interference with one of them is not judged here (W9c's
    demonstration holds it to what the app's result named); every interference is still kept in ``out``. A record
    without the mode N (a W9c Modes row removed) has no N to measure the slide from, so ``moved`` is not said."""
    box = desk.record.gearbox
    a = desk.a
    reports = {m.name: m for m in a.report.modes}
    fixed = set(box.fixed)
    ids = dict(W.bodies(box))
    slide = next(m for m in box.mates if m.kind == "slide")
    recorded = dict(slide.values)
    n_origin = every["frames"]["N"]["RangeSlv"][1][2] if "N" in every["frames"] else None
    clean = True
    for mode in box.modes:
        frames = every["frames"][mode]
        gap_, at = W.frames_gap(frames, W.mode_record_frames(desk, mode))
        errors = {n: c for n, (c, sup) in every["mates"][mode].items() if c and not sup}
        free = {g: v for g, v in every["status"][mode].items()
                if g in ids and g not in fixed and v != findings.COMPONENT_UNDER_DEFINED}
        clashes = [c for c in every["interferences"][mode] if not set(c[0]) & set(users)]
        value = every["values"][slide.name][mode]
        moved = frames["RangeSlv"][1][2] - n_origin if n_origin is not None else float("nan")
        bands, dogs, hub = measured(frames, globals_, banded)
        app_bands, app_dogs, app_hub = app_spans(a, mode)
        off = [f"{k} {v} not {app_bands.get(k)}" for k, v in bands.items()
               if k not in app_bands or any(abs(x - y) > SPAN_TOL for x, y in zip(v, app_bands[k]))]
        off += [f"{d} {v} not {app_dogs[d]}" for d, v in dogs.items() if any(abs(x - y) > SPAN_TOL
                                                                            for x, y in zip(v, app_dogs[d]))]
        if hub is not None and app_hub is not None and any(abs(x - y) > SPAN_TOL for x, y in zip(hub, app_hub)):
            off.append(f"Hub {hub} not {app_hub}")
        judged = judge_mode(bands, dogs)
        engaged = [g for _, g in reports[mode].engaged]
        origin = frames["RangeSlv"][1][2]
        slid = slide_agrees(value, recorded[mode], origin)
        if out is not None:
            out.setdefault("modes", {})[mode] = {
                "slide_read": value, "slide_recorded": recorded[mode], "origin_z": origin, "frame_gap": gap_,
                "bands": bands, "dogs": dogs, "hub": hub, "interferences": clashes, "errors": errors,
                "not_free": free, "engaged": judged["engaged"], "least": judged["least"]}
        ok = (gap_ <= TOL and not errors and not free and not clashes and not off and judged["engaged"] == engaged
              and slid)
        check(ok, f"{label}, {mode} shown: every body at its frame on record ({gap_:.1e} at {at or '-'}); no mate in "
                  f"error {errors or ''}; every app gear free {not free} {free or ''}; no interference {clashes or ''}; "
                  f"{slide.name} reads {value:.6f} mm, the record {recorded[mode]:.6f} (SolidWorks gives a distance "
                  f"without its sign), RangeSlv's Front plane at z {origin:.6f}: {'agree' if slid else 'DISAGREE'}; bands "
                  f"and dogs where the app's read puts them to {SPAN_TOL:g} mm {off or ''}; engaged {judged['engaged']} "
                  f"as the app's {engaged}")
        say(f"fact    {label}, {mode}: measured bands {bands}, dogs {dogs}, hub {hub}; RangeSlv moved {moved:+.6f} mm "
            f"from N; least running gap {judged['least']} at {judged['least_at']}; relief holds {judged['relief_holds']}")
        clean = clean and ok
        if against_section3:
            differ = section3_of(judged, bands, mode)
            ratio = reports[mode].ratio
            ratio_ok = (reports[mode].ratio_why == "neutral" if SECTION3[mode]["ratio"] is None
                        else ratio is not None and round(ratio, 6) == SECTION3[mode]["ratio"])
            check(not differ and abs(moved - SECTION3[mode]["slide"]) <= SPAN_TOL and ratio_ok,
                  f"{label}, {mode}: §3's table: slide {SECTION3[mode]['slide']:+} (moved {moved:+.6f}), bands, relief, "
                  f"engaged {SECTION3[mode]['engaged']}, least gap {SECTION3[mode]['least']} at "
                  f"{SECTION3[mode]['least_at']}, ratio {SECTION3[mode]['ratio'] or 'neutral'} ({ratio}, "
                  f"{reports[mode].ratio_why!r}): differs {differ or 'nothing'}")
            if hub is not None:
                check(all(abs(x - y) <= SPAN_TOL for x, y in zip(hub, HUB))
                      and abs(gap(hub, dogs["HighDog"]) - HUB_TO_HIGHDOG) <= SPAN_TOL,
                      f"{label}, {mode}: Hub {hub} (§3 {HUB}), {gap(hub, dogs['HighDog']):.6f} mm from HighDog (§3 "
                      f"{HUB_TO_HIGHDOG})")
    wrong = {m.name: (every["flags"].get(m.name), list(m.modes or [])) for m in box.mates
             if every["flags"].get(m.name) != {c: bool(m.modes) and not swbuild.on_in(tuple(m.modes), c)
                                               for c in box.modes}}
    check(not wrong, f"{label}: every mate's flag in every mode as on record, the couplings on only in their modes: "
                     f"wrong {wrong or 'none'}")
    return clean and not wrong


def hub_mates(label, desk, plan):
    """Hub as Output's anchor, RangeSlv splined to it: the built plan's anchors and the record's mates."""
    names = {m.name: m.kind for m in desk.record.gearbox.mates}
    want = {"Hub on Output Axis": "axis", "Hub along Output": "along", "RangeSlv splined to Hub": "spline",
            "RangeSlv along Output": "slide", "RangeSlv engages HighDog": "couple", "RangeSlv engages LowDog": "couple"}
    anchor = plan.motion.anchors.get("Output") if plan is not None and plan.motion is not None else None
    check(anchor == "Hub" and all(names.get(n) == k for n, k in want.items()),
          f"{label}: Hub is Output's anchor ({anchor}) and the record holds {sorted(want)}: "
          f"{ {n: names.get(n) for n in want} }")


def read_checks(label, desk, expected):
    a = desk.a
    got = warnings_of(a)
    check(got == expected and not errors_of(a) and a.lay_out_refusal() == "",
          f"{label}: the read's warnings are the fixture's own ({len(expected)}), no error: extra "
          f"{sorted(set(got) - set(expected))}, missing {sorted(set(expected) - set(got))}, errors {errors_of(a)}")
    w9b = w9b_check_warnings(a)
    check(not w9b and not any("would hold both at once" in m for m in got),
          f"{label}: none from W9b's three checks (reach, hub, running clearance) and no stroke warning: {w9b}")


def expected_fixed_warnings():
    """``assess`` of the fixture itself, in this process: the warnings the plan says RangeBox_Fixed keeps."""
    from gear_generator.workbook import assess
    a = assess.assess(dataclasses.replace(spec_fixed(""), source_path="C:\\B\\X.xlsx"), [], "C:\\Out\\")
    return warnings_of(a)


def section_build(out):
    say("== build  RangeBox_Fixed written by the app's write_new and built from scratch by the app's own Build, kept as "
        "fixed.master; per mode, §3's engagement, slides, interference and bands measured from the model (M7)")
    folder, path, book, desk = A.w8_step(W.write_fixture, CTX["worker"], CTX["excel"], "fixed", spec_fixed)
    kept = ""
    try:
        read_checks("build", desk, expected_fixed_warnings())
        plan, result = A.w8_step(W.build_turning, CTX["worker"], desk, "build", None, None)
        check(result.ok and not result.clashes and not result.interference_error,
              f"build: the Build ended ok with no interference: ok {result.ok}, clashes {result.clashes}")
        say(f"fact    build: the build's per-mode checks {getattr(result, 'modes', None)}")
        after = warnings_of(desk.a)
        check(after == expected_fixed_warnings(), f"build: no warning after the build beyond the fixture's own: "
                                                  f"{sorted(set(after) - set(expected_fixed_warnings()))}")
        hub_mates("build", desk, plan)
        box = desk.record.gearbox
        sleeve = next(c.part for c in box.components if c.gear == "RangeSlv")
        sidecar = store.read_sidecar(store.sidecar_path(sleeve))
        check(sidecar is not None and sidecar.schema_version == 2 and clutch.RELIEF in sidecar.record.features,
              f"build: the sleeve's sidecar at schema 2 and its features holding {clutch.RELIEF}: "
              f"{sidecar.schema_version if sidecar else None}")
        globals_ = out["globals"] = part_globals(desk, ("RangeSlv", "HighDog", "LowDog", "Hub"))
        shown = {g: {k: v for k, v in gl.items() if k in SLEEVE_GLOBALS} for g, gl in globals_.items()}
        say(f"fact    build: the parts' globals {shown}")
        every = mode_read("build", desk)
        out["clean"] = judge_every("build", desk, every, globals_, out=out)
        RESULT["proposal"]["M7_build"] = {"clean": out["clean"], "interferences": every["interferences"]}
    finally:
        if not W.HUNG["on"]:
            kept = A.w8_step(W.keep_master, CTX["worker"], folder, "fixed")
            FIXED_MASTER["path"] = kept
            check(bool(kept), f"build: kept as fixed.master: {kept}")


def fixed_master():
    here = os.path.join(OUT, "fixed" + W.MASTER_SUFFIX)
    if FIXED_MASTER["path"]:
        return FIXED_MASTER["path"]
    if not os.path.isdir(here):
        if os.path.exists(os.path.join(OUT, "fixed")):
            raise AssertionError("build ran earlier in this <out> and kept no fixed.master")
        say("fresh   no fixed.master in this <out>: build runs first")
        section_build(RESULT["sections"].setdefault("build", {}))
    if not os.path.isdir(here):
        raise AssertionError("build kept no fixed.master")
    FIXED_MASTER["path"] = here
    return here


# -- update ------------------------------------------------------------------------------------------------------------


def documents_state(label, desk, folder):
    """The SolidWorks documents of the copy: GetSaveFlag of each open one, and each file's modification time."""
    flags = run(f"{label}: save flags", job(desk.record.gearbox.assembly, lambda s: W.folder_flags(s, folder)), 300)
    times = {n: os.path.getmtime(os.path.join(folder, n)) for n in os.listdir(folder)
             if n.lower().endswith((".sldprt", ".sldasm"))}
    return {"flags": flags, "times": times}


def nothing_written(label, before, after):
    changed = {n: (before["times"].get(n), t) for n, t in after["times"].items() if before["times"].get(n) != t}
    marked = {n: (before["flags"].get(n), f) for n, f in after["flags"].items() if before["flags"].get(n) != f}
    check(not changed and not marked, f"{label}: nothing written to SolidWorks: files changed {changed or 'none'}, "
                                      f"documents newly marked {marked or 'none'}")


def clear_row(book, sheet, key):
    """Every cell of ``sheet``'s row whose first column reads ``key`` emptied, as a person deletes the row's text."""
    first = W.cell(book, sheet, "Gear", key)
    row = int(re.sub(r"^[A-Z]+", "", first))
    ws = book.wb.Worksheets(sheet)
    count = next(c for c in range(1, 60) if not str(ws.Cells(1, c).Value or "").strip()) - 1
    return [(sheet, f"{W.column_letter(c)}{row}", None) for c in range(1, count + 1)]


def section_update(out):
    say(f"== update  a copy of fixed.master: Start band 5 -> {BAND_EDIT} as a value Update, read back in the part and per "
        "mode; then the bands taken off, alone (refused at the workbook) and as the smallest legal edit (Build again… "
        "in a sentence), neither writing anything to SolidWorks")
    folder, path, book, desk = A.copy_desk(fixed_master(), "update", "RangeBox_Fixed.xlsx")
    try:
        W.edit(desk, book, ("Gears", W.cell(book, "Gears", "Start band", "RangeSlv"), BAND_EDIT))
        u = desk.update
        changed = [p for p in (u.changed_parts if u is not None else [])]
        check(u is not None and not u.needs_new_revision and not u.structural
              and [os.path.basename(p.path) for p in changed] == ["Sleeve_m1.25_N17.SLDPRT"],
              f"update: classify makes Start band {BAND_EDIT} a value Update of the sleeve's part: structural "
              f"{u and list(u.structural)}, parts {[os.path.basename(p.path) for p in changed]}")
        read_checks("update", desk, warnings_of(desk.a))
        result, _ = A.press(desk, f"update Start band {BAND_EDIT}")
        out["update"] = A._update_fact(desk, result)
        check(result is not None and result.ok and not result.failures,
              f"update: the Update went ahead and ended ok: {desk.note[0] if desk.note else desk.error}")
        box = desk.record.gearbox
        globals_ = out["globals"] = part_globals(desk, ("RangeSlv", "HighDog", "LowDog", "Hub"))
        sleeve = next(c.part for c in box.components if c.gear == "RangeSlv")

        def planes(s):
            return {n: [round(v * 1000.0, 9) for _, v in s.feature_dimensions(n)]
                    for n in (clutch.RELIEF_START_PLANE, clutch.RELIEF_END_PLANE)}, \
                [(f.name, f.code) for f in s.feature_states() if f.code]
        offsets, bad = run("update: the sleeve's planes", job(sleeve, planes), 300)
        check(abs(globals_["RangeSlv"][clutch.START_BAND] - BAND_EDIT) < 1e-9
              and any(abs(v - BAND_EDIT) < 1e-6 for v in offsets[clutch.RELIEF_START_PLANE])
              and any(abs(v - PLANES[1]) < 1e-6 for v in offsets[clutch.RELIEF_END_PLANE]) and not bad,
              f"update: the part reads Start Band {BAND_EDIT}, its planes {offsets}, no feature in error {bad or ''}")
        every = mode_read("update", desk)
        out["clean"] = judge_every("update", desk, every, globals_, against_section3=False, out=out)
        for mode in box.modes:      # what the band change leaves as §3 has it: slides, the end band, engagement
            bands, dogs, _ = measured(every["frames"][mode], globals_)
            judged = judge_mode(bands, dogs)
            same = (all(abs(x - y) <= SPAN_TOL for x, y in zip(bands["end"], SECTION3[mode]["end"]))
                    and judged["engaged"] == SECTION3[mode]["engaged"])
            check(same, f"update, {mode}: the end band and what is engaged as §3 ({bands['end']}, {judged['engaged']}); "
                        f"the start band now {bands['start']}")

        say("-- update  the bands taken off alone: the read refuses it before anything (the 26 mm sleeve jams L)")
        before = documents_state("update", desk, folder)
        W.edit(desk, book, ("Gears", W.cell(book, "Gears", "Start band", "RangeSlv"), None),
               ("Gears", W.cell(book, "Gears", "End band", "RangeSlv"), None))
        f = desk.say_footer("update, the bands off alone")
        refusal = desk.a.lay_out_refusal()
        check(refusal.startswith("Fix the workbook") and "jammed" in refusal and not f.update_enabled
              and not f.build_enabled, f"update: the bands off alone are refused at the workbook, nothing offered: "
                                       f"{refusal[:200]!r}")
        nothing_written("update, the bands off alone", before, documents_state("update", desk, folder))

        say("-- update  the smallest legal edit that takes the bands off: RangeSlv as RangeBox has it, Hub's row "
            "cleared; Build again… in a sentence")
        cells = [("Gears", W.cell(book, "Gears", header, "RangeSlv"), value) for header, value in AS_RANGEBOX.items()]
        W.edit(desk, book, *cells, *clear_row(book, "Gears", "Hub"))
        u = desk.update
        sentence = "Bands cannot be given to or taken from a built sleeve"
        check(u is not None and u.needs_new_revision and any(sentence in s for s in u.structural),
              f"update: classify sends it to Build again…, the bands named: {u and list(u.structural)}")
        f = desk.say_footer("update, the bands off as RangeBox")
        question = ui_text.build_again_question(u, desk.plan, record=desk.record) if u is not None else ""
        say(f"question {question}")
        check(f.build_enabled and f.build_action == ui_text.BUILD_AGAIN and sentence in question,
              f"update: the footer offers Build again… ({f.build_label!r}) and its question says {sentence!r}")
        nothing_written("update, the bands off as RangeBox", before, documents_state("update", desk, folder))
    finally:
        A.w8_step(W.end_copy, CTX["worker"], folder, "update")


# -- old: RangeBox as it is ----------------------------------------------------------------------------------------------


def section_old(out):
    say("== old  RangeBox (no bands, no hub) built by today's app as before W9b: seven warnings (§3's four and W9b's "
        "three), §3's engagement and speeds, the unbanded sleeve as before; per mode as build, without bands. Not "
        "S0's rangebox.master: that was built by an app before W9b, which changed the anchor rule and engagement")
    folder, path, book, desk = A.w8_step(W.write_fixture, CTX["worker"], CTX["excel"], "old", spec_old)
    try:
        a = desk.a
        w9b = [bare(m) for m in w9b_check_warnings(a)]
        got = warnings_of(a)
        check(len(got) == 7 and not errors_of(a) and len(w9b) == 3 and all(m in got for m in w9b),
              f"old: seven warnings, W9b's three among them (reach, hub, the N clearance): {[m[:70] for m in w9b]}")
        missing = [m for m in PLAN_W9B_WARNINGS if m not in got]
        check(not missing, f"old: W9b's three warnings in the read are §2.2's and §2.3's sentences word for word: "
                           f"missing {missing or 'none'}")
        modes = {m.name: m for m in a.report.modes}
        speeds = {k: round(float(v), 3) for k, v in a.report.motion.speeds.items()}
        check([g for _, g in modes["H"].engaged] == ["HighDog"] and modes["N"].engaged == ()
              and [g for _, g in modes["L"].engaged] == ["LowDog"] and abs(modes["H"].ratio - 1.0) < 1e-9
              and round(modes["L"].ratio, 6) == 2.896552 and speeds.get("Carrier") == 517.857
              and speeds.get("Planet") == -1673.077,
              f"old: §3's engagement, ratios and speeds: {[(n, m.engaged, m.ratio) for n, m in modes.items()]}, {speeds}")
        plan, result = A.w8_step(W.build_turning, CTX["worker"], desk, "old", None, None)
        box = desk.record.gearbox
        anchor = plan.motion.anchors.get("Output") if plan is not None and plan.motion is not None else None
        sleeve = next(p for p in desk.record.parts if "RangeSlv" in p.gears)
        sidecar = store.read_sidecar(store.sidecar_path(sleeve.path))
        check(anchor == "RangeSlv" and "start_band" not in sleeve.spec and sidecar is not None
              and sidecar.schema_version == 1 and clutch.RELIEF not in sidecar.record.features,
              f"old: RangeSlv still Output's anchor ({anchor}); the sleeve unbanded as before W9b, its sidecar at schema "
              f"{sidecar.schema_version if sidecar else None}, no {clutch.RELIEF}")
        globals_ = part_globals(desk, ("RangeSlv", "HighDog", "LowDog"))
        every = mode_read("old", desk)
        out["clean"] = judge_every("old", desk, every, globals_, banded=False, against_section3=False, out=out)
    finally:
        if not W.HUNG["on"]:
            A.w8_step(W.keep_master, CTX["worker"], folder, "old")


# -- the run -------------------------------------------------------------------------------------------------------------

ORDER = ["part", "build", "update", "old"]
SECTIONS = {"part": section_part, "build": section_build, "update": section_update, "old": section_old}
FOLDERS = {"part": ["part"], "build": ["fixed", "fixed" + W.MASTER_SUFFIX], "update": ["update"],
           "old": ["old", "old" + W.MASTER_SUFFIX]}


def done_here(name):
    """What of a section this <out> holds already (W9a's ``done_here`` for these sections' folders)."""
    return [p for p in (os.path.join(OUT, f) for f in FOLDERS.get(name, [name])) if os.path.exists(p)]


def main():
    A.SECTIONS.clear()
    A.SECTIONS.update(SECTIONS)
    if A._given in ("", "all"):                    # noqa: SLF001
        A.CHOSEN = list(ORDER)
    A.done_here = done_here
    A.RUN_TITLE, A.JSON_STEM = "W9b demonstration", "w9b-demo"
    return A.main()


if __name__ == "__main__":
    code = 1
    try:
        code = main()
    finally:
        with open(W.LOG_PATH, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(W.LOG) + "\n")
    raise SystemExit(code)
