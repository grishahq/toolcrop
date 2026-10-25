"""Load and verify fixed trusted task specifications."""

import copy
import json
from importlib.resources import files

from .contracts import SCHEMAS


def load_tasks(split="all"):
    """Return frozen specifications, independent of the candidate source."""
    if split not in ("all", "development", "heldout"):
        raise ValueError("split must be all, development or heldout")
    tasks = json.loads(files("toolcrop.specs").joinpath("inventory-v1.json").read_text())
    ids = set()
    for task in tasks:
        if task["id"] in ids or task["schema"] not in SCHEMAS:
            raise ValueError("invalid or duplicate trusted task")
        ids.add(task["id"])
    return copy.deepcopy([t for t in tasks if split == "all" or t["split"] == split])


def public_task(task):
    """Exclude goal state from generation prompts."""
    return {key: copy.deepcopy(task[key]) for key in ("id", "schema", "initial", "request")}
