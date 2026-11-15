"""Running a build plan against SolidWorks, in the right order.

A :class:`~gears.base.BuildPlan` is plain data; this module is the one place
that walks it and says what happened. What SolidWorks is reached through is a
:class:`SolidWorks` protocol, so every rule below is testable against a fake
on a machine with no CAD package at all:

* **Measure the document's trig units before writing a global.** A degree
  expression in a radian document is a wrong gear with no red equation to
  show for it.
* **Suppress the rebuild for the whole batch and restore it in a ``finally``.**
  A document left suppressed looks fine and silently stops updating.
* **Stop geometry at the first failure.** A sketch that did not close cannot
  be extruded, and every later step would fail in a way that hides the first.
* **Rebuild exactly once, even after a stop,** so what is left open for
  inspection shows SolidWorks' own view of it.
* **Read names and values back.** A kept name that differs from the one asked
  for stops the build before an equation refers to it, and every global's value
  after the rebuild is compared with the maths.
* **Save only a build with no failures,** and never over an existing file.
"""

from __future__ import annotations

import math
import os
import re
from dataclasses import dataclass, field
from typing import Callable, Collection, Dict, List, Mapping, Optional, Protocol, Sequence, Tuple, Union

from . import findings
from .gears import base
from .gears.base import BuildPlan, GlobalVariable
from .gears.equations import DEGREES, RADIANS, EquationError, evaluate_all, split_equation
from .gears.spur import AXIS_NAME
from .store import GEARBOX_MOTION, GEARBOX_STATIC, same_path
from .swcom import (ASSEMBLY_PAIR, ASSEMBLY_STATIC, ASSEMBLY_TRAIN, COMPONENT_FIND_ROUTES, CONFIGURATION_FINDINGS,
                    DOC_ASSEMBLY, MINIMUM_MAJOR, configuration_finding, positions_per_configuration,
                    ENTITY_ALONG, LINE_TOLERANCE, RESOLVED_ROUTE_FINDING, ComponentGone, ConfigurationGone, DocInfo, MateGone, MateRefused, MateState,
                    SenseUnreadable, SolidWorksError, Vec3, axes_parallel, lines_meet, meets_minimum, own_axes_angle,
                    rebuild_call, release_year, turned_refusal)

VALUE_TOLERANCE = 1e-6
FULLY_DEFINED = 3


class SolidWorks(Protocol):
    """Exactly the slice of :class:`swcom.Session` a build uses."""

    revision: Tuple[int, ...]

    def active_document(self) -> Optional[DocInfo]: ...
    def begin_build(self) -> None: ...
    def end_build(self) -> None: ...
    def new_part(self, template: str = "") -> DocInfo: ...
    def new_assembly(self, template: str = "") -> DocInfo: ...
    def document_path(self) -> str: ...
    def set_rebuild_suppressed(self, suppressed: bool) -> None: ...
    def rebuild(self, kind: Optional[str] = None) -> bool: ...
    def save_as(self, path: str) -> str: ...
    def detect_trig_units(self) -> str: ...
    def add_global_variable(self, name: str, expression: str) -> int: ...
    def set_global_variable(self, name: str, expression: str) -> None: ...
    def link_dimension(self, dimension: str, expression: str) -> int: ...
    def equations(self) -> List[Tuple[str, float]]: ...
    def equation_values(self) -> Dict[str, float]: ...
    def insert_axis(self, handle: str, name: str, planes: Tuple[base.PlaneRef, base.PlaneRef]) -> str: ...
    def open_sketch(self, handle: str, plane: Union[int, str]) -> None: ...
    def close_sketch(self, handle: str, name: str) -> str: ...
    def sketch_status(self, name: str) -> int: ...
    def sketch_circle(self, handle: str, centre, radius: float, construction: bool = False) -> None: ...
    def sketch_arc(self, handle: str, centre, start, end, direction: int = 1, construction: bool = False) -> None: ...
    def sketch_line(self, handle: str, start, end, construction: bool = False) -> None: ...
    def sketch_point(self, handle: str, at) -> None: ...
    def sketch_equation_curve(self, handle: str, x: str, y: str, t1: str, t2: str, start, end) -> None: ...
    def add_relation(self, kind: str, refs: Sequence[str]) -> str: ...
    def dimension(self, name: str, refs: Sequence[str], at) -> str: ...
    def extrude(self, handle: str, sketch: str, name: str, depth: float, depth_dim: str) -> Tuple[str, str]: ...
    def cut_extrude(self, handle: str, sketch: str, name: str) -> str: ...
    def circular_pattern(self, handle: str, name: str, axis: str, feature: str, count: int,
                         count_dim: str) -> Tuple[str, str]: ...
    def ref_plane(self, handle: str, name: str, plane: int, offset: float, flip: bool,
                  offset_dim: str) -> Tuple[str, str]: ...
    def sweep_cut(self, handle: str, profile: str, path: str, name: str, twist: float, reverse: bool,
                  twist_dim: str) -> Tuple[str, str]: ...
    def mirror_body(self, handle: str, name: str, plane: str) -> str: ...
    def ref_plane_normal(self, handle: str, name: str, line: str, point: str) -> str: ...
    def revolve(self, handle: str, sketch: str, name: str, axis: str) -> str: ...
    def loft_cut(self, handle: str, name: str, profiles: Sequence[str]) -> str: ...
    def add_component(self, handle: str, path: str, at) -> str: ...
    def fix_component(self, handle: str) -> None: ...
    def unfix_component(self, handle: str) -> None: ...
    def add_mate(self, handle: str, kind: str, a: str, b: str, value: float = 0.0,
                 name: str = "", ratio: Tuple[float, float] = (1.0, 1.0), flip: bool = False) -> Tuple[str, str]: ...
    def interference_count(self) -> Tuple[int, float]: ...
    def set_custom_property(self, name: str, value: str) -> None: ...
    def place_component(self, handle: str, rotation: Sequence[float], at, kind: Optional[str] = None) -> None: ...
    # W4 (a workbook's layout part and static assembly). ``documents`` and ``feature_names`` are swcom.Session's
    # own, unchanged; the other four are new there (each docstring in swcom says what it does).
    def documents(self) -> List[DocInfo]: ...
    def feature_names(self) -> List[str]: ...
    def open_document(self, path: str) -> DocInfo: ...
    def has_unsaved_changes(self) -> bool: ...
    def find_component(self, handle: str, name: str, *, lightweight_ok: bool = False) -> str: ...
    def component_frame(self, handle: str) -> Tuple[Tuple[float, ...], Tuple[float, float, float]]: ...
    def interferences(self) -> List[Tuple[Tuple[str, ...], float]]: ...
    # W5 (the workbook gearbox that turns): new in swcom.Session, each docstring there says what it does. ``add_mate``
    # also takes kind "lock" (bare handles, anchor first: gears.base.Mate) and keeps AddMate5's status.
    def mate_status(self, name: str) -> Optional[int]: ...
    def mate_states(self, *, others: Optional[List[str]] = None) -> List[MateState]: ...
    def constrained_status(self, handle: str) -> int: ...
    def find_mate(self, handle: str, name: str) -> str: ...
    def set_mate_suppressed(self, handle: str, suppressed: bool) -> None: ...
    def set_gear_ratio(self, handle: str, a: str, b: str, ratio: Tuple[int, int]) -> None: ...
    def gear_mate_ratio(self, handle: str) -> Tuple[float, float]: ...
    def component_resolved(self, handle: str) -> bool: ...
    # W6 (W6-INTERFACES.md): ``(right, (τa, τb))`` against the two gears' own +Z as placed and the mesh's ``k > 0``;
    # on parallel axes only the product τa·τb means anything (§7.4), and nothing here names a single τ.
    def gear_mate_sense(self, handle: str, same_sense: bool,
                        axes: Tuple[Vec3, Vec3]) -> Tuple[bool, Tuple[int, int]]: ...
    def line_axis(self, handle: str, name: str, point: Vec3, direction: Vec3, length: float) -> str: ...
    def axis_line(self, handle: str, name: str) -> Tuple[Vec3, Vec3]: ...
    def remake_gear_mate(self, handle: str, a: str, b: str, ratio: Sequence[float], flip: bool,
                         *, saved: bool = True) -> None: ...
    # W8 (W8-INTERFACES.md §2; Agent A writes the bodies in swcom.Session): an assembly's configurations, a mate's
    # flag and a distance mate's value per configuration. After add_configuration and show_configuration (and an
    # open) every component and mate handle is fetched again by name before it is used (the handle rule).
    def configurations(self) -> List[str]: ...
    def active_configuration(self) -> str: ...
    def add_configuration(self, name: str) -> None: ...
    def show_configuration(self, name: str) -> None: ...
    def delete_configuration(self, name: str) -> None: ...
    def set_mate_suppressed_in(self, handle: str, suppressed: bool, configurations: Sequence[str]) -> None: ...
    def mate_suppression(self, handle: str, configurations: Sequence[str]) -> Dict[str, bool]: ...
    def set_dimension_in(self, mate_handle: str, value_mm: float, configurations: Sequence[str]) -> None: ...
    def dimension_values(self, mate_handle: str, configurations: Sequence[str]) -> Dict[str, float]: ...
    def is_fixed(self, handle: str) -> bool: ...
    def component_path(self, handle: str) -> str: ...


class BuildError(SolidWorksError):
    """The build could not start at all; nothing was made."""


class NotAsBuilt(BuildError):
    """A document built earlier, opened and read, does not hold what it should: a global's text differs or is
    gone, or a feature or component named on record was renamed or deleted in SolidWorks. ``path`` is that
    document. :func:`build_gearbox` turns it into :attr:`GearboxResult.mismatched` (the finish records it, so the
    next plan makes the part new rather than reuse it: W4 review B2's last corner); :func:`update_gearbox` raises
    it from its check phase, before anything changes."""

    def __init__(self, message: str, path: str = "") -> None:
        super().__init__(message)
        self.path = path


@dataclass
class BuildResult:
    kind: str = ""
    recipe: str = ""
    document: str = ""
    path: str = ""
    trig: str = ""
    done: List[str] = field(default_factory=list)
    failures: List[Tuple[str, str]] = field(default_factory=list)
    stopped_at: str = ""
    features: List[str] = field(default_factory=list)
    dimensions: Dict[str, str] = field(default_factory=dict)   # planned "Dim@Owner" -> what SolidWorks kept
    manual: List[str] = field(default_factory=list)
    checks: List[str] = field(default_factory=list)            # things to look at that do not fail a build
    rebuilt: bool = False
    saved: str = ""
    components: Dict[str, str] = field(default_factory=dict)   # an assembly's plan handle -> the Name2 it kept
    # W5, a train's mate check (filled only for a build of kind ASSEMBLY_TRAIN; see :func:`build`): every REFUSAL
    # found, as a full sentence naming the mate or gear, each also a failure (so the assembly is not saved), and every
    # mate as SolidWorks held it when checked, for the log. Only SolidWorks' own refusals go here (MateRefused, and
    # the check's status, error code, suppressed and constrained findings); a COM or any other failure is an
    # ordinary failed build, as in W4, with no mate problem.
    mate_problems: List[str] = field(default_factory=list)
    mates: List[MateState] = field(default_factory=list)
    # W5, which way each gear mate turns (probe ring_mate_sense): the gear mates the read-back found turning their
    # gears against their mesh, made again with the other Flip (and then read right). Empty when no sense was read.
    turned_round: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failures

    def log_lines(self) -> List[str]:
        lines = [f"build   {self.document or '(no document)'} · {self.kind} · recipe {self.recipe} · trig {self.trig or '?'}"]
        lines.extend(f"ok      {line}" for line in self.done)
        lines.extend(_mate_line(mate) for mate in self.mates)
        if self.turned_round:
            lines.append("ok      read turning against their mesh, so made again with the other Flip: "
                         + ", ".join(self.turned_round))
        for what, why in self.failures:
            lines.append(f"FAIL    {what}: {why}")
        if self.stopped_at:
            lines.append(f"STOPPED at {self.stopped_at}; the part is left open as it is")
        lines.extend(f"CHECK   {line}" for line in self.checks)
        if self.document or self.rebuilt:          # no document made (_build_in_job): nothing was rebuilt either
            lines.append("ok      rebuilt once" if self.rebuilt else "FAIL    the rebuild reported an error")
        if self.manual:
            lines.append(f"MANUAL  {len(self.manual)} step(s) to do by hand")
            lines.extend(f"MANUAL  {text}" for text in self.manual)
        lines.append(f"ok      saved {self.saved}" if self.saved else "not saved")
        return lines


@dataclass
class PairResult:
    gear_a: BuildResult
    gear_b: Optional[BuildResult] = None
    assembly: Optional[BuildResult] = None
    skipped: str = ""

    @property
    def ok(self) -> bool:
        return all(r is not None and r.ok for r in (self.gear_a, self.gear_b, self.assembly))

    def log_lines(self) -> List[str]:
        lines: List[str] = []
        for result in (self.gear_a, self.gear_b, self.assembly):
            if result is not None:
                lines.extend(result.log_lines())
        if self.skipped:
            lines.append(f"SKIPPED {self.skipped}")
        return lines


@dataclass
class UpdateResult:
    document: str = ""
    changed: List[str] = field(default_factory=list)
    unchanged: List[str] = field(default_factory=list)
    failures: List[Tuple[str, str]] = field(default_factory=list)
    rebuilt: bool = False
    trig: str = ""

    @property
    def ok(self) -> bool:
        return not self.failures


def _mate_line(mate: MateState) -> str:
    """``mate    G3 locked to G2 · error code 46, at fault · suppressed``: one mate as the check read it. The error
    code's number is logged, never interpreted (2024 and 2026 give different numbers for the same mates)."""
    line = f"mate    {mate.name}"
    if mate.code:
        line += f" · error code {mate.code}, {'a warning' if mate.warning else 'at fault'}"
    if mate.suppressed:
        line += " · suppressed"
    return line


def _gate(sw: SolidWorks) -> None:
    if not meets_minimum(sw.revision):
        raise BuildError(f"Building needs SolidWorks {release_year(MINIMUM_MAJOR)} or newer.")


_SET = object()     # a finding that must merely be in findings.py (not None), whatever its value

# What a train's mate check reads (findings.py, "the workbook gearbox that turns (tier 8)"): AddMate5's status, the
# mates found by walking the MateGroup (their suppression read in this configuration), and each gear's constrained
# status — as (finding, the value it must have).
TRAIN_CHECK_FINDINGS = (("ADD_MATE_NO_ERROR", _SET), ("ADD_MATE_OVER_DEFINED", _SET), ("COMPONENT_UNDER_DEFINED", _SET),
                        ("COMPONENT_FULLY_DEFINED", _SET), ("COMPONENT_OVER_DEFINED", _SET),
                        ("MATE_FIND_ROUTE", "mate group"), ("THIS_CONFIGURATION", _SET))
# What a train's plan makes, beyond the check: a lock (swcom.Session._lock_mate), a mate given a name.
LOCK_FINDINGS = (("COMPOUND_LOCK_ROUTE", "lock alone"), ("LOCK_SELECT_ROUTE", "Select4 with a mark-1 select data"),
                 ("MATE_LOCK", _SET), ("MATE_ALIGN_CLOSEST", _SET))
RENAME_FINDINGS = (("MATE_RENAME_ROUTE", "IFeature.Name put"),)
# A Build makes its mates in one batch with CommandInProgress on (_run: set_rebuild_suppressed), and renames each one
# straight after its AddMate5 in the new, unsaved assembly: probe round P0c, mates_under_command_in_progress.
BUILD_MATE_FINDINGS = (("MATES_UNDER_COMMAND_IN_PROGRESS", True),)
BUILD_RENAME_FINDINGS = (("MATE_RENAME_AT_ONCE", True),)
# What swcom.Session.add_mate and _gear_mate read for each kind of mate a train plan makes (W4-era members, read there
# mid-build): an axis mate (coincident), an anchor's origin on or at a distance from the Front plane, a gear mate.
MATE_KIND_FINDINGS = {
    "coincident": (("MATE_COINCIDENT", _SET), ("MATE_ALIGN_CLOSEST", _SET)),
    "point": (("MATE_COINCIDENT", _SET), ("MATE_ALIGN_CLOSEST", _SET), ("ORIGIN_POINT", _SET)),
    "point distance": (("MATE_DISTANCE", _SET), ("MATE_ALIGN_CLOSEST", _SET), ("ORIGIN_POINT", _SET)),
    "gear": (("MATE_GEAR", _SET), ("GEAR_MATE_ROUTE", _SET), ("GEAR_MATE_NUMERATOR_FIRST", _SET),
             ("MATE_ALIGN_CLOSEST", _SET)),
}


def _settled(needed: Sequence[Tuple[str, object]]) -> Optional[Tuple[str, object]]:
    """The first (finding, its value) of ``needed`` that is missing, None, or not the value it must have."""
    for name, wanted in needed:
        value = getattr(findings, name, None)
        if value is None or (wanted is not _SET and value != wanted):
            return name, value
    return None


def _train_gate(plan: Optional[BuildPlan] = None, *, building: bool = False) -> None:
    """Refuse, before anything is made or changed in SolidWorks, a train whose SolidWorks calls are not all settled:
    every finding of :data:`TRAIN_CHECK_FINDINGS`, and for ``plan`` the lock findings when it locks a gear and the
    rename finding when it names a mate (each read with getattr).

    ``building`` (a Build, not an Update): ``swcom.rebuild_call`` gives a train one route, the one a built train
    re-solves under (``findings.MATED_ASSEMBLY_REBUILD_ROUTE``), for Build and Update alike; probe round P0b
    measured the route a train may be built under apart (``findings.MATED_BUILD_REBUILD_ROUTE``). A Build is refused
    while that is not settled, or while it differs from the one the build would take, so a later probe changing one
    never leaves the build silently following the other."""
    if building:
        built = getattr(findings, "MATED_BUILD_REBUILD_ROUTE", None)
        solved = getattr(findings, "MATED_ASSEMBLY_REBUILD_ROUTE", None)
        if built is None:
            raise BuildError(f"How a gearbox built to turn may be rebuilt while it is built has not been settled on "
                             f"SolidWorks (findings.MATED_BUILD_REBUILD_ROUTE is None, and findings."
                             f"MATED_ASSEMBLY_REBUILD_ROUTE is {solved!r}), so nothing is made or changed; run probe "
                             "tier 8 first.")
        if built != solved:
            raise BuildError(f"A gearbox built to turn would be built under findings.MATED_BUILD_REBUILD_ROUTE "
                             f"{built!r}, but Gear Generator rebuilds a train under findings."
                             f"MATED_ASSEMBLY_REBUILD_ROUTE {solved!r}, and the two differ, so nothing is made or "
                             "changed; run probe tier 8 again.")
    needed = list(TRAIN_CHECK_FINDINGS)
    mates = [op for op in plan.ops if isinstance(op, base.Mate)] if plan is not None else []
    if building and mates:
        needed += BUILD_MATE_FINDINGS
    if building and any(op.kind == "gear" for op in mates):
        missing = _settled(BUILD_SENSE_FINDINGS)
        if missing is not None:
            raise BuildError(f"A gearbox built to turn checks which way each gear mate turns its gears as it makes "
                             f"them, and that has not been settled on SolidWorks (findings.{missing[0]} is "
                             f"{missing[1]!r}), so nothing is made or changed; run probe ring_trains_saved first.")
    if any(op.kind == "lock" for op in mates):
        needed += LOCK_FINDINGS
    if any(op.name for op in mates):
        needed += RENAME_FINDINGS + (BUILD_RENAME_FINDINGS if building else ())
    for kind in dict.fromkeys(op.kind for op in mates):
        needed += MATE_KIND_FINDINGS.get(kind, ())
    missing = _settled(needed)
    if missing is not None:
        raise BuildError(f"A gearbox built to turn needs findings.{missing[0]} settled on SolidWorks (it is "
                         f"{missing[1]!r}), so nothing is made or changed; run probe tier 8 first.")


def _assembly_rebuild_gate(kind: str) -> None:
    """Refuse, before anything is made or changed, a job that would rebuild an assembly of this kind while how to
    rebuild one is not settled: :func:`swcom.rebuild_call`'s sentence, as a :class:`BuildError`. Every assembly
    rebuild goes through ``rebuild_call`` (``Session.rebuild`` and ``place_component``), so without this a job
    would make or change its parts and only then refuse at the assembly. A pair or a train is refused only for a
    finding of its own this code does not know: with none, it takes the full rebuild."""
    try:
        rebuild_call(DOC_ASSEMBLY, kind)
    except SolidWorksError as exc:
        raise BuildError(str(exc)) from None


def is_mated(plan: BuildPlan) -> bool:
    """Whether an assembly plan mates its components (W5-PLAN §1's predicate)."""
    return any(isinstance(op, base.Mate) for op in plan.ops)


def workbook_assembly_kind(plan: BuildPlan) -> str:
    """The kind of a workbook gearbox's assembly, and of any assembly built outside :func:`build_pair`: a train
    when its plan mates its components (W5), else static (fixed components, W4)."""
    return ASSEMBLY_TRAIN if is_mated(plan) else ASSEMBLY_STATIC


# -- the operations ---------------------------------------------------------


def _kept(result: BuildResult, what: str, wanted: str, kept: str) -> None:
    if kept != wanted:
        raise SolidWorksError(f"SolidWorks named the {what} {kept!r} instead of {wanted!r}, "
                              "so the equations that name it would break.")
    result.features.append(kept)


def _add_global(sw, op: base.AddGlobal, result, trig):
    sw.add_global_variable(op.name, op.expression_for(trig))
    return f"global \"{op.name}\""


def _link(sw, op: base.LinkDimension, result, trig):
    # A dimension SolidWorks named for itself (a mate's D1) is linked by what it kept.
    dimension = result.dimensions.get(op.dimension, op.dimension)
    sw.link_dimension(dimension, op.expression_for(trig))
    return f"link \"{dimension}\""


def _axis(sw, op: base.Axis, result, trig):
    _kept(result, "axis", op.name, sw.insert_axis(op.id, op.name, op.planes))
    return f"axis {op.name}"


def _line_axis(sw, op: base.LineAxis, result, trig):
    """W6: a slanted shaft's axis on a one-line 3D sketch (``Session.line_axis``, Agent A)."""
    _kept(result, "axis", op.name, sw.line_axis(op.id, op.name, op.point, op.direction, op.length))
    return f"axis {op.name} on {op.sketch}"


def _open(sw, op: base.OpenSketch, result, trig):
    sw.open_sketch(op.id, op.plane)
    return f"sketch {op.id} opened on plane {op.plane}"


def _circle(sw, op: base.Circle, result, trig):
    sw.sketch_circle(op.id, op.centre, op.radius, op.construction)
    return f"circle {op.id}"


def _arc(sw, op: base.Arc, result, trig):
    sw.sketch_arc(op.id, op.centre, op.start, op.end, op.direction, op.construction)
    return f"arc {op.id}"


def _line(sw, op: base.Line, result, trig):
    sw.sketch_line(op.id, op.start, op.end, op.construction)
    return f"line {op.id}"


def _point(sw, op: base.Point, result, trig):
    sw.sketch_point(op.id, op.at)
    return f"point {op.id}"


def _curve(sw, op: base.EquationCurve, result, trig):
    sw.sketch_equation_curve(op.id, op.x, op.y, op.t1, op.t2, op.start, op.end)
    return f"curve {op.id}"


def _relation(sw, op: base.Relation, result, trig):
    note = sw.add_relation(op.kind, op.refs)
    return f"{op.kind} {' '.join(op.refs)}" + (f" ({note})" if note else "")


def _dimension(sw, op: base.Dimension, result, trig):
    kept = sw.dimension(op.name, op.refs, op.at)
    if kept != op.name:
        raise SolidWorksError(f"SolidWorks named the dimension {kept!r} instead of {op.name!r}.")
    result.dimensions[op.name] = kept
    return f"dimension {op.name}"


def _close(sw, op: base.CloseSketch, result, trig):
    kept = sw.close_sketch(op.id, op.name)
    _kept(result, "sketch", op.name, kept)
    for planned in [k for k in result.dimensions if "@" not in k]:
        result.dimensions[f"{planned}@{kept}"] = f"{result.dimensions.pop(planned)}@{kept}"
    return f"sketch {op.name}"


def _extrude(sw, op: base.Extrude, result, trig):
    kept, dim = sw.extrude(op.id, op.sketch, op.name, op.depth, op.depth_dim)
    _kept(result, "extrusion", op.name, kept)
    if dim != op.depth_dim:
        raise SolidWorksError(f"The depth of {kept} kept the name {dim!r} instead of {op.depth_dim!r}.")
    result.dimensions[f"{op.depth_dim}@{op.name}"] = f"{dim}@{kept}"
    return f"extrude {op.name}"


def _cut(sw, op: base.Cut, result, trig):
    _kept(result, "cut", op.name, sw.cut_extrude(op.id, op.sketch, op.name))
    return f"cut {op.name}"


def _pattern(sw, op: base.CircularPattern, result, trig):
    kept, dim = sw.circular_pattern(op.id, op.name, op.axis, op.feature, op.count, op.count_dim)
    _kept(result, "pattern", op.name, kept)
    if dim != op.count_dim:
        raise SolidWorksError(f"The count of {kept} kept the name {dim!r} instead of {op.count_dim!r}.")
    result.dimensions[f"{op.count_dim}@{op.name}"] = f"{dim}@{kept}"
    return f"pattern {op.name} × {op.count}"


def _ref_plane(sw, op: base.RefPlane, result, trig):
    kept, dim = sw.ref_plane(op.id, op.name, op.plane, op.offset, op.flip, op.offset_dim)
    _kept(result, "plane", op.name, kept)
    if dim != op.offset_dim:
        raise SolidWorksError(f"The offset of {kept} kept the name {dim!r} instead of {op.offset_dim!r}.")
    result.dimensions[f"{op.offset_dim}@{op.name}"] = f"{dim}@{kept}"
    return f"plane {op.name}"


def _sweep(sw, op: base.SweepCut, result, trig):
    kept, dim = sw.sweep_cut(op.id, op.profile, op.path, op.name, op.twist, op.reverse, op.twist_dim)
    _kept(result, "sweep", op.name, kept)
    if dim != op.twist_dim:
        raise SolidWorksError(f"The twist of {kept} kept the name {dim!r} instead of {op.twist_dim!r}.")
    result.dimensions[f"{op.twist_dim}@{op.name}"] = f"{dim}@{kept}"
    return f"sweep {op.name}, twist {op.twist:.4f}°" + (" reversed" if op.reverse else "")


def _mirror(sw, op: base.MirrorBody, result, trig):
    _kept(result, "mirror", op.name, sw.mirror_body(op.id, op.name, op.plane))
    return f"mirror {op.name}"


def _ref_plane_normal(sw, op: base.RefPlaneNormal, result, trig):
    _kept(result, "plane", op.name, sw.ref_plane_normal(op.id, op.name, op.line, op.point))
    return f"plane {op.name}"


def _revolve(sw, op: base.Revolve, result, trig):
    _kept(result, "revolve", op.name, sw.revolve(op.id, op.sketch, op.name, op.axis))
    return f"revolve {op.name}"


def _loft_cut(sw, op: base.LoftCut, result, trig):
    _kept(result, "loft", op.name, sw.loft_cut(op.id, op.name, op.profiles))
    return f"loft {op.name}"


def _property(sw, op: base.CustomProperty, result, trig):
    sw.set_custom_property(op.name, op.value)
    return f"property {op.name!r}"


def _component(sw, op: base.AddComponent, result, trig):
    kept = sw.add_component(op.id, op.path, op.at)
    result.features.append(kept)
    result.components[op.id] = kept
    return f"component {kept}"


def _fix(sw, op: base.Fix, result, trig):
    sw.fix_component(op.component)
    return f"fixed {op.component}"


def _unfix(sw, op: base.Unfix, result, trig):
    sw.unfix_component(op.component)
    return f"unfixed {op.component}"


def _place(sw, op: base.Place, result, trig, kind):
    sw.place_component(op.component, op.rotation, op.at, kind=kind)
    return f"placed {op.component}"


def _mate(sw, op: base.Mate, result, trig):
    extra = {"ratio": op.ratio, "flip": op.flip} if op.kind == "gear" else {}
    kept, dim = sw.add_mate(op.id, op.kind, op.a, op.b, op.value, op.name, **extra)
    if op.name:
        _kept(result, "mate", op.name, kept)
    else:
        result.features.append(kept)
    if op.kind in base.VALUED_MATES:
        if not dim:
            raise SolidWorksError(f"The {op.kind} mate {kept} has no dimension with its value.")
        result.dimensions[f"D1@{op.name or op.id}"] = f"{dim}@{kept}"
    return f"mate {op.kind} {op.a} ~ {op.b}" + (f" as {kept}" if op.name else "")


_RUNNERS: Mapping[type, Callable] = {
    base.AddGlobal: _add_global,
    base.LinkDimension: _link,
    base.Axis: _axis,
    base.LineAxis: _line_axis,
    base.OpenSketch: _open,
    base.Circle: _circle,
    base.Arc: _arc,
    base.Line: _line,
    base.Point: _point,
    base.EquationCurve: _curve,
    base.Relation: _relation,
    base.Dimension: _dimension,
    base.CloseSketch: _close,
    base.Extrude: _extrude,
    base.Cut: _cut,
    base.CircularPattern: _pattern,
    base.RefPlane: _ref_plane,
    base.SweepCut: _sweep,
    base.MirrorBody: _mirror,
    base.RefPlaneNormal: _ref_plane_normal,
    base.Revolve: _revolve,
    base.LoftCut: _loft_cut,
    base.CustomProperty: _property,
    base.AddComponent: _component,
    base.Fix: _fix,
    base.Unfix: _unfix,
    base.Place: _place,
    base.Mate: _mate,
}


# -- building ---------------------------------------------------------------


def build(sw: SolidWorks, plan: BuildPlan, exists: Callable[[str], bool] = os.path.exists,
          kind: Optional[str] = None, *, gears: Optional[Mapping[str, str]] = None,
          senses: Optional[Mapping[str, bool]] = None, modes: Optional[ModesPlan] = None,
          mode_checks: Optional[List[ModeCheck]] = None,
          progress: Optional[Callable[[Step], None]] = None) -> BuildResult:
    """Make the plan's document, run every step, rebuild once, check, and save.

    Raises :class:`BuildError` only before anything is made. After that every
    problem is a failure in the result, and the document is left open.

    ``kind`` says what kind of assembly this is (``swcom.ASSEMBLY_KINDS``),
    for every rebuild and put of it (:func:`swcom.rebuild_call`); None reads
    it off the plan (:func:`workbook_assembly_kind`: a train if it mates its
    components, else static). :func:`build_pair` passes ``ASSEMBLY_PAIR``, so a
    pair keeps its own route whatever its plan holds, the puts before its
    mates included.

    W5 (Agent A writes it; W5-INTERFACES.md): a build whose kind, as
    resolved here, is ``ASSEMBLY_TRAIN`` runs the mate check after ``_run``,
    the rebuild and ``_verify``, before the save — every ``Mate`` op's
    ``sw.mate_status`` is ``findings.ADD_MATE_NO_ERROR``, ``sw.mate_states()``
    holds every planned mate with code 0 and not suppressed, and every mated
    gear (a handle in a ``Mate`` op whose last ``Fix``/``Unfix`` op is
    ``Unfix``) reads ``findings.COMPONENT_UNDER_DEFINED`` — each problem a
    sentence in :attr:`BuildResult.mate_problems` and a failure, so the
    document is left open, unsaved. A ``Mate`` op that raises
    ``swcom.MateRefused`` in ``_run`` puts its sentence in ``mate_problems``
    too; any other raise during a mate (a COM or RPC failure, a selection
    that did not take) is an ordinary failure, as in W4, and adds nothing to
    ``mate_problems`` — so the record holds Build back only for a refusal
    that repeats on every press. There is no ``mates=`` keyword: the
    kind decides, so a pair (``ASSEMBLY_PAIR``) and a static assembly are
    never mate-checked.

    ``senses`` (keyword, W6; W6-INTERFACES.md): gear mate name -> whether
    the mesh turns its two gears the same way about their own axes (``k >
    0``; ``GearboxPlan.mate_senses``). Given, and with the read-back settled
    (:func:`_sense_settled`), every gear mate is read straight after it is
    made (:func:`_settle_sense`) against its two gears' planned axes, and one
    turning its gears against their mesh is made again with the other Flip;
    with the read-back not settled, a plan with a mesh inside a ring is
    refused before anything is made, since its sense cannot be told. None:
    no gear mate between parallel axes is read (as before).

    Whatever is given, every gear mate's planned axes are judged before
    anything is made (:func:`_sense_gate`; W6-INTERFACES §7.3): one between
    gears whose axes are not of one family is refused while its sense cannot
    be read (the turned finding missing, or its angle outside the angles the
    finding covers) — there is no static fallback (W6-PLAN D16) — and, when
    it can, refused too unless ``senses`` says which way it turns.

    ``gears`` (keyword, :func:`build_gearbox`'s map of assembly handle to
    workbook gear id) names a gear in a mate problem by its id; without it,
    by the Name2 it kept. The check runs only when every op ran (a build
    stopped part-way has its failure already), and is refused before
    anything is made while a finding it reads is missing (:func:`_train_gate`).

    ``modes`` (keyword, W8; W8-INTERFACES.md §3): the configurations of a turning assembly, set up after the mate
    check and before the save (W8-PLAN §1.8, steps 1-7: :func:`_set_up_modes`; step 8, interference per mode, is
    :func:`build_gearbox`'s, after the save). None is W5's build call for call. Given, it is judged before anything
    is made (:func:`_modes_gate`, with the running version), and the assembly is saved in the first mode.
    ``mode_checks`` (keyword): a list each mode's :class:`ModeCheck` is appended to as it is checked.
    ``progress`` (keyword): told ``Step(STAGE_MODE, mode, index, count)`` as each mode is set up, and again as each
    is checked.
    """
    _gate(sw)
    problems = plan.check()
    if problems:
        raise BuildError("The build plan is not sound: " + " ".join(problems))
    _modes_gate(plan, modes, revision=sw.revision, senses=senses)
    first = plan.ops[0]
    if kind is None:
        kind = workbook_assembly_kind(plan)
    if modes is not None and kind != ASSEMBLY_TRAIN:
        raise BuildError("Modes were given for an assembly that is not built to turn, so nothing is made; that is a "
                         "fault in Gear Generator.")
    if isinstance(first, base.NewAssembly):
        _assembly_rebuild_gate(kind)
        if kind == ASSEMBLY_TRAIN:
            _train_gate(plan, building=True)
            senses = _sense_gate(plan, senses)
    save = next((op for op in plan.ops if isinstance(op, base.SaveAs)), None)
    if save is not None and save.path and exists(save.path):
        raise BuildError(f"{save.path} already exists, and a build never overwrites a file.")

    result = BuildResult(kind=plan.kind, recipe=plan.recipe, path=save.path if save else "")
    result.manual = [op.text for op in plan.manual_steps()]
    sw.begin_build()
    try:
        made = sw.new_part(first.template) if isinstance(first, base.NewPart) else sw.new_assembly(first.template)
        result.document = made.title
        result.done.append(f"new {'part' if isinstance(first, base.NewPart) else 'assembly'} {made.title}")
        try:
            result.trig = sw.detect_trig_units()
            result.done.append(f"trig units measured: {result.trig}")
            made: Dict[str, str] = {}
            sense = None
            if kind == ASSEMBLY_TRAIN and senses is not None and _sense_settled():
                sense = (dict(senses), _planned_axes(plan), dict(gears or {}), _planned_origins(plan))
            _run(sw, plan, result, kind, made, sense)
            result.rebuilt = bool(sw.rebuild(kind=kind))
            _verify(sw, plan, result)
            # A failed rebuild is an ordinary failed build (a component may be at fault): nothing is read as a mate
            # problem from it, so it never holds Build back.
            if kind == ASSEMBLY_TRAIN and not result.stopped_at and result.rebuilt:
                _check_mates(sw, plan, result, made, gears or {})
            if modes is not None and result.ok and result.rebuilt:
                _set_up_modes(sw, plan, modes, result, made, gears or {}, kind, sense, mode_checks,
                              progress or _quiet)
        except Exception as exc:  # noqa: BLE001 - the document is made: every problem is now a failure (B1)
            result.failures.append(("the build", _said(exc)))
            result.stopped_at = result.stopped_at or "the build"
    finally:
        sw.end_build()

    if save is not None and result.ok and result.rebuilt:
        try:
            result.saved = sw.save_as(save.path)
        except Exception as exc:  # noqa: BLE001 - a COM error or anything else on the save is the save's failure
            result.failures.append(("save", _said(exc)))
    return result


