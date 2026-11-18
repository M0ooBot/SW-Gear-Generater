"""PLAN-PRINTED §2.7: the rule F1 keeps, pinned before F1's first line.

*A gear marked Machined builds exactly what every gear builds today, is told exactly what it is told today, and is
recorded exactly as it is recorded today.* Every value here was taken at f3c4873, the commit the branch `printed` was
cut from (W9d), before any of F1's code, and must hold at every commit of F1 (§2.8). A gear the code builds without
saying its process is machined (§1), so nothing below says one: these are the specs W9 built, and after F1 they are
what a machined gear is.

- every strip plan of every kind and recipe, its steps in both trig variants, its warnings and its file name;
- the three pair assembly plans; Solve's rows for spur, helical, ring, bevel and crossed pairs;
- the W8 fixtures' fingerprints (`test_workbook_planetary._fingerprint`), RangeBox and RangeBox_Fixed with them;
- the whole `.gear.json` of a machined part, its spec and derived both, and its entry in a link record;
- what Update, the strip and Build again… say of a record written before F1: nothing.

The link record's own `link_schema_version` is left out of the record's pin: F1 moves it to 11 for every record by
ruling (§1.2), and its pins are elsewhere. Pins are by sha256, as BEFORE_W7 and BEFORE_W8 are.
"""

import hashlib
import json
from dataclasses import replace
from types import SimpleNamespace

import pytest

from gear_generator import findings, gui, store
from gear_generator.gears import kind_for, pair
from gear_generator.gears.base import GeometryError, describe
from gear_generator.gears.equations import DEGREES, RADIANS
from gear_generator.spec import GearSpec, PairSpec
from gear_generator.workbook import assess, gearbox, motion, update

STAMP = "2026-11-18T00:00:00Z"
TEMPLATE = "C:\\T\\Part.prtdot"
OUT = "C:\\Out\\"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


# -- the gears, one of each kind the strip and a workbook build ------------------------------------------------------

GEARS = {
    "spur": dict(),
    "spur_m1_z12": dict(module="1", teeth="12"),                               # undercut and thin-tip territory
    "spur_m0.5_z30": dict(module="0.5", teeth="30", bore="2"),
    "spur_m3_z40": dict(module="3", teeth="40", bore="20"),
    "spur_shifted": dict(module="2", teeth="15", profile_shift="0.3"),
    "spur_typed": dict(backlash="0.1", fillet="0.4", bore=""),
    "spur_named": dict(name="MyGear", teeth="31"),
    "helical": dict(kind="helical", helix_angle="20"),
    "helical_shifted": dict(kind="helical", helix_angle="15", hand="left", teeth="15", profile_shift="0.2"),
    "herringbone": dict(kind="herringbone", helix_angle="30", module="2", teeth="20"),
    "herringbone_grooved": dict(kind="herringbone", helix_angle="30", module="2", teeth="20", groove="4"),
    "ring": dict(teeth_side="internal", teeth="60", bore=""),
    "ring_rim": dict(teeth_side="internal", teeth="55", module="1.25", rim="90", bore=""),
    "ring_helical": dict(kind="helical", teeth_side="internal", teeth="60", helix_angle="15", bore=""),
    "ring_herringbone": dict(kind="herringbone", teeth_side="internal", teeth="60", helix_angle="25", bore=""),
    "bevel": dict(kind="bevel", teeth="20", mate_teeth="40"),
    "bevel_s80": dict(kind="bevel", teeth="20", mate_teeth="30", shaft_angle="80", module="2"),
    "bevel_crown": dict(kind="bevel", teeth="40", mate_teeth="20", shaft_angle="120", bore="8"),
    "bevel_internal": dict(kind="bevel", teeth="40", mate_teeth="16", shaft_angle="120", bore=""),
    "sleeve": dict(kind="sleeve", teeth_side="internal", module="1.25", teeth="17", face_width="26", bore=""),
    "sleeve_banded": dict(kind="sleeve", teeth_side="internal", module="1.25", teeth="17", face_width="26", bore="",
                          start_band="6", end_band="6"),
    "dog": dict(kind="dog", module="1.25", teeth="17", face_width="8", bore="8"),
    "hub": dict(kind="hub", module="1.25", teeth="17", face_width="20", bore="8"),
}


def _spec(name: str, **marked: str) -> GearSpec:
    return GearSpec(**{**GEARS[name], **marked})


# F1-0's interface commit: the same gears said machined in so many words, as the form's row and a workbook's Box
# write them (§1.3), and with a nozzle typed, which a machined gear does not read. Each must be the pin.
MACHINED = (dict(process="machined"), dict(process="Machined"), dict(process=" MACHINED ", nozzle="0.6"),
            dict(process=""))


def strip_print(name: str, **marked: str) -> str:
    """Everything the strip makes and says of one gear: its file name, warnings, globals in both trig variants and
    every step of each recipe's plan, described in both."""
    spec = _spec(name, **marked)
    kind = kind_for(spec)
    derived = kind.derive(spec)
    out = [spec.default_stem(), spec.stem(), repr(kind.recipe_for(spec))]
    out.append(repr([(d.level, d.message, d.field) for d in kind.validate(spec, derived)]))
    for trig in (DEGREES, RADIANS):
        out.append(repr([(v.name, v.expression_for(trig)) for v in kind.variables(spec, derived)]))
    for recipe in sorted(kind.recipes):
        try:
            plan = kind.plan(spec, derived, recipe, TEMPLATE, OUT + spec.stem() + ".SLDPRT")
        except GeometryError as exc:        # a recipe that cannot draw this gear is pinned as its sentence
            out.append(f"{recipe}: {exc}")
            continue
        out.append(repr(plan))
        for trig in (DEGREES, RADIANS):
            out.append("\n".join(describe(op, trig) for op in plan.ops))
    return _sha("\n".join(out))


