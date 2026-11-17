# W9a package B (issue #1): what the user sees and what the record keeps

Package B of `ISSUE-1-PLAN.md` §5's W9a, on top of package A as revised (`W9A-INTERFACES.md`, `W9A-REVIEW-A.md`),
reviewed in `W9A-REVIEW-B.md` (`6056d71`) and revised in one fix round under the coordinator's rulings 1 to 8 (the
last section). The worker-side changes: the build job's read of the old assembly (the coordinator's correction: it is
W9a's, package B's), which reuses package A's own inventory read and, since the fix round, reads the old assembly
without activating it (`swcom.Session.use_open_document`); and, by ruling 3, the check of a carried component that is
suppressed or lightweight moved into the shared `judge_user_work`, unchanged in what it refuses.

## What was built

| Item (§5, package B) | Where |
|---|---|
| §0.1: the tests' made-up phase is W99; "W8 is the last phase" rewritten everywhere it stood, PLAN-WORKBOOK §6 gains a W9 row | `e3cb13d` |
| Link record schema 7 (below); `finish_update` records the inventory; the window records a refused press (`UserWorkRefused`) | `store.py`, `update.record_user_work` / `refused_update`, `workbook_gui._record_refusal` |
| K4: the footer before the press, from the recorded inventory with its time, by package A's pure judgement | `update.user_work_ahead` / `bodies_put`, `ui_text.user_work_line`, in `workbook_footer` |
| The Build again? clause (K5 until W9d), from the record with its time | `update.stays_behind`, `ui_text.stays_behind_sentence`, in `build_again_question` |
| The build job's read of the old assembly, first, read-only, and the result's sentence | `swbuild.OldAssembly`, `read_old_assembly`, `build_gearbox(..., before=)`, `GearboxResult.old_user_work` / `old_read`; `update.old_assembly`; `ui_text.stayed_behind_status` |
| After an Update: carried components, the user's features rebuilt into error, the user's items in error (with modes), a component found by its part | `ui_text._user_after`, in `gearbox_update_status` |
| `read_sidecar` passed to `classify` from the window (and gen.py) | `workbook_gui._plan_solidworks_pass` |
| K12: board first, then `_fit` capped, the body page, the footer's ceiling, the wheel; its Tk tests; UI-DESIGN's three places | boards `9c33e3b`, window `feec547` |
| Boards: `WorkbookShortScreen` (K12), `WorkbookUserWork` (K4); every existing board regenerates byte-identical | `design/canvas/gen.py` |

## Schema 7 as written

`LINK_SCHEMA_VERSION = 7` (`_W8_LINK_SCHEMA + 1`). `GearboxRecord.user_work: Optional[UserWorkEntry]`, None = nothing
read (every record before 7; a new assembly until its first Update — `finish_build` drops an entry read in another
assembly).

```
user_work: {
  read_at: "2026-11-16T14:02:00Z",      # store.now() of the worker's read, before anything changed
  assembly: <path>, digest: <workbook read the press came from>, revision: [34, 1, 1] ([] unknown),
  components: [{name, kind: part|assembly|"" (file not named), fixed, code, state}],   # never the user's file path
  mates:      [{name, kind: lock|gear|other, type, touches: [[app|layout|assembly|user|unread, name]], on: [modes],
                code, warning, whole}],
  features:   [{path, name, type_name, code, warning}],
  carried:    [{component, gear, locks: [..]}],
  problems:   [{kind, sentence, mates: [..], values: [{document, name, live, wanted, recorded, mode, cell,
                unsaved}]}]   # [] unless refused
}
```

