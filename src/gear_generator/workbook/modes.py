"""A workbook's modes: where each slider sits in each mode, and what each mode engages (phase W8; W8-PLAN §1.2-§1.3).

Pure. The one home of three rules: a mode's picks (a blank pick is the slider's position at 0, J5; with sliders and
no Modes rows there is one implicit mode, every slider at its 0); a slider's place in a mode (its face centre at
``point + (At + offset) × axis``); and engagement (J4): a sleeve engages a dog on another shaft on its axis exactly
when it covers the dog's whole face — partial cover is an error, teeth that do not match while they overlap at all
an error — and a sliding mesh is in mesh when the narrower face is covered, out with no overlap, an error between.

A coupling is never a gear mesh: it does not go through ``checks._check_mesh``, ``checks.internal_working_centre``
or the ring's tip check (equal teeth at centre distance 0 would be refused by each), and sleeves and dogs listed on
Meshes are errors of their own (``checks``), so none of those is ever called on one.

W9b (ISSUE-1-PLAN §2.2-§2.4, K7-K10; W9B-INTERFACES): a sleeve may have two toothed bands, and every rule above is
judged per band (:func:`band_spans`; an unbanded sleeve is one band, its whole face, so it reads as W8 read it); a
**hub** row carries a sleeve on its own shaft, engages nothing and must lie under a band of it in every mode
(:func:`hub_errors`).
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Tuple

from ..gears.base import ERROR, WARNING, Diagnostic
from .geometry import Placed, _place
from .model import GearboxSpec, Gear

SLEEVE, DOG, HUB = "sleeve", "dog", "hub"
CLUTCH_KINDS = (SLEEVE, DOG, HUB)
COVER_TOLERANCE = 1e-6          # mm: a face covered to this is covered whole; overlapping less than this is apart
AXIS_TOLERANCE = 1e-9           # mm: two shafts on one line (layout.BASE_TOLERANCE)


@dataclass(frozen=True)
class Picks:
    """One mode's picks: ``name`` (``""`` for the implicit mode), ``row`` its Modes-sheet row (0 implicit), and per
    slider ``(position, offset mm)``, sliders in the Modes sheet's column order then any other slider's in
    Gears-sheet order."""

    name: str
    row: int
    positions: Dict[str, Tuple[str, float]] = field(default_factory=dict)


def sliders(spec: GearboxSpec) -> List[Gear]:
    """Every gear with Slides, in Gears-sheet order."""
    return [g for g in spec.gears if g.id and g.slides.strip()]


def mode_picks(spec: GearboxSpec) -> Tuple[List[Picks], List[Diagnostic]]:
    """Every mode's picks, Modes-sheet order (or the implicit mode), and the errors at their cells: a blank pick
    whose slider has no position at 0 (J5); with no Modes rows, a slider with no position at 0 (at its Slides cell);
    Modes rows with no slider column. A slider whose Slides do not read is the read's error and left out."""
    out: List[Picks] = []
    errors: List[Diagnostic] = []
    moving = sliders(spec)
    readable = {}
    for g in moving:
        try:
            readable[g.id] = g.positions()
        except ValueError:
            continue
    if spec.modes and not spec.sliders and not moving:
        errors.append(Diagnostic(ERROR, "Modes: the Modes sheet has modes but no slider column.", "Modes"))
        return out, errors
    if not moving:
        return out, errors
    order = [s for s in spec.sliders if s in readable] + [g.id for g in moving if g.id not in spec.sliders
                                                           and g.id in readable]
    if not spec.modes:
        picks: Dict[str, Tuple[str, float]] = {}
        for gid in order:
            zero = next((p for p, v in readable[gid].items() if v == 0), None)
            if zero is None:
                gear = spec.gear(gid)
                where = spec.cell("Gears", gear.row, "slides")
                errors.append(Diagnostic(ERROR, f"{where}: {gid} has no position at 0, and with no Modes rows each "
                                                "slider sits at its position 0; add one, or add Modes rows.", where))
                continue
            picks[gid] = (zero, 0.0)
        out.append(Picks("", 0, picks))
        return out, errors
    for mode in spec.modes:
        chosen = dict(mode.positions)
        picks = {}
        for gid in order:
            pick = str(chosen.get(gid, "") or "").strip()
            positions = readable[gid]
            if not pick:
                pick = next((p for p, v in positions.items() if v == 0), "")
                if not pick:
                    where = spec.cell("Modes", mode.row, gid)
                    names = list(positions)
                    listed = " and ".join(names) if len(names) <= 2 else ", ".join(names[:-1]) + " and " + names[-1]
                    errors.append(Diagnostic(ERROR, f"{where}: {gid} has no position at 0, so a blank here does not "
                                                    f"say where it sits; pick one of {listed}.", where))
                    continue
            name = next((p for p in positions if p.casefold() == pick.casefold()), None)    # §9.6: ignoring case
            if name is None:
                continue                                  # the read's error (model): a pick not among the positions
            picks[gid] = (name, float(positions[name]))
        out.append(Picks(mode.name, mode.row, picks))
    return out, errors


