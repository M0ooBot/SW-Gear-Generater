"""Probe tier 9: a gear mate's sense between non-parallel axes (W6-PLAN §7.2, package P).

W5's read-back compares the two mate entities' directions with each other, which means nothing when they are at an
angle. W6 proposes H: a gear mate's ``Reverse`` is True exactly when it turns its two gears the same way about its two
entities' own directions. This probe makes gear mates between two cylinders (radius 10 and 20, standing for 20- and
40-tooth gears) on meeting axes at 30°, 60° and 90°, on skew axes at 60° and 90° on both hands of crossing, and on
parallel and anti-parallel axes as controls, every facing and both Flips, and judges each by the drive.

It carries its own few lines of the rule (``h_says``) and the entity matching, so it depends on no W6 code; the
app's ``swcom.sense_reading`` is later tested against its recorded cases.
"""

from __future__ import annotations

import math
import os
import time
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .. import findings
from ..swcom import call
from . import scaffold as sc
from .harness import Px, Require, probe

Vec = Tuple[float, float, float]
Matrix = Tuple[Vec, Vec, Vec]

RADIUS_A, RADIUS_B = 10.0, 20.0          # mm: a 20- and a 40-tooth gear of module 1
LENGTH = 10.0                            # mm along each cylinder's own +Z
TEETH = (20, 40)
FROM_A, FROM_B = 30.0, 50.0              # mm from the meeting point (or foot) along each own +Z
SKEW_OFFSET = 30.0                       # mm, the sum of the radii
PARALLEL_X = 30.0
DRIVE = "Drive"
DRIVE_FROM, DRIVE_TO = 90.0, 120.0
MATCH = 0.99                             # |d·g| an entity must reach to be matched to a gear
RATIO_TOL = 1e-6
MOVE_TOL = 1e-6
TAG = "Probe W9 Sense"

#: (class, Σf, side, facings): W6-PLAN §7.2's table
GEOMETRIES = (
    ("M", 30.0, "", ((1, 1), (1, -1), (-1, 1), (-1, -1))),
    ("M", 60.0, "", ((1, 1), (1, -1), (-1, 1), (-1, -1))),
    ("M", 90.0, "", ((1, 1), (1, -1), (-1, 1), (-1, -1))),
    ("K", 60.0, "+Y", ((1, 1), (1, -1))),
    ("K", 60.0, "-Y", ((1, 1), (1, -1))),
    ("K", 90.0, "+Y", ((1, 1), (1, -1))),
    ("K", 90.0, "-Y", ((1, 1), (1, -1))),
    ("P", 0.0, "+X", ((1, 1), (1, -1))),
)
#: (class, Σf, side, facing) saved, closed and reopened with the Flip H calls right
REOPENED = (("M", 90.0, "", (1, 1)), ("M", 60.0, "", (1, -1)), ("K", 90.0, "+Y", (1, 1)), ("K", 60.0, "-Y", (1, 1)))


# -- the pure part: geometry, the rule, the judgement ---------------------------------------------------------------

def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(float(x) * float(y) for x, y in zip(a, b))


def _cross(a: Sequence[float], b: Sequence[float]) -> Vec:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _unit(a: Sequence[float]) -> Vec:
    n = math.sqrt(_dot(a, a))
    return (a[0] / n, a[1] / n, a[2] / n)


def _scale(a: Sequence[float], k: float) -> Vec:
    return (a[0] * k, a[1] * k, a[2] * k)


def _add(a: Sequence[float], b: Sequence[float]) -> Vec:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def geometry_name(cls: str, sigma_f: float, side: str) -> str:
    return f"{cls}{sigma_f:g}{side.replace('+', 'p').replace('-', 'm')}"


def lines(cls: str, sigma_f: float, side: str) -> Dict[str, Any]:
    """The two frame axes: each a point and a direction (mm), the common perpendicular e from A to B (skew only)."""
    b = (math.sin(math.radians(sigma_f)), 0.0, math.cos(math.radians(sigma_f)))
    if cls == "M":
        return {"a": ((0.0, 0.0, 0.0), (0.0, 0.0, 1.0)), "b": ((0.0, 0.0, 0.0), b), "e": None,
                "foot_a": (0.0, 0.0, 0.0), "foot_b": (0.0, 0.0, 0.0)}
    if cls == "K":
        y = SKEW_OFFSET if side == "+Y" else -SKEW_OFFSET
        return {"a": ((0.0, 0.0, 0.0), (0.0, 0.0, 1.0)), "b": ((0.0, y, 0.0), b), "e": (0.0, math.copysign(1.0, y), 0.0),
                "foot_a": (0.0, 0.0, 0.0), "foot_b": (0.0, y, 0.0)}
    return {"a": ((0.0, 0.0, 0.0), (0.0, 0.0, 1.0)), "b": ((PARALLEL_X, 0.0, 0.0), (0.0, 0.0, 1.0)), "e": None,
            "foot_a": (0.0, 0.0, 0.0), "foot_b": (PARALLEL_X, 0.0, 0.0)}


