<!-- CONFIG
archive_cadence: monthly
tail_lines: 120
-->

# Workflow Log — ci-agent-building

A record of meaningful stages in this project: decisions made, approaches agreed upon, and significant outputs produced.

## Field Taxonomy

- **Phase**: Planning / Implementation / Debugging / Review / Other
- **Initiator**: User / Assistant / Joint
- **User Engagement**: High / Medium / Low
- **User Action Type**: Problem framing / Constraint setting / Scope rejection / Target definition / Evaluation criteria / Planning & sequencing / Structuring / Approval only / Meta-analysis
- **Input Modality**: File attachment / URL / Named reference / Search instruction / In-conversation text / In-conversation artifact
- **Decision Dependency**: User-critical / User-influenced / Assistant-driven
- **Reason for deviation**: Disagreement / Missing context / Ambiguity / Quality / Other *(only if Decision Dependency is User-critical or User-influenced)*

## Entries

### S01 — Project Setup & Paper Ingestion Architecture — 2026-03-10

- **Phase**: Planning
- **Initiator**: User
- **User Engagement**: High
- **User Action Type**: Problem framing / Constraint setting / Planning & sequencing
- **Input Modality**: In-conversation text / Named reference (README.md)
- **Prompt summary**: User introduced the project goal (AI-assisted causal inference workflows, personal prototype now, team/public later). Asked about paper ingestion strategy, context management via subagents, extraction tiers, and team knowledge sharing.
- **AI output summary**: Recommended subagent-based paper ingestion writing to a repo-based `knowledge/` folder. Defined three extraction tiers (Deep/Standard/Skim). Created `knowledge/` folder structure with `index.md`, `paper_template.md`, and `papers/`.
- **Decision Dependency**: User-critical
- **Reason for deviation**: Ambiguity
- **Outcome**: Knowledge base folder structure in place; extraction tiers and template defined; ready to begin paper extraction.
- **Notes**: —

---

### S02 — Session Continuity & Memory Strategy — 2026-03-10

- **Phase**: Planning
- **Initiator**: User
- **User Engagement**: High
- **User Action Type**: Constraint setting / Evaluation criteria
- **Input Modality**: In-conversation text
- **Prompt summary**: User asked about handling context limits without losing history, session branching via `--fork-session`, and whether memory files could replace forking entirely for cross-session continuity.
- **AI output summary**: Explained `/compact`, `--fork-session`, and checkpoint rewind. Concluded that memory files are the primary continuity mechanism — forking/compacting only needed for mid-task continuity not yet in memory. Wrote initial `MEMORY.md` summarizing all project decisions to date.
- **Decision Dependency**: User-influenced
- **Reason for deviation**: Ambiguity
- **Outcome**: `MEMORY.md` written; session continuity strategy established.
- **Notes**: —

---

### S03 — References Catalog, Tier Tracking & Hook Infrastructure — 2026-03-10

- **Phase**: Implementation
- **Initiator**: User
- **User Engagement**: Medium
- **User Action Type**: Structuring / Constraint setting
- **Input Modality**: In-conversation text
- **Prompt summary**: User asked for a catalog in `references/` to track uploaded PDFs with a tier field, and a PostToolUse hook for this project only. Follow-ups: re-extraction signal design (Skim → Deep upgrade); Skim handling for non-standard papers; global hook should skip any project with its own `.claude/settings.json`; pre-approve `Bash(python *)` for subagents.
- **AI output summary**: Created `references/CATALOG.md` with mismatch-based re-extraction logic (Extracted column records tier-at-extraction). Created `.claude/settings.json` and `.claude/hooks/tool_audit.py` logging to project-level `tool_audit.log`. Updated global hook to defer via `.claude/settings.json` detection. Added `Bash(python *)` to project permissions. Fixed path-quoting bug in hook command.
- **Decision Dependency**: User-influenced
- **Reason for deviation**: Ambiguity *(re-extraction signal design; hook scope)*
- **Outcome**: Catalog and hook infrastructure in place; mismatch-based re-extraction logic established; subagents can run pdfplumber without approval prompts.
- **Notes**: Write tool remains unapproved for subagents by design — keeps a natural review checkpoint before extractions land on disk.