def place_mode(spec: GearboxSpec, placed: Dict[str, Placed], picks: Picks) -> Dict[str, Placed]:
    """Every slider placed at its pick (``geometry._place`` with ``At + offset``), keyed by gear id; a slider not
    placed in the layout is left out."""
    shafts = {s.id: s for s in spec.shafts}
    out: Dict[str, Placed] = {}
    for gid, (_pos, offset) in picks.positions.items():
        gear = spec.gear(gid)
        if gear is None or gid not in placed or gear.shaft not in shafts:
            continue
        at = float(gear.at or 0) + offset
        out[gid] = _place(spec, replace(gear, at=repr(at)), shafts[gear.shaft])
    return out


def _span(p: Placed) -> Tuple[float, float]:
    return p.z_range


def _coaxial(a: Placed, b: Placed) -> bool:
    cross = (a.axis[1] * b.axis[2] - a.axis[2] * b.axis[1], a.axis[2] * b.axis[0] - a.axis[0] * b.axis[2],
             a.axis[0] * b.axis[1] - a.axis[1] * b.axis[0])
    if max(abs(c) for c in cross) > 1e-9:
        return False
    return abs(a.x - b.x) <= AXIS_TOLERANCE and abs(a.y - b.y) <= AXIS_TOLERANCE


def overlap(a: Placed, b: Placed) -> float:
    """How much two faces share along their common axis, mm (negative: the gap)."""
    (a0, a1), (b0, b1) = _span(a), _span(b)
    return min(a1, b1) - max(a0, b0)


# -- W9b: a sleeve's bands (ISSUE-1-PLAN §2.4, K10; W9B-INTERFACES §2) -------------------------------------------------

START, END = "start", "end"          # a band's word; "" for an unbanded sleeve's whole face


def bands(gear: Gear) -> Optional[Tuple[float, float]]:
    """A sleeve's ``(start band, end band)`` in mm, or None when it has none, or when they do not read as two
    positive lengths that leave a relief (the kind's own errors say so at their cells)."""
    texts = (gear.start_band.strip(), gear.end_band.strip())
    if not any(texts):
        return None
    try:
        b1, b2 = (float(t.replace("\u2212", "-")) for t in texts)
        face = float(gear.face_width)
    except ValueError:
        return None
    if b1 <= 0 or b2 <= 0 or b1 + b2 >= face:
        return None
    return b1, b2


def band_spans(gear: Gear, p: Placed) -> Tuple[Tuple[str, float, float], ...]:
    """Where a sleeve's toothed bands stand along global z as placed, ``(word, low, high)``: an unbanded sleeve's one
    span is its whole face (word ``""``); a banded one's start band at its face's start (its part's front face, the
    end toward its shaft's Axis minus side) and its end band at the other end, start band first."""
    z0, z1 = _span(p)
    held = bands(gear) if gear.kind_word() == SLEEVE else None
    if held is None:
        return (("", z0, z1),)
    b1, b2 = held
    if p.sigma >= 0:
        return ((START, z0, z0 + b1), (END, z1 - b2, z1))
    return ((START, z1 - b1, z1), (END, z0, z0 + b2))


def _band_owner(sleeve: str, word: str) -> str:
    """``RangeSlv`` for a whole face, ``RangeSlv's start band`` for a band."""
    return f"{sleeve}'s {word} band" if word else sleeve


