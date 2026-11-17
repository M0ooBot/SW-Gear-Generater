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

## Second reading: `c997e85` and `ff98d5a` (2026-11-17)

Independent review of the two commits that answer the review above, read at head `64bec58` on Linux against the
fake, with no SolidWorks. Line numbers are at `64bec58`. The whole suite ran once: 3682 passed, 10 skipped, 2 failed.
Both failures, and 8 of the skips, are this Linux venv lacking `tkinter`, not the code:
`test_gears_clutch.py::test_the_strip_never_offers_them` imports `gui`, and
`test_ui_text.py::test_the_end_view_readout_always_fits_and_lists_up_to_four_heights` imports `workbook_gui`.
`test_workbook_window.py` is skipped whole, which is why the known font-width failure does not show and the counts
are lower than the other device's. The ninth skip is the bevel recipe B ring, which is refused. `test_swbuild_landing.py`,
`test_workbook_in_place_round_trip.py` and `test_swbuild.py` pass (550).
Every finding marked **shown** was run with a throwaway test outside the repo.

### The earlier findings at head

- **M1: answered.** `swbuild.py:1448-1455` sets the final count and rebuilds whatever leg one's rebuild returned. It
  stops at the intermediate only where the count's own set failed (`:1452`). That stop leaves `changed` empty for a
  count-only change, so nothing is called changed. Pinned by
  `test_a_first_leg_whose_rebuild_reads_false_still_goes_on_to_the_workbooks_count`.
- **M2: answered.** At `swbuild.py:3788-3800` the landing lines are nested under `if result.changed:`, and
  `elif not result.failures` is that `if`'s again. Pinned for a spur and a ring.
- **M3: partly.** `update.py:2256-2264` no longer clears the mark because a press ended clean, and a press that set
  nothing now says so (`ui_text.py:1880-1892`). But the mark goes only through `_documents_rebuilt_clean`
  (`update.py:2308-2314`), which needs `d.rebuilt`. A part's rebuild reads False whenever the user's own feature is in
  error (P0), so a part the press did put right can never clear its mark. See N1.
- **S1: answered.** `_global_values` (`swbuild.py:1476-1491`) evaluates only names without `@`, in order. It leaves
  out a value that is refused, complex or not finite, and `:1439-1442` catches the foresight as a whole. The fake
  reads globals the same way. The test covers a dimension equation, an unknown function, a complex value and an
  overflow.
- **S2: answered** (`landing.py:64-69`). A part with any global whose name contains `Inner Diameter`, other than the
  ring's own, is not classified. Only a user's global could trip this on an external gear (note 3).
- **S3: answered** (`landing.py:7-21`, `:36-39`). The figures now match the seventh run's log line for line
  (0.0379/0.0378 failed; 0.0996, 0.1276, 0.1438, 0.1730 clean), the Sun figures are 3.57 and 1.57, and the
  `Li+` length nit is fixed.
- **S4: answered** (`swbuild.py:1456-1460`). A module alone that lands goes via 54 and back. `changed` is
  `["Module"]`, the count stays in `unchanged`, and the log says "went by way of … and back". This is not so when
  leg two's set fails (N3).
- **S5: answered, by a weaker test than asked** (`swbuild.py:1507-1508`). The recipe is told by any dimension
  equation whose name before the `@` is `HalfSpace`, `Flank`, `Base` or `Pitch`, in any sketch. A user's own
  dimension named one of those blinds a recipe A part (N2).
- **S6: answered** (`update.py:2734-2740`, `:2771`, `:2996-3006`). `modes_read` is the plan's configurations less
  `in_place.modes_added`, which is `box.modes` less the modes the plan removes, in the record's spelling.
  `follow_modes_added` adds only the added modes on record that appear in `took_active_state`. `refused_update` uses
  the same rule. Records without `modes` read `[]` through `_known` and take the old fallback. Records written by
  `0eb0768`–`5c02c6a` keep their `box.modes` value until the next read, which is harmless for the demonstration's
  fresh snapshots.
- **S7: answered** (`update.py:2268-2298`). `document_stem` and `names_document` (stem, then end, `.` or space) are
  shared by `ui_text._parts_left_in_error` and the record mark. `Gear_m1.25_N2` never names `Gear_m1.25_N29`.
- **S8: answered for leg one only.** If the count's set fails in leg two, the part is left at the intermediate count
  (N3).

### New findings

