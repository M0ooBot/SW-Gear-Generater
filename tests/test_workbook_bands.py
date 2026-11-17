"""W9b package B (ISSUE-1-PLAN §2.2-§2.4, §3, K8, K10; W9B-INTERFACES.md): a sleeve's two toothed bands and the relief
bore between, read from the Gears sheet's Start band and End band and judged per band; the hub kind and its rules;
the relief in the part's plan; the link record's schema 8 and a banded part's ``.gear.json`` at schema 2. Against
the fake only."""

import json
from dataclasses import replace

import pytest

from gear_generator import gears, spec as spec_mod, store, swbuild
from gear_generator.gears import clutch, helical, kind_for, plan_for
from gear_generator.gears.base import AddGlobal, LoftCut
from gear_generator.spec import GearSpec
from gear_generator.workbook import assess, gearbox, model, modes, schema, xlsx
from workbook_fixtures import range_box, range_box_fixed

BOOK = "C:\\B\\RangeBox_Fixed.xlsx"


def assessed(spec):
    return assess.assess(replace(spec, source_path=BOOK), [], "C:\\Out\\")


def with_gear(spec, gid, **changes):
    return replace(spec, gears=tuple(replace(g, **changes) if g.id == gid else g for g in spec.gears))


def said(a):
    return [(d.level, d.message) for d in a.diagnostics]


def errors(a):
    return [d.message for d in a.diagnostics if d.is_error]


# -- the Gears sheet's two columns ------------------------------------------------------------------------------------

def test_the_two_columns_follow_slides_numeric_in_mm_and_hub_is_a_kind_word():
    keys = [c.key for c in schema.GEARS.columns]
    assert keys[keys.index("slides") + 1:keys.index("slides") + 3] == ["start_band", "end_band"]
    assert keys[keys.index("end_band") + 1] == "part_name"
    for key, title in (("start_band", "Start band (mm)"), ("end_band", "End band (mm)")):
        column = schema.GEARS.column(key)
        assert column.numeric and not column.whole and column.title == title
        assert column.blank == "teeth over the whole face"
    assert schema.KINDS[-1] == "hub" and schema.GEARS.column("kind").canonical("Hub") == "hub"


def test_a_banded_sleeve_and_a_hub_round_trip_through_a_workbook(tmp_path):
    path = tmp_path / "RangeBox_Fixed.xlsx"
    xlsx.write_new(str(path), model.to_sheets(range_box_fixed()))
    spec, diagnostics = model.from_book(xlsx.read(str(path)))
    assert diagnostics == []
    assert spec.without_rows() == range_box_fixed().without_rows()
    sleeve = spec.gear("RangeSlv")
    assert (sleeve.start_band, sleeve.end_band) == ("5", "5") and spec.gear("Hub").kind == "hub"


def test_a_workbook_without_the_columns_reads_as_before():
    """Old workbooks: no Start band or End band column, every band blank, and the read says nothing of them."""
    import os
    here = os.path.join(os.path.dirname(__file__), "fixtures", "excel-windows", "Reducer_12to1.xlsx")
    spec, diagnostics = model.from_book(xlsx.read(here))
    assert diagnostics == [] and spec.gears
    assert all(g.start_band == "" == g.end_band for g in spec.gears)
    assert "start_band" not in spec.columns["Gears"] and "end_band" not in spec.columns["Gears"]


# -- bands in the spec ------------------------------------------------------------------------------------------------

def test_the_spec_carries_the_bands_and_leaves_them_out_of_its_dict_while_blank():
    gear = range_box_fixed().gear("RangeSlv")
    values = gear.spec_values(range_box_fixed().box)
    assert (values["start_band"], values["end_band"]) == ("5", "5")
    banded = gear.gear_spec(range_box_fixed().box)
    assert banded.bands_mm() == (5.0, 5.0) and banded.to_dict()["start_band"] == "5"
    plain = range_box().gear("RangeSlv").gear_spec(range_box().box)
    assert plain.bands_mm() is None and "start_band" not in plain.to_dict() and "end_band" not in plain.to_dict()
    assert GearSpec.from_dict(banded.to_dict()) == banded and GearSpec.from_dict(plain.to_dict()) == plain


