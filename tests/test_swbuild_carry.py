"""W9d package A (W9D-INTERFACES.md; ISSUE-1-PLAN §2.5): Build again… carries the user's work. The pure decisions
(``plan_carry``, ``carry_gates``) on hand-made ``OldWork``s, and the worker against the fake SolidWorks of
``test_swbuild``. A test that needs a W9d finding set patches it; one that needs it unset takes ``none_on_2026`` (the
probes' reads) or ``w9d_unmeasured`` (the demonstration's, set on 2026 since its review), and each is also tested at
None, where the item is named with the finding, never guessed."""

import math

import pytest

from gear_generator import findings, swbuild, swcom
from gear_generator.swcom import SolidWorksError
from gear_generator.swbuild import (APP, ASSEMBLY, ENTITY_EDGE, ENTITY_FACE, ENTITY_FEATURE, ENTITY_ORIGIN,
                                    ENTITY_PLANE, ENTITY_UNREAD, ENTITY_VERTEX, ENTITY_WHOLE, LAYOUT, USER, Carry,
                                    CarryBody, OldComponent, OldEntity, OldMate, OldWork, UNREAD_ENTITY)

I9 = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
REVISION = (34, 1, 1)                      # SolidWorks 2026
Y = "2026"
OLD = swbuild.OldAssembly(r"C:\B\RangeBox.SLDASM", (("Sun", "gear1-1"), ("Ring", "gear2-1")), "layout-1",
                          r"C:\B\RangeBox_layout.SLDPRT", ("Mesh1",), ("H", "L"))
LAYOUT_NAMES = ("Input Axis", "Output Axis", "Input Plane")
GEAR_NAMES = ("Gear Axis", "Tooth Space", "Teeth")


def _bodies(sun_same=False, ring_handle="gear2", output=True):
    return (CarryBody("layout", "layout-1", "layout", False, "its layout part is new with every revision",
                      LAYOUT_NAMES if output else ("Input Axis", "Input Plane"), LAYOUT_NAMES),
            CarryBody("C carrier", "carrier1-1", "carrier1", False, "its carrier part is new", ("Planet Axis",),
                      ("Planet Axis",)),
            CarryBody("Sun", "gear1-1", "gear1", sun_same, "" if sun_same else "its Flank changed", GEAR_NAMES,
                      GEAR_NAMES),
            CarryBody("Ring", "gear2-1", ring_handle, False, "its Part name changed" if ring_handle else "",
                      GEAR_NAMES, GEAR_NAMES))


def _carry(**kwargs):
    return Carry(OLD, _bodies(**kwargs), ("H", "L"), "H", (34,), ())


def comp(name="Sprocket-1", path=r"C:\U\Sprocket.SLDPRT", frame=(I9, (0.0, 0.0, 20.0)), **kw):
    kw.setdefault("configurations", ("Default",))
    kw.setdefault("configuration", "Default")
    kw.setdefault("active_configuration", "Default")
    return OldComponent(name, path, kw.pop("kind", "part"), kw.pop("fixed", False), 0, kw.pop("state", 2), frame,
                        **kw)


def ent(what, owner, kind, feature="", **kw):
    select = {ENTITY_FEATURE: 5 if feature.endswith("Axis") else 4, ENTITY_PLANE: 4, ENTITY_FACE: 2, ENTITY_EDGE: 1,
              ENTITY_VERTEX: 3, ENTITY_WHOLE: 20, ENTITY_ORIGIN: 6}.get(kind, -1)
    kw.setdefault("select_type", select)
    if kind in (ENTITY_FACE, ENTITY_EDGE, ENTITY_VERTEX) or (what == USER and kind in (ENTITY_FEATURE, ENTITY_PLANE)):
        kw.setdefault("reference", "384a0001")
    return OldEntity(what, owner, kind, feature, **kw)


def mate(name, type_, *entities, values=(), params=(), on=("H", "L"), type_name="", whole=True):
    return OldMate(name, type_, type_name, 0, False, tuple(values), tuple(entities), tuple(params), on, 0, True, whole)


def lock(name, a, b):
    return mate(name, 16, a, b)


SUN_WHOLE = ent(APP, "Sun", ENTITY_WHOLE)


def work(components=(), mates=(), how=swbuild.OLD_OPEN, **kw):
    kw.setdefault("states_route", "route")              # read per mode, unless a test says otherwise
    return OldWork("2026-11-17T10:00:00Z", OLD.path, how, kw.pop("active", "H"), kw.pop("modes", ("H", "L")),
                   list(components), list(mates),
                   kw.pop("app_frames", (("Sun", (I9, (0.0, 0.0, 10.0))), ("Ring", (I9, (0.0, 0.0, 0.0))))), **kw)


W9D_SET_ON_2026 = ("COMPONENT_STATE_PER_CONFIGURATION_ROUTE", "COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED",
                   "FILE_VERSION_READ", "DEPENDENCIES_READ", "OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS",
                   "OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN", "SUBASSEMBLY_OPEN_MARKS", "SUBASSEMBLY_READ_ONLY_INSERT",
                   "SUBASSEMBLY_OPEN_MARKS_WHEN_LOADED", "PERSIST_REFERENCE_ROUTE_FOR_FACES",
                   "PERSIST_REFERENCE_ROUTE_FOR_EDGES", "PERSIST_REFERENCE_SURVIVES_RELOAD", "COAXIAL_FACE_READ",
                   "CARRY_INSERT_MARKS_USER_DOCUMENTS")


@pytest.fixture
def none_on_2026(monkeypatch):
    """Every W9d probe read None on 2026 (the fake's version), as before W9d's probes set §8.1's; the demonstration's
    findings are ``w9d_unmeasured``'s (conftest)."""
    for name in W9D_SET_ON_2026:
        monkeypatch.setattr(findings, f"{name}_ON_2026", None)


@pytest.fixture
def every_gate(monkeypatch):
    """Every W9d gate patched to its settled value on 2026, as M9 patches them in its own process."""
    def patch(**override):
        values = dict(CARRY_INSERTS=True, CARRY_INSERTS_IN_A_CONFIGURATION=True, CARRY_INSERTS_A_SUBASSEMBLY=True,
                      REFERENCED_CONFIGURATION_READ=True, SUBASSEMBLY_OPEN_MARKS=False,
                      SUBASSEMBLY_OPEN_MARKS_WHEN_LOADED=False, SUBASSEMBLY_READ_ONLY_INSERT=True,
                      PERSIST_REFERENCE_ROUTE_FOR_FACES=swcom.PERSIST_ROUTE_R3,
                      PERSIST_REFERENCE_ROUTE_FOR_EDGES=swcom.PERSIST_ROUTE_R3,
                      PERSIST_REFERENCE_ROUTE_FOR_VERTICES="route", PERSIST_REFERENCE_SURVIVES_RELOAD=True,
                      COAXIAL_FACE_READ=True, CARRY_REMAKE_KINDS=swbuild.CARRY_KIND_WORDS,
                      CARRY_GEAR_MATE_ON_AN_APP_GEAR=True, COMPONENT_STATE_PER_CONFIGURATION_ROUTE="route",
                      FILE_VERSION_READ="route", DEPENDENCIES_READ="route", OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN=True,
                      OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS=True)
        values.update(override)
        for name, value in values.items():
            monkeypatch.setattr(findings, f"{name}_ON_2026", value)
    return patch


def _named(plan):
    return {n.item: (n.why, n.subjects) for n in plan.named}


# -- plan_carry and carry_gates: every reason, with its subjects slot by slot (§2.3) ----------------------------------


def test_with_every_gate_none_nothing_is_carried_and_each_item_names_its_finding(w9d_unmeasured):
    w = work([comp()], [lock("Lock1", SUN_WHOLE, ent(USER, "Sprocket-1", ENTITY_WHOLE))])
    plan = swbuild.plan_carry(w, _carry(), REVISION)
    assert plan.components == () and plan.mates == ()
    assert _named(plan) == {"Sprocket-1": ("unmeasured", ("insert", "CARRY_INSERTS_ON_2026", Y)),
                            "Lock1": ("component not carried", ("Sprocket-1",))}
    assert swbuild.carry_gates(w, _carry(), REVISION) == [(swbuild.STEP_CARRY_INSERT, "CARRY_INSERTS_ON_2026")]


def test_what_a_carry_is_gated_on_per_version_as_committed():
    """With no fixture (findings.py as committed: W9d's probes and M9's runs set on 2026 and on 2024): on
    2026 a part, a part in one of its file's configurations, a lock, an axis mate and a gear mate on Sun's Gear Axis
    are carried with nothing gated, and only what M9's fixture had none of is held, each by its finding: a
    sub-assembly, a kind outside the eight (perpendicular), a vertex and an origin; a virtual part is named by its
    `^` with no finding. On 2024, set since the 2024 probes and confirming run each as its 2026 twin, the same."""
    face = ent(USER, "Sprocket-1", ENTITY_FACE)
    values = (("GearRatioNumerator", 29.0), ("GearRatioDenominator", 20.0), ("Reverse", 1.0))
    params = ((0, 0, 0, 0, 0, 1), (0, 0, 0, 0, 0, 1))
    mates = [lock("Lock1", SUN_WHOLE, ent(USER, "Sprocket-1", ENTITY_WHOLE)),
             mate("UserAxis1", 0, ent(USER, "Sprocket-1", ENTITY_FEATURE, "Axis1"),
                  ent(APP, "Sun", ENTITY_FEATURE, "Gear Axis")),
             mate("Gear6", 10, ent(USER, "Sprocket-11", ENTITY_FEATURE, "Axis1"),
                  ent(APP, "Sun", ENTITY_FEATURE, "Gear Axis"), values=values, params=params),
             mate("Perp1", 2, face, ent(APP, "Sun", ENTITY_PLANE, "plane1")),
             mate("Vertex1", 0, ent(USER, "Sprocket-1", ENTITY_VERTEX), ent(APP, "Sun", ENTITY_PLANE, "plane2")),
             mate("Origin1", 0, ent(USER, "Sprocket-1", ENTITY_ORIGIN, "origin"), ent(APP, "Sun", ENTITY_PLANE,
                                                                                      "plane1"))]
    w = work([comp(), comp("Sprocket-11", configurations=("Z15", "Z20"), configuration="Z20",
                           active_configuration="Z15"),
              comp("Drive-1", r"C:\U\Drive.SLDASM", kind="assembly"),
              comp("Part1^RangeBox-1", r"C:\Temp\Part1^RangeBox.sldprt")], mates)
    plan = swbuild.plan_carry(w, _carry(), REVISION)
    assert swbuild.carry_gates(w, _carry(), REVISION) == [
        (swbuild.STEP_CARRY_SUBASSEMBLY, "CARRY_INSERTS_A_SUBASSEMBLY_ON_2026"),
        (swbuild.STEP_CARRY_KIND, "CARRY_REMAKE_KINDS_ON_2026"),
        (swbuild.STEP_CARRY_VERTICES, "PERSIST_REFERENCE_ROUTE_FOR_VERTICES_ON_2026"),
        (swbuild.STEP_CARRY_ORIGIN, "ORIGIN_ENTITY_READ_ON_2026")]
    assert [i.component.name for i in plan.components] == ["Sprocket-1", "Sprocket-11"]
    assert [m.mate.name for m in plan.mates] == ["Lock1", "UserAxis1", "Gear6"]
    assert _named(plan) == {
        "Drive-1": ("unmeasured", ("sub-assembly", "CARRY_INSERTS_A_SUBASSEMBLY_ON_2026", Y)),
        "Part1^RangeBox-1": ("no file", ("Part1^RangeBox.sldprt", "virtual")),
        "Perp1": ("unmeasured", ("perpendicular", "CARRY_REMAKE_KINDS_ON_2026", Y)),
        "Vertex1": ("unmeasured", ("vertex", "PERSIST_REFERENCE_ROUTE_FOR_VERTICES_ON_2026", Y, "Sprocket-1")),
        "Origin1": ("unmeasured", ("origin", "ORIGIN_ENTITY_READ_ON_2026", Y, "Sprocket-1"))}
    on_2024 = (32, 5, 0)                    # set since the 2024 run as each 2026 twin: the same, on 2024
    plan = swbuild.plan_carry(w, _carry(), on_2024)
    assert swbuild.carry_gates(w, _carry(), on_2024) == [
        (swbuild.STEP_CARRY_SUBASSEMBLY, "CARRY_INSERTS_A_SUBASSEMBLY_ON_2024"),
        (swbuild.STEP_CARRY_KIND, "CARRY_REMAKE_KINDS_ON_2024"),
        (swbuild.STEP_CARRY_VERTICES, "PERSIST_REFERENCE_ROUTE_FOR_VERTICES_ON_2024"),
        (swbuild.STEP_CARRY_ORIGIN, "ORIGIN_ENTITY_READ_ON_2024")]
    assert [i.component.name for i in plan.components] == ["Sprocket-1", "Sprocket-11"]
    assert [m.mate.name for m in plan.mates] == ["Lock1", "UserAxis1", "Gear6"]
    assert _named(plan) == {
        "Drive-1": ("unmeasured", ("sub-assembly", "CARRY_INSERTS_A_SUBASSEMBLY_ON_2024", "2024")),
        "Part1^RangeBox-1": ("no file", ("Part1^RangeBox.sldprt", "virtual")),
        "Perp1": ("unmeasured", ("perpendicular", "CARRY_REMAKE_KINDS_ON_2024", "2024")),
        "Vertex1": ("unmeasured", ("vertex", "PERSIST_REFERENCE_ROUTE_FOR_VERTICES_ON_2024", "2024", "Sprocket-1")),
        "Origin1": ("unmeasured", ("origin", "ORIGIN_ENTITY_READ_ON_2024", "2024", "Sprocket-1"))}


def test_a_user_part_locked_to_sun_is_carried_against_sun_and_its_lock_remade(every_gate):
    every_gate()
    c, s = math.cos(math.radians(37.0)), math.sin(math.radians(37.0))
    old_sun = ((c, -s, 0.0, s, c, 0.0, 0.0, 0.0, 1.0), (0.0, 0.0, 10.0))
    sprocket = (old_sun[0], (0.0, 0.0, 20.0))                  # stood with Sun, which the user had turned 37°
    w = work([comp(frame=sprocket)], [lock("Lock1", SUN_WHOLE, ent(USER, "Sprocket-1", ENTITY_WHOLE))],
             app_frames=(("Sun", old_sun),))
    new_sun = (I9, (0.0, 0.0, 10.5))
    plan = swbuild.plan_carry(w, _carry(), REVISION, new_frames={"Sun": new_sun})
    assert plan.named == () and plan.gates == ()
    (item,) = plan.components
    assert item.anchor == "Sun" and item.cluster == 0
    # Its pose relative to Sun is kept: 37° less in the world, 0.5 mm along with Sun.
    rel_old, rel_new = swbuild._relative(old_sun, sprocket), swbuild._relative(new_sun, item.frame)
    assert all(abs(a - b) < 1e-9 for a, b in zip(rel_old[0] + rel_old[1], rel_new[0] + rel_new[1]))
    assert all(abs(a - b) < 1e-9 for a, b in zip(item.frame[0], I9)) and abs(item.frame[1][2] - 20.5) < 1e-9
    (m,) = plan.mates
    assert m.targets == ("gear1", "carried1") and m.cluster == 0 and m.ratio == (1.0, 1.0) and m.sense == 0
    assert plan.clusters == (("Sprocket-1",),)
    # B's foresight (no frames): the same decisions, the old frame kept.
    foreseen = swbuild.plan_carry(w, _carry(), REVISION)
    assert foreseen.components[0].frame == sprocket and foreseen.components[0].anchor == "Sun"


