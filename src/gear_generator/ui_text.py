"""The words the window puts on screen, worked out without a window.

Every panel header's readout, every derived row, candidate row and status line
is derived text: one short line standing for the state of something. Working
them out here keeps them testable on a machine with no display, and keeps
:mod:`gui` to laying out widgets and wiring handlers.

Nothing here touches tkinter, and nothing here holds state.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

from .gears import pair as pairs, standards
from .gears.base import Diagnostic
from .gears.equations import literal
from .spec import MODE_PAIR, RECIPE_ARCS, RECIPE_INVOLUTE, GearSpec, InputError, PairSpec, pair_stems

RECIPE_WORDS = {RECIPE_INVOLUTE: "involute curve", RECIPE_ARCS: "arc flanks"}
RECIPE_LABELS = {RECIPE_INVOLUTE: "Involute", RECIPE_ARCS: "Arcs"}
KIND_LABELS = {"spur": "Spur", "helical": "Helical", "herringbone": "Herringbone", "bevel": "Bevel",
               "internal": "Internal"}
TEETH_SIDE_LABELS = {"external": "External", "internal": "Internal"}
MESH_LABELS = TEETH_SIDE_LABELS
SHAFTS_LABELS = {"parallel": "Parallel", "crossed": "Crossed"}
MOTION_LABELS = {"fixed": "Fixed", "gear mate": "Gear mate"}
HANDS_PAIRING_LABELS = {"same": "Same", "opposite": "Opposite"}
HAND_LABELS = {"right": "Right", "left": "Left"}
# Five kinds share one segmented row, and "Herringbone" does not fit its share;
# the Gear panel's readout still says the whole word.
KIND_BUTTON_LABELS = {**KIND_LABELS, "herringbone": "Double"}
SERIES_LABELS = {standards.SERIES_1: "Series 1", standards.SERIES_1_2: "1 + 2", standards.SERIES_ALL: "+ fine"}

# What a readout says when the gear it stands for does not work out yet.
CHECK_THE_FIELDS = "check the fields"


def _n(value: float, places: int = 3) -> str:
    return literal(round(float(value), places))


# ------------------------------------------------------------- the readouts


def kind_readout(kind: str, recipe: str) -> str:
    """``Spur · involute curve``."""
    return f"{KIND_LABELS.get(kind, kind.title())} · {RECIPE_WORDS.get(recipe, recipe)}"


def gear_readout(spec: GearSpec) -> str:
    """``m1.5 · z25 · 20° · PD 37.5 mm``, or what is stopping it.

    A helical gear adds its helix, ``β15° R``, and its pitch diameter is the
    transverse one, ``m z / cos β``. A shifted gear adds ``x+0.25``. A ring ends
    ``· ring``; a bevel gear names its mate and shaft angle, ``z20:40 · Σ90°``.
    """
    try:
        m = spec.module_mm()
        n = spec.teeth_count()
        alpha = spec.pressure_angle_deg()
        if spec.kind == "bevel":
            return (f"m{_n(m)} · z{n}:{spec.mate_teeth_count()} · {_n(alpha, 2)}° · "
                    f"Σ{_n(spec.shaft_angle_deg(), 2)}° · PD {_n(m * n)} mm")
        shift = spec.profile_shift_value()
        if spec.is_helical():
            beta = spec.helix_angle_deg()
            hand = spec.hand_value()
            if not 0.0 < beta < 90.0:
                return CHECK_THE_FIELDS
    except InputError:
        return CHECK_THE_FIELDS
    ring = " · ring" if spec.is_internal() else ""
    shifted = f"x{shift_text(shift)} · " if shift else ""
    if spec.is_helical():
        return (f"m{_n(m)} · z{n} · {_n(alpha, 2)}° · β{_n(beta, 2)}° {hand[0].upper()} · {shifted}"
                f"PD {_n(m * n / math.cos(math.radians(beta)))} mm{ring}")
    return f"m{_n(m)} · z{n} · {_n(alpha, 2)}° · {shifted}PD {_n(m * n)} mm{ring}"


def is_bevel(g) -> bool:
    """A :class:`bevel.BevelDerived` — which passes every other name through to its back-cone section."""
    return type(g).__name__ == "BevelDerived"


def is_ring(g) -> bool:
    return type(g).__name__ == "InternalDerived"


def derived_line(g) -> str:
    """``PD 37.5 · OD 40.5 · RD 33.75 · base 35.238 · p 4.712``.

    A bevel gear: ``δ 26.565° · R 67.082 · OD 67.218 · X 58.195``; a ring
    ``PD 120 · tip 116 · root 125 · rim 137``.
    """
    if is_bevel(g):
        form = " · crown" if g.crown else (" · internal" if g.ring else "")
        return (f"δ {_n(g.delta, 3)}° · R {_n(g.cone_distance)} · OD {_n(g.da)} · X {_n(g.crown_to_apex)}{form}")
    if is_ring(g):
        return f"PD {_n(g.d)} · tip {_n(g.da)} · root {_n(g.df)} · rim {_n(g.rim)}"
    return (
        f"PD {_n(g.d)} · OD {_n(g.da)} · RD {_n(g.df)} · base {_n(g.db)} · p {_n(g.p)}"
    )


def derived_rows(g) -> List[Tuple[str, str]]:
    """The Derived panel's label/value rows. Every value is in mm, said once above them.

    Short on purpose: in pair mode two columns of these share the width the
    preview leaves.
    """
    if is_bevel(g):
        return [
            ("Pitch cone δ", f"{_n(g.delta, 3)}°"),
            ("Cone distance", _n(g.cone_distance)),
            ("Pitch diameter", _n(g.d)),
            ("Tip diameter" if g.ring else "Outer diameter", _n(g.da)),
            ("Apex to crown", _n(g.crown_to_apex)),
            ("Addendum", _n(g.addendum)),
            ("Dedendum", _n(g.dedendum)),
            ("Face angle", f"{_n(g.face_angle, 3)}°"),
            ("Root angle", f"{_n(g.root_angle, 3)}°"),
            ("Virtual teeth", "∞ · a rack" if g.crown else _n(g.virtual_teeth, 2) + (" · a ring" if g.ring else "")),
            ("Toe scale", _n(g.toe_scale, 4)),
            ("Tooth at pitch", _n(g.section.s)),
            ("Backlash", _n(g.section.backlash) + ("" if g.section.backlash_typed else " · 0.3m")),
        ]
    ring = []
    if is_ring(g):
        ring = [
            ("Rim diameter", _n(g.rim) + ("" if g.rim_typed else " · root + 6m")),
        ]
    helix = []
    if hasattr(g, "helix_angle_deg"):
        helix = [
            ("Helix", f"{_n(g.helix_angle_deg, 4)}° · {HAND_LABELS.get(g.hand, g.hand).lower()}"),
            ("Transverse m", _n(g.transverse_module, 4)),
            ("Transverse α", f"{_n(g.pressure_angle_deg, 3)}°"),
            ("Lead", _n(g.lead, 2)),
            ("Twist on face", f"{_n(g.face_twist_deg, 2)}°"),
            ("Overlap εβ", _n(g.overlap, 3)),
        ]
        if getattr(g, "groove", 0.0):
            helix.append(("Centre groove", f"{_n(g.groove)} · floor {_n(g.groove_d)}"))
    if is_ring(g):
        fillet_note = " · 0.15m"
        tip_label = "Inner tip"
    else:
        fillet_note = " · 0.38m"
        tip_label = "Outer diameter"
    shift = getattr(g, "shift", 0.0)
    if shift:
        # The coefficient, and how far that moves the tip and the root, in mm.
        ring = ring + [("Profile shift", f"{shift_text(shift)} · {_n(shift * g.module)}")]
    return helix + ring + [
        ("Pitch diameter", _n(g.d)),
        (tip_label, _n(g.da)),
        ("Root diameter", _n(g.df)),
        ("Base diameter", _n(g.db)),
        ("Tooth depth", _n(g.h)),
        ("Circular pitch", _n(g.p)),
        ("Space at pitch", _n(g.space)),
        ("Tooth at pitch", _n(g.s)),
        ("Tip thickness", _n(g.tip_thickness)),
        ("Backlash", _n(g.backlash) + ("" if g.backlash_typed else " · 0.3m")),
        ("Fillet", _n(g.fillet) + ("" if g.fillet_typed else fillet_note)),
    ]


def warning_lines(diagnostics: Sequence[Diagnostic]) -> List[str]:
    """Errors first, then warnings, each once."""
    ordered = [d for d in diagnostics if d.is_error] + [d for d in diagnostics if not d.is_error]
    return list(dict.fromkeys(d.message for d in ordered))


def pair_readout(centre: str, ratio: str, chosen: Optional["pairs.Candidate"] = None, symbol: str = "C") -> str:
    """``C 60 mm · i 3`` and, once one is chosen, ``· m1.5 20:60``; a bevel pair's ``R 50 mm``."""
    parts = []
    if centre.strip():
        parts.append(f"{symbol} {centre.strip()} mm")
    if ratio.strip():
        parts.append(f"i {ratio.strip()}")
    if chosen is not None:
        parts.append(f"m{_n(chosen.module, 4)} {chosen.teeth_driver}:{chosen.teeth_driven}")
    return " · ".join(parts) or "centre distance and ratio"


def pair_derived_readout(centre: float, ratio: float, epsilon: float, symbol: str = "C") -> str:
    """``C 60 mm · i 3 · contact ratio 1.671`` — the Derived panel's readout in pair mode.

    The three numbers are the pair's own, from :func:`pairs.describe`: the
    centre distance the teeth make, the ratio they turn at, and how many teeth
    are in contact on average. The per-gear sizes are in the table below it.
    """
    return f"{symbol} {_n(centre)} mm · i {_n(ratio)} · contact ratio {contact_ratio_text(epsilon)}"


def pair_derived_rows(centre: float, ratio: float, epsilon: float,
                      teeth_driver: int, teeth_driven: int, label: str = "Centre distance",
                      working_angle: Optional[float] = None) -> List[Tuple[str, str]]:
    """The three rows above the per-gear columns in Derived; a bevel pair's first is its cone distance.

    A shifted pair adds a fourth, the pressure angle it actually meshes at.
    """
    rows = [
        (label, f"{_n(centre)} mm"),
        ("Ratio", f"{_n(ratio)} · {teeth_driver} : {teeth_driven}"),
        ("Contact ratio", contact_ratio_text(epsilon)),
    ]
    if working_angle is not None:
        rows.append(("Working α", f"{_n(working_angle, 3)}°"))
    return rows


def candidate_row(candidate: "pairs.Candidate") -> Tuple[str, str, str, str]:
    """``(MODULE, TEETH, ERROR, tag)`` for one row of the candidate list.

    The tag is ``exact`` or ``near``, which is what the row is coloured by.
    """
    module = _n(candidate.module, 4) + ("" if candidate.standard else " *")
    teeth = f"{candidate.teeth_driver} : {candidate.teeth_driven}"
    errors = []
    symbol = "R" if candidate.cone else "C"
    if abs(candidate.centre_error) > pairs.TOLERANCE:
        errors.append(f"{symbol} {'+' if candidate.centre_error > 0 else '−'}{_n(abs(candidate.centre_error))} mm")
    if candidate.ratio_error > pairs.TOLERANCE:
        errors.append(f"i {_n(candidate.ratio_error * 100, 2)} %")
    if candidate.undercut:
        errors.append("undercut")
    if candidate.clashes:
        errors.append(f"clash {_n(candidate.clash, 2)} mm")
    text = " · ".join(errors) if errors else "exact"
    if candidate.shifted:
        text = f"x {shift_text(candidate.shift_1)}/{shift_text(candidate.shift_2)} · {text}"
    if candidate.cone:
        forms = pairs.bevel_forms(candidate.teeth_driver, candidate.teeth_driven, candidate.shaft_angle)
        named = [f"{side} {form}" for side, form in zip("AB", forms) if form != pairs.bevel.FORM_CONE]
        if named:
            text = f"{', '.join(named)} · {text}"
    if candidate.crossed:
        text = f"β{_n(candidate.helix_angle, 2)}°/{_n(candidate.helix_angle_b, 2)}° · {text}"
    elif candidate.helix_angle:
        text = f"β{_n(candidate.helix_angle, 2)}° · {text}"
    return module, teeth, text, "exact" if candidate.exact else "near"


def _exact_counts(candidates: Sequence["pairs.Candidate"]) -> Tuple[int, int]:
    """Clean rows — exact, standard, not undercut — without profile shift, and with it."""
    clean = [c for c in candidates if c.exact and c.standard and not c.undercut]
    shifted = sum(1 for c in clean if c.shifted)
    return len(clean) - shifted, shifted


def shift_text(shift: float) -> str:
    """``+0.25``, ``−0.1``, ``0``: a profile shift coefficient with its sign, always."""
    if not shift:
        return "0"
    return ("+" if shift > 0 else "−") + _n(abs(shift), 4)


def solve_summary(candidates: Sequence["pairs.Candidate"],
                  chosen: Optional["pairs.Candidate"] = None) -> str:
    """``64 candidates · 3 exact``, and the chosen row once there is one.

    ``64 candidates · 3 exact · m1.5 20 : 60 chosen``. The Pair panel and the
    flyout show the same line, so the strip still says what was picked with the
    candidates hidden.
    """
    if not candidates:
        return "No pair of whole tooth counts fits; widen the series or Min teeth."
    exact, shifted = _exact_counts(candidates)
    noun = "candidate" if len(candidates) == 1 else "candidates"
    text = f"{len(candidates)} {noun} · {exact} exact"
    if shifted:
        text += f" · {shifted} with shift"
    if chosen is not None:
        text += f" · m{_n(chosen.module, 4)} {chosen.teeth_driver} : {chosen.teeth_driven} chosen"
    return text


def output_readout(folder: str, limit: int = 38) -> str:
    """The folder, shortened from the left so its last parts stay readable."""
    text = folder.strip()
    if not text:
        return "choose a folder"
    if len(text) <= limit:
        return text
    return "…" + text[-(limit - 1):]


def link_headline(available: bool, snapshot: Optional[dict]) -> Tuple[str, str]:
    """The SolidWorks bar's readout, and which colour its dot takes.

    Unlike Airfoil Converter this app makes its own documents, so no document
    open is a perfectly good state to build from: it is ``ok``.
    """
    if not available:
        return "pywin32 not installed", "off"
    if snapshot is None:
        return "not reachable", "bad"
    label = snapshot.get("version") or "SolidWorks"
    if snapshot.get("newer_than_tested"):
        label += " (newer than tested)"
    title = snapshot.get("title")
    if not title:
        return f"{label} — no document open", "ok"
    return f"{label} — {title}", "ok"


def mode_note(mode: str, stems: Sequence[str], update_count: int = 0, document: str = "") -> str:
    """What the primary button is about to do, in a sentence."""
    if update_count and document:
        noun = "variable" if update_count == 1 else "variables"
        return f"Update values will change {update_count} {noun} in {document}."
    if mode == MODE_PAIR and len(stems) >= 3:
        return f"Build will make {stems[0]}.SLDPRT, {stems[1]}.SLDPRT and {stems[2]}.SLDASM."
    if stems:
        return f"Build will make {stems[0]}.SLDPRT."
    return "Build will make a new part."


def manual_steps_line(steps: Iterable[str]) -> str:
    """``1 thing to do by hand: …`` — counted, so it is not a surprise."""
    listed = list(dict.fromkeys(steps))
    if not listed:
        return ""
    noun = "thing" if len(listed) == 1 else "things"
    return f"{len(listed)} {noun} to do by hand: " + "; ".join(s.rstrip(".") for s in listed) + "."


# ------------------------------------------- what the number being typed means
#
# One card at the foot of the panel holding the caret. The name, the symbol and
# the sentences are fixed copy; the worked line is derived text like every
# readout, so it changes as the form does.

# The fields with a card, in the order they are on the form.
GEAR_EXPLAINERS = ("module", "teeth", "pressure_angle", "face_width", "bore", "backlash", "fillet", "profile_shift",
                   "helix_angle", "hand", "groove", "teeth_side", "rim", "shaft_angle", "mate_teeth", "name")
PAIR_EXPLAINERS = ("centre_distance", "cone_distance", "ratio", "pair_module", "series", "teeth_range", "mesh",
                   "shafts", "pair_shaft_angle", "hands", "motion", "assembly_name")
EXPLAINER_FIELDS = GEAR_EXPLAINERS + PAIR_EXPLAINERS

# (name, symbol, what it is). The symbol is what the diagram beside it marks.
_EXPLAINER_COPY: Dict[str, Tuple[str, str, str]] = {
    "module": ("Module", "m",
               "Tooth size, in mm: the pitch diameter divided by the number of teeth. A bigger module means "
               "bigger, stronger teeth and fewer of them for the same diameter. Two gears mesh only if their "
               "modules match."),
    "teeth": ("Teeth", "z",
              "How many teeth go round the gear. With the module it sets the size, PD = m × z, and the ratio "
              "between two gears is the ratio of their tooth counts. Fewer than 17 undercuts the root at 20°."),
    "pressure_angle": ("Pressure angle", "α",
                       "The slant of the flank: the angle between the line along which the teeth push on each "
                       "other and the tangent to the pitch circle. 20° is the standard; 14.5° runs quieter but "
                       "undercuts sooner, 25° is stronger but loads the bearings more. Meshing gears must "
                       "share it."),
    "face_width": ("Face width", "b",
                   "How thick the gear is along its axis: the depth it is extruded. Wider carries more load; "
                   "6 to 12 × module is usual for a spur gear."),
    "bore": ("Bore", "",
             "The hole through the centre for the shaft. Blank makes a solid disc. Leave a rim between the "
             "bore and the root circle: the form warns under one module, and two to three is usual."),
    "backlash": ("Backlash", "j",
                 "How much each tooth is thinned at the pitch circle so the pair does not bind: the space "
                 "grows by this and the tooth shrinks by it, on both gears, so the play in the mesh is twice "
                 "the number. Blank uses 0.3 × module, the default the equations carry; ISO asks 0.02–0.05 × m "
                 "for a precise pair."),
    "fillet": ("Fillet", "ρ",
               "The radius where each flank meets the root circle. It rounds off the sharp inside corner where "
               "a tooth would otherwise crack. Blank uses 0.38 × module."),
    "profile_shift": ("Profile shift", "x",
                      "How far the cutting rack is moved out from the gear, in modules. A positive shift makes the "
                      "tip and root circles bigger and the tooth thicker, which cures undercut on a small pinion; "
                      "the shifts of a pair together move its centre distance, which is how a standard module is "
                      "made to fit one. 0 is the standard tooth."),
    "helix_angle": ("Helix angle", "β",
                    "How far the teeth lean from the axis, measured on the pitch cylinder. Module and pressure "
                    "angle are then the normal ones, square to the teeth; round the gear the pitch is longer, "
                    "mt = m / cos β. Steeper runs smoother but pushes the gear harder along its shaft: 8–25° is "
                    "usual for a helical gear, 20–40° for a herringbone."),
    "hand": ("Hand", "",
             "Which way the teeth wind: a right-hand gear's lean like a right-hand screw thread. Helical gears on "
             "parallel shafts mesh only with opposite hands, and a pinion inside a ring with the same hand; in a "
             "pair gear B's hand follows gear A's. A herringbone's names its half nearest the Front plane."),
    "groove": ("Groove", "g",
               "A plain channel round the middle of a herringbone gear, between its two sets of teeth, where a "
               "hob or a grinding wheel runs out. Its floor is two modules inside the root circle. Blank leaves "
               "the two halves meeting at a point, as they do on a gear cut in one piece."),
    "teeth_side": ("Teeth", "",
                   "Which side of the rim the teeth are cut on. External teeth point outward, as on any gear; "
                   "internal teeth point inward from a ring, and a pinion runs inside it turning the same way. "
                   "A bevel gear's side is set by its cone, not here: outside a pitch cone under 90°, inside one "
                   "past it."),
    "rim": ("Rim", "",
            "A ring's outside diameter: the solid rim round the roots of its teeth. Blank leaves three modules "
            "of rim outside the root circle; under two modules the ring is thin."),
    "shaft_angle": ("Shaft angle", "Σ",
                    "The angle between the two shafts a bevel gear works across, 90° for a right-angle drive. "
                    "Each gear's pitch cone is its share of it, set by the two tooth counts; both gears of a pair "
                    "must be cut for the same angle. Past 90° the bigger gear's cone opens out: where it reaches "
                    "90° exactly it is a crown gear, its teeth on its face, and beyond that an internal bevel "
                    "gear, its teeth inside a cone."),
    "mate_teeth": ("Mate teeth", "z₂",
                   "How many teeth the gear this bevel gear meshes with has. A bevel gear's cone, and the Gleason "
                   "split of its tooth depth, depend on its mate; in a pair it is the other gear's teeth."),
    "name": ("Name", "",
             "The file the part is saved as, without .SLDPRT. Blank uses the name shown, built from module and "
             "teeth; in a pair the smaller gear is the pinion."),
    "centre_distance": ("Centre distance", "C",
                        "Shaft to shaft, centre to centre. Standard gears sit at C = m (z₁ + z₂) / 2, their "
                        "pitch circles touching, so C fixes how many teeth the pair has between them once a "
                        "module is chosen."),
    "cone_distance": ("Cone distance", "R",
                      "From the pitch apex, where the two bevel gears' axes meet, out along the pitch cone to "
                      "the back of the teeth. It is a bevel pair's size, as the centre distance is a spur "
                      "pair's: R = m √(z₁² + z₂² + 2 z₁ z₂ cos Σ) / (2 sin Σ)."),
    "mesh": ("Mesh", "",
             "External puts the two gears side by side, turning opposite ways. Internal makes gear B a ring "
             "with gear A inside it, turning the same way, at C = m (z₂ − z₁) / 2."),
    "shafts": ("Shafts", "",
               "Parallel shafts mesh helical gears of equal helix and opposite hand. Crossed shafts mesh them "
               "at an angle: of the same hand their two helix angles add up to the shaft angle, of opposite "
               "hands they differ by it."),
    "hands": ("Hands", "",
              "Whether the two gears of a crossed pair are the same hand or opposite hands. The same hand splits "
              "the shaft angle between the two helices, β₁ + β₂ = Σ, and suits a large angle such as 90°; "
              "opposite hands make it the difference, β₁ − β₂ = Σ, which reaches a small angle with two steep "
              "helices."),
    "pair_shaft_angle": ("Shaft angle", "Σ",
                         "The angle between the two shafts. A crossed helical pair splits it between its helix "
                         "angles; a bevel pair between its pitch cones."),
    "motion": ("Assembly", "",
               "Fixed holds both gears still, meshed: gear 1 fixed and gear 2 mated where its teeth meet gear 1's. "
               "Gear mate lets gear 1 turn on its axis and adds a SolidWorks gear mate, so dragging gear 1 turns "
               "gear 2 at the tooth ratio, the other way round, or the same way round a ring."),
    "ratio": ("Ratio", "i",
              "Turns of the driver for one turn of the driven gear, z₂ / z₁. 3 or 3:1 makes the second gear "
              "three times the first; 1:3 makes it a third."),
    "pair_module": ("Module", "m",
                    "Pin the module the solver may use, or leave it blank to try every standard one in the "
                    "chosen series."),
    "series": ("Series", "",
               "Which standard modules the solver tries. Series 1 is the preferred set (1, 1.25, 1.5, 2, "
               "2.5 …); 1 + 2 adds the in-between sizes (1.125, 1.375 …); + fine adds 0.5, 0.6, 0.7, 0.8 and "
               "0.9 for small gears."),
    "teeth_range": ("Teeth", "min to max",
                    "The tooth counts the solver may give either gear. Below 17 a 20° pinion undercuts; the "
                    "maximum keeps the list short."),
    "assembly_name": ("Assembly name", "",
                      "The file the assembly is saved as, without .SLDASM. Blank uses the name shown, built "
                      "from the module and both tooth counts."),
}


def explainer(field: str, derived, stem: str = "", pair: Optional[PairSpec] = None,
              folder: str = "") -> Tuple[str, str, str, str]:
    """``(name, symbol, what it is, the worked line)`` for one field of the form.

    ``derived`` is the :class:`spur.SpurDerived` of the gear the caret is in and
    ``pair`` the :class:`PairSpec` the solver's own fields are worked out from;
    ``stem`` is the name the part would be saved as and ``folder`` the output
    folder, both of which the Name lines quote. A gear that does not work out —
    ``derived`` ``None``, or a solver field the form cannot yet be read for —
    says ``check the fields``, exactly as the gear readout does, rather than
    showing a number that is about to change.

    The sentences are fixed copy; the worked line is derived text, so the card
    is filled in again on every re-derive and not only when the caret moves.
    """
    try:
        name, symbol, what = _EXPLAINER_COPY[field]
    except KeyError:
        raise ValueError(
            f"There is no explainer for a field called {field!r}; the fields with one are "
            f"{', '.join(EXPLAINER_FIELDS)}."
        ) from None
    return name, symbol, what, _worked_line(field, derived, stem, pair, folder)


def _in(folder: str) -> str:
    """`` in D:\\Gears`` — nothing at all until a folder is chosen."""
    return f" in {folder.strip()}" if folder.strip() else ""


def _worked_line(field: str, derived, stem: str, pair: Optional[PairSpec], folder: str) -> str:
    if derived is None:
        return CHECK_THE_FIELDS
    try:
        if field in PAIR_EXPLAINERS:
            if pair is None:
                return CHECK_THE_FIELDS
            return _pair_worked(field, derived, pair, folder)
        return _gear_worked(field, derived, stem, folder)
    except (InputError, ValueError, ZeroDivisionError):
        return CHECK_THE_FIELDS


def _gear_worked(field: str, g, stem: str, folder: str) -> str:
    if field == "module":
        return (f"m {_n(g.module)} × z {g.teeth} = PD {_n(g.d)} mm · tooth depth {_n(g.h)} · "
                f"circular pitch {_n(g.p)}")
    if field == "teeth":
        undercut = "undercut" if g.undercut else f"no undercut ({_n(g.undercut_limit, 2)} or more)"
        return f"z {g.teeth} → PD {_n(g.d)} mm · OD {_n(g.da)} mm · {undercut}"
    if field == "pressure_angle":
        return (f"{_n(g.pressure_angle_deg, 2)}° → base diameter {_n(g.db)} mm · "
                f"undercut below {_n(g.undercut_limit, 2)} teeth")
    if field == "face_width":
        return f"{_n(g.face_width)} mm = {_n(g.face_width / g.module, 1)} × module"
    if field == "bore":
        if g.bore <= 0:
            return "blank → a solid disc, no bore feature"
        return f"{_n(g.bore)} mm → rim {_n((g.df - g.bore) / 2)} mm to the root circle"
    if field == "backlash":
        # The equations thin the tooth by j and widen the space by j on both
        # gears, so what a mesh actually has to play with is 2 j.
        blank = "" if g.backlash_typed else "blank → "
        default = "" if g.backlash_typed else " (0.3 m)"
        return (f"{blank}{_n(g.backlash)} mm{default} · tooth {_n(g.s)} · space {_n(g.space)} · "
                f"play in the mesh {_n(2 * g.backlash)}")
    if field == "fillet":
        blank = "" if g.fillet_typed else "blank → "
        default = "" if g.fillet_typed else (" (0.15 m)" if is_ring(g) else " (0.38 m)")
        return f"{blank}{_n(g.fillet)} mm{default}"
    if field == "profile_shift":
        if is_bevel(g):
            return "a bevel gear's Gleason addendum is its shift; this stays 0"
        if is_ring(g):
            return "a ring is cut unshifted; this stays 0"
        shift = getattr(g, "shift", 0.0)
        lead = f"x {shift_text(shift)} →" if shift else "0 → a standard tooth ·"
        return (f"{lead} OD {_n(g.da)} mm · root {_n(g.df)} · tooth at pitch {_n(g.s)} · "
                f"undercut below {_n(g.undercut_limit, 2)} teeth")
    if field == "helix_angle":
        if not hasattr(g, "helix_angle_deg"):
            return "only a helical gear has a helix angle"
        return (f"β {_n(g.helix_angle_deg, 4)}° → mt {_n(g.transverse_module, 4)} · PD {_n(g.d)} mm · "
                f"lead {_n(g.lead, 2)} · overlap εβ {_n(g.overlap, 3)}")
    if field == "hand":
        if not hasattr(g, "helix_angle_deg"):
            return "only a helical gear has a hand"
        return (f"{HAND_LABELS.get(g.hand, g.hand).lower()} → wound like a {g.hand}-hand thread, "
                f"{_n(g.face_twist_deg, 2)}° round across the face")
    if field == "groove":
        if getattr(g, "kind", "") != "herringbone":
            return "only a herringbone gear has a centre groove"
        if not g.groove:
            return f"blank → the halves meet at the apex, {_n(g.face_width / 2)} mm of teeth each side"
        return (f"{_n(g.groove)} mm → {_n(g.toothed_width)} mm of teeth each side · floor ⌀ {_n(g.groove_d)} mm")
    if field == "teeth_side":
        if is_bevel(g):
            if g.ring:
                return f"internal → its pitch cone is {_n(g.delta, 2)}°, past 90°, so its teeth are inside the cone"
            if g.crown:
                return "external → a crown gear's teeth stand on its face"
            return "external → a bevel gear's teeth are outside its cone below 90°"
        if is_ring(g):
            return f"internal → teeth point inward from a {_n(g.rim)} mm rim, tips at {_n(g.da)} mm"
        return f"external → teeth point outward, tips at {_n(g.da)} mm"
    if field == "rim":
        if not is_ring(g):
            return "only a ring has a rim"
        blank = "" if g.rim_typed else "blank → "
        return f"{blank}{_n(g.rim)} mm → {_n((g.rim - g.df) / 2)} mm of rim outside the root circle"
    if field == "shaft_angle":
        if not is_bevel(g):
            return "only a bevel gear has a shaft angle"
        form = " · a crown gear" if g.crown else (" · an internal bevel" if g.ring else "")
        return (f"Σ {_n(g.shaft_angle, 2)}° → this gear's cone {_n(g.delta, 3)}°, its mate's "
                f"{_n(g.delta_mate, 3)}°{form}")
    if field == "mate_teeth":
        if not is_bevel(g):
            return "only a bevel gear has a mate count"
        return (f"z₂ {g.mate_teeth} → cone distance {_n(g.cone_distance)} mm · addendum {_n(g.addendum)} · "
                f"dedendum {_n(g.dedendum)}")
    if field == "name":
        return f"{stem}.SLDPRT{_in(folder)}"
    raise ValueError(f"There is no worked line for a gear field called {field!r}.")


def _pair_worked(field: str, g, pair: PairSpec, folder: str) -> str:
    if field == "centre_distance":
        centre = pair.centre_distance_mm()
        # The gear's own module first, then the two standard ones below it: the
        # same centre distance buys more teeth as the module comes down.
        smaller = [m for m in standards.modules(pair.series or standards.SERIES_1) if m < g.module - 1e-9]
        tried = [g.module] + sorted(smaller, reverse=True)[:2]
        sums = " · ".join(f"{int(round(2 * centre / m))} at m {_n(m)}" for m in tried)
        return f"{_n(centre)} mm → z₁ + z₂ = {sums}"
    if field == "cone_distance":
        radius = pair.cone_distance_mm()
        shaft = pair.shaft_angle_deg()
        return (f"{_n(radius)} mm at Σ {_n(shaft, 2)}° → m {_n(g.module)} × z {g.teeth} gives R "
                f"{_n(pairs.bevel.cone_distance(g.module, g.teeth, pair.gear_b.teeth_count(), shaft))}")
    if field == "mesh":
        if pair.mesh_value() == "internal":
            return f"internal → gear B is a ring round gear A, C = m (z₂ − z₁) / 2"
        return "external → the gears sit side by side, C = m (z₁ + z₂) / 2"
    if field == "shafts":
        if pair.shafts_value() == "crossed":
            if pair.hands_value() == "opposite":
                return f"crossed → |β₁ − β₂| = {_n(pair.shaft_angle_deg(), 2)}°, opposite hands"
            return f"crossed → β₁ + β₂ = {_n(pair.shaft_angle_deg(), 2)}°, both gears the same hand"
        return "parallel → both gears the same helix angle, opposite hands"
    if field == "hands":
        shaft = _n(pair.shaft_angle_deg(), 2)
        if pair.hands_value() == "opposite":
            return f"opposite → β₁ − β₂ = ±{shaft}°, gear B the other hand from gear A"
        return f"same → β₁ + β₂ = {shaft}°, gear B the same hand as gear A"
    if field == "pair_shaft_angle":
        return f"Σ {_n(pair.shaft_angle_deg(), 2)}°"
    if field == "motion":
        n1, n2 = pair.gear_a.teeth_count(), pair.gear_b.teeth_count()
        if pair.motion_value() == "fixed":
            return "fixed → gear 1 fixed, gear 2 mated at the mesh angle; nothing turns"
        way = "the same way" if pair.mesh_value() == "internal" else "the other way"
        return f"gear mate → a turn of gear 1 turns gear 2 {_n(n1 / n2, 4)} of a turn, {way}"
    if field == "ratio":
        wanted = pair.ratio.strip() or _n(pair.ratio_value())
        return f"{wanted} → {pair.gear_a.teeth_count()} : {pair.gear_b.teeth_count()}"
    if field == "pair_module":
        pinned = pair.module_mm()
        if pinned is not None:
            return f"m {_n(pinned)} → the solver tries only this module"
        allowed = standards.modules(pair.series or standards.SERIES_1)
        listed = " · ".join(_n(m) for m in allowed[:7])
        return f"blank → {listed} … from {SERIES_LABELS.get(pair.series, pair.series)}"
    if field == "series":
        allowed = standards.modules(pair.series or standards.SERIES_1)
        label = SERIES_LABELS.get(pair.series, pair.series)
        return f"{label} → {len(allowed)} modules from {_n(allowed[0])} to {_n(allowed[-1])} (ISO 54)"
    if field == "teeth_range":
        candidates = pairs.solve_spec(pair)
        exact, shifted = _exact_counts(candidates)
        noun = "candidate" if len(candidates) == 1 else "candidates"
        return (f"{pair.min_teeth_count()} to {pair.max_teeth_count()} → {len(candidates)} {noun} at "
                f"C {_n(pair.centre_distance_mm())}, i {pair.ratio.strip()} · {exact} exact"
                + (f" · {shifted} with shift" if shifted else ""))
    if field == "assembly_name":
        return f"{pair_stems(pair)[2]}.SLDASM{_in(folder)}"
    raise ValueError(f"There is no worked line for a solver field called {field!r}.")


def angle_text(degrees: float) -> str:
    return f"{_n(degrees, 4)}°"


def contact_ratio_text(epsilon: float) -> str:
    return "—" if not math.isfinite(epsilon) else _n(epsilon, 3)


# -- after SolidWorks has done something -------------------------------------


def _file(path: str) -> str:
    return path.replace("\\", "/").rsplit("/", 1)[-1] if path else ""


def build_status(result) -> Tuple[str, bool]:
    """One sentence for a finished build, and whether it went well.

    ``result`` is a :class:`swbuild.BuildResult`, read by its fields only.
    """
    if result.failures:
        what, why = result.failures[0]
        where = f"{result.document} was left open, unsaved" if result.document else "Nothing was built"
        return f"{where}. {what.strip()}: {why}", False
    if not result.saved:
        return f"SolidWorks reported an error rebuilding {result.document}, so it was left open, unsaved.", False
    text = f"Built {_file(result.saved)}."
    if result.checks:
        text += " Check: " + "; ".join(result.checks) + "."
    manual = manual_steps_line(result.manual)
    if manual:
        text += " " + manual
    return text, not result.checks


def pair_status(result) -> Tuple[str, bool]:
    """One sentence for a pair: the first thing that went wrong, or all three files."""
    for part in (result.gear_a, result.gear_b, result.assembly):
        if part is None:
            continue
        text, ok = build_status(part)
        if not ok or not part.saved:
            return text + (f" Skipped {result.skipped}." if result.skipped else ""), False
    files = [_file(part.saved) for part in (result.gear_a, result.gear_b, result.assembly) if part is not None]
    manual = [step for part in (result.gear_a, result.gear_b, result.assembly) if part is not None
              for step in part.manual]
    checks = [check for part in (result.gear_a, result.gear_b, result.assembly) if part is not None
              for check in part.checks]
    text = f"Built {', '.join(files[:-1])} and {files[-1]}."
    if checks:
        text += " Check: " + "; ".join(checks) + "."
    line = manual_steps_line(manual)
    return (text + (" " + line if line else "")), not checks


def update_status(result) -> Tuple[str, bool]:
    """One sentence for Update values."""
    if result.failures:
        what, why = result.failures[0]
        return f"{what} could not be set in {result.document}: {why}", False
    if not result.changed:
        return f"Nothing to update: every value in {result.document} already matches the form.", True
    noun = "variable" if len(result.changed) == 1 else "variables"
    if not result.rebuilt:
        return (f"Changed {len(result.changed)} {noun} in {result.document}, but SolidWorks reported an error "
                "on the rebuild."), False
    return f"Changed {len(result.changed)} {noun} in {result.document} and rebuilt it.", True


# -- the Workbook window (docs/PLAN-WORKBOOK.md §5) --------------------------------------


def _plural(count: int, one: str, many: str = "") -> str:
    return f"{count} {one if count == 1 else (many or one + 's')}"


def short_path(path: str, limit: int = 64) -> str:
    """A path that fits a line: the start and as much of the end as room allows, ``…`` between.

    The end — the folder a file is in, and its name — is what tells files apart,
    so it is kept whole whenever it fits.
    """
    if len(path) <= limit:
        return path
    sep = "\\" if "\\" in path and "/" not in path else "/"
    parts = path.split(sep)
    head = sep.join(parts[:2]) if path.startswith(sep) else parts[0]
    tail: List[str] = []
    for piece in reversed(parts[1:]):
        candidate = sep.join([piece] + tail)
        if len(head) + len(candidate) + 3 > limit and tail:
            break
        tail.insert(0, piece)
    text = f"{head}{sep}…{sep}{sep.join(tail)}"
    if len(text) > limit:
        # One component is longer than the room: keep the start and end of the last one, which is the name.
        name = parts[-1]
        room = max(8, limit - len(head) - 4)
        keep = (room - 1) // 2
        text = f"{head}{sep}…{sep}{name[:keep]}…{name[-(room - 1 - keep):]}"
    return text if len(text) < len(path) else path


def workbook_counts(spec) -> str:
    """``3 shafts · 4 gears · 2 meshes · no modes`` — the header's readout of what the file holds."""
    modes = _plural(len(spec.modes), "mode") if spec.modes else "no modes"
    return " · ".join([_plural(len(spec.shafts), "shaft"), _plural(len(spec.gears), "gear"),
                       _plural(len(spec.meshes), "mesh", "meshes"), modes])


def workbook_read_line(clock_text: str, open_in_excel: bool) -> str:
    """``read 14:02:31 · open in Excel`` — when the file was last read, and whether Excel holds it."""
    return f"read {clock_text}" + (" · open in Excel" if open_in_excel else "")


GEAR_STATE_BUILDS, GEAR_STATE_SHARES, GEAR_STATE_LATER, GEAR_STATE_ERROR = "builds", "shares", "later", "error"
# W4 (Agent C): a gear whose part is built and matches the record; built, and Update SolidWorks would change it;
# built, but its change needs a new part (a new revision). ``workbook_gear_rows`` gains keyword-only ``record=None,
# update=None`` (a store.LinkRecord and a workbook.update.UpdatePlan) to choose them; without them it is as today.
GEAR_STATE_BUILT, GEAR_STATE_CHANGES, GEAR_STATE_NEW_PART = "built", "changes", "new part"


PART_CHARS = 18
# The most characters a Gears-table Part cell is shortened to: the longest names the boards show whole, fixture B's
# "Helical_m2_N20_45R", are 18. It is not a promise that 18 fit: the window shortens further to the room its Part
# column has left beside this workbook's other columns (workbook_gui.WorkbookWindow._fit_part_cells, as measured in
# the table's fonts), down to PART_CHARS_FLOOR. A longer name is shortened (:func:`part_cell`); Tk never cuts a
# label, so it would widen the window, and the board's end-cut hid the end that tells a part from its neighbour.
PART_CHARS_FLOOR = 10
# The fewest characters the window shortens a Part cell to (its head, "…" and five of its end, "Slee…N30_r2" less
# one): below that a cell no longer tells one part from another, so past it the window widens instead.
PART_HEAD = 4                # the characters of a shortened name's head; its kind word starts it
GEAR_STATE_CHARS = 20
# The characters the Gears table's state column holds beside its dot: TABLE_WIDTHS' 128 px, less the 8 px dot and its
# 6 px gap, in the 12 px sans of the hint font — about 20. A wider state widens the column and the window (Tk never
# cuts a label), as "the same part as RangeSlv" took the Gears panel to 643 px against LEFT_WIDTH 610 on the W8
# fixtures. Every state fits: the fixed ones are written to it, and a gear named in one is shortened head and tail
# as the Part column shortens a part name (:func:`_part_cells`, two different gears never reading alike).
SHARES_WORDS = "same as "    # a row whose part another row makes: "same as RangeSlv" (that row's part, by the Part cell)


def part_cell(name: str, width: int = PART_CHARS) -> str:
    """``name`` as the Gears table's Part cell shows it: as it is when it fits ``width`` characters, else its first
    :data:`PART_HEAD` characters, ``…`` and as much of its end as fits — the end is what tells a part from its
    neighbours (teeth, mate teeth, angle, hand, revision; the module it drops has its own column) — the end begun at
    a ``_`` when one falls within two characters of the cut: ``Bevel_m2.5_N20_M30_S120`` is ``Beve…_N20_M30_S120``.
    Only the table's cell (:func:`workbook_gear_rows` keeps different names apart); every sentence names the part
    whole."""
    if len(name) <= width:
        return name
    tail = name[len(name) - (width - PART_HEAD - 1):]
    cut = next((i for i in range(1, 3) if tail[i:i + 1] == "_"), 0) if tail[:1] != "_" else 0
    return name[:PART_HEAD] + "…" + tail[cut:]


def _part_cells(names: Iterable[str], chars: int = PART_CHARS) -> Dict[str, str]:
    """Each distinct part name's cell: :func:`part_cell`, lengthened (up to the whole name) wherever two different
    names would share one, since two rows with the same Part cell read as one shared part file — which the app does
    make for identical gears, and which identical names keep. ``chars``: the room (the state column's gear names
    take :data:`GEAR_STATE_CHARS` less their sentence's words, by the same rule)."""
    names = sorted({n for n in names if n})
    width = {n: chars for n in names}
    while True:
        cells = {n: part_cell(n, width[n]) for n in names}
        by_cell: Dict[str, List[str]] = {}
        for n, cell in cells.items():
            by_cell.setdefault(cell, []).append(n)
        clashes = [group for group in by_cell.values() if len(group) > 1]
        grown = False
        for group in clashes:
            for n in group:
                if width[n] < len(n):
                    width[n] += 1
                    grown = True
        if not grown:
            return cells


def workbook_gear_rows(spec, parts, diagnostics: Sequence[Diagnostic], *, record=None,
                       update=None, plan=None, part_chars: int = PART_CHARS) -> List[Tuple[str, ...]]:
    """One row per gear for the window's table: gear, shaft, kind, teeth, module, face, part, state, what.

    ``part`` is the part file's name without ``.SLDPRT`` (every part is one), so the column stays narrow, and
    one longer than ``part_chars`` (the room the window measured, :data:`PART_CHARS` at most) is shortened to its
    head and end (:func:`part_cell`), two different names never sharing a cell (:func:`_part_cells`).

    ``parts`` is a :class:`workbook.build.PartsPlan` (it may be empty when the
    workbook has errors); ``diagnostics`` are the per-gear ones, each naming its
    cell. ``state`` is one of the ``GEAR_STATE_*`` words, for the window's dot.

    With ``record`` (a ``store.LinkRecord``) a gear its current parts serve is
    *built*, its part the recorded file's; with ``update`` too (a
    ``workbook.update.UpdatePlan``) it is *changes on Update* when its
    part's values change, and *needs a new part* (red) when a reason Update
    cannot carry names it, or its part's file is missing. A gear still to
    build shows the part the build would make — ``plan.part_of`` (a
    ``workbook.gearbox.GearboxPlan``), which is ``<stem>_r2`` when its own
    file name is taken — rather than its own stem (second review N6). A built
    gear whose part the next build would make new rather than reuse
    (``plan.made_new``: its Update not saved, or found not as recorded) is
    *new part on Build*, as the footer says it (the W4 rerun on
    SolidWorks: the table said *built* beside a footer making G2's part new).
    """
    by_gear = {}
    for job in parts.jobs:
        for index, gear_id in enumerate(job.gear_ids):
            by_gear[gear_id] = (job, index)
    later = dict(parts.later)
    built = {g: p for p in (record.current_parts() if record is not None else []) for g in p.gears}
    erred_rows = {_gears_row(d.field) for d in diagnostics if d.is_error}
    erred = {gear.id for gear in spec.gears if gear.row in erred_rows}
    rows = []
    for gear in spec.gears:
        kind = KIND_LABELS.get(gear.kind_word(), gear.kind_word().title())
        if gear.side == "internal":
            kind = "Ring"
        part = ""
        if gear.id in later:
            import re
            phase = re.search(r"phase (W\d+)", later[gear.id])
            state, what = GEAR_STATE_LATER, f"later · phase {phase.group(1)}" if phase else "later"
        elif gear.id in erred:
            state, what = GEAR_STATE_ERROR, "see Checks"
        elif gear.id in built:
            entry = built[gear.id]
            part = _stem(entry.path)
            state, what = _built_state(gear.id, entry, update, plan)
        elif gear.id in by_gear:
            job, index = by_gear[gear.id]
            planned = (getattr(plan, "part_of", None) or {}).get(gear.id, "") if plan is not None else ""
            part = _stem(planned) if planned else job.stem
            if index:
                state, what = GEAR_STATE_SHARES, (SHARES_WORDS, job.gear_ids[0])
            else:
                state, what = GEAR_STATE_BUILDS, "to build"
        else:
            state, what = GEAR_STATE_ERROR, "see Checks"
        rows.append((gear.id, gear.shaft, kind, gear.teeth, gear.module, gear.face_width, part, state, what))
    cells = _part_cells((r[6] for r in rows), part_chars)   # shortened over the whole table, different names apart
    named = _part_cells((r[8][1] for r in rows if isinstance(r[8], tuple)), GEAR_STATE_CHARS - len(SHARES_WORDS))
    return [r[:6] + (cells.get(r[6], r[6]), r[7], r[8][0] + named[r[8][1]] if isinstance(r[8], tuple) else r[8])
            for r in rows]


def _built_state(gear_id: str, entry, update, plan=None) -> Tuple[str, str]:
    """A gear already built: whether Update SolidWorks leaves it, changes it, or cannot carry its change — and
    whether the next build makes its part new rather than reuse it (``plan.made_new``)."""
    import re
    from .store import same_path
    if update is not None:
        named = re.compile(rf"(?<![\w]){re.escape(gear_id)}(?![\w])")
        if any(same_path(entry.path, m) for m in update.missing) or any(named.search(s) for s in update.structural):
            return GEAR_STATE_NEW_PART, "needs a new part"
    if update is not None and any(gear_id in p.gear_ids for p in update.changed_parts):
        return GEAR_STATE_CHANGES, "changes on Update"          # built: the Part cell is the recorded file
    if any(gear_id in m.gear_ids and same_path(m.old, entry.path) for m in (getattr(plan, "made_new", ()) or ())):
        return GEAR_STATE_CHANGES, "new part on Build"
    return GEAR_STATE_BUILT, "built"


def _gears_row(where: str) -> int:
    """The row of a Gears-sheet cell a diagnostic names (``Gears!F3``, ``Gears row 3``), or 0."""
    import re
    match = re.match(r"^Gears(?:!\$?[A-Za-z]{1,3}\$?(\d+)| row (\d+))$", where or "")
    return int(match.group(1) or match.group(2)) if match else 0


def workbook_parts_readout(parts, *, record=None) -> str:
    """The Gears panel's readout: ``4 parts to build · 1 later``.

    With ``record`` (a ``store.LinkRecord``), the parts whose every gear its
    current parts serve are counted as built, as the table's rows say:
    ``4 parts built``, ``3 parts built · 1 to build``."""
    served = {g for p in (record.current_parts() if record is not None else []) for g in p.gears}
    built = [job for job in parts.jobs if job.gear_ids and all(g in served for g in job.gear_ids)]
    new = len(parts.jobs) - len(built)
    if built:
        pieces = [_plural(len(built), "part") + " built"] + ([f"{new} to build"] if new else [])
    else:
        pieces = [_plural(len(parts.jobs), "part") + " to build"] if parts.jobs else ["nothing to build yet"]
    if parts.later:
        pieces.append(f"{len(parts.later)} later")
    return " · ".join(pieces)


CHECKS_PROVISIONAL = ("Provisional: the workbook's formulas still hold Excel's old values, so these checks may "
                      "change once Excel recalculates and saves it, and no fixes are offered until then.")
EXPORT_WAITS = ("the workbook's formulas still hold Excel's old values; open and save it in Excel first, so what is "
                "exported is worked out from what they now give.")


def provisional_tag(provisional: bool) -> str:
    """`` · provisional`` after a readout worked out from a read whose formulas Excel has yet to recalculate."""
    return " · provisional" if provisional else ""


def workbook_checks_readout(diagnostics: Sequence[Diagnostic], provisional: bool = False) -> str:
    if provisional:
        rest = workbook_checks_readout(diagnostics)
        return "provisional" + ("" if rest == "no problems" else f" · {rest}")
    errors = sum(1 for d in diagnostics if d.is_error)
    warnings = len(diagnostics) - errors
    if not diagnostics:
        return "no problems"
    pieces = []
    if errors:
        pieces.append(_plural(errors, "error"))
    if warnings:
        pieces.append(_plural(warnings, "warning"))
    return " · ".join(pieces)


def workbook_changes_readout(changes: Sequence[str], clock_text: str) -> str:
    if not changes:
        return f"nothing changed · {clock_text}"
    return f"{_plural(len(changes), 'change')} · {clock_text}"


CONSEQUENCE_CELLS = 3      # cells named in one piece of the line; more are counted, not named


def _cells(fields: Sequence[str]) -> str:
    cells = list(dict.fromkeys(f for f in fields if f))
    shown = ", ".join(cells[:CONSEQUENCE_CELLS]) + (", …" if len(cells) > CONSEQUENCE_CELLS else "")
    return f" ({shown})" if shown else ""


COVERED_BY_FIX = ", covered by the chosen fix"


def workbook_consequence(consequence, covered: Sequence[Tuple[str, str]] = ()) -> str:
    """What a save did to the checks, in one line: ``G1–G2 now 0.25 mm off · 1 new error (Gears!F3)``.

    ``consequence`` is a :class:`workbook.link.Consequence`. Empty when the
    checks say what they said before; the Checks panel has the sentences.
    ``covered``: meshes said to be off that a chosen, unexported fix puts back
    on centres (:func:`workbook.link.covered_by_fix`)."""
    if not consequence:
        return ""
    pieces = [f"{a}–{b} now on centres" if off is None
              else f"{a}–{b} now {_n(off)} mm off" + (COVERED_BY_FIX if (a, b) in covered else "")
              for a, b, off in consequence.meshes]
    if consequence.new_errors:
        pieces.append(_plural(len(consequence.new_errors), "new error") + _cells(consequence.new_errors))
    if consequence.new_warnings:
        pieces.append(_plural(len(consequence.new_warnings), "new warning") + _cells(consequence.new_warnings))
    if consequence.cleared:
        pieces.append(f"{len(consequence.cleared)} cleared" + _cells(consequence.cleared))
    return " · ".join(pieces)


def workbook_change_lines(changes: Sequence[str], consequence=None,
                          covered: Sequence[Tuple[str, str]] = ()) -> List[str]:
    """The Since the last read panel: one line per changed cell, and what they did.

    One cell changed: what it did follows it on its line, *Gears!F3 G2 Teeth
    68 → 70 · G1–G2 now 1.5 mm off*. Several: no one cell did it, so it is a
    line of its own after them."""
    did = workbook_consequence(consequence, covered) if consequence is not None else ""
    if not did:
        return list(changes)
    if len(changes) == 1:
        return [f"{changes[0]} · {did}"]
    return list(changes) + [did]


def _left_for_later(parts) -> str:
    """`` The layout and assembly are not built: Gears!A6: …`` — never a bare "Ready" or "Built" while rows hold the
    layout back: they are not checked, and nothing places them. W8 was the last phase of the import as planned on
    2026-11-11; W9 (issue #1) builds on it and leaves no row waiting for a phase, so no phase is named: the row's own
    sentence says it is not built by this version of the app (W8-PLAN J18)."""
    refused = getattr(parts, "refused", [])
    if not refused:
        return ""
    more = f" ({len(refused) - 1} more under Checks)" if len(refused) > 1 else ""
    return f" The layout and assembly are not built: {refused[0].message}{more}"


def _shared_steps(results) -> List[str]:
    """Manual steps across a batch, one line for a step every part shares: *Assign a material to each of the 4
    parts* rather than four sentences that differ only in the part's name."""
    import os
    import re
    counts: Dict[str, List[str]] = {}
    for result in results:
        stem = os.path.splitext(os.path.basename(result.saved.replace("\\", "/")))[0]
        for step in result.manual:
            # The part's name as a whole word, and the last one: a name like "a" also reads as a word earlier on.
            found = list(re.finditer(rf"(?<![\w.-]){re.escape(stem)}(?![\w.-])", step)) if stem else []
            key = step[:found[-1].start()] + "{part}" + step[found[-1].end():] if found else step
            counts.setdefault(key, []).append(step)
    out = []
    for key, steps in counts.items():
        if len(steps) > 1 and "{part}" in key:
            out.append(key.replace("{part}", f"each of the {len(steps)} parts"))
        else:
            out.extend(steps)
    return out


NOTE_JOB = "job"              # a finished job's own sentence: it marks a moment the workbook may have moved on from
NOTE_STANDING = "standing"    # what an Export, a Locate… or a save did: no job stood between it and the state
NOTE_ANSWER = "answer"        # how the Build again? question was answered: the state it answered still holds


@dataclass(frozen=True)
class Note:
    """The Workbook window's last sentence of its own, kept until the file next changes: ``text``, shown as good
    when ``ok``, and its ``kind``, which says how the footer joins it to the state (:func:`workbook_footer`):

    - :data:`NOTE_JOB` — a build's or an update's sentence. It takes the
      state's place while the state is fine; otherwise *… Since then: <state>*.
    - :data:`NOTE_STANDING` — what an Export, a Locate… or a save did. It
      takes the state's place while the state is fine; otherwise the state
      follows plainly, since it was already so.
    - :data:`NOTE_ANSWER` — No to *Build again?*, or the question left open
      while the workbook changed. The state follows plainly, always: the
      reason the question was asked still stands (W4 review nit).
    """

    text: str
    ok: bool
    kind: str = NOTE_JOB


def _as_note(note) -> Optional[Note]:
    """A :class:`Note`, or a plain ``(text, ok)`` pair from a caller that knows only a job's sentence (the
    demonstration script's desk), taken as a job's."""
    if note is None or isinstance(note, Note):
        return note
    text, ok = note
    return Note(text, ok)


def export_note(done, copy_name: str = "") -> Note:
    """What an Export did, for the footer: a :data:`NOTE_STANDING` :class:`Note`. ``done`` is a
    :class:`workbook.export.Exported`; ``copy_name`` the file Export as… wrote, or ``""``.

    A formula cell is never written over. When it is a fix's target the
    formula may well land on the fix's value once Excel recalculates — S3's X
    as ``=C3+68`` follows S2 — so the sentence says what to look for rather than
    asking for the formula to be typed over, and Results wait for that save.
    The fix's own value is given (no fix is offered from a provisional read,
    so it is worked from what Excel last calculated), but Checks are the test.
    When every cell the fix names is a formula nothing reaches the file, so
    nothing a formula reads has changed: that is said as a fault, and the
    formula, or a cell it reads, is what has to change."""
    formula_cells = {cell for cell, *_ in done.formulas}
    if not done.written and done.formulas and all(cell in formula_cells for cell, _ in done.refused):
        # Nothing reached the file, so nothing a formula reads changed: recalculating cannot move them.
        cells = "; ".join(f"{cell} ({item} {header}, the fix would make it {value})"
                          for cell, item, header, value in done.formulas)
        where = f"changed in the copy, {copy_name}" if copy_name else "written"
        return Note(f"Nothing was {where}: every cell the fix would change holds a formula — {cells} — and Excel "
                    "recalculating cannot move them, since nothing they read has changed. Change the formula, or a "
                    "cell it reads, in Excel; the fix stays chosen until then.", False, NOTE_STANDING)
    what = _plural(len(done.written), "cell") + (" and the Results sheet" if done.results else "")
    parts = [f"Exported {what}" + (f" to {copy_name}" if copy_name else "") + "."]
    if done.added_headers:
        parts.append("Added the column " + ", ".join(done.added_headers) + ".")
    for cell, item, header, value in done.formulas:
        parts.append(f"{cell} ({item} {header}) holds a formula, so it was not written (the fix would make it "
                     f"{value}): once Excel has recalculated, Checks will say whether {item} sits where its meshes "
                     "need it.")
    others = [(cell, why) for cell, why in done.refused if cell not in formula_cells]
    if others:
        parts.append("Not written: " + "; ".join(f"{cell} ({why})" for cell, why in others)
                     + ". Results were not written, since the fix is only partly in the workbook.")
    elif done.formulas:
        parts.append("The Results sheet was left out until then: Export again after Excel's save to write it."
                     if not copy_name else "The Results sheet was left out of the copy, since the fix is only "
                                           "partly in it.")
    if done.results_error:
        parts.append(f"The Results sheet could not be written: {done.results_error} Export again to write it.")
    return Note(" ".join(parts), not others and not done.results_error, NOTE_STANDING)


RECALC_WAIT = ("Export wrote cells that formulas in the workbook may depend on: open and save it in Excel so they "
               "recalculate; Build and Export wait for that save.")
RESULTS_DUE = " Export again to write the Results sheet: it waited for Excel to recalculate."


NBSP = "\u00a0"
# A no-break space: the Speeds lines wrap at the end view's width in the window, and must break only between their
# parts, never between a number and its unit or inside a slant's vector. U+00A0 rather than the narrow U+202F: it is
# in every font Tk and the boards' HTML fall back to, and keeps an ordinary space's width, so nothing moves.


def _copies_of(shaft) -> int:
    """A Shafts row's Copies as a number (blank, or anything not a whole number above 0, is 1)."""
    try:
        n = int(str(getattr(shaft, "copies", "") or "1").strip())
    except ValueError:
        return 1
    return n if n > 0 else 1


def _held_members(spec) -> set:
    """The held members of a planetary stage, from the workbook's rows (W7): a carrier (a shaft another is mounted
    on) or a frame shaft whose gear meshes a planet, whose Role is ``fixed`` — whether or not a torque is typed, so
    the Speeds panel says *held* either way."""
    shafts = list(getattr(spec, "shafts", ()) or ())
    mounted = {s.id: s.mount() for s in shafts if hasattr(s, "mount") and s.mount() != "frame"}
    if not mounted:
        return set()
    shaft_of = {g.id: g.shaft for g in getattr(spec, "gears", ()) or ()}
    planets = {g for g, shaft in shaft_of.items() if shaft in mounted}
    members = set(mounted.values())
    for mesh in getattr(spec, "meshes", ()) or ():
        if mesh.a in planets:
            members.add(shaft_of.get(mesh.b, ""))
        if mesh.b in planets:
            members.add(shaft_of.get(mesh.a, ""))
    return {s.id for s in shafts if s.id in members and str(getattr(s, "role", "")).strip().lower() == "fixed"}


def workbook_speed_lines(spec, motion) -> Tuple[List[str], str]:
    """The Speeds panel: one line per shaft (speed, way round, torque), and its header readout. A gearbox a
    later phase drives gives the one sentence saying so, and no readout.

    W6 (W6-PLAN §2.9, D12): each shaft's way round is seen from its own family's + end (``Motion.seen_from``,
    ``"+X"``, or a slant's plus direction ``"(0.5, −0.866, 0)"``). When every shaft is in the Z family the panel
    reads as W3's, *seen from +Z* in the readout; otherwise each line says which end it is seen from, *S1 1500.0
    rpm anticlockwise seen from the +X end · 10.00 N·m* (a slant's *seen from the (0.5, −0.866, 0) end*: one form
    for both, so the slant's components never read as a point), and the readout is *seen from each shaft's + end*.
    Each number is joined to its unit, and a slant's vector held together, by :data:`NBSP`, so a wrapped line
    breaks only between its parts. W7: a planet shaft and a held member take :func:`planetary_speed_line`."""
    return _speed_lines(spec, motion)


def _speed_lines(spec, motion, *, free: str = "not driven") -> Tuple[List[str], str]:
    """:func:`workbook_speed_lines`' body; ``free`` is what a shaft no input settles reads (W8: a member a mode
    leaves free *turns freely*, :func:`mode_speed_lines`)."""
    if motion.later:
        return [motion.later], ""
    seen = getattr(motion, "seen_from", None) or {}
    every_z = all(seen.get(shaft.id, "+Z") == "+Z" for shaft in spec.shafts)
    lines = []
    held = set(getattr(motion, "held", None) or {}) | _held_members(spec)
    for shaft in spec.shafts:
        mount = shaft.mount() if hasattr(shaft, "mount") else "frame"
        if mount != "frame":                      # W7: a planet shaft, its speed on its carrier and its copies
            lines.append(planetary_speed_line(shaft.id, motion, copies=_copies_of(shaft), carrier=mount))
            continue
        if shaft.id in held:                      # W7: a held member of a planetary stage, and what it holds
            lines.append(planetary_speed_line(shaft.id, motion, held=True))
            continue
        speed = motion.speeds.get(shaft.id)
        if speed is None:
            lines.append(f"{shaft.id:<4}  {free}")
            continue
        torque = motion.torques.get(shaft.id)
        torque_text = f" · {torque:.2f}{NBSP}N·m" if torque is not None else ""
        onward = (getattr(motion, "shared", None) or {}).get(shaft.id)
        if onward and torque is not None:          # W8 (J17): an output that also drives onward
            torque_text += f", shared with {_and(onward)} (the share depends on the loads)"
        elif shaft.id in (getattr(motion, "past_split", None) or ()):
            torque_text = " · — (past a split)"
        turns = motion.turns(shaft.id)
        where = seen.get(shaft.id, "+Z").replace(" ", NBSP)        # a slant's vector held together
        if not every_z and turns and turns != "still":
            turns = f"{turns} seen from the {where} end"
        lines.append(f"{shaft.id:<4}  {abs(float(speed)):.1f}{NBSP}rpm {turns}{torque_text}")
    note = _torque_note_shown(motion)
    if note:                                      # W7: why a torque through a planetary stage is not given
        lines.append(_sentence(note))
    if not motion.speeds:
        return lines, "no input"
    return lines, ("seen from +Z" if every_z else "seen from each shaft's + end")


def _torque_note_shown(motion) -> str:
    """``Motion.torque_note`` when the Speeds panel ends with it (shafts are turning and no later phase drives the
    gearbox), else ""."""
    note = getattr(motion, "torque_note", "")
    return note if note and motion.speeds and not motion.later else ""


def speeds_prose_rows(motion, lines: Sequence[str], *, mode: bool = False, chooser: bool = False) -> Set[int]:
    """Which of the Speeds panel's ``lines`` are sentences, shown in prose, not as a shaft's line: every line when a
    later phase drives the gearbox (``Motion.later``), else the torque note when the panel shows it (W7). W8: with
    ``mode`` the lines are :func:`mode_speed_lines`' and ``motion`` that mode's (``ModeReport.motion``), whose first
    two lines, the mode's speeds and ratio and what it couples, are prose too; with ``chooser`` the window shows its
    mode chooser and the panel ends with :func:`mode_chooser_note`, prose, after everything else (the torque note
    then the line before it). The one home of that rule; the window and the design board ask it."""
    if not lines:
        return set()
    if motion.later:
        return set(range(len(lines)))
    end = len(lines) - 1 if chooser else len(lines)          # past the shafts' lines and the torque note
    rows = {end} if chooser else set()
    if end and _torque_note_shown(motion):
        rows.add(end - 1)
    return rows | ({0, 1} & set(range(end)) if mode else set())


VIEW_READOUT_CHARS = 44
# The characters the End view panel's header leaves its readout at the window's design width: the panel is the end
# view's 392 px canvas plus its 12 px body padding each side, and its header holds 12 px, the title END VIEW, FROM
# YOUR ORIGIN (about 170 px of 11.5 px bold capitals), 8 px, the readout and 12 px — about 216 px of 11.5 px sans,
# some 44 characters of heights, dots and spaces (workbook_gui.END_VIEW, widgets.Panel; the boards draw it the same).
# Tk never cuts a label, so a longer readout widens the right column and squeezes the Gears table.
VIEW_READOUT_HEIGHTS = 4     # face heights listed one by one, at most (W8: a transfer case in 2H has 7)


def end_view_readout(view) -> str:
    """The end view's header: the face heights it colours apart, and whether the origin is in sight — *z 7.5 · z
    27 · origin* (*· origin off view*). Up to :data:`VIEW_READOUT_HEIGHTS` heights are listed while the line fits
    :data:`VIEW_READOUT_CHARS`; past that it counts them, *7 face heights, z 10 to 130 · origin* (the colours still
    one per face height, in UI-DESIGN's order, nearest +Z drawn last), and *7 face heights · origin off view* where
    even the range would not fit."""
    origin = " · origin" if view.origin else " · origin off view"
    planes = list(view.planes or ())
    listed = " · ".join(f"z {_n(z, 1)}" for z in planes) + origin
    if len(planes) <= VIEW_READOUT_HEIGHTS and len(listed) <= VIEW_READOUT_CHARS:
        return listed
    count = f"{len(planes)} face heights"
    ranged = f"{count}, z {_n(min(planes), 1)} to {_n(max(planes), 1)}{origin}"
    return ranged if len(ranged) <= VIEW_READOUT_CHARS else f"{count}{origin}"


# -- W4: the footer as one decision, and the sentences of a gearbox build and update ----------------------------
#
# Interfaces pinned in the W4 interface commit (docs/PLAN-WORKBOOK.md §5, W4-PLAN §4.1–§4.2). ``workbook_footer``
# replaced W2–W3's ``workbook_state`` once the window was wired to it. Everything here reads the plans and the
# worker's results by their fields only (never ``GearboxResult.ok``), and the worker's own BuildError text is
# shown as it comes, never reworded.

BUILD = "build"              # make the parts, the layout part and the assembly (reusing what is built)
BUILD_PARTS = "parts"        # W2's batch, when only rows a later phase builds hold the layout back
BUILD_AGAIN = "again"        # an assembly is on record: ask, then make the next revision
BUILD_LABELS = {BUILD: "Build", BUILD_PARTS: "Build parts", BUILD_AGAIN: "Build again…"}

RECALC_WAIT_UPDATE = ("Export wrote cells that formulas in the workbook may depend on: open and save it in Excel so "
                      "they recalculate; Build, Update SolidWorks and Export wait for that save.")
ALREADY_MATCHES = "SolidWorks already matches the workbook: nothing was changed."


def save_to_keep(paths: Sequence[str]) -> str:
    """After an update, the save asked for, naming every document it changed (W4 review S4.8: a bare *Save in
    SolidWorks to keep it.* followed a list of several)."""
    return f"Save {_and(_stem(p) for p in paths)} in SolidWorks to keep {_them(len(paths))}."


@dataclass(frozen=True)
class Footer:
    """The Workbook window's footer, decided whole: the sentence and how it is shown, and both buttons.

    ``build_action`` is one of :data:`BUILD`, :data:`BUILD_PARTS`,
    :data:`BUILD_AGAIN` and ``build_label`` its :data:`BUILD_LABELS` word;
    ``build_primary`` is False for Build again… (Update is the primary then).
    ``update_shown`` once anything is on record; ``update_enabled`` under the
    same gate as Build plus the record's own checks; ``update_primary`` once
    an assembly is on record.
    """

    text: str
    ok: bool
    build_action: str = BUILD
    build_label: str = "Build"
    build_enabled: bool = False
    build_primary: bool = True
    update_shown: bool = False
    update_enabled: bool = False
    update_primary: bool = False


_EXTENSIONS = (".sldprt", ".sldasm", ".slddrw")


def _stem(path: str) -> str:
    """``C:\\P\\Gear_m1.5_N68.SLDPRT`` -> ``Gear_m1.5_N68``; a SolidWorks extension only, so ``Gear_m1.5`` keeps
    its ``.5``."""
    name = _file(path)
    return name[:-7] if name.lower().endswith(_EXTENSIONS) else name


def _folder_of(path: str) -> str:
    text = path.replace("\\", "/")
    return path[:len(text.rsplit("/", 1)[0])] if "/" in text else ""


def _and(items: Iterable[str]) -> str:
    """``A``, ``A and B``, ``A, B and C``."""
    items = [str(i) for i in items if str(i)]
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def _sentence(text: str) -> str:
    text = text.strip()
    return text if not text or text[-1] in ".?!…" else text + "."


def progress_text(step, updating: bool = False) -> str:
    """*Building in SolidWorks: part 2 of 4, Gear_m1.5_N68…*, *… the layout part…*, *… the assembly…*,
    *… checking interference…*; *Updating SolidWorks: Gear_m1.5_N68…* — from a ``swbuild.Step`` (None: the
    first words alone)."""
    from . import swbuild
    lead = "Updating SolidWorks" if updating else "Building in SolidWorks"
    if step is None:
        return f"{lead}…"
    name, of = step.name, (f"{step.index} of {step.count}" if step.count else "")
    stage = step.stage
    if stage == swbuild.STAGE_PART:
        what = ", ".join(p for p in (f"part {of}" if of else "a part", name) if p)
    elif stage == swbuild.STAGE_CHECK:
        counted = (f"{of} already built" if not updating else of) if of else ""
        what = f"checking {name or 'what is built'}" + (f" ({counted})" if counted else "")
    elif stage == swbuild.STAGE_LAYOUT:
        what = "the layout part" + (f", {name}" if name else "")
    elif stage == swbuild.STAGE_ASSEMBLY:
        what = "the assembly" + (f", {name}" if name else "")
    elif stage == swbuild.STAGE_INTERFERENCE:
        what = "checking interference"
    elif stage == swbuild.STAGE_VALUES:
        what = name or "the values"
    elif stage == swbuild.STAGE_PLACE:
        what = "placing the gears" + (f" in {name}" if name else "")
    elif stage == getattr(swbuild, "STAGE_MODE", None):
        # W8: one mode's configuration, set up or checked (Step.name: the mode's name; Step does not say which).
        what = ("checking mode " if updating else "mode ") + name + (f", {of}" if of and not updating else "")
    else:
        what = name
    return f"{lead}: {what}…" if what else f"{lead}…"


def _clash_lines(clashes) -> List[str]:
    lines = []
    for clash in clashes:
        named = [g for g in (clash.gears or clash.components) if g]
        if len(named) >= 2:
            lines.append(f"{_and(named)} interfere, {_n(clash.volume)} mm³")
        elif named:
            lines.append(f"{named[0]} interferes with something, {_n(clash.volume)} mm³")
        else:
            lines.append(f"an interference of {_n(clash.volume)} mm³ that SolidWorks could not name")
    return lines


def _all_meshes(clashes, meshes) -> bool:
    """Whether every clash is between the two gears of a listed mesh. ``meshes`` None: not known (the wording from
    before W4's smoke test, which took every clash for a mesh)."""
    if meshes is None:
        return True
    listed = {frozenset(pair) for pair in meshes}
    return all(len(set(c.gears)) == 2 and frozenset(c.gears) in listed for c in clashes)


def _interference(clashes, error: str, assembly: str, meshes=None, *, turning: bool = False) -> Tuple[str, bool]:
    """``; no interference between the gears`` (to end a sentence), or a sentence of its own that stands out. In an
    assembly whose gears turn (``turning``) the check is of where they stand: ``… where they stand`` (W5-PLAN §1.8).

    A clash is said to be at *their mesh* only when its two gears are a listed mesh (``meshes``, pairs of gear
    ids): SolidWorks 2026 showed a widened gear clashing with one beside it on the same shaft that it does not
    mesh with (W4 smoke test), so any other clash, or one it could not name, is *where they meet*."""
    where = f" in {assembly}" if assembly else ""
    if error:
        return f". Interference could not be checked: {_sentence(error)} Look at each mesh{where} by eye.", False
    if clashes:
        lines = _clash_lines(clashes)
        if _all_meshes(clashes, meshes):
            look = "at their mesh" if len(lines) == 1 else "at those meshes"
        else:
            look = "where they meet"
        return f". Check: {'; '.join(lines)}; look {look}{where}.", False
    return f"; no interference between the gears{' where they stand' if turning else ''}.", True


def _done_phrase(made: Sequence[str], reused: Sequence[str]) -> str:
    """``Built 1 part and R_r2_Layout, reusing the 3 parts already built``; ``Reused R_Layout and …``."""
    if made:
        return "Built " + _and(made) + (", reusing " + _and(reused) if reused else "")
    if reused:
        return "Reused " + _and(reused)
    return ""


def _already(count: int) -> str:
    return "" if not count else ("the part already built" if count == 1 else f"the {count} parts already built")


def _layout_reused(plan) -> bool:
    from .workbook.gearbox import LayoutReuse
    return isinstance(getattr(plan, "layout", None), LayoutReuse)


def _never_made(doc) -> bool:
    """A document SolidWorks never made (``swbuild._build_in_job``: no title, its first step the new document's):
    a template it could not use, nearly always, so pressing again fails the same way until that is changed."""
    return not doc.document and doc.stopped_at in ("new part", "new assembly")


def _went_wrong(doc, name: str, title: str = "") -> str:
    """What one document's failure left, as a sentence: *SolidWorks did not make the assembly. There is no
    assembly template at …* for one never made (no label left lower-case in the middle: W4 review S4.3), else
    *Part3 was left open, unsaved; cut 'Tooth Space': FeatureCut4 would not cut.* ``title``: how the document
    made is named (*the assembly Assem1*), its SolidWorks title by default."""
    title = title or doc.document
    if doc.failures:
        what, why = doc.failures[0]
        if _never_made(doc):
            return f"SolidWorks did not make {name}. {_sentence(why)}"
        if what.strip() == "save":
            return f"{title} was left open, unsaved, since it would not save: {_sentence(why)}"
        if what.strip() == "the build":
            return f"{title} was left open, unsaved: {_sentence(why)}"
        return f"{title} was left open, unsaved; {what.strip()}: {_sentence(why)}"
    return f"SolidWorks reported an error rebuilding {title}, so it was left open, unsaved."


def _template_first(doc, button: str, reused: str) -> str:
    """For a document never made: change the template before pressing again (the same press would fail the same
    way); else ``""``."""
    if not _never_made(doc):
        return ""
    noun = "assembly" if doc.stopped_at == "new assembly" else "part"
    tail = f": {reused}" if reused else ""
    return (f" Set {'an' if noun == 'assembly' else 'a'} {noun} template SolidWorks can use (the Box sheet's "
            f"{noun.capitalize()} template, else the strip's), then press {button}{tail}.")


def _gears_part(gear_ids: Sequence[str], count: int = 1) -> Tuple[str, str]:
    """(``G2's part`` / ``the part for G1 and G5`` / ``the parts for G1 and G2``, ``is``/``are``)."""
    ids = list(gear_ids)
    if count == 1:
        return (f"{ids[0]}'s part" if len(ids) == 1 else f"the part for {_and(ids)}"), "is"
    return f"the parts for {_and(ids)}", "are"


def _them(count: int) -> str:
    return "it" if count == 1 else "them"


def _mismatched_status(plan, result, button: str) -> str:
    """A build the live check stopped (``GearboxResult.mismatched``): what it found, and that the next press makes
    those parts new — the finish has recorded them (W4 review B2's last corner) — rather than fail again."""
    from . import store
    found = [p for p, _ in result.mismatched]
    reuse = list(getattr(plan, "reuse", ()) or ())
    parts = [r for r in reuse if any(store.same_path(r.path, p) for p in found)]
    layout = getattr(plan, "layout", None)
    layout_bad = _layout_reused(plan) and any(store.same_path(layout.path, p) for p in found)
    does = []
    if parts:
        who, _ = _gears_part([g for r in parts for g in r.gear_ids], len(parts))
        does.append(f"makes {who} new rather than reuse {_and(r.stem for r in parts)}")
    if layout_bad:
        does.append("builds the next revision, with a layout part of its own")
    whys = " ".join(_sentence(why) for _, why in result.mismatched)
    then = (f" The next press of {button} {_and(does)}; nothing is overwritten." if does else
            f" The next press of {button} does not reuse {_them(len(found))}.")
    return f"Nothing was built. {whys}{then}"


def gearbox_status(plan, result, again: bool = False) -> Tuple[str, bool]:
    """A finished build's sentence (``workbook.gearbox.GearboxPlan``, ``swbuild.GearboxResult``): *Built 4 parts,
    Reducer_12to1_Layout and Reducer_12to1.SLDASM; no interference between the gears.*, a clash's *Check: G1 and
    G2 interfere, 12.345 mm³; …*, or what went wrong and what the next press does.

    ``again``: the press was Build again… (an assembly was on record), so
    until this revision's layout part is saved the button still reads Build
    again… and the sentence names it. A document SolidWorks never made (its
    template) asks for the template first rather than another press that
    would fail the same way. A raise between documents
    (``GearboxResult.failures``) says where the job stopped and what was not
    attempted; a live check that found a document to reuse not holding what
    it should (``mismatched``) says what it found and that the next press
    makes it new."""
    parts_only = plan is None or (plan.layout is None and plan.assembly is None)
    layout = result.layout
    layout_on = bool(result.layout_reused) or (layout is not None and layout.ok and bool(layout.saved))
    button = "Build parts" if parts_only else ("Build again…" if again and not layout_on else "Build")
    if result.mismatched:
        return _mismatched_status(plan, result, button), False
    made = [r for r in result.parts.built if r.ok and r.saved]
    reused_parts = len(plan.reuse) if plan is not None else 0
    reused_layout = _stem(result.layout_reused) if result.layout_reused else ""
    made_names = [_plural(len(made), "part")] if made else []

    for part in result.parts.built:
        if not (part.ok and part.saved):
            text = _went_wrong(part, _stem(part.path) or "the part")
            before = f"{_plural(len(made), 'part')} built before it; " if made else ""
            skipped = len(result.parts.skipped)
            if parts_only:
                tail = f" {_plural(skipped, 'part')} not attempted." if skipped else ""
            elif skipped:
                tail = f" {_plural(skipped, 'part')} not attempted, nor the layout and assembly."
            else:
                tail = " The layout and assembly were not attempted."
            reused = "what was built is reused" if made or reused_parts else ""
            then = _template_first(part, button, reused) or (
                f" Press {button} to carry on" + (f": {reused}." if reused else "."))
            return f"{before}{text}{tail}{then}", False

    if layout is not None and not (layout.ok and layout.saved):
        text = _went_wrong(layout, "the layout part")
        done = _done_phrase(made_names, [_already(reused_parts)] if reused_parts else [])
        lead = f"{done}; " if done else ""
        reused = ("the parts are reused" if made or reused_parts else "")
        then = _template_first(layout, button, reused) or (
            f" Press {button} to carry on" + (f": {reused}." if reused else "."))
        return f"{lead}{text} The assembly was not attempted.{then}", False

    layout_name = _stem(layout.saved) if layout is not None and layout.saved else ""
    carriers = list(getattr(result, "carriers", ()) or ())                  # W7: the carrier parts, after the layout
    carrier_names = [_stem(c.saved) for c in carriers if c.ok and c.saved]
    carriers_reused = [_stem(p) for p in getattr(result, "carriers_reused", ()) or ()]
    for carrier in carriers:
        if not (carrier.ok and carrier.saved):
            text = _went_wrong(carrier, "the carrier part")
            done = _done_phrase(made_names + ([layout_name] if layout_name else []) + carrier_names,
                                ([reused_layout] if reused_layout else []) + carriers_reused
                                + ([_already(reused_parts)] if reused_parts else []))
            lead = f"{done}; " if done else ""
            text = text if lead else text[:1].upper() + text[1:]
            reused = "the parts and layout are reused" if done else ""
            then = _template_first(carrier, button, reused) or (
                f" Press {button} to carry on" + (f": {reused}." if reused else "."))
            return f"{lead}{text} The assembly was not attempted.{then}", False
    assembly = result.assembly
    if (assembly is not None and not (assembly.ok and assembly.saved)
            and any(str(p).strip() for p in assembly.mate_problems)):
        return mate_refused_status(plan, result, again)      # W5: a refused or flagged mate stops the build
    if assembly is not None and not (assembly.ok and assembly.saved):
        made_now = made_names + ([layout_name] if layout_name else []) + carrier_names
        reused_now = (([reused_layout] if reused_layout else []) + carriers_reused
                      + ([_already(reused_parts)] if reused_parts else []))
        done = _done_phrase(made_now, reused_now)
        failed = _went_wrong(assembly, "the assembly", f"the assembly {assembly.document}")
        lead = f"{done}; " if done else ""
        failed = failed if lead else failed[:1].upper() + failed[1:]
        then = _template_first(assembly, button, "the parts and layout are reused") or (
            f" Press {button} to try the assembly again: the parts and layout are reused.")
        return f"{lead}{failed}{then}", False

    built_names = made_names + ([layout_name] if layout_name else []) + carrier_names
    asm_name = _file(assembly.saved) if assembly is not None and assembly.saved else ""
    if asm_name:
        built_names.append(asm_name)
    reused_names = (([reused_layout] if reused_layout else []) + carriers_reused
                    + ([_already(reused_parts)] if reused_parts else []))
    done = _done_phrase(built_names, reused_names)
    if result.failures:
        # A raise between documents (W4 review B1): the job returned what it had saved, and says where it stopped.
        what, why = result.failures[0]
        later = [] if plan is None else [
            name for name, planned, reached in (
                ("the layout part", plan.layout is not None and not _layout_reused(plan), layout is not None),
                ("the assembly", plan.assembly is not None, assembly is not None))
            if planned and not reached and name != what]
        missed = (f" {_and(later)[:1].upper()}{_and(later)[1:]} {'was' if len(later) == 1 else 'were'} not "
                  "attempted.") if later else ""
        stopped = f"The job stopped during {what}: {_sentence(why)}{missed}"
        if not done:
            return f"Nothing was saved. {stopped} Press {button} to try again.", False
        return f"{done}. {stopped} Press {button} to carry on: what was built is reused.", False
    if not done:
        return "Nothing was built.", False
    results = made + [r for r in (layout, *carriers, assembly) if r is not None and r.saved]
    checks = [c for r in results for c in r.checks]
    ok = not checks
    if not parts_only and not asm_name:
        # Planned and never reached, with nothing failing: say what the worker said was left.
        skipped = f" {_sentence(result.skipped)}" if result.skipped else " The assembly was not made."
        text, ok = f"{done}.{skipped}", False
    elif asm_name:
        from .store import GEARBOX_MOTION
        listed = tuple(plan.meshes) if plan is not None and plan.meshes else None
        if getattr(result, "modes", None):                 # W8: each mode's configuration, checked in turn
            ending, clean = _modes_interference(result.modes, asm_name, listed, _modes_of(plan))
        else:
            ending, clean = _interference(result.clashes, result.interference_error, asm_name, listed,
                                          turning=getattr(result, "kind", "") == GEARBOX_MOTION)
        text, ok = done + ending, ok and clean
        turning = motion_done_line(plan, result)
        if turning:
            text += " " + turning
    else:
        text = f"{done}."
    if checks:
        text += " Check: " + "; ".join(checks) + "."
    manual = manual_steps_line(_shared_steps(results))
    if manual:
        text += " " + manual
    return text, ok


def _missing_sentence(missing: Sequence[str]) -> str:
    files = [_file(p) for p in missing]
    if len(files) == 1:
        folder = _folder_of(missing[0])
        where = f"in {short_path(folder, 48)}" if folder else "where it was built"
        return (f"{files[0]} is no longer {where}: it was moved, renamed or deleted since it was built, so Update "
                "SolidWorks cannot change it.")
    return (f"{_and(files)} are no longer where they were built: they were moved, renamed or deleted since, so "
            "Update SolidWorks cannot change them.")


_STRIP_AGAIN = "; build it again as a new part."


def _reason(text: str) -> str:
    """A reason Update cannot carry, as the workbook says it. ``swbuild.structural_change`` ends its sentence for
    the strip's single part, *…; build it again as a new part.*; folded into the footer's offer that read "build
    again" twice (W4 review S4.2), so here the part *needs a new part* and the offer says how."""
    text = _sentence(text)
    return text[:-len(_STRIP_AGAIN)] + ", so it needs a new part." if text.endswith(_STRIP_AGAIN) else text


def _cannot_carry(update) -> str:
    """Why Update SolidWorks cannot carry the change, as one sentence (the first reason, and how many more)."""
    if update.missing:
        more = len(update.structural)
        also = f" (and {_plural(more, 'other change')} it cannot carry)" if more else ""
        return _missing_sentence(update.missing)[:-1] + also + "."
    more = len(update.structural) - 1
    also = f" (and {_plural(more, 'other change')} Update SolidWorks cannot carry)" if more else ""
    return _reason(update.structural[0])[:-1] + also + "."


def _again_sentence(update, name: str = "", *, turning: str = "") -> str:
    """Why Update cannot carry it, and the offer: *Gear_m1.5_N17 (G1): The recipe changed from 'A' to 'B', so it
    needs a new part. Update SolidWorks offers to build again as Reducer_12to1_r2.* — "build again" once.
    ``turning`` (W5, D5): what the offer adds for a static gearbox whose new revision turns, *; it was built
    static, …, and the new revision's gears turn*, so that is said in the one offer rather than a second."""
    target = name or "a new revision"
    offer = f"Update SolidWorks offers to build again as {target}{turning}."
    if update.missing:
        more = len(update.structural)
        also = f" (and {_plural(more, 'other change')} Update SolidWorks cannot carry)" if more else ""
        files = [_file(p) for p in update.missing]
        if len(files) == 1:
            folder = _folder_of(update.missing[0])
            where = f"in {short_path(folder, 48)}" if folder else "where it was built"
            return (f"{files[0]} is no longer {where}: it was moved, renamed or deleted since it was built{also}, so "
                    f"{offer}")
        return (f"{_and(files)} are no longer where they were built: they were moved, renamed or deleted since{also}, "
                f"so {offer}")
    return f"{_cannot_carry(update)} {offer}"


def _mated_copies(update) -> Dict[str, int]:
    """Each planet row's copies among the recorded mates (``update.motion.mates``), for :func:`_bodies`."""
    motion = getattr(update, "motion", None)
    return _copy_counts(g for m in getattr(motion, "mates", ()) or () for g in m.gears)


def _carrier_part_of(update, shaft: str) -> str:
    """The stem of ``shaft``'s carrier part among ``update.carriers`` (``layout.carrier_stem``'s ending), or ``""``."""
    from .workbook.layout import CARRIER_SUFFIX
    for doc in getattr(update, "carriers", ()) or ():
        if _stem(doc.path).endswith(f"_{shaft}{CARRIER_SUFFIX}"):
            return _stem(doc.path)
    return ""


def _carrier_shaft_of(update, stem: str) -> str:
    """The carrier shaft whose part is ``stem`` (``layout.carrier_stem``'s ending), from the carriers the update
    knows (``update.motion.carriers``, ``update.carriers_moved``); ``""`` if none."""
    from .store import CARRIER_ID_SUFFIX
    from .workbook.layout import CARRIER_SUFFIX
    links = getattr(getattr(update, "motion", None), "carriers", ()) or ()
    shafts = [c.carrier[:-len(CARRIER_ID_SUFFIX)] for c in links if c.carrier.endswith(CARRIER_ID_SUFFIX)]
    shafts += list(getattr(update, "carriers_moved", ()) or ())
    return next((shaft for shaft in shafts if stem.endswith(f"_{shaft}{CARRIER_SUFFIX}")), "")


def _to_replace(update) -> List[str]:
    """The gears Update SolidWorks will put: ``update.replaced`` on W4's static path. On a turning gearbox
    (``update.motion``), a mated gear the plan must move — its frame changes, its Face Z is set (``update.axial``),
    its shaft moves (``update.moved_shafts``, through its axis and along mates), or a gear mate of its train takes a
    new ratio — takes every mated gear of its train with it (review M1, and package A's rule since ba2bc1f), the
    train read from the recorded meshes and locks (``MotionUpdate.meshes``, ``locks``; a mated gear with neither is
    a train of its own); a gear on no mate
    (left fixed, re-placed W4's way) is named as it is. In ``placements`` order, then in the gears' own order (G2
    before G10)."""
    replaced = [g for g in update.replaced if g]
    motion = getattr(update, "motion", None)
    if motion is None:
        return replaced
    mated = [g for m in motion.mates for g in m.gears if g]
    group = {g: {g} for g in mated}
    links = [(m.a, m.b) for m in motion.meshes] + [(k.anchor, k.follower) for k in motion.locks]
    links += [(c.carrier, p) for c in getattr(motion, "carriers", ()) or () for p in c.planets]   # W7: its planets
    for a, b in links:
        joined = group.setdefault(a, {a}) | group.setdefault(b, {b})
        for g in joined:
            group[g] = joined
    axial = {g for g in getattr(update, "axial", ()) or () if g}
    # W7: a row's shared Face Z global is keyed by the row (W7-INTERFACES §6.7): every copy of it moves.
    rows = {g for g in mated if _copy_parts(g)[1] and _copy_parts(g)[0] in axial}
    axial = {g for g in axial if g in group or not any(_copy_parts(c)[0] == g for c in rows)} | rows
    wanted = set(replaced) | axial
    for name in getattr(update, "ratios", ()) or ():
        wanted.update(g for m in motion.mates if m.name == name for g in m.gears if g)
    moved = set(getattr(update, "moved_shafts", ()) or ())
    wanted.update(g for m in motion.mates if m.shaft and m.shaft in moved for g in m.gears if g)
    out = set()
    for gear in wanted:
        out |= group.get(gear, {gear})
    # W7 (§6.5): a held member is put only when it must be re-placed itself, and then first (J15's order: held
    # member, carrier, train); a train's put never moves it.
    held = set(getattr(motion, "held", ()) or ())
    out -= held - set(replaced)
    import re
    from .store import CARRIER_ID_SUFFIX
    seen = [g for g in dict.fromkeys(p.gear for p in update.placements) if g in out]
    rest = sorted(out - set(seen), key=lambda g: [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", g)])
    ordered = seen + rest
    return ([g for g in ordered if g in held] + [g for g in ordered if g.endswith(CARRIER_ID_SUFFIX)]
            + [g for g in ordered if g not in held and not g.endswith(CARRIER_ID_SUFFIX)])


def _parts_left_in_error(result) -> List[str]:
    """The documents an Update changed whose rebuild reported an error, by stem (``swbuild.UpdateResult``: a change
    set, not rebuilt, and a failure of the job naming the document; a rebuild in error from the user's features alone
    is no failure): the parts, the layout and the carriers."""
    from .workbook.update import documents_left_in_error
    return [_stem(d.document) for d in documents_left_in_error(result)]


def update_summary(update) -> str:
    """What Update SolidWorks will do, before the press (``workbook.update.UpdatePlan``): *Update SolidWorks will
    change G2's values (Gear_m1.5_N68), move S2 and S3 in Reducer_12to1_Layout, and re-place G2, G3 and G4.*; the
    structural sentence when it needs a new revision; *SolidWorks already matches the workbook on record* when
    nothing on record differs. On a turning gearbox (W5) also *move G4 along S3* (``update.axial``) and *set the
    gear mate G1 meshes G2 to 17 : 69* (``update.ratios``)."""
    if update.refusal:
        return update.refusal
    if update.needs_new_revision:
        return _again_sentence(update)
    axial = [g for g in getattr(update, "axial", ()) if g]
    ratios = [n for n in getattr(update, "ratios", ()) if n]
    modal = _mode_summary_pieces(update)             # W8: slide values and flags per configuration
    in_place = in_place_pieces(update)               # W9c: what it adds, takes out, makes and remakes in place
    if update.record_matches and not (axial or ratios or getattr(update, "resensed", ())
                                      or getattr(update, "carriers_moved", ()) or modal or in_place):
        text = ("SolidWorks already matches the workbook on record; Update SolidWorks checks it live and puts right "
                "anything changed there")
        if getattr(update, "motion", None) is not None:
            text += "; gears turned in SolidWorks stay where they are unless something must move"
        return _with_leftovers(text + ".", update)
    pieces = list(in_place)
    changed = update.changed_parts
    if len(changed) == 1 and len(changed[0].gear_ids) == 1:
        pieces.append(f"change {changed[0].gear_ids[0]}'s values ({_stem(changed[0].path)})")
    elif changed:
        pieces.append("change the values in " + _and(f"{_stem(p.path)} ({', '.join(p.gear_ids)})" for p in changed))
    if update.moved_shafts:
        layout = f" in {_stem(update.layout.path)}" if update.layout is not None else ""
        pieces.append(f"move {_and(update.moved_shafts)}{layout}")
    for shaft in getattr(update, "carriers_moved", ()) or ():   # W7: the planets' axes in the carrier part
        part = _carrier_part_of(update, shaft)
        pieces.append(f"move the planets on {shaft}" + (f" in {part}" if part else ""))
    if axial:                                  # W5: an anchor's distance along its shaft (its Face Z global)
        pieces.append(f"move {_along(update, axial)}")
    resensed = [n for n in getattr(update, "resensed", ()) or () if n]
    plain = [n for n in ratios if n not in resensed]
    if plain:                                  # W5: only once a gear mate's ratio can be changed (D7)
        with_modes = bool(_configurations_of(update))
        pieces.append(f"set {_gear_mates(update, plain)}"
                      + (" (made again, with its flag set in every mode)" if with_modes and len(plain) == 1 else
                         " (made again, with their flags set in every mode)" if with_modes else ""))
    for name in resensed:                      # W6 (M4, D17): a crossed mesh's sense changed with a move
        at = f" at {_asked_ratio(update, name)}" if name in ratios and _asked_ratio(update, name) else ""
        pieces.append(f"remake the gear mate {name}{at} {_resense_why(update, name)}")
    pieces += modal
    replaced = _to_replace(update)
    if replaced:
        pieces.append(f"re-place {_and(_bodies(replaced, _mated_copies(update)))}")
    if len(pieces) > 1:
        pieces[-1] = "and " + pieces[-1]
    return _with_leftovers("Update SolidWorks will " + ", ".join(pieces) + ".", update)


def _with_leftovers(text: str, update) -> str:
    said = leftovers_sentence(update)
    return f"{text} {said}" if said else text


def leftovers_sentence(update) -> str:
    """W9c (the review's must-fix 2): what an Update that stopped part way made that this read no longer uses
    (``UpdatePlan.leftovers``), said as the app's own, before the press and after it: *An Update SolidWorks that
    stopped part way left the global Hub Face Z, the configuration R and the part Hub_m1.25_N17.SLDPRT, which the
    workbook no longer uses: Update SolidWorks leaves them as they are and keeps them on record as its own, so a
    later press can use them again; delete them in SolidWorks if you no longer want them.*"""
    from .workbook.update import LEFT_CONFIGURATION, LEFT_GLOBAL
    left = list(getattr(update, "leftovers", ()) or ())
    if not left:
        return ""
    words = [f"the global {name}" if what == LEFT_GLOBAL else f"the configuration {name}"
             if what == LEFT_CONFIGURATION else f"the part {_file(name)}" for what, name in left]
    one = len(words) == 1
    return (f"An Update SolidWorks that stopped part way left {_and(words)}, which the workbook no longer uses: "
            f"Update SolidWorks leaves {'it' if one else 'them'} as {'it is' if one else 'they are'} and keeps "
            f"{'it' if one else 'them'} on record as its own, so a later press can use {'it' if one else 'them'} "
            f"again; delete {'it' if one else 'them'} in SolidWorks if you no longer want {'it' if one else 'them'}.")


def _kept_name(path: str, spec) -> str:
    """`` (it now has 69 teeth; its file keeps its name)`` when a value update leaves a default-named part's file
    name saying what it no longer holds; ``""`` otherwise (a Part name of the user's own never goes stale)."""
    import re
    if spec is None or str(getattr(spec, "name", "")).strip():
        return ""
    try:
        wanted = spec.default_stem()
    except Exception:  # noqa: BLE001 - a spec that does not work out has no name to compare
        return ""
    held = re.sub(r"_r\d+$", "", _stem(path))
    if held == wanted:
        return ""
    for mark, word in (("N", "{} teeth"), ("m", "module {}")):
        old, new = (re.search(rf"_{mark}([^_]+)", s) for s in (held, wanted))
        if old and new and old.group(1) != new.group(1):
            now_ = "now has" if mark == "N" else "is now"
            return f" (it {now_} {word.format(new.group(1))}; its file keeps its name)"
    return " (its file keeps its name, which no longer says what it holds)"


def _layout_shafts(names: Sequence[str]) -> List[str]:
    """``["S2 X", "S3 X", "S3 Y"]`` -> ``["S2", "S3"]``: the shafts a layout's changed globals move."""
    shafts: List[str] = []
    for name in names:
        head, _, axis = name.rpartition(" ")
        if head and axis in ("X", "Y") and head not in shafts:
            shafts.append(head)
    return shafts


def gearbox_update_status(update, result, dragged: Sequence[str] = (), **kwargs) -> Tuple[str, bool]:
    """:func:`_gearbox_update_status`, and (the W9c fixes review's M3) when the finish found documents still on
    record as left in error by an earlier Update that stopped (``Finished.still_in_error``: this press neither found
    them closed nor rebuilt them clean, so it set nothing in them), the truthful answer: never *SolidWorks already
    matches the workbook*, but to close them without saving and press again."""
    text, ok = _gearbox_update_status(update, result, dragged, **kwargs)
    finished = kwargs.get("finished")
    still = list(getattr(finished, "still_in_error", ()) or ()) if finished is not None else []
    if not still or result.failures:
        return text, ok
    said = still_in_error_sentence(still)
    if text.startswith(ALREADY_MATCHES):
        # Only the claim is replaced; what follows it (the interference, the user's work, the modes, the leftovers)
        # stays (the second reading of the fixes review, N4).
        return said + text[len(ALREADY_MATCHES):], False
    return f"{text} {said}", False


def still_in_error_sentence(paths: Sequence[str]) -> str:
    """*Gear_m1.25_N29 is still open in SolidWorks as an earlier Update SolidWorks left it, in error and holding the
    new values, so this press set nothing in it: close it in SolidWorks without saving (the file on disk is as before
    that Update), then press Update SolidWorks again.*"""
    one = len(paths) == 1
    return (f"{_and(_stem(p) for p in paths)} {'is' if one else 'are'} still open in SolidWorks as an earlier Update "
            f"SolidWorks left {'it' if one else 'them'}, in error and holding the new values, so this press set "
            f"nothing in {'it' if one else 'them'}: close {'it' if one else 'them'} in SolidWorks without saving (the "
            f"{'file' if one else 'files'} on disk {'is' if one else 'are'} as before that Update), then press Update "
            "SolidWorks again.")


def _gearbox_update_status(update, result, dragged: Sequence[str] = (), *, meshes=None,
                          finished=None, revision: Sequence[int] = ()) -> Tuple[str, bool]:
    """A finished update's sentence (``UpdatePlan``, ``swbuild.GearboxUpdate``, ``Finished.dragged``), ending
    with :func:`save_to_keep` naming the documents whenever ``result.changed`` is not empty; *SolidWorks already
    matches the workbook: nothing was changed.* when nothing was. ``meshes``: the record's listed meshes (pairs of
    gear ids), so a clash is called a mesh only when it is one (see :func:`_interference`).

    On a turning gearbox (``update.motion``, W5) the sentence adds what the
    motion path did and found (:func:`_motion_pieces`, :func:`_motion_after`),
    the interference is of the gears *where they stand*, and a job that
    stopped says every failure, not only the first: a lock that could not be
    turned back on after a put that failed is a failure of its own, naming
    the compound gears left unlocked (review M8), and must not be hidden
    behind the put's. W4's static path reads as it always has.

    ``revision`` (W9a): the SolidWorks the job ran on (the window's ``Job.revision``), for
    :data:`WHATS_WRONG_AFTER` where that version shows What's Wrong with the user's work in error.

    ``finished`` (``workbook.gearbox.Finished``, the window passes it): when
    its ``earlier_update`` is set — an earlier Update's changes to the
    assembly were never saved, closed unsaved (``lost``) or not saved — what
    was found off the record is not laid to the user, on either path: no
    *had been moved* or *turned … in SolidWorks*, but
    :func:`_earlier_update_sentence`. With ``earlier_update`` ``""`` (or no
    ``finished``) every sentence is as before."""
    changed_docs = [_stem(p) for p in result.changed]
    motion = getattr(update, "motion", None) is not None
    earlier = getattr(finished, "earlier_update", "") if finished is not None else ""
    off_after = [g for g in getattr(finished, "off_after_update", ()) or () if g] if earlier else []
    pairs_after = [tuple(p) for p in getattr(finished, "out_of_step_after_update", ()) or ()] if earlier else []
    if result.failures:
        what, why = result.failures[0]
        text = f"Update SolidWorks stopped. {what.strip()}: {_sentence(why)}"
        if motion:
            groups: List[Tuple[str, List[str]]] = []
            for what, why in result.failures:
                if groups and groups[-1][0] == what.strip():
                    groups[-1][1].append(_sentence(why))
                else:
                    groups.append((what.strip(), [_sentence(why)]))
            text = "Update SolidWorks stopped. " + " ".join(f"{w}: {' '.join(ys)}" for w, ys in groups)
        done_in_place = in_place_done_pieces(update, result) if motion else []
        if done_in_place:                  # W9c: what it made or took away before it stopped, and what it did not
            text += f" Before it stopped it {_and(done_in_place)}."
        if motion and result.skipped and getattr(update, "in_place", None):
            text += f" It did not get to {str(result.skipped).rstrip('.')}."
        in_error = _parts_left_in_error(result)
        if changed_docs and in_error:
            # The W9c runs review's should-fix: a part whose rebuild reported an error stays open in its failed state,
            # holding the new value, so a press on it sets nothing and it never mends; and the documents changed with
            # it, saved beside it closed, would leave gears at their new values against it as it was. So every
            # document changed is closed without saving, and saving is never offered.
            one = len(changed_docs) == 1
            text += (f" It had already changed {_and(changed_docs)}, not saved, and {_and(in_error)} "
                     f"{'is' if len(in_error) == 1 else 'are'} left in error: close {'it' if one else 'them all'} in "
                     f"SolidWorks without saving (the {'file' if one else 'files'} on disk {'is' if one else 'are'} as "
                     "before this Update), then press Update SolidWorks again.")
        elif changed_docs:
            one = len(changed_docs) == 1
            text += (f" It had already changed {_and(changed_docs)}, not saved: press Update SolidWorks again once "
                     f"that is put right, or save {'it' if one else 'them'} in SolidWorks to keep what it did.")
        elif not done_in_place:
            text += " Nothing was changed."
        # K3 on the failure path too (the close review's must-fix 2): what of the user's features this Update rebuilt
        # into error is named as theirs, with what it set under them, after the stop, which stays as it is; one
        # already in error before is said here only when the stop's own sentence has not named it.
        for sentence in _user_feature_sentences(result, update):
            if " was in error in SolidWorks before this Update" in sentence and \
                    sentence.split(" in ", 1)[0].replace("Your ", "", 1) in text:
                continue
            text += " " + sentence
        if (changed_docs or result.placed) and _users_in_error(result) and whats_wrong_shows(revision):
            text += " " + WHATS_WRONG_AFTER         # W9a: SolidWorks 2024's box, once, after a stop that wrote
        return text, False

    pieces: List[str] = []
    ok = True
    for index, part in enumerate(result.parts):
        if not part.changed:
            continue
        planned = update.parts[index] if index < len(update.parts) else None
        name = _stem(planned.path) if planned is not None else _stem(part.document)
        pieces.append(f"changed {_plural(len(part.changed), 'variable')} in {name}"
                      + _kept_name(planned.path if planned is not None else part.document,
                                   getattr(planned, "spec", None)))
        if not part.rebuilt and not _users_alone(planned.path if planned is not None else part.document, result):
            pieces[-1] += " (SolidWorks reported an error rebuilding it)"
            ok = False
    if result.layout is not None and result.layout.changed:
        name = _stem(update.layout.path) if update.layout is not None else _stem(result.layout.document)
        shafts = _layout_shafts(result.layout.changed)
        pieces.append(f"moved {_and(shafts)} in {name}" if shafts
                      else f"changed {_plural(len(result.layout.changed), 'variable')} in {name}")
        if not result.layout.rebuilt:
            pieces[-1] += " (SolidWorks reported an error rebuilding it)"
            ok = False
    for carrier in getattr(result, "carriers", ()) or ():                # W7 (§6.11): as the layout's
        if not carrier.changed:
            continue
        # Matched to its carrier part by file name, never by position; one that matches none is not said.
        doc = next((d for d in getattr(update, "carriers", ()) or ()
                    if _file(d.path).lower() == _file(carrier.document).lower()), None)
        shaft = _carrier_shaft_of(update, _stem(doc.path)) if doc is not None else ""
        if not shaft:
            continue
        pieces.append(f"moved the planets on {shaft} in {_stem(doc.path)}")
        if not carrier.rebuilt:
            pieces[-1] += " (SolidWorks reported an error rebuilding it)"
            ok = False
    if motion:
        pieces = in_place_done_pieces(update, result) + pieces     # W9c: what it built, added and took out first
        pieces.extend(_motion_pieces(update, result))
        pieces.extend(_mode_pieces(update, result))   # W8: slide values and flags, per configuration
    after = _motion_after(update, result, earlier) if motion else []
    dragged = list(dragged)
    placed = [g for g in result.placed if g not in dragged]
    if placed:                                       # W7: the carrier and N copies named once (§2.12)
        pieces.append(f"re-placed {_and(_bodies(placed, _mated_copies(update)) if motion else placed)}"
                      + _put_where(update, result))

    assembly = _file(update.assembly) if update.assembly else ""
    nothing = not pieces and not dragged and not result.changed
    if motion:
        after = after + _mode_after(update, result, changed=not nothing, earlier=earlier)
    if earlier:
        told = _earlier_update_sentence(update, result if motion else None, earlier, off_after, pairs_after,
                                        changed=not nothing,
                                        still_in_error=bool(getattr(finished, "still_in_error", ()) or ()))
        after = ([told] if told else []) + after
    # W9a: what it did with and found of the user's work, after the assembly's rebuild laid to that work alone.
    after = after + _rebuild_from_user(update, result) + _user_after(update, result)
    after = after + in_place_after(update, result)                   # W9c: the modes' consequences for the user
    if leftovers_sentence(update):
        after = after + [leftovers_sentence(update)]                 # W9c: the app's leftovers, said as its own

    if not nothing and _users_in_error(result) and whats_wrong_shows(revision):
        # W9a: SolidWorks 2024's box, once, after an Update that changed or put something (never a quiet press,
        # which rebuilds nothing: the close review on 2024 found it said after such presses, where no box came).
        after.append(WHATS_WRONG_AFTER)
    if nothing:
        text = ALREADY_MATCHES
        if assembly and getattr(result, "modes", None) and any(m.clashes or m.interference_error
                                                                for m in result.modes):
            ending, ok = _modes_interference(result.modes, assembly, meshes, _configurations_of(update))
            text += ending[1:]
        elif assembly and (result.clashes or result.interference_error):
            ending, ok = _interference(result.clashes, result.interference_error, assembly, meshes, turning=motion)
            text += ending[1:]
        return _joined(text, *after), ok
    put_back = ""
    if dragged:
        one = len(dragged) == 1
        put_back = (f"{_and(dragged)} had been moved in SolidWorks; put back where the workbook has "
                    f"{'it' if one else 'them'}")
    text = "Updated SolidWorks: " + (", ".join(pieces) if pieces else put_back)
    if assembly:
        if not result.rebuilt and not getattr(result, "rebuild_from_user_alone", None):
            text += f". SolidWorks reported an error rebuilding {assembly}, so look at it before saving."
            ok = False
        elif getattr(result, "modes", None):         # W8: each configuration it post-checked
            ending, clean = _modes_interference(result.modes, assembly, meshes, _configurations_of(update))
            text, ok = text + ending, ok and clean
        else:
            ending, clean = _interference(result.clashes, result.interference_error, assembly, meshes,
                                          turning=motion)
            text, ok = text + ending, ok and clean
    else:
        text += "."
    if put_back and pieces:
        text += f" {put_back}."
    if after:
        text += " " + " ".join(after)
    if result.changed:
        text += " " + save_to_keep(result.changed)
    return text, ok


def _configurations_of(update) -> Tuple[str, ...]:
    """The modes on record an Update works across (``MotionUpdate.configurations``); ``()`` with none."""
    return tuple(getattr(getattr(update, "motion", None), "configurations", ()) or ())


def _put_where(update, result) -> str:
    """W8: `` in 4H and 4L`` / `` in every mode`` after *re-placed …*, from ``result.put_in`` (the configurations
    gears were put in); ``""`` for a gearbox with no modes."""
    put = [str(c) for c in getattr(result, "put_in", ()) or () if str(c)]
    if not put:
        return ""
    every = [str(c).casefold() for c in getattr(getattr(update, "motion", None), "configurations", ()) or ()]
    if every and sorted(c.casefold() for c in put) == sorted(every) and len(every) > 1:
        return " in every mode"
    return f" in {_and(put)}"


def _made_new_by(plan, why: str) -> list:
    return [m for m in (getattr(plan, "made_new", ()) or ()) if m.why == why]


def _occupied(plan, overwritten: bool = True, superseded: Sequence[str] = ()) -> str:
    """Why a new part takes another file name than its own (``GearboxPlan.made_new``, review S5), one sentence per
    reason: *Gear_m1.5_N17.SLDPRT is already there, built from this workbook for values G1 no longer has, so G1's
    part is made as Gear_m1.5_N17_r2; nothing is overwritten.* For a copied workbook the files of the workbook it
    was copied from are said once, by :func:`_copy_sentence`, not part by part. *Nothing is overwritten* is said
    once, after the last (``overwritten``; the question says it in its own last sentence). A part of this
    workbook's own for other values that is one of the parts on record (``superseded``) is not said: it is the
    part a change Update cannot carry replaces, and that change's sentence says so already."""
    from . import store
    from .workbook.gearbox import NO_RECORD, OTHER_WORKBOOK, STALE
    folder = getattr(plan, "folder", "") or ""
    copied = getattr(plan, "foreign_record", "") or ""
    groups: Dict[Tuple[str, str], list] = {}
    for m in getattr(plan, "made_new", ()) or ():
        if m.why not in (STALE, OTHER_WORKBOOK, NO_RECORD):
            continue
        if m.why == OTHER_WORKBOOK and copied and store.same_path(m.workbook, copied):
            continue
        if m.why == STALE and any(store.same_path(m.old, p) for p in superseded):
            continue
        groups.setdefault((m.why, m.workbook.lower()), []).append(m)
    out = []
    for (why, _), items in groups.items():
        one = len(items) == 1
        files = _and(_file(m.old) for m in items)
        there = _folder_of(items[0].old)
        where = ("already there" if not there or store.same_path(there, folder)
                 else f"already in {short_path(there, 48)}")
        ids = [g for m in items for g in m.gear_ids]
        who, be = _gears_part(ids, len(items))
        lead = f"{files} {'is' if one else 'are'} {where}"
        if why == STALE:
            lead += f", built from this workbook for values {_and(ids)} no longer {'has' if len(ids) == 1 else 'have'}"
        elif why == OTHER_WORKBOOK:
            lead += f", built from {_file(items[0].workbook)}"
        else:
            lead += (f", with no record that this workbook built {_them(len(items))} (a build that was interrupted "
                     "can leave such a file)")
        out.append(f"{lead}, so {who} {be} made as {_and(_stem(m.new) for m in items)}")
    if not out:
        return ""
    return ". ".join(out) + ("; nothing is overwritten." if overwritten else ".")


def _held_back(plan, subject: str, after_unsaved_line: bool) -> str:
    """The parts made new although a built one matched (``GearboxPlan.made_new``, UNSAVED and MISMATCHED), as what
    ``subject`` (*Build*, *the new revision*) does: *While Gear_m1.5_N68's changes are not saved, the new revision
    makes G2's part new, as Gear_m1.5_N69, rather than reuse it.* — after the sentence asking for the save, which is
    not asked again (W4 review S3, S4.1); true too if SolidWorks closed it unsaved, which nothing here can know
    (second review N2) — else with its own reason. A part marked mismatched — a check found it not holding what
    the record says, or a job found it closed with Update's changes unsaved — *does not hold what the record
    says, as the last job in SolidWorks found*."""
    from .workbook.gearbox import MISMATCHED, UNSAVED
    out = []
    for why in (UNSAVED, MISMATCHED):
        items = _made_new_by(plan, why)
        if not items:
            continue
        one = len(items) == 1
        olds = _and(_stem(m.old) for m in items)
        who, _ = _gears_part([g for m in items for g in m.gear_ids], len(items))
        does = (f"{subject} makes {who} new, as {_and(_stem(m.new) for m in items)}, rather than reuse "
                f"{_them(len(items))}.")
        if why == UNSAVED and after_unsaved_line:
            whose = f"{olds}'s changes are" if one else f"the changes in {olds} are"
            out.append(f"While {whose} not saved, {does}")
        elif why == UNSAVED:
            out.append(f"{olds} {'has' if one else 'have'} changes from Update SolidWorks that are not saved, so "
                       f"{does}")
        else:
            out.append(f"{olds} {'does' if one else 'do'} not hold what the record says, as the last job in "
                       f"SolidWorks found, so {does}")
    return " ".join(out)


def _copy_sentence(plan) -> str:
    """A copied workbook (``GearboxPlan.foreign_record``, review S1): the record that came with it, and the files it
    lists, are the other workbook's; Build makes this one's own beside them. A record whose workbook is gone, and
    nobody has said whether this one was moved from it (``plan.foreign_gone``, second review N1c), is said as
    such: the window is asking. One whose workbook is gone and which the person said this one is a copy of
    (``plan.foreign_said``, third review) is said so — never "still there" — with the way to take the answer back:
    it holds for the session only, so until this workbook has built its own gearbox, a new session asks again."""
    other = plan.foreign_record
    if getattr(plan, "foreign_said", False):
        return (f"The record that came with this workbook was written for {short_path(other, 48)}, which you said "
                "this workbook is a copy of, so that record, and the SolidWorks files it lists, are that workbook's: "
                "Build makes this workbook's own gearbox beside them, sharing and overwriting nothing. If this "
                "workbook was in fact moved or renamed from it, quit Gear Generator and open this workbook again "
                "before you build, and you are asked again.")
    if getattr(plan, "foreign_gone", False):
        return (f"The record that came with this workbook was written for {short_path(other, 48)}, which is not there "
                "any more: until you say whether this workbook was moved or renamed from it, Build makes this "
                "workbook's own gearbox beside the files it lists, sharing and overwriting nothing.")
    return (f"This workbook is a copy of {short_path(other, 48)}, which is still there, so the record that came with "
            "it is that workbook's, and so are the SolidWorks files it lists: Build makes this workbook's own gearbox "
            "beside them, sharing and overwriting nothing.")


def build_again_question(update, again, *, record=None, foresight=None) -> str:
    """The *Build again?* question (``UpdatePlan``, and the ``GearboxPlan`` it would run): why Update cannot carry
    the change, what the new revision makes and reuses — and why a part is made new although one was built — and,
    decision 8, that the reused parts are shared, so a later Update changes the earlier revision's assembly too.
    Never promises the old assembly is untouched, and never names one when none was built (a record from Build
    parts).

    W5 (D5): when ``record`` (the link record the question is about) holds a
    static assembly and the new revision's plan turns (``again.motion``),
    the question says so — *Reducer_12to1.SLDASM was built static; the new
    revision's gears are mated to turn.* — in place of *Nothing on record
    needs a new revision.*, or after the reasons. Without ``record`` nothing
    is said about it: ``update.motion`` alone cannot tell a static gearbox
    from a turning one whose change needs a new revision.

    W9d: what of the user's work the new revision takes (:func:`carry_sentence`), from ``foresight``
    (``workbook.update.CarryForesight``; None: worked here from ``record``)."""
    from .store import GEARBOX_STATIC
    from .workbook.gearbox import MISMATCHED, UNSAVED
    reasons = []
    if update is not None and update.refusal:
        reasons.append(_sentence(update.refusal))   # e.g. classify refusing a recorded mate it cannot act on (W5)
    if update is not None and update.missing:
        reasons.append(_missing_sentence(update.missing))
    if update is not None:
        reasons.extend(_reason(s) for s in update.structural)
    box = getattr(record, "gearbox", None)
    if box is not None and box.assembly and box.kind == GEARBOX_STATIC and getattr(again, "motion", None) is not None:
        reasons.append(f"{_file(box.assembly)} was built static; the new revision's gears are mated to turn.")
    if not reasons:
        reasons.append("Nothing on record needs a new revision.")
    text = " ".join(reasons) + f" Build again as {again.name}?"
    if again.refusal:
        return f"{text} It cannot go ahead: {again.refusal}"

    does = []
    if again.build:
        news = [f"{', '.join(job.gear_ids)} ({job.stem})" for job in again.build]
        does.append(f"makes {'a new part' if len(news) == 1 else 'new parts'} for {_and(news)}")
    kept = len(again.reuse)
    if kept:
        does.append(f"reuses {_plural(kept, 'part')} that {'has' if kept == 1 else 'have'} not changed")
    asm = _file(again.assembly_path) if again.assembly_path else ""
    new_carriers, kept_carriers = _plan_carriers(again)          # W7: the carrier part beside the layout part
    if _layout_reused(again):
        reusing = [_stem(again.layout.path)] + kept_carriers
        made = (f"makes a new carrier part and assembly ({_and(new_carriers + [asm])})" if new_carriers
                else f"makes a new assembly, {asm}")
        does.append(f"reuses {_and(reusing)} and {made}")
    elif again.layout is not None:
        if new_carriers or kept_carriers:
            also = f", reusing {_and(kept_carriers)}" if kept_carriers else ""
            what = "layout part, carrier part and assembly" if new_carriers else "layout part and assembly"
            does.append(f"makes a new {what} ({_and([_stem(again.layout_path)] + new_carriers + [asm])}){also}")
        else:
            does.append(f"makes a new layout part and assembly ({_stem(again.layout_path)} and {asm})")
    if does:
        text += " That " + _and(does) + "."
    for why, because, after in ((UNSAVED, "has changes from Update SolidWorks that are not saved", True),
                                (MISMATCHED, "does not hold what the record says, as the last job in SolidWorks "
                                             "found", False)):
        items = _made_new_by(again, why)
        if not items:
            continue
        one = len(items) == 1
        who, be = _gears_part([g for m in items for g in m.gear_ids], len(items))
        olds = _and(_stem(m.old) for m in items)
        said = because if one else because.replace("has", "have", 1).replace("does", "do", 1)
        text += f" {who[:1].upper()}{who[1:]} {be} new because {olds} {said}"
        # The save it asks for may no longer be possible (SolidWorks closed since): said so, true either way (N2).
        them = _them(len(items))
        text += (f"; to reuse {them} instead, answer No and save {them} in SolidWorks first (if SolidWorks has "
                 f"closed {them} since without saving, those changes are gone, and {them} cannot be reused)."
                 if after else ".")
    occupied = _occupied(again, overwritten=False,
                         superseded=[p.path for p in update.parts] if update is not None else ())
    if occupied:
        text += " " + occupied

    old = _file(update.assembly) if update is not None and update.assembly else ""
    if not old:
        text += " Nothing is overwritten, and what is already built is left as it is."
    elif kept:
        one = kept == 1
        text += (f" Nothing is overwritten, and {old} stays as it is on disk, but it shares the "
                 f"{'reused part' if one else f'{kept} reused parts'}: a later Update SolidWorks that changes "
                 f"{'it' if one else 'one of them'} changes {old} too.")
    else:
        text += f" Nothing is overwritten, and {old} and its files are left as they are."
    # W9d (W9D-INTERFACES §9.1): what of the user's the new revision takes, from the record's inventory with its time
    # through plan_carry's foresight (W9a's stays-behind clause, led by its finding, while CARRY_INSERTS is unset).
    if foresight is None:
        from .workbook.update import carry_foresight
        foresight = carry_foresight(record, again)
    behind = carry_sentence(foresight, again)
    if behind:
        text += " " + behind
    return text


def _without_folder(assessment):
    """The assessment as if an output folder were set: Update SolidWorks writes nothing there, so a folder unset
    or gone must not hold it back (review nit)."""
    if assessment.folder:
        return assessment
    import dataclasses
    return dataclasses.replace(assessment, folder="-")


def _plan_carriers(plan) -> Tuple[List[str], List[str]]:
    """The carrier parts a ``GearboxPlan`` makes and those it reuses, by stem (W7: ``plan.carriers``, a
    ``CarrierReuse`` for one reused, and ``plan.carrier_paths``)."""
    from .workbook.gearbox import CarrierReuse
    kept = [c.path for c in getattr(plan, "carriers", ()) or () if isinstance(c, CarrierReuse)]
    paths = list((getattr(plan, "carrier_paths", None) or {}).values())
    if not getattr(plan, "carriers", ()):
        return [], []
    from . import store
    made = [p for p in paths if not any(store.same_path(p, k) for k in kept)]
    return [_stem(p) for p in made], [_stem(p) for p in kept]


def _ready_build(assessment, plan, folder: str, superseded: Sequence[str] = ()) -> Tuple[str, bool]:
    """*Ready: Build makes 4 parts, Reducer_12to1_Layout and Reducer_12to1.SLDASM in C:\\Parts\\Reducer_12to1.*,
    reusing what is built; whether its gears are mated to turn (:func:`motion_ready_line`); why the revision is not
    0; why a new part takes another name (:func:`_occupied`); and, for a copied workbook, whose the files beside it
    are (:func:`_copy_sentence`)."""
    where = short_path((plan.folder if plan is not None and plan.folder else folder), 48)
    if plan is None:
        return (f"Ready: Build makes {_plural(len(assessment.parts.jobs), 'part')}, the layout part and the "
                f"assembly in {where}."), True
    made = [_plural(len(plan.build), "part")] if plan.build else []
    reused = []
    if _layout_reused(plan):
        reused.append(_stem(plan.layout.path))
    elif plan.layout is not None:
        made.append(_stem(plan.layout_path))
    new_carriers, kept_carriers = _plan_carriers(plan)          # W7: the carrier part, made or reused
    made += new_carriers
    reused += kept_carriers
    if plan.assembly is not None:
        made.append(_file(plan.assembly_path))
    if plan.reuse:
        reused.append(_already(len(plan.reuse)))
    text = f"Ready: Build makes {_and(made)} in {where}" + (", reusing " + _and(reused) if reused else "") + "."
    turning = motion_ready_line(plan)          # W5: whether its gears turn, said before Build, next to the assembly
    if turning:
        text += " " + turning
    copied = bool(getattr(plan, "foreign_record", ""))
    if plan.revision_reason and not copied:
        text += " " + _sentence(plan.revision_reason)
    occupied = _occupied(plan, superseded=superseded)
    if occupied:
        text += " " + occupied
    if copied:
        text += " " + _copy_sentence(plan)
    return text, bool(made)


def _waiting_rows(parts) -> str:
    refused = parts.refused
    more = f" ({len(refused) - 1} more under Checks)" if len(refused) > 1 else ""
    return f"the layout and assembly are not built: {refused[0].message}{more}" if refused else ""


def _ready_parts(assessment, plan, folder: str, superseded: Sequence[str] = (), *,
                 turned: str = "") -> Tuple[str, bool]:
    """*Ready: Build parts makes 2 parts in …; the layout and assembly are not built: Gears!A6: …* (W2's
    batch, through the same reuse as Build, decision 9). ``turned`` (W6, D16): planning's refusal of a gearbox with
    a turned mesh while the probes have not settled it (``motion.turned_refusal``), said whole after the line."""
    where = short_path((plan.folder if plan is not None and plan.folder else folder), 48)
    new = len(plan.build) if plan is not None else len(assessment.parts.jobs)
    kept = len(plan.reuse) if plan is not None else 0
    waits = _waiting_rows(assessment.parts)
    after = f" {_sentence(turned)}" if turned else ""
    if not new:
        lead = (f"The {_plural(kept, 'part')} {'is' if kept == 1 else 'are'} built already, so Build parts has "
                "nothing to make")
        return (f"{lead}; {waits}" if waits else f"{lead}.") + after, True
    text = f"Ready: Build parts makes {_plural(new, 'part')} in {where}"
    if kept:
        text += f", reusing {_already(kept)}"
    text += (f"; {waits}" if waits else ".") + after
    occupied = _occupied(plan, superseded=superseded) if plan is not None else ""
    if occupied:
        text += " " + occupied
    if plan is not None and getattr(plan, "foreign_record", ""):
        text += " " + _copy_sentence(plan)
    return text, True


def _unsaved_line(paths: Sequence[str], update_puts_back: bool = False, in_error: Sequence[str] = ()) -> str:
    """The save asked for once, naming every document of the current revision Update changed and that is not
    saved: parts first, the assembly last, as Update changed them. Nothing here can know whether SolidWorks has
    them open still, so the sentence is true either way (second review N2): if SolidWorks closed them without
    saving, the changes are gone — and, where Update SolidWorks would carry the workbook again
    (``update_puts_back``), pressing it makes them again. A job that finds them closed takes the mark off."""
    paths = sorted(paths, key=lambda p: str(p).lower().endswith(".sldasm"))
    one = len(paths) == 1
    them = _them(len(paths))
    if in_error:
        # The W9c runs review's should-fix, kept on the record (``LinkRecord.unsaved_in_error``): the Update that left
        # them stopped on a part in error, so the footer says what that press said, never to save.
        from .store import same_path
        failed = [p for p in paths if any(same_path(p, e) for e in in_error)] or list(in_error)
        return (f"{_and(_stem(p) for p in paths)} {'has' if one else 'have'} changes from Update SolidWorks that are "
                f"not saved, and {_and(_stem(p) for p in failed)} {'was' if len(failed) == 1 else 'were'} left in "
                f"error when it stopped: close {'it' if one else 'them all'} in SolidWorks without saving (the "
                f"{'file' if one else 'files'} on disk {'is' if one else 'are'} as before that Update), then press "
                "Update SolidWorks again.")
    then = (" press Update SolidWorks to make them again." if update_puts_back else " those changes are gone.")
    return (f"{_and(_stem(p) for p in paths)} {'has' if one else 'have'} changes from Update SolidWorks that are not "
            f"saved: save {them} in SolidWorks to keep {them}. If SolidWorks closed {them} without saving,{then}")


def workbook_footer(assessment, *, record=None, record_problem: str = "", plan=None, update=None,
                    error: str = "", folder: str = "", folder_exists: bool = True, building: bool = False,
                    updating: bool = False, progress=None, note=None, results_due: bool = False,
                    digest: str = "", positions_per_configuration: Optional[bool] = None) -> Footer:
    """The footer for every state of the window (design/UI-DESIGN.md §9's table): its sentence, colour, buttons.

    ``assessment`` is the last good read's ``workbook.assess.Assessment``
    (assessed with ``provisional=`` the window's recalc, and its chosen
    fixes), or None when there is none. ``record`` is the planning read of the
    link record (``store.read_link_record``) when it is this workbook's (None
    for a copy's: ``plan.foreign_record`` says so), ``record_problem`` the
    sentence if that read raised (a newer or broken record). ``plan`` is the
    ``workbook.gearbox.GearboxPlan`` the build button would run (None while
    the gate refuses) and ``update`` the ``workbook.update.UpdatePlan`` from
    ``classify`` (None with nothing on record). ``building``/``updating``: a
    worker job is running, and ``progress`` its last ``swbuild.Step``.
    ``note``: the window's last sentence of its own, a :class:`Note` (a plain
    ``(text, ok)`` is a job's). Order of the gate: the window's own state
    (error, a job running, the folder missing on disk, the record problem),
    then ``assessment.lay_out_refusal()`` — falling back to Build parts when
    only ``parts.refused`` holds the layout back and ``build_refusal()``
    passes — then ``plan.refusal``.

    The build button's action follows the record and the read, not the
    moment: Build again… once an assembly is on record, else Build parts
    while rows a later phase builds are there, else Build. A newer record
    (its sentence ends ``store.LINK_WAITS``) holds both buttons back; a
    broken one only Update. Update SolidWorks is gated as Build is, but never
    on the output folder, since it writes nothing there; it stays enabled
    when the record says nothing differs (the worker compares live), and
    when the change needs a new revision once an assembly is built (the press
    asks, then builds again) — but not when that build cannot go, nor before
    an assembly is built, when Build itself makes what is needed.

    Every sentence is decided from fields, never from another sentence's
    words: a greyed button always has its reason on screen, no sentence offers
    a greyed button, the save of what Update left unsaved is asked for once
    (:func:`_unsaved_line`), and the parts a build makes new rather than reuse
    are said from ``plan.made_new`` (:func:`_occupied`, :func:`_held_back`).
    The note joins as its kind says (:class:`Note`).

    W5 (Agent C; W5-INTERFACES.md): ``digest`` is the sha256 of the read the
    window shows (``Reading.digest``; the window passes it, Agent D). While
    the record's gearbox has no assembly and its ``mate_problems`` came from
    this same read (``mate_problems_digest == digest``), Build is not
    enabled and the sentence says SolidWorks refused a mate, naming it, and
    that changing the workbook makes Build available again (W5-DECISIONS, answer 1:
    the footer never invites a retry of an unchanged workbook). ``""``, as
    every W4 caller passes, never matches.

    W8 (W8-INTERFACES §9.12): ``positions_per_configuration`` is the running SolidWorks' answer as the last job's
    result carried it (None after a restart: neither claim is made), for the record line of a gearbox with modes,
    which also reads the workbook's Modes rows now (``assessment.spec.modes``) to say a reorder.
    """
    from .store import GEARBOX_STATIC, LINK_WAITS
    a = assessment
    note = _as_note(note)
    gearbox = getattr(record, "gearbox", None)
    has_assembly = bool(gearbox is not None and gearbox.assembly)
    on_record = record is not None and bool(record.parts or gearbox is not None)
    # W6 (D16): a turned mesh the probes have not settled holds the layout back as rows a later phase builds do,
    # and Build parts goes ahead (``assess.Assessment.turned_refusal``, the one home of that test).
    turned = a.turned_refusal() if a is not None else ""
    later = bool(a is not None and (a.parts.refused or turned))
    action = BUILD_AGAIN if has_assembly else (BUILD_PARTS if later else BUILD)
    newer = bool(record_problem) and record_problem.rstrip().endswith(LINK_WAITS)
    # W5: SolidWorks refused or flagged a mate of the last assembly, built from this very read: the same press would
    # make the same mates, so Build waits for a changed workbook (W5-DECISIONS answer 1; ruling b on 2f82a0e).
    refused_here = bool(gearbox is not None and not gearbox.assembly
                        and any(str(p).strip() for p in gearbox.mate_problems)
                        and gearbox.mate_problems_digest and gearbox.mate_problems_digest == digest)
    refused_shown = False
    record_words = dict(positions_per_configuration=positions_per_configuration,
                        modes=tuple(m.name for m in getattr(getattr(a, "spec", None), "modes", ()) or ()))

    def footer(text: str, ok: bool, build: bool = False, update_on: bool = False) -> Footer:
        return Footer(text, ok, action, BUILD_LABELS[action], build, action != BUILD_AGAIN, on_record,
                      update_on and on_record, has_assembly)

    if building or updating:
        return footer(progress_text(progress, updating=updating), True)
    if error:
        return footer(error, False)
    if a is None:
        return footer(record_problem, not record_problem)
    if note is not None and not note.ok and a.chosen:
        return footer(note.text, False)          # a refused Export must show, even with a fix still chosen
    if a.chosen:
        n = len(a.chosen)
        waits = "Build and Update SolidWorks wait" if on_record else "Build waits"
        return footer(f"{_plural(n, 'fix', 'fixes')} chosen: Export writes {'it' if n == 1 else 'them'} into the "
                      f"workbook, and {waits} for that, so the workbook and SolidWorks agree.", True)
    if a.provisional:
        lead = f"{note.text} " if note is not None else ""
        return footer(lead + (RECALC_WAIT_UPDATE if on_record else RECALC_WAIT), True)

    due = RESULTS_DUE if results_due else ""
    if newer:
        text = _after_note(note, record_problem) if note is not None else record_problem
        return footer(text + due, False)

    where = folder or a.folder
    missing_folder = (f"The output folder {short_path(where, 48)} does not exist; make it, or change it on the Box "
                      "sheet.")
    gate = a.build_refusal() if action == BUILD_PARTS else a.lay_out_refusal()
    build_block = gate or ("" if folder_exists else missing_folder) or (plan.refusal if plan is not None else "")
    loose = _without_folder(a)
    update_gate = loose.lay_out_refusal() if gearbox is not None else loose.build_refusal()
    update_on = on_record and not update_gate and update is not None and not update.refusal
    if update is not None:
        unsaved = list(update.unsaved)
    elif record is not None:
        unsaved = list(record.current_marks(record.unsaved))
    else:
        unsaved = []
    superseded = [p.path for p in record.parts] if record is not None else []

    held = ""              # why Build again… or Update SolidWorks is greyed, when the sentence does not say it
    folded = ""            # W5: the static record's turning revision, said inside Update's own offer
    subject = ""           # who makes the plan's parts new, when this state offers the plan's build
    if action == BUILD_AGAIN:
        build_on = not build_block
        if update_gate:
            text, ok = update_gate, False
        elif update is None:
            text, ok, held = f"{_file(gearbox.assembly)} is built from this workbook.", True, build_block
        elif update.refusal:
            text, ok, held = update.refusal, False, build_block
        elif update.needs_new_revision and build_block:
            # Update would ask, then build again, and that build cannot go: say why, and offer neither.
            name = f", {plan.name}," if plan is not None and plan.name else ""
            text, ok, update_on = (f"{_cannot_carry(update)} The new revision it needs{name} cannot be built yet: "
                                   f"{build_block}"), False, False
        elif update.needs_new_revision:
            # W5 (D5): a static gearbox whose new revision turns is told so in the one offer (W4 review S4.1).
            if (gearbox.kind == GEARBOX_STATIC and plan is not None and not plan.refusal
                    and getattr(plan, "motion", None) is not None):
                folded = ("; it was built static, and the new revision's gears turn" if gearbox.static_reason else
                          "; it was built static, before gears could be mated to turn, and the new revision's gears "
                          "turn")
            text = _again_sentence(update, plan.name if plan is not None else "", turning=folded)
            ok = not update.missing
            occupied = _occupied(plan, superseded=superseded) if plan is not None else ""
            if occupied:
                text += " " + occupied
            subject = "the new revision"
        else:
            text, ok, held = update_summary(update), True, build_block
        if ok and not folded:
            # W5: what kind of assembly is on record; W4's static one is offered a turning revision only when Build
            # again… is on and its plan turns (D5: never forced), so a W4 sentence otherwise stays as it was.
            line = motion_record_line(record, digest, offer=bool(
                build_on and plan is not None and not plan.refusal and getattr(plan, "motion", None) is not None),
                **record_words)
            if line:
                text += " " + line
    else:
        if build_block:
            text, ok, build_on = build_block, False, False
        elif refused_here and action == BUILD:
            text, ok, build_on, refused_shown = motion_record_line(record, digest, **record_words), False, False, True
        elif action == BUILD_PARTS:
            text, ok = _ready_parts(a, plan, where, superseded, turned=turned)
            build_on = plan is None or bool(plan.build)
            subject = "Build parts"
        else:
            text, ok = _ready_build(a, plan, where, superseded)
            build_on = ok
            subject = "Build"
            if ok and gearbox is not None and not gearbox.assembly:
                # W5: a refusal on record, from an earlier read
                line = motion_record_line(record, digest, offer=build_on, **record_words)
                if line:
                    text += " " + line
        if on_record and update is not None and not update.refusal and update.needs_new_revision:
            # Nothing is assembled yet (a record from Build parts): Build makes what is needed, and Update would
            # otherwise offer a build-again of an assembly that was never built (W4 review S4.4).
            update_on = False
            held = f"{_cannot_carry(update)} Update SolidWorks waits until Build has made what that needs."
        elif on_record and update is not None and update.refusal:
            held = update.refusal              # Update shown but greyed: its reason, whatever shows (S4.5)
        if refused_shown and on_record:
            held = UPDATE_WAITS_FOR_ASSEMBLY   # not the record's "Build carries on with it": Build waits too

    if record_problem:                            # a broken record: Build goes ahead and sets it aside
        text, ok = f"{text} {record_problem}", False
    puts_back = bool(update_on and update is not None and not update.needs_new_revision)
    if note is None or note.kind == NOTE_ANSWER:
        # The state's own lines — the save asked for, the parts made new — follow an answer too (after "No" to
        # Build again? the reason it answered is kept, and these with it).
        if puts_back:
            # W9a (K4): what this press would do with the user's work the record holds, with the time it was read.
            from .workbook.update import in_place_ahead, user_work_ahead
            ahead = user_work_ahead(update, record, digest)
            line, line_ok = user_work_line(ahead)
            # W9c (K4): what would stop an in-place change, foreseen (an unmeasured step, the user's work on a gear to
            # be taken out). When it would, it is said in place of W9a's prediction of what the press does with the
            # user's work (a press that changes nothing does nothing with it). A refusal on record is said instead of
            # foreseeing the same again (a new part's file on disk, never part of a refusal recorded, is still said).
            recorded = ahead is not None and bool(ahead.refused)
            stop, stop_ok = in_place_line(() if recorded else in_place_ahead(update, record), record, known=line,
                                          on_disk=getattr(update, "new_parts_on_disk", ()))
            if stop and not stop_ok and not recorded:
                line, line_ok = "", True
            # Never "will" for a press the same footer says would change nothing (the gates' line, or W9a's foresight
            # of the user's work, red: the review's should-fix 2).
            if (stop and not stop_ok) or (line and not line_ok and "would stop" in line):
                text = text.replace("Update SolidWorks will ", "Update SolidWorks would ", 1)
            for said, said_ok in ((line, line_ok), (stop, stop_ok)):
                if said:
                    text, ok = f"{text} {said}", ok and said_ok
        if unsaved:
            text += " " + _unsaved_line(unsaved, puts_back, getattr(record, "unsaved_in_error", ()) or ())
        carried = carry_footer_line(record)       # W9d (§9.4): the carry a Build again… left unsaved, until saved
        if carried:
            text += " " + carried
        if subject and plan is not None and not plan.refusal:
            back = _held_back(plan, subject, after_unsaved_line=bool(unsaved))
            if back:
                text += " " + back
    if note is not None:
        carried = carry_footer_line(record)
        if carried and note.kind == NOTE_JOB and _asks_carry_save(note.text, record):
            carried = ""                       # the build's own sentence asks the save already (W9a's rule 3)
        if refused_shown and note.kind == NOTE_JOB:
            text, ok = note.text, note.ok      # the refusing build's own sentence already says all of it
        elif note.kind == NOTE_ANSWER:
            text, ok = f"{note.text} {text}", ok and note.ok
        elif ok:
            text, ok = note.text + _left_for_later(a.parts), note.ok
        else:
            text = _after_note(note, text)
        if carried and note.kind == NOTE_JOB:
            # §9.4 (the demonstration's record check): while the carry stands unsaved the footer says so after a job's
            # own sentence too, unless that sentence asks the save itself.
            text += " " + carried
    if held:
        text += " " + held
    return footer(text + due, ok, build_on, update_on)


def _asks_carry_save(text: str, record) -> bool:
    """Whether a job's sentence already asks the carry's save (``carried_status``' last sentence)."""
    box = getattr(record, "gearbox", None)
    name = _stem(box.assembly) if box is not None and box.assembly else ""
    return bool(name) and f"Save {name} in SolidWorks to keep what was carried." in text


# -- W4: what the Workbook window itself says around a job (the window wiring) ----------------------------------
#
# The footer's sentence is :func:`workbook_footer`'s and a finished job's is :func:`gearbox_status` or
# :func:`gearbox_update_status`; these are the few things only the window knows to say: a job that could not
# start, a record it could not write, the question's title and its "No", and the header's word on the record.

BUILD_AGAIN_TITLE = "Build again?"
NOTHING_CHANGED = "Nothing was changed in SolidWorks."
ASKED_TOO_LATE = ("The workbook changed while the question was open, so nothing was built; press Build again… once "
                  "more if it still applies.")


def _after_note(note: Note, text: str) -> str:
    """A note, then a state that is not fine: *Built 4 parts. Since then: Fix the workbook …* after a job, which
    marks a moment the workbook may have moved on from; plainly joined after anything else, which marks none —
    *Exported 1 cell and the Results sheet. Fix the workbook before building: …* — since what follows was already
    so."""
    if note.kind != NOTE_JOB:
        return f"{note.text} {text}"
    return f"{note.text} Since then: {text}"


def workbook_built_tag(record, digest: str) -> str:
    """The header's word on the record beside the workbook: `` · built from this version`` or `` · changed since
    it was built`` once a layout part or assembly is on record (``record.digest`` is the read SolidWorks was last
    built or updated from), `` · parts built from this version`` / `` · changed since its parts were built`` for
    W2's parts alone, and ``""`` with nothing on record. While documents of the current revision Update changed
    are not saved (``record.unsaved``) this version is in SolidWorks only: `` · updated from this version, not
    yet saved`` (W4 review S4.7); an earlier revision's are not counted (second review N2). While a document of
    the current revision is marked mismatched (a check found it not holding what the record says, or a job found
    Update's changes in it lost) it is `` · SolidWorks no longer holds all of this version``. After a build whose
    assembly SolidWorks refused a mate of (W5: no assembly, ``mate_problems`` on record) it is compared with the
    read the refusal came from: `` · its assembly was refused for this version``, `` · changed since its assembly
    was refused``, or ``""`` when either read is not known."""
    if record is None or not (record.parts or record.gearbox is not None):
        return ""
    same = bool(digest) and record.digest == digest
    unsaved = bool(record.current_marks(record.unsaved))
    if same and record.current_marks(record.mismatched):
        return " · SolidWorks no longer holds all of this version"
    if record.gearbox is None:
        if same:
            return (" · parts updated from this version, not yet saved" if unsaved
                    else " · parts built from this version")
        return " · changed since its parts were built"
    box = record.gearbox
    if not box.assembly and any(str(p).strip() for p in box.mate_problems):
        # W5: the last build's assembly was refused, so no build is on record to have changed since; the read the
        # refusal came from is ``mate_problems_digest``, and with neither read known nothing is claimed.
        if not (digest and box.mate_problems_digest):
            return ""
        if box.mate_problems_digest == digest:
            return " · its assembly was refused for this version"
        return " · changed since its assembly was refused"
    if same:
        return " · updated from this version, not yet saved" if unsaved else " · built from this version"
    return " · changed since it was built"


def job_unreachable(reason: str, updating: bool = False) -> str:
    """*SolidWorks cannot be reached from here, so nothing was built.* and why (``swcom.unavailable_reason``)."""
    done = "updated" if updating else "built"
    return f"SolidWorks cannot be reached from here, so nothing was {done}. {reason}".strip()


def unowned_job_busy(updating: bool = False) -> str:
    """A job whose window was closed anyway (``close_anyway_question``) is still running in SolidWorks: no window
    will collect it, and a new build or update must not overtake it (third W4 review)."""
    then = "press Update SolidWorks" if updating else "build"
    return (f"A job from a Workbook window that was closed while SolidWorks had not answered is still running in "
            f"SolidWorks; {then} when it has finished.")


def strip_busy(updating: bool = False) -> str:
    """The strip has a build of its own in SolidWorks (they share one worker)."""
    then = "press Update SolidWorks" if updating else "build the workbook"
    return f"The strip is building in SolidWorks; {then} when it has finished."


def job_failed(error: BaseException, updating: bool = False) -> str:
    """A job the worker answered with a raise.

    Since the W4 review that is a refusal before anything was made or
    changed: ``build_gearbox`` and ``update_gearbox`` turn whatever goes wrong
    after their own checks into failures on the result they return. So it is
    one of those checks — the paths, a document of the same name open from
    another folder, the plans, a document to reuse or update that cannot be
    opened or read, and Update's check phase (a global, feature or component
    gone; new values that do not evaluate) — or the connection to SolidWorks
    failing before the job began. One thing short of a change is done first:
    when an Update's new values evaluate in one trig unit only, that
    document's units are measured, which leaves it marked modified in
    SolidWorks although no value in it changed. A live check that finds a
    document to reuse not holding what it should is not a raise any more
    (``GearboxResult.mismatched``).

    A SolidWorks refusal is said as it came; anything else is named. A
    document Update found not as it was built (``swbuild.NotAsBuilt``: a
    component, feature or global renamed or deleted in SolidWorks) gets the
    way on, since Update cannot put it back (W4 review S4.6)."""
    from .swbuild import NotAsBuilt
    from .swcom import SolidWorksError
    if isinstance(error, SolidWorksError):
        text = str(error)
        if updating and isinstance(error, NotAsBuilt):
            text = (f"{_sentence(text)} Update SolidWorks cannot put that back; Build again… builds the next revision "
                    "beside it, with an assembly of its own, and leaves this one as it is.")
        return text
    what = "Update SolidWorks stopped before it changed anything" if updating else \
        "The build stopped before it made anything"
    return f"{what} — {type(error).__name__}: {error}"


def planning_failed(error: BaseException) -> str:
    """Planning a build or an update raised, which it should never do: say so rather than offer the button."""
    return (f"What to build could not be worked out — {type(error).__name__}: {error}. Nothing is built or updated "
            "until it can be.")


def sidecar_unwritten(path: str, error: BaseException) -> str:
    """A part saved, but its ``.gear.json`` could not be written beside it."""
    return f"The part's record {_file(path)} could not be written beside it: {error}."


def record_unwritten(path: str, error: BaseException) -> str:
    """The ``.workbook.json`` could not be written (the disk refused): the files SolidWorks saved stay."""
    return (f"The record of what was built, {_file(path)}, could not be written: {error}. What SolidWorks saved "
            "stays on disk, and the next Build goes beside it rather than over it.")


FIX_SET_ASIDE = ("The workbook changed, so the fix you chose no longer applies as it was and was set aside; choose "
                 "again from Checks.")


def record_not_carried(why: str) -> str:
    """Locate…: the record beside the workbook's old place could not be carried to its new one."""
    return f"The record of what was built stays beside the workbook's old place: {_sentence(why)}"


def export_busy(updating: bool = False) -> str:
    """Why Export waits while a job runs (follows *Nothing was exported:*)."""
    if updating:
        return "Update SolidWorks is running; export when it has finished."
    return "a build is running in SolidWorks; export when it has finished."


def closes_when_done(updating: bool = False) -> str:
    """The window was closed while a job runs: it stays until what the job saved is on record."""
    job = "the update" if updating else "the build"
    return (f"This window closes once {job} has finished and what it saved is on record; it stays open if "
            "something needs saying.")


def collect_failed(error: BaseException, updating: bool = False) -> str:
    """A finished job whose answer the window could not take in."""
    what = "update" if updating else "build"
    return f"The {what} could not be collected — {type(error).__name__}: {error}"


def finish_failed(error: BaseException, updating: bool = False, journaled: bool = False,
                  changed: bool = True) -> str:
    """Working out what a finished job leaves on record raised (W4 review B1, the window's half), so nothing of the
    record was written. A build whose journal was written before it began (``journaled``, second review N4) still
    has it on record: the next Build reuses what SolidWorks saved, once checked. Update saves nothing: what it
    changed is in SolidWorks only, and not marked unsaved — unless it changed nothing (``changed`` False, third
    review), when nothing is said to be in SolidWorks."""
    lead = f"What the {'update changed' if updating else 'build saved'} could not all be put on record — " \
           f"{type(error).__name__}: {error}."
    if updating and not changed:
        return (f"What the update found could not all be put on record — {type(error).__name__}: {error}. It "
                "changed nothing in SolidWorks.")
    if updating:
        return f"{lead} Its changes are in SolidWorks, not saved: save them there to keep them."
    if journaled:
        return (f"{lead} What SolidWorks saved stays on disk, and the next Build finds it from the journal written "
                "before the build, checks it in SolidWorks and reuses what it can.")
    return f"{lead} What SolidWorks saved stays on disk, and the next Build goes beside it rather than over it."


def app_closes_when_done(count: int = 1, strip: bool = False) -> str:
    """The strip's window was closed while Workbook windows (``count``) or the strip itself (``strip``) have jobs in
    SolidWorks: the app stays until they have finished and been collected (the worker thread would die with it,
    and nothing would reach the record). Closing it again offers to quit anyway (:func:`quit_anyway_question`).

    Only a Workbook window stays open to show what its job said (``CloseGuard.check``); the strip is not waited
    on for that — once its job is collected the app quits, whatever it said — and the strip's job may be a build
    or an update of a part's values, so it is called a job, collected, not a build whose saved files are on record
    (third W4 review)."""
    said = []
    if count:
        jobs = "a workbook's job" if count == 1 else f"{count} workbooks' jobs"
        said.append(f"{jobs} in SolidWorks {'has' if count == 1 else 'have'} finished and "
                    f"what {'it' if count == 1 else 'they'} did is on record")
    if strip:
        said.append("the strip's job in SolidWorks has finished and the strip has collected it")
    text = "Gear Generator closes once " + ", and once ".join(said)
    if count:
        text += "; it stays open if a Workbook window has something to say"
    return text + "."


APP_CLOSES_AFTER_QUESTION = "Gear Generator closes once the question open in a Workbook window is answered."

QUIT_ANYWAY_TITLE = "Quit anyway?"
CLOSE_ANYWAY_TITLE = "Close anyway?"


def quit_anyway_question(workbook_build: bool = False) -> str:
    """Asked (default No) when the strip's window is closed a second time while a job in SolidWorks has not
    answered — SolidWorks may be held by a dialog, and nothing can stop a call it does not answer (second W4
    review N4.3). What it says is what holds: nothing those jobs save or change is put on record by this session
    (not only what they do from now: their finishes never run), and no file is overwritten (a build never
    overwrites one). ``workbook_build``: a workbook's build is among the jobs; its journal covers the files a
    build saves — written before it began unless the record could not be written, which is said as such — and
    never an update's changes (third review)."""
    text = ("SolidWorks has not answered yet: a job is still running there, perhaps held up by a dialog open in "
            "SolidWorks. Quit anyway? Nothing that job saves or changes is put on record by this session, and nothing "
            "will be overwritten.")
    if workbook_build:
        text += (" A workbook's build lists what it is about to make in that workbook's record before it begins, "
                 "unless the record cannot be written, so the workbook's next Build finds the files it saved, checks "
                 "them in SolidWorks and reuses what it can.")
    return text


def close_anyway_question(updating: bool = False, journaled: bool = False) -> str:
    """The Workbook window's own close, a second time while its job has not answered (second W4 review N4.3).
    Nothing the job saves or changes is put on record by this window — not only what it does from now: its finish
    never runs. The build's journal (``journaled``: written before it began) lets the next Build find what it
    saved; without one, the next Build goes beside those files. An update has no journal: what it changes is in
    SolidWorks only (third review)."""
    if updating:
        return ("SolidWorks has not answered yet: Update SolidWorks is still running there, perhaps held up by a "
                "dialog open in SolidWorks. Close this window anyway? Nothing the update changes is put on record by "
                "this window, so it will not ask for those documents to be saved, and nothing will be overwritten.")
    then = ("the build listed what it is about to make in the record before it began, so the next Build finds those "
            "files, checks them in SolidWorks and reuses what it can." if journaled else
            "what the build was about to make could not be listed in the record before it began, so the next Build "
            "goes beside the files it saves rather than over them.")
    return ("SolidWorks has not answered yet: the build is still running there, perhaps held up by a dialog open in "
            "SolidWorks. Close this window anyway? Nothing the build saves is put on record by this window, and "
            f"nothing will be overwritten: {then}")


MOVED_TITLE = "Moved, or a copy?"


def moved_question(workbook: str, other: str) -> str:
    """Asked once (default No) when the record beside a workbook was written for another that is not there any more
    (``store.UNSURE``, second W4 review N1c): moved or renamed — the record is this workbook's — or a copy of an
    original since deleted, renamed or gone offline, whose files are not this workbook's. Yes is kept in the record;
    No holds for the session, and is asked again in a new one until this workbook has built its own gearbox (third
    review). A drive not connected now is named, and No is the safe answer then."""
    return (f"The record of what was built beside this workbook was written for {short_path(other, 60)}, which is not "
            "there any more. Was this workbook moved or renamed from it? Yes: the record is this workbook's, and "
            "Update SolidWorks and Build carry on from what it lists; the answer is kept in the record. No: this "
            "workbook is a copy, so Build makes its own gearbox beside those files, sharing and overwriting nothing; "
            "until it has, you are asked again the next time Gear Generator opens this workbook. If that workbook "
            "may be on a drive that is not connected now, answer No: nothing is shared or overwritten.")


def answer_not_kept(error: BaseException) -> str:
    """The move-or-copy answer could not be written into the record: this session keeps it."""
    return (f"Your answer holds until Gear Generator closes, but it could not be kept in the record of what was "
            f"built: {error}.")


APP_STAYED_OPEN = ("Gear Generator stayed open: a workbook's job has something to say in its window. Close this window "
                   "again to quit.")


# -- W5: the gearbox that turns (docs/notes-workbook/W5-PLAN.md §1.8, as W5-INTERFACES.md amends it) ---------------
#
# Interfaces pinned in the W5 interface commit, written by package C and called from the functions above that
# already exist (``_ready_build``, ``gearbox_status``, ``workbook_footer``, ``build_again_question``,
# ``update_summary``, ``gearbox_update_status``), whose signatures stay as they are (``workbook_footer`` gained
# ``digest``; ``build_again_question`` and ``motion_record_line`` keyword-only ``record``/``offer``). What a static
# gearbox of W4's is told stays word for word as it was, except the offer of a turning revision (D5).
# Every sentence is decided from fields, never from another sentence's words, and is true in every state; a mate
# problem (``BuildResult.mate_problems``, ``GearboxRecord.mate_problems``) is a whole sentence of the worker's and is
# shown as one, never lower-cased or cut into another sentence. There is no static fallback, so no sentence about one
# (W5-DECISIONS, answer 1).


def _gears_alone(motion) -> List[str]:
    """The gears of a turning plan that are mated to their shaft but turn apart from every train: the anchor of a
    shaft in no train, then the gears locked to it (``MotionPlan.anchors``, ``trains``, LOCK mates)."""
    from .store import CARRIER_ID_SUFFIX
    in_trains = {shaft for train in motion.trains for shaft in train}
    on_carrier = {m.shaft for m in motion.mates if getattr(m, "on", "") and m.shaft}     # W7: planet copies' axes
    out: List[str] = []
    for shaft, anchor in motion.anchors.items():
        if shaft in in_trains or not anchor or shaft in on_carrier or anchor.endswith(CARRIER_ID_SUFFIX):
            continue
        out.append(anchor)
        out.extend(m.gears[1] for m in motion.mates
                   if m.kind == "lock" and len(m.gears) == 2 and m.gears[0] == anchor and m.gears[1])
    return out


def _alone_sentence(gears: Sequence[str], trains: int = 1) -> str:
    """*G7 turns apart from the train: it meshes no other gear.* (review M11: such a gear does not follow the drag;
    *apart from the train* stays true of a gear locked to it, which turns with it); *… the trains* for two or more."""
    if not gears:
        return ""
    one = len(gears) == 1
    return (f"{_and(gears)} {'turns' if one else 'turn'} apart from the train{'' if trains <= 1 else 's'}: "
            f"{'it meshes' if one else 'they mesh'} no other gear.")


def _turning_subject(motion) -> str:
    """``Its gears``, or ``Its turning gears`` when some are left fixed (said after it)."""
    return "Its turning gears" if _fixed_gears(motion) else "Its gears"


def _train_count(motion) -> int:
    """How many trains a turning plan has: ``trains``, else one per ``drag`` gear."""
    return len(motion.trains) or len([g for g in motion.drag if g])


def _fixed_sentence(fixed: Sequence[str]) -> str:
    """*G9 stays fixed where it is placed: its shaft does not turn.* (W5-PLAN D9 and review M9: on a fixed shaft,
    or on one a fixed shaft holds still; either way its shaft does not turn)."""
    fixed = [g for g in fixed if g]
    if not fixed:
        return ""
    one = len(fixed) == 1
    return (f"{_and(fixed)} {'stays' if one else 'stay'} fixed where {'it is' if one else 'they are'} placed: "
            f"{'its shaft does' if one else 'their shafts do'} not turn.")


def _joined(*sentences: str) -> str:
    return " ".join(s for s in sentences if s)


def _mate_problems(problems: Sequence[str]) -> str:
    """The worker's mate problems, each its own whole sentence as it came (never lower-cased or cut into another)."""
    return " ".join(mode_problem(p) for p in problems if str(p).strip())


def _mates_lead(problems: Sequence[str]) -> str:
    """``a problem`` / ``2 problems`` with the mates."""
    count = len([p for p in problems if str(p).strip()])
    return "a problem" if count == 1 else f"{count} problems"


SAME_MATES = "the same workbook would make the same mates"
UPDATE_WAITS_FOR_ASSEMBLY = "Update SolidWorks waits until Build has made the assembly."


def _fixed_gears(motion) -> List[str]:
    """``MotionPlan.fixed`` less a held carrier, which :func:`_carrier_sentences` says (W7)."""
    from .store import CARRIER_ID_SUFFIX
    return [g for g in motion.fixed if g and not g.endswith(CARRIER_ID_SUFFIX)]


def _planets_phrase(planets: Sequence[str]) -> Tuple[str, bool]:
    """(*the 3 copies of Planet* / *Planet* / *Planet and PlanetB*, whether it is plural)."""
    counts = _copy_counts(planets)
    names, rows = [], set()
    for name in planets:
        row, k = _copy_parts(name)
        if k and counts.get(row, 0) > 1:
            if row not in rows:
                names.append(f"the {counts[row]} copies of {row}")
                rows.add(row)
        else:
            names.append(name)
    plural = len(names) > 1 or any(counts.get(_copy_parts(n)[0], 0) > 1 for n in planets)
    return _and(names), plural


def _carrier_sentences(plan, built: bool = False) -> str:
    """What a planetary stage's carrier is (W7-PLAN §2.12), from a ``GearboxPlan``'s ``motion`` and carriers, once
    per carrier. Before Build: *C is built as a carrier of axes and planes only, turning with the 3 copies of Planet
    on it.*; a held carrier *C is built as axes and planes only, held fixed; the 3 copies of Planet turn on it.*
    After Build: *The 3 copies of Planet turn on C, and Planetary_4to1_C_Carrier holds C's axes and planes only: a
    plate and pins are yours to add.* (*…turn on C, which is held fixed, and …*). The copies are said once, never
    one by one; the held ring is said by :func:`_fixed_sentence`, the meshes left unmated not at all (J17)."""
    from .store import CARRIER_ID_SUFFIX
    motion = getattr(plan, "motion", None)
    if motion is None:
        return ""
    out = []
    for shaft, path in _carrier_parts(plan):
        cid = f"{shaft}{CARRIER_ID_SUFFIX}"
        planets = [m.gears[0] for m in motion.mates if m.kind == "axis" and getattr(m, "on", "") == cid and m.gears]
        if not planets:
            continue
        what, many = _planets_phrase(planets)
        held = cid in motion.fixed and cid not in getattr(motion, "carriers", ())
        if not built:
            out.append(f"{shaft} is built as axes and planes only, held fixed; {what} turn{'' if many else 's'} on it."
                       if held else
                       f"{shaft} is built as a carrier of axes and planes only, turning with {what} on it.")
            continue
        part = (f"{_stem(path)} holds {shaft}'s axes and planes only: a plate and pins are yours to add" if path
                else f"{shaft} is axes and planes only: a plate and pins are yours to add")
        where = f"{shaft}, which is held fixed," if held else f"{shaft},"
        out.append(f"{what[:1].upper()}{what[1:]} turn{'' if many else 's'} on {where} and {part}.")
    return " ".join(out)


def drag_phrase(drag: Sequence[str]) -> str:
    """The gear(s) to drag, from ``MotionPlan.drag`` / ``GearboxRecord.drag`` (one per train): *drag G1 in
    SolidWorks and the rest of its train follow* for one train (review M11: "of its train", since a lone gear or a
    fixed one does not follow), *drag G1 in SolidWorks to turn one train and G5 to turn the other* for two, *drag
    G1, G5 and G9 in SolidWorks, one for each train* for three or more; ``""`` for none."""
    drag = [str(g) for g in drag if str(g)]
    if not drag:
        return ""
    if len(drag) == 1:
        return f"drag {drag[0]} in SolidWorks and the rest of its train follow"
    if len(drag) == 2:
        return f"drag {drag[0]} in SolidWorks to turn one train and {drag[1]} to turn the other"
    return f"drag {_and(drag)} in SolidWorks, one for each train"


def motion_ready_line(plan) -> str:
    """Said before Build (``_ready_build``, right after its first sentence), from a ``workbook.gearbox.GearboxPlan``.

    With ``plan.motion``: *Its gears are mated to their shafts and to each
    other, so they turn together in SolidWorks.*; two or more trains, *… so
    each train turns together …*; where a shaft meshes nothing, *… and, where
    they mesh, to each other, so those that mesh turn together …* and which
    gears turn apart from the train; with no train, *Its gears are each mated
    to their shaft, free to turn in SolidWorks.*; *Its turning gears* when
    some are left fixed, and those (:func:`_fixed_sentence`). With
    ``plan.static_reason`` (a W5 finding missing: the static build is kept
    and said here, as ruled on review of 2f82a0e): *Its gears are placed
    meshed and fixed, not mated to turn.* followed by ``static_reason``, the
    planning's own whole sentence, as it came. ``""`` for a parts-only or refused plan, and
    for W4's static plan, which says nothing new.
    """
    if plan is None or plan.assembly is None or plan.refusal:
        return ""
    motion = getattr(plan, "motion", None)
    if motion is None:
        reason = getattr(plan, "static_reason", "")
        return f"Its gears are placed meshed and fixed, not mated to turn. {_sentence(reason)}" if reason else ""
    alone = _gears_alone(motion)
    trains = _train_count(motion)
    who = _turning_subject(motion)
    where = ", where they mesh," if alone else ""
    if getattr(motion, "modes", ()):
        # W8: what turns together is each mode's, said by mode (modes_ready_line), never one train for all.
        return _joined(f"{who} are mated to their shafts and, as each mode engages them, to each other, so they turn "
                       "together in SolidWorks.", modes_ready_line(plan), _carrier_sentences(plan),
                       _fixed_sentence(_fixed_gears(motion)))
    if not motion.anchors:
        text = ""
    elif not trains:
        text = f"{who} are each mated to their shaft, free to turn in SolidWorks."
    elif trains == 1:
        together = "those that mesh turn together" if alone else "they turn together"
        text = f"{who} are mated to their shafts and{where} to each other, so {together} in SolidWorks."
    else:
        text = f"{who} are mated to their shafts and{where} to each other, so each train turns together in SolidWorks."
    return _joined(text, _alone_sentence(alone, trains) if trains else "", _carrier_sentences(plan),
                   _fixed_sentence(_fixed_gears(motion)), modes_ready_line(plan))


def motion_done_line(plan, result) -> str:
    """After a build whose assembly saved (``swbuild.GearboxResult.kind``).

    For ``motion.MOTION``: *Its gears are mated to turn together, and
    SolidWorks reports no mate in error: drag G1 in SolidWorks and the rest
    of its train follow.*; two or more trains, *Its gears are mated to turn
    in 2 trains, …* with :func:`drag_phrase`; where a shaft meshes nothing,
    *… mated to their shafts and, where they mesh, to each other; SolidWorks
    reports …*; no train, *Its gears are each mated to their shaft, free to
    turn, and SolidWorks reports no mate in error.*; then the gears that turn
    apart from the train and those left fixed (*Its turning gears* then). It
    claims only what the mate check read (W5-PLAN D3: the app does not drive
    the train). For ``motion.STATIC`` with ``plan.static_reason``, that they
    are placed fixed and why. ``""`` otherwise: W4's static build, and a
    result whose ``kind`` was not filled in, say nothing new.
    """
    from .store import GEARBOX_MOTION, GEARBOX_STATIC
    kind = getattr(result, "kind", "")
    if kind == GEARBOX_STATIC:
        reason = getattr(plan, "static_reason", "") if plan is not None else ""
        return f"Its gears are placed meshed and fixed, not mated to turn. {_sentence(reason)}" if reason else ""
    if kind != GEARBOX_MOTION:
        return ""
    motion = getattr(plan, "motion", None) if plan is not None else None
    if motion is None:
        return "Its gears are mated to turn, and SolidWorks reports no mate in error."
    if getattr(motion, "modes", ()):
        return modes_done_line(plan, result)              # W8: a configuration per mode
    drag = [g for g in motion.drag if g]
    alone = _gears_alone(motion)
    trains = _train_count(motion)
    who = _turning_subject(motion)
    tail = f": {drag_phrase(drag)}." if drag else "."
    if not motion.anchors:
        text = ""
    elif not trains:
        text = f"{who} are each mated to their shaft, free to turn, and SolidWorks reports no mate in error."
    elif alone:
        text = (f"{who} are mated to their shafts and, where they mesh, to each other; SolidWorks reports no mate in "
                f"error{tail}")
    elif trains == 1:
        text = f"{who} are mated to turn together, and SolidWorks reports no mate in error{tail}"
    else:
        text = f"{who} are mated to turn in {trains} trains, and SolidWorks reports no mate in error{tail}"
    return _joined(text, _alone_sentence(alone, trains) if trains else "", _carrier_sentences(plan, built=True),
                   _fixed_sentence(_fixed_gears(motion)))


def mate_refused_status(plan, result, again: bool = False) -> Tuple[str, bool]:
    """A build whose assembly SolidWorks refused or flagged a mate of (``result.assembly.mate_problems``; the
    assembly not saved and nothing saved in its place: W5-DECISIONS, answer 1).

    *Built 4 parts and Reducer_12to1_Layout; no assembly was saved, because
    SolidWorks found a problem with its mates. The mate G3 locked to G2
    over-defines the assembly. The parts and the layout part are kept. The
    assembly is left open in SolidWorks as Assem1, not saved; its parts are
    the saved ones. Build is available again once the workbook changes: the
    same workbook would make the same mates.* Each mate problem is the
    worker's own sentence, whole. The open document is named only when there
    is one (``result.assembly.document``). Never an invitation to press again
    on the same workbook: the footer keeps Build greyed for this read
    (:func:`workbook_footer`'s ``digest``). ``ok`` is False. ``again`` as
    :func:`gearbox_status`'s.
    """
    assembly = result.assembly
    layout = result.layout
    layout_on = bool(result.layout_reused) or (layout is not None and layout.ok and bool(layout.saved))
    button = "Build again…" if again and not layout_on else "Build"
    made = [r for r in result.parts.built if r.ok and r.saved]
    made_names = [_plural(len(made), "part")] if made else []
    layout_name = _stem(layout.saved) if layout is not None and layout.saved else ""
    reused_parts = len(plan.reuse) if plan is not None else 0
    reused_layout = _stem(result.layout_reused) if result.layout_reused else ""
    carriers = [_stem(c.saved) for c in getattr(result, "carriers", ()) or () if c.ok and c.saved]
    carriers_reused = [_stem(p) for p in getattr(result, "carriers_reused", ()) or ()]
    done = _done_phrase(made_names + ([layout_name] if layout_name else []) + carriers,
                        ([reused_layout] if reused_layout else []) + carriers_reused
                        + ([_already(reused_parts)] if reused_parts else []))
    problems = list(assembly.mate_problems)
    what = "its mates or its modes" if getattr(plan, "modes_plan", None) is not None else "its mates"
    because = f"no assembly was saved, because SolidWorks found {_mates_lead(problems)} with {what}."
    lead = f"{done}; {because}" if done else because[:1].upper() + because[1:]
    kept = (("The parts, the layout part and the carrier part are kept." if carriers or carriers_reused
             else "The parts and the layout part are kept.") if done else "")
    left = (f"The assembly is left open in SolidWorks as {assembly.document}, not saved; its parts are the saved ones."
            if assembly.document else "")
    then = f"{button} is available again once the workbook changes: {SAME_MATES}."
    return _joined(lead, _mate_problems(problems), kept, left, then), False


def motion_record_line(record, digest: str = "", *, offer: bool = True,
                       positions_per_configuration: Optional[bool] = None, modes: Sequence[str] = ()) -> str:
    """The footer's line on a gearbox on record (``store.LinkRecord``), appended in the Build again… states whose
    sentence is not an error, and in Build's state after a refusal.

    ``kind`` ``motion``: *It was built with its gears mated to turn: drag G1
    in SolidWorks and the rest of its train follow.* (:func:`drag_phrase`:
    *… to turn one train and G5 to turn the other* for two; review M11).
    ``static`` with no ``static_reason`` (W4's, D5): *It was built static,
    before gears could be mated to turn: Build again… makes a new revision
    whose gears turn.* — only when ``offer`` (Build again… is on and its plan
    turns), else ``""``, so a W4 sentence stays as it was. ``static`` with a
    ``static_reason``: *It was built static.* and that whole sentence, and when
    ``offer``, *That is settled now, so Build again… makes a new revision
    whose gears turn.* No assembly and ``mate_problems`` (a refused build):
    *Reducer_12to1.SLDASM was not saved, because SolidWorks found a problem
    with its mates.*, each problem, and — when the problems came from this
    same read (``mate_problems_digest == digest``) — *Build is available
    again once the workbook changes: the same workbook would make the same
    mates.*; else, when ``offer``, *The workbook has changed since, so Build
    tries the assembly again.* when both digests are known and differ, and
    only *Build tries the assembly again.* when either is ``""`` (a change
    cannot be claimed then). ``""`` with no gearbox.

    W8: a gearbox on record with modes is said by :func:`modes_record_line`, given ``positions_per_configuration``
    and ``modes`` (the workbook's Modes rows now) as they come.
    """
    from .store import GEARBOX_MOTION
    box = getattr(record, "gearbox", None)
    if box is None:
        return ""
    if not box.assembly:
        problems = [p for p in box.mate_problems if str(p).strip()]
        if not problems:
            return ""
        what = f"{box.name}.SLDASM" if box.name else "The assembly"
        lead = f"{what} was not saved, because SolidWorks found {_mates_lead(problems)} with its mates."
        if box.mate_problems_digest and box.mate_problems_digest == digest:
            then = f"Build is available again once the workbook changes: {SAME_MATES}."
        elif not offer:
            then = ""
        elif box.mate_problems_digest and digest:
            then = "The workbook has changed since, so Build tries the assembly again."
        else:
            then = "Build tries the assembly again."      # which read it came from, or this one, is not known
        return _joined(lead, _mate_problems(problems), then)
    if box.kind == GEARBOX_MOTION:
        drag = [g for g in box.drag if g]
        # W7 (J14): a carrier is axes and planes only, so the drag is a gear of its train, never the carrier.
        carrier = carrier_phrase(record)
        nothing = f" {carrier} is axes and planes only, so it has nothing to drag." if carrier else ""
        if box.modes:
            return modes_record_line(record, positions_per_configuration=positions_per_configuration,
                                     modes=modes) + nothing
        if drag:
            return f"It was built with its gears mated to turn: {drag_phrase(drag)}.{nothing}"
        return f"It was built with its gears each mated to their shaft, free to turn.{nothing}"
    if box.static_reason:
        return _joined(f"It was built static. {_sentence(box.static_reason)}",
                       "That is settled now, so Build again… makes a new revision whose gears turn." if offer else "")
    return ("It was built static, before gears could be mated to turn: Build again… makes a new revision whose gears "
            "turn.") if offer else ""


def _shaft_of(update, gear: str) -> str:
    """The shaft of ``gear``'s ALONG mate in ``update.motion.mates``; ``""`` if none is recorded."""
    motion = getattr(update, "motion", None)
    for mate in getattr(motion, "mates", ()) or ():
        if mate.kind == "along" and tuple(mate.gears)[:1] == (gear,) and mate.shaft:
            return mate.shaft
    return ""


def _along(update, gears: Sequence[str]) -> str:
    """``G4 along S3`` / ``G4 along S3 and G6 along S5`` (``along its shaft`` if no ALONG mate names it). W7: a
    planet row (its shared Face Z global is keyed by the row, W7-INTERFACES §6.7), or all its copies, as *Planet (3
    copies) along P*, the shaft found through the along mates of the row's copies."""
    motion = getattr(update, "motion", None)
    alongs = [m for m in getattr(motion, "mates", ()) or () if m.kind == "along" and m.gears]
    items, rows = [], set()
    for g in gears:
        shaft = _shaft_of(update, g)
        row, k = _copy_parts(g)
        copies = [m for m in alongs if _copy_parts(m.gears[0])[1] and _copy_parts(m.gears[0])[0] == (row if k else g)]
        if (not shaft or k) and copies:
            key = row if k else g
            if key in rows:
                continue
            rows.add(key)
            items.append(f"{copies_phrase(key, len(copies))} along {_copy_parts(copies[0].shaft)[0]}")
            continue
        items.append(f"{g} along {shaft or 'its shaft'}")
    return _and(items)


def _asked_ratio(update, name: str) -> str:
    """``17 : 69``, the ratio ``update.motion.ratios`` asks of the gear mate ``name``; ``""`` if it asks none."""
    motion = getattr(update, "motion", None)
    for mate, a, b in getattr(motion, "ratios", ()) or ():
        if mate == name:
            return f"{a} : {b}"
    return ""


def _ratio_of(update, name: str) -> str:
    """``G1 meshes G2 to 17 : 69`` from ``update.motion.ratios``; ``G1 meshes G2 to its new ratio`` if not there."""
    return f"{name} to {_asked_ratio(update, name) or 'its new ratio'}"


def _gear_mates(update, names: Sequence[str]) -> str:
    """``the gear mate G1 meshes G2 to 17 : 69`` / ``the gear mates … and …``."""
    names = [n for n in names if n]
    return f"the gear mate{'' if len(names) == 1 else 's'} {_and(_ratio_of(update, n) for n in names)}"


def _motion_pieces(update, result) -> List[str]:
    """What the motion path did, as pieces of *Updated SolidWorks: …*, in the order it did them: *turned the mate
    G1 meshes G2 back on (it was suppressed in SolidWorks)* (D10), *moved G4 along S3* (``result.axial``), *set the
    gear mate G1 meshes G2 to 17 : 69* (``result.ratios``), *set the gear mate G1 meshes G2 back to the workbook's
    ratio, which SolidWorks held at another* (``result.ratios_found``: no change was asked, SolidWorks had another),
    or with ``result.ratios_read`` naming both, *set the gear mate G1 meshes G2 back to 17 : 69 (SolidWorks held it
    at 17 : 68)*; a remake that failed (not in ``result.ratios``) is never said to be set. A gear mate the check
    phase found turning against its mesh and made again (``result.sense_found_wrong``, also in ``ratios``): *turned
    the gear mate G5 meshes G6 the right way round (SolidWorks held it turning against its mesh)*. A gear mate the
    app itself made again the other way round straight after making it (``result.turned_round``) is the app doing
    its job: nothing is said of it (the coordinator's ruling), and nothing said counts how often a mate was made."""
    pieces = []
    back = [n for n in result.unsuppressed if n]
    if back:
        one = len(back) == 1
        pieces.append(f"turned the mate{'' if one else 's'} {_and(back)} back on ({'it was' if one else 'they were'} "
                      "suppressed in SolidWorks)")
    axial = [g for g in result.axial if g]
    if axial:
        pieces.append(f"moved {_along(update, axial)}")
    found_all = [n for n in getattr(result, "ratios_found", ()) or () if n]
    # ``sense_found_wrong``: found turning against its mesh and remade (package A, b4d4bdd). Remade for that alone,
    # it is not in ``result.ratios`` (that list is only for a ratio that changed): a turn round, never a new ratio.
    # One whose ratio changed too is said once, its ratio and its turn round in the same piece.
    # A planned remake for a sense the workbook changed (W6, M4): never the check phase's "found wrong" (§2.7). The
    # worker's own list (``GearboxUpdate.resensed``, A's 128aa8e: sense only there, a changed ratio in ``ratios``
    # too); a result without it (a hand-made one) falls back to a remake the plan asked that reached ``ratios``.
    made = getattr(result, "resensed", None)
    asked = [n for n in getattr(update, "resensed", ()) or () if n]
    if made is not None:
        resensed = [n for n in made if n]
        new_ratio = {n for n in resensed if n in result.ratios}
    else:
        resensed = [n for n in asked if n in result.ratios]
        new_ratio = {n for n in resensed if n in (getattr(update, "ratios", ()) or ())}
    wrong = [n for n in getattr(result, "sense_found_wrong", ()) or () if n and n not in resensed]
    against = "SolidWorks held it turning against its mesh"
    for name in resensed:
        read = _ratio_read(result, name)
        if read is not None:
            at = f" at {read[3]} : {read[4]}" if (read[1], read[2]) != (read[3], read[4]) else ""
        else:
            at = f" at {_asked_ratio(update, name)}" if name in new_ratio and _asked_ratio(update, name) else ""
        pieces.append(f"remade the gear mate {name}{at} {_resense_why(update, name)}")
    ratios = [n for n in result.ratios if n and n not in found_all and n not in resensed]
    plain = [n for n in ratios if n not in wrong]
    if plain:
        pieces.append(f"set {_gear_mates(update, plain)}")
    for name in [n for n in ratios if n in wrong]:
        pieces.append(f"set the gear mate {_ratio_of(update, name)} and turned it the right way round ({against})")
    only = [n for n in wrong if n not in result.ratios]
    if only:
        one = len(only) == 1
        pieces.append(f"turned the gear mate{'' if one else 's'} {_and(only)} the right way round (SolidWorks held "
                      f"{'it turning against its mesh' if one else 'them turning against their meshes'})")
    # Found at another ratio though the plan asked no change (a remake lost with an unsaved close, say): set back —
    # said only of a remake that was made (in ``result.ratios``), with both ratios where ``ratios_read`` has them.
    found = [n for n in found_all if n in result.ratios and n not in resensed]
    named = [n for n in found if _ratio_read(result, n) is not None]
    if named:
        one = len(named) == 1
        held = []
        for name in named:
            _, live_a, live_b, want_a, want_b = _ratio_read(result, name)
            turning = ", turning against its mesh" if name in wrong else ""
            held.append(f"{name} back to {want_a} : {want_b} (SolidWorks held it at {live_a} : {live_b}{turning})")
        pieces.append(f"set the gear mate{'' if one else 's'} {_and(held)}")
    unnamed = [n for n in found if n not in named]
    if unnamed:
        one = len(unnamed) == 1
        turning = ((", turning against its mesh" if one else ", turning against their meshes")
                   if all(n in wrong for n in unnamed) else "")
        pieces.append(f"set the gear mate{'' if one else 's'} {_and(unnamed)} back to the workbook's "
                      f"ratio{'' if one else 's'}, which SolidWorks held at another{turning}")
    return pieces


def _gear_shaft(update, gear: str) -> str:
    """The shaft ``gear`` is on, from the recorded mates in ``update.motion``: an anchor's axis or along mate, a
    follower's lock to its anchor; ``""`` if they do not say."""
    mates = getattr(getattr(update, "motion", None), "mates", ()) or ()
    for mate in mates:
        if mate.kind in ("axis", "along") and tuple(mate.gears)[:1] == (gear,) and mate.shaft:
            return mate.shaft
    for mate in mates:
        if mate.kind == "lock" and len(mate.gears) == 2 and mate.gears[1] == gear:
            return _gear_shaft(update, mate.gears[0]) if mate.gears[0] != gear else ""
    return ""


def _resense_why(update, name: str) -> str:
    """Why a gear mate is remade for its sense (W6-PLAN §2.9, as the review corrected it), bracketed so it does not
    run into the next item of a list: *(since S2 now passes S1 on its other side, so G1 and G2 turn the other way
    against each other)*. Only a crossed mesh's sense changes with a move, and crossed shafts pass each other; what
    changes is how the two gears turn against each other — neither is said to reverse, since one may be the input,
    whose speed the workbook fixes. The shaft named first is the one in ``update.moved_shafts`` (the second gear's
    when both moved); when neither of the mesh's shafts moved, or the record does not say them, no shaft is named:
    *(since G1 and G2 now turn the other way against each other)*."""
    mates = getattr(getattr(update, "motion", None), "mates", ()) or ()
    gears = next((tuple(m.gears) for m in mates if m.name == name and len(m.gears) == 2), ())
    if not gears:
        return "(since its gears now turn the other way against each other)"
    a, b = gears
    sa, sb = _gear_shaft(update, a), _gear_shaft(update, b)
    moved = set(getattr(update, "moved_shafts", ()) or ())
    if sa and sb and sa != sb and (sa in moved or sb in moved):
        mover, other = (sb, sa) if sb in moved else (sa, sb)
        return (f"(since {mover} now passes {other} on its other side, so {a} and {b} turn the other way against "
                "each other)")
    return f"(since {a} and {b} now turn the other way against each other)"


def _ratio_read(result, name: str):
    """``(name, live_a, live_b, want_a, want_b)`` from ``result.ratios_read`` for the gear mate ``name``, else None."""
    for entry in getattr(result, "ratios_read", ()) or ():
        if entry and entry[0] == name and len(entry) == 5:
            return tuple(entry)
    return None


def _pair_kind(update, pair: Tuple[str, str]) -> str:
    """``"lock"`` when ``pair`` is a recorded LOCK (anchor, follower), else ``"mesh"``."""
    motion = getattr(update, "motion", None)
    for lock in getattr(motion, "locks", ()) or ():
        if (lock.anchor, lock.follower) == tuple(pair):
            return "lock"
    return "mesh"


def _motion_after(update, result, earlier: str = "") -> List[str]:
    """What the motion path found and put right, each a whole sentence, after the pieces: a relation out of step
    (*G1 and G2 had been turned out of step with each other in SolidWorks; they are back in mesh.* — which of the
    two was turned cannot be told, so neither is said to be), then one sentence per train put
    (``result.restored``: *G1, G2, G3 and G4 had been turned in SolidWorks; their train is back at the turn it was
    built at.* — that train's gears only; a train put with none turned is never mentioned), then, when the check
    phase found the gears turned (``result.turned``) and no mated gear was put, *The gears stand where they were
    turned in SolidWorks.* (W5-DECISIONS answer 2: the train stays where it was turned, and the footer says so),
    or, when some mated gears were put and some not, *Any gear it did not put back stands where it was turned in
    SolidWorks.* (which train stood turned is not told), then the mates the app did not make, left alone
    (``result.extra_mates``).

    W8 (W8-INTERFACES §9.18): on a gearbox with modes where the running version can show a turn in other modes
    (``result.positions_per_configuration`` False), nothing put and no other mode shown, the gears left standing
    turned get :data:`TURN_SHOWN_ELSEWHERE` straight after (after an earlier unsaved Update, when they stand "as
    they were found", :data:`GEARS_SHOWN_ELSEWHERE`, which needs no antecedent): the footer then shows this status
    alone, not the record line's turning note, and another mode may stand with a dog across its sleeve.

    ``earlier`` (``Finished.earlier_update``, set when an earlier Update's
    changes to the assembly were never saved): the frames on record are not
    known to be what SolidWorks held, so nothing is laid to the user — the
    relations out of step and the gears turned back are said by
    :func:`_earlier_update_sentence` instead, and gears left standing are
    *as they were found in SolidWorks*, not *where they were turned*."""
    out = []
    # W8: a crossed coupling in the mode worked in and put there is said once, by _mode_after ("In 4L, RangeSlv's
    # teeth stood across LoDog's …"); a coupling is a dog in a sleeve, not a mesh.
    config = str(getattr(result, "configuration", "") or "")
    per_mode = bool(config) and any(str(c).casefold() == config.casefold()
                                    for c in getattr(result, "put_in", ()) or ())
    if not earlier:
        for a, b in result.out_of_step:
            if per_mode and _couple_pair(update, (a, b)):
                continue
            back = "they are back in step" if _pair_kind(update, (a, b)) == "lock" else "they are back in mesh"
            out.append(f"{a} and {b} had been turned out of step with each other in SolidWorks; {back}.")
        for gears in result.restored:
            gears = [g for g in gears if g]
            if not gears:
                continue
            names = _bodies(gears, _mated_copies(update))          # W7: "C (the carrier)", "Planet (3 copies)"
            one = len(gears) == 1
            out.append(f"{_and(names)} had been turned in SolidWorks; {'its' if one else 'their'} train is back at "
                       "the turn it was built at.")
    if result.turned:
        # Answer 2: with nothing to put, the train stays where it was turned, and the sentence says so plainly.
        motion = getattr(update, "motion", None)
        mated = {g for m in getattr(motion, "mates", ()) or () for g in m.gears if g}
        put = mated & set(result.placed)
        how = "as they were found" if earlier else "where they were turned"
        if not put:
            out.append(f"The gears stand {how} in SolidWorks.")
            # The switch is False only on an Update with modes: swbuild._modes_check sets it on the result just after
            # the configuration worked in, and nothing else sets it on an Update, so no configuration test is needed.
            if getattr(result, "positions_per_configuration", None) is False and not getattr(result, "visited", ()):
                # After an earlier unsaved Update the sentence before says the gears stand "as they were found", so
                # "that turn" would have no antecedent: the wording that needs none.
                out.append(GEARS_SHOWN_ELSEWHERE if earlier else TURN_SHOWN_ELSEWHERE)
        elif put != mated and not getattr(result, "configuration", ""):
            # W8: an Update with modes that put anything showed every mode and put every train found turned in it
            # (W8-INTERFACES §9.18), so no gear it left stands turned; a held gear (a ring) is mated but never put.
            how = "as it was found" if earlier else "where it was turned"
            out.append(f"Any gear it did not put back stands {how} in SolidWorks.")
    already = [n for n in getattr(result, "ratios_already", ()) or () if n]
    if already:
        # Asked to change, found already at the wanted ratio, so not remade: said, as the summary promised the set.
        one = len(already) == 1
        ratios = []
        for name in already:
            read = _ratio_read(result, name)
            ratios.append(f"{read[3]} : {read[4]}" if read is not None else _asked_ratio(update, name))
        if all(ratios):
            what = f"{_and(already)} {'was' if one else 'were'} already {_and(ratios)}"
        else:
            what = f"{_and(already)} {'was' if one else 'were'} already at the ratio the workbook wants"
        out.append(f"The gear mate{'' if one else 's'} {what} in SolidWorks, so "
                   f"{'it was' if one else 'they were'} left as {'it is' if one else 'they are'}.")
    extra = [n for n in result.extra_mates if n]
    if extra:
        one = len(extra) == 1
        where = _file(update.assembly) if update.assembly else "The assembly"
        left = f"Update SolidWorks left {'it as it is' if one else 'them as they are'}."
        if _configurations_of(update):
            # W8 (J12): read in every mode's configuration only; one the record does not know is never read.
            out.append(f"{where} also has {'a mate' if one else 'mates'} the app did not make, {_and(extra)}, "
                       f"suppressed in every mode; {left}")
        else:
            out.append(f"{where} also has {'a suppressed mate' if one else 'suppressed mates'} the app did not make, "
                       f"{_and(extra)}; {left}")
    return out


def _pairs_text(pairs: Sequence[Tuple[str, str]]) -> str:
    """``G2 and G3`` for one relation, ``G1 with G2 and G2 with G3`` for more."""
    pairs = [(a, b) for a, b in pairs if a and b]
    if len(pairs) == 1:
        return f"{pairs[0][0]} and {pairs[0][1]}"
    return _and(f"{a} with {b}" for a, b in pairs)


def _earlier_update_sentence(update, result, earlier: str, off: Sequence[str],
                             pairs: Sequence[Tuple[str, str]], changed: bool = True,
                             still_in_error: bool = False) -> str:
    """What an Update says when an earlier one's changes to the assembly were never saved (``Finished
    .earlier_update``): the frames on record are that Update's, so a gear found off them, or a relation out of
    step, is never said to be the user's doing.

    ``lost`` (SolidWorks closed the assembly unsaved): *The last Update
    SolidWorks was not saved before Reducer_12to1.SLDASM was closed, so its
    changes were made again: G4 is back where the workbook has it.*
    ``not saved`` (still open, or not known; the record cannot tell whether
    that Update finished or stopped part way, so neither is claimed): *G4 was
    not where the last Update SolidWorks, which is not saved, has it on
    record; it is in place again.* and *G2 and G3 were not in step as that
    Update has them on record either; they are in step again.* The gears
    named are ``off`` (``Finished.off_after_update``) and, on the motion
    path, those a put turned back (``result.restored``); the relations are
    ``pairs`` (``Finished.out_of_step_after_update``). ``still_in_error`` (``Finished.still_in_error`` not empty):
    a document an earlier stop left in error is still open, so a press that changed nothing never also says
    SolidWorks holds the workbook (the re-check's note under N4)."""
    from .workbook.gearbox import UPDATE_LOST
    gears: List[str] = []
    for gear in list(off) + [g for train in getattr(result, "restored", ()) or () for g in train]:
        if gear and gear not in gears:
            gears.append(gear)
    rank = {g: i for i, g in enumerate(p.gear for p in update.placements)}
    gears.sort(key=lambda g: rank.get(g, len(rank)))          # as the gears are listed, the order sort keeps
    pairs = [(a, b) for a, b in pairs if a and b]
    one = len(gears) == 1
    if earlier == UPDATE_LOST:
        asm = _file(update.assembly) if update.assembly else "the assembly"
        if not changed and still_in_error:
            return f"The last Update SolidWorks was not saved before {asm} was closed."
        if not changed:
            # This Update changed nothing: the workbook as it now is was already what SolidWorks holds.
            return (f"The last Update SolidWorks was not saved before {asm} was closed; SolidWorks already holds the "
                    "workbook as it now is, so nothing needed making again.")
        found = []
        if gears:
            found.append(f"{_and(gears)} {'is' if one else 'are'} back where the workbook has "
                         f"{'it' if one else 'them'}")
        if pairs:
            found.append(f"{_pairs_text(pairs)} are back in step{' with each other' if len(pairs) == 1 else ''}")
        return (f"The last Update SolidWorks was not saved before {asm} was closed, so its changes were made again"
                + (": " + "; ".join(found) if found else "") + ".")
    out = []
    if gears:
        out.append(f"{_and(gears)} {'was' if one else 'were'} not where the last Update SolidWorks, which is not "
                   f"saved, has {'it' if one else 'them'} on record; {'it is' if one else 'they are'} in place again.")
    if pairs:
        out.append(f"{_pairs_text(pairs)} were not in step as "
                   + ("that Update has them on record either" if gears else
                      "the last Update SolidWorks, which is not saved, has them on record")
                   + "; they are in step again.")
    return " ".join(out)


def motion_update_lines(update, result) -> List[str]:
    """The W5 pieces of a finished update's sentence (``UpdatePlan``, ``swbuild.GearboxUpdate`` of the motion
    path), each a whole sentence, in order: *Turned the mate G1 meshes G2 back on (it was suppressed in
    SolidWorks).*, *Moved G4 along S3.*, *Set the gear mate G1 meshes G2 to 17 : 69.*, then
    :func:`_motion_after`'s. :func:`gearbox_update_status` folds the first three into its *Updated SolidWorks: …*
    list and adds the rest after it. ``[]`` for W4's static path (``update.motion`` None)."""
    if getattr(update, "motion", None) is None:
        return []
    return [_sentence(p[:1].upper() + p[1:]) for p in _motion_pieces(update, result)] + _motion_after(update, result)


# -- W7: planetary stages (W7-PLAN §2.12; Agent C writes them) ----------------------------------------------------
#
# Pinned in W7's interface commit (docs/notes-workbook/W7-INTERFACES.md). Until C writes them each raises a sentence;
# nothing calls them before C does.


def _carrier_parts(record_or_plan) -> List[Tuple[str, str]]:
    """``(carrier shaft, part path)`` from a ``store.LinkRecord`` (``gearbox.carriers``) or a
    ``workbook.gearbox.GearboxPlan`` (``carrier_layouts`` and ``carrier_paths``), in their order."""
    box = getattr(record_or_plan, "gearbox", None)
    if box is not None:
        return [(c.shaft, c.path) for c in getattr(box, "carriers", ()) or () if c.shaft]
    paths = getattr(record_or_plan, "carrier_paths", None) or {}
    layouts = getattr(record_or_plan, "carrier_layouts", ()) or ()
    shafts = [c.shaft for c in layouts] or list(paths)
    return [(shaft, paths.get(shaft, "")) for shaft in shafts if shaft]


def carrier_phrase(record_or_plan, *, part: bool = False) -> str:
    """How the carrier is named in the window's sentences, from a ``store.LinkRecord`` (its ``gearbox.carriers``) or
    a ``workbook.gearbox.GearboxPlan`` (its ``carrier_layouts``): *"C (the carrier)"*, and with ``part`` — where a
    sentence names the part — *"C, built as Planetary_4to1_C_Carrier (axes and planes only)"*; ``""`` with no
    carrier."""
    carriers = _carrier_parts(record_or_plan)
    if part:
        return _and(f"{shaft}, built as {_stem(path)} (axes and planes only)" if path else f"{shaft} (the carrier)"
                    for shaft, path in carriers)
    return _and(f"{shaft} (the carrier)" for shaft, _ in carriers)


def copies_phrase(row: str, n: int) -> str:
    """A planet row and its copies in a sentence: *"Planet (3 copies)"*, and the row alone with Copies 1."""
    return f"{row} ({n} copies)" if n > 1 else row


def _copy_parts(name: str) -> Tuple[str, int]:
    """``("Planet", 2)`` for ``"Planet copy 2"`` (``workbook.planetary.copy_of``), ``(name, 0)`` for any other."""
    row, sep, k = name.rpartition(" copy ")
    return (row, int(k)) if sep and row and k.isdigit() else (name, 0)


def _copy_counts(names: Iterable[str]) -> Dict[str, int]:
    """Each planet row's number of copies among ``names`` (every gear the plan or the record mates)."""
    counts: Dict[str, set] = {}
    for name in names:
        row, k = _copy_parts(name)
        if k:
            counts.setdefault(row, set()).add(k)
    return {row: len(ks) for row, ks in counts.items()}


def _bodies(ids: Sequence[str], counts: Mapping[str, int]) -> List[str]:
    """Gear and carrier ids as a sentence names them (W7-PLAN §2.12): a carrier ``"C carrier"`` as *C (the
    carrier)*; every copy of a planet row, when all of them are listed, once as *Planet (3 copies)* where its first
    copy stands — never N near-identical names; a copy listed without its fellows by its own id."""
    from .store import CARRIER_ID_SUFFIX
    listed = set(ids)
    out: List[str] = []
    done: set = set()
    for name in ids:
        if not name:
            continue
        if name.endswith(CARRIER_ID_SUFFIX):
            out.append(f"{name[:-len(CARRIER_ID_SUFFIX)]} (the carrier)")
            continue
        row, k = _copy_parts(name)
        n = counts.get(row, 0)
        if k and n > 1 and all(f"{row} copy {i}" in listed for i in range(1, n + 1)):
            if row not in done:
                out.append(copies_phrase(row, n))
                done.add(row)
            continue
        out.append(name)
    return out


def _turn_word(value, sign: int) -> str:
    about = value * sign
    return "still" if about == 0 else ("anticlockwise" if about > 0 else "clockwise")


def planetary_speed_line(shaft: str, motion, *, copies: int = 1, carrier: str = "", held: bool = False) -> str:
    """The Speeds line of a planet shaft or a held member (W7-PLAN §2.12) from a ``kinematics.Motion``, in the
    panel's own form (:func:`workbook_speed_lines`): a planet shaft's speed about its own axis, then its speed on its
    carrier (``motion.relative``), and how many copies turn so — *"P     500.0 rpm clockwise, 750.0 rpm clockwise
    relative to C · 3 copies"*, with W6's *seen from the +X end* once after the first way round when any shaft is
    off Z (W6-INTERFACES §7.19); a held member (``held``, or in ``motion.held``) *"R     held still · 5.76 N·m"*,
    the torque it holds when one is worked out.
    Numbers are joined to their units by :data:`NBSP`."""
    holds = getattr(motion, "held", None) or {}
    if not carrier and (held or shaft in holds):
        return f"{shaft:<4}  held still" + (f" · {holds[shaft]:.2f}{NBSP}N·m" if shaft in holds else "")
    speed = motion.speeds.get(shaft)
    if speed is None:
        return f"{shaft:<4}  not driven"
    seen = getattr(motion, "seen_from", None) or {}
    sign = (getattr(motion, "axis_sign", None) or {}).get(shaft, 1)
    turns = _turn_word(speed, sign)
    if turns != "still" and any(v != "+Z" for v in seen.values()):
        turns = f"{turns} seen from the {seen.get(shaft, '+Z').replace(' ', NBSP)} end"
    text = f"{shaft:<4}  {abs(float(speed)):.1f}{NBSP}rpm {turns}"
    relative = (getattr(motion, "relative", None) or {}).get(shaft)
    if carrier and relative is not None:
        text += f", {abs(float(relative)):.1f}{NBSP}rpm {_turn_word(relative, sign)} relative to {carrier}"
    if copies > 1:
        text += f" · {copies} copies"
    return text


# --- W8: modes (W8-PLAN §1.12, W8-INTERFACES.md §7 and §9). Each sentence as §1.12 gives it, filled from fields,
# with two changes of words: a mode is "a mode" wherever the user acts on it (each is a configuration named as the
# mode, said once, and switched in SolidWorks' ConfigurationManager: SWITCH_MODE), and the assembly is said to be
# saved in its first mode (§9.9). The existing functions keep their signatures (keyword-only additions) and call these.

TURN_STAYS = "A turn you give the gears in one mode stays in that mode."
# After an Update with modes that found the gears turned in the mode showing and put nothing, where the running version
# can show a turn in other modes (W8-INTERFACES §9.18): said straight after "The gears stand where they were turned in
# SolidWorks." (_motion_after), since the footer shows that status alone.
TURN_SHOWN_ELSEWHERE = ("This version of SolidWorks can show that turn in other modes, so a dog may stand across its "
                        "sleeve in another; to put the gears back there, press Update SolidWorks with that mode showing.")
GEARS_SHOWN_ELSEWHERE = ("This version of SolidWorks can show the gears at the same turn in other modes, so a dog may "
                         "stand across its sleeve in another; to put the gears back there, press Update SolidWorks with "
                         "that mode showing.")
# "Can show", not "shows": on 2026 a turn was read in every mode on a copy no Update had moved (W8 s7), but after an
# Update had put every mode a fresh turn was read in 4L, while 4H and N, shown after a put in 2H, stood at the built
# turn (W8 s2, 34.0.0, a sequence that showed 4L alone before the press and has not run again). On 34.1.1 s2's current
# sequence and every turn s7 gave showed in every mode, as on 2024 in s2 and s7; 34.0.0's one differing reading stays
# unexplained (W8-INTERFACES §9.18, findings.TURN_PER_CONFIGURATION).
TURN_CAN_SHOW_ELSEWHERE = ("A turn you give the gears in one mode can show in other modes, so a dog can stand across "
                           "its sleeve in another; to put the gears back there, press Update SolidWorks with that mode "
                           "showing.")
# An Update pressed in a mode whose train is in step, with nothing changed in the workbook, puts nothing and judges
# no other mode (J25), so TURN_CAN_SHOW_ELSEWHERE makes pressing it with that mode showing the condition, and no more.


def turning_note(positions_per_configuration: Optional[bool]) -> str:
    """The footer's sentence about turning in a gearbox with modes (W8-PLAN §1.9, §1.12), chosen by
    ``swcom.positions_per_configuration`` for the running version — carried on ``GearboxResult`` /
    ``GearboxUpdate.positions_per_configuration``: True :data:`TURN_STAYS`, False :data:`TURN_CAN_SHOW_ELSEWHERE`,
    None (the finding unsettled for this version) ``""``: neither claim. The one home of that switch; every
    sentence that says where a turn shows asks it."""
    if positions_per_configuration is True:
        return TURN_STAYS
    if positions_per_configuration is False:
        return TURN_CAN_SHOW_ELSEWHERE
    return ""


def workbook_part_refusal(path: str, kind: str) -> str:
    """The strip's refusal of a part made from a gearbox workbook (W8-PLAN §1.1, the plan review's S9), through Open
    .gear.json and the live link alike: *Sleeve_m1.5_N30.SLDPRT is a sleeve made from a gearbox workbook; open that
    workbook to change it.* — the file's name, and the kind in the workbook's own word (its Gears sheet's Kind, so a
    dog is *a dog*). Only for a kind in ``gears.WORKBOOK_KINDS``, the one home of which kinds those are; any other
    kind is a ValueError sentence, since a lone gear of it opens as always."""
    from .gears import WORKBOOK_KINDS
    if kind not in WORKBOOK_KINDS:
        raise ValueError(f"A {kind or 'gear'} part is not made from a gearbox workbook, so the strip does not refuse "
                         "it as one.")
    return f"{_file(path)} is a {kind} made from a gearbox workbook; open that workbook to change it."


CHOOSER_SHOWS = "The mode chosen here changes only what this window shows"


def mode_chooser_note(record=None) -> str:
    """The grey line at the foot of the Speeds panel whenever the window shows its mode chooser (W8-PLAN J21): the
    chooser picks which mode's speeds and end view the window shows and never switches SolidWorks. With an assembly
    on record built with modes (``GearboxRecord.modes``), where the footer tells the user to switch mode in
    SolidWorks: *The mode chosen here changes only what this window shows; it does not switch the mode SolidWorks
    shows.* Before that, with nothing in SolidWorks to switch: *The mode chosen here changes only what this window
    shows.*"""
    box = getattr(record, "gearbox", None)
    if box is not None and box.assembly and getattr(box, "modes", None):
        return f"{CHOOSER_SHOWS}; it does not switch the mode SolidWorks shows."
    return f"{CHOOSER_SHOWS}."


SWITCH_IN_STEP = "Switching mode never by itself puts a dog tooth on tooth."


def switching_note(positions_per_configuration: Optional[bool]) -> str:
    """What showing another mode does to a coupling's teeth, said only where the running version keeps each
    configuration's own positions (``positions_per_configuration`` True, W8-PLAN §1.9: each coupling was made in its
    own configuration at the built turn, and a switch inherits no angle); ``""`` where it is False or unknown, since
    with shared positions a switch can engage a coupling at whatever angle a turn left."""
    return SWITCH_IN_STEP if positions_per_configuration is True else ""


def _positions_notes(positions_per_configuration: Optional[bool]) -> str:
    """:func:`turning_note` and :func:`switching_note`, as the footer says them."""
    return _joined(turning_note(positions_per_configuration), switching_note(positions_per_configuration))


SWITCH_MODE = "to switch mode, double-click another mode's configuration in SolidWorks' ConfigurationManager"
# How a user shows another mode in SolidWorks (each mode is a configuration named as the mode): said in the
# workbook's word, mode, naming SolidWorks' own list as the place.


def _slides(mates) -> List[Tuple[str, str]]:
    """``(slider, shaft)`` for each SLIDE mate of a turning plan or record, in order."""
    return [(tuple(m.gears)[0], m.shaft) for m in mates or () if m.kind == "slide" and tuple(m.gears)]


def modes_ready_line(plan) -> str:
    """Before Build (:func:`motion_ready_line` asks it), for a ``GearboxPlan`` whose ``motion`` has modes: *It has 4
    modes, 2H, 4H, N and 4L: each becomes a configuration of the assembly, and it opens in 2H.*; one mode, *It has
    one mode, 2H, which becomes a configuration of the assembly, the one it opens in.*; sliders and no Modes rows,
    *RangeSlv and ModeSlv slide, but the Modes sheet has no rows, so the assembly has one configuration with each at
    its position 0.* (*RangeSlv slides, … with it at …*); ``""`` with neither."""
    motion = getattr(plan, "motion", None) if plan is not None else None
    if motion is None:
        return ""
    modes = [str(m) for m in getattr(motion, "modes", ()) or () if str(m)]
    if len(modes) == 1:
        return (f"It has one mode, {modes[0]}, which becomes a configuration of the assembly, the one it opens in.")
    if modes:
        return (f"It has {len(modes)} modes, {_and(modes)}: each becomes a configuration of the assembly, and it opens "
                f"in {modes[0]}.")
    sliders = [g for g, _ in _slides(motion.mates)]
    if not sliders:
        return ""
    who, one = _and(sliders), len(sliders) == 1
    return (f"{who} slide{'s' if one else ''}, but the Modes sheet has no rows, so the assembly has one configuration "
            f"with {'it' if one else 'each'} at its position 0.")


def _modes_of(plan) -> List[str]:
    motion = getattr(plan, "motion", None) if plan is not None else None
    return [str(m) for m in getattr(motion, "modes", ()) or () if str(m)]


def _slides_sentence(motion) -> str:
    """*RangeSlv and ModeSlv slide along Rear, each to its place in each mode.* (*G4 slides along S3 and G7 along
    S5, …* for sliders on different shafts)."""
    slides = _slides(getattr(motion, "mates", ()))
    if not slides:
        return ""
    shafts = list(dict.fromkeys(shaft for _, shaft in slides))
    one = len(slides) == 1
    if len(shafts) == 1:
        what = f"{_and(g for g, _ in slides)} slide{'s' if one else ''} along {shafts[0]}"
    else:
        what = (f"{slides[0][0]} slides along {slides[0][1]} and "
                + _and(f"{g} along {s}" for g, s in slides[1:]))
    return f"{what}, {'to its' if one else 'each to its'} place in each mode."


def _drag_sentence(drag: Sequence[str]) -> str:
    """:func:`drag_phrase` as a sentence of its own: *Drag Sun in SolidWorks and the rest of its train follow.*"""
    phrase = drag_phrase(drag)
    return f"{phrase[:1].upper()}{phrase[1:]}." if phrase else ""


def modes_done_line(plan, result) -> str:
    """After a Build with modes whose assembly saved (:func:`motion_done_line` asks it): *Its gears are mated to
    turn in each of its 4 modes, one configuration each (2H, 4H, N and 4L), and SolidWorks reports no mate in error
    in any of them: it opens in 2H; to switch mode, double-click another mode's configuration in SolidWorks'
    ConfigurationManager. Drag Sun in SolidWorks and the rest of its train follow.*, the sliders' sentence, then, by
    the running
    version (``result.positions_per_configuration``), :func:`turning_note` and :func:`switching_note`. The
    interference ending per mode is :func:`gearbox_status`'s (:func:`_modes_interference`). ``""`` without modes."""
    modes = _modes_of(plan)
    motion = getattr(plan, "motion", None) if plan is not None else None
    if not modes or motion is None:
        return ""
    drag = [g for g in motion.drag if g]
    count = "one mode, one configuration" if len(modes) == 1 else f"{len(modes)} modes, one configuration each"
    names = modes[0] if len(modes) == 1 else _and(modes)
    any_of = "in it" if len(modes) == 1 else "in any of them"
    switch = f"; {SWITCH_MODE}" if len(modes) > 1 else ""
    text = (f"{_turning_subject(motion)} are mated to turn in each of its {count} ({names}), and SolidWorks "
            f"reports no mate in error {any_of}: it opens in {modes[0]}{switch}.")
    return _joined(text, _drag_sentence(drag), _slides_sentence(motion), _carrier_sentences(plan, built=True),
                   _fixed_sentence(_fixed_gears(motion)),
                   _positions_notes(getattr(result, "positions_per_configuration", None)))


def _modes_interference(modes, assembly: str, meshes=None, every: Sequence[str] = ()) -> Tuple[str, bool]:
    """:func:`_interference` across the configurations a build or an Update checked (``ModeCheck`` each, mode
    order). ``every``: all the gearbox's modes (the plan's, or ``MotionUpdate.configurations``). Clean: *; no
    interference between the gears in any mode, where they stand.* only when the modes checked are every mode
    (compared ignoring case), else naming those checked, *…in 4H and 2H, where they stand.* (W8-INTERFACES §9.11,
    §9.13: nothing is said of a mode not shown). Clashes, each list said once with the modes it was found in, *.
    Check: in 2H and 4H, RangeSlv and InDog interfere, 0.5 mm³; look where they meet in TransferCase.SLDASM.*; and a
    mode it could not check, *Interference could not be checked in 4L: …*, after any clash, so neither hides the
    other."""
    where = f" in {assembly}" if assembly else ""
    errors = [(m.name, m.interference_error) for m in modes if m.interference_error]
    groups: List[Tuple[List[str], Tuple[str, ...]]] = []
    clashes: list = []
    for mode in modes:
        if not mode.clashes:
            continue
        lines = tuple(_clash_lines(mode.clashes))
        clashes.extend(mode.clashes)
        for names, said in groups:
            if said == lines:
                names.append(mode.name)
                break
        else:
            groups.append(([mode.name], lines))
    out = []
    if groups:
        look = ("at their mesh" if len(groups) == 1 and len(groups[0][1]) == 1 else "at those meshes") \
            if _all_meshes(clashes, meshes) else "where they meet"
        found = "; ".join(f"in {_and(names)}, {'; '.join(lines)}" for names, lines in groups)
        out.append(f"Check: {found}; look {look}{where}.")
    if errors:
        said = " ".join(f"Interference could not be checked in {name}: {_sentence(err)}" for name, err in errors)
        out.append(f"{said} Look at each mesh{where} by eye.")
    if out:
        return ". " + " ".join(out), False
    checked = sorted(str(m.name).casefold() for m in modes)
    if len(modes) > 1 and checked == sorted(str(m).casefold() for m in every):
        return "; no interference between the gears in any mode, where they stand.", True
    return f"; no interference between the gears in {_and(m.name for m in modes)}, where they stand.", True


def mode_problem(problem: str) -> str:
    """A problem of the per-mode check (A writes *In mode 4L, the mate RangeSlv engages LoDog over-defines the
    assembly.*, *SolidWorks would not make the configuration 4L.*, …), shown whole: the one home of how a worker's
    problem sentence is shown (:func:`_mate_problems` says each through it)."""
    return _sentence(str(problem))


def _order_sentence(built: Sequence[str], modes: Sequence[str]) -> str:
    """The Modes rows reordered since the build (the same names, ignoring case, in another order: W8-INTERFACES
    §9.9, an Update with nothing to do): *The Modes rows are in another order now, which changes nothing in
    SolidWorks: it keeps 2H as the mode it was saved in, and Build again… would save the next revision in 4L.*; with
    the same first mode, *…: it keeps 2H as the mode it was saved in.*"""
    built = [str(m) for m in built if str(m)]
    modes = [str(m) for m in modes if str(m)]
    if not built or not modes or len(built) != len(modes):
        return ""
    folded = [m.casefold() for m in built], [m.casefold() for m in modes]
    if sorted(folded[0]) != sorted(folded[1]) or folded[0] == folded[1]:
        return ""
    text = (f"The Modes rows are in another order now, which changes nothing in SolidWorks: it keeps {built[0]} as "
            f"the mode it was saved in")
    if folded[0][0] != folded[1][0]:
        text += f", and Build again… would save the next revision in {modes[0]}"
    return text + "."


def modes_record_line(record, *, positions_per_configuration: Optional[bool] = None,
                      modes: Sequence[str] = ()) -> str:
    """The footer for a gearbox on record with modes (``GearboxRecord.modes``; :func:`motion_record_line` asks it):
    *It was built with a configuration per mode (2H, 4H, N and 4L), each named as its mode, and saved in 2H; to
    switch mode, double-click another mode's configuration in SolidWorks' ConfigurationManager. Drag Sun in
    SolidWorks and the rest of its train follow.* (the first of ``modes`` on record is the one it was saved in, W8-INTERFACES §9.9). Then,
    with ``modes`` (the workbook's Modes rows now, in order), the reordered rows' sentence (:func:`_order_sentence`),
    and by ``positions_per_configuration`` (the running version's, from the last job; None after a restart: neither
    claim) :func:`turning_note` and :func:`switching_note`. ``""`` with no modes on record."""
    box = getattr(record, "gearbox", None)
    built = [str(m) for m in getattr(box, "modes", ()) or () if str(m)] if box is not None else []
    if not built:
        return ""
    drag = [g for g in box.drag if g]
    each = "one configuration, named as its mode," if len(built) == 1 else \
        f"a configuration per mode ({_and(built)}), each named as its mode, and"
    lead = f"It was built with {each} saved in {built[0]}"
    if len(built) == 1:
        lead = f"It was built with {each} and saved in it"
    text = f"{lead}; {SWITCH_MODE}." if len(built) > 1 else f"{lead}."
    return _joined(text, _drag_sentence(drag), _order_sentence(built, modes), _positions_notes(positions_per_configuration))


def _recorded_mate(update, name: str):
    for mate in getattr(getattr(update, "motion", None), "mates", ()) or ():
        if mate.name == name:
            return mate
    return None


def _slide_words(update, name: str) -> Tuple[str, str]:
    """(slider, shaft) of the SLIDE ``name`` on record, else (``name``, "")."""
    mate = _recorded_mate(update, name)
    if mate is None or not tuple(mate.gears):
        return name, ""
    return tuple(mate.gears)[0], mate.shaft


def _by_value(entries: Sequence[Tuple[str, float]]) -> List[Tuple[List[str], float]]:
    """``[(configurations, value)]``: entries of one value said once, in the order first met."""
    groups: List[Tuple[List[str], float]] = []
    for config, value in entries:
        for names, v in groups:
            if abs(v - value) < 1e-9:
                names.append(config)
                break
        else:
            groups.append(([config], float(value)))
    return groups


def _places(groups: Sequence[Tuple[List[str], float]], back: bool = False) -> str:
    """``in 4L to 66.5 mm`` / ``in 2H and 4H to 46 mm and in 4L to 66 mm`` (``back to`` with ``back``)."""
    to = "back to" if back else "to"
    return " and ".join(f"in {_and(names)} {to} {_n(value)} mm" for names, value in groups)


def _per_slide(triples: Sequence[Tuple[str, str, float]]) -> List[Tuple[str, List[Tuple[str, float]]]]:
    """``[(slide, [(configuration, value)])]`` in the order the slides are first met."""
    out: Dict[str, List[Tuple[str, float]]] = {}
    for name, config, value in triples:
        out.setdefault(name, []).append((config, float(value)))
    return list(out.items())


def _wanted_value(update, name: str, config: str) -> Optional[float]:
    for slide, conf, value in getattr(getattr(update, "motion", None), "slide_values", ()) or ():
        if slide == name and str(conf).casefold() == str(config).casefold():
            return float(value)
    return None


def _recorded_value(update, name: str, config: str) -> Optional[float]:
    mate = _recorded_mate(update, name)
    for conf, value in getattr(mate, "values", ()) or ():
        if str(conf).casefold() == str(config).casefold():
            return abs(float(value))
    return None


def _on_record(update, name: str, config: str) -> bool:
    """Whether the record has the mate ``name`` on in ``config`` (``swbuild.on_in`` of its recorded on-set)."""
    from .swbuild import on_in
    mate = _recorded_mate(update, name)
    return on_in(tuple(getattr(mate, "modes", ()) or ()), config)


def _flag_pieces(pairs_on: Sequence[Tuple[str, str]], pairs_off: Sequence[Tuple[str, str]], update,
                 *, done: bool) -> List[str]:
    """Each mate's flags set, per mate, its configurations named once. A flag that puts the record's own state back
    (D10 per configuration) — *turned the mate RangeSlv engages LoDog back on in 4L* / *suppressed the mate RangeSlv
    engages InDog again in 4L, where it was on* — or one a workbook edit changes (J14) — *switched the mate ModeSlv
    engages FrontDog off in 4H* (``done`` False: *switch …*)."""
    order: List[str] = []
    back_on: Dict[str, List[str]] = {}
    again: Dict[str, List[str]] = {}
    switch: Dict[str, List[Tuple[str, bool]]] = {}
    for (name, config), on in [(p, True) for p in pairs_on] + [(p, False) for p in pairs_off]:
        if name not in order:
            order.append(name)
        recorded = _on_record(update, name, config)
        if done and on and recorded:
            back_on.setdefault(name, []).append(config)
        elif done and not on and not recorded:
            again.setdefault(name, []).append(config)
        else:
            switch.setdefault(name, []).append((config, on))
    pieces = []
    verb = "switched" if done else "switch"
    for name in order:
        if name in back_on:
            pieces.append(f"turned the mate {name} back on in {_and(back_on[name])}")
        if name in again:
            pieces.append(f"suppressed the mate {name} again in {_and(again[name])}, where it was on")
        if name in switch:
            ons = [c for c, on in switch[name] if on]
            offs = [c for c, on in switch[name] if not on]
            said = [f"on in {_and(ons)}"] if ons else []
            said += [f"off in {_and(offs)}"] if offs else []
            pieces.append(f"{verb} the mate {name} {' and '.join(said)}")
    return pieces


def _mode_summary_pieces(update) -> List[str]:
    """What an Update with modes will do (:func:`update_summary`): each slide value that differs from the record,
    *move RangeSlv in 4L to 66.5 mm along Rear*, and each coupling's or sliding mesh's on-set that differs, *switch
    the mate ModeSlv engages FrontDog off in 4H*."""
    motion = getattr(update, "motion", None)
    if motion is None or not getattr(motion, "configurations", ()):
        return []
    pieces = []
    moves = [(name, config, value) for name, config, value in motion.slide_values
             if _recorded_value(update, name, config) is None
             or abs(_recorded_value(update, name, config) - float(value)) > 1e-9]
    for name, entries in _per_slide(moves):
        gear, shaft = _slide_words(update, name)
        pieces.append(f"move {gear} {_places(_by_value(entries))}" + (f" along {shaft}" if shaft else ""))
    on, off = [], []
    for name, wanted in motion.on_sets:
        from .swbuild import on_in
        for config in motion.configurations:
            want, had = on_in(tuple(wanted), config), _on_record(update, name, config)
            if want != had:
                (on if want else off).append((name, config))
    pieces += _flag_pieces(on, off, update, done=False)
    return pieces


def _mode_pieces(update, result) -> List[str]:
    """What an Update with modes did, as pieces of *Updated SolidWorks: …*: the slide values set for an edit
    (``result.slid``: *moved RangeSlv in 4H and 4L to 66.5 mm along Rear*), those set back to the record's
    (``values_restored``: *set RangeSlv's place in 4L back to 66 mm, where it had been changed in SolidWorks*), and
    the flags set (``unsuppressed_in``, ``suppressed_in``: :func:`_flag_pieces`), each configuration named once."""
    pieces = []
    for name, entries in _per_slide(getattr(result, "slid", ()) or ()):
        gear, shaft = _slide_words(update, name)
        pieces.append(f"moved {gear} {_places(_by_value(entries))}" + (f" along {shaft}" if shaft else ""))
    restored = []
    for name, config in getattr(result, "values_restored", ()) or ():
        value = _wanted_value(update, name, config)
        if value is None:
            value = _recorded_value(update, name, config)
        if value is not None:
            restored.append((name, config, value))
    for name, entries in _per_slide(restored):
        gear, _ = _slide_words(update, name)
        pieces.append(f"set {gear}'s place {_places(_by_value(entries), back=True)}, where it had been changed in "
                      "SolidWorks")
    pieces += _flag_pieces(list(getattr(result, "unsuppressed_in", ()) or ()),
                           list(getattr(result, "suppressed_in", ()) or ()), update, done=True)
    return pieces


def _couple_pair(update, pair: Tuple[str, str]) -> bool:
    """Whether ``pair`` is a coupling on record (a COUPLE mate of those two gears, either order)."""
    mates = getattr(getattr(update, "motion", None), "mates", ()) or ()
    return any(m.kind == "couple" and set(m.gears) == set(pair) for m in mates)


def _mode_after(update, result, *, changed: bool, earlier: str = "") -> List[str]:
    """The whole sentences an Update with modes adds (``result.configuration`` set): a coupling found out of step
    in the configuration it worked in and put there, *In 4H, RangeSlv's teeth stood across InDog's; the gears of 4H
    are back at the turn they were built at.* (and, only where the running version shares positions, that the turn
    may have been given in another mode); where it worked and what it showed (W8-INTERFACES §9.11: always, for a
    quiet Update too), *It worked in 4H, the configuration that was active, then showed and checked 2H, N and 4L and
    left the assembly in 4H.* or *It worked in 4H, the configuration that was active; it did not show the other
    modes, since nothing in 4H needed changing.* (the reason is known only for the mode worked in: with shared
    positions another mode may stand turned, J25); where the running version shares positions and the mode worked in
    was put, the visited modes found at the built turn when shown (*The gears of 2H, N and 4L stood at the turn they
    were built at when Update SolidWorks showed them.*: read, never inferred); after showing others with nothing of
    the assembly's changed, that SolidWorks marks it modified; and the configurations the app did not make, left
    alone. A result on a gearbox with modes (``MotionUpdate.configurations``) that names no configuration still says
    the other modes were not shown: *It worked in the configuration that was active; it did not show the other
    modes, …*.

    ``earlier`` (``Finished.earlier_update``, an earlier Update's changes never saved): a crossed coupling is said
    once, by :func:`_earlier_update_sentence` (it is in ``Finished.out_of_step_after_update``), and never laid to a
    turn, so neither its per-mode sentence nor the shared-turn one is said here (W8-REVIEW-LATE-FIXES S1)."""
    config = getattr(result, "configuration", "")
    if not config:
        if not _configurations_of(update):
            return []
        since = ", since nothing there needed changing" if not changed else ""
        return [f"It worked in the configuration that was active; it did not show the other modes{since}."]
    out = []
    asm = _file(update.assembly) if getattr(update, "assembly", "") else "the assembly"
    put_here = any(str(c).casefold() == config.casefold() for c in getattr(result, "put_in", ()) or ())
    if put_here and not earlier:
        # One sentence per crossed coupling, the last carrying "the gears of 4L are back …" once, then the
        # shared-turn sentence once: two crossed couplings in one mode (W8 s2's 4L) are not said back twice.
        crossed = [(a, b) for a, b in result.out_of_step if _couple_pair(update, (a, b))]
        for index, (a, b) in enumerate(crossed, 1):
            if index < len(crossed):
                out.append(f"In {config}, {a}'s teeth stood across {b}'s.")
            else:
                out.append(f"In {config}, {a}'s teeth stood across {b}'s; the gears of {config} are back at the turn "
                           "they were built at.")
        if crossed and getattr(result, "positions_per_configuration", None) is False:
            out.append("This version of SolidWorks can show a turn given in one mode in the others, so the turn may "
                       "have been given in another.")
    visited = [str(v) for v in getattr(result, "visited", ()) or () if str(v)]
    if put_here and visited and getattr(result, "positions_per_configuration", None) is False:
        # Shared positions: say which visited modes were READ at the built turn when shown, and no more. Their
        # ModeCheck, taken on showing: nothing off its place (off_axis empty) and nothing out of step, so train_check
        # judged every mated gear at its frame on record and in step, and only then is "turned" False a judgement
        # (train_check sets turned = in_step and …); and the mode not put, so every gear no train holds was at its
        # frame too (_modes_put puts one that is not). A mode with a gear off its place is never named.
        put = {str(c).casefold() for c in getattr(result, "put_in", ()) or ()}
        built = [c.name for c in getattr(result, "modes", ()) or ()
                 if str(c.name).casefold() != config.casefold() and str(c.name).casefold() not in put
                 and not c.out_of_step and not c.off_axis and not c.turned]
        if built:
            out.append(f"The gears of {_and(built)} stood at the turn they were built at when Update SolidWorks "
                       f"showed {'it' if len(built) == 1 else 'them'}.")
    if visited:
        out.append(f"It worked in {config}, the configuration that was active, then showed and checked "
                   f"{_and(visited)} and left the assembly in {config}.")
        if update.assembly and not any(_file(p).lower() == _file(update.assembly).lower() for p in result.changed):
            out.append(f"Showing {'it' if len(visited) == 1 else 'them'} leaves {asm} marked modified in SolidWorks, "
                       "although nothing in it changed.")
    else:
        since = f", since nothing in {config} needed changing" if not changed else ""
        out.append(f"It worked in {config}, the configuration that was active; it did not show the other "
                   f"modes{since}.")
    unread = _senses_unread_sentence(update, result)
    if unread:
        out.append(unread)
    ours = {str(name).casefold() for what, name in getattr(update, "leftovers", ()) or () if what == "configuration"}
    extra = [str(c) for c in getattr(result, "extra_configurations", ()) or ()
             if str(c) and str(c).casefold() not in ours]
    if extra:
        one = len(extra) == 1
        out.append(f"{asm[:1].upper()}{asm[1:]} also has {'a configuration' if one else 'configurations'} the app did "
                   f"not make ({_and(extra)}); Update SolidWorks left {'it as it is' if one else 'them as they are'}.")
    return out


UNREAD_PAIRS = 3       # gear pairs named in the unread-senses sentence; more are counted, as CONSEQUENCE_CELLS


def _senses_unread_sentence(update, result) -> str:
    """W8-INTERFACES §9.16: the recorded gear mates whose turning direction no read reached in this Update
    (``GearboxUpdate.senses_unread``: couplings, splines or sliding meshes off in the mode SolidWorks shows), named by
    their gears, the first :data:`UNREAD_PAIRS` and the rest counted: *Which way ModeSlv and FrontDog, and RangeSlv
    and LoDog, turn against each other was not checked this time: their mates are switched off in 2H, the mode
    SolidWorks is showing, and are checked when an Update works in a mode that has them on.* A fact, not a problem:
    nothing is asked of the user. ``""`` with none."""
    names = [str(n) for n in getattr(result, "senses_unread", ()) or () if str(n)]
    if not names:
        return ""
    pairs = []
    for name in names:
        mate = _recorded_mate(update, name)
        gears = [g for g in getattr(mate, "gears", ()) or () if g] if mate is not None else []
        pairs.append(f"{gears[0]} and {gears[1]}" if len(gears) == 2 else name)
    shown = pairs[:UNREAD_PAIRS]
    if len(pairs) > UNREAD_PAIRS:
        rest = len(pairs) - UNREAD_PAIRS
        shown.append(f"{rest} more pair{'' if rest == 1 else 's'}")
    config = getattr(result, "configuration", "")
    where = f"in {config}, the mode SolidWorks is showing" if config else "in the mode SolidWorks is showing"
    if len(pairs) == 1:
        return (f"Which way {shown[0]} turn against each other was not checked this time: its mate is switched off "
                f"{where}, and is checked when an Update works in a mode that has it on.")
    who = ", ".join(shown[:-1]) + ", and " + shown[-1]       # each pair holds an "and", so commas set them apart
    return (f"Which way {who}, turn against each other was not checked this time: their mates are switched off "
            f"{where}, and are checked when an Update works in a mode that has them on.")


def mode_update_lines(update, result) -> List[str]:
    """After an Update with modes, each a whole sentence: :func:`_mode_pieces`' (*Moved RangeSlv in 4L to 66.5 mm
    along Rear.*, …) then :func:`_mode_after`'s. :func:`gearbox_update_status` folds the pieces into its *Updated
    SolidWorks: …* list and adds the rest after it. ``[]`` for a gearbox with no modes."""
    if not getattr(result, "configuration", "") and not _configurations_of(update):
        return []
    pieces = _mode_pieces(update, result)
    return ([_sentence(p[:1].upper() + p[1:]) for p in pieces]
            + _mode_after(update, result, changed=bool(pieces or result.changed or result.placed)))


def _mode_report(report, mode: str):
    for entry in getattr(report, "modes", ()) or ():
        if str(entry.name).casefold() == str(mode).casefold():
            return entry
    return None


FREE = "turns freely"        # a member a mode leaves free (J16): never "0 rpm"


def _engaged_sentence(entry) -> str:
    """What a mode couples, from its ``ModeReport``: *In 4H, RangeSlv engages InDog and ModeSlv engages FrontDog.*;
    *In N, no sleeve engages a dog.*; a listed mesh a slide takes out of mesh, *…; G4 and G5 are out of mesh.*; the
    implicit mode of sliders with no Modes rows, *With every slider at its position 0, …*. How a coupled pair turns
    is never said here (W8-INTERFACES §9.3: it follows each coupling's own sense)."""
    where = f"In {entry.name}" if entry.name else "With every slider at its position 0"
    engaged = [(s, d) for s, d in entry.engaged if s and d]
    said = _and(f"{s} engages {d}" for s, d in engaged) if engaged else "no sleeve engages a dog"
    out = [f"{a} and {b}" for a, b in entry.out_of_mesh if a and b]
    if out:
        said += "; " + "; ".join(f"{pair} are out of mesh" for pair in out)
    return f"{where}, {said}."


def _mode_line(spec, entry) -> str:
    """A mode's speeds and ratio, from its ``ModeReport`` (B's one home of a mode's ratio: ``ratio``, ``ratio_why``,
    ``driven``): *4L: Rear 375 rpm · Front 375 rpm · 4.000 : 1*; an output the mode does not drive, *2H: Rear 1500
    rpm · Front not driven · 1.000 : 1*; no output turning, *N: neutral — Rear, FrontDrv, Idler and Front turn
    freely.* (every shaft the mode leaves free, not held, in Shafts-sheet order). The implicit mode of sliders with
    no Modes rows has no name, so its line starts at the speeds."""
    name = f"{entry.name}: " if entry.name else ""
    motion = entry.motion
    if entry.ratio_why == "neutral":
        held = _held_members(spec) | set(getattr(motion, "held", None) or {})
        free = [s.id for s in spec.shafts if motion.speeds.get(s.id) is None and s.id not in held]
        one = len(free) == 1
        rest = f" — {_and(free)} turn{'s' if one else ''} freely" if free else ""
        return f"{name}{'neutral' if name else 'Neutral'}{rest}."
    parts = []
    for out, ratio in (entry.driven or {}).items():
        speed = motion.speeds.get(out)
        parts.append(f"{out} {_n(abs(float(speed)), 1)}{NBSP}rpm" if ratio is not None and speed is not None
                     else f"{out} not driven")
    if entry.ratio is not None:
        parts.append(f"{entry.ratio:.3f} : 1")
    elif entry.ratio_why:
        parts.append(entry.ratio_why)
    return name + " · ".join(parts)


def mode_speed_lines(spec, report, mode: str) -> Tuple[List[str], str]:
    """The Speeds panel at ``mode`` (a ``checks.ModeReport`` of ``report.modes``, its name compared ignoring case):
    the mode's speeds and ratio (:func:`_mode_line`), what it couples (:func:`_engaged_sentence`), then one line per
    shaft from that mode's ``motion`` as :func:`workbook_speed_lines` gives them — a member the mode leaves free
    reading *Front  turns freely* (J16), a held member *held still*, an output that also drives onward *Rear  1500.0
    rpm anticlockwise · 10.00 N·m, shared with FrontDrv (the share depends on the loads)* and each shaft past it
    *… · — (past a split)* (J17: ``Motion.shared``, ``past_split``) — and the readout, as
    :func:`workbook_speed_lines`'. ``([], "")`` for a mode the report does not have."""
    entry = _mode_report(report, mode)
    if entry is None:
        return [], ""
    lines, readout = _speed_lines(spec, entry.motion, free=FREE)
    if entry.motion.later:
        return lines, readout
    return [_mode_line(spec, entry), _engaged_sentence(entry)] + lines, readout



# -- W9a package B: the user's work in a built assembly (ISSUE-1-PLAN §2.1 items 5, 6 and 8, K4, K5) ----------------
#
# The record keeps what the last Update read of the user's work (schema 7, ``store.UserWorkEntry``); planning decides
# from it what a press would do (``workbook.update.user_work_ahead``, the worker's own judgement) and what a Build
# again… leaves behind (``update.stays_behind``); these word it, each with the time it was read. The inventory is what
# the press read — the user's components, mates and the features in the app's parts — never called all of the user's
# work: assembly features (a cut, a pattern) are not read (W9A-INTERFACES §5).

USER_NAMED = 3       # components named in a sentence about the user's work; more are counted


def read_time(stamp: str) -> str:
    """A record's UTC stamp (``store.now()``) as the local clock reads it: *14:02* today, *14:02 on 2026-11-15*
    another day; the stamp itself when it does not read."""
    import calendar
    import time
    try:
        then = time.localtime(calendar.timegm(time.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")))
    except (TypeError, ValueError, OverflowError):
        return stamp or "an earlier press"
    today = time.localtime()
    if (then.tm_year, then.tm_yday) == (today.tm_year, today.tm_yday):
        return time.strftime("%H:%M", then)
    return time.strftime("%H:%M on %Y-%m-%d", then)


def _yours(components: Sequence[str], mates: int = 0, features: Sequence[str] = ()) -> List[str]:
    """``["Sprocket-1", "Chain-1", "6 mates"]``: up to :data:`USER_NAMED` components by name, the rest counted, then
    the mates counted, then each feature named (*Keyway in Gear_m1.25_N17*)."""
    names = list(dict.fromkeys(c for c in components if c))
    out = names[:USER_NAMED]
    if len(names) > USER_NAMED:
        more = len(names) - USER_NAMED
        out.append(f"{more} other component{'' if more == 1 else 's'}")
    if mates:
        out.append(_plural(mates, "mate"))
    return out + list(features)


def _mate_words(names: Sequence[str], other: bool = False) -> List[str]:
    """The user's mates in a list of their work: one by its name, more counted (*6 mates*, *2 other mates* after
    some were named)."""
    names = [n for n in names if n]
    if len(names) == 1:
        return names
    return [_plural(len(names), "other mate" if other else "mate")] if names else []


def _stem_of_file(name: str) -> str:
    """``Gear_m1.25_N17.SLDPRT`` -> ``Gear_m1.25_N17``."""
    return _stem(name)


def _feature_words(features) -> List[str]:
    """*Keyway in Gear_m1.25_N17*, or *Keyway and Groove in Gear_m1.25_N17* for several in one part, for
    ``swbuild.UserFeature`` / ``store.UserFeatureEntry`` items, parts in the order first met."""
    by: Dict[str, List[str]] = {}
    for f in features:
        by.setdefault(_stem(f.path), []).append(f.name)
    return [f"{_and(names)} in {stem}" for stem, names in by.items()]


def _features_list(groups: Sequence[str]) -> str:
    """Feature groups by part (:func:`_feature_words`) in one list: each part's own *and* kept apart from the list's,
    by commas and a last *, and* when there are several parts."""
    groups = list(groups)
    if len(groups) <= 1:
        return "".join(groups)
    return ", ".join(groups[:-1]) + ", and " + groups[-1]


def _clauses(clauses: Sequence[str]) -> str:
    """Clauses of one sentence: *a and b*, or *a, b, and c* (long clauses, the last after a comma)."""
    clauses = list(clauses)
    if len(clauses) > 2:
        return ", ".join(clauses[:-1]) + ", and " + clauses[-1]
    return " and ".join(clauses)


# SolidWorks 2024's What's Wrong box in the app's Update (measured, d7cbcda): with something of the user's in error it
# shows for some seconds, blocks nothing and goes by itself, and the Update completes; 2026 shows none. The app leaves
# it alone and changes no setting (the coordinator's ruling); these say so, once, where the version is measured to
# show it (``swbuild.whats_wrong_shows_in_update``), so the user is not surprised.
WHATS_WRONG_AHEAD = ("SolidWorks may show its What's Wrong box for up to half a minute during the Update: leave it "
                     "alone, it closes by itself, and the Update carries on.")
WHATS_WRONG_AFTER = ("SolidWorks may have shown its What's Wrong box for up to half a minute during the Update; nothing "
                     "in it needed answering.")
# Measured on 2024: 22 to 23 s on a gearbox with modes, 3 to 5 s on a plain one (W9A-CLOSE-2024-REVIEW.md); what a
# person pressing its buttons mid-Update does was not measured, so the sentence asks them to leave it.


def whats_wrong_shows(revision: Sequence[int]) -> bool:
    """Whether the SolidWorks of ``revision`` is measured to show What's Wrong during the app's Update when something
    of the user's is in error (``swbuild.whats_wrong_shows_in_update`` True); False where it does not, or where
    unmeasured, or the revision is not known."""
    from . import swbuild
    shows = getattr(swbuild, "whats_wrong_shows_in_update", None)
    if shows is None or not revision:
        return False
    return shows(tuple(int(n) for n in revision)) is True


def _users_in_error(result) -> bool:
    """Whether an Update's result has something of the user's in error, before or after it changed anything."""
    work = getattr(result, "user_work", None)
    return bool(getattr(result, "user_in_error", None) or getattr(result, "user_features_in_error", None)
                or getattr(result, "rebuild_from_user_alone", None) or (work is not None and work.in_error))


def _prediction(ahead, at: str, known: Sequence[str] = ()) -> Tuple[str, bool]:
    """What the worker's judgement on the recorded inventory says the next press does with it (or, red, that it
    would refuse), with the time read; ``("", True)`` with nothing to say. ``known``: refusal sentences already said
    (a recorded refusal), said again only as *for the same reason*, never in full twice."""
    entry = ahead.entry
    if ahead.problems:
        new = [p.sentence for p in ahead.problems if p.sentence and p.sentence not in known]
        again = any(p.sentence in known for p in ahead.problems)
        if not new:
            return f"As read at {at}, the next press would stop for the same reason.", False
        said = " ".join(_sentence(s) for s in new)
        also = " for the same reason and" if again else ""
        return (f"As read at {at}, the next press would stop{also} before changing anything: {said} It reads your "
                "work in SolidWorks again when pressed."), False
    clauses: List[str] = []
    followed = list(ahead.followed)
    if followed:
        clauses.append(f"rebuilds your {_and(_feature_words(followed))} after the app's features")
    carried: List[str] = []
    said: List[str] = []                             # the user's mates already named
    for gear, held in ahead.carried:
        components = [c for c, _ in held]
        locks = list(dict.fromkeys(lock for _, ls in held for lock in ls))
        carried += components
        said += locks
        body = _and(_bodies([gear], {}))
        clauses.append(f"moves your {_and(components)} with {body}, which your {_and(locks)} "
                       f"{'holds' if len(locks) == 1 else 'hold'} {'it' if len(components) == 1 else 'them'} to")
    touched = {m.name: [n for w, n in m.touches if w == "app"] for m in entry.mates}
    for bodies, mates in ahead.unread_ties:
        # The train is named by the first of its bodies the user's mates are on, as the worker's tie sentence is;
        # its mates by name up to USER_NAMED, else counted (the demonstration's footer listed eight).
        on = [b for b in bodies if any(b in touched.get(m, ()) for m in mates)] or list(bodies)
        said += list(mates)
        train = f"{_and(_bodies(on[:1], {}))}'s train"
        whose = (f"your {_and(mates)} {'leaves' if len(mates) == 1 else 'leave'} {train}" if len(mates) <= USER_NAMED
                 else f"the {len(mates)} mates of yours on {train} leave it")
        clauses.append(f"asks SolidWorks, when pressed, whether {whose} free to turn (if not, it changes nothing and "
                       "names the mates to suppress)")
    others = [m.name for m in entry.mates if m.name not in said]
    rest = _yours([c.name for c in entry.components if c.name not in carried], 0, _mate_words(others, other=bool(said)))
    left = _feature_words([f for f in entry.features if not any(f.path == g.path and f.name == g.name for g in followed)])
    if left and not any(" and " in group for group in left):
        rest, left = rest + left, []                 # each part's one feature: one list
    if rest or left:
        # Several features of one part in a clause of their own after the rest (re-check R2: never "… 8 mates and
        # Keyway and Groove in …").
        one = len(rest) + len(left) == 1 and len(others) < 2
        if rest and left:
            clauses.append(f"leaves your {_and(rest)} as {'it is' if len(rest) == 1 and len(others) < 2 else 'they are'}"
                           f", and your {_features_list(left)} too")
        else:
            clauses.append(f"leaves your {_features_list(left) if left else _and(rest)} "
                           f"{'as it is' if one and not (left and ' and ' in left[0]) else 'as they are'}")
    text = f"As read at {at}, Update SolidWorks {_clauses(clauses)}." if clauses else ""
    work_errors = ([m.name for m in entry.mates if m.code and m.code != -1]
                   + [c.name for c in entry.components if c.code and c.code != -1]
                   + _feature_words([f for f in entry.features if f.code and f.code != -1]))
    if work_errors:
        one = len(work_errors) == 1
        text = _joined(text, f"Your {_and(work_errors)} {'was' if one else 'were'} already in error in SolidWorks "
                             "then.")
        if whats_wrong_shows(entry.revision):
            text = _joined(text, WHATS_WRONG_AHEAD)
    return text, True


def user_work_line(ahead) -> Tuple[str, bool]:
    """The footer's sentence before the press on what Update would do with the user's work in the assembly as it was
    last read (``workbook.update.UserWorkAhead``; K4), and whether all is well; ``("", True)`` with nothing to say.

    A press that refused over the user's work is said as recorded, with its time: *Update SolidWorks refused at
    14:02, before changing anything: … The next press reads your work in SolidWorks again, and refuses again unless
    that has been dealt with.* (red). Once the workbook has changed since, *… The workbook has changed since, and the
    next press reads your work in SolidWorks again.*, then the prediction, in its own colour. The prediction is the
    worker's own judgement on the inventory: a refusal it foresees, red, *As read at 14:02, Update SolidWorks would
    stop before changing anything: …*; else *As read at 14:02, Update SolidWorks rebuilds your Keyway in
    Gear_m1.25_N17 after the app's features, moves your Sprocket-1 with Sun, which your Lock3 holds it to, and leaves
    your Chain-1 and 6 mates as they are.*, and what of the user's was already in error then."""
    if ahead is None:
        return "", True
    at = read_time(ahead.entry.read_at)
    if ahead.refused:
        recorded = [p.sentence for p in ahead.refused if p.sentence]
        said = " ".join(_sentence(s) for s in recorded)
        when = read_time(getattr(ahead.entry, "refused_at", "") or ahead.entry.read_at)
        text = f"Update SolidWorks refused at {when}, before changing anything: {said}"
        if not ahead.changed_since:
            return (text + " The next press reads your work in SolidWorks again, and refuses again unless that has "
                           "been dealt with."), False
        still = list(getattr(ahead, "still", ()) or ())
        if still:
            # Re-check R1: a value the user typed in SolidWorks that the changed workbook still does not ask.
            asks = _and(f"{now} for {v.name} in {_stem_of_file(v.document)}"
                        + (f" in {v.mode}" if v.mode else "") + f", where SolidWorks held {v.live}" for v, now in still)
            text += (f" The workbook has changed since, but it still asks {asks}, so that refusal stands unless "
                     f"{'it has' if len(still) == 1 else 'they have'} been set in SolidWorks since.")
        else:
            text += " The workbook has changed since, and the next press reads your work in SolidWorks again."
        then, ok = _prediction(ahead, at, known=recorded)
        return _joined(text, then), ok and not still
    return _prediction(ahead, at)


def _stays_text(stays, again, lead: str = "As read at") -> str:
    """The clause of what stays behind: from the record's inventory, with its time and *nor anything added since*;
    with nothing on record, the same without a time. ``lead`` capitalised or not, as it follows."""
    name = getattr(again, "name", "") or "the new revision"
    old = _file(stays.assembly) if stays.assembly else "the old assembly"
    entry = stays.entry
    if entry is None or not (stays.components or stays.mates or stays.left or stays.kept):
        start = "Anything" if lead[:1].isupper() else "anything"
        return (f"{start} you added to {old} in SolidWorks (components, mates, and features in parts this revision "
                f"makes new) stays there, and {name} has none of it.")
    part_of = dict(getattr(again, "part_of", {}) or {})
    from . import store
    pieces = []
    items = _yours(stays.components, 0, _mate_words(stays.mates))
    if items:
        one = len(items) == 1 and len(stays.mates) < 2
        pieces.append(f"your {_and(items)} {'stays' if one else 'stay'} in {old}")
    by_part: Dict[str, Tuple[List[str], Tuple[str, ...]]] = {}
    for feature, path, gears in stays.left:
        by_part.setdefault(path, ([], gears))[0].append(feature)
    for path, (features, gears) in by_part.items():
        replacing = [g for g in gears if g in part_of and not store.same_path(part_of[g], path)]
        why = (f"which {_and(replacing)}'s new part replaces" if replacing
               else f"which {name} does not use")
        pieces.append(f"your {_and(features)} {'stays' if len(features) == 1 else 'stay'} in {_stem(path)}, {why}")
    text = ""
    if pieces:
        single = len(pieces) == 1 and ((items and len(items) == 1 and len(stays.mates) < 2)
                                       or (not items and len(stays.left) == 1))
        joined = pieces[0] if len(pieces) == 1 else f"{', '.join(pieces[:-1])}, and {pieces[-1]}"
        text = (f"{lead} {read_time(entry.read_at)}, {joined}; {name} has none of {'it' if single else 'them'}, nor "
                "anything added since.")
    else:
        text = f"{'Anything' if lead[:1].isupper() else 'anything'} added to {old} since {read_time(entry.read_at)} " \
               f"stays there, and {name} has none of it."
    kept: Dict[str, List[str]] = {}
    for feature, path in stays.kept:
        kept.setdefault(path, []).append(feature)
    for path, features in kept.items():
        one = len(features) == 1
        text = _joined(text, f"Your {_and(features)} in {_stem(path)} {'comes' if one else 'come'} with that part, "
                             f"which {name} reuses.")
    return text


def stays_behind_sentence(stays, again) -> str:
    """The Build again? question's clause on what of the user's stays behind (K5 until W9d; the coordinator's ruling
    on package B's review, point 4), from ``workbook.update.StaysBehind``: with an inventory on record, its items
    with its time, *As read at 14:02, your Sprocket-1, Chain-1 and 6 mates stay in RangeBox.SLDASM, and your Keyway
    stays in Gear_m1.25_N17, which Sun's new part replaces; RangeBox_r2 has none of them, nor anything added
    since.*, and a feature in a part the new revision reuses comes with it, *Your Groove in Sleeve_m1.25_N17 comes
    with that part, which RangeBox_r2 reuses.*; with none, without a time, *Anything you added to RangeBox.SLDASM in
    SolidWorks (components, mates, and features in parts this revision makes new) stays there, and RangeBox_r2 has
    none of it.* ``""`` with no assembly on record."""
    return "" if stays is None else _stays_text(stays, again)


def stayed_behind_status(stays, result, again, old_path: str = "") -> str:
    """After a Build again…: what of the user's stayed in the old assembly, as the build job read it first
    (``GearboxResult.old_user_work``) — *Your Sprocket-1, Chain-1 and 6 mates stay in RangeBox.SLDASM, as read when
    this build began; RangeBox_r2 has none of them.* — with the features the record says stay in parts made new; or,
    when that assembly was not open in SolidWorks, or the read raised, what the record held with its time (or, with
    nothing on record, that anything added there stays there). ``old_path`` the old assembly (``OldAssembly.path``)."""
    from .swbuild import OLD_NOT_OPEN
    name = getattr(again, "name", "") or "the new revision"
    path = (stays.assembly if stays is not None else "") or old_path
    old = _file(path) if path else "the old assembly"
    work = getattr(result, "old_user_work", None)
    why = getattr(result, "old_read", "") or ""
    if stays is None:
        from .workbook.update import StaysBehind
        stays = StaysBehind(None, path)
    if work is not None:
        items = _yours([c.name for c in work.components], 0, _mate_words([m.name for m in work.mates]))
        features = ""
        if stays.entry is not None and stays.left:
            features = _stays_text(type(stays)(stays.entry, path, (), (), stays.left, ()), again)
        if not items:
            return features
        one = len(items) == 1 and len(work.mates) < 2
        lead = (f"Your {_and(items)} {'stays' if one else 'stay'} in {old}, as read when this build began; {name} "
                f"has none of {'it' if one else 'them'}.")
        return _joined(lead, features)
    if why == OLD_NOT_OPEN:
        return f"{old} was not open in SolidWorks, so it was not read again; {_stays_text(stays, again, 'as read at')}"
    return _joined(_sentence(why) if why else "", _stays_text(stays, again))


def _users_alone(path: str, result) -> bool:
    """Whether a part whose rebuild SolidWorks reported in error is in error through the user's own features alone:
    the Update went on (no failure names it, or the status would have said it as stopped) and a user feature in that
    part reads in error after it (``result.user_features_in_error``), so the error is not laid to the app (K3, the
    demonstration's ruling)."""
    from . import store
    if getattr(result, "failures", None):
        return False
    return any(store.same_path(f.path, path) or _file(f.path).lower() == _file(path).lower()
               for f in getattr(result, "user_features_in_error", ()) or ())


def _rebuild_from_user(update, result) -> List[str]:
    """The assembly's rebuild reported in error from the user's own work alone (``result.rebuild_from_user_alone``;
    the worker went on, ``rebuilt`` staying False as SolidWorks answered): *SolidWorks reports an error rebuilding
    RangeBox.SLDASM, from your own work alone: nothing of the app's is in error, so the Update was made.* What of the
    user's is in error is named by the sentences after it; anything they do not name, here."""
    alone = [str(n) for n in getattr(result, "rebuild_from_user_alone", ()) or () if n]
    if not alone or getattr(result, "rebuilt", True):
        return []
    assembly = _file(update.assembly) if getattr(update, "assembly", "") else "the assembly"
    named = {name for _, name in getattr(result, "user_in_error", ()) or ()}
    named |= {f"{f.name} in {_file(f.path)}".lower() for f in getattr(result, "user_features_in_error", ()) or ()}
    rest = []
    for item in alone:
        if item in named or item.lower() in named:
            continue
        head, sep, tail = item.rpartition(" in ")
        rest.append(f"{head} in {_stem(tail)}" if sep else item)
    yours = f" (your {_and(rest)})" if rest else ""
    return [f"SolidWorks reports an error rebuilding {assembly}, from your own work alone{yours}: nothing of the "
            "app's is in error, so the Update was made."]


def _expression_words(name: str, expression: str, evaluated: str) -> Tuple[str, bool]:
    """A part global's value as the workbook shows it, and whether its cell is blank, in package A's
    ``ValueEdit.blank`` wording (``swbuild._blank_meaning``): a Bore of 0 is *no bore*; an expression that is no number
    is the default a blank cell means, *0.375 (from its blank cell, 0.3 × Module)* — its evaluation where known, never
    the raw equation; a number as it is. ``evaluated``: what SolidWorks evaluated it to (``ValueSet.was``/``now``)."""
    from .gears.spur import BORE as BORE_GLOBAL
    from .swbuild import _literal
    literal = _literal(expression) if expression else _literal(evaluated)
    if name == BORE_GLOBAL and literal == 0.0:
        return "no bore", True
    if expression and literal is None:
        default = expression.replace('"', "").replace(" * ", " × ")
        number = evaluated if _literal(evaluated) is not None else ""
        return (f"{number} (from its blank cell, {default})" if number else f"the default of its blank cell, "
                f"{default}"), True
    text = evaluated if evaluated and _literal(evaluated) is not None else (
        f"{float(literal):.6g}" if literal is not None else evaluated)
    return text, False


def _value_under(update, value) -> Tuple[str, str, str]:
    """``(what it was, what it is, how to have it back)`` for one global this Update set under a user feature
    (``swbuild.ValueSet``), as the workbook shows it: the expressions from the plan's document (what the record says
    the file held, and what it sets now), so a blank cell is said as blank — *clear Gears!J2 again* — and an
    equation never raw. ``how`` is ``""`` with no cell."""
    from . import store
    docs = list(getattr(update, "parts", ()) or ()) + [d for d in [getattr(update, "layout", None)] if d is not None] \
        + list(getattr(update, "carriers", ()) or ())
    doc = next((d for d in docs if store.same_path(d.path, value.path)), None)
    old = dict(getattr(doc, "recorded", None) or ()).get(value.name, "") if doc is not None else ""
    new = next((v.expression_for("degrees") for v in getattr(doc, "variables", ()) or () if v.name == value.name),
               "") if doc is not None else ""
    was, was_blank = _expression_words(value.name, old, value.was)
    now, _ = _expression_words(value.name, new, value.now)
    how = ""
    if value.cell and (was_blank or value.was):
        how = f"clear {value.cell} again" if was_blank else f"type {was} in {value.cell} again"
    return was, now, how


def _user_feature_sentences(result, update=None) -> List[str]:
    """K3 after the demonstration's ruling: each user feature SolidWorks rebuilt in error, named as the user's.
    One already in error before this Update changed anything, *Your Keyway in Gear_m1.25_N17 was in error in
    SolidWorks before this Update changed anything, and still is.*; one newly in error with what this Update set in
    its part (``result.values_under``) and what the user can do: *Your Keyway in Gear_m1.25_N17 is in error in
    SolidWorks now, after this Update set Bore Diameter 8 to 14 (Gears!J2) in that part: change your Keyway to fit,
    or type 8 in Gears!J2 again.* (*clear Gears!J2 again* for a cell that was blank; a value said as the workbook shows
    it, ``update``'s documents given). Features of one part with the same story are said together."""
    features = list(getattr(result, "user_features_in_error", ()) or ())
    was = getattr(result, "user_feature_was_in_error", None)
    under = getattr(result, "values_under", None)
    groups: Dict[Tuple[str, bool, tuple], List[str]] = {}
    for f in features:
        before = bool(was(f)) if callable(was) else False
        values = tuple(under(f)) if callable(under) and not before else ()
        groups.setdefault((_stem(f.path), before, values), []).append(f.name)
    out = []
    for (stem, before, values), names in groups.items():
        one = len(names) == 1
        yours = f"{_and(names)} in {stem}"
        if before:
            out.append(f"Your {yours} {'was' if one else 'were'} in error in SolidWorks before this Update changed "
                       f"anything, and still {'is' if one else 'are'}.")
            continue
        text = f"Your {yours} {'is' if one else 'are'} in error in SolidWorks now"
        if values:
            said = [(v, *_value_under(update, v)) for v in values]
            set_ = _and((f"{v.name} {w} to {n}" if w else f"{v.name} to {n}") + (f" ({v.cell})" if v.cell else "")
                        for v, w, n, _ in said)
            back = _and(how for _, _, _, how in said if how)
            text += (f", after this Update set {set_} in that part: change your {_and(names)} to fit"
                     + (f", or {back}" if back else "") + ".")
        else:
            text += (f", rebuilt after the app's features: change your {_and(names)} to fit "
                     f"{'it' if one else 'them'}.")
        out.append(text)
    return out


def _user_after(update, result) -> List[str]:
    """After an Update, what it did with and found of the user's work (K2, K3; W9A-INTERFACES §2.1), each a whole
    sentence: each of the user's components it put with its gear by route (c1) (*Your Sprocket-1 went with Sun in H,
    N and L, which your locks hold it to.*), each component found by its part under another name (K1), each user
    feature SolidWorks rebuilt into an error (*SolidWorks rebuilt your Keyway in Gear_m1.25_N17 after the app's
    features, and it is in error.*), and each mate or component of the user's in error after it, with its mode —
    those already in error before it changed anything told apart, so nothing is laid to the Update that it did not
    do."""
    out: List[str] = []
    every = [str(c) for c in getattr(getattr(update, "motion", None), "configurations", ()) or ()]
    by: Dict[Tuple[str, str], List[str]] = {}
    for component, gear, configuration in getattr(result, "carried", ()) or ():
        modes = by.setdefault((component, gear), [])
        if configuration and configuration not in modes:
            modes.append(configuration)
    for (component, gear), modes in by.items():
        where = ""
        if modes:
            where = " in every mode" if len(every) > 1 and sorted(modes) == sorted(every) else f" in {_and(modes)}"
        out.append(f"Your {component} went with {_and(_bodies([gear], {}))}{where}, which your locks hold it to.")
    for gear, before, found in getattr(result, "renamed", ()) or ():
        out.append(f"{gear}'s component {before} is named {found} in SolidWorks now; it was found by its part, and the "
                   "record names it so.")
    out.extend(_user_feature_sentences(result, update))
    work = getattr(result, "user_work", None)
    before = set(work.in_error) if work is not None else set()
    named: Dict[str, List[str]] = {}
    for mode, name in getattr(result, "user_in_error", ()) or ():
        modes = named.setdefault(name, [])
        if mode and mode not in modes:
            modes.append(mode)
    for already in (True, False):
        names = [name for name in named if (name in before) == already]
        if not names:
            continue
        parts = [f"{name} in {_and(named[name])}" if named[name] else name for name in names]
        one = len(names) == 1
        if already:
            # Re-check R3: before the change only the mode showing was read (W9A-INTERFACES §5), so that is what is
            # said of before, and the modes only of after.
            out.append(f"Your {_and(names)} {'was' if one else 'were'} in error in SolidWorks in the mode showing "
                       f"before this Update changed anything; after it, {_and(parts)} {'is' if one else 'are'} in "
                       "error.")
        else:
            out.append(f"Your {_and(parts)} {'is' if one else 'are'} in error in SolidWorks now.")
    return out


# -- W9c: Update adds, removes and re-mates in place (ISSUE-1-PLAN §2.1 "W9c", K6, §2.4; W9C-INTERFACES §5, §6) ----

# What each in-place step does, as the sentences name a step a finding gates (``swbuild.in_place_gates``).
IN_PLACE_STEP_WORDS = {
    "remove a gear": "take a gear out of the assembly",
    "add a gear": "insert a gear into the assembly and mate it",
    "make a mate": "make a gear mate in an assembly with modes again and set its flag in each mode",
    "make a coupling": "make a coupling or sliding mesh between gears already in the assembly and set its flag in "
                       "each mode",
    "bands in place": "give a built sleeve its bands in its own part",
    "suppress the relief": "suppress a sleeve's relief to take its bands away, or turn it back on to give them back",
    "add a mode": "add a mode's configuration to the assembly",
    "remove a mode": "delete a mode's configuration from the assembly",
}


# Each in-place finding's step, by the finding's name less its ``_ON_<year>`` (W9C-INTERFACES §8).
_STEP_OF_FINDING = (("COMPONENT_DELETE", "remove a gear"), ("UPDATE_INSERTS_A_GEAR", "add a gear"),
                    ("UPDATE_MAKES_MATES_WITH_MODES", "make a mate"),
                    ("UPDATE_MAKES_A_NEW_COUPLING", "make a coupling"), ("UPDATE_BANDS_IN_PLACE", "bands in place"),
                    ("UPDATE_SUPPRESSES_THE_RELIEF", "suppress the relief"), ("UPDATE_ADDS_A_MODE", "add a mode"),
                    ("UPDATE_REMOVES_A_MODE", "remove a mode"))


def _step_of(finding: str) -> str:
    return next((step for prefix, step in _STEP_OF_FINDING if finding.startswith(prefix)), "")


def _version_of(finding: str) -> str:
    """``SolidWorks 2026`` from ``UPDATE_INSERTS_A_GEAR_ON_2026``; ``the SolidWorks it runs on`` when the version is
    not known (``…_ON_?``)."""
    year = finding.rsplit("_ON_", 1)[-1] if "_ON_" in finding else ""
    return f"SolidWorks {year}" if year.isdigit() else "the SolidWorks it runs on"


def in_place_gate_sentence(steps: Sequence[str], findings_: Sequence[str]) -> str:
    """The steps a finding gates that are not settled, in one sentence: *Update SolidWorks would insert a gear into
    the assembly and mate it, which Gear Generator has not yet been shown to do on SolidWorks 2026
    (findings.UPDATE_INSERTS_A_GEAR_ON_2026), so the press changes nothing; Build again… makes the new revision
    instead.* A version not known is said *the SolidWorks it runs on*, the finding ``…_ON_<year>``."""
    names = [n.replace("_ON_?", "_ON_<year>") for n in dict.fromkeys(findings_)]
    what = _and(IN_PLACE_STEP_WORDS.get(step, step) for step in dict.fromkeys(steps))
    return (f"Update SolidWorks would {what}, which Gear Generator has not yet been shown to do on "
            f"{_version_of(list(findings_)[0])} ({_and('findings.' + n for n in names)}), so the press changes "
            "nothing; Build again… makes the new revision instead.")


def in_place_pieces(update) -> List[str]:
    """What an Update will make or take away in place, before the press (``UpdatePlan.in_place``; W9c), each a piece
    of :func:`update_summary`'s sentence: *add Hub on Output (a new part, Hub_m1.25_N17), as its anchor with RangeSlv
    splined to it*, *take G4 out with its 3 mates*, *give RangeSlv its bands in Sleeve_m1.25_N17*, *take RangeSlv's
    bands away (its Relief suppressed)*, *make ModeSlv engages LoDog, on in 2H*, *add the mode 4X*, *delete the mode L*
    (*…, so M becomes the first mode on record*)."""
    ip = getattr(update, "in_place", None)
    if not ip:
        return []
    pieces: List[str] = []
    for gone in ip.removed:
        n = len(gone.mates)
        pieces.append(f"take {gone.gear} out with its {_plural(n, 'mate')}" if n else f"take {gone.gear} out")
    for added in ip.added:
        mates = [op for op in added.ops if type(op).__name__ == "Mate"]
        anchor = next((m for m in mates if m.kind == "coincident"), None)
        shaft = anchor.b.split(":", 1)[-1][:-len(" Axis")] if anchor is not None and anchor.b.endswith(" Axis") else ""
        part = f"a new part, {_stem(added.part)}" if added.build is not None else f"its part {_stem(added.part)}"
        text = f"add {added.gear}{' on ' + shaft if shaft else ''} ({part})"
        splined = [m.name for m in mates if m.kind == "gear" and m.name.endswith(f" splined to {added.gear}")]
        if splined:
            sleeves = [m.split(" splined to ", 1)[0] for m in splined]
            text += f", as its shaft's anchor with {_and(sleeves)} splined to it"
        pieces.append(text)
    for band in ip.bands:
        if band.add and getattr(band, "back", False):
            pieces.append(f"give {band.gear} its bands back in {_stem(band.part)} (its Relief turned back on)")
        elif band.add:
            pieces.append(f"give {band.gear} its bands in {_stem(band.part)}")
        else:
            pieces.append(f"take {band.gear}'s bands away in {_stem(band.part)} (its Relief suppressed)")
    for new in ip.new_mates:
        pieces.append(f"make {new.op.name}, on in {_and(list(new.on))}")
    if ip.modes_added:
        one = len(ip.modes_added) == 1
        pieces.append(f"add the {'mode' if one else 'modes'} {_and(list(ip.modes_added))}, "
                      f"{'a copy' if one else 'each a copy'} of the mode showing in SolidWorks when you press (your "
                      "items there take that mode's state)")
    if ip.modes_removed:
        text = f"delete the {'mode' if len(ip.modes_removed) == 1 else 'modes'} {_and(list(ip.modes_removed))}"
        if ip.first_mode:
            text += f", so {ip.first_mode} becomes the first mode on record"
        pieces.append(text)
    return pieces


def new_part_on_disk_sentence(gear: str, path: str) -> str:
    """An added gear's new part whose file is already on disk and on no record (W9c; the worker refuses rather than
    build over it): *Hub_m1.25_N17.SLDPRT is already on disk though nothing on record holds it (a press that stopped
    part way may have built it), so Update SolidWorks would not build Hub's new part over it: move that file away or
    delete it, then press Update SolidWorks again.*"""
    return (f"{_file(path)} is already on disk though nothing on record holds it (a press that stopped part way may "
            f"have built it), so Update SolidWorks would not build {gear}'s new part over it: move that file away or "
            "delete it, then press Update SolidWorks again.")


def in_place_line(problems, record=None, known: str = "", on_disk=()) -> Tuple[str, bool]:
    """The footer's sentence before the press on what would stop an in-place change (``workbook.update.
    in_place_ahead``; K4, no question before an Update), red; ``("", True)`` with nothing to say. Each step a finding
    gates and that is not settled for the SolidWorks the record last read (:func:`in_place_gate_sentence`), then the
    user's work on a gear to be taken out, as the worker words it, each once (``known``: the line already said)."""
    if not problems and not on_disk:
        return "", True
    gates: Dict[str, List[str]] = {}
    depends: Dict[Tuple[str, ...], List[Tuple[str, str]]] = {}
    said: List[str] = []
    from .swbuild import PROBLEM_UNSETTLED
    from .workbook.update import PROBLEM_DEPENDS
    for p in problems or ():
        subjects = tuple(getattr(p, "subjects", ()) or ())
        if p.kind == PROBLEM_UNSETTLED and subjects and _step_of(subjects[0]):
            gates.setdefault(_step_of(subjects[0]), []).append(subjects[0])
        elif p.kind == PROBLEM_DEPENDS:
            unshown = tuple(sorted({_version_of(s) for s in subjects}))
            for s in subjects:
                depends.setdefault(unshown, []).append((_step_of(s) or "", s))
        elif p.sentence and p.sentence not in known and p.sentence not in said:
            said.append(p.sentence)
    sentences = ([in_place_gate_sentence(list(gates), [n for names in gates.values() for n in names])] if gates
                 else []) + [_sentence(s) for s in said] + [new_part_on_disk_sentence(g, p) for g, p in on_disk]
    maybe = [in_place_depends_sentence(found) for found in depends.values()]
    if not sentences:
        return " ".join(maybe), True
    entry = getattr(getattr(record, "gearbox", None), "user_work", None)
    read = entry is not None and not getattr(entry, "unread", False) and entry.read_at
    lead = f"As read at {read_time(entry.read_at)}, the" if read and said else "The"
    return " ".join([f"{lead} next press would stop before changing anything: " + " ".join(sentences)] + maybe), False


def in_place_depends_sentence(found: Sequence[Tuple[str, str]]) -> str:
    """With no SolidWorks version on record, steps shown on some versions the findings know and not yet on others, in
    one sentence, neither red nor a refusal (the press reads the version first): *Whether Update SolidWorks can take a
    gear out of the assembly depends on the SolidWorks in use: Gear Generator has been shown to do so on SolidWorks
    2026, not yet on SolidWorks 2024 (findings.COMPONENT_DELETE_ROUTE_ON_2024), and the press reads which it runs on
    before it changes anything.*"""
    from .workbook.update import known_finding_revisions
    names = list(dict.fromkeys(name for _, name in found))
    unshown = sorted({_version_of(n) for n in names})
    shown = [f"SolidWorks {year}" for year, _ in known_finding_revisions() if f"SolidWorks {year}" not in unshown]
    what = _and(IN_PLACE_STEP_WORDS.get(step, step) for step in dict.fromkeys(s for s, _ in found if s))
    return (f"Whether Update SolidWorks can {what} depends on the SolidWorks in use: Gear Generator has been shown to "
            f"do so on {_and(shown)}, not yet on {_and(unshown)} ({_and('findings.' + n for n in names)}), and the "
            "press reads which it runs on before it changes anything.")


def in_place_done_pieces(update, result) -> List[str]:
    """What an Update made or took away in place, after the press (``swbuild.GearboxUpdate``'s W9c fields), each a
    piece of :func:`gearbox_update_status`'s sentence: *built Hub_m1.25_N17*, *inserted Hub as Hub-1 and mated it
    (Hub on Output Axis, Hub along Output, RangeSlv splined to Hub)*, *took G4 out (G4-1) with its 3 mates*, *gave
    RangeSlv its bands*, *took RangeSlv's bands away*, *made ModeSlv engages LoDog, on in 2H*, *made the gear mate
    G1 meshes G2 again in every mode it is on in*, *added the mode 4X*, *deleted the mode L*."""
    pieces: List[str] = []
    built = [b.saved for b in getattr(result, "built", []) or [] if getattr(b, "saved", "")]
    if built:
        pieces.append(f"built {_and(_stem(p) for p in built)}")
    deleted = list(getattr(result, "deleted", []) or [])
    if deleted:
        n = len(getattr(result, "mates_deleted", []) or [])
        what = _and(f"{g} ({name})" for g, name in deleted)
        # Ruling C6: a part no gear left uses leaves the record; its file is never deleted.
        used = {str(getattr(p, "part", "") or "").replace("/", "\\").casefold()
                for p in getattr(update, "placements", ()) or ()}
        gone = [r.part for r in getattr(getattr(update, "in_place", None), "removed", ()) or ()
                if r.gear in {g for g, _ in deleted} and r.part and r.part.replace("/", "\\").casefold() not in used]
        files = list(dict.fromkeys(_file(p) for p in gone))
        pieces.append(f"took {what} out" + (f" with {_plural(n, 'mate')}" if n else "")
                      + (f", leaving {'its part' if len(files) == 1 else 'their parts'} {_and(files)} on disk"
                         if files else ""))
    made = dict((name, tuple(on)) for name, on in getattr(result, "mates_made", []) or [])
    ip = getattr(update, "in_place", None)
    for gear, name in getattr(result, "inserted", []) or []:
        own = [op.name for a in (ip.added if ip else ()) if a.gear == gear for op in a.ops
               if type(op).__name__ == "Mate" and op.name in made]
        pieces.append(f"inserted {gear} as {name}" + (f" and mated it ({_and(own)})" if own else ""))
    coupled = [m.op.name for m in (ip.new_mates if ip else ()) if m.op.name in made]
    for name in coupled:
        on = made[name]
        pieces.append(f"made {name}" + (f", on in {_and(list(on))}" if on else ""))
    remade = list(getattr(result, "remade_in_modes", []) or [])
    if remade:
        pieces.append(f"made {_and(remade)} again, with {'its flag' if len(remade) == 1 else 'their flags'} set in "
                      "every mode")
    given = list(getattr(result, "bands_added", []) or [])
    if given:
        pieces.append(f"gave {_and(given)} {'its' if len(given) == 1 else 'their'} bands")
    taken = list(getattr(result, "bands_removed", []) or [])
    if taken:
        pieces.append(f"took {_and(f'{g}' + chr(39) + 's' for g in taken)} bands away")
    added = list(getattr(result, "modes_added", []) or [])
    if added:
        pieces.append(f"added the {'mode' if len(added) == 1 else 'modes'} {_and(added)}")
    removed = list(getattr(result, "modes_removed", []) or [])
    if removed:
        pieces.append(f"deleted the {'mode' if len(removed) == 1 else 'modes'} {_and(removed)}")
    return pieces


def in_place_after(update, result) -> List[str]:
    """The sentences after an in-place Update on the user's own states (C5) and the record's first mode (C11): *The
    new mode 4X copied the mode showing, so your Lock3 is on and your Sprocket-1 resolved there, as they are in the
    mode showing; change them in 4X if they should differ.* *Your own states in L went with it: your Lock3 was
    suppressed there, and any state of your components particular to it.* *L was the first mode on record; M is now.*"""
    out: List[str] = []
    took: Dict[str, List[str]] = {}
    for mode, item, state in getattr(result, "took_active_state", []) or []:
        took.setdefault(mode, []).append(f"your {item} {state}")
    for mode, items in took.items():
        out.append(f"The new mode {mode} copied the mode showing, so {_and(items)} there, as in the mode showing; "
                   f"change {'it' if len(items) == 1 else 'them'} in {mode} if {'it' if len(items) == 1 else 'they'} "
                   "should differ.")
    lost: Dict[str, List[str]] = {}
    for mode, mate, flag in getattr(result, "flags_lost", []) or []:
        lost.setdefault(mode, []).append(f"your {mate} was {flag} there")
    for mode in getattr(result, "modes_removed", []) or []:
        items = lost.get(mode, [])
        said = f"{_and(items)}, and so was " if items else ""
        out.append(f"Your own states in {mode} went with it: {said}any state of your components particular to it.")
    ip = getattr(update, "in_place", None)
    removed = list(getattr(result, "modes_removed", []) or [])
    if ip and ip.first_mode and removed:
        out.append(f"{removed[0]} was the first mode on record; {ip.first_mode} is now.")
    return out


# -- W9d: Build again… carries the user's work (ISSUE-1-PLAN §2.5; W9D-INTERFACES §9) ----------------------------

# The kinds of mate a carry makes again (§2.5), as the sentences and CARRY_REMAKE_KINDS word them.
CARRY_KIND_WORDS = ("coincident", "concentric", "parallel", "perpendicular", "tangent", "distance", "angle",
                    "limit distance", "limit angle", "lock", "gear")
CARRY_STANDING = ("Assembly features, display states and appearances stay behind; sub-assemblies come over rigid, "
                  "pattern instances as components of their own.")
CARRY_STANDING_NO_PATTERN = "Assembly features, display states and appearances stay behind; sub-assemblies come over rigid."
CARRY_IN_CONTEXT = "If a part of yours was made in context of {old}, it still refers to that assembly's parts."
_ENTITY_WORDS = {"face": "a face", "edge": "an edge", "vertex": "a vertex", "origin": "an origin",
                 "feature": "a feature", "plane": "a base plane", "whole": "the whole", "unread": "an entity"}
_ENTITY_PLURALS = {"face": "faces", "edge": "edges", "vertex": "vertices"}

import re as _re  # noqa: E402 - W9d's path reduction only

# A drive or share, then folders: a folder's name may hold spaces, but not a file's extension before a space or a
# punctuation mark, nor ". " or ", " (so a path is never run on into the words after a file); then a word ending in a
# backslash before a file's name (what is left of a folder the first pass stopped in; "A\B" with no file is left).
_FOLDERS = _re.compile(r"(?:[A-Za-z]:|\\\\[^\\/\s]+)[\\/]+"
                       r"(?:(?:(?!\.[A-Za-z][A-Za-z0-9]{1,5}(?:[\s.,;:)\]]|$)|[.,;] )[^\\/:*?\"<>|\r\n])+[\\/]+)*")
_LEFT = _re.compile(r"[^\s\\/:*?\"<>|()]+\\+(?=[^\s\\/:*?\"<>|()]+\.[A-Za-z][A-Za-z0-9]{1,5}\b)")


def bare_files(text: str) -> str:
    """``text`` with every Windows path reduced to its file's name (the coordinator's privacy ruling: a folder never
    goes into the record or a sentence from what the worker says, which may hold an exception's text)."""
    return _LEFT.sub("", _FOLDERS.sub("", str(text or "")))


def _a(word: str) -> str:
    return f"{'an' if word[:1].lower() in 'aeiou' else 'a'} {word}"


def _on_version(version: str) -> str:
    return f"SolidWorks {version}" if str(version).isdigit() else "the SolidWorks it runs on"


def _finding_ref(finding: str) -> str:
    return "findings." + str(finding).replace("_ON_?", "_ON_<year>")


def _unmeasured_verb(what: str, finding: str, owner: str = "") -> str:
    """What a finding not yet set would show Gear Generator doing, by §2.3's ``unmeasured`` first slot."""
    if what in CARRY_KIND_WORDS:
        return f"make {what} mates again in a new revision"
    if what in ("face", "edge", "vertex"):
        whose = f" of {owner}" if owner else ""
        after = " after its part is closed and opened again" if "SURVIVES_RELOAD" in finding else \
            " in a new revision"
        return f"find a mate's {what}{whose} again{after}"
    return {"origin": "read an origin as a mate's entity",
            "insert": "carry your work into a new revision",
            "sub-assembly": "insert a sub-assembly of yours into a new revision",
            "configuration": "insert a component in one of its file's several configurations",
            "gear mate on an app gear": "make a gear mate on an app gear again in a new revision",
            "leaf": "make a mate on a part inside a sub-assembly of yours again"}.get(
        what, f"carry what {what} needs into a new revision")


def _marks_sub(finding: str) -> bool:
    """Whether a sub-assembly finding reads that opening it marks it (settled the wrong way, not unset)."""
    from . import findings
    return finding.startswith("SUBASSEMBLY_OPEN_MARKS") and getattr(findings, finding, None) is True


def _subjects(named, n: int = 5) -> List[str]:
    return [bare_files(str(x)) for x in named.subjects] + [""] * n


def carry_named_clause(named, *, name: str = "the new revision", old: str = "the old assembly",
                       resolved: Sequence[str] = ()) -> str:
    """One item not carried, in §9.3's words, from its ``why`` and §2.3's subjects (``swbuild.CarryNamed``):
    *Concentric5 was on Sun's bore, and Sun's part is new because its Flank changed*. ``name`` the new revision,
    ``old`` the old assembly's file name; ``resolved`` the components the carry left resolved in it
    (``CarryResult.resolved_in_old``), whose lightweight state is then said in the past. No full stop: the caller ends
    it (:func:`_with_verdict`)."""
    from . import swbuild as sb
    item, why = named.item, named.why
    s = _subjects(named)
    if why == sb.WHY_KIND:
        return f"{item} is {_a(s[0] or 'kind of')} mate, which Gear Generator does not make again"
    if why == sb.WHY_UNMEASURED:
        what, finding, version, owner = s[0], s[1], s[2], s[3]
        if what == "sub-assembly" and _marks_sub(finding):
            return (f"your sub-assembly {item} is not carried: opening it to insert it marks it as changed in "
                    "SolidWorks, and Gear Generator never changes a file of yours")
        head = f"{item} is not carried" if named.what == "component" else f"{item} is not made again"
        return (f"{head}: Gear Generator has not yet been shown to {_unmeasured_verb(what, finding, owner)} on "
                f"{_on_version(version)} ({_finding_ref(finding)})")
    if why == sb.WHY_PART_NEW:
        gear, because, kind, where = s[0], s[1], s[2], s[3]
        if where == "bore":
            on = f"{gear}'s bore"
        elif where == "axis":
            on = f"a face of {gear} on its axis"
        else:
            on = f"{_ENTITY_WORDS.get(kind, 'an entity')} of {gear}"
        return f"{item} was on {on}, and {gear}'s part is new because {because or 'it changed'}"
    if why == sb.WHY_GONE:
        what, gone, owner = s[0], s[1], s[2]
        if what == "gear":
            return f"{item} was on {gone}, which {name} does not have"
        if what == "shaft":
            return f"{item} was on the layout's {gone} Axis, and {name} has no shaft {gone}"
        if owner:
            return f"{item} was on {owner}'s {gone}, which {owner}'s new part does not have"
        return f"{item} was on {gone} in an app part, which that part in {name} does not have"
    if why == sb.WHY_ASSEMBLY_FEATURE:
        return f"{item} is on {s[0]}, a feature you made in {old}, which is not carried"
    if why == sb.WHY_NOT_CARRIED:
        return f"{item} joins {s[0]}, which is not carried"
    if why == sb.WHY_UNREAD:
        cause = s[1]
        if cause == sb.CAUSE_SUPPRESSED:
            return f"{item} is on {_suppressed_where(s[2], s[3], old)}, so it could not be read and is not made again"
        if cause == sb.CAUSE_BESIDE_LIGHTWEIGHT:
            return f"{item} is on a plane of {old} itself, {_beside_light(s[2], resolved)}, so it is not made again"
        if cause == sb.CAUSE_TYPE_NOT_TAKEN:
            # The re-check of b67cdc5, item 2: SolidWorks answered; it is Gear Generator that does not take the type.
            # The type's number stays in the record, unshown: the contract names only the types the app takes.
            return f"{item} is on a kind of entity Gear Generator does not make mates on again"
        if s[0] == KIND_UNANSWERED:
            return f"SolidWorks would not say what kind of entity {item} is on"
        # SolidWorks the subject once, and only in the worker's clause where it is the one not answering.
        return f"{item} could not be read wholly" + (f" ({s[0]})" if s[0] else "")
    if why == sb.WHY_LIGHTWEIGHT:
        return f"{item} is on {s[0]}, which was lightweight in {old}, so what it joins could not be read"
    if why == sb.WHY_NO_FILE:
        if s[1] == "virtual":
            return f"{item} is a virtual component, with no file of its own, so it is not carried"
        if not s[0]:
            return f"{item} has no file SolidWorks would name, so it is not carried"
        return f"{item}'s file {s[0]} is not on disk, so it is not carried"
    if why == sb.WHY_LEAF:
        return f"{item} is on a part inside your sub-assembly {s[0]}, which Gear Generator does not make again"
    if why == sb.WHY_NOT_FOUND:
        return f"{item}'s {s[0] or 'entity'} of {s[1]} could not be found again in {s[2] or 'its file'}"
    if why == getattr(sb, "WHY_TOO_LONG", "too long"):
        kind, owner, file = s[0] or "face", s[1], s[2]
        many = _ENTITY_PLURALS.get(kind, "entities")
        among = f" among {file}'s {many}" if file else ""
        return (f"{item} is on {_ENTITY_WORDS.get(kind, 'an entity')} of {owner or 'a component'} that Gear Generator "
                f"did not look for, since finding it{among} would have taken too long")
    if why == sb.WHY_CONFIGURATION:
        component, used, opens = s[0] or item, s[1], s[2]
        if not used:
            return f"{component}'s configuration could not be read, so it is not carried"
        besides = f", not {opens} which its file opens in," if opens and opens != used else ""
        return (f"{component} uses its configuration {used}{besides} and Gear Generator cannot carry it in {used} "
                "here, so it is not carried")
    if why == sb.WHY_NO_FRAME:
        mode = f"in {s[1]}, the mode {old} showed" if s[1] else f"in the mode {old} showed"
        return (f"{s[0] or item} is suppressed {mode}, and SolidWorks would not say where it stands, so it is not "
                "carried")
    if why == getattr(sb, "WHY_REFUSED", "refused"):
        said = s[0].rstrip(".")
        return f"{item} is not made again: SolidWorks refused it" + (f", saying {said}" if said else "")
    if why == sb.WHY_DIFFERS:
        if s[0] == "left":
            return (f"{item} made again read otherwise than it was and could not be taken out again: it is left in "
                    f"{name} as {s[1] or item}; delete it there in SolidWorks")
        return f"{item} made again read otherwise than it was (its {s[0] or 'definition'}), so it was taken out again"
    if why == sb.WHY_OLD_UNREAD:
        return f"{old} was not read" + (f": {s[0]}" if s[0] else "")
    return f"{item} is not carried ({why})"


_MATE_VERDICTS = ("not made again", "not make again", "taken out again", "would have taken too long")
_COMPONENT_VERDICTS = ("not carried",)


def _with_verdict(clause: str, what: str) -> str:
    """A §9.3 clause as a sentence, with the item's own verdict where the clause does not say it: a mate's is *made
    again* (a clause ending *which is not carried* speaks of its component), a component's *carried*."""
    verdicts = _COMPONENT_VERDICTS if what == "component" else _MATE_VERDICTS
    if not any(v in clause for v in verdicts):
        clause += (", and it is" if ", so " in clause else ", so it is") + \
            (" not carried" if what == "component" else " not made again")
    return _sentence(clause[:1].upper() + clause[1:])


def _named_sentences(named, *, name: str, old: str, refs: Optional[List[str]] = None,
                     resolved: Sequence[str] = ()) -> List[str]:
    """Every item not carried as sentences, one per kind of reason: those a finding not yet set holds back grouped by
    what and finding (*Gear Generator has not yet been shown to make concentric mates again in a new revision on
    SolidWorks 2024 (findings.CARRY_REMAKE_KINDS_ON_2024), so Concentric5 and Concentric8 are not made again.*), the
    mates of a component not carried grouped by it, then each other one by its clause and verdict. ``refs``: when a
    list, the findings are not named in the sentences but added to it, for one sentence at the end (the question)."""
    from . import swbuild as sb
    groups: Dict[Tuple[str, str, str, str], List] = {}
    joins: Dict[str, List[str]] = {}
    causes: Dict[Tuple[str, str, str], List[str]] = {}       # A's sixth round: (cause, component, mode) -> mates
    out: List[str] = []
    for n in named:
        s = _subjects(n)
        if n.why == sb.WHY_UNMEASURED and not (s[0] == "sub-assembly" and _marks_sub(s[1])):
            groups.setdefault((s[0], s[1], s[2], s[3] if s[0] in ("face", "edge", "vertex") else ""), []).append(n)
        elif n.why == sb.WHY_NOT_CARRIED and n.what == "mate":
            joins.setdefault(s[0], []).append(n.item)
        elif n.why == sb.WHY_UNREAD and s[1] in (sb.CAUSE_SUPPRESSED,
                                                 sb.CAUSE_BESIDE_LIGHTWEIGHT):
            causes.setdefault((s[1], s[2], s[3]), []).append(n.item)
        elif n.why != sb.WHY_OLD_UNREAD:                     # said once, by the sentence for nothing read
            out.append(_with_verdict(carry_named_clause(n, name=name, old=old, resolved=resolved), n.what))
    lead: List[str] = []
    for (what, finding, version, owner), items in groups.items():
        names = [n.item for n in items]
        verdict = "carried" if all(n.what == "component" for n in items) else "made again"
        if refs is None:
            ref = f" ({_finding_ref(finding)})"
        else:
            ref = ""
            if _finding_ref(finding) not in refs:
                refs.append(_finding_ref(finding))
        lead.append(f"Gear Generator has not yet been shown to {_unmeasured_verb(what, finding, owner)} on "
                    f"{_on_version(version)}{ref}, so {_and(names)} {'is' if len(names) == 1 else 'are'} not "
                    f"{verdict}.")
    for component, mates in joins.items():
        one = len(mates) == 1
        lead.append(f"{_and(mates)} {'joins' if one else 'join'} {component}, which is not carried, so "
                    f"{'it is' if one else 'they are'} not made again.")
    for (cause, component, mode), mates in causes.items():
        one = len(mates) == 1
        if cause == sb.CAUSE_SUPPRESSED:
            lead.append(f"{_and(mates)} {'is' if one else 'are'} on {_suppressed_where(component, mode, old)}, so "
                        f"{'it' if one else 'they'} could not be read and {'is' if one else 'are'} not made again.")
        else:
            lead.append(f"{_and(mates)} {'is' if one else 'are'} on a plane of {old} itself, "
                        f"{_beside_light(component, resolved)}, so {'it is' if one else 'they are'} not made "
                        "again.")
    return lead + out


KIND_UNANSWERED = "SolidWorks would not say what kind of entity it is"     # the worker's clause, no cause


def _beside_light(component: str, resolved: Sequence[str] = ()) -> str:
    """*which Gear Generator does not read while Sprocket-1 is lightweight in it*; in the past where the carry left it
    resolved there (the re-check of b67cdc5, item 1: beside D10's *… is resolved there now*)."""
    if component in set(resolved or ()):
        return f"which Gear Generator did not read while {component} was lightweight in it"
    return f"which Gear Generator does not read while {component} is lightweight in it"


def _suppressed_where(component: str, mode: str, old: str) -> str:
    """*Sprocket-9, which is suppressed in H, the mode RangeBox.SLDASM showed* (with no modes, *… suppressed in
    RangeBox.SLDASM*)."""
    return (f"{component}, which is suppressed in {mode}, the mode {old} showed" if mode
            else f"{component}, which is suppressed in {old}")


def _parts_left(stays, name: str, why_new: Mapping[str, str]) -> Tuple[List[str], List[Tuple[str, str]]]:
    """W9a's features in parts made new, each part once, with the gears whose new part replaces it and why: *your
    Keyway stays in Gear_m1.25_N29, which Sun's new part replaces because its Flank changed*; and ``(feature names,
    part path)`` per part, for the advice that follows."""
    if stays is None or stays.entry is None:
        return [], []
    by_part: Dict[str, Tuple[List[str], Tuple[str, ...]]] = {}
    for feature, path, gears in stays.left:
        by_part.setdefault(path, ([], gears))[0].append(feature)
    out, parts = [], []
    for path, (features, gears) in by_part.items():
        replacing = [g for g in gears if g in why_new]
        if replacing:
            whose = f"which {_and(replacing)}'s new part replaces because {why_new[replacing[0]]}"
        else:
            whose = f"which {name} does not use"
        out.append(f"your {_and(features)} {'stays' if len(features) == 1 else 'stay'} in {_stem(path)}, {whose}")
        parts.append((_and(features), path))
    return out, parts


def _features_left_sentence(stays, name: str, old: str, why_new: Mapping[str, str], past: bool = False) -> str:
    """The features left in parts made new, one sentence (§9.1, §9.2): *Your Keyway stays in Gear_m1.25_N29, which
    Sun's new part replaces because its Flank changed; RangeBox.SLDASM and that file keep it.* (the result's with the
    keepers in brackets)."""
    left, parts = _parts_left(stays, name, why_new)
    if not left:
        return ""
    files = "that file keeps" if len(parts) == 1 else "those files keep"
    files = files.replace("keeps", "keep")
    them = "it" if len(left) == 1 and " and " not in parts[0][0] else "them"
    keep = f"{old} and {files} {them}"
    body = f"{left[0][:1].upper()}{left[0][1:]}" + "".join(f"; {x}" for x in left[1:])
    return _sentence(f"{body} ({keep})" if past else f"{body}; {keep}")


def _features_question(stays, name: str, why_new: Mapping[str, str]) -> str:
    """The question's one sentence on the user's features (§9.1, kept short, S3): those left in parts made new, with
    why, and those that come with a part the new revision reuses: *Your Keyway stays in Gear_m1.25_N29, which Sun's new
    part replaces (its Flank changed); your Groove comes with Sleeve_m1.25_N17.*"""
    pieces = []
    by_part: Dict[str, Tuple[List[str], Tuple[str, ...]]] = {}
    for feature, path, gears in (stays.left if stays is not None and stays.entry is not None else ()):
        by_part.setdefault(path, ([], gears))[0].append(feature)
    for path, (features, gears) in by_part.items():
        replacing = [g for g in gears if g in why_new]
        whose = (f"which {_and(replacing)}'s new part replaces ({why_new[replacing[0]]})" if replacing
                 else f"which {name} does not use")
        pieces.append(f"your {_and(features)} {'stays' if len(features) == 1 else 'stay'} in {_stem(path)}, {whose}")
    kept: Dict[str, List[str]] = {}
    for feature, path in (stays.kept if stays is not None else ()):
        kept.setdefault(path, []).append(feature)
    for path, features in kept.items():
        pieces.append(f"your {_and(features)} {'comes' if len(features) == 1 else 'come'} with {_stem(path)}")
    if not pieces:
        return ""
    return _sentence("; ".join(pieces)[:1].upper() + "; ".join(pieces)[1:])


def _features_kept(stays, name: str) -> List[str]:
    kept: Dict[str, List[str]] = {}
    for feature, path in (stays.kept if stays is not None else ()):
        kept.setdefault(path, []).append(feature)
    return [f"Your {_and(f)} in {_stem(p)} {'comes' if len(f) == 1 else 'come'} with that part, which {name} reuses."
            for p, f in kept.items()]


def _reuse_advice(fore, parts: Sequence[Tuple[str, str]], again) -> List[str]:
    """The way back to reusing a part made new only because of the user (D17): MISMATCHED with the value and cell the
    record's K11 entry holds, or without one; UNSAVED: save it first."""
    from .workbook.gearbox import MISMATCHED, UNSAVED
    out = []
    for features, path in parts:
        made = [m for m in getattr(again, "made_new", ()) or () if _file(m.old).lower() == _file(path).lower()]
        if not made:
            continue
        why = made[0].why
        if why == MISMATCHED:
            value = fore.values.get(_file(path).lower()) if fore is not None else None
            if value is not None and value.live and value.cell:
                out.append(f"{_stem(path)} is new only because it holds {value.name} {value.live} where the workbook "
                           f"asks {value.wanted}: answer No, type {value.live} in {value.cell}, and Build again… "
                           f"reuses that part with your {features}.")
            else:
                out.append(f"{_stem(path)} is new only because it does not hold what the record says: answer No, "
                           "make the workbook ask what that part holds in SolidWorks, and Build again… reuses it "
                           f"with your {features}.")
        elif why == UNSAVED:
            out.append(f"{_stem(path)} is new only because Update SolidWorks left it unsaved: answer No and save it "
                       f"in SolidWorks first, and Build again… reuses it with your {features}.")
    return out


def _not_open_clause(fore, old: str, refs: List[str]) -> str:
    """§9.1's clause for an old assembly closed when the press is made (the window cannot know whether it will be, so
    it is said as *if*). A closed file's versions are read without opening it; while a finding the open rests on is
    unset it is not opened at all (the re-check's R1), else only under R.2's conditions. The findings go to ``refs``,
    named once at the end."""
    if fore.not_open:
        refs.extend(_finding_ref(f) for f in fore.not_open if _finding_ref(f) not in refs)
        return f"If {old} is closed when you press, nothing is carried: open it in SolidWorks first."
    if fore.keeps_open:
        if _finding_ref(fore.keeps_open) not in refs:
            refs.append(_finding_ref(fore.keeps_open))
        others = "nothing else is open"
    else:
        others = "nothing of yours is open"
    return (f"If {old} is closed, open it first unless this SolidWorks last saved it and its files, those files are "
            f"where it says, and {others}.")


def _placement_words(anchors: Sequence[str], past: bool = False) -> str:
    """Where carried components stand: against their gear (or carrier) when each has one, else where they stand."""
    stands = "stood" if past else "stands"
    each = "each " if len(anchors) != 1 else ""
    bodies = [a for a in anchors if a and a != "layout"]
    if anchors and len(bodies) == len(anchors):
        what = "gear or carrier" if any(a.endswith(" carrier") for a in bodies) else "gear"
        return f"{each}where it {stands} against its {what}"
    return f"{each}where it {stands}"


def _components_named(names: Sequence[str]) -> List[str]:
    """Up to four components by name, else three and the rest counted (W9a's cap, with the fourth named when it is
    the last)."""
    names = list(dict.fromkeys(n for n in names if n))
    return names if len(names) <= USER_NAMED + 1 else _yours(names)


def carry_sentence(fore, again) -> str:
    """The Build again? question's clauses on the user's work (W9D-INTERFACES §9.1; replaces W9a's
    :func:`stays_behind_sentence`), from ``workbook.update.CarryForesight``: with ``CARRY_INSERTS`` set on the
    SolidWorks the record last saw, what is carried and what is not, with the time it was read, one sentence per kind
    of thing, the findings named once at the end; not set, W9a's sentence led by the finding; not known, W9c's mixed
    form. ``""`` with no assembly on record."""
    if fore is None:
        return ""
    name = getattr(again, "name", "") or fore.name or "the new revision"
    old = _file(fore.assembly) if fore.assembly else "the old assembly"
    stays = fore.stays
    if stays is None:
        from .workbook.update import StaysBehind
        stays = StaysBehind(None, fore.assembly)
    if fore.inserts is None:
        found = [f"CARRY_INSERTS_ON_{y}" for y in fore.unshown]
        return _joined(f"Whether {name} takes your work depends on the SolidWorks in use: Gear Generator has been "
                       f"shown to do so on {_and('SolidWorks ' + y for y in fore.shown)}, not yet on "
                       f"{_and('SolidWorks ' + y for y in fore.unshown)} ({_and(_finding_ref(f) for f in found)}), "
                       "and the press reads which it runs on.",
                       f"The press reads {old} again first, and says whatever it cannot carry.")
    if not fore.inserts:
        lead = (f"Gear Generator has not yet been shown to carry your work into a new revision on "
                f"{_on_version(fore.year)} ({_finding_ref('CARRY_INSERTS_ON_' + fore.year)}), so ")
        return lead + _stays_text(stays, again, "as read at")
    refs: List[str] = []
    entry = fore.entry
    texts: List[str] = []
    if entry is None:
        texts.append(f"Anything you added to {old} in SolidWorks the press reads first and carries into {name} "
                     "where it can, saying whatever it cannot.")
        texts.append(_not_open_clause(fore, old, refs))
        return " ".join(texts + _findings_sentence(refs, fore.year))
    at = read_time(entry.read_at)
    plan = fore.plan
    carries = plan is None or bool(plan.components or plan.mates)
    on_suppressed: Dict[str, List[str]] = {}         # B3: component -> its mates unread for it, said with it
    beside_light: Dict[str, List[str]] = {}          # B3: lightweight component -> the assembly's own planes' mates
    if plan is None:
        items = _yours([c.name for c in entry.components], 0, _mate_words([m.name for m in entry.mates]))
        texts.append(f"As read at {at}, {old} held your {_and(items)}: the press reads it again first and carries "
                     f"into {name} what it can, saying whatever it cannot." if items else
                     f"As read at {at}, {old} held features of yours in the app's parts, said below.")
    else:
        from . import swbuild as sb
        unknown = {n.item for n in plan.named if n.why == sb.WHY_UNREAD and n.subjects
                   and str(n.subjects[0]) == _unknown_entity()}
        light = {c.name for c in entry.components if c.state in (1, 4)}
        comps = [i.component.name for i in plan.components]
        # The re-check of 11a63ab, item 1: a recorded distance or angle mate is said as *may* while the gate answers
        # its plain and its limit kind differently, since the record keeps its type, never its type name or range.
        limit_may = _limit_may(fore, entry, plan)
        may_items = {m for ms in limit_may.values() for m in ms}
        carries = carries or bool(may_items)
        mates = [m.mate.name for m in plan.mates if m.mate.name not in may_items]
        clauses = []
        if comps:
            clauses.append(f"takes your {_and(_components_named(comps))}")
        bad = {m.name for m in entry.mates if m.code and m.code != -1}
        if mates:
            one = len(mates) == 1
            clauses.append(f"makes {'your ' + mates[0] if one else f'your {len(mates)} mates'} again in the modes "
                           f"{'it was' if one else 'each was'} on in")
            if one and mates[0] in bad:
                # B1's rule, each mate in one sentence: the one mate named is said in error here, not again below.
                clauses[-1] += (f"; it was in error in {old} as read, and made again it is carried if it reads no "
                                "error or the one it had, and not if it keeps a gear from turning")
        may_said = _limit_may_sentences(limit_may)
        if clauses:
            texts.append(f"As read at {at}, {name} {' and '.join(clauses)}.")
        elif may_said:
            may_said[0] = f"As read at {at}, {may_said[0][:1].lower()}{may_said[0][1:]}"
        else:
            texts.append(f"As read at {at}, nothing of yours in {old} would be carried into {name}.")
        # M5: a lightweight component's mates are said once, by its own sentence below, as the condition they are.
        # The demonstration's review (item 1): what only the inventory's silence names is said as *may*, never as fact.
        silent_ratio, silent_axis = _foresight_silences(fore, entry, plan)
        axis_items = {m for ms in silent_axis.values() for m in ms}          # B1: by mate, not by gear
        # B3: a mate unread for its component suppressed as read is said with that component's own sentence, as one
        # thought; one on the assembly's own plane beside a lightweight component, with what lets it be read.
        for n in plan.named:
            cause = (n.subjects[1] if n.why == sb.WHY_UNREAD and len(n.subjects) > 2 else "")
            if cause == sb.CAUSE_SUPPRESSED and any(c.name == n.subjects[2] and c.state == 0
                                                    for c in entry.components):
                on_suppressed.setdefault(str(n.subjects[2]), []).append(n.item)
            elif cause == sb.CAUSE_BESIDE_LIGHTWEIGHT:
                beside_light.setdefault(str(n.subjects[2]), []).append(n.item)
        caused = {m for ms in list(on_suppressed.values()) + list(beside_light.values()) for m in ms}
        named = [n for n in plan.named if n.item not in unknown and n.item not in silent_ratio
                 and n.item not in axis_items and n.item not in caused and n.item not in may_items
                 and not (n.why == sb.WHY_LIGHTWEIGHT and n.subjects and str(n.subjects[0]) in light)]
        texts += _named_sentences(named, name=name, old=old, refs=refs)
        texts += _unknown_entities(fore, entry, unknown)
        texts += _may_sentences(silent_ratio, silent_axis)
        texts += may_said
        texts += _in_error_before(entry, plan, old, mates)
        if fore.assumed and fore.configuration:
            one = len(fore.assumed) == 1
            refs.extend(_finding_ref(f) for f in fore.configuration if _finding_ref(f) not in refs)
            texts.append(f"{_and(fore.assumed)} {'is' if one else 'are'} carried only if "
                         f"{'its file has' if one else 'each file has'} one configuration.")
    texts += _component_states(entry, old, on_suppressed)
    for light, mates in beside_light.items():
        one = len(mates) == 1
        texts.append(f"{_and(mates)} {'is' if one else 'are'} on a plane of {old} itself, which Gear Generator does "
                     f"not read while {light} is lightweight in it: {'it is' if one else 'they are'} made again only "
                     f"if you set {light} resolved in SolidWorks before you press.")
    left, parts = _parts_left(stays, name, fore.why_new)
    texts.append(_features_question(stays, name, fore.why_new))
    texts += _reuse_advice(fore, parts, again)
    if carries:
        texts.append(f"{name} holds what it carries unsaved.")
        texts.append(_not_open_clause(fore, old, refs))
        if (plan.components if plan is not None else entry.components) and fore.first and not fore.states_read:
            texts.append(f"Each component takes, in every mode of {name}, its state in the mode {old} shows; its other "
                         "states cannot be read without changing it.")
        texts += _modes_said(fore, name, old)
        texts.append(_standing())
    return " ".join([t for t in texts if t] + _findings_sentence(refs, fore.year))


def _foresight_silences(fore, entry, plan) -> Tuple[List[str], Dict[str, List[str]]]:
    """What the question's foresight names only because the record's inventory is silent (the demonstration's review,
    item 1): ``(gear mates named unread though the inventory holds them whole, with every entity's kind known — their
    ratio and sense, never kept, are what plan_carry missed; gear id -> gear mates on a face of a gear whose part is
    new while the coaxial read is shown: whether the face is on its axis, never kept)``."""
    from . import swbuild as sb
    by = {m.name: m for m in entry.mates}
    ratio: List[str] = []
    axis: Dict[str, List[str]] = {}
    # B2: the axis is all that could stand in the way only while the coaxial read is shown and both gates a gear mate
    # on an app gear passes would let it be made.
    kinds = _finding_value("CARRY_REMAKE_KINDS", fore.year) if fore.year != "?" else None
    coaxial = (fore.year != "?" and _finding_value("COAXIAL_FACE_READ", fore.year) is True
               and _finding_value("CARRY_GEAR_MATE_ON_AN_APP_GEAR", fore.year) is True
               and isinstance(kinds, (tuple, list)) and "gear" in kinds)
    for n in plan.named:
        m = by.get(n.item)
        if m is None or m.kind != "gear":
            continue
        known = bool(m.entities) and m.whole and all(len(e) == 4 and e[2] not in ("unread", "") for e in m.entities)
        s = [str(x) for x in n.subjects] + ["", "", "", ""]
        if n.why == sb.WHY_UNREAD and known:
            ratio.append(n.item)
        elif n.why == sb.WHY_PART_NEW and s[2] == "face" and coaxial:
            axis.setdefault(s[0], []).append(n.item)
    return ratio, axis


def _finding_value(name: str, year: str):
    from . import findings
    return getattr(findings, f"{name}_ON_{year}", None)


def _may_sentences(ratio: Sequence[str], axis: Mapping[str, Sequence[str]]) -> List[str]:
    """The *may* for what the inventory cannot know: a gear mate's ratio and sense (*Your UserGear6 is made again if
    the press reads its gear ratio and which way it turns.*), and whether a gear mate's face of a gear made new is on
    its axis (*Your UserGearRoot is made again only if the face of Sun it is on proves to be on Sun's axis, since
    Sun's part is new.*)."""
    out = []
    if ratio:
        one = len(ratio) == 1
        out.append(f"Your {_and(ratio)} {'is' if one else 'are'} made again if the press reads "
                   f"{'its gear ratio and which way it turns' if one else 'their gear ratios and which way they turn'}.")
    for gear, mates in axis.items():
        one = len(mates) == 1
        out.append(f"Your {_and(mates)} {'is' if one else 'are'} made again only if the face of {gear} "
                   f"{'it is' if one else 'each is'} on proves to be on {gear}'s axis, since {gear}'s part is new.")
    return out


def _limit_may(fore, entry, plan) -> Dict[Tuple[str, bool], List[str]]:
    """``(kind word, plain allowed) -> mates``: the recorded distance and angle mates whose kind the record cannot
    tell (``UserMateEntry`` keeps the type, 5 or 6, the same for a plain and a limit mate) while
    ``CARRY_REMAKE_KINDS`` on the SolidWorks the record last saw allows one of the two kinds and not the other: made
    again by the plan as plain (plain allowed), or named unmeasured for the plain kind (the limit kind allowed)."""
    from . import swbuild as sb
    kinds = _finding_value("CARRY_REMAKE_KINDS", fore.year) if fore.year != "?" else None
    if not isinstance(kinds, (tuple, list)):
        return {}
    split = {w: w in kinds for w in ("distance", "angle") if (w in kinds) != (f"limit {w}" in kinds)}
    if not split:
        return {}
    word_of = {5: "distance", 6: "angle"}
    recorded = {m.name: word_of.get(m.type) for m in entry.mates}
    out: Dict[Tuple[str, bool], List[str]] = {}
    for item in plan.mates:
        word = recorded.get(item.mate.name)
        if word in split and split[word]:
            out.setdefault((word, True), []).append(item.mate.name)
    for n in plan.named:
        word = recorded.get(n.item)
        if (word in split and not split[word] and n.why == sb.WHY_UNMEASURED and n.subjects
                and str(n.subjects[0]) == word):
            out.setdefault((word, False), []).append(n.item)
    return out


def _limit_may_sentences(may: Mapping[Tuple[str, bool], Sequence[str]]) -> List[str]:
    """*Your UserLimit10 is made again if the press reads it as a plain distance mate; a limit distance mate is not
    made again.*, or, the limit kind the one allowed, *… only if the press reads it as a limit distance mate; a plain
    distance mate is not made again.*"""
    out = []
    for (word, plain), mates in may.items():
        one = len(mates) == 1
        said, other = ("plain", "limit") if plain else ("limit", "plain")
        out.append(f"Your {_and(mates)} {'is' if one else 'are'} made again {'if' if plain else 'only if'} the press "
                   f"reads {'it as a' if one else 'them as'} {said} {word} {'mate' if one else 'mates'}; "
                   f"{'a ' if one else ''}{other} {word} {'mate is' if one else 'mates are'} not made again.")
    return out


def _in_error_before(entry, plan, old: str, lead: Optional[Sequence[str]] = None) -> List[str]:
    """The demonstration's review (§6): a mate of the user's the inventory holds in error, which the plan makes again:
    *UserLock8a was in error in RangeBox.SLDASM as read; made again, it is carried if it reads no error or the one it
    had, and not if it keeps a gear from turning.*"""
    made = set(lead) if lead is not None else {m.mate.name for m in plan.mates}
    if len(made) == 1:
        return []                              # the one mate made again is named, and said in error, in the lead
    bad = [m.name for m in entry.mates if m.name in made and m.code and m.code != -1]
    if not bad:
        return []
    one = len(bad) == 1
    return [f"{_and(bad)} {'was' if one else 'were'} in error in {old} as read; made again, "
            f"{'it is' if one else 'each is'} carried if it reads no error or the one it had, and not if it keeps a "
            "gear from turning."]


def _findings_sentence(refs: Sequence[str], year: str) -> List[str]:
    """The findings the question's clauses rest on, named once at the end (S3)."""
    if not refs:
        return []
    return [f"(Not yet shown on {_on_version(year)}: {_and(refs)}.)"]


def _unknown_entity() -> str:
    from .workbook.update import UNKNOWN_ENTITY
    return UNKNOWN_ENTITY


def _unknown_entities(fore, entry, unknown: Set[str]) -> List[str]:
    """A schema 9 inventory's mates, whose entity kinds were never kept (*may*): those on an app gear whose part is
    new, *your Lock3 and UserAxis4 join Sun, whose part is new: a mate on one of its faces or edges is not made again,
    and the press reads which they are.*; any other, that the press reads what it is on and makes it again where it
    can."""
    if not unknown:
        return []
    out = []
    on_new: Dict[str, List[str]] = {}
    rest = []
    for m in entry.mates:
        if m.name not in unknown:
            continue
        gears = [n for w, n in m.touches if w == "app" and n in fore.why_new]
        if gears:
            on_new.setdefault(gears[0], []).append(m.name)
        else:
            rest.append(m.name)
    for gear, names in on_new.items():
        one = len(names) == 1
        out.append(f"Your {_and(names)} {'joins' if one else 'join'} {gear}, whose part is new: a mate on one of its "
                   f"faces or edges is not made again, and the press reads which {'it is' if one else 'they are'}.")
    if rest:
        one = len(rest) == 1
        out.append(f"The record does not say what your {_and(rest)} {'is' if one else 'are'} on, so the press reads "
                   f"{'it' if one else 'them'} and makes {'it' if one else 'each'} again where it can.")
    return out


def _component_states(entry, old: str, unread: Optional[Mapping[str, Sequence[str]]] = None) -> List[str]:
    """§9.1's lightweight and suppressed components, as read (``UserComponentEntry.state``: 0 suppressed, 1 and 4
    lightweight), each said once as the condition it is (M5); a suppressed one with the mates ``unread`` for it (B3:
    ``CAUSE_SUPPRESSED``) in the same sentence."""
    out = []
    unread = unread or {}
    for c in entry.components:
        mates = [m.name for m in entry.mates if any(w == "user" and n == c.name for w, n in m.touches)]
        if c.state in (1, 4):
            # A's third round (D10's fact, ruled): loading its part to carry it resolves it in the old assembly too.
            too = f"carrying it resolves it in {old} too, if that is open"
            if mates:
                one = len(mates) == 1
                its = f"its {mates[0]}" if one else f"its {len(mates)} mates"
                out.append(f"{c.name} was lightweight as read: {too}, and {its} {'is' if one else 'are'} made again "
                           "only if you set it resolved in SolidWorks before you press.")
            else:
                out.append(f"{c.name} was lightweight as read: it is carried resolved, and {too}.")
        elif c.state == 0 and unread.get(c.name):
            ms = list(unread[c.name])
            one = len(ms) == 1
            out.append(f"{c.name} was suppressed in the mode {old} showed, as read, so {_and(ms)} on it could not be "
                       f"read: show a mode where {c.name} is resolved before you press, or {c.name} may not be carried "
                       f"and {ms[0] + ' is' if one else 'they are'} not made again.")
        elif c.state == 0:
            out.append(f"{c.name} was suppressed in the mode {old} showed, as read: show a mode where it is resolved "
                       "before you press, or it may not be carried.")
    return out


def _modes_said(fore, name: str, old: str) -> List[str]:
    return _modes_words(fore.modes_gone, fore.modes_new, fore.first, name, old)


def _modes_words(gone: Sequence[str], added: Sequence[str], first: str, name: str, old: str) -> List[str]:
    """D14 (§9.1, §9.2): an old mode the revision has not, and what a new mode takes."""
    out = [f"{name} has no mode {mode}: what your items were in {mode} stays in {old}." for mode in gone]
    if added and first:
        one = len(added) == 1
        out.append(f"Its new {'mode' if one else 'modes'} {_and(added)} {'takes' if one else 'take'} what they were "
                   f"in {first}.")
    return out


def _standing(revision: Sequence[int] = ()) -> str:
    """The standing list of what is not carried as it was. In the result the pattern clause leaves it once
    ``PATTERN_INSTANCE_READ`` is set on the SolidWorks the job ran on, and the per-instance sentence says it (D12); the
    question cannot know which component is an instance, so it keeps the clause."""
    if revision:
        from . import findings, swcom
        year = swcom.release_year(int(revision[0]))
        if getattr(findings, f"PATTERN_INSTANCE_READ_ON_{year}", None) is True:
            return CARRY_STANDING_NO_PATTERN
    return CARRY_STANDING


def _split_stop(done) -> Tuple[str, str]:
    """``(the stop, the files found changed after the carry)`` (the re-check's N2): the files from the worker's own
    field, ``CarryResult.changed_files`` (base names), said in B's words; the worker's sentence for them, which it
    still appends to ``stopped``, cut off at the last place that field's names begin it, so the stop is the stop only.
    Nothing else of the worker's words is matched."""
    text = bare_files(getattr(done, "stopped", "") or "").strip()
    files = [bare_files(str(f)) for f in getattr(done, "changed_files", ()) or () if f]
    if not files:
        return text, ""
    at = text.rfind(_and(files))
    if at >= 0:
        text = text[:at].strip()
    one = len(files) == 1
    return text, (f"{_and(files)} changed on disk while Build again… carried your work, which Gear Generator never "
                  f"does; look at {'it' if one else 'them'} in SolidWorks.")


def _stop_tail(stop: str, skipped: str) -> str:
    """*It did not get to …*, without the step the stop already names (the re-check's note: *… stopped the carry while
    reading the new revision: … It did not get to reading the new revision.*)."""
    skipped = skipped.rstrip(".").strip()
    if not skipped or not stop:
        return ""
    for sep in (", ", " and "):
        head, _, rest = skipped.partition(sep)
        if rest and f"while {head}" in stop:
            return f" It did not get to {rest}."
    if f"while {skipped}" in stop:
        return ""
    return f" It did not get to {skipped}."


def _inserts_held(done) -> str:
    """The ``CARRY_INSERTS`` finding when it held everything back (a gate the worker kept), else ``""``."""
    return next((f for _, f in getattr(done, "gates", ()) or () if str(f).startswith("CARRY_INSERTS_ON_")), "")


def carried_status(result, again, old_path: str = "", anchors: Optional[Mapping[str, str]] = None,
                   revision: Sequence[int] = (), *, carry=None, stays=None) -> str:
    """After a carrying Build again…, what was carried, after ``gearbox_status`` (W9D-INTERFACES §9.2; replaces W9a's
    :func:`stayed_behind_status`), from ``result.carry`` (``swbuild.CarryResult``): *Carried into RangeBox_r2,
    unsaved: your Sprocket-1, Sprocket-2, Chain-1 and Housing-1, each where it stood against its gear, and 7 of your 8
    mates, each on in the modes it was on in.*, each item not carried, the features left in parts made new, each
    fallback, mate in the error it had, component moved, clash, the placement and the states, the modes, a sub-assembly
    made rigid, the marks fact, a stop, the standing list. With nothing carried, the reason as a lead and W9a's sentence
    of what stays (M1); an old assembly not read, its reason and the record's (M3). ``anchors`` each carried
    component's anchor by its old Name2; ``revision`` the SolidWorks the job ran on; ``carry`` the ``swbuild.Carry``
    the job was given (why each part is new, the new modes); ``stays`` W9a's ``workbook.update.StaysBehind``. ``""``
    without a carry. Every path the worker's words hold is said by its file's name only."""
    from . import swbuild as sb
    done = getattr(result, "carry", None)
    if done is None:
        return ""
    name = getattr(again, "name", "") or "the new revision"
    work = done.work
    path = (work.assembly if work is not None and work.assembly else "") or old_path
    old = _file(path) if path else "the old assembly"
    if stays is None:
        from .workbook.update import StaysBehind
        stays = StaysBehind(None, path)
    why_new = {b.old: b.why_new for b in (getattr(carry, "bodies", ()) or ()) if b.why_new}
    stop, after = _split_stop(done)
    if work is None:
        reason = stop.rstrip(".") or f"SolidWorks did not answer the read of {old}"
        return _joined(f"{reason}, so nothing of yours was carried; {old} and your files are as they were on disk.",
                       _stays_text(stays, again))
    held = _inserts_held(done)
    if work.how == sb.OLD_UNREAD and held:
        # Nothing could be carried at all: W9a's own sentence for an old assembly not open, behind the one lead.
        year = held.rsplit("_ON_", 1)[-1]
        return _joined(f"Gear Generator has not yet been shown to carry your work into a new revision on "
                       f"{_on_version(year)} ({_finding_ref(held)}).",
                       stayed_behind_status(stays, result, again, path))
    if work.how == sb.OLD_UNREAD:
        reason = "; ".join(bare_files(u).rstrip(".") for u in work.unread) or f"{old} was not read"
        return f"{reason}, so nothing of yours was carried; {_stays_text(stays, again, 'as read at')}"
    if work.marked:
        return (f"Reading {old} marked {_and(_file(p) for p in work.marked)} as changed in SolidWorks, which Gear "
                f"Generator never does on purpose, so nothing of yours was carried; nothing in "
                f"{'it' if len(work.marked) == 1 else 'them'} changed, and {old} and your files are as they were on "
                "disk.")
    if work.left:
        one = len(work.left) == 1
        return (f"Reading {old} left {_and(_file(p) for p in work.left)} open in SolidWorks, so nothing of yours was "
                f"carried; close {'it' if one else 'them'} without saving.")
    skipped = _stop_tail(stop, done.skipped)
    if not done.inserted and not done.remade:
        return " ".join(t for t in _nothing_carried(done, result, again, path, stays, name, old, stop, skipped)
                        + [after, _resolved_in_old(done, old), _after_unread(done)] if t)
    texts: List[str] = []
    new_of = dict(done.inserted)
    old_of = {n: o for o, n in done.inserted}
    anchors = dict(anchors or {})
    comps = [n if n == o else f"{n} (was {o})" for o, n in done.inserted]
    total = len(work.mates)
    clauses = []
    if comps:
        clauses.append(f"your {_and(_components_named(comps))}, "
                       f"{_placement_words([anchors.get(o, '') for o, _ in done.inserted], past=True)}")
    kept_of = {o: k for o, k, _ in done.remade}
    if done.remade:
        made = len(done.remade)
        # A's 7e3ad9a: a mate kept under SolidWorks' name, said as a renamed component is (*Mate12 (was Lock1)*).
        renamed = [_kept_as(o, kept_of) for o, k, _ in done.remade if k and k != o]
        among = f", {_and(renamed)} among them" if renamed else ""
        if made == total == 1:
            clauses.append(f"your {_kept_as(done.remade[0][0], kept_of)}, on in the modes it was on in")
        elif made == total:
            clauses.append(f"your {_plural(total, 'mate')}{among}, each on in the modes it was on in")
        elif made == 1 and renamed:
            clauses.append(f"1 of your {_plural(total, 'mate')}, {renamed[0]}, on in the modes it was on in")
        else:
            clauses.append(f"{made} of your {_plural(total, 'mate')}{among}, each on in the modes it was on in")
    texts.append(f"Carried into {name}, unsaved: {', and '.join(clauses)}.")
    texts += _named_sentences(done.named, name=name, old=old, resolved=getattr(done, "resolved_in_old", ()) or ())
    texts.append(_features_left_sentence(stays, name, old, why_new, past=True))
    for fallback in done.fixed:
        texts.append(_fallback_sentence(fallback, name, old, work.active, getattr(again, "modes_plan", None),
                                        kept_of))
    for mate, code in done.same_error:
        # The re-check of 11a63ab, item 2: each name beside the assembly it is in.
        kept = kept_of.get(mate, mate) or mate
        texts.append(f"Your {mate} was in error in {old} and is in {name} too, as it was." if kept == mate else
                     f"Your {mate} was in error in {old} and, as {kept}, is in {name} too, as it was.")
    texts += _moved_sentences(done.moved, old_of, anchors)
    for mode, clash in done.clashes:
        names = list(getattr(clash, "gears", ()) or getattr(clash, "components", ()))
        carried = [n for n in names if n in new_of.values()]
        others = [n for n in names if n not in carried]
        if carried:
            texts.append(f"{'In mode ' + mode + ', y' if mode else 'Y'}our {_and(carried)} "
                         f"{'interferes' if len(carried) == 1 else 'interfere'} with {_and(others) or 'each other'} "
                         f"({clash.volume:.1f} mm³).")
    modes = [s.name for s in again.modes_plan.steps] if getattr(again, "modes_plan", None) is not None else []
    if modes and done.inserted and work.active:
        # N1: where they were placed; the every-mode claim only of one no carried mate holds (a component locked to a
        # sliding gear follows it).
        remade = {o for o, _, _ in done.remade}
        held_by = {e.owner for m in work.mates if m.name in remade for e in m.entities if e.what == sb.USER}
        fallen = {n for f in done.fixed for n in f.components}
        free = [c for c in work.components if c.name in new_of and not c.fixed and c.name not in held_by
                and new_of[c.name] not in fallen]
        texts.append(f"Your components were placed where they stood in {work.active}, the mode {old} showed"
                     + ("; one no mate holds stands there in every mode." if free else "."))
    if modes and done.inserted and not work.states_route and work.active:
        others = [m for m in work.modes if m.casefold() != work.active.casefold()]
        texts.append(f"Your components take in every mode the state they had in {work.active}, the mode {old} showed"
                     + (f": their states in {_and(others)} could not be read without changing it." if others
                        else "."))
    new_modes = list(getattr(carry, "modes", ()) or ()) or modes
    if carry is not None and new_modes:
        gone = [m for m in work.modes if not any(m.casefold() == n.casefold() for n in new_modes)]
        added = [m for m in new_modes if not any(m.casefold() == o.casefold() for o in work.modes)]
        texts += _modes_words(gone, added if work.modes else [], getattr(carry, "first", "") or "", name, old)
    for o, n in done.inserted:
        component = next((c for c in work.components if c.name == o), None)
        if component is not None and component.kind == "assembly":
            texts.append(f"Your sub-assembly {n} comes over rigid: set it flexible in SolidWorks again if it was.")
    if done.marked_user:
        # The fact CARRY_INSERT_MARKS_USER_DOCUMENTS (§8): True, the insert alone marks them, so nothing in them is
        # said to have changed; otherwise only what SolidWorks reads is said.
        from . import findings, swcom
        files = _and(_file(p) for p in done.marked_user)
        one = len(done.marked_user) == 1
        year = swcom.release_year(int(revision[0])) if revision else None
        fact = year is not None and getattr(findings, f"CARRY_INSERT_MARKS_USER_DOCUMENTS_ON_{year}", None) is True
        though = f", though nothing in {'it' if one else 'them'} changed" if fact else ""
        texts.append(f"SolidWorks reads {files} as changed since {'it was' if one else 'they were'} inserted into "
                     f"{name}{though}: saving {name} with its parts saves {'that file' if one else 'those files'} "
                     "again too.")
    if stop:
        texts.append(_sentence(stop) + skipped + (f" What was carried before it is in {name}, unsaved, and {name} as "
                                                  "built is saved." if done.unsaved else
                                                  f" Nothing of yours was carried, and {name} as built is saved."))
    texts.append(_standing(revision))
    if _standing(revision) == CARRY_STANDING_NO_PATTERN:
        instances = [new_of[c.name] for c in work.components if c.name in new_of and c.pattern_instance]
        if instances:
            one = len(instances) == 1
            own = "a component of its own" if one else "components of their own"
            texts.append(f"Your {_and(instances)} {'was an instance' if one else 'were instances'} of a pattern of "
                         f"yours, and {'comes' if one else 'come'} over as {own}.")
    if any(c.kind == "part" for c in work.components if c.name in new_of):
        texts.append(CARRY_IN_CONTEXT.format(old=old))
    texts.append(after)
    texts.append(_resolved_in_old(done, old))
    texts.append(_after_unread(done))
    if done.unsaved and not stop:
        texts.append(f"Save {name} in SolidWorks to keep what was carried.")
    return " ".join(t for t in texts if t)


def _resolved_in_old(done, old: str) -> str:
    """A's third round (D10's fact, ruled: not a stop, not undone, said): *Sprocket-9 was lightweight in RangeBox.SLDASM
    and is resolved there now: SolidWorks loaded its part to carry it.*"""
    names = [str(n) for n in getattr(done, "resolved_in_old", ()) or () if n]
    if not names:
        return ""
    one = len(names) == 1
    return (f"{_and(names)} {'was' if one else 'were'} lightweight in {old} and {'is' if one else 'are'} resolved "
            f"there now: SolidWorks loaded {'its part' if one else 'their parts'} to carry {'it' if one else 'them'}.")


def _after_unread(done) -> str:
    """A's third round: why the user's files' times and flags could not be read after the carry
    (``CarryResult.after_unread``), the fact it is, through :func:`bare_files`; never a stop."""
    return _sentence(bare_files(getattr(done, "after_unread", "") or "").strip())


def _nothing_carried(done, result, again, path: str, stays, name: str, old: str, stop: str,
                     skipped: str) -> List[str]:
    """M1: the old assembly read and nothing of the user's carried. A stop is said as the worker says it, with what it
    did not get to; else the findings that held everything back lead W9a's sentence of what stays (*Gear Generator
    has not yet been shown to carry your work into a new revision on SolidWorks 2026 (findings.CARRY_INSERTS_ON_2026),
    so your Sprocket-1, Housing-1 and Lock3 stay in RangeBox.SLDASM, as read when this build began; …*); any other
    reason an item was not carried follows."""
    from . import swbuild as sb
    behind = stayed_behind_status(stays, result, again, path)
    texts: List[str] = []
    if stop:
        texts.append(_sentence(stop) + skipped + f" Nothing of yours was carried, and {name} as built is saved.")
        texts.append(behind)
        return texts
    held = [n for n in done.named if n.why == sb.WHY_UNMEASURED]
    groups: Dict[Tuple[str, str, str], None] = {}
    for n in held:
        s = _subjects(n)
        groups.setdefault((s[0], s[1], s[2]), None)
    if groups and behind:
        verbs = list(dict.fromkeys(_unmeasured_verb(w, f) for w, f, _ in groups))
        found = list(dict.fromkeys(_finding_ref(f) for _, f, _ in groups))
        version = next(iter(groups))[2]
        texts.append(f"Gear Generator has not yet been shown to {_and(verbs)} on {_on_version(version)} "
                     f"({_and(found)}), so {behind[:1].lower()}{behind[1:]}")
    else:
        texts.append(behind)
    others = [n for n in done.named if n.why not in (sb.WHY_UNMEASURED, sb.WHY_NOT_CARRIED, sb.WHY_OLD_UNREAD)]
    texts += _named_sentences(others, name=name, old=old, resolved=getattr(done, "resolved_in_old", ()) or ())
    return texts


def _moved_sentences(moved, old_of: Mapping[str, str], anchors: Mapping[str, str]) -> List[str]:
    """§9.2's *moved*, one sentence per component, its modes grouped: *SolidWorks moved Sprocket-4 off where it stood
    against Sun when your mates were made again: 2.0 mm in L.*"""
    by: Dict[str, List[Tuple[str, float]]] = {}
    for component, mode, mm in moved:
        by.setdefault(component, []).append((mode, mm))
    out = []
    for component, items in by.items():
        anchor = anchors.get(old_of.get(component, component), "")
        against = f" against {anchor}" if anchor and anchor != "layout" else ""
        sizes = {f"{mm:.1f}" for _, mm in items}
        modes = [m for m, _ in items if m]
        if len(sizes) == 1:
            where = f"{next(iter(sizes))} mm" + (f" in {_and(modes)}" if modes else "")
        else:
            where = _and(f"{mm:.1f} mm in {m}" if m else f"{mm:.1f} mm" for m, mm in items)
        out.append(f"SolidWorks moved {component} off where it stood{against} when your mates were made again: "
                   f"{where}.")
    return out


def _kept_as(old_name: str, kept_of: Mapping[str, str]) -> str:
    """A mate made again by the name it has in the new revision: *Mate12 (was Lock1)* where SolidWorks kept its own
    name (A's 7e3ad9a), else its old name, as :func:`carried_status` names a renamed component."""
    kept = kept_of.get(old_name, old_name) or old_name
    return old_name if kept == old_name else f"{kept} (was {old_name})"


def _fallback_sentence(fallback, name: str, old: str, active: str, modes_plan=None,
                       kept_of: Optional[Mapping[str, str]] = None) -> str:
    """A cluster that fell back (§6, §9.2): *Sprocket-8 is fixed where it stood in RangeBox_r2: with your Lock8 and
    Lock9 made again SolidWorks reads Sun unable to turn, so those two were not kept; Coincident7 beside them was.*
    A mate kept is named as it is in the new revision (``kept_of``, old -> kept); one deleted by its old name."""
    from . import swbuild as sb
    kept_of = kept_of or {}
    comps = list(fallback.components)
    deleted = list(fallback.deleted)
    s = [str(x) for x in fallback.subjects] + ["", "", "", ""]
    one = len(comps) == 1
    head = f"{_and(comps)} {'is' if one else 'are'} fixed where {'it' if one else 'they'} stood in {name}"
    first = modes_plan.steps[0].name if modes_plan is not None and modes_plan.steps else ""
    if fallback.why == sb.FELL_TIE:
        mode = f" in {s[1]}" if s[1] and s[1] != first else ""
        reason = f"with your {_and(deleted)} made again SolidWorks reads {s[0]} unable to turn{mode}"
    elif fallback.why == sb.FELL_NEW_ERROR:
        mate, now, before, mode = s[0], s[1], s[2], s[3]
        was = (f", which it did not in {active}, the mode {old} showed" if before in ("", "0") else
               f", where it read error {before} in {active}, the mode {old} showed")
        if mate in deleted or mate in fallback.kept or not mate:
            said = _kept_as(mate, kept_of) if mate in fallback.kept else mate
            reason = f"with your {said} made again it reads error {now}" + (f" in {mode}" if mode else "") + was
        else:                                  # one of the app's own mates, put in error by the cluster (A's M3)
            was = was.replace("which it did not", "which it did not before your mates were made again").replace(
                ", where it read", ", where it read before")
            reason = (f"with your {_and(deleted) or 'mates'} made again the app's {mate} reads error {now}"
                      + (f" in {mode}" if mode else "") + was)
    else:
        reason = (f"your {s[0]} made again over-defines {'it' if one else 'them'}" if s[0]
                  else f"with your mates made again SolidWorks reads {'it' if one else 'one of them'} over-defined")
    n = len(deleted)
    gone = ("so it was not kept" if n == 1 else "so those two were not kept" if n == 2 else
            f"so those {n} were not kept") if n else ""
    kept = [_kept_as(k, kept_of) for k in fallback.kept]
    tail = (f"; {_and(kept)} beside {'it' if n == 1 else 'them'} {'was' if len(kept) == 1 else 'were'}" if kept
            else "")
    return f"{head}: {reason}" + (f", {gone}" if gone else "") + tail + "."


def carry_footer_line(record) -> str:
    """§9.4: while the current revision holds what Build again… carried unsaved (``CarryEntry.unsaved_at``), *RangeBox_r2
    holds what Build again… carried of yours, not saved: save it in SolidWorks to keep it.*; ``""`` otherwise."""
    from . import store
    carry = store.carry_unsaved(record)
    if carry is None:
        return ""
    return (f"{_stem(record.gearbox.assembly)} holds what Build again… carried of yours, not saved: save it in "
            "SolidWorks to keep it.")


def carry_lost_line(assembly: str, old: str) -> str:
    """§9.4: found closed unsaved by a later job, *RangeBox_r2 was closed without saving after Build again… carried
    your work into it, so it does not hold it; RangeBox.SLDASM still does.*"""
    return (f"{_stem(assembly)} was closed without saving after Build again… carried your work into it, so it does "
            f"not hold it; {_file(old) if old else 'the old assembly'} still does.")


def carry_unsaid(again, result, exc: BaseException) -> str:
    """The re-check's N3: what the window says when the carry's own sentence raised, after the build's own (never as
    the build failing): *What was carried into RangeBox_r2 could not be said (KeyError: …); it holds it unsaved: save
    it in SolidWorks to keep it.*, the last clause only when something was written into it; the exception through
    :func:`bare_files`."""
    name = getattr(again, "name", "") or "the new revision"
    said = bare_files(f"{type(exc).__name__}: {exc}").strip()
    unsaved = bool(getattr(getattr(result, "carry", None), "unsaved", False))
    return (f"What was carried into {name} could not be said ({said})"
            + ("; it holds it unsaved: save it in SolidWorks to keep it." if unsaved else "."))