# -- errors at their cells (§2.4) -------------------------------------------------------------------------------------

def _row_error(spec, cell):
    a = assessed(spec)
    found = [m for m in errors(a) if m.startswith(cell + ":")]
    assert found, errors(a)
    return found[0]


@pytest.mark.parametrize("gid, kind_text", [("Sun", "a spur gear"), ("HighDog", "a dog"), ("Hub", "a hub")])
def test_bands_on_a_row_that_is_not_a_sleeve_are_an_error_at_each_band_cell(gid, kind_text):
    spec = with_gear(range_box_fixed(), gid, start_band="2", end_band="2")
    a = assessed(spec)
    row = spec.gear(gid).row
    for key, word in (("start_band", "Start band"), ("end_band", "End band")):
        assert (f"Gears row {row}: {gid} is {kind_text}, and bands are a sleeve's: clear its {word}."
                in errors(a))
    assert a.lay_out_refusal().startswith("Fix the workbook before building")


@pytest.mark.parametrize("changes, sentence", [
    (dict(start_band="0"), "RangeSlv: Start band must be more than 0 mm (got '0')."),
    (dict(end_band="-2"), "RangeSlv: End band must be more than 0 mm (got '-2')."),
    (dict(end_band=""), "RangeSlv: A sleeve with bands has two, one at each end of its face: give End band too, or "
                        "clear Start band."),
    (dict(start_band="26"), "RangeSlv: Start band of 26 mm takes the whole 26 mm face; a band is shorter than the "
                            "face."),
    (dict(start_band="13", end_band="13"), "RangeSlv: Bands of 13 and 13 mm leave no relief on a 26 mm face: "
                                           "together they must be shorter than the face."),
    (dict(start_band="16", end_band="12"), "RangeSlv: Bands of 16 and 12 mm leave no relief on a 26 mm face: "
                                           "together they must be shorter than the face."),
    (dict(rim="25"), "RangeSlv: A rim of 25 mm does not clear the relief bore between the bands, 25 mm (module × "
                     "(teeth + 3)); make it bigger."),
])
def test_a_band_not_positive_one_band_alone_no_relief_or_a_rim_inside_the_relief_is_an_error(changes, sentence):
    message = _row_error(with_gear(range_box_fixed(), "RangeSlv", **changes), "Gears row 7")
    assert message == f"Gears row 7: {sentence}"


def test_the_errors_name_the_band_and_rim_cells_when_the_workbook_has_the_columns(tmp_path):
    path = tmp_path / "Bad.xlsx"
    xlsx.write_new(str(path), model.to_sheets(with_gear(range_box_fixed(), "RangeSlv", end_band="21", rim="24")))
    spec, read = model.from_book(xlsx.read(str(path)))
    a = assess.assess(spec, read, "C:\\Out\\")
    col = {k: xlsx.make_ref(7, c) for k, c in spec.columns["Gears"].items()}
    assert any(m.startswith(f"Gears!{col['end_band']}: RangeSlv: Bands of 5 and 21 mm") for m in errors(a))


def test_a_typed_rim_just_clear_of_the_relief_is_no_error():
    a = assessed(with_gear(range_box_fixed(), "RangeSlv", rim="25.5"))
    assert errors(a) == [] and a.lay_out_refusal() == ""


# -- the relief in the part's plan (§2.4; W9B-INTERFACES §4) -----------------------------------------------------------

def _sleeve(**changes):
    values = dict(kind="sleeve", teeth_side="internal", module="1.25", teeth="17", face_width="26", bore="")
    values.update(changes)
    return GearSpec(**values)


