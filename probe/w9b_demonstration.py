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

**The volumes (M7).** The unbanded sleeve is one section along its face, F0 = V / 26; a band keeps it and the relief
leaves the ring π(Ro² − r²) between the bore and the outside, Ro and r read from the part's cylinders. So V(banded) =
F0 × (b1 + b2) + π(Ro² − r²) × (26 − b1 − b2), for 5/5 and for 4/5, to 1e-4 of the volume (the first 2026 run read
3.8e-5 and 3.5e-5). The area one more mm of relief removes (a difference of two volumes) is a fact, held to the hard
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
# relative, of the part's volume: SolidWorks' mass-property volume against the exact form below. The first 2026 run
# (w9b-demo-20261117-045137.json) read residuals of 3.8e-5 (5/5) and 3.5e-5 (4/5) of the volume; 1e-4 holds them with
# room and is far below what a wrong relief would move (one mm of it is 114.6 mm³, 1.2e-2 of the part).
VOLUME_TOL = 1e-4
BORE_TOL = 1e-6            # mm: the relief bore's radius and its ends against the planes
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
    ends = sorted(f["z"] for f in steps)
    out.update(ends=ends, box_z=(box[2], box[5]),
               padding=(round(ends[0] - box[2], 6), round(box[5] - ends[-1], 6)) if len(ends) == 2 else None)
    held = len(ends) == 2 and abs(ends[0] - z_lo) <= BORE_TOL and abs(ends[1] - z_hi) <= BORE_TOL
    return out, held


def outer_radius(faces, face):
    """The sleeve's outer cylinder: the largest cylinder whose box runs the whole face (its radius is exact; its box,
    padded or not, is only used to tell it from the short ones)."""
    whole = [f for f in faces if f["kind"] == "cylinder" and f["box"][2] <= 1e-3 and f["box"][5] >= face - 1e-3]
    return max(f["r"] for f in whole) if whole else None


def banded_volume(v_unbanded, face, bands, outer, bore):
    """What a banded sleeve's volume must be, exactly in form: the unbanded sleeve is one section along its whole face
    (Blank, Tooth Space, Teeth), F0 = V / face; each band keeps it, and over the relief the section is the ring between
    the bore and the outside, π(Ro² − r²)."""
    f0 = v_unbanded / face
    relief = face - bands[0] - bands[1]
    return f0 * (bands[0] + bands[1]) + math.pi * (outer * outer - bore * bore) * relief, f0


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
    for label, volume, bands in (("5/5", v1, (5.0, 5.0)), ("4/5", v2, (4.0, 5.0))):
        want, f0 = banded_volume(v0, 26.0, bands, outer, bore)
        ok(abs(volume - want) <= VOLUME_TOL * volume,
           f"replay volume {label}: {volume:.6f} against {want:.6f} (F0 {f0:.6f}, Ro {outer}), "
           f"{abs(volume - want) / volume:.1e} of it")
    wrong, _ = banded_volume(v0, 26.0, (5.0, 5.0), outer, bore + 0.25)
    ok(abs(v1 - wrong) > VOLUME_TOL * v1, f"replay volume: a relief 0.5 mm wider would fail by "
                                          f"{abs(v1 - wrong) / v1:.1e} of the volume ({VOLUME_TOL:g} allowed)")
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
    ok(len(warnings_of(o)) == 7 and len(w9b_check_warnings(o)) == 3,
       f"RangeBox: seven warnings, three of them W9b's: {[m[:60] for m in w9b_check_warnings(o)]}")
    speeds = {k: round(float(v), 3) for k, v in o.report.motion.speeds.items()}
    ok(speeds.get("Carrier") == 517.857 and speeds.get("Planet") == -1673.077, f"RangeBox's speeds: {speeds}")
    replay_first_run(ok)
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


def part_read(label, path, relief):
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
    ends = [f for f in got["faces"] if f["kind"] == "plane" and f.get("z") is not None and abs(f["z"]) <= 1e-6]
    out["end_face_area"] = max((f["area"] for f in ends if f["area"] is not None), default=None)
    close_folder("part unbanded", folder)

    folder = os.path.join(root, "banded")
    path, kind, derived = build_part("part banded", folder, banded)
    got = out["banded"] = part_read("part banded", path, True)
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
    out["volumes"] = {"unbanded": v0, "banded": v1, "banded_start_4": v2, "area_per_mm_measured": area,
                      "bounds_per_mm": [low, high], "outer_radius": outer, "bore_radius": bore,
                      "end_face_area": out.get("end_face_area")}
    say(f"fact    part: volumes unbanded {v0:.6f}, banded {v1:.6f}, Start Band {BAND_EDIT} {v2:.6f} mm³; one more mm of "
        f"relief removed {area:.6f} mm³ (a difference of two mass-property volumes, a fact only)")
    check(low < area < high, f"part: the area one more mm of relief removes, {area:.6f} mm², lies between the ring "
                             f"outside the roots ({low:.3f}) and the ring outside the tips ({high:.3f})")
    if outer is None or bore is None:
        check(False, f"part: the outer radius ({outer}) and the bore's ({bore}) were not both read from the faces, so "
                     "the volumes cannot be judged")
    else:
        for label, volume, bands in (("5/5", v1, (5.0, 5.0)), (f"{BAND_EDIT}/5", v2, (float(BAND_EDIT), 5.0))):
            want, f0 = banded_volume(v0, derived.face_width, bands, outer, bore)
            out["volumes"][f"expected_{label}"] = want
            check(abs(volume - want) <= VOLUME_TOL * volume,
                  f"part: the banded part's volume ({label}) is the unbanded section F0 = V/{derived.face_width:g} = "
                  f"{f0:.6f} mm² over the bands and the ring π(Ro² − r²), Ro {outer} and r {bore} from the faces, over "
                  f"the relief: {volume:.6f} against {want:.6f} mm³, {abs(volume - want):.6f} apart "
                  f"({abs(volume - want) / volume:.1e} of it; {VOLUME_TOL:g} allowed)")
        if out.get("end_face_area"):
            say(f"fact    part: F0 two ways: the unbanded volume over its face {v0 / derived.face_width:.6f} mm², its "
                f"front end face's area (IFace2.GetArea) {out['end_face_area']:.6f} mm² "
                f"({abs(v0 / derived.face_width - out['end_face_area']) / out['end_face_area']:.1e} apart)")

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


def judge_every(label, desk, every, globals_, banded=True, against_section3=True, out=None):
    """Per mode, the read against the app's record and its own read of the workbook, and (``against_section3``) §3's
    table: the frames on record, the flags, the slide's value, the gears free, no mate in error, no interference, the
    bands and dogs where the app says, what is engaged and the least running gaps."""
    box = desk.record.gearbox
    a = desk.a
    reports = {m.name: m for m in a.report.modes}
    fixed = set(box.fixed)
    ids = dict(W.bodies(box))
    slide = next(m for m in box.mates if m.kind == "slide")
    recorded = dict(slide.values)
    n_origin = every["frames"]["N"]["RangeSlv"][1][2]
    clean = True
    for mode in box.modes:
        frames = every["frames"][mode]
        gap_, at = W.frames_gap(frames, W.mode_record_frames(desk, mode))
        errors = {n: c for n, (c, sup) in every["mates"][mode].items() if c and not sup}
        free = {g: v for g, v in every["status"][mode].items()
                if g in ids and g not in fixed and v != findings.COMPONENT_UNDER_DEFINED}
        clashes = every["interferences"][mode]
        value = every["values"][slide.name][mode]
        moved = frames["RangeSlv"][1][2] - n_origin
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
