# Review of F2-0 (the interface and the probe), before the probe's first run

Read at `dcb1ee7` on `printed`: `20dba07` (the interface), `26049a9` (`probe/f2_probes.py`, `F2-PROBES.md`), `dcb1ee7`
(`F2-0.md`), against PLAN-PRINTED §3 at `a20108b`, the macro database at `/home/m0obot/SW-Macro-Database` and this repo's
ledger. Run here, with `PYTHONPATH=src` (the import path checked): the probe's `--self-check` (103 checks, 0 failed); the
whole suite, **4748 passed, 1 skipped, 1 failed**, the known Tk font-width test
(`test_workbook_window.py::test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left`). `git diff
02b3ff1 dcb1ee7 -- tests` removes no line: no existing test changed, one test added. Nothing was run on SolidWorks.

**Verdict.** The interface is fit for A, B and C to start. The probe is fit to run once one must-fix is in (M1 below, a
few lines): as written it never reads the window of a *part* open in its own window but not active, which is the one
case `PART_WINDOW_READ` exists to tell apart, and a wrong reading there would let the job close a user's window.

## 1. The probe

**How it runs.** On W9a's harness through `w9c_probes`, as W9c's and W9d's probes do: attach by PID, the dialog watch
(`C.watched`: logs, never answers; a dialog that came and went is a `CaseStop` and that step's findings go None; a
dialog that stays or a job over 120 s is `BoxSeen`, a `DemoStop` that `part` re-raises, ending the run with nothing
closed or saved), keep-awake, JSON as it goes, APPDATA in the run folder. `--close-outlived-whats-wrong` is wired as
F1's demonstration wires it (`w9c_demonstration.close_outlived_on`, in force on 2024 only); the command lines give it
for 2024 and not for 2026. Builds are by the app's own routes into fresh folders, so no master is needed.

**Step by step: is each answer a real reading, each proposal printed from it?**

- *Step 1* reads `swSaveAsOptions_e` from the running install's `swconst.tlb`, after W9c's enumerations and their
  positive control (the mate types), and proposes Copy only when Silent reads the app's 1. Real, and controlled.
- *Steps 2 and 4*: `SaveAs` through the same `_out_long()` and `_null_dispatch()` the macro database's verified code
  used, both answer forms handled (a bool, or a tuple whose tail is the codes), both codes named from the enums, the
  file's existence and size, and a bracket (the document's path, title and flag; the active document; every folder
  document's and user document's flag) read before and after. `STEP_EXPORT` is True only when both exports are clean
  and both files pass the frame check. Sound.
- *Step 3* reads the file as text only (GOTCHAS §20). Its parser counts instances, not substrings, reads complex units
  and matches the schema by prefix; the self-check covers each failing way.
- *Step 5* is the determinism control, and step 2's text is kept in memory before step 5 overwrites its file. Good.
- *Step 6* activates the helical part and exports the spur by `use_open_document`'s object. "Right" means equal to step
  2's file but for `FILE_NAME` and not equal to step 4's, under step 5's control; a different text with the same
  geometry is None, not wrong. Sound.
- *Step 8* (the modified part) is facts only, and closing it unsaved is `QuitDoc` on a part, which discards silently on
  both versions (`API-LEDGER.md:98,107,116`).
- *Step 7*: (a) `GetOpenDocumentByName` on a component-only part, with a negative control (a file that does not exist)
  and positive controls in 7d (the part open alone answers its own path; closed answers None), so an API that always
  answers None cannot pass. (b) is the fallback, opened beside then `CloseDoc`, with the assembly's flag, the
  component's state and the user's flags read. (c) is lightweight. (d) gives the reference files and their own control.
  Each proposal is a pure function of what was read, and each judgement's failing ways are in the self-check.

**Could it report clean while the export is wrong?**

- **`STEP_EXPORT` does not look at what the file holds** beyond the frame: the spur's file could hold one closed solid of
  the wrong part, or the wrong size, and still pass. The vertex extent is computed (`extent_holds`) and printed but not
  judged. On the spur, d_a/2 = 16.5 and face 8 are certain vertices. **Should-fix (S1):** require the spur's
  `extent_holds` for `STEP_EXPORT` True, keeping the helical's as a fact. If not done, the reviewer of the run must read
  that fact line before setting the finding.
