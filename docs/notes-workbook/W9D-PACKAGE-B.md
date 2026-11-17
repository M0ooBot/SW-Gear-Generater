# W9d package B (planning, the question, the result's sentences, the record, the window): hand-back note

Package B of W9d, against `W9D-INTERFACES.md` as committed at `23ed8c5` (the re-check's R1, R2, S-a to S-g taken) and
package A's shapes (`c20b1cf`, `9ee64e6`), `plan_carry` (`7ed2d80`) and worker (`3c6a954`). Written and tested against
the fake only; no SolidWorks or Excel was started.

## What was built

| Item (§14.2, §17) | Where |
|---|---|
| Schema 10: `CarryEntry` and its four entries, `GearboxRecord.carry`, `UserMateEntry.entities`; nested readers; a W9c-era reader refuses 10 with its sentence, byte-identical; 9 reads forward and is written as 10; `unsaved_at`'s newer-file rule (`clear_carry_saved`, run by `clear_saved`) | `store.py` |
| `carry_for(record, again, old)`: every body on record to the new plan, `same_file`, `why_new`, `names`/`old_names`, `modes`, `first`, `written_on`, `app_files` | `workbook/update.py` |
| `recorded_old_work(record)`: the inventory as an `OldWork` for the foresight | `workbook/update.py` |
| An Update's inventory keeps each mate's entities | `update.user_work_entry` |
| The question: `carry_foresight` (plan_carry on the inventory) and `carry_sentence`, in `build_again_question` | `workbook/update.py`, `ui_text.py` |
| The result: `carried_status`, `carry_named_clause` (one clause per §9.3 reason), the fallback sentences | `ui_text.py` |
| The finish: `carry_entry`, `carried_user_work`, `carry_anchors`; `finish_build(..., carry=)` | `workbook/gearbox.py` |
| The footer's §9.4 line (`carry_footer_line`, in `workbook_footer`); the lost line from a later Update (`update._follow_carry`, said in that press's sentence) | `ui_text.py`, `workbook/update.py` |
| The window: `Job.carry`, `_start_build` passes `carry`, `_finish_build` says `carried_status` and passes `carry` to the finish, `_saved_since` looks at the carry's mark | `workbook_gui.py` |
| UI-DESIGN §9: a W9d section; the W9a section's *Build again?* paragraph and its last sentence | `design/UI-DESIGN.md` |

## Tests (§14.2), each and where

All in `tests/test_workbook_carry.py` unless named.

- `carry_for`: every body mapped, planet copy *k* to copy *k*, the layout and the carrier, `same_file` from `reuse`,
  `why_new` from the Gears columns (Flank; Face width and Bore; Part name and Flank), `UNSAVED`, `MISMATCHED`, a gear
  with no handle, `names` from `plan_features` and the sidecars, `written_on`, `app_files`: three tests.
- The question: W9a's clause led by `CARRY_INSERTS`; the mixed form; carried and named with the time; a kind not in
  `CARRY_REMAKE_KINDS` grouped with its finding; the configuration *may*; each reason and a group (hand-made plan);
  the `MISMATCHED` advice with the cell and value and without, the `UNSAVED` advice; a schema 9 inventory's *may*; a
  lightweight and a suppressed component; the not-open clause for each failing condition (five cases); the states
  clause and its going; a mode renamed; nothing on record; a foresight that raises; the whole question.
- The result: carried and saved; every `why` with every subjects slot (mates 20 cases, components 9); the sub-assembly
  marks sentence; each fallback kind (5 cases); `same_error`, `moved`, a clash, a sub-assembly made rigid, the marks
  fact both ways, the states and placement sentences; a stop; nothing read (unread, raised), a read that marked, a
  document left open; the pattern-instance sentence once `PATTERN_INSTANCE_READ` is set.
- The record: schema 10 round trip; 9 read forward and written as 10; a W9c-era reader refusing 10, byte-identical;
  damaged carries and entities refused naming them; `unsaved_at` dropped only when the file is newer or gone; the
  spelled words pinned to swbuild's.
