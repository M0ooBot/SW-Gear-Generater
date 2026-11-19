"""The form as data.

Every field of the form is kept as the text the user typed, because ``""``
means something different from ``"0"`` — a blank backlash is the
``0.3 × Module`` equation, while ``"0"`` is no backlash at all — and because a
number that round-trips through ``float`` comes back as ``25.0`` when the user
typed ``25``. Parsing happens in the methods below, each of which names its
field in the sentence it raises.

Output folder and templates are not here: like the output folder in Airfoil
Converter they are app state, remembered across runs, not a property of a gear.
"""

from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass, field, fields, replace
from typing import Any, Dict, Optional, Sequence, Tuple


KIND_SPUR = "spur"
KIND_HELICAL = "helical"
KIND_HERRINGBONE = "herringbone"
KIND_BEVEL = "bevel"
HELICAL_KINDS = (KIND_HELICAL, KIND_HERRINGBONE)
TEETH_EXTERNAL = "external"
TEETH_INTERNAL = "internal"
TEETH_SIDES = (TEETH_EXTERNAL, TEETH_INTERNAL)
MESH_EXTERNAL = "external"
MESH_INTERNAL = "internal"
MESHES = (MESH_EXTERNAL, MESH_INTERNAL)
SHAFTS_PARALLEL = "parallel"
SHAFTS_CROSSED = "crossed"
SHAFTS = (SHAFTS_PARALLEL, SHAFTS_CROSSED)
HANDS_SAME = "same"
HANDS_OPPOSITE = "opposite"
HAND_PAIRINGS = (HANDS_SAME, HANDS_OPPOSITE)
MOTION_FIXED = "fixed"
MOTION_GEAR_MATE = "gear mate"
MOTIONS = (MOTION_FIXED, MOTION_GEAR_MATE)
HAND_RIGHT = "right"
HAND_LEFT = "left"
HANDS = (HAND_RIGHT, HAND_LEFT)
RECIPE_INVOLUTE = "A"
RECIPE_ARCS = "B"
RECIPES = (RECIPE_INVOLUTE, RECIPE_ARCS)

MODE_SINGLE = "single"
MODE_PAIR = "pair"
MODES = (MODE_SINGLE, MODE_PAIR)


BAND_FIELDS = ("start_band", "end_band")     # W9b: GearSpec.to_dict leaves them out while both are blank

# F1 (PLAN-PRINTED §1.1; docs/notes-printed/F1-INTERFACES.md): how a gear is made. A spec that does not say, in code or
# in a record written before F1, is machined; only the form's Process row and a Box sheet's blank are the user's
# Printed. GearSpec.to_dict leaves both fields out of any spec that is not printed, so a machined record is W9's.
PROCESS_PRINTED = "printed"
PROCESS_MACHINED = "machined"
PROCESSES = (PROCESS_PRINTED, PROCESS_MACHINED)
PROCESS_FIELDS = ("process", "nozzle")
NOZZLE_DEFAULT = 0.4          # mm, a printed gear's line width when its Nozzle is blank
PRINTED_STEM_MARK = "_P"      # D10: a part built printed ends _P (Gear_m1.5_N25_P)

# F3 (PLAN-PRINTED §4.1, §4.2; docs/notes-printed/F3-INTERFACES.md): the bore as cut. A Bore allowance is on the
# diameter, so the hole is cut at Bore + allowance and Bore stays the shaft's size; a Drive of flat cuts a D whose Flat
# is the shaft's size across its flat. GearSpec.to_dict leaves the three out at their defaults, so a record without
# them is byte for byte what it was before F3.
DRIVE_ROUND = "round"
DRIVE_FLAT = "flat"
DRIVES = (DRIVE_ROUND, DRIVE_FLAT)
BORE_FIELDS = ("bore_allowance", "drive", "flat")
RECORD_ONLY_FIELDS = ("built_allowance",)   # set by as_built only: never on a form, never written, never compared
BORE_ALLOWANCE_GLOBAL = "Bore Allowance"    # spur.BORE_ALLOWANCE, the part's global; here so as_built can read it
BORE_FLAT_GLOBAL = "Bore Flat"              # spur.BORE_FLAT
# mm on the diameter: what a blank Bore allowance is for a printed part not yet built. A placeholder until the user's
# coupons give their printer's figure (§3.2, V1), which replaces this one constant (spur.BORE_ALLOWANCE_DEFAULT is it).
BORE_ALLOWANCE_DEFAULT = 0.2