- **`PART_WINDOW_READ` is proposed without the reading it is for: must-fix M1.** `window_proposal`'s "own window" list
  holds the assembly while active, the assembly while not active, the gear active beside it, and the gear open alone
  and active (`f2_probes.py:1281`, `:1354-1355`, `:1423`). It never holds a **part in its own window that is not
  active**, but that is exactly the part §5.2 of the interface reads it on (the active one counts as own-window
  anyway). If `Visible` or `ActiveView` read otherwise on a background part window, the job would take a user's open
  part for a component, open it "beside" (no new window, only activation) and then `CloseDoc` it, **closing the user's
  window**. The fix is two lines in 7d (`:1411-1418`): after `s.open_document(pin_path)` the gear is open in its own
  window and not active, so read `window_read` of the gear's document there and add it to `windows["own"]`. The export
  section's step 6 offers the same case (the spur, with the helical active). **This blocks the probe's run**: the run is
  per version and the house rule gives one follow-up round.
- Not measured, written as a caveat: a minimised part window, or a document an add-in opened hidden.

**Safety of every call new to the app or to any earlier script.**

| Call | Where | Ledger / macro database | Risk, as written |
|---|---|---|---|
| `IModelDocExtension.SaveAs(…, 0, 1\|2, null, out, out)` to `.step` | 2, 4, 5, 6, 7a-d, 8 | Verified on SW 2026 by the Airfoil Converter on the active part (`API-LEDGER.md:190`, files/04); **unverified on 2024, on a part not active, on a component, on a modified part** | writes only inside `f2-*/print`; step 5 overwrites its own file on purpose; under the watch |
| `ISldWorks.GetOpenDocumentByName` | loaded, 7a, 7c, 7d | **Unverified** (`API-LEDGER.md:94`) | a read; controls both ways |
| `IModelDoc2.Visible` (read) | window reads | **No entry for a document**: `:89` is the application's `Visible`, `:486` a body's | a property get, read only; never set |
| `IModelDoc2.ActiveView` | window reads | Verified on the active document, SW 2024 (`:152`); never on a component-only document | a read |
| `CloseDoc` on a part's own window while an open assembly holds it | 7b, 7c | `:98,107` (parts, no prompt); `:116` the reverse (the assembly closed, parts in windows) on both versions; **this order not measured** | the part is unmodified; the watch |
| `SetSuppression2` lightweight, then resolved, on a component | 7c | used by W9a on RangeBox (`CARRY_RESOLVES_A_LIGHTWEIGHT…` on both versions) | **marks the assembly**, a fact; the assembly is later closed unsaved by `QuitDoc` in 7d; `:113` records one 2024 *Save Modified Documents* box on closing an assembly whose *parts* were changed through it (not this case). A box that stays ends the run with nothing saved, as the watch is built to do |
| `SaveAs` on a lightweight component's document, if `GetOpenDocumentByName` reaches one | 7c | nothing known | **the likeliest step to hang or raise a dialog** (see S2) |
| `Session.activate` on a part, `use_open_document`, `open_document`, `set_global_variable`, `rebuild` | throughout | the app's own routes, both versions | none new |

Nothing is written outside the run's folder: every STEP file goes into the section's `print` folder, the only saves are
the builds' own to new paths, and the user's documents are only read (their flags at each section's start and end;
`users_changed` is self-checked). No path is logged but relative to the run's folder, and no STEP header is logged.
Nothing is left saved or modified: each section ends with `QuitDoc` of its folder under the watch.

**Should-fix S2 (not blocking): run 7c last.** 7d makes the reference files that 7a's and 7b's judgements rest on, and it
runs after 7c. If the lightweight export hangs (`BoxSeen`), 7d never runs, and 7a and 7b come out None though they ran
clean, which costs the follow-up round. Order: loaded, 7a, 7b, 7d, then the assembly opened again, 7c.

**Should-fix S3 (not blocking): units.** `length_unit` refuses a file whose `LENGTH_UNIT` instances differ. But an inch
file written by SolidWorks also holds the SI base unit its `CONVERSION_BASED_UNIT` refers to, so a real inch file
reads unreadable, while the self-check's made-up inch file has one unit only. The app forces millimetres
(`swcom.py:1358`), so the probe will not meet it. B's `check_step` should take the unit the representation context
assigns (`GLOBAL_UNIT_ASSIGNED_CONTEXT`), not every `LENGTH_UNIT`, or the interface's "inch accepted" is not true.

