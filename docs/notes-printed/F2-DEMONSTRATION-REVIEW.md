# Review of F2's SolidWorks demonstration, before its first run

Read at `f6d920a` on `printed`: `probe/f2_demonstration.py` (2427 lines) and `docs/notes-printed/F2-DEMONSTRATION.md`, against
PLAN-PRINTED §3.3 (*The SolidWorks demonstration*, *Done when*), F2-PROBES-REVIEW §3 and §4, F2-REVIEW §9 and §10, and the
app at head (`ac83420` plus the review notes since; `src` unchanged since `2cc34d9`). Read beside it:
`probe/w9a_demonstration.py` (Desk9, `keyway`, `press`, `k3_keyway_and_bore`, `MASTER`) and
`probe/workbook_assembly_check.py` (`write_fixture`, `copy_built`, `keep_master`, W8's `Desk`). No code was changed and
nothing was run on SolidWorks. `--self-check` here (`PYTHONPATH=src`, Tk present): **31 checks, 0 failed**, its scratch
folder removed.

**Verdict: fit for its first run on SolidWorks 2026 once M1 (one line) is fixed.** Nothing in it can save, close or
change anything outside its run folder. It makes no SolidWorks call that an earlier script has not made, and every
press is judged by real readings against values worked out apart from the app. I found one way it can FAIL falsely
(M1). I found no way it can report clean while the app is wrong, beyond the small hazards in S1 and S2. Three of the
Done-when's steps are shown on other states than the plan's, or not at all (S3, S4). The herringbone is read but not
judged (S5).

## 1. What it shows against the plan and the two reviews

| Asked | Where | By what reading | Verdict |
|---|---|---|---|
| §3.3 form: a printed spur built from the form, pressed, the file checked by app and script; path, title, flag unchanged; the active document put back; the list | `form` (Coupon_A) | the app's facts; `step_read` (frame, schema, one solid in a closed shell, mm, d_a/2 16.5 and face 8 to 0.01, worked here); `docs_judged` (title, flag, Visible, active); `sw_files` (size, mtime, sha256); `list_judged`; calls (one SaveAs, nothing else watched) | shown |
| §3.3 form: one global changed, unsaved, refused; saved, refused | `refusals` (Coupon_R): MODIFIED, GLOBALS_DIFFER | C's words exactly, no press folder, no file changed, docs the same, no watched call | shown |
| §3.3 form: **after Update values**, a second press makes a second folder | `form` pressed twice (second folder; the first untouched; the same vertices). Coupon_R's value is **put back by hand** (`set_global`, line 2089), never by Update values | — | **partly** (S3) |
| §3.3 workbook: the 12 : 1 printed and built; assembly open, parts' windows closed; every part and the list with counts | `workbook`, component-only press | the parts read Visible False before the press; four SaveAs and nothing else watched; four files by both readings at four sizes up to z 68; the list's rows, counts and spans (k 2, 8, 2, 6); components resolved after | shown |
| §3.3 workbook: one Gears cell edited, refused until Update; updated and not saved, refused; saved, a second folder | `refusals`: Bore 14, then CHANGES_ON_UPDATE, then UNSAVED_MARK, then saved, then **FEATURE_IN_ERROR** (the keyway falls inside the bore). `userwork`: Printed typed, then Update, UNSAVED_MARK, saved, **written**, but with no press between the edit and the Update | — | **split across two gearboxes** (S4) |
| Probe review 1: the job's reads off a part not active or only a component | G2 component-only: GLOBALS_DIFFER; G1 behind the user's: MODIFIED, then GLOBALS_DIFFER; G1 not active: FEATURE_IN_ERROR | each refusal's words carry the live value (16) or the features as the script read them; Visible read before | shown (the feature-error read on a *component-only* part is shown only in its negative form, by the clean presses) |
| Probe review 2: the export of a component-only part through the job's own handle | component-only press | SaveAs ×4 with no open or activation, so the walk's handle is the only one (`DOCUMENT_BY_PATH_ROUTE` "walk") | shown |
| Probe review 3: a background part exported unactivated | Coupon (active) and G1 (MODIFIED/GLOBALS) only. A clean *write* of a background part is not pressed | — | partly (nit) |
| Probe review 4: a lightweight component refused, left lightweight | `refusals`: G4 set to 1 | the words, the state after (1 or 4), the assembly unmarked | shown |
| Probe review 5: every part of the 12 : 1 passes the size check | component-only press, plus the two later writes | the app's fact "checked" and the script's radius and extent, each against d_a/2 and the face worked here (fixture: no shift, default PA and backlash, checked) | shown |
| Probe review 6: a part the job opens itself | the copy closed; four OpenDoc6, four CloseDoc, four SaveAs | the user's part active and every flag the same after | shown |
| The open-beside fallback | FROM_COMPONENT False in this process | four OpenDoc6 and four CloseDoc; resolved after; Visible False again | shown |
| A herringbone's reading | `form` | radius and extent logged; **judged only if the app ever checks it** (lines 1815-1823) | **a fact, no verdict** (S5) |

**No judge passes on an empty set**, but one:

- `stem_lists_judged`, `list_judged`, `new_folders_judged`, `docs_judged` (an empty read fails) and `same_vertices` each refuse emptiness.
- The calls wrapper is proven live by every write's exact SaveAs count, so a refusal's "no watched call" cannot pass
  because nothing was counted.
- The exception: **`all(v == 2 for v in states.values())`** (lines 1974, 2029) passes on `{}`. A read of no components
  would pass "every component resolved" (S6).

## 2. The refusals section

**Each state is made as a person makes it.**

- Every one is made with the app's own calls or W9a's: `set_global` (opened as the app opens, set, rebuilt, saved
  by W8's `save_docs`, closed), `set_component`, `A.keyway`, `A.save_user`, `A.press`, Excel edits by `W.edit`, and
  `user_pair` by `build_pair`.
- The keyway geometry suits both parts: a Ø3 circle at (5, 0), spanning radius 3.5 to 6.5.
  - On Coupon_R's bore 8 (radius 4) it cuts.
  - On G1's fixture bore 8 it cuts, as in W9a's k3.
  - On G1 at bore 14 (radius 7) it lies inside the bore and goes into error.
- Offline, on W9's fixture with Printed on its Box, neither G4 on arcs nor G1 at bore 14 gives an assessment error (G4:
  only the warning that arcs stand in to 42.2 µm). So the planner reaches NEW_REVISION and CHANGES_ON_UPDATE, not
  WORKBOOK_ERROR.
- The unsaved marks clear on the person's save: the window's planning drops a mark saved since, in memory
  (`workbook_gui.py:725`). That holds both for FEATURE_IN_ERROR after the save and for userwork's written press.

**"Nothing was exported" is read, not assumed**, three ways:

- the Output folder's `print` folder before and after (no new press folder, every earlier one byte for byte);
- every SolidWorks file of the folders by sha256;
- for a refusal in the job, its result (nothing written, no folder) and its calls (no SaveAs, OpenDoc6, ActivateDoc3,
  CloseDoc, save or rebuild).

A planning refusal is held to *nothing submitted*. The NO_FOLDER case also checks the missing folder was not made.

**The sentences** are the app's own at the press. The script's 22 copies are held to `ui_text.print_refusal` in the
self-check, so a change of C's words fails there before a live run. The live status is the app's, compared exactly.

**G4's Flank on arcs names OutputGear alone**: very likely, as the author assumes.

- The Flank change is `swbuild.structural_change`'s for G4's spec alone.
- A mesh-level sentence names no part, and `workbook_print` names only parts in `changes`.
- The script checks `needs_new_revision` before the press. If the app named more parts the check would FAIL; it
  cannot pass falsely.
- One thing I could not run offline: the classify of a *built* printed 12 : 1 (no such record is in the fixtures).

**The suppressed component as a fact** is right.

- Both of the app's possible answers are judged whole: LIGHTWEIGHT's words held exactly (untrue, said so), or the set
  written and judged as any write.
- This is the one state here whose SolidWorks behaviour no earlier script read: `SetSuppression2(0)` on a gear-mated
  component in the active configuration. W8 suppressed components only in modes.
- A suppressed component's mates are suppressed with it and nothing rebuilds, so I expect no window. On 2026 a What's
  Wrong would end the run, so the coordinator should know this is the novel step.

**One false FAIL** (M1): `reducer_expect(..., features={"G1": ("User Keyway",)})` (line 2185) hard-codes the list line
*Your features left in it: User Keyway.* W9a's own check (`w9a_demonstration.py:1580-1587`) allows the inventory to list
the keyway's sketch too, "when SolidWorks keeps it top-level … either is right". If it does, the app's line is
*User Keyway Sketch and User Keyway* (or the reverse) and the check fails although the app is right. `userwork` already
takes the names from the record's inventory; do the same here (the `listed` names in G1's part, line 2180).

