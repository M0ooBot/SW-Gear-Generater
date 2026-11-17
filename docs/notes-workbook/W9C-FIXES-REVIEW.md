# Review of W9c's demonstration fixes: `63bbc33`, `0eb0768`, `d432846`, `5c02c6a`

Independent review, on Linux against the fake, with no SolidWorks. The whole suite ran once: 3789 passed, 1 skipped,
and the one known failure (`test_workbook_window.py::test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left`).
Every scenario marked **shown** below was run on the fake with a throwaway test kept outside the repo. Line numbers are
at `5c02c6a`.

## Must-fix

**M1. A routed change can be left at the intermediate count, with no failure reported** (`swbuild.py:1446`, with
`_update_document` at `swbuild.py:3985-3988`). Leg one returns early when `rebuild()` is False. On 2026 and 2024 a
part's rebuild returns False whenever *any* feature is in error, including one of the user's own (P0). Then
`_update_document` sees only the user's features in error (`theirs_alone`) and adds no failure. The Update carries on
with the part holding the intermediate count, and its log says only *CHECK the rebuild reported an error, from your
features alone*.
*Shown:* ring m1.25 at 55 with a user feature at code 41, then Update to 54. The result is `failures == []`, the part
holds `"No. of Teeth" = 53`, and `by_way_of == ("No. of Teeth", "53")`. Before this commit the same part ended at 54,
with the same CHECK.
*Fix:* after leg one, set the final count and rebuild whatever leg one's rebuild returned. Stop early only when the
count's own set failed. At worst the part then ends in error at the workbook's value, which the stop sentence already
covers. This also mends S8.

**M2. Every changed document's log now says it "already holds the workbook's values"** (`swbuild.py:3763-3770`). The
new `if result.by_way_of / elif result.landing` was put between `if result.changed` and its old
`elif not result.failures`, so that `elif` now hangs off the new `if`. Every plain change with no failure logs both
lines.
*Shown:* Sun m1.25 29 to 30 logs `ok set "No. of Teeth"`, then `ok already holds the workbook's values`, then
`ok rebuilt once`. No test pins this.
*Fix:* nest the landing lines under `if result.changed:` and give `elif not result.failures` back to that `if`.

**M3. A clean press made without closing clears the mark, and the footer then says to save a part still in error**
(`workbook/update.py:2258-2259`, `5c02c6a`). The stop tells the user a press on the failed part "would set nothing",
and that is what happens: the part holds the new values, so `update_variables` sets nothing, rebuilds nothing and
reports no failure. The press "ends clean", and `rec.unsaved_in_error = []` runs.
*Shown:* `Desk`, `range_box`, and Sun given `breaks_on_set` Tooth Space 72. The stop is correct and the mark is
written. The user presses Update again without closing. The press says *SolidWorks already matches the workbook:
nothing was changed*, the mark is `[]`, the part is still unsaved with Tooth Space at 72, and the footer says *save it
in SolidWorks to keep it*. That is the old offer, for a part in error, which is what `5c02c6a` set out to stop.
*Fix:* do not clear the mark just because a press had no failures. Let it go only through `keep_in_error`, when the
document leaves `unsaved` (saved, or found closed and settled from its file), or when this press changed and rebuilt
that very document clean. A note for later, not part of this fix: a press could re-read the features of an open
document marked in error rather than report "already matches".

## Should-fix

**S1. The foresight cannot see a part whose equations hold anything this evaluator refuses, and a few such equations
make the document fail** (`swbuild.py:1470-1479`). `before = evaluate_all(held)` runs over *every* equation in the
part. Two kinds of equation from the user's own work defeat it:
- One that names a dimension (`"D1@Sketch9" = "D2@Sketch9" * 2`) or a function this grammar lacks raises
  `EquationError`, and the route returns `([], None)`. The hazardous change then goes straight.
  *Shown:* ring 55 to 54 with that one equation added gives no landing and no route.
- One that yields a complex value or overflows (`( "a" - "b" ) ^ 0.5` with a < b, or `10 ^ 400`) raises `TypeError`
  or `OverflowError`, which nothing catches. `_update_document` then fails the whole document, part, layout or
  carrier, before anything is set. That document updated fine before this commit.

The fake shares the first blind spot: `FakeSolidWorks._evaluated` returns `{}` on the same error, so the fake also
rebuilds clean.
*Fix:* evaluate only the globals (equations whose name has no `@`), skip any that fail, and catch `Exception` around
the whole foresight. The foresight must never be what fails a document.

**S2. An internal bevel ring is read as an external gear** (`gears/landing.py:57`). A bevel ring's globals carry
`Back Cone Inner Diameter`, not `Inner Diameter` (`test_bevel_forms.py:125`). It also carries `Root Diameter` and
`Fillet Radius`, so `_line` takes it as the external `L+`. Its sketch is `internal.space_ops`, with `Li+` to the cap.
*Computed:*
- mate 16, shaft 120°, z 47→46 and 48→47 are "foreseen" from a line that is not there (0.134 and 0.054); the true
  `Li+` fractions are 7.4 and 6.4.