## 2. The interface

**Precise and complete enough to start.** Every name the plan's §3.3 lists is importable with its stub; the codes are
constants whose value is their name, with their detail keys and drafted sentences in one table, so B's tests read codes
and C owns the words (M4). The gate is checked twice by B, in planning and in the job, with `PrintPlan.revision`
catching a SolidWorks that changed since the plan. The reach table (§5.2) is conservative in every row where a finding
is None, and never closes a document it did not open, provided `PART_WINDOW_READ` is measured as M1 asks.

**The files are disjoint**: A `gears/span.py` and `tests/test_span.py`; B `printout.py`, its lines of `swcom.py` and
`swbuild.py`, `test_printout.py`, `test_swbuild_print.py`, and only `FakeSolidWorks`'s members in `test_swbuild.py` and
`export_step` in `test_swcom.py`; C `gui.py`, `ui_text.py`, `workbook_gui.py`, `design/`, `README.md`, `test_ui_text.py`,
`test_print_form.py`, `test_print_window.py`. No package touches `findings.py` or `test_findings.py`. **Nothing machined
and nothing pinned moved**: the diff adds lines only; `test_printed_rule.py` and W9's pins pass; the findings test pins
the eleven new names None and `SAVE_AS_SILENT` and `SAVE_AS_CALL` as they were.

**Should-fixes, none blocking the start:**

- **S4. The build document for an object.** `document_by_path` answers an object, but `export_step`, `has_unsaved_changes`,
  `equations` and `feature_states` all act on the session's build document, and nothing in the interface makes an
  arbitrary object that document (`use_open_document` walks by path, and the walk may not reach a component-only
  document, which the probe asks). B will need a member such as `use_document(doc)` in `swcom` and in the `SolidWorks`
  Protocol. Both files are B's, so this is B's to add and say in its note, but the interface should name it now.
- **S5. One worktree, three agents.** Commits by path keep the files apart, but test runs are not: `swbuild.py` and
  `swcom.py` are imported by nearly every test, so B's edits in progress can fail A's and C's runs. Either give each
  package its own worktree off `printed` (the files are disjoint, so the merges are trivial), or tell A and C to
  believe a failure only on a run when B's files are committed. C's `test_print_form.py` and `test_print_window.py` need
  a fake for the job: write them against the stub `print_parts` or a local fake, not against B's `FakeSolidWorks` while
  B is changing it.
- **S6. A draft sentence's arithmetic** (`F2-INTERFACES.md` §6): *your printer adds 0.041 mm a flank; 0.22 mm a gear…*.
  The formula gives `2 (0.041 + 0.04) / cos 20° = 0.172` mm. C would write a test to it.
- **S7.** `PrintResult.active_restored` defaults to True. B's tests must set it from the job, or a job that forgets to
  put the active document back reads as having done it.

## 3. The twenty decisions in F2-0.md: recommended rulings

1. Three notes: **accept**.
2. `PrintResult` in `printout`: **accept**. The import cycle is real (`workbook.update` → `swbuild` → `printout`).
3. `SolidWorksVersion = Tuple[int, ...]`: **accept**.
4. The extra names (`revision`, `name`, `pressed`, `warnings`, `now`/`exists`, the Protocol lines): **accept**, with S7.
5. `print_bar_line(plan)`: **accept**.
6. No new code for "none connected" or "changed since the plan", only `GATE` with its detail: **accept**.
7. The order of refusals, and one refusal naming every part that fails the first failing read: **accept**.
8. The sentences as drafts, C's to word: **accept**, with S6.
9. **A feature warning does not refuse; an error does: accept.** SolidWorks built the geometry it warns about, and the
   file is what it built; the warning is named in the result and the list. The probe does not measure this, and needs
   not to: it is a read the app already makes (`feature_states`).
10. **The extent check skipped as a fact for bevel gears, rings, sleeves, dogs and hubs, and for any part holding the
    user's features: accept.** Their outer radius or length is not d_a/2 and the face, and a false refusal there would
    stop a good print. It is still a refusal on external spur, helical and herringbone gears, if step 3 bears it out.
11. `SAVE_AS_COPY` one name, set when both runs agree: **accept**.
12. **`PART_WINDOW_READ_ON_<year>` as a sixth finding: accept, with M1.** Nothing else tells a part open in its own window
    from one loaded only as a component: `OpenDoc6` answers warning 128 for both (`API-LEDGER.md:114`), and the walk
    reaches both. Without the finding the fallback could close a user's window. While it is None the reach table
    refuses rather than guess, which is right. It must be proposed from a reading of a non-active part window.
