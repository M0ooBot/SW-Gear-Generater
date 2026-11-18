"""Print files (PLAN-PRINTED §3.1.3, §3.1.4): which parts a press exports to STEP for the slicer, where, and whether a
file written is fit to print. Pure planning: structure and codes, never a sentence a user reads (must-fix M4).

F2-0 fixed the names, the dataclasses and the codes (``docs/notes-printed/F2-INTERFACES.md`` §2); package B filled
:func:`form_print`, :func:`workbook_print`, :func:`check_step` and :func:`write_list` and added what its note
(``docs/notes-printed/F2-PACKAGE-B.md``) lists. B returns codes, package C's ``ui_text`` words them (one sentence per code),
and ``swbuild.print_parts`` (B's) runs the job a plan describes.

The gate (:func:`gate`) is read here at planning and again by the job: while ``findings.SAVE_AS_COPY`` is None every press
is refused with :data:`GATE_COPY`, and while ``findings.STEP_EXPORT_ON_<year>`` is not True for the connected SolidWorks
with :data:`GATE`. Both are None on every version until a reviewed run of ``probe/f2_probes.py`` sets them, so until then
no folder is chosen and nothing is written.

Imports at run time: ``gears`` (each part's kind, to derive its span and its size), ``spec``, ``findings`` (the gate),
``store.same_path`` and ``swcom.release_year`` (neither imports ``swbuild``). ``store``'s, ``workbook.assess``'s and
``workbook.update``'s types are annotations only.
"""

from __future__ import annotations

import math
import os
import re
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from . import findings
from .gears import kind_for
from .gears.span import NONE as NO_SPAN, SpanReading, span
from .spec import GearSpec
from .store import same_path
from .swcom import release_year

if TYPE_CHECKING:                                   # annotations only: workbook.update imports swbuild, which imports
    from .store import LinkRecord, Sidecar          # this module (no cycle at run time)
    from .workbook.assess import Assessment
    from .workbook.update import UpdatePlan

# The connected SolidWorks' revision, as ``swcom.Session.revision`` reads it ((34, 1, 1)); () when none is connected.
SolidWorksVersion = Tuple[int, ...]

# -- refusal codes (Refusal.code) ----------------------------------------------------------------------------------------
# Planning (pure, before any job): form_print and workbook_print.
GATE = "GATE"                      # STEP_EXPORT_ON_<year> is not True for the connected version (or none is connected)
GATE_COPY = "GATE_COPY"            # findings.SAVE_AS_COPY is None: refused on every version
UNSAVED_MARK = "UNSAVED_MARK"      # the record marks a part unsaved (W9a's mark, update._mark)
MISMATCHED_MARK = "MISMATCHED_MARK"  # the record marks a part mismatched
CHANGES_ON_UPDATE = "CHANGES_ON_UPDATE"  # Update SolidWorks would change a part's values or make it new (E3: not the
#                                          layout or the assembly alone)
NO_PART = "NO_PART"                # a Gears row has no part yet, or a part on record is not on disk
WORKBOOK_ERROR = "WORKBOOK_ERROR"  # the workbook has an error
FOREIGN_RECORD = "FOREIGN_RECORD"  # the record is not this workbook's
NO_RECORD = "NO_RECORD"            # the form: the active part has no readable .gear.json beside it
NOT_A_PART = "NOT_A_PART"          # the form: nothing is active in SolidWorks, or the active document is not a part
# F2-REVIEW's must-fix M1 (the coordinator's ruling): a part whose change Update SolidWorks cannot carry, since the
# Update plan needs a new revision (workbook.update.UpdatePlan.needs_new_revision: Update is then never run and the window
# offers Build again…). Detail as CHANGES_ON_UPDATE's, {stem: "values" or "new part"}; the user is told to use Build
# again…, never Update SolidWorks.
NEW_REVISION = "NEW_REVISION"
PLANNING_CODES = (GATE, GATE_COPY, UNSAVED_MARK, MISMATCHED_MARK, CHANGES_ON_UPDATE, NO_PART, WORKBOOK_ERROR,
                  FOREIGN_RECORD, NO_RECORD, NOT_A_PART, NEW_REVISION)
