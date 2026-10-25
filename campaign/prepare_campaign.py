"""Prepare the authorized campaign only after actual release readback exists."""

import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
release = json.loads((root / "evidence/published-release.json").read_text())
assert release["publishedAt"] and not release["isDraft"]
repo = "https://github.com/grishahq/toolcrop"
R = release["url"]
D = repo + "/blob/v0.1.0/toolcrop_docs/DATA_CARD.md"
E = repo + "/blob/v0.1.0/evidence/inventory-v1"
items = [
    {
        "id": "01-problem", "audience": "Dataset authors and developers building tool-use benchmarks",
        "hook": "The JSON is valid. The tool runs. The training example is still wrong.",
        "evidence": [E + "/rejected.jsonl", "development-000:wrong_argument", "src/toolcrop/contracts.py", "recipe_tests/test_recipe.py"],
        "cta": "Run the fixture and inspect the residual inventory before admitting a tool-use example.",
        "asset": "assets/concept-filter.png", "asset_type": "AI-generated conceptual illustration",
        "alt_text": "Conceptual ToolCrop illustration: instruction cards pass through a transparent mechanical test rig. Mint building blocks continue and amber cards are diverted. Text: ToolCrop. Plausible is only the start. This is artwork, not measured software output.",
        "linkedin": f"""The JSON is valid. The tool runs. The training example is still wrong.

Here is a small, reproducible failure: a task asks to ship one item. The proposed sequence reserves two and ships one. Both tool calls execute. One item remains reserved, so the task's declared final state is wrong.

A dataset pipeline that checks only function names and argument types can keep that example. A pipeline that checks only for execution errors can keep it, too.

I built ToolCrop as an attributed fork of Bespoke Labs Curator to make that gap inspectable. Its first recipe runs multi-step inventory trajectories in memory, compares their results with independently specified goals, and exports accepted and rejected rows with reasons.

This example is a deliberately constructed fixture, not a claim about how often a model makes the mistake. The useful engineering question is narrower: can the dataset check distinguish an executable sequence from a completed task?

Try development-000:wrong_argument in the checked-in rejection records. Read the residual reservation and the final-state mismatch. Then ask what equivalent failure could enter your own dataset.

Code and offline quickstart: {repo}

Curator already supplied generation, structured outputs and caching; ToolCrop adds this execution-validation recipe. Concept image is AI-generated artwork, not a product screenshot.""",
        "x": [
            "1/4 Valid JSON. Real tool execution. Still a bad training example. A fixture asks to ship one item; the sequence reserves two and ships one. Every call runs, but one item stays reserved.",
            "2/4 Checking the function schema misses that. Checking only for runtime errors misses it, too. The independently specified final inventory catches it. This is a controlled counterexample, not a measured model failure rate.",
            "3/4 ToolCrop adds an inventory dataset recipe to Bespoke Labs Curator: execute proposed calls, check trusted goals, retain reasons, export accepted/rejected rows. The image is conceptual AI artwork, not a screenshot.",
            f"4/4 Reproduce without an API key: run toolcrop demo and inspect development-000:wrong_argument in rejected.jsonl. What equivalent residual state could your dataset miss? Code: {repo}",
        ],
    },
    {
        "id": "02-tradeoff", "audience": "Agent benchmark engineers and small-model dataset teams",
        "hook": "A successful API response is only one part of a tool-use label.",
        "evidence": [D, "src/toolcrop/validators.py", "recipe_tests/test_recipe.py::test_hold_release_requires_requested_intermediate_state"],
        "cta": "Review the oracle and contribute a minimal false-accept example.",
        "asset": "assets/concept-destination.png", "asset_type": "AI-generated conceptual illustration",
        "alt_text": "Conceptual ToolCrop artwork shows a parcel at a forked mechanical route. A mint route reaches the intended dock; an amber route reaches a dock marked with a cross. Text: ToolCrop. Check the destination, too. No empirical result is depicted.",
        "linkedin": f"""A successful API response is only one part of a tool-use label.

The straightforward filter is attractive: validate the schema, execute the calls, keep anything that returns successfully. It is fast to understand, but it cannot tell whether stock reached the requested destination or an unrelated dock.

ToolCrop makes a deliberate tradeoff: start with one small environment whose success conditions can be specified independently. The generator sees the request, starting state and tool schemas. The evaluator owns the trusted goal. A generated answer cannot rewrite its own pass condition.

Review exposed a more subtle case. 'Hold three items, then release them' ends at the initial state. A final-state-only validator could accept holding the wrong item. The fix was a separately specified intermediate checkpoint, plus regression cases for wrong items and matched wrong quantities.

That extra specification costs effort. It also makes the guarantee narrower and easier to inspect: the trajectory must execute and satisfy declared state/checkpoint predicates. The recipe does not prove every possible policy constraint or optimal plan.

Curator supplies the generation infrastructure; ToolCrop adds this contained validation workflow. Arbitrary external tools remain outside the environment.

Oracle, methodology and limits: {D}

If you can produce a false accept, open a minimal fixture. That is more useful than a larger synthetic row count. Illustration is conceptual AI artwork.""",
        "x": [
            "1/4 A successful tool response does not prove the task succeeded. Shipping to the wrong dock can execute perfectly. Dataset labels need a goal that exists independently of the proposed trajectory.",
            "2/4 ToolCrop's tradeoff: one small in-memory inventory environment, trusted declarative goals, bounded calls. Curator handles generation; the evaluator owns execution and judgment. A candidate cannot replace its own oracle.",
            "3/4 Review caught a trap: hold-then-release ends at the starting state. Work on the wrong item could pass a final-state-only check. We added independent intermediate checkpoints and regression fixtures for all 41 hold/release tasks.",
            f"4/4 This checks declared conditions, not arbitrary tool safety or optimal planning. Review the oracle; send a minimal false accept. Methodology: {D} Concept image: AI-generated artwork.",
        ],
    },
    {
        "id": "03-demo", "audience": "Developers who need a runnable tool-use dataset recipe",
        "hook": "A tool-use dataset demo you can reproduce without a model key.",
        "evidence": [E + "/report.json", E + "/report.html", "evidence/clean-install.txt", "campaign/assets/real-report-screenshot.jpg"],
        "cta": "Run the demo, then validate your own proposed calls against a trusted task ID.",
        "asset": "assets/real-report-screenshot.jpg", "asset_type": "Genuine screenshot of the generated HTML report",
        "alt_text": "Actual ToolCrop HTML report for 620 controlled offline trajectories. Table shows 124 references accepted; 124 examples in each of four corruption classes rejected. Wrong argument and wrong destination rows execute successfully but have zero goal matches. No model experiment is measured.",
        "linkedin": f"""A tool-use dataset demo you can reproduce without a model key.

ToolCrop's first recipe produces 100 accepted development trajectories and a separate 24-task held-out export. The reference planner and negative examples are deterministic, so you can inspect the whole pipeline before spending on model generation.

Run 'toolcrop demo --output reproduced', then open reproduced/report.html. The attached screenshot is the actual generated report. Expand a rejected record to see its proposed calls, executed tool results, final inventory and rejection reasons.

The output includes candidates.jsonl, accepted.jsonl, rejected.jsonl, separate development/held-out chat records and checksums. Initial state and tool schemas travel with the accepted chat records; converting them for a training provider is a separate step.

To test your own proposals, supply JSONL rows with exactly task_id and calls. The selected trusted task registry supplies the goal. Invalid tool calls become reasoned rejections instead of disappearing from the audit trail.

The optional adapter uses Curator's structured generation. This release's evidence uses offline reference fixtures and stubbed provider IO, not live model results. The adapter plans whole sequences; reactive tool-feedback rollout is future work.

Quickstart and examples: {repo}

Run it, inspect one rejection, and tell me which missing check would matter in your environment.""",
        "x": [
            "1/4 A runnable tool-use dataset recipe, no model key needed: ToolCrop's offline demo emits 100 accepted development trajectories plus a separate 24-task held-out export. Screenshot: the real HTML report.",
            "2/4 Run: toolcrop demo --output reproduced. Open reproduced/report.html. Inspect a rejection: proposed calls, actual simulator results, final inventory, and why the goal failed.",
            "3/4 Exported: accepted/rejected JSONL, separate split chat records, tool schemas, initial-state metadata, coverage and checksums. These are reference fixtures. The optional Curator generation adapter is not a measured live-model experiment.",
            f"4/4 Next, feed your own task_id + calls JSONL through toolcrop validate. The registry owns the oracle. Try it and report one missing check: {repo}",
        ],
    },
    {
        "id": "04-experiment", "audience": "Dataset researchers and engineers evaluating validation pipelines",
        "hook": "Same 620 trajectories. Three different admission decisions.",
        "evidence": [D, E + "/report.json", "scripts/plot_evidence.py", "campaign/assets/filter-comparison.png"],
        "cta": "Reproduce the counts and propose a corruption that the current oracle misses.",
        "asset": "assets/filter-comparison.png", "asset_type": "Matplotlib chart calculated from actual exported counts",
        "alt_text": "Chart of the same 620 controlled ToolCrop fixtures: schema validation admits 496, error-free execution admits 372, and execution plus independent goal/checkpoint checks admits 124. Pool: 124 reference plans and 496 predefined corruptions in one toy inventory environment. These are not measured model performance results.",
        "linkedin": f"""Same 620 trajectories. Three different admission decisions.

I evaluated ToolCrop's first inventory recipe with a fixed pool: 124 reference plans and four predefined corruptions per task. Each method receives the same proposed calls and initial state. No extra model budget, retries or regenerated candidates.

Schema checks admit 496 trajectories. Requiring error-free execution admits 372. Adding independent final-state and required checkpoint checks admits 124: all references and none of the injected corruptions.

That means the schema-only baseline admits 372 corrupted rows in this pool; execution-only admission still admits 248. The plotted chart comes directly from the exported JSON report.

The denominator matters. Development acceptance is 100/500 and held-out acceptance is 24/120 because the pool intentionally contains four negatives for each reference. A 20% acceptance rate here is a fixture design choice, not a model-quality statistic.

Coverage is 100/100 development tasks and 24/24 held-out tasks with at least one accepted reference. Both sets use the same three task families; held-out item IDs and tool schemas differ. The reference planner explicitly supports both. These are descriptive toy-environment checks, not independent statistical trials, learned generalization, or a training-quality gain.

Methodology, exact corruption definitions and reproduction: {D}

Try a different corruption. Finding the next false accept would make this recipe more useful than treating perfect rejection on a designed pool as proof of correctness.""",
        "x": [
            "1/4 Same 620 tool-use trajectories: schema checks admit 496; error-free execution admits 372; independent goal/checkpoint checks admit 124. Chart calculated from actual exported fixture counts.",
            "2/4 Pool: 124 reference plans + 496 predefined corruptions. Wrong argument, missing step, unavailable tool, wrong destination/release. Every filter gets identical candidates and initial state. Zero injected corruptions pass the goal checks.",
            "3/4 Limits matter: one toy environment, templated tasks, no model API calls or training. The held-out schema is explicitly supported by the reference planner. These counts do not show learned generalization or model-quality gains.",
            f"4/4 Acceptance is 20% on each intentionally corrupted split; coverage is 100/100 development and 24/24 held-out tasks. Reproduce the method, then propose a missed corruption: {D}",
        ],
    },
    {
        "id": "05-release", "audience": "Open-source users, dataset teams and engineering reviewers",
        "hook": "ToolCrop v0.1.0 is released as an experimental Curator fork.",
        "evidence": [R, "evidence/published-release.json", "evidence/published-artifact-check.json", "evidence/validation-tests.txt", "evidence/review.md"],
        "cta": "Install the release, reproduce the report and open a focused issue with a task/candidate fixture.",
        "asset": "assets/real-report-screenshot.jpg", "asset_type": "Genuine screenshot of the release's executable demo",
        "alt_text": "Actual ToolCrop report shipped with the experimental v0.1.0 recipe. It separates schema validity, error-free execution and independently checked goal success for reference and corrupted tool-use trajectories. The report clearly labels the pool as offline fixtures with no model training experiment.",
        "linkedin": f"""ToolCrop v0.1.0 is released as an experimental Curator fork.

The scope is deliberately concrete: one contained inventory environment, independent goals and required checkpoints, a complete acceptance/rejection trail, dataset exports and coverage reports. Curator's original synthetic-data and bulk-inference functionality remains in the fork, with its history, Apache-2.0 license and attribution preserved.

The release includes a wheel, source package, fixture bundle and checksums. Clean installation preserves Curator imports and reproduces the demo output digests. 197 recipe/selected upstream checks pass. Independent correctness review found issues in the first implementation; the fixes and recheck are documented rather than hidden.

Quickstart on Python 3.11:
1. Clone {repo}
2. Check out v0.1.0 and install with 'python -m pip install .'
3. Run 'toolcrop demo --output reproduced'
4. Open reproduced/report.html and inspect accepted.jsonl alongside rejected.jsonl.

No model key is required for that demo. Live provider inference and full upstream GPU/provider suites are outside the measured release evidence. The fixtures do not establish a model-quality gain or a production-safety guarantee.

Next: expand negative cases and coverage, add reactive model rollout, then a second environment based on external usage.

Release and downloadable assets: {R}

If you build tool-use datasets, try one task and open a focused issue with the candidate sequence and the independently expected outcome. The screenshot is real software output.""",
        "x": [
            f"1/4 ToolCrop v0.1.0 is released: an experimental, attributed Curator fork for execution-validated tool-use datasets. Wheel, source, fixture data and checksums: {R}",
            "2/4 Quickstart: clone grishahq/toolcrop, check out v0.1.0, install with python -m pip install ., then run toolcrop demo --output reproduced. Open reproduced/report.html. No model key needed for the deterministic demo.",
            "3/4 197 recipe/selected upstream checks pass. Clean artifact install reproduces export digests; independent review findings and fixes are recorded. Full provider/GPU suites and live model inference are not measured here.",
            f"4/4 Curator's library/history/license stay intact. ToolCrop adds the contained inventory recipe, independent oracle, rejection trail and exports. Try a task and send a minimal false accept/reject: {repo} No model-quality gain is claimed.",
        ],
    },
]

