"""Package B of PLAN-PRINTED's stage F1 (§2.8): the workbook's Process and Nozzle, its checks for printed pairs, the
gearbox build and records at their new schemas, Update and Build again… with Process, and what a gearbox built before
F1 meets when it is first opened (D11, ruled (B) by the coordinating session on 2026-11-18).

The rule (§2.7, test_printed_rule.py) holds that nothing machined moves; these hold what printed does. Each read of a
committed workbook is left unmarked here, so a blank Process is read as the user left it."""

import json
import re
from dataclasses import replace
from pathlib import Path

import pytest

from gear_generator import store, ui_text
from gear_generator.gears import pair as pairs
from gear_generator.gears.equations import split_equation
from gear_generator.spec import GearSpec
from gear_generator.workbook import assess, checks, gearbox, model, schema, update, xlsx
from gear_generator.workbook.model import Box, Gear, GearboxSpec, Mesh, Shaft
from test_workbook_model import edit, read, reducer, write
from test_workbook_planetary import planetary_4to1
from test_workbook_turned import bevel_reducer
from test_workbook_in_place_round_trip import Desk, users_work
from workbook_fixtures import range_box

FIXTURES = Path(__file__).resolve().parent / "fixtures"
COMMITTED = (FIXTURES / "excel-windows" / "Reducer_12to1.xlsx", FIXTURES / "excel-windows" / "Arc_Move.xlsx",
             FIXTURES / "excel-windows" / "Risky_Placements.xlsx", FIXTURES / "excel" / "Reducer_12to1.xlsx",
             FIXTURES / "libreoffice" / "Reducer_12to1.xlsx")
BOOK = "C:\\B\\W.xlsx"
OUT = "C:\\Out\\"


def box_of(spec, **changes):
    return replace(spec, box=replace(spec.box, **changes))


def assessed(spec, record=None, diagnostics=()):
    """The read worked through as the window does it: a blank Process resolved by the record beside it (D11)."""
    return assess.assess(replace(spec, source_path=BOOK), list(diagnostics), OUT,
                         blank_process=assess.blank_process(record))


def errors(a):
    return [d.message for d in a.diagnostics if d.is_error]


# -- the Box sheet: Process and Nozzle read, checked and written (§1.3) -------------------------------------------

@pytest.mark.parametrize("typed, kept", [("Printed", "printed"), ("PRINTED", "printed"), ("printed", "printed"),
                                         ("Machined", "machined"), (" machined ", "machined"), ("", "")])
def test_the_boxs_process_is_read_in_any_case_and_kept_lower_case_and_a_blank_is_kept_blank(tmp_path, typed, kept):
    """Ruling 7: any case is read, and the word is kept lower case. A blank is the user's blank, "" as read, never
    resolved here; assess resolves it (D11). Where it was read is Box!B9, the row after Efficiency."""
    path = write(tmp_path, reducer())
    edit(path, "Box", {"B9": typed})
    spec, diagnostics = read(path)
    assert diagnostics == [] and spec.box.process == kept and spec.box.process_cell == "Box!B9"


def test_a_process_word_that_does_not_read_is_said_once_at_its_cell_and_no_gear_is_told_it(tmp_path):
    """Ruling 3: one bad Box cell is said once, at the Box, and not again at every gear row: the gears' specs take
    only a word that checked, and a word that did not is the spec's blank."""
    path = write(tmp_path, reducer())
    edit(path, "Box", {"B9": "wood"})
    spec, diagnostics = read(path)
    assert [d.message for d in diagnostics] == ["Box!B9: Process is Printed or Machined (got 'wood')."]
    assert spec.box.process == "wood"                       # kept as typed, so the window shows what is in the cell
    a = assess.assess(replace(spec, source_path=BOOK), diagnostics, OUT)
    assert [m for m in errors(a) if "Process" in m or "process" in m] == [
        "Box!B9: Process is Printed or Machined (got 'wood')."]
    assert all(j.spec.process == "" and not j.spec.is_printed() for j in a.parts.jobs)
    assert a.build_refusal().startswith("Fix the workbook before building: Box!B9: Process is Printed or Machined")


@pytest.mark.parametrize("typed, said", [
    ("x", "Box!B10: Nozzle must be a number (got 'x')."),
    ("0", "Box!B10: Nozzle must be more than zero (got '0')."),
    ("-0.4", "Box!B10: Nozzle must be more than zero (got '-0.4')."),
])
def test_a_nozzle_that_does_not_read_is_said_once_at_its_cell_and_no_gear_is_told_it(tmp_path, typed, said):
    path = write(tmp_path, reducer())
    edit(path, "Box", {"B9": "Printed", "B10": typed})
    spec, diagnostics = read(path)
    assert [d.message for d in diagnostics] == [said]
    a = assess.assess(replace(spec, source_path=BOOK), diagnostics, OUT)
    assert [m for m in errors(a) if "Nozzle" in m] == [said]
    assert all(j.spec.is_printed() and j.spec.nozzle == "" for j in a.parts.jobs)


