"""What Update SolidWorks would change, and recording what it did (docs/PLAN-WORKBOOK.md §4.5, phase W4).

Pure, on the Tk thread: :func:`classify` compares the linked file's latest
read with the link record and says what Update SolidWorks carries — part
values, the layout's globals, components re-placed — or why a new revision is
needed instead; :func:`finish_update` turns what the worker did
(``swbuild.GearboxUpdate``) into the sidecars and record to save. The worker
runs ``swbuild.update_gearbox(session, **plan.update_kwargs())`` and nothing
else. No COM, no Tk; the file system only through injected callables.

Interfaces pinned in the W4 interface commit; every body that raises
NotImplementedError is Agent B's.

**What is structural** (a new revision, offered after asking): a gear, shaft
or mesh added, removed or renamed; a coordinate that changes side or reaches
or leaves 0 (a layout plane cannot follow a global across its base plane); a
built part whose gears now want different parts (a split); a part whose
resulting stem changes; and ``swbuild.structural_change`` on what is left,
once the plans and stems have been compared and the fields a kind ignores
normalised (decision 5: a spur gear's Hand, a Part name equal to the default
stem, are not). **A value update**: the kind's variable texts differ. **A
move**: X or Y on the same side (the layout's globals), Z, Z± or At (while the
assembly is static). Speeds, torques and efficiencies change nothing in
SolidWorks. A part keeps its file name after a value update (N68 holding 69
teeth).

The record is compared for the sentence before the press; the worker compares
with SolidWorks live, so Update stays enabled even when the record says
nothing differs (an unsaved or lost update is put right).

**A gearbox built to turn** (W5, ``GearboxRecord.kind`` MOTION) is classified
from the record's own mates (:func:`_turning`): more is structural — a mated
shaft's Z± flipped, a mated gear on another shaft, a shaft starting or ceasing
to stand still (its Role ``fixed``, or held still through a fixed shaft), an
anchor's front face reaching, leaving or crossing the Front plane, a meshed
gear's tooth change while ``findings.GEAR_MATE_RATIO_ROUTE`` is not
``"remake"``, and a follower's place along its shaft unless
``findings.LOCK_RETAKES_AN_OFFSET`` — and what is left goes to the worker's
motion path as a ``swbuild.MotionUpdate``. A static gearbox keeps W4's path
untouched (W5-PLAN D5).
"""

from __future__ import annotations

import copy
import math
import os
import re
from dataclasses import asdict, dataclass, field, replace
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from .. import findings, store, swbuild
from ..gears import bevel, clutch, equations, kind_for, spur
from ..gears import base
from ..gears.base import GlobalVariable
from ..spec import GearSpec, InputError
from ..store import GearboxRecord, LinkRecord, MateEntry, PartEntry, ShaftEntry, Sidecar
from ..swbuild import (MARK_MISMATCHED, MARK_UNSAVED, POSE_TOLERANCE, DocumentValues, GearboxUpdate, LockLink, MateRef, MeshLink, MotionUpdate, Placement,
                       _caps_with_arc, on_in, plan_features, same_frame, structural_change)
from . import gearbox, geometry, layout, motion, planetary, schema
from .assess import Assessment
from .build import PartJob
from .gearbox import Finished
from .layout import ShaftLayout


@dataclass(frozen=True)
class PartUpdate:
    """One part of the current revision and what it should hold now. ``variables`` is every global as it should
    be (``kind.variables(spec, derived)``; the worker sets only those SolidWorks holds differently). ``changed``:
    the record's variables differ from these — for the sentence only."""

    path: str
    gear_ids: Tuple[str, ...]
    spec: GearSpec
    derived: Any
    variables: Tuple[GlobalVariable, ...]
    changed: bool = False
    # W9a (ISSUE-1-PLAN K11, K1/K3; W9A-INTERFACES.md), handed to the worker in its ``DocumentValues``: ``recorded``
    # the ``(global, expression)`` pairs the record says the file holds (None when it has none), ``cells`` the
    # workbook cell of each global a cell sets (every row's, joined, for a shared part), ``made`` every feature the
    # record lists for the part (its ``.gear.json``), else the part's plan's, and ``mark`` the record's mark on it,
    # from which the worker decides whether the record vouches for the file.
    recorded: Optional[Tuple[Tuple[str, str], ...]] = None
    cells: Tuple[Tuple[str, str], ...] = ()
    made: Tuple[str, ...] = ()
    mark: str = ""                  # the record's mark on the file: "unsaved", "mismatched" or ""


@dataclass(frozen=True)
class UpdatePlan:
    """What Update SolidWorks would do, from the record and the latest read.

    ``parts``: every part of the current revision (``record.current_parts()``),
    with its wanted values. ``layout``: the layout part and every layout
    global as wanted (``features`` its planes and axes, checked live), or None
    when no layout is recorded (W2 parts only). ``assembly``: its path, or
    ``""``. ``placements``: every gear's wanted frame, by the component
    ``Name2`` on record, with its pitch. For the sentence, against the record:
    ``moved_shafts`` (X, Y, Z or Z± changed), ``replaced`` (gears whose frame
    differs, modulo pitch). ``structural``: sentences, each a reason a new
    revision is needed (Update is then not run; the window offers to build
    again). ``missing``: recorded files no longer on disk (likewise).
    ``unsaved``: documents of the current revision an earlier Update changed
    and that are not yet saved (an earlier revision's are left out: second
    review N2). ``refusal``: ``""``, or why there is nothing Update can act on
    (no record, a record with no parts, a record that is another workbook's).
    ``foreign_record``: that other workbook, when the record beside this one
    was written for a workbook still on disk, or one the person said this is
    a copy of — and Update leaves that workbook's files alone (review S1) —
    or for a workbook that is gone, until the person says this one was moved
    or renamed from it (second review N1c, ``store.record_owner``).

    W5 (Agent B fills them; W5-INTERFACES.md): ``motion`` is what the worker's
    motion path is given for a gearbox on record as turning
    (``GearboxRecord.kind == motion.MOTION``), None for a static one (W4's
    path, unchanged: W5-PLAN D5). For the sentence: ``axial`` the gears whose
    ``"<Gear> Face Z"`` changes, ``ratios`` the gear mates (by name) whose
    ratio changes — empty while ``findings.GEAR_MATE_RATIO_ROUTE`` is not
    ``"remake"``, a tooth change being structural then.
    """

    parts: Tuple[PartUpdate, ...] = ()
    layout: Optional[DocumentValues] = None
    assembly: str = ""
    placements: Tuple[Placement, ...] = ()
    moved_shafts: Tuple[str, ...] = ()
    replaced: Tuple[str, ...] = ()
    structural: Tuple[str, ...] = ()
    missing: Tuple[str, ...] = ()
    unsaved: Tuple[str, ...] = ()
    refusal: str = ""
    shafts: Tuple[ShaftLayout, ...] = ()       # the shafts as now wanted, for the record (Agent B, additive)
    foreign_record: str = ""
    motion: Optional[MotionUpdate] = None
    axial: Tuple[str, ...] = ()
    ratios: Tuple[str, ...] = ()
    drag: Tuple[str, ...] = ()                 # a turning gearbox's drag gear per train, now (Agent B, additive)
    # W6 (B; W6-PLAN §2.7, D17): gear mates (by name) whose mesh sense the new read changes — a crossed shaft moved
    # to the other side of its partner — each remade by Update through ``MotionUpdate.ratios``, for the sentence.
    resensed: Tuple[str, ...] = ()
    # W7 (B; W7-PLAN §2.10, §5.3): each carrier part and every global it should hold now (``features`` its axes),
    # and the carriers whose planet axes move (for the sentence). Empty with no planetary stage.
    carriers: Tuple[DocumentValues, ...] = ()
    carriers_moved: Tuple[str, ...] = ()
    # W7 (Agent B, additive, as ``shafts`` is): the carriers as now laid out, for the record a finish writes.
    carrier_layouts: Tuple[Any, ...] = ()
    # W8 (B, additive): the slide mates whose value in some configuration, and the couplings and sliding meshes whose
    # on-set, the workbook now changes (J14) — so ``record_matches`` is False; the sentence reads
    # ``motion.slide_values`` and ``on_sets`` against the record's mates.
    modes_changed: Tuple[str, ...] = ()
    # W9c (B; W9C-INTERFACES §2, §3): what the Update makes or takes away in place (K6, §2.4); empty: W9a's Update.
    in_place: Any = field(default_factory=lambda: swbuild.InPlace())
    # W9c (B's own, for ``finish_update``, §7): what the record takes from the read when the Update makes or takes
    # away in place — None when it does neither.
    in_place_record: Optional["InPlaceRecord"] = None
    # W9c: ``(gear, path)`` of each added gear's new part whose file is already on disk though the record does not hold
    # it (a press that stopped after building it, or a file of the user's): the worker refuses rather than build over
    # it, and the footer says so before the press.
    new_parts_on_disk: Tuple[Tuple[str, str], ...] = ()
    # W9c (the review's must-fix 2): what a press that stopped part way left of the app's that this read no longer
    # uses, ``(what, name)`` with ``what`` one of LEFT_GLOBAL, LEFT_CONFIGURATION, LEFT_PART (the part's path): the
    # footer and the result say each as the app's own leftover, left as it is and kept on record.
    leftovers: Tuple[Tuple[str, str], ...] = ()

    @property
    def changed_parts(self) -> Tuple[PartUpdate, ...]:
        return tuple(p for p in self.parts if p.changed)

    @property
    def needs_new_revision(self) -> bool:
        """Update cannot carry it: the window asks whether to build again instead."""
        return bool(self.structural or self.missing)

    @property
    def record_matches(self) -> bool:
        """Nothing on record differs from the workbook (the worker still compares live)."""
        return not (self.changed_parts or self.moved_shafts or self.replaced or self.needs_new_revision
                    or self.modes_changed or bool(self.in_place))

    def update_kwargs(self) -> Dict[str, Any]:
        """The arguments of ``swbuild.update_gearbox(session, **plan.update_kwargs())``. Never called on a plan
        that is refused or needs a new revision. ``"motion"`` is there only for a turning gearbox, so a static
        one's call is W4's, key for key."""
        if self.refusal or self.needs_new_revision:
            raise ValueError("Update SolidWorks cannot carry this change: "
                             + " ".join((self.refusal,) + self.structural + self.missing).strip())
        kwargs: Dict[str, Any] = {
            "parts": [DocumentValues(p.path, tuple(p.variables), recorded=p.recorded, cells=p.cells, made=p.made,
                                     mark=p.mark) for p in self.parts],
            "layout": self.layout,
            "assembly": self.assembly,
            "placements": list(self.placements),
        }
        if self.motion is not None:
            kwargs["motion"] = self.motion
        lines = layout.layout_lines(self.shafts) if self.layout is not None else ()
        if lines:                                     # W6 (§7.15): each slanted shaft's line axis, read back
            kwargs["lines"] = {name: (point, direction) for name, point, direction in lines}
        if self.carriers:                             # W7: only with a planetary stage
            kwargs["carriers"] = list(self.carriers)
        if self.in_place:                             # W9c: only when something is made or taken away in place
            kwargs["in_place"] = self.in_place
        return kwargs


MOVE_TOLERANCE = POSE_TOLERANCE         # mm: a shaft coordinate that changed less than this has not moved


def _names(items: Sequence[str]) -> str:
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def _is(items: Sequence[str]) -> str:
    return "is" if len(items) == 1 else "are"


def _number(value: float) -> str:
    return equations.literal(round(value, 6))


def _side_change(shaft: str, coordinate: str, old: float, new: float) -> str:
    """Why a coordinate that changed side of its base plane needs a new layout part, or ``""`` (decision: any
    change between plus, minus and base is structural — findings.OFFSET_GLOBAL_CROSSES_ZERO is False, and a
    global set below zero was taken without a word while its plane stayed where it was)."""
    was, now = layout.side(old), layout.side(new)
    if was == now:
        return ""
    move = f"{_number(old)} → {_number(new)}"
    if was == layout.BASE:
        return (f"{shaft}'s {coordinate} moves off 0 ({move}): the layout part has no plane for {shaft} {coordinate}, "
                "so it needs a new layout part.")
    if now == layout.BASE:
        return (f"{shaft}'s {coordinate} moves to 0 ({move}): its layout plane cannot reach the base plane, so it "
                "needs a new layout part.")
    return (f"{shaft}'s {coordinate} crosses 0 ({move}): a layout plane cannot follow a global across its base "
            "plane, so it needs a new layout part.")


