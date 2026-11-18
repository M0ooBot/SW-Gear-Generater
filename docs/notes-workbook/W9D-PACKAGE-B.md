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
7. *Dropped* (the review could not reproduce it, and on A's worker at `98ed62e` the round trip reads `moved` []): the
   "moved 30 mm in N and L" first seen with A's worker at `3c6a954`.
8. `ui_text.CARRY_KIND_WORDS` repeats `swbuild.CARRY_KIND_WORDS`, pinned equal by a test.

## Not done

- Nothing of the first round's list: since the fix round the Tk tests drive A's worker on the fake.

## The review's fix round (`W9D-REVIEW-B.md`, `7981967`; the coordinator's rulings)

Committed as `6441e34` (code and tests) and the commit after it (the anchors' re-derivation dropped, the tests on `swcom.PERSIST_ROUTE_R3`, UI-DESIGN §9 and this note). The round trip asserts nothing reads as moved (A's fake fix): request 7 is closed.

| Point | Done | Test (`tests/test_workbook_carry.py` unless named) |
|---|---|---|
| M1 nothing carried: W9a's sentence, led | `ui_text._nothing_carried` | `test_nothing_carried_today_leads_w9as_sentence_with_the_finding`; end to end on A's worker `test_the_round_trip_today_…`; under Tk `test_workbook_window.py::test_a_build_again_today_…` |
| M2 the feature left in a part made new | `_features_left_sentence` in `carried_status` | `test_the_result_says_what_was_carried_unsaved_and_the_feature_left_…`; the round trip |
| M3 not read: the reason, the record's sentence, no press again | `carried_status` | `test_an_old_assembly_not_read_says_why_…` |
| M4 a stop: A's sentence, its tail, "carried before it" only when unsaved; the files-changed check apart | `_split_stop`, `carried_status` | `test_a_carry_that_stopped_says_the_workers_sentence_…`, `test_a_files_change_found_after_the_carry_…` |
| M5 lightweight said once | `carry_sentence` drops the `WHY_LIGHTWEIGHT` items `_component_states` speaks for | `test_a_lightweight_component_is_said_once_…` |
| S1 verdict per item, `WHY_NOT_CARRIED` grouped | `_with_verdict`, `_named_sentences` | `test_a_mate_is_always_told_it_is_not_made_again` (5 cases), `test_the_question_says_each_kind_of_reason_once` |
| S2 no save asked when nothing would be carried | `carry_sentence` | `test_the_question_says_each_kind_of_reason_once` |
| S3 length | one sentence per kind; the closed clause short; findings once at the end | `test_the_question_says_what_is_carried_…_short_…` (< 120 words), `test_the_whole_question_is_a_length_a_person_reads` (< 200) |
| S4 A's anchors | `gearbox.carry_anchors` takes `CarryResult.anchors` (by the new Name2) and nothing else: the re-derivation is dropped (ruled) | the finish test (A's anchors), the round trip (A's worker) |
| S5 the result's D14 sentence | `_modes_words` from `carry.modes` | `test_the_result_says_a_mode_gone_…` |
| S6 the in-context sentence as an if | `CARRY_IN_CONTEXT` | the result tests |
| S7 a raised read: "on disk", the reason as a clause | `carried_status` | `test_a_read_that_raised_…` |
| S8 grammar | fallback *beside it*; *a mate's face*; the colon; `moved` grouped, *against* its anchor | the reason and fallback tables, `test_the_results_other_sentences_…` |
| S9 entity kinds through the round trip | `_desk(entity_kinds)` | `test_the_round_trip_…[False]`, `[True]` |
| S10 "bore" | the where slot "bore" / "axis" / ""; `carry_for` fills `CarryBody.bore_mm` from the OLD part's spec (what its Bore Diameter was written from; the contract's §2.1, which says the old part — the ruling's "the plan's gear" read so, since the radius is read on the old part) | the reason table (bore, axis, ""), `test_carry_for_…` |
| The coordinator's privacy ruling | `ui_text.bare_files` on every word of A's that B says or keeps (`stopped`, `unread`, subjects, sentences) | `test_a_path_in_the_workers_words_…`, `test_a_read_that_raised_…`; under Tk, the record's carry holds no folder |
| The window test on A's worker | two Tk tests replace the hand-made one: a carry, and today's state | `test_workbook_window.py` |
| The window's carry sentence in its own try | `_finish_build` | — |
| New reasons from A | `WHY_TOO_LONG` (§9.3's sentence), `WHY_REFUSED` (*M1 is not made again: SolidWorks refused it, saying …*) | the reason table |

**Word counts** (RangeBox, W9a's user work, Sun's Flank to arcs). The whole question, everything set: 326 before, 169
now (the build's own part, not B's, is 82 of them; B's carry part 180 before, 85 now). Today's question (every finding
None) is unchanged at 145. The result's carry part, everything set: ~190 before, 133 now (the build's own 179 before
it).

**Shape requests after the review's rulings**: 1 (anchors) and 3 (owner slots) made by A and used; 2, 4 and 5 stand as
work-arounds; 6 (`exists` into the read) made by A, so the round trip no longer patches `os.path.isfile`; 7 dropped.
Still asked of A, through the coordinator: **the files-changed fact a field of its own** (the review's M4). Until then
B tells it from the worker's own words (`ui_text._split_stop`, matching A's sentence); a change to that sentence would
make it said as a stop again, which the test `test_a_files_change_found_after_the_carry_…` would catch only with its
hand-written copy of A's words.

## The re-check of the fix round (`W9D-REVIEW-B.md`, `56ca105`)

Committed as `1ab1029` and the commit after it.

| Point | Done | Test |
|---|---|---|
| N1 the placement sentence | *Your components were placed where they stood in H, the mode RangeBox.SLDASM showed; one no mate holds stands there in every mode.*, the clause only when a carried component is held by no remade mate, not fixed and not fixed by a fallback | `test_a_component_a_carried_mate_holds_is_not_said_to_stand_still_in_every_mode`; the six states |
| N2 the files changed | from A's `CarryResult.changed_files`; A's sentence in `stopped` cut at the last place those names begin it; `CarryEntry.changed_files` (defaulted, schema 10) and `stopped` the stop only | `test_a_files_change_found_after_the_carry_…` (a stop with the fact keeps its tail), `test_the_files_changed_are_kept_by_name_…` |
| N3 the window's own `try` | `ui_text.carry_unsaid`, through `bare_files`, the save asked only when unsaved | `test_a_carry_sentence_that_raises_is_said_as_its_own_…` |
| N4 `bare_files` | a file's name ends on punctuation as well as a space; a folder segment never holds `. ` or `, `; the leftover pass only before a file's name, so *A\B* stays | `test_bare_files_ends_a_file_name_on_punctuation_…` (6 cases) |
| `WHY_DIFFERS` ("left", name) | *Lock4 made again read otherwise than it was and could not be taken out again: it is left in RangeBox_r2 as Lock4-2; delete it there in SolidWorks.* | `test_a_mate_left_in_the_new_assembly_…` |
| `FELL_NEW_ERROR` on an app mate | *… with your Lock3 made again the app's G1 meshes G2 reads error 46 in L, which it did not before your mates were made again in H, the mode RangeBox.SLDASM showed, so it was not kept.* | `test_a_fallback_for_an_app_mate_put_in_error_…` |
| `OLD_UNREAD` with `CARRY_INSERTS` None | the lead, then W9a's own sentence for an old assembly not open (state 7 below) | `test_an_old_assembly_unread_because_nothing_can_be_carried_…` |
| `CarryResult.facts` | never said (the log's) | — |
| *each* with one component | dropped | `test_the_result_says_what_was_carried_…` |
| the stop's tail repeating A's step | the step the stop names is left out of *It did not get to …* | `test_a_files_change_found_after_the_carry_…` |
| A's not-open parenthesis | A's text, left as it is | — |

**Still a field for A** (asked, not matched): why the times and flags could not be read after the carry. A still
appends *Whether your files changed could not be read after the carry: …* to `stopped`; B no longer matches it, so it
is said as part of the stop (with *What was carried before it …* when something is unsaved), which is not false but
reads as a stop. An `after_unread: str` field would let B say it as the fact it is. Also cleaner: A no longer
appending the files-changed sentence to `stopped` at all (B cuts it by `changed_files`' names meanwhile).

**Residual of N4**: a folder whose own name holds `, ` or `. ` before a file (*C:\My Docs, old\x.SLDPRT*) leaves the
part before that comma (*My Docs, x.SLDPRT*).

## In step with A's third round (`9837c73`)

Committed as `73db554`. Tests at the end of `tests/test_workbook_carry.py`.
- `CarryResult.after_unread`: said after the result as the fact it is (A's sentence through `bare_files`), never as a
  stop; kept as `CarryEntry.after_unread` (defaulted, schema 10). `test_files_unread_after_the_carry_…`.
- `CarryResult.resolved_in_old`: *Sprocket-9 was lightweight in RangeBox.SLDASM and is resolved there now: SolidWorks
  loaded its part to carry it.* (grouped). The question's one lightweight sentence: *Sprocket-1 was lightweight as read:
  carrying it resolves it in RangeBox.SLDASM too, if that is open, and its Lock3 is made again only if you set it
  resolved in SolidWorks before you press.* `test_a_component_resolved_in_the_old_assembly_…`,
  `test_a_lightweight_component_is_said_once_…`.
- A fixed component placed by its world frame: *each where it stood*, never *against its gear*.
  `test_a_fixed_component_placed_by_its_world_frame_…`.
- R.2's moved-folder refusal: the result says A's clause, then the record's sentence, with no advice; the question's
  closed clause names the condition: *If RangeBox.SLDASM is closed, open it first unless this SolidWorks last saved it
  and its files, those files are where it says, and nothing of yours is open.*
  `test_an_old_assembly_whose_files_were_moved_…`.
- B's earlier ask of A (an `after_unread` field) is met; the after-carry sentence is no longer in `stopped`.

## After the first SolidWorks 2026 run (`W9D-DEMONSTRATION-REVIEW.md` addendum, `e2207d9`)

1. **The question foresees only what the inventory knows.** A gear mate the inventory holds whole, every entity's kind
   known, that `plan_carry` names unread (its ratio and sense are never kept) is said as *may*: *Your UserGear6 is made
   again if the press reads its gear ratio and which way it turns.* A gear mate on a face of a gear whose part is new,
   while `COAXIAL_FACE_READ` is set (the coaxial read is never kept): *Your UserGearRoot is made again only if the face
   of Sun it is on proves to be on Sun's axis, since Sun's part is new.* Every other reason stays a fact.
   `test_what_only_the_inventorys_silence_names_is_said_as_may`. **For A** (not needed for the sentences, but
   cleaner): a way for `plan_carry` to know it is foreseeing, e.g. `OldWork.recorded: bool` (or `OldMate.values_known`
   False), so it says a ratio, a sense or a face's axis as not known rather than as missing; B would then read that
   instead of telling silence from the inventory itself.
2. **Reasons with no why** (UserAxis9 on a component suppressed in the mode showing; UserAsm6 beside a lightweight
   component). A's fields do not carry it: both entities come back `UNREAD_ENTITY` with `OldEntity.unread` "". **For A**:
   set `unread` to the clause, e.g. *"Sprocket-9 is suppressed in H, the mode RangeBox.SLDASM showed"* and *"the
   assembly's own planes are not read while a component is lightweight"*; B's clause already says it: *SolidWorks would
   not describe UserAxis9 wholly (Sprocket-9 is suppressed in H, the mode RangeBox.SLDASM showed), so it is not made
   again.*
3. **The footer after the build.** By design (W9a's rule 3) a job's own sentence stands in place of the state's lines
   until the workbook's next save, so §9.4's line was hidden behind the build's note; the build's sentence itself ends
   *Save RangeBox_r2 in SolidWorks to keep what was carried.* when the carry is unsaved. Now §9.4's line is said after a
   job's sentence too, unless that sentence asks the save itself (a stop's does not). **For the script**: after the
   build, read the footer (`desk.say_footer`, with the build's note) and accept either *Save RangeBox_r2 in SolidWorks
   to keep what was carried.* (the build finished its carry) or `ui_text.carry_footer_line(record)` (it did not say
   the save); with the note gone (`desk.note = None` and the footer read again), the line itself.
   `test_the_footer_after_a_build_…`; under Tk `test_a_build_again_hands_the_worker_its_carry_…`.
4. **A mate in error as read.** The inventory holds each mate's code, so: *Lock3 was in error in RangeBox.SLDASM as
   read; made again, it is carried only if it reads the same error, and it never keeps a gear from turning.*, for the
   mates the plan makes again. `test_a_mate_in_error_as_read_…`.

The seven printed states below are unchanged by this round.

## The re-check of `5f52913` (`W9D-REVIEW-B.md`, `7892a53`)

- **B1**: the definite reasons drop the axis *may*'s mates by mate, not by gear, so UserGearRoot is said once.
  `test_the_demonstrations_question_names_each_mate_in_exactly_one_sentence` builds the demonstration's question on
  2026 (the probe reads measured, the write gates patched, the coaxial read shown; a ratio *may*, an axis *may*, a face
  of a part made new, a mate in error, a lock) and asserts every mate is named in exactly one sentence. To hold that for
  a single mate made again that the inventory holds in error, its clause now joins the lead: *… and makes your Lock3
  again in the modes it was on in; it was in error in RangeBox.SLDASM as read, and made again it is carried if it reads
  no error or the one it had, and not if it keeps a gear from turning.* With several, the sentence of its own stands.
- **B2**: the axis *may* only while `CARRY_GEAR_MATE_ON_AN_APP_GEAR` is True and `gear` is in `CARRY_REMAKE_KINDS`
  (else the plan's reason, said as fact); the in-error clause in the reviewer's words: *Lock3 was in error in
  RangeBox.SLDASM as read; made again, it is carried if it reads no error or the one it had, and not if it keeps a gear
  from turning.*
- **B3** waited for A's coded cause: below.

The seven printed states below are unchanged by this round.

## B3: the unread reasons' coded causes (A's `5d51640`)

- **The result.** `WHY_UNREAD` with `CAUSE_SUPPRESSED` (component, mode) says *UserAxis9 is on Sprocket-9, which is
  suppressed in H, the mode RangeBox.SLDASM showed, so it could not be read and is not made again.*; with no modes,
  *… which is suppressed in RangeBox.SLDASM, so …*. With `CAUSE_BESIDE_LIGHTWEIGHT` (component) it is Gear Generator's
  rule, said so: *UserAsm6 is on a plane of RangeBox.SLDASM itself, which Gear Generator does not read while
  SprocketLight-1 is lightweight in it, so it is not made again.* Mates of one cause, component and mode group into
  one sentence (*Lock1 and UserAxis9 are on Sprocket-1, which is suppressed in 2H, …, so they could not be read and are
  not made again.*), as a component not carried groups its mates. No cause: *SolidWorks would not describe … wholly
  (…)* stood (reworded in the next round, below). The worker's clause is not shown where the cause is worded.
- **The question.** `recorded_old_work` gives a recorded entity the worker's cause where the inventory knows it: on a
  component of the user's suppressed as read (state 0) with its kind unread or empty, `CAUSE_SUPPRESSED` with mode
  `""` (the inventory does not keep the mode showing); the assembly's own entity while a component read lightweight,
  `CAUSE_BESIDE_LIGHTWEIGHT` with the first such. A schema 9 inventory's entities (no kinds) take no cause and stay
  *may*. The suppressed component's own advice takes its mates, one thought: *Housing-1 was suppressed in the mode
  RangeBox.SLDASM showed, as read, so UserAxis9 on it could not be read: show a mode where Housing-1 is resolved before
  you press, or Housing-1 may not be carried and UserAxis9 is not made again.* (several: *… and they are not made
  again.*). Beside a lightweight component the question says what the user can change: *UserAsm6 is on a plane of
  RangeBox.SLDASM itself, which Gear Generator does not read while Sprocket-1 is lightweight in it: it is made again
  only if you set Sprocket-1 resolved in SolidWorks before you press.* Each such mate is named in one sentence only.
- **Fragments.** None the demonstration script matches changed: a suppressed component with no unread mate keeps
  *… as read: show a mode where it is resolved before you press, or it may not be carried.*
- Tests: four on the result's exact strings, one end to end on A's worker on the fake (`_tc_again`, Sprocket-1
  suppressed in 2H with Lock1 and UserAxis9), two on the question's.

The seven printed states below are unchanged by B3 (none has a suppressed component or a plane of the assembly).

## The re-check of `b67cdc5` (`W9D-REVIEW-B.md`, `8164a3d`) and A's seventh round (`6211143`)

- **Item 1, the tense beside D10.** Where the carry left the lightweight component resolved in the old assembly
  (`CarryResult.resolved_in_old`), the plane's reason is said in the past, beside D10's sentence: *UserAsm6 is on a
  plane of T.SLDASM itself, which Gear Generator did not read while Sprocket-1 was lightweight in it, so it is not made
  again. … Sprocket-1 was lightweight in T.SLDASM and is resolved there now: SolidWorks loaded its part to carry it.*
  Where it is still lightweight the present stays. The record's per-item sentence (`carry_entry`) follows the same
  field.
- **Item 2, SolidWorks once.** No type read (the worker's clause *SolidWorks would not say what kind of entity it
  is*): *SolidWorks would not say what kind of entity Coincident8 is on, so it is not made again.* A type read that the
  app does not take (`CAUSE_TYPE_NOT_TAKEN`): *Coincident8 is on a kind of entity Gear Generator does not make mates on
  again, so it is not made again.* The type's number stays in the record's subjects and is not shown: the contract
  names only the types the app takes. Any other clause with no cause: *M1 could not be read wholly (SolidWorks would
  not say what it is on)*, SolidWorks only inside the worker's own clause; with no clause, *M1 could not be read
  wholly*. The question's inventory cannot tell the two kinds apart (it keeps the kind, not the type), so it says the
  last.
- **Item 3, B1's check over every shape.** `_each_mate_once` runs the exactly-one-sentence check on any record; it
  now runs on the demonstration's shape, the suppressed shape, the beside-lightweight shape and both together. The
  escape is tightened: a mate may be named nowhere only if the plan makes it again among several and the lead says
  *makes your N mates again* with N the plan's own count.
- **Fragments.** None the demonstration script matches changed.

The seven printed states below are unchanged by this round.

## A mate kept under SolidWorks' name (A's `7e3ad9a`)

`CarryResult.remade` holds `(old, kept, on)`; where the kept name differs the result says it as a renamed component
is: one mate, *… and your Mate1303 (was Lock3), on in the modes it was on in.* (A's worker on the fake,
`rename_refused`); several, counted, with the renamed ones named, *your 3 mates, Mate12 (was Lock2) and Mate14 (was
Lock3) among them, each on in the modes it was on in.* The same form where the result names such a mate while it stands
in the new revision: in error as before (*Your Mate12 (was Lock2) was in error in RangeBox.SLDASM and is in
RangeBox_r2 too, as it was.*) and kept beside a fallback (*…; Mate12 (was Lock2) beside it was.*); a mate a fallback
deleted keeps its old name, as it is no longer there. The record already wrote the kept name (`CarriedMateEntry(name=
kept, was=old)`, the inventory's `UserMateEntry(name=kept)`), so the next question (*… makes your Mate1303 again in the
modes it was on in.*) and W9a's sentence of what stays name it so; the footer's line and the lost-carry line name no
mate. Pinned on exact strings, one end to end on A's worker. No fragment the demonstration matches changed; the seven
printed states are unchanged.

## The re-check of `11a63ab` (`W9D-REVIEW-B.md`, `684ac38`)

- **Item 1, a limit mate foreseen as plain.** The record keeps a mate's type (5 or 6) and nothing that tells a limit
  mate from a plain one (no type name, no range), so while `CARRY_REMAKE_KINDS` on the SolidWorks the record last saw
  answers the plain kind and its limit kind differently, a recorded distance or angle mate is said as *may*, grouped by
  kind: *Your UserLimit10 is made again if the press reads it as a plain distance mate; a limit distance mate is not
  made again.* (plain allowed: the plan makes it again, and it leaves the lead's count), or *Your UserLimit10 is made
  again only if the press reads it as a limit distance mate; a plain distance mate is not made again.* (limit allowed:
  the plan's unmeasured reason for the plain kind gives way to it). Where both kinds are allowed or both refused the
  question says it as fact, as before. With nothing else definite carried the *may* takes the lead's time (*As read at
  …, your UserLimit10 is made again if …*) and the question asks the save. Pinned on the real `plan_carry` with gate
  tuples that split the kinds each way and that do not, every shape through `_each_mate_once`.
- **Item 2, each name beside its assembly.** *Your Dist9 was in error in RangeBox.SLDASM and, as Mate14, is in
  RangeBox_r2 too, as it was.*; a name unchanged keeps today's sentence. And the one mate made again among several,
  renamed: *1 of your 2 mates, Mate12 (was M1), on in the modes it was on in* (no longer *…, Mate12 (was M1) among
  them, each …*).
- No fragment the demonstration matches changed.

## The merge's ruling (`7ce641e`): close without saving beside an unsaved carry

Wherever the app says to close the record's assembly without saving (a stop in a part left in error, the footer's line
on documents left in error, the still-in-error sentence; the assembly named with the part or among the documents),
that advice stands and says its cost inside its parenthesis, and the carry's save line is not said beside it, in the
footer (state lines) or after a job's sentence (`CLOSE_LOSES_CARRY` marks it). On A's worker and W9c's press on the
fake, a carry left unsaved in RangeBox_r2 and an Update of r2 stopped on Sun's part in error:

> Update SolidWorks stopped. Gear_m1.25_N29_r2.SLDPRT: SolidWorks reported an error rebuilding Gear_m1.25_N29_r2. It
> had already changed Gear_m1.25_N29_r2, not saved, and Gear_m1.25_N29_r2 is left in error: close it and RangeBox_r2
> in SolidWorks without saving, answering No when SolidWorks asks to save them (the files on disk are as before this
> Update; closing RangeBox_r2 so also discards whatever else is unsaved in it, including what Build again… carried
> into it, which RangeBox.SLDASM held when it was carried), then press Update SolidWorks again.

The footer after it is that sentence alone; the footer with no note ends with the same advice in its *have changes
… that are not saved* form, and no *save it in SolidWorks to keep it*. Pinned too: the assembly alone left in error,
the assembly beside a part in error, several parts, a stopped Update's own sentence closing the assembly; and, with no
close advice (a stop with nothing in error, documents unsaved but none in error), the carry line as before.

- **Which clauses, and why.** The old assembly's name is the carry's own (`CarryEntry.assembly`), as the lost-carry
  line has it. *Build again… carries it again* is not said: a later Build again… reads the record's current revision,
  RangeBox_r2, not RangeBox.SLDASM.
- **The user's own unsaved work (W9C-RUNS-REVIEW's low should-fix).** No press reads the save flag of an assembly that
  was open before it (`_note_opened` reads only a document the press loads, `_vouches` only one marked unsaved), so the
  app cannot know it was modified before the press; the short form is said whenever the assembly is closed so, carry
  or not: *; closing RangeBox so also discards whatever else is unsaved in it*. That changes W9c's pinned sentences in
  `tests/test_workbook_in_place_round_trip.py` (five strings, the parenthesis only); a part-only close is unchanged.
- **Fragments.** `probe/w9c_demonstration.py`'s matchers (*the assembly named*, *in SolidWorks without saving,
  answering No when SolidWorks asks to save*, no *to keep*) still match; its hand-written examples in its self-check
  keep the old parenthesis, which no matcher reads. `probe/w9d_demonstration.py`'s carry footer line and save phrase
  are unchanged wherever no close advice is given.
- The window passes the job's record to `gearbox_update_status` (`record=`), used when the finish wrote none.

### The review of `9cbfc08` (`dd07597`): the cost parenthesis reworded

The clause now names what it closes and counts the carry once, as part of what is unsaved; the old assembly is said
in the past, since the app cannot see whether the user changed it since. The lost-carry line likewise: *RangeBox_r2 was
closed without saving after Build again… carried your work into it, so it does not hold it; RangeBox.SLDASM held it
when it was carried.* Each form as printed (the fake; the footer's forms with the record's marks set by hand):

- Stop, carry unsaved: *… close it and RangeBox_r2 in SolidWorks without saving, answering No when SolidWorks asks to
  save them (the files on disk are as before this Update; closing RangeBox_r2 so also discards whatever else is
  unsaved in it, including what Build again… carried into it, which RangeBox.SLDASM held when it was carried), then
  press Update SolidWorks again.*
- Stop, no carry: *… close it and RangeBox in SolidWorks without saving, answering No when SolidWorks asks to save
  them (the files on disk are as before this Update; closing RangeBox so also discards whatever else is unsaved in
  it), then press Update SolidWorks again.*
- Footer, the assembly alone in error: *… close it in SolidWorks without saving (the file on disk is as before that
  Update; closing RangeBox_r2 so also discards whatever else is unsaved in it, including …), then press …*
- Footer, the assembly beside a part in error: *… close them all in SolidWorks without saving, answering No when
  SolidWorks asks to save them (the files on disk are as before that Update; closing RangeBox_r2 so also discards …)*
- Footer, several parts: *… close them all and RangeBox_r2 in SolidWorks without saving, answering No when SolidWorks
  asks to save them (the files on disk are as before that Update; closing RangeBox_r2 so also discards …)*
- Parts only, no assembly closed: unchanged (*close it in SolidWorks without saving (the file on disk is as before
  this Update), then press Update SolidWorks again.*).

`probe/w9c_demonstration.py`'s matched words (*in SolidWorks without saving, answering No when SolidWorks asks to save*,
the assembly's name) are unchanged; `probe/w9d_demonstration.py` matches *was closed without saving after Build again…
carried your work into it* of the lost-carry line, unchanged. The printed states are unchanged.

## The strings, in full

Made by A's worker on the fake (`Desk`'s RangeBox, W9a's user work: Sprocket-1 locked to Sun, Housing-1 fixed, a
Keyway in Sun's part, a Groove in RangeSlv's; the edit Sun's Flank to arcs). States 4 and 5 put a hand-made fallback
and stop on the real carry's result, since the fake makes neither on this work. The fake names an inserted component by
its handle (*carried1-1*); SolidWorks keeps the file's name. The fake also reads the user's parts marked after the
insert, where the 2026 probe found SolidWorks does not (`CARRY_INSERT_MARKS_USER_DOCUMENTS_ON_2026` False), hence the
*SolidWorks reads … as changed* sentence in states 3–5. The time is the run's.

### 1. Every W9d finding None (2024 today; 2026 before `013c14c`)

QUESTION (145 words):
Gear_m1.25_N29 (Sun): Flank changed from involute to arcs, which its values cannot carry, so it needs a new part. Build again as RangeBox_r2? That makes a new part for Sun (Gear_m1.25_N29_r2), reuses 4 parts that have not changed and makes a new layout part, carrier part and assembly (RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM). Nothing is overwritten, and RangeBox.SLDASM stays as it is on disk, but it shares the 4 reused parts: a later Update SolidWorks that changes one of them changes RangeBox.SLDASM too. Gear Generator has not yet been shown to carry your work into a new revision on SolidWorks 2026 (findings.CARRY_INSERTS_ON_2026), so as read at 15:38, your Sprocket-1, Housing-1 and Lock3 stay in RangeBox.SLDASM, and your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces; RangeBox_r2 has none of them, nor anything added since. Your Groove in Sleeve_m1.25_N17 comes with that part, which RangeBox_r2 reuses.

RESULT (241 words):
Built 1 part, RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM, reusing the 4 parts already built; no interference between the gears in any mode, where they stand. Its turning gears are mated to turn in each of its 3 modes, one configuration each (H, N and L), and SolidWorks reports no mate in error in any of them: it opens in H; to switch mode, double-click another mode's configuration in SolidWorks' ConfigurationManager. Drag Sun in SolidWorks and the rest of its train follow. RangeSlv slides along Output, to its place in each mode. The 3 copies of Planet turn on Carrier, and RangeBox_r2_Carrier_Carrier holds Carrier's axes and planes only: a plate and pins are yours to add. Ring stays fixed where it is placed: its shaft does not turn. A turn you give the gears in one mode can show in other modes, so a dog can stand across its sleeve in another; to put the gears back there, press Update SolidWorks with that mode showing. 1 thing to do by hand: Assign a material to Gear_m1.25_N29_r2; the build leaves it unset. Gear Generator has not yet been shown to carry your work into a new revision on SolidWorks 2026 (findings.CARRY_INSERTS_ON_2026), so your Sprocket-1, Housing-1 and Lock3 stay in RangeBox.SLDASM, as read when this build began; RangeBox_r2 has none of them. As read at 15:38, your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces; RangeBox_r2 has none of it, nor anything added since.

### 2. The 2026 probe reads set, the write gates None (today, since A's `013c14c`)

QUESTION (145 words):
Gear_m1.25_N29 (Sun): Flank changed from involute to arcs, which its values cannot carry, so it needs a new part. Build again as RangeBox_r2? That makes a new part for Sun (Gear_m1.25_N29_r2), reuses 4 parts that have not changed and makes a new layout part, carrier part and assembly (RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM). Nothing is overwritten, and RangeBox.SLDASM stays as it is on disk, but it shares the 4 reused parts: a later Update SolidWorks that changes one of them changes RangeBox.SLDASM too. Gear Generator has not yet been shown to carry your work into a new revision on SolidWorks 2026 (findings.CARRY_INSERTS_ON_2026), so as read at 15:38, your Sprocket-1, Housing-1 and Lock3 stay in RangeBox.SLDASM, and your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces; RangeBox_r2 has none of them, nor anything added since. Your Groove in Sleeve_m1.25_N17 comes with that part, which RangeBox_r2 reuses.

RESULT (241 words):
Built 1 part, RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM, reusing the 4 parts already built; no interference between the gears in any mode, where they stand. Its turning gears are mated to turn in each of its 3 modes, one configuration each (H, N and L), and SolidWorks reports no mate in error in any of them: it opens in H; to switch mode, double-click another mode's configuration in SolidWorks' ConfigurationManager. Drag Sun in SolidWorks and the rest of its train follow. RangeSlv slides along Output, to its place in each mode. The 3 copies of Planet turn on Carrier, and RangeBox_r2_Carrier_Carrier holds Carrier's axes and planes only: a plate and pins are yours to add. Ring stays fixed where it is placed: its shaft does not turn. A turn you give the gears in one mode can show in other modes, so a dog can stand across its sleeve in another; to put the gears back there, press Update SolidWorks with that mode showing. 1 thing to do by hand: Assign a material to Gear_m1.25_N29_r2; the build leaves it unset. Gear Generator has not yet been shown to carry your work into a new revision on SolidWorks 2026 (findings.CARRY_INSERTS_ON_2026), so your Sprocket-1, Housing-1 and Lock3 stay in RangeBox.SLDASM, as read when this build began; RangeBox_r2 has none of them. As read at 15:38, your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces; RangeBox_r2 has none of it, nor anything added since.

### 3. Everything set: RangeBox with W9a's user work carried

QUESTION (175 words):
Gear_m1.25_N29 (Sun): Flank changed from involute to arcs, which its values cannot carry, so it needs a new part. Build again as RangeBox_r2? That makes a new part for Sun (Gear_m1.25_N29_r2), reuses 4 parts that have not changed and makes a new layout part, carrier part and assembly (RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM). Nothing is overwritten, and RangeBox.SLDASM stays as it is on disk, but it shares the 4 reused parts: a later Update SolidWorks that changes one of them changes RangeBox.SLDASM too. As read at 15:38, RangeBox_r2 takes your Sprocket-1 and Housing-1 and makes your Lock3 again in the modes it was on in. Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces (its Flank changed); your Groove comes with Sleeve_m1.25_N17. RangeBox_r2 holds what it carries unsaved. If RangeBox.SLDASM is closed, open it first unless this SolidWorks last saved it and its files, those files are where it says, and nothing of yours is open. Assembly features, display states and appearances stay behind; sub-assemblies come over rigid, pattern instances as components of their own.

RESULT (308 words):
Built 1 part, RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM, reusing the 4 parts already built; no interference between the gears in any mode, where they stand. Its turning gears are mated to turn in each of its 3 modes, one configuration each (H, N and L), and SolidWorks reports no mate in error in any of them: it opens in H; to switch mode, double-click another mode's configuration in SolidWorks' ConfigurationManager. Drag Sun in SolidWorks and the rest of its train follow. RangeSlv slides along Output, to its place in each mode. The 3 copies of Planet turn on Carrier, and RangeBox_r2_Carrier_Carrier holds Carrier's axes and planes only: a plate and pins are yours to add. Ring stays fixed where it is placed: its shaft does not turn. A turn you give the gears in one mode can show in other modes, so a dog can stand across its sleeve in another; to put the gears back there, press Update SolidWorks with that mode showing. 1 thing to do by hand: Assign a material to Gear_m1.25_N29_r2; the build leaves it unset. Carried into RangeBox_r2, unsaved: your carried1-1 (was Sprocket-1) and carried2-1 (was Housing-1), each where it stood, and your Lock3, on in the modes it was on in. Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces because its Flank changed (RangeBox.SLDASM and that file keep it). Your components were placed where they stood in H, the mode RangeBox.SLDASM showed. SolidWorks reads Sprocket.SLDPRT and Housing.SLDPRT as changed since they were inserted into RangeBox_r2: saving RangeBox_r2 with its parts saves those files again too. Assembly features, display states and appearances stay behind; sub-assemblies come over rigid, pattern instances as components of their own. If a part of yours was made in context of RangeBox.SLDASM, it still refers to that assembly's parts. Save RangeBox_r2 in SolidWorks to keep what was carried.

### 4. A tied cluster fallen back (hand-made fallback on the real carry)

QUESTION (175 words):
Gear_m1.25_N29 (Sun): Flank changed from involute to arcs, which its values cannot carry, so it needs a new part. Build again as RangeBox_r2? That makes a new part for Sun (Gear_m1.25_N29_r2), reuses 4 parts that have not changed and makes a new layout part, carrier part and assembly (RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM). Nothing is overwritten, and RangeBox.SLDASM stays as it is on disk, but it shares the 4 reused parts: a later Update SolidWorks that changes one of them changes RangeBox.SLDASM too. As read at 15:38, RangeBox_r2 takes your Sprocket-1 and Housing-1 and makes your Lock3 again in the modes it was on in. Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces (its Flank changed); your Groove comes with Sleeve_m1.25_N17. RangeBox_r2 holds what it carries unsaved. If RangeBox.SLDASM is closed, open it first unless this SolidWorks last saved it and its files, those files are where it says, and nothing of yours is open. Assembly features, display states and appearances stay behind; sub-assemblies come over rigid, pattern instances as components of their own.

RESULT (321 words):
Built 1 part, RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM, reusing the 4 parts already built; no interference between the gears in any mode, where they stand. Its turning gears are mated to turn in each of its 3 modes, one configuration each (H, N and L), and SolidWorks reports no mate in error in any of them: it opens in H; to switch mode, double-click another mode's configuration in SolidWorks' ConfigurationManager. Drag Sun in SolidWorks and the rest of its train follow. RangeSlv slides along Output, to its place in each mode. The 3 copies of Planet turn on Carrier, and RangeBox_r2_Carrier_Carrier holds Carrier's axes and planes only: a plate and pins are yours to add. Ring stays fixed where it is placed: its shaft does not turn. A turn you give the gears in one mode can show in other modes, so a dog can stand across its sleeve in another; to put the gears back there, press Update SolidWorks with that mode showing. 1 thing to do by hand: Assign a material to Gear_m1.25_N29_r2; the build leaves it unset. Carried into RangeBox_r2, unsaved: your carried1-1 (was Sprocket-1) and carried2-1 (was Housing-1), each where it stood. Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces because its Flank changed (RangeBox.SLDASM and that file keep it). carried1-1 is fixed where it stood in RangeBox_r2: with your Lock3 made again SolidWorks reads Sun unable to turn, so it was not kept. Your components were placed where they stood in H, the mode RangeBox.SLDASM showed. SolidWorks reads Sprocket.SLDPRT and Housing.SLDPRT as changed since they were inserted into RangeBox_r2: saving RangeBox_r2 with its parts saves those files again too. Assembly features, display states and appearances stay behind; sub-assemblies come over rigid, pattern instances as components of their own. If a part of yours was made in context of RangeBox.SLDASM, it still refers to that assembly's parts. Save RangeBox_r2 in SolidWorks to keep what was carried.

### 5. A stop part-way (hand-made stop on the real carry)

QUESTION (175 words):
Gear_m1.25_N29 (Sun): Flank changed from involute to arcs, which its values cannot carry, so it needs a new part. Build again as RangeBox_r2? That makes a new part for Sun (Gear_m1.25_N29_r2), reuses 4 parts that have not changed and makes a new layout part, carrier part and assembly (RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM). Nothing is overwritten, and RangeBox.SLDASM stays as it is on disk, but it shares the 4 reused parts: a later Update SolidWorks that changes one of them changes RangeBox.SLDASM too. As read at 15:38, RangeBox_r2 takes your Sprocket-1 and Housing-1 and makes your Lock3 again in the modes it was on in. Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces (its Flank changed); your Groove comes with Sleeve_m1.25_N17. RangeBox_r2 holds what it carries unsaved. If RangeBox.SLDASM is closed, open it first unless this SolidWorks last saved it and its files, those files are where it says, and nothing of yours is open. Assembly features, display states and appearances stay behind; sub-assemblies come over rigid, pattern instances as components of their own.

RESULT (334 words):
Built 1 part, RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM, reusing the 4 parts already built; no interference between the gears in any mode, where they stand. Its turning gears are mated to turn in each of its 3 modes, one configuration each (H, N and L), and SolidWorks reports no mate in error in any of them: it opens in H; to switch mode, double-click another mode's configuration in SolidWorks' ConfigurationManager. Drag Sun in SolidWorks and the rest of its train follow. RangeSlv slides along Output, to its place in each mode. The 3 copies of Planet turn on Carrier, and RangeBox_r2_Carrier_Carrier holds Carrier's axes and planes only: a plate and pins are yours to add. Ring stays fixed where it is placed: its shaft does not turn. A turn you give the gears in one mode can show in other modes, so a dog can stand across its sleeve in another; to put the gears back there, press Update SolidWorks with that mode showing. 1 thing to do by hand: Assign a material to Gear_m1.25_N29_r2; the build leaves it unset. Carried into RangeBox_r2, unsaved: your carried1-1 (was Sprocket-1) and carried2-1 (was Housing-1), each where it stood. Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces because its Flank changed (RangeBox.SLDASM and that file keep it). Your components were placed where they stood in H, the mode RangeBox.SLDASM showed; one no mate holds stands there in every mode. SolidWorks reads Sprocket.SLDPRT and Housing.SLDPRT as changed since they were inserted into RangeBox_r2: saving RangeBox_r2 with its parts saves those files again too. SolidWorks stopped the carry while making Lock3 again: AddMate5 answered nothing. It did not get to checking the assembly in every mode. What was carried before it is in RangeBox_r2, unsaved, and RangeBox_r2 as built is saved. Assembly features, display states and appearances stay behind; sub-assemblies come over rigid, pattern instances as components of their own. If a part of yours was made in context of RangeBox.SLDASM, it still refers to that assembly's parts.

### 6. The old assembly closed and not read (the write gates set, every probe read None, RangeBox.SLDASM not open)

QUESTION (196 words):
Gear_m1.25_N29 (Sun): Flank changed from involute to arcs, which its values cannot carry, so it needs a new part. Build again as RangeBox_r2? That makes a new part for Sun (Gear_m1.25_N29_r2), reuses 4 parts that have not changed and makes a new layout part, carrier part and assembly (RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM). Nothing is overwritten, and RangeBox.SLDASM stays as it is on disk, but it shares the 4 reused parts: a later Update SolidWorks that changes one of them changes RangeBox.SLDASM too. As read at 15:38, RangeBox_r2 takes your Sprocket-1 and Housing-1 and makes your Lock3 again in the modes it was on in. Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces (its Flank changed); your Groove comes with Sleeve_m1.25_N17. RangeBox_r2 holds what it carries unsaved. If RangeBox.SLDASM is closed when you press, nothing is carried: open it in SolidWorks first. Each component takes, in every mode of RangeBox_r2, its state in the mode RangeBox.SLDASM shows; its other states cannot be read without changing it. Assembly features, display states and appearances stay behind; sub-assemblies come over rigid, pattern instances as components of their own. (Not yet shown on SolidWorks 2026: findings.FILE_VERSION_READ_ON_2026, findings.DEPENDENCIES_READ_ON_2026 and findings.OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_2026.)

RESULT (249 words):
Built 1 part, RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM, reusing the 4 parts already built; no interference between the gears in any mode, where they stand. Its turning gears are mated to turn in each of its 3 modes, one configuration each (H, N and L), and SolidWorks reports no mate in error in any of them: it opens in H; to switch mode, double-click another mode's configuration in SolidWorks' ConfigurationManager. Drag Sun in SolidWorks and the rest of its train follow. RangeSlv slides along Output, to its place in each mode. The 3 copies of Planet turn on Carrier, and RangeBox_r2_Carrier_Carrier holds Carrier's axes and planes only: a plate and pins are yours to add. Ring stays fixed where it is placed: its shaft does not turn. A turn you give the gears in one mode can show in other modes, so a dog can stand across its sleeve in another; to put the gears back there, press Update SolidWorks with that mode showing. 1 thing to do by hand: Assign a material to Gear_m1.25_N29_r2; the build leaves it unset. RangeBox.SLDASM is not open in SolidWorks, and Gear Generator reads it then only when its close has been shown clean (findings.OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_2026), so nothing of yours was carried; as read at 15:38, your Sprocket-1, Housing-1 and Lock3 stay in RangeBox.SLDASM, and your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces; RangeBox_r2 has none of them, nor anything added since. Your Groove in Sleeve_m1.25_N17 comes with that part, which RangeBox_r2 reuses.

### 7. Today (2026 probe reads set, the write gates None), RangeBox.SLDASM closed

QUESTION (145 words):
Gear_m1.25_N29 (Sun): Flank changed from involute to arcs, which its values cannot carry, so it needs a new part. Build again as RangeBox_r2? That makes a new part for Sun (Gear_m1.25_N29_r2), reuses 4 parts that have not changed and makes a new layout part, carrier part and assembly (RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM). Nothing is overwritten, and RangeBox.SLDASM stays as it is on disk, but it shares the 4 reused parts: a later Update SolidWorks that changes one of them changes RangeBox.SLDASM too. Gear Generator has not yet been shown to carry your work into a new revision on SolidWorks 2026 (findings.CARRY_INSERTS_ON_2026), so as read at 15:38, your Sprocket-1, Housing-1 and Lock3 stay in RangeBox.SLDASM, and your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces; RangeBox_r2 has none of them, nor anything added since. Your Groove in Sleeve_m1.25_N17 comes with that part, which RangeBox_r2 reuses.

RESULT (253 words):
Built 1 part, RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM, reusing the 4 parts already built; no interference between the gears in any mode, where they stand. Its turning gears are mated to turn in each of its 3 modes, one configuration each (H, N and L), and SolidWorks reports no mate in error in any of them: it opens in H; to switch mode, double-click another mode's configuration in SolidWorks' ConfigurationManager. Drag Sun in SolidWorks and the rest of its train follow. RangeSlv slides along Output, to its place in each mode. The 3 copies of Planet turn on Carrier, and RangeBox_r2_Carrier_Carrier holds Carrier's axes and planes only: a plate and pins are yours to add. Ring stays fixed where it is placed: its shaft does not turn. A turn you give the gears in one mode can show in other modes, so a dog can stand across its sleeve in another; to put the gears back there, press Update SolidWorks with that mode showing. 1 thing to do by hand: Assign a material to Gear_m1.25_N29_r2; the build leaves it unset. Gear Generator has not yet been shown to carry your work into a new revision on SolidWorks 2026 (findings.CARRY_INSERTS_ON_2026). RangeBox.SLDASM was not open in SolidWorks, so it was not read again; as read at 15:38, your Sprocket-1, Housing-1 and Lock3 stay in RangeBox.SLDASM, and your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces; RangeBox_r2 has none of them, nor anything added since. Your Groove in Sleeve_m1.25_N17 comes with that part, which RangeBox_r2 reuses.