## 3. The userwork section

That the user's components and features are neither exported nor touched is read eight ways:

- the press folder holds exactly the five stems and the list (`written`), and no file named for Sprocket or Housing;
- every `.SLDPRT` and `.SLDASM` of the copy by size, mtime and sha256, the user's own part files among them, also named
  apart;
- every open document's title, flag and Visible, with RangeBox active (the user's components' parts are among the open
  documents);
- the job's calls: SaveAs ×5 and nothing that opens, activates, saves, suppresses or rebuilds;
- W9a's `users_in_copy` (the user's components present);
- every one of the eight user mates' entities, before and after, equal and complete;
- the User Keyway's code in Sun's part before and after, read without activation;
- the record file's sha256.

**That is enough** for what the job could do: it only reads and exports by object. Two things it does not read are
also out of the job's reach: the user's components' suppression states and positions. A gate the press would have to
pass first (Process typed, Update, save) is shown with its UNSAVED_MARK. Sun's size check skipped for the user's
feature and the list naming it come from the record's inventory, as ruled.

## 4. Safety with nobody at the keyboard

- **Calls.** Every SolidWorks call is the app's own or an earlier script's:
  - F2's probe: SaveAs, Visible, the walk, GetSaveFlag, CloseDoc on a part's window inside an assembly, `build_pair`;
  - W9a: lightweight 1 and 2, the keyway, k3's value Update into error and its save at `end_copy`;
  - W8: `save_docs`, Excel edits, `write_fixture`, `build_turning`, `copy_built`;
  - F1: the form's build.

  The one new *state* is §2's component suppressed in the active configuration. The job's own reads off a non-active
  part (`equations`, `feature_states`) are new to SolidWorks, and showing them is what the section is for.