STRIP = {
    "bevel": "11cb1d53527c2f3d4d83eb9084143818bd7181df5b9929c5b47244440ff4c7fd",
    "bevel_crown": "011ecb96029d836d9f146b1e652a19ac745fd06ff43ed5ed11b033dd0d19bf0a",
    "bevel_internal": "b96c95c2414f4e3a79098495ddc78dc7b096fac6a01386be12b41dc99ac2d903",
    "bevel_s80": "cc7c79e394ea3ef2aea918fe33c1ba934a5cbf73e5c213414337cca70fa0d460",
    "dog": "c2ba802d645d25b9ab5087f64211f8eb36ea3d813c96e0324ef88931f938ed6d",
    "helical": "8458036f12ee8612b8ad56897a0d251059aa8780bf215edc55332a04b5a3ff66",
    "helical_shifted": "b18caa91ac55ec4d8cb8b2a3cd2a00aafbdd8a59c10be970480e0d95871eacd4",
    "herringbone": "a29baff4fd21b07e8667367f6dd19f69e8a400ab593cb5218b201b9b60080f11",
    "herringbone_grooved": "2ab3cd8ec5370a114a8913d7c1380d3d43e7cea76509933346d64f4e497a266b",
    "hub": "c5ca3099745c80251bd3e018227dd96ed54e62fd4287f878a3ae091791fc025d",
    "ring": "38fe55191c4d9abeadf4b154773b1ddd473e8f7b31b26ec29d72670d96250ee2",
    "ring_helical": "8772c732dc7d0a4ee518d5db934c8a56f0e7641ed5a1292f7cbe47c007bc72d0",
    "ring_herringbone": "646c399b61f7f32f2e068fce6815e469457d785f76ade0b465657436ee276728",
    "ring_rim": "56d6f7ea67c4fc75b1e9517dd4869393122b91ff25ef326000b01ebd68cf1e7e",
    "sleeve": "3651a132729c86d788f43cbedb3b9892d5c786f6c024f16681f370983f86ac94",
    "sleeve_banded": "41498da9a834e6411106da984ccaa190ec358fe742bedd234d6ae3c0509380b8",
    "spur": "9c15ec70f318d7e10d04b278dbde8b0d3f51dadb2e9da8b29685f4a1a674a8ee",
    "spur_m0.5_z30": "d2880bf1a93ae9288b3e91b7848db92de5b1ccc96f4ae5ec6114ff7e12276fc5",
    "spur_m1_z12": "0e6e9bc1381b7a5250b0fce9d75bca9b823d4567812b0b3f60ddd30530720277",
    "spur_m3_z40": "3a0212379e0c193505360c0b4bd4db2cb56883165686e7ff46dbbadaf5a00596",
    "spur_named": "f4071c9a1d590cd08e5b47328a6e206df6f6120fc1edb729ed1fbaee8a1eb8d5",
    "spur_shifted": "ccb0f58946384057ebc0bedbde959f8df11295ca5a8c8ae659e88393832a0708",
    "spur_typed": "0745b35f07eaeff8c2ff0b9e6bb337cc24e5e064068575483807d7feca7e3261",
}


@pytest.mark.parametrize("name", sorted(GEARS))
def test_every_kind_and_recipe_plans_says_and_names_as_at_the_cut(name):
    assert strip_print(name) == STRIP[name]


@pytest.mark.parametrize("marked", MACHINED, ids=repr)
@pytest.mark.parametrize("name", sorted(GEARS))
def test_a_gear_marked_machined_plans_says_and_names_as_at_the_cut(name, marked):
    assert strip_print(name, **marked) == STRIP[name]


# -- the three pair assembly plans -------------------------------------------------------------------------------

def assembly_prints():
    a, b = GearSpec(teeth="20"), GearSpec(teeth="40")
    ring_a, ring_b = GearSpec(teeth="20", bore="8"), GearSpec(teeth="60", teeth_side="internal", bore="")
    ha, hb = GearSpec(kind="helical", helix_angle="45", teeth="20"), GearSpec(kind="helical", helix_angle="45",
                                                                              teeth="30")
    ba, bb = GearSpec(kind="bevel", teeth="20", mate_teeth="40"), GearSpec(kind="bevel", teeth="40", mate_teeth="20")
    paths = ("C:\\Out\\A.SLDPRT", "C:\\Out\\B.SLDPRT", TEMPLATE, "C:\\Out\\Pair.SLDASM")
    plans = {
        "parallel_fixed": pair.assembly_plan(a, b, *paths),
        "parallel_gear_mate": pair.assembly_plan(a, b, *paths, motion="gear mate"),
        "ring": pair.assembly_plan(ring_a, ring_b, *paths),
        "crossed_mates": pair.crossed_assembly_plan(ha, hb, *paths, 90.0, route=pair.ROUTE_MATES),
        "crossed_fixed": pair.crossed_assembly_plan(ha, hb, *paths, 90.0, route=pair.ROUTE_FIXED),
        "bevel": pair.bevel_assembly_plan(ba, bb, *paths),
    }
    return {k: _sha(repr(p) + "\n" + "\n".join(describe(op, t) for t in (DEGREES, RADIANS) for op in p.ops))
            for k, p in plans.items()}


ASSEMBLIES = {
    "bevel": "a105d876794b6060f12a1e5bd9975663dfab422918d6dcdd2789783ce05a5a8b",
    "crossed_fixed": "bfb11d36e777cf6ba415578e500df9ee5c28d5f5d432ba1c778827260c1862ab",
    "crossed_mates": "a9d1213e40d7ef45dea40074f947ee992eb8c320a347f5a19e379d533b309926",
    "parallel_fixed": "7846e0baf276eb78ca45196d3e1ec2d19734eb314298444043de75932242010a",
    "parallel_gear_mate": "a46cdef5e628899140d69e918d91774bd35bc1019d50181cf54a303ed9a33ebe",
    "ring": "297a510196eba42eef93f0df8aeb8def08e4e863a04b0e85546ed9d93ae67a43",
}


def test_the_three_pair_assembly_plans_are_as_at_the_cut():
    assert assembly_prints() == ASSEMBLIES


# -- Solve's rows ------------------------------------------------------------------------------------------------

SOLVES = {
    "spur": PairSpec(mode="pair", centre_distance="60", ratio="3"),
    "spur_near": PairSpec(mode="pair", centre_distance="61.3", ratio="2.5", min_teeth="12"),
    "spur_module": PairSpec(mode="pair", centre_distance="45", ratio="2", module="1"),
    "helical": PairSpec(mode="pair", centre_distance="60", ratio="3", gear_a=GearSpec(kind="helical"),
                        gear_b=GearSpec(kind="helical")),
    "herringbone": PairSpec(mode="pair", centre_distance="80", ratio="2", gear_a=GearSpec(kind="herringbone"),
                            gear_b=GearSpec(kind="herringbone")),
    "ring": PairSpec(mode="pair", centre_distance="30", ratio="4", mesh="internal",
                     gear_b=GearSpec(teeth_side="internal")),
    "bevel": PairSpec(mode="pair", cone_distance="50", ratio="2", gear_a=GearSpec(kind="bevel"),
                      gear_b=GearSpec(kind="bevel")),
    "crossed": PairSpec(mode="pair", centre_distance="40", ratio="2", shafts="crossed",
                        gear_a=GearSpec(kind="helical"), gear_b=GearSpec(kind="helical")),
}