def rot_y(degrees: float) -> Matrix:
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    return ((c, 0.0, s), (0.0, 1.0, 0.0), (-s, 0.0, c))


def _mul(a: Matrix, b: Matrix) -> Matrix:
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)) for i in range(3))  # type: ignore


FLIP_X: Matrix = ((1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, -1.0))
IDENTITY: Matrix = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


def frames(cls: str, sigma_f: float, side: str, facing: Tuple[int, int]) -> Dict[str, Tuple[Matrix, Vec]]:
    """Each cylinder's frame (by rows) and origin (mm): its own +Z along (σ = +1) or against (σ = −1) its frame axis,
    its origin FROM_A / FROM_B along its own +Z from its foot."""
    geo = lines(cls, sigma_f, side)
    sa, sb = facing
    ra = IDENTITY if sa > 0 else FLIP_X
    tilt = sigma_f if cls != "P" else 0.0
    rb = rot_y(tilt) if sb > 0 else _mul(rot_y(tilt), FLIP_X)
    ga = (ra[0][2], ra[1][2], ra[2][2])
    gb = (rb[0][2], rb[1][2], rb[2][2])
    return {"A": (ra, _add(geo["foot_a"], _scale(ga, FROM_A))), "B": (rb, _add(geo["foot_b"], _scale(gb, FROM_B)))}


def own_axis(matrix: Sequence[Sequence[float]]) -> Vec:
    return (float(matrix[0][2]), float(matrix[1][2]), float(matrix[2][2]))


def own_angle(ga: Sequence[float], gb: Sequence[float]) -> float:
    return math.degrees(math.acos(max(-1.0, min(1.0, _dot(ga, gb)))))


def along_plane(g: Sequence[float]) -> str:
    """The base plane whose normal is nearest a cylinder's axis: Front (Z), Right (X), ties to Right."""
    return "right" if abs(g[0]) >= abs(g[2]) - 1e-9 and abs(g[0]) > 1e-9 else "front"


def match_entities(directions: Sequence[Sequence[float]], axes: Sequence[Sequence[float]]) -> Dict[str, Any]:
    """Each entity matched to the cylinder whose own +Z it lies along (|d·g| ≥ MATCH); τ per cylinder; whether
    MateEntity(0) is the first selection (A). Raises ValueError when the matching fails."""
    if len(directions) != 2:
        raise ValueError(f"A gear mate holds {len(directions)} entities, not two.")
    if all(abs(_dot(d, g)) >= MATCH for d in directions for g in axes):
        # Parallel axes: each entity lies along both gears, and either pairing gives the same τA·τB (§2.6), so the
        # selection order is taken; nothing here says which entity is which.
        return {"tau": tuple(1 if _dot(d, g) > 0 else -1 for d, g in zip(directions, axes)), "entity_of": (0, 1),
                "first_is_a": None, "parallel": True}
    found: Dict[int, Tuple[int, float]] = {}
    for i, d in enumerate(directions):
        hits = [j for j, g in enumerate(axes) if abs(_dot(d, g)) >= MATCH]
        if len(hits) != 1:
            raise ValueError(f"Entity {i} along {list(d)} lies along {len(hits)} of the two gears' axes.")
        found[hits[0]] = (i, _dot(d, axes[hits[0]]))
    if set(found) != {0, 1}:
        raise ValueError("Both entities lie along one gear's axis.")
    return {"tau": (1 if found[0][1] > 0 else -1, 1 if found[1][1] > 0 else -1),
            "entity_of": (found[0][0], found[1][0]), "first_is_a": found[0][0] == 0}


def h_says(reverse: bool, tau: Sequence[int]) -> int:
    """H's sense: +1 when the mate turns the two gears the same way about their own +Z, −1 when opposite."""
    return (1 if reverse else -1) * int(tau[0]) * int(tau[1])


def skew_right(ga: Sequence[float], gb: Sequence[float], e: Sequence[float], line_b: Sequence[float]) -> Dict[str, Any]:
    """The sense a real crossed helical pair placed on this case would need, W6-PLAN §7.2: a virtual pair of the same
    hand, β_A = β_B = Σl/2, in gears/crossed.py's convention (gear 1 on its own +Z, the contact at +X toward gear 2,
    gear 2's axis rot_x(tilt)·Z with tilt = −hand·Σl), carried to the case with gear 1's own +Z on A's and its +X on
    e; the hand is the one whose gear-2 axis lies along the case's B line (right when both do, at 90°). The tooth
    direction at the contact on gear 1 is (0, hand·tan β, 1) (crossed.tooth_direction at azimuth 0, per mm of z);
    right is m = −s_A·s_B with s = sign(g·t)."""
    y_local = _cross(ga, e)
    cosl = abs(_dot(ga, line_b))
    sigma_l = math.degrees(math.acos(max(-1.0, min(1.0, cosl))))
    chosen = None
    for hand in (1, -1):
        axis2 = _add(_scale(y_local, hand * math.sin(math.radians(sigma_l))), _scale(ga, math.cos(math.radians(sigma_l))))
        if abs(abs(_dot(axis2, line_b)) - 1.0) < 1e-9:
            chosen = hand
            break
    if chosen is None:
        raise ValueError("Neither hand of crossed pair lies along the case's lines.")
    beta = sigma_l / 2.0
    t = _add(_scale(y_local, chosen * math.tan(math.radians(beta))), ga)
    s_a = 1 if _dot(ga, t) > 0 else -1
    s_b = 1 if _dot(gb, t) > 0 else -1
    return {"m": -s_a * s_b, "hand": "right" if chosen == 1 else "left", "sigma_l": sigma_l, "s": (s_a, s_b)}


