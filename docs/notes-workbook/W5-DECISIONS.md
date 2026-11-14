# W5: the user's answers and the orchestrator's rulings on the plan and its review

Read in this order: `docs/PLAN-WORKBOOK.md` (the authority), `W5-PLAN.md` (the implementation plan),
`W5-PLAN-REVIEW.md` (its independent review), then this file. Where they disagree, this file wins over the
review, the review over W5-PLAN, and PLAN-WORKBOOK over all three unless this file says a reading was chosen.
Written 2026-11-14 while the probe batch the review asked for (package P0) was still running; what depended on
its findings is ruled on in the later sections, added the same day as each probe round was committed and reviewed.

## The user's answers (2026-11-14)

1. **A refused mate stops the build and says why** (review M6, option A; overrules D2). No static assembly is
   made in its place. The parts and the layout part the job built are kept and recorded, as W4's continued
   revision keeps them; no assembly is saved; the sentence names the mate SolidWorks refused or flagged. The
   next Build makes the assembly once the workbook has changed. The footer never invites a retry of an
   unchanged workbook. The refused document: closed by the job only if a probe shows that is safe on 2024
   (`probe/scaffold.py:120` shows the hang); otherwise left open and named, with the sentence saying its parts
   are the saved ones.
2. **Update returns a train the user turned to its built position whenever it has to move any gear** (D4
   stands, with M1's rule below). With nothing to put, the train stays where the user turned it. The footer
   says so plainly when it happens.
3. **No datum plane: the first gear's place along its shaft is measured from the Front plane** (D8 stands;
   review M5's alternative is declined — an extra plane in the layout part is not wanted for geometry that is
   not part of the specified gear train). So an anchor's front face reaching, leaving or crossing the Front
   plane is structural (Build again…), which includes a face-width or `At` change on an anchor whose front face
   sits on the Front plane, as G1 and G2 of the 12 : 1 do. The sentence names the edit ("G1's face width
   moves its front face off the Front plane…"), never only the plane. Probe `axial_datum_plane` is recorded
   for the record and nothing is built on it.
4. **The Checks panel stays as built: problems only**, a clean workbook saying so in one line
   (`design/UI-DESIGN.md`, "Where it differs from PLAN-WORKBOOK §5"). PLAN-WORKBOOK §5's "then the passed
   checks, one line each" is not built.
5. **Document titles in old probe results are scrubbed going forward** (`ee46d20`); history is left as it is.

## Rulings on the review

- **M1 accepted.** When a train needs any put, every mated gear of that train is put, unconditionally. Locks are
  tested exactly (δ_follower ≡ δ_anchor, to tolerance), never modulo a pitch; "modulo pitch" stays for meshes
  only. A fake test covers the one-tooth scenario the review describes.
- **M2 accepted.** `k == ω_b/ω_a` and `δ_i = 30°·ω_i/ω_in`, speeds about each shaft's own axis. The Risky
  values (+0.7, +0.636364, −0.388889) are pinned.
- **M3 accepted.** The interface commit starts on the commit that closes W4 (the rebuild fix, its review's
  changes, and the demonstration reruns on SolidWorks 2026 and 2024), named in `W5-INTERFACES.md`.
- **M4 accepted**, and widened: package P0 probes the ratio change (P1), the lock re-taken after a move along
  the shaft (P2), renaming each kind of mate and finding it by name, the demonstration's drive, a put on a gear
  in two gear mates, the datum plane (probed before answer 3 was given; not used), and — from the review of probe `assembly_rebuild_scope` — which rebuild a
  mated assembly needs and what it marks modified (`MATED_ASSEMBLY_REBUILD_ROUTE`). Until that last finding
  is set, every mated assembly rebuilds in full (`ForceRebuild3(False)`), as tiers 4, 5 and 8 proved it.
- **M6** is answer 1. **M5** is answer 3: declined, with its last point kept (the sentence names the edit).
- **M7 accepted:** in the check phase, a mate the record does not know that touches a gear refuses the Update
  before anything is changed, naming the mate ("suppress Angle1 and press again").
- **M8 accepted:** locks are unsuppressed in a `finally`; if that fails, the failure sentence says which
  compound gears are not locked.
- **M9 accepted:** a gear on a shaft whose solved speed is 0 through a fixed shaft is left fixed; the plan's
  "a fixed–turning mesh is jammed" claim is reworded.
- **M10 accepted:** ratios are computed in the record's gear order for each mesh entry, the pair matched
  unordered to the new Meshes rows.
- **M11 accepted:** "the rest of its train follow"; the fallback sentence no longer exists (answer 1).
- **M12 accepted** as written (set Drive back before deleting the control mate; check every frame against the
  built frames to 1e-6; before any save, assert no Drive global, angle mate or control mate is left and no lock
  is suppressed).
- **M13 accepted:** the loop test uses one internal mesh, or two meshes between the same two shafts.

## Rulings on package P0's findings (2026-11-14, after their independent review)

P0 is commits `0d638db` to `8504856`; the findings are in `findings.py` from "tier 8 items 7–13".

- **D8's follower case: an Update.** `LOCK_RETAKES_AN_OFFSET` is True on both versions, and the measurement
  tells a working lock from a dead one (11° and 3 mm kept through a drive; a dead lock would have read 18.5°).
  A follower's `At` or face-width change is carried by Update. The anchor's Front-plane cases stay structural
  (answer 3).
- **D7: a tooth change stays structural (Build again…) until probe P1b passes.** `GEAR_MATE_RATIO_ROUTE` is
  None. Changing the gear mate's definition in place works on 2026 and leaves an assembly SolidWorks 2024
  cannot close, so it is never used on either version. Deleting the gear mate and adding it again ("remake")
  gave the right ratio in the right sense on both, but on 2024 it has only run in a session that already held
  an assembly it could not close, and never in the shape an Update needs. P1b, in a fresh session on each
  version with the remake first: the part's teeth changed through its globals; locks suppressed, the gear mate
  remade and renamed, every gear put to its built frame; locks on, rebuild, drive at the new ratio,
  interference; close without saving and reopen; and the same on a gear that carries two gear mates. Both
  branches of D7 are coded and tested against the fake, as W5-PLAN says; only `"remake"` or None can be the
  finding, and code refuses `"modify definition"` with a sentence.
- **A lock does not hold against a put.** With the lock on, a `Transform2` put moved one gear, its locked
  partner did not follow, and SolidWorks reported nothing (both versions). This agrees with M1 and M8 — the
  app only ever puts with every lock of the train suppressed — and it changes the fake: its `place_component`
  must take a put on a locked gear silently and leave the partner where it was, as SolidWorks does, so a test
  can catch a put made with a lock on. What the lock does on its next solve after such a put was not measured
  (no drive followed); nothing may be built on it.
- **The train's rebuild: top-only (`ForceRebuild3(True)`) for Update, on probation for Build.**
  `MATED_ASSEMBLY_REBUILD_ROUTE` re-solved a changed global and a drive on a built, saved, reopened train and
  marked only the assembly, on both versions. Not yet shown: a train *built* under the top-only rebuild (the
  probe's train was built with the full one), a drive after a layout move under it, and 2024 in a session with
  no stuck assembly holding the shared layout and part. Probe round P0b adds those. Code passes the train kind
  for Build and Update alike; if P0b shows the build needs the full rebuild, the build gets its own kind in
  `swcom.rebuild_call` (package A's file) and nothing else changes. The demonstration (package E) does not run
  before P0b is committed and reviewed.
- **Mates are found by walking the mate group** (`MATE_FIND_ROUTE`), named by an `IFeature.Name` put
  (`MATE_RENAME_ROUTE`), all four kinds, both versions. The demonstration's drive holds and returns every gear
  to its built frame (M12 stands as written). A put on a gear in two gear mates holds.

## Rulings on probe round P0b (2026-11-14, after its independent review)

P0b is commits `10fb0d4`, `61d390e`, `4ced012`, `771c8eb` (results) and `4f865d8` (findings). Its review found
no must-fix: the 2024 evidence now comes from fresh sessions in which the remake ran first and nothing was
stranded beside it (`sw2024/probe-results-20261114-071324`), with the definition route alone in its own session
(`…-073328`), and the two differences between the versions that P0 had read are gone.

- **D7: a tooth change the globals carry is an Update, by the remake.** `GEAR_MATE_RATIO_ROUTE` is `"remake"`.
  Probe `gear_mate_update` carried it in an Update's shape on both versions: teeth changed through the part's
  globals, every lock suppressed, the gear mate deleted, made again at the new ratio and renamed, every gear put
  to its built frame, locks on, a top-only rebuild, the mate checks, a drive at the new ratio and sense (2.7°
  for 30°, where the old ratio gives 2.5° and the inverse about 20.8°), no interference, an unsaved close that
  left the file as saved, and a save, reopen and drive. `"modify definition"` is never used on either version.
  **Accepted with one gap:** on a gear that carries two gear mates the remake was driven and measured
  (`put_on_twice_meshed_gear`) but not in the whole Update shape (no tooth change in the parts, no puts, no
  interference, no unsaved close). A probe step on a train with an idler is asked of round P0c; until it is
  committed the demonstration's tooth change is on the 12 : 1, which has no such gear.
- **A train's Build may use the top-only rebuild.** `MATED_BUILD_REBUILD_ROUTE` is `"ForceRebuild3(True)"`: a
  train built with it as its only rebuild matched the full rebuild's train frame for frame and drove at its
  ratio, and its build marks nothing but the assembly, where the full rebuild leaves the layout and the part
  marked. The app has one route for the train kind (`swcom.rebuild_call` reads
  `MATED_ASSEMBLY_REBUILD_ROUTE`), so a train build refuses, before anything is made, when the two findings
  differ (package A's gate).
- **The lock against a put, measured:** after a put with the lock on, a drive turned both gears together with
  the relative angle the put left — the lock took the new angle and held it. The app still never puts with a
  lock on (M1, M8).

## Rulings on probe rounds P0c and P0d (2026-11-14, after their independent review)

P0c is commits `59910e0` to `c66d321`; its review found no must-fix and asked for three things to be read
again and four comments reworded, which round P0d did (`5667999`, `ed2fdc4`, `b2162a5`, `26cbf9c`). Both rounds
ran on SolidWorks 2026 and 2024, each started fresh, and read the same on both.

- **A tooth change on a gear that carries two gear mates is an Update** (`IDLER_UPDATE_HOLDS`). This closes the
  gap P0b's ruling left: on a train with an idler, the teeth changed through the parts' globals, both of the
  idler's gear mates were deleted, made again and renamed, every gear put, and the train drove at the new ratios,
  closed unsaved as saved, and reopened saved with the new teeth. Package A's Update refuses such a remake,
  before anything changes, while that finding is missing.
- **Interference is judged against a control.** At the old phase a changed train can happen to show no clash, so
  the demonstration's control is a gear put half a pitch off its new phase (`UPDATE_INTERFERENCE_CONTROL_HOLDS`).
- **The Update check may read every gear mate's ratio.** Reading a gear mate's definition marks no document
  (`GEAR_MATE_DEFINITION_READ_MARKS`), so an Update with nothing to do still changes nothing. The check reads it
  only while that finding says "nothing".
- **Mates may sit in folders.** A folder shows in the mate group's walk as two entries of type "FtrFolder" with
  the mates between them as ordinary entries, found by name; this held with a folder inside a folder, after a
  save and reopen, and with the folder suppressed (which suppresses the mates inside). A turning Update skips
  entries of that type and still refuses any other entry that is not a mate. A remade mate lands at the end of
  the mate group, outside its folder, and is left there. Not probed: turning a mate back on by itself while its
  folder is suppressed; the app must stop with a sentence if the mate still reads suppressed.
- **A turning Update refuses while a gear is loaded lightweight.** Forced lightweight, a train's first drive
  turned one gear wrongly and only then were its components resolved (`LIGHTWEIGHT_FIRST_DRIVE_RIGHT`,
  `LIGHTWEIGHT_RESOLVED_BY`). The app does not resolve components itself; it reads each gear
  (`COMPONENT_RESOLVED_ROUTE`, `COMPONENT_FULLY_RESOLVED_STATES`) in the check phase and says how to resolve
  them in SolidWorks. A plain open on this machine reads every gear resolved.
- **Mates are made with `CommandInProgress` on and renamed straight after they are made**
  (`MATES_UNDER_COMMAND_IN_PROGRESS`, `MATE_RENAME_AT_ONCE`); a train Build reads both findings first.
- **A lock that already reads on is never turned on again:** the call marks the assembly modified
  (`UNSUPPRESS_ON_LOCK_ALREADY_ON_MARKS_MODIFIED`). A suppressed mate reads error code 0 whatever it would
  report when on, so nothing judges a suppressed mate by its code.
- **The refused assembly stays open and is named** (answer 1 as built). A second new assembly beside it holds
  (`SECOND_ASSEMBLY_BESIDE_UNSAVED_HOLDS`), but no probe closed a new, never-saved, refused assembly on 2024
  under a watch for a dialog, so the job does not close it.
- **An unsaved Update can be closed without a question on both versions** (`UNSAVED_UPDATE_CLOSE_ASKS`), with
  the changed parts open in their own windows as Update leaves them. The app still closes nothing itself.
- **The "moved" tolerance of 1e-6 mm stands:** origins read 0.0 mm apart around a top-only rebuild and 2.8e-14 mm
  across a temporary drive (`ORIGIN_NOISE_MM`).
- **The demonstration keeps its temporary driving mate.** The drag operator, called as the macro database's
  entry calls it, turned only the dragged gear on these trains (`DRAG_OPERATOR_TURNS_TRAIN`); what differs from
  that entry's own success (the mate kind holding each gear, an internal mesh, the angle) was not varied. The
  person's drag in SolidWorks remains the check that a mouse turns the train (W5-PLAN §4.4).

## Rulings on the ring probe and its follow-up (2026-11-14)

The first demonstration passed on SolidWorks 2024 and failed seven checks on 2026, all one fault: the ring of
Risky_Placements turned the wrong way (`w5-workbook-assembly-20261114-112629.log`, section m3). Probe
`ring_mate_sense` isolated it (`ad08864`, results `566b8b4`, findings `79e5341`); the follow-up round read the
footing of the fix (`5fcbdc3` to `5a57837`, results `9b382df`, findings `9afe65b`).

- **No Flip is chosen from the plan.** Every toothed ring probed needs the opposite Flip on the two versions,
  and which one depends on the ring (`GEAR_MATE_FLIP_NEEDED_ON_2026`, `_ON_2024`, and the `_MORE_` tables:
  helical and herringbone rings one way, spur rings the other). `GEAR_MATE_FLIP_STATIC_RULE` is None and
  `GEAR_MATE_FLIP` stays False as the first try. An external pair needs False on both versions in every shaft
  sense probed (++, --, -+).
- **Every gear mate is read back, and a wrong one is made again with the other Flip.** Right is
  `(Reverse == the two entities' directions parallel) == internal` (`GEAR_MATE_SENSE_READ_BACK`); the read
  agrees with what a drive does straight after the mate is made, after the rebuild, after a remake and after a
  save and reopen (`GEAR_MATE_SENSE_READ_POINTS_AGREE`). A mate that reads wrong both ways round stops the job
  as a refused mate (answer 1); there is no static fallback and the old mate is not put back.
- **The record does not carry the Flip.** What is on record is the ratio; the sense is read from SolidWorks each
  time, so a file saved by the other version needs nothing converted. A train saved by 2024 and opened in 2026
  keeps its stored Reverse, reads right and turns right with no remake (`CROSS_VERSION_READ_BACK_TELLS_SENSE`,
  `CROSS_VERSION_RING_TURNS_RIGHT`).
- **Update's check phase reads every gear mate's sense** now that the read is known to mark no document
  (`GEAR_MATE_SENSE_READ_MARKS`). This closes the must-fix of package B's review: after an Update stopped on a
  mate wrong both ways, a second press no longer takes that mate as already right. A mate found wrong is made
  again and the window says so (`sense_found_wrong`); the remake a build makes itself is not mentioned
  (`turned_round`). An interim rule that would have remade every gear mate on every Update was refused: it would
  have ended the "already … left as it is" case.
- **Build reads and remakes inside `CommandInProgress`**, as the probe did
  (`GEAR_MATE_SENSE_READ_UNDER_COMMAND_IN_PROGRESS`, `GEAR_MATE_REMAKE_UNDER_COMMAND_IN_PROGRESS`), and Update's
  remake at a new ratio is read back the same way (`GEAR_MATE_READ_BACK_HOLDS_AFTER_A_RATIO_REMAKE`: on 2026 the
  ring mesh read wrong after the remake, was made again and then turned right). A train Build or a remake
  refuses, before anything changes, while one of these findings is missing.
- **Closing a changed assembly of an older version in 2026 can raise the CAM add-in's "Save changes?" box**
  (`CROSS_VERSION_CLOSE_ASKS_TO_SAVE`; Yes and No only, on this machine). The app closes nothing itself, so no
  code follows from it; probes and the demonstration answer No.
- **Seen on the way, not W5's:** the app took a +0.3 shifted pinion inside an unshifted ring at the unshifted
  centre distance, and its build then reported a clash of 1.38 mm³. The build's interference check caught it;
  whether the Checks panel should say so before a build is a question for the user.

The follow-up round's independent review found no must-fix: every finding the app depends on is supported by
both versions' result files, and "marks nothing" was read on the assembly, the layout and every part. What it
asked to be written down, and is not run again (the rule of 2026-11-14):

- On 2024 the remake under `CommandInProgress` only ever went from a right gear mate to a wrong one; the app's
  direction, wrong to right, was shown under it on 2026 only. The first mate made under `CommandInProgress` was
  deleted before any drive, so its read is right by comparison (the same read with it off, and the opposite of
  the remade mate's), not by a drive.
- In the Update-shaped remake at a new ratio, 2026's first "wrong" was the read-back's word alone; the train was
  driven only after the second remake, when it read right and turned right with no clash.
- The probe read the ratio and the reference component on top of the app's sense reads; "marks nothing" holds
  for that larger set.
- The cross-version evidence is 2024-saved trains opened in 2026. 2024 cannot open a 2026 file.
- The CAM add-in's box came up on closing a 2024 assembly the probe had changed, on this machine; a same-version
  unsaved close asked nothing (P0c). It is tied to the file's version and to the add-in, not to `CloseDoc`.
- The two versions' `ring_trains_saved` runs came from different probe commits (2024 at `498f248`, 2026 at
  `3176557`); the difference between them is how the remake verdict is judged, and the raw readings agree.

## Rulings at W5's close (2026-11-14)

- **The run that closes the phase** is the full run on SolidWorks 2026 from `9afe65b` (`0514c26`), together with a
  rerun, from the final source (`d99654a`), of every section whose path the later commits changed: m1, m6, m8, and
  m5, a, a3. The last review asked for the last three, or a ruling; they were run. SolidWorks 2024's confirming run
  is m1, m3, m7, m8, the window check and the cross-version open, as the user's rule of that day says.
- **The Flip a new ring gear mate needs is not predicted, on either version, from anything.** On 2024 one made
  straight after an Update had moved its pinion 2 mm along its shaft and put the train needed Flip True, where one
  made after the build and a reopen, pinion unmoved, needed False; the mate made at the build still turned the ring
  right after the move. Whether the move, the Update's puts and rebuild, or the missing reopen changed it was not
  separated, and is not probed: the app reads back every gear mate it makes or remakes, so nothing depends on the
  cause. Section m8 is that path run by the app on both versions.

Caveats of the demonstration's two reviews, written down and not run again:

- "Read back wrong, then turned round" for the remade ring mate in m8 is the app's own result; SolidWorks shows the
  end state (the drive at 15 : 37, the interference control, the both-Flips control).
- Section c builds the Risky gearbox without driving it, so its `turned_round` there is the app's word; m3, m7 and
  m8 drive the ring.
- On SolidWorks 2024, m2, m4, m5, m6, a, a2, a3, b and c were not run on the final source (they passed there on the
  first demonstration, before the ring fix); m6's suppressed mate folder ran on 2026 only.
- a3's typed-back quiet Update checks frames and a drive but does not assert the save flags.
- The 2026 reruns of m3 and m7 with the both-Flips control ran in the same session as the main run, not a fresh one.
- Not shown through the app on either version: an idler's tooth change (probe P0c showed the steps), the
  lightweight refusal, a fixed shaft, a loop-closer, Update on a pair's assembly.
