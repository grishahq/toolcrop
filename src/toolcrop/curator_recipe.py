"""Optional Curator generation adapter; offline imports require no provider SDK.

Model outputs are proposals. The separate pipeline owns execution and the
trusted task registry owns the oracle. This plans whole trajectories; it does
not implement reactive multi-turn model rollout with tool feedback.
"""

import json

from .contracts import tool_schemas
from .pipeline import evaluate
from .tasks import load_tasks, public_task


def build_generator(model_name, **kwargs):
    """Build a real Curator structured-output generator when dependencies exist."""
    from pydantic import BaseModel, ConfigDict, Field

    from bespokelabs import curator

    class Call(BaseModel):
        model_config = ConfigDict(extra="forbid")
        name: str
        arguments: dict

    class Trajectory(BaseModel):
        model_config = ConfigDict(extra="forbid")
        calls: list[Call] = Field(min_length=1, max_length=32)

    class InventoryGenerator(curator.LLM):
        response_format = Trajectory

        def prompt(self, row):
            public = json.loads(row["task_json"])
            return (
                "Propose a sequence of tool calls that completes the request from initial state. "
                "Reserve before shipping. Use only the supplied tools. No code or external actions.\n"
                + json.dumps({"task": public, "tools": tool_schemas(public["schema"])})
            )

        def parse(self, row, response):
            return {"task_id": row["id"], "calls_json": json.dumps([call.model_dump() for call in response.calls])}

    return InventoryGenerator(model_name=model_name, **kwargs)


def generate_and_evaluate(model_name, split="development", limit=10, **kwargs):
    """Generate proposals with Curator then evaluate against original specs.

    The held-out split is opt-in and should not be used for prompt tuning.
    No model-generated success labels or expected states enter the validator.
    """
    from datasets import Dataset

    tasks = load_tasks(split)[:limit]
    if not tasks or limit < 1:
        raise ValueError("limit must select at least one task")
    generator = build_generator(model_name, **kwargs)
    # Never send goal fields to generation infrastructure or caches.
    generated = generator(Dataset.from_list([{"id": t["id"], "task_json": json.dumps(public_task(t))} for t in tasks]))
    registry = {task["id"]: task for task in tasks}
    records = []
    for index, row in enumerate(generated.dataset):
        task = registry[row["task_id"]]
        records.append(evaluate(task, json.loads(row["calls_json"]), f"curator:{index}", f"curator:{model_name}"))
    return records
