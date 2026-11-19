r"""F3's demonstration on SolidWorks (PLAN-PRINTED §4.6, *The SolidWorks demonstration* and *Done when*;
F3-INTERFACES.md; F3-PACKAGE-A, -B and -C): the bore allowance and the D-flat, through the app's own paths, each change
read back from what SolidWorks holds. The sections, what each line bears out, the masters, the command lines, the times
and what the script does not measure are in docs/notes-printed/F3-DEMONSTRATION.md.

python.exe probe/f3_demonstration.py <repo src> <output folder under C:\> --pid PID [--log FILE]
                                     [--sections dshape,allowance,print,built,hub,userwork|all]
                                     [--user-master <W9a's setup.master>]
                                     [--reducer-off-master <this script's f3-reducer-off.master>]
                                     [--reducer-on-master <this script's f3-reducer-on.master>]
                                     [--reducer-machined-master <this script's f3-reducer-machined.master>]
                                     [--redo] [--close-outlived-whats-wrong]
python probe/f3_demonstration.py --self-check     (no SolidWorks, no Excel: every judgement below on made-up readings
                                                   and on the app's own figures, each failing way shown; the strip's
                                                   form needs Tk)
python probe/f3_demonstration.py --help

The switch. A printed gear's blank Bore allowance plans spec.BORE_ALLOWANCE_DEFAULT only while
spur.PRINTED_DEFAULT_IN_PLANS is True (F3-INTERFACES §13; off as committed, turned on by the coordinator's last commit).
This script is written for the switch on. The log's head says what it reads, and every section says it again; the
sections that judge the default (allowance, print, built) refuse with a sentence when it is off. dshape and userwork
judge typed and as-built figures only and run either way. Where a section needs what F2's code built, it builds it in
this run with the switch turned off in this process only, says so, and turns it back.

Sections (each runs alone; built keeps its three reducers as masters for a rerun; userwork needs --user-master).
Every build's checks are held free of a sketch not fully defined:

- dshape     First (S6): the stand-in for a probe of a sketch that could solve to the far side, as W9c's landing
             section was for the ring. A printed spur (m 1.5, z 20, face 8, Bore 8, allowance 0.2 typed, Drive flat,
             Flat 7) built by the strip's form; then Flat, Bore and Bore allowance changed by the form's own Update
             values across their range, to each bound of §4.2 at its edge, past each (refused by the form in A's words,
             nothing written), back, and to a press fit; the allowance to 0 and the Drive to round each refused in B's
             words; then from D to round and back, each made new by the form's Build. After every change: no feature in
             error, the Bore Sketch fully defined, the volume within 0.1 % of the same gear built from scratch, the
             bore read face by face without trusting a face's padded box (every round face of radius (D + a)/2 about
             the axis, together reaching -X; one flat whose plane is at h on +X: the 278-degree D, never the sliver),
             the tip lands counted (where they sit, and the boxes' lengths, logged as facts), and the chord link read
             as SolidWorks holds it, equal to the app's text, evaluating to the app's figure, its Value agreeing.
- allowance  A printed spur, helical, herringbone and bevel gear and a hub, each built with the default allowance and with one typed
             (the spur's negative): the hole as cut read from the part's faces against Bore plus allowance, the
             global as SolidWorks holds it, the .gear.json at schema 4; a machined gear of the same sizes built beside
             each: no F3 global, schema 1, the hole its Bore, its record that of F3-0's pins.
- print      Print files on the strip's form for a printed D with a typed allowance and for a printed round bore at the
             default: each press judged whole by F2's judges; the bore read from the STEP file itself (one cylinder of
             the hole's radius, the D's one flat at h on +X, the least vertex radius (D + a)/2, the flat's corners at
             x = h); the print list's bore line.
- built      Nothing built before F3 moves: a printed coupon and the printed 12 : 1 built in this run with the switch
             off (F2's code), then read with it on: the strip's record counts nothing for Update values and a quiet
             Update values writes nothing; the window's footer as with the switch off and a quiet Update writes
             nothing; an allowance typed on one of them is refused as structural (G4), naming that part alone. Then the
             printed 12 : 1 built with the switch on: G2's allowance typed and one Update, G2's bore changed in place
             and nothing else touched or saved; G2's allowance changed by hand in SolidWorks, saved, and pressed again:
             the Update stops naming the global and its cell (K11). Then a machined 12 : 1 built before F3, Printed
             typed and one Update: each part's Backlash written, no "Bore Allowance" added.
- hub        RangeBox_Fixed (W9b's fixture with the hub) printed, its Hub row with a D bore and an allowance (its mate
             RangeSlv, a sleeve, takes none), built by the app's own Build, turned through every mode as W9b's build
             section turns it with no interference read, and the Hub's hole as cut read as dshape reads a D.
- userwork   A copy of W9a's setup.master (RangeBox with the user's work), Printed typed and one Update; Sun (built
             with no bore) given Bore, allowance, Drive flat and Flat, which only Build again... can do; the user's
             keyway cut again in the new Sun and a mate of the user's on its D bore face, recorded by a quiet press;
             Sun's allowance and Flat changed in place by one Update, the user's feature and mates read before and
             after; then Sun's allowance cleared and its part name changed, Build again...: the new Sun keeps its
             allowance as built (ruling 1) and the mate on its bore face is carried, as W9d's "bore" says of a D's
             partial cylinder.

Everything W9a's script does for a run is done by running its main with these sections, as W9b's, W9c's, W9d's, F1's
and F2's scripts do; F2's live part is imported for its form, its presses and its reads. --close-outlived-whats-wrong
(SolidWorks 2024 only) is W9c's own close path, put in when the flag is given. No document title but the run's own is
logged, no path but under the run folder, and never a STEP file's header.

SolidWorks calls: none new to the repo (the note lists each with the script that made it first).
"""

import dataclasses
import hashlib
import json
import math
import os
import re
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SELF_CHECK = "--self-check" in sys.argv

if "--help" in sys.argv or "-h" in sys.argv:
    print(__doc__)
    raise SystemExit(0)


def _f2_head():
    """F2's demonstration's pure part, everything above its 'if SELF_CHECK:' line: its STEP reader, its judges of a
    press, C's print sentences, the strip's form and the presses' Strand, reused here rather than restated. Executed
    into a module of its own, so nothing of F2's live part (W9a's harness and the argv it parses) runs from it; F2's file
    is not changed."""
    path = os.path.join(HERE, "f2_demonstration.py")
    with open(path, encoding="utf-8") as handle:
        src = handle.read()
    module = types.ModuleType("f2_demonstration_head")
    module.__file__ = path
    exec(compile(src[:src.index("\nif SELF_CHECK:")], path, "exec"), module.__dict__)  # noqa: S102 - the repo's file
    return module


F2P = _f2_head()

# -- what the plan and the interface say, pinned ----------------------------------------------------------------------

SWITCH = "PRINTED_DEFAULT_IN_PLANS"   # spur's switch (F3-INTERFACES §13), read from the module at call time
DEFAULT_ALLOWANCE = 0.2               # spec.BORE_ALLOWANCE_DEFAULT (G1), held to it in the self-check
LEAST_H, LEAST_DEPTH = 0.25, 0.3      # §4.2's bounds: h >= 0.25 R, D - F >= 0.3 mm (spur.FLAT_LEAST_H, FLAT_LEAST_DEPTH)
VOLUME_TOL = 1e-3                     # relative: the plan's 0.1 % (small_pinion_check's), a part against its twin
RADIUS_TOL = 1e-4                     # mm: a face's radius (W9d's "bore": W9D-INTERFACES §4.4)
FLAT_TOL = 1e-4                       # mm: the flat's plane from the axis, by PlaneParams
BOX_TOL = 0.1                         # mm: a face's box (GetBox pads, W9b), read only to tell a side or a length
ANGLE_TOL = 1.0                       # degrees: a tip land's box centre against the half pitch
EQ_TOL = 1e-6                         # mm: a link's expression evaluated here against the app's figure
STEP_TOL = 0.01                       # mm: the hole read from a STEP file (the plan's 0.01)
AXIS_TOL = 1e-6                       # a direction's component; a point's offset from the axis is 1e3 times it in mm
FULLY_DEFINED = 3                     # GetConstrainedStatus
SKETCH = "Bore Sketch"                # spur.BORE_SKETCH
BORE_DIM, FLAT_DIM = "Bore@" + SKETCH, "Flat@" + SKETCH
ALLOWANCE_GLOBAL, FLAT_GLOBAL, BORE_GLOBAL = "Bore Allowance", "Bore Flat", "Bore Diameter"
GLOBAL_OF = {"bore": BORE_GLOBAL, "bore_allowance": ALLOWANCE_GLOBAL, "flat": FLAT_GLOBAL}
MINUS, DOT = "\N{MINUS SIGN}", "\N{MIDDLE DOT}"
# §4.2's table (D, a, F) -> (h, R, chord, sweep), each to the places the plan gives.
PLAN_TABLE = (((8.0, 0.2, 7.0), (3.1, 4.1, 5.3666, 278.24)), ((8.0, 0.0, 7.0), (3.0, 4.0, 5.2915, 277.18)),
              ((8.0, 0.3, 7.0), (3.15, 4.15, 5.4037, 278.76)), ((8.0, 0.2, 7.2), (3.3, 4.1, 4.8662, 287.20)),
              ((5.0, 0.2, 4.5), (2.1, 2.6, 3.0659, 287.74)), ((3.0, 0.2, 2.5), (1.1, 1.6, 2.3238, 266.87)))

# dshape: the part and its changes, each through the strip's Update values. "value": a change the part's globals
# carry; "bound": past a bound of §4.2, refused by the form (A's sentence at Flat); "structural": refused by Update values
# in B's words. Each value step's state is the part's after it; a refused step leaves the part as it was.
DSHAPE = dict(module="1.5", teeth="20", face_width="8", bore="8", bore_allowance="0.2", drive="flat", flat="7")
DSHAPE_NAME, DSHAPE_ROUND, DSHAPE_AGAIN = "DShape", "DShape_Round", "DShape_D"
DSHAPE_STEPS = (
    ("Flat 7 to 5", {"flat": "5"}, "value"),
    ("Flat 5 to 7.6", {"flat": "7.6"}, "value"),
    ("Flat 7.6 to 7", {"flat": "7"}, "value"),
    ("Bore 8 to 10 with Flat 7 to 9", {"bore": "10", "flat": "9"}, "value"),
    ("allowance 0.2 to 0.4", {"bore_allowance": "0.4"}, "value"),
    ("Flat 9 to 6.1, h at 0.25 R exactly", {"flat": "6.1"}, "value"),
    ("Flat 6, past h >= 0.25 R", {"flat": "6"}, "bound"),
    ("Flat 6.1 to 9.7, the flat 0.3 deep exactly", {"flat": "9.7"}, "value"),
    ("Flat 9.8, past 0.3 deep", {"flat": "9.8"}, "bound"),
    ("back: Bore 10 to 8, Flat 9.7 to 7, allowance 0.4 to 0.2", {"bore": "8", "flat": "7", "bore_allowance": "0.2"},
     "value"),
    ("allowance 0.2 to -0.1, a press fit", {"bore_allowance": "-0.1"}, "value"),
    ("allowance -0.1 to 0", {"bore_allowance": "0"}, "structural"),
    ("Drive flat to round", {"bore_allowance": "-0.1", "drive": "round"}, "structural"),
)

# allowance: (name in F3-0's pins, the fields of tests/test_printed_rule.py's GEARS, the allowance typed). Each is built
# printed with the allowance blank (the default), printed with it typed, and machined with it blank.
ALLOWANCE_KINDS = (("spur", dict(), "-0.1"),
                   ("helical", dict(kind="helical", helix_angle="20"), "0.3"),
                   ("herringbone", dict(kind="herringbone", helix_angle="30", module="2", teeth="20"), "0.3"),
                   ("bevel", dict(kind="bevel", teeth="20", mate_teeth="40"), "0.3"),
                   ("hub", dict(kind="hub", module="1.25", teeth="17", face_width="20", bore="8"), "0.25"))

PRINT_D = dict(DSHAPE)
PRINT_ROUND = dict(module="1.5", teeth="20", face_width="8", bore="8")
COUPON = dict(module="1.5", teeth="20", face_width="8", bore="8")       # §3.2's coupon, as F2's code built it
REDUCER = F2P.REDUCER                     # the printed 12 : 1: gear -> (stem, module, teeth, face)
REDUCER_BOOK = F2P.REDUCER_BOOK
TYPED_G2, K11_LIVE = "0.3", "0.5"          # built: G2's allowance typed in the workbook, then set by hand in SolidWorks
SUN_D = dict(bore="8", bore_allowance="0.2", drive="flat", flat="7")     # userwork: what Sun is given
SUN_IN_PLACE = dict(bore_allowance="0.3", flat="7.2")                     # then changed in place
SUN_NEW_NAME = "SunGear"                  # W9a's again sections' Part name for Sun: a new file, so Build again...
BORE_MATE = "UserBoreMate"                # the user's concentric on Sun's bore face
SPROCKET_BORE_R = 5.0                     # S0's Sprocket: Bore 10
BORE_TITLES = ("Bore allowance (mm)", "Drive", "Flat (mm)")   # schema.GEARS' titles of the three columns (self-check)
HEADS = {"bore": "Bore", "bore_allowance": "Bore allowance", "drive": "Drive", "flat": "Flat",
         "part_name": "Part name"}         # a Gears column found by its title's start, as W8's cell finds it


# -- the maths, worked here -------------------------------------------------------------------------------------------


def fmt(value, places=3):
    """A figure as the app's sentences show it (equations.literal of a value rounded to three places)."""
    text = f"{round(float(value), places):.{places}f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def signed(a):
    """+ 0.2, or the minus sign C's words use and 0.1."""
    return f"{MINUS if a < 0 else '+'} {fmt(abs(a))}"


def d_expected(bore, allowance, flat):
    """§4.2 worked here: R = (D + a)/2, h = F - D/2 + a/2, the chord 2 sqrt(R^2 - h^2), the major arc's sweep
    360 - 2 acos(h/R) degrees, the flat's depth R - h, and the bounds' Flats: least (5D - 3a)/8, most D - 0.3."""
    D, a, F = float(bore), float(allowance), float(flat)
    R, h = (D + a) / 2.0, F - D / 2.0 + a / 2.0
    chord = 2.0 * math.sqrt(max(0.0, R * R - h * h))
    sweep = 360.0 - 2.0 * math.degrees(math.acos(max(-1.0, min(1.0, h / R))))
    return {"R": R, "h": h, "chord": chord, "sweep": sweep, "depth": R - h,
            "least": D / 2.0 - a / 2.0 + LEAST_H * (D + a) / 2.0, "most": D - LEAST_DEPTH}


def hole_of(fields):
    """(D, a, F or None) of a gear's fields: the allowance typed (blank 0 here), F only with Drive flat."""
    D = float(fields.get("bore") or 0)
    a = float(fields.get("bore_allowance") or 0)
    F = float(fields["flat"]) if str(fields.get("drive", "")).lower() == "flat" and fields.get("flat") else None
    return D, a, F


def dshape_states():
    """Each dshape step with the form's fields after it and the part's (unchanged by a refused step)."""
    form, part, out = dict(DSHAPE), dict(DSHAPE), []
    for tag, changes, how in DSHAPE_STEPS:
        form.update(changes)
        if how == "value":
            part = dict(form)
        out.append((tag, changes, how, dict(form), dict(part)))
    return out


# -- the words, written out here so a change to them is seen ----------------------------------------------------------

SAID_ALLOWANCE = ("A bore allowance cannot be added to or taken out of a built part through its values; build it again "
                  "as a new part.")
SAID_NOT_WORKED = "The gear on the form does not work out yet, so nothing was updated."


def said_drive(was, now):
    """B's structural sentence for a Drive changed on the strip."""
    return f"The drive changed from {was!r} to {now!r}; build it again as a new part."


def said_flat_h(bore, allowance, flat):
    """A's refusal at Flat for h under 0.25 R."""
    d = d_expected(bore, allowance, flat)
    return (f"The flat is {fmt(d['h'])} mm from the axis, under a quarter of the hole's radius "
            f"({fmt(LEAST_H * d['R'])} mm); type a Flat of at least {fmt(d['least'])} mm, or use a round bore.")


def said_flat_depth(bore, flat):
    """A's refusal at Flat for a shaft's flat under 0.3 mm deep."""
    D, F = float(bore), float(flat)
    return (f"Your shaft's flat is {fmt(D - F)} mm deep (Bore {fmt(D)} less Flat {fmt(F)}), under the "
            f"{fmt(LEAST_DEPTH)} mm a printed D needs to hold; type a Flat of at most {fmt(D - LEAST_DEPTH)} mm, which "
            "leaves the flat a little play, or use a round bore.")


def said_refusal(fields):
    """The sentence a dshape step past a bound is refused with, from the form's fields."""
    D, a, F = hole_of(fields)
    d = d_expected(D, a, F)
    return said_flat_h(D, a, F) if d["h"] < LEAST_H * d["R"] - 1e-9 else said_flat_depth(D, F)


def said_bore_row(bore, allowance):
    """The Derived panel's Bore as cut: 8.2, a middle dot, 8 + 0.2; or the Bore alone with no allowance."""
    D, a = float(bore), float(allowance)
    return fmt(D + a) + (f" {DOT} {fmt(D)} {signed(a)}" if a else "")


