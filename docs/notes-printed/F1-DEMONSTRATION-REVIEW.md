# Review of F1's SolidWorks demonstration (probe/f1_demonstration.py) and the harness fix

*Independent, 2026-11-18, before the script's first run.*

- **Reviewed:**
  - \`probe/f1_demonstration.py\` and \`docs/notes-printed/F1-DEMONSTRATION.md\` at \`353d09f\` (\`64d8fc7\`, \`353d09f\`);
  - W8's harness fix \`e3705a1\` (\`probe/workbook_assembly_check.py\`);
  - \`e0a8d62\` (\`probe/w9d_demonstration.py\`).
- **Read beside them:**
  - W9a's harness (\`Desk9\`, \`press\`, \`run\`, \`save_user\`, \`section_stop\`, \`whats_wrong_rule\`, \`main\`);
  - W8's (\`Desk\`, \`copy_built\`, \`end_clean\`, \`quit_in\`, \`in_assembly\`, \`edit\`, \`w8_update\`);
  - W9c's \`close_outlived_on\`, \`small_pinion_check\`, \`gear_pairs_check\`;
  - \`swbuild._value_edits\` (K11);
  - \`ui_text._process_names_kept\` after \`47a7dcb\`, and \`WorkbookWindow._blank_process\` / \`_settled\` after \`f526dbf\`.
- **The pattern** is \`W9D-DEMONSTRATION-REVIEW.md\`'s first section. Three questions are asked of the script:
  - Could it report clean while the app is wrong?
  - Could it STOP or FAIL falsely?
  - What could end or spoil the run for the script's own reasons?
- **No SolidWorks, Excel or Windows Python was started.** Nothing was changed but this file.
- **Run in a clean \`git archive\` of \`353d09f\`** (scratchpad, deleted after). Every self-check ran 0 failed:
  - \`f1_demonstration\` (51 ok);
  - \`workbook_assembly_check\`;
  - \`w9b_demonstration\`, \`w9c_demonstration\` and \`w9d_demonstration\`;
  - \`w9c_probes\` and \`w9d_probes\`.

  \`w9a_demonstration\` has no self-check. Given \`--self-check\` it starts its \`main\`, which STOPs at once on Linux
  ("the app's Recent list would be written outside this run's folder") and writes nothing.
- **Every name the live part takes from W9a, W8, gear_pairs_check and small_pinion_check exists** (checked by name).
  So does every \`swcom\` member those two scripts' functions call: \`interference_count\`, \`_put_indexed\`,
  \`_out_long\`, \`_out_bool\`, \`_by_ref\`, \`_read\`, \`volume_mm3\`, \`open_document\`, \`begin_build\`.

## Verdict

**Fit for its first run on SolidWorks 2026. No must-fix.**

- Every Done-when item rests on a reading of its own, held to a figure the script works out itself or to W9a's reads
  of the user's work.
- The few places where a reading could pass on nothing are covered by a neighbouring check. Each is listed under S1,
  to be made explicit.
- The K11 risk the author names is real only if SolidWorks hands the IIF back in a form other than the depth IIF it
  has handed back unchanged on both versions since W4 (§1.4). If it does, two separate FAIL lines say so, with the
  text, before anything is written.
- The harness fix \`e3705a1\` is right. It changes W9's scripts only where intended.
- \`e0a8d62\` is right.

The should-fixes make the run's evidence tighter. None of them risks a file or the session.

## 1. The three things of the Done-when

### 1.1 One printed spur gear (\`spur\`)

The gear is built by the strip's own \`GearApp\`: its \`_derive_now\`, \`_gear_spec\`, \`_plan_single\` and
\`_finish_single\`. Only \`_build_gear\`'s submit is restated, and \`_build_gear\` (\`gui.py:1606\`) holds nothing else
that matters here: a folder check, \`_plan_*\`, the existing-file check and the submit. The form's real \`_start_link\`
is replaced, so no second driver attaches.

Each reading against its own expectation:

| What | Read from | Held to |
|---|---|---|
| name | the form's planned path | _P printed only; the file new |
| Backlash text | \`Session.equations\` (SolidWorks) | the script's pinned IIF or \`0.3 * "Module"\`, spaces aside |
| Backlash value | SolidWorks' \`Value(i)\` | \`backlash_wanted\`, worked in the script (not the app), to 1e-9; the app's derived figure the same |
| tooth | small_pinion_check's \`readings\` | its \`judge_part\`: no feature in error, one body, volume within 0.1 % of the outline, 4 tip corners a tooth on the outer radius |
| printed vs machined | the two volumes | each within 0.1 % of its own outline and not of the other's (1.29 % apart at m1.5); equal to 1e-6 at m0.8 |
| record | the \`.gear.json\` the form's finish wrote | printed: sidecar 3, process, 0.4 nozzle, IIF; machined: sidecar 1, W9's eighteen keys, no nozzle |

**Could it pass with the app wrong? No.**
- A printed gear built machined fails three ways: the name, the Backlash text and value, and the volume against its
  own outline at m1.5.
- A wrong IIF fails the text check.
- A right IIF with a wrong SolidWorks evaluation fails the value check.

The m0.8 pair proves only that the two geometries are one. The equation text is what distinguishes them, and the
Backlash line reads it. The note says so.

### 1.2 One printed pair (\`pair\`)

The pair is the form's (25 / 50, module 1.5, Motion set to gear mate). It is built by \`_plan_pair\` and \`build_pair\`,
and driven by gear_pairs_check's own \`drive\`:
- gear A turns 30°, gear B −0.5 of it, to 1e-6;
- no interference at 10° or at 40°;
- gear A not fixed.

The pair section also checks:
- each part's Backlash and \`.gear.json\`;
- the three _P names.

A pair that does not build fails \`built\` and returns before the drive. The section's last line needs both cases
clean. Nothing passes on nothing.

The mesh's play is not measured, and the note says so. "Turns as a machined pair does" is the same judgement passed
by both, which is what §2.8 asks.

### 1.3 RangeBox: the gearbox before F1, Printed typed, one Update (\`rangebox\`)

**Before the copy.** The master's own record is read from its file (\`raw_record\`, read-only). The section stops
unless that record is below link 11 and no part says a process. I checked the keys against W9's record (\`parts\`,
\`spec\`, \`link_schema_version\`): they are right. On the masters the note names, the record is at 7.

**Opened as built:**
- *the Process:* \`as_built_judged\`. The read is blank with no row, it resolves machined, no job is printed or named
  _P, Update has nothing to do, and \`record_matches\`. A missing plan fails.
- *the footer:* W9's prefix, and none of *Process*, *printed*, *Printed* or *_P*.
- *the Workbook panel's line:* the pinned *(add a row labelled Process)* line.
- *the files:* size, mtime and sha256 of every \`.SLDPRT\`, \`.SLDASM\`, \`.xlsx\` and \`.json\` of the copy, before and
  after the read and planning. The copy is flat: W9a puts Sprocket and Housing beside the gears, so the top-level
  listing is the whole copy.

**Printed typed.** Excel types a row labelled Process (\`Box!A10\`, \`B10\`), as a person following the line would.
Then:
- the Box reads \`printed\` at \`Box!B10\` with no error;
- the line reads *Printed, 0.4 mm nozzle*;
- \`backlash_only_judged\` holds: every expected part changes in \`Backlash\` alone, from the machined rule to the IIF,
  with no structural change, new revision or in-place change, and each file keeps its name;
- the footer before the press begins with B's sentence;
- \`ahead_of\` foresees nothing stopping the press.

**The press**, by W9a's \`press\`, which first asserts that the footer offers it:
- *the result:* each of the five parts' own \`UpdateResult.changed == ['Backlash']\`, and nothing in the layout or the
  carriers. All five GearboxUpdate fields the "nothing made new" check reads (\`built\`, \`inserted\`, \`deleted\`,
  \`bands_added\`, \`modes_added\`) exist, so that check is not vacuous.
- *the carry:* what was carried is what the footer foresaw.
- *the puts:* every put is an app body or a locked sprocket, else a STOP.
- *the user's work:* nothing of the user's in error.
- *the files:* no \`.SLDPRT\` or \`.SLDASM\` changed on disk.
- *the sentence:* C's sentence said exactly once, without the stale clause. The live path gives the sentence the
  record taken at the press: Desk9 runs the window's own \`_finish_update\` with \`job.record\` (\`w9a_demonstration.py:603\`),
  as \`47a7dcb\` needs. So the sentence is said on this press, as the self-check's \`rec1\` case shows.

**Read back:**
- every part's Backlash read from SolidWorks as the IIF, evaluating to 0.3;
- the record read from disk: link 11, the same five paths, each part printed with the IIF, each \`.gear.json\` at 3;
- the user's work by W9a's own reads: every user mate's entities equal before and after, \`go_judge\` in every mode,
  the User Keyway at code 0, the user's components in the copy.

**The second press:**
- saved and closed as the user would (\`save_user\`, \`quit_in\`), planned quiet, and pressed;
- it changes nothing, places nothing, says \`ui_text.ALREADY_MATCHES\` without the names sentence, and passes W8's
  \`check_quiet_update\`;
- the record on disk then holds no unsaved or mismatched document. W9c's \`fixed\` section makes the same check after
  its second press and passed live (\`w9c_demonstration.py:2360\`).

**Could it report clean with the app wrong?** I found no way.
- A part not written fails the live Backlash read, independently of the result.
- A part written but not recorded fails \`record_judged\`.
- A user item moved or put in error fails W9a's reads.
- A file saved by the app fails the snapshot.
- A sentence said twice or missing fails.

Three readings could pass on an empty set. Each is covered by a neighbour, but none says its own count:
- \`judged_live_backlash\` (\`:911\`) loops over whatever \`desk.record.current_parts()\` holds; \`record_judged\` would
  catch an empty record;
- \`as_built_judged\` (\`:967\`) passes on no jobs at all; the footer and \`W.turning\` checks beside it would not;
- \`entities_after == entities_before\` (\`:1084\`) holds for two empty maps; the check that all eight user mates are
  set up (\`flags_set\`) precedes it.

See S1.

### 1.4 The second press and K11: is the comparison robust?

**What is compared.** K11 (\`swbuild._value_edits\`, \`:5424\`) splits each live equation with \`split_equation\`. It
calls a global the user's edit only when its text differs, with whitespace removed (\`_squash\`), from both the record
and the workbook's planned text. Quotes and letter case are kept.

**What SolidWorks hands back, as measured:**
- *On 2026:* W9b's committed JSON (\`probe/results/w9b-demo-20261117-*.json\`) holds \`Session.equations\` read from
  SolidWorks: \`"Tooth Depth"= IIF ( "Module" <= 1.25 , "Module" * 2.4 , "Module" * 2.25 )\` and
  \`"Backlash"= 0.3 * "Module"\`. That is exactly the app's typed text: same quotes, same case, same \`<=\`, same spacing,
  no units added.
- *On 2024:*
  - P1 accepted the same IIF shapes, \`<=\` among them (\`sw2024/probe-results-20261102-*.txt\`).
  - Every Update since W4 compares every planned global's text, the depth IIF included, by the same squash:
    \`planned_changes\`, \`_held_unit\`, and since W9a K11.
  - W9a's 2024 confirming run (go, reducer, nocarrier: 0 failed) and its quiet presses refused nothing. If 2024
    rewrote the IIF, the depth global would have read as the user's edit in every one of them.

**The printed IIF has the depth IIF's shape:** the same \`IIF ( "Module" <= n , … , … )\`, unit-less literals and the
same spacing. It is written by the same \`set_global_variable\` path, and read back by the same \`Equation(i)\`.

So the comparison is robust, from what is measured. The one difference, an integer bound (\`1\`) where the depth
writes \`1.25\`, is a literal SolidWorks has never been seen to reformat.

**If SolidWorks did store it otherwise, the run says so twice, and writes nothing more:**
1. \`judged_live_backlash\`, after the first press, fails each part's line with the text SolidWorks holds.
2. The second press is refused by K11 before any write. \`press\` returns None, and the line fails with K11's sentence.
   \`check_quiet_update\` is then skipped, and the copy is ended as usual.

Nothing is lost but that line. The script's own text check uses the same squash as K11, so the two cannot disagree.

## 2. The harness fix \`e3705a1\`, and \`e0a8d62\`

**\`e3705a1\` is right.**
- W8's \`Desk._after_read\` was the harness's only user-facing \`assess\` call (\`workbook_assembly_check.py:1103\`). It
  now passes \`blank_process=self._blank_process()\`.
- \`_blank_process\` and \`_settled\` are the window's own functions, bound on the Desk. What they read the Desk has:
  - \`self.link.path\`;
  - \`process_record\`, initialised in \`Desk.__init__\`;
  - \`workbook_gui._VERDICTS\`, empty in the harness.
- \`Desk9\`, and through it W9b's, W9c's and W9d's desks, inherit it. None overrides \`_after_read\`.
- It writes nothing:
  - \`store.read_link_record\` moves nothing;
  - \`_settled\` settles the owner in memory only;
  - the record is read once more per read.

**What it changes, case by case, against assess's default before it:**

| The record beside the workbook | Before (blank read) | After |
|---|---|---|
| current parts, all built machined (every W9 master: setup, rangebox, reducer, fixed-updated) | printed, every part changed | **machined, nothing changed**, as W9 read it |
| a part built printed | printed | printed |
| none, no parts, newer or unreadable | printed | printed (\`process_record\` set for the last two) |
| another workbook's, or owner UNSURE (no answer in \`_VERDICTS\`) | printed | printed |
| any typed Process | as typed | as typed |

Only the first row moves, and that is the intent.
- The UNSURE row cannot be met in these scripts. \`copy_built\` requires the copy's record to be OURS
  (\`:4227-4240\`), and no probe script renames a workbook: the only renames are of folders, before \`copy_built\`.
- Fixtures the harness writes (\`write_fixture\`, \`to_sheets\`) say \`machined\` on their Box and never reach the blank.
- No probe script uses \`model.template\`.

**One thing that changes in a W9-era script by F1 itself, not by this fix.** \`probe/workbook_window_check.py\` (and
\`workbook_assembly_check\`'s Excel-saved fixtures through \`FIXTURE_DIR\`) build from the committed
\`tests/fixtures/excel-windows\` workbooks. Those have no Process row and no record, so they now read Printed and build
_P parts. That is D2's answer for a new gearbox, and the fix neither causes nor changes it. A W4–W8 section re-run
after F1 would meet it, and should be said so in its note if one is ever run again.

**\`e0a8d62\` is right.**
- Both places now hold the record on disk to \`store.LINK_SCHEMA_VERSION\`: the run's \`record_judged\` and the
  self-check. Each has a comment that it was 10 when W9d ran.
- That is W9c's practice already.
- It still fails on any record written at another schema. It no longer pins the number itself, which
  \`test_printed_rule\` and \`test_store\` do.
- No other probe script holds a link-schema literal. The sidecar literals in W9b and W9c (1 and 2) are machined
  sleeves', which F1 leaves as they were.

## 3. Safety with nobody at the keyboard

**Calls no committed script has made on the version run.**
- *On 2026:* none. The builds are \`swbuild.build\` and \`build_pair\`, and the Update \`update_gearbox\`. The reads are
  W9a's, W9b's \`Session.equations\`, small_pinion_check's \`readings\` (\`small-pinion-2026-20261114-184220.log\`) and
  gear_pairs_check's \`drive\`.
- *On 2024:* \`readings\` brings \`IBody2.GetVertices\` and \`IVertex.GetPoint\` for the first time.
  - The rest of \`readings\` has run on 2024: \`GetErrorCode2\` per feature (W9a's \`feature_list\`), \`GetBodies2\`,
    the volume and the Equation Manager's \`Status\`.
  - Both new calls are read-only on a part the run built, inside \`run\` and so under the watch.
  - \`drive\` has its 2024 log (\`sw2024/gear-pairs-20261113-184641.log\`).
- *The note's "none new to the repo"* is right with that qualification, which it already makes.

**Dialogs.**
- *Tk:* the strip's \`GearApp\` holds no \`messagebox\`. Its \`filedialog\` calls are behind buttons the script never
  presses, and the root is withdrawn. No \`mainloop\` runs, so its \`after\` timers (\`_fit_page\`, \`_tick\`) never fire,
  and \`_tick\` would have no worker anyway. Tk under python.exe is proven by \`workbook_window_check\`'s window runs.
- *Closes:* every close is \`QuitDoc\` (\`quit_in\`), which closes modified parts and assemblies with no dialog on both
  versions (\`W9C-RUNS-REVIEW.md\`:1126). That includes the pair's driven assembly. gear_pairs_check's own 2024 modal
  came from \`CloseDoc\`, which this script does not use.
- *Version mixing:* nothing is opened that another version saved. Each version is given its own master, as W9c's and
  W9d's runs were.
- *Lightweight saves:* no assembly with a lightweight component is saved. setup.master's components are resolved, and
  \`save_user\` is W9a's own, run on the same master.

**Writes.**
- The masters are read (the record by \`open\`) and copied, never opened in SolidWorks or Excel.
- The spur and pair parts go into fresh folders under \`<out>\`.
- The Recent list goes into \`<out>\\appdata\` (W9a refuses to start otherwise).
- Excel is the run's own, on the copy's workbook, and is closed by \`end_copy\`.
- \`snapshot\` only reads.

**Hangs.** Every SolidWorks job goes through \`run\` with a timeout:
- 900 s for a part;
- 1800 s for a pair;
- 600 s for a read or a drive;
- 2400 s for the Update, in \`Desk9\`.

**What's Wrong and the close flag** are wired as W9c wires them:
- \`main\` imports \`w9c_demonstration\` and calls \`close_outlived_on()\` only when \`--close-outlived-whats-wrong\` is
  given. W9d's \`close_path_asked\` is the same switch.
- The rule itself is W9a's \`whats_wrong_rule\`, which reads the year's finding.
- Importing W9c touches none of \`A.SECTIONS\`, \`A.CHOSEN\` or \`A.done_here\`, which \`main\` set first. It adds
  \`AddComponent5\` to W8's traced writes, as W9c's and W9d's runs have it.

**The 6 GB floor before the 2024 press** (\`:1032\`) is sensible. W9c measured the first 2024 press on a freshly opened
RangeBox at 3.3 to 4 GB. With W9a's 2 GB floor that comes to 5.3 to 6 GB.

Two things about it on this laptop:
- **The figure is Windows' free memory, and WSL2's VM counts as used there.** Other agents running the test suite in
  WSL while the 2024 rangebox runs could push it under 6 GB. That would be a false section STOP: safe, but the
  section is lost. Keep WSL idle for that run.
- **The check comes after the copy, the open, every read and Excel's edit** (about ten minutes on 2024). A copy of it
  before \`copy_built\` (\`:939\`) would stop the section before it has spent anything (S2).

## 4. The self-check

The self-check runs every plain judgement on the app's own figures and on W9's own record of RangeBox, and fails each
in its main ways. What it does not hold:

- **The live wiring after \`if SELF_CHECK:\`**, as in every demonstration. A Linux import with pywin32 stood in
  found every name; I confirmed the names separately.
- **Branches of the judgements not failed on their own:**
  - \`as_built_judged\` with only the Update busy (its one failing Update case also has Printed typed);
  - \`backlash_only_judged\` with a part planned machined or renamed _P;
  - \`record_judged\` with a \`.gear.json\` missing;
  - \`sidecar_judged\` with a printed record lacking its nozzle;
  - \`master_before_f1\` on any record (W9's fixture, at link 10 with no process, would do).
- **The second press's judgement** (\`:1108\`), which is inline. Its parts are W8's and W9a's, run live before.

None of these would let the run pass wrongly. Each is a branch a careless edit could break unseen (S3).

## 5. Command lines, masters and order

The masters are right for each version. Both are the ones W9c's and W9d's runs copied (\`W9D-DEMONSTRATION.md\`:534,
:536). The 2026 master does not open in 2024.

The order is right:
- **2026:** \`spur\`, \`pair\` and \`rangebox\` in one invocation. The builds come first and are cheap.
- **2024:** \`rangebox\` first, in a fresh session, with the close flag, as W9c's 2024 confirm ran. Then \`spur\` and
  \`pair\` in a second invocation into the same \`out\`. W9a's \`done_here\` skips sections already in \`out\`, and each
  invocation has its own log and JSON.

The note's lines use \`RUN\\\` placeholders, as W9c's and W9d's notes do. Written out for this laptop, with \`<probe
folder>\` as F1-DEMONSTRATION.md defines it and \`<commit>\` the commit to run (\`353d09f\` or later):

\`\`\`
# from WSL: the snapshot (one per version), as every W9 run
RUN=/mnt/c/<probe folder as a WSL path>/f1-demo-sw2026-<stamp>
mkdir -p $RUN/snap $RUN/out
git -C /home/m0obot/SW-Gear-Generater-printed archive <commit> | tar -x -C $RUN/snap
echo <commit> > $RUN/snap/SNAPSHOT_COMMIT
\`\`\`

\`\`\`
rem SolidWorks 2026, a session started for the run, nothing of the user's open
python.exe <probe folder>\f1-demo-sw2026-<stamp>\snap\probe\f1_demonstration.py ^
    <probe folder>\f1-demo-sw2026-<stamp>\snap\src <probe folder>\f1-demo-sw2026-<stamp>\out ^
    --pid PID --log <probe folder>\f1-demo-sw2026-<stamp>\f1-demo-sw2026-1.log --sections spur,pair,rangebox ^
    --user-master <probe folder>\w9a-final-sw2026-20261117-023433\out\setup.master

rem SolidWorks 2024, a fresh session; WSL idle
python.exe <probe folder>\f1-demo-sw2024-<stamp>\snap\probe\f1_demonstration.py ^
    <probe folder>\f1-demo-sw2024-<stamp>\snap\src <probe folder>\f1-demo-sw2024-<stamp>\out ^
    --pid PID --log <probe folder>\f1-demo-sw2024-<stamp>\f1-demo-sw2024-1.log --sections rangebox ^
    --close-outlived-whats-wrong ^
    --user-master <probe folder>\w9a-confirm-sw2024-20261117-002313\out\setup.master
python.exe <probe folder>\f1-demo-sw2024-<stamp>\snap\probe\f1_demonstration.py ^
    <probe folder>\f1-demo-sw2024-<stamp>\snap\src <probe folder>\f1-demo-sw2024-<stamp>\out ^
    --pid PID --log <probe folder>\f1-demo-sw2024-<stamp>\f1-demo-sw2024-2.log --sections spur,pair
\`\`\`

Run \`python probe/f1_demonstration.py --self-check\` on the snapshot first, with \`PYTHONPATH=src\`. It ran 51 ok,
0 failed at \`353d09f\`.

## Summary

**Must-fix before the first run: none.**

**Should-fix (none blocking):**
- **S1** \`probe/f1_demonstration.py\` (\`:911\`, \`:967\`, \`:1084\`): let no reading pass on nothing.
  - \`judged_live_backlash\` holds the part count to five;
  - the as-built check holds its jobs to the record's gears;
  - the entities check requires the eight user mates on both sides.
- **S2** \`:939\` / \`:1032\`: take \`PRESS_FREE_GB\` before \`copy_built\` as well as before the press, so 2024 stops
  early rather than after ten minutes. Run the 2024 \`rangebox\` with WSL idle.
- **S3** the self-check: fail each judgement branch it does not yet fail on its own (§4). Hold \`master_before_f1\` to
  W9's fixture record.
- **S4** \`F1-DEMONSTRATION.md\`: say that the Excel-saved fixtures (\`workbook_window_check\`, W8's \`FIXTURE_DIR\`) now
  read Printed under D2, so a W4–W8 section re-run after F1 builds _P parts (§2). This is a note, not a fix.
