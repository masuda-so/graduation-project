# Where Does AI Opinion Aggregation Lose Minority Reasons?

[日本語](README.md) | [English](README.en.md)

## Overview

An undergraduate thesis project that traces, stage by stage, where low-frequency reasons and conditions are lost in the kouchou-ai pipeline compared with frequent ones (argument extraction → clustering → cluster labelling → overview), using the public comments on the Agency for Cultural Affairs' draft "Approach to AI and Copyright" as input. Prepared as the research output for the course "Graduation Project 2" (Fall 2026), Faculty of Environment and Information Studies, Keio University Shonan Fujisawa Campus (SFC). Author: So Masuda.

Status: planning stage (as of 2026-10-20). First progress presentation on 2026-10-26; final registration deadline 2027-02-01.

License: code (`pilot/` and future annotation/aggregation scripts) under MIT (`LICENSE`); documents, figures and annotation data (`docs/`, `literature/`, artefacts under `experiments/`) under CC BY 4.0 (`LICENSE-CC-BY-4.0`). Cite So Masuda and this repository when reusing.

## Features and limitations

- kouchou-ai is run unmodified at the pinned commit `eb38328d6cc9b93c767ff81fe28c3d518fc03ff8` through its official CLI (`packages/analysis-core`). Research code stays outside the pipeline (annotation, judgement, aggregation).
- One setting is changed at a time (extraction prompt; label sampling size); each condition runs five times and results are reported as ranges. Random seeds are not fixed.
- Comment texts are copyrighted by their submitters and are not included here. Only receipt numbers and annotation labels are published; the original texts are re-fetched from the agency's site.
- Third-party materials (paper PDFs, snapshots of other repositories) are not included either; `literature/sources-index.md` records their sources and SHA-256 digests.
- Not claimed: superiority of a new method, generalisation to all municipalities or models, representation of social minorities.

## Getting started and usage

1. Fetch kouchou-ai at the pinned commit and install it into a dedicated virtual environment.

   ```bash
   git clone https://github.com/digitaldemocracy2030/kouchou-ai.git vendor/kouchou-ai
   git -C vendor/kouchou-ai checkout --detach eb38328d6cc9b93c767ff81fe28c3d518fc03ff8
   uv venv .venv --python 3.12
   uv pip install --python .venv/bin/python -e "vendor/kouchou-ai/packages/analysis-core[embeddings,clustering]"
   ```

2. Put `config.json` and `inputs/<name>.csv` (columns `comment-id`, `comment-body`) under `experiments/<run-name>/`.
3. Dry-run first, then run.

   ```bash
   .venv/bin/kouchou-analyze --config experiments/<run-name>/config.json --input-dir experiments/<run-name>/inputs --output-dir experiments/<run-name>/outputs --dry-run
   ```

4. Use `args.csv`, `relations.csv`, `hierarchical_clusters.csv`, `hierarchical_*_labels.csv` and `hierarchical_overview.txt` in `outputs/` for the stage-wise judgement.

`experiments/trial-2026-10-17-pypi/` is a smoke test (PyPI release, five example comments from the official guide, gpt-4o-mini), not a research result.

## Support and documentation

### Repository layout

| Path | Contents |
|---|---|
| `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` | Working rules for AI coding agents (`CLAUDE.md` and `GEMINI.md` only import `AGENTS.md`) |
| `docs/` | Plans and notes; the schedule of record is `docs/スケジュール.md`. `docs/private/` holds internal memos and is not committed |
| `literature/` | Prior-work list, research map, survey notes, source index. `literature/sources/` is local only (read-only, not committed) |
| `experiments/` | Config, inputs and outputs, one folder per run: `experiments/<date-topic>/` |
| `pilot/` | Helper code for the setup trial (written by Codex) |
| `vendor/kouchou-ai` | Clone of kouchou-ai at the commit above (detached HEAD). Never edited |

### Related resources

- kouchou-ai: https://github.com/digitaldemocracy2030/kouchou-ai (AGPL-3.0)
- Input data: Agency for Cultural Affairs, Copyright Subcommittee, Legal Systems Working Group (7th meeting) materials https://www.bunka.go.jp/seisaku/bunkashingikai/chosakuken/hoseido/r05_07/
- Prior work: `literature/先行研究リスト_2026-10-15.md`
- Third-party materials and data: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

Questions go to GitHub Issues.

## Development and contributions

This is an individual thesis project and does not accept external changes. Error reports are welcome as Issues. See `docs/スケジュール.md` and `AGENTS.md` for the schedule, policies and agent working rules.