def said_flat_row(flat, allowance):
    """The Derived panel's Flat as cut: 7.2, a middle dot, 7 + 0.2."""
    F, a = float(flat), float(allowance)
    return fmt(F + a) + (f" {DOT} {fmt(F)} {signed(a)}" if a else "")


def said_print_bore(bore_text, allowance, flat):
    """The print list's bore, as C words it: bore 8 mm, + 0.2 mm allowance (8.2 mm as cut), and a D's D-flat."""
    a = float(allowance)
    text = f"bore {bore_text} mm"
    if a:
        text += f" {signed(a)} mm allowance ({fmt(float(bore_text) + a)} mm as cut)"
    if flat is not None:
        text += f", D-flat {fmt(flat)} mm" + (f" ({fmt(float(flat) + a)} mm as cut)" if a else "")
    return text


# -- the judgements: plain data in, a list of what is wrong out (empty: it holds) ------------------------------------


def coaxial(face, tol=AXIS_TOL):
    """A cylinder read by CylinderParams (its point in mm) on the part's Z axis through the origin."""
    axis, point = face.get("axis") or (), face.get("point") or ()
    return (len(axis) == 3 and len(point) == 3 and abs(axis[0]) <= tol and abs(axis[1]) <= tol
            and abs(abs(axis[2]) - 1.0) <= tol and math.hypot(point[0], point[1]) <= 1e3 * tol)


def box_reach(box):
    """The farthest a face's box goes from the axis in X or Y (mm)."""
    return max(abs(box[0]), abs(box[1]), abs(box[3]), abs(box[4])) if box and len(box) == 6 else float("inf")


def bore_faces(faces, reach):
    """The faces of the bore: cylinders about the axis under reach (mm, well inside the teeth) and planes square to the
    end faces whose box lies within reach. (cylinders, flats)."""
    cylinders = [f for f in faces if f.get("kind") == "cylinder" and coaxial(f) and f["r"] < reach]
    flats = [f for f in faces if f.get("kind") == "plane" and abs((f.get("normal") or (0, 0, 1))[2]) <= AXIS_TOL
             and box_reach(f.get("box")) < reach]
    return cylinders, flats


def hole_radius(faces, reach):
    """The smallest cylinder about the axis under reach: the hole as cut (mm), or None."""
    cylinders, _ = bore_faces(faces, reach)
    return min((f["r"] for f in cylinders), default=None)


def bore_judged(faces, radius, h=None):
    """The bore as its faces read, without a box wherever a box could mislead (GetBox pads a face's box, about 0.24 mm
    at each end in W9b's reading): every cylinder about the axis in the bore at the hole's radius (CylinderParams); with
    h, a D: those cylinders together reaching -X by their boxes (one-sided, so padding cannot pass a sliver, whose
    round lies between x = h and R), SolidWorks free to make the arc one face or more, and exactly one flat, its normal
    along X and its plane at x = h on +X (PlaneParams' point); without h, no flat at all. The far side shows as the
    plane at -h, a sliver as a round not reaching -X, a wrong chord as the plane off h, a wrong radius as the radius."""
    cylinders, flats = bore_faces(faces, radius + 1.0)
    out = []
    if not cylinders:
        out.append("no cylinder about the axis in the bore")
    off = [round(f["r"], 6) for f in cylinders if abs(f["r"] - radius) > RADIUS_TOL]
    if off:
        out.append(f"the bore's cylinder radius {off}, not {radius:.6f} (to {RADIUS_TOL:g})")
    if h is None:
        if flats:
            out.append(f"{len(flats)} flat face(s) in a round bore")
        return out
    if cylinders and min(c["box"][0] for c in cylinders) > -radius + BOX_TOL:
        out.append(f"the round's box starts at x {min(c['box'][0] for c in cylinders):.4f}: it does not reach -X (the "
                   "minor arc, the sliver)")
    if len(flats) != 1:
        out.append(f"{len(flats)} flat faces in the D, not one")
        return out
    n, root = flats[0]["normal"], flats[0]["root"]
    if abs(abs(n[0]) - 1.0) > AXIS_TOL:
        out.append(f"the flat's normal {[round(v, 9) for v in n]} is not along X")
    elif abs(root[0] - h) > FLAT_TOL:
        out.append(f"the flat's plane at x {root[0]:.6f}, not at h {h:.6f} on +X (to {FLAT_TOL:g})")
    return out


def bore_facts(faces, radius, h=None, chord=None):
    """What the boxes say of the bore, for the log only (M1 of the review: GetBox pads): how many faces the round is,
    its boxes' least and greatest x (the padding beyond -R shown), and on a D the round's greatest x past the flat and
    the flat's span along Y against the chord."""
    cylinders, flats = bore_faces(faces, radius + 1.0)
    out = {"cylinders": len(cylinders), "flats": len(flats)}
    if cylinders:
        x0, x1 = min(c["box"][0] for c in cylinders), max(c["box"][3] for c in cylinders)
        out.update(round_x=[round(x0, 4), round(x1, 4)], padding_beyond_minus_r=round(-radius - x0, 4))
        if h is not None:
            out["round_past_the_flat"] = round(x1 - h, 4)
    if h is not None and len(flats) == 1:
        b = flats[0]["box"]
        out.update(flat_span=round(b[4] - b[1], 4), chord=None if chord is None else round(chord, 4))
    return out


def lands_judged(faces, tip_radius, teeth):
    """The tip lands, the cylinders about the axis at d_a / 2 that the cut spaces leave of the blank's outer cylinder,
    number the teeth. Where they sit (a space on +X, ruling 2) rests on partial faces' boxes no run has read, so it is
    a fact (lands_facts), not judged here."""
    lands = [f for f in faces if f.get("kind") == "cylinder" and coaxial(f) and abs(f["r"] - tip_radius) <= 1e-3]
    return [] if len(lands) == int(teeth) else [f"{len(lands)} tip lands at radius {tip_radius:.4f}, not {teeth}"]


def lands_facts(faces, tip_radius, teeth):
    """The tip lands' box centres as angles: the two nearest +X (a space centred there puts them at plus and minus half
    a pitch) and whether any land's box crosses +X; facts until a log shows partial faces' boxes are tight."""
    lands = [f for f in faces if f.get("kind") == "cylinder" and coaxial(f) and abs(f["r"] - tip_radius) <= 1e-3]
    angles = [math.degrees(math.atan2((f["box"][1] + f["box"][4]) / 2.0, (f["box"][0] + f["box"][3]) / 2.0))
              for f in lands]
    above = min((a for a in angles if a > 0), default=None)
    below = max((a for a in angles if a < 0), default=None)
    across = sum(1 for f in lands if f["box"][3] > 0 and f["box"][1] < 0 < f["box"][4])
    half = 180.0 / int(teeth)
    return {"nearest_above": None if above is None else round(above, 3),
            "nearest_below": None if below is None else round(below, 3), "half_pitch": round(half, 3),
            "crossing_plus_x": across,
            "space_on_plus_x": (above is not None and below is not None and abs(above - half) <= ANGLE_TOL
                                and abs(below + half) <= ANGLE_TOL and not across)}


def undefined(checks):
    """The lines of a build's checks saying a sketch is not fully defined (swbuild's _verify puts them in checks, not
    failures, so a result reads ok with one)."""
    return [str(c) for c in (checks or ()) if "not fully defined" in str(c)]


def gearbox_undefined(result):
    """The same over every part a gearbox build built."""
    return [c for r in getattr(getattr(result, "parts", None), "built", []) or [] for c in undefined(getattr(r, "checks", []))]


def mate_face_judged(entities, component, radius):
    """A mate's entities as Session.mate_definition reads them ([(component Name2, kind, EntityParams)]): exactly one on
    the component, a face, a cylinder's EntityParams (point, axis, radius in metres) of the radius given, to 1e-4 mm."""
    mine = [e for e in entities if e[0] == component]
    if len(mine) != 1:
        return [f"{len(mine)} of the mate's entities on {component}, not one"]
    _, kind, params = mine[0]
    if kind != "face" or len(params) < 7:
        return [f"the mate's entity on {component} is a {kind} with params {list(params)}, not a cylinder's face"]
    got = float(params[6]) * 1000.0
    return [] if abs(got - radius) <= RADIUS_TOL else [f"the mate's face on {component} has radius {got:.6f}, not "
                                                        f"{radius:.6f}"]


def value_judged(value, want):
    """The Equation Manager's own Value of a link against the figure worked here, read as mm or as m (its unit is not
    documented for a dimension's equation): (what is wrong, the unit it agreed in)."""
    if value is None:
        return ["no Value"], ""
    if abs(float(value) - want) <= 1e-6:
        return [], "mm"
    if abs(float(value) * 1000.0 - want) <= 1e-6:
        return [], "m"
    return [f"the Value {value} is {want:.6f} neither in mm nor in m"], ""


def norm(text):
    return "".join(str(text).split())


def link_judged(equations, values, dimension, app_text, want, split, evaluate):
    """One link as SolidWorks holds it ([(text, value)] of the Equation Manager; values its names' values): exactly one
    equation for the dimension, its expression the app's text (spaces aside), no sqr, and evaluated here on the values
    SolidWorks holds to want (mm). split and evaluate are the app's equation reader and evaluator."""
    found = []
    for text, value in equations:
        try:
            name, expression = split(text)
        except ValueError:
            continue
        if name == dimension:
            found.append((expression, value))
    if len(found) != 1:
        return [f"{len(found)} equations for {dimension!r}, not one"]
    expression, _ = found[0]
    out = []
    if norm(expression) != norm(app_text):
        out.append(f"{dimension} reads {expression!r}, not the app's {app_text!r}")
    if re.search(r"\bsqr\b", expression, re.I):
        out.append(f"{dimension} holds sqr")
    try:
        got = float(evaluate(expression, values))
    except Exception as exc:  # noqa: BLE001 - what will not evaluate is said
        return out + [f"{dimension} does not evaluate here: {type(exc).__name__}: {exc}"]
    if abs(got - want) > EQ_TOL:
        out.append(f"{dimension} evaluates to {got:.9f}, not {want:.9f}")
    wrong, _ = value_judged(found[0][1], want)
    out += [f"{dimension}: {w}" for w in wrong]
    return out


def volume_judged(volume, reference, tol=VOLUME_TOL):
    if volume is None or not reference:
        return [f"no volume to compare ({volume} against {reference})"]
    rel = abs(volume - reference) / reference
    return [] if rel <= tol else [f"the volume {volume:.4f} is {rel:.2e} off its twin's {reference:.4f}, over {tol:g}"]


def stem_lists_judged(what, got, want):
    return F2P.stem_lists_judged(what, got, want)


# A STEP file's faces, read as text apart from printout's reader: each ADVANCED_FACE's surface, a PLANE or a
# CYLINDRICAL_SURFACE by its AXIS2_PLACEMENT_3D (location, axis; a cylinder's radius), in the file's unit (mm).
_REF = re.compile(r"#(\d+)")
_FACE = re.compile(r"ADVANCED_FACE\s*\(\s*'[^']*'\s*,\s*\((.*)\)\s*,\s*#(\d+)\s*,\s*\.[TF]\.\s*\)$", re.S)


def _triple(body):
    m = re.search(r"\(\s*'[^']*'\s*,\s*\(([^)]*)\)\s*\)", body)
    try:
        return tuple(float(v) for v in m.group(1).split(",")) if m else None
    except ValueError:
        return None


# The entities a face's bounds pass through on the way to its vertices: never its surface, nor an edge's curve.
_BOUND_KINDS = ("FACE_OUTER_BOUND", "FACE_BOUND", "EDGE_LOOP", "ORIENTED_EDGE", "EDGE_CURVE", "VERTEX_LOOP")


def _face_vertices(data, bounds):
    """The points of every VERTEX_POINT a face's bounds reach (its loops, their edges, their ends), in the file's unit."""
    seen, todo, points = set(), [int(r) for r in _REF.findall(bounds)], []
    while todo:
        ref = todo.pop()
        if ref in seen:
            continue
        seen.add(ref)
        body = data.get(ref, "")
        name = body.split("(", 1)[0].strip().upper()
        if name == "VERTEX_POINT":
            refs = _REF.findall(body)
            p = _triple(data.get(int(refs[0]), "")) if refs else None
            if p is not None and len(p) == 3:
                points.append(p)
        elif name in _BOUND_KINDS:
            todo.extend(int(r) for r in _REF.findall(body))
    return points


def step_faces(text):
    """[("plane", location, normal, vertices) | ("cylinder", location, axis, radius) | ("other",)] of every
    ADVANCED_FACE; a plane's vertices are those its bounds reach (_face_vertices)."""
    data = {}
    for m in F2P._STATEMENT.finditer(text or ""):  # noqa: SLF001
        s = m.group(0)[:-1].replace("\r", "").replace("\n", " ").strip()
        d = re.match(r"#(\d+)\s*=\s*(.*)$", s, re.S)
        if d:
            data[int(d.group(1))] = d.group(2).strip()

    def placement(ref):
        body = data.get(ref, "")
        refs = [int(r) for r in _REF.findall(body)]
        if not body.upper().startswith("AXIS2_PLACEMENT_3D") or len(refs) < 2:
            return None, None
        return _triple(data.get(refs[0], "")), _triple(data.get(refs[1], ""))
    out = []
    for body in data.values():
        f = _FACE.match(body)
        if not f:
            continue
        surface = data.get(int(f.group(2)), "")
        refs = [int(r) for r in _REF.findall(surface)]
        name = surface.split("(", 1)[0].strip().upper()
        if name == "PLANE" and refs:
            out.append(("plane",) + placement(refs[0]) + (_face_vertices(data, f.group(1)),))
        elif name == "CYLINDRICAL_SURFACE" and refs:
            loc, axis = placement(refs[0])
            r = re.search(r",\s*([-+0-9.Ee]+)\s*\)\s*$", surface)
            out.append(("cylinder", loc, axis, float(r.group(1)) if r else None))
        else:
            out.append(("other",))
    return out


def step_bore_judged(text, radius, h=None, reach=None):
    """The bore as the STEP file holds it: one cylinder or more about Z of the hole's radius (a D's arc one or more), to STEP_TOL;
    with h, exactly one plane face square to the end faces within reach, its normal along X, its location on x = h;
    without, none; the least VERTEX_POINT radius (D + a)/2, and on a D at least two vertices of that radius at x = h.
    A plane face is within reach when every vertex its bounds reach is: the plane's own distance from the axis does not
    tell, since a tooth's radial flank lies on a plane through the axis (SolidWorks 2026's first print run: 40 of them).
    A plane face square to the end faces whose bounds reach no vertex fails, so no face is passed unread."""
    reach = reach if reach is not None else radius + 1.0
    faces = step_faces(text)
    cylinders = [f for f in faces if f[0] == "cylinder" and f[1] and f[2] and f[3] is not None
                 and abs(abs(f[2][2]) - 1.0) <= AXIS_TOL and math.hypot(f[1][0], f[1][1]) <= 1e-3 and f[3] < reach]
    square = [f for f in faces if f[0] == "plane" and f[1] and f[2] and abs(f[2][2]) <= AXIS_TOL]
    planes = [f for f in square if f[3] and all(math.hypot(p[0], p[1]) < reach for p in f[3])]
    out = []
    unread = sum(1 for f in square if not f[3])
    if unread:
        out.append(f"{unread} plane face(s) square to the end faces whose bounds reach no vertex")
    if not cylinders:
        out.append("no cylinder about Z in the bore")
    off = [round(f[3], 6) for f in cylinders if abs(f[3] - radius) > STEP_TOL]
    if off:
        out.append(f"the bore's cylinder radius {off}, not {radius:.4f} (to {STEP_TOL:g})")
    if h is None and planes:
        out.append(f"{len(planes)} plane(s) in a round bore")
    if h is not None:
        if len(planes) != 1:
            out.append(f"{len(planes)} planes in the D, not one")
        elif abs(abs(planes[0][2][0]) - 1.0) > AXIS_TOL or abs(planes[0][1][0] - h) > STEP_TOL:
            out.append(f"the D's plane at {planes[0][1]} with normal {planes[0][2]}, not on x = {h:.4f}")
    vertices = [p for p in F2P.step_read(text)["vertices"] if len(p) == 3]
    radii = [math.hypot(p[0], p[1]) for p in vertices]
    least = min(radii) if radii else None
    if least is None or abs(least - radius) > STEP_TOL:
        out.append(f"the least vertex radius {least}, not {radius:.4f}")
    if h is not None:
        corners = [p for p, r in zip(vertices, radii) if abs(r - radius) <= STEP_TOL and abs(p[0] - h) <= STEP_TOL]
        if len(corners) < 2:
            out.append(f"{len(corners)} vertices of radius {radius:.4f} at x = {h:.4f}, not two or more")
    return out


def sidecar_schema(text):
    """A .gear.json's schemaVersion, None when it does not read."""
    try:
        return json.loads(text).get("schemaVersion")
    except (ValueError, AttributeError):
        return None


def globals_judged(values, allowance, flat):
    """The F3 globals as SolidWorks holds them ({name: value}): "Bore Allowance" the allowance exactly when it is not 0,
    "Bore Flat" the Flat exactly with a D, and neither otherwise."""
    out = []
    for name, want in ((ALLOWANCE_GLOBAL, allowance if allowance else None), (FLAT_GLOBAL, flat)):
        got = values.get(name)
        if want is None and got is not None:
            out.append(f'"{name}" = {got} where the part should hold none')
        elif want is not None and (got is None or abs(float(got) - float(want)) > 1e-9):
            out.append(f'"{name}" = {got}, not {want}')
    return out


