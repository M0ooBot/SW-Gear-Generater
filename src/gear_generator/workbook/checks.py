"""The gearbox-level checks (docs/PLAN-WORKBOOK.md §3.4; phase W3: shafts on the frame along Z+ or Z-).

Each gear's own checks are the strip's (:mod:`workbook.build`); these are the
ones only a whole gearbox has: meshing gears that agree with each other and
sit exactly where their teeth put them, faces that meet, gears that do not
clash, tips that miss other shafts, and speeds every shaft can be given.
Every message names the cell to look at, and a centre distance that is off
comes with the fixes of :mod:`workbook.fixes`. Rows a later phase builds are
not errors: :func:`workbook.build.later_rows` says each one, and Build refuses it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from itertools import combinations
from typing import Dict, List, Optional, Tuple

from ..gears import helical, internal as internal_gears, pair as pairs, spur
from ..gears.base import ERROR, WARNING, Diagnostic
from . import fixes as fixes_mod, geometry, kinematics, modes as modes_mod, planetary, strength as strength_mod
from .fixes import Fix
from .geometry import Layout, Placed
from .model import GearboxSpec

CENTRE_TOLERANCE = 0.005      # mm: half the last digit of a distance typed to two decimals
NEAR_MESH_BAND = 0.1          # × module: two unlisted gears this near their mesh distance would mesh (a warning);
                              # nearer than that they jam, and that is a clash
CLASH_GAP = 0.5               # × module: the least room between gears that do not mesh


@dataclass
class ModeReport:
    """One mode worked out (W8-PLAN §1.3-§1.5; B fills it, C and D read it). ``name``: the mode's, ``""`` for the
    implicit mode of sliders with no Modes rows; ``row`` its Modes-sheet row (0 for the implicit one).
    ``positions``: slider -> (position name, offset mm) here. ``engaged``: (sleeve, dog) pairs engaged here, dogs in
    Gears-sheet order. ``out_of_mesh``: listed meshes a slide takes out of mesh here. ``off``: relations left off
    here as loop-closers (J15). ``placed``: every slider placed at its position here. ``motion``: this mode's
    speeds (``kinematics.Motion``; a free member's speed is absent, J16)."""

    name: str
    row: int = 0
    positions: Dict[str, Tuple[str, float]] = field(default_factory=dict)
    engaged: Tuple[Tuple[str, str], ...] = ()
    out_of_mesh: Tuple[Tuple[str, str], ...] = ()
    off: Tuple[Tuple[str, str], ...] = ()
    placed: Dict[str, Placed] = field(default_factory=dict)
    motion: kinematics.Motion = field(default_factory=kinematics.Motion)
    # W8 (B, additive; the one home of a mode's ratio, for the Speeds line and Export): ``ends`` the first input
    # and the first output joined to it that turns here (``("", "")`` without); ``ratio`` input speed ÷ that
    # output's, None without; ``ratio_why`` ``""`` with a ratio, else why — ``"neutral"`` when no output turns
    # here; ``driven`` every output -> input ÷ output here, None when it does not turn here ("not driven").
    ends: Tuple[str, str] = ("", "")
    ratio: Optional[float] = None
    ratio_why: str = ""
    driven: Dict[str, Optional[float]] = field(default_factory=dict)


@dataclass
class Report:
    diagnostics: List[Diagnostic] = field(default_factory=list)
    fixes: Dict[str, List[Fix]] = field(default_factory=dict)   # by the diagnostic's field (its cell)
    layout: Layout = field(default_factory=Layout)
    theta: Dict[str, float] = field(default_factory=dict)       # each placed gear's turn, radians
    motion: kinematics.Motion = field(default_factory=kinematics.Motion)
    centres: Dict[Tuple[str, str], Tuple[float, float]] = field(default_factory=dict)   # mesh -> (needed, placed)
    contact: Dict[Tuple[str, str], float] = field(default_factory=dict)                # mesh -> εα at the needed centre
    # W6 (B; W6-PLAN §2.3): every listed mesh mesh_geometry laid out, keyed by the Meshes row's ordered pair (a, b).
    meshes: Dict[Tuple[str, str], geometry.MeshGeometry] = field(default_factory=dict)
    # W7 (B; W7-PLAN §2.1, §2.3): every planetary stage recognised (planetary.stages); () when there is none.
    stages: Tuple[planetary.Stage, ...] = ()
    # W7 (B; W7-PLAN §2.3 item 7): the gears of a planetary stage below the undercut limit (row ids, Gears-sheet
    # order), whose undercut is not modelled — for the interference sentence's clause; () when there is none.
    undercut: Tuple[str, ...] = ()
    off_centre: List[Diagnostic] = field(default_factory=list)   # the "not where the teeth put them" errors
    # W8 (B; W8-PLAN §1.4-§1.5, W8-INTERFACES.md §4): one ModeReport per mode in Modes-sheet order, or one with name ""
    # for sliders with no Modes rows; () with no sliders. ``motion`` above is then the first mode's (S1).
    modes: Tuple["ModeReport", ...] = ()
    worked_out_as: str = ""
    # Why the gearbox was not checked at all ("" when it was): a carrier or a turned axis, laid out in a later
    # phase. Then ``diagnostics`` is empty because nothing was looked at, not because nothing is wrong.
    unchecked: str = ""
    # F4 (package B; PLAN-PRINTED §5.2, F4-INTERFACES §4): every Meshes row's teeth in every mode, against what they
    # are rated to take (strength.mesh_strengths); () for a machined gearbox or one whose first input has no torque.
    strength: Tuple[strength_mod.MeshStrength, ...] = ()

    @property
    def checked(self) -> bool:
        return not self.unchecked

    @property
    def errors(self) -> List[Diagnostic]:
        return [d for d in self.diagnostics if d.is_error]


def _error(report: Report, where: str, message: str) -> None:
    report.diagnostics.append(Diagnostic(ERROR, f"{where}: {message}", where))


def _warning(report: Report, where: str, message: str) -> None:
    report.diagnostics.append(Diagnostic(WARNING, f"{where}: {message}", where))


def _n(value: float, places: int = 3) -> str:
    return f"{value:.{places}f}".rstrip("0").rstrip(".")


def check(spec: GearboxSpec, skip_gears=()) -> Report:
    """Every gearbox-level check for what this phase lays out. ``skip_gears``: gears with errors of their own."""
    report = Report()
    report.layout = lay = geometry.layout(spec, skip_gears)
    # W7-PLAN §1.2, with the orchestrator's ruling: a planetary form this version does not build is an error of the
    # workbook, said at its cell (never "waiting for a later phase"), whether or not the rows can be laid out.
    report.diagnostics.extend(planetary.refusals(spec))
    if lay.later:
        # A carrier or a turned axis: nothing here is checked until its phase. Each such row is said, at its
        # cell, by workbook.build.later_rows, with the rows Build refuses; the report says it was not checked.
        report.unchecked = lay.later[0]
        report.worked_out_as = "Not laid out yet: " + lay.later[0].split(":")[0]
        report.motion = kinematics.solve(spec, skip_gears)
        return report
    # From here every shaft is on the frame along Z+ or Z-: kinematics.solve has worked out what it can
    # (its ``later`` is set only for the layouts returned above).
    gears = {g.id: g for g in spec.gears}
    placed = lay.placed
    # W8 (W8-PLAN §1.2-§1.3): every slider stands at the first mode's position for the checks of the whole box;
    # every other mode re-places its sliders below. A sleeve or dog on Meshes, a dog with Slides, a pick with no 0.
    picks, pick_errors = modes_mod.mode_picks(spec)
    report.diagnostics.extend(pick_errors)
    report.diagnostics.extend(modes_mod.row_errors(spec))
    if picks:
        placed.update(modes_mod.place_mode(spec, placed, picks[0]))
    for gear_id, why in lay.problems.items():
        _error(report, spec.cell("Gears", gears[gear_id].row, "id"), f"{gear_id} could not be placed: {why}")

    # W7: a planet's copies are placed one by one (keyed by copy id); a Meshes row is checked once, on copy 1, under
    # its row's names, and clearances and phases take the meshes copy by copy (W7-PLAN §2.2, §2.3).
    first = {}
    for p in placed.values():
        first.setdefault(p.row or p.gear, p)
    expanded = geometry.expand_meshes(spec, placed)
    listed = {frozenset(pair) for pair in expanded} | {frozenset((m.a, m.b)) for m in spec.meshes}
    report.stages = planetary.stages(spec) if any(p.carrier for p in placed.values()) else ()
    unfit: List[Tuple[str, str]] = []              # Meshes rows that fit no carrier: their consequences are not said
    clutches = {g.id for g in spec.gears if g.kind_word() in modes_mod.CLUTCH_KINDS}
    for mesh in spec.meshes:
        a, b = first.get(mesh.a), first.get(mesh.b)
        if a is None or b is None or mesh.a in clutches or mesh.b in clutches:
            continue                               # a sleeve or dog on Meshes is an error of its own (modes)
        where = spec.cell("Meshes", mesh.row, "a")
        if a.carrier or b.carrier:
            a, b = _as_row(a), _as_row(b)
            if planetary.mesh_carrier(spec, mesh.a, mesh.b) is None:
                unfit.append((mesh.a, mesh.b))
                carried, other = (a, b) if a.carrier else (b, a)
                carrier = carried.carrier
                _error(report, where, f"{carried.gear} rides {carrier} and meshes {other.gear}, whose shaft "
                                      f"{other.shaft} is not on {carrier}'s axis: a gear on a carrier meshes only a "
                                      f"gear on a shaft along its carrier's axis.")
                continue
        try:
            laid = geometry.mesh_geometry(a, b)
        except (ValueError, ArithmeticError, AttributeError) as exc:
            _error(report, where, f"{a.gear} and {b.gear}: {exc}")
            continue
        if laid.kind == geometry.PARALLEL:
            _check_mesh(report, spec, mesh, a, b, where)
            needed = report.centres.get((a.gear, b.gear), (laid.needed, laid.placed))[0]
            report.meshes[(mesh.a, mesh.b)] = replace(laid, a=mesh.a, b=mesh.b, needed=needed)
        else:
            if _check_turned(report, spec, a, b, laid, where):
                report.meshes[(mesh.a, mesh.b)] = laid
    assembly_said = _check_stages(report, spec, placed) if report.stages else False

    senses = {key: m.sense for key, m in report.meshes.items() if not m.problem}
    report.motion = kinematics.solve(spec, skip_gears, senses=senses)
    if picks:
        report.modes = tuple(_mode_report(report, spec, skip_gears, senses, placed, p) for p in picks)
        report.motion = report.modes[0].motion
    # A mesh that fits no carrier is the one true error: the speeds, pass-overs and phase loops it upsets are not
    # said beside it (the shafts of its stage are left out of those).
    shaft_of = {g.id: g.shaft for g in spec.gears}
    upset = set()
    for a_id, b_id in unfit:
        upset.update(x for x in (shaft_of.get(a_id), shaft_of.get(b_id)) if x)
        upset.update(x.carrier for x in placed.values() if x.row in (a_id, b_id) and x.carrier)
    upset.update(x.id for x in spec.shafts if x.mount() in upset)
    _check_clearances(report, spec, placed, listed)
    for m in report.modes[1:]:                      # W8: each other mode's sliders where that mode puts them
        here = dict(placed)
        here.update(m.placed)
        _check_clearances(report, spec, here, listed, only=set(m.placed), said={d.message for d in report.diagnostics})
    report.diagnostics.extend(d for d in modes_mod.mode_checks(spec, placed, report.modes)
                              if d not in report.diagnostics)
    report.diagnostics.extend(d for d in modes_mod.hub_errors(spec, placed, report.modes)     # W9b: K8
                              if d not in report.diagnostics)
    # W9b package A (ISSUE-1-PLAN §2.2, §2.3): the sleeve checks, each a warning at its cell.
    report.diagnostics.extend(d for d in modes_mod.reach_warnings(spec, placed) + modes_mod.hub_warnings(spec, placed)
                              + modes_mod.clearance_warnings(spec, placed, report.modes)
                              if d not in report.diagnostics)
    _check_shafts(report, spec, placed, upset)
    _check_turned_clearances(report, spec, placed, listed)
    _check_motion(report, spec, upset)
    couplings = []
    for m in report.modes:
        couplings += [pair for pair in m.engaged if pair not in couplings]
    order = [g.id for g in spec.gears]
    couplings.sort(key=lambda pair: order.index(pair[1]))       # the dogs' Gears-sheet order (W8-PLAN §1.6)
    # A sleeve or dog on Meshes is an error of its own (modes.row_errors): its row is left out of the phase walk too,
    # so nothing is said beside it (a loop "that does not close" through a row that is not a mesh).
    on_meshes = [(m.a, m.b) for m in spec.meshes if m.a in clutches or m.b in clutches]
    report.theta, conflicts = geometry.phases(spec, placed, with_conflicts=True, meshes_=report.meshes,
                                              leave_out=list(unfit) + on_meshes, couplings=couplings)
    carried = {p.gear for p in placed.values() if p.carrier}
    for gear_id, other in conflicts:
        row = placed[gear_id].row or gear_id
        sentence = (f"{gear_id}'s teeth cannot sit in the spaces of every gear it meshes with at once (the turn "
                    f"{other} asks of it disagrees): a loop of meshes that does not close; check the tooth counts.")
        if gear_id in carried or other in carried:
            # W7-PLAN §2.4: a loop through a carrier's copies that does not close is the assembly condition failing,
            # an error; said once, by _check_stages, when it reduces to the simple stage's count.
            if not assembly_said:
                _error(report, spec.cell("Gears", gears[row].row, "id"), sentence)
            continue
        _warning(report, spec.cell("Gears", gears[row].row, "id"), sentence)
    _check_strength(report, spec)
    report.worked_out_as = _worked_out_as(spec, report)
    return report


def _check_strength(report: Report, spec: GearboxSpec) -> None:
    """F4 (package B; PLAN-PRINTED §5.2, §5.4): a printed gearbox's teeth against what they are rated to take, mode by
    mode, kept in ``report.strength`` for the Results sheet, and one warning at a Meshes row whose share passes 100 %
    in some mode or that has a ring not rated in a loaded mode (``strength.warning_sentence``), the pair first as F1's
    clearance warning is said. A machined gearbox, or one whose first input has no torque, is told nothing."""
    report.strength = strength_mod.mesh_strengths(spec, report)
    if not report.strength:
        return
    allowable, typed = strength_mod.allowable_of(spec)
    for mesh in spec.meshes:
        sentence = strength_mod.warning_sentence([r for r in report.strength if r.row == mesh.row], allowable, typed)
        if sentence:
            _warning(report, spec.cell("Meshes", mesh.row, "a"), f"{mesh.a} and {mesh.b}: {sentence}")


def _mode_report(report: Report, spec: GearboxSpec, skip_gears, senses, placed: Dict[str, Placed],
                 picks: "modes_mod.Picks") -> "ModeReport":
    """One mode worked out (W8-PLAN §1.3-§1.5): its sliders placed, what it engages, its speeds and torques (J17),
    its jam said at its cell, and its ratio (the one home: :func:`mode_ratio`)."""
    here = dict(placed)
    moved = modes_mod.place_mode(spec, placed, picks)
    here.update(moved)
    found = modes_mod.engagement(spec, here, picks)
    report.diagnostics.extend(d for d in found.diagnostics if d not in report.diagnostics)
    motion = kinematics.solve(spec, skip_gears, senses=senses, leave_out=found.out_of_mesh, couples=found.engaged)
    out = ModeReport(picks.name, picks.row, dict(picks.positions), tuple(found.engaged), tuple(found.out_of_mesh),
                     (), moved, motion)
    if motion.jammed and spec.meshes:
        where = spec.cell("Modes", picks.row, "name") if picks.row else "Modes"
        twice = [s for s in {s for s, _ in found.engaged} if sum(1 for x, _ in found.engaged if x == s) > 1]
        gears = {g.id: g for g in spec.gears}
        if twice:
            dogs = [d for s, d in found.engaged if s == twice[0]]
            _error(report, where, f"in {picks.name} {twice[0]} engages {' and '.join(dogs)} at once, which joins "
                                  f"{' to '.join(gears[d].shaft for d in dogs)}: as written the box is jammed in this "
                                  "mode.")
        elif found.engaged:
            # §1.5: name what engages what, and the shafts it joins that the meshes already turn at other speeds.
            said = _and([f"{s} engages {d}" for s, d in found.engaged])
            dogs = list(dict.fromkeys(gears[d].shaft for _, d in found.engaged))
            sleeves = list(dict.fromkeys(gears[s].shaft for s, _ in found.engaged))
            joined = (f"which joins {_and(dogs)} through {_and(sleeves)}" if len(dogs) > 1 else
                      f"which joins {dogs[0]} to {_and(sleeves)}")
            _error(report, where, f"in {picks.name or 'its one mode'} {said}, {joined}, and the meshes turn them at "
                                  "different speeds: as written the box is jammed in this mode.")
        else:
            _error(report, where, f"in {picks.name or 'its one mode'} the meshes and couplings contradict each "
                                  "other: as written the box is jammed in this mode.")
    ratio, ends, why, driven = mode_ratio(spec, motion)
    out.ratio, out.ends, out.ratio_why, out.driven = ratio, ends, why, driven
    return out


def mode_ratio(spec: GearboxSpec, motion: kinematics.Motion) -> Tuple[Optional[float], Tuple[str, str], str,
                                                                        Dict[str, Optional[float]]]:
    """The one home of a mode's ratio (for the Speeds line, Export and :func:`_worked_out_as`): ``(input ÷ output,
    (input, output), why there is none, every output -> input ÷ output or None)``. The input is the first one that
    turns; the output the first output that turns in this mode — a free output is "not driven" (None) and with no
    output turning the mode is ``"neutral"``."""
    inputs = [s for s in spec.shafts if s.role == "input" and motion.speeds.get(s.id)]
    outputs = [s for s in spec.shafts if s.role == "output"]
    if not inputs:
        return None, ("", ""), NO_ENDS, {s.id: None for s in outputs}
    first = inputs[0]
    driven = {s.id: (abs(float(motion.speeds[first.id] / motion.speeds[s.id])) if motion.speeds.get(s.id) else None)
              for s in outputs}
    turning = [s.id for s in outputs if driven[s.id] is not None]
    if not turning:
        return None, ("", ""), "neutral", driven
    return driven[turning[0]], (first.id, turning[0]), "", driven


def _as_row(p: Placed) -> Placed:
    """A placed copy under its row's names (``Planet``, ``P``), for the checks a Meshes row says once."""
    return replace(p, gear=p.row or p.gear, shaft=planetary.copy_of(p.shaft)[0])


def _and(items: List[str], word: str = "and") -> str:
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + f" {word} " + items[-1]


def _check_stages(report: Report, spec: GearboxSpec, placed: Dict[str, Placed]) -> bool:
    """What W7 adds on top of the mesh checks for each planetary stage (W7-PLAN §2.3 items 1-3, 7), each at its
    cell: the ring's tooth count for a simple unshifted stage, said in place of the centre errors it causes; the
    assembly condition; the copies' room round the carrier; a sun or planet below the undercut limit. Whether the
    assembly condition was said (the phase walk's loop error is then not said again)."""
    gears = {g.id: g for g in spec.gears}
    shafts = {x.id: x for x in spec.shafts}
    said = False
    for stage in report.stages:
        copies = [p for p in placed.values() if p.row == stage.planet and p.carrier == stage.carrier]
        sun, ring = placed.get(stage.sun), placed.get(stage.ring)
        if not copies:
            continue
        planet = copies[0]
        n = len(copies)
        planet_shaft = shafts[stage.planet_shaft]
        copies_cell = spec.cell("Shafts", planet_shaft.row, "copies")
        if sun is not None and ring is not None:
            z_s, z_p, z_r = sun.teeth, planet.teeth, ring.teeth
            shifted = any(getattr(g.derived, "shift", 0.0) for g in (sun, planet, ring))
            ring_wrong = not shifted and z_r != z_s + 2 * z_p
            if ring_wrong:
                said = True                         # the copies' loop cannot close either: said once, here
                rows = {spec.cell("Meshes", m.row, "a") for m in spec.meshes
                        if {m.a, m.b} in ({stage.sun, stage.planet}, {stage.planet, stage.ring})}
                report.diagnostics = [d for d in report.diagnostics if d not in report.off_centre or d.field not in rows]
                report.off_centre = [d for d in report.off_centre if d.field not in rows]
                _error(report, spec.cell("Gears", gears[stage.ring].row, "teeth"),
                       f"{stage.ring} has {z_r} teeth, and a ring around {stage.sun} ({z_s}) and {stage.planet} "
                       f"({z_p}) needs {z_s} + 2 × {z_p} = {z_s + 2 * z_p}: with {z_r} the planets cannot mesh with "
                       "both at once.")
            outer = report.centres.get((stage.sun, stage.planet)) or report.centres.get((stage.planet, stage.sun))
            inner = report.centres.get((stage.planet, stage.ring)) or report.centres.get((stage.ring, stage.planet))
            if shifted and outer and inner and abs(outer[0] - inner[0]) > CENTRE_TOLERANCE:
                # The reviewer's note: with a shift the two working centres can differ, and then no radius works.
                ring_row = next((spec.cell("Meshes", m.row, "a") for m in spec.meshes
                                 if {m.a, m.b} == {stage.planet, stage.ring}), "")
                tail = (f" {stage.planet} meshes {_n(outer[0])} mm from {stage.sun}'s axis and {_n(inner[0])} mm from "
                        f"{stage.ring}'s, so no one distance from {stage.carrier}'s axis meshes both.")
                for i, d in enumerate(report.diagnostics):
                    if d in report.off_centre and d.field == ring_row:
                        new = replace(d, message=d.message + tail)
                        report.diagnostics[i] = new
                        report.off_centre[report.off_centre.index(d)] = new
            a = math.hypot(planet.x - sun.x, planet.y - sun.y)
            fit = planetary.most_that_fit(a, planet.outer_radius * 2.0, planet.module)
            counts = planetary.assembly_counts(z_s, z_r, fit)
            listed = _and([str(c) for c in counts], "or")
            if (z_s + z_r) % n and not ring_wrong:
                said = True
                _error(report, copies_cell,
                       f"{n} copies of {stage.planet} cannot all mesh with {stage.sun} and {stage.ring} at once: "
                       f"({z_s} + {z_r}) / {n} = {_n((z_s + z_r) / n)} is not a whole number. With these teeth the "
                       f"copies can be {listed}; more would not fit round {stage.carrier}.")
            if n > fit:
                need = planet.outer_radius * 2.0 + CLASH_GAP * planet.module
                also = (f", and of those {_and([str(c) for c in counts])} also mesh with {stage.sun} and "
                        f"{stage.ring}." if counts else ".")
                _error(report, copies_cell,
                       f"{n} copies of {stage.planet} stand {_n(2 * a * math.sin(math.pi / n))} mm apart round "
                       f"{stage.carrier}, and their tips need {_n(need)} mm: {fit} is the most that fit round "
                       f"{stage.carrier}{also}")
        for small, other in ((sun, planet), (planet, sun)):
            if small is None or other is None or not getattr(small.derived, "undercut", False):
                continue
            row = small.row or small.gear
            report.undercut = tuple(g.id for g in spec.gears if g.id in set(report.undercut) | {row})
            _warning(report, spec.cell("Gears", gears[row].row, "id"),
                     f"{row} ({small.teeth} teeth) is below the undercut limit, which is not modelled, and meshes "
                     f"{other.row or other.gear} ({other.teeth} teeth): the build checks interference only where the "
                     f"gears stand, so check {row} with {other.row or other.gear} turning in SolidWorks.")
    return said


def _plane_cells(gear: geometry.Placed) -> str:
    """The Shafts cells that place a shaft in its family's plane (W6): ``X and Y`` for the Z family, ``Y and Z`` for
    X, ``X and Z`` for Y, all three for a slant."""
    plus = tuple(float(v) for v in getattr(gear, "family", (0.0, 0.0, 1.0)))
    return {(1.0, 0.0, 0.0): "Y and Z", (0.0, 1.0, 0.0): "X and Z", (0.0, 0.0, 1.0): "X and Y"}.get(plus,
                                                                                                  "X, Y and Z")


def _check_mesh(report: Report, spec: GearboxSpec, mesh, a: Placed, b: Placed, where: str) -> None:
    gears = {g.id: g for g in spec.gears}
    ga, gb = gears[a.gear], gears[b.gear]
    planetary_mesh = bool(a.carrier or b.carrier)
    if a.shaft == b.shaft:
        _error(report, where, f"{a.gear} and {b.gear} are on the same shaft, {a.shaft}; gears that mesh turn on "
                              "different shafts.")
        return
    kind_a, kind_b = ga.kind_word(), gb.kind_word()
    if kind_a != kind_b:
        _error(report, where, f"{a.gear} is {kind_a} and {b.gear} is {kind_b}; meshing gears are the same kind.")
        return
    if kind_a == "bevel":
        _error(report, where, f"{a.gear} and {b.gear} are bevel gears on parallel shafts; bevel gears mesh across "
                              "shafts at an angle.")
        return
    if abs(a.module - b.module) > 1e-9:
        _error(report, where, f"{a.gear} has module {_n(a.module)} and {b.gear} {_n(b.module)}; meshing gears "
                              "share one module.")
        return
    pa_a = float(ga.pressure_angle or spec.box.pressure_angle_text())
    pa_b = float(gb.pressure_angle or spec.box.pressure_angle_text())
    if abs(pa_a - pa_b) > 1e-9:
        _error(report, where, f"{a.gear}'s pressure angle is {_n(pa_a)}° and {b.gear}'s {_n(pa_b)}°; meshing "
                              "gears share one.")
        return
    if a.internal and b.internal:
        _error(report, where, f"{a.gear} and {b.gear} are both rings; a ring meshes with a gear inside it.")
        return
    beta = 0.0
    if kind_a in ("helical", "herringbone"):
        beta = float(ga.helix_angle)
        if abs(beta - float(gb.helix_angle)) > 1e-9:
            _error(report, where, f"{a.gear}'s helix angle is {_n(beta)}° and {b.gear}'s {_n(float(gb.helix_angle))}°;"
                                  " gears on parallel shafts mesh at one helix angle.")
            return
        ring = a.internal or b.internal
        same = (ga.hand or "right") == (gb.hand or "right")
        # A herringbone's hand names its half nearest its own front face. Turned over on a Z- shaft, that half
        # sits at the other end, so against a gear on Z+ it presents the other hand: the typed hands then pair
        # the other way. A helical gear's helix reads the same from either end, so its hand never flips.
        flipped = kind_a == "herringbone" and a.sigma != b.sigma
        want_same = ring != flipped
        if want_same and not same:
            why = ("a pinion in a ring takes the same hand as the ring" if ring else
                   "herringbones on shafts facing opposite ways take the same typed hand, since one is turned over")
            _error(report, where, f"{a.gear} and {b.gear} have opposite hands; {why}.")
            return
        if not want_same and same:
            why = ("a ring and its pinion facing opposite ways take opposite typed hands, since one is turned over"
                   if ring else "gears on parallel shafts take opposite hands")
            _error(report, where, f"{a.gear} and {b.gear} are both {ga.hand or 'right'}-handed; {why}.")
            return

    pinion, other = (a, b) if not a.internal else (b, a)
    try:
        if a.internal or b.internal:
            if other.teeth <= pinion.teeth:
                _error(report, where, f"the ring {other.gear} has {other.teeth} teeth and {pinion.gear} "
                                      f"{pinion.teeth}; a ring needs more teeth than the gear inside it.")
                return
            needed, _, epsilon = pairs.describe(a.module, pinion.teeth, other.teeth, pa_a, beta, mesh="internal")
            shifts = (getattr(pinion.derived, "shift", 0.0) or 0.0, getattr(other.derived, "shift", 0.0) or 0.0)
            few = other.teeth - pinion.teeth < internal_gears.CLASH_CHECK_BELOW
            if any(shifts):
                # A shifted pinion (a ring refuses a shift today) meshes at its own working distance, not the plain
                # one pairs.describe gives a pinion inside a ring.
                try:
                    needed = internal_working_centre(a.module, pinion.teeth, other.teeth, pa_a, beta, *shifts)
                except ValueError:
                    _error(report, where, f"{a.gear} and {b.gear}: a profile shift of {shifts[0]:+g} on "
                                          f"{pinion.gear} is too much for it to mesh inside {other.gear} at all.")
                    unshift = None if planetary_mesh else fixes_mod.unshift_fix(spec, pinion, other, CENTRE_TOLERANCE)
                    if unshift is not None:
                        report.fixes[where] = [unshift]
                    return
                if few:
                    _warning(report, where, f"{pinion.gear}'s tips against {other.gear}'s could not be checked: the "
                                            f"check knows plain teeth only, and {pinion.gear} is shifted with "
                                            f"{other.teeth - pinion.teeth} teeth between them; check the pair in "
                                            "SolidWorks after the build, or use plain teeth or a ring with more "
                                            "teeth.")
            elif few:
                _check_ring_tips(report, where, pinion, other, pa_a, beta)
        else:
            needed, _, epsilon = pairs.describe(a.module, a.teeth, b.teeth, pa_a, beta,
                                                shift_1=getattr(a.derived, "shift", 0.0),
                                                shift_2=getattr(b.derived, "shift", 0.0))
    except ValueError as exc:
        _error(report, where, f"{a.gear} and {b.gear}: {exc}")
        return
    if _printed(a, b):
        _check_printed_clearance(report, where, a, b, pinion, other, pa_a, beta)
    placed_at = geometry.centre_distance(a, b)
    report.centres[(a.gear, b.gear)] = (needed, placed_at)
    report.contact[(a.gear, b.gear)] = epsilon
    off = placed_at - needed
    if abs(off) > CENTRE_TOLERANCE:
        shafts = {s.id: s for s in spec.shafts}
        tail = ("; no fix is offered for a planetary stage, whose three gears and copies must change together."
                if planetary_mesh else ".")
        off_error = Diagnostic(
            ERROR, f"{where}: {a.gear} and {b.gear} are {_n(placed_at)} apart; their teeth make {_n(needed)} "
                   f"({'+' if off > 0 else '−'}{_n(abs(off))} mm). Check the {_plane_cells(a)} of {a.shaft} and {b.shaft} "
                   f"(Shafts rows {shafts[a.shaft].row} and {shafts[b.shaft].row}); a shaft at an angle is "
                   f"best placed by formula{tail}", where)
        report.diagnostics.append(off_error)
        report.off_centre.append(off_error)
        if planetary_mesh:
            return                                 # W7-PLAN §2.3 item 6 (review M3): no fix on a planetary mesh
        offered = []
        move = fixes_mod.move_fix(spec, a, b, needed)
        if move is not None:
            offered.append(move)
        shift = fixes_mod.shift_fix(spec, a, b)
        if shift is None and (a.internal or b.internal):
            shift = fixes_mod.unshift_fix(spec, pinion, other, CENTRE_TOLERANCE)
        if shift is not None:
            offered.append(shift)
        if offered:
            report.fixes[where] = offered
    overlap = geometry.faces_overlap(a, b)
    if overlap <= 0:
        _error(report, where, f"{a.gear} and {b.gear} do not meet along the axis: their faces are {_n(-overlap)} mm "
                              "apart. Check their At.")
    elif a.herringbone and abs(a.z - b.z) > CENTRE_TOLERANCE:
        _error(report, where, f"{a.gear} and {b.gear} are herringbones whose middles are {_n(abs(a.z - b.z))} mm "
                              "apart along the axis; a herringbone pair meshes middle to middle.")


def _printed(a: Placed, b: Placed) -> bool:
    """Whether a pair is printed (F1): either gear's derived gear says so (its ``printed`` property, its nozzle set),
    which is the Box's Process, one for the whole gearbox. A machined pair is told nothing new."""
    return bool(getattr(a.derived, "printed", False) or getattr(b.derived, "printed", False))


def _printed_clearance_warning(report: Report, where: str, a: Placed, b: Placed, clearance: float,
                               shifted: bool) -> None:
    """F1 (PLAN-PRINTED §2.2; F1-INTERFACES §8): a printed pair's tip clearance under the 0.3 mm two printed surfaces
    take (less a rounding tolerance: module 0.75's computes as 0.2999999999999998), at its Meshes row, in the words
    the form says it in (package A's ``pair.printed_clearance_sentence``), prefixed with the pair as this file
    prefixes its sentences. The depth is left alone; the advice names less profile shift only when the pair has a
    shift to take off."""
    sentence = pairs.printed_clearance_sentence(clearance, shifted)
    if sentence:
        _warning(report, where, f"{a.gear} and {b.gear}: {sentence}")


def _check_printed_clearance(report: Report, where: str, a: Placed, b: Placed, pinion: Placed, other: Placed,
                             pressure_angle: float, beta: float) -> None:
    """A printed pair on parallel shafts: its tip clearance at the working centre distance, by
    ``pair.tip_clearance`` outside and ``pair.ring_tip_clearance`` for a pinion in a ring (package A's maths). A
    shift the pair maths cannot answer is said elsewhere in this file, so nothing is said here."""
    shift_a, shift_b = (getattr(g.derived, "shift", 0.0) or 0.0 for g in (a, b))
    try:
        if a.internal or b.internal:
            clearance = pairs.ring_tip_clearance(a.module, pinion.teeth, other.teeth, pressure_angle, beta,
                                                 getattr(pinion.derived, "shift", 0.0) or 0.0,
                                                 getattr(other.derived, "shift", 0.0) or 0.0)
        else:
            clearance = pairs.tip_clearance(a.module, a.teeth, b.teeth, pressure_angle, beta, shift_a, shift_b)
    except (ValueError, ArithmeticError):
        return
    _printed_clearance_warning(report, where, a, b, clearance, bool(shift_a or shift_b))


def internal_working_centre(module: float, pinion_teeth: int, ring_teeth: int, pressure_angle: float,
                            helix_angle: float = 0.0, pinion_shift: float = 0.0, ring_shift: float = 0.0) -> float:
    """Where a pinion and the ring round it mesh without play from the flanks, mm, with their profile shifts:
    ``inv αw = inv α + 2 tan αn (x_ring − x_pinion) / (z_ring − z_pinion)`` and ``a_w = mt (z_ring − z_pinion) / 2 ·
    cos α / cos αw``, transverse values for a helical pair (``α`` the transverse pressure angle, ``αn`` the normal
    one, ``mt = m / cos β``), as :func:`gears.spur.working_pressure_angle` writes the outside pair's. Unshifted it
    is the plain ``mt (z_ring − z_pinion) / 2``. ``ring_shift`` keeps the formula whole, but a ring refuses a
    profile shift today, so it is always 0. A pinion shift no angle answers is a ValueError with a sentence."""
    mt = module / math.cos(math.radians(helix_angle))
    alpha = math.radians(helical.transverse_pressure_angle(pressure_angle, helix_angle) if helix_angle
                         else pressure_angle)
    plain = mt * (ring_teeth - pinion_teeth) / 2.0
    difference = ring_shift - pinion_shift
    if not difference:
        return plain
    tan_normal = math.tan(math.radians(pressure_angle))
    value = spur.inv(alpha) + 2.0 * tan_normal * difference / (ring_teeth - pinion_teeth)
    if value <= 0.0:
        raise ValueError(f"A profile shift of {pinion_shift:+g} on a {pinion_teeth}-tooth pinion is too much for it to "
                         f"mesh inside a {ring_teeth}-tooth ring at all.")
    return plain * math.cos(alpha) / math.cos(spur.inv_inverse(value))


def _check_ring_tips(report: Report, where: str, pinion: Placed, ring: Placed, pressure_angle: float,
                     beta: float) -> None:
    """A pinion whose tips run into the ring's as they turn (``internal.tip_clash``: standard teeth, a tooth
    difference under ``internal.CLASH_CHECK_BELOW``), as the pair solver judges a ring: a warning, since the model
    leaves backlash out."""
    mt = pinion.module / math.cos(math.radians(beta))
    alpha = helical.transverse_pressure_angle(pressure_angle, beta) if beta else pressure_angle
    try:
        depth = internal_gears.tip_clash(mt, pinion.teeth, ring.teeth, alpha)
    except ValueError:
        return
    if depth > internal_gears.CLASH_TOLERANCE:
        _warning(report, where, f"{pinion.gear}'s teeth run {_n(depth)} mm into {ring.gear}'s as they turn: "
                                f"{ring.teeth - pinion.teeth} teeth between a ring and its pinion are too few for "
                                "plain teeth; give the ring more teeth or the pinion fewer.")


def _check_clearances(report: Report, spec: GearboxSpec, placed: Dict[str, Placed], listed, *, only=None,
                      said=frozenset()) -> None:
    """Gears on different shafts that do not mesh, and share some height: they must not touch. W8: a sleeve and a
    dog are never judged here (engagement owns them, ``modes.engagement``: a coaxial pair is engaged whole, apart, or
    an error); ``only`` limits the pairs to those with one of its gears (another mode's sliders), and a sentence in
    ``said`` is not said twice."""
    gears = {g.id: g for g in spec.gears}
    clutch = {g.id: g.kind_word() for g in spec.gears if g.kind_word() in modes_mod.CLUTCH_KINDS}
    start = len(report.diagnostics)
    for a, b in combinations(placed.values(), 2):
        if only is not None and a.gear not in only and b.gear not in only:
            continue
        if {clutch.get(a.gear), clutch.get(b.gear)} in ({modes_mod.SLEEVE, modes_mod.DOG},
                                                         {modes_mod.SLEEVE, modes_mod.HUB}):
            continue                                   # W9b: a sleeve over a hub is engagement's to judge too
        if a.shaft == b.shaft or frozenset((a.gear, b.gear)) in listed or not geometry.parallel(a, b):
            continue                                   # across an angle: _check_turned_clearances
        if a.carrier and a.row == b.row and a.carrier == b.carrier:
            continue                                   # copies of one planet: _check_stages' room round the carrier
        if geometry.faces_overlap(a, b) <= 0:
            continue
        d = geometry.centre_distance(a, b)
        gap = CLASH_GAP * max(a.module, b.module)
        where = spec.cell("Gears", gears[b.row or b.gear].row, "shaft")
        if a.internal and b.internal:
            continue
        if a.internal or b.internal:
            ring, g = (a, b) if a.internal else (b, a)
            if d - g.outer_radius >= ring.outer_radius + gap:
                continue                                    # wholly outside the ring, with room to spare
            if d - g.outer_radius >= ring.outer_radius - gap and d > ring.outer_radius:
                _error(report, where, f"{g.gear} is less than {_n(gap)} mm from {ring.gear}'s rim.")
                continue
            near = abs(d - (ring.derived.d - g.derived.d) / 2.0) < NEAR_MESH_BAND * g.module
            if near and abs(ring.module - g.module) < 1e-9:
                _warning(report, where, f"{g.gear} sits where it would mesh inside {ring.gear}: list them on "
                                        "Meshes, or move one.")
            elif d + g.outer_radius > ring.tip_radius - gap:
                _error(report, where, f"{g.gear} reaches {ring.gear}'s teeth: there is less than {_n(gap)} mm "
                                      f"between them.")
            continue
        near = abs(d - (a.derived.d + b.derived.d) / 2.0) < NEAR_MESH_BAND * max(a.module, b.module)
        if near and abs(a.module - b.module) < 1e-9:
            _warning(report, where, f"{a.gear} and {b.gear} sit where they would mesh: list them on Meshes, or "
                                    "move one.")
        elif d < a.outer_radius + b.outer_radius + gap:
            _error(report, where, f"{a.gear} and {b.gear} clash: {_n(d)} mm apart, with tips reaching "
                                  f"{_n(a.outer_radius + b.outer_radius)} mm and less than {_n(gap)} mm to spare.")
    if said:
        report.diagnostics[start:] = [d for d in report.diagnostics[start:] if d.message not in said]


def _hands(a: Placed, b: Placed) -> str:
    word = {1: "right", -1: "left"}
    beta_a, beta_b = _n(a.derived.helix_angle_deg), _n(b.derived.helix_angle_deg)
    if a.hand_sign == b.hand_sign:
        return f"both {word[a.hand_sign]}-handed at {beta_a}° and {beta_b}°"
    return f"{word[a.hand_sign]}- and {word[b.hand_sign]}-handed at {beta_a}° and {beta_b}°"


def _check_turned(report: Report, spec: GearboxSpec, a: Placed, b: Placed, laid: "geometry.MeshGeometry",
                  where: str) -> bool:
    """A mesh across an angle (W6-PLAN §2.5, the sentences of §2.9). Whether it may go into the speeds and phases
    (no error that leaves its geometry meaningless)."""
    gears = {g.id: g for g in spec.gears}
    ga, gb = gears[a.gear], gears[b.gear]
    kind_a, kind_b = ga.kind_word(), gb.kind_word()
    angle = _n(laid.shaft_angle)
    for ring in (a, b):
        if ring.internal:
            _error(report, where, f"{ring.gear} is a ring, and a ring meshes only on a parallel shaft.")
            return False
    if kind_a != kind_b:
        _error(report, where, f"{a.gear} is {kind_a} and {b.gear} is {kind_b}; meshing gears are the same kind.")
        return False
    if kind_a == "herringbone":
        _error(report, where, f"{a.gear} and {b.gear} are herringbone gears on crossed shafts; only helical gears mesh "
                              "on crossed shafts.")
        return False
    if kind_a not in ("bevel", "helical"):
        _error(report, where, f"{a.gear} and {b.gear} are {kind_a} gears on shafts at {angle}°; across an angle only "
                              "bevel gears (on shafts that meet) and helical gears (on crossed shafts) mesh.")
        return False
    if abs(a.module - b.module) > 1e-9:
        _error(report, where, f"{a.gear} has module {_n(a.module)} and {b.gear} {_n(b.module)}; meshing gears "
                              "share one module.")
        return False
    pa_a = float(ga.pressure_angle or spec.box.pressure_angle_text())
    pa_b = float(gb.pressure_angle or spec.box.pressure_angle_text())
    if abs(pa_a - pa_b) > 1e-9:
        _error(report, where, f"{a.gear}'s pressure angle is {_n(pa_a)}° and {b.gear}'s {_n(pa_b)}°; meshing "
                              "gears share one.")
        return False
    if kind_a == "bevel":
        if _printed(a, b):
            # Gleason's clearance (0.188 × module, the same along the face), by the form's own figure (F1 review, S4).
            _printed_clearance_warning(report, where, a, b, pairs.bevel_tip_clearance(a.derived, b.derived), False)
        if laid.placed > CENTRE_TOLERANCE:
            shafts = {x.id: x for x in spec.shafts}
            point = geometry._add(b.centre, b.axis, -float(gb.at or 0))
            foot_a, foot_b = geometry.lines_closest(a.centre, a.axis, b.centre, b.axis)
            apart = geometry._norm(geometry._sub(foot_b, foot_a))
            text = (f"{a.gear} and {b.gear} are bevel gears whose cone tips are {_n(laid.placed)} mm apart; they mesh "
                    "only with their tips together")
            if apart > CENTRE_TOLERANCE:
                text += f", and their shafts do not meet: they pass {_n(apart)} mm apart."
            else:
                at = geometry._dot(geometry._sub(a.centre, point), b.axis)
                text += f". {b.gear}'s At would be {_n(at)} to put its tip on {a.gear}'s."
            del shafts
            _error(report, where, text)
            return False
        return True
    # crossed helical gears
    if laid.problem == "meet":
        _error(report, where, f"{a.gear} and {b.gear} are helical gears on shafts that meet; across an angle helical "
                              "gears mesh only on crossed shafts that pass apart, and gears on shafts that meet are "
                              "bevel gears.")
        return False
    if getattr(a.derived, "shift", 0.0) or getattr(b.derived, "shift", 0.0):
        _error(report, where, f"{a.gear} and {b.gear} are crossed helical gears with profile shift; crossed gears are "
                              "built without it: set both shifts to 0.")
        return False
    if _printed(a, b):
        # Unshifted, each tip stands the depth less two addenda from the other's root, whatever the helix angles.
        try:
            _printed_clearance_warning(report, where, a, b, pairs.tip_clearance(a.module, a.teeth, b.teeth, pa_a),
                                       False)
        except (ValueError, ArithmeticError):
            pass
    tilt = geometry._reduce_line(-(a.hand_sign * a.derived.helix_angle_deg + b.hand_sign * b.derived.helix_angle_deg))
    lines = min(laid.shaft_angle, 180.0 - laid.shaft_angle)
    foot_a, foot_b = geometry.lines_closest(a.centre, a.axis, b.centre, b.axis)
    e = geometry._unit(geometry._sub(foot_b, foot_a))
    turned = geometry.signed_crossing(a.axis, b.axis, e)
    if abs(abs(tilt) - lines) > 1e-6:
        _error(report, where, f"{a.gear} and {b.gear} are {_hands(a, b)}, so their shafts must cross at "
                              f"{_n(abs(tilt))}°; they cross at {_n(lines)}°.")
        return False
    if abs(tilt - turned) > 1e-6:
        _error(report, where, f"{a.gear} and {b.gear} are {_hands(a, b)}, so, seen along the line from {a.gear} to "
                              f"{b.gear}, {b.gear}'s shaft must be turned {_n(tilt)}° from {a.gear}'s; it is turned "
                              f"{_n(turned)}°.".replace("-", "\u2212"))
        return False
    ok = True
    off = laid.placed - laid.needed
    if abs(off) > CENTRE_TOLERANCE:
        shafts = {x.id: x for x in spec.shafts}
        _error(report, where, f"{a.gear} and {b.gear} are {_n(laid.placed)} mm apart where their shafts pass closest; "
                              f"their teeth make {_n(laid.needed)} ({'+' if off > 0 else '−'}{_n(abs(off))} mm). Check "
                              f"the place of {b.shaft} (Shafts row {shafts[b.shaft].row}); a shaft at an angle is best "
                              "placed by formula.")
        ok = False
    for gear, other in ((a, b), (b, a)):
        height = geometry._dot(geometry._sub(laid.contact, gear.centre), gear.axis)
        if abs(height) > gear.face / 2.0 + 1e-9:
            _error(report, where, f"{gear.gear}'s face does not reach where {other.gear} touches it: that point is "
                                  f"{_n(abs(height))} mm along {gear.shaft} from {gear.gear}'s middle, and its face is "
                                  f"{_n(gear.face)} mm wide.")
            ok = False
    return ok


def _check_turned_clearances(report: Report, spec: GearboxSpec, placed: Dict[str, Placed], listed) -> None:
    """Gears, and shafts as the span of their gears, across an angle (W6-PLAN §2.5, D8): their true bounding
    cylinders within ``CLASH_GAP`` × module are a warning, never an error — the bound over-reaches a toothed
    blank, and the build's interference check is the judge. A bevel gear's partner shaft is exempt."""
    gears = {g.id: g for g in spec.gears}
    partners = {(m.a, m.b) for m in spec.meshes} | {(m.b, m.a) for m in spec.meshes}
    for a, b in combinations(placed.values(), 2):
        if a.shaft == b.shaft or geometry.parallel(a, b) or frozenset((a.gear, b.gear)) in listed:
            continue
        gap = geometry.cylinder_gap(a, b)
        if gap < CLASH_GAP * max(a.module, b.module):
            where = spec.cell("Gears", gears[b.row or b.gear].row, "shaft")
            _warning(report, where, f"{a.gear} and {b.gear} may touch: on shafts at {_n(geometry.angle_between_axes(a, b))}°, "
                                    f"their blanks come within {_n(gap)} mm of each other; the build's interference "
                                    "check says for certain.")
    shafts = sorted({p.shaft for p in placed.values()})
    for shaft in shafts:
        span = geometry.shaft_span(placed, shaft)
        mine = [p for p in placed.values() if p.shaft == shaft]
        for g in placed.values():
            if g.shaft == shaft or geometry.parallel(g, mine[0]):
                continue
            if g.bevel and any((g.gear, m.gear) in partners and m.bevel for m in mine):
                continue                               # the partner's axis runs through every bevel blank's apex region
            gap = geometry.solid_gap(span, geometry.bounding_cylinder(g))
            if gap < CLASH_GAP * g.module:
                where = spec.cell("Gears", gears[g.row or g.gear].row, "shaft")
                _warning(report, where, f"{shaft} may touch {g.gear}: on shafts at "
                                        f"{_n(geometry.angle_between_axes(g, mine[0]))}°, the shaft comes within "
                                        f"{_n(gap)} mm of its blank; the build's interference check says for certain.")


def _check_shafts(report: Report, spec: GearboxSpec, placed: Dict[str, Placed], upset=frozenset()) -> None:
    gears_on: Dict[str, List[Placed]] = {}
    for p in placed.values():
        gears_on.setdefault(p.shaft, []).append(p)
    carriers = planetary.carriers(spec) if any(p.carrier for p in placed.values()) else []
    on_carrier_axis = set()
    if carriers:
        # W7-PLAN §2.3 item 5 (review S4): shafts on a carrier's axis (sun, carrier, ring, coaxial frame shafts)
        # pass over each other's axes by design, and a carrier needs no gear of its own.
        on_carrier_axis = {x.id for x in spec.shafts if x.mount() == "frame" and x.id
                           and any(planetary.coaxial(spec, x.id, c) for c in carriers)}
    on_carrier_axis |= _in_line(spec)
    for shaft in spec.shafts:
        if shaft.id and not any(g.shaft == shaft.id for g in spec.gears) and shaft.id not in carriers:
            _warning(report, spec.cell("Shafts", shaft.row, "id"), f"{shaft.id} carries no gear.")
    # A gear whose metal passes over another shaft's line, within the height that shaft's gears span.
    for g in placed.values():
        for shaft_id, on in gears_on.items():
            if shaft_id == g.shaft or not geometry.parallel(g, on[0]):
                continue                               # a shaft across an angle: _check_turned_clearances
            if g.shaft in on_carrier_axis and shaft_id in on_carrier_axis:
                continue                           # one line by design: a carrier's axis, or shafts a sleeve joins
            if carriers and (planetary.copy_of(g.shaft)[0] in upset or shaft_id in upset):
                continue                               # a member off its carrier's axis: said once, at its mesh
            lo = min(p.z_range[0] for p in on)
            hi = max(p.z_range[1] for p in on)
            if min(g.z_range[1], hi) - max(g.z_range[0], lo) <= 0:
                continue
            other = on[0]
            d = ((other.x - g.x) ** 2 + (other.y - g.y) ** 2) ** 0.5
            inside_metal = (g.tip_radius <= d <= g.outer_radius) if g.internal else d < g.outer_radius
            if inside_metal and carriers and d < CENTRE_TOLERANCE:
                continue                               # coaxial shafts of a planetary stage: never "0 mm from its own"
            if inside_metal:
                row = {x.id: x.row for x in spec.gears}[g.row or g.gear]
                _warning(report, spec.cell("Gears", row, "id"),
                         f"{g.gear} passes over {shaft_id}'s axis, {_n(d)} mm from its own: a real shaft there "
                         "would be cut.")


def _in_line(spec: GearboxSpec) -> set:
    """W8 (decided deliberately, after the interface review): frame shafts on one line that a sleeve joins — a
    sleeve's shaft and the shafts of the dogs on its axis — are coaxial by design, as a carrier's members are, and
    pass over each other's axes without a warning. Every other coaxial pair keeps W3's warning."""
    shafts = {s.id: s for s in spec.shafts if s.id and s.mount() == "frame"}
    point = {}
    for sid, s in shafts.items():
        try:
            point[sid] = (float(s.x or 0), float(s.y or 0))
        except ValueError:
            continue
    out = set()
    for sleeve in (g for g in spec.gears if g.kind_word() == modes_mod.SLEEVE and g.shaft in point):
        for dog in (g for g in spec.gears if g.kind_word() == modes_mod.DOG and g.shaft in point):
            if dog.shaft != sleeve.shaft and point[dog.shaft] == point[sleeve.shaft]:
                out.update({sleeve.shaft, dog.shaft})
    return out


def _check_motion(report: Report, spec: GearboxSpec, upset=frozenset()) -> None:
    motion = report.motion
    # W8: the one home of the whole-box jam. With modes, ``report.motion`` is the first mode's, and a mode that jams
    # is said at its own Modes row (``_mode_report``); the box "cannot turn at all" only when every mode jams, so what
    # is said never depends on the order of the Modes rows.
    named = [m for m in report.modes if m.name]
    jammed = all(m.motion.jammed for m in named) if named else bool(motion.jammed)
    if jammed:
        if not planetary.second_inputs(spec):     # W7 §6.15: two inputs on a stage are said once, at the Role cell
            _error(report, "Meshes", motion.jammed)
        return
    if named and motion.jammed:
        motion = next(m.motion for m in named if not m.motion.jammed)
    if not spec.meshes:
        return                                  # parts only: nothing turns anything, and that is fine
    if not any(s.role == "input" and s.speed for s in spec.shafts):
        _error(report, "Shafts", "the gears mesh, but no shaft is an input with a speed: set one shaft's Role to "
                                 "input and give it a Speed.")
        return
    gears_meshed = {g for m in spec.meshes for g in (m.a, m.b)}
    meshed_shafts = {g.shaft for g in spec.gears if g.id in gears_meshed}
    free_everywhere = set(motion.free)
    for m in report.modes:                          # W8 (J16): free in some mode is the Speeds panel's to say
        free_everywhere &= set(m.motion.free)
    for shaft in spec.shafts:
        if shaft.id not in free_everywhere or shaft.id in upset:
            continue
        where = spec.cell("Shafts", shaft.row, "id")
        if report.modes and any(m.name for m in report.modes):      # W8: across the modes
            if shaft.id in meshed_shafts:
                _error(report, where, f"nothing settles {shaft.id}'s speed in any mode: no input reaches it through "
                                      "the meshes and couplings, so the box needs another input (or a fixed shaft) "
                                      "to be driven.")
            elif shaft.role == "output":
                _warning(report, where, f"nothing drives {shaft.id} in any mode: no input reaches it through the "
                                        "meshes and couplings.")
        elif shaft.id in meshed_shafts:
            _error(report, where, f"nothing settles {shaft.id}'s speed: no input reaches it through the meshes, "
                                  "so the box needs another input (or a fixed shaft) to be driven.")
        elif shaft.role == "output":
            _warning(report, where, f"nothing drives {shaft.id}: no input reaches it through the meshes.")


def _driven_from(spec: GearboxSpec, start: str) -> set:
    """Every shaft the meshes join to ``start``: gears on one shaft are one body, and a mesh joins two shafts."""
    shaft_of = {g.id: g.shaft for g in spec.gears}
    joins: Dict[str, set] = {}
    for mesh in spec.meshes:
        a, b = shaft_of.get(mesh.a), shaft_of.get(mesh.b)
        if a and b:
            joins.setdefault(a, set()).add(b)
            joins.setdefault(b, set()).add(a)
    for shaft in spec.shafts:                       # W7: a planet shaft and its carrier turn together
        if shaft.mount() != "frame" and shaft.id:
            joins.setdefault(shaft.id, set()).add(shaft.mount())
            joins.setdefault(shaft.mount(), set()).add(shaft.id)
    seen, todo = {start}, [start]
    while todo:
        for other in joins.get(todo.pop(), ()):
            if other not in seen:
                seen.add(other)
                todo.append(other)
    return seen


NO_ENDS = "no input and output that both turn"
NBSP = "\u00a0"            # a no-break space: what holds one mode's "2H 1.000 : 1" together in Worked out as


def _ends(spec: GearboxSpec, motion: kinematics.Motion):
    """(the first input that turns, the first output the meshes join to it and that turns, why there is no pair).

    The output is looked for among those the meshes reach from that input: two
    separate trains in one workbook have no ratio between them, whatever their
    speeds divide to."""
    inputs = [s for s in spec.shafts if s.role == "input" and s.id in motion.speeds]
    outputs = [s for s in spec.shafts if s.role == "output" and motion.speeds.get(s.id)]
    if not inputs or not outputs:
        return None, None, NO_ENDS
    reached = _driven_from(spec, inputs[0].id)
    joined = [s for s in outputs if s.id in reached]
    if not joined:
        named = ", ".join(s.id for s in outputs)
        which = "the output" if len(outputs) == 1 else "an output"
        return None, None, f"no meshes join {inputs[0].id} to {which}, {named}"
    return inputs[0], joined[0], ""


MODE_KINDS = ("sleeve", "dog")


def overall_ratio(spec: GearboxSpec, report: Report) -> Tuple[Optional[float], str, str]:
    """(input speed ÷ output speed, which shafts it is between, why there is none).

    ``(12.0, "S1 to S3", "")`` for the 12 : 1 reducer: the first input to the
    first output the meshes join to it. It is withheld — ``(None, "", why)`` — whenever a gear that
    would change it is not in the sums: a gearbox not checked yet, a meshing
    gear that was not laid out (an error of its own, or a later phase's kind),
    or a box whose power path changes with its modes (sleeves, dogs, sliding
    gears, the Modes sheet), so it is never a confident wrong number.
    """
    if report.unchecked:
        return None, "", "the gearbox is not checked yet"
    meshed = {g for m in spec.meshes for g in (m.a, m.b)}
    laid_out = {p.row or p.gear for p in report.layout.placed.values()}       # W7: a planet's copies are its row
    missing = [g.id for g in spec.gears if g.id in meshed and g.id not in laid_out]
    if missing:
        one = len(missing) == 1
        return None, "", f"{', '.join(missing)} {'meshes but is' if one else 'mesh but are'} not laid out"
    if report.modes:
        # W8: the ratio is each mode's (``ModeReport.ratio``, :func:`mode_ratio`); the box's is its first mode's.
        first = report.modes[0]
        if first.ratio is None:
            return None, "", first.ratio_why
        return first.ratio, f"{first.ends[0]} to {first.ends[1]}", ""
    if spec.modes or any(g.kind_word() in MODE_KINDS or g.slides.strip() for g in spec.gears):
        return None, "", "it changes with the modes"
    motion = report.motion
    first, last, why = _ends(spec, motion)
    if first is None:
        return None, "", why
    return abs(float(motion.speeds[first.id] / motion.speeds[last.id])), f"{first.id} to {last.id}", ""


def _worked_out_as(spec: GearboxSpec, report: Report) -> str:
    """``Parallel train · 2 meshes · 12.000 : 1`` — what the rows add up to. W7: ``Planetary, R fixed · 3 planets ·
    4.000 : 1 · output turns the same way`` (``Planetary and parallel, …`` with meshes off the stage)."""
    kinds = [m.kind for m in report.meshes.values()]
    meshes = len(report.meshes) if report.meshes else len(report.centres)
    pieces = ["Parallel train", f"{meshes} mesh{'es' if meshes != 1 else ''}"]
    turned = [k for k in (geometry.CROSSED, geometry.BEVEL) if k in kinds]
    if report.stages:
        stage = report.stages[0]
        in_stage = {stage.sun, stage.planet, stage.ring}
        others = [m for m in spec.meshes if not {m.a, m.b} <= in_stage]
        held = f", {stage.held} fixed" if stage.held else ""
        pieces = [f"Planetary{' and parallel' if others else ''}{held}",
                  f"{stage.copies} planet{'s' if stage.copies != 1 else ''}"]
    elif turned:
        words = [k.capitalize() if i == 0 else k for i, k in enumerate(turned)]
        if geometry.PARALLEL in kinds:
            words.append("parallel")
        pieces[0] = " and ".join(words) + " train" if len(words) > 1 else words[0] + " train"
    elif report.modes:
        pieces[0] = "Parallel train with modes"
    elif any(p.internal for p in report.layout.placed.values()):
        pieces[0] = "Parallel train with a ring"
    if report.modes and report.modes[0].name:
        # W8-PLAN §1.4: each mode's ratio, from the one home (ModeReport.ratio); "neutral" with no output turning.
        meshes = len([m for m in spec.meshes if not ({m.a, m.b} & {g.id for g in spec.gears
                                                                    if g.kind_word() in MODE_KINDS})])
        pieces[1] = f"{meshes} mesh{'es' if meshes != 1 else ''}"
        if report.stages:
            head, comma, held = pieces[0].partition(",")
            pieces[0] = f"{head} with modes{comma}{held}"
            pieces[1] = f"{report.stages[0].copies} planet{'s' if report.stages[0].copies != 1 else ''}"
        # Each mode is one unit, joined inside by no-break spaces ("2H 1.000 : 1"), so a line wrapped at a cell's
        # width breaks only between modes. Export writes them back as ordinary spaces (export.results_sheet).
        said = ", ".join(f"{m.name}{NBSP}{m.ratio:.3f}{NBSP}:{NBSP}1" if m.ratio is not None
                         else f"{m.name}{NBSP}{m.ratio_why}" for m in report.modes)
        return " · ".join(pieces + [said])
    motion = report.motion
    ratio, _, why = overall_ratio(spec, report)
    if ratio is None and why != NO_ENDS:
        pieces.append(f"no overall ratio: {why}")       # said, so a ratio's absence is never read as an oversight
    if ratio is not None:
        ends = _ends(spec, motion)
        pieces.append(f"{ratio:.3f} : 1")
        placed = report.layout.placed
        first = next((p for p in placed.values() if p.shaft == ends[0].id), None)
        last = next((p for p in placed.values() if p.shaft == ends[1].id), None)
        if first is not None and last is not None and not geometry.parallel(first, last):
            pieces.append(f"output at {_n(geometry.angle_between_axes(first, last))}° to the input")
        else:
            same = motion.turns(ends[0].id) == motion.turns(ends[1].id)   # seen from the shared family's + end
            pieces.append("output turns the same way" if same else "output turns the other way")
    return " · ".join(pieces)