# The job (swbuild.print_parts), per part, after every part's reads and before any file is written; then the export.
MODIFIED = "MODIFIED"              # the part's own GetSaveFlag is on
GLOBALS_DIFFER = "GLOBALS_DIFFER"  # a live global is not what its record says (spaces aside, swbuild._squash)
FEATURE_IN_ERROR = "FEATURE_IN_ERROR"  # a feature's GetErrorCode2 is non-zero and not a warning
COMPONENT_ONLY = "COMPONENT_ONLY"  # open only inside an assembly, and neither measured route reaches it
# Package B's addition, to the coordinator's ruling after F2's probe run (8d2c5fb): a part not found among SolidWorks'
# documents while an assembly is open may be a lightweight component of it (neither the walk nor GetOpenDocumentByName
# reaches one, and opening the part beside resolves it, changing the user's assembly), so it is refused by name: resolve
# it, or open the part, and press again. Detail as COMPONENT_ONLY's: {stem: the one open assembly's file name, or ""}.
LIGHTWEIGHT = "LIGHTWEIGHT"
SOLIDWORKS_REFUSED = "SOLIDWORKS_REFUSED"  # SolidWorks would not open, reach or export a part (its codes or swcom's)
FILE_CHECK = "FILE_CHECK"          # a file written failed check_step
JOB_CODES = (MODIFIED, GLOBALS_DIFFER, FEATURE_IN_ERROR, COMPONENT_ONLY, LIGHTWEIGHT, SOLIDWORKS_REFUSED, FILE_CHECK)
CODES = PLANNING_CODES + JOB_CODES

# -- check_step's reason codes (§3.1.4) ----------------------------------------------------------------------------------
FRAME = "FRAME"                    # it does not begin ISO-10303-21; or end END-ISO-10303-21;
SCHEMA = "SCHEMA"                  # its FILE_SCHEMA is none of STEP_SCHEMAS
SOLIDS = "SOLIDS"                  # not exactly one MANIFOLD_SOLID_BREP instance, or no CLOSED_SHELL
OPEN_SHELL = "OPEN_SHELL"          # an OPEN_SHELL instance
SURFACE_MODEL = "SURFACE_MODEL"    # a SHELL_BASED_SURFACE_MODEL instance
UNIT = "UNIT"                      # no length unit it can read
EXTENT = "EXTENT"                  # largest radius from the axis or axial extent off the part's by over EXTENT_TOL
REASONS = (FRAME, SCHEMA, SOLIDS, OPEN_SHELL, SURFACE_MODEL, UNIT, EXTENT)
EXTENT_TOL = 0.01                  # mm

# The schemas a file may declare, matched by the FILE_SCHEMA name's prefix (SolidWorks writes the name followed by
# "{ 1 0 10303 ... }"; AP203's second edition is AP203_CONFIGURATION_CONTROLLED_3D_DESIGN_..., not
# CONFIG_CONTROL_DESIGN): the re-check's should-fix. Which one a file declares is the user's Tools > Options > Export.
STEP_SCHEMAS: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("AP203", ("CONFIG_CONTROL_DESIGN", "AP203_CONFIGURATION_CONTROLLED_3D_DESIGN")),
    ("AP214", ("AUTOMOTIVE_DESIGN",)),
    ("AP242", ("AP242_MANAGED_MODEL_BASED_3D_ENGINEERING",)),
)

# -- the files' place and names (§3.1.3, M3) ------------------------------------------------------------------------------
PRINT_FOLDER = "print"             # <Output folder>\print\<press folder>\
PRESS_FOLDER_FORMAT = "%Y-%m-%d %H.%M.%S"   # time.strftime; a name that exists gets " (2)", " (3)", ...
LIST_NAME = "print list.txt"
STEP_SUFFIX = ".step"              # each part's file: its stem + STEP_SUFFIX, so ..._r2.SLDPRT prints as ..._r2.step

# Keys of PrintResult.facts, each joined to a file's name: "<file>|schema" the FILE_SCHEMA name as written,
# "<file>|unit" the length unit as read ("MILLI.METRE", "METRE", "INCH", "FOOT"), "<file>|extent" "checked" or
# "skipped: <why>" (EXTENT_SKIPPED). Facts, never refusals.
FACT_SCHEMA, FACT_UNIT, FACT_EXTENT = "schema", "unit", "extent"
EXTENT_SKIPPED = ("bevel", "ring", "sleeve", "dog", "hub", "herringbone", "user features", "not measured")
# Package B's additions to the facts (data, never a sentence; the coordinator's to rule): "<title>|close" is
# "failed: <swcom's sentence>" for a window the job opened and could not close, and "job|flags" is "unread: <swcom's
# sentence>" when the save flags could not be read again at the end (then flags_turned_on cannot be known).
FACT_CLOSE, FACT_FLAGS, FACT_JOB = "close", "flags", "job"

# Whether the size check is made is findings.EXTENT_MEASURED (moved there by the coordinator's ruling on F2-REVIEW's
# choice B6): True since F2's probe reruns bore it out on spur and helical gears on both versions. EXTENT_TOL's 0.01 mm
# keeps eight times 2026's largest measured excess (0.0012 mm at the spur's tip), while a cut missing, another part's
# file or a unit slip is off by far more. A herringbone is skipped ("herringbone") until a run has measured one.