def _between(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """How much two spans share (negative: the gap)."""
    return min(a[1], b[1]) - max(a[0], b[0])


def hub_sleeve(spec: GearboxSpec, hub: Gear) -> Optional[Gear]:
    """The sleeve a hub carries (W9B-INTERFACES §3): the sleeve on its shaft whose bands, over its positions, overlap
    the hub; the first sleeve on that shaft when none does; None with no sleeve there."""
    on = [g for g in spec.gears if g.kind_word() == SLEEVE and g.shaft == hub.shaft and g.id]
    if not on:
        return None
    try:
        h_at, h_face = float(hub.at or 0), float(hub.face_width)
    except ValueError:
        return on[0]
    for s in on:
        try:
            offsets = list(s.positions().values()) or [0.0]
            at, face = float(s.at or 0), float(s.face_width)
        except ValueError:
            continue
        lo, hi = at - face / 2.0 + min(offsets), at + face / 2.0 + max(offsets)
        if min(hi, h_at + h_face / 2.0) - max(lo, h_at - h_face / 2.0) > COVER_TOLERANCE:
            return s
    return on[0]


@dataclass
class Engagement:
    """What one mode engages: ``engaged`` (sleeve, dog) pairs, dogs in Gears-sheet order; ``out_of_mesh`` listed
    meshes a slide takes out of mesh; ``diagnostics`` its errors and warnings, each naming ``where`` (the mode's
    cell, or the gear's when there is no Modes row)."""

    engaged: List[Tuple[str, str]] = field(default_factory=list)
    out_of_mesh: List[Tuple[str, str]] = field(default_factory=list)
    diagnostics: List[Diagnostic] = field(default_factory=list)


def _pressure_angle(spec: GearboxSpec, gear: Gear) -> float:
    return float(gear.spec_values(spec.box)["pressure_angle"] or 20)


def engagement(spec: GearboxSpec, placed: Dict[str, Placed], picks: Picks) -> Engagement:
    """Engagement in one mode (W8-PLAN §1.3, J4), from every gear as placed there (``placed``: the layout's with
    this mode's sliders). The teeth-match check reads each row's pressure angle through ``Gear.spec_values`` (the
    row's, else the Box's)."""
    out = Engagement()
    gears = {g.id: g for g in spec.gears}
    where = spec.cell("Modes", picks.row, "name") if picks.row else ""
    label = f"in {picks.name} " if picks.name else ""
    sleeves = [p for p in placed.values() if gears.get(p.row or p.gear) is not None
               and gears[p.row or p.gear].kind_word() == SLEEVE]
    dogs = [p for g in spec.gears if g.kind_word() == DOG for p in [placed.get(g.id)] if p is not None]
    for d in dogs:
        for s in sleeves:
            if not _coaxial(s, d):
                continue
            touched = [(word, _between((lo, hi), _span(d))) for word, lo, hi in band_spans(gears[s.gear], s)]
            touched = [(word, share) for word, share in touched if share > COVER_TOLERANCE]
            if not touched:
                continue                           # W9b: a dog under the relief touches no band, and is not engaged
            cell = where or spec.cell("Gears", gears[s.gear].row, "id")
            if s.shaft == d.shaft:
                out.diagnostics.append(Diagnostic(WARNING, f"{cell}: {label}{s.gear} covers {d.gear} on their own "
                                                           f"shaft, {s.shaft}, and engages nothing there.", cell))
                continue
            gs, gd = gears[s.gear], gears[d.gear]
            if (s.teeth, s.module) != (d.teeth, d.module) or abs(_pressure_angle(spec, gs)
                                                                   - _pressure_angle(spec, gd)) > 1e-9:
                out.diagnostics.append(Diagnostic(ERROR, f"{cell}: {label}{s.gear} ({s.teeth} teeth, module "
                                                         f"{_n(s.module)}) cannot engage {d.gear} ({d.teeth} teeth, "
                                                         f"module {_n(d.module)}): a sleeve and the dog it engages "
                                                         "have the same teeth, module and pressure angle.", cell))
                continue
            for word, share in touched:
                if share >= d.face - COVER_TOLERANCE:
                    if (s.gear, d.gear) not in out.engaged:
                        out.engaged.append((s.gear, d.gear))
                else:
                    out.diagnostics.append(Diagnostic(ERROR, f"{cell}: {label}{_band_owner(s.gear, word)} covers "
                                                             f"{_n(share)} mm of {d.gear}'s {_n(d.face)} mm face: a "
                                                             "sleeve engages a dog only over its whole face; move the "
                                                             "position on or off it.", cell))
    moving = set(picks.positions)
    for mesh in spec.meshes:
        if mesh.a not in moving and mesh.b not in moving:
            continue
        a, b = placed.get(mesh.a), placed.get(mesh.b)
        if a is None or b is None:
            continue
        share = overlap(a, b)
        narrower = min(a.face, b.face)
        if share >= narrower - COVER_TOLERANCE:
            continue
        if share <= COVER_TOLERANCE:
            out.out_of_mesh.append((mesh.a, mesh.b))
            continue
        cell = where or spec.cell("Meshes", mesh.row, "a")
        out.diagnostics.append(Diagnostic(ERROR, f"{cell}: {label}{mesh.a} and {mesh.b} share {_n(share)} mm of "
                                                 f"their {_n(narrower)} mm face: a sliding gear is in mesh over the "
                                                 "whole narrower face or out of it.", cell))
    return out


def _n(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def slider_of(spec: GearboxSpec, gear_id: str) -> Optional[Gear]:
    gear = spec.gear(gear_id)
    return gear if gear is not None and gear.slides.strip() else None


def row_errors(spec: GearboxSpec) -> List[Diagnostic]:
    """The rows' own W8 errors, each at its cell (W8-PLAN §0.1): a sleeve or dog listed on Meshes (a sleeve engages
    a dog by sliding over it, worked out per mode); a dog with Slides; and what this version does not build — a
    slider, sleeve or dog on a fixed shaft, on a turned axis or on a shaft mounted on a carrier, a bevel gear that
    slides — said with what does build (J18: no phase named)."""
    from .geometry import axis_vector
    out: List[Diagnostic] = []
    gears = {g.id: g for g in spec.gears if g.id}
    shafts = {s.id: s for s in spec.shafts if s.id}
    for mesh in spec.meshes:
        for gid in (mesh.a, mesh.b):
            g = gears.get(gid)
            if g is not None and g.kind_word() in (SLEEVE, DOG):
                where = spec.cell("Meshes", mesh.row, "a")
                out.append(Diagnostic(ERROR, f"{where}: {gid} is a {g.kind_word()}, which is not listed on Meshes: "
                                             "a sleeve engages a dog by sliding over it, worked out for each mode.",
                                      where))
                break
            if g is not None and g.kind_word() == HUB:            # W9b
                where = spec.cell("Meshes", mesh.row, "a")
                out.append(Diagnostic(ERROR, f"{where}: {gid} is a hub, which is not listed on Meshes: a hub carries "
                                             "the sleeve on its shaft and meshes nothing.", where))
                break
    for g in spec.gears:                                           # W9b: bands are a sleeve's
        if g.kind_word() == SLEEVE:
            continue
        for key, word in (("start_band", "Start band"), ("end_band", "End band")):
            if getattr(g, key).strip():
                where = spec.cell("Gears", g.row, key)
                what = _a(g.kind_word()) if g.kind_word() in CLUTCH_KINDS else _a(f"{g.kind_word()} gear")
                out.append(Diagnostic(ERROR, f"{where}: {g.id} is {what}, and bands are a sleeve's: clear its {word}.",
                                      where))
    for g in spec.gears:                                           # W9b: a hub's own rules (K8)
        if g.kind_word() != HUB or not g.id:
            continue
        if g.slides.strip():
            continue                                               # said below, as a dog's
        sleeve = hub_sleeve(spec, g)
        if sleeve is None:
            if g.shaft in shafts:
                where = spec.cell("Gears", g.row, "kind")
                out.append(Diagnostic(ERROR, f"{where}: {g.id} is a hub, which carries a sleeve on its own shaft, and "
                                             f"no sleeve is on {g.shaft}.", where))
            continue
        try:
            same = ((int(float(g.teeth)), float(g.module)) == (int(float(sleeve.teeth)), float(sleeve.module))
                    and abs(_pressure_angle(spec, g) - _pressure_angle(spec, sleeve)) <= 1e-9)
        except ValueError:
            continue
        if not same:
            where = spec.cell("Gears", g.row, "teeth")
            out.append(Diagnostic(ERROR, f"{where}: {g.id} carries {sleeve.id} on its teeth, so it has {sleeve.id}'s "
                                         f"teeth, module and pressure angle ({sleeve.teeth} teeth, module "
                                         f"{sleeve.module}).", where))
    for g in spec.gears:
        kind = g.kind_word()
        moving = bool(g.slides.strip())
        if kind in (DOG, HUB) and moving:
            where = spec.cell("Gears", g.row, "slides")
            out.append(Diagnostic(ERROR, f"{where}: {g.id} is {_a(kind)}, which is fixed to its shaft: a sleeve "
                                         "slides over it, so clear its Slides.", where))
            continue
        if not (moving or kind in CLUTCH_KINDS):
            continue
        what = "slides" if moving else f"is a {kind}"
        where = spec.cell("Gears", g.row, "id")
        shaft = shafts.get(g.shaft)
        if kind == "bevel":
            out.append(Diagnostic(ERROR, f"{where}: {g.id} is a bevel gear that slides, which is not built by this "
                                         "version of the app; a sliding gear is spur, helical or herringbone.", where))
            continue
        if shaft is None:
            continue
        try:
            axis = axis_vector(shaft.axis)
        except ValueError:
            continue
        if shaft.mount() != "frame":
            out.append(Diagnostic(ERROR, f"{where}: {g.id} {what} on {shaft.id}, which rides a carrier, and that is not "
                                         "built by this version of the app; a slider, sleeve or dog is built on a "
                                         "frame shaft.", where))
        elif axis not in ((0.0, 0.0, 1.0), (0.0, 0.0, -1.0)):
            out.append(Diagnostic(ERROR, f"{where}: {g.id} {what} on {shaft.id}, whose axis is {shaft.axis}, and that "
                                         "is not built by this version of the app; a slider, sleeve or dog is built "
                                         "on a shaft along Z+ or Z-.", where))
        elif shaft.role == "fixed":
            out.append(Diagnostic(ERROR, f"{where}: {g.id} {what} on {shaft.id}, which is fixed, and that is not built "
                                         "by this version of the app; a slider, sleeve or dog is built on a shaft that "
                                         "turns.", where))
    return out


def _n(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def _a(kind: str) -> str:
    """``a dog``, ``a hub``, ``an internal …``: the kind word with its article."""
    return f"an {kind}" if kind[:1] in "aeiou" else f"a {kind}"


def _listed(items: List[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def mode_checks(spec: GearboxSpec, placed: Dict[str, Placed], reports) -> List[Diagnostic]:
    """The checks across modes (W8-PLAN §1.5, J22), each at its cell, from the layout (``placed``: sliders at the
    first mode's place) and every mode worked out (``reports``: ``checks.ModeReport``s). *Errors:* two sliders on
    one shaft overlapping in a mode. *Warnings:* a dog no mode engages; a listed sliding mesh in mesh in no mode; a
    sleeve longer than the gap between two dogs within its travel; two modes that engage the same."""
    out: List[Diagnostic] = []
    if not reports:
        return out
    gears = {g.id: g for g in spec.gears}
    moving = [g.id for g in sliders(spec) if g.id in placed]
    for m in reports:                                        # J22: two sliders on one shaft overlap
        where = spec.cell("Modes", m.row, "name") if m.row else ""
        here = {g: m.placed.get(g, placed[g]) for g in moving}
        said = set()
        for i, a in enumerate(moving):
            for b in moving[i + 1:]:
                pa, pb = here[a], here[b]
                if pa.shaft != pb.shaft or (a, b) in said or overlap(pa, pb) <= 0.0:
                    continue
                said.add((a, b))
                cell = where or spec.cell("Gears", gears[b].row, "slides")
                label = f"in {m.name} " if m.name else ""
                out.append(Diagnostic(ERROR, f"{cell}: {label}{a} and {b} overlap by {_n(overlap(pa, pb))} mm on "
                                             f"{pa.shaft}: two sliders on one shaft must stay clear of each other.",
                                      cell))
    engaged = {d for m in reports for _, d in m.engaged}
    for g in spec.gears:                                     # a dog no mode engages
        if g.kind_word() == DOG and g.id in placed and g.id not in engaged:
            cell = spec.cell("Gears", g.row, "id")
            out.append(Diagnostic(WARNING, f"{cell}: no mode engages {g.id}: no sleeve covers its face in any mode.",
                                  cell))
    for mesh in spec.meshes:                                 # a sliding mesh in mesh in no mode
        if mesh.a not in moving and mesh.b not in moving:
            continue
        if all((mesh.a, mesh.b) in m.out_of_mesh for m in reports):
            cell = spec.cell("Meshes", mesh.row, "a")
            slider = mesh.a if mesh.a in moving else mesh.b
            other = mesh.b if slider == mesh.a else mesh.a
            out.append(Diagnostic(WARNING, f"{cell}: {mesh.a} and {mesh.b} are in mesh in no mode: no position of "
                                           f"{slider} brings it over {other}.", cell))
    shafts = {s.id: s for s in spec.shafts}
    for gid in moving:                                       # J22: a stroke that bridges two dogs
        gear = gears[gid]
        if gear.kind_word() != SLEEVE or gear.shaft not in shafts:
            continue
        try:
            positions = gear.positions()
        except ValueError:
            continue
        if len(positions) < 2:
            continue
        low = min(positions, key=lambda p: positions[p])
        high = max(positions, key=lambda p: positions[p])
        ends = [_place(spec, replace(gear, at=repr(float(gear.at or 0) + positions[p])), shafts[gear.shaft])
                for p in (low, high)]
        # W9b: per band (an unbanded sleeve is one band, its whole face, as W8 judged it).
        for index, (word, _lo, _hi) in enumerate(band_spans(gear, ends[0])):
            spans = [band_spans(gear, e)[index] for e in ends]
            swept = (min(b[1] for b in spans), max(b[2] for b in spans))
            length = spans[0][2] - spans[0][1]
            dogs = sorted((placed[g.id] for g in spec.gears if g.kind_word() == DOG and g.id in placed
                           and _coaxial(placed[g.id], placed[gid])
                           and min(swept[1], _span(placed[g.id])[1]) - max(swept[0], _span(placed[g.id])[0]) > 0),
                          key=lambda p: _span(p)[0])
            for d1, d2 in zip(dogs, dogs[1:]):
                gap = _span(d2)[0] - _span(d1)[1]
                if length > gap:
                    cell = spec.cell("Gears", gear.row, "slides")
                    out.append(Diagnostic(WARNING, f"{cell}: {_band_owner(gid, word)} is {_n(length)} mm long and "
                                                   f"{d1.gear} and {d2.gear} are {_n(gap)} mm apart: on its way from "
                                                   f"{low} to {high} it would hold both at once.", cell))
    seen: Dict[Tuple[frozenset, frozenset], str] = {}         # two modes that engage the same
    for m in reports:
        if not m.name:
            continue
        key = (frozenset(m.engaged), frozenset(frozenset(p) for p in m.out_of_mesh))
        if key in seen:
            cell = spec.cell("Modes", m.row, "name")
            out.append(Diagnostic(WARNING, f"{cell}: {seen[key]} and {m.name} engage the same: they are one mode "
                                           "twice.", cell))
        else:
            seen[key] = m.name
    return out


def _covers(a: Tuple[float, float], b: Tuple[float, float]) -> bool:
    """Whether span ``a`` holds span ``b`` whole, to :data:`COVER_TOLERANCE`."""
    return a[0] <= b[0] + COVER_TOLERANCE and a[1] >= b[1] - COVER_TOLERANCE


def hub_errors(spec: GearboxSpec, placed: Dict[str, Placed], reports) -> List[Diagnostic]:
    """W9b (ISSUE-1-PLAN §2.2, K8; W9B-INTERFACES §3): in every mode a band of a hub's sleeve covers the hub whole, or
    the hub the band (the narrower covered), else an error at that mode's Modes cell (the hub's Gears cell for the
    implicit mode of sliders with no Modes rows). ``placed``: the layout's; ``reports``: ``checks.ModeReport``s."""
    out: List[Diagnostic] = []
    for hub in spec.gears:
        if hub.kind_word() != HUB or hub.id not in placed or hub.slides.strip():
            continue
        sleeve = hub_sleeve(spec, hub)
        if sleeve is None or sleeve.id not in placed:
            continue
        under = _span(placed[hub.id])
        for m in reports or ():
            here = m.placed.get(sleeve.id, placed[sleeve.id])
            spans = band_spans(sleeve, here)
            if any(_covers((lo, hi), under) or _covers(under, (lo, hi)) for _, lo, hi in spans):
                continue
            cell = spec.cell("Modes", m.row, "name") if m.row else spec.cell("Gears", hub.row, "id")
            label = f"in {m.name} " if m.name else ""
            if spans[0][0]:
                said = (f"{label}{hub.id} is under no band of {sleeve.id}: in every mode a band of the sleeve covers "
                        f"its hub whole, or the hub the band; move {hub.id}, or the bands.")
            else:
                said = (f"{label}{sleeve.id} and {hub.id} do not cover one another: in every mode a sleeve covers its "
                        f"hub whole, or the hub the sleeve; move {hub.id}.")
            out.append(Diagnostic(ERROR, f"{cell}: {said}", cell))
    return out


# -- W9b package A: the sleeve checks (ISSUE-1-PLAN §2.2, §2.3; K7, K8, K9; W9B-INTERFACES §6) ---------------------

RUNNING_FLOOR = 0.5             # mm: the least running clearance, at any module
RUNNING_MODULES = 0.5           # × module: the running clearance a side, above the floor


def running_clearance(module: float) -> float:
    """K9: the least axial gap between a sleeve's toothed band and a dog or hub it does not engage, c = max(0.5 mm,
    0.5 × module): 0.625 mm at module 1.25."""
    return max(RUNNING_FLOOR, RUNNING_MODULES * module)


def _why_clearance(module: float) -> str:
    return "0.5 × module" if RUNNING_MODULES * module >= RUNNING_FLOOR else "the least at any module"


def _signed(value: float) -> str:
    """``+5``, ``−5`` (U+2212), ``0``: an offset or an At as the sentences write it."""
    if abs(value) < 1e-12:
        return "0"
    return ("+" if value > 0 else "\u2212") + _n(abs(value))


def _at_text(gear: Gear) -> str:
    try:
        value = float(gear.at or 0)
    except ValueError:
        return gear.at
    return "\u2212" + _n(-value) if value < 0 else _n(value)


def _frame_line(spec: GearboxSpec, shaft_id: str) -> Optional[Tuple[float, float]]:
    """A frame shaft along Z+ or Z-: its (x, y); None for any other (a sleeve's checks look along Z only)."""
    from .geometry import axis_vector
    shaft = spec.shaft(shaft_id)
    if shaft is None or shaft.mount() != "frame":
        return None
    try:
        axis = axis_vector(shaft.axis)
        point = (float(shaft.x or 0), float(shaft.y or 0))
    except ValueError:
        return None
    if axis not in ((0.0, 0.0, 1.0), (0.0, 0.0, -1.0)):
        return None
    return point


def _on_line(a: Optional[Tuple[float, float]], b: Optional[Tuple[float, float]]) -> bool:
    return a is not None and b is not None and abs(a[0] - b[0]) <= AXIS_TOLERANCE and abs(a[1] - b[1]) <= AXIS_TOLERANCE


def _sleeve_places(spec: GearboxSpec, gear: Gear) -> List[Placed]:
    """A sleeve placed at each of its Slides positions in their order (once, where it stands, with no Slides)."""
    shaft = spec.shaft(gear.shaft)
    if shaft is None:
        return []
    try:
        offsets = list(gear.positions().values()) or [0.0]
        at = float(gear.at or 0)
    except ValueError:
        return []
    return [_place(spec, replace(gear, at=repr(at + offset)), shaft) for offset in offsets]


def _owners(spec: GearboxSpec, placed: Dict[str, Placed]) -> Dict[str, List[Tuple[Gear, float, float]]]:
    """Every frame shaft along Z and the gears that make it present (§2.2): its own gears that do not slide, and a
    carrier's planets as its gears (a copy counted once, under its row); each ``(row, low, high)``, Gears-sheet
    order."""
    gears = {g.id: g for g in spec.gears}
    out: Dict[str, List[Tuple[Gear, float, float]]] = {}
    seen = set()
    for g in spec.gears:
        for p in placed.values():
            if (p.row or p.gear) != g.id or g.slides.strip():
                continue
            owner = p.carrier or p.shaft
            if (owner, g.id) in seen:
                continue
            seen.add((owner, g.id))
            lo, hi = _span(p)
            out.setdefault(owner, []).append((gears[g.id], lo, hi))
    return out


def _blocked(present: List[Tuple[Gear, float, float]], point: float, below: bool) -> Optional[Gear]:
    """§2.2: a shaft present across ``point`` (its gears' hull holds it with more than ``COVER_TOLERANCE`` to spare
    each side) with a gear reaching past it, below (toward Z−) or above; the gear nearest the point, else None."""
    lo = min(g[1] for g in present)
    hi = max(g[2] for g in present)
    if not (lo < point - COVER_TOLERANCE and hi > point + COVER_TOLERANCE):
        return None
    if below:
        past = [g for g in present if g[1] < point - COVER_TOLERANCE]
        return max(past, key=lambda g: g[2])[0] if past else None
    past = [g for g in present if g[2] > point + COVER_TOLERANCE]
    return min(past, key=lambda g: g[1])[0] if past else None


def _hubs_of(spec: GearboxSpec, sleeve: Gear) -> List[Gear]:
    return [g for g in spec.gears if g.kind_word() == HUB and not g.slides.strip()
            and hub_sleeve(spec, g) is not None and hub_sleeve(spec, g).id == sleeve.id]


def reach_warnings(spec: GearboxSpec, placed: Dict[str, Placed]) -> List[Diagnostic]:
    """K7 (§2.2): a sleeve S on shaft O whose every way in is blocked, a warning at S's Gears cell. From Z− O must
    reach p− (the largest start of S's places; the hub's start with a hub), from Z+ p+ (the smallest end; the hub's
    end); an end is blocked when another shaft on O's line is present across that point and has a gear reaching past
    it. With bands and no hub each band is tried in place of the whole face, and the warning stands only when every
    band is blocked both ways."""
    out: List[Diagnostic] = []
    owners = _owners(spec, placed)
    order = [s.id for s in spec.shafts]
    for sleeve in spec.gears:
        if sleeve.kind_word() != SLEEVE or sleeve.id not in placed:
            continue
        line = _frame_line(spec, sleeve.shaft)
        others = [sid for sid in order if sid != sleeve.shaft and sid in owners and _on_line(line,
                                                                                            _frame_line(spec, sid))]
        if line is None or not others:
            continue
        hubs = [h for h in _hubs_of(spec, sleeve) if h.id in placed]
        if hubs:
            candidates = [_span(placed[hubs[0].id])]
        else:
            places = [band_spans(sleeve, p) for p in _sleeve_places(spec, sleeve)]
            if not places:
                continue
            candidates = [(max(p[i][1] for p in places), min(p[i][2] for p in places)) for i in range(len(places[0]))]
        found = []
        for p_minus, p_plus in candidates:
            minus = [(sid, _blocked(owners[sid], p_minus, True)) for sid in others]
            plus = [(sid, _blocked(owners[sid], p_plus, False)) for sid in others]
            minus = [(sid, g) for sid, g in minus if g is not None]
            plus = [(sid, g) for sid, g in plus if g is not None]
            if not minus or not plus:
                found = []
                break
            found.append((minus, plus))
        if not found:
            continue
        minus, plus = found[0]
        both = [sid for sid, _ in minus if sid in {s for s, _ in plus}]
        cell = spec.cell("Gears", sleeve.row, "id")
        if both:
            shaft = both[0]
            low, high = dict(minus)[shaft], dict(plus)[shaft]
            rows = {g.id: i for i, g in enumerate(spec.gears)}
            first, second = sorted({low.id: low, high.id: high}.values(), key=lambda g: rows[g.id]) + \
                ([] if low.id != high.id else [high])
            said = (f"{sleeve.shaft} cannot reach {sleeve.id}: {shaft} runs through {sleeve.id}'s travel (from "
                    f"{first.id} at {_at_text(first)} to {second.id} at {_at_text(second)}), so {sleeve.shaft} would "
                    f"have to pass {low.id} toward Z\u2212 or {high.id} toward Z+, each on {shaft}.")
        else:
            (s_low, low), (s_high, high) = minus[0], plus[0]
            said = (f"{sleeve.shaft} cannot reach {sleeve.id}: {s_low} and {s_high} run through {sleeve.id}'s travel, "
                    f"so {sleeve.shaft} would have to pass {low.id} on {s_low} toward Z\u2212 or {high.id} on {s_high} "
                    "toward Z+.")
        out.append(Diagnostic(WARNING, f"{cell}: {said}", cell))
    return out


def _free_length(span: Tuple[float, float], taken: List[Tuple[float, float]]) -> float:
    """The longest stretch of ``span`` that none of ``taken`` overlaps."""
    lo, hi = span
    if hi - lo <= COVER_TOLERANCE:
        return 0.0
    best, at = 0.0, lo
    for a, b in sorted(t for t in taken if min(t[1], hi) - max(t[0], lo) > COVER_TOLERANCE):
        best = max(best, min(a, hi) - at)
        at = max(at, b)
    return max(best, hi - at)


def hub_warnings(spec: GearboxSpec, placed: Dict[str, Placed]) -> List[Diagnostic]:
    """K8 (§2.2): a sleeve with no hub row of its own, a warning at its Gears cell; and when, as laid out, no hub could
    be under a band of it in every mode — none inside what every place of one band shares, clear of the gears of the
    other shafts on its line, and none covering one band's whole travel clear of them — it says so and why."""
    out: List[Diagnostic] = []
    owners = _owners(spec, placed)
    for sleeve in spec.gears:
        if sleeve.kind_word() != SLEEVE or sleeve.id not in placed or _hubs_of(spec, sleeve):
            continue
        line = _frame_line(spec, sleeve.shaft)
        taken = [(lo, hi) for sid, present in owners.items() if sid != sleeve.shaft
                 and _on_line(line, _frame_line(spec, sid)) for _, lo, hi in present]
        places = [band_spans(sleeve, p) for p in _sleeve_places(spec, sleeve)]
        banded = bool(places) and bool(places[0][0][0])
        fits = not places
        for i in range(len(places[0]) if places else 0):
            shared = (max(p[i][1] for p in places), min(p[i][2] for p in places))
            travel = (min(p[i][1] for p in places), max(p[i][2] for p in places))
            inside = _free_length(shared, taken) > COVER_TOLERANCE
            around = not any(min(t[1], travel[1]) - max(t[0], travel[0]) > COVER_TOLERANCE for t in taken)
            fits = fits or inside or around
        cell = spec.cell("Gears", sleeve.row, "id")
        if banded:
            said = (f"nothing keys {sleeve.id} to {sleeve.shaft}: no hub row is under it; add a hub on {sleeve.shaft} "
                    f"that a band of {sleeve.id} covers in every mode")
        else:
            said = (f"nothing keys {sleeve.id} to {sleeve.shaft}: its whole bore is teeth and no hub row is under it; "
                    f"add a hub on {sleeve.shaft} that a band of {sleeve.id} covers in every mode")
        if not fits:
            said += "; as laid out none can, since " + _why_none(sleeve, places, banded)
        out.append(Diagnostic(WARNING, f"{cell}: {said}.", cell))
    return out


def _why_none(sleeve: Gear, places, banded: bool) -> str:
    if banded:
        return ("what every place of each band shares is too short or taken, and each band's travel holds a gear of "
                "another shaft")
    try:
        positions = sleeve.positions()
        face = float(sleeve.face_width)
    except ValueError:
        return "its places share no length clear of the other shafts' gears"
    if not positions:
        return "what it stands over is taken by another shaft's gear"
    low = min(positions, key=lambda p: positions[p])
    high = max(positions, key=lambda p: positions[p])
    shared = max(p[0][1] for p in places), min(p[0][2] for p in places)
    tail = ("its places share no length" if shared[1] - shared[0] <= COVER_TOLERANCE
            else "the length its places share is taken by another shaft's gear")
    return (f"its {_n(face)} mm face slides {_n(positions[high] - positions[low])} mm ({low} {_signed(positions[low])} "
            f"to {high} {_signed(positions[high])}) and {tail}")


def clearance_warnings(spec: GearboxSpec, placed: Dict[str, Placed], reports) -> List[Diagnostic]:
    """K9 (§2.3): in every mode, every dog or hub on another shaft on a sleeve's line that no band of it engages there,
    standing less than c (:func:`running_clearance`) from a band (0 ≤ gap < c), one warning per mode and sleeve at the
    mode's Modes cell (the sleeve's Gears cell for the implicit mode); and, once, a hub less than c from a dog on
    another shaft, at the hub's Gears cell. A gap of exactly c is clean."""
    out: List[Diagnostic] = []
    gears = {g.id: g for g in spec.gears}
    near = [g for g in spec.gears if g.kind_word() in (DOG, HUB) and g.id in placed and not g.slides.strip()]
    for m in reports or ():
        for sleeve in spec.gears:
            if sleeve.kind_word() != SLEEVE or sleeve.id not in placed:
                continue
            here = m.placed.get(sleeve.id, placed[sleeve.id])
            spans = band_spans(sleeve, here)
            c = running_clearance(here.module)
            found: List[Tuple[str, str, float]] = []
            for d in near:
                p = placed[d.id]
                if p.shaft == here.shaft or not _coaxial(p, here) or (sleeve.id, d.id) in m.engaged:
                    continue
                shares = [_between((lo, hi), _span(p)) for _, lo, hi in spans]
                if any(share > COVER_TOLERANCE for share in shares):
                    continue                                    # over it: engaged, or engagement's own error
                for (word, _, _), share in zip(spans, shares):
                    gap = max(0.0, -share)
                    if gap < c - 1e-9:
                        found.append((word, d.id, gap))
            if not found:
                continue
            cell = spec.cell("Modes", m.row, "name") if m.row else spec.cell("Gears", sleeve.row, "id")
            label = f"in {m.name} " if m.name else ""
            pieces = []
            for word, _lo, _hi in spans:
                these = [f"{_n(gap)} mm from {d}" for w, d, gap in found if w == word]
                if not these:
                    continue
                what = (f"{_band_owner(sleeve.id, word)} stands" if not pieces else f"its {word} band")
                pieces.append(f"{what} {' and '.join(these)}")
            said = (f"{label}{', and '.join(pieces)}, which it does not engage there: leave at least {_n(c)} mm "
                    f"({_why_clearance(here.module)}) each side.")
            out.append(Diagnostic(WARNING, f"{cell}: {said}", cell))
    for hub in spec.gears:
        if hub.kind_word() != HUB or hub.id not in placed or hub.slides.strip():
            continue
        h = placed[hub.id]
        for d in spec.gears:
            if d.kind_word() != DOG or d.id not in placed:
                continue
            p = placed[d.id]
            if p.shaft == h.shaft or not _coaxial(p, h):
                continue
            gap = -_between(_span(h), _span(p))
            module = max(h.module, p.module)
            c = running_clearance(module)
            if -COVER_TOLERANCE <= gap < c - 1e-9:
                cell = spec.cell("Gears", gears[hub.id].row, "id")
                out.append(Diagnostic(WARNING, f"{cell}: {hub.id} stands {_n(max(0.0, gap))} mm from {d.id}, on "
                                               f"another shaft: leave at least {_n(c)} mm ({_why_clearance(module)}) "
                                               "between them.", cell))
    return out