# -- the strip's form, as the live sections and the self-check set it -------------------------------------------------


def form_set(app, folder, fields, name="", process="printed"):
    """The strip's form as a person sets it for one gear: Single gear, the process, the kind, the fields typed (Bore
    allowance, Drive and Flat put to blank, round and blank unless given), the Name; worked out by its own _derive_now."""
    from gear_generator import gui
    from gear_generator.spec import MODE_SINGLE, PROCESS_MACHINED, PROCESS_PRINTED
    app.mode.set(MODE_SINGLE)
    app._on_mode_changed()  # noqa: SLF001
    app.out_folder.set(folder)
    app.process.set(PROCESS_PRINTED if process == "printed" else PROCESS_MACHINED)
    app.kind.set(fields.get("kind", "spur"))
    app._on_kind_changed()  # noqa: SLF001
    blank = {"bore_allowance": "", "drive": "round", "flat": ""}
    for field, attr in gui.GEAR_VARS:
        if field in fields or field in blank:
            app.gear_vars["a"][attr].set(fields.get(field, blank.get(field)))
    app.gear_vars["a"]["name"].set(name)
    app._derive_now()  # noqa: SLF001


def strip_press(app, strand, changes, snapshot):
    """Update values pressed on the strip as a person presses it: the fields changed, the bar's snapshot read, the form
    worked out, then the form's own _update_values and, a job having answered, its own _collect_build. What the strip
    counted for Update values first, the jobs submitted, the status and the form's errors."""
    for attr, value in changes.items():
        app.gear_vars["a"][attr].set(value)
    app._snapshot = snapshot  # noqa: SLF001
    app._derive_now()  # noqa: SLF001
    count = app._update_target()[0]  # noqa: SLF001
    jobs = len(strand.jobs)
    app._update_values()  # noqa: SLF001
    if app._pending_build is not None:  # noqa: SLF001
        app._collect_build()  # noqa: SLF001
    return {"count": count, "jobs": strand.jobs[jobs:], "status": app.status.get(),
            "errors": [d.message for d in app._diagnostics["a"] if d.is_error]}  # noqa: SLF001


# -- --self-check -------------------------------------------------------------------------------------------------------


def arc_box(r, a0, a1, z0=0.0, z1=8.0):
    """The box of an arc of radius r from a0 to a1 degrees (counter-clockwise), mm, as [x0, y0, z0, x1, y1, z1]."""
    span = (a1 - a0) % 360.0 or 360.0
    xs, ys = [], []
    for i in range(721):
        a = math.radians(a0 + span * i / 720.0)
        xs.append(r * math.cos(a))
        ys.append(r * math.sin(a))
    return [min(xs), min(ys), z0, max(xs), max(ys), z1]


def made_faces(radius, h=None, chord=None, *, sliver=False, flat_x=None, two_flats=False, teeth=20, tip=16.5,
               shift=0.0, lands=None, pad=0.0, split=False):
    """Made-up face reads of a printed spur's part, as part_faces gives them: the tip lands about the axis, a fillet
    off it, the two end faces, and the bore (a round, or a D's arc and flat)."""
    faces = [{"kind": "plane", "normal": (0.0, 0.0, s), "root": (0.0, 0.0, z), "box": [-tip, -tip, z, tip, tip, z]}
             for s, z in ((-1.0, 0.0), (1.0, 8.0))]
    pitch = 360.0 / teeth
    for k in range(teeth if lands is None else lands):
        centre = (k + 0.5) * pitch + shift
        faces.append({"kind": "cylinder", "r": tip, "axis": (0.0, 0.0, 1.0), "point": (0.0, 0.0, 0.0),
                      "box": arc_box(tip, centre - 2.0, centre + 2.0)})
    faces.append({"kind": "cylinder", "r": 0.57, "axis": (0.0, 0.0, 1.0), "point": (13.0, 1.0, 0.0),
                  "box": [12.4, 0.4, 0.0, 13.6, 1.6, 8.0]})
    if h is None:
        faces.append({"kind": "cylinder", "r": radius, "axis": (0.0, 0.0, -1.0), "point": (0.0, 0.0, 0.0),
                      "box": arc_box(radius, 0.0, 360.0)})
        return faces
    half = math.degrees(math.acos(h / radius))
    a0, a1 = ((-half, half) if sliver else (half, 360.0 - half))
    for b0, b1 in ([(a0, 180.0), (180.0, a1)] if split else [(a0, a1)]):
        faces.append({"kind": "cylinder", "r": radius, "axis": (0.0, 0.0, 1.0), "point": (0.0, 0.0, 0.0),
                      "box": arc_box(radius, b0, b1)})
    for x in ([flat_x if flat_x is not None else h] + ([-h] if two_flats else [])):
        faces.append({"kind": "plane", "normal": (-1.0, 0.0, 0.0), "root": (x, 0.0, 4.0),
                      "box": [x, -chord / 2.0, 0.0, x, chord / 2.0, 8.0]})
    for f in faces:          # GetBox pads every box (W9b: about 0.24 mm at each end)
        f["box"] = [v - pad for v in f["box"][:3]] + [v + pad for v in f["box"][3:]]
    return faces


def made_step_bore(radius, h=None, chord=None, *, plane_x=None, extra_plane=False, r_off=0.0, vertex_off=0.0,
                   split=False, teeth=2, bounds=True):
    """A made-up STEP file of a printed spur's bore as SolidWorks writes one: the bore's cylinder and the D's plane as
    ADVANCED_FACEs on their AXIS2_PLACEMENT_3Ds, the gear's outer cylinder, an end face, teeth radial flanks (planes
    through the axis, out at the teeth, as SolidWorks 2026 wrote the tooth spaces' straight sides), and the vertices.
    Each plane square to the end faces is bounded by a loop through its corners' VERTEX_POINTs (with bounds False the
    D's plane's bound reaches nothing, its corners left as loose vertices)."""
    lines = ["ISO-10303-21;", "HEADER;", "FILE_SCHEMA (( 'AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }' ));", "ENDSEC;",
             "DATA;"]
    n = [100]

    def add(body):
        n[0] += 1
        lines.append(f"#{n[0]} = {body} ;")
        return n[0]

    def point(x, y, z):
        return add(f"CARTESIAN_POINT ( 'NONE',  ( {x:.12f}, {y:.12f}, {z:.12f} ) )")

    def direction(x, y, z):
        return add(f"DIRECTION ( 'NONE',  ( {x:.12f}, {y:.12f}, {z:.12f} ) )")

    def place(p, d, r):
        return add(f"AXIS2_PLACEMENT_3D ( 'NONE', #{point(*p)}, #{direction(*d)}, #{direction(*r)} )")

    def face(surface):
        return add(f"ADVANCED_FACE ( 'NONE', ( #{add('FACE_OUTER_BOUND ( ''NONE'', #1, .T. )')} ), #{surface}, .T. )")

    def vertex(p):           # the bore's vertices moved out by vertex_off, the teeth's left
        scale = (radius + vertex_off) / radius if math.hypot(p[0], p[1]) < radius + 1.0 else 1.0
        return add(f"VERTEX_POINT ( 'NONE', #{point(p[0] * scale, p[1] * scale, p[2])} )")
    line = add(f"LINE ( 'NONE', #{point(0, 0, 0)}, #{direction(0, 0, 1)} )")   # an edge's curve: never walked

    def bounded(surface, corners):
        ends = [vertex(p) for p in corners]
        edges = []
        for a, b in zip(ends, ends[1:] + ends[:1]):
            curve = add(f"EDGE_CURVE ( 'NONE', #{a}, #{b}, #{line}, .T. )")
            edges.append(add(f"ORIENTED_EDGE ( 'NONE', *, *, #{curve}, .T. )"))
        loop = add("EDGE_LOOP ( 'NONE', ( " + ", ".join(f"#{e}" for e in edges) + " ) )")
        bound = add(f"FACE_OUTER_BOUND ( 'NONE', #{loop}, .T. )")
        return add(f"ADVANCED_FACE ( 'NONE', ( #{bound} ), #{surface}, .T. )")

    def rect(x, half):
        return [(x, -half, 0.0), (x, half, 0.0), (x, half, 8.0), (x, -half, 8.0)]
    for _ in range(2 if split else 1):
        face(add(f"CYLINDRICAL_SURFACE ( 'NONE', #{place((0, 0, 0), (0, 0, 1), (1, 0, 0))}, {radius + r_off:.12f} )"))
    face(add(f"CYLINDRICAL_SURFACE ( 'NONE', #{place((0, 0, 0), (0, 0, 1), (1, 0, 0))}, 16.5 )"))
    face(add(f"PLANE ( 'NONE', #{place((0, 0, 8), (0, 0, 1), (1, 0, 0))} )"))
    for k in range(teeth):   # a radial flank: its plane through the axis, its face from the root out to the tip
        a = math.radians(4.2 + 18.0 * k)
        c, s = math.cos(a), math.sin(a)
        bounded(add(f"PLANE ( 'NONE', #{place((14.0 * c, 14.0 * s, 0), (-s, c, 0), (c, s, 0))} )"),
                [(13.0 * c, 13.0 * s, 0.0), (16.5 * c, 16.5 * s, 0.0), (16.5 * c, 16.5 * s, 8.0), (13.0 * c, 13.0 * s, 8.0)])
    if h is not None:
        x = h if plane_x is None else plane_x
        surface = add(f"PLANE ( 'NONE', #{place((x, 0, 0), (-1, 0, 0), (0, 1, 0))} )")
        if bounds:
            bounded(surface, rect(x, chord / 2.0))
        else:
            face(surface)
            for p in rect(x, chord / 2.0):
                vertex(p)
        if extra_plane:
            bounded(add(f"PLANE ( 'NONE', #{place((-x, 0, 0), (1, 0, 0), (0, 1, 0))} )"), rect(-x, chord / 2.0))
    else:
        for p in [(-radius, 0.0, 0.0), (-radius, 0.0, 8.0)]:
            vertex(p)
    for p in [(16.5, 0.0, 0.0), (0.0, 16.5, 8.0)]:
        vertex(p)
    lines += ["ENDSEC;", "END-ISO-10303-21;"]
    return "\n".join(lines) + "\n"