def test_a_nozzle_that_reads_goes_into_every_gear_as_typed(tmp_path):
    path = write(tmp_path, reducer())
    edit(path, "Box", {"B9": "Printed", "B10": 0.6})
    spec, diagnostics = read(path)
    assert diagnostics == [] and (spec.box.process, spec.box.nozzle) == ("printed", "0.6")
    a = assess.assess(replace(spec, source_path=BOOK), [], OUT)
    assert {(j.spec.process, j.spec.nozzle, j.spec.nozzle_mm()) for j in a.parts.jobs} == {("printed", "0.6", 0.6)}
    assert {j.derived.nozzle for j in a.parts.jobs} == {0.6}


@pytest.mark.parametrize("process, nozzle, word, text", [
    ("Printed", "0.4", "printed", "0.4"), ("printed", "", "printed", ""), ("MACHINED", "0.4", "machined", "0.4"),
    ("", "", "", ""), ("wood", "0.4", "", "0.4"), ("printed", "x", "printed", ""), ("printed", "0", "printed", ""),
    ("printed", "nan", "printed", "")])
def test_the_gears_take_only_a_checked_process_word_and_nozzle_from_the_box(process, nozzle, word, text):
    """Ruling 3, in model.Gear.spec_values: the word lower case, or the spec's blank; the nozzle as typed, or blank
    (0.4 mm) when it does not read as a number above zero."""
    values = reducer().gears[0].spec_values(Box(name="R", process=process, nozzle=nozzle))
    assert (values["process"], values["nozzle"]) == (word, text)
    assert (model.checked_process(Box(process=process)), model.checked_nozzle(Box(nozzle=nozzle))) == (word, text)


def test_a_box_with_no_process_row_reads_blank_with_no_cell():
    """A workbook written before F1 has no Process or Nozzle row (Units is in B9): both read "", and process_cell says
    there is no row, for the Workbook panel's "(add a row labelled Process)" (F1-INTERFACES §5)."""
    path = FIXTURES / "printed" / "RangeBox_W9.xlsx"
    spec, diagnostics = read(path)
    assert diagnostics == []
    assert (spec.box.process, spec.box.nozzle, spec.box.process_cell) == ("", "", "")
    box = xlsx.read(str(path)).sheet("Box")
    labels = [box.cell(row, 1).text for row in range(2, box.max_row() + 1) if box.cell(row, 1) is not None]
    assert "Process" not in labels and labels[7] == "Units"


def test_new_workbook_writes_process_printed_and_a_0_4_nozzle_and_reads_back_clean(tmp_path):
    """§1.3, D2: New workbook… is printed. The rows it writes, read back."""
    rows = {row[0]: row[1:] for row in model.to_sheets(model.template("NewBox"))[0].rows[1:]}
    assert rows["Process"] == ["printed", "Printed or Machined; blank: Printed for a new gearbox, as built for one "
                                          "already built"]
    assert rows["Nozzle (mm)"] == [0.4, "the printer's line width; blank: 0.4"]
    spec, diagnostics = read(write(tmp_path, model.template("NewBox")))
    assert diagnostics == [] and (spec.box.process, spec.box.nozzle, spec.box.process_cell) == ("printed", "0.4",
                                                                                                "Box!B9")
    assert spec.box == model.template("NewBox").box


@pytest.mark.parametrize("word", ["printed", "machined"])
def test_to_sheets_and_from_book_round_trip_both_words(tmp_path, word):
    spec = box_of(reducer(), process=word, nozzle="0.6")
    back, diagnostics = read(write(tmp_path, spec))
    assert diagnostics == [] and back.without_rows() == spec


def test_the_backlash_columns_blank_says_what_a_blank_is_printed_and_machined():
    """The schema as data (§2.8, B's): the Backlash column's blank words name both defaults."""
    blank = schema.GEARS.column("backlash").blank
    assert blank == "printed: 0.3, or 0.3 × module below module 1; machined: 0.3 × module"


# -- the five committed workbooks, read as the user left them (the review's should-fix 2) --------------------------

