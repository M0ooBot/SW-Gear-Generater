"""What the probe settled about the SolidWorks API, as constants the tool reads.

Every value here is a finding, not a preference: each names the probe it came
from, and every one of them was observed on SolidWorks 2026 (revision 34.0.0,
and again in a full run on 34.1.1, which latest.json now is).
SolidWorks 2024 (revision 32.5.0) reached the same decisions; its runs are in
``probe/results/sw2024/``, where the README says what each one showed.
``tests/test_findings.py`` checks them against ``probe/results/latest.json``
through :mod:`probe.decide`, so they cannot drift from the evidence. They are
constants rather than runtime JSON because the exe must behave the same for
someone who never ran the probe.
"""

from __future__ import annotations

VERIFIED_ON = "SolidWorks 2026 (revision 34.1.1)"

# -- decisions -------------------------------------------------------------

# decide.flank_recipe: curve_literal, curve_globals and curve_rebuild all pass.
DEFAULT_RECIPE = "A"

# equation_syntax: sin ( 90 ) = 1 in a new part from the default template.
# The build measures every document anyway; this is what the dry run prints.
TRIG_DEFAULT = "degrees"

# -- equations --------------------------------------------------------------

# equation_add: Add3 returned -1 on a one-configuration part, as its help says
# it will; Add2 added, read back, and deleted.
EQUATION_ADD_CALL = "Add2"

# equation_set: an indexed property put of Equation(i) propagated to a
# dependent global on rebuild; SetEquationAndConfigurationOption returned -1.
EQUATION_SET_ROUTE = "indexed put Equation(i)"

# -- documents --------------------------------------------------------------

# document_units: this reads the session's default part template, so it says
# what that template is rather than anything about the API. In the 2026-09-15
# run the default was an inch document (swUnitsLinear 3), and
# SetUserPreferenceInteger(swUnitSystem, 0, MMGS) made a new part millimetres,
# after which a global of 30 drove a dimension to 0.030 m (that run's results
# are kept beside latest.json). By 2026-11-13 the default was a millimetre
# template ("MMGS 8 Decimals"), so there was nothing to set, as on 2024. The
# build measures every new part and sets MMGS only when it is not millimetres.
SET_UNITS_MMGS_AFTER_NEW = False
UNIT_SYSTEM = 263            # swUserPreferenceIntegerValue_e.swUnitSystem
UNIT_SYSTEM_MMGS = 5         # swUnitSystem_e.swUnitSystem_MMGS
UNITS_LINEAR = 47            # swUserPreferenceIntegerValue_e.swUnitsLinear
LENGTH_MM = 0                # swLengthUnit_e.swMM

# save_as: IModelDocExtension.SaveAs3 with typed nulls and two by-reference
# longs returned a plain True, not a tuple, and silently overwrote a file that
# was already there — so the tool refuses an existing path itself.
SAVE_AS_CALL = "IModelDocExtension.SaveAs3"
SAVE_AS_OVERWRITES = True
SAVE_AS_SILENT = 1           # swSaveAsOptions_e.swSaveAsOptions_Silent

# -- selecting --------------------------------------------------------------

# sketch_open_close, close_document: IFeature.Select2 on a plane returned False
# with nothing selected in some runs and True in others; SelectByID2 with the
# plane's name read from the tree selected it every time.
PLANE_SELECT_ROUTE = "Select2 checked by count, then SelectByID2 by tree name"

# The dialog AddDimension2 opens for a value; turned off for the build.
INPUT_DIM_VAL_ON_CREATE = 10  # swUserPreferenceToggle_e.swInputDimValOnCreate

# -- sketches ---------------------------------------------------------------

# relations: every constant below was checked by where the geometry went.
# sgEQUAL left two radii at 4 and 7 mm; sgSAMELENGTH made them equal.
RELATIONS = {
    "coincident": "sgCOINCIDENT",
    "tangent": "sgTANGENT",
    "symmetric": "sgSYMMETRIC",
    "horizontal": "sgHORIZONTAL2D",
    "fixed": "sgFIXED",
    "equal": "sgSAMELENGTH",
    # path_sketch_relations: vertical on both path lines left the sketch fully defined.
    "vertical": "sgVERTICAL2D",
}

# dimensions: a circle's AddDimension2 measures its diameter, an arc's its
# radius; an angle's SystemValue is radians.
CIRCLE_DIMENSION = "diameter"
ARC_DIMENSION = "radius"

# constrained_status: a free line read 2, the same line defined read 3.
UNDER_CONSTRAINED = 2
FULLY_CONSTRAINED = 3

# curve_end_points: an entity drawn starting exactly on another's end shares
# that point — a line on a curve's end, a line's, or an arc's — so a coincident
# relation between them already holds and is skipped.
SHARED_ENDS_ARE_ONE_POINT = True

# curve_literal: expressions are in document units and their trig in radians,
# and a degree conversion inside one was refused. curve_fixed_rebuild: sgFIXED
# makes the curve fully defined and it still follows its globals.
CURVE_TRIG = "radians"
CURVE_UNITS = "document"
CURVES_ARE_FIXED = True

# -- features ---------------------------------------------------------------

# extrude: the blank's volume was pi r^2 w to 1e-3, and its depth was D1.
EXTRUDE_CALL = "IFeatureManager.FeatureExtrusion3"

# cut: from the blank's own plane the default direction removed nothing;
# swEndCondThroughAllBoth removed exactly the hole.
CUT_CALL = "IFeatureManager.FeatureCut4"
CUT_END_CONDITION = 9        # swEndConditions_e.swEndCondThroughAllBoth

# pattern: FeatureCircularPattern5 with DName "NULL", axis at mark 1 and the
# cut at mark 4; its dimensions came back as [D3 = 2 pi, D1 = count].
PATTERN_CALL = "IFeatureManager.FeatureCircularPattern5"
PATTERN_COUNT_DIM_INDEX = 1
PATTERN_COUNT_DIM_NAME = "D1"

# -- assemblies -------------------------------------------------------------

# assembly_components_and_mates: AddMate5 returned the mate itself; a distance
# mate's dimension is D1. Whether the first component inserted comes in fixed
# follows the session's default assembly template: it did with the stock
# template (2026-09-15, and 2024), and did not with "MMGS 8 Decimals.asmdot"
# (2026-11-13). The build fixes gear 1 itself (Fix), so it does not rely on it.
MATE_CALL = "IAssemblyDoc.AddMate5"
MATE_COINCIDENT = 0          # swMateType_e
MATE_DISTANCE = 5
MATE_ANGLE = 6
MATE_ALIGN_CLOSEST = 2       # swMateAlign_e
FIRST_COMPONENT_FIXED = False
MATE_DISTANCE_DIM_NAME = "D1"

# -- helical and herringbone ------------------------------------------------

# equation_inverse_trig: atn ( 1 ) read 45 in a degree document, arcsin and
# arccos answered in degrees too, arctan was refused; atn of the transverse
# pressure angle read back equal to the maths.
INVERSE_TANGENT = "atn"
INVERSE_TRIG_UNITS = "degrees"

# center_of_mass: a boss extruded from the Front plane has its centre of mass
# at z = +w/2, so a blank goes toward +Z. The Top plane's sketch x is model +X
# and its sketch y is model -Z, so a line along the axis is sketch-vertical.
EXTRUDE_Z_SIGN = 1
TOP_SKETCH_Y_IS_MINUS_Z = True

# ref_plane_offset: InsertRefPlane(8, d, 0, 0, 0, 0) on the Front plane put the
# plane at z = +d, and with the flip bit 256 at z = -d; both planes' sketches
# face +Z like the Front plane's. The offset is the plane's only dimension, D1.
REF_PLANE_CALL = "IFeatureManager.InsertRefPlane"
REF_PLANE_DISTANCE = 8       # swRefPlaneReferenceConstraints_e.swRefPlaneReferenceConstraint_Distance
REF_PLANE_FLIP = 256         # swRefPlaneReferenceConstraint_OptionFlip
REF_PLANE_UNFLIPPED_IS_PLUS_Z = True

# mirror_body_merge: with the body selected at mark 256 and the plane at mark 2,
# InsertMirrorFeature2(True, False, True, False, 0) made one body of twice the
# volume centred on the plane; marks 1/2 and 1/1 mirrored nothing.
MIRROR_CALL = "IFeatureManager.InsertMirrorFeature2"
MIRROR_BODY_MARK = 256
MIRROR_PLANE_MARK = 2

# sweep_twist: selected as profile at mark 1 and path at mark 4, a sweep with
# swTwistControlConstantTwistAlongPath (8) and a twist of pi/2 turned a circle
# at r 12 a uniform quarter turn (centroid within 3e-4 mm of r0 sin θ/θ), its
# volume A·L to 3e-4. The twist argument is radians; a negative one turned the
# same way as a positive one. Unreversed, the section turned counter-clockwise
# about +Z as z increased for a path toward +Z and for one toward -Z alike — a
# right-hand helix both ways. D1ReverseTwistDir, set through GetDefinition,
# AccessSelections(doc, null) and ModifyDefinition(data, doc, null), turned it
# the other way. Its one dimension is the twist, in radians, D4 by default.
TWIST_CONSTANT_ALONG_PATH = 8   # swTwistControlType_e.swTwistControlConstantTwistAlongPath
SWEEP_DIRECTION = 0            # swSweepDirection_e.swSweepDirection1
SWEEP_PROFILE_MARK = 1
SWEEP_PATH_MARK = 4
TWIST_TURN = {"plus z": 1, "minus z": 1}
TWIST_REVERSE_ROUTE = "ISweepFeatureData.D1ReverseTwistDir through ModifyDefinition"

# sweep_twist_link: renamed Twist and linked to a global of 45, the dimension
# read pi/4: a linked twist is in degrees, and the sweep followed it.
# sweep_cut_ends: InsertCutSwept5 (22 arguments) removed A·w from a blank to
# 1e-7 with the section 2 mm ahead of the face and the path 2 mm past the far
# one, and to 1.5e-4 with the section on the face itself; one body either way.
SWEEP_CUT_CALL = "IFeatureManager.InsertCutSwept5"
SWEEP_ENDS = "overrun"

# pattern_sweep: FeatureCircularPattern5 of a twisted cut left N·A·w removed and
# one body; 24 of them rebuilt in 0.37 s, 0.20 s as a geometry pattern.
PATTERN_OF_SWEEPS_SECONDS_24 = 0.373

# -- internal gears ---------------------------------------------------------

# annulus_extrude: a sketch of two concentric circles, D 40 and d 24, extruded
# by FeatureExtrusion3 to one body of pi/4 (D^2 - d^2) w to 1e-6; the inner
# circle's diameter linked to a global of 20 opened the hole to match.
ANNULUS_EXTRUDES = True

# -- interference -----------------------------------------------------------

# interference: IAssemblyDoc.InterferenceDetectionManager on two r 20 mm,
# 10 mm cylinders 30 mm apart counted one interference of 1813.247 mm^3, the
# lens exactly, and none 50 mm apart. GetInterferenceCount, GetInterferences
# and IInterference.Volume (m^3) read as properties; Done is a method. The
# options below were set before counting.
INTERFERENCE_CALL = "IAssemblyDoc.InterferenceDetectionManager"
INTERFERENCE_OPTIONS = (
    ("TreatCoincidenceAsInterference", False),
    ("TreatSubAssembliesAsComponents", True),
    ("IncludeMultibodyPartInterferences", True),
    ("MakeInterferingPartsTransparent", False),
    ("CreateFastenersFolder", False),
    ("IgnoreHiddenBodies", True),
    ("ShowIgnoredInterferences", False),
    ("UseTransform", False),
)
# So a pair's assembly is checked for interference by the build, and a person
# no longer has to look along the axis for clashing teeth.
INTERFERENCE_CHECKED = True

# -- bevel gears ------------------------------------------------------------

# revolve: a square revolved by FeatureRevolve2 (20 arguments, a full turn in
# radians) about a sketch centreline weighed 2 pi r A to 1e-4 with its centre of
# mass on the centreline, along Z and tilted. With one centreline the sketch
# alone was enough; with a second one in the sketch, the axis line had to be
# selected too, at mark 16, by SelectByID2 "LineN@Sketch" EXTSKETCHSEGMENT.
REVOLVE_CALL = "IFeatureManager.FeatureRevolve2"
REVOLVE_AXIS_MARK = 16
REVOLVE_TYPE = "Revolution"

# ref_plane_normal: InsertRefPlane(2 perpendicular, 0, 4 coincident, 0, 0, 0)
# with a sketch line at mark 0 and its end, selected by its model location
# (EXTSKETCHPOINT), at mark 1 made a plane square to the line through its end.
# Its sketch's origin was the line's end, its x the outward radial of a cone
# whose axis is Z, its y +Y and its normal along the line; the plane kept that
# frame when the line's linked angle and length changed.
REF_PLANE_PERPENDICULAR = 2   # swRefPlaneReferenceConstraint_Perpendicular
REF_PLANE_COINCIDENT = 4      # swRefPlaneReferenceConstraint_Coincident
BEVEL_SECTION_X_SIGN = 1      # the section's outward radial is the plane's sketch +x

# bevel_planes_beyond_90: the same plane made fresh on a pitch cone of 90° (a
# crown gear's, square to X) and of 120° (an internal bevel's, leaning past it).
# On both, the angle placed on the bisector read the angle meant (90°, 120°, not
# a supplement), the plane's origin was the line's end, and its sketch +x was
# (cos δ, 0, −sin δ), the way the teeth's tips point, as it is below 90°; its y
# was +Y and its normal along the line.
BEVEL_CROWN_SECTION_X_SIGN = 1
BEVEL_INTERNAL_SECTION_X_SIGN = 1

# loft_cut_sections: InsertCutBlend (12 arguments) through two similar
# rectangles on parallel planes, both at mark 1 in order, removed their frustum
# L A (1 + k + k^2) / 3 to 1e-4 and left one body.
LOFT_CUT_CALL = "IFeatureManager.InsertCutBlend"
LOFT_PROFILE_MARK = 1
LOFT_CUT_TYPE = "BlendCut"

# axis_from_sketch_line: an angle dimension between two lines on the Top plane,
# placed inside the angle at a point given in model coordinates, read the angle
# (30°); placed at the same point's sketch coordinates it had read 150°.
DIMENSION_PLACED_IN_MODEL_SPACE = True

# move_body_rotate: InsertMoveCopyBody2 turned a body about Y as expected, but the
# feature carried no dimension, so no equation can drive its turn. The bevel
# recipe builds in its final frame instead.
MOVE_BODY_TURN_IS_DIMENSION = False

# -- non-parallel assemblies ------------------------------------------------

# nonparallel_mates: IMathUtility.CreateTransform answered "member not found"
# to late binding and made a transform when invoked as a method with a double
# array; put on IComponent2.Transform2 with the rotation in columns it set the
# frame to 1e-16. AddComponent5 put a part's middle, not its origin, at the
# point given, so the first gear is set on the assembly frame too.
PLACE_ROUTE = "Transform2 put"
TRANSFORM_ARRAY_ORDER = "columns"
# A component's origin selected by SelectByID2 "Point1@Origin@<component>@<assembly>"
# as EXTSKETCHPOINT; two origins made a coincident mate.
ORIGIN_POINT = "Point1"
# Placed first and then mated — origins coincident, gear 2's axis in gear 1's
# top plane, an angle mate between the axes and one between the top planes — a
# bevel-style frame held to 1e-16 and 0 mm.
BEVEL_MATE_ROUTE = "mates"

# -- custom properties ------------------------------------------------------

# custom_properties: IModelDocExtension.CustomPropertyManager("") gave the
# part's manager; Add3(name, swCustomInfoText, value, swCustomPropertyReplaceValue)
# returned 0 and Get6 with by-reference outs read the value back; a second Add3
# of the same name replaced it. Both enum values were read from swconst.tlb.
# A property whose value was a global's quoted name, '"No. of Teeth"', resolved
# to that text itself, before and after the global changed from 25 to 40, so
# the sizes are not stamped: as plain text they would go stale.
CUSTOM_PROPERTY_ROUTE = "Add3"
CUSTOM_INFO_TEXT = 30            # swCustomInfoType_e.swCustomInfoText
CUSTOM_PROPERTY_REPLACE = 2      # swCustomPropertyAddOption_e.swCustomPropertyReplaceValue
PROPERTY_READ_ROUTE = "Get6 with by-reference outs"
PROPERTY_LINKS_GLOBALS = False

# -- gear mate --------------------------------------------------------------

# gear_mate: two cylinders, the first unfixed by IAssemblyDoc.UnfixComponent and
# held on the assembly's own planes with an angle mate to drive it, the second's
# axis held 60 mm away, and AddMate5(swMateGEAR, closest, flip, 0, 0, 0, 20, 40,
# ...) between the two axes made one MateGearDim. Driving the angle mate through
# a global turned the first 30° and the second 15°: the ratio's numerator goes
# with the first selection. With Flip off the two turned opposite ways, as an
# external pair does; with Flip on, the same way. swMateGEAR was read from
# swconst.tlb, after the reader gave back the three mate types above.
GEAR_MATE_ROUTE = "mates"
MATE_GEAR = 10                   # swMateType_e.swMateGEAR
GEAR_MATE_NUMERATOR_FIRST = True
GEAR_MATE_EXTERNAL_FLIP = False
# The same Flip serves a ring. probe/gear_pairs_check.py built pairs through
# pair.assembly_plan and drove gear 1 30°: an external 20 / 40 spur pair turned
# opposite ways at 1 : 2 with Flip False, and a 20-tooth pinion in a 60-tooth ring
# turned the SAME way as the ring at 3 : 1, with no interference, also with Flip
# False; with Flip True it turned against the ring and the teeth clashed (4
# interferences). So SolidWorks takes the sense from where the gears sit, and
# Flip only reverses it; pair.py no longer inverts it for a ring.
# The crossed frame's mates held its rotation; a point's distance from a plane is
# measured along the plane's normal, so a negative offset is mated flipped.
CROSSED_ROUTE = "mates"

# -- the workbook's layout part and static assembly (tier 7) -----------------
#
# Probe tier 7 (p7_workbook), PLAN-WORKBOOK §4.2, on SolidWorks 2026 (34.0.0)
# and 2024 (32.5.0) with the same answers; tests/test_findings.py pins each one
# against both versions' latest.json.

# layout_planes: InsertRefPlane(8 | flip 256, 7 mm) from the Right plane put the
# unflipped plane at x = +7 and the flipped one at -7, both facing +X; from the
# Top plane, y = +7 and -7, both facing +Y. The sketch transform and
# IRefPlane.Transform agreed. The offset was the plane's only dimension, D1, and
# linked to a global it followed 7 -> 23. So, as from Front, unflipped is the plus side.
LAYOUT_PLUS_FLIP = {"right": False, "top": False}
LAYOUT_OFFSET_DIM = "D1"
# A plane on the minus side keeps a positive offset; linked as
# "Offset@<plane>"= - "<global>" it followed a negative global (-7 -> -11), so a
# shaft's X and Y globals can keep their sign. The first form tried was taken.
LAYOUT_NEGATED_LINK = "minus"

# layout_plane_negative_global: a plus-side plane's offset linked to a global set
# to -9 did NOT cross zero. The Equation Manager took the value (it read -9),
# ForceRebuild3 returned True and the plane's error code was 0, yet the offset
# stayed 7 mm and the plane at x = +7: the change was dropped without a word.
# So a shaft whose X or Y changes sign is a structural change, and the layout
# must never rely on a global to carry a plane across its base plane.
OFFSET_GLOBAL_CROSSES_ZERO = False

# axis_through_named_planes: InsertAxis2(True) through two planes made in the
# same part, selected by IFeature.Select2 on the feature found by name (the
# route the app's _select_feature takes first), by SelectByID2 "<name>", "PLANE",
# and by Select2 on the RefPlane InsertRefPlane returned: all three made the axis
# where the planes cross, and it followed both planes' globals on a rebuild.
AXIS_PLANE_SELECT_ROUTE = "Select2 on the feature found by name"
# Every axis made this way, from a Right-parallel and a Top-parallel plane in
# that order, read along -Z from GetRefAxisParams (its second point below the first).
# The order of selection sets it: each gear part's "Gear Axis", made from Top then
# Right (swcom.insert_axis, planes 2 and 3), read +Z in the parts built by
# probe/gear_pairs_check.py on 2026. A layout axis that a gear's axis is to be
# mated to (W5) can be made Top-parallel first so the two agree.
LAYOUT_AXIS_Z_SIGN = -1
# axis_through_base_planes: with the Right or Top plane itself in place of an
# offset plane (a shaft at X = 0, Y = 0, or both), the axis lay on it and the
# other coordinate still followed its global.
AXIS_THROUGH_BASE_PLANE = True