def solve_print(name: str) -> str:
    rows = pair.solve_spec(SOLVES[name])
    out = [repr(rows)]
    pairs = SOLVES[name]
    for row in rows[:3]:                    # each row applied to the form, and what the pair is told
        a, b = pair.apply(row, pairs.gear_a, pairs.gear_b)
        try:
            g1, g2 = kind_for(a).derive(a), kind_for(b).derive(b)
        except Exception as exc:            # noqa: BLE001 -- a row that does not derive is pinned as its sentence
            out.append(f"{type(exc).__name__}: {exc}")
            continue
        out.append(repr((a.to_dict(), b.to_dict(), pair.mesh_warnings(g1, g2))))
    return _sha("\n".join(out))


SOLVE = {
    "bevel": "ea91fcaf7216df31db7edaeff8575fa21d4fb551ed835e8bde4dcbd226830ae0",
    "crossed": "62813d8cfbf118d30024d4263aeda5dbd016dc175d16699a720c0aad2d21c273",
    "helical": "36a647d7f42b9e2b8ab812d9ae5eff364af067d56c2da8790e2fcdd80065ac5a",
    "herringbone": "16201c5e839c5b1d15dcbcd530d6012073d8bc53be8d46c669ac60fa9ca1cdad",
    "ring": "31c961bb9caf3ebf965378db588fdb58f7753a2324e8cecc6fef7683356e05f2",
    "spur": "69c7843a5a80840deff78a3bd109b14bad1d780f171b506015ebe6006238bcba",
    "spur_module": "d0e9cd2f4cf8eb456f0a2308791547832c97bf7e3f34fb95910cd767e2398c3f",
    "spur_near": "513c33239056da0c42959001a43f8a711203d960b37679f85d9378e3f38a03a5",
}


@pytest.mark.parametrize("name", sorted(SOLVES))
def test_solves_rows_and_what_their_pair_is_told_are_as_at_the_cut(name):
    assert solve_print(name) == SOLVE[name]


# -- the W8 fixtures, RangeBox and RangeBox_Fixed ------------------------------------------------------------------

def fixture_prints():
    from test_workbook_planetary import _fingerprint
    from workbook_fixtures import e4_transfer_case, range_box, range_box_fixed, transfer_case_parallel
    makes = {"transfer_case_parallel": transfer_case_parallel, "e4_transfer_case": e4_transfer_case,
             "range_box": range_box, "range_box_fixed": range_box_fixed}
    return {name: _fingerprint(assess.assess(replace(make(), source_path="C:\\B\\W.xlsx"), [], OUT))
            for name, make in makes.items()}


FIXTURES = {
    "e4_transfer_case": "9fb7a6c1c19cb57c2c3162959b9b92497f852d3639b04dc0a7642c7ef772e1b6",
    "range_box": "b1d010f97e062dcbc8c8fd59c8a217e3e07ea40e828ab654f406868dacd2071a",
    "range_box_fixed": "c97cbfffc9c7e639b3b00e908fdb2019764b0196625396640f27db9a7945d82f",
    "transfer_case_parallel": "8fef58f5f5339e6fb004bb2813905a00871a47444f329eb23023163c04e0b027",
}


def test_the_w8_fixtures_and_rangebox_plan_bit_for_bit_as_at_the_cut(monkeypatch):
    monkeypatch.setattr(findings, "TURNED_GEAR_MATE_SENSE_READ_BACK", "entity senses", raising=False)
    assert fixture_prints() == FIXTURES


# -- the record: a machined part's whole .gear.json, and its entry in a link record --------------------------------

RECORDED = ("spur", "spur_shifted", "helical", "herringbone_grooved", "ring", "ring_helical", "bevel", "bevel_crown",
            "sleeve", "sleeve_banded", "hub")


def sidecar_text(name: str, **marked: str) -> str:
    """The .gear.json the strip writes for this gear (`gui.GearApp._write_sidecar`'s call), with a fixed id and stamp."""
    spec = _spec(name, **marked)
    kind = kind_for(spec)
    derived = kind.derive(spec)
    plan = kind.plan(spec, derived, kind.recipe_for(spec), TEMPLATE, OUT + spec.stem() + ".SLDPRT")
    path = plan.path or OUT + spec.stem() + ".SLDPRT"
    previous = store.Sidecar(part_path=path, record=store.GearRecord(record_id="gear-0000f1f1", created=STAMP))
    sidecar = store.built_sidecar(
        path, spec.stem() + ".SLDPRT", kind=spec.kind, recipe=plan.recipe, spec=spec.to_dict(),
        derived=derived.to_dict(), variables=[[v.name, v.expression_for(DEGREES)] for v in kind.variables(spec, derived)],
        features=["Gear"], dimensions=[], manual_steps=[], template=TEMPLATE, trig=DEGREES,
        written_by="gear-generator test", previous=previous, stamp=STAMP)
    return store.to_json(sidecar)


def entry_text(name: str, **marked: str) -> str:
    """The part's entry in a link record, as `link_record_to_json` writes it."""
    spec = _spec(name, **marked)
    kind = kind_for(spec)
    derived = kind.derive(spec)
    entry = store.PartEntry(path=OUT + spec.stem() + ".SLDPRT", gears=["G1"], revision=0, kind=spec.kind,
                            spec=spec.to_dict(), trig=DEGREES,
                            variables=[[v.name, v.expression_for(DEGREES)] for v in kind.variables(spec, derived)])
    raw = json.loads(store.link_record_to_json(store.LinkRecord(workbook="C:\\B\\W.xlsx", parts=[entry])))
    return json.dumps(raw["parts"][0], indent=2, sort_keys=True, ensure_ascii=False)


SIDECARS = {
    "bevel": "8ccb02fc9fc94142350e13ca8e2a7e4c4d6baaae9405fdcaa9ade3441742554f",
    "bevel_crown": "20f1699a71df250674e1d536e14ddf85d2d925ffb7564ec3c0c38ec489048bb8",
    "helical": "c658a3dd6730d8cd84fbfc67c123880ea0ce2d2c19b3cc1a5cfdd9ec4e1379e0",
    "herringbone_grooved": "d553001d4046499e47b72dcb24ab741b40a074ef54b3cfd61f9b4d59b49b34ac",
    "hub": "7b90e15ecc47ef5e4a93ec744b1678566400c5ae27e86baa463362ee1e1fa846",
    "ring": "bf8e36c5b3e2acb3505df40227b95a229800c9e3af9fca778041410a6d0f1f3d",
    "ring_helical": "beef40b5c4c590890ca8360df3c88acb74adef5e3c77994a73371b27db1360e2",
    "sleeve": "6051bc4f9ff771f27dbbdadba9e8813a7389cdfe4f82e3902fe57f527b992b66",
    "sleeve_banded": "9633805e9fefafb7ca88a30a5926fb85e0ad829d0da9fd9e9c250fc6a4fc7ffa",
    "spur": "548d8e41b2b124e4a0434fb8c0d390b7692877dddecbd29f052bbc2eaacbd341",
    "spur_shifted": "88a9923c62e8fa414c35039f2b2568140b7476e64e84e816647ab0c45b908d06",
}

