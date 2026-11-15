# Review of package A's W8 fixes: `c48b6ef`, `ff1c4dd`, `c14e1b2`, `03a4e51`

*Independent, 2026-11-15, read only on code.* Under review: the four commits that answer `W8-REVIEW-LATE-A.md`
(points 1–3 ruled "fix", its item 4 ruled "leave as a caveat") and the app fault W8 s0's first SolidWorks 2026 run
found. That fault: `IFeature.IsSuppressed2(3, names)` answers in the document's configuration order, filtered to the
names asked, whatever order they are passed in, and `swcom.Session.mate_suppression` paired the answers with the
order passed (`probe/results/w8-configuration-order-20261115-092100.txt`,
`probe/results/w8-workbook-assembly-20261115-091456-s0-stopped-by-an-app-fault.log`). Line numbers are at `03a4e51`.

**Verdict.** Sound. All four commits do what their messages say:

- On a gearbox with modes, every suppress, read and restore around a put goes through the measured per-configuration
  calls, naming the configuration shown and no other.
- A gearbox without modes makes exactly the calls it made.
- The read after the last mode compares against the right on-set and says each wrong flag once.
- `mate_suppression` reads one name per call, which is what the evidence shows answering right.
- The build's sentence now says what was read.

Every mutant I tried on the new behaviour was caught except one (point 5). Nothing below is a must. One thing should
change: the order finding is in a results file and in docstrings, but not in `findings.py`, and `findings.py` and
`W8-SPIKE.md` still state the old conclusion (point 1). The rest are notes. Point 2 is the one the SolidWorks run has
to answer.

---

## Points

**1. Should fix (records, not code): the order finding is not in `findings.py`, and two records still say the
opposite.** `findings.py:1168-1169`, `:1177`; `W8-SPIKE.md:102`; `swbuild.py:4215`, `:4924`.

- *What stands.*
  - `findings.py:1168-1169` reads *"IsSuppressed2(3, names) gave one flag per name, in order, as set"*.
  - `W8-SPIKE.md:102` reads *"One flag per name, in that order"*.
  - The spike asked `["Default", "X", "Y"]`, which happened to be the document's own order, so its reads were right
    but the conclusion does not hold in general. The 092100 reads show three orders of the full list answering
    identically.
- *What the app now depends on.* One name per call, measured only in the 092100 results file (`['N'] -> (True,)`,
  `['2H'] -> (False,)`) and cited only in `swcom.mate_suppression`'s docstring. The house rule is that the app
  depends on calls a probe measured, read from `findings.py`. Today a later reader of `findings.py` would find the
  multi-name read described as safe, and could put it back.
- *Stale docstrings.* Two in `swbuild` still describe the read as `IsSuppressed2(3, names)`:
  - `_modes_flags_after`, `:4215`;
  - `_put_train`'s `configuration` paragraph, `:4924`.
- *Change.*
  - Under `MATE_SUPPRESSION_PER_CONFIGURATION_ROUTE`, add a dated comment with the 092100 reads:
    - several names answer in `GetConfigurationNames` order, filtered;
    - one name answers its own flag;
    - `GetSystemValue3(3, names)` answers in the order passed;
    - so the app asks one name per call.
  - Amend the spike line and the two docstrings to match.
  - The route string can stay as it is. `configuration_finding` compares it verbatim, and changing it would change
    the gate.
  - Whoever owns `findings.py` at the moment should make this edit; I was told another agent may have it open.

**2. Note (for the run, not for code): the put route now suppresses with `SetSuppression2(…, 3, [active])` and then
rebuilds without a show. No probe has run that sequence, though a failure would show.** `swbuild.py:4940-4944`,
`:4952-4960`.

- *Why it is new.* `PLANETARY_PUT_ROUTE` was measured with the this-configuration call.
  `MATE_SUPPRESSION_PER_CONFIGURATION_ROUTE` was measured for flags. Every place the app has used it so far has had a
  show between the set and the geometry it relies on:
  - the build's step 5 sets the flags, and step 6 shows each mode;
  - Update's D10 sets the flags before the mode loop, and each mode is shown and rebuilt before its put;
  - the spike's geometry was read only after `ShowConfiguration2`.
