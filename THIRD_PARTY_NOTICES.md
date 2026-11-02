# Third-Party Notices

This file supplements, and does not replace, the repository licenses. The MIT
license (`LICENSE`) covers the code written for this repository and CC BY 4.0
(`LICENSE-CC-BY-4.0`) covers its documents, figures and annotation data. The
third-party materials that the research depends on are listed below. None of
them is redistributed in this repository; each is referenced, re-fetched or
cited under its own terms. Sources and SHA-256 digests of the locally held
copies are recorded in
[literature/sources-index.md](literature/sources-index.md).

## kouchou-ai (広聴AI)

- Source: https://github.com/digitaldemocracy2030/kouchou-ai
- License: GNU Affero General Public License v3.0 (AGPL-3.0)
- Use: the official CLI of `packages/analysis-core` is run unmodified at commit
  `eb38328d6cc9b93c767ff81fe28c3d518fc03ff8`. The repository records this
  commit as a git submodule at `vendor/kouchou-ai`; the submodule is a
  reference, not a copy, and no kouchou-ai source code is included here.
  Research code (annotation, judgement, aggregation) stays outside the
  pipeline and is not a derivative work of it. Pipeline outputs under
  `experiments/*/outputs/` are results produced by running the tool on the
  author's inputs.

## Public comments on "Approach to AI and Copyright" (Agency for Cultural Affairs)

- Source: 文化庁 文化審議会著作権分科会 法制度小委員会（第7回）配付資料
  https://www.bunka.go.jp/seisaku/bunkashingikai/chosakuken/hoseido/r05_07/
- Terms: each comment is the work of its submitter and is not redistributed.
  Only receipt numbers and the author's annotation labels are published
  (`experiments/*/inputs/receipt-numbers.txt`,
  `experiments/*/annotation/`). Comment texts are re-fetched from the agency
  site by anyone reproducing the study; diagnostic files that would contain
  them are excluded by `.gitignore`.

## Papers and other collected materials

- Papers from the ACL Anthology (Barker et al. 2016, Huang et al. 2023,
  Zhang et al. 2024) are licensed CC BY 4.0 by the Anthology and are cited,
  not included.
- A Chiyoda City PDF, GitHub issue threads of kouchou-ai, excerpts of
  kouchou-ai documentation (AGPL-3.0) and files from `kouchou-ai-kit`
  (no license statement) are held locally for reading only under
  `literature/sources/`, which is excluded from the repository. Their
  provenance and digests are in `literature/sources-index.md`.

## Model outputs

- Pipeline runs call the OpenAI API (`gpt-4o-mini`) through kouchou-ai. The
  generated labels and overviews stored under `experiments/*/outputs/` are
  published as research data under CC BY 4.0 together with the configuration
  that produced them. No API credentials are stored in the repository.

Names and links above identify sources and license terms only. Nothing in this
file states or implies that the Digital Democracy 2030 project, the Agency for
Cultural Affairs, the ACL, Chiyoda City or OpenAI sponsors, endorses or
approves this research.