ENTRIES = {
    "bevel": "926e716bc3e56a42244e93f33d305ce961b15767f7dd23b9b71423249d91edf8",
    "bevel_crown": "8acf3b2157aa4dacfd17205f5896e6c66a76f26e31f3d43877aa3c490e65ee77",
    "helical": "0d609801f853893547e0637c38c0014f98c3a302589ce705fd4c362e47709225",
    "herringbone_grooved": "9adf4dafc6458932bcacdf75332b9907d9a9d9701c2ba747b9aa5fd51cea0ab1",
    "hub": "7bf72979a0668f2427f88686097b980f8aa08faa953c775c735bc088a9ed1f75",
    "ring": "eea6014af803541cc4ac933a280b5a08e1c0ebab97cc4e59505d00ca8a534ac4",
    "ring_helical": "6c6fa94c85b947162973ccfa51b48f5467f6a9750df0fbf20a19abba97d20a55",
    "sleeve": "40daedd5bd241cd65737af53a03de512cc55380be601baaef9f47e7c64a798f2",
    "sleeve_banded": "86bc69492df871f5a3f149fa7a2d51c81dd0fcd43f95a1969176738750e91ac2",
    "spur": "f1b7d49d58e267ff826d794d9cce045d8e86cadd99efcd2497ca615867a87516",
    "spur_shifted": "40f3503bcf6832695c859c4eefe70e4b127bc055200cb2fd39679f4c83e2bfd2",
}


@pytest.mark.parametrize("name", RECORDED)
def test_a_machined_parts_gear_json_and_record_entry_are_byte_for_byte_as_at_the_cut(name):
    text = sidecar_text(name)
    assert _sha(text) == SIDECARS[name]
    assert json.loads(text)["schemaVersion"] == (2 if name == "sleeve_banded" else 1)
    assert _sha(entry_text(name)) == ENTRIES[name]


@pytest.mark.parametrize("marked", MACHINED, ids=repr)
@pytest.mark.parametrize("name", RECORDED)
def test_a_part_marked_machined_is_recorded_byte_for_byte_as_at_the_cut(name, marked):
    assert _sha(sidecar_text(name, **marked)) == SIDECARS[name]
    assert _sha(entry_text(name, **marked)) == ENTRIES[name]


# -- a record written before F1: Update, the strip and Build again… find nothing to do ----------------------------

def _gearbox_findings(monkeypatch):
    """The findings the W4 gearbox tests pin (test_workbook_gearbox), and its static assembly."""
    import test_workbook_gearbox as w4
    for name, value in {**w4.TIER_7, **w4.SETTLED}.items():
        monkeypatch.setattr(findings, name, value, raising=name in w4.SETTLED)
    monkeypatch.setattr(motion, "motion_reason", lambda: w4.STATIC_FOR_W4)
    monkeypatch.setattr(store, "new_record_id", lambda: "gear-0000f1f1")


def built_reducer():
    """The 12 : 1 reducer built once on the fake disk, as W4's tests build it: (disk, record, record's text)."""
    from test_workbook_gearbox import Disk, assessed, build
    from test_workbook_model import reducer
    disk = Disk()
    _, _, record = build(assessed(reducer()), None, disk)
    raw = json.loads(store.link_record_to_json(record))
    raw.pop(store.LINK_SCHEMA_KEY)
    return disk, record, json.dumps(raw, indent=2, sort_keys=True, ensure_ascii=False)


RECORD_BEFORE_F1 = "5abe227ca98f6a810ff1bf80dd5fe819eb4ad066647c1a102e7f89af2b8576e6"


def nothing_to_do(record, disk, a):
    """What Update, Build again… and W9d's carry say of `record` against the assessment `a`: (Update's plan, its
    fingerprint, the parts Build again… makes, the parts it reuses, the columns that changed for each part)."""
    plan = update.classify(record, a, exists=disk.exists)
    again = gearbox.plan_gearbox(a, record, exists=disk.exists, read_sidecar=disk.read_sidecar)
    jobs = {j.gear_ids[0]: j for j in gearbox.plan_gearbox(a, None, exists=lambda p: False,
                                                           read_sidecar=lambda p: None).build}
    columns = [update._changed_columns(p.spec, jobs[p.gears[0]].spec.to_dict()) for p in record.current_parts()]
    matches = [gearbox._matches(p.spec, p.variables, p.trig, jobs[p.gears[0]]) for p in record.current_parts()]
    return plan, again, columns, matches


def test_a_record_written_before_f1_is_nothing_to_update_or_make_again(monkeypatch):
    from test_workbook_gearbox import assessed
    from test_workbook_model import reducer
    _gearbox_findings(monkeypatch)
    disk, record, text = built_reducer()
    assert _sha(text) == RECORD_BEFORE_F1
    assert all("process" not in p.spec and "nozzle" not in p.spec for p in record.parts)
    plan, again, columns, matches = nothing_to_do(record, disk, assessed(reducer()))
    assert (plan.refusal, plan.structural, plan.missing, plan.replaced, plan.moved_shafts) == ("", (), (), (), ())
    assert [p.changed for p in plan.parts] == [False] * 4 and plan.record_matches
    assert again.refusal == "" and list(again.build) == [] and len(again.reuse) == 4
    assert columns == [[]] * 4 and matches == [True] * 4


def strip_form(sidecar, spec):
    """What `gui.GearApp._update_target` reads of the strip: the record opened, its part active, the form's gear."""
    return SimpleNamespace(_loaded=sidecar, _snapshot={"path": sidecar.part_path, "title": "Gear_m1.5_N25"},
                           mode=SimpleNamespace(get=lambda: gui.MODE_SINGLE),
                           _derived={"a": kind_for(spec).derive(spec)}, _gear_spec=lambda which: spec)


@pytest.mark.parametrize("name", RECORDED)
def test_a_strip_record_written_before_f1_has_nothing_for_update_values(name):
    sidecar = store.from_json(sidecar_text(name))
    assert "process" not in sidecar.record.spec
    form = GearSpec.from_dict(sidecar.record.spec)
    assert gui.GearApp._update_target(strip_form(sidecar, form))[0] == 0


