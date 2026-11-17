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

## The strings, in full

Made by A's worker on the fake (`Desk`'s RangeBox, W9a's user work: Sprocket-1 locked to Sun, Housing-1 fixed, a
Keyway in Sun's part, a Groove in RangeSlv's; the edit Sun's Flank to arcs). States 4 and 5 put a hand-made fallback
and stop on the real carry's result, since the fake makes neither on this work. The fake names an inserted component by
its handle (*carried1-1*); SolidWorks keeps the file's name. The fake also reads the user's parts marked after the
insert, where the 2026 probe found SolidWorks does not (`CARRY_INSERT_MARKS_USER_DOCUMENTS_ON_2026` False), hence the
*SolidWorks reads … as changed* sentence in states 3–5. The time is the run's.

### 1. Every W9d finding None (today)

QUESTION (145 words):
Gear_m1.25_N29 (Sun): Flank changed from involute to arcs, which its values cannot carry, so it needs a new part. Build again as RangeBox_r2? That makes a new part for Sun (Gear_m1.25_N29_r2), reuses 4 parts that have not changed and makes a new layout part, carrier part and assembly (RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM). Nothing is overwritten, and RangeBox.SLDASM stays as it is on disk, but it shares the 4 reused parts: a later Update SolidWorks that changes one of them changes RangeBox.SLDASM too. Gear Generator has not yet been shown to carry your work into a new revision on SolidWorks 2026 (findings.CARRY_INSERTS_ON_2026), so as read at 14:57, your Sprocket-1, Housing-1 and Lock3 stay in RangeBox.SLDASM, and your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces; RangeBox_r2 has none of them, nor anything added since. Your Groove in Sleeve_m1.25_N17 comes with that part, which RangeBox_r2 reuses.

RESULT (241 words):
Built 1 part, RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM, reusing the 4 parts already built; no interference between the gears in any mode, where they stand. Its turning gears are mated to turn in each of its 3 modes, one configuration each (H, N and L), and SolidWorks reports no mate in error in any of them: it opens in H; to switch mode, double-click another mode's configuration in SolidWorks' ConfigurationManager. Drag Sun in SolidWorks and the rest of its train follow. RangeSlv slides along Output, to its place in each mode. The 3 copies of Planet turn on Carrier, and RangeBox_r2_Carrier_Carrier holds Carrier's axes and planes only: a plate and pins are yours to add. Ring stays fixed where it is placed: its shaft does not turn. A turn you give the gears in one mode can show in other modes, so a dog can stand across its sleeve in another; to put the gears back there, press Update SolidWorks with that mode showing. 1 thing to do by hand: Assign a material to Gear_m1.25_N29_r2; the build leaves it unset. Gear Generator has not yet been shown to carry your work into a new revision on SolidWorks 2026 (findings.CARRY_INSERTS_ON_2026), so your Sprocket-1, Housing-1 and Lock3 stay in RangeBox.SLDASM, as read when this build began; RangeBox_r2 has none of them. As read at 14:57, your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces; RangeBox_r2 has none of it, nor anything added since.

### 2. The 2026 probe reads set, the write gates None (today, since A's `013c14c`)

QUESTION (145 words):
Gear_m1.25_N29 (Sun): Flank changed from involute to arcs, which its values cannot carry, so it needs a new part. Build again as RangeBox_r2? That makes a new part for Sun (Gear_m1.25_N29_r2), reuses 4 parts that have not changed and makes a new layout part, carrier part and assembly (RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM). Nothing is overwritten, and RangeBox.SLDASM stays as it is on disk, but it shares the 4 reused parts: a later Update SolidWorks that changes one of them changes RangeBox.SLDASM too. Gear Generator has not yet been shown to carry your work into a new revision on SolidWorks 2026 (findings.CARRY_INSERTS_ON_2026), so as read at 14:57, your Sprocket-1, Housing-1 and Lock3 stay in RangeBox.SLDASM, and your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces; RangeBox_r2 has none of them, nor anything added since. Your Groove in Sleeve_m1.25_N17 comes with that part, which RangeBox_r2 reuses.

