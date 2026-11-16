"""The constants in findings.py against the committed probe evidence.

``probe/results/latest.json`` is what SolidWorks did; this is what stops the
tool's constants drifting from it.
"""

import json
import math
from pathlib import Path

import pytest

from gear_generator import findings
from gear_generator.probe import decide
from gear_generator.probe import p8_motion as p8

LATEST = Path(__file__).resolve().parents[1] / "probe" / "results" / "latest.json"


@pytest.fixture(scope="module")
def evidence():
    assert LATEST.is_file(), f"{LATEST} is the committed probe evidence and must exist"
    data = json.loads(LATEST.read_text(encoding="utf-8"))
    records = {r["name"]: r for r in data["records"]}
    return data, records, decide.decide(records)


def facts(records, name):
    assert records[name]["status"] == "pass", f"{name} did not pass"
    return records[name]["facts"]


def test_the_evidence_is_from_the_version_the_findings_name(evidence):
    data, _, _ = evidence
    assert data["meta"]["version"] == findings.VERIFIED_ON


def test_every_probe_passed_including_the_end_to_end_build(evidence):
    data, records, decided = evidence
    assert [name for name, r in records.items() if r["status"] != "pass"] == []
    assert decided["end_to_end"] is True
    assert {r["tier"] for r in records.values()} >= {0, 1, 2, 3, 4, 5}


def test_decisions(evidence):
    _, _, decided = evidence
    assert decided["flank_recipe"] == findings.DEFAULT_RECIPE
    assert decided["trig_default"] == findings.TRIG_DEFAULT
    assert decided["equation_add_call"] == findings.EQUATION_ADD_CALL
    assert decided["equation_set_route"] == findings.EQUATION_SET_ROUTE
    assert decided["set_units_mmgs_after_new"] is findings.SET_UNITS_MMGS_AFTER_NEW
    assert decided["plane_select_route"] == findings.PLANE_SELECT_ROUTE
    assert decided["equal_constraint"] == findings.RELATIONS["equal"]
    assert decided["circle_dimension"] == findings.CIRCLE_DIMENSION
    assert decided["arc_dimension"] == findings.ARC_DIMENSION
    assert decided["curve_trig"] == findings.CURVE_TRIG
    assert decided["curves_are_fixed"] is findings.CURVES_ARE_FIXED
    assert decided["shared_ends_are_one_point"] is findings.SHARED_ENDS_ARE_ONE_POINT
    assert decided["cut_end_condition"] == findings.CUT_END_CONDITION
    assert decided["pattern_count_dim_index"] == findings.PATTERN_COUNT_DIM_INDEX
    assert decided["save_as_overwrites"] is findings.SAVE_AS_OVERWRITES
    assert decided["first_component_fixed"] is findings.FIRST_COMPONENT_FIXED
    assert decided["manual_steps"] == ["material"]


def test_units(evidence):
    _, records, _ = evidence
    units = facts(records, "document_units")
    if "units_2026_folder" in units:
        assert units["units_2026_folder"] == {"linear": findings.LENGTH_MM, "system": findings.UNIT_SYSTEM_MMGS,
                                              "path": units["units_2026_folder"]["path"]}
    else:
        # On the machine of the 34.1.1 run the default template IS the 2026 folder's Part.PRTDOT, so the probe read
        # it once, as the default: millimetres, with the unit system that template carries there (4, custom).
        assert units["units_default"]["path"].lower().endswith(r"solidworks 2026\templates\part.prtdot")
        assert units["units_default"]["linear"] == findings.LENGTH_MM
    if units["default_template_is_mm"]:
        # A millimetre default template leaves nothing to set (probe/results/probe-results-20260915-023929.json
        # is the run on an inch default, where setting MMGS made a part millimetres).
        assert units["units_default"]["linear"] == findings.LENGTH_MM
        assert findings.SET_UNITS_MMGS_AFTER_NEW is False
    else:
        assert units["set_mmgs_default"]["linear_after"] == findings.LENGTH_MM


INCH_DEFAULT_RUN = LATEST.parent / "probe-results-20260915-023929.json"


def test_an_inch_default_template_is_set_to_millimetres():
    """Probe document_units on the stock 2026 templates (2026-09-15), whose default part was inches.

    The machine's defaults are millimetres now, so latest.json no longer shows
    the inch route the build still takes for an inch template; this run does.
    """
    data = json.loads(INCH_DEFAULT_RUN.read_text(encoding="utf-8"))
    assert data["meta"]["version"] == "SolidWorks 2026 (revision 34.0.0)"
    units = facts({r["name"]: r for r in data["records"]}, "document_units")
    assert units["default_template_is_mm"] is False
    assert units["units_default"]["linear"] == 3          # swLengthUnit_e.swINCHES
    assert units["set_mmgs_works"] is True
    assert units["set_mmgs_default"]["linear_after"] == findings.LENGTH_MM
    assert decide.decide({r["name"]: r for r in data["records"]})["set_units_mmgs_after_new"] is True


def test_constrained_status(evidence):
    _, records, _ = evidence
    status = facts(records, "constrained_status")
    assert status["status_free_line"] == findings.UNDER_CONSTRAINED
    assert status["status_defined_line"] == findings.FULLY_CONSTRAINED


def test_pattern_and_extrude_dimensions(evidence):
    _, records, _ = evidence
    pattern = facts(records, "pattern")
    assert pattern["pattern_call"].startswith(findings.PATTERN_CALL.split(".")[-1])
    name, value = pattern["pattern_dimensions"][findings.PATTERN_COUNT_DIM_INDEX]
    assert name == findings.PATTERN_COUNT_DIM_NAME and value == 6.0
    assert any(math.isclose(v, 2 * math.pi) for _, v in pattern["pattern_dimensions"])


def test_mates(evidence):
    _, records, _ = evidence
    mates = facts(records, "assembly_components_and_mates")
    assert [kind for _, kind in mates["mates"]] == ["MateCoincident", "MateCoincident", "MateDistanceDim",
                                                    "MatePlanarAngleDim"]
    assert mates["distance_mate_dimensions"][0][0] == findings.MATE_DISTANCE_DIM_NAME
    link = facts(records, "assembly_distance_link")
    assert link["component_b_translation_mm_after_global_70"][0] == pytest.approx(70.0)


def test_save_as_returns_a_plain_flag(evidence):
    _, records, _ = evidence
    assert facts(records, "save_as")["save_as3_result_is_tuple"] is False


def test_helical_decisions(evidence):
    _, records, decided = evidence
    assert decided["helix_route"] == "twist"
    assert decided["herringbone_route"] == "mirror"
    assert decided["inverse_tangent"] == findings.INVERSE_TANGENT
    assert decided["extrude_z_sign"] == findings.EXTRUDE_Z_SIGN
    assert decided["top_sketch_y_is_minus_z"] is findings.TOP_SKETCH_Y_IS_MINUS_Z
    assert decided["ref_plane_unflipped_is_plus_z"] is findings.REF_PLANE_UNFLIPPED_IS_PLUS_Z
    assert decided["twist_turn"] == findings.TWIST_TURN
    assert decided["twist_reverse_flips"] is True
    assert decided["mirror_body_route"] == (f"body mark {findings.MIRROR_BODY_MARK}, "
                                            f"plane mark {findings.MIRROR_PLANE_MARK}")
    assert decided["helical_end_to_end"] is True
    assert "overrun " + findings.SWEEP_CUT_CALL.split(".")[-1] in facts(records, "sweep_cut_ends")["sweep_cut_routes"]
    assert facts(records, "equation_inverse_trig")["inverse_trig_accepted"]["atn"] == findings.INVERSE_TRIG_UNITS


def test_bevel_decisions(evidence):
    _, records, decided = evidence
    assert decided["revolve_axis_mark"] == findings.REVOLVE_AXIS_MARK
    assert facts(records, "revolve")["revolve_selected_type"] == findings.REVOLVE_TYPE
    assert decided["bevel_section_x_sign"] == findings.BEVEL_SECTION_X_SIGN
    assert decided["loft_cut_route"] == f"heel then toe, mark {findings.LOFT_PROFILE_MARK}"
    assert decided["loft_cut_type"] == findings.LOFT_CUT_TYPE
    assert decided["bevel_end_to_end"] is True


def test_bevel_beyond_ninety_decisions(evidence):
    """Probe bevel_planes_beyond_90: a crown's and an internal bevel's heel planes face as a cone's does."""
    _, records, decided = evidence
    assert decided["bevel_crown_section_x_sign"] == findings.BEVEL_CROWN_SECTION_X_SIGN
    assert decided["bevel_internal_section_x_sign"] == findings.BEVEL_INTERNAL_SECTION_X_SIGN
    beyond = facts(records, "bevel_planes_beyond_90")
    assert beyond["beyond_cone_dimension_90"] == pytest.approx(90.0)
    assert beyond["beyond_cone_dimension_120"] == pytest.approx(120.0)
    for cone in ("90", "120"):
        assert beyond["beyond_signs"][cone] == {"x_along_outward": 1, "y_along_plus_y": 1, "normal_along_line": 1}


def test_non_parallel_assembly_decisions(evidence):
    _, records, decided = evidence
    assert decided["place_route"] == findings.PLACE_ROUTE
    assert decided["transform_array_order"] == findings.TRANSFORM_ARRAY_ORDER
    assert decided["origin_select_route"] == f"SelectByID2 EXTSKETCHPOINT {findings.ORIGIN_POINT}@Origin"
    assert decided["bevel_mate_route"] == findings.BEVEL_MATE_ROUTE
    assert decided["crossed_route"] == findings.CROSSED_ROUTE
    assert decided["crossed_end_to_end"] is True


def test_gear_mate_decisions(evidence):
    """Probe gear_mate: a 20 : 40 gear mate turned the second axis half as far, opposite ways with Flip off."""
    _, records, decided = evidence
    mate = facts(records, "gear_mate")
    for run, opposite in (("plain", True), ("flipped", False)):
        turned = mate[f"gear_mate_turn_{run}"]
        assert abs(turned["a"]) == pytest.approx(30.0)
        assert turned["b"] / turned["a"] == pytest.approx(-0.5 if opposite else 0.5)
    assert decided["gear_mate_route"] == findings.GEAR_MATE_ROUTE
    assert decided["mate_gear_type"] == findings.MATE_GEAR
    assert decided["gear_mate_numerator_first"] is findings.GEAR_MATE_NUMERATOR_FIRST
    assert decided["gear_mate_external_flip"] is findings.GEAR_MATE_EXTERNAL_FLIP


def test_custom_property_decisions(evidence):
    """Probe custom_properties: Add3 and Get6 work; a global's quoted name stays text, so sizes are not stamped."""
    _, records, decided = evidence
    linked = facts(records, "custom_properties")["linked_property"]
    assert linked["resolved_after"] == '"No. of Teeth"'
    assert decided["custom_property_route"] == findings.CUSTOM_PROPERTY_ROUTE
    assert decided["custom_info_text"] == findings.CUSTOM_INFO_TEXT
    assert decided["custom_property_replace"] == findings.CUSTOM_PROPERTY_REPLACE
    assert decided["property_read_route"] == findings.PROPERTY_READ_ROUTE
    assert decided["property_links_globals"] is findings.PROPERTY_LINKS_GLOBALS


# -- tier 7, on both versions: W4's layout and assembly must build on 2024 and 2026 alike

# The 2024 tier-7 run, in the user's own session; sw2024/latest.json stays that folder's last FULL run.
SW2024 = LATEST.parent / "sw2024" / "probe-results-20261113-184353.json"


@pytest.fixture(scope="module", params=["2026", "2024"])
def tier_seven(request):
    path = LATEST if request.param == "2026" else SW2024
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["meta"]["version"].startswith(f"SolidWorks {request.param} ")
    records = {r["name"]: r for r in data["records"]}
    return records, decide.decide(records)


def test_layout_planes_from_right_and_top(tier_seven):
    """Probes layout_planes and layout_plane_negative_global: unflipped is the plus side; a global cannot cross zero."""
    records, decided = tier_seven
    planes = facts(records, "layout_planes")
    assert decided["layout_plus_flip"] == findings.LAYOUT_PLUS_FLIP
    for base, axis in (("right", 0), ("top", 1)):
        plus = str(findings.LAYOUT_PLUS_FLIP[base])
        assert planes["layout_plane_positions"][base][plus]["origin_mm"][axis] == pytest.approx(7.0)
        assert planes["layout_offset_follows_global"][base]["plane_at_mm"] == pytest.approx(23.0)
        assert planes["layout_offset_dim_default_names"][base] == findings.LAYOUT_OFFSET_DIM
    assert decided["layout_negated_link"] == findings.LAYOUT_NEGATED_LINK
    assert planes["negated_global_link"][findings.LAYOUT_NEGATED_LINK]["plane_at_mm"] == pytest.approx(-11.0)
    if "layout_plane_negative_global" in records:     # an extra, left off in the user's 2024 session
        assert decided["offset_global_crosses_zero"] is findings.OFFSET_GLOBAL_CROSSES_ZERO
        dropped = facts(records, "layout_plane_negative_global")["negative_global"]
        assert dropped["global_value"] == -9.0 and dropped["rebuild"] is True and dropped["error_code"] == 0
        assert dropped["plane_x_mm"] == pytest.approx(7.0)            # silently left where it was


def test_layout_axes(tier_seven):
    """Probes axis_through_named_planes and axis_through_base_planes: every route made the axis where the planes cross."""
    records, decided = tier_seven
    assert decided["axis_plane_select_route"] == findings.AXIS_PLANE_SELECT_ROUTE
    named = facts(records, "axis_through_named_planes")
    assert all(named["axis_plane_select_routes"].values())
    assert named["named_axes_after_globals"]["S1"]["at_mm"] == pytest.approx([26.0, 9.0])
    base = facts(records, "axis_through_base_planes")
    assert decided["axis_through_base_plane"] is findings.AXIS_THROUGH_BASE_PLANE
    assert base["base_plane_axes_after_globals"]["B1"]["at_mm"] == pytest.approx([0.0, 18.0])
    assert base["base_plane_axes_after_globals"]["B2"]["at_mm"] == pytest.approx([31.0, 0.0])
    for axis in list(named["named_axes"].values()) + list(base["base_plane_axes"].values()):
        assert axis["direction"] == pytest.approx([0.0, 0.0, float(findings.LAYOUT_AXIS_Z_SIGN)])