def _said(exc: BaseException) -> str:
    """What a raise says, for a failure line: a SolidWorks refusal (``swcom.ComError`` included) as it came, and
    anything else named, since it is not a sentence of ours."""
    if isinstance(exc, SolidWorksError):
        return str(exc)
    text = str(exc).strip().rstrip(".")
    return f"it stopped on an unexpected {type(exc).__name__}" + (f": {text}." if text else ".")


def _modes_gate(plan: Optional[BuildPlan], modes: Optional[ModesPlan], *, revision: Sequence[int] = (),
                senses: Optional[Mapping[str, bool]] = None) -> None:
    """Before anything is made: ``modes`` None passes. Otherwise refused with a :class:`BuildError` naming why:
    a ``ModesPlan`` with no assembly plan to set up in, or one that does not turn (a static assembly holds no modes);
    one :meth:`ModesPlan.check` finds unsound against it (every problem named); the build not told which way its gear
    mates turn (a coupling and a spline are settled by the read-back alone: the two versions give a collinear gear
    mate opposite senses, the W8 spike); a configuration finding the build calls on unsettled (each with getattr,
    :data:`swcom.CONFIGURATION_FINDINGS` and :data:`MODES_FINDINGS`), or the read-back's; and the running version not
    shown to hold a slide's value per configuration (:func:`_modes_version_refusal`, W8-INTERFACES §9.5: the
    worker's refusal, read from ``revision``)."""
    if modes is None:
        return
    if plan is None or not plan.ops or not isinstance(plan.ops[0], base.NewAssembly):
        raise BuildError("Modes were given with no assembly to make their configurations in, so nothing is made; "
                         "that is a fault in Gear Generator.")
    if workbook_assembly_kind(plan) != ASSEMBLY_TRAIN:
        raise BuildError("Modes were given for an assembly that does not turn, and only a gearbox built to turn holds "
                         "configurations, so nothing is made; that is a fault in Gear Generator.")
    problems = modes.check(plan)
    if problems:
        raise BuildError("The modes plan is not sound, so nothing is made: " + " ".join(problems))
    if senses is None:
        raise BuildError("A gearbox with modes was not told which way its gear mates turn, and its couplings and "
                         "splines are known only by reading each back, so nothing is made; that is a fault in Gear "
                         "Generator.")
    for name, _ in CONFIGURATION_FINDINGS:
        problem = configuration_finding(name)
        if problem is not None:
            raise BuildError(f"Working with an assembly's configurations has not been settled on SolidWorks "
                             f"({problem}), so a gearbox with modes is not built and nothing is made.")
    route = getattr(findings, "COMPONENT_FIND_ROUTE", None)
    if route not in COMPONENT_FIND_ROUTES:
        raise BuildError(f"Finding a component again after a configuration change has not been settled on "
                         f"SolidWorks (findings.COMPONENT_FIND_ROUTE is {route!r}), so a gearbox with modes is not "
                         "built and nothing is made.")
    missing = _settled(MODES_FINDINGS + SENSE_FINDINGS + SENSE_REMAKE_FINDINGS)
    if missing is not None:
        raise BuildError(f"A gearbox with modes needs findings.{missing[0]} settled on SolidWorks (it is "
                         f"{missing[1]!r}), so it is not built and nothing is made.")
    refusal = _modes_version_refusal(revision)
    if refusal is not None:
        raise BuildError(refusal)


def _build_in_job(sw: SolidWorks, plan: BuildPlan, exists: Callable[[str], bool],
                  kind: Optional[str] = None, gears: Optional[Mapping[str, str]] = None,
                  senses: Optional[Mapping[str, bool]] = None, *, modes: Optional[ModesPlan] = None,
                  mode_checks: Optional[List[ModeCheck]] = None,
                  progress: Optional[Callable[[Step], None]] = None) -> BuildResult:
    """:func:`build`, for one document of a job that has already saved others: what :func:`build` raises (its
    template is not there, SolidWorks would not make the document, the path was taken since the job's own check)
    comes back as a failed :class:`BuildResult` instead, so the job still reports, and the record still keeps,
    the documents saved before it.

    On SolidWorks 2026 (34.0.0, probe/workbook_assembly_check.py 2026-11-13) a workbook build whose assembly
    template was not there raised "There is no assembly template at …" out of ``build_gearbox`` after its four
    parts and its layout part had saved, so the window's finish never ran and none of the five was on record.
    Any other raise is caught too (W4 review B1: a ``pywintypes.com_error`` part-way through orphaned every file
    already saved), with its type named.
    """
    try:
        return build(sw, plan, exists, kind=kind, gears=gears, senses=senses, modes=modes, mode_checks=mode_checks,
                     progress=progress)
    except Exception as exc:  # noqa: BLE001 - see the docstring
        first = plan.ops[0] if plan.ops else None
        what = ("new part" if isinstance(first, base.NewPart) else "new assembly"
                if isinstance(first, base.NewAssembly) else "the build")
        save = next((op for op in plan.ops if isinstance(op, base.SaveAs)), None)
        return BuildResult(kind=plan.kind, recipe=plan.recipe, path=save.path if save else "",
                           failures=[(what, _said(exc))], stopped_at=what,
                           manual=[op.text for op in plan.manual_steps()])


def _run(sw: SolidWorks, plan: BuildPlan, result: BuildResult, kind: str,
         made: Optional[Dict[str, str]] = None,
         sense: Optional[Tuple[Mapping[str, bool], Mapping[str, Vec3], Mapping[str, str],
                               Mapping[str, Vec3]]] = None) -> None:
    """Every op in order, stopping at the first failure. ``made`` collects each ``Mate`` op's id and the name its
    mate kept (for the train's mate check). In a train, a mate SolidWorks would not make (``swcom.MateRefused``)
    is a mate problem as well as the failure; any other raise is the failure alone (W5-INTERFACES). ``sense``
    (each gear mate's same sense, each handle's planned axis, the gears map, each handle's planned origin): each
    gear mate's sense is
    read straight after it is made, as probe ring_mate_sense read it (:func:`_settle_sense`); a sense SolidWorks
    gets wrong with either Flip is a mate problem too."""
    sw.set_rebuild_suppressed(True)
    try:
        for op in plan.ops[1:]:
            runner = _RUNNERS.get(type(op))
            if runner is None:  # ManualStep, Rebuild, SaveAs: counted or done around the loop
                continue
            try:
                if runner is _place:
                    result.done.append(_place(sw, op, result, result.trig, kind))
                else:
                    result.done.append(runner(sw, op, result, result.trig))
                    if made is not None and isinstance(op, base.Mate):
                        made[op.id] = result.features[-1]
                    if sense is not None and isinstance(op, base.Mate) and op.kind == "gear":
                        _settle_sense(sw, op, result.features[-1], sense, result)
            except SolidWorksError as exc:
                label = base.describe(op, result.trig)
                result.failures.append((label, str(exc)))
                result.stopped_at = label
                if kind == ASSEMBLY_TRAIN and isinstance(op, base.Mate) and isinstance(exc, _SenseRefused):
                    result.mate_problems.append(str(exc))
                elif kind == ASSEMBLY_TRAIN and isinstance(op, base.Mate) and isinstance(exc, MateRefused):
                    result.mate_problems.append(f"SolidWorks would not make the mate {op.name or op.id}.")
                return
    finally:
        sw.set_rebuild_suppressed(False)


class _SenseRefused(SolidWorksError):
    """SolidWorks turns a gear mate's gears against their mesh with either Flip, or reads its axes otherwise than
    the plan placed them: a refusal that repeats on every press, so a mate problem."""


SENSE_FINDINGS = (("GEAR_MATE_SENSE_READ_BACK", "(Reverse == entities parallel) == internal"),
                  ("GEAR_MATE_READ_BACK_TELLS_SENSE", True))
# A gear mate read wrong is made again with the other Flip (ring_mate_sense's fallback), by swcom's remake.
SENSE_REMAKE_FINDINGS = (("GEAR_MATE_CHECK_AND_REMAKE_HOLDS", True), ("MATE_DELETE_ROUTE", "Select2 then EditDelete()"),
                         ("MATE_RENAME_ROUTE", "IFeature.Name put"))


def _sense_settled() -> bool:
    """Whether a gear mate's sense can be read back (probe ring_mate_sense's findings, read with getattr)."""
    return _settled(SENSE_FINDINGS) is None


def _sense_gate(plan: BuildPlan, senses: Optional[Mapping[str, bool]]) -> Optional[Dict[str, bool]]:
    """Before anything is made; returns each gear mate's same sense as given, or None when none is.

    First, whatever is given (W6-INTERFACES §7.3), every gear mate's two planned axes (each handle's last ``Place``):
    a gear mate between gears whose axes are not of one family (:func:`swcom.axes_parallel`, planning's rule, §7.5)
    is refused with its sentence while its sense cannot be read — the turned finding missing, or the angle between
    the own axes outside the angles it covers (:func:`swcom.turned_refusal`; W6-PLAN §2.6, D16, D18) — and refused
    as a fault when it can be read but nothing says which way it turns. Then W5's rule for the rest: with the
    read-back settled, a train with gear mates needs the remake's findings too (a wrong one is made again with the
    other Flip); without it, a train with a mesh inside a ring is refused, since no Flip chosen before the mate is
    made is right on both versions (findings.GEAR_MATE_FLIP_STATIC_RULE None) and its sense cannot be told."""
    gear_mates = [op for op in plan.ops if isinstance(op, base.Mate) and op.kind == "gear"]
    given = None if senses is None else {str(name): bool(same) for name, same in senses.items()}
    if not gear_mates:
        return given
    axes, origins = _planned_axes(plan), _planned_origins(plan)
    turned: List[str] = []
    for op in gear_mates:
        name = op.name or op.id
        ga, gb = _mate_axes(op, name, axes)
        if not axes_parallel(ga, gb):
            oa, ob = _mate_axes(op, name, origins)
            refusal = turned_refusal(name, own_axes_angle(ga, gb), "so nothing is made or changed.",
                                     meet=lines_meet(oa, ga, ob, gb))
            if refusal is not None:
                raise BuildError(refusal)
            turned.append(name)
    if given is None:
        if turned:
            raise BuildError(f"The gear mate {turned[0]} joins gears on shafts at an angle, and the build was not told "
                             "which way it turns them, so nothing is made; that is a fault in Gear Generator.")
        return None
    for op in gear_mates:
        if (op.name or op.id) not in given:
            raise BuildError(f"The build was not told which way the gear mate {op.name or op.id} turns its gears, so "
                             "nothing is made; that is a fault in Gear Generator.")
    missing = _settled(SENSE_FINDINGS)
    if missing is not None:
        rings = [op.name or op.id for op in gear_mates
                 if _inside_ring(given[op.name or op.id], *_mate_axes(op, op.name or op.id, axes))]
        if rings:
            raise BuildError(f"The gear mate {rings[0]} meshes inside a ring, and which way a gear mate turns a ring "
                             f"cannot be told on SolidWorks yet (findings.{missing[0]} is {missing[1]!r}), so nothing "
                             "is made or changed; run probe ring_mate_sense first.")
        return given
    missing = _settled(SENSE_REMAKE_FINDINGS)
    if missing is not None:
        raise BuildError(f"A gearbox built to turn needs findings.{missing[0]} settled on SolidWorks (it is "
                         f"{missing[1]!r}), so nothing is made or changed; run probe tier 8 first.")
    return given


def _inside_ring(same: bool, axis_a: Sequence[float], axis_b: Sequence[float]) -> bool:
    """A parallel mesh is inside a ring exactly when its same sense agrees with its two axes pointing alike."""
    return axes_parallel(axis_a, axis_b) and bool(same) == (sum(p * q for p, q in zip(axis_a, axis_b)) > 0)


def _axis_of(rotation: Sequence[float]) -> Vec3:
    """A gear's own +Z: its frame's third column (W6-PLAN §4.3's convention for every ``Place`` and ``Placement``)."""
    return (float(rotation[2]), float(rotation[5]), float(rotation[8]))


def _planned_axes(plan: BuildPlan) -> Dict[str, Vec3]:
    """Each handle's own +Z as the plan places it: its last ``Place``'s third column."""
    out: Dict[str, Vec3] = {}
    for op in plan.ops:
        if isinstance(op, base.Place):
            out[op.component] = _axis_of(op.rotation)
    return out


def _planned_origins(plan: BuildPlan) -> Dict[str, Vec3]:
    """Each handle's origin as the plan places it (its last ``Place``): a point on its axis, so with
    :func:`_planned_axes` the gear's axis as a line (a bevel gear's origin is its apex)."""
    out: Dict[str, Vec3] = {}
    for op in plan.ops:
        if isinstance(op, base.Place):
            out[op.component] = tuple(float(v) for v in op.at)
    return out


def _mate_axes(op: base.Mate, name: str, axes: Mapping[str, Vec3]) -> Tuple[Vec3, Vec3]:
    """The planned axes (or origins) of a gear mate's two gears, its first gear first; a gear the plan never places
    is a fault."""
    ga, gb = axes.get(op.a.partition(":")[0]), axes.get(op.b.partition(":")[0])
    if ga is None or gb is None:
        raise BuildError(f"The gear mate {name} joins a gear the plan never places, so which way it turns cannot be "
                         "told and nothing is made; that is a fault in Gear Generator.")
    return ga, gb


def _vector(v: Sequence[float]) -> str:
    return "(" + ", ".join(f"{round(float(x), 3) + 0.0:g}" for x in v) + ")"


def _sense_read(sw: SolidWorks, handle: str, name: str, same: bool, axis_a: Sequence[float],
                axis_b: Sequence[float], gear_a: str, gear_b: str, refusal: type,
                origins: Optional[Tuple[Sequence[float], Sequence[float]]] = None) -> bool:
    """One read of a gear mate's sense against its gears' own axes as placed (``swcom.sense_reading``'s rule H,
    which is W5's rule on parallel axes): whether it turns them as they mesh. A turned mate is read with whether its
    planned axes meet (``origins``, a point on each; :func:`swcom.lines_meet`), which picks the angles its gate
    reads. A mate whose entities are not one along each gear's axis does not hold the axes the plan asked for, and
    nothing is guessed: ``refusal`` with a sentence naming the gears (W6-PLAN §2.9)."""
    meet = None
    if origins is not None and not axes_parallel(axis_a, axis_b):
        meet = lines_meet(origins[0], axis_a, origins[1], axis_b)
    try:
        right, _ = sw.gear_mate_sense(handle, bool(same), (tuple(axis_a), tuple(axis_b)), meet=meet)
    except SenseUnreadable as exc:
        raise refusal(_unreadable(name, exc, gear_a, gear_b)) from None
    return bool(right)


def _unreadable(name: str, exc: SenseUnreadable, gear_a: str, gear_b: str) -> str:
    """The read-back's refusal, naming the gears (W6-PLAN §2.9) where :func:`swcom.sense_reading` could name only
    the axes."""
    found, wanted = list(exc.directions), list(exc.axes)
    if len(found) != 2 or len(wanted) != 2:
        return str(exc)

    def along(d: Sequence[float], g: Sequence[float]) -> bool:
        return abs(sum(p * q for p, q in zip(d, g))) >= ENTITY_ALONG

    stray = next((d for d in found if not any(along(d, g) for g in wanted)), None)
    if stray is not None:
        return (f"SolidWorks reads an axis of the gear mate {name} as pointing {_vector(stray)}, which is not along "
                f"{gear_a}'s axis {_vector(wanted[0])} or {gear_b}'s {_vector(wanted[1])}, so the mate does not hold "
                "the axes the gears were placed on, and nothing is guessed.")
    gear, axis = (gear_a, wanted[0]) if all(along(d, wanted[0]) for d in found) else (gear_b, wanted[1])
    return (f"SolidWorks reads both axes of the gear mate {name} as along {gear}'s axis {_vector(axis)}, where it "
            f"should hold one along {gear_a}'s and one along {gear_b}'s, so the mate does not hold the axes the gears "
            "were placed on, and nothing is guessed.")


def _settle_sense(sw: SolidWorks, op: base.Mate, name: str,
                  sense: Tuple[Mapping[str, bool], Mapping[str, Vec3], Mapping[str, str]], result: BuildResult) -> None:
    """A gear mate just made (and renamed), read where probe ring_mate_sense read it — before any rebuild: wrong,
    it is made again with the other Flip (``GEAR_MATE_CHECK_AND_REMAKE_HOLDS``) and read again; wrong again, the
    build stops with a mate problem naming it (the user's answer 1)."""
    senses, axes, gears, origins = sense
    ha, hb = op.a.partition(":")[0], op.b.partition(":")[0]
    ends = (origins[ha], origins[hb])
    ga, gb = gears.get(ha) or result.components.get(ha) or ha, gears.get(hb) or result.components.get(hb) or hb
    same = senses.get(op.name or op.id, senses.get(name))
    if _sense_read(sw, op.id, name, same, axes[ha], axes[hb], ga, gb, _SenseRefused, ends):
        return
    sw.remake_gear_mate(op.id, op.a, op.b, op.ratio, not op.flip, saved=False)
    result.turned_round.append(name)
    if not _sense_read(sw, op.id, name, same, axes[ha], axes[hb], ga, gb, _SenseRefused, ends):
        raise _SenseRefused(f"SolidWorks turns the gears of the mate {name} against the way they mesh, whichever way "
                            "round the mate is made.")


def _mated_handles(plan: BuildPlan) -> List[str]:
    """Each handle a ``Mate`` op names (a lock's bare handles, else the part before ``:``; never the assembly's own
    ``asm``) whose last ``Fix``/``Unfix`` op is ``Unfix``: the gears meant to turn, in the order first mated."""
    last: Dict[str, str] = {}
    for op in plan.ops:
        if isinstance(op, (base.Fix, base.Unfix)):
            last[op.component] = "unfix" if isinstance(op, base.Unfix) else "fix"
    out: List[str] = []
    for op in plan.ops:
        if not isinstance(op, base.Mate):
            continue
        refs = (op.a, op.b) if op.kind == "lock" else (op.a.partition(":")[0], op.b.partition(":")[0])
        for handle in refs:
            if handle != "asm" and last.get(handle) == "unfix" and handle not in out:
                out.append(handle)
    return out


def _mate_problems(sw: SolidWorks, names: Sequence[str], statuses: bool) -> Tuple[List[str], List[MateState]]:
    """The mate check's findings for the mates ``names`` (W5-PLAN §1.4, W5-INTERFACES): with ``statuses``, each
    one's AddMate5 status (``findings.ADD_MATE_NO_ERROR`` or a sentence: 5 over-defines, anything else its number);
    then ``mate_states()`` — each present and not suppressed, and every mate with a non-zero error code, naming
    those whose ``warning`` is False as at fault (all of them when none is), its number never read into. Returns
    the sentences and the states read. Raises what SolidWorks raises (an ordinary failure, never a problem)."""
    problems: List[str] = []
    told = set()
    if statuses:
        for name in names:
            sentence = _status_sentence(name, sw.mate_status(name))
            if sentence is None:
                continue
            told.add(name)
            problems.append(sentence)
    states = list(sw.mate_states())
    by_name = {state.name: state for state in states}
    for name in names:
        state = by_name.get(name)
        if state is None:
            problems.append(f"The mate {name} is missing from the assembly.")
            told.add(name)
        elif state.suppressed:
            problems.append(f"The mate {name} is suppressed in SolidWorks.")
            told.add(name)
    flagged = [state for state in states if state.code]
    for state in [s for s in flagged if not s.warning] or flagged:
        if state.name not in told:
            problems.append(f"The mate {state.name} is in error in SolidWorks.")
    return problems, states


def _status_sentence(name: str, status: Optional[int]) -> Optional[str]:
    """A mate's AddMate5 status as the mate check says it: None for ``findings.ADD_MATE_NO_ERROR``, else a sentence
    (over-defines; no answer; any other number given as it came)."""
    if status == findings.ADD_MATE_NO_ERROR:
        return None
    if status == findings.ADD_MATE_OVER_DEFINED:
        return f"The mate {name} over-defines the assembly."
    if status is None:
        return f"SolidWorks gave no answer when making the mate {name}."
    return f"SolidWorks answered {status} when making the mate {name}."


def _free_to_turn(sw: SolidWorks, handles: Sequence[str], gear_of: Callable[[str], str]) -> List[str]:
    """Each handle's constrained status must be ``findings.COMPONENT_UNDER_DEFINED``: a sentence per gear that is
    not, naming it by ``gear_of``."""
    problems: List[str] = []
    for handle in handles:
        status = sw.constrained_status(handle)
        if status == findings.COMPONENT_UNDER_DEFINED:
            continue
        gear = gear_of(handle)
        if status == findings.COMPONENT_OVER_DEFINED:
            problems.append(f"{gear} is over-defined in SolidWorks.")
        elif status == findings.COMPONENT_FULLY_DEFINED:
            problems.append(f"{gear} cannot turn: SolidWorks reads it fully defined.")
        else:
            problems.append(f"{gear} reads {status} in SolidWorks, not free to turn.")
    return problems


def _check_mates(sw: SolidWorks, plan: BuildPlan, result: BuildResult, made: Mapping[str, str],
                 gears: Mapping[str, str]) -> None:
    """A train's mate check, after the rebuild and before the save (:func:`build`): every mate's status and state,
    every mated gear free to turn. Each problem is a sentence in ``mate_problems`` and a failure; ``mates`` keeps
    what was read, for the log."""
    names = [made.get(op.id, op.name or op.id) for op in plan.ops if isinstance(op, base.Mate)]
    problems, result.mates = _mate_problems(sw, names, statuses=True)
    problems += _free_to_turn(sw, _mated_handles(plan),
                              lambda handle: gears.get(handle) or result.components.get(handle) or handle)
    for problem in problems:
        result.mate_problems.append(problem)
        result.failures.append(("the mate check", problem))
    if not problems:
        result.done.append("every mate sound, every gear free to turn")


def _verify(sw: SolidWorks, plan: BuildPlan, result: BuildResult) -> None:
    """Every global's value against the maths, and every sketch's definition."""
    if not result.ok:
        return
    try:
        expected = plan.values(result.trig)
    except EquationError as exc:
        result.failures.append(("the maths", str(exc)))
        return
    got = sw.equation_values()
    for name, value in expected.items():
        if name not in got:
            result.failures.append((f"\"{name}\"", "is not in the Equation Manager after the rebuild."))
        elif abs(got[name] - value) > VALUE_TOLERANCE * max(1.0, abs(value)):
            result.failures.append((f"\"{name}\"", f"SolidWorks has {got[name]!r} where the maths says {value!r}."))
    if expected and result.ok:
        result.done.append(f"{len(expected)} globals read back and match the maths")
    for op in plan.ops:
        if isinstance(op, base.CloseSketch):
            status = sw.sketch_status(op.name)
            if status != FULLY_DEFINED:
                word = {2: "under-defined", 4: "over-defined"}.get(status, f"in state {status}")
                result.checks.append(f"{op.name} is {word}, not fully defined")
            else:
                result.done.append(f"{op.name} is fully defined")


def build_pair(sw: SolidWorks, gear_a: BuildPlan, gear_b: BuildPlan, assembly: BuildPlan,
               exists: Callable[[str], bool] = os.path.exists) -> PairResult:
    """Both parts, then the assembly — skipped if either part failed — then whether the teeth interfere.

    An assembly that built cleanly is checked for interference (probe
    interference): none is a line in ``done``, and any is a ``CHECK`` with the
    count and volume, which does not fail the build — the parts are still the
    gears asked for, and the sentence says where to look.
    """
    for plan in (gear_a, gear_b, assembly):
        save = next((op for op in plan.ops if isinstance(op, base.SaveAs)), None)
        if save is not None and save.path and exists(save.path):
            raise BuildError(f"{save.path} already exists, and a build never overwrites a file.")
    # Before the gears, not after them at the assembly: a bad PAIR_ASSEMBLY_REBUILD_ROUTE would otherwise leave two
    # saved gears behind, which the next Build refuses to overwrite. It never refuses while that finding is absent.
    _assembly_rebuild_gate(ASSEMBLY_PAIR)
    pair = PairResult(gear_a=build(sw, gear_a, exists))
    if not pair.gear_a.ok:
        pair.skipped = "the second gear and the assembly, because the first gear failed"
        return pair
    pair.gear_b = build(sw, gear_b, exists)
    if not pair.gear_b.ok:
        pair.skipped = "the assembly, because the second gear failed"
        return pair
    # A pair for every rebuild and put, whatever the plan holds (a crossed pair placed fixed has no mate): the full
    # rebuild every pair result on record ran (probe tiers 4 and 5), never the workbook train's route.
    pair.assembly = build(sw, assembly, exists, kind=ASSEMBLY_PAIR)
    if pair.assembly.ok and findings.INTERFERENCE_CHECKED:
        try:
            count, volume = sw.interference_count()
        except SolidWorksError as exc:
            pair.assembly.checks.append(f"interference could not be checked: {exc}")
        else:
            if count:
                pair.assembly.checks.append(
                    f"the gears interfere in {count} place{'s' if count != 1 else ''}, {volume:.3f} mm³; "
                    "look along the gear axis at the mesh")
            else:
                pair.assembly.done.append("no interference between the gears")
    return pair


@dataclass
class ManyResult:
    """A batch of parts (a workbook's, phase W2): each one's result in order, and what was not reached."""

    built: List[BuildResult] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)      # paths not attempted, after a failure

    @property
    def ok(self) -> bool:
        return bool(self.built) and all(r.ok for r in self.built) and not self.skipped

    def log_lines(self) -> List[str]:
        lines: List[str] = []
        for result in self.built:
            lines.extend(result.log_lines())
        if self.skipped:
            lines.append(f"SKIPPED {len(self.skipped)} part(s) after a failure: "
                         + ", ".join(os.path.basename(p) for p in self.skipped))
        return lines


def build_many(sw: SolidWorks, plans: Sequence[BuildPlan],
               exists: Callable[[str], bool] = os.path.exists, *,
               progress: "Optional[Callable[[Step], None]]" = None,
               into: Optional[ManyResult] = None) -> ManyResult:
    """Every plan's part in order, each by :func:`build`; the first that fails stops the rest.

    Every path is checked before anything is made, so a batch either starts
    with nothing in the way or does not start: a build never overwrites a file
    (``findings.SAVE_AS_OVERWRITES`` is True, so this check is the only guard).
    ``progress``, if given, is told ``Step(STAGE_PART, stem, i, n)`` as each
    part starts.

    ``into`` is for a job that has done its own checks first
    (:func:`build_gearbox`): each part's result is put in it as soon as it is
    known, so whatever raises later loses none of the parts already saved,
    and the first part too goes through :func:`_build_in_job`, which never
    raises. Without it, W2's batch, the first part's :class:`BuildError`
    (nothing made) still raises.
    """
    paths = []
    for plan in plans:
        save = next((op for op in plan.ops if isinstance(op, base.SaveAs)), None)
        path = save.path if save is not None else ""
        if path and exists(path):
            raise BuildError(f"{path} already exists, and a build never overwrites a file.")
        if path and any(same_path(path, p) for p in paths):
            raise BuildError(f"Two parts in this batch would both be saved as {path}.")
        paths.append(path)
    many = into if into is not None else ManyResult()
    for index, plan in enumerate(plans):
        if progress is not None:
            progress(Step(STAGE_PART, _stem(paths[index] or plan.path), index + 1, len(plans)))
        in_job = into is not None or bool(many.built)
        result = _build_in_job(sw, plan, exists) if in_job else build(sw, plan, exists)
        many.built.append(result)
        if not (result.ok and result.saved):
            many.skipped = [p for p in paths[index + 1:]]
            break
    return many


# -- changing values in a built part ----------------------------------------


STRUCTURAL = ("kind", "recipe", "hand", "teeth_side")


def structural_change(built: Mapping[str, str], wanted: Mapping[str, str]) -> str:
    """Why a change cannot go through the equations, as a sentence; empty when it can.

    The sketch's topology is fixed when it is built: another recipe or kind is
    different entities, and a bore that appears or vanishes is a feature that
    is not there.
    """
    for key in STRUCTURAL:
        # A record written before a key existed held its default: external teeth.
        default = "external" if key == "teeth_side" else ""
        if str(built.get(key, default) or default) != str(wanted.get(key, default) or default):
            return (f"The {key} changed from {built.get(key)!r} to {wanted.get(key)!r}; "
                    "build it again as a new part.")

    def has_bore(values: Mapping[str, str]) -> bool:
        text = str(values.get("bore", "")).strip()
        try:
            return bool(text) and float(text) > 0
        except ValueError:
            return False

    if has_bore(built) != has_bore(wanted):
        return ("A bore cannot be added to or removed from a built part through its values; "
                "build it again as a new part.")

    def has_shift(values: Mapping[str, str]) -> bool:
        text = str(values.get("profile_shift", "")).strip()
        try:
            return bool(text) and float(text) != 0
        except ValueError:
            return False

    # An unshifted part has no "Profile Shift" global for a new value to go into.
    if has_shift(built) != has_shift(wanted):
        return ("Profile shift cannot be added to or taken out of a built part through its values; "
                "build it again as a new part.")

    def has_groove(values: Mapping[str, str]) -> bool:
        text = str(values.get("groove", "")).strip()
        try:
            return bool(text) and float(text) != 0
        except ValueError:
            return False

    # A groove is a hub feature and a shorter blank: features, not values.
    if has_groove(built) != has_groove(wanted):
        return ("A centre groove cannot be added to or taken out of a built part through its values; "
                "build it again as a new part.")
    # An arc built for a small pinion still closes the space at more teeth (SolidWorks 2024
    # rebuilt 6 → 7 → 12 → 6 through the values); a chord does not at fewer. The record
    # holds the last values, not the build's, so an arc part taken up to 12 and back to 6
    # is refused too: safe, if stricter than it needs to be.
    if _caps_with_arc(built) is False and _caps_with_arc(wanted) is True:
        return ("At these values the teeth are too few to be cut by changing this part's values; build it again as "
                "a new part.")
    return ""


def _caps_with_arc(values: Mapping[str, str]) -> Optional[bool]:
    """Whether the form's tooth space closes with an arc on the tip cap; None when that does not apply.

    A pinion too small for a chord (:func:`spur.caps_with_arc`) gets an arc,
    which is other entities in the sketch: a part built with a chord and
    changed to six teeth through its values would keep the chord, inside the
    tips, and leave material in the mouth of every space. The other way is
    fine, since the arc clears the tips at any tooth count.
    """
    from .gears import kind_for, spur
    from .spec import GearSpec

    try:
        spec = GearSpec.from_dict(dict(values))
        kind = kind_for(spec)
        if kind is None or spec.is_internal():
            return None
        derived = kind.derive(spec)
        section = getattr(derived, "section", derived)
        if not isinstance(section, spur.SpurDerived):
            return None
        return spur.caps_with_arc(section, kind.recipe_for(spec))
    except Exception:  # noqa: BLE001 - a record or form that does not work out says nothing here
        return None


def planned_changes(current: Sequence[Tuple[str, float]], variables: Sequence[GlobalVariable],
                    trig: str) -> List[Tuple[str, str]]:
    """The globals whose text differs from what the part holds, as (name, expression)."""
    held: Dict[str, str] = {}
    for text, _ in current:
        try:
            name, expression = split_equation(text)
        except (ValueError, EquationError):
            continue
        held[name] = expression
    out = []
    for variable in variables:
        expression = variable.expression_for(trig)
        if variable.name not in held:
            raise BuildError(f"\"{variable.name}\" is not in this part, so it was not built by this tool "
                             "or its equations were edited.")
        if _squash(held[variable.name]) != _squash(expression):
            out.append((variable.name, expression))
    return out


def _squash(text: str) -> str:
    return "".join(text.split())


def update_variables(sw: SolidWorks, variables: Sequence[GlobalVariable], expected_path: str) -> UpdateResult:
    """Set a built part's globals from the form, in one suppressed batch, and rebuild once.

    Refuses unless the active document is the part the record describes: a
    wrong document would take the values silently where names happened to match.
    """
    _gate(sw)
    active = sw.active_document()
    if active is None:
        raise BuildError("No document is open in SolidWorks; open the gear's part first.")
    if not active.path or not same_path(active.path, expected_path):
        raise BuildError(f"The active document is {active.title}, not {os.path.basename(expected_path)}; "
                         "open the gear's part and try again.")
    result = UpdateResult(document=active.title)
    sw.begin_build()
    try:
        result.trig = sw.detect_trig_units()
        changes = planned_changes(sw.equations(), variables, result.trig)
        names = {name for name, _ in changes}
        result.unchanged = [v.name for v in variables if v.name not in names]
        try:
            evaluate_all([(v.name, v.expression_for(result.trig)) for v in variables], result.trig)
        except EquationError as exc:
            raise BuildError(f"The new values do not evaluate: {exc}") from None
        if not changes:
            return result
        sw.set_rebuild_suppressed(True)
        try:
            for name, expression in changes:
                try:
                    sw.set_global_variable(name, expression)
                    result.changed.append(name)
                except Exception as exc:  # noqa: BLE001 - what was set stays listed in ``changed`` (B1)
                    result.failures.append((f"\"{name}\"", _said(exc)))
        finally:
            sw.set_rebuild_suppressed(False)
        result.rebuilt = bool(sw.rebuild())
    finally:
        sw.end_build()
    return result


