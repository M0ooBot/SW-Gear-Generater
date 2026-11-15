# Handoff: the workbook import (branch `workbook`)

Rewritten the night of 2026-11-13, when work on the Windows host was wound down so it can carry on from
another machine. **`docs/PLAN-WORKBOOK.md` is the plan and the authority**; this note only says where things
stand within it. The working papers of the session (plans, reviews, reports) are in `docs/notes-workbook/`
and are named below where they matter. Where one of them names a script such as `w4x_….py` or `w5r_….py`,
that was a throwaway repro in a temp folder and was not kept; the fixes' regression tests replace them.

**Updated 2026-11-14**, on the Windows host again (a WSL clone, with SolidWorks 2026 and 2024 both started and
exited by the agents): W4 was closed and W5 begun. The dated paragraphs below say what changed; the user's
answers of that day and the rulings that follow from them are in `notes-workbook/W5-DECISIONS.md`.

**Updated 2026-11-15 (later that day), from a second Windows host** (`DESKTOP-QJTI7HF`, a WSL clone; its SolidWorks
2026 is SP0, revision **34.0.0**, where W5 to W7 and the W8 spike ran on the other machine at 34.1.1): W8 was picked
up again at the user's word. *W8 picked up* under "W8 in detail" says where it stands. The run folders of W5 to W7
(`w6-full-…`, `w7-full-…`) are on the other machine, not this one.

## Where it stands

| Phase | State |
|---|---|
| W0–W1 xlsx read/write, model, schema | done, reviewed, review fixes in |
| W2 Workbook window, live link, Build parts | done, reviewed, fixes in. The batch build (`swbuild.build_many`) ran on SolidWorks 2024 and 2026 (`208712c`); logs `probe/results/w2-build-20261113-164647.log` and `probe/results/sw2024/w2-build-20261113-165706.log`. |
| W3 geometry, phases, kinematics, checks, fixes, Export, Results sheet, two-column window | done, reviewed twice, every item fixed. The Excel checks passed on Windows: the Windows-saved fixture (`aa86cc7`) reads, and exported files open in Excel with no repair prompt. |
| W4 layout part + static assembly, Update SolidWorks, build-again `_r<n>` | **closed 2026-11-14**: the rebuild fault probed and fixed, pass 4 verified, both demonstrations rerun on SolidWorks 2026 and 2024 with every check passing, each step reviewed. Details and what is left open below. |
| W5 motion | **closed 2026-11-14**: probes P0 to P0d and the two ring rounds run and reviewed, packages A to E written and reviewed, the demonstration run in full on SolidWorks 2026 and confirmed on 2024, the user's hand drag passed on both. Details, and what is left open, below. |
| W6 right-angle | **closed 2026-11-15, but for the person's drag**: planned, reviewed and revised; probe tier 9 (a turned gear mate's sense, on cylinders, SolidWorks 2026) run and reviewed; packages A to E written and each reviewed; the full build run on SolidWorks 2026 and the confirming build on 2024, both from one snapshot (`931fe1a`), every check passing, each run reviewed. Left for the user: drag G1 in the built right-angle gearbox. Details below. |
| W7 planetary | **closed 2026-11-15, but for the person's drag**: planned, reviewed and revised; the spike on SolidWorks 2026 (`W7-SPIKE.md`); packages A to E written and each reviewed; the demonstration run on SolidWorks 2026 — its first run found one app fault (a turned planetary's put did not hold), the probe `planetary_put_back` measured the route that does, the fix `9f21d99` was reviewed, and every section then passed, the planetary sections and the W5/W6 Update sections once more on the final code; the confirming build on 2024 passed; the run's evidence reviewed. Left for the user: drag Sun in the built planetary. Details below. |
| W8 sleeves and modes | **picked up 2026-11-15 and running on SolidWorks 2026 (34.0.0, the second host)**: `s0` and `s1` pass (0 failed, `s1.master` kept); `s2` to `s4` being written and run; `s5`, `s7`, the window check, the closing run and SolidWorks 2024 left. See *W8 picked up* below. Before that: planned, reviewed and revised to the spike (`W8-PLAN.md`, `W8-PLAN-REVIEW.md`, `W8-SPIKE.md` with its follow-up and its SolidWorks 2024 section: one slide mate with a value per configuration, mates switched per configuration, positions kept per configuration, handles stale after every add and show, the same on both versions); the interface commit with its rulings (`W8-INTERFACES.md` §9); the findings set and reviewed (`ea7a46f`); packages A, B, C and D written, each reviewed, the reviews' points in, the suite green. **No W8 code has run on SolidWorks:** the demonstration (package E), the full build on 2026, the confirming build on 2024 and the close are left. Details below. |
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

