"""Independent state predicates: no imports from the trajectory generator.

Task goals are frozen declarative specifications. Candidate-supplied goals and
candidate-supplied tool outputs are never used as an oracle.
"""


def check_final_state(task, state, trace=()):
    """Check exact requested allocations, residual state and conservation."""
    reasons = []
    goal, initial = task["goal"], task["initial"]
    for field in ("available", "reserved", "shipments"):
        if state.get(field) != goal[field]:
            reasons.append(f"final_{field}_mismatch")
    cursor = 0
    for expected in task.get("required_states", []):
        for index in range(cursor, len(trace)):
            if trace[index]["result"]["state"] == expected:
                cursor = index + 1
                break
        else:
            reasons.append("required_state_not_reached")
            break
    for sku in initial["available"]:
        before = initial["available"][sku] + initial["reserved"][sku]
        after = state["available"][sku] + state["reserved"][sku]
        after += sum(items.get(sku, 0) for items in state["shipments"].values())
        before += sum(items.get(sku, 0) for items in initial["shipments"].values())
        if before != after:
            reasons.append(f"conservation_failed:{sku}")
        if state["available"][sku] < 0 or state["reserved"][sku] < 0:
            reasons.append(f"negative_inventory:{sku}")
    return reasons