def pinned_tests():
    """tests/test_printed_rule.py, F3-0's pins, imported. Where pytest is not installed (Windows' python.exe) a stand-in
    gives the decorators the module uses at import; nothing of pytest runs."""
    import importlib.util
    try:
        import pytest  # noqa: F401
    except ImportError:
        stub = types.ModuleType("pytest")

        class _Mark:
            def __getattr__(self, name):
                return lambda *args, **kwargs: (lambda fn: fn)
        stub.mark = _Mark()
        stub.fixture = lambda *args, **kwargs: args[0] if args and callable(args[0]) else (lambda fn: fn)
        sys.modules["pytest"] = stub
    path = os.path.join(REPO, "tests", "test_printed_rule.py")
    spec = importlib.util.spec_from_file_location("f3_pinned_rule", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def self_check():
    import shutil
    import tempfile
    scratch = tempfile.mkdtemp(prefix="f3-self-check-")
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


def _spec_of(fields, process="printed", **more):
    from gear_generator.spec import GearSpec
    return GearSpec(**{**fields, "process": process, **more})


def _self_check(ok, scratch):
    from gear_generator import gui, printout as po, spec as specs, store, swbuild, ui_text
    from gear_generator.gears import kind_for, spur
    from gear_generator.gears.equations import DEGREES, evaluate, split_equation
    from gear_generator.workbook import schema

    # 1. The names and bounds this script pins, against the app's.
    titles = {c.key: c.title for c in schema.GEARS.columns}
    ok(hasattr(spur, SWITCH) and spur.FLAT_LEAST_H == LEAST_H and spur.FLAT_LEAST_DEPTH == LEAST_DEPTH
       and specs.BORE_ALLOWANCE_DEFAULT == DEFAULT_ALLOWANCE and spur.BORE_SKETCH == SKETCH
       and (spur.BORE_ALLOWANCE, spur.BORE_FLAT, spur.BORE) == (ALLOWANCE_GLOBAL, FLAT_GLOBAL, BORE_GLOBAL)
       and tuple(titles.get(k) for k in ("bore_allowance", "drive", "flat")) == BORE_TITLES,
       f"names: spur.{SWITCH} exists (reads {getattr(spur, SWITCH, None)!r} here), the bounds 0.25 R and 0.3 mm, the "
       f"default 0.2, the Bore Sketch, the three globals and the Gears titles {BORE_TITLES} are the app's")

    # 2. §4.2 worked here, against the plan's table and package A's d_flat.
    off = []
    for (D, a, F), (h, R, chord, sweep) in PLAN_TABLE:
        d = d_expected(D, a, F)
        if abs(d["h"] - h) > 5e-5 or abs(d["R"] - R) > 5e-5 or abs(d["chord"] - chord) > 5e-5 \
                or abs(d["sweep"] - sweep) > 5e-3:
            off.append(((D, a, F), d))
    states = [hole_of(part) for _, _, how, _, part in dshape_states()] + [hole_of(DSHAPE)]
    for D, a, F in [k for k, _ in PLAN_TABLE] + [s for s in states if s[2] is not None]:
        d, app = d_expected(D, a, F), spur.d_flat(D, a, F)
        if max(abs(d["h"] - app.h), abs(d["R"] - app.radius), abs(d["chord"] - app.chord),
               abs(d["sweep"] - app.sweep_deg), abs(d["least"] - app.least_flat), abs(d["most"] - app.most_flat)) > 1e-9:
            off.append(("A", (D, a, F)))
    ok(not off, f"maths: R, h, the chord, the sweep and the bounds' Flats hold §4.2's six rows and agree with A's d_flat "
                f"on every dshape state: {off or 'all'}")

    # 3. dshape's steps, offline: each value step plans exactly the globals it changes and is no structural change;
    # each bound step is A's error at Flat in the words here; each structural step is B's sentence here.
    wrong = []
    part, words = dict(DSHAPE), {}
    for tag, changes, how, form, after in dshape_states():
        built = _spec_of(part)
        wanted = _spec_of(form)
        kind = kind_for(wanted)
        built_vars = [[v.name, v.expression_for(DEGREES)] for v in kind.variables(built, kind.derive(built))]
        errors = [d for d in kind.validate(wanted) if d.is_error]
        reason = swbuild.structural_change(built.to_dict(), wanted.to_dict(), built_variables=built_vars)
        if how == "value":
            held = dict(built_vars)
            planned = {v.name: v.expression_for(DEGREES) for v in kind.variables(wanted, kind.derive(wanted))}
            moved = {n for n, e in planned.items() if norm(held.get(n, "")) != norm(e)}
            want = {GLOBAL_OF[k] for k, v in changes.items() if part.get(k) != v}
            if errors or reason or moved != want:
                wrong.append((tag, [e.message for e in errors], reason, sorted(moved), sorted(want)))
            part = dict(form)
        elif how == "bound":
            said = said_refusal(form)
            words[tag] = said
            if [(e.field, e.message) for e in errors] != [("flat", said)]:
                wrong.append((tag, [(e.field, e.message) for e in errors], said))
        else:
            said = SAID_ALLOWANCE if "drive" not in changes else said_drive("flat", "round")
            words[tag] = said
            if errors or reason != said:
                wrong.append((tag, reason, said))
    rd = _spec_of(dict(DSHAPE, drive="round", flat=""))
    dd = _spec_of(DSHAPE)
    to_round = swbuild.structural_change(dd.to_dict(), rd.to_dict(), built_variables=[[ALLOWANCE_GLOBAL, "0.2"],
                                                                                         [FLAT_GLOBAL, "7"]])
    to_d = swbuild.structural_change(rd.to_dict(), dd.to_dict(), built_variables=[[ALLOWANCE_GLOBAL, "0.2"]])
    ok(not wrong and to_round == said_drive("flat", "round") and to_d == said_drive("round", "flat"),
       f"dshape offline: every value step plans exactly its own globals and is no structural change; the two bound "
       f"steps are A's error at Flat in this script's words; the allowance to 0 and Drive to round are B's sentences "
       f"here, and so are D to round and round to D: {wrong or 'all'}")

    # 4. The links: the app's texts evaluate to the figures here, as SolidWorks would hold them, and SolidWorks' own
    # Value (in mm or in m) agrees; each fault fails.
    held_ok, faults = [], {}
    ev = (lambda e, v: evaluate(e, v, DEGREES))
    for D, a, F in [hole_of(p) for _, _, how, _, p in dshape_states() if how == "value"] + [hole_of(DSHAPE)]:
        gs = _spec_of(dict(DSHAPE, bore=str(D), bore_allowance=str(a), flat=str(F)))
        g = kind_for(gs).derive(gs)
        cut, radius_expr, h_expr = spur.bore_expressions(g)
        chord_expr = spur.chord_expression(radius_expr, h_expr)
        values = {BORE_GLOBAL: D, ALLOWANCE_GLOBAL: a, FLAT_GLOBAL: F}
        d = d_expected(D, a, F)
        eqs = [(f'"{BORE_GLOBAL}" = {D}', D), (f'"{ALLOWANCE_GLOBAL}" = {a}', a), (f'"{FLAT_GLOBAL}" = {F}', F),
               (f'"{BORE_DIM}" = {radius_expr}', d["R"] / 1000.0), (f'"{FLAT_DIM}" = {chord_expr}', d["chord"])]
        held_ok.append(link_judged(eqs, values, FLAT_DIM, chord_expr, d["chord"], split_equation, ev)
                       + link_judged(eqs, values, BORE_DIM, radius_expr, d["R"], split_equation, ev))
        faults = {
            "sqr": link_judged([(t.replace("^ 0.5", "") .replace("( ( abs", "( sqr ( abs") if FLAT_DIM in t else t, v)
                                for t, v in eqs], values, FLAT_DIM, chord_expr, d["chord"], split_equation, ev),
            "the far side's chord": link_judged(eqs, values, FLAT_DIM, chord_expr, d["chord"] + 0.01, split_equation, ev),
            "missing": link_judged(eqs[:4], values, FLAT_DIM, chord_expr, d["chord"], split_equation, ev),
            "twice": link_judged(eqs + eqs[-1:], values, FLAT_DIM, chord_expr, d["chord"], split_equation, ev),
            "another text": link_judged(eqs, values, FLAT_DIM, chord_expr.replace("2 *", "2.0 *"), d["chord"],
                                        split_equation, ev),
            "SolidWorks' Value off": link_judged(eqs[:4] + [(eqs[4][0], d["chord"] + 0.01)], values, FLAT_DIM,
                                                 chord_expr, d["chord"], split_equation, ev)}
    units = (value_judged(5.3666, 5.3666), value_judged(0.0053666, 5.3666), value_judged(0.53666, 5.3666),
             value_judged(None, 5.3666))
    ok(not any(held_ok) and all(faults.values()) and "^ 0.5" in chord_expr and "abs" in chord_expr
       and [u[1] for u in units] == ["mm", "m", "", ""] and not units[0][0] and units[2][0] and units[3][0],
       f"links: the app's chord and radius links, as SolidWorks would give them back, evaluate here to the chord and R "
       f"on every dshape state, and SolidWorks' own Value agrees read in mm (the chord) or in m (the radius); sqr, a "
       f"chord 0.01 off, none, two, another text and a Value 0.01 off each fail, and a Value in neither unit: "
       f"{[h for h in held_ok if h] or 'held'}; faults caught {sorted(k for k, v in faults.items() if v)}")

    # 5. The bore by its faces: judged without the boxes' padding (the review's M1), a split arc accepted (S1).
    d = d_expected(8, 0.2, 7)
    R, h, c = d["R"], d["h"], d["chord"]
    good = made_faces(R, h, c)
    holds = {"exact boxes": good, "boxes padded 0.25 mm (W9b measured 0.24)": made_faces(R, h, c, pad=0.25),
             "the arc as two faces": made_faces(R, h, c, split=True),
             "two faces, padded": made_faces(R, h, c, split=True, pad=0.25)}
    cases = {"the sliver": made_faces(R, h, c, sliver=True), "the sliver padded": made_faces(R, h, c, sliver=True,
                                                                                            pad=0.25),
             "the flat on -X": made_faces(R, h, c, flat_x=-h), "two flats": made_faces(R, h, c, two_flats=True),
             "the radius 2e-4 over": made_faces(R + 2e-4, h, c), "the flat 2e-4 off": made_faces(R, h, c, flat_x=h + 2e-4),
             "a round where a D is wanted": made_faces(R)}
    failed = [k for k, f in holds.items() if bore_judged(f, R, h)]
    held = [k for k, f in cases.items() if not bore_judged(f, R, h)]
    facts = bore_facts(made_faces(R, h, c, pad=0.25), R, h, c)
    ok(not failed and not held and bore_judged(made_faces(R), R) == [] and bore_judged(good, R) != []
       and bore_judged([f for f in good if not (f["kind"] == "cylinder" and f["r"] == R)], R, h) != []
       and abs(facts["padding_beyond_minus_r"] - 0.25) < 1e-3 and abs(facts["round_past_the_flat"] - 0.25) < 1e-3
       and abs(facts["flat_span"] - (c + 0.5)) < 1e-3,
       f"faces: the D (every round face of R about the axis, together reaching -X; one flat at h on +X) and a round bore "
       f"hold with {', '.join(holds)}; a D read as round, no cylinder, and {', '.join(cases)} each fail; the boxes' "
       f"padding is logged, not judged ({facts}): failed {failed or 'none'}, held {held or 'none'}")
    lf = lands_facts(good, 16.5, 20)
    ok(lands_judged(good, 16.5, 20) == [] and lands_judged(made_faces(R, h, c, pad=0.25), 16.5, 20) == []
       and lands_judged(made_faces(R, h, c, lands=19), 16.5, 20) != []
       and lf["space_on_plus_x"] and not lands_facts(made_faces(R, h, c, shift=9.0), 16.5, 20)["space_on_plus_x"],
       f"faces: the tip lands number the teeth, padded or not; a land missing fails; where they sit is a fact, a space on "
       f"+X read so and a tooth on +X not: {lf}")
    ok(volume_judged(100.0, 100.05) == [] and volume_judged(100.0, 100.2) != [] and volume_judged(None, 100.0) != []
       and volume_judged(100.0, 0.0) != [], "volume: 0.05 % holds; 0.2 %, no volume and no twin each fail")
    ok(undefined(["Bore Sketch is fully defined", "a value checked"]) == []
       and undefined(["Bore Sketch is under-defined, not fully defined"]) != []
       and gearbox_undefined(types.SimpleNamespace(parts=types.SimpleNamespace(built=[
           types.SimpleNamespace(checks=[]), types.SimpleNamespace(checks=["Tooth Space Sketch is over-defined, not "
                                                                           "fully defined"])]))) != []
       and gearbox_undefined(types.SimpleNamespace(parts=types.SimpleNamespace(built=[]))) == [],
       "sketches: a build's checks saying a sketch is not fully defined are caught, a part's among a gearbox's too")
    ent = [("Sun-1", "face", (0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0041)), ("Sprocket-4", "face", (0, 0, 0, 0, 0, 1, 0.005))]
    ok(mate_face_judged(ent, "Sun-1", 4.1) == [] and mate_face_judged(ent, "Sun-1", 4.15) != []
       and mate_face_judged([("Sun-1", "edge", ())] + ent[1:], "Sun-1", 4.1) != []
       and mate_face_judged(ent[1:], "Sun-1", 4.1) != [] and mate_face_judged(ent + ent[:1], "Sun-1", 4.1) != [],
       "mates: the bore mate's entity on Sun a face of radius 4.1 by EntityParams holds; another radius (a carry onto "
       "another face about the axis), an edge, none and two each fail")

    # 6. The bore read from a STEP file. Every made-up file holds teeth radial flanks, planes through the axis out at the
    # teeth, as SolidWorks 2026 wrote them; the reading at c5d4391 counted each as in the bore (its plane's distance from
    # the axis), so its count of the made-up D's planes is held at 3 here to show the files carry what failed it.
    def _old_step_planes(text):
        return sum(1 for f in step_faces(text) if f[0] == "plane" and f[1] and f[2] and abs(f[2][2]) <= AXIS_TOL
                   and abs(sum(p * n for p, n in zip(f[1], f[2]))) < R + 1.0)
    step_cases = {"the plane on -X": made_step_bore(R, h, c, plane_x=-h), "two planes": made_step_bore(R, h, c,
                                                                                                      extra_plane=True),
                  "the radius 0.02 over": made_step_bore(R, h, c, r_off=0.02),
                  "the vertices 0.02 out": made_step_bore(R, h, c, vertex_off=0.02),
                  "a round where a D is wanted": made_step_bore(R),
                  "the D's plane with bounds that reach no vertex": made_step_bore(R, h, c, bounds=False)}
    held = [k for k, t in step_cases.items() if not step_bore_judged(t, R, h)]
    faces = step_faces(made_step_bore(R, h, c))
    ok(step_bore_judged(made_step_bore(R, h, c), R, h) == [] and step_bore_judged(made_step_bore(R), R) == []
       and step_bore_judged(made_step_bore(R, h, c, split=True), R, h) == []
       and step_bore_judged(made_step_bore(R, h, c), R) != [] and not held
       and sorted(f[0] for f in faces) == ["cylinder", "cylinder"] + ["plane"] * 4
       and step_bore_judged(made_step_bore(R, h, c, teeth=40), R, h) == [] and step_bore_judged(made_step_bore(R, teeth=40), R) == []
       and _old_step_planes(made_step_bore(R, h, c)) == 3,
       f"step: the D (one cylinder of R about Z, or the arc as two, one plane face in the bore by its vertices, on x = h, "
       f"the least vertex radius R, the flat's corners at x = h) and a round bore hold, with two teeth radial flanks or "
       f"forty (planes through the axis, which the reading at c5d4391 counted in the bore: 3 planes in the D), read "
       f"through F2's statement splitter; a D read as round and "
       f"{', '.join(step_cases)} each fail: held {held or 'none'}")

    # 7. The words, against the app's own.
    from gear_generator.gears import kind_for as kf
    rows_wrong = []
    for fields, want in ((DSHAPE, (said_bore_row(8, 0.2), said_flat_row(7, 0.2))),
                         (dict(DSHAPE, bore_allowance="-0.1"), (said_bore_row(8, -0.1), said_flat_row(7, -0.1))),
                         (dict(COUPON, bore_allowance="0"), (said_bore_row(8, 0), None))):
        got = dict(ui_text.bore_rows(kf(_spec_of(fields)).derive(_spec_of(fields))))
        if (got.get(ui_text.BORE_AS_CUT_LABEL), got.get(ui_text.FLAT_AS_CUT_LABEL)) != want:
            rows_wrong.append((fields, got, want))
    lines = []
    with F2P.patched(spur, {SWITCH: True}):
        for fields, variables, want in (
                (DSHAPE, [[ALLOWANCE_GLOBAL, "0.2"], [FLAT_GLOBAL, "7"]], said_print_bore("8", 0.2, 7.0)),
                (PRINT_ROUND, [[ALLOWANCE_GLOBAL, "0.2"]], said_print_bore("8", 0.2, None)),
                (dict(PRINT_ROUND, bore_allowance="-0.1"), [[ALLOWANCE_GLOBAL, "-0.1"]], said_print_bore("8", -0.1, None)),
                (COUPON, [], said_print_bore("8", 0, None))):
            part = po.print_part("C:\\a\\P.SLDPRT", _spec_of(fields).to_dict(), variables=variables)
            if ui_text._print_bore(part) != want:  # noqa: SLF001
                lines.append((fields, ui_text._print_bore(part), want))  # noqa: SLF001
    gui_src = open(gui.__file__, encoding="utf-8").read()
    ok(not rows_wrong and not lines and SAID_NOT_WORKED in gui_src,
       f"words: Bore as cut and Flat as cut, the print list's bore (a D typed, a round at the default, a press fit, a "
       f"part built before F3) and Update values' refusal of a form that does not work out are the app's: "
       f"{rows_wrong or lines or 'the same'}")

    # 8. allowance, offline: the hole as cut, the globals and the schema of each kind, printed and machined.
    wrong = []
    for name, fields, typed in ALLOWANCE_KINDS:
        for how, process, allowance, want_a in (("default", "printed", "", DEFAULT_ALLOWANCE),
                                                ("typed", "printed", typed, float(typed)),
                                                ("machined", "machined", "", 0.0)):
            spec = _spec_of(fields, process=process, bore_allowance=allowance)
            kind = kind_for(spec)
            with F2P.patched(spur, {SWITCH: True}):
                derived = kind.derive(spec)
                variables = [[v.name, v.expression_for(DEGREES)] for v in kind.variables(spec, derived)]
                errors = [e.message for e in kind.validate(spec) if e.is_error]
            # a helical gear's hole is on its section; a bevel gear's on its derived, whose section has no bore
            holder = derived if getattr(derived, "bore", 0) else getattr(derived, "section", derived)
            values = {n: e for n, e in variables}
            D = float(spec.bore)
            schema_ = store.sidecar_schema(spec.to_dict(), variables)
            if errors or abs(holder.bore_as_cut - (D + want_a)) > 1e-9 or schema_ != (4 if want_a else 1) \
                    or (ALLOWANCE_GLOBAL in values) != bool(want_a) or FLAT_GLOBAL in values \
                    or (want_a and abs(float(values[ALLOWANCE_GLOBAL]) - want_a) > 1e-12):
                wrong.append((name, how, errors, holder.bore_as_cut, schema_, values.get(ALLOWANCE_GLOBAL)))
        with F2P.patched(spur, {SWITCH: False}):
            spec = _spec_of(fields)
            if spur.bore_allowance_of(spec) != 0.0:
                wrong.append((name, "the default planned with the switch off"))
    ok(not wrong, f"allowance offline: the spur, helical, bevel and hub plan the hole as cut at Bore + 0.2 by default "
                  f"(switch on), at the figure typed (the spur's -0.1 among them), at the Bore machined; the global "
                  f"exactly when printed, schema 4 or 1; with the switch off the default plans 0: {wrong or 'all'}")

    # 9. The machined parts are F3-0's pins: their plans and .gear.json byte for byte as at the cut.
    pins = pinned_tests()
    wrong = [n for n, f, _ in ALLOWANCE_KINDS
             if pins.GEARS[n] != f or pins.strip_print(n, process="machined") != pins.STRIP[n]
             or pins._sha(pins.sidecar_text(n, process="machined")) != pins.SIDECARS[n]]  # noqa: SLF001
    ok(not wrong, f"pins: the four machined gears built beside the printed ones are tests/test_printed_rule.py's GEARS, "
                  f"and their plans and .gear.json hold F3-0's STRIP and SIDECARS hashes: {wrong or 'all four'}")

    # 10. The live part, read as source: every name it takes from the scripts it runs on is one they define, and every
    # Session member it calls is the app's (the live part cannot be imported off Windows).
    missing = live_names_missing()
    ok(not missing[0] and not missing[1] and missing[2] > 40,
       f"live: the {missing[2]} names the live sections take from W9a's, W8's, F2's, W9c's, W9d's and W9c's probes' "
       f"scripts are each defined there, and every Session member they call is swcom.Session's: missing "
       f"{missing[0] or 'none'}; members {missing[1] or 'all found'}")

    # 11. hub, offline: RangeBox_Fixed printed with the Hub row's D assesses with no error, plans the Hub's D and its
    # globals, and records it at schema 4.
    import importlib.util
    spec_ = importlib.util.spec_from_file_location("f3_workbook_fixtures", os.path.join(REPO, "tests",
                                                                                       "workbook_fixtures.py"))
    fixtures = importlib.util.module_from_spec(spec_)
    spec_.loader.exec_module(fixtures)
    made = fixtures.range_box_fixed()
    hub_d = dict(bore="8", bore_allowance="0.2", drive="flat", flat="7")
    box = dataclasses.replace(made, gears=tuple(dataclasses.replace(g, **hub_d) if g.id == "Hub" else g
                                                 for g in made.gears),
                              box=dataclasses.replace(made.box, process="printed"), source_path="C:\\B\\X.xlsx")
    from gear_generator.workbook import assess
    a = assess.assess(box, [], "C:\\Out\\")
    job_ = next((j for j in a.parts.jobs if "Hub" in j.gear_ids), None)
    held = {v.name: v.expression_for(DEGREES) for v in kind_for(job_.spec).variables(job_.spec, job_.derived)} \
        if job_ else {}
    ok(not [d for d in a.diagnostics if d.is_error] and job_ is not None and job_.derived.bore_flat == 7.0
       and abs(job_.derived.bore_allowance - 0.2) < 1e-12 and float(held.get(ALLOWANCE_GLOBAL, "nan")) == 0.2
       and float(held.get(FLAT_GLOBAL, "nan")) == 7.0
       and store.sidecar_schema(job_.spec.to_dict(), list(held.items())) == 4
       and made.gear("Hub").kind == "hub",
       f"hub offline: RangeBox_Fixed printed with the Hub's D assesses with no error, and the Hub plans Flat 7 at 0.2, "
       f"its two globals and schema 4: errors {[d.message for d in a.diagnostics if d.is_error]}")

    # 12. The strip's own form, through dshape's steps, a job answered here.
    _self_check_form(ok, scratch)


LIVE_FROM = {"A": "w9a_demonstration.py", "W": "workbook_assembly_check.py", "F2": "f2_demonstration.py",
             "D": "w9d_demonstration.py", "CP": "w9c_probes.py", "C9": "w9c_demonstration.py",
             "C": "w9c_demonstration.py", "B9": "w9b_demonstration.py"}


def live_names_missing():
    """(the names the live part takes from another script that the script does not define at its top level, the
    Session members it calls that swcom.Session lacks, how many names were looked up)."""
    from gear_generator import swcom
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    live = src[src.index("\n# -- the live run"):]
    tops = {}
    for alias, name in LIVE_FROM.items():
        text = open(os.path.join(HERE, name), encoding="utf-8").read()
        found = set(re.findall(r"^(?:def|class)\s+(\w+)", text, re.M))
        for targets in re.findall(r"^([A-Za-z_][\w, ]*?)\s*=(?!=)", text, re.M):
            found |= {t.strip() for t in targets.split(",") if t.strip()}
        found |= set(re.findall(r"^import\s+\S+\s+as\s+(\w+)", text, re.M))
        for imported in re.findall(r"^from\s+\S+\s+import\s+([^(#\n]+)", text, re.M):
            found |= {n.split(" as ")[-1].strip() for n in imported.split(",")}
        tops[alias] = found
    used = set(re.findall(r"(?<![\w.])(A|W|F2|D|CP|C9|C|B9)\.([A-Za-z_]\w*)", live))
    gone = sorted(f"{a}.{n}" for a, n in used if n not in tops[a])
    members = set(re.findall(r"(?<![\w.])s\.([A-Za-z_]\w*)\(", live))
    lacking = sorted(m for m in members if not hasattr(swcom.Session, m))
    return gone, lacking, len(used) + len(members)


def _self_check_form(ok, scratch):
    """The strip's own form, as dshape presses it: a D built (its record written by the form's own _write_sidecar),
    then every step through the form's own Update values, a job answered here with the globals it would change."""
    from gear_generator import swbuild
    try:
        import tkinter as tk
        root = tk.Tk()
    except Exception as exc:  # noqa: BLE001 - said: the live sections need the form, so its check is a failure
        ok(False, f"form: the strip's form cannot be made here ({type(exc).__name__}: {exc}); the live sections need "
                  "Tk, as python.exe on Windows has it")
        return
    root.withdraw()
    holder = {}

    def runner(fn):
        app = holder["app"]
        context = app._build_context or {}  # noqa: SLF001
        held = {n: norm(e) for n, e in app._loaded.record.variables}  # noqa: SLF001
        trig = "degrees"
        changed = [v.name for v in context.get("variables", ()) if held.get(v.name) != norm(v.expression_for(trig))]
        return swbuild.UpdateResult(document="DShape.SLDPRT", changed=changed, rebuilt=True, trig=trig), None, []
    strand = F2P.Strand(runner)
    try:
        app = F2P.make_form(root, strand)
        holder["app"] = app
        folder = os.path.join(scratch, "dshape")
        os.makedirs(folder)

        def record(name):
            app.gear_vars["a"]["name"].set(name)
            app._derive_now()  # noqa: SLF001
            context = app._plan_single(folder)  # noqa: SLF001
            path = context["paths"][0]
            fake = types.SimpleNamespace(saved=path, trig="degrees", features=[], dimensions={}, manual=[])
            note, sidecar, where = app._write_sidecar(context["specs"][0], context["derived"][0],  # noqa: SLF001
                                                      context["plans"][0], fake)
            app._loaded, app._loaded_path = sidecar, where  # noqa: SLF001 - as the form's _finish_single does
            with open(where, encoding="utf-8") as handle:
                return path, sidecar_schema(handle.read()), note
        form_set(app, folder, DSHAPE, name=DSHAPE_NAME)
        derived = app._derived["a"]  # noqa: SLF001
        rows = F2P.shown_rows(app)
        path, schema_, note = record(DSHAPE_NAME)
        ok(derived is not None and derived.bore_flat == 7.0 and abs(derived.bore_allowance - 0.2) < 1e-12
           and rows.get("Bore as cut") == said_bore_row(8, 0.2) and rows.get("Flat as cut") == said_flat_row(7, 0.2)
           and schema_ == 4,
           f"form: the D on the form plans Flat 7 and 0.2, shows Bore as cut {rows.get('Bore as cut')!r} and Flat as "
           f"cut {rows.get('Flat as cut')!r}; its record written by the form at schema {schema_} ({note or 'no note'})")
        snapshot = {"key": (1, "DShape.SLDPRT", path), "version": "SolidWorks 2026", "newer_than_tested": False,
                    "title": "DShape.SLDPRT", "path": path, "doc_type": 1, "is_part": True, "revision": (34, 1, 1)}
        part, wrong = dict(DSHAPE), []
        for tag, changes, how, form, after in dshape_states():
            seen = strip_press(app, strand, changes, snapshot)
            if how == "value":
                want = {GLOBAL_OF[k] for k, v in changes.items() if part.get(k) != v}
                spec = app._loaded.record.spec  # noqa: SLF001
                good = (seen["count"] == len(want) and len(seen["jobs"]) == 1
                        and set(seen["jobs"][0]["value"].changed) == want
                        and all(str(spec.get(k, "")) == v for k, v in changes.items()))
                part = dict(form)
            elif how == "bound":
                good = (seen["count"] == 0 and not seen["jobs"] and seen["status"] == SAID_NOT_WORKED
                        and said_refusal(form) in seen["errors"])
            else:
                said = SAID_ALLOWANCE if "drive" not in changes else said_drive("flat", "round")
                good = seen["count"] == 0 and not seen["jobs"] and seen["status"] == said
            if not good:
                wrong.append((tag, seen["count"], [j["value"].changed for j in seen["jobs"]], seen["status"],
                              seen["errors"]))
        ok(not wrong, f"form: through the strip's own Update values, each value step counts and sends exactly its own "
                      f"globals and the record follows; each bound step is refused by the form in A's words with "
                      f"nothing sent; each structural step in B's words with nothing sent: {wrong or 'all thirteen'}")
        form_set(app, folder, dict(DSHAPE, drive="round", flat=""), name=DSHAPE_ROUND)
        path_r, schema_r, _ = record(DSHAPE_ROUND)
        seen = strip_press(app, strand, {"drive": "flat", "flat": "7"}, dict(snapshot, path=path_r))
        ok(schema_r == 4 and app._derived["a"] is not None and not seen["jobs"]  # noqa: SLF001
           and seen["status"] == said_drive("round", "flat"),
           f"form: the round part's record at schema {schema_r}; Drive flat on it refused in B's words, nothing sent: "
           f"{seen['status']!r}")
    finally:
        root.destroy()


if SELF_CHECK:
    raise SystemExit(self_check())


# -- the live run: W9a's harness, through F2's live part ----------------------------------------------------------------

sys.path.insert(0, HERE)
import f2_demonstration as F2  # noqa: E402  (W9a's harness, and F2's form, presses, reads and judges)

A, W = F2.A, F2.W
from gear_generator import gui, store, swbuild, swcom  # noqa: E402
from gear_generator.gears import kind_for, plan_for, spur  # noqa: E402
from gear_generator.gears.equations import DEGREES, evaluate, split_equation  # noqa: E402
from gear_generator.spec import GearSpec, as_built  # noqa: E402
from gear_generator.swcom import call  # noqa: E402
from gear_generator.workbook import link as wb_link  # noqa: E402

say, check, note = W.say, W.check, W.note
OUT = W.OUT
CTX, RESULT, run, job = A.CTX, A.RESULT, A.run, A.job
WW_CLOSE_FLAG = "--close-outlived-whats-wrong"      # W9c's flag, its own path (w9c_demonstration.close_outlived_on)
GIVEN = {"off": A._arg("--reducer-off-master"), "on": A._arg("--reducer-on-master"),  # noqa: SLF001
         "machined": A._arg("--reducer-machined-master")}  # noqa: SLF001
FREE_GB = F2.PRESS_FREE_GB                          # F1's floor before a RangeBox copy and its presses


def switch_now():
    return getattr(spur, SWITCH, None)


def switch_line(where):
    v = switch_now()
    return (f"switch  {where}: spur.{SWITCH} reads {v!r} (" + ("on" if v is True else "OFF") + ": a printed gear's "
            f"blank Bore allowance on a part not yet built plans " + (f"{DEFAULT_ALLOWANCE:g} mm" if v is True else
                                                                      "0, not the default") + ")")


def require_switch(section, what):
    """A section that judges the printed default refuses with the switch off: what it would read is not F3's."""
    say(switch_line(section))
    if switch_now() is not True:
        A.section_stop(f"{section}: spur.{SWITCH} reads {switch_now()!r}, so {what} is not judged; this script is "
                       "written for the switch on, which the coordinator's last commit of F3 makes")


def switched(on, why):
    """spur's switch set in this process only, said, and put back after (F2's patched)."""
    say(f"switch  {why}")
    return F2.patched(spur, {SWITCH: on}, say=say)


def file_of(path):
    return F2P.file_of(path)


def sidecar_of(path):
    """A part's .gear.json: (its path, its text, its schemaVersion)."""
    where = store.sidecar_path(path)
    with open(where, encoding="utf-8") as handle:
        text = handle.read()
    return where, text, sidecar_schema(text)


def app_runner(what):
    """The strip's worker for Update values and Build: the job on this run's worker under W9a's watch, as an app job
    (the What's Wrong rule applying)."""
    def runner(fn):
        value, error = A.watched_wait(CTX["worker"].submit(fn), 900, what, app_job=True)
        return value, error, []
    return runner


# -- reads, without changing anything -----------------------------------------------------------------------------------


def part_faces(s):
    """Every face of the build document (W9b's part_faces, its calls): a cylinder's radius, axis and point
    (CylinderParams); a plane's normal and a point on it (PlaneParams); each face's box (GetBox), mm."""
    def got(obj, name, *args):
        value = call(obj, name, *args)
        return swcom._guarded(name, value) if type(value).__name__ == "method" else value  # noqa: SLF001
    out = []
    for body in list(call(s._doc(), "GetBodies2", 0, True) or []):  # noqa: SLF001
        for face in list(got(body, "GetFaces") or []):
            surface = got(face, "GetSurface")
            box = [float(v) * 1000.0 for v in got(face, "GetBox")]
            if got(surface, "IsCylinder"):
                p = [float(v) for v in got(surface, "CylinderParams")]
                out.append({"kind": "cylinder", "r": p[6] * 1000.0, "axis": p[3:6],
                            "point": [v * 1000.0 for v in p[0:3]], "box": box})
            elif got(surface, "IsPlane"):
                p = [float(v) for v in got(surface, "PlaneParams")]
                out.append({"kind": "plane", "normal": p[0:3], "root": [v * 1000.0 for v in p[3:6]], "box": box})
            else:
                out.append({"kind": "other", "box": box})
    return out


def part_read(label, path):
    """A part as SolidWorks holds it, read without activating it where it is open (use_open_document; opened when it
    is not): its features in error, the Bore Sketch's status, its volume, every face, the Equation Manager's
    equations and values, its save flag."""
    def work(s):
        if s.use_open_document(path) is None:
            s.open_document(path)
        out = {"in_error": [(f.name, f.code) for f in s.feature_states() if f.code]}
        try:
            out["sketch"] = s.sketch_status(SKETCH)
        except Exception as exc:  # noqa: BLE001 - a part with no Bore Sketch: said in its place
            out["sketch"] = f"unread: {type(exc).__name__}: {exc}"
        try:
            out["volume"] = s.volume_mm3()
        except Exception as exc:  # noqa: BLE001
            out["volume"] = None
        out["faces"] = part_faces(s)
        out["equations"] = [(str(t), float(v)) for t, v in s.equations()]
        out["values"] = s.equation_values()
        out["flag"] = bool(call(s._doc(), "GetSaveFlag"))  # noqa: SLF001
        return out
    return run(f"{label}: {file_of(path)} read", work, 600)


def values_of(label, path):
    """A part's equation values and save flag, read without activating it."""
    def work(s):
        if s.use_open_document(path) is None:
            return None
        return {"values": s.equation_values(), "flag": bool(call(s._doc(), "GetSaveFlag"))}  # noqa: SLF001
    return run(f"{label}: {file_of(path)}'s values", work, 300)


def flags_in(label, folder):
    """{file: GetSaveFlag} of every document SolidWorks holds under the folder, opening nothing."""
    def work(s):
        return {os.path.basename(str(call(d, "GetPathName") or "")): bool(call(d, "GetSaveFlag"))
                for d in W.documents(s._app) if W.under(str(call(d, "GetPathName") or ""), folder)}  # noqa: SLF001
    return run(f"{label}: the save flags", work, 300)


def mates_now(label, asm):
    """Every mate of the assembly as Session.mate_states reads it: {name: (code, suppressed)}."""
    got = run(f"{label}: the mates", job(asm, lambda s: {m.name: (m.code, m.suppressed) for m in s.mate_states()}))
    return got


def facts_of(got):
    """A read for the log and the JSON, its faces summed up."""
    cyl = sorted({round(f["r"], 6) for f in got.get("faces", []) if f["kind"] == "cylinder" and coaxial(f)})
    planes = [f for f in got.get("faces", []) if f["kind"] == "plane" and abs(f["normal"][2]) <= AXIS_TOL]
    return {"in_error": got.get("in_error"), "sketch": got.get("sketch"), "volume": got.get("volume"),
            "coaxial_radii": cyl[:4], "side_planes": [(round(f["root"][0], 6), [round(v, 9) for v in f["normal"]])
                                                      for f in planes][:6],
            "links": [t for t, _ in got.get("equations", []) if "@" + SKETCH in t.split("=", 1)[0]],
            "link_values": [v for t, v in got.get("equations", []) if "@" + SKETCH in t.split("=", 1)[0]],
            "globals": {k: v for k, v in got.get("values", {}).items() if k in GLOBAL_OF.values()}}


def judge_hole(label, got, fields, derived, reference=None, volume=True):
    """A part's bore as read, against the hole worked here from its fields (D, a, F): the faces (bore_judged), the
    tooth space on +X (spur kinds), the links as SolidWorks holds them (the chord and the radius for a D, the diameter
    for a round), the F3 globals, nothing in error, the Bore Sketch fully defined, and the volume against its twin."""
    D, a, F = hole_of(fields)
    cut, radius_expr, h_expr = spur.bore_expressions(derived)
    values = dict(got["values"])

    def ev(expression, scope):
        return evaluate(expression, scope, DEGREES)
    if F is not None:
        d = d_expected(D, a, F)
        problems = bore_judged(got["faces"], d["R"], d["h"])
        problems += link_judged(got["equations"], values, FLAT_DIM, spur.chord_expression(radius_expr, h_expr),
                                d["chord"], split_equation, ev)
        problems += link_judged(got["equations"], values, BORE_DIM, radius_expr, d["R"], split_equation, ev)
    else:
        problems = bore_judged(got["faces"], (D + a) / 2.0)
        problems += link_judged(got["equations"], values, BORE_DIM, cut, D + a, split_equation, ev)
    teeth = int(fields.get("teeth") or getattr(derived, "teeth", 0) or 0)
    tip = getattr(derived, "da", None)
    if tip and teeth:
        problems += lands_judged(got["faces"], tip / 2.0, teeth)
    problems += globals_judged(values, a, F)
    problems += [f"in error {got['in_error']}"] if got["in_error"] else []
    problems += [] if got["sketch"] == FULLY_DEFINED else [f"the Bore Sketch reads {got['sketch']}, not 3 (fully "
                                                           "defined)"]
    if volume:
        problems += volume_judged(got["volume"], reference)
    facts = facts_of(got)
    facts["boxes"] = bore_facts(got["faces"], (D + a) / 2.0, *((d["h"], d["chord"]) if F is not None else ()))
    if tip and teeth:
        facts["tip_lands"] = lands_facts(got["faces"], tip / 2.0, teeth)
    facts["link_value_units"] = [value_judged(v, w)[1] for (dim, w) in (
        (FLAT_DIM, d["chord"] if F is not None else None), (BORE_DIM, d["R"] if F is not None else D + a))
        for t, v in got["equations"] if w is not None and t.split("=", 1)[0].strip().strip('"') == dim]
    say(f"fact    {label}: {facts}; its twin's volume {reference}")
    check(not problems, f"{label}: D {fmt(D)}, a {fmt(a)}, " + (f"Flat {fmt(F)}" if F is not None else "round")
          + ": nothing in error, the Bore Sketch fully defined, the bore by its faces"
          + (" (the round of R about the axis reaching -X, one flat at h on +X, the tip lands counted)"
             if F is not None else " (round, no flat)") + ", the links as SolidWorks holds them and its Values, the globals"
          + (", the volume within 0.1 % of its twin" if volume else "") + f": {problems or 'as said'}")
    return {"facts": facts, "problems": problems}


# -- the strip's form, built as a person builds a gear ----------------------------------------------------------------


def form_build_now(label, app, folder):
    """The gear set on the form built by the form's own plan, job (on this run's worker) and finish (its .gear.json,
    which it then holds open); the part made active, as the form leaves it. (spec, derived, path, result)."""
    app._derive_now()  # noqa: SLF001
    spec, derived = app._held_spec("a"), app._derived["a"]  # noqa: SLF001
    context = app._plan_single(folder)  # noqa: SLF001
    path = context["paths"][0]
    check(derived is not None and not os.path.exists(path), f"{label}: the form plans {file_of(path)}, a new file")
    result = run(f"{label}: built", context.pop("job"), 900)
    for line in result.log_lines():
        say("        " + line)
    app._finish_single(context, result)  # noqa: SLF001 - the form's own finish: the status and the .gear.json
    say(f"status  {label}: {app.status.get()}")
    check(result.ok and bool(result.saved) and os.path.isfile(store.sidecar_path(path)) and not undefined(result.checks),
          f"{label}: built and saved by the form's job, every sketch fully defined, its .gear.json written by the form: "
          f"ok {result.ok}, failures {list(result.failures)}, not fully defined {undefined(result.checks) or 'none'}")
    F2.activate(label, path)
    return spec, derived, path, result


def twin(label, spec, folder, cache):
    """The same gear built from scratch by the app's plan and build into a folder of its own, its volume read, then
    closed unsaved; once per spec (its name aside). None when it does not build clean."""
    key = json.dumps(dataclasses.replace(spec, name="", built_allowance="").to_dict(), sort_keys=True)
    if key in cache:
        return cache[key]
    n = len(cache) + 1
    where = os.path.join(folder, f"twin-{n}")
    os.makedirs(where)
    spec_n = dataclasses.replace(spec, name=f"Twin{n}")
    kind = kind_for(spec_n)
    path = os.path.join(where, spec_n.stem() + ".SLDPRT")
    plan = plan_for(spec_n, kind.derive(spec_n), "", path)

    def build(s):
        r = swbuild.build(s, plan)
        return r, ({"volume": s.volume_mm3(), "in_error": [(f.name, f.code) for f in s.feature_states() if f.code]}
                   if r.ok else None)
    try:
        result, state = run(f"{label}: twin {n} built from scratch", build, 900)
    finally:
        left = run(f"{label}: twin {n} closed", W.quit_in(where))
    clean = result.ok and state is not None and not state["in_error"] and not undefined(result.checks)
    say(f"fact    {label}: twin {n} ({spec_n.stem()}): built ok {result.ok}, failures {list(result.failures)}, "
        f"not fully defined {undefined(result.checks) or 'none'}, {state}; left open {left}")
    check(clean and not left, f"{label}: twin {n} built from scratch clean and closed")
    cache[key] = state["volume"] if clean else None
    return cache[key]


# -- dshape -------------------------------------------------------------------------------------------------------------


def section_dshape(out):
    say("== dshape  the D's Updates measured first (S6): a printed spur with a D bore built by the strip's form, then "
        "Flat, Bore and Bore allowance changed by the form's own Update values across their range, to and past each "
        "bound, back, and to a press fit; the allowance to 0 and Drive to round refused; then D to round and back, "
        "each made new by the form's Build; every state read by its faces, its links, its globals and its volume "
        "against the same gear built from scratch")
    say(switch_line("dshape (typed figures only: judged whatever it reads)"))
    folder = W.fresh_folder("dshape")
    twins = os.path.join(folder, "twins")
    os.makedirs(twins)
    cache = {}
    root, strand = F2.tk_root(), F2.Strand(app_runner("the strip's job"))
    steps = out.setdefault("steps", {})
    try:
        app = F2.make_form(root, strand)
        form_set(app, folder, DSHAPE, name=DSHAPE_NAME)
        rows = F2.shown_rows(app)
        check(rows.get("Bore as cut") == said_bore_row(8, 0.2) and rows.get("Flat as cut") == said_flat_row(7, 0.2),
              f"dshape: the form shows Bore as cut {rows.get('Bore as cut')!r} and Flat as cut "
              f"{rows.get('Flat as cut')!r}")
        spec, derived, path, _ = form_build_now("dshape: DShape", app, folder)
        where, text, schema_ = sidecar_of(path)
        check(schema_ == 4, f"dshape: DShape's .gear.json at schema {schema_} (4: it holds the bore's globals)")
        part = dict(DSHAPE)
        steps["as built"] = judge_hole("dshape: as built", part_read("dshape: as built", path), part, derived,
                                       twin("dshape: as built", spec, twins, cache))
        for tag, changes, how, form, after in dshape_states():
            label = f"dshape, {tag}"
            say(f"-- {label} ({how})")
            F2.activate(label, path)
            before = values_of(label, path)
            sc_before = F2.sha(where)
            snapshot = run(f"{label}: the strip's bar reads SolidWorks", gui._read_snapshot)  # noqa: SLF001
            seen = strip_press(app, strand, changes, snapshot)
            say(f"status  {label}: {seen['status']}")
            if how == "value":
                want = {GLOBAL_OF[k] for k, v in changes.items() if part.get(k) != v}
                j = seen["jobs"][-1] if seen["jobs"] else None
                result = j["value"] if j else None
                record = dict(app._loaded.record.spec)  # noqa: SLF001
                check(seen["count"] == len(want) and j is not None and j["error"] is None and result is not None
                      and result.ok and result.rebuilt and set(result.changed) == want and not result.by_way_of
                      and all(str(record.get(k, "")) == v for k, v in changes.items()),
                      f"{label}: the strip counted {seen['count']} and Update values set {sorted(want)} in one rebuild, "
                      f"its record following: changed {list(result.changed) if result else None}, failures "
                      f"{list(result.failures) if result else (j and j['error'])}")
                part = dict(form)
                state = app._held_spec("a")  # noqa: SLF001
                steps[tag] = judge_hole(label, part_read(label, path), part, app._derived["a"],  # noqa: SLF001
                                        twin(label, state, twins, cache))
                continue
            after_values = values_of(label, path)
            unchanged = (before is not None and after_values is not None and before["values"] == after_values["values"]
                         and F2.sha(where) == sc_before)
            if how == "bound":
                said = said_refusal(form)
                check(said in seen["errors"] and app._derived["a"] is None and seen["count"] == 0  # noqa: SLF001
                      and not seen["jobs"] and seen["status"] == SAID_NOT_WORKED and unchanged,
                      f"{label}: refused by the form at Flat in A's words ({said!r}), Update values saying "
                      f"{SAID_NOT_WORKED!r}, nothing sent, the part's globals and record as they were: errors "
                      f"{seen['errors']}")
            else:
                said = SAID_ALLOWANCE if "drive" not in changes else said_drive("flat", "round")
                check(seen["status"] == said and seen["count"] == 0 and not seen["jobs"] and unchanged,
                      f"{label}: refused by Update values in B's words ({said!r}), nothing sent, the part's globals and "
                      f"record as they were")
            steps[tag] = {"refused": seen["status"], "errors": seen["errors"]}
        say("-- dshape  from D to round and back: Drive is structural, so each is made new by the form's Build with the "
            "record open (the ruling on decision 11 keeps nothing here: the allowance is typed)")
        round_fields = dict(DSHAPE, drive="round", flat="")
        form_set(app, folder, round_fields, name=DSHAPE_ROUND)
        spec_r, derived_r, path_r, _ = form_build_now("dshape: DShape_Round", app, folder)
        steps["round"] = judge_hole("dshape: round", part_read("dshape: round", path_r), round_fields, derived_r,
                                    twin("dshape: round", spec_r, twins, cache))
        snapshot = run("dshape: the strip's bar reads SolidWorks", gui._read_snapshot)  # noqa: SLF001
        seen = strip_press(app, strand, {"drive": "flat", "flat": "7"}, snapshot)
        check(seen["status"] == said_drive("round", "flat") and not seen["jobs"] and seen["count"] == 0,
              f"dshape: Drive flat on the round part refused by Update values in B's words, nothing sent: "
              f"{seen['status']!r}")
        app.gear_vars["a"]["name"].set(DSHAPE_AGAIN)
        spec_d, derived_d, path_d, _ = form_build_now("dshape: DShape_D", app, folder)
        steps["round to D"] = judge_hole("dshape: round to D", part_read("dshape: round to D", path_d), dict(DSHAPE),
                                         derived_d, twin("dshape: round to D", spec_d, twins, cache))
        out["twins"] = len(cache)
    finally:
        root.destroy()
        left = run("dshape: closed", W.quit_in(folder))
        check(not left, f"dshape: its documents closed unsaved: left {left}")


# -- allowance ----------------------------------------------------------------------------------------------------------


def section_allowance(out):
    say("== allowance  a printed spur, helical and bevel gear and a hub, each built with the default allowance and "
        "with one typed, and machined beside: the hole as cut by its faces, the global as SolidWorks holds it, the "
        ".gear.json's schema; the machined parts as F3-0's pins hold them")
    require_switch("allowance", "the printed default's hole")
    folder = W.fresh_folder("allowance")
    pins = pinned_tests()
    root = F2.tk_root()
    try:
        app = F2.make_form(root, F2.Strand(app_runner("the strip's job")))
        for name, fields, typed in ALLOWANCE_KINDS:
            for how, process, allowance, want_a in (("default", "printed", "", DEFAULT_ALLOWANCE),
                                                    ("typed", "printed", typed, float(typed)),
                                                    ("machined", "machined", "", 0.0)):
                label = f"allowance, {name} {how}"
                where = os.path.join(folder, f"{name}-{how}")
                os.makedirs(where)
                spec = GearSpec(**{**fields, "process": process, "bore_allowance": allowance})
                kind = kind_for(spec)
                derived = kind.derive(spec)
                errors = [d.message for d in kind.validate(spec) if d.is_error]
                path = os.path.join(where, spec.stem() + ".SLDPRT")
                plan = plan_for(spec, derived, "", path)

                def build(s, plan=plan):
                    r = swbuild.build(s, plan)
                    if not r.ok:
                        return r, None
                    return r, {"faces": part_faces(s), "values": s.equation_values(),
                               "in_error": [(f.name, f.code) for f in s.feature_states() if f.code]}
                try:
                    result, state = run(f"{label}: built", build, 900)
                    note_, sidecar, sc = (app._write_sidecar(spec, derived, plan, result) if result.saved  # noqa: SLF001
                                          else ("not saved", None, ""))
                finally:
                    left = run(f"{label}: closed", W.quit_in(where))
                D = float(spec.bore)
                R = (D + want_a) / 2.0
                hole = hole_radius(state["faces"], R + 1.0) if state else None
                values = state["values"] if state else {}
                text = open(sc, encoding="utf-8").read() if sc and os.path.isfile(sc) else ""
                problems = list(errors) + ([] if result.ok and state and not state["in_error"] else
                                           [f"built ok {result.ok}, failures {list(result.failures)}, in error "
                                            f"{state and state['in_error']}"])
                problems += undefined(result.checks)
                problems += [] if hole is not None and abs(hole - R) <= RADIUS_TOL else [f"the hole reads {hole}, not "
                                                                                        f"{R:.6f}"]
                problems += bore_judged(state["faces"], R) if state else []
                problems += globals_judged(values, want_a, None)
                problems += [] if sidecar_schema(text) == (4 if want_a else 1) else [
                    f"the .gear.json at schema {sidecar_schema(text)}, not {4 if want_a else 1} ({note_ or 'no note'})"]
                if how == "machined":
                    built = store.from_json(text).record if text else None
                    pinned = store.from_json(pins.sidecar_text(name, process="machined")).record
                    same = built is not None and result.trig == DEGREES and (
                        built.spec, built.derived, built.variables) == (pinned.spec, pinned.derived, pinned.variables)
                    problems += [] if same else ["its record's spec, derived and globals are not F3-0's pin's "
                                                 f"(trig {result.trig})"]
                say(f"fact    {label}: {file_of(path)}: the hole by its faces {hole}; the F3 globals "
                    f"{ {k: v for k, v in values.items() if k in (ALLOWANCE_GLOBAL, FLAT_GLOBAL)} }; schema "
                    f"{sidecar_schema(text)}; left open {left}")
                check(not problems and not left,
                      f"{label}: the hole as cut {fmt(D)} + {fmt(want_a)}, radius {R:.4f} to {RADIUS_TOL:g} by its "
                      f"faces, " + (f'"{ALLOWANCE_GLOBAL}" {fmt(want_a)} in SolidWorks, schema 4' if want_a else
                                    "no F3 global, schema 1, its record F3-0's pin") + f": {problems or 'as said'}")
                out[f"{name} {how}"] = {"hole": hole, "schema": sidecar_schema(text), "problems": problems}
    finally:
        root.destroy()


# -- print --------------------------------------------------------------------------------------------------------------


def section_print(out):
    say("== print  Print files on the strip's form: a printed D with its allowance typed, and a printed round bore at "
        "the default; each press judged whole by F2's judges, the bore read from the STEP file, the list's bore line")
    require_switch("print", "the round part's default allowance in its file and its list")
    F2.require_findings("print")
    folder = W.fresh_folder("print")
    root, strand = F2.tk_root(), F2.Strand(F2.press_runner)
    try:
        app = F2.make_form(root, strand)
        for tag, fields, name, a, flat in (("D", PRINT_D, "Print_D", 0.2, 7.0),
                                           ("round", PRINT_ROUND, "Print_R", DEFAULT_ALLOWANCE, None)):
            label = f"print, {tag}"
            form_set(app, folder, fields, name=name)
            _, derived, path, _ = form_build_now(label, app, folder)
            span = F2.span_on_form(label, app, dict(fields))
            expect = {name: {"radius": F2P.outer_radius(1.5, 20), "face": 8.0, "extent": F2.extent_want(), "rows": (),
                             "count": 1, "span": span}}
            before = F2.snap_all(label, (folder,))
            seen = F2.press_form(app, strand, label)
            after = F2.snap_all(label, (folder,))
            got = F2.written(label, seen, folder, expect, before[0], after[0], (before[1], after[1]),
                             (before[2], after[2]), name=name, calls={"SaveAs": 1, "GetOpenDocumentByName": None})
            if got is None:
                continue
            text = F2.read_text(os.path.join(got["where"], name + ".step"))
            D = 8.0
            if flat is not None:
                d = d_expected(D, a, flat)
                problems = step_bore_judged(text, d["R"], d["h"])
            else:
                problems = step_bore_judged(text, (D + a) / 2.0)
            faces = step_faces(text)
            say(f"fact    {label}: the STEP file's faces: {len(faces)}, of them planes "
                f"{sum(1 for f in faces if f[0] == 'plane')} and cylinders {sum(1 for f in faces if f[0] == 'cylinder')}")
            check(not problems, f"{label}: the bore read from the STEP file itself: one cylinder of radius "
                                f"{(D + a) / 2.0:.4f} about Z" + (", one plane on x = h, the flat's corners at x = h"
                                                                  if flat is not None else ", no plane")
                                + f", the least vertex radius the hole's, to {STEP_TOL:g} mm: {problems or 'as said'}")
            block = F2P.list_blocks(got["list"]).get(name + ".step", [])
            line = said_print_bore("8", a, flat)
            check(any(f" {DOT} {line} {DOT} " in x for x in block),
                  f"{label}: the print list's bore line says {line!r}: {[x for x in block if 'bore' in x]}")
            out[tag] = {"folder": got["folder"], "problems": problems}
    finally:
        root.destroy()
        left = run("print: closed", W.quit_in(folder))
        check(not left, f"print: its documents closed unsaved: left {left}")


# -- built --------------------------------------------------------------------------------------------------------------


def reducer_master(which):
    """The 12 : 1 built once through the app's own Build (W8's write_fixture and build_turning): printed with the switch
    off ("off": F2's code) or on ("on": F3's), or machined with it off ("machined": a gearbox built before F3), kept as
    f3-reducer-<which>.master, or given by --reducer-<which>-master."""
    if GIVEN[which]:
        return GIVEN[which]
    name = f"f3-reducer-{which}"
    here = os.path.join(OUT, name + W.MASTER_SUFFIX)
    if os.path.isdir(here):
        say(f"fact    the printed 12 : 1 kept earlier in this <out> is copied: {os.path.basename(here)}")
        return here
    if os.path.exists(os.path.join(OUT, name)):
        raise AssertionError(f"an earlier build of {name} in this <out> kept no master; give --reducer-{which}-master "
                             "or a fresh <out>")
    made = wb_link.Link(W.FIXTURE_12).read().spec
    why = {"off": "in this process only, so the printed 12 : 1 is built as F2's code built it: a blank allowance plans "
                  "none",
           "on": "on, as committed after F3: a blank allowance plans the default",
           "machined": "in this process only: the machined 12 : 1 built as before F3 (a machined blank plans none "
                       "either way)"}[which]
    printed = which != "machined"
    with switched(which == "on", f"{name}: {why}"):
        # The machined one says Machined on its Box: the fixture's Process is blank, and a blank Process on a workbook
        # with no record beside it reads back Printed (F1, PLAN-PRINTED §2.8 item 5; model.to_sheets writes the word as
        # held), so W9a's spec_reducer planned the four parts printed on SolidWorks 2026's first run.
        folder, _, _, wdesk = A.w8_step(W.write_fixture, CTX["worker"], CTX["excel"], name,
                                        (lambda f: F2P.spec_printed_reducer(made, f)) if printed else
                                        (lambda f: dataclasses.replace(made, box=dataclasses.replace(
                                            made.box, output_folder=f, process="machined"))))
        try:
            jobs = {j.gear_ids[0]: j.spec.process for j in wdesk.a.parts.jobs}
            check(sorted(jobs) == sorted(REDUCER) and all(p == ("printed" if printed else "machined")
                                                         for p in jobs.values()),
                  f"{name}: the four parts plan {'printed' if printed else 'machined'}: {jobs}")
            built = A.w8_step(W.build_turning, CTX["worker"], wdesk, name, 4)
            result = built[1] if isinstance(built, tuple) and len(built) == 2 else None
            check(result is not None and not gearbox_undefined(result),
                  f"{name}: every part's sketches fully defined: {gearbox_undefined(result) if result else 'no result'}")
        except (AssertionError, W.Halt):
            A.w8_step(W.end_copy, CTX["worker"], folder, name)
            raise
    kept = A.w8_step(W.keep_master, CTX["worker"], folder, name)
    if not kept:
        raise AssertionError(f"{name} was not kept as a master")
    return kept


def record_parts(path):
    """The link record's parts as written: {file: (spec, variables)}."""
    with open(store.link_record_path(path), encoding="utf-8") as handle:
        raw = json.load(handle)
    return {os.path.basename(p.get("path", "")): (p.get("spec"), p.get("variables")) for p in raw.get("parts", [])}


def gear_parts(desk):
    """The record's current parts by gear: {gear: path}."""
    box = desk.record.gearbox
    return {c.gear: c.part for c in box.components if c.gear in REDUCER}


def section_built(out):
    say("== built  nothing built before F3 moves: a printed coupon and the printed 12 : 1 built with the switch off "
        "(F2's code) and read with it on; an allowance typed on each refused as structural; then the printed 12 : 1 "
        "built with the switch on: G2's allowance in place by one Update, and K11 when it is changed by hand")
    require_switch("built", "a part built before F3 read with the default in")
    folder = W.fresh_folder("built")
    root, strand = F2.tk_root(), F2.Strand(app_runner("the strip's job"))
    try:
        app = F2.make_form(root, strand)
        with switched(False, "built: the coupon built as F2's code built it, in this process only"):
            form_set(app, folder, COUPON, name="Coupon_F2")
            _, _, path, _ = form_build_now("built: Coupon_F2", app, folder)
        where, text, schema_ = sidecar_of(path)
        held = dict((str(n), str(v)) for n, v in store.from_json(text).record.variables)
        check(schema_ == 3 and ALLOWANCE_GLOBAL not in held and FLAT_GLOBAL not in held,
              f"built: Coupon_F2's .gear.json at schema {schema_} with no F3 global, as F2 wrote one")
        say(switch_line("built, the coupon opened"))
        prints = (F2.sw_files(folder), F2.sha(where))
        app._load_record(where)  # noqa: SLF001 - the strip's Open .gear.json
        snapshot = run("built: the strip's bar reads SolidWorks", gui._read_snapshot)  # noqa: SLF001
        app._snapshot = snapshot  # noqa: SLF001
        app._derive_now()  # noqa: SLF001
        rows = F2.shown_rows(app)
        count = app._update_target()[0]  # noqa: SLF001
        held_a = app._derived["a"].bore_allowance if app._derived["a"] is not None else None  # noqa: SLF001
        check(count == 0 and rows.get("Bore as cut") == said_bore_row(8, 0) and held_a == 0.0,
              f"built: Coupon_F2 opened with the switch on reads as built: Update values counts {count}, Bore as cut "
              f"{rows.get('Bore as cut')!r}, the hole planned with {held_a} allowance")
        flags = flags_in("built, before the quiet Update values", folder)
        seen = strip_press(app, strand, {}, snapshot)
        r = seen["jobs"][-1]["value"] if seen["jobs"] else None
        files_now, record_now, flags_now = F2.sw_files(folder), F2.sha(where), flags_in("built, after", folder)
        # Each part of the judgement said apart (SolidWorks 2026's first run failed it with none of them shown).
        moved = {k: (prints[0].get(k), files_now.get(k)) for k in set(prints[0]) | set(files_now)
                 if prints[0].get(k) != files_now.get(k)}
        check(r is not None and r.ok and not r.changed and files_now == prints[0] and record_now == prints[1]
              and flags_now == flags,
              f"built: a quiet Update values on Coupon_F2 writes nothing: changed {r and list(r.changed)}, no file or "
              f"record written, no save flag turned: {seen['status']!r}; jobs {len(seen['jobs'])}, ok "
              f"{r is not None and r.ok}; SolidWorks files moved {moved or 'none'}; the .gear.json "
              f"{'the same' if record_now == prints[1] else 'changed'}; save flags {flags} before, {flags_now} after")
        seen = strip_press(app, strand, {"bore_allowance": TYPED_G2}, snapshot)
        check(seen["status"] == SAID_ALLOWANCE and not seen["jobs"] and seen["count"] == 0
              and F2.sha(where) == prints[1],
              f"built: an allowance typed on Coupon_F2 is refused by Update values in B's words, nothing sent: "
              f"{seen['status']!r}")
        app.gear_vars["a"]["bore_allowance"].set("")
    finally:
        root.destroy()
        left = run("built: the coupon closed", W.quit_in(folder))
        check(not left, f"built: the coupon closed unsaved: left {left}")

    say("-- built  the printed 12 : 1 built by F2's code, read with the switch on")
    copy, path, book, desk = A.copy_desk(reducer_master("off"), "built-f2", REDUCER_BOOK)
    try:
        asm = desk.record.gearbox.assembly
        parts = gear_parts(desk)
        cars = {g: sidecar_of(p) for g, p in parts.items()}
        bare = {g: (s, ALLOWANCE_GLOBAL in t) for g, (_, t, s) in cars.items()}
        check(sorted(parts) == sorted(REDUCER) and all(s == 3 and not has for s, has in bare.values()),
              f"built-f2: the four parts' .gear.json at schema 3 with no F3 global, as F2 wrote them: {bare}")
        with switched(False, "built-f2: the footer read as F2's code reads it, in this process only"):
            desk.plan_solidworks()
            footer_off = desk.footer().text
        desk.plan_solidworks()
        f = desk.say_footer("built-f2, the switch on")
        u = desk.update
        check(u is not None and u.record_matches and not u.needs_new_revision and f.text == footer_off,
              f"built-f2: with the switch on Update plans nothing and the footer is word for word as with it off: "
              f"{f.text!r}")
        F2.open_assembly("built-f2: the assembly opened", asm)
        before = (F2.sw_files(copy), {g: F2.sha(w) for g, (w, _, _) in cars.items()}, record_parts(path))
        result, _ = A.press(desk, "built-f2: the quiet Update")
        flags = flags_in("built-f2, after the quiet Update", copy)
        after = (F2.sw_files(copy), {g: F2.sha(w) for g, (w, _, _) in cars.items()}, record_parts(path))
        marks = W.marked(flags)
        expected = W.expected_marks(result, asm) if result is not None else None
        check(result is not None and result.changed == [] and result.placed == [] and before == after
              and marks == expected,
              f"built-f2: the quiet Update writes nothing: changed {result and result.changed}, placed "
              f"{result and result.placed}; every file, .gear.json and the record's parts as they were; marked "
              f"{marks} (the Update's own rebuild: {expected})")
        ref = W.cell(book, "Gears", HEADS["bore_allowance"], "G2")
        W.edit(desk, book, ("Gears", ref, float(TYPED_G2)))
        u = desk.update
        f = desk.say_footer("built-f2, G2's allowance typed")
        g2 = file_of(parts["G2"]).rsplit(".", 1)[0]
        said = list(u.structural) if u is not None else []
        # The plan lists a part whose change is structural among its changed parts (workbook/update.py's _part makes
        # every part's PartUpdate changed=True and returns the sentence beside it), so G2's part is the one changed
        # part here, not none (SolidWorks 2026's first run read ['Gear_m1.5_N68_P.SLDPRT'] with the sentence).
        changing = [file_of(p.path) for p in (u.changed_parts if u else [])]
        check(u is not None and u.needs_new_revision and len(said) == 1 and g2 in said[0] and SAID_ALLOWANCE in said[0]
              and changing == [file_of(parts["G2"])] and f.build_action == F2.ui_text.BUILD_AGAIN,
              f"built-f2: an allowance typed on G2 (built before F3, no global) is structural (G4): Update would make "
              f"G2's part new, naming it alone, and the window offers Build again...: {said}; changed parts {changing}; "
              f"the footer's action {f.build_action!r}")
        W.edit(desk, book, ("Gears", ref, None))
        check(desk.update is not None and desk.update.record_matches and F2.sw_files(copy) == before[0],
              "built-f2: the allowance cleared, Update plans nothing again; nothing was written")
    finally:
        if not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], copy, "built-f2", save=False)

    say("-- built  the printed 12 : 1 built with the switch on: G2's allowance changed in place by one Update; K11")
    copy, path, book, desk = A.copy_desk(reducer_master("on"), "built-f3", REDUCER_BOOK)
    try:
        asm = desk.record.gearbox.assembly
        parts = gear_parts(desk)
        entries = {e.path: dict((str(n), str(v)) for n, v in e.variables) for e in desk.record.current_parts()}
        check(all(entries.get(p, {}).get(ALLOWANCE_GLOBAL) == "0.2" for p in parts.values()),
              f"built-f3: every part built with the default holds \"{ALLOWANCE_GLOBAL}\" 0.2 on record")
        ref = W.cell(book, "Gears", HEADS["bore_allowance"], "G2")
        cell = "Gears!" + ref
        W.edit(desk, book, ("Gears", ref, float(TYPED_G2)))
        u = desk.update
        changing = [p.path for p in (u.changed_parts if u else [])]
        check(u is not None and not u.needs_new_revision and len(changing) == 1
              and store.same_path(changing[0], parts["G2"]),
              f"built-f3: G2's allowance typed {TYPED_G2} is a value: Update changes G2's part alone: "
              f"{[file_of(p) for p in changing]}")
        F2.open_assembly("built-f3: the assembly opened", asm)
        others = {g: run(f"built-f3: {g}'s globals", lambda s, p=p: W.live_globals(s, p))
                  for g, p in parts.items() if g != "G2"}
        files = F2.sw_files(copy)
        result, _ = A.press(desk, "built-f3: G2's allowance, one Update")
        D = float(desk.reading.spec.gear("G2").bore or 0)
        got = part_read("built-f3: G2 after the Update", parts["G2"])
        hole = hole_radius(got["faces"], (D + float(TYPED_G2)) / 2.0 + 1.0)
        after = {g: run(f"built-f3: {g}'s globals after", lambda s, p=p: W.live_globals(s, p))
                 for g, p in parts.items() if g != "G2"}
        entry = next(e for e in desk.record.current_parts() if store.same_path(e.path, parts["G2"]))
        recorded = dict((str(n), str(v)) for n, v in entry.variables).get(ALLOWANCE_GLOBAL)
        check(result is not None and [file_of(p) for p in result.changed] == [file_of(parts["G2"])]
              and hole is not None and abs(hole - (D + float(TYPED_G2)) / 2.0) <= RADIUS_TOL
              and abs(float(got["values"].get(ALLOWANCE_GLOBAL, "nan")) - float(TYPED_G2)) <= 1e-9
              and after == others and F2.sw_files(copy) == files and recorded == TYPED_G2,
              f"built-f3: G2's bore changed in place to {fmt(D)} + {TYPED_G2} (its hole by its faces {hole}), "
              f"\"{ALLOWANCE_GLOBAL}\" {got['values'].get(ALLOWANCE_GLOBAL)} in SolidWorks and {recorded} on record; "
              f"the Update changed {result and [file_of(p) for p in result.changed]}, the other parts' globals as they "
              f"were, nothing saved")
        say("-- built  K11: G2's allowance set by hand in SolidWorks, saved by the person; Update pressed again")
        run(f"built-f3: G2's \"{ALLOWANCE_GLOBAL}\" {K11_LIVE} by hand",
            job(parts["G2"], lambda s: (s.set_global_variable(ALLOWANCE_GLOBAL, K11_LIVE), bool(s.rebuild()))))
        run("built-f3: the assembly rebuilt, as the person would", job(asm, lambda s: bool(
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN))))
        A.save_user(copy, "K11: the person's change saved")
        desk.plan_solidworks()
        before_k11 = run("built-f3: G2's globals", lambda s: W.live_globals(s, parts["G2"]))
        result, _ = A.press(desk, "built-f3: K11")
        error = desk.error
        values = [v for p in getattr(error, "problems", ()) for v in p.values]
        after_k11 = run("built-f3: G2's globals after", lambda s: W.live_globals(s, parts["G2"]))
        for p in getattr(error, "problems", ()):
            say(f"        {p.kind}: {p.sentence}")
        check(result is None and isinstance(error, swbuild.UserWorkRefused)
              and any(v.name == ALLOWANCE_GLOBAL and v.cell == cell and float(v.live) == float(K11_LIVE) for v in values)
              and after_k11 == before_k11,
              f"built-f3: the Update stops and names \"{ALLOWANCE_GLOBAL}\" with its cell {cell} (K11), nothing "
              f"written: {[(v.name, v.live, v.wanted, v.cell) for v in values]}")
        out["k11"] = [p.sentence for p in getattr(error, "problems", ())]
    finally:
        if not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], copy, "built-f3", save=False)


    say("-- built  a machined 12 : 1 built before F3, Printed typed and one Update (guard 4, live): Backlash written, no "
        "\"Bore Allowance\" added")
    copy, path, book, desk = A.copy_desk(reducer_master("machined"), "built-machined", REDUCER_BOOK)
    try:
        asm = desk.record.gearbox.assembly
        parts = gear_parts(desk)
        before = {g: run(f"built-machined: {g}'s globals", lambda s, p=p: W.live_globals(s, p)) for g, p in parts.items()}
        found, empty = F2.box_process_row(book)
        row = found or empty
        W.edit(desk, book, *(([] if found else [("Box", f"A{row}", "Process")]) + [("Box", f"B{row}", "Printed")]))
        u = desk.update
        check(desk.a.spec.box.process == "printed" and u is not None and not u.needs_new_revision
              and len(u.changed_parts) == len(parts),
              f"built-machined: Printed typed: Update changes the {len(parts)} parts in place, none made new: "
              f"{[file_of(p.path) for p in (u.changed_parts if u else [])]}")
        F2.open_assembly("built-machined: the assembly opened", asm)
        result, _ = A.press(desk, "built-machined: Printed, one Update")
        after = {g: run(f"built-machined: {g}'s globals after", lambda s, p=p: W.live_globals(s, p))
                 for g, p in parts.items()}
        moved = {g: (before[g].get(spur.BACKLASH), after[g].get(spur.BACKLASH)) for g in parts}
        added = {g: sorted(n for n in (ALLOWANCE_GLOBAL, FLAT_GLOBAL) if n in after[g]) for g in parts}
        on_record = {file_of(e.path): sorted(str(n) for n, _ in e.variables if str(n) in (ALLOWANCE_GLOBAL, FLAT_GLOBAL))
                     for e in desk.record.current_parts()}
        schemas = {g: sidecar_of(p)[2] for g, p in parts.items()}
        check(result is not None and result.ok and all(b is not None and a is not None and abs(a - b) > 1e-9
                                                       for b, a in moved.values())
              and not any(added.values()) and not any(on_record.values())
              and all(s is not None and s < 4 for s in schemas.values()),
              f"built-machined: the Update wrote each part's Backlash ({moved}) and no F3 global, in SolidWorks "
              f"({added}) or on record ({on_record}); each .gear.json below schema 4 ({schemas})")
    finally:
        if not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], copy, "built-machined", save=False)