checks = []
for item in items:
    assert len(item["linkedin"]) <= 3000
    assert len(item["alt_text"]) <= 1000
    assert (root / "campaign" / item["asset"]).is_file()
    weighted = []
    for post in item["x"]:
        assert post.isascii(), "Keep this check simple and reproducible with ASCII copy"
        count = len(re.sub(r"https?://\S+", "x" * 23, post))
        assert count <= 280, (item["id"], count, post)
        weighted.append(count)
    checks.append({"id": item["id"], "linkedin_characters": len(item["linkedin"]), "x_weighted_characters": weighted, "alt_text_characters": len(item["alt_text"])})
pack = {"project": "ToolCrop", "language": "English", "release": R, "prepared": True, "scheduled": False, "published": False,
        "timezone": "Asia/Dubai", "items": items}
(root / "campaign/campaign.json").write_text(json.dumps(pack, indent=2) + "\n")
(root / "campaign/character-checks.json").write_text(json.dumps({"method": "LinkedIn <=3000; ASCII X copy <=280 weighted characters, URLs count as 23; alt text <=1000", "checks": checks}, indent=2) + "\n")
lines = ["# ToolCrop English launch campaign", "", "Prepared copy is not scheduled or published. Read scheduling-status.json for actual platform state. Five beats; each X thread is one primary item. Portfolio cap: three primary items/week/platform across all five projects. Timezone: Asia/Dubai.", "", "Release verified before preparing release claims: " + R, ""]
for item in items:
    lines += ["## " + item["id"], "", "Audience: " + item["audience"], "", "Hook: " + item["hook"], "", "Evidence: " + "; ".join(item["evidence"]), "", "Call to action: " + item["cta"], "", "Image: " + item["asset"] + " (" + item["asset_type"] + ")", "", "Alt text: " + item["alt_text"], "", "### LinkedIn", "", item["linkedin"], "", "### X thread", ""]
    for post in item["x"]:
        lines += [post, ""]
(root / "campaign/CAMPAIGN.md").write_text("\n".join(lines))
print(json.dumps(checks, indent=2))
