"""What each Meshes row's teeth take, mode by mode, against what they are rated to take (PLAN-PRINTED §5.2, §5.4).

**Package B's, over F4-0's stub** (docs/notes-printed/F4-INTERFACES.md §4): F4-0 fixed the names below, which package
C's boards and the Results block read; B wrote the bodies and added only after them (a seventh state, its wording and
the helpers the Results block and the warning share). Nothing here is read for a machined gearbox, nor for one whose
first input has no torque: :func:`mesh_strengths` then gives ``()``, so nothing is said and no Results block is
written.

The figures come from :mod:`gear_generator.gears.strength` (F4-0's, package A's maths, whole): ``rate``, ``holds``
(with the mesh's width and ``two_way``), ``PLANET_SHARE``, ``TWO_WAY`` and the rounding helpers, so the workbook and the
form round alike.

**The force on each mesh** (§5.2), from the assessment's own torques, ``report.motion`` with no modes or each
``ModeReport.motion``, with ``kinematics.py`` unchanged:

1. a Meshes row on parallel shafts is *loaded* in a mode only when both its gears' shafts carry a torque there, in
   ``torques`` (0 counting: an idler, a planet) or in ``held``;
2. a planetary mesh (one gear on a carrier) takes the member's torque, sun or ring, over ``d · N``, × ``PLANET_SHARE``
   for two planets or more;
3. any other takes the larger of ``2000 T / d`` over its two gears whose shaft carries a torque above 0; a shaft
   driving two meshes gives each its whole torque;
4. an idler (a gear whose shaft carries exactly 0 and is no planet) passes on the largest force its non-idler mates
   give it, and a chain of idlers shares one figure.

Each gear is rated to take ``holds(rating, allowable, width=b, two_way=…)``, ``b`` the faces' overlap and no more than
either toothed width, two-way when its shaft carries exactly 0 in that mode (R1: an allowance for running, never part of
a figure called *once*). The share is the force over the smaller figure, that gear the weaker. A ring whose tips lie
inside its base circle is not rated (M1): the share then counts the gear that rates alone, a true lower bound, and the
ring is named in ``unrated``.

**A mesh that is not loaded** is told apart by why (the review's S3; *no torque here* is never said):

- ``NOT_SHARED``: a shaft of it lies past a shared output (``Motion.past_split``), whose torque kinematics does not
  share out (J17): it carries torque, and its share is not worked out;
- ``UNWORKED`` (B's, past the stub's six): both its shafts turn and its branch reaches a turning output without
  passing a loaded shaft, yet kinematics gives it no torque (a W3 split, one shaft driving two branches; a stage with
  nothing held). It carries torque too, and is not worked out;
- ``UNLOADED``: anything else, a shaft that does not turn (a free member), a stage that idles, a branch reaching no
  output (J17's pruning): it *turns unloaded here*.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from ..gears import kind_for, strength
from ..gears.strength import ToothRating
from . import geometry, model, planetary
from .schema import FRAME

# The states of one Meshes row in one mode (§5.2, §5.4; the review's S3).
RATED = "rated"                    # loaded here, at least one of its gears rated: force, weaker, share
UNLOADED = "unloaded"              # not loaded here: a stage that idles, a branch reaching no output, a free member
NOT_SHARED = "not shared"          # loaded past a shared output, which kinematics does not share out (J17)
NOT_RATED = "not rated"            # loaded here, and neither gear rates
BEVEL = "bevel"                    # a bevel pair: never rated (§5.1)
CROSSED = "crossed"                # a crossed helical pair: never rated (§5.1)
# B's, after the stub's six: turning and reaching an output, but given no torque by kinematics (a W3 split, a stage
# with nothing held). Loaded, and not worked out; never *turns unloaded here*.
UNWORKED = "not worked out"

# The Results block's wordings where no force is worked out (§5.4), never *no torque here*.
TURNS_UNLOADED = "turns unloaded here"
NOT_SHARED_OUT = "the torque past a shared output is not shared out (not worked out)"
NOT_GIVEN = "the torque here is not given (past a split, not worked out)"          # B's, for UNWORKED

# The Results block's words (F4-INTERFACES §6.3) and the warning's (§6.1), each in one place.
RESULTS_HEAD = ("Tooth strength (printed)", "Mode", "Force (N)", "Weaker gear", "Rated to take (N)", "Share used (%)")
RESULTS_WORST = "Worst share"
RESULTS_ALLOWABLE = "Allowable stress (MPa)"
ALLOWABLE_TYPED = "the Box's"
ALLOWABLE_BLANK = "blank: provisional, type your own in the Box's Allowable stress"
ALLOWABLE_UNREAD = "the Box's does not read as a figure above zero: provisional, type your own there"
RESULTS_NOTE = ("An estimate for teeth printed flat, the whole load on one tooth's tip: rated to take once, not a running "
                "rating. Heat, wear, creep and load across layers are not worked out.")
PAIR_WORDS = {BEVEL: "a bevel pair", CROSSED: "a crossed pair"}
WHY_NOT_WORKED = {NOT_SHARED: "past a shared output", UNWORKED: "its torque is not given"}
TWO_WAY_MARK = "(0.7)"
PAST_RANGE_MARK = "(stress factor past its range)"
PROVISIONAL = " (provisional: type your own in the Box's Allowable stress)"
REMEDY = ("Use a larger module, a wider face, less torque, or your own tested allowable. An estimate for teeth printed "
          "flat, with the whole load on one tooth's tip: not a running rating; heat, wear and creep are not worked out.")


@dataclass(frozen=True)
class GearSide:
    """One gear's side of a mesh in one mode: its Gears-sheet id, its rating (:func:`strength.rate` of its derived
    gear), what one tooth is rated to take in this mesh at the allowable, N (at the mesh's width, × 0.7 when
    `two_way`; None when the gear is not rated or the mesh is not loaded), and whether its teeth are loaded in both
    directions as the gearbox runs (an idler or a planet: a shaft torque of exactly 0 in this mode)."""

    gear: str
    rating: ToothRating
    held: Optional[float] = None
    two_way: bool = False


@dataclass(frozen=True)
class MeshStrength:
    """One Meshes row in one mode (§5.2). `row` is its Meshes-sheet row; `mode` the mode's name, `""` for a gearbox
    with no modes; `force` Ft at the pitch circle, N (None unless RATED); `width` b, mm, the faces' overlap;
    `sides` the two gears, a then b; `weaker` the id of the rated gear with the smaller figure; `share` Ft over that
    figure, a fraction (1.0 is 100 %); `planets` N for a planetary mesh (the force then shared with K_γ), else 0;
    `unrated` the ids of its gears not rated (a ring whose tips lie inside its base circle), whose share then counts
    the gear that rates alone, a true lower bound."""

    a: str
    b: str
    row: int
    mode: str = ""
    state: str = RATED
    force: Optional[float] = None
    width: float = 0.0
    sides: Tuple[GearSide, ...] = ()
    weaker: str = ""
    share: Optional[float] = None
    planets: int = 0
    unrated: Tuple[str, ...] = ()

    @property
    def name(self) -> str:
        """The mesh as the Results sheet names it, ``Sun–Planet``."""
        return f"{self.a}–{self.b}"

    def side(self, gear: str) -> Optional[GearSide]:
        return next((s for s in self.sides if s.gear == gear), None)


# -- which gearboxes, and the gears as placed ------------------------------------------------------------------------


def _number(text: str) -> float:
    try:
        return float(str(text or "").strip().replace("−", "-"))
    except ValueError:
        return 0.0


def worked_out(spec: Any) -> bool:
    """Whether a gearbox's teeth are worked out at all: printed (its Box's Process, resolved by ``assess`` before
    the checks) and its first input given a torque (§5.4). A machined gearbox is told nothing new."""
    if model.checked_process(spec.box) != "printed":
        return False
    inputs = [s for s in spec.shafts if s.id and s.role == "input" and s.speed]
    return bool(inputs) and _number(inputs[0].torque) != 0.0


def allowable_of(spec: Any) -> Tuple[float, bool]:
    """The allowable the checks use, MPa, and whether it is the Box's own (typed and read) or the provisional 17."""
    typed = model.checked_allowable(spec.box)
    return strength.allowable_mpa(typed), bool(typed)