**N1 (must-fix). After a stop, a part whose rebuild reads False only because of the user's own feature keeps its
in-error mark for good. Each later press then says it "set nothing in it" and to close it without saving, in a
loop.** `update.py:2314` clears the mark only for `d.changed and d.rebuilt`. `_update_document`
(`swbuild.py:4015-4018`) already makes a False rebuild a failure unless the user's features alone are in error
(`theirs_alone`). So a document this press changed, with no failure naming it, has the app's features clean, yet its
mark is kept. `out.still_in_error` (`update.py:2263-2264`) is then everything still marked, including documents this
press did change.
*Shown:* `Desk`, `range_box`, `rebuild_ok = False`, Sun backlash pressed. The stop marks Sun. Then:
1. `close_all()` (as told), `rebuild_ok = True`, and a user feature `Keyway` at code 41 in Sun's part. Pressed
   again: `failures == []`, and Sun is `changed == ["Backlash"]`, `rebuilt False`.
2. The status says both "Save Gear_m1.25_N29 and RangeBox in SolidWorks to keep them" and "Gear_m1.25_N29 is still
   open … so this press set nothing in it: close it in SolidWorks without saving". The mark stays, and the footer
   says "was left in error when it stopped: close them all … without saving".
3. Closing without saving and pressing a third time gives the same status and the same mark, every time.

Real cases look like this: a K3 user fillet that errors at the new count, or a keyway already in error before the
Update. The user is told never to save, which is the only thing that would clear the mark.
*Fix:* in `_documents_rebuilt_clean`, drop `d.rebuilt`: changed, and no failure names it. Make `still_in_error`
leave out any document this press changed. The remake section's M3 steps run the same either way: step 2 changes
nothing, and step 3's ring rebuilds True.

**N2 (should-fix). A recipe A part whose user named a dimension `Pitch`, `Base`, `Flank` or `HalfSpace` is taken for
recipe B, and its landing goes straight** (`swbuild.py:1473`, `:1507`).
*Shown:* ring m1.25 55 with `"Pitch@Sketch9"= 12` among its equations. `_landing_route` returns `([], None)`; set to
54 on the fake, it lands on the far branch (Tooth Space 72).
*Fix:* match only the tooth space's own sketches: the name after `@` is `spur.SPACE_SKETCH`, or a bevel's heel or toe
section sketch. Better still, take the recipe from the record onto `DocumentValues`, as the first review suggested.
Neither changes a demonstrated path: the recipe B case's links are on `Tooth Space Sketch`, and the recipe A cases
have none.

**N3 (should-fix, rare: the second set has to fail after the first succeeded). If the count's set fails in leg two,
the part is left at the intermediate, and the result says otherwise** (`swbuild.py:1455-1460`).
*Shown* with a fake that refuses only the second set of `No. of Teeth`:
- Ring 55 to 54 holds 53, with `rebuilt True`. The log says "set … by way of 53 first, rebuilt there, then the
  workbook's value" and "rebuilt twice". The part is not "left in error", so the stop offers to save a ring at a
  count that is neither the old one nor the workbook's.
- A module alone (m1.225) holds 54. `changed == ["Module"]` and the count is in `unchanged`, though it was changed
  and never set back.

The failure itself is reported, and `finish_update` records nothing for a part with failures.
*Fix:* if the final set fails, keep the count in `changed` (skip the S4 removal) and set `result.rebuilt = False`.
The part then reads as left in error and the stop says to close it without saving.

**N4 (should-fix). The status after a press that set nothing loses the rest of its sentence**
(`ui_text.py:1891-1892`). When the text starts with `ALREADY_MATCHES`, the wrapper returns the still-in-error
sentence alone. `_gearbox_update_status` adds more after `ALREADY_MATCHES`: the interference ending when a mode's or
the assembly's check found clashes, the user-work sentences, `in_place_after`, and the leftovers sentence. All of
these are dropped.
*Shown:* the M3 press on `Desk` builds "SolidWorks already matches the workbook: nothing was changed. It worked in H,
… since nothing in H needed changing." It says only the still-in-error sentence. A clash found by a quiet press would
be dropped the same way.
*Fix:* replace only the prefix: `said + text[len(ALREADY_MATCHES):]`. The demonstration matches sentences by their
distinctive parts, so its remake step 2 still matches.

### Notes

