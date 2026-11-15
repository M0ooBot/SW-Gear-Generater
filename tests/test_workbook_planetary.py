"""A workbook's planetary stage (W7, ``workbook/planetary.py``): the pieces W7's interface commit wrote — copy names,
copy offsets, the carrier's id and stem, mesh links measured against a carrier. Agent B adds the planning tests
(W7-PLAN §5.5)."""

import math

import pytest

from gear_generator import swbuild
from gear_generator.workbook import layout, motion, planetary
from gear_generator.workbook.planetary import copy_id, copy_of, copy_offsets


@pytest.mark.parametrize("name, k, copies, expected", [("Planet", 1, 1, "Planet"), ("Planet", 2, 3, "Planet copy 2"),
                                                       ("P", 3, 3, "P copy 3"), ("P-2_b", 1, 4, "P-2_b copy 1")])
def test_a_copy_is_named_for_its_row_and_its_number(name, k, copies, expected):
    assert copy_id(name, k, copies) == expected
    assert copy_of(expected) == ((name, k) if copies > 1 else (name, 0))


@pytest.mark.parametrize("name, k, copies", [("Planet", 0, 3), ("Planet", 4, 3), ("Planet", 1, 0), ("", 1, 1)])
def test_a_copy_that_does_not_exist_is_refused(name, k, copies):
    with pytest.raises(ValueError, match=r"\.$"):
        copy_id(name, k, copies)


def test_copy_offsets_stand_evenly_round_the_carriers_own_axis():
    """W7-PLAN §4.1: (18, 0, 0) in 3 gives (18, 0), (−9, 15.588457268), (−9, −15.588457268) in the carrier's frame."""
    assert copy_offsets(18.0, 0.0, 0.0, 3) == ((18.0, 0.0, 0.0), (-9.0, 15.58845726812, 0.0),
                                                (-9.0, -15.58845726812, 0.0))
    four = copy_offsets(18.0, 0.0, 0.0, 4)
    assert four == ((18.0, 0.0, 0.0), (0.0, 18.0, 0.0), (-18.0, 0.0, 0.0), (0.0, -18.0, 0.0))
    assert all(math.copysign(1.0, v) > 0 for point in four for v in point if v == 0)        # no -0.0
    assert copy_offsets(18.0, -3.0, 2.5, 1) == ((18.0, -3.0, 2.5),)
    p3 = copy_offsets(19.5, 0.0, 0.0, 3)
    assert p3[1] == pytest.approx((-9.75, 16.887495374, 0.0)) and p3[2] == pytest.approx((-9.75, -16.887495374, 0.0))
    with pytest.raises(ValueError):
        copy_offsets(18.0, 0.0, 0.0, 0)


def test_a_carrier_goes_by_its_shaft_and_its_part_by_the_gearbox_name():
    assert layout.carrier_id("C") == "C carrier"
    assert layout.carrier_stem("Planetary_4to1", 0, "C") == "Planetary_4to1_C_Carrier"
    assert layout.carrier_stem("Planetary_4to1", 2, "C") == "Planetary_4to1_r2_C_Carrier"
    assert motion.mate_name(motion.AXIS, ("C carrier",), "C") == "C carrier on C Axis"
    assert motion.mate_name(motion.LOCK, ("C carrier", "CarrierGear")) == "CarrierGear locked to C carrier"
    assert motion.mate_name(motion.AXIS, ("Planet copy 2",), "P copy 2") == "Planet copy 2 on P copy 2 Axis"
    with pytest.raises(ValueError):
        layout.carrier_id("")


def test_mesh_links_carry_the_carrier_a_mesh_is_measured_against():
    """The fixture's sun mesh (c = +1, k = −1) and ring mesh (c = −1, k = +1/3), relative to C."""
    teeth = {"Sun": 18, "Planet copy 1": 18, "Ring": 54}
    meshes = [("Sun", "Planet copy 1"), ("Planet copy 1", "Ring")]
    sense = {("Sun", "Planet copy 1"): 1, ("Planet copy 1", "Ring"): -1}
    links = motion.mesh_links(meshes, teeth, sense, carrier_of={m: "C carrier" for m in meshes})
    assert links == (swbuild.MeshLink("Sun", "Planet copy 1", -1.0, 20.0, "C carrier"),
                     swbuild.MeshLink("Planet copy 1", "Ring", 1 / 3, 360 / 54, "C carrier"))
    assert motion.mesh_links(meshes[:1], teeth, sense)[0].carrier == ""


def test_the_stage_is_a_frozen_record_of_its_members():
    stage = planetary.Stage("C", "Sun", "Ring", "Planet", "P", 3, "R")
    assert (stage.carrier, stage.copies, stage.held) == ("C", 3, "R")