def _rating(spec: Any, placed: geometry.Placed) -> ToothRating:
    gear_spec = placed.spec
    if gear_spec is None:
        row = spec.gear(placed.row or placed.gear)
        gear_spec = row.gear_spec(spec.box) if row is not None else None
    kind = kind_for(gear_spec) if gear_spec is not None else None
    recipe = kind.recipe_for(gear_spec) if kind is not None else ""
    return strength.rate(placed.derived, recipe)


def _shaft(placed: geometry.Placed) -> str:
    """The shaft's row id, as kinematics keys its torques (a planet copy's ``P copy 2`` is ``P``)."""
    return planetary.copy_of(placed.shaft)[0]


# -- the force, mode by mode -----------------------------------------------------------------------------------------


def _loaded(motion: Any, shaft: str) -> bool:
    return shaft in motion.torques or shaft in motion.held


def _torque(motion: Any, shaft: str) -> float:
    if shaft in motion.torques:
        return float(motion.torques[shaft])
    return float(motion.held.get(shaft, 0.0))


def _reaches_output(spec: Any, links: Dict[str, Set[str]], motion: Any, start: Sequence[str], mesh: Set[str]) -> bool:
    """Whether a shaft of an unloaded mesh is, or reaches, a turning output through turning shafts that carry no torque
    here (an output that carries one counts as reached), never through the mesh's own two shafts."""
    outputs = {s.id for s in spec.shafts if s.role == "output" and s.id in motion.speeds}
    if any(shaft in outputs for shaft in start):
        return True
    seen, todo = set(mesh), list(start)
    while todo:
        shaft = todo.pop()
        for other in links.get(shaft, ()):
            if other in seen:
                continue
            seen.add(other)
            if other in outputs:
                return True
            if not _loaded(motion, other) and other in motion.speeds:
                todo.append(other)
    return False


