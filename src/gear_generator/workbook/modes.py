"""A workbook's modes: where each slider sits in each mode, and what each mode engages (phase W8; W8-PLAN §1.2-§1.3).

Pure. The one home of three rules: a mode's picks (a blank pick is the slider's position at 0, J5; with sliders and
no Modes rows there is one implicit mode, every slider at its 0); a slider's place in a mode (its face centre at
``point + (At + offset) × axis``); and engagement (J4): a sleeve engages a dog on another shaft on its axis exactly
when it covers the dog's whole face — partial cover is an error, teeth that do not match while they overlap at all
an error — and a sliding mesh is in mesh when the narrower face is covered, out with no overlap, an error between.

A coupling is never a gear mesh: it does not go through ``checks._check_mesh``, ``checks.internal_working_centre``
or the ring's tip check (equal teeth at centre distance 0 would be refused by each), and sleeves and dogs listed on
Meshes are errors of their own (``checks``), so none of those is ever called on one.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Tuple

from ..gears.base import ERROR, WARNING, Diagnostic
from .geometry import Placed, _place
from .model import GearboxSpec, Gear

SLEEVE, DOG = "sleeve", "dog"
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
            if pick not in positions:
                continue                                  # the read's error (model): a pick not among the positions
            picks[gid] = (pick, float(positions[pick]))
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
            share = overlap(s, d)
            if share <= COVER_TOLERANCE:
                continue
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
            if share >= d.face - COVER_TOLERANCE:
                out.engaged.append((s.gear, d.gear))
            else:
                out.diagnostics.append(Diagnostic(ERROR, f"{cell}: {label}{s.gear} covers {_n(share)} mm of "
                                                         f"{d.gear}'s {_n(d.face)} mm face: a sleeve engages a dog "
                                                         "only over its whole face; move the position on or off "
                                                         "it.", cell))
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
    for g in spec.gears:
        kind = g.kind_word()
        moving = bool(g.slides.strip())
        if kind == DOG and moving:
            where = spec.cell("Gears", g.row, "slides")
            out.append(Diagnostic(ERROR, f"{where}: {g.id} is a dog, which is fixed to its shaft: a sleeve slides "
                                         "over it, so clear its Slides.", where))
            continue
        if not (moving or kind in (SLEEVE, DOG)):
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
