# ToolCrop implementation plan

ToolCrop is an Apache-2.0 attributed Curator fork. Baseline: bespokelabsai/curator at `7fa08c5207c3b1fd5c1d0f15f1dc25a6547a3d8a`. Preserve history, Curator APIs, examples and license. Curator already provides structured generation, caching/retries, function calling and multi-turn agents. New work is a complete execution-filtered dataset recipe, not those existing features.

## Stages and v0.1 acceptance
1. Specify an in-memory inventory environment and independently authored declarative task goals. Freeze 100 development tasks and 24 held-out tasks with separate tool names/argument schemas. No generated code, network calls, shell or filesystem tool operations.
2. Add deterministic reference trajectories, optional Curator structured generation, strict call validation, bounded execution, independent final-state checks, rejection reasons, JSONL/chat export and HTML/JSON coverage reporting. Keep the validator independent of the candidate source.
3. Predefine wrong argument, missing required step, unavailable tool and wrong destination corruptions. Evaluate the same fixed pool with schema-only and execution-plus-goal filters. Report acceptance, execution success, coverage and limits; never claim model training gains.
4. Test invalid input, invariants, external candidate import, held-out separation, reproducibility, packaging and relevant upstream behavior. Obtain an independent implementation review. Clean-install release artifacts and reproduce evidence.
5. Publish grishahq/toolcrop v0.1.0 as an experimental prerelease with source, wheel, dataset, checksums and English notes. Verify release readback.
6. Prepare five LinkedIn posts and five X threads, two generated concept images plus genuine screenshot/chart, alt text, provenance and campaign status. Schedule only with verified account access and the portfolio's exclusive social lock.

Acceptance: 100 accepted offline reference trajectories, a separately reported 24-task held-out set, four corruption classes with explicit rejection reasons, deterministic exports, callable Curator adapter, clean install and retained upstream APIs. These are hand-programmed synthetic fixtures, not measured model generations. The held-out set tests schema adaptation and pipeline generality, not a trained policy's generalization.

## Roadmap
- v0.2: expand negative cases and coverage dimensions using external feedback; streaming/reactive model rollout with execution feedback; more independently reviewed task specifications.
- v0.3: a second contained environment and requested dataset integrations; independent training/evaluation before model-quality claims.

## Maintenance
Keep recipe modules separate under `src/toolcrop`; retain Curator namespace and upstream remote. Review upstream monthly, merge only with offline recipe tests and selected baseline tests passing. Do not rewrite published tags. Reproduce fixtures for each release, document compatibility and data format changes, and triage reported false accepts/rejects with minimal fixtures. No API keys are required for the offline path; live provider work requires separately configured credentials.
