# Independent correctness review

An isolated GPT-6.1 Sol / high read-only reviewer inspected new recipe modules, tests and packaging independently of implementation. It ran checks in the project environment and reported four actionable findings:

1. P1: hold/release tasks could pass after work on the wrong item because their final goal equaled the initial state.
2. P2: Arrow batch conversion unioned inventory dictionary keys across tasks, injecting unrelated null entries in model prompts.
3. P2: the first adapter test used an unknown provider model; changing to a recognized model then exposed construction-time rate-limit IO.
4. P2: report methodology claimed reference-fixture provenance for imported/model candidates.

Fixes: independently specified intermediate states plus matched-wrong-quantity and spare-item regression cases for all 41 hold/release tasks; per-row public JSON serialization; recognized model with rate-limit and inference IO stubs; source-aware report methodology. No goal fields enter generation inputs.

The reviewer rechecked all four fixes and ran the then-current recipe suite: **186 passed**, no remaining correctness blockers. It also identified a minor wording issue for --no-negatives; that was subsequently corrected to 'any included predefined corruptions' and a dedicated provenance regression test added. The final combined validation log includes this additional test and selected upstream checks. Live provider inference and full upstream GPU/integration suites remain unmeasured. This review is not a full security audit.