- After a carry: the new revision's `user_work` from the carried items (None when nothing carried), `unsaved_at`, the
  footer's line, a save dropping it, the lost line from a later Update, `LinkRecord.unsaved` untouched.
- The round trip: classify → question → `carry_for` → A's `build_gearbox(..., carry=)` on the fake → `finish_build` →
  the record → the footer (`test_the_round_trip_…`). Through the window itself, under Tk:
  `tests/test_workbook_window.py::test_a_build_again_hands_the_worker_its_carry_…`, with a hand-made `CarryResult` on
  the real build's result (it was written before A's worker landed; the Linux round trip covers the worker).
- Changed because the contract changed the sentence or the schema: `test_workbook_user_record.py`'s question test and
  the window's `TIMELESS` (W9a's clause now led by `CARRY_INSERTS`), every test pinning the schema at 9, and the two
  that showed this reader refusing 10 (now 11).

## Judgement calls on wording (beyond §9)

- **The not-open clause is said as *if***: the window cannot know before the press whether the old assembly will be
  open. *If RangeBox.SLDASM is not open in SolidWorks when you press, it is not read: Gear Generator has not yet been
  shown to read which SolidWorks last saved a file (findings.FILE_VERSION_READ_ON_2026), …, so nothing of yours would
  be carried: open RangeBox.SLDASM in SolidWorks before you press, and it is read as it stands there.* With every
  closed-file finding set: *… Gear Generator reads it then only when it and every file it uses were last saved by this
  SolidWorks (a file saved since on another SolidWorks is not read) and nothing else is open in SolidWorks
  (findings.OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS_ON_2026); otherwise …* (or *nothing but Gear Generator's own files is
  open in SolidWorks* once that finding is set).
- **Each item not carried is its own sentence**, §9.3's clause with *so it is not made again* / *so it is not carried*
  where the clause does not already say it (*…, and it is not made again* after a clause with *so* in it). §9.2's
  *Not carried:* lead is dropped, since each sentence says it. Items a finding holds back are grouped: *Gear Generator
  has not yet been shown to make concentric mates again in a new revision on SolidWorks 2024
  (findings.CARRY_REMAKE_KINDS_ON_2024), so Concentric5 and Concentric8 are not made again.*
- The single `unmeasured` clause: *Concentric5 is a concentric mate, which Gear Generator has not yet been shown to
  make again in a new revision on SolidWorks 2024 (…)*; *M1 is on a face, which … to find again in a new revision
  (, after its part is closed and opened again,) on …*; *M1 is on an origin, which … to read an origin as a mate's
  entity on …*; a component: *X is not carried, which … to carry your work into a new revision / insert a sub-assembly
  of yours into a new revision / insert a component in a configuration of its file's several on …*; a version not known
  is *the SolidWorks it runs on*.
- A schema 9 inventory's mate (no entity kinds): on an app gear whose part is new, §9.1's sentence; any other, *The
  record does not say what your Dist2 is on, so the press reads it and makes it again where it can.*
- A file whose configurations the record does not keep (never kept): *Sprocket-1 and Housing-1 are carried only if
  each one's file has a single configuration: Gear Generator has not yet been shown to insert a component in one of
  several on SolidWorks 2026 (findings.…), and the press reads which.* — only while either configuration finding is
  unset.
- A lightweight component with no mates: *Sprocket-4 was lightweight as read: it is carried resolved.* The suppressed
  one names *the mode RangeBox.SLDASM showed* without its name (the inventory does not keep which mode showed).
- `CARRY_INSERTS` unset: W9a's clause led, and no standing list (nothing would be carried). A foresight that raises:
  *As read at 14:02, RangeBox.SLDASM held your …: the press reads it again first and carries into RangeBox_r2 what it
  can, saying whatever it cannot.*
