"""A workbook's planetary stage: copies, the stage recognised, its checks' numbers (phase W7; W7-PLAN §2.1-§2.3).

Pure. A planetary stage is written with the rows PLAN-WORKBOOK §1 already has: a carrier is a frame shaft another
shaft is ``Mounted on``; a planet shaft's X, Y, Z are read in its carrier's own frame at the carrier's starting turn,
and its ``Copies`` stand evenly round the carrier's axis. This module names the copies and works out their offsets
(written at W7's interface commit, with tests, because geometry, the carrier part, the mates and the record all rest
on them), and recognises the stage (Agent B).

Interfaces pinned in the W7 interface commit (``docs/notes-workbook/W7-INTERFACES.md``); a body not yet written
raises a ValueError with a full sentence, as a planning refusal does.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ..gears.base import ERROR, Diagnostic
from .model import GearboxSpec, Shaft
from .schema import FRAME

COPY_WORD = " copy "          # "Planet copy 2": a space is not allowed in a workbook name, so no copy id is a name


def copy_id(name: str, k: int, copies: int) -> str:
    """The id of copy ``k`` (1 … ``copies``) of a gear or shaft called ``name`` (W7-PLAN §2.1, reading J3): ``name``
    itself when ``copies`` is 1, else ``"<name> copy <k>"`` (``"Planet copy 2"``, ``"P copy 2"``). A workbook name
    holds no space (``schema.NAME_PATTERN``), so a copy id never equals a gear's or a shaft's own. A ``k`` outside
    1 … ``copies``, ``copies`` below 1, or no name is a ValueError."""
    if not name:
        raise ValueError("A copy needs the name of the gear or shaft it is a copy of.")
    if int(copies) < 1:
        raise ValueError(f"{name} has {copies} copies; it has at least one.")
    if not 1 <= int(k) <= int(copies):
        raise ValueError(f"{name} has {copies} {'copy' if copies == 1 else 'copies'}, so there is no copy {k}.")
    return name if int(copies) == 1 else f"{name}{COPY_WORD}{int(k)}"


def copy_of(copy: str) -> Tuple[str, int]:
    """``(name, k)`` back from a copy id: ``"Planet copy 2"`` → ``("Planet", 2)``; a name with no copy word →
    ``(name, 0)`` (Copies 1: ``ComponentEntry.of`` is then ``""``)."""
    head, word, tail = copy.rpartition(COPY_WORD)
    if word and head and tail.isdigit():
        return head, int(tail)
    return copy, 0


def copy_offsets(x: float, y: float, z: float, copies: int) -> Tuple[Tuple[float, float, float], ...]:
    """Each copy's point IN THE CARRIER'S OWN FRAME (W7-PLAN §2.1): copy k (1 … N) is copy 1 turned ``ψ_k = (k −
    1)·360/N`` degrees about the carrier's own +Z, ``rot_z(ψ_k)·(x, y, z)``; copy 1 is the typed point exactly.
    Each coordinate is rounded to 1e-12 mm (so ``(18, 0, 0)`` in 3 gives ``(-9.0, 15.58845726812, 0.0)``, and a
    quarter turn lands on 0 exactly), with no ``-0.0``. The carrier part holds these as they are, on either sense of
    carrier; the world point is ``p_c + base_frame(a_c)·offset`` (W7-INTERFACES.md §3)."""
    n = int(copies)
    if n < 1:
        raise ValueError(f"A planet shaft has at least one copy, not {copies}.")
    out = []
    for k in range(n):
        psi = math.radians(k * 360.0 / n)
        c, s = math.cos(psi), math.sin(psi)
        point = (x * c - y * s, x * s + y * c, z) if k else (x, y, z)
        out.append(tuple(round(float(v), 12) + 0.0 for v in point))
    return tuple(out)


@dataclass(frozen=True)
class Stage:
    """One planetary stage, recognised from the rows (:func:`stages`; ``checks.Report.stages``). ``carrier`` the
    carrier shaft; ``sun`` and ``ring`` the gears (ids) on the frame shafts coaxial with it that mesh the planet
    outside and inside; ``planet`` the planet gear's Gears row id and ``planet_shaft`` its shaft's row id (the copies
    are ``copy_id(planet, k, copies)``); ``copies`` N; ``held`` the member SHAFT whose Role is fixed — the sun's,
    the ring's or the carrier's."""

    carrier: str
    sun: str
    ring: str
    planet: str
    planet_shaft: str
    copies: int
    held: str


COAXIAL_TOLERANCE = 0.005    # mm: two shaft lines this close (and parallel) are one line (checks.CENTRE_TOLERANCE)


def copies_of(shaft: Shaft) -> Optional[int]:
    """A shaft's Copies as a whole number (blank is 1), or None when it does not read as one of at least 1 (the
    read's error, ``model._check_references``)."""
    text = str(shaft.copies or "").strip() or "1"
    try:
        value = float(text)
    except ValueError:
        return None
    if value != int(value) or value < 1:
        return None
    return int(value)


