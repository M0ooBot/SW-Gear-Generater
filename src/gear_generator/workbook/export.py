"""Writing back to the workbook: the fixes chosen in the app, and the Results sheet (PLAN-WORKBOOK §2, §5; W3).

Only on Export, only the cells a fix names, and never over a formula
(:func:`xlsx.write_cells` refuses those and they come back to be listed). A fix
may name a column the sheet does not have — columns are optional, so a
workbook without Profile shift is ordinary — and Export then writes that
column's header at the end of row 1 first. A cell formatted as a percentage
gets a fraction (0.97 for 97), as Excel holds one.

The Results sheet is the app's own and is replaced whole each time; the reader
never reads it. Whatever else is in the workbook is left exactly as it was.
"""

from __future__ import annotations

import hashlib
import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from ..gears import bevel, crossed
from . import checks, geometry, schema, xlsx
from .checks import Report
from .fixes import Fix
from .model import GearboxSpec, from_book as model_from_book
from .xlsx import NewSheet, make_ref

SHEET_DEFS = {"Shafts": schema.SHAFTS, "Gears": schema.GEARS, "Meshes": schema.MESHES}
RESULTS_RATIO = "Overall ratio (input speed ÷ output speed)"
RESULTS_BOX = "Box size, over the gears' outside diameters (X, Y) and faces (Z)"
RESULTS_LEFT_OUT = "Not in the box size"


@dataclass
class Exported:
    path: str = ""
    written: List[str] = field(default_factory=list)
    refused: List[Tuple[str, str]] = field(default_factory=list)    # (cell, why) — formulas, mostly
    added_headers: List[str] = field(default_factory=list)
    digest: str = ""                       # the file as written, so the live link knows its own write
    has_formulas: bool = False             # Excel must recalculate and save before the values can be trusted
    results: bool = False                  # the Results sheet was written (not when a cell was refused)
    results_error: str = ""                # the cells were written, but writing Results then failed: why
    # Refused because the cell holds a formula: (cell, item, column header, the value the fix wants there)
    formulas: List[Tuple[str, str, str, str]] = field(default_factory=list)


