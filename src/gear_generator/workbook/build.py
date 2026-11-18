"""From workbook rows to SolidWorks build plans (docs/PLAN-WORKBOOK.md §4.1, phase W2: parts only).

Each row is turned into the strip's own form, ``GearSpec``, and from there
into the strip's own plan, with the strip's own validation in between — so a
row builds exactly the part the strip would build from the same values, and
every rule the strip enforces holds here too. What is new is only the
bookkeeping: which rows this phase can build, which share one part file, and
where each diagnostic points in the workbook.

**Rows a later phase builds** (§3.4: bevel gears, carriers and copies, turned
axes, sleeves, dogs, sliding gears, modes) are read, and refused at Build with
the phase that builds them — not errors. :func:`later_rows` names each one.
Build parts leaves out the parts of bevel, sleeve and dog rows and builds the
rest, since a planet or a sliding gear is an ordinary part; but none of these
rows is laid out, checked or placed before its phase, so the layout part and
assembly (W4) are refused whole while any is there. Whether anything may be
built is not decided here, from the parts alone: :mod:`.assess` decides it from
everything the read, the gears and the gearbox checks say.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from ..gears import kind_for, plan_for
from ..gears.base import ERROR, WARNING, BuildPlan, Diagnostic, GeometryError
from ..spec import GearSpec, InputError, as_built
from .geometry import bevel_cuts, cut_overrides
from .model import Gear, GearboxSpec

PART_SUFFIX = ".SLDPRT"

# Kinds a later phase builds: what such a row is, and the phase that builds it (PLAN-WORKBOOK §6).
# W8 was the last phase of the import as planned on 2026-11-11 (sleeves and dogs are built, gears/clutch.py); W9
# (issue #1) builds on it and leaves no row waiting for a phase.
LATER: Dict[str, Tuple[str, str]] = {}

# A GearSpec field's diagnostics belong to a workbook column; most share the name.
FIELD_COLUMN = {"teeth_side": "side", "recipe": "flank", "name": "part_name"}


@dataclass(frozen=True)
class PartJob:
    """One part file to build, and every workbook row it serves (identical gears share one part)."""

    stem: str
    path: str
    gear_ids: Tuple[str, ...]
    spec: GearSpec
    derived: Any
    plan: BuildPlan


@dataclass
class PartsPlan:
    jobs: List[PartJob] = field(default_factory=list)
    diagnostics: List[Diagnostic] = field(default_factory=list)   # each names its cell; ``refused`` among them
    later: List[Tuple[str, str]] = field(default_factory=list)    # (gear, why its part is not built yet)
    refused: List[Diagnostic] = field(default_factory=list)       # every row a later phase builds (later_rows)

    @property
    def errors(self) -> List[Diagnostic]:
        """The parts' own errors only — not the read's, nor the gearbox's. Gate on :mod:`.assess`, not on this."""
        return [d for d in self.diagnostics if d.is_error]


def _where(spec: GearboxSpec, gear: Gear, field_name: str) -> str:
    key = FIELD_COLUMN.get(field_name, field_name)
    if field_name and key in {c for c in spec.columns.get("Gears", {})}:
        return spec.cell("Gears", gear.row, key)
    return spec.cell("Gears", gear.row, "id")


def check_gear(spec: GearboxSpec, gear: Gear, cuts: Optional[Dict[str, Any]] = None,
               variables: Optional[Sequence[Sequence[str]]] = None) -> Tuple[Optional[GearSpec], Any, List[Diagnostic]]:
    """The strip's checks on one row: (its GearSpec, what it works out to or None, diagnostics naming cells).

    A bevel row (W6) is checked as cut for its partner and shaft angle (``geometry.bevel_cuts``; ``cuts`` when the
    caller has them already); a cut with a problem is an error at the gear's cell, and the gear is not planned.

    F3 (PLAN-PRINTED §4.1.1; F3-INTERFACES §14, S3): ``variables``, the globals on record of the part the row's gear
    has, read the row as built (``spec.as_built``), so its checks speak of the hole that part was cut with (a blank
    Bore allowance on a part built before F3 is none) and it plans that hole; None, a row with no part on record."""
    if gear.kind_word() == "bevel":
        cut = (cuts if cuts is not None else bevel_cuts(spec)).get(gear.id)
        if cut is not None and cut.problem:
            where = _where(spec, gear, "")
            return gear.gear_spec(spec.box), None, [Diagnostic(ERROR, f"{where}: {cut.problem}", where)]
        gear_spec = gear.gear_spec(spec.box, **cut_overrides(cut))
    else:
        gear_spec = gear.gear_spec(spec.box)
    if variables is not None:
        gear_spec = as_built(gear_spec, variables)
    kind = kind_for(gear_spec)
    if kind is None:
        return gear_spec, None, []
    out: List[Diagnostic] = []
    try:
        for d in kind.validate(gear_spec):
            where = _where(spec, gear, d.field)
            out.append(Diagnostic(d.level, f"{where}: {gear.id}: {d.message}", where))
        if any(d.is_error for d in out):
            return gear_spec, None, out
        return gear_spec, kind.derive(gear_spec), out
    except (GeometryError, InputError, ValueError) as exc:
        where = _where(spec, gear, "")
        out.append(Diagnostic(ERROR, f"{where}: {gear.id}: {exc}", where))
        return gear_spec, None, out


def rows_with_errors(diagnostics) -> set:
    """The Gears rows a reading error already points at: the strip's checks would only repeat it."""
    rows = set()
    for d in diagnostics:
        if d.is_error:
            match = re.match(r"^Gears(?:!\$?[A-Za-z]{1,3}\$?(\d+)| row (\d+))$", d.field or "")
            if match:
                rows.add(int(match.group(1) or match.group(2)))
    return rows