**The demonstration (package E), as run.** `probe/workbook_assembly_check.py` sections r1 to r8 (fixture A,
`Bevel_Reducer`: r1 built, r2 to r4 and r7 from copies or variants; fixture B, `Crossed_Slant`: r5 built, r6 and r8
from copies), `probe/workbook_window_check.py`, `probe/cross_version_open_check.py`. `copy_built` builds each fixture
once and starts the later sections from a copy of the built folder.

- *The first full build on SolidWorks 2026* (2026-11-14; `probe/results/w6-workbook-assembly-20261114-210827.log`)
  found one fault of the app: `swcom.line_axis` asked the sketch manager for `Insert3DSketch2`, which is a member of
  the document; the sketch manager's is `Insert3DSketch`. Fixed in `b3a88f6` (and `0c32b17`), checked step by step on
  SolidWorks (`w6-line-axis-steps-20261114-221843.log`), and the sections that needed fixture B rerun
  (`…-221901-r5-r6-r8.log`). The log's seven FAIL lines are that fault (six) and one fault of the script.
- *The run that closes the phase*, both versions from one `git archive` of `931fe1a`: SolidWorks 2026, every W6
  section (`w6-workbook-assembly-20261114-233518-w6-931fe1a.log`, 1146 checks, none failed); SolidWorks 2024, the
  confirming set r1, r5, r3, r6, r8 and W5's m3 (`sw2024/w6-workbook-assembly-20261114-224626-confirm.log`, 949
  checks, none failed), the window check on each, and a 2024-built `Crossed_Slant` opened unmodified in 2026
  (`w6-cross-version-2024-in-2026-20261114-233432.log`).
- *What only real teeth could show, and did, on both versions:* on every turned mesh the drive matches the plan's
  hand-worked turns, exactly one Flip turns right, the right Flip runs clear and the wrong one clashes with its
  partner alone (142 to 497 mm³), and the app's read-back agrees with the drive on both Flips. Fixture A's bevel mate
  is right as first made; fixture B's crossed mate and its 120° bevel mate are made wrong, read wrong and made again,
  the same on 2024 as on 2026.
- *Also shown on both:* the slanted axis on its line; anchors on the negative side of the Right and Top planes; a
  turned gear mate made again at a new ratio (r3, r6, r8); a quiet Update on a turned gearbox marking no document.

**Left for the user (W6-PLAN §6.1):** drag G1 in `Bevel_Reducer.SLDASM` and watch G4 turn at one sixth, the other
way round as the Speeds panel says. The 2026 build is kept at
`C:\Users\M0obo\Documents\GearGeneratorProbe\w6-full-20261114-210827\out\r1`.

**Caveats the reviews asked to be written down and not run again** are in `W6-INTERFACES.md` §7.21.

## W7 in detail

*Written 2026-11-14 and brought to the close on 2026-11-15.* The
authority order is `PLAN-WORKBOOK.md` → `W5-DECISIONS.md` → `notes-workbook/W7-PLAN.md` (revised after its review
`W7-PLAN-REVIEW.md`, `939b726`, and the spike `W7-SPIKE.md`, `8a798fe`; its §10 lists every change, "After the W8
check" included) → `W7-INTERFACES.md`, whose §6 holds the rulings on the interface review that bind the packages.

**The user's decision, taken before W7:** a carrier is built as **a skeleton only** — a part of axes and planes with
no solid, as the layout part is, free to turn about its own shaft's axis, each planet mated to an axis in it. The app
makes no plate and no pins: that geometry depends on the gearbox at hand and is left to the user.

**The orchestrating session's rulings, taken while the user was away; the user may overrule each** (PLAN-WORKBOOK
§4.5 marks them *ruled*): the first draft's absolute-ratio fallback dropped, since SolidWorks showed it turning the
planets wrong; a gear on the carrier's own shaft built, locked to the carrier, because W8's transfer case needs one,
and refused if it meshes; no fix offered on a planetary mesh; every planetary form W7 does not build refused as an
error, not left for a phase; and J5's gear mates as below (`W7-INTERFACES.md` §6.14).