- *What `c14e1b2` relies on.* That a per-configuration suppression naming the active configuration takes effect at
  the next top-only rebuild, so that the carrier put holds (without it, the 6.2° pull-back of
  `PLANETARY_PUT_ROUTE`'s route A).
- *Why it is only a note.* This trades point 1 of the late review for a smaller unknown, and the trade is a good one.
  The old unknown, a leak into other configurations, would have been silent. This one would be loud:
  `place_component` reads every put back, and `_modes_post_check` judges every frame to 1e-6. If it fails, the
  Update stops naming the gear, and no flag is left wrong (I traced every exit path; see *Checked*).
- *Change.* Nothing in code. The run below must show it.

**3. Note: an answer of `None` for one name now reads as "on", and nothing catches it.** `swcom.py:2966-2973`,
`_per_name` at `:467-474`.

- *Before.* A multi-name ask answered with a scalar or `None` gave `_per_name(...) == [None]`. Its length differed
  from the number of names, so the read raised a sentence.
- *Now.* Every read asks one name, so `[None]` has length 1 and `bool(None)` is `False`, which reads as not
  suppressed.
- *Where that would bite.*
  - `set_mate_suppressed_in(…, False, …)`'s read-back passes.
  - `_put_train`'s read before the restore (`swbuild.py:5020`) skips the restore. The mode's post-check, which reads
    through `IsSuppressed2(1, …)`, would then say *"is suppressed in SolidWorks, where this mode has it on"*. So it
    is said, but the mate is left off.
- *Why only a note.* No probe has seen `IsSuppressed2` answer `None`. It answered a tuple every time, and once a
  doubly wrapped one, which `_per_name` unwraps. The app passes only names it read from `GetConfigurationNames`.
- *Change, if wanted.* Take an item that is neither `bool` nor `int` as no answer:
  `if len(flags) != 1 or not isinstance(flags[0], (bool, int))`. That reaches the same sentence. The sentence would
  then need *"gave no flag"* in place of *"gave 1 answer"* for that case.

**4. Note: what the change costs in calls.** `swcom.py:2957-2996`.

- *`IsSuppressed2` calls.* They grow with mates × configurations, never with the square of either. I counted them on
  HEAD's swbuild call lists, once with one call per read (the reader before `03a4e51`) and once with one call per
  name (now), counting each `mate_suppression` and each `set_mate_suppressed_in` read-back:

  | E4 transfer case, HEAD's calls | one call per read | one call per name |
  |---|---|---|
  | build (fake, no `Default`) | 21 | 42 |
  | changed Update (s2's edit) | 171 | 279 |

  On SolidWorks the build reads `Default` too, so its count is a little higher.
- *The larger cost is the tree walks.* Each `_kept_mate` walks the whole feature tree (`_mate_group`):
  - `set_mate_suppressed_in` walks it twice, once itself and once inside `mate_suppression`;
  - each read before a restore walks it once;
  - the old route walked it once per `set_mate_suppressed` and once per mode for `mate_states`.

  For a changed E4 Update I count about 225 walks in the put route against about 94 before (90 suppress and restore
  calls × 2, plus 45 reads, against 90 + 4). Each walk is about (top-level features + mates) × 2 COM calls. That is
  roughly 15 000 more calls, likely a few seconds out of process.
- *Change, if s2's log shows it is slow.* Let `set_mate_suppressed_in` read back through a private
  `_flags(feature, configurations)` with the feature it already holds. That halves its walks.

**5. Note: `c48b6ef`'s other path, where `MateGone` becomes the error, is right but untested, and a mutant of it
survives the suite.** `swbuild.py:5040-5044`; `tests/test_swbuild_planetary.py:208`.

- *By reading.*
  - With no error on its way out, the first `MateGone` becomes `pending`.
  - Every other lock and gear mate is still tried, since the loop does not break.
  - The closing rebuild runs; its failure is kept as a failure because `pending` is set.
  - `MateGone` is raised, and Update's change phase turns it into the failure *"The mate "…" is not in … any more:
    it was renamed or deleted in SolidWorks."*. That is true, and the next press goes to `NotAsBuilt` and *Build
    again…*.
- *Can a mate that is not gone be left suppressed unsaid?* Only if `suppress` raised `MateGone` for a mate that
  exists. `_kept_mate` raises it only when no MateGroup sub-feature has that name, and it raises before any call, in
  both the W7 and the per-configuration route. So no.
- *The mutant.* With `if pending is None: pending = exc` replaced by `pass`, the gone mate is swallowed. The 1153
  tests of the nine A-side files still pass. On W7's path the next `gear_mate_ratio` would still raise, but on W8's
  path (`settle` None) only the post-check's *"missing from the assembly"* would remain.
- *A test that catches it.* It passes at HEAD and fails under the mutant. Add it beside `c48b6ef`'s test:

```python
def test_a_gear_mate_gone_during_the_puts_with_no_error_pending():
    from gear_generator import swbuild, swcom
    from gear_generator.workbook import update
    from test_workbook_planetary import direct, edited, fake_build, planetary_4to1

    sw, _, record = fake_build(planetary_4to1())
    spec = edited(planetary_4to1(), gears={"Planet": dict(at="12")})
    real_place, real_supp, lost = sw.place_component, sw.set_mate_suppressed, []

    def place(handle, rotation, at, kind=None):
        if not lost:                                   # gone during the puts, with nothing raised
            old = sw.mate("Sun meshes Planet copy 2")
            sw.mates.remove(old)
            lost.append(old.name)
        return real_place(handle, rotation, at, kind=kind)

    def supp(handle, suppressed):
        name = sw.mate_handles[handle]
        if sw.mate(name) is None:
            raise swcom.MateGone(f'The mate "{name}" is not in Planetary_4to1.SLDASM any more: it was renamed or '
                                 "deleted in SolidWorks.")
        return real_supp(handle, suppressed)
    sw.place_component, sw.set_mate_suppressed = place, supp
    up = update.classify(record, direct(spec), exists=lambda p: True)
    result = swbuild.update_gearbox(sw, **up.update_kwargs(), exists=lambda p: True, mtime=lambda p: 5.0)
    texts = [t for _, t in result.failures]
    assert lost and texts == ['The mate "Sun meshes Planet copy 2" is not in Planetary_4to1.SLDASM any more: it was '
                              'renamed or deleted in SolidWorks.'], texts
    assert not [m.name for m in sw.mates if m.suppressed]
```

**6. Note: the COM-level fake goes one step past the evidence on a name the document does not hold.**
`tests/test_swcom.py:2514-2515`, `:2895`.

- *What the fake does.* It answers several names in document order, filtered, and one name with its own flag. Both
  are measured.
- *Beyond the evidence.* It gives no answer for a name not in `doc.configs`. The commit message calls that "as
  SolidWorks gives", but the 092100 reads asked only names the document held.
- *Why it does not matter.* The app never asks such a name: every caller's names come from
  `configurations()`.
- *Change.* Word the commit's claim as the fake's choice, not a finding. Or leave it; it is harmless. (The swbuild
  fake, `tests/test_swbuild.py:1213`, answers `False`, meaning on, for an unknown configuration. That is a third
  behaviour, equally unreached.)

---

## What the coming SolidWorks runs must show (W8-PLAN §5)

The fixes count as shown only when these readings are in the logs:

- **The s0 and s1 builds** (TransferCase_Parallel, then E4).
  - The build passes §1.8 step 5's flag read-back and step 6's mate check in every mode. No footer sentence
    *"… reads … where the mode has it …"*. This is the fault s0 stopped on.
  - For each coupling, the script logs its own raw `IsSuppressed2(3, GetConfigurationNames())`, document order,
    paired by that order, beside the app's per-name `mate_suppression`. The two agree, and both match W8-PLAN §2.3's
    on-sets.
  - This matters because the script's §5 flag measurement (`workbook_assembly_check.py:1716`, `:5395`, `:5566`)
    calls `session.mate_suppression`, the app's own reader. It is not an independent check of the reader. It would
    have read the same swapped flags as the build did.
- **s2's changed Update** (FDrive, FIdler and FOut At 130 → 132, 4L active), the reading for point 2 and for
  `c14e1b2`:
  - no put refused;
  - `result.placed` with `Carrier carrier` first in each mode, and `put_in` listing all four modes;
  - each mode's post-check clean, every frame at its new wanted frame to 1e-6.

  That shows a suppression naming the active configuration frees the train for the carrier put. Straight after the
  Update, before anything is shown, the script's raw per-configuration read of every recorded mate must give:
  - `RangeSlv engages InDog` on in 2H and 4H only;
  - `RangeSlv engages LoDog` on in 4L only;
  - `ModeSlv engages FrontDog` on in 4H and 4L only;
  - every lock, mesh and the spline on in all four modes.

  Also log the Update's elapsed time (point 4). If §5's driven proof can be added after this Update in 4L and 4H, it
  shows the couplings and the spline came back with their sense, as the late review asked.
- **s3** (D10 per configuration, Update in 2H):
  - the two 4L flags and N's value put right;
  - every mode shown and put, and no failure from `_modes_flags_after`;
  - the same raw read afterwards.
- **s4's J14 edit on E4** (4H's ModeSlv 4WD → 2WD):
  - `ModeSlv engages FrontDog` reads off in 4H and on in 4L only, raw, after the Update;
  - the Update gives no failure;
  - on the fake, 4H's put never calls FrontDog's coupling (I checked this with a scratch test). On SolidWorks the
    raw read is the evidence.
- **2024**, the confirming s0, s1, s2 and s3: the same readings.
  - The multi-name order behaviour is measured on 2026 only. The app no longer depends on it.
  - Logging one raw multi-name read in a non-document order on 2024 would say whether `findings.py`'s new comment
    holds there too.
- **`c48b6ef`** is shown on the fake only. No section loses a mate inside a put, and none should try to.

---

## What I checked and found sound

- **The per-configuration route around a put** (`_put_train(configuration=…)`, `swbuild.py:4893-5072`).
  - With a configuration, `suppress()` sends every lock and gear mate, both ways and including a remade one
    suppressed again, to `set_mate_suppressed_in(h, flag, [configuration])`. `set_mate_suppressed` is never
    reached.
  - The read before the restore is one `mate_suppression(h, [configuration])` per mate, so one `IsSuppressed2` each.
    A read that raises leaves the mate to be turned back on, as W7's unread `mate_states` did.
  - Every exit path restores, and touches no other configuration: a lock or gear mate refused or read back wrong
    (listed before the call), the first rebuild, a put refused, `MateGone`, a restore refused (a failure naming it,
    `_LocksLeftOff`), and the closing rebuild.
  - The late review's refused-third-put test (now `ff1c4dd`) leaves every flag in every configuration as built, with
    2H active.
  - No handle is held across a show: suppress, put and restore run inside one `_modes_put`. `swbuild` holds only
    string handles, and `Session` finds each mate again by name on every call.
- **The mutants on the new behaviour, each caught by the committed tests:**
  - `_modes_flags_after` dropped;
  - `configuration=` not passed from `_modes_put`;
  - the read before the restore skipped;
  - the de-duplication dropped;
  - the read compared against the record's `modes` in place of J14's on-set (caught by
    `test_after_j14s_edit_…`);
  - `c48b6ef`'s `except MateGone` removed;
  - the build's old sentence put back.

  Point 5's is the one that survives.
- **A gearbox without modes makes exactly the calls it made.**
  - I logged every `FakeSolidWorks` call list in the A-side test files, HEAD's tests on `a4ae910`'s `src` against
    HEAD's `src`: 565 identical and 17 different.
  - All 17 are gearboxes with modes. The differences are `set_mate_suppressed` → `set_mate_suppressed_in` one for
    one, one `mate_states` per mode → a `mate_suppression` per mate, and three reads after the last mode.
  - `git diff fa4e508..HEAD -- tests/test_swbuild.py tests/test_swbuild_planetary.py` shows the planetary file only
    gaining `c48b6ef`'s test. The `swbuild` file only gained two findings in the `mode_findings` fixture, from
    `08318d7`, which is outside these four commits.
  - The pinned W7 put-back log (`test_the_w7_put_back_calls_are_pinned_whole`) and every call-sequence test are
    unedited and pass.
- **`_modes_flags_after`** (`swbuild.py:4212-4236`).
  - It runs only after the mode loop of a changed Update, or one with fixes. It does not run on a quiet Update, nor
    when a mode's put raises; in those cases no other configuration was touched, by the route above.
  - It reads every mate with record `modes` or a J14 on-set, in every mode's configuration and only those, so no
    false failure for `Default` or a user's `Exploded`.
  - It compares against `_on_set`, the same target D10 has just set, so a flag D10 turned back on is not a failure.
  - Its sentences are the post-check's own (`swbuild.py:4339-4342`), and a failure already on the result is not
    added twice.
  - A J14 edit on E4 (4H 4WD → 2WD) with every mode put, on the fake: no failure; FrontDog's coupling on in 4L only;
    4H's put never calls it (scratch test).
- **One name per call** (`swcom.py:2957-2974`).
  - It is right for every caller the commit names: `set_mate_suppressed_in`'s read-back, `_set_up_modes`, the build's
    per-mode check, `_modes_check`, the read before a restore, and `_modes_flags_after`. `mate_suppression` is the
    only multi-configuration `IsSuppressed2` in `src`.
  - An empty list now makes no call and returns `{}`, where it used to make one call with an empty array. No caller
    passes one.
  - A scalar answer is taken as one flag; an answer wrapped once more is unwrapped. `None` is point 3.
  - The new sentence is reached only on 0 or 2+ answers, so it is true where it is said. It follows its neighbour in
    `dimension_values`.
  - `GetSystemValue3` is left multi-name, rightly: the same file shows it answering in the order passed.
- **The COM-level fake** (`test_swcom.py:2510-2516`).
  - It models the measured order, except for point 6.
  - `test_flags_are_read_one_configuration_at_a_time_…` fails on `03a4e51^`'s reader, on values and on the logged
    calls. The two re-pinned tests also fail there.
  - The re-pins are exact, not loose: the read-back's `IsSuppressed2` log is now asserted whole, where it used to be
    asserted by containment; the short-answer sentence is pinned in full; `X` is added to the document because a
    filtered answer needs it.
- **The build's sentence** (`swbuild.py:2145-2149`).
  - Of the four combinations of wanted and read, the two that differ say what was read against what the mode wants.
    The two that agree say nothing.
  - `test_a_flag_read_back_wrong_in_a_build_…` pins both differing ones with the s0 run's own pairing. Every clean
    build test pins the agreeing ones.
  - The s0 log's two sentences are exactly what the old code printed for the swap the 092100 reads explain (2H read
    suppressed, N read on).