# layout_assembly_five / layout_assembly_reopen: five components (one part twice,
# named "<part>-1" and "<part>-2"), each set by a Transform2 put, then fixed by
# Select4 + FixComponent(), saved, closed and opened again by OpenDoc6: each was
# where it was left and still fixed, found by IAssemblyDoc.GetComponentByName
# (GetComponents(True), the root component's GetChildren and FeatureByName ->
# GetSpecificFeature2 found all five too). A Transform2 put moved a FIXED
# component without unfixing it, and the new frames survived a save and reopen.
COMPONENT_FIND_ROUTE = "GetComponentByName"
REPLACE_FIXED_ROUTE = "Transform2 put"
OPEN_ASSEMBLY_ROUTE = "OpenDoc6"

# open_and_activate_part: OpenDoc6(path, 1, swOpenDocOptions_Silent 1, "", out,
# out) returned the document itself, not a tuple, with errors 0, and made a
# closed part active over another document. On a part already open it returned
# the same document with warning 128 (swFileLoadWarning_AlreadyOpen) and did NOT
# bring it forward, so ActivateDoc3 always follows; swbuild.update_variables
# then accepted it. open_part_from_assembly: the same for a part loaded only as
# a component of an open assembly (listed among the open documents, opened with
# warning 128, activated, and changed by update_variables).
UPDATE_OPEN_ROUTE = "open and activate"
OPEN_DOC_ROUTE = "OpenDoc6"
OPEN_DOC_SILENT = 1              # swOpenDocOptions_e.swOpenDocOptions_Silent, read from swconst.tlb
OPEN_DOC_ALREADY_OPEN_WARNING = 128
OPEN_PART_BESIDE_ASSEMBLY = True

# layout_part_without_body: the layout part as W4 makes it, planes and named axes
# and no solid body, inserted by AddComponent5 at (12, -7, 3) mm landed with its
# ORIGIN there (a solid part lands with the middle of its box there, see
# PLACE_ROUTE), was placed at identity, fixed, and saved with no error or warning;
# interference detection ran with it in the assembly and found nothing. Reopened,
# it was found by GetComponentByName at identity, fixed and fully resolved, and
# each named axis selected in the assembly both by FeatureByName + Select2 and by
# SelectByID2 "<axis>@<component>@<assembly>", "AXIS".
LAYOUT_PART_WITHOUT_BODY = True
BODILESS_LANDS_ORIGIN_AT_POINT = True

# add_component_opened_part: AddComponent5 of a part saved and CLOSED returned
# None, though the API help's "the file must be loaded" is about exactly this;
# the same part opened by OpenDoc6 first (and left the active document) went in.
# So a part reused from an earlier build is opened before it is inserted. The
# same file inserted twice is "<stem>-1" and "<stem>-2".
REUSE_ADD_ROUTE = "opened"
# add_component_same_name_elsewhere (extra): with "<stem>.SLDPRT" in the assembly,
# OpenDoc6 of another folder's "<stem>.SLDPRT" returned nothing with error 65536
# (swFileWithSameTitleAlreadyOpen) and AddComponent5 of it returned None. No
# dialog. Two parts of one file name cannot be in one session, so the build must
# refuse a reused part whose name clashes with one it makes.
SAME_NAME_ELSEWHERE_INSERTED = False
SAME_NAME_OPEN_ERROR = 65536

# interference_components (extra): IInterference.Components, read as a property
# through late binding, gave a tuple of the two components; their Name2s named the
# two overlapping cylinders and not the third, with the lens's volume. So a CHECK
# can say which gears interfere.
INTERFERENCE_NAMES_ROUTE = "Components (property)"

# layout_assembly_reopen: every component of a reopened assembly came back fully
# resolved (GetSuppression2 2, swComponentFullyResolved), on 2026 and in the
# user's own 2024 session, so finding and re-placing them need no resolve step.
COMPONENTS_RESOLVED_AFTER_REOPEN = True

# Items 1-4 of PLAN-WORKBOOK §4.2 and the body-less layout part all passed, so the
# layout part and the static assembly are built.
WORKBOOK_LAYOUT_ROUTE = "layout"

# -- which rebuild Update SolidWorks gives an assembly (tier 7, item 6) ------
#
# assembly_rebuild_scope, after the W4 rerun on 2026 found ForceRebuild3(False) on an
# assembly marking every component modified (docs/notes-workbook/W4-RERUN-2026.md).
# Observed on SolidWorks 2026 (34.1.1, a full run, latest.json) and 2024 (32.5.0, this
# item and what it needs, sw2024/probe-results-20261114-014813) on 2026-11-14, with every
# decision the same. Each route ran on a two-gear gearbox of its own (17 and 68 teeth,
# module 1.5) built by assess, plan_gearbox and build_gearbox, saved, closed and opened
# again (every document then read GetSaveFlag False, as W4's a3 expects of a document
# just opened). Then: a raw Transform2 put turning G2 half a pitch and back; S2 X moved
# 63.75 -> 68.75 in the layout part's own document (opened by path, rebuilt there); G2
# given 69 teeth by update_variables in its own document; and G2's Bore Diameter set
# to 500, which failed its Bore cut (error code 1). After each, the route ran on the
# assembly, and the frame, the interferences, CreateMeasure from the layout's S2 Axis
# in the assembly to the assembly's Right plane, and every document's GetSaveFlag were
# read.
#
# What shows does not depend on the route: with every route, and with no rebuild at
# all, the put's frame read back, G2 half a pitch round clashed with G1 and was clean
# put back, the layout axis measured 68.75 mm from Right in the assembly, and the
# 69-tooth G2 at its old frame clashed with G1. What differs is what is marked and
# what is reported:
# - ForceRebuild3(False) marked G1, which nothing changed, and every other document
#   modified at the first step; the fault the rerun found.
# - ForceRebuild3(True) and EditRebuild3 marked exactly the documents changed on
#   purpose at every step (the assembly; then the layout; then G2), G1 never, both
#   before and after the interference check; and both returned False while G2 was in
#   error and True once it was put right. ForceRebuild3(True) is the app's existing
#   call with its one argument turned over, so it is taken.
# - With no rebuild the put did not mark the assembly modified at all (only the
#   interference check afterwards did), and nothing reports G2's failure; so a put is
#   always followed by the rebuild, though it shows without one.
# A Face Width of 0 failed nothing: G2's rebuild returned True with no feature error
# and the global was taken (as a negative layout global is, OFFSET_GLOBAL_CROSSES_ZERO).
ASSEMBLY_REBUILD_ROUTE = "ForceRebuild3(True)"
ASSEMBLY_REBUILD_TOP_ONLY = True          # the argument ForceRebuild3 takes for that route
ASSEMBLY_REBUILD_KEEPS_COMPONENTS_UNMODIFIED = True
FULL_ASSEMBLY_REBUILD_MARKS_COMPONENTS_MODIFIED = True   # ForceRebuild3(False): every component
PUT_NEEDS_REBUILD = False                 # to show; the rebuild still follows, for the mark and the report
PUT_MARKS_ASSEMBLY_MODIFIED = False       # a Transform2 put on its own
OPENED_READS_UNMODIFIED = True            # every document of an assembly just opened

# -- the workbook gearbox that turns (tier 8) --------------------------------
#
# Probe tier 8 (p8_motion), PLAN-WORKBOOK §4.4 / phase W5, which needs PLAN-GEARBOX's
# tier 6 items 3-5. Observed on SolidWorks 2026 (34.0.0, a full run, latest.json) and
# 2024 (32.5.0, tier 8 in a freshly restarted session, sw2024/probe-results-20261113-223412)
# on 2026-11-13, with every decision the same; the one difference (the mate error codes
# GetErrorCode2 gives) is noted where it bites. tests/test_findings.py pins each finding
# against both files.

# motion_enums, read from swconst.tlb after the reader gave back coincident 0,
# distance 5, angle 6 and gear 10.
MATE_CONCENTRIC = 1              # swMateType_e.swMateCONCENTRIC
MATE_LOCK = 16                   # swMateType_e.swMateLOCK
MATE_ALIGN_ALIGNED = 0           # swMateAlign_e
MATE_ALIGN_ANTI_ALIGNED = 1
ADD_MATE_NO_ERROR = 1            # swAddMateError_e.swAddMateError_NoError

# shaft_axis_mates: eight cylinders placed turned and fixed as W4 leaves them, on
# shafts along Z+ and Z-, then unfixed (UnfixComponent) and mated to their shaft's
# "<Shaft> Axis" in the body-less layout part. AddMate5(swMateCOINCIDENT, closest)
# between the gear's "Gear Axis" and the layout axis held it: no gear moved or turned
# over (closest kept a Z- gear anti-aligned: IMate2.Alignment read 0 on Z+, 1 on Z-),
# a Transform2 put turning it 25° about its axis stayed, and one moving it 5 mm off
# the axis, 5 mm along it, or tilting it 10° came back on the rebuild; the mates and
# frames came back unchanged after a save and reopen, with no mate error. The axes
# selected by FeatureByName + Select2, by SelectByID2 "<axis>@<component>@<assembly>"
# and by GetCorresponding of the part's feature + Select4 alike. A CONCENTRIC mate
# between the two axes was refused: AddMate5 returned nothing with status 0
# (swAddMateError_ErrorUknown), on Z+ and Z-. The cylinder's outside face concentric
# with the layout axis held too. Given explicitly, swMateAlignANTI_ALIGNED turned a Z+
# gear over and swMateAlignALIGNED a Z- one, so closest is what keeps W4's placing.
AXIS_MATE_ROUTE = "axis coincident"
AXIS_CONCENTRIC_REFUSED = True
# Along the shaft: a distance from the gear's origin (Point1@Origin, its front-face
# centre) to the layout's Front plane, |z| with Flip set when z < 0 (a point's distance
# is along the plane's normal, as nonparallel_mates found), held a gear at z = 5, -12
# and 8 on Z+ and Z-, and a coincident one at z = 0. The gear's Front plane at a distance
# from the layout's Front, Flip off, put it on the wrong side (12 and 14 mm off).
AXIAL_MATE_ROUTE = "origin distance"

# gear_mate_sense: nineteen pairs of cylinders and annuli on layout axes, mated as
# above, each joined by AddMate5(swMateGEAR) and its first gear driven 30° by an angle
# mate on one global. With Flip False every external pair turned opposite ways about
# +Z, at the ratio, whichever way the two shafts pointed (Z+ Z+, Z+ Z-, Z- Z+, Z- Z-),
# whichever number of the ratio was the bigger, and whether the gears' axes, their
# outside faces or one of each were selected; with Flip True, the same way. An annulus
# round a cylinder (a ring round its pinion) turned the SAME way as it with Flip False,
# ring selected first or second, on Z+ or Z-, axes or faces. AddMate5's alignment
# (aligned, anti-aligned or closest) changed nothing, and IMate2.Alignment read 2
# (closest) whatever was passed. So Flip False is the mesh's own sense, read from where
# the gears sit, and every mesh a workbook lists - outside or inside a ring, on any
# shafts - takes Flip False. What the mate keeps as IGearMateFeatureData.Reverse is
# about the selected axes' own senses instead: Flip, reversed once for opposed axes
# and once for a ring (with a face, its own sense). Two of the layout's own axes
# were refused as a gear mate's entities (AddMate5 returned nothing, status 0).
# What would break this: a pair SolidWorks cannot tell is inside a ring, which a
# meshing pair is not (the pinion's axis is inside the ring's bore, an external
# partner's outside the other gear); geometry not loaded (lightweight components) is
# untried.
GEAR_MATE_FLIP_RULE = "mesh"
GEAR_MATE_FLIP = False

# compound_lock: two cylinders on one layout axis, the second placed turned 37° (or
# 137°) from the first, the first driven 30° then 90° more. A LOCK mate
# (AddMate5(swMateLOCK) on the two components, each selected by IComponent2.Select4
# with a mark-1 select data) between the second and the first, the second not mated to
# the axis itself, held 37° through both drives on Z+ and on Z-, the second on the axis
# and with no mate error. With the second ALSO on the axis and along it, the lock held
# too, but its axial mates (and on Z- its axis mate) were flagged (GetErrorCode2 46,
# swFeatureErrorMateOverdefined, as a warning; on Z- both components read
# GetConstrainedStatus 4), so a locked gear is not mated to its shaft as well. An
# angle mate between the two Top planes at the placed angle held 37° and 137° without
# error; a 1 : 1 gear mate between the two axes held with Flip off and slipped with it
# on (a coaxial pair is read as one gear inside the other).
COMPOUND_LOCK_ROUTE = "lock alone"
# How an over-defined assembly shows (the same pair given a second angle mate 10°
# off the first): AddMate5's status out-parameter is 5
# (swAddMateError_OverDefinedAssembly) but the mate IS made; that mate's
# GetErrorCode2 is 47 (swFeatureErrorMateIlldefined, not a warning) and the mates it
# fights read 46 (overdefined, warning); the over-defined component's
# GetConstrainedStatus is 4; IModelDocExtension.GetWhatsWrongCount rose (6 to 8, and
# GetWhatsWrong, given three by-reference variants, named them); and ForceRebuild3
# still returns True. Deleted (Select2, then EditDelete(), as compound_lock's
# over_defined.deleted_by records; W5-PROBE-REPORT's "DeleteSelection2(0)" was a
# misstatement, and DeleteSelection2 was never reached), its errors went and
# the status was 3 again. SolidWorks 2024 flagged exactly the same mates, the same
# warnings and the same status, but GetErrorCode2 gave 51 for every one of them (the
# number swconst calls swSketchErrorExtRefFail) where 2026 gave 46, 47 and 1. So a
# build checks AddMate5's status, treats any non-zero GetErrorCode2 as a mate problem
# and IsWarning False as the mate at fault, and never reads meaning into the number;
# the rebuild's result says nothing.
ADD_MATE_OVER_DEFINED = 5        # swAddMateError_e.swAddMateError_OverDefinedAssembly
MATE_ERROR_OVER_DEFINED = 46     # swFeatureError_e.swFeatureErrorMateOverdefined (a warning); 2026 only
MATE_ERROR_ILL_DEFINED = 47      # swFeatureError_e.swFeatureErrorMateIlldefined; 2026 only
MATE_ERROR_2024 = 51             # what 2024 gave for each of the same mates
COMPONENT_OVER_DEFINED = 4       # IComponent2.GetConstrainedStatus, swConstrainedStatus_e
COMPONENT_FULLY_DEFINED = 3
COMPONENT_UNDER_DEFINED = 2

# mated_train: the 12 : 1 reducer (17/68 + 17/51) twice, all shafts Z+ and the middle
# shaft Z-, nine components: placed turned and fixed as W4 leaves them, then each gear
# unfixed and mated by the routes above (the second gear of each compound shaft locked
# to the first and not mated to its axis), the two gear mates with Flip False, and no
# gear moved (0 mm, 0 rotation). Every gear read GetConstrainedStatus 2 (under-defined)
# until one angle mate drove the input, which made all of them 3 (fully defined): the
# train has one degree of freedom. Driven 30°, each output turned 2.5° the same way as
# its input, 1/12, on both trains; saved, reopened (the same mates, no errors, every
# gear where it was) and driven again, the same. A gear mate follows the SOLVER, not a
# transform: turning the input by a Transform2 put, SetTransformAndSolve2 or
# IDragOperator (Drag or DragAsUI, every call answering True) turned the input alone,
# and a Transform2 put on the output turned it alone while the input stayed driven;
# IDragOperator's TransformType 1 and 2 and DragMode 0, 1 and 2 did no better. So no
# API drag reproduces a mouse drag, and W5's demonstrable (drag the input in
# SolidWorks) is seen by a person; the one degree of freedom and the 1/12 are
# measured here through the solver. The same on 2024.
MOTION_ROUTE = "mates"

# motion_update: the saved train, its output shaft swung 20° round the compound shaft
# by the layout part's two globals (the layout opened by path, activated, rebuilt; then
# the assembly rebuilt): the output gear went with its axis, nothing else moved, no
# mate error, and the train still turned 1/12. SolidWorks turned the output about +Z
# by -(1 + 17/51)·20° as its shaft swung, the opposite of the +(1 + 17/51)·20° staying
# in mesh needs, so after any move the app puts each gear back to the frame
# workbook.layout.frames gives. A Transform2 put turning the output with its gear mate
# on was kept (the rest of the train did not move) and the train then turned 1/12 from
# there: the gear mate takes the new phase. Suppressing the gear mate around the put,
# then unsuppressing it, kept the new phase too. A compound lock suppressed
# (SetSuppression2, this configuration), its second gear turned 11° by a put, and
# unsuppressed, held the new 11° through a drive. The output's axial distance mate
# (D1) linked to an assembly global and the global changed moved the gear along its
# shaft alone.
# W9 S0 read the unsuppress again for a user's lock (route (b) of ISSUE-1-PLAN's K2; W9-S0.md), on RangeBox, a
# gearbox with modes: run 1, SolidWorks 2026 34.1.1 at 55a82c1 (probe/results/w9-s0-sw2026-20261116-050200.log,
# w9-s0-20261116-045653.json, cases A-b and B-b), and 2024 32.5.0 at 423e227
# (probe/results/sw2024/w9-s0-sw2024-20261116-065000.log, case A-b, its put lines 974 and 989, "clean False"). The
# user's lock (Sprocket-1 to Sun, Sprocket-2 to RangeSlv) was suppressed in the mode around the app's put and turned
# back on, read back on in every configuration with code 0: the gear went back to its built frame and the sprocket
# stayed where the drive had left it, the lock keeping the new angle (Sprocket-1 37° from Sun after H's put, 74° after
# L's; on 2024 its pose in Sun's frame 0.60 and 0.96 off). What tier 8 did not hold: the angle kept is the mate's, so
# it reaches every mode: in the last read, each mode shown, A-b's Sprocket-1 stood 74° from Sun in H, N and L alike
# (the JSON's frames). This is why the app puts a user's locked component with its gear (USER_MATE_PUT_ROUTE).
LAYOUT_MOVE_CARRIES_MATES = True
MESH_PHASE_ROUTE = "Transform2 put with the gear mate on"
LOCK_UNSUPPRESS_KEEPS_THE_NEW_ANGLE = True
AXIAL_GLOBAL_MOVES_GEAR = True

# -- what W5 takes from tier 8, and tier 8 items 7-13 (W5-PLAN §0.3, package P0) --
#
# Six values read off tier 8's records as they stand (no new probe): motion_enums'
# motion_enum_values from swconst.tlb, the route motion_update suppressed and
# unsuppressed both its gear mate and its compound lock by (judged by IsSuppressed2),
# how compound_lock selected both components of every lock it made, and how it deleted
# the mate it over-defined the assembly with. Each matches W5-PLAN §0.3's text, in
# 2026's full runs and every 2024 file alike.
FEATURE_SUPPRESS = 0        # swFeatureSuppressionAction_e.swSuppressFeature
FEATURE_UNSUPPRESS = 1      # swFeatureSuppressionAction_e.swUnSuppressFeature
THIS_CONFIGURATION = 1      # swInConfigurationOpts_e.swThisConfiguration
SUPPRESSION_ROUTE = "SetSuppression2 this configuration, None"
LOCK_SELECT_ROUTE = "Select4 with a mark-1 select data"
MATE_DELETE_ROUTE = "Select2 then EditDelete()"

