# W9d: review of the merge of `workbook` into `w9d`

This reviews merge commit `7ce641e` (parents `cd86232` on `w9d` and `4315774` on `workbook`; merge base `ec50a53`). It also
reviews the script's `cd86232`, which sits just under the merge. No SolidWorks was run. B's footer fix, which is in flight,
is left to B's reviewer.

## Verdict

**The merged tree is fit for the second 2026 run, leaving aside B's footer fix.**
- Nothing of either side is lost, doubled or changed in meaning.
- None of W9d's code, tests or script reads a W9c gate.
- The W9d script's two presses still change nothing with the gates open.
- D5 and D6 degrade to printed facts.

**What was run on the merged tree:**
- The suite: 3977 passed, 10 skipped. The only failures are the two that need tkinter.
- `probe/w9d_demonstration.py --self-check`: 0 failed.
- `probe/w9c_demonstration.py --self-check`: 0 failed.

## Each side kept, nothing doubled

I compared each file's change on each side against the merge. For each file and each side, the change one side made from
the merge base is the same set of changed lines as the merge shows against the other parent:
- `swbuild.py`, `workbook/update.py`, `findings.py`, `tests/test_swbuild.py`, `tests/conftest.py`, `design/UI-DESIGN.md`;
- the two files that conflicted, `ui_text.py` and `tests/test_findings.py`.

So each conflict was resolved by keeping both sides whole. The old all-None W9c test was removed on `workbook` itself, and
`w9d` had not changed it.

In `workbook_footer`, the two calls to `carry_footer_line` are as on `w9d`:
- the state line's call is the one that follows the unsaved line;
- the job-note branch's call is used only for a job's note.

So the carry line cannot be said twice. Every caller of `_unsaved_line`, which takes a new argument, is updated.

## `workbook`'s M3 work beside the carry

**A Build again that carries never passes through `_held_in_error`.**
- `_held_in_error` sits only in `update_gearbox` and `_update_motion`.
- `build_gearbox`, the Build again path, calls neither of them.
- Its `reuse` documents are built in `workbook/gearbox.py` without `left_in_error`, so they keep the default False.

**The two marks on the record do not interfere.**
- `left_in_error` comes only from the record's `unsaved_in_error`. Only `finish_update` writes that, from a failed Update,
  and `keep_in_error` keeps it only while `record.unsaved` holds the path.
- The carry's mark is `CarryEntry.unsaved_at`, a field of its own, cleared by `clear_carry_saved` by its own rule.
- Neither rule reads the other's field, and `workbook` changed neither `store.py` nor `gearbox.py`.
- `read_clean` and the change that says `still_in_error` even on a failed press touch only `unsaved_in_error`.

**Older than the merge, on both sides (a note).** A Build again whose old revision has a part left in error, still open,
reuses that part without the M3 check, because the check is Update-only. The fixture has no part left in error.

**The fake.** `workbook`'s one change to the fake resets the far-branch ring's error codes on a close without saving and a
reopen. It touches nothing the audit set and no knob W9d uses.

## The W9c gates

Five gates are True on 2026: inserting a gear, mates with modes, bands in place, adding a mode, and removing a mode. The
other three are None. Every 2024 value of a W9c or W9d finding is None.

**`findings.py`.**
- Each finding is assigned once, with no duplicates.
- The set of finding names in the merge is the union of both parents.
- Each finding's merged value is what a three-way merge gives from the base and both parents.

**Nothing of W9d reads a W9c gate.** None of these mentions a W9c gate, `in_place_gates` or `w9c_unmeasured`:
- `test_swbuild_carry.py`, `test_workbook_carry.py`, `test_swbuild_user_work.py`;
- `probe/w9d_demonstration.py`, `probe/w9d_probes.py`;
- the carry's code (the only mention there is a docstring).

**The script's two presses still change nothing.**
- **The fixture's quiet press** runs on a workbook equal to its record, so whatever the gates are, it has nothing to write.
- **carry-closed's later Update** comes after Build again recorded `RangeBox_r2` from the edited workbook. Runs 2 and 3
  read it as *"SolidWorks already matches the workbook: nothing was changed"* (run 2 :1179). An open gate gives an
  in-place path only where the workbook differs from the record.
- **The demonstration's edit still needs building again.** It adds the shaft Aux, which the layout part has no axis for.
  The self-check's `up.needs_new_revision and "Flank" in said and "Aux" in said` passes on the merged tree with the gates
  as set.

**The W9c script's functions the W9d script imports are unchanged.** `15bd445` only adds functions and changes
`self_check` and `remake_again`. The functions W9d uses keep the bodies they had: `specs`, `same_sheets`, `edit_live`,
`row_edits`, `interference_judged`, `record_on_disk` and `press`.

## `cd86232`: D4 to D6

**D4 is right.**
- A mode where the component's `GetSuppression2` read suppressed is skipped and said.
- A component suppressed in every mode is "not reached", which FAILs.
- Both cases are self-checked.

**D5 degrades to a printed fact.**
- A frame that will not read is None (`_frames`), and every use is guarded, so it prints "unread".
- The frames all have the shape `pose_gap` takes: the script's own reads, and R's `OldComponent.frame`.
- `judge_carry`'s new lines use no name that is not defined. I checked this by walking its syntax tree, since the
  self-check never runs `judge_carry`.

**D6 degrades to a printed fact.**
- Every way `constrained_names` can fail is caught and said: `CP.swconst` raising, a missing PID, a type library that
  will not load, or a control that disagrees. The statuses then print as plain numbers.
- `status_named` prints a value with no name, including None, as the bare value.

**One weakness in D6 (a note).** `CP.swconst` returns its cache whenever it is already filled. Had anything filled the
cache first without `swConstrainedStatus_e`, D6 would print "unread" without saying why.
- In the W9d run nothing calls `swconst` before `constrained_names`, so this does not bite.
- Clearing `CP.ENUMS` when the enum is missing, or asking for it whatever the cache holds, would make D6 robust.