def right_m(cls: str, ga: Sequence[float], gb: Sequence[float], e: Optional[Sequence[float]],
            line_b: Sequence[float]) -> int:
    """The sense a real pair placed so needs: meeting −1 (opposite about the own axes); skew by skew_right;
    parallel −1, anti-parallel +1 (W5)."""
    if cls == "M":
        return -1
    if cls == "K":
        return int(skew_right(ga, gb, e or (0.0, 1.0, 0.0), line_b)["m"])
    return -1 if _dot(ga, gb) > 0 else 1


def w5_says_right(reverse: bool, directions: Sequence[Sequence[float]], internal: bool = False) -> bool:
    """W5's rule, defined on parallel axes only: right when (Reverse == the entities point the same way) == internal."""
    return (reverse == (_dot(directions[0], directions[1]) > 0)) == internal


def alternative_says(reverse: bool, directions: Sequence[Sequence[float]], tau: Sequence[int],
                     e: Optional[Sequence[float]]) -> Dict[str, Optional[int]]:
    """The readings that differ from H on non-parallel axes (§7.2): Reverse against the sign of dA·dB (SolidWorks'
    closest alignment), and, for skew axes, against the sign of (dA × dB)·e. Each as a sense m like h_says."""
    r = 1 if reverse else -1
    t = int(tau[0]) * int(tau[1])
    dd = _dot(directions[0], directions[1])
    out: Dict[str, Optional[int]] = {"closest": r * (1 if dd > 0 else -1) * t if abs(dd) > 1e-9 else None}
    if e is not None:
        c = _dot(_cross(directions[0], directions[1]), e)
        out["crossing"] = r * (1 if c > 0 else -1) * t if abs(c) > 1e-9 else None
    return out


def judge(case: Mapping[str, Any]) -> Dict[str, Any]:
    """One driven gear mate, judged: the ratio, the measured sense m, H's, the right one, and the both-Flips fields."""
    da, db = case.get("delta_a"), case.get("delta_b")
    out: Dict[str, Any] = {"ratio_ok": False, "m": None}
    if isinstance(da, (int, float)) and isinstance(db, (int, float)) and abs(da) > 1e-9:
        ratio = db / da
        out["ratio"] = ratio
        out["ratio_ok"] = abs(abs(ratio) - TEETH[0] / TEETH[1]) < RATIO_TOL and \
            abs(abs(da) - (DRIVE_TO - DRIVE_FROM)) < 1e-6
        out["m"] = 1 if ratio > 0 else -1
    tau = case.get("tau")
    if not tau and case.get("directions") and case.get("own_axes"):
        try:      # the recorded directions and axes, matched again (a case recorded before the parallel matching)
            tau = match_entities(case["directions"], case["own_axes"])["tau"]
        except ValueError:
            tau = None
    out["tau"] = list(tau) if tau else None
    out["m_h"] = h_says(case["reverse"], tau) if tau and isinstance(case.get("reverse"), bool) else None
    out["right_m"] = case.get("right_m")
    out["turned_right"] = out["m"] == out["right_m"] if out["m"] is not None else None
    out["h_right"] = out["m_h"] == out["right_m"] if out["m_h"] is not None else None
    out["h_tells"] = out["m_h"] == out["m"] if out["m"] is not None and out["m_h"] is not None else False
    return out


# -- the decision (decide.py calls these) ----------------------------------------------------------------------------