# -- hub ----------------------------------------------------------------------------------------------------------------


HUB_D = dict(bore="8", bore_allowance="0.2", drive="flat", flat="7")   # the Hub row's bore; RangeSlv, its mate, takes none


def spec_hub(folder=""):
    """RangeBox_Fixed (W9b's fixture with the hub, tests/workbook_fixtures.py) with Printed on its Box and the Hub row
    given a D bore and an allowance; its mate RangeSlv is a sleeve, which takes no bore field (G9), so no other row."""
    made = W.w8_fixtures().range_box_fixed()
    gears = tuple(dataclasses.replace(g, **HUB_D) if g.id == "Hub" else g for g in made.gears)
    return dataclasses.replace(made, gears=gears, box=dataclasses.replace(made.box, output_folder=folder,
                                                                          process="printed"))


def section_hub(out):
    say("== hub  RangeBox_Fixed printed, its Hub row with Bore 8, allowance 0.2, Drive flat and Flat 7, written by the "
        "app's write_new and built by the app's own Build; turned through every mode as W9b's build section turns it, "
        "no interference; the Hub's hole as cut read")
    say(switch_line("hub (typed figures only: judged whatever it reads)"))
    import w9b_demonstration as B9   # noqa: PLC0415 - W9b's per-mode read and judgement
    folder, path, book, desk = A.w8_step(W.write_fixture, CTX["worker"], CTX["excel"], "hub", spec_hub)
    try:
        hub_row = desk.reading.spec.gear("Hub")
        errors = B9.errors_of(desk.a)
        check(not errors and desk.a.spec.box.process == "printed"
              and (hub_row.bore_allowance, hub_row.drive, hub_row.flat) == ("0.2", "flat", "7"),
              f"hub: the workbook reads Printed and the Hub row's D, with no error: {errors}")
        plan, result = A.w8_step(W.build_turning, CTX["worker"], desk, "hub", None, None)
        check(result.ok and not result.clashes and not result.interference_error and not gearbox_undefined(result),
              f"hub: the Build ended ok, every sketch fully defined, no interference: clashes {result.clashes}, "
              f"{gearbox_undefined(result) or ''}")
        B9.hub_mates("hub", desk, plan)
        globals_ = B9.part_globals(desk, ("RangeSlv", "HighDog", "LowDog", "Hub"))
        every = B9.mode_read("hub", desk)
        out["clean"] = B9.judge_every("hub", desk, every, globals_, against_section3=False, out=out)
        out["interferences"] = every["interferences"]
        check(all(not v for v in every["interferences"].values()) and len(every["interferences"]) == len(desk.record.gearbox.modes),
              f"hub: no interference read in any of the {len(every['interferences'])} modes: {every['interferences']}")
        box = desk.record.gearbox
        hub = next(c.part for c in box.components if c.gear == "Hub")
        entry = next(e for e in desk.record.current_parts() if store.same_path(e.path, hub))
        spec = as_built(GearSpec.from_dict(dict(entry.spec)), entry.variables)
        derived = kind_for(spec).derive(spec)
        out["hub_hole"] = judge_hole("hub: the Hub's hole", part_read("hub: the Hub", hub),
                                     dict(HUB_D, teeth=spec.teeth), derived, volume=False)
        check(sidecar_of(hub)[2] == 4, f"hub: the Hub's .gear.json at schema {sidecar_of(hub)[2]} (4)")
    finally:
        if not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], folder, "hub", save=False)