# CHANGES_ON_UPDATE's detail values (F2-INTERFACES.md §2.3): Update would change a part's values, or put a new part in
# the gearbox (a part it would build new, one that needs building again, or a part a gear added in place brings).
CHANGE_VALUES, CHANGE_NEW_PART = "values", "new part"
# NO_PART's detail values.
NO_PART_YET, NOT_ON_DISK = "no part", "not on disk"


@dataclass(frozen=True)
class Refusal:
    """Why a press writes nothing (planning) or no usable set (the job): a code of :data:`CODES`, the parts it names
    (stems; for NO_PART the Gears rows; for NOT_A_PART / NO_RECORD the active document's file name, or none), and its
    detail, keyed per code as ``F2-INTERFACES.md`` §2.3 gives."""

    code: str
    parts: Tuple[str, ...] = ()
    detail: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class PrintPart:
    """One part of a press: its file, its stem, the rows it serves (Sun, Planet), how many to print (one per row it
    serves, times a planet's copies), its process word, its span (A's :func:`gears.span.span`), the user's features
    left in it by name (the record's inventory; () on the form), and its spec as recorded.

    Package B's additions (the coordinator's to rule; F2-INTERFACES.md §2.1 has no field for them and the job needs
    both): ``variables``, the (global, expression) pairs the record says the file holds, which the job compares with the
    live globals (GLOBALS_DIFFER; () when the record has none, and then nothing is compared); ``made``, the features the
    record lists as the app's, from which the job tells the user's features live (``swbuild._user_features``), so the
    size check is skipped for a part of the form's that holds one."""

    path: str
    stem: str
    rows: Tuple[str, ...] = ()
    count: int = 1
    process: str = ""
    span: SpanReading = NO_SPAN
    user_features: Tuple[str, ...] = ()
    spec: GearSpec = field(default_factory=GearSpec)
    variables: Tuple[Tuple[str, str], ...] = ()
    made: Tuple[str, ...] = ()


@dataclass(frozen=True)
class PrintPlan:
    """A press as planned: a refusal (then no parts and no folder), or the parts and the press's own new folder, chosen
    here by M3's rule and made by the job. F2-0's additions, for the job and the list's head: ``revision`` is the version
    the gate was read for (the job refuses with GATE when the session's revision is not this one); ``name`` is the
    gearbox's name (the Box's), or on the form the part's stem; ``pressed`` is the press's time, seconds since the
    epoch, the one its folder is named by."""

    refusal: Optional[Refusal]
    parts: Tuple[PrintPart, ...] = ()
    folder: str = ""
    revision: SolidWorksVersion = ()
    name: str = ""
    pressed: float = 0.0


@dataclass(frozen=True)
class PrintResult:
    """What the job did (``swbuild.print_parts``). ``written``: (part path, file path); ``failed``: (file path, reason
    code of :data:`REASONS`); ``facts``: see :data:`FACT_SCHEMA`; ``active_restored``: the document active at the start
    is active again (True when it was closed meanwhile by the user, or none was); ``flags_turned_on``: documents (paths,
    a new one's title) whose save flag the job turned on; ``warnings`` (F2-0's addition): (part path, feature names) of
    features whose GetErrorCode2 is a warning, which do not refuse (the re-check's should-fix).

    ``active_restored`` has no default (F2-0-REVIEW S7, given to package B): every result says it, so a job that forgot
    to put the user's document back cannot read as having done so: it is a keyword every caller must give
    (``PrintResult(refusal=..., active_restored=True)``), and leaving it out is a TypeError, not a quiet True."""

    written: Tuple[Tuple[str, str], ...] = ()
    folder: str = ""
    refusal: Optional[Refusal] = None
    failed: Tuple[Tuple[str, str], ...] = ()
    facts: Mapping[str, str] = field(default_factory=dict)
    active_restored: bool = field(kw_only=True)
    flags_turned_on: Tuple[str, ...] = ()
    warnings: Tuple[Tuple[str, Tuple[str, ...]], ...] = ()


# -- the gate (§3 of the interface; checked here at planning and again by swbuild.print_parts) --------------------------


def dotted(version: SolidWorksVersion) -> str:
    """A revision as SolidWorks writes it, "32.5.0"; "" for none."""
    return ".".join(str(n) for n in version)


def version_detail(version: SolidWorksVersion, prefix: str = "") -> Dict[str, str]:
    """GATE's detail for a version: ``year`` and ``revision`` ("2024", "32.5.0"), each key behind ``prefix``
    ("planned_" for the plan's); {} for none."""
    version = tuple(version or ())
    if not version:
        return {}
    return {f"{prefix}year": str(release_year(version[0])), f"{prefix}revision": dotted(version)}


