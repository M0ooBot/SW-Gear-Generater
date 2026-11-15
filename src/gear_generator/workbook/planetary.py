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

from ..gears.base import Diagnostic
from .model import GearboxSpec

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


def stages(spec: GearboxSpec, placed: Dict[str, object]) -> Tuple[Stage, ...]:
    """Every planetary stage of ``spec`` (W7 builds one; §1.2 refuses a second), from the read and the placed gears
    (keyed by copy id). Agent B writes it."""
    raise ValueError("Planetary stages are not recognised by this version of Gear Generator yet, so this workbook is "
                     "not laid out.")


def assembly_counts(z_sun: int, z_ring: int, fit: int) -> Tuple[int, ...]:
    """Every number of copies from 1 to ``fit`` that meshes with the sun and the ring at once: N dividing ``z_sun +
    z_ring`` (W7-PLAN §2.3 item 2). Agent B writes it."""
    raise ValueError("Which numbers of planets fit a planetary stage is not worked out by this version of Gear "
                     "Generator yet.")


def most_that_fit(a: float, outer_diameter: float, module: float) -> int:
    """The most copies that stand round a carrier at ``a`` mm from its axis with their tips clear: the largest N
    with ``2a·sin(π/N) >= outer_diameter + CLASH_GAP·module`` (W7-PLAN §2.3 item 3). Agent B writes it."""
    raise ValueError("How many planets fit round a carrier is not worked out by this version of Gear Generator yet.")


def mesh_carrier(spec: GearboxSpec, a: str, b: str) -> Optional[str]:
    """What a listed mesh between gears ``a`` and ``b`` is measured against (W7-PLAN §2.5): ``"frame"`` when both
    are on frame shafts; the carrier shaft's id when one is on a shaft mounted on it and the other on a frame shaft
    coaxial with it; None when it fits no carrier (an error). Agent B writes it."""
    raise ValueError("Which carrier a mesh turns against is not worked out by this version of Gear Generator yet.")


def refusals(spec: GearboxSpec) -> List[Diagnostic]:
    """§1.2's rows of what W7 does not build, each a warning at its cell, for ``build.later_rows`` (Build parts still
    builds every gear's part). Agent B writes it."""
    raise ValueError("Which planetary stages this version builds is not worked out by this version of Gear "
                     "Generator yet.")
