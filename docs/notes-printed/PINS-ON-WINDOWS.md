# The hashed pins under Windows' python.exe

By the coordinator's ruling of 2026-11-19 on F3-DEMONSTRATION-RUNS-REVIEW §4, then the coordinator's rulings on this
note's findings (the last section). Commits `a118315` (the pins), `280bff8` (F3's demonstration self-check), `cf1bb84`
(this note), then the Linux-only skips and the three self-checks' fixes, and this note updated. No SolidWorks and no
Excel were used.

## What was done

- **The hashes are unchanged** and are still the pin on Linux: every `assert sha == pinned` of before is still made
  there.
- **The text each hash was taken over is stored** beside it in `tests/fixtures/printed/pinned.json`. It holds 103 texts
  (2.0 MB): STRIP 23, ASSEMBLIES 6, SOLVE 8, FIXTURES 4, SIDECARS 13, ENTRIES 13, RECORD_BEFORE_F1 1, K11 15, CARD 15,
  RESULTS 5.
- **Each pin compares the text made with the stored one** (`pin_problem` / `assert_pinned` in
  `tests/test_printed_rule.py`):
  - Two floats (repr or `float.hex`) are equal within `math.isclose(rel_tol=1e-12, abs_tol=1e-12)`.
  - Everything else must match exactly: words, integers, a float against an integer, and a number inside a name
    such as `Gear_m1.5_N25`.
  - Where `sys.platform` is not Linux, the hash is not compared, and this comparison is the pin.
- **Every pin is covered:**
  - F1's STRIP, ASSEMBLIES, SOLVE, FIXTURES, SIDECARS, ENTRIES, RECORD_BEFORE_F1, K11 and CARD;
  - F3-0's uses of STRIP and SIDECARS, including the as-built test;
  - F4-0's RESULTS;
  - the pins check in `probe/f3_demonstration.py`'s self-check, now through `pin_problem`. Its line also says which
    way the pins were held.
  - No other probe or demonstration self-check compares against a pin.
- **The functions are split into text and hash.** `strip_text`, `solve_text`, `assembly_texts`, `fixture_texts` and
  `results_texts` are new, and the old names still return the hashes. `test_workbook_planetary._fingerprint` is
  split into `_fingerprint_text` and its hash, and is unchanged.
- **Two new tests:**
  - `test_the_stored_text_of_every_pin_is_the_text_its_hash_was_taken_over` holds every stored text to its hash on
    any platform.
  - `test_the_text_comparison_takes_a_floats_last_bits_and_nothing_more` checks what the comparison lets through and
    what it does not.
- **No test was loosened, and no assertion was removed.**
- **F2's fixture-backed comparisons are unchanged.** These are `F2_built.json`'s print lists, footers, records and
  sidecars. They compare rounded text exactly and pass under python.exe as they are.

## How the stored text was made and checked

`pinned.json` was written on Linux at `12440a3`, whose `src` and `tests` are `1afc1f0`'s. It was made by the pins'
own text functions, with the same monkeypatches the tests use. Before writing, the script asserted that every one of
the 103 texts hashes to its pinned value, so no text could be written that is not the pinned text. The new test
re-checks this on every run.

The scratch script is not committed. Its steps are the text functions above, then `sha256`, then `json.dump`.

## Linux against Windows: what differs

The same texts were made under both Pythons at `12440a3`.

- **Identical on both:** ASSEMBLIES, CARD, ENTRIES, K11, RESULTS and SIDECARS.
- **Numbers differ** in all of STRIP, four of SOLVE and all of FIXTURES.
  - 466 numbers differ in all. The largest relative difference is 8.2e-14.
  - Two are near nothing: in Solve's crossed pair, `7.105427357601002e-15` against `0.0`, which is one ulp of 40 left
    by a subtraction. A relative tolerance alone cannot take these, so an absolute 1e-12 is added. This is finer than
    the review's suggested 1e-9.
