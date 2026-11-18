# F2, package A, handed back

The span over k teeth of PLAN-PRINTED §3.0, on branch `printed`, against F2-0's interface (`F2-INTERFACES.md` §1).
Pure code; no SolidWorks call is added or changed, and no file but package A's own is touched.

## Commits

1. `b09a036`: `src/gear_generator/gears/span.py` filled (F2-0's stub), and `tests/test_span.py` (new, 76 tests).
2. This note.

No existing test was changed. Suite at `b09a036` (`PYTHONPATH=src`, the import path checked against this worktree):
4824 passed, 1 skipped, 1 failed, the known Tk font test
(`test_workbook_window.py::test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left`); that is
F2-0's 4748 plus these 76. Packages B and C had uncommitted edits to `printout.py`, `swcom.py` and `ui_text.py` in
the worktree during that run; nothing of theirs failed then.

## What was built

All of it in `gears/span.py`; the interface's names (`SpanReading`, the five `KIND_*`, `KINDS`, `NONE`,
`span(derived, recipe)`) are unchanged.

- **`span(derived, recipe)`**, in this order:
  - `"none"` for anything not an external involute section (a ring, its section an `InternalDerived`; a spur ring or
    sleeve, an `InternalDerived`; a bevel gear or crown, a `BevelDerived`; anything else), for a machined gear, and
    for a recipe that is neither "A" nor "B";
  - `"arcs"` on recipe B, no figure (§3.0's ruling);
  - `"no_contact"` when no k from 1 to z − 1 has its contact radius between `max(flank_start_d, form_d) / 2` and
    `d_a / 2 − 0.2`;
  - `"narrow_face"` for a helical gear whose face, or a herringbone whose `toothed_width`, is under
    `W_n sin β_b + 3` at the k chosen, with that figure in `needed_face_mm`;
  - else `"span"`: k, `w_mm` = W_n, `w_t_mm` = W_t, `contact_d` = 2 r_c.
  A `SpurDerived` covers a spur gear, a dog and a hub (`clutch._as_spur`); a `HelicalDerived` with a `SpurDerived`
  section covers a helical and a herringbone gear. Pure; it raises nothing for any gear a kind derives (tested on
  every kind, both recipes, both processes, and on `None`, `0`, a string and a bare object).
- **`span_over(derived, k)`**: the formula alone at a given k, whatever the process and with no bound (the plan's
  machined row is "the formula only"); `NONE` for a gear not measured with jaws.
- **`contact_bounds(section)`** and **`choose(radii, target, low, high)`**: the bound and the choice of k, public so
  that the rule is tested on its own (below).
- **`base_helix_angle(beta, alpha_n)`**: sin β_b = sin β cos α_n.
- **`measured(reading, measured_mm, alpha_n_deg, module) -> Optional[Measured]`**, `Measured(flank_mm, backlash_mm,
  floored, over_default)`: the arithmetic back from a caliper reading, e = (reading − W_n) / 2, j = 2 (e + 0.04) /
  cos α_n with the gear's own normal angle, never under 0.1 mm (`floored` True when held there), `over_default` True
  when the proposed j exceeds 0.3 × module. None when no reading is typed or the reading is not `"span"`.
- Constants: `TIP_MARGIN_MM` 0.2, `FACE_MARGIN_MM` 3.0, `KEPT_PLAY_MM` 0.04, `BACKLASH_FLOOR_MM` 0.1.

## The formulas and their sources

- **The span** (§3.0): W_t = (k − 1) π d cos α_t / z + d_b (s_t / d + inv α_t), W_n = W_t cos β_b, sin β_b = sin β
  cos α_n; `s_t` the derived section's `s` (backlash and shift in it; a helical section's thinned by j / cos β, so
  the app's backlash is normal). The closed form W_n = m_n cos α_n [(k − 0.5) π + z inv α_t] + 2 x m_n sin α_n −
  j_n cos α_n is computed in the tests from each row's numbers alone. Source: KHK's *Gear Technical Reference*, span
  measurement, Tables 5.10 and 5.11, with `A_Wk = A_sn cos α_n`, as the plan cites it; DIN 3960 and ISO 21771 not
  checked. **No printed worked example was found**; as §3.0 provides, the check is the app's own outline (below).
- **The contact radius** (§3.0, M1): r_c = √(r_b² + (W_n cos β_b / 2)²); k nearest r + x m_n.
- **The textbook k the tests compare** (not used by the code): k = z / π (tan α_M / cos² β_b − inv α_t − 2 x tan α_n
  / z) + 0.5 through d_M = d + 2 x m_n, cos α_M = d_b / d_M, rounded. This is the rule as this package and F2's
  review know it (ISO 21771 / DIN 3960's form, KHK's shifted spur rule at β = 0), not checked against the standards'
  text; it reproduces the review's unrounded figures (2.72, 1.83, 3.83, 2.62, 3.72, 1.94; 2.94, 3.80, 3.79).
- **The narrow face** (§3.0): b ≥ W_n sin β_b + Δb, Δb = 3 mm (KHK's text, "Δb > 3 mm").
- **The Measured line** (§3.0, §3.2): e = (W_measured − W) / 2; j = 2 (e + 0.04) / cos α_n; floor 0.1; the line past
  0.3 × module (`spur.BACKLASH_FACTOR`).

## The figures, recomputed

Every row of §3.0's table agrees with the plan to 1e-4 mm in both forms, and with the outline:

| Gear | k | W_n (W_t) | r_c |
|---|---|---|---|
| spur m 1.5, z 20, printed | 3 | 11.20875 | 15.1687 |
| spur m 1.5, z 20, machined (`span_over`; `span` is none) | 3 | 11.06780 | 15.1428 |
| spur m 1, z 12 | 2 | 4.31436 | 6.0367 |
| spur m 2, z 30 | 4 | 21.22334 | 30.1219 |
| spur m 1.5, z 15, x +0.3 | 3 | 11.41153 | 12.0130 |
| spur m 1.25, z 29 (Sun) | 4 | 13.14137 | 18.2554 |
| spur m 1.25, z 13 (Planet) | 2 | 5.48093 | 8.1119 (bound 7.635) |
| helical m_n 2, z 20, β 15° | 3 | 15.09719 (15.56454) | 20.7129 |
| helical m_n 1.5, z 25, β 20° | 4 | 15.84379 (16.73147) | 20.0617 |
| helical m_n 2, z 20, β 30°, face 14 | 4 | 21.22548 (24.04478) | 23.2602 |

Faces needed: 6.672, 8.092, 12.973 mm (β_b 14.076°, 18.747°, 28.024°). The β 30° gear at face 12 (and 10, and 12.97)
reads `"narrow_face"` with 12.9727; at 12.98 it reads k 4.

**The outline check** (`test_the_span_read_off_the_drawn_outline_is_the_formula`): `SpurGear.outline`'s recipe-A
points on tooth 0's clockwise flank and tooth k−1's counter-clockwise flank are each turned back to their involute's
base-circle origin (θ ∓ inv α_r); every point of a flank gives one origin to 1e-12 rad, and r_b times the angle between
the two origins equals the formula's W_t to 1e-4 mm on all nine printed rows (the helical rows on their transverse
section, then × cos β_b), and to 1e-9 for k 1 to 5 on the m 1.5, z 20 gear.

## Choices the plan left open, each the coordinator's to rule

1. **The arithmetic of the Measured line is in `span.measured`.** The task gives package A "the arithmetic from a
   user's measured span back to a backlash"; `F2-INTERFACES.md` §6 says C computes it in `ui_text.span_rows`. Both
   cannot be the one source: C's work in progress (uncommitted when this was written) has its own `measured_line`
   doing the sums. **For the coordinator:** whether C calls `span.measured` (one source, A's tests on the sums, C's on
   the words) or keeps its own (then `span.measured` is unused and should go). Nothing in the interface changes
   either way.
2. **k = 1 is allowed.** The textbook k is 1 on a z 6 pinion (1.17) and on m 1.5, z 20, x −0.5 (1.47), and k 1 (jaws on
   both flanks of one tooth) is the same base tangent length. k runs 1 to z − 1.
3. **"The next k inward or outward"** is taken as the nearest k among those whose contact is inside the bounds, which
   is the same k (r_c grows with k) and also covers a case two steps away. A tie goes to the smaller k; a contact exactly
   on a bound is inside. On the app's own gears the next-k branch never arises: a sweep of spur gears (z 6 to 50,
   m 0.5 to 2, 14.5° to 30°, x −1 to +1, default and large fillets) and helical gears (β 15° to 75°) found the bound
   acting only as "no contact", on heavily negatively shifted pinions (z 6 to 9, x −0.7 to −1) and at β 75°, where
   z − 1 teeth do not reach the involute. So `choose` is tested on made-up radii.
