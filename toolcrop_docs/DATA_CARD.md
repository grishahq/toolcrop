# Inventory-v1 dataset card and experiment

## Purpose and provenance

This is a deterministic development/validation fixture, not measured LLM training data. A versioned task registry contains 124 hand-designed, parameterized inventory scenarios. Expected states and required intermediate checkpoints were specified directly from intent, without running the trajectory planner. The planner sees only task ID, request, schema and initial state; goals/checkpoints stay in the evaluator. The independent validator imports no generator code. No human/private inventory, API response, testimonial or adoption data appears here.

The useful retained upstream baseline is Curator's synthetic-data/bulk-inference package. ToolCrop adds the controlled environment and recipe. Live Curator generation is optional and unmeasured in v0.1.

## Frozen splits

- Development: 100 tasks, 34 single shipments, 33 split shipments, 33 hold/release tasks. Item IDs start DEV. Tools: reserve(sku, quantity), ship(sku, quantity, destination), cancel(sku, quantity).
- Held-out: 24 tasks, 8 of each family. Item IDs start EVAL. Tools: hold_stock(item, units), dispatch_stock(item, units, address), release_stock(item, units).

Held-out tasks are not consumed by the default live generator/import command. Offline `demo` evaluates both and exports accepted chats separately. Both splits share grammar and intent families. The reference planner explicitly implements both schemas. This is limited schema-separation testing, not an unseen-task benchmark or evidence that a trained policy generalizes. Quantities and inventory patterns are repetitive; 124 rows do not mean 124 independent task designs.

## Environment and oracle

A reservation moves available to reserved inventory. Shipment consumes reserved inventory and records the destination allocation. Cancellation restores reserved to available. An operation cannot consume unavailable inventory. Each trajectory begins from a fresh private copy. The executor stops on the first failure; partial state is retained for audit, never reused by the next candidate.

A trajectory is accepted only when every call is well-formed and executes, exact final available/reserved/shipment dictionaries match the trusted goal, inventory is conserved, and every required checkpoint occurs in order. Hold/release tasks require the exact requested intermediate reserved state; merely returning to initial state is insufficient. The oracle does not prove minimality or judge every possible intermediate policy constraint. An alternative trajectory that satisfies the same declared checks can pass.

## Predeclared corruption experiment

For each task, evaluate one reference plus exactly four corruptions on the same initial state:

1. Wrong argument: increase the first reservation by one, leaving the rest unchanged. It executes but leaves an incorrect residual reservation.
2. Missing required step: remove the first reservation. The next operation fails with insufficient reserved stock.
3. Unavailable tool: rename the first operation to delete_database. Schema validation rejects it; no such tool exists or executes.
4. Wrong destination: substitute the final shipment destination with UNREQUESTED; for hold/release, replace the final release with a schema-valid shipment to UNREQUESTED. This executes but violates the goal.

The exact benchmark pool is 620 candidates: 124 references and 496 corruptions. We compare strict schema-only admission, error-free execution admission, and execution with independent final/checkpoint predicates. The baseline is defined here, not an assertion that Curator itself claims schema-only quality assurance. Every method receives the same candidate pool; no retries, filtering or different generation budgets are used. Tests additionally probe matched wrong quantities and wrong items for hold/release; those regression checks are not silently added to the fixed benchmark denominator.

## Results and formulas

| Split | Candidates | Schema valid | Executes | Accepted | Accepted unique tasks |
| --- | ---: | ---: | ---: | ---: | ---: |
| Development | 500 | 400 | 300 | 100 | 100/100 |
| Held-out | 120 | 96 | 72 | 24 | 24/24 |
| Total | 620 | 496 | 372 | 124 | 124/124 |

Acceptance = accepted / candidate count. Executable success = trajectories with no schema or execution errors / candidate count. Task coverage = unique tasks with at least one accepted candidate / number of specified tasks in that split. Family coverage counts unique accepted tasks per family; it does not measure all possible states or tools. All four negative classes have 0/124 accepted. Schema-only admission includes 372 corrupted trajectories; execution-only admission includes 248 corrupted trajectories. Goal/checkpoint validation admits zero of these predefined corruptions.

There is no before/after model-quality result, training experiment, real-model acceptance rate, measured human time saving, uncertainty interval or production generalization claim. The pool was intentionally constructed to expose these faults. Perfect rejection on this pool does not prove a generally correct validator.

## Files, license and use

The Apache-2.0 project license applies to new recipe code and fixture data. Accepted records contain full execution history; chat exports also store initial-state metadata and schemas. Preserve state context when converting to a training format. Inspect quality, diversity and held-out contamination before any training. The held-out export is for evaluation only. Source provenance remains reference_planner; never relabel these rows as model generations.

Reproduce with `toolcrop demo --output reproduced` and compare checksums against `evidence/inventory-v1/checksums.json`. CLI output, JSON report and Matplotlib plot all derive from the same evaluated records. Conceptual campaign artwork is clearly labeled separately.