def gate(version: SolidWorksVersion) -> Optional[Refusal]:
    """Whether Print files may write on this SolidWorks: None when it may, else the refusal. GATE_COPY while
    ``findings.SAVE_AS_COPY`` is None (every version; it comes first, so it is said even with none connected); GATE
    with no detail when none is connected; GATE with the year and revision while ``findings.STEP_EXPORT_ON_<year>`` is not
    True (a year with no such finding is not measured)."""
    if getattr(findings, "SAVE_AS_COPY", None) is None:
        return Refusal(GATE_COPY)
    version = tuple(version or ())
    if not version:
        return Refusal(GATE)
    if getattr(findings, f"STEP_EXPORT_ON_{release_year(version[0])}", None) is not True:
        return Refusal(GATE, (), version_detail(version))
    return None


# -- the press's folder (M3) ----------------------------------------------------------------------------------------------

_COUNTER = re.compile(r" \((\d+)\)$")


def free_folder(folder: str, exists: Callable[[str], bool] = os.path.exists) -> str:
    """``folder`` when nothing is there, else the first of "<folder> (2)", "<folder> (3)" ... that is free. A folder
    already carrying a counter counts on from its base name, so the job's second look never gives "... (2) (2)"."""
    if not exists(folder):
        return folder
    base = _COUNTER.sub("", folder)
    n = 2
    while exists(f"{base} ({n})"):
        n += 1
    return f"{base} ({n})"


def press_folder(output_folder: str, pressed: float, exists: Callable[[str], bool] = os.path.exists) -> str:
    r"""``<output folder>\print\<press time>``, the press's local time by :data:`PRESS_FOLDER_FORMAT`, with a counter when
    that name is taken."""
    stamp = time.strftime(PRESS_FOLDER_FORMAT, time.localtime(pressed))
    return free_folder(os.path.join(output_folder, PRINT_FOLDER, stamp), exists)


def step_name(part: PrintPart) -> str:
    """The file a part prints as: its stem and :data:`STEP_SUFFIX`, nothing added (``..._r2`` stays ``..._r2``)."""
    return part.stem + STEP_SUFFIX


def _file(path: str) -> str:
    return str(path or "").replace("/", "\\").rsplit("\\", 1)[-1]


def _stem(path: str) -> str:
    return os.path.splitext(_file(path))[0]


def _key(path: str) -> str:
    return str(path or "").replace("/", "\\").lower()


# -- one part ------------------------------------------------------------------------------------------------------------


def _derived(spec: GearSpec):
    """``(kind, derived)`` of a spec as recorded, or (kind, None) / (None, None) when it does not derive or has no kind."""
    kind = kind_for(spec)
    if kind is None:
        return None, None
    try:
        return kind, kind.derive(spec)
    except Exception:  # noqa: BLE001 - a record whose spec no longer derives: no span, and its size cannot be checked
        return kind, None


def _span_of(spec: GearSpec) -> SpanReading:
    kind, derived = _derived(spec)
    if derived is None:
        return NO_SPAN
    try:
        return span(derived, kind.recipe_for(spec))
    except Exception:  # noqa: BLE001 - A's span never raises; a recipe that does not read gives no span
        return NO_SPAN


def print_part(path: str, spec: Optional[Mapping[str, object]], *, variables: Sequence[Sequence[str]] = (),
               made: Sequence[str] = (), rows: Sequence[str] = (), count: int = 1,
               user_features: Sequence[str] = ()) -> PrintPart:
    """A :class:`PrintPart` from a part's record: its spec (``GearSpec.to_dict()`` as kept), its globals as recorded, the
    app's features, the rows it serves and how many to print, the user's features on record."""
    gear = GearSpec.from_dict(dict(spec or {}))
    return PrintPart(path=path, stem=_stem(path), rows=tuple(rows), count=int(count), process=gear.process,
                     span=_span_of(gear), user_features=tuple(user_features), spec=gear,
                     variables=tuple((str(p[0]), str(p[1])) for p in variables if len(p) == 2),
                     made=tuple(str(m) for m in made))


# -- the planners --------------------------------------------------------------------------------------------------------


def _refused(refusal: Refusal, version: SolidWorksVersion) -> PrintPlan:
    return PrintPlan(refusal, revision=tuple(version or ()))