@pytest.mark.parametrize("path", COMMITTED, ids=lambda p: f"{p.parent.name}/{p.name}")
def test_a_committed_workbook_reads_a_blank_process_and_plans_printed_with_no_record(path):
    """None of the five has a Process row. Read unmarked, Process is "" with no cell; with no record beside it, a
    blank is printed (D2), so every part plans printed and its name ends _P."""
    spec, diagnostics = read(path)
    assert (spec.box.process, spec.box.process_cell) == ("", "")
    a = assessed(spec, None, diagnostics)
    assert a.read.box.process == a.spec.box.process == "printed"
    assert a.parts.jobs and all(j.spec.is_printed() for j in a.parts.jobs)
    assert all(j.stem.endswith("_P") or j.spec.name for j in a.parts.jobs)          # a typed Part name is kept
    assert all(j.derived is not None for j in a.parts.jobs)


@pytest.mark.parametrize("path", COMMITTED, ids=lambda p: f"{p.parent.name}/{p.name}")
@pytest.mark.parametrize("word", ["printed", "machined"])
def test_no_assessment_holds_a_blank_process_in_read_or_spec(path, word):
    """§2.8 (held here, as the plan gives it to B's new file): whatever the record says, assess leaves no blank in read
    or in spec, so nothing built later from a.read.box falls to GearSpec's machined default unseen."""
    spec, diagnostics = read(path)
    a = assess.assess(replace(spec, source_path=BOOK), diagnostics, OUT, blank_process=word)
    assert a.read.box.process == a.spec.box.process == word
    spaces = assess.assess(replace(box_of(spec, process="  "), source_path=BOOK), diagnostics, OUT, blank_process=word)
    assert spaces.read.box.process == spaces.spec.box.process == word


# -- the checks for printed pairs at a Meshes row (§2.2's radial clearance) -----------------------------------------

def outside_pair(module, teeth=(20, 40), shifts=("", ""), process="printed"):
    """Two spur gears on frame shafts at their working centre distance."""
    centre = pairs.describe(module, teeth[0], teeth[1], 20.0, 0.0, shift_1=float(shifts[0] or 0),
                            shift_2=float(shifts[1] or 0))[0]
    return GearboxSpec(
        box=Box(name="Pair", pressure_angle="20", efficiency="98", process=process),
        shafts=(Shaft("S1", "frame", "0", "0", "0", "Z+", "input", "", "1000", "1", row=2),
                Shaft("S2", "frame", f"{centre:.6f}", "0", "0", "Z+", "output", row=3)),
        gears=(Gear("G1", "S1", "0", "spur", "external", str(teeth[0]), str(module), "", "5", "",
                    profile_shift=shifts[0], row=2),
               Gear("G2", "S2", "0", "spur", "external", str(teeth[1]), str(module), "", "5", "",
                    profile_shift=shifts[1], row=3)),
        meshes=(Mesh("G1", "G2", row=2),))


def ring_pair(module, teeth=(20, 60), process="printed"):
    centre = module * (teeth[1] - teeth[0]) / 2.0
    return GearboxSpec(
        box=Box(name="RingPair", pressure_angle="20", efficiency="98", process=process),
        shafts=(Shaft("P", "frame", f"{centre:.6f}", "0", "0", "Z+", "input", "", "1000", "1", row=2),
                Shaft("R", "frame", "0", "0", "0", "Z+", "output", row=3)),
        gears=(Gear("Pin", "P", "0", "spur", "external", str(teeth[0]), str(module), "", "5", "", row=2),
               Gear("Ring", "R", "0", "spur", "internal", str(teeth[1]), str(module), "", "5", "", row=3)),
        meshes=(Mesh("Pin", "Ring", row=2),))


def bevel_pair(module, process="printed"):
    """W6's fixture A with its bevel stage at the module given (its cone tips meet at S1's point whatever the
    module)."""
    spec = bevel_reducer()
    gears = tuple(replace(g, module=str(module), face_width="8") if g.kind == "bevel" else g for g in spec.gears)
    meshes = tuple(replace(m, row=row) for row, m in enumerate(spec.meshes, start=2))
    return replace(spec, box=replace(spec.box, process=process), gears=gears, meshes=meshes)


def crossed_pair(module, process="printed"):
    """A crossed helical pair at 45° each, 20 and 40 teeth, on S1 (Z+) and S2 (X+) the pitch radii apart."""
    centre = module * (20 + 40) / 2.0 / 0.7071067811865476
    helix = dict(helix_angle="45", hand="right")
    return GearboxSpec(
        box=Box(name="Crossed", pressure_angle="20", efficiency="98", process=process),
        shafts=(Shaft("S1", "frame", "0", "0", "0", "Z+", "input", "", "1000", "1", row=2),
                Shaft("S2", "frame", "0", f"{centre:.6f}", "8", "X+", "output", row=3)),
        gears=(Gear("G1", "S1", "8", "helical", "external", "20", str(module), "", "6", "", row=2, **helix),
               Gear("G2", "S2", "0", "helical", "external", "40", str(module), "", "6", "", row=3, **helix)),
        meshes=(Mesh("G1", "G2", row=2),))