- **Tests in general.**
  - The E4 tests drive the whole of `_modes_assembly` on the fake. `test_e4_put_suppresses_…` asserts the call
    sequence, but the sequence is the change being made, which calls are used, so that is the right thing to pin.
  - `test_the_read_after_the_last_mode_…` calls the private function with a hand-made state. That is acceptable for
    the de-duplication.
  - Nothing was deleted, skipped or loosened.
  - `ff1c4dd`'s two tests also pass on `a4ae910`. They guard `5fcaa6a`'s behaviour, and by the late review they fail
    on `9f21d99`.

## What I could not check

- Anything on SolidWorks. I ran no Windows program: another agent is driving SolidWorks on this host.
- Whether `SetSuppression2(…, 3, [active])` followed by a top-only rebuild with no show frees the train for the puts
  (point 2).
- What `IsSuppressed2(3, [name])` answers for a lock mate, for `Default`, or on 2024. The 092100 reads cover a
  coupling and a distance mate on 2026, `2H` (active) and `N`.
- The real COM cost of point 4. The walk counts come from the code and the fake's call counts, not from a timed run.

## Tests run

- `PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_swbuild.py tests/test_swbuild_modes.py
  tests/test_swbuild_planetary.py tests/test_workbook_modes.py tests/test_workbook_planetary.py tests/test_swcom.py`:
  `993 passed in 4.82s`.
- The whole suite: `2 failed, 3075 passed, 10 skipped in 42.33s`. Both failures are the known `ModuleNotFoundError`
  for `tkinter` in this venv (`tests/test_gears_clutch.py::test_the_strip_never_offers_them`,
  `tests/test_ui_text.py::test_the_end_view_readout_always_fits_and_lists_up_to_four_heights`).
- HEAD's tests on `a4ae910`'s `src`, in a scratch copy with its own `pyproject.toml`, over the nine A-side files:
  `8 failed, 1145 passed`. The 8 are the new tests of `c48b6ef`, `c14e1b2` and `03a4e51`, and the two re-pinned
  `test_swcom` tests. HEAD's `src`: `1153 passed`.
- `03a4e51^`'s `swcom.py` under HEAD's `test_swcom.py`: `3 failed, 271 passed`.
- Scratch tests:
  - point 5's test: passes at HEAD, fails under the mutant;
  - the E4 J14 test: passes;
  - the cost count above.