def carriers(spec: GearboxSpec) -> List[str]:
    """The carrier shafts, in Shafts-sheet order: frame shafts another shaft is mounted on."""
    ids = {s.id for s in spec.shafts if s.id}
    mounted = {s.mount() for s in spec.shafts if s.mount() != FRAME}
    return [s.id for s in spec.shafts if s.id in mounted and s.id in ids and s.mount() == FRAME]


def _axis_word(text: str) -> str:
    return str(text or "").strip() or "Z+"


def not_laid_out(spec: GearboxSpec) -> str:
    """Why the rows cannot be laid out at all (``geometry.layout``'s ``later``; ``kinematics.solve``'s), or ``""``:
    a shaft mounted on a shaft that is itself mounted (W7-PLAN §1.2), or a planet shaft whose Axis does not lie
    along its carrier's (either way). Each is also a refusal at its cell (:func:`refusals`); this is the one home
    of both sentences. A mount the read refuses (no such shaft, a shaft on itself) is the read's error."""
    from .geometry import axis_vector
    shafts = {s.id: s for s in spec.shafts if s.id}
    for shaft in spec.shafts:
        mount = shaft.mount()
        if mount == FRAME or mount not in shafts or mount == shaft.id:
            continue
        carrier = shafts[mount]
        if carrier.mount() != FRAME:
            return _nested(shaft, carrier)
        try:
            local = axis_vector(_axis_word(shaft.axis))
        except ValueError:
            continue                                      # the read says so at the cell
        if abs(abs(local[2]) - 1.0) > 1e-9:
            return _across(shaft)
    return ""


def _nested(shaft: Shaft, carrier: Shaft) -> str:
    return (f"{shaft.id} is mounted on {carrier.id}, which is itself mounted on {carrier.mount()}: a carrier riding "
            "another carrier is not built by this version; a planet shaft is built mounted on a frame shaft.")


def _across(shaft: Shaft) -> str:
    return (f"{shaft.id}'s axis is {_axis_word(shaft.axis)} on {shaft.mount()}: a planet turns about an axis parallel "
            "to its carrier's, so this is not built by this version; leave its Axis blank to turn on its carrier's.")


def _coaxial(line_a, line_b) -> bool:
    """Two shaft lines ``(point, direction)`` that are one line, either way along it."""
    (pa, da), (pb, db) = line_a, line_b
    cross = (da[1] * db[2] - da[2] * db[1], da[2] * db[0] - da[0] * db[2], da[0] * db[1] - da[1] * db[0])
    if math.sqrt(sum(c * c for c in cross)) > 1e-9:
        return False
    d = tuple(b - a for a, b in zip(pa, pb))
    along = sum(x * y for x, y in zip(d, da))
    off = math.sqrt(max(0.0, sum(x * x for x in d) - along * along))
    return off <= COAXIAL_TOLERANCE


def coaxial(spec: GearboxSpec, a: str, b: str) -> bool:
    """Whether two frame shafts lie on one line (sun, carrier and ring of a stage; W7-PLAN §2.3 item 5)."""
    lines = _lines(spec)
    return a in lines and b in lines and _coaxial(lines[a], lines[b])


