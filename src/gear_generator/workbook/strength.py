"""What each Meshes row's teeth take, mode by mode, against what they are rated to take (PLAN-PRINTED §5.2, §5.4).

**Package B's, from F4-0's stub** (docs/notes-printed/F4-INTERFACES.md §4). F4-0 fixes the names below, which package
C's boards and the Results block read, and leaves them neutral: :func:`mesh_strengths` gives nothing and
:func:`warning_sentence` says nothing, so a gearbox reads exactly as it did until B writes them. B may add fields after
the ones here; it does not rename or reorder them.

The figures come from :mod:`gear_generator.gears.strength` (F4-0's, package A's maths, whole): `rate`, `holds`
(with the mesh's width and `two_way`), `torque_held`, `allowable_mpa`, `PLANET_SHARE` and the rounding helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Sequence, Tuple

from ..gears.strength import ToothRating

# The states of one Meshes row in one mode (§5.2, §5.4; the review's S3).
RATED = "rated"                    # loaded here, at least one of its gears rated: force, weaker, share
UNLOADED = "unloaded"              # not loaded here: a stage that idles, a branch reaching no output, a free member
NOT_SHARED = "not shared"          # loaded past a shared output, which kinematics does not share out (J17)
NOT_RATED = "not rated"            # loaded here, and neither gear rates
BEVEL = "bevel"                    # a bevel pair: never rated (§5.1)
CROSSED = "crossed"                # a crossed helical pair: never rated (§5.1)

# The Results block's two wordings where no force is worked out (§5.4), never *no torque here*.
TURNS_UNLOADED = "turns unloaded here"
NOT_SHARED_OUT = "the torque past a shared output is not shared out (not worked out)"


@dataclass(frozen=True)
class GearSide:
    """One gear's side of a mesh in one mode: its Gears-sheet id, its rating (:func:`strength.rate` of its derived
    gear), what one tooth is rated to take in this mesh at the allowable, N (at the mesh's width, × 0.7 when
    `two_way`; None when the gear is not rated), and whether its teeth are loaded in both directions as the gearbox
    runs (an idler or a planet: a shaft torque of exactly 0 in this mode)."""

    gear: str
    rating: ToothRating
    held: Optional[float] = None
    two_way: bool = False


@dataclass(frozen=True)
class MeshStrength:
    """One Meshes row in one mode (§5.2). `row` is its Meshes-sheet row; `mode` the mode's name, `""` for a gearbox
    with no modes; `force` Ft at the pitch circle, N (None unless RATED); `width` b, mm, the faces' overlap;
    `sides` the two gears, a then b; `weaker` the id of the rated gear with the smaller figure; `share` Ft over that
    figure, a fraction (1.0 is 100 %); `planets` N for a planetary mesh (the force then shared with K_γ), else 0;
    `unrated` the ids of its gears not rated (a ring whose tips lie inside its base circle), whose share then counts
    the gear that rates alone, a true lower bound."""

    a: str
    b: str
    row: int
    mode: str = ""
    state: str = RATED
    force: Optional[float] = None
    width: float = 0.0
    sides: Tuple[GearSide, ...] = ()
    weaker: str = ""
    share: Optional[float] = None
    planets: int = 0
    unrated: Tuple[str, ...] = ()


def mesh_strengths(spec: Any, report: Any) -> Tuple[MeshStrength, ...]:
    """Every Meshes row of a printed gearbox in every mode, in the Meshes sheet's order and each mode's (§5.2); `()`
    for a machined gearbox or one whose first input has no torque.

    F4-0's stub, package B's to write: gives nothing, so nothing is said and no Results block is written."""
    return ()


def warning_sentence(rows: Sequence[MeshStrength], allowable: float, typed: bool) -> str:
    """The one warning at a Meshes row (§5.4, F4-INTERFACES §6): `rows` that row's MeshStrength in every mode;
    `""` when it says nothing (no share past 100 % and no gear not rated in a loaded mode).

    F4-0's stub, package B's to write: says nothing."""
    return ""


__all__ = [
    "BEVEL", "CROSSED", "GearSide", "MeshStrength", "NOT_RATED", "NOT_SHARED", "NOT_SHARED_OUT", "RATED",
    "TURNS_UNLOADED", "UNLOADED", "mesh_strengths", "warning_sentence",
]