def test_the_banded_plan_is_the_internal_rings_plus_the_relief():
    plain, banded = _sleeve(), _sleeve(start_band="5", end_band="5")
    kind = kind_for(banded)
    path = "C:\\Out\\Sleeve_m1.25_N17.SLDPRT"
    a = plan_for(plain, kind.derive(plain), "", path)
    b = plan_for(banded, kind.derive(banded), "", path)
    assert b.check() == [] and b.kind == a.kind == "internal spur" and b.recipe == a.recipe
    added_globals = [AddGlobal(v.name, v.expression, v.radian_expression)
                     for v in clutch.relief_globals((5.0, 5.0))]
    relief = clutch.relief_ops(26.0, (5.0, 5.0), 25.0)
    last = max(i for i, op in enumerate(a.ops) if isinstance(op, AddGlobal))
    count = next(i for i, op in enumerate(a.ops) if getattr(op, "dimension", "") == "Count@Teeth")
    expected = a.ops[:last + 1] + tuple(added_globals) + a.ops[last + 1:count + 1] + tuple(relief) + a.ops[count + 1:]
    assert b.ops == expected
    assert [g.name for g in added_globals] == ["Start Band", "End Band", "Relief Diameter"]
    assert isinstance(relief[-1], LoftCut) and relief[-1].name == "Relief"
    assert b.values()["Relief Diameter"] == pytest.approx(25.0)          # m(z + 3), §3's Ø 25.0


def test_the_relief_runs_from_the_start_band_to_the_face_less_the_end_band():
    planes = [op for op in clutch.relief_ops(26.0, (4.0, 6.0), 25.0) if type(op).__name__ == "RefPlane"]
    assert [(p.name, p.plane, p.offset, p.flip) for p in planes] == [
        ("Relief Start Plane", 1, 4.0, helical._flip_for(4.0)), ("Relief End Plane", 1, 20.0, helical._flip_for(20.0))]
    links = {op.dimension: op.expression for op in clutch.relief_ops(26.0, (4.0, 6.0), 25.0)
             if type(op).__name__ == "LinkDimension"}
    assert links == {"Offset@Relief Start Plane": '"Start Band"', "Offset@Relief End Plane": '"Face Width" - "End Band"',
                     "Relief@Relief Start Sketch": '"Relief Diameter"', "Relief@Relief End Sketch": '"Relief Diameter"'}


def test_a_band_changed_is_a_value_change_and_bands_given_or_taken_are_structural():
    five, six = _sleeve(start_band="5", end_band="5"), _sleeve(start_band="6", end_band="5")
    assert swbuild.structural_change(five.to_dict(), six.to_dict()) == ""
    kind = kind_for(six)
    values = {v.name: v.expression for v in kind.variables(six, kind.derive(six))}
    assert values["Start Band"] == "6" and values["End Band"] == "5"
    for built, wanted in ((_sleeve(), five), (five, _sleeve())):
        assert swbuild.structural_change(built.to_dict(), wanted.to_dict()) == (
            "Bands cannot be given to or taken from a built sleeve through its values; build it again as a new part.")


# -- engagement per band, RangeBox_Fixed (§3) -------------------------------------------------------------------------

def test_range_box_fixed_engages_per_band_as_section_3s_table():
    a = assessed(range_box_fixed())
    assert errors(a) == [] and a.lay_out_refusal() == ""
    modes_ = {m.name: m for m in a.report.modes}
    assert {n: m.engaged for n, m in modes_.items()} == {"H": (("RangeSlv", "HighDog"),), "N": (),
                                                         "L": (("RangeSlv", "LowDog"),)}
    assert modes_["H"].ratio == pytest.approx(1.0) and modes_["N"].ratio_why == "neutral"
    assert round(modes_["L"].ratio, 6) == 2.896552
    sleeve = a.spec.gear("RangeSlv")
    spans = {n: modes.band_spans(sleeve, m.placed["RangeSlv"]) for n, m in modes_.items()}
    assert spans == {"H": (("start", -55.5, -50.5), ("end", -34.5, -29.5)),
                     "N": (("start", -48.0, -43.0), ("end", -27.0, -22.0)),
                     "L": (("start", -40.5, -35.5), ("end", -19.5, -14.5))}
    assert a.report.layout.placed["Hub"].z_range == (-55.5, -35.5)


def test_a_band_that_covers_part_of_a_dog_is_an_error_naming_the_band():
    a = assessed(with_gear(range_box_fixed(), "RangeSlv", slides="H=-7.5, N=0, L=+6"))
    assert ("Modes row 4: in L RangeSlv's end band covers 3.5 mm of LowDog's 5 mm face: a sleeve engages a dog only "
            "over its whole face; move the position on or off it." in errors(a))


