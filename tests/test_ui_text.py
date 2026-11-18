"""The window's derived text, tested without a window."""

import pytest

from gear_generator import ui_text
from gear_generator.gears import KINDS, pair
from gear_generator.gears.base import Diagnostic
from gear_generator.spec import GearSpec, PairSpec, pair_stems

SPUR = KINDS["spur"]


def test_the_gear_panel_reads_out_kind_and_recipe():
    assert ui_text.kind_readout("spur", "A") == "Spur · involute curve"
    assert ui_text.kind_readout("spur", "B") == "Spur · arc flanks"


def test_a_gear_reads_out_in_one_breath():
    assert ui_text.gear_readout(GearSpec()) == "m1.5 · z25 · 20° · PD 37.5 mm"
    assert ui_text.gear_readout(GearSpec(module="1.25", teeth="72", pressure_angle="14.5")) == (
        "m1.25 · z72 · 14.5° · PD 90 mm"
    )


def test_a_half_typed_gear_says_so():
    assert ui_text.gear_readout(GearSpec(teeth="2x")) == "check the fields"


def test_the_derived_line():
    g = SPUR.derive(GearSpec())
    assert ui_text.derived_line(g) == "PD 37.5 · OD 40.5 · RD 33.75 · base 35.238 · p 4.712"


def test_the_derived_rows_say_where_a_value_came_from():
    rows = dict(ui_text.derived_rows(SPUR.derive(GearSpec())))
    assert rows["Pitch diameter"] == "37.5"
    assert rows["Backlash"] == "0.45 · 0.3m"
    typed = dict(ui_text.derived_rows(SPUR.derive(GearSpec(backlash="0.05"))))
    assert typed["Backlash"] == "0.05"


def test_errors_come_before_warnings_and_each_is_said_once():
    lines = ui_text.warning_lines([
        Diagnostic("warning", "Thin rim."),
        Diagnostic("error", "No tooth."),
        Diagnostic("warning", "Thin rim."),
    ])
    assert lines == ["No tooth.", "Thin rim."]


def test_the_pair_readout_grows_as_it_is_filled_in():
    assert ui_text.pair_readout("", "") == "centre distance and ratio"
    assert ui_text.pair_readout("60", "3") == "C 60 mm · i 3"
    chosen = pair.solve(60, 3)[0]
    assert ui_text.pair_readout("60", "3", chosen) == "C 60 mm · i 3 · m1.5 20:60"


def test_a_candidate_row_says_what_is_off_about_it():
    found = pair.solve(60, 3)
    assert ui_text.candidate_row(found[0]) == ("1.5", "20 : 60", "exact", "exact")
    near = next(c for c in found if c.ratio_error > 0 and not c.undercut)
    module, teeth, error, tag = ui_text.candidate_row(near)
    assert error.startswith("i ") and error.endswith(" %") and tag == "near"
    undercut = next(c for c in found if c.undercut and c.exact)
    assert ui_text.candidate_row(undercut)[2] == "undercut"


def test_a_non_standard_module_is_starred():
    odd = next(c for c in pair.solve(62, 3) if not c.standard)
    assert ui_text.candidate_row(odd)[0].endswith(" *")


def test_a_centre_distance_miss_is_signed():
    miss = next(c for c in pair.solve(61, 3) if abs(c.centre_error) > 1e-9)
    assert ui_text.candidate_row(miss)[2].startswith(("C +", "C −"))


def test_the_solve_summary_counts():
    found = pair.solve(60, 3)
    # Two of the exact rows are undercut ones cleared by equal and opposite shifts.
    assert ui_text.solve_summary(found).endswith("· 3 exact · 2 with shift")
    assert "No pair" in ui_text.solve_summary([])


def test_the_solve_summary_names_the_chosen_candidate():
    """With the flyout closed, the strip still says which pair was picked."""
    found = pair.solve(60, 3)
    assert ui_text.solve_summary(found, found[0]) == "69 candidates · 3 exact · 2 with shift · m1.5 20 : 60 chosen"


# -- Derived, in pair mode -----------------------------------------------------


def test_the_derived_panel_reads_out_the_pair():
    centre, ratio, epsilon = pair.describe(1.5, 20, 60, 20.0)
    assert ui_text.pair_derived_readout(centre, ratio, epsilon) == "C 60 mm · i 3 · contact ratio 1.671"


def test_the_pair_rows_above_the_table():
    centre, ratio, epsilon = pair.describe(1.5, 20, 60, 20.0)
    assert ui_text.pair_derived_rows(centre, ratio, epsilon, 20, 60) == [
        ("Centre distance", "60 mm"),
        ("Ratio", "3 · 20 : 60"),
        ("Contact ratio", "1.671"),
    ]


# -- the explainer card --------------------------------------------------------
#
# The worked lines are design/UI-DESIGN.md §2's table: Gear A of the pair the
# docs use throughout — m 1.5, 20 teeth, 20°, bore 10, at C 60 and i 3.

GEAR_A = GearSpec(teeth="20")
GEAR_B = GearSpec(teeth="60")
PAIR = PairSpec(mode="pair", centre_distance="60", ratio="3", gear_a=GEAR_A, gear_b=GEAR_B)
DERIVED_A = SPUR.derive(GEAR_A)
FOLDER = r"D:\Gears"

WORKED = {
    "module": "m 1.5 × z 20 = PD 30 mm · tooth depth 3.375 · circular pitch 4.712",
    "teeth": "z 20 → PD 30 mm · OD 33 mm · no undercut (17 or more)",
    "pressure_angle": "20° → base diameter 28.191 mm · undercut below 17 teeth",
    "face_width": "10 mm = 6.7 × module",
    "bore": "10 mm → rim 8.125 mm to the root circle",
    "backlash": "blank → 0.45 mm (0.3 m) · tooth 1.906 · space 2.806 · play in the mesh 0.9",
    "fillet": "blank → 0.57 mm (0.38 m)",
    "groove": "only a herringbone gear has a centre groove",
    "helix_angle": "only a helical gear has a helix angle",
    "hand": "only a helical gear has a hand",
    "hands": "same → β₁ + β₂ = 90°, gear B the same hand as gear A",
    "profile_shift": "0 → a standard tooth · OD 33 mm · root 26.25 · tooth at pitch 1.906 · undercut below 17 teeth",
    "name": r"Pinion_m1.5_N20.SLDPRT in D:\Gears",
    "centre_distance": "60 mm → z₁ + z₂ = 80 at m 1.5 · 96 at m 1.25 · 120 at m 1",
    "ratio": "3 → 20 : 60",
    "pair_module": "blank → 1 · 1.25 · 1.5 · 2 · 2.5 · 3 · 4 … from Series 1",
    "series": "Series 1 → 18 modules from 1 to 50 (ISO 54)",
    "teeth_range": "17 to 200 → 69 candidates at C 60, i 3 · 3 exact · 2 with shift",
    "assembly_name": r"Pair_m1.5_20T_60T.SLDASM in D:\Gears",
    "teeth_side": "external → teeth point outward, tips at 33 mm",
    "rim": "only a ring has a rim",
    "shaft_angle": "only a bevel gear has a shaft angle",
    "mate_teeth": "only a bevel gear has a mate count",
    "cone_distance": "check the fields",
    "mesh": "external → the gears sit side by side, C = m (z₁ + z₂) / 2",
    "shafts": "parallel → both gears the same helix angle, opposite hands",
    "pair_shaft_angle": "Σ 90°",
    "motion": "fixed → gear 1 fixed, gear 2 mated at the mesh angle; nothing turns",
}


@pytest.mark.parametrize("field", ui_text.EXPLAINER_FIELDS)
def test_every_field_works_its_own_value_out(field):
    name, symbol, what, worked = ui_text.explainer(field, DERIVED_A, pair_stems(PAIR)[0], PAIR, FOLDER)
    assert name and what.endswith(".")
    assert worked == WORKED[field]
    assert (symbol == "") == (field in ("bore", "name", "series", "assembly_name", "teeth_side", "rim", "mesh",
                                        "shafts", "motion", "hand", "hands"))


def test_every_field_on_the_form_has_a_card():
    assert set(ui_text.EXPLAINER_FIELDS) == set(WORKED)
    assert len(ui_text.GEAR_EXPLAINERS) == 16 and len(ui_text.PAIR_EXPLAINERS) == 12


def test_a_typed_backlash_and_fillet_drop_the_word_blank():
    typed = SPUR.derive(GearSpec(teeth="20", backlash="0.05", fillet="0.4"))
    assert ui_text.explainer("backlash", typed, "", PAIR)[3].startswith("0.05 mm · tooth")
    assert ui_text.explainer("fillet", typed, "", PAIR)[3] == "0.4 mm"


def test_a_blank_bore_says_what_blank_means():
    solid = SPUR.derive(GearSpec(teeth="20", bore=""))
    assert ui_text.explainer("bore", solid, "")[3] == "blank → a solid disc, no bore feature"


def test_a_gear_that_does_not_work_out_says_check_the_fields():
    for field in ui_text.EXPLAINER_FIELDS:
        assert ui_text.explainer(field, None, "", PAIR, FOLDER)[3] == "check the fields"
    # …and so does a solver field with nothing to solve.
    empty = PairSpec(mode="pair", gear_a=GEAR_A, gear_b=GEAR_B)
    assert ui_text.explainer("centre_distance", DERIVED_A, "", empty)[3] == "check the fields"
    assert ui_text.explainer("ratio", DERIVED_A, "", None)[3] == "check the fields"


def test_the_name_line_drops_the_folder_until_one_is_chosen():
    assert ui_text.explainer("name", DERIVED_A, "Gear_m1.5_N20")[3] == "Gear_m1.5_N20.SLDPRT"


def test_an_unknown_field_is_refused_in_a_sentence():
    with pytest.raises(ValueError, match="no explainer for a field called 'kind'"):
        ui_text.explainer("kind", DERIVED_A, "")


def test_the_output_readout_keeps_the_end_of_a_long_path():
    assert ui_text.output_readout("") == "choose a folder"
    assert ui_text.output_readout(r"C:\Gears") == r"C:\Gears"
    long = "C:\\" + "very\\" * 20 + "Gears"
    shortened = ui_text.output_readout(long)
    assert shortened.startswith("…") and shortened.endswith("Gears") and len(shortened) == 38


def test_the_link_headline_is_happy_with_no_document_open():
    assert ui_text.link_headline(False, None) == ("pywin32 not installed", "off")
    assert ui_text.link_headline(True, None) == ("not reachable", "bad")
    assert ui_text.link_headline(True, {"version": "SolidWorks 2026", "title": ""}) == (
        "SolidWorks 2026 — no document open", "ok"
    )
    assert ui_text.link_headline(True, {"version": "SolidWorks 2026", "title": "Gear.SLDPRT"})[1] == "ok"


def test_the_mode_note_says_what_the_button_will_do():
    assert ui_text.mode_note("single", ["Gear_m1.5_N25"]) == "Build will make Gear_m1.5_N25.SLDPRT."
    assert ui_text.mode_note("pair", ["Pinion_m1.5_N20", "Gear_m1.5_N60", "Pair_m1.5_20T_60T"]) == (
        "Build will make Pinion_m1.5_N20.SLDPRT, Gear_m1.5_N60.SLDPRT and Pair_m1.5_20T_60T.SLDASM."
    )
    assert ui_text.mode_note("single", ["X"], update_count=3, document="Gear_m1.5_N25.SLDPRT") == (
        "Update values will change 3 variables in Gear_m1.5_N25.SLDPRT."
    )


def test_manual_steps_are_counted():
    assert ui_text.manual_steps_line([]) == ""
    assert ui_text.manual_steps_line(["Assign a material."]) == "1 thing to do by hand: Assign a material."
    assert ui_text.manual_steps_line(["A.", "B", "A."]) == "2 things to do by hand: A; B."


# -- after a build -------------------------------------------------------------


def _result(**values):
    from gear_generator.swbuild import BuildResult
    base = dict(document="Part1", saved=r"C:\Gears\Gear_m1.5_N25.SLDPRT", rebuilt=True,
                manual=["Assign a material to Gear_m1.5_N25; the build leaves it unset."])
    base.update(values)
    return BuildResult(**base)


def test_a_clean_build_names_the_file_and_the_manual_step():
    text, ok = ui_text.build_status(_result())
    assert ok
    assert text == ("Built Gear_m1.5_N25.SLDPRT. 1 thing to do by hand: Assign a material to Gear_m1.5_N25; "
                    "the build leaves it unset.")


def test_a_failed_build_says_where_it_stopped_and_what_solidworks_said():
    text, ok = ui_text.build_status(_result(saved="", failures=[("cut     'Tooth Space' from space, through all",
                                                                   "FeatureCut4 would not cut.")]))
    assert not ok
    assert text == "Part1 was left open, unsaved. cut     'Tooth Space' from space, through all: FeatureCut4 would not cut."


def test_a_build_with_something_to_check_is_not_all_clear():
    text, ok = ui_text.build_status(_result(checks=["Tooth Space Sketch is under-defined, not fully defined"]))
    assert not ok and "Check: Tooth Space Sketch is under-defined" in text


def test_a_pair_lists_all_three_files_or_the_first_failure():
    from gear_generator.swbuild import PairResult
    asm = _result(saved=r"C:\Gears\Pair_m1.5_20T_60T.SLDASM", manual=["Look along the gear axis."])
    text, ok = ui_text.pair_status(PairResult(_result(saved=r"C:\G\Pinion.SLDPRT"), _result(saved=r"C:\G\Gear.SLDPRT"), asm))
    assert ok and text.startswith("Built Pinion.SLDPRT, Gear.SLDPRT and Pair_m1.5_20T_60T.SLDASM.")
    assert "2 things to do by hand" in text
    broken = PairResult(_result(saved="", failures=[("pattern", "no")]), skipped="the second gear and the assembly")
    text, ok = ui_text.pair_status(broken)
    assert not ok and text.endswith("Skipped the second gear and the assembly.")


def test_update_values_says_how_many_changed():
    from gear_generator.swbuild import UpdateResult
    assert ui_text.update_status(UpdateResult(document="G.SLDPRT", changed=["Module"], rebuilt=True)) == (
        "Changed 1 variable in G.SLDPRT and rebuilt it.", True)
    assert ui_text.update_status(UpdateResult(document="G.SLDPRT"))[0].startswith("Nothing to update")
    text, ok = ui_text.update_status(UpdateResult(document="G.SLDPRT", failures=[('"Module"', "refused")]))
    assert not ok and text == '"Module" could not be set in G.SLDPRT: refused'


# -- W4: the footer as one decision, and the sentences of a gearbox build and update -----------------------------
#
# Plans, results and records are built from their dataclasses, never by plan_gearbox, classify, build_gearbox or
# update_gearbox; the gate is a real assessment of the 12 : 1 fixture.

import dataclasses  # noqa: E402

from gear_generator import store, swbuild  # noqa: E402
from gear_generator.gears.base import BuildPlan, GlobalVariable, NewAssembly, NewPart  # noqa: E402
from gear_generator.workbook import assess, model, xlsx  # noqa: E402
from gear_generator.workbook.build import PartJob  # noqa: E402
from gear_generator.workbook.gearbox import GearboxPlan, LayoutReuse, PartReuse  # noqa: E402
from gear_generator.workbook.model import Gear, Shaft  # noqa: E402
from gear_generator.workbook.update import PartUpdate, UpdatePlan  # noqa: E402
from test_workbook_model import reducer, write  # noqa: E402

P = "C:\\Parts\\Reducer_12to1"
STEMS = ("Gear_m1.5_N17", "Gear_m1.5_N68", "Gear_m2_N17", "OutputGear")


def _path(stem, ext=".SLDPRT"):
    return f"{P}\\{stem}{ext}"


@pytest.fixture
def ready(tmp_path):
    """The 12 : 1 workbook, read and assessed: every gate open."""
    spec, diagnostics = model.from_book(xlsx.read(write(tmp_path, reducer())))
    a = assess.assess(spec, diagnostics, P)
    assert a.lay_out_refusal() == ""
    return a


HELD_BACK = ("Gears!A6: G6 slides on S3, a shaft whose Role is fixed, so it is not built by this version of the "
             "app.")


@pytest.fixture
def with_carrier(tmp_path):
    """The 12 : 1 workbook with a row whose part builds and which holds the layout back (a bevel row did until W6
    laid bevels out, a carrier until W7, a dog ring until W8 built them; W8 was the last phase of the import as
    planned on 2026-11-11, and W9 (issue #1) builds on it and leaves no row waiting for a phase, so such a row is one
    this version does not build, W8-PLAN §0.1 — written into the parts plan here, since its sentence is B's)."""
    spec, diagnostics = model.from_book(xlsx.read(write(tmp_path, reducer())))
    a = assess.assess(spec, diagnostics, P)
    a = dataclasses.replace(a, parts=dataclasses.replace(a.parts, refused=[Diagnostic("error", HELD_BACK,
                                                                                         "Gears!A6")]))
    assert a.build_refusal() == "" and a.parts.refused
    return a


def _job(stem, gears, path=None):
    return PartJob(stem, path or _path(stem), tuple(gears), GearSpec(), None, BuildPlan("spur", "A", (NewPart(""),)))


def _reuse(stem, gears, revision=0):
    return PartReuse(_path(stem), stem, tuple(gears), GearSpec(), None, (GlobalVariable("No. of Teeth", "17"),),
                     revision)


def _gearbox(name="Reducer_12to1", build=(), reuse=(), layout="build", assembly=True, **changes):
    layout_path = _path(f"{name}_Layout")
    plans = {"build": BuildPlan("layout", "", (NewPart(""),)),
             "reuse": LayoutReuse(layout_path, (GlobalVariable("S2 X", "63.75"),), ("S2 Axis",)), None: None}
    fields = dict(revision=0, name=name, folder=P, layout_path=layout_path if layout else "",
                  assembly_path=_path(name, ".SLDASM") if assembly else "", build=tuple(build), reuse=tuple(reuse),
                  shafts=(), frames={}, layout=plans[layout],
                  assembly=BuildPlan("assembly", "", (NewAssembly(""),)) if assembly else None, handles={},
                  part_of={})
    fields.update(changes)
    return GearboxPlan(**fields)


FULL = dict(build=[_job(s, [g]) for s, g in zip(STEMS, ("G1", "G2", "G3", "G4"))])


def _record(assembly=True, layout=True, unsaved=None):
    parts = [store.PartEntry(path=_path(s), gears=[g], revision=0) for s, g in zip(STEMS, ("G1", "G2", "G3", "G4"))]
    gearbox = store.GearboxRecord(
        revision=0, name="Reducer_12to1", layout=_path("Reducer_12to1_Layout") if layout else "",
        assembly=_path("Reducer_12to1", ".SLDASM") if assembly else "",
        components=[store.ComponentEntry(gear=g, part=_path(s), name=f"{s}-1") for s, g in
                    zip(STEMS, ("G1", "G2", "G3", "G4"))] if assembly else [])
    return store.LinkRecord(workbook=f"{P}\\Reducer_12to1.xlsx", parts=parts, gearbox=gearbox if layout else None,
                            unsaved=unsaved or {})


def _update(**changes):
    part = PartUpdate(_path("Gear_m1.5_N68"), ("G2",), GearSpec(module="1.5", teeth="69"), None,
                      (GlobalVariable("No. of Teeth", "69"),), changed=True)
    fields = dict(parts=(part,), layout=swbuild.DocumentValues(_path("Reducer_12to1_Layout")),
                  assembly=_path("Reducer_12to1", ".SLDASM"), moved_shafts=("S2", "S3"),
                  replaced=("G2", "G3", "G4"))
    fields.update(changes)
    return UpdatePlan(**fields)


def _saved(stem, ext=".SLDPRT", **values):
    return swbuild.BuildResult(document=stem, saved=_path(stem, ext), **values)


def _failed(document, what="cut 'Tooth Space'", why="FeatureCut4 would not cut."):
    return swbuild.BuildResult(document=document, failures=[(what, why)])


# progress


@pytest.mark.parametrize("step,updating,text", [
    (None, False, "Building in SolidWorks…"),
    (None, True, "Updating SolidWorks…"),
    (swbuild.Step("part", "Gear_m1.5_N68", 2, 4), False, "Building in SolidWorks: part 2 of 4, Gear_m1.5_N68…"),
    (swbuild.Step("check", "Gear_m1.5_N17", 1, 3), False,
     "Building in SolidWorks: checking Gear_m1.5_N17 (1 of 3 already built)…"),
    (swbuild.Step("layout", "Reducer_12to1_Layout"), False,
     "Building in SolidWorks: the layout part, Reducer_12to1_Layout…"),
    (swbuild.Step("assembly", "Reducer_12to1"), False, "Building in SolidWorks: the assembly, Reducer_12to1…"),
    (swbuild.Step("interference"), False, "Building in SolidWorks: checking interference…"),
    (swbuild.Step("check", "Gear_m1.5_N68", 1, 6), True, "Updating SolidWorks: checking Gear_m1.5_N68 (1 of 6)…"),
    (swbuild.Step("values", "Gear_m1.5_N68"), True, "Updating SolidWorks: Gear_m1.5_N68…"),
    (swbuild.Step("place", "Reducer_12to1"), True, "Updating SolidWorks: placing the gears in Reducer_12to1…"),
    (swbuild.Step("interference"), True, "Updating SolidWorks: checking interference…"),
])
def test_progress_says_what_the_worker_is_doing(step, updating, text):
    assert ui_text.progress_text(step, updating) == text


# a finished build


def test_a_built_gearbox_names_its_files_and_says_there_is_no_interference():
    plan = _gearbox(**FULL)
    result = swbuild.GearboxResult(
        parts=swbuild.ManyResult(built=[_saved(s, manual=[f"Assign a material to {s}; the build leaves it unset."])
                                        for s in STEMS]),
        layout=_saved("Reducer_12to1_Layout"), assembly=_saved("Reducer_12to1", ".SLDASM"))
    assert ui_text.gearbox_status(plan, result) == (
        "Built 4 parts, Reducer_12to1_Layout and Reducer_12to1.SLDASM; no interference between the gears. 1 thing "
        "to do by hand: Assign a material to each of the 4 parts; the build leaves it unset.", True)


def test_a_build_again_says_what_it_reused():
    plan = _gearbox("Reducer_12to1_r2", build=[_job("Gear_m1.5_N68_r2", ["G2"])],
                    reuse=[_reuse("Gear_m1.5_N17", ["G1"]), _reuse("Gear_m2_N17", ["G3"]),
                           _reuse("OutputGear", ["G4"])])
    result = swbuild.GearboxResult(parts=swbuild.ManyResult(built=[_saved("Gear_m1.5_N68_r2")]),
                                   layout=_saved("Reducer_12to1_r2_Layout"),
                                   assembly=_saved("Reducer_12to1_r2", ".SLDASM"))
    assert ui_text.gearbox_status(plan, result) == (
        "Built 1 part, Reducer_12to1_r2_Layout and Reducer_12to1_r2.SLDASM, reusing the 3 parts already built; no "
        "interference between the gears.", True)


def test_a_clash_is_a_check_that_stands_out():
    plan = _gearbox(**FULL)
    result = swbuild.GearboxResult(
        parts=swbuild.ManyResult(built=[_saved(s) for s in STEMS]), layout=_saved("Reducer_12to1_Layout"),
        assembly=_saved("Reducer_12to1", ".SLDASM"),
        clashes=[swbuild.Clash(("Gear_m1.5_N17-1", "Gear_m1.5_N68-1"), ("G1", "G2"), 12.3454)])
    assert ui_text.gearbox_status(plan, result) == (
        "Built 4 parts, Reducer_12to1_Layout and Reducer_12to1.SLDASM. Check: G1 and G2 interfere, 12.345 mm³; look "
        "at their mesh in Reducer_12to1.SLDASM.", False)
    result.clashes.append(swbuild.Clash((), (), 0.5))
    assert ui_text.gearbox_status(plan, result)[0].endswith(
        "Check: G1 and G2 interfere, 12.345 mm³; an interference of 0.5 mm³ that SolidWorks could not name; look at "
        "those meshes in Reducer_12to1.SLDASM.")
    result.clashes, result.interference_error = [], "SolidWorks did not answer."
    assert ui_text.gearbox_status(plan, result) == (
        "Built 4 parts, Reducer_12to1_Layout and Reducer_12to1.SLDASM. Interference could not be checked: "
        "SolidWorks did not answer. Look at each mesh in Reducer_12to1.SLDASM by eye.", False)


def test_a_part_that_fails_stops_the_rest_and_build_carries_on():
    plan = _gearbox(**FULL)
    result = swbuild.GearboxResult(parts=swbuild.ManyResult(built=[_saved(STEMS[0]), _failed("Part3")],
                                                            skipped=[_path(STEMS[2]), _path(STEMS[3])]))
    assert ui_text.gearbox_status(plan, result) == (
        "1 part built before it; Part3 was left open, unsaved; cut 'Tooth Space': FeatureCut4 would not cut. 2 parts "
        "not attempted, nor the layout and assembly. Press Build to carry on: what was built is reused.", False)
    result.parts.skipped = []
    assert ui_text.gearbox_status(plan, result)[0].endswith(
        "would not cut. The layout and assembly were not attempted. Press Build to carry on: what was built is "
        "reused.")
    parts_only = _gearbox(layout=None, assembly=False, **FULL)
    result.parts.skipped = [_path(STEMS[2])]
    assert ui_text.gearbox_status(parts_only, result)[0].endswith(
        "would not cut. 1 part not attempted. Press Build parts to carry on: what was built is reused.")


def test_a_layout_that_fails_leaves_the_parts_for_the_next_press():
    plan = _gearbox(**FULL)
    result = swbuild.GearboxResult(parts=swbuild.ManyResult(built=[_saved(s) for s in STEMS]),
                                   layout=_failed("Part5", "insert plane 'S2 X Plane'", "SolidWorks returned None."))
    assert ui_text.gearbox_status(plan, result) == (
        "Built 4 parts; Part5 was left open, unsaved; insert plane 'S2 X Plane': SolidWorks returned None. The "
        "assembly was not attempted. Press Build to carry on: the parts are reused.", False)


def test_an_assembly_that_fails_leaves_the_parts_and_layout_for_the_next_press():
    plan = _gearbox(**FULL)
    result = swbuild.GearboxResult(parts=swbuild.ManyResult(built=[_saved(s) for s in STEMS]),
                                   layout=_saved("Reducer_12to1_Layout"),
                                   assembly=_failed("Assem1", "place G2", "Transform2 was not taken."))
    assert ui_text.gearbox_status(plan, result) == (
        "Built 4 parts and Reducer_12to1_Layout; the assembly Assem1 was left open, unsaved; place G2: Transform2 was "
        "not taken. Press Build to try the assembly again: the parts and layout are reused.", False)


def test_a_retry_after_the_assembly_failed_reuses_the_layout():
    plan = _gearbox(layout="reuse", reuse=[_reuse(s, [g]) for s, g in zip(STEMS, ("G1", "G2", "G3", "G4"))])
    result = swbuild.GearboxResult(layout_reused=_path("Reducer_12to1_Layout"),
                                   assembly=_saved("Reducer_12to1", ".SLDASM"))
    assert ui_text.gearbox_status(plan, result) == (
        "Built Reducer_12to1.SLDASM, reusing Reducer_12to1_Layout and the 4 parts already built; no interference "
        "between the gears.", True)
    result.assembly = _failed("Assem1", "place G2", "Transform2 was not taken.")
    assert ui_text.gearbox_status(plan, result)[0].startswith(
        "Reused Reducer_12to1_Layout and the 4 parts already built; the assembly Assem1 was left open, unsaved;")


def test_build_parts_counts_what_it_made():
    plan = _gearbox(layout=None, assembly=False, build=[_job(STEMS[1], ["G2"])], reuse=[_reuse(STEMS[0], ["G1"])])
    result = swbuild.GearboxResult(parts=swbuild.ManyResult(built=[_saved(STEMS[1])]))
    assert ui_text.gearbox_status(plan, result) == ("Built 1 part, reusing the part already built.", True)


# before Update SolidWorks, and after


def test_the_update_summary_says_what_will_change():
    assert ui_text.update_summary(_update()) == (
        "Update SolidWorks will change G2's values (Gear_m1.5_N68), move S2 and S3 in Reducer_12to1_Layout, and "
        "re-place G2, G3 and G4.")
    shared = PartUpdate(_path("Gear_m1.5_N17"), ("G1", "G5"), GearSpec(), None, (), changed=True)
    assert ui_text.update_summary(_update(parts=(_update().parts[0], shared), moved_shafts=(), replaced=())) == (
        "Update SolidWorks will change the values in Gear_m1.5_N68 (G2) and Gear_m1.5_N17 (G1, G5).")
    assert ui_text.update_summary(_update(parts=(), moved_shafts=(), replaced=("G4",))) == (
        "Update SolidWorks will re-place G4.")
    assert ui_text.update_summary(_update(parts=(), moved_shafts=(), replaced=())) == (
        "SolidWorks already matches the workbook on record; Update SolidWorks checks it live and puts right anything "
        "changed there.")


def test_a_change_update_cannot_carry_offers_to_build_again():
    assert ui_text.update_summary(_update(structural=("G2's bore was added, which its built part cannot take.",))) == (
        "G2's bore was added, which its built part cannot take. Update SolidWorks offers to build again as a new "
        "revision.")
    two = _update(structural=("G2's bore was added, which its built part cannot take.", "S4 was added."))
    assert ui_text.update_summary(two).startswith("G2's bore was added, which its built part cannot take (and 1 "
                                                  "other change Update SolidWorks cannot carry). Update ")
    # swbuild.structural_change's own "build it again" is not said twice (W4 review S4.2).
    recipe = _update(structural=("Gear_m1.5_N17 (G1): The recipe changed from 'A' to 'B'; build it again as a new "
                                 "part.",))
    assert ui_text.update_summary(recipe) == (
        "Gear_m1.5_N17 (G1): The recipe changed from 'A' to 'B', so it needs a new part. Update SolidWorks offers to "
        "build again as a new revision.")
    assert ui_text.update_summary(_update(missing=(_path("Gear_m1.5_N68"),))) == (
        f"Gear_m1.5_N68.SLDPRT is no longer in {P}: it was moved, renamed or deleted since it was built, so Update "
        "SolidWorks offers to build again as a new revision.")
    both = _update(missing=(_path("Gear_m1.5_N68"), _path("Reducer_12to1_Layout")), structural=("S4 was added.",))
    assert ui_text.update_summary(both) == (
        "Gear_m1.5_N68.SLDPRT and Reducer_12to1_Layout.SLDPRT are no longer where they were built: they were moved, "
        "renamed or deleted since (and 1 other change Update SolidWorks cannot carry), so Update SolidWorks offers to build "
        "again as a new revision.")


def _updated(**values):
    fields = dict(parts=[swbuild.UpdateResult(document="Gear_m1.5_N68.SLDPRT", changed=["No. of Teeth"],
                                              rebuilt=True)],
                  layout=swbuild.UpdateResult(document="Reducer_12to1_Layout.SLDPRT", changed=["S2 X", "S3 X"],
                                              rebuilt=True),
                  placed=["G2", "G3", "G4"], rebuilt=True,
                  changed=[_path("Gear_m1.5_N68"), _path("Reducer_12to1_Layout"), _path("Reducer_12to1", ".SLDASM")])
    fields.update(values)
    return swbuild.GearboxUpdate(**fields)


def test_an_update_says_what_it_changed_that_a_file_keeps_its_name_and_to_save():
    assert ui_text.gearbox_update_status(_update(), _updated()) == (
        "Updated SolidWorks: changed 1 variable in Gear_m1.5_N68 (it now has 69 teeth; its file keeps its name), "
        "moved S2 and S3 in Reducer_12to1_Layout, re-placed G2, G3 and G4; no interference between the gears. Save "
        "Gear_m1.5_N68, Reducer_12to1_Layout and Reducer_12to1 in SolidWorks to keep them.", True)


def test_a_part_with_a_name_of_its_own_never_goes_stale():
    named = PartUpdate(_path("Pinion"), ("G2",), GearSpec(teeth="69", name="Pinion"), None, (), changed=True)
    text, _ = ui_text.gearbox_update_status(_update(parts=(named,)), _updated(placed=[]))
    assert text.startswith("Updated SolidWorks: changed 1 variable in Pinion, moved")
    module = PartUpdate(_path("Gear_m1.5_N68"), ("G2",), GearSpec(module="2", teeth="68"), None, (), changed=True)
    text, _ = ui_text.gearbox_update_status(_update(parts=(module,)), _updated(placed=[]))
    assert "Gear_m1.5_N68 (it is now module 2; its file keeps its name)" in text


def test_a_component_dragged_in_solidworks_is_put_back_and_said():
    text, ok = ui_text.gearbox_update_status(_update(parts=(), layout=None), _updated(
        parts=[], layout=None, placed=["G4"], changed=[_path("Reducer_12to1", ".SLDASM")]), dragged=["G4"])
    assert (text, ok) == ("Updated SolidWorks: G4 had been moved in SolidWorks; put back where the workbook has it; "
                          "no interference between the gears. Save Reducer_12to1 in SolidWorks to keep it.", True)
    text, _ = ui_text.gearbox_update_status(_update(), _updated(), dragged=["G3", "G4"])
    assert "re-placed G2; no interference" in text and "G3 and G4 had been moved in SolidWorks; put back where the " \
                                                       "workbook has them." in text


def test_an_update_that_changed_nothing_says_so():
    nothing = _updated(parts=[swbuild.UpdateResult(document="Gear_m1.5_N68.SLDPRT", unchanged=["No. of Teeth"],
                                                   rebuilt=True)], layout=None, placed=[], changed=[])
    assert ui_text.gearbox_update_status(_update(), nothing) == (ui_text.ALREADY_MATCHES, True)
    nothing.clashes = [swbuild.Clash(("a-1", "b-1"), ("G1", "G2"), 1.0)]
    assert ui_text.gearbox_update_status(_update(), nothing) == (
        "SolidWorks already matches the workbook: nothing was changed. Check: G1 and G2 interfere, 1 mm³; look at "
        "their mesh in Reducer_12to1.SLDASM.", False)