class InputError(Exception):
    """A field on the form could not be read."""


def parse_float(text: str, name: str) -> float:
    stripped = str(text).strip()
    if not stripped:
        raise InputError(f"{name} is empty; it needs a number.")
    try:
        value = float(stripped)
    except ValueError:
        raise InputError(f"{name} must be a number (got {stripped!r}).") from None
    if not math.isfinite(value):
        raise InputError(f"{name} must be a finite number (got {stripped!r}).")
    return value


def parse_whole(text: str, name: str) -> int:
    value = parse_float(text, name)
    if abs(value - round(value)) > 1e-9:
        raise InputError(f"{name} must be a whole number (got {str(text).strip()!r}).")
    return int(round(value))


def parse_ratio(text: str) -> float:
    """``"3"``, ``"3:1"``, ``"1:3"``, ``"0.333"`` -> N driven / N driver.

    ``a:b`` reads as a over b, so ``3:1`` is 3 and ``1:3`` is a third — the
    driven gear the smaller one.
    """
    stripped = str(text).strip()
    if not stripped:
        raise InputError("Ratio is empty; type it as 3, or as 1:3.")
    if ":" in stripped:
        left, _, right = stripped.partition(":")
        a = parse_float(left, "Ratio")
        b = parse_float(right, "Ratio")
        if a <= 0 or b <= 0:
            raise InputError(f"Both sides of the ratio must be more than zero (got {stripped!r}).")
        return a / b
    value = parse_float(stripped, "Ratio")
    if value <= 0:
        raise InputError(f"Ratio must be more than zero (got {stripped!r}).")
    return value


def sanitize_stem(stem: str, fallback: str = "Gear") -> str:
    """A name reduced to something legal as a file name and a feature name."""
    cleaned = re.sub(r'[<>:"/\\|?*@]', "_", str(stem)).strip().strip(".")
    return cleaned or fallback


def _number_text(text: str) -> str:
    """A typed number as it goes into a file name: ``1.50`` -> ``1.5``.

    Kept free of :mod:`gears` so the gear kinds can import this module.
    """
    try:
        value = float(str(text).strip())
    except ValueError:
        return str(text).strip()
    if not math.isfinite(value):
        return str(text).strip()
    text = f"{value:.9f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def _angle_text(text: str) -> str:
    """A helix angle as it goes into a file name: two decimals at most, so a solved
    ``18.194872`` names the file ``18.19``."""
    try:
        value = round(float(str(text).strip()), 2)
    except ValueError:
        return str(text).strip()
    return _number_text(str(value)) if math.isfinite(value) else str(text).strip()