def test_components_named_for_each_reason_with_their_subjects(every_gate):
    every_gate(CARRY_INSERTS_A_SUBASSEMBLY=None)
    w = work([comp("Part1^RangeBox-1", r"C:\Temp\Part1^RangeBox.sldprt"),
              comp("Bracket-1", r"C:\U\Bracket.SLDPRT", on_disk=False),
              comp("Drive-1", r"C:\U\Drive.SLDASM", kind="assembly"),
              comp("Sprocket-7", frame=None, state=0),
              comp("Sprocket-11", configurations=("Z15", "Z20"), configuration="Z20", active_configuration="Z15"),
              comp("Sprocket-12", configurations=None, configuration="", active_configuration="")])
    plan = swbuild.plan_carry(w, _carry(), REVISION)
    assert _named(plan) == {
        "Part1^RangeBox-1": ("no file", ("Part1^RangeBox.sldprt", "virtual")),
        "Bracket-1": ("no file", ("Bracket.SLDPRT", "")),
        "Drive-1": ("unmeasured", ("sub-assembly", "CARRY_INSERTS_A_SUBASSEMBLY_ON_2026", Y)),
        "Sprocket-7": ("no frame", ("Sprocket-7", "H")),
        "Sprocket-12": ("configuration", ("Sprocket-12", "", ""))}
    assert [i.component.name for i in plan.components] == ["Sprocket-11"]          # several, both findings set
    assert plan.gates == ((swbuild.STEP_CARRY_SUBASSEMBLY, "CARRY_INSERTS_A_SUBASSEMBLY_ON_2026"),)


def test_a_file_of_several_configurations_needs_both_findings_and_one_needs_neither(every_gate):
    every_gate(REFERENCED_CONFIGURATION_READ=None, CARRY_INSERTS_IN_A_CONFIGURATION=None)
    w = work([comp("Sprocket-11", configurations=("Z15", "Z20"), configuration="Z20", active_configuration="Z15"),
              comp("Sprocket-1")])
    plan = swbuild.plan_carry(w, _carry(), REVISION)
    assert _named(plan) == {"Sprocket-11": ("unmeasured", ("configuration", "REFERENCED_CONFIGURATION_READ_ON_2026",
                                                           Y))}
    assert [i.component.name for i in plan.components] == ["Sprocket-1"]
    every_gate(CARRY_INSERTS_IN_A_CONFIGURATION=None)
    assert _named(swbuild.plan_carry(w, _carry(), REVISION))["Sprocket-11"][1][1] == \
        "CARRY_INSERTS_IN_A_CONFIGURATION_ON_2026"
    every_gate()                                       # set, but its configuration not among its file's: named
    odd = work([comp("Sprocket-11", configurations=("Z15",), configuration="Z99")])
    assert swbuild.plan_carry(odd, _carry(), REVISION).components     # one configuration: today's insert
    odd = work([comp("Sprocket-11", configurations=("Z15", "Z20"), configuration="Z99", active_configuration="Z15")])
    assert _named(swbuild.plan_carry(odd, _carry(), REVISION)) == {
        "Sprocket-11": ("configuration", ("Sprocket-11", "Z99", "Z15"))}


def test_a_sub_assembly_is_carried_only_by_an_open_measured_clean_or_the_read_only_insert(every_gate):
    sub = comp("Drive-1", r"C:\U\Drive.SLDASM", kind="assembly")
    every_gate(SUBASSEMBLY_OPEN_MARKS=True, SUBASSEMBLY_READ_ONLY_INSERT=None)
    assert _named(swbuild.plan_carry(work([sub]), _carry(), REVISION)) == {
        "Drive-1": ("unmeasured", ("sub-assembly", "SUBASSEMBLY_READ_ONLY_INSERT_ON_2026", Y))}
    every_gate(SUBASSEMBLY_OPEN_MARKS=True)
    assert swbuild.plan_carry(work([sub]), _carry(), REVISION).components


def test_mates_named_for_each_reason_with_their_subjects(every_gate):
    every_gate(CARRY_REMAKE_KINDS=("lock", "coincident", "distance"))
    user = ent(USER, "Sprocket-1", ENTITY_WHOLE)
    sprocket_face = ent(USER, "Sprocket-1", ENTITY_FACE)
    mates = [
        mate("Width1", 11, sprocket_face, ent(APP, "Sun", ENTITY_FACE)),
        mate("Concentric5", 1, ent(APP, "Sun", ENTITY_FACE, coaxial=True, radius_mm=5.0), ent(USER, "Sprocket-1", ENTITY_FEATURE,
                                                                               "Axis1")),
        lock("Lock4", ent(APP, "Ring", ENTITY_WHOLE), user),
        mate("UserAxis2", 0, ent(LAYOUT, "", ENTITY_FEATURE, "Output Axis"), ent(USER, "Sprocket-1", ENTITY_FEATURE,
                                                                                  "Axis1")),
        mate("Coincident9", 0, ent(ASSEMBLY, "", ENTITY_FEATURE, "Plane1"), sprocket_face),
        mate("Lock6", 16, ent(USER, "Bracket-1", ENTITY_WHOLE), user),
        mate("Mate12", 0, sprocket_face, ent(UNREAD_ENTITY, "", ENTITY_UNREAD, unread="its second entity"),
             whole=False),
        lock("Lock7", ent(USER, "Sprocket-4", ENTITY_WHOLE), SUN_WHOLE),
        mate("LeafAxis", 0, ent(USER, "Drive-1", ENTITY_FEATURE, "Axis1", leaf="Drive-1/P2Sprocket-1"),
             ent(APP, "Sun", ENTITY_FEATURE, "Gear Axis")),
        mate("Coincident6", 0, ent(APP, "Sun", ENTITY_FEATURE, "Mid Plane"), sprocket_face),
        mate("Origin1", 0, ent(USER, "Sprocket-1", ENTITY_ORIGIN, "origin"), ent(APP, "Sun", ENTITY_PLANE,
                                                                                  "plane1")),
        mate("Parallel2", 3, sprocket_face, ent(APP, "Sun", ENTITY_PLANE, "plane1")),
    ]
    bodies = _bodies(ring_handle="", output=False)
    bodies = bodies[:2] + (CarryBody("Sun", "gear1-1", "gear1", False, "its Flank changed", GEAR_NAMES,
                                     GEAR_NAMES + ("Mid Plane",), bore_mm=10.0),) + bodies[3:]
    carry = Carry(OLD, bodies, ("H", "L"), "H")
    w = work([comp(), comp("Sprocket-4", state=1), comp("Bracket-1", r"C:\U\Bracket.SLDPRT", on_disk=False)], mates)
    plan = swbuild.plan_carry(w, carry, REVISION)
    named = _named(plan)
    assert named == {
        "Bracket-1": ("no file", ("Bracket.SLDPRT", "")),
        "Width1": ("kind", ("width",)),
        "Concentric5": ("part new", ("Sun", "its Flank changed", "face", "bore")),
        "Lock4": ("gone", ("gear", "Ring")),
        "UserAxis2": ("gone", ("shaft", "Output")),
        "Coincident9": ("assembly feature", ("Plane1",)),
        "Lock6": ("component not carried", ("Bracket-1",)),
        "Mate12": ("unread", ("its second entity",)),
        "Lock7": ("lightweight", ("Sprocket-4",)),
        "LeafAxis": ("leaf", ("Drive-1",)),
        "Coincident6": ("gone", ("feature", "Mid Plane", "Sun")),
        "Origin1": ("unmeasured", ("origin", "ORIGIN_ENTITY_READ_ON_2026", Y, "Sprocket-1")),
        "Parallel2": ("unmeasured", ("parallel", "CARRY_REMAKE_KINDS_ON_2026", Y)),
    }, named
    assert {m.mate.name for m in plan.mates} == set()
    assert [i.component.name for i in plan.components] == ["Sprocket-1", "Sprocket-4"]   # lightweight: carried
    assert (swbuild.STEP_CARRY_KIND, "CARRY_REMAKE_KINDS_ON_2026") in plan.gates
    assert (swbuild.STEP_CARRY_ORIGIN, "ORIGIN_ENTITY_READ_ON_2026") in plan.gates
    assert (swbuild.STEP_CARRY_LEAF, "CARRY_REMAKES_ON_A_LEAF_ON_2026") in plan.gates


def test_tier_one_on_faces_and_edges_named_with_the_finding_while_it_is_none(every_gate):
    every_gate(PERSIST_REFERENCE_ROUTE_FOR_FACES=None, PERSIST_REFERENCE_ROUTE_FOR_EDGES=None,
               PERSIST_REFERENCE_ROUTE_FOR_VERTICES=None)
    face, edge = ent(USER, "Sprocket-1", ENTITY_FACE), ent(USER, "Sprocket-3", ENTITY_EDGE)
    vertex = ent(USER, "Sprocket-1", ENTITY_VERTEX)
    w = work([comp(), comp("Sprocket-3")],
             [mate("Coincident1", 0, face, ent(USER, "Sprocket-3", ENTITY_FACE)),
              mate("Concentric2", 1, edge, ent(APP, "Sun", ENTITY_FEATURE, "Gear Axis")),
              mate("Coincident3", 0, vertex, ent(APP, "Sun", ENTITY_PLANE, "plane2"))])
    plan = swbuild.plan_carry(w, _carry(), REVISION)
    assert _named(plan) == {
        "Coincident1": ("unmeasured", ("face", "PERSIST_REFERENCE_ROUTE_FOR_FACES_ON_2026", Y, "Sprocket-1")),
        "Concentric2": ("unmeasured", ("edge", "PERSIST_REFERENCE_ROUTE_FOR_EDGES_ON_2026", Y, "Sprocket-3")),
        "Coincident3": ("unmeasured", ("vertex", "PERSIST_REFERENCE_ROUTE_FOR_VERTICES_ON_2026", Y, "Sprocket-1"))}
    assert [g[0] for g in plan.gates] == [swbuild.STEP_CARRY_FACES, swbuild.STEP_CARRY_EDGES,
                                          swbuild.STEP_CARRY_VERTICES]
    every_gate()
    plan = swbuild.plan_carry(w, _carry(), REVISION)
    assert plan.named == ()
    by = {m.mate.name: m for m in plan.mates}
    assert by["Coincident1"].targets == ("ref:carried1:face:384a0001", "ref:carried2:face:384a0001")
    # Tier 2 on Sun's Gear Axis by name; a part made new is fine for a feature the app names.
    assert by["Concentric2"].targets == ("ref:carried2:edge:384a0001", "gear1:Gear Axis")
    # Point to plane coincident: MateEntity(0) is the second selection (the ledger), so selected reversed.
    assert by["Coincident3"].targets == ("gear1:plane2", "ref:carried1:vertex:384a0001")
    # One cluster: Sprocket-1 and -3 joined by Coincident1 (user–user).
    assert plan.clusters == (("Sprocket-1", "Sprocket-3"),)


def test_the_not_open_path_names_tier_one_until_a_reference_is_shown_to_survive_a_reload(every_gate):
    every_gate(PERSIST_REFERENCE_SURVIVES_RELOAD=None)
    w = work([comp()], [mate("Coincident1", 0, ent(USER, "Sprocket-1", ENTITY_FEATURE, "Sprocket Axis"),
                             ent(APP, "Sun", ENTITY_FEATURE, "Gear Axis")),
                        lock("Lock1", SUN_WHOLE, ent(USER, "Sprocket-1", ENTITY_WHOLE))],
             how=swbuild.OLD_READ_ONLY)
    plan = swbuild.plan_carry(w, _carry(), REVISION)
    assert _named(plan) == {"Coincident1": ("unmeasured", ("feature", "PERSIST_REFERENCE_SURVIVES_RELOAD_ON_2026", Y, "Sprocket-1"))}
    assert [m.mate.name for m in plan.mates] == ["Lock1"]
    assert plan.gates == ((swbuild.STEP_CARRY_RELOAD, "PERSIST_REFERENCE_SURVIVES_RELOAD_ON_2026"),)
    # Open: the same mate goes by tier 1, axis to axis selected reversed (MateEntity(0) the second selection).
    plan = swbuild.plan_carry(work(w.components, w.mates), _carry(), REVISION)
    assert plan.mates[0].targets == ("gear1:Gear Axis", "ref:carried1:feature:384a0001")


def test_an_old_assembly_not_read_names_everything_with_the_reason(every_gate, none_on_2026, w9d_unmeasured):
    w = work([comp()], [lock("Lock1", SUN_WHOLE, ent(USER, "Sprocket-1", ENTITY_WHOLE))], how=swbuild.OLD_UNREAD,
             unread=["RangeBox.SLDASM is not open in SolidWorks"])
    plan = swbuild.plan_carry(w, _carry(), REVISION)
    assert plan.components == () and plan.mates == ()
    assert _named(plan) == {"Sprocket-1": ("old unread", ("RangeBox.SLDASM is not open in SolidWorks",)),
                            "Lock1": ("old unread", ("RangeBox.SLDASM is not open in SolidWorks",))}
    assert [f for _, f in plan.gates] == ["FILE_VERSION_READ_ON_2026", "DEPENDENCIES_READ_ON_2026",
                                          "OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_2026", "CARRY_INSERTS_ON_2026"]
    every_gate()
    assert swbuild.carry_gates(w, _carry(), REVISION) == []


def test_a_user_gear_mate_on_an_app_gear_is_taken_on_its_gear_axis_when_coaxial(every_gate):
    every_gate(CARRY_GEAR_MATE_ON_AN_APP_GEAR=None)
    values = (("GearRatioNumerator", 20.0), ("GearRatioDenominator", 17.0), ("Reverse", 1.0))
    params = ((0, 0, 0, 0, 0, 1), (0, 0, 0, 0, 0, 1))
    six = ent(USER, "Sprocket-6", ENTITY_FEATURE, "Axis1")
    on_axis = mate("Gear1", 10, six, ent(APP, "Sun", ENTITY_FEATURE, "Gear Axis"), values=values, params=params)
    w = work([comp("Sprocket-6")], [on_axis])
    plan = swbuild.plan_carry(w, _carry(), REVISION)
    assert _named(plan) == {"Gear1": ("unmeasured", ("gear mate on an app gear",
                                                     "CARRY_GEAR_MATE_ON_AN_APP_GEAR_ON_2026", Y))}
    every_gate()
    on_face = mate("Gear2", 10, six, ent(APP, "Sun", ENTITY_FACE, coaxial=True), values=values, params=params)
    keyway = mate("Gear3", 10, six, ent(APP, "Sun", ENTITY_FACE, coaxial=False), values=values, params=params)
    edge = mate("Gear4", 10, six, ent(APP, "Sun", ENTITY_EDGE), values=values, params=params)
    plan = swbuild.plan_carry(work([comp("Sprocket-6")], [on_axis, on_face, keyway, edge]), _carry(), REVISION)
    by = {m.mate.name: m for m in plan.mates}
    assert by["Gear1"].targets == by["Gear2"].targets == ("ref:carried1:feature:384a0001", "gear1:Gear Axis")
    assert by["Gear1"].ratio == (17.0, 20.0)                   # the read denominator is AddMate5's numerator
    assert by["Gear1"].sense == 1                              # Reverse with the entities the same way: same way
    assert _named(plan) == {"Gear3": ("part new", ("Sun", "its Flank changed", "face", "")),
                            "Gear4": ("part new", ("Sun", "its Flank changed", "edge", ""))}
    # On a part reused, the keyway's face goes by tier 1.
    plan = swbuild.plan_carry(work([comp("Sprocket-6")], [keyway]), _carry(sun_same=True), REVISION)
    assert plan.mates[0].targets == ("ref:carried1:feature:384a0001", "ref:gear1:face:384a0001")
    # The coaxial read not set: a face on an app gear goes by the other tiers, and the gate is said.
    every_gate(COAXIAL_FACE_READ=None)
    unread_face = mate("Gear2", 10, six, ent(APP, "Sun", ENTITY_FACE), values=values, params=params)
    plan = swbuild.plan_carry(work([comp("Sprocket-6")], [unread_face]), _carry(), REVISION)
    assert _named(plan)["Gear2"][0] == "part new"
    assert (swbuild.STEP_CARRY_GEAR_MATE, "COAXIAL_FACE_READ_ON_2026") in plan.gates