def read_back_verdict(cases: Sequence[Mapping[str, Any]], reopened: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Whether H tells every case, per W6-PLAN §7.2's conditions, and, if not, which alternative reading does."""
    turned = [c for c in cases if c["cls"] != "P"]
    controls = [c for c in cases if c["cls"] == "P"]
    problems: List[str] = []
    for c in cases:
        j = judge(c)
        tag = f"{c['geometry']} {tuple(c['facing'])} flip {c['flip']}"
        if c.get("status") != findings.ADD_MATE_NO_ERROR:
            problems.append(f"{tag}: AddMate5 status {c.get('status')}")
        if c.get("moved_on_make"):
            problems.append(f"{tag}: a cylinder moved when the mate was made")
        if not j["ratio_ok"]:
            problems.append(f"{tag}: the ratio was {j.get('ratio')}")
        if not j["h_tells"]:
            problems.append(f"{tag}: H said {j['m_h']}, the drive {j['m']}")
    both: Dict[str, bool] = {}
    for key in sorted({(c["geometry"], tuple(c["facing"])) for c in cases}):
        pair = [judge(c) for c in cases if (c["geometry"], tuple(c["facing"])) == key]
        ok = len(pair) == 2 and sorted(bool(p["turned_right"]) for p in pair) == [False, True] and \
            all(p["h_right"] == p["turned_right"] for p in pair)
        both[f"{key[0]} {key[1]}"] = ok
        if not ok:
            problems.append(f"{key}: the both-Flips control fails")
    for c in controls:
        if w5_says_right(c["reverse"], c["directions"]) != judge(c)["turned_right"]:
            problems.append(f"{c['geometry']} {tuple(c['facing'])} flip {c['flip']}: W5's rule disagrees with the drive")
    for r in reopened:
        if r.get("m_h") != r.get("m_h_first") or r.get("m") != r.get("m_first"):
            problems.append(f"{r.get('geometry')} {r.get('facing')}: the reopened read or drive differs from the first")
    alternatives: Dict[str, bool] = {}
    for name in ("closest", "crossing"):
        relevant = [c for c in turned if name != "crossing" or c["cls"] == "K"]
        alternatives[name] = bool(relevant) and all(
            (c.get("alternatives") or {}).get(name) == judge(c)["m"] for c in relevant)
    holds = not problems and len(turned) == 40 and len(controls) == 4
    value = "entity senses" if holds else None
    if not holds and alternatives.get("closest") and not [p for p in problems if "H said" not in p]:
        value = "closest alignment"
    return {"value": value, "problems": problems, "both_flips": both, "alternatives": alternatives,
            "turned": len(turned), "controls": len(controls)}


def angles_verdict(cases: Sequence[Mapping[str, Any]], value: Optional[str]) -> Optional[Tuple[float, float]]:
    """The least and greatest angle between the own axes over which every turned case held; None when none did."""
    if value is None:
        return None
    held = [c["own_angle"] for c in cases if c["cls"] != "P" and judge(c)["h_tells"] and judge(c)["ratio_ok"]]
    failed = [c["own_angle"] for c in cases if c["cls"] != "P" and not (judge(c)["h_tells"] and judge(c)["ratio_ok"])]
    if not held:
        return None
    lo, hi = min(held), max(held)
    if failed:
        # Narrowed to the band between the failures nearest 90°.
        below = [a for a in failed if a <= 90.0]
        above = [a for a in failed if a >= 90.0]
        lo = min(a for a in held if not below or a > max(below)) if below else lo
        hi = max(a for a in held if not above or a < min(above)) if above else hi
    return (round(lo, 6), round(hi, 6))


# -- SolidWorks ------------------------------------------------------------------------------------------------------

def _cylinder(px: Px, folder: str, stem: str, radius: float) -> str:
    """A solid cylinder ``radius`` × LENGTH mm extruded from Front along +Z, its Gear Axis from Top then Right
    (reading +Z, as every gear part's); saved, left open."""
    from .p2_solid import _extrude_args  # noqa: PLC0415
    from .p7_workbook import _millimetres  # noqa: PLC0415
    path = os.path.join(folder, f"{stem}.SLDPRT")
    px.require(not os.path.exists(path), f"{path} does not exist yet")
    doc = sc.new_document(px)
    _millimetres(px, doc)
    with sc.quiet_dimensions(px):
        before = sc.feature_names(doc)
        manager = sc.open_sketch(px, doc, 1)
        circle = call(manager, "CreateCircleByRadius", 0.0, 0.0, 0.0, radius / sc.MM)
        sc.relate(doc, "sgCOINCIDENT", call(circle, "GetCenterPoint2"), sc.origin_point(doc))
        sketch = sc.close_sketch(px, doc, f"{stem} Sketch", before)
    px.require(sc.select_feature(doc, sc.feature_by_name(doc, sketch)), f"{stem}'s sketch selects")
    feature = call(sc.feature_manager(doc), "FeatureExtrusion3", *_extrude_args(LENGTH / sc.MM))
    call(doc, "ClearSelection2", True)
    px.require(feature is not None, f"{stem} extrudes")
    px.require(sc.select_plane(doc, 2) and sc.select_plane(doc, 3, append=True), f"{stem}: Top and Right select")
    before = sc.feature_names(doc)
    call(doc, "InsertAxis2", True)
    call(doc, "ClearSelection2", True)
    axis = sc.feature_by_name(doc, sc.new_features(doc, before)[0][0])
    axis.Name = "Gear Axis"
    params = [float(v) for v in call(call(axis, "GetSpecificFeature2"), "GetRefAxisParams")]
    d = _unit((params[3] - params[0], params[4] - params[1], params[5] - params[2]))
    px.fact(f"{stem} Gear Axis direction", [round(v, 9) for v in d])
    result = call(sc.extension(doc), "SaveAs3", path, 0, 1, sc.null(), sc.null(), sc.out_long(), sc.out_long())
    px.shared.setdefault("created", []).append(str(call(doc, "GetTitle")))
    px.require(os.path.isfile(path), f"{stem} saves: {result!r}")
    return path


def _frame_part(px: Px, folder: str, cls: str, sigma_f: float, side: str) -> Tuple[str, Dict[str, Any]]:
    """``SenseFrame_<case>``: "A Axis" through Top and Right (the Z axis), "B Axis" by InsertAxis2 on the one line
    of a 2D sketch on Top (or a plane offset from Top by SKEW_OFFSET), the line fixed by its end points in model
    coordinates; both read back."""
    from .p2_bevel import _segment_name, _select_segment, _sketch_point  # noqa: PLC0415
    from .p2_helical import model_to_sketch, open_on  # noqa: PLC0415
    from .p7_workbook import _millimetres  # noqa: PLC0415
    from .p8_motion import _plane_from  # noqa: PLC0415

    name = geometry_name(cls, sigma_f, side)
    path = os.path.join(folder, f"SenseFrame_{name}.SLDPRT")
    px.require(not os.path.exists(path), f"{path} does not exist yet")
    geo = lines(cls, sigma_f, side)
    doc = sc.new_document(px)
    _millimetres(px, doc)
    read: Dict[str, Any] = {}
    px.require(sc.select_plane(doc, 2) and sc.select_plane(doc, 3, append=True), f"{name}: Top and Right select")
    before = sc.feature_names(doc)
    call(doc, "InsertAxis2", True)
    call(doc, "ClearSelection2", True)
    a_axis = sc.feature_by_name(doc, sc.new_features(doc, before)[0][0])
    a_axis.Name = "A Axis"
    plane = sc.planes(doc)[1]
    if cls == "K":
        flips = px.shared.get("layout_plus_flip") or {}
        px.require("top" in flips, "layout_planes has said which flip puts a plane on +Y")
        plus = bool(flips["top"])
        plane = _plane_from(px, doc, plane, SKEW_OFFSET, plus if side == "+Y" else not plus, "B Plane",
                            {"plane": {}, "axis": {}})
    point, direction = geo["b"]
    with sc.quiet_dimensions(px):
        before = sc.feature_names(doc)
        manager = open_on(px, doc, plane)
        data = model_to_sketch(call(manager, "ActiveSketch"))
        p0 = _sketch_point(data, _add(point, _scale(direction, -40.0)))
        p1 = _sketch_point(data, _add(point, _scale(direction, 40.0)))
        line = call(manager, "CreateLine", p0[0], p0[1], 0.0, p1[0], p1[1], 0.0)
        px.require(line is not None, f"{name}: the B line is made")
        segment = _segment_name(line)
        sketch = sc.close_sketch(px, doc, "B Line", before)
    px.require(_select_segment(doc, sketch, segment, False, 0), f"{segment}@{sketch} selects")
    before = sc.feature_names(doc)
    made = call(doc, "InsertAxis2", True)
    call(doc, "ClearSelection2", True)
    new = [n for n, t in sc.new_features(doc, before) if t == "RefAxis"]
    px.require(bool(made) and len(new) == 1, f"{name}: InsertAxis2 makes one axis from the line")
    b_axis = sc.feature_by_name(doc, new[0])
    b_axis.Name = "B Axis"
    for key, axis, (pt, want) in (("A", a_axis, geo["a"]), ("B", b_axis, geo["b"])):
        params = [float(v) for v in call(call(axis, "GetSpecificFeature2"), "GetRefAxisParams")]
        p = (params[0] * sc.MM, params[1] * sc.MM, params[2] * sc.MM)      # metres to mm
        d = _unit((params[3] - params[0], params[4] - params[1], params[5] - params[2]))
        off = _add(p, _scale(pt, -1.0))
        distance = math.sqrt(max(0.0, _dot(off, off) - _dot(off, want) ** 2))
        read[key] = {"direction": [round(v, 9) for v in d], "off_line_mm": round(distance, 9)}
        px.require(abs(abs(_dot(d, want)) - 1.0) < 1e-9 and distance < MOVE_TOL,
                   f"{name}: {key} Axis lies along {list(want)} through {list(pt)} (read {read[key]})")
    result = call(sc.extension(doc), "SaveAs3", path, 0, 1, sc.null(), sc.null(), sc.out_long(), sc.out_long())
    px.shared.setdefault("created", []).append(str(call(doc, "GetTitle")))
    px.require(os.path.isfile(path), f"{name}'s frame part saves: {result!r}")
    return path, read


def _frame_of(component: Any) -> Tuple[Matrix, Vec]:
    from .p4_nonparallel import frame_of  # noqa: PLC0415
    return frame_of(component)


def _moved(a: Tuple[Matrix, Vec], b: Tuple[Matrix, Vec]) -> float:
    return max(max(abs(a[0][i][j] - b[0][i][j]) for i in range(3) for j in range(3)), math.dist(a[1], b[1]))


def _anchor(px: Px, doc: Any, comp: Any, frame: Any, axis: str, g: Vec, origin: Vec, label: str) -> List[str]:
    """W5's anchor mates: the Gear Axis coincident with the frame axis (closest), the origin at a point distance from
    the frame base plane whose normal is nearest the axis, linked to nothing."""
    from .p8_motion import _enums, _plane_names, _select_origin, add_mate, not_made, select_in, unfix  # noqa: PLC0415
    enums = _enums(px)
    px.require(unfix(px, doc, comp), f"{label} floats")
    px.require(bool(select_in(px, doc, comp, "Gear Axis", "AXIS", False)) and
               bool(select_in(px, doc, frame, axis, "AXIS", True)), f"{label}'s axis and {axis} select")
    made = [add_mate(px, doc, f"{label} on {axis}", enums["coincident"], enums["closest"])]
    plane = along_plane(g)
    index, coordinate = (2, origin[0]) if plane == "right" else (0, origin[2])
    px.require(bool(_select_origin(px, doc, comp, append=False)) and
               bool(select_in(px, doc, frame, _plane_names(frame)[index], "PLANE", True)),
               f"{label}'s origin and the frame's {plane.title()} plane select")
    if abs(coordinate) < 1e-9:
        made.append(add_mate(px, doc, f"{label} along", enums["coincident"], enums["closest"]))
    else:
        made.append(add_mate(px, doc, f"{label} along", enums["distance"], enums["closest"], flip=coordinate < 0,
                             distance=abs(coordinate)))
    for m in made:
        if not m.get("name"):
            raise Require(not_made(label, m))
    return [m["name"] for m in made]


def _make_and_read(px: Px, doc: Any, comps: Mapping[str, Any], flip: bool) -> Dict[str, Any]:
    """With CommandInProgress on: the gear mate A–B, ratio 20 : 40, ``flip``, renamed; Reverse and both entities read
    straight after; CommandInProgress off; both frames again."""
    from .p8_motion import (_command_in_progress, _enums, _rename, add_mate, entity_params,  # noqa: PLC0415
                            gear_mate_definition, mate_feature, select_in)
    enums = _enums(px)
    before = {k: _frame_of(c) for k, c in comps.items()}
    out: Dict[str, Any] = {"flip": flip, "cip_on": _command_in_progress(px, True)}
    try:
        picked = bool(select_in(px, doc, comps["A"], "Gear Axis", "AXIS", False)) and \
            bool(select_in(px, doc, comps["B"], "Gear Axis", "AXIS", True))
        made = add_mate(px, doc, f"A meshes B flip {flip}", enums["gear"], enums["closest"], flip=flip,
                        ratio=(float(TEETH[0]), float(TEETH[1]))) if picked else {"name": None, "status": None}
        out["status"] = made.get("status")
        out["made"] = made
        if made.get("name"):
            _rename(px, mate_feature(doc, made["name"]), "A meshes B")
            out["definition"] = gear_mate_definition(px, doc, "A meshes B")
            out["entities"] = entity_params(px, doc, "A meshes B")
    finally:
        out["cip_off"] = _command_in_progress(px, False)
    after = {k: _frame_of(c) for k, c in comps.items()}
    out["moved_on_make"] = max(_moved(before[k], after[k]) for k in comps) > MOVE_TOL
    return out


def _drive(px: Px, doc: Any, comps: Mapping[str, Any], frame: Any, label: str) -> Dict[str, Any]:
    """The temporary drive: A's Top plane to the frame's Right at 90°, on the global "Drive"; 90 → 120; each
    cylinder's turn about its own +Z; set back; the link, global and angle mate deleted."""
    from .p1_equations import adder  # noqa: PLC0415
    from .p8_motion import (TOP_ONLY, _enums, _plane_names, _set_global, _spike_undrive, drive_mate,  # noqa: PLC0415
                            own_turn, rebuild)
    add = adder(px, call(doc, "GetEquationMgr"))
    px.require(add(f'"{DRIVE}"= {DRIVE_FROM:g}') >= 0, f"{label}: the drive global is added")
    drive = drive_mate(px, doc, comps["A"], _plane_names(comps["A"])[1], frame, _plane_names(frame)[2], "A", add,
                       _enums(px)["closest"], angle=DRIVE_FROM, global_name=DRIVE)
    px.require(bool(drive), f"{label}: A is driven")
    rebuild(px, doc, f"{label}: drive added", top_only=TOP_ONLY)
    start = {k: _frame_of(c) for k, c in comps.items()}
    _set_global(call(doc, "GetEquationMgr"), DRIVE, DRIVE_TO)
    rebuild(px, doc, f"{label}: driven", top_only=TOP_ONLY)
    end = {k: _frame_of(c) for k, c in comps.items()}
    out = {"delta_a": round(own_turn(start["A"][0], end["A"][0]), 9),
           "delta_b": round(own_turn(start["B"][0], end["B"][0]), 9),
           "origins_moved_mm": {k: round(math.dist(start[k][1], end[k][1]), 9) for k in comps},
           "axes_moved": {k: round(math.degrees(math.acos(max(-1.0, min(1.0, _dot(own_axis(start[k][0]),
                                                                                  own_axis(end[k][0])))))), 9)
                          for k in comps}}
    _set_global(call(doc, "GetEquationMgr"), DRIVE, DRIVE_FROM)
    rebuild(px, doc, f"{label}: set back", top_only=TOP_ONLY)
    out["back"] = max(_moved(start[k], _frame_of(c)) for k, c in comps.items())
    _spike_undrive(px, doc, drive, DRIVE)
    rebuild(px, doc, f"{label}: drive taken away", top_only=TOP_ONLY)
    return out


def _record(px: Px, cls: str, sigma_f: float, side: str, facing: Tuple[int, int], placed: Mapping[str, Any],
            made: Mapping[str, Any], driven: Mapping[str, Any]) -> Dict[str, Any]:
    geo = lines(cls, sigma_f, side)
    ga, gb = own_axis(placed["A"][0]), own_axis(placed["B"][0])
    directions = [e.get("params", [0] * 6)[3:6] for e in made.get("entities") or []]
    case: Dict[str, Any] = {"cls": cls, "sigma_f": sigma_f, "side": side, "geometry": geometry_name(cls, sigma_f, side),
                            "facing": list(facing), "flip": made["flip"], "status": made.get("status"),
                            "reverse": (made.get("definition") or {}).get("Reverse"),
                            "ratio_read": [(made.get("definition") or {}).get("GearRatioNumerator"),
                                           (made.get("definition") or {}).get("GearRatioDenominator")],
                            "directions": directions, "own_axes": [list(ga), list(gb)],
                            "own_angle": round(own_angle(ga, gb), 6), "moved_on_make": made.get("moved_on_make"),
                            **{k: driven.get(k) for k in ("delta_a", "delta_b", "origins_moved_mm", "axes_moved",
                                                          "back")}}
    try:
        matched = match_entities(directions, (ga, gb))
        case.update(tau=list(matched["tau"]), first_is_a=matched["first_is_a"])
    except ValueError as exc:
        case.update(tau=None, match_error=str(exc))
    case["right_m"] = right_m(cls, ga, gb, geo["e"], geo["b"][1])
    if cls == "K":
        case["virtual_pair"] = skew_right(ga, gb, geo["e"], geo["b"][1])
    if case.get("tau") and isinstance(case["reverse"], bool):
        case["alternatives"] = alternative_says(case["reverse"], directions, case["tau"], geo["e"])
    case.update(judge(case))
    return case


@probe("turned_gear_mate_sense", needs=("motion_enums", "layout_planes", "axis_from_sketch_line"), tier=9,
       members=("IAssemblyDoc.AddMate5 gear non-parallel", "IGearMateFeatureData.Reverse", "IMateEntity2.EntityParams",
                "IModelDoc2.InsertAxis2 sketch line", "ISldWorks.CommandInProgress"))
def turned_gear_mate_sense(px: Px) -> None:
    """A gear mate between non-parallel axes: does H (Reverse == the mate turns its gears the same way about its
    entities' own directions) tell every case's sense, judged by the drive? W6-PLAN §7.2."""
    from .p4_nonparallel import place  # noqa: PLC0415
    from .p7_workbook import _millimetres, _save_in_place, close_paths, open_by_path  # noqa: PLC0415
    from .p8_motion import TOP_ONLY, _close_quietly, delete_mate, fix, rebuild  # noqa: PLC0415

    folder = os.path.join(sc.env_scratch_folder(px), "w9sense")
    px.require(folder[1:3] == ":\\" and not os.path.exists(folder), f"{folder} is new and on a drive")
    os.makedirs(folder)
    a_path = _cylinder(px, folder, "SenseA", RADIUS_A)
    b_path = _cylinder(px, folder, "SenseB", RADIUS_B)
    cases: List[Dict[str, Any]] = []
    reopened: List[Dict[str, Any]] = []
    frames_read: Dict[str, Any] = {}
    timing: Dict[str, float] = {}
    for cls, sigma_f, side, facings in GEOMETRIES:
        gname = geometry_name(cls, sigma_f, side)
        frame_path, frames_read[gname] = _frame_part(px, folder, cls, sigma_f, side)
        _close_quietly(px, [frame_path])
        for facing in facings:
            started = time.monotonic()
            placed = frames(cls, sigma_f, side, facing)
            asm_path = os.path.join(folder, f"{TAG} {gname} {facing[0]:+d}{facing[1]:+d}.SLDASM")
            paths = [asm_path, frame_path, a_path, b_path]
            doc = None
            per_flip: Dict[bool, Dict[str, Any]] = {}
            try:
                for p in (frame_path, a_path, b_path):
                    open_by_path(px, p, prefer="OpenDoc6")
                doc = sc.new_document(px, sc.SW_DOC_ASSEMBLY)
                _millimetres(px, doc)
                frame = call(doc, "AddComponent5", frame_path, 0, "", False, "", 0.0, 0.0, 0.0)
                px.require(frame is not None, f"{gname}: the frame is inserted")
                place(px, doc, frame, IDENTITY, (0.0, 0.0, 0.0))
                px.require(fix(px, doc, frame), f"{gname}: the frame is fixed")
                comps = {}
                for key, path in (("A", a_path), ("B", b_path)):
                    m, at = placed[key]
                    comp = call(doc, "AddComponent5", path, 0, "", False, "", sc.m(at[0]), sc.m(at[1]), sc.m(at[2]))
                    px.require(comp is not None, f"{gname}: {key} is inserted")
                    place(px, doc, comp, m, at)
                    comps[key] = comp
                for key in ("A", "B"):
                    m, at = placed[key]
                    _anchor(px, doc, comps[key], frame, f"{key} Axis", own_axis(m), at, key)
                rebuild(px, doc, f"{gname}: anchored", top_only=TOP_ONLY)
                mounted = {k: _frame_of(c) for k, c in comps.items()}
                mount_off = max(_moved(placed[k], mounted[k]) for k in comps)
                for flip in (False, True):
                    made = _make_and_read(px, doc, comps, flip)
                    driven = _drive(px, doc, comps, frame, f"{gname} {facing} flip {flip}") if made.get("made", {}).get(
                        "name") else {}
                    case = _record(px, cls, sigma_f, side, facing, {k: mounted[k] for k in comps}, made, driven)
                    case["mount_off"] = mount_off
                    cases.append(case)
                    per_flip[flip] = case
                    if made.get("made", {}).get("name"):
                        delete_mate(px, doc, "A meshes B")
                        rebuild(px, doc, f"{gname} {facing}: gear mate deleted", top_only=TOP_ONLY)
                if (cls, sigma_f, side, tuple(facing)) in REOPENED:
                    chosen = next((f for f, c in per_flip.items() if c.get("h_right")), None)
                    if chosen is not None:
                        made = _make_and_read(px, doc, comps, chosen)
                        rebuild(px, doc, f"{gname} {facing}: kept", top_only=TOP_ONLY)
                        px.require(_save_in_place(px, doc, asm_path, f"{gname} {facing}") and os.path.isfile(asm_path),
                                   f"{gname} {facing} saves")
                        px.shared["created"].append(str(call(doc, "GetTitle")))
                        names = {k: str(call(c, "Name2")) for k, c in comps.items()}
                        frame_name = str(call(frame, "Name2"))
                        _close_quietly(px, paths)
                        doc = None
                        doc2, _ = open_by_path(px, asm_path, sc.SW_DOC_ASSEMBLY, prefer="OpenDoc6")
                        comps2 = {k: call(doc2, "GetComponentByName", n) for k, n in names.items()}
                        frame2 = call(doc2, "GetComponentByName", frame_name)
                        from .p8_motion import entity_params, gear_mate_definition  # noqa: PLC0415
                        again = {"flip": chosen, "definition": gear_mate_definition(px, doc2, "A meshes B"),
                                 "entities": entity_params(px, doc2, "A meshes B"), "status": 1,
                                 "moved_on_make": False}
                        drove = _drive(px, doc2, comps2, frame2, f"{gname} {facing} reopened")
                        r = _record(px, cls, sigma_f, side, facing, {k: _frame_of(c) for k, c in comps2.items()},
                                    again, drove)
                        r.update(m_h_first=per_flip[chosen]["m_h"], m_first=per_flip[chosen]["m"])
                        reopened.append(r)
            finally:
                if doc is not None and not str(call(doc, "GetPathName") or ""):
                    try:
                        sc.close(px, doc)          # the unsaved assembly, which no path finds
                    except Exception as exc:  # noqa: BLE001
                        px.note(f"CLEANUP {exc}")
                _close_quietly(px, paths)
            timing[f"{gname} {facing}"] = round(time.monotonic() - started, 1)
        _close_quietly(px, [frame_path])
    _close_quietly(px, [a_path, b_path])
    px.fact("turned_sense_frames", frames_read)
    px.fact("turned_sense_cases", cases)
    px.fact("turned_sense_reopened", reopened)
    px.fact("turned_sense_seconds", timing)
    verdict = read_back_verdict(cases, reopened)
    table = {f"{c['geometry']} {c['facing'][0]:+d}{c['facing'][1]:+d} flip {c['flip']}":
             {"angle": c["own_angle"], "Reverse": c["reverse"], "tau": c.get("tau"), "m": c["m"], "m_H": c["m_h"],
              "right": c["right_m"], "ratio": c.get("ratio"), "status": c["status"]} for c in cases}
    px.check(True, f"turned gear mates: {table}")
    px.fact("turned_sense_table", table)
    px.fact("turned_sense_verdict", verdict)
    px.fact("turned_sense_read_back", verdict["value"])
    px.fact("turned_sense_angles", angles_verdict(cases, verdict["value"]))
    px.fact("turned_gear_mate_moves_on_make", any(bool(c.get("moved_on_make")) for c in cases))
    orders = {c.get("first_is_a") for c in cases if c.get("first_is_a") is not None}
    px.fact("gear_mate_entity_order", "first selection first" if orders == {True} else
            "second selection first" if orders == {False} else f"mixed: {sorted(orders)}")