# -- userwork -----------------------------------------------------------------------------------------------------------


def ensure_bore_headers(book, label):
    """A workbook written before F3 has no Bore allowance, Drive or Flat column: a person inserts the three just
    before Part name, where the app's write_new puts them, heads them as it does, and saves; said. Excel's own column
    insert (W9c's ensure_headers)."""
    import w9c_demonstration as C9   # noqa: PLC0415
    heads = C9.headers_of(book, "Gears")
    missing = [t for t, key in zip(BORE_TITLES, ("bore_allowance", "drive", "flat"))
               if not any(str(h).startswith(HEADS[key]) for h in heads)]
    if not missing:
        return []
    at = next((i + 1 for i, h in enumerate(heads) if str(h).startswith(HEADS["part_name"])),
              next(i + 1 for i, h in enumerate(heads) if not h))
    ws = book.wb.Worksheets("Gears")
    typed = []
    for i, title in enumerate(missing):
        ws.Columns(at + i).Insert()
        ref = f"{C9.column_letter(at + i)}1"
        book.set("Gears", ref, title)
        typed.append(f"{ref} {title!r}")
    book.save()
    say(f"person  {label}: the workbook was written before F3; the three columns inserted before Part name and headed "
        f"as the app heads them: {typed}")
    return typed


def sun_cells(book, fields):
    return [("Gears", W.cell(book, "Gears", HEADS[k], "Sun"), (None if v == "" else (float(v) if k != "drive" else v)))
            for k, v in fields.items()]