@dataclass(frozen=True)
class GearSpec:
    """Every setting of one gear, as typed."""

    kind: str = KIND_SPUR
    recipe: str = ""              # "" = findings.DEFAULT_RECIPE
    module: str = "1.5"
    teeth: str = "25"
    pressure_angle: str = "20"
    face_width: str = "10"
    bore: str = "10"              # "" = no bore feature
    backlash: str = ""            # "" = the 0.3 × Module equation; typed = a literal
    fillet: str = ""              # "" = the 0.38 × Module equation; typed = a literal
    profile_shift: str = "0"      # x, × module; external spur and helical gears only
    helix_angle: str = ""         # degrees; helical kinds only
    hand: str = HAND_RIGHT        # helical kinds only; a herringbone's names its half nearest the Front plane
    groove: str = ""              # herringbone only: the centre groove's width in mm; "" = none
    teeth_side: str = TEETH_EXTERNAL  # "internal" = a ring, teeth pointing in; spur and helical kinds
    rim: str = ""                 # a ring's outside diameter; "" = root + 6 × module
    shaft_angle: str = "90"       # bevel only: degrees between the two shafts
    mate_teeth: str = ""          # bevel only: the other gear's teeth, which set the pitch cone
    name: str = ""                # "" = default_stem()
    # W9b (ISSUE-1-PLAN §2.4, K10; W9B-INTERFACES §2): a workbook sleeve's two toothed bands, mm; "" both = teeth over
    # the whole face. Never on the strip's form.
    start_band: str = ""
    end_band: str = ""
    # F1 (PLAN-PRINTED §1.1): "printed" or "machined"; blank or anything else is not printed. The dataclass default is
    # machined, what a spec written before F1 or built in code means; the form and a workbook's Box write the word.
    process: str = PROCESS_MACHINED
    nozzle: str = ""              # mm, the printer's line width; "" = NOZZLE_DEFAULT. Read by checks only.
    # F3 (PLAN-PRINTED §4.1, §4.2): the bore as cut. "" allowance = as built for a part on record (built_allowance),
    # else BORE_ALLOWANCE_DEFAULT printed and 0 machined; typed = that figure, negative allowed (a press fit).
    bore_allowance: str = ""
    drive: str = DRIVE_ROUND      # "round" or "flat"; blank is round
    flat: str = ""                # mm, the shaft across its flat, read with Drive flat
    # F3 (§4.1.1): the allowance the part on record holds, set only by as_built ("" = not on record). Never written by
    # to_dict, never read by from_dict; bore_allowance_mm reads it after a typed figure and before the default.
    built_allowance: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Every field, but the bands left out while both are blank, and the process and nozzle left out of a spec
        that is not printed (F1, PLAN-PRINTED §1.1): an unbanded machined part's record is byte for byte W9's.
        Never raises, whatever the process says; a machined spec's typed nozzle is not kept (nothing reads it)."""
        values = asdict(self)
        if not str(self.start_band).strip() and not str(self.end_band).strip():
            for key in BAND_FIELDS:
                values.pop(key, None)
        if not self.is_printed():
            for key in PROCESS_FIELDS:
                values.pop(key, None)
        # F3 (§4.3): the bore's three keys left out at their defaults, a record's built allowance always (§4.1.1).
        if not str(self.bore_allowance).strip():
            values.pop("bore_allowance", None)
        if str(self.drive).strip().lower() in ("", DRIVE_ROUND):
            values.pop("drive", None)
        if not str(self.flat).strip():
            values.pop("flat", None)
        for key in RECORD_ONLY_FIELDS:
            values.pop(key, None)
        return values

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "GearSpec":
        """The spec a record's ``spec`` holds. Unknown keys are dropped, and so is ``built_allowance`` should a record
        hold one: only :func:`as_built` sets it, from the part's globals (§4.1.1)."""
        known = {f.name for f in fields(cls)} - set(RECORD_ONLY_FIELDS)
        return cls(**{k: str(v) for k, v in (raw or {}).items() if k in known})

    # -- reading the fields ------------------------------------------------

    def module_mm(self) -> float:
        return parse_float(self.module, "Module")

    def teeth_count(self) -> int:
        return parse_whole(self.teeth, "No. of teeth")

    def pressure_angle_deg(self) -> float:
        return parse_float(self.pressure_angle, "Pressure angle")

    def face_width_mm(self) -> float:
        return parse_float(self.face_width, "Face width")

    def has_bore(self) -> bool:
        text = self.bore.strip()
        return bool(text) and parse_float(text, "Bore") != 0.0

    def bore_mm(self) -> float:
        """Zero when blank: no bore feature is made, and the global reads 0."""
        text = self.bore.strip()
        return parse_float(text, "Bore") if text else 0.0

    def backlash_mm(self) -> Optional[float]:
        """None when blank, which means the ``0.3 × Module`` equation."""
        text = self.backlash.strip()
        return parse_float(text, "Backlash") if text else None

    def fillet_mm(self) -> Optional[float]:
        """None when blank, which means the ``0.38 × Module`` equation."""
        text = self.fillet.strip()
        return parse_float(text, "Fillet") if text else None

    def profile_shift_value(self) -> float:
        text = self.profile_shift.strip()
        return parse_float(text, "Profile shift") if text else 0.0

    def is_helical(self) -> bool:
        return self.kind in HELICAL_KINDS

    def helix_angle_deg(self) -> float:
        return parse_float(self.helix_angle, "Helix angle")

    def hand_value(self) -> str:
        hand = str(self.hand).strip().lower()
        if hand not in HANDS:
            raise InputError(f"Hand must be {' or '.join(HANDS)} (got {self.hand.strip()!r}).")
        return hand

    def teeth_side_value(self) -> str:
        side = str(self.teeth_side).strip().lower() or TEETH_EXTERNAL
        if side not in TEETH_SIDES:
            raise InputError(f"Teeth must be {' or '.join(TEETH_SIDES)} (got {self.teeth_side.strip()!r}).")
        return side

    def groove_mm(self) -> Optional[float]:
        """None when blank or zero: no centre groove."""
        text = self.groove.strip()
        if not text:
            return None
        value = parse_float(text, "Groove")
        return value or None

    def is_internal(self) -> bool:
        return str(self.teeth_side).strip().lower() == TEETH_INTERNAL

    def process_value(self) -> str:
        """``printed`` or ``machined``, in any case; a blank is machined (a spec that does not say). Raises InputError on
        any other word, as :meth:`teeth_side_value` does."""
        process = str(self.process).strip().lower() or PROCESS_MACHINED
        if process not in PROCESSES:
            raise InputError(f"Process must be {' or '.join(PROCESSES)} (got {str(self.process).strip()!r}).")
        return process

    def is_printed(self) -> bool:
        """Whether the gear is made printed: ``printed`` in any case. Never raises; anything else is not printed."""
        return str(self.process).strip().lower() == PROCESS_PRINTED

    def nozzle_mm(self) -> float:
        """The printer's line width, mm: :data:`NOZZLE_DEFAULT` when blank. Raises InputError naming Nozzle on a value
        that does not read or is not more than zero."""
        text = str(self.nozzle).strip()
        if not text:
            return NOZZLE_DEFAULT
        value = parse_float(text, "Nozzle")
        if value <= 0:
            raise InputError(f"Nozzle must be more than zero (got {text!r}).")
        return value

    def bore_allowance_mm(self) -> float:
        """The allowance the hole is cut with, mm on the diameter (F3, §4.1.1), in this order: a typed figure (any sign,
        0 included); else the part's as built (:attr:`built_allowance`, set by :func:`as_built` for a part on record);
        else :data:`BORE_ALLOWANCE_DEFAULT` for a printed gear; else 0. Raises InputError naming Bore allowance on a
        figure that does not read. Whether the gear has a bore is not asked here: see :meth:`bore_as_cut_mm`."""
        text = str(self.bore_allowance).strip()
        if text:
            return parse_float(text, "Bore allowance")
        built = str(self.built_allowance).strip()
        if built:
            return parse_float(built, "Bore allowance")
        return BORE_ALLOWANCE_DEFAULT if self.is_printed() else 0.0

    def bore_as_cut_mm(self) -> float:
        """The hole's diameter as cut, mm: Bore plus :meth:`bore_allowance_mm`, or 0 with no bore."""
        return self.bore_mm() + self.bore_allowance_mm() if self.has_bore() else 0.0

    def drive_value(self) -> str:
        """``round`` or ``flat``, in any case; a blank is round. Raises InputError on any other word."""
        drive = str(self.drive).strip().lower() or DRIVE_ROUND
        if drive not in DRIVES:
            raise InputError(f"Drive must be {' or '.join(DRIVES)} (got {str(self.drive).strip()!r}).")
        return drive

    def has_flat(self) -> bool:
        """Whether the bore is a D (Drive flat, in any case). Never raises; anything else is round."""
        return str(self.drive).strip().lower() == DRIVE_FLAT

    def flat_mm(self) -> Optional[float]:
        """The shaft's size across its flat, mm, or None when blank. Raises InputError naming Flat on text that does
        not read. Read with Drive flat; the gears' checks say a flat with no Flat, or one out of bounds."""
        text = str(self.flat).strip()
        return parse_float(text, "Flat") if text else None

    def has_bands(self) -> bool:
        """Whether either band is typed (W9b): the part is then a banded sleeve's, with a relief between."""
        return bool(str(self.start_band).strip() or str(self.end_band).strip())

    def bands_mm(self) -> Optional[Tuple[float, float]]:
        """``(start band, end band)`` in mm, or None when both are blank. A band that does not read is an
        InputError naming it; one blank beside a typed one reads as 0 (the kind's check says it)."""
        if not self.has_bands():
            return None
        start = str(self.start_band).strip()
        end = str(self.end_band).strip()
        return (parse_float(start, "Start band") if start else 0.0, parse_float(end, "End band") if end else 0.0)

    def rim_mm(self) -> Optional[float]:
        """None when blank, which means the root diameter plus six modules."""
        text = self.rim.strip()
        return parse_float(text, "Rim") if text else None

    def shaft_angle_deg(self) -> float:
        return parse_float(self.shaft_angle, "Shaft angle")

    def mate_teeth_count(self) -> int:
        return parse_whole(self.mate_teeth, "Mate teeth")

    def recipe_or(self, default: str) -> str:
        recipe = self.recipe.strip() or default
        if recipe not in RECIPES:
            raise InputError(f"Recipe must be {' or '.join(RECIPES)} (got {recipe!r}).")
        return recipe

    def default_stem(self) -> str:
        return default_stem(self)

    def stem(self) -> str:
        return sanitize_stem(self.name) if self.name.strip() else self.default_stem()

    def with_values(self, **changes: str) -> "GearSpec":
        """The spec with ``changes``, through :meth:`to_dict`; a built allowance set by :func:`as_built` is kept unless
        changed, since it says what the part on record holds, not what the form says."""
        values = self.to_dict()
        values.update(built_allowance=self.built_allowance)
        values.update(changes)
        return GearSpec(**values)


