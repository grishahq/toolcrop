"""Author the trusted scenario registry without executing a candidate plan.

This module defines task intent, initial state, final oracle and required
checkpoints. It does not import the trajectory generator or executor.
"""

import argparse
import copy
import json
from pathlib import Path


def build_specs(development=100, heldout=24):
    """Parameterize three scenario families into two disjoint schema splits."""
    tasks = []
    for split, count in [("development", development), ("heldout", heldout)]:
        for i in range(count):
            prefix = "DEV" if split == "development" else "EVAL"
            sku, spare = f"{prefix}-{i:03d}", f"{prefix}-SPARE-{i:03d}"
            n, destination = 1 + i % 7, f"{prefix}-DOCK-{i % 5}"
            stock = n * 3 + 4
            family = ["single_ship", "split_ship", "hold_release"][i % 3]
            initial = {"available": {sku: stock, spare: 9}, "reserved": {sku: 0, spare: 0}, "shipments": {}}
            goal = copy.deepcopy(initial)
            required_states = []
            if family == "single_ship":
                request = f"Ship {n} units of {sku} to {destination}"
                goal["available"][sku] -= n
                goal["shipments"] = {destination: {sku: n}}
            elif family == "split_ship":
                second = f"{prefix}-BACKUP-{i % 4}"
                request = f"Ship {n} units of {sku} to {destination}; Ship 1 units of {sku} to {second}"
                goal["available"][sku] -= n + 1
                goal["shipments"] = {destination: {sku: n}, second: {sku: 1}}
            else:
                request = f"Hold then release {n} units of {sku}"
                checkpoint = copy.deepcopy(initial)
                checkpoint["available"][sku] -= n
                checkpoint["reserved"][sku] += n
                required_states.append(checkpoint)
            tasks.append(
                {
                    "id": f"{split}-{i:03d}",
                    "split": split,
                    "schema": split,
                    "family": family,
                    "request": request,
                    "initial": initial,
                    "goal": goal,
                    "required_states": required_states,
                }
            )
    return tasks


def main():
    """Generate specifications in a new file, leaving the installed oracle alone."""
    parser = argparse.ArgumentParser(description="Reproduce the trusted inventory scenario specifications.")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    path = Path(args.output)
    if path.exists():
        parser.error("output already exists; choose a new path to preserve the trusted oracle")
    path.write_text(json.dumps(build_specs(), indent=2) + "\n", encoding="utf-8")
    print(f"Wrote 100 development and 24 held-out trusted specifications to {path}")


if __name__ == "__main__":
    main()