RESULT (241 words):
Built 1 part, RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM, reusing the 4 parts already built; no interference between the gears in any mode, where they stand. Its turning gears are mated to turn in each of its 3 modes, one configuration each (H, N and L), and SolidWorks reports no mate in error in any of them: it opens in H; to switch mode, double-click another mode's configuration in SolidWorks' ConfigurationManager. Drag Sun in SolidWorks and the rest of its train follow. RangeSlv slides along Output, to its place in each mode. The 3 copies of Planet turn on Carrier, and RangeBox_r2_Carrier_Carrier holds Carrier's axes and planes only: a plate and pins are yours to add. Ring stays fixed where it is placed: its shaft does not turn. A turn you give the gears in one mode can show in other modes, so a dog can stand across its sleeve in another; to put the gears back there, press Update SolidWorks with that mode showing. 1 thing to do by hand: Assign a material to Gear_m1.25_N29_r2; the build leaves it unset. Gear Generator has not yet been shown to carry your work into a new revision on SolidWorks 2026 (findings.CARRY_INSERTS_ON_2026), so your Sprocket-1, Housing-1 and Lock3 stay in RangeBox.SLDASM, as read when this build began; RangeBox_r2 has none of them. As read at 14:57, your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces; RangeBox_r2 has none of it, nor anything added since.

### 3. Everything set: RangeBox with W9a's user work carried

QUESTION (169 words):
Gear_m1.25_N29 (Sun): Flank changed from involute to arcs, which its values cannot carry, so it needs a new part. Build again as RangeBox_r2? That makes a new part for Sun (Gear_m1.25_N29_r2), reuses 4 parts that have not changed and makes a new layout part, carrier part and assembly (RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM). Nothing is overwritten, and RangeBox.SLDASM stays as it is on disk, but it shares the 4 reused parts: a later Update SolidWorks that changes one of them changes RangeBox.SLDASM too. As read at 14:57, RangeBox_r2 takes your Sprocket-1 and Housing-1 and makes your Lock3 again in the modes it was on in. Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces (its Flank changed); your Groove comes with Sleeve_m1.25_N17. RangeBox_r2 holds what it carries unsaved. If RangeBox.SLDASM is closed, open it first unless this SolidWorks last saved it and its files and nothing of yours is open. Assembly features, display states and appearances stay behind; sub-assemblies come over rigid, pattern instances as components of their own.

RESULT (312 words):
Built 1 part, RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM, reusing the 4 parts already built; no interference between the gears in any mode, where they stand. Its turning gears are mated to turn in each of its 3 modes, one configuration each (H, N and L), and SolidWorks reports no mate in error in any of them: it opens in H; to switch mode, double-click another mode's configuration in SolidWorks' ConfigurationManager. Drag Sun in SolidWorks and the rest of its train follow. RangeSlv slides along Output, to its place in each mode. The 3 copies of Planet turn on Carrier, and RangeBox_r2_Carrier_Carrier holds Carrier's axes and planes only: a plate and pins are yours to add. Ring stays fixed where it is placed: its shaft does not turn. A turn you give the gears in one mode can show in other modes, so a dog can stand across its sleeve in another; to put the gears back there, press Update SolidWorks with that mode showing. 1 thing to do by hand: Assign a material to Gear_m1.25_N29_r2; the build leaves it unset. Carried into RangeBox_r2, unsaved: your carried1-1 (was Sprocket-1) and carried2-1 (was Housing-1), each where it stood, and your Lock3, on in the modes it was on in. Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces because its Flank changed (RangeBox.SLDASM and that file keep it). Your components stand in every mode of RangeBox_r2 where they stood in H, the mode RangeBox.SLDASM showed. SolidWorks reads Sprocket.SLDPRT and Housing.SLDPRT as changed since they were inserted into RangeBox_r2: saving RangeBox_r2 with its parts saves those files again too. Assembly features, display states and appearances stay behind; sub-assemblies come over rigid, pattern instances as components of their own. If a part of yours was made in context of RangeBox.SLDASM, it still refers to that assembly's parts. Save RangeBox_r2 in SolidWorks to keep what was carried.

### 4. A tied cluster fallen back (hand-made fallback on the real carry)