def results_sheet(spec: GearboxSpec, report: Report, when: Optional[str] = None) -> NewSheet:
    """The Results sheet: speeds, turning, torque per shaft; ratio, centres and contact ratio per mesh; what the
    box was worked out as, its overall ratio, and the room its gears take (:func:`geometry.extent`)."""
    when = when or time.strftime("%Y-%m-%d %H:%M")
    motion = report.motion
    # W6 (D12): every shaft in the Z family keeps W3's column; else each cell says what it is seen from.
    all_z = all(motion.seen_from.get(s.id, "+Z") == "+Z" for s in spec.shafts)
    # W7 (W7-PLAN §2.12): a column "On its carrier (rpm)" for mounted shafts, and a held member's torque "held".
    carried = bool(motion.relative)
    rows: List[List] = [["Shaft", "Speed (rpm)", "Turns, seen from +Z" if all_z else "Turns", "Torque (N·m)"]
                        + (["On its carrier (rpm)"] if carried else [])]
    for shaft in spec.shafts:
        speed = motion.speeds.get(shaft.id)
        torque = motion.torques.get(shaft.id)
        turns = motion.turns(shaft.id)
        if turns and not all_z and turns != "still":
            turns = f"{turns}, seen from {motion.seen_from.get(shaft.id, '+Z')}"
        if torque is None and shaft.id in motion.held:
            torque_cell = f"{round(motion.held[shaft.id], 6)} held"
        else:
            torque_cell = round(torque, 6) if torque is not None else "—"
        row = [shaft.id, round(float(speed), 6) if speed is not None else "—", turns or "—", torque_cell]
        if carried:
            relative = motion.relative.get(shaft.id)
            row.append(round(float(relative), 6) if relative is not None else "")
        rows.append(row)
    rows.append([])
    turned = [m for m in report.meshes.values() if m.kind != geometry.PARALLEL and not m.problem]
    rows.append(["Mesh", "Ratio", "Centres needed (mm)", "Centres placed (mm)", "Off by (mm)", "Contact ratio"]
                + (["Shaft angle (°)", "Cone distance (mm)", "Apex distance (mm)"] if turned else []))
    gears = {g.id: g for g in spec.gears}
    mesh_rows: Dict[Tuple[str, str], List] = {}
    for (a, b), (needed, placed) in report.centres.items():
        ratio = float(gears[b].teeth) / float(gears[a].teeth)
        mesh_rows[(a, b)] = [f"{a}–{b}", round(ratio, 6), round(needed, 6), round(placed, 6), round(placed - needed, 6),
                             round(report.contact.get((a, b), 0.0), 4)] + (["", "", ""] if turned else [])
    if turned:                                    # W6: every kind of mesh in the Meshes sheet's order
        mesh_rows.update({(m.a, m.b): _turned_row(m, report.layout.placed) for m in turned})
        listed = [(m.a, m.b) for m in spec.meshes if (m.a, m.b) in mesh_rows]
        mesh_rows = {key: mesh_rows[key] for key in listed + [k for k in mesh_rows if k not in listed]}
    rows.extend(mesh_rows.values())
    rows.append([])
    rows.append(["Overall", "Value"])
    rows.append(["Worked out as", report.worked_out_as or "—"])
    ratio, between, why = checks.overall_ratio(spec, report)
    rows.append([RESULTS_RATIO, round(ratio, 6), between] if ratio is not None else [RESULTS_RATIO, "—", why])
    rows.append([])
    rows.append([RESULTS_BOX, "Size (mm)", "From (mm)", "To (mm)"])
    box = geometry.extent(report.layout.placed)
    for axis, span in zip("XYZ", box or ((None, None),) * 3):
        lo, hi = span
        rows.append([axis] + ([round(hi - lo, 6), round(lo, 6), round(hi, 6)] if lo is not None else ["—"] * 3))
    left_out = box_left_out(spec, report)
    if left_out:
        rows.append([RESULTS_LEFT_OUT, left_out])
    note = schema.RESULTS_NOTE.format(when=when)
    if any(m.kind == geometry.CROSSED for m in turned):
        note += (" The efficiency typed for a crossed helical mesh is the workbook's: a crossed pair slides along its "
                 "teeth, and its real efficiency is far lower.")
    return NewSheet(schema.RESULTS, rows, header=False, note=note)


def _turned_row(laid: geometry.MeshGeometry, placed: Dict[str, geometry.Placed]) -> List:
    """A BEVEL or CROSSED mesh's Results row (W6-PLAN §2.4, review S5): the ratio and shaft angle; a bevel pair's
    cone distance, the distance between its two cone tips (0 when right) and the contact ratio of its back-cone
    pair, its centres blank; a crossed pair's centres needed and placed along the common perpendicular, off by, and
    its normal contact ratio."""
    a, b = placed[laid.a], placed[laid.b]
    ratio = round(b.teeth / a.teeth, 6)
    angle = round(laid.shaft_angle, 6)
    if laid.kind == geometry.BEVEL:
        cone = bevel.cone_distance(a.module, a.teeth, b.teeth, laid.shaft_angle)
        return [f"{laid.a}–{laid.b}", ratio, "", "", "", round(bevel.contact_ratio(a.derived), 4), angle,
                round(cone, 6), round(laid.placed, 6)]
    contact = crossed.normal_contact_ratio(a.module, a.teeth, b.teeth, a.derived.helix_angle_deg,
                                           b.derived.helix_angle_deg, a.derived.normal_pressure_angle_deg)
    return [f"{laid.a}–{laid.b}", ratio, round(laid.needed, 6), round(laid.placed, 6),
            round(laid.placed - laid.needed, 6), round(contact, 4), angle, "", ""]


def box_left_out(spec: GearboxSpec, report: Report) -> str:
    """What the box size does not count, each gear with why: ``G5 (a bevel gear, phase W6), G6 (a sleeve, phase
    W8)``; a sliding gear is counted at its At only. ``""`` when it counts every gear where it will be."""
    pieces = [f"{gear} ({why})" for gear, why in report.layout.left_out.items()]
    pieces += [f"{g.id} (slides: counted at its At only, phase W8)" for g in spec.gears
               if g.slides.strip() and g.id in report.layout.placed]
    return ", ".join(pieces)