def clearance_said(spec):
    a = assess.assess(replace(spec, source_path=BOOK), [], OUT)
    assert [m for m in errors(a) if "Meshes" in m] == [], errors(a)
    return [d.message for d in a.report.diagnostics if "tip clearance" in d.message]


@pytest.mark.parametrize("module, said", [
    (0.7, ["Meshes row 2: G1 and G2: Printed, the tip clearance is 0.28 mm, under the 0.3 mm two printed surfaces take; "
           "use a larger module."]),
    (0.75, []),          # 0.2999999999999998 by the maths: passes within the rounding tolerance
    (1.0, []), (1.5, []),
])
def test_a_printed_outside_pair_under_0_3_mm_of_tip_clearance_is_said_at_its_meshes_row(module, said):
    assert clearance_said(outside_pair(module)) == said
    assert clearance_said(outside_pair(module, process="machined")) == []


def test_a_shifted_printed_pair_names_less_profile_shift_and_gives_the_clearance_the_shifts_leave():
    spec = outside_pair(1.5, teeth=(15, 30), shifts=("0.5", "0.4"))
    clearance = pairs.tip_clearance(1.5, 15, 30, 20.0, 0.0, 0.5, 0.4)
    assert clearance < 0.3
    assert clearance_said(spec) == [
        f"Meshes row 2: G1 and G2: Printed, the tip clearance is {checks._n(clearance)} mm, under the 0.3 mm two printed "
        "surfaces take; use a larger module or less profile shift."]
    assert clearance_said(box_of(spec, process="machined")) == []


@pytest.mark.parametrize("module, said", [(0.5, True), (0.7, True), (0.75, False), (1.25, False), (2.0, False)])
def test_a_printed_pinion_in_a_ring_is_checked_by_the_ring_pairs_clearance(module, said):
    """A ring pair's clearance (package A's pair.ring_tip_clearance): unshifted, 0.4 × module up to module 1.25."""
    got = clearance_said(ring_pair(module))
    assert bool(got) == said
    if said:
        c = pairs.ring_tip_clearance(module, 20, 60)
        assert got == [f"Meshes row 2: Pin and Ring: Printed, the tip clearance is {checks._n(c)} mm, under the 0.3 mm "
                       "two printed surfaces take; use a larger module."]
    assert clearance_said(ring_pair(module, process="machined")) == []


@pytest.mark.parametrize("module, said", [(1.5, ["0.282"]), (1.6, []), (3.0, [])])
def test_a_printed_bevel_pair_under_module_1_6_is_said_by_gleasons_clearance(module, said):
    """Gleason's clearance is 0.188 × module, under 0.3 mm below module 1.596 (§2.2)."""
    got = clearance_said(bevel_pair(module))
    assert [re.search(r"is ([\d.]+) mm", m).group(1) for m in got] == said
    assert all(m.startswith("Meshes row 2: G1 and G2: Printed, the tip clearance is") and m.endswith(
        "use a larger module.") for m in got)
    assert clearance_said(bevel_pair(module, process="machined")) == []


def test_a_printed_bevel_pairs_meshes_row_says_what_the_form_says_of_the_same_two_gears():
    """F1 review, S4: the workbook takes a bevel pair's clearance from pair.bevel_tip_clearance, the figure the form's
    mesh_warnings judges by, so the Meshes row and the strip say one sentence of the same pair."""
    spec = bevel_pair(1.5)
    a = assess.assess(replace(spec, source_path=BOOK), [], OUT)
    placed = a.report.layout.placed
    form = pairs.mesh_warnings(placed["G1"].derived, placed["G2"].derived)
    assert clearance_said(spec) == [f"Meshes row 2: G1 and G2: {form[0]}"]
    assert pairs.bevel_tip_clearance(placed["G1"].derived, placed["G2"].derived) == pytest.approx(0.188 * 1.5)


def test_a_printed_crossed_pair_is_checked_as_an_outside_pair():
    """Crossed helical gears are unshifted, so each tip stands the depth less two addenda from the other's root."""
    assert clearance_said(crossed_pair(0.5)) == [
        "Meshes row 2: G1 and G2: Printed, the tip clearance is 0.2 mm, under the 0.3 mm two printed surfaces take; "
        "use a larger module."]
    assert clearance_said(crossed_pair(2.0)) == [] and clearance_said(crossed_pair(0.5, process="machined")) == []


_PROVISIONAL = "17 MPa (provisional: type your own in the Box's Allowable stress)"
_PLANET = ("N once, with an allowance of 0.7 because a planet's teeth are loaded in both directions as the gearbox runs; "
           "the load is shared by 3 planets, one taking 1.25 of an even share.")
