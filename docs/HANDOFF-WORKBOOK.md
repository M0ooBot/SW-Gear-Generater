# Handoff: the workbook import (branch `workbook`)

Rewritten the night of 2026-11-13, when work on the Windows host was wound down so it can carry on from
another machine. **`docs/PLAN-WORKBOOK.md` is the plan and the authority**; this note only says where things
stand within it. The working papers of the session (plans, reviews, reports) are in `docs/notes-workbook/`
and are named below where they matter. Where one of them names a script such as `w4x_….py` or `w5r_….py`,
that was a throwaway repro in a temp folder and was not kept; the fixes' regression tests replace them.

**Updated 2026-11-14**, on the Windows host again (a WSL clone, with SolidWorks 2026 and 2024 both started and
exited by the agents): W4 was closed and W5 begun. The dated paragraphs below say what changed; the user's
answers of that day and the rulings that follow from them are in `notes-workbook/W5-DECISIONS.md`.

## Where it stands

| Phase | State |
|---|---|
| W0–W1 xlsx read/write, model, schema | done, reviewed, review fixes in |
| W2 Workbook window, live link, Build parts | done, reviewed, fixes in. The batch build (`swbuild.build_many`) ran on SolidWorks 2024 and 2026 (`208712c`); logs `probe/results/w2-build-20261113-164647.log` and `probe/results/sw2024/w2-build-20261113-165706.log`. |
| W3 geometry, phases, kinematics, checks, fixes, Export, Results sheet, two-column window | done, reviewed twice, every item fixed. The Excel checks passed on Windows: the Windows-saved fixture (`aa86cc7`) reads, and exported files open in Excel with no repair prompt. |
| W4 layout part + static assembly, Update SolidWorks, build-again `_r<n>` | **closed 2026-11-14**: the rebuild fault probed and fixed, pass 4 verified, both demonstrations rerun on SolidWorks 2026 and 2024 with every check passing, each step reviewed. Details and what is left open below. |
| W5 motion | **closed 2026-11-14**: probes P0 to P0d and the two ring rounds run and reviewed, packages A to E written and reviewed, the demonstration run in full on SolidWorks 2026 and confirmed on 2024, the user's hand drag passed on both. Details, and what is left open, below. |
| W6 right-angle | **in progress (2026-11-14)**: the plan written, reviewed and revised (`notes-workbook/W6-PLAN.md`, `W6-PLAN-REVIEW.md`); probe tier 9 run on SolidWorks 2026 on cylinders and reviewed (a turned gear mate's sense is read per entity); the interface commit `34bfb85` with its rulings (`W6-INTERFACES.md` §7); packages A, B, C and D written and each reviewed, on the fake. **Left:** the demonstration on SolidWorks 2026 (package E), the confirming run on 2024, and the close. Details below. |
| W7 planetary | planned: `W7-PLAN.md`, reviewed (`W7-PLAN-REVIEW.md`) and revised; its riskiest point measured on SolidWorks 2026 (`W7-SPIKE.md`: a gear mate on a carrier-borne axis turns in the carrier's frame, and the plan's mates turn the 4 : 1 right). No code yet; it starts when W6 closes. |
| W8 sleeves and modes | planned: `W8-PLAN.md`, reviewed (`W8-PLAN-REVIEW.md`) and revised; a spike on SolidWorks 2026 (`W8-SPIKE.md`: the collinear 1 : 1 gear mate and per-configuration suppression work; component handles go stale after a configuration is added or shown; the per-mode slide link as planned fails). The plan is to be revised to the spike. No code yet. |
| How the user's absence is handled | the user said on 2026-11-14 to carry on, in order, until W8 is done. Judgement calls are taken at each plan's recommended reading and listed for the user as readings to overrule. |
| The small-pinion tip cap | `fix/small-pinion-cap` merged at `0f5a121` (the user's instruction): 6- and 7-tooth pinions build with an arc on the tip cap, version 0.3.2. Built on SolidWorks 2024 by the branch; the 2026 build and the merge's review are in hand. |

Suite, measured on a clean `git archive` of `2250ceb` (WSL, 2026-11-13): `PYTHONPATH=src .venv/bin/python -m
pytest -q` → **1559 passed, 10 skipped**. On the 2026-11-14 clone (another Python, fewer skips): 1699 passed, 1
skipped at `8504856`, where W4 closed; 1759 passed, 1 skipped at the W5 interface commit `07fd66a`; 2096 passed, 1 skipped at `c7770c8`, after D's review and B's
and C's fixes (2026-11-14); **2258 passed, 1 skipped** on a clean archive of `4cd8e7f`, where W5 closed (source as
`d99654a`).
The window's Tk tests run under Windows Python: `python.exe -m pytest tests/test_workbook_build.py
tests/test_workbook_window.py -q` → 115 passed, 2 skipped at `c7770c8` (a "no display for Tk" skip is a known flake that moves between tests;
rerun). The `PYTHONPATH` matters in a copy: the
venv's editable install otherwise imports the working tree's `src`, uncommitted edits and all.

## W4 in detail

**What exists.** Probe tier 7 passed on SolidWorks 2026 (a full run, `probe/results/latest.json` at the time)
and 2024 (`probe/results/sw2024/`), every decision the same; findings set in `bfc9ef5`. Then the interfaces
(`a93d6d9`), the record's schema 2 (`1f0548b`), the planning (`cb7e042` layout, `17f4bce` gearbox, `a623610`
update), the worker (`afb0c00`, `7ce7a26`, `d0203cd`), the footer and every sentence (`4b128a6`, `8fa0216`),
the window (`ccef692`), boards and docs (`b215dee`, `649d8db`, `47e4648`); the helical phase across Z+/Z−
was fixed first (`119da25`), and the ring pair's gear-mate Flip in `4c8a73a`.

**Demonstrated before the reviews** (`5154de1` and before): SolidWorks 2026 — all of it, 244 checks, 0
failed (`probe/results/w4-workbook-assembly-20261113-194228.log`, `…-200255-a2.log`,
`w4-window-20261113-195843.log`); SolidWorks 2024 — tier 7, the 12 : 1 build, its measurements and
controls, the Excel edit and Update only (`probe/results/sw2024/w4-workbook-assembly-20261113-200555.log`).
The user's 2024 session ran out of memory then; they have restarted it since.

**Reviews and fixes.** Three independent reviews, four fix passes:

- review 1 → pass 1, worker, planning and record (`042f276`, `9c64960`, `88385f1`, `a6abd5d`, `2b752a1`),
  and pass 2, the window, every sentence and the docs (`a8bb817`, `7dc0d90`, `571cf1a`, `2a4653e`,
  `94c85d7`, `01b889e`). Rulings: `notes-workbook/W4-DECISIONS.md`, `W4-REVIEW-RULINGS.md`.
- review 2 (N1–N6) → pass 3 (`45173e0`, `a9d20ab`, `707bfcb`, `7de851a`, `d5eecb2`, `fb3bbdc`, `ae1d208`,
  `d2cd2d6`, `d37ae52`): a part's own name claimed before any suffix; the held-values check compares
  evaluated values; every COM action through `swcom._guarded`; whose a record is, by the file, and asked
  once when its workbook is gone; marks a job can prove cleared; a build's journal; close anyway / quit
  anyway; the demonstration's new section a3. Report: `notes-workbook/W4-REPORT-FIX3.md`.
- review 3 (`notes-workbook/W4-REVIEW-3.md`: the 200-document cap that could clear an unsaved mark, a file
  id of 0 making two workbooks one, the journal wiped by any refused job, a false sentence after "No") →
  pass 4 (`f335379`, `2250ceb`). Report: `notes-workbook/W4-REPORT-FIX4.md`. **Pass 4 has not been verified
  by a reviewer**, and it was wound down early: its code and tests are complete and green, but four boards'
  `.dc.html` were regenerated without redrawing their PNGs in `design/renders/` (`WorkbookCloseAnyway`,
  `WorkbookMoved`, `WorkbookUnsaved`, `WorkbookUpdated`).

**The rerun on SolidWorks 2026** (code at `9aeed80`, that is pass 3 without pass 4; logs in `8b1ef15`;
report `notes-workbook/W4-RERUN-2026.md`): **292 checks passed, 3 failed, all three from one fault in the
app.** After an Update, SolidWorks marks every part modified, including parts Update never changed, because
the app rebuilds an assembly with `ForceRebuild3(False)` (`swcom.py`: `rebuild()` and the re-place of a
component), which rebuilds every component. So SolidWorks would ask to save parts nothing changed, parts
shared with earlier revisions among them. A repro on a saved assembly showed `ForceRebuild3(True)` and
`EditRebuild3` marking the assembly only. The fake SolidWorks does not model this. What only SolidWorks
could confirm did hold: `QuitDoc` closed modified documents without a dialog, `documents()` listed every
document in memory, and the value comparison never disagreed falsely. Journal reuse and the marks clearing
(section a3) passed.

**Open for W4, in order:**

1. **The rebuild fault.** Probe first (the house rule): which assembly rebuild still shows a put's new
   frame, the layout's moved axes and a changed part, while leaving unchanged components unmodified. Nothing
   of this probe is written; `notes-workbook/W4-REBUILD-PROBE-TODO.md` says exactly what to build and run
   (a new tier-7 item, on 2026 and 2024). Then change the two rebuild sites, teach the fake that a full
   rebuild marks every component modified, and add the regression test.

   *2026-11-14: done as far as code goes.* The probe is `assembly_rebuild_scope` (`e79e863`, `6d0b1bb`); it
   passed in a full run on 2026, now 34.1.1 (76 of 76, `latest.json`), and alone on 2024 (27 of 27,
   `sw2024/probe-results-20261114-014813`), every decision the same (`9b9f546`): every route, even no rebuild,
   showed the put, the layout move and the changed part; `ForceRebuild3(True)` marked only what changed and
   returned False on a failed component; `ForceRebuild3(False)` marked every component. Findings in `e57aca7`
   (`ASSEMBLY_REBUILD_ROUTE` and the rest). The fix is `9c39fb8`, narrowed after its review: `swcom.rebuild_call`
   is the one place that decides, and the CALLER says which of three kinds of assembly it is, refused with a
   sentence when it does not. A part rebuilds as always. STATIC (fixed components: today's workbook gearbox)
   takes `ASSEMBLY_REBUILD_ROUTE`, top-only, which it requires: unsettled, a build or Update refuses before
   changing anything. TRAIN (W5's mated workbook gearbox, any plan with a `Mate` op built outside `build_pair`;
   nothing builds one yet) takes `MATED_ASSEMBLY_REBUILD_ROUTE`, full while None (set to the top-only route by W5's probes in
   `8504856`; `notes-workbook/W5-DECISIONS.md` says what that does and does not yet cover). PAIR (everything `build_pair`
   makes, and the p5 half-pitch controls) keeps the full `ForceRebuild3(False)` probe tiers 4 and 5 ran, whatever
   the train's finding says, since that is measured on other mates; an absent `PAIR_ASSEMBLY_REBUILD_ROUTE` is
   where a later pair probe could change it. The probe tried no mate and no assembly equation. The fake
   marks what the probe saw for the static route (a full rebuild marks every component, top-only the
   assembly, a put nothing; the reads after a put or a build mark the assembly, which the fake pins on the interference check though the probe did not isolate it); it models nothing unprobed.
   Since the review of `31d1ac9` an assembly's kind must always be said, and a pair's gate is back before its
   gears. **What the SolidWorks rerun (step 3) must still confirm:** the three checks the 2026 rerun failed
   now pass under the demonstration's corrected invariant (marked modified = `GearboxUpdate.changed` ∪ the
   assembly when Update rebuilt it or ran the interference check: `changed` keeps meaning content changed);
   the new part-only Update step in b; after a fresh build no part or layout part reads `GetSaveFlag` True and
   the assembly does (the reads after its save mark it — frame reads and/or the interference check, not yet
   isolated: the rerun logs the flags after each as fact lines, and an extra probe step is to settle it — with
   nothing to lose by not saving it); a document just opened from its file reads False. Still unprobed for
   the static route, and shown only by that rerun: a put
   and its top-only rebuild under `set_rebuild_suppressed(True)` (Update places with `CommandInProgress` on); an
   assembly BUILT with the top-only route; whether the assembly still reports needing a rebuild after the
   route; and a part opened alone by path reading `GetSaveFlag` False.
2. **A brief independent verification of pass 4** (`git diff 8b1ef15..f335379`).

   *2026-11-14: verified* (`notes-workbook/W4-REVIEW-PASS4.md`). It found one fault outside the diff, of the
   same kind as review 3's item 2: Export as… could write over another file on a volume whose file ids are all
   0. Fixed in `8bd2530`.
3. **Rerun both demonstration scripts** (`probe/workbook_assembly_check.py`,
   `probe/workbook_window_check.py`) on SolidWorks 2026, and on 2024 in a fresh session — there, for the
   first time, the structural step and `_r2`, a2, a3, b, c and the window run. Commit the logs. The 2026
   rerun went through a launcher that lets the app see only one SolidWorks process, because
   `swcom.find_candidates` asks every running SolidWorks for its version and the user's 2024 was running;
   that launcher was a scratch file on the host and has to be written again (`W4-RERUN-2026.md`, "How it
   ran"). Pass 4 added one expectation a rerun must confirm: a document just opened from its file reads
   `GetSaveFlag` False.

   *2026-11-14: rerun done, every check passed on both versions*, from a `git archive` snapshot of `9ac36c5`
   (the app as of `388c8d3`, with `findings.py` as of `8504856`, whose new values only the train kind reads and
   W4 never builds; `cross_version_open_check.py` as committed with these logs), one SolidWorks at a time, each started for the run and exited
   after it (no launcher needed). `workbook_assembly_check.py`: 322 of 322 on 2026 (34.1.1,
   `probe/results/w4-workbook-assembly-20261114-053855.log`) and 322 of 322 on 2024 (32.5.0, all five sections
   for the first time, `sw2024/w4-workbook-assembly-20261114-055924.log`), exit 0 both. `workbook_window_check.py`:
   10 of 10 on each (`w4-window-20261114-055011.log`, `sw2024/w4-window-20261114-061023.log`).
   `gear_pairs_check.py` on 2026: spur, ring, crown and internal all ok, as before the three kinds
   (`gear-pairs-20261114-055230.log`). The three checks the 2026 rerun failed now pass; after a build no part
   or layout part is marked and the assembly is; the part-only Update in b marks G2's part and the rebuilt
   assembly, the record the part alone; every document reads `GetSaveFlag` False straight after a reopen. The
   new fact lines isolate what marks the assembly: the frame reads leave every flag False, `interferences()`
   marks the assembly (six reopens on each version). A gearbox saved by 2024 and opened in 2026
   (`probe/cross_version_open_check.py`, `w4-cross-version-2024-in-2026-*.log`): every document reads False
   straight after the open and no file changes; but `QuitDoc` on each such assembly raised a modal "SOLIDWORKS
   CAM Warning: Save changes to <assembly>?" from the CAM add-in. The flag was read only straight after the
   open, not again before the close, so what it read when the prompt came up is not known. The agent running
   the script dismissed each prompt from outside it: a separate Python helper found the dialog's "&No" button
   and posted it `BM_CLICK`; nothing was saved and the files compared equal afterwards. The logs have no trace
   of the dialog (that script has no dialog watcher), and the commit message of `64f4620` calls this "answered
   No by hand". A 2026-made assembly closed by `QuitDoc` in a3 raised none. The app never closes a document,
   so it cannot meet this prompt; a person closing a 2024-saved gearbox in 2026 will. The first 2026 attempt stopped at a script fault
   (a local shadowing the new `marked()`), kept as `w4-workbook-assembly-20261114-053142-stopped-by-a-script-fault.log`.
4. Redraw the four board PNGs. Then W4 can be called closed.

   *2026-11-14: redrawn* (`41b92eb`, `3dd5ec8`).

**W4 was closed on 2026-11-14**, after an independent review of the rerun (its points on the notes and the
scripts are in `eb5dff5`). The reviews of that day found these and left them open; none blocks W4:

- **Whether the assembly still reports needing a rebuild after the top-only route** was never read, and a put
  with its top-only rebuild under `set_rebuild_suppressed(True)` was shown only by the reruns, not by a probe.
  `PUT_NEEDS_REBUILD` is False in `findings.py` but **not established**: nothing may skip a rebuild on it.
  Extra steps for probe `assembly_rebuild_scope` are planned.
- **A journaled file on a drive that is disconnected is treated as gone** (`W4-REVIEW-PASS4.md`). A design call
  for the user.
- Probe `assembly_rebuild_scope`'s own limits, from its review: its "shown" readings could not tell the routes
  apart (every route showed every change), and the failed-rebuild case was tried only on a failing part.

**Known and left:** a journaled assembly (an interrupted build that had got as far as saving the assembly)
forces a whole `_r<n>`, and its layout part and assembly stay in the journal; with two SolidWorks sessions
running, a document left unsaved in the other session cannot be seen.

## W5 in detail

*Rewritten 2026-11-14, after packages A–D.* The authority order is `PLAN-WORKBOOK.md` → `notes-workbook/W5-DECISIONS.md`
→ `W5-PLAN-REVIEW.md` → `W5-PLAN.md`; the shapes the packages share are pinned in `notes-workbook/W5-INTERFACES.md`.

**Probes.** Tier 8 (`probe/p8_motion.py`: `c53bc2d`, `b9ddb12`; results `853e91b`; findings `9aeed80`) passed on
SolidWorks 2026 (75 of 75) and 2024 (31 of 31), every decision the same. Report: `notes-workbook/W5-PROBE-REPORT.md`
(one misstatement: a mate was deleted by "Select2 then EditDelete()", not `DeleteSelection2`). A gear's axis is mated
*coincident* with the layout's shaft axis (concentric is refused); one gear per shaft, the anchor, is held that way and
along the shaft, every other gear on it by a lock mate alone; every gear mate took Flip False in tier 8 (no longer assumed: see *The ring* below); a 12 : 1 train driven
30° turned its output 2.5° the right way. No API drag reproduces a mouse drag: "drag the input" is a person's step, and
the API proof is a temporary driving mate. PLAN-WORKBOOK §4.4 now carries this as a dated note (*Readings changed by
probe tier 8*), and §6's W5 row says "once probe tier 8 has passed".

**Plan and decisions.** `notes-workbook/W5-PLAN.md`, reviewed in `W5-PLAN-REVIEW.md` (M1–M13). The user's answers of
2026-11-14 and the rulings on the review and on P0 are in `W5-DECISIONS.md` and in PLAN-WORKBOOK §4.5 as *Readings
chosen (W5)*: a refused mate stops the build (no static fallback); Update returns a turned train to its built turn
whenever it has to move any gear (the user's words; ruled per train with review M1: only a train it must put is
put back, whole); no datum plane, so an anchor's Front-plane edits need Build again…; a follower's
place along its shaft is an Update; a tooth change that alters a gear mate's ratio is an Update, by the remake
(Build again… only until probe P0b settled the route); W4 static gearboxes stay static; a recorded mate found suppressed is turned back on.

**Probe rounds.** P0 (`0d638db` … `8504856`), P0b (to `4f865d8`), P0c (to `c66d321`) and P0d (to `26cbf9c`) ran on
both versions and were each reviewed; `W5-DECISIONS.md` has a section of rulings for each. What they settled, in one
line each: a tooth change the globals carry is an Update, by deleting the gear mate and making it again
(`GEAR_MATE_RATIO_ROUTE = "remake"`), also on a gear with two gear mates; a train is built and updated under the
top-only rebuild; mates are found by walking the mate group, may sit in folders, and are made under
`CommandInProgress`; a turning Update refuses while a gear is lightweight. Two more rounds followed the first
demonstration's ring fault (`ad08864` … `79e5341`, then `5fcbdc3` … `9afe65b`); see *The ring* below.

**Interface commit** `2f82a0e`, its review's rulings `07fd66a` (`W5-INTERFACES.md` §6). The packages, each reviewed
independently (D's review of 2026-11-14 asked for the fixes now in, below):

- **A — SolidWorks** (`swcom.py`, `swbuild.py`, the fake): `e231ae3` (the train's mate members from tier 8),
  `6ffc84a` (the fake learns mates), `171a50b` (the mate check before the save; a refused mate stops the build),
  `bad8fc8` (Update's motion path); review fixes `3eba2ec`, `39ddf45`, `0459c04`, `885de1c`.
- **B — planning** (`motion.py`, `gearbox.py`, `update.py`): `e39b9d4` (the mates: anchors, locks, gear mates, loops,
  shafts held still), `84db947` (build to turn whenever the findings allow; record what was made or refused),
  `8bb1d86` (classify and finish a turning Update), `0536153` (the turning round trip on the fake), `1b1bb39` (tests
  pin the findings a probe round may change).
- **C — record and sentences** (`store.py`, `ui_text.py`): `e224e2e`, `5c25a1b`, `0110c88`, `bf3202e`.
- **D — window, boards, docs**: `f71c5c4` (the window passes the read's digest to the footer and the record to the
  Build again? question; its tests restored and the W5 states added), `aa9c5f0` (boards), and the docs commit after
  it; after D's review, `fe62c5f` (C's fixed sentences pinned; W4's failure cases on a turning gearbox: an Update
  lost with SolidWorks, one that stops part way, the structural step with Update unsaved) and a docs commit. The
  window needed no new control. `c7770c8` passes the update's finish to its sentence (B's and C's fix for what an
  unsaved Update left). Its two hanging tests hung on a Build again? question no test answered; every
  window test now gets a stand-in that fails at once on an unexpected question. The four tests about W4's
  tooth-change Update run on a gearbox built as W4 built it (`built_w4`); the W5 findings are pinned in the test file.
  New boards: `WorkbookRefused`, `WorkbookTurned`, `WorkbookStatic` (no fallback board: there is no fallback); every
  board after a build is redrawn with the gears mated. Their Update boards use an edit Update carries whatever the
  ratio finding says (G3 and G4 to module 2.5 with S3 X 148.75, G4's At 27 → 30) in place of G2 68 → 69.

**The ring (found by the first demonstration, 2026-11-14).** The first full run passed on SolidWorks 2024 and failed
seven checks on 2026, all one fault: the ring of Risky_Placements turned the wrong way. No Flip can be chosen from the
plan: every toothed ring probed needs the opposite Flip on the two versions, and which one depends on the ring. On
2024 a new ring gear mate made straight after an Update had moved its pinion 2 mm along its shaft needed the other
Flip from one made after the build and a reopen; whether the move, the Update's puts and rebuild, or the missing
reopen caused it was not separated. So the app assumes none. Each gear mate is read
back after it is made (`swcom.gear_mate_sense`: right when `(Reverse == directions parallel) == internal`) and a wrong
one is deleted and made again with the other Flip; one wrong both ways stops the job as a refused mate. Update's
check phase reads every recorded gear mate the same way (a suppressed one only after Update has turned it back on)
and remakes one found wrong. The record holds no Flip. Code: A `a0d5fad`, `6d7172f`, `8ee3c59`, `c2e8489`, `980f10b`,
`b4d4bdd`, `d99654a`; B `7dbc10f`, `7c0eecc`, `f32e744`; C `1df2384`, `17ff636`; each reviewed, the last must-fix closed
in `d99654a`.

**The demonstration (package E), as run.** Scripts `probe/workbook_assembly_check.py` (sections m1 to m8 for W5; a, a2,
a3, b, c from W4), `probe/workbook_window_check.py`, `probe/cross_version_open_check.py`. Every run started a fresh
SolidWorks and used a `git archive` snapshot named in its log's run line.

- *SolidWorks 2026, the full run* (from `9afe65b`; logs `probe/results/w5-*-20261114-163249*`): every section passes
  once m3 and m7 were rerun with a control that drives both Flips (the main log's two FAILs are the old control, which
  assumed the mate still had the first Flip). Window check 21 of 21.
- *SolidWorks 2026, after the last code* (src of `d99654a`; `…-171802.log`, `…-174603-m8.log`, `…-180303.log`): m1,
  m6 with a suppressed mate folder, m8, and m5, a and a3 pass. Those are the sections whose path the commits after
  the full run changed (`W5-DECISIONS.md`, *Rulings at W5's close*).
- *SolidWorks 2024, the confirming run* (src of `d99654a`; `probe/results/sw2024/w5-*-20261114-171802*`,
  `…-174603.log`): m1, m3, m7, m8 and the window check pass. The one FAIL in the `171802` log is an assertion of the
  script whose premise was wrong (that a fresh ring gear mate needs the Flip the recorded one was made with, after a
  move); `7e2135f` asserts it only while neither gear has moved, and the `174603` rerun of m7 passes.
- *m8, on both:* the app itself moves the ring's pinion (G5 At 45 → 47) and then changes the ring mesh's teeth
  (14/36 → 15/37, an Update). The remade gear mate reads back wrong and is turned round, and a drive at the new ratio
  turns the ring the right way, again after a save and reopen.
- *A 2024-built ring gearbox opened in 2026* reads unmodified and no file changes
  (`w5-cross-version-2024-in-2026-20261114-174215.log`). Closing it there raises the SOLIDWORKS CAM add-in's Yes/No
  "Save changes?" box, which ignores Escape; the scripts answer No. The app closes nothing itself.
- *The person's step* (W5-PLAN §4.4): the user dragged G1 by hand in the 12 : 1 on SolidWorks 2026 and on 2024
  (2026-11-14); the train turned as it should on both, closing asked nothing, and the files on disk were unchanged.

The first demonstration's logs (`…-20261114-112629*`) are kept: 2024 1307 of 1307, 2026 with the seven ring failures.
What the runs leave out, with the reasons, is in the scripts' headers (a fixed shaft, a loop-closer, Update on a pair,
an idler's tooth change: no fixture has one; the idler was shown by probe P0c).

**Open, none of it blocking:**

- **The refused `Assem<n>` left open** is named once, in the build's sentence; the window does not track it, so
  neither the footer afterwards nor a close mentions it (UI-DESIGN §9 says so).
- Caveats the reviews asked to be written down and not run again are at the end of `W5-DECISIONS.md` (for example:
  section c takes the app's word that it turned the ring's mate round and does not drive the ring; the remake under
  `CommandInProgress` from wrong to right was a probe step on 2026 only, and m8 is what shows the app doing it on
  2024).
- The app took a +0.3 shifted pinion inside an unshifted ring at the unshifted centre distance, and the build then
  reported a clash (seen by the ring probe; a question for the user below).
- From W4: whether the assembly still reports needing a rebuild after the top-only route (`PUT_NEEDS_REBUILD` not
  established); a journaled file on a disconnected drive is treated as gone (below).
- For the next phase's demonstration: build each fixture once and start later sections from a copy (*Rules carried
  over*).

## W6 in detail

*Written 2026-11-14, after packages A–D (A on a small second pass, A's and B's reviews running).* The authority order
is `PLAN-WORKBOOK.md` → `notes-workbook/W6-PLAN.md` (revised after its review `W6-PLAN-REVIEW.md`, at `eb195d0`; its
*Changes after the review* section says what moved) → `W6-INTERFACES.md`, whose §7 holds the rulings (eighteen so far) on the
interface review that bind the packages. W5's decisions stay in force.

**What W6 adds.** Shafts along `X±`, `Y±` or any direction; bevel meshes between shafts that meet and crossed
helical meshes between shafts that pass each other; speeds about each shaft's own axis; the layout part with planes
for cardinal turned axes and a fixed 3D-sketch line for a slanted one; anchors measured from the base plane square to
the shaft; gear mates between non-parallel axes, read back by a rule probe tier 9 found; the record's schema 4. The
decisions D1–D18 are in PLAN-WORKBOOK §4.5 as *Readings chosen (W6)*, and §4.2 has a dated note on turned axes;
the ones to put to the user first are D1 (one facing per shaft), D4 (if the 3D line fails, slanted axes are refused
in W6) and D16 (a turned mesh is refused before Build while the finding is missing, with no static fallback).

**Probe tier 9** (package P, `turned_gear_mate_sense`, W6-PLAN §7.2): run first, on SolidWorks 2026, while the
packages were written (D6). `8f529f6`, `1b9b281`, `c2fbaca`; results `c0483f3`; findings `11ee1e2`
(`TURNED_GEAR_MATE_SENSE_READ_BACK = "entity senses"`, `TURNED_GEAR_MATE_SENSE_ANGLES = (30.0, 150.0)`) and, after
the tier 9 review's must-fix, `9ac7d6d` (`TURNED_GEAR_MATE_SENSE_ANGLES_SKEW = (60.0, 120.0)`: axes that pass each
other were run only at 60°, 90° and 120°). Both gates read the class of the mesh (`swcom.lines_meet`) and its
range (`swcom.turned_angles`), ruling §7.12–§7.13.

**Interface commit** `34bfb85`, its review's rulings `9d3b43f`, `8200fcb`, `c65cd15`, `92dd04e`, `63c6e65`. The packages:

- **A — SolidWorks** (`swcom.py`, `swbuild.py`, the fake): `11ec034` (`lines_meet`, `turned_angles`), `8b6a080`
  (the turned sense read by rule H, gated per class), `128aa8e` (build and update turned gear mates against their
  planned axes; remake a mesh whose sense moved), `ec85d3e`, `377921a` (W5's ring list dropped once planning passes
  senses), `293fdee` (the fake works a turned mesh's sense out itself; fixture B driven whole). A second pass is in
  hand.
- **B — planning** (`workbook/`): `25d677a` (turned layout, own-axis speeds), `59b196f` (check, refuse and plan
  turned meshes; bevel and turned rows built), `1d14dbd` (the turned refusal asked only with a turned mesh),
  `efe2709` (classify turned Updates, the resense remake, the slanted lines to the worker), `e3ae0ce` (Results rows
  for bevel and crossed meshes; *seen from*), `2d660fa` (the move fix in any parallel family's plane), `f38036e`
  (bevel rows of `plan_parts`), `107c6ea` (a mesh's recorded sense kept on a failed Update).
- **C — record and sentences** (`store.py`, `ui_text.py`): `c2e48b5` (schema 4's refusals), `7657e62` (sense 0 legal
  on a parallel mesh, ruling §7.1), `95c1589` (speeds, the turned refusal, the sense remake), `34ed1c8` (W6's
  structural sentences), `26c6776` (the remake and refusal sentences made true).
- **D — window, boards, docs**: `f88e331` (five later-phase tests re-pinned to a carrier, a sleeve and a slide, since
  W6 builds bevel rows and turned axes), `872e596` (the end view draws turned shafts; the window plans Build parts
  when a turned mesh is refused, which the footer already offered and the press could not run; W6's window tests),
  `cd1c168` (a turned shaft's name kept on the canvas; the Speeds lines wrap at the end view's width so the window
  keeps its own), `34e1238` (boards `WorkbookRightAngle` and `WorkbookCrossed`; `WorkbookError` redrawn, its bevel
  row now an error), and the docs commit after it. The window has no new control (D15), checked from the code: the
  only changes to `workbook_gui.py` since W5 closed are the end view's lines, the Speeds wrap and the parts-only
  plan.

**The two fixtures** (W6-PLAN §5), written as specs in `tests/test_workbook_turned.py`, to be committed as Excel
saves them by E: A, `Bevel_Reducer` (a bevel stage, S1 along X+ into S2, feeding a parallel stage: 6.000 : 1, output at 90°
to the input); B, `Crossed_Slant` (a crossed helical stage, then a bevel stage at 120° onto the slanted S3: 3.000 :
1). Their Checks panels, header lines and speeds are pinned by B. In the window both build to turn on the fake; a crossed
shaft moved to its partner's other side is an Update that remakes the gear mate (D17).

**What the demonstration (package E) still has to show**, on SolidWorks 2026 with the committed findings only and
then one confirming build on 2024 (W6-PLAN §6, the testing rule of 2026-11-14): both fixtures built end to end,
fixture A first; each turned gear mate read back and driven, with the interference check after every control drive
(the right Flip clear, the wrong one clashing: M2); the slanted line axis (`line_axis`, never probed ahead: ruling
§7.16) built and read back; sections r1–r6 (r1 and r5 the full builds of A and B; from copies of them, `copy_built`
of W6-INTERFACES §4: r2 a turn by hand then a move along S1 with G2's apex, r3 G1 20 → 21 teeth with the remake on
the bevel mate, r4 S1's Axis X+ → X− as Build again…, r6 on B a Face Z move, G4 30 → 31 on the 120° mate, the slant
changed as classify only, and the crossed resense as classify only); and the window check rw. Its expected Speeds
lines in W6-PLAN §6.1 read *"seen from +X"*; C's sentence, as the window shows it, is *"seen from the +X end"*. Then
the person's drag of fixture A's input (W6-PLAN §6.1's last paragraph).

**Open:**

- A's second pass and A's and B's reviews are running; a shape may still move slightly.
- If the full build shows the 3D-sketch line failing, D4 falls back to refusing slanted axes in W6, and that goes to
  the user.
- The Speeds line of a shaft seen from an end other than +Z is longer than the end view is wide, and wraps there
  (`cd1c168`); a shorter wording is C's, if wanted.
- The end view's readout still names the face heights (`z 5 · z 60`); for a gear on a turned shaft that is the height
  of its At point (a bevel's apex), which is what colours a right-angle stage as one.

## Questions waiting for the user

Questions 1 to 5 of 2026-11-14 are answered (`notes-workbook/W5-DECISIONS.md`; PLAN-WORKBOOK §4.5, *Readings chosen
(W5)*). Still open:

1. **A journaled file on a disconnected drive is treated as gone** — keep that, or hold such entries until the drive
   is back?
2. ~~Should the Checks panel say, before a build, that a profile-shifted pinion inside a ring clashes at the
   unshifted centre distance?~~ **Yes** (the user, 2026-11-14); added in `d3f4dcf` and `9efde87` (the pinion is held
   to the working centre distance its shifts make, with the outside pair's error and move fix).
3. Readings the user may overrule: Update SolidWorks does not save; a part keeps its file name after a teeth change;
   one build button; no static option in the window once W5 is in (a gearbox is built static only when a W5 finding
   is missing, and a W4 one stays static until Build again…).

Answered ahead of its phase (the user, 2026-11-14), for W7's sub-plan:

- **A carrier is built as a skeleton only.** W7 makes a carrier as a part of axes and planes with no solid, as the
  layout part is, free to turn about its own shaft's axis, with each planet mated to an axis in it. The app makes
  no solid carrier (a plate, pins): that geometry depends on the gearbox at hand and is left to the user. PLAN-WORKBOOK
  already has the carrier as a shaft row that planets are `Mounted on`; this settles what stands for it in
  SolidWorks.

## Rules carried over

- Commits and PRs carry **no Claude co-author or attribution line**. Commit by explicit path only
  (`git add <paths>`; `git commit -m "…" -- <paths>`), prose messages with the why; never `add -A`,
  `commit -a`, stash or reset. ~~Push only when the user says so.~~ Since 2026-11-14 the user wants each
  reviewed step pushed to `origin` as the work goes; the orchestrating session pushes, subagents commit only.
- **The repo is public**: no user document titles in committed logs (`<user document N>`), no other
  personal data.
- Each phase's plan and result is reviewed by a separate subagent before moving on. In the 2026-11-13
  session the user asked for Opus subagents only, with no cap on their number.
- ~~Every SolidWorks call is probed before the app depends on it.~~ **Since 2026-11-14 (the user, after W5's
  six probe rounds): the full build comes first.** A phase is written against the fake and then built end to
  end on SolidWorks early; what that build gets wrong is what gets probed step by step. Probing before the
  app depends on a call is kept for one kind only: a call not used before that could hang, raise a dialog, or
  leave a file or a session damaged. **SolidWorks 2026 is the working version**: probes and the full test run
  there, and SolidWorks 2024 gets one full build at the phase's end to confirm, with what fails there fixed
  then. One follow-up probe round per phase; a reviewer's point the app does not depend on is written down as a
  caveat, not run again. After a fix only the affected demonstration sections are rerun, with one full run at
  the phase's close. Findings are still read from committed `findings.py` only, a missing one still refuses
  with a sentence, and the plan's STOP-and-ask triggers apply.
  *What the confirming build on 2024 is:* not the whole demonstration again. It is one full turning build
  with its edits, plus every section in which the two versions have been seen to differ (for W5: `m1`, and the
  ring sections `m3` and `m7`; about 12 minutes where the whole run takes 36).
  *Not done yet, for the phase after W5:* the demonstration builds each fixture from scratch in nearly every
  section (the 12 : 1 seven times). Build each fixture once and start the later sections from a copy of the
  built folder; the records hold paths, so the script has to carry them over, and that change is reviewed like
  any other.
- **SolidWorks runs only on the Windows host.** SolidWorks 2024 there is the user's live session: record
  the open titles before a run, close only documents the run created, never save, close or modify theirs,
  never exit it, stop under 2 GB of free RAM, and prefer a freshly restarted session for long runs (one
  long probe run grew it by about 5 GB). An agent may start and exit its own SolidWorks 2026. One driver at
  a time. *On the user's own device (2026-11-14):* the user allows both SolidWorks 2026 and 2024 to be started,
  exited, and killed when one will not exit or memory is short; still one SolidWorks running at a time (the
  app asks every running SolidWorks for its version), and nothing the user has open is touched.
- Excel on the Windows host may be opened: use only an Excel the run starts, close only the workbook you
  opened, never quit the user's Excel.
- Screenshots on the Mac: capture by window id (`screencapture -l`), not by region, because a region
  capture picks up whatever app is in front.
