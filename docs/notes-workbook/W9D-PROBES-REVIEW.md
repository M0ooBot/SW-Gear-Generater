# Review of W9d's probes on SolidWorks 2026

*Independent, 2026-11-17, at `24aea8c` (branch `w9d`). I started no SolidWorks or Excel and changed nothing but this
file. Two implementers' uncommitted edits in the tree were left alone.*

- *Run 1:* `64acec9`, from snapshot `23ed8c5`, sections `faces`, `state` and `sub`. Log
  `probe/results/w9d-probes-sw2026-20261117-1-face-routes-none.log`, JSON `w9d-probes-20261117-140231.json`.
- *Run 2:* `890df13`, from `c86ad54`, `faces` alone with route r3. Log `…-2-faces-r3-clean.log`, JSON
  `w9d-probes-20261117-141450.json`.
- *Read:* both logs whole, the JSON wherever a proposal rests on it, the diff `23ed8c5..c86ad54 -- probe/w9d_probes.py`,
  `W9D-PROBES.md`, and the contract at `23ed8c5`.
- *Run here:* `--self-check` at `c86ad54`, 63 checks, 0 failed.

**Verdict.**

- **Every proposal but one is borne out by its lines and its JSON, and may be set for 2026** with the caveats below.
  `DEPENDENCIES_READ` may be set too, but only with a contract rule its reading does not cover (sub-assemblies).
- **r3 is held to a stricter standard than r1 and r2, not a weaker one.** I found no way its log could read clean
  while the route is wrong.
- **One must-fix before package A writes tier 1's face and edge read: r3's cost.** The contract must say how the walk is
  bounded. The growth itself should be measured in the 2024 run.
- **The revision is worth stating.** Both runs attached to **34.0.0**. W9c's S5 ran on 34.1.1 (`w9c…-2.log:4`). The
  `_ON_2026` findings set from these runs will also stand for 34.1.1. One reading disagrees between the two (the
  marking route, below), so each comment should name the revision.

## The new route, r3, read as code

`route_r3` (`c86ad54`) does the following:

1. It lists every face (or, for an edge entity, every edge) of the component's part, over `GetBodies2(0, True)`: solid,
   visible bodies.
2. It carries **each** candidate into the assembly by `IComponent2.GetCorresponding` and compares it with the mate's
   entity by `ISldWorks.IsSame`. It walks them **all**, so the matches are counted, and exactly one is required.
3. It reads that part entity's place (`where_in_part`) and its coaxial read.
4. It reads `GetPersistReference3` in the part and resolves it with `GetObjectByPersistReference3`. The code is named
   through `swPersistReferencedObjectStates_e`.
5. It requires the resolved object to be the entity's own kind, `IsSame` to the part entity (`same_part`), and, carried
   back through the component, `IsSame` to the mate's entity (`same`).
6. It brackets itself with every document under the copy's folder. A bracket that started marked is unclean
   (`marked_before`).

`persist_verdict` checks a marked start, a mark, and a match count other than one *before* anything else. Where
`same_part` is present it demands both `IsSame` answers. There is **no area fallback** for r3; the self-check holds
that: "r3: carried back not the mate's entity, or IsSame unanswered: not clean (no area fallback)". r1 and r2 are
unchanged.

**Could it read clean while wrong?** I looked for four ways.

- *`IsSame` answering 1 for any two faces.* Then every one of the 163 faces would match, and the count would not be 1.
  The count is the control, and it read 1 of 163, 1 of 235 and 1 of 482.
- *A face of another instance of the same file.* Sprocket-5, -6 and -7 are one file. The candidates are carried
  through *this* component, and `IsSame` is against this component's entity, so another instance's face cannot match.
  (c) then remade all four mates on the new instances with every frame at 0.0 and every definition equal
  (`-2.log:96-101`).
- *A trivially true in-session round trip.* `same_part` is close to tautological in one session: the reference read
  from that object resolves to it. The real test is (d): every reference resolved in the part reopened alone, `Ok`,
  with the same kind, the same place and the same area (`-2.log:103-104`).
  - "Place" separates the two end faces of one sprocket, which have equal areas: z 0.006 against z 0.0
    (`UserFaceCoin:0` and `:1`). That was the weakness S-c named, now closed.