def test_a_quiet_press_on_a_part_still_in_error_replaces_only_the_claim_and_keeps_what_follows():
    """The second reading of the fixes review, N4: the still-in-error sentence takes the place of *already matches*
    alone; the interference the press found after it is still said."""
    from types import SimpleNamespace
    nothing = _updated(parts=[swbuild.UpdateResult(document="Gear_m1.5_N68.SLDPRT", unchanged=["No. of Teeth"],
                                                   rebuilt=True)], layout=None, placed=[], changed=[])
    nothing.clashes = [swbuild.Clash(("a-1", "b-1"), ("G1", "G2"), 1.0)]
    finished = SimpleNamespace(still_in_error=["C:\\Out\\Gear_m1.5_N68.SLDPRT"])
    assert ui_text.gearbox_update_status(_update(), nothing, finished=finished) == (
        ui_text.still_in_error_sentence(finished.still_in_error, "C:\\Out\\Reducer_12to1.SLDASM") + " Check: G1 and G2 "
        "interfere, 1 mm³; look at their "
        "mesh in Reducer_12to1.SLDASM.", False)


def test_an_update_that_stops_says_what_it_had_changed_unsaved():
    stopped = _updated(failures=[("Reducer_12to1_Layout", "S2 X could not be set: the value was refused")],
                       changed=[_path("Gear_m1.5_N68")])
    assert ui_text.gearbox_update_status(_update(), stopped) == (
        "Update SolidWorks stopped. Reducer_12to1_Layout: S2 X could not be set: the value was refused. It had already "
        "changed Gear_m1.5_N68, not saved: press Update SolidWorks again once that is put right, or save it in "
        "SolidWorks to keep what it did.", False)
    stopped.changed = []
    assert ui_text.gearbox_update_status(_update(), stopped)[0].endswith("the value was refused. Nothing was changed.")


def test_an_assembly_that_will_not_rebuild_after_an_update_stands_out():
    text, ok = ui_text.gearbox_update_status(_update(), _updated(rebuilt=False))
    assert not ok and "re-placed G2, G3 and G4. SolidWorks reported an error rebuilding Reducer_12to1.SLDASM, so " \
                      "look at it before saving. Save Gear_m1.5_N68, Reducer_12to1_Layout and Reducer_12to1 in " \
                      "SolidWorks to keep them." in text


# the build-again question (decision 8)


def _again():
    return _gearbox("Reducer_12to1_r2", build=[_job("Gear_m1.5_N68_r2", ["G2"])],
                    reuse=[_reuse("Gear_m1.5_N17", ["G1"]), _reuse("Gear_m2_N17", ["G3"]),
                           _reuse("OutputGear", ["G4"])])


def test_the_build_again_question_never_promises_the_old_assembly_is_untouched():
    update = _update(structural=("G2's bore was added, which its built part cannot take through its values.",))
    assert ui_text.build_again_question(update, _again()) == (
        "G2's bore was added, which its built part cannot take through its values. Build again as Reducer_12to1_r2? "
        "That makes a new part for G2 (Gear_m1.5_N68_r2), reuses 3 parts that have not changed and makes a new "
        "layout part and assembly (Reducer_12to1_r2_Layout and Reducer_12to1_r2.SLDASM). Nothing is overwritten, and "
        "Reducer_12to1.SLDASM stays as it is on disk, but it shares the 3 reused parts: a later Update SolidWorks "
        "that changes one of them changes Reducer_12to1.SLDASM too.")


def test_the_build_again_question_for_a_missing_file_or_by_choice():
    missing = ui_text.build_again_question(_update(missing=(_path("Gear_m1.5_N68"),)), _again())
    assert missing.startswith(f"Gear_m1.5_N68.SLDPRT is no longer in {P}: it was moved, renamed or deleted since it "
                              "was built, "
                              "so Update SolidWorks cannot change it. Build again as Reducer_12to1_r2? ")
    fresh = _gearbox("Reducer_12to1_r2", **FULL)
    chosen = ui_text.build_again_question(_update(), fresh)
    assert chosen.startswith("Nothing on record needs a new revision. Build again as Reducer_12to1_r2? That makes new "
                             "parts for G1 (Gear_m1.5_N17), ")
    assert chosen.endswith("Nothing is overwritten, and Reducer_12to1.SLDASM and its files are left as they are.")
    refused = ui_text.build_again_question(_update(), _gearbox("Reducer_12to1_r2", refusal="Save Gear_m1.5_N68 first."))
    assert refused.endswith("Build again as Reducer_12to1_r2? It cannot go ahead: Save Gear_m1.5_N68 first.")


# the footer: every state


def _footer(a, **kw):
    return ui_text.workbook_footer(a, folder=P, **kw)


def test_ready_to_build_the_whole_gearbox(ready):
    f = _footer(ready, plan=_gearbox(**FULL))
    assert f == ui_text.Footer(f"Ready: Build makes 4 parts, Reducer_12to1_Layout and Reducer_12to1.SLDASM in {P}.",
                               True, ui_text.BUILD, "Build", True, True, False, False, False)


def test_ready_with_the_parts_already_built(ready):
    record = _record(layout=False)
    plan = _gearbox(reuse=[_reuse(s, [g]) for s, g in zip(STEMS, ("G1", "G2", "G3", "G4"))])
    f = _footer(ready, record=record, plan=plan, update=_update(parts=(), moved_shafts=(), replaced=(), layout=None,
                                                                assembly=""))
    assert f.text == (f"Ready: Build makes Reducer_12to1_Layout and Reducer_12to1.SLDASM in {P}, reusing the 4 parts "
                      "already built.")
    assert (f.build_action, f.build_enabled, f.build_primary) == (ui_text.BUILD, True, True)
    assert (f.update_shown, f.update_enabled, f.update_primary) == (True, True, False)


def test_ready_to_carry_on_after_the_assembly_failed(ready):
    plan = _gearbox(layout="reuse", reuse=[_reuse(s, [g]) for s, g in zip(STEMS, ("G1", "G2", "G3", "G4"))])
    f = _footer(ready, record=_record(assembly=False), plan=plan)
    assert f.text == (f"Ready: Build makes Reducer_12to1.SLDASM in {P}, reusing Reducer_12to1_Layout and the 4 parts "
                      "already built.")
    assert f.build_action == ui_text.BUILD and f.build_enabled and not f.update_primary


def test_ready_at_a_later_revision_says_why(ready):
    plan = _gearbox("Reducer_12to1_r2", revision=2, revision_reason="Reducer_12to1.SLDASM is already there, with no "
                                                                    "record of it", **FULL)
    assert _footer(ready, plan=plan).text.endswith(
        f"Reducer_12to1_r2.SLDASM in {P}. Reducer_12to1.SLDASM is already there, with no record of it.")


def test_a_refused_plan_holds_build_back(ready):
    f = _footer(ready, plan=_gearbox(refusal=f"{P}\\Reducer_12to1.SLDASM already exists.", **FULL))
    assert (f.text, f.ok, f.build_enabled) == (f"{P}\\Reducer_12to1.SLDASM already exists.", False, False)


def test_build_parts_while_a_later_phase_holds_the_layout_back(with_carrier):
    f = _footer(with_carrier, plan=_gearbox(layout=None, assembly=False, **FULL))
    assert f.text == f"Ready: Build parts makes 4 parts in {P}; the layout and assembly are not built: {HELD_BACK}"
    assert (f.ok, f.build_action, f.build_label, f.build_enabled, f.build_primary) == (
        True, ui_text.BUILD_PARTS, "Build parts", True, True)
    plan = _gearbox(layout=None, assembly=False, build=[_job(STEMS[3], ["G4"])],
                    reuse=[_reuse(s, [g]) for s, g in zip(STEMS[:3], ("G1", "G2", "G3"))])
    f = _footer(with_carrier, plan=plan, record=_record(layout=False))
    assert f.text.startswith(f"Ready: Build parts makes 1 part in {P}, reusing the 3 parts already built; the layout")
    assert f.update_shown and not f.update_primary
    nothing = _gearbox(layout=None, assembly=False, reuse=plan.reuse + (_reuse(STEMS[3], ["G4"]),))
    f = _footer(with_carrier, plan=nothing, record=_record(layout=False))
    assert f.text.startswith("The 4 parts are built already, so Build parts has nothing to make; the layout and ")
    assert f.ok and not f.build_enabled


def test_built_and_changed_since_offers_update(ready):
    f = _footer(ready, record=_record(), plan=_again(), update=_update())
    assert f == ui_text.Footer(
        "Update SolidWorks will change G2's values (Gear_m1.5_N68), move S2 and S3 in Reducer_12to1_Layout, and "
        "re-place G2, G3 and G4.", True, ui_text.BUILD_AGAIN, "Build again…", True, False, True, True, True)


def test_built_and_matching_keeps_update_enabled(ready):
    f = _footer(ready, record=_record(), update=_update(parts=(), moved_shafts=(), replaced=()))
    assert f.text.startswith("SolidWorks already matches the workbook on record") and f.update_enabled


def test_a_structural_change_offers_to_build_again(ready):
    update = _update(structural=("G2's bore was added, which its built part cannot take.",))
    f = _footer(ready, record=_record(), plan=_again(), update=update)
    assert (f.text, f.ok, f.update_enabled, f.build_enabled) == (
        "G2's bore was added, which its built part cannot take. Update SolidWorks offers to build again as "
        "Reducer_12to1_r2.", True, True, True)
    # The build it offers cannot go: neither button offers it, and the sentence says why (W4 review S4.1).
    blocked = _footer(ready, record=_record(), plan=dataclasses.replace(
        _again(), refusal="Gears!R5: G4's part would be Reducer_12to1_Layout.SLDPRT, …: give it another Part name."),
        update=update)
    assert blocked.text == ("G2's bore was added, which its built part cannot take. The new revision it needs, "
                            "Reducer_12to1_r2, cannot be built yet: Gears!R5: G4's part would be "
                            "Reducer_12to1_Layout.SLDPRT, …: give it another Part name.")
    assert "offers" not in blocked.text
    assert (blocked.ok, blocked.update_enabled, blocked.build_enabled) == (False, False, False)


def test_a_missing_file_offers_to_build_again_and_stands_out(ready):
    f = _footer(ready, record=_record(), plan=_again(), update=_update(missing=(_path("Gear_m1.5_N68"),)))
    assert f.text.endswith("offers to build again as Reducer_12to1_r2.") and not f.ok and f.update_enabled


def test_an_answer_is_followed_plainly_by_what_was_already_so(ready, tmp_path):
    """No to Build again? for a missing file: nothing happened, so *Since then* would be wrong (it read
    "Nothing was changed in SolidWorks. Since then: Gear_m1.5_N68.SLDPRT is no longer in …")."""
    missing = _update(missing=(_path("Gear_m1.5_N68"),))
    f = _footer(ready, record=_record(), plan=_again(), update=missing,
                note=ui_text.Note(ui_text.NOTHING_CHANGED, True, ui_text.NOTE_ANSWER))
    assert f.text == (f"Nothing was changed in SolidWorks. Gear_m1.5_N68.SLDPRT is no longer in {P}: it was moved, "
                      "renamed or deleted since it was built, so Update SolidWorks offers to build again as "
                      "Reducer_12to1_r2.")
    assert not f.ok
    f = _footer(ready, record=_record(), plan=_again(), update=missing,
                note=ui_text.Note(ui_text.ASKED_TOO_LATE, False, ui_text.NOTE_ANSWER))
    assert f.text.startswith(ui_text.ASKED_TOO_LATE + " Gear_m1.5_N68.SLDPRT is no longer in")
    # An Export's sentence is an answer too: an error it did not mend was there before it.
    spec = model.replace(reducer(), gears=(reducer().gears[0], model.replace(reducer().gears[1], teeth="68.5"))
                         + reducer().gears[2:])
    read, diagnostics = model.from_book(xlsx.read(write(tmp_path, spec, "Bad.xlsx")))
    bad = assess.assess(read, diagnostics, P)
    from gear_generator.workbook.export import Exported
    exported = ui_text.export_note(Exported(written=["Shafts!C3"], results=True))
    assert exported == ui_text.Note("Exported 1 cell and the Results sheet.", True, ui_text.NOTE_STANDING)
    f = _footer(bad, note=exported)
    assert f.text.startswith("Exported 1 cell and the Results sheet. Fix the workbook before building:")
    # A job's sentence keeps *Since then*: the workbook may have moved on while it ran.
    assert _footer(bad, note=("Built 4 parts.", True)).text.startswith("Built 4 parts. Since then: Fix the workbook")


def test_an_update_left_unsaved_is_said_until_it_is_saved(ready):
    update = _update(unsaved=(_path("Gear_m1.5_N68"), _path("Reducer_12to1_Layout")))
    f = _footer(ready, record=_record(), update=update)
    assert f.text.endswith("re-place G2, G3 and G4. Gear_m1.5_N68 and Reducer_12to1_Layout have changes from Update "
                           "SolidWorks that are not saved: save them in SolidWorks to keep them. If SolidWorks "
                           "closed them without saving, press Update SolidWorks to make them again.")
    f = _footer(ready, record=_record(unsaved={_path("Gear_m1.5_N68"): 1.0}), update=None)
    assert "Gear_m1.5_N68 has changes from Update SolidWorks that are not saved: save it" in f.text


def test_a_job_running_holds_both_buttons(ready):
    step = swbuild.Step("part", "Gear_m1.5_N68", 2, 4)
    f = _footer(ready, record=_record(), update=_update(), building=True, progress=step)
    assert (f.text, f.ok, f.build_enabled, f.update_enabled, f.update_shown) == (
        "Building in SolidWorks: part 2 of 4, Gear_m1.5_N68…", True, False, False, True)
    f = _footer(ready, record=_record(), update=_update(), updating=True)
    assert f.text == "Updating SolidWorks…" and not f.update_enabled


def test_the_window_own_troubles_come_first(ready):
    gone = f"The workbook is no longer at {P}\\Reducer_12to1.xlsx."
    f = _footer(ready, record=_record(), update=_update(), error=gone)
    assert (f.text, f.ok, f.build_enabled, f.update_enabled) == (gone, False, False, False)
    f = _footer(dataclasses.replace(ready, chosen=("a fix",)), record=_record(), update=_update())
    assert f.text == ("1 fix chosen: Export writes it into the workbook, and Build and Update SolidWorks wait for "
                      "that, so the workbook and SolidWorks agree.") and not f.update_enabled
    f = _footer(dataclasses.replace(ready, provisional=True), record=_record(), update=_update())
    assert f.text == ui_text.RECALC_WAIT_UPDATE and f.ok and not (f.build_enabled or f.update_enabled)
    f = _footer(dataclasses.replace(ready, provisional=True), plan=_gearbox(**FULL))
    assert f.text == ui_text.RECALC_WAIT


def test_a_workbook_error_holds_build_and_update(ready, tmp_path):
    spec = model.replace(reducer(), gears=(reducer().gears[0], model.replace(reducer().gears[1], teeth="68.5"))
                         + reducer().gears[2:])
    read, diagnostics = model.from_book(xlsx.read(write(tmp_path, spec, "Bad.xlsx")))
    bad = assess.assess(read, diagnostics, P)
    f = _footer(bad, record=_record(), update=_update())
    assert f.text.startswith("Fix the workbook before building: Gears!F3") and not f.ok
    assert (f.build_action, f.build_enabled, f.update_shown, f.update_enabled) == (ui_text.BUILD_AGAIN, False, True,
                                                                                   False)


def test_a_missing_output_folder_holds_build_but_not_update(ready):
    f = _footer(ready, plan=_gearbox(**FULL), folder_exists=False)
    assert (f.text, f.ok, f.build_enabled) == (
        f"The output folder {P} does not exist; make it, or change it on the Box sheet.", False, False)
    f = _footer(ready, record=_record(), plan=_again(), update=_update(), folder_exists=False)
    assert f.text.startswith("Update SolidWorks will change") and f.update_enabled and not f.build_enabled
    unset = dataclasses.replace(ready, folder="")
    f = ui_text.workbook_footer(unset, record=_record(), plan=_again(), update=_update())
    assert f.update_enabled and not f.build_enabled


def test_a_newer_record_holds_build_and_update(ready, tmp_path):
    (tmp_path / "R.workbook.json").write_text('{"link_schema_version": %d}' % (store.LINK_SCHEMA_VERSION + 1))
    with pytest.raises(store.UnknownSchema) as caught:
        store.read_link_record(str(tmp_path / "R.xlsx"))
    f = _footer(ready, record_problem=str(caught.value), plan=_gearbox(**FULL))
    assert (f.text, f.ok, f.build_enabled, f.update_shown) == (str(caught.value), False, False, False)


def test_a_broken_record_lets_build_go_ahead_and_says_so(ready, tmp_path):
    (tmp_path / "R.workbook.json").write_text("{half")
    with pytest.raises(store.StoreError) as caught:
        store.read_link_record(str(tmp_path / "R.xlsx"))
    f = _footer(ready, record_problem=str(caught.value), plan=_gearbox(**FULL))
    assert f.text.startswith("Ready: Build makes 4 parts") and f.text.endswith(
        "R.workbook.json, cannot be read: it is not JSON (Expecting property name enclosed in double quotes: line 1 "
        "column 2 (char 1)). The next Build sets it aside and starts a new one.")
    assert (f.ok, f.build_enabled) == (False, True)


def test_a_finished_jobs_sentence_stays_until_something_goes_wrong(ready, tmp_path):
    built = ("Built 4 parts, Reducer_12to1_Layout and Reducer_12to1.SLDASM. Check: G1 and G2 interfere, 1 mm³; look "
             "at their mesh in Reducer_12to1.SLDASM.", False)
    f = _footer(ready, record=_record(), plan=_again(), update=_update(parts=(), moved_shafts=(), replaced=()),
                note=built)
    assert (f.text, f.ok, f.build_enabled, f.update_enabled) == (built[0], False, True, True)
    f = _footer(ready, record=_record(), update=_update(), note=("Updated SolidWorks: … Save in SolidWorks to keep "
                                                                 "it.", True), results_due=True)
    assert f.text == "Updated SolidWorks: … Save in SolidWorks to keep it." + ui_text.RESULTS_DUE and f.ok
    f = _footer(ready, record=_record(), plan=_again(), update=_update(), note=built, folder_exists=False,
                error="")
    assert f.text.startswith(built[0])
    spec = model.replace(reducer(), gears=(reducer().gears[0], model.replace(reducer().gears[1], teeth="68.5"))
                         + reducer().gears[2:])
    read, diagnostics = model.from_book(xlsx.read(write(tmp_path, spec, "Bad.xlsx")))
    f = _footer(assess.assess(read, diagnostics, P), record=_record(), update=_update(), note=built)
    assert f.text.startswith(built[0] + " Since then: Fix the workbook before building:") and not f.update_enabled


def test_the_gear_table_says_what_is_built_and_what_update_changes(ready):
    rows = {r[0]: r for r in ui_text.workbook_gear_rows(ready.spec, ready.parts, ready.diagnostics,
                                                         record=_record(), update=_update())}
    assert rows["G1"][6:] == ("Gear_m1.5_N17", ui_text.GEAR_STATE_BUILT, "built")
    assert rows["G2"][6:] == ("Gear_m1.5_N68", ui_text.GEAR_STATE_CHANGES, "changes on Update")
    structural = _update(structural=("G4's bore was added, which its built part cannot take.",),
                         missing=(_path("Gear_m2_N17"),))
    rows = {r[0]: r for r in ui_text.workbook_gear_rows(ready.spec, ready.parts, ready.diagnostics,
                                                         record=_record(), update=structural)}
    assert rows["G4"][7:] == (ui_text.GEAR_STATE_NEW_PART, "needs a new part")
    assert rows["G3"][7:] == (ui_text.GEAR_STATE_NEW_PART, "needs a new part")
    assert rows["G1"][7] == ui_text.GEAR_STATE_BUILT
    plain = {r[0]: r for r in ui_text.workbook_gear_rows(ready.spec, ready.parts, ready.diagnostics)}
    assert plain["G1"][7:] == (ui_text.GEAR_STATE_BUILDS, "to build")


def test_the_gear_table_shows_the_part_the_build_would_make(ready):
    """Second W4 review N6: a gear whose own file name is taken is built as <stem>_r2, but the Part column showed
    its own stem (visible on the WorkbookCopy board)."""
    plan = _gearbox(part_of={"G1": _path("Gear_m1.5_N17_r2"), "G2": _path("Gear_m1.5_N68"),
                             "G3": _path("Gear_m2_N17_r3"), "G4": _path("OutputGear")})
    rows = {r[0]: r for r in ui_text.workbook_gear_rows(ready.spec, ready.parts, ready.diagnostics, plan=plan)}
    assert [rows[g][6] for g in ("G1", "G2", "G3", "G4")] == ["Gear_m1.5_N17_r2", "Gear_m1.5_N68", "Gear_m2_N17_r3",
                                                              "OutputGear"]


# -- what the Workbook window itself says around a job (the W4 window wiring) ------------------------------------


def test_the_gears_readout_counts_what_is_on_record(ready):
    assert ui_text.workbook_parts_readout(ready.parts) == "4 parts to build"
    assert ui_text.workbook_parts_readout(ready.parts, record=_record()) == "4 parts built"
    two = store.LinkRecord(parts=_record().parts[:2])
    assert ui_text.workbook_parts_readout(ready.parts, record=two) == "2 parts built · 2 to build"
    assert ui_text.workbook_parts_readout(ready.parts, record=store.LinkRecord()) == "4 parts to build"


def test_the_header_says_whether_what_is_built_is_this_version():
    assert ui_text.workbook_built_tag(None, "abc") == ""
    assert ui_text.workbook_built_tag(store.LinkRecord(digest="abc"), "abc") == ""        # nothing on record
    built = dataclasses.replace(_record(), digest="abc")
    assert ui_text.workbook_built_tag(built, "abc") == " · built from this version"
    assert ui_text.workbook_built_tag(built, "def") == " · changed since it was built"
    parts = dataclasses.replace(_record(layout=False), digest="abc")
    assert ui_text.workbook_built_tag(parts, "abc") == " · parts built from this version"
    assert ui_text.workbook_built_tag(parts, "def") == " · changed since its parts were built"


def test_a_job_that_cannot_start_says_why():
    assert ui_text.job_unreachable("pywin32 is not installed.") == (
        "SolidWorks cannot be reached from here, so nothing was built. pywin32 is not installed.")
    assert ui_text.job_unreachable("", updating=True) == "SolidWorks cannot be reached from here, so nothing was " \
                                                          "updated."
    assert ui_text.strip_busy() == "The strip is building in SolidWorks; build the workbook when it has finished."
    assert ui_text.strip_busy(True) == ("The strip is building in SolidWorks; press Update SolidWorks when it has "
                                        "finished.")
    assert ui_text.export_busy() == "a build is running in SolidWorks; export when it has finished."
    assert ui_text.export_busy(True) == "Update SolidWorks is running; export when it has finished."


def test_a_job_that_raised_is_said_as_it_came_or_named():
    refusal = swbuild.BuildError("C:\\P\\R.SLDASM already exists, and a build never overwrites a file.")
    assert ui_text.job_failed(refusal) == str(refusal)
    assert ui_text.job_failed(KeyError("x")) == "The build stopped before it made anything — KeyError: 'x'"
    assert ui_text.job_failed(ValueError("v"), updating=True) == (
        "Update SolidWorks stopped before it changed anything — ValueError: v")
    # A component renamed or deleted in SolidWorks: Update cannot put it back, and says the way on (S4.6).
    gone = swbuild.NotAsBuilt("Gear_m1.5_N68-1 is not in Reducer_12to1.SLDASM any more: it was renamed or deleted in "
                              "SolidWorks.", _path("Reducer_12to1", ".SLDASM"))
    assert ui_text.job_failed(gone, updating=True) == (
        "Gear_m1.5_N68-1 is not in Reducer_12to1.SLDASM any more: it was renamed or deleted in SolidWorks. Update "
        "SolidWorks cannot put that back; Build again… builds the next revision beside it, with an assembly of its "
        "own, and leaves this one as it is.")
    assert ui_text.collect_failed(ValueError("v")) == "The build could not be collected — ValueError: v"
    assert ui_text.planning_failed(ValueError("v")) == (
        "What to build could not be worked out — ValueError: v. Nothing is built or updated until it can be.")


def test_records_that_could_not_be_written_or_carried():
    assert ui_text.sidecar_unwritten("C:\\P\\G.gear.json", OSError("denied")) == (
        "The part's record G.gear.json could not be written beside it: denied.")
    assert ui_text.record_unwritten("C:\\P\\R.workbook.json", OSError("denied")) == (
        "The record of what was built, R.workbook.json, could not be written: denied. What SolidWorks saved stays "
        "on disk, and the next Build goes beside it rather than over it.")
    assert ui_text.record_not_carried("it was written by a newer Gear Generator") == (
        "The record of what was built stays beside the workbook's old place: it was written by a newer Gear "
        "Generator.")


def test_the_question_its_answer_and_closing_while_a_job_runs():
    assert ui_text.BUILD_AGAIN_TITLE == "Build again?" and ui_text.NOTHING_CHANGED == "Nothing was changed in " \
                                                                                      "SolidWorks."
    assert ui_text.ASKED_TOO_LATE == ("The workbook changed while the question was open, so nothing was built; press "
                                      "Build again… once more if it still applies.")     # "build again" once
    assert ui_text.closes_when_done() == ("This window closes once the build has finished and what it saved is on "
                                          "record; it stays open if something needs saying.")
    assert ui_text.closes_when_done(True).startswith("This window closes once the update has finished")


def test_a_clash_is_called_a_mesh_only_when_it_is_one():
    """W4 smoke test on SolidWorks 2026: a widened G1 clashed with G4 beside it, which it does not mesh with."""
    asm = _saved("Reducer_12to1", ".SLDASM")
    built = dict(parts=swbuild.ManyResult(built=[_saved(s) for s in STEMS]), layout=_saved("Reducer_12to1_Layout"),
                 assembly=asm)
    plan = _gearbox(**FULL, meshes=(("G1", "G2"), ("G3", "G4")))
    mesh = swbuild.Clash(("Gear_m1.5_N17-1", "Gear_m1.5_N68-1"), ("G2", "G1"), 1.0)
    beside = swbuild.Clash(("Gear_m1.5_N17-1", "OutputGear-1"), ("G1", "G4"), 2.0)
    result = swbuild.GearboxResult(clashes=[mesh], **built)
    assert ui_text.gearbox_status(plan, result)[0].endswith(
        "Check: G2 and G1 interfere, 1 mm³; look at their mesh in Reducer_12to1.SLDASM.")
    result.clashes = [beside]
    assert ui_text.gearbox_status(plan, result)[0].endswith(
        "Check: G1 and G4 interfere, 2 mm³; look where they meet in Reducer_12to1.SLDASM.")
    result.clashes = [mesh, beside]
    assert ui_text.gearbox_status(plan, result)[0].endswith(
        "Check: G2 and G1 interfere, 1 mm³; G1 and G4 interfere, 2 mm³; look where they meet in "
        "Reducer_12to1.SLDASM.")
    result.clashes = [swbuild.Clash((), (), 0.5)]               # unnamed: not known to be a mesh
    assert ui_text.gearbox_status(plan, result)[0].endswith("look where they meet in Reducer_12to1.SLDASM.")
    nothing = _updated(parts=[], layout=None, placed=[], changed=[], clashes=[beside])
    assert ui_text.gearbox_update_status(_update(), nothing, meshes=[["G1", "G2"], ["G3", "G4"]])[0].endswith(
        "look where they meet in Reducer_12to1.SLDASM.")
    nothing.clashes = [mesh]
    assert ui_text.gearbox_update_status(_update(), nothing, meshes=[["G1", "G2"], ["G3", "G4"]])[0].endswith(
        "look at their mesh in Reducer_12to1.SLDASM.")


def test_an_update_left_unsaved_never_holds_build_again(ready):
    """W4 review B2: a part Update left unsaved is made new by the next build (GearboxPlan.unsaved_made_new), so
    Build again… is never greyed for a save; the footer still asks for the save, and reads no refusal's words."""
    unsaved = {_path("Gear_m1.5_N68"): 1.0, _path("Reducer_12to1", ".SLDASM"): 1.0}
    again = _gearbox(name="Reducer_12to1_r2", revision=2)
    matches = _update(parts=(), moved_shafts=(), replaced=(), unsaved=tuple(unsaved))
    f = _footer(ready, record=_record(unsaved=unsaved), plan=again, update=matches)
    assert f.build_enabled and f.update_enabled
    assert f.text.endswith("Gear_m1.5_N68 and Reducer_12to1 have changes from Update SolidWorks that are not saved: "
                           "save them in SolidWorks to keep them. If SolidWorks closed them without saving, press "
                           "Update SolidWorks to make them again.")
    assert "waits" not in f.text
    updated = ("Updated SolidWorks: changed 1 variable in Gear_m1.5_N68; no interference between the gears. Save in "
               "SolidWorks to keep it.", True)
    f = _footer(ready, record=_record(unsaved=unsaved), plan=again, update=matches, note=updated)
    assert f.text == updated[0] and f.build_enabled
    # A refusal that happens to name an unsaved file is said as the refusal it is, not as a wait for a save.
    taken = _gearbox(name="Reducer_12to1_r2", revision=2,
                     refusal=r"This build would use both C:\P\Gear_m1.5_N68.SLDPRT and C:\Q\Gear_m1.5_N68.SLDPRT.")
    f = _footer(ready, record=_record(unsaved=unsaved), plan=taken, update=matches)
    assert not f.build_enabled and f.text.endswith(taken.refusal)


def test_build_again_greyed_always_says_why(ready):
    # Held for anything else, the reason itself follows what Update would do.
    f = _footer(ready, record=_record(), plan=_gearbox(name="Reducer_12to1_r2", revision=2), update=_update(),
                folder_exists=False)
    assert not f.build_enabled and f.update_enabled and f.text.startswith("Update SolidWorks will change")
    assert f.text.endswith("does not exist; make it, or change it on the Box sheet.")


def test_a_job_that_stopped_between_documents_says_so_and_what_it_saved():
    """W4 review B1: build_gearbox no longer raises after its pre-flight; a raise between documents is a failure on
    the result (GearboxResult.failures): the sentence says what was saved, where it stopped, what was not
    attempted, and that Build carries on."""
    from gear_generator import swbuild
    result = swbuild.GearboxResult()
    result.parts.built = [swbuild.BuildResult(saved=r"C:\P\A.SLDPRT", rebuilt=True),
                          swbuild.BuildResult(saved=r"C:\P\B.SLDPRT", rebuilt=True)]
    result.failures = [("the layout part", "SolidWorks did not complete SaveAs3: The remote procedure call failed "
                                           "(RPC_S_CALL_FAILED).")]
    text, ok = ui_text.gearbox_status(_gearbox(), result)
    assert not ok and text == ("Built 2 parts. The job stopped during the layout part: SolidWorks did not complete "
                               "SaveAs3: The remote procedure call failed (RPC_S_CALL_FAILED). The assembly was not "
                               "attempted. Press Build to carry on: what was built is reused.")
    result.failures = [("the parts", "it stopped on an unexpected KeyError: 'x'.")]
    assert ui_text.gearbox_status(_gearbox(), result)[0] == (
        "Built 2 parts. The job stopped during the parts: it stopped on an unexpected KeyError: 'x'. The layout part "
        "and the assembly were not attempted. Press Build to carry on: what was built is reused.")
    result.parts.built = []
    assert ui_text.gearbox_status(_gearbox(), result) == (
        "Nothing was saved. The job stopped during the parts: it stopped on an unexpected KeyError: 'x'. The layout "
        "part and the assembly were not attempted. Press Build to try again.", False)


# -- W4 review, pass 2: every sentence true, the save asked once, a greyed button always with its reason -----------


def _made(gears, old, new, why, workbook=""):
    from gear_generator.workbook.gearbox import MadeNew
    return MadeNew(tuple(gears), _path(old), _path(new), why, workbook)


UNSAVED_DOCS = {_path("Gear_m1.5_N68"): 1.0, _path("Reducer_12to1_Layout"): 1.0, _path("Reducer_12to1", ".SLDASM"): 1.0}


def test_structural_and_unsaved_asks_for_the_save_once_and_says_which_part_is_made_new(ready):
    """W4 review S4.1 and the demonstration's log: the save was asked twice, Update offered while greyed, "build
    again" three times, and only one of three unsaved documents named."""
    from gear_generator.workbook.gearbox import UNSAVED
    again = dataclasses.replace(_again(), revision=2, made_new=(_made(["G2"], "Gear_m1.5_N68", "Gear_m1.5_N69",
                                                                       UNSAVED),))
    update = _update(structural=("Gear_m1.5_N17 (G1): A bore cannot be added to or removed from a built part through "
                                 "its values; build it again as a new part.",), unsaved=tuple(UNSAVED_DOCS))
    f = _footer(ready, record=_record(unsaved=UNSAVED_DOCS), plan=again, update=update)
    assert f.text == (
        "Gear_m1.5_N17 (G1): A bore cannot be added to or removed from a built part through its values, so it needs a "
        "new part. Update SolidWorks offers to build again as Reducer_12to1_r2. Gear_m1.5_N68, Reducer_12to1_Layout "
        "and Reducer_12to1 have changes from Update SolidWorks that are not saved: save them in SolidWorks to keep "
        "them. If SolidWorks closed them without saving, those changes are gone. While Gear_m1.5_N68's changes are "
        "not saved, the new revision makes G2's part new, as Gear_m1.5_N69, rather than reuse it.")
    assert (f.ok, f.build_enabled, f.update_enabled) == (True, True, True)
    assert f.text.count("save them") == 1 and all(s.lower().count("build again") <= 1 for s in f.text.split(". "))
    question = ui_text.build_again_question(update, again)
    assert ("G2's part is new because Gear_m1.5_N68 has changes from Update SolidWorks that are not saved; to reuse "
            "it instead, answer No and save it in SolidWorks first (if SolidWorks has closed it since without saving, "
            "those changes are gone, and it cannot be reused).") in question