# Items 7-15, as probe round P0b left them (W5-DECISIONS, "Rulings on package P0's findings"), observed on
# SolidWorks 2026 (34.1.1: latest.json, a full run, probe-results-20261114-081921, 85 of 85) and 2024 (32.5.0,
# each in a SolidWorks started fresh for it: sw2024/probe-results-20261114-071324, items 7-14 and what they
# need, and sw2024/probe-results-20261114-073328, gear_mate_definition alone), every snapshot the app as of
# 64f4620 with the probes as of 4ced012, on 2026-11-14. Every decision is the same on both versions. Items
# 7, 8-11 each work on their own on-disk copy of the 12 : 1 train mated_train saved (all Z+, and with a Z-
# middle shaft); 7b and 13 build their own; each
# rebuilds with ForceRebuild3(True) as Update will, except where item 13 compares the routes. The earlier files
# (P0: latest.json's predecessors, sw2024/...-040636 and -051023) are kept: the 2024 ones ran beside an assembly
# the definition route had stranded.
#
# gear_mate_ratio (P1): the output's gear mate (17 : 51, made by AddMate5 with the first
# selection's count first) deleted (MATE_DELETE_ROUTE) and made again by AddMate5 between the
# two components found by GetComponentByName, at (17, 60), Flip False, given its old name: the
# output turned 17/60 of its partner (input 30°, output 2.125°, the other train still 2.5°),
# saved, closed, reopened, the same, closed; on both versions, the 2024 one in a clean
# session. The remade mate went to the end of the mate group (8th of 20 before, last after)
# and is found by its name all the same.
# gear_mate_update (P1b): an Update's whole tooth change, on W4's 12 : 1 reducer built by the
# app (assess, plan_gearbox, build_gearbox) and mated here as W5 will (anchors G1, G2, G4 on
# their axes and along their shafts, G4's distance on "G4 Face Z", G3 locked to G2, two gear
# mates, D12's names; the mate check clean, 1/12, no interference): G3 17 -> 18 and G4 51 -> 50
# (the same 68 mm centre distance) by swbuild.update_variables in each part's own document;
# every lock suppressed; "G3 meshes G4" deleted, made again at 18 : 50 and given its old name;
# every gear put to its new built frame (workbook.layout.frames); the locks back on; a top-only
# rebuild; the mate check clean, every gear at its frame to 1e-6, the train driven 30° (the
# demonstration's 90° drive) turning G4 2.7° (17/68 x 18/50) the same way and every gear back
# at its frame after, no interference at the built phase, and a full rebuild afterwards moving
# nothing. Closed without saving the assembly (the parts set back first, since the probe saves
# its parts on closing) and reopened: as it was saved, 17 : 51, the same frames and mates.
# Again, saved: reopened with 18 and 50 teeth, the frames, a clean check, 2.7° and no
# interference. The same on both versions. So D7 may be an Update, by the remake.
# The definition route (gear_mate_definition, last in the tier, recorded and never chosen):
# GetDefinition reads the counts the other way round from AddMate5 (GearRatioNumerator 51, the
# SECOND selection's), but the fields take them in AddMate5's order: 17 in GearRatioNumerator
# and 60 in GearRatioDenominator turned the train 17/60 and read back 60 : 17 (P0's 2026 full
# run also showed 60 in the field that read 51 inverting the ratio). On 2026 that copy closed;
# on 2024 it could not be closed: CloseDoc raised 0x80010105 ("the server threw an exception")
# and then, like QuitDoc, left it open without a word, holding the train's layout and part
# (sw2024/...-040636, -051023 and sw2024/probe-results-20261114-073328). AccessSelections does not exist on this
# definition (AttributeError).
GEAR_MATE_RATIO_ROUTE = "remake"
GEAR_MATE_RATIO_REMAKE_WORKS = True                 # on both versions, closing included
GEAR_MATE_UPDATE_HOLDS = True                       # P1b: the whole tooth change as an Update
REMADE_GEAR_MATE_GOES_LAST = True                   # in the mate group; found by name all the same
MODIFIED_GEAR_MATE_CLOSES_ON_2024 = False           # after ModifyDefinition on a gear mate
GEAR_MATE_RATIO_PUT_NUMERATOR_FIRST = True          # put: numerator = the first selection's teeth
GEAR_MATE_DEFINITION_READS_NUMERATOR_SECOND = True  # read: numerator = the second selection's teeth

# lock_retake_offset (P2): each compound lock suppressed (SUPPRESSION_ROUTE), its second
# gear put 3 mm along its own axis and 11° round, the lock unsuppressed and rebuilt: the
# second gear kept 11° and 3 mm against the first, on its axis, after the lock came back
# and after the anchor turned -7.5° under a drive, on the Z+ and the Z- compound shaft,
# no mate error. So a follower's At or face-width change is an Update (D8): the lock
# re-takes whatever relative frame it finds, along the shaft as well as round it.
LOCK_RETAKES_AN_OFFSET = True

# lock_mate_rename (M4a): a lock, a gear mate, an axis (coincident) mate, an axial
# distance mate, and the other train's lock suppressed first, renamed by an IFeature.Name
# put to "TG3 locked to TG2", "TG3 meshes TG4", "TG4 on T3 Axis", "TG4 along T3" and
# "UG3 locked to UG2": each read its new name back; nothing moved, and no mate's type,
# suppression or error code changed. Saved, closed, reopened: each was found by its new
# name through the MateGroup's sub-features and by IModelDoc2.FeatureByName, no old name
# was left, each was still its kind (IMate2.Type 16, 10, 0, 5, 16), the suppressed lock
# still suppressed and the others not; driven, the renamed lock held, the renamed gear
# mate turned the output 1/12, the renamed axis and axial mates held it; the suppressed
# lock, turned back on by its new name, held. So Update finds mates by W5's names.
MATE_RENAME_ROUTE = "IFeature.Name put"
MATE_FIND_ROUTE = "mate group"

# demonstration_drive (M4b): with tier 8's drives suppressed and each input put at its
# built phase (θ = 0), an angle mate from the input's Top plane to the layout's Right
# plane at 90°, its dimension linked to an assembly global, moved no gear and made every
# gear fully defined; the global 90 -> 120 turned each input +30° about +Z and each output
# +2.5°, on both trains; back to 90 every frame was where it was built (to 1e-13), and with
# the link equation and global deleted (IEquationMgr.Delete) and the angle mates deleted
# (MATE_DELETE_ROUTE) every frame still was, no mate error, every gear under-defined again.
# The 90° geometry behaves as tier 8's 10° -> 40° drive between Top planes did.
DEMONSTRATION_DRIVE_HOLDS = True
DEMONSTRATION_DRIVE_SENSE = 1    # the input (on Z+) turns +θ about +Z as the angle grows

# put_on_twice_meshed_gear (M4c): tier 8's records covered a put on the driven output
# (motion_update put_with_gear_mate_on), on the undriven input (mated_train dragged
# "Transform2 put") and on a follower under a suppressed lock in a driven train
# (lock_moved), not this. In the undriven train, every lock suppressed, rebuilt, the put,
# every lock unsuppressed and rebuilt (W5-PLAN §1.6 step 6): the compound anchor TG2
# (meshing TG1, locked to TG3 which meshes TG4) put 7° round held to 1e-6, nothing else
# turned and its lock took the new angle; every gear put back to where it started was
# there after the locks came back; TG4 joined to the other train's input by one more gear
# mate, so it carries two, put 9° round held and nothing else turned; no mate error, every
# gear under-defined, and one drive then made all eight fully defined and turned them as
# one train. Recorded beside it (lock_on_put_turns): a put on TG2 with its lock ON held too,
# TG3 did not follow and no mate reported an error. Then driven (lock_on_put_after_drive, P0b):
# TG2 and TG3 both turned -2.5° and their relative angle stayed where the put left it, no
# error: the lock takes the relative frame it finds, so a put with a lock on silently changes
# the pair's relation, which is why W5 puts only with every lock suppressed (M1, M8).
# The remake on a gear carrying two gear mates (P0b): TG3-TG4 deleted and made again at 17 : 60
# under suppressed locks and given its old name, while TG4 also carried the gear mate to the
# other train: found by its name and the other mate by its own, the joined train turning at the
# new ratio through both (UG1 -2.125° for TG1's 10°); the remade mate went to the end of the
# mate group (8th of 21 before, last after). The same on both versions.
# W9 S0 read the lock's re-take again for a user's lock left on through the app's put (route (a) of ISSUE-1-PLAN's
# K2; W9-S0.md), on RangeBox, a gearbox with modes: run 1, SolidWorks 2026 34.1.1 at 55a82c1
# (probe/results/w9-s0-sw2026-20261116-050200.log, w9-s0-20261116-045653.json, cases A-a and B-a), and 2024 32.5.0 at
# 423e227 (probe/results/sw2024/w9-s0-sw2024-20261116-065000.log, case A-a, its put lines 893 and 908, "clean False").
# Every put held, no mate read an error, and the user's sprocket stayed where the drive had taken it, its lock taking
# the new relation: Sprocket-1 37° from Sun after H's put and 74° after L's (each put adds to it), Sprocket-2 37° and
# 49.77° on RangeSlv; on 2024 Sprocket-1's pose in Sun's frame 0.60 and 0.96 off. What P0b did not hold: the relation
# re-taken is the mate's, so it reaches every mode: in the last read, each mode shown, A-a's Sprocket-1 stood 74° from
# Sun in H, N and L alike; and in C2, where Sprocket-1, locked to Sun, was tied to a fixed part in L only, H's put
# left L, shown next, with Sun at -37° and no error (the JSON's frames). So a user's lock is never left on
# through a put of its gear alone: the app puts the user's component with it (USER_MATE_PUT_ROUTE).
PUT_ON_TWICE_MESHED_GEAR_HOLDS = True
LOCK_RETAKES_AFTER_A_PUT = True                     # with the lock on: the pair's new relation is kept
REMAKE_ON_TWICE_MESHED_GEAR_HOLDS = True

# axial_datum_plane (M5): a plane in the layout part offset 1000 mm from Front with the
# flip bit (REF_PLANE_UNFLIPPED_IS_PLUS_Z: it landed at z = -1000, facing +Z), and an
# anchor on Z+ and one on Z-, each held by AXIS_MATE_ROUTE and by a distance from its
# origin (Point1@Origin) to that plane, Flip False (no anchor moved when mated), the
# distance linked to an assembly global. The global at 1000, 995 and back to 1017 put both
# origins at z = 0, -5 and 17 (through where the Front plane is, with no flip change),
# on their axes; both read under-defined, no mate error, and their 20 : 40 gear mate drove
# GB -15° for GA's 30°. Saved, reopened: where they were, moved to z = 8 by the global,
# and turning. So a datum plane far behind Front would remove D8's Front-plane cases (an
# anchor's front face reaching, leaving or crossing Front would be a global's new value).
# The user declined that route on 2026-11-14: W5 keeps the Front plane as the axial
# reference (W5-PLAN D8), and nothing is built on these two values; they stay as a record.
AXIAL_DATUM_ROUTE = "origin distance from a datum plane"
AXIAL_DATUM_FLIP = False

# mated_rebuild_scope (as probe round P0b rebuilt it): each route built its own train from its
# own layout part and gear part, with that route as its only assembly rebuild (Transform2 puts,
# then the route; mates; the output's axial distance on "TG4 Face Z"; the drive), and every
# build passed W5-PLAN §1.4's mate check (18 AddMate5 statuses 1, no mate error, every gear
# under-defined), one drive made every gear fully defined, both trains turned 1/12 the same
# way, and its frames were the full rebuild's build's to 1e-13. The full rebuild's build left
# its layout and part modified; the top-only and EditRebuild3 builds left them unmodified.
# Saved, closed, reopened (every document read GetSaveFlag False), each train took six changes
# under its route, each read once between the change and the route and once after it:
# - shown only by the route: the axial global +4 mm (0 before, 4 after) and the drive +30°
#   (nothing turned before, 1/12 after); and the compound anchor put 7° under its suppressed
#   lock held after the lock came back and the route (judged then: a reading straight after a
#   Transform2 put is the put's own value);
# - shown before any route (recorded, not counted): the output shaft moved in the layout's own
#   document (it had moved once ActivateDoc3 brought the assembly back), the gears' part's OD
#   (the volume read new before the route, though a mass property may itself update what it
#   measures), and the conflicting angle mate's errors (AddMate5 solves: status 5, errors 47 /
#   46 on 2026, 51 on 2024, before and after the route; deleted, cleared before the route).
#   No route returned False with the mate error;
# - driven 30° after the put, after the layout move and after the part change, under the route:
#   both trains 1/12, the put's lock angle kept, the output on its moved axis; every frame
#   the full rebuild's train's to 1e-13.
# ForceRebuild3(True) and EditRebuild3 marked exactly the documents changed on purpose at every
# step; ForceRebuild3(False) marked the layout and the part at the first step. NeedsRebuild and
# NeedsRebuild2 read True / 1 after an assembly global changed and False / 0 after every route;
# after a change in the layout's or the part's own document they read False / 0 before the
# route, on both versions. The P0 file's two 2024 differences (the layout move not shown before
# the route; NeedsRebuild True / 1 there) did not recur in a clean 2024 session: they were the
# stranded assembly's. So a train is built and changed with the top-only rebuild.
# What it was measured on, and so what it covers: the workbook TRAIN as W5 builds it, every
# gear's Gear Axis coincident with its layout "<Shaft> Axis", each anchor's origin a distance
# from the layout's Front plane (the output's linked to an assembly global), compound gears held
# by a lock mate alone, external gear mates (Flip False), and an angle mate between Top planes
# driven by an assembly global. It does NOT cover a gear-PAIR assembly (swbuild.build_pair, the
# p5 half-pitch controls): their centre-distance equation, mesh or shaft-angle mates and point
# mates were not measured here, and pairs keep the full rebuild.
MATED_ASSEMBLY_REBUILD_ROUTE = "ForceRebuild3(True)"
MATED_REBUILD_KEEPS_COMPONENTS_UNMODIFIED = True
MATED_BUILD_REBUILD_ROUTE = "ForceRebuild3(True)"      # building the train, with nothing else
MATED_BUILD_KEEPS_COMPONENTS_UNMODIFIED = True

# -- probe round P0c: what W5's build and Update code do that no probe had done -------------
# Evidence: probe/results/probe-results-20261114-095421.json (2026) and
# probe/results/sw2024/probe-results-20261114-102300.json (2024), each in a SolidWorks started
# fresh for it. The same on both versions except where a line says otherwise.

# gear_mate_update and idler_update (P1b, the review's additions). On W4's 12 : 1, every pass
# also read interference at the old frames before the put (4 clashes) and with G4 put half a
# pitch off its new phase (4), then 0 after the put: the interference reading tells. A train
# with an idler (17/30/40 -> 15/32/38, module 2, no shaft moved), built by the app and mated as
# W5 does, carried the change as an Update. Both of the idler's gear mates were deleted, made
# again at the new ratio and given their old names (found by name; they were last in the mate
# group already and stayed there). Only G2's built phase changes (-0.375°); G1's and G3's are
# the same before and after, so the put tells success from failure on G2 alone. Every gear
# stood at its new built frame to 8e-15. The check
# was clean and a full rebuild moved nothing. Driven 30°, G2 turned -14.0625° and G3 +11.842°.
# Interference was 0 after the put. At the old frames it was 0 too (a changed phase can happen
# to clear), and with G2 half a pitch off it was 6, so the half-pitch reading is the control.
# Closed unsaved and reopened, the train was as saved (17/30/40, the old definitions); saved and
# reopened, it had 15/32/38, ratios 32 : 15 and 38 : 32, the same turns and no interference.
IDLER_UPDATE_HOLDS = True
UPDATE_INTERFERENCE_CONTROL_HOLDS = True        # a gear half a pitch off clashes; at its built phase none

# unsaved_update_close: after an unsaved Update (G3 and G4 changed in their own documents, the
# assembly updated, nothing saved: the assembly and both parts GetSaveFlag True), CloseDoc on
# the assembly returned at once (0.34 s) with no window opened. The two parts stayed open,
# still modified, and CloseDoc on each closed it silently. On disk afterwards nothing had been
# written and the parts still had their saved teeth. QuitDoc did exactly the same. On 2024 too:
# no "Save Modified Documents" here. The earlier 2024 dialog (scaffold.save_created_parts,
# 2026-11-02, probe assembly_distance_link) was observed once and has not been reproduced since.
# There too the two parts were open in their own windows when the assembly closed (p4_assembly's
# _assembly before 4392c8b: each made by _part_with_axis, saved and left open, then the assembly
# closed first). So being open in their own windows is not the difference. The cases differ in
# how the parts came to be modified: there, through the assembly's full rebuild (ForceRebuild3(False))
# after a linked global changed; here, by edits in each part's own document. Which difference
# decides whether 2024 asks is not known.
UNSAVED_UPDATE_CLOSE_ASKS = False
UNSAVED_UPDATE_CLOSE_DISCARDS = True            # CloseDoc and QuitDoc alike, assembly first then each part

# gear_mate_definition_read: the saved 12 : 1 reopened, every document GetSaveFlag False. Each of
# its two gear mates read as the app's Update check reads it (IFeature.GetDefinition, then
# GearRatioNumerator and GearRatioDenominator, the object released; no ModifyDefinition, no
# AccessSelections), both in one session. The reads gave 68 : 17 and 50 : 18 (numerator the
# second gear's). Every flag stayed False after the get, after the reads and after the release,
# and the train then closed with nothing left. So an Update with nothing to do may read the
# ratios and still change nothing.
GEAR_MATE_DEFINITION_READ_MARKS = "nothing"

# origin_noise: each gear's origin read at full precision before and after ForceRebuild3(True)
# moved 0.0 mm after nothing, after a part's teeth changed by its globals, and after another
# shaft moved 1 mm by its layout global. That shaft's own gear had moved its full 1 mm by the
# first read, once the assembly was active again. After the temporary drive was added, driven,
# set back and taken away it also moved 0.0 mm; from before the drive to after it, the largest
# move was 2.8e-14 mm. So the app's 1e-6 mm "moved" tolerance sits eight orders above the noise.
ORIGIN_NOISE_MM = 0.0                           # around a top-only rebuild, every case
ORIGIN_NOISE_AFTER_A_DRIVE_MM = 2.8474599777423056e-14   # from before the drive to after its removal

# mates_under_command_in_progress: with ISldWorks.CommandInProgress True, the whole W5 mate set
# (18 AddMate5 calls) answered status 1, every mate code 0, every gear under-defined, none moved,
# one drive defined it and it turned 1/12. A conflicting angle mate under it answered status 5
# with the codes P0b saw (47 / 46 on 2026, 51 on 2024). Each mate renamed straight after its
# AddMate5, in a new unsaved assembly, read its new name back at once and was found by it; saved
# and reopened, every mate was found by its new name and no first name was left.
# SetSuppression2(unsuppress) on a lock already on returned True, left it on, raised no error,
# and marked the assembly modified. The mark is the call's own (P0d): every GetSaveFlag read
# straight before it and straight after, nothing between, went from False to True for the
# assembly alone (the layout and part stayed False). Suppressed, a sound lock and a conflicting angle mate both
# read GetErrorCode2 0 with the warning flag False.
MATES_UNDER_COMMAND_IN_PROGRESS = True
MATE_RENAME_AT_ONCE = True
UNSUPPRESS_ON_LOCK_ALREADY_ON_MARKS_MODIFIED = True
SUPPRESSED_MATE_ERROR_CODE = 0                  # warning flag False, whatever the mate would report on

# mate_folders: IFeatureManager.InsertFeatureTreeFolder2(swFeatureTreeFolder_Containing = 2) with
# two mates selected made a folder in the mate group. The MateGroup walk then lists the folder
# (GetTypeName2 "FtrFolder"), the mates inside it as ordinary following siblings, and an end
# marker "Folder1___EndTag___" (also "FtrFolder"). FeatureByName finds a mate inside it. Every
# type met: FtrFolder, MateCoincident, MateDistanceDim, MateGearDim, MateLock,
# MatePlanarAngleDim. A walk that keeps only types starting with "Mate" skips both folder
# entries and still sees every mate.
# P0d: the same held in every case walked. With a folder inside the folder holding a mate (made
# by the same call, the mate inside selected), the walk reads the outer folder, its mate, the
# inner folder, its mate, "Folder2___EndTag___", then "Folder1___EndTag___". Saved under its own
# name, closed and reopened, the walk read the same and FeatureByName found both mates. The outer
# folder suppressed by SetSuppression2 (the call that suppresses a mate) suppressed both mates in
# it (IsSuppressed2 True), and the walk still listed them; unsuppressing it brought both back with
# no error. So a walk on a reopened assembly sees every mate, however deep the folders. A mate
# in a suppressed folder reads suppressed, so a walk must read IsSuppressed2 on each mate.
MATE_FOLDER_ROUTE = "IFeatureManager.InsertFeatureTreeFolder2(swFeatureTreeFolder_Containing)"
MATE_FOLDER_TYPE_NAME = "FtrFolder"
MATE_GROUP_WALK_SEES_MATES_IN_A_FOLDER = True    # one folder, nested folders, reopened, folder suppressed
MATE_FOLDER_SUPPRESSION_SUPPRESSES_ITS_MATES = True

