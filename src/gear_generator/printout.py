"""Print files (PLAN-PRINTED §3.1.3, §3.1.4): which parts a press exports to STEP for the slicer, where, and whether a
file written is fit to print. Pure planning: structure and codes, never a sentence a user reads (must-fix M4).

**F2-0's interface stub. Package B owns this file and fills** :func:`form_print`, :func:`workbook_print`,
:func:`check_step` and :func:`write_list` (``docs/notes-printed/F2-INTERFACES.md`` §2). The names, the dataclasses and the
codes below are the interface: B returns them, package C's ``ui_text`` words them (one sentence per code, given once in the
interface note), and ``swbuild.print_parts`` (B's) runs the job a plan describes.

Until B fills them, both planners refuse every press with :data:`GATE_COPY`, which is what the filled planners answer
while ``findings.SAVE_AS_COPY`` is None (as it is until the probe's runs are reviewed): no folder is chosen and nothing
is written.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Mapping, Optional, Tuple

from .gears.span import NONE as NO_SPAN, SpanReading
from .spec import GearSpec

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
PLANNING_CODES = (GATE, GATE_COPY, UNSAVED_MARK, MISMATCHED_MARK, CHANGES_ON_UPDATE, NO_PART, WORKBOOK_ERROR,
                  FOREIGN_RECORD, NO_RECORD, NOT_A_PART)
# The job (swbuild.print_parts), per part, after every part's reads and before any file is written; then the export.
MODIFIED = "MODIFIED"              # the part's own GetSaveFlag is on
GLOBALS_DIFFER = "GLOBALS_DIFFER"  # a live global is not what its record says (spaces aside, swbuild._squash)
FEATURE_IN_ERROR = "FEATURE_IN_ERROR"  # a feature's GetErrorCode2 is non-zero and not a warning
COMPONENT_ONLY = "COMPONENT_ONLY"  # open only inside an assembly, and neither measured route reaches it
SOLIDWORKS_REFUSED = "SOLIDWORKS_REFUSED"  # SolidWorks would not open, reach or export a part (its codes or swcom's)
FILE_CHECK = "FILE_CHECK"          # a file written failed check_step
JOB_CODES = (MODIFIED, GLOBALS_DIFFER, FEATURE_IN_ERROR, COMPONENT_ONLY, SOLIDWORKS_REFUSED, FILE_CHECK)
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
EXTENT_SKIPPED = ("bevel", "ring", "sleeve", "dog", "hub", "user features", "not measured")


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
    left in it by name (the record's inventory; () on the form), and its spec as recorded."""

    path: str
    stem: str
    rows: Tuple[str, ...] = ()
    count: int = 1
    process: str = ""
    span: SpanReading = NO_SPAN
    user_features: Tuple[str, ...] = ()
    spec: GearSpec = field(default_factory=GearSpec)


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
    """What the job did (``swbuild.print_parts``). ``written``: (part path, file); ``failed``: (file, reason code of
    :data:`REASONS`); ``facts``: see :data:`FACT_SCHEMA`; ``active_restored``: the document active at the start is active
    again (True when it was closed meanwhile by the user, or none was); ``flags_turned_on``: documents (paths, a new
    one's title) whose save flag the job turned on; ``warnings`` (F2-0's addition): (part path, feature names) of
    features whose GetErrorCode2 is a warning, which do not refuse (the re-check's should-fix)."""

    written: Tuple[Tuple[str, str], ...] = ()
    folder: str = ""
    refusal: Optional[Refusal] = None
    failed: Tuple[Tuple[str, str], ...] = ()
    facts: Mapping[str, str] = field(default_factory=dict)
    active_restored: bool = True
    flags_turned_on: Tuple[str, ...] = ()
    warnings: Tuple[Tuple[str, Tuple[str, ...]], ...] = ()


def _stub_gate(version: SolidWorksVersion) -> PrintPlan:
    return PrintPlan(Refusal(GATE_COPY), revision=tuple(version or ()))


def form_print(sidecar: Optional["Sidecar"], part_path: str, output_folder: str, version: SolidWorksVersion, *,
               now: Optional[float] = None, exists: Callable[[str], bool] = os.path.exists) -> PrintPlan:
    """The form's press: the part active in SolidWorks (``part_path``, "" when none) with its ``.gear.json`` read
    (``sidecar``, None when there is none or it does not read), into ``output_folder``'s print folder. ``now`` (seconds
    since the epoch, the press's time) and ``exists`` are for tests; None is the clock.

    F2-0's stub: refuses with GATE_COPY. Package B fills it."""
    return _stub_gate(version)


def workbook_print(record: Optional["LinkRecord"], assessment: Optional["Assessment"],
                   update_plan: Optional["UpdatePlan"], output_folder: str, version: SolidWorksVersion, *,
                   now: Optional[float] = None, exists: Callable[[str], bool] = os.path.exists) -> PrintPlan:
    """The Workbook window's press: every part of the record's current revision (``LinkRecord.current_parts``), each once,
    from the window's planning read (``assessment``, ``update_plan``), into ``output_folder`` (the Box's, else the
    strip's) print folder.

    F2-0's stub: refuses with GATE_COPY. Package B fills it."""
    return _stub_gate(version)


def check_step(text: str, part: PrintPart) -> Optional[str]:
    """None when the STEP file's text passes §3.1.4's check for ``part``, else the first failing reason of
    :data:`REASONS` (in that order). EXTENT is never a refusal for a part with user features or a kind in
    :data:`EXTENT_SKIPPED`; it is then a fact.

    F2-0's stub: answers None (it is called by nothing until package B fills it)."""
    return None


def write_list(result: PrintResult, text: str) -> str:
    """Write ``text`` (C's ``ui_text.print_list_text``) as ``LIST_NAME`` in the press's folder (``result.folder``), UTF-8,
    never over an existing file; the path written.

    F2-0's stub: writes nothing and answers "". Package B fills it."""
    return ""