def _lines(spec: GearboxSpec):
    from .geometry import shaft_lines
    return shaft_lines(spec)


def stages(spec: GearboxSpec, placed: Optional[Dict[str, object]] = None) -> Tuple[Stage, ...]:
    """Every planetary stage of ``spec``, one per carrier in Shafts-sheet order (W7 builds one; §1.2 refuses a
    second), recognised from the rows: the carrier's first planet shaft and its first gear; the sun, a gear outside
    the planet on a frame shaft coaxial with the carrier that meshes it; the ring, a ring that meshes it on such a
    shaft (``""`` when there is none); the held member, the first of the sun's, the ring's and the carrier's shafts
    whose Role is fixed (``""`` when none is). ``placed`` is not needed: the rows say it all."""
    del placed
    shafts = {s.id: s for s in spec.shafts if s.id}
    gears = {g.id: g for g in spec.gears if g.id}
    lines = _lines(spec)
    out = []
    for carrier in carriers(spec):
        planet_shafts = [s for s in spec.shafts if s.mount() == carrier and s.id]
        if not planet_shafts:
            continue
        planet_shaft = planet_shafts[0]
        on_planet = [g for g in spec.gears if g.shaft == planet_shaft.id and g.id]
        if not on_planet:
            continue
        planet = on_planet[0]
        sun = ring = ""
        for mesh in spec.meshes:
            if planet.id not in (mesh.a, mesh.b):
                continue
            other = gears.get(mesh.b if mesh.a == planet.id else mesh.a)
            if other is None or other.shaft not in shafts or shafts[other.shaft].mount() != FRAME:
                continue
            if other.shaft == carrier or other.shaft not in lines or carrier not in lines:
                continue
            if not _coaxial(lines[other.shaft], lines[carrier]):
                continue
            if other.side == "internal":
                ring = ring or other.id
            else:
                sun = sun or other.id
        held = ""
        for member in ([gears[sun].shaft] if sun else []) + ([gears[ring].shaft] if ring else []) + [carrier]:
            if shafts[member].role == "fixed":
                held = member
                break
        out.append(Stage(carrier, sun, ring, planet.id, planet_shaft.id, copies_of(planet_shaft) or 1, held))
    return tuple(out)


def assembly_counts(z_sun: int, z_ring: int, fit: int) -> Tuple[int, ...]:
    """Every number of copies from 1 to ``fit`` that meshes with the sun and the ring at once: N dividing ``z_sun +
    z_ring`` (W7-PLAN §2.3 item 2; profile shift changes nothing, being symmetric about the space centre)."""
    total = int(z_sun) + int(z_ring)
    return tuple(n for n in range(1, int(fit) + 1) if total % n == 0)


def most_that_fit(a: float, outer_diameter: float, module: float) -> int:
    """The most copies that stand round a carrier at ``a`` mm from its axis with their tips clear: the largest N
    with ``2a·sin(π/N) >= outer_diameter + CLASH_GAP·module`` (W7-PLAN §2.3 item 3); 1 always fits."""
    from .checks import CLASH_GAP
    need = float(outer_diameter) + CLASH_GAP * float(module)
    best, n = 1, 2
    while n <= 1000 and 2.0 * float(a) * math.sin(math.pi / n) >= need - 1e-9:
        best, n = n, n + 1
    return best


