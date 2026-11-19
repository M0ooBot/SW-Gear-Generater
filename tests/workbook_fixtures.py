"""W8's two fixtures as specs (W8-PLAN §2.1, §2.2): the E4 transfer case (needs W7's planetary) and
TransferCase_Parallel (the same with its low range on a reverted layshaft). Every shaft is on the frame along Z+
unless said; the Box's pressure angle is 20° and its efficiency 98 %. The demonstration writes the same rows through
``model.to_book`` / ``xlsx.write_new`` (``write``). ISSUE-1-PLAN §3's ``RangeBox`` (the issue's box as written) and
``RangeBox_Fixed`` (after W9b) are here too."""

from dataclasses import replace

from gear_generator.spec import PROCESS_MACHINED
from gear_generator.workbook.model import Box, Gear, GearboxSpec, Mesh, Mode, Shaft


def machined(spec: GearboxSpec) -> GearboxSpec:
    """``spec`` with its Box's Process set to machined (PLAN-PRINTED §2.7, F1-0): how every test marks a read of a
    committed workbook, none of which has a Process row. Once package B keeps the user's blank Process as read, such a
    read is printed (a blank with no record); marked here, it keeps what the test pins. Before B it changes nothing,
    since a read's Box is then machined already. None (a read that failed) is passed through."""
    if spec is None:
        return spec
    return replace(spec, box=replace(spec.box, process=PROCESS_MACHINED))


def machined_reads(monkeypatch) -> None:
    """Every read a Workbook window or ``link.Link`` makes in this test marked :func:`machined`: for the window tests
    that read a committed workbook (or a copy of one) themselves, where no read is in the test's hands."""
    from gear_generator.workbook import link
    from_book = link.from_book

    def read(book):
        spec, diagnostics = from_book(book)
        return machined(spec), diagnostics

    monkeypatch.setattr(link, "from_book", read)

SLIDERS = ("RangeSlv", "ModeSlv")
MODES = (Mode("2H", (("RangeSlv", "H"), ("ModeSlv", "2WD")), "road", row=2),
         Mode("4H", (("RangeSlv", "H"), ("ModeSlv", "4WD")), "", row=3),
         Mode("N", (("RangeSlv", "N"), ("ModeSlv", "2WD")), "towing", row=4),
         Mode("4L", (("RangeSlv", "L"), ("ModeSlv", "4WD")), "crawl", row=5))


def _gear(gear, shaft, at, kind, teeth, module, face, slides="", side="", row=0):
    return Gear(gear, shaft, at, kind, side, teeth, module, "", face, "", slides=slides, row=row)


def _rear_and_front(first_row):
    """The rows both fixtures share: the range sleeve and the dogs it engages, and the front drive."""
    r = first_row
    return (_gear("RangeSlv", "Rear", "60", "sleeve", "30", "1.5", "8", "H=-10, N=0, L=+10", row=r),
            _gear("FrontDog", "FrontDrv", "110", "dog", "30", "1.5", "6", row=r + 1),
            _gear("ModeSlv", "Rear", "100", "sleeve", "30", "1.5", "8", "2WD=0, 4WD=+10", row=r + 2),
            _gear("FDrive", "FrontDrv", "130", "spur", "30", "2", "10", row=r + 3),
            _gear("FIdler", "Idler", "130", "spur", "20", "2", "10", row=r + 4),
            _gear("FOut", "Front", "130", "spur", "30", "2", "10", row=r + 5))


def transfer_case_parallel() -> GearboxSpec:
    """W8-PLAN §2.2: the low range on a reverted layshaft (17 : 34 twice at 51 mm, 4 : 1), every shaft a frame shaft."""
    shafts = (Shaft("In", "frame", "0", "0", "0", "Z+", "input", "", "1500", "10", row=2),
              Shaft("Lay", "frame", "0", "-51", "0", "Z+", "", row=3),
              Shaft("Lo", "frame", "0", "0", "0", "Z+", "", row=4),
              Shaft("Rear", "frame", "0", "0", "0", "Z+", "output", row=5),
              Shaft("FrontDrv", "frame", "0", "0", "0", "Z+", "", row=6),
              Shaft("Idler", "frame", "50", "0", "0", "Z+", "", row=7),
              Shaft("Front", "frame", "100", "0", "0", "Z+", "output", row=8))
    gears = (_gear("InPin", "In", "10", "spur", "17", "2", "10", row=2),
             _gear("InDog", "In", "50", "dog", "30", "1.5", "6", row=3),
             _gear("LayGear", "Lay", "10", "spur", "34", "2", "10", row=4),
             _gear("LayPin", "Lay", "30", "spur", "17", "2", "10", row=5),
             _gear("LoGear", "Lo", "30", "spur", "34", "2", "10", row=6),
             _gear("LoDog", "Lo", "70", "dog", "30", "1.5", "6", row=7)) + _rear_and_front(8)
    meshes = (Mesh("InPin", "LayGear", row=2), Mesh("LayPin", "LoGear", row=3), Mesh("FDrive", "FIdler", row=4),
              Mesh("FIdler", "FOut", row=5))
    return GearboxSpec(box=Box(name="TransferCase_Parallel", pressure_angle="20", efficiency="98"), shafts=shafts,
                       gears=gears, meshes=meshes, modes=MODES, sliders=SLIDERS)


