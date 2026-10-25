# ToolCrop v0.1.0 — experimental

A reproducible execution-filtered tool-use dataset recipe, built as an attributed Apache-2.0 fork of Bespoke Labs Curator at `7fa08c5207c3b1fd5c1d0f15f1dc25a6547a3d8a`. Curator's library, synthetic-data/bulk-inference capabilities, examples and history are preserved.

## Included

- One contained in-memory inventory environment with strict, bounded tool calls; no generated shell, filesystem or network side effects.
- 100 development and 24 separately exported held-out task specifications, with independent final-state checks and required intermediate checkpoints.
- Deterministic multi-step reference trajectories, four predefined corruption classes, reasoned rejection records, chat JSONL and HTML/JSON coverage reports.
- An optional Curator structured-generation adapter. Live model inference is not part of this release's measured evidence.

## Reproduce

Install the attached `toolcrop_curator-0.1.0-py3-none-any.whl` with Python 3.11 and `python -m pip install /path/to/the.whl`, then run `toolcrop demo --output reproduced` and open `reproduced/report.html`. Or clone the repository, check out `v0.1.0`, and run `python -m pip install .`.

The attached inventory fixture bundle includes accepted/rejected records, actual simulator traces, split chat exports, methodology and SHA-256 digests. `SHA256SUMS` covers the attached build/data artifacts. The source archive and wheel retain Apache-2.0 LICENSE and attribution NOTICE. Do not install bespokelabs-curator and toolcrop-curator in the same environment: they share the Curator namespace. No package-registry publication is required.

## Evidence and limits

197 recipe/selected upstream tests pass; new-code lint/format checks pass; an isolated correctness review's four findings were fixed and rechecked. Clean wheel installation preserves Curator imports and reproduces all output digests.

Same 620 controlled fixture trajectories: schema checks admit 496, error-free execution admits 372, execution plus independent goals/checkpoints admits 124. All 100 development and 24 held-out references pass; all 496 predefined corruptions are rejected. Acceptance is 20% and executable success is 60% on each deliberately corrupted split; accepted task coverage is 100% on this small registry.

These are deterministic templated fixtures, not measured model generations, independent statistical trials, a model-quality improvement, production-safety evidence or adoption. The held-out schema is explicitly supported by the reference planner and shares task families/grammar. Full upstream GPU/provider integration suites and live provider calls were not run. The adapter plans whole sequences; reactive tool-feedback rollout is future work.

See README, toolcrop_docs/DATA_CARD.md, evidence/README.md, CHANGELOG.md and IMPLEMENTATION_PLAN.md for commands, provenance, roadmap and maintenance scope. v0.2 expands negative cases/coverage and reactive rollout; v0.3 adds another contained environment and requested integrations. This fork is not an official Bespoke Labs release.