1. **The maths is right for the lines it claims, profile shift included.** For spur (z 12–80) and ring (z 25–80), at
   x 0, 0.3, −0.2 and 0.5 and m 1, 1.25 and 2.5, `landing._line` equals `spur.involute_flank` (`start`,
   `line_inner`) and `internal.involute_flank` (`start`, `cap`) to 0 mm. A ring refuses a shift. Helical, sleeve and
   dog draw the same sketch at the origin from the same globals. A module change and a count change together are
   foreseen from the globals as they would be set, and the route keeps the new module for both legs (40 m1.25 → 32
   m1.5 via 31 at m1.5, as measured).
2. **Intermediates are safe in practice.**
   - Every routed ring (m 0.5–3, z 20–150, one to four down: 620 cases) and every routed sleeve takes `wanted − 1`.
     That is smaller, so it is safe against a typed rim.
   - Spur intermediates are 14–18 at m ≤ 1.25 and 9–13 at m ≥ 2. None reaches 6 or 7, where `caps_with_arc` would
     want an arc for a chord-built part.
   - The `n < 5` floor is below the spur's minimum of 6. That is harmless today, but `n < 6` (or the kind's own
     minimum) would be truer.
   - Both legs are foreseen (`swbuild.py:1524-1525`). The intermediate is never the count held or wanted.
   - Leg one sets every other global at its final value. The foresight's `mid` models exactly that hybrid.
   - Nothing is saved.
3. **The external bevel gear is foreseen in a frame its sketch does not have.** Its globals are the spur's
   (`spur.profile_variables` on the back cone), so `_line` reads it as `L+`. Its sketches are the heel and toe
   sections, moved by `Heel/Toe Virtual Radius` and scaled by `Heel/Toe Scale` (`bevel.py:1065-1080`,
   `spur._framed`), and both of those move with the count. In sketch coordinates the fraction differs. For example,
   m1 mate 20 at 90°, 20 → 19, is 4.09 by the foresight and 1.21 (heel) and 0.83 (toe) in the sketch.
   A sweep was run: m 1 and 2; shaft 60, 90 and 120°; mate 10–60; z 8–69; −1 to −3 and +1; 6532 cases. Nothing
   below 0.2 in either sketch was missed, and 14 cases were routed needlessly (shaft 120°, z 9–11). That is harmless
   today, but the docstring's "the sketch's geometry is a function of [the globals]" is not true of a bevel. The fix
   is to leave a part with a `Heel Scale` global unclassified, or to measure in the section's frame.
4. **Small items.**
   - The S2 guard also blinds an external gear that carries a user global whose name contains `Inner Diameter`.
   - At head, 0.2 routes the externals measured clean straight at 0.0996 and 0.1276 (m ≤ 1.25, 16→15 to 20→19). They
     cost one more rebuild each, which is known and acceptable.
   - The run-7 note "each with the old end toward the cap" is a ring's words. For `L+` the line runs toward the
     root.
5. **Records.** Schema 9 records written by `0eb0768` to `5c02c6a` read at head:
   - `unsaved_in_error` and `UserWorkEntry.modes` default to `[]` through `_known`;
   - `store.clear_saved` and `keep_in_error` drop the mark when the file is saved, missing, or found closed;
   - a stale mark cannot outlive its `unsaved` entry.

   A user who saves the part in error against the advice clears both. The next press then says "already matches"
   for a part still in error, which is the first review's "note for later" and is unchanged.

### Tests that matter and are missing

- N1: a re-press after a stop where the marked part changes clean but reads False from a user feature.
- N3: a route whose second set fails, for a count change and for a module alone.
- N2: a recipe A part with a user dimension named `Pitch` (or `Base`).
- N4: the still-in-error status keeping what follows `ALREADY_MATCHES`.
- A bevel external's landing pinned to whatever rule note 3 settles.

The happy paths and each first-review item are pinned. The fake's 0.05 threshold still means nothing between 0.05
and 0.2 fails there, which is fair to the evidence.

### Must the SolidWorks demonstration be run again?

**No.** N1, N4 and N2's record-side fix are Tk-thread code, and they change no call the worker makes:
- **N1:** the remake section's M3 step 2 changes nothing, and step 3's ring rebuilds True, so they come out the same.
- **N2:** the narrower fix (a sketch-name match) changes what the worker routes only for a part carrying a user
  dimension named `Pitch`, `Base`, `Flank` or `HalfSpace`, and no demonstrated part has one.