def as_built(spec: GearSpec, variables: Optional[Sequence[Sequence[str]]]) -> GearSpec:
    """F3's one rule, and its one home (PLAN-PRINTED §4.1.1): a blank Bore allowance on a part on record is the figure
    the part holds, so a default that moves later (V1) rebuilds nothing already built, as D11's (B) does for Process.

    ``variables`` are the part's globals as its record holds them (``[name, expression]``, a ``GearRecord``'s or a
    ``PartEntry``'s ``variables``), or None for a spec with no part on record. The spec comes back with
    :attr:`GearSpec.built_allowance` set:

    - to the literal of ``"Bore Allowance"`` in ``variables``, spaces aside, when they are given and the spec's Bore
      allowance is blank;
    - to ``"0"`` when they are given, the allowance is blank and the part holds no such global, as no part built before
      F3 does. An empty ``variables`` reads the same way: a part on record whose record lists no globals (a v1 record,
      or the build journal's entries, which ``gearbox.journal`` writes with none) reads as built with no allowance;
    - to ``""`` otherwise: no part on record (None), or a typed allowance, which means what it says.

    Nothing else changes, and ``to_dict`` never writes the field, so a record written from the result holds the spec
    it held. :meth:`GearSpec.bore_allowance_mm` reads the field after a typed figure and before the default, so every
    derive and plan of the result sees the hole as built. Pure; never raises (a recorded text that is not a number
    raises only when bore_allowance_mm reads it, naming Bore allowance)."""
    if variables is None or str(spec.bore_allowance).strip():
        return replace(spec, built_allowance="") if spec.built_allowance else spec
    held = "0"
    for pair in variables:
        if len(pair) >= 2 and str(pair[0]).strip() == BORE_ALLOWANCE_GLOBAL:
            held = "".join(str(pair[1]).split()) or "0"
            break
    return replace(spec, built_allowance=held)