def plan_parts(spec: GearboxSpec, folder: str, part_template: str = "", skip_rows=(),
               built: Optional[Mapping[str, Sequence[Sequence[str]]]] = None) -> PartsPlan:
    """A plan per distinct part: each buildable row checked, identical rows sharing one file.

    Two rows share a file when they would build the same part: their plans are
    compared, not their forms, so a Part name typed as the default, or a Hand
    on a spur gear, does not make two identical gears different. Two rows that
    would make the same file name — ignoring case, as Windows does — but not
    the same part (a different face width, which the name leaves out) are an
    error naming both, since one file cannot be both gears.

    A gear with an error is not planned, but the others still are: the window
    shows what each good gear will become, and Build waits for the errors.

    F3 (F3-INTERFACES §14, S3): ``built`` maps a gear to the globals on record of its part (``built_globals``), and each
    such row is checked and planned as built (:func:`check_gear`); a gear not in it, or None, as a row with no part.
    """
    out = PartsPlan()
    template = spec.box.part_template or part_template
    jobs: Dict[str, PartJob] = {}          # by the file name in lower case
    order: List[str] = []
    out.refused = later_rows(spec)
    cuts = bevel_cuts(spec)
    for gear in spec.gears:
        if gear.kind_word() in LATER:
            out.later.append((gear.id, _later_kind(gear)))
            continue
        if gear.row in skip_rows:
            continue                       # its own cell is already an error; it is not built
        gear_spec, derived, diagnostics = check_gear(spec, gear, cuts, (built or {}).get(gear.id))
        out.diagnostics.extend(diagnostics)
        if derived is None:
            continue
        stem = gear_spec.stem()
        key = stem.lower()
        if key in jobs:
            first = jobs[key]
            if plan_for(gear_spec, derived, template, first.path) != first.plan:
                where = _where(spec, gear, "name")
                same = "" if stem == first.stem else f" ({first.stem} and {stem} are one name to Windows)"
                # W9b (the coordinator's ruling on the review's should-fix 5): no band mark in a file name, since W9c
                # gives a built sleeve its bands in place and it keeps its file; so say why the two differ.
                banded = [g for g, s in ((gear.id, gear_spec), (first.gear_ids[0], first.spec)) if s.has_bands()]
                why = (f" ({banded[0]} has bands and {gear.id if banded[0] != gear.id else first.gear_ids[0]} has "
                       "none, and a file name does not say so)" if len(banded) == 1 else "")
                out.diagnostics.append(Diagnostic(
                    ERROR, f"{where}: {gear.id} and {first.gear_ids[0]} would both be {first.stem}{PART_SUFFIX}"
                           f"{same}, but they are not the same gear{why}; give one of them a Part name.", where))
                continue
            jobs[key] = PartJob(first.stem, first.path, first.gear_ids + (gear.id,), first.spec, first.derived,
                                first.plan)
            continue
        path = os.path.join(folder, stem + PART_SUFFIX)
        jobs[key] = PartJob(stem, path, (gear.id,), gear_spec, derived, plan_for(gear_spec, derived, template, path))
        order.append(key)
    out.jobs = [jobs[key] for key in order]
    out.diagnostics.extend(out.refused)          # listed under Checks with the rest, each at its cell
    return out


def _later_kind(gear: Gear) -> str:
    """``G5 is a bevel gear: right-angle stages are built in phase W6.``"""
    what, phase = LATER[gear.kind_word()]
    return f"{gear.id} is {what}: {phase}."


def later_rows(spec: GearboxSpec) -> List[Diagnostic]:
    """Every row a later phase builds, each a warning naming its cell, the row and the phase that builds it.

    The gears whose own part waits (sleeve, dog), the gears that slide, and
    the modes. Turned axes and bevel gears are W6's, laid out and built (a
    turned mesh waits only for its probe finding: ``motion.turned_refusal``);
    carriers and copies W7's. A planetary form no version builds yet is not a
    later phase's row: it is an error of the workbook (``planetary.refusals``,
    said by ``checks.check``).
    """
    out: List[Diagnostic] = []

    def refuse(where: str, sentence: str) -> None:
        out.append(Diagnostic(WARNING, f"{where}: {sentence}", where))

    for gear in spec.gears:
        where = spec.cell("Gears", gear.row, "id")
        if gear.kind_word() in LATER:
            refuse(where, _later_kind(gear))
    # W8 builds sliding gears, sleeves, dogs and modes: none waits for a later phase now.
    return out


def gear_diagnostics(spec: GearboxSpec, skip_rows=(),
                     built: Optional[Mapping[str, Sequence[Sequence[str]]]] = None) -> List[Diagnostic]:
    """Every row's own checks, for the window to show as the file changes — no plans are made. ``built`` as for
    :func:`plan_parts`."""
    out: List[Diagnostic] = []
    cuts = bevel_cuts(spec)
    for gear in spec.gears:
        if gear.kind_word() in LATER or gear.row in skip_rows:
            continue
        out.extend(check_gear(spec, gear, cuts, (built or {}).get(gear.id))[2])
    return out


def built_globals(record: Any) -> Dict[str, Sequence[Sequence[str]]]:
    """Each gear the record's current parts serve (``LinkRecord.current_parts()``), and the globals on record of its
    part (``PartEntry.variables``), the first part in the record's order for a gear listed twice: what
    :func:`plan_parts` reads a row on record as built from (F3). Empty with no record."""
    out: Dict[str, Sequence[Sequence[str]]] = {}
    for entry in (record.current_parts() if record is not None else []):
        for gear in entry.gears:
            out.setdefault(gear, list(entry.variables or []))
    return out