def test_one_document_left_unsaved_is_it_throughout(ready):
    f = _footer(ready, record=_record(unsaved={_path("Gear_m1.5_N68"): 1.0}), update=None)
    assert f.text.endswith("Gear_m1.5_N68 has changes from Update SolidWorks that are not saved: save it in "
                           "SolidWorks to keep it. If SolidWorks closed it without saving, those changes are gone.")
    assert ui_text.save_to_keep([_path("Gear_m1.5_N68")]) == "Save Gear_m1.5_N68 in SolidWorks to keep it."


def test_parts_from_build_parts_never_offer_a_build_again_of_an_assembly_never_built(ready):
    """W4 review S4.4 (w4r_partsonly): Update was enabled and asked "Build again as …?", claiming an earlier
    assembly, while the primary Build did the same without asking."""
    update = _update(structural=("G5 is new, and Update SolidWorks cannot add a part to what was built.",),
                     layout=None, assembly="")
    f = _footer(ready, record=_record(layout=False), plan=_gearbox(**FULL), update=update)
    assert (f.build_action, f.build_enabled, f.update_shown, f.update_enabled) == (ui_text.BUILD, True, True, False)
    assert f.text.endswith("G5 is new, and Update SolidWorks cannot add a part to what was built. Update SolidWorks "
                           "waits until Build has made what that needs.")
    question = ui_text.build_again_question(update, _gearbox(**FULL))
    assert "stays as it is on disk" not in question and question.endswith(
        "Nothing is overwritten, and what is already built is left as it is.")


def test_update_greyed_after_a_stopped_build_says_why_even_under_the_jobs_sentence(ready):
    """W4 review S4.5: after a build whose assembly failed, Update showed greyed with no reason."""
    waits = ("Reducer_12to1_Layout.SLDPRT was saved but its assembly was not made: Build carries on with it, and "
             "Update SolidWorks waits until it has.")
    plan = _gearbox(layout="reuse", reuse=[_reuse(s, [g]) for s, g in zip(STEMS, ("G1", "G2", "G3", "G4"))])
    f = _footer(ready, record=_record(assembly=False), plan=plan, update=UpdatePlan(refusal=waits))
    assert f.update_shown and not f.update_enabled and f.text.endswith(" " + waits)
    note = ui_text.Note("Built 4 parts and Reducer_12to1_Layout; the assembly Assem1 was left open, unsaved; place "
                        "G2: Transform2 was not taken. Press Build to try the assembly again: the parts and layout are "
                        "reused.", False)
    f = _footer(ready, record=_record(assembly=False), plan=plan, update=UpdatePlan(refusal=waits), note=note)
    assert f.text == f"{note.text} {waits}"


def test_a_file_in_the_way_of_a_part_says_whose_it_is_once_per_reason(ready):
    from gear_generator.workbook.gearbox import NO_RECORD, OTHER_WORKBOOK, STALE
    plan = dataclasses.replace(_gearbox(**FULL), made_new=(
        _made(["G1"], "Gear_m1.5_N17", "Gear_m1.5_N17_r2", NO_RECORD),
        _made(["G4"], "OutputGear", "OutputGear_r2", OTHER_WORKBOOK, "C:\\Other\\Box.xlsx"),
        _made(["G2", "G5"], "Gear_m1.5_N68", "Gear_m1.5_N68_r2", STALE)))
    assert _footer(ready, plan=plan).text == (
        f"Ready: Build makes 4 parts, Reducer_12to1_Layout and Reducer_12to1.SLDASM in {P}. Gear_m1.5_N17.SLDPRT is "
        "already there, with no record that this workbook built it (a build that was interrupted can leave such a "
        "file), so G1's part is made as Gear_m1.5_N17_r2. OutputGear.SLDPRT is already there, built from Box.xlsx, so "
        "G4's part is made as OutputGear_r2. Gear_m1.5_N68.SLDPRT is already there, built from this workbook for "
        "values G2 and G5 no longer have, so the part for G2 and G5 is made as Gear_m1.5_N68_r2; nothing is "
        "overwritten.")
    # The part a change Update cannot carry replaces is not said again: that change's sentence says it.
    again = dataclasses.replace(_again(), made_new=(_made(["G2"], "Gear_m1.5_N68", "Gear_m1.5_N68_r2", STALE),))
    update = _update(structural=("G2's bore was added, which its built part cannot take.",))
    assert _footer(ready, record=_record(), plan=again, update=update).text == (
        "G2's bore was added, which its built part cannot take. Update SolidWorks offers to build again as "
        "Reducer_12to1_r2.")


def test_a_copied_workbook_is_said_once_in_green_with_build_going_ahead(ready):
    from gear_generator.workbook.gearbox import OTHER_WORKBOOK
    original = "C:\\Work\\Reducer_12to1.xlsx"
    plan = dataclasses.replace(
        _gearbox("Reducer_12to1_r2", revision=2, revision_reason="Reducer_12to1_Layout.SLDPRT is already in C:\\P, and "
                 "a build never overwrites a file. So this build is Reducer_12to1_r2, beside it; nothing is "
                 "overwritten.", **FULL),
        foreign_record=original,
        made_new=(_made(["G1"], "Gear_m1.5_N17", "Gear_m1.5_N17_r2", OTHER_WORKBOOK, original),))
    f = _footer(ready, plan=plan)
    assert (f.ok, f.build_enabled, f.update_shown) == (True, True, False)
    assert f.text == (f"Ready: Build makes 4 parts, Reducer_12to1_r2_Layout and Reducer_12to1_r2.SLDASM in {P}. This "
                      f"workbook is a copy of {original}, which is still there, so the record that came with it is "
                      "that workbook's, and so are the SolidWorks files it lists: Build makes this workbook's own "
                      "gearbox beside them, sharing and overwriting nothing.")


def test_a_part_that_failed_the_live_check_is_said_and_the_next_press_makes_it_new(ready):
    """W4 review B2's last corner: the reuse check refused on every press ("68 there and 69 here")."""
    from gear_generator.workbook.gearbox import MISMATCHED
    why = ('Gear_m1.5_N68.SLDPRT does not hold what the workbook asks of it, so it cannot be reused: "No. of Teeth" '
           "is 68 there and 69 here.")
    plan = _gearbox("Reducer_12to1_r2", build=[_job("Gear_m1.5_N17_r2", ["G1"])],
                    reuse=[_reuse("Gear_m1.5_N68", ["G2"]), _reuse("Gear_m2_N17", ["G3"])])
    result = swbuild.GearboxResult(mismatched=[(_path("Gear_m1.5_N68"), why)])
    assert ui_text.gearbox_status(plan, result, again=True) == (
        f"Nothing was built. {why} The next press of Build again… makes G2's part new rather than reuse "
        "Gear_m1.5_N68; nothing is overwritten.", False)
    assert ui_text.gearbox_status(plan, result)[0].endswith("The next press of Build makes G2's part new rather "
                                                            "than reuse Gear_m1.5_N68; nothing is overwritten.")
    again = dataclasses.replace(_again(), made_new=(_made(["G2"], "Gear_m1.5_N68", "Gear_m1.5_N69", MISMATCHED),))
    f = _footer(ready, record=_record(), plan=again, update=_update(structural=("G1's bore was cleared.",)))
    assert f.text.endswith("Update SolidWorks offers to build again as Reducer_12to1_r2. Gear_m1.5_N68 does not hold "
                           "what the record says, as the last job in SolidWorks found, so the new revision makes G2's "
                           "part new, as Gear_m1.5_N69, rather than reuse it.")
    assert "G2's part is new because Gear_m1.5_N68 does not hold what the record says, as the last job in SolidWorks " \
           "found." \
        in ui_text.build_again_question(_update(structural=("G1's bore was cleared.",)), again)


def test_a_document_never_made_asks_for_the_template_first():
    """W4 review S4.3: "…the assembly was not made. new assembly: There is no assembly template at …", and "Press
    Build to try the assembly again" while the same press must fail the same way."""
    asm = swbuild.BuildResult(failures=[("new assembly", "There is no assembly template at C:\\T\\No.asmdot.")],
                              stopped_at="new assembly")
    result = swbuild.GearboxResult(parts=swbuild.ManyResult(built=[_saved(s) for s in STEMS]),
                                   layout=_saved("Reducer_12to1_Layout"), assembly=asm)
    assert ui_text.gearbox_status(_gearbox(**FULL), result) == (
        "Built 4 parts and Reducer_12to1_Layout; SolidWorks did not make the assembly. There is no assembly template "
        "at C:\\T\\No.asmdot. Set an assembly template SolidWorks can use (the Box sheet's Assembly template, else "
        "the strip's), then press Build: the parts and layout are reused.", False)
    part = swbuild.BuildResult(path=_path(STEMS[0]), failures=[("new part", "There is no part template at "
                                                                             "C:\\T\\No.prtdot.")],
                               stopped_at="new part")
    result = swbuild.GearboxResult(parts=swbuild.ManyResult(built=[part], skipped=[_path(s) for s in STEMS[1:]]))
    assert ui_text.gearbox_status(_gearbox(**FULL), result) == (
        "SolidWorks did not make Gear_m1.5_N17. There is no part template at C:\\T\\No.prtdot. 3 parts not attempted, "
        "nor the layout and assembly. Set a part template SolidWorks can use (the Box sheet's Part template, else the "
        "strip's), then press Build.", False)


def test_a_build_again_that_stopped_before_its_layout_names_build_again():
    plan = _gearbox("Reducer_12to1_r2", build=[_job("Gear_m1.5_N68_r2", ["G2"])], reuse=[_reuse(STEMS[0], ["G1"])])
    result = swbuild.GearboxResult(parts=swbuild.ManyResult(built=[_failed("Part3")]))
    assert ui_text.gearbox_status(plan, result, again=True)[0].endswith(
        "The layout and assembly were not attempted. Press Build again… to carry on: what was built is reused.")
    result = swbuild.GearboxResult(parts=swbuild.ManyResult(built=[_saved("Gear_m1.5_N68_r2")]),
                                   layout=_saved("Reducer_12to1_r2_Layout"), assembly=_failed("Assem1"))
    assert "Press Build to try the assembly again" in ui_text.gearbox_status(plan, result, again=True)[0]


def test_the_header_never_says_built_from_this_version_while_an_update_is_unsaved():
    """W4 review S4.7: " · built from this version" right after an Update whose changes were not saved."""
    built = dataclasses.replace(_record(unsaved={_path("Gear_m1.5_N68"): 1.0}), digest="abc")
    assert ui_text.workbook_built_tag(built, "abc") == " · updated from this version, not yet saved"
    assert ui_text.workbook_built_tag(built, "def") == " · changed since it was built"
    parts = dataclasses.replace(_record(layout=False, unsaved={_path("Gear_m1.5_N68"): 1.0}), digest="abc")
    assert ui_text.workbook_built_tag(parts, "abc") == " · parts updated from this version, not yet saved"


def test_an_answer_keeps_the_reason_it_answered(ready):
    """W4 review nit: after No the footer showed only "Nothing was changed in SolidWorks.", and the structural
    reason was gone until the next save."""
    update = _update(structural=("G2's bore was added, which its built part cannot take.",))
    no = ui_text.Note(ui_text.NOTHING_CHANGED, True, ui_text.NOTE_ANSWER)
    f = _footer(ready, record=_record(), plan=_again(), update=update, note=no)
    assert (f.text, f.ok, f.build_enabled, f.update_enabled) == (
        "Nothing was changed in SolidWorks. G2's bore was added, which its built part cannot take. Update SolidWorks "
        "offers to build again as Reducer_12to1_r2.", True, True, True)
    # A plain (text, ok) pair is a job's sentence, as the demonstration script's desk passes it.
    f = _footer(ready, record=_record(), plan=_again(), update=update, note=("Built 4 parts.", True))
    assert f.text == "Built 4 parts."


def test_what_the_window_says_when_the_app_closes_mid_job_or_a_finish_raises():
    assert ui_text.app_closes_when_done(1) == (
        "Gear Generator closes once a workbook's job in SolidWorks has finished and what it did is on record; it "
        "stays open if a Workbook window has something to say.")
    assert ui_text.app_closes_when_done(2).startswith("Gear Generator closes once 2 workbooks' jobs in SolidWorks have "
                                                      "finished and what they did")
    assert ui_text.APP_STAYED_OPEN == ("Gear Generator stayed open: a workbook's job has something to say in its "
                                       "window. Close this window again to quit.")
    assert ui_text.finish_failed(RuntimeError("boom")) == (
        "What the build saved could not all be put on record — RuntimeError: boom. What SolidWorks saved stays on "
        "disk, and the next Build goes beside it rather than over it.")
    assert ui_text.finish_failed(RuntimeError("boom"), journaled=True) == (
        "What the build saved could not all be put on record — RuntimeError: boom. What SolidWorks saved stays on "
        "disk, and the next Build finds it from the journal written before the build, checks it in SolidWorks and "
        "reuses what it can.")
    assert ui_text.finish_failed(RuntimeError("boom"), updating=True) == (
        "What the update changed could not all be put on record — RuntimeError: boom. Its changes are in SolidWorks, "
        "not saved: save them there to keep them.")


# -- the second W4 review: the save asked only where it can happen (N2), the answer keeps the state's lines (N6) ----


def test_an_earlier_revisions_unsaved_documents_are_never_nagged_about(ready):
    """Second review N2 (w4v_after_build_again_unsaved): after Build again… made the next revision, the header for
    _r2 read "updated from this version, not yet saved" because revision 0's documents were still marked, for ever
    if they were abandoned. Only the current revision's documents count, in the header and the footer."""
    record = _record(unsaved=UNSAVED_DOCS)
    record.digest = "d"
    assert ui_text.workbook_built_tag(record, "d") == " · updated from this version, not yet saved"
    record.earlier = [store.EarlierRevision(revision=0, name="Reducer_12to1", layout=_path("Reducer_12to1_Layout"),
                                            assembly=_path("Reducer_12to1", ".SLDASM"),
                                            parts=[_path("Gear_m1.5_N68")])]
    r2 = [_path(s) for s in ("Gear_m1.5_N17", "Gear_m1.5_N69", "Gear_m2_N17", "OutputGear")]
    record.parts = [store.PartEntry(path=p, gears=[g]) for p, g in zip(r2, ("G1", "G2", "G3", "G4"))]
    record.gearbox = store.GearboxRecord(
        revision=2, name="Reducer_12to1_r2", layout=_path("Reducer_12to1_r2_Layout"),
        assembly=_path("Reducer_12to1_r2", ".SLDASM"),
        components=[store.ComponentEntry(gear=g, part=p, name="x-1") for p, g in zip(r2, ("G1", "G2", "G3", "G4"))])
    assert record.current_marks(record.unsaved) == []
    assert ui_text.workbook_built_tag(record, "d") == " · built from this version"
    f = _footer(ready, record=record, update=None)
    assert "not saved" not in f.text and "save" not in f.text


def test_a_document_found_not_holding_what_the_record_says_is_not_called_built_from_this_version():
    record = _record()
    record.digest = "d"
    record.mismatched = {_path("Gear_m1.5_N68"): 1.0}
    assert ui_text.workbook_built_tag(record, "d") == " · SolidWorks no longer holds all of this version"
    assert ui_text.workbook_built_tag(record, "e") == " · changed since it was built"
    record.mismatched = {_path("Gear_m1.5_N68_old"): 1.0}               # an earlier revision's: not counted
    assert ui_text.workbook_built_tag(record, "d") == " · built from this version"


def test_after_no_to_build_again_the_unsaved_and_made_new_lines_stay_with_the_reason(ready):
    """The leftover nit: after "No" the reason was kept, but the save asked for and the part made new were dropped."""
    from gear_generator.workbook.gearbox import UNSAVED
    again = dataclasses.replace(_again(), revision=2, made_new=(_made(["G2"], "Gear_m1.5_N68", "Gear_m1.5_N69",
                                                                       UNSAVED),))
    update = _update(structural=("G1's bore was cleared.",), unsaved=tuple(UNSAVED_DOCS))
    plain = _footer(ready, record=_record(unsaved=UNSAVED_DOCS), plan=again, update=update).text
    answered = _footer(ready, record=_record(unsaved=UNSAVED_DOCS), plan=again, update=update,
                       note=ui_text.Note(ui_text.NOTHING_CHANGED, True, ui_text.NOTE_ANSWER)).text
    assert answered == f"{ui_text.NOTHING_CHANGED} {plain}"
    assert "have changes from Update SolidWorks that are not saved" in answered
    assert "the new revision makes G2's part new, as Gear_m1.5_N69" in answered


def test_the_save_is_never_asked_as_if_it_were_certain_to_be_possible(ready):
    """Second review N2: the footer asked for a save of documents SolidWorks had closed. Nothing on the Tk thread can
    know whether they are open, so the sentence is true either way and says what to press."""
    f = _footer(ready, record=_record(unsaved=UNSAVED_DOCS), plan=_again(), update=_update(unsaved=tuple(UNSAVED_DOCS)))
    assert f.update_enabled and f.text.endswith(
        "save them in SolidWorks to keep them. If SolidWorks closed them without saving, press Update SolidWorks to "
        "make them again.")


# -- the third W4 review: sentences true in every state they appear in ------------------------------------------


def test_the_strips_close_sentence_says_only_what_is_true_for_the_strip():
    """The strip does not stay open to show what its job said (CloseGuard.check quits once it is collected), and its
    job may be an update of a part's values, not a build with saved files."""
    alone = ui_text.app_closes_when_done(0, strip=True)
    assert alone == ("Gear Generator closes once the strip's job in SolidWorks has finished and the strip has "
                     "collected it.")
    both = ui_text.app_closes_when_done(1, strip=True)
    assert both == ("Gear Generator closes once a workbook's job in SolidWorks has finished and what it did is on "
                    "record, and once the strip's job in SolidWorks has finished and the strip has collected it; it "
                    "stays open if a Workbook window has something to say.")
    assert "build" not in alone and "saved" not in alone


def test_the_escape_questions_say_nothing_the_job_does_reaches_the_record_and_promise_only_a_written_journal():
    for question in (ui_text.quit_anyway_question(), ui_text.quit_anyway_question(True),
                     ui_text.close_anyway_question(), ui_text.close_anyway_question(journaled=True),
                     ui_text.close_anyway_question(updating=True)):
        assert "from now" not in question and "nothing will be overwritten" in question
    assert "Nothing that job saves or changes is put on record by this session" in ui_text.quit_anyway_question()
    built = ui_text.close_anyway_question(journaled=True)
    assert "Nothing the build saves is put on record by this window" in built
    assert built.endswith("the build listed what it is about to make in the record before it began, so the next "
                          "Build finds those files, checks them in SolidWorks and reuses what it can.")
    unjournaled = ui_text.close_anyway_question(journaled=False)
    assert "finds" not in unjournaled and unjournaled.endswith(
        "what the build was about to make could not be listed in the record before it began, so the next Build goes "
        "beside the files it saves rather than over them.")
    update = ui_text.close_anyway_question(updating=True)
    assert "Nothing the update changes is put on record by this window" in update and "journal" not in update
    assert "Build finds" not in update
    # The quit question's promise is worded to hold even when a workbook's journal could not be written.
    assert "unless the record cannot be written" in ui_text.quit_anyway_question(True)


def test_a_finish_that_raises_after_an_update_that_changed_nothing_never_says_its_changes_are_in_solidworks():
    nothing = ui_text.finish_failed(RuntimeError("boom"), updating=True, changed=False)
    assert nothing == ("What the update found could not all be put on record — RuntimeError: boom. It changed "
                       "nothing in SolidWorks.")
    assert "Its changes are in SolidWorks" in ui_text.finish_failed(RuntimeError("boom"), updating=True)


def test_the_moved_question_names_a_drive_not_connected_and_says_no_holds_only_until_the_copy_builds():
    q = ui_text.moved_question("C:\\Copy\\R.xlsx", "Z:\\Work\\R.xlsx")
    assert "a drive that is not connected now, answer No: nothing is shared or overwritten." in q
    assert "the answer is kept in the record. No:" in q
    assert "until it has, you are asked again the next time Gear Generator opens this workbook" in q


def test_a_copy_by_answer_whose_original_is_gone_is_never_said_to_be_still_there(ready):
    """Third review item 4 (w4x_copy_of_gone_sentence): after No, with the original gone, the footer and Update's
    refusal both said the original "is still there"."""
    plan = dataclasses.replace(_again(), revision=0, foreign_record="C:\\Work\\Reducer_12to1.xlsx",
                               foreign_said=True)
    sentence = ui_text._copy_sentence(plan)
    assert "still there" not in sentence
    assert sentence.startswith("The record that came with this workbook was written for C:\\Work\\Reducer_12to1.xlsx, "
                               "which you said this workbook is a copy of,")
    assert sentence.endswith("If this workbook was in fact moved or renamed from it, quit Gear Generator and open "
                             "this workbook again before you build, and you are asked again.")
    refusal = store.foreign_record_sentence("C:\\Copy\\Reducer_12to1.xlsx", "C:\\Work\\Reducer_12to1.xlsx",
                                            said=True)
    assert "still there" not in refusal and "which you said this workbook is a copy of" in refusal


def test_a_job_a_closed_window_left_running_holds_build_and_update_with_a_sentence():
    assert ui_text.unowned_job_busy() == (
        "A job from a Workbook window that was closed while SolidWorks had not answered is still running in "
        "SolidWorks; build when it has finished.")
    assert ui_text.unowned_job_busy(True).endswith("press Update SolidWorks when it has finished.")


def test_a_built_gear_the_next_build_makes_new_is_never_shown_as_simply_built(ready):
    """The W4 rerun on SolidWorks 2026, window state 06: the Gears table said G2 was "built" while the footer said
    the new revision makes G2's part new (its Update not saved)."""
    from gear_generator.workbook.gearbox import MISMATCHED, UNSAVED
    record = _record()
    for why in (UNSAVED, MISMATCHED):
        plan = dataclasses.replace(_again(), made_new=(_made(["G2"], "Gear_m1.5_N68", "Gear_m1.5_N69", why),))
        rows = {r[0]: (r[7], r[8]) for r in ui_text.workbook_gear_rows(ready.spec, ready.parts, [], record=record,
                                                                       plan=plan)}
        assert rows["G2"] == (ui_text.GEAR_STATE_CHANGES, "new part on Build")
        assert rows["G1"] == (ui_text.GEAR_STATE_BUILT, "built")


# -- W5: the gearbox that turns (W5-PLAN §1.8 as W5-DECISIONS and W5-INTERFACES amend it) ---------------------------
#
# Plans and results are built by hand from the pinned dataclasses, as W4's were: nothing here runs package A's or
# B's bodies. Every sentence is checked whole, and for what must never be in one.

import re  # noqa: E402

from gear_generator.workbook.motion import MatePlan, MotionPlan  # noqa: E402

REFUSED_LAYOUT = ("Reducer_12to1_Layout.SLDPRT was saved but its assembly was not made: Build carries on with it, "
                  "and Update SolidWorks waits until it has.")
LOCK_PROBLEM = "The mate G3 locked to G2 over-defines the assembly."
FLAG_PROBLEM = "SolidWorks answered 3 when making the mate G1 meshes G2."
TURN_PROBLEM = "G2 cannot turn: SolidWorks reads it fully defined."
STATIC_REASON = ("How a gear is mated to its shaft's axis is not settled by the probes for this version "
                 "(findings.AXIS_MATE_ROUTE).")         # motion.motion_reason()'s shape: a whole sentence


def _clean(text):
    """No sentence says "None", leaves an empty pair of quotes, a doubled space or a dangling comma."""
    assert "None" not in text and "''" not in text and '""' not in text and "  " not in text, text
    assert not re.search(r",\s*[.;:)]|,\s*$|\s[.,;]|\(\s*\)|\.\.(?!\.)", text), text
    return text


def _axis(gear, shaft, z=0.0):
    along = MatePlan(f"{gear} along {shaft}", "along", (gear,), shaft, face_global=f"{gear} Face Z" if z else "",
                     z_front=z)
    return (MatePlan(f"{gear} on {shaft} Axis", "axis", (gear,), shaft), along)


def _motion(trains=(("S1", "S2", "S3"),), drag=("G1",), fixed=(), extra_shafts=None, locks=(("G2", "G3"),),
            meshes=(("G1", "G2", 17, 68), ("G3", "G4", 17, 51))):
    """The 12 : 1's turning plan (anchors G1, G2, G4; G3 locked to G2), or a variant."""
    anchors = {"S1": "G1", "S2": "G2", "S3": "G4"}
    anchors.update(extra_shafts or {})
    mates = []
    for shaft, gear in anchors.items():
        mates.extend(_axis(gear, shaft, 17.0 if gear == "G4" else 0.0))
    mates.extend(MatePlan(f"{f} locked to {a}", "lock", (a, f)) for a, f in locks)
    mates.extend(MatePlan(f"{a} meshes {b}", "mesh", (a, b), ratio=(za, zb)) for a, b, za, zb in meshes)
    return MotionPlan(anchors=anchors, mates=tuple(mates), fixed=tuple(fixed), trains=tuple(trains), drag=tuple(drag))


def _turning(**kw):
    return _gearbox(motion=_motion(**kw), **FULL)


def _built(kind="motion", **values):
    fields = dict(parts=swbuild.ManyResult(built=[_saved(s) for s in STEMS]), layout=_saved("Reducer_12to1_Layout"),
                  assembly=_saved("Reducer_12to1", ".SLDASM"), kind=kind)
    fields.update(values)
    return swbuild.GearboxResult(**fields)


def _refused(*problems, document="Assem1", **values):
    assembly = swbuild.BuildResult(document=document, failures=[("the mate check", p) for p in problems],
                                   mate_problems=list(problems))
    return _built(kind="", assembly=assembly, **values)


# before Build


def test_drag_phrase_for_one_two_and_three_trains():
    assert ui_text.drag_phrase(()) == ""
    assert ui_text.drag_phrase(("G1",)) == "drag G1 in SolidWorks and the rest of its train follow"
    assert ui_text.drag_phrase(("G1", "G5")) == "drag G1 in SolidWorks to turn one train and G5 to turn the other"
    assert ui_text.drag_phrase(("G1", "G5", "G9")) == "drag G1, G5 and G9 in SolidWorks, one for each train"
    assert ui_text.drag_phrase(("G1", "", "G5")) == ui_text.drag_phrase(("G1", "G5"))


def test_before_build_a_turning_gearbox_says_its_gears_turn_together():
    plan = _turning()
    assert _clean(ui_text.motion_ready_line(plan)) == (
        "Its gears are mated to their shafts and to each other, so they turn together in SolidWorks.")


def test_the_ready_line_says_it_right_after_naming_the_assembly(ready):
    f = _footer(ready, plan=_turning())
    assert (_clean(f.text), f.ok, f.build_enabled) == (
        f"Ready: Build makes 4 parts, Reducer_12to1_Layout and Reducer_12to1.SLDASM in {P}. Its gears are mated to "
        "their shafts and to each other, so they turn together in SolidWorks.", True, True)
    later = dataclasses.replace(_turning(), name="Reducer_12to1_r2", revision=2,
                                assembly_path=_path("Reducer_12to1_r2", ".SLDASM"),
                                revision_reason="Reducer_12to1.SLDASM is already there, with no record of it")
    assert _footer(ready, plan=later).text.endswith(
        "Reducer_12to1_r2.SLDASM in C:\\Parts\\Reducer_12to1. Its gears are mated to their shafts and to each other, "
        "so they turn together in SolidWorks. Reducer_12to1.SLDASM is already there, with no record of it.")


def test_before_build_gears_that_turn_alone_or_stay_fixed_are_said():
    """Review M11: the sentence is true in every state, so a lone shaft's gears and fixed ones are named."""
    lone = _turning(extra_shafts={"S4": "G7"}, locks=(("G2", "G3"), ("G7", "G8")))
    assert _clean(ui_text.motion_ready_line(lone)) == (
        "Its gears are mated to their shafts and, where they mesh, to each other, so those that mesh turn together "
        "in SolidWorks. G7 and G8 turn apart from the train: they mesh no other gear.")
    one = _turning(extra_shafts={"S4": "G7"})
    assert ui_text.motion_ready_line(one).endswith(" G7 turns apart from the train: it meshes no other gear.")
    assert _clean(ui_text.motion_ready_line(_turning(fixed=("G9",)))) == (
        "Its turning gears are mated to their shafts and to each other, so they turn together in SolidWorks. G9 "
        "stays fixed where it is placed: its shaft does not turn.")
    assert ui_text.motion_ready_line(_turning(fixed=("G9", "G10", "G11"))).endswith(
        " G9, G10 and G11 stay fixed where they are placed: their shafts do not turn.")


def test_before_build_two_trains_each_turn_together():
    two = _turning(trains=(("S1", "S2"), ("S3",)), drag=("G1", "G4"))
    assert _clean(ui_text.motion_ready_line(two)) == (
        "Its gears are mated to their shafts and to each other, so each train turns together in SolidWorks.")
    lone = _turning(trains=(("S1", "S2"), ("S3",)), drag=("G1", "G4"), extra_shafts={"S4": "G7"}, fixed=("G9",))
    assert _clean(ui_text.motion_ready_line(lone)) == (
        "Its turning gears are mated to their shafts and, where they mesh, to each other, so each train turns "
        "together in SolidWorks. G7 turns apart from the trains: it meshes no other gear. G9 stays fixed where it is "
        "placed: its shaft does not turn.")


def test_before_build_with_no_mesh_each_gear_is_mated_to_its_shaft():
    plan = _turning(trains=(), drag=(), meshes=())
    assert _clean(ui_text.motion_ready_line(plan)) == (
        "Its gears are each mated to their shaft, free to turn in SolidWorks.")
    fixed = _turning(trains=(), drag=(), meshes=(), fixed=("G9",))
    assert _clean(ui_text.motion_ready_line(fixed)) == (
        "Its turning gears are each mated to their shaft, free to turn in SolidWorks. G9 stays fixed where it is "
        "placed: its shaft does not turn.")


def test_before_build_a_missing_finding_says_the_assembly_will_be_static_and_why(ready):
    """Ruling (a) on 2f82a0e: the static build stays when a W5 finding is missing, and is said before Build."""
    plan = _gearbox(static_reason=STATIC_REASON, **FULL)
    assert _clean(ui_text.motion_ready_line(plan)) == (
        "Its gears are placed meshed and fixed, not mated to turn. How a gear is mated to its shaft's axis is not "
        "settled by the probes for this version (findings.AXIS_MATE_ROUTE).")
    assert _footer(ready, plan=plan).text == (
        f"Ready: Build makes 4 parts, Reducer_12to1_Layout and Reducer_12to1.SLDASM in {P}. Its gears are placed "
        "meshed and fixed, not mated to turn. How a gear is mated to its shaft's axis is not settled by the probes "
        "for this version (findings.AXIS_MATE_ROUTE).")


def test_nothing_new_is_said_for_parts_only_refused_or_w4_static_plans():
    assert ui_text.motion_ready_line(None) == ""
    assert ui_text.motion_ready_line(_gearbox(layout=None, assembly=False, motion=_motion(), **FULL)) == ""
    assert ui_text.motion_ready_line(_gearbox(refusal="No.", motion=_motion(), **FULL)) == ""
    assert ui_text.motion_ready_line(_gearbox(**FULL)) == ""


# after Build


def test_after_build_one_train_says_drag_and_the_rest_of_its_train_follow():
    assert ui_text.gearbox_status(_turning(), _built()) == (
        "Built 4 parts, Reducer_12to1_Layout and Reducer_12to1.SLDASM; no interference between the gears where they "
        "stand. Its gears are mated to turn together, and SolidWorks reports no mate in error: drag G1 in SolidWorks "
        "and the rest of its train follow.", True)


def test_after_build_two_and_three_trains_name_a_gear_for_each():
    two = _turning(trains=(("S1", "S2"), ("S3", "S4")), drag=("G1", "G5"))
    assert _clean(ui_text.motion_done_line(two, _built())) == (
        "Its gears are mated to turn in 2 trains, and SolidWorks reports no mate in error: drag G1 in SolidWorks to "
        "turn one train and G5 to turn the other.")
    three = _turning(trains=(("S1",), ("S2",), ("S3",)), drag=("G1", "G5", "G9"))
    assert _clean(ui_text.motion_done_line(three, _built())) == (
        "Its gears are mated to turn in 3 trains, and SolidWorks reports no mate in error: drag G1, G5 and G9 in "
        "SolidWorks, one for each train.")


def test_after_build_with_no_train_each_gear_turns_on_its_shaft_and_fixed_or_lone_gears_are_said():
    assert ui_text.motion_done_line(_turning(trains=(), drag=(), meshes=()), _built()) == (
        "Its gears are each mated to their shaft, free to turn, and SolidWorks reports no mate in error.")
    both = _turning(extra_shafts={"S4": "G7"}, fixed=("G9", "G10"))
    assert _clean(ui_text.motion_done_line(both, _built())) == (
        "Its turning gears are mated to their shafts and, where they mesh, to each other; SolidWorks reports no mate "
        "in error: drag G1 in SolidWorks and the rest of its train follow. G7 turns apart from the train: it meshes "
        "no other gear. G9 and G10 stay fixed where they are placed: their shafts do not turn.")
    assert ui_text.motion_done_line(_turning(fixed=("G9",)), _built()).startswith(
        "Its turning gears are mated to turn together, and SolidWorks reports no mate in error: drag G1")