def test_the_stroke_warning_is_per_band():
    """§3: the 26 mm sleeve slides past two dogs 10 mm apart, but each band is 5 mm: no stroke warning. Its whole-face
    reading (no bands) would hold both at once."""
    fixed = [m for _, m in said(assessed(range_box_fixed())) if "would hold both at once" in m]
    assert fixed == []
    long = with_gear(range_box_fixed(), "RangeSlv", start_band="", end_band="")
    assert any("RangeSlv is 26 mm long and HighDog and LowDog are 10 mm apart" in m for _, m in said(assessed(long)))
    wide = with_gear(range_box_fixed(), "RangeSlv", end_band="11", slides="H=-7.5, N=0, L=+7.5")
    assert any(m.startswith("Gears row 7: RangeSlv's end band is 11 mm long and HighDog and LowDog are 10 mm apart")
               for _, m in said(assessed(wide)))


# -- the hub (K8) -----------------------------------------------------------------------------------------------------

def test_the_hub_is_a_workbook_kind_an_external_spline_ring_named_hub():
    hub = GearSpec(kind="hub", module="1.25", teeth="17", face_width="20", bore="8")
    assert isinstance(gears.WORKBOOK_KINDS["hub"], clutch.HubKind) and kind_for(hub) is gears.WORKBOOK_KINDS["hub"]
    assert spec_mod.default_stem(hub) == "Hub_m1.25_N17"
    dog = replace(hub, kind="dog")
    k = kind_for(hub)
    hub_plan = plan_for(hub, k.derive(hub), "", "C:\\Out\\Hub.SLDPRT")
    dog_plan = plan_for(dog, kind_for(dog).derive(dog), "", "C:\\Out\\Hub.SLDPRT")
    strip = lambda p: [op for op in p.ops if type(op).__name__ != "CustomProperty"]     # noqa: E731
    assert strip(hub_plan) == strip(dog_plan)                    # a dog's ring with the row's Bore
    assert any(type(op).__name__ == "Cut" and op.id == "bore_cut" for op in hub_plan.ops)


def test_the_hub_engages_nothing_and_is_outputs_anchor_with_the_sleeve_splined_to_it():
    a = assessed(range_box_fixed())
    assert all("Hub" not in pair for m in a.report.modes for pair in m.engaged)
    plan = gearbox.plan_gearbox(a, None, exists=lambda p: False, read_sidecar=lambda p: None)
    assert plan.refusal == ""
    assert plan.motion.anchors["Output"] == "Hub"
    mates = {m.name: m for m in plan.motion.mates}
    assert mates["Hub on Output Axis"].kind == "axis" and mates["Hub along Output"].kind == "along"
    assert mates["Hub along Output"].z_front == -55.5
    assert mates["RangeSlv splined to Hub"].kind == "spline" and mates["RangeSlv splined to Hub"].gears == ("Hub",
                                                                                                         "RangeSlv")
    assert mates["RangeSlv along Output"].values == (("H", -55.5), ("N", -48.0), ("L", -40.5))
    assert mates["RangeSlv engages HighDog"].modes == ("H",) and mates["RangeSlv engages LowDog"].modes == ("L",)
    assert not any(name.startswith(("RangeSlv locked", "Hub locked")) for name in mates)


def test_a_hub_no_band_covers_in_a_mode_is_an_error_at_that_modes_cell():
    moved = with_gear(range_box_fixed(), "Hub", at="-48.75", face_width="13.5")       # −55.5…−42: L's band is past it
    assert ("Modes row 4: in L Hub is under no band of RangeSlv: in every mode a band of the sleeve covers its hub "
            "whole, or the hub the band; move Hub, or the bands." in errors(assessed(moved)))
    assert not any(m.startswith(("Modes row 2", "Modes row 3")) and "under no band" in m
                   for m in errors(assessed(moved)))