- **Not a last bit (the finding):** FIXTURES (4 texts) and RECORD_BEFORE_F1 differ in **path separators**.
  - Linux gives `C:\Out\/Gear_m2_N17.SLDPRT` and `C:\Parts\Reducer_12to1/Reducer_12to1.SLDASM`.
  - python.exe gives `C:\Out\Gear_m2_N17.SLDPRT`.
  - The cause is that the planner joins a Windows folder and a file name with `os.path.join`: `workbook/build.py:190`
    and `workbook/gearbox.py:781`, `:782` and `:817`. That is posixpath on Linux and ntpath on Windows.
  - Nothing was normalised to hide this. By ruling 1 these two pins (five tests) are **Linux-only**. Off Linux they
    are skipped, and the skip says why (see *Linux-only pins* below).

## Deliberate breaks (scratch copies, deleted afterwards)

The breaks are F1-0-REVIEW's and F1-0's, F3-0-REVIEW's simulated default moved to machined gears, and F4-0-REVIEW's
"a strength warning or reworded Results line reaches a machined gearbox". Each was applied to a copy of the working
tree, and `tests/test_printed_rule.py` was run three ways:

- on Linux by hash;
- on Linux with `HASHED_HERE = False`, so the text comparison alone is the pin;
- under python.exe.

Each cell gives tests failed / pin tests among them.

| Break | Linux, hash | Linux, text only | python.exe |
|---|---|---|---|
| none | 0 / 0 | 0 / 0 | 5 / 5 (the path joins) |
| `to_dict` keeps `process` | 106 / 90 | 106 / 90 | 107 / 91 |
| `"nozzle": null` in `derived` | 90 / 78 | 90 / 78 | 95 / 83 |
| machined factor 0.31 | 219 / 217 | 219 / 217 | 223 / 221 |
| K11's ` × ` as ` x ` | 15 / 14 | 15 / 14 | 20 / 19 |
| card's ` · 0.3m` as ` · 0.30m` | 15 / 14 | 15 / 14 | 20 / 19 |
| F3: blank allowance 0.2 for machined too | 151 / 148 | 151 / 148 | 152 / 149 |
| F4: machined gearboxes rated | 12 / 12 | 12 / 12 | 16 / 16 |
| F4: Results row "Worked out as" reworded | 1 / 1 | 1 / 1 | 6 / 6 |
| last bit only: `BACKLASH_FACTOR` one ulp up | 238 / 216 | 22 / 0 | 27 / 5 |

- **For every break, the text-only failures are exactly the hash failures,** test for test.
- **The python.exe failures are exactly the Linux text-only set plus the five path-join tests.** Where python.exe's
  pin count is lower than Linux's plus five, the extra Linux failure is one of those five.
- **The last row is the trade the ruling makes:**
  - The hash catches a one-ulp change, and the text comparison lets it through, on both platforms.
  - The 22 tests that still fail there are not pins. They are tests elsewhere in the file that compare a float or an
    equation exactly.

## The numbers

**First pass**, before the rulings below:
- Linux whole suite: 5568 passed, 1 failed, 1 skipped.
- python.exe:
  - `test_printed_rule.py`: 483 passed, 5 failed. At `12440a3`, before any of this work, it was 339 passed, 147 failed.
  - `test_workbook_build.py` and `test_workbook_window.py`, run alone: 166 passed, 2 skipped.
  - A wider batch: the F2 and F3 test files and `test_findings` passed. `BEFORE_W7` (5), `BEFORE_W8` (9) and
    `test_swbuild`'s W7 put-back log (1) failed, being Linux-only hashes. Two `test_strength_form.py` tests failed on
    Tk font metrics.

**After the rulings:** see *Rulings and what was done* below.

## Found, for a ruling

1. **The path joins.** FIXTURES and RECORD_BEFORE_F1 differ in separators, not in last bits, so they still fail under
   python.exe. There are two ways to hold them there:
   - (a) A second stored text for these two, made at the same state with `os.path` as `ntpath`, shown to differ from
     the hashed text only at the joins and in last bits.
   - (b) Rule them Linux-only, said in their failure.
   - Not done either way without a ruling.
2. **The absolute tolerance.** The ruling names a relative 1e-12, and `abs_tol=1e-12` is added for the
   cancellation residual. The review suggested 1e-9; 1e-12 is the finer of the two.