- **N3:** it touches only a failed second set, which no run provokes.

The running 2026 run, on head's `src/`, stays valid evidence for these fixes. Its status text for remake step 2 will
read as N4 describes, without what follows "already matches". That is a wording fact, not a worker one.

## Re-check of the second reading's fixes, 2026-11-17

This is a re-check of the builder's `8792512` (N1), `ef4b8f2` (N4), `6585f6d` (N2), `535a019` (N3) and `6aacc90`
(the note-4 guard). It reads head `550767c`, whose `src/` and `tests/` are `6aacc90`'s. Line numbers are at that head.
`550767c` itself is the run agent's and touches `probe/` only.
- **Suite:** 3691 passed, 10 skipped, 2 failed. The two failures are the `tkinter`-only pair named above.
- **Repros:** the second reading's throwaway repros were re-run against head. Each new regression test was run in a
  scratch copy of `src/` and `tests/`, once against head and once with the fixed file put back as it was before its
  fix. All 9 new tests pass at head, and every one fails on its pre-fix file.

### Per finding

- **N1: fixed.**
  - `update.py:2310-2320`: `_documents_rebuilt_clean` now asks only `d.changed` and no failure naming the document.
  - `update.py:2266`: `still_in_error` leaves out every path in `result.changed`.
  - *Repro:* the second reading's case, closed and changed again beside the user's keyway at code 41. The mark goes,
    the status says only "Save Gear_m1.25_N29 and RangeBox in SolidWorks to keep them", and the footer's unsaved line
    is the ordinary save offer. The third press is the same.
  - *Test:* `test_a_part_left_in_error_then_put_right_beside_the_users_own_feature_in_error_sheds_its_mark` fails on
    `23dfa01`'s `update.py`.
  - *Can the mark now go while the app's own feature is still in error?* Not through any path the code has.
    - In `_update_document` (`swbuild.py:4038-4058`), a changed document with a False rebuild gets the failure
      `(name, "SolidWorks reported an error rebuilding …")`. The only exceptions are `theirs_alone` and N3's
      `left_on_the_way`.
    - `left_on_the_way` carries its own failure, `"<file> \"No. of Teeth\""`, so it is never cleared.
    - `theirs_alone` needs three things: features read (a raise or an empty read makes it False); every feature in
      `doc.made | doc.features` read neither in error nor `UNREAD`; and `WHATS_WRONG_OPENS_ON_PART_REBUILD is False`.
      An empty `doc.made` also makes it False.
    - The band step (`swbuild.py:6230-6245`) raises on any app feature in error.
    - So no failure naming the document means the app's features read clean.
  - *What names a document in a failure:*
    - every failure a document's own step makes is `_file(doc.path)`, alone or followed by a space;
    - `UpdateResult.document` is `GetTitle`;
    - `names_document` compares stems, case aside.

    The match could miss only if `GetTitle` ever differed from the file name by more than the extension. No log shows
    that, so this is a note.
  - *Can leaving every changed path out of `still_in_error` hide a part still in error?* Only when a path is in
    `result.changed` but has no changed `UpdateResult`. That happens to a sleeve whose bands alone this press gave. Its
    mark is not cleared, and the band step raises if the app's features are in error, so it is never hidden in error.
    What remains is the reverse, a stale mark: the footer keeps "left in error … without saving" while the status
    says to save. That is a note: it needs a sleeve marked by an earlier stop that healed in a band step.
- **N4: fixed** (`ui_text.py:1891`). It now replaces `ALREADY_MATCHES` exactly and keeps the rest.
  - *Repro:* the status keeps "It worked in H … nothing in H needed changing".
  - *Tests:* `test_a_quiet_press_on_a_part_still_in_error_replaces_only_the_claim_and_keeps_what_follows`, and the
    round trip's amended check, fail on `23dfa01`'s `ui_text.py`.
  - *What can follow the claim:*
    - the interference ending;
    - `_mode_after`;
    - `_earlier_update_sentence`, put after the claim by `_joined`;
    - `_rebuild_from_user`, `_user_after`, `in_place_after` and the leftovers.

    `save_to_keep` and `WHATS_WRONG_AFTER` are never added on that branch. One can contradict:
    `_earlier_update_sentence` with `UPDATE_LOST` and nothing changed says "SolidWorks already holds the workbook as it
    now is, so nothing needed making again" (`ui_text.py:3571`).
    - This happens when an earlier clean Update's assembly change was lost (the assembly was closed unsaved) while a
      part a later stop left in error is still open. The status would then say the part is in error and also that
      SolidWorks holds the workbook.
    - *Not reproduced:* closing only the assembly on the fake left `open_before` holding it, and the press read
      "not saved".
    - A note, with an easy fix: pass `still_in_error` to `_earlier_update_sentence`, or drop that clause when it is
      non-empty.