def _links(spec: Any, first: Dict[str, geometry.Placed], out_of_mesh, engaged) -> Dict[str, Set[str]]:
    """The shafts joined in a mode: each mesh in mesh, each engaged coupling, and each planet shaft to its carrier."""
    links: Dict[str, Set[str]] = {}

    def join(p: str, q: str) -> None:
        if p and q and p != q:
            links.setdefault(p, set()).add(q)
            links.setdefault(q, set()).add(p)

    gone = {tuple(pair) for pair in out_of_mesh}
    for mesh in spec.meshes:
        a, b = first.get(mesh.a), first.get(mesh.b)
        if a is not None and b is not None and (mesh.a, mesh.b) not in gone:
            join(_shaft(a), _shaft(b))
    shaft_of = {g.id: g.shaft for g in spec.gears}
    for sleeve, dog in engaged:
        join(shaft_of.get(sleeve, ""), shaft_of.get(dog, ""))
    for s in spec.shafts:
        if s.id and s.mount() != FRAME:
            join(s.id, s.mount())
    return links


@dataclass(eq=False)
class _Mesh:
    """A parallel Meshes row as laid out: its row, its two gears placed (a planet's copy 1) and rated."""

    a: str
    b: str
    row: int
    pa: geometry.Placed
    pb: geometry.Placed
    ra: ToothRating
    rb: ToothRating
    width: float
    planets: int