3. **The W-era hashes** (`BEFORE_W7`, `BEFORE_W8`, `W7_PUT_BACK_LOG`) remain Linux-only, as the review noted.
   - The same treatment would apply to them.
   - They live in W-era files that w9d's agents may be closing.
4. **Two F4 strip tests fail under python.exe on Tk font metrics** (`test_strength_form.py:289`, `:309`).
   - The derived panel is 1 px wider than the strip there.
   - This is a real layout question on Windows, not a pin question.
5. **workbook_assembly_check's self-check cannot run under python.exe.**
   - Its pywin32 stand-in's `win32api` is met by the real `win32com`, which `swcom` imports. `win32com`'s
     `SetupEnvironment` then fails with `AttributeError: module 'win32api' has no attribute 'error'`.
   - It is a Linux-only self-check by construction.
6. **w9b's and w9c's self-checks crash under python.exe when their output is piped,** because `π` and `−` are not in
   cp1252. They pass with `PYTHONIOENCODING=utf-8`.

## Rulings and what was done (2026-11-19, the user's to overrule)

1. **Path joins: the pins are Linux-only.** In `tests/test_printed_rule.py` these five tests are marked `LINUX_PATHS`.
   Off Linux they are skipped, with the reason said in the skip, and no second text is stored:
   - `test_the_w8_fixtures_and_rangebox_plan_bit_for_bit_as_at_the_cut` (FIXTURES);
   - `test_a_record_written_before_f1_is_nothing_to_update_or_make_again` (RECORD_BEFORE_F1);
   - `test_a_record_written_before_f1_is_nothing_to_do_against_a_workbook_marked_machined_or_left_blank`, three cases
     (RECORD_BEFORE_F1).
2. **The absolute tolerance of 1e-12 is accepted.**
3. **W7's hashes are left as they are and are Linux-only.**
   - These are `test_workbook_planetary.test_every_workbook_before_w7_plans_bit_for_bit_as_it_did`, `BEFORE_W7`, five
     cases. They are skipped off Linux with the reason said.
   - Their text was checked under both Pythons. Per workbook, 7 to 73 numbers differ, all within 1e-12 (the `float.hex`
     figures among them). There are 11 to 15 path joins, as in (1).
   - **The Linux-only pins on the branch are exactly these ten tests (five here, five in (1)).** Every other hashed pin of
     `test_printed_rule.py` holds by its stored text off Linux.
   - Outside this ruling's reach, and not touched: `test_workbook_modes`' `BEFORE_W8` and `test_swbuild`'s
     `W7_PUT_BACK_LOG`. They are Linux-only hashes too and still fail under python.exe.
4. **`test_strength_form.py`'s two Tk-metric tests** are the form's author's. They were left alone.
5. **The three self-checks run under python.exe, and nothing any of them checks changed.**
   - `workbook_assembly_check` now uses the real `win32api`, `win32gui` and `win32process` where they import, and its
     stand-ins only where they do not. `xlhelp` is always stood in, and the self-check calls none of them.
   - `w9b_demonstration` and `w9c_demonstration` reconfigure stdout and stderr to UTF-8, as the other probe scripts do.

Commits: `0e876b1` (the skips) and `d1d5d35` (the self-checks).

**The numbers after the rulings:**

- **Linux,** whole suite: **5568 passed, 1 failed, 1 skipped.** The failure is the known Tk font-width test.
- **python.exe,** `test_printed_rule.py`, `test_workbook_planetary.py` and `test_findings.py` together: **744 passed, 10
  skipped, 0 failed.** The ten skips are the Linux-only pins above, each saying why.
- **Self-checks,** ok / failed, the same on Linux and under python.exe, with no `PYTHONIOENCODING` set:

  | Script | ok / failed |
  |---|---|
  | f1_demonstration | 61 / 0 |
  | f2_demonstration | 35 / 0 |
  | f3_demonstration | 18 / 0 |
  | f2_probes | 125 / 0 |
  | w9b_demonstration | 50 / 0 |
  | w9c_demonstration | 105 / 0 |
  | w9c_probes | 27 / 0 |
  | w9d_demonstration | 62 / 0 |
  | w9d_probes | 73 / 0 |
  | workbook_assembly_check | 7 / 0 |