- `assembly feature`: *a feature you made in RangeBox.SLDASM* (not *a plane*: the subjects do not say its kind).
- `gone` feature with no owner slot: *M1 was on Mid Plane in an app part, which that part in RangeBox_r2 does not
  have*.
- The result's components by their new Name2, *(was Sprocket-1)* where SolidWorks named it otherwise; *each where it
  stood against the gear it is mated to* / *each where it stood* / *…, against the gear it is mated to where it has
  one* by the anchors (`carry_anchors`). *In L, SolidWorks moved Sprocket-4 2.0 mm from where it was placed when your
  mates were made again.* (the anchor is not in `moved`).
- Nothing read: *RangeBox.SLDASM was not read (…), so nothing of yours was carried; it and your files are as they were.
  Open RangeBox.SLDASM in SolidWorks before you press Build again… to carry it.* (the last sentence only for
  `OLD_UNREAD`).
- The marks fact: *…, though nothing in it changed* only while `CARRY_INSERT_MARKS_USER_DOCUMENTS` is True on the
  version the job ran on; otherwise only *SolidWorks reads Sprocket.SLDPRT as changed since it was inserted into
  RangeBox_r2: saving RangeBox_r2 with its parts saves that file again too.*
- Fallbacks: *with your Lock8 made again SolidWorks reads Sun unable to turn in L, so it was not kept* (the mode said
  when it is not the first); `FELL_NEW_ERROR` with a code before: *…, where it read error 12 in H, the mode … showed*;
  `FELL_OVER_DEFINED` with no mate: *with your mates made again SolidWorks reads it over-defined*.
- Once `PATTERN_INSTANCE_READ` is set, the result drops the standing list's pattern clause and says *Your Sprocket-2
  was an instance of a pattern of yours, and comes over as a component of its own.*; the question keeps the clause (it
  cannot know an instance).

## Shape requests and deviations

1. **`CarryResult` does not hand back each component's anchor**, which `CarriedComponentEntry.anchor` and *against its
   gear* need. `gearbox.carry_anchors` works it again by `plan_carry` on what was read (pure; the anchor rests on the
   mates). Request: an `anchors` field, or the anchor in `inserted`.
2. **`CarryResult` does not hand back a remade mate's code after**: `CarriedMateEntry.code_after` is its `same_error`
   code, else 0 (a new error falls its cluster back, so a kept mate has no other).
3. **§2.3's `unmeasured` (entity kind) and `gone` (feature) subjects do not say whose** face or part, which §9.3's
   examples name (*a face of Sprocket-1*, *Sun's Mid Plane*). The clauses take an optional extra slot (a 4th for
   `unmeasured`, a 3rd for `gone`) and say it without one, as above. Request: those slots.
4. **The inventory keeps no user file path and no file configurations** (W9a ruling 6; schema 10 adds neither), while
   `plan_carry` names a component with no path `WHY_NO_FILE` and one with `configurations` None `WHY_CONFIGURATION`.
   `recorded_old_work` stands each file in by its Name2 and kind's extension; the foresight takes each file as of one
   configuration and says the *may* above. Not a shape change.
5. **The lost line is said once, in the later Update's sentence** (`Finished.notes`), not kept for the footer:
   `CarryEntry` has no field for it, and the mark itself goes. A later Build again… from that revision is not told.
6. **`build_gearbox` does not pass `exists` to the read's `isfile`** (A's `_read_old_contents` uses `os.path.isfile`),
   so the round trip patches `os.path.isfile` for the fake's disk. For A to thread through, if wanted.
7. On the fake, A's carry reports the carried sprocket `moved` 30 mm in N and L (`test_the_round_trip_…` does not
   assert on `moved`); it may be the fake's per-mode frames. For A to judge.
8. `ui_text.CARRY_KIND_WORDS` repeats `swbuild.CARRY_KIND_WORDS`, pinned equal by a test.

## Not done

- No window test drives A's real worker under Tk (the window test uses a hand-made `CarryResult`; the Linux round trip
  drives the worker on the fake).