@pytest.mark.parametrize("box_process", ["", "machined", "Machined"])
def test_a_record_written_before_f1_is_nothing_to_do_against_a_workbook_marked_machined_or_left_blank(
        monkeypatch, box_process):
    """D11 ruled (B): against a Box whose Process is blank, a gearbox built before F1 is Machined, as built, and
    nothing changes; against one marked Machined, nothing changes either (§2.7). F1-0's interface commit."""
    from test_workbook_gearbox import FOLDER, WORKBOOK
    from test_workbook_model import reducer
    _gearbox_findings(monkeypatch)
    disk, record, text = built_reducer()
    assert _sha(text) == RECORD_BEFORE_F1 and assess.blank_process(record) == "machined"
    read = replace(reducer(), box=replace(reducer().box, process=box_process), source_path=WORKBOOK)
    a = assess.assess(read, [], FOLDER, blank_process=assess.blank_process(record))
    assert a.lay_out_refusal() == "" and a.read.box.process == a.spec.box.process == (box_process or "machined")
    plan, again, columns, matches = nothing_to_do(record, disk, a)
    assert (plan.refusal, plan.structural, plan.missing, plan.replaced, plan.moved_shafts) == ("", (), (), (), ())
    assert [p.changed for p in plan.parts] == [False] * 4 and plan.record_matches
    assert again.refusal == "" and list(again.build) == [] and len(again.reuse) == 4
    assert columns == [[]] * 4 and matches == [True] * 4


@pytest.mark.parametrize("marked", MACHINED, ids=repr)
@pytest.mark.parametrize("name", RECORDED)
def test_a_strip_record_written_before_f1_against_a_form_marked_machined_has_nothing_for_update_values(name, marked):
    sidecar = store.from_json(sidecar_text(name))
    form = replace(GearSpec.from_dict(sidecar.record.spec), **marked)
    assert gui.GearApp._update_target(strip_form(sidecar, form))[0] == 0


# -- F1-0's interface (PLAN-PRINTED §2.8 items 1 to 7; docs/notes-printed/F1-INTERFACES.md), held so that packages A,
# -- B and C build on it. Each package tests its own work in its own files; these hold only what F1-0 lands.

def test_the_spec_says_its_process_and_leaves_both_keys_out_unless_printed():
    from gear_generator import spec as spec_module
    from gear_generator.spec import InputError
    assert (spec_module.PROCESS_PRINTED, spec_module.PROCESS_MACHINED, spec_module.NOZZLE_DEFAULT) == (
        "printed", "machined", 0.4)
    assert (GearSpec().process, GearSpec().nozzle) == ("machined", "")
    for word in ("", "machined", "Machined", "wood", "  "):
        values = GearSpec(process=word, nozzle="0.6").to_dict()          # never raises, whatever the word
        assert "process" not in values and "nozzle" not in values
    assert GearSpec(process="Printed").to_dict()["process"] == "Printed"
    assert GearSpec(process="printed").to_dict()["nozzle"] == ""
    assert [GearSpec(process=w).is_printed() for w in ("printed", " PRINTED ", "machined", "", "wood")] == [
        True, True, False, False, False]
    assert [GearSpec(process=w).process_value() for w in ("Printed", "machined", "")] == [
        "printed", "machined", "machined"]
    with pytest.raises(InputError, match=r"Process must be printed or machined \(got 'wood'\)\."):
        GearSpec(process="wood").process_value()
    assert GearSpec().nozzle_mm() == 0.4 and GearSpec(nozzle="0.6").nozzle_mm() == 0.6
    for bad, said in (("x", r"Nozzle must be a number"), ("0", r"Nozzle must be more than zero")):
        with pytest.raises(InputError, match=said):
            GearSpec(nozzle=bad).nozzle_mm()
    assert GearSpec(process="printed").default_stem() == "Gear_m1.5_N25_P"
    assert GearSpec(process="printed", teeth="15", profile_shift="0.09").default_stem() == "Gear_m1.5_N15_x0.09_P"
    assert GearSpec(process="printed", name="Mine").stem() == "Mine"
    assert GearSpec.from_dict(GearSpec(process="printed", nozzle="0.6").to_dict()) == GearSpec(
        process="printed", nozzle="0.6")


def test_the_record_is_at_link_schema_11_and_a_printed_part_at_sidecar_schema_3():
    assert (store.LINK_SCHEMA_VERSION, store._W9D_LINK_SCHEMA) == (11, 10)
    assert (store.SCHEMA_VERSION, store.PRINTED_SCHEMA, store.BANDED_SCHEMA, store.PLAIN_SCHEMA) == (3, 3, 2, 1)
    assert store.sidecar_schema(GearSpec(process="printed").to_dict()) == 3
    assert store.sidecar_schema(GearSpec(process="Printed", start_band="2", end_band="2").to_dict()) == 3
    assert store.sidecar_schema(GearSpec(process="machined").to_dict()) == 1
    assert store.sidecar_schema(GearSpec(start_band="2", end_band="2").to_dict()) == 2


# Each of the five variable writers, and a sleeve, dog and hub through the spur and ring kinds they are built from.
WRITERS = ("spur", "helical", "ring", "ring_helical", "bevel", "bevel_crown", "bevel_internal", "sleeve_banded", "dog",
           "hub", "herringbone_grooved", "ring_herringbone")
IIF = 'IIF ( "Module" <= 1 , 0.3 * "Module" , 0.3 )'


@pytest.mark.parametrize("name", WRITERS)
def test_a_printed_gear_with_a_blank_backlash_writes_the_printed_default_and_carries_its_nozzle(name):
    from gear_generator.gears import spur
    assert spur.printed_backlash_expression() == spur.printed_backlash_expression("Module") == IIF
    spec = _spec(name, process="printed", nozzle="0.6")
    kind = kind_for(spec)
    g = kind.derive(spec)
    backlash = [v for v in kind.variables(spec, g) if v.name == "Backlash"]
    assert [(v.expression, v.radian_expression or v.expression) for v in backlash] == [(IIF, IIF)]
    assert g.printed and g.backlash_printed and g.nozzle == 0.6
    data = g.to_dict()
    assert (data["section"] if "section" in data else data)["nozzle"] == 0.6
    typed = _spec(name, process="printed", backlash="0.2")
    held = kind.derive(typed)
    assert held.printed and not held.backlash_printed and held.nozzle == 0.4
    assert [v.expression for v in kind.variables(typed, held) if v.name == "Backlash"] == ["0.2"]
    machined = kind.derive(_spec(name))
    assert not machined.printed and not machined.backlash_printed and machined.nozzle is None
    assert "nozzle" not in json.dumps(machined.to_dict())