def _laid_out(spec: Any, report: Any) -> Tuple[List[Tuple[Any, Optional[_Mesh], str]], Dict[str, geometry.Placed]]:
    """Every Meshes row the check laid out, in the Meshes sheet's order: (row, its parallel mesh or None, its kind).
    A sleeve, dog or hub (couplings, never meshes), a row not laid out and one laid out with a problem are left out."""
    first: Dict[str, geometry.Placed] = {}
    for p in report.layout.placed.values():
        first.setdefault(p.row or p.gear, p)
    gears = {g.id: g for g in spec.gears}
    clutch = {"sleeve", "dog", "hub"}
    out: List[Tuple[Any, Optional[_Mesh], str]] = []
    for mesh in spec.meshes:
        laid = report.meshes.get((mesh.a, mesh.b))
        ga, gb = gears.get(mesh.a), gears.get(mesh.b)
        if laid is None or laid.problem or ga is None or gb is None:
            continue
        if ga.kind_word() in clutch or gb.kind_word() in clutch:
            continue
        if laid.kind in (geometry.BEVEL, geometry.CROSSED):
            out.append((mesh, None, laid.kind))
            continue
        if laid.kind != geometry.PARALLEL:
            continue
        pa, pb = first.get(mesh.a), first.get(mesh.b)
        if pa is None or pb is None:
            continue
        ra, rb = _rating(spec, pa), _rating(spec, pb)
        width = min(geometry.faces_overlap(pa, pb), strength.toothed_width(pa.derived),
                    strength.toothed_width(pb.derived))
        planets = 0
        carried = pa if pa.carrier else pb if pb.carrier else None
        if carried is not None:
            row = carried.row or carried.gear
            planets = sum(1 for p in report.layout.placed.values() if (p.row or p.gear) == row)
        out.append((mesh, _Mesh(mesh.a, mesh.b, mesh.row, pa, pb, ra, rb, width, planets), laid.kind))
    return out, first


def _own_force(motion: Any, placed: geometry.Placed) -> float:
    """``2000 T / d`` for a gear whose shaft carries a torque above 0 here, else 0 (an idler, a planet)."""
    torque = _torque(motion, _shaft(placed))
    return 2000.0 * torque / placed.derived.d if torque > 0.0 else 0.0


def _idler(motion: Any, placed: geometry.Placed) -> bool:
    """An idler: a frame gear whose shaft carries exactly 0 here (kinematics' own rule); a planet is not one."""
    shaft = _shaft(placed)
    return not placed.carrier and shaft in motion.torques and motion.torques[shaft] == 0.0


def _forces(motion: Any, loaded: List[_Mesh]) -> Dict[int, float]:
    """Each loaded mesh's force in one mode, by its Meshes row (§5.2 items 2 to 4)."""
    forces: Dict[int, float] = {}
    plain = [m for m in loaded if not m.planets]
    for m in loaded:
        if m.planets:
            member = m.pb if m.pa.carrier else m.pa
            share = strength.PLANET_SHARE if m.planets >= 2 else 1.0
            forces[m.row] = 2000.0 * _torque(motion, _shaft(member)) / (member.derived.d * m.planets) * share
    # The idlers: each chain of idler gears (joined by meshes between two idlers) takes the largest force any of its
    # non-idler mates gives it.
    chain: Dict[str, str] = {}

    def root(gear: str) -> str:
        while chain.get(gear, gear) != gear:
            gear = chain[gear]
        return gear

    for m in plain:
        for p in (m.pa, m.pb):
            if _idler(motion, p):
                chain.setdefault(p.gear, p.gear)
        if _idler(motion, m.pa) and _idler(motion, m.pb):
            chain[root(m.pa.gear)] = root(m.pb.gear)
    passed: Dict[str, float] = {}
    for m in plain:
        for idler, mate in ((m.pa, m.pb), (m.pb, m.pa)):
            if _idler(motion, idler) and not _idler(motion, mate):
                key = root(idler.gear)
                passed[key] = max(passed.get(key, 0.0), _own_force(motion, mate))
    for m in plain:
        forces[m.row] = max(passed.get(root(p.gear), 0.0) if _idler(motion, p) else _own_force(motion, p)
                            for p in (m.pa, m.pb))
    return forces