- mate 20, shaft 150°, every z from 51 to 89 one tooth down has a true `Li+` fraction between 0.03 and 0.2, but is
  read as 1.1 to 1.2 and not foreseen.

Internal bevels are unbuilt on SolidWorks, so this is should-fix, not must-fix.
*Fix:* take "ring" from `Flank Offset < 0` (negative only on a ring), or from either inner-diameter name.

**S3. The threshold's quoted evidence is wrong** (`gears/landing.py:15` and `:31`; the `63bbc33` message; §11 "From
A"). These say Sun 29→28 was "clean at 0.24" and 29→30 at "2.4". By `line_landings` itself, Sun m1.25 29→28 is
**1.565** (landed 0.383 mm on a line 0.244 mm long) and 29→30 is **3.566**. The 0.24 is L+'s length in mm. So 0.2
rests only on 0.038 failing and ≥1.0 clean, and nothing between them has been measured. 0.2 is defensible only as a
guess, and today's straight runs must settle it (see the measurement section below).
*Fix:* correct the docstring and comment.

**S4. A module-only change can be routed, and then the count is listed as both changed and unchanged**
(`swbuild.py:1414`). `result.unchanged` is worked out before the route. Ring 55, m1.25 to m1.225, lands at 0.04
(computed), and the route takes the count to 54 and back.
*Shown:* `changed == ["No. of Teeth", "Module"]`, and `unchanged` also holds `"No. of Teeth"`. The log says
`set "No. of Teeth"` for a count that did not change. `changed` feeds `values_set`, which is what Update says it set
under a user feature in error.
*Fix:* keep a global whose final value equals the held one out of `changed`, or work out `unchanged` again after the
route. Keep the routing itself: the landing is real, by the same maths.

**S5. Recipe B (arcs) parts are routed though their sketch has no such line.** Their globals are identical to recipe
A's (checked: ring 55, recipes A and B, same list), so ring B 55→54 is "foreseen" too. The cost is a needless second
rebuild through a count the user never asked for, and a log line saying a sketch line would have landed when there is
none.
*Fix:* hand the recipe to the worker on `DocumentValues`, from the record's part entry, and foresee only for A.

**S6. `UserWorkEntry.modes` can name a mode the read never covered** (`workbook/update.py:2725` and `:2956`). Both set
it to `box.modes` after the press. Per `swbuild.work_without_modes`, the worker reads only the modes left after the
Update. Take a press that plans to delete mode X but stops before deleting it (for example a ring left in error
earlier in the press): `box.modes` keeps X, the inventory has no flag there, and `modes` claims X was read. If the user
then puts X back in the workbook, the footer takes X as read with every user mate off, rather than as a copy.
*Fix:* `modes` should be the modes the read covered (the plan's modes after the Update that existed at the read),
plus the added modes whose `took_active_state` was written.

**S7. The two "left in error" rules disagree on how they match a document's name** (`workbook/update.py:2278` against
`ui_text._parts_left_in_error`). The stop sentence matches by `startswith(d.document)`. The record mark needs
`basename(path) == d.document` exactly. `d.document` is `GetTitle`, which comes without `.SLDPRT` on a Windows that
hides extensions; every probe log so far shows it with the extension. On such a machine the stop says "close without
saving", the mark is not written, and the footer offers to save.
*Fix:* one shared helper comparing stems, case aside.

**S8. A first-leg set failure on a rebuild that went through** (`swbuild.py:1446`). The route stops at the
intermediate. The part rebuilt, so it is not "left in error", and the stop offers *save it in SolidWorks to keep what
it did* for a ring at a count that is neither the old one nor the workbook's. This is rare (a set has to fail). M1's
fix covers it.

## Notes

- **Geometry: right for both sketches it claims.**
  - Ring `Li+` (`internal.py:741-760`): "origin on Li+" makes the line radial, and "end on cap" puts its end at
    `rc` along the start's direction. `_start(lower=True)` is the upper flank, as `I+` uses
    `_curve_expressions(lower=True)`. It reproduces the probe's dump: 0.0237 mm landed on a 0.625 mm line.
  - External `L+` (`spur.py:1190-1210`): a radial line tangent to a fillet that is itself tangent to the root circle
    from outside has its end at `sqrt(rf² + 2·rf·ρ)`. The test pins this against `spur.involute_flank().line_inner`.
  - Docstring nit: "Li+ … m/2 long" holds only where the flank starts at `inner − m`. Below about 50 teeth at 20° it
    starts on the base circle, and `Li+ = rb − rc`.
- **Which way the old end lies.** The measured failure is purely sideways: the old end sits square to the new line,
  0.000 along it and 0.038 across. Every short case in today's straight set has the old end toward the cap, which is
  the easy direction: 30→28 (0.135 along), 40→32 (0.035), 18→17 (0.032), 17→16 (0.086). None has it on the far side
  of the new start. Examples of that: ring m1 36→34 (0.056, along −0.026) and ring m1 44→42 (0.367, along −0.363,
  not routed). 55→53 was clean at along −1.0.