def e4_transfer_case() -> GearboxSpec:
    """W8-PLAN §2.1: canvas E4, E3's 4 : 1 planetary (sun on In, ring held) as the low range."""
    shafts = (Shaft("In", "frame", "0", "0", "0", "Z+", "input", "", "1500", "10", row=2),
              Shaft("Carrier", "frame", "0", "0", "0", "Z+", "", row=3),
              Shaft("Planet", "Carrier", "24", "0", "0", "", "", "3", row=4),
              Shaft("Ring", "frame", "0", "0", "0", "Z+", "fixed", row=5),
              Shaft("Rear", "frame", "0", "0", "0", "Z+", "output", row=6),
              Shaft("FrontDrv", "frame", "0", "0", "0", "Z+", "", row=7),
              Shaft("Idler", "frame", "50", "0", "0", "Z+", "", row=8),
              Shaft("Front", "frame", "100", "0", "0", "Z+", "output", row=9))
    gears = (_gear("Sun", "In", "20", "spur", "24", "1", "10", row=2),
             _gear("Pl", "Planet", "20", "spur", "24", "1", "10", row=3),
             _gear("Ring", "Ring", "20", "spur", "72", "1", "10", side="internal", row=4),
             _gear("InDog", "In", "50", "dog", "30", "1.5", "6", row=5),
             _gear("LoDog", "Carrier", "70", "dog", "30", "1.5", "6", row=6)) + _rear_and_front(7)
    meshes = (Mesh("Sun", "Pl", row=2), Mesh("Pl", "Ring", row=3), Mesh("FDrive", "FIdler", row=4),
              Mesh("FIdler", "FOut", row=5))
    return GearboxSpec(box=Box(name="TransferCase_E4", pressure_angle="20", efficiency="98"), shafts=shafts,
                       gears=gears, meshes=meshes, modes=MODES, sliders=SLIDERS)


def range_box() -> GearboxSpec:
    """ISSUE-1-PLAN §3, ``RangeBox``: the issue's two-speed planetary range box as the issue wrote it (before W9b). The
    sun on Input drives three planets on Carrier inside a fixed ring; RangeSlv on Output engages HighDog (Input) in H,
    nothing in N, LowDog (Carrier) in L. Module 1.25 throughout, the Box's 20° and 98 %."""
    shafts = (Shaft("Input", "frame", "0", "0", "0", "Z+", "input", "", "1500", "10", row=2),
              Shaft("Carrier", "frame", "0", "0", "0", "Z+", "", row=3),
              Shaft("Planet", "Carrier", "26.25", "0", "0", "", "", "3", row=4),
              Shaft("Ring", "frame", "0", "0", "0", "Z+", "fixed", row=5),
              Shaft("Output", "frame", "0", "0", "0", "Z+", "output", row=6))
    gears = (_gear("Sun", "Input", "10.5", "spur", "29", "1.25", "10", row=2),
             _gear("Planet", "Planet", "10.5", "spur", "13", "1.25", "10", row=3),
             _gear("Ring", "Ring", "10.5", "spur", "55", "1.25", "10", side="internal", row=4),
             _gear("HighDog", "Input", "-32", "dog", "17", "1.25", "5", row=5),
             _gear("LowDog", "Carrier", "-17", "dog", "17", "1.25", "5", row=6),
             _gear("RangeSlv", "Output", "-24.5", "sleeve", "17", "1.25", "10", "H=-5, N=0, L=+5", row=7))
    meshes = (Mesh("Sun", "Planet", row=2), Mesh("Planet", "Ring", row=3))
    modes = (Mode("H", (("RangeSlv", "H"),), "", row=2),
             Mode("N", (("RangeSlv", "N"),), "", row=3),
             Mode("L", (("RangeSlv", "L"),), "", row=4))
    return GearboxSpec(box=Box(name="RangeBox", pressure_angle="20", efficiency="98"), shafts=shafts, gears=gears,
                       meshes=meshes, modes=modes, sliders=("RangeSlv",))


def range_box_fixed() -> GearboxSpec:
    """ISSUE-1-PLAN §3, ``RangeBox_Fixed`` (after W9b): ``range_box`` with the issue put right — RangeSlv 26 mm long at
    −35 with a 5 mm toothed band at each end (the relief between, 16 mm long, Ø 25.0), sliding H −7.5, N 0, L +7.5; and
    Hub, a 17-tooth hub on Output at −45.5, 20 mm long (−55.5…−35.5), under RangeSlv's start band in every mode."""
    made = range_box()
    sleeve = next(g for g in made.gears if g.id == "RangeSlv")
    sleeve = replace(sleeve, at="-35", face_width="26", slides="H=-7.5, N=0, L=+7.5", start_band="5", end_band="5")
    hub = _gear("Hub", "Output", "-45.5", "hub", "17", "1.25", "20", row=8)
    gears = tuple(sleeve if g.id == "RangeSlv" else g for g in made.gears) + (hub,)
    return replace(made, box=replace(made.box, name="RangeBox_Fixed"), gears=gears)
