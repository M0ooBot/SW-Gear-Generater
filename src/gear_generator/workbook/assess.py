"""One read of a workbook, worked through once, and what may be built from it (docs/PLAN-WORKBOOK.md §3–§4).

:func:`assess` is the one pipeline the window, the design boards and SolidWorks
builds share: the read's own diagnostics, each gear through the strip's checks
(:func:`build.plan_parts`), and the gearbox checks (:func:`checks.check`) on
what is left, with any chosen fixes made first. Its answers are the gates:

- :func:`build_refusal` — may **Build parts** go ahead? Not while anything is
  an error, nor without an output folder; rows a later phase builds do not
  hold it back, their parts are left out.
- :meth:`Assessment.lay_out_refusal` — may the layout part and the assembly
  (phase W4) be built? Everything Build parts asks, and also: a read that is
  not provisional, no fix waiting for Export, a gearbox that was checked at
  all, no row a later phase builds, and every gear placed and planned, so an
  assembly is never made without one.

**Provisional.** After Export has written cells into a workbook with formulas,
the file holds Excel's old values for every formula until Excel recalculates
and saves it. A read of it then is provisional: its checks may report errors
that are not real, so it offers no fixes (a fix worked from an old value lands
wrong once Excel recalculates), and nothing may be built or exported from it.
Only the window knows this state (it wrote the file); it passes it in.

Each gate answers with the sentence that refuses, or ``""``. Nothing here
touches Tk, COM or the file system.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import List, Optional, Sequence, Tuple

from .. import store
from ..gears.base import Diagnostic
from ..spec import PROCESS_MACHINED, PROCESS_PRINTED, GearSpec
from . import build, checks, fixes, geometry, motion
from .build import PartsPlan
from .checks import Report
from .fixes import Fix
from .model import GearboxSpec

PROVISIONAL = ("The workbook's formulas still hold Excel's old values, since Export wrote cells they may depend "
               "on: open and save it in Excel so they recalculate.")
NO_FOLDER = "Choose an output folder (the Box sheet's, or the strip's Output) before building."


def _plural(count: int, one: str, many: str = "") -> str:
    return f"{count} {one if count == 1 else (many or one + 's')}"


def _more(items: Sequence) -> str:
    return f" ({len(items) - 1} more under Checks)" if len(items) > 1 else ""


TURNED_KINDS = (geometry.BEVEL, geometry.CROSSED)     # the mesh kinds Assessment.turned_refusal asks about (W6)


@dataclass
class Assessment:
    read: GearboxSpec                       # the workbook as read
    read_diagnostics: List[Diagnostic]      # what the read itself said, each at its cell
    spec: GearboxSpec                       # the read with the chosen fixes made
    chosen: Tuple[Fix, ...] = ()
    parts: PartsPlan = field(default_factory=PartsPlan)
    report: Report = field(default_factory=Report)
    diagnostics: List[Diagnostic] = field(default_factory=list)    # all of it, as Checks lists it
    folder: str = ""                        # where the parts go: the Box sheet's, or the strip's
    provisional: bool = False               # formulas hold Excel's old values (see the module's docstring)

    @property
    def errors(self) -> List[Diagnostic]:
        return [d for d in self.diagnostics if d.is_error]

    def build_refusal(self) -> str:
        """Why Build parts may not go ahead, or ``""``. A fix waiting for Export, and a provisional read, are
        the window's footer to say first (``ui_text.workbook_footer``)."""
        return build_refusal(self.parts, self.diagnostics, self.folder)

    def lay_out_refusal(self) -> str:
        """Why the layout part and the static assembly (W4) may not be built from this workbook, or ``""``.

        The one gate for W4. It reads everything the workbook says — whether the
        read is provisional, the fixes chosen but not exported, the read, every
        gear's own checks, the gearbox checks, the rows a later phase builds —
        and the output folder being set.

        **The caller must still check** what only it knows, before this: that
        the file is there and read whole (not gone, half-saved or unreadable),
        that no build is running, that the output folder exists on disk, and
        that it passed ``provisional=True`` to :func:`assess` while Excel has
        yet to recalculate an Export (the window's ``recalc``). The window
        asks those, for every button, in ``ui_text.workbook_footer``.
        """
        if self.provisional:
            return PROVISIONAL
        if self.chosen:
            n = len(self.chosen)
            return (f"{_plural(n, 'fix', 'fixes')} chosen: Export writes {'it' if n == 1 else 'them'} into the "
                    "workbook first, so the workbook and the assembly agree.")
        refusal = self.build_refusal()
        if refusal:
            return refusal
        if self.report.unchecked:
            return f"The gearbox cannot be laid out yet, since it is not checked: {self.report.unchecked}"
        refused = self.parts.refused
        if refused:
            return f"The layout and assembly are not built: {refused[0].message}{_more(refused)}"
        placed = {p.row or p.gear for p in self.report.layout.placed.values()}     # W7: a planet's copies, its row
        planned = {g for job in self.parts.jobs for g in job.gear_ids}
        missing = [g.id for g in self.spec.gears if g.id not in placed or g.id not in planned]
        if missing:
            # Every way a gear is left out is an error or a refused row above; this says it if one ever is not.
            one = len(missing) == 1
            return (f"{', '.join(missing)} {'is' if one else 'are'} not placed, so the assembly would be built "
                    f"without {'it' if one else 'them'}; see Checks.")
        return self.turned_refusal()

    def turned_refusal(self) -> str:
        """W6 (D16): the sentence refusing to build a gearbox with a turned mesh the probes have not shown a gear
        mate's sense for (``motion.turned_refusal``), or ``""`` when nothing is refused. The one test of "is there a
        turned mesh, and is it refused" — ``lay_out_refusal`` ends with it, and the footer and the window ask it
        rather than keeping copies.

        A gearbox is asked only when ``report.meshes`` holds a turned mesh — a BEVEL or CROSSED one — so a
        gearbox of parallel meshes only is W5's and never asked. The guard names what is turned rather than
        "anything not PARALLEL", so a mesh kind a later phase adds is not silently counted as turned: W7 and W8
        extend it deliberately if they need to. A gearbox that is not checked (a carrier row, W7) has no meshes
        laid out and so gives ``""`` here; ``lay_out_refusal`` says why it waits before it asks this."""
        if any(laid.kind in TURNED_KINDS for laid in self.report.meshes.values()):
            return motion.turned_refusal(self.report)
        return ""