- *Brackets that could not see.* (a) saved the copy, and (b) started with every document unmarked and ended so
  (`-2.log:82`; the JSON's `flags_before` and `flags_after` are all False). Each r3 call's own bracket is `[]` / `[]`.
  (c)'s three flag reads are all False. (d)'s brackets are clean.

The JSON bears every one of these out (per entity: walked, matches 1, `same_part` 1, `same` 1, code 0, marked `[]`,
reload place equal).

## The findings, one by one (2026)

Set each `_ON_2026` as follows. The comment beside each should carry its caveat and cite the log lines; the run
revision is 34.0.0 throughout.

| Finding | Set `_ON_2026` to | Caveat the comment must carry |
|---|---|---|
| `COMPONENT_STATE_PER_CONFIGURATION_ROUTE` | `"IConfiguration.GetComponentSuppressionState(Name2)"` | Agreed with the shown truth on 3 components × 3 modes, from an unmarked start, marking nothing (`-1.log:114-118`). Covered: suppressed in the mode showing (Housing-1 in H) and in another (Sprocket-4 in L). It reads a lightweight component False (not suppressed) (`:121`). Top-level `Name2` only. Run on **34.0.0**: there `GetRootComponent3(True)` per configuration marked nothing (`:117`), where W9c measured it marking on 34.1.1 (`w9c…-2.log:282`). Marking can differ by revision or state, so R.6's check after the read stays the guard. |
| `COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED` | `True` | One component suppressed in one mode, unsaved, read right (`:119-120`). |
| `FILE_VERSION_READ` | `"ISldWorks.VersionHistory(path), its last entry against GetLatestSupportedFileVersion"` | The copy just saved read last `19000[2025/260]` against latest 19000. The negative control, a 2024-saved assembly, read `17000[2024/282]` (`:122-123`). Compare the **number**, never the year label: SolidWorks 2026 labels itself 2025. Take the **last** entry: the 2026 file's history begins with 17000 (its template). |
| `DEPENDENCIES_READ` | `"ISldWorks.GetDocumentDependencies2(path, False, False, False), each one's VersionHistory"` | It named all nine parts (`:124-125`). Traverse is False, so the paths are **top level only**: a referenced sub-assembly's own files are not listed. The paths are the **stored** ones (Searchflag False). Here the copy had just been saved in place in (a), so they were the copy's files. That is my inference: the JSON keeps file names only. A path not on disk, or a history that does not read, is not the running version. |
| `OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS` | `True` | Two user parts stood in for the app documents R.2 allows: one changed (a global added), one unchanged. Each was open, with the same flag and not read-only after the open and after the shows, and the change was kept (`:126-127`). The read-only assembly itself read **modified** straight after its open (warning 32, NeedsRegen) beside the changed part. See below. |
| `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN` | `True` | Files saved by this version only. Closed by `QuitDoc` **with its flag True** (shown, NeedsRegen), with no dialog, every document it loaded gone, no file time changed, and the open parts as they were (`:128-129`). |
| `SUBASSEMBLY_OPEN_MARKS` | `False` | A healthy one-part sub-assembly with no configurations of its own, opened Silent and not loaded: flag False straight after and 5 s later (`:135-136`). One with a missing part marks (W9c, `SUBASSEMBLY_MISSING_PART_READS`). |
| `SUBASSEMBLY_READ_ONLY_INSERT` | `True` | Inserted with its child. The sub-assembly read flag False and read-only after the insert; the host it went into read modified, as it is the job's own (`:138-139`). |
| `SUBASSEMBLY_OPEN_MARKS_WHEN_LOADED` | `False` | Loaded as a component of an open host; `OpenDoc6` answered warning 128, flag False before, after the open and after the insert (`:141-142`). |
| `PERSIST_REFERENCE_ROUTE_FOR_FACES` | r3's route string as proposed (`-2.log:89`) | 5 faces on two files: one cylinder (a bore), three sprocket end planes, one Sun end plane. r1 is dead on 2026: `GetCorrespondingEntity2` gives nothing for a mate's entity, so `GetPersistReference3(None)` fails. r2 is dead too: the reference resolves `swPersistReferencedObject_Invalid`. **The walk's cost grew through the session** (0.26 s to 8.1 s for the same 163 faces), and the contract bounds it (must-fix 1). |
| `PERSIST_REFERENCE_ROUTE_FOR_EDGES` | the same string (`-2.log:90`) | One circular edge; 482 edges walked in 8.2 s. |
| `PERSIST_REFERENCE_SURVIVES_RELOAD` | `True` | 6 references (5 faces, 1 edge) resolved `Ok` in their parts reopened alone and unchanged on disk: kind, place and area as read, nothing marked (`-2.log:103-104`). A part edited and saved since may resolve otherwise. Any code but `Ok`, or another kind, is `WHY_NOT_FOUND`. |
| `COAXIAL_FACE_READ` | `True` | Cylinders only, by `CylinderParams` of r3's part-level entity, in part coordinates (`-2.log:92-93`). Positives: the sprocket's bore, and Sun's 29 tip and 29 root cylinders. Negatives: Sun's User Keyway (Ø3 at (5, 0)), **Sun's 58 root-fillet cylinders (r 0.475, app-made and off-axis)**, and every plane. |
| `CARRY_INSERT_MARKS_USER_DOCUMENTS` | `False` | One case: user parts loaded as components of the open old assembly, unchanged, opened (activated) and inserted into a second assembly, which marked none of them (`-2.log:101-102`). A user part open in its own window with unsaved edits is not measured. |
| `REFERENCED_CONFIGURATION_READ` | stays **None** | Every component references its file's only configuration (`-2.log:94`). M9 sets it, on Sprocket-11 (R2). |
| `VIRTUAL_READ`, `PATTERN_INSTANCE_READ` | stay **None** | Read negative only (`-2.log:95`). |

**Facts for the contract, not findings:**
- (a): Sprocket-4's three mates read **on** in L, where Sprocket-4 is suppressed (`-1.log:113`). A mate's own flag is
  what `IsSuppressed2` reads, not its effective state. That bears out §3 C.6.1's "left as SolidWorks has it".
- (f): setting **one** Sprocket instance lightweight read **every** instance of `Sprocket.SLDPRT` lightweight (`:121`).
  So D10's `WHY_LIGHTWEIGHT` falls on every instance of that file, as each one's own read will say. The question should
  not be surprised by it.
- (f), the root read with a lightweight component: both `GetRootComponent3(False)` and `(True)` answered `RangeBox`
  and resolved nothing. Whether either marks is still unknown, so `_read_user_work`'s rule stands.

## The two things the run agent flagged

**(a) The read-only document read modified straight after its open.**

What was read: `OpenDoc6` answered warnings 32 (NeedsRegen), and `RangeBox.SLDASM` read flag True and read-only
(JSON: `state/read_only/after_open`). The changed `Sprocket.SLDPRT` was beside it, and the unchanged `Housing.SLDPRT`
read False before and after.

*Ruling: `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN = True` stands.*

- §0.3's STOP is about a read W9 adds marking a document of the **user's**: one they have open, or a file of theirs.
  This document is the job's own in-memory, read-only load, opened and closed by the job. Its file time did not change,
  and every document the user had open read as before.
- The case that could have hurt was measured in exactly this state: `QuitDoc` of a read-only document with its flag
  True, after shows, with no dialog.

*The contract needs a sentence, for package A.*

- §3 R.1 lists the session's documents and flags *before* the open. R.6 then flags "any turned on". As written, the
  job's own read-only document would read "turned on" (absent before, True after) and stop every not-open carry with an
  app document changed beside it, with a false *"Reading RangeBox.SLDASM marked …"*.
- *Edit:* the job's own read-only document is judged from its flag read straight after its `OpenDoc6`. True there
  (warning 32, measured beside a changed part) is logged, not a mark; only a turn after that read counts, as for every
  other document.
- R reads that document without rebuilding it. Say in §11.2 that its frames and mates are read as loaded, before any
  regeneration. A changed app part beside it could make them differ from what a rebuild would show. I infer that; it
  was not measured.

*Does the unmeasured case (no changed part beside it) matter?* No.

- W9c's s5 (d) read the read-only open with nothing open beside it: flag False, warnings 0 (`w9c…-2.log:291`).
- The close is the harder of the two cases, and it was measured with the flag True.
- With the sentence above, R.6 does not depend on which flag the open leaves.

**(b) r3's cost grows through the session.**

The same 163-face walk timed 0.26, 2.09, 3.66 and 8.08 s across one job (`-2.log:83-88`). The 482-edge walk took 8.2 s
and Sun's 235 faces 5.6 s. That is about 50 ms per `GetCorresponding` + `IsSame` by the end, up from 1.6 ms. Why is not
known. It may be per-call accumulation or a slowing of the whole session.

R runs **before the build** (D1), so a slower session would also slow the build that follows. A user's assembly may hold
dozens of face mates on parts of thousands of faces. Unbounded, this is minutes per carry, or worse.

*What the contract must tell package A (must-fix 1):*
1. **One walk per component.** Group all of that component's face and edge entities. List its part's faces (and edges)
   once, and carry each candidate by `GetCorresponding` **at most once**, comparing it with every entity of the group.
2. **Prefilter before `GetCorresponding`, cheaply, by area for a face:** the part face's `GetArea` against the mate's
   entity's `GetArea`, to a relative 1e-9. The area is read in the part, so no call into the assembly is needed. For an
   edge, a circle against a circle of the same radius (`CircleParams`), a line against a line.
   - The decisive test stays `IsSame`, so the filter can lose no true match. A part face and its assembly
     correspondent have one area, as every entity of both runs shows (`area` pairs equal).
   - On these parts it leaves a handful: 2 equal end faces, 29 tip cylinders.
3. **Keep counting within the filtered set, exactly one required.** Uniqueness was measured 6 of 6, and after the
   filter counting costs almost nothing. Do not stop at the first match.
4. **A cap.** If a component's filtered candidates exceed a number (say 200), or its walk exceeds a time budget (say
   20 s), its remaining entities are named, not searched: `WHY_UNREAD` with the clause *"SolidWorks took too long to say
   which face of Sprocket-5 it is"*. A cap should never stop the carry.

