# W9a package B (issue #1): what the user sees and what the record keeps

Package B of `ISSUE-1-PLAN.md` §5's W9a, on top of package A as revised (`W9A-INTERFACES.md`, `W9A-REVIEW-A.md`).
Nothing of package A's judgement of what refuses is changed. The one change on the worker side is the build job's read
of the old assembly (the coordinator's correction: it is W9a's, package B's), which reuses package A's own inventory
read.

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
  components: [{name, path, fixed, code, state}],
  mates:      [{name, kind: lock|gear|other, type, touches: [[app|layout|assembly|user|unread, name]], on: [modes],
                code, warning, whole}],
  features:   [{path, name, type_name, code, warning}],
  carried:    [{component, gear, locks: [..]}],
  problems:   [{kind, sentence, mates: [..], values: [{document, name, live, wanted, recorded, mode, cell}]}]   # [] unless refused
}
```

A v1–v6 record reads as v7 with `user_work` None and writes back the same; a W8 reader (schema 6) refuses a v7 record
and leaves it byte-identical, as `store.py` refuses any newer schema. An entity word outside the five, or a touch that
is not a pair, is refused with a sentence. `revision` comes from the worker's session, captured by the window's job
(`Job.revision`), since `UserWork` does not carry it.

## Judgement calls where the plan left room

1. **The prediction's "put"** (`update.bodies_put`) follows `swbuild._may_put` from the record: with modes, every mated
   body whenever the press changes anything; without, the trains of gears re-placed, moved along their shaft or whose
   gear mate is remade, every train when the layout or a carrier moves; a held or fixed gear only when re-placed; a
   quiet press nothing. Trains are joined over every mode's links (the mode showing at the press is unknown).
   `branches` is always given (`user_carry_branches`) with the revision the inventory was read on.
2. **A recorded refusal is said as recorded** and the prediction is not run beside it (a tie is a solver read; the
   recorded sentences are a superset). Red while the workbook is the one the refusal came from, green with "the
   workbook has changed since" otherwise. A foreseen refusal is red. Update stays enabled in every case (no new
   control; the press reads again).
3. The footer line follows the state as the save line does: never after a job's own sentence, which already says it.
   Nothing is said when nothing of the user's was read, so no existing footer, board or pin moves.
4. **Wording**: a single mate is named, several counted; components named up to three, then counted; the inventory is
   never called complete (W9A-INTERFACES §5's gaps are in UI-DESIGN's new section, not in the footer, which would be
   long on every state).
5. **The Build again? clause only when the record holds an inventory** with something in it; a record with none (built
   before W9a, never updated since) gets the question as before. A feature in a part the new revision reuses is said to
   come with it; one in a part made new "stays in Gear_…, which G1's new part replaces" (or "which RangeBox_r2 does
   not use").
6. **The old assembly's read** reads components and mates only; the user's features left in parts made new come from
   the record (with its time). It is made only when the old assembly is open in the session (`documents()`; it is never
   opened from its file), via `open_document` (activates an open document, loads nothing), `begin_build`/`end_build`
   as Update's check phase uses them, `mate_states`, `configurations`, `mate_suppression` per mode (no mode shown). A
   read that raises never stops the build; its reason is said.
7. **K12's scroll-bar lane is the window's right padding** (12 px, the bar's width), not taken from the left column:
   the bar sits in a fixed-width frame there, so no column narrows and no part-cell pin moves. The plan said "counted in
   the left column's width"; this keeps the column exactly as before, which is what that clause is for.
8. K12's numbers: frame 40 px (as the strip), body least height 160 px, footer ceiling a third of the work area. The
   board draws 1570 px at 150 % as 1047 px at 100 %; the renders were taken with Windows' Chrome from WSL (render.py's
   steps, a scratch wrapper for the Chrome path), not on the Mac of the other renders.
9. gen.py draws the read's time in UTC, stamped 14:02 today, so boards stay byte-deterministic.

## What the demonstration on SolidWorks must show for package B

- After a value Update and a slide-offset Update on S0's master with the user's work: the record beside the workbook
  holds `user_work` (components, mates with what each touches, the keyway, `carried` with the sprocket, `revision`
  34.1.1), and the footer then names the sprocket going with Sun/RangeSlv, with the time.
- The lock-to-housing and the Bore-typed refusals: the record holds the problems; the footer says "Update SolidWorks
  refused at …" until the workbook changes.
- Build again… (e.g. Sun's Flank changed) with the old assembly open: the question ends with what stays behind; the
  build's sentence lists what it read first; `GetSaveFlag` of the old assembly, every user mate's flag and error code
  and its active configuration are unchanged before and after the build job's read (§0.3's STOP on a changed save flag
  applies to this read). Once more with the old assembly closed: the sentence says it was not open and gives the
  record's inventory.
- The window check's W8 stage on this device (2560 × 1600 at 150 %, SolidWorks 2026): `w8_footer_whole`, the frame's
  bottom (`GetWindowRect`) inside the work area, and the body's last line scrolled into view.