A v1–v6 record reads as v7 with `user_work` None and writes back the same; a W8 reader (schema 6) refuses a v7 record
and leaves it byte-identical, as `store.py` refuses any newer schema. An entity word outside the five, or a touch that
is not a pair, or a component kind not one of the three, is refused with a sentence. Schema 7 is not yet released,
so the fix round changed it freely (ruling 6: a component's kind, not its path; `ValueEdit.unsaved` kept). `revision` comes from the worker's session, captured by the window's job
(`Job.revision`), since `UserWork` does not carry it.

## Judgement calls where the plan left room

1. **The prediction's "put"** (`update.bodies_put`) follows `swbuild._may_put` from the record: with modes, every mated
   body whenever the press changes anything; without, the trains of gears re-placed, moved along their shaft or whose
   gear mate is remade, every train when the layout or a carrier moves; a held or fixed gear only when re-placed; a
   quiet press nothing. Trains are joined over every mode's links (the mode showing at the press is unknown).
   `branches` is always given (`user_carry_branches`) with the revision the inventory was read on.
2. **A recorded refusal is said as recorded**, red, while the workbook is the one the refusal came from; once it has
   changed, the prediction runs too and follows it, in its own colour (ruling 5). A foreseen refusal is red. Update
   stays enabled in every case (no new control; the press reads again). The footer says what the worker would do
   with the assembly **as it was last read**, never more: the time says how old that read is.
3. The footer line follows the state as the save line does: never after a job's own sentence, which already says it.
   Nothing is said when nothing of the user's was read, so no existing footer, board or pin moves.
4. **Wording**: a single mate is named, several counted; components named up to three, then counted; the inventory is
   never called complete (W9A-INTERFACES §5's gaps are in UI-DESIGN's new section, not in the footer, which would be
   long on every state).
5. **The Build again? clause** (ruling 4): with an inventory on record, its items with the time and "nor anything
   added since"; with none (or one with nothing in it), without a time, that anything added in SolidWorks stays in
   the old assembly and the new revision has none of it. A feature in a part the new revision reuses is said to come
   with it; one in a part made new "stays in Gear_…, which G1's new part replaces" (or "which RangeBox_r2 does not
   use"). The build's own sentence says it only once the new assembly is saved.
6. **The old assembly's read** reads components and mates only; the user's features left in parts made new come from
   the record (with its time). It is made only when the old assembly is open in the session (it is never opened from
   its file), through `use_open_document` (the document walk `documents()` already makes, then that document made the
   build document: no `OpenDoc6`, no `ActivateDoc3`, so the old assembly is not brought forward and nothing is rebuilt
   on activation — review point 6, ruling 7), `begin_build`/`end_build` as Update's check phase uses them,
   `mate_states`, `configurations`, `mate_suppression` per mode (no mode shown). A read that raises never stops the
   build; its reason is said (a repo test). The fresh read is said, not kept in the record (W9d's schema 9 is where a
   kept one belongs); the read takes the record's Name2s, so an app component renamed in the old assembly is listed
   as the user's in that sentence (review point 14, a known limit).
7. **K12's scroll-bar lane is the window's right padding** (12 px, the bar's width), not taken from the left column:
   the bar sits in a fixed-width frame there, so no column narrows and no part-cell pin moves. The plan said "counted in
   the left column's width"; this keeps the column exactly as before, which is what that clause is for.
8. K12's numbers: frame 40 px (as the strip), body least height 160 px, footer ceiling a third of the work area. The
   board draws 1570 px at 150 % as 1047 px at 100 %; the renders were taken with Windows' Chrome from WSL (render.py's
   steps, a scratch wrapper for the Chrome path), not on the Mac of the other renders.
9. gen.py draws the read's time in UTC, stamped 14:02 today, so boards stay byte-deterministic.

10. **Withdrawn windows in the Tk tests** (ruling 8): Tk on Windows keeps a withdrawn toplevel at its requested size
   whatever geometry it is given until it is mapped; Linux applies it at once. So the K12 tests map the window
   (`deiconify`, `update`) for the geometric checks and withdraw it after. Mapped, the real window takes the capped
   height and its footer stands whole (measured under Windows Python: 739 asked, 739 taken, the footer's bottom at
   715 of an outer frame 715 tall). The app's window is always mapped, so it never had the fault.

## The fix round (`W9A-REVIEW-B.md`, the coordinator's rulings)

| Point | What changed |
|---|---|
| 1 (must) | `_set_status` wraps the sentence and fits its box; a Tk test sets six sentences the window sets alone and measures the box |
| 2 (must) | The Tk tests measure `_status_box` against the label's request (whole: equal, no bar; above the ceiling: the box at the ceiling, its bar shown). `probe/` is not package B's (ruling 2) |
| 3 (must) | The suppressed/lightweight check is in `judge_user_work`; the record keeps each component's state; a test foresees the refusal the press makes |
| 4 | The Build again? clause with and without an inventory (above); pins moved, listed in the commit |
| 5 | After a recorded refusal, a changed workbook runs the prediction too |
| 6 | The record keeps a component's kind, not its path |
| 7 | A repo test of a raising read; the Workbook window's wheel guarded to its own window; both guards tested; the sentence fixes (one item "none of it", no capital after a colon, the file not named twice, the old assembly named with nothing on record, the tie clause says what follows, "in error … now" and those already in error before told apart, several features in one part named once); `README.md` and `tests/test_workbook_modes.py` no longer say W8 is the last phase; the old assembly read without activation |
| 8 | The Windows failure: a withdrawn window's geometry (point 10 above), not the app |
| 9-14 (notes) | Said in UI-DESIGN's section (the quiet press, layout and carrier features) and above (the fresh read not kept, the renamed component) |

## The second fix round (the re-check's R1 to R4, and the demonstration's footer lines)

- **R1.** After a K11 refusal, a changed workbook keeps the line red while it still does not ask the value SolidWorks
  held (`update._asked_now`: a part's, the layout's or a carrier's global against the plan's globals; on the
  assembly a Face Z, a slide's value and a mate's flag in their mode against the plan's motion; what it cannot find
  stands), saying what the workbook asks now; then the prediction (ruling 5). Once the workbook asks the held value,
  or no longer sets it, the refusal gives way.
- **R2.** Several features of one part in a longer list get a clause of their own (*…, and your Keyway and Groove in
  Gear_m1.5_N17 too*); one feature per part stays in the list.
- **R3.** An item already in error before the change is said *in error in the mode showing before this Update
  changed anything; after it, Lock3 in L is in error*: before, only the mode showing was read.
- **R4 (note).** `recorded_user_work` gives each component a made-up path (its name and its kind's extension), right
  for the judgement's sub-assembly branch, which reads the extension, and never a file: said at the function.
- **The demonstration's footer lines** (`probe/results/w9a-demo-sw2026-20261116-*.log`, `footer`/`line`): a
  prediction that repeats a recorded refusal is said only as *for the same reason*; *Update SolidWorks would stop
  … Update SolidWorks would put …* is now *the next press would stop …*; a tie read on a train with more than three
  of the user's mates counts them. The repetition left (each sprocket's lightweight refusal in full, each gear's
  no-carrier refusal in full, the tie naming nine mates twice) is in the worker's own sentences, package A's.

## What the demonstration on SolidWorks must show for package B

- After a value Update and a slide-offset Update on S0's master with the user's work: the record beside the workbook
  holds `user_work` (components, mates with what each touches, the keyway, `carried` with the sprocket, `revision`
  34.1.1), and the footer then names the sprocket going with Sun/RangeSlv, with the time.
- The lock-to-housing and the Bore-typed refusals: the record holds the problems; the footer says "Update SolidWorks
  refused at …" until the workbook changes.
- Build again… (e.g. Sun's Flank changed) with the old assembly open behind another document, and in one run needing a
  rebuild: the question ends with what stays behind; the build's sentence lists what it read first; `GetSaveFlag` of
  the old assembly, every user mate's flag and error code, its active configuration, which document is active, and no
  dialog, unchanged before and after the build job's read (§0.3's STOP on a changed save flag applies to this read),
  and that `use_open_document`'s reads (`_mate_group`, `IsSuppressed2` per configuration, `MateEntity`) answer on a
  document that is not the active one. Once more with the old assembly closed: the sentence says it was not open and
  gives the record's inventory.
- A sprocket set to lightweight: the footer foresees the refusal, and the press makes it.
- The window check's W8 stage on this device (2560 × 1600 at 150 %, SolidWorks 2026): `w8_footer_whole`, the frame's
  bottom (`GetWindowRect`) inside the work area, and the body's last line scrolled into view.
