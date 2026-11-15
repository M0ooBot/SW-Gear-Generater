# Review of the tier-11 fixes: `d2f492e`, `f87ecc3`, `0c49d24`, `74ac826`

*Independent, 2026-11-15, read only on code.* Under review: the four commits that answer `W8-REVIEW-TIER11.md`
points M2, S2, S3 and S4. Line numbers are at `74ac826`.

**Verdict.** Sound. Each commit does what its message says.

- **Update with modes (M2).** A mate the record does not hold, on in any mode's configuration, now refuses in the
  check phase. The refusal comes after J13's refusal of an active configuration that is no mode, and before anything
  is shown, set or marked. That holds on every path I tried: a quiet Update, a changed one, a J14 edit, and a
  recorded mate that D10 would turn back on.
- **A gearbox without modes** takes W5's branch, call for call.
- **The gates (S2, S3).** Both findings are required at exactly their committed values. The refusal comes before any
  SolidWorks call, in the build as well as the Update.
- **The fake (S4)** models only what tier 11 measured.
- **No existing call list changed.**

Nothing below is a must. Two things should change, both in tests:

- the new refusal is pinned only for modes that are not active (point 1);
- one W7 test still rides on a committed finding (point 2).

Point 3 is a note on one word the user is told.

---

## Points

**1. Should fix: no test pins the M2 refusal when the mate is on in the active mode, or a list of three or more
modes. Two mutants of `d2f492e` survive the whole suite.** `tests/test_swbuild_modes.py:302-310`;
`swbuild.py:4561-4562`, `:4084-4085`.

- *What is pinned.* The two parametrized cases are "on in N" and "on in 4H and N". In both, 2H is active and the mate
  is suppressed there.
- *Mutant A.* `elif motion.configurations:` changed to `elif motion.configurations and state.suppressed:`
  (`swbuild.py:4561`).
  - A mate on in the active mode then takes W5's sentence ("suppress Distance3 in SolidWorks"). That sentence names
    no mode, so a user who suppresses it only in 2H is refused again for N on the next press.
  - The commit message claims every mode is named. Nothing catches the mutant: 2 failed (tkinter), 3112 passed.
- *Mutant B.* The list `", ".join(on_in_modes[:-1]) + f" and {on_in_modes[-1]}"` changed to
  `" and ".join(on_in_modes)` (`swbuild.py:4085`). Nothing catches this either.
- *What the code says today* (a scratch test, all four modes on, 2H active): "In modes 2H, 4H, N and 4L, Distance3 is
  a mate in TransferCase.SLDASM that Gear Generator did not make, and it may hold the gears where Update SolidWorks
  would put them, so nothing is changed; in SolidWorks, suppress Distance3 in 2H, 4H, N and 4L and press Update
  SolidWorks again." This is right, and it matches `_modes_check`'s own list form (`swbuild.py:4032`).
- *Why it matters.* A mate added by hand in SolidWorks is usually on in every configuration. So this case, not "on in
  N only", is the one users will meet most.
- *Change.* Add a third case to the parametrize at `:302`, `(("2H", "4H", "N", "4L"), "<the sentence above>")`. It
  kills both mutants.

**2. Should fix: `test_an_update_on_the_fake_leaves_the_train_turning_as_worked_by_hand` (4 cases) still rides on the
committed `PLANETARY_PUT_ROUTE`. Confirmed.** `tests/test_workbook_planetary.py:858`.

- *Evidence.* In a scratch copy with `findings.PLANETARY_PUT_ROUTE = None`, the whole suite gave 7 failures:
  - the two tkinter failures;
  - `test_findings.py::test_a_turned_planetary_is_put_back_with_its_gear_mates_off`, which should fail, since it pins
    the committed value against the file;
  - exactly these four cases.
  - The eight `turned_findings` Updates in `test_swbuild.py` and the two `put_route` tests in
    `test_swbuild_planetary.py` passed. The fixer's claim holds.
- *Change.* The file already imports `findings` (`:74`). Add `monkeypatch` to the test's arguments, and make the first
  line of its body:
  `monkeypatch.setattr(findings, "PLANETARY_PUT_ROUTE", "gear mates off around the puts", raising=False)`.

**3. Note: "suppressed" overstates a mate that is on in a configuration that is no mode.** `swbuild.py:3303-3305`
(CHECK line); `ui_text.py:3350-3354` (the footer); `tests/test_swbuild_modes.py:338-346`.