def test_layout_assembly(tier_seven):
    """Probes layout_assembly_five and layout_assembly_reopen: found by name after a reopen, re-placed while fixed."""
    records, decided = tier_seven
    assert decided["workbook_layout_route"] == findings.WORKBOOK_LAYOUT_ROUTE
    assert decided["component_find_route"] == findings.COMPONENT_FIND_ROUTE
    assert decided["replace_fixed_route"] == findings.REPLACE_FIXED_ROUTE
    assert decided["open_assembly_route"] == findings.OPEN_ASSEMBLY_ROUTE
    five = facts(records, "layout_assembly_five")
    assert five["component_instances"]["Probe W7 C"] == ["Probe W7 C-1", "Probe W7 C-2"]
    assert all(five["fixed_after_fix_component"].values())
    reopened = facts(records, "layout_assembly_reopen")
    assert all(v["fixed"] for v in reopened["frames_after_reopen"].values())
    assert all(v["origin_mm"] < 1e-6 for v in reopened["replaced_frames_after_second_open"].values())


def test_opening_a_part_for_update(tier_seven):
    """Probes open_and_activate_part and open_part_from_assembly: OpenDoc6, then ActivateDoc3, then update_variables."""
    records, decided = tier_seven
    assert decided["update_open_route"] == findings.UPDATE_OPEN_ROUTE
    assert decided["open_doc_route"] == findings.OPEN_DOC_ROUTE
    assert decided["open_part_beside_assembly"] is findings.OPEN_PART_BESIDE_ASSEMBLY
    opened = facts(records, "open_and_activate_part")
    assert opened["open Probe W7 Open.SLDPRT"]["errors"] == 0
    again = opened["open_doc_on_open_part"]
    assert again["same_title"] is True and again["made_active"] is False       # so ActivateDoc3 always follows
    assert facts(records, "open_part_from_assembly")["open Probe W7 A.SLDPRT"]["warnings"] == \
        findings.OPEN_DOC_ALREADY_OPEN_WARNING
    assert opened["update_after_reactivate"]["changed"] == ["Probe Teeth"]


def test_layout_part_and_reused_parts(tier_seven):
    """Probes layout_part_without_body and add_component_opened_part: a body-less part works; a closed one is opened first."""
    records, decided = tier_seven
    bodiless = facts(records, "layout_part_without_body")
    assert bodiless["bodiless_solid_bodies"] == 0 and findings.LAYOUT_PART_WITHOUT_BODY is True
    assert (bodiless["bodiless_insert"]["landed_mm"] == bodiless["bodiless_insert"]["asked_mm"]) is \
        findings.BODILESS_LANDS_ORIGIN_AT_POINT
    assert bodiless["bodiless_interference"]["count"] == 0
    assert bodiless["bodiless_save"] == {"returned": True, "errors": 0, "warnings": 0}
    after = bodiless["bodiless_after_reopen"]
    assert after["fixed"] is True and after["origin_mm"] < 1e-6 and after["rotation"] < 1e-6
    assert all(all(routes.values()) for routes in bodiless["bodiless_axes_reachable"].values())
    reuse = facts(records, "add_component_opened_part")
    assert decided["reuse_add_route"] == findings.REUSE_ADD_ROUTE
    assert reuse["add_component_routes"] == {"closed": False, "opened": True}
    assert reuse["same_file_twice_names"] == ["Probe W7 Reuse-1", "Probe W7 Reuse-2"]
    assert decided["components_resolved_after_reopen"] is findings.COMPONENTS_RESOLVED_AFTER_REOPEN
    if "add_component_same_name_elsewhere" in records:     # extras
        assert decided["same_name_elsewhere_inserted"] is findings.SAME_NAME_ELSEWHERE_INSERTED
        clash = facts(records, "add_component_same_name_elsewhere")["same_name_open"]
        assert clash["returned"] is False and clash["errors"] == findings.SAME_NAME_OPEN_ERROR
    if "interference_components" in records:
        entries = facts(records, "interference_components")["interference_entries"]
        assert decided["interference_names_route"] == findings.INTERFERENCE_NAMES_ROUTE
        assert [e["names"] for e in entries] == [["Probe W7 Clash A-1", "Probe W7 Clash B-1"]]


# -- tier 8, on both versions: W5's motion must work on 2024 and 2026 alike

# The 2024 tier-8 run, in the user's freshly restarted session; sw2024/latest.json stays the last FULL 2024 run.
SW2024_TIER8 = LATEST.parent / "sw2024" / "probe-results-20261113-223412.json"


@pytest.fixture(scope="module", params=["2026", "2024"])
def tier_eight(request):
    path = LATEST if request.param == "2026" else SW2024_TIER8
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["meta"]["version"].startswith(f"SolidWorks {request.param} ")
    records = {r["name"]: r for r in data["records"]}
    return records, decide.decide(records), request.param


def test_motion_route_and_its_enums(tier_eight):
    """Tier 8 (PLAN-WORKBOOK §4.4): PLAN-GEARBOX tier 6 items 3-5 passed, so W5 builds the gearbox to turn."""
    records, decided, _version = tier_eight
    assert decided["motion_route"] == findings.MOTION_ROUTE
    for name in decide.MOTION_NEEDS + ("motion_enums", "motion_update"):
        assert records[name]["status"] == "pass", name
    values = facts(records, "motion_enums")["motion_enum_values"]
    assert (values["concentric"], values["lock"]) == (findings.MATE_CONCENTRIC, findings.MATE_LOCK)
    assert (values["aligned"], values["anti_aligned"], values["closest"]) == \
        (findings.MATE_ALIGN_ALIGNED, findings.MATE_ALIGN_ANTI_ALIGNED, findings.MATE_ALIGN_CLOSEST)
    assert values["no_error"] == findings.ADD_MATE_NO_ERROR


def test_a_gear_held_on_its_layout_axis(tier_eight):
    """Probe shaft_axis_mates: Gear Axis coincident with the layout axis; origin a distance from the layout's Front."""
    records, decided, _version = tier_eight
    axes = facts(records, "shaft_axis_mates")
    assert decided["axis_mate_route"] == findings.AXIS_MATE_ROUTE
    assert decided["axis_concentric_refused"] is findings.AXIS_CONCENTRIC_REFUSED
    assert decided["axial_mate_route"] == findings.AXIAL_MATE_ROUTE
    assert axes["axis_cases_holding"] == {"g1": True, "g2": True, "g3": False, "g4": False, "g5": True, "g6": True}
    assert axes["axial_cases_holding"] == {"g1": True, "g2": True, "g3": True, "g4": True, "g5": False, "g6": False}
    assert all(r["status"] == 0 for r in axes["axis_mates_refused"].values())
    assert all(v["turned_over"] for v in axes["explicit_alignment"].values())
    assert all(axes["closest_keeps_the_side"].values())
    reopened = axes["axis_reopened"]
    assert not reopened["errors_on_open"] and not reopened["errors_after_rebuild"]
    entities = axes["axis_mate_entities"]
    assert (entities["g1 axis"]["alignment"], entities["g2 axis"]["alignment"]) == (0, 1)


def test_the_gear_mate_turns_its_gears_the_way_they_mesh(tier_eight):
    """Probe gear_mate_sense: Flip False is the mesh's own sense on every pair, so every listed mesh takes it."""
    records, decided, _version = tier_eight
    sense = facts(records, "gear_mate_sense")
    assert decided["gear_mate_flip_rule"] == findings.GEAR_MATE_FLIP_RULE
    assert sense["sense_rules_consistent"] == sense["sense_rules_consistent_with_faces_too"] == ["mesh"]
    assert decided["gear_mate_sense_depends_on_entities"] is False
    assert sense["alignment_changes_sense"] is False and sense["kept_reverse_follows_the_axes"] is True
    for case in sense["sense_cases"]:
        assert case["turned_by_ratio"], case["name"]
        if not case["placement"]:
            assert case["world_same"] is (case["internal"] != case["flip"]), case["name"]
    # Where it stops: a pinion inside a ring's bore but clear of its face is read as outside it.
    assert sense["sense_boundary_cases"]["ring ++ F apart"]["world_same"] is False
    from gear_generator.probe.p8_motion import needed_flip
    for sa in (1, -1):
        for sb in (1, -1):
            for internal in (False, True):
                assert needed_flip(findings.GEAR_MATE_FLIP_RULE, sa, sb, internal) is findings.GEAR_MATE_FLIP
    assert sense["gear_mate_on_layout_axes"]["mate"]["name"] is None


def test_compound_gears_are_locked_and_an_over_definition_shows(tier_eight):
    """Probe compound_lock: a lock alone holds the placed angle; a conflicting mate is made but shows in four ways."""
    records, decided, version = tier_eight
    lock = facts(records, "compound_lock")
    assert decided["compound_lock_route"] == findings.COMPOUND_LOCK_ROUTE
    holding = lock["lock_holding"]
    for name in ("lock alone", "lock alone, Z-", "angle 37", "angle 137"):
        assert holding[name]["held"] and holding[name]["no_errors"], name
    # The codes differ by version (2026: 46 for a redundant mate, 47 for the one at fault; 2024: 51 for both),
    # the warning flag does not: the mate at fault is the one that is not a warning.
    redundant = findings.MATE_ERROR_OVER_DEFINED if version == "2026" else findings.MATE_ERROR_2024
    at_fault = findings.MATE_ERROR_ILL_DEFINED if version == "2026" else findings.MATE_ERROR_2024
    for name in ("lock, both on the shaft", "lock, both on the shaft, Z-"):          # held, but over-defined
        assert holding[name]["held"] and not holding[name]["no_errors"], name
        assert redundant in [e["code"] for e in holding[name]["errors"].values()]
        assert all(e["warning"] for e in holding[name]["errors"].values())
    over = lock["over_defined"]
    assert over["mate"]["status"] == findings.ADD_MATE_OVER_DEFINED and over["mate"]["name"]   # made all the same
    fault = over["errors"][over["mate"]["name"]]
    assert fault["code"] == at_fault and fault["warning"] is False
    assert all(e["warning"] for n, e in over["errors"].items() if n != over["mate"]["name"])
    assert over["constrained"]["q"] == findings.COMPONENT_OVER_DEFINED
    assert over["rebuild"]["returned"] is True                                                  # the rebuild says nothing
    assert over["mate"]["name"] not in over["errors_after_delete"]


def test_the_twelve_to_one_train_mated_from_w4s_state(tier_eight):
    """Probe mated_train: nine components, no jump, output 1/12 the same way, one degree of freedom, kept on reopen."""
    records, decided, _version = tier_eight
    train = facts(records, "mated_train")
    assert train["train_right_way"] == {"all Z+": True, "middle Z-": True}
    t = train["train"]
    assert t["components"] == 9 and t["rule"] == findings.GEAR_MATE_FLIP_RULE
    assert t["lock"] == findings.COMPOUND_LOCK_ROUTE
    for name, turns in list(t["turns"].items()) + list(t["reopened"]["turns"].items()):
        values = [turns[k] for k in sorted(turns)]
        assert values[0] == pytest.approx(30.0) and values[3] / values[0] == pytest.approx(1 / 12), name
    assert train["one_drive_fully_defines_the_train"] is True
    assert set(t["constrained_mated"].values()) == {findings.COMPONENT_UNDER_DEFINED}
    assert set(t["constrained_driven"].values()) == {findings.COMPONENT_FULLY_DEFINED}
    assert train["put_turns_a_gear_mated_gear_alone"] is True
    assert max(max(v.values()) for v in t["jumps_after_mating"].values()) < 1e-6


def test_update_after_motion(tier_eight):
    """Probe motion_update: the layout's globals carry the mated gears; a put with the gear mate on re-phases it."""
    records, decided, _version = tier_eight
    assert decided["layout_move_carries_mates"] is findings.LAYOUT_MOVE_CARRIES_MATES
    assert decided["mesh_phase_route"] == findings.MESH_PHASE_ROUTE
    assert decided["lock_unsuppress_keeps_the_new_angle"] is findings.LOCK_UNSUPPRESS_KEEPS_THE_NEW_ANGLE
    assert decided["axial_global_moves_gear"] is findings.AXIAL_GLOBAL_MOVES_GEAR
    move = facts(records, "motion_update")["turn_on_a_shaft_move"]
    assert move["as_a_multiple_of_the_need"] == pytest.approx(-1.0)          # SolidWorks turns it the wrong way


# -- tier 7, item 6, on both versions: which rebuild Update SolidWorks gives an assembly

# assembly_rebuild_scope and what it needs on 2024, in a SolidWorks started for the run.
SW2024_REBUILD = LATEST.parent / "sw2024" / "probe-results-20261114-014813.json"


@pytest.fixture(scope="module", params=["2026", "2024"])
def rebuild_scope(request):
    path = LATEST if request.param == "2026" else SW2024_REBUILD
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["meta"]["version"].startswith(f"SolidWorks {request.param} ")
    records = {r["name"]: r for r in data["records"]}
    return records, decide.decide(records)