_REMEDY = (" Use a larger module, a wider face, less torque, or your own tested allowable. An estimate for teeth printed "
           "flat, with the whole load on one tooth's tip: not a running rating; heat, wear and creep are not worked out.")
STRENGTH_SAID = {        # F4 (PLAN-PRINTED §5.5, the review's S7): exactly B's sentences, in order, with their figures
    "RangeBox": [
        "Meshes row 2: Sun and Planet: Printed, these teeth take about 230 N at the pitch circle in L, 13.6 times the "
        f"17 N Planet's teeth are rated to take at {_PROVISIONAL}: 24 {_PLANET}{_REMEDY}",
        "Meshes row 3: Planet and Ring: Printed, these teeth take about 221 N at the pitch circle in L, 13.1 times the "
        f"17 N Planet's teeth are rated to take at {_PROVISIONAL}: 24 {_PLANET}{_REMEDY}"],
    "planetary_4to1": [
        "Meshes row 2: Sun and Planet: Printed, these teeth take about 93 N at the pitch circle, 6.4 times the 14 N "
        f"Planet's teeth are rated to take at {_PROVISIONAL}: 21 {_PLANET}{_REMEDY}",
        "Meshes row 3: Planet and Ring: Printed, these teeth take about 89 N at the pitch circle, 6.2 times the 14 N "
        f"Planet's teeth are rated to take at {_PROVISIONAL}: 21 {_PLANET}{_REMEDY}"],
    "Risky_Placements": [
        f"Meshes!A{row}: {a} and {b}: Printed, these teeth take about {force} N at the pitch circle, {times} times the "
        f"{held} N {a}'s teeth are rated to take once at {_PROVISIONAL}.{_REMEDY}"
        for row, a, b, force, times, held in ((2, "G1", "G2", 336, "6.6", 51), (3, "G3", "G4", 453, "7.2", 63),
                                              (4, "G5", "G6", 724, "14.3", 51))],
}


@pytest.mark.parametrize("make", [range_box, planetary_4to1, "Risky_Placements"], ids=["RangeBox", "planetary_4to1",
                                                                                     "Risky_Placements"])
def test_printed_gearboxes_carry_the_gearbox_warnings_they_carry_machined(make):
    """§2.3 and §2.8: no pair interference warning is built, printed or machined, and W7's planetary sentence and
    report.undercut stay as they are. What printed adds is the gears' own (§2.2, package A's), never the gearbox's,
    but for F4's strength warnings (§5.5): a printed gearbox says exactly what its machined twin says, then B's
    sentences for it, in order, each with its figures."""
    if make == "Risky_Placements":
        spec, _ = read(FIXTURES / "excel-windows" / "Risky_Placements.xlsx")
    else:
        spec = make()
    machined = assess.assess(replace(box_of(spec, process="machined"), source_path=BOOK), [], OUT)
    printed = assess.assess(replace(box_of(spec, process="printed"), source_path=BOOK), [], OUT)
    name = make if isinstance(make, str) else {range_box: "RangeBox", planetary_4to1: "planetary_4to1"}[make]
    assert [d.message for d in printed.report.diagnostics] == ([d.message for d in machined.report.diagnostics]
                                                               + STRENGTH_SAID[name])
    assert printed.report.undercut == machined.report.undercut
    assert printed.report.stages == machined.report.stages


# -- D11 (B): blank_process with each kind of record ---------------------------------------------------------------

def w9_snapshot():
    """RangeBox as W9's own code (f3c4873, the commit printed was cut from) built it on the fake, with W9a's user work
    on it read onto its record by a quiet press: the record's text, each part's .gear.json, the files on disk, and
    what W9 told the user then (its footer, Update's parts and Build again…'s reuse)."""
    return json.loads((FIXTURES / "printed" / "RangeBox_W9_record.json").read_text(encoding="utf-8"))


class W9Disk:
    """The files of that snapshot, as the window would find them."""

    def __init__(self, snap):
        self.files = set(snap["files"])
        self.sidecars = dict(snap["sidecars"])

    @staticmethod
    def key(path):
        return path.replace("/", "\\").lower()

    def exists(self, path):
        return self.key(path) in self.files

    def read_sidecar(self, path):
        text = self.sidecars.get(self.key(path))
        return store.from_json(text) if text is not None and self.exists(path) else None


def printed_desk():
    """RangeBox built printed on the fake by this branch."""
    d = Desk()
    d.build(box_of(range_box(), process="printed"))
    return d


def machined_desk():
    d = Desk()
    d.build(range_box())
    return d