**What W7 adds.** One simple planetary stage per workbook: a sun, a ring and a spur planet gear on a planet shaft
`Mounted on` a carrier, with any number of `Copies`, every shaft of the stage along Z+ or Z− facing the carrier's way,
exactly one member held and one the input; beside it, W5's trains, other frame shafts on the carrier's axis, and
gears on the carrier's own shaft locked to it (J8). Copies placed in the carrier's frame (J4) and phased so every
copy meshes at once; the assembly condition and the room round the carrier as errors; speeds with the carrier term
and torques with the held member's reaction; the carrier part (`<Name>_<C>_Carrier`); the gear mates (J5, by
default, which the user may overrule): one for each sun mesh, so one per copy, and exactly one with the ring, from
copy 1, chosen by member and not by the order of the Meshes sheet's rows; Update's puts held member first, carrier
next (J15); schema 5. The readings J1–J20 as revised are in PLAN-WORKBOOK §4.5, *Readings chosen (W7)*, with notes
under §3.3, §3.5 and §4.2. Everything else that reads as a planetary is **refused as an error of the workbook** at
its cell: a differential, two inputs on a stage (whether or not their speeds agree: §6.15), a compound or double
planet, a gear on the carrier that meshes, a helical planetary, members facing different ways, a carrier on a
carrier or off Z±, a second carrier — each listed for the user as something a later pass could open.

**The spike** (`w7_planetary_spike` in `probe/p8_motion.py`, results `probe/results/w7-spike-20261114-192709.*`, on
SolidWorks 2026 only): a gear mate between a carrier-borne axis and another turns its gears relative to the line
between their axes, so in a planetary relative to the carrier; the plan's mates turned the 4 : 1 right (sun 30°,
carrier 7.5°, each planet −15°, ring still, no interference); the ring mate read back wrong with Flip False and right
remade. The first draft's kinematic fallback turned the planets wrong and is gone.

**Interface commit** `5d5d51d`, its review's rulings `abca489`, `541585b`. The packages:

- **A — SolidWorks** (`swcom.py`, `swbuild.py`, the fake): `75d089b` (the carrier part built and updated; a planetary
  train put back in order), `f1395ae` (a held gear joined by its gear mates; the stages the drive had not covered),
  `7a34852`; after the run, `9f21d99` (the put with the gear mates off). Reviewed.
- **B — planning** (`workbook/`): `366ff42` (lay out, solve and check a stage), `5146b75` (the carrier part, mates and
  build; the carrier on record), `42fbe29` (Update's classification of a stage), `4700a3e` (the Results sheet: a
  planet's speed on its carrier, a held member's torque), `a22369f` (every fixture driven on the fake after its build
  and each Update), then the review's points (`6ed3439`, `765c2ca`). Reviewed.
- **C — record and sentences** (`store.py`, `ui_text.py`): `efe47a2` (schema 5's refusals), `f81fec5` (the carrier id
  suffix in the store), `0e8df59` (a stage's words: carrier, copies, speeds), `ff57941` (the refusals whole, with
  Build parts offered), `60f2fbe` (a carrier part's moved planets after Update), `cc106e5` (the review's points on the
  record and the Speeds panel).
- **D — window, boards, docs**: `c37c1e7` (the later-phase tests re-pinned to W8's rows; a carrier builds),
  `bac9eef` (the end view's carrier circle through its planets, the torque note in prose, the window tests of every
  fixture), `d650e0f` (boards `WorkbookPlanetary`, `WorkbookPlanetaryCopies`), and these notes; then the review's
  points: the carrier's axis and the Speeds panel's prose rows asked of `geometry.carrier_axes` and
  `ui_text.speeds_prose_rows`, names on a shared cross in the Shafts sheet's order (`S, C, R`, as the Speeds panel)
  and every end-view name on a plain backing (every Workbook board redrawn), a 4 : 1 off the origin in the tests,
  two inputs among the refused kinds.

**The fixtures** (W7-PLAN §4), as B's `tests/test_workbook_planetary.py` writes them: `Planetary_4to1` (the ring
held, sun in at 1000 rpm, carrier out, three copies, `CarrierGear` on the carrier: 4.000 : 1), the sun held (1.333 :
1), the stage on Z−, the carrier held (3.000 : 1, the other way).