def _not_loaded_state(spec: Any, links: Dict[str, Set[str]], motion: Any, m: _Mesh) -> str:
    shafts = (_shaft(m.pa), _shaft(m.pb))
    past = set(getattr(motion, "past_split", ()) or ())
    if any(s in past for s in shafts):
        return NOT_SHARED
    if all(s in motion.speeds for s in shafts):
        start = [s for s in shafts if not _loaded(motion, s)]
        if _reaches_output(spec, links, motion, start, set(shafts)):
            return UNWORKED
    return UNLOADED


def _rated_row(m: _Mesh, mode: str, motion: Any, force: float, allowable: float) -> MeshStrength:
    sides = []
    for gear, placed, rating in ((m.a, m.pa, m.ra), (m.b, m.pb, m.rb)):
        shaft = _shaft(placed)
        two_way = shaft in motion.torques and motion.torques[shaft] == 0.0
        held = strength.holds(rating, allowable, width=m.width, two_way=two_way) if rating.rated else None
        sides.append(GearSide(gear, rating, held, two_way))
    unrated = tuple(s.gear for s in sides if s.held is None)
    rated = [s for s in sides if s.held is not None]
    if not rated:
        return MeshStrength(m.a, m.b, m.row, mode, NOT_RATED, None, m.width, tuple(sides), planets=m.planets,
                            unrated=unrated)
    weaker = min(rated, key=lambda s: s.held)          # the first of two equal figures
    share = force / weaker.held if weaker.held > 0.0 else None
    return MeshStrength(m.a, m.b, m.row, mode, RATED, force, m.width, tuple(sides), weaker.gear, share, m.planets,
                        unrated)


def mesh_strengths(spec: Any, report: Any) -> Tuple[MeshStrength, ...]:
    """Every Meshes row of a printed gearbox in every mode, in the Meshes sheet's order and each mode's (§5.2); `()`
    for a machined gearbox or one whose first input has no torque.

    The body is package B's, over F4-0's stub. A row is left out of a mode in which a slide takes it out of mesh; a
    bevel or crossed pair is one row, its mode ``""``, never rated (§5.1); a sleeve's couplings are not on Meshes and
    give nothing."""
    if not worked_out(spec) or not getattr(report, "checked", True):
        return ()
    allowable, _typed = allowable_of(spec)
    rows, first = _laid_out(spec, report)
    modes = ([(m.name, m.motion, tuple(m.out_of_mesh), tuple(m.engaged)) for m in report.modes]
             or [("", report.motion, (), ())])
    per_mode: List[Dict[int, MeshStrength]] = []
    for name, motion, out_of_mesh, engaged in modes:
        gone = {tuple(pair) for pair in out_of_mesh}
        meshes = [m for _row, m, _kind in rows if m is not None and (m.a, m.b) not in gone]
        loaded = [m for m in meshes if _loaded(motion, _shaft(m.pa)) and _loaded(motion, _shaft(m.pb))]
        forces = _forces(motion, loaded)
        links = _links(spec, first, out_of_mesh, engaged)
        found: Dict[int, MeshStrength] = {}
        for m in meshes:
            if m in loaded:
                found[m.row] = _rated_row(m, name, motion, forces[m.row], allowable)
            else:
                sides = (GearSide(m.a, m.ra), GearSide(m.b, m.rb))
                found[m.row] = MeshStrength(m.a, m.b, m.row, name, _not_loaded_state(spec, links, motion, m), None,
                                            m.width, sides, planets=m.planets,
                                            unrated=tuple(s.gear for s in sides if not s.rating.rated))
        per_mode.append(found)
    out: List[MeshStrength] = []
    for mesh, m, kind in rows:
        if m is None:
            out.append(MeshStrength(mesh.a, mesh.b, mesh.row, "", BEVEL if kind == geometry.BEVEL else CROSSED))
        else:
            out.extend(found[m.row] for found in per_mode if m.row in found)
    return tuple(out)


# -- the words -------------------------------------------------------------------------------------------------------