@pytest.mark.parametrize("module, backlash", [("0.5", 0.15), ("1", 0.3), ("1.5", 0.3), ("3", 0.3)])
def test_the_printed_default_is_the_smaller_of_0_3_mm_and_0_3_module(module, backlash):
    from gear_generator.gears import spur
    printed = kind_for(GearSpec()).derive(GearSpec(module=module, process="printed"))
    machined = kind_for(GearSpec()).derive(GearSpec(module=module))
    assert printed.backlash == pytest.approx(backlash) and printed.backlash <= machined.backlash + 1e-12
    assert spur.printed_backlash(float(module)) == pytest.approx(backlash)
    assert (spur.PRINTED_BACKLASH, spur.PRINTED_BACKLASH_UP_TO_MODULE) == (0.3, 1.0)


def test_a_printed_specs_unreadable_nozzle_or_process_word_is_an_error_at_its_field():
    kind = kind_for(GearSpec())
    said = [(d.message, d.field) for d in kind.validate(GearSpec(process="printed", nozzle="x"))]
    assert said == [("Nozzle must be a number (got 'x').", "nozzle")]
    said = [(d.message, d.field) for d in kind.validate(GearSpec(process="wood"))]
    assert said == [("Process must be printed or machined (got 'wood').", "process")]
    assert kind.validate(GearSpec(nozzle="x")) == kind.validate(GearSpec())         # a machined gear's is not read


def test_the_pair_stubs_answer_as_the_machined_maths_until_package_a_fills_them():
    assert pair.ring_tip_clearance(1.5, 20, 60) == pair.tip_clearance(1.5, 20, 60)
    assert pair.printed_tip_thickness(1, 20, 20.0, 0.0, 0.0, 0.4) == pair.tip_thickness(1, 20, 20.0, 0.0, 0.0)
    assert pair.solve(60, 3, process="printed", nozzle=0.6) == pair.solve(60, 3)
    assert pair.shift_for_centre(2, 15, 30, 46, printed=True) == pair.shift_for_centre(2, 15, 30, 46)


def test_the_box_says_process_and_nozzle_and_a_gearbox_built_in_code_is_written_machined():
    from gear_generator.workbook import model, schema
    from test_workbook_model import reducer
    settings = {s.key: s for s in schema.BOX_SETTINGS}
    keys = [s.key for s in schema.BOX_SETTINGS]
    assert keys.index("process") == keys.index("efficiency") + 1 and keys.index("units") == keys.index("nozzle") + 1
    assert settings["process"].words == ("printed", "machined") and not settings["process"].numeric
    assert settings["process"].note == ("Printed or Machined; blank: Printed for a new gearbox, as built for one "
                                        "already built")
    assert (settings["nozzle"].title, settings["nozzle"].numeric, settings["nozzle"].default) == (
        "Nozzle (mm)", True, "0.4")
    assert (model.Box().process, model.Box().nozzle) == ("machined", "")
    box = {row[0]: row[1] for row in model.to_sheets(reducer())[0].rows[1:]}
    assert (box["Process"], box["Nozzle (mm)"]) == ("machined", "")
    printed = replace(reducer(), box=replace(reducer().box, process="printed", nozzle="0.6"))
    box = {row[0]: row[1] for row in model.to_sheets(printed)[0].rows[1:]}
    assert box["Process"] == "printed" and float(box["Nozzle (mm)"]) == 0.6
    gear = reducer().gears[0]
    assert gear.gear_spec(printed.box).process == "printed" and gear.gear_spec(printed.box).nozzle == "0.6"
    assert gear.gear_spec(reducer().box).to_dict() == gear.gear_spec(model.Box()).to_dict()


def _entry(**spec):
    return store.PartEntry(path="C:\\P\\G.SLDPRT", gears=["G1"], spec=GearSpec(**spec).to_dict())


@pytest.mark.parametrize("record, word", [
    (None, "printed"),
    (store.LinkRecord(workbook="W.xlsx"), "printed"),
    (store.LinkRecord(workbook="W.xlsx", parts=[_entry()]), "machined"),
    (store.LinkRecord(workbook="W.xlsx", parts=[store.PartEntry(path="C:\\P\\G.SLDPRT", gears=["G1"])]), "machined"),
    (store.LinkRecord(workbook="W.xlsx", parts=[_entry(), _entry(process="printed")]), "printed"),
    (store.LinkRecord(workbook="W.xlsx", parts=[_entry(process="Printed")]), "printed"),
], ids=["no record", "no parts", "machined", "v1 part", "one printed", "Printed"])
def test_a_blank_process_is_as_built(record, word):
    """D11 (B): machined when every current part was built machined, printed otherwise; the same after a record is
    written forward to 11, since the rule reads the parts and never the schema number."""
    assert assess.blank_process(record) == word
    if record is not None:
        again = store.link_record_from_json(store.link_record_to_json(record))
        assert again.schema_version == 11 and assess.blank_process(again) == word


def test_assess_resolves_a_blank_process_in_the_read_and_the_spec_and_leaves_a_word_alone():
    from test_workbook_model import reducer
    blank = replace(reducer(), box=replace(reducer().box, process=""), source_path="C:\\B\\W.xlsx")
    for given, want in (({}, "printed"), (dict(blank_process="machined"), "machined")):
        a = assess.assess(blank, [], OUT, **given)
        assert a.read.box.process == a.spec.box.process == want
    said = replace(blank, box=replace(blank.box, process="machined"))
    a = assess.assess(said, [], OUT, blank_process="printed")
    assert a.read.box.process == a.spec.box.process == "machined"


def test_the_form_shares_process_and_nozzle_between_a_pairs_gears():
    assert gui.GEAR_COMPOUND == ("kind", "recipe", "process", "nozzle")

# The sentences a machined gear is told by K11 (an app-owned value changed in SolidWorks) and by the card. The
# functions saying them are B's (swbuild's K11 words) and C's (ui_text) to change for printed gears, so what they say
# of a machined gear is held here, outside their own test files (F1-0-REVIEW §7, must-fix 3).

TOLD = ("spur", "spur_m0.5_z30", "spur_shifted", "spur_typed", "helical", "herringbone_grooved", "ring", "ring_rim",
        "ring_helical", "bevel", "bevel_crown", "bevel_internal", "sleeve_banded", "dog", "hub")
K11_GLOBALS = ("Backlash", "Fillet Radius", "Bore Diameter")