def test_clusters_anchors_and_cluster_minus_one(every_gate):
    every_gate()
    s1, s3, s5 = (ent(USER, n, ENTITY_WHOLE) for n in ("Sprocket-1", "Sprocket-3", "Sprocket-5"))
    housing = ent(USER, "Housing-1", ENTITY_WHOLE)
    mates = [lock("Lock1", ent(APP, "Ring", ENTITY_WHOLE), s3),          # Sprocket-3's own lock: to Ring
             lock("Lock2", SUN_WHOLE, s1),                              # the cluster's first lock: to Sun
             lock("Lock3", s1, s3),                                     # user–user: one cluster
             mate("Angle1", 6, ent(APP, "Sun", ENTITY_PLANE, "plane1"), ent(ASSEMBLY, "", ENTITY_PLANE, "plane1"),
                  values=(("Angle", 0.5),)),                            # no user component: cluster -1
             mate("Distance1", 5, ent(USER, "Housing-1", ENTITY_PLANE, "plane1"),
                  ent(LAYOUT, "", ENTITY_FEATURE, "Input Plane"), values=(("Distance", 0.01),)),
             lock("Lock5", s5, housing)]
    w = work([comp("Sprocket-1"), comp("Sprocket-3"), comp("Housing-1", fixed=True), comp("Sprocket-5"),
              comp("Lonely-1")], mates)
    plan = swbuild.plan_carry(w, _carry(), REVISION)
    assert plan.named == ()
    # Numbered, and each cluster's components listed, in first-mate order (Lock1 names Sprocket-3 first).
    assert plan.clusters == (("Sprocket-3", "Sprocket-1"), ("Housing-1", "Sprocket-5"), ("Lonely-1",))
    anchors = {i.component.name: (i.anchor, i.cluster) for i in plan.components}
    assert anchors == {"Sprocket-1": ("Sun", 0), "Sprocket-3": ("Ring", 0), "Housing-1": ("", 1),
                       "Sprocket-5": ("", 1), "Lonely-1": ("", 2)}
    clusters = {m.mate.name: m.cluster for m in plan.mates}
    assert clusters == {"Lock1": 0, "Lock2": 0, "Lock3": 0, "Angle1": -1, "Distance1": 1, "Lock5": 1}
    by = {m.mate.name: m.targets for m in plan.mates}
    assert by["Angle1"] == ("gear1:plane1", "asm:plane1")
    assert by["Distance1"] == ("ref:carried3:plane:384a0001", "layout:Input Plane")


def test_a_kind_unknown_and_an_unread_type_are_named_by_kind(every_gate):
    every_gate()
    w = work([comp()], [mate("Odd1", 99, ent(USER, "Sprocket-1", ENTITY_WHOLE), SUN_WHOLE),
                        mate("Slot1", 21, ent(USER, "Sprocket-1", ENTITY_FACE), SUN_WHOLE),
                        mate("Limit1", 5, ent(USER, "Sprocket-1", ENTITY_PLANE, "plane1"),
                             ent(APP, "Sun", ENTITY_PLANE, "plane1"), type_name="MateLimitDistanceDim",
                             values=(("MaximumDistance", 0.02), ("MinimumDistance", 0.01)))])
    plan = swbuild.plan_carry(w, _carry(), REVISION)
    assert _named(plan) == {"Odd1": ("kind", ("unknown",)), "Slot1": ("kind", ("slot",))}
    assert swbuild.carry_kind(plan.mates[0].mate) == "limit distance"


def test_a_version_not_known_settles_nothing():
    w = work([comp()], [])
    plan = swbuild.plan_carry(w, _carry(), ())
    assert _named(plan) == {"Sprocket-1": ("unmeasured", ("insert", "CARRY_INSERTS_ON_?", ""))}


def test_the_states_route_is_a_gate_when_the_gearbox_has_modes(every_gate):
    every_gate(COMPONENT_STATE_PER_CONFIGURATION_ROUTE=None)
    w = work([comp()], [], states_route="")
    assert swbuild.carry_gates(w, _carry(), REVISION) == [
        (swbuild.STEP_CARRY_STATES, "COMPONENT_STATE_PER_CONFIGURATION_ROUTE_ON_2026")]
    shown = work([comp()], [], states_route="shown read-only")
    assert swbuild.carry_gates(shown, _carry(), REVISION) == []
    assert swbuild.carry_gates(work([comp()], [], modes=(), states_route=""), _carry(), REVISION) == []
    # The route set but not read (an open assembly with unsaved changes, the unsaved read not shown): that is why.
    every_gate(COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED=None)
    assert swbuild.carry_gates(w, _carry(), REVISION) == [
        (swbuild.STEP_CARRY_STATES, "COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED_ON_2026")]


def test_the_selection_order_follows_the_ledger():
    axis = ent(APP, "Sun", ENTITY_FEATURE, "Gear Axis")
    face = ent(USER, "Sprocket-1", ENTITY_FACE)
    plane = ent(APP, "Sun", ENTITY_PLANE, "plane1")
    origin = ent(USER, "Sprocket-1", ENTITY_ORIGIN, "origin")
    assert swbuild.selection_reversed("coincident", (axis, axis))
    assert swbuild.selection_reversed("concentric", (face, axis)) and swbuild.selection_reversed("concentric",
                                                                                                  (axis, face))
    assert swbuild.selection_reversed("coincident", (origin, plane))
    assert not swbuild.selection_reversed("distance", (origin, plane))
    assert not swbuild.selection_reversed("gear", (axis, axis))
    assert not swbuild.selection_reversed("coincident", (plane, plane))


# -- UserMate.entities: every Update's inventory keeps each entity's kind and feature (D5) ----------------------------


def test_an_updates_inventory_keeps_each_mates_entity_kinds_and_features():
    from test_swbuild import IDENTITY9, T_ASM, W, _built_train
    from test_swbuild_user_work import _moving

    fake = _built_train()
    fake.read_entity_kinds = True
    fake.user_component(T_ASM, "Housing-1", W + "Housing.SLDPRT", (IDENTITY9, (0.0, 0.0, -40.0)), fixed=True)
    fake.user_component(T_ASM, "Chain-1", W + "Sprocket.SLDPRT", (IDENTITY9, (0.0, 0.0, 60.0)))
    fake.user_mate(T_ASM, "Coincident7", kind="coincident", a=("Chain-1", "face:3"), b=("Housing-1", "plane1"))
    fake.user_mate(T_ASM, "Concentric8", kind="coincident", a=("Chain-1", "Gear Axis"), b=("layout-1", "S1 Axis"))
    fake.user_mate(T_ASM, "Distance9", kind="distance", a=("Housing-1", "origin"), b=("asm", "plane2"))
    fake.user_lock(T_ASM, "Lock1", "Housing-1", "Chain-1")
    result = _moving(fake)
    assert result.ok, result.log_lines()
    # A coincident reads its entities in its components' tree order, whatever was selected first (the W9d audit:
    # the probe's UserFaceCoin and M9's): Housing-1 was inserted before Chain-1, the layout before both.
    assert {m.name: m.entities for m in result.user_work.mates} == {
        "Coincident7": (("user", "Housing-1", "plane", "plane1"), ("user", "Chain-1", "face", "")),
        "Concentric8": (("layout", "", "feature", "S1 Axis"), ("user", "Chain-1", "feature", "Gear Axis")),
        "Distance9": (("user", "Housing-1", "origin", "origin"), ("assembly", "", "plane", "plane2")),
        "Lock1": (("user", "Housing-1", "whole", ""), ("user", "Chain-1", "whole", ""))}
    # A session that gives no kinds (an inventory read before W9d): no entities, as before.
    fake = _built_train()
    fake.user_component(T_ASM, "Housing-1", W + "Housing.SLDPRT", (IDENTITY9, (0.0, 0.0, -40.0)), fixed=True)
    fake.user_mate(T_ASM, "Distance9", kind="distance", a=("Housing-1", "plane2"), b=("asm", "plane2"))
    assert _moving(fake).user_work.mates[0].entities == ()


# -- the worker against the fake: a Build again… of the T train that carries the user's work --------------------------

from dataclasses import replace as _replace                                       # noqa: E402

from test_swbuild import (FakeSolidWorks, P17, P51, P68, S17, S51, S68, T_ASM, T_LAYOUT, TRAIN_GEARS, TRAIN_MATES,  # noqa: E402,E501
                          W, _built_train, _key, _train_layout_plan, _train_plan, plan as part_plan)
from gear_generator.gears import base as ops                                      # noqa: E402

R2 = {P17: W + "Gear_m1.5_N17_r2.SLDPRT", P68: W + "Gear_m1.5_N68_r2.SLDPRT", P51: W + "Gear_m1.5_N51_r2.SLDPRT",
      T_LAYOUT: W + "T_r2_Layout.SLDPRT", T_ASM: W + "T_r2.SLDASM"}
SPROCKET, HOUSING = W + "Sprocket.SLDPRT", W + "Housing.SLDPRT"
T_OLD = swbuild.OldAssembly(T_ASM, tuple((g, f"{h}-1") for h, g in TRAIN_GEARS.items()), "layout-1", T_LAYOUT,
                            tuple(TRAIN_MATES), ())
T_LAYOUT_NAMES = ("S2 X Plane", "S3 X Plane", "S3 Y Plane", "S1 Axis", "S2 Axis", "S3 Axis")


def _t_carry(written_on=(34,), app_files=None):
    bodies = (CarryBody("layout", "layout-1", "layout", False, "its layout part is new with every revision",
                        T_LAYOUT_NAMES, T_LAYOUT_NAMES),) + tuple(
        CarryBody(g, f"{h}-1", h, False, "its Part name changed", GEAR_NAMES, GEAR_NAMES)
        for h, g in TRAIN_GEARS.items())
    files = app_files if app_files is not None else (T_ASM, T_LAYOUT, P17, P68, P51) + tuple(R2.values())
    return Carry(T_OLD, bodies, (), "", written_on, files)


def _again_kwargs():
    def moved(op):
        return _replace(op, path=R2.get(op.path, op.path)) if isinstance(op, (ops.AddComponent, ops.SaveAs)) else op
    assembly = _train_plan()
    assembly = _replace(assembly, ops=tuple(moved(op) for op in assembly.ops), path=R2[T_ASM])
    layout = _train_layout_plan(path=R2[T_LAYOUT])
    parts = [part_plan(S17, path=R2[P17]), part_plan(S68, path=R2[P68]), part_plan(S51, path=R2[P51])]
    return dict(parts=parts, layout=layout, assembly=assembly, gears=TRAIN_GEARS)


def _old_train(**user):
    """The T train built, the user's Sprocket-1 locked to G1 in T.SLDASM (open, unsaved), and the fake guarding the
    old assembly and the user's files."""
    fake = _built_train()
    fake.read_entity_kinds = True
    fake.strict_handles = True                 # the fourth round: a handle is kept only within its bracket
    fake.user_component(T_ASM, "Sprocket-1", SPROCKET, (I9, (0.0, 0.0, 30.0)))
    fake.user_lock(T_ASM, "Lock1", "gear1-1", "Sprocket-1")
    fake._w9d()
    fake.protected = {_key(T_ASM), _key(SPROCKET), _key(HOUSING)}
    fake.no_save_after = _key(R2[T_ASM])
    fake.saved[_key(SPROCKET)] = ([], [])                     # the user's part on disk
    fake.saved[_key(HOUSING)] = ([], [])
    return fake


def _build_again(fake, carry=None, **kwargs):
    carry = carry or _t_carry()
    kwargs.setdefault("mtime", lambda path: 1.0)
    return swbuild.build_gearbox(fake, **_again_kwargs(), exists=fake.exists, before=carry.old, carry=carry,
                                 **kwargs)


def _isfile(monkeypatch, fake):
    monkeypatch.setattr(swbuild.os.path, "isfile", lambda path: _key(path) in fake.saved)


def test_build_again_refuses_a_carry_whose_old_assembly_is_not_the_one_left_behind():
    fake = _built_train()
    carry = _t_carry()
    with pytest.raises(swbuild.BuildError, match="fault in Gear Generator"):
        swbuild.build_gearbox(fake, **_again_kwargs(), exists=fake.exists, carry=carry)
    with pytest.raises(swbuild.BuildError, match="fault in Gear Generator"):
        swbuild.build_gearbox(fake, **_again_kwargs(), exists=fake.exists, before=_replace(T_OLD), carry=carry)
    assert fake.calls == []


def test_with_every_gate_none_the_old_assembly_is_read_nothing_is_carried_and_the_build_stands(monkeypatch,
                                                                                               none_on_2026,
                                                                                               w9d_unmeasured):
    fake = _old_train()
    _isfile(monkeypatch, fake)
    result = _build_again(fake)
    assert result.ok, result.log_lines()
    cr = result.carry
    assert cr.work.how == swbuild.OLD_OPEN and [c.name for c in cr.work.components] == ["Sprocket-1"]
    assert [m.name for m in cr.work.mates] == ["Lock1"]
    assert cr.inserted == [] and cr.remade == [] and not cr.unsaved and cr.stopped == ""
    assert {n.item: n.why for n in cr.named} == {"Sprocket-1": "unmeasured", "Lock1": "component not carried"}
    assert result.old_user_work is not None and [c.name for c in result.old_user_work.components] == ["Sprocket-1"]
    names = [n for n, *_ in fake.calls]
    assert "open_document" not in names[:names.index("new_part")]        # the old assembly never opened
    # Not open, every gate None: unread, never opened.
    fake = _old_train()
    fake.open_docs = [d for d in fake.open_docs if _key(d.path) != _key(T_ASM)]
    result = _build_again(fake)
    assert result.ok and result.carry.work.how == swbuild.OLD_UNREAD
    assert "open_read_only" not in [n for n, *_ in fake.calls]
    assert result.carry.work.unread[0].startswith("T.SLDASM is not open in SolidWorks, and Gear Generator reads it "
                                                  "then only when")


def test_a_user_part_locked_to_g1_is_carried_placed_against_g1_and_its_lock_made_again(monkeypatch, every_gate):
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.turn("gear1-1", 37.0)                                       # the user turned G1 in the old assembly
    old_g1, old_sprocket = fake.frames["gear1-1"], fake.frames["Sprocket-1"]
    import copy
    old_mates, touched = copy.deepcopy(fake.memory_mates[_key(T_ASM)]), set(fake.touched)
    result = _build_again(fake)
    assert result.ok, result.log_lines()
    cr = result.carry
    assert cr.stopped == "", cr.stopped
    assert cr.named == [] and cr.inserted == [("Sprocket-1", "carried1-1")]
    assert [(r[0], r[1]) for r in cr.remade] == [("Lock1", "Lock1")] and cr.unsaved
    new_g1, new_sprocket = fake.frames["gear1-1"], fake.frames["carried1-1"]
    old_rel, new_rel = swbuild._relative(old_g1, old_sprocket), swbuild._relative(new_g1, new_sprocket)
    assert all(abs(a - b) < 1e-9 for a, b in zip(old_rel[0] + old_rel[1], new_rel[0] + new_rel[1]))
    lock = fake.mate("Lock1", R2[T_ASM])
    assert lock is not None and (lock.a[0], lock.b[0]) == ("gear1-1", "carried1-1") and not lock.user
    # Nothing written to the old assembly, nothing saved after the new one's first save (the fake guards both).
    assert fake.memory_mates[_key(T_ASM)] == old_mates and (_key(T_ASM) in fake.touched) == (_key(T_ASM) in touched)
    assert [p for n, (p, *_) in ((n, a) for n, a in fake.calls if n == "save_as")][-1] == R2[T_ASM]
    assert cr.moved == [] and cr.fixed == []
    lines = result.log_lines()
    assert lines[-3:] == ["ok      carried Sprocket-1 as carried1-1", "ok      made Lock1 again",
                          "CHECK   the new assembly holds what was carried, not saved"]


