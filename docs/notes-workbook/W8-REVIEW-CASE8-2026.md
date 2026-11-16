# Review of s7 case 8 on SolidWorks 2026 34.1.1, and what was written from it

*Independent, 2026-11-15. I changed no code and started no SolidWorks.* Under review:

- `9bd3a58`: the run's log and result,
  `probe/results/w8-workbook-assembly-20261115-220745-s1-s7-case8.log` (written ":N" below) and
  `probe/results/w8-s7-20261115-222252-case8.json`.
- `0e7f203`: the comments on `POSITIONS_PER_CONFIGURATION_ON_2026` and `TURN_PER_CONFIGURATION_ON_2026` in
  `src/gear_generator/findings.py`, ruling 9.18 in `W8-INTERFACES.md`, `HANDOFF-WORKBOOK.md`, and the new pins in
  `tests/test_findings.py`.

Line numbers are at `0e7f203`. For comparison I used 2024's case 8 (`6b16963`), s2's 34.0.0 log
`probe/results/w8-workbook-assembly-20261115-151412-s2.log` ("s2:N"), and the probe and app source.

**Verdict.**

- Every reading the commits cite is in the files: per mode, per step, by the numbers. Case 8 at `fe74276` holds its
  own Update, so `W8-REVIEW-LATE-FIXES.md` MF1 is met. The pins are real. The two result files carry nothing
  personal beyond the `C:\Users\M0obo\…` paths earlier logs already carry.
- No must-fix. Pushable once the first should-fix is in, since it is a one-word misreading of the very claim. The
  others are records and can follow, but should land before the closing run, whose s2 re-reads the open state.
- Should fix:
  1. The handoff's sentence on the moving put reads as if the put stayed in all four modes (S1).
  2. The comments present case 8 as the s2 sequence on another revision. It is not. Its Update reading repeats
     34.0.0's own first press, so it adds no difference (S2).
  3. Five places still say case 8 "is to settle" or "is to measure" this, or that it is open on 2026 (S3).
  4. The in-Update reading the comments cite is in the log only. It is not in the JSON and not pinned (S4).

---

## What the files hold (question 1)

I read the JSON with Python, step by step and mode by mode, and grepped the log. Turns are the first element of each
`expressed` entry (degrees from the frame on record).

| Step (`case 8`) | 2H | 4H | N | 4L | Judgement |
|---|---|---|---|---|---|
| as copied | 0 | 0 | 0 | 0 | — |
| drive +37 in 2H | Sun, InDog, RangeSlv, ModeSlv +37; LoDog, carrier +9.25; each Pl −18.5 [3.870 mm radial] | same | same | same | turn; every train body "moved" in all four; fits shared, H, H_private_put; rules out per_configuration |
| after the quiet Update in 4L | 0 | 0 | 0 | 0 | — (:1927-1930, largest 8.3e-10 at Pl copy 2 in each) |
| fresh drive +37 in 2H | as the first drive | same | same | same | turn; fits **shared** only; rules out per_configuration, H, H_private_put |
| moving put in 2H, the train back to its built frames | 0 | as the fresh turn | same | same | put; 2H "moved", 4H/N/4L "still" for all nine train bodies; rules out shared |
| saved and reopened (in 2H) | 0 | as the fresh turn | same | same | `same_as_before_save` true |

- *Update.* `put_in` is 2H, 4H, N, 4L; `visited` is 2H, 4H, N; `failures` is empty; it took 239.6 s; 52 puts
  (:1902-1904).
- *Run.* SolidWorks 2026 revision 34.1.1 (:2), snapshot `fe74276` (:1), and `s7: only the cases ['8'] run` (:1749).
  s1 has 555 `ok` lines, s7 has 27, and the log ends `done 0 failed: []; 1 noted for a ruling` (:2037). The one NOTE
  is SolidWorks' notification box during `SetSuppression2` (:1834).
- *The in-Update reading.* "After its put in 2H, 4H and N still showed the first turn": :1855 and :1905-1907 read
  4H out of step at ModeSlv–FrontDog and N turned in step. These are the judgements on showing, not after the put.
  `_modes_put` fills `ModeCheck.out_of_step`/`turned` from `train_check` before it puts (`swbuild.py` 4239-4246,
  4341-4344). The probe labels the line "post-check of …" (`probe/workbook_assembly_check.py` 6512), but the reading
  is as the comments state it. 4H's out-of-step is what +37° on ModeSlv against FrontDog at 0 gives: a 12° pitch,
  1° off, and the residual is 1.75e-2 rad (:1897).