def k11_sentences(name: str) -> list:
    """K11's sentence for each of the gear's Backlash, Fillet and Bore found changed in SolidWorks to 0.123: with its
    cell, with no cell, and on a document left unsaved (`swbuild._value_sentence`, through `_blank_meaning`,
    `_wanted_words` and `_back_words`)."""
    from gear_generator import swbuild
    spec = _spec(name)
    kind = kind_for(spec)
    g = kind.derive(spec)
    plan = kind.plan(spec, g, kind.recipe_for(spec), TEMPLATE, OUT + spec.stem() + ".SLDPRT")
    values = plan.values(DEGREES)
    out = []
    for v in kind.variables(spec, g):
        if v.name not in K11_GLOBALS:
            continue
        wanted = f"{values[v.name]:g}"
        for cell, unsaved in (("Gears!P2", False), ("", False), ("Gears!P2", True)):
            edit = swbuild.ValueEdit(spec.stem() + ".SLDPRT", v.name, "0.123", wanted, wanted, cell=cell,
                                     unsaved=unsaved, blank=swbuild._blank_meaning(v))
            out.append(swbuild._value_sentence(edit))
    return out


def card_text(name: str) -> str:
    """The card a machined gear shows: its Derived rows and line, and the explainer of every field the card has."""
    from gear_generator import ui_text
    spec = _spec(name)
    g = kind_for(spec).derive(spec)
    out = [repr(ui_text.derived_rows(g)), ui_text.derived_line(g)]
    for field in ui_text.EXPLAINER_FIELDS:
        if field not in ui_text.PAIR_EXPLAINERS:
            try:
                out.append(repr(ui_text.explainer(field, g, spec.stem(), folder="C:\\Out")))
            except Exception as exc:        # noqa: BLE001 -- a field the card cannot work out for this kind, as it is
                out.append(f"{field}: {type(exc).__name__}")
    return "\n".join(out)


K11 = {
    "bevel": "64d22adad95289e2684498d2c3370d6b3248de58105438a74be26e089284b18e",
    "bevel_crown": "cdcb2e5273bb1da3b8ff9d821cfd5b37b46fe9ab7493e66d4a4c2e1b6c32a33a",
    "bevel_internal": "96d4f500dfbe65dd56271bd242ddd7101ddda64e25498374d7d3a489aee238c6",
    "dog": "036ca9077d7aba48ef8c1b531ce20351430b56264f38c6cd10530f4b63159f66",
    "helical": "0d66bff68b845356dabadb73af89c5482e43c6f8fa3049f9f2fff7f66afaeb03",
    "herringbone_grooved": "89f7b8bac8e8b4f8323fdc1104cba784bd8dfca81c0f76d4c3dafc383730c2a6",
    "hub": "7973a5ebaa7628793a19223e5f0bf4284301d1649cfeb6ffd17cc412914c191b",
    "ring": "d495bf4858cdb31c3c1eb2e9140031b97ac73d7b43949565ad5b84bc8cd53b38",
    "ring_helical": "cebab19f67a7762042cef03ee2710a95830073a9008a15d0fe21b86c20322e19",
    "ring_rim": "2b81898edce72dcd37c005d1cfcab153115e0ffab7749edfb0fb74c0b2de0856",
    "sleeve_banded": "c414a3bf6d33d82f21441056cd49e18015ae461fab1803840439fcfba3759dcc",
    "spur": "634f17fe1a470bd72c68acc548ef9cf686a6e6ecf70a11e1308d96d4fbcc5144",
    "spur_m0.5_z30": "7e205f851d453b09f300b460904dd9ec983cbf1188b1cedbad41987088c85927",
    "spur_shifted": "eb2cf7ede948f303001d6b5596e8b195f23e0b89c4720308ae14aa21a2634f73",
    "spur_typed": "61d179dfd30887a3db9a84a1355a95b43b1c02ec3b51c16dda2b21d5103a85c0",
}

CARD = {
    "bevel": "36a5c1b95918e0c0220b41a811bd04694238728efebbc0813c995b0db72cb9f9",
    "bevel_crown": "2d268d847f83fda5403fd411a02ec3fdad20a0ddeb83bccbcbb192bd5cdbe90c",
    "bevel_internal": "030f48fb461013d180a073b8aeef489eba73b137d01e0142ff9dfda5a11e58b6",
    "dog": "bcb1146fa852c0da7b7d65d3543c123ac28be27d2511fb92234f129bd471c7cd",
    "helical": "07a5f9523fd3bd1e533f816378d95b55b0d0a5d497521e3eaddaf584a19e4d2b",
    "herringbone_grooved": "7984b6a2be08bbb52a11171f74743d8629cadaea4e473d319a0d92627a083f37",
    "hub": "c835d9b888e7157f7dd57755f9fb83822fecd3ead1a9715bb935e8cde6a25100",
    "ring": "cbdf1a639b3a4bbea88f671cea6c354e8f1e1d268b7bb22f6a7c5a0220059dda",
    "ring_helical": "bc98bfdbf768c1244542fac865262dec980693f3ceb648a06988be32894589a1",
    "ring_rim": "6beabbafe2e88b215354c34014c9f927b114404bca1bcf208aa587cd7915ae51",
    "sleeve_banded": "15a77567b77e73f9493f1f06fddcf108f0948bd2598b38b95d7660443ed1f3f7",
    "spur": "dd4ae6bd8a4861d269b3f8adf0a06edd11803a479455b4ec9dc97f60f5cf74bc",
    "spur_m0.5_z30": "33321deb1b3d701ab6f92a7b7f8de2af692431b73e790fb91a7e10f45aa64389",
    "spur_shifted": "cc40ab41f8e2d93c065b1673c8f2852f086382d1dd08a4805aaece5c083fc9fa",
    "spur_typed": "2be86bb010539576b54ed461348ca40faa413f1431745bf29ce1df263e1ff37d",
}


@pytest.mark.parametrize("name", TOLD)
def test_what_k11_tells_of_a_machined_gear_is_as_at_the_cut(name):
    assert _sha("\n".join(k11_sentences(name))) == K11[name]


def test_k11_says_a_machined_blank_backlash_and_fillet_as_their_equations():
    said = k11_sentences("spur")
    assert ("Backlash in Gear_m1.5_N25 is 0.123 in SolidWorks and 0.45 (from its blank cell, 0.3 × Module) in the "
            "workbook: type 0.123 in Gears!P2, or set it back to the equation 0.3 × Module in SolidWorks, and press "
            "Update SolidWorks again.") in said
    assert ("Fillet Radius in Gear_m1.5_N25 is 0.123 in SolidWorks and 0.57 (from its blank cell, 0.38 × Module) in "
            "the workbook: type 0.123 in Gears!P2, or set it back to the equation 0.38 × Module in SolidWorks, and "
            "press Update SolidWorks again.") in said