def mesh_carrier(spec: GearboxSpec, a: str, b: str) -> Optional[str]:
    """What a listed mesh between gears ``a`` and ``b`` (row ids, or copy ids) is measured against (W7-PLAN §2.5):
    ``"frame"`` when both are on frame shafts; the carrier shaft's id when one is on a shaft mounted on it and the
    other on a frame shaft coaxial with it (the carrier's own shaft among them), or both on shafts mounted on that
    carrier; None when it fits no carrier (an error)."""
    gears = {g.id: g for g in spec.gears if g.id}
    shafts = {s.id: s for s in spec.shafts if s.id}
    ga, gb = gears.get(copy_of(a)[0]), gears.get(copy_of(b)[0])
    if ga is None or gb is None or ga.shaft not in shafts or gb.shaft not in shafts:
        return None
    ma, mb = shafts[ga.shaft].mount(), shafts[gb.shaft].mount()
    if ma == FRAME and mb == FRAME:
        return FRAME
    if ma != FRAME and mb != FRAME:
        return ma if ma == mb else None
    carrier, frame_shaft = (ma, gb.shaft) if ma != FRAME else (mb, ga.shaft)
    if frame_shaft == carrier:
        return carrier
    lines = _lines(spec)
    if carrier in lines and frame_shaft in lines and _coaxial(lines[carrier], lines[frame_shaft]):
        return carrier
    return None


def second_inputs(spec: GearboxSpec) -> List[Tuple[Stage, str, str]]:
    """``(stage, the first input member's shaft, a further input member's shaft)`` for every planetary stage with a
    member held and more than one member given Role input (W7-INTERFACES §6.15): its members are the sun's shaft,
    the ring's shaft and the carrier (a gear on the carrier's own shaft is on the carrier, so it shares its role).
    An input elsewhere in the train that reaches the stage through another mesh is not a member, and ordinary. A
    stage with no member held is a differential, said as one (:func:`refusals`)."""
    shafts = {x.id: x for x in spec.shafts if x.id}
    gears = {g.id: g for g in spec.gears if g.id}
    out = []
    for stage in stages(spec):
        if not stage.held:
            continue
        members = ([gears[stage.sun].shaft] if stage.sun else []) + [stage.carrier] + (
            [gears[stage.ring].shaft] if stage.ring else [])
        inputs = [x.id for x in spec.shafts if x.id in members and x.role == "input"]     # Shafts-sheet order
        out.extend((stage, inputs[0], extra) for extra in inputs[1:])
    return out


def _warn(spec: GearboxSpec, sheet: str, row: int, key: str, sentence: str) -> Diagnostic:
    where = spec.cell(sheet, row, key)
    return Diagnostic(ERROR, f"{where}: {sentence}", where)