- **What 0.2 routes in practice.**
  - Rings: one tooth down from about 50 teeth up (0.02 to 0.04), and two or three down at low counts (for example
    m1 30→28 at 0.144, 36→34 at 0.056).
  - Externals at m ≤ 1.25: one tooth down from 20→19 to 16→15 (0.10 to 0.17). Common planet and sun sizes, so many
    Updates now take two rebuilds, though no external landing has ever failed.
  - At m ≥ 2: 12→11 to 15→14.
- **Intermediates.**
  - Only `n < 5` and evaluability are checked. In practice rings almost always take `wanted − 1`, which is smaller and
    so safe against a typed rim (`rim_typed` literal); `+1` past a typed rim could fail leg one.
  - External intermediates can fall below the undercut limit (16→15 via 14). That is a warning, not a build failure:
    13-tooth planets build.
  - Equations that do not evaluate at the intermediate (a bevel's cone) are skipped by `except EquationError`.
  - Clutch, crossed, layout and carrier globals lack `Base Radius` / `Flank Offset` / `Involute t1`, so they foresee
    nothing (fine).
  - Changes with no landing take exactly the old path (`apply(changes)`, one rebuild). Only the log changed; see M2.
- **The fake makes the tests meaningful.**
  - Removing the route fails `test_a_ring_set_one_tooth_down_goes_by_way_of_a_safe_count_and_rebuilds_clean`, and the
    `LANDING_STEPS=()` test shows the far branch persisting.
  - `_ring_lands` uses `internal.section` and `involute_flank`, not `landing.py`.
  - Its 0.05 limit means nothing between 0.05 and 0.2 fails in the fake, and it models rings only, not externals.
    That is fair to the evidence.
  - It shares the evaluate-every-equation blind spot (S1).
- **`0eb0768`'s paths, each true:**
  - a mode added from the mode showing: the flags are read after the worker set the app's mates there;
  - an add and a removal in one press: the read covers the modes after the Update, and `box.modes` drops the removed
    one, except as S6;
  - a press that stops half-way: an added mode is not in `box.modes`, its flags are skipped, and the next plan judges
    it as a copy;
  - a second workbook: guarded by `record_user_work`'s same-assembly check;
  - no user work, or `unread`: nothing is written.
- **The fallback for old records is sound.** A mode no user mate is on in reads as never read and is judged as a copy
  of each mode that was read; only what all of those foresee is foreseen. The stated cost is the only real one.
  - An old record whose user mates are on in no mode at all turns every mode into a copy. Then `shown == []`, and the
    judgement is the raw inventory, exactly as before the fix.
  - The press still reads, and refuses, live.
- **`d432846` / `5c02c6a` decide "left in error" correctly** apart from M3 and S7:
  - It is changed, not rebuilt, and named in a failure. The user's own features alone add no failure where
    `WHATS_WRONG_OPENS_ON_PART_REBUILD` is False, so they do not trigger it.
  - It covers parts, the layout and carriers.
  - The sentences are true: the failed part holds the new values, a press sets nothing, and the files on disk are as
    before the Update.
  - Other stops keep the offer (pinned by `test_a_stop_with_nothing_changed_in_error_still_offers_to_save`).
- **Pre-existing, unchanged here:** an exception from `rebuild()` (not a False) comes back from `_update_document` as
  a fresh `UpdateResult` with `changed == []`. A part already set is then neither "changed" nor "left in error". The
  route now calls `rebuild` twice, which doubles the exposure.

## What SolidWorks should additionally show

The planned cases (routed: ring m1.25 55→54 and 56→55, ring m1 30→28; the same set straight; external m1 18→17 and
17→16; unrouted: ring 55→53, 55→56, Sun 29→30; ring m1.25→m1.5 with 40→32) have these gaps:

1. **Cases just above 0.2, which the fix leaves direct.** None is planned, and these are what decide whether 0.2 is
   high enough: ring m1 27→25 (0.204), spur m1 15→14 (0.203), spur m1 14→13 (0.239).
2. **A short landing whose old end lies beyond the new start**, run straight: ring m1 36→34 (0.056, along −0.026).
   Also ring m1 44→42 (0.367, along −0.363), which is not routed. Every short case planned has the old end toward the
   cap.
3. **External m1 18→17 and 17→16 run straight as well as routed.** The list does not make clear that they are in the
   straight set. No external landing has ever been seen to fail, so straight is what tests the external half of the
   foresight.
4. **A landing with no tooth change:** ring m1.25 N55, module 1.25→1.225 (0.04), straight and routed (S4).
5. **Recipe B ring m1.25 55→54 straight:** expected clean, which would confirm S5's route is needless.
6. **The M3 path:** after the routed fix is off (straight 55→54 fails), press Update again without closing. Confirm
   the part stays at code 72 and the press says it matches.
7. **A dump for each straight case:** `Li+` / `L+` endpoints before and after, and whether the end went to the far
   side. That gives the along/across picture, not just pass or fail.