**The demonstration, as run** (package E, `probe/workbook_assembly_check.py` sections p1 to p7; W7-PLAN §6). Every
number below is SolidWorks' own reading, judged against the plan's hand-worked turns.

- **The 4 : 1 built through the app turns right** (p1): the sun's +30° gives the carrier and CarrierGear +7.5°,
  every copy −15°, the ring 0, to about 1e-13°; all six meshes stay in step, the two ring meshes with no gear mate
  among them; no interference as built, at three other phases, or driven. A wrong Flip clashes (about 50 mm³ at each
  planet–ring mesh). The carrier part has no solid body, and each copy's axis passes through its copy's centre to
  2e-9 mm.
- **The other stages** build, drive and reopen: the sun held (p5: carrier +22.5°, planets +45°), the stage on Z−
  (p6), the carrier held (p7: ring −10°, planets −30°), four copies (p4). A second planet–ring gear mate (p2, never
  saved) was logged as facts only.
- **Update** (p3): after a turn of 37° on the sun and an edit, the whole train goes back — the carrier first, or the
  held ring first when it is off — and a tooth change to 3.714 : 1 remakes its four gear mates and turns right
  (carrier +8.077°).
- **The one app fault the run found, and its fix.** The first full run (snapshot `39ecf66`) stopped in p3: the
  carrier's put did not hold while the train's gear mates were on (ruling 13's unshown assumption). The probe
  `planetary_put_back` (tier 10, `probe/p10_planetary.py`, results `w7-planetary-put-20261115-012409.*` and its
  follow-ons) tried four routes on SolidWorks 2026; the one that held is **every gear mate of the train and its
  locks suppressed around the puts**, then everything turned back on (`findings.PLANETARY_PUT_ROUTE`). A's `9f21d99`
  does that for a train with a carrier only; a train without one makes the calls it always made (468 call sequences
  on the fake compared identical). `5fcaa6a` then keeps a per-mode gear mate off through such a put (W8's path).
- **SolidWorks 2024, the confirming build** (log `w7-2024-20261115-020234-p1-p5-p3-step1.log`): p1, p5
  and p3's put-back pass. One difference, handled by the read-back as everywhere: on 2024 the planet–ring gear mate
  turns right as first made, on 2026 the build turns it round.
- **The window** ran through its boards on 2026 (`w7-window-20261115-015017.log`): the planetary builds with its
  carrier part, its footer says to drag Sun, and five copies give the assembly-condition error with Build not
  offered.

Logs: `probe/results/w7-workbook-assembly-20261115-000138-*.log` (the first run and the regression of W6's and W5's
sections, all passing, on `39ecf66`), `w7-put-fix-20261115-014257-p3-p4.log`, and the two named above (on `9f21d99`).
The closing run, from one archive of HEAD `08fd712` (which holds `5fcaa6a`), on SolidWorks 2026:
`w7-close-20261115-021540-p-r-m.log` — p1, p2, p5, p6, p7 again, and the W6 and W5 sections that press Update (r1 a
quiet Update, r2 a turned train put back, r3 a ratio remade, m8 a move and the ring mate remade, m5 a lost Update
pressed again), all passing: the review of the evidence asked for it, since `db4d4e3` and `ccb05ae` had changed
Update and the sense read for every gearbox after the first run.

**Caveats at the close** (`W7-INTERFACES.md` §6.17 has them in full): the put order is logged from the app's own
result, SolidWorks confirming the frames after the puts; in p7 a wrong Flip lands every gear a whole number of
pitches off, so there the right sense rests on the frames, not on a clash; 2024 ran p1, p5 and p3's first step
only; a gear mate remade inside the suppression (a tooth change on a planetary) is read when remade and not again
once turned back on; `Planetary_4to1.xlsx` as Excel saves it is not committed (no test or script reads it).

**Left for the user:** open `Planetary_4to1.SLDASM` in the built folder
`C:\Users\M0obo\Documents\GearGeneratorProbe\w7-full-20261115-000138\out\p1` and drag Sun by hand: the carrier
should follow at a quarter of the turn with the planets rolling between sun and ring. Close without saving.

**Open:**

- `assess.lay_out_refusal`'s *"The gearbox cannot be laid out yet, since it is not checked: …"* is reached by no
  input found: `Report.unchecked` is set only from `planetary.not_laid_out` (a carrier riding a carrier, a planet
  across its carrier), and `planetary.refusals` says each of those as an error at its cell under the same
  conditions, so `build_refusal` answers first.

## W8 in detail

*Written 2026-11-15, while packages A, B and C land their passes.* The authority order is `PLAN-WORKBOOK.md` →
`W5-DECISIONS.md` → `notes-workbook/W8-PLAN.md` (revised after its review `W8-PLAN-REVIEW.md` and after the spike
`W8-SPIKE.md`, with its follow-up and its SolidWorks 2024 rerun; *Changes after the review* and *Changes after the
spike* list every change, and where they differ the second wins) → `W8-INTERFACES.md` (interface commit `e9efab9`),
whose §9 holds the rulings on the interface review that bind the packages.

**What W8 adds.** The `sleeve` and `dog` kinds (the strip's ring and spur teeth, `gears/clutch.py`, never offered by
the strip), gears that slide (`Slides`) on frame shafts along Z±, and the Modes sheet: each mode places every slider,
what it engages is worked out (a sleeve covering a dog's whole face couples their shafts), and speeds, torques,
ratios and checks are per mode. Build makes one configuration per mode, named as the mode, the first Modes row the
one the assembly opens in; one distance mate per slider with a value per configuration; each coupling and each
spline a 1 : 1 gear mate between collinear axes, settled by the read-back, a coupling switched on only in the modes
that engage it. Update works across the configurations (W8-PLAN §1.10). The record's schema 6. W8 is the last phase:
no row waits for a later one, and what this version does not build is an error naming no phase. The readings J1–J27
as revised are in PLAN-WORKBOOK §4.5, *Readings chosen (W8)*, with a note under §3.4 and one under §6.

**The orchestrating session's rulings, taken while the user was away; the user may overrule each** (PLAN-WORKBOOK
§4.5 marks them *ruled*): the sleeve and dog as toothed rings with **no fork groove, hub or chamfers** (J1) and at
the Box's **20° by default**, not canvas E4's 30° spline, which the strip's full-depth teeth would make a 0.022 mm tip
(J2); the collinear gear mate (J8); **a slide as one distance mate with a value per mode** (J7, after the spike);
**one configuration per mode** (J10); a Modes edit that needs no new mate is an Update (J14), but **one that would
leave a coupling or sliding mesh on in no mode is Build again…** (W8-INTERFACES §9.1); **a coupling between shafts
facing opposite ways is refused until one has been shown** (§9.3); every quiet Update of a gearbox with modes says
which mode it worked in and that it did not show the others (§9.11). J16 departs from PLAN-WORKBOOK §3.4's warning
and is announced as such. W8-PLAN §0.4 puts J1, J2, J16, J14 and J11 at the top of the list for the user.

**Measured by the probes, not yet by the app:** **positions are kept per configuration** (a turn the user gives in
one mode stays in that mode, J11) and **a put holds in the configuration shown only** (so Update puts mode by mode,
J26). The W8 spike's follow-up measured both on SolidWorks 2026, and its rerun on 2024 measured the same, against
what GOTCHAS §83 recorded for a free mechanism (the findings are committed in `ea7a46f`). **No W8 code has run on
SolidWorks yet**: the spike and its follow-up,
on both versions, are all W8 has shown there. What the app says about a turn follows the running version's finding
(`swcom.positions_per_configuration`), and makes neither claim where it is unsettled or after a restart.

**The window (package D).** The **mode chooser** in the Speeds panel's header — the window's first new control since
W5, drawn on the board first (`WorkbookModes`) — one segment per Modes row, the first chosen, kept across re-reads
while a mode of that name is there. It chooses which mode's speeds and end view *the window* shows; it does not
switch SolidWorks' configuration and clicking it sends nothing to SolidWorks, and a grey line at the panel's foot says
so (`ui_text.mode_chooser_note`). The end view draws each slider at the chosen mode's place: a slide runs along the
view, so a sleeve over a dog is drawn in that dog's face colour. Every end-view name now stays on the canvas, clear
of the names placed before it where a side allows, and a name many coaxial shafts share breaks onto lines. The
footer passes the last job's `positions_per_configuration` to C's sentences (§9.12). The strip refuses a sleeve's or
dog's `.gear.json` with C's sentence (W8-PLAN §1.1, review S9), at Open .gear.json, the only way a record reaches
the live link's Update values.

**For the user to look at:** the mode chooser — `design/renders/WorkbookModes.png` (the E4 transfer case, on 4L) and
`WorkbookModesBuilt.png` (TransferCase_Parallel built, on 2H), and UI-DESIGN §9, *Modes*, which says why it exists
and what it does not do; and the readings above.

**Packages so far** (`git log e9efab9..`): **P/E — probes and logs** `ed81031`, `eca568d`, `bdc4c50` (the spike and
follow-up on 2024); **A — SolidWorks** `6a54fb1`, `3ea4d87`, `a6c04cc`, `d872ca5`, `f9a8cae` (the build's mode phase,
the build gate lifted), `39ecf66`, `db4d4e3` (Update across configurations); **B — planning** `120192d` (the sleeve
and dog kinds), `bb1a946`, `73e3ebe`, `33b28b3`, `124df33`, `f0417a7`, `7fbc56c`, `a13dd18`, `6669717`, `7124394`,
`0ea5cc1`, `a25f9be`, `0665c40`, `bdefb90`; **C — record and words** `d005549`, `5bf7825`, `131bcd2`, `0f1defd`,
`5a49a04`, `4f1e1bd`, `3b1bcc1`, `634f37c`; **D — window, boards, docs** `2b45315` and `e23f41e` (the later-phase tests re-pinned: no real kind waits now, the channel tested with a dog made a made-up W9's), `33c4729` (the chooser, the end view per mode, the footer's claim, the strip's refusal), `527f65e` (boards `WorkbookModes`, `WorkbookModesBuilt`) and these notes.

**The fixtures** (W8-PLAN §2, `tests/workbook_fixtures.py`): **TransferCase_Parallel**, the low range on a reverted
layshaft (17 : 34 twice at 51 mm), every shaft a frame shaft — W7-free, built first as the shakedown; and the **E4
transfer case**, E3's 4 : 1 planetary as the low range. Modes 2H, 4H, N, 4L for both: Rear 1500 / 1500 / free / 375
rpm, Front free / 1500 / free / 375.

**What the demonstration (package E) still has to show** (W8-PLAN §5), on SolidWorks 2026 and then one confirming
build on 2024: TransferCase_Parallel built through the app as the shakedown (the sleeve and dog kinds' own parts
first), then the E4 transfer case; each mode's configuration, slides at their values, couplings on where they
engage, driven per mode with the both-Flips control; interference per mode with a half-pitch control; Update across
modes (an inactive configuration's value and flag set back, a J14 edit, a turn in one mode left alone by an Update in
another); and the window through these states. Sliding gears are tested against the fake only: neither fixture has
one.

**Where W8 was paused (2026-11-15, the user's call, to keep usage down).** Every package is written and reviewed,
and each review's points are in: A (`6a851c2` the slide's dimension reached as the probes reached it, `ccb05ae` and
ruling 9.16, `5fcaa6a`), B (`13043de` the frames each mode hands the build pinned from the teeth, `89f143b` and
ruling 9.17, `e56e892`), C (`45479ea`, `295a214`: the Gears table's states shortened to fit their column — "same as
G1", "changes on Update", "new part on Build"), D (`22d0dce`, `14d1125` the window back at 1080 px with modes and
every mode name whole, `93708d6` the boards redrawn as the window draws). The suite is green. **No W8 code has run
on SolidWorks**, and the findings are set, so the app WILL build a gearbox with modes there: treat it as unshown.

**W8 picked up (2026-11-15, the second host; the coordinating session with Opus subagents, each step reviewed
by a separate one, every commit pushed as it lands).** The list under *To pick W8 up* below is kept as it was written;
this paragraph says what has been done of it.

- **The late passes were reviewed** (item 3 below): C's and D's in `notes-workbook/W8-REVIEW-LATE-CD.md`, A's
  `5fcaa6a` in `W8-REVIEW-LATE-A.md`. The suite was NOT green at `fa4e508`: one window test failed under Windows
  Python, because `c29ea2e`'s finding (a suppressed gear mate's sense is read) took a sentence out of a quiet Update
  that a test, a board and UI-DESIGN still showed. Fixed (`08318d7`), with the chooser's dead trace (`a4ae910`) and
  the Speeds header's room (`b12838d`: the chooser now gets the room the header leaves beside its readout, 172 px
  beside "seen from +Z" and 91 px beside a turned shaft's readout at 100 %, at most 200 px — so 2H 4H N 4L goes to
  rows whenever a shaft is off Z; no board draws that yet). Their review is `W8-REVIEW-FIX-CD.md`, its points in
  (`34e48b5`, `7e6c09d`, `4c233b2`). The redrawn `WorkbookModesUpdated.png` stands; this host draws text about 1 %
  wider than the host that drew its neighbours, so the three mode boards should be redrawn together next time.
- **A's fixes from that review**: a carrier train with modes is put back through the measured per-configuration
  suppression, and every per-mode mate's flag is read in every configuration after Update's mode loop (`c14e1b2`);
  E4 through a changed Update on the fake (`ff1c4dd`); a gear mate lost inside a planetary's put is said gone, not
  "left suppressed" (`c48b6ef`, `963eac4`). Reviewed in `W8-REVIEW-FIX-A.md`. Item 4 below (a gear mate remade inside
  a planetary's suppressed put is not read again) is **left as a caveat**: W7's p3 showed the case on 2026, W8 never
  remakes, and the gap is 2024.
- **The first build on SolidWorks found one app fault**, fixed: `IFeature.IsSuppressed2(3, names)` answers in the
  document's configuration order whatever order the names are passed in, and the app paired the answers with the
  order asked, so a build refused itself on flags it had set right
  (`probe/results/w8-workbook-assembly-20261115-091456-s0-stopped-by-an-app-fault.log`,
  `w8-configuration-order-20261115-092100.txt`). The app asks one configuration per call since `03a4e51`; an answer
  that is not a flag is a sentence (`2d8fb47`).
- **Probe tier 11** (`src/gear_generator/probe/p11_modes.py`; W8-PLAN §4.2 item 1, which the plan called
  `p9_modes`; results `probe/results/w8-over-defined-20261115-100312.*`, SolidWorks 2026 34.0.0): a configuration
  whose two slides fight shows with no window that asks; a non-modal "Over Defined" balloon tip came once and stood
  at least about 2.3 s; both slides read code 47 and the app's mate check names them; the configurations shown after
  it solve. A coupling beside a lock across the same pair reads **no error at all** (left as a caveat: no path of the
  app makes that pair). Findings `CONFIGURATION_SHOW_OVER_DEFINED`, `SUPPRESSION_READ_ORDER`, `VALUE_READ_ORDER`
  (`a75c617`, comments corrected in `6f35d33`). Reviewed in `W8-REVIEW-TIER11.md`, which also found that **Update
  refused a mate it did not make only when it was on in the active configuration**; since `d2f492e` it reads such a
  mate in every mode and refuses before showing anything. The two new findings gate a gearbox with modes (`f87ecc3`,
  `0c49d24`). Tier 9 item 2 of §4.2 (the copied folder) was already W6's `copy_built`.
- **Package E, `s0` and `s1`** (`probe/workbook_assembly_check.py`, `--only modes`; the script reviewed in
  `W8-REVIEW-DEMO-S0-S1.md`, every point in before the run): both pass on SolidWorks 2026 34.0.0 from a snapshot of
  `31f5966` — `probe/results/w8-workbook-assembly-20261115-102101-s0-s1.log`, s0 517 checks, s1 555, 0 failed, no
  STOP. Each mode's flags (the app's read and a raw read in document order, against §2.3), slides, frames, mates,
  interference, a clash control on every mesh and every dog in every mode, the driven proof per mode against the
  key, the both-Flips controls in 4H and 4L (exactly one Flip right, the read naming it), reopen. Facts: every
  coupling was first made with Flip False, read wrong and remade with True on this host (the spike's host had it
  right with False); the drive's global link was accepted with four configurations, so the script's value route
  never ran. Two NOTEs, both the same untitled SolidWorks notification box (texts 'Title', 'Description',
  'Button1', …) coming up mid-run, unanswered: ruled a notification, exempt whenever it appears.
  `s1.master` is in `C:\Users\M0obo\Documents\GearGeneratorProbe\w8-s0s1-20261115-095232\out2\s1.master`.
- **Left:** `s2`, `s3`, `s4` (being written and run); `s5` (W8-REVIEW-TIER11's verdict on ruling 3 says how: the
  doctored distance at a value other than N's own, the balloon tolerated present or absent); `s7`; the window
  check; one full run at the close from the final source; SolidWorks 2024's confirming build; the person's step
  `s6`; PLAN-WORKBOOK §4.5 and UI-DESIGN's last words; the close.
- **Not yet shown on SolidWorks:** `c14e1b2`'s put route (suppress in the configuration shown, then a top-only
  rebuild with no show between), `d2f492e`'s refusal, D10 per configuration, any Update of a gearbox with modes.
- **Small things open:** `tests/test_workbook_planetary.py::test_an_update_on_the_fake_leaves_the_train_turning_as_worked_by_hand`
  still rides on the committed `PLANETARY_PUT_ROUTE` (a one-line pin); W8-PLAN §2.2's sentence on the Checks
  panel's warnings does not match the app (Parallel gives 9, E4 gives 7: `W8-REVIEW-DEMO-S0-S1.md` N5); the NOTE at
  the head of `probe/results/w8-over-defined-attempt-20261115-094752.txt` names the wrong mates for the lock alone
  (`findings.py` has it right); the three tier 11 result files carry SolidWorks' main window title, which names
  the licence edition (asked of the user; the probe now leaves such windows out).
- **On this host the Linux venv has no tkinter** (Python 3.14): two tests fail there for that alone
  (`tests/test_gears_clutch.py::test_the_strip_never_offers_them`,
  `tests/test_ui_text.py::test_the_end_view_readout_always_fits_and_lists_up_to_four_heights`) and pass under
  Windows Python. At `74ac826`: 3112 passed, 10 skipped, those 2 failed.

**To pick W8 up:**

1. Package E writes W8's sections of the demonstration (W8-PLAN §5) — fresh handles after every configuration
   switch; every mode shown and post-checked after a per-mode put, which also settles the one path the review of the
   findings found unmeasured (a put on a gear whose gear mates are on in every configuration).
2. The full build on SolidWorks 2026, fixes, then one confirming build on 2024. On 2024 read once a suppressed gear
   mate's sense on a reopened, unmodified copy: `SUPPRESSED_GEAR_MATE_SENSE_READ` is measured on 2026 only.
3. D's last pass (`14d1125`, `93708d6`) and C's (`45479ea`, `295a214`) had no separate review; A's `5fcaa6a` was
   read by the orchestrating session only.
4. The lesser point left from A's review: a gear mate remade inside a planetary's suppressed put is not read again
   once it is turned back on (`swbuild._put_train`, the comment says so). Reading it again changes W7's call
   sequence, so it waits for a run on SolidWorks.

**Open, for the user to overrule:** making a gear mate of a gearbox with modes again (a tooth change, a sense found
wrong) is refused with a sentence that says to build the gearbox again (ruling 9.16); a slider whose place moves in
a workbook with no Modes rows needs a new revision; the chooser goes to rows above the Speeds lines when its
segments pass the room the header leaves beside the readout (at most 200 px; `b12838d`); the sleeve's and dog's pressure angle is the Box's (20° by default), with no fork groove, hub
or chamfers.

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

4. **Defaults taken while the user was away (2026-11-14 and 15), each to overrule.** They are the rulings of the
   orchestrating session, listed whole in `W6-INTERFACES.md` §7, `W7-INTERFACES.md` §6 and `W8-INTERFACES.md` §9, and
   marked *ruled* in PLAN-WORKBOOK §4.5. The ones a user would notice: W6 — long part names in the Gears table are
   shortened head and tail. W7 — a planetary's gear mates are one per sun mesh and one with the ring from copy 1,
   whatever the Meshes sheet's row order (§6.14); two inputs on a stage are refused (§6.15), as are compound
   planets, a second stage, helical planetaries and a carrier gear that meshes. W8 — the list at the end of *W8 in
   detail*.
5. **Two hand drags** (a person's step the scripts cannot stand in for): G1 in the right-angle gearbox
   (`…\GearGeneratorProbe\w6-full-20261114-210827\out\r1`), and Sun in the planetary
   (`…\GearGeneratorProbe\w7-full-20261115-000138\out\p1`).
   *Both folders are on the machine W5 to W7 ran on, not on the second host of 2026-11-15.*
6. **`tests/fixtures/excel-windows/Planetary_4to1.xlsx`** as Excel saves it was not committed: the session's
   permission check refused the write, and no test or script reads it. Commit it by hand if it is wanted; the file
   is in `…\GearGeneratorProbe\w7-full-20261115-000138\fixtures\`.
7. **Probe folders** under `C:\Users\M0obo\Documents\GearGeneratorProbe` hold over a gigabyte of built gearboxes;
   only the two folders of item 5 are still needed.

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