@pytest.mark.parametrize("make, word", [
    (lambda: store.link_record_from_json(w9_snapshot()["record"]), "machined"),       # W9 wrote it (schema 10)
    (lambda: machined_desk().record, "machined"),                                       # built machined after F1 (11)
    (lambda: printed_desk().record, "printed"),                                         # built printed
    (lambda: store.LinkRecord(workbook=BOOK), "printed"),                               # no parts
    (lambda: None, "printed"),                                                          # no record
], ids=["W9", "machined after F1", "printed", "no parts", "none"])
def test_a_blank_process_is_as_built_for_each_kind_of_record(make, word):
    """D11 (B): machined while every current part was built machined, before F1 or after it; printed with no record,
    no parts, or a part built printed. Written forward to 11 by any F1 write, the answer is the same."""
    record = make()
    assert assess.blank_process(record) == word
    if record is not None:
        again = store.link_record_from_json(store.link_record_to_json(record))
        assert again.schema_version == store.LINK_SCHEMA_VERSION == 12 and assess.blank_process(again) == word


# -- the gearbox build and its records at the new schemas (§1.2) ---------------------------------------------------

def _stem(path):
    return Path(path.replace("\\", "/")).stem


def test_a_printed_gearbox_builds_p_parts_recorded_with_their_process_at_link_11_and_sidecar_3():
    d = printed_desk()
    rec = d.record
    assert rec.schema_version == 12
    assert [_stem(p.path) for p in rec.parts] == [
        "Gear_m1.25_N29_P", "Gear_m1.25_N13_P", "Ring_m1.25_N55_P", "Dog_m1.25_N17_P", "Sleeve_m1.25_N17_P"]
    assert all(p.spec["process"] == "printed" and p.spec["nozzle"] == "" for p in rec.parts)
    for part in rec.parts:
        car = d.disk.read_sidecar(store.sidecar_path(part.path))
        assert car.schema_version == store.PRINTED_SCHEMA == 3 and car.record.spec == part.spec
        assert car.record.derived["nozzle"] == 0.4
        assert dict(part.variables)["Backlash"] == 'IIF ( "Module" <= 1 , 0.3 * "Module" , 0.3 )'


def test_a_machined_gearbox_built_after_f1_records_no_process_and_its_sidecars_stay_at_1_or_2():
    """The record's link schema is 11 whatever the parts (§1.2); a machined part's spec and .gear.json are W9's, at
    sidecar 1 or 2 (the bytes are test_printed_rule's pins)."""
    d = machined_desk()
    assert d.record.schema_version == 12
    for part in d.record.parts:
        assert "process" not in part.spec and "nozzle" not in part.spec
        assert d.disk.read_sidecar(store.sidecar_path(part.path)).schema_version in (1, 2)


# -- a gearbox built before F1, opened after it (D11 (B)), on the record W9 wrote -----------------------------------

def _w9_opened(process=""):
    snap = w9_snapshot()
    record = store.link_record_from_json(snap["record"])
    disk = W9Disk(snap)
    spec, diagnostics = read(FIXTURES / "printed" / "RangeBox_W9.xlsx")
    assert diagnostics == []
    spec = box_of(spec, process=process)
    a = assess.assess(replace(spec, source_path=snap["workbook"]), [], OUT, blank_process=assess.blank_process(record))
    up = update.classify(record, a, exists=disk.exists, read_sidecar=disk.read_sidecar)
    again = gearbox.plan_gearbox(a, record, exists=disk.exists, read_sidecar=disk.read_sidecar)
    return snap, record, disk, a, up, again


def _footer(a, record, again, up):
    f = ui_text.workbook_footer(a, record=record, plan=again, update=up, digest=record.digest, folder=OUT)
    return [re.sub(r"As read at \d\d:\d\d", "As read at HH:MM", f.text), f.ok]