def test_a_hub_that_a_band_covers_whole_or_that_covers_the_band_is_clean_in_every_mode():
    a = assessed(range_box_fixed())                     # the hub (20) covers the start band (5) in H, N and L
    assert not any("Hub" in m for m in errors(a))
    narrow = with_gear(with_gear(range_box_fixed(), "Hub", at="-44.75", face_width="2"),
                       "RangeSlv", slides="H=-1, N=0, L=+1", start_band="7", end_band="7")
    assert not any("under no band" in m for m in errors(assessed(narrow)))


def test_an_unbanded_sleeve_and_its_hub_must_cover_one_another_in_every_mode():
    """RangeSlv 26 mm long at −35, no bands, sliding ±1 (−49…−23, −48…−22, −47…−21): a hub at −42…−38 is under it in
    every mode; one at −52…−48 is not under it in any."""
    box = with_gear(range_box_fixed(), "RangeSlv", start_band="", end_band="", slides="H=-1, N=0, L=+1")
    hubbed = with_gear(box, "Hub", at="-40", face_width="4")
    assert not any("do not cover one another" in m for m in errors(assessed(hubbed)))
    off = errors(assessed(with_gear(box, "Hub", at="-50", face_width="4")))
    assert ("Modes row 2: in H RangeSlv and Hub do not cover one another: in every mode a sleeve covers its hub "
            "whole, or the hub the sleeve; move Hub." in off)
    assert sum("do not cover one another" in m for m in off) == 3


@pytest.mark.parametrize("change, cell, sentence", [
    (lambda s: with_gear(s, "Hub", slides="A=0, B=1"), "Gears row 8",
     "Hub is a hub, which is fixed to its shaft: a sleeve slides over it, so clear its Slides."),
    (lambda s: with_gear(s, "Hub", shaft="Input", at="-60"), "Gears row 8",
     "Hub is a hub, which carries a sleeve on its own shaft, and no sleeve is on Input."),
    (lambda s: with_gear(s, "Hub", teeth="18"), "Gears row 8",
     "Hub carries RangeSlv on its teeth, so it has RangeSlv's teeth, module and pressure angle (17 teeth, module "
     "1.25)."),
    (lambda s: replace(s, meshes=s.meshes + (model.Mesh("Hub", "Sun", row=4),)), "Meshes row 4",
     "Hub is a hub, which is not listed on Meshes: a hub carries the sleeve on its shaft and meshes nothing."),
])
def test_a_hubs_own_rules_are_errors_at_their_cells(change, cell, sentence):
    assert f"{cell}: {sentence}" in errors(assessed(change(range_box_fixed())))


# -- the record and the sidecar (§2.4; W9B-INTERFACES §5) ---------------------------------------------------------------

def _built():
    from test_swbuild import FakeSolidWorks
    sw = FakeSolidWorks()
    a = assessed(range_box_fixed())
    plan = gearbox.plan_gearbox(a, None, exists=sw.exists, read_sidecar=lambda p: None)
    assert plan.refusal == "", plan.refusal
    result = swbuild.build_gearbox(sw, **plan.build_kwargs(), exists=sw.exists)
    done = gearbox.finish_build(plan, result, None, workbook=BOOK, digest="d1", written_by="test",
                                read_sidecar=lambda p: None, exists=sw.exists)
    return sw, result, done


def test_range_box_fixed_builds_on_the_fake_its_sleeve_with_the_relief():
    sw, result, done = _built()
    assert result.ok, result.failures
    sleeve = next(p for p in done.record.parts if "RangeSlv" in p.gears)
    assert sleeve.spec["start_band"] == "5" and sleeve.spec["end_band"] == "5"
    sidecar = dict(done.sidecars)[next(path for path in dict(done.sidecars) if "Sleeve" in path)]
    assert "Relief" in sidecar.record.features and "Relief Start Plane" in sidecar.record.features
    hub = next(p for p in done.record.parts if "Hub" in p.gears)
    assert hub.path.endswith("Hub_m1.25_N17.SLDPRT") and "start_band" not in hub.spec


def test_a_banded_parts_sidecar_is_schema_2_and_every_other_stays_1():
    _, _, done = _built()
    versions = {path.replace("\\", "/").rsplit("/", 1)[-1]: s.schema_version for path, s in done.sidecars}
    assert versions.pop("Sleeve_m1.25_N17.gear.json") == 2
    assert versions and set(versions.values()) == {1}
    for path, s in done.sidecars:
        text = store.to_json(s)
        assert json.loads(text)["schemaVersion"] == s.schema_version
        assert ("start_band" in text) == (s.schema_version == 2)
        assert store.from_json(text).record == s.record