def test_the_assembly_rebuild_route(rebuild_scope):
    """Probe assembly_rebuild_scope: a top-only rebuild shows every change, reports a failure and marks only what changed."""
    records, decided = rebuild_scope
    scope = facts(records, "assembly_rebuild_scope")
    assert decided["assembly_rebuild_route"] == findings.ASSEMBLY_REBUILD_ROUTE
    assert findings.ASSEMBLY_REBUILD_ROUTE == f"ForceRebuild3({findings.ASSEMBLY_REBUILD_TOP_ONLY})"
    assert decided["assembly_rebuild_keeps_components_unmodified"] is findings.ASSEMBLY_REBUILD_KEEPS_COMPONENTS_UNMODIFIED
    assert decided["full_rebuild_marks_components_modified"] is findings.FULL_ASSEMBLY_REBUILD_MARKS_COMPONENTS_MODIFIED
    assert decided["put_needs_rebuild"] is findings.PUT_NEEDS_REBUILD
    assert decided["opened_reads_unmodified"] is findings.OPENED_READS_UNMODIFIED
    verdicts = scope["rebuild_verdicts"]
    # What shows does not depend on the route, not even on rebuilding at all.
    for route, verdict in verdicts.items():
        for criterion in ("frame_after_put", "interference_after_put", "layout_move_shown", "part_change_shown"):
            assert verdict[criterion] is True, (route, criterion)
    # What is marked and reported does.
    assert all(verdicts[r]["only_changed_marked"] and verdicts[r]["failure_reported"]
               for r in ("ForceRebuild3(True)", "EditRebuild3"))
    assert verdicts["ForceRebuild3(False)"]["only_changed_marked"] is False
    assert verdicts["none"]["failure_reported"] is False
    marked = scope["rebuild_marked"]
    assert marked["ForceRebuild3(False)"]["put"] == ["assembly", "layout", "G1", "G2"]
    assert (marked["none"]["put"] == ["assembly"]) is findings.PUT_MARKS_ASSEMBLY_MODIFIED
    cases = scope["rebuild_cases"]
    for route in ("ForceRebuild3(True)", "EditRebuild3", "ForceRebuild3(False)"):
        failure = cases[route]["failure"]
        assert failure["how"] == "Bore Diameter = 500" and failure["rebuild"]["returned"] is False, route
        assert failure["restored"]["rebuild"]["returned"] is True, route
        assert cases[route]["layout"]["measure"]["Distance_mm"] == pytest.approx(68.75)
        assert cases[route]["layout"]["measure_before"]["Distance_mm"] == pytest.approx(63.75)
    width = cases["ForceRebuild3(True)"]["failure"]["tried"][0]
    assert width["global"] == "Face Width" and width["part_rebuild"] is True and width["part_errors"] == {}


# -- packages P0 and P0b (W5-PLAN §0.3, its review's M4 and M5, the mated rebuild, the rulings), on both versions

# Items 7-14 and what they need on 2024, as round P0b left them, in a SolidWorks started fresh for them.
SW2024_P0 = LATEST.parent / "sw2024" / "probe-results-20261114-071324.json"
# gear_mate_definition alone on 2024, in another fresh SolidWorks (it strands what it changes there).
SW2024_DEFINITION = LATEST.parent / "sw2024" / "probe-results-20261114-073328.json"
# P0's first runs, kept: 2026's full run of 388c8d3, and 2024's beside an assembly the definition route stranded.
FIRST_2026 = LATEST.parent / "probe-results-20261114-034458.json"
FIRST_2024 = LATEST.parent / "sw2024" / "probe-results-20261114-040636.json"


def _records(path):
    return {r["name"]: r for r in json.loads(path.read_text(encoding="utf-8"))["records"]}


@pytest.fixture(scope="module", params=["2026", "2024"])
def package_p0(request):
    path = LATEST if request.param == "2026" else SW2024_P0
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["meta"]["version"].startswith(f"SolidWorks {request.param} ")
    records = {r["name"]: r for r in data["records"]}
    return records, decide.decide(records), request.param


def test_the_six_values_w5_takes_from_tier_eights_records(tier_eight, package_p0):
    """W5-PLAN §0.3: read off motion_enums, motion_update and compound_lock, the same in every file."""
    for records, decided, _version in (tier_eight, package_p0):
        assert (decided["feature_suppress"], decided["feature_unsuppress"], decided["this_configuration"]) == \
            (findings.FEATURE_SUPPRESS, findings.FEATURE_UNSUPPRESS, findings.THIS_CONFIGURATION)
        assert decided["suppression_route"] == findings.SUPPRESSION_ROUTE
        assert decided["lock_select_route"] == findings.LOCK_SELECT_ROUTE
        assert decided["mate_delete_route"] == findings.MATE_DELETE_ROUTE
        assert facts(records, "motion_update")["motion_update"]["lock_moved"]["unsuppressed_by"] == \
            findings.SUPPRESSION_ROUTE


# gear_mate_ratio as it now runs (both routes, each copy's close recorded), alone with what it needs, on each version.
RATIO_2026 = LATEST.parent / "probe-results-20261114-052417.json"
RATIO_2024 = LATEST.parent / "sw2024" / "probe-results-20261114-051023.json"


@pytest.fixture(scope="module", params=["2026", "2024"])
def gear_ratio(request):
    path = RATIO_2026 if request.param == "2026" else RATIO_2024
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["meta"]["version"].startswith(f"SolidWorks {request.param} ")
    records = {r["name"]: r for r in data["records"]}
    return records, decide.decide(records), request.param


def test_a_saved_gear_mates_ratio_two_routes_and_the_versions_split(gear_ratio):
    """Probe gear_mate_ratio: the definition changes the ratio on both versions (its counts put in AddMate5's order,
    read back reversed), but on 2024 that copy cannot be closed; a remade gear mate works and closes on both. The
    versions decided differently then; round P0b settled it (the remake, after P1b)."""
    records, decided, version = gear_ratio
    ratio = facts(records, "gear_mate_ratio")
    tries = {t["how"]: t for t in ratio["gear_mate_ratio"]["tries"]}
    assert list(tries) == [p8.RATIO_CROSSED, "remake"]
    crossed_over = tries[p8.RATIO_CROSSED]
    assert crossed_over["definition"]["fields"] == {"GearRatioNumerator": 17.0, "GearRatioDenominator": 60.0}
    assert crossed_over["definition"]["before"]["GearRatioNumerator"] == 51.0
    assert crossed_over["definition"]["after"]["GearRatioNumerator"] == 60.0
    assert findings.GEAR_MATE_RATIO_PUT_NUMERATOR_FIRST is True
    assert ratio["definition_numerator_is_second_teeth"] is findings.GEAR_MATE_DEFINITION_READS_NUMERATOR_SECOND
    for how, attempt in tries.items():
        assert attempt["right"] is True, how
        assert attempt["turns_before"]["TG4"] == pytest.approx(2.5)
        assert attempt["turns"]["TG4"] == pytest.approx(30 * 17 / 68 * 17 / 60), how
    closes = ratio["gear_mate_ratio_closes"]
    assert closes["remake"] is True and ratio["gear_mate_ratio_routes"]["remake"] is findings.GEAR_MATE_RATIO_REMAKE_WORKS
    assert closes[p8.RATIO_CROSSED] is (True if version == "2026" else findings.MODIFIED_GEAR_MATE_CLOSES_ON_2024)
    # What that version of the item decided; decide now also needs P1b (gear_mate_update), which these files lack.
    assert ratio["gear_mate_ratio_route"] == ("modify definition" if version == "2026" else "remake")
    assert decided["gear_mate_ratio_route"] is None


@pytest.mark.parametrize("version", ["2026", "2024"])
def test_the_first_runs_of_gear_mate_ratio_on_2026_and_2024(version):
    """The full runs' gear_mate_ratio, recipes in their first order: on 2026 the first two inverted the ratio and the
    third was right; on 2024 the first one's copy could not be closed, so the item failed and decided nothing."""
    records = _records(FIRST_2026 if version == "2026" else FIRST_2024)
    decided = decide.decide(records)
    if version == "2024":
        assert records["gear_mate_ratio"]["status"] == "fail" and decided["gear_mate_ratio_route"] is None
        assert "CloseDoc" in records["gear_mate_ratio"]["reason"]
        return
    tries = {t["how"]: t for t in facts(records, "gear_mate_ratio")["gear_mate_ratio"]["tries"]}
    assert list(tries) == [p8.RATIO_ALONE, p8.RATIO_AS_READ, p8.RATIO_CROSSED]
    for how in (p8.RATIO_ALONE, p8.RATIO_AS_READ):      # each turned the output 60/17 of its partner, not 17/60
        assert tries[how]["turns"]["TG4"] == pytest.approx(7.5 * 60 / 17) and not tries[how]["right"]
        assert tries[how]["definition"]["after"]["GearRatioNumerator"] == 17.0
    assert tries[p8.RATIO_CROSSED]["right"] is True


def test_a_lock_re_takes_an_offset_along_the_shaft_and_mates_keep_new_names(package_p0):
    """Probes lock_retake_offset and lock_mate_rename."""
    records, decided, _version = package_p0
    assert decided["lock_retakes_an_offset"] is findings.LOCK_RETAKES_AN_OFFSET
    for case in facts(records, "lock_retake_offset")["lock_retake_offset"]["cases"].values():
        for step in ("after_unsuppress", "after_drive"):
            assert case[step]["angle"] == pytest.approx(11.0) and case[step]["along"] == pytest.approx(3.0)
        assert case["anchor_turned"] == pytest.approx(-7.5)
    assert decided["mate_rename_route"] == findings.MATE_RENAME_ROUTE
    assert decided["mate_find_route"] == findings.MATE_FIND_ROUTE
    renamed = facts(records, "lock_mate_rename")["lock_mate_rename"]
    assert all(renamed["reopened"]["old_gone"].values())
    assert {n: s["suppressed"] for n, s in renamed["reopened"]["states"].items()} == {
        "TG3 locked to TG2": False, "TG3 meshes TG4": False, "TG4 on T3 Axis": False, "TG4 along T3": False,
        "UG3 locked to UG2": True}


def test_the_demonstrations_drive_and_a_put_on_a_twice_meshed_gear(package_p0):
    """Probes demonstration_drive and put_on_twice_meshed_gear."""
    records, decided, _version = package_p0
    assert decided["demonstration_drive_holds"] is findings.DEMONSTRATION_DRIVE_HOLDS
    drive = facts(records, "demonstration_drive")
    assert drive["demonstration_drive_sense"] == {"all Z+": findings.DEMONSTRATION_DRIVE_SENSE,
                                                  "middle Z-": findings.DEMONSTRATION_DRIVE_SENSE}
    turns = drive["demonstration_drive"]["turns"]
    assert (turns["TG1"], turns["TG4"]) == (pytest.approx(30.0), pytest.approx(2.5))
    assert decided["put_on_twice_meshed_gear_holds"] is findings.PUT_ON_TWICE_MESHED_GEAR_HOLDS
    twice = facts(records, "put_on_twice_meshed_gear")
    assert twice["lock_on_put_turns"]["TG2"] == pytest.approx(7.0) and twice["lock_on_put_turns"]["TG3"] == 0.0


def test_an_anchor_held_from_a_datum_plane_far_behind_front(package_p0):
    """Probe axial_datum_plane: the distance never reaches zero, so no Flip changes as the gear passes Front."""
    records, decided, _version = package_p0
    assert decided["axial_datum_route"] == findings.AXIAL_DATUM_ROUTE
    assert decided["axial_datum_flip"] is findings.AXIAL_DATUM_FLIP
    datum = facts(records, "axial_datum_plane")["axial_datum_plane"]
    for step in datum["steps"]:
        assert [r["z"] for r in step["read"].values()] == pytest.approx([step["z"]] * 2)
    assert [s["z"] for s in datum["steps"]] == [17.0, 0.0, -5.0, 17.0]
    assert [r["z"] for r in datum["reopened"]["read"].values()] == pytest.approx([8.0, 8.0])


def test_the_rebuild_a_mated_train_needs_to_be_built_and_changed(package_p0):
    """Probe mated_rebuild_scope (P0b): each route built its own train with itself as the only rebuild and changed
    it; the top-only rebuild did everything the full one did, frame for frame, and marked only what changed."""
    records, decided, _version = package_p0
    assert decided["mated_assembly_rebuild_route"] == findings.MATED_ASSEMBLY_REBUILD_ROUTE == findings.ASSEMBLY_REBUILD_ROUTE
    assert decided["mated_rebuild_keeps_components_unmodified"] is findings.MATED_REBUILD_KEEPS_COMPONENTS_UNMODIFIED
    assert decided["mated_build_rebuild_route"] == findings.MATED_BUILD_REBUILD_ROUTE
    assert decided["mated_build_keeps_components_unmodified"] is findings.MATED_BUILD_KEEPS_COMPONENTS_UNMODIFIED
    scope = facts(records, "mated_rebuild_scope")
    assert all(all(v.values()) for v in scope["mated_build_verdicts"].values())
    assert scope["mated_build_marked"]["ForceRebuild3(False)"]["before_save"] == ["layout", "part"]
    assert scope["mated_build_marked"]["ForceRebuild3(True)"]["before_save"] == []
    for route, verdict in scope["mated_rebuild_verdicts"].items():
        for criterion in p8.MATED_EVIDENCE:
            if not (route == "ForceRebuild3(False)" and criterion == "only_changed_marked"):
                assert verdict[criterion] is True, (route, criterion)
        assert verdict["put_held"] is True
        # Shown before any route, so not evidence for one: the layout move, the part change, the mate error.
        assert {c for c in p8.MATED_RECORDED if verdict[c] == p8.BEFORE} == \
            {"layout_shown", "part_shown", "failure_shown", "failure_cleared"}, route
    assert scope["mated_rebuild_verdicts"]["ForceRebuild3(False)"]["only_changed_marked"] is False
    assert all(max(d.values()) < 1e-6 for d in scope["mated_frames_against_reference"].values())
    for case in scope["mated_rebuild_cases"].values():
        assert case["axial"]["before_route_mm"] == 0.0 and case["axial"]["moved_mm"] == pytest.approx(4.0)
        assert case["drive"]["before_route"]["TG1"] == 0.0
        # The P0 file's 2024 differences did not recur in a clean session: the move shows after ActivateDoc3.
        assert case["layout"]["before_activate_mm"] == 0.0 and case["layout"]["before_route_mm"] == pytest.approx(5.0)
        assert case["layout"]["status_before_route"]["IModelDocExtension.NeedsRebuild2"] == 0
    assert all(r["failure"] is True for r in scope["mated_rebuild_returned"].values())


