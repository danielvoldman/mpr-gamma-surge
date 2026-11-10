# MS14 search log (G8 novelty re-check)

**Read this first (sub-step 16, DL-732 A2).**

1. **This log is NOT complete in the sense of the plan's Table 11.1.** The plan's MS14 row (docs/plan.md line 1365) asks for "Novelty re-check: Scholar (including cited-by checks on Xu 2023 and Borjigin 2013), PubMed, three slow-passage searches, Kalia journal version, eLife RP 104249, PMC12549018" with done-when "docs/search_log.md complete". The native Google Scholar and PubMed searches and the other checks of that row are missing: by the user's statement of 2026-11-10 (15:12 local time, America/Toronto; docs/ms14_user_reports_2026-11-10.md, last section) none of the items 1 to 7 was done natively.
2. **The user ruled on 2026-11-10 to proceed** without them (DL-732 A3). MS14 is therefore closed by user ruling as a departure from the plan; the plan is not edited.
3. **No search result is claimed by this log.** The only search record that exists is the plan's own Table E.1 (section 1 below), a general web-search pre-check of October 2026. The user's two earlier reports of 2026-11-10 (02:19 and 02:21) are WITHDRAWN by the user (15:12) and nothing in them is used here; their contents ("0 direct hits", "3 results", "4 results", the findings and the papers named) are not evidence of any search and must not be cited as such. They are kept, unchanged and marked withdrawn, in docs/ms14_user_reports_2026-11-10.md.
4. Claude Code searched nothing for this file (no internet) and makes no judgement of novelty. Gate G8 is not decided here.

## 1. The plan's Table E.1 (the web-search pre-check of October 2026; the only search record that exists)