- *MF1.* `cbdb7ac` is an ancestor of `fe74276`, and between `fe74276` and HEAD neither the probe nor `src/` changed
  except `findings.py`'s comments. Case 8 now checks `result.ok`, no failures and `put_in ⊇ modes` (:1910). It then
  holds every configuration to the built frames (:1927-1930). Both passed. Item 3, running it alone on 2026 before
  the closing run, is done. MF1 is met.

## Points

**S1. Should fix: the handoff's put sentence misreads.** `docs/HANDOFF-WORKBOOK.md` 656-657: *"the moving put in 2H
after it stayed in 2H, 4H, N and 4L still at the fresh turn through a save and reopen"*. It parses as "stayed in 2H,
4H, N and 4L", which is the opposite of the reading. Write it as `W8-INTERFACES.md` 343-344 does: *"stayed in 2H: 4H,
N and 4L still stood at the fresh turn, through a save and reopen"*.

**S2. Should fix (records): case 8 is not s2's sequence, and its Update reading repeats 34.0.0's.**
`findings.py` 1262-1269 and 1288-1293, `W8-INTERFACES.md` 333-347, `HANDOFF-WORKBOOK.md` 652-660.

- *What the text implies.* "s2's reading on 34.0.0 was not seen on 34.1.1; 34.0.0 has not run case 8" reads as if
  the revision were the one thing left between the two. Case 8 and s2's 151412 run differ in more than that:
  1. *Showing between turn and put.* After the fresh turn, case 8's read shows and rebuilds every configuration
     before the put (`s7_read_job`). The 151412 s2 run showed 4L alone between the fresh turn and its second press
     (s2:356, then the press). The current s2 shows 4H, N and 4L there (`workbook_assembly_check.py` 6837-6841, review
     M1), but has not run on 2026 since.
  2. *Whose put.* Case 8's put is the probe's own `s7_put_job` (mates off in 2H, `place_component`, mates on).
     s2's was the app's second Update press. N2 of `W8-REVIEW-LATE-FIXES.md` named exactly this ("the app's
     sequence differs from the script's"). Case 8 on 34.1.1 does not run the app's second press.
  3. *Machine.* Case 8 ran on another machine as well as another revision.
- *The in-Update reading.* "In that Update, after its put in 2H, 4H and N showed the first turn still standing" is
  presented as a 34.1.1 reading set against s2's. s2's own first press on 34.0.0 read the same, from a copy no Update
  had moved: 2H turned, 4H ModeSlv–FrontDog out of step, N turned, 4L both crossed (s2:224-227; the s2 pin's
  docstring says so, `tests/test_findings.py` 1398). So on the one state both revisions ran, they agree.
- *What to write.*
  - Case 8 on 34.1.1 read neither possibility *in its own sequence*.
  - Its Update reading matches 34.0.0's first press.
  - s2's second-press reading is unexplained between revision, machine and sequence (the shows before the put,
    and the app's press against the script's put).
  - The closing run's s2, which now reads 4H, N and 4L after the fresh turn and then presses in 4L, is the
    re-read of s2's own sequence. Say which revision it runs on.
- *Wording.* Drop "34.0.0 has not run case 8" as the thing left. It is true, but it points at the revision alone.

**S3. Should fix (records): "is to settle" and "open" left elsewhere.**

- `docs/PLAN-WORKBOOK.md` 640-643: *"…and 2026's s7 case 8 is to settle which."*
- `docs/notes-workbook/W8-PLAN.md` 167: *"…is not settled; a further s7 case is to measure it"*.
- `docs/notes-workbook/W8-PLAN.md` 511-513: *"Which is not settled on 2026; s7 case 8 is to measure it."* (and
  "the put stay in 2H", sic).
- `src/gear_generator/ui_text.py` 3583-3586, the comment above `TURN_CAN_SHOW_ELSEWHERE`: *"which it reaches then is
  not settled on 2026 (W8 s2)"*.
- `tests/test_findings.py` 1395-1400, the s2 pin's docstring: *"…in that state is open (findings.py)"*.

Each should name 34.0.0 for s2's reading and point to 9.18 for case 8 on 34.1.1. None changes a value or a
sentence the app says.

**S4. Should fix (records): the in-Update reading is cited but held by nothing.** `findings.py` 1267-1268,
`W8-INTERFACES.md` 340-341, `HANDOFF-WORKBOOK.md` 657-658.