13. **Lightweight handled only by the open-beside fallback** (a part not found while an assembly is open is opened
    beside only when `OPEN_BESIDE…` is True, else refused): **accept**. The job never changes a component's state, and
    both component findings are proposed True only if 7c covers the lightweight case. It refuses some parts that are in
    no open assembly while `OPEN_BESIDE…` is None: the right side to err on.
14. `document_by_path`'s route left to the probe's review: **accept**, with S4.
15. The probe's stricter judgements (the frame check in `STEP_EXPORT`, "cannot tell" as None, a marked start as None):
    **accept**, and add S1.
16. The probe's shapes (helical face 10, the spur activated before step 8, 7 split (a) to (d), the old step 8 not run):
    **accept**, with S2's order.
17. Nothing personal in a log, the STEP files never committed: **accept**. The run's reviewer should check the run
    folder is not added to git.
18. The β 30° row at face 14, and Coupon_E as module 1.5, z 20 for a large shaft: **accept**, and put the same sentence
    in PLAN-PRINTED §3.2 (the coordinator's edit).
19. `toothed_width` for the plan's `half_width`: **accept**; correct the plan's citation.
20. W9a's `main` starting its own Excel: **accept** as it is. It is the harness's own Excel, quit at the end, as in every
    W9 run (house rule: only an Excel the run starts).

## 4. Must-fix and should-fix

| | Point | File and line | Blocks |
|---|---|---|---|
| **M1** | `PART_WINDOW_READ` proposed with no reading of a non-active part in its own window; add one in 7d after the pinion opens (and, if wanted, in step 6) | `probe/f2_probes.py:1411-1418`, `:1423` | **the probe's run** |
| S1 | `STEP_EXPORT` True only with the spur's extent holding | `probe/f2_probes.py:418-428`, `:1135` | neither (else the run's reviewer reads the fact) |
| S2 | run 7c after 7d | `probe/f2_probes.py:1405-1436` | neither |
| S3 | the length unit taken from the context, not every `LENGTH_UNIT` (inch files) | `probe/f2_probes.py:217-243`; B's `check_step` | neither |
| S4 | a member that makes an object the build document, named in the interface | `F2-INTERFACES.md` §4, §5.2; B's `swcom` and Protocol | neither (B's to add) |
| S5 | test isolation of three agents in one worktree; C's job tests not on B's changing fake | process; `F2-INTERFACES.md` §8 | neither |
| S6 | the Measured line's draft example (0.172, not 0.22) | `F2-INTERFACES.md` §6 | neither |
| S7 | `active_restored` defaulting to True | `printout.py`, `PrintResult` | neither |

**A, B and C may start now.** **The probe may run once M1 is in**, with its self-check run again (it should gain a check
that a non-active part window is in the own-window list).

## Re-check of `9f97e01` (the probe to this review), 2026-11-18

**M1 is fixed at its cause.** `window_proposal` now takes a third list, *background*: parts open in their own window
but not active. It proposes a read only when that read is True on every one of them as well as on the active documents,
and False on every component-only one, and it proposes None when the list is empty. The new readings are real: in step
6 the spur's window is read with the helical active, and in 7d the gear's window is read after the pinion is opened
(`open_document` raises if the pinion is not then active, `swcom.py:3606`). The active document is logged beside each.
The self-check holds the failing ways: no background reading gives None; a background `Visible` False rules `Visible`
out; a background part read as a component by both reads gives None. **S1:** `STEP_EXPORT` needs the spur's
`extent_holds` True, with the helical's left a fact; the cases "wrong size" and "not read" are each None and
self-checked. **S2:** 7c now runs last, on the assembly opened again. 7a's and 7b's files are judged, and
`PART_WINDOW_READ` proposed, before it. The two component proposals still come after 7c, as they must, since each is
True only if the lightweight case is covered. **Nothing else moved**: the diff is these changes, the docstring and
`F2-PROBES.md`. The self-check gives 109 ok, 0 failed. **One small should-fix, not blocking:** step 6's background
entry does not check that the helical really became active (`Session.activate` does not verify). If it had not, that
entry would be a reading of an active window. 7d's entry is guarded, though, and the proposal needs every entry True,
so the proposal still rests on a real background reading whenever 7d runs. The reviewer of the run should read the
`active` label logged with each entry. **Fit to run unattended**: on SolidWorks 2026 as written, then on SolidWorks 2024
in a fresh session with `--close-outlived-whats-wrong`.