def form_print(sidecar: Optional["Sidecar"], part_path: str, output_folder: str, version: SolidWorksVersion, *,
               now: Optional[float] = None, exists: Callable[[str], bool] = os.path.exists) -> PrintPlan:
    """The form's press: the part active in SolidWorks (``part_path``, "" when none) with its ``.gear.json`` read
    (``sidecar``, None when there is none or it does not read), into ``output_folder``'s print folder. ``now`` (seconds
    since the epoch, the press's time) and ``exists`` are for tests; None is the clock.

    The refusals in order: the gate (:func:`gate`); NOT_A_PART when nothing is active or what is active is not a part
    (``part_path`` not a .SLDPRT; its file name in ``parts`` when there is one); NO_RECORD when it has no readable
    ``.gear.json`` (its file name). Otherwise one part, the plan's ``name`` its stem. An empty ``output_folder`` (the
    strip's) falls back to the part's own folder (B's choice, the coordinator's to rule)."""
    refusal = gate(version)
    if refusal is not None:
        return _refused(refusal, version)
    name = _file(part_path)
    if not part_path or not str(part_path).lower().endswith(".sldprt"):
        return _refused(Refusal(NOT_A_PART, (name,) if name else ()), version)
    if sidecar is None:
        return _refused(Refusal(NO_RECORD, (name,)), version)
    record = sidecar.record
    part = print_part(part_path, record.spec, variables=record.variables, made=record.features)
    pressed = time.time() if now is None else float(now)
    folder = press_folder(output_folder or os.path.dirname(part_path), pressed, exists)
    return PrintPlan(None, (part,), folder, tuple(version), part.stem, pressed)


def _copies(spec, row: str) -> int:
    """How many of a Gears row's gear stand in the gearbox: its shaft's Copies (a planet's), else 1."""
    gear = spec.gear(row)
    shaft = spec.shaft(gear.shaft) if gear is not None else None
    try:
        return max(1, int(float(str(getattr(shaft, "copies", "") or "1").strip() or "1")))
    except ValueError:
        return 1


def workbook_print(record: Optional["LinkRecord"], assessment: Optional["Assessment"],
                   update_plan: Optional["UpdatePlan"], output_folder: str, version: SolidWorksVersion, *,
                   now: Optional[float] = None, exists: Callable[[str], bool] = os.path.exists) -> PrintPlan:
    """The Workbook window's press: every part of the record's current revision (``LinkRecord.current_parts``) that a
    Gears row of the workbook still uses, each once, from the window's planning read (``assessment``, and ``update_plan``
    as ``workbook.update.classify`` gives it), into ``output_folder`` (the Box's, else the strip's) print folder.

    The refusals in order (F2-INTERFACES.md §2.2), each naming every part it applies to:

    - the gate (:func:`gate`);
    - FOREIGN_RECORD: the record beside the workbook is another's (``update_plan.foreign_record``);
    - WORKBOOK_ERROR: no assessment, or it has an error, is provisional (Excel to recalculate an Export), or holds fixes
      chosen and not exported;
    - NO_PART: a Gears row no part on record serves and no Update would add in place (detail "no part"), or a part on
      record that is not on disk ("not on disk"); with nothing built, every row;
    - WORKBOOK_ERROR again when there is no ``update_plan`` or it is refused for another reason: Update cannot say what it
      would change, so whether the parts are the workbook's cannot be told (B's choice, the coordinator's to rule);
    - UNSAVED_MARK, MISMATCHED_MARK: the record's marks on a part (W9a's, ``update._mark``);
    - CHANGES_ON_UPDATE: a part whose values Update would change ("values"), and a gear Update would add in place ("new
      part", its part's stem), while Update can run;
    - NEW_REVISION instead (F2-REVIEW M1) when the Update plan needs a new revision (``needs_new_revision``: Update is
      never run, Build again… is the way): the same parts and detail, a part that needs a part of its own or building
      again among them ("new part").

    A change Update would make only to the layout or the assembly does not refuse (E3), and neither does a part whose
    every row has gone from the workbook: it is left out of the set (B's choice, the coordinator's to rule). Each part's
    rows are the Gears rows it serves, in the workbook's order, and its count one per row times the row's shaft's Copies.
    An empty ``output_folder`` falls back to the assessment's folder, then the workbook's own."""
    refusal = gate(version)
    if refusal is not None:
        return _refused(refusal, version)
    if update_plan is not None and getattr(update_plan, "foreign_record", ""):
        return _refused(Refusal(FOREIGN_RECORD), version)
    if assessment is None or assessment.errors or assessment.provisional or assessment.chosen:
        return _refused(Refusal(WORKBOOK_ERROR), version)
    spec = assessment.spec
    rows = [g.id for g in spec.gears]
    entries = list(record.current_parts()) if record is not None else []
    added = tuple(getattr(getattr(update_plan, "in_place", None), "added", ()) or ())
    added_rows = {a.gear for a in added}

    served = {g for e in entries for g in e.gears}
    no_part = [r for r in rows if r not in served and r not in added_rows]
    kept = [e for e in entries if any(g in rows for g in e.gears)]
    off_disk = [e for e in kept if not exists(e.path)]
    if no_part or off_disk or not rows:
        detail = {r: NO_PART_YET for r in no_part}
        detail.update({_stem(e.path): NOT_ON_DISK for e in off_disk})
        return _refused(Refusal(NO_PART, tuple(detail), detail), version)
    if update_plan is None or getattr(update_plan, "refusal", ""):
        return _refused(Refusal(WORKBOOK_ERROR), version)

    for marks, code in ((record.unsaved, UNSAVED_MARK), (record.mismatched, MISMATCHED_MARK)):
        marked = [_stem(e.path) for e in kept if any(same_path(e.path, m) for m in marks)]
        if marked:
            return _refused(Refusal(code, tuple(marked)), version)

    updates = {_key(p.path): p for p in update_plan.parts}
    structural = tuple(getattr(update_plan, "structural", ()) or ())
    changes: Dict[str, str] = {}
    for e in kept:
        stem = _stem(e.path)
        update = updates.get(_key(e.path))
        if update is None:
            changes[stem] = CHANGE_NEW_PART       # its rows now differ from one another: they need parts of their own
        elif update.changed:
            # classify keeps a part Update cannot carry (it needs a new part) as changed, with a sentence opening with its
            # stem in update_plan.structural; any other changed part is a change of values.
            changes[stem] = CHANGE_NEW_PART if any(s.startswith(stem + " (") for s in structural) else CHANGE_VALUES
    for a in added:
        changes.setdefault(_stem(a.part), CHANGE_NEW_PART)
    if changes:
        code = NEW_REVISION if getattr(update_plan, "needs_new_revision", False) else CHANGES_ON_UPDATE
        return _refused(Refusal(code, tuple(changes), changes), version)

    box = record.gearbox
    work = getattr(box, "user_work", None) if box is not None else None
    features = list(getattr(work, "features", ()) or ()) if work is not None else []
    parts: List[PrintPart] = []
    for e in kept:
        served_rows = [r for r in rows if r in e.gears]
        update = updates.get(_key(e.path))
        parts.append(print_part(
            e.path, e.spec, variables=e.variables, made=tuple(getattr(update, "made", ()) or ()), rows=served_rows,
            count=sum(_copies(spec, r) for r in served_rows),
            user_features=tuple(dict.fromkeys(f.name for f in features if same_path(f.path, e.path)))))
    pressed = time.time() if now is None else float(now)
    base = output_folder or getattr(assessment, "folder", "") or os.path.dirname(record.workbook or "")
    folder = press_folder(base, pressed, exists)
    name = getattr(spec.box, "name", "") or (box.name if box is not None else "") or _stem(record.workbook or "")
    return PrintPlan(None, tuple(parts), folder, tuple(version), name, pressed)