QUESTION (169 words):
Gear_m1.25_N29 (Sun): Flank changed from involute to arcs, which its values cannot carry, so it needs a new part. Build again as RangeBox_r2? That makes a new part for Sun (Gear_m1.25_N29_r2), reuses 4 parts that have not changed and makes a new layout part, carrier part and assembly (RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM). Nothing is overwritten, and RangeBox.SLDASM stays as it is on disk, but it shares the 4 reused parts: a later Update SolidWorks that changes one of them changes RangeBox.SLDASM too. As read at 14:57, RangeBox_r2 takes your Sprocket-1 and Housing-1 and makes your Lock3 again in the modes it was on in. Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces (its Flank changed); your Groove comes with Sleeve_m1.25_N17. RangeBox_r2 holds what it carries unsaved. If RangeBox.SLDASM is closed, open it first unless this SolidWorks last saved it and its files and nothing of yours is open. Assembly features, display states and appearances stay behind; sub-assemblies come over rigid, pattern instances as components of their own.

RESULT (325 words):
Built 1 part, RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM, reusing the 4 parts already built; no interference between the gears in any mode, where they stand. Its turning gears are mated to turn in each of its 3 modes, one configuration each (H, N and L), and SolidWorks reports no mate in error in any of them: it opens in H; to switch mode, double-click another mode's configuration in SolidWorks' ConfigurationManager. Drag Sun in SolidWorks and the rest of its train follow. RangeSlv slides along Output, to its place in each mode. The 3 copies of Planet turn on Carrier, and RangeBox_r2_Carrier_Carrier holds Carrier's axes and planes only: a plate and pins are yours to add. Ring stays fixed where it is placed: its shaft does not turn. A turn you give the gears in one mode can show in other modes, so a dog can stand across its sleeve in another; to put the gears back there, press Update SolidWorks with that mode showing. 1 thing to do by hand: Assign a material to Gear_m1.25_N29_r2; the build leaves it unset. Carried into RangeBox_r2, unsaved: your carried1-1 (was Sprocket-1) and carried2-1 (was Housing-1), each where it stood. Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces because its Flank changed (RangeBox.SLDASM and that file keep it). carried1-1 is fixed where it stood in RangeBox_r2: with your Lock3 made again SolidWorks reads Sun unable to turn, so it was not kept. Your components stand in every mode of RangeBox_r2 where they stood in H, the mode RangeBox.SLDASM showed. SolidWorks reads Sprocket.SLDPRT and Housing.SLDPRT as changed since they were inserted into RangeBox_r2: saving RangeBox_r2 with its parts saves those files again too. Assembly features, display states and appearances stay behind; sub-assemblies come over rigid, pattern instances as components of their own. If a part of yours was made in context of RangeBox.SLDASM, it still refers to that assembly's parts. Save RangeBox_r2 in SolidWorks to keep what was carried.

### 5. A stop part-way (hand-made stop on the real carry)

QUESTION (169 words):
Gear_m1.25_N29 (Sun): Flank changed from involute to arcs, which its values cannot carry, so it needs a new part. Build again as RangeBox_r2? That makes a new part for Sun (Gear_m1.25_N29_r2), reuses 4 parts that have not changed and makes a new layout part, carrier part and assembly (RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM). Nothing is overwritten, and RangeBox.SLDASM stays as it is on disk, but it shares the 4 reused parts: a later Update SolidWorks that changes one of them changes RangeBox.SLDASM too. As read at 14:57, RangeBox_r2 takes your Sprocket-1 and Housing-1 and makes your Lock3 again in the modes it was on in. Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces (its Flank changed); your Groove comes with Sleeve_m1.25_N17. RangeBox_r2 holds what it carries unsaved. If RangeBox.SLDASM is closed, open it first unless this SolidWorks last saved it and its files and nothing of yours is open. Assembly features, display states and appearances stay behind; sub-assemblies come over rigid, pattern instances as components of their own.