# lightweight_remake: OpenDoc6 with swOpenDocOptions_LoadLightweight (128) alone left every
# component swComponentFullyResolved. Adding swOpenDocOptions_OverrideDefaultLoadLightweight
# (64) made all eight swComponentLightweight. On both versions the SOLIDWORKS CAM add-in then put
# up a modal "SOLIDWORKS CAM Error" box ("...loading of lightweight parts has been detected"),
# which blocks OpenDoc6 until it is closed: the probe's watch closed it with WM_CLOSE.
# P0d read every gear's IComponent2.GetSuppression2 at each step. After the open, and after
# FeatureByName("Gear Axis") found the axis on two of them, every gear read 1
# (swComponentLightweight). The first drive, 30° on the input, read TG4 as turned -24.17° where
# 2.5° is right (TG1-TG3 and the other train right). After that drive every gear read 2
# (swComponentFullyResolved). The drive is one step to the probe: every frame read, the global
# set, a top-only rebuild, every frame read again. Which of these resolves was not separated, and
# the wrong turn may be a stale frame read while lightweight rather than a wrong solve. So the remake ran on resolved components: it made the gear mate
# (status 1, no error) and the train turned at the new ratio (TG4 2.125° for 30°), still 2 after.
# "Holds" therefore means: once resolved, not while lightweight. A lightweight train must not be
# driven or judged before its components read fully resolved. W5 does not open lightweight; if it
# ever does, the add-in's box must be expected.
LIGHTWEIGHT_FORCED_BY = "swOpenDocOptions_LoadLightweight | swOpenDocOptions_OverrideDefaultLoadLightweight"
LIGHTWEIGHT_REMAKE_HOLDS = True                 # on components already resolved by the first drive
LIGHTWEIGHT_FIRST_DRIVE_RIGHT = False           # TG4 -24.17° where 2.5° is right, on both versions
# The first drive (frame reads, a global set, a top-only rebuild); which of these resolves was not
# separated, and the wrong turn may be a stale frame read rather than a wrong solve.
LIGHTWEIGHT_RESOLVED_BY = "the first drive"

# The read an Update gates on (P0d, package A): IComponent2.GetSuppression2 of each gear
# component. After a plain OpenDoc6 (silent, no lightweight option: this machine's default) every
# gear read 2, swComponentFullyResolved, on both versions; lightweight read 1. Only 2 was seen
# for a resolved gear (swComponentResolved, 3, never came), so 2 alone means fully resolved.
COMPONENT_RESOLVED_ROUTE = "GetSuppression2"
COMPONENT_FULLY_RESOLVED_STATES = (2,)
LIGHTWEIGHT_OPEN_RAISES_AN_ADDIN_DIALOG = True  # SOLIDWORKS CAM, modal, on this machine's install
# The same add-in boxes a save: in W9a's demonstration on 2026 (34.1.1, snapshot 9dded70), the script's own SaveAs3
# of an assembly holding a lightweight component raised the modal Yes/No "SOLIDWORKS CAM Warning" ("SOLIDWORKS CAM
# data cannot be stored as lightweight parts have been detected"), and the session hung behind it
# (probe/results/w9a-demo-sw2026-20261116-2-m1-refuse-stopped-by-a-dialog.log lines 354-355, the hang 358-362).
# One occurrence, never answered: what Yes or No does, and whether the save completes, were not seen. No app code
# reads it: the Update never saves, and Build again saves only a new revision, which holds none of the user's work.
LIGHTWEIGHT_SAVE_RAISES_AN_ADDIN_DIALOG_ON_2026 = True
LIGHTWEIGHT_SAVE_RAISES_AN_ADDIN_DIALOG_ON_2024 = None

# second_assembly_beside_unsaved: a new assembly left open and unsaved ("Assem20"), holding a
# component of a saved part with its mate. A second new assembly ("Assem21") from the same part
# took the same component name, its mate, and saved to its path under the file's name. There
# was no dialog, no refusal and no name clash, and both closed afterwards.
SECOND_ASSEMBLY_BESIDE_UNSAVED_HOLDS = True

# drag_operator_turns_train (optional): the saved 12 : 1 trains, undriven (both drive mates
# suppressed, so nothing held the input but its gear mates), dragged by
# SW-Macro-Database entries/assemblies/05's recipe: AddComponent(gear, False), TransformType 0,
# UseAbsoluteTransform False, DragMode left at 3, BeginDrag, Drag with a relative turn per step
# about the gear's own axis, EndDrag. It was dragged 10°, since 30° on the output would turn the
# input 360°. Every Drag returned True. The output (10 steps, the entry's success; then 1 and 30
# steps), the input and the compound follower each turned exactly 10° and every other gear 0°.
# No mate reported an error, nothing was left selected and CommandInProgress read False. Not
# varied: the mate holding a gear to its axis (W5's axis coincident; the entry's held case was
# concentric to sketch points). So the demonstration keeps its temporary driving mate.
DRAG_OPERATOR_TURNS_TRAIN = False

# -- ring_mate_sense: which way a gear mate turns an app-built ring (W5 demonstration, m3) --------
# Evidence: probe/results/probe-results-20261114-133014.json (2026) and
# probe/results/sw2024/probe-results-20261114-135104.json (2024), each in a fresh session.
# The Risky_Placements train, built by the app from its fixture workbook and mated as the app mates
# it (G5 on Z+ selected first, ring G6 on Z-, ratio 14 : 36, Flip False), turned G6 the wrong way
# on 2026. Driven 10° off the built phase, G5 and G6 clashed 5 times. On 2024 it turned the right
# way and stayed clear, as in the demonstration.
# The case table had 52 mates, each a pinion selected first or a ring selected first, with Flip
# False or True. The pairs were the app's toothed spur and 20° helical ring pairs on every
# combination of pinion and ring shaft sense; gear_mate_sense's plain annulus and cylinder on the
# same shafts and frames; and an external pair on opposite shafts. Every pair turned at its ratio.
# Which gear is selected first never changed the Flip a pair needs. The plain annulus needed
# False everywhere, and so did the external pair, on both versions (gear_mate_sense's reading).
# Every toothed ring needed the OPPOSITE Flip on the two versions, below. So no rule from what the
# app knows before it makes the mate (inside or outside, both shaft senses, which gear first,
# spur or helical) is right on both versions. GEAR_MATE_FLIP = False is right for outside pairs and
# the plain annulus on both versions. On 2026 it is wrong for every helical ring and for spur rings
# on same-sense shafts (++, --). On 2024 it is right for helical rings and spur rings on same-sense
# shafts, but wrong for spur rings on opposite shafts (+-, -+). So the app's Flip False gives a
# wrongly turning ring on BOTH versions, only for different rings.
GEAR_MATE_FLIP_NEEDED_ON_2026 = {
    "spur ring ++": True, "spur ring +-": False, "spur ring -+": False, "spur ring --": True,
    "helical ring ++": True, "helical ring +-": True, "helical ring -+": True, "helical ring --": True,
    "plain annulus": False, "external +-": False}
GEAR_MATE_FLIP_NEEDED_ON_2024 = {
    "spur ring ++": False, "spur ring +-": True, "spur ring -+": True, "spur ring --": False,
    "helical ring ++": False, "helical ring +-": False, "helical ring -+": False, "helical ring --": False,
    "plain annulus": False, "external +-": False}
GEAR_MATE_FLIP_STATIC_RULE = None   # none is right on both versions for an app-built ring

# What SolidWorks reports once the mate is made does tell which way it turns, on both versions and
# in every case: the 52, plus the Risky pair before and after its remake. A gear mate turns its
# gears as they mesh exactly when IGearMateFeatureData.Reverse (read through IFeature.GetDefinition)
# equals whether its two MateEntity directions (IMateEntity2.EntityParams 3..5) point the same way,
# for a pair with a ring; for an outside pair, exactly when the two differ (decide.read_back_says_right).
# The versions store a different Reverse for the same toothed-ring call (they decide differently
# whether it is inside a ring), and the read-back follows what they decided.
GEAR_MATE_SENSE_READ_BACK = "(Reverse == entities parallel) == internal"
# What it rests on (each against the drive's sense and, for toothed pairs, interference off the built
# phase):
# - ring_mate_sense: 52 mates per version, plus the Risky pair before and after its remake;
# - ring_trains_saved: 13 meshes per version (2024: probe-results-20261114-151013 in sw2024; 2026:
#   probe-results-20261114-162034), read straight after AddMate5, after the top-only rebuild, after any
#   remake and after a save and reopen;
# - the Risky ring remade at 15 : 37 in an Update's shape;
# - ring_trains_from_another_version: the 13 meshes 2024 saved, opened in 2026.
# The cases: toothed spur rings on all four shaft-sense combinations; 20° left- and right-hand, 15°
# and herringbone helical rings; a spur ring with a -0.3 shifted pinion; the external pair on all
# four combinations; the plain annulus; Risky's train (helical and herringbone outside meshes and its
# ring). All with axis-to-axis gear mates and CLOSEST alignment, as the app makes them.
GEAR_MATE_READ_BACK_TELLS_SENSE = True

# Physical evidence: driven 10° off the built phase, every toothed pair stayed clear exactly when
# its sense was right; the wrong sense clashed (3 interferences for a spur ring, 4 for a helical
# ring, 2 for the external pair). At the built phase every toothed pair was clear.
WRONG_GEAR_MATE_SENSE_CLASHES = True

# The fallback, on the Risky train:
# - A temporary drive (the demonstration's, 10°) judges each mesh by the sign of its driven gear's
#   turn. It is set back and taken away, and every frame comes back to 1.1e-10.
# - A wrong gear mate is remade with the other Flip (G5 meshes G6 on 2026; nothing on 2024).
# - The result is the right-first-time train: frames 2.3e-10 apart on 2026 (1.1e-10 on 2024), the
#   same mates in the same order once the remade one is counted last, no mate error, and the layout
#   and every part unmodified (only the assembly marked).
GEAR_MATE_CHECK_AND_REMAKE_HOLDS = True

# -- the read-back's footing (ring_trains_saved, ring_trains_from_another_version) -------------------
# Evidence:
# - 2024: probe/results/sw2024/probe-results-20261114-151013.json;
# - 2026: probe/results/probe-results-20261114-162034.json (ring_trains_saved);
# - 2026: probe/results/probe-results-20261114-162546.json (the 2024 trains opened in 2026).
# Each run was in a fresh session.

# On each saved train, reopened with every document GetSaveFlag False, each gear mate was read as the
# app reads it, and every save flag was read straight before and after each read. The reads were
# GetDefinition (Reverse, numerator, denominator), then GetSpecificFeature2, MateEntity(0 and 1) and
# EntityParams. No flag changed, on 3 trains and 13 gear mates, on both versions. So an Update's
# check phase may read the sense of every recorded gear mate before anything changes.
GEAR_MATE_SENSE_READ_MARKS = "nothing"

# On copies of the static Risky and pairs assemblies (G5 meshes G6, and the external ++ pair), the
# app's Build steps were run with CommandInProgress True and no rebuild between: make the gear mate,
# rename it, read it back, delete it (Select2 then EditDelete), make it again with the other Flip,
# rename it, read it back. Then CommandInProgress went off, a top-only rebuild, a read and a drive.
# On both versions the read of the remade mate under CommandInProgress equalled the read after the
# rebuild and told the drive's sense. The first mate was deleted before any rebuild or drive, so
# it was never driven: its read is taken as right because it equals the same read with
# CommandInProgress off and is the opposite of the remade mate's, and CommandInProgress read True
# at the reads. The same steps with it off left the same mates by name and order, the same frames
# (0.0 apart), the same reads and the same drive, with no mate error. On 2024 the remake under
# CommandInProgress only ever went from a right mate to a wrong one; the app's direction, wrong to
# right, was shown under it on 2026 only (the Risky ring). The existing reads straight after
# AddMate5 (below) ran with CommandInProgress off.
GEAR_MATE_SENSE_READ_UNDER_COMMAND_IN_PROGRESS = True
GEAR_MATE_REMAKE_UNDER_COMMAND_IN_PROGRESS = True

# The read point. Every gear mate of the three trains was read straight after the AddMate5 calls
# (before any rebuild, CommandInProgress off), after the top-only rebuild, straight after any remake,
# and after a save, close and reopen. At each point it told the sense the drive found, as made and
# at the end, on both versions (13 meshes each). So reading after the rebuild, or on a reopened
# assembly, gives the same answer as reading straight after AddMate5.
GEAR_MATE_SENSE_READ_POINTS_AGREE = True

# More static cases, the Flip each needed (selected pinion first, Flip False as made):
# - the external pair on same-sense and opposite shafts: Flip False on both versions, as +- did;
# - the other rings, on Risky's shaft senses (pinion Z+, ring Z-): the right-hand 20°, 15° and
#   herringbone helical rings need Flip True on 2026 and False on 2024, like the 20° left-hand ring;
# - the spur ring with a shifted pinion needs Flip False on 2026 and True on 2024, like the plain
#   spur ring +- (that pair was run at 22 mm, 0.552 mm inside its working distance).
# The read-back told every one.
GEAR_MATE_FLIP_NEEDED_MORE_ON_2026 = {
    "external ++": False, "external --": False, "external -+": False,
    "helical ring right +-": True, "helical ring 15 +-": True, "herringbone ring +-": True,
    "spur ring shifted pinion +-": False}
GEAR_MATE_FLIP_NEEDED_MORE_ON_2024 = {
    "external ++": False, "external --": False, "external -+": False,
    "helical ring right +-": False, "helical ring 15 +-": False, "herringbone ring +-": False,
    "spur ring shifted pinion +-": True}

# A ring mesh remade at a new ratio in an Update's shape: the Risky train's G5 14 -> 15 and G6
# 36 -> 37 through the parts' globals, every lock suppressed, the gear mate deleted and made again
# with Flip False, every gear put to its new built frame. On 2026 it read wrong; remade with Flip
# True it read right. On 2024 it read right. Driven, every mesh turned right with no clash, on both.
GEAR_MATE_READ_BACK_HOLDS_AFTER_A_RATIO_REMAKE = True

# The 2024-saved trains (Risky, pairs, geometry; each mated right on 2024) opened in 2026.
# - Every document read GetSaveFlag False on open and after the read-back.
# - Every gear mate kept the Reverse 2024 stored, the read-back said right, and the drive turned
#   all 13 meshes right with no clash: the stored mate carries its sense across, and 2026 does not
#   re-decide on open.
# - No remake was needed.
# - Closing a modified 2024 assembly in 2026 by CloseDoc put up the SOLIDWORKS CAM add-in's modal
#   "Save changes to ...?" box, Yes and No only, which ignores WM_CLOSE and Escape. It was answered
#   No, and every file on disk was left as it was.
CROSS_VERSION_RING_TURNS_RIGHT = True
CROSS_VERSION_READ_BACK_TELLS_SENSE = True
CROSS_VERSION_CLOSE_ASKS_TO_SAVE = True        # the CAM add-in's Yes/No box, on this machine's 2026

# -- turned_gear_mate_sense: a gear mate's sense between non-parallel axes (W6-PLAN §7.2, probe tier 9) ----------
# Evidence: probe/results/probe-results-20261114-195608.json, SolidWorks 2026 34.1.1, one round in a fresh session;
# 2024 is confirmed at W6's end (r1, r3, r5).
#
# The rig was two cylinders standing for a 20- and a 40-tooth gear, radius 10 and 20, each 10 long on its own +Z
# side. Each was held by W5's anchor mates to a frame axis: the A axis along Z, and the B axis from one sketch line.
#
# Cases (44 gear mates in 22 assemblies, both Flips each):
#   meeting axes   30°, 60° and 90°, every facing (own-axis angles 30, 60, 90, 120, 150)
#   skew axes      60° and 90°, both hands of crossing, facings (+,+) and (+,−) (own-axis angles 60, 90, 120)
#   controls       parallel and anti-parallel
#
# Every gear mate was made under CommandInProgress with ratio 20 : 40 and read straight after: Reverse and both
# EntityParams, each entity matched to its cylinder by axis. Each was then judged by a 30° drive: the sign of each
# cylinder's turn about its own +Z.
#
# Results:
# - In all 40 turned mates the mate turned its two cylinders the same way about their entities' own directions
#   exactly when Reverse was True. This is H: m = (+1 if Reverse else −1)·τA·τB, with τ = sign(entity·own +Z).
# - In every geometry exactly one Flip turned right, and H called that one right and the other wrong.
#   - Right for meeting axes means opposite turns about the own axes.
#   - Right for skew axes means the sense a crossed helical pair of the crossing's hand needs, in gears/crossed.py's
#     convention. At 90° either hand fits and the right hand was taken; H told the measured sense either way.
# - The four controls agreed with W5's rule and with H.
# - Reopened, M90 ++, M60 +−, K90 +Y ++ and K60 −Y ++ read and drove as when first made.
# - Every AddMate5 returned status 1 and every ratio held at 0.5 to 1e-6.
# - Neither of the alternatives decide.py would have tried tells the cases: Reverse against the sign of dA·dB, and
#   Reverse against the crossing.
#
# Bounds, read per class of mesh (W6-INTERFACES §7.12), each the least and greatest own-axis angle at which every
# case of the class held:
# - TURNED_GEAR_MATE_SENSE_ANGLES covers axes that MEET: they ran at 30, 60, 90, 120 and 150°, and the angles between
#   are taken as covered.
# - TURNED_GEAR_MATE_SENSE_ANGLES_SKEW covers axes that do not meet: skew cases ran only at 60, 90 and 120°.
# - The app refuses a turned mesh outside its class's range.
# - Not covered: real teeth (E's interference controls confirm it, M2), and a remake at a new ratio on a turned mate.
#
# Caveats (tier 9's review):
# - In all 44 cases each mate entity pointed along its own cylinder's +Z (τA = τB = +1), so the per-entity sign τ
#   in H was never exercised.
# - The probe's own verdict fact reads None in the result file. The finding comes from decide.py re-judging the raw
#   readings after c2fbaca, and the reviewer recomputed all 44 cases independently by hand with the same result.
# - "Right" for a skew case is set by a virtual crossed pair from gears/crossed.py. Tier 9 shows H reads the
#   measured sense, not that the app's mesh sense k is right for a crossed mesh; the demonstration's interference
#   controls with real teeth carry that.
# - Plain cylinders, on SolidWorks 2026 only.
TURNED_GEAR_MATE_SENSE_READ_BACK = "entity senses"
TURNED_GEAR_MATE_SENSE_ANGLES = (30.0, 150.0)
TURNED_GEAR_MATE_SENSE_ANGLES_SKEW = (60.0, 120.0)
# Recorded, nothing branching on them: no cylinder moved when a turned gear mate was made (1e-6 mm, 1e-6 per rotation
# entry), and MateEntity(0) was the first selection in all 40 turned mates. The app matches by axis either way (S1).
TURNED_GEAR_MATE_MOVES_ON_MAKE = False
GEAR_MATE_ENTITY_ORDER = "first selection first"