def keyway_code(label, path):
    found = [f for f in (F2.features_of(label, path) or []) if f[0] == "User Keyway"]
    return found[0][1] if found else None


def sun_judged(label, desk, fields, out):
    """Sun's part on record read: its D by its faces, links and globals (judge_hole, no twin), and its .gear.json at 4."""
    path = A.sun_part(desk.record.gearbox)
    entry = next(e for e in desk.record.current_parts() if store.same_path(e.path, path))
    spec = as_built(GearSpec.from_dict(dict(entry.spec)), entry.variables)
    derived = kind_for(spec).derive(spec)
    got = part_read(label, path)
    full = dict(fields, teeth=spec.teeth)
    out[label] = judge_hole(label, got, full, derived, volume=False)
    _, _, schema_ = sidecar_of(path)
    check(schema_ == 4, f"{label}: {file_of(path)}'s .gear.json at schema {schema_} (4)")
    return path


def bore_mate(label, desk, radius):
    """The user's concentric mate between Sprocket-4's bore (S0's Sprocket, Bore 10) and Sun's D's arc face, by
    AddMate5 on the two faces (W9c's probes' raw_mate and select_face, as W9d's fixture made its face mates), on in
    every mode, read back."""
    import w9c_probes as CP   # noqa: PLC0415
    box = desk.record.gearbox
    modes = list(box.modes)
    sun_name = dict(W.bodies(box))["Sun"]

    def work(s):
        s.find_component("sun", sun_name)
        s.find_component("u4", "Sprocket-4", lightweight_ok=True)
        sun, u4 = s._component("sun"), s._component("u4")  # noqa: SLF001
        mine = [f for k, r, f in CP.part_faces_of(sun) if k == "cylinder" and abs(r - radius) <= 1e-4]
        theirs = [f for k, r, f in CP.part_faces_of(u4) if k == "cylinder" and abs(r - SPROCKET_BORE_R) <= 1e-4]
        if not mine or not theirs:
            return {"faces": (len(mine), len(theirs))}
        kept, status = CP.raw_mate(s, BORE_MATE, 1, (lambda: CP.select_face(s, sun, mine[0], False, 1),
                                                     lambda: CP.select_face(s, u4, theirs[0], True, 1)))
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        s.find_mate("bm", kept)
        s.set_mate_suppressed_in("bm", False, modes)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        return {"faces": (len(mine), len(theirs)), "kept": kept, "status": status,
                "flags": s.mate_suppression("bm", modes),
                "codes": {m.name: (m.code, m.suppressed) for m in s.mate_states()},
                "entities": mate_entities(s, "bm")}
    got = run(label, job(box.assembly, work))
    say(f"person  {label}: {got}")
    wrong = mate_face_judged(got.get("entities", []), sun_name, radius)
    check(got.get("kept") == BORE_MATE and got["codes"].get(BORE_MATE, (1, True))[0] == 0
          and not any(got["flags"].values()) and not wrong,
          f"{label}: the user's concentric made on Sun's bore face (its entity on Sun read by mate_definition: a face "
          f"of radius {radius:.4f}; the arc read as {got.get('faces', (0,))[0]} face(s)), on in every mode, in no error: "
          f"{wrong or 'as said'}")
    return got