# -- the file read back as text (§3.1.4, M2; F2-INTERFACES.md §2.4) -------------------------------------------------------

SI_PREFIX_MM = {None: 1000.0, "MILLI": 1.0, "CENTI": 10.0, "DECI": 100.0, "MICRO": 0.001, "KILO": 1.0e6}
CONVERSION_MM = {"INCH": 25.4, "FOOT": 304.8}


@dataclass(frozen=True)
class StepReading:
    """What :func:`read_step` read in a file (package B's addition, so the job keeps the facts beside the verdict):
    ``reason`` None when it passes, else the first of :data:`REASONS`; ``schema`` the FILE_SCHEMA's name as written
    ("" none), ``ap`` which accepted AP it is ("" none); ``unit`` the length unit as read ("MILLI.METRE", "INCH"; ""
    unreadable); ``extent`` "checked" or "skipped: <why>" (:data:`EXTENT_SKIPPED`), "" when the file failed before it."""

    reason: Optional[str]
    schema: str = ""
    ap: str = ""
    unit: str = ""
    extent: str = ""


def _statements(text: str) -> Tuple[List[str], bool]:
    """A Part 21 file's statements in order, split at each semicolon outside a quoted string ('' a quote inside one)
    and outside a comment, line breaks dropped; and whether the file ended inside a statement. As
    ``probe/f2_probes.py``'s ``statements``."""
    out: List[str] = []
    cur: List[str] = []
    i, n, quoted = 0, len(text), False
    while i < n:
        c = text[i]
        if quoted:
            cur.append(c)
            if c == "'":
                if i + 1 < n and text[i + 1] == "'":
                    cur.append("'")
                    i += 1
                else:
                    quoted = False
        elif c == "'":
            quoted = True
            cur.append(c)
        elif c == "/" and text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = n if end < 0 else end + 2
            continue
        elif c == ";":
            out.append("".join(cur).replace("\r", "").replace("\n", "").strip())
            cur = []
        else:
            cur.append(c)
        i += 1
    tail = "".join(cur).replace("\r", "").replace("\n", "").strip()
    if tail:
        out.append(tail)
    return out, bool(tail)