- *What happens.* `test_a_mate_not_on_record_on_only_in_a_configuration_that_is_no_mode_does_not_refuse` has
  Distance3 on in Exploded. The Update puts Distance3 in `extra_mates`, so the user reads "TransferCase.SLDASM also
  has a suppressed mate the app did not make, Distance3; Update SolidWorks left it as it is." The log reads "CHECK
  suppressed mates Gear Generator did not make, left as they are: Distance3".
- *Why it is only a note.* Leaving the mate is right by J12, and Update never works in Exploded: J13 refuses first
  when Exploded is active (see "Sound"). The word is true in every mode, but the app never read Exploded.
- *Change, if wanted.* For an Update with modes, say "suppressed in every mode" in both places, for example "…also
  has a mate the app did not make, Distance3, suppressed in every mode; …".

---

## What the SolidWorks runs must show for M2 (W8-PLAN §5, `s3`)

- *The setup.* The angle mate the record does not know is made with 2H active. It is then suppressed in 2H, 4H and 4L
  with the per-configuration call. Each flag is read back one name per call: on in N, suppressed in the other three.
  2H stays active.
- *The refusal.*
  - The text: "In mode N, <the angle mate> is a mate in <the assembly> that Gear Generator did not make, and it may
    hold the gears where Update SolidWorks would put them, so nothing is changed; in SolidWorks, suppress <the angle
    mate> in N and press Update SolidWorks again."
  - Between the open and the refusal, the call log holds no `ShowConfiguration2`, `SetSuppression2`,
    `SetSystemValue3`, rebuild, put or `AddMate5`.
  - Four `IsSuppressed2(3, [c])` reads on the angle mate, one name each, in mode order.
  - 2H still active after. `GetSaveFlag` False on the assembly and every part. No window under the watch.
- *It finds the mate by name, which is new.* This is the first time the app finds a user's mate by name
  (`find_mate`). W5's M7 only listed such a mate through `mate_states`. The run shows that `_is_mate` accepts an
  angle mate made by hand, and that `mate_suppression` reads it.
- *Suppressed → listed and left.*
  - The script suppresses the mate in N with 2H still active. The next Update goes through, and the CHECK line and
    footer name the mate.
  - Its four flags read suppressed afterwards, unchanged.
  - A changed Update here shows every mode with the user's mate suppressed in all of them: nothing in error from it.
- *Order with J13.* With `Exploded` active, the refusal is J13's (the configuration sentence), not M2's. On the fake
  it is, and the angle mate is never read.

## What I checked and found sound

- **M2, the order of the check.**
  - `_update_motion` reads `mate_states` with others refused (`:4547-4554`). It collects the unknown mates
    (`:4556-4568`). Then `_modes_check` runs (`:4573`): ConfigurationGone and J13's active-not-a-mode refusal come
    first. `_modes_unknown_mates` follows (`:4575`).
  - D10 and J14's flags are only collected in the check phase (`state.flags`, `state.values`) and applied in
    `_modes_assembly`, the change phase. `suppressed.clear()` throws away W5's this-configuration D10 list.
  - So nothing can change before the refusal.