# -- W8: sleeves and modes. The W8 spike (probe w8_modes_spike) and its follow-up (w8_followup), W8-SPIKE.md --------
#
# Both probes ran on SolidWorks 2026 (34.1.1) and on SolidWorks 2024 (32.5.0), each in a session started fresh for it:
#   probe/results/w8-spike-20261114-204436.json            probe/results/sw2024/w8-spike-20261114-232510.json
#   probe/results/w8-followup-20261114-205913.json         probe/results/sw2024/w8-followup-20261114-233330.json
# What they built:
# - Parts: the app's own spur (30 teeth, module 1.5, face 10) as anchor A and dog D, and its internal spur ring of 30
#   teeth as sleeve S. Not W8's sleeve and dog kinds, which did not exist yet.
# - The layout: A Axis and D Axis on one line along +Z. A and D held as W5 holds an anchor (AXIS and ALONG), and S
#   on A Axis only. The follow-up adds F, a third spur on its own axis, AXIS and ALONG, with no gear mate anywhere.
# - Every gear mate was made at 1 : 1 under CommandInProgress, renamed at once and read straight after. The drive
#   is W5's temporary angle mate on A, 90 -> 120.
# Every value below is the same on both versions, except the collinear spline's Flip. decide.py derives each from
# the four result files (decide.w8_findings), and tests/test_findings.py pins each against them.
#
# The collinear 1 : 1 gear mate (the SPLINE S-A and the COUPLE S-D; W8-PLAN J8):
# - AddMate5 returned 1 for each.
# - Nothing moved when one was made (0 mm), and S stayed under-defined (2), free to slide.
# - Driven 90 -> 120, one Flip turned S +30 with A and the other turned it -30.
# - Both W5's rule ((Reverse == entities parallel) == same way) and H named the right one. The coupling read same
#   way and drove A, S and D each +30.
# - THE RIGHT FLIP DIFFERS between the versions for the spline: False on 2026, True on 2024. The coupling's was False
#   on both. So no Flip is assumed for a spline or a coupling; each is settled by the read-back.
# Not covered: τ was +1 for both entities in every case (both along +Z), so the per-entity sign was never exercised.
COLLINEAR_GEAR_MATE_SENSE_READ_BACK = True
# Recorded, nothing reads them: the Flip the spline needed, and that a collinear gear mate moved nothing on make.
COLLINEAR_GEAR_MATE_FLIP_NEEDED_ON_2026 = False
COLLINEAR_GEAR_MATE_FLIP_NEEDED_ON_2024 = True
COLLINEAR_GEAR_MATE_MOVES_ON_MAKE = False
# The slide under the spline (spike step 4):
# - A distance mate from S's origin to the layout's Front, linked to a global, was moved 10 -> 20.
# - S moved +10.0 mm along the axis and 0.0 off it. Its turn relative to A changed by 0.0°, with no mate error.
# - The spline still read right, and the drive still turned S with A.
# The follow-up's single per-configuration slide (below) held too.
COLLINEAR_GEAR_MATE_HOLDS_SLIDE = True
#
# Configurations (spike step 6 and its reopen):
# - X and Y were added with AddConfiguration2(name, "", "", 0, "", "", True): each returned an IConfiguration and
#   activated itself, read back by ConfigurationManager.ActiveConfiguration.Name.
# - ShowConfiguration2 X -> Y -> X returned True each time, and the active name read back as shown. It returns False
#   when the configuration is already active (seen on the reopened file), so success is judged by the name.
# - A top-only rebuild (ForceRebuild3(True)) after each show was enough: S stood at its configuration's slide (10,
#   30, 10 mm), with no mate error, and the drive turned D in X and left it still in Y.
# - DeleteConfiguration2 of the template's "Default", with X active, returned True, and the names read back
#   ["X", "Y"].
# - SetSuppression2(0 or 1, 3, VT_ARRAY|VT_BSTR names) returned True each time after a rebuild. IsSuppressed2(3,
#   names) gave one flag per name, in order, as set: unshown, after every show, after the delete, after reopening.
# - No add, show or delete brought up any window, under the dialog watch.
# Not covered here: showing a configuration whose mates over-define it (W8-PLAN's tier 9 item 1, measured since by
# tier 11: CONFIGURATION_SHOW_OVER_DEFINED below); more than three configurations; the template holding a
# configuration of a mode's name.
CONFIGURATION_ADD_ROUTE = "AddConfiguration2(name, '', '', 0, '', '', True)"
CONFIGURATION_SHOW_ROUTE = "ShowConfiguration2, active name read back"
CONFIGURATION_DELETE_ROUTE = "DeleteConfiguration2, names read back"
SPECIFY_CONFIGURATIONS = 3                      # swInConfigurationOpts_e.swSpecifyConfiguration (motion_enums' read)
MATE_SUPPRESSION_PER_CONFIGURATION_ROUTE = "SetSuppression2(action, 3, names) after a rebuild; IsSuppressed2(3, names)"
CONFIGURATION_SHOW_RAISES_DIALOG = False
# The first two SetSuppression2 calls made straight after AddConfiguration2, with no rebuild between, failed in all
# five spike runs that reached them (four on 2026: three attempts and the passing run; one on 2024):
# - the first raised 0x80010105, yet took effect;
# - the second returned False and did nothing.
# The follow-up rebuilt after adding its configurations, and both of its calls returned True on both versions.
# So: rebuild first, never trust the return value, and read every flag back.
SUPPRESSION_RIGHT_AFTER_ADD = "unreliable"
# A mate made while Y was active, with Default, X and Y present, came out suppressed in Default and on in X and Y:
# neither "on everywhere" nor "only here". Every flag is set explicitly for that reason.
NEW_MATE_IN_OTHER_CONFIGURATIONS = "suppressed in the template's, on in the others"
#
# Component handles:
# - After every AddConfiguration2 and ShowConfiguration2, every IComponent2 held from before answered Transform2
#   with None and IsFixed with False, including the fixed layout's: a wrong answer, not an error.
# - Handles fetched again by GetComponentByName (COMPONENT_FIND_ROUTE) answered correctly: Transform2, IsFixed,
#   GetModelDoc2 and Name2.
# - Handles held across DeleteConfiguration2 of a configuration not active stayed good.
# Not covered: on 2026 a fresh handle once answered GetModelDoc2 with None and once Name2 with "", in two of the
# spike's attempts (logs kept beside it), and never in any run since. The app selects by held names.
HANDLES_STALE_AFTER_CONFIGURATION_CHANGE = True
# The layout read IsFixed True in each new configuration through a fresh handle: AddConfiguration2 carries a
# component's fixed state over.
FIXED_KEPT_IN_NEW_CONFIGURATION = True
#
# Marks and saving, read on the reopened spike, when every document read unmodified:
# - The configuration names, every IsSuppressed2(3, names) flag and both gear mates' sense read-backs marked
#   nothing.
# - ShowConfiguration2 marked the assembly, before any rebuild, and no part.
# - The follow-up's GetSystemValue3(3, names) on its reopened file marked nothing.
# - The save (SaveAs3, silent) of the assembly with several configurations brought up no window.
# - Closing it unsaved after a switch (CloseDoc) asked nothing and discarded the switch, as W5's unsaved Update
#   close does.
# - It reopened in the configuration active at the save, X, twice, every document unmodified.
# Not covered: whether a suppressed gear mate's sense read marks anything, which was read only on the unsaved
# assembly, already modified, so W8-PLAN's SUPPRESSED_GEAR_MATE_SENSE_READ is not set; it answered there.
SUPPRESSION_READ_MARKS = "nothing"
CONFIGURATION_SHOW_MARKS = "assembly"
VALUE_READ_MARKS = "nothing"
MULTI_CONFIGURATION_SAVE_ASKS = False
REOPENS_IN_SAVED_CONFIGURATION = True
#
# A slide's distance per configuration (the follow-up's A):
# - S had one distance mate from its origin to the layout's Front, typed at 10 mm, with no global. Its D1 took a
#   value per configuration by IDimension.SetSystemValue3(m, 3, [name]), which returned 0 (swSetValue_Successful).
# - GetSystemValue3(3, names) read Default 10, X 10, Y 30 as typed, without activating any configuration.
# - S stood at 10, 30 and 10 mm on the shows X, Y, X.
# - Y was set to 35 while X was active (returned 0): X's sleeve did not move, and Y then showed 35.
# - Saved and reopened, the values read 10, 10, 35, and S stood at 10, 35 and 10 mm.
# - The signatures were read from sldworks.tlb, and swSetValue_InSpecificConfigurations = 3 from swconst.tlb.
# Not covered: a slide at the Front plane (distance 0); a slide not along +Z; more than one slider. IEquationMgr.Add2
# linking a second slide's D1 to a global with several configurations present returned -1 on both versions
# (W8-SPIKE.md), which is why the app sets values per configuration and keeps no slide global.
SLIDE_VALUE_ROUTE = "SetSystemValue3(m, 3, [configuration]); GetSystemValue3(3, configurations)"
SET_VALUE_IN_SPECIFIC_CONFIGURATIONS = 3        # swSetValueInConfiguration_e.swSetValue_InSpecificConfigurations
SLIDE_VALUE_PER_CONFIGURATION_ON_2026 = True
SLIDE_VALUE_PER_CONFIGURATION_ON_2024 = True
# Before any configuration had its own value, GetSystemValue3 read 0 for every configuration not active (Default 0,
# X 0, Y 10 with Y active), so every configuration's value is set explicitly before one is read.
VALUE_UNSET_READS_ZERO = True
# Recorded, nothing reads it: IDimension.SystemValue on the handle read 30 in X while S stood at 10. It does not
# follow the shown configuration; only GetSystemValue3 with the name does.
SYSTEM_VALUE_FOLLOWS_CONFIGURATION = False
#
# Positions per configuration, what a put that moves a body does elsewhere. Read, not a rule:
# - W8 s7 (SolidWorks 2026 34.0.0, this host, fresh copies of the built E4; probe/results/w8-s7-20261115-135428.json,
#   case 5): FIdler turned +20° in N and +10° in 4H by a plain Transform2 with its mates on, and FDrive moved 2 mm
#   along its axis in 2H by the app's put route; each kept its place in the configuration showing alone, through a
#   save and reopen. In the s2 rerun (…-132348-s2-put-kept-per-configuration.log) the app's puts in 4L and 4H, back
#   from a +37° turn, were kept there while 2H and N kept the turn. The spike's follow-up B and C read the same of a
#   component no mate holds (2026 34.1.1 on another machine, again on this host,
#   probe/results/w8-followup-20261115-114828.json; 2024, probe/results/sw2024/w8-followup-20261114-233330.json).
# - On 2024 (32.5.0, W8 s7, probe/results/sw2024/w8-s7-20261115-162418.json, its log
#   w8-workbook-assembly-20261115-162357-s7.log): case 5's three moving puts each stayed in their configuration
#   alone (log 831-859, 909). Then FrontDog driven +15° in N left FIdler, which had stood at 0, +10, +20 and 0 in 2H,
#   4H, N and 4L, at −2.5° in all four (log 863-884, JSON same_amount_or_place): the same place in every
#   configuration, not moved by the same amount, and 4H's put of +10° was gone. So on 2024 a moving put is kept by
#   its configuration only until that train is next turned in any configuration. In case 8's rerun
#   (…-172046-s7-case8.log, w8-s7-20261115-172104-case8.json) the moving put in 2H, after an Update had put every mode
#   and a fresh turn, stayed in 2H. In 2024's s2 (…-233045-s2.log lines 220-223 and 462-465) both of the app's
#   quiet Updates in 4L, after their put in 2H, found 4H out of step at ModeSlv–FrontDog and N turned when they showed
#   them, so 2H's put had not reached them; after each put every mode read at its built frames (237-244, 479-486).
# - On 2026 34.1.1 (W8's closing run, s7 every case at c583f48: probe/results/
#   w8-workbook-assembly-20261116-020805-s2-s7.log, w8-s7-20261116-023505.json, 0 failed): case 5's three moving
#   puts each stayed in their configuration alone (log lines 1993, 2018, 2070), and FrontDog driven +15° in N left
#   FIdler, standing at 0, +10, +20 and 0, at −2.5° in all four (line 2043): the same place in every configuration,
#   not moved by the same amount, as on 2024.
# - On 2026 34.0.0, in W8 s2, after an Update had put every mode, a put in 2H was twice found in 4H and N, shown next,
#   and not in 4L (probe/results/w8-workbook-assembly-20261115-151412-s2.log lines 448-451, the second press, and
#   569-572 and 709, the changed Update's FDrive; the same in …-111951-s2-turn-carried-per-body.log lines 297-300).
#   The changed Update's FDrive reading recurred where its sequence was run again: its put of FDrive in 2H was found
#   in 4H and N and not in 4L on 34.1.1 (…-020805-s2-s7.log line 723) and on 2024 (sw2024/…-233045-s2.log line 724),
#   so it is no 34.0.0 peculiarity. Read, and nothing is built on it: that Update shows and puts every mode.
# - On 2026 34.1.1 (another machine; s7 case 8 alone at fe74276, after s1 built there: probe/results/
#   w8-workbook-assembly-20261115-220745-s1-s7-case8.log, w8-s7-20261115-222252-case8.json, 0 failed), case 8 read
#   what 2024's did: after the app's quiet Update in 4L had put every mode and a fresh +37° in 2H had read in all
#   four, the moving put in 2H by the app's route (the train back to its built frames, the carrier first) stayed in
#   2H; 4H, N and 4L still stood at the fresh turn (the Sun at +37°), through a save and reopen. In that Update,
#   after its put in 2H, 4H and N, each read when shown, before its put, showed the first turn still standing (4H
#   ModeSlv–FrontDog out of step, N turned; log lines 1855 and 1905-1907, the lines the probe labels "post-check"; in
#   the log only, not the JSON, and not pinned), as s2's own first press read on 34.0.0 from a copy no Update had
#   moved (…-151412-s2.log lines 224-227), so that is no new difference. Case 8 is not s2's sequence: it showed every
#   configuration between the fresh turn and the put, where that s2 showed 4L alone; its put is the probe's own
#   (s7_put_job), not the app's second Update press in 4L; and it ran on another machine as well as another revision.
#   The closing run's s2 on 34.1.1 (…-020805-s2-s7.log lines 357-369, 461-464) ran s2's current sequence, which shows
#   4H, N and 4L between the fresh turn and the press (7c9634d), and read what 2024's s2 and both case 8s read: the
#   turn in every mode shown, and 2H's put not carried. The 151412 sequence, 4L alone shown before the press, has not
#   run again on any version, so 34.0.0's reading stays unexplained between revision, machine and sequence. On 34.0.0
#   itself the first press, made after every mode had been shown, read the same as 34.1.1 and 2024 (…-151412-s2.log
#   lines 224-227). A no-op put changed nothing (s7 cases 2 and 3, on both versions).
# No behaviour reads these: every mode an Update shows is put to its built frames and post-checked (W8-INTERFACES
# §9.18). Not covered: a drag in the user interface (s6).
POSITIONS_PER_CONFIGURATION_ON_2026 = True
POSITIONS_PER_CONFIGURATION_ON_2024 = True
#
# A turn per configuration: whether a turn given to the gears in one configuration (the solver moving the mated bodies,
# here W5's drive) stays there. On 2026 it does not: it has been read in others.
# - In all four, on copies no Update had moved, on 34.0.0 (W8 s7 cases 1-3, as above): the drive's +37° on the Sun
#   in 2H moved every body of the train by the same amount in each (the Sun, InDog, RangeSlv and ModeSlv +37°, each
#   planet copy −18.5° and carried round, LoDog and the carrier +9.25°), also after no-op puts in 4L and in each
#   configuration, for a turn given in 4L, and for one given in N after a save and reopen. W8 s2 read it first, with
#   LoDog in interference with RangeSlv in 4L (531.913 mm³; …-111951-s2-turn-carried-per-body.log, and
#   probe/results/w8-turn-across-configurations-20261115-115500.txt, by a value set in 2H alone and by a global).
# - In 4L after an Update had put every mode, on 34.0.0 (…-151412-s2.log line 356: a fresh +37° in 2H read in 4L).
#   In that same state on 34.0.0 the fresh turn was NOT read in 4H and N: shown after the Update's put in 2H, both
#   read at the built turn, in step and not turned (…-151412-s2.log lines 448-451). In the 135428 run s7 case 4's
#   Update moved only the front train, so a turn "after the app's own Update" rests there on no-op puts of the driven
#   train.
# - In all four after an Update had put every mode, on 34.1.1 (s7 case 8 alone, …-220745-s1-s7-case8.log and
#   w8-s7-20261115-222252-case8.json, 0 failed): the drive's +37° in 2H read in all four by the same amount; the app's
#   quiet Update in 4L put every mode and every configuration then read at its built frames; a fresh +37° in 2H read
#   in all four by the same amount again ("shared" fitting, "per_configuration" ruled out); the moving put in 2H after
#   it stayed in 2H (POSITIONS above). So in case 8 on 34.1.1 the turn reached 4H and N and the put did not. Case 8
#   is not s2's sequence (POSITIONS above: every configuration shown before the put, the probe's put for the app's
#   second press, another machine).
# - In every mode on 34.1.1, W8's closing run at c583f48 (…-020805-s2-s7.log, w8-s7-20261116-023505.json, 0 failed):
#   s7 cases 1-4 and 8 each read the turn in all four configurations ("shared" fitting, "per_configuration" ruled
#   out), as on 34.0.0 and 2024; and s2, in its current sequence (4H, N and 4L each shown after the fresh turn, then
#   the press in 4L, 7c9634d), read the fresh +37° in 2H in 4H, N and 4L alike (lines 357, 362, 367; LoDog–RangeSlv
#   531.913 mm³ in 4L, line 368), and the Update in 4L after it found 4H out of step at ModeSlv–FrontDog and N turned
#   when it showed them after its put in 2H (461-464): the turn reached every mode and 2H's put did not carry, what
#   2024's s2 and both case 8s read. The 151412 sequence (4L alone shown before the press) has not run again on any
#   version, so s2's 34.0.0 reading stays unexplained between revision, machine and sequence; 34.0.0's own first
#   press, made after every mode had been shown, read the same as 34.1.1 and 2024 (…-151412-s2.log lines 224-227).
# On 2024 (32.5.0, W8 s7 on that host; probe/results/sw2024/w8-s7-20261115-162418.json and its log
# w8-workbook-assembly-20261115-162357-s7.log) every turn of the train s7 gave read "moved" in all four
# configurations, by the same amount, "shared" among the fits and "per_configuration" ruled out: on copies no Update
# had moved (cases 1-3); after the app's changed Update had put the turned train back in every mode (case 4); and after
# the app's quiet Update in 4L had put every mode (case 8, and its rerun, …-172046-s7-case8.log and
# w8-s7-20261115-172104-case8.json, 0 failed).
# LoDog then stood +9.25° against RangeSlv's +37° in 4L, where they are coupled: the dog across its sleeve the
# sentences warn of. So TURN_PER_CONFIGURATION_ON_2024 is False too. 2024's s2 on the next device (0e7f203,
# sw2024/w8-workbook-assembly-20261115-233045-s2.log lines 354-370) read the fresh turn in 4H, N and 4L after an
# Update had put every mode, the sequence the closing run then repeated on 34.1.1. A turn given while the
# configurations stood differently (case 5) brought the turned bodies to the same place in every configuration, not
# by the same amount, on 2024 and on 34.1.1 (POSITIONS above).
# Read by swcom.positions_per_configuration for the sentences about a turn (ui_text.turning_note, switching_note,
# TURN_SHOWN_ELSEWHERE, GEARS_SHOWN_ELSEWHERE, and _mode_after's two); no behaviour reads it. A version with no
# finding of its own (None) makes neither claim.
# Not covered: a drag in the user interface (s6, the person's step).
TURN_PER_CONFIGURATION_ON_2026 = False
TURN_PER_CONFIGURATION_ON_2024 = False

# -- W7's follow-up: putting a turned planetary back (probe planetary_put_back, tier 10, SolidWorks 2026 34.1.1) -----
#
# Results:
#   probe/results/w7-planetary-put-20261115-012409.json             routes A-E on the turned train, and the
#                                                                   suppressed read
#   probe/results/w7-planetary-put-follow-ons-20261115-013108.json  C's two follow-ons
# The first run passed gear_mate_sense the opposite same_sense (sense > 0, where the record writes -1 for "the same
# way"). Its sense verdicts are re-judged exactly in decide.py (senses_inverted=True), and a note at the top of its
# .txt says so.
#
# What was done:
# - The gearbox: W7's built, un-driven Planetary_4to1 (E's p1). The sun is the input, the ring is held, there is a
#   skeleton carrier, and three copies of one planet part. CarrierGear is locked to the carrier.
# - It was copied afresh for every route, opened, and every component checked to resolve in the copy.
# - The sun was driven +37° (the carrier then stood 9.25° off, each copy -18.5°) and the drive deleted.
# - Then each route put every body back to the record's built frames, through the app's swcom.Session members.
# - Judged through fresh handles after a top-only rebuild: every frame within place_component's 1e-6, every gear mate
#   read right, no interference. Then the sun was driven +20°: the carrier must turn +5°, CarrierGear +5°, each
#   copy -10°, the ring 0, with nothing clashing.
#
# Route by route:
# - A (the app today: the lock off, then the carrier put first with the gear mates on) failed:
#   - the carrier read back 0.1074 off (6.2°, as in p3);
#   - the copies read back 1.93, 1.62 and 1.73 mm off;
#   - 24 interferences were found.
# - B (the sun alone first) failed: the solver did not carry the train back. After the sun's put, the carrier read
#   0.1607 off; then A's failures followed.
# - D (every put, then one rebuild) failed: the carrier read 0.1074 off, the copies 0.1048 and 1.6-1.9 mm off, and
#   the sun 0.2136 off.
# - C held: every gear mate and the lock suppressed, a top-only rebuild, then the puts in W7-INTERFACES §6.13's
#   order (the held ring only if off; the carrier; the sun, each copy, CarrierGear), each by place_component and read
#   back. Then a rebuild, every gear mate and the lock turned back on, and a rebuild.
#   - Every frame read back within 2e-9 mm, every sense read right, and nothing interfered.
#   - Driven +20°: sun 20, carrier 5, CarrierGear 5, copies -10, ring 0, nothing interfering.
#   - It held as well with the copies also moved 2 mm along their axes ("Planet Face Z" 5 -> 7, set before the
#     puts, the train turned 37°), and on a train not turned at all.
# - E (C with the copies' axis mates also off) held too; it is not needed.
#
# A dispatches on the value. Not covered:
# - SolidWorks 2024 (the confirming run);
# - more than one carrier;
# - a held member that is off;
# - a planetary with the carrier held;
# - ratios remade inside the route (p3's step 3).
PLANETARY_PUT_ROUTE = "gear mates off around the puts"
# Route C's gear mates turned back on, in all three C cases:
# - each kept its ratio (18 : 18 and 18 : 54, read before and after);
# - each read right by gear_mate_sense;
# - turning them on marked no document beyond what the puts had marked (the assembly; no part).
GEAR_MATE_BACK_ON_KEEPS_SENSE_AND_RATIO = True
GEAR_MATE_BACK_ON_MARKS = "nothing beyond the puts"
#
# A suppressed gear mate's sense read (W8; read where swbuild's Update reads it, swbuild._sense_read):
# - "Planet copy 1 meshes Ring" was suppressed, rebuilt, saved (SaveAs3 in place), closed and reopened. The
#   assembly read GetSaveFlag False on reopening, and the mate read suppressed.
# - Read twice, the mate answered right both times, as it had before it was suppressed (Reverse and both entities
#   read; τ +1, +1). The assembly read GetSaveFlag False after each read.
# - The control, "Sun meshes Planet copy 2" left on, did the same.
# On 2024 (32.5.0, W8 s7 case 7 at 1560b25; probe/results/sw2024/w8-workbook-assembly-20261115-162357-s7.log line
# 1170, w8-s7-20261115-162418.json cases[6].suppressed_sense): on a copy of the 2024-built E4 opened from its files,
# every document GetSaveFlag False, 2H active, the coupling "RangeSlv engages LoDog", suppressed in 2H by the build,
# read once by gear_mate_sense answered right (τ +1, +1), as the control "RangeSlv engages InDog" left on did, and no
# document read modified before or after. The app's own quiet Updates on 2024 then read every sense, the suppressed
# couplings included, and marked nothing (sw2024/…-230215-s3.log lines 739-742 and 821-824, …-233045-s2.log lines
# 344-349).
# On 2026 34.1.1 (W8's closing run, s7 case 7 at c583f48; probe/results/w8-workbook-assembly-20261116-020805-s2-s7.log
# line 2382, w8-s7-20261116-023505.json cases[6].suppressed_sense): the same read on a copy of the E4 built there,
# with the same answers (τ +1, +1 for both mates) and no document modified before or after.
# Not covered: on 2024, a suppressed mesh between parallel axes (2024 read a collinear coupling, 2026 a planet's
# mesh), or a second read.
SUPPRESSED_GEAR_MATE_SENSE_READ = "answers, marks nothing"