def _sections(text: str) -> Tuple[bool, List[str], Dict[int, str]]:
    """``(frame, header, data)``: whether the file opens ISO-10303-21 and closes END-ISO-10303-21 whole; the HEADER's
    statements; the DATA's instances as {number: body}."""
    parts, cut = _statements(text)
    frame = bool(parts) and not cut and parts[0] == "ISO-10303-21" and parts[-1] == "END-ISO-10303-21"
    header: List[str] = []
    data: Dict[int, str] = {}
    where = None
    for s in parts:
        if s in ("HEADER", "DATA"):
            where = s
        elif s == "ENDSEC":
            where = None
        elif where == "HEADER":
            header.append(s)
        elif where == "DATA":
            m = re.match(r"#(\d+)\s*=\s*(.*)$", s, re.S)
            if m:
                data[int(m.group(1))] = m.group(2).strip()
    return frame, header, data


def _unquoted(body: str) -> str:
    return re.sub(r"'(?:[^']|'')*'", "''", body)


def _names(body: str) -> List[str]:
    """An instance's entity names: one for NAME(...), each top-level one of a complex instance ( A() B(...) ); never a
    name written inside a quoted string."""
    body = _unquoted(body).strip()
    if not body.startswith("("):
        m = re.match(r"([A-Z_][A-Z0-9_]*)\s*\(", body, re.I)
        return [m.group(1).upper()] if m else []
    names: List[str] = []
    depth, i = 0, 0
    while i < len(body):
        c = body[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif depth == 1:
            m = re.match(r"([A-Z_][A-Z0-9_]*)\s*\(", body[i:], re.I)
            if m:
                names.append(m.group(1).upper())
                i += len(m.group(1))
                continue
        i += 1
    return names


def _count(data: Mapping[int, str], name: str) -> int:
    return sum(1 for body in data.values() if name in _names(body))


def _schema(header: Sequence[str]) -> str:
    for s in header:
        if s.upper().startswith("FILE_SCHEMA"):
            m = re.search(r"'((?:[^']|'')*)'", s)
            if m:
                return re.split(r"[\s{]", m.group(1).strip(), maxsplit=1)[0].upper()
    return ""


def schema_ap(name: str) -> str:
    """Which accepted AP a FILE_SCHEMA name is, by its prefix (:data:`STEP_SCHEMAS`): "AP203", "AP214", "AP242" or ""."""
    for ap, prefixes in STEP_SCHEMAS:
        if name and any(name.upper().startswith(p) for p in prefixes):
            return ap
    return ""


def _unit_of(data: Mapping[int, str], number: int) -> Tuple[str, Optional[float]]:
    """One LENGTH_UNIT instance as ``(label, millimetres per unit)``; ("", None) when it does not read."""
    body = data.get(number, "")
    names = _names(body)
    if "LENGTH_UNIT" not in names:
        return "", None
    if "SI_UNIT" in names:
        m = re.search(r"SI_UNIT\s*\(\s*(\$|\.(\w+)\.)\s*,\s*\.(\w+)\.\s*\)", _unquoted(body), re.I)
        if m and m.group(3).upper() == "METRE":
            prefix = m.group(2).upper() if m.group(2) else None
            if prefix in SI_PREFIX_MM:
                return (prefix + "." if prefix else "") + "METRE", SI_PREFIX_MM[prefix]
        return "", None
    if "CONVERSION_BASED_UNIT" in names:
        m = re.search(r"CONVERSION_BASED_UNIT\s*\(\s*'((?:[^']|'')*)'", body, re.I)
        label = m.group(1).strip().upper() if m else ""
        return (label, CONVERSION_MM[label]) if label in CONVERSION_MM else ("", None)
    return "", None


def _length_unit(data: Mapping[int, str]) -> Tuple[str, Optional[float]]:
    """The length unit the file's geometry is in: the LENGTH_UNIT each GLOBAL_UNIT_ASSIGNED_CONTEXT assigns
    (F2-0-REVIEW S3: an inch file also holds the SI unit its conversion refers to, so not every LENGTH_UNIT is the
    file's unit), every context assigning the same one. A file with no such context falls back to every LENGTH_UNIT
    instance, which must then agree. ("", None) when it cannot be read."""
    assigned: List[int] = []
    for body in data.values():
        if "GLOBAL_UNIT_ASSIGNED_CONTEXT" not in _names(body):
            continue
        plain = _unquoted(body)
        at = plain.upper().find("GLOBAL_UNIT_ASSIGNED_CONTEXT")
        m = re.match(r"GLOBAL_UNIT_ASSIGNED_CONTEXT\s*\(\s*\(([^()]*)\)", plain[at:], re.I)
        if not m:
            return "", None
        lengths = [int(r) for r in re.findall(r"#(\d+)", m.group(1)) if "LENGTH_UNIT" in _names(data.get(int(r), ""))]
        if len(lengths) != 1:
            return "", None
        assigned.append(lengths[0])
    numbers = assigned or [k for k, body in data.items() if "LENGTH_UNIT" in _names(body)]
    found = {_unit_of(data, k) for k in numbers}
    if len(found) != 1:
        return "", None
    label, mm = next(iter(found))
    return (label, mm) if mm else ("", None)


def _vertices(data: Mapping[int, str]) -> List[Tuple[float, ...]]:
    """Every VERTEX_POINT's CARTESIAN_POINT, in the file's unit."""
    out: List[Tuple[float, ...]] = []
    for body in data.values():
        if _names(body) != ["VERTEX_POINT"]:
            continue
        m = re.search(r"#(\d+)\s*\)\s*$", body)
        point = data.get(int(m.group(1))) if m else None
        p = re.match(r"CARTESIAN_POINT\s*\(\s*'(?:[^']|'')*'\s*,\s*\(([^)]*)\)\s*\)$", point or "", re.I)
        if p:
            try:
                out.append(tuple(float(v) for v in p.group(1).split(",")))
            except ValueError:
                continue
    return out


def extent_skipped(part: PrintPart) -> str:
    """Why the size check is not made on ``part`` (one of :data:`EXTENT_SKIPPED`), or "" when it is: a bevel gear, a
    sleeve, a dog, a hub, a herringbone (not measured yet) or a ring (teeth inside) by its kind; a part holding the
    user's features; and every part while ``findings.EXTENT_MEASURED`` is not True."""
    kind = str(part.spec.kind or "").strip().lower()
    if kind == "bevel":
        return "bevel"
    if kind in ("sleeve", "dog", "hub", "herringbone"):
        return kind
    if str(part.spec.teeth_side or "").strip().lower() == "internal":
        return "ring"
    if part.user_features:
        return "user features"
    if not getattr(findings, "EXTENT_MEASURED", None):
        return "not measured"
    return ""


def _extent_holds(data: Mapping[int, str], mm: float, part: PrintPart) -> bool:
    """The largest radius from Z among the vertices against the part's d_a / 2, and their axial extent against its face
    width, each to :data:`EXTENT_TOL` mm (the build's own frame: the axis on Z, the face from the Front plane). False when
    the part's spec does not derive or the file has no vertex."""
    _kind, derived = _derived(part.spec)
    points = _vertices(data)
    if derived is None or not points or any(len(p) != 3 for p in points):
        return False
    radius = max(math.hypot(x, y) for x, y, _ in points) * mm
    zs = [z for _, _, z in points]
    extent = (max(zs) - min(zs)) * mm
    return abs(radius - derived.da / 2.0) <= EXTENT_TOL and abs(extent - derived.face_width) <= EXTENT_TOL


def read_step(text: str, part: PrintPart) -> StepReading:
    """§3.1.4's check of a file's text for ``part``, with what it read: the first failing reason of :data:`REASONS` (or
    None), and the schema, the unit and the extent as facts."""
    frame, header, data = _sections(text or "")
    schema = _schema(header)
    ap = schema_ap(schema)
    unit, mm = _length_unit(data)

    def reading(reason: Optional[str], extent: str = "") -> StepReading:
        return StepReading(reason, schema, ap, unit, extent)

    if not frame:
        return reading(FRAME)
    if not ap:
        return reading(SCHEMA)
    if _count(data, "MANIFOLD_SOLID_BREP") != 1 or not _count(data, "CLOSED_SHELL"):
        return reading(SOLIDS)
    if _count(data, "OPEN_SHELL"):
        return reading(OPEN_SHELL)
    if _count(data, "SHELL_BASED_SURFACE_MODEL"):
        return reading(SURFACE_MODEL)
    if not mm:
        return reading(UNIT)
    why = extent_skipped(part)
    if why:
        return reading(None, f"skipped: {why}")
    if not _extent_holds(data, mm, part):
        return reading(EXTENT, "checked")
    return reading(None, "checked")


def check_step(text: str, part: PrintPart) -> Optional[str]:
    """None when the STEP file's text passes §3.1.4's check for ``part``, else the first failing reason of
    :data:`REASONS` (in that order). EXTENT is never a refusal for a part with user features or a kind in
    :data:`EXTENT_SKIPPED`, nor while ``findings.EXTENT_MEASURED`` is not True; it is then a fact (:func:`read_step`)."""
    return read_step(text, part).reason


def write_list(result: PrintResult, text: str) -> str:
    """Write ``text`` (C's ``ui_text.print_list_text``) as :data:`LIST_NAME` in the press's folder (``result.folder``),
    UTF-8, never over an existing file (opened "x": a file there already raises FileExistsError and nothing is written);
    the path written. "" and nothing written when the result names no folder."""
    if not result.folder:
        return ""
    path = os.path.join(result.folder, LIST_NAME)
    with open(path, "x", encoding="utf-8", newline="") as handle:
        handle.write(text)
    return path