- **N2: fixed** (`swbuild.py:1500`, `:1521-1526`). Recipe B is told only by `HalfSpace`, `Flank`, `Base` or `Pitch` at
  `Tooth Space Sketch`, `Heel Section Sketch` or `Toe Section Sketch`, case aside.
  - *Repro:* the ring with a user's `"Pitch@Sketch9"` is routed via 53 and rebuilds clean.
  - *Tests:* both new tests fail on `6585f6d^`'s `swbuild.py`. One fails as an `AttributeError`, since
    `_arc_recipe_link` is new.
  - *Every kind, from the plans the code generates* (scratch script over `kind.plan` for each spec):
    - spur, helical and herringbone, external and internal, sleeve, dog, hub and the external bevel: recipe B links
      `Pitch`, `Base`, `HalfSpace` and `Flank` in `Tooth Space Sketch`, or in the bevel's `Heel/Toe Section Sketch`.
      All are told.
    - Recipe A of all of these links none. This includes the 6–7-tooth arc-cap spur, which is refused for recipe B,
      as are the shifted 14-tooth spur and the 12-tooth bevel pinion at 60°.
    - The internal bevel (signs stubbed) is told for B, and has no line anyway.
    - One mismatch: the crown gear's **recipe A** links `Flank@Heel/Toe Section Sketch` (`_rack_ops`), so it reads as
      recipe B. That is harmless: a crown has no `Base Radius`, so `_line` foresees nothing either way.
    - Crossed helicals are helical parts; there is no separate kind.
  - *On SolidWorks:* the equation names read back as `"Root@Tooth Space Sketch"`, with no document suffix. These are
    the keys of `equation_values` in the run 6 and run 7 logs, so the exact sketch match holds there.
  - Left over (a note): a user's own `Pitch`, `Base`, `Flank` or `HalfSpace` dimension added *inside* the app's tooth
    space sketch still blinds a recipe A part.
- **N3: fixed.**
  - *What the code does:*
    - `swbuild.py:1463-1478`: on a failed second set, the count stays in `changed`, leaves `unchanged`, and
      `rebuilt = False`. The failure now says the count it holds.
    - `UpdateResult.left_on_the_way` (`:264-268`) drives the log's `FAIL … it holds 53` and the suppression of the
      rebuild-error failure (`:4057`).
    - It needs `by_way_of[0] in changed`, so a count that never left its value cannot trip it.
  - *Repro:* the count case holds 53 with `changed ["No. of Teeth"]` and `rebuilt False`. The module alone holds 54
    with `changed ["No. of Teeth", "Module"]` and the count not in `unchanged`.
  - *Test:* the parametrised test fails on `6585f6d`'s `swbuild.py`.
  - *Every consumer, read and run:*
    - `documents_left_in_error`: changed, not rebuilt, and the count's failure (prefixed `"<file> "`) names it. The
      stop says to close it without saving and never to save it (the test asserts both).
    - `finish_update` (`update.py:2128`): skips the entry, since `done.failures` is set.
    - `marks`: the part is unsaved and marked in error, and N1 never clears it, because a failure names it.
    - The strip's single-part Update (`gui.py:1671`, `ui_text.update_status`): says `failures[0]`, which now carries
      "holds … = 53, … not the workbook's 54". It writes no sidecar.
    - The workbook status's changed pieces (`ui_text.py:1995`) are not reached on a stop.
  - *Suppressing the rebuild-error failure is right:* the rebuild that ran was asked only for the intermediate. The
    count's own failure already names the document, so nothing depends on the extra one.
- **The note-4 guard: fixed** (`landing.py:65`, by `bevel.BACK_INNER` exactly).
  - *Test:* `test_a_users_global_whose_name_holds_inner_diameter_never_hides_an_external_gear` fails on
    `23dfa01`'s `landing.py`.
  - `landing` now imports `bevel`. The import cycle is fine: the suite imports every module.