def test_a_tooth_change_is_an_update_by_the_remake(package_p0):
    """Probes gear_mate_ratio (the remake, alone) and gear_mate_update (P1b): GEAR_MATE_RATIO_ROUTE is "remake"."""
    records, decided, _version = package_p0
    assert decided["gear_mate_ratio_route"] == findings.GEAR_MATE_RATIO_ROUTE == "remake"
    assert decided["gear_mate_update_holds"] is findings.GEAR_MATE_UPDATE_HOLDS
    ratio = facts(records, "gear_mate_ratio")
    remade = ratio["gear_mate_ratio"]
    assert remade["turns_before"]["TG4"] == pytest.approx(2.5) and remade["turns"]["TG4"] == pytest.approx(30 * 17 / 68 * 17 / 60)
    assert remade["close"]["closed"] and remade["reopened"]["close"]["closed"]
    assert remade["reopened"]["turns"]["TG4"] == pytest.approx(30 * 17 / 68 * 17 / 60)
    position = ratio["remade_mate_position"]
    assert (position["after"] == position["count"] - 1 and position["before"] < position["after"]) is \
        findings.REMADE_GEAR_MATE_GOES_LAST
    update = facts(records, "gear_mate_update")["gear_mate_update"]
    for label in ("unsaved", "saved"):
        p = update[label]
        assert p8.update_pass_holds(p, update["teeth_after"]), label
        assert p["drive"]["turns"]["G4"] == pytest.approx(30 * 17 / 68 * 18 / 50)
    assert update["unsaved"]["moved_by_the_full_rebuild"] < 1e-6
    assert update["unsaved"]["reopened"]["definition"] == update["definition_saved"]
    assert update["unsaved"]["reopened"]["teeth"] == {"G3": 17.0, "G4": 51.0}
    assert update["saved"]["reopened"]["teeth"] == {"G3": 18.0, "G4": 50.0}
    assert update["saved"]["reopened"]["interference"]["count"] == 0


@pytest.mark.parametrize("version", ["2026", "2024"])
def test_the_definition_route_is_recorded_and_never_chosen(version):
    """Probe gear_mate_definition, last: the right ratio on both versions; on 2024 the copy cannot be closed."""
    records = _records(LATEST if version == "2026" else SW2024_DEFINITION)
    decided = decide.decide(records)
    assert decided["gear_mate_definition_numerator_is_second"] is findings.GEAR_MATE_DEFINITION_READS_NUMERATOR_SECOND
    tries = facts(records, "gear_mate_definition")["gear_mate_definition"]["tries"]
    assert [t["how"] for t in tries] == [p8.RATIO_CROSSED] and tries[0]["right"] is True
    assert tries[0]["definition"]["fields"] == {"GearRatioNumerator": 17.0, "GearRatioDenominator": 60.0}
    assert findings.GEAR_MATE_RATIO_PUT_NUMERATOR_FIRST is True
    assert decided["modified_gear_mate_closes"] is (True if version == "2026" else findings.MODIFIED_GEAR_MATE_CLOSES_ON_2024)
    assert decided["gear_mate_ratio_route"] != "modify definition"


def test_a_lock_after_a_put_and_the_remake_on_a_twice_meshed_gear(package_p0):
    """Probe put_on_twice_meshed_gear (P0b): driven after a put made with the lock on, the pair turns together at
    the angle the put left; the remake on a gear carrying two gear mates holds and is found by name."""
    records, decided, _version = package_p0
    twice = facts(records, "put_on_twice_meshed_gear")
    after = twice["lock_on_put_after_drive"]
    assert after["relative_angle_change"] == pytest.approx(0.0) and not after["errors"]
    assert (after["anchor_turned"] == pytest.approx(after["follower_turned"]) == pytest.approx(-2.5)) is \
        findings.LOCK_RETAKES_AFTER_A_PUT
    assert decided["remake_on_twice_meshed_gear_holds"] is findings.REMAKE_ON_TWICE_MESHED_GEAR_HOLDS
    e = twice["put_on_twice_meshed_gear"]["remake_on_twice_meshed"]
    assert e["mates_after"][-1] == "GearMate2" and e["mates_before"].index("GearMate2") < len(e["mates_before"]) - 1
    assert e["turns"]["UG1"] == pytest.approx(-10 * 17 / 68 * 17 / 60 * 51 / 17)


P0C_2026 = LATEST.parent / "probe-results-20261114-095421.json"
P0C_2024 = LATEST.parent / "sw2024" / "probe-results-20261114-102300.json"


@pytest.fixture(params=["2026", "2024"])
def round_p0c(request):
    data = json.loads((P0C_2026 if request.param == "2026" else P0C_2024).read_text(encoding="utf-8"))
    assert data["meta"]["version"].startswith(f"SolidWorks {request.param} ")
    records = {r["name"]: r for r in data["records"]}
    assert all(r["status"] == "pass" for r in records.values())
    return records, decide.decide(records), request.param


def test_p1b_carries_an_idlers_tooth_change_and_its_interference_reading_tells(round_p0c):
    """Probes idler_update and gear_mate_update (round P0c): both of the idler's gear mates remade in the whole
    Update shape; a gear half a pitch off clashes where the built phase does not."""
    records, decided, _version = round_p0c
    assert decided["idler_update_holds"] is findings.IDLER_UPDATE_HOLDS is True
    assert decided["gear_mate_update_holds"] is findings.GEAR_MATE_UPDATE_HOLDS
    assert (decided["idler_interference_control_discriminates"] and
            decided["update_interference_control_discriminates"]) is findings.UPDATE_INTERFERENCE_CONTROL_HOLDS
    idler = facts(records, "idler_update")["idler_update"]
    for label in ("unsaved", "saved"):
        p = idler[label]
        assert p8.update_pass_holds(p, idler["teeth_after"], p8.IDLER), label
        assert set(p8.remakes_of(p)) == {"G1 meshes G2", "G2 meshes G3"}
        assert p["drive"]["turns"]["G2"] == pytest.approx(-30 * 15 / 32)
        assert p["drive"]["turns"]["G3"] == pytest.approx(30 * 15 / 38)
        assert idler["interference_control"][label] == {"before_put": 0, "half_pitch": 6, "after": 0}
    assert idler["unsaved"]["reopened"]["teeth"] == {"G1": 17.0, "G2": 30.0, "G3": 40.0}
    assert idler["saved"]["reopened"]["teeth"] == {"G1": 15.0, "G2": 32.0, "G3": 38.0}
    assert idler["saved"]["reopened"]["definitions"]["G2 meshes G3"]["GearRatioNumerator"] == 38.0
    reducer = facts(records, "gear_mate_update")["update_interference_control"]
    assert all(c["half_pitch"] > 0 and c["after"] == 0 for c in reducer.values())


def test_an_unsaved_update_closes_without_asking_and_writes_nothing(round_p0c):
    """Probe unsaved_update_close: CloseDoc and QuitDoc on the assembly, then on each part still open, after an
    unsaved Update left the parts modified."""
    records, decided, _version = round_p0c
    assert all(v is findings.UNSAVED_UPDATE_CLOSE_ASKS for v in decided["unsaved_update_close_asks"].values())
    assert all(v is findings.UNSAVED_UPDATE_CLOSE_DISCARDS for v in decided["unsaved_update_close_discards"].values())
    for how, r in facts(records, "unsaved_update_close")["unsaved_update_close"].items():
        assert r["open_before"]["Probe W8 Update.SLDASM"]["modified"] is True, how
        assert r["teeth_in_memory"] != r["teeth_on_disk"] == r["teeth_on_disk_after"], how
        assert not r["written"] and not r["open_after"] and not r["assembly"]["windows"], how


def test_reading_gear_mate_ratios_marks_nothing_and_origins_do_not_drift(round_p0c):
    """Probes gear_mate_definition_read and origin_noise: what the app's Update check reads and measures."""
    records, decided, _version = round_p0c
    assert decided["gear_mate_definition_read_marks"] == findings.GEAR_MATE_DEFINITION_READ_MARKS == "nothing"
    read = facts(records, "gear_mate_definition_read")["gear_mate_definition_read"]
    assert not any(read["flags_on_open"].values()) and not any(read["flags_after_both"].values())
    assert [(r["GearRatioNumerator"], r["GearRatioDenominator"]) for r in read["reads"]] == [(68.0, 17.0), (50.0, 18.0)]
    assert read["close"]["closed"] and not read["open_after"]
    noise = decided["origin_noise_mm"]
    assert max(v for k, v in noise.items() if k != "drive_start_to_end") == findings.ORIGIN_NOISE_MM
    assert noise["drive_start_to_end"] <= findings.ORIGIN_NOISE_AFTER_A_DRIVE_MM < 1e-6
    assert decided["origin_noise_within_moved_tolerance"] is True
    moved = facts(records, "origin_noise")["origin_noise_detail"]["layout_move"]["moved_shaft_gears_mm"]
    assert moved["G4"] == pytest.approx(1.0)


def test_mates_under_command_in_progress_folders_lightweight_and_a_second_assembly(round_p0c):
    """Probes mates_under_command_in_progress, mate_folders, lightweight_remake, second_assembly_beside_unsaved."""
    records, decided, version = round_p0c
    assert decided["mates_under_command_in_progress"] is findings.MATES_UNDER_COMMAND_IN_PROGRESS
    assert decided["mate_rename_at_once"] is findings.MATE_RENAME_AT_ONCE
    cip = facts(records, "mates_under_command_in_progress")
    assert cip["unsuppress_on_a_lock_already_on"] == {"returned": True, "suppressed_after": False, "errors": {},
                                                      "marks_assembly": findings.UNSUPPRESS_ON_LOCK_ALREADY_ON_MARKS_MODIFIED}
    assert {v["code"] for v in cip["suppressed_mate_error_codes"].values()} == {findings.SUPPRESSED_MATE_ERROR_CODE}
    assert not any(v["warning"] for v in cip["suppressed_mate_error_codes"].values())
    folders = facts(records, "mate_folders")
    assert decided["mate_group_walk_sees_mates_in_a_folder"] is findings.MATE_GROUP_WALK_SEES_MATES_IN_A_FOLDER
    assert folders["mate_folders"]["folder_type"] == findings.MATE_FOLDER_TYPE_NAME
    assert [w["name"] for w in folders["mate_folders"]["walk"] if w["type"] == "FtrFolder"] == \
        ["Probe W8 Mate Folder", "Folder1___EndTag___"]
    assert decided["lightweight_remake"] is findings.LIGHTWEIGHT_REMAKE_HOLDS
    light = facts(records, "lightweight_remake")
    attempts = light["lightweight_remake"]["attempts"]
    assert [set(a["suppression"].values()) for a in attempts] == [{"swComponentFullyResolved"}, {"swComponentLightweight"}]
    assert attempts[1]["options"] - attempts[0]["options"] == 64     # the override flag
    titles = [w[0] for w in light["lightweight_open_dialogs"]["silent, lightweight, overriding the default"]]
    assert ("SOLIDWORKS CAM Error" in titles) is findings.LIGHTWEIGHT_OPEN_RAISES_AN_ADDIN_DIALOG
    assert decided["second_assembly_beside_unsaved"] is findings.SECOND_ASSEMBLY_BESIDE_UNSAVED_HOLDS


def test_the_drag_operator_by_the_knowledge_base_recipe_turns_only_the_gear_it_drags(round_p0c):
    """Probe drag_operator_turns_train (optional): SW-Macro-Database entries/assemblies/05's recipe, then one
    thing varied at a time."""
    records, decided, _version = round_p0c
    assert decided["drag_operator_turns_train"]["holds"] is findings.DRAG_OPERATOR_TURNS_TRAIN
    cases = facts(records, "drag_operator_turns_train")["drag_operator"]["cases"]
    assert len(cases) == len(p8.DRAG_CASES)
    for label, c in cases.items():
        turned = {k: v for k, v in c["train"]["turns"].items() if abs(v) > 1e-6}
        assert turned == {c["dragged"]: pytest.approx(p8.DRAG_DEGREES)}, label
        assert all(ok is True for ok in c["calls"]["Drag"]) and not c["errors"], label
        assert c["calls"]["TransformType as it came"] == 0 and c["calls"]["DragMode as it came"] == 3, label


P0D_2026 = LATEST.parent / "probe-results-20261114-105135.json"
P0D_2024 = LATEST.parent / "sw2024" / "probe-results-20261114-111150.json"


@pytest.fixture(params=["2026", "2024"])
def round_p0d(request):
    data = json.loads((P0D_2026 if request.param == "2026" else P0D_2024).read_text(encoding="utf-8"))
    assert data["meta"]["version"].startswith(f"SolidWorks {request.param} ")
    records = {r["name"]: r for r in data["records"]}
    assert all(r["status"] == "pass" for r in records.values())
    return records, decide.decide(records), request.param


def test_the_unsuppress_on_a_lock_already_on_marks_the_assembly_by_the_call_itself(round_p0d):
    """Probe mates_under_command_in_progress (P0d): every save flag straight before the call and straight after."""
    records, _decided, _version = round_p0d
    u = facts(records, "mates_under_command_in_progress")["unsuppress_on_a_lock_already_on"]
    assert u["flags_before_call"] == {"assembly": False, "layout": False, "part": False}
    assert u["flags_after_call"] == {"assembly": True, "layout": False, "part": False}
    assert (u["marked_by_the_call"] == ["assembly"]) is findings.UNSUPPRESS_ON_LOCK_ALREADY_ON_MARKS_MODIFIED


def test_mates_in_folders_stay_siblings_nested_reopened_and_suppressed(round_p0d):
    """Probe mate_folders (P0d): one folder, a folder inside it, saved and reopened, the folder suppressed."""
    records, decided, _version = round_p0d
    assert decided["mate_folders_hold_in_every_case"] is findings.MATE_GROUP_WALK_SEES_MATES_IN_A_FOLDER is True
    cases = facts(records, "mate_folders")["mate_folder_cases"]
    assert set(cases) == {"one folder", "a folder in a folder", "reopened", "folder suppressed"}
    folders = facts(records, "mate_folders")["mate_folders"]
    walk = [(w["name"], w["type"]) for w in folders["cases"]["reopened"]["walk"] if w["type"] == "FtrFolder"]
    assert walk == [("Probe W8 Mate Folder", "FtrFolder"), ("Probe W8 Inner Folder", "FtrFolder"),
                    ("Folder2___EndTag___", "FtrFolder"), ("Folder1___EndTag___", "FtrFolder")]
    sup = folders["folder_suppression"]
    assert all(sup["mates_suppressed"].values()) is findings.MATE_FOLDER_SUPPRESSION_SUPPRESSES_ITS_MATES
    assert not any(sup["mates_after"].values()) and not sup["errors_after"]