def _closed(fake):
    """T.SLDASM saved with the user's work in it, then closed: only the app's parts and layout stay open."""
    import copy
    fake.saved_mates[_key(T_ASM)] = copy.deepcopy(fake.memory_mates[_key(T_ASM)])
    fake.open_docs = [d for d in fake.open_docs if _key(d.path) != _key(T_ASM)]
    for kept in (fake.memory, fake.memory_mates, fake.memory_configs):
        kept.pop(_key(T_ASM), None)
    fake.touched.discard(_key(T_ASM))
    return fake


@pytest.mark.parametrize("doctor, clause", [
    (dict(FILE_VERSION_READ=None), "findings.FILE_VERSION_READ_ON_2026"),
    (dict(DEPENDENCIES_READ=None), "findings.DEPENDENCIES_READ_ON_2026"),
    (dict(OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN=None), "findings.OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_2026"),
    (dict(OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS=None), "findings.OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS_ON_2026"),
    ("written on 2024", "it was last written on this SolidWorks"),
    ("file saved on 2024", "every file it uses were last saved by this SolidWorks"),
    ("a part of the user's saved on 2024", "every file it uses were last saved by this SolidWorks"),
    ("another document open", "nothing else is open in SolidWorks"),
])
def test_the_not_open_read_is_refused_unless_every_condition_holds_and_never_opens(monkeypatch, every_gate, doctor,
                                                                                  clause):
    every_gate(**(doctor if isinstance(doctor, dict) else {}))
    fake = _closed(_old_train())
    _isfile(monkeypatch, fake)
    fake.dependencies_of[_key(T_ASM)] = [SPROCKET]
    carry = _t_carry(written_on=(32,) if doctor == "written on 2024" else (34,))
    if doctor == "file saved on 2024":
        fake.file_versions[_key(T_ASM)] = 32
    if doctor == "a part of the user's saved on 2024":
        fake.file_versions[_key(SPROCKET)] = 32
    if doctor == "another document open":
        fake.open_docs.append(swcom.DocInfo("Other.SLDPRT", W + "Other.SLDPRT", 1))
    result = _build_again(fake, carry)
    assert result.ok
    cr = result.carry
    assert cr.work.how == swbuild.OLD_UNREAD and clause in cr.work.unread[0], cr.work.unread
    assert "open_read_only" not in [n for n, *_ in fake.calls]
    assert cr.inserted == [] and not cr.unsaved


def test_the_not_open_read_opens_read_only_shows_nothing_marks_nothing_and_closes(monkeypatch, every_gate):
    every_gate(PERSIST_REFERENCE_SURVIVES_RELOAD=None)
    fake = _closed(_old_train())
    _isfile(monkeypatch, fake)
    result = _build_again(fake)
    assert result.ok, result.log_lines()
    cr = result.carry
    assert cr.work.how == swbuild.OLD_READ_ONLY and cr.work.left == [] and cr.work.marked == []
    names = [n for n, *_ in fake.calls]
    assert names.index("open_read_only") < names.index("close_unsaved") < names.index("new_part")
    assert not any(_key(d.path) == _key(T_ASM) for d in fake.open_docs)
    assert cr.inserted == [("Sprocket-1", "carried1-1")] and [r[0] for r in cr.remade] == ["Lock1"]
    assert result.open_before == [d for d in result.open_before if _key(d) != _key(T_ASM)]


def test_tier_one_on_the_not_open_path_is_named_until_a_reference_survives_a_reload(monkeypatch, every_gate):
    every_gate(PERSIST_REFERENCE_SURVIVES_RELOAD=None)
    fake = _old_train()
    fake.user_mate(T_ASM, "Coincident2", kind="coincident", a=("Sprocket-1", "plane1"), b=("gear1-1", "plane1"))
    _closed(fake)
    _isfile(monkeypatch, fake)
    cr = _build_again(fake).carry
    assert {n.item: (n.why, n.subjects) for n in cr.named} == {
        "Coincident2": ("unmeasured", ("plane", "PERSIST_REFERENCE_SURVIVES_RELOAD_ON_2026", Y, "Sprocket-1"))}
    # Set, but the reference does not resolve after the reload here (asked by name: the fake's default is the
    # finding's, True on 2026): not found, its component carried.
    every_gate()
    fake = _old_train()
    fake.user_mate(T_ASM, "Coincident2", kind="coincident", a=("Sprocket-1", "plane1"), b=("gear1-1", "plane1"))
    _closed(fake)
    _isfile(monkeypatch, fake)
    fake._w9d().reload_ok = False
    cr = _build_again(fake).carry
    assert {n.item: n.why for n in cr.named} == {"Coincident2": "not found"}
    assert cr.inserted and [r[0] for r in cr.remade] == ["Lock1"]
    fake = _old_train()
    fake.user_mate(T_ASM, "Coincident2", kind="coincident", a=("Sprocket-1", "plane1"), b=("gear1-1", "plane1"))
    _closed(fake)
    _isfile(monkeypatch, fake)
    cr = _build_again(fake).carry                                   # the default: as the finding, set
    assert cr.named == [] and sorted(r[0] for r in cr.remade) == ["Coincident2", "Lock1"]


def test_a_read_that_marks_a_document_carries_nothing_and_says_so(monkeypatch, every_gate):
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.read_marks = {_key(T_ASM)}
    fake.touched.discard(_key(T_ASM))
    fake.memory[_key(T_ASM)] = fake.saved[_key(T_ASM)]
    result = _build_again(fake)
    assert result.ok and result.carry.work.marked == [T_ASM]
    assert result.carry.inserted == [] and result.carry.stopped.startswith("Reading T.SLDASM marked T.SLDASM")


def test_a_read_only_close_that_leaves_the_document_open_carries_nothing(monkeypatch, every_gate):
    every_gate()
    fake = _closed(_old_train())
    _isfile(monkeypatch, fake)
    fake.read_only_left = True
    result = _build_again(fake)
    assert result.ok and result.carry.work.left == [T_ASM] and result.carry.inserted == []
    assert "left T.SLDASM open" in result.carry.stopped


def _two_clusters(fake):
    """Sprocket-1 locked to G1 (the old train); Housing-1 fixed, with Sprocket-2 locked to it and to G4: a cluster that
    ties G4's train once its locks are on."""
    fake.user_component(T_ASM, "Housing-1", HOUSING, (I9, (0.0, 0.0, -40.0)), fixed=True)
    fake.user_component(T_ASM, "Sprocket-2", SPROCKET, (I9, (0.0, 0.0, 50.0)))
    fake.user_lock(T_ASM, "Lock2", "Housing-1", "Sprocket-2")
    fake.user_lock(T_ASM, "Lock3", "gear4-1", "Sprocket-2")
    return fake


def test_a_tied_cluster_falls_back_alone_while_the_other_is_carried_with_every_mate(monkeypatch, every_gate):
    every_gate()
    fake = _two_clusters(_old_train())
    _isfile(monkeypatch, fake)
    # Made again, Lock3 ties G4's train to the fixed housing (G3, G4 read fully defined while it is on).
    fake.locks["Lock3"] = ("gear3", "gear4", "gear3-1", "gear4-1", "gear2", "gear2-1")
    result = _build_again(fake)
    assert result.ok, result.log_lines()
    cr = result.carry
    assert cr.stopped == "", cr.stopped
    (fell,) = cr.fixed
    assert fell.why == swbuild.FELL_TIE and fell.deleted == ("Lock3",) and fell.kept == ("Lock2",)
    assert set(fell.components) == {"carried2-1", "carried3-1"}
    assert {r[0] for r in cr.remade} == {"Lock1", "Lock2"}
    assert fake.mate("Lock3", R2[T_ASM]) is None and fake.mate("Lock1", R2[T_ASM]) is not None
    assert {"carried2-1", "carried3-1"} <= fake.fixed
    fake.strict_handles = False                                       # the test's own look, after the job
    assert all(fake.constrained_status(h) == findings.COMPONENT_UNDER_DEFINED for h in ("gear1-1", "gear4-1"))


@pytest.mark.parametrize("case", ["new error", "over-defined", "same error"])
def test_a_new_error_or_an_over_definition_falls_back_and_the_same_error_is_carried(monkeypatch, every_gate, case):
    every_gate()
    fake = _two_clusters(_old_train())
    _isfile(monkeypatch, fake)
    if case == "same error":
        # Lock1 alone holds Sprocket-1 to G1 and was in error before: its over-definition and tie are its own, excused.
        fake.mate_codes["Lock1"] = (46, True)
        fake.remake_codes["Lock1"] = (46, True)
    elif case == "new error":
        fake.remake_codes["Lock3"] = (46, True)
    else:
        fake.remake_status["Lock3"] = findings.ADD_MATE_OVER_DEFINED
    cr = _build_again(fake).carry
    if case == "same error":
        # M3 (fifth round): Lock1 reads its old over-definition again, and with it G1, free before, no longer turns:
        # the same-error excuse never excuses a gear's tie (K2), so its cluster falls back.
        assert [(f.why, f.subjects) for f in cr.fixed][0] == (swbuild.FELL_TIE, ("G1", ""))
        assert cr.same_error == []                      # what the fallback deleted is not said carried
        return
    (fell,) = cr.fixed
    assert fell.why == (swbuild.FELL_NEW_ERROR if case == "new error" else swbuild.FELL_OVER_DEFINED)
    assert fell.subjects == (("Lock3", "46", "0", "") if case == "new error" else ("Lock3",))
    assert "Lock1" in {r[0] for r in cr.remade}


def test_a_carry_that_stops_part_way_says_what_it_did_and_leaves_the_build_saved(monkeypatch, every_gate):
    every_gate()
    fake = _two_clusters(_old_train())
    _isfile(monkeypatch, fake)
    fake.raises["remake_mate"] = (3, RuntimeError("SolidWorks stopped answering."))   # a COM failure, not a refusal
    result = _build_again(fake)
    assert result.ok and result.assembly.saved == R2[T_ASM]
    cr = result.carry
    assert cr.inserted and len(cr.remade) == 2 and cr.unsaved
    assert cr.stopped.startswith("The carry stopped while making the mates of Housing-1 and Sprocket-2 "
                                 "again"), cr.stopped                     # ours, so SolidWorks is not the subject
    assert cr.skipped == "checking every mode with your mates on"          # what is left, not what was in hand (S6)


def test_a_component_whose_configuration_reads_back_otherwise_is_deleted_again_and_named(monkeypatch, every_gate):
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.component_configs["Sprocket-1"] = ("Z20", "Z15", ("Z15", "Z20"))
    fake.insert_config_kept = False
    cr = _build_again(fake).carry
    assert {n.item: (n.why, n.subjects) for n in cr.named} == {
        "Sprocket-1": ("configuration", ("Sprocket-1", "Z20", "Z15")),
        "Lock1": ("component not carried", ("Sprocket-1",))}
    assert cr.inserted == [] and fake.deleted == ["carried1-1"]
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.component_configs["Sprocket-1"] = ("Z20", "Z15", ("Z15", "Z20"))
    cr = _build_again(fake).carry
    assert cr.inserted == [("Sprocket-1", "carried1-1")]
    assert [a for n, a in fake.calls if n == "add_component_in"] == [("carried1", SPROCKET, "Z20")]


def test_a_remade_mate_read_back_otherwise_is_deleted_again_and_named(monkeypatch, every_gate):
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.readback_alignment = {"Lock1": 1}                     # it reads back anti-aligned, however made
    cr = _build_again(fake).carry
    assert {n.item: (n.why, n.subjects) for n in cr.named} == {"Lock1": ("differs", ("alignment",))}
    assert cr.remade == [] and fake.mate("Lock1", R2[T_ASM]) is None
    assert len([a for n, a in fake.calls if n == "remake_mate"]) == 1           # not retried: not a swap or a sense


def test_a_remade_mate_read_back_with_its_entities_swapped_is_made_once_more_reversed(monkeypatch, every_gate):
    """A distance, whose two entities are not interchangeable (a lock's are: the review's A5), read back the other way
    round is made once more with its selections reversed."""
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    gap = fake.user_mate(T_ASM, "UserDist4", kind="distance", a=("gear1-1", "plane1"), b=("Sprocket-1", "plane1"))
    gap.value = 30.0
    fake.kind_swap = {"UserDist4"}                              # SolidWorks keeps the selection the other way
    cr = _build_again(fake).carry
    assert cr.named == [] and sorted(r[0] for r in cr.remade) == ["Lock1", "UserDist4"]
    tried = [a[1] for n, a in fake.calls if n == "remake_mate" and a[2] == "UserDist4"]
    assert [tuple(t.split(":")[1] if t.startswith("ref:") else t.split(":")[0] for t in ts) for ts in tried] == [
        ("gear1", "carried1"), ("carried1", "gear1")]
    gap = fake.mate("UserDist4", R2[T_ASM])
    assert (gap.a[0], gap.b[0]) == ("gear1-1", "carried1-1")
    # A lock read back the other way round is the same lock (A5): kept at once.
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.kind_swap = {"Lock1"}
    cr = _build_again(fake).carry
    assert cr.named == [] and [a[1] for n, a in fake.calls if n == "remake_mate"] == [("gear1", "carried1")]


def test_a_lightweight_user_component_is_carried_resolved_and_its_mates_named(monkeypatch, every_gate):
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.lightweight.add("Sprocket-1")
    cr = _build_again(fake).carry
    assert cr.inserted == [("Sprocket-1", "carried1-1")]
    assert {n.item: n.why for n in cr.named} == {"Lock1": "lightweight"}
    # The audit (2026-11-17): the fake's default is SolidWorks' as the first M9 run read it, opening the part to insert
    # it resolves the old assembly's instance (lightweight is per file); the read itself resolved nothing.
    assert "Sprocket-1" not in fake.lightweight and cr.resolved_in_old == ("Sprocket-1",)
    read = fake.calls[:[n for n, *_ in fake.calls].index("new_part")]
    assert ("open_document", (SPROCKET,)) not in read                # R opens nothing of the user's
    assert ("root_component", (True,)) not in read      # never in the old assembly beside its lightweight component


# -- a gearbox with modes: states and flags per mode, a mode the old assembly has not ---------------------------------

from test_swbuild import (TC_ASM, TC_DOG, TC_LAYOUT, TC_MODES, TC_NAMES, TC_SENSES, TC_SLEEVE, _tc_gearbox,  # noqa: E402
                          _tc_modes, _tc_plan, mode_findings)  # noqa: F401
from gear_generator.gears.base import BuildPlan                                     # noqa: E402