RESULT (329 words):
Built 1 part, RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM, reusing the 4 parts already built; no interference between the gears in any mode, where they stand. Its turning gears are mated to turn in each of its 3 modes, one configuration each (H, N and L), and SolidWorks reports no mate in error in any of them: it opens in H; to switch mode, double-click another mode's configuration in SolidWorks' ConfigurationManager. Drag Sun in SolidWorks and the rest of its train follow. RangeSlv slides along Output, to its place in each mode. The 3 copies of Planet turn on Carrier, and RangeBox_r2_Carrier_Carrier holds Carrier's axes and planes only: a plate and pins are yours to add. Ring stays fixed where it is placed: its shaft does not turn. A turn you give the gears in one mode can show in other modes, so a dog can stand across its sleeve in another; to put the gears back there, press Update SolidWorks with that mode showing. 1 thing to do by hand: Assign a material to Gear_m1.25_N29_r2; the build leaves it unset. Carried into RangeBox_r2, unsaved: your carried1-1 (was Sprocket-1) and carried2-1 (was Housing-1), each where it stood. Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces because its Flank changed (RangeBox.SLDASM and that file keep it). Your components stand in every mode of RangeBox_r2 where they stood in H, the mode RangeBox.SLDASM showed. SolidWorks reads Sprocket.SLDPRT and Housing.SLDPRT as changed since they were inserted into RangeBox_r2: saving RangeBox_r2 with its parts saves those files again too. SolidWorks stopped the carry while making Lock3 again: AddMate5 answered nothing. It did not get to checking the assembly in every mode. What was carried before it is in RangeBox_r2, unsaved, and RangeBox_r2 as built is saved. Assembly features, display states and appearances stay behind; sub-assemblies come over rigid, pattern instances as components of their own. If a part of yours was made in context of RangeBox.SLDASM, it still refers to that assembly's parts.

### 6. The old assembly closed and not read (the write gates set, every probe read None, RangeBox.SLDASM not open)

QUESTION (196 words):
Gear_m1.25_N29 (Sun): Flank changed from involute to arcs, which its values cannot carry, so it needs a new part. Build again as RangeBox_r2? That makes a new part for Sun (Gear_m1.25_N29_r2), reuses 4 parts that have not changed and makes a new layout part, carrier part and assembly (RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM). Nothing is overwritten, and RangeBox.SLDASM stays as it is on disk, but it shares the 4 reused parts: a later Update SolidWorks that changes one of them changes RangeBox.SLDASM too. As read at 14:57, RangeBox_r2 takes your Sprocket-1 and Housing-1 and makes your Lock3 again in the modes it was on in. Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces (its Flank changed); your Groove comes with Sleeve_m1.25_N17. RangeBox_r2 holds what it carries unsaved. If RangeBox.SLDASM is closed when you press, nothing is carried: open it in SolidWorks first. Each component takes, in every mode of RangeBox_r2, its state in the mode RangeBox.SLDASM shows; its other states cannot be read without changing it. Assembly features, display states and appearances stay behind; sub-assemblies come over rigid, pattern instances as components of their own. (Not yet shown on SolidWorks 2026: findings.FILE_VERSION_READ_ON_2026, findings.DEPENDENCIES_READ_ON_2026 and findings.OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_2026.)

RESULT (249 words):
Built 1 part, RangeBox_r2_Layout, RangeBox_r2_Carrier_Carrier and RangeBox_r2.SLDASM, reusing the 4 parts already built; no interference between the gears in any mode, where they stand. Its turning gears are mated to turn in each of its 3 modes, one configuration each (H, N and L), and SolidWorks reports no mate in error in any of them: it opens in H; to switch mode, double-click another mode's configuration in SolidWorks' ConfigurationManager. Drag Sun in SolidWorks and the rest of its train follow. RangeSlv slides along Output, to its place in each mode. The 3 copies of Planet turn on Carrier, and RangeBox_r2_Carrier_Carrier holds Carrier's axes and planes only: a plate and pins are yours to add. Ring stays fixed where it is placed: its shaft does not turn. A turn you give the gears in one mode can show in other modes, so a dog can stand across its sleeve in another; to put the gears back there, press Update SolidWorks with that mode showing. 1 thing to do by hand: Assign a material to Gear_m1.25_N29_r2; the build leaves it unset. RangeBox.SLDASM is not open in SolidWorks, and Gear Generator reads it then only when its close has been shown clean (findings.OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_2026), so nothing of yours was carried; as read at 14:57, your Sprocket-1, Housing-1 and Lock3 stay in RangeBox.SLDASM, and your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces; RangeBox_r2 has none of them, nor anything added since. Your Groove in Sleeve_m1.25_N17 comes with that part, which RangeBox_r2 reuses.