def test_a_lightweight_train_resolves_on_its_first_drive_and_a_plain_open_reads_fully_resolved(round_p0d):
    """Probe lightweight_remake (P0d): GetSuppression2 at every step, and after a plain OpenDoc6."""
    records, decided, _version = round_p0d
    assert decided["lightweight_remake"] is findings.LIGHTWEIGHT_REMAKE_HOLDS
    assert decided["lightweight_first_drive_right"] is findings.LIGHTWEIGHT_FIRST_DRIVE_RIGHT is False
    assert decided["lightweight_resolved_by"] == "after the first drive"
    light = facts(records, "lightweight_remake")["lightweight_remake"]
    assert light["turns_before"]["TG4"] == pytest.approx(-24.166666658) and light["turns"]["TG4"] == pytest.approx(2.125)
    values = {stage: {v[0] for v in read.values()} for stage, read in light["states"].items()}
    assert values["after the open"] == values["after FeatureByName('Gear Axis')"] == {1}
    assert values["after the first drive"] == values["after the remake"] == values["after the drive that follows"] == {2}
    read = decided["component_resolved_read"]
    assert read["call"] == "IComponent2.GetSuppression2" and findings.COMPONENT_RESOLVED_ROUTE == "GetSuppression2"
    assert tuple(read["plain_open_values"]) == findings.COMPONENT_FULLY_RESOLVED_STATES == (read["fully_resolved"],)


RING_2026 = LATEST.parent / "probe-results-20261114-133014.json"
RING_2024 = LATEST.parent / "sw2024" / "probe-results-20261114-135104.json"


def _ring_records(version):
    data = json.loads((RING_2026 if version == "2026" else RING_2024).read_text(encoding="utf-8"))
    assert data["meta"]["version"].startswith(f"SolidWorks {version} ")
    records = {r["name"]: r for r in data["records"]}
    assert all(r["status"] == "pass" for r in records.values())
    return records


def _needed_by_key(records):
    """The Flip each static key needed, read off the cases (selection order folded in: it never mattered)."""
    out = {}
    for c in facts(records, "ring_mate_sense")["ring_sense_cases"]:
        senses = ("+" if c["sigma_p"] > 0 else "-") + ("+" if c["sigma_r"] > 0 else "-")
        key = {"spur": f"spur ring {senses}", "helical": f"helical ring {senses}", "annulus": "plain annulus"}[c["kind"]] \
            if c["internal"] else f"external {senses}"
        needed = c["flip"] if c["right"] else (not c["flip"])
        assert out.get(key, needed) == needed, key
        out[key] = needed
    return out


@pytest.mark.parametrize("version", ["2026", "2024"])
def test_the_flip_a_ring_needs_is_read_off_each_versions_cases(version):
    """Probe ring_mate_sense: the Flip every case needed, per version; the Risky pair as the demonstration saw it."""
    records = _ring_records(version)
    decided = decide.decide(records)
    wanted = findings.GEAR_MATE_FLIP_NEEDED_ON_2026 if version == "2026" else findings.GEAR_MATE_FLIP_NEEDED_ON_2024
    assert _needed_by_key(records) == wanted
    assert decided["ring_risky_app_way_right"] is (version == "2024")
    clashes = facts(records, "ring_mate_sense")["ring_risky_wrong_sense_clashes"]
    assert clashes == ({"app's way": 5, "after the remake": 0} if version == "2026" else {"app's way": 0, "after the remake": 0})
    assert decided["gear_mate_read_back_tells_sense"] is findings.GEAR_MATE_READ_BACK_TELLS_SENSE is True
    assert decided["ring_sense_clash_tells"] is findings.WRONG_GEAR_MATE_SENSE_CLASHES is True
    assert decided["ring_check_and_remake_holds"] is findings.GEAR_MATE_CHECK_AND_REMAKE_HOLDS is True
    risky = facts(records, "ring_mate_sense")["ring_risky"]
    assert list(risky["checked"]["remade"]) == (["G5 meshes G6"] if version == "2026" else [])
    assert not any(risky["checked"]["flags_after"].values()) and not any(risky["right first"]["flags_after"].values())


def test_no_flip_from_static_inputs_is_right_on_both_versions():
    """Every toothed ring needs opposite Flips on 2026 and 2024; only the annulus and the outside pair agree."""
    a, b = _needed_by_key(_ring_records("2026")), _needed_by_key(_ring_records("2024"))
    assert set(a) == set(b)
    agree = {k for k in a if a[k] == b[k]}
    assert agree == {"plain annulus", "external +-"}
    assert findings.GEAR_MATE_FLIP_STATIC_RULE is None


def test_the_read_back_rule_is_stated_as_decide_applies_it():
    assert decide.read_back_says_right(True, True, True) is True and decide.read_back_says_right(False, True, True) is False
    assert decide.read_back_says_right(True, False, False) is True and decide.read_back_says_right(True, True, False) is False
    assert decide.read_back_says_right(None, True, True) is None


TRAINS_SAVED = {"2024": LATEST.parent / "sw2024" / "probe-results-20261114-151013.json",
                "2026": LATEST.parent / "probe-results-20261114-162034.json"}
CROSS_OPENED = LATEST.parent / "probe-results-20261114-162546.json"
CROSS_LABEL = {"G14P meshes G14R": "external ++", "G15P meshes G15R": "external --", "G16P meshes G16R": "external -+",
               "G17P meshes G17R": "helical ring right +-", "G18P meshes G18R": "helical ring 15 +-",
               "G19P meshes G19R": "herringbone ring +-", "G20P meshes G20R": "spur ring shifted pinion +-"}


def _trains_saved(version):
    data = json.loads(TRAINS_SAVED[version].read_text(encoding="utf-8"))
    assert data["meta"]["version"].startswith(f"SolidWorks {version} ")
    records = {r["name"]: r for r in data["records"]}
    assert records["ring_trains_saved"]["status"] == "pass"
    return records


@pytest.mark.parametrize("version", ["2026", "2024"])
def test_the_read_back_marks_nothing_tells_the_sense_everywhere_and_holds_under_command_in_progress(version):
    """Probe ring_trains_saved: the reads around the save flags, the read points, CommandInProgress, more cases."""
    records = _trains_saved(version)
    decided = decide.decide(records)
    assert decided["entity_params_read_marks"] == findings.GEAR_MATE_SENSE_READ_MARKS == "nothing"
    assert decided["ring_trains_read_back_tells_sense"] is findings.GEAR_MATE_SENSE_READ_POINTS_AGREE is True
    assert decided["gear_mate_sense_read_under_command_in_progress"] is \
        findings.GEAR_MATE_SENSE_READ_UNDER_COMMAND_IN_PROGRESS is True
    assert decided["gear_mate_remake_under_command_in_progress"] is findings.GEAR_MATE_REMAKE_UNDER_COMMAND_IN_PROGRESS
    saved = facts(records, "ring_trains_saved")
    assert set(saved["read_after_add_was_under_command_in_progress"].values()) == {False}
    points = saved["ring_trains_read_points"]
    assert len(points) == 13
    for mesh, p in points.items():
        assert p["after AddMate5"] is p["after the rebuild"] is p["driven as made"], mesh
        assert p["after the reopen"] is p["driven at the end"] is True, mesh
    needed = {CROSS_LABEL[k.split(": ")[1]]: v for k, v in saved["ring_trains_needed_flip"].items()
              if k.split(": ")[1] in CROSS_LABEL}
    assert needed == (findings.GEAR_MATE_FLIP_NEEDED_MORE_ON_2026 if version == "2026"
                      else findings.GEAR_MATE_FLIP_NEEDED_MORE_ON_2024)
    update = saved["ring_update_shape"]
    assert update["read_back_says_right"] is (version == "2024") and all(update["check"].values())
    assert (update["remade"] is None) is (version == "2024")
    assert not any(update["check_after"]["clashes_driven"].values()) and findings.GEAR_MATE_READ_BACK_HOLDS_AFTER_A_RATIO_REMAKE


def test_a_ring_train_2024_saved_turns_right_in_2026_and_the_read_back_says_so():
    """Probe ring_trains_from_another_version: 2024's three trains opened in 2026, never saved."""
    data = json.loads(CROSS_OPENED.read_text(encoding="utf-8"))
    assert data["meta"]["version"].startswith("SolidWorks 2026 ")
    records = {r["name"]: r for r in data["records"]}
    decided = decide.decide(records)
    turned = decided["cross_version_ring_turns_right"]
    assert sum(len(v) for v in turned.values()) == 13
    assert all(v for t in turned.values() for v in t.values()) is findings.CROSS_VERSION_RING_TURNS_RIGHT
    assert decided["cross_version_read_back_tells_sense"] is findings.CROSS_VERSION_READ_BACK_TELLS_SENSE is True
    assert all(decided["cross_version_closed_unsaved_unchanged"].values())
    opened = facts(records, "ring_trains_from_another_version")["ring_trains_from_another_version"]
    assert opened["saved_by"] == "32" and opened["opened_on"] == "34"
    for tag in ("risky", "pairs", "geometry"):
        t = opened[tag]
        assert not any(t["flags_on_open"].values()) and not any(t["flags_after_read_back"].values()), tag
        assert not t["remade"] and not any(t["check"]["clashes_driven"].values()), tag
        titles = [w["title"] for c in t["closes"] for w in c["windows"]]
        assert ("SOLIDWORKS CAM Warning" in titles) is findings.CROSS_VERSION_CLOSE_ASKS_TO_SAVE, tag


TURNED = LATEST.parent / "probe-results-20261114-195608.json"


def test_a_turned_gear_mates_reverse_tells_its_sense_about_the_entities_own_directions():
    """Probe turned_gear_mate_sense (W6-PLAN §7.2, SolidWorks 2026): H on meeting axes at 30°, 60° and 90° (own-axis
    angles 30–150) and skew axes at 60° and 90° on both hands, every facing, both Flips; W5's controls."""
    from gear_generator.probe import p9_turned as p9
    data = json.loads(TURNED.read_text(encoding="utf-8"))
    assert data["meta"]["version"].startswith("SolidWorks 2026 ")
    records = {r["name"]: r for r in data["records"]}
    decided = decide.decide(records)
    assert decided["turned_sense_read_back"] == findings.TURNED_GEAR_MATE_SENSE_READ_BACK == "entity senses"
    assert decided["turned_sense_angles"] == findings.TURNED_GEAR_MATE_SENSE_ANGLES == (30.0, 150.0)
    assert decided["turned_sense_angles_skew"] == findings.TURNED_GEAR_MATE_SENSE_ANGLES_SKEW == (60.0, 120.0)
    assert decided["turned_gear_mate_moves_on_make"] is findings.TURNED_GEAR_MATE_MOVES_ON_MAKE is False
    assert decided["gear_mate_entity_order"] == findings.GEAR_MATE_ENTITY_ORDER
    cases = facts(records, "turned_gear_mate_sense")["turned_sense_cases"]
    turned = [c for c in cases if c["cls"] != "P"]
    assert len(turned) == 40 and len(cases) == 44
    assert sorted({c["own_angle"] for c in turned if c["cls"] == "M"}) == [30.0, 60.0, 90.0, 120.0, 150.0]
    assert sorted({c["own_angle"] for c in turned if c["cls"] == "K"}) == [60.0, 90.0, 120.0]
    assert {c["side"] for c in turned if c["cls"] == "K"} == {"+Y", "-Y"}
    for c in cases:
        j = p9.judge(c)
        assert j["ratio_ok"] and j["h_tells"] and c["status"] == findings.ADD_MATE_NO_ERROR, c["geometry"]
    reopened = facts(records, "turned_gear_mate_sense")["turned_sense_reopened"]
    assert len(reopened) == 4 and all(r["m"] == r["m_first"] and r["m_h"] == r["m_h_first"] for r in reopened)


W8_RESULTS = {
    "2026": (LATEST.parent / "w8-spike-20261114-204436.json", LATEST.parent / "w8-followup-20261114-205913.json"),
    "2024": (LATEST.parent / "sw2024" / "w8-spike-20261114-232510.json",
             LATEST.parent / "sw2024" / "w8-followup-20261114-233330.json"),
}


def _w8_decided(year):
    """decide's W8 readings from one version's spike and follow-up files, the spike's first, each from its own."""
    spike_path, followup_path = W8_RESULTS[year]
    out = {}
    for path in (spike_path, followup_path):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["meta"]["version"].startswith(f"SolidWorks {year} ")
        records = {r["name"]: r for r in data["records"]}
        assert records.get("w8_modes_spike" if path == spike_path else "w8_followup", {}).get("status") == "pass"
        for key, value in decide.w8_findings(records).items():
            if value is not None and key not in out:
                out[key] = value
    return out


@pytest.mark.parametrize("year", ["2026", "2024"])
def test_a_collinear_gear_mate_is_settled_by_its_read_back_on_both_versions(year):
    """The W8 spike (W8-PLAN J8, §4.3): the spline and coupling as 1 : 1 gear mates between collinear axes."""
    decided = _w8_decided(year)
    assert decided["collinear_gear_mate_sense_read_back"] is findings.COLLINEAR_GEAR_MATE_SENSE_READ_BACK is True
    assert decided["collinear_gear_mate_moves_on_make"] is findings.COLLINEAR_GEAR_MATE_MOVES_ON_MAKE is False
    assert decided["collinear_gear_mate_holds_slide"] is findings.COLLINEAR_GEAR_MATE_HOLDS_SLIDE is True
    assert decided["collinear_gear_mate_flip_needed"] is getattr(findings, f"COLLINEAR_GEAR_MATE_FLIP_NEEDED_ON_{year}")


def test_the_collinear_spline_needs_opposite_flips_on_the_two_versions():
    """So no Flip is assumed for a spline or a coupling: each is settled by the read-back."""
    assert _w8_decided("2026")["collinear_gear_mate_flip_needed"] is False
    assert _w8_decided("2024")["collinear_gear_mate_flip_needed"] is True
    assert findings.COLLINEAR_GEAR_MATE_FLIP_NEEDED_ON_2026 != findings.COLLINEAR_GEAR_MATE_FLIP_NEEDED_ON_2024