# -- W8's last call probed ahead: a configuration whose mates fight, shown (W8-PLAN §4.2 item 1); and the order the
# -- per-configuration reads answer in (probe w8_over_defined_show, tier 11, SolidWorks 2026 34.0.0) ----------------
#
# Results:
#   probe/results/w8-over-defined-20261115-100312.json           the evidence (from 2b530eb)
#   probe/results/w8-over-defined-attempt-20261115-094752.txt    the first run (from b296c7f), kept: its app mate check
#                                                                raised outside a build and its lock fought alone
# Both ran on THIS machine's SolidWorks 2026 SP0 (revision 34.0.0), each in a session started fresh for it. The W8
# spike, its follow-up and W5-W7's probes ran on another machine at 34.1.1, so what is set here is 34.0.0's.
# The plan names the probe p9_modes; tiers 9 and 10 were taken, so it is tier 11 (p11_modes.py).
#
# The shape is the W8 spike's (the strip's spur as A and D, its internal ring as sleeve S; the spline S-A and the
# coupling S-D as 1 : 1 gear mates; one slide, S's origin to the layout's Front). X, Z and Y were added in that order,
# so the document's configuration order is Default, X, Z, Y. The slide read Default 10, X 15, Z 20, Y 30 mm.
#
# Two slides on one sleeve in one configuration:
# - A second distance mate on the same entities, made at 25 mm and set to 25 mm in every configuration
#   (SetSystemValue3 answered 0 each time; that value was never read back), was on in Z only, beside the first (20 mm
#   in Z).
# - ShowConfiguration2("Z") returned True, and Z read back active. No window opened during the show, under the dialog
#   watch.
# - The top-only rebuild (ForceRebuild3(True)) returned True. It put up one window, a balloon tip (class
#   swBalloonTip): "Over Defined" / "The assembly is over defined. Click here to view mate errors." It is non-modal:
#   it was first seen 0.26 s into the rebuild, the rebuild's watch saw it for 0.79 s (to the end of that watch, not
#   to the end of the balloon), and it was still standing after the reads that followed and when Y's show and
#   rebuild began. It was gone once Y's reads ended: it stood at least about 2.3 s. Nothing answered it, and the
#   calls went on while it stood. What closed it, by itself or Y's show, the file does not show.
# - Both slides read GetErrorCode2 47 (swFeatureErrorMateIlldefined), warning False. S read GetConstrainedStatus 4.
#   What's Wrong listed "Mates" (1), "S slide" (47) and "S slide 2" (47).
# - The app's own reads: Session.mate_states gave both slides code 47, warning False, not suppressed; the mate check
#   (swbuild._mate_problems) said "The mate S slide is in error in SolidWorks." and "The mate S slide 2 is in error in
#   SolidWorks." S stood at 30 mm, neither slide's value.
# - Y, then X, shown and rebuilt after it: every code 0, nothing over-defined, the mate check silent, S at 30 and 15 mm
#   (within 1e-6). Z shown again read as the first time, with no balloon tip: the second show and rebuild of Z put up
#   no window. With the second slide suppressed in Z and a rebuild, Z read clean with S at 20 mm.
# - The first run read the same, with one difference: its show of Z saw two windows open, swWelcomeScreen (0.78 s
#   in) and SysShadow (1.05 s), neither answered and neither asking anything (most likely the fresh session's own
#   Welcome screen coming back late, not the show); the rerun's show saw none. Its balloon tip, too, was still
#   standing after the rebuild's watch.
# So a watcher must allow a balloon tip that outlives the call that raised it and stands at the next, and must not
# require one: it came once per run, on the first rebuild into the fight only.
# So showing such a configuration asks nothing and hangs nothing: it is seen only by reading the mates afterwards,
# which the build's and Update's per-mode checks already do.
# A coupling beside a lock across the same pair (S-D), on in Y, the lock alone holding S there (S's own slide and axis
# mate off in Y): no window, every code 0, nothing over-defined, the mate check silent; X after it and Y with the lock
# off read clean too. So that pair is redundant but not in error, and is NOT caught by reading the mates. In the
# first run, with S's slide and axis mate still on, the lock itself was made with AddMate5 status 5 (the coupling
# off): S's axis mate (code 1, warning True), D's along mate and S's slide (code 46, swFeatureErrorMateOverdefined,
# warning True) read in error, and D and S status 4. With the coupling then on beside it, the mates in error were D's
# axis mate (code 1) and D's along mate, the spline, the coupling and S's slide (code 46), and A read status 3. That
# over-defining make, and the rebuilds after it, put up no window and no balloon tip.
# Not covered:
# - Save flags: the assembly was never saved and the parts read modified from the mounts on, so every GetSaveFlag
#   read True throughout, and what an over-defined show marks is not told.
# - A fight in a saved, reopened assembly; a fight among gear mates; SolidWorks 2024.
# - SolidWorks' option to show errors at every rebuild was left as installed; a person who turns it on may see a
#   What's Wrong window.
CONFIGURATION_SHOW_OVER_DEFINED = "shown; no window asks; its mates read in error; others solve after"
#
# The read order, measured again (W8 s0's first run found it ad hoc: probe/results/w8-configuration-order-20261115-
# 092100.txt, read on that run's refused assembly). At three moments, each mate whose flags differ between
# configurations (the coupling, off in Y only; the second slide, on in Z only; the lock, on in Y only; the first slide,
# off in Y only) was read with IsSuppressed2(3, names), and the slide with GetSystemValue3(3, names). Each read
# passed the full list in the document's order, reversed and shuffled, two-name lists both ways round, and each name
# alone; each was judged against the single-name reads, which matched what was set in every case.
# - IsSuppressed2(3, names) answered in the document's configuration order (GetConfigurationNames: Default, X, Z, Y,
#   the order of creation, not alphabetical), filtered to the names asked, whatever order they were passed in. For
#   example, the coupling (on in Default, X and Z, off in Y): [Y, Z, X, Default] -> (False, False, False, True), and
#   [Y, X] -> (False, True).
# - GetSystemValue3(3, names) answered in the order passed: [Y, Z, X, Default] -> 30, 20, 15, 10 mm.
# What these reads tell apart, and what they do not:
# - At all three tier-11 moments Y was active, and Y is last in the document's order. So tier 11 alone cannot tell
#   "the document's order" from "the active configuration last". The s0 file settles it: with 2H active and second
#   in the document's order, it read ['N', '2H'] -> (False, True), 2H's flag first.
# - Default's and X's flags were equal in every pattern read, so their places in the answer are never told apart.
# - The order of creation and GetConfigurationNames' order were the same in both files, so which of the two the
#   answer follows is not told.
# So a flag is read one configuration per call (swcom.Session.mate_suppression), or its answers are keyed by the
# document's order; a value read may pair answers with the names passed.
SUPPRESSION_READ_ORDER = "the document's configuration order"
VALUE_READ_ORDER = "the order passed"