4. **The order** none, arcs, no_contact, narrow_face, span: a machined arcs gear reads "none" (no row, as the rule
   asks); the face is judged at the k the contact rule chose.
5. **An unknown recipe** (`""` or anything but "A" and "B") reads "none", not a figure: `span` cannot know the default
   recipe without `findings`, and B passes `kind.recipe_for(spec)`, which is never blank.
6. **Names beyond the interface**: `span_over`, `contact_bounds`, `choose`, `base_helix_angle`, `measured`,
   `Measured` and the four constants. None of the interface's names changed.

## What the reviewer should look at hardest

- **The outline check's independence.** It reads the base-circle origins of the drawn involute, so it rests on the
  involute property of `involute_point` and on `phi` (from the space and inv α); the formula rests on `s` and inv α.
  Both come from `spur.profile`'s `space`. It tests the app's backlash, shift, mirroring and patterning conventions,
  as §3.0 asks, but it is not a caliper simulation of the polyline (13 points a flank are too coarse for 1e-4 mm).
- **The contact bound's lower limit is at the base circle on most printed gears** (`form_d` = `d_b` when the rack's
  reach is negative, and `flank_start_d` = `d_b` until z ≈ 23), so it almost never acts; the tip margin is what
  stops a heavily shifted pinion. Whether the plan meant the bound to act more often is worth a look.
- **The helical lower bound** uses the transverse section's `flank_start_d` and `form_d` (`form_d` from the
  transverse pressure angle and the normal module, as `spur.profile` computes it for every helical section).
- **`measured`'s `over_default`** compares the proposed (floored) j with 0.3 × module, as §3.0 words it, not with the
  printed default min(0.3, 0.3 × module): on a module 1.5 gear a printer adding 0.12 mm proposes 0.34 mm, over today's
  printed 0.3 but not flagged. That is the plan's wording; U4 is the user's.

## Needs the others before it shows

- The span on the form, the Measured entry and its line, the print list's span lines and the explainer are C's.
- `PrintPart.span` is B's, from `span(kind.derive(spec), kind.recipe_for(spec))` per part.
- Nothing here waits on the probe or any finding: the span is pure maths and shows whatever the findings are.