def test_a_train_with_no_drag_gear_is_never_said_to_be_gears_each_on_their_shaft():
    assert ui_text.motion_done_line(_turning(drag=()), _built()) == (
        "Its gears are mated to turn together, and SolidWorks reports no mate in error.")
    assert ui_text.motion_done_line(_turning(drag=(), trains=(("S1", "S2"), ("S3",))), _built()) == (
        "Its gears are mated to turn in 2 trains, and SolidWorks reports no mate in error.")


def test_after_build_a_clash_still_stands_out_and_the_mates_are_said_after_it():
    result = _built(clashes=[swbuild.Clash(("Gear_m1.5_N17-1", "Gear_m1.5_N68-1"), ("G1", "G2"), 12.3454)])
    plan = dataclasses.replace(_turning(), meshes=(("G1", "G2"),))
    assert ui_text.gearbox_status(plan, result) == (
        "Built 4 parts, Reducer_12to1_Layout and Reducer_12to1.SLDASM. Check: G1 and G2 interfere, 12.345 mm³; look "
        "at their mesh in Reducer_12to1.SLDASM. Its gears are mated to turn together, and SolidWorks reports no mate "
        "in error: drag G1 in SolidWorks and the rest of its train follow.", False)


def test_after_build_a_static_build_by_necessity_says_why_and_w4s_says_nothing_new():
    plan = _gearbox(static_reason=STATIC_REASON, **FULL)
    assert ui_text.gearbox_status(plan, _built(kind="static")) == (
        "Built 4 parts, Reducer_12to1_Layout and Reducer_12to1.SLDASM; no interference between the gears. Its gears "
        "are placed meshed and fixed, not mated to turn. How a gear is mated to its shaft's axis is not settled by "
        "the probes for this version (findings.AXIS_MATE_ROUTE).", True)
    w4 = "Built 4 parts, Reducer_12to1_Layout and Reducer_12to1.SLDASM; no interference between the gears."
    assert ui_text.gearbox_status(_gearbox(**FULL), _built(kind="static")) == (w4, True)
    assert ui_text.gearbox_status(_gearbox(**FULL), _built(kind="")) == (w4, True)
    assert ui_text.motion_done_line(None, _built()) == (
        "Its gears are mated to turn, and SolidWorks reports no mate in error.")


# a refused or flagged mate stops the build (W5-DECISIONS, answer 1): no fallback text anywhere


def test_a_refused_mate_names_it_keeps_the_parts_and_says_build_waits_for_a_changed_workbook():
    text, ok = ui_text.gearbox_status(_turning(), _refused(LOCK_PROBLEM))
    assert (_clean(text), ok) == (
        "Built 4 parts and Reducer_12to1_Layout; no assembly was saved, because SolidWorks found a problem with its "
        "mates. The mate G3 locked to G2 over-defines the assembly. The parts and the layout part are kept. The "
        "assembly is left open in SolidWorks as Assem1, not saved; its parts are the saved ones. Build is available "
        "again once the workbook changes: the same workbook would make the same mates.", False)
    assert "static" not in text and "fixed" not in text and "Press" not in text and "try" not in text


def test_blank_mate_problems_are_no_refusal_and_never_counted_as_none():
    """A failed assembly whose problems are all blank is W4's failed assembly, never "found 0 problems"."""
    result = _refused("", " ")
    text, _ = ui_text.gearbox_status(_turning(), result)
    assert "0 problems" not in text and "no assembly was saved" not in text
    assert text.startswith("Built 4 parts and Reducer_12to1_Layout; the assembly Assem1 was left open, unsaved;")
    text, _ = ui_text.gearbox_status(_turning(), _refused("", LOCK_PROBLEM))
    assert "found a problem with its mates. The mate G3 locked to G2 over-defines the assembly. The parts" in text


def test_every_problem_is_its_own_whole_sentence_and_they_are_counted():
    text, _ = ui_text.mate_refused_status(_turning(), _refused(FLAG_PROBLEM, TURN_PROBLEM))
    assert _clean(text).startswith(
        "Built 4 parts and Reducer_12to1_Layout; no assembly was saved, because SolidWorks found 2 problems with its "
        "mates. SolidWorks answered 3 when making the mate G1 meshes G2. G2 cannot turn: SolidWorks reads it fully "
        "defined. The parts and the layout part are kept.")
    three, _ = ui_text.mate_refused_status(_turning(), _refused(LOCK_PROBLEM, FLAG_PROBLEM, "G4 is over-defined in "
                                                                                           "SolidWorks"))
    assert "found 3 problems with its mates. The mate G3 locked to G2 over-defines the assembly. SolidWorks answered " \
           "3 when making the mate G1 meshes G2. G4 is over-defined in SolidWorks. The parts" in _clean(three)


def test_a_refusal_after_reusing_the_parts_and_layout_and_with_no_document_left_open():
    plan = _gearbox(layout="reuse", motion=_motion(), reuse=[_reuse(s, [g]) for s, g in zip(STEMS, ("G1", "G2", "G3",
                                                                                                   "G4"))])
    result = _refused(TURN_PROBLEM, document="", parts=swbuild.ManyResult(), layout=None,
                      layout_reused=_path("Reducer_12to1_Layout"))
    text, ok = ui_text.gearbox_status(plan, result, again=True)
    assert (_clean(text), ok) == (
        "Reused Reducer_12to1_Layout and the 4 parts already built; no assembly was saved, because SolidWorks found a "
        "problem with its mates. G2 cannot turn: SolidWorks reads it fully defined. The parts and the layout part are "
        "kept. Build is available again once the workbook changes: the same workbook would make the same mates.",
        False)


def test_an_assembly_that_failed_for_any_other_reason_is_w4s_sentence_and_build_carries_on():
    """Only a real refusal is a mate problem; a COM failure during a mate is W4's failed assembly (W5-INTERFACES)."""
    result = _built(kind="", assembly=_failed("Assem1", "mate G1 meshes G2", "The RPC server is unavailable."))
    assert ui_text.gearbox_status(_turning(), result) == (
        "Built 4 parts and Reducer_12to1_Layout; the assembly Assem1 was left open, unsaved; mate G1 meshes G2: The "
        "RPC server is unavailable. Press Build to try the assembly again: the parts and layout are reused.", False)


def _refused_record(digest="d1", problems=(LOCK_PROBLEM,)):
    record = _record(assembly=False)
    record.gearbox.mate_problems, record.gearbox.mate_problems_digest = list(problems), digest
    record.digest = digest
    return record


def _carry_on_plan():
    return _gearbox(layout="reuse", motion=_motion(), reuse=[_reuse(s, [g]) for s, g in zip(STEMS, ("G1", "G2", "G3",
                                                                                                   "G4"))])


def test_the_footer_after_a_refusal_keeps_build_greyed_for_the_same_read_and_says_why(ready):
    """Ruling (b): Build stays greyed for the read the refusal came from; the sentence names the mate and says that
    changing the workbook makes Build available again; Update's own reason is not the record's "Build carries on"."""
    f = _footer(ready, record=_refused_record(), plan=_carry_on_plan(), update=UpdatePlan(refusal=REFUSED_LAYOUT),
                digest="d1")
    assert _clean(f.text) == (
        "Reducer_12to1.SLDASM was not saved, because SolidWorks found a problem with its mates. The mate G3 locked "
        "to G2 over-defines the assembly. Build is available again once the workbook changes: the same workbook "
        "would make the same mates. Update SolidWorks waits until Build has made the assembly.")
    assert (f.ok, f.build_action, f.build_enabled, f.update_shown, f.update_enabled) == (
        False, ui_text.BUILD, False, True, False)
    assert "carries on" not in f.text


def test_under_the_refusing_builds_own_sentence_the_footer_does_not_say_it_twice(ready):
    said = ui_text.gearbox_status(_carry_on_plan(), _refused(LOCK_PROBLEM, parts=swbuild.ManyResult(), layout=None,
                                                             layout_reused=_path("Reducer_12to1_Layout")))
    f = _footer(ready, record=_refused_record(), plan=_carry_on_plan(), update=UpdatePlan(refusal=REFUSED_LAYOUT),
                digest="d1", note=said)
    assert f.text == (
        "Reused Reducer_12to1_Layout and the 4 parts already built; no assembly was saved, because SolidWorks found a "
        "problem with its mates. The mate G3 locked to G2 over-defines the assembly. The parts and the layout part "
        "are kept. The assembly is left open in SolidWorks as Assem1, not saved; its parts are the saved ones. Build "
        "is available again once the workbook changes: the same workbook would make the same mates. Update "
        "SolidWorks waits until Build has made the assembly.")
    assert (f.ok, f.build_enabled, f.update_enabled) == (False, False, False)
    assert f.text.count(LOCK_PROBLEM) == 1


READY_CARRY_ON = (f"Ready: Build makes Reducer_12to1.SLDASM in {P}, reusing Reducer_12to1_Layout and the 4 parts "
                  "already built. Its gears are mated to their shafts and to each other, so they turn together in "
                  "SolidWorks.")
REFUSAL_ON_RECORD = ("Reducer_12to1.SLDASM was not saved, because SolidWorks found a problem with its mates. The mate "
                     "G3 locked to G2 over-defines the assembly.")


def test_once_the_workbook_changes_build_is_offered_and_the_refusal_still_said(ready):
    f = _footer(ready, record=_refused_record(), plan=_carry_on_plan(), update=UpdatePlan(refusal=REFUSED_LAYOUT),
                digest="d2")
    assert _clean(f.text) == (
        f"{READY_CARRY_ON} {REFUSAL_ON_RECORD} The workbook has changed since, so Build tries the assembly again. "
        f"{REFUSED_LAYOUT}")
    assert (f.ok, f.build_enabled, f.update_enabled) == (True, True, False)


def test_a_change_is_never_claimed_when_either_read_is_not_known(ready):
    """With no digest from the window ("", as today's caller passes) or none on record, the footer cannot tell the
    workbook changed: it offers Build and says only that it tries the assembly again."""
    for record_digest, digest in (("d1", ""), ("", "d2"), ("", "")):
        f = _footer(ready, record=_refused_record(digest=record_digest), plan=_carry_on_plan(),
                    update=UpdatePlan(refusal=REFUSED_LAYOUT), digest=digest)
        assert _clean(f.text) == (
            f"{READY_CARRY_ON} {REFUSAL_ON_RECORD} Build tries the assembly again. {REFUSED_LAYOUT}")
        assert "changed since" not in f.text and f.build_enabled
    assert ui_text.motion_record_line(_refused_record(), "", offer=False) == REFUSAL_ON_RECORD
    unnamed = _refused_record()
    unnamed.gearbox.name = ""
    assert ui_text.motion_record_line(unnamed, "d1").startswith("The assembly was not saved, because SolidWorks found")


def test_a_record_with_no_problems_or_no_digest_never_holds_build(ready):
    record = _refused_record(digest="")
    f = _footer(ready, record=record, plan=_carry_on_plan(), digest="")
    assert f.build_enabled and f.text == f"{READY_CARRY_ON} {REFUSAL_ON_RECORD} Build tries the assembly again."
    record = _refused_record(problems=(" ", ""))
    f = _footer(ready, record=record, plan=_carry_on_plan(), digest="d1")
    assert f.build_enabled and f.text == READY_CARRY_ON
    record = _refused_record(problems=())
    f = _footer(ready, record=record, plan=_carry_on_plan(), digest="d1")
    assert f.build_enabled and f.text == (
        f"Ready: Build makes Reducer_12to1.SLDASM in {P}, reusing Reducer_12to1_Layout and the 4 parts already built. "
        "Its gears are mated to their shafts and to each other, so they turn together in SolidWorks.")


def test_a_gate_that_refuses_comes_before_the_refusal(ready, tmp_path):
    f = _footer(ready, record=_refused_record(), plan=_carry_on_plan(), digest="d1", folder_exists=False)
    assert f.text.startswith("The output folder") and not f.build_enabled


# the footer on a gearbox on record


def _turning_record(drag=("G1",)):
    record = _record()
    record.gearbox.kind, record.gearbox.drag = store.GEARBOX_MOTION, list(drag)
    return record


def test_the_footer_on_a_turning_gearbox_says_which_gear_to_drag(ready):
    f = _footer(ready, record=_turning_record(), plan=_turning(), update=_update())
    assert _clean(f.text) == (
        "Update SolidWorks will change G2's values (Gear_m1.5_N68), move S2 and S3 in Reducer_12to1_Layout, and "
        "re-place G2, G3 and G4. It was built with its gears mated to turn: drag G1 in SolidWorks and the rest of "
        "its train follow.")
    assert ui_text.motion_record_line(_turning_record(("G1", "G5"))) == (
        "It was built with its gears mated to turn: drag G1 in SolidWorks to turn one train and G5 to turn the other.")
    assert ui_text.motion_record_line(_turning_record(("G1", "G5", "G9"))) == (
        "It was built with its gears mated to turn: drag G1, G5 and G9 in SolidWorks, one for each train.")
    assert ui_text.motion_record_line(_turning_record(())) == (
        "It was built with its gears each mated to their shaft, free to turn.")
    nothing = _footer(ready, record=_turning_record(), plan=_turning())
    assert nothing.text == (
        "Reducer_12to1.SLDASM is built from this workbook. It was built with its gears mated to turn: drag G1 in "
        "SolidWorks and the rest of its train follow.")


def test_a_w4_static_gearbox_is_offered_a_turning_revision_never_forced(ready):
    """D5: the footer says it was built before gears could turn and that Build again… makes a turning revision;
    Update stays the primary, and every W4 sentence before it is as it was."""
    f = _footer(ready, record=_record(), plan=dataclasses.replace(_again(), motion=_motion()), update=_update())
    assert _clean(f.text) == (
        "Update SolidWorks will change G2's values (Gear_m1.5_N68), move S2 and S3 in Reducer_12to1_Layout, and "
        "re-place G2, G3 and G4. It was built static, before gears could be mated to turn: Build again… makes a new "
        "revision whose gears turn.")
    assert (f.build_action, f.build_enabled, f.build_primary, f.update_enabled, f.update_primary) == (
        ui_text.BUILD_AGAIN, True, False, True, True)
    structural = _footer(ready, record=_record(), plan=dataclasses.replace(_again(), motion=_motion()),
                         update=_update(structural=("G2's bore was added, which its built part cannot take.",)))
    # A structural edit: Update already offers the new revision, so the D5 fact is said in that one offer, and
    # "build again" is said once (W4 review S4.1).
    assert structural.text == (
        "G2's bore was added, which its built part cannot take. Update SolidWorks offers to build again as "
        "Reducer_12to1_r2; it was built static, before gears could be mated to turn, and the new revision's gears "
        "turn.")
    assert structural.text.lower().count("build again") == 1
    missing = _footer(ready, record=_record(), plan=dataclasses.replace(_again(), motion=_motion()),
                      update=_update(missing=(_path("Gear_m1.5_N68"),)))
    assert missing.text == (
        f"Gear_m1.5_N68.SLDPRT is no longer in {P}: it was moved, renamed or deleted since it was built, so Update "
        "SolidWorks offers to build again as Reducer_12to1_r2; it was built static, before gears could be mated to "
        "turn, and the new revision's gears turn.")
    reason = _record()
    reason.gearbox.static_reason = STATIC_REASON
    folded = _footer(ready, record=reason, plan=dataclasses.replace(_again(), motion=_motion()),
                     update=_update(structural=("G2's bore was added, which its built part cannot take.",)))
    assert folded.text == (
        "G2's bore was added, which its built part cannot take. Update SolidWorks offers to build again as "
        "Reducer_12to1_r2; it was built static, and the new revision's gears turn.")
    # A next revision that would not turn: W4's offer, word for word.
    w4 = _footer(ready, record=_record(), plan=_again(),
                 update=_update(structural=("G2's bore was added, which its built part cannot take.",)))
    assert w4.text == ("G2's bore was added, which its built part cannot take. Update SolidWorks offers to build "
                       "again as Reducer_12to1_r2.")


def test_a_w4_static_gearbox_whose_next_revision_would_not_turn_or_cannot_go_is_told_nothing_new(ready):
    w4 = ("Update SolidWorks will change G2's values (Gear_m1.5_N68), move S2 and S3 in Reducer_12to1_Layout, and "
          "re-place G2, G3 and G4.")
    assert _footer(ready, record=_record(), plan=_again(), update=_update()).text == w4
    static_next = dataclasses.replace(_again(), static_reason=STATIC_REASON)
    assert _footer(ready, record=_record(), plan=static_next, update=_update()).text == w4
    greyed = _footer(ready, record=_record(), plan=dataclasses.replace(_again(), motion=_motion()), update=_update(),
                     folder_exists=False)
    assert "Build again… makes" not in greyed.text and not greyed.build_enabled


def test_a_gearbox_built_static_for_a_missing_finding_says_why_and_offers_once_it_is_settled(ready):
    record = _record()
    record.gearbox.static_reason = STATIC_REASON
    assert _clean(ui_text.motion_record_line(record, offer=False)) == (
        "It was built static. How a gear is mated to its shaft's axis is not settled by the probes for this version "
        "(findings.AXIS_MATE_ROUTE).")
    f = _footer(ready, record=record, plan=dataclasses.replace(_again(), motion=_motion()), update=_update())
    assert f.text.endswith(
        "re-place G2, G3 and G4. It was built static. How a gear is mated to its shaft's axis is not settled by the "
        "probes for this version (findings.AXIS_MATE_ROUTE). That is settled now, so Build again… makes a new "
        "revision whose gears turn.")


def test_the_record_line_is_empty_with_no_gearbox_and_never_follows_an_error(ready):
    assert ui_text.motion_record_line(None) == "" and ui_text.motion_record_line(_record(layout=False)) == ""
    f = _footer(ready, record=_turning_record(), plan=_turning(), update=_update(missing=(_path("Gear_m1.5_N68"),)))
    assert not f.ok and "drag" not in f.text


def test_the_build_again_question_on_a_static_record_says_the_new_revision_turns():
    fresh = _gearbox("Reducer_12to1_r2", motion=_motion(), **FULL)
    question = ui_text.build_again_question(_update(), fresh, record=_record())
    assert _clean(question).startswith(
        "Reducer_12to1.SLDASM was built static; the new revision's gears are mated to turn. Build again as "
        "Reducer_12to1_r2? That makes new parts for G1 (Gear_m1.5_N17), ")
    update = _update(structural=("G2's bore was added, which its built part cannot take.",))
    assert ui_text.build_again_question(update, fresh, record=_record()).startswith(
        "G2's bore was added, which its built part cannot take. Reducer_12to1.SLDASM was built static; the new "
        "revision's gears are mated to turn. Build again as Reducer_12to1_r2? ")
    # A turning record, a static next revision, or no record given: W4's words.
    for record, plan in ((_turning_record(), fresh), (_record(), _gearbox("Reducer_12to1_r2", **FULL)), (None, fresh)):
        assert ui_text.build_again_question(_update(), plan, record=record).startswith(
            "Nothing on record needs a new revision. Build again as Reducer_12to1_r2? ")


def test_a_structural_edit_on_a_turning_gearbox_is_shown_as_classify_wrote_it(ready):
    """D8, answer 3 and D7 are classify's sentences (package B); the footer and the question show them whole."""
    face = ("G1's face width moves its front face off the Front plane (0 → 2 mm), and its mate along S1 has no "
            "distance to set, so it needs a new revision.")
    teeth = ("G2's teeth changed from 68 to 69, and the gear mate G1 meshes G2 still turns at 17 : 68: Update "
             "SolidWorks cannot change a gear mate's ratio, so it needs a new revision.")
    update = _update(structural=(face, teeth))
    f = _footer(ready, record=_turning_record(), plan=dataclasses.replace(_again(), motion=_motion()), update=update)
    assert _clean(f.text) == (
        "G1's face width moves its front face off the Front plane (0 → 2 mm), and its mate along S1 has no distance "
        "to set, so it needs a new revision (and 1 other change Update SolidWorks cannot carry). Update SolidWorks "
        "offers to build again as Reducer_12to1_r2. It was built with its gears mated to turn: drag G1 in "
        "SolidWorks and the rest of its train follow.")
    question = ui_text.build_again_question(update, _again(), record=_turning_record())
    assert question.startswith(f"{face} {teeth} Build again as Reducer_12to1_r2? ")


# before Update SolidWorks, and after, on a turning gearbox


def _motion_update(plan=None, **changes):
    refs = tuple(swbuild.MateRef(m.name, m.kind, m.gears, m.shaft) for m in (plan or _motion()).mates)
    motion = swbuild.MotionUpdate(mates=refs, locks=(swbuild.LockLink("G2", "G3", 0.0),),
                                  meshes=(swbuild.MeshLink("G1", "G2", -0.25, 5.294),
                                          swbuild.MeshLink("G3", "G4", -1 / 3, 7.059)),
                                  ratios=(("G1 meshes G2", 17, 69), ("G3 meshes G4", 17, 52)))
    fields = dict(motion=motion, parts=(), layout=None, moved_shafts=(), replaced=())
    fields.update(changes)
    return _update(**fields)


ASM = _path("Reducer_12to1", ".SLDASM")


def _moved(**values):
    fields = dict(parts=[], layout=None, placed=[], rebuilt=True, changed=[])
    fields.update(values)
    return swbuild.GearboxUpdate(**fields)


def test_the_update_summary_names_a_move_along_a_shaft_and_a_new_ratio():
    # A put on G4 puts every mated gear of its train (review M1), so the summary names them all, as the result will.
    assert ui_text.update_summary(_motion_update(axial=("G4",), replaced=("G4",))) == (
        "Update SolidWorks will move G4 along S3, and re-place G1, G2, G3 and G4.")
    both = _motion_update(axial=("G2", "G4"), ratios=("G1 meshes G2",), replaced=("G2", "G3", "G4"),
                          moved_shafts=("S2",), layout=swbuild.DocumentValues(_path("Reducer_12to1_Layout")))
    assert _clean(ui_text.update_summary(both)) == (
        "Update SolidWorks will move S2 in Reducer_12to1_Layout, move G2 along S2 and G4 along S3, set the gear mate "
        "G1 meshes G2 to 17 : 69, and re-place G1, G2, G3 and G4.")
    # A gear mate given a new ratio is put with its train, whatever frames change.
    two = _motion_update(ratios=("G1 meshes G2", "G3 meshes G4"))
    assert ui_text.update_summary(two) == (
        "Update SolidWorks will set the gear mates G1 meshes G2 to 17 : 69 and G3 meshes G4 to 17 : 52, and re-place "
        "G1, G2, G3 and G4.")


def _summary_motion(plan, **changes):
    """A turning update whose links come from ``plan``'s mates, as classify makes them."""
    refs = tuple(swbuild.MateRef(m.name, m.kind, m.gears, m.shaft) for m in plan.mates)
    meshes = tuple(swbuild.MeshLink(m.gears[0], m.gears[1], -1.0, 5.0) for m in plan.mates if m.kind == "mesh")
    locks = tuple(swbuild.LockLink(m.gears[0], m.gears[1], 0.0) for m in plan.mates if m.kind == "lock")
    fields = dict(motion=swbuild.MotionUpdate(mates=refs, meshes=meshes, locks=locks), parts=(), layout=None,
                  moved_shafts=(), replaced=())
    fields.update(changes)
    return _update(**fields)


def test_the_summary_names_each_train_it_must_put_and_only_those():
    plan = TWO_TRAINS                    # G1-G4 one train (G3 locked to G2), G5-G6 the other
    placements = tuple(swbuild.Placement(g, f"{g}-1", (1, 0, 0, 0, 1, 0, 0, 0, 1), (0, 0, 0))
                       for g in ("G6", "G5", "G4", "G3", "G2", "G1"))
    one = _summary_motion(plan, replaced=("G5",))
    assert ui_text.update_summary(one) == "Update SolidWorks will re-place G5 and G6."
    ordered = _summary_motion(plan, replaced=("G5",), placements=placements)
    assert ui_text.update_summary(ordered) == "Update SolidWorks will re-place G6 and G5."      # placements order
    both = _summary_motion(plan, replaced=("G3", "G6"))
    assert ui_text.update_summary(both) == "Update SolidWorks will re-place G1, G2, G3, G4, G5 and G6."
    # A gear on a shaft that meshes nothing is a train of its own; a fixed gear (on no mate) is named as it is.
    lone = _turning(extra_shafts={"S4": "G7"}, locks=(("G2", "G3"), ("G7", "G8"))).motion
    assert ui_text.update_summary(_summary_motion(lone, replaced=("G7", "G9"))) == (
        "Update SolidWorks will re-place G7, G8 and G9.")
    assert ui_text.update_summary(_summary_motion(lone, replaced=("G10", "G2"))) == (
        "Update SolidWorks will re-place G1, G2, G3, G4 and G10.")
    # A static gearbox: W4's words, the gears whose frames differ.
    assert ui_text.update_summary(_update(parts=(), moved_shafts=(), replaced=("G4",))) == (
        "Update SolidWorks will re-place G4.")


def test_after_update_a_train_that_had_to_move_is_said_to_be_back_at_its_built_turn():
    """Answer 2 and D4: when Update had to put a train, it put every mated gear of it back to the built turn."""
    result = _moved(placed=["G1", "G2", "G3", "G4"], changed=[ASM], restored=[("G1", "G2", "G3", "G4")],
                    layout=swbuild.UpdateResult(document="Reducer_12to1_Layout.SLDPRT", changed=["S2 X"], rebuilt=True))
    update = _motion_update(moved_shafts=("S2",), layout=swbuild.DocumentValues(_path("Reducer_12to1_Layout")))
    assert _clean(ui_text.gearbox_update_status(update, result)[0]) == (
        "Updated SolidWorks: moved S2 in Reducer_12to1_Layout, re-placed G1, G2, G3 and G4; no interference between "
        "the gears where they stand. G1, G2, G3 and G4 had been turned in SolidWorks; their train is back at the turn "
        "it was built at. Save Reducer_12to1 in SolidWorks to keep it.")
    one = _moved(placed=["G1", "G2"], changed=[ASM], restored=[("G2",)])
    assert "G2 had been turned in SolidWorks; its train is back at the turn it was built at." in \
        ui_text.gearbox_update_status(_motion_update(), one)[0]


TWO_TRAINS = _motion(trains=(("S1", "S2", "S3"), ("S4", "S5")), drag=("G1", "G5"),
                     extra_shafts={"S4": "G5", "S5": "G6"},
                     meshes=(("G1", "G2", 17, 68), ("G3", "G4", 17, 51), ("G5", "G6", 20, 40)))


def test_two_trains_where_only_one_was_put_name_only_that_train():
    """The first train had to move (G4 along S3) and is said to be back; the second, which the user also turned,
    was not put: which one stayed turned cannot be told from the result, so the sentence says it of any gear not
    put back, and never names "the gears" as if all were back."""
    result = _moved(placed=["G1", "G2", "G3", "G4"], changed=[ASM], turned=True, restored=[("G1", "G2", "G3", "G4")],
                    axial=["G4"])
    text, ok = ui_text.gearbox_update_status(_motion_update(TWO_TRAINS), result)
    assert (_clean(text), ok) == (
        "Updated SolidWorks: moved G4 along S3, re-placed G1, G2, G3 and G4; no interference between the gears where "
        "they stand. G1, G2, G3 and G4 had been turned in SolidWorks; their train is back at the turn it was built "
        "at. Any gear it did not put back stands where it was turned in SolidWorks. Save Reducer_12to1 in SolidWorks "
        "to keep it.", True)
    assert "G5" not in text and "G6" not in text
    # Both trains put: nothing stands turned, so nothing more is said.
    every = _moved(placed=["G1", "G2", "G3", "G4", "G5", "G6"], changed=[ASM], turned=True,
                   restored=[("G1", "G2", "G3", "G4"), ("G5", "G6")])
    assert ui_text.gearbox_update_status(_motion_update(TWO_TRAINS), every)[0] == (
        "Updated SolidWorks: re-placed G1, G2, G3, G4, G5 and G6; no interference between the gears where they stand. "
        "G1, G2, G3 and G4 had been turned in SolidWorks; their train is back at the turn it was built at. G5 and G6 "
        "had been turned in SolidWorks; their train is back at the turn it was built at. Save Reducer_12to1 in "
        "SolidWorks to keep it.")


def test_a_train_put_with_no_gear_turned_back_gets_no_sentence():
    put = _moved(placed=["G1", "G2", "G3", "G4"], changed=[ASM], restored=[])
    assert ui_text.gearbox_update_status(_motion_update(), put)[0] == (
        "Updated SolidWorks: re-placed G1, G2, G3 and G4; no interference between the gears where they stand. Save "
        "Reducer_12to1 in SolidWorks to keep it.")


def test_with_nothing_to_put_a_turned_train_stays_and_the_sentence_says_so():
    """W5-DECISIONS answer 2: with nothing to put, the train stays where the user turned it, said plainly."""
    turned = _moved(turned=True)
    assert ui_text.gearbox_update_status(_motion_update(), turned) == (
        "SolidWorks already matches the workbook: nothing was changed. The gears stand where they were turned in "
        "SolidWorks.", True)
    values = _moved(turned=True, parts=[swbuild.UpdateResult(document="Gear_m1.5_N68.SLDPRT", changed=["No. of Teeth"],
                                                             rebuilt=True)], changed=[_path("Gear_m1.5_N68")])
    text, _ = ui_text.gearbox_update_status(_motion_update(parts=_update().parts), values)
    assert _clean(text) == (
        "Updated SolidWorks: changed 1 variable in Gear_m1.5_N68 (it now has 69 teeth; its file keeps its name); no "
        "interference between the gears where they stand. The gears stand where they were turned in SolidWorks. Save "
        "Gear_m1.5_N68 in SolidWorks to keep it.")
    # A fixed gear re-placed (W4's rule) is no mated gear put: the train still stands as it was turned.
    fixed = _moved(turned=True, placed=["G9"], changed=[ASM])
    assert ui_text.gearbox_update_status(_motion_update(), fixed)[0] == (
        "Updated SolidWorks: re-placed G9; no interference between the gears where they stand. The gears stand where "
        "they were turned in SolidWorks. Save Reducer_12to1 in SolidWorks to keep it.")
    # Not turned: nothing about it.
    assert ui_text.gearbox_update_status(_motion_update(), _moved()) == (ui_text.ALREADY_MATCHES, True)


def test_the_summary_before_update_on_a_turning_gearbox_never_promises_to_put_a_turn_back():
    assert ui_text.update_summary(_motion_update()) == (
        "SolidWorks already matches the workbook on record; Update SolidWorks checks it live and puts right anything "
        "changed there; gears turned in SolidWorks stay where they are unless something must move.")
    assert ui_text.update_summary(_update(parts=(), moved_shafts=(), replaced=())) == (
        "SolidWorks already matches the workbook on record; Update SolidWorks checks it live and puts right anything "
        "changed there.")


def test_a_relation_out_of_step_is_said_without_guessing_which_gear_was_turned():
    result = _moved(placed=["G1", "G2", "G3", "G4"], changed=[ASM], out_of_step=[("G1", "G2"), ("G2", "G3")],
                    restored=[("G2", "G3", "G4")])
    text = _clean(ui_text.gearbox_update_status(_motion_update(), result)[0])
    assert text == (
        "Updated SolidWorks: re-placed G1, G2, G3 and G4; no interference between the gears where they stand. G1 and "
        "G2 had been turned out of step with each other in SolidWorks; they are back in mesh. G2 and G3 had been "
        "turned out of step with each other in SolidWorks; they are back in step. G2, G3 and G4 had been turned in "
        "SolidWorks; their train is back at the turn it was built at. Save Reducer_12to1 in SolidWorks to keep it.")


def test_a_gear_moved_off_its_axis_is_w4s_put_back():
    result = _moved(placed=["G1", "G2", "G3", "G4"], changed=[ASM], off_axis=["G4"])
    text, _ = ui_text.gearbox_update_status(_motion_update(), result, dragged=["G4"])
    assert text == ("Updated SolidWorks: re-placed G1, G2 and G3; no interference between the gears where they stand. "
                    "G4 had been moved in SolidWorks; put back where the workbook has it. Save Reducer_12to1 in "
                    "SolidWorks to keep it.")


def test_a_recorded_mate_found_suppressed_was_turned_back_on_and_said():
    """D10."""
    result = _moved(changed=[ASM], unsuppressed=["G1 meshes G2"])
    assert ui_text.gearbox_update_status(_motion_update(), result)[0] == (
        "Updated SolidWorks: turned the mate G1 meshes G2 back on (it was suppressed in SolidWorks); no interference "
        "between the gears where they stand. Save Reducer_12to1 in SolidWorks to keep it.")
    two = _moved(changed=[ASM], unsuppressed=["G1 meshes G2", "G3 locked to G2"], axial=["G4"],
                 ratios=["G3 meshes G4"])
    assert _clean(ui_text.gearbox_update_status(_motion_update(), two)[0]).startswith(
        "Updated SolidWorks: turned the mates G1 meshes G2 and G3 locked to G2 back on (they were suppressed in "
        "SolidWorks), moved G4 along S3, set the gear mate G3 meshes G4 to 17 : 52; no interference")


def test_mates_the_app_did_not_make_and_left_alone_are_said_even_when_nothing_changed():
    one = _moved(extra_mates=["Angle1"])
    assert ui_text.gearbox_update_status(_motion_update(), one) == (
        "SolidWorks already matches the workbook: nothing was changed. Reducer_12to1.SLDASM also has a suppressed "
        "mate the app did not make, Angle1; Update SolidWorks left it as it is.", True)
    three = _moved(changed=[ASM], placed=["G4"], extra_mates=["Angle1", "Angle2", "Distance3"])
    assert ("Reducer_12to1.SLDASM also has suppressed mates the app did not make, Angle1, Angle2 and Distance3; "
            "Update SolidWorks left them as they are. Save Reducer_12to1") in \
        _clean(ui_text.gearbox_update_status(_motion_update(), three)[0])