# -- W9 S0: the user's work on a gear Update puts back (ISSUE-1-PLAN §4, probe/w9_user_work_check.py; W9-S0.md,
# -- reviewed in W9-S0-REVIEW.md) ------------------------------------------------------------------------------------
#
# Results, each run in a SolidWorks session started fresh for it:
#   probe/results/w9-s0-sw2026-20261116-050200.log, w9-s0-20261116-045653.json    run 1, 2026 34.1.1 at 55a82c1: P0,
#                                                                                  case 0, routes (a) and (b), C, C2
#   probe/results/w9-s0c-sw2026-20261116-054300.log, w9-s0-20261116-054213.json   run 2, 2026 34.1.1 at 423e227:
#                                                                                  route (c) in A, B, E; D, C, C2
#   probe/results/sw2024/w9-s0-sw2024-20261116-065000.log                         run 3, 2024 32.5.0 at 423e227: P0
#                                                                                  to C; no JSON (the session was
#                                                                                  lost at the start of C2)
# The app's source is the same at 55a82c1 and 423e227. Each case: the issue's RangeBox (tests/workbook_fixtures.
# range_box) built by the app; the user's sprockets and housing added by AddComponent5 into the reopened assembly with
# its modes H, N and L, mated by named axes and planes, saved under a new name and reopened; in H and then in L, each
# shown, W8 s7's drive +37°, then the train put back to its built frames, read before and after; after the last put,
# every mode shown, rebuilt and read. Which user components a case ties came from the case's own list, not from reading
# the user's mates. No app code reads these findings yet.
#
# The route for a user's component locked to a gear the put moves (ISSUE-1-PLAN K2, route (c1)). Routes (a) and (b)
# leave the component behind (LOCK_RETAKES_AFTER_A_PUT, LOCK_UNSUPPRESS_KEEPS_THE_NEW_ANGLE). Route (c1): in the mode
# shown, the app's locks, gear mates and couplings on there suppressed and the assembly rebuilt; the app's bodies put
# (carriers first); then each user component rigid to a put gear through the user's locks, directly or through a
# chain, put by its gear's rigid motion (G_target · G_before⁻¹ · U_before), each read back by place_component; a
# rebuild, the app's mates back on; the user's locks left on throughout. Cases A (Sprocket-1 locked to Sun), B
# (Sprocket-2 locked to RangeSlv, which slides by mode) and E (A, and Sprocket-3 locked to Sprocket-1), each put twice
# in H and twice in L: every put clean (every body, the user's included, at its target to 6.6e-10 or better with the
# mates back on; each locked sprocket at its pose of the setup in its gear's frame, the worst 7.1e-15; no mate in
# error; no read marking a document); a further rebuild and a second drive re-took no offset; and in the last read,
# each mode shown, every app body stood at its built frame and every locked sprocket at its pose. (c2), the user's
# locks suppressed around the puts and turned back on, read the same, and writes more of the user's.
# - 2026: run 2's proposal (the JSON's "proposal", log lines 1034-1035) and each case's outcome; 0 failed.
# - 2024: run 3's per-put lines, every one "clean True": 1055-1104 (A-c1), 1171-1220 (A-c2), 1289-1340 (B-c1),
#   1408-1457 (B-c2), 1526-1575 (E-c1), 1644-1695 (E-c2); and each case's last-read checks (1112, 1228, 1348, 1465,
#   1583, 1703). There is no propose line: the run ended before it.
# Covers user LOCK mates that are on in the mode being put, chains included, and nothing else. Not measured, and
# refused by K2 before any write until measured: a user gear mate on a put gear (a put with a gear mate on re-phases
# it silently, MESH_PHASE_ROUTE), a concentric, coincident, parallel or angle mate to a gear's own faces or planes, and
# a user lock whose flag differs between the mode put and another (S0 carried a tied component in every mode whatever
# its lock's flag there). The chain is to be read from each user lock's entities in the mode shown (the plan's M1).
USER_MATE_PUT_ROUTE = "put along, the user's locks left on"
#
# The grounded tie (K2), case C: Sprocket-1 locked to Sun and its Top plane coincident with the fixed Housing-1's, the
# tie on in every mode. Three things, written apart:
# - USER_TIE_READ, the value read: GetConstrainedStatus 3 (COMPONENT_FULLY_DEFINED) on every app body of the tied
#   train (Sun, the three planet copies, the carrier, HighDog, LowDog, RangeSlv), unshown with H active, shown in H and
#   shown in L, before any put; every case without the tie read 2 for every mated body. On 2026: run 2 lines 909, 914
#   and 929, the JSON's proposal "USER_TIE_READ" "C", and run 1 the same; on 2024: run 3 lines 1835, 1840 and 1857.
#   Never 4 in these reads. N was read only in the last read, after the puts, and there RangeSlv, not coupled in N,
#   read 2 (run 2 line 945): which bodies a tie holds follows the mode's couplings.
# - USER_TIE_RULE, the rule the app applies: a train is tied when a body of it reads anything but
#   COMPONENT_UNDER_DEFINED, as swbuild._free_to_turn tests, never "equal to 3". SolidWorks raised its "The assembly is
#   over defined" balloon during C's drive in H on both versions (run 2 line 917, run 3 line 1843) while the drive job
#   read no error, so a tie whose geometry conflicts could read 4.
# - USER_TIE_READ_PER_MODE_ON_<year>, case C2 (the tie suppressed in H and N, on in L): True where a mode's tie was read
#   only with that mode shown. On 2026: the unshown read with H active and H shown read the train free, every mated
#   body 2, and L shown read it tied (run 2 lines 991, 996 and 1012; the JSON's proposal "USER_TIE_READ" "C2"; run 1
#   the same). On 2024 the same, from C2 run alone in a fresh session at d086705 (run 4,
#   sw2024/w9-s0-c2-sw2024-20261116-155327.log lines 54, 59 and 75 and its JSON's proposal; 0 failed): run 3 had
#   ended at C2's first read (line 1920). With the same flags in every mode, C read H and L the same; that the showing mode's read decides every
#   mode is not measured (N was not read before a put).
# No behaviour may rest on the per-mode reading: K2 reads a mode whose user flags differ when it is shown, on every
# version.
USER_TIE_READ = 3                               # COMPONENT_FULLY_DEFINED; on 2026 and 2024
USER_TIE_RULE = "not COMPONENT_UNDER_DEFINED"
USER_TIE_READ_PER_MODE_ON_2026 = True
USER_TIE_READ_PER_MODE_ON_2024 = True           # run 4, C2 alone
#
# What's Wrong on a failing rebuild (the plan's P0, probed ahead for a dialog), first in runs 1 and 3: a scratch part
# built by the strip and opened by the app's route, visible and active; a user keyway (a Ø3 cut through the bore's
# edge) made by the session's own sketch and cut calls; "show errors every rebuild" (swUserPreferenceToggle_e 77) on as
# found and after; Bore Diameter 10 -> 14, which left the keyway inside the bore. The part's rebuild (s.rebuild(),
# ForceRebuild3(False) for a part) returned False, the keyway alone read in error (GetErrorCode2 71 on 2026 and 51 on
# 2024, warning False; never read for meaning, as MATE_ERROR_2024's comment rules), GetWhatsWrongCount read 1, and no
# new window of SolidWorks' process came up in the 8 s after. On 2026: run 1 lines 9-12, the JSON's "p0"; on 2024:
# run 3 lines 8-12.
# Covers a part's rebuild only. An assembly's rebuild (Update's ForceRebuild3(True)) with only a user mate or feature
# in error was not run: whether it opens What's Wrong or reports failure is the plan's M3, to be measured in W9a's
# demonstration, where a dialog is a STOP.
WHATS_WRONG_OPENS_ON_PART_REBUILD = False
#
# D: Sprocket-2's axis on Output Axis and its Front plane coincident with the sliding RangeSlv's, no lock; the train put
# by the app's route with nothing of the user's moved. It stood on RangeSlv's plane (0 mm from it, to 1e-9) through the
# drives and puts in H and L and in the last read in H, N and L, no mate in error, RangeSlv and Sprocket-2
# under-defined throughout. On 2026: run 2 line 868, the JSON's proposal "D_on_slide" and D's last frames (RangeSlv at
# z -34.5, -29.5 and -24.5 in H, N and L, Sprocket-2 with it); on 2024: run 3 lines 1771, 1787 and 1792 (no frames
# there, so RangeSlv's slide itself was read on 2026 only). Scope: an axis mate and a plane-coincident mate, no lock;
# the puts turned RangeSlv only, and the slide came from showing each mode. Nothing reads it.
USER_PLANE_MATE_ON_SLIDER_FOLLOWS = True
#
# Route (c1)'s branches S0 did not measure (W9a package A's review, point 4; the coordinating session's ruling 4,
# 2026-11-16). S0 put a user component with its gear on RangeBox's one train, which has a carrier, every app lock,
# gear mate and coupling on there suppressed around the put (USER_MATE_PUT_ROUTE above). Update also puts gears by
# other sequences, and each is gated by its own finding here, None (not measured) on both versions, so a user
# component locked to such a gear refuses before any write until a run reads the branch clean and sets it True:
# - NO_CARRIER: a train with no carrier, put with its gear mates left on (swbuild._put_train), the commonest case
#   (a plain parallel gearbox); measured on 2026 and 2024 by W9a's demonstration (below).
# - HELD_GEAR: a held gear of a train, re-placed first by REPLACE_FIXED_ROUTE (swbuild._put_train).
# - FIXED_GEAR: a fixed gear re-placed W4's way, unfixed, put and fixed again with the user's lock on
#   (swbuild._motion_assembly, swbuild._modes_put).
# - SUBASSEMBLY: a user sub-assembly put as one top-level component (Transform2 on an assembly component).
# Nothing measured HELD_GEAR, FIXED_GEAR or SUBASSEMBLY; no probe or run is cited for them.
# NO_CARRIER on 2026: True, from W9a's demonstration, section nocarrier (SolidWorks 2026 revision 34.1.1, snapshot
# 9dded70; probe/results/w9a-demo-sw2026-20261116-3-again-reducer-k3-nocarrier.log, r3 below, lines 1445-1598, and
# w9a-demo-20261116-215415.json, "sections" "nocarrier" and "proposal" "USER_MATE_PUT_NO_CARRIER_ON_2026"), as the
# run's review accepts it (docs/notes-workbook/W9A-RUN-2026-REVIEW.md). The 12 : 1 (G1 on S1 drives G2, G3 locked to
# G2 drives G4 on S3; no carrier, one configuration, no modes), with the user's Sprocket-1 locked to the driving G1
# (UserLock1, its axis on S1 Axis by UserAxis1), Sprocket-2 locked to the driven G4 (UserLock2, on S3 Axis by
# UserAxis2) and Sprocket-3 locked to Sprocket-1 (UserLock3, a chain of one; r3:1463); every gear labelled the
# no-carrier branch (r3:1480); the default refusal with the finding None, writing nothing (r3:1503-1532). With the
# finding patched True for the measurement only (r3:1533, 1596), two presses, each after the user turned G1 by +37
# degrees (r3:1481, 1553), the whole train put back to its built turn and G4 moved 3 mm along S3 and back (At 27 ->
# 30, then 30 -> 27): seven puts each, the gear mates left on as _put_train puts such a train (the trace's two
# SetSuppression2 calls a press are not named in the log; r3:1544, 1587), ok True (r3:1548, 1591); read after, and
# after a further rebuild, every gear at its frame on record (worst 1.1e-14), each sprocket on its gear as set up
# (worst 2.8e-15), no mate in error, every gear free (r3:1541-1552, 1584-1595); the proposal True, both presses clean
# (r3:1598). Not measured: a train with no carrier on a gearbox with modes (its own branch, NO_CARRIER_MODES below),
# a user lock to G2 or G3 (the gears the app's own lock joins), an idler, the turn the other way.
# The closing run (c2 is probe/results/w9a-close-sw2026-20261116-2-go-m1-refuse-again-nocarrier.log, snapshot 6f3d6fb,
# with w9a-demo-20261116-232221.json) ran nocarrier again with the finding committed True (the patch a no-op, "was
# True", c2:1350, 1412): both presses read clean and the footer's carry was the press's (c2:1366-1370, 1407-1411;
# the proposal, c2:1414).
# What it opens, which is wider than the evidence: user_carry_branches labels every train with no carrier on a
# gearbox without modes NO_CARRIER, so on 2026 and 2024 route (c1) now carries a user's locked component on any such
# train — crossed-axis trains, ring trains, idlers, several trains, compound pairs — where only the parallel 12 : 1
# was run.
# The risk is bounded: route (c1) reads every carried pose back after the put (swbuild._carried_problems).
# NO_CARRIER on 2024: True, scoped as 2026's, from W9a's confirming session on 2024 (32.5.0, snapshot 19651ee;
# probe/results/sw2024/w9a-confirm-sw2024-20261117-2-setup-go-reducer-nocarrier.log, section nocarrier from line 799,
# with sw2024/w9a-demo-20261117-003040.json, "sections" "nocarrier" "clean" [true, true]): the same 12 : 1 and
# sprockets (line 817), every gear labelled the no-carrier branch (834), the default refusal naming the 2024 finding
# (877); with the finding patched True for the measurement only (887, 948), both presses went ahead and put each
# locked sprocket with its gear, its gear mates on (902, 943), the footer's carry the press's (944), and read clean,
# and again after a further rebuild (905-906, 946-947; worst 1.1e-14 gear, 1.4e-14 sprocket); the proposal (951).
USER_MATE_PUT_NO_CARRIER_ON_2026 = True
USER_MATE_PUT_NO_CARRIER_ON_2024 = True
# - NO_CARRIER_MODES: the same on a gearbox with modes (swbuild._modes_put, each mode shown and put), kept apart from
#   NO_CARRIER because the demonstration put a train with no carrier on a gearbox with no modes only. Not measured.
USER_MATE_PUT_NO_CARRIER_MODES_ON_2026 = None
USER_MATE_PUT_NO_CARRIER_MODES_ON_2024 = None
USER_MATE_PUT_HELD_GEAR_ON_2026 = None
USER_MATE_PUT_HELD_GEAR_ON_2024 = None
USER_MATE_PUT_FIXED_GEAR_ON_2026 = None
USER_MATE_PUT_FIXED_GEAR_ON_2024 = None
USER_MATE_PUT_SUBASSEMBLY_ON_2026 = None
USER_MATE_PUT_SUBASSEMBLY_ON_2024 = None
#
# An assembly's rebuild with the user's work in error (the plan's M3), measured in W9a's demonstration on SolidWorks
# 2026 (revision 34.1.1, snapshot 9dded70) and checked by the run's review (docs/notes-workbook/W9A-RUN-2026-REVIEW.md,
# finding 2). r1 is probe/results/w9a-demo-sw2026-20261116-1-m3-setup-go.log, section m3, with its JSON
# w9a-demo-20261116-204840.json ("sections" "m3", "proposal" "M3"); r3 is
# w9a-demo-sw2026-20261116-3-again-reducer-k3-nocarrier.log, section k3, with w9a-demo-20261116-215415.json
# ("sections" "k3"). Each rebuild was the app's train route (swcom.rebuild_call for ASSEMBLY_TRAIN), the assembly
# active. "Show errors every rebuild" was not read in this run (it was last read on in S0's P0, another session of
# the same install, w9-s0-sw2026-20261116-050200.log line 9). Three findings, written apart, each None on 2024 until
# its confirming m3 and k3 run:
# - ASSEMBLY_REBUILD_WITH_USER_MATE_IN_ERROR_ON_<year>, what the rebuild returns with only user mates in error: True.
#   RangeBox in H, two user mates on one user component, Sprocket-1: UserFront, a distance mate to the layout's Front
#   plane, and UserGap, a distance mate to the user's fixed Housing-1 at the distance UserFront left plus 1 mm (AddMate5
#   status 5, r1:48). Both read in error (46 and 47) and nothing of the app's; the rebuild returned True,
#   GetWhatsWrongCount 3, no window (r1:49-51; JSON "mate_error"); with UserGap suppressed every code read 0 again
#   (r1:84). As a fact of that run, not a rule: the app's value Update with the mates in error went ahead and named
#   both as the user's, in error before (r1:71, 73).
# - ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_<year>, what the rebuild returns with a feature in error in a
#   part: False. RangeBox in H: the user's keyway in the user's own Sprocket.SLDPRT, left inside the bore by its Bore
#   Diameter 10 -> 14 (code 71); the part's rebuild returned False, and the assembly's returned False with
#   GetWhatsWrongCount 1, no mate in error and the component Sprocket-1 reading code 1 (r1:88-91; JSON "part_rebuild",
#   "feature_error"). The 12 : 1 with no modes: the user's keyway in G1's part rebuilt into error (code 71) by a value
#   Update setting G1's Bore 8 -> 14, G1's app features reading no error (r3:1439-1440); that Update's assembly
#   rebuild reported failure, "SolidWorks reported an error rebuilding Reducer_12to1." (r3:1432, 1434), with two
#   ForceRebuild3 calls in its trace (r3:1435); k3 read no component code and no What's Wrong count. As facts of the
#   run: both Updates stopped (r1:112; r3:1434).
# - WHATS_WRONG_OPENS_ON_ASSEMBLY_REBUILD_ON_<year>: False. "windows new none" after each of m3's rebuilds read
#   (r1:45, 49, 84, 90); no "NOTE a SolidWorks window" line in r1 or r3, and k3's watch stopped nothing. Since the
#   2024 review it covers the mate case only (r1:49); the feature case is its own finding below, as on 2024 a box
#   came and went within the activate-and-rebuild step, too briefly for these after-the-step window lists.
# Scope of all three: two user mates of one kind (distance), over-defined; one feature kind (a cut swallowed by the
# bore, code 71), in one part at a time; RangeBox in H, and the 12 : 1 without modes. Not measured: a user mate in
# error of another kind or on an app gear, several parts in error, an app feature in error. They do not say
# the app may go on after a False rebuild: swbuild._rebuild_laid_to_user decides that, gated per version by
# swbuild.assembly_rebuild_settled — since the coordinator's ruling on 2024's box (below), on the two rebuild
# findings being set and WHATS_WRONG_IN_UPDATE_BLOCKS_ON_<year> False, no longer on WHATS_WRONG_OPENS_ON_ASSEMBLY_
# REBUILD_ON_<year>; with any of them None (or the box blocking) a False rebuild stays a failure.
# What that rule does not read (the close review, docs/notes-workbook/W9A-CLOSE-2026-REVIEW.md, finding 4): the
# assembly's own feature tree beyond its mates and components, its equations (the Face Z globals) and any
# assembly-level feature, the app's or the user's. Reading it would take GetErrorCode2 on top-level assembly features
# other than components, a read the app has never made and no run has measured (which of them reads in error when a
# component does is not known), so it is not read: an app equation in error beside a user component in error would be
# laid to the user. Rare, and nothing measured it.
#
# W9a's closing run on 2026 (34.1.1, one session, snapshot 6f3d6fb; c1 is
# probe/results/w9a-close-sw2026-20261116-1-m3-reducer-k3-setup-lightweight.log with w9a-demo-20261116-225659.json)
# repeated each reading with "show errors every rebuild" (toggle 77) read True (c1:41): the mate case True, What's
# Wrong 3 (c1:55); the feature case, the part False and the assembly False, What's Wrong 1, Sprocket-1 code 1
# (c1:111-113); no new window after any of them (c1:51, 55, 107, 111, 113). And the app's own Updates ran with the
# user's work in error and no window, with the rule above in force: m3's with the mates in error (c1:91-105), m3's
# with Sprocket-1 in error, laid to the user (c1:148-161, 160), and k3's with the keyway newly in error in G1's part,
# laid to the user, G1's own component reading code 1 (c1:786-800, 798, 800).
# SolidWorks 2024 (32.5.0), every run in a fresh session, all under probe/results/sw2024/ and checked by the 2024
# review (docs/notes-workbook/W9A-CLOSE-2024-REVIEW.md). v24 is w9a-confirm-sw2024-20261117-1-m3-stopped-by-whats-
# wrong.log (snapshot 19651ee, JSON w9a-demo-20261117-002344.json); b1 and b2 the box runs, under a watch that only
# logs (nothing set, answered, closed or saved once a box was seen): w9a-box-sw2024-20261117-1-box.log (b985cab,
# w9a-demo-20261117-013103.json) and w9a-box-sw2024-20261117-2-reducer-box-k3.log (b985cab, w9a-demo-20261117-
# 014251.json); s3, s4 and s5 the confirming set: w9a-confirm-sw2024-20261117-3-m3-stopped-by-the-scripts-rule.log
# (0a60fd3, w9a-demo-20261117-015234.json), w9a-confirm-sw2024-20261117-4-m3.log (10a6a08, w9a-demo-20261117-
# 020629.json, 0 failed) and w9a-confirm-sw2024-20261117-5-reducer-k3.log (10a6a08, w9a-demo-20261117-023110.json,
# 0 failed), whose watch logs a box owned by SolidWorks' frame as a fact, waits the job, and at its end wants the box
# gone within 60 s and the frame enabled (s4:7). "Show errors every rebuild" (toggle 77) read True in every run that
# read it (v24:37, b1:39, s3:39, s4:37; b2:592); s5 did not read it.
# - ASSEMBLY_REBUILD_WITH_USER_MATE_IN_ERROR_ON_2024: True, with 2026's scope. UserGap over-defining (status 5), the
#   script's own rebuild True, What's Wrong 3, codes 51 and 51, no new window: v24:50-51, b1:53-54, s3:52-53,
#   s4:51-52.
# - ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_2024: False. Read directly in s4: the user's keyway in the user's
#   own Sprocket.SLDPRT left inside the bore (code 51; the part's rebuild False, s4:113), then the script's own
#   assembly rebuild (ForceRebuild3, the app's train route) returned False, What's Wrong 1, no mate in error,
#   Sprocket-1 reading code 51 (s4:119-120). The app's two Updates laid their False rebuilds to the user under the
#   rule: m3's, the feature in the user's own part (s4:172-173, ['Sprocket-1']), and k3's, the keyway in G1's part
#   rebuilt into error by the Update's Bore 8 -> 14 (s5:600, 611-612, ['User Keyway in Gear_m1.5_N17.SLDPRT']; G1's
#   component read 51, s5:613). (box-k3's stop before the ruling, b2:605-608, said the same.)
# - WHATS_WRONG_OPENS_ON_ASSEMBLY_REBUILD_ON_<year>, scoped to the MATE case and the rebuild call: False on 2024 —
#   with the two user mates in error the script's own activate-and-rebuild step showed no box (s4:54, "What's Wrong
#   box during the step none", under s4's watch; v24:51, b1:54, s3:53 by the window lists after it). Nothing in the
#   app reads it any more.
# - WHATS_WRONG_OPENS_ON_ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_<year>, the FEATURE case: True on 2024. With
#   the keyway in error in the user's part, the same step showed the box: up 0.53 s in with the worker in
#   ActivateDoc3, gone 1.05 s in during ForceRebuild3, nothing closing it, the frame enabled at the end (s4:115-118,
#   120); at 0a60fd3 the same box stopped the run under the script's earlier rule (s3:116-119). It is the box a
#   person meets doing the same (activate the assembly, rebuild). On 2026: None. The 2026 runs' watch polled every
#   2 s and their window lists read after the step (r1:90, c1:113 "windows new none"), so a box as short as 2024's
#   here could have been missed; the final 2026 run, with s4's watch, is the read that settles it. Nothing in the
#   app reads it.
ASSEMBLY_REBUILD_WITH_USER_MATE_IN_ERROR_ON_2026 = True
ASSEMBLY_REBUILD_WITH_USER_MATE_IN_ERROR_ON_2024 = True
ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_2026 = False
ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_2024 = False
WHATS_WRONG_OPENS_ON_ASSEMBLY_REBUILD_ON_2026 = False
WHATS_WRONG_OPENS_ON_ASSEMBLY_REBUILD_ON_2024 = False
WHATS_WRONG_OPENS_ON_ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_2026 = None
WHATS_WRONG_OPENS_ON_ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_2024 = True
#
# What's Wrong during the app's own Update with the user's work in error (the close review, "The 2024 fact and the
# options"; the 2024 review). The mate case, WHATS_WRONG_OPENS_IN_UPDATE_WITH_USER_MATE_IN_ERROR_ON_<year>: RangeBox
# in H, two user distance mates on Sprocket-1 over-defined (UserFront to the layout's Front plane, UserGap to the
# user's fixed Housing-1), the app's value Update (Sun's Backlash):
# - 2024: True. The footer named both mates in error before the press (v24:82); the box came up during the press
#   (#32770: Show errors, Show warnings, "Display What's Wrong during rebuild", FeatureXpert, Close, Help; v24:88-89)
#   and the script, under its rule then, stopped (v24:90-96); the quiet press before it made the same reads with no
#   box (v24:56-66). Then in every run: b1:103, 105-106, 110; s3:90-94; s4:89-93, each time the Update going ahead
#   (b1:141; s3:95-98; s4:94-97, 106-107).
# - 2026: False. The same Update went ahead with no window (c1:41, 91-105; the first run's r1:53-82 the same).
# The feature case, WHATS_WRONG_OPENS_IN_UPDATE_WITH_PART_FEATURE_IN_ERROR_ON_<year>:
# - 2024: True. The Update over a feature in error in the user's own part (s4:155-159, going ahead, s4:160-163,
#   172-173), and the Update rebuilding the user's keyway in G1's part into error (b2:597, 599-600; s5:594-598,
#   going ahead, s5:599-603, 611-612).
# - 2026: False, the closing run's two such Updates with no window (c1:148-161, 786-800).
# The 2026 values rest on a watch that polled every 2 s; every Update box seen on 2024 stayed 3 s or more.
# Not known: which call raises the box (the worker was in ActivateDoc3 when it was seen in b1, b2, s3 and s4's
# Updates, in GetComponentByName in s5:596, in GetNextSubFeature in v24:89), and anything with the toggle off.
# swbuild.whats_wrong_shows_in_update reads these two for package B's sentence (True where either is True, False
# where both are False, None unmeasured).
WHATS_WRONG_OPENS_IN_UPDATE_WITH_USER_MATE_IN_ERROR_ON_2026 = False
WHATS_WRONG_OPENS_IN_UPDATE_WITH_USER_MATE_IN_ERROR_ON_2024 = True
WHATS_WRONG_OPENS_IN_UPDATE_WITH_PART_FEATURE_IN_ERROR_ON_2026 = False
WHATS_WRONG_OPENS_IN_UPDATE_WITH_PART_FEATURE_IN_ERROR_ON_2024 = True
#
# Whether that box blocks the Update (the coordinator's ruling, 2026-11-17, put to the user as the default they may
# change: the box is left alone, and the app behaves on 2024 as on 2026 — it does not suppress the box, change
# SolidWorks' setting or refuse because of it). WHATS_WRONG_IN_UPDATE_BLOCKS_ON_<year>; it gates
# swbuild.assembly_rebuild_settled.
# - 2024: False. In every Update run with something of the user's in error the box came up, went while the job went
#   on, nothing closing it, and the job returned, its results as they should be:
#   - b1, the mates in error with modes: up 97.45 to 120.08 s, a #32770 popup owned by SolidWorks' frame, the frame
#     enabled and a read on a second connection answering in 0.5 s while it was up, the calls growing (b1:103-104,
#     110, 142); the Update ok after 306 s (b1:133, 141), the app's bodies 6.6e-10 from their frames on record, the
#     user's components unmoved, the user's mates' codes and flags as before (b1:145), what it wrote read raw before
#     and after, the toggle True before and after (b1:143);
#   - b2, k3 before the ruling: up 17.57 to 22.59 s, the frame enabled and the second connection answering
#     (b2:597-598, 603); the job returned in 22.6 s, a failure then as the rebuild findings were None, naming the
#     keyway newly in error (b2:605-607, 612-614); it went as the job ended, so b2 alone does not tell "went by
#     itself" from "went with the job";
#   - s3, the mates in error: up 90.41 to 112.51 s, the Update ok at 300.9 s (s3:92-98);
#   - s4, the mates in error: up 99.92 to 123.01 s, ok at 314.4 s (s4:89-97, 105-107);
#   - s4, a feature in error in the user's own part: up 98.02 to 120.63 s, ok at 352.8 s, the False rebuilds laid to
#     the user (s4:155-163, 171-173);
#   - s5, k3 under the ruling: up 17.12 to 20.13 s, the job on until 22.7 s and ok, the keyway named the user's,
#     newly in error (s5:596-603, 607, 611-612);
#   and in each confirming run 0 up at the job's end and SolidWorks' frame enabled (s3:94, s4:93, 117, 159, s5:598).
#   A carried component in error was refused before any write as the rule says, foreseen by the footer (s4:174, 206,
#   211-212, 220-223).
#   Lifetimes 3 to 23 s in Updates; 0.5 s at the script's own activate-and-rebuild step (above).
#   Only b1 and b2 checked the frame and a second connection's read WHILE the box was up; the confirming runs check
#   the frame at the job's end. Not run: a person pressing FeatureXpert, or the "Display What's Wrong during rebuild"
#   box, during the job; a box that outlives its job (none did); a Build with the user's work in error (the again
#   sections never ran on 2024); the mate case on a gearbox without modes; an Update that puts by route (c1) with
#   the user's work in error and a lock carried; mate errors of other kinds than two over-defined distance mates;
#   any box longer than the 23 s seen; "show errors every rebuild" off.
# - 2026: False. No box opened at all in the closing run's Updates with the user's work in error (c1:91-105,
#   148-161, 786-800).
WHATS_WRONG_IN_UPDATE_BLOCKS_ON_2026 = False
WHATS_WRONG_IN_UPDATE_BLOCKS_ON_2024 = False