# -- a workbook's gearbox: parts, layout part and static assembly (phase W4) ---------
#
# docs/PLAN-WORKBOOK.md §4.2–§4.5. The shapes were pinned in one interface commit before the work was split;
# the worker's side is here, from probe tier 7. Planning is pure and runs on the Tk thread (workbook.gearbox,
# workbook.update); everything here that takes ``sw`` runs on the worker thread, as one job, and is given plain
# data — never a workbook type — so swbuild stays below the workbook package.

POSE_TOLERANCE = 1e-6        # mm for an origin, and per matrix entry (≈ radians) for a rotation

# What the worker is doing, for the footer (ui_text turns a Step into its sentence).
STAGE_CHECK = "check"                 # opening a document already built and checking it holds what is expected
STAGE_PART = "part"                   # building part ``index`` of ``count``
STAGE_LAYOUT = "layout"               # building the layout part
STAGE_ASSEMBLY = "assembly"           # building the assembly
STAGE_INTERFERENCE = "interference"   # checking the assembly for interference
STAGE_VALUES = "values"               # Update: setting a part's or the layout's globals
STAGE_PLACE = "place"                 # Update: re-placing components in the assembly
STAGE_CARRIER = "carrier"             # W7: building a carrier part (Step.name: its stem)
STAGE_MODE = "mode"                   # W8: setting up or checking a mode's configuration (Step.name: the mode's name)
STAGES = (STAGE_CHECK, STAGE_PART, STAGE_LAYOUT, STAGE_ASSEMBLY, STAGE_INTERFERENCE, STAGE_VALUES, STAGE_PLACE,
          STAGE_CARRIER, STAGE_MODE)


@dataclass(frozen=True)
class Step:
    """One thing the worker has started. ``name`` is the document's file stem (``Gear_m1.5_N68``), or ``""``;
    ``index`` counts from 1 among ``count`` for STAGE_PART, STAGE_CHECK and STAGE_MODE (``name`` the mode's), and is
    0 otherwise."""

    stage: str
    name: str = ""
    index: int = 0
    count: int = 0


class Progress:
    """The last :class:`Step` a worker job said, for the Tk thread's poll to read.

    One attribute, replaced whole by the worker and only read by Tk, so no
    lock is needed under the GIL. Make one per job and pass its ``say`` to
    :func:`build_gearbox` or :func:`update_gearbox`; never share one as a
    default argument (it would outlive the job and leak its last step into
    the next).
    """

    def __init__(self) -> None:
        self.step: Optional[Step] = None

    def say(self, step: Step) -> None:
        self.step = step


@dataclass(frozen=True)
class DocumentValues:
    """A saved document and the globals it should hold, in a workbook build or update.

    In :func:`build_gearbox` (a reused part or layout) it must already hold
    every one exactly — ``planned_changes(sw.equations(), variables, trig) ==
    []`` in the document's own trig units — and every name in ``features``
    (a reused layout's planes and axes); otherwise nothing is built. In
    :func:`update_gearbox` the variables are what it is to hold afterwards,
    and only those that differ are set. ``path`` is the absolute Windows path.
    """

    path: str
    variables: Tuple[GlobalVariable, ...] = ()
    features: Tuple[str, ...] = ()


@dataclass(frozen=True)
class Placement:
    """Where one gear's component belongs in a built assembly: the rotation's 9 numbers by rows and its origin
    in mm (as :class:`gears.base.Place`), found by the ``Name2`` recorded at insertion. ``pitch`` is the gear's
    angular pitch in degrees (360 / teeth): a frame turned a whole number of pitches about the part's own axis
    is the same placement (:func:`same_frame`). 0 compares exactly."""

    gear: str
    component: str
    rotation: Tuple[float, ...]
    at: Tuple[float, float, float]
    pitch: float = 0.0


@dataclass(frozen=True)
class Clash:
    """One clash in an assembly: every interference SolidWorks found between the same components, merged
    (:func:`_clashes`). ``components`` are the ``Name2``s SolidWorks gave (``()`` when the names
    could not be read, ``findings.INTERFERENCE_NAMES_ROUTE``); ``gears`` the workbook's gear ids for them, in
    the same order, where the caller's map knows them (else the Name2 itself). ``volume`` in mm³."""

    components: Tuple[str, ...]
    gears: Tuple[str, ...]
    volume: float