@pytest.mark.parametrize("year", ["2026", "2024"])
def test_the_configuration_calls_hold_as_the_members_are_written_on_both_versions(year):
    """The W8 spike's step 6 and its reopen: the calls swcom's configuration members make, each read back."""
    from gear_generator import swcom
    decided = _w8_decided(year)
    assert decided["configuration_routes"] == {"add": True, "show": True, "delete": True, "suppression": True}
    assert [swcom.configuration_finding(name) for name, _ in swcom.CONFIGURATION_FINDINGS] == [None] * 7
    assert decided["configuration_show_raises_dialog"] is findings.CONFIGURATION_SHOW_RAISES_DIALOG is False
    assert decided["multi_configuration_save_asks"] is findings.MULTI_CONFIGURATION_SAVE_ASKS is False
    assert decided["reopens_in_saved_configuration"] is findings.REOPENS_IN_SAVED_CONFIGURATION is True
    assert decided["suppression_right_after_add"] == findings.SUPPRESSION_RIGHT_AFTER_ADD == "unreliable"
    assert decided["new_mate_in_other_configurations"] == findings.NEW_MATE_IN_OTHER_CONFIGURATIONS
    assert decided["handles_stale_after_configuration_change"] is findings.HANDLES_STALE_AFTER_CONFIGURATION_CHANGE
    assert findings.HANDLES_STALE_AFTER_CONFIGURATION_CHANGE is True
    assert decided["fixed_kept_in_new_configuration"] is findings.FIXED_KEPT_IN_NEW_CONFIGURATION is True
    assert decided["configuration_show_marks"] == findings.CONFIGURATION_SHOW_MARKS == "assembly"
    assert decided["suppression_read_marks"] == findings.SUPPRESSION_READ_MARKS == "nothing"
    assert decided["value_read_marks"] == findings.VALUE_READ_MARKS == "nothing"


@pytest.mark.parametrize("year", ["2026", "2024"])
def test_a_slides_distance_is_held_per_configuration_and_positions_are_kept_per_configuration(year):
    """The W8 follow-up: one distance mate's value per configuration (A), and a free component's place, set by a
    Transform2 put, kept per configuration, the put reaching the active configuration only (B, C), on both versions.
    Since 2026-11-15 nothing reads POSITIONS_PER_CONFIGURATION (W8-INTERFACES §9.18)."""
    decided = _w8_decided(year)
    assert decided["slide_value_per_configuration"] is getattr(findings, f"SLIDE_VALUE_PER_CONFIGURATION_ON_{year}")
    assert getattr(findings, f"SLIDE_VALUE_PER_CONFIGURATION_ON_{year}") is True
    assert decided["value_unset_reads_zero"] is findings.VALUE_UNSET_READS_ZERO is True
    assert decided["system_value_follows_configuration"] is findings.SYSTEM_VALUE_FOLLOWS_CONFIGURATION is False
    assert decided["positions_per_configuration"] is getattr(findings, f"POSITIONS_PER_CONFIGURATION_ON_{year}")
    assert getattr(findings, f"POSITIONS_PER_CONFIGURATION_ON_{year}") is True


def test_a_free_components_put_reads_per_configuration_again_on_this_host():
    """The follow-up rerun unchanged on 2026-11-15 on this host (34.0.0; the first 2026 reading was 34.1.1): B and C
    read as before, so the put fact is not the host's or the revision's."""
    path = LATEST.parent / "w8-followup-20261115-114828.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["meta"]["version"] == "SolidWorks 2026 (revision 34.0.0)"
    records = {r["name"]: r for r in data["records"]}
    assert records["w8_followup"]["status"] == "pass"
    assert decide.w8_findings(records)["positions_per_configuration"] is True
    assert findings.POSITIONS_PER_CONFIGURATION_ON_2026 is True


W8_S2_TURN = LATEST.parent / "w8-workbook-assembly-20261115-111951-s2-turn-carried-per-body.log"
W8_TURN_CHECK = LATEST.parent / "w8-turn-across-configurations-20261115-115500.txt"


def test_a_turn_of_the_mated_train_given_in_one_mode_was_read_in_every_mode_on_a_copy_no_update_had_moved():
    """W8 s2 and the check after it (SolidWorks 2026 34.0.0, this host), the first reading of the turn: on the E4 as
    built, the train turned +37° in 2H stood turned in 4H, N and 4L, LoDog in interference with RangeSlv in 4L; the
    check, by a value set in 2H alone and by a global, turned every body by the same amount in all four. What these
    lines read, not a rule: after an Update had put every mode the same run's successor read otherwise
    (test_s2_after_an_update_had_put_every_mode_…, below)."""
    log = W8_S2_TURN.read_bytes().decode("utf-8", errors="replace")
    assert "attach  SolidWorks 2026 (revision 34.0.0)" in log
    for mode in ("4H", "N", "4L"):
        line = next(x for x in log.splitlines() if x.startswith(f"fact    s2, 2H turned, {mode} shown: as built: in "
                                                                f"{mode}, off the wanted frame: "))
        for body in ("'Sun turned +37.000000", "'RangeSlv turned +37.000000", "'ModeSlv turned +37.000000",
                     "'InDog turned +37.000000", "'LoDog turned +9.250000", "'Carrier carrier turned +9.250000",
                     "'Pl copy 1 turned -18.500000"):
            assert body in line, (mode, body)
    assert "FAIL    s2, 2H turned, 4L shown: as built: no interference in 4L: [(('LoDog', 'RangeSlv'), 531.913)]" in log
    check = W8_TURN_CHECK.read_bytes().decode("utf-8", errors="replace")
    assert check.startswith("# W8 s2's finding checked (SolidWorks 2026, 34.0.0,")
    turned = {"A, the value route": "{'Sun': 37.0, 'Pl copy 1': -18.5, 'Pl copy 2': -18.5, 'Pl copy 3': -18.5, "
                                    "'InDog': 37.0, 'LoDog': 9.25, 'RangeSlv': 37.0, 'ModeSlv': 37.0, "
                                    "'Carrier carrier': 9.25}",
              "B, the global route (from A's end)": "{'Sun': 20.0, 'Pl copy 1': -10.0, 'Pl copy 2': -10.0, "
                                                    "'Pl copy 3': -10.0, 'InDog': 20.0, 'LoDog': 5.0, "
                                                    "'RangeSlv': 20.0, 'ModeSlv': 20.0, 'Carrier carrier': 5.0}"}
    for route, turns in turned.items():
        for mode in ("2H", "4H", "N", "4L"):
            assert f"{route}: {mode}: turned from the start {turns}" in check, (route, mode)
    assert findings.TURN_PER_CONFIGURATION_ON_2026 is False


W8_S7 = LATEST.parent / "w8-s7-20261115-135428.json"
S7_MODES = ("2H", "4H", "N", "4L")
S7_TURNS = (("1", "drive +37 in 2H", 37.0), ("2", "drive +37 in 2H", 37.0), ("3", "drive +37 in 2H", 37.0),
            ("3", "drive +20 in 4L", 20.0), ("3", "drive +11 in N after the reopen", 11.0),
            ("4", "drive +37 in 2H", 37.0))
S7_MOVING_PUTS = (("FIdler +20 in N, plain", "FIdler", "N", "held by FIdler on Idler Axis"),
                  ("FIdler +10 in 4H, plain", "FIdler", "4H", "held by FIdler on Idler Axis"),
                  ("FDrive +2 mm in 2H, the app's route", "FDrive", "2H", "wholly free"))


def _s7_step(data, case, step):
    return next(s for c in data["cases"] if c["case"] == case for s in c["steps"] if s["step"] == step)


def _s7_holds(data):
    """What s7 read, as the two findings comments (POSITIONS_PER_CONFIGURATION, TURN_PER_CONFIGURATION) cite it,
    against the file's own judgements and readings: pins of s7's readings, not rules (s2 read otherwise after an
    Update had put every mode). Raises AssertionError on any that the data does not show."""
    assert data["revision"] == [34, 0, 0] and data["finding_turn"] is False
    # s7 read each turn in every configuration: every body the drive moved, moved in all four, by the step's amount
    # where it was made (as built; after a no-op put in 4L; after it in each; given in 4L; given in N after a reopen;
    # and after case 4's Update, whose puts moved only the front train, so no-op puts for the driven one).
    for case, step, amount in S7_TURNS:
        judgement = _s7_step(data, case, step)["judgement"]
        assert judgement["kind"] == "turn" and judgement["moved_bodies"], (case, step)
        for body, read in judgement["bodies"].items():
            assert read["state"] == {m: "moved" for m in S7_MODES}, (case, step, body)
        assert abs(judgement["bodies"]["Sun"]["change_where_made"][0] - amount) < 1e-6, (case, step)
        assert "shared" in judgement["fits"] and "per_configuration" in judgement["rules_out"], (case, step)
    # ... and it shows at every turned body's own amount in each configuration (the 2H drive on the copy as built).
    first = _s7_step(data, "1", "drive +37 in 2H")["expressed"]
    for mode in S7_MODES:
        assert [first[mode][b][0] for b in ("Sun", "InDog", "RangeSlv", "ModeSlv", "LoDog", "Carrier carrier")] == \
            [37.0, 37.0, 37.0, 37.0, 9.25, 9.25], mode
        assert all(first[mode][f"Pl copy {i}"][0] == -18.5 for i in (1, 2, 3)), mode
    # The configuration once put in splits off from the rest (H) is ruled out for no-op puts: after a no-op put in
    # every configuration a turn still showed in all four.
    after_puts = _s7_step(data, "3", "drive +37 in 2H")["judgement"]
    assert after_puts["bodies"]["Sun"]["forked_before"] == ["2H", "4H", "4L", "N"]
    assert "H" in after_puts["rules_out"] and "H_private_put" in after_puts["rules_out"]
    # A no-op put changed nothing anywhere.
    for case, step in (("2", "no-op put in 4L"), ("3", "no-op put in 2H"), ("3", "no-op put in 4H"),
                       ("3", "no-op put in N"), ("3", "no-op put in 4L")):
        judgement = _s7_step(data, case, step)["judgement"]
        assert judgement["kind"] == "put" and judgement["moved_bodies"] == [] and judgement["bodies"] == {}, step
    # s7 read each moving put stay in the configuration showing, held or free: the body moved there and still in the
    # others.
    for step, body, made_in, during in S7_MOVING_PUTS:
        here = _s7_step(data, "5", step)
        judgement = here["judgement"]
        assert judgement["made_in"] == made_in and judgement["moved_bodies"] == [body], step
        assert judgement["bodies"][body]["state"] == {m: ("moved" if m == made_in else "still") for m in S7_MODES}
        assert judgement["fits"] == ["per_configuration", "H_private_put"], step
        assert here["put"]["held"][body].startswith(during), step
    fdrive = _s7_step(data, "5", "FDrive +2 mm in 2H, the app's route")["put"]
    assert fdrive["route"] == "app" and "FDrive locked to FrontDog" in fdrive["mates_off"]
    assert fdrive["in_mode_mates_off"]["FDrive"] == [0.0, 2.0, 0.0] == fdrive["in_mode_mates_on"]["FDrive"]
    fidler = _s7_step(data, "5", "FIdler +20 in N, plain")["put"]
    assert fidler["route"] == "plain" and fidler["mates_off"] == []
    # Every reading held through a save and reopen.
    reopens = [s for c in data["cases"] for s in c["steps"] if "same_as_before_save" in s]
    assert len(reopens) == 6 and all(s["same_as_before_save"] is True for s in reopens)


def test_s7_read_a_turn_in_every_configuration_and_each_moving_put_only_where_it_was_made():
    """W8 s7 on SolidWorks 2026 34.0.0 (snapshot 1ecd115), on copies no Update had moved: what it read, cited by
    TURN_PER_CONFIGURATION_ON_2026 = False and POSITIONS_PER_CONFIGURATION_ON_2026 = True. Not a rule for the state
    after an Update has put every mode (test_s2_after_an_update_had_put_every_mode_…). The run's five FAILs are its
    flag check after a put (corrected in be07ebd); nothing pinned here rests on them."""
    data = json.loads(W8_S7.read_text(encoding="utf-8"))
    _s7_holds(data)
    assert findings.TURN_PER_CONFIGURATION_ON_2026 is False and findings.POSITIONS_PER_CONFIGURATION_ON_2026 is True


@pytest.mark.parametrize("doctor", ["a turn not reaching 4L", "a turn reaching 4H by a different amount",
                                    "a moving put reaching 2H", "a no-op put moving a body", "a reopen changing"])
def test_s7_pins_fail_on_a_doctored_copy(doctor):
    import copy
    data = copy.deepcopy(json.loads(W8_S7.read_text(encoding="utf-8")))
    if doctor == "a turn not reaching 4L":
        _s7_step(data, "4", "drive +37 in 2H")["judgement"]["bodies"]["Sun"]["state"]["4L"] = "still"
    elif doctor == "a turn reaching 4H by a different amount":
        _s7_step(data, "1", "drive +37 in 2H")["expressed"]["4H"]["RangeSlv"][0] = 30.0
    elif doctor == "a moving put reaching 2H":
        _s7_step(data, "5", "FIdler +20 in N, plain")["judgement"]["bodies"]["FIdler"]["state"]["2H"] = "moved"
    elif doctor == "a no-op put moving a body":
        _s7_step(data, "3", "no-op put in N")["judgement"]["moved_bodies"] = ["FIdler"]
    else:
        next(s for c in data["cases"] for s in c["steps"] if "same_as_before_save" in s)["same_as_before_save"] = False
    with pytest.raises(AssertionError):
        _s7_holds(data)


W8_S7_2024 = LATEST.parent / "sw2024" / "w8-s7-20261115-162418.json"
W8_S7_2024_CASE8 = LATEST.parent / "sw2024" / "w8-s7-20261115-172104-case8.json"
S7_TRAIN = ["Sun", "Pl copy 1", "Pl copy 2", "Pl copy 3", "InDog", "LoDog", "RangeSlv", "ModeSlv", "Carrier carrier"]
S7_2024_TURNS = (("1", "drive +37 in 2H", 37.0), ("2", "drive +37 in 2H", 37.0), ("3", "drive +37 in 2H", 37.0),
                 ("3", "drive +20 in 4L", 20.0), ("3", "drive +11 in N after the reopen", 11.0),
                 ("4", "drive +37 in 2H before the Update", 37.0), ("4", "drive +37 in 2H", 37.0),
                 ("8", "drive +37 in 2H", 37.0), ("8", "fresh drive +37 in 2H", 37.0))


