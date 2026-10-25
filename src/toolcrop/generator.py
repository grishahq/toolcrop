"""Deterministic reference planner and predefined candidate corruptions.

This planner sees public requests and starting state, never validator goals.
It is an honest offline fixture generator, not an LLM experiment.
"""

import copy
import re

CORRUPTIONS = ("wrong_argument", "missing_required_step", "unavailable_tool", "wrong_destination")


def reference_calls(public):
    """Parse the constrained request grammar into multi-step reference calls."""
    heldout = public["schema"] == "heldout"
    names = ("hold_stock", "dispatch_stock", "release_stock") if heldout else ("reserve", "ship", "cancel")
    calls = []

    def add(op, sku, count, destination=None):
        args = {"item" if heldout else "sku": sku, "units" if heldout else "quantity": int(count)}
        if destination:
            args["address" if heldout else "destination"] = destination
        calls.append({"name": names[op], "arguments": args})

    for clause in public["request"].split("; "):
        match = re.fullmatch(r"(Ship|Hold then release) (\d+) units of ([\w-]+)(?: to ([\w-]+))?", clause)
        if not match:
            raise ValueError("Reference planner only supports the documented fixture grammar")
        action, count, sku, destination = match.groups()
        add(0, sku, count)
        add(1 if action == "Ship" else 2, sku, count, destination)
    return calls


def corrupt(calls, kind, schema):
    """Apply a predeclared, deterministic one-change fault to a reference."""
    result = copy.deepcopy(calls)
    if kind == "wrong_argument":
        result[0]["arguments"]["units" if schema == "heldout" else "quantity"] += 1
    elif kind == "missing_required_step":
        result.pop(0)
    elif kind == "unavailable_tool":
        result[0]["name"] = "delete_database"
    elif kind == "wrong_destination":
        # For hold/release tasks, changing the final operation to shipping is
        # schema-valid yet violates the independently specified release goal.
        args = result[-1]["arguments"]
        result[-1]["name"] = "dispatch_stock" if schema == "heldout" else "ship"
        args["address" if schema == "heldout" else "destination"] = "UNREQUESTED"
    else:
        raise ValueError(f"unknown corruption: {kind}")
    return result