def _mm(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def _and(items: Sequence[str]) -> str:
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def once(row: MeshStrength, side: GearSide, allowable: float) -> float:
    """What one of the side's teeth is rated to take once at the mesh's width, without the 0.7 (R1)."""
    return strength.holds(side.rating, allowable, width=row.width)


def _over(row: MeshStrength, allowable: float, typed: bool) -> str:
    """The sentence for the weaker gear of a row whose share passes 100 % (§6.1), with its full stop."""
    side = row.side(row.weaker)
    rating = side.rating
    fillet = (f" (its {_mm(rating.rho_f)} mm fillet is sharper than the stress factor's range, which is carried past "
              "it)" if rating.ring and rating.past_range else "")
    mpa = strength.megapascals(allowable)
    provisional = "" if typed else PROVISIONAL
    head = (f"these teeth take about {strength.newtons(row.force)} N at the pitch circle"
            f"{' in ' + row.mode if row.mode else ''}, {strength.times(row.share)} times the "
            f"{strength.newtons(side.held)} N {side.gear}'s teeth{fillet} are rated to take")
    if side.two_way:
        who = "a planet's" if row.planets else "an idler's"
        text = (f"{head} at {mpa} MPa{provisional}: {strength.newtons(once(row, side, allowable))} N once, with an "
                f"allowance of {strength.TWO_WAY:g} because {who} teeth are loaded in both directions as the gearbox "
                "runs")
    else:
        text = f"{head} once at {mpa} MPa{provisional}"
    if row.planets >= 2:
        text += (f"; the load is shared by {row.planets} planets, one taking {strength.PLANET_SHARE:g} of an even "
                 "share")
    return text + "."


def _unrated_clause(row: MeshStrength) -> str:
    """M1's sentence for each gear of a loaded row that is not rated, with its full stop."""
    pieces = [f"{s.gear} is not rated: {s.rating.why}" for s in row.sides if s.gear in row.unrated]
    rated = [s.gear for s in row.sides if s.gear not in row.unrated]
    tail = f"the share counts {rated[0]} alone" if rated else "so no share is worked out"
    return "; ".join(pieces) + f"; {tail}."


def warning_sentence(rows: Sequence[MeshStrength], allowable: float, typed: bool) -> str:
    """The one warning at a Meshes row (§5.4, F4-INTERFACES §6.1), without the pair (the check puts *Sun and Planet:*
    before it, as F1's clearance warning is said): `rows` that row's MeshStrength in every mode; `""` when it says
    nothing (no share past 100 % and no gear not rated in a loaded mode). It names the mode with the largest share.

    The body is package B's, over F4-0's stub."""
    worst = None
    for r in rows:
        if r.state == RATED and r.share is not None and (worst is None or r.share > worst.share):
            worst = r
    over = worst if worst is not None and worst.share > 1.0 else None
    unrated = next((r for r in rows if r.state in (RATED, NOT_RATED) and r.unrated), None)
    if over is None and unrated is None:
        return ""
    pieces = []
    if over is not None:
        pieces.append(_over(over, allowable, typed))
    if unrated is not None:
        pieces.append(_unrated_clause(over if over is not None and over.unrated else unrated))
    if over is not None:
        pieces.append(REMEDY)
    return "Printed, " + " ".join(pieces)


# -- the Results block's rows (export.results_sheet writes them) -----------------------------------------------------


def _held_cell(side: GearSide):
    """A gear's figure as a number to 0.001 N, or as text with its marks: *(0.7)*, *(stress factor past its range)*."""
    marks = ([TWO_WAY_MARK] if side.two_way else []) + ([PAST_RANGE_MARK] if side.rating.past_range else [])
    return f"{side.held:.3f} {' '.join(marks)}" if marks else round(side.held, 3)


def results_rows(rows: Sequence[MeshStrength], allowable: float, typed: bool, box_text: str = "") -> List[List]:
    """The Results sheet's *Tooth strength* block (§5.4, F4-INTERFACES §6.3): its head, a row per Meshes row and mode,
    *Worst share*, *Allowable stress (MPa)* and the note. `box_text` is the Box's Allowable stress as typed, to tell a
    blank from a figure that does not read."""
    out: List[List] = [list(RESULTS_HEAD)]
    for r in rows:
        if r.state in PAIR_WORDS:
            out.append([r.name, "", f"not rated: {PAIR_WORDS[r.state]}"])
        elif r.state == UNLOADED:
            out.append([r.name, r.mode, "—", "", "", TURNS_UNLOADED])
        elif r.state == NOT_SHARED:
            out.append([r.name, r.mode, "—", "", "", NOT_SHARED_OUT])
        elif r.state == UNWORKED:
            out.append([r.name, r.mode, "—", "", "", NOT_GIVEN])
        elif r.state == NOT_RATED:
            said = ", ".join(f"{s.gear} ({s.rating.short})" for s in r.sides)
            out.append([r.name, r.mode, "—", "", "", f"not rated: {said}"])
        else:
            weaker = r.weaker + "".join(f" ({g} not rated)" for g in r.unrated)
            out.append([r.name, r.mode, round(r.force, 3), weaker, _held_cell(r.side(r.weaker)),
                        round(100.0 * r.share, 1) if r.share is not None else "—"])
    out.append(worst_row(rows))
    figure = int(allowable) if allowable == int(allowable) else allowable
    words = ALLOWABLE_TYPED if typed else (ALLOWABLE_UNREAD if str(box_text or "").strip() else ALLOWABLE_BLANK)
    out.append([RESULTS_ALLOWABLE, figure, words])
    out.append([RESULTS_NOTE])
    return out


def worst_row(rows: Sequence[MeshStrength]) -> List:
    """*Worst share*: the largest share over every rated mesh and mode (*Sun–Planet in L, 1364.3 %*, with *(Ring not
    rated)* when it counts one gear alone), *—* with none; then, in a third cell joined by *; *, every mesh or gear not
    rated with its reason, and every loaded mesh not worked out with its modes (the re-check's should-fix)."""
    worst = None
    for r in rows:
        if r.state == RATED and r.share is not None and (worst is None or r.share > worst.share):
            worst = r
    if worst is None:
        said = "—"
    else:
        said = f"{worst.name}{' in ' + worst.mode if worst.mode else ''}, {100.0 * worst.share:.1f} %"
        said += "".join(f" ({g} not rated)" for g in worst.unrated)
    not_rated: List[str] = []
    for r in rows:
        items = ([f"{r.name} ({PAIR_WORDS[r.state]})"] if r.state in PAIR_WORDS else []) + \
            [f"{s.gear} ({s.rating.short})" for s in r.sides if not s.rating.rated]
        not_rated += [item for item in items if item not in not_rated]
    modes: Dict[Tuple[str, str], List[str]] = {}
    for r in rows:
        if r.state in WHY_NOT_WORKED:
            modes.setdefault((r.name, r.state), []).append(r.mode)
    groups: Dict[Tuple[Tuple[str, ...], str], List[str]] = {}
    for (name, state), its in modes.items():
        groups.setdefault((tuple(its), state), []).append(name)
    unworked = [f"{', '.join(names)}{' in ' + _and(its) if any(its) else ''} ({WHY_NOT_WORKED[state]})"
                for (its, state), names in groups.items()]
    listed = ([f"not rated: {', '.join(not_rated)}"] if not_rated else []) + \
        ([f"not worked out: {', '.join(unworked)}"] if unworked else [])
    return [RESULTS_WORST, said] + (["; ".join(listed)] if listed else [])


__all__ = [
    "BEVEL", "CROSSED", "GearSide", "MeshStrength", "NOT_GIVEN", "NOT_RATED", "NOT_SHARED", "NOT_SHARED_OUT", "RATED",
    "TURNS_UNLOADED", "UNLOADED", "UNWORKED", "allowable_of", "mesh_strengths", "results_rows", "warning_sentence",
    "worked_out", "worst_row",
]