@pytest.mark.parametrize("name", TOLD)
def test_the_card_of_a_machined_gear_is_as_at_the_cut(name):
    assert _sha(card_text(name)) == CARD[name]


def test_the_card_says_a_machined_blank_backlash_is_0_3_module():
    from gear_generator import ui_text
    g = kind_for(GearSpec()).derive(GearSpec())
    assert dict(ui_text.derived_rows(g))["Backlash"] == "0.45 · 0.3m"
    assert ui_text.explainer("backlash", g, "Gear_m1.5_N25")[3].startswith("blank → 0.45 mm (0.3 m) · tooth ")


# -- a pair's names (the coordinator's ruling 2 on F1-0's decision 2, 2026-11-18) ----------------------------------

G = GearSpec
PAIRS = {
    "spur": (PairSpec(gear_a=G(teeth="20"), gear_b=G(teeth="60")),
             ("Pinion_m1.5_N20", "Gear_m1.5_N60", "Pair_m1.5_20T_60T")),
    "spur_reversed": (PairSpec(gear_a=G(teeth="60"), gear_b=G(teeth="20")),
                      ("Gear_m1.5_N60", "Pinion_m1.5_N20", "Pair_m1.5_60T_20T")),
    "shifted": (PairSpec(gear_a=G(teeth="15", profile_shift="0.09"), gear_b=G(teeth="30", profile_shift="-0.09")),
                ("Pinion_m1.5_N15_x0.09", "Gear_m1.5_N30_x-0.09", "Pair_m1.5_15T_30T_x0.09_-0.09")),
    "ring": (PairSpec(mesh="internal", gear_a=G(teeth="20"), gear_b=G(teeth="60", teeth_side="internal")),
             ("Pinion_m1.5_N20", "Ring_m1.5_N60", "Pair_m1.5_20T_60T_INT")),
    "helical": (PairSpec(gear_a=G(kind="helical", helix_angle="20", teeth="20"),
                         gear_b=G(kind="helical", helix_angle="20", hand="left", teeth="40")),
                ("Pinion_m1.5_N20_20R", "Gear_m1.5_N40_20L", "Pair_m1.5_20T_40T_H20")),
    "herringbone": (PairSpec(gear_a=G(kind="herringbone", helix_angle="30", teeth="20"),
                             gear_b=G(kind="herringbone", helix_angle="30", hand="left", teeth="40")),
                    ("Pinion_m1.5_N20_HB30R", "Gear_m1.5_N40_HB30L", "Pair_m1.5_20T_40T_HB30")),
    "ring_helical": (PairSpec(mesh="internal", gear_a=G(kind="helical", helix_angle="15", teeth="20"),
                              gear_b=G(kind="helical", helix_angle="15", teeth="60", teeth_side="internal")),
                     ("Pinion_m1.5_N20_15R", "Ring_m1.5_N60_15R", "Pair_m1.5_20T_60T_INT_H15")),
    "crossed": (PairSpec(shafts="crossed", shaft_angle="90", gear_a=G(kind="helical", helix_angle="45", teeth="20"),
                         gear_b=G(kind="helical", helix_angle="45", teeth="30")),
                ("Pinion_m1.5_N20_45R", "Gear_m1.5_N30_45R", "Pair_m1.5_20T_30T_X90")),
    "crossed_opposite": (PairSpec(shafts="crossed", shaft_angle="30", hands="opposite",
                                  gear_a=G(kind="helical", helix_angle="45", teeth="20"),
                                  gear_b=G(kind="helical", helix_angle="15", hand="left", teeth="30")),
                         ("Pinion_m1.5_N20_45R", "Gear_m1.5_N30_15L", "Pair_m1.5_20T_30T_XO30")),
    "bevel": (PairSpec(gear_a=G(kind="bevel", teeth="20", mate_teeth="40"),
                       gear_b=G(kind="bevel", teeth="40", mate_teeth="20")),
              ("Pinion_m1.5_N20_M40", "Gear_m1.5_N40_M20", "Pair_m1.5_20T_40T_B90")),
    "bevel_s80": (PairSpec(shaft_angle="80", gear_a=G(kind="bevel", teeth="20", mate_teeth="30", shaft_angle="80"),
                           gear_b=G(kind="bevel", teeth="30", mate_teeth="20", shaft_angle="80")),
                  ("Pinion_m1.5_N20_M30_S80", "Gear_m1.5_N30_M20_S80", "Pair_m1.5_20T_30T_B80")),
    "named": (PairSpec(assembly_name="MyPair", gear_a=G(teeth="20", name="A1"), gear_b=G(teeth="60")),
              ("A1", "Gear_m1.5_N60", "MyPair")),
}


def _pair_marked(pair, **marked):
    return replace(pair, gear_a=replace(pair.gear_a, **marked), gear_b=replace(pair.gear_b, **marked))


@pytest.mark.parametrize("marked", ({},) + MACHINED, ids=repr)
@pytest.mark.parametrize("name", sorted(PAIRS))
def test_a_machined_pairs_names_are_as_at_the_cut(name, marked):
    """Each value as pair_stems gave it at f3c4873, for every shape of pair (checked there by running this table)."""
    from gear_generator.spec import pair_stems
    pair, stems = PAIRS[name]
    assert pair_stems(_pair_marked(pair, **marked)) == stems


@pytest.mark.parametrize("name", sorted(PAIRS))
def test_a_printed_pair_and_its_assembly_end_p_and_a_typed_name_is_kept(name):
    from gear_generator.spec import pair_stems
    pair, (a, b, assembly) = PAIRS[name]
    got = pair_stems(_pair_marked(pair, process="printed"))
    typed = (pair.gear_a.name, pair.gear_b.name, pair.assembly_name)
    assert got == tuple(s if t else s + "_P" for s, t in zip((a, b, assembly), typed))
    one = pair_stems(replace(pair, gear_b=replace(pair.gear_b, process="Printed")))
    assert one[2] == (assembly if pair.assembly_name else assembly + "_P")          # either gear printed marks it


# -- where the Box's Process was read (the review's must-fix 1) ---------------------------------------------------

def test_the_box_says_where_its_process_was_read_and_it_is_not_what_the_gearbox_is():
    from gear_generator.workbook import model
    assert model.Box().process_cell == ""
    assert model.Box(process="", process_cell="Box!B9") == model.Box(process="")
    rows = [row[0] for row in model.to_sheets(replace(model.template(), box=model.Box(process_cell="Box!B9")))[0].rows]
    assert "process_cell" not in " ".join(map(str, rows))