def refusals(spec: GearboxSpec) -> List[Diagnostic]:
    """§1.2's rows of what this version does not build, each an ERROR at its cell, said by ``checks.check`` (the
    orchestrator's ruling: a planetary form this version does not build is not waiting for a later phase, so it is
    an error of the workbook, and each sentence says what does build): a carrier riding a carrier; a carrier off
    Z±; a planet facing away from its carrier or across it; a sun or ring facing the other way from its carrier; a
    stage with no member held; a second input among a stage's members (§6.15); a compound planet; a double planet; a gear on a carrier's own shaft that meshes; a
    helical or herringbone gear in a stage; a second carrier."""
    from .geometry import axis_vector
    out: List[Diagnostic] = []
    shafts = {s.id: s for s in spec.shafts if s.id}
    gears = {g.id: g for g in spec.gears if g.id}
    lines = _lines(spec)
    for shaft in spec.shafts:
        mount = shaft.mount()
        if mount == FRAME or mount not in shafts or mount == shaft.id:
            continue
        carrier = shafts[mount]
        if carrier.mount() != FRAME:
            out.append(_warn(spec, "Shafts", shaft.row, "id", _nested(shaft, carrier)))
            continue
        try:
            local = axis_vector(_axis_word(shaft.axis))
        except ValueError:
            continue
        if abs(abs(local[2]) - 1.0) > 1e-9:
            out.append(_warn(spec, "Shafts", shaft.row, "id", _across(shaft)))
        elif local[2] < 0:
            out.append(_warn(spec, "Shafts", shaft.row, "id",
                             f"{shaft.id} faces {_axis_word(shaft.axis)} on {mount}, the other way from its carrier: "
                             "a planet that faces away from its carrier is not built by this version; leave its Axis "
                             "blank to face its carrier's way."))
    found = carriers(spec)
    for index, carrier_id in enumerate(found):
        carrier = shafts[carrier_id]
        if index:
            out.append(_warn(spec, "Shafts", carrier.row, "id", f"{carrier_id} is a second carrier: one planetary "
                                                                "stage per workbook is built by this version."))
            continue
        if carrier_id in lines and lines[carrier_id][1] not in ((0.0, 0.0, 1.0), (0.0, 0.0, -1.0)):
            out.append(_warn(spec, "Shafts", carrier.row, "id", f"{carrier_id}'s axis is {_axis_word(carrier.axis)}: a "
                                                                "planetary stage is built only on an axis along Z+ or "
                                                                "Z- by this version."))
        for planet_shaft in (s for s in spec.shafts if s.mount() == carrier_id and s.id):
            on = [g.id for g in spec.gears if g.shaft == planet_shaft.id and g.id]
            if len(on) > 1:
                out.append(_warn(spec, "Shafts", planet_shaft.row, "id",
                                 f"{planet_shaft.id} carries {_and(on)}: a compound planet is not built by this "
                                 "version; a planet shaft is built with one gear."))
    for stage in stages(spec):
        carrier = shafts[stage.carrier]
        members = [g for g in (stage.sun, stage.ring) if g]
        for gear_id in members:
            shaft_id = gears[gear_id].shaft
            if shaft_id in lines and stage.carrier in lines:
                dot = sum(x * y for x, y in zip(lines[shaft_id][1], lines[stage.carrier][1]))
                if dot < 0:
                    out.append(_warn(spec, "Shafts", shafts[shaft_id].row, "id",
                                     f"{shaft_id} faces {_axis_word(shafts[shaft_id].axis)} and {stage.carrier} faces "
                                     f"{_axis_word(carrier.axis)}: a planetary stage whose shafts face different ways "
                                     f"is not built by this version; give {shaft_id} the Axis of {stage.carrier}."))
        for _stage, first, extra in (x for x in second_inputs(spec) if x[0] == stage):
            out.append(_warn(spec, "Shafts", shafts[extra].row, "role",
                             f"{extra} is an input as well as {first}, and both are members of {stage.carrier}'s "
                             f"planetary stage: one member of a planetary stage is the input; set {extra}'s Role to "
                             "output, or leave it blank."))
        if not stage.held and stage.sun and stage.ring:
            names = [gears[stage.sun].shaft] if stage.sun else []
            names += [stage.carrier] + ([gears[stage.ring].shaft] if stage.ring else [])
            out.append(_warn(spec, "Shafts", carrier.row, "id",
                             f"{_and(names)} form a planetary stage with no member held: a differential is not built "
                             "by this version; set one of them to Role fixed."))
        for gear_id in members + [stage.planet]:
            kind = gears[gear_id].kind_word()
            if kind in ("helical", "herringbone"):
                out.append(_warn(spec, "Gears", gears[gear_id].row, "id",
                                 f"{gear_id} is {kind}: a planetary stage is built with spur gears only by this "
                                 "version."))
    for mesh in spec.meshes:
        ga, gb = gears.get(mesh.a), gears.get(mesh.b)
        if ga is None or gb is None or ga.shaft not in shafts or gb.shaft not in shafts:
            continue
        ma, mb = shafts[ga.shaft].mount(), shafts[gb.shaft].mount()
        if ma != FRAME and ma == mb:
            out.append(_warn(spec, "Meshes", mesh.row, "a", f"{mesh.a} meshes {mesh.b} on the same carrier: a double "
                                                            "planet is not built by this version; a planet is built "
                                                            "meshing a sun and a ring on its carrier's axis."))
            continue
        for gear, other in ((ga, gb), (gb, ga)):
            if gear.shaft in found:
                out.append(_warn(spec, "Meshes", mesh.row, "a",
                                 f"{gear.id} is on {gear.shaft}, the carrier, and meshes {other.id}: a gear on the "
                                 "carrier that meshes another gear is not built by this version; it is built locked "
                                 "to the carrier when it meshes nothing."))
                break
    return out


def _and(items: List[str]) -> str:
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]
