"""W9d package A (W9D-INTERFACES.md; ISSUE-1-PLAN §2.5): Build again… carries the user's work. The pure decisions
(``plan_carry``, ``carry_gates``) on hand-made ``OldWork``s, and the worker against the fake SolidWorks of
``test_swbuild``. Every finding W9d reads is None in findings.py; a test that needs one set patches it, and each is
also tested at None, where the item is named with the finding, never guessed."""

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


@pytest.fixture
def every_gate(monkeypatch):
    """Every W9d gate patched to its settled value on 2026, as M9 patches them in its own process."""
    def patch(**override):
        values = dict(CARRY_INSERTS=True, CARRY_INSERTS_IN_A_CONFIGURATION=True, CARRY_INSERTS_A_SUBASSEMBLY=True,
                      REFERENCED_CONFIGURATION_READ=True, SUBASSEMBLY_OPEN_MARKS=False,
                      SUBASSEMBLY_OPEN_MARKS_WHEN_LOADED=False, SUBASSEMBLY_READ_ONLY_INSERT=True,
                      PERSIST_REFERENCE_ROUTE_FOR_FACES="route", PERSIST_REFERENCE_ROUTE_FOR_EDGES="route",
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


def test_with_every_gate_none_nothing_is_carried_and_each_item_names_its_finding():
    w = work([comp()], [lock("Lock1", SUN_WHOLE, ent(USER, "Sprocket-1", ENTITY_WHOLE))])
    plan = swbuild.plan_carry(w, _carry(), REVISION)
    assert plan.components == () and plan.mates == ()
    assert _named(plan) == {"Sprocket-1": ("unmeasured", ("insert", "CARRY_INSERTS_ON_2026", Y)),
                            "Lock1": ("component not carried", ("Sprocket-1",))}
    assert swbuild.carry_gates(w, _carry(), REVISION) == [(swbuild.STEP_CARRY_INSERT, "CARRY_INSERTS_ON_2026")]


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
        mate("Concentric5", 1, ent(APP, "Sun", ENTITY_FACE, coaxial=True), ent(USER, "Sprocket-1", ENTITY_FEATURE,
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
                                     GEAR_NAMES + ("Mid Plane",)),) + bodies[3:]
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
        "Coincident6": ("gone", ("feature", "Mid Plane")),
        "Origin1": ("unmeasured", ("origin", "ORIGIN_ENTITY_READ_ON_2026", Y)),
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
        "Coincident1": ("unmeasured", ("face", "PERSIST_REFERENCE_ROUTE_FOR_FACES_ON_2026", Y)),
        "Concentric2": ("unmeasured", ("edge", "PERSIST_REFERENCE_ROUTE_FOR_EDGES_ON_2026", Y)),
        "Coincident3": ("unmeasured", ("vertex", "PERSIST_REFERENCE_ROUTE_FOR_VERTICES_ON_2026", Y))}
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
    assert _named(plan) == {"Coincident1": ("unmeasured", ("feature", "PERSIST_REFERENCE_SURVIVES_RELOAD_ON_2026", Y))}
    assert [m.mate.name for m in plan.mates] == ["Lock1"]
    assert plan.gates == ((swbuild.STEP_CARRY_RELOAD, "PERSIST_REFERENCE_SURVIVES_RELOAD_ON_2026"),)
    # Open: the same mate goes by tier 1, axis to axis selected reversed (MateEntity(0) the second selection).
    plan = swbuild.plan_carry(work(w.components, w.mates), _carry(), REVISION)
    assert plan.mates[0].targets == ("gear1:Gear Axis", "ref:carried1:feature:384a0001")


