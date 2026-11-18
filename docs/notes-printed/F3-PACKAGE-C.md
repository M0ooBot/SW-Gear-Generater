# F3, package C, handed back

Package C of PLAN-PRINTED's stage F3 (§4.1, §4.1.1, §4.2, §4.6; `F3-INTERFACES.md` §5, §7, §9, §14): what the user
sees of the bore as cut. Written beside A and B in this worktree; wound down at the coordinator's word. No SolidWorks,
no Excel.

## Commits

1. `7051698`: `gui.py`, `ui_text.py`, `workbook_gui.py` (the one wiring the coordinator gave C), `tests/test_ui_text.py`
   (additions), `tests/test_bore_form.py` (new, 21 tests).
2. `1dfde10`: `design/UI-DESIGN.md` (section *The bore as cut (F3)*), `design/canvas/gen.py`, the new board `PrintedBore`,
   every strip board regenerated.
3. `5000c82`: `README.md`.
4. This note.

**No existing test changed.** Suite at `478a6f2` plus 1 to 3, switch off, in a scratch copy: **5384 passed, 1 skipped, 1
failed** (the known Tk font test). **Guards, switch on**: 639 passed, 1 failed, guard 5
(`test_swbuild_user_work`, B's analysis in F3-PACKAGE-B.md: not reachable by threading). **Guard 10 reads green with the
switch on** (`_update_target` derives again from the as-built spec), and so do the six strip pins (6 to 9, bevel, crown).

## Built, against the interface's list for C

- **Form rows** under Bore: Bore allowance (placeholder from the derived gear: *0.2 · printed*, *0 · as built*, *0*),
  Drive (Round/Flat), Flat while Drive is flat. Ring: none; bevel: no Drive or Flat (G5); a hidden row goes across blank.
- **The strip through `as_built`** (`gui.held_spec`): every derive, `_update_target`, Update values, and a Build with a
  record open, which keeps the as-built allowance (ruling 11) and says so in the bar: *Build will make X.SLDPRT with no
  bore allowance, as Y was built, since Bore allowance is blank.* Tested on the real strip path for every F2 strip part
  (S4, S2).
- **Words**: *Bore as cut* / *Flat as cut* rows (none on a plain machined gear; card pin green); three cards out of
  `EXPLAINER_FIELDS`; Bore's worked line on the hole as cut; print list *bore 8 mm + 0.2 mm allowance (8.2 mm as cut)*,
  *bore 10 mm* unchanged with none; K3. Every sentence is in UI-DESIGN's new section and pinned in the tests.
- **A's warnings and B's strip refusal** pinned as the form shows them (the depth refusal naming D less F; the no-Bore
  allowance a warning, Build enabled).
- **`workbook_gui._assess`** hands `assess` the record `_blank_process` reads (`assessed_record`); test: a printed
  gearbox built before F3 keeps its warnings word for word with the switch on, where a fresh read would add a rim warning.
- **README**: the coupon table after F3 (shaft in Bore, 0 typed to 0.3 in Bore allowance; never shaft + offset), section
  *The bore* (blank meanings, hole compensation 0, the D-flat and how to type it, the flat's fixed angle, and that the
  assembly does not model a shaft's flat: phased by flats in the machine, by meshes in the assembly).

## Not done, or for a ruling

- **PNG renders** not redone (needs the Mac's Chrome). **Run `gen.py` again after the switch's commit**: the boards were
  made with the switch off, so a printed board's blank placeholder reads *0 · printed*.
- **K3 deviates from the interface's draft** (for a ruling): the way back to an allowance is *type 0.2 in Gears!V2*, never
  *clear … again* nor *again*: after the Update the part holds the new figure, so a cleared (as-built) cell would keep it,
  and K3 cannot see whether the old cell was blank. B's `blank_cells` is the current cell's, so it does not answer this.
- **Choices for a ruling**: a pair is never read as built (the record is one gear's); Drive and Flat hidden on a bevel
  gear; Flat sent blank while Drive is round; with the switch off the cards' fixed copy says 0.2 while plans cut 0
  (placeholders and worked lines say what is cut).
- **Found, not fixed (outside F3)**: Open .gear.json never sets the form's Kind, so a helical or bevel record opens onto
  whatever Kind the form had (the tests set Kind first). F2_built.json's strip specs have a blank Flank (recipe ""), so on
  the real strip every change of them reads as structural; the tests write recipe A into their copy and say why.
- A's h-bound sentence says a negative distance (*The flat is -0.9 mm from the axis*) for a Flat past the axis: true, odd.

## Look at hardest

`_update_target` and `held_spec` against `_f2_strip_form` and `strip_form` (the stand-ins have no `_held_spec`); the
ruling-11 Build when a record stays open while the user designs something else; the placeholder's figure source.