CLUTCH_WORDS = {"sleeve": "Sleeve", "dog": "Dog", "hub": "Hub"}   # a workbook sleeve's, dog's and hub's stem word


def default_stem(spec: GearSpec, prefix: str = "") -> str:
    """``Gear_m1.5_N25``; ``Helical_m2_N20_15R`` and ``Herringbone_m2_N20_30L`` for the helical kinds.

    A pair's ``Pinion`` and ``Gear`` prefixes keep the helix suffix, since two
    gears differing only in hand would otherwise share a name, and a
    herringbone's is marked ``HB`` (``Pinion_m2.5_N15_HB20.36R``): the solver can
    give a helical and a herringbone pair the same module, teeth and angle.

    A ring is ``Ring_m2_N60`` whatever else it is, so its helix suffix carries
    the ``HB`` mark too; a bevel gear names its mate, ``Bevel_m3_N20_M40``, and
    its shaft angle when that is not 90°, ``Bevel_m3_N20_M40_S80``. A grooved
    herringbone ends with its groove, ``Herringbone_m2_N20_30R_G8``. A shifted
    gear ends with its shift, ``Gear_m2_N15_x0.09`` (``_x-0.09`` negative), since
    it is a different part from the unshifted gear of the same module and teeth.
    A printed gear ends ``_P`` after everything else (F1, D10): ``Gear_m1.5_N25_P``,
    ``Pinion_m2_N15_x0.09_P``. A machined gear's name is as it was.
    """
    words = {KIND_HELICAL: "Helical", KIND_HERRINGBONE: "Herringbone", KIND_BEVEL: "Bevel"}
    internal = spec.is_internal() and spec.kind != KIND_BEVEL
    lead = "Ring" if internal and prefix != "Pinion" else (prefix or words.get(spec.kind, "Gear"))
    lead = CLUTCH_WORDS.get(spec.kind, lead)          # W8: Sleeve_m1.5_N30, Dog_m1.5_N30 (W8-PLAN §1.1)
    stem = f"{lead}_m{_number_text(spec.module)}_N{_number_text(spec.teeth)}"
    if spec.kind in HELICAL_KINDS:
        hand = str(spec.hand).strip().lower()[:1].upper()
        mark = "HB" if (prefix or internal) and spec.kind == KIND_HERRINGBONE else ""
        stem += f"_{mark}{_angle_text(spec.helix_angle) if spec.helix_angle.strip() else 'H'}{hand}"
        if spec.kind == KIND_HERRINGBONE and _shifted(spec.groove):
            stem += f"_G{_number_text(spec.groove)}"
    elif spec.kind == KIND_BEVEL:
        stem += f"_M{_number_text(spec.mate_teeth) if spec.mate_teeth.strip() else 'x'}"
        if spec.shaft_angle.strip() and _number_text(spec.shaft_angle) != "90":
            stem += f"_S{_angle_text(spec.shaft_angle)}"
    if spec.kind != KIND_BEVEL and _shifted(spec.profile_shift):
        stem += f"_x{_shift_name(spec.profile_shift)}"
    if spec.is_printed():
        stem += PRINTED_STEM_MARK         # F1, D10: a different part from the machined gear of the same sizes
    return sanitize_stem(stem)