TC2 = {TC_ASM: TC_ASM.replace("TransferCase", "TransferCase_r2"),
       TC_LAYOUT: TC_LAYOUT.replace("TransferCase", "TransferCase_r2"),
       TC_SLEEVE: TC_SLEEVE.replace(".SLDPRT", "_r2.SLDPRT"), TC_DOG: TC_DOG.replace(".SLDPRT", "_r2.SLDPRT")}
TC_GEAR_IDS = {h: n for h, n in TC_NAMES.items()}


@pytest.mark.parametrize("unsaved_read", [True, None])
def test_states_and_flags_are_set_in_every_mode_and_a_mode_the_old_assembly_has_not_takes_the_first(
        monkeypatch, every_gate, mode_findings, unsaved_read):
    # The old assembly is open with unsaved changes (the build's interference read marked it): the unshown state
    # route is used only once it is shown to read them; else each component takes the mode showing's state (D2).
    every_gate(COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED=unsaved_read)
    fake, built, _ = _tc_gearbox(FakeSolidWorks())
    assert built.ok
    fake._w9d()
    fake.read_entity_kinds = True
    fake.strict_handles = True
    fake.user_component(TC_ASM, "Sprocket-1", SPROCKET, (I9, (0.0, 0.0, 200.0)))
    fake.states_by.setdefault("N", {})["Sprocket-1"] = 0                       # suppressed in N
    # Locked to InDog, which stands still in every mode (the fake solves no lock on a show: a sleeve's slide carrying
    # a locked component along, contradiction 6, is M9's to show).
    fake.user_lock(TC_ASM, "Lock1", "gear2-1", "Sprocket-1", flags={"2H": False, "4H": False, "N": True, "4L": False})
    fake.saved[_key(SPROCKET)] = ([], [])
    fake.protected = {_key(TC_ASM), _key(SPROCKET)}
    fake.no_save_after = _key(TC2[TC_ASM])
    _isfile(monkeypatch, fake)
    recorded = tuple(m.name for m in fake.memory_mates[_key(TC_ASM)] if not m.user)
    old = swbuild.OldAssembly(TC_ASM, tuple((n, f"{h}-1") for h, n in TC_NAMES.items()), "layout-1", TC_LAYOUT,
                              recorded, ("2H", "4H", "N"))              # 4L is new in this revision, say
    bodies = (CarryBody("layout", "layout-1", "layout", False, "new", ("Rear Axis",), ("Rear Axis",)),) + tuple(
        CarryBody(n, f"{h}-1", h, False, "its Part name changed", GEAR_NAMES, GEAR_NAMES) for h, n in TC_NAMES.items())
    carry = Carry(old, bodies, TC_MODES, "2H", (34,), tuple(TC2) + tuple(TC2.values()))

    def moved(op):
        return _replace(op, path=TC2.get(op.path, op.path)) if isinstance(op, (ops.AddComponent, ops.SaveAs)) else op
    assembly = _tc_plan()
    assembly = _replace(assembly, ops=tuple(moved(op) for op in assembly.ops), path=TC2[TC_ASM])
    layout = BuildPlan("layout", "", (ops.NewPart(""), ops.Rebuild(), ops.SaveAs(TC2[TC_LAYOUT])), TC2[TC_LAYOUT])
    parts = [part_plan(path=TC2[p]) for p in (TC_SLEEVE, TC_DOG)]
    result = swbuild.build_gearbox(fake, parts, layout=layout, assembly=assembly,
                                   gears={h: n for h, n in TC_NAMES.items()} | {"layout": "layout"}, senses=TC_SENSES,
                                   modes=_tc_modes(), exists=fake.exists, before=old, carry=carry,
                                   mtime=lambda p: 1.0)
    assert result.ok, result.log_lines()
    cr = result.carry
    assert cr.stopped == "", cr.stopped
    assert cr.inserted == [("Sprocket-1", "carried1-1")]
    if unsaved_read is None:
        assert cr.work.states_route == "" and cr.work.components[0].suppressed_in is None
        assert cr.states == [("carried1-1", ())]                          # 2H's state, showing, in every mode
        assert (swbuild.STEP_CARRY_STATES, "COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED_ON_2026") in cr.gates
    else:
        assert cr.work.states_route == "route" and cr.work.components[0].suppressed_in == ("N",)
        assert cr.states == [("carried1-1", ("N",))]                      # 4L took 2H's: resolved
    assert [(r[0], set(r[2])) for r in cr.remade] == [("Lock1", {"2H", "4H", "4L"})]
    shown = [a[0] for n, a in fake.calls if n == "show_configuration"]
    assert shown[-1] == "2H"
    assert cr.moved == []


@pytest.mark.parametrize("gate", [True, None])
def test_a_user_gear_mate_on_g1s_gear_axis_is_made_again_with_its_ratio_and_sense_read_back(monkeypatch, every_gate,
                                                                                            gate):
    every_gate(CARRY_GEAR_MATE_ON_AN_APP_GEAR=gate)
    fake = _old_train()
    _isfile(monkeypatch, fake)
    gear = fake.user_mate(T_ASM, "Gear6", kind="gear", a=("Sprocket-1", "Sprocket Axis"), b=("gear1-1", "Gear Axis"))
    gear.ratio, gear.flip = (20.0, 17.0), True
    cr = _build_again(fake).carry
    if gate is None:
        assert {n.item: n.subjects for n in cr.named} == {
            "Gear6": ("gear mate on an app gear", "CARRY_GEAR_MATE_ON_AN_APP_GEAR_ON_2026", Y)}
        return
    assert cr.named == [] and {r[0] for r in cr.remade} == {"Lock1", "Gear6"}
    made = fake.mate("Gear6", R2[T_ASM])
    assert (made.a, made.b) == (("carried1-1", "Sprocket Axis"), ("gear1-1", "Gear Axis"))
    assert made.ratio == (20.0, 17.0) and made.flip is True               # read back as the old one reads


# -- the review's fixes (W9D-REVIEW-A.md), each a test that failed before ---------------------------------------------


def test_a_gear_not_free_before_the_carry_never_stops_it_after_a_tied_cluster_falls_back(monkeypatch, every_gate):
    """M2: the tie is judged only on gears free before, after every fallback too; here G1 reads fully defined from
    the start (held, as RangeBox's Ring is), and the carry goes on after the tied cluster falls back."""
    every_gate()
    fake = _two_clusters(_old_train())
    _isfile(monkeypatch, fake)
    fake.locks["Lock3"] = ("gear3", "gear4", "gear3-1", "gear4-1", "gear2", "gear2-1")
    fake.held_after_save = {"gear1-1"}             # held, as RangeBox's Ring is, once the build has checked its own
    cr = _build_again(fake).carry
    assert cr.stopped == "", cr.stopped
    assert [f.why for f in cr.fixed] == [swbuild.FELL_TIE] and cr.fixed[0].subjects[0] in ("G2", "G3", "G4"), (cr.named, cr.remade, cr.stopped)


def test_a_cluster_with_only_mates_between_app_bodies_leaves_the_new_assembly_unsaved(monkeypatch, every_gate):
    """S1: a cluster −1 mate alone, no component carried: the new assembly holds it unsaved."""
    every_gate()
    fake = _built_train()
    fake.read_entity_kinds = True
    fake.strict_handles = True
    fake.user_mate(T_ASM, "Angle9", kind="angle", a=("gear1-1", "plane1"), b=("gear4-1", "plane1"))
    fake._w9d()
    fake.protected = {_key(T_ASM)}
    cr = _build_again(fake).carry
    assert [r[0] for r in cr.remade] == ["Angle9"] and cr.inserted == [] and cr.unsaved


def test_the_carry_reads_the_new_assembly_even_when_the_build_bracket_drops_the_document(monkeypatch, every_gate):
    """S4: the Session's begin_build falls back to no build document; the carry opens the new assembly first."""
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.begin_drops_document = True
    cr = _build_again(fake).carry
    assert cr.stopped == "" and cr.inserted == [("Sprocket-1", "carried1-1")]
    names = [(n, a) for n, a in fake.calls]
    first_read = next(i for i, (n, a) in enumerate(names) if n == "component_frame" and a[0] == "gear1"
                      and i > [k for k, (m, _) in enumerate(names) if m == "save_as"][-1])
    saved = [k for k, (m, _) in enumerate(names) if m == "save_as"][-1]
    assert ("open_document", (R2[T_ASM],)) in names[saved:first_read]


def test_a_reference_found_again_as_another_kind_stops_the_carry(monkeypatch, every_gate):
    every_gate()
    fake = _old_train()
    fake.user_mate(T_ASM, "Coincident2", kind="coincident", a=("Sprocket-1", "plane1"), b=("gear1-1", "plane1"))
    _isfile(monkeypatch, fake)
    fake.resolve_other_kind = {"plane1"}
    cr = _build_again(fake).carry
    assert "found again is a face" in cr.stopped and "Coincident2" in cr.stopped


def test_a_build_that_did_not_finish_says_the_carry_was_skipped(monkeypatch, every_gate):
    """S12."""
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.fail_on = {"new_assembly": "SolidWorks would not make an assembly."}
    result = _build_again(fake)
    assert not result.ok and result.carry.skipped.startswith("carrying your work, because the")
    assert result.carry.inserted == []


def test_the_read_only_documents_own_flag_after_its_open_is_not_a_mark(monkeypatch, every_gate):
    """R.6: modified straight after OpenDoc6 (NeedsRegen, as 2026 read it) is logged, not a mark."""
    every_gate()
    fake = _closed(_old_train())
    _isfile(monkeypatch, fake)
    fake.read_only_needs_regen = True
    cr = _build_again(fake).carry
    assert cr.work.how == swbuild.OLD_READ_ONLY and cr.work.marked == [] and cr.inserted


def test_a_sub_assembly_dependency_refuses_the_not_open_read(monkeypatch, every_gate):
    every_gate()
    fake = _closed(_old_train())
    _isfile(monkeypatch, fake)
    fake.saved[_key(W + "Drive.SLDASM")] = ([], [])
    fake.dependencies_of[_key(T_ASM)] = [SPROCKET, W + "Drive.SLDASM"]
    cr = _build_again(fake).carry
    assert cr.work.how == swbuild.OLD_UNREAD and "a sub-assembly's own files are not" in cr.work.unread[0]
    fake = _closed(_old_train())
    _isfile(monkeypatch, fake)
    fake.dependencies_of[_key(T_ASM)] = [W + "Gone.SLDPRT"]          # not on disk
    assert _build_again(fake).carry.work.how == swbuild.OLD_UNREAD


@pytest.mark.parametrize("case", ["unique", "none", "several", "candidates", "seconds", "not ok"])
def test_faces_by_r3_one_walk_per_component_exactly_one_match_capped(monkeypatch, every_gate, case):
    """M1: §10's walk on the fake — one walk per component for its faces, exactly one match, the cap, the resolve's
    code; a face on a part made new is never walked unless a gear mate needs its coaxial read."""
    every_gate()
    fake = _old_train()
    fake.user_mate(T_ASM, "Coincident2", kind="coincident", a=("Sprocket-1", "face:3"), b=("gear1-1", "plane1"))
    fake.user_mate(T_ASM, "Coincident3", kind="coincident", a=("Sprocket-1", "face:4"), b=("gear1-1", "face:9"))
    _isfile(monkeypatch, fake)
    fake._w9d()
    key = (_key(SPROCKET), "face:3")
    fake.r3_filtered = {key: 250} if case == "candidates" else {}
    fake.r3_seconds = {key: 30.0} if case == "seconds" else {}
    fake.r3_matches = {key: {"none": 0, "several": 2}[case]} if case in ("none", "several") else {}
    fake.r3_resolve = {key: 2} if case == "not ok" else {}
    cr = _build_again(fake).carry
    walks = [items for _, items in fake.walks]
    # Sprocket-1's two faces, each its coincident's second entity: SolidWorks reads a coincident in tree order (the
    # audit), and G1 stands before Sprocket-1 in the tree whichever was selected first.
    assert len(walks) == 1 and [i[1:] for i in walks[0]] == [(1, "face"), (1, "face")]
    named = {n.item: (n.why, n.subjects) for n in cr.named}
    # Coincident3's other face is on G1's part, made new: never walked, named part new — its first entity in tree order
    # (the audit), so named so even where the cap took Sprocket-1's later face too.
    assert named.pop("Coincident3") == ("part new", ("G1", "its Part name changed", "face", ""))
    if case == "unique":
        assert named == {} and "Coincident2" in {r[0] for r in cr.remade}
    elif case in ("candidates", "seconds"):
        assert named == {"Coincident2": ("too long", ("face", "Sprocket-1", "Sprocket.SLDPRT", case))}
    else:
        assert named["Coincident2"][0] == "unread"


def test_bore_is_said_only_where_the_radius_is_half_the_bore(every_gate):
    every_gate()
    sun = CarryBody("Sun", "gear1-1", "gear1", False, "its Flank changed", GEAR_NAMES, GEAR_NAMES, bore_mm=10.0)
    carry = Carry(OLD, _bodies()[:2] + (sun,) + _bodies()[3:], ("H", "L"), "H")
    face = dict(coaxial=True)
    w = work([comp()], [mate("C1", 0, ent(APP, "Sun", ENTITY_FACE, radius_mm=5.0, **face),
                             ent(USER, "Sprocket-1", ENTITY_PLANE, "plane1")),
                        mate("C2", 0, ent(APP, "Sun", ENTITY_FACE, radius_mm=12.0, **face),
                             ent(USER, "Sprocket-1", ENTITY_PLANE, "plane1")),
                        mate("C3", 0, ent(APP, "Sun", ENTITY_FACE, radius_mm=5.0, coaxial=False),
                             ent(USER, "Sprocket-1", ENTITY_PLANE, "plane1"))])
    where = {n.item: n.subjects[3] for n in swbuild.plan_carry(w, carry, REVISION).named}
    assert where == {"C1": "bore", "C2": "axis", "C3": ""}


def test_a_component_suppressed_in_the_mode_showing_is_read_and_its_mate_named_not_a_stop(monkeypatch, every_gate):
    """M4: R finds it for reads (its frame read, so it is not named for its configuration), it is carried suppressed,
    and its lock, with no mode where it is resolved, is named; the carry goes on."""
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.component_states["Sprocket-1"] = 0
    cr = _build_again(fake).carry
    assert cr.work.components[0].frame is not None and cr.work.components[0].configurations == ("Default",)
    assert cr.inserted == [("Sprocket-1", "carried1-1")] and cr.stopped == ""
    assert {n.item: n.why for n in cr.named} == {"Lock1": "unread"}


def test_a_lightweight_component_is_carried_resolved_its_configurations_read_from_its_file(monkeypatch, every_gate):
    """M7 (D10): no document, so its file's configurations are read closed; carried resolved, its mates named."""
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.lightweight.add("Sprocket-1")
    cr = _build_again(fake).carry
    assert ("file_configurations", (SPROCKET,)) in fake.calls
    assert cr.inserted == [("Sprocket-1", "carried1-1")] and cr.work.components[0].active_configuration == ""


