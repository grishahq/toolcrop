"""Exercise the real Curator adapter contract with deterministic generation IO."""

import json
from types import SimpleNamespace

from bespokelabs import curator
from bespokelabs.curator.request_processor.online.openai_online_request_processor import OpenAIOnlineRequestProcessor
from toolcrop.curator_recipe import build_generator, generate_and_evaluate
from toolcrop.generator import reference_calls
from toolcrop.tasks import load_tasks, public_task


def test_real_curator_generator_prompt_parse_and_oracle_separation(monkeypatch):
    # Keep actual Curator class construction and structured response machinery;
    # replace only inference. This tests the integration without an API call.
    captured = []
    # Curator probes provider rate limits during construction. Stub that IO too.
    monkeypatch.setattr(OpenAIOnlineRequestProcessor, "get_header_based_rate_limits", lambda self: (100, 10000))

    def fake_inference(self, dataset, *args, **kwargs):
        rows = []
        for row in dataset:
            assert set(row) == {"id", "task_json"}
            public = json.loads(row["task_json"])
            captured.append(self.prompt(row))
            response = self.response_format.model_validate({"calls": reference_calls(public)})
            rows.append(self.parse(row, response))
        return SimpleNamespace(dataset=rows)

    monkeypatch.setattr(curator.LLM, "__call__", fake_inference)
    generator = build_generator("gpt-4o-mini")
    task = load_tasks()[0]
    prompt = generator.prompt({"id": task["id"], "task_json": json.dumps(public_task(task))})
    assert '"goal"' not in prompt
    assert '"reserve"' in prompt
    records = generate_and_evaluate("gpt-4o-mini", limit=3)
    assert len(records) == 3 and all(record["accepted"] for record in records)
    assert all('"goal"' not in prompt for prompt in captured)
    for prompt, original in zip(captured, load_tasks()[:3], strict=True):
        payload = json.loads(prompt.split("\n", 1)[1])
        assert payload["task"]["initial"] == original["initial"]
    response = generator.response_format.model_validate({"calls": reference_calls(public_task(task))})
    assert json.loads(generator.parse({"id": task["id"]}, response)["calls_json"]) == reference_calls(public_task(task))
