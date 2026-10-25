# Reproducing scenario authoring

`python scripts/build_task_specs.py --output regenerated-specs.json` reconstructs the frozen 100 development / 24 held-out registry. Compare its bytes with `src/toolcrop/specs/inventory-v1.json`. The source authoring procedure is a supplementary release asset and is also kept on the repository's main branch with the campaign and post-release verification records. The v0.1.0 tag contains the frozen task registry itself.

This source defines three small task-intent templates and parameterizes quantities, item IDs and destinations. It calculates expected state directly from intent and adds the hold/release checkpoint. It does not execute a candidate or import the planner, executor or validator. This structural independence helps make the oracle inspectable; it does not establish correctness by itself. The separate tests hand-check conservation and adversarial sequences.

New task families require human-authored semantics, independent review of success predicates and a new versioned task-registry identifier. Generate them to a new file; do not silently change the published inventory-v1 oracle, relabel evaluation fixtures as training data, or let model candidates supply expected outcomes. The initial held-out schema is explicitly supported by the offline planner and shares task grammar; no unseen-family or learned-generalization claim follows.