def _s7_2024_holds(data, rerun):
    """What W8 s7 read on SolidWorks 2024 32.5.0, the grounds of TURN_PER_CONFIGURATION_ON_2024 = False: every turn
    of the train read moved in all four configurations, by the step's amount where it was made, "shared" fitting and
    "per_configuration" ruled out — on copies no Update had moved (cases 1-3), after the app's changed Update had put
    the turned train back in every mode (case 4), and after its quiet Update in 4L had put every mode (case 8, and the
    rerun). Raises AssertionError on any that the data does not show."""
    assert data["revision"] == [32, 5, 0] and data["finding_turn"] is None and rerun["revision"] == [32, 5, 0]
    for case, step, amount in S7_2024_TURNS:
        judgement = _s7_step(data, case, step)["judgement"]
        assert judgement["kind"] == "turn" and "Sun" in judgement["moved_bodies"], (case, step)
        if "in 2H" in step:       # in 4L the front train turns too, in N the sleeves stand free
            assert judgement["moved_bodies"] == S7_TRAIN, (case, step)
        for body, read in judgement["bodies"].items():
            assert read["state"] == {m: "moved" for m in S7_MODES}, (case, step, body)
        assert abs(judgement["bodies"]["Sun"]["change_where_made"][0] - amount) < 1e-6, (case, step)
        assert "shared" in judgement["fits"] and "per_configuration" in judgement["rules_out"], (case, step)
    for case, step in (("1", "drive +37 in 2H"), ("8", "fresh drive +37 in 2H")):
        turned = _s7_step(data, case, step)["expressed"]
        for mode in S7_MODES:     # LoDog a quarter of RangeSlv's turn in 4L, where they are coupled
            assert [turned[mode][b][0] for b in ("Sun", "RangeSlv", "LoDog", "Carrier carrier", "Pl copy 1")] == \
                [37.0, 37.0, 9.25, 9.25, -18.5], (case, mode)
    for case, step in (("4", "after the changed Update"), ("8", "after the quiet Update in 4L")):
        back = _s7_step(data, case, step)["expressed"]
        assert all(abs(back[m][b][0]) < 1e-9 for m in S7_MODES for b in S7_TRAIN), (case, step)
    update = next(c for c in data["cases"] if c["case"] == "8")["update"]
    assert update["put_in"] == ["2H", "4H", "N", "4L"] and update["failures"] == []
    # the rerun of case 8: the fresh turn in all four again, then the moving put in 2H stayed there
    fresh = _s7_step(rerun, "8", "fresh drive +37 in 2H")["judgement"]
    assert all(r["state"] == {m: "moved" for m in S7_MODES} for r in fresh["bodies"].values())
    assert fresh["fits"] == ["shared"]
    put = _s7_step(rerun, "8", "moving put in 2H, the train back to its built frames")["judgement"]
    assert put["kind"] == "put" and put["moved_bodies"] == S7_TRAIN and "shared" in put["rules_out"]
    assert all(r["state"] == {m: ("moved" if m == "2H" else "still") for m in S7_MODES} for r in put["bodies"].values())
    reopens = [s for d in (data, rerun) for c in d["cases"] for s in c["steps"] if "same_as_before_save" in s]
    assert len(reopens) == 7 and all(s["same_as_before_save"] is True for s in reopens)


def test_s7_on_2024_read_every_turn_in_every_configuration_so_the_2024_turn_finding_is_false():
    """W8 s7 on SolidWorks 2024 32.5.0 (snapshot 1560b25; probe/results/sw2024/w8-workbook-assembly-20261115-162357-
    s7.log, whose one FAIL is case 8's put, its expectation since corrected; the case-8 rerun at 8702389, 0 failed)."""
    _s7_2024_holds(json.loads(W8_S7_2024.read_text(encoding="utf-8")),
                   json.loads(W8_S7_2024_CASE8.read_text(encoding="utf-8")))
    assert findings.TURN_PER_CONFIGURATION_ON_2024 is False


@pytest.mark.parametrize("doctor", ["a turn not reaching N", "case 8's fresh turn not reaching 4H",
                                    "the case-8 put reaching 4L", "case 4's Update leaving the train turned"])
def test_the_2024_s7_pins_fail_on_a_doctored_copy(doctor):
    import copy
    data = copy.deepcopy(json.loads(W8_S7_2024.read_text(encoding="utf-8")))
    rerun = copy.deepcopy(json.loads(W8_S7_2024_CASE8.read_text(encoding="utf-8")))
    if doctor == "a turn not reaching N":
        _s7_step(data, "2", "drive +37 in 2H")["judgement"]["bodies"]["LoDog"]["state"]["N"] = "still"
    elif doctor == "case 8's fresh turn not reaching 4H":
        _s7_step(data, "8", "fresh drive +37 in 2H")["judgement"]["bodies"]["Sun"]["state"]["4H"] = "still"
    elif doctor == "the case-8 put reaching 4L":
        step = _s7_step(rerun, "8", "moving put in 2H, the train back to its built frames")
        step["judgement"]["bodies"]["Sun"]["state"]["4L"] = "moved"
    else:
        _s7_step(data, "4", "after the changed Update")["expressed"]["4H"]["RangeSlv"][0] = 37.0
    with pytest.raises(AssertionError):
        _s7_2024_holds(data, rerun)


W8_S7_2026_CASE8 = LATEST.parent / "w8-s7-20261115-222252-case8.json"


def _s7_case8_2026_holds(data):
    """What W8 s7 case 8 read on SolidWorks 2026 34.1.1 (alone, at fe74276), cited by the comments of
    TURN_PER_CONFIGURATION_ON_2026 and POSITIONS_PER_CONFIGURATION_ON_2026 and by W8-INTERFACES §9.18: both turns in
    2H read in all four configurations by the same amount, the app's quiet Update in 4L put every mode and left every
    configuration at its built frames, and the moving put in 2H after the fresh turn stayed in 2H (4H, N and 4L at
    the fresh turn after it and after the reopen). Pins of what was
    read, not rules (s2 on 34.0.0 read otherwise). Raises AssertionError on any that the data does not show."""
    assert data["revision"] == [34, 1, 1] and data["snapshot"] == "fe74276" and data["finding_turn"] is False
    for step in ("drive +37 in 2H", "fresh drive +37 in 2H"):
        judgement = _s7_step(data, "8", step)["judgement"]
        assert judgement["kind"] == "turn" and judgement["moved_bodies"] == S7_TRAIN, step
        assert all(r["state"] == {m: "moved" for m in S7_MODES} for r in judgement["bodies"].values()), step
        assert "shared" in judgement["fits"] and "per_configuration" in judgement["rules_out"], step
        turned = _s7_step(data, "8", step)["expressed"]
        for mode in S7_MODES:
            assert [turned[mode][b][0] for b in ("Sun", "RangeSlv", "LoDog", "Carrier carrier", "Pl copy 1")] == \
                [37.0, 37.0, 9.25, 9.25, -18.5], (step, mode)
    update = next(c for c in data["cases"] if c["case"] == "8")["update"]
    assert update["put_in"] == ["2H", "4H", "N", "4L"] and update["failures"] == []
    back = _s7_step(data, "8", "after the quiet Update in 4L")["expressed"]
    assert all(abs(back[m][b][0]) < 1e-9 for m in S7_MODES for b in S7_TRAIN)
    put = _s7_step(data, "8", "moving put in 2H, the train back to its built frames")["judgement"]
    assert put["kind"] == "put" and put["moved_bodies"] == S7_TRAIN and "shared" in put["rules_out"]
    assert all(r["state"] == {m: ("moved" if m == "2H" else "still") for m in S7_MODES} for r in put["bodies"].values())
    for step in ("moving put in 2H, the train back to its built frames", "saved and reopened"):
        stood = _s7_step(data, "8", step)["expressed"]
        for mode in S7_MODES:
            assert [stood[mode][b][0] for b in ("Sun", "RangeSlv", "LoDog", "Carrier carrier", "Pl copy 1")] == \
                ([0.0] * 5 if mode == "2H" else [37.0, 37.0, 9.25, 9.25, -18.5]), (step, mode)
    reopens = [s for c in data["cases"] for s in c["steps"] if "same_as_before_save" in s]
    assert len(reopens) == 1 and reopens[0]["same_as_before_save"] is True


def test_s7_case8_on_2026_34_1_1_read_the_fresh_turn_in_every_configuration_and_the_put_in_2h_alone():
    """W8 s7 case 8 alone on SolidWorks 2026 34.1.1 (probe/results/w8-workbook-assembly-20261115-220745-s1-s7-
    case8.log, 0 failed): neither of s2's two 34.0.0 possibilities; the findings keep their values."""
    _s7_case8_2026_holds(json.loads(W8_S7_2026_CASE8.read_text(encoding="utf-8")))
    assert findings.TURN_PER_CONFIGURATION_ON_2026 is False and findings.POSITIONS_PER_CONFIGURATION_ON_2026 is True


@pytest.mark.parametrize("doctor", ["the fresh turn not reaching 4H", "the put reaching N",
                                    "the Update leaving 4L turned", "the put's 4H Sun at 0, its judgement left"])
def test_the_2026_case8_pins_fail_on_a_doctored_copy(doctor):
    import copy
    data = copy.deepcopy(json.loads(W8_S7_2026_CASE8.read_text(encoding="utf-8")))
    if doctor == "the fresh turn not reaching 4H":
        _s7_step(data, "8", "fresh drive +37 in 2H")["judgement"]["bodies"]["Sun"]["state"]["4H"] = "still"
    elif doctor == "the put reaching N":
        step = _s7_step(data, "8", "moving put in 2H, the train back to its built frames")
        step["judgement"]["bodies"]["Sun"]["state"]["N"] = "moved"
    elif doctor == "the put's 4H Sun at 0, its judgement left":
        _s7_step(data, "8", "moving put in 2H, the train back to its built frames")["expressed"]["4H"]["Sun"][0] = 0.0
    else:
        _s7_step(data, "8", "after the quiet Update in 4L")["expressed"]["4L"]["RangeSlv"][0] = 37.0
    with pytest.raises(AssertionError):
        _s7_case8_2026_holds(data)


def test_s7_on_2024_kept_each_moving_put_in_its_configuration_until_a_turn_wrote_one_place_into_every_one():
    """W8 s7 case 5 on SolidWorks 2024 32.5.0 (findings.py, POSITIONS_PER_CONFIGURATION): the three moving puts each
    read in their configuration alone; then FrontDog driven +15° in N left FIdler, standing at 0, +10, +20 and 0, at
    −2.5° in all four — the same place, not the same amount — so 4H's put was gone. W8's closing run read the same on
    2026 34.1.1 (the test after this one)."""
    data = json.loads(W8_S7_2024.read_text(encoding="utf-8"))
    assert data["revision"] == [32, 5, 0]
    _s7_case5_holds(data)
    assert findings.POSITIONS_PER_CONFIGURATION_ON_2024 is True


W8_S7_CLOSE_2026 = LATEST.parent / "w8-s7-20261116-023505.json"


def test_s7_case5_on_2026_34_1_1_read_as_on_2024():
    """W8's closing run, s7 every case on SolidWorks 2026 34.1.1 (snapshot c583f48): case 5 read what 2024's did —
    each moving put in its configuration alone, then FIdler at the same place in every configuration after FrontDog's
    turn in N, not moved by the same amount (findings.py, POSITIONS_PER_CONFIGURATION)."""
    data = json.loads(W8_S7_CLOSE_2026.read_text(encoding="utf-8"))
    assert data["revision"] == [34, 1, 1] and data["snapshot"] == "c583f48" and data["finding_turn"] is False
    _s7_case5_holds(data)
    assert findings.POSITIONS_PER_CONFIGURATION_ON_2026 is True


@pytest.mark.parametrize("path, revision", [(W8_S7_2024, [32, 5, 0]), (W8_S7_CLOSE_2026, [34, 1, 1])])
def test_s7_case7_read_a_suppressed_couplings_sense_right_on_an_unmodified_copy_marking_nothing(path, revision):
    """W8 s7 case 7 on SolidWorks 2024 32.5.0 and on 2026 34.1.1 (findings.py, SUPPRESSED_GEAR_MATE_SENSE_READ): on a
    copy opened from its files, 2H active, "RangeSlv engages LoDog", suppressed in 2H by the build, answered right
    (τ +1, +1) as "RangeSlv engages InDog", on in 2H, did, and no document read modified before or after."""
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["revision"] == revision
    read = next(c for c in data["cases"] if c["case"] == "7")["suppressed_sense"]
    assert read["active"] == "2H"
    assert read["reads"] == {"RangeSlv engages LoDog": {"suppressed": True, "right": True, "taus": [1, 1]},
                             "RangeSlv engages InDog": {"suppressed": False, "right": True, "taus": [1, 1]}}
    assert len(read["flags_before"]) == len(read["flags_after"]) == 9
    assert not any(read["flags_before"].values()) and not any(read["flags_after"].values())
    assert findings.SUPPRESSED_GEAR_MATE_SENSE_READ == "answers, marks nothing"


def _s7_case5_holds(data):
    for step, body, made_in, during in S7_MOVING_PUTS:
        judgement = _s7_step(data, "5", step)["judgement"]
        assert judgement["made_in"] == made_in and judgement["moved_bodies"] == [body], step
        assert judgement["bodies"][body]["state"] == {m: ("moved" if m == made_in else "still") for m in S7_MODES}
        assert judgement["fits"] == ["per_configuration", "H_private_put"], step
    drive = _s7_step(data, "5", "FrontDog +15 in N, FIdler standing differently")
    assert drive["judgement"]["kind"] == "turn" and drive["judgement"]["fits"] == []
    read = drive["same_amount_or_place"]
    assert read["body"] == "FIdler" and read["made_in"] == "N"
    before = {m: round(read["by_configuration"][m]["before"], 6) for m in S7_MODES}
    after = {m: round(read["by_configuration"][m]["after"], 6) for m in S7_MODES}
    assert before == {"2H": 0.0, "4H": 10.0, "N": 20.0, "4L": 0.0} and set(after.values()) == {-2.5}
    assert {m: read["by_configuration"][m]["same_place"] for m in S7_MODES} == {m: True for m in S7_MODES}
    assert {m: read["by_configuration"][m]["same_amount"] for m in S7_MODES} == {m: m == "N" for m in S7_MODES}


def test_the_w8_gates_open_on_both_versions_from_these_findings():
    """The worker's per-version refusal reads these findings by the revision; the sentence switch reads the turn
    finding: on 2026 and on 2024 a turn can show in other modes (False); a version with no finding of its own makes
    neither claim."""
    from gear_generator import swbuild, swcom
    assert swbuild._modes_version_refusal((34, 1, 1)) is None and swbuild._modes_version_refusal((32, 5, 0)) is None
    assert swcom.positions_per_configuration((34, 1, 1)) is False
    assert swcom.positions_per_configuration((32, 5, 0)) is False
    assert swcom.positions_per_configuration((33, 0, 0)) is None
    assert swbuild._settled(swbuild.MODES_FINDINGS) is None