def build_refusal(parts: PartsPlan, diagnostics: Sequence[Diagnostic], folder: str) -> str:
    """Why Build parts may not go ahead — any error, nothing to build, no output folder — or ``""``.

    Whether the folder exists on disk is the caller's to check: nothing here
    touches the file system."""
    errors = [d for d in diagnostics if d.is_error]
    if errors:
        return f"Fix the workbook before building: {errors[0].message}{_more(errors)}"
    if not parts.jobs:
        return "Nothing in this workbook can be built yet: " + (parts.later[0][1] if parts.later
                                                                else "it has no gears.")
    if not folder:
        return NO_FOLDER
    return ""


def blank_process(record: Optional[store.LinkRecord]) -> str:
    """What a blank Process on the Box sheet means for the gearbox ``record`` describes (PLAN-PRINTED §1.3, D11 ruled
    (B) by the coordinating session, 2026-11-18): *as built*.

    Machined when the record lists current parts (:meth:`store.LinkRecord.current_parts`) and none was built
    printed (no part entry's ``spec`` reads printed; a part built before F1, or built machined after it, holds no
    ``process``). Printed otherwise: no record, a record with no parts, or any part built printed. The rule goes by
    the parts, never by the record's schema number, which any F1 write moves to 11.

    This body is D11's one switch: under (A) it returns :data:`PROCESS_PRINTED` always. The window passes no record
    when the one beside the workbook is another workbook's (package C).
    """
    parts = record.current_parts() if record is not None else []
    if not parts:
        return PROCESS_PRINTED
    if any(GearSpec.from_dict(dict(p.spec or {})).is_printed() for p in parts):
        return PROCESS_PRINTED
    return PROCESS_MACHINED


def assess(read: GearboxSpec, read_diagnostics: Sequence[Diagnostic], folder: str, part_template: str = "",
           chosen: Sequence[Fix] = (), provisional: bool = False,
           blank_process: str = PROCESS_PRINTED, record: Optional[store.LinkRecord] = None) -> Assessment:
    """The read worked through: the chosen fixes made, every gear planned, the gearbox checked.

    A gear with an error of its own — from the read or the strip's checks — is
    left out of the parts and the gearbox checks (the error says where), and
    then out of the layout too (:attr:`geometry.Layout.left_out`). A
    ``provisional`` read offers no fixes (``report.fixes`` is empty).

    F1 (PLAN-PRINTED §1.3): a Box whose Process is blank (``""``, the user's blank as read) takes ``blank_process``,
    in the assessment's ``read`` and ``spec`` both, so no Assessment holds a blank Process. The window passes
    :func:`blank_process` of the record beside the workbook; a gearbox built in code says machined and never meets it.

    F3 (PLAN-PRINTED §4.1.1; F3-INTERFACES §14, S3, the rule's tenth caller): ``record``, the record beside the workbook
    (this workbook's: the window passes the one it reads :func:`blank_process` from, None for another workbook's), reads
    each row whose gear's part is on record as built (``build.built_globals``), so the window's checks (the printed rim,
    the bore against the root) speak of the hole that part was cut with; its job is planned as typed (F3-REVIEW M2). None, every row as
    a row with no part on record, as before.
    """
    if not str(read.box.process).strip():
        read = replace(read, box=replace(read.box, process=blank_process))
    spec = read
    for fix in chosen:
        spec = fixes.apply(spec, fix)
    read_diagnostics = list(read_diagnostics)
    skip_rows = build.rows_with_errors(read_diagnostics)
    parts = build.plan_parts(spec, folder, part_template, skip_rows=skip_rows,
                             built=build.built_globals(record) if record is not None else None)
    bad_rows = skip_rows | build.rows_with_errors(parts.diagnostics)
    report = checks.check(spec, {g.id for g in spec.gears if g.row in bad_rows})
    if provisional:
        report.fixes = {}
    return Assessment(read=read, read_diagnostics=read_diagnostics, spec=spec, chosen=tuple(chosen), parts=parts,
                      report=report, diagnostics=read_diagnostics + parts.diagnostics + report.diagnostics,
                      folder=folder, provisional=provisional)