def test_an_unknown_mate_not_suppressed_refuses_the_update_in_the_workers_own_words():
    """M7: the worker's check phase raises a BuildError naming the mate; the window shows it as it came."""
    said = ("Reducer_12to1.SLDASM has a mate the app did not make, Angle1, and it is not suppressed: suppress Angle1 "
            "in SolidWorks and press Update SolidWorks again.")
    assert ui_text.job_failed(swbuild.BuildError(said), updating=True) == said


def test_locks_that_could_not_be_turned_back_on_are_never_hidden_behind_the_failure_before_them():
    """M8: the put fails, then the locks' unsuppress in the finally fails too; both are said, in order."""
    result = _moved(changed=[ASM], failures=[
        ("Reducer_12to1.SLDASM", "G2 would not move: Transform2 was not taken."),
        ("Reducer_12to1.SLDASM", "The compound gears G2 and G3 are not locked: press Update SolidWorks again.")])
    assert ui_text.gearbox_update_status(_motion_update(), result) == (
        "Update SolidWorks stopped. Reducer_12to1.SLDASM: G2 would not move: Transform2 was not taken. The compound "
        "gears G2 and G3 are not locked: press Update SolidWorks again. It had already changed Reducer_12to1, not "
        "saved: press Update SolidWorks again once that is put right, or save it in SolidWorks to keep what it did.",
        False)
    post = _moved(failures=[("Gear_m1.5_N68.SLDPRT", "SolidWorks reported an error rebuilding Gear_m1.5_N68."),
                            ("Reducer_12to1.SLDASM", "G4 is not where Update SolidWorks put it once the assembly "
                                                     "rebuilt: a mate holds it elsewhere.")])
    assert ui_text.gearbox_update_status(_motion_update(), post)[0] == (
        "Update SolidWorks stopped. Gear_m1.5_N68.SLDPRT: SolidWorks reported an error rebuilding Gear_m1.5_N68. "
        "Reducer_12to1.SLDASM: G4 is not where Update SolidWorks put it once the assembly rebuilt: a mate holds it "
        "elsewhere. Nothing was changed.")
    # W4's static path keeps saying the first failure only, word for word.
    assert ui_text.gearbox_update_status(_update(), post)[0] == (
        "Update SolidWorks stopped. Gear_m1.5_N68.SLDPRT: SolidWorks reported an error rebuilding Gear_m1.5_N68. "
        "Nothing was changed.")


def test_motion_update_lines_are_whole_sentences_and_empty_on_the_static_path():
    result = _moved(changed=[ASM], placed=["G1", "G2", "G3", "G4"], unsuppressed=["G1 meshes G2"], axial=["G4"],
                    ratios=["G1 meshes G2"], out_of_step=[("G1", "G2")], restored=[("G1", "G2")],
                    extra_mates=["Angle1"])
    lines = ui_text.motion_update_lines(_motion_update(), result)
    assert lines == [
        "Turned the mate G1 meshes G2 back on (it was suppressed in SolidWorks).",
        "Moved G4 along S3.",
        "Set the gear mate G1 meshes G2 to 17 : 69.",
        "G1 and G2 had been turned out of step with each other in SolidWorks; they are back in mesh.",
        "G1 and G2 had been turned in SolidWorks; their train is back at the turn it was built at.",
        "Reducer_12to1.SLDASM also has a suppressed mate the app did not make, Angle1; Update SolidWorks left it as "
        "it is."]
    for line in lines:
        assert _clean(line)[0].isupper() and line.endswith(".")
    assert ui_text.motion_update_lines(_update(), result) == []


def test_a_static_gearboxs_update_reads_exactly_as_in_w4_whatever_the_result_carries():
    result = _updated(restored=[("G2",)], unsuppressed=["X"], extra_mates=["Angle1"], turned=True)
    assert ui_text.gearbox_update_status(_update(), result) == (
        "Updated SolidWorks: changed 1 variable in Gear_m1.5_N68 (it now has 69 teeth; its file keeps its name), "
        "moved S2 and S3 in Reducer_12to1_Layout, re-placed G2, G3 and G4; no interference between the gears. Save "
        "Gear_m1.5_N68, Reducer_12to1_Layout and Reducer_12to1 in SolidWorks to keep them.", True)


def test_no_w5_sentence_says_fallback_or_static_instead():
    """W5-DECISIONS answer 1: there is no static fallback, so nothing anywhere speaks of one."""
    import inspect
    source = inspect.getsource(ui_text)
    for phrase in ("static instead", "fallback record", "tries again as a new revision", "would not mate them",
                   "close it without saving"):
        assert phrase not in source


# what the Workbook window found (package D): the question after a refusal, the header after a refused mate


BAD_MATE_REFUSAL = ("gearbox.mates[3] on record is a mesh mate with 1 gear, so Update SolidWorks cannot act on the "
                    "gearbox the record describes: Build again… makes a new revision from the workbook instead.")


def test_the_build_again_question_gives_classifys_refusal_as_its_reason(ready):
    question = ui_text.build_again_question(_update(refusal=BAD_MATE_REFUSAL), _again(), record=_turning_record())
    assert question.startswith(f"{BAD_MATE_REFUSAL} Build again as Reducer_12to1_r2? That makes a new part for G2 ")
    assert "Nothing on record needs a new revision" not in question
    f = _footer(ready, record=_turning_record(), plan=_again(), update=_update(refusal=BAD_MATE_REFUSAL))
    assert f.text == BAD_MATE_REFUSAL and f.build_enabled


def test_the_header_after_a_refused_mate_compares_with_the_read_the_refusal_came_from():
    record = _refused_record(digest="d1")
    record.digest = ""                          # no assembly was built, so no build read is on record
    assert ui_text.workbook_built_tag(record, "d1") == " · its assembly was refused for this version"
    assert ui_text.workbook_built_tag(record, "d2") == " · changed since its assembly was refused"
    assert ui_text.workbook_built_tag(record, "") == ""
    unknown = _refused_record(digest="")
    assert ui_text.workbook_built_tag(unknown, "d1") == ""
    blank = _refused_record(digest="d1", problems=(" ",))
    blank.digest = ""
    assert ui_text.workbook_built_tag(blank, "d1") == " · changed since it was built"     # W4's, unchanged
    built = _turning_record()
    built.digest = "d1"
    assert ui_text.workbook_built_tag(built, "d1") == " · built from this version"
    assert ui_text.workbook_built_tag(built, "d2") == " · changed since it was built"


# an Update after an earlier one whose changes to the assembly were never saved (package B's Finished fields)


def _finished(earlier, off=(), pairs=()):
    from gear_generator.workbook.gearbox import Finished
    return Finished(earlier_update=earlier, off_after_update=list(off), out_of_step_after_update=list(pairs))


PLACED = tuple(swbuild.Placement(g, f"{g}-1", (1, 0, 0, 0, 1, 0, 0, 0, 1), (0, 0, 0)) for g in ("G1", "G2", "G3", "G4"))


def test_after_a_lost_update_its_changes_are_said_to_be_made_again_never_moved_by_the_user():
    from gear_generator.workbook.gearbox import UPDATE_LOST
    result = _moved(placed=["G1", "G2", "G3", "G4"], changed=[ASM], axial=["G4"])
    text, ok = ui_text.gearbox_update_status(_motion_update(placements=PLACED), result,
                                             finished=_finished(UPDATE_LOST, off=["G4"]))
    assert (_clean(text), ok) == (
        "Updated SolidWorks: moved G4 along S3, re-placed G1, G2, G3 and G4; no interference between the gears where "
        "they stand. The last Update SolidWorks was not saved before Reducer_12to1.SLDASM was closed, so its changes "
        "were made again: G4 is back where the workbook has it. Save Reducer_12to1 in SolidWorks to keep it.", True)
    assert "had been" not in text
    pairs = _moved(placed=["G1", "G2", "G3", "G4"], changed=[ASM], out_of_step=[("G2", "G3")],
                   restored=[("G3", "G4")])
    text, _ = ui_text.gearbox_update_status(_motion_update(placements=PLACED), pairs,
                                            finished=_finished(UPDATE_LOST, pairs=[("G2", "G3")]))
    assert "made again: G3 and G4 are back where the workbook has them; G2 and G3 are back in step with each " \
           "other. Save" in _clean(text) and "out of step" not in text and "had been" not in text
    nothing_off = _moved(placed=["G4"], changed=[ASM])
    assert ui_text.gearbox_update_status(_motion_update(), nothing_off, finished=_finished(UPDATE_LOST))[0] == (
        "Updated SolidWorks: re-placed G4; no interference between the gears where they stand. The last Update "
        "SolidWorks was not saved before Reducer_12to1.SLDASM was closed, so its changes were made again. Save "
        "Reducer_12to1 in SolidWorks to keep it.")


def test_after_an_update_not_saved_neither_finishing_nor_stopping_is_claimed_and_the_user_is_never_blamed():
    """The record cannot tell whether that Update finished or stopped part way: neither is said."""
    from gear_generator.workbook.gearbox import UPDATE_NOT_SAVED
    result = _moved(placed=["G1", "G2", "G3", "G4"], changed=[ASM], out_of_step=[("G2", "G3")],
                    restored=[("G3",)], turned=True)
    text, ok = ui_text.gearbox_update_status(_motion_update(placements=PLACED), result,
                                             finished=_finished(UPDATE_NOT_SAVED, off=["G4"], pairs=[("G2", "G3")]))
    assert (_clean(text), ok) == (
        "Updated SolidWorks: re-placed G1, G2, G3 and G4; no interference between the gears where they stand. G3 and "
        "G4 were not where the last Update SolidWorks, which is not saved, has them on record; they are in place "
        "again. G2 and G3 were not in step as that Update has them on record either; they are in step again. Save "
        "Reducer_12to1 in SolidWorks to keep it.", True)
    for blame in ("had been", "turned in SolidWorks", "moved in SolidWorks", "stopped", "finished"):
        assert blame not in text
    one = _moved(placed=["G1", "G2", "G3", "G4"], changed=[ASM])
    assert ui_text.gearbox_update_status(_motion_update(), one, finished=_finished(UPDATE_NOT_SAVED, off=["G4"]))[0] \
        .endswith("stand. G4 was not where the last Update SolidWorks, which is not saved, has it on record; it is in "
                  "place again. Save Reducer_12to1 in SolidWorks to keep it.")
    two_pairs = _moved(placed=["G1", "G2", "G3", "G4"], changed=[ASM], out_of_step=[("G1", "G2"), ("G2", "G3")])
    assert ("stand. G1 with G2 and G2 with G3 were not in step as the last Update SolidWorks, which is not saved, has "
            "them on record; they are in step again. Save") in ui_text.gearbox_update_status(
        _motion_update(), two_pairs, finished=_finished(UPDATE_NOT_SAVED, pairs=[("G1", "G2"), ("G2", "G3")]))[0]
    # Gears left standing are as they were found, never "where they were turned".
    standing = _moved(turned=True, parts=[swbuild.UpdateResult(document="Gear_m1.5_N68.SLDPRT",
                                                               changed=["No. of Teeth"], rebuilt=True)],
                      changed=[_path("Gear_m1.5_N68")])
    text, _ = ui_text.gearbox_update_status(_motion_update(parts=_update().parts), standing,
                                            finished=_finished(UPDATE_NOT_SAVED))
    assert "The gears stand as they were found in SolidWorks." in text and "where they were turned" not in text
    nothing = _moved(turned=True)
    assert ui_text.gearbox_update_status(_motion_update(), nothing, finished=_finished(UPDATE_NOT_SAVED)) == (
        "SolidWorks already matches the workbook: nothing was changed. The gears stand as they were found in "
        "SolidWorks.", True)


def test_a_static_gearbox_after_an_earlier_update_says_the_same_and_never_had_been_moved():
    from gear_generator.workbook.gearbox import UPDATE_LOST, UPDATE_NOT_SAVED
    result = _updated(placed=["G2", "G3", "G4"])
    lost, _ = ui_text.gearbox_update_status(_update(), result, finished=_finished(UPDATE_LOST, off=["G4"]))
    assert lost == (
        "Updated SolidWorks: changed 1 variable in Gear_m1.5_N68 (it now has 69 teeth; its file keeps its name), "
        "moved S2 and S3 in Reducer_12to1_Layout, re-placed G2, G3 and G4; no interference between the gears. The "
        "last Update SolidWorks was not saved before Reducer_12to1.SLDASM was closed, so its changes were made again: "
        "G4 is back where the workbook has it. Save Gear_m1.5_N68, Reducer_12to1_Layout and Reducer_12to1 in "
        "SolidWorks to keep them.")
    kept, _ = ui_text.gearbox_update_status(_update(), result, finished=_finished(UPDATE_NOT_SAVED, off=["G3", "G4"]))
    assert "gears. G3 and G4 were not where the last Update SolidWorks, which is not saved, has them on record; they " \
           "are in place again. Save" in kept and "had been moved" not in kept


def test_with_no_earlier_update_every_update_sentence_is_as_before():
    result = _moved(placed=["G1", "G2", "G3", "G4"], changed=[ASM], out_of_step=[("G1", "G2")],
                    restored=[("G1", "G2")])
    plain = ui_text.gearbox_update_status(_motion_update(), result)
    assert ui_text.gearbox_update_status(_motion_update(), result, finished=_finished("")) == plain
    assert "G1 and G2 had been turned out of step with each other in SolidWorks" in plain[0]
    static = ui_text.gearbox_update_status(_update(), _updated(), dragged=["G4"], finished=_finished(""))
    assert static == ui_text.gearbox_update_status(_update(), _updated(), dragged=["G4"])


# gear mates judged by their live ratio (package A, ba2bc1f)


def test_a_gear_mate_found_at_another_ratio_is_said_to_be_set_back_never_given_a_new_ratio():
    """``ratios_found``: no change was asked, SolidWorks held another ratio; the ratio it held is not in the result,
    so it is not named."""
    result = _moved(placed=["G1", "G2", "G3", "G4"], changed=[ASM], ratios=["G1 meshes G2"],
                    ratios_found=["G1 meshes G2"])
    text, ok = ui_text.gearbox_update_status(_motion_update(ratios=()), result)
    assert (_clean(text), ok) == (
        "Updated SolidWorks: set the gear mate G1 meshes G2 back to the workbook's ratio, which SolidWorks held at "
        "another, re-placed G1, G2, G3 and G4; no interference between the gears where they stand. Save "
        "Reducer_12to1 in SolidWorks to keep it.", True)
    assert "new ratio" not in text
    both = _moved(placed=["G1", "G2", "G3", "G4"], changed=[ASM], ratios=["G1 meshes G2", "G3 meshes G4"],
                  ratios_found=["G3 meshes G4"])
    assert ui_text.gearbox_update_status(_motion_update(), both)[0].startswith(
        "Updated SolidWorks: set the gear mate G1 meshes G2 to 17 : 69, set the gear mate G3 meshes G4 back to the "
        "workbook's ratio, which SolidWorks held at another, re-placed")
    two = _moved(changed=[ASM], ratios=["G1 meshes G2", "G3 meshes G4"], ratios_found=["G1 meshes G2", "G3 meshes G4"])
    assert "set the gear mates G1 meshes G2 and G3 meshes G4 back to the workbook's ratios, which SolidWorks held at " \
           "another;" in ui_text.gearbox_update_status(_motion_update(), two)[0]


def test_a_gear_mate_already_at_the_asked_ratio_is_said_so_after_the_summary_promised_the_set():
    """``ratios_already``: the summary said *set the gear mate … to 17 : 69*; after the press it says it was already
    so, rather than a bare *nothing was changed*."""
    update = _motion_update(ratios=("G1 meshes G2",))
    assert ui_text.update_summary(update) == (
        "Update SolidWorks will set the gear mate G1 meshes G2 to 17 : 69, and re-place G1, G2, G3 and G4.")
    result = _moved(ratios_already=["G1 meshes G2"])
    assert ui_text.gearbox_update_status(update, result) == (
        "SolidWorks already matches the workbook: nothing was changed. The gear mate G1 meshes G2 was already 17 : 69 "
        "in SolidWorks, so it was left as it is.", True)
    two = _moved(ratios_already=["G1 meshes G2", "G3 meshes G4"], changed=[ASM], placed=["G4"])
    assert ("The gear mates G1 meshes G2 and G3 meshes G4 were already 17 : 69 and 17 : 52 in SolidWorks, so they "
            "were left as they are. Save") in _clean(ui_text.gearbox_update_status(_motion_update(), two)[0])
    unknown = _moved(ratios_already=["G9 meshes G10"])
    assert ui_text.gearbox_update_status(_motion_update(), unknown)[0].endswith(
        "The gear mate G9 meshes G10 was already at the ratio the workbook wants in SolidWorks, so it was left as it "
        "is.")


def test_after_a_lost_update_that_needed_nothing_making_again_it_never_says_made_again():
    from gear_generator.workbook.gearbox import UPDATE_LOST
    nothing = _moved()
    assert ui_text.gearbox_update_status(_motion_update(), nothing, finished=_finished(UPDATE_LOST)) == (
        "SolidWorks already matches the workbook: nothing was changed. The last Update SolidWorks was not saved before "
        "Reducer_12to1.SLDASM was closed; SolidWorks already holds the workbook as it now is, so nothing needed making "
        "again.", True)
    static = _updated(parts=[], layout=None, placed=[], changed=[])
    text, _ = ui_text.gearbox_update_status(_update(), static, finished=_finished(UPDATE_LOST))
    assert "made again" not in text and text.endswith("so nothing needed making again.")
    changed = _moved(placed=["G4"], changed=[ASM])
    assert "so its changes were made again" in ui_text.gearbox_update_status(
        _motion_update(), changed, finished=_finished(UPDATE_LOST))[0]


def test_after_a_lost_update_with_a_part_still_in_error_it_never_says_solidworks_holds_the_workbook():
    """The re-check's note under N4: a press that changed nothing, beside a part an earlier stop left in error, says
    the part is still in error and never also that SolidWorks holds the workbook as it now is."""
    from dataclasses import replace
    from gear_generator.workbook.gearbox import UPDATE_LOST
    finished = replace(_finished(UPDATE_LOST), still_in_error=["C:\\Out\\Gear_m1.5_N68.SLDPRT"])
    text, ok = ui_text.gearbox_update_status(_motion_update(), _moved(), finished=finished)
    assert not ok and text == (
        ui_text.still_in_error_sentence(finished.still_in_error) + " The last Update SolidWorks was not saved before "
        "Reducer_12to1.SLDASM was closed."), text


def test_a_gear_mate_ratio_that_cannot_be_given_refuses_the_update_in_the_workers_own_words():
    said = ("The gear mate G1 meshes G2 in T.SLDASM is at 17 : 68 and the workbook wants 17 : 69, and giving a gear "
            "mate a new ratio has not been settled on SolidWorks (findings.GEAR_MATE_RATIO_ROUTE is None), so nothing "
            "is changed; build the gearbox again.")
    assert ui_text.job_failed(swbuild.BuildError(said), updating=True) == said


def test_the_summary_names_the_whole_train_for_a_face_z_set_or_a_shaft_moved_under_it():
    assert ui_text.update_summary(_motion_update(axial=("G4",))) == (
        "Update SolidWorks will move G4 along S3, and re-place G1, G2, G3 and G4.")
    shaft = _motion_update(moved_shafts=("S3",), layout=swbuild.DocumentValues(_path("Reducer_12to1_Layout")))
    assert ui_text.update_summary(shaft) == (
        "Update SolidWorks will move S3 in Reducer_12to1_Layout, and re-place G1, G2, G3 and G4.")
    lone = _turning(extra_shafts={"S4": "G7"}, locks=(("G2", "G3"), ("G7", "G8"))).motion
    moved = _summary_motion(lone, moved_shafts=("S4",), layout=swbuild.DocumentValues(_path("Reducer_12to1_Layout")))
    assert ui_text.update_summary(moved) == (
        "Update SolidWorks will move S4 in Reducer_12to1_Layout, and re-place G7 and G8.")


def test_a_gear_mate_set_back_names_both_ratios_from_what_the_worker_read():
    """``ratios_read`` (package A, ceb6433): the ratio SolidWorks held and the one it was set back to."""
    result = _moved(placed=["G1", "G2", "G3", "G4"], changed=[ASM], ratios=["G1 meshes G2"],
                    ratios_found=["G1 meshes G2"], ratios_read=[("G1 meshes G2", 17, 68, 17, 69)])
    text, ok = ui_text.gearbox_update_status(_motion_update(ratios=()), result)
    assert (_clean(text), ok) == (
        "Updated SolidWorks: set the gear mate G1 meshes G2 back to 17 : 69 (SolidWorks held it at 17 : 68), "
        "re-placed G1, G2, G3 and G4; no interference between the gears where they stand. Save Reducer_12to1 in "
        "SolidWorks to keep it.", True)
    two = _moved(changed=[ASM], placed=["G1", "G2", "G3", "G4"], ratios=["G1 meshes G2", "G3 meshes G4"],
                 ratios_found=["G1 meshes G2", "G3 meshes G4"],
                 ratios_read=[("G1 meshes G2", 17, 68, 17, 69), ("G3 meshes G4", 17, 51, 17, 52)])
    assert ui_text.gearbox_update_status(_motion_update(ratios=()), two)[0].startswith(
        "Updated SolidWorks: set the gear mates G1 meshes G2 back to 17 : 69 (SolidWorks held it at 17 : 68) and G3 "
        "meshes G4 back to 17 : 52 (SolidWorks held it at 17 : 51), re-placed G1, G2, G3 and G4;")
    # One read, one not: each said as far as the result knows.
    mixed = _moved(changed=[ASM], ratios=["G1 meshes G2", "G3 meshes G4"],
                   ratios_found=["G1 meshes G2", "G3 meshes G4"], ratios_read=[("G1 meshes G2", 17, 68, 17, 69)])
    assert ui_text.gearbox_update_status(_motion_update(ratios=()), mixed)[0].startswith(
        "Updated SolidWorks: set the gear mate G1 meshes G2 back to 17 : 69 (SolidWorks held it at 17 : 68), set the "
        "gear mate G3 meshes G4 back to the workbook's ratio, which SolidWorks held at another;")


def test_a_remake_that_failed_is_never_said_to_be_set():
    """The read stays when the remake then fails, and ``ratios`` does not list the mate: no ratio is said to be set,
    and the job's failure is what the sentence says."""
    failed = _moved(changed=[ASM], ratios=[], ratios_found=["G1 meshes G2"],
                    ratios_read=[("G1 meshes G2", 17, 68, 17, 69)],
                    failures=[("Reducer_12to1.SLDASM", "The gear mate G1 meshes G2 could not be made again.")])
    text, ok = ui_text.gearbox_update_status(_motion_update(ratios=()), failed)
    assert not ok and "set the gear mate" not in text and "17 : 69" not in text
    assert ui_text.motion_update_lines(_motion_update(ratios=()), _moved(
        ratios_found=["G1 meshes G2"], ratios_read=[("G1 meshes G2", 17, 68, 17, 69)])) == []


def test_a_gear_mate_already_right_takes_its_ratio_from_what_the_worker_read():
    result = _moved(ratios_already=["G9 meshes G10"], ratios_read=[("G9 meshes G10", 20, 60, 20, 60)])
    assert ui_text.gearbox_update_status(_motion_update(), result) == (
        "SolidWorks already matches the workbook: nothing was changed. The gear mate G9 meshes G10 was already 20 : 60 "
        "in SolidWorks, so it was left as it is.", True)


# which way each gear mate turns (packages A and B: a0d5fad, 7dbc10f)


def test_a_gear_mate_found_turning_the_wrong_way_is_said_to_be_turned_the_right_way_round():
    """``sense_found_wrong`` (found wrong and remade; package A, b4d4bdd): the gearbox turned wrongly before this
    Update and does not now. Remade for that alone it is not in ``ratios``, and is said as a turn round, never a new
    ratio and never "nothing was changed"; one whose ratio changed too is said once, both in one piece."""
    unasked = _motion_update()
    unasked = dataclasses.replace(unasked, motion=dataclasses.replace(unasked.motion, ratios=()))
    only = _moved(changed=[ASM], sense_found_wrong=["G1 meshes G2"], placed=["G1", "G2", "G3", "G4"])
    text, ok = ui_text.gearbox_update_status(unasked, only)
    assert (_clean(text), ok) == (
        "Updated SolidWorks: turned the gear mate G1 meshes G2 the right way round (SolidWorks held it turning against "
        "its mesh), re-placed G1, G2, G3 and G4; no interference between the gears where they stand. Save "
        "Reducer_12to1 in SolidWorks to keep it.", True)
    assert "ratio" not in text and ui_text.ALREADY_MATCHES not in text
    assert ui_text.gearbox_update_status(_motion_update(), only)[0] == text      # a ratio asked elsewhere: the same
    two = _moved(changed=[ASM], sense_found_wrong=["G1 meshes G2", "G3 meshes G4"])
    assert "turned the gear mates G1 meshes G2 and G3 meshes G4 the right way round (SolidWorks held them turning " \
           "against their meshes);" in _clean(ui_text.gearbox_update_status(unasked, two)[0])
    # Its ratio changed as the plan asked, and it was found wrong: one piece, the mate named once.
    asked = _moved(changed=[ASM], ratios=["G1 meshes G2"], sense_found_wrong=["G1 meshes G2"])
    text = _clean(ui_text.gearbox_update_status(_motion_update(), asked)[0])
    assert text.startswith(
        "Updated SolidWorks: set the gear mate G1 meshes G2 to 17 : 69 and turned it the right way round (SolidWorks "
        "held it turning against its mesh); no interference")
    assert text.count("G1 meshes G2") == 1
    both = _moved(changed=[ASM], ratios=["G1 meshes G2", "G3 meshes G4"], sense_found_wrong=["G3 meshes G4"])
    assert ui_text.gearbox_update_status(_motion_update(), both)[0].startswith(
        "Updated SolidWorks: set the gear mate G1 meshes G2 to 17 : 69, set the gear mate G3 meshes G4 to 17 : 52 and "
        "turned it the right way round (SolidWorks held it turning against its mesh); no interference")
    # Found at another ratio though none was asked, and wrong: the set-back piece says both.
    lost = _moved(changed=[ASM], ratios=["G1 meshes G2"], ratios_found=["G1 meshes G2"],
                  ratios_read=[("G1 meshes G2", 17, 68, 17, 69)], sense_found_wrong=["G1 meshes G2"])
    text = _clean(ui_text.gearbox_update_status(unasked, lost)[0])
    assert text.startswith("Updated SolidWorks: set the gear mate G1 meshes G2 back to 17 : 69 (SolidWorks held it at "
                           "17 : 68, turning against its mesh); no interference")
    assert text.count("G1 meshes G2") == 1
    unread = _moved(changed=[ASM], ratios=["G1 meshes G2"], ratios_found=["G1 meshes G2"],
                    sense_found_wrong=["G1 meshes G2"])
    assert ui_text.gearbox_update_status(unasked, unread)[0].startswith(
        "Updated SolidWorks: set the gear mate G1 meshes G2 back to the workbook's ratio, which SolidWorks held at "
        "another, turning against its mesh; no interference")
    # A ratio change alone reads as before.
    plain = _moved(changed=[ASM], ratios=["G1 meshes G2"])
    assert ui_text.gearbox_update_status(_motion_update(), plain)[0].startswith(
        "Updated SolidWorks: set the gear mate G1 meshes G2 to 17 : 69; no interference")
    # A remake that failed is a failure: the stopped sentence, never put right.
    failed = _moved(sense_found_wrong=["G1 meshes G2"], failures=[("Reducer_12to1.SLDASM", "It would not remake.")])
    assert "right way round" not in ui_text.gearbox_update_status(unasked, failed)[0]


def test_a_gear_mate_the_app_made_again_the_other_way_round_is_not_said_and_changes_no_sentence():
    """``turned_round`` (Build and Update): the app doing its job; nothing is said, and nothing counts mates made."""
    build = _built(assembly=_saved("Reducer_12to1", ".SLDASM", turned_round=["G3 meshes G4"]))
    assert ui_text.gearbox_status(_turning(), build) == ui_text.gearbox_status(_turning(), _built())
    remade = _moved(changed=[ASM], ratios=["G1 meshes G2"], turned_round=["G1 meshes G2"], placed=["G1", "G2"])
    plain = _moved(changed=[ASM], ratios=["G1 meshes G2"], placed=["G1", "G2"])
    assert ui_text.gearbox_update_status(_motion_update(), remade) == \
        ui_text.gearbox_update_status(_motion_update(), plain)


def test_the_workers_sense_stops_read_whole_in_the_refused_build_and_the_stopped_update():
    """A's stop sentences reach the user through the refused-mate wording, whole; the same workbook would make the
    same mates, so "Build is available again once the workbook changes" stays true."""
    either = ("SolidWorks turns the gears of the mate G3 meshes G4 against the way they mesh, whichever way round the "
              "mate is made.")
    text, ok = ui_text.gearbox_status(_turning(), _refused(either))
    assert (_clean(text), ok) == (
        "Built 4 parts and Reducer_12to1_Layout; no assembly was saved, because SolidWorks found a problem with its "
        f"mates. {either} The parts and the layout part are kept. The assembly is left open in SolidWorks as Assem1, "
        "not saved; its parts are the saved ones. Build is available again once the workbook changes: the same "
        "workbook would make the same mates.", False)
    axes = ("SolidWorks reads the axes of the gear mate G3 meshes G4 as pointing the same way, but G3 and G4 sit on "
            "shafts pointing opposite ways, so the mate does not hold the axes the gears were placed on, and nothing "
            "is guessed.")
    assert f"its mates. {axes} The parts" in ui_text.gearbox_status(_turning(), _refused(axes))[0]
    stopped = _moved(changed=[ASM], failures=[("Reducer_12to1.SLDASM", "SolidWorks turns the gears of the mate G1 "
                                               "meshes G2 against the way they mesh, whichever way round it is made; "
                                               "the saved Reducer_12to1.SLDASM still has it as it was: close "
                                               "Reducer_12to1.SLDASM in SolidWorks without saving to bring it back.")])
    assert ui_text.gearbox_update_status(_motion_update(), stopped)[0] == (
        "Update SolidWorks stopped. Reducer_12to1.SLDASM: SolidWorks turns the gears of the mate G1 meshes G2 against "
        "the way they mesh, whichever way round it is made; the saved Reducer_12to1.SLDASM still has it as it was: "
        "close Reducer_12to1.SLDASM in SolidWorks without saving to bring it back. It had already changed "
        "Reducer_12to1, not saved: press Update SolidWorks again once that is put right, or save it in SolidWorks to "
        "keep what it did.")


# -- W6: right-angle (W6-PLAN §2.9, as W6-INTERFACES §7 rules) -------------------------------------------------------

from types import SimpleNamespace  # noqa: E402

from gear_generator.workbook import kinematics  # noqa: E402


def _held_together(lines):
    """No ordinary space inside a number and its unit, or inside a slant's vector: a wrapped line breaks only
    between its parts (the window wraps the Speeds lines at the end view's width)."""
    for line in lines:
        assert not re.search(r"\d (rpm|N·m)", line), line
        for vector in re.findall(r"\([^)]*\)", line):
            assert " " not in vector, line


def _speeds_spec(*ids):
    return SimpleNamespace(shafts=[SimpleNamespace(id=i) for i in ids])


def test_the_speeds_panel_on_z_shafts_reads_as_w3():
    from fractions import Fraction
    motion = kinematics.Motion(speeds={"S1": Fraction(1500), "S2": Fraction(-375), "S3": Fraction(125)},
                               torques={"S1": 10.0, "S2": 39.2, "S3": 115.248}, axis_sign={"S1": 1, "S2": 1, "S3": -1},
                               seen_from={"S1": "+Z", "S2": "+Z", "S3": "+Z"})
    lines, readout = ui_text.workbook_speed_lines(_speeds_spec("S1", "S2", "S3"), motion)
    assert lines == ["S1    1500.0\u00a0rpm anticlockwise · 10.00\u00a0N·m",
                     "S2    375.0\u00a0rpm clockwise · 39.20\u00a0N·m",
                     "S3    125.0\u00a0rpm clockwise · 115.25\u00a0N·m"]
    assert readout == "seen from +Z"
    motion.seen_from = {}                                   # before planning fills it: the same
    assert ui_text.workbook_speed_lines(_speeds_spec("S1", "S2", "S3"), motion) == (lines, readout)


def test_the_speeds_panel_across_turned_axes_says_where_each_is_seen_from():
    from fractions import Fraction
    motion = kinematics.Motion(speeds={"S1": Fraction(1500), "S2": Fraction(-500), "S3": Fraction(1000, 3),
                                       "S4": Fraction(0)},
                               torques={"S1": 10.0, "S2": 9.8, "S3": 14.406},
                               seen_from={"S1": "+X", "S2": "+Z", "S3": "(0.5, −0.866, 0)", "S4": "+Y"})
    lines, readout = ui_text.workbook_speed_lines(_speeds_spec("S1", "S2", "S3", "S4", "S5"), motion)
    assert lines == ["S1    1500.0\u00a0rpm anticlockwise seen from the +X end · 10.00\u00a0N·m",
                     "S2    500.0\u00a0rpm clockwise seen from the +Z end · 9.80\u00a0N·m",
                     "S3    333.3\u00a0rpm anticlockwise seen from the (0.5,\u00a0−0.866,\u00a00) end · 14.41\u00a0N·m",
                     "S4    0.0\u00a0rpm still",
                     "S5    not driven"]
    assert readout == "seen from each shaft's + end"
    assert not any("None" in line or line.endswith(" ") for line in lines)
    _held_together(lines)
    assert ui_text.workbook_speed_lines(_speeds_spec("S1"), kinematics.Motion(seen_from={"S1": "+X"}))[1] == \
        "no input"