def test_the_gear_mate_read_turning_the_wrong_way_is_made_once_more_with_the_other_flip(monkeypatch, every_gate):
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    gear = fake.user_mate(T_ASM, "Gear6", kind="gear", a=("Sprocket-1", "Sprocket Axis"), b=("gear1-1", "Gear Axis"))
    gear.ratio, gear.flip = (20.0, 17.0), True
    cr = _build_again(fake).carry
    flips = [a[3] for n, a in fake.calls if n == "remake_mate" and a[2] == "Gear6"]
    assert flips == [None, True] and "Gear6" in {r[0] for r in cr.remade}
    # Wrong both ways: named, never kept.
    fake = _old_train()
    _isfile(monkeypatch, fake)
    gear = fake.user_mate(T_ASM, "Gear6", kind="gear", a=("Sprocket-1", "Sprocket Axis"), b=("gear1-1", "Gear Axis"))
    gear.ratio, gear.flip = (20.0, 17.0), True
    fake.readback_reverse = {"Gear6": 0.0}                     # read turning the other way, whatever its Flip
    cr = _build_again(fake).carry
    assert {n.item: n.why for n in cr.named} == {"Gear6": "differs"} and fake.mate("Gear6", R2[T_ASM]) is None
    # The audit: its alignment read otherwise is not a difference, AddMate5 ignoring it for a gear mate (GOTCHAS §96).
    fake = _old_train()
    _isfile(monkeypatch, fake)
    gear = fake.user_mate(T_ASM, "Gear6", kind="gear", a=("Sprocket-1", "Sprocket Axis"), b=("gear1-1", "Gear Axis"))
    gear.ratio, gear.flip = (20.0, 17.0), True
    fake.readback_alignment = {"Gear6": 1}
    cr = _build_again(fake).carry
    assert "Gear6" in {r[0] for r in cr.remade} and cr.named == [], cr.named


def test_a_gear_mate_on_a_face_read_against_its_gears_axis_is_made_on_the_gear_axis_with_the_flip_that_keeps_its_sense(
        monkeypatch, every_gate):
    """The audit (2026-11-17): EntityParams are the entities' own directions in the assembly, as SolidWorks gives
    them (W5 ring_mate_sense, W6 tier 9), not one direction for every entity. A user gear mate on G1's cylindrical face,
    whose axis SolidWorks reads against G1's Z, is made again on G1's Gear Axis (§4.3), which reads along it: with the
    old Flip it turns the other way, so it is made once more with the other Flip, and kept turning as it did."""
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    gear = fake.user_mate(T_ASM, "Gear7", kind="gear", a=("Sprocket-1", "Sprocket Axis"), b=("gear1-1", "face:root"))
    gear.ratio, gear.flip = (20.0, 17.0), False
    fake.coaxial[(_key(P17), "face:root")] = True
    fake.entity_axes = {"face:root": (0.0, 0.0, -1.0)}
    cr = _build_again(fake).carry
    old = next(m for m in cr.work.mates if m.name == "Gear7")
    assert swbuild.gear_sense(old.values, old.params) == 1                     # Reverse 0 on entities lying opposite
    flips = [a[3] for n, a in fake.calls if n == "remake_mate" and a[2] == "Gear7"]
    assert flips == [None, True] and "Gear7" in {r[0] for r in cr.remade}, (cr.named, cr.stopped)
    made = fake.mate("Gear7", R2[T_ASM])
    assert made.b == ("gear1-1", "Gear Axis") and made.flip is True
    assert swbuild.gear_sense(fake.mate_definition(next(h for h, n in fake.mate_handles.items() if n == "Gear7")).values,
                              ((0, 0, 0, 0, 0, 1.0), (0, 0, 0, 0, 0, 1.0))) == 1


def _tc_again(monkeypatch, flags, tweak=lambda fake: None, anchor="gear2-1"):
    """The TransferCase built with modes, Sprocket-1 locked to ``anchor`` with its lock's ``flags`` per mode, built
    again with its carry; ``tweak`` doctors the fake before the build again."""
    fake, built, _ = _tc_gearbox(FakeSolidWorks())
    assert built.ok
    fake._w9d()
    fake.read_entity_kinds = True
    fake.strict_handles = True
    fake.user_component(TC_ASM, "Sprocket-1", SPROCKET, (I9, (0.0, 0.0, 200.0)))
    fake.user_lock(TC_ASM, "Lock1", anchor, "Sprocket-1", flags=flags)
    fake.saved[_key(SPROCKET)] = ([], [])
    fake.protected = {_key(TC_ASM), _key(SPROCKET)}
    fake.no_save_after = _key(TC2[TC_ASM])
    _isfile(monkeypatch, fake)
    recorded = tuple(m.name for m in fake.memory_mates[_key(TC_ASM)] if not m.user)
    old = swbuild.OldAssembly(TC_ASM, tuple((n, f"{h}-1") for h, n in TC_NAMES.items()), "layout-1", TC_LAYOUT,
                              recorded, TC_MODES)
    bodies = (CarryBody("layout", "layout-1", "layout", False, "new", ("Rear Axis",), ("Rear Axis",)),) + tuple(
        CarryBody(n, f"{h}-1", h, False, "its Part name changed", GEAR_NAMES, GEAR_NAMES) for h, n in TC_NAMES.items())
    carry = Carry(old, bodies, TC_MODES, "2H", (34,), tuple(TC2) + tuple(TC2.values()))

    def moved(op):
        return _replace(op, path=TC2.get(op.path, op.path)) if isinstance(op, (ops.AddComponent, ops.SaveAs)) else op
    assembly = _tc_plan()
    assembly = _replace(assembly, ops=tuple(moved(op) for op in assembly.ops), path=TC2[TC_ASM])
    layout = BuildPlan("layout", "", (ops.NewPart(""), ops.Rebuild(), ops.SaveAs(TC2[TC_LAYOUT])), TC2[TC_LAYOUT])
    parts = [part_plan(path=TC2[p]) for p in (TC_SLEEVE, TC_DOG)]
    tweak(fake)
    result = swbuild.build_gearbox(fake, parts, layout=layout, assembly=assembly,
                                   gears={h: n for h, n in TC_NAMES.items()} | {"layout": "layout"}, senses=TC_SENSES,
                                   modes=_tc_modes(), exists=fake.exists, before=old, carry=carry,
                                   mtime=lambda p: 1.0)
    assert result.ok, result.log_lines()
    return result.carry, fake


ALL_ON = {"2H": False, "4H": False, "N": False, "4L": False}


def test_a_remade_mate_in_error_in_one_mode_only_falls_its_cluster_back_there(monkeypatch, every_gate, mode_findings):
    """M3: the post-check reads each remade mate's code in every mode where it is on."""
    every_gate()

    def tweak(fake):
        fake.remake_codes_in = {"Lock1": {"4L": (46, True)}}
    cr, fake = _tc_again(monkeypatch, ALL_ON, tweak)
    assert [(f.why, f.subjects) for f in cr.fixed] == [(swbuild.FELL_NEW_ERROR, ("Lock1", "46", "0", "4L"))]
    assert cr.remade == [] and cr.stopped == ""


def test_a_cluster_tying_in_some_modes_only_falls_back_once_in_the_first_of_them(monkeypatch, every_gate,
                                                                                 mode_findings):
    """S3, §6: flags that differ by mode are judged in each mode where they differ; the cluster falls back once."""
    every_gate()

    def tweak(fake):
        fake.locks["Lock1"] = ("gear2", "gear2-1")                 # on, it ties InDog's train
    cr, fake = _tc_again(monkeypatch, {"2H": True, "4H": True, "N": False, "4L": False}, tweak)
    assert [(f.why, f.subjects[1]) for f in cr.fixed] == [(swbuild.FELL_TIE, "N")], cr.stopped
    assert cr.stopped == ""


def test_a_carried_component_off_its_pose_in_a_mode_is_said_moved_in_its_anchors_frame(monkeypatch, every_gate,
                                                                                    mode_findings):
    every_gate()

    def tweak(fake):
        fake.drift_in = {"N": {"carried1-1": (0.0, 0.0, 2.0)}}
    cr, fake = _tc_again(monkeypatch, ALL_ON, tweak)
    assert cr.moved == [("carried1-1", "N", pytest.approx(2.0))]


# -- the re-check of the fix round (W9D-REVIEW-A.md, fd599f8), each a test that failed before ------------------------


def test_while_nothing_can_be_carried_there_is_no_walk_and_no_not_open_read(monkeypatch, every_gate):
    """N3, ruled: with CARRY_INSERTS None, no r3 walk and a closed old assembly never opened; named by that finding."""
    every_gate(CARRY_INSERTS=None)
    fake = _old_train()
    fake.user_mate(T_ASM, "Coincident2", kind="coincident", a=("Sprocket-1", "face:3"), b=("gear1-1", "plane1"))
    _isfile(monkeypatch, fake)
    cr = _build_again(fake).carry
    assert "entity_references" not in [n for n, *_ in fake.calls] and cr.work.how == swbuild.OLD_OPEN
    assert {n.item: n.subjects for n in cr.named}["Sprocket-1"] == ("insert", "CARRY_INSERTS_ON_2026", Y)
    fake = _closed(_old_train())
    _isfile(monkeypatch, fake)
    cr = _build_again(fake).carry
    assert "open_read_only" not in [n for n, *_ in fake.calls] and cr.work.how == swbuild.OLD_UNREAD
    assert "findings.CARRY_INSERTS_ON_2026" in cr.work.unread[0]


def test_a_cluster_on_in_every_mode_is_not_blamed_for_another_clusters_tie(monkeypatch, every_gate, mode_findings):
    """N1 (the re-check's reproduction): cluster A (Sprocket-2 locked to InDog, on everywhere) is judged clean; cluster
    B (Lock1, on in N and 4L only) ties InDog there. B falls back in N, A is never fallen back, the carry goes on."""
    every_gate()

    def tweak(fake):
        fake.user_component(TC_ASM, "Sprocket-2", SPROCKET, (I9, (0.0, 0.0, 210.0)))
        fake.user_lock(TC_ASM, "Lock0", "gear2-1", "Sprocket-2", flags=ALL_ON)
        _first_in_tree(fake, "Lock0")                  # the innocent cluster first, as the reproduction has it
        fake.locks["Lock1"] = ("gear2", "gear2-1")
    cr, fake = _tc_again(monkeypatch, {"2H": True, "4H": True, "N": False, "4L": False}, tweak)
    assert [(f.deleted, f.why, f.subjects) for f in cr.fixed] == [(("Lock1",), swbuild.FELL_TIE, ("InDog", "N"))]
    assert cr.stopped == "" and "Lock0" in {r[0] for r in cr.remade}


def test_a_mode_where_a_clusters_component_is_suppressed_is_not_judged_and_is_said_as_a_fact(
        monkeypatch, every_gate, mode_findings):
    """N2: Sprocket-1 suppressed in N; Lock1 reads error 46 there (made up): not judged, logged."""
    every_gate()

    def tweak(fake):
        fake.states_by.setdefault("N", {})["Sprocket-1"] = 0
        fake.remake_codes_in = {"Lock1": {"N": (46, True)}}
    cr, fake = _tc_again(monkeypatch, ALL_ON, tweak)
    assert cr.fixed == [] and cr.stopped == "" and [r[0] for r in cr.remade] == ["Lock1"]
    assert any(f.startswith("Lock1 in N, where Sprocket-1 is suppressed: on, code 46; not judged") for f in cr.facts)
    assert any(line.startswith("fact    Lock1 in N, where") for line in cr.log_lines())


def test_an_app_mate_put_in_error_in_one_mode_falls_the_cluster_back_there(monkeypatch, every_gate, mode_findings):
    """M3's remaining part: the app's own mates' codes are read in every mode after the carry."""
    every_gate()

    def tweak(fake):
        fake.remake_codes_in = {"Lock1": {}}
        original = fake.mate_states

        def states(*, others=None):
            out = original(others=others)
            broken = fake.config == "4L" and any(m.name == "Lock1" and not m.user and not m.suppressed
                                                for m in fake.mates)
            return [swcom.MateState(x.name, 46, True, x.suppressed) if broken and x.name == "InDog on Rear Axis"
                    else x for x in out]
        monkeypatch.setattr(fake, "mate_states", states)
    cr, fake = _tc_again(monkeypatch, ALL_ON, tweak)
    assert [(f.why, f.subjects) for f in cr.fixed] == [(swbuild.FELL_NEW_ERROR, ("InDog on Rear Axis", "46", "0",
                                                                                   "4L"))]
    assert cr.stopped == ""


def test_the_files_changed_after_the_carry_have_a_field_and_the_sentence_stays(monkeypatch, every_gate):
    """Item 7."""
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    times = iter([1.0, 1.0] + [2.0] * 10)
    cr = _build_again(fake, mtime=lambda p: next(times)).carry
    assert cr.changed_files == ["T.SLDASM", "Sprocket.SLDPRT"]
    assert "changed on disk while Build again" in cr.stopped


def test_a_stop_in_another_mode_shows_the_first_again_and_a_com_failure_stops(monkeypatch, every_gate, mode_findings):
    """Item 8: a lost connection in a remake is a stop, not a refusal; the first mode is shown again."""
    every_gate()

    def tweak(fake):
        # Suppressed in N only (in the mode showing its entities would read unread, as SolidWorks reads them).
        fake.states_by.setdefault("N", {})["Sprocket-1"] = 0
        error = swcom.ComError("AddMate5", Exception(-2147023174, "The RPC server is unavailable.", None, None))
        fake.raises["remake_mate"] = (1, error)
    cr, fake = _tc_again(monkeypatch, ALL_ON, tweak)
    assert cr.stopped.startswith("SolidWorks stopped the carry while making the mates of Sprocket-1 again")
    assert fake.config == "2H" and cr.named == []


def test_a_retry_whose_delete_raises_says_the_mate_was_left_in_place(monkeypatch, every_gate):
    """Item 8: never silent."""
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.readback_alignment = {"Lock1": 1}
    fake.fail_on = {"delete_mate": "SolidWorks would not delete the mate Lock1."}
    cr = _build_again(fake).carry
    assert {n.item: n.subjects for n in cr.named} == {"Lock1": ("left", "Lock1")}
    assert cr.facts == ["Lock1 is left in the new assembly as Lock1: SolidWorks would not delete the mate Lock1."]


def test_each_walk_is_logged_with_its_counts_seconds_and_cap(monkeypatch, every_gate):
    """Item 6: the first measurement of the route as written comes from these lines."""
    every_gate()
    fake = _old_train()
    fake.user_mate(T_ASM, "Coincident2", kind="coincident", a=("Sprocket-1", "face:3"), b=("gear1-1", "plane1"))
    _isfile(monkeypatch, fake)
    cr = _build_again(fake).carry
    (walk,) = cr.work.walks
    assert walk.startswith("walk Sprocket-1: face of 2: 2 after the prefilter") and "cap not reached" in walk
    assert f"fact    {walk}" in cr.log_lines()


# -- the demonstration review's third round (W9D-DEMONSTRATION-REVIEW.md, 6f67791) -----------------------------------


def _first_in_tree(fake, name):
    mates = fake.memory_mates[_key(TC_ASM)]
    mates.insert(0, mates.pop(next(i for i, m in enumerate(mates) if m.name == name)))


def test_an_app_mate_in_error_blames_only_a_cluster_on_its_bodies(monkeypatch, every_gate, mode_findings):
    """Item 2: InDog's axis mate errs in 4L once Lock1 (Sprocket-1 to InDog) is on; Lock0 (Sprocket-2 to LoDog), first
    in the tree, is not on InDog's bodies and is not blamed."""
    every_gate()

    def tweak(fake):
        fake.user_component(TC_ASM, "Sprocket-2", SPROCKET, (I9, (0.0, 0.0, 210.0)))
        fake.user_lock(TC_ASM, "Lock0", "gear6-1", "Sprocket-2", flags=ALL_ON)
        _first_in_tree(fake, "Lock0")
        original = fake.mate_states

        def states(*, others=None):
            out = original(others=others)
            broken = fake.config == "4L" and any(m.name == "Lock1" and not m.user and not m.suppressed
                                                for m in fake.mates)
            return [swcom.MateState(x.name, 46, True, x.suppressed) if broken and x.name == "InDog on Rear Axis"
                    else x for x in out]
        monkeypatch.setattr(fake, "mate_states", states)
    cr, fake = _tc_again(monkeypatch, ALL_ON, tweak)
    assert [(f.deleted, f.why) for f in cr.fixed] == [(("Lock1",), swbuild.FELL_NEW_ERROR)], cr.fixed
    assert "Lock0" in {r[0] for r in cr.remade} and cr.stopped == ""