def test_an_older_app_refuses_a_schema_2_sidecar(monkeypatch):
    _, _, done = _built()
    sleeve = next(s for path, s in done.sidecars if "Sleeve" in path)
    text = store.to_json(sleeve)
    monkeypatch.setattr(store, "SCHEMA_VERSION", 1)
    with pytest.raises(store.UnknownSchema, match=r"schema 2, this one reads 1"):
        store.from_json(text)


def test_the_updated_sidecar_keeps_a_banded_parts_schema_and_an_unbanded_ones():
    _, _, done = _built()
    for path, s in done.sidecars:
        again = store.updated_sidecar(s, s.record.spec, s.record.derived, s.record.variables)
        assert again.schema_version == s.schema_version


def test_the_link_record_is_schema_8_and_carries_the_bands():
    _, _, done = _built()
    raw = json.loads(store.link_record_to_json(done.record))
    assert store.LINK_SCHEMA_VERSION == 8 == store._W9A_LINK_SCHEMA + 1 and raw["link_schema_version"] == 8
    back = store.link_record_from_json(json.dumps(raw))
    assert back == store.link_record_from_json(store.link_record_to_json(done.record))
    assert next(p for p in back.parts if "RangeSlv" in p.gears).spec["start_band"] == "5"


@pytest.mark.parametrize("version", [6, 7])
def test_a_schema_6_or_7_record_reads_as_before(tmp_path, version):
    _, _, done = _built()
    raw = json.loads(store.link_record_to_json(done.record))
    raw["link_schema_version"] = version
    target = tmp_path / "R.workbook.json"
    target.write_text(json.dumps(raw))
    first = store.link_record_from_json(target.read_text())
    assert first.schema_version == 8 and first == store.link_record_from_json(store.link_record_to_json(done.record))


def test_an_older_reader_refuses_schema_8_and_leaves_it_byte_identical(tmp_path, monkeypatch):
    _, _, done = _built()
    done.record.workbook = str(tmp_path / "R.xlsx")
    text = store.link_record_to_json(done.record)
    target = tmp_path / "R.workbook.json"
    target.write_text(text)
    monkeypatch.setattr(store, "LINK_SCHEMA_VERSION", 7)
    with pytest.raises(store.UnknownSchema, match=r"schema 8, this one reads 7"):
        store.read_link_record(str(tmp_path / "R.xlsx"))
    assert target.read_text() == text and sorted(p.name for p in tmp_path.iterdir()) == ["R.workbook.json"]


def test_update_carries_a_band_changed_on_a_built_banded_sleeve_through_its_globals():
    from gear_generator.workbook import update
    _, _, done = _built()
    record = store.link_record_from_json(store.link_record_to_json(done.record))
    up = update.classify(record, assessed(with_gear(range_box_fixed(), "RangeSlv", start_band="6")),
                         exists=lambda p: True)
    assert up.refusal == "" and not up.needs_new_revision and up.structural == ()
    changed = [p for p in up.parts if p.changed]
    assert [p.path.replace("\\", "/").rsplit("/", 1)[-1] for p in changed] == ["Sleeve_m1.25_N17.SLDPRT"]
    assert {v.name: v.expression for v in changed[0].variables if "Band" in v.name} == {"Start Band": "6",
                                                                                         "End Band": "5"}


def test_bands_taken_from_a_built_sleeve_need_build_again_until_w9c():
    from gear_generator.workbook import update
    _, _, done = _built()
    record = store.link_record_from_json(store.link_record_to_json(done.record))
    plain = with_gear(range_box_fixed(), "RangeSlv", start_band="", end_band="")
    up = update.classify(record, assessed(plain), exists=lambda p: True)
    assert up.needs_new_revision and up.structural == (
        "Sleeve_m1.25_N17 (RangeSlv): Bands cannot be given to or taken from a built sleeve through its values; build "
        "it again as a new part.",)