TURNED_REFUSAL = ("G1 and G2 mesh across shafts at 90°, and which way a gear mate turns gears on shafts at an angle is "
                  "not settled by the probes for this version (findings.TURNED_GEAR_MATE_SENSE_READ_BACK), so the "
                  "gearbox is not built.")      # B's, ending at "not built" as ruled on review: the footer offers


def _turned_assessment(ready, kind="bevel"):
    from gear_generator.workbook import geometry
    mesh = SimpleNamespace(kind={"bevel": geometry.BEVEL, "crossed": geometry.CROSSED,
                                 "parallel": geometry.PARALLEL}[kind])
    report = dataclasses.replace(ready.report, meshes={("G1", "G2"): mesh})
    return dataclasses.replace(ready, report=report)


def test_a_turned_mesh_the_probes_have_not_settled_is_refused_and_build_parts_offered_only_where_it_is_on(
        ready, monkeypatch):
    """D16 (ruled): no static fallback. Planning's sentence (``motion.turned_refusal``, B's, ending at "not built") is
    shown whole; the footer offers Build parts where it is the enabled action, and nowhere else."""
    from gear_generator.workbook import motion
    monkeypatch.setattr(motion, "turned_refusal", lambda report: TURNED_REFUSAL)
    for kind in ("bevel", "crossed"):
        f = _footer(_turned_assessment(ready, kind), plan=_gearbox(layout=None, assembly=False, **FULL))
        assert (_clean(f.text), f.ok) == (f"Ready: Build parts makes 4 parts in {P}. {TURNED_REFUSAL}", True)
        assert (f.build_action, f.build_label, f.build_enabled) == (ui_text.BUILD_PARTS, "Build parts", True)
    built = _footer(_turned_assessment(ready), plan=_gearbox(layout=None, assembly=False,
                                                             reuse=[_reuse(s, [g]) for s, g in
                                                                    zip(STEMS, ("G1", "G2", "G3", "G4"))]))
    assert built.text == f"The 4 parts are built already, so Build parts has nothing to make. {TURNED_REFUSAL}"
    assert not built.build_enabled and "Build parts makes" not in built.text
    # A gearbox on record (Build again…): the refusal alone, with Build again… and Update greyed beside it.
    again = _footer(_turned_assessment(ready), record=_turning_record(), plan=_again(), update=_update())
    assert (again.text, again.ok) == (TURNED_REFUSAL, False)
    assert (again.build_action, again.build_enabled, again.update_enabled) == (ui_text.BUILD_AGAIN, False, False)


def test_a_parallel_mesh_or_a_settled_turned_mesh_leaves_build_as_it_was(ready, monkeypatch):
    from gear_generator.workbook import motion
    monkeypatch.setattr(motion, "turned_refusal", lambda report: "")
    f = _footer(_turned_assessment(ready, "parallel"), plan=_gearbox(**FULL))
    assert f.build_action == ui_text.BUILD and f.text.startswith("Ready: Build makes 4 parts")
    f = _footer(_turned_assessment(ready), plan=_gearbox(**FULL))
    assert f.build_action == ui_text.BUILD and f.build_enabled


def test_the_speeds_panel_through_the_solver_on_an_x_shaft():
    """Fixture A (W6-PLAN §5.1) through ``kinematics.solve`` with its meshes' senses, as the window has it."""
    from test_workbook_turned import bevel_reducer, laid
    spec = bevel_reducer()
    _, meshes = laid(spec)
    motion = kinematics.solve(spec, senses={k: v.sense for k, v in meshes.items()})
    assert ui_text.workbook_speed_lines(spec, motion) == (
        ["S1    1500.0\u00a0rpm anticlockwise seen from the +X end · 10.00\u00a0N·m",
         "S2    750.0\u00a0rpm clockwise seen from the +Z end · 19.60\u00a0N·m",
         "S3    250.0\u00a0rpm anticlockwise seen from the +Z end · 57.62\u00a0N·m"], "seen from each shaft's + end")


def test_w6_structural_sentences_are_shown_whole(ready):
    """B's §2.9 sentences are shown as classify writes them, ending "…, so the gearbox needs building again." as the
    W5 sentences the window already pins do; the strip's "; build it again as a new part." is folded as in W4."""
    axis = ("S1's axis is now X- where it was built X+: the layout's axis and the mates on it keep the direction they "
            "were made with, so the gearbox needs building again.")
    tip = ("G1's At (0 → 2) moves its cone tip off the Right plane (x 0 → 2): the mate G1 along S1 holds it on that "
           "plane and cannot take a distance, so the gearbox needs building again.")
    form = ("G2's teeth (40 → 41) make it a crown gear where it was built a cone, which its values cannot carry; build "
            "it again as a new part.")
    f = _footer(ready, record=_turning_record(), plan=_again(), update=_update(structural=(axis,)))
    assert _clean(f.text) == (
        f"{axis} Update SolidWorks offers to build again as Reducer_12to1_r2. It was built with its gears mated to "
        "turn: drag G1 in SolidWorks and the rest of its train follow.")
    question = ui_text.build_again_question(_update(structural=(tip, form)), _again(), record=_turning_record())
    assert question.startswith(
        f"{tip} G2's teeth (40 → 41) make it a crown gear where it was built a cone, which its values cannot carry, so "
        "it needs a new part. Build again as Reducer_12to1_r2? ")


def _resensed_update(**changes):
    """The 12 : 1's turning update with G2's mesh to G1 remade for its sense (a crossed shaft moved round)."""
    fields = dict(resensed=("G1 meshes G2",), moved_shafts=("S2",),
                  layout=swbuild.DocumentValues(_path("Reducer_12to1_Layout")))
    fields.update(changes)
    return _motion_update(**fields)


PASSES = "(since S2 now passes S1 on its other side, so G1 and G2 turn the other way against each other)"


def test_before_the_press_a_mesh_whose_sense_changed_is_said_to_be_remade_and_why():
    """Only a crossed mesh's sense changes with a move, and crossed shafts pass each other; the reason names how the
    two gears turn against each other, never one gear reversing (one may be the input), and names a shaft only when
    one of the mesh's shafts moved."""
    assert _clean(ui_text.update_summary(_resensed_update())) == (
        f"Update SolidWorks will move S2 in Reducer_12to1_Layout, remake the gear mate G1 meshes G2 {PASSES}, and "
        "re-place G1, G2, G3 and G4.")
    asked = _resensed_update(ratios=("G1 meshes G2",))
    assert f"remake the gear mate G1 meshes G2 at 17 : 69 {PASSES}" in ui_text.update_summary(asked)
    assert "set the gear mate" not in ui_text.update_summary(asked)
    s1 = _resensed_update(moved_shafts=("S1",))                       # the input's shaft moved
    assert ("remake the gear mate G1 meshes G2 (since S1 now passes S2 on its other side, so G1 and G2 turn the other "
            "way against each other)") in ui_text.update_summary(s1)
    neither = _resensed_update(moved_shafts=("S3",))
    assert ("remake the gear mate G1 meshes G2 (since G1 and G2 now turn the other way against each other), and "
            "re-place") in _clean(ui_text.update_summary(neither))
    assert "passes" not in ui_text.update_summary(neither)


def test_after_the_press_a_mesh_remade_for_its_sense_is_said_once_and_never_as_found_wrong():
    """``GearboxUpdate.resensed`` (A, 128aa8e): a sense-only remake is there alone; one whose ratio changed too is in
    ``ratios`` as well."""
    result = _moved(changed=[ASM], placed=["G1", "G2", "G3", "G4"], resensed=["G1 meshes G2"],
                    ratios_read=[("G1 meshes G2", 17, 68, 17, 68)], sense_found_wrong=["G1 meshes G2"],
                    layout=swbuild.UpdateResult(document="Reducer_12to1_Layout.SLDPRT", changed=["S2 X"], rebuilt=True))
    text, ok = ui_text.gearbox_update_status(_resensed_update(), result)
    assert (_clean(text), ok) == (
        f"Updated SolidWorks: moved S2 in Reducer_12to1_Layout, remade the gear mate G1 meshes G2 {PASSES}, re-placed "
        "G1, G2, G3 and G4; no interference between the gears where they stand. Save Reducer_12to1 in SolidWorks to "
        "keep it.", True)
    assert text.count("G1 meshes G2") == 1 and "right way round" not in text and "17 : 69" not in text
    new_ratio = dataclasses.replace(result, ratios=["G1 meshes G2"], ratios_read=[("G1 meshes G2", 17, 68, 17, 69)],
                                    sense_found_wrong=[])
    assert f"remade the gear mate G1 meshes G2 at 17 : 69 {PASSES}" in \
        ui_text.gearbox_update_status(_resensed_update(), new_ratio)[0]
    # No read of it: the ratio the summary promised is still said, from the plan.
    unread = dataclasses.replace(new_ratio, ratios_read=[])
    asked = _resensed_update(ratios=("G1 meshes G2",))
    assert f"remade the gear mate G1 meshes G2 at 17 : 69 {PASSES}" in ui_text.gearbox_update_status(asked, unread)[0]
    sense_only = dataclasses.replace(result, ratios_read=[], sense_found_wrong=[])
    assert f"remade the gear mate G1 meshes G2 {PASSES}," in ui_text.gearbox_update_status(_resensed_update(),
                                                                                            sense_only)[0]
    s1 = dataclasses.replace(result, layout=None)
    assert ("remade the gear mate G1 meshes G2 (since S1 now passes S2 on its other side, so G1 and G2 turn the other "
            "way against each other)") in ui_text.gearbox_update_status(_resensed_update(moved_shafts=("S1",)),
                                                                         s1)[0]
    failed = dataclasses.replace(result, resensed=[], failures=[("Reducer_12to1.SLDASM", "It would not remake.")])
    assert "remade" not in ui_text.gearbox_update_status(_resensed_update(), failed)[0]


def test_the_workers_turned_refusals_are_shown_as_whole_sentences_with_no_solidworks_api_words():
    """A's §2.9 sentences as the window shows them: whole, ending as a sentence, with no API word in what the user
    reads (the W5 rule: no "Flip", "Reverse" or "entities")."""
    gate = ("The gear mate G1 meshes G2 joins gears on shafts at an angle, and which way such a gear mate turns cannot "
            "be told on SolidWorks yet (findings.TURNED_GEAR_MATE_SENSE_READ_BACK is None), so nothing is made or "
            "changed.")
    read = ("SolidWorks reads an axis of the gear mate G1 meshes G2 as pointing (0.0, 0.0, 1.0), which is not along "
            "G1's axis (1, 0, 0), so the mate does not hold the axes the gears were placed on, and nothing is guessed.")
    shown = [ui_text.job_failed(swbuild.BuildError(gate)), ui_text.gearbox_status(_turning(), _refused(read))[0]]
    assert shown[0] == gate and f"its mates. {read} The parts and the layout part are kept." in shown[1]
    for text in shown:                         # (the gate quotes a finding's value, None, as A writes it)
        assert text.endswith(".") and text[0].isupper() and "  " not in text
        for word in ("Flip", "Reverse", "entit", "EntityParams", "AddMate"):
            assert word not in text


# -- the Gears table's Part column (package D's finding on fixture B) ------------------------------------------------


def test_a_part_name_longer_than_the_column_keeps_a_short_head_and_as_much_of_its_end_as_fits():
    """The end tells a part from its neighbours (teeth, mate teeth, angle, hand, revision)."""
    assert (ui_text.PART_CHARS, ui_text.PART_HEAD) == (18, 4)
    assert ui_text.part_cell("Bevel_m2.5_N20_M30_S120") == "Beve…_N20_M30_S120"
    assert ui_text.part_cell("Bevel_m2.5_N30_M20_S120") == "Beve…_N30_M20_S120"
    at_limit = "Helical_m2_N20_45R"                                   # 18: as it is
    assert len(at_limit) == 18 and ui_text.part_cell(at_limit) == at_limit
    one_over = "Helical_m2_N20_45RX"                                  # 19: the end begun at the "_" just past the cut
    assert ui_text.part_cell(one_over) == "Heli…_m2_N20_45RX"
    assert ui_text.part_cell("Bevel_m2.5_N20_M30_S120_r2") == "Beve…_M30_S120_r2"
    assert ui_text.part_cell("ABCDEFGHIJKLMNOPQRSTUVWXYZ") == "ABCD…NOPQRSTUVWXYZ"     # no "_" near the cut
    for name in ("Bevel_m2.5_N20_M30_S120", one_over, "x" * 40, "a_" + "b" * 30):
        assert len(ui_text.part_cell(name)) <= 18
    assert ui_text.part_cell("") == "" and ui_text.part_cell("Gear_m1.5_N17_r2") == "Gear_m1.5_N17_r2"


def _rows_for(*parts):
    """``workbook_gear_rows`` over hand-made parts: one job per name, G1, G2, … in order, a repeated name one part
    shared by two gears."""
    from gear_generator.workbook.build import PartsPlan
    names = list(dict.fromkeys(parts))
    gears = [Gear(f"G{i}", "S1", "0", "spur", "external", "20", "1.5", "", "10", "10")
             for i in range(1, len(parts) + 1)]
    jobs = tuple(_job(n, [f"G{i}" for i, p in enumerate(parts, 1) if p == n]) for n in names)
    spec = SimpleNamespace(gears=gears)
    return [r[6] for r in ui_text.workbook_gear_rows(spec, PartsPlan(jobs=jobs), [])]


def test_different_names_never_share_a_cell_and_one_shared_part_keeps_one():
    assert _rows_for("Bevel_m2.5_N20_M30_S120", "Bevel_m2.5_N30_M20_S120") == [
        "Beve…_N20_M30_S120", "Beve…_N30_M20_S120"]
    # These collide under head and end ("Bevel_m2_…" and "Bevel_m3_…" lose the one character that differs): each is
    # lengthened until they read apart.
    a, b = "Bevel_m2_N20_M30_S120_X", "Bevel_m3_N20_M30_S120_X"
    assert ui_text.part_cell(a) == ui_text.part_cell(b)
    cells = _rows_for(a, b)
    assert cells[0] != cells[1] and cells == [a, b]
    # One part file shared by two identical gears: the same cell, as it is the same part.
    shared = _rows_for("Bevel_m2.5_N20_M30_S120", "Bevel_m2.5_N20_M30_S120", "Bevel_m2.5_N30_M20_S120")
    assert shared == ["Beve…_N20_M30_S120", "Beve…_N20_M30_S120", "Beve…_N30_M20_S120"]


def test_fixture_bs_rows_keep_their_ends_and_the_12_to_1s_are_unchanged(ready, tmp_path):
    from test_workbook_turned import crossed_slant
    (tmp_path / "b").mkdir()
    read, diagnostics = model.from_book(xlsx.read(write(tmp_path / "b", crossed_slant())))
    b = assess.assess(read, diagnostics, "C:\\Parts\\Crossed_Slant")
    rows = ui_text.workbook_gear_rows(b.spec, b.parts, b.diagnostics)
    assert [r[6] for r in rows] == ["Helical_m2_N20_45R", "Helical_m2_N40_45R", "Beve…_N20_M30_S120",
                                    "Beve…_N30_M20_S120"]
    twelve = ui_text.workbook_gear_rows(ready.spec, ready.parts, ready.diagnostics)
    assert [r[6] for r in twelve] == list(STEMS)


# -- W7: the planetary stage (W7-PLAN §2.12, as W7-INTERFACES §6 rules) ----------------------------------------------

from gear_generator.workbook.gearbox import CarrierReuse  # noqa: E402
from gear_generator.workbook.layout import CarrierLayout  # noqa: E402

PLANETS = ("Planet copy 1", "Planet copy 2", "Planet copy 3")
CARRIER_PATH = _path("Planetary_4to1_C_Carrier")


def _planetary_motion(held="ring"):
    """W7-PLAN §4.1's mates by rank: three sun mates and ONE ring mate; two planet–ring meshes left unmated."""
    mates = [MatePlan("Sun on S Axis", "axis", ("Sun",), "S"), MatePlan("Sun along S", "along", ("Sun",), "S")]
    if held != "carrier":
        mates += [MatePlan("C carrier on C Axis", "axis", ("C carrier",), "C"),
                  MatePlan("C carrier along C", "along", ("C carrier",), "C")]
    for k, planet in enumerate(PLANETS, 1):
        mates += [MatePlan(f"{planet} on P copy {k} Axis", "axis", (planet,), f"P copy {k}", on="C carrier"),
                  MatePlan(f"{planet} along P copy {k}", "along", (planet,), f"P copy {k}",
                           face_global="Planet Face Z", z_front=5.0)]
    mates += [MatePlan(f"Sun meshes {p}", "mesh", ("Sun", p), ratio=(18, 18), sense=1) for p in PLANETS]
    mates += [MatePlan("Planet copy 1 meshes Ring", "mesh", ("Planet copy 1", "Ring"), ratio=(18, 54), sense=-1)]
    return MotionPlan(anchors={"S": "Sun", **{f"P copy {k}": p for k, p in enumerate(PLANETS, 1)}},
                      mates=tuple(mates), fixed=("Ring",) if held == "ring" else ("C carrier",),
                      unmated=(("Planet copy 2", "Ring"), ("Planet copy 3", "Ring")), trains=(("S", "C"),),
                      drag=("Sun",), carriers=("C carrier",) if held != "carrier" else ())


def _planetary_plan(held="ring", reuse_carrier=False, **changes):
    carriers = (CarrierReuse(CARRIER_PATH, (), ()),) if reuse_carrier else (BuildPlan("carrier", "", (NewPart(""),)),)
    fields = dict(build=[_job(s, [s]) for s in ("Sun", "Planet", "Ring")], motion=_planetary_motion(held),
                  carrier_layouts=(CarrierLayout("C", 0.0, 0.0, 0.0, (0.0, 0.0, 1.0), ()),),
                  carrier_paths={"C": CARRIER_PATH}, carriers=carriers)
    fields.update(changes)
    name = fields.pop("name", "Planetary_4to1")
    return _gearbox(name, **fields)


def _planetary_built(**values):
    fields = dict(parts=swbuild.ManyResult(built=[_saved(s) for s in ("Sun", "Planet", "Ring")]),
                  layout=_saved("Planetary_4to1_Layout"), carriers=[_saved("Planetary_4to1_C_Carrier")],
                  assembly=_saved("Planetary_4to1", ".SLDASM"), kind="motion")
    fields.update(values)
    return swbuild.GearboxResult(**fields)


def test_copies_phrase_and_carrier_phrase():
    assert ui_text.copies_phrase("Planet", 3) == "Planet (3 copies)" and ui_text.copies_phrase("Planet", 1) == "Planet"
    assert ui_text.carrier_phrase(_planetary_plan()) == "C (the carrier)"
    assert ui_text.carrier_phrase(_planetary_plan(), part=True) == (
        "C, built as Planetary_4to1_C_Carrier (axes and planes only)")
    record = _record()
    assert ui_text.carrier_phrase(record) == "" and ui_text.carrier_phrase(_gearbox(**FULL)) == ""
    record.gearbox.carriers = [store.CarrierEntry(shaft="C", path=CARRIER_PATH, direction=[0.0, 0.0, 1.0])]
    assert ui_text.carrier_phrase(record) == "C (the carrier)"


def test_before_build_the_carrier_is_said_once_with_its_copies_and_the_held_ring(ready):
    f = _footer(ready, plan=_planetary_plan())
    assert _clean(f.text) == (
        f"Ready: Build makes 3 parts, Planetary_4to1_Layout, Planetary_4to1_C_Carrier and Planetary_4to1.SLDASM in "
        f"{P}. Its turning gears are mated to their shafts and to each other, so they turn together in SolidWorks. "
        "C is built as a carrier of axes and planes only, turning with the 3 copies of Planet on it. Ring stays fixed "
        "where it is placed: its shaft does not turn.")
    assert "copy 2" not in f.text and "unmated" not in f.text
    held = ui_text.motion_ready_line(_planetary_plan("carrier"))
    assert held == ("Its gears are mated to their shafts and to each other, so they turn together in SolidWorks. C is "
                    "built as axes and planes only, held fixed; the 3 copies of Planet turn on it.")
    reused = _footer(ready, plan=_planetary_plan(reuse_carrier=True))
    assert reused.text.startswith(f"Ready: Build makes 3 parts, Planetary_4to1_Layout and Planetary_4to1.SLDASM in "
                                  f"{P}, reusing Planetary_4to1_C_Carrier.")


def test_after_build_the_carrier_part_is_named_and_one_ring_mate_reads_as_nothing_missing():
    """Three planet–ring meshes and ONE gear mate (J5): nothing may read as two mates missing or broken (§6.6)."""
    text, ok = ui_text.gearbox_status(_planetary_plan(), _planetary_built())
    assert (_clean(text), ok) == (
        "Built 3 parts, Planetary_4to1_Layout, Planetary_4to1_C_Carrier and Planetary_4to1.SLDASM; no interference "
        "between the gears where they stand. Its turning gears are mated to turn together, and SolidWorks reports no "
        "mate in error: drag Sun in SolidWorks and the rest of its train follow. The 3 copies of Planet turn on C, "
        "and Planetary_4to1_C_Carrier holds C's axes and planes only: a plate and pins are yours to add. Ring stays "
        "fixed where it is placed: its shaft does not turn.", True)
    for word in ("unmated", "missing", "copy 2", "2 mates", "not mated"):
        assert word not in text
    held = ui_text.gearbox_status(_planetary_plan("carrier"), _planetary_built())[0]
    assert held.endswith("The 3 copies of Planet turn on C, which is held fixed, and Planetary_4to1_C_Carrier holds "
                         "C's axes and planes only: a plate and pins are yours to add.")


def test_a_carrier_part_that_fails_leaves_the_parts_and_layout_and_the_refused_train_keeps_it():
    failed = _planetary_built(carriers=[_failed("Part4", "insert plane 'P copy 2 X Plane'", "SolidWorks returned "
                                                                                             "None.")],
                              assembly=None, kind="")
    assert ui_text.gearbox_status(_planetary_plan(), failed) == (
        "Built 3 parts and Planetary_4to1_Layout; Part4 was left open, unsaved; insert plane 'P copy 2 X Plane': "
        "SolidWorks returned None. The assembly was not attempted. Press Build to carry on: the parts and layout are "
        "reused.", False)
    refused, _ = ui_text.mate_refused_status(_planetary_plan(), _refused(LOCK_PROBLEM,
                                                                         carriers=[_saved("Planetary_4to1_C_Carrier")]))
    assert ("Built 4 parts, Reducer_12to1_Layout and Planetary_4to1_C_Carrier; no assembly was saved" in refused
            and "The parts, the layout part and the carrier part are kept." in refused)