@pytest.mark.parametrize("stored, beside, refused", [
    ("D:\\Elsewhere\\Sprocket.SLDPRT", True, True),     # copied: a same-named file sits beside the assembly
    (SPROCKET, True, False),                                # stored in the assembly's own folder
    ("D:\\Lib\\Bolt.SLDPRT", False, False),               # legitimately elsewhere, nothing beside
])
def test_a_dependency_stored_elsewhere_with_a_same_named_file_beside_refuses_the_not_open_read(
        monkeypatch, every_gate, stored, beside, refused):
    """Item 3, ruled: SolidWorks loads the file beside the assembly first, so the stored path's version is not it."""
    every_gate()
    fake = _closed(_old_train())
    _isfile(monkeypatch, fake)
    fake.saved[_key(stored)] = ([], [])
    if not beside:
        fake.saved.pop(_key(W + _file_name(stored)), None)
    fake.dependencies_of[_key(T_ASM)] = [stored]
    cr = _build_again(fake).carry
    if refused:
        assert cr.work.how == swbuild.OLD_UNREAD and "Sprocket.SLDPRT is stored in another folder" in cr.work.unread[0]
        assert "Elsewhere" not in cr.work.unread[0]                           # base file names only
    else:
        assert cr.work.how == swbuild.OLD_READ_ONLY, cr.work.unread


def _file_name(path):
    return path.replace("/", "\\").rsplit("\\", 1)[-1]


def test_a_fixed_component_stands_by_its_world_frame_with_no_app_anchor(every_gate):
    """Item 4, ruled (D20): a fixed housing in a cluster locked to a turned Sun keeps its world frame; the floating
    sprocket of the same cluster is placed against Sun."""
    every_gate()
    c, s_ = math.cos(math.radians(37.0)), math.sin(math.radians(37.0))
    old_sun = ((c, -s_, 0.0, s_, c, 0.0, 0.0, 0.0, 1.0), (0.0, 0.0, 10.0))
    housing = comp("Housing-1", HOUSING, frame=(I9, (0.0, 0.0, -40.0)), fixed=True)
    w = work([comp(), housing], [lock("Lock1", SUN_WHOLE, ent(USER, "Sprocket-1", ENTITY_WHOLE)),
                                 lock("Lock2", ent(USER, "Housing-1", ENTITY_WHOLE), ent(USER, "Sprocket-1",
                                                                                          ENTITY_WHOLE))],
             app_frames=(("Sun", old_sun),))
    plan = swbuild.plan_carry(w, _carry(), REVISION, new_frames={"Sun": (I9, (0.0, 0.0, 10.0))})
    items = {i.component.name: i for i in plan.components}
    assert items["Housing-1"].anchor == "" and items["Housing-1"].frame == housing.frame
    assert items["Sprocket-1"].anchor == "Sun" and items["Sprocket-1"].cluster == items["Housing-1"].cluster


def test_a_fixed_component_reads_world_in_the_results_anchors(monkeypatch, every_gate):
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.fixed.add("Sprocket-1")
    cr = _build_again(fake).carry
    assert cr.anchors == [("carried1-1", "")]


def test_the_files_after_the_carry_not_read_is_its_own_field_not_a_stop(monkeypatch, every_gate):
    """Item 5."""
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.raises["save_flags"] = (3, SolidWorksError("SolidWorks stopped answering."))   # R reads it twice first
    cr = _build_again(fake).carry
    assert cr.stopped == "" and cr.after_unread.startswith("Whether your files changed could not be read")


@pytest.mark.parametrize("resolves", [True, False])
def test_a_lightweight_instance_resolved_in_the_old_assembly_by_the_insert_is_said(monkeypatch, every_gate, resolves):
    """Item 6 (D10): read before and after the parts are opened; a fact and a field, never a stop, never set back."""
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.lightweight.add("Sprocket-1")
    fake.open_resolves_lightweight = resolves
    cr = _build_again(fake).carry
    assert cr.inserted == [("Sprocket-1", "carried1-1")] and cr.stopped == ""
    assert cr.resolved_in_old == (("Sprocket-1",) if resolves else ())
    assert any("Sprocket-1 in T.SLDASM was lightweight and read resolved" in f for f in cr.facts) == resolves


# -- the fourth round: the first M9 run on SolidWorks 2026 (probe/results/w9d-demo-sw2026-20261117-2-…) --------------


def test_a_gear_new_in_the_revision_is_found_again_before_its_tie_is_read(monkeypatch, every_gate):
    """Fault 2: the build's handles end with its bracket; G4 is new here (no CarryBody), and the carry reads every
    mated gear free before the mates; it is found again by its Name2 first, so the carry goes on."""
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    carry = _t_carry()
    carry = _replace(carry, bodies=tuple(b for b in carry.bodies if b.old != "G4"))
    cr = _build_again(fake, carry).carry
    assert cr.stopped == "" and [r[0] for r in cr.remade] == ["Lock1"]


def test_a_mate_on_a_lightweight_components_feature_is_named_lightweight_and_never_read(monkeypatch, every_gate):
    """Fault 3 (UserAxisLight): no part document, so nothing of it is read; named WHY_LIGHTWEIGHT (D10), and no
    sentence carries Python text."""
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.user_mate(T_ASM, "UserAxisLight", kind="coincident", a=("Sprocket-1", "Sprocket Axis"),
                   b=("gear1-1", "Gear Axis"))
    fake.lightweight.add("Sprocket-1")
    cr = _build_again(fake).carry
    named = {n.item: n for n in cr.named}
    assert named["UserAxisLight"].why == swbuild.WHY_LIGHTWEIGHT
    assert not [a for n, a in fake.calls if n == "entity_reference"]
    assert not any("object" in str(n.subjects) for n in cr.named)


def test_a_fault_of_ours_never_reaches_a_sentence_as_python_text(monkeypatch, every_gate):
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.raises["remake_mate"] = (1, TypeError("'method' object is not iterable"))
    cr = _build_again(fake).carry
    assert cr.stopped.startswith("The carry stopped while")                       # S1: not "SolidWorks stopped"
    assert cr.stopped.endswith("a fault in Gear Generator, not in SolidWorks.") and "method" not in cr.stopped
    assert any("TypeError" in f for f in cr.facts)


# -- the fifth round (W9D-REVIEW-A.md's addendum eb66f22, W9D-DEMONSTRATION-REVIEW.md's e2207d9) --------------------


def test_a_mates_flag_read_otherwise_where_its_component_is_suppressed_is_a_fact_not_a_stop(
        monkeypatch, every_gate, mode_findings):
    """M2 (§3 C.6.1): Sprocket-1 suppressed in N; its Lock1 set on there reads suppressed (made up: unmeasured)."""
    every_gate()

    def tweak(fake):
        fake.states_by.setdefault("N", {})["Sprocket-1"] = 0
        original = fake.mate_suppression

        def reads(handle, configurations):
            out = original(handle, configurations)
            if fake.mate_handles.get(handle) == "Lock1" and fake.saved_after:
                out = {k: (True if k == "N" else v) for k, v in out.items()}
            return out
        monkeypatch.setattr(fake, "mate_suppression", reads)
    cr, fake = _tc_again(monkeypatch, ALL_ON, tweak)
    assert cr.stopped == "" and [r[0] for r in cr.remade] == ["Lock1"]
    assert any("Lock1 reads suppressed in N, where a component it joins is suppressed" in f for f in cr.facts)



def test_a_fault_in_a_features_reference_read_reaches_the_logs_facts(monkeypatch, every_gate):
    """S2's remainder: the Session keeps the Python text of a fault of ours in reference_faults; it reaches the log."""
    every_gate()
    fake = _old_train()
    fake.user_mate(T_ASM, "Coincident2", kind="coincident", a=("Sprocket-1", "plane1"), b=("gear1-1", "plane1"))
    _isfile(monkeypatch, fake)

    def reading(mate_handle, index):
        fake.reference_faults = getattr(fake, "reference_faults", []) + ["AttributeError: no FeatureByName"]
        return "plane", "", None, "its reference could not be read (a fault in Gear Generator)"
    monkeypatch.setattr(fake, "entity_reference", reading)
    cr = _build_again(fake).carry
    assert "fact    reference read fault: AttributeError: no FeatureByName" in cr.log_lines()
    assert {n.item: n.subjects for n in cr.named}["Coincident2"] == (
        "its reference could not be read (a fault in Gear Generator)",)



# -- the sixth round (W9D-REVIEW-A.md 2ad7ad8) --------------------------------------------------------------------


def test_a_mate_on_a_component_suppressed_in_the_mode_showing_hands_its_cause_as_structure(monkeypatch, every_gate):
    """A1: SolidWorks reads such an entity's kind unread; the cause goes out as (clause, "suppressed", component,
    mode)."""
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.user_mate(T_ASM, "UserAxis9", kind="coincident", a=("Sprocket-1", "Sprocket Axis"),
                   b=("gear1-1", "Gear Axis"))
    fake.component_states["Sprocket-1"] = 0
    cr = _build_again(fake).carry
    named = {n.item: n for n in cr.named}
    assert named["UserAxis9"].why == swbuild.WHY_UNREAD
    assert named["UserAxis9"].subjects[1:] == (swbuild.CAUSE_SUPPRESSED, "Sprocket-1", "")
    # The second entity: a coincident reads in tree order (the audit), G1 before Sprocket-1.
    entity = next(m for m in cr.work.mates if m.name == "UserAxis9").entities[1]
    assert (entity.kind, entity.cause, entity.cause_parts) == ("unread", "suppressed", ("Sprocket-1", ""))


def test_the_assemblys_plane_beside_a_lightweight_component_hands_its_cause_as_structure(monkeypatch, every_gate):
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.assembly_entity = "root"                    # 2026: the root names the assembly's own entity
    fake.user_component(T_ASM, "Housing-1", HOUSING, (I9, (0.0, 0.0, -40.0)), fixed=True)
    fake.user_mate(T_ASM, "UserAsm6", kind="distance", a=("Housing-1", "plane1"), b=("asm", "plane1"))
    fake.lightweight.add("Sprocket-1")                       # another component, lightweight
    cr = _build_again(fake).carry
    named = {n.item: n for n in cr.named}
    assert named["UserAsm6"].subjects[1:] == (swbuild.CAUSE_BESIDE_LIGHTWEIGHT, "Sprocket-1")


def test_a_same_error_mate_that_ties_no_gear_is_carried(monkeypatch, every_gate):
    """A2: Lock2 holds Chain-1 to a fixed Housing-1 and read 46 before; made again it reads 46: carried as it was."""
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.user_component(T_ASM, "Housing-1", HOUSING, (I9, (0.0, 0.0, -40.0)), fixed=True)
    fake.user_component(T_ASM, "Chain-1", SPROCKET, (I9, (0.0, 0.0, 60.0)))
    fake.user_lock(T_ASM, "Lock2", "Housing-1", "Chain-1")
    fake.mate_codes["Lock2"] = (46, True)
    fake.remake_codes["Lock2"] = (46, True)
    cr = _build_again(fake).carry
    assert cr.fixed == [] and cr.same_error == [("Lock2", 46)] and "Lock2" in {r[0] for r in cr.remade}



# -- the seventh round (W9D-REVIEW-A.md 0d45c9a) ------------------------------------------------------------------


@pytest.mark.parametrize("modes", [False, True])
def test_a_mate_to_the_assemblys_own_plane_is_made_again_and_kept(monkeypatch, every_gate, mode_findings, modes):
    """N1: SolidWorks names the assembly's own entity by its root's Name2 (the fake's default now); the remade mate
    reads back equal and is kept, in the first mode and per mode."""
    every_gate()
    if modes:
        def tweak(fake):
            fake.user_mate(TC_ASM, "UserAsm6", kind="distance", a=("Sprocket-1", "plane1"), b=("asm", "plane1"))
            fake.memory_mates[_key(TC_ASM)][-1].flags = dict(ALL_ON)
        cr, fake = _tc_again(monkeypatch, ALL_ON, tweak)
    else:
        fake = _old_train()
        _isfile(monkeypatch, fake)
        fake.user_mate(T_ASM, "UserAsm6", kind="distance", a=("Sprocket-1", "plane1"), b=("asm", "plane1"))
        cr = _build_again(fake).carry
    assert "UserAsm6" in {r[0] for r in cr.remade}, cr.named
    assert "UserAsm6" not in {n.item for n in cr.named}


def test_a_carry_that_stops_in_a_later_mode_leaves_the_first_mode_showing(monkeypatch, every_gate, mode_findings):
    """S5: the finally's show of the first mode, pinned."""
    every_gate()

    def tweak(fake):
        original = fake.mate_states

        def states(*, others=None):
            if fake.config == "N" and getattr(fake, "saved_after", False) and fake.mate("Lock1") is not None \
                    and not fake.mate("Lock1").user:
                raise RuntimeError("SolidWorks stopped answering.")
            return original(others=others)
        monkeypatch.setattr(fake, "mate_states", states)
    cr, fake = _tc_again(monkeypatch, ALL_ON, tweak)
    assert cr.stopped and fake.config == "2H"


def test_an_entity_of_a_type_the_app_does_not_take_says_so_as_structure(monkeypatch, every_gate):
    """S6: ReferenceType2 answered (a sketch point, 11 say); the cause is the type, not SolidWorks declining."""
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.user_mate(T_ASM, "Coincident8", kind="coincident", a=("Sprocket-1", "Point1"), b=("gear1-1", "plane1"))
    original = fake.mate_definition

    def definition(handle):
        d = original(handle)
        if d.name != "Coincident8":
            return d
        first = swcom.MateEntityRead(d.entities[0].component, 11, "unread", "", d.entities[0].params)
        return _replace(d, entities=(first,) + d.entities[1:])
    monkeypatch.setattr(fake, "mate_definition", definition)
    cr = _build_again(fake).carry
    named = {n.item: n.subjects for n in cr.named}
    assert named["Coincident8"][1:] == (swbuild.CAUSE_TYPE_NOT_TAKEN, "11")


# -- the audit of the fake's defaults against SolidWorks as measured (W9D-PACKAGE-A.md, 2026-11-17) ------------------


@pytest.mark.parametrize("type_name, values, word", [
    # As SolidWorks 2026 read them (W9c S5 (a); the first M9 run, w9d-demo-sw2026-…-2 :604-605, :634; W9c m1):
    ("MateDistanceDim", (("Distance", 0.09), ("MaximumDistance", 0.09), ("MinimumDistance", 0.09)), "distance"),
    ("MatePlanarAngleDim", (("Angle", 1.5708), ("MaximumAngle", 1.5708), ("MinimumAngle", 1.5708)), "angle"),
    ("MateLimitDistanceDim", (("Distance", 0.02), ("MaximumDistance", 0.03), ("MinimumDistance", 0.01)),
     "limit distance"),
    ("MateLimitPlanarAngleDim", (("Angle", 0.17), ("MaximumAngle", 0.70), ("MinimumAngle", 0.0)), "limit angle"),
    # The type name not read (a recorded inventory, say): the range decides, and only a range that is one.
    ("", (("Distance", 0.09), ("MaximumDistance", 0.09), ("MinimumDistance", 0.09)), "distance"),
    ("", (("Distance", 0.02), ("MaximumDistance", 0.03), ("MinimumDistance", 0.01)), "limit distance"),
    ("", (("MaximumDistance", 0.02), ("MinimumDistance", 0.01)), "limit distance"),
    ("", (), "distance"),
])
def test_a_plain_distance_or_angle_reading_its_range_is_no_limit_mate(type_name, values, word):
    """The audit: SolidWorks reads a plain distance's or angle's range too, each end its value, so the range alone
    made every one a limit mate (named ``limit distance``, gated by a word M9 might not set)."""
    kind = 6 if "Angle" in type_name or any(k == "Angle" for k, _ in values) else 5
    m = mate("M", kind, ent(USER, "Sprocket-1", ENTITY_PLANE, "plane1"), ent(APP, "Sun", ENTITY_PLANE, "plane1"),
             values=values, type_name=type_name)
    assert swbuild.carry_kind(m) == word