*The growth itself* should be measured before M9 relies on it. M9's few face entities would pass, but they would not
tell us how it scales. In the 2024 run, and in a short 2026 rerun of `faces` (b) alone:
- the same walk repeated five times on one entity, each timed;
- a fixed cheap call (`component_frame` × 100) timed before and after the walks, to tell per-call growth from a slower
  session;
- the area-prefiltered walk timed beside the full one;
- SolidWorks' private memory before and after.

That is a few minutes. Until it is known, the cap is the contract's answer, and the caveat stays on the finding.

## Must fix

**1. Bound r3 in the contract (§10, §4.1)**, as (b) above. Package A's `entity_reference` must implement the walk with
the grouping, the area prefilter, the count and the cap. The fake should model a cap reached.

## What the contract must now change (for the designer)

- **§4.1**
  - *Old:* the paragraph "The route from the assembly-context entity … `GetCorrespondingEntity2` … the probe measures it
    beside handing the assembly entity straight to the part's `GetPersistReference3` (§11.4), each route per entity
    kind."
  - *New:* for a face or an edge, the part-level entity is the one face (or edge) of the component's part that,
    carried by `IComponent2.GetCorresponding`, is `IsSame` as the mate's entity: walked once per component, prefiltered
    by area (a circle's radius for an edge), exactly one, capped (§10). Then the part's `GetPersistReference3`, resolved
    by `GetObjectByPersistReference3`, must answer `swPersistReferencedObject_Ok`. `GetCorrespondingEntity2` gives
    nothing for a mate's entity, and the part's `GetPersistReference3` on the assembly entity resolves Invalid (2026,
    `w9d…-1.log:51-80`).
  - The table: face and edge rows **measured on 2026** (`w9d…-2.log:83-90`), the reload row measured (`:103-104`),
    2024 not yet.
- **§10 `entity_reference`**
  - *Old:* "the face and edge route as the probe finds it, per kind".
  - *New:* r3 with must-fix 1's four rules, returning `(kind, hex, coaxial, why)`, the cap's clause in `why`.
- **§11.4**
  - *Old:* "two routes to the part-level reference (`GetCorrespondingEntity2` in the assembly; the mate's entity
    straight to the part's `GetPersistReference3`) … *Ruled*: … by the route the probe proposes".
  - *New:* say that r1 and r2 read nothing on 2026 and r3 read all six clean, both ways, and survived a reload. Add the
    timings.
- **§2.2 `OldEntity.coaxial`, §2.3's `part new` slot, §4.4.**
  - *The problem:* "bore" is said wherever `coaxial` is True on a cylinder. Sun's 29 tip and 29 root cylinders read
    coaxial, so a mate on a tooth tip would be worded *"on Sun's bore"*.
  - *New:* "bore" only for a coaxial cylinder whose radius is the old part's `Bore Diameter`/2. The global is on record
    for every app gear part, and a gear with no bore has none. Otherwise say *"a face of Sun on its axis"*.
  - This needs the radius in `OldEntity` (`radius_mm: Optional[float] = None`): a shape change through you.
- **§4.3**
  - *Old:* "every rotational face the app makes on a gear (a bore, a relief) is coaxial with `Gear Axis` by
    construction".
  - *New:* the app's own faces are not all coaxial either. Sun's 58 root fillets are off-axis cylinders (r 0.475), and
    the rule's `coaxial` read decides, not where the face came from.
- **§15 (M9).** *Old:* "the face variant is shown on the fake only, since no face of Sun is coaxial". *New:* Sun's root
  (or tip) cylinders are coaxial (`w9d…-2.log:92`). So M9 can show a user gear mate picked on Sun's root cylinder taken
  as `Gear Axis`, and one picked on a root fillet named. Add both.
- **§11.1, D2 and §9.1's states clause.** *Old:* written as though no clean unshown route may exist. *New:* on 2026
  `COMPONENT_STATE_PER_CONFIGURATION_ROUTE` is set (and `…_READS_UNSAVED` True), so the states are read unshown in both
  situations. D2's fallback (the mode showing's state in every mode, said) is the path where the finding is None (2024
  until its run), and the not-open path's per-mode show is used only there. M9's judged list keeps its two branches.