## Re-check of `b49044f`, `e3dc598` and `d333ff8` (the probe after its first runs, `8d2c5fb`), 2026-11-18

**The geometry comparison is sound for what it judges.** `same_part` reads the DATA section only and requires three
things within 1e-4 mm: the same count of every entity kind, the same `CARTESIAN_POINT`s one to one (every vertex,
control point and placement origin), and the same circle, cylinder, sphere and torus radii.

- **Can it pass two different parts?** Not among the ones the probe can meet. Any change of size or shape the app makes
  moves a vertex or a control point by the whole change, or alters the counts. The probe's alternatives are the other
  document (helical, pinion: other counts) or another state of the same document (the 9 mm spur: a whole face moves 1
  mm). It does not compare directions, B-spline weights, ellipse axes or cone angles, so it is not a general test of
  equality. Package B must not lift it into the app as one.
- **Can it fail the same part exported twice?** Not on the evidence. The 2026 spur's tip vertex is 0.001185 mm over
  nominal (16.501185; 2024 writes 16.500000) and its face 8.000031. Those are the kernel's distances from the *design*,
  the same in every export of the document, not differences *between* exports. The runs' own files agree exactly
  between exports: the spur twice, the gear twice, and 7a's and 7b's files against 7d's reference across a close and
  reopen (4698 and 10946 points on 2026, 4429 and 10265 on 2024; `F2-PROBES.md`). So 1e-4 is safe. Were a reopen ever to
  regenerate a part, the kernel's 1e-3 scale could show here as a false "not the same part". That errs safe: each
  finding then sends the job to activation, the fallback or a refusal, never to a wrong export.
- **The controls are real.** Two positives (2 against 5, 7d's gear twice) and three negatives (spur against helical, 8
  mm against 9 mm, gear against pinion) are read in the run itself. No file is judged unless both sections' controls
  held, and a control not read does not hold. The negatives are coarse (other counts, or a 1 mm move), but they are the
  wrong answers the judged steps can actually give. The self-check holds the edges: a 5e-5 mm move the same, 5e-4 not, a
  radius changed by 0.001, a renumbered and reordered file the same.

**The lightweight reading is sound.** `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN` is proposed only for a component read fully
resolved before 7b. Both runs read state 2, `swComponentFullyResolved`. 7c's beside path, the assembly's flag after
its close and the component's state are now facts. `STEP_EXPORT_FROM_COMPONENT` still needs the lightweight part not
reached by the object route, which both runs found. One small point for B, not blocking: the interface takes
lightweight as state 1. Reading `swComponentFullyLightweight` (4) as lightweight too costs nothing.

**e3dc598** activates the spur before step 8's change, as decision 16 said, and changes nothing else. The self-check
gives 125 ok, 0 failed.

**The app's routes.** Every write of an equation or global in `src/` is made on a document the app has just made
active or has just created. No route writes one on a document reached without activation.

- The gearbox Update's value step opens the part first (`swbuild.py:4151`, `open_document`: `OpenDoc6`, then
  `ActivateDoc3`, checked by path at `swcom.py:3606`). `update_variables` then refuses unless the active document is
  that part (`:1431-1440`), and the form's Update values goes through the same `update_variables`.
- The bands open the sleeve's part first (`:6399`, then `:6406-6408`).
- The assembly-level Face Z globals and an added gear's globals follow `open_document(assembly)` (`:5027` for
  `:5073`, `:9818` for `:9876`, `:6668` for `:6682-6700`), with no other document activated between.
- The build writes into the part or assembly it has just made (`:425`, `:432`).
- The three non-activating `use_open_document` calls (`:6935`, `:7791`, `:8266`) only read the old assembly.
- `set_global_variable` reads its put back and raises when it did not take (`swcom.py:1455-1470`). That is how the
  probe's run 1 failed loudly rather than silently, so a route that broke this rule would refuse, not write the wrong
  value.

**Fit to rerun unattended** on SolidWorks 2026, then 2024 with `--close-outlived-whats-wrong`, the command lines as in
`F2-PROBES.md`.