def _shift_name(text: str) -> str:
    """A shift as it goes into a file name: three decimals at most, so a solved
    ``0.050501234`` names the file ``0.051``."""
    try:
        value = round(float(str(text).strip() or "0"), 3)
    except ValueError:
        return str(text).strip()
    return _number_text(str(value)) if math.isfinite(value) else str(text).strip()


def _shifted(text: str) -> bool:
    """A shift that is typed and not zero; one that does not read is left to the form to refuse."""
    try:
        return float(str(text).strip() or "0") != 0.0
    except ValueError:
        return False


@dataclass(frozen=True)
class PairSpec:
    """A gear pair: the solver's inputs and the two gears it fills in."""

    mode: str = MODE_SINGLE
    centre_distance: str = ""
    ratio: str = ""
    module: str = ""              # "" = any module the series allows
    series: str = "1"
    min_teeth: str = "17"
    max_teeth: str = "200"
    helix_angle: str = ""         # "" = solved within helix_min..helix_max
    helix_min: str = ""           # "" = the kind's default range
    helix_max: str = ""
    mesh: str = MESH_EXTERNAL     # "internal" = gear B is a ring round gear A
    shafts: str = SHAFTS_PARALLEL  # "crossed" = helical gears on shafts at an angle
    shaft_angle: str = "90"       # crossed and bevel pairs, degrees
    hands: str = HANDS_SAME       # crossed pairs: "opposite" makes the shaft angle |β1 − β2|
    cone_distance: str = ""       # bevel pairs: what Solve aims for instead of a centre distance
    motion: str = MOTION_FIXED    # "gear mate": gear 1 turns and a gear mate turns gear 2 with it
    gear_a: GearSpec = field(default_factory=GearSpec)
    gear_b: GearSpec = field(default_factory=GearSpec)
    assembly_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["gear_a"] = self.gear_a.to_dict()
        data["gear_b"] = self.gear_b.to_dict()
        return data

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "PairSpec":
        known = {f.name for f in fields(cls)}
        values: Dict[str, Any] = {}
        for key, value in (raw or {}).items():
            if key not in known:
                continue
            if key in ("gear_a", "gear_b"):
                values[key] = GearSpec.from_dict(value if isinstance(value, dict) else {})
            else:
                values[key] = str(value)
        return cls(**values)

    def centre_distance_mm(self) -> float:
        value = parse_float(self.centre_distance, "Centre distance")
        if value <= 0:
            raise InputError(f"Centre distance must be more than zero (got {self.centre_distance.strip()!r}).")
        return value

    def ratio_value(self) -> float:
        return parse_ratio(self.ratio)

    def module_mm(self) -> Optional[float]:
        text = self.module.strip()
        if not text:
            return None
        value = parse_float(text, "Module")
        if value <= 0:
            raise InputError(f"Module must be more than zero (got {text!r}).")
        return value

    def min_teeth_count(self) -> int:
        return parse_whole(self.min_teeth, "Min teeth")

    def max_teeth_count(self) -> int:
        return parse_whole(self.max_teeth, "Max teeth")

    def helix_angle_deg(self) -> Optional[float]:
        """None when blank: the solver finds the angle."""
        text = self.helix_angle.strip()
        return parse_float(text, "Helix angle") if text else None

    def mesh_value(self) -> str:
        mesh = str(self.mesh).strip().lower() or MESH_EXTERNAL
        if mesh not in MESHES:
            raise InputError(f"Mesh must be {' or '.join(MESHES)} (got {self.mesh.strip()!r}).")
        return mesh

    def shafts_value(self) -> str:
        shafts = str(self.shafts).strip().lower() or SHAFTS_PARALLEL
        if shafts not in SHAFTS:
            raise InputError(f"Shafts must be {' or '.join(SHAFTS)} (got {self.shafts.strip()!r}).")
        return shafts

    def shaft_angle_deg(self) -> float:
        return parse_float(self.shaft_angle, "Shaft angle")

    def hands_value(self) -> str:
        hands = str(self.hands).strip().lower() or HANDS_SAME
        if hands not in HAND_PAIRINGS:
            raise InputError(f"Hands must be {' or '.join(HAND_PAIRINGS)} (got {self.hands.strip()!r}).")
        return hands

    def motion_value(self) -> str:
        motion = str(self.motion).strip().lower() or MOTION_FIXED
        if motion not in MOTIONS:
            raise InputError(f"Assembly must be {' or '.join(MOTIONS)} (got {self.motion.strip()!r}).")
        return motion

    def cone_distance_mm(self) -> float:
        value = parse_float(self.cone_distance, "Cone distance")
        if value <= 0:
            raise InputError(f"Cone distance must be more than zero (got {self.cone_distance.strip()!r}).")
        return value

    def helix_range(self, default: Tuple[float, float]) -> Tuple[float, float]:
        low = parse_float(self.helix_min, "Helix min") if self.helix_min.strip() else default[0]
        high = parse_float(self.helix_max, "Helix max") if self.helix_max.strip() else default[1]
        if not 0.0 < low <= high < 90.0:
            raise InputError(f"The helix range must run upward from above 0° to below 90° (got {low:g} to {high:g}).")
        return low, high


