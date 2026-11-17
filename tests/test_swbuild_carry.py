"""W9d package A (W9D-INTERFACES.md; ISSUE-1-PLAN §2.5): Build again… carries the user's work. The pure decisions
(``plan_carry``, ``carry_gates``) on hand-made ``OldWork``s, and the worker against the fake SolidWorks of
``test_swbuild``. Every finding W9d reads is None in findings.py; a test that needs one set patches it, and each is
also tested at None, where the item is named with the finding, never guessed."""

import math

import pytest

from gear_generator import findings, swbuild
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
    w = work([comp()], [])
    assert swbuild.carry_gates(w, _carry(), REVISION) == [
        (swbuild.STEP_CARRY_STATES, "COMPONENT_STATE_PER_CONFIGURATION_ROUTE_ON_2026")]
    shown = work([comp()], [], states_route="shown read-only")
    assert swbuild.carry_gates(shown, _carry(), REVISION) == []
    assert swbuild.carry_gates(work([comp()], [], modes=()), _carry(), REVISION) == []


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