def test_an_old_assembly_not_read_names_everything_with_the_reason(every_gate):
    w = work([comp()], [lock("Lock1", SUN_WHOLE, ent(USER, "Sprocket-1", ENTITY_WHOLE))], how=swbuild.OLD_UNREAD,
             unread=["RangeBox.SLDASM is not open in SolidWorks"])
    plan = swbuild.plan_carry(w, _carry(), REVISION)
    assert plan.components == () and plan.mates == ()
    assert _named(plan) == {"Sprocket-1": ("old unread", ("RangeBox.SLDASM is not open in SolidWorks",)),
                            "Lock1": ("old unread", ("RangeBox.SLDASM is not open in SolidWorks",))}
    assert [f for _, f in plan.gates] == ["FILE_VERSION_READ_ON_2026", "DEPENDENCIES_READ_ON_2026",
                                          "OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_2026"]
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
    assert {m.name: m.entities for m in result.user_work.mates} == {
        "Coincident7": (("user", "Chain-1", "face", ""), ("user", "Housing-1", "plane", "plane1")),
        "Concentric8": (("user", "Chain-1", "feature", "Gear Axis"), ("layout", "", "feature", "S1 Axis")),
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


def test_with_every_gate_none_the_old_assembly_is_read_nothing_is_carried_and_the_build_stands(monkeypatch):
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
        "Coincident2": ("unmeasured", ("plane", "PERSIST_REFERENCE_SURVIVES_RELOAD_ON_2026", Y))}
    # Set, but the reference does not resolve after the reload on this fake: not found, its component carried.
    every_gate()
    fake = _old_train()
    fake.user_mate(T_ASM, "Coincident2", kind="coincident", a=("Sprocket-1", "plane1"), b=("gear1-1", "plane1"))
    _closed(fake)
    _isfile(monkeypatch, fake)
    cr = _build_again(fake).carry
    assert {n.item: n.why for n in cr.named} == {"Coincident2": "not found"}
    assert cr.inserted and [r[0] for r in cr.remade] == ["Lock1"]
    fake = _old_train()
    fake.user_mate(T_ASM, "Coincident2", kind="coincident", a=("Sprocket-1", "plane1"), b=("gear1-1", "plane1"))
    _closed(fake)
    _isfile(monkeypatch, fake)
    fake.reload_ok = True
    cr = _build_again(fake).carry
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
    assert all(fake.constrained_status(h) == findings.COMPONENT_UNDER_DEFINED for h in ("gear1", "gear4"))


@pytest.mark.parametrize("case", ["new error", "over-defined", "same error"])
def test_a_new_error_or_an_over_definition_falls_back_and_the_same_error_is_carried(monkeypatch, every_gate, case):
    every_gate()
    fake = _two_clusters(_old_train())
    _isfile(monkeypatch, fake)
    if case == "same error":
        fake.mate_codes["Lock3"] = (46, True)          # in error in the old assembly already
        fake.remake_codes["Lock3"] = (46, True)
    elif case == "new error":
        fake.remake_codes["Lock3"] = (46, True)
    else:
        fake.remake_status["Lock3"] = findings.ADD_MATE_OVER_DEFINED
    cr = _build_again(fake).carry
    if case == "same error":
        assert cr.fixed == [] and cr.same_error == [("Lock3", 46)]
        return
    (fell,) = cr.fixed
    assert fell.why == (swbuild.FELL_NEW_ERROR if case == "new error" else swbuild.FELL_OVER_DEFINED)
    assert fell.subjects == (("Lock3", "46", "0", "") if case == "new error" else ("Lock3",))
    assert "Lock1" in {r[0] for r in cr.remade}


def test_a_carry_that_stops_part_way_says_what_it_did_and_leaves_the_build_saved(monkeypatch, every_gate):
    every_gate()
    fake = _two_clusters(_old_train())
    _isfile(monkeypatch, fake)
    fake.raises["remake_mate"] = (3, SolidWorksError("SolidWorks stopped answering."))
    result = _build_again(fake)
    assert result.ok and result.assembly.saved == R2[T_ASM]
    cr = result.carry
    assert cr.inserted and len(cr.remade) == 2 and cr.unsaved
    assert cr.stopped.startswith("SolidWorks stopped the carry while making Lock3 again")
    assert cr.skipped == "making Lock3 again and everything after it"


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
    fake.kind_swap = {"Lock1"}
    cr = _build_again(fake).carry
    assert {n.item: (n.why, n.subjects) for n in cr.named} == {"Lock1": ("differs", ("entities",))}
    assert cr.remade == [] and fake.mate("Lock1", R2[T_ASM]) is None


def test_a_lightweight_user_component_is_carried_resolved_and_its_mates_named(monkeypatch, every_gate):
    every_gate()
    fake = _old_train()
    _isfile(monkeypatch, fake)
    fake.lightweight.add("Sprocket-1")
    cr = _build_again(fake).carry
    assert cr.inserted == [("Sprocket-1", "carried1-1")]
    assert {n.item: n.why for n in cr.named} == {"Lock1": "lightweight"}
    assert "Sprocket-1" in fake.lightweight                         # nothing resolved in the old assembly
    assert ("root_component", (True,)) not in fake.calls


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