def pair_stems(pair: PairSpec) -> Tuple[str, str, str]:
    """``(Pinion_m1.5_N20, Gear_m1.5_N60, Pair_m1.5_20T_60T)``, typed names first.

    The smaller gear is the pinion. On a tie the first is called the pinion,
    so the two files never share a name. A ring is always ``Ring_``, with its
    pinion ``Pinion_``, and the pair ends ``_INT``; a crossed pair ends with its
    shaft angle, ``_X90`` (``_XO30`` of opposite hands), and a bevel pair ``_B90``. A shifted pair ends with
    both shifts, ``_x0.09_-0.09``. A printed pair ends ``_P`` after all of it, as its parts do (F1, D10; the
    coordinator's ruling of 2026-11-18): ``Pair_m1.5_20T_60T_P``. A machined pair's name is as it was, and a typed
    assembly name is kept as typed.
    """
    a, b = pair.gear_a, pair.gear_b
    internal = b.is_internal() and b.kind != KIND_BEVEL
    try:
        a_smaller = internal or a.teeth_count() <= b.teeth_count()
    except InputError:
        a_smaller = True
    stem_a = sanitize_stem(a.name) if a.name.strip() else default_stem(a, "Pinion" if a_smaller else "Gear")
    stem_b = sanitize_stem(b.name) if b.name.strip() else default_stem(b, "Gear" if a_smaller else "Pinion")
    if pair.assembly_name.strip():
        stem_pair = sanitize_stem(pair.assembly_name)
    else:
        crossed = a.kind in HELICAL_KINDS and str(pair.shafts).strip().lower() == SHAFTS_CROSSED
        if a.kind == KIND_BEVEL:
            suffix = f"_B{_angle_text(pair.shaft_angle) if pair.shaft_angle.strip() else 'x'}"
        elif crossed:
            # Of opposite hands the same module, teeth and shaft angle is another pair: _XO30.
            opposite = "O" if str(pair.hands).strip().lower() == HANDS_OPPOSITE else ""
            suffix = f"_X{opposite}{_angle_text(pair.shaft_angle) if pair.shaft_angle.strip() else 'x'}"
        else:
            mark = "HB" if a.kind == KIND_HERRINGBONE else "H"
            suffix = ("_INT" if internal else "") + (
                f"_{mark}{_angle_text(a.helix_angle)}" if a.kind in HELICAL_KINDS and a.helix_angle.strip() else "")
            if _shifted(a.profile_shift) or _shifted(b.profile_shift):
                suffix += f"_x{_shift_name(a.profile_shift)}_{_shift_name(b.profile_shift)}"
        if a.is_printed() or b.is_printed():
            suffix += PRINTED_STEM_MARK
        stem_pair = sanitize_stem(
            f"Pair_m{_number_text(a.module)}_{_number_text(a.teeth)}T_{_number_text(b.teeth)}T{suffix}"
        )
    return stem_a, stem_b, stem_pair
