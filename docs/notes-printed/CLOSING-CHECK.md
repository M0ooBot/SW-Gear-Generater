# Closing check: the pins under Windows' python.exe, and the strip's width under Windows' fonts

**Read at `523cbe6` on `printed`.** The commits checked are:
- for (1): `a118315`, `280bff8`, `0e876b1` and `d1d5d35`, with `PINS-ON-WINDOWS.md`;
- for (2): `523cbe6`.

No code was changed. The breaks below were made in scratch copies (`git archive`), and the copies were deleted
afterwards. SolidWorks and Excel were not used.

**Verdict: sound, no must-fix.** No pin was loosened on Linux. Off Linux, the stored-text comparison catches every
deliberate break the hash catches, but for a last-bit change, which is the trade the ruling chose. The ten skips say
why they skip. `523cbe6` changes no word any gear is told. Its tests assert a real width requirement, and the old code
fails that requirement under Windows.

## 1. The pins

**What the code does.**
- `pin_problem` (`tests/test_printed_rule.py`) first holds the stored text to its pinned hash.
- On Linux it then asserts the made text's hash, as before, and then the text comparison as well.
- Off Linux, the text comparison alone is the pin.
- In `text_difference`, words, integers, and a float set against an integer must match exactly. Only two floats are
  compared to a tolerance, `isclose(rel 1e-12, abs 1e-12)`. A number inside a name such as `Gear_m1.5_N25` is not
  taken as a number.
- Every old `== STRIP[...]`, `_sha(...) ==` and `== ASSEMBLIES` check became `assert_pinned` with the same
  coverage:
  - the dict pins check their keys first;
  - the as-built SIDECARS test falls back to exact text equality where it used `.get`.
- `_fingerprint` hashes exactly the text it hashed before.

**The stored texts are what the hashes pin.**
- I checked this independently: `pinned.json` holds 103 texts in the ten groups.
- Each group's keys equal its pin dict's keys, and every text's sha256 equals its pin.
- `test_the_stored_text_of_every_pin_is_the_text_its_hash_was_taken_over` does the same on every platform, and it
  passes.

**The deliberate breaks.** Each break was applied to a copy of `HEAD`, and `tests/test_printed_rule.py` was run three
ways: on Linux by hash; on Linux with `HASHED_HERE = False`, so the text comparison alone is the pin; and under
`python.exe` (3.13.14, pytest 9.1.1) against the copy's Windows path, with `PYTHONPATH` set to its `src`.

| Break | Linux, hash | Linux, text only | python.exe |
|---|---|---|---|
| none | 488 passed | 488 passed | 483 passed, 5 skipped |
| F3-0's: a blank allowance plans 0.2 for machined too (`spec.py:327`) | 151 failed | 151 failed | 147 failed, 5 skipped |
| F1-0's: machined backlash 0.31 × module (`spur.py:340`) | 219 failed | 219 failed | 218 failed, 5 skipped |
| F4-0's: the Results row "Worked out as" reworded (`export.py:87`) | 1 failed | 1 failed | 1 failed, 5 skipped |
| one ulp only: `BACKLASH_FACTOR` 0.30000000000000004 | 238 failed | 22 failed | 22 failed, 5 skipped |

- **For every break that is not a last bit, the text-only failures are the hash failures,** test for test (compared
  by node id).
- **The python.exe failures are exactly the Linux text-only set,** less the Linux-only tests that are skipped there.
  Under the allowance break, four RECORD_BEFORE_F1 tests were skipped; under the 0.31 break, the FIXTURES test was.
- **The ulp row is the trade the ruling makes.** The text comparison lets a one-ulp change through. The 22 that still
  fail are exact float or equation tests elsewhere in the file. These figures reproduce `PINS-ON-WINDOWS.md`'s table.
- **F3's demonstration self-check** (`280bff8`):
  - At `HEAD` it gives 0 failed on Linux, by hash, and 0 failed under python.exe, by the stored text on win32. Its
    line says which way the pins were held.
  - With the allowance break it fails its pins check on both platforms, naming STRIP['spur'].

**The ten skips are narrow and say why.**
- They are `LINUX_PATHS` on five tests (FIXTURES, and RECORD_BEFORE_F1 ×4) and a skipif on `BEFORE_W7`'s five cases.
- Each runs on Linux, unchanged.
- Each skip's reason names the cause and the ruling: the posix-joined `C:\Out\/Gear_...`, and for W7, `float.hex`
  last bits.
- **One thing to know, not a must-fix.** The skip covers the whole test, so off Linux it also skips that test's
  assertions that are not pins. Examples are RECORD_BEFORE_F1's nothing-to-update and nothing-to-make-again checks.
  The suite's platform is Linux, where they all run, and other tests still caught every break under python.exe.
- `BEFORE_W8` and `W7_PUT_BACK_LOG` stay Linux-only hashes that fail under python.exe, outside the ruling, as the
  note says.

## 2. The strip's width under Windows' fonts (`523cbe6`)

**Only `gui.py` and tests change; `ui_text.py` is untouched.** What changes is where lines break:
- Each warning and the line under the rows wraps at `_text_room`, which is the body's 434 px less the label's own
  chrome.
- The Holds once value's room takes off its own label's chrome instead of a flat 8 px.

**Read live, before (`523cbe6^`) and after, with a scratch probe test** on a single A10 ring, printed and machined, and
on a pair with a 33-tooth ring:
- **Linux:** identical before and after: every warning, the line under the rows and both Holds once cells
  (`not rated: tips inside\nthe base circle`). Every wraplength is 430 on both.
- **Windows:**
  - Every text is the same, and the Holds once cells are the same before and after.
  - The wraplength goes from 430 to 428.
  - The machined A10 ring's own warning (older than F4) was 435 px wide before, past the body's 434. It is 418 px
    after.

**So nothing a machined gear is told changed in words.** Only where a line breaks changed, and only under Windows.

**The tests assert a real requirement.**
- `test_the_row_and_its_line_keep_the_strip_as_wide_as_it_is_without_them` covers seven forms × printed and machined,
  replacing one pair and three single forms. It asserts that:
  - the panel is no wider than the strip's 460;
  - the rows keep within 434;
  - the row and its line widen nothing.
- `test_a_long_warning_and_the_line_under_the_rows_wrap_inside_the_panel_body` holds wraplength + chrome to the body
  and each label's width within it. Under Windows the old code fails it (436 and 435).
- The old width tests failed under python.exe on `523cbe6^`, and the new file passes there: 47 passed, 1 skipped. The
  skip was the fixture's "no display for Tk" on one parametrised case, a Tk start-up, not an assertion.
- **The one assertion relaxed:** the pair's unrated ring now asserts the whole value and that it breaks, not where. The
  reason is that Windows' font breaks it twice. On Linux the break is where the old test pinned it. Acceptable: where a
  line breaks is the platform's font, not a requirement.
- A small note: `_text_room` takes the raw-pixel chrome off `theme.px(434)`, where the old code had `theme.px(430)`.
  At a display scale other than 1, the wrap moves by a pixel or two. It is covered by the same width test.

## 3. The suite

Run on Linux from this worktree's root (`PYTHONPATH=src`; `gear_generator` imported from this checkout): **5582 passed,
1 skipped, 1 failed**. The failure is the known font-width test,
`test_workbook_window.py::test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left`.
`test_strength_form.py` run alone on Linux: 48 passed.