---

### S04 — Full Paper Extraction Run (All 5 Papers) — 2026-03-10

- **Phase**: Implementation
- **Initiator**: Joint
- **User Engagement**: Medium
- **User Action Type**: Planning & sequencing / Approval only
- **Input Modality**: In-conversation text / Named reference (CATALOG.md)
- **Prompt summary**: User requested extraction of all remaining papers. Agreed on Option 4 strategy: 3 lighter papers in parallel (Skim + 2 Standard), then Deep separately. Special instruction for IZA paper: pay close attention to replication methodology and exact steps. User approved pdfplumber install when Read tool failed due to missing pdftoppm.
- **AI output summary**: Ran 3 parallel background agents (2021 AER Standard, 2021 AER Appendix Skim, 2023 JoE Standard). Ran IZA Deep and 2004 QJE Deep sequentially. Resolved two issues mid-run: (1) pdftoppm missing → installed pdfplumber; (2) Write blocked for background agents → workaround: agents return content, main context writes files. All 5 extractions written to `knowledge/papers/`. Catalog updated with Extracted tiers.
- **Decision Dependency**: User-influenced
- **Reason for deviation**: Quality *(pdfplumber install needed; Write-blocking workaround adopted)*
- **Outcome**: All 5 papers extracted at assigned tiers; catalog fully up to date; pdfplumber installed for future runs.
- **Notes**: IZA extraction includes detailed Replication Notes section (exact Stata commands, numerical results, dataset details) per user's replication goal.

---

### S05 — Synthetic DiD Analysis Module (sdid/) — 2026-03-17

- **Phase**: Implementation
- **Initiator**: User
- **User Engagement**: Medium
- **User Action Type**: Target definition / Constraint setting / Approval only
- **Input Modality**: In-conversation text
- **Prompt summary**: User requested a simple, reusable Python tool for running synthetic DiD analysis with "one or a few clicks," rigorous and replicable, with sensitivity test options. Follow-up clarifications: Python + function/class interface; sensitivity tests to include pre-period length, outlier exclusion, inference method comparison, covariate variants, and estimator comparison (DiD vs SC vs SDID). User approved plan then directed to proceed with n_reps=10 for smoke tests; instructed to document timeout issues and move on rather than debug them.
- **AI output summary**: Identified `synthdid` PyPI package (v0.10.1) as the wrapping target. Applied two pandas-3.0 compatibility patches to installed package (`groupby.apply` → `transform` in `utils.py` and `vcov.py`). Built `sdid/` module: `core.py` (`SyntheticDiD` class, `SyntheticDiDResults`), `sensitivity.py` (`SensitivityRunner`, `SensitivityResults` with forest plot), `utils.py` (balance check, outlier detection, loader), `validate.py` (IZA replication validator). Built `notebooks/sdid_demo.ipynb`. IZA validation passes: Prop 99 ATT = -15.604, Quota ATT = 8.034. Sensitivity suite smoke-tested on 6 variants (baseline, SC, DiD, 2 pre-period trims, outlier drop) — all ran cleanly.
- **Decision Dependency**: User-influenced
- **Reason for deviation**: Quality *(pandas 3.0 incompatibility required patching upstream package; staggered inference too slow for full n_reps=200 — documented as known issue)*
- **Outcome**: `sdid/` module committed. Working prototype: one-call SDID/SC/DiD estimation + sensitivity suite, validated against IZA paper.
- **Notes**: Known perf issue: placebo inference ~1-3s/rep for block designs, ~26s/rep for staggered adoption. `synthdid` patches are to the installed package and will need re-applying after reinstall. Jackknife invalid for quota dataset (most cohorts have 1 treated unit).

---