def _today_is(monkeypatch, stamp):
    """The clock fixed to the day of the record stamp ``stamp`` (``store.now()``'s form): ``ui_text.read_time`` says *14:02*
    for a stamp of today and *14:02 on 2026-11-18* for another day, so a footer kept from that day reads the same on any
    day the test runs. Only ``time.localtime()`` with no argument, the one clock read_time asks, is fixed."""
    import calendar
    import time
    fixed = calendar.timegm(time.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ"))
    real = time.localtime
    monkeypatch.setattr(time, "localtime", lambda *when: real(*when) if when else real(fixed))


def test_a_gearbox_w9_built_opens_machined_with_nothing_changed_and_nothing_written(monkeypatch):
    """What a user's gearbox meets the first time it is opened after F1, under (B): its workbook has no Process row,
    its record (schema 10) lists parts built machined, so the blank reads Machined, as built. Update finds nothing to
    do, Build again… reuses every part, W9d's columns find nothing changed, the footer says what W9 said, and the
    record and the files are left exactly as W9 wrote them (no write is planned; the window writes only on a press)."""
    snap, record, disk, a, up, again = _w9_opened()
    _today_is(monkeypatch, record.gearbox.user_work.read_at)    # the day W9's footer was kept (it says no date)
    assert json.loads(snap["record"])["link_schema_version"] == 10 and a.read.box.process_cell == ""
    assert a.read.box.process == a.spec.box.process == "machined" and errors(a) == []
    assert all(not j.spec.is_printed() and not j.stem.endswith("_P") for j in a.parts.jobs)
    assert (up.refusal, up.structural, up.missing, up.replaced, up.moved_shafts) == ("", (), (), (), ())
    assert [p.changed for p in up.parts] == snap["update"][1] == [False] * 5 and up.record_matches
    assert [again.refusal, [j.stem for j in again.build], len(again.reuse)] == snap["build_again"]
    jobs = {g: j for j in gearbox.plan_gearbox(a, None, exists=lambda p: False, read_sidecar=lambda p: None).build
            for g in j.gear_ids}
    assert [update._changed_columns(p.spec, jobs[p.gears[0]].spec.to_dict()) for p in record.current_parts()] == \
        [[]] * 5
    w9_footer = [re.sub(r"As read at \d\d:\d\d", "As read at HH:MM", snap["footer"][0]), snap["footer"][1]]
    assert _footer(a, record, again, up) == w9_footer
    # Nothing written: the record as read is W9's text, byte for byte but the number a write would move, after every
    # plan above; and the .gear.json files as W9 wrote them.
    assert store.link_record_to_json(record).replace('"link_schema_version": 12', '"link_schema_version": 10') == \
        snap["record"]
    assert disk.sidecars == snap["sidecars"]


def test_a_gearbox_w9_built_said_machined_in_so_many_words_opens_the_same():
    _, record, _, a, up, again = _w9_opened("machined")
    _, _, _, blank_a, blank_up, blank_again = _w9_opened("")
    assert [p.changed for p in up.parts] == [False] * 5 and len(again.reuse) == 5
    assert _footer(a, record, again, up) == _footer(blank_a, record, blank_again, blank_up)


def test_typing_printed_on_a_gearbox_w9_built_changes_each_parts_backlash_alone_in_place():
    """§1.3: with Printed typed, every part reads changed on Update in its Backlash alone (the blank cell's
    equation, 0.3 * "Module" to the printed IIF), and none needs a new part, a new revision or a put."""
    _, record, _, a, up, again = _w9_opened("printed")
    assert a.read.box.process == "printed" and errors(a) == []
    assert (up.refusal, up.structural, up.missing, up.replaced, up.needs_new_revision) == ("", (), (), (), False)
    assert [p.changed for p in up.parts] == [True] * 5
    for entry, part in zip(record.current_parts(), up.parts):
        was = {str(n): str(v) for n, v in entry.variables}
        now = {v.name: v.expression_for(entry.trig) for v in part.variables}
        assert [n for n in now if was.get(n, "").replace(" ", "") != now[n].replace(" ", "")] == ["Backlash"]
        assert was["Backlash"] == '0.3 * "Module"'
        assert now["Backlash"] == 'IIF ( "Module" <= 1 , 0.3 * "Module" , 0.3 )'
        assert part.spec.is_printed() and store.same_path(part.path, entry.path)   # the file keeps its name (D10)


def test_build_again_on_a_gearbox_w9_built_after_printed_makes_each_part_new_because_its_process_changed():
    """§6: a part is reused only when its globals are as recorded, so every gear is made new, now _P; W9d names
    the reason for each body it carries as *its Process changed* (update._SPEC_COLUMNS)."""
    _, record, disk, a, _, again = _w9_opened("printed")
    assert again.refusal == "" and [j.stem for j in again.build] == [
        "Gear_m1.25_N29_P", "Gear_m1.25_N13_P", "Ring_m1.25_N55_P", "Dog_m1.25_N17_P", "Sleeve_m1.25_N17_P"]
    assert list(again.reuse) == []
    carry = update.carry_for(record, again, update.old_assembly(record, again), read_sidecar=disk.read_sidecar)
    gears = {b.old: b.why_new for b in carry.bodies if b.old not in ("layout", "Carrier carrier")}
    assert gears == {g: "its Process changed" for g in
                     ("Sun", "Planet copy 1", "Planet copy 2", "Planet copy 3", "Ring", "HighDog", "LowDog",
                      "RangeSlv")}


def test_the_changed_columns_read_a_missing_process_as_machined_and_the_word_in_any_case():
    machined, printed = GearSpec().to_dict(), GearSpec(process="printed").to_dict()
    assert "process" not in machined
    assert update._changed_columns(machined, printed) == ["Process"]
    assert update._changed_columns(printed, machined) == ["Process"]
    assert update._changed_columns(machined, dict(machined, process="Machined")) == []
    assert update._changed_columns(printed, dict(printed, process="PRINTED", nozzle="0.6")) == []
    assert update._changed_columns(machined, dict(printed, teeth="26")) == ["Teeth", "Process"]


# -- Update on the fake, end to end, with the user's work (§2.8, *A gearbox built before F1*) -----------------------

@pytest.fixture
def desk():
    """RangeBox built machined on the fake (W9's record byte for byte but its schema number, by test_printed_rule's
    pins), W9a's user work on it read onto the record by a quiet press."""
    d = Desk()
    d.build(range_box())
    users_work(d)
    return d


def test_printed_typed_on_a_built_gearbox_is_one_update_writing_each_backlash_and_keeping_the_users_work(desk):
    before = desk.record
    assert assess.blank_process(before) == "machined"
    names = sorted(_stem(p.path) for p in before.parts)
    printed = box_of(range_box(), process="printed")
    press = desk.press(printed)
    text, ok = press.before
    assert ok and text.startswith("Update SolidWorks will change the values in Gear_m1.25_N29 (Sun), "
                                  "Gear_m1.25_N13 (Planet), Ring_m1.25_N55 (Ring), Dog_m1.25_N17 (HighDog, LowDog) "
                                  "and Sleeve_m1.25_N17 (RangeSlv).")
    assert press.refused is None and press.result.ok, (press.result.failures, press.result.skipped)
    assert [(r.document, r.changed) for r in press.result.parts] == [
        (n, ["Backlash"]) for n in ("Gear_m1.25_N29.SLDPRT", "Gear_m1.25_N13.SLDPRT", "Ring_m1.25_N55.SLDPRT",
                                    "Dog_m1.25_N17.SLDPRT", "Sleeve_m1.25_N17.SLDPRT")]
    assert not press.result.inserted and not press.result.bands_added
    # The user's work as it was: the lock, the components and the features.
    asm = desk.record.gearbox.assembly
    assert any(m.name == "Lock3" for m in desk.sw.memory_mates[asm.replace("/", "\\").lower()])
    assert {c.name for c in desk.record.gearbox.user_work.components} == {"Sprocket-1", "Housing-1"}
    assert desk.sw.frames.get("Sprocket-1") is not None
    # The record: link 11, each part printed under its old file name, its .gear.json at sidecar 3.
    rec = desk.record
    assert rec.schema_version == 12 and sorted(_stem(p.path) for p in rec.parts) == names
    for part in rec.parts:
        assert part.spec["process"] == "printed"
        assert dict(part.variables)["Backlash"] == 'IIF ( "Module" <= 1 , 0.3 * "Module" , 0.3 )'
        assert desk.disk.read_sidecar(store.sidecar_path(part.path)).schema_version == 3
    assert assess.blank_process(rec) == "printed"                # the blank now reads as built: printed
    again = desk.press(printed)
    assert again.result.ok and again.after.startswith(ui_text.ALREADY_MATCHES[:30]), again.after
    blank = desk.press(box_of(range_box(), process=""))
    assert blank.result.ok and blank.after.startswith(ui_text.ALREADY_MATCHES[:30]), blank.after


def test_a_printed_default_the_user_changed_in_solidworks_is_refused_by_k11_in_its_own_words(desk):
    """§6, K11: after the Update, the user types 0.25 for Backlash in Sun's part in SolidWorks; the next press refuses
    before any write, naming the workbook's value in words and the exact IIF SolidWorks must hold."""
    printed = box_of(range_box(), process="printed")
    assert desk.press(printed).result.ok
    assert store.clear_saved(desk.record, mtime=lambda p: 1.0)          # the user saves the Update's parts
    sun = next(p.path for p in desk.record.parts if "Sun" in p.gears)
    key = sun.replace("/", "\\").lower()
    for texts in (desk.sw.memory[key][0], desk.sw.saved[key][0]):
        texts[:] = [t if split_equation(t)[0] != "Backlash" else '"Backlash"= 0.25' for t in texts]
    press = desk.press(printed)
    assert press.refused is not None and press.result is None
    (problem,) = press.refused.problems
    assert problem.sentence == (
        "Backlash in Gear_m1.25_N29 is 0.25 in SolidWorks and 0.3 (from its blank cell, the printed default: 0.3 mm, "
        "or 0.3 × Module below module 1) in the workbook: type 0.25 in Gears row 2, or set it back to the equation "
        "IIF ( \"Module\" <= 1 , 0.3 * \"Module\" , 0.3 ) in SolidWorks, and press Update SolidWorks again.")