def turn_between(rotation_a: Sequence[float], rotation_b: Sequence[float],
                 tolerance: float = POSE_TOLERANCE) -> Optional[float]:
    """The turn about frame a's own Z (its gear axis) that takes rotation a to rotation b, in radians in (−π, π]
    — positive the right-handed way about a's own +Z — or None when the two differ otherwise (a tilt, a gear
    turned over): ``M = Raᵀ·Rb`` must be a turn about local Z to ``tolerance`` per entry. Rotations are 9 numbers
    by rows, ``v_global = R · v_local + at``, as everywhere here. Pure (W5; :func:`same_frame` and
    :func:`train_check` both rest on it)."""
    ra = [[float(rotation_a[i * 3 + j]) for j in range(3)] for i in range(3)]
    rb = [[float(rotation_b[i * 3 + j]) for j in range(3)] for i in range(3)]
    # M = Ra^T Rb: the turn, in a's own frame, that takes a to b. It must be a turn about local Z.
    m = [[sum(ra[k][i] * rb[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    turn = math.atan2(m[1][0], m[0][0])
    c, s = math.cos(turn), math.sin(turn)
    about_z = ((c, -s, 0.0), (s, c, 0.0), (0.0, 0.0, 1.0))
    if any(abs(m[i][j] - about_z[i][j]) > tolerance for i in range(3) for j in range(3)):
        return None
    return turn


def same_frame(rotation_a: Sequence[float], at_a: Sequence[float], rotation_b: Sequence[float],
               at_b: Sequence[float], pitch: float = 0.0, tolerance: float = POSE_TOLERANCE) -> bool:
    """Whether two component frames place the same gear the same way.

    The origins must agree to ``tolerance`` mm on each axis. The rotations
    must differ only by a turn about the part's own Z (its gear axis) of a
    whole number of ``pitch`` degrees — a gear turned one tooth is the same
    gear in the same place (review 14: comparing θ itself would call
    2.5e-14 and one whole pitch different). ``pitch`` 0 asks for the same
    rotation. Rotations are 9 numbers by rows, ``v_global = R · v_local + at``.
    The turn is :func:`turn_between`'s.
    """
    if any(abs(float(a) - float(b)) > tolerance for a, b in zip(at_a, at_b)):
        return False
    turn = turn_between(rotation_a, rotation_b, tolerance)
    if turn is None:
        return False
    if pitch <= 0:
        return abs(turn) <= tolerance
    step = math.radians(pitch)
    off = turn % step
    return min(off, step - off) <= tolerance


# -- W5: whether a mated train stands as built, up to a turn (W5-PLAN §1.6, review M1/M2) -----------------------

TRAIN_TOLERANCE = 1e-5     # radians on each relation; the demonstration logs the residuals it sees (W5-PLAN §4)


@dataclass(frozen=True)
class MeshLink:
    """One listed, gear-mated mesh (a, b) as :func:`train_check` reads it: b turns ``k`` times a's turn, each
    about its OWN part's +Z (review M2: ``k == ω_b/ω_a`` with ``kinematics.solve``'s speeds, which are about each
    shaft's own axis; ``workbook.motion.mesh_links`` makes them), and ``pitch`` is b's angular pitch in degrees
    (360 / b's teeth): the relation holds modulo it, since a whole tooth of a times k is a whole tooth of b.

    W7: ``carrier`` is a :class:`CarrierLink` ``carrier`` id when the mesh is measured against that carrier (a
    planetary mesh: a planet copy and a sun or ring), else ``""``. Then ``k`` is the ratio of turns RELATIVE TO
    THE CARRIER (``k = −c·za/zb`` with ``c`` the carrier-frame sense, W6's parallel rule), and
    :func:`train_check` takes each gear's turn relative to the carrier (W7-INTERFACES.md §3)."""

    a: str
    b: str
    k: float
    pitch: float
    carrier: str = ""
    # W8 (W8-INTERFACES.md §3): the configurations (modes) this link holds in — a coupling's or a sliding mesh's
    # on-set — and () for one on in every configuration; :func:`links_in` is the one rule that reads it.
    modes: Tuple[str, ...] = ()


@dataclass(frozen=True)
class LockLink:
    """One lock mate: ``follower`` is held to ``anchor``. :func:`train_check` tests it EXACTLY (review M1: the
    follower's turn equals the anchor's, to tolerance, never modulo a pitch); ``pitch`` is the follower's angular
    pitch in degrees, kept for the log and for W8, and not used by the test."""

    anchor: str
    follower: str
    pitch: float
    # W8: as MeshLink.modes (a spline is a LockLink, on in every configuration, so () in practice; kept for the rule).
    modes: Tuple[str, ...] = ()


@dataclass(frozen=True)
class TrainCheck:
    """What :func:`train_check` found. ``off_axis``: gears not at their place or not along their axis (or not
    found at all), in ``wanted``'s order; their relations are not judged. ``out_of_step``: (a, b) meshes and
    (anchor, follower) locks whose relation does not hold, in the order given (meshes first). ``turned``: in step,
    and some gear stands turned other than by a whole number of its own pitch. ``residuals``: every relation
    judged, (a, b, residual in radians) — a mesh's distance from the nearest whole pitch of b, a lock's from no
    difference at all — meshes then locks, for the log (the demonstration reports what a real drag leaves)."""

    off_axis: Tuple[str, ...] = ()
    out_of_step: Tuple[Tuple[str, str], ...] = ()
    turned: bool = False
    residuals: Tuple[Tuple[str, str, float], ...] = ()

    @property
    def in_step(self) -> bool:
        return not (self.off_axis or self.out_of_step)


Frame9 = Tuple[Sequence[float], Sequence[float]]     # (rotation, 9 numbers by rows; origin in mm)


def _wrapped(angle: float) -> float:
    """``angle`` (radians) brought into (−π, π]."""
    out = math.remainder(angle, 2 * math.pi)
    return math.pi if out == -math.pi else out


def _off_whole(angle: float, step: float) -> float:
    """How far ``angle`` is from the nearest whole multiple of ``step`` (radians; ``step`` ≤ 0: of a full turn)."""
    if step <= 0:
        return abs(_wrapped(angle))
    off = angle % step
    return min(off, step - off)


@dataclass(frozen=True)
class CarrierLink:
    """A turning (or held) carrier as :func:`train_check` reads it (W7-PLAN §2.9, §5.3). ``carrier`` its component
    id, ``layout.carrier_id(shaft)`` (``"C carrier"``), the key of its frame in ``found``/``wanted``; ``planets``
    every gear id on its planet shafts (copy ids), in plan order; ``point`` its origin as placed, mm (on the
    layout's Front plane: z 0); ``axis`` its own +Z in the origin's frame, a unit W6 vector. ``point`` and ``axis``
    are the carrier's WANTED frame's origin and third column (an identity the caller keeps)."""

    carrier: str
    planets: Tuple[str, ...]
    point: Tuple[float, float, float]
    axis: Tuple[float, float, float]


def on_in(modes: Sequence[str], configuration: str) -> bool:
    """Whether a mate or link whose on-set is ``modes`` is on in ``configuration`` (W8-INTERFACES.md §3: the one
    home of "which mates are on in mode M"). ``()`` is on in every configuration (W5's mates, W7's, the splines,
    the slides, the axis mates). Names compare ignoring case, since mode names are unique ignoring case (J6) and a
    mode named as one of the template's configurations uses that configuration (§1.8 step 2)."""
    if not modes:
        return True
    wanted = str(configuration).casefold()
    return any(str(mode).casefold() == wanted for mode in modes)


def links_in(links: Sequence[object], configuration: str) -> Tuple[object, ...]:
    """The links (``MeshLink``, ``LockLink``, ``MateRef``, …) on in ``configuration``, in the order given: each by
    :func:`on_in` of its ``modes``; one with no ``modes`` field (a :class:`CarrierLink`) is on in every one. What
    :func:`train_check` is given in a configuration (W8-PLAN §1.7: it judges only the links on there)."""
    return tuple(link for link in links if on_in(getattr(link, "modes", ()), configuration))


def _about(axis: Sequence[float], angle: float) -> Tuple[Tuple[float, float, float], ...]:
    """The rotation by ``angle`` radians about the unit vector ``axis``, right-handed, as 3 rows (Rodrigues)."""
    length = math.sqrt(sum(float(v) * float(v) for v in axis))
    x, y, z = (float(v) / length for v in axis)
    c, s_, t = math.cos(angle), math.sin(angle), 1.0 - math.cos(angle)
    return ((t * x * x + c, t * x * y - s_ * z, t * x * z + s_ * y),
            (t * x * y + s_ * z, t * y * y + c, t * y * z - s_ * x),
            (t * x * z - s_ * y, t * y * z + s_ * x, t * z * z + c))


def _carried(frame: Frame9, link: CarrierLink, angle: float) -> Frame9:
    """``frame`` carried round the carrier's axis line (through ``link.point`` along ``link.axis``) by ``angle``."""
    rows = _about(link.axis, angle)
    rotation = [float(v) for v in frame[0]]
    turned = tuple(sum(rows[i][k] * rotation[k * 3 + j] for k in range(3)) for i in range(3) for j in range(3))
    off = [float(a) - float(p) for a, p in zip(frame[1], link.point)]
    at = tuple(float(link.point[i]) + sum(rows[i][k] * off[k] for k in range(3)) for i in range(3))
    return turned, at


def train_check(found: Mapping[str, Frame9], wanted: Mapping[str, Frame9], meshes: Sequence[MeshLink],
                locks: Sequence[LockLink], pitch: Mapping[str, float],
                tolerance: float = TRAIN_TOLERANCE, *, carriers: Sequence[CarrierLink] = (),
                held: Sequence[str] = ()) -> TrainCheck:
    """Whether the gears ``found`` stand as ``wanted`` does, up to a turn of each train and whole teeth (pure).

    ``found`` and ``wanted`` map a gear id to its frame (rotation 9 numbers
    by rows, origin in mm). Per gear of ``wanted``: missing from ``found``,
    an origin off by more than :data:`POSE_TOLERANCE` mm on any axis, or a
    rotation that is not ``wanted``'s turned about its own Z
    (:func:`turn_between`) is off its axis. Otherwise δ is its turn from
    wanted to found about its own +Z. Per mesh, ``δb − k·δa`` must be a whole
    number of b's pitch, to ``tolerance`` radians; per lock, ``δf − δa`` must
    be 0 (modulo a full turn), to ``tolerance`` — exactly, not modulo a pitch
    (review M1: a lock left a whole anchor tooth off is out of step). A
    relation with an off-axis gear is not judged. ``turned``: in step, and
    some gear's δ is not a whole number of its ``pitch`` (degrees; missing or
    0: any turn at all). Gears of ``found`` not in ``wanted`` are ignored.

    W7 (written at W7's interface commit; W7-PLAN §2.9, review M1; the identities in W7-INTERFACES.md §3):

    - ``carriers``: each carrier's frame is in ``found``/``wanted`` under its
      ``carrier`` id and is judged first like any gear, giving its own turn
      ``δ_c`` (its pitch is 0, so any carrier turn makes the train
      ``turned``). Every gear in its ``planets`` has its wanted frame
      CARRIED by ``δ_c`` about the carrier's axis line before it is judged
      (origin and axis against the carried frame), and its δ is its turn
      RELATIVE TO THE CARRIER. A carrier off its axis makes each of its
      planets off its axis too (where they belong cannot be told).
    - A mesh whose ``MeshLink.carrier`` is set takes each of its frame
      gears relative to that carrier, ``δ − s·δ_c``, ``s = ±1`` the sign of
      the gear's wanted axis (its frame's third column) against the
      carrier's ``axis``; a planet's δ is already relative.
    - ``held``: gears to be judged against their wanted frame exactly, but
      for whole pitches — a held gear whose δ is not a whole number of its
      ``pitch`` is off its axis (it must be re-placed); a held carrier is
      given in both ``carriers`` and ``held`` (its δ_c must then be 0).
    - A lock is judged on the δ's as kept (a carrier's own, a frame gear's
      own, a planet's relative), so ``LockLink("C carrier", "CarrierGear")``
      holds exactly when the carrier gear turned as far as the carrier.

    With no ``carriers`` and no ``held`` it is W5's function, result for result. A ``MeshLink.carrier`` that names
    no given carrier, or a gear among two carriers' planets, is a ValueError with a sentence.
    """
    links = {link.carrier: link for link in carriers}
    planet_of: Dict[str, CarrierLink] = {}
    for link in carriers:
        for gear in link.planets:
            if gear in planet_of and planet_of[gear].carrier != link.carrier:
                raise ValueError(f"{gear} is among the planets of both {planet_of[gear].carrier} and {link.carrier}, "
                                 "so which carrier it turns on cannot be told.")
            planet_of[gear] = link
    for mesh in meshes:
        if mesh.carrier and mesh.carrier not in links:
            raise ValueError(f"The mesh {mesh.a}–{mesh.b} is measured against {mesh.carrier}, which the check was "
                             "not given, so it cannot be judged.")
    held_set = set(held)

    def judge(frame_w: Frame9, gear: str) -> Optional[float]:
        frame_f = found.get(gear)
        if frame_f is None:
            return None
        if any(abs(float(a) - float(b)) > POSE_TOLERANCE for a, b in zip(frame_w[1], frame_f[1])):
            return None
        return turn_between(frame_w[0], frame_f[0])

    carrier_turn: Dict[str, Optional[float]] = {}
    for name, link in links.items():
        turn = judge(wanted[name], name) if name in wanted else None
        if turn is not None and name in held_set and _off_whole(turn, 0.0) > tolerance:
            turn = None
        carrier_turn[name] = turn

    off_axis: List[str] = []
    delta: Dict[str, float] = {}
    for gear, frame_w in wanted.items():
        if gear in links:
            turn = carrier_turn[gear]
        elif gear in planet_of:
            angle = carrier_turn.get(planet_of[gear].carrier)
            turn = None if angle is None else judge(_carried(frame_w, planet_of[gear], angle), gear)
        else:
            turn = judge(frame_w, gear)
        if turn is not None and gear in held_set and gear not in links and \
                _off_whole(turn, math.radians(pitch.get(gear, 0.0) or 0.0)) > tolerance:
            turn = None
        if turn is None:
            off_axis.append(gear)
            continue
        delta[gear] = turn

    def relative(gear: str, carrier: str) -> Optional[float]:
        if gear not in delta:
            return None
        if not carrier or gear in planet_of or gear == carrier:
            return 0.0 if gear == carrier else delta[gear]
        if carrier not in delta:
            return None
        link = links[carrier]
        axis = [float(wanted[gear][0][i * 3 + 2]) for i in range(3)]
        sign = 1.0 if sum(a * float(b) for a, b in zip(axis, link.axis)) > 0 else -1.0
        return delta[gear] - sign * delta[carrier]

    out: List[Tuple[str, str]] = []
    residuals: List[Tuple[str, str, float]] = []
    for mesh in meshes:
        da, db = relative(mesh.a, mesh.carrier), relative(mesh.b, mesh.carrier)
        if da is not None and db is not None:
            residual = _off_whole(db - mesh.k * da, math.radians(mesh.pitch))
            residuals.append((mesh.a, mesh.b, residual))
            if residual > tolerance:
                out.append((mesh.a, mesh.b))
    for lock in locks:
        if lock.anchor in delta and lock.follower in delta:
            residual = abs(_wrapped(delta[lock.follower] - delta[lock.anchor]))
            residuals.append((lock.anchor, lock.follower, residual))
            if residual > tolerance:
                out.append((lock.anchor, lock.follower))
    in_step = not (off_axis or out)
    turned = in_step and any(_off_whole(turn, math.radians(pitch.get(gear, 0.0) or 0.0)) > tolerance
                             for gear, turn in delta.items())
    return TrainCheck(tuple(off_axis), tuple(out), turned, tuple(residuals))


MODE_NAME = re.compile(r"^[A-Za-z0-9_-]+$")    # a mode's name, a configuration's (``schema.NAME_PATTERN``, J6)
SLIDE_TOLERANCE = 1e-9                          # mm: a SLIDE's value at or below it is on the Front plane (J27)
FrameValue = Tuple[Tuple[float, ...], Tuple[float, float, float]]


@dataclass(frozen=True)
class ModeStep:
    """One mode's configuration, as the build sets it up (W8-PLAN §1.8, W8-INTERFACES.md §3).

    ``name``: the configuration's name, the mode's (letters, digits, ``_`` and ``-``). ``ops``: the gear ``Mate``
    ops (couplings, sliding meshes) first made in this configuration — each made while it is shown, named
    (``Mate.name``, ``workbook.motion.mate_name``), in the order made. ``on``: every mate name on in this
    configuration — the base plan's mates (always on) and the per-mode mates on here; ``off``: every per-mode mate
    off here. ``values``: every SLIDE's name -> its |z_front| in mm here (a magnitude, > 0: the mate's Flip carries
    the side, J27). ``frames``: assembly handle -> ``(rotation 9 by rows, origin mm)`` wanted here, for the
    per-mode check (every gear at the built turn, each slider at its value)."""

    name: str
    ops: Tuple[base.Op, ...] = ()
    on: Tuple[str, ...] = ()
    off: Tuple[str, ...] = ()
    values: Mapping[str, float] = field(default_factory=dict)
    frames: Mapping[str, FrameValue] = field(default_factory=dict)


@dataclass(frozen=True)
class ModesPlan:
    """The configurations a turning assembly gets, beside its ``BuildPlan`` (W8-PLAN §1.8): one :class:`ModeStep`
    per mode in Modes-sheet order, ``steps[0]`` the one the assembly is saved and opens in. ``same_way``: the
    steps' gear mates (by name) that turn their two gears the same way about their own axes (``k > 0``: every
    coupling; a sliding mesh only inside a ring); a step gear mate not listed turns them opposite ways. It is the
    steps' half of W6's ``senses`` — the base plan's gear mates (meshes and splines) are in ``build``'s
    ``senses`` and never here, and each name has its sense in exactly one of the two (W8-INTERFACES.md §6)."""

    steps: Tuple[ModeStep, ...]
    same_way: Tuple[str, ...] = ()

    def check(self, plan: Optional[BuildPlan] = None) -> List[str]:
        """Every way this plan is unsound, as sentences (``[]`` when sound); pure. ``plan`` (the assembly's
        ``BuildPlan``), when given, is checked against too. The rules (W8-PLAN §3.2, W8-INTERFACES.md §3):

        * at least one step; every name a mode name (:data:`MODE_NAME`) and the names unique ignoring case;
        * every step op a named gear ``Mate`` (no ``LinkDimension``: a slide has no global), op ids unique across
          the steps and the plan, op names unique across the steps and not a plan mate's name;
        * in every step ``on`` and ``off`` share no name, and ``on`` ∪ ``off`` is the same set in every step;
        * every per-mode mate (a name in some ``off``, or a step op) is made exactly once, in the first step it is
          on in, and is on in some step; ``same_way`` names only step ops;
        * every step's ``values`` names the same SLIDEs, each value finite and above :data:`SLIDE_TOLERANCE`
          (J27: never on the Front plane; the one side is the Flip's, so a magnitude is all a step holds);
        * every frame nine and three finite numbers;
        * with ``plan``: ``on`` ∪ ``off`` is exactly the plan's mate names and the step ops' names, each SLIDE is
          a ``point distance`` mate of the plan, and each frame's handle a component the plan adds;
        * with ``plan`` (W8-INTERFACES §9.7): each step op's ``a`` and ``b`` a component the plan adds, and a
          coupling — a step gear mate whose two gears' planned axis lines (each component's last ``Place``) are
          one line — whose axes point the same way listed in ``same_way`` (it turns both the same way about their
          own axes: COUPLE ``sense = −σ_S·σ_D``, §9.3).
        """
        problems: List[str] = []
        if not self.steps:
            return ["The modes plan has no modes."]
        seen: Dict[str, str] = {}
        for step in self.steps:
            if not MODE_NAME.match(step.name or ""):
                problems.append(f"The mode name {step.name!r} is not letters, digits, _ and - only.")
            elif step.name.casefold() in seen:
                problems.append(f"The modes {seen[step.name.casefold()]} and {step.name} have one name, ignoring "
                                "case, and a configuration name can be used once.")
            else:
                seen[step.name.casefold()] = step.name
        plan_mates = [op for op in (plan.ops if plan is not None else ()) if isinstance(op, base.Mate)]
        plan_ids = {getattr(op, "id", "") for op in (plan.ops if plan is not None else ()) if getattr(op, "id", "")}
        plan_names = {op.name or op.id for op in plan_mates}
        made_in: Dict[str, int] = {}
        op_ids: set = set()
        for index, step in enumerate(self.steps):
            for op in step.ops:
                if not isinstance(op, base.Mate) or op.kind != "gear":
                    problems.append(f"In mode {step.name}, {getattr(op, 'id', op)!r} is not a gear mate, and a "
                                    "mode makes only couplings and sliding meshes.")
                    continue
                if not op.name:
                    problems.append(f"In mode {step.name}, the gear mate {op.id} has no name to be found by.")
                    continue
                if op.id in op_ids or op.id in plan_ids:
                    problems.append(f"In mode {step.name}, the id {op.id} is used twice.")
                op_ids.add(op.id)
                if op.name in made_in or op.name in plan_names:
                    problems.append(f"In mode {step.name}, the mate {op.name} is made a second time.")
                    continue
                made_in[op.name] = index
        per_mode = set(made_in)
        everything = None
        for index, step in enumerate(self.steps):
            on, off = set(step.on), set(step.off)
            both = sorted(on & off)
            if both:
                problems.append(f"In mode {step.name}, {', '.join(both)} {'is' if len(both) == 1 else 'are'} both "
                                "on and off.")
            per_mode |= off
            if everything is None:
                everything = on | off
            elif on | off != everything:
                differ = sorted((on | off) ^ everything)
                problems.append(f"Mode {step.name} does not say on or off for the same mates as mode "
                                f"{self.steps[0].name}: {', '.join(differ)}.")
        for name in sorted(per_mode):
            on_steps = [i for i, step in enumerate(self.steps) if name in step.on]
            if name not in made_in:
                problems.append(f"The mate {name} is switched per mode but no mode makes it.")
            elif not on_steps:
                problems.append(f"The mate {name} is on in no mode.")
            elif made_in[name] != on_steps[0]:
                problems.append(f"The mate {name} is made in mode {self.steps[made_in[name]].name}, not in "
                                f"{self.steps[on_steps[0]].name}, the first mode it is on in.")
        for name in self.same_way:
            if name not in made_in:
                problems.append(f"{name} is said to turn its gears the same way, and no mode makes it.")
        slides = set(self.steps[0].values)
        for step in self.steps:
            if set(step.values) != slides:
                differ = sorted(set(step.values) ^ slides)
                problems.append(f"Mode {step.name} does not give a value for the same slides as mode "
                                f"{self.steps[0].name}: {', '.join(differ)}.")
            for name, value in step.values.items():
                ok = isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
                if not ok or value <= SLIDE_TOLERANCE:
                    problems.append(f"In mode {step.name}, the slide {name} is given {value!r} mm, where it holds a "
                                    "distance from the Front plane above 0.")
            for handle, frame in step.frames.items():
                if not _frame_sound(frame):
                    problems.append(f"In mode {step.name}, the frame of {handle} is not nine and three numbers.")
        if plan is not None:
            wanted = plan_names | set(made_in)
            if everything is not None and everything != wanted:
                differ = sorted(everything ^ wanted)
                problems.append(f"The modes do not say on or off for exactly the assembly's mates: "
                                f"{', '.join(differ)}.")
            distances = {op.name or op.id for op in plan_mates if op.kind == "point distance"}
            for name in sorted(slides - distances):
                problems.append(f"The slide {name} is not a distance mate of the assembly.")
            components = {op.id for op in plan.ops if isinstance(op, base.AddComponent)}
            for step in self.steps:
                for handle in step.frames:
                    if handle not in components:
                        problems.append(f"In mode {step.name}, {handle} is not a component of the assembly.")
            axes, origins = _planned_axes(plan), _planned_origins(plan)
            for step in self.steps:
                for op in step.ops:
                    if not isinstance(op, base.Mate) or op.kind != "gear" or not op.name:
                        continue
                    ends = [op.a.partition(":")[0], op.b.partition(":")[0]]
                    strangers = [h for h in ends if h not in components]
                    for handle in strangers:
                        problems.append(f"In mode {step.name}, the gear mate {op.name} joins {handle}, which is not a "
                                        "component of the assembly.")
                    if strangers or any(h not in axes or h not in origins for h in ends):
                        continue
                    ga, gb = axes[ends[0]], axes[ends[1]]
                    if _one_line(origins[ends[0]], ga, origins[ends[1]], gb) and \
                            sum(p * q for p, q in zip(ga, gb)) > 0 and op.name not in self.same_way:
                        problems.append(f"In mode {step.name}, the coupling {op.name} turns its two gears the same "
                                        "way, and it is not listed as doing so.")
        return problems


def _one_line(point_a: Sequence[float], axis_a: Sequence[float], point_b: Sequence[float],
              axis_b: Sequence[float]) -> bool:
    """Whether two planned axis lines are one line (a coupling's or a spline's, never a mesh's): parallel
    (:func:`swcom.axes_parallel`) and b's point on a's line to :data:`LINE_TOLERANCE` mm."""
    if not axes_parallel(axis_a, axis_b):
        return False
    off = [float(q) - float(p) for p, q in zip(point_a, point_b)]
    length = math.sqrt(sum(float(v) * float(v) for v in axis_a)) or 1.0
    u = [float(v) / length for v in axis_a]
    along = sum(o * w for o, w in zip(off, u))
    return math.sqrt(max(0.0, sum(o * o for o in off) - along * along)) <= LINE_TOLERANCE


def _frame_sound(frame: object) -> bool:
    """Whether ``frame`` is ``(rotation, at)`` of nine and three finite numbers."""
    try:
        rotation, at = frame                                        # type: ignore[misc]
        numbers = [float(v) for v in rotation] + [float(v) for v in at]
    except (TypeError, ValueError):
        return False
    return len(rotation) == 9 and len(at) == 3 and all(math.isfinite(v) for v in numbers)


@dataclass
class ModeCheck:
    """One configuration as the per-mode check read it (W8-PLAN §1.8 step 6, §1.10's post-check), through handles
    fetched after it was shown. ``mates``: every mate as read there. ``suppressed``: every per-mode mate's flag
    there, as read back. ``values``: every SLIDE's value there, as read back (mm). ``clashes`` and
    ``interference_error``: this configuration's interference, as :class:`GearboxResult` holds the first's.

    W8-INTERFACES §9.14, for a mode an Update SHOWED (``GearboxUpdate.modes`` holds a check only for those):
    ``off_axis``, ``out_of_step`` and ``turned`` are what ``train_check`` found there, with that mode's links, when it
    was shown and before anything was put — empty and False for a mode shown and found right. A build's checks
    leave them empty."""

    name: str
    mates: List[MateState] = field(default_factory=list)
    suppressed: Dict[str, bool] = field(default_factory=dict)
    values: Dict[str, float] = field(default_factory=dict)
    clashes: list = field(default_factory=list)
    interference_error: str = ""
    out_of_step: List[Tuple[str, str]] = field(default_factory=list)
    off_axis: List[str] = field(default_factory=list)
    turned: bool = False


# W8: the configurations of a turning assembly (W8-PLAN §1.8)

# Findings the build of a gearbox with modes reads that do not depend on the version (W8-PLAN §4.2), each with getattr
# before anything is made: ``_SET`` for any value but None, else the value it must hold.
# VALUE_READ_ORDER: swcom.dimension_values pairs GetSystemValue3(3, names)' answers with the names in the order passed,
# which tier 11 found SolidWorks 2026 answers in (measured on 2026 only; 2024's confirming run should read it).
# CONFIGURATION_SHOW_OVER_DEFINED: CONFIGURATION_SHOW_RAISES_DIALOG was measured on configurations that solve (the
# spike); the build's step 6 shows every mode, and would show one whose mates fight if step 5 let it through. Tier 11
# showed such a configuration on SolidWorks 2026 with no window asking; it applies on 2024 unmeasured until the
# confirming run, as SUPPRESSED_GEAR_MATE_SENSE_READ does.
# SUPPRESSION_READ_ORDER is no gate: IsSuppressed2(3, names) answers in the document's configuration order, and the app
# asks one configuration per call (swcom.Session.mate_suppression), so it depends on no order.
MODES_FINDINGS = (("FEATURE_SUPPRESS", _SET), ("FEATURE_UNSUPPRESS", _SET), ("MATE_FIND_ROUTE", "mate group"),
                  ("CONFIGURATION_SHOW_RAISES_DIALOG", False), ("MULTI_CONFIGURATION_SAVE_ASKS", False),
                  ("COLLINEAR_GEAR_MATE_SENSE_READ_BACK", True), ("VALUE_READ_ORDER", "the order passed"),
                  ("CONFIGURATION_SHOW_OVER_DEFINED",
                   "shown; no window asks; its mates read in error; others solve after"))
SLIDE_READ_TOLERANCE = 1e-6        # mm: a slide's value read back per configuration


def _modes_version_refusal(revision: Sequence[int]) -> Optional[str]:
    """W8-INTERFACES §9.5: the per-version refusal, read from the running SolidWorks' revision — a gearbox with modes
    is built only on a version shown to hold a slide's value per configuration
    (``findings.SLIDE_VALUE_PER_CONFIGURATION_ON_<year>`` True, by getattr; the W8 spike's follow-up A on 2026 and
    on 2024). ``None`` when it may be built, else the sentence."""
    try:
        major = int(revision[0])
    except (TypeError, ValueError, IndexError):
        return ("The running SolidWorks' version could not be read, so whether it holds a slide's value per "
                "configuration cannot be told; a gearbox with modes is not built and nothing is made.")
    year = release_year(major)
    if getattr(findings, f"SLIDE_VALUE_PER_CONFIGURATION_ON_{year}", None) is not True:
        return (f"SolidWorks {year} has not been shown to hold a slide's value per configuration, so a gearbox with "
                "modes is not built there and nothing is made.")
    return None


def _configuration_names(modes: ModesPlan, template: Sequence[str]) -> Dict[str, str]:
    """Each mode's configuration name: the template's own configuration of the same name ignoring case (§1.8 step
    2, :func:`on_in`'s rule), else the mode's name."""
    out: Dict[str, str] = {}
    for step in modes.steps:
        out[step.name] = next((str(t) for t in template if on_in((step.name,), str(t))), step.name)
    return out


def _mate_handles_by_name(plan: BuildPlan, modes: ModesPlan) -> Dict[str, str]:
    """Every mate's name (as planned) -> the handle it is made under (its op id), the plan's and the steps'."""
    ops = [op for op in plan.ops if isinstance(op, base.Mate)] + [op for s in modes.steps for op in s.ops]
    return {op.name or op.id: op.id for op in ops}


def _fixed_handles(plan: BuildPlan) -> List[str]:
    """Each component whose last ``Fix``/``Unfix`` op is ``Fix``: the layout part and the gears held still."""
    last: Dict[str, bool] = {}
    for op in plan.ops:
        if isinstance(op, (base.Fix, base.Unfix)):
            last[op.component] = isinstance(op, base.Fix)
    return [handle for handle, fixed in last.items() if fixed]


_ARTICLES = ("The ", "A ", "An ")


def _in_mode(mode: str, sentence: str) -> str:
    """*"In mode 4L, …"*: a sentence put after its mode. Only a leading article is lowercased; a sentence that starts
    with a name (a gear id, a part, SolidWorks, a mode) keeps it as written, since a name is the workbook's spelling."""
    if sentence.startswith(_ARTICLES):
        sentence = sentence[0].lower() + sentence[1:]
    return f"In mode {mode}, {sentence}"


def _mode_problem(result: BuildResult, mode: str, sentence: str) -> None:
    """A problem of the per-mode check: *"In mode 4L, …"*, a mate problem and a failure (W5's rule: nothing saved)."""
    text = _in_mode(mode, sentence)
    result.mate_problems.append(text)
    result.failures.append((f"the mate check in mode {mode}", text))


def _set_up_modes(sw: SolidWorks, plan: BuildPlan, modes: ModesPlan, result: BuildResult, made: Dict[str, str],
                  gears: Mapping[str, str], kind: str, sense: Optional[tuple],
                  checks: Optional[List[ModeCheck]], say: Callable[[Step], None]) -> None:
    """W8-PLAN §1.8 steps 1-7, after W5's run, rebuild, verify and mate check and before the save, in that order
    exactly: the template's configurations read; a configuration per mode added (or the template's of that name
    used); one rebuild before any flag; every slide's value set in every configuration and read back; per mode, it
    shown and rebuilt, its couplings and sliding meshes made (each read for sense and made again with the other Flip
    if wrong), and every flag of each set in every configuration and read back; the per-mode check through fresh
    handles; the first mode shown, the template's configurations that are no mode deleted, and a rebuild. Handles are
    names throughout (the Session fetches again after every add and show). A problem is a sentence beginning *"In
    mode 4L, …"* in ``mate_problems`` and a failure, so nothing is saved; any raise is an ordinary failure (the
    caller's)."""
    template = [str(t) for t in sw.configurations()]
    names = _configuration_names(modes, template)
    configs = [names[s.name] for s in modes.steps]
    extra = [t for t in template if t not in configs]
    for step in modes.steps:
        if names[step.name] in template:
            result.done.append(f"configuration {names[step.name]} kept for the mode {step.name}")
            continue
        sw.add_configuration(names[step.name])
        result.done.append(f"configuration {names[step.name]} made")
    # Step 3: straight after AddConfiguration2 the spike's first two flag calls misbehaved; after a rebuild none did.
    if not sw.rebuild(kind=kind):
        result.failures.append(("the configurations", "The rebuild after the configurations were made reported an "
                                                      "error."))
        return
    handles = _mate_handles_by_name(plan, modes)
    # Step 4: every slide's value in every configuration, the first's included (J7's caution), then read back.
    slides = list(modes.steps[0].values)
    for slide in slides:
        for step in modes.steps:
            sw.set_dimension_in(handles[slide], float(step.values[slide]), [names[step.name]])
        read = sw.dimension_values(handles[slide], configs)
        for step in modes.steps:
            got, wanted = float(read.get(names[step.name], 0.0)), float(step.values[slide])
            if abs(got - wanted) > SLIDE_READ_TOLERANCE:
                _mode_problem(result, step.name, f"The slide {slide} reads {got:g} mm where the mode puts it "
                                                 f"{wanted:g} mm from the Front plane.")
    if result.failures:
        return
    result.done.append(f"{len(slides)} slide value(s) set and read back in {len(configs)} configurations")
    # Step 5: per mode, its own mates made while it is shown, then every flag of each set and read back.
    step_sense = None
    if sense is not None:
        given, axes, gear_ids, origins = sense
        step_sense = (dict(given, **{op.name: op.name in modes.same_way for s in modes.steps for op in s.ops}),
                      axes, gear_ids, origins)
    count = len(modes.steps)
    for index, step in enumerate(modes.steps, 1):
        say(Step(STAGE_MODE, step.name, index, count))
        sw.show_configuration(names[step.name])
        if not sw.rebuild(kind=kind):
            result.failures.append((f"the mode {step.name}", f"The rebuild in the configuration {names[step.name]} "
                                                             "reported an error."))
            return
        if not step.ops:
            continue
        sw.set_rebuild_suppressed(True)
        try:
            for op in step.ops:
                try:
                    result.done.append(_mate(sw, op, result, result.trig))
                    made[op.id] = result.features[-1]
                    if step_sense is not None:
                        _settle_sense(sw, op, result.features[-1], step_sense, result)
                except SolidWorksError as exc:
                    label = f"{base.describe(op, result.trig)} in mode {step.name}"
                    result.failures.append((label, str(exc)))
                    result.stopped_at = label
                    if isinstance(exc, _SenseRefused):
                        result.mate_problems.append(_in_mode(step.name, str(exc)))
                    elif isinstance(exc, MateRefused):
                        result.mate_problems.append(f"In mode {step.name}, SolidWorks would not make the mate "
                                                    f"{op.name or op.id}.")
                    return
        finally:
            sw.set_rebuild_suppressed(False)
        for op in step.ops:
            sentence = _status_sentence(made[op.id], sw.mate_status(made[op.id]))
            if sentence is not None:
                _mode_problem(result, step.name, sentence)
        if result.failures:
            return
        for op in step.ops:
            on = [names[s.name] for s in modes.steps if op.name in s.on]
            off = [names[s.name] for s in modes.steps if op.name not in s.on] + extra
            sw.set_mate_suppressed_in(op.id, True, off)
            sw.set_mate_suppressed_in(op.id, False, on)
            read = sw.mate_suppression(op.id, configs + extra)
            for s in modes.steps:
                wanted = op.name not in s.on                  # suppressed there
                got = bool(read.get(names[s.name], not wanted))
                if got != wanted:
                    _mode_problem(result, s.name, f"The mate {op.name} reads {'suppressed' if got else 'on'} "
                                                  f"where the mode has it {'off' if wanted else 'on'}.")
            for t in extra:
                if not read.get(t, False):
                    result.failures.append(("the configurations", f"The mate {op.name} reads on in {t}, which is "
                                                                  "no mode and is deleted before the save."))
        if result.failures:
            return
    # Step 6: the mate check per mode, through handles fetched again after each show.
    per_mode = sorted({op.name for s in modes.steps for op in s.ops} | {n for s in modes.steps for n in s.off})
    fixed = _fixed_handles(plan)
    mated = _mated_handles(plan)

    def gear_of(handle: str) -> str:
        return gears.get(handle) or result.components.get(handle) or handle

    for index, step in enumerate(modes.steps, 1):
        say(Step(STAGE_MODE, step.name, index, count))
        sw.show_configuration(names[step.name])
        if not sw.rebuild(kind=kind):
            result.failures.append((f"the mode {step.name}", f"The rebuild in the configuration {names[step.name]} "
                                                             "reported an error."))
            return
        check = ModeCheck(step.name)
        if checks is not None:
            checks.append(check)
        check.mates = list(sw.mate_states())
        for name in per_mode:
            check.suppressed[name] = sw.mate_suppression(handles[name], [names[step.name]])[names[step.name]]
        for slide in slides:
            check.values[slide] = sw.dimension_values(handles[slide], [names[step.name]])[names[step.name]]
        for sentence in _mode_problems(sw, step, check, mated, fixed, gear_of):
            _mode_problem(result, step.name, sentence)
    if result.failures:
        return
    result.done.append(f"every mode checked: {', '.join(configs)}")
    # Step 7: the first mode shown, the template's configurations that are no mode deleted, rebuilt for the save.
    sw.show_configuration(configs[0])
    for name in extra:
        sw.delete_configuration(name)
        result.done.append(f"configuration {name} deleted")
    if not sw.rebuild(kind=kind):
        result.failures.append(("the configurations", f"The rebuild in the configuration {configs[0]} before the save "
                                                      "reported an error."))


def _mode_problems(sw: SolidWorks, step: ModeStep, check: ModeCheck, mated: Sequence[str], fixed: Sequence[str],
                   gear_of: Callable[[str], str]) -> List[str]:
    """One mode's check (§1.8 step 6) as W5's ``_check_mates`` with this mode's lists: every mate on in it present,
    unsuppressed and without error; every per-mode mate off in it reading suppressed, and not judged by its error
    code (GOTCHAS §103); every mated gear free to turn; every frame the step gives at its place (each slider at its
    value); every component meant to stay fixed reading fixed through a handle fetched after the show (a held one
    reads False even for the layout: the spike). A sentence per problem, without the mode."""
    problems: List[str] = []
    by_name = {state.name: state for state in check.mates}
    told = set()
    for name in step.on:
        state = by_name.get(name)
        if state is None:
            problems.append(f"The mate {name} is missing from the assembly.")
            told.add(name)
        elif state.suppressed:
            problems.append(f"The mate {name} is suppressed in SolidWorks.")
            told.add(name)
    for name in step.off:
        if name in by_name and not check.suppressed.get(name, by_name[name].suppressed):
            problems.append(f"The mate {name} is on in SolidWorks, where the mode has it off.")
        told.add(name)
    flagged = [s for s in check.mates if s.code and not s.suppressed and s.name not in told]
    for state in [s for s in flagged if not s.warning] or flagged:
        problems.append(f"The mate {state.name} is in error in SolidWorks.")
    problems += _free_to_turn(sw, mated, gear_of)
    for handle, (rotation, at) in step.frames.items():
        found, where = sw.component_frame(handle)
        if any(abs(float(a) - float(b)) > POSE_TOLERANCE for a, b in zip(where, at)) or \
                any(abs(float(found[i]) - float(rotation[i])) > POSE_TOLERANCE for i in (2, 5, 8)):
            problems.append(f"{gear_of(handle)} stands at {_vector(where)} where the mode places it at "
                            f"{_vector(at)}.")
    for handle in fixed:
        if not sw.is_fixed(handle):
            problems.append(f"{gear_of(handle)} reads not fixed in SolidWorks, where it was fixed.")
    return problems


def _modes_interference(sw: SolidWorks, result: GearboxResult, checks: Sequence[ModeCheck], kind: str,
                        gear_of: Mapping[str, str], say: Callable[[Step], None], stem: str) -> None:
    """§1.8 step 8, after the save: per mode, it shown, the train's rebuild, ``interferences()`` (a raise is that
    mode's ``interference_error``, a CHECK); then the first mode shown again and rebuilt. The first mode's clashes are
    also :attr:`GearboxResult.clashes`. A show marks the assembly and no part (the spike), as W4's check already
    does."""
    names = _configuration_names(ModesPlan(tuple(ModeStep(c.name) for c in checks)), sw.configurations())
    for index, check in enumerate(checks, 1):
        say(Step(STAGE_MODE, check.name, index, len(checks)))
        sw.show_configuration(names[check.name])
        sw.rebuild(kind=kind)
        try:
            check.clashes = _clashes(sw.interferences(), gear_of)
        except Exception as exc:  # noqa: BLE001 - a clash check that cannot run is a CHECK, never a failure
            check.interference_error = _said(exc)
    if checks:
        result.clashes = list(checks[0].clashes)
        result.interference_error = checks[0].interference_error
        say(Step(STAGE_INTERFERENCE, stem))
        sw.show_configuration(names[checks[0].name])
        sw.rebuild(kind=kind)


@dataclass(frozen=True)
class MateRef:
    """A mate on record, as Update needs it: its name in SolidWorks' tree, its kind (``workbook.motion`` AXIS,
    ALONG, LOCK or MESH, the strings ``"axis"``, ``"along"``, ``"lock"``, ``"mesh"``), its gears by id (AXIS/ALONG
    ``(gear,)``; LOCK ``(anchor, follower)``; MESH ``(a, b)`` in the order the gear mate was made, its first
    selection first) and, for AXIS/ALONG, its shaft. ``store.MateEntry`` without the numbers."""

    name: str
    kind: str
    gears: Tuple[str, ...]
    shaft: str = ""
    # W8 (W8-INTERFACES.md §3): a SLIDE's values on record, ``(configuration, signed z_front mm)`` — the pairs of
    # ``store.MateEntry.values`` in the order it holds them (read them as a dict) — else (); a coupling's or sliding
    # mesh's on-set (``MateEntry.modes``), () = every configuration.
    values: Tuple[Tuple[str, float], ...] = ()
    modes: Tuple[str, ...] = ()


@dataclass(frozen=True)
class MotionUpdate:
    """What Update SolidWorks is given for a gearbox built to turn (``workbook.update.classify``, Agent B; the
    worker's motion path, Agent A). None in ``update_gearbox``'s ``motion`` is W4's static path, untouched.

    ``mates``: every mate on record. ``meshes``: a :class:`MeshLink` per
    recorded MESH mate with the tooth counts now wanted, in its recorded gear
    order. ``locks``: a :class:`LockLink` per recorded LOCK mate.
    ``recorded``: the frames on record (what was last put), one
    ``Placement`` per gear of the assembly, its ``pitch`` from the teeth AS
    BUILT (as ``recorded_meshes``); the frames now wanted, with the pitch
    now wanted, are ``update_gearbox``'s ``placements``.
    ``recorded_meshes``: as ``meshes``, with the tooth counts the gear mates
    hold now (the record's MESH ratios). ``face_globals``: ``(gear, its
    "<Gear> Face Z" global as now wanted)`` for every recorded ALONG mate
    with a face global, its expression the literal |z_front| in mm
    (``workbook.motion.face_global`` names it); the worker sets only those
    the assembly holds differently. ``ratios``: ``(gear mate name, numerator,
    denominator)`` for every MESH whose (za, zb) changed, in the mate's own
    gear order (review M10) — always empty while
    ``findings.GEAR_MATE_RATIO_ROUTE`` is not ``"remake"`` (W5-DECISIONS: a
    tooth change is then structural). ``fixed``: gears left fixed (on a
    fixed shaft, or held still by one: W5-PLAN D9, review M9), which Update
    re-places as W4 does, modulo pitch, with
    ``findings.REPLACE_FIXED_ROUTE``.
    """

    mates: Tuple[MateRef, ...] = ()
    meshes: Tuple[MeshLink, ...] = ()
    locks: Tuple[LockLink, ...] = ()
    recorded: Tuple["Placement", ...] = ()
    recorded_meshes: Tuple[MeshLink, ...] = ()
    face_globals: Tuple[Tuple[str, GlobalVariable], ...] = ()
    ratios: Tuple[Tuple[str, int, int], ...] = ()
    fixed: Tuple[str, ...] = ()
    # W7 (B fills them, A reads them; W7-PLAN §2.9-§2.10): every turning or held carrier of the gearbox, for
    # train_check and the puts (a held carrier is also in ``held``); and the held gears a recorded gear mate
    # touches — judged against their wanted frames, and re-placed FIRST, before the carrier and the train (M1).
    carriers: Tuple[CarrierLink, ...] = ()
    held: Tuple[str, ...] = ()
    # W8 (B fills them, A reads them; W8-PLAN §1.10, W8-INTERFACES.md §3). All empty for a gearbox with no modes,
    # which is W7's path unchanged. ``configurations``: the modes on record (``GearboxRecord.modes``), in order.
    # ``mode_placements``: per configuration, the frames now wanted there (``update_gearbox``'s ``placements`` are
    # the active one's too, as before). ``recorded_by_mode``: per configuration, the frames on record there
    # (``ComponentEntry.frames``; a configuration with none of its own repeats ``recorded``). ``slide_values``:
    # ``(SLIDE name, configuration, wanted |z_front| mm)``, one per SLIDE per configuration. ``on_sets``:
    # ``(per-mode mate, the configurations wanted on)`` for every coupling and sliding mesh, the J14 edits included;
    # an always-on mate is not listed.
    configurations: Tuple[str, ...] = ()
    mode_placements: Tuple[Tuple[str, Tuple["Placement", ...]], ...] = ()
    recorded_by_mode: Tuple[Tuple[str, Tuple["Placement", ...]], ...] = ()
    slide_values: Tuple[Tuple[str, str, float], ...] = ()
    on_sets: Tuple[Tuple[str, Tuple[str, ...]], ...] = ()


def same_named_elsewhere(documents: Sequence[DocInfo], paths: Sequence[str]) -> List[Tuple[str, str]]:
    """``(open document's path, wanted path)`` for every open document with the same file name as a path this
    job will build, open or insert, but in another folder (decision 7: SolidWorks keys open documents by file
    name, so it would answer with the wrong one). Unsaved documents are not compared. Pure."""
    def name(path: str) -> str:
        return os.path.basename(path.replace("\\", "/")).lower()

    out: List[Tuple[str, str]] = []
    for doc in documents:
        if not doc.path:
            continue
        for wanted in paths:
            if wanted and name(doc.path) == name(wanted) and not same_path(doc.path, wanted):
                out.append((doc.path, wanted))
    return out


def _quiet(_step: Step) -> None:
    """The progress callback when the caller gave none."""


def _stem(path: str) -> str:
    """A path's file stem (``Gear_m1.5_N68``), the only name a :class:`Step` carries."""
    return os.path.splitext(os.path.basename(str(path).replace("\\", "/")))[0]


def _file(path: str) -> str:
    return os.path.basename(str(path).replace("\\", "/"))


def _saved_path(plan: BuildPlan) -> str:
    save = next((op for op in plan.ops if isinstance(op, base.SaveAs)), None)
    return save.path if save is not None and save.path else plan.path


def _clash_line(clash: Clash) -> str:
    """``G1 and G2 interfere, 12.345 mm³; look where they meet``, or the volume alone when nothing was named.

    Not "their mesh": two gears on one shaft can clash too (on SolidWorks 2026, gearbox_smoke 2026-11-13, a
    gear widened by Update ran into its neighbour on the same shaft)."""
    names = list(clash.gears or clash.components)
    if not names:
        return (f"an interference of {clash.volume:.3f} mm³ between components SolidWorks did not name; "
                "look at each mesh")
    if len(names) == 1:
        return f"{names[0]} interferes, {clash.volume:.3f} mm³; look where it meets the others"
    listed = ", ".join(names[:-1]) + f" and {names[-1]}"
    return f"{listed} interfere, {clash.volume:.3f} mm³; look where they meet"


def _clashes(found: Sequence[Tuple[Sequence[str], float]], gear_of: Mapping[str, str]) -> List[Clash]:
    """``interferences()`` as :class:`Clash`es, each Name2 mapped to its gear id where the map knows it.

    SolidWorks gives one interference per region of contact: on 2026 (34.0.0,
    gearbox_smoke 2026-11-13) a 24-tooth gear turned half a pitch against a
    16-tooth one gave three, each between the same two components. Those are
    one clash to a reader, so interferences between the same components are
    merged, in the order first met, their volumes summed. Unnamed ones are
    kept apart: nothing says they are the same pair.
    """
    merged: Dict[object, Clash] = {}
    for index, (names, volume) in enumerate(found):
        names = tuple(names)
        key: object = frozenset(names) if names else index
        if key in merged:
            earlier = merged[key]
            merged[key] = Clash(earlier.components, earlier.gears, earlier.volume + float(volume))
        else:
            merged[key] = Clash(names, tuple(gear_of.get(n, n) for n in names), float(volume))
    return list(merged.values())


def _interference_lines(clashes: Sequence[Clash], error: str, ran: bool) -> List[str]:
    if error:
        return [f"CHECK   interference could not be checked: {error}"]
    if not ran:
        return []
    if not clashes:
        return ["ok      no interference between the gears"]
    return [f"CHECK   {_clash_line(c)}" for c in clashes]


def _held(current: Sequence[Tuple[str, float]]) -> Dict[str, str]:
    held: Dict[str, str] = {}
    for text, _ in current:
        try:
            name, expression = split_equation(text)
        except (ValueError, EquationError):
            continue
        held[name] = expression
    return held


def _read_live(sw: SolidWorks, doc: DocumentValues, verb: str,
               after_open: Optional[Callable[[str], None]] = None, *,
               lines: Optional[Mapping[str, Tuple[Vec3, Vec3]]] = None) -> Tuple[List[Tuple[str, float]],
                                                                            Dict[str, List[Tuple[str, str]]],
                                                                            Dict[str, float]]:
    """Open a saved document and read what it holds, writing nothing: its equations, the planned changes
    (``planned_changes``) in each trig unit, ``{DEGREES: […], RADIANS: […]}``, and the values SolidWorks
    evaluates its equations to (``equation_values``), for :func:`_held_unit`. ``after_open`` is told the path
    as soon as the document is open and still the build document (:func:`_note_opened`).

    ``open_document`` (which also refuses a same-named document from another
    folder), then ``planned_changes`` — which raises when a global is missing
    — and every name in ``doc.features`` looked for. Every refusal is a
    :class:`BuildError` naming the file, worded "<file> cannot be <verb>: …".

    Nothing here measures the trig units. ``detect_trig_units`` adds and
    deletes an equation, and on SolidWorks 2026 (34.0.0, gearbox_smoke
    2026-11-13) that alone left each document marked modified, where opening
    it, reading its equations and walking its features did not. So the
    units are read from the text: a document that holds the degree form or
    the radian form of every global holds what is asked, in those units —
    provided SolidWorks also evaluates them as that unit would (see
    :func:`_held_unit`).

    W6 (W6-PLAN §2.7, review S7): ``lines`` (a layout part's slanted shafts'
    line axes as the record has them, axis name -> (point, direction) in mm)
    are each read back (``axis_line``, which marks nothing) and must lie on
    the recorded line, either way along it, to 1e-6: an axis moved in
    SolidWorks is a :class:`NotAsBuilt`, since only a new revision rebuilds
    a fixed line.
    """
    name = _file(doc.path)
    sw.begin_build()
    try:
        try:
            sw.open_document(doc.path)
            if after_open is not None:
                after_open(doc.path)
            current = sw.equations()
        except BuildError as exc:
            raise BuildError(f"{name} cannot be {verb}: {exc}") from None
        except SolidWorksError as exc:
            raise BuildError(str(exc)) from None
        try:
            by_unit = {t: planned_changes(current, doc.variables, t) for t in (DEGREES, RADIANS)}
        except BuildError as exc:            # a global it should hold is not in it: not the document on record
            raise NotAsBuilt(f"{name} cannot be {verb}: {exc}", doc.path) from None
        if doc.features:
            try:
                present = set(sw.feature_names())
            except SolidWorksError as exc:
                raise BuildError(f"{name} cannot be {verb}: its features could not be read: {exc}") from None
            lost = [f for f in doc.features if f not in present]
            if lost:
                listed = ", ".join(f'"{f}"' for f in lost)
                raise NotAsBuilt(f"{name} cannot be {verb}: {listed} {'is' if len(lost) == 1 else 'are'} no "
                                 "longer in it; it was renamed or deleted in SolidWorks.", doc.path)
        for index, (axis, (point, direction)) in enumerate(sorted((lines or {}).items()), 1):
            try:
                read = sw.axis_line(f"line{index}", axis)
            except SolidWorksError as exc:
                raise BuildError(f"{name} cannot be {verb}: where its axis {axis} lies could not be read: "
                                 f"{exc}") from None
            if not _on_line(read, point, direction):
                shaft = axis[:-len(" Axis")] if axis.endswith(" Axis") else axis
                said = ("so Update SolidWorks cannot act on it; Build again… makes a new revision."
                        if verb == "updated" else f"so {name} cannot be {verb}.")
                raise NotAsBuilt(f"{shaft}'s axis in the layout part is not where the record has it (it was moved in "
                                 f"SolidWorks), {said}", doc.path)
        try:
            values = dict(sw.equation_values())
        except SolidWorksError as exc:
            raise BuildError(f"{name} cannot be {verb}: its equations' values could not be read: {exc}") from None
        return current, by_unit, values
    finally:
        sw.end_build()


def _on_line(read: Tuple[Sequence[float], Sequence[float]], point: Sequence[float],
             direction: Sequence[float]) -> bool:
    """Whether an axis read back (a point on it, its direction) lies on the line through ``point`` along
    ``direction``, either way along it, to ``swcom.LINE_TOLERANCE`` (mm, and per direction component)."""
    try:
        at, along = [float(v) for v in read[0]], [float(v) for v in read[1]]
        want = [float(v) for v in direction]
        size, wanted = math.sqrt(sum(v * v for v in along)), math.sqrt(sum(v * v for v in want))
        along, want = [v / size for v in along], [v / wanted for v in want]
    except (TypeError, ValueError, IndexError, ZeroDivisionError):
        return False
    if len(at) != 3 or len(along) != 3 or len(want) != 3:
        return False
    sign = 1.0 if sum(p * q for p, q in zip(along, want)) >= 0 else -1.0
    if max(abs(sign * along[i] - want[i]) for i in range(3)) > LINE_TOLERANCE:
        return False
    off = [at[i] - float(point[i]) for i in range(3)]
    reach = sum(off[i] * want[i] for i in range(3))
    return math.sqrt(max(0.0, sum(v * v for v in off) - reach * reach)) <= LINE_TOLERANCE


def _values_off(values: Mapping[str, float], variables: Sequence[GlobalVariable],
                trig: str) -> Optional[Tuple[str, float, float]]:
    """The first global whose value SolidWorks evaluates (``values``) differs from what ``variables`` give in
    ``trig``, as (name, SolidWorks' value, the expected value); None when every one agrees (to the build's own
    tolerance, :data:`VALUE_TOLERANCE`), or when the expected values cannot be worked out here — then the text
    alone decides, as before."""
    try:
        expected = evaluate_all([(v.name, v.expression_for(trig)) for v in variables], trig)
    except EquationError:
        return None
    for variable in variables:
        want, got = expected.get(variable.name), values.get(variable.name)
        if want is None or got is None:
            continue
        if abs(float(got) - want) > VALUE_TOLERANCE * max(1.0, abs(want)):
            return variable.name, float(got), want
    return None


def _held_unit(by_unit: Mapping[str, Sequence[Tuple[str, str]]], values: Optional[Mapping[str, float]] = None,
               variables: Sequence[GlobalVariable] = ()) -> str:
    """The trig unit in which a document already holds every global as asked (degrees first), or ``""``.

    The text decides which unit's form it holds; with ``values`` (what
    SolidWorks evaluates, ``equation_values``) that unit must also be the one
    SolidWorks evaluates in: the values ``variables`` give in it must be the
    values SolidWorks has (:func:`_values_off`). A document holding the
    degree form of ``"Pitch Diameter" * cos ( "Pressure Angle" )`` whose
    angle unit was later set to radians evaluates cos(20 rad): its text is
    right and its geometry is not, so it does not hold what is asked, and
    Update sets it (measuring the unit) rather than leave it (W4 review N5;
    before S2, Update measured the unit every time). A global with no trig
    has the same text and value in both units, so only trig globals can
    differ. The build's own read-back (:func:`_verify`) has compared
    ``equation_values`` with the maths on SolidWorks 2026 and 2024; this
    comparison on a reopened document has not yet run on real SolidWorks."""
    for trig in (DEGREES, RADIANS):
        if by_unit[trig]:
            continue
        if values is not None and _values_off(values, variables, trig) is not None:
            continue
        return trig
    return ""


def _check_live(sw: SolidWorks, doc: DocumentValues, verb: str,
                after_open: Optional[Callable[[str], None]] = None, *,
                lines: Optional[Mapping[str, Tuple[Vec3, Vec3]]] = None) -> str:
    """A document to be reused, opened and checked, writing nothing (:func:`_read_live`): it must hold every
    global exactly, in either trig unit, SolidWorks must evaluate them as that unit would (:func:`_held_unit`),
    and every feature named must be there; returns that unit. Otherwise a :class:`NotAsBuilt` saying what
    differs — the texts in the unit that differs less, or the first value when only the angle unit is wrong —
    (a :class:`BuildError` when it cannot be opened or read at all)."""
    current, by_unit, values = _read_live(sw, doc, verb, after_open, lines=lines)
    unit = _held_unit(by_unit, values, doc.variables)
    if unit:
        return unit
    written = next((t for t in (DEGREES, RADIANS) if not by_unit[t]), "")
    off = _values_off(values, doc.variables, written) if written else None
    if off is not None:
        name, got, want = off
        raise NotAsBuilt(f"{_file(doc.path)} does not hold what the workbook asks of it, so it cannot be {verb}: its "
                         f"equations are written for {written}, but SolidWorks evaluates them otherwise (\"{name}\" "
                         f"is {got:.6g} there and {want:.6g} here), so its angle unit was changed since they were "
                         "written.", doc.path)
    changes = min((by_unit[t] for t in (DEGREES, RADIANS)), key=len)
    held = _held(current)
    shown = "; ".join(f'"{n}" is {held.get(n, "?")} there and {e} here' for n, e in changes[:3])
    more = f"; and {len(changes) - 3} more" if len(changes) > 3 else ""
    raise NotAsBuilt(f"{_file(doc.path)} does not hold what the workbook asks of it, so it cannot be {verb}: "
                     f"{shown}{more}.", doc.path)


def _evaluates(sw: SolidWorks, doc: DocumentValues, verb: str) -> None:
    """The new values of a document Update will change, evaluated before anything changes. They are evaluated in
    both trig units, which needs nothing from SolidWorks; only when they evaluate in one unit and not the other is
    the document's own unit measured (``detect_trig_units``) — it is about to change anyway — to say which."""
    failed: Dict[str, EquationError] = {}
    for trig in (DEGREES, RADIANS):
        try:
            evaluate_all([(v.name, v.expression_for(trig)) for v in doc.variables], trig)
        except EquationError as exc:
            failed[trig] = exc
    if not failed:
        return
    if len(failed) == 1:
        sw.begin_build()
        try:
            sw.open_document(doc.path)
            trig = sw.detect_trig_units()
        except SolidWorksError as exc:
            raise BuildError(str(exc)) from None
        finally:
            sw.end_build()
        if trig not in failed:
            return
    else:
        trig = DEGREES
    raise BuildError(f"{_file(doc.path)} cannot be {verb}: the new values do not evaluate: {failed[trig]}")


def _refuse_paths(sw: SolidWorks, made: Sequence[str], opened: Sequence[str], verb_made: str,
                  verb_opened: str) -> List[str]:
    """The path checks of a job, each a :class:`BuildError` sentence naming the file: one path twice, two files
    of one name from two folders (SolidWorks keeps one document per file name: probe
    add_component_same_name_elsewhere), and a document of the same name already open from another folder
    (decision 7, :func:`same_named_elsewhere`). Returns the saved documents open in SolidWorks as the job
    begins (their paths), read once here for both."""
    everything = list(made) + list(opened)
    for index, path in enumerate(everything):
        for earlier in everything[:index]:
            if same_path(path, earlier):
                raise BuildError(f"{path} is named twice in this job, so one document would take the place of the "
                                 "other.")
            if _file(path).lower() == _file(earlier).lower():
                raise BuildError(f"{earlier} and {path} have the same file name, and SolidWorks keeps one document "
                                 "per file name, so they cannot both be in one job.")
    documents = sw.documents()
    clashes = same_named_elsewhere(documents, everything)
    if clashes:
        said = []
        for open_path, wanted in clashes:
            verb = verb_made if any(same_path(wanted, p) for p in made) else verb_opened
            said.append(f"{open_path} is open in SolidWorks, and it has the same file name as {wanted}, which this "
                        f"job would {verb}")
        files = [_file(p) for p, _ in clashes]
        listed = files[0] if len(files) == 1 else ", ".join(files[:-1]) + f" and {files[-1]}"
        raise BuildError(f"{'; '.join(said)}; SolidWorks keeps one document per file name, so close {listed} in "
                         "SolidWorks and try again.")
    return [d.path for d in documents if d.path]


def _from_disk(path: str, open_before: Optional[Sequence[str]]) -> bool:
    """Whether a document the job opens was not open in SolidWorks before it (``documents()`` at the pre-flight),
    so ``open_document`` loaded it from its file: what it holds in memory is then what the file holds. Never when
    what was open is not known (``open_before`` None)."""
    return open_before is not None and not any(same_path(path, p) for p in open_before)


def _note_opened(sw: SolidWorks, path: str, result: Union["GearboxResult", "GearboxUpdate"]) -> None:
    """Right after ``open_document(path)``: list ``path`` in ``result.opened`` — loaded from its file, so its
    unsaved marks may go — only when it was not open as the job began (:func:`_from_disk` on
    ``result.open_before``) and SolidWorks reads no unsaved changes in it (``has_unsaved_changes``,
    ``GetSaveFlag``). The second is the belt to the first's braces (third W4 review, item 1): a document holding
    changes not saved is never one whose mark may be cleared, whatever the list of open documents said — it was
    open before the job, so it joins ``result.open_before``, and the finishes never take it for one SolidWorks
    closed. A flag that cannot be read counts as changes."""
    if not _from_disk(path, result.open_before) or any(same_path(path, p) for p in result.opened):
        return
    try:
        unsaved = bool(sw.has_unsaved_changes())
    except SolidWorksError:
        unsaved = True
    if unsaved:
        result.open_before.append(path)
    else:
        result.opened.append(path)


@dataclass
class GearboxResult:
    """What :func:`build_gearbox` did, step by step; every part saved before a failure stays saved.

    ``checked``: documents already built (reused parts, then a reused
    layout), opened and found to hold what was expected, in order.
    ``layout`` is None when the layout was reused (``layout_reused`` is then
    its path) or not reached; ``assembly`` None when not reached or not
    planned (Build parts). ``components`` is the assembly's
    ``BuildResult.components`` (handle -> Name2, the layout's ``"layout"``
    included). ``clashes`` and ``interference_error`` are filled only after
    an assembly that built cleanly; a clash is a CHECK, not a failure.
    ``skipped`` says, as a phrase, what a failure left unattempted.
    ``parts.ok`` is False for an empty batch, so :attr:`ok` must not lean
    on it when every part was reused. ``failures`` are (what, why) for a
    raise that stopped the job between its documents (each document's own
    failures stay on its :class:`BuildResult`): after the pre-flight nothing
    escapes :func:`build_gearbox`, so what saved before it still reaches the
    finish (W4 review B1).

    ``mismatched`` are (path, why) for each document to reuse that the live
    check found not holding what it should (:class:`NotAsBuilt`); then
    nothing is made at all, and ``mtimes`` holds each such file's time as
    read at the check, so the finish can record it and the next plan make
    that part new instead of failing the same check on every press (W4
    review B2's last corner: an Update left unsaved, SolidWorks closed
    without saving, and the unchanged file saved later, so its time moved on
    while it still held the old values).

    ``held``: each document in ``checked`` and the trig unit the check found
    it holding its globals in, for the ``.gear.json`` the finish writes beside
    a part only the journal knew. ``open_before``: the saved documents open
    in SolidWorks when the job began (None when not read, as in a test's
    hand-made result), and ``opened`` the documents the job opened from disk
    — not open before it — whose state in memory is therefore their file's
    (second W4 review N2: the finish clears or re-decides their marks, and a
    document marked unsaved that was not open when the job began has lost
    its unsaved changes). That a document in memory is listed by
    ``documents()`` (``GetFirstDocument``/``GetNext``, walked to the end of
    the list) whether or not its window is open is what decision 7's
    same-name check already relies on; it has not yet been exercised for
    this on real SolidWorks. So a document is listed in ``opened`` only when
    ``GetSaveFlag`` also reads it holding no unsaved changes once opened
    (:func:`_note_opened`, third W4 review): one holding Update's changes is
    never counted as loaded from its file, and joins ``open_before``, since
    it was evidently open before the job.
    """

    parts: ManyResult = field(default_factory=ManyResult)
    checked: List[str] = field(default_factory=list)
    layout: Optional[BuildResult] = None
    layout_reused: str = ""
    assembly: Optional[BuildResult] = None
    components: Dict[str, str] = field(default_factory=dict)
    clashes: List[Clash] = field(default_factory=list)
    interference_error: str = ""
    skipped: str = ""
    failures: List[Tuple[str, str]] = field(default_factory=list)
    mismatched: List[Tuple[str, str]] = field(default_factory=list)
    mtimes: Dict[str, float] = field(default_factory=dict)
    held: Dict[str, str] = field(default_factory=dict)
    open_before: Optional[List[str]] = None
    opened: List[str] = field(default_factory=list)
    # W5: which assembly saved — GEARBOX_MOTION (its plan mates its gears: a train) or GEARBOX_STATIC (W4's fixed
    # one) — or "" when none did. A train SolidWorks refused or flagged a mate of is not saved, and nothing is
    # saved in its place (W5-DECISIONS, answer 1): ``assembly`` is then that failed BuildResult, its
    # ``mate_problems`` the sentences and its ``document`` the title it is left open under, and ``kind`` is "".
    kind: str = ""
    # W7 (A fills them; W7-PLAN §2.9): each carrier part built, in the order given (a failure skips the assembly),
    # and the paths of the carrier parts reused (checked live, as the layout is).
    carriers: List[BuildResult] = field(default_factory=list)
    carriers_reused: List[str] = field(default_factory=list)
    # W8 (A fills them; W8-PLAN §1.8, W8-INTERFACES.md §3): the per-mode check of each configuration, in mode order
    # (empty with no ``modes``); and ``swcom.positions_per_configuration`` of the running version, read once by the
    # worker for the sentences (None: neither claim made).
    modes: List[ModeCheck] = field(default_factory=list)
    positions_per_configuration: Optional[bool] = None

    @property
    def ok(self) -> bool:
        """Every part planned was saved, the layout saved or reused (when planned), the assembly saved (when
        planned), and nothing stopped the job between them. Clashes do not count against it."""
        def saved(result: Optional[BuildResult]) -> bool:
            return result is None or (result.ok and bool(result.saved))

        return (all(saved(r) for r in self.parts.built) and not self.parts.skipped and saved(self.layout)
                and all(saved(r) for r in self.carriers)
                and saved(self.assembly) and not self.skipped and not self.failures and not self.mismatched)

    def _interference_ran(self) -> bool:
        return (self.assembly is not None and self.assembly.ok and bool(self.assembly.saved)
                and bool(getattr(findings, "INTERFERENCE_CHECKED", False)))

    def _mode_lines(self) -> List[str]:
        """W8: per mode, ``config  4L: 11 mates as planned`` and ``mode    4L: every mate sound, every gear free to
        turn, no interference`` (or its clashes as CHECKs naming the mode), for a build whose modes all checked
        clean; a mode with a problem has its sentence among the assembly's failures."""
        lines: List[str] = []
        clean = self.assembly is not None and not self.assembly.mate_problems
        ran = self._interference_ran()
        for check in self.modes:
            if not clean:
                break
            on = [m for m in check.mates if not m.suppressed]
            lines.append(f"config  {check.name}: {len(on)} mates as planned"
                         + (f", {len(check.mates) - len(on)} off" if len(on) != len(check.mates) else ""))
            said = f"mode    {check.name}: every mate sound, every gear free to turn"
            if ran and not check.clashes and not check.interference_error:
                said += ", no interference"
            lines.append(said)
            if ran and check.interference_error:
                lines.append(f"CHECK   in mode {check.name}, interference could not be checked: "
                             f"{check.interference_error}")
            lines.extend(f"CHECK   in mode {check.name}, {_clash_line(clash)}" for clash in (check.clashes if ran else ()))
        return lines

    def log_lines(self) -> List[str]:
        """The parts' lines, the checked documents, the layout's, the assembly's, then ``ok      no interference
        between the gears`` or one ``CHECK`` per clash naming the gears, then ``SKIPPED …``."""
        lines = self.parts.log_lines()
        lines.extend(f"ok      checked {_file(p)}: it holds what the workbook asks, so it is reused"
                     for p in self.checked)
        lines.extend(f"FAIL    checked {_file(p)}: {why}" for p, why in self.mismatched)
        if self.layout is not None:
            lines.extend(self.layout.log_lines())
        elif self.layout_reused:
            lines.append(f"ok      layout {_file(self.layout_reused)} reused")
        for carrier in self.carriers:
            lines.extend(carrier.log_lines())
        lines.extend(f"ok      carrier part {_file(p)} reused" for p in self.carriers_reused)
        if self.assembly is not None:
            lines.extend(self.assembly.log_lines())
            if self.assembly.mate_problems and not self.assembly.saved and self.assembly.document:
                held = ("the parts, the layout part and the carrier part" if self.carriers or self.carriers_reused
                        else "the parts and the layout part")
                lines.append(f"STOPPED SolidWorks refused or flagged a mate, so {self.assembly.document} is left open "
                             f"in SolidWorks, unsaved, and no assembly is built in its place; {held} it holds are "
                             "saved")
        if self.modes:
            lines.extend(self._mode_lines())
        else:
            lines.extend(_interference_lines(self.clashes, self.interference_error, self._interference_ran()))
        lines.extend(f"FAIL    {what}: {why}" for what, why in self.failures)
        if self.skipped:
            lines.append(f"SKIPPED {self.skipped}")
        return lines


def build_gearbox(sw: SolidWorks, parts: Sequence[BuildPlan], reuse: Sequence[DocumentValues] = (),
                  layout: Union[BuildPlan, DocumentValues, None] = None, assembly: Optional[BuildPlan] = None,
                  gears: Optional[Mapping[str, str]] = None, *,
                  exists: Callable[[str], bool] = os.path.exists,
                  progress: Optional[Callable[[Step], None]] = None,
                  mtime: Callable[[str], float] = os.path.getmtime,
                  senses: Optional[Mapping[str, bool]] = None,
                  lines: Optional[Mapping[str, Tuple[Vec3, Vec3]]] = None,
                  carriers: Sequence[Union[BuildPlan, DocumentValues]] = (),
                  modes: Optional[ModesPlan] = None) -> GearboxResult:
    """A workbook's parts, its layout part and its static assembly, in one worker job (PLAN-WORKBOOK §4.2–§4.3).

    ``parts`` are the new parts' plans; ``reuse`` the parts already built and
    unchanged; ``layout`` a plan to build, a saved layout to reuse
    (:class:`DocumentValues` with its globals and its plane and axis names),
    or None with ``assembly`` None too (Build parts: W2's batch, now able to
    resume over parts already made); ``gears`` maps each assembly handle to
    its gear id, for naming clashes. Order, and what may stop it:

    1. **Before anything is made**, raise :class:`BuildError` (nothing made,
       nothing changed) if a new path exists or two are the same, a reused
       path is missing, a document of the same file name is open from another
       folder (:func:`same_named_elsewhere` over every path built, opened or
       inserted), or a reused document cannot be opened and read. Each
       reused document is opened with ``open_document`` and checked live
       (decision 3: ``planned_changes(...) == []`` and every ``features``
       name present); one that does not hold what is expected is not a
       raise but :attr:`GearboxResult.mismatched` — every one is checked,
       its file's time noted (``mtime``), and the result returned with
       nothing made, so the finish records it and the next plan makes it
       new.
    2. The new parts, by :func:`build_many`; a failure skips the rest.
    3. The layout: built (a failure skips the assembly), or the reused one
       left open from step 1.
    4. The assembly, by :func:`build`; then, if it built cleanly,
       ``sw.interferences()`` (a raise becomes ``interference_error``).

    ``progress`` is told each :class:`Step` as it starts. Nothing is closed;
    a failed document is left open, unsaved. Runs on the worker thread.

    Also refused in step 1, each with a sentence: a plan that is not sound;
    an assembly with no layout; an assembly that would insert a file this
    job neither makes nor reuses; two files of one name from two folders;
    and documents built earlier going into the assembly while
    ``findings.REUSE_ADD_ROUTE`` is neither "opened" nor "closed". With
    "opened" (probe add_component_opened_part, 2026: AddComponent5 refused a
    closed part and took one opened by OpenDoc6) the reused documents must be
    open when the assembly inserts them, and they are, from the live check;
    with "closed" they would not need to be, but the live check opens them
    anyway. A clash keeps :attr:`GearboxResult.ok` True (W4 agreement 9).

    On SolidWorks 2026 (34.0.0, probe/gearbox_smoke.py 2026-11-13) the live
    check left every reused document unmodified, but once inserted into the
    new assembly, rebuilt and saved, each part (and the layout) read
    ``GetSaveFlag`` True: SolidWorks' own doing, nothing of theirs on disk is
    stale, so it is not a reason to mark them unsaved. The cause was the
    assembly's full rebuild (``ForceRebuild3(False)``, in ``rebuild`` and in
    every ``place_component``), which probe assembly_rebuild_scope found
    marking every component modified on 2026 and 2024; the assembly is now
    rebuilt top-only (``swcom.rebuild_call``), which is enough because every
    part and the layout were built, rebuilt and saved in their own documents
    first, and a reused one is only read. Refused before anything is made: an
    assembly while ``findings.ASSEMBLY_REBUILD_ROUTE`` is not settled.

    W5 (Agent A; W5-INTERFACES.md): an assembly plan that mates its gears is
    a train (:func:`workbook_assembly_kind`) and its :func:`build` runs the
    mate check before the save. A train SolidWorks refuses or flags a mate of
    is left open, unsaved, and nothing is built in its place — no static
    fallback (W5-DECISIONS, answer 1, overruling W5-PLAN D2): the parts and
    the layout part already saved stay saved and reach the finish, which
    records them as W4's continued revision. :attr:`GearboxResult.kind` says
    which assembly saved. The signature is unchanged: no ``static=``.

    ``senses`` (keyword, W6): gear mate name -> same sense (``k > 0``), as
    :func:`build` takes it, judged with every gear mate's planned axes before
    anything is made, parts included (:func:`_sense_gate`: a turned gear
    mate is refused while its sense cannot be read).

    ``lines`` (keyword, W6; review S7): a reused layout part's slanted
    shafts' line axes as the record has them (axis name -> (point,
    direction), mm), each read back when the layout is checked; one moved in
    SolidWorks makes the layout mismatched (:attr:`GearboxResult.mismatched`),
    as a changed global does, so it is not reused.

    W7 (W7-PLAN §2.9, W7-INTERFACES.md): ``carriers`` (keyword): each carrier part, a plan to make (a skeleton of
    axes and planes, built as the layout part is) or a saved one to reuse (checked live as the layout is, a
    mismatch recorded and nothing built), made after the layout part and before the assembly, each announced as
    ``Step(STAGE_CARRIER, stem)``, into :attr:`GearboxResult.carriers` (reused: ``carriers_reused``). A carrier
    part that fails skips the assembly, the parts and the layout part staying saved. Its paths join the pre-flight
    (never overwritten, a reused one still there, both among what the assembly may insert). The assembly's mate
    problems name a carrier by its id when ``gears`` maps the carrier's handle to it.

    W8 (W8-INTERFACES.md §3): ``modes`` (keyword), passed to :func:`build` for the assembly (its configurations,
    W8-PLAN §1.8 steps 1-7), judged before anything is made, parts included (:func:`_modes_gate`, with the running
    version). Each mode's check is in :attr:`GearboxResult.modes`; after the save, interference runs once per mode
    (step 8, :func:`_modes_interference`), the first mode's clashes also in ``clashes``, and the assembly is left in
    the first mode. ``positions_per_configuration`` is the running version's (:func:`swcom.positions_per_configuration`).
    None is W7's call.
    """
    say = progress or _quiet
    _gate(sw)
    gear_of_handle = dict(gears or {})
    layout_plan = layout if isinstance(layout, BuildPlan) else None
    layout_reuse = layout if isinstance(layout, DocumentValues) else None
    carrier_plans = [c for c in carriers if isinstance(c, BuildPlan)]
    carrier_reuse = [c for c in carriers if isinstance(c, DocumentValues)]
    if len(carrier_plans) + len(carrier_reuse) != len(carriers):
        raise BuildError("A carrier part was given as something that is neither a plan to make nor a saved part to "
                         "reuse, so nothing is made; that is a fault in Gear Generator.")
    if carriers and assembly is None:
        raise BuildError("Carrier parts were given with no assembly to put them in, so nothing is made; that is a "
                         "fault in Gear Generator.")
    if assembly is not None and layout is None:
        raise BuildError("The assembly is built around its layout part, and this build has neither a layout part "
                         "to make nor one to reuse.")
    _modes_gate(assembly, modes, revision=sw.revision, senses=senses)
    if assembly is not None:
        _assembly_rebuild_gate(workbook_assembly_kind(assembly))
        if workbook_assembly_kind(assembly) == ASSEMBLY_TRAIN:
            _train_gate(assembly, building=True)
            senses = _sense_gate(assembly, senses)
    plans = list(parts) + ([layout_plan] if layout_plan is not None else []) + carrier_plans + \
        ([assembly] if assembly is not None else [])
    for plan in plans:
        problems = plan.check()
        if problems:
            raise BuildError(f"The build plan for {_file(_saved_path(plan)) or plan.kind} is not sound: "
                             + " ".join(problems))
    made = [p for p in (_saved_path(plan) for plan in plans) if p]
    reused_docs = list(reuse) + ([layout_reuse] if layout_reuse is not None else []) + carrier_reuse
    reused = [d.path for d in reused_docs]
    for path in made:
        if exists(path):
            raise BuildError(f"{path} already exists, and a build never overwrites a file.")
    for path in reused:
        if not exists(path):
            raise BuildError(f"{path} is no longer there, so it cannot be reused: it was moved, renamed or deleted "
                             "since it was built.")
    open_before = _refuse_paths(sw, made, reused, "make", "reuse")
    inserted = [op.path for op in assembly.ops if isinstance(op, base.AddComponent)] if assembly is not None else []
    for path in inserted:
        if not any(same_path(path, p) for p in made + reused):
            raise BuildError(f"The assembly would insert {path}, which this build neither makes nor reuses.")
    reused_in_assembly = [p for p in reused if any(same_path(p, q) for q in inserted)]
    route = getattr(findings, "REUSE_ADD_ROUTE", None)
    if reused_in_assembly and route not in ("opened", "closed"):
        raise BuildError(f"Putting a document built earlier into a new assembly has not been settled on SolidWorks "
                         f"yet (findings.REUSE_ADD_ROUTE is {route!r}), so this build, which reuses "
                         f"{_file(reused_in_assembly[0])}, cannot start; run probe tier 7 first.")

    result = GearboxResult(open_before=list(open_before))
    if modes is not None:
        result.positions_per_configuration = positions_per_configuration(sw.revision)
    for index, doc in enumerate(reused_docs, 1):
        say(Step(STAGE_CHECK, _stem(doc.path), index, len(reused_docs)))
        try:
            result.held[doc.path] = _check_live(sw, doc, "reused", lambda path: _note_opened(sw, path, result),
                                                lines=lines if doc is layout_reuse else None)
        except NotAsBuilt as exc:
            # Not a refusal: the finish records it, and the next plan makes that part new (review B2's last
            # corner). Every document is still checked, so one press finds them all.
            result.mismatched.append((doc.path, str(exc)))
            try:
                result.mtimes[doc.path] = float(mtime(doc.path))
            except (OSError, ValueError, TypeError):
                pass
            continue
        result.checked.append(doc.path)
    if result.mismatched:
        result.skipped = "everything, because a document to reuse does not hold what it should"
        return result

    # From here on documents are made and saved: nothing raises out (W4 review B1). Each document's own trouble
    # is a failure on its BuildResult (_build_in_job); anything else becomes a failure on the result, so what
    # SolidWorks already saved still reaches the finish and the record.
    stage = ["the parts" if parts else "the layout part" if layout_plan is not None
             else "the carrier parts" if carrier_plans else "the assembly"]
    try:
        _build_gearbox_body(sw, result, parts, layout_plan, layout_reuse, assembly, gear_of_handle, exists, say,
                            stage, senses, carrier_plans, carrier_reuse, modes=modes)
    except Exception as exc:  # noqa: BLE001 - see above
        if stage[0] == "the interference check":
            result.interference_error = _said(exc)        # a clash check that cannot run is a CHECK, not a failure
            return result
        result.failures.append((stage[0], _said(exc)))
        rest = {"the parts": [p for p, planned in (("the layout part", layout_plan is not None),
                                                    (_carrier_phrase(carrier_plans), bool(carrier_plans)),
                                                    ("the assembly", assembly is not None)) if planned],
                "the layout part": [p for p, planned in ((_carrier_phrase(carrier_plans), bool(carrier_plans)),
                                                         ("the assembly", assembly is not None)) if planned],
                "the carrier parts": ["the assembly"] if assembly is not None else [],
                }.get(stage[0], [])
        if rest and not result.skipped:
            result.skipped = f"{' and '.join(rest)}, because the job stopped during {stage[0]}"
    return result


def _build_gearbox_body(sw: SolidWorks, result: GearboxResult, parts: Sequence[BuildPlan],
                        layout_plan: Optional[BuildPlan], layout_reuse: Optional[DocumentValues],
                        assembly: Optional[BuildPlan], gear_of_handle: Mapping[str, str],
                        exists: Callable[[str], bool], say: Callable[[Step], None], stage: List[str],
                        senses: Optional[Mapping[str, bool]] = None, carrier_plans: Sequence[BuildPlan] = (),
                        carrier_reuse: Sequence[DocumentValues] = (), *, modes: Optional[ModesPlan] = None) -> None:
    """Steps 2–4 of :func:`build_gearbox`, filling ``result`` as each document finishes; ``stage[0]`` says which
    step is under way, for the failure if something raises. W7: the carrier parts after the layout part."""
    later = [phrase for phrase, planned in (("the layout part", layout_plan is not None),
                                            (_carrier_phrase(carrier_plans), bool(carrier_plans)),
                                            ("the assembly", assembly is not None)) if planned]
    if parts:
        stage[0] = "the parts"
        build_many(sw, parts, exists, progress=say, into=result.parts)
        if not (all(r.ok and r.saved for r in result.parts.built) and not result.parts.skipped):
            if later:
                result.skipped = f"{' and '.join(later)}, because a part failed"
            return

    if layout_plan is not None:
        stage[0] = "the layout part"
        say(Step(STAGE_LAYOUT, _stem(_saved_path(layout_plan))))
        result.layout = _build_in_job(sw, layout_plan, exists)
        if not (result.layout.ok and result.layout.saved):
            rest = [p for p, planned in ((_carrier_phrase(carrier_plans), bool(carrier_plans)),
                                         ("the assembly", assembly is not None)) if planned]
            if rest:
                result.skipped = f"{' and '.join(rest)}, because the layout part failed"
            return
    elif layout_reuse is not None:
        result.layout_reused = layout_reuse.path

    # W7: each carrier part, a skeleton of axes and planes built as the layout part is, before the assembly.
    for doc in carrier_reuse:
        result.carriers_reused.append(doc.path)
    for plan in carrier_plans:
        stage[0] = "the carrier parts"
        say(Step(STAGE_CARRIER, _stem(_saved_path(plan))))
        built = _build_in_job(sw, plan, exists)
        result.carriers.append(built)
        if not (built.ok and built.saved):
            if assembly is not None:
                result.skipped = f"the assembly, because the carrier part {_file(_saved_path(plan))} failed"
            return

    if assembly is None:
        return
    stage[0] = "the assembly"
    stem = _stem(_saved_path(assembly))
    say(Step(STAGE_ASSEMBLY, stem))
    # Its kind said explicitly: today's workbook gearbox is fixed (static, top-only); W5's mated one is a train, by
    # the same predicate the gate above used.
    kind = workbook_assembly_kind(assembly)
    result.assembly = _build_in_job(sw, assembly, exists, kind=kind, gears=gear_of_handle, senses=senses,
                                    modes=modes, mode_checks=result.modes if modes is not None else None,
                                    progress=say)
    result.components = dict(result.assembly.components)
    if result.assembly.ok and result.assembly.saved:
        result.kind = GEARBOX_MOTION if kind == ASSEMBLY_TRAIN else GEARBOX_STATIC
    if result.assembly.ok and result.assembly.saved and getattr(findings, "INTERFERENCE_CHECKED", False):
        stage[0] = "the interference check"
        gear_of = {name: gear_of_handle.get(handle, name) for handle, name in result.components.items()}
        if modes is not None:
            _modes_interference(sw, result, result.modes, kind, gear_of, say, stem)
            return
        say(Step(STAGE_INTERFERENCE, stem))
        try:
            result.clashes = _clashes(sw.interferences(), gear_of)
        except Exception as exc:  # noqa: BLE001 - a clash check that cannot run is a CHECK, never a failure
            result.interference_error = _said(exc)


def _carrier_phrase(plans: Sequence[BuildPlan]) -> str:
    return "the carrier part" if len(plans) == 1 else "the carrier parts"


REPLACE_ROUTES = ("Transform2 put", "UnfixComponent, Transform2 put, FixComponent")   # REPLACE_FIXED_ROUTE
PLANETARY_PUT_ROUTE = "gear mates off around the puts"      # the one findings.PLANETARY_PUT_ROUTE this code puts by


@dataclass
class GearboxUpdate:
    """What :func:`update_gearbox` did. Nothing is saved: ``changed`` lists every document whose CONTENT it
    changed in SolidWorks — a part's or the layout's globals set, the assembly's components re-placed — and the
    record marks those unsaved until the app sees them saved (decision 3). A document SolidWorks marks modified
    only because it was rebuilt or read afterwards (frames, interference) is not in it: after a part-only Update the assembly is
    rebuilt (and so reads modified in SolidWorks) but holds nothing new, and listing it would tell a user who
    saved the part and closed the assembly unsaved that SolidWorks no longer holds this version. So what
    SolidWorks marks modified is ``changed`` and the assembly whenever ``rebuilt`` (it is then also read), as
    probe assembly_rebuild_scope saw.

    ``parts`` holds one result per part reached, in the order given;
    ``layout`` the layout's, if one was given and reached. ``found`` is each
    placed gear's live frame (rotation by rows, origin in mm) as read before
    anything moved — the finish compares it with the record to say a
    component the user dragged was put back. ``placed`` lists the gears
    re-placed because ``found`` differed from the wanted frame
    (:func:`same_frame`, modulo the gear's pitch). ``rebuilt`` is the
    assembly's one rebuild. ``failures`` are (what, why) in the order met.
    ``mtimes`` is each document's file time as read before the job changed
    anything (path -> ``os.path.getmtime``; a file whose time could not be
    read is left out): the finish marks a changed document unsaved at that
    time, so a save made in SolidWorks while the job was answering still
    reads as newer (W4 review nit). ``open_before`` and ``opened`` are as on
    :class:`GearboxResult`: the documents open when the job began, and those
    it opened from disk and found holding no unsaved changes (every part and
    the layout in the check phase, and the assembly when it was reached).
    """

    parts: List[UpdateResult] = field(default_factory=list)
    layout: Optional[UpdateResult] = None
    # W7: each carrier part's values as set, in the order given (after the layout's).
    carriers: List[UpdateResult] = field(default_factory=list)
    found: Dict[str, Tuple[Tuple[float, ...], Tuple[float, float, float]]] = field(default_factory=dict)
    placed: List[str] = field(default_factory=list)
    rebuilt: bool = False
    clashes: List[Clash] = field(default_factory=list)
    interference_error: str = ""
    failures: List[Tuple[str, str]] = field(default_factory=list)
    changed: List[str] = field(default_factory=list)
    skipped: str = ""
    mtimes: Dict[str, float] = field(default_factory=dict)
    open_before: Optional[List[str]] = None
    opened: List[str] = field(default_factory=list)
    # W5, the motion path only (``update_gearbox(..., motion=...)``); all empty on W4's static path, and ``found``
    # and ``placed`` keep their W4 meanings on the motion path too (every gear's frame as read before anything moved;
    # every gear put, mated or fixed). Found before anything changed, against the record — ``train_check`` with both
    # maps restricted to the MATED gears (fixed ones are W4's business, never "missing" or off axis here):
    # ``turned``, ``out_of_step`` and ``off_axis`` as TrainCheck has them, and its ``residuals`` for the log.
    # ``restored``: one entry per train that was put (W5-PLAN D4 and review M1: when a train needs any put, every
    # mated gear of it is put), listing that train's gears, in ``placements`` order, whose check-phase δ was not a
    # whole number of their pitch — the gears the put turned back to the built turn; a train put with none turned
    # (a layout move alone) has no entry, and a train not put is never listed. ``unsuppressed``:
    # recorded mates found suppressed and turned back on (D10), by name. ``axial``: gears whose "<Gear> Face Z" was
    # set, in ``face_globals`` order. ``ratios``: gear mates given a new ratio, by name (empty while
    # ``findings.GEAR_MATE_RATIO_ROUTE`` is None). ``extra_mates``: mates in the assembly the record does not list,
    # found suppressed and left as they are (an unsuppressed one refuses the Update in its check phase instead:
    # review M7). ``mates``: every mate as read after the last rebuild.
    turned: bool = False
    out_of_step: List[Tuple[str, str]] = field(default_factory=list)
    off_axis: List[str] = field(default_factory=list)
    residuals: List[Tuple[str, str, float]] = field(default_factory=list)
    restored: List[Tuple[str, ...]] = field(default_factory=list)
    unsuppressed: List[str] = field(default_factory=list)
    axial: List[str] = field(default_factory=list)
    ratios: List[str] = field(default_factory=list)
    # W5, the gear mates judged live (each recorded gear mate's ratio read in the check phase, as frames are): a gear
    # mate found at another ratio than the workbook wants though the plan asked no change of it (a remake lost with
    # an unsaved close, say), remade to the wanted ratio — also in ``ratios``; and a gear mate the plan asked to
    # change found already at the wanted ratio, so not remade (the record should take the plan's ratio for it).
    ratios_found: List[str] = field(default_factory=list)
    ratios_already: List[str] = field(default_factory=list)
    # ``ratios_read``: for every gear mate whose live ratio was read and acted on — to be remade (asked by the plan,
    # or in ``ratios_found``) or found already right (``ratios_already``) — ``(name, live_a, live_b, want_a,
    # want_b)``: the tooth counts SolidWorks held and the counts the workbook wants, integers, in the gear mate's
    # own gear order (its first selection first, as ``MateRef.gears``). A gear mate read and found at the ratio the
    # record already held, which the plan did not ask to change, is not listed. Filled in the check phase.
    ratios_read: List[Tuple[str, int, int, int, int]] = field(default_factory=list)
    # W5, which way each gear mate turns (probe ring_mate_sense). ``turned_round``: gear mates this Update made again
    # with the other Flip because the read-back found the remade one turning its gears against their mesh (by name,
    # also in ``ratios`` or ``sense_found_wrong``). ``sense_found_wrong``: gear mates the check phase read turning
    # against their mesh before anything changed, and remade (their trains put): filled when the check phase reads
    # the sense (:data:`SENSE_CHECK_FINDINGS`).
    turned_round: List[str] = field(default_factory=list)
    sense_found_wrong: List[str] = field(default_factory=list)
    # W6 (review M4): gear mates remade because the workbook now turns their gears the other way (a crossed shaft
    # moved to the other side of its partner; ``UpdatePlan.resensed``), read back against the new ``k``. Never in
    # ``sense_found_wrong`` (not found wrong: the workbook moved), and in ``ratios`` only when the ratio changed
    # too (then ``ratios_read`` has its counts). Filled once each is remade and read back.
    resensed: List[str] = field(default_factory=list)
    extra_mates: List[str] = field(default_factory=list)
    mates: List[MateState] = field(default_factory=list)
    # W8 (A fills them; W8-PLAN §1.10, W8-INTERFACES.md §3), all empty for a gearbox with no modes.
    # ``configuration``: the one Update worked in (active when it opened the assembly). ``visited``: the others it
    # showed and post-checked, in mode order (none in a quiet Update that put nothing; every other mode once it put
    # the active one, W8-INTERFACES §9.18). ``unsuppressed_in`` / ``suppressed_in``: ``(mate, configuration)``
    # turned on / suppressed (D10 per configuration and J14's flags). ``slid``: ``(SLIDE name, configuration, value
    # mm)`` set for a J14 edit; ``values_restored``: ``(SLIDE name, configuration)`` set back to the record's value.
    # ``put_in``: the configurations in which gears were put, in the order put (the active one last on a changed
    # Update; first when a quiet Update put it and then visited the others). ``extra_configurations``:
    # configurations the record does not know, left as they are. ``modes``: the post-check of each configuration
    # visited, and of the one worked in. ``positions_per_configuration``: as on GearboxResult.
    configuration: str = ""
    visited: List[str] = field(default_factory=list)
    unsuppressed_in: List[Tuple[str, str]] = field(default_factory=list)
    suppressed_in: List[Tuple[str, str]] = field(default_factory=list)
    slid: List[Tuple[str, str, float]] = field(default_factory=list)
    values_restored: List[Tuple[str, str]] = field(default_factory=list)
    put_in: List[str] = field(default_factory=list)
    extra_configurations: List[str] = field(default_factory=list)
    modes: List[ModeCheck] = field(default_factory=list)
    positions_per_configuration: Optional[bool] = None
    # W8-INTERFACES §9.16: the recorded gear mates (meshes, couplings, splines) of a gearbox with modes whose sense no
    # read reached in this Update — in a quiet one, those off in the active configuration while a suppressed gear
    # mate's sense is not read (findings.SUPPRESSED_GEAR_MATE_SENSE_READ), and every one while the read-back is not
    # settled — by name, in the record's order; empty when every sense was read, and for a gearbox with no modes.
    senses_unread: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Nothing failed and nothing was left unattempted. Clashes, and an interference check that could not run,
        do not count against it (as in a build)."""
        return not self.failures and not self.skipped

    def log_lines(self) -> List[str]:
        """Each document's values, the re-placed gears, the assembly's rebuild, any failure, the interference,
        what was changed and not saved, then ``SKIPPED …``."""
        lines: List[str] = []
        for result in self.parts + ([self.layout] if self.layout is not None else []) + list(self.carriers):
            lines.append(f"update  {result.document or '(no document)'} · trig {result.trig or '?'}")
            if result.changed:
                lines.append("ok      set " + ", ".join(f'"{n}"' for n in result.changed))
            elif not result.failures:
                lines.append("ok      already holds the workbook's values")
            if result.changed:
                lines.append("ok      rebuilt once" if result.rebuilt else "FAIL    the rebuild reported an error")
        if self.found:
            if self.placed:
                lines.append("ok      re-placed " + ", ".join(self.placed))
            elif self.turned:
                lines.append("ok      nothing needed putting: the gears stay turned where they stand, in step")
            else:
                lines.append("ok      every gear is where the workbook puts it")
        lines.extend(self._motion_lines())
        if self.rebuilt:
            lines.append("ok      assembly rebuilt once")
        lines.extend(f"FAIL    {what}: {why}" for what, why in self.failures)
        ran = self.rebuilt and not self.failures and bool(getattr(findings, "INTERFERENCE_CHECKED", False))
        lines.extend(_interference_lines(self.clashes, self.interference_error, ran))
        if self.changed:
            lines.append("not saved: " + ", ".join(_file(p) for p in self.changed)
                         + " changed in SolidWorks; save there to keep it")
        else:
            lines.append("nothing changed in SolidWorks")
        if self.skipped:
            lines.append(f"SKIPPED {self.skipped}")
        return lines

    def _motion_lines(self) -> List[str]:
        """What the motion path found and did (every field here is empty on W4's static path, so it adds nothing
        there): as found before the Update, what was turned back, turned back on, moved along a shaft or given a
        new ratio, mates left alone, and every mate as last read."""
        lines: List[str] = []
        if self.off_axis:
            lines.append("ok      found off their axes before the Update: " + ", ".join(self.off_axis))
        if self.out_of_step:
            lines.append("ok      found out of step before the Update: "
                         + ", ".join(f"{a} with {b}" for a, b in self.out_of_step))
        if self.turned:
            lines.append("ok      found turned in SolidWorks, in step")
        for gears in self.restored:
            lines.append("ok      turned back to where they were built: " + ", ".join(gears))
        if self.unsuppressed:
            lines.append("ok      turned back on: " + ", ".join(self.unsuppressed))
        if self.axial:
            lines.append("ok      moved along their shafts: " + ", ".join(self.axial))
        if self.ratios:
            lines.append("ok      given their new ratio: " + ", ".join(self.ratios))
        if self.ratios_found:
            lines.append("ok      found in SolidWorks at another ratio than the workbook's, and remade: "
                         + ", ".join(self.ratios_found))
        if self.ratios_already:
            lines.append("ok      already at the ratio the workbook asks, so not remade: " + ", ".join(self.ratios_already))
        if self.sense_found_wrong:
            lines.append("ok      found turning against their mesh, so made again: " + ", ".join(self.sense_found_wrong))
        if self.resensed:
            lines.append("ok      made again to turn their gears the other way, as the workbook now has them: "
                         + ", ".join(self.resensed))
        if self.turned_round:
            lines.append("ok      made again with the other Flip: " + ", ".join(self.turned_round))
        if self.extra_mates and self.configuration:
            # W8 (J12): read in every mode's configuration only; one the record does not know is never read.
            lines.append("CHECK   mates Gear Generator did not make, suppressed in every mode, left as they are: "
                         + ", ".join(self.extra_mates))
        elif self.extra_mates:
            lines.append("CHECK   suppressed mates Gear Generator did not make, left as they are: "
                         + ", ".join(self.extra_mates))
        lines.extend(self._mode_update_lines())
        lines.extend(_mate_line(mate) for mate in self.mates)
        return lines

    def _mode_update_lines(self) -> List[str]:
        """W8: where the Update worked, what it set per configuration, where it put, and what each mode it showed
        was found holding (§9.11: always which mode it worked in, and that it did not show the others)."""
        if not self.configuration:
            return []
        lines = []
        if self.visited:
            lines.append(f"ok      worked in {self.configuration}, the configuration that was active, and showed "
                         f"{', '.join(self.visited)} too")
        else:
            lines.append(f"ok      worked in {self.configuration}, the configuration that was active; did not show "
                         "the other modes")
        if self.unsuppressed_in:
            lines.append("ok      turned back on: " + ", ".join(f"{m} in {c}" for m, c in self.unsuppressed_in))
        if self.suppressed_in:
            lines.append("ok      suppressed again: " + ", ".join(f"{m} in {c}" for m, c in self.suppressed_in))
        if self.values_restored:
            lines.append("ok      slides set back to the record: " + ", ".join(f"{m} in {c}"
                                                                             for m, c in self.values_restored))
        if self.slid:
            lines.append("ok      slides moved: " + ", ".join(f"{m} in {c} to {v:g} mm" for m, c, v in self.slid))
        if self.put_in:
            lines.append("ok      gears put in " + ", ".join(self.put_in))
        for check in self.modes:
            if check.off_axis or check.out_of_step:
                found = [f"{g} off its axis" for g in check.off_axis] + \
                    [f"{a} with {b} out of step" for a, b in check.out_of_step]
                lines.append(f"ok      found in mode {check.name}: " + ", ".join(found))
        if self.extra_configurations:
            lines.append("CHECK   configurations Gear Generator did not make, left as they are: "
                         + ", ".join(self.extra_configurations))
        if self.senses_unread:
            lines.append("CHECK   which way these gear mates turn was not read, since no mode shown had them on: "
                         + ", ".join(self.senses_unread))
        return lines


def _update_document(sw: SolidWorks, doc: DocumentValues) -> Tuple[UpdateResult, List[Tuple[str, str]]]:
    """``open_document`` then :func:`update_variables`; the result and its failures, never a raise."""
    name = _file(doc.path)
    try:
        sw.open_document(doc.path)
        result = update_variables(sw, doc.variables, doc.path)
    except Exception as exc:  # noqa: BLE001 - a raise is this document's failure, never the job's (B1)
        # Marked on the document's own result too, so the finish never takes it for one found holding its values.
        return UpdateResult(document=name, failures=[("", _said(exc))]), [(name, _said(exc))]
    failures = [(f"{name} {what}", why) for what, why in result.failures]
    if result.changed and not result.rebuilt:
        failures.append((name, f"SolidWorks reported an error rebuilding {_stem(doc.path)}."))
    return result, failures


MODE_MATE_KINDS = ("slide", "spline", "couple")      # workbook.motion SLIDE, SPLINE, COUPLE: W8's mates


def update_gearbox(sw: SolidWorks, parts: Sequence[DocumentValues] = (), layout: Optional[DocumentValues] = None,
                   assembly: str = "", placements: Sequence[Placement] = (), *,
                   motion: Optional[MotionUpdate] = None,
                   exists: Callable[[str], bool] = os.path.exists,
                   progress: Optional[Callable[[Step], None]] = None,
                   mtime: Callable[[str], float] = os.path.getmtime,
                   lines: Optional[Mapping[str, Tuple[Vec3, Vec3]]] = None,
                   carriers: Sequence[DocumentValues] = ()) -> GearboxUpdate:
    """Update SolidWorks from the workbook: part values, the layout's globals, and the static assembly's
    components re-placed (PLAN-WORKBOOK §4.5), in one worker job and in two phases, so a missing piece changes
    nothing.

    *Check* — raise :class:`BuildError` before any change if a path is
    missing, a same-named document is open from another folder, a document
    lacks a global it should hold (``planned_changes`` raises), or a
    component is not found by its recorded ``Name2`` — those three a
    :class:`NotAsBuilt` naming the document, since only a new revision
    (Build again…) gets past them. Each document is opened
    with ``open_document`` (decision: Update always opens and activates) and
    read, writing nothing (:func:`_read_live`); each file's time is noted
    first (``mtime``, into :attr:`GearboxUpdate.mtimes`).

    *Change* — each part, then the layout, that does not already hold what
    it should: ``open_document`` then :func:`update_variables`; the first
    failure stops. A document the check found holding every global already
    (in either trig unit, and evaluating them as that unit would:
    :func:`_held_unit`) is not touched at all: no trig units measured, no
    equation added, nothing set (W4 review S2: on SolidWorks 2026 measuring
    the units alone left every part marked modified, so every Update asked
    for saves of parts it had not changed). Then the assembly, when
    ``assembly`` is given: ``open_document``, ``find_component`` each, read
    ``component_frame``, re-place only those not :func:`same_frame` (with
    Unfix/Fix around it if ``findings.REPLACE_FIXED_ROUTE`` asks); then, if
    any document changed or any gear was re-placed (a teeth change alters
    the mesh), one ``rebuild`` and ``interferences`` — with nothing changed,
    the assembly is only read.

    Compares with SolidWorks live, never with the record, so an update the
    user never saved, or a component they dragged, is put right on the next
    press. Saves nothing and closes nothing. After the check phase nothing
    raises out: a raise becomes a failure on the result, so what was changed
    is still reported and recorded unsaved (W4 review B1). Runs on the worker
    thread.

    The check phase also refuses: placements with no assembly; one
    component recorded for two gears; a layout plane or axis no longer in
    the layout; new values that do not evaluate (:func:`_evaluates`, in both
    trig units, measuring only when they differ); re-placing while
    ``REPLACE_FIXED_ROUTE`` is not one of :data:`REPLACE_ROUTES` (probe
    layout_assembly_reopen, 2026: a Transform2 put moved a FIXED component
    and the frame survived a save and reopen, so "Transform2 put"). When
    ``findings.OPEN_PART_BESIDE_ASSEMBLY`` is not True (probe
    open_part_from_assembly, 2026: it is), values are not changed while the
    assembly is open — the user is asked to close it — and the assembly is
    opened only after the values, so a missing component is then a failure
    rather than a refusal. ``place_component`` reads each frame back after a
    rebuild of its own (probe nonparallel_mates); the assembly's one
    rebuild here is the one after every put, with ``CommandInProgress``
    restored in a ``finally``. Both are top-only (``swcom.rebuild_call``,
    probe assembly_rebuild_scope): each changed part and the layout were
    already rebuilt in their own documents by :func:`update_variables`, and a
    full rebuild of the assembly marked every part modified, those Update
    never touched among them. Refused in the check phase too: an assembly
    while ``findings.ASSEMBLY_REBUILD_ROUTE`` is not settled.

    W5: ``motion`` None is all of the above, unchanged (a W4 static
    gearbox, W5-PLAN D5). Given, the assembly is a train
    (``ASSEMBLY_TRAIN`` for every rebuild and put) and the motion path runs
    in W5-PLAN §1.6's order as W5-INTERFACES.md amends it
    (:func:`_update_motion`).

    W6: ``lines`` (keyword; W6-PLAN §2.7, review S7): the layout part's
    slanted shafts' line axes as the record has them (axis name -> (point,
    direction), mm), read back in the check phase with the layout part; one
    moved in SolidWorks is a :class:`NotAsBuilt` and nothing changes.

    W8 (W8-PLAN §1.10): a ``motion`` with ``configurations`` is a gearbox with modes, updated across its
    configurations (:func:`_modes_check`, :func:`_modes_assembly`): the check phase reads every flag, slide value and
    coupling sense in every mode without showing one; the change phase sets flags and values per configuration
    without showing, then puts once per mode with that mode shown, the active one last and shown again at the end.
    A record carrying anything of modes without its configurations is refused before anything is read
    (:func:`_update_modes_gate`, W8-INTERFACES §9.2), so it never goes down W7's path.

    W7 (W7-PLAN §2.9): ``carriers`` (keyword): each carrier part's globals as now wanted, read in the check
    phase with the parts and the layout (a missing global or plane is :class:`NotAsBuilt`) and set in the change
    phase after the layout's, as the layout's are (one already holding them untouched), so its axes move before the
    assembly rebuilds; each result in :attr:`GearboxUpdate.carriers`. A carrier part that fails stops the job before
    the assembly.
    """
    _update_modes_gate(motion, sw.revision)
    if lines and layout is None:
        raise BuildError("Update SolidWorks was given line axes to check but no layout part to find them in, so "
                         "nothing is changed; that is a fault in Gear Generator.")
    if motion is not None and not carriers and (
            motion.carriers or motion.held
            or any(m.carrier for m in tuple(motion.meshes) + tuple(motion.recorded_meshes))):
        # W7-INTERFACES §6.3: a planetary gearbox always comes with its carrier parts, so it can never be updated
        # as a W6 train.
        raise BuildError("Update SolidWorks was given a planetary stage without its carrier part, so nothing is "
                         "changed; that is a fault in Gear Generator.")
    if motion is not None:
        return _update_motion(sw, parts, layout, assembly, placements, motion, exists, progress, mtime, lines,
                              carriers=carriers)
    say = progress or _quiet
    _gate(sw)
    result = GearboxUpdate()
    documents = list(parts) + ([layout] if layout is not None else []) + list(carriers)
    paths = [d.path for d in documents] + ([assembly] if assembly else [])
    if placements and not assembly:
        raise BuildError("Gears can only be re-placed in an assembly, and Update SolidWorks was given none.")
    if assembly:
        _assembly_rebuild_gate(ASSEMBLY_STATIC)    # the workbook's static gearbox: fixed components, no mates
    for path in paths:
        if not exists(path):
            raise BuildError(f"{path} is no longer there, so Update SolidWorks cannot change it: it was moved, "
                             "renamed or deleted since it was built.")
    open_before = _refuse_paths(sw, [], paths, "make", "change")
    result.open_before = list(open_before)
    for index, placement in enumerate(placements):
        for earlier in placements[:index]:
            if placement.component == earlier.component:
                raise BuildError(f"{placement.component} is recorded for both {earlier.gear} and {placement.gear}, "
                                 "so one of them would be placed twice.")
    route = getattr(findings, "REPLACE_FIXED_ROUTE", None)
    if placements and route not in REPLACE_ROUTES:
        raise BuildError(f"Moving a fixed component has not been settled on SolidWorks yet "
                         f"(findings.REPLACE_FIXED_ROUTE is {route!r}), so Update SolidWorks cannot re-place the "
                         "gears; run probe tier 7 first.")
    beside = getattr(findings, "OPEN_PART_BESIDE_ASSEMBLY", None) is True
    if assembly and documents and not beside and any(same_path(d.path, assembly) for d in sw.documents()):
        raise BuildError(f"Close {_file(assembly)} in SolidWorks, then press Update SolidWorks again: changing a "
                         "part while its assembly is open has not been settled on this SolidWorks "
                         "(findings.OPEN_PART_BESIDE_ASSEMBLY).")
    for path in paths:
        try:
            result.mtimes[path] = float(mtime(path))
        except (OSError, ValueError, TypeError):
            pass

    # -- check: opens and reads, writes nothing
    total = len(paths)
    holds: List[str] = []           # per document: the trig unit it already holds every global in, or ""
    for index, doc in enumerate(documents, 1):
        say(Step(STAGE_CHECK, _stem(doc.path), index, total))
        _, by_unit, values = _read_live(sw, doc, "updated", lambda path: _note_opened(sw, path, result),
                                        lines=lines if doc is layout else None)
        holds.append(_held_unit(by_unit, values, doc.variables))
    if assembly and (beside or not documents):
        say(Step(STAGE_CHECK, _stem(assembly), total, total))
        sw.begin_build()
        try:
            sw.open_document(assembly)
            _note_opened(sw, assembly, result)
            for index, placement in enumerate(placements, 1):
                sw.find_component(f"placed{index}", placement.component)
        except ComponentGone as exc:      # renamed or deleted in SolidWorks: only a new revision puts it back
            raise NotAsBuilt(str(exc), assembly) from None
        except SolidWorksError as exc:
            raise BuildError(str(exc)) from None
        finally:
            sw.end_build()
    for doc, unit in zip(documents, holds):
        if not unit:
            _evaluates(sw, doc, "updated")

    # -- change: values first, then the assembly. Nothing raises out from here (B1).
    stage = [_file(documents[0].path) if documents else _file(assembly)]
    try:
        _update_change(sw, result, parts, layout, documents, holds, assembly, placements, route, say, stage)
    except Exception as exc:  # noqa: BLE001 - see above
        result.failures.append((stage[0], _said(exc)))
        if not result.skipped and assembly and stage[0] != _file(assembly):
            result.skipped = f"the assembly, because the job stopped during {stage[0]}"
    finally:
        if result.placed and assembly not in result.changed:
            result.changed.append(assembly)
    return result


def _update_values(sw: SolidWorks, result: GearboxUpdate, parts: Sequence[DocumentValues],
                   layout: Optional[DocumentValues], documents: Sequence[DocumentValues], holds: Sequence[str],
                   assembly: str, say: Callable[[Step], None], stage: List[str]) -> bool:
    """Each part, then the layout, then each carrier part (W7: ``documents`` past the parts and the layout), set as
    W4's Update sets them (a document holding its values already is left untouched: S2); True when one failed,
    which stops the job (``result.skipped`` says what was left)."""
    first_carrier = len(parts) + (1 if layout is not None else 0)
    for position, doc in enumerate(documents):
        stage[0] = _file(doc.path)
        in_parts = position < len(parts)
        is_carrier = position >= first_carrier
        if holds[position]:
            # It already holds every global as asked: left as it is, not even its trig units measured (S2).
            done = UpdateResult(document=_file(doc.path), unchanged=[v.name for v in doc.variables],
                                trig=holds[position])
            failures: List[Tuple[str, str]] = []
        else:
            say(Step(STAGE_VALUES, _stem(doc.path)))
            done, failures = _update_document(sw, doc)
        if in_parts:
            result.parts.append(done)
        elif is_carrier:
            result.carriers.append(done)
        else:
            result.layout = done
        if done.changed:
            result.changed.append(doc.path)
        if failures:
            result.failures.extend(failures)
            rest = len(parts) - position - 1 if in_parts else 0
            left = [f"{rest} more part{'s' if rest != 1 else ''}"] if rest else []
            if layout is not None and in_parts:
                left.append("the layout part")
            carriers_left = len(documents) - max(position + 1, first_carrier)
            if carriers_left:
                left.append("the carrier part" if carriers_left == 1 else f"{carriers_left} carrier parts")
            if assembly:
                left.append("the assembly")
            if left:
                listed = left[0] if len(left) == 1 else ", ".join(left[:-1]) + f" and {left[-1]}"
                result.skipped = f"{listed}, because {_file(doc.path)} failed"
            return True
    return False


def _update_change(sw: SolidWorks, result: GearboxUpdate, parts: Sequence[DocumentValues],
                   layout: Optional[DocumentValues], documents: Sequence[DocumentValues], holds: Sequence[str],
                   assembly: str, placements: Sequence[Placement], route: Optional[str],
                   say: Callable[[Step], None], stage: List[str]) -> None:
    """The change phase of :func:`update_gearbox`, filling ``result`` as it goes; ``stage[0]`` names the document
    under way, for the failure if something raises."""
    if _update_values(sw, result, parts, layout, documents, holds, assembly, say, stage):
        return

    if not assembly:
        return
    stage[0] = _file(assembly)
    stem = _stem(assembly)
    say(Step(STAGE_PLACE, stem))
    sw.begin_build()
    try:
        opened = False
        try:
            sw.open_document(assembly)
            opened = True
            _note_opened(sw, assembly, result)
            handles = [f"placed{index}" for index in range(1, len(placements) + 1)]
            for handle, placement in zip(handles, placements):
                sw.find_component(handle, placement.component)
            for handle, placement in zip(handles, placements):
                rotation, at = sw.component_frame(handle)
                result.found[placement.gear] = (tuple(rotation), tuple(at))
            moves = [(h, p) for h, p in zip(handles, placements)
                     if not same_frame(result.found[p.gear][0], result.found[p.gear][1], p.rotation, p.at, p.pitch)]
            unfix = route == REPLACE_ROUTES[1]
            sw.set_rebuild_suppressed(True)
            try:
                for handle, placement in moves:
                    if unfix:
                        sw.unfix_component(handle)
                    sw.place_component(handle, placement.rotation, placement.at, kind=ASSEMBLY_STATIC)
                    result.placed.append(placement.gear)
                    if unfix:
                        sw.fix_component(handle)
            finally:
                sw.set_rebuild_suppressed(False)
        except Exception as exc:  # noqa: BLE001 - the assembly's failure; what was placed stays listed (B1)
            result.failures.append((_file(assembly), _said(exc)))
        if opened and (result.changed or result.placed):
            result.rebuilt = bool(sw.rebuild(kind=ASSEMBLY_STATIC))
            if not result.rebuilt:
                result.failures.append((_file(assembly), f"SolidWorks reported an error rebuilding {stem}."))
        if result.rebuilt and not result.failures and getattr(findings, "INTERFERENCE_CHECKED", False):
            say(Step(STAGE_INTERFERENCE, stem))
            gear_of = {p.component: p.gear for p in placements}
            try:
                result.clashes = _clashes(sw.interferences(), gear_of)
            except Exception as exc:  # noqa: BLE001 - a clash check that cannot run is a CHECK, never a failure
                result.interference_error = _said(exc)
    finally:
        sw.end_build()


# -- W5: Update SolidWorks on a gearbox built to turn (W5-PLAN §1.6 as W5-INTERFACES.md §3 orders it) ---------------

# What the motion path rests on (findings.py, tier 8 and items 7-13), each read with getattr: (name, the value it
# must have, what it settles, whether it is needed only when the record holds locks / Face Z globals).
MOTION_UPDATE_FINDINGS = (
    ("MESH_PHASE_ROUTE", "Transform2 put with the gear mate on", "putting a gear with its gear mate on", ""),
    ("SUPPRESSION_ROUTE", "SetSuppression2 this configuration, None", "suppressing a mate and turning it back on", ""),
    ("FEATURE_SUPPRESS", _SET, "suppressing a mate and turning it back on", ""),
    ("FEATURE_UNSUPPRESS", _SET, "suppressing a mate and turning it back on", ""),
    ("THIS_CONFIGURATION", _SET, "suppressing a mate and turning it back on", ""),
    ("LAYOUT_MOVE_CARRIES_MATES", True, "a mated gear following its shaft when the layout moves", ""),
    ("LOCK_UNSUPPRESS_KEEPS_THE_NEW_ANGLE", True, "a lock keeping the angle a gear was put at", "locks"),
    ("AXIAL_GLOBAL_MOVES_GEAR", True, "a gear moved along its shaft by its Face Z global", "face_globals"),
    ("GEAR_MATE_DEFINITION_READS_NUMERATOR_SECOND", _SET, "reading a gear mate's ratio", "meshes"),
    # The check phase reads every recorded gear mate's definition before anything changes, so an Update with nothing
    # to do must leave every document unmarked (probe round P0c, gear_mate_definition_read).
    ("GEAR_MATE_DEFINITION_READ_MARKS", "nothing", "reading a gear mate's ratio without marking the assembly",
     "meshes"),
    ("GEAR_MATE_RATIO_REMAKE_WORKS", True, "making a gear mate again at a new ratio", "ratios"),
    ("MATE_DELETE_ROUTE", "Select2 then EditDelete()", "making a gear mate again at a new ratio", "ratios"),
    ("MATE_RENAME_ROUTE", "IFeature.Name put", "making a gear mate again at a new ratio", "ratios"),
    ("GEAR_MATE_FLIP", _SET, "making a gear mate again at a new ratio", "ratios"),
    ("GEAR_MATE_ROUTE", _SET, "making a gear mate again at a new ratio", "ratios"),
    ("MATE_GEAR", _SET, "making a gear mate again at a new ratio", "ratios"),
    ("GEAR_MATE_NUMERATOR_FIRST", _SET, "making a gear mate again at a new ratio", "ratios"),
)


def _motion_gate(motion: MotionUpdate) -> None:
    """Refuse, before anything is read or changed, a motion Update whose SolidWorks calls are not settled: a new
    ratio first by its route (the reason a user can act on), then every finding of :data:`MOTION_UPDATE_FINDINGS`."""
    route = getattr(findings, "GEAR_MATE_RATIO_ROUTE", None)
    if motion.ratios and route != "remake":
        raise BuildError(f"Giving a gear mate a new ratio has not been settled on SolidWorks (findings."
                         f"GEAR_MATE_RATIO_ROUTE is {route!r}), so nothing is changed; build the gearbox again for a "
                         "new tooth count.")
    for name, wanted, what, needed_for in MOTION_UPDATE_FINDINGS:
        if needed_for and not getattr(motion, needed_for):
            continue
        value = getattr(findings, name, None)
        if value is None or (wanted is not _SET and value != wanted):
            raise BuildError(f"Update SolidWorks on a gearbox built to turn needs {what} settled on SolidWorks "
                             f"(findings.{name} is {value!r}), so nothing is changed; run probe tier 8 first.")


def _remake_gate() -> None:
    """The remake's findings (:data:`MOTION_UPDATE_FINDINGS` marked "ratios"), for a remake the live check phase
    found needed though the plan asked none; read before anything changes."""
    for name, wanted, what, needed_for in MOTION_UPDATE_FINDINGS:
        if needed_for != "ratios":
            continue
        value = getattr(findings, name, None)
        if value is None or (wanted is not _SET and value != wanted):
            raise BuildError(f"Update SolidWorks on a gearbox built to turn needs {what} settled on SolidWorks "
                             f"(findings.{name} is {value!r}), so nothing is changed; run probe tier 8 first.")


def _idler_gate(motion: MotionUpdate, remakes: Sequence[Tuple[str, int, int]]) -> None:
    """A remake on a gear that carries two (or more) recorded gear mates — an idler — rests on probe round P0c's
    idler_update (``findings.IDLER_UPDATE_HOLDS``): refused before anything changes while that is not True. A train
    whose remade gear mates touch no such gear (the 12 : 1) does not read it."""
    carried: Dict[str, int] = {}
    for mate in motion.mates:
        if mate.kind == "mesh":
            for gear in mate.gears:
                carried[gear] = carried.get(gear, 0) + 1
    remade = {name for name, _, _ in remakes}
    idlers = [g for m in motion.mates if m.kind == "mesh" and m.name in remade for g in m.gears if carried[g] > 1]
    value = getattr(findings, "IDLER_UPDATE_HOLDS", None)
    if idlers and value is not True:
        gear = idlers[0]
        raise BuildError(f"Giving a new ratio to a gear mate of {gear}, which carries two gear mates, has not been "
                         f"settled on SolidWorks (findings.IDLER_UPDATE_HOLDS is {value!r}), so nothing is changed; "
                         "run probe tier 8 first, or build the gearbox again.")


# The check phase's read of every recorded gear mate's sense: it marks nothing, a read after a rebuild, a remake or a
# save and reopen agrees with the drive as one straight after AddMate5 does, and a train saved by one version reads
# right in the other (probe ring_trains_saved). Any of them missing: the check phase does not read the sense.
SENSE_CHECK_FINDINGS = (("GEAR_MATE_SENSE_READ_MARKS", "nothing"), ("GEAR_MATE_SENSE_READ_POINTS_AGREE", True),
                        ("CROSS_VERSION_READ_BACK_TELLS_SENSE", True))
# A Build reads each gear mate's sense, and remakes a wrong one, straight after making it, inside the batch it makes
# its mates in with CommandInProgress on (probe ring_trains_saved: both held there).
BUILD_SENSE_FINDINGS = (("GEAR_MATE_SENSE_READ_UNDER_COMMAND_IN_PROGRESS", True),
                        ("GEAR_MATE_REMAKE_UNDER_COMMAND_IN_PROGRESS", True))


def _mesh_senses(motion: MotionUpdate) -> Dict[str, bool]:
    """Each recorded gear mate's mesh sense as now wanted: whether it turns its two gears the same way about their own
    axes, ``k > 0`` of its ``MeshLink`` (``k = −c·za/zb``, W6-PLAN §2.4) — for any axes, parallel or turned."""
    out: Dict[str, bool] = {}
    for mate in motion.mates:
        if mate.kind != "mesh" or len(mate.gears) != 2:
            continue
        link = next((m for m in motion.meshes if (m.a, m.b) == tuple(mate.gears)), None)
        if link is not None:
            out[mate.name] = link.k > 0
    return out


def _resensed(motion: MotionUpdate) -> List[str]:
    """The recorded gear mates whose mesh sense the plan changes (a crossed shaft moved to the other side of its
    partner, W6-PLAN §2.7, review M4): ``k``'s sign in ``meshes`` against ``recorded_meshes`` (the record's own
    senses). Each is remade, its tooth counts new or not, and read back against the new ``k``."""
    out: List[str] = []
    for mate in motion.mates:
        if mate.kind != "mesh" or len(mate.gears) != 2:
            continue
        now = next((m for m in motion.meshes if (m.a, m.b) == tuple(mate.gears)), None)
        then = next((m for m in motion.recorded_meshes if (m.a, m.b) == tuple(mate.gears)), None)
        if now is not None and then is not None and now.k and then.k and (now.k > 0) != (then.k > 0):
            out.append(mate.name)
    return out


def _mate_ends(motion: MotionUpdate, name: str, axes: Mapping[str, Vec3]) -> Tuple[str, str, Vec3, Vec3]:
    """A recorded gear mate's two gears and their own axes as now placed."""
    ga, gb = next(m.gears for m in motion.mates if m.name == name)
    return ga, gb, axes[ga], axes[gb]


def _turned_update_gate(motion: MotionUpdate, axes: Mapping[str, Vec3], origins: Mapping[str, Vec3]) -> None:
    """Before anything is read or changed: every recorded gear mate between gears whose axes are not of one family
    needs its sense readable (the turned finding, the angle inside it; :func:`swcom.turned_refusal`), since the
    check phase reads it and a remake reads it back (W6-PLAN §2.6, §2.7)."""
    for mate in motion.mates:
        if mate.kind != "mesh" or len(mate.gears) != 2:
            continue
        ga, gb = axes.get(mate.gears[0]), axes.get(mate.gears[1])
        if ga is None or gb is None or axes_parallel(ga, gb):
            continue
        meet = lines_meet(origins[mate.gears[0]], ga, origins[mate.gears[1]], gb)
        refusal = turned_refusal(mate.name, own_axes_angle(ga, gb), "so nothing is made or changed.", meet=meet)
        if refusal is not None:
            raise BuildError(refusal)


def _remake_sense_gate(remakes: Sequence[Tuple[str, int, int]], senses: Mapping[str, bool], motion: MotionUpdate,
                       axes: Mapping[str, Vec3]) -> None:
    """A remake's gear mate is read back and turned round if wrong: that needs the read-back and the remake with the
    other Flip settled; without the read-back a remake inside a ring is refused (its sense cannot be told), and one
    outside goes ahead as before (GEAR_MATE_FLIP is right for an outside pair on both versions). A turned gear mate
    never gets here unread: :func:`_turned_update_gate` refuses it first."""
    missing = _settled(SENSE_FINDINGS)
    if missing is not None:
        rings = [name for name, _, _ in remakes
                 if name in senses and _inside_ring(senses[name], *_mate_ends(motion, name, axes)[2:])]
        if rings:
            raise BuildError(f"The gear mate {rings[0]} meshes inside a ring, and which way a gear mate turns a ring "
                             f"cannot be told on SolidWorks yet (findings.{missing[0]} is {missing[1]!r}), so nothing "
                             "is changed; run probe ring_mate_sense first, or build the gearbox again.")
        return
    missing = _settled(SENSE_REMAKE_FINDINGS + (("GEAR_MATE_READ_BACK_HOLDS_AFTER_A_RATIO_REMAKE", True),))
    if missing is not None:
        raise BuildError(f"Update SolidWorks on a gearbox built to turn needs findings.{missing[0]} settled on "
                         f"SolidWorks (it is {missing[1]!r}), so nothing is changed; run probe tier 8 first.")


def _wanted_teeth(motion: MotionUpdate) -> Dict[str, Tuple[int, int]]:
    """Each recorded gear mate's wanted tooth counts, in its own gear order: the plan's ``ratios`` entry where it
    lists one, else from its ``MeshLink`` (``meshes`` holds the counts now wanted: ``pitch`` = 360 / zb and
    ``|k|`` = za / zb, review M2). A link whose counts are not whole numbers is a fault, refused with a sentence."""
    asked = {name: (int(n), int(d)) for name, n, d in motion.ratios}
    out: Dict[str, Tuple[int, int]] = {}
    for mate in motion.mates:
        if mate.kind != "mesh" or len(mate.gears) != 2:
            continue
        if mate.name in asked:
            out[mate.name] = asked[mate.name]
            continue
        link = next((m for m in motion.meshes if (m.a, m.b) == tuple(mate.gears)), None)
        if link is None or not link.pitch:
            raise BuildError(f"Update SolidWorks was given the gear mate {mate.name} on record with no mesh between "
                             f"{mate.gears[0]} and {mate.gears[1]} to say the ratio the workbook wants, so the record "
                             "and the plan disagree about it and nothing is changed; that is a fault in Gear "
                             "Generator, not in SolidWorks.")
        zb = 360.0 / link.pitch
        za = abs(link.k) * zb
        if abs(zb - round(zb)) > 1e-6 or abs(za - round(za)) > 1e-6:
            raise BuildError(f"Update SolidWorks was given {mate.name} with tooth counts that are not whole numbers "
                             f"({za:g} : {zb:g}), so nothing is changed; that is a fault in Gear Generator, not in "
                             "SolidWorks.")
        out[mate.name] = (int(round(za)), int(round(zb)))
    return out


def _same_ratio(live: Tuple[float, float], wanted: Tuple[int, int]) -> bool:
    """Two ratios as proportions (a·d == b·c), to the read's precision."""
    return abs(live[0] * wanted[1] - live[1] * wanted[0]) <= 1e-6 * max(1.0, abs(live[1] * wanted[0]))


def _motion_consistent(motion: MotionUpdate, placements: Sequence[Placement]) -> None:
    """Every gear the motion record names has a placement, every lock and ratio its mate on record: anything else is
    a fault in the caller, refused with a sentence before anything is read."""
    placed = {p.gear for p in placements}
    named = [g for m in motion.mates for g in m.gears] + [g for m in motion.meshes for g in (m.a, m.b)] + \
        [g for lock in motion.locks for g in (lock.anchor, lock.follower)] + list(motion.fixed) + \
        [g for link in motion.carriers for g in (link.carrier,) + tuple(link.planets)] + list(motion.held)
    stray = [g for g in dict.fromkeys(named) if g not in placed]
    if stray:
        raise BuildError(f"Update SolidWorks was given a gearbox to turn whose record names {', '.join(stray)} without "
                         "a place for it, so nothing is changed; that is a fault in Gear Generator, not in SolidWorks.")
    splines = {tuple(sorted(m.gears)) for m in motion.mates if m.kind == "spline"}
    for lock in motion.locks:
        if _lock_mate_name(motion, lock) is None and tuple(sorted((lock.anchor, lock.follower))) not in splines:
            raise BuildError(f"Update SolidWorks was given {lock.follower} locked to {lock.anchor} with no lock mate on "
                             "record, so nothing is changed; that is a fault in Gear Generator, not in SolidWorks.")
    meshes = {m.name for m in motion.mates if m.kind == "mesh" and len(m.gears) == 2}
    for name, _, _ in motion.ratios:
        if name not in meshes:
            raise BuildError(f"Update SolidWorks was asked to give {name} a new ratio, which is not a gear mate on "
                             "record, so nothing is changed; that is a fault in Gear Generator, not in SolidWorks.")


def _lock_mate_name(motion: MotionUpdate, lock: LockLink) -> Optional[str]:
    return next((m.name for m in motion.mates if m.kind == "lock" and tuple(m.gears) == (lock.anchor, lock.follower)),
                None)


def _trains(mated: Sequence[str], meshes: Sequence[MeshLink], locks: Sequence[LockLink],
            carriers: Sequence[CarrierLink] = ()) -> List[Tuple[str, ...]]:
    """The mated gears grouped into trains — joined by meshes and locks, and (W7) a carrier to every gear on its
    planet shafts — each in ``mated``'s order, the trains in the order of their first gear. A gear joined to
    nothing is a train of its own. A held gear given in ``mated`` joins the trains the ``meshes`` touch, so the
    caller gives, for a held gear, only its gear-mated meshes (W7-PLAN §2.9)."""
    parent = {g: g for g in mated}

    def root(g: str) -> str:
        while parent[g] != g:
            g = parent[g]
        return g
    carried = [(link.carrier, planet) for link in carriers for planet in link.planets]
    for a, b in [(m.a, m.b) for m in meshes] + [(lock.anchor, lock.follower) for lock in locks] + carried:
        if a in parent and b in parent:
            parent[root(a)] = root(b)
    groups: Dict[str, List[str]] = {}
    for g in mated:
        groups.setdefault(root(g), []).append(g)
    return [tuple(group) for group in groups.values()]


def _moved(before: Optional[Frame9], after: Frame9) -> bool:
    """Whether a gear's origin moved between two frames (a turn about its own axis is not a move)."""
    return before is not None and any(abs(float(a) - float(b)) > POSE_TOLERANCE for a, b in zip(before[1], after[1]))


def _not_whole(turn: float, pitch: float) -> bool:
    return _off_whole(turn, math.radians(pitch or 0.0)) > TRAIN_TOLERANCE


# -- W8: Update SolidWorks across configurations (W8-PLAN §1.10)

# As MODES_FINDINGS: VALUE_READ_ORDER because the check phase reads every slide's value with dimension_values;
# CONFIGURATION_SHOW_OVER_DEFINED because a changed Update shows every mode, one of which may fight (a mate the user
# made is refused first only when it is on in a mode: _modes_unknown_mates). SUPPRESSION_READ_ORDER is no gate here
# either (one configuration per call).
MODES_UPDATE_FINDINGS = (("FEATURE_SUPPRESS", _SET), ("FEATURE_UNSUPPRESS", _SET), ("MATE_FIND_ROUTE", "mate group"),
                         ("CONFIGURATION_SHOW_RAISES_DIALOG", False), ("COLLINEAR_GEAR_MATE_SENSE_READ_BACK", True),
                         ("VALUE_READ_ORDER", "the order passed"),
                         ("CONFIGURATION_SHOW_OVER_DEFINED",
                          "shown; no window asks; its mates read in error; others solve after"))


@dataclass
class _ModesState:
    """What the check phase of an Update of a gearbox with modes found, for the change phase: each mode's
    configuration name in SolidWorks, the mode active, every flag and slide value to set (never one already right),
    and the per-mode mates off in the active configuration as the record has them."""

    names: Dict[str, str]
    active: str
    flags: List[Tuple[str, str, bool]] = field(default_factory=list)      # (mate, configuration, suppress)
    values: List[Tuple[str, str, float, bool]] = field(default_factory=list)   # (slide, configuration, mm, an edit)
    off_here: List[str] = field(default_factory=list)
    read: set = field(default_factory=set)                                   # gear mates whose sense was read


def _suppressed_readable() -> bool:
    """Whether a suppressed gear mate's sense may be read (``findings.SUPPRESSED_GEAR_MATE_SENSE_READ``: it answers
    and marks nothing). Until then a gear mate off in the configuration shown is read only in a mode that has it on."""
    return getattr(findings, "SUPPRESSED_GEAR_MATE_SENSE_READ", None) == "answers, marks nothing"


def _gear_mate_same(motion: MotionUpdate, mate: MateRef) -> bool:
    """Whether a recorded gear mate turns its two gears the same way about their own axes, as now wanted: a SPLINE
    always (§9.3); a COUPLE or a MESH by its ``MeshLink``'s ``k``. A coupling or mesh with no link is a fault in the
    record, refused with a sentence."""
    if mate.kind == "spline":
        return True
    link = next((m for m in motion.meshes if {m.a, m.b} == set(mate.gears)), None)
    if link is None:
        raise BuildError(f"Update SolidWorks was given the gear mate {mate.name} on record with no mesh between "
                         f"{mate.gears[0]} and {mate.gears[1]} to say which way it turns them, so nothing is changed; "
                         "that is a fault in Gear Generator, not in SolidWorks.")
    return link.k > 0


def _senses_readable() -> bool:
    """Whether a gear mate's sense may be read in an Update: the read-back settled and the check-phase findings
    (:data:`SENSE_CHECK_FINDINGS`), as W6's loop requires."""
    return _sense_settled() and _settled(SENSE_CHECK_FINDINGS) is None


GEAR_MATE_KINDS = ("mesh", "couple", "spline")


def _update_modes_gate(motion: Optional[MotionUpdate], revision: Sequence[int] = ()) -> None:
    """Before anything is read, for an Update of a gearbox with modes (``motion.configurations`` set): every finding
    its calls rest on settled (the configuration findings, the component find route, the flag actions, the mate
    walk, a show raising no window), and the running version shown to hold a slide's value per configuration
    (:func:`_modes_version_refusal`). A record that carries anything of modes without its configurations is a
    fault, refused, so it never goes down W7's path, which reads only the active configuration and turns on every
    recorded mate it finds suppressed (W8-INTERFACES §9.2)."""
    if motion is None:
        return
    carries = (motion.slide_values or motion.on_sets or motion.mode_placements or motion.recorded_by_mode
               or any(m.modes or m.values or m.kind in MODE_MATE_KINDS for m in motion.mates)
               or any(link.modes for link in tuple(motion.meshes) + tuple(motion.recorded_meshes))
               or any(link.modes for link in motion.locks))
    if not motion.configurations:
        if carries:
            raise BuildError("Update SolidWorks was given a gearbox with modes but not its configurations, so nothing "
                             "was read or changed; that is a fault in Gear Generator.")
        return
    for name, _ in CONFIGURATION_FINDINGS:
        problem = configuration_finding(name)
        if problem is not None:
            raise BuildError(f"Working with an assembly's configurations has not been settled on SolidWorks "
                             f"({problem}), so a gearbox with modes is not updated and nothing was read or changed.")
    route = getattr(findings, "COMPONENT_FIND_ROUTE", None)
    if route not in COMPONENT_FIND_ROUTES:
        raise BuildError(f"Finding a component again after a configuration change has not been settled on "
                         f"SolidWorks (findings.COMPONENT_FIND_ROUTE is {route!r}), so a gearbox with modes is not "
                         "updated and nothing was read or changed.")
    missing = _settled(MODES_UPDATE_FINDINGS)
    if missing is not None:
        raise BuildError(f"Update SolidWorks on a gearbox with modes needs findings.{missing[0]} settled on "
                         f"SolidWorks (it is {missing[1]!r}), so nothing was read or changed.")
    refusal = _modes_version_refusal(revision)
    if refusal is not None:
        raise BuildError(refusal.replace("is not built there and nothing is made",
                                         "is not updated there and nothing was read or changed")
                         .replace("is not built and nothing is made", "is not updated and nothing was read or changed"))


def _on_set(motion: MotionUpdate, mate: MateRef) -> Tuple[str, ...]:
    """The configurations a recorded mate is wanted on in: its J14 edit (``on_sets``) where there is one, else its
    record's ``modes``; ``()`` is every configuration (:func:`on_in`)."""
    edited = dict(motion.on_sets)
    return tuple(edited.get(mate.name, mate.modes))


def _slide_wanted(motion: MotionUpdate, mate: MateRef, mode: str) -> Optional[float]:
    """A SLIDE's wanted |z_front| in a mode: ``slide_values`` where it lists one, else the record's value there."""
    for name, configuration, value in motion.slide_values:
        if name == mate.name and on_in((configuration,), mode):
            return abs(float(value))
    recorded = dict(mate.values)
    for configuration, value in recorded.items():
        if on_in((configuration,), mode):
            return abs(float(value))
    return None


def _modes_check(sw: SolidWorks, assembly: str, motion: MotionUpdate, result: GearboxUpdate,
                 mate_handle: Mapping[str, str]) -> _ModesState:
    """The check phase's reads of a gearbox with modes, none of which shows a configuration (J25, §9.11): which
    configuration is active (one not a mode refuses, J13), each mode's configuration (one gone is
    ``ConfigurationGone``: Build again…), every recorded mate's flag in every mode (``mate_suppression``, which marks
    nothing) against the record's on-sets and J14's, and every SLIDE's value in every mode (``dimension_values``)
    against the record and J14's. Fills ``configuration``, ``extra_configurations`` and
    ``positions_per_configuration``."""
    file = _file(assembly)
    present = [str(c) for c in sw.configurations()]
    active = str(sw.active_configuration())
    names: Dict[str, str] = {}
    for mode in motion.configurations:
        found = next((c for c in present if on_in((mode,), c)), None)
        if found is None:
            raise ConfigurationGone(f"The configuration {mode} is not in {file} any more: it was renamed or deleted in "
                                    "SolidWorks.")
        names[mode] = found
    active_mode = next((mode for mode in motion.configurations if on_in((mode,), active)), None)
    if active_mode is None:
        modes = list(motion.configurations)
        listed = modes[0] if len(modes) == 1 else ", ".join(modes[:-1]) + f" and {modes[-1]}"
        raise BuildError(f"Update SolidWorks works in one of the gearbox's own configurations ({listed}), and "
                         f"{active} is active in SolidWorks: pick one of them and press Update SolidWorks again.")
    result.configuration = names[active_mode]
    result.extra_configurations = [c for c in present if c not in names.values()]
    result.positions_per_configuration = positions_per_configuration(sw.revision)
    state = _ModesState(names, active_mode)
    configs = [names[m] for m in motion.configurations]
    for mate in motion.mates:
        on_set = _on_set(motion, mate)
        if not on_in(on_set, active_mode):
            state.off_here.append(mate.name)
        read = sw.mate_suppression(mate_handle[mate.name], configs)
        for mode in motion.configurations:
            want_off = not on_in(on_set, mode)
            if bool(read.get(names[mode], want_off)) != want_off:
                state.flags.append((mate.name, names[mode], want_off))
    for mate in motion.mates:
        if mate.kind != "slide":
            continue
        read = sw.dimension_values(mate_handle[mate.name], configs)
        recorded = {c.casefold(): abs(float(v)) for c, v in mate.values}
        for mode in motion.configurations:
            wanted = _slide_wanted(motion, mate, mode)
            if wanted is None:
                raise BuildError(f"Update SolidWorks was given the slide {mate.name} with no value in {mode}, so "
                                 "nothing is changed; that is a fault in Gear Generator.")
            if abs(float(read.get(names[mode], 0.0)) - wanted) > SLIDE_READ_TOLERANCE:
                edit = abs(recorded.get(mode.casefold(), wanted) - wanted) > SLIDE_READ_TOLERANCE
                state.values.append((mate.name, names[mode], wanted, edit))
    return state


def _modes_unknown_mates(sw: SolidWorks, assembly: str, motion: MotionUpdate, result: GearboxUpdate,
                         state: _ModesState, unknown: Sequence[str]) -> None:
    """W8-PLAN J12 and §1.10, W5's M7 read in every mode's configuration: each mate in the assembly that is not on
    record found by name and its flag read in each mode's configuration, one configuration per call
    (``mate_suppression``, ``IsSuppressed2(3, [name])``, which marks nothing; no configuration shown). One on in any
    mode refuses the Update before anything is shown or changed, naming the mate and every mode it is on in; one
    suppressed in every mode's configuration is listed in ``extra_mates`` and left as it is. A configuration the
    record does not know (the template's ``Default``, a user's ``Exploded``) is no mode and is not read: a mate on
    only there does not refuse (J12: "an unsuppressed mate not on record in any MODE'S configuration refuses")."""
    file = _file(assembly)
    for index, name in enumerate(unknown, 1):
        handle = f"other{index}"
        sw.find_mate(handle, name)
        on_in_modes = []
        for mode in motion.configurations:
            configuration = state.names[mode]
            if not sw.mate_suppression(handle, [configuration])[configuration]:
                on_in_modes.append(mode)
        if on_in_modes:
            listed = on_in_modes[0] if len(on_in_modes) == 1 else \
                ", ".join(on_in_modes[:-1]) + f" and {on_in_modes[-1]}"
            where = f"In mode {listed}" if len(on_in_modes) == 1 else f"In modes {listed}"
            raise BuildError(f"{where}, {name} is a mate in {file} that Gear Generator did not make, and it may hold "
                             "the gears where Update SolidWorks would put them, so nothing is changed; in "
                             f"SolidWorks, suppress {name} in {listed} and press Update SolidWorks again.")
        result.extra_mates.append(name)


def _modes_senses(sw: SolidWorks, assembly: str, motion: MotionUpdate, state: _ModesState,
                  mate_handle: Mapping[str, str], axes: Mapping[str, Vec3], origins: Mapping[str, Vec3]) -> None:
    """Every coupling's and spline's sense read in the check phase (§1.10; §9.3: a SPLINE the same way, a COUPLE by
    its ``k``), when the read-back and the check-phase findings are settled (:func:`_senses_readable`). One off in
    the active configuration is read only while :func:`_suppressed_readable`; otherwise a mode shown with it on reads
    it (:func:`_modes_post_check`), and one never read is listed in ``senses_unread`` (W8-INTERFACES §9.16). One read
    wrong refuses the Update before anything changes: making a gear mate of a gearbox with modes again is not
    written yet."""
    if not _senses_readable():
        return
    for mate in motion.mates:
        if mate.kind not in ("couple", "spline") or len(mate.gears) != 2:
            continue
        same = _gear_mate_same(motion, mate)
        if mate.name in state.off_here and not _suppressed_readable():
            continue
        ga, gb = mate.gears
        state.read.add(mate.name)
        if not _sense_read(sw, mate_handle[mate.name], mate.name, same, axes[ga], axes[gb], ga, gb, BuildError,
                           (origins[ga], origins[gb])):
            raise BuildError(f"The gear mate {mate.name} in {_file(assembly)} turns its gears against each other, and "
                             "making a gear mate of a gearbox with modes again is not in this version of Gear "
                             "Generator, so nothing is changed; build the gearbox again.")


def _real_locks(motion: MotionUpdate, locks: Sequence[LockLink]) -> List[LockLink]:
    """The links of ``locks`` that are lock mates on record (a SPLINE is a ``LockLink`` but a gear mate, §9.3)."""
    return [lock for lock in locks if _lock_mate_name(motion, lock) is not None]


def _modes_assembly(sw: SolidWorks, result: GearboxUpdate, assembly: str, placements: Sequence[Placement],
                    motion: MotionUpdate, mated: Sequence[str], route: Optional[str],
                    axial: Sequence[Tuple[str, GlobalVariable]], say: Callable[[Step], None], touched: List[bool],
                    state: _ModesState) -> None:
    """The change phase of an Update of a gearbox with modes (W8-PLAN §1.10), in the build begun by
    :func:`_update_motion`.

    The values first (done by the caller); the assembly opened (it opens in the configuration last active) and
    rebuilt when a part or the layout changed. Then, without showing anything: D10 per configuration and J14's
    flags (``set_mate_suppressed_in`` for exactly the configurations found wrong, every flag read back; never a call
    on a mate already right), each SLIDE's value set back or set anew in its configuration (``set_dimension_in``,
    read back), each differing Face Z; one rebuild. Then the puts, one per mode with it shown, the active mode last:
    when anything changed, every mode is shown, rebuilt, its frames read through fresh handles and judged with its
    own links (:func:`links_in`); a train is put whole (its lock mates off in that configuration around the puts)
    when the workbook moved it or it is out of step there; fixed gears W4's way; a rebuild. Each mode shown is
    post-checked (frames, sliders at their values after the show, its mates on and off, gears free to turn) and its
    interference read, into a :class:`ModeCheck`. After the last mode, every per-mode mate's flag is read in every
    configuration and held against the record (:func:`_modes_flags_after`). With nothing to change, only the active
    mode is judged, from where it stands, and nothing is shown, unless something is to be put there: then it is a
    changed Update, every mode shown and every train put whole to its built frames, the active one last (J13, W5's
    answer 2, W8-INTERFACES §9.18). Whatever happens, the
    configuration that was active is shown again at the end; one that cannot be is said, naming the configuration
    left active."""
    file, stem = _file(assembly), _stem(assembly)
    sw.open_document(assembly)
    _note_opened(sw, assembly, result)
    handle: Dict[str, str] = {}
    for index, placement in enumerate(placements, 1):
        sw.find_component(f"placed{index}", placement.component)
        handle[placement.gear] = f"placed{index}"
    mate_handle: Dict[str, str] = {}
    for index, mate in enumerate(motion.mates, 1):
        sw.find_mate(f"mate{index}", mate.name)
        mate_handle[mate.name] = f"mate{index}"
    gear_of_handle = {h: g for g, h in handle.items()}
    names, active_mode = state.names, state.active
    active = names[active_mode]
    shown = [active]

    def rebuild() -> None:
        result.rebuilt = bool(sw.rebuild(kind=ASSEMBLY_TRAIN))
        if not result.rebuilt:
            raise SolidWorksError(f"SolidWorks reported an error rebuilding {stem} in {shown[0]}.")

    try:
        if result.changed:
            rebuild()
        grouped: Dict[Tuple[str, bool], List[str]] = {}
        for name, configuration, suppress in state.flags:
            grouped.setdefault((name, suppress), []).append(configuration)
        for (name, suppress), configurations in grouped.items():
            touched[0] = True
            sw.set_mate_suppressed_in(mate_handle[name], suppress, configurations)
            target = result.suppressed_in if suppress else result.unsuppressed_in
            target.extend((name, c) for c in configurations)
            if not suppress and active in configurations:
                result.unsuppressed.append(name)
        for name, configuration, value, edit in state.values:
            touched[0] = True
            sw.set_dimension_in(mate_handle[name], value, [configuration])
            if edit:
                result.slid.append((name, configuration, value))
            else:
                result.values_restored.append((name, configuration))
        for gear, variable in axial:
            touched[0] = True
            sw.set_global_variable(variable.name, variable.expression_for(DEGREES))
            result.axial.append(gear)
        fixes = bool(state.flags or state.values or axial)
        if fixes:
            rebuild()
        wanted_by = {mode: {p.gear: (p.rotation, p.at) for p in frames} for mode, frames in motion.mode_placements}
        recorded_by = {mode: {p.gear: (p.rotation, p.at) for p in frames} for mode, frames in motion.recorded_by_mode}
        base = {p.gear: (p.rotation, p.at) for p in placements}
        recorded = {p.gear: (p.rotation, p.at) for p in motion.recorded}

        def wanted_in(mode: str) -> Dict[str, Frame9]:
            return dict(base, **wanted_by.get(mode, {}))

        moved = bool(result.changed or axial or result.slid) or any(
            not same_frame(w[0], w[1], *recorded_by.get(mode, recorded).get(g, w)) for mode in motion.configurations
            for g, w in wanted_in(mode).items())
        found_here: Optional[ModeCheck] = None
        if not (moved or fixes):
            # Nothing the workbook or the record changes: only the active mode is judged, where it stands, and
            # nothing is shown (J25). Nothing to put there: done, nothing shown or marked. Something to put there
            # (W5's answer 2: Update returns a turned train to its built turn whenever it has to move any gear): from
            # here this is a changed Update (J13, §1.10) and is done as one, every mode shown and every train put
            # whole to its built frames, the active mode last, then every per-mode flag read in every configuration.
            # SolidWorks 2026 was seen (W8 s2, twice) to keep a put in the configuration it was made in while a turn
            # given before any put showed in the others, so a mode not put could be left turned and fail its
            # post-check against the built frames. Its judgement on showing is kept in its ModeCheck.
            found_here = ModeCheck(active_mode)
            if not _modes_put(sw, result, motion, active_mode, active, placements, mated, wanted_in(active_mode),
                              handle, mate_handle, route, rebuild, file, touched, moved=False, check=found_here,
                              judge_only=True):
                return
            moved = True
        order = [m for m in motion.configurations if m != active_mode] + [active_mode]
        for index, mode in enumerate(order, 1):
            say(Step(STAGE_MODE, mode, index, len(order)))
            sw.show_configuration(names[mode])
            shown[0] = names[mode]
            rebuild()
            judged = found_here is not None and mode == active_mode      # already judged where it stood
            check = found_here if judged else ModeCheck(mode)
            result.modes.append(check)
            if mode != active_mode:
                result.visited.append(names[mode])
            _modes_put(sw, result, motion, mode, names[mode], placements, mated, wanted_in(mode), handle,
                       mate_handle, route, rebuild, file, touched, moved=moved, check=None if judged else check,
                       put_turned=True)
            _modes_post_check(sw, result, motion, mode, names[mode], placements, mated, wanted_in(mode), handle,
                              mate_handle, gear_of_handle, check, file, state.read)
            if getattr(findings, "INTERFERENCE_CHECKED", False):
                gear_of = {p.component: p.gear for p in placements}
                try:
                    check.clashes = _clashes(sw.interferences(), gear_of)
                except Exception as exc:  # noqa: BLE001 - a clash check that cannot run is a CHECK, never a failure
                    check.interference_error = _said(exc)
        _modes_flags_after(sw, result, motion, names, mate_handle, file)
        if result.modes:
            result.clashes = list(result.modes[-1].clashes)
            result.interference_error = result.modes[-1].interference_error
    finally:
        # Which configuration is active is read, never assumed from the last show asked for: a show whose read-back
        # raised may still have switched.
        try:
            now = str(sw.active_configuration())
        except Exception:  # noqa: BLE001 - unread: show the one that was active again all the same
            now = ""
        if not on_in((active,), now):
            try:
                sw.show_configuration(active)
                sw.rebuild(kind=ASSEMBLY_TRAIN)
            except Exception as exc:  # noqa: BLE001 - said: which configuration is left active
                try:
                    left = str(sw.active_configuration())
                except Exception:  # noqa: BLE001
                    left = now or "another configuration"
                result.failures.append((file, f"Update SolidWorks could not show {active} again, so {left} is left "
                                              f"active in SolidWorks ({_said(exc)})"))
        placed = list(dict.fromkeys(result.placed))
        result.placed[:] = placed


def _modes_flags_after(sw: SolidWorks, result: GearboxUpdate, motion: MotionUpdate, names: Mapping[str, str],
                       mate_handle: Mapping[str, str], file: str) -> None:
    """Once every mode is put and post-checked: every per-mode mate's flag (record's ``modes`` or a J14 on-set) read
    in every configuration (``mate_suppression``, one ``IsSuppressed2(3, [name])`` per configuration, which marks
    nothing) and held against what the record wants (:func:`_on_set`). Each mode's post-check reads only the
    configuration shown, so a flag a later mode's put changed in a mode already checked would otherwise go unseen
    (W8-REVIEW-LATE-A point 1). A difference is the post-check's own failure, *"In mode 2H, the mate … is on in
    SolidWorks, where this mode has it off."*, said once."""
    configurations = [names[mode] for mode in motion.configurations]
    edited = dict(motion.on_sets)
    for mate in motion.mates:
        if not (mate.modes or mate.name in edited):
            continue
        on_set = _on_set(motion, mate)
        read = sw.mate_suppression(mate_handle[mate.name], configurations)
        for mode in motion.configurations:
            on, off_read = on_in(on_set, mode), bool(read[names[mode]])
            if on and off_read:
                problem = f"The mate {mate.name} is suppressed in SolidWorks, where this mode has it on."
            elif not on and not off_read:
                problem = f"The mate {mate.name} is on in SolidWorks, where this mode has it off."
            else:
                continue
            failure = (file, _in_mode(mode, problem))
            if failure not in result.failures:
                result.failures.append(failure)


def _modes_put(sw: SolidWorks, result: GearboxUpdate, motion: MotionUpdate, mode: str, configuration: str,
               placements: Sequence[Placement], mated: Sequence[str], wanted: Mapping[str, Frame9],
               handle: Mapping[str, str], mate_handle: Mapping[str, str], route: Optional[str],
               rebuild: Callable[[], None], file: str, touched: List[bool], *, moved: bool,
               check: Optional[ModeCheck], judge_only: bool = False, put_turned: bool = False) -> bool:
    """One mode's puts, with it shown (or, on a quiet Update, the active one judged where it stands): every frame
    read through fresh handles; the trains — joined over EVERY mode's relations, so the same set is right if
    positions turn out shared (§1.9, J26) — each judged with this mode's links; one put whole when the workbook
    ``moved`` it or it is out of step here, its lock mates off in this configuration around the puts; fixed gears
    W4's way; a rebuild after. The judgement found on showing is the ``check``'s ``off_axis``, ``out_of_step`` and
    ``turned`` (§9.14). Returns whether anything was put; with ``judge_only``, whether anything would be, and
    nothing is put or rebuilt. ``put_turned`` (every mode an Update shows, W8-INTERFACES §9.18): a train found turned
    in step is put whole too, so the mode ends at its built frames whatever SolidWorks kept there (W5's answer 2:
    an Update that changes the assembly returns a turned train to its built turn); a quiet Update's judgement of the
    active mode leaves it out, so a turn in step there stays where it stands."""
    live = {p.gear: sw.component_frame(handle[p.gear]) for p in placements}
    pitch = {p.gear: p.pitch for p in placements}
    held = [g for g in motion.held if g in wanted]
    judged = list(mated) + [g for g in held if g not in mated]
    meshes_here = links_in(motion.meshes, mode)
    locks_here = links_in(motion.locks, mode)
    put_any = False
    for train in _trains(judged, motion.meshes, motion.locks, motion.carriers):
        meshes = [m for m in meshes_here if m.a in train and m.b in train]
        locks = [lock for lock in locks_here if lock.anchor in train and lock.follower in train]
        links = [link for link in motion.carriers if link.carrier in train]
        held_here = [g for g in held if g in train]
        try:
            here = train_check({g: live[g] for g in train}, {g: wanted[g] for g in train}, meshes, locks, pitch,
                               carriers=links, held=held_here)
        except ValueError as exc:
            raise SolidWorksError(f"Update SolidWorks cannot judge the gears on record: {exc} That is a fault in "
                                  "Gear Generator.") from None
        if check is not None:
            check.off_axis.extend(here.off_axis)
            check.out_of_step.extend(here.out_of_step)
            check.turned = check.turned or here.turned
        lone = not (meshes or locks or links)
        needed = moved or (bool(here.off_axis) if lone else (not here.in_step or (put_turned and here.turned)))
        if not needed:
            continue
        if judge_only:
            put_any = True
            continue
        lock_mates = _real_locks(motion, [lock for lock in locks_here
                                          if lock.anchor in train and lock.follower in train])
        on_here = [m.name for m in motion.mates if m.kind in GEAR_MATE_KINDS and on_in(_on_set(motion, m), mode)]
        _put_train(sw, result, motion, train, lock_mates, [], handle, mate_handle, wanted, rebuild, file, touched,
                   held=held_here, carriers=[link.carrier for link in links], live=live, pitch=pitch, route=route,
                   gear_mates=on_here, configuration=configuration)
        put_any = True
    unfix = route == REPLACE_ROUTES[1]
    for placement in placements:
        gear = placement.gear
        if gear in mated or gear not in wanted or same_frame(live[gear][0], live[gear][1], wanted[gear][0],
                                                             wanted[gear][1], placement.pitch):
            continue
        if judge_only:
            put_any = True
            continue
        touched[0] = True
        if unfix:
            sw.unfix_component(handle[gear])
        sw.place_component(handle[gear], wanted[gear][0], wanted[gear][1], kind=ASSEMBLY_TRAIN)
        result.placed.append(gear)
        if unfix:
            sw.fix_component(handle[gear])
        put_any = True
    if judge_only:
        return put_any
    if put_any:
        rebuild()
        result.put_in.append(configuration)
    return put_any


def _modes_post_check(sw: SolidWorks, result: GearboxUpdate, motion: MotionUpdate, mode: str, configuration: str,
                      placements: Sequence[Placement], mated: Sequence[str], wanted: Mapping[str, Frame9],
                      handle: Mapping[str, str], mate_handle: Mapping[str, str],
                      gear_of_handle: Mapping[str, str], check: ModeCheck, file: str,
                      state_read: Optional[set] = None) -> None:
    """A mode shown, post-checked through fresh handles: every gear's origin where this mode wants it (a slider
    read back after the show, so a put on a slider that its slide does not take back is said, as SolidWorks has not
    shown what it does), each train in step with this mode's links, every recorded mate on here present,
    unsuppressed and without error and every one off here suppressed, every mated gear free to turn; each problem a
    failure beginning *"In mode 4L, …"*. Fills ``check``'s mates, flags and slide values."""
    after = {p.gear: sw.component_frame(handle[p.gear]) for p in placements}
    problems: List[str] = []
    for gear, (rotation, at) in wanted.items():
        if gear in after and any(abs(float(a) - float(b)) > POSE_TOLERANCE for a, b in zip(after[gear][1], at)):
            problems.append(f"{gear} stands at {_vector(after[gear][1])} once the assembly rebuilt, where this mode "
                            f"places it at {_vector(at)}.")
    pitch = {p.gear: p.pitch for p in placements}
    meshes_here, locks_here = links_in(motion.meshes, mode), links_in(motion.locks, mode)
    for train in _trains(list(mated), motion.meshes, motion.locks, motion.carriers):
        try:
            again = train_check({g: after[g] for g in train}, {g: wanted[g] for g in train},
                                [m for m in meshes_here if m.a in train and m.b in train],
                                [lock for lock in locks_here if lock.anchor in train and lock.follower in train],
                                pitch, carriers=[link for link in motion.carriers if link.carrier in train])
        except ValueError:
            continue
        problems += [f"{a} and {b} are out of step once the assembly rebuilt." for a, b in again.out_of_step]
    check.mates = list(sw.mate_states())
    by_name = {s.name: s for s in check.mates}
    for mate in motion.mates:
        on = on_in(_on_set(motion, mate), mode)
        state = by_name.get(mate.name)
        if mate.modes or mate.name in dict(motion.on_sets):
            check.suppressed[mate.name] = bool(state.suppressed) if state is not None else True
        if state is None:
            problems.append(f"The mate {mate.name} is missing from the assembly.")
        elif on and state.suppressed:
            problems.append(f"The mate {mate.name} is suppressed in SolidWorks, where this mode has it on.")
        elif not on and not state.suppressed:
            problems.append(f"The mate {mate.name} is on in SolidWorks, where this mode has it off.")
        elif on and state.code and not state.warning:
            problems.append(f"The mate {mate.name} is in error in SolidWorks.")
    for mate in motion.mates:
        if mate.kind == "slide":
            check.values[mate.name] = sw.dimension_values(mate_handle[mate.name], [configuration])[configuration]
    problems += _free_to_turn(sw, [handle[g] for g in mated], lambda h: gear_of_handle.get(h, h))
    # W8-INTERFACES §9.16: every gear mate on in this mode read for sense, through fresh handles; a wrong one is a
    # problem naming it and the mode, never a remake (remaking a gear mate of a gearbox with modes is refused).
    if _senses_readable():
        frames = {p.gear: (p.rotation, wanted.get(p.gear, (p.rotation, p.at))[1]) for p in placements}
        for mate in motion.mates:
            if mate.kind not in GEAR_MATE_KINDS or len(mate.gears) != 2 or not on_in(_on_set(motion, mate), mode):
                continue
            ga, gb = mate.gears
            axis_a, axis_b = _axis_of(frames[ga][0]), _axis_of(frames[gb][0])
            try:
                right = _sense_read(sw, mate_handle[mate.name], mate.name, _gear_mate_same(motion, mate), axis_a,
                                    axis_b, ga, gb, SolidWorksError, (frames[ga][1], frames[gb][1]))
            except SolidWorksError as exc:
                problems.append(str(exc))
                continue
            if state_read is not None:
                state_read.add(mate.name)
            if not right:
                problems.append(f"The gear mate {mate.name} turns its gears against the way they mesh.")
    for problem in problems:
        result.failures.append((file, _in_mode(mode, problem)))


def _update_motion(sw: SolidWorks, parts: Sequence[DocumentValues], layout: Optional[DocumentValues], assembly: str,
                   placements: Sequence[Placement], motion: MotionUpdate, exists: Callable[[str], bool],
                   progress: Optional[Callable[[Step], None]], mtime: Callable[[str], float],
                   lines: Optional[Mapping[str, Tuple[Vec3, Vec3]]] = None, *,
                   carriers: Sequence[DocumentValues] = ()) -> GearboxUpdate:
    """:func:`update_gearbox` for a gearbox built to turn, in W5-INTERFACES §3's order.

    *Check — writes nothing; a raise here changes nothing:* W4's checks
    (paths, same-named documents, one component per gear, each part and
    the layout read live); the train's gates (:func:`_assembly_rebuild_gate`,
    :func:`_train_gate`, :func:`_motion_gate`); then the assembly opened,
    each placement's component found and its frame read (``found``), each
    mate on record found by name (``MateGone`` → :class:`NotAsBuilt`), every
    mate read — one the record does not know that is not suppressed refuses
    the Update naming it (review M7), a suppressed one is listed in
    ``extra_mates`` — and each ``"<Gear> Face Z"`` read from the assembly's
    equations (gone → :class:`NotAsBuilt`). ``train_check`` of ``found``
    against the record, both restricted to the mated gears, gives
    ``turned``, ``out_of_step``, ``off_axis`` and ``residuals``.

    *Change — nothing raises out (W4 review B1):* the values (W4); the
    assembly opened, and rebuilt (as a train) when a part or the layout
    changed; recorded mates found suppressed turned back on (D10) and each
    differing Face Z set, then one rebuild when either did, before any put;
    every frame read; a train needing a put (a gear off its axis, a relation
    out of step, or a ratio to set, against ``placements``) has every lock
    suppressed, a rebuild, its ratios remade, EVERY mated gear put (review
    M1), and its locks turned back on whatever happened (review M8: one that
    will not come back on is a failure naming the compound gears), then a
    rebuild; a lone mated gear is put only when off its axis; fixed gears
    W4's way. With nothing to put the train stays where the user turned it
    (D4). Then, when anything changed, the post-check (each put gear where
    it was put, each train put in step, every mate on record present,
    unsuppressed and in no error, every mated gear free to turn: each
    problem a failure sentence) and interference (W4).
    """
    say = progress or _quiet
    _gate(sw)
    result = GearboxUpdate()
    documents = list(parts) + ([layout] if layout is not None else []) + list(carriers)
    if not assembly:
        raise BuildError("A gearbox built to turn is updated through its assembly, and Update SolidWorks was given "
                         "none.")
    paths = [d.path for d in documents] + [assembly]
    _assembly_rebuild_gate(ASSEMBLY_TRAIN)
    _train_gate()
    _motion_gate(motion)
    put_route = getattr(findings, "PLANETARY_PUT_ROUTE", None)
    if motion.carriers and put_route != PLANETARY_PUT_ROUTE:
        raise BuildError(f"Putting a turned planetary stage back has not been settled on SolidWorks (findings."
                         f"PLANETARY_PUT_ROUTE is {put_route!r}), so nothing is changed; run probe planetary_put_back "
                         "first.")
    for path in paths:
        if not exists(path):
            raise BuildError(f"{path} is no longer there, so Update SolidWorks cannot change it: it was moved, "
                             "renamed or deleted since it was built.")
    result.open_before = list(_refuse_paths(sw, [], paths, "make", "change"))
    for index, placement in enumerate(placements):
        for earlier in placements[:index]:
            if placement.component == earlier.component:
                raise BuildError(f"{placement.component} is recorded for both {earlier.gear} and {placement.gear}, "
                                 "so one of them would be placed twice.")
    _motion_consistent(motion, placements)
    axes = {p.gear: _axis_of(p.rotation) for p in placements}
    origins = {p.gear: tuple(float(v) for v in p.at) for p in placements}
    _turned_update_gate(motion, axes, origins)
    fixed = set(motion.fixed)
    route = getattr(findings, "REPLACE_FIXED_ROUTE", None)
    if fixed and route not in REPLACE_ROUTES:
        raise BuildError(f"Moving a fixed component has not been settled on SolidWorks yet "
                         f"(findings.REPLACE_FIXED_ROUTE is {route!r}), so Update SolidWorks cannot re-place the "
                         "gears; run probe tier 7 first.")
    if documents and getattr(findings, "OPEN_PART_BESIDE_ASSEMBLY", None) is not True:
        raise BuildError(f"Update SolidWorks reads {_file(assembly)} before it changes anything, and changing a part "
                         "while its assembly is open has not been settled on this SolidWorks "
                         "(findings.OPEN_PART_BESIDE_ASSEMBLY), so nothing is changed.")
    for path in paths:
        try:
            result.mtimes[path] = float(mtime(path))
        except (OSError, ValueError, TypeError):
            pass

    # -- check: opens and reads, writes nothing
    total = len(paths)
    holds: List[str] = []
    for index, doc in enumerate(documents, 1):
        say(Step(STAGE_CHECK, _stem(doc.path), index, total))
        _, by_unit, values = _read_live(sw, doc, "updated", lambda path: _note_opened(sw, path, result),
                                        lines=lines if doc is layout else None)
        holds.append(_held_unit(by_unit, values, doc.variables))
    say(Step(STAGE_CHECK, _stem(assembly), total, total))
    recorded_names = {m.name for m in motion.mates}
    wanted_teeth = _wanted_teeth(motion)
    senses = _mesh_senses(motion)
    resensed = _resensed(motion)                     # gear mates the plan turns the other way: each remade
    respaced: set = set()                            # gear mates found live at another ratio than wanted
    remakes: List[Tuple[str, int, int]] = []         # gear mates found live at another ratio than wanted
    sense_wrong = set()                              # gear mates read turning against their mesh, to be remade
    deferred: List[str] = []                         # recorded gear mates found suppressed: read once turned on
    suppressed: List[str] = []                       # recorded mates found suppressed: turned back on (D10)
    axial: List[Tuple[str, GlobalVariable]] = []     # Face Z globals the assembly holds otherwise
    sw.begin_build()
    try:
        sw.open_document(assembly)
        _note_opened(sw, assembly, result)
        # Lightweight gears (a user whose SolidWorks loads assemblies lightweight). Probe round P0d: every gear of a
        # train opened lightweight read 1; the first drive turned one gear -24.17° where 2.5° is right, and afterwards
        # every gear read 2; the remake and the drive after it ran resolved and were right. So with the read settled
        # each gear is read and one that is not fully resolved refuses the Update here. Without the finding,
        # find_component's own check stands.
        resolving = getattr(findings, RESOLVED_ROUTE_FINDING, None) is not None
        for index, placement in enumerate(placements, 1):
            if resolving:
                sw.find_component(f"placed{index}", placement.component, lightweight_ok=True)
            else:
                sw.find_component(f"placed{index}", placement.component)
        if resolving:
            for index, placement in enumerate(placements, 1):
                if not sw.component_resolved(f"placed{index}"):
                    raise BuildError(f"{placement.gear} ({placement.component}) is not fully resolved in "
                                     f"{_file(assembly)}: SolidWorks loaded it lightweight, and a train with a "
                                     "lightweight gear does not turn as it was built, so nothing is changed; in "
                                     f"SolidWorks, right-click {_file(assembly)} and choose Set Lightweight to "
                                     "Resolved, then press Update SolidWorks again.")
        for index, placement in enumerate(placements, 1):
            rotation, at = sw.component_frame(f"placed{index}")
            result.found[placement.gear] = (tuple(rotation), tuple(at))
        for index, mate in enumerate(motion.mates, 1):
            sw.find_mate(f"mate{index}", mate.name)
        others: List[str] = []
        result.mates = list(sw.mate_states(others=others))
        if others:
            listed = ", ".join(f'"{name}"' for name in others)
            one = len(others) == 1
            raise BuildError(f"{_file(assembly)} holds {listed} among its mates, which {'is' if one else 'are'} not "
                             f"{'a mate' if one else 'mates'}, and how Update SolidWorks would read "
                             f"{'it' if one else 'them'} (a folder of mates, say) has not been settled, so nothing is "
                             f"changed; move the mates out of {listed} in SolidWorks (or delete "
                             f"{'it' if one else 'them'} if empty) and press Update SolidWorks again.")
        unknown: List[str] = []                          # W8: mates not on record, judged in every mode below
        for state in result.mates:
            if state.name in recorded_names:
                if state.suppressed:
                    suppressed.append(state.name)
            elif motion.configurations:
                unknown.append(state.name)
            elif not state.suppressed:
                raise BuildError(f"{state.name} is a mate in {_file(assembly)} that Gear Generator did not make, and "
                                 "it may hold the gears where Update SolidWorks would put them, so nothing is "
                                 f"changed; suppress {state.name} in SolidWorks and press Update SolidWorks again.")
            else:
                result.extra_mates.append(state.name)
        modes_state: Optional[_ModesState] = None
        if motion.configurations:
            # W8: every flag and slide value read in every mode, no configuration shown; D10 is per configuration
            # there, so W5's this-configuration D10 list is not used (a per-mode mate off here is right off).
            modes_state = _modes_check(sw, assembly, motion, result,
                                       {m.name: f"mate{i}" for i, m in enumerate(motion.mates, 1)})
            _modes_unknown_mates(sw, assembly, motion, result, modes_state, unknown)
            suppressed.clear()
        # Every recorded gear mate judged live, as the frames are (a remake lost with an unsaved close leaves the
        # old ratio in SolidWorks whatever the record says).
        asked = {name for name, _, _ in motion.ratios}
        ratio_route = getattr(findings, "GEAR_MATE_RATIO_ROUTE", None)
        for index, mate in enumerate(motion.mates, 1):
            if mate.name not in wanted_teeth:
                continue
            live = tuple(float(n) for n in sw.gear_mate_ratio(f"mate{index}"))
            want = wanted_teeth[mate.name]
            read = (mate.name, int(round(live[0])), int(round(live[1])), want[0], want[1])
            same = _same_ratio(live, want)
            if same and mate.name not in resensed:
                if mate.name in asked:
                    result.ratios_already.append(mate.name)
                    result.ratios_read.append(read)
                continue
            if same and ratio_route != "remake":
                raise BuildError(f"The gear mate {mate.name} in {_file(assembly)} must be made again, since the "
                                 "workbook now has it turn its gears the other way about their axes, and making a "
                                 "gear mate again has not been settled on SolidWorks (findings.GEAR_MATE_RATIO_ROUTE "
                                 f"is {ratio_route!r}), so nothing is changed; build the gearbox again.")
            if ratio_route != "remake":
                raise BuildError(f"The gear mate {mate.name} in {_file(assembly)} is at {live[0]:g} : {live[1]:g} "
                                 f"and the workbook wants {want[0]} : {want[1]}, and giving a gear mate a new ratio "
                                 "has not been settled on SolidWorks (findings.GEAR_MATE_RATIO_ROUTE is "
                                 f"{ratio_route!r}), so nothing is changed; build the gearbox again.")
            remakes.append((mate.name, want[0], want[1]))
            if not same:
                respaced.add(mate.name)
                result.ratios_read.append(read)
                if mate.name not in asked:
                    result.ratios_found.append(mate.name)
        # Which way each recorded gear mate turns, read before anything changes (SENSE_CHECK_FINDINGS; without
        # them the sense is not read here, as before).
        # A gear mate found suppressed is never read here (no probe read Reverse or its axes on a suppressed mate):
        # it is read once D10 has turned it back on and the assembly has rebuilt (``deferred``, in the change
        # phase; GEAR_MATE_SENSE_READ_POINTS_AGREE covers a read after a rebuild). A gear mate the plan turns the
        # other way (``resensed``) is not read here: it is remade whatever it reads, and read back against its new
        # ``k`` once remade, so it is never said to have been found turning wrong (W6-PLAN §2.7).
        if _sense_settled() and _settled(SENSE_CHECK_FINDINGS) is None:
            for index, mate in enumerate(motion.mates, 1):
                if mate.name not in wanted_teeth or mate.name in resensed:
                    continue
                if modes_state is not None and mate.name in modes_state.off_here and not _suppressed_readable():
                    continue                          # a sliding mesh off in this mode: read when a mode shows it on
                if mate.name in suppressed:
                    deferred.append(mate.name)
                    continue
                ga, gb = mate.gears
                if modes_state is not None:
                    modes_state.read.add(mate.name)
                if not _sense_read(sw, f"mate{index}", mate.name, senses.get(mate.name, False), axes[ga], axes[gb],
                                   ga, gb, BuildError, (origins[ga], origins[gb])):
                    if ratio_route != "remake":
                        raise BuildError(f"The gear mate {mate.name} in {_file(assembly)} turns its gears against the "
                                         "way they mesh, and making a gear mate again has not been settled on "
                                         "SolidWorks (findings.GEAR_MATE_RATIO_ROUTE is "
                                         f"{ratio_route!r}), so nothing is "
                                         "changed; build the gearbox again.")
                    sense_wrong.add(mate.name)
                    # At the wanted ratio but turning wrong (an Update stopped after a remake that read wrong either
                    # way round, and the open assembly kept): not "already there" — it is remade.
                    if mate.name in result.ratios_already:
                        result.ratios_already.remove(mate.name)
                    if all(name != mate.name for name, _, _ in remakes):
                        remakes.append((mate.name, *wanted_teeth[mate.name]))
        # A gear mate found suppressed may turn wrong once it is turned back on, and then it is remade in the change
        # phase. So every one of them counts here as a possible remake (conservative): the route and the remake's
        # gates are read now, before anything changes, and none of them can refuse after a change.
        if deferred and ratio_route != "remake":
            name = deferred[0]
            raise BuildError(f"The gear mate {name} in {_file(assembly)} is suppressed, so which way it turns can be "
                             "read only once Update SolidWorks has turned it back on, and making it again should it "
                             "turn against the way its gears mesh has not been settled on SolidWorks "
                             f"(findings.GEAR_MATE_RATIO_ROUTE is {ratio_route!r}), so nothing is changed; unsuppress "
                             f"{name} in SolidWorks and press Update SolidWorks again.")
        if modes_state is not None:
            for mate in motion.mates:
                if mate.kind in GEAR_MATE_KINDS and mate.kind != "mesh" and len(mate.gears) == 2:
                    _gear_mate_same(motion, mate)          # a coupling with no link is a fault, refused now
            _modes_senses(sw, assembly, motion, modes_state,
                          {m.name: f"mate{i}" for i, m in enumerate(motion.mates, 1)}, axes, origins)
            if remakes or deferred or resensed:
                name = (remakes[0][0] if remakes else deferred[0] if deferred else resensed[0])
                raise BuildError(f"The gear mate {name} in {_file(assembly)} would have to be made again, and making a "
                                 "gear mate of a gearbox with modes again is not in this version of Gear Generator, "
                                 "so nothing is changed; build the gearbox again.")
        possible = list(remakes) + [(name, *wanted_teeth[name]) for name in deferred
                                    if all(n != name for n, _, _ in remakes)]
        if possible:
            _remake_gate()
            _idler_gate(motion, possible)
            _remake_sense_gate(possible, senses, motion, axes)
        held = _held(sw.equations()) if motion.face_globals else {}
        for gear, variable in motion.face_globals:
            if variable.name not in held:
                raise NotAsBuilt(f'{_file(assembly)} cannot be updated: "{variable.name}" is no longer in it, so its '
                                 "equations were edited in SolidWorks.", assembly)
            if _squash(held[variable.name]) != _squash(variable.expression_for(DEGREES)):
                axial.append((gear, variable))
    except ComponentGone as exc:      # a component or a mate renamed or deleted: only a new revision puts it back
        raise NotAsBuilt(str(exc), assembly) from None
    except BuildError:
        raise
    except SolidWorksError as exc:
        raise BuildError(str(exc)) from None
    finally:
        sw.end_build()
    mated = [p.gear for p in placements if p.gear not in fixed]
    # W7: the held gears a recorded gear mate touches are judged with the trains (review M1), and each carrier's
    # planets against their carried frames (train_check's carriers).
    judged = mated + [g for g in motion.held if g not in mated]
    recorded = {p.gear: p for p in motion.recorded}
    found = {g: result.found[g] for g in judged if g in result.found}
    recorded_meshes, recorded_locks = motion.recorded_meshes, motion.locks
    if modes_state is not None:                       # W8: the active mode's frames on record and links (links_in)
        recorded = dict(recorded, **{p.gear: p for mode, frames in motion.recorded_by_mode
                                     if on_in((mode,), modes_state.active) for p in frames})
        recorded_meshes = links_in(motion.recorded_meshes, modes_state.active)
        recorded_locks = links_in(motion.locks, modes_state.active)
    try:
        check = train_check(found, {g: (recorded[g].rotation, recorded[g].at) for g in judged if g in recorded},
                            recorded_meshes, recorded_locks, {g: p.pitch for g, p in recorded.items()},
                            carriers=motion.carriers, held=motion.held)
    except ValueError as exc:                         # W7-INTERFACES §6.3: a record that cannot be judged
        raise BuildError(f"Update SolidWorks cannot judge the gears on record: {exc} So nothing is changed; that is "
                         "a fault in Gear Generator.") from None
    result.turned, result.off_axis = check.turned, list(check.off_axis)
    result.out_of_step, result.residuals = list(check.out_of_step), list(check.residuals)
    turned_back: Dict[str, bool] = {}                # per mated gear: its check-phase turn was not whole teeth
    for gear in mated:
        if gear in found and gear in recorded:
            turn = turn_between(recorded[gear].rotation, found[gear][0])
            turned_back[gear] = turn is not None and _not_whole(turn, recorded[gear].pitch)
    for doc, unit in zip(documents, holds):
        if not unit:
            _evaluates(sw, doc, "updated")

    # -- change: nothing raises out from here (B1)
    stage = [_file(documents[0].path) if documents else _file(assembly)]
    touched = [False]        # a change was asked of the assembly (it is then marked modified, even if the call failed)
    try:
        if not _update_values(sw, result, parts, layout, documents, holds, assembly, say, stage):
            stage[0] = _file(assembly)
            say(Step(STAGE_PLACE, _stem(assembly)))
            sw.begin_build()
            try:
                if modes_state is not None:
                    _modes_assembly(sw, result, assembly, placements, motion, mated, route, axial, say, touched,
                                    modes_state)
                else:
                    _motion_assembly(sw, result, assembly, placements, motion, mated, route, suppressed, axial,
                                     turned_back, say, touched, remakes, sense_wrong=sense_wrong, deferred=deferred,
                                     wanted_teeth=wanted_teeth, resensed=resensed, respaced=respaced)
            finally:
                sw.end_build()
    except _LocksLeftOff:
        pass                                      # its failure, naming the compound gears, is on the result already
    except Exception as exc:  # noqa: BLE001 - see above
        result.failures.append((stage[0], _said(exc)))
        if not result.skipped and stage[0] != _file(assembly):
            result.skipped = f"the assembly, because the job stopped during {stage[0]}"
    finally:
        if (touched[0] or result.unsuppressed or result.axial or result.placed or result.ratios
                or result.unsuppressed_in or result.suppressed_in or result.slid or result.values_restored) \
                and assembly not in result.changed:
            result.changed.append(assembly)
        if modes_state is not None:          # W8-INTERFACES §9.16: what no read reached, for C to say
            result.senses_unread = [m.name for m in motion.mates
                                    if m.kind in GEAR_MATE_KINDS and m.name not in modes_state.read]
    return result


class _LocksLeftOff(Exception):
    """A train's locks would not all come back on (review M8): the failure is on the result already; the job stops."""


def _motion_assembly(sw: SolidWorks, result: GearboxUpdate, assembly: str, placements: Sequence[Placement],
                     motion: MotionUpdate, mated: Sequence[str], route: Optional[str], suppressed: Sequence[str],
                     axial: Sequence[Tuple[str, GlobalVariable]], turned_back: Mapping[str, bool],
                     say: Callable[[Step], None], touched: List[bool],
                     remakes: Sequence[Tuple[str, int, int]] = (), *, sense_wrong: Optional[set] = None,
                     deferred: Sequence[str] = (),
                     wanted_teeth: Optional[Mapping[str, Tuple[int, int]]] = None,
                     resensed: Collection[str] = (), respaced: Collection[str] = ()) -> None:
    """Steps 2-7 of the motion path's change phase, in the build begun by :func:`_update_motion`. ``sense_wrong``:
    gear mates read turning against their mesh (remade; listed in ``sense_found_wrong`` once remade, and in
    ``ratios`` only when the plan asked their ratio changed). ``deferred``: gear mates found suppressed, whose sense
    is read here once D10 has turned them back on and the assembly has rebuilt."""
    remakes = list(remakes)
    sense_wrong = set(sense_wrong or ())
    file, stem = _file(assembly), _stem(assembly)
    sw.open_document(assembly)
    _note_opened(sw, assembly, result)
    handle: Dict[str, str] = {}
    for index, placement in enumerate(placements, 1):
        sw.find_component(f"placed{index}", placement.component)
        handle[placement.gear] = f"placed{index}"
    mate_handle: Dict[str, str] = {}
    for index, mate in enumerate(motion.mates, 1):
        sw.find_mate(f"mate{index}", mate.name)
        mate_handle[mate.name] = f"mate{index}"
    gear_of_handle = {h: g for g, h in handle.items()}
    axes = {p.gear: _axis_of(p.rotation) for p in placements}
    origins = {p.gear: tuple(float(v) for v in p.at) for p in placements}
    senses = _mesh_senses(motion)

    def read(name: str) -> bool:
        ga, gb = next(m.gears for m in motion.mates if m.name == name)
        return _sense_read(sw, mate_handle[name], name, senses.get(name, False), axes[ga], axes[gb], ga, gb,
                           SolidWorksError, (origins[ga], origins[gb]))

    def settle(name: str, a_ref: str, b_ref: str, ratio: Tuple[int, int]) -> None:
        """A gear mate just remade, read where probe ring_mate_sense read it (straight after it is made and named):
        wrong, made again with the other Flip than findings.GEAR_MATE_FLIP (which the remake tried first) and read
        again; wrong again, Update stops naming it (the locks are turned back on as for any failure)."""
        if not _sense_settled():
            return
        if read(name):
            return
        touched[0] = True
        first = bool(getattr(findings, "GEAR_MATE_FLIP", False))
        sw.remake_gear_mate(mate_handle[name], a_ref, b_ref, ratio, not first)
        result.turned_round.append(name)
        if not read(name):
            raise SolidWorksError(f"SolidWorks turns the gears of the mate {name} against the way they mesh, whichever "
                                  f"way round it is made; the saved {file} still has it as it was: close {file} in "
                                  "SolidWorks without saving to bring it back.")
    dirty = [False]

    def rebuild() -> None:
        result.rebuilt = bool(sw.rebuild(kind=ASSEMBLY_TRAIN))
        dirty[0] = False
        if not result.rebuilt:
            raise SolidWorksError(f"SolidWorks reported an error rebuilding {stem}.")

    # 2. a part or the layout changed: the mates carry the gears with their shafts (LAYOUT_MOVE_CARRIES_MATES)
    if result.changed:
        rebuild()
    # 3-4. recorded mates found suppressed turned back on (D10); each differing Face Z set; one rebuild, before any put
    for name in suppressed:
        touched[0] = True
        sw.set_mate_suppressed(mate_handle[name], False)
        result.unsuppressed.append(name)
    for gear, variable in axial:
        touched[0] = True
        sw.set_global_variable(variable.name, variable.expression_for(DEGREES))
        result.axial.append(gear)
    if result.unsuppressed or result.axial:
        rebuild()
    # A gear mate found suppressed, now turned back on and rebuilt: its sense read here, where the read-back holds
    # after a rebuild; one wrong joins the remakes, and its train is put below like any other. The route and the
    # remake's gates were read in the check phase, with every such mate counted as a possible remake.
    for name in deferred:
        if name not in result.unsuppressed:
            continue
        if read(name):
            continue
        # At the wanted ratio but turning wrong (an Update stopped on a remake wrong either way round, then the mate
        # suppressed): not "already there" — it is remade, as the check phase does for one found on.
        if name in result.ratios_already:
            result.ratios_already.remove(name)
        if all(n != name for n, _, _ in remakes):
            remakes.append((name, *(wanted_teeth or {})[name]))
        sense_wrong.add(name)
    # 5. every frame as it now stands; each train that needs a put is put whole, its locks off around the puts
    live = {p.gear: sw.component_frame(handle[p.gear]) for p in placements}
    axial_gears = {gear for gear, _ in axial}
    wanted = {p.gear: (p.rotation, p.at) for p in placements}
    pitch = {p.gear: p.pitch for p in placements}
    put_trains: List[Tuple[str, ...]] = []
    held = [g for g in motion.held if g in wanted]
    judged = list(mated) + [g for g in held if g not in mated]

    def links_of(train: Sequence[str]) -> Tuple[List[MeshLink], List[LockLink], List[CarrierLink], List[str]]:
        return ([m for m in motion.meshes if m.a in train and m.b in train],
                [lock for lock in motion.locks if lock.anchor in train and lock.follower in train],
                [link for link in motion.carriers if link.carrier in train], [g for g in held if g in train])

    def judge(frames: Mapping[str, Frame9], train: Sequence[str]) -> TrainCheck:
        meshes, locks, links, held_here = links_of(train)
        try:
            return train_check({g: frames[g] for g in train}, {g: wanted[g] for g in train}, meshes, locks, pitch,
                               carriers=links, held=held_here)
        except ValueError as exc:                     # W7-INTERFACES §6.3, as the check phase says it
            raise SolidWorksError(f"Update SolidWorks cannot judge the gears on record: {exc} That is a fault in "
                                  "Gear Generator.") from None

    # A held gear joins a train through its GEAR MATES only (W7-PLAN §2.9): an unmated mesh (a planetary's other
    # ring meshes) does not join two trains, so a train the user turned in step is never put because another one
    # sharing the held gear needed it; the unmated meshes are still judged within the train their gears are in.
    mated_pairs = {tuple(m.gears) for m in motion.mates if m.kind == "mesh" and len(m.gears) == 2}
    joining = [m for m in motion.meshes if not ({m.a, m.b} & set(held)) or (m.a, m.b) in mated_pairs]
    for train in _trains(judged, joining, motion.locks, motion.carriers):
        meshes, locks, links, held_here = links_of(train)
        ratios = [r for r in remakes if all(g in train for m in motion.mates if m.name == r[0] for g in m.gears)]
        here = judge(live, train)
        # Update moves a gear of this train (a shaft moved under it, its Face Z set, its gear mate remade): the user's
        # answer 2 — whenever Update moves any gear of a train, the train goes back to its built turn, whole.
        moved = any(g in axial_gears or _moved(result.found.get(g), live[g]) for g in train)
        if not (meshes or locks or links):
            needed = bool(here.off_axis) or moved     # a lone mated gear turns freely: put when off its axis or moved
        else:
            needed = not here.in_step or bool(ratios) or moved
        if not needed:
            continue
        _put_train(sw, result, motion, train, locks, ratios, handle, mate_handle, wanted, rebuild, file, touched,
                   settle, sense_wrong, resensed, respaced, held=held_here,
                   carriers=[link.carrier for link in links], live=live, pitch=pitch, route=route)
        put_trains.append(train)
        dirty[0] = dirty[0] or not locks
        restored = tuple(g for g in train if turned_back.get(g))
        if restored:
            result.restored.append(restored)
    unfix = route == REPLACE_ROUTES[1]
    put_set = {g for train in put_trains for g in train}
    for placement in placements:
        if placement.gear in mated or placement.gear in put_set or \
                same_frame(live[placement.gear][0], live[placement.gear][1], placement.rotation, placement.at,
                           placement.pitch):
            continue
        touched[0] = True
        if unfix:
            sw.unfix_component(handle[placement.gear])
        sw.place_component(handle[placement.gear], placement.rotation, placement.at, kind=ASSEMBLY_TRAIN)
        result.placed.append(placement.gear)
        if unfix:
            sw.fix_component(handle[placement.gear])
        dirty[0] = True
    if dirty[0]:
        rebuild()
    if not (result.changed or result.unsuppressed or result.axial or result.placed or result.ratios):
        return                                    # nothing changed: the assembly is only read (W4 review S2)

    # 6. the post-check: any surprise from an unprobed combination is a sentence, never silence
    after = {p.gear: sw.component_frame(handle[p.gear]) for p in placements}
    problems: List[str] = []
    for gear in result.placed:
        if not same_frame(after[gear][0], after[gear][1], wanted[gear][0], wanted[gear][1]):
            problems.append(f"{gear} is not where Update SolidWorks put it once the assembly rebuilt: a mate holds it "
                            "elsewhere.")
    for train in put_trains:
        again = judge(after, train)
        problems += [f"{a} and {b} are out of step once the assembly rebuilt." for a, b in again.out_of_step]
        problems += [f"{gear} is not where its train was put once the assembly rebuilt: a mate holds it elsewhere."
                     for gear in again.off_axis if gear not in result.placed]
    for name in result.ratios:
        status = sw.mate_status(name)
        if status != findings.ADD_MATE_NO_ERROR:
            problems.append(f"SolidWorks answered {status} when making the gear mate {name} again with its new ratio.")
    found_problems, result.mates = _mate_problems(sw, [m.name for m in motion.mates], statuses=False)
    problems += found_problems
    problems += _free_to_turn(sw, [handle[g] for g in mated], lambda h: gear_of_handle.get(h, h))
    result.failures.extend((file, problem) for problem in problems)

    # 7. interference (W4)
    if result.rebuilt and not result.failures and getattr(findings, "INTERFERENCE_CHECKED", False):
        say(Step(STAGE_INTERFERENCE, stem))
        gear_of = {p.component: p.gear for p in placements}
        try:
            result.clashes = _clashes(sw.interferences(), gear_of)
        except Exception as exc:  # noqa: BLE001 - a clash check that cannot run is a CHECK, never a failure
            result.interference_error = _said(exc)


def _put_train(sw: SolidWorks, result: GearboxUpdate, motion: MotionUpdate, train: Sequence[str],
               locks: Sequence[LockLink], ratios: Sequence[Tuple[str, int, int]], handle: Mapping[str, str],
               mate_handle: Mapping[str, str], wanted: Mapping[str, Frame9], rebuild: Callable[[], None],
               file: str, touched: List[bool],
               settle: Optional[Callable[[str, str, str, Tuple[int, int]], None]] = None,
               sense_wrong: Collection[str] = (), resensed: Collection[str] = (),
               respaced: Collection[str] = (), *, held: Collection[str] = (), carriers: Collection[str] = (),
               live: Optional[Mapping[str, Frame9]] = None, pitch: Optional[Mapping[str, float]] = None,
               route: Optional[str] = None, gear_mates: Optional[Collection[str]] = None,
               configuration: Optional[str] = None) -> None:
    """One train put back whole: every lock of it suppressed (a lock does not hold against a put: W5-DECISIONS),
    a rebuild, its ratios remade, EVERY mated gear of it put (review M1), then — whatever happened — every lock
    turned back on and a rebuild (review M8).

    W7 (W7-PLAN §2.9, review M1, M5; reading J15): the puts go in this order — each ``held`` gear of the train that
    is not where it belongs (whole pitches allowed) re-placed FIRST, by ``findings.REPLACE_FIXED_ROUTE`` as a fixed
    gear is; then each carrier; then every other gear, its planets among them. A carrier's lock to the gear on its
    own shaft is one of the train's locks, so it is off around the puts and that gear is put to its own wanted
    frame. A train WITH a carrier is put by ``findings.PLANETARY_PUT_ROUTE`` ("gear mates off around the puts", probe
    planetary_put_back on SolidWorks 2026): with the gear mates on, a carrier put first read back 6.2° short, as did
    the sun alone first and every put before one rebuild; what held, to 2e-9 mm, is every gear mate of the train
    suppressed with its locks, a rebuild, the puts in the order above (each read back by ``place_component``), a
    rebuild, every gear mate and lock turned back on, a rebuild — the gear mates keeping their ratio and sense
    (``GEAR_MATE_BACK_ON_KEEPS_SENSE_AND_RATIO``) — and here each gear mate's sense read again after (``settle``). A
    ratio remade inside it (a tooth change on a planetary, not covered by the probe) is remade after the
    suppression and its rebuild, read for sense, and suppressed again before the puts. A train with no carrier is
    put as before, its gear mates on. ``gear_mates`` (W8): the gear mates on in the configuration shown; only those
    are suppressed and turned back on, so a per-mode one off there stays off (§9.1). None (W7): every gear mate of
    the train, which D10 has turned on before any put. ``configuration`` (W8): the configuration shown; every lock
    and gear mate is then suppressed and turned back on in it alone by the measured per-configuration route
    (``set_mate_suppressed_in``, ``findings.MATE_SUPPRESSION_PER_CONFIGURATION_ROUTE``, each flag read back) and
    read before it is turned back on by ``mate_suppression`` (one ``IsSuppressed2(3, [name])`` per configuration,
    here the one shown, which marks nothing), never by ``SetSuppression2(…, this configuration, None)``, which no
    probe has run on an assembly with several configurations (W8-REVIEW-LATE-A point 1). None (W5, W6, W7):
    ``set_mate_suppressed`` and ``mate_states``, the calls as before. A lock or gear mate that will not come back on
    is a failure naming it, and stops the job (:class:`_LocksLeftOff`); what raised inside is raised again once they
    are tried. A gear mate gone from the assembly by then (a remake that lost it after the delete) is not said to be
    left suppressed: the error on its way out says it is gone, and, with none, its own ``MateGone`` sentence stops
    the job.

    A lock counts as tried the moment its suppression is asked for, so one whose suppression took before the call
    raised (a read-back that failed) is still turned back on. Turning back on, each lock is read first and one that
    reads not suppressed is skipped, never called: unsuppressing a lock that is on marks the assembly modified
    (probe round P0c, ``findings.UNSUPPRESS_ON_LOCK_ALREADY_ON_MARKS_MODIFIED``)."""
    off: List[LockLink] = []
    gear_off: List[str] = []                 # a train with a carrier: its gear mates, off around the puts
    pending: Optional[BaseException] = None

    def suppress(name: str, suppressed: bool) -> None:
        if configuration is None:
            sw.set_mate_suppressed(mate_handle[name], suppressed)
        else:
            sw.set_mate_suppressed_in(mate_handle[name], suppressed, [configuration])

    try:
        for lock in locks:
            off.append(lock)
            touched[0] = True
            suppress(_lock_mate_name(motion, lock), True)
        if carriers:
            for mate in motion.mates:
                if mate.kind in GEAR_MATE_KINDS and len(mate.gears) == 2 and all(g in train for g in mate.gears) \
                        and mate.name in mate_handle and (gear_mates is None or mate.name in gear_mates):
                    gear_off.append(mate.name)
                    touched[0] = True
                    suppress(mate.name, True)
        if off or gear_off:
            rebuild()
        for name, numerator, denominator in ratios:
            a, b = next(m.gears for m in motion.mates if m.name == name)
            touched[0] = True
            sw.set_gear_ratio(mate_handle[name], f"{handle[a]}:{AXIS_NAME}", f"{handle[b]}:{AXIS_NAME}",
                              (numerator, denominator))
            # ``ratios`` is for a ratio that changed (asked by the plan, or found at another); a gear mate remade only
            # because it turned wrong, at the ratio it already held, is ``sense_found_wrong`` alone. One the plan asked
            # stays in ``ratios`` even if SolidWorks already held the asked ratio (a stopped remake pressed again,
            # read on or turned back on first): the workbook's record takes the plan's ratio from ``ratios``.
            # One remade because the workbook now turns it the other way (``resensed``) is in ``ratios`` only when its
            # ratio changed too (``respaced``), and is listed in ``resensed`` once read back against its new ``k``.
            sense_only = name in sense_wrong and all(n != name for n, _, _ in motion.ratios) \
                and name not in result.ratios_found
            if name in resensed:
                if name in respaced:
                    result.ratios.append(name)
            elif not sense_only:
                result.ratios.append(name)
            if settle is not None:
                settle(name, f"{handle[a]}:{AXIS_NAME}", f"{handle[b]}:{AXIS_NAME}", (numerator, denominator))
            if name in resensed:
                result.resensed.append(name)
            elif name in sense_wrong:
                result.sense_found_wrong.append(name)
        remade_off = [name for name, _, _ in ratios if name in gear_off]
        for name in remade_off:                       # made again on: off again before the puts
            suppress(name, True)
        if remade_off:
            rebuild()
        unfix = route == REPLACE_ROUTES[1]
        for gear in [g for g in train if g in held]:
            frame = (live or {}).get(gear)
            if frame is not None and same_frame(frame[0], frame[1], wanted[gear][0], wanted[gear][1],
                                                (pitch or {}).get(gear, 0.0)):
                continue                          # a held gear where it belongs (whole teeth allowed) stays
            touched[0] = True
            if unfix:
                sw.unfix_component(handle[gear])
            sw.place_component(handle[gear], wanted[gear][0], wanted[gear][1], kind=ASSEMBLY_TRAIN)
            result.placed.append(gear)
            if unfix:
                sw.fix_component(handle[gear])
        rest = [g for g in train if g not in held]
        for gear in [g for g in rest if g in carriers] + [g for g in rest if g not in carriers]:
            touched[0] = True
            sw.place_component(handle[gear], wanted[gear][0], wanted[gear][1], kind=ASSEMBLY_TRAIN)
            result.placed.append(gear)
    except BaseException as exc:  # noqa: BLE001 - raised again below, once the locks are back on
        pending = exc
    left_off = False
    states: Optional[Dict[str, bool]] = None           # mate name -> suppressed in the configuration shown
    if (off or gear_off) and configuration is None:
        try:
            states = {state.name: state.suppressed for state in sw.mate_states()}
        except Exception:  # noqa: BLE001 - unread: each lock is turned back on, as if it read suppressed
            states = None
    elif off or gear_off:
        states = {}
        for name in [_lock_mate_name(motion, lock) for lock in off] + gear_off:
            try:
                states[name] = bool(sw.mate_suppression(mate_handle[name], [configuration])[configuration])
            except Exception:  # noqa: BLE001 - unread: turned back on, as if it read suppressed
                pass
    for lock in off:
        name = _lock_mate_name(motion, lock)
        if states is not None and name in states and not states[name]:
            continue
        try:
            suppress(name, False)
        except Exception as exc:  # noqa: BLE001 - review M8: said, never lost
            left_off = True
            said = _said(exc).rstrip(".")
            result.failures.append((file, f"The compound gears {lock.anchor} and {lock.follower} are not locked: "
                                          f"SolidWorks would not turn {name} back on ({said}); press Update "
                                          "SolidWorks again, which turns it back on."))
    for name in gear_off:
        if states is not None and name in states and not states[name]:
            continue
        try:
            suppress(name, False)
        except MateGone as exc:
            # Gone, not left suppressed (a remake inside the route that lost its mate after the delete): pressing
            # Update again would find it gone, so the error on its way out, which says so, is the sentence.
            if pending is None:
                pending = exc
        except Exception as exc:  # noqa: BLE001 - said, never lost
            left_off = True
            result.failures.append((file, f"The gear mate {name} is left suppressed: SolidWorks would not turn it "
                                          f"back on ({_said(exc).rstrip('.')}); press Update SolidWorks again, which "
                                          "turns it back on."))
    if off or gear_off:
        try:
            rebuild()
        except Exception as exc:  # noqa: BLE001 - kept when something else is already on its way out
            if pending is None and not left_off:
                raise
            result.failures.append((file, _said(exc)))
    if pending is not None:
        raise pending
    if left_off:
        raise _LocksLeftOff()
    if gear_off and settle is not None:
        # Each gear mate turned back on read for sense, by the same path as a remade one (wrong: made again with
        # the other Flip, read again; wrong again stops the job).
        for name in gear_off:
            if any(n == name for n, _, _ in ratios):
                # A mate remade inside the suppression is read when it is remade and not again once turned back on:
                # GEAR_MATE_BACK_ON_KEEPS_SENSE_AND_RATIO was measured on built mates, not on remade ones.
                continue
            a, b = next(m.gears for m in motion.mates if m.name == name)
            live = sw.gear_mate_ratio(mate_handle[name])
            settle(name, f"{handle[a]}:{AXIS_NAME}", f"{handle[b]}:{AXIS_NAME}",
                   (int(round(float(live[0]))), int(round(float(live[1])))))