def mate_entities(s, handle):
    """A found mate's entities as Session.mate_definition reads them: [(component Name2, kind, EntityParams)]."""
    definition = s.mate_definition(handle)
    return [(e.component, e.kind, tuple(e.params)) for e in definition.entities]


def carried_face(label, desk, name, radius):
    """The carried bore mate read in the new revision by mate_definition: its entity on Sun a face of the hole's
    radius, so a concentric remade onto another face about the axis fails."""
    box = desk.record.gearbox
    sun_name = dict(W.bodies(box))["Sun"]

    def work(s):
        s.find_mate("cm", name)
        return mate_entities(s, "cm")
    entities = run(label, job(box.assembly, work))
    say(f"fact    {label}: {entities}")
    return mate_face_judged(entities, sun_name, radius)


def carry_said(label, result, out):
    """What the Build again's carry did, said (W9d's CarryResult), and that it ran to its end."""
    cr = getattr(result, "carry", None)
    if cr is None:
        check(False, f"{label}: the Build again carried nothing (no CarryResult)")
        return None
    out[label] = {"inserted": list(cr.inserted), "remade": [list(r[:2]) for r in cr.remade],
                  "named": [(n.item, n.what, n.why) for n in cr.named], "stopped": cr.stopped,
                  "changed_files": list(cr.changed_files), "facts": list(cr.facts)}
    for line in cr.log_lines():
        say("        " + line)
    check(not cr.stopped and not cr.changed_files,
          f"{label}: the carry ran to its end with no file of the user's changed on disk: stopped {cr.stopped!r}")
    return cr


def build_again(label, desk):
    """Build again... pressed as the window runs it (W9d's DeskD: old_assembly as before, carry_for as carry), the
    footer offering it."""
    if W.free_gb() < FREE_GB:
        A.section_stop(f"{label}: {W.memory()}: under {FREE_GB:g} GB free before the Build again")
    f = desk.say_footer(f"{label}, before")
    check(f.build_enabled and f.build_action == F2.ui_text.BUILD_AGAIN,
          f"{label}: the footer offers Build again... ({f.build_label!r}, enabled {f.build_enabled})")
    _, result = desk.build()
    if result is None:
        raise AssertionError(f"{label}: the build raised: {desk.error}")
    check(bool(getattr(result, "ok", False)) and not gearbox_undefined(result),
          f"{label}: built ok, every part's sketches fully defined: {list(getattr(result, 'failures', []))} "
          f"{gearbox_undefined(result) or ''}")
    return result


def section_userwork(out):
    say("== userwork  a copy of W9a's setup.master: Printed and one Update; Sun given a D bore by Build again...; the "
        "user's keyway and a mate on Sun's bore face; Sun's allowance and Flat in place by one Update; then Build "
        "again... for Sun's part name with its allowance cleared: kept as built, the bore mate carried")
    say(switch_line("userwork (typed and as-built figures only: judged whatever it reads)"))
    master = A.MASTER["setup"]
    if not master:
        raise AssertionError("userwork: give --user-master, W9a's setup.master for this SolidWorks version")
    if W.free_gb() < FREE_GB:
        A.section_stop(f"userwork: {W.memory()}: under {FREE_GB:g} GB free before the copy (run it first, in a fresh "
                       "session)")
    import w9d_demonstration as D   # noqa: PLC0415 - DeskD: Build again... with the carry, as the window runs it
    copy, path, book, desk = D.copy_desk(master, "userwork")
    try:
        box = desk.record.gearbox
        asm = box.assembly
        users = A.rb_users()
        sun0 = A.sun_part(box)
        entry = next(e for e in desk.record.current_parts() if store.same_path(e.path, sun0))
        # The keyway is read once RangeBox is open: features_of reads an open part only (None otherwise), and on
        # SolidWorks 2026's first run this check came before the open and read None.
        F2.open_assembly("userwork: RangeBox opened", asm)
        code0 = keyway_code("userwork: Sun", sun0)
        check(not GearSpec.from_dict(dict(entry.spec)).has_bore() and code0 == 0,
              f"userwork: Sun was built with no bore and holds the User Keyway, in no error (its code {code0})")
        A.users_in_copy("userwork, before", desk, copy, users)
        mates0 = mates_now("userwork, before", asm)

        say("-- userwork  Printed typed on the Box sheet; one Update SolidWorks; saved as the person saves")
        found, empty = F2.box_process_row(book)
        row = found or empty
        W.edit(desk, book, *(([] if found else [("Box", f"A{row}", "Process")]) + [("Box", f"B{row}", "Printed")]))
        u = desk.update
        n = len(desk.record.current_parts())
        check(desk.a.spec.box.process == "printed" and u is not None and len(u.changed_parts) == n
              and not u.needs_new_revision, f"userwork: Printed: Update plans the {n} parts in place")
        if W.free_gb() < FREE_GB:
            A.section_stop(f"userwork: {W.memory()}: under {FREE_GB:g} GB free before the press")
        result, _ = A.press(desk, "userwork: Printed, one Update")
        check(result is not None and result.ok and not result.user_in_error and not result.user_features_in_error,
              f"userwork: the Update ended ok, nothing of the user's in error: {desk.error}")
        A.save_user(copy, "the Update's result")
        desk.plan_solidworks()
        mates1 = mates_now("userwork, after Printed", asm)
        check(mates1 == mates0 and keyway_code("userwork: Sun", sun0) == 0,
              "userwork: after Printed's Update every mate's code and state and the User Keyway as before")

        say("-- userwork  Sun given Bore 8, allowance 0.2, Drive flat and Flat 7: structural, so Build again...")
        ensure_bore_headers(book, "userwork")
        W.edit(desk, book, *sun_cells(book, SUN_D))
        u = desk.update
        said = list(u.structural) if u is not None else []
        check(u is not None and u.needs_new_revision and len(said) == 1 and "(Sun)" in said[0],
              f"userwork: Sun's bore and D are structural, Sun alone: {said}")
        result = build_again("userwork: Sun given a D", desk)
        carry_said("userwork: Sun given a D", result, out)
        sun1 = sun_judged("userwork: Sun's new part", desk, SUN_D, out)
        check(not store.same_path(sun1, sun0), f"userwork: Sun is a new part: {file_of(sun1)}")
        A.save_user(copy, "the new revision")
        desk.plan_solidworks()
        asm = desk.record.gearbox.assembly

        # The bore mate is made after the in-place Update, not before it: a user's concentric on Sun's own face is a
        # mate K2 refuses an Update that puts Sun back over (ISSUE-1-PLAN K2: "a mate to a gear's own faces or planes"
        # refuses before any write, named), and SolidWorks 2026's first run met exactly that refusal, naming
        # UserBoreMate in H, N and L. So the in-place Update is made with the user's keyway in Sun and their eight
        # mates, and the bore mate, made on the D as the Update left it, is what the last Build again... carries.
        say("-- userwork  the user's keyway cut again in Sun; a quiet press records it")
        A.keyway("userwork: the user's keyway in the new Sun", sun1)
        A.save_user(copy, "the user's keyway")
        desk.plan_solidworks()
        result, _ = A.press(desk, "userwork: the quiet press")
        work = desk.record.gearbox.user_work
        check(result is not None and result.changed == [] and work is not None
              and "User Keyway" in [f.name for f in work.features if store.same_path(f.path, sun1)],
              f"userwork: the quiet press changed nothing and recorded the keyway in Sun")

        say("-- userwork  Sun's allowance 0.2 to 0.3 and Flat 7 to 7.2: one Update, in place")
        W.edit(desk, book, *sun_cells(book, SUN_IN_PLACE))
        u = desk.update
        changing = [p.path for p in (u.changed_parts if u else [])]
        check(u is not None and not u.needs_new_revision and len(changing) == 1
              and store.same_path(changing[0], sun1), f"userwork: Update changes Sun's part alone, in place: "
                                                      f"{[file_of(p) for p in changing]}")
        mates_b = mates_now("userwork, before the in-place Update", asm)
        result, _ = A.press(desk, "userwork: Sun's allowance and Flat, one Update")
        check(result is not None and result.ok and not result.user_in_error and not result.user_features_in_error,
              f"userwork: the Update ended ok, nothing of the user's in error: {desk.error}")
        placed = dict(SUN_D, **SUN_IN_PLACE)
        sun_judged("userwork: Sun in place", desk, placed, out)
        mates_a = mates_now("userwork, after the in-place Update", asm)
        users_mates = sorted(n for n in mates_b if n.startswith("User"))
        check(mates_a == mates_b and len(users_mates) == 8 and all(mates_a[n][0] == 0 for n in users_mates)
              and keyway_code("userwork: Sun", sun1) == 0,
              f"userwork: the user's feature and mates as before the Update (codes and states, the eight carried, "
              f"every one in no error; the User Keyway in no error): {users_mates}")
        A.save_user(copy, "the in-place Update")
        desk.plan_solidworks()

        say("-- userwork  a mate of the user's on the D's bore face as the Update left it; a quiet press records it")
        bore_mate("userwork: the user's bore mate", desk, d_expected(8, 0.3, 7.2)["R"])
        A.save_user(copy, "the user's bore mate")
        desk.plan_solidworks()
        result, _ = A.press(desk, "userwork: the quiet press after the bore mate")
        work = desk.record.gearbox.user_work
        check(result is not None and result.changed == [] and work is not None
              and BORE_MATE in [m.name for m in work.mates]
              and "User Keyway" in [f.name for f in work.features if store.same_path(f.path, sun1)],
              f"userwork: the quiet press changed nothing and recorded the bore mate and the keyway in Sun")

        say("-- userwork  Sun's allowance cleared (as built: 0.3) and its Part name SunGear: Build again...")
        W.edit(desk, book, *sun_cells(book, {"bore_allowance": ""}),
               ("Gears", W.cell(book, "Gears", HEADS["part_name"], "Sun"), SUN_NEW_NAME))
        result = build_again("userwork: Sun made new, its allowance blank", desk)
        cr = carry_said("userwork: Sun made new, its allowance blank", result, out)
        sun2 = sun_judged("userwork: Sun's newest part", desk, placed, out)
        entry = next(e for e in desk.record.current_parts() if store.same_path(e.path, sun2))
        kept = dict((str(n), str(v)) for n, v in entry.variables).get(ALLOWANCE_GLOBAL)
        check(file_of(sun2).startswith(SUN_NEW_NAME) and kept == SUN_IN_PLACE["bore_allowance"]
              and not str(dict(entry.spec).get("bore_allowance", "")).strip(),
              f"userwork: Sun made new as {file_of(sun2)} keeps its allowance as built ({kept}; ruling 1), its cell "
              "blank on record")
        remade = {r[0]: r[1] for r in (cr.remade if cr else [])}
        named = [n.item for n in (cr.named if cr else [])]
        codes = mates_now("userwork, the new revision", desk.record.gearbox.assembly)
        # K5, as W9D-INTERFACES section 4.4 rules it: a face of an app part made new is never re-found, but named
        # (WHY_PART_NEW), whatever made the part new; only a gear mate's face is read for its axis there (swbuild's
        # M1 walk), so a concentric's face on the old Sun is not read and is said as "a face of Sun". The script at
        # c5d4391 expected the mate remade; SolidWorks 2026's run named it so, with the eight others remade.
        bore_named = [n for n in (cr.named if cr else []) if n.item == BORE_MATE]
        subjects = tuple(bore_named[0].subjects) if bore_named else ()
        say(f"fact    userwork: the carry's reading of the bore mate's entity on the old Sun: {subjects} (where "
            f"{subjects[3] if len(subjects) > 3 else None!r}: \"bore\" only for a face read coaxial, and a face of a part "
            f"made new is read so for a gear mate only)")
        check(cr is not None and BORE_MATE not in remade and named == [BORE_MATE]
              and bore_named[0].why == swbuild.WHY_PART_NEW and len(subjects) >= 3 and subjects[2] == "face"
              and "Part name" in str(subjects[1]) and sorted(remade) == users_mates
              and all(codes.get(n, (1, True))[0] == 0 for n in users_mates),
              f"userwork: the mate on Sun's bore face is named, not made again, Sun's part being new for its Part name "
              f"(K5, W9D-INTERFACES section 4.4), and the user's eight other mates made again in no error: remade "
              f"{sorted(remade)}, named {[(n.item, n.why, tuple(n.subjects)) for n in (cr.named if cr else [])]}")
        A.users_in_copy("userwork, after", desk, copy, users)
    finally:
        if not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], copy, "userwork", save=False)


# -- the run ------------------------------------------------------------------------------------------------------------

ORDER = ["dshape", "allowance", "print", "built", "hub", "userwork"]
SECTIONS = {"dshape": section_dshape, "allowance": section_allowance, "print": section_print, "built": section_built,
            "hub": section_hub, "userwork": section_userwork}
FOLDERS = {"dshape": ["dshape"], "allowance": ["allowance"], "print": ["print"],
           "built": ["built", "built-f2", "built-f3", "built-machined"], "hub": ["hub"], "userwork": ["userwork"]}


def done_here(name):
    """What of a section this <out> holds already (W9a's done_here for these sections' folders)."""
    return [p for p in (os.path.join(OUT, f) for f in FOLDERS.get(name, [name])) if os.path.exists(p)]


def main():
    say(switch_line("the run's head"))
    RESULT["switch"] = repr(switch_now())
    A.SECTIONS.clear()
    A.SECTIONS.update(SECTIONS)
    if A._given in ("", "all"):                    # noqa: SLF001
        A.CHOSEN = list(ORDER)
    A.done_here = done_here
    A.RUN_TITLE, A.JSON_STEM = "F3 demonstration", "f3-demo"
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