# ---------------------------------------------------------------------------------------------------------------------
# W9c's probes (ISSUE-1-PLAN §4 P1, M1's leftovers, S5 and P2) on SolidWorks 2026 34.1.1, as their review sets them
# (docs/notes-workbook/W9C-PROBES-REVIEW.md, 88a251e). w9c is probe/results/w9c-probes-sw2026-20261117-2.log (snapshot
# 37eee43) with w9c-probes-20261117-061130.json, the second run, which repeats the first run's p1, m1 and p2 and runs
# s5 whole. Every case under a watch that logs a dialog and answers none; none came but progress boxes and the
# notification box (w9c:9, 23, 53, 126, 212, 290, 320-321, 325).
#
# SolidWorks 2024 32.5.0, as the review's addendum sets it (W9C-PROBES-REVIEW.md, 9b85411 and 0df56da): w9c24 is
# probe/results/sw2024/w9c-probes-sw2024-20261117.log (snapshot 529f939, the 2026 run's own) with
# w9c-probes-20261117-062201.json, commit 9e77303. Every result line reads as 2026's but for the order s5 (a) lists the
# top-level components in (nothing uses it), two balloon-tip facts and the times; no What's Wrong box came up in any
# job. Each _ON_2024 below is set as its _ON_2026 twin, at the same scope, from w9c24's own lines as cited per finding;
# COMPONENT_STATE_PER_CONFIGURATION_ROUTE stays None on both for the same two reasons.
#
# Deleting a component (P1). Four cases, each on its own fresh copy, the assembly reopened from disk: G4 out of the
# 12 : 1 by three routes (w9c:14-35, 37-56, 58-76) and HighDog out of RangeBox with its three modes by the first
# (w9c:78-102). Judged by the reads, not the calls' returns (EditDelete returns None, w9c:33, 54, 100).
# - COMPONENT_DELETE_ROUTE: IComponent2.Select4(False, null, False), then IModelDoc2.EditDelete(). Clean on every
#   case (the component gone, every mate touching it gone by the MateGroup walk and by FeatureByName, every other mate
#   still there, nothing else moved, no error after; w9c:34, 55, 75, 101). The other two routes (the component's
#   feature selected, MATE_DELETE_ROUTE's form; DeleteSelection2(0)) were equally clean on the 12 : 1. Shown on a
#   gear with app mates only, alone in its file (G4) and sharing its file with another instance (HighDog beside
#   LowDog, all of whose mates stayed). Not shown: a component with a user mate or an in-context reference on it;
#   W9c refuses those before any delete (ISSUE-1-PLAN §2.1).
# - COMPONENT_DELETE_ROUTE_IN_EVERY_CONFIGURATION: True for that route only, on RangeBox's three modes, the assembly
#   reopened from disk, each mode shown and its components listed after the delete (the JSON's case 4
#   components_by_configuration). The other routes were not run with configurations, and the mates' error codes were
#   read in the active mode only (the review's should-fix 2 and 4).
# - COMPONENT_DELETE_TAKES_ITS_MATES: True. Covered: a coupling on in one mode only (RangeSlv engages HighDog), a
#   lock, a mesh, an axis and an along (w9c:34, 101).
# - COMPONENT_DELETE_KEEPS_OTHER_HANDLES: True within one epoch only: no configuration shown and no open between
#   keeping a handle and using it (epoch_kept equal to epoch_held_read, every held handle answering Name2 and
#   Transform2). After a show handles go stale anyway (ruling 9.4).
# - COMPONENT_DELETE_DIALOG: False, on every route (w9c:35, 56, 76, 102, 108).
# 2024: the same four cases clean by the same route, EditDelete returning None (w9c24:32-34, 55, 77, 102-104), the
# RangeBox case with its three modes (w9c24:103) and the proposals as on 2026 (w9c24:106-110).
COMPONENT_DELETE_ROUTE_ON_2026 = "select4-editdelete"
COMPONENT_DELETE_ROUTE_ON_2024 = "select4-editdelete"
COMPONENT_DELETE_ROUTE_IN_EVERY_CONFIGURATION_ON_2026 = True
COMPONENT_DELETE_ROUTE_IN_EVERY_CONFIGURATION_ON_2024 = True
COMPONENT_DELETE_TAKES_ITS_MATES_ON_2026 = True
COMPONENT_DELETE_TAKES_ITS_MATES_ON_2024 = True
COMPONENT_DELETE_KEEPS_OTHER_HANDLES_ON_2026 = True
COMPONENT_DELETE_KEEPS_OTHER_HANDLES_ON_2024 = True
COMPONENT_DELETE_DIALOG_ON_2026 = False
COMPONENT_DELETE_DIALOG_ON_2024 = False
#
# M1's leftovers: the user-mate kinds W9a left unread, each made on its own user component in a copy of RangeBox with
# H active (every flag read back as set in every mode, w9c:142) and read by the app's own swcom.mate_info and a quiet
# press, GetSaveFlag around every read (nothing marked, w9c:151). mate_info gave each one's swMateType_e and every
# entity's component, whole True (w9c:152-156), and each went into the recorded inventory (w9c:190-194):
# - M1_READS_CONCENTRIC (type 1, a face of a user part and the layout's axis), _LIMIT_DISTANCE (type 5) and
#   _LIMIT_ANGLE (type 6, plane to plane; their range in the definition's MaximumDistance/MinimumDistance and
#   MaximumAngle/MinimumAngle), _WIDTH (type 11, four faces; made only with the tab faces at mark 16, w9c:147-149),
#   _GEAR_ON_AN_APP_GEAR (type 10, a user component's axis to Sun's; the footer's judgement refuses it by name,
#   w9c:187). Read, not judged: concentric, both limits and width touched only the layout and user components, so
#   no put body was involved and the judgement could not have named them (the review's should-fix 3). What stays
#   refused is unchanged: any kind but a lock with an entity on a body Update puts.
# - M1_READS_SUBASSEMBLY_LEAF: True. A coincident to a leaf of a user sub-assembly reads the leaf's Name2 as the path
#   "UserSub-1/P2Sprocket-1" (w9c:322, 324), which swbuild's owner already splits to its top-level component. One
#   leaf, one coincident, the sub-assembly with no configurations of its own.
# 2024: every flag read back as set (w9c24:143), width again made only with the tab faces at mark 16 (w9c24:148-150),
# the reads marking nothing (w9c24:152), the same mate_info for each (w9c24:196-200) and the leaf read as the same path
# (w9c24:322, 324).
M1_READS_CONCENTRIC_ON_2026 = True
M1_READS_CONCENTRIC_ON_2024 = True
M1_READS_LIMIT_DISTANCE_ON_2026 = True
M1_READS_LIMIT_DISTANCE_ON_2024 = True
M1_READS_LIMIT_ANGLE_ON_2026 = True
M1_READS_LIMIT_ANGLE_ON_2024 = True
M1_READS_WIDTH_ON_2026 = True
M1_READS_WIDTH_ON_2024 = True
M1_READS_GEAR_ON_AN_APP_GEAR_ON_2026 = True
M1_READS_GEAR_ON_AN_APP_GEAR_ON_2024 = True
M1_READS_SUBASSEMBLY_LEAF_ON_2026 = True
M1_READS_SUBASSEMBLY_LEAF_ON_2024 = True
#
# ASSEMBLY_ENTITY_COMPONENT_IS_ROOT: a mate entity on the assembly's own plane names, through ReferenceComponent, the
# active configuration's root component (Name2 the assembly's title, "RangeBox"), not None. s5 (a) read UserAsm6's
# second entity, a distance to the assembly's own Front Plane, so (w9c:232, 260-262). swbuild's user-work read maps
# that root to the assembly's own (the review's must-fix 1); W9a's read before took it for a user component.
# 2024: the same, the root read 'RangeBox' (w9c24:233) and UserAsm6's entity on the assembly's Front Plane naming it
# (w9c24:261, 263). So the must-fix stands on both versions.
ASSEMBLY_ENTITY_COMPONENT_IS_ROOT_ON_2026 = True
ASSEMBLY_ENTITY_COMPONENT_IS_ROOT_ON_2024 = True
#
# For W9d (S5 and P2), on record now; nothing may rest on one that is None.
# - PERSIST_REFERENCE_ROUTE_FOR_REFERENCE_FEATURES: GetPersistReference3 on the part-level feature, reached through
#   the component's GetModelDoc2, and GetObjectByPersistReference3 in that part: 13 entities read and each resolved to
#   its own feature (w9c:265). Reference features only: the axes and planes of user parts and the layout. Not shown: a
#   face, an edge or a vertex (the review's must-fix 3), the assembly-context route (read only), 2024.
# - MATE_REMAKE_ON_AXES_PLANES_AND_LOCKS_ROUTE: AddMate5 from IMate2's Type, Alignment and Flipped and the
#   definition's values, on entities found by part-level reference, the layout's name, the assembly's plane by tree
#   order or the whole component: ten mates remade with equal definitions and frames, coincident x5 (axis to axis),
#   lock x3 (whole components), distance x2 (plane to plane, one to the assembly's own Front Plane by tree order) and
#   angle x1, all at alignment 0 or 2, none flipped, into a one-configuration assembly (w9c:267-279). Not covered:
#   concentric, parallel, perpendicular, tangent, limit distance and angle, gear, any face, edge or vertex, a flipped
#   mate, a leaf inside a sub-assembly, a mate's flag set per configuration.
# - COMPONENT_STATE_PER_CONFIGURATION_ROUTE: None. IsSuppressed2 on the component's feature read L wrong; each
#   configuration's GetRootComponent3(True) read right, the configuration not shown included, and marked the
#   assembly (w9c:281-284; the review's must-fix 2). GetRootComponent3(False) is not tried.
# - OPEN_READ_ONLY_ROUTE_WHEN_NOT_OPEN: OpenDoc6(path, assembly, Silent | ReadOnly) on an assembly not open: the
#   document read-only, its flag False, errors 0, components opened (a progress box only; w9c:290-291). On one already
#   open it returns that document, warning 128, not read-only, and its effect on the flag is not shown (w9c:288).
# - OPEN_READ_ONLY_DIALOG: False, both opens (w9c:288, 291).
# - SUBASSEMBLY_INSERT_ROUTE: OpenDoc6 the sub-assembly, then AddComponent5, into an assembly with modes; its children
#   under the path "UserSub-1/P2Sprocket-1", the leaf mate's flags off in every mode (w9c:322-323). Not read: the
#   opened sub-assembly's own save flag, the inserted one's state per mode.
# - SUBASSEMBLY_MISSING_REFERENCE_DIALOG: False, for a Silent open (OpenDoc6 with swOpenDocOptions_Silent) of a
#   sub-assembly whose part file is gone, and for its insert: no dialog in either, nor 10 s after (w9c:326-328).
# - SUBASSEMBLY_MISSING_PART_READS: what that open read: errors 2, warnings 0; the missing child GetSuppression2 0,
#   its stored path kept, no document; the sub-assembly modified (save flag True) straight after the open and after
#   the settle; inserted, the child the same under "UserSubMissing-1/P2Missing-1" (w9c:326-327).
# 2024, each as on 2026 at the same scope: 13 feature entities read and resolved, still no face (w9c24:266-267); the
# same ten remade equal, every frame at 0.0 (w9c24:279-280); IsSuppressed2 read L wrong and GetRootComponent3(True)
# read right but marked RangeBox.SLDASM, so no route (w9c24:282-285); the read-only open when not open, already open
# reading as on 2026 (w9c24:289, 292-294); the sub-assembly insert (w9c24:322-323); the missing part's Silent open
# and insert, errors 2, the child suppressed with no document, no dialog (w9c24:325-327).
PERSIST_REFERENCE_ROUTE_FOR_REFERENCE_FEATURES_ON_2026 = (
    "GetPersistReference3 on the part-level feature, through the component's GetModelDoc2")
PERSIST_REFERENCE_ROUTE_FOR_REFERENCE_FEATURES_ON_2024 = PERSIST_REFERENCE_ROUTE_FOR_REFERENCE_FEATURES_ON_2026
MATE_REMAKE_ON_AXES_PLANES_AND_LOCKS_ROUTE_ON_2026 = (
    "AddMate5 from IMate2 Type, Alignment, Flipped and the definition's values")
MATE_REMAKE_ON_AXES_PLANES_AND_LOCKS_ROUTE_ON_2024 = MATE_REMAKE_ON_AXES_PLANES_AND_LOCKS_ROUTE_ON_2026
COMPONENT_STATE_PER_CONFIGURATION_ROUTE_ON_2026 = None
COMPONENT_STATE_PER_CONFIGURATION_ROUTE_ON_2024 = None
OPEN_READ_ONLY_ROUTE_WHEN_NOT_OPEN_ON_2026 = "OpenDoc6(path, assembly, Silent | ReadOnly)"
OPEN_READ_ONLY_ROUTE_WHEN_NOT_OPEN_ON_2024 = "OpenDoc6(path, assembly, Silent | ReadOnly)"
OPEN_READ_ONLY_DIALOG_ON_2026 = False
OPEN_READ_ONLY_DIALOG_ON_2024 = False
SUBASSEMBLY_INSERT_ROUTE_ON_2026 = "OpenDoc6 the sub-assembly, then AddComponent5"
SUBASSEMBLY_INSERT_ROUTE_ON_2024 = "OpenDoc6 the sub-assembly, then AddComponent5"
SUBASSEMBLY_MISSING_REFERENCE_DIALOG_ON_2026 = False
SUBASSEMBLY_MISSING_REFERENCE_DIALOG_ON_2024 = False
SUBASSEMBLY_MISSING_PART_READS_ON_2026 = (
    "the open's errors 2; the child suppressed (0), its path kept, no document; the sub-assembly marked modified")
SUBASSEMBLY_MISSING_PART_READS_ON_2024 = SUBASSEMBLY_MISSING_PART_READS_ON_2026
#
# W9c's gates (W9C-INTERFACES.md §8, the coordinator's ruling C7, 2026-11-17): each new kind of write Update makes in
# place is gated by its own per-version finding, None until W9c's full build (the plan's demonstration, RangeBox to
# RangeBox_Fixed, then a mode added and one removed) reads it clean on that version, patched True in that run's
# process for the measurement only, as W9a's nocarrier was. Nothing measured them; no run is cited. A step whose
# finding is not True refuses before any write, naming it.
# - EXTERNAL_REFERENCES_READ (M4): an external-references read of the user's parts, so a removal can tell whether a
#   user part holds an in-context reference to the gear removed. While None, a removal refuses whenever any component
#   of the user's is in the assembly (C4).
# - UPDATE_INSERTS_A_GEAR (M5, M6): a gear's part inserted into a saved, reopened assembly (with modes or without),
#   placed and mated as the build mates it, every new mate's flag and the component's state read back in every
#   configuration.
# - UPDATE_MAKES_MATES_WITH_MODES (M6): a gear mate of a gearbox with modes made again (lifting ruling 9.16), its flags
#   set and read back in every configuration.
# - UPDATE_BANDS_IN_PLACE (M8): band globals and the relief features added to a built sleeve's part after the user's
#   features.
# - UPDATE_ADDS_A_MODE, UPDATE_REMOVES_A_MODE (M10): a configuration added by Update (copied from the active one, every
#   app mate's flag and slide value set and read back there) and one deleted, in a reopened assembly with the user's
#   items.
EXTERNAL_REFERENCES_READ_ON_2026 = None
EXTERNAL_REFERENCES_READ_ON_2024 = None
UPDATE_INSERTS_A_GEAR_ON_2026 = None
UPDATE_INSERTS_A_GEAR_ON_2024 = None
UPDATE_MAKES_MATES_WITH_MODES_ON_2026 = None
UPDATE_MAKES_MATES_WITH_MODES_ON_2024 = None
UPDATE_BANDS_IN_PLACE_ON_2026 = None
UPDATE_BANDS_IN_PLACE_ON_2024 = None
UPDATE_ADDS_A_MODE_ON_2026 = None
UPDATE_ADDS_A_MODE_ON_2024 = None
UPDATE_REMOVES_A_MODE_ON_2026 = None
UPDATE_REMOVES_A_MODE_ON_2024 = None
#
# Split from the two above at the demonstration's ruling (2026-11-17: a finding gates only what was measured, and no
# legal edit of the demonstration's fixtures reaches these):
# - UPDATE_MAKES_A_NEW_COUPLING: a coupling or sliding mesh newly made by Update between components on record
#   (InPlace.new_mates), made in the first mode it is on in and its flag set and read back in every configuration.
#   UPDATE_MAKES_MATES_WITH_MODES keeps the remake of a gear mate of a gearbox with modes (ruling 9.16 lifted); an
#   added gear's own mates are UPDATE_INSERTS_A_GEAR's.
# - UPDATE_SUPPRESSES_THE_RELIEF: a built sleeve's bands taken away (the Relief loft cut suppressed, a part feature's
#   IFeature.SetSuppression2 through Session.suppress_feature) and bands given back (the relief turned back on, the
#   band globals set, no second relief). UPDATE_BANDS_IN_PLACE keeps bands given (the globals and the relief made
#   after the user's features).
UPDATE_MAKES_A_NEW_COUPLING_ON_2026 = None
UPDATE_MAKES_A_NEW_COUPLING_ON_2024 = None
UPDATE_SUPPRESSES_THE_RELIEF_ON_2026 = None
UPDATE_SUPPRESSES_THE_RELIEF_ON_2024 = None
#
# ---------------------------------------------------------------------------------------------------------------------
# W9d: Build again… carries the user's work (W9D-INTERFACES.md §8). Every name below is None on both versions until a
# reviewed SolidWorks log sets it: the reads from W9d's probe (probe/w9d_probes.py, W9D-PROBES.md), the writes from
# the demonstration M9 (patched in that run's process for the measurement only, as W9a's nocarrier and W9c's gates
# were). Nothing measured them; no run is cited. One not settled keeps its items from being carried, named with the
# finding, and never stops the build.
# - OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN (True): the close of a read-only document, shown or not, under no dialog; gates
#   the not-open read at all and its per-mode show (probe state (h)).
# - OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS (True): the read-only open leaves the app's documents already open as they
#   were, one with changes included; gates the not-open read when any document is open (probe state (g)).
# - FILE_VERSION_READ (a route string): the closed file's last saved version (ISldWorks.VersionHistory); the not-open
#   read opens only when it is set and reads the running version (probe state (v)).
# - COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED (True): the per-mode state route reads an open assembly's unsaved
#   change (probe state (e)).
# - PERSIST_REFERENCE_ROUTE_FOR_FACES / _FOR_EDGES / _FOR_VERTICES (a route string): tier 1 on faces, edges, vertices
#   (probe faces (b); vertices: nothing in W9d).
# - PERSIST_REFERENCE_SURVIVES_RELOAD (True): a part-level reference resolved after its part is closed and opened
#   again; tier 1 on the not-open path (probe faces (d)).
# - COAXIAL_FACE_READ (True): a face on an app gear read coaxial with its Gear Axis (probe faces (b)).
# - REFERENCED_CONFIGURATION_READ (True): IComponent2.ReferencedConfiguration read right (M9's Sprocket-11 sets it).
# - VIRTUAL_READ, PATTERN_INSTANCE_READ (True): IComponent2.IsVirtual, IsPatternInstance (read negative only).
# - ORIGIN_ENTITY_READ (True): an origin as a mate entity (nothing in W9d).
# - SUBASSEMBLY_OPEN_MARKS, SUBASSEMBLY_OPEN_MARKS_WHEN_LOADED (settled False): opening a healthy user sub-assembly,
#   not loaded or loaded as a component, marks nothing (probe sub (a), (c)).
# - SUBASSEMBLY_READ_ONLY_INSERT (True): a sub-assembly opened read-only, then inserted (probe sub (b)).
# - CARRY_INSERT_MARKS_USER_DOCUMENTS (a fact, True or False): an insert marks the user's documents; True adds a
#   sentence (probe faces (c)).
# - CARRY_INSERTS (True): user parts inserted, placed, fixed, their states set in every mode and read back (M9).
# - CARRY_INSERTS_IN_A_CONFIGURATION (True): an insert in a referenced configuration (M9).
# - CARRY_INSERTS_A_SUBASSEMBLY (True): a user sub-assembly inserted by its file (M9, if its fixture holds one).
# - CARRY_REMAKE_KINDS (a tuple of kind words): the kinds of mate M9 made again clean (D4).
# - CARRY_GEAR_MATE_ON_AN_APP_GEAR (True): a user gear mate on an app gear's Gear Axis, ratio and sense read back (M9).
# - CARRY_REMAKES_ON_A_LEAF (True): a mate on a leaf of a user sub-assembly (nothing in W9d).
OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_2026 = None
OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_2024 = None
OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS_ON_2026 = None
OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS_ON_2024 = None
FILE_VERSION_READ_ON_2026 = None
FILE_VERSION_READ_ON_2024 = None
COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED_ON_2026 = None
COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED_ON_2024 = None
PERSIST_REFERENCE_ROUTE_FOR_FACES_ON_2026 = None
PERSIST_REFERENCE_ROUTE_FOR_FACES_ON_2024 = None
PERSIST_REFERENCE_ROUTE_FOR_EDGES_ON_2026 = None
PERSIST_REFERENCE_ROUTE_FOR_EDGES_ON_2024 = None
PERSIST_REFERENCE_ROUTE_FOR_VERTICES_ON_2026 = None
PERSIST_REFERENCE_ROUTE_FOR_VERTICES_ON_2024 = None
PERSIST_REFERENCE_SURVIVES_RELOAD_ON_2026 = None
PERSIST_REFERENCE_SURVIVES_RELOAD_ON_2024 = None
COAXIAL_FACE_READ_ON_2026 = None
COAXIAL_FACE_READ_ON_2024 = None
REFERENCED_CONFIGURATION_READ_ON_2026 = None
REFERENCED_CONFIGURATION_READ_ON_2024 = None
VIRTUAL_READ_ON_2026 = None
VIRTUAL_READ_ON_2024 = None
PATTERN_INSTANCE_READ_ON_2026 = None
PATTERN_INSTANCE_READ_ON_2024 = None
ORIGIN_ENTITY_READ_ON_2026 = None
ORIGIN_ENTITY_READ_ON_2024 = None
SUBASSEMBLY_OPEN_MARKS_ON_2026 = None
SUBASSEMBLY_OPEN_MARKS_ON_2024 = None
SUBASSEMBLY_OPEN_MARKS_WHEN_LOADED_ON_2026 = None
SUBASSEMBLY_OPEN_MARKS_WHEN_LOADED_ON_2024 = None
SUBASSEMBLY_READ_ONLY_INSERT_ON_2026 = None
SUBASSEMBLY_READ_ONLY_INSERT_ON_2024 = None
CARRY_INSERT_MARKS_USER_DOCUMENTS_ON_2026 = None
CARRY_INSERT_MARKS_USER_DOCUMENTS_ON_2024 = None
CARRY_INSERTS_ON_2026 = None
CARRY_INSERTS_ON_2024 = None
CARRY_INSERTS_IN_A_CONFIGURATION_ON_2026 = None
CARRY_INSERTS_IN_A_CONFIGURATION_ON_2024 = None
CARRY_INSERTS_A_SUBASSEMBLY_ON_2026 = None
CARRY_INSERTS_A_SUBASSEMBLY_ON_2024 = None
CARRY_REMAKE_KINDS_ON_2026 = None
CARRY_REMAKE_KINDS_ON_2024 = None
CARRY_GEAR_MATE_ON_AN_APP_GEAR_ON_2026 = None
CARRY_GEAR_MATE_ON_AN_APP_GEAR_ON_2024 = None
CARRY_REMAKES_ON_A_LEAF_ON_2026 = None
CARRY_REMAKES_ON_A_LEAF_ON_2024 = None