def _ignored_fields_as_built(built: GearSpec, wanted: GearSpec, template: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Both forms as dicts, with every field the wanted part's kind ignores set to the built value (decision 5):
    a field is ignored when giving it the built value leaves the wanted plan as it is. ``name`` is never compared
    here (:func:`gearbox.name_changed` decides it)."""
    b, w = built.to_dict(), wanted.to_dict()
    b.pop("name", None)
    w.pop("name", None)
    for form, values in ((built, b), (wanted, w)):     # a blank recipe is the kind's default: say which
        try:
            values["recipe"] = kind_for(form).recipe_for(form)
        except (AttributeError, InputError, ValueError):
            pass
    plan = gearbox._plan_of(wanted, template)
    for key in list(w):
        if str(b.get(key, "")) == str(w[key]):
            continue
        try:
            trial = wanted.with_values(**{key: str(b.get(key, ""))})
        except (TypeError, ValueError):
            continue
        if plan is not None and gearbox._plan_of(trial, template) == plan:
            w[key] = b.get(key, "")
    return b, w


# The fields swbuild.structural_change names by their field name, as the Gears sheet calls them (second W4 review
# N6: the footer said "The recipe changed from 'A' to 'B'" where the person had typed Flank = arcs, and "The
# teeth_side changed" for Side). Bore, profile shift and groove it already says in words.
_COLUMNS = (("kind", "Kind"), ("recipe", "Flank"), ("hand", "Hand"), ("teeth_side", "Side"))
_FLANK_OF_RECIPE = {recipe: flank for flank, recipe in schema.FLANK_RECIPE.items()}


def _structural(built: Dict[str, Any], wanted: Dict[str, Any]) -> str:
    """``swbuild.structural_change`` in the workbook's words: *Flank changed from involute to arcs, which its values
    cannot carry; build it again as a new part.* (``ui_text`` turns the tail into the footer's). The strip keeps
    ``structural_change``'s own sentence, in its own words."""
    for key, column in _COLUMNS:
        default = "external" if key == "teeth_side" else ""
        was, now = (str(values.get(key, default) or default) for values in (built, wanted))
        if was != now:
            word = (lambda v: _FLANK_OF_RECIPE.get(v, v)) if key == "recipe" else (lambda v: v)
            return (f"{column} changed from {word(was) or 'blank'} to {word(now) or 'blank'}, which its values cannot "
                    "carry; build it again as a new part.")
    return structural_change(built, wanted)


_BUILD_NOT_ON_RECORD = ("The record does not say how this part was built, so whether its teeth can be cut this "
                        "few through its values cannot be told; build it again as a new part.")


def _part(entry: PartEntry, job: PartJob, exists: Callable[[str], bool]) -> Tuple[PartUpdate, str]:
    """What Update does to one built part, and the sentence if it cannot (``""``)."""
    variables = gearbox._variables_of(job)
    label = f"{gearbox._stem_of(entry.path)} ({_names(entry.gears)})"
    recorded = tuple((str(pair[0]), str(pair[1])) for pair in entry.variables if len(pair) == 2) or None
    update = PartUpdate(entry.path, tuple(entry.gears), job.spec, job.derived, variables, changed=True,
                        recorded=recorded, made=plan_features(job.plan) if job.plan is not None else ())
    built: Optional[GearSpec] = None
    if entry.spec:
        try:
            built = GearSpec.from_dict(entry.spec)
        except (TypeError, ValueError, AttributeError):
            built = None
    if built is None:
        # A v1 record (or one whose form will not read): what the part holds is known only live, and that is
        # enough for its values, but not for teeth so few their spaces close with an arc on the tip cap, which no
        # global carries: a part built with a chord would keep it, inside the tips.
        if _caps_with_arc(job.spec.to_dict()) is True:
            return update, f"{label}: {_BUILD_NOT_ON_RECORD}"
        return update, ""
    template = gearbox._template_of(job.plan)
    if gearbox.name_changed(built, job.spec):
        return update, (f"{label}: its Part name now makes {job.spec.stem()}{layout.PART_EXTENSION}, and a built "
                        "part's file is never renamed, so it needs a new part.")
    unchanged = gearbox._variables_match(entry.variables, entry.trig, variables)
    reformed = _bevel_form_change(entry, built, job.spec)
    if reformed:
        return update, reformed
    if gearbox.same_part(built, job.spec, template):
        return replace(update, changed=not unchanged or not entry.variables), ""
    b, w = _ignored_fields_as_built(built, job.spec, template)
    why = _structural(b, w)
    if why:
        return update, f"{label}: {why}"
    held = {str(pair[0]) for pair in entry.variables if pair}
    if held:
        lacking = [v.name for v in variables if v.name not in held]
        if lacking:
            return update, (f"{label}: its new values need the global \"{lacking[0]}\", which the built part does "
                            "not have, so it needs a new part.")
        if unchanged:
            return update, (f"{label}: it would now be built differently in a way its values do not carry, so it "
                            "needs a new part.")
    return update, ""


_FORM_WORDS = {bevel.FORM_CONE: "a cone", bevel.FORM_CROWN: "a crown gear",
               bevel.FORM_INTERNAL: "an internal bevel gear"}


def _bevel_form(spec: GearSpec) -> str:
    """A bevel gear's form (``bevel.form_of`` of its pitch cone), or ``""`` when it is not a bevel gear or its
    teeth, mate teeth or shaft angle do not read."""
    if str(getattr(spec, "kind", "")) != "bevel":
        return ""
    try:
        return bevel.form_of(bevel.pitch_cone_angle(spec.teeth_count(), spec.mate_teeth_count(),
                                                    spec.shaft_angle_deg()))
    except (InputError, ValueError, ZeroDivisionError):
        return ""


def _bevel_form_change(entry: PartEntry, built: GearSpec, wanted: GearSpec) -> str:
    """W6 (D14, W6-PLAN §2.7): a bevel gear whose new teeth, mate teeth or shaft angle change its form (cone, crown,
    internal) needs a new part, since the part's operations differ and ``swbuild.structural_change`` does not see
    it: *G2's teeth (40 → 41) make it a crown gear where it was built a cone, which its values cannot carry; build
    it again as a new part.* ``""`` otherwise."""
    was, now = _bevel_form(built), _bevel_form(wanted)
    if not was or not now or was == now:
        return ""
    gear = entry.gears[0] if entry.gears else "The gear"
    edits = []
    for field_, words in (("teeth", f"{gear}'s teeth"), ("mate_teeth", "its mate's teeth"),
                          ("shaft_angle", "the shaft angle")):
        old, new = (str(getattr(form, field_, "")).strip() for form in (built, wanted))
        if old != new:
            edits.append(f"{words} ({old} → {new})")
    if not edits:
        edits = [f"{gear}'s values"]
    edits[0] = edits[0][0].upper() + edits[0][1:]
    verb = "makes" if len(edits) == 1 and edits[0].startswith("The shaft angle") else "make"
    return (f"{' and '.join(edits)} {verb} it {_FORM_WORDS[now]} where it was built {_FORM_WORDS[was]}, which its "
            "values cannot carry; build it again as a new part.")


@store.in_one_pass
def classify(record: Optional[LinkRecord], a: Assessment, *,
             exists: Callable[[str], bool] = os.path.exists,
             read_sidecar: Optional[Callable[[str], Optional[Sidecar]]] = None) -> UpdatePlan:
    """What Update SolidWorks would change, from the planning read of the record (``store.read_link_record``) and
    an assessment that passed ``a.lay_out_refusal()`` (or ``a.build_refusal()`` when only parts are recorded).
    Acts only on ``record.current_parts()`` (decision 2). Pure but for ``exists``.

    Plans and stems are compared before ``structural_change``, and the
    fields a kind ignores are normalised first (decision 5), so an edit the
    part cannot see is no change at all. The gears to re-place are those
    whose wanted frame (``layout.frames``) is not the recorded one modulo the
    gear's pitch (``swbuild.same_frame``, review 14), whatever moved them:
    a shaft, an At, a face width, a tooth count, a mesh's phase, the input.

    A gearbox on record as turning is refused while :func:`motion.update_reason`
    says so, or while a recorded mate cannot be read (:func:`_bad_mates`);
    otherwise W4's rules run first and :func:`_turning` adds its structural
    cases, ``motion``, ``axial`` and ``ratios``.
    """
    if record is None:
        return UpdatePlan(refusal="Nothing has been built from this workbook yet, so Update SolidWorks has nothing "
                                  "to change.")
    here = str(a.read.source_path or a.spec.source_path or "")
    owner, foreign = store.record_owner(record, here, exists)
    if owner != store.OURS:
        return UpdatePlan(refusal=store.foreign_record_sentence(here, foreign, gone=owner == store.UNSURE,
                                                                said=store.copy_by_answer(record, here, exists)),
                          foreign_record=foreign)
    box = record.gearbox
    if box is not None and not box.assembly:
        return UpdatePlan(refusal=(f"{os.path.basename(box.layout)} was saved but its assembly was not made: Build "
                                   "carries on with it, and Update SolidWorks waits until it has."))
    turning = box is not None and box.kind == motion.MOTION
    if turning:
        why = motion.update_reason() or _bad_mates(box)
        if why:
            return UpdatePlan(refusal=why)
    entries = record.current_parts()
    if not entries:
        return UpdatePlan(refusal="The record of what was built lists no parts, so Update SolidWorks has nothing "
                                  "to change.")
    spec = a.spec
    job_of: Dict[str, PartJob] = {g: job for job in a.parts.jobs for g in job.gear_ids}
    structural: List[str] = []
    missing: List[str] = []

    # Gears, shafts and meshes added, removed or renamed. W7: a copy is compared through the row it is of
    # (``ComponentEntry.of``), and a change in the number of copies is said once (W7-PLAN §2.10).
    if box is not None:
        recorded = list(dict.fromkeys(c.of or c.gear for c in box.components))
        current = [g.id for g in spec.gears]
        structural.extend(_planetary_structural(box, a))
    else:
        recorded = [g for p in entries for g in p.gears]
        current = [g.id for g in spec.gears if g.id in job_of]
    gone = [g for g in recorded if g not in current]
    new = [g for g in current if g not in recorded]
    # W9c (K6; W9C-INTERFACES §3): on a gearbox built to turn, a gear added on a frame shaft on record along Z± and
    # one taken out that anchors no other gear are carried in place; every other is said, each by its own sentence.
    in_added: List[str] = []
    in_removed: List[str] = []
    if turning and (gone or new):
        in_added, in_removed, said = _in_place_gears(box, a, gone, new, job_of, entries, exists)
        structural.extend(said)
    else:
        if gone:
            structural.append(f"{_names(gone)} {_is(gone)} no longer in the workbook, and Update SolidWorks cannot "
                              f"take a part out of what was built.")
        if new:
            structural.append(f"{_names(new)} {_is(new)} new, and Update SolidWorks cannot add a part to what was "
                              "built.")
    whole_box = box
    if in_removed:
        box = _kept_box(box, in_removed)
    sliding_now = set(_slider_ids(a)) if turning else set()

    shafts: Tuple[ShaftLayout, ...] = ()
    moved: List[str] = []
    layout_values: Optional[DocumentValues] = None
    if box is not None:
        try:
            shafts = layout.shaft_layouts(spec)
        except ValueError as exc:
            return UpdatePlan(refusal=str(exc))
        before = {s.shaft: s for s in box.shafts}
        now = {s.shaft: s for s in shafts}
        gone_s = [s for s in before if s not in now]
        new_s = [s for s in now if s not in before]
        if gone_s:
            structural.append(f"Shaft {_names(gone_s)} {_is(gone_s)} no longer in the workbook, and its axis cannot "
                              "be taken out of the layout part.")
        if new_s:
            structural.append(f"Shaft {_names(new_s)} {_is(new_s)} new, and the layout part has no axis for it.")
        for shaft in shafts:
            old = before.get(shaft.shaft)
            if old is None:
                continue
            # The coordinates the layout holds as planes (W6: square to the shaft's axis; a slant has none).
            index = _cardinal(_direction(shaft))
            if index is not None and index == _cardinal(_direction(old)):
                for i, (coordinate, was, value) in enumerate((("X", old.x, shaft.x), ("Y", old.y, shaft.y),
                                                               ("Z", old.z, shaft.z))):
                    why = "" if i == index else _side_change(shaft.shaft, coordinate, was, value)
                    if why:
                        structural.append(why)
            why = _slant_change(old, shaft) or ("" if turning else _family_change(old, shaft))
            if why:
                structural.append(why)
            if (any(abs(p - q) > MOVE_TOLERANCE for p, q in ((old.x, shaft.x), (old.y, shaft.y), (old.z, shaft.z)))
                    or _direction(old) != _direction(shaft)):
                moved.append(shaft.shaft)
        listed = lambda pairs: {frozenset(p) for p in pairs}           # noqa: E731
        was_meshed, meshed = listed(tuple(m) for m in box.meshes), listed((m.a, m.b) for m in spec.meshes)
        was_meshed = listed(tuple(m) for m in whole_box.meshes)
        for pair in sorted(meshed - was_meshed, key=sorted):
            if pair & set(in_added) or pair & sliding_now:
                continue                    # W9c: an added gear's own mesh, or a sliding mesh (``_modes``)
            structural.append(f"The mesh {'–'.join(sorted(pair))} is new, and Update SolidWorks cannot add one.")
        for pair in sorted(was_meshed - meshed, key=sorted):
            if pair & set(in_removed):
                continue                    # W9c: it goes with the gear taken out
            structural.append(f"The mesh {'–'.join(sorted(pair))} is no longer listed, and Update SolidWorks cannot "
                              "take one out.")
        try:
            features = layout.layout_features(shafts)
            layout_values = DocumentValues(box.layout, layout.layout_globals(shafts), features,
                                           recorded=_recorded_layout(box), cells=_shaft_cells(spec, shafts),
                                           made=features)
        except ValueError as exc:
            return UpdatePlan(refusal=str(exc))
        if not exists(box.layout):
            missing.append(box.layout)
        # W7 (W7-INTERFACES §6.3): every carrier part on record, always, with the globals it should hold now.
        try:
            carrier_values, carriers_moved, carrier_why = _carrier_parts(box, a)
        except ValueError as exc:
            return UpdatePlan(refusal=str(exc))
        structural.extend(carrier_why)
        missing.extend(c.path for c in box.carriers if not exists(c.path))

    # The parts, each against the part its gears now want.
    parts: List[PartUpdate] = []
    band_changes: List[Any] = []
    for entry in entries:
        if not exists(entry.path):
            missing.append(entry.path)
        jobs = []
        for gear in entry.gears:
            job = job_of.get(gear)
            if job is not None and job not in jobs:
                jobs.append(job)
        if not jobs:
            continue                        # every gear it served is gone: said above
        if len(jobs) > 1:
            first = jobs[0].gear_ids[0]
            others = [g for j in jobs[1:] for g in j.gear_ids if g in entry.gears]
            structural.append(f"{_names(entry.gears)} share {os.path.basename(entry.path)}, but {_names(others)} "
                              f"now {'differs' if len(others) == 1 else 'differ'} from {first}, so they need parts "
                              "of their own.")
            continue
        toggle = _band_toggle(entry, jobs[0]) if turning else None
        if toggle is None:
            update, why = _part(entry, jobs[0], exists)
        else:
            # W9c (§2.4): bands given to or taken from a built sleeve go in place; the rest of the part is judged as
            # if neither had bands, and its values carry no band global until the bands' own step adds them.
            update, why = _part(*_without_bands(entry, jobs[0]), exists)
            if not why:
                update = replace(update, spec=jobs[0].spec, changed=True,
                                 recorded=tuple((str(p[0]), str(p[1])) for p in entry.variables if len(p) == 2)
                                 or None)
                band_changes.append(_band_change(entry, jobs[0], toggle,
                                                 _recorded_features(entry.path, read_sidecar) or ()))
        if why:
            structural.append(why)
        made = _recorded_features(entry.path, read_sidecar) or update.made
        if toggle:
            made = tuple(made) + tuple(f for f in _RELIEF_FEATURES if f not in made)      # C2: the relief is the app's
        parts.append(replace(update, cells=_gear_cells(spec, entry.gears), made=made))

    # The assembly: every gear's wanted frame, by the Name2 on record.
    placements: List[Placement] = []
    replaced: List[str] = []
    assembly = ""
    if box is not None:
        assembly = box.assembly
        if not exists(assembly):
            missing.append(assembly)
        placed = a.report.layout.placed
        # W8: with modes, the frames wanted in the configuration the assembly was saved in (the record's first mode,
        # found ignoring case), which is what ``ComponentEntry.rotation`` / ``at`` hold; else the one layout's.
        by_mode = _wanted_by_mode(box, a)
        # W9c (C11): with the record's first mode taken out, the next one on record is the mode the record opens in.
        first = next((c for c in box.modes if c in by_mode), None)
        wanted = by_mode[first] if first is not None else layout.frames(a.report)
        sliding = _recorded_sliders(box)
        # W7 (W7-INTERFACES §6.4): each carrier is a placement too, pitch 0, its frame as the carrier part goes now.
        carrier_frames = _carrier_frames(a)
        for entry in box.carriers:
            f = carrier_frames.get(entry.shaft)
            if f is None:
                continue
            cid = layout.carrier_id(entry.shaft)
            placements.append(Placement(cid, entry.component, f.rotation, f.at, 0.0, part=entry.path))
            if not (entry.rotation and entry.at and same_frame(entry.rotation, entry.at, f.rotation, f.at, 0.0)):
                replaced.append(cid)
        for c in box.components:
            if c.gear not in wanted:
                continue
            f, step = wanted[c.gear], layout.pitch(placed[c.gear])
            placements.append(Placement(c.gear, c.name, f.rotation, f.at, step, part=c.part))
            # W8: a slider's place along its shaft is its slide mate's value, set per configuration (J14), never a
            # put: it is re-placed only when its frame differs otherwise.
            at = list(c.at)
            if c.gear in sliding and len(at) == 3:
                at[2] = f.at[2]
            if not (c.rotation and c.at and same_frame(c.rotation, at, f.rotation, f.at, step)):
                replaced.append(c.gear)
        for gear in in_added:              # W9c (C1): its Name2 is the worker's to fill once inserted
            if gear in wanted:
                f = wanted[gear]
                placements.append(Placement(gear, "", f.rotation, f.at, layout.pitch(placed[gear]),
                                            part=job_of[gear].path))

    turn = _Turning()
    modal = _Modes()
    in_place = swbuild.InPlace()
    in_place_record: Optional[InPlaceRecord] = None
    leftovers: Tuple[Tuple[str, str], ...] = ()
    if turning:
        turn = _turning(box, entries, a, shafts)
        structural.extend(turn.structural)
        modal = _modes(box, a, turn, placements, added_gears=in_added)
        structural.extend(modal.structural)
        # A part a stopped press built for a gear it did not insert is on record though no component names it yet
        # (the coordinator's ruling): the added gear takes it as a part on record.
        held = list(entries) + [p for p in record.parts if p.revision == box.revision and p.gears
                                and not any(p is e for e in entries) and exists(p.path)]
        in_place, why, in_place_record = _in_place(whole_box, box, a, held, in_added, in_removed, job_of, modal,
                                                   band_changes)
        if in_place and whole_box.left:
            in_place = replace(in_place, left=tuple(whole_box.left))         # F1: a stopped press's leftovers
        leftovers = _leftovers_unwanted(record, whole_box, a, in_place)
        structural.extend(why)
        if in_place_record is not None and (modal.motion or turn.motion) is not None:
            links = _new_links(in_place_record.mates, a, modal.configurations or tuple(box.modes))
            target = modal.motion or turn.motion
            target = replace(target, meshes=target.meshes + links[0], locks=target.locks + links[1])
            if modal.motion is not None:
                modal.motion = target
            else:
                turn.motion = target
    elif box is not None and (spec.modes or _slider_ids(a)):
        structural.append(_STATIC_MODES)

    if box is None:
        carrier_values, carriers_moved = (), ()
    # W9a (K11, ruling 3 after package A's review): the record's mark on each file goes with what the record says it
    # holds; the worker vouches for a marked file only when it stayed open, modified, since the Update that marked
    # it (swbuild._vouches), and a lost Update keeps W8's set-back.
    mark_of = lambda path: _mark(record, path)                                       # noqa: E731
    parts = [replace(p, mark=mark_of(p.path)) for p in parts]
    if layout_values is not None:
        layout_values = replace(layout_values, mark=mark_of(layout_values.path))
    carrier_values = [replace(c, mark=mark_of(c.path)) for c in carrier_values]
    moving = modal.motion or turn.motion
    if moving is not None and box is not None:
        moving = _with_user_work(moving, box, spec, mark_of(box.assembly))
    return UpdatePlan(parts=tuple(parts), layout=layout_values, assembly=assembly, placements=tuple(placements),
                      moved_shafts=tuple(moved), replaced=tuple(replaced), structural=tuple(structural),
                      missing=tuple(dict.fromkeys(missing)), unsaved=tuple(record.current_marks(record.unsaved)),
                      shafts=shafts, motion=moving, axial=turn.axial, ratios=turn.ratios,
                      drag=turn.drag, modes_changed=modal.changed,
                      resensed=turn.resensed, carriers=tuple(carrier_values), carriers_moved=tuple(carriers_moved),
                      carrier_layouts=_carrier_layouts_on_record(box, a), in_place=in_place,
                      in_place_record=in_place_record if in_place else None,
                      new_parts_on_disk=tuple((g.gear, g.part) for g in in_place.added
                                              if g.build is not None and exists(g.part)),
                      leftovers=leftovers)


# -- W9a: what the worker needs to tell the user's work from the app's (ISSUE-1-PLAN K1, K11; W9A-INTERFACES.md) ------

# The part globals a Gears cell sets as it is: the global's name -> the Gears column's key. A global another sets
# through a formula (Pitch Diameter, Backlash's default) has no cell, and its sentence names none.
_GLOBAL_COLUMN = {spur.TEETH: "teeth", spur.MODULE: "module", spur.BORE: "bore", spur.PRESSURE_ANGLE: "pressure_angle",
                  spur.FACE_WIDTH: "face_width", spur.BACKLASH: "backlash", spur.FILLET: "fillet",
                  spur.PROFILE_SHIFT: "profile_shift",
                  clutch.START_BAND: "start_band", clutch.END_BAND: "end_band"}      # W9b: a banded sleeve's bands


def _mark(record: LinkRecord, path: str) -> str:
    """The record's mark on a file: ``"mismatched"`` (an Update lost), ``"unsaved"`` (an Update not yet saved), or
    ``""``."""
    if any(store.same_path(path, m) for m in record.mismatched):
        return MARK_MISMATCHED
    if any(store.same_path(path, m) for m in record.unsaved):
        return MARK_UNSAVED
    return ""


def _recorded_features(path: str, read_sidecar: Optional[Callable[[str], Optional[Sidecar]]]) -> Tuple[str, ...]:
    """The features the part's ``.gear.json`` lists as the build kept them (K1: what the record lists), or ``()``
    when there is no reader, no sidecar or no list (a reused part's sidecar may hold none): then the plan's are used."""
    if read_sidecar is None:
        return ()
    try:
        sidecar = read_sidecar(store.sidecar_path(path))
    except (OSError, ValueError, store.StoreError):
        return ()
    return tuple(sidecar.record.features) if sidecar is not None and sidecar.record.features else ()


def _gear_cells(spec: Any, gears: Sequence[str]) -> Tuple[Tuple[str, str], ...]:
    """``(global, Gears cell)`` for a part's globals a cell sets: every row the part serves (a part shared by G1 and
    G3 is set by both rows, and typing one alone would split it), joined, ``"Gears!J3 and Gears!J5"``; a planet copy
    by its row."""
    rows: List[int] = []
    for gear in gears:
        found = spec.gear(gear) or spec.gear(gear.split(" copy ")[0])
        if found is not None and found.row and found.row not in rows:
            rows.append(found.row)
    if not rows:
        return ()
    return tuple((name, _names([spec.cell("Gears", row, key) for row in rows])) for name, key in _GLOBAL_COLUMN.items())


def _shaft_cells(spec: Any, shafts: Sequence[ShaftLayout]) -> Tuple[Tuple[str, str], ...]:
    """``(layout global, Shafts cell)``: ``"S2 X"`` -> its shaft's X cell, and so for Y and Z."""
    out: List[Tuple[str, str]] = []
    for s in shafts:
        found = spec.shaft(s.shaft)
        if found is None or not found.row:
            continue
        for name, key in ((s.x_global, "x"), (s.y_global, "y"), (s.z_global, "z")):
            if name:
                out.append((name, spec.cell("Shafts", found.row, key)))
    return tuple(out)


def _recorded_layout(box: GearboxRecord) -> Optional[Tuple[Tuple[str, str], ...]]:
    """The layout's globals as the record's shafts say the file holds them (``layout.layout_globals`` of the shafts
    on record), or None when they cannot be read."""
    try:
        was = tuple(ShaftLayout(**asdict(entry)) for entry in box.shafts)
        return tuple((g.name, g.expression) for g in layout.layout_globals(was))
    except (TypeError, ValueError):
        return None


def _with_user_work(moving: MotionUpdate, box: GearboxRecord, spec: Any, mark: str) -> MotionUpdate:
    """The motion path's W9a fields: the layout's Name2 on record; ``record_holds`` (the record's word is given) and
    the assembly's ``mark``, from which the worker decides whether it vouches; each Face Z as the record holds it (``|z_front|`` of its along mate, keyed as
    ``face_globals`` is, by the gear's row); and the cell each Face Z (the gear's At) and each slide (its Slides)
    is set by."""
    rows = {g.name: row for row, g in moving.face_globals}
    faces = tuple((rows[m.face_global], equations.literal(round(abs(float(m.z_front)), 9))) for m in box.mates
                  if m.kind == motion.ALONG and m.face_global in rows)
    cells: List[Tuple[str, str]] = []
    for row, variable in moving.face_globals:
        gear = spec.gear(row)
        if gear is not None and gear.row:
            cells.append((variable.name, spec.cell("Gears", gear.row, "at")))
    for mate in moving.mates:
        if mate.kind == "slide" and mate.gears:
            gear = spec.gear(mate.gears[0])
            if gear is not None and gear.row:
                cells.append((mate.name, spec.cell("Gears", gear.row, "slides")))
    return replace(moving, layout_component=box.layout_component, record_holds=True, assembly_mark=mark,
                   recorded_faces=tuple(dict(faces).items()), cells=tuple(cells))


# -- W7: a planetary stage on record (W7-PLAN §2.10; W7-INTERFACES §6.1, §6.3, §6.4) ------------------------------

def _carrier_layouts_on_record(box: Optional[GearboxRecord], a: Assessment) -> Tuple[Any, ...]:
    if box is None or not box.carriers:
        return ()
    try:
        current = {c.shaft: c for c in layout.carrier_layouts(a.spec, a.report)}
    except ValueError:
        return ()
    return tuple(current[c.shaft] for c in box.carriers if c.shaft in current)


def _carrier_frames(a: Assessment) -> Dict[str, Any]:
    """Each carrier part's frame as the rows now put it (``layout.carrier_frame``), by carrier shaft."""
    try:
        return {c.shaft: layout.carrier_frame(c) for c in layout.carrier_layouts(a.spec, a.report)}
    except ValueError:
        return {}


def _recorded_carrier_layout(entry: Any) -> Any:
    from .layout import CarrierLayout
    return CarrierLayout(entry.shaft, 0.0, 0.0, 0.0, tuple(entry.direction or (0.0, 0.0, 1.0)),
                         tuple(ShaftLayout(**asdict(axis)) for axis in entry.axes))


def _carrier_parts(box: GearboxRecord, a: Assessment) -> Tuple[List[DocumentValues], List[str], List[str]]:
    """``(every carrier part on record with the globals and features it should hold now, the carriers whose planet
    axes move, the structural sentences)``: a copy's coordinate changing side of the carrier part's base plane, or
    reaching or leaving it, is structural as the layout's is (``OFFSET_GLOBAL_CROSSES_ZERO`` False); any other move
    of a planet on its carrier is a value Update of the carrier part. A carrier no longer one is said by
    :func:`_planetary_structural`."""
    if not box.carriers:
        return [], [], []
    current = {c.shaft: c for c in layout.carrier_layouts(a.spec, a.report)}
    values: List[DocumentValues] = []
    moved: List[str] = []
    why: List[str] = []
    for entry in box.carriers:
        now = current.get(entry.shaft)
        if now is None:
            continue
        drawn = layout.carrier_shafts(now)
        was = layout.carrier_shafts(_recorded_carrier_layout(entry))
        features = layout.layout_features(drawn)
        values.append(DocumentValues(entry.path, layout.layout_globals(drawn), features,
                                     recorded=tuple((g.name, g.expression) for g in layout.layout_globals(was)),
                                     made=features))
        if layout.layout_globals(drawn) != layout.layout_globals(was):
            moved.append(entry.shaft)
        old = {x.shaft: x for x in was}
        if len(was) != len(drawn):
            continue                               # the number of copies changed: said once, as structural
        for axis in drawn:
            before = old.get(axis.shaft)
            if before is None:
                continue
            for coordinate, p, q in (("X", before.x, axis.x), ("Y", before.y, axis.y)):
                text = _side_change(axis.shaft, coordinate, p, q)
                if text:
                    why.append(text.replace("a new layout part", f"a new carrier part for {entry.shaft}")
                               .replace("the layout part has no plane", f"the carrier part of {entry.shaft} has no "
                                                                         "plane")
                               .replace("its layout plane", "its carrier plane"))
    return values, moved, why


def _planetary_structural(box: GearboxRecord, a: Assessment) -> List[str]:
    """What a planetary stage on record cannot take through Update (W7-PLAN §2.10): the number of copies changed;
    a planet shaft now mounted on another carrier, or on the frame; a shaft becoming or ceasing to be a carrier."""
    from . import planetary
    spec = a.spec
    out: List[str] = []
    recorded_carriers = [c.shaft for c in box.carriers]
    if not recorded_carriers and not planetary.carriers(spec):
        return out
    built_on: Dict[str, str] = {}
    for entry in box.carriers:
        for axis in entry.axes:
            built_on.setdefault(planetary.copy_of(axis.shaft)[0], entry.shaft)
    shafts = {x.id: x for x in spec.shafts if x.id}
    for planet, carrier in built_on.items():
        shaft = shafts.get(planet)
        if shaft is None or shaft.mount() == carrier:
            continue
        where = "on the frame" if shaft.mount() == "frame" else f"mounted on {shaft.mount()}"
        out.append(f"{planet} is now {where} where it was built on {carrier}, and its mates hold it to {carrier}'s "
                   f"axes, {_REBUILD}.")
    now_carriers = planetary.carriers(spec)
    for c in now_carriers:
        if c not in recorded_carriers:
            out.append(f"{c} now carries planets where it was built carrying none, and the assembly has no carrier "
                       f"part for it, {_REBUILD}.")
    for c in recorded_carriers:
        if c not in now_carriers and c in shafts:
            out.append(f"{c} carries no planet now where it was built as a carrier, and its carrier part cannot be "
                       f"taken out of the assembly, {_REBUILD}.")
    placed = a.report.layout.placed
    was: Dict[str, int] = {}
    for c in box.components:
        if c.of:
            was[c.of] = was.get(c.of, 0) + 1
    now: Dict[str, int] = {}
    for p in placed.values():
        if p.carrier:
            now[p.row] = now.get(p.row, 0) + 1
    for row in sorted(set(was) | set(now), key=lambda r: [g.id for g in spec.gears].index(r)
                      if r in [g.id for g in spec.gears] else 0):
        gear = spec.gear(row)
        before = was.get(row, 1 if any(c.gear == row for c in box.components) else 0)
        after = now.get(row, 1 if row in placed else 0)
        if gear is None or not before or not after or before == after:
            continue
        shaft = gear.shaft
        out.append(f"{shaft} now has {after} {'copy' if after == 1 else 'copies'} where it was built with {before}, "
                   f"and Update SolidWorks cannot add or take out a planet, {_REBUILD}.")
    return out


# -- a gearbox built to turn (W5-PLAN §1.6's classify, as W5-DECISIONS and W5-INTERFACES amend it) ------------------

_REBUILD = "so the gearbox needs building again"


def _axis_word(sigma: int) -> str:
    return "Z+" if sigma > 0 else "Z-"


def _direction(shaft: Any) -> Tuple[float, ...]:
    """A shaft's direction (a ``ShaftLayout`` or a recorded ``ShaftEntry``), as compared (W6-INTERFACES §7.7: never
    ``sigma`` or the ``axis`` text, which are for sentences)."""
    direction = tuple(float(v) for v in (getattr(shaft, "direction", None) or ()))
    return direction or (0.0, 0.0, float(getattr(shaft, "sigma", 1) or 1))


def _axis_name(shaft: Any) -> str:
    return getattr(shaft, "axis", "") or _axis_word(int(_direction(shaft)[2] or 1))


def _cardinal(direction: Sequence[float]) -> Optional[int]:
    """The index (0 X, 1 Y, 2 Z) of the base axis ``direction`` lies along, either way; None for a slant."""
    for index, value in enumerate(direction):
        if abs(abs(float(value)) - 1.0) <= 1e-9:
            return index
    return None


def _slanted(shaft: Any) -> bool:
    """A shaft the layout holds as a fixed line (``line``; a slant), recorded or as now read."""
    return bool(getattr(shaft, "line", "")) or _cardinal(_direction(shaft)) is None


def _slant_change(old: Any, new: Any) -> str:
    """W6 (D4, W6-PLAN §2.7, §2.9): a slanted shaft's point or direction changing, which a fixed line axis cannot
    follow: *S3's axis slants, and the layout holds a slanted axis as a fixed line: its point moved (Z 8 → 10), so
    the gearbox needs building again.* ``""`` when either is not a slant, or neither changed."""
    if not (_slanted(old) and _slanted(new)):
        return ""
    moved = [f"{c} {_number(p)} → {_number(q)}" for c, p, q in (("X", old.x, new.x), ("Y", old.y, new.y),
                                                                 ("Z", old.z, new.z)) if abs(p - q) > MOVE_TOLERANCE]
    pieces = [f"point moved ({', '.join(moved)})"] if moved else []
    if any(abs(p - q) > 1e-9 for p, q in zip(_direction(old), _direction(new))):
        pieces.append("direction changed")
    if not pieces:
        return ""
    return (f"{new.shaft}'s axis slants, and the layout holds a slanted axis as a fixed line: its "
            f"{' and its '.join(pieces)}, {_REBUILD}.")


def _family_change(old: Any, new: Any) -> str:
    """A static gearbox's shaft turned onto another base axis, or between a base axis and a slant: the layout part's
    planes and axis for it are another set, so a new layout part (a flip along one base axis is W4's move)."""
    a, b = _cardinal(_direction(old)), _cardinal(_direction(new))
    if (a is not None and a == b) or (_slanted(old) and _slanted(new)):
        return ""                                   # a flip along one base axis, or a slant's (said by _slant_change)
    return (f"{new.shaft}'s axis is now {_axis_name(new)} where it was built {_axis_name(old)}: the layout part's "
            "planes and axis for it keep the direction they were made with, so it needs a new layout part.")


def _plural(items: Sequence[str], one: str, many: str) -> str:
    return one if len(items) == 1 else many


def _number_or_none(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def _bad_mates(box: GearboxRecord) -> str:
    """A refusal sentence for the first mate on record Update cannot act on — a kind the app does not make, the
    wrong number of gears for its kind, no name, an axis or along mate with no shaft, a mesh whose ratio is not
    two whole tooth counts, an along mate whose distance is not a number, or a gear not in the assembly on record
    — else ``""``. A hand-edited or damaged record is refused with a sentence, never an IndexError.

    W8: a slide mate holds one gear and names its shaft, as an axis mate does, and its places are numbers other than
    0; a spline or coupling holds two gears and a sense, as a mesh does; an on-set is a list of names."""
    known = {c.gear for c in box.components} | {layout.carrier_id(c.shaft) for c in box.carriers if c.shaft}
    tail = (", so Update SolidWorks cannot act on the gearbox the record describes: Build again… makes a new revision "
            "from the workbook instead.")
    for entry in box.mates:
        name = entry.name if isinstance(entry.name, str) else ""
        label = f"The record of what was built lists the mate \"{name}\"" if name else (
            "The record of what was built lists a mate with no name")
        kind = entry.kind
        if kind not in motion.MATE_KINDS:
            article = "an" if str(kind)[:1].lower() in "aeiou" else "a"
            return f"{label} as {article} {kind!r} mate, which is not a kind of mate the app makes{tail}"
        one_gear = (motion.AXIS, motion.ALONG, motion.SLIDE)          # W8: a slide holds its slider alone
        want = 1 if kind in one_gear else 2
        gears = list(entry.gears) if isinstance(entry.gears, (list, tuple)) else []
        if len(gears) != want or not all(isinstance(g, str) and g for g in gears):
            return (f"{label} with {len(gears)} gear{'' if len(gears) == 1 else 's'} where a {kind} mate holds "
                    f"{want}{tail}")
        if not name:
            return f"{label}, and Update SolidWorks finds each mate by its name{tail}"
        if kind in one_gear and not (isinstance(entry.shaft, str) and entry.shaft):
            return f"{label} with no shaft, where a {kind} mate names the shaft it holds its gear to{tail}"
        values = getattr(entry, "values", {}) or {}
        if kind == motion.SLIDE and not (isinstance(values, dict) and all(
                isinstance(k, str) and k and _number_or_none(v) for k, v in values.items())):
            return (f"{label} with the places {values!r}, where a slide mate holds a distance other than 0 for each "
                    f"mode{tail}")
        on_set = getattr(entry, "modes", []) or []
        if not (isinstance(on_set, (list, tuple)) and all(isinstance(m, str) and m for m in on_set)):
            return f"{label} on in {on_set!r}, where a mate is on in modes named on the Modes sheet{tail}"
        if kind == motion.ALONG and _number_or_none(entry.z_front) is None:
            return f"{label} with the distance {entry.z_front!r}, which is not a number{tail}"
        plane = getattr(entry, "plane", motion.FRONT_PLANE)
        if kind == motion.ALONG and plane not in motion.PLANES:
            return (f"{label} measured from the plane {plane!r}, where an along mate is measured from the Front, Top "
                    f"or Right plane{tail}")
        sense = getattr(entry, "sense", 0)
        if kind in (motion.MESH, motion.COUPLE, motion.SPLINE) and (isinstance(sense, bool)
                                                                      or sense not in (-1, 0, 1)):
            return f"{label} with the sense {sense!r}, where a gear mate's sense is -1 or +1{tail}"
        if kind == motion.MESH:
            ratio = list(entry.ratio) if isinstance(entry.ratio, (list, tuple)) else []
            counts = [_number_or_none(n) for n in ratio]
            if len(counts) != 2 or not all(n is not None and n > 0 and n == int(n) for n in counts):
                return f"{label} with the ratio {entry.ratio!r}, where a gear mate holds two tooth counts{tail}"
        strangers = [g for g in gears if g not in known]
        if strangers:
            return (f"{label} on {_names(strangers)}, which {_is(strangers)} not in the assembly on "
                    f"record{tail}")
    return ""


@dataclass
class _Turning:
    """What :func:`_turning` found: sentences for a new revision, and what the worker's motion path is given."""

    structural: List[str] = field(default_factory=list)
    motion: Optional[MotionUpdate] = None
    axial: Tuple[str, ...] = ()
    ratios: Tuple[str, ...] = ()
    drag: Tuple[str, ...] = ()
    resensed: Tuple[str, ...] = ()


def _built_part(entries: Sequence[PartEntry], gear: str) -> Dict[str, Any]:
    """The spec (``GearSpec.to_dict``) of the part on record that holds ``gear``, or ``{}``."""
    entry = next((p for p in entries if gear in p.gears and p.spec), None)
    return dict(entry.spec) if entry is not None else {}


def _axial_edit(gear: str, shaft: str, z_front: float, along: float, built_shaft_z: Optional[float],
                shaft_z: float, built_face: Optional[float], face: float, at: float, *, coordinate: str = "Z",
                cone: bool = False, moves: Optional[List[str]] = None) -> Tuple[str, str]:
    """``(subject and verb, object)`` naming the edit that moves ``gear`` along its shaft (W5-DECISIONS answer 3:
    the sentence names the edit, never only the plane): *G1's face width (15 → 20) moves* / *its front face*;
    *G4's At (27 → 30) and S3's Z (0 → 5) move* / *G4's front face*. The built At is worked back from the
    built front face, the shaft's built Z and the part's built face width; an edit that cannot be told is left
    out, and with none told the subject is the gear's front face itself.

    W6: ``z_front`` and the shaft's coordinates are along the measuring plane's normal (``coordinate``: X for
    Right, Y for Top, Z for Front), and ``along`` the shaft direction's component there (W5's sigma on Z). A bevel
    gear (``cone``) is placed by its cone tip, which its face width does not move: *G1's At (0 → 2) moves* / *its
    cone tip*.

    W7: ``moves``, when given, names the shaft edits in place of ``"<shaft>'s Z (a → b)"`` — a planet's, whose
    place along its axis is its carrier's Z plus its own offset: *C's Z (0 → -5) moves* / *Planet's front face*."""
    gear_edits: List[str] = []
    thing = "cone tip" if cone else "front face"
    if not cone and built_face is not None and abs(built_face - face) > MOVE_TOLERANCE:
        gear_edits.append(f"face width ({_number(built_face)} → {_number(face)})")
    if (cone or built_face is not None) and built_shaft_z is not None and along:
        built_at = (z_front - built_shaft_z) / along + (0.0 if cone else built_face / 2.0)
        if abs(built_at - at) > MOVE_TOLERANCE:
            gear_edits.append(f"At ({_number(built_at)} → {_number(at)})")
    moved = built_shaft_z is not None and abs(built_shaft_z - shaft_z) > MOVE_TOLERANCE
    shaft_parts = [f"{shaft}'s {coordinate} ({_number(built_shaft_z)} → {_number(shaft_z)})"] if moved else []
    if moves is not None:
        shaft_parts, moved = list(moves), bool(moves)
    parts = ([f"{gear}'s " + " and ".join(gear_edits)] if gear_edits else []) + shaft_parts
    if not parts:
        return f"{gear}'s {thing} moves", ""
    verb = "moves" if len(gear_edits) + len(shaft_parts) == 1 else "move"
    return f"{' and '.join(parts)} {verb}", (f"its {thing}" if not moved else f"{gear}'s {thing}")


def _drag(spec: Any, of_kind: Mapping[str, Sequence[MateEntry]], built_on: Mapping[str, str]) -> Tuple[str, ...]:
    """Each train's drag gear as the workbook now has it, from the record's mates (``motion.motion_plan``'s rule:
    the shafts the gear mates join, input shafts first then Shafts-sheet order, the trains in the order of their
    first shaft; the anchor of each train's first shaft). Moving the input to another shaft is an Update, and the
    footer's drag gear follows it."""
    order = {s.id: i for i, s in enumerate(spec.shafts)}
    role = {s.id: s.role for s in spec.shafts}
    anchor_of = {m.shaft: m.gears[0] for m in of_kind[motion.AXIS]}
    parent: Dict[str, str] = {}

    def root(x: str) -> str:
        while parent.setdefault(x, x) != x:
            x = parent[x]
        return x
    joined: List[str] = []
    for m in of_kind[motion.MESH]:
        a, b = (built_on.get(g) for g in m.gears)
        if a and b:
            parent[root(a)] = root(b)
            joined += [s for s in (a, b) if s not in joined]
    joined.sort(key=lambda s: order.get(s, len(order)))
    out: List[str] = []
    seen = set()
    for shaft in joined:
        if root(shaft) in seen:
            continue
        seen.add(root(shaft))
        members = [s for s in joined if root(s) == root(shaft)]
        first = next((s for s in members if role.get(s) == "input"), members[0])
        if first in anchor_of:
            out.append(anchor_of[first])
    return tuple(out)


def _turning(box: GearboxRecord, entries: Sequence[PartEntry], a: Assessment,
             shafts: Sequence[ShaftLayout]) -> _Turning:
    """Classify an edit of a gearbox built to turn, from the record's own mates (anchors are never worked out
    again: a reordered Gears sheet keeps them) and the new read. Called once :func:`_bad_mates` passed.

    **Structural** (each a sentence naming the edit): a mated shaft's Z±
    flipped; a mated gear now on another shaft; a gear built fixed whose
    shaft now turns, or one built mated whose shaft's Role is now ``fixed``
    or that now stands still through a fixed shaft (review M9, as a Role
    change); an anchor's front face reaching, leaving or crossing the
    Front plane (W5-DECISIONS answer 3); a meshed gear's tooth change while
    ``findings.GEAR_MATE_RATIO_ROUTE`` is not ``"remake"`` (ruling c); a
    follower's place along its shaft changing unless
    ``findings.LOCK_RETAKES_AN_OFFSET`` is True. **An Update**: an anchor's
    move along its shaft on one side of the Front plane (its Face Z), a
    follower's (the lock re-takes it), layout moves, turn-backs, and a tooth
    change by remake (a ratio, in the record's gear order: review M10)."""
    spec = a.spec
    placed = a.report.layout.placed
    wanted = layout.frames(a.report)
    out = _Turning()
    now = {s.shaft: s for s in shafts}
    before = {s.shaft: s for s in box.shafts}
    gear_of = {g.id: g for g in spec.gears}

    def row_of(gear: str) -> str:                  # W7: a copy's Gears row
        return (placed[gear].row or gear) if gear in placed else gear
    components = {c.gear: c for c in box.components}
    order = {s.id: i for i, s in enumerate(spec.shafts)}
    mates = list(box.mates)
    of_kind = {kind: [m for m in mates if m.kind == kind] for kind in motion.MATE_KINDS}
    built_on: Dict[str, str] = {}                  # each mated gear's shaft as built
    for m in of_kind[motion.AXIS] + of_kind[motion.ALONG]:
        built_on[m.gears[0]] = m.shaft
    for m in of_kind[motion.LOCK]:
        if m.gears[0] in built_on:
            built_on[m.gears[1]] = built_on[m.gears[0]]
    told: set = set()                              # gears an edit was said for: one edit, one sentence

    flipped = set()
    for m in of_kind[motion.AXIS]:
        old, new = before.get(m.shaft), now.get(m.shaft)
        if old is None or new is None:
            continue
        if _slant_change(old, new):                # said by classify: a fixed line moved or turned
            told.update(g for g, s in built_on.items() if s == m.shaft)
            continue
        if _direction(old) == _direction(new):
            continue
        flipped.add(m.shaft)
        told.update(g for g, s in built_on.items() if s == m.shaft)
        out.structural.append(f"{m.shaft}'s axis is now {_axis_name(new)} where it was built {_axis_name(old)}: the "
                              f"layout's axis and the mates on it keep the direction they were made with, {_REBUILD}.")

    for gear, shaft in built_on.items():
        row = gear_of.get(gear)
        if row is None or row.shaft == shaft or gear in told:
            continue
        if shaft not in now:
            told.add(gear)                         # its shaft is gone or renamed, which is said already
            continue
        holding = [m.name for m in mates if (m.kind in (motion.AXIS, motion.ALONG) and m.gears[0] == gear)
                   or (m.kind == motion.LOCK and m.gears[1] == gear)]
        told.add(gear)
        out.structural.append(f"{gear} is now on {row.shaft} where it was built on {shaft}: the "
                              f"{_plural(holding, 'mate', 'mates')} {_names(holding)} "
                              f"{_plural(holding, 'holds', 'hold')} it to {shaft}, {_REBUILD}.")

    still = motion.still_shafts(spec, a.report)
    fixed_now = {g for g, p in placed.items() if p.shaft in still}
    was_fixed = set(box.fixed)
    in_box = [c.gear for c in box.components if c.gear in placed and c.gear not in told]
    freed: Dict[str, List[str]] = {}
    held: Dict[str, List[str]] = {}
    for gear in in_box:
        if gear in was_fixed and gear not in fixed_now:
            freed.setdefault(placed[gear].shaft, []).append(gear)
        elif gear not in was_fixed and gear in fixed_now:
            held.setdefault(placed[gear].shaft, []).append(gear)
    for shaft in sorted(freed, key=lambda s: order.get(s, len(order))):
        names = freed[shaft]
        told.update(names)
        out.structural.append(f"{_names(names)} {_plural(names, 'was', 'were')} built fixed, but {shaft} now turns "
                              "(its Role is not fixed and no fixed shaft holds it still), so the gearbox needs "
                              f"building again to mate {_plural(names, 'it', 'them')} to turn.")
    for shaft in sorted(held, key=lambda s: order.get(s, len(order))):
        names = held[shaft]
        told.update(names)
        why = (f"{shaft}'s Role is now fixed" if not still.get(shaft) else
               f"{shaft} now stands still, held through the fixed shaft {still[shaft]}")
        out.structural.append(f"{why}, but {_names(names)} {_plural(names, 'was', 'were')} built mated to turn, so "
                              f"the gearbox needs building again to hold {_plural(names, 'it', 'them')} fixed.")

    def point(shaft: Any) -> Tuple[float, float, float]:
        return (float(shaft.x), float(shaft.y), float(shaft.z))

    def edit(gear: str, shaft: str, z_front: float, index: int = 2) -> Tuple[str, str]:
        old, new = before.get(shaft), now.get(shaft)
        direction = _direction(new) if new is not None else tuple(placed[gear].axis)
        built_face = _number_or_none(_built_part(entries, gear).get("face_width"))
        return _axial_edit(gear, shaft, z_front, direction[index], point(old)[index] if old is not None else None,
                           point(new)[index] if new is not None else placed[gear].centre[index], built_face,
                           placed[gear].face, _number_or_none(gear_of[row_of(gear)].at or 0) or 0.0,
                           coordinate="XYZ"[index], cone=bool(getattr(placed[gear], "bevel", False)))

    recorded_offsets = {axis.shaft: axis for entry in box.carriers for axis in entry.axes}

    def planet_edit(gear: str, z_front: float, index: int) -> Tuple[str, str]:
        """A planet copy's edit, named through its carrier: its place along its axis is the carrier's coordinate
        plus its own offset (W7-PLAN §2.1); either may have moved."""
        p = placed[gear]
        row, carrier, planet = p.row or gear, p.carrier, planetary.copy_of(p.shaft)[0]
        old_c, new_c = before.get(carrier), now.get(carrier)
        along = (_direction(new_c) if new_c is not None else tuple(p.axis))[index]
        shaft_row = next((x for x in spec.shafts if x.id == planet), None)
        old_axis = recorded_offsets.get(p.shaft)
        new_off = _number_or_none(shaft_row.z or 0) if shaft_row is not None else None
        old_off = float(old_axis.z) if old_axis is not None else new_off
        moves: List[str] = []
        letter = "XYZ"[index]
        if old_c is not None and new_c is not None and abs(point(old_c)[index] - point(new_c)[index]) > MOVE_TOLERANCE:
            moves.append(f"{carrier}'s {letter} ({_number(point(old_c)[index])} → {_number(point(new_c)[index])})")
        if old_off is not None and new_off is not None and abs(old_off - new_off) > MOVE_TOLERANCE:
            moves.append(f"{planet}'s Z on {carrier} ({_number(old_off)} → {_number(new_off)})")
        built = (point(old_c)[index] + along * (old_off or 0.0)) if old_c is not None else None
        wanted_point = (point(new_c)[index] if new_c is not None else 0.0) + along * (new_off or 0.0)
        built_face = _number_or_none(_built_part(entries, row).get("face_width"))
        return _axial_edit(row, planet, z_front, along, built, wanted_point, built_face, p.face,
                           _number_or_none(gear_of[row].at or 0) or 0.0, coordinate=letter, moves=moves)

    face_globals: List[Tuple[str, GlobalVariable]] = []
    axial: List[str] = []
    for m in of_kind[motion.ALONG]:
        gear = m.gears[0]
        if gear not in wanted or row_of(gear) not in gear_of:
            continue
        plane = m.plane or motion.FRONT_PLANE
        index = motion._PLANE_INDEX.get(plane, 2)
        old_z, new_z = float(m.z_front), float(wanted[gear].at[index])
        row = placed[gear].row or gear                 # W7 (§6.7): a planet's copies share one global, by row
        if m.face_global and all(g.name != m.face_global for _, g in face_globals):
            face_globals.append((row, GlobalVariable(m.face_global, equations.literal(round(abs(new_z), 9)))))
        if gear in told:
            continue
        was, is_ = layout.side(old_z), layout.side(new_z)
        if was == is_:
            if m.face_global and abs(new_z - old_z) > MOVE_TOLERANCE and row not in axial:
                axial.append(row)
            continue
        told.add(gear)
        names = [m.name]
        if placed[gear].carrier:
            # W7: the copies of a planet move together; one sentence for the row, naming the edit through its
            # carrier (review of a22369f: a carrier's Z edit was said once per copy, without the edit).
            siblings = [x for x in of_kind[motion.ALONG] if x.gears[0] in placed and x.gears[0] != gear
                        and placed[x.gears[0]].row == row and placed[x.gears[0]].carrier]
            told.update(x.gears[0] for x in siblings)
            names += [x.name for x in siblings]
            subject, what = planet_edit(gear, old_z, index)
        else:
            subject, what = edit(gear, m.shaft, old_z, index)
        named = f"the {plane.capitalize()} plane"
        mates_ = (f"the mate {names[0]} holds" if len(names) == 1 else
                  f"the mates {', '.join(names[:-1])} and {names[-1]} hold")
        if was == layout.BASE:
            where, why = f"off {named}", f"{mates_} it on that plane and cannot take a distance"
        elif is_ == layout.BASE:
            where, why = (f"onto {named}", f"{mates_} it at a distance from that plane and cannot reach it")
        else:
            where, why = (f"across {named}", f"the mate {m.name} cannot carry its distance across that plane"
                          if len(names) == 1 else f"the mates {', '.join(names[:-1])} and {names[-1]} cannot carry "
                                                  "its distance across that plane")
        out.structural.append(f"{subject} {what + ' ' if what else ''}{where} ({'xyz'[index]} {_number(old_z)} → "
                              f"{_number(new_z)}): {why}, {_REBUILD}.")

    retakes = getattr(findings, "LOCK_RETAKES_AN_OFFSET", None)
    for m in of_kind[motion.LOCK]:
        anchor, follower = m.gears
        c = components.get(follower)
        if follower in told or follower not in wanted or row_of(follower) not in gear_of or c is None or len(c.at) < 3:
            continue
        shaft = built_on.get(follower, placed[follower].shaft)
        index = motion._PLANE_INDEX[motion.along_plane(_direction(now[shaft]) if shaft in now
                                                       else placed[follower].axis)]
        old_z, new_z = float(c.at[index]), float(wanted[follower].at[index])
        if abs(old_z - new_z) <= MOVE_TOLERANCE or retakes is True:
            continue
        told.add(follower)
        subject, what = edit(follower, shaft, old_z, index)
        if retakes is None:
            why = (f"whether its lock to {anchor} takes a new place along the shaft is not settled "
                   "(findings.LOCK_RETAKES_AN_OFFSET)")
        else:
            why = (f"the probes found that its lock to {anchor} does not take a new place along the shaft "
                   "(findings.LOCK_RETAKES_AN_OFFSET)")
        out.structural.append(f"{subject} {what + ' ' if what else ''}along {shaft} ({'xyz'[index]} "
                              f"{_number(old_z)} → {_number(new_z)}), and {why}, {_REBUILD}.")

    route = getattr(findings, "GEAR_MATE_RATIO_ROUTE", None)
    teeth = {g: int(p.teeth) for g, p in placed.items()}
    ratios: List[Tuple[str, int, int]] = []
    for m in of_kind[motion.MESH]:
        a_, b_ = m.gears
        if a_ not in teeth or b_ not in teeth:
            continue
        built = (int(m.ratio[0]), int(m.ratio[1]))
        new = (teeth[a_], teeth[b_])
        if built == new or built[0] * new[1] == built[1] * new[0]:
            continue                               # the gear mate already turns the train at this ratio
        if route == "remake":
            ratios.append((m.name, new[0], new[1]))
            continue
        changed = [f"{g}'s teeth ({old} → {n})" for g, old, n in zip(m.gears, built, new) if old != n]
        if route is None:
            why = ("and a gear mate's ratio cannot be changed in a built assembly until the probes settle how "
                   "(findings.GEAR_MATE_RATIO_ROUTE)")
        elif route == "modify definition":
            why = ("and the only way found to change a gear mate's ratio in place leaves an assembly SolidWorks 2024 "
                   "cannot close")
        else:
            why = (f"and findings.GEAR_MATE_RATIO_ROUTE is {route!r}, which this version does not know how to "
                   "follow")
        out.structural.append(f"{_names(changed)} change the gear mate {m.name} from {built[0]} : {built[1]} to "
                              f"{new[0]} : {new[1]}, {why}, {_REBUILD}.")
    out.axial = tuple(axial)
    out.ratios = tuple(name for name, _, _ in ratios)
    out.drag = _drag(spec, of_kind, built_on)

    carrier_ids = {layout.carrier_id(c.shaft) for c in box.carriers if c.shaft}
    mated = {g for m in mates for g in m.gears} - carrier_ids
    if not all(g in placed for g in mated):
        return out                                 # a mated gear is gone: said above, and there is nothing to give

    # Each gear mate's sense now (the new read's mesh, else W5's parallel rule from the placed axes) and as made
    # (the record's own; 0, a v3 or parallel entry, is taken from the read: W6-INTERFACES §7.1). A mate whose sense
    # the read changes (a crossed shaft moved to the other side of its partner) is remade by Update — the worker
    # finds it from the two senses — and named in ``resensed``; in ``UpdatePlan.ratios`` only when its teeth changed
    # too.
    sense: Dict[Tuple[str, str], int] = {}
    built_sense: Dict[Tuple[str, str], int] = {}
    resensed: List[str] = []
    for m in of_kind[motion.MESH]:
        a_, b_ = m.gears
        laid = a.report.meshes.get((a_, b_)) or a.report.meshes.get((b_, a_))      # c is the same either way round
        was_c = int(m.sense) if m.sense in (-1, 1) else 0
        if laid is not None and laid.sense in (-1, 1):
            now_c = int(laid.sense)
        elif was_c and not geometry.parallel(placed[a_], placed[b_]):
            now_c = was_c                          # a turned mesh the checks did not lay out: they say why
        else:
            now_c = motion._parallel_sense_of(placed[a_], placed[b_])
        was_c = was_c or now_c
        sense[(a_, b_)], built_sense[(a_, b_)] = now_c, was_c
        if was_c == now_c or a_ in told or b_ in told:
            continue                               # unchanged, or its gears' edit is said already
        if route == "remake":
            resensed.append(m.name)
            # In the worker's ratios too (W6-INTERFACES §7.14), its tooth counts new or not, so the motion gate
            # refuses it first while the remake route is missing; never in ``UpdatePlan.ratios`` for a sense alone.
            if all(name != m.name for name, _, _ in ratios):
                ratios.append((m.name, teeth[a_], teeth[b_]))
            continue
        if route is None:
            why = ("and making a gear mate again in a built assembly is not settled by the probes "
                   "(findings.GEAR_MATE_RATIO_ROUTE)")
        else:
            why = f"and findings.GEAR_MATE_RATIO_ROUTE is {route!r}, which this version does not follow for it"
        out.structural.append(f"{b_} now turns the other way against {a_} about its axis, so the gear mate {m.name} "
                              f"must be made again, {why}, {_REBUILD}.")
    out.resensed = tuple(resensed)

    def built_teeth(gear: str) -> int:
        value = _number_or_none(_built_part(entries, gear).get("teeth"))
        if value is None:
            value = next((float(m.ratio[m.gears.index(gear)]) for m in of_kind[motion.MESH] if gear in m.gears),
                         None)
        return int(value) if value else teeth.get(gear, 0)

    recorded = []
    for entry in box.carriers:                     # W7 (§6.4): the carrier's recorded frame, pitch 0
        if len(entry.rotation) == 9 and len(entry.at) == 3:
            recorded.append(Placement(layout.carrier_id(entry.shaft), entry.component,
                                      tuple(float(v) for v in entry.rotation), tuple(float(v) for v in entry.at), 0.0))
    for c in box.components:
        z = built_teeth(c.gear)
        if len(c.rotation) == 9 and len(c.at) == 3:
            recorded.append(Placement(c.gear, c.name, tuple(float(v) for v in c.rotation),
                                      tuple(float(v) for v in c.at), 360.0 / z if z > 0 else 0.0))
    meshes = [tuple(m.gears) for m in of_kind[motion.MESH]]
    carriers: Tuple[Any, ...] = ()
    held: Tuple[str, ...] = ()
    carrier_of: Dict[Tuple[str, str], str] = {}
    unmated: List[Tuple[str, str]] = []
    if box.carriers:
        # W7 (W7-PLAN §2.10; W7-INTERFACES §6.5, §6.6): every carrier linked, the held gears a recorded gear mate
        # touches judged (a held carrier too), and the unmated meshes judged as links beside the gear mates.
        carriers = motion.carrier_links(spec, a.report, None)
        fixed = set(box.fixed)
        touched = {g for m in of_kind[motion.MESH] for g in m.gears}
        held = tuple(g for g in box.fixed if g in touched or g in carrier_ids)
        for pair in box.unmated:
            x, y = pair
            if x in placed and y in placed and (x, y) not in sense:
                unmated.append((x, y))
                laid = a.report.meshes.get((placed[x].row or x, placed[y].row or y)) or \
                    a.report.meshes.get((placed[y].row or y, placed[x].row or x))
                c = int(laid.sense) if laid is not None and laid.sense in (-1, 1) else \
                    motion._parallel_sense_of(placed[x], placed[y])
                sense[(x, y)] = c
                built_sense[(x, y)] = c
        for x, y in list(meshes) + unmated:
            carrier = placed[x].carrier or placed[y].carrier
            if carrier:
                carrier_of[(x, y)] = layout.carrier_id(carrier)
        del fixed
    built_counts = {g: built_teeth(g) for g in placed}
    out.motion = MotionUpdate(
        mates=tuple(motion.mate_ref(m) for m in mates),
        meshes=motion.mesh_links(list(meshes) + unmated, teeth, sense, carrier_of=carrier_of),
        locks=motion.lock_links([tuple(m.gears) for m in of_kind[motion.LOCK]], teeth),
        recorded=tuple(recorded),
        recorded_meshes=tuple(motion.mesh_links([tuple(m.gears)], {m.gears[0]: int(m.ratio[0]),
                                                                    m.gears[1]: int(m.ratio[1])}, built_sense,
                                                carrier_of=carrier_of)[0]
                              for m in of_kind[motion.MESH])
        + tuple(motion.mesh_links([pair], built_counts, built_sense, carrier_of=carrier_of)[0] for pair in unmated),
        face_globals=tuple(face_globals),
        ratios=tuple(ratios),
        fixed=tuple(box.fixed),
        carriers=carriers,
        held=held)
    return out


# -- W8: a gearbox with modes on record (W8-PLAN §1.10, J14; W8-INTERFACES §9.1, §9.6, §9.9) -----------------------

_NEW_REVISION = "so it needs a new revision"
_STATIC_MODES = ("The workbook has modes or sliding gears now, and the gearbox on record was built static, while a "
                 "gearbox with modes is built to turn with a configuration per mode, so it needs building again.")


def _conf(configurations: Sequence[str], name: str) -> Optional[str]:
    """The configuration of ``configurations`` (the record's spelling) that the mode ``name`` is, compared as
    SolidWorks compares configuration names (``swbuild.on_in``, W8-INTERFACES §9.6), else None."""
    return next((c for c in configurations if on_in((c,), name)), None)


def _slider_ids(a: Assessment) -> List[str]:
    """The gears that slide in the new read, Gears-sheet order."""
    moving = {g for m in a.report.modes for g in m.positions}
    return [g.id for g in a.spec.gears if g.id in moving]


def _recorded_sliders(box: GearboxRecord) -> List[str]:
    return [m.gears[0] for m in box.mates if m.kind == motion.SLIDE and m.gears]


def _wanted_by_mode(box: GearboxRecord, a: Assessment) -> Dict[str, Dict[str, Any]]:
    """Each configuration on record (its own spelling) -> every gear's frame wanted there now
    (``layout.frames_by_mode``), for the modes the new read still has."""
    if not box.modes:
        return {}
    out = {}
    for name, frames in layout.frames_by_mode(a.report).items():
        conf = _conf(box.modes, name)
        if conf is not None:
            out[conf] = frames
    return out


def _per_mode(mates: Sequence[Any]) -> List[Any]:
    """The mates on in some modes only: every coupling, and each sliding mesh (a MESH with an on-set)."""
    return [m for m in mates if m.kind == motion.COUPLE or (m.kind == motion.MESH and m.modes)]


@dataclass
class _Modes:
    """What :func:`_modes` found: sentences for a new revision, the motion path's W8 fields, and the mates whose
    values or on-sets change."""

    structural: List[str] = field(default_factory=list)
    motion: Optional[MotionUpdate] = None
    changed: Tuple[str, ...] = ()
    # W9c (K6; W9C-INTERFACES §2, §3): the Modes rows added (the read's names, Modes-sheet order) and removed (the
    # record's spelling), the configurations after the Update (the record's order, the added after them), the
    # record's first mode when a removal changes it (C11), and the per-mode mates the read needs between gears on
    # record that are not on record (made in place as ``NewMate``s).
    modes_added: Tuple[str, ...] = ()
    modes_removed: Tuple[str, ...] = ()
    configurations: Tuple[str, ...] = ()
    first_mode: str = ""
    new_mates: Tuple[Any, ...] = ()


def _modes(box: GearboxRecord, a: Assessment, turn: _Turning, placements: Sequence[Placement],
           added_gears: Sequence[str] = ()) -> _Modes:
    """J14 on a gearbox built to turn: are all the mates the new read's modes need already on record? One SLIDE per
    slider, and each coupling and sliding mesh some mode engages, with the same gears (the new plan's own, from
    ``motion.motion_plan``: one home for which mate each mode needs, J15's loop-closers included).

    **Structural**: a Modes row renamed (W9c: a row taken out and another added in one edit is read so), the first
    Modes rows on a gearbox built with none, or every row taken out; a gear that slides now or no longer does; a mode
    whose slide value would reach or cross the Front plane (J27, naming the position); one on record that would be on
    in no mode (§9.1: never written as ``[]``), a Modes row removed that leaves one so included; with no Modes rows, a
    slider's place moving. **An Update**: a slide value per configuration, an on-set changed between mates on record;
    W9c (K6) a Modes row added or removed, and a coupling or sliding mesh some mode needs between gears on record that
    is not on record (``new_mates``). A per-mode mate touching a gear Update adds (``added_gears``) is that gear's. The Modes rows reordered change nothing (§9.9): configurations stay in the record's order and
    spelling, and names compare through ``swbuild.on_in`` (§9.6)."""
    out = _Modes()
    spec, report = a.spec, a.report
    slides = [m for m in box.mates if m.kind == motion.SLIDE and m.gears]
    per_mode = _per_mode(box.mates)
    now_sliders = _slider_ids(a)
    if not (box.modes or slides or per_mode or spec.modes or now_sliders):
        return out                                 # W7's path, untouched
    names = [m.name for m in report.modes if m.name]
    added = [n for n in names if _conf(box.modes, n) is None]
    gone = [c for c in box.modes if _conf(names, c) is None]
    if added and gone:
        out.structural.append(f"The Modes sheet has {_names(added)} where the assembly has {_names(gone)}: a mode "
                              "renamed, or one taken out and another added in one edit, keeps nothing of the user's "
                              "own states in that configuration when it is deleted and made again, and a "
                              f"configuration is not renamed in place, {_NEW_REVISION}.")
    elif added and not box.modes:
        out.structural.append(f"The Modes sheet has {'a new mode' if len(added) == 1 else 'new modes'}, "
                              f"{_names(added)}, and the assembly was built with no configuration per mode, "
                              f"{_NEW_REVISION}.")
    elif gone and not names:
        out.structural.append(f"The {_plural(gone, 'mode', 'modes')} {_names(gone)} {_is(gone)} no longer on the Modes "
                              f"sheet and no mode is left, and the assembly keeps a configuration per mode, "
                              f"{_NEW_REVISION}.")
    else:
        out.modes_added, out.modes_removed = tuple(added), tuple(gone)
    confs = [c for c in box.modes if c not in gone] + added
    out.configurations = tuple(confs)
    if gone and box.modes and box.modes[0] in gone and confs:
        out.first_mode = confs[0]
    ids = {g.id for g in spec.gears}
    recorded = _recorded_sliders(box)
    new_s = [g for g in now_sliders if g not in recorded]
    gone_s = [g for g in recorded if g not in now_sliders and g in ids]
    if new_s:
        out.structural.append(f"{_names(new_s)} {_plural(new_s, 'slides', 'slide')} now, and a slide mate is made when "
                              f"the assembly is built, {_NEW_REVISION}.")
    if gone_s:
        out.structural.append(f"{_names(gone_s)} no longer {_plural(gone_s, 'slides', 'slide')}, and "
                              f"{_plural(gone_s, 'its slide mate is', 'their slide mates are')} not taken out of the "
                              f"assembly that was built, {_NEW_REVISION}.")
    if out.structural or turn.motion is None or any(g not in ids for g in recorded):
        return out
    places = {s: motion.slide_places(report, s) for s in recorded}
    if not box.modes:
        # §9.8: sliders with no Modes rows, one configuration; their slide mates' distances are not reset by Update.
        for m in slides:
            z = places[m.gears[0]][0][1] if places[m.gears[0]] else None
            if z is not None and abs(z - float(m.z_front)) > MOVE_TOLERANCE:
                out.structural.append(f"{m.gears[0]}'s front face moves along {m.shaft} (z {_number(float(m.z_front))} "
                                      f"→ {_number(z)}), and with no Modes rows Update SolidWorks does not set a slide "
                                      f"mate's distance, {_NEW_REVISION}.")
        return out
    for m in slides:                               # J27, naming the position
        slider = m.gears[0]
        sign = next((1 if float(v) > 0 else -1 for v in m.values.values() if _number_or_none(v)), 1)
        for mode, z in places[slider]:
            if abs(z) >= motion.SLIDE_TOLERANCE and (z > 0) == (sign > 0):
                continue
            conf = _conf(box.modes, mode)
            old = next((float(v) for k, v in m.values.items() if k == conf), None)
            position, offset = next((x.positions.get(slider, ("", 0.0)) for x in report.modes if x.name == mode))
            where = "onto" if abs(z) < motion.SLIDE_TOLERANCE else "across"
            was = f"z {_number(old)} → {_number(z)}" if old is not None else f"z {_number(z)}"
            out.structural.append(f"{slider} at its position {position} ({_number(offset)} mm) in {mode} would stand "
                                  f"with its front face {where} the Front plane ({was}), from which the slide mate "
                                  f"{m.name} is measured, {_NEW_REVISION}.")
            break
    if out.structural:
        return out
    try:
        plan = motion.motion_plan(spec, report, layout.frames(report))
    except ValueError as exc:
        out.structural.append(str(exc))
        return out

    def key(m: Any) -> Tuple[str, frozenset]:
        return m.kind, frozenset(m.gears)
    new_gears = set(added_gears)
    wanted = {key(m): m for m in _per_mode(plan.mates) if not new_gears & set(m.gears)}
    on_record = {key(m) for m in per_mode}
    # W9c (K6): a coupling or sliding mesh newly needed between gears on record is made in place.
    out.new_mates = tuple(m for k, m in wanted.items() if k not in on_record)
    on_sets: List[Tuple[str, Tuple[str, ...]]] = []
    changed: List[str] = []
    for m in per_mode:
        now = wanted.get(key(m))
        if now is None:                            # §9.1: never on in no mode
            x, y = m.gears
            verb = "engages" if m.kind == motion.COUPLE else "meshes"
            only = [c for c in box.modes if on_in(tuple(m.modes), c)]
            if gone and only and all(c in gone for c in only):
                out.structural.append(f"The {_plural(only, 'mode', 'modes')} {_names(only)} {_is(only)} no longer on "
                                      f"the Modes sheet, and the mate {m.name} is on there alone: a mate made to be on "
                                      f"in some modes is never left on in none, {_NEW_REVISION}.")
            else:
                out.structural.append(f"No mode {verb} {y} with {x} now, and the mate {m.name}, made to be on in some "
                                      f"modes, is never left on in none, {_NEW_REVISION}.")
            continue
        want = tuple(c for c in confs if any(on_in((c,), n) for n in now.modes))
        on_sets.append((m.name, want))
        if set(want) != {c for c in box.modes if on_in(tuple(m.modes), c)}:
            changed.append(m.name)
    if out.structural:
        return out
    slide_values: List[Tuple[str, str, float]] = []
    for m in slides:
        held = {k: abs(float(v)) for k, v in m.values.items()}
        moved = False
        for conf in confs:
            z = abs(next(v for mode, v in places[m.gears[0]] if on_in((conf,), mode)))
            slide_values.append((m.name, conf, z))
            had = next((v for k, v in held.items() if on_in((conf,), k)), None)
            moved = moved or had is None or abs(had - z) > MOVE_TOLERANCE
        if moved:
            changed.append(m.name)

    # The links: a sliding mesh holds in its wanted on-set; a coupling is a MeshLink with k = σ_S·σ_D (§9.3), turns
    # relative to nothing, pitch the dog's; a spline is a LockLink, on in every configuration.
    placed = report.layout.placed
    want_of = dict(on_sets)
    had_of = {m.name: tuple(m.modes) for m in per_mode}
    names_of = {frozenset(m.gears): m.name for m in per_mode if m.kind == motion.MESH}

    def with_modes(links: Sequence[MeshLink], modes_of: Mapping[str, Tuple[str, ...]]) -> Tuple[MeshLink, ...]:
        return tuple(replace(link, modes=modes_of[names_of[frozenset((link.a, link.b))]])
                     if frozenset((link.a, link.b)) in names_of else link for link in links)
    couples = [m for m in per_mode if m.kind == motion.COUPLE]

    def couple_links(modes_of: Mapping[str, Tuple[str, ...]]) -> Tuple[MeshLink, ...]:
        return tuple(MeshLink(s, d, float(placed[s].sigma * placed[d].sigma), layout.pitch(placed[d]),
                              modes=modes_of[m.name]) for m in couples for s, d in (m.gears,))
    splines = tuple(LockLink(m.gears[0], m.gears[1], layout.pitch(placed[m.gears[1]]))
                    for m in box.mates if m.kind == motion.SPLINE)
    by_mode = _wanted_by_mode(box, a)
    for name, frames in layout.frames_by_mode(report).items():      # W9c: a mode added, by the read's name
        if name in added:
            by_mode[name] = frames
    components = {c.gear: c for c in box.components}

    def recorded_in(conf: str, p: Placement) -> Placement:
        c = components.get(p.gear)
        frame = next((f for k, f in (c.frames.items() if c is not None else ()) if on_in((conf,), k)), None)
        if not frame:
            return p
        return replace(p, rotation=tuple(float(v) for v in frame["rotation"]), at=tuple(float(v) for v in frame["at"]))
    out.motion = replace(
        turn.motion,
        meshes=with_modes(turn.motion.meshes, want_of) + couple_links(want_of),
        recorded_meshes=with_modes(turn.motion.recorded_meshes, had_of) + couple_links(had_of),
        locks=turn.motion.locks + splines,
        configurations=tuple(confs),
        mode_placements=tuple((conf, tuple(replace(p, rotation=by_mode[conf][p.gear].rotation,
                                                   at=by_mode[conf][p.gear].at) if p.gear in by_mode[conf] else p
                                           for p in placements)) for conf in confs),
        # W9c: a mode added has nothing on record; it is recorded as wanted (its frames are set, not judged).
        recorded_by_mode=tuple((conf, tuple(recorded_in(conf, p) if conf in box.modes else
                                            (replace(p, rotation=by_mode[conf][p.gear].rotation,
                                                     at=by_mode[conf][p.gear].at) if p.gear in by_mode[conf] else p)
                                            for p in turn.motion.recorded)) for conf in confs),
        slide_values=tuple(slide_values),
        on_sets=tuple(on_sets))
    out.changed = tuple(changed)
    return out


# -- W9c: Update adds, removes and re-mates in place (ISSUE-1-PLAN §2.1 "W9c", K6, §2.4; W9C-INTERFACES.md) ----------

_Z_AXES = ((0.0, 0.0, 1.0), (0.0, 0.0, -1.0))


def _band_toggle(entry: PartEntry, job: PartJob) -> Optional[bool]:
    """Bands given to a built sleeve (True) or taken from it (False), the part's spec on record against the read's;
    None when neither (or the record holds no form). A sleeve's part only."""
    if not entry.spec or job.spec.kind != clutch.SLEEVE:
        return None
    try:
        built = GearSpec.from_dict(dict(entry.spec))
    except (TypeError, ValueError, AttributeError):
        return None
    if built.kind != clutch.SLEEVE or built.has_bands() == job.spec.has_bands():
        return None
    return job.spec.has_bands()


_BAND_GLOBALS = (clutch.START_BAND, clutch.END_BAND, clutch.RELIEF_DIAMETER)
_RELIEF_FEATURES = (clutch.RELIEF_START_PLANE, clutch.RELIEF_END_PLANE, clutch.RELIEF_START_SKETCH,
                    clutch.RELIEF_END_SKETCH, clutch.RELIEF)


def _without_bands(entry: PartEntry, job: PartJob) -> Tuple[PartEntry, PartJob]:
    """The part on record and the part the read asks for, each with no bands: what :func:`_part` judges when only the
    bands come or go (W9c: they are given or taken in place, §2.4)."""
    from ..gears import plan_for
    spec = replace(job.spec, start_band="", end_band="")
    plan = job.plan
    if job.plan is not None:
        plan = plan_for(spec, job.derived, gearbox._template_of(job.plan), job.path)
    kept = {k: v for k, v in dict(entry.spec).items() if k not in ("start_band", "end_band")}
    variables = [list(pair) for pair in entry.variables if not (pair and str(pair[0]) in _BAND_GLOBALS)]
    return replace(entry, spec=kept, variables=variables), replace(job, spec=spec, plan=plan)


def _band_change(entry: PartEntry, job: PartJob, add: bool, made: Sequence[str] = ()) -> Any:
    """The ``swbuild.BandChange`` for a sleeve given bands (its band globals and relief ops, as the banded plan has
    them after the teeth) or relieved of them (its ``Relief`` loft cut suppressed: the coordinator's ruling C8).
    ``made``: the part's features on record. A sleeve whose record holds the relief while its spec has no bands (an
    earlier Update suppressed it) is given its bands back (``back``): the band globals, and the ``Relief`` turned back
    on, never made a second time."""
    gear = entry.gears[0] if entry.gears else job.gear_ids[0]
    if not add:
        return swbuild.BandChange(gear, entry.path, False, (), (clutch.RELIEF,))
    bands = job.spec.bands_mm()
    d = job.derived
    ops = tuple(base.AddGlobal(v.name, v.expression, v.radian_expression)
                for v in clutch.relief_globals(bands))
    if clutch.RELIEF in made:
        return swbuild.BandChange(gear, entry.path, True, ops, (clutch.RELIEF,), back=True)
    ops += tuple(clutch.relief_ops(d.face_width, bands, clutch.relief_diameter(d.module, d.teeth)))
    return swbuild.BandChange(gear, entry.path, True, ops, _RELIEF_FEATURES)


def _frame_shaft_on_z(spec: Any, shaft_id: str) -> bool:
    shaft = spec.shaft(shaft_id)
    if shaft is None or shaft.mount() != "frame":
        return False
    try:
        return geometry.axis_vector(shaft.axis) in _Z_AXES
    except ValueError:
        return False


def _in_place_gears(box: GearboxRecord, a: Assessment, gone: Sequence[str], new: Sequence[str],
                    job_of: Mapping[str, PartJob], entries: Sequence[PartEntry],
                    exists: Callable[[str], bool]) -> Tuple[List[str], List[str], List[str]]:
    """K6 (W9C-INTERFACES §3): of the gears new in the read and those gone from it, which Update adds and removes in
    place, and a sentence for each it cannot. Added: a gear on a frame shaft on record along Z+ or Z−, not a
    planet's copy, whose part is on record or a file not yet on disk. Removed: one that anchors no other gear (no
    lock or spline on record has it first) and is no planet's copy. Whether a recorded mate would change is
    :func:`_mate_changes`'."""
    spec, placed = a.spec, a.report.layout.placed
    on_record = {s.shaft for s in box.shafts}
    paths = {p.path.lower() for p in entries}
    added: List[str] = []
    removed: List[str] = []
    said: List[str] = []
    for g in new:
        gear = spec.gear(g)
        shaft = gear.shaft if gear is not None else ""
        job = job_of.get(g)
        if gear is None or g not in placed or job is None:
            said.append(f"{g} is new, and Update SolidWorks cannot add a part to what was built.")
        elif shaft not in on_record:
            said.append(f"{g} is new on {shaft}, which is new too, and Update SolidWorks adds a gear only on a shaft "
                        f"the layout part has, {_REBUILD}.")
        elif placed[g].carrier or spec.shaft(shaft).mount() != "frame":
            said.append(f"{g} is new on {shaft}, which rides a carrier, and Update SolidWorks adds a gear only on a "
                        f"shaft on the frame, {_REBUILD}.")
        elif not _frame_shaft_on_z(spec, shaft):
            said.append(f"{g} is new on {shaft}, whose axis is {spec.shaft(shaft).axis}, and Update SolidWorks adds a "
                        f"gear only on a shaft along Z+ or Z-, {_REBUILD}.")
        else:
            added.append(g)
    copies = {c.of for c in box.components if c.of}
    for g in gone:
        holds = [m for m in box.mates if m.kind in (motion.LOCK, motion.SPLINE) and m.gears and m.gears[0] == g]
        if g in copies:
            said.append(f"{g} is no longer in the workbook, and it is a planet whose copies ride a carrier, which "
                        f"Update SolidWorks does not take out, {_REBUILD}.")
        elif not any(c.gear == g for c in box.components):
            said.append(f"{g} is no longer in the workbook, and Update SolidWorks cannot take a part out of what was "
                        "built.")
        elif holds:
            followers = [m.gears[1] for m in holds]
            names = [m.name for m in holds]
            said.append(f"{g} is no longer in the workbook, and it anchors {_names(followers)} (the "
                        f"{_plural(names, 'mate', 'mates')} {_names(names)}): Update SolidWorks takes out only a gear "
                        f"that anchors none, {_REBUILD}.")
        else:
            removed.append(g)
    return added, removed, said


def _kept_box(box: GearboxRecord, removed: Sequence[str]) -> GearboxRecord:
    """The gearbox on record less the gears Update takes out and every mate touching them: what stays (§1)."""
    if not removed:
        return box
    gone = set(removed)
    return replace(box, components=[c for c in box.components if c.gear not in gone],
                   mates=[m for m in box.mates if not gone & set(m.gears)],
                   fixed=[g for g in box.fixed if g not in gone],
                   unmated=[pair for pair in box.unmated if not gone & set(pair)],
                   drag=[g for g in box.drag if g not in gone])


def _mate_changes(kept: GearboxRecord, plan: motion.MotionPlan, added: Sequence[str]) -> List[str]:
    """§3's "still structural when a recorded mate would change": each mate that stays on record (less the per-mode
    ones, :func:`_modes`') that the read's plan no longer makes as it was — its name gone, or its kind or gears
    another (an anchor that is no longer the first gear that does not slide, a lock that becomes a spline) — and each
    mate the plan would now make between gears on record that is not on record. A mate touching a gear added is the
    added gear's own (``AddedGear.ops``)."""
    new = set(added)
    per_mode = {m.name for m in _per_mode(kept.mates)}
    wanted = {m.name: m for m in plan.mates if not m.modes and not new & set(m.gears)}
    said: List[str] = []
    for m in kept.mates:
        if m.name in per_mode:
            continue
        now = wanted.get(m.name)
        if now is None or now.kind != m.kind or tuple(now.gears) != tuple(m.gears):
            said.append(f"With the gears added or taken out, the mate {m.name} on record would not be made as it was, "
                        f"and Update SolidWorks does not make a gear's own mates again in place, {_REBUILD}.")
    recorded = {m.name for m in kept.mates}
    for name, m in wanted.items():
        if name not in recorded:
            said.append(f"With the gears added or taken out, {_names(list(m.gears))} would need the new mate {name}, "
                        f"and Update SolidWorks makes new mates in place only for a gear it adds, a coupling or a "
                        f"sliding mesh, {_REBUILD}.")
    return said


def _mates_never_made(kept: GearboxRecord, plan: motion.MotionPlan) -> List[str]:
    """Each gear on record with none of its own mates on record, that the read's plan mates (an Update that inserted
    it stopped before making them): *Hub is in the assembly, inserted by an Update SolidWorks that stopped before
    making its mates Hub on Output Axis, Hub along Output and RangeSlv splined to Hub, and Update SolidWorks makes a
    gear's own mates only as it adds the gear, so the gearbox needs building again.*"""
    said: List[str] = []
    for c in kept.components:
        if c.gear in kept.fixed or any(c.gear in m.gears for m in kept.mates):
            continue
        names = [m.name for m in plan.mates if c.gear in m.gears and not m.modes]
        if names:
            said.append(f"{c.gear} is in the assembly, inserted by an Update SolidWorks that stopped before making its "
                        f"mates {_names(names)}, and Update SolidWorks makes a gear's own mates only as it adds the "
                        "gear, "
                        f"{_REBUILD}.")
    return said


def _components_for(box: GearboxRecord, a: Assessment, added: Mapping[str, PartJob]) -> Tuple[
        List[Tuple[str, str, Any]], Dict[str, str], Dict[str, str]]:
    """The assembly plan's components as a build of this read would insert them (carriers ``carrier<i>`` first, then
    each gear ``gear<index>`` with its copies, as ``gearbox.plan_gearbox`` numbers them), each with its part's path —
    the record's for a gear on record, the new part's for one added; ``handle_of`` gear (or carrier id) -> handle;
    and ``name_of`` handle -> the ``Name2`` on record (the layout's, every gear's and carrier's)."""
    spec, report = a.spec, a.report
    frames = layout.frames(report)
    components: List[Tuple[str, str, Any]] = []
    handle_of: Dict[str, str] = {}
    name_of: Dict[str, str] = {layout.LAYOUT_HANDLE: box.layout_component}
    carrier_frames = _carrier_frames(a)
    for i, entry in enumerate(box.carriers, 1):
        handle = f"{layout.CARRIER_HANDLE}{i}"
        cid = layout.carrier_id(entry.shaft)
        handle_of[cid] = handle
        name_of[handle] = entry.component
        f = carrier_frames.get(entry.shaft)
        if f is not None:
            components.append((handle, entry.path, f))
    recorded = {c.gear: c for c in box.components}
    copies_of: Dict[str, List[str]] = {}
    for p in report.layout.placed.values():
        if p.carrier:
            copies_of.setdefault(p.row, []).append(p.gear)
    for index, gear in enumerate(spec.gears, 1):
        ids = copies_of.get(gear.id, [gear.id])
        for gear_id in ids:
            if gear_id not in frames:
                continue
            k = planetary.copy_of(gear_id)[1] if gear.id in copies_of and len(ids) > 1 else 0
            handle = f"{layout.GEAR_HANDLE}{index}" + (f"c{k}" if k else "")
            if gear_id in recorded:
                part = recorded[gear_id].part
                name_of[handle] = recorded[gear_id].name
            elif gear_id in added:
                part = added[gear_id].path
            else:
                continue
            handle_of[gear_id] = handle
            components.append((handle, part, frames[gear_id]))
    return components, handle_of, name_of


def _touches(op: Any, handle: str) -> bool:
    refs = [getattr(op, k, "") for k in ("a", "b", "component", "id")] if isinstance(op, base.Mate) else \
        [getattr(op, "component", ""), getattr(op, "id", "")]
    return any(str(r).split(":", 1)[0] == handle for r in refs if r)


def _added_gears(box: GearboxRecord, a: Assessment, plan: motion.MotionPlan, added: Mapping[str, PartJob],
                 entries: Sequence[PartEntry], configurations: Sequence[str]) -> Tuple[Tuple[Any, ...], Any]:
    """Each ``swbuild.AddedGear`` (W9C-INTERFACES §2), its ops taken from the assembly plan a build of this read
    makes (``motion.motion_assembly_plan``, and ``motion.modes_plan`` for its mates on in some modes only), in plan
    order; and the modes plan (or None), from which :func:`_new_mates` takes a new coupling's op."""
    components, handle_of, name_of = _components_for(box, a, added)
    assembly = motion.motion_assembly_plan(box.layout, components, handle_of, plan, "", box.assembly)
    modes = motion.modes_plan(plan, handle_of, layout.frames_by_mode(a.report))
    step_ops = [op for step in (modes.steps if modes is not None else ()) for op in step.ops]
    mates = {m.name: m for m in plan.mates}
    on_record = {p.path.lower() for p in entries}
    out = []
    for gear, job in added.items():
        handle = handle_of[gear]
        touching = {m.name for m in plan.mates if gear in m.gears}
        faces = {m.face_global for m in plan.mates if m.name in touching and m.face_global}
        ops: List[Any] = []
        for op in assembly.ops:
            if isinstance(op, base.AddGlobal) and op.name in faces:
                ops.append(op)
            elif isinstance(op, (base.AddComponent, base.Place, base.Fix,
                                 base.Unfix)) and _touches(op, handle):
                ops.append(op)
            elif isinstance(op, base.Mate) and op.name in touching:
                ops.append(op)
            elif isinstance(op, base.LinkDimension) and op.dimension.split("@", 1)[-1] in touching:
                ops.append(op)
        ops += [op for op in step_ops if op.name in touching]
        named = {str(r).split(":", 1)[0] for op in ops if isinstance(op, base.Mate) for r in (op.a, op.b)}
        others = tuple((h, name_of[h]) for h in sorted(named) if h != handle and h in name_of)
        senses = tuple((n, mates[n].sense == -1) for n in sorted(touching)
                       if mates[n].kind in (motion.MESH, motion.SPLINE, motion.COUPLE))
        on_sets = tuple((n, tuple(c for c in configurations if on_in(tuple(mates[n].modes), c)))
                        for n in sorted(touching) if mates[n].modes)
        build = None if job.path.lower() in on_record else job.plan
        refs = tuple(_ref_of(mates[n], configurations) for n in [m.name for m in plan.mates if m.name in touching])
        out.append(swbuild.AddedGear(gear, handle, job.path, build, tuple(ops), others, senses, on_sets, refs))
    return tuple(out), (modes, handle_of, name_of)


def _ref_of(m: Any, configurations: Sequence[str]) -> MateRef:
    """The ``MateRef`` the record will hold for a mate the Update makes (``motion.mate_entry`` as recorded): a mate on
    in some modes only carries the configurations (the record's spelling) its modes are."""
    entry = motion.mate_entry(m)
    if m.modes:
        entry.modes = [c for c in configurations if on_in(tuple(m.modes), c)]
    return motion.mate_ref(entry)


def _new_mates(wanted: Sequence[Any], modes: Any, handle_of: Mapping[str, str], name_of: Mapping[str, str],
               configurations: Sequence[str]) -> Tuple[Any, ...]:
    """Each ``swbuild.NewMate``: a coupling or sliding mesh the read's modes need between gears on record (K6), its op
    as the build makes it in the first mode it is on in, on in the configurations its modes are."""
    if modes is None:
        return ()
    ops = {op.name: op for step in modes.steps for op in step.ops}
    out = []
    for m in wanted:
        op = ops.get(m.name)
        if op is None:
            continue
        handles = tuple((handle_of[g], name_of[handle_of[g]]) for g in m.gears
                        if g in handle_of and handle_of[g] in name_of)
        on = tuple(c for c in configurations if on_in(tuple(m.modes), c))
        out.append(swbuild.NewMate(op, handles, on, m.name in modes.same_way, _ref_of(m, configurations)))
    return tuple(out)


@dataclass(frozen=True)
class InPlaceRecord:
    """What ``finish_update`` writes for an in-place Update (W9C-INTERFACES §7), from the read: ``mates`` every mate
    the Update makes (an added gear's, a new coupling or sliding mesh), as the plan has them; ``jobs`` each added
    gear's part job (a new part's record and ``.gear.json``); ``fixed`` the gears that stand still after it;
    ``meshes`` the listed meshes and ``unmated`` those closing a loop, as a build of the read records them."""

    mates: Tuple[Any, ...] = ()
    jobs: Tuple[Tuple[str, PartJob], ...] = ()
    fixed: Tuple[str, ...] = ()
    meshes: Tuple[Tuple[str, str], ...] = ()
    unmated: Tuple[Tuple[str, str], ...] = ()


def _new_links(mates: Sequence[Any], a: Assessment, configurations: Sequence[str]) -> Tuple[
        Tuple[MeshLink, ...], Tuple[LockLink, ...]]:
    """The links of the mates an Update makes in place (W9C-INTERFACES §11 "From A": ``motion.meshes`` and ``locks``
    hold the gearbox's links after the Update): a gear mate's ``MeshLink`` from its teeth and sense, a coupling's
    with ``k = σ_S·σ_D`` and its on-set (as :func:`_modes` links one on record), a lock's or spline's ``LockLink``."""
    placed = a.report.layout.placed
    teeth = {g: int(p.teeth) for g, p in placed.items()}
    meshes: List[MeshLink] = []
    locks: List[LockLink] = []
    for m in mates:
        if not all(g in placed for g in m.gears):
            continue
        on = tuple(c for c in configurations if on_in(tuple(m.modes), c)) if m.modes else ()
        if m.kind == motion.MESH:
            link = motion.mesh_links([tuple(m.gears)], teeth, {tuple(m.gears): int(m.sense) or
                                                              motion._parallel_sense_of(placed[m.gears[0]],
                                                                                        placed[m.gears[1]])})[0]
            meshes.append(replace(link, modes=on) if on else link)
        elif m.kind == motion.COUPLE:
            s, d = m.gears
            meshes.append(MeshLink(s, d, float(placed[s].sigma * placed[d].sigma), layout.pitch(placed[d]), modes=on))
        elif m.kind in (motion.LOCK, motion.SPLINE):
            locks.append(LockLink(m.gears[0], m.gears[1], layout.pitch(placed[m.gears[1]])))
    return tuple(meshes), tuple(locks)


def _in_place(whole: GearboxRecord, kept: GearboxRecord, a: Assessment, entries: Sequence[PartEntry],
              added: Sequence[str], removed: Sequence[str], job_of: Mapping[str, PartJob], modal: "_Modes",
              band_changes: Sequence[Any]) -> Tuple[Any, List[str]]:
    """The ``swbuild.InPlace`` for a gearbox built to turn (W9C-INTERFACES §2, §3), and the sentences of what stops it
    being carried in place (a recorded mate that would change, :func:`_mate_changes`). ``whole``: the record's gearbox;
    ``kept``: it less the gears taken out."""
    why: List[str] = []
    added_gears: Tuple[Any, ...] = ()
    new_mates: Tuple[Any, ...] = ()
    record: Optional[InPlaceRecord] = None
    if added or removed or modal.new_mates:
        try:
            plan = motion.motion_plan(a.spec, a.report, layout.frames(a.report))
        except ValueError as exc:
            return swbuild.InPlace(), [str(exc)], None
        new = set(added)
        made = tuple(m for m in plan.mates if new & set(m.gears)) + tuple(modal.new_mates)
        record = InPlaceRecord(mates=made, jobs=tuple((g, job_of[g]) for g in added), fixed=tuple(plan.fixed),
                               meshes=tuple((m.a, m.b) for m in a.spec.meshes), unmated=tuple(plan.unmated))
        if added or removed:
            why.extend(_mate_changes(kept, plan, added))
        if not why and (added or modal.new_mates):
            try:
                added_gears, (modes, handle_of, name_of) = _added_gears(
                    kept, a, plan, {g: job_of[g] for g in added}, entries, modal.configurations or tuple(kept.modes))
                new_mates = _new_mates(modal.new_mates, modes, handle_of, name_of, modal.configurations)
            except ValueError as exc:
                why.append(str(exc))
    elif any(not any(c.gear in m.gears for m in kept.mates) for c in kept.components if c.gear not in kept.fixed):
        # A gear on record with no mate on record: an Update that inserted it stopped before making its mates (the
        # record says what was done). Nothing here makes a gear's own mates for a gear already in, so it is said.
        try:
            plan = motion.motion_plan(a.spec, a.report, layout.frames(a.report))
        except ValueError as exc:
            return swbuild.InPlace(), [str(exc)], None
        why.extend(_mates_never_made(kept, plan))
    components = {c.gear: c for c in whole.components}
    gone = tuple(swbuild.RemovedGear(g, components[g].name, components[g].part,
                                     tuple(m.name for m in whole.mates if g in m.gears)) for g in removed)
    return swbuild.InPlace(added=added_gears, removed=gone, new_mates=new_mates, bands=tuple(band_changes),
                           modes_added=modal.modes_added, modes_removed=modal.modes_removed,
                           first_mode=modal.first_mode), why, record


def finish_update(plan: UpdatePlan, result: GearboxUpdate, record: LinkRecord, *, digest: str,
                  read_sidecar: Callable[[str], Optional[Sidecar]] = store.read_sidecar,
                  mtime: Callable[[str], float] = os.path.getmtime,
                  stamp: Optional[str] = None, workbook: str = "", revision: Sequence[int] = (),
                  written_by: str = "") -> Finished:
    """The sidecars and record an update leaves (Tk thread, after the worker).

    ``record`` is the record as read just before writing
    (``store.open_link_record``). For each part whose values changed in
    SolidWorks (``result.parts[i].changed``): ``store.updated_sidecar`` and its
    ``PartEntry`` spec and variables. The re-placed gears' component frames.
    ``last_updated`` set when anything changed. Every path in
    ``result.changed`` goes into ``record.unsaved`` with the file's time as
    the worker read it before changing anything (``result.mtimes``; else
    ``mtime(path)`` now), so a save made in SolidWorks while the job was
    answering still reads as newer: Update does not save (decision 3). The
    ``.gear.json`` of a part it changed is marked ``unsaved_since`` that same
    time, so it never claims, to a later plan, values the file may not hold
    (review B2): reuse by ``.gear.json`` skips a marked one until the file is
    newer. ``workbook``, when given, is this workbook's path now, and a
    record that names an older one is adopted (``store.adopt``).
    ``dragged`` lists the gears whose live frame
    (``result.found``) differed from the recorded one while the recorded one
    was already the wanted one: moved by hand in SolidWorks, and put back.
    Pure but for ``read_sidecar`` and ``mtime``.

    W9a (K4, schema 7): what the worker read of the user's work before it changed anything
    (``result.user_work``) goes on record as the gearbox's ``user_work``, with the read of the workbook the press
    came from (``digest``) and the SolidWorks it ran on (``revision``, the session's), whatever the press then did;
    a press that read nothing leaves what is on record.

    W9c (W9C-INTERFACES §7; schema 8 gains nothing): what the Update made or took away in place, as the worker
    reports it done (:func:`_follow_in_place`): each gear inserted a ``ComponentEntry`` by the ``Name2`` kept, each
    mate made a ``MateEntry`` on in the configurations it reads on in, a new part a ``PartEntry`` and its
    ``.gear.json`` (``written_by``); each gear deleted, its entry and its mates gone, and its part's entry too when no
    gear of the revision uses that file (the file stays: C6); the modes added and removed in ``modes``, the record's
    order with the added after it; a sleeve's bands in its spec (sidecar schema 2) with the relief's features among
    its features, only once the worker reports them given or taken.

    A gearbox built to turn (``plan.motion`` set): a mated gear is dragged
    only when the worker found it off its axis (a turn is never a drag),
    fixed gears by W4's rule; mated gears' frames go on record a whole
    train at a time (:func:`_follow_trains`); the record's mates follow the
    ratios and Face Z globals set, and a ratio the parts now hold at the
    same proportion (:func:`_follow_mates`); ``drag`` follows the workbook
    (``plan.drag``).

    Marks (second W4 review N2): a document the job loaded from its file
    (``result.opened``) and found holding what the workbook asks is neither
    unsaved nor mismatched any more — both its entries and its
    ``.gear.json``'s mark go; before, an Update left unsaved and lost when
    SolidWorks closed was marked for ever, and every later build made that
    part new. A document Update changes now loses any mismatched mark (it
    holds the values in memory; the save its unsaved mark asks for clears
    both). A document marked unsaved that was not open when the job began
    (``result.open_before``) and that the job did not change lost Update's
    changes when it was closed: its mark becomes a ``mismatched`` one at
    the same time, since its file does not hold what the record says.

    A part reached without a failure is recorded as holding the wanted values
    even when nothing in it changed: SolidWorks was found to hold them already
    (an earlier update, or values set by hand), and the record follows
    SolidWorks. ``digest`` is the read SolidWorks wholly matches, so it is set
    only when the update ran with no failure and nothing skipped. An update
    that stopped part-way keeps the digest it had, even though it changed
    something: the header would otherwise say "built from this version" of a
    gearbox whose layout, say, was never moved (found by the window wiring,
    2026-11-13). What it did change is still recorded, part by part.
    """
    stamp = stamp or store.now()
    rec = copy.deepcopy(record)
    if workbook:
        store.adopt(rec, workbook)
    out = Finished(record=rec)
    changed = bool(result.changed or result.placed)
    settled = _settled(plan, result)
    marks: Dict[str, float] = {}
    for path in result.changed:
        then = next((t for p, t in getattr(result, "mtimes", {}).items() if store.same_path(p, path)), None)
        if then is None:
            try:
                then = float(mtime(path))
            except OSError:
                out.notes.append(f"{os.path.basename(path)} could not be found on disk to note that it is changed "
                                 "but not saved.")
                continue
        marks[path] = then

    written = []
    for update, done in zip(plan.parts, result.parts):
        if done.failures or not (done.changed or done.unchanged):
            continue                        # not reached, or it failed: what it holds is not known
        entry = next((p for p in rec.parts if store.same_path(p.path, update.path)), None)
        trig = done.trig or (entry.trig if entry is not None else "")
        variables = [[v.name, v.expression_for(trig)] for v in update.variables]
        spec = update.spec.to_dict()
        band = next((b for b in plan.in_place.bands if store.same_path(b.part, update.path)), None)
        band_done = band is not None and band.gear in (getattr(result, "bands_added", []) or []) + \
            (getattr(result, "bands_removed", []) or [])
        if band is not None and not band_done and entry_spec_of(rec, update.path) is not None:
            # W9c: the values were set but the bands were not given or taken: the spec keeps the bands it had.
            had = entry_spec_of(rec, update.path)
            spec = {k: v for k, v in spec.items() if k not in ("start_band", "end_band")}
            spec.update({k: had[k] for k in ("start_band", "end_band") if k in had})
        if band_done and band.add:
            variables += [[v.name, v.expression_for(trig)] for v in clutch.relief_globals(update.spec.bands_mm())
                          if all(v.name != pair[0] for pair in variables)]
        if entry is not None and entry.spec == spec and entry.variables == variables and not done.changed:
            continue
        if entry is not None:
            entry.spec, entry.variables, entry.trig, entry.kind = spec, variables, trig, update.spec.kind
        sidecar_path = store.sidecar_path(update.path)
        sidecar = read_sidecar(sidecar_path)
        if sidecar is None:
            out.notes.append(f"{os.path.basename(sidecar_path)} could not be read, so it was left as it is; the "
                             "workbook's record says what the part now holds.")
            continue
        if done.changed:
            mark = next((t for p, t in marks.items() if store.same_path(p, update.path)), None)
        else:
            mark = 0.0 if _in(update.path, settled) else None
        renewed = store.updated_sidecar(sidecar, spec, update.derived.to_dict(), variables, stamp, unsaved_since=mark)
        if band_done and band.add:                  # W9c: the relief is the app's, after the user's features (C2)
            renewed.record.features = list(renewed.record.features) + [
                f for f in band.features if f not in renewed.record.features]
        out.sidecars.append((sidecar_path, renewed))
        written.append(update.path)

    box = rec.gearbox
    if box is not None:
        if plan.layout is not None and result.layout is not None and not result.layout.failures and plan.shafts:
            box.shafts = [ShaftEntry(**asdict(s)) for s in plan.shafts]
        # W9a (K1): a component the worker found by its part, not its recorded Name2, is recorded by the name found.
        for gear, before, found_name in getattr(result, "renamed", []) or []:
            for component in box.components:
                if component.gear == gear and component.name == before:
                    component.name = found_name
            for carrier in box.carriers:
                if carrier.component == before and layout.carrier_id(carrier.shaft) == gear:
                    carrier.component = found_name
        if plan.in_place:                           # W9c (§7): before the frames, so an added gear's are written
            _follow_in_place(rec, box, plan, result, read_sidecar, stamp, out, written_by)
        wanted = {p.gear: p for p in plan.placements}
        turning = plan.motion is not None
        held = set(plan.motion.fixed) if turning else set()
        off_axis = set(getattr(result, "off_axis", []) or []) if turning else set()
        for component in box.components:
            p = wanted.get(component.gear)
            if p is None:
                continue
            found = result.found.get(component.gear)
            recorded_is_wanted = bool(component.rotation and component.at) and same_frame(
                component.rotation, component.at, p.rotation, p.at, p.pitch)
            if turning and component.gear not in held:
                # A mated gear the user turned is not a drag (W5-PLAN D4): only one found off its axis or place.
                if component.gear in off_axis:
                    out.dragged.append(component.gear)
            elif found is not None and recorded_is_wanted and not same_frame(
                    component.rotation, component.at, found[0], found[1], p.pitch):
                out.dragged.append(component.gear)
            if turning and component.gear not in held:
                continue                    # a mated gear's frame follows its whole train (below)
            if component.gear in result.placed or (found is not None and same_frame(found[0], found[1], p.rotation,
                                                                                     p.at, p.pitch)):
                component.rotation, component.at = list(p.rotation), list(p.at)
        if turning:
            _follow_trains(box, plan, result, held)
            _follow_mates(box, plan, result)
            _follow_modes(box, plan, result)
            box.drag = list(plan.drag)
        _follow_carriers(box, plan, result)
        if record_user_work(rec, getattr(result, "user_work", None), assembly=plan.assembly, digest=digest,
                            revision=revision, modes_read=modes_read(plan)):
            follow_modes_added(box.user_work, result, box.modes)
        if revision:
            box.solidworks = [int(n) for n in revision]       # schema 9: the SolidWorks this press ran on
        _follow_carry(rec, plan, result, out, mtime)           # W9d: what Build again… carried, found lost or saved
        out.earlier_update = _earlier_update(record, plan, result, mtime)
        if out.earlier_update:
            out.off_after_update, out.dragged = out.dragged, []
            out.out_of_step_after_update = [tuple(pair) for pair in getattr(result, "out_of_step", []) or []]
        if changed:
            box.updated = stamp

    # The marks (second W4 review N2). A document the job loaded from its file and found holding what the workbook
    # asks holds it in memory and on disk alike: neither unsaved nor mismatched any more. A document marked unsaved
    # that was not open when the job began lost what Update had changed in it when it was closed unsaved, and the
    # job did not put it back: its file does not hold what the record says, which is what ``mismatched`` means.
    for path in settled:
        _drop(rec.unsaved, path)
        _drop(rec.mismatched, path)
    unmark = [p for p in settled if not _in(p, written)]
    open_before = getattr(result, "open_before", None)
    if open_before is not None:
        for path, then in list(rec.unsaved.items()):
            if _in(path, open_before) or _in(path, result.changed):
                continue
            del rec.unsaved[path]
            if store.saved_since(path, then, mtime):
                continue                    # saved since: the mark goes, as store.clear_saved would take it
            _drop(rec.mismatched, path)
            rec.mismatched[path] = then
            unmark.append(path)
    for path in unmark:
        sidecar = read_sidecar(store.sidecar_path(path))
        if sidecar is not None and sidecar.record.unsaved_since:
            out.sidecars.append((store.sidecar_path(path), store.unmarked(sidecar)))
    for path, then in marks.items():
        _drop(rec.unsaved, path)
        _drop(rec.mismatched, path)          # held in memory now: the save the unsaved mark asks for clears both
        rec.unsaved[path] = then
    if changed:
        rec.last_updated = stamp
    if not (result.failures or result.skipped):
        rec.digest = digest
    # The runs review's should-fix: a stop that left a part in error is marked on the unsaved documents, so the footer
    # says to close them without saving. The mark goes only when the document leaves ``unsaved`` (saved, or found
    # closed: store.keep_in_error) or this press changed that very document, by its values or its bands, with no
    # failure naming it (the fixes review's M3: a press that set nothing in it proves nothing, the part still holding
    # the new values in error; its second reading's N1: a rebuild that read false from the user's own features alone
    # is no failure, and clears it).
    clean = _documents_changed_clean(plan, result)
    rec.unsaved_in_error = [p for p in rec.unsaved_in_error if not any(store.same_path(p, q) for q in clean)]
    if result.failures:
        failed = _documents_left_in_error(plan, result)
        if failed:
            rec.unsaved_in_error = list(dict.fromkeys(list(rec.unsaved_in_error) + failed))
    store.keep_in_error(rec)
    if not result.failures:
        # A document this press changed is never one it set nothing in (N1), so it is never said as one.
        out.still_in_error = [p for p in rec.unsaved_in_error if not _in(p, getattr(result, "changed", []) or [])]
    return out


def document_stem(name: str) -> str:
    """A document's name as the two "left in error" rules compare it (the fixes review's S7): its file name without
    folder or SolidWorks extension, case aside — ``GetTitle`` comes without ``.SLDPRT`` where Windows hides
    extensions."""
    base = os.path.basename(str(name).replace("\\", "/")).strip()
    for ext in (".sldprt", ".sldasm"):
        if base.casefold().endswith(ext):
            base = base[:-len(ext)]
    return base.casefold()


def names_document(what: str, document: str) -> bool:
    """Whether a failure's ``what`` (``"Gear_m1.25_N29.SLDPRT"``, ``"Gear_m1.25_N29 Face Width"``) names ``document``
    (a title or a path), by stem: the stem, then the end, an extension or a space."""
    stem, text = document_stem(document), str(what).strip().casefold()
    return bool(stem) and text.startswith(stem) and (len(text) == len(stem) or text[len(stem)] in ". ")


def _value_documents(result: Any) -> List[Any]:
    """The parts', the layout's and the carriers' ``swbuild.UpdateResult`` of an Update."""
    docs = list(getattr(result, "parts", []) or []) + [getattr(result, "layout", None)] + \
        list(getattr(result, "carriers", []) or [])
    return [d for d in docs if d is not None and getattr(d, "document", "")]


def changed_documents(result: Any) -> List[str]:
    """Every document an Update changed, by name or path: a value set (its ``UpdateResult.changed``) or anything else
    it changed there (``GearboxUpdate.changed``: a sleeve given or relieved of its bands alone). One rule for the stop's
    "left in error" and for the mark's clearing, so the two never disagree about a document (the third re-check)."""
    return [d.document for d in _value_documents(result) if getattr(d, "changed", None)] + \
        [str(p) for p in getattr(result, "changed", []) or []]


def documents_left_in_error(result: Any) -> List[Any]:
    """The documents (``swbuild.UpdateResult``) an Update changed (:func:`changed_documents`) and left in error: a
    failure of the job names it, and either its values' rebuild reported an error, or the worker lists it changed in
    SolidWorks (``GearboxUpdate.changed``) and the failure names the document as a whole (a sleeve's band step: the
    app's own feature in error, after its values rebuilt clean or with none to set). A rebuild in error from the
    user's features alone is no failure; a single global refused beside a clean rebuild names the global, and is not
    this. The parts, the layout and the carriers. One rule for the stop's sentence and the record's mark."""
    named = [str(what) for what, _why in getattr(result, "failures", []) or []]
    changed = {document_stem(c) for c in changed_documents(result)}
    listed = {document_stem(str(p)) for p in getattr(result, "changed", []) or []}
    return [d for d in _value_documents(result) if document_stem(d.document) in changed
            and any(names_document(w, d.document) for w in named)
            and (not getattr(d, "rebuilt", True) or (document_stem(d.document) in listed
                                                       and any(document_stem(w) == document_stem(d.document)
                                                               for w in named)))]


def _plan_paths(plan: UpdatePlan) -> List[str]:
    return [p.path for p in plan.parts] + ([plan.layout.path] if plan.layout is not None else []) + \
        [c.path for c in getattr(plan, "carriers", ()) or () if getattr(c, "path", "")]


def _documents_left_in_error(plan: UpdatePlan, result: GearboxUpdate) -> List[str]:
    """The paths of the documents this Update left in error (:func:`documents_left_in_error`)."""
    stems = {document_stem(d.document) for d in documents_left_in_error(result)}
    return [p for p in _plan_paths(plan) if document_stem(p) in stems]


def _documents_changed_clean(plan: UpdatePlan, result: GearboxUpdate) -> List[str]:
    """The paths of the documents this Update changed with no failure naming them: the app's features rebuilt clean.
    Their rebuild may still read false, from the user's own features alone (P0), which the worker never makes a
    failure (``swbuild._update_document``'s ``theirs_alone``); such a document is put right as much as this press
    can, and keeping its mark would tell the user, press after press, to close it without saving (the second reading
    of the fixes review, N1). Changed means a value set (its ``UpdateResult``) or anything else the press changed in
    it (``result.changed``: a sleeve given its bands alone, whose band step raises on any feature of the app's in
    error), so the mark and the status's save offer never disagree about it (the re-check's note under N1)."""
    named = [str(what) for what, _why in getattr(result, "failures", []) or []]
    stems = {document_stem(c) for c in changed_documents(result) if not any(names_document(w, c) for w in named)}
    return [p for p in _plan_paths(plan) if document_stem(p) in stems]


def entry_spec_of(rec: LinkRecord, path: str) -> Optional[Dict[str, Any]]:
    entry = next((p for p in rec.parts if store.same_path(p.path, path)), None)
    return dict(entry.spec) if entry is not None and entry.spec else None


LEFT_GLOBAL, LEFT_CONFIGURATION, LEFT_PART = "global", "configuration", "part"


def _leftovers_unwanted(record: LinkRecord, box: GearboxRecord, a: Assessment, in_place: Any) -> Tuple[
        Tuple[str, str], ...]:
    """The app's leftovers this read does not use (:attr:`UpdatePlan.leftovers`): a global no step of ``in_place``
    adds, a configuration that is not one of the read's modes, a part built for a gear no component names whose gear
    is not added by ``in_place`` (its part entry stays on record, with no component)."""
    named = {op.name for g in in_place.added for op in g.ops if isinstance(op, base.AddGlobal)}
    named |= {op.name for b in in_place.bands for op in b.ops if isinstance(op, base.AddGlobal)}
    modes = {m.name.casefold() for m in a.spec.modes}
    adding = {g.gear for g in in_place.added}
    components = {c.gear for c in box.components} | {c.of for c in box.components if c.of}
    out: List[Tuple[str, str]] = [(LEFT_GLOBAL, name) for _doc, name in box.left_globals if name not in named]
    out += [(LEFT_CONFIGURATION, c) for c in box.left_configurations if c.casefold() not in modes]
    out += [(LEFT_PART, p.path) for p in record.parts if p.revision == box.revision and p.gears
            and not set(p.gears) & components and not set(p.gears) & adding]
    return tuple(out)


def _global_used(name: str, plan: UpdatePlan, result: GearboxUpdate) -> bool:
    """Whether a global of the app's was used by this press: an op of its in-place steps names it, and that step was
    done (the added gear inserted, the sleeve given its bands), so the record holds it as part of what was made."""
    for g in plan.in_place.added:
        if any(isinstance(op, base.AddGlobal) and op.name == name for op in g.ops):
            return g.gear in [gear for gear, _ in getattr(result, "inserted", []) or []]
    for b in plan.in_place.bands:
        if any(isinstance(op, base.AddGlobal) and op.name == name for op in b.ops):
            return b.gear in (getattr(result, "bands_added", []) or [])
    return False


def _follow_in_place(rec: LinkRecord, box: GearboxRecord, plan: UpdatePlan, result: GearboxUpdate,
                     read_sidecar: Callable[[str], Optional[Sidecar]], stamp: str, out: Finished,
                     written_by: str) -> None:
    """W9c (W9C-INTERFACES §7): the record follows what the worker reports done in place, and only that."""
    extra = plan.in_place_record or InPlaceRecord()
    # Gears taken out: their components and every mate touching them; their part's entry when no gear uses it (C6).
    for gear, _name in getattr(result, "deleted", []) or []:
        box.components = [c for c in box.components if c.gear != gear]
        box.mates = [m for m in box.mates if gear not in m.gears]
        box.fixed = [g for g in box.fixed if g != gear]
        box.unmated = [pair for pair in box.unmated if gear not in pair]
        box.meshes = [pair for pair in box.meshes if gear not in pair]
        for entry in rec.parts:              # ruling C6 (current_parts() no longer names it: its component is gone)
            if entry.revision == box.revision and gear in entry.gears:
                entry.gears = [g for g in entry.gears if g != gear]
        rec.parts = [p for p in rec.parts if p.gears or p.revision != box.revision]
    gone = set(getattr(result, "mates_deleted", []) or [])
    box.mates = [m for m in box.mates if m.name not in gone]
    # Modes taken out and added: the record's order, the added after it.
    removed = list(getattr(result, "modes_removed", []) or [])
    if removed:
        box.modes = [c for c in box.modes if c not in removed]
        for m in box.mates:
            m.values = {k: v for k, v in m.values.items() if k not in removed}
            m.modes = [c for c in m.modes if c not in removed]
            if m.kind == motion.SLIDE and box.modes and box.modes[0] in m.values:
                m.z_front = float(m.values[box.modes[0]])
        for c in box.components:
            c.frames = {k: f for k, f in c.frames.items() if k not in removed}
    # A press that stopped keeps the configurations it added, and the globals, as the app's leftovers (F1), handed back
    # as InPlace.left so the next press goes on from them; its modes are on record once a press runs to its end.
    added_modes = [c for c in getattr(result, "modes_added", []) or [] if c not in box.modes]
    if result.ok:
        box.modes = list(box.modes) + added_modes
    # The review's must-fix 2: each leftover stays until a press uses it (its step done) or takes it away, never
    # cleared because a press ran to its end; a configuration added is the app's leftover until a press that ran to its
    # end puts it on record as a mode.
    box.left_configurations = [c for c in dict.fromkeys(list(box.left_configurations) + added_modes)
                               if not (result.ok and c in added_modes)]
    kept: Dict[str, List[str]] = {}
    for doc, name in list(box.left_globals) + [list(g) for g in getattr(result, "globals_added", []) or []]:
        if not _global_used(name, plan, result):
            kept.setdefault(name, [doc, name])
    box.left_globals = list(kept.values())
    # Gears inserted: each by the Name2 SolidWorks kept, its frame from the plan (the trains' rule writes it after).
    placed = {p.gear: p for p in plan.placements}
    jobs = dict(extra.jobs)
    built = {store.sidecar_path(b.saved).lower(): b for b in getattr(result, "built", []) or [] if b.ok and b.saved}
    # Each new part built and saved is on record, whatever happened after (the coordinator's ruling on a press that
    # failed after building it): the next press hands it as an AddedGear with build None, never builds over it.
    for gear, job in jobs.items():
        b = built.get(store.sidecar_path(job.path).lower())
        if b is None or any(store.same_path(e.path, job.path) for e in rec.parts if e.revision == box.revision):
            continue
        kind = kind_for(job.spec)
        variables = [[v.name, v.expression_for(b.trig)] for v in kind.variables(job.spec, job.derived)]
        rec.parts.append(PartEntry(path=job.path, gears=[gear], revision=box.revision, kind=job.spec.kind,
                                   spec=job.spec.to_dict(), variables=variables, trig=b.trig))
        out.sidecars.append((store.sidecar_path(job.path), store.built_sidecar(
            job.path, os.path.basename(job.path), kind=job.spec.kind, recipe=job.plan.recipe,
            spec=job.spec.to_dict(), derived=job.derived.to_dict(), variables=variables, features=list(b.features),
            dimensions=sorted(b.dimensions.values()), manual_steps=list(b.manual),
            template=gearbox._template_of(job.plan), trig=b.trig, written_by=written_by,
            previous=read_sidecar(store.sidecar_path(job.path)), stamp=stamp, workbook=rec.workbook,
            workbook_gears=[gear])))
    for gear, name in getattr(result, "inserted", []) or []:
        p = placed.get(gear)
        job = jobs.get(gear)
        part = job.path if job is not None else (p.part if p is not None else "")
        box.components.append(store.ComponentEntry(gear=gear, part=part, name=name,
                                                   rotation=list(p.rotation) if p is not None else [],
                                                   at=list(p.at) if p is not None else []))
        if gear in extra.fixed and gear not in box.fixed:
            box.fixed.append(gear)
        entry = next((e for e in rec.parts if e.revision == box.revision and store.same_path(e.path, part)), None)
        if entry is not None:
            entry.gears = list(entry.gears) + ([gear] if gear not in entry.gears else [])
    # Mates made: as the plan has them, on in the configurations each reads on in.
    made = {name: tuple(on) for name, on in getattr(result, "mates_made", []) or []}
    plans = {m.name: m for m in extra.mates}
    for name, on in made.items():
        m = plans.get(name)
        if m is None or any(e.name == name for e in box.mates):
            continue
        entry = motion.mate_entry(m)
        if m.modes:
            entry.modes = [c for c in box.modes if c in on or on_in(tuple(m.modes), c)]
        if entry.values:
            entry.values = {(_conf(box.modes, k) or k): v for k, v in entry.values.items()}
        box.mates.append(entry)
    if getattr(result, "inserted", None) or getattr(result, "deleted", None):
        box.meshes = [list(pair) for pair in extra.meshes]
        names = {c.gear for c in box.components}
        box.unmated = [list(pair) for pair in extra.unmated if set(pair) <= names]


def _earlier_update(record: LinkRecord, plan: UpdatePlan, result: GearboxUpdate,
                    mtime: Callable[[str], float]) -> str:
    """Whether the record as read shows an earlier Update's change to the assembly that was never saved
    (``gearbox.UPDATE_LOST``, ``gearbox.UPDATE_NOT_SAVED`` or ``""``; see ``Finished``). Read from the record's
    ``unsaved`` mark on the assembly (the earlier finish marks every path of that Update's ``changed``), the
    assembly's file time as this job read it before changing anything (``result.mtimes``, else ``mtime``), and
    ``result.open_before``."""
    asm = plan.assembly
    if not asm:
        return ""
    then = next((t for p, t in record.unsaved.items() if store.same_path(p, asm)), None)
    if then is None:
        return ""
    now = next((t for p, t in (getattr(result, "mtimes", {}) or {}).items() if store.same_path(p, asm)), None)
    if (now is not None and now > then) or (now is None and store.saved_since(asm, then, mtime)):
        return ""                            # saved since: the file holds that Update's changes
    open_before = getattr(result, "open_before", None)
    if open_before is not None and not _in(asm, open_before):
        return gearbox.UPDATE_LOST
    return gearbox.UPDATE_NOT_SAVED


def _follow_trains(box: GearboxRecord, plan: UpdatePlan, result: GearboxUpdate, held: set) -> None:
    """A turning gearbox's mated gears take their wanted frames on record a whole train at a time, or not at all
    (review M1's spirit: a record mixing new and old frames within one train reads out of step next time). A train
    every gear of which was put takes them; so does every train when the update ran to its end with no failure,
    since the worker then left a train unput only because it already stood in step with its wanted frames. Trains
    are the mated gears joined by the meshes and locks given to the worker."""
    wanted = {p.gear: p for p in plan.placements}
    mated = [c.gear for c in box.components if c.gear in wanted and c.gear not in held]
    parent = {g: g for g in mated}

    def root(g: str) -> str:
        while parent[g] != g:
            g = parent[g]
        return g
    links = [(m.a, m.b) for m in plan.motion.meshes] + [(k.anchor, k.follower) for k in plan.motion.locks]
    for a, b in links:
        if a in parent and b in parent:
            parent[root(a)] = root(b)
    whole = not (result.failures or result.skipped)
    placed = set(result.placed)
    trains: Dict[str, List[str]] = {}
    for g in mated:
        trains.setdefault(root(g), []).append(g)
    take = {g for train in trains.values() if whole or all(g in placed for g in train) for g in train}
    for component in box.components:
        if component.gear in take:
            p = wanted[component.gear]
            component.rotation, component.at = list(p.rotation), list(p.at)


def _follow_carriers(box: GearboxRecord, plan: UpdatePlan, result: GearboxUpdate) -> None:
    """W7: each carrier on record takes its axes as now laid out once an Update ran to its end with no failure
    (its globals were set), and its wanted frame whenever its train was put or the update ran whole; a failed
    Update keeps what was last known true, as the ratios and senses do."""
    if not box.carriers or (result.failures or result.skipped):
        return
    laid = {c.shaft: c for c in plan.carrier_layouts}
    wanted = {p.gear: p for p in plan.placements}
    for entry in box.carriers:
        now = laid.get(entry.shaft)
        if now is not None:
            entry.axes = [ShaftEntry(**asdict(axis)) for axis in now.axes]
            entry.direction = list(now.direction)
        p = wanted.get(layout.carrier_id(entry.shaft))
        if p is not None:
            entry.rotation, entry.at = list(p.rotation), list(p.at)


def _teeth_held(plan: UpdatePlan, result: GearboxUpdate) -> Dict[str, int]:
    """Each gear's teeth as its part now holds them: the parts the update reached without a failure."""
    out: Dict[str, int] = {}
    for update, done in zip(plan.parts, result.parts):
        if done.failures or not (done.changed or done.unchanged):
            continue
        teeth = _number_or_none(getattr(update.spec, "teeth", None))
        if teeth:
            out.update({g: int(teeth) for g in update.gear_ids})
    return out


def _follow_mates(box: GearboxRecord, plan: UpdatePlan, result: GearboxUpdate) -> None:
    """The record's mates follow what Update set: a MESH entry's ``ratio`` for each gear mate in
    ``result.ratios`` or ``result.ratios_already`` that the plan asked to change (the ratio given, in the mate's
    own gear order), and an ALONG entry's ``z_front`` for each
    gear in ``result.axial`` (where its wanted frame puts its front face). A MESH whose gears' parts now hold teeth
    at the same ratio as the mate (17 : 68 → 34 : 136: no remake needed) takes those counts too, so a later
    classify does not read it as a change, and its pitch is the teeth the parts hold.

    W6 (W6-PLAN §2.7, §2.8; W6-INTERFACES §7.1): a MESH entry rewritten here takes its real sense (+1 or −1, the
    plan's ``k`` as ``c = −sign k``), never 0; one the worker remade for its sense (``result.resensed``) takes the new
    sense whether or not its ratio changed, and one the plan meant to remake that was not (a failure first) keeps
    the sense it was made with. As the ratios: on a failed or skipped Update no mesh's sense on record changes (a
    remade mate may not hold its new sense), and the next Update's classify finds it to remake again."""
    teeth = _teeth_held(plan, result)
    now_c = {(m.a, m.b): (1 if m.k < 0 else -1) for m in plan.motion.meshes if m.k}
    was_c = {(m.a, m.b): (1 if m.k < 0 else -1) for m in plan.motion.recorded_meshes if m.k}
    failed = bool(result.failures or result.skipped)
    remade = set() if failed else set(getattr(result, "resensed", []) or [])

    def real(entry: MateEntry) -> int:
        if failed and entry.sense in (-1, 1):
            return int(entry.sense)
        pair = (entry.gears[0], entry.gears[1])
        if entry.name in plan.resensed and entry.name not in remade:
            return int(was_c.get(pair, entry.sense))
        return int(now_c.get(pair, entry.sense))
    for entry in box.mates:
        if entry.kind != motion.MESH or len(entry.gears) != 2 or len(entry.ratio) != 2:
            continue
        a, b = entry.gears
        if a in teeth and b in teeth and (teeth[a], teeth[b]) != tuple(entry.ratio) and \
                entry.ratio[0] * teeth[b] == entry.ratio[1] * teeth[a]:
            entry.ratio = [teeth[a], teeth[b]]
            entry.sense = real(entry)
        if entry.name in remade:
            entry.sense = real(entry)
    # A gear mate remade (``ratios``), or one the plan asked to change that SolidWorks already held at the wanted
    # ratio and so was not remade (``ratios_already``: a lost Update's record typed back, say), takes the plan's
    # ratio. One found at another ratio and remade though the plan asked no change (``ratios_found``, also in
    # ``ratios``) is not in the plan's ratios: the record already holds the wanted ratio for it.
    set_ratios = set(getattr(result, "ratios", []) or []) | set(getattr(result, "ratios_already", []) or [])
    if result.failures or result.skipped:
        # An Update that failed keeps on record the ratios last known true: a mate listed in ``ratios`` may not hold
        # the new one (a remake read wrong with both Flips is listed before its sense is settled), and the next
        # Update's live read finds what it does hold.
        set_ratios = set()
    moved = set(getattr(result, "axial", []) or [])
    given = {name: [int(n), int(d)] for name, n, d in plan.motion.ratios}
    at = {p.gear: p.at for p in plan.placements}
    for entry in box.mates:
        if entry.kind == motion.MESH and entry.name in set_ratios and entry.name in given:
            entry.ratio = list(given[entry.name])
            entry.sense = real(entry)
        elif entry.kind == motion.ALONG and entry.gears and entry.gears[0] in at and (
                entry.gears[0] in moved or planetary.copy_of(entry.gears[0])[0] in moved):   # W7: by row (§6.7)
            index = motion._PLANE_INDEX.get(entry.plane or motion.FRONT_PLANE, 2)
            entry.z_front = float(at[entry.gears[0]][index])


def _follow_modes(box: GearboxRecord, plan: UpdatePlan, result: GearboxUpdate) -> None:
    """W8 (W8-PLAN §1.10's ``finish_update``): each SLIDE entry's values follow the values set, each coupling's and
    sliding mesh's ``modes`` the flags set, and each component's per-mode frames what was put there. An Update that
    ran whole with no failure takes the plan's own (the worker left a value, a flag or a frame alone only because it
    already held it); one that stopped takes only what it reports set (``slid``, ``unsuppressed_in`` /
    ``suppressed_in``, ``put_in`` with ``placed``). Keys keep the record's spelling and ``GearboxRecord.modes`` is
    never reordered (§9.6, §9.9). A slide keeps a value for every mode, and an on-set is never written ``[]``
    (§9.1): a flag set that would leave a mate on in no mode keeps the on-set it had."""
    motion_ = plan.motion
    if motion_ is None or not motion_.configurations or not box.modes:
        return
    whole = not (result.failures or result.skipped)
    confs = list(box.modes)

    def own(name: str) -> Optional[str]:
        return _conf(confs, name)
    slides = {m.name: m for m in box.mates if m.kind == motion.SLIDE}
    set_values = list(motion_.slide_values) if whole else list(getattr(result, "slid", []) or [])
    for name, conf, value in set_values:
        entry, key = slides.get(name), own(conf)
        if entry is None or key is None:
            continue
        sign = next((1.0 if float(v) > 0 else -1.0 for v in entry.values.values() if float(v)), 1.0)
        values = {own(k) or k: float(v) for k, v in entry.values.items()}
        values[key] = sign * abs(float(value))
        entry.values = {c: values[c] for c in confs if c in values}
        if confs[0] in entry.values:
            entry.z_front = entry.values[confs[0]]
    per_mode = {m.name: m for m in _per_mode(box.mates)}
    if whole:
        wanted = {name: list(on) for name, on in motion_.on_sets}
    else:
        wanted = {name: [c for c in confs if on_in(tuple(m.modes), c)] for name, m in per_mode.items()}
        for name, conf in getattr(result, "unsuppressed_in", []) or []:
            key = own(conf)
            if name in wanted and key is not None and key not in wanted[name]:
                wanted[name].append(key)
        for name, conf in getattr(result, "suppressed_in", []) or []:
            key = own(conf)
            if name in wanted and key in wanted[name]:
                wanted[name].remove(key)
    for name, on in wanted.items():
        entry = per_mode.get(name)
        if entry is not None and on:
            entry.modes = [c for c in confs if c in on]
    put = {own(c) for c in getattr(result, "put_in", []) or []} - {None}
    placed = set(result.placed)
    for conf, placements in motion_.mode_placements:
        key = own(conf)
        if key is None:
            continue
        for p in placements:
            component = next((c for c in box.components if c.gear == p.gear), None)
            if component is None or not (whole or (key in put and p.gear in placed)):
                continue
            frames = {own(k) or k: f for k, f in component.frames.items()}
            frames[key] = {"rotation": [float(v) for v in p.rotation], "at": [float(v) for v in p.at]}
            component.frames = {c: frames[c] for c in confs if c in frames}


def _in(path: str, paths) -> bool:
    return any(store.same_path(path, p) for p in paths)


def _drop(marks: Dict[str, float], path: str) -> None:
    for key in [k for k in marks if store.same_path(k, path)]:
        del marks[key]


def _settled(plan: UpdatePlan, result: GearboxUpdate) -> List[str]:
    """The documents this update loaded from their files (``result.opened``) and found holding what the workbook
    asks, changing nothing in them: each part and the layout reached without a failure and left as it was, and
    the assembly reached, unchanged, with no failure of its own."""
    opened = list(getattr(result, "opened", []) or [])
    out: List[str] = []
    for update, done in zip(plan.parts, result.parts):
        if _in(update.path, opened) and done.unchanged and not done.changed and not done.failures:
            out.append(update.path)
    done = result.layout
    if (plan.layout is not None and done is not None and _in(plan.layout.path, opened) and done.unchanged
            and not done.changed and not done.failures):
        out.append(plan.layout.path)
    asm = plan.assembly
    if (asm and _in(asm, opened) and not _in(asm, result.changed) and not result.placed
            and not any(what == os.path.basename(asm.replace("\\", "/")) for what, _ in result.failures)
            and not result.skipped):
        out.append(asm)
    return out


# -- W9a package B: the user's work on record, said before the press (ISSUE-1-PLAN §2.1 items 6 and 8, K4, K5) ---------

def user_work_entry(work: swbuild.UserWork, *, assembly: str, digest: str = "", revision: Sequence[int] = (),
                    problems: Sequence[swbuild.UserProblem] = ()) -> store.UserWorkEntry:
    """What the record keeps of an Update's read of the user's work (schema 7): the worker's inventory, the assembly
    and workbook read it was made in and from, the SolidWorks it ran on, and — for a press that refused over the
    user's work — every problem it said."""
    return store.UserWorkEntry(
        read_at=work.read_at or store.now(), assembly=assembly, digest=digest,
        revision=[int(n) for n in revision],
        components=[store.UserComponentEntry(c.name, _component_kind(c.path), bool(c.fixed), int(c.code), int(c.state))
                    for c in work.components],
        mates=[store.UserMateEntry(m.name, m.kind, int(m.type), [[w, n] for w, n in m.touches], list(m.on),
                                   int(m.code), bool(m.warning), bool(m.whole),
                                   [[str(x) for x in e] for e in getattr(m, "entities", ()) or ()])  # W9d, D5
               for m in work.mates],
        features=[store.UserFeatureEntry(f.path, f.name, f.type_name, int(f.code), bool(f.warning))
                  for f in work.features],
        carried=[store.UserCarriedEntry(c, g, list(locks)) for c, g, locks in work.carried],
        problems=[store.UserProblemEntry(p.kind, p.sentence, list(p.mates),
                                         [store.ValueEditEntry(v.document, v.name, v.live, v.wanted, v.recorded,
                                                               v.mode, v.cell, bool(v.unsaved)) for v in p.values],
                                         [str(s) for s in getattr(p, "subjects", ()) or ()])
                  for p in problems])


_KIND_EXTENSION = {"part": ".SLDPRT", "assembly": ".SLDASM"}


def _component_kind(path: str) -> str:
    """A user component's kind for the record, by its file's extension: ``assembly``, ``part``, or ``""`` when
    SolidWorks would not name the file."""
    if not path:
        return ""
    return "assembly" if path.lower().endswith(".sldasm") else "part"


def recorded_user_work(entry: store.UserWorkEntry) -> swbuild.UserWork:
    """The record's inventory back as the worker's :class:`swbuild.UserWork`, for its pure judgement only. Each
    component's ``path`` is made up (its name with its kind's extension, ``Sprocket-1.SLDPRT``), since the record
    keeps no path of the user's: right for the judgement's one use of it (the sub-assembly branch reads the
    extension), and never a file to open."""
    return swbuild.UserWork(
        read_at=entry.read_at,
        # The record keeps no user file path, only its kind, so each component is given a path by its name with the
        # extension the worker's judgement reads (its sub-assembly branch); one whose file was not named, none.
        components=[swbuild.UserComponent(c.name, _KIND_EXTENSION.get(c.kind, "") and c.name + _KIND_EXTENSION[c.kind],
                                          c.fixed, c.code, c.state) for c in entry.components],
        mates=[swbuild.UserMate(m.name, m.kind, m.type, tuple((w, n) for w, n in m.touches), tuple(m.on), m.code,
                                m.warning, m.whole) for m in entry.mates],
        features=[swbuild.UserFeature(f.path, f.name, f.type_name, f.code, f.warning) for f in entry.features],
        carried=[(c.component, c.gear, tuple(c.locks)) for c in entry.carried])


def modes_read(plan: UpdatePlan) -> List[str]:
    """The configurations a press's read of the user's work covers (the fixes review's S6): the worker reads the modes
    after the Update that exist at its start, so the plan's configurations less those it adds; ``[]`` with no modes."""
    m = plan.motion
    if m is None:
        return []
    return [str(c) for c in m.configurations if c not in plan.in_place.modes_added]


def record_user_work(record: LinkRecord, work: Optional[swbuild.UserWork], *, assembly: str, digest: str = "",
                     revision: Sequence[int] = (), problems: Sequence[swbuild.UserProblem] = (),
                     modes_read: Sequence[str] = ()) -> bool:
    """Put what a press read of the user's work into ``record`` (in place) as its gearbox's ``user_work``, when the
    record's assembly is the one read (a record whose current revision has moved on is left alone). Whether it was
    written. ``work`` None (the assembly was not read) leaves what is on record as it was."""
    box = record.gearbox
    if box is None or not box.assembly or not store.same_path(box.assembly, assembly):
        return False
    if work is None:
        if not problems:
            return False
        # W9c (§5): a refusal read before the user's work (the mode showing) keeps the inventory on record as it was
        # (its components, mates, features and carries), with the refusal's time, workbook, SolidWorks and problems,
        # so the footer says them as any refusal's until the next press reads again. With none on record, an empty
        # inventory carries them: nothing of the user's is claimed, and the next press reads it all.
        said = user_work_entry(swbuild.UserWork(), assembly=assembly, digest=digest, revision=revision,
                               problems=problems)
        kept = box.user_work
        if kept is None:
            # Nothing ever read: an entry that carries the refusal alone, marked unread, which the foresight takes as
            # no inventory at all (the review's should-fix 3: never an empty inventory as if it were a read).
            box.user_work = replace(said, read_at="", refused_at=said.read_at, unread=True)
        else:
            # The inventory keeps its own read time; the refusal's time is kept beside it.
            box.user_work = replace(kept, digest=digest, refused_at=said.read_at, problems=said.problems)
        return True
    box.user_work = user_work_entry(work, assembly=assembly, digest=digest, revision=revision, problems=problems)
    box.user_work.modes = list(modes_read)     # the configurations the read covered (a press's adds follow it)
    return True


def refused_update(record: LinkRecord, plan: UpdatePlan, error: swbuild.UserWorkRefused, *, digest: str,
                   revision: Sequence[int] = ()) -> LinkRecord:
    """The record after a press that refused over the user's work before changing anything (K4): a copy with the
    inventory as read and every problem said, so the footer says them until the next press reads again. Pure."""
    rec = copy.deepcopy(record)
    record_user_work(rec, error.user_work, assembly=plan.assembly, digest=digest, revision=revision,
                     problems=error.problems, modes_read=modes_read(plan))
    if rec.gearbox is not None and revision:
        rec.gearbox.solidworks = [int(n) for n in revision]
    return rec


@dataclass(frozen=True)
class UserWorkAhead:
    """What the footer says before a press of the user's work on record (K4), decided here and worded by
    ``ui_text``: ``entry`` the record's inventory (its ``read_at``); ``refused`` the problems of the last press when
    it refused over the user's work, and ``changed_since`` whether the workbook read now is not the one that press
    was made from; otherwise the prediction by the worker's own judgement (``swbuild.judge_user_work`` on the
    inventory, no tie read): ``carried`` gear -> [(component, the user's locks)], ``problems`` the refusals it
    foresees, ``unread_ties`` (gears, user mates) of each train SolidWorks will be asked about at the press.
    ``followed``: the user's features in parts this press changes, which SolidWorks rebuilds after the app's.
    ``still``: after a refusal the workbook has changed since, each recorded K11 value the workbook still does not
    ask as SolidWorks held it, with what the workbook asks now (package B's re-check R1): that refusal stands."""

    entry: store.UserWorkEntry
    refused: Tuple[store.UserProblemEntry, ...] = ()
    changed_since: bool = False
    still: Tuple[Tuple[store.ValueEditEntry, str], ...] = ()
    carried: Tuple[Tuple[str, Tuple[Tuple[str, Tuple[str, ...]], ...]], ...] = ()
    problems: Tuple[swbuild.UserProblem, ...] = ()
    unread_ties: Tuple[Tuple[Tuple[str, ...], Tuple[str, ...]], ...] = ()
    followed: Tuple[swbuild.UserFeature, ...] = ()


def _on_record(record: Optional[LinkRecord]) -> Optional[store.UserWorkEntry]:
    """The record's inventory of the user's work in its current assembly, or None."""
    box = getattr(record, "gearbox", None)
    entry = getattr(box, "user_work", None)
    if entry is None or not box.assembly or (entry.assembly and not store.same_path(entry.assembly, box.assembly)):
        return None
    return entry


def _judged_trains(plan: UpdatePlan) -> Tuple[List[str], List[Tuple[str, ...]]]:
    """The mated bodies, and the trains as the worker's check joins them (``swbuild._user_check``): without modes, a
    held gear joined only through its gear-mated meshes; with modes, over every mode's links (the mode that will be
    showing at the press is not known here)."""
    m = plan.motion
    gears = [p.gear for p in plan.placements]
    fixed = set(m.fixed)
    mated = [g for g in gears if g not in fixed]
    held = [g for g in m.held if g in gears]
    judged = mated + [g for g in held if g not in mated]
    meshes = list(m.meshes)
    if not m.configurations:
        pairs = {tuple(x.gears) for x in m.mates if x.kind == motion.MESH and len(x.gears) == 2}
        meshes = [x for x in meshes if not ({x.a, x.b} & set(held)) or (x.a, x.b) in pairs]
    return mated, swbuild._trains(judged, meshes, m.locks, m.carriers)


def bodies_put(plan: UpdatePlan) -> set:
    """The app bodies a press of ``plan`` would put, foreseen from the record as the worker's check judges it from
    SolidWorks (``swbuild._may_put``): with modes, every mated body whenever the press changes anything (ruling
    9.18); without, every train with a gear re-placed, moved along its shaft or whose gear mate is remade, and every
    train when the layout or a carrier moves. A held or fixed gear only when it is re-placed. A quiet press puts
    nothing (unless SolidWorks turns out to differ, which only the press reads)."""
    m = plan.motion
    if m is None:
        return set()
    gears = [p.gear for p in plan.placements]
    still = set(m.fixed) | set(m.held)
    free = {g for g in gears if g not in still}
    moved_still = {g for g in plan.replaced if g in still}
    changing = bool(not plan.record_matches or plan.axial or plan.ratios or plan.resensed or plan.carriers_moved
                    or plan.modes_changed)
    if not changing:
        return set()
    if m.configurations or plan.moved_shafts or plan.carriers_moved:
        return free | moved_still
    remade = set(plan.ratios) | set(plan.resensed)
    seeds = set(plan.replaced) | set(plan.axial) | {g for x in m.mates if x.name in remade for g in x.gears}
    _, trains = _judged_trains(plan)
    return {g for train in trains if set(train) & seeds for g in train if g in free} | moved_still


def user_work_ahead(plan: Optional[UpdatePlan], record: Optional[LinkRecord],
                    digest: str = "") -> Optional[UserWorkAhead]:
    """K4: what a press of ``plan`` would do with the user's work the record holds, or None when nothing is on
    record, nothing of the user's was read, or the plan is not an Update (refused, or a new revision). The worker's
    own pure judgement on the recorded inventory, never a second one: a recorded refusal (a tie is a solver read
    nothing here can redo) is said as recorded; otherwise ``swbuild.judge_user_work`` with the bodies the press
    would put (:func:`bodies_put`), every branch of route (c1) from ``swbuild.user_carry_branches`` (always given:
    an unmeasured branch is foreseen as refused) and the SolidWorks the inventory was read on."""
    entry = _on_record(record)
    if entry is None or plan is None or plan.refusal or plan.needs_new_revision:
        return None
    if not entry and not entry.problems:
        return None
    work = recorded_user_work(entry)
    followed = tuple(f for f in work.features if any(store.same_path(f.path, p.path) for p in plan.changed_parts))
    refused = tuple(entry.problems)
    changed_since = bool(refused) and bool(digest) and bool(entry.digest) and entry.digest != digest
    if refused and not changed_since:
        return UserWorkAhead(entry, refused=refused, followed=followed)
    if entry.unread:
        return None                       # a refusal carried with nothing read: nothing of the user's to foresee
    still: Tuple[Tuple[store.ValueEditEntry, str], ...] = ()
    if changed_since:
        still = tuple((v, now) for p in refused if p.kind == swbuild.PROBLEM_VALUE for v in p.values
                      for now in [_asked_now(plan, v)] if now is not None)
    # A press that went ahead, or a refused one the workbook has changed since (the coordinator's ruling on package
    # B's review, point 5): the prediction, on the inventory as last read.
    m = plan.motion
    if m is None:                                    # W4's static path reads the user's features only
        return UserWorkAhead(entry, refused=refused, changed_since=changed_since, still=still, followed=followed)
    mated, trains = _judged_trains(plan)
    if plan.in_place.modes_removed:
        # The review's must-fix 1: the worker reads the user's flags over the modes after the Update only, so the modes
        # removed leave each recorded mate's on-list first (the mirror of swbuild.work_in_added_modes).
        work = swbuild.work_without_modes(work, plan.in_place.modes_removed)
    # A mode the inventory never read the user's flags in: one this press adds, and — on a record written before the
    # runs review's must-fix (its inventory has no ``modes``) — one an earlier press added after the read. Each is
    # judged as a copy of a mode the inventory did read, as the worker made it.
    read = _modes_read(entry)
    copies = tuple(plan.in_place.modes_added) + tuple(
        c for c in m.configurations if c not in plan.in_place.modes_added and read is not None and c not in read)

    def judge(copied: str) -> Any:
        judged = work
        if copies and copied:
            # F2: an added mode is a copy of the mode showing at the press: the user's mates on there are on in it too.
            judged = swbuild.work_in_added_modes(work, copies, copied)
        return swbuild.judge_user_work(
            judged, tuple(m.configurations) or ("",), bodies_put(plan),
            file=os.path.basename(plan.assembly.replace("\\", "/")), trains=trains, mated=mated, read_tie=None,
            branches=swbuild.user_carry_branches(m, plan.placements), revision=tuple(entry.revision))

    # The mode showing at the press is not known here (the review's should-fix 4): an added mode is judged as a copy of
    # each mode on record in turn, and only what every one of them foresees is foreseen.
    shown = [c for c in m.configurations if c not in copies] if copies else []
    judgements = [judge(c) for c in shown] or [judge("")]
    judgement = judgements[0]
    problems = [p for p in judgement.problems
                if all(any(_problem_key(p) == _problem_key(q) for q in other.problems) for other in judgements[1:])]
    return UserWorkAhead(entry, refused=refused, changed_since=changed_since, still=still,
                         carried=tuple((g, tuple(held)) for g, held in judgement.carried.items()),
                         problems=tuple(problems), unread_ties=tuple(judgement.unread_ties),
                         followed=followed)


def in_place_ahead(plan: Optional[UpdatePlan], record: Optional[LinkRecord]) -> Tuple[swbuild.UserProblem, ...]:
    """W9c (K4; W9C-INTERFACES §5, §8): what would stop a press of ``plan``'s in-place change, foreseen as the worker
    judges it (``swbuild.judge_in_place``), from the record: each step whose finding is not settled for the
    SolidWorks the record's inventory was read on (unknown with none: every gated step then reads unsettled), the
    user's mates on a gear to be taken out, and a removal while any component of the user's is there and the
    external-references read is unmeasured (C4). ``()`` when the plan changes nothing in place, is refused or needs a
    new revision. The mode showing (C12) and an added mode's name taken are read live, at the press, never here."""
    if plan is None or plan.refusal or plan.needs_new_revision:
        return ()
    modes = tuple(plan.motion.configurations) if plan.motion is not None else ()
    if not plan.in_place and not (modes and plan.ratios):        # a gear mate made again with modes is gated too
        return ()
    entry = _on_record(record)
    work = recorded_user_work(entry) if entry is not None and not entry.unread else None

    def judge(revision: Sequence[int]) -> List[swbuild.UserProblem]:
        return swbuild.judge_in_place(
            work, plan.in_place, file=os.path.basename(plan.assembly.replace("\\", "/")) or "the assembly",
            revision=revision, modes=modes, remakes=bool(modes) and bool(plan.ratios))

    revision = solidworks_on_record(record)
    if revision:
        return tuple(judge(revision))
    # No SolidWorks version on record (no press has read one yet): judged over every version the findings know
    # (the demonstration's first contact). Stopped on every one, foreseen as stopping; on none, nothing foreseen; on
    # some, a PROBLEM_DEPENDS naming the findings not yet shown, said as depending on the SolidWorks in use.
    known = [(year, judge(rev)) for year, rev in known_finding_revisions()]
    if not known:
        return tuple(judge(()))
    out: List[swbuild.UserProblem] = []
    for problem in judge(()):
        key = _problem_key(problem)
        stopped = [(year, q) for year, found in known for q in found if _problem_key(q) == key]
        if len(stopped) == len(known):
            out.append(problem)
        elif stopped:
            unshown = tuple(s for _, q in stopped for s in q.subjects if _FINDING_YEAR.search(s))
            # A problem naming no finding (none such yet) is foreseen as it stands rather than left unsaid.
            out.append(swbuild.UserProblem(PROBLEM_DEPENDS, problem.sentence, mates=tuple(problem.mates),
                                           subjects=unshown) if unshown else problem)
    return tuple(out)


# W9c (the demonstration's first contact): a step that stops a press on some SolidWorks versions the findings know and
# not on others, foreseen with no version on record. ``subjects``: the findings not yet shown, each on its year.
PROBLEM_DEPENDS = "depends on the version"
_FINDING_YEAR = re.compile(r"_ON_(\d{4}|\?)$")


def _modes_read(entry: store.UserWorkEntry) -> Optional[set]:
    """The configurations the inventory holds the user's flags for: its ``modes`` (written since the runs review's
    must-fix); on an older record, the configurations any of its mates is on in (a mode no mate of the user's is on
    in reads as never read, and is judged as a copy); None with no mates (nothing judged by mode)."""
    if entry.modes:
        return {str(c) for c in entry.modes}
    if not entry.mates:
        return None
    return {str(c) for m in entry.mates for c in m.on}


def follow_modes_added(entry: Optional[store.UserWorkEntry], result: GearboxUpdate, modes: Sequence[str]) -> None:
    """The runs review's must-fix: an inventory read at the start of a press that then added modes holds no flag of
    the user's there. Each user mate's flag the worker read in a mode it added (``result.took_active_state``) goes
    into its on-list, for each added mode the record now holds; ``entry.modes`` becomes the record's modes, so the
    inventory says which configurations it covers: those the read covered (``entry.modes`` as recorded) and each added
    mode on record whose flags the worker read (the fixes review's S6: never a mode no read covered). In place."""
    if entry is None or entry.unread:
        return
    on_record = {str(c) for c in modes}
    by_name = {m.name: m for m in entry.mates}
    read_there: List[str] = []
    for mode, item, state in getattr(result, "took_active_state", []) or []:
        if mode in on_record and mode not in read_there:
            read_there.append(mode)
        mate = by_name.get(item)
        if mate is None or mode not in on_record:
            continue
        if state == "on" and mode not in mate.on:
            mate.on = list(mate.on) + [mode]
        elif state == "suppressed" and mode in mate.on:
            mate.on = [c for c in mate.on if c != mode]
    entry.modes = [c for c in modes if c in set(entry.modes) | set(read_there)]


def solidworks_on_record(record: Optional[LinkRecord]) -> Tuple[int, ...]:
    """The SolidWorks revision the record last saw: its user-work inventory's (the last Update's read), else the one
    its last Build or Update ran on (``GearboxRecord.solidworks``, schema 9), else ``()`` (an older record)."""
    entry = _on_record(record)
    if entry is not None and entry.revision:
        return tuple(entry.revision)
    box = getattr(record, "gearbox", None)
    return tuple(getattr(box, "solidworks", ()) or ())


def known_finding_revisions() -> List[Tuple[int, Tuple[int, ...]]]:
    """``(year, revision)`` for each SolidWorks release the findings hold values for (a ``…_ON_<year>`` name), oldest
    first; the revision is the major one ``swcom.release_year`` names that year by."""
    from .. import findings, swcom
    years = sorted({int(m.group(1)) for name in dir(findings) for m in [_FINDING_YEAR.search(name)]
                    if m is not None and m.group(1).isdigit()})
    base = swcom.release_year(0)
    return [(year, (year - base,)) for year in years]


def _problem_key(problem: swbuild.UserProblem) -> Tuple[Any, ...]:
    """A problem as the same whatever version it was judged on: its kind, its mates and its subjects less the year."""
    return (problem.kind, tuple(problem.mates), tuple(_FINDING_YEAR.sub("", s) for s in problem.subjects))


def _same_value(live: str, wanted: str) -> bool:
    """Whether two values K11 said, as text, are the same: as numbers where both are, else as text without spaces."""
    a, b = swbuild._literal(live), swbuild._literal(wanted)
    if a is not None and b is not None:
        return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))
    return swbuild._squash(str(live)) == swbuild._squash(str(wanted))


def _asked_now(plan: UpdatePlan, value: store.ValueEditEntry) -> Optional[str]:
    """R1 of package B's re-check: what the workbook now asks for a K11 value a press refused on, as text, when it
    still is not what SolidWorks held (``value.live``), so that refusal stands; None when the workbook now asks the
    value SolidWorks held, or no longer sets it. A part's, the layout's or a carrier's global is judged against the
    plan's globals; on the assembly, a Face Z, a slide's value in its mode and a mate's flag in its mode against the
    plan's motion; anything this cannot find stands (the press reads it again)."""
    def named(path: str) -> bool:
        return os.path.basename(str(path).replace("\\", "/")).lower() == value.document.lower()
    documents = [(p.path, p.variables) for p in plan.parts]
    documents += [(d.path, d.variables) for d in ([plan.layout] if plan.layout is not None else []) + list(plan.carriers)]
    m = plan.motion
    if m is not None and plan.assembly and named(plan.assembly):
        documents.append((plan.assembly, tuple(g for _, g in m.face_globals)))
        for name, configuration, wanted in m.slide_values:
            if name == value.name and configuration.casefold() == value.mode.casefold():
                now = swbuild._number_text(abs(float(wanted)), str(wanted))
                return None if _same_value(value.live, now) else now
        for name, on in m.on_sets:
            if name == value.name and value.mode:
                now = "on" if any(c.casefold() == value.mode.casefold() for c in on) else "suppressed"
                return None if now == value.live else now
    for path, variables in documents:
        if not named(path):
            continue
        variable = next((v for v in variables if v.name == value.name), None)
        if variable is None:
            return None                              # the workbook no longer sets it
        expression = variable.expression_for(equations.DEGREES)
        literal = swbuild._literal(expression)
        now = swbuild._number_text(literal, expression)
        return None if _same_value(value.live, now) else now
    return value.wanted or "another value"


@dataclass(frozen=True)
class StaysBehind:
    """K5 until W9d: what of the user's a Build again… leaves in the old revision, from the record's inventory with
    its time (``entry.read_at``): ``assembly`` the old assembly; ``components`` and ``mates`` (names) in it;
    ``left`` (feature, old part path, the gears whose new part replaces it) for each user feature in a part the new
    revision makes new; ``kept`` (feature, part path) for each in a part it reuses, which comes along with the part.
    ``entry`` None when the record holds no inventory, or one with nothing in it: then only that anything added
    there stays there is said (the coordinator's ruling on package B's review, point 4)."""

    entry: Optional[store.UserWorkEntry]
    assembly: str
    components: Tuple[str, ...] = ()
    mates: Tuple[str, ...] = ()
    left: Tuple[Tuple[str, str, Tuple[str, ...]], ...] = ()
    kept: Tuple[Tuple[str, str], ...] = ()


def stays_behind(record: Optional[LinkRecord], again: Any) -> Optional[StaysBehind]:
    """What :class:`StaysBehind` says for a Build again… of ``again`` (``gearbox.GearboxPlan``) from ``record``; None
    when the record has no assembly; with no inventory of it on record, or one with nothing of the user's in it, a
    :class:`StaysBehind` with no ``entry``."""
    box = getattr(record, "gearbox", None)
    if box is None or not box.assembly or again is None:
        return None
    entry = _on_record(record)
    if entry is None or not entry:
        return StaysBehind(None, box.assembly)
    reused = [r.path for r in getattr(again, "reuse", ()) or ()]
    gears_of = {p.path: p.gears for p in record.parts}
    left, kept = [], []
    for f in entry.features:
        if any(store.same_path(f.path, r) for r in reused):
            kept.append((f.name, f.path))
            continue
        gears = next((tuple(g) for path, g in gears_of.items() if store.same_path(path, f.path)), ())
        left.append((f.name, f.path, gears))
    return StaysBehind(entry, record.gearbox.assembly, tuple(c.name for c in entry.components),
                       tuple(m.name for m in entry.mates), tuple(left), tuple(kept))


def old_assembly(record: Optional[LinkRecord], again: Any) -> Optional[swbuild.OldAssembly]:
    """For a Build again… (``again``, a ``gearbox.GearboxPlan`` whose assembly is not the one on record): the
    assembly it leaves behind, for the build job to read the user's work in first (``swbuild.build_gearbox``'s
    ``before``); None for any other build."""
    box = getattr(record, "gearbox", None)
    if box is None or not box.assembly or again is None or getattr(again, "assembly", None) is None:
        return None
    if store.same_path(getattr(again, "assembly_path", "") or "", box.assembly):
        return None
    bodies = [(c.gear, c.name) for c in box.components if c.name]
    bodies += [(layout.carrier_id(c.shaft), c.component) for c in box.carriers if c.component]
    return swbuild.OldAssembly(box.assembly, tuple(bodies), box.layout_component, box.layout,
                               tuple(m.name for m in box.mates), tuple(box.modes))


# -- W9d: Build again… carries the user's work (ISSUE-1-PLAN §2.5; W9D-INTERFACES §2.1, §7, §9.1) -----------------

# Each spec field a gear's part is built from, as the Gears sheet calls it (``schema.GEAR_COLUMNS``), for why a gear's
# part is new: *its Flank changed*. ``shaft_angle`` and ``mate_teeth`` are a bevel gear's, from its shafts and its mate.
_SPEC_COLUMNS = (("name", "Part name"), ("kind", "Kind"), ("teeth_side", "Side"), ("recipe", "Flank"),
                 ("teeth", "Teeth"), ("module", "Module"), ("pressure_angle", "Pressure angle"),
                 ("face_width", "Face width"), ("bore", "Bore"), ("helix_angle", "Helix angle"), ("hand", "Hand"),
                 ("groove", "Groove"), ("profile_shift", "Profile shift"), ("backlash", "Backlash"),
                 ("fillet", "Fillet"), ("rim", "Rim"), ("start_band", "Start band"), ("end_band", "End band"),
                 ("shaft_angle", "shaft angle"), ("mate_teeth", "mate's Teeth"))

WHY_NEW_UNSAVED = "it had changes from Update SolidWorks that were not saved"
WHY_NEW_MISMATCHED = "it did not hold what the record says, as the last job in SolidWorks found"
WHY_NEW_LAYOUT = "its layout part is new with every revision"
WHY_NEW_CARRIER = "its carrier part is new with this revision"
WHY_NEW_VALUES = "its values changed"


def _changed_columns(built: Mapping[str, Any], wanted: Mapping[str, Any]) -> List[str]:
    """The Gears columns whose values differ between two parts' forms (``GearSpec.to_dict``), in sheet order; a blank
    and its default compare the same way ``gearbox.same_part`` reads them, as text without spaces."""
    out = []
    for key, column in _SPEC_COLUMNS:
        default = "external" if key == "teeth_side" else ""
        was, now = (str(values.get(key, default) or default) for values in (built, wanted))
        if swbuild._squash(was) != swbuild._squash(now):
            out.append(column)
    return out


def _why_part_new(entry: Optional[PartEntry], gear: str, again: Any) -> str:
    """B's phrase for why ``gear``'s part in the new revision is a new file (``CarryBody.why_new``): a part that would
    have been reused but for Update's unsaved changes or a live check (``again.made_new``), else the Gears columns that
    changed (*its Flank changed*, *its Teeth and Face width changed*), else *its values changed*."""
    for made in getattr(again, "made_new", ()) or ():
        if gear in made.gear_ids and made.why == gearbox.UNSAVED:
            return WHY_NEW_UNSAVED
        if gear in made.gear_ids and made.why == gearbox.MISMATCHED:
            return WHY_NEW_MISMATCHED
    job = next((j for j in getattr(again, "build", ()) or () if gear in j.gear_ids), None)
    if entry is not None and entry.spec and job is not None:
        columns = _changed_columns(entry.spec, job.spec.to_dict())
        if columns:
            return f"its {_names(columns)} changed"
    return WHY_NEW_VALUES


def _old_carrier_names(entry: store.CarrierEntry) -> Tuple[str, ...]:
    """The app's own feature names in a carrier part as the record has it: its own axis, then each copy's planes and
    axis (``layout.carrier_shafts``' order)."""
    return layout.layout_features((layout._local_axis(entry.shaft, 0.0, 0.0, 0.0),) + tuple(entry.axes))


def carry_for(record: Optional[LinkRecord], again: Any, old: Optional[swbuild.OldAssembly], *,
              read_sidecar: Callable[[str], Optional[Sidecar]] = store.read_sidecar) -> Optional[swbuild.Carry]:
    """What a carrying Build again… is given (W9D-INTERFACES §2.1): every app body on record in ``old`` (the layout
    first, carriers, then gears) and what stands for it in ``again`` (``gearbox.GearboxPlan``): planet copy *k* to copy
    *k* (by id, the same on both), a body the new plan has no handle for with handle ``""``; ``same_file`` when the new
    plan reuses the very file the old component was; ``why_new`` from ``again.made_new`` and the Gears columns that
    changed; ``names`` the app's own features in the new file (``plan_features`` of a part made new, the sidecar's of
    one reused, ``layout_features`` of the layout and each carrier) and ``old_names`` in the old (its sidecar's, the
    recorded shafts'). ``modes`` the new revision's in Modes-sheet order, ``first`` the old record's first mode,
    ``written_on`` the SolidWorks the last job on record ran on, ``app_files`` every file the record names as the app's.
    None when ``old`` is None (not a Build again…). Pure but for ``read_sidecar``."""
    box = getattr(record, "gearbox", None)
    if old is None or box is None or again is None:
        return None
    bodies: List[swbuild.CarryBody] = []
    new_layout = getattr(again, "layout_path", "") or ""
    layout_same = bool(new_layout) and store.same_path(new_layout, box.layout)
    bodies.append(swbuild.CarryBody(
        old=layout.LAYOUT_HANDLE, old_name=box.layout_component,
        handle=layout.LAYOUT_HANDLE if getattr(again, "layout", None) is not None else "", same_file=layout_same,
        why_new="" if layout_same else WHY_NEW_LAYOUT, names=layout.layout_features(tuple(again.shafts)),
        old_names=layout.layout_features(tuple(box.shafts))))
    handle_of = {cid: h for h, cid in again.carrier_handles.items()}
    new_carriers = {c.shaft: c for c in getattr(again, "carrier_layouts", ()) or ()}
    for c in box.carriers:
        cid = layout.carrier_id(c.shaft)
        handle = handle_of.get(cid, "")
        path = (getattr(again, "carrier_paths", None) or {}).get(c.shaft, "")
        same = bool(handle) and bool(path) and store.same_path(path, c.path)
        drawn = new_carriers.get(c.shaft)
        bodies.append(swbuild.CarryBody(
            old=cid, old_name=c.component, handle=handle, same_file=same,
            why_new="" if same or not handle else WHY_NEW_CARRIER,
            names=layout.layout_features(layout.carrier_shafts(drawn)) if drawn is not None else (),
            old_names=_old_carrier_names(c)))
    gear_handle = {gear: h for h, gear in again.handles.items()}
    parts = {p.path: p for p in record.parts}
    for c in box.components:
        handle = gear_handle.get(c.gear, "")
        new_path = again.part_of.get(c.gear, "") if handle else ""
        reused = next((r for r in again.reuse if store.same_path(r.path, c.part)), None)
        same = bool(handle) and reused is not None and store.same_path(new_path, c.part)
        entry = next((p for path, p in parts.items() if store.same_path(path, c.part)), None)
        old_sidecar = read_sidecar(store.sidecar_path(c.part)) if c.part else None
        old_names = tuple(old_sidecar.record.features) if old_sidecar is not None else ()
        if same:
            names = tuple(reused.features) or old_names
        else:
            job = next((j for j in again.build if c.gear in j.gear_ids), None)
            names = swbuild.plan_features(job.plan) if job is not None and job.plan is not None else ()
        bodies.append(swbuild.CarryBody(
            old=c.gear, old_name=c.name, handle=handle, same_file=same,
            why_new="" if same or not handle else _why_part_new(entry, c.gear, again),
            names=tuple(names), old_names=old_names))
    modes_plan = getattr(again, "modes_plan", None)
    modes = tuple(step.name for step in modes_plan.steps) if modes_plan is not None else ()
    files: List[str] = [p.path for p in record.parts]
    files += [box.layout, box.assembly] + [c.path for c in box.carriers]
    for earlier in record.earlier:
        files += [earlier.layout, earlier.assembly] + list(earlier.parts)
    app_files: List[str] = []
    for path in files:
        if path and not any(store.same_path(path, p) for p in app_files):
            app_files.append(path)
    return swbuild.Carry(old=old, bodies=tuple(bodies), modes=modes, first=box.modes[0] if box.modes else "",
                         written_on=tuple(int(n) for n in box.solidworks), app_files=tuple(app_files))


def recorded_old_work(record: Optional[LinkRecord]) -> Optional[swbuild.OldWork]:
    """The record's inventory of the user's work in its assembly as an :class:`swbuild.OldWork` (W9D-INTERFACES §2.3),
    for the Build again? question to foresee through ``swbuild.plan_carry`` what is carried and what named: each
    component's file a stand-in by its Name2 (the record keeps only its kind), no frames
    (``new_frames`` empty, and each component at the world frame, so its placement is not judged here), no definitions
    beyond what the inventory keeps (type, entities, flags per mode, code), ``how`` OLD_OPEN (as it would be read where
    it stands), ``active`` ``""`` (the inventory does not keep which mode showed), each component's configurations
    None (never kept). A schema 9 inventory's mates have no entity kinds:
    a lock's entities are whole components by what a lock is (S5's ReferenceType2 0), every other mate's are
    ``ENTITY_UNREAD`` with ``unread`` ``"not on record"``, which the question words as *may*. None with no inventory of
    the current assembly, or one never read."""
    entry = _on_record(record)
    if entry is None or entry.unread:
        return None
    box = record.gearbox
    identity: swbuild.Frame9 = (layout.IDENTITY, (0.0, 0.0, 0.0))
    # The record never keeps a user's file (W9a ruling 6), only its kind: a component stands for its file by its own
    # Name2 and the kind's extension, so the foresight takes it as on disk; the press reads the real one.
    components = [swbuild.OldComponent(
        name=c.name, path=c.name + (".SLDASM" if c.kind == "assembly" else ".SLDPRT"), kind=c.kind, fixed=c.fixed, code=c.code, state=c.state, frame=identity,
        virtual="^" in c.name) for c in entry.components]
    mates = []
    for m in entry.mates:
        if m.entities:
            entities = tuple(swbuild.OldEntity(what=e[0], owner=e[1], kind=e[2], feature=e[3]) for e in m.entities)
        else:
            kind = swbuild.ENTITY_WHOLE if m.kind == swbuild.USER_LOCK else swbuild.ENTITY_UNREAD
            entities = tuple(swbuild.OldEntity(what=t[0], owner=t[1], kind=kind,
                                               unread="" if kind == swbuild.ENTITY_WHOLE else UNKNOWN_ENTITY)
                             for t in m.touches)
        mates.append(swbuild.OldMate(name=m.name, type=m.type, type_name="", alignment=0, flipped=False, values=(),
                                     entities=entities, on=tuple(m.on), code=m.code, warning=m.warning,
                                     whole=m.whole))
    return swbuild.OldWork(read_at=entry.read_at, assembly=box.assembly, how=swbuild.OLD_OPEN,
                           active="", modes=tuple(box.modes), components=components,
                           mates=mates, app_frames=())


UNKNOWN_ENTITY = "not on record"


def _follow_carry(rec: LinkRecord, plan: UpdatePlan, result: GearboxUpdate, out: Finished,
                  mtime: Callable[[str], float]) -> None:
    """W9d (D16, §9.4): ``CarryEntry.unsaved_at`` after a later Update of the revision a Build again… carried into.
    Found loaded from its file by this job (``result.opened``, or not open when it began), the assembly does not hold
    what was carried: the mark goes and the press's sentence says it was lost; saved since (its file newer), the mark
    goes silently. ``LinkRecord.unsaved`` is not the carry's and is not touched."""
    carried = store.carry_unsaved(rec)
    if carried is None or not plan.assembly:
        return
    open_before = getattr(result, "open_before", None)
    loaded = _in(plan.assembly, getattr(result, "opened", []) or []) or (
        open_before is not None and not _in(plan.assembly, open_before))
    if loaded and not store.saved_since(plan.assembly, carried.unsaved_at, mtime):
        from .. import ui_text
        carried.unsaved_at = 0.0
        out.notes.append(ui_text.carry_lost_line(plan.assembly, carried.assembly))
        return
    store.clear_carry_saved(rec, mtime)     # OldEntity.unread of a schema 9 inventory's entity: its kind was never kept


@dataclass(frozen=True)
class CarryForesight:
    """What the Build again? question says of the user's work (W9D-INTERFACES §9.1), from the record's inventory with
    its time, through ``swbuild.plan_carry``'s foresight (:func:`carry_foresight`). ``assembly`` the old assembly,
    ``entry`` its inventory (None: nothing of the user's on record); ``year`` the SolidWorks the record last saw
    (``"?"``: not known); ``inserts`` whether ``CARRY_INSERTS`` is set there (None: not known, with ``shown`` and
    ``unshown`` the years it is and is not set on); ``plan`` what ``plan_carry`` foresees (None: nothing foreseen, the
    worker not able to say); ``assumed`` the components whose file's configurations the record does not keep (foreseen
    as a file of one) and ``configuration`` the findings unset that a file of several needs; ``not_open`` the findings
    unset that keep a closed old assembly from being read at all (R.2), and ``keeps_open`` the one that lets it be read
    beside open documents, if unset; ``states_read`` whether the states per mode can be read unshown; ``modes_gone``
    the old modes the revision has not, ``modes_new`` its modes the old record has not, ``first`` the old record's
    first mode; ``stays`` the features left in parts made new and kept in parts reused (W9a's); ``why_new`` gear ->
    why its part is new; ``made_new`` gear -> ``MadeNew.why``; ``values`` part file name -> the K11 value on record
    for it (MISMATCHED's advice)."""

    assembly: str
    name: str
    entry: Optional[store.UserWorkEntry]
    year: str
    inserts: Optional[bool]
    shown: Tuple[str, ...] = ()
    unshown: Tuple[str, ...] = ()
    plan: Optional[swbuild.CarryPlan] = None
    assumed: Tuple[str, ...] = ()
    configuration: Tuple[str, ...] = ()
    not_open: Tuple[str, ...] = ()
    keeps_open: str = ""
    states_read: bool = False
    modes_gone: Tuple[str, ...] = ()
    modes_new: Tuple[str, ...] = ()
    first: str = ""
    stays: Optional[StaysBehind] = None
    why_new: Mapping[str, str] = field(default_factory=dict)
    made_new: Mapping[str, str] = field(default_factory=dict)
    values: Mapping[str, store.ValueEditEntry] = field(default_factory=dict)


def _finding(name: str, year: str) -> Any:
    return getattr(findings, f"{name}_ON_{year}", None)


def _record_year(record: Optional[LinkRecord]) -> str:
    """The SolidWorks year the record last saw (:func:`solidworks_on_record`), ``"?"`` when not known."""
    from .. import swcom
    revision = solidworks_on_record(record)
    return str(swcom.release_year(int(revision[0]))) if revision else "?"


# R.2's conditions that hold a closed old assembly unread whatever is open (W9D-INTERFACES §3 R.2, the re-check's R1
# and S-f), in the order the question names them; OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS only when documents are open.
NOT_OPEN_FINDINGS = ("FILE_VERSION_READ", "DEPENDENCIES_READ", "OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN")


def carry_foresight(record: Optional[LinkRecord], again: Any, *, plan_carry: Optional[Callable[..., Any]] = None,
                    read_sidecar: Callable[[str], Optional[Sidecar]] = store.read_sidecar
                    ) -> Optional[CarryForesight]:
    """:class:`CarryForesight` for a Build again… of ``again`` from ``record``; None when the record has no assembly
    (nothing is left behind). ``plan_carry`` is ``swbuild.plan_carry`` (a test passes its own); called on
    :func:`recorded_old_work` with ``new_frames`` empty, each component whose configurations the record does not keep
    foreseen as a file of one (``assumed``: the question says so). A foresight that raises is no foresight
    (``plan`` None): the question then says only that the press reads and carries what it can."""
    box = getattr(record, "gearbox", None)
    if box is None or not box.assembly or again is None:
        return None
    entry = _on_record(record)
    if entry is not None and (entry.unread or not entry):
        entry = None
    year = _record_year(record)
    if year == "?":
        known = [str(y) for y, _ in known_finding_revisions()]
        shown = tuple(y for y in known if _finding("CARRY_INSERTS", y))
        unshown = tuple(y for y in known if y not in shown)
        inserts = None if shown and unshown else bool(shown)
    else:
        shown = unshown = ()
        inserts = bool(_finding("CARRY_INSERTS", year))
    old = old_assembly(record, again)
    carry = carry_for(record, again, old, read_sidecar=read_sidecar) if old is not None else None
    plan = None
    assumed: Tuple[str, ...] = ()
    work = recorded_old_work(record) if entry is not None else None
    if work is not None and carry is not None and inserts:
        assumed = tuple(c.name for c in work.components if c.configurations is None)
        work.components = [replace(c, configurations=("",)) if c.configurations is None else c
                           for c in work.components]
        revision = solidworks_on_record(record)
        try:
            plan = (plan_carry or swbuild.plan_carry)(work, carry, revision, new_frames={})
        except Exception:  # noqa: BLE001 - a foresight never stops the question: the press reads and says
            plan = None
    probe = year if year != "?" else (unshown[0] if unshown else (shown[0] if shown else "?"))
    configuration = tuple(f"{n}_ON_{probe}" for n in ("REFERENCED_CONFIGURATION_READ",
                                                      "CARRY_INSERTS_IN_A_CONFIGURATION")
                          if not _finding(n, probe))
    not_open = tuple(f"{n}_ON_{probe}" for n in NOT_OPEN_FINDINGS if not _finding(n, probe))
    keeps = "" if _finding("OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS", probe) else \
        f"OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS_ON_{probe}"
    new_modes = tuple(carry.modes) if carry is not None else ()
    gone = tuple(m for m in box.modes if not any(m.casefold() == n.casefold() for n in new_modes))
    added = tuple(m for m in new_modes if not any(m.casefold() == o.casefold() for o in box.modes))
    why_new = {b.old: b.why_new for b in (carry.bodies if carry is not None else ()) if b.why_new}
    made = {g: m.why for m in getattr(again, "made_new", ()) or () for g in m.gear_ids}
    values: Dict[str, store.ValueEditEntry] = {}
    for problem in (entry.problems if entry is not None else []):
        for value in problem.values:
            values.setdefault(value.document.lower(), value)
    return CarryForesight(
        assembly=box.assembly, name=getattr(again, "name", "") or "", entry=entry, year=year, inserts=inserts,
        shown=shown, unshown=unshown, plan=plan, assumed=assumed if plan is not None else (),
        configuration=configuration, not_open=not_open, keeps_open=keeps,
        states_read=bool(_finding("COMPONENT_STATE_PER_CONFIGURATION_ROUTE", probe)),
        modes_gone=gone if new_modes else (), modes_new=added if box.modes else (),
        first=box.modes[0] if box.modes else "", stays=stays_behind(record, again), why_new=why_new, made_new=made,
        values=values)