- The JSON's `update` holds `put_in`, `visited`, `failures`, `seconds` and `status`. It does not hold the
  `ModeCheck`s, so the 4H/N reading lives in the log alone (:1855, :1905-1907).
- The comments cite only the log file, and no pin covers it.
- Cite the lines. If the probe is touched again, have case 8 write each `ModeCheck`'s judgement on showing into
  `update`, and call it that rather than "post-check" (`workbook_assembly_check.py` 6512).

**N1. Note: "as 2024's case 8 did not".** `W8-INTERFACES.md` 335: *"read neither 34.0.0 possibility, as 2024's case
8 did not"* reads backwards. Write "as 2024's case 8 did".

**N2. Note: the put step's turns are not pinned.** `_s7_case8_2026_holds` (`tests/test_findings.py` 1306-1331) pins
the put's judgement states but not its `expressed` values. The comment cites them: "4H, N and 4L still stood at the
fresh turn (the Sun at +37°)", `findings.py` 1266-1267. I ran mutants on scratch copies of the JSON:

- *Caught:* the revision, the snapshot, the reopen flag, an Update failure, `put_in` missing a mode, a fresh-turn
  value, a drive judgement, an after-Update value, and the put's `rules_out`.
- *Not caught:* the put step's 4H Sun set to 0 with the judgement left alone.

One line holding 2H at 0 and the others at the fresh turn's values after the put (and after the reopen) would close
it. The three doctored copies in the test are real: each fails the helper.

**N3. Note: the handoff's status row.** `HANDOFF-WORKBOOK.md` 46 now drops case 8 from "Left" but still says "shown
on SolidWorks 2026 (34.0.0)" and does not mention the 34.1.1 run. The same row's "**No W8 code has run on
SolidWorks**" predates tonight and contradicts its own first half.

**N4. Note: revisions in the turn comment, and the put fact's scope.**

- `findings.py` 1276-1282: the turn comment's first two bullets (copies no Update had moved; 4L after an Update)
  are 34.0.0 readings but are not labelled. The new bullets are labelled, so label these too.
- `swcom.positions_per_configuration`'s docstring (`swcom.py` 499-500) describes the put fact as "a Transform2 put
  of a component no mate holds". The comment now rests it on mated trains as well (case 5 on 34.0.0, case 8 on
  34.1.1, 2024).

## The app's Update path under the answer read (question 3)

Nothing the app says or does is made wrong by "turns shared, moving puts per configuration".

- *The Update path.* This is the `put_splits` world the Update was tested against
  (`test_e4_a_turn_in_2h_then_an_update_in_4l_puts_every_mode_back_where_a_put_stays_in_its_configuration`). Case
  8's own Update shows the path on 34.1.1: every visited mode was found turned or crossed, `put_turned` put each
  whole, and every configuration read at its built frames afterwards.
- *"The gears of 2H and N stood at the turn they were built at…"* (`ui_text.py` 4024-4037). It names only modes
  judged untouched on showing, so under this answer it does not fire, and in this run it was not said (:1901).
- *The shared-turn sentence* ("can show … may have been given in another") was said, and is right.
- *The switch.* `swcom.positions_per_configuration` maps any major 34 to `ON_2026`, so 34.1.1 and 34.0.0 get the
  same False and the same sentences. That is consistent with the reading.
- *`W8-REVIEW-LATE-FIXES.md`'s conclusion holds.* The one state where a mode can stand wrong under a green status
  is still the quiet Update that puts nothing, with a turn in step in the active mode. With turns shared, that
  state is real (a turn in 2H crosses 4L's couplings). The status says it did not show the other modes, and the
  footer's `TURN_CAN_SHOW_ELSEWHERE` says to press Update with that mode showing.

## Public repo (question 5)

- Both files carry the run folder `C:\Users\M0obo\Documents\GearGeneratorProbe\w8-s7c8-sw2026-20261115-220518\…`
  (37 times in the log). That is the same user folder earlier committed logs carry (e.g.
  `gearbox-smoke-20261113-191036.log`).
- No user document is named: only the probe's own E4 files.
- No window title beyond SolidWorks' progress boxes. The notification box at :1833 logs its control names only
  ("Title", "Description", …), not its text.
- No licence edition, host name or e-mail. PIDs and memory figures only.

## Not verified

- I did not rerun anything on SolidWorks. Every reading above is from the committed files.
- I did not check the 34.1.1 machine's state, or that its `s1.master` is the same build as this host's (the log's
  555 passing checks are the only evidence).
- I ran `tests/test_findings.py` only (118 passed), not the whole suite.