Copied word for word from docs/plan.md by script (lines 1844 to 1867 of the plan as it stands; markdown escapes as in the file; a script check that these lines equal the plan's lines is recorded in DL-733). Row n (1 to 19) is plan line 1845+n, that is lines 1846 to 1864; row Q-F1 is line 1865, row Q-F2 line 1866, row S line 1867. The three columns are the plan's own and are the form of Appendix E.

| **\#** | **Query or action** | **Tool / database actually reached** |
| --- | --- | --- |
| 1 | model mechanism gamma surge dying brain cardiac arrest | Web search (hits: PNAS, PMC, ScienceDirect) |
| 2 | next generation neural mass model hypoxia | Web search (arXiv, eNeuro, J Neurophysiol, Frontiers) |
| 3 | Taher Avitabile Desroches bursting next generation neural mass slow passage | Web search (Springer, VU Amsterdam, ResearchGate) |
| 4 | computational model near-death gamma oscillations hypoxia network simulation | Web search (Frontiers, PMC, eLife) |
| 5 | neural mass model ischemia EEG oxygen deprivation Hopf bifurcation | Web search (bioRxiv, PMC, arXiv) |
| 6 | exact mean-field quadratic integrate-and-fire anesthesia propofol | Web search (arXiv, bioRxiv) |
| 7 | dying brain gamma surge mechanism computational model 2025 | Web search (ResearchGate, PNAS, ClinicalTrials.gov) |
| 8 | delayed Hopf bifurcation slow ramp neural mass model oscillation onset | Web search (APS PRE, PubMed, bioRxiv, Springer, arXiv) |
| 9 | hypoxia gamma oscillations interneurons model transient increase anoxia | Web search (Springer, PLOS ONE, eNeuro, PMC) |
| 10 | "cardiac arrest" EEG neural mass model simulation gamma | Web search (bioRxiv, PMC, PNAS) |
| 11 | Borjigin gamma surge mechanism model simulation interneuron hypoxia preprint biorxiv | Web search (bioRxiv, PNAS) |
| 12 | Montbrió Pazó Roxin model slow parameter ramp transient oscillations | Web search (arXiv, PLOS Comput Biol, APS PRX) |
| 13 | Li Borjigin 2023 gamma dying brain rat asphyxia | Web search (PubMed, PMC, Borjigin lab site) |
| 14 | next generation neural mass model anaesthesia loss of consciousness | Web search (Cell/Neuron, bioRxiv, Nature Comms Bio, arXiv) |
| 15 | next generation neural mass ion concentration potassium dynamics seizure spreading depolarization | Web search (arXiv, PMC, PLOS ONE) |
| 16 | "slow passage" Hopf "theta neurons" OR "quadratic integrate-and-fire" mean-field | Web search (PMC, Springer, arXiv) |
| 17 | Kalia Meijer van Putten neural mass ischemia EEG 2024 published | Web search (bioRxiv, ResearchGate, U. Twente) |
| 18 | agonal EEG terminal spreading depolarization model gamma before isoelectric | Web search (Wiley Ann Neurol, PubMed, OUP Brain) |
| 19 | arXiv dying brain gamma oscillations model 2024 2025 2026 | Failed (search budget exhausted, not executed) |
| Q-F1 | Fetch: biorxiv.org/content/10.1101/2025.08.04.668381v1.full | bioRxiv full text (introduction) |
| Q-F2 | Fetch: biorxiv.org/content/10.1101/2023.04.07.535995v1.full | bioRxiv full text (introduction + methods) |
| S | Subagent: 9 queries incl. "next generation neural mass model ischemia OR hypoxia OR anoxia", "Montbrió Pazó Roxin model hypoxia energy ATP neural mass", "spiking network model hypoxia transient gamma increase before isoelectric EEG", ""Li D" Borjigin 2023 dying brain gamma" | General web search only; no direct Scholar/PubMed/bioRxiv/arXiv querying |

What the plan says about this table (word for word, with plan line numbers):

> L1842: Source: RESULT A, "Search log (paste into search_log.md)", October 2026. This table is the content for docs/search_log.md (section 10.1). It records the G8 pre-check (verdict PARTIAL OVERLAP, section 12.7) and does not complete MS14, which also needs native Scholar and PubMed searches and the other checks in Table 11.1 \[R2, §6 rec. 6\].

> L1869: *Table E.1. G8 search log as recorded by RA. Fetch rows renamed Q-F1 and Q-F2 in v0.4 so they do not collide with figure IDs.*

> L1871: **Not reached directly:** Google Scholar, medRxiv, the PubMed search interface, and bioRxiv or arXiv native search. These sites appeared only as web-search results \[RA\].

> L1873: **Coverage and read depth** \[RA, Caveats\]. Results came from PubMed/PMC, bioRxiv, arXiv, PLOS, PNAS, Springer, APS, Frontiers and ResearchGate pages. The cited-by lists of Borjigin 2013 and Xu 2023 were not walked, and conference abstracts (CNS, SfN, BMC Neuroscience supplements) or non-indexed theses could have been missed. Roberts et al. 2023 and Schramm et al. 2019 (RA's year; Appendix A, 40 gives Prog Neurobiol 2020) were read as abstracts only; Kalia et al. 2023 as introduction and methods; the 2025 noisy-Hopf preprint as introduction; Taher et al. 2022 as abstract and introduction.

So Table E.1 is a general web search: the plan itself (lines 1871 and 1873) says that Google Scholar, medRxiv, the PubMed search interface and the native bioRxiv or arXiv search were not reached directly and that the cited-by lists of Borjigin 2013 and Xu 2023 were not walked. Which day in October 2026 each query was run is not stated by the plan (UNVERIFIED).

## 2. The MS14 items 1 to 7 (user statement of 2026-11-10, 15:12)

The first three columns are the plan's Appendix E columns, word for word (plan line 1844): `| **\#** | **Query or action** | **Tool / database actually reached** |`. Two columns are ADDED after them (Table E.1 has none): "Date" and "Result". Item names follow the plan's MS14 row (line 1365) and C20 (line 1467). Row ids MS14-<item><letter> do not collide with the ids of Table E.1. The result cell is the user's wording, exactly as the user asked it to be logged. Where the user's statement gives no query text, the cell says "not stated"; no query is listed as a search that was done.

| **\#** | **Query or action** | **Tool / database actually reached** | Date | Result |
| --- | --- | --- | --- | --- |
| MS14-1a | Item 1: Scholar, cited-by check on Xu 2023 | none (Google Scholar not reached natively); query text not stated | 2026-11-10 (user statement) | Not done natively on Nov 10; general web-search pre-check only |
| MS14-1b | Item 1: Scholar, cited-by check on Borjigin 2013 | none (Google Scholar not reached natively); query text not stated | 2026-11-10 (user statement) | Not done natively on Nov 10; general web-search pre-check only |
| MS14-2 | Item 2: PubMed, the two author queries | none (PubMed not reached natively); query texts not stated | 2026-11-10 (user statement) | Not done natively on Nov 10; general web-search pre-check only |
| MS14-3a | Item 3: slow-passage search 1 | none; query text not stated | 2026-11-10 (user statement) | Not done natively on Nov 10; general web-search pre-check only |
| MS14-3b | Item 3: slow-passage search 2 | none; query text not stated | 2026-11-10 (user statement) | Not done natively on Nov 10; general web-search pre-check only |
| MS14-3c | Item 3: slow-passage search 3 | none; query text not stated | 2026-11-10 (user statement) | Not done natively on Nov 10; general web-search pre-check only |
| MS14-4 | Item 4: Kalia journal version (check whether a published journal version exists) | none; query not stated | 2026-11-10 (user statement) | Not done natively on Nov 10; general web-search pre-check only |
| MS14-5 | Item 5: eLife RP 104249 | none; query not stated | 2026-11-10 (user statement) | Not done natively on Nov 10; general web-search pre-check only |
| MS14-6 | Item 6: PMC12549018 | none; query not stated | 2026-11-10 (user statement) | Not done natively on Nov 10; general web-search pre-check only |
| MS14-7 | Item 7: Taher 2022 full-text reading (plan line 1467, C20: "read the full text at MS14") | none; no full-text reading stated | 2026-11-10 (user statement) | Not done natively on Nov 10; general web-search pre-check only |

## 3. Notes by Claude Code (read from the plan; no judgement; no search)

- Which rows of Table E.1 relate to which MS14 item is NOT stated by the user. By the plan's own text only: line 1525 says RA ran four slow-passage or slow-ramp queries (Appendix E, queries 3, 8, 12 and 16), which bears on item 3; row 17 and row Q-F2 concern the Kalia preprint (item 4), and line 1873 says Kalia et al. 2023 was read as introduction and methods; row 3 looks up Taher and colleagues and line 1873 says Taher et al. 2022 was read as abstract and introduction (item 7: the full text was not read, as C20 asks). No row of Table E.1 contains "104249" or "12549018" (checked by script), so the pre-check has no row that names the eLife RP 104249 item (5) or PMC12549018 (6) (UNVERIFIED whether the pre-check covered them in some other way). The user's wording "general web-search pre-check only" is entered as given for all seven items; whether it is accurate for items 5 and 6 is the user's to say.
- The query texts of the withdrawn report 1 equal rows of Table E.1 (found in sub-step 15); they are not repeated here as searches of 2026-11-10.
- The plan's own note above Table E.1 (line 1842) says that the table "does not complete MS14, which also needs native Scholar and PubMed searches and the other checks in Table 11.1".

## 4. G8 outcome

The plan's G8 row (docs/plan.md line 1380, word for word, markdown escapes as in the file):

> | G8 Novelty | No close work found | An MPR hypoxia gamma model exists → reposition as a robustness, regime-map or E–I study and cite it as the precedent. A non-MPR model exists → keep the paper, stress what the exact mean field adds, add a comparison figure \[R2, §4\]. An MPR slow-ramp study exists → adopt its delay metrics \[R1, §4\]. v0.3 pre-check (RA): PARTIAL OVERLAP. MPR slow-passage studies exist (Taher et al. 2022 \[R1, §2.5; R5, SQ4; RA\]; Avitabile et al. 2022 \[single source: RA\]), and a non-MPR ischemia model exists without a surge (Kalia et al. 2023 \[R2; RA\]). v0.4: D41 decided (section 12.7): reframe as a first mechanistic model and cite Taher et al. 2022 and Avitabile et al. 2022 as method precedent; the third branch is met by A7's entry–exit delay metrics |

and the note under Table 11.2 (line 1382):

> *Table 11.2. Stop-or-continue gates. G0 and G5–G8 are new. Thresholds: G0, D34; G5–G8, D35. What each gate blocks: G0 blocks S5 onward; G1 sets the model for MS5 onward; G2 and G3 open MS12; G5–G7 limit or stop the claims that depend on them; G4 and G8 are report-only for the run order (G4 limits claims to the mean field; G8 shapes the manuscript at MS15).*

The plan does not say how the outcome is to be written down (UNVERIFIED). This log states no outcome and does not judge novelty.

**G8 outcome: to be written by the user.**

Because no systematic search was done, any novelty statement must be limited to what the web-search pre-check (Table E.1, section 1) supports.

## 5. MS14 status

MS14: native searches not done; proceed by user ruling 2026-11-10; this is a departure from the plan (the plan is not edited). Decision log DL-732 (A3).

## 6. What this log does not hold

1. Native Google Scholar searches, including the lists of papers citing Xu 2023 and Borjigin 2013: not done.
2. Native PubMed searches (the two author queries): not done.
3. The three slow-passage searches: not done natively; no query text is stated.
4. The check for a published journal version of the Kalia preprint: not done natively.
5. eLife RP 104249 and PMC12549018: not checked natively.
6. The full-text reading of Taher 2022: not done.
7. The day of each October 2026 query of Table E.1 (the plan gives the month only).