- **§3 R.1/R.6 and §11.2.** The job's own read-only document is judged from its flag straight after its open, and read
  as loaded, without a rebuild (3 (a) above).
- **§3 R.2's `DEPENDENCIES_READ` condition.** Add three things:
  - the paths are the stored ones, top level only;
  - any dependency that is itself an assembly (`.SLDASM`) refuses the not-open read, since its own files are not
    listed (Traverse False), until a run reads with Traverse True;
  - a path not on disk, or a history that does not read, refuses.
- **§13 item 8.** Closed on 2026: both findings are set, and a closed file saved by the other version is refused
  without being opened. Open on 2024 until its run.
- **§8.** Set-by entries for the faces, edges and reload findings: `w9d…-2.log`, r3. A new row is not needed.

## The 2024 run (all three sections with r3, about 40 minutes)

*Change before it runs:*
- Log each dependency's **full path relative to the run folder**, and whether it is under the copy (`DEPENDENCIES_READ`'s
  inference above).
- Add the growth measurement of (b), run once.

Optionally read `GetDocumentDependencies2(path, True, False, False)` beside it. It is a closed-file read, which would let
R.2 accept a sub-assembly. Make sure `--other` names a file **2026 saved**, so 2024's negative control reads newer.
`VersionHistory` is verified on 2026 only in the ledger; a closed-file read of a newer file should not open it. That is
my inference, so watch the line.

*What could differ on 2024:*
- **`GetComponentSuppressionState`** may mark, or read otherwise. 2024's W9c run saw `GetRootComponent3(True)` mark
  (`w9c24:283`).
- **The read-only open's NeedsRegen flag**, and whether `QuitDoc` of a flagged read-only document asks. The "Save
  Modified Documents" box of GOTCHAS §100 was seen once on 2024, from `CloseDoc`.
- **r3's timings.** Expect about twice 2026's, and the growth with them.
- **The version numbers.** 17000 for 2024; the year label may again lag.

The face routes r1 and r2 are likely dead there too, and the sub-assembly opens likely as on 2026 (W9c's P2 was alike
on both).