def _planetary_update(**changes):
    refs = tuple(swbuild.MateRef(m.name, m.kind, m.gears, m.shaft) for m in _planetary_motion().mates)
    meshes = tuple(swbuild.MeshLink("Sun", p, -1.0, 20.0, carrier="C carrier") for p in PLANETS) + tuple(
        swbuild.MeshLink(p, "Ring", 1 / 3, 6.6667, carrier="C carrier") for p in PLANETS)   # unmated ones too (§6.6)
    link = swbuild.CarrierLink("C carrier", PLANETS, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    motion = swbuild.MotionUpdate(mates=refs, meshes=meshes, carriers=(link,), held=("Ring",), fixed=("Ring",))
    fields = dict(motion=motion, parts=(), layout=None, moved_shafts=(), replaced=(),
                  assembly=_path("Planetary_4to1", ".SLDASM"),
                  carriers=(swbuild.DocumentValues(CARRIER_PATH),))
    fields.update(changes)
    return UpdatePlan(**fields)


def test_the_update_summary_names_the_carrier_and_the_copies_once():
    assert _clean(ui_text.update_summary(_planetary_update(carriers_moved=("C",), replaced=("Planet copy 1",)))) == (
        "Update SolidWorks will move the planets on C in Planetary_4to1_C_Carrier, and re-place C (the carrier), "
        "Planet (3 copies) and Sun.")
    # The shared Face Z global is keyed by the row (§6.7): one move, the shaft from the copies' along mates.
    assert _clean(ui_text.update_summary(_planetary_update(axial=("Planet",)))) == (
        "Update SolidWorks will move Planet (3 copies) along P, and re-place C (the carrier), Planet (3 copies) and "
        "Sun.")
    # The held ring moves: re-placed first, then the carrier, then the train (J15).
    assert ui_text.update_summary(_planetary_update(replaced=("Ring",))) == (
        "Update SolidWorks will re-place Ring, C (the carrier), Planet (3 copies) and Sun.")
    # A train only turned, with nothing the plan must put, is promised nothing.
    assert ui_text.update_summary(_planetary_update()).startswith("SolidWorks already matches the workbook on record")


def test_after_update_the_restored_train_names_the_carrier_and_its_copies_once():
    result = _moved(placed=["C carrier", "Sun", *PLANETS], changed=[_path("Planetary_4to1", ".SLDASM")],
                    restored=[("Sun", "C carrier", *PLANETS)])
    text, ok = ui_text.gearbox_update_status(_planetary_update(), result)
    assert (_clean(text), ok) == (
        "Updated SolidWorks: re-placed C (the carrier), Sun and Planet (3 copies); no interference between the gears "
        "where they stand. Sun, C (the carrier) and Planet (3 copies) had been turned in SolidWorks; their train is "
        "back at the turn it was built at. Save Planetary_4to1 in SolidWorks to keep it.", True)
    one = _moved(placed=["Planet copy 2"], changed=[_path("Planetary_4to1", ".SLDASM")])
    assert "re-placed Planet copy 2;" in ui_text.gearbox_update_status(_planetary_update(), one)[0]


def test_the_footer_on_a_built_planetary_says_what_to_drag_and_that_the_carrier_has_nothing_to_grab():
    record = _turning_record(("Sun",))
    record.gearbox.carriers = [store.CarrierEntry(shaft="C", path=CARRIER_PATH, direction=[0.0, 0.0, 1.0])]
    record.gearbox.unmated = [["Planet copy 2", "Ring"], ["Planet copy 3", "Ring"]]
    assert ui_text.motion_record_line(record) == (
        "It was built with its gears mated to turn: drag Sun in SolidWorks and the rest of its train follow. C (the "
        "carrier) is axes and planes only, so it has nothing to drag.")


def test_the_speeds_panel_on_a_planetary_stage():
    """W7-PLAN §4.1, ring held: S 1000, C 250 (4 : 1), P −500 about its own axis and −750 on C, R held 5.762."""
    from fractions import Fraction
    shafts = [SimpleNamespace(id="S", mount=lambda: "frame", copies=""),
              SimpleNamespace(id="C", mount=lambda: "frame", copies=""),
              SimpleNamespace(id="P", mount=lambda: "C", copies="3"),
              SimpleNamespace(id="R", mount=lambda: "frame", copies="")]
    motion = kinematics.Motion(speeds={"S": Fraction(1000), "C": Fraction(250), "P": Fraction(-500), "R": Fraction(0)},
                               torques={"S": 2.0, "C": 7.7624}, relative={"P": Fraction(-750)}, held={"R": 5.7624},
                               seen_from={"S": "+Z", "C": "+Z", "P": "+Z", "R": "+Z"})
    lines, readout = ui_text.workbook_speed_lines(SimpleNamespace(shafts=shafts), motion)
    assert lines == ["S     1000.0 rpm anticlockwise · 2.00 N·m",
                     "C     250.0 rpm anticlockwise · 7.76 N·m",
                     "P     500.0 rpm clockwise, 750.0 rpm clockwise relative to C · 3 copies",
                     "R     held still · 5.76 N·m"]
    assert readout == "seen from +Z"
    _held_together(lines)
    assert ui_text.planetary_speed_line("P", motion, copies=1, carrier="C") == (
        "P     500.0 rpm clockwise, 750.0 rpm clockwise relative to C")
    on_x = dataclasses.replace(motion, seen_from={"S": "+X", "C": "+X", "P": "+X", "R": "+X"})
    assert ui_text.planetary_speed_line("P", on_x, copies=3, carrier="C") == (
        "P     500.0 rpm clockwise seen from the +X end, 750.0 rpm clockwise relative to C · 3 copies")


def test_copies_share_one_part_cell():
    """The Gears table has one row per Gears row, so the copies of Planet are one row; two rows sharing a part file
    still show the same cell."""
    assert _rows_for("Bevel_m2.5_N20_M30_S120", "Bevel_m2.5_N20_M30_S120") == ["Beve…_N20_M30_S120"] * 2


def test_the_build_again_question_names_the_carrier_part():
    reused = _planetary_plan(reuse_carrier=True, layout="reuse", name="Planetary_4to1_r2",
                             assembly_path=_path("Planetary_4to1_r2", ".SLDASM"))
    assert ("reuses Planetary_4to1_r2_Layout and Planetary_4to1_C_Carrier and makes a new assembly, "
            "Planetary_4to1_r2.SLDASM") in ui_text.build_again_question(_update(), reused)
    fresh = _planetary_plan(name="Planetary_4to1_r2", layout_path=_path("Planetary_4to1_r2_Layout"),
                            assembly_path=_path("Planetary_4to1_r2", ".SLDASM"),
                            carrier_paths={"C": _path("Planetary_4to1_r2_C_Carrier")})
    assert ("makes a new layout part, carrier part and assembly (Planetary_4to1_r2_Layout, Planetary_4to1_r2_C_Carrier "
            "and Planetary_4to1_r2.SLDASM)") in ui_text.build_again_question(_update(), fresh)


def test_a_planetary_refused_at_build_is_said_whole_with_build_parts_offered_and_a_checks_error_holds_build(ready):
    """§1.2's refusals are B's sentences, each at its cell (``later_rows``): shown whole, with Build parts offered
    as for every row a later pass builds. §2.3's errors (the assembly condition, neighbouring copies) are Checks
    errors: Build waits for them, the sentence whole after "Fix the workbook before building:"."""
    from gear_generator.gears.base import ERROR, WARNING
    refusals = ["Shafts!A4: S, C and R form a planetary stage with no member held: a differential is not built by this "
                "version; set one of them to Role fixed.",
                "Gears!A3: Planet is helical: a planetary stage is built with spur gears only by this version.",
                "Shafts!A6: C2 is a second carrier: one planetary stage per workbook is built by this version."]
    for message in refusals:
        parts = dataclasses.replace(ready.parts, refused=[Diagnostic(WARNING, message, message.split(":")[0])])
        f = _footer(dataclasses.replace(ready, parts=parts), plan=_gearbox(layout=None, assembly=False, **FULL))
        assert _clean(f.text) == f"Ready: Build parts makes 4 parts in {P}; the layout and assembly are not built: {message}"
        assert (f.build_action, f.build_enabled) == (ui_text.BUILD_PARTS, True)
    condition = ("Shafts!H4: 5 copies of Planet cannot all mesh with Sun and Ring at once: (18 + 54) / 5 = 14.4 is not "
                 "a whole number. With these teeth the copies can be 1, 2, 3 or 4; more would not fit round C.")
    errored = dataclasses.replace(ready, diagnostics=[Diagnostic(ERROR, condition, "Shafts!H4")])
    f = _footer(errored, plan=_gearbox(**FULL))
    assert (f.text, f.build_enabled) == (f"Fix the workbook before building: {condition}", False)


def test_after_update_a_carrier_part_whose_values_changed_is_said_as_the_layouts_is():
    """W7-INTERFACES §6.11: ``GearboxUpdate.carriers`` holds each carrier part's values as set, after the layout's."""
    changed = swbuild.UpdateResult(document="Planetary_4to1_C_Carrier.SLDPRT", changed=["P copy 2 X", "P copy 2 Y"],
                                   rebuilt=True)
    result = _moved(placed=["C carrier", "Sun", *PLANETS], carriers=[changed],
                    changed=[CARRIER_PATH, _path("Planetary_4to1", ".SLDASM")])
    text, ok = ui_text.gearbox_update_status(_planetary_update(carriers_moved=("C",)), result)
    assert (_clean(text), ok) == (
        "Updated SolidWorks: moved the planets on C in Planetary_4to1_C_Carrier, re-placed C (the carrier), Sun and "
        "Planet (3 copies); no interference between the gears where they stand. Save Planetary_4to1_C_Carrier and "
        "Planetary_4to1 in SolidWorks to keep them.", True)
    still = dataclasses.replace(result, carriers=[swbuild.UpdateResult(document="Planetary_4to1_C_Carrier.SLDPRT",
                                                                        unchanged=["P copy 2 X"], rebuilt=True)],
                                changed=[_path("Planetary_4to1", ".SLDASM")])
    assert "planets on C" not in ui_text.gearbox_update_status(_planetary_update(), still)[0]
    broken = dataclasses.replace(result, carriers=[dataclasses.replace(changed, rebuilt=False)])
    text, ok = ui_text.gearbox_update_status(_planetary_update(), broken)
    assert ("moved the planets on C in Planetary_4to1_C_Carrier (SolidWorks reported an error rebuilding it)" in text
            and not ok)


def test_each_carriers_result_is_matched_to_its_part_by_file_name_never_by_position():
    """Two carriers given in the other order (made up: the app refuses two stages today, but the matching must not
    lean on that), and a result that matches no carrier part is not said."""
    c2_path = _path("Planetary_4to1_C2_Carrier")
    link2 = swbuild.CarrierLink("C2 carrier", ("Q copy 1",), (50.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    update = _planetary_update(carriers=(swbuild.DocumentValues(CARRIER_PATH), swbuild.DocumentValues(c2_path)))
    update = dataclasses.replace(update, motion=dataclasses.replace(update.motion,
                                                                    carriers=update.motion.carriers + (link2,)))
    results = [swbuild.UpdateResult(document="Planetary_4to1_C2_Carrier.SLDPRT", changed=["Q copy 1 X"],
                                    rebuilt=True),
               swbuild.UpdateResult(document="Planetary_4to1_C_Carrier.SLDPRT", unchanged=["P copy 2 X"],
                                    rebuilt=True)]
    text = ui_text.gearbox_update_status(update, _moved(carriers=results, changed=[c2_path]))[0]
    assert text.startswith("Updated SolidWorks: moved the planets on C2 in Planetary_4to1_C2_Carrier;")
    assert "planets on C " not in text and "planets on C in" not in text
    stray = [swbuild.UpdateResult(document="Somewhere_Else.SLDPRT", changed=["X"], rebuilt=True)]
    assert "planets" not in ui_text.gearbox_update_status(update, _moved(carriers=stray, changed=[]))[0]


def test_the_speeds_panel_through_the_solver_on_the_4_to_1_held_ring_and_held_sun():
    """W7-PLAN §4.1 and §4.2 through ``kinematics.solve`` (B's), so a sign that differs from the solver's shows."""
    from test_workbook_planetary import planetary_4to1, sun_held
    lines, readout = ui_text.workbook_speed_lines(planetary_4to1(), kinematics.solve(planetary_4to1()))
    assert (lines, readout) == (["S     1000.0\u00a0rpm anticlockwise · 2.00\u00a0N·m",
                                 "C     250.0\u00a0rpm anticlockwise · 7.76\u00a0N·m",
                                 "P     500.0\u00a0rpm clockwise, 750.0\u00a0rpm clockwise relative to C · 3 copies",
                                 "R     held still · 5.76\u00a0N·m"], "seen from +Z")
    _held_together(lines)
    lines, _ = ui_text.workbook_speed_lines(sun_held(), kinematics.solve(sun_held()))
    assert lines == ["S     held still · 0.64\u00a0N·m",
                     "C     750.0\u00a0rpm anticlockwise · 2.64\u00a0N·m",
                     "P     1500.0\u00a0rpm anticlockwise, 750.0\u00a0rpm anticlockwise relative to C · 3 copies",
                     "R     1000.0\u00a0rpm anticlockwise · 2.00\u00a0N·m"]


def test_a_held_member_reads_held_with_no_torque_typed_and_the_missing_torque_is_said():
    """"held" comes from the stage's held member, not from whether a torque is worked out; when the torque through
    the stage is not worked out, the panel says why (``Motion.torque_note``) in a line of its own."""
    from test_workbook_planetary import edited, planetary_4to1
    no_torque = edited(planetary_4to1(), shafts={"S": dict(torque="")})
    motion = kinematics.solve(no_torque)
    lines, _ = ui_text.workbook_speed_lines(no_torque, motion)
    assert lines[3] == "R     held still" and "R" not in motion.held
    noted = dataclasses.replace(motion, torque_note="The torque through C's planetary stage is not worked out: its "
                                                    "members' speeds do not settle which of them drives.")
    assert ui_text.workbook_speed_lines(no_torque, noted)[0][-1] == (
        "The torque through C's planetary stage is not worked out: its members' speeds do not settle which of them "
        "drives.")


def test_the_speeds_prose_rows_are_the_torque_note_or_a_later_phases_sentence():
    """``speeds_prose_rows`` is the one rule for which Speeds lines are prose: on the 4 : 1 with its torque typed
    none; with no torque typed and the note given, the last; on a W6 gearbox none; and a later phase's panel all."""
    from test_workbook_planetary import edited, planetary_4to1
    from test_workbook_turned import bevel_reducer, laid
    spec = planetary_4to1()
    motion = kinematics.solve(spec)
    lines, _ = ui_text.workbook_speed_lines(spec, motion)
    assert ui_text.speeds_prose_rows(motion, lines) == set()
    no_torque = edited(spec, shafts={"S": dict(torque="")})
    noted = dataclasses.replace(kinematics.solve(no_torque), torque_note="The torque through C's planetary stage is "
                                "not worked out: its members' speeds do not settle which of them drives.")
    lines, _ = ui_text.workbook_speed_lines(no_torque, noted)
    assert ui_text.speeds_prose_rows(noted, lines) == {len(lines) - 1} and len(lines) == 5
    assert lines[-1].startswith("The torque through C's")
    turned = bevel_reducer()
    _, meshes = laid(turned)
    w6 = kinematics.solve(turned, senses={k: v.sense for k, v in meshes.items()})
    assert ui_text.speeds_prose_rows(w6, ui_text.workbook_speed_lines(turned, w6)[0]) == set()
    later = dataclasses.replace(noted, later="G6 is driven through a dog ring: its speeds come in phase W8.")
    lines, readout = ui_text.workbook_speed_lines(no_torque, later)
    assert (lines, readout) == ([later.later], "") and ui_text.speeds_prose_rows(later, lines) == {0}
    idle = dataclasses.replace(noted, speeds={})                 # nothing turning: no note, no prose
    assert ui_text.speeds_prose_rows(idle, ui_text.workbook_speed_lines(no_torque, idle)[0]) == set()


def test_the_4_to_1s_gears_table_has_one_row_and_one_part_cell_for_the_planet_and_its_copies(tmp_path):
    from test_workbook_planetary import planetary_4to1
    (tmp_path / "p").mkdir()
    read, diagnostics = model.from_book(xlsx.read(write(tmp_path / "p", planetary_4to1())))
    a = assess.assess(read, diagnostics, "C:\\Parts\\Planetary_4to1")
    rows = ui_text.workbook_gear_rows(a.spec, a.parts, a.diagnostics)
    planet = [r for r in rows if r[0] == "Planet"]
    assert [r[0] for r in rows] == ["Sun", "Planet", "Ring", "CarrierGear"] and len(planet) == 1
    assert planet[0][6] == "Planet" and [s.copies for s in a.spec.shafts if s.id == planet[0][1]] == ["3"]


# -- W8: modes (W8-PLAN §1.12, W8-INTERFACES §7 and §9), on TransferCase_Parallel's shapes (§2.2, §2.3) ----------

from gear_generator.workbook import checks, gearbox  # noqa: E402

MODES = ("2H", "4H", "N", "4L")
TC_ASM = _path("TransferCase", ".SLDASM")
SLIDE_VALUES = {"RangeSlv along Rear": (46.0, 46.0, 56.0, 66.0), "ModeSlv along Rear": (96.0, 106.0, 96.0, 106.0)}
ON_SETS = {"RangeSlv engages InDog": ("2H", "4H"), "RangeSlv engages LoDog": ("4L",),
           "ModeSlv engages FrontDog": ("4H", "4L")}


def _tc_mates(modes=MODES):
    mates = [MatePlan("InPin on In Axis", "axis", ("InPin",), "In"), MatePlan("InPin along In", "along", ("InPin",), "In"),
             MatePlan("InDog locked to InPin", "lock", ("InPin", "InDog")),
             MatePlan("RangeSlv on Rear Axis", "axis", ("RangeSlv",), "Rear"),
             MatePlan("RangeSlv along Rear", "slide", ("RangeSlv",), "Rear", z_front=46.0,
                      values=tuple(zip(modes, SLIDE_VALUES["RangeSlv along Rear"])) if modes else ()),
             MatePlan("ModeSlv on Rear Axis", "axis", ("ModeSlv",), "Rear"),
             MatePlan("ModeSlv along Rear", "slide", ("ModeSlv",), "Rear", z_front=96.0,
                      values=tuple(zip(modes, SLIDE_VALUES["ModeSlv along Rear"])) if modes else ()),
             MatePlan("ModeSlv splined to RangeSlv", "spline", ("RangeSlv", "ModeSlv"), ratio=(1, 1), sense=-1)]
    if modes:
        mates += [MatePlan(name, "couple", tuple(name.split(" engages ")), ratio=(1, 1), sense=-1, modes=on)
                  for name, on in ON_SETS.items()]
    mates += [MatePlan("InPin meshes LayGear", "mesh", ("InPin", "LayGear"), ratio=(17, 34), sense=-1)]
    return tuple(mates)


def _tc_motion(modes=MODES):
    return MotionPlan(anchors={"In": "InPin", "Lay": "LayGear", "Lo": "LoGear", "Rear": "RangeSlv",
                               "FrontDrv": "FrontDog", "Idler": "FIdler", "Front": "FOut"},
                      mates=_tc_mates(modes), trains=(("In", "Lay", "Lo"),), drag=("InPin",), modes=modes,
                      drag_by_mode={m: ("InPin",) for m in modes})


def _tc_plan(modes=MODES, **changes):
    fields = dict(build=[_job(s, [s]) for s in ("InPin", "InDog", "RangeSlv")], motion=_tc_motion(modes),
                  meshes=(("InPin", "LayGear"),))
    fields.update(changes)
    return _gearbox("TransferCase", **fields)


def _tc_built(**values):
    checks_ = [swbuild.ModeCheck(m) for m in MODES]
    fields = dict(parts=swbuild.ManyResult(built=[_saved(s) for s in ("InPin", "InDog", "RangeSlv")]),
                  layout=_saved("TransferCase_Layout"), assembly=_saved("TransferCase", ".SLDASM"), kind="motion",
                  modes=checks_, positions_per_configuration=True)
    fields.update(values)
    return swbuild.GearboxResult(**fields)


def test_before_build_the_modes_are_named_and_the_first_is_where_it_opens(ready):
    f = _footer(ready, plan=_tc_plan())
    assert _clean(f.text) == (
        f"Ready: Build makes 3 parts, TransferCase_Layout and TransferCase.SLDASM in {P}. Its gears are mated to their "
        "shafts and, as each mode engages them, to each other, so they turn together in SolidWorks. It has 4 modes, "
        "2H, 4H, N and 4L: each becomes a configuration of the assembly, and it opens in 2H.")
    assert ui_text.modes_ready_line(_tc_plan(modes=("2H",))) == (
        "It has one mode, 2H, which becomes a configuration of the assembly, the one it opens in.")
    assert ui_text.modes_ready_line(_tc_plan(modes=())) == (
        "RangeSlv and ModeSlv slide, but the Modes sheet has no rows, so the assembly has one configuration with each "
        "at its position 0.")
    assert ui_text.motion_ready_line(_tc_plan(modes=())).endswith(
        "RangeSlv and ModeSlv slide, but the Modes sheet has no rows, so the assembly has one configuration with each "
        "at its position 0.")
    assert ui_text.modes_ready_line(_gearbox(**FULL)) == ""


def test_after_build_each_mode_is_named_once_and_the_switch_is_said_in_the_workbooks_word():
    text, ok = ui_text.gearbox_status(_tc_plan(), _tc_built())
    assert (_clean(text), ok) == (
        "Built 3 parts, TransferCase_Layout and TransferCase.SLDASM; no interference between the gears in any mode, "
        "where they stand. Its gears are mated to turn in each of its 4 modes, one configuration each (2H, 4H, N and "
        "4L), and SolidWorks reports no mate in error in any of them: it opens in 2H; to switch mode, double-click "
        "another mode's configuration in SolidWorks' ConfigurationManager. Drag InPin in SolidWorks and the rest of "
        "its train follow. RangeSlv and ModeSlv slide along Rear, each to its place in each mode. A turn you give the "
        "gears in one mode stays in that mode. Switching mode never by itself puts a dog tooth on tooth.", True)
    for word in ("pick a configuration", "same way"):
        assert word not in text


@pytest.mark.parametrize("positions", [False, None])
def test_the_two_claims_about_positions_are_made_only_where_the_running_version_keeps_them(positions):
    text = ui_text.gearbox_status(_tc_plan(), _tc_built(positions_per_configuration=positions))[0]
    assert ui_text.SWITCH_IN_STEP not in text and ui_text.TURN_STAYS not in text
    assert (ui_text.TURN_CAN_SHOW_ELSEWHERE in text) == (positions is False)


def test_a_clash_in_some_modes_is_said_once_with_the_modes_it_was_found_in():
    clash = swbuild.Clash(components=("Sleeve_m1.5_N30-1", "Dog_m1.5_N30-2"), gears=("RangeSlv", "LoDog"), volume=0.5)
    modes = [swbuild.ModeCheck("2H"), swbuild.ModeCheck("4H"), swbuild.ModeCheck("N", clashes=[clash]),
             swbuild.ModeCheck("4L", clashes=[clash])]
    text, ok = ui_text.gearbox_status(_tc_plan(), _tc_built(modes=modes))
    assert not ok and _clean(text).startswith(
        "Built 3 parts, TransferCase_Layout and TransferCase.SLDASM. Check: in N and 4L, RangeSlv and LoDog interfere, "
        "0.5 mm³; look where they meet in TransferCase.SLDASM. Its gears are mated")
    error = [swbuild.ModeCheck("2H"), swbuild.ModeCheck("4L", interference_error="SolidWorks returned nothing.")]
    assert ". Interference could not be checked in 4L: SolidWorks returned nothing. Look at each mesh in " \
           "TransferCase.SLDASM by eye." in ui_text.gearbox_status(_tc_plan(), _tc_built(modes=error))[0]


def test_a_problem_in_one_mode_is_shown_whole_and_the_refusal_names_the_modes():
    problems = ("In mode 4L, the mate RangeSlv engages LoDog over-defines the assembly.",
                "SolidWorks would not make the configuration 4L.",
                "RangeSlv's place in 4L reads 0 mm in SolidWorks, not the 66 mm set.")
    assert [ui_text.mode_problem(p) for p in problems] == list(problems)
    plan = _tc_plan(modes_plan=swbuild.ModesPlan(steps=tuple(swbuild.ModeStep(m) for m in MODES)))
    text, ok = ui_text.mate_refused_status(plan, _refused(*problems))
    assert not ok and "SolidWorks found 3 problems with its mates or its modes. " + " ".join(problems) in text


def _tc_record(modes=MODES):
    record = _turning_record(("InPin",))
    record.gearbox.name, record.gearbox.assembly, record.gearbox.modes = "TransferCase", TC_ASM, list(modes)
    return record


def test_the_footer_on_a_gearbox_built_with_modes_says_where_it_was_saved_and_how_to_switch():
    record = _tc_record()
    line = ui_text.motion_record_line(record)
    assert line == ("It was built with a configuration per mode (2H, 4H, N and 4L), each named as its mode, and saved "
                    "in 2H; to switch mode, double-click another mode's configuration in SolidWorks' "
                    "ConfigurationManager. Drag InPin in SolidWorks and the rest of its train follow.")
    assert "pick a configuration" not in line
    kept = ui_text.motion_record_line(record, positions_per_configuration=True)
    assert kept == f"{line} {ui_text.TURN_STAYS} {ui_text.SWITCH_IN_STEP}"
    shared = ui_text.motion_record_line(record, positions_per_configuration=False)
    assert shared == f"{line} {ui_text.TURN_CAN_SHOW_ELSEWHERE}"
    assert ui_text.modes_record_line(_turning_record()) == ""


def test_the_modes_rows_reordered_change_nothing_and_say_where_the_next_revision_is_saved():
    record = _tc_record()
    assert ui_text.modes_record_line(record, modes=("4L", "2H", "4H", "N")).endswith(
        "The Modes rows are in another order now, which changes nothing in SolidWorks: it keeps 2H as the mode it was "
        "saved in, and Build again… would save the next revision in 4L.")
    assert ui_text.modes_record_line(record, modes=("2h", "N", "4H", "4L")).endswith(
        "The Modes rows are in another order now, which changes nothing in SolidWorks: it keeps 2H as the mode it was "
        "saved in.")
    for same in (MODES, ("2h", "4h", "n", "4l"), ("2H", "4H", "N", "4X"), ("2H", "4H", "N")):
        assert "another order" not in ui_text.modes_record_line(record, modes=same)


def test_the_footer_reads_the_modes_rows_from_the_workbook_and_the_positions_from_the_window(ready):
    spec = dataclasses.replace(ready.spec, modes=tuple(SimpleNamespace(name=m) for m in ("N", "2H", "4H", "4L")))
    a = dataclasses.replace(ready, spec=spec)
    update = _update(parts=(), moved_shafts=(), replaced=(), layout=None)
    f = _footer(a, record=_tc_record(), plan=_again(), update=update, positions_per_configuration=False)
    assert "Build again… would save the next revision in N." in f.text and ui_text.TURN_CAN_SHOW_ELSEWHERE in f.text


def _tc_update(**changes):
    refs = tuple(swbuild.MateRef(m.name, m.kind, m.gears, m.shaft, values=m.values, modes=m.modes)
                 for m in _tc_mates())
    slide_values = tuple((name, m, v) for name, vs in SLIDE_VALUES.items() for m, v in zip(MODES, vs))
    motion = dict(mates=refs, configurations=MODES, slide_values=slide_values,
                  on_sets=tuple(ON_SETS.items()))
    motion.update(changes.pop("motion", {}))
    fields = dict(motion=swbuild.MotionUpdate(**motion), parts=(), layout=None, moved_shafts=(), replaced=(),
                  assembly=TC_ASM)
    fields.update(changes)
    return UpdatePlan(**fields)


def _tc_moved(**values):
    fields = dict(configuration="4H", positions_per_configuration=True)
    fields.update(values)
    return _moved(**fields)


def test_the_update_summary_moves_a_slide_in_one_mode_and_switches_a_coupling():
    values = tuple((n, m, 66.5 if (n, m) == ("RangeSlv along Rear", "4L") else v)
                   for n, vs in SLIDE_VALUES.items() for m, v in zip(MODES, vs))
    assert _clean(ui_text.update_summary(_tc_update(motion=dict(slide_values=values)))) == (
        "Update SolidWorks will move RangeSlv in 4L to 66.5 mm along Rear.")
    # J14: 4H's ModeSlv pick 4WD -> 2WD: its value in 4H, and the coupling to FrontDog off there.
    values = tuple((n, m, 96.0 if (n, m) == ("ModeSlv along Rear", "4H") else v)
                   for n, vs in SLIDE_VALUES.items() for m, v in zip(MODES, vs))
    on_sets = tuple((n, ("4L",) if n == "ModeSlv engages FrontDog" else on) for n, on in ON_SETS.items())
    assert _clean(ui_text.update_summary(_tc_update(motion=dict(slide_values=values, on_sets=on_sets)))) == (
        "Update SolidWorks will move ModeSlv in 4H to 96 mm along Rear, and switch the mate ModeSlv engages FrontDog "
        "off in 4H.")
    assert ui_text.update_summary(_tc_update()).startswith("SolidWorks already matches the workbook on record")


@pytest.mark.parametrize("positions", [True, False, None])
def test_a_quiet_update_says_where_it_worked_and_that_it_did_not_show_the_other_modes(positions):
    """§9.11: every quiet Update of a gearbox with modes says it, always. The reason it gives is the one known: the
    mode it worked in needed nothing (since the review of W8 s2, where a turn showed in every mode, it no longer says
    "since nothing needed changing" of modes it did not read). The same words whatever the positions switch says."""
    result = _tc_moved(positions_per_configuration=positions)
    text, ok = ui_text.gearbox_update_status(_tc_update(), result)
    assert (text, ok) == (
        "SolidWorks already matches the workbook: nothing was changed. It worked in 4H, the configuration that was "
        "active; it did not show the other modes, since nothing in 4H needed changing.", True)
    assert ui_text.mode_update_lines(_tc_update(), result) == [
        "It worked in 4H, the configuration that was active; it did not show the other modes, since nothing in 4H "
        "needed changing."]
    assert ui_text.mode_update_lines(_update(), _moved()) == []
    # A result on a gearbox with modes that names no configuration still says the others were not shown.
    assert ui_text.gearbox_update_status(_tc_update(), _moved(positions_per_configuration=positions)) == (
        "SolidWorks already matches the workbook: nothing was changed. It worked in the configuration that was "
        "active; it did not show the other modes, since nothing there needed changing.", True)


def test_an_update_that_showed_the_other_modes_says_so_and_that_the_assembly_reads_modified():
    part = _path("Sleeve_m1.5_N30")
    result = _tc_moved(parts=[swbuild.UpdateResult(document="Sleeve_m1.5_N30", changed=["Teeth"], rebuilt=True)],
                       visited=["2H", "N", "4L"], changed=[part])
    update = _tc_update(parts=(PartUpdate(part, ("RangeSlv",), None, None, (), changed=True),))
    text, ok = ui_text.gearbox_update_status(update, result)
    assert _clean(text) == (
        "Updated SolidWorks: changed 1 variable in Sleeve_m1.5_N30; no interference between the gears where they "
        "stand. It worked in 4H, the configuration that was active, then showed and checked 2H, N and 4L and left the "
        "assembly in 4H. Showing them leaves TransferCase.SLDASM marked modified in SolidWorks, although nothing in "
        "it changed. Save Sleeve_m1.5_N30 in SolidWorks to keep it.")
    assert "quiet" not in text and "nothing needed changing" not in text
    one = ui_text.gearbox_update_status(update, dataclasses.replace(result, visited=["2H"]))[0]
    assert "then showed and checked 2H and left the assembly in 4H. Showing it leaves TransferCase.SLDASM" in one


def test_after_update_slides_and_flags_are_said_once_across_modes():
    result = _tc_moved(slid=[("RangeSlv along Rear", "4H", 47.0), ("RangeSlv along Rear", "2H", 47.0),
                             ("RangeSlv along Rear", "4L", 67.0)],
                       values_restored=[("ModeSlv along Rear", "4H"), ("ModeSlv along Rear", "4L")],
                       unsuppressed_in=[("RangeSlv engages LoDog", "4L")],
                       suppressed_in=[("RangeSlv engages InDog", "N"), ("RangeSlv engages InDog", "4L")],
                       visited=["2H", "N", "4L"], put_in=list(MODES), placed=["RangeSlv", "ModeSlv"],
                       modes=[swbuild.ModeCheck(m) for m in MODES], changed=[TC_ASM])
    text, ok = ui_text.gearbox_update_status(_tc_update(), result)
    assert (_clean(text), ok) == (
        "Updated SolidWorks: moved RangeSlv in 4H and 2H to 47 mm and in 4L to 67 mm along Rear, set ModeSlv's place "
        "in 4H and 4L back to 106 mm, where it had been changed in SolidWorks, turned the mate RangeSlv engages LoDog "
        "back on in 4L, suppressed the mate RangeSlv engages InDog again in N and 4L, where it was on, re-placed "
        "RangeSlv and ModeSlv in every mode; no interference between the gears in any mode, where they stand. It "
        "worked in 4H, the configuration that was active, then showed and checked 2H, N and 4L and left the assembly "
        "in 4H. Save TransferCase in SolidWorks to keep it.", True)


def test_a_flag_a_workbook_edit_changes_is_a_switch_not_a_repair():
    result = _tc_moved(suppressed_in=[("ModeSlv engages FrontDog", "4H")], unsuppressed_in=[
        ("ModeSlv engages FrontDog", "N")], visited=["2H", "N", "4L"], changed=[TC_ASM])
    lines = ui_text.mode_update_lines(_tc_update(), result)
    assert lines[0] == "Switched the mate ModeSlv engages FrontDog on in N and off in 4H."


@pytest.mark.parametrize("positions, said", [
    (True, "A turn you give the gears in one mode stays in that mode."),
    (False, "A turn you give the gears in one mode can show in other modes, so a dog can stand across its sleeve in "
            "another; to put the gears back there, press Update SolidWorks with that mode showing."),
    (None, ""),
])
def test_the_turning_note_promises_only_what_an_update_does(positions, said):
    """Since the review of W8 s2: an Update pressed in a mode whose train is in step puts nothing and judges no other
    mode, so the shared-positions note no longer says Update puts the gears back, only where pressing it does."""
    assert ui_text.turning_note(positions) == said
    assert ui_text.switching_note(positions) == ("Switching mode never by itself puts a dog tooth on tooth."
                                                 if positions is True else "")


@pytest.mark.parametrize("positions", [True, False, None])
def test_a_quiet_update_that_found_the_gears_turned_in_step_warns_of_the_other_modes_only_where_a_turn_is_shared(
        positions):
    """W8-INTERFACES §9.18 (the review of its commits, point 1): the train turned in the mode showing, in step there,
    nothing put and nothing shown. The footer then shows this status alone, so where the running version shows a
    turn in every mode the status itself says another mode may stand with a dog across its sleeve."""
    result = _tc_moved(turned=True, configuration="2H", positions_per_configuration=positions)
    text, ok = ui_text.gearbox_update_status(_tc_update(), result)
    warning = ("This version of SolidWorks can show that turn in other modes, so a dog may stand across its sleeve in "
               "another; to put the gears back there, press Update SolidWorks with that mode showing.")
    assert ok and text == (
        "SolidWorks already matches the workbook: nothing was changed. The gears stand where they were turned in "
        "SolidWorks. " + (warning + " " if positions is False else "") + "It worked in 2H, the configuration that "
        "was active; it did not show the other modes, since nothing in 2H needed changing.")
    assert ui_text.TURN_SHOWN_ELSEWHERE == warning
    # not after a put, which shows and checks every mode (§9.18, J13), nor on a gearbox without modes
    put = _tc_moved(turned=True, configuration="2H", positions_per_configuration=False, placed=["RangeSlv"],
                    put_in=["2H"], visited=["4H", "N", "4L"], changed=[TC_ASM])
    assert warning not in ui_text.gearbox_update_status(_tc_update(), put)[0]
    assert warning not in " ".join(ui_text.motion_update_lines(_motion_update(), _moved(turned=True)))
    # nor after a changed Update that put no mated gear but showed and checked every other mode (the review of the
    # fixes, point 4: the visit has just looked at them)
    part = _path("Sleeve_m1.5_N30")
    visited = _tc_moved(turned=True, configuration="2H", positions_per_configuration=False, placed=[],
                        visited=["4H", "N", "4L"], changed=[part],
                        parts=[swbuild.UpdateResult(document="Sleeve_m1.5_N30", changed=["Teeth"], rebuilt=True)])
    text = ui_text.gearbox_update_status(_tc_update(parts=(PartUpdate(part, ("RangeSlv",), None, None, (),
                                                                       changed=True),)), visited)[0]
    assert "The gears stand where they were turned in SolidWorks." in text and warning not in text


@pytest.mark.parametrize("earlier", ["not saved", "lost"])
def test_after_an_earlier_unsaved_update_the_warning_needs_no_antecedent(earlier):
    """The review of the fixes, point 3: after an earlier unsaved Update the gears stand "as they were found", so the
    warning does not say "that turn"."""
    result = _tc_moved(turned=True, configuration="2H", positions_per_configuration=False)
    text = ui_text.gearbox_update_status(_tc_update(), result, finished=_finished(earlier))[0]
    found = ("This version of SolidWorks can show the gears at the same turn in other modes, so a dog may stand across "
             "its sleeve in another; to put the gears back there, press Update SolidWorks with that mode showing.")
    assert ui_text.GEARS_SHOWN_ELSEWHERE == found
    assert text.count(found) == 1 and "that turn" not in text
    assert "The gears stand as they were found in SolidWorks. " + found in text
    shown_where_turned = ui_text.gearbox_update_status(_tc_update(), result)[0]
    assert "The gears stand where they were turned in SolidWorks. " + ui_text.TURN_SHOWN_ELSEWHERE in shown_where_turned
    for positions in (True, None):                    # neither wording where a turn stays in its mode or is unknown
        other = _tc_moved(turned=True, configuration="2H", positions_per_configuration=positions)
        text = ui_text.gearbox_update_status(_tc_update(), other, finished=_finished(earlier))[0]
        assert "The gears stand as they were found in SolidWorks." in text and "This version of SolidWorks" not in text


@pytest.mark.parametrize("kind", ["not saved", "lost"])
def test_after_an_earlier_unsaved_update_a_crossed_coupling_is_said_once_and_no_turn_is_laid_to_the_user(kind):
    """W8-REVIEW-LATE-FIXES S1: 4L worked in, RangeSlv across LoDog, every mode put, the switch False, an earlier
    Update not saved. The pair is said once, by the earlier-update sentence (``Finished.out_of_step_after_update`` is
    the result's out_of_step, workbook.update), and "the turn may have been given in another" is not said."""
    from gear_generator.workbook.gearbox import UPDATE_LOST
    earlier = UPDATE_LOST if kind == "lost" else "not saved"
    result = _tc_moved(configuration="4L", out_of_step=[("RangeSlv", "LoDog")], put_in=["2H", "4H", "N", "4L"],
                       visited=["2H", "4H", "N"], placed=["RangeSlv"], changed=[TC_ASM],
                       positions_per_configuration=False)
    text = ui_text.gearbox_update_status(_tc_update(), result,
                                         finished=_finished(earlier, pairs=[("RangeSlv", "LoDog")]))
    told = {"not saved": "RangeSlv and LoDog were not in step as the last Update SolidWorks, which is not saved, has "
                         "them on record; they are in step again.",
            "lost": "The last Update SolidWorks was not saved before TransferCase.SLDASM was closed, so its changes "
                    "were made again: RangeSlv and LoDog are back in step with each other."}[kind]
    assert text == ("Updated SolidWorks: re-placed RangeSlv in every mode; no interference between the gears where they "
                    f"stand. {told} It worked in 4L, the configuration that was active, then showed and checked 2H, 4H "
                    "and N and left the assembly in 4L. Save TransferCase in SolidWorks to keep it.", True)
    fresh = ui_text.gearbox_update_status(_tc_update(), result)[0]      # with no earlier Update: as before
    assert ("In 4L, RangeSlv's teeth stood across LoDog's; the gears of 4L are back at the turn they were built at. "
            "This version of SolidWorks can show a turn given in one mode in the others, so the turn may have been "
            "given in another.") in fresh


def _put_and_visited(positions, **values):
    """A quiet Update that found 4H's coupling out of step, put 4H, then showed and checked the others (J13): 2H and N
    found at the built turn, 4L found with a gear off its axis."""
    fields = dict(out_of_step=[("RangeSlv", "InDog")], put_in=["4H"], placed=["RangeSlv", "InDog"],
                  changed=[TC_ASM], visited=["2H", "N", "4L"], positions_per_configuration=positions,
                  modes=[swbuild.ModeCheck("2H"), swbuild.ModeCheck("N"), swbuild.ModeCheck("4L", off_axis=["FOut"]),
                         swbuild.ModeCheck("4H", out_of_step=[("RangeSlv", "InDog")])])
    fields.update(values)
    return _tc_moved(**fields)


@pytest.mark.parametrize("positions", [True, False, None])
def test_after_a_put_in_the_mode_worked_in_visited_modes_read_at_the_built_turn_are_said_with_shared_positions(
        positions):
    lines = ui_text.mode_update_lines(_tc_update(), _put_and_visited(positions))
    teeth = "In 4H, RangeSlv's teeth stood across InDog's; the gears of 4H are back at the turn they were built at."
    shared = ("This version of SolidWorks can show a turn given in one mode in the others, so the turn may have been "
              "given in another.")
    built = "The gears of 2H and N stood at the turn they were built at when Update SolidWorks showed them."
    worked = ("It worked in 4H, the configuration that was active, then showed and checked 2H, N and 4L and left the "
              "assembly in 4H.")
    assert lines == ([teeth, shared, built, worked] if positions is False else [teeth, worked])


def test_the_visited_modes_at_the_built_turn_are_only_those_read_so():
    one = ui_text.mode_update_lines(_tc_update(), _put_and_visited(False, modes=[
        swbuild.ModeCheck("2H"), swbuild.ModeCheck("N", turned=True), swbuild.ModeCheck("4L", out_of_step=[("a", "b")]),
        swbuild.ModeCheck("4H")]))
    assert "The gears of 2H stood at the turn they were built at when Update SolidWorks showed it." in one
    put_too = ui_text.mode_update_lines(_tc_update(), _put_and_visited(False, put_in=["4H", "2H", "N"]))
    assert not any(line.startswith("The gears of") for line in put_too)        # put there: not a reading of a turn
    not_put_here = ui_text.mode_update_lines(_tc_update(), _put_and_visited(False, put_in=["2H"]))
    assert not any(line.startswith("The gears of") for line in not_put_here)   # nothing put in the mode worked in


@pytest.mark.parametrize("positions", [True, False, None])
def test_two_crossed_couplings_in_one_mode_are_each_said_and_the_gears_said_back_once(positions):
    """W8 s2's quiet Update in 4L found RangeSlv with LoDog and ModeSlv with FrontDog out of step: one sentence per
    pair, "the gears of 4L are back …" once, on the last, and the shared-turn sentence once (the review of ruling
    9.18's commits, point 2)."""
    result = _tc_moved(configuration="4L", out_of_step=[("RangeSlv", "LoDog"), ("ModeSlv", "FrontDog")],
                       put_in=["4L"], placed=["RangeSlv", "ModeSlv", "LoDog", "FrontDog"], changed=[TC_ASM],
                       positions_per_configuration=positions)
    lines = ui_text.mode_update_lines(_tc_update(), result)
    assert lines[:2] == ["In 4L, RangeSlv's teeth stood across LoDog's.",
                         "In 4L, ModeSlv's teeth stood across FrontDog's; the gears of 4L are back at the turn they "
                         "were built at."]
    shared = ("This version of SolidWorks can show a turn given in one mode in the others, so the turn may have been "
              "given in another.")
    assert lines.count(shared) == (1 if positions is False else 0)
    assert sum("are back at the turn" in line for line in lines) == 1
    if positions is False:
        assert lines[2] == shared
    # The full status says each crossed coupling once, in the per-mode form: never also "… had been turned out of
    # step with each other in SolidWorks; they are back in mesh." (a coupling is not a mesh).
    text = _clean(ui_text.gearbox_update_status(_tc_update(), result)[0])
    assert "out of step with each other" not in text and "back in mesh" not in text
    assert text.count("RangeSlv's teeth stood across LoDog's") == 1 and text.count("ModeSlv's teeth stood across") == 1


def test_a_mesh_out_of_step_on_a_gearbox_with_modes_is_still_said_as_a_mesh():
    """Only couplings move to the per-mode form; a mesh proper keeps _motion_after's sentence."""
    result = _tc_moved(configuration="4L", out_of_step=[("InPin", "InGear")], put_in=["4L"], placed=["InPin"],
                       changed=[TC_ASM])
    assert ui_text.motion_update_lines(_tc_update(), result)[0] == (
        "InPin and InGear had been turned out of step with each other in SolidWorks; they are back in mesh.")


def test_a_coupling_out_of_step_is_said_only_in_the_mode_it_was_found_and_put_in():
    result = _tc_moved(out_of_step=[("RangeSlv", "InDog")], put_in=["4H"], placed=["RangeSlv", "InDog"],
                       changed=[TC_ASM], visited=["2H", "N", "4L"])
    lines = ui_text.mode_update_lines(_tc_update(), result)
    assert lines[0] == ("In 4H, RangeSlv's teeth stood across InDog's; the gears of 4H are back at the turn they were "
                        "built at.")
    assert "another" not in " ".join(lines)
    shared = ui_text.mode_update_lines(_tc_update(), dataclasses.replace(result, positions_per_configuration=False))
    assert shared[1] == ("This version of SolidWorks can show a turn given in one mode in the others, so the turn may "
                         "have been given in another.")
    unknown = ui_text.mode_update_lines(_tc_update(), dataclasses.replace(result, positions_per_configuration=None))
    assert "another" not in " ".join(unknown)
    not_put = ui_text.mode_update_lines(_tc_update(), dataclasses.replace(result, put_in=["2H"]))
    assert not any("teeth" in line for line in not_put)


def test_a_configuration_the_app_did_not_make_is_left_and_said():
    lines = ui_text.mode_update_lines(_tc_update(), _tc_moved(extra_configurations=["Exploded"]))
    assert lines[-1] == ("TransferCase.SLDASM also has a configuration the app did not make (Exploded); Update "
                         "SolidWorks left it as it is.")
    two = ui_text.mode_update_lines(_tc_update(), _tc_moved(extra_configurations=["Exploded", "Display"]))
    assert two[-1].endswith("configurations the app did not make (Exploded and Display); Update SolidWorks left them "
                            "as they are.")


def test_a_mode_added_needs_build_again_with_bs_sentence_whole(ready):
    why = ("The Modes sheet has a new mode, 4X, and each mode's configuration is made when the assembly is built, so "
           "it needs a new revision.")
    f = _footer(ready, record=_tc_record(), plan=_again(), update=_update(structural=(why,)))
    assert f.text.startswith(why[:-1] + ". Update SolidWorks offers to build again as")


def test_the_progress_of_a_mode():
    assert ui_text.progress_text(swbuild.Step(swbuild.STAGE_MODE, "4L", 4, 4)) == (
        "Building in SolidWorks: mode 4L, 4 of 4…")
    assert ui_text.progress_text(swbuild.Step(swbuild.STAGE_MODE, "4L"), updating=True) == (
        "Updating SolidWorks: checking mode 4L…")


def _tc_assessed(make):
    from workbook_fixtures import e4_transfer_case, transfer_case_parallel
    spec = {"parallel": transfer_case_parallel, "e4": e4_transfer_case}[make]()
    return assess.assess(dataclasses.replace(spec, source_path="C:\\Books\\TransferCase.xlsx"), [], "C:\\Out\\")


def test_the_speeds_panel_in_each_mode_through_bs_modes():
    """§2.3 through B's per-mode solve, ratio home (``ModeReport.ratio``, ``ratio_why``, ``driven``) and J17's
    split (``Motion.shared``, ``past_split``): a member a mode leaves free reads as free, never 0 rpm."""
    a = _tc_assessed("parallel")
    lines = {m.name: ui_text.mode_speed_lines(a.spec, a.report, m.name) for m in a.report.modes}
    assert lines["4H"] == ([
        "4H: Rear 1500\u00a0rpm · Front 1500\u00a0rpm · 1.000 : 1",
        "In 4H, RangeSlv engages InDog and ModeSlv engages FrontDog.",
        "In    1500.0\u00a0rpm anticlockwise · 10.00\u00a0N·m",
        "Lay   750.0\u00a0rpm clockwise",
        "Lo    375.0\u00a0rpm anticlockwise",
        "Rear  1500.0\u00a0rpm anticlockwise · 10.00\u00a0N·m, shared with FrontDrv (the share depends on the loads)",
        "FrontDrv  1500.0\u00a0rpm anticlockwise · — (past a split)",
        "Idler  2250.0\u00a0rpm clockwise · — (past a split)",
        "Front  1500.0\u00a0rpm anticlockwise · — (past a split)"], "seen from +Z")
    assert lines["2H"][0][:2] == ["2H: Rear 1500\u00a0rpm · Front not driven · 1.000 : 1",
                                  "In 2H, RangeSlv engages InDog."]
    assert lines["2H"][0][-3:] == ["FrontDrv  turns freely", "Idler  turns freely", "Front  turns freely"]
    assert lines["N"][0][:2] == ["N: neutral — Rear, FrontDrv, Idler and Front turn freely.",
                                 "In N, no sleeve engages a dog."]
    assert lines["4L"][0][0] == "4L: Rear 375\u00a0rpm · Front 375\u00a0rpm · 4.000 : 1"
    assert "Lo    375.0\u00a0rpm anticlockwise · 38.42\u00a0N·m" in lines["4L"][0]
    for m in a.report.modes:
        said = lines[m.name][0]
        assert not re.search(r"\s0\.0\u00a0rpm", " ".join(said)) and "same way" not in " ".join(said)
        assert ui_text.speeds_prose_rows(m.motion, said, mode=True) == {0, 1}
    assert ui_text.mode_speed_lines(a.spec, a.report, "4l") == lines["4L"]
    assert ui_text.mode_speed_lines(a.spec, a.report, "4X") == ([], "")
    e4 = _tc_assessed("e4")
    neutral = ui_text.mode_speed_lines(e4.spec, e4.report, "N")[0]
    assert neutral[0] == "N: neutral — Rear, FrontDrv, Idler and Front turn freely." and "Ring  held still" in neutral
    assert ("Planet  750.0\u00a0rpm clockwise, 1125.0\u00a0rpm clockwise relative to Carrier · 3 copies"
            in neutral)


def test_the_implicit_mode_has_no_name_to_lead_with():
    implicit = checks.ModeReport("", engaged=(("RangeSlv", "InDog"),), out_of_mesh=(("G4", "G5"),))
    assert ui_text._engaged_sentence(implicit) == (
        "With every slider at its position 0, RangeSlv engages InDog; G4 and G5 are out of mesh.")


def test_the_workers_refusal_of_modes_on_a_version_is_shown_whole_as_a_build_refusal(monkeypatch):
    """§9.5: the per-version refusal is the worker's (``swbuild._modes_version_refusal``), before anything is made;
    the window shows it whole, naming the version as the window does and no API word."""
    from gear_generator import findings
    monkeypatch.setattr(findings, "SLIDE_VALUE_PER_CONFIGURATION_ON_2024", None, raising=False)
    why = swbuild._modes_version_refusal((32, 0, 0))
    shown = ui_text.job_failed(swbuild.BuildError(why))
    assert shown == why and "SolidWorks 2024" in shown and shown.endswith("nothing is made.")
    for word in ("Flip", "Reverse", "entit", "SystemValue", "Suppress", "findings", "revision", "IConfiguration"):
        assert word not in shown


def test_any_mode_is_said_only_when_every_mode_was_checked():
    """§9.11, §9.13: an Update that showed 4H and 2H of four modes says those two, never "any mode"."""
    asm = TC_ASM
    def status(checked):
        result = _tc_moved(visited=[m for m in checked if m != "4H"], modes=[swbuild.ModeCheck(m) for m in checked],
                           changed=[asm], placed=["InPin"], put_in=["4H"])
        return ui_text.gearbox_update_status(_tc_update(), result)[0]
    assert "; no interference between the gears in 4H and 2H, where they stand." in status(["4H", "2H"])
    assert "; no interference between the gears in any mode, where they stand." in status(["4H", "2h", "n", "4L"])
    assert "; no interference between the gears in 4H, where they stand." in status(["4H"])
    assert "any mode" not in status(["4H", "2H"])
    built = ui_text.gearbox_status(_tc_plan(), _tc_built(modes=[swbuild.ModeCheck("2H"), swbuild.ModeCheck("4H")]))
    assert "; no interference between the gears in 2H and 4H, where they stand." in built[0]


def test_an_error_in_one_mode_never_hides_a_clash_in_another():
    clash = swbuild.Clash(components=("a", "b"), gears=("RangeSlv", "InDog"), volume=0.5)
    modes = [swbuild.ModeCheck("2H", clashes=[clash]), swbuild.ModeCheck("4H"), swbuild.ModeCheck("N"),
             swbuild.ModeCheck("4L", interference_error="SolidWorks returned nothing.")]
    text, ok = ui_text.gearbox_status(_tc_plan(), _tc_built(modes=modes))
    assert not ok and _clean(text).startswith(
        "Built 3 parts, TransferCase_Layout and TransferCase.SLDASM. Check: in 2H, RangeSlv and InDog interfere, 0.5 "
        "mm³; look where they meet in TransferCase.SLDASM. Interference could not be checked in 4L: SolidWorks "
        "returned nothing. Look at each mesh in TransferCase.SLDASM by eye. Its gears are mated")


# The real-plan variants (the review): B's plan_gearbox and finish, A's build_gearbox on its fake, beside the hand-made
# shapes above. The Update's and the record's wait for A's Update across configurations (§9.2's gate) and a finish
# the fake's result can pass.

from test_swbuild import mode_findings  # noqa: E402,F401 - the fixture: every finding a build with modes reads


def _tc_real_plan(sw):
    a = _tc_assessed("parallel")
    plan = gearbox.plan_gearbox(a, None, exists=sw.exists, read_sidecar=lambda p: None)
    assert plan.refusal == ""
    return plan


def test_the_real_plan_names_its_modes_before_build(mode_findings):  # noqa: F811
    from test_swbuild import FakeSolidWorks
    line = ui_text.motion_ready_line(_tc_real_plan(FakeSolidWorks()))
    assert line == ("Its gears are mated to their shafts and, as each mode engages them, to each other, so they turn "
                    "together in SolidWorks. It has 4 modes, 2H, 4H, N and 4L: each becomes a configuration of the "
                    "assembly, and it opens in 2H.")


def test_a_real_build_with_modes_on_the_fake_is_said_mode_by_mode(mode_findings):  # noqa: F811
    from test_swbuild import FakeSolidWorks
    sw = FakeSolidWorks()
    plan = _tc_real_plan(sw)
    result = swbuild.build_gearbox(sw, **plan.build_kwargs(), exists=sw.exists)
    assert result.ok and [m.name for m in result.modes] == list(MODES)
    text, ok = ui_text.gearbox_status(plan, result)
    assert ok and _clean(text).startswith(
        "Built 6 parts, TransferCase_Parallel_Layout and TransferCase_Parallel.SLDASM; no interference between the "
        "gears in any mode, where they stand. Its gears are mated to turn in each of its 4 modes, one configuration "
        "each (2H, 4H, N and 4L), and SolidWorks reports no mate in error in any of them: it opens in 2H; to switch "
        "mode, double-click another mode's configuration in SolidWorks' ConfigurationManager. Drag InPin in "
        "SolidWorks to turn one train and FrontDog to turn the other. RangeSlv and ModeSlv slide along Rear, each to "
        "its place in each mode.")
    assert (ui_text.TURN_STAYS in text) == (result.positions_per_configuration is True)
    assert (ui_text.SWITCH_IN_STEP in text) == (result.positions_per_configuration is True)
    for word in ("Flip", "Reverse", "entities", "same way"):
        assert word not in text


def test_the_mode_chooser_says_it_changes_only_the_window():
    """J21: the chooser picks what the window shows, never SolidWorks' configuration; once an assembly with modes is
    on record (the footer tells the user to switch mode in SolidWorks) it says so."""
    built = ui_text.mode_chooser_note(_tc_record())
    assert built == ("The mode chosen here changes only what this window shows; it does not switch the mode "
                     "SolidWorks shows.")
    for record in (None, _record(assembly=False), _turning_record()):
        assert ui_text.mode_chooser_note(record) == "The mode chosen here changes only what this window shows."
    for word in ("configuration", "Configuration", "Flip", "Show", "Suppress"):
        assert word not in built
    a = _tc_assessed("parallel")
    for entry in a.report.modes:
        lines = ui_text.mode_speed_lines(a.spec, a.report, entry.name)[0] + [built]
        assert ui_text.speeds_prose_rows(entry.motion, lines, mode=True, chooser=True) == {0, 1, len(lines) - 1}
    from fractions import Fraction
    motion = kinematics.Motion(speeds={"S": Fraction(1000)}, torque_note="The torque through C's planetary stage "
                                                                          "is not worked out.")
    lines = ["S     1000.0 rpm anticlockwise", "The torque through C's planetary stage is not worked out.", built]
    assert ui_text.speeds_prose_rows(motion, lines, chooser=True) == {1, 2}
    assert ui_text.speeds_prose_rows(motion, lines[:2]) == {1}


def _end_view(spec, mode=None):
    """The end view as the window lays it out (workbook_gui._draw_end_view; the boards' end_view_svg)."""
    from gear_generator import preview, workbook_gui
    from gear_generator.workbook import geometry as wb_geometry
    a = assess.assess(dataclasses.replace(spec, source_path="C:\\Books\\X.xlsx"), [], "C:\\Out\\")
    entry = next((m for m in a.report.modes if m.name == mode), None)
    carriers = {c: p[:2] for c, (p, _) in wb_geometry.carrier_axes(a.spec, a.report).items()}
    placed = {**a.report.layout.placed, **(entry.placed if entry is not None else {})}
    w, h = workbook_gui.END_VIEW
    return preview.layout_gearbox(placed, a.report.theta, w, h, step=2, carriers=carriers,
                                  shafts=[s.id for s in a.spec.shafts])


def test_the_end_view_readout_always_fits_and_lists_up_to_four_heights():
    """D's 392 px end view: a transfer case in 2H has 7 face heights, so it is counted; every gearbox before W8
    reads as it did, byte for byte."""
    from test_workbook_planetary import on_z_minus, planetary_4to1
    from test_workbook_turned import bevel_reducer, crossed_slant
    from workbook_fixtures import e4_transfer_case, transfer_case_parallel
    assert ui_text.end_view_readout(_end_view(reducer())) == "z 7.5 · z 27 · origin"
    assert ui_text.end_view_readout(_end_view(bevel_reducer())) == "z 5 · z 60 · origin"
    assert ui_text.end_view_readout(_end_view(crossed_slant())) == "z 8 · z 10 · origin"
    assert ui_text.end_view_readout(_end_view(planetary_4to1())) == "z 10 · z 30 · origin"
    assert ui_text.end_view_readout(_end_view(on_z_minus())) == "z -30 · z -10 · origin"
    parallel = {m: ui_text.end_view_readout(_end_view(transfer_case_parallel(), m)) for m in MODES}
    assert parallel == {"2H": "7 face heights, z 10 to 130 · origin", "4H": "6 face heights, z 10 to 130 · origin",
                        "N": "8 face heights, z 10 to 130 · origin", "4L": "6 face heights, z 10 to 130 · origin"}
    e4 = {m: ui_text.end_view_readout(_end_view(e4_transfer_case(), m)) for m in MODES}
    assert e4 == {"2H": "6 face heights, z 20 to 130 · origin", "4H": "5 face heights, z 20 to 130 · origin",
                  "N": "7 face heights, z 20 to 130 · origin", "4L": "5 face heights, z 20 to 130 · origin"}
    view = SimpleNamespace(planes=[7.5, 27.0, 30.0, 47.0], origin=None)
    assert ui_text.end_view_readout(view) == "z 7.5 · z 27 · z 30 · z 47 · origin off view"
    long = SimpleNamespace(planes=[107.5, 127.5, 207.5, 227.5], origin=None)
    assert ui_text.end_view_readout(long) == "4 face heights · origin off view"
    wide = SimpleNamespace(planes=[-12.5, 10.0, 30.0, 50.0, 70.0], origin=(1, 1))
    assert ui_text.end_view_readout(wide) == "5 face heights, z -12.5 to 70 · origin"
    for v in (view, long, wide, _end_view(transfer_case_parallel(), "N")):
        assert len(ui_text.end_view_readout(v)) <= ui_text.VIEW_READOUT_CHARS


def test_gear_mates_whose_turning_no_read_reached_are_named_by_their_gears_and_asked_nothing():
    """§9.16 (A's ccb05ae): a quiet Update of TransferCase_Parallel standing in 2H leaves the two couplings off there
    unread; said as a fact, by the gears, never as a problem."""
    result = _tc_moved(configuration="2H", senses_unread=["ModeSlv engages FrontDog", "RangeSlv engages LoDog"])
    text, ok = ui_text.gearbox_update_status(_tc_update(), result)
    assert ok and text == (
        "SolidWorks already matches the workbook: nothing was changed. It worked in 2H, the configuration that was "
        "active; it did not show the other modes, since nothing in 2H needed changing. Which way ModeSlv and "
        "FrontDog, and RangeSlv and LoDog, turn against each other was not checked this time: their mates are "
        "switched off in 2H, the mode SolidWorks is showing, and are checked when an Update works in a mode that has "
        "them on.")
    for word in ("engages", "sense", "Reverse", "Flip", "press", "Check:", "error"):
        assert word not in text.split("needed changing. ")[1]
    one = ui_text.mode_update_lines(_tc_update(), _tc_moved(senses_unread=["RangeSlv engages LoDog"]))
    assert one[-1] == ("Which way RangeSlv and LoDog turn against each other was not checked this time: its mate is "
                       "switched off in 4H, the mode SolidWorks is showing, and is checked when an Update works in a "
                       "mode that has it on.")
    many = _tc_moved(senses_unread=["RangeSlv engages InDog", "RangeSlv engages LoDog", "ModeSlv engages FrontDog",
                                    "ModeSlv splined to RangeSlv", "InPin meshes LayGear"])
    assert ui_text.mode_update_lines(_tc_update(), many)[-1].startswith(
        "Which way RangeSlv and InDog, RangeSlv and LoDog, ModeSlv and FrontDog, and 2 more pairs, turn against each "
        "other was not checked this time: their mates")
    assert not any("not checked this time" in line for line in ui_text.mode_update_lines(_tc_update(), _tc_moved()))


def test_a_mode_that_jams_is_shown_whole_in_the_footer_with_its_longer_sentence():
    """B's 89f143b: a mode's own jam names what engages what; the footer and the Checks readout carry it whole."""
    from test_workbook_modes import JAM, assessed, with_mode
    a = assessed(with_mode(JAM, 0, positions=(("RangeSlv", "H"), ("ModeSlv", "J"))))
    jam = ("Modes row 2: in 2H RangeSlv engages InDog and ModeSlv engages LoDog, which joins In and Lo through Rear, and "
           "the meshes turn them at different speeds: as written the box is jammed in this mode.")
    assert [d.message for d in a.diagnostics if d.is_error] == [jam]
    assert ui_text.workbook_checks_readout(a.diagnostics).startswith("1 error")
    f = ui_text.workbook_footer(a, folder=P)
    assert (f.text, f.ok, f.build_enabled) == (f"Fix the workbook before building: {jam}", False, False)


def test_every_state_fits_its_column_and_a_long_gear_name_is_shortened_as_a_part_name_is():
    """GEAR_STATE_CHARS (D: the Gears panel reached 643 px on the W8 fixtures against LEFT_WIDTH 610): every state
    fits; a gear named in one is shortened head and tail by the Part column's rule, two different gears apart."""
    for make in ("parallel", "e4"):
        a = _tc_assessed(make)
        rows = {r[0]: r for r in ui_text.workbook_gear_rows(a.spec, a.parts, a.diagnostics)}
        assert rows["ModeSlv"][7:] == (ui_text.GEAR_STATE_SHARES, "same as RangeSlv")
        assert all(len(r[8]) <= ui_text.GEAR_STATE_CHARS for r in rows.values())
    spec = reducer()
    long_a, long_b = "Gear_Twenty_Chars_AB", "Gear_Other_Name_hars_AB"     # alike at 12: Gear…hars_AB
    gears = [dataclasses.replace(g, id=long_a) if g.id == "G2" else g for g in spec.gears]
    twins = [dataclasses.replace(g, id=f"{g.id}b", row=g.row + 10) for g in gears if g.id in ("G1", long_a)]
    spec = dataclasses.replace(spec, gears=tuple(gears) + tuple(twins))
    jobs = [PartJob("Gear_m1.5_N17", _path("Gear_m1.5_N17"), ("G1", "G1b"), GearSpec(), None,
                    BuildPlan("spur", "A", (NewPart(""),))),
            PartJob("Gear_m1.5_N68", _path("Gear_m1.5_N68"), (long_a, f"{long_a}b"), GearSpec(), None,
                    BuildPlan("spur", "A", (NewPart(""),)))]
    plan = SimpleNamespace(jobs=jobs, later=[])
    rows = {r[0]: r[8] for r in ui_text.workbook_gear_rows(spec, plan, [])}
    assert rows["G1b"] == "same as G1"
    assert rows[f"{long_a}b"] == "same as Gear…hars_AB" and len(rows[f"{long_a}b"]) <= ui_text.GEAR_STATE_CHARS
    # A second long gear that would read alike is lengthened apart, as the Part column does.
    jobs.append(PartJob("Gear_m1.5_N69", _path("Gear_m1.5_N69"), (long_b, "Other"), GearSpec(), None,
                        BuildPlan("spur", "A", (NewPart(""),))))
    spec2 = dataclasses.replace(spec, gears=spec.gears + (dataclasses.replace(gears[1], id=long_b, row=40),
                                                          dataclasses.replace(gears[1], id="Other", row=41)))
    rows = {r[0]: r[8] for r in ui_text.workbook_gear_rows(spec2, plan, [])}
    assert rows[f"{long_a}b"] != rows["Other"] and rows["Other"].startswith("same as Gear…")
    assert ui_text._mode_line(SimpleNamespace(shafts=()), checks.ModeReport("", ratio_why="neutral")) == "Neutral."


from gear_generator import findings  # noqa: E402

# -- What's Wrong where it stays (W9C-RUNS-REVIEW.md, the review of 1dc9350, §3; findings.WHATS_WRONG_STAYS_WITHOUT_A_
# REBUILD): said only on a SolidWorks measured to leave the box up, once, after the sentence it belongs to ------------

Y24, Y26 = (32, 5, 0), (34, 1, 1)


def _left_in_error(**values):
    """A press that changed G2's part, whose rebuild reported an error, and stopped there: the part left in error."""
    fields = dict(parts=[swbuild.UpdateResult(document="Gear_m1.5_N68.SLDPRT", changed=["No. of Teeth"],
                                              rebuilt=False)],
                  layout=None, placed=[], rebuilt=False, changed=[_path("Gear_m1.5_N68")],
                  failures=[("Gear_m1.5_N68.SLDPRT", "SolidWorks reported an error rebuilding Gear_m1.5_N68.")],
                  skipped="the layout part and the assembly, because Gear_m1.5_N68.SLDPRT failed")
    fields.update(values)
    return swbuild.GearboxUpdate(**fields)


def _held(**values):
    """The press again on a part still open in error: it stops before any write on that part alone."""
    fields = dict(parts=[], layout=None, placed=[], rebuilt=False, changed=[],
                  failures=[("Gear_m1.5_N68.SLDPRT", "SolidWorks reads Teeth in error in Gear_m1.5_N68.")],
                  skipped="the assembly, because Gear_m1.5_N68.SLDPRT is in error")
    fields.update(values)
    return swbuild.GearboxUpdate(**fields)


def _still():
    from types import SimpleNamespace
    return SimpleNamespace(still_in_error=[_path("Gear_m1.5_N68")])


def _three_forms(revision):
    """The three forms of gearbox_update_status that say the still-in-error sentence: the held stop alone, beside
    another failure, and in place of 'already matches'."""
    nothing = _updated(parts=[swbuild.UpdateResult(document="Gear_m1.5_N68.SLDPRT", unchanged=["No. of Teeth"],
                                                   rebuilt=True)], layout=None, placed=[], changed=[])
    beside = _held(failures=[("Gear_m1.5_N68.SLDPRT", "SolidWorks reads Teeth in error in Gear_m1.5_N68."),
                             ("Reducer_12to1.SLDASM", "SolidWorks did not answer.")])
    return [ui_text.gearbox_update_status(_update(), r, finished=_still(), revision=revision)[0]
            for r in (_held(), beside, nothing)]


def test_whats_wrong_stays_is_said_once_after_the_still_in_error_sentence_in_each_form_on_2024():
    said = ui_text.still_in_error_sentence(_still().still_in_error, ASM)
    alone, beside, quiet = _three_forms(Y24)
    assert alone == said + " " + ui_text.WHATS_WRONG_STAYS
    assert beside.endswith(said + " " + ui_text.WHATS_WRONG_STAYS) and beside.startswith("Update SolidWorks stopped.")
    assert quiet.startswith(said + " " + ui_text.WHATS_WRONG_STAYS)
    for text in (alone, beside, quiet):
        assert text.count("What's Wrong") == 1 and ui_text.WHATS_WRONG_NEXT not in text, text


@pytest.mark.parametrize("revision", [Y26, (34, 0, 0), ()])
def test_whats_wrong_stays_is_not_said_where_the_box_is_not_measured_to_stay(revision):
    assert all("What's Wrong" not in text for text in _three_forms(revision))


def test_whats_wrong_stays_is_not_said_on_2024_with_its_finding_unmeasured(monkeypatch):
    monkeypatch.setattr(findings, "WHATS_WRONG_STAYS_WITHOUT_A_REBUILD_ON_2024", None)
    assert all("What's Wrong" not in text for text in _three_forms(Y24))


def test_whats_wrong_next_is_said_once_in_a_stop_that_leaves_a_part_in_error_on_2024_in_place_of_after(monkeypatch):
    work = SimpleNamespace(in_error=["Sprocket-1"])                  # the user's work in error too: AFTER would come
    stopped = _left_in_error(user_work=work)
    text, ok = ui_text.gearbox_update_status(_update(), stopped, revision=Y24)
    assert not ok and "Gear_m1.5_N68 is left in error" in text, text
    assert text.count(ui_text.WHATS_WRONG_NEXT) == 1 and ui_text.WHATS_WRONG_AFTER not in text, text
    assert text.index("then press Update SolidWorks again.") < text.index(ui_text.WHATS_WRONG_NEXT)
    for revision in (Y26, ()):
        assert "What's Wrong" not in ui_text.gearbox_update_status(_update(), stopped, revision=revision)[0]
    monkeypatch.setattr(findings, "WHATS_WRONG_STAYS_WITHOUT_A_REBUILD_ON_2024", None)
    text, _ = ui_text.gearbox_update_status(_update(), stopped, revision=Y24)
    assert ui_text.WHATS_WRONG_NEXT not in text and text.count(ui_text.WHATS_WRONG_AFTER) == 1, text


def test_after_a_stop_with_the_users_work_in_error_and_no_part_left_in_error_after_is_still_said_once():
    work = SimpleNamespace(in_error=["Sprocket-1"])
    stopped = _updated(failures=[("Reducer_12to1.SLDASM", "SolidWorks did not answer.")], user_work=work,
                       skipped="the rest")
    text, ok = ui_text.gearbox_update_status(_update(), stopped, revision=Y24)
    assert not ok and text.count(ui_text.WHATS_WRONG_AFTER) == 1 and ui_text.WHATS_WRONG_NEXT not in text, text


def test_a_part_left_in_error_and_one_still_in_error_say_stays_alone_never_next_beside_it():
    from types import SimpleNamespace as NS
    stopped = _left_in_error()
    finished = NS(still_in_error=[_path("Gear_m1.5_N17")])
    text, _ = ui_text.gearbox_update_status(_update(), stopped, finished=finished, revision=Y24)
    assert text.count(ui_text.WHATS_WRONG_STAYS) == 1 and ui_text.WHATS_WRONG_NEXT not in text, text
    assert "What's Wrong" not in ui_text.gearbox_update_status(_update(), stopped, finished=finished, revision=Y26)[0]


# -- F1: what a printed gear and a gearbox's Process are told (PLAN-PRINTED §1.3, §2.1, §6; package C) -------------

from gear_generator.gears import kind_for  # noqa: E402
from gear_generator.spec import PROCESS_MACHINED, PROCESS_PRINTED  # noqa: E402

PRINTED_BACKLASH_WHAT = (
    "How much each tooth is thinned at the pitch circle so the pair does not bind: the space grows by this and the "
    "tooth shrinks by it, on both gears, so the play in the mesh is twice the number. Printed, blank uses 0.3 mm, or "
    "0.3 × module below module 1: room for walls printed a little fat, and a starting value until your own prints "
    "are measured. A slicer's X-Y compensation does the same job, so use one or the other, not both.")


def _printed(**fields):
    spec = GearSpec(process="printed", **fields)
    return kind_for(spec).derive(spec)


@pytest.mark.parametrize("fields, row", [
    ({}, "0.3 · printed default"),
    ({"module": "0.5", "teeth": "30"}, "0.15 · printed default"),          # 0.3 × module below module 1
    ({"kind": "helical", "helix_angle": "15"}, "0.3 · printed default"),
    ({"teeth": "60", "teeth_side": "internal"}, "0.3 · printed default"),
    ({"kind": "bevel", "teeth": "20", "mate_teeth": "40", "face_width": "10"}, "0.3 · printed default"),
    ({"backlash": "0.1"}, "0.1"),                                            # typed: as typed, printed or not
])
def test_a_printed_gears_derived_backlash_row_says_the_printed_default(fields, row):
    assert dict(ui_text.derived_rows(_printed(**fields)))["Backlash"] == row


def test_a_printed_gears_backlash_card_says_the_printed_default_and_the_bevels_toe():
    assert ui_text.explainer("backlash", _printed(), "Gear_m1.5_N25_P") == (
        "Backlash", "j", PRINTED_BACKLASH_WHAT,
        "blank → 0.3 mm · printed default · tooth 2.056 · space 2.656 · play in the mesh 0.6")
    assert ui_text.explainer("backlash", _printed(module="0.5", teeth="30"), "x")[3] == (
        "blank → 0.15 mm · printed default · tooth 0.635 · space 0.935 · play in the mesh 0.3")
    bevel = _printed(kind="bevel", teeth="20", mate_teeth="40", face_width="10")
    assert round(bevel.toe_scale, 2) == 0.70                                 # §2.1's 20 / 40 at module 1.5, face 10
    assert ui_text.explainer("backlash", bevel, "x")[3] == (
        "blank → 0.3 mm · printed default, 0.211 at the toe · tooth 2.433 · space 2.279 · play in the mesh 0.6")
    typed = ui_text.explainer("backlash", _printed(backlash="0.1"), "x")
    assert typed[2] == PRINTED_BACKLASH_WHAT and typed[3].startswith("0.1 mm · tooth ")


def test_the_backlash_card_takes_the_forms_process_when_the_gear_does_not_work_out():
    assert ui_text.explainer("backlash", None, printed=True)[2:] == (PRINTED_BACKLASH_WHAT, "check the fields")
    machined = ui_text.explainer("backlash", None, printed=False)[2]
    assert machined == ui_text.explainer("backlash", None)[2] and "Blank uses 0.3 × module" in machined
    # Only Backlash changes its copy: every other card is the machined gear's, printed or not.
    g, m = _printed(), KINDS["spur"].derive(GearSpec())
    for field in ui_text.GEAR_EXPLAINERS:
        if field != "backlash":
            assert ui_text.explainer(field, g, "x")[2] == ui_text.explainer(field, m, "x")[2], field


def test_the_forms_process_row_and_what_it_does_to_the_backlash_field():
    assert ui_text.PROCESS_LABELS == {PROCESS_PRINTED: "Printed", PROCESS_MACHINED: "Machined"}
    assert (ui_text.NOZZLE_PLACEHOLDER, ui_text.NOZZLE_HINT) == ("0.4", "the printer's line width")
    assert ui_text.BACKLASH_PLACEHOLDERS == {PROCESS_MACHINED: "0.3 × module", PROCESS_PRINTED: "0.3 · printed"}
    assert ui_text.BACKLASH_HINTS == {PROCESS_MACHINED: "ISO: 0.02–0.05 × m", PROCESS_PRINTED: "0.3 × m below m1"}


def _boxes(typed, resolved=None, cell="Box!B9", nozzle=""):
    """The Box as read (``typed``, "" for a blank) and as assessed (its blank resolved to ``resolved``)."""
    read = model.Box(name="R", process=typed, nozzle=nozzle, process_cell=cell)
    return read, dataclasses.replace(read, process=resolved if resolved is not None else typed)


@pytest.mark.parametrize("typed, resolved, cell, nozzle, line", [
    ("printed", None, "Box!B9", "", "Printed, 0.4 mm nozzle"),
    ("Printed", "printed", "Box!B9", "0.6", "Printed, 0.6 mm nozzle"),
    ("", "printed", "Box!B9", "", "Printed, 0.4 mm nozzle"),                  # a new gearbox left blank
    ("", "printed", "", "", "Printed, 0.4 mm nozzle"),                        # … with no row: Printed all the same
    ("", "machined", "Box!B9", "",
     "Machined, as built: type Printed beside Process on the Box sheet to print it"),
    ("", "machined", "", "",                                                  # built before F1: no Process row
     "Machined, as built: type Printed beside Process on the Box sheet to print it (add a row labelled Process)"),
    ("machined", None, "Box!B9", "", "Machined, as the Box sheet says: type Printed beside Process to print it"),
    ("MACHINED", "machined", "Box!B12", "0.6",
     "Machined, as the Box sheet says: type Printed beside Process to print it"),
    ("wood", None, "Box!B9", "", "Process does not read: the Checks panel says why"),
    ("", "wood", "Box!B9", "", "Process does not read: the Checks panel says why"),
    ("printed", None, "Box!B9", "x", "Printed; its Nozzle does not read: the Checks panel says why"),
    ("printed", None, "Box!B9", "0", "Printed; its Nozzle does not read: the Checks panel says why"),
])
def test_the_workbook_panels_process_line(typed, resolved, cell, nozzle, line):
    assert ui_text.workbook_process_line(*_boxes(typed, resolved, cell, nozzle)) == line