- **The dialog watch and What's Wrong.** Every step runs in W9a's `run`, and each press's job in `watched_wait(…,
  app_job=True)`, so W9a's rule per version applies to every press. `--close-outlived-whats-wrong` enters W9c's own
  close path only when given; the note gives it on 2024 alone. The one expected What's Wrong is the bore Update on 2024
  (W9a's box-k3). The FEATURE_IN_ERROR read never activates G1 (`use_document`, `features_of` by `use_open_document`).
- **Memory.** W9a's 2 GB floor before each section; `userwork` stops under 6 GB before its copy and before its Update. On
  2024 `userwork` runs first in its own fresh session, the other four in a second.
- **Where it writes.** Only under `<out>`:
  - each section's `fresh_folder`, `user-parts` and `<out>\appdata`;
  - the reducer's master, built in `<out>\f2-reducer` and renamed by `keep_master`;
  - copies by `copy_built`, which only reads the master (also one given by `--printed-reducer-master`) and refuses an
    existing copy;
  - `--user-master` only copied, and its record opened read-only.

  The window's Output folder is the strip's (a copy's Box Output folder is blank, from `write_fixture`'s `spec("")`), and
  `window_press` stops its section if that folder is not under `<out>`. No user document title is logged
  (`label_of`), and no STEP header is.
- **DeskP.** Seven window methods run as themselves: `press_print`, `_submit`, `_collect_job`, `_finish_print`,
  `_worker_free`, `_foreign_record` and `_folder`. `_plan` is Desk9's `plan_solidworks`, the window's own pass inside
  `store.one_pass`. Four painting methods are stubbed (`_refresh_state`, `_refresh_read_line`, `_paint`, `_set_status`), and two
  are made to raise (`close`, `_settle_journal`). The strip is Desk9's stand-in with the snapshot, the folder and the
  Strand. I traced `press_print`, `_submit` and `_collect_job` at head: everything they read on the window is on DeskP,
  Desk9 or W8's Desk (`update_plan`, `state`, `link`, `_settled`, `reading.ok`, `reading.digest` …). The
  self-check's guard is weaker than the note says: it holds the window's reads to a *hand-written list*
  (`DESK_PROVIDES`, line 705; check at 1069), not to DeskP, which cannot be imported off Windows. It catches a new read
  in the window, not a name the list claims and DeskP lacks; the offline rehearsal covered the planning half only.
- **The press's status in the window** (S2): `window_press` reads `desk.note` after `press_print` (lines 1483-1510)
  without clearing it first. A press that returns at its first line (`_pending` set, or `reading` None after a failed
  re-read) would be judged on the previous press's words. Consecutive expected sentences differ throughout, so this
  shows as a FAIL, not a false clean. Still, set `desk.note = None` and `desk.said = []` before the press.

## 5. The self-check

Thirty-one lines, but most hold several failing ways each:

- the STEP reader ten faults;
- the documents eight changes;
- the calls six;
- the list nine;
- the findings eight;
- the gate eight states.

On that count it is no thinner than F1's 61. Not covered:

- **`refused` and `written` as wholes**: the in-job branch (a result that wrote nothing, its folder empty), the status
  comparison, the press folder's place. Each part is checked, the composition is not.
- **The machined list**: `MACHINED_SPAN`, `INTERNAL_SPAN` and *Process: Machined* (userwork's first press) are not held to
  `print_list_text` on a machined part. I checked them by hand against `ui_text._print_span_line` and `_print_process`;
  they agree.
- **DeskP itself**: see §4.
- **`rangebox_expect`** on a record shaped like setup.master's; the planner check uses W9's RangeBox record, a close
  stand-in.
- **The herringbone and suppressed paths** (facts).

Worth adding: one self-check line each for the machined list and for `refused`'s in-job branch.

## 6. The three app points

1. **The print list does not name a user's feature no record lists** (the form's keyway; also any window part's live
   find). §3.1.3 says the list gives "the user's features left in the part, by name". The job reads them
   (`swbuild._run_print_job`'s `live_user`) but `PrintResult` does not carry them, so C cannot word them.
   **Package B** adds them to the result (a field, or facts), and **package C** names them in the block.
2. **The form's NOT_A_PART never names the active assembly.** `gui._form_print_plan` (`gui.py:1386`) passes `""`
   whenever the snapshot is not a part, so `form_print`'s name branch is dead on the form. The sentence is true
   without the name. **Package C**: pass the snapshot's path, and the sidecar only for a part.
3. **LIGHTWEIGHT's words are untrue for a closed part while an unrelated assembly is open** (and for a suppressed
   component). Package B's inference (ruled, F2-REVIEW B3) is safe. The words are **package C's** to make true of every
   case it stands for, e.g. *with Pair_… open, OutputGear is not open in SolidWorks and may be a lightweight or
   suppressed component of it; open the part itself, or resolve it, then print again*. Reading the component states (B)
   is the larger fix and is not needed.

**Recommendation: all three before the run, in one small round.** Each is pure, and each is shown only in `refusals`. A
fix after the run means rerunning `refusals` on both versions, about 23 SolidWorks minutes and a fresh 2024 session.
The script's three expectations change with them:

- the keyway's list line becomes a check, not a NOTE (line 2101);
- `said_not_a_part(file)` takes the assembly's name;
- `said_lightweight` takes the new words.

Its self-check pairs change with them. If the coordinator would rather not delay, carry all three as caveats: none is
unsafe, and the script already says each as a fact or a NOTE.

## 7. Must-fix and should-fix

**Must-fix before the first run:**

- **M1.** `probe/f2_demonstration.py:2185`: G1's expected features hard-coded `("User Keyway",)`. If SolidWorks keeps the
  keyway's sketch top-level, the inventory lists it too (W9a allows either) and the list check FAILs falsely. Take
  them from the record's inventory, as `rangebox_expect` does.

**Should-fix:**

- **S1.** The self-check's DeskP guard holds a hand list, not DeskP (lines 705, 1069). Say so in the note, or check the
  list's names against `A.Desk9`/`W.Desk` attributes when the live part is importable.
- **S2.** `window_press` (lines 1483-1510): clear `desk.note` and `desk.said` before `press_print`.
- **S3.** §3.3's "after Update values, a second press makes a second folder": put Coupon_R's Face Width back by the
  form's own Update values (with its record loaded) instead of `set_global` (line 2089), then press. GLOBALS_DIFFER's
  sentence names that remedy.
- **S4.** In `userwork`, press once after Printed is typed and before the Update (line 2335 onward): CHANGES_ON_UPDATE
  naming the five parts, planning only. With it the plan's whole sequence (edited, refused, updated unsaved, refused,
  saved, written) is shown on one gearbox.
- **S5.** The herringbone's size reading (lines 1815-1823): give it a verdict, logged as a NOTE (*holds* or *does not
  hold* against d_a/2 and the face to 0.01 mm) and in the JSON. The run can then tell the coordinator whether
  `EXTENT_SKIPPED`'s "herringbone" may be lifted, which is what F2-PROBES-REVIEW asked.
- **S6.** Lines 1974, 2029: require the components read to be the assembly's own (the four gears' Name2s and the
  layout's), not merely all resolved.
- **Nit.** A clean *write* of a part open in its own window behind the user's is not pressed (probe review point 3 is
  shown through refusals only). Leaving G1's window open for the component-only press, or a clean press after
  GLOBALS_DIFFER on G1 is put back, would show it.

## 8. Command lines and order

As the note gives them (§*Command lines*), from a `git archive` snapshot with `--self-check` run on it first:

- **SolidWorks 2026**: one invocation in a session started for the run, sections `gates,form,workbook,refusals,userwork`
  in that order, `--user-master <probe folder>\w9a-final-sw2026-20261117-023433\out\setup.master`, no
  `--close-outlived-whats-wrong`. About 30 minutes. `userwork` runs last, so the 6 GB floor may end it on a grown
  session. If it does, rerun `userwork` alone in a fresh session.
- **SolidWorks 2024**: two invocations, each in a fresh session, both with `--close-outlived-whats-wrong`.
  - First `--sections userwork --user-master <probe folder>\w9a-confirm-sw2024-20261117-002313\out\setup.master`,
    with WSL idle.
  - Then `--sections gates,form,workbook,refusals`, with `workbook` before `refusals` so the printed 12 : 1 is built once.

  About 14 + 32 minutes.


## 9. Re-check of the round before the run (2e5f7f5, b3fe4a1; 888035a, 567773c, 5e45718)

Read at `b3fe4a1`. Nothing here should stop the run on SolidWorks 2026.

**The script.**

- **M1 is fixed at its cause.** G1's expected features (and Coupon_R's, and RangeBox's in `userwork`) are now the
  top-level features named *User…* that the script reads itself, without activation, which is what the job reads live.
  The keyway's sketch is therefore expected exactly when SolidWorks keeps it top-level.
- **Each should-fix is taken, and no check is looser.**
  - The list judge is stricter: a features line is now required to be absent where none is expected.
  - The DeskP guard now reads DeskP, Desk9 and W8's Desk from their sources, and is shown to fail without DeskP's body.
  - `window_press` clears the note and the said lines before each press.
  - Coupon_R is put back by the form's own Update values (`_finish_single` loads the record, so it is offered), then
    saved and written into a folder of its own.
  - `userwork` presses once after Printed is typed: CHANGES_ON_UPDATE naming the five parts, planning only.
  - The herringbone gets a verdict, as a NOTE and in the JSON.
  - `resolved_judged` requires the assembly's own components (the gears' Name2s and the layout), and fails on none
    read.
  - A clean write of G1 open behind the user's part is added (SaveAs ×4, nothing activated).
  - Its self-check covers the machined and ring lists, the herringbone verdict and the components judge.
- **Self-check: 35 checks, 0 failed.**

**The app.**

- **`live_features` (B).** It carries exactly the names `_user_features` already gave the size check, one entry per part
  holding any, through `with_list`. C names them for a written part, and falls back to the record's list for a part
  the job stopped before writing. True in both states.
- **NOT_A_PART names the active assembly (C).** The form now passes whatever is active and reads a record only for a
  part.
- **LIGHTWEIGHT's new words are true of all three cases B folds into it**: a lightweight or suppressed component, or a
  part simply closed while an assembly is open. Pinned with the plural and no-assembly forms.
- **The only test lines removed** are the two old LIGHTWEIGHT pins, replaced for that rewording, and one stand-in result
  given its `live_features`.
- **Nothing else in `src` moved** (gui 7, printout 6, swbuild 5, ui_text 31 lines).
- **Targeted tests:** `test_printout`, `test_swbuild_print`, `test_ui_text`, `test_print_form`, `test_print_window`,
  `test_printed_rule` and `test_findings`: 1193 passed.