def _value(column: Optional[schema.Column], text: str, percent: bool):
    """A model value as a cell value: numbers as numbers (a fraction in a percentage cell), text as text."""
    if column is not None and column.numeric and text:
        try:
            value = float(text)
        except ValueError:
            return text
        if percent:
            return value / 100.0
        return int(value) if value == int(value) and abs(value) < 1e15 else value
    return text


def export(path: str, spec: GearboxSpec, chosen: Sequence[Fix], report: Optional[Report],
           out_path: str = "", expected_digest: str = "") -> Exported:
    """Write the chosen fixes' cells and the Results sheet into ``path`` (or a copy at ``out_path``).

    Each edit names a shaft or gear, and its row is found in the file as it is
    now, so rows inserted or sorted since the fix was chosen do not misdirect
    it. ``expected_digest`` is the file as the window last read it: a save in
    Excel since then (inside the one-second poll) is refused rather than
    written over. If any cell is refused (a formula), the Results sheet is not
    written: the fix is then only partly in the workbook, and Results would
    describe a gearbox the file does not hold. A formula cell refused is listed
    in ``formulas`` with the value the fix wants, since after Excel recalculates
    it may land there by itself.

    The cells and the Results sheet are two writes, one after the other. If the
    second fails, the first stands: ``results_error`` says why, and ``digest`` is
    still the file as it now is, so the live link knows the write was the app's.
    """
    with open(path, "rb") as handle:
        data = handle.read()
    if expected_digest and hashlib.sha256(data).hexdigest() != expected_digest:
        raise xlsx.XlsxError("The workbook changed since it was last read, so nothing was written; it is read "
                             "again now. Choose the fix again if it still applies.")
    book = xlsx.read_bytes(data, path)
    current, _ = model_from_book(book)
    rows = {("Shafts", s.id): s.row for s in current.shafts}
    rows.update({("Gears", g.id): g.row for g in current.gears})
    changes: Dict[str, Dict[str, object]] = {}
    targets: Dict[str, Tuple[str, str, str]] = {}     # cell -> (item, column header, value), for a refusal
    out = Exported(path=out_path or path)
    for fix in chosen:
        for edit in fix.edits:
            sheet = book.sheet(edit.sheet)
            sheet_def = SHEET_DEFS[edit.sheet]
            column = sheet_def.column(edit.key)
            row = rows.get((edit.sheet, edit.item))
            if sheet is None or row is None:
                out.refused.append((f"{edit.sheet} {edit.item}", f"{edit.item} is no longer on the {edit.sheet} "
                                                                 "sheet"))
                continue
            headers = {col: cell.text for (r, col), cell in sheet.cells.items() if r == 1 and cell.text}
            found, _, _ = schema.match_headers(sheet_def, headers)
            col = found.get(edit.key)
            cells = changes.setdefault(sheet.name, {})
            if col is None:
                # The column is optional and this workbook has none: add its header after the last one.
                col = max([sheet.max_col()] + [xlsx.split_ref(r)[1] for r in cells]) + 1
                cells[make_ref(1, col)] = column.title
                out.added_headers.append(f"{sheet.name}!{make_ref(1, col)} {column.title}")
                sheet.cells[(1, col)] = xlsx.Cell(make_ref(1, col), 1, col, column.title)
            existing = sheet.cell(row, col)
            cells[make_ref(row, col)] = _value(column, edit.value, bool(existing and existing.percent))
            targets[f"{sheet.name}!{make_ref(row, col)}"] = (edit.item, column.header, edit.value)
    written = xlsx.write_cells(path, changes, out_path=out_path)
    out.written, out.refused = written.written, out.refused + written.refused
    out.formulas = [(cell,) + targets[cell] for cell, why in written.refused if "formula" in why and cell in targets]
    target = out_path or path
    if report is not None and not out.refused:
        try:
            xlsx.write_cells(target, {}, replace_sheets=[results_sheet(spec, report)])
            out.results = True
        except (xlsx.XlsxError, OSError) as exc:
            out.results_error = str(exc)
    with open(target, "rb") as handle:
        out.digest = hashlib.sha256(handle.read()).hexdigest()
    out.has_formulas = any(cell.formula for name, sheet in book.sheets.items() if name != schema.RESULTS
                           for cell in sheet.cells.values())
    return out