### The neighbouring case the builder left alone (note, reproduced)

Ring m1.25 40 → m1.5 32, routed via 31, where the count's first set fails: the part holds 40 teeth at m1.5, and
`by_way_of == ("No. of Teeth", "31")`.
- The log says `ok went by way of "No. of Teeth" = 31 and back, rebuilt there first`, which is false.
- `_update_document` adds `SolidWorks reported an error rebuilding Ring…`, though the rebuild of that hybrid read
  clean on the fake.
- The user-facing stop is right: it leads with the count's failure, calls the part left in error, and says to close
  it without saving, which is the right advice for a part at neither the old values nor the workbook's.

So this is wrong only in the log and in a second failure line. It needs a set to fail after another global set in the
same batch. A note.
*Fix:* at `swbuild.py:1461`, before the early return, mark the route as not taken, either by clearing `by_way_of` or
with a flag that `log_lines` reads. Treat it like `left_on_the_way` for the rebuild-error failure.

### The demonstration (point 3)

`probe/w9c_demonstration.py` was read at head. The marks and `still_in_error` exist only in `remake_again` (`:2308-2400`);
no other section stops a part in error. Section by section, against the run in progress on `64bec58`'s `src/`:
- **`landing`:** the worker is the same on every case.
  - Cases 1–7 and 9 have no dimension links outside the app's sketch.
  - Case 8 (recipe B) links at `Tooth Space Sketch`, which head tells the same as before.
  - Case 10's user equation is `UserCutD@…` (`:385`, `:2767`), neither rule's name.
  - No case fails a second set, and no part has a `… Inner Diameter` global or a bevel.
  - One thing to check in the run's log: case 8 prints the dimension links as the app reads them. If they read
    exactly `…@Tooth Space Sketch`, head's rule is confirmed on SolidWorks. If they carry anything else, head would
    route recipe B (one needless rebuild), and only case 8 would need running again.
- **`remake`, M3:**
  - Step 1 is unchanged.
  - Step 2 sets nothing in the ring, so N1 changes nothing. Under N4, the status keeps what followed "already matches"
    only if the press changed nothing at all. If it remade the stage's mates, the status is `text + said` on both
    commits. The check (`:2364-2366`) passes either way.
  - Step 3's ring rebuilds True, so its mark goes on both commits.
- **`fixed`, `modes`, `remove`, `remake` (main), `bands-off`, `m4`, `w9b-part`:** none has an in-error mark, a routed
  landing with a failing set, or a user dimension of those names, so the worker and the record are the same.

**Verdict:** the 2026 whole run on `64bec58` stands as evidence for head in every section. Nothing needs rerunning
on 2026, unless case 8's printed links show a name other than `…@Tooth Space Sketch`.

### Documents that now misdescribe the code (point 4)

- `W9C-INTERFACES.md:741-743` (§11, "From B (the fixes review)", M3): "changed and rebuilt that very document". This
  is now "changed with no failure naming it". Also:
  - `:744` says the sentence comes "instead of *already matches*"; it now replaces only the claim and keeps what
    followed.
  - `:736-737` (the bullet before it), "cleared by a press that ends with no failure", has been stale since
    `ff98d5a`.
- `swbuild.update_variables`' docstring (`swbuild.py:1404`), "in one suppressed batch, and rebuild once", has been
  stale since `63bbc33`. A routed change is two batches and two rebuilds.
- `update._documents_rebuilt_clean`: the name still says "rebuilt clean", although its docstring is now right.
- `HANDOFF-WORKBOOK.md`:
  - `:86-89` say `c997e85` and `ff98d5a` have not been read by a reviewer, and do not mention the second reading
    (`23dfa01`) or these five fixes.
  - `:100` says the last whole run was at `0eb0768`, 3786 passed.
- `W9C-DEMONSTRATION.md:348` ("c997e85 tells recipe B by its sketch's dimension links") is still true in substance.
  Since `6585f6d` it is links in the app's own tooth-space sketch.
- `design/UI-DESIGN.md:1414-1420` is accurate for a press that set nothing. It does not say that a press which changes
  the part clean, beside the user's own error, sheds the warning. Omitted, not wrong.

### New must-fix or should-fix

None. The four notes above — N1's stale-mark reverse, the `UPDATE_LOST` clause after the still-in-error sentence,
the leg-one log, and the user's dimension inside the app's sketch — are all narrow and none is user-facing advice in
error.