def test_a_plain_distance_as_solidworks_reads_it_is_made_again_under_the_distance_word(monkeypatch, every_gate):
    """The audit: the fake now reads a plain distance as SolidWorks does (its range, each end its value, and
    MateDistanceDim); it is made again while CARRY_REMAKE_KINDS holds "distance" and not "limit distance"."""
    every_gate(CARRY_REMAKE_KINDS=("distance", "lock"))
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.user_mate(T_ASM, "UserDist4", kind="distance", a=("Sprocket-1", "plane1"), b=("gear1-1", "plane1"))
    fake.memory_mates[_key(T_ASM)][-1].value = 90.0
    cr = _build_again(fake).carry
    old = next(m for m in cr.work.mates if m.name == "UserDist4")
    assert dict(old.values)["MaximumDistance"] == dict(old.values)["Distance"] and old.type_name == "MateDistanceDim"
    assert "UserDist4" in {r[0] for r in cr.remade} and cr.named == [], cr.named
    assert fake.mate("UserDist4", R2[T_ASM]).kind == "distance"


def test_a_gear_mate_read_back_swapped_is_made_once_more_with_its_counts_swapped_too(monkeypatch, every_gate):
    """The audit: AddMate5's numerator goes with the first selection, so the reversed retry reverses the counts with
    the selections; else the gear mate would come back at the inverse ratio (and kept, where SolidWorks reads the
    ratio by selection)."""
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    gear = fake.user_mate(T_ASM, "Gear6", kind="gear", a=("Sprocket-1", "Sprocket Axis"), b=("gear1-1", "Gear Axis"))
    gear.ratio, gear.flip = (20.0, 17.0), False
    fake.kind_swap = {"Gear6"}                                  # SolidWorks keeps the selection the other way
    cr = _build_again(fake).carry
    assert "Gear6" in {r[0] for r in cr.remade}, cr.named
    made = fake.mate("Gear6", R2[T_ASM])
    assert (made.a, made.b) == (("carried1-1", "Sprocket Axis"), ("gear1-1", "Gear Axis"))
    assert fake.definition("Gear6", R2[T_ASM]) == fake.definition("Gear6", T_ASM)   # each count with its own gear


def test_a_plane_on_a_lightweight_component_is_unread_for_no_document_not_for_its_type(monkeypatch, every_gate):
    """The audit: ReferenceType2 answers a plane on a lightweight component, but its tree order needs the part's
    document (none), so its kind reads unread; that is not "a kind of entity Gear Generator does not take" (S6), and
    the mate is named lightweight (D10)."""
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.user_mate(T_ASM, "UserDist4", kind="distance", a=("Sprocket-1", "plane1"), b=("gear1-1", "plane1"))
    fake.lightweight.add("Sprocket-1")
    cr = _build_again(fake).carry
    entity = next(m for m in cr.work.mates if m.name == "UserDist4").entities[0]
    assert (entity.kind, entity.select_type) == (ENTITY_UNREAD, swbuild.SEL_DATUMPLANES)
    assert entity.cause != swbuild.CAUSE_TYPE_NOT_TAKEN
    assert {n.item: n.why for n in cr.named}["UserDist4"] == "lightweight"


def test_the_closed_assemblys_dependencies_are_every_file_it_holds_as_solidworks_lists_them(monkeypatch, every_gate):
    """The audit: the fake's GetDocumentDependencies2 lists what the closed assembly holds (the app's parts, the
    layout, the user's parts), as DEPENDENCIES_READ read nine; R.2 judges each, and reads the old assembly."""
    every_gate()
    fake = _closed(_old_train())
    _isfile(monkeypatch, fake)
    listed = {_key(p) for p in fake.dependencies(T_ASM)}
    assert {_key(P17), _key(P68), _key(P51), _key(T_LAYOUT), _key(SPROCKET)} <= listed
    cr = _build_again(fake).carry
    assert cr.work.how == swbuild.OLD_READ_ONLY, cr.work.unread
    fake = _closed(_old_train())
    _isfile(monkeypatch, fake)
    fake.file_versions[_key(P68)] = 32                      # one app part last saved by 2024: not read
    cr = _build_again(fake).carry
    assert cr.work.how == swbuild.OLD_UNREAD and "last saved by this SolidWorks" in cr.work.unread[0]


@pytest.mark.parametrize("listed", [("Chain-1", "Chain-2"), ("Chain-2", "Chain-1")])
def test_a_coincident_between_two_carried_components_inserted_in_another_order_is_kept(monkeypatch, every_gate,
                                                                                      listed):
    """The audit: SolidWorks reads a coincident's entities in its components' tree order, and R inserts the carried
    components in GetComponents' order, which is not the tree's (the first M9 run listed Chain-2 before Chain-1). So a
    coincident between two of them can read back the other way round however it is selected; it is the same mate (a
    coincident, concentric, parallel, perpendicular or tangent mate is one whichever entity comes first), kept."""
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.user_component(T_ASM, "Chain-1", SPROCKET, (I9, (0.0, 0.0, 60.0)))
    fake.user_component(T_ASM, "Chain-2", SPROCKET, (I9, (0.0, 0.0, 60.0)))
    fake.user_lock(T_ASM, "Lock2", "gear1-1", "Chain-1")
    fake.user_mate(T_ASM, "UserFaceCoin", kind="coincident", a=("Chain-2", "plane1"), b=("Chain-1", "plane1"))
    fake.listing_order = list(listed)
    cr = _build_again(fake).carry
    old = next(m for m in cr.work.mates if m.name == "UserFaceCoin")
    assert [e.owner for e in old.entities] == ["Chain-1", "Chain-2"]           # tree order, not the selection's
    assert cr.stopped == "" and "UserFaceCoin" in {r[0] for r in cr.remade}, cr.named
    assert [a[2] for n, a in fake.calls if n == "remake_mate"].count("UserFaceCoin") == 1    # made once, no retry


# -- the coordinator's rulings on the audit's §3 (2026-11-17) --------------------------------------------------------


def _distance_case(monkeypatch, every_gate, flipped_read=False, reads_back=None):
    """A user distance on the side its FlipDimension 1 says, IMate2.Flipped read False (as every distance read so)."""
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    gap = fake.user_mate(T_ASM, "UserDist4", kind="distance", a=("Sprocket-1", "plane1"), b=("gear1-1", "plane1"))
    gap.value, gap.flip = 90.0, True
    original = fake.mate_definition

    def definition(handle):
        d = original(handle)
        if d.name != "UserDist4":
            return d
        if fake.mate(d.name) is gap:
            return _replace(d, flipped=flipped_read)
        if reads_back is not None:
            return _replace(d, values=tuple((k, reads_back if k == "FlipDimension" else v) for k, v in d.values))
        return d
    monkeypatch.setattr(fake, "mate_definition", definition)
    return _build_again(fake).carry, fake


def test_a_distance_is_made_again_on_the_side_its_flip_dimension_says_and_its_read_back_said(monkeypatch, every_gate):
    """Ruled: its FlipDimension goes to AddMate5 as the Flip, not IMate2.Flipped; the fake puts the component on the
    other side for the other Flip, so the pose check would say it moved."""
    cr, fake = _distance_case(monkeypatch, every_gate)
    flips = [a[3] for n, a in fake.calls if n == "remake_mate" and a[2] == "UserDist4"]
    assert flips == [True] and "UserDist4" in {r[0] for r in cr.remade} and cr.moved == [], (cr.named, cr.moved)
    assert "UserDist4 made again with Flip True for its FlipDimension 1; it reads FlipDimension 1" in cr.facts


def test_a_distance_reading_another_flip_dimension_back_is_kept_and_said(monkeypatch, every_gate):
    """Ruled: how a FlipDimension reads back was never measured, so it is said, never a reason to delete."""
    cr, fake = _distance_case(monkeypatch, every_gate, reads_back=0.0)
    assert "UserDist4" in {r[0] for r in cr.remade} and cr.named == []
    assert "UserDist4 made again with Flip True for its FlipDimension 1; it reads FlipDimension 0" in cr.facts


def test_a_name_solidworks_will_not_give_keeps_the_mate_under_its_own_and_says_so(monkeypatch, every_gate):
    """Ruled: the mate is good, only its name is not the old one; carried under SolidWorks' name, which the result's
    remade (old, kept) and the record's CarriedMateEntry (name, was) already hold."""
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.rename_refused = {"Lock1"}
    cr = _build_again(fake).carry
    ((was, kept, _),) = cr.remade
    assert was == "Lock1" and kept != "Lock1" and fake.mate(kept, R2[T_ASM]) is not None and cr.stopped == ""
    assert f"Lock1 is carried as {kept}: SolidWorks kept the name it gave it" in cr.facts


@pytest.mark.parametrize("per_configuration", [True, False])
def test_a_fallback_in_another_mode_fixes_its_components_in_every_mode_whatever_one_fix_does(
        monkeypatch, every_gate, mode_findings, per_configuration):
    """Ruled: whether one FixComponent fixes in every configuration is not measured. After a fallback seen in 4L, each
    other mode is read: a component not fixed there is put at its frame and fixed there, and what was read is said."""
    every_gate()

    def tweak(fake):
        fake.remake_codes_in = {"Lock1": {"4L": (46, True)}}
        fake.fix_per_configuration = per_configuration
    cr, fake = _tc_again(monkeypatch, ALL_ON, tweak)
    assert [(f.why, f.subjects) for f in cr.fixed] == [(swbuild.FELL_NEW_ERROR, ("Lock1", "46", "0", "4L"))]
    said = [f for f in cr.facts if f.startswith("after carried1-1 fell back in 4L")]
    if per_configuration:
        assert said == ["after carried1-1 fell back in 4L: carried1-1 had to be fixed in 2H, 4H and N, where one "
                        "FixComponent in 4L had left it not fixed (0 mm from its frame)"], cr.facts
    else:
        assert said == ["after carried1-1 fell back in 4L: carried1-1 fixed in every mode by one FixComponent in 4L"]
    for mode in TC_MODES:
        fake.config = mode
        assert fake._fixed_here("carried1-1"), mode


@pytest.mark.parametrize("per_configuration", [True, False])
def test_a_component_fixed_in_the_old_assembly_is_read_fixed_in_every_mode(monkeypatch, every_gate, mode_findings,
                                                                           per_configuration):
    """The same reading for a component fixed in the old assembly, fixed at its insert in the first mode."""
    every_gate()

    def tweak(fake):
        fake.user_component(TC_ASM, "Housing-1", HOUSING, (I9, (0.0, 0.0, -40.0)), fixed=True)
        fake.saved[_key(HOUSING)] = ([], [])
        fake.fix_per_configuration = per_configuration
    cr, fake = _tc_again(monkeypatch, ALL_ON, tweak)
    said = [f for f in cr.facts if f.startswith("fixed as in TransferCase.SLDASM")]
    if per_configuration:
        assert said == ["fixed as in TransferCase.SLDASM: carried2-1 had to be fixed in 4H, N and 4L, where one "
                        "FixComponent in 2H had left it not fixed (0 mm from its frame)"], cr.facts
    else:
        assert said == ["fixed as in TransferCase.SLDASM: carried2-1 fixed in every mode by one FixComponent in 2H"]


def test_a_fallback_puts_first_what_is_joined_to_a_fixed_component_so_a_kept_mate_cannot_pull_it(monkeypatch,
                                                                                                 every_gate):
    """The review's A8: the fallback puts and fixes each component at once, beginning with one whose kept partners
    stand settled (Housing-1, fixed in the old assembly at its frame). Here the tie leaves Sprocket-2 5 mm off its frame
    when its cluster falls back, and a kept coincident pulls a component put while its partner is free (the fake's
    ``kept_mates_pull``, never measured): put first, Chain-1 (listed first) would be pulled after Sprocket-2, off its
    frame, and the carry would stop with SolidWorks' sentence."""
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.user_component(T_ASM, "Housing-1", HOUSING, (I9, (0.0, 0.0, -40.0)), fixed=True)
    fake.user_component(T_ASM, "Sprocket-2", SPROCKET, (I9, (0.0, 0.0, 50.0)))
    fake.user_component(T_ASM, "Chain-1", SPROCKET, (I9, (0.0, 0.0, 70.0)))
    fake.user_mate(T_ASM, "UserH", kind="coincident", a=("Housing-1", "plane1"), b=("Sprocket-2", "plane1"))
    fake.user_mate(T_ASM, "UserX", kind="coincident", a=("Sprocket-2", "plane2"), b=("Chain-1", "plane2"))
    fake.user_lock(T_ASM, "Lock3", "gear4-1", "Sprocket-2")
    fake.listing_order = ["Chain-1"]                  # GetComponents' order: Chain-1 carried first (carried1)
    fake.locks["Lock3"] = ("gear3", "gear4", "gear3-1", "gear4-1", "gear2", "gear2-1")
    fake.kept_mates_pull = True
    original = fake.remake_mate

    def remake(handle, definition, targets, name, ratio=(1.0, 1.0), flip=None):
        kept = original(handle, definition, targets, name, ratio, flip)
        if definition.name == "Lock3":                # the tie moved Sprocket-2 (carried4-1) 5 mm
            rotation, at = fake.frames["carried4-1"]
            fake.frames["carried4-1"] = (rotation, (at[0], at[1], at[2] + 5.0))
        return kept
    monkeypatch.setattr(fake, "remake_mate", remake)
    cr = _build_again(fake).carry
    assert cr.stopped == "", cr.stopped
    (fell,) = cr.fixed
    assert fell.why == swbuild.FELL_TIE and set(fell.kept) == {"UserH", "UserX"} and fell.deleted == ("Lock3",)
    puts = [a[0] for n, a in fake.calls if n == "place_component" and a[0] in ("carried1", "carried4")]
    assert puts[-2:] == ["carried4", "carried1"]      # Sprocket-2 (its partner Housing-1 settled), then Chain-1
    assert cr.moved == []


def test_a_fallen_component_fixed_in_another_mode_but_off_its_frame_there_is_put_back(monkeypatch, every_gate,
                                                                                      mode_findings):
    """Positions are per configuration (POSITIONS_PER_CONFIGURATION): one FixComponent fixing in every mode (the knob
    False) leaves a component fixed where it stood in each; one standing off its frame there is put back at it, said."""
    every_gate()

    def tweak(fake):
        fake.remake_codes_in = {"Lock1": {"4L": (46, True)}}
        fake.fix_per_configuration = False
        fake.drift_in = {"N": {"carried1-1": (0.0, 0.0, 2.0)}}
    cr, fake = _tc_again(monkeypatch, ALL_ON, tweak)
    assert "after carried1-1 fell back in 4L: carried1-1 read fixed in N but 2 mm from its frame there, so it was put " \
        "back at it" in cr.facts, cr.facts
    assert "after carried1-1 fell back in 4L: carried1-1 fixed in every mode by one FixComponent in 4L" in cr.facts