- **M2 on the fake, by scratch tests outside the repo** (both position variants each). Each refused with the "In
  mode N" sentence, made no call in `MODE_CHANGES`, and left the recorded mate's flags as found:
  - a quiet Update with the mate on in N;
  - a J14 edit (`on_sets`) with it on in N;
  - a recorded slide found suppressed in N (D10's case) beside it.
- **The instruction works.** After the refusal, the mate set suppressed in 4H and N let the next changed Update
  through, listed and left. `Exploded` active refuses with J13's sentence before any read of the user's mate.
- **Without modes.** `motion.configurations` is empty, so the `elif` falls through to W5's two branches unchanged.
  Every pre-existing call list is identical (below).
- **The sentence.** It is true where reached: the mate is unsuppressed in exactly the modes named.
  - It follows M7's words with the neighbours' "In mode N, …" prefix.
  - "In modes" is new, but grammatical, and the list form matches `_modes_check`'s.
  - It is in house style, as far as I can judge.
- **The cost.** Per unknown mate: one `find_mate`, a walk of the mate group, plus one `IsSuppressed2` per mode. Four
  calls on the transfer case. Negligible beside the check phase's per-mode reads.
- **S2 and S3.**
  - Both tuples carry the exact committed strings (`swbuild.py:1997-2001`, `:3903-3907`; `findings.py:1380`,
    `:1403`).
  - The Update test asserts `fake.calls == []`. The build test asserts only that no `new_*` call was made
    (`test_swbuild.py:6262`). A scratch test showed `fake.calls == []` for the build too, with either finding None.
  - `_modes_gate` returns on `modes is None`, and `_update_modes_gate` returns without configurations, so a
    gearbox without modes needs neither finding.
  - All callers of `dimension_values` and `set_dimension_in` are modes paths (`swbuild.py:2096-2097`, `:2188`,
    `:4052`, `:4179`, `:4392`).
  - With both committed findings set to None in a scratch copy, only the three `test_findings` tests that pin them
    failed. So no test of the app rides on them, and `test_the_w8_gates_open_on_both_versions_from_these_findings`
    catches a committed value that would close the gate.
- **2024 and `CONFIGURATION_SHOW_OVER_DEFINED`.** It is gated version-free, as `CONFIGURATION_SHOW_RAISES_DIALOG`
  and `VALUE_READ_ORDER` are. The comment names 2024 as unmeasured, as `SUPPRESSED_GEAR_MATE_SENSE_READ`'s does, and
  `findings.py`'s own "Not covered" list says 2024. The finding only opens a gate. No user sentence states anything
  about 2024 or about a fight.
- **`turned_findings` and `put_route`.** They pin the value already committed, so behaviour is identical with the
  committed value as it is. The unset-route test (`_planetary_turned_and_pressed`, `test_swbuild.py:6669`) sets the
  route in its body, after the fixture, so it still proves the refusal.
- **S4.**
  - `mate_codes_in` answers only for the active configuration, and falls back to `mate_codes` and the mate's own
    code (0) everywhere else. That is tier 11's 47 / False in one configuration and 0 elsewhere, and nothing more.
  - The non-empty tuple `(0, False)` would also be honoured, since it is truthy.
  - Giving the code on the recorded slide rather than staging two slides is still a test of the app. The fake
    reports the code, and the app's `_mode_problems` and `_modes_post_check` turn it into exactly "In mode N, the mate
    RangeSlv along Rear is in error in SolidWorks.". The test pins the one failure, the code read only in N
    (`checks[2]`), and 0 in the other three.
  - "Saves nothing" is shown, not assumed. `result.saved == ""` and `"save_as" not in names(fake)`, and `save_as` is
    the fake's save (`test_swbuild.py:379`, called at `swbuild.py:703`).
  - The Update test needs no save check: an Update saves nothing by design (`GearboxUpdate`'s docstring,
    `swbuild.py:3116`).
- **Nothing weakened.** `git diff 6f35d33..74ac826 -- tests` removes no assertion. The removed lines are two fixture
  docstrings, one fixture tuple's closing line, two test signatures (now taking `put_route`), and the fake's one
  `mate_codes` line, which now falls back to the same expression.
- **Call lists.** I recorded every `test_swbuild.FakeSolidWorks` instance's `calls` per test, with a scratch plugin,
  on `git archive 6f35d33` and on `74ac826`. The result: 531 tests identical, 0 changed, 0 gone, and 19 new (11 with
  non-empty call lists). These are the 8 gate cases, the 8 M2 cases and the 3 S4 cases. My counting unit differs from
  the fixer's 538 / 12, but the claim that no existing call list changed holds.

## What I could not check

- **Anything on SolidWorks.** No run, by the brief. That includes:
  - `find_mate` and `IsSuppressed2(3, [c])` on a mate made by hand;
  - whether a user's mate inside a mate folder suppressed in one configuration reads suppressed there through its own
    `IsSuppressed2(3, …)`. If it does not, Update refuses although the mate is off: a safe error, and the instruction
    still clears it.
- **2024.** No 2024 read of the new path, and none of either finding.
- **The fixer's exact 538 / 12 tally.** Their logger is not committed. My own tally is above.

## Tests run

```
PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_swbuild.py tests/test_swbuild_modes.py tests/test_swbuild_planetary.py tests/test_workbook_modes.py tests/test_workbook_planetary.py tests/test_swcom.py
1014 passed in 4.90s

PYTHONPATH=src .venv/bin/python -m pytest -q
FAILED tests/test_gears_clutch.py::test_the_strip_never_offers_them - ModuleN...
FAILED tests/test_ui_text.py::test_the_end_view_readout_always_fits_and_lists_up_to_four_heights
2 failed, 3112 passed, 10 skipped in 42.84s
```

The two failures are the known `No module named 'tkinter'` in this Linux venv. Mutants, scratch tests and the call
recorder ran in copies under the session scratchpad, never in the repo.