W8_S2_AFTER_UPDATE = LATEST.parent / "w8-workbook-assembly-20261115-151412-s2.log"


def test_s2_after_an_update_had_put_every_mode_the_turn_was_read_in_4l_and_not_in_4h_or_n():
    """W8 s2 (SolidWorks 2026 34.0.0, app at 4871a85), the state neither finding settles: after an Update had put every
    mode, a fresh +37° in 2H was read in 4L (line 356), and the next Update found 4H and N, shown after its put in 2H,
    at the built turn (lines 448-451); its changed Update found the put of FDrive in 2H in 4H and N and not in 4L
    (569-572, 709). The first press, from a copy no Update had moved, found 2H's put in neither (224-227). So a turn
    has been read in another configuration (TURN_PER_CONFIGURATION_ON_2026 = False, what the sentences rest on). This
    run showed 4L alone between the fresh turn and the second press, a sequence no run has repeated. s7 case 8 on
    34.1.1 read the turn in all four and the put in 2H alone in that state, and the closing run's s2 on 34.1.1, in
    s2's current sequence (4H, N and 4L shown first), read the same as case 8 (the pin below); this 34.0.0 reading
    stays unexplained (W8-INTERFACES §9.18)."""
    lines = W8_S2_AFTER_UPDATE.read_bytes().decode("utf-8", errors="replace").splitlines()
    assert lines[1].startswith("attach  SolidWorks 2026 (revision 34.0.0)") and "(snapshot: 4871a85)" in lines[0]
    assert lines[250].startswith("fact    s2: the state before the fresh turn: modes put in by an Update so far "
                                 "['2H', '4H', '4L', 'N']")
    assert lines[355].startswith("        s2, the fresh turn in 2H, 4L shown")
    for body in ("Sun +37.000000000°", "InDog +37.000000000°", "RangeSlv +37.000000000°", "ModeSlv +37.000000000°",
                 "LoDog +9.250000000°", "Pl copy 1 -18.500000000°"):
        assert body in lines[355], body
    second = "fact    s2 Update in 4L after the fresh turn in 2H: "
    assert lines[447] == second + "2H when shown: out of step [], off axis [], turned True; after its put: clashes []"
    for i, mode in ((448, "4H"), (449, "N")):
        assert lines[i] == second + f"{mode} when shown: out of step [], off axis [], turned False; after its put: " \
                                    "clashes []"
    assert lines[450].startswith(second + "4L when shown: out of step [('RangeSlv', 'LoDog'), ('ModeSlv', 'FrontDog')]")
    for i, (mode, off) in zip(range(568, 572), (("2H", "['FDrive']"), ("4H", "[]"), ("N", "[]"), ("4L", "['FDrive']"))):
        assert lines[i] == f"        post-check of {mode}: turned False; out of step []; off axis {off}; clashes []; " \
                           "interference error ''", mode
    assert lines[708].startswith("fact    s2 changed Update: each mode's judgement when shown") and \
        lines[708].endswith("[('2H', False, ['FDrive'], []), ('4H', False, [], []), ('N', False, [], []), "
                            "('4L', False, ['FDrive'], [])]")
    first = "fact    s2 quiet Update in 4L: "
    assert lines[223].startswith(first + "2H when shown: out of step [], off axis [], turned True")
    assert lines[224].startswith(first + "4H when shown: out of step [('ModeSlv', 'FrontDog')], off axis [], "
                                         "turned False")
    assert lines[225].startswith(first + "N when shown: out of step [], off axis [], turned True")
    assert findings.TURN_PER_CONFIGURATION_ON_2026 is False


W8_CLOSE_S2_2026 = LATEST.parent / "w8-workbook-assembly-20261116-020805-s2-s7.log"


def test_the_closing_s2_on_34_1_1_read_the_fresh_turn_in_every_mode_and_2h_s_put_carried_to_none():
    """W8's closing run, s2 on SolidWorks 2026 34.1.1 (snapshot c583f48): s2's current sequence, which shows 4H, N and
    4L between the fresh turn and the press (7c9634d), not the 151412 one (4L alone). After an Update had put every
    mode, the fresh +37° in 2H read in 4H, N and 4L alike (lines 357, 362, 367), and the Update in 4L after it found 4H
    out of step at ModeSlv–FrontDog and N turned when it showed them after its put in 2H (461-464), as its first press
    did (221-224): the turn reached every mode and 2H's put did not carry, what 2024's s2 and both case 8s read. The
    changed Update's FDrive put in 2H was found in 4H and N and not in 4L (723), as on 34.0.0 and 2024."""
    lines = W8_CLOSE_S2_2026.read_bytes().decode("utf-8", errors="replace").splitlines()
    assert lines[1].startswith("attach  SolidWorks 2026 (revision 34.1.1)") and "(snapshot: c583f48)" in lines[0]
    assert lines[248].startswith("fact    s2: the state before the fresh turn: modes put in by an Update so far "
                                 "['2H', '4H', '4L', 'N']")
    for i, mode in ((356, "4H"), (361, "N"), (366, "4L")):
        assert lines[i].startswith(f"        s2, the fresh turn in 2H, {mode} shown"), mode
        for body in ("Sun +37.000000000°", "InDog +37.000000000°", "RangeSlv +37.000000000°", "ModeSlv +37.000000000°",
                     "LoDog +9.250000000°", "Pl copy 1 -18.500000000°", "FrontDog +0.000000000°"):
            assert body in lines[i], (mode, body)
    assert "(('LoDog', 'RangeSlv'), 531.913)" in lines[367]
    for at, label in ((220, "s2 quiet Update in 4L: "), (460, "s2 Update in 4L after the fresh turn in 2H: ")):
        head = "fact    " + label
        assert lines[at] == head + "2H when shown: out of step [], off axis [], turned True; after its put: clashes []"
        assert lines[at + 1] == head + "4H when shown: out of step [('ModeSlv', 'FrontDog')], off axis [], turned " \
                                       "False; after its put: clashes []"
        assert lines[at + 2] == head + "N when shown: out of step [], off axis [], turned True; after its put: " \
                                       "clashes []"
        assert lines[at + 3].startswith(head + "4L when shown: out of step [('RangeSlv', 'LoDog'), ('ModeSlv', "
                                               "'FrontDog')]")
    assert lines[722].startswith("fact    s2 changed Update: each mode's judgement when shown") and \
        lines[722].endswith("[('2H', False, ['FDrive'], []), ('4H', False, [], []), ('N', False, [], []), "
                            "('4L', False, ['FDrive'], [])]")
    assert findings.TURN_PER_CONFIGURATION_ON_2026 is False and findings.POSITIONS_PER_CONFIGURATION_ON_2026 is True


W7_PUT =LATEST.parent / "w7-planetary-put-20261115-012409.json"
W7_PUT_FOLLOW_ONS = LATEST.parent / "w7-planetary-put-follow-ons-20261115-013108.json"


def _w7_records(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["meta"]["version"].startswith("SolidWorks 2026 ")
    return {r["name"]: r for r in data["records"]}


def test_a_turned_planetary_is_put_back_with_its_gear_mates_off():
    """Probe planetary_put_back (W7's follow-up): routes A-E on Planetary_4to1 turned 37°, C's follow-ons after; the
    first run's senses re-judged (it passed the opposite same_sense; the verdict flips exactly)."""
    first, later = _w7_records(W7_PUT), _w7_records(W7_PUT_FOLLOW_ONS)
    verdicts = decide.planetary_route_verdicts(first, senses_inverted=True)
    assert verdicts == {"A turned": False, "B turned": False, "C turned": True, "D turned": False, "E turned": True}
    assert decide.planetary_route_verdicts(later) == {"C turned and moved": True, "C not turned": True}
    assert decide.planetary_put_route(first, later, senses_inverted=True) == findings.PLANETARY_PUT_ROUTE \
        == "gear mates off around the puts"
    assert decide.planetary_put_route(first, later) is None          # as judged in the run, nothing held
    back = [decide.gear_mates_back_on(r) for r in (first, later)]
    assert back == [{"ratio_kept": True, "marks_nothing_more": True}] * 2
    assert findings.GEAR_MATE_BACK_ON_KEEPS_SENSE_AND_RATIO is True
    assert findings.GEAR_MATE_BACK_ON_MARKS == "nothing beyond the puts"


def test_a_suppressed_gear_mate_answers_its_sense_and_marks_nothing():
    first = _w7_records(W7_PUT)
    assert decide.suppressed_gear_mate_sense_read(first, senses_inverted=True) \
        == findings.SUPPRESSED_GEAR_MATE_SENSE_READ == "answers, marks nothing"


W8_OVER_DEFINED = LATEST.parent / "w8-over-defined-20261115-100312.json"
W8_CONFIGURATION_ORDER = LATEST.parent / "w8-configuration-order-20261115-092100.txt"


def _w8_over_defined():
    """Probe w8_over_defined_show's facts (tier 11), from the run on this machine's SolidWorks 2026 (34.0.0)."""
    data = json.loads(W8_OVER_DEFINED.read_text(encoding="utf-8"))
    assert data["meta"]["version"] == "SolidWorks 2026 (revision 34.0.0)" and data["meta"]["exit_code"] == 0
    records = {r["name"]: r for r in data["records"]}
    return facts(records, "w8_over_defined_show")["w8_over_defined"]


def test_an_over_defined_configuration_shows_without_a_window_that_asks_and_reads_in_error():
    """W8-PLAN §4.2 item 1: two slides on one sleeve in Z, Z shown and rebuilt; Y and X after it; the second slide off."""
    from gear_generator.probe import p11_modes as p11
    w = _w8_over_defined()
    reading = p11.fight_reading(w, "slides")
    assert p11.show_over_defined(reading) == findings.CONFIGURATION_SHOW_OVER_DEFINED == p11.SHOWN_IN_ERROR
    assert reading["windows"] == [("into the fight: ForceRebuild3(True) in Z", "swBalloonTip", "")]
    assert reading["windows_answered"] == []
    assert reading["mates_in_error"] == ["S slide", "S slide 2"] and reading["over_defined"] == ["S"]
    into = w["slides"]["into"]
    assert into["show"]["windows"] == [] and into["active_after_show"] == "Z"
    assert {m: e["code"] for m, e in into["errors_on"].items()} == {"S slide": 47, "S slide 2": 47}
    assert reading["app_problems"] == ["The mate S slide is in error in SolidWorks.",
                                       "The mate S slide 2 is in error in SolidWorks."]
    assert [w["slides"][k]["S_z"] for k in ("after", "also", "back")] == [30.0, 15.0, 20.0]
    assert reading["others_clean"] == {"Y": True, "X": True} and reading["named_exactly"]
    assert w["slides"]["also"]["errors_on"] == {} and w["slides"]["also"]["app_problems"] == []
    assert reading["watch_errors"] == [] and all(c["watch_error"] is None for c in w["watched_calls"])
    assert w["slides"]["again"]["show"]["windows"] == [] and w["slides"]["again"]["rebuild"]["windows"] == []
    assert w["saved_nothing"] is True and all(c.get("dialog") is False for c in w["closes"])


def test_the_balloon_tip_outlived_the_watch_of_the_rebuild_that_raised_it():
    """M1 of W8-REVIEW-TIER11: stood_s 0.79 is where the rebuild's watch stopped looking; the balloon still stood
    after the reads that followed and when Y's show and rebuild began, and was gone once Y's reads ended."""
    w = _w8_over_defined()
    balloon = w["slides"]["into"]["rebuild"]["windows"][0]
    assert balloon["class"] == "swBalloonTip" and balloon["first_s"] == 0.26 and balloon["stood_s"] == 0.79
    assert balloon["answered"] == []
    classes = lambda found: [x.get("class") for x in found]  # noqa: E731
    assert "swBalloonTip" in classes(w["slides"]["into"]["standing_after"])
    assert "swBalloonTip" in classes(w["slides"]["after"]["standing_before"])
    for call in ("the other configuration after it: ShowConfiguration2(Y)",
                 "the other configuration after it: ForceRebuild3(True) in Y"):
        assert "swBalloonTip" in classes(next(c for c in w["watched_calls"] if c["call"] == call)["standing_at_entry"])
    assert "swBalloonTip" not in classes(w["slides"]["after"]["standing_after"])


def test_a_coupling_beside_a_lock_holding_the_sleeve_reads_no_error():
    """§4.2's other fight, measured: redundant but not in error, so reading the mates does not catch it."""
    from gear_generator.probe import p11_modes as p11
    reading = p11.fight_reading(_w8_over_defined(), "coupling_and_lock")
    assert reading["show_returned"] is True and reading["active_is_target"]
    assert reading["mates_in_error"] == [] and reading["over_defined"] == [] and reading["app_problems"] == []
    assert reading["windows"] == [] and reading["other_clean"] and reading["back_clean"]
    assert p11.show_over_defined(reading) is None


def test_a_flag_read_answers_in_the_documents_order_and_a_value_read_in_the_order_passed():
    """Tier 11's reads at three moments, judged against the single-name reads; W8 s0's ad hoc reads said the same."""
    from gear_generator.probe import p11_modes as p11
    w = _w8_over_defined()
    assert w["document_order"] == ["Default", "X", "Z", "Y"] and p11.truths_agree(w)
    sup, val = p11.all_reads(w, "suppression"), p11.all_reads(w, "value")
    assert p11.order_of(sup) == p11.DOCUMENT_ORDER and findings.SUPPRESSION_READ_ORDER == "the document's configuration order"
    assert p11.order_of(val) == p11.ORDER_PASSED and findings.VALUE_READ_ORDER == "the order passed"
    assert sum(r["verdict"] == p11.DOCUMENT_ORDER for r in sup) >= 10
    assert sum(r["verdict"] == p11.ORDER_PASSED for r in val) >= 9
    earlier = W8_CONFIGURATION_ORDER.read_text(encoding="utf-8")
    assert "RangeSlv engages InDog IsSuppressed2(3, ['N', '2H'] ) -> (False, True)" in earlier
    assert "RangeSlv along Rear GetSystemValue3(3, ['4L', 'N'] ) -> (0.066, 0.056)" in earlier
