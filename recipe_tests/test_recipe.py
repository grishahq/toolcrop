"""Contract and behavior tests for the execution-filtered recipe."""

import copy
import json

import pytest

from toolcrop.contracts import execute, validate_calls
from toolcrop.generator import CORRUPTIONS, corrupt, reference_calls
from toolcrop.pipeline import evaluate, export, import_records, reference_records, render_report, summarize
from toolcrop.tasks import load_tasks, public_task
from toolcrop.validators import check_final_state


@pytest.mark.parametrize("task", load_tasks(), ids=lambda t: t["id"])
def test_all_reference_tasks_and_corruptions(task):
    public = public_task(task)
    assert "goal" not in public
    calls = reference_calls(public)
    result = evaluate(task, calls, "reference", "reference")
    assert result["accepted"] and result["executable"]
    assert task["initial"] == result["initial"]  # executor must not mutate fixture
    for kind in CORRUPTIONS:
        result = evaluate(task, corrupt(calls, kind, task["schema"]), kind, kind)
        assert not result["accepted"], (task["id"], kind)
        assert result["reasons"]
    # A schema-valid, executable wrong reservation proves goals add information.
    wrong = evaluate(task, corrupt(calls, "wrong_argument", task["schema"]), "wrong", "wrong")
    assert wrong["schema_valid"] and wrong["executable"] and not wrong["accepted"]


@pytest.mark.parametrize(
    "calls",
    [
        None,
        {},
        [],
        [None],
        [{"name": [], "arguments": {}}],
        [{"name": "reserve", "arguments": {"sku": "a", "quantity": True}}],
        [{"name": "reserve", "arguments": {"sku": "a", "quantity": 0}}],
        [{"name": "reserve", "arguments": {"sku": "a", "quantity": -1}}],
        [{"name": "reserve", "arguments": {"sku": "a", "quantity": 1001}}],
        [{"name": "reserve", "arguments": {"sku": "a", "quantity": 1.0}}],
        [{"name": "reserve", "arguments": {"sku": "a", "quantity": 1, "path": "/tmp"}}],
        [{"name": "reserve", "arguments": "{}"}],
        [{"name": "__import__", "arguments": {}}] * 33,
    ],
)
def test_invalid_input_fails_closed(calls):
    task = load_tasks()[0]
    state, trace, errors = execute(task, calls)
    assert errors and not trace and state == task["initial"]


def test_unknown_item_insufficient_stock_and_early_stop():
    task = load_tasks()[0]
    for sku, count, reason in [("unknown", 1, "unknown_item"), ("DEV-000", 999, "insufficient_available")]:
        calls = [{"name": "reserve", "arguments": {"sku": sku, "quantity": count}}]
        state, trace, errors = execute(task, calls + reference_calls(public_task(task)))
        assert errors == [f"call_0:{reason}"] and not trace and state == task["initial"]


def test_schema_split_is_disjoint():
    development, heldout = load_tasks("development"), load_tasks("heldout")
    assert len(development) == 100 and len(heldout) == 24
    assert not ({t["id"] for t in development} & {t["id"] for t in heldout})
    assert not ({sku for t in development for sku in t["initial"]["available"]} & {sku for t in heldout for sku in t["initial"]["available"]})
    calls = reference_calls(public_task(heldout[0]))
    assert not validate_calls(calls, "heldout")
    assert validate_calls(calls, "development")


def test_independent_validator_detects_changes_and_conservation():
    task = load_tasks()[0]
    state = copy.deepcopy(task["goal"])
    assert check_final_state(task, state) == []
    state["available"]["DEV-SPARE-000"] -= 1
    assert "final_available_mismatch" in check_final_state(task, state)
    assert "conservation_failed:DEV-SPARE-000" in check_final_state(task, state)
    task["goal"]["available"]["DEV-SPARE-000"] -= 1
    assert check_final_state(task, state) == ["conservation_failed:DEV-SPARE-000"]


def test_import_cannot_override_oracle_or_split(tmp_path):
    path = tmp_path / "rows.jsonl"
    row = {"task_id": "development-000", "calls": reference_calls(public_task(load_tasks()[0]))}
    path.write_text(json.dumps(row) + "\n")
    assert import_records(path)[0]["accepted"]
    for invalid in [{**row, "goal": {}}, {**row, "task_id": "heldout-000"}, {**row, "task_id": []}]:
        path.write_text(json.dumps(invalid) + "\n")
        with pytest.raises(ValueError):
            import_records(path)


def test_exports_are_reproducible_and_chat_contains_real_results(tmp_path):
    records = reference_records()
    first, second = tmp_path / "one", tmp_path / "two"
    report = export(records, first)
    export(reference_records(), second)
    assert report["overall"]["candidates"] == 620
    assert report["overall"]["schema_valid"] == 496
    assert report["overall"]["executable"] == 372
    assert report["overall"]["accepted"] == 124
    assert report["by_split"]["development"]["task_coverage"]["rate"] == 1
    for file in first.iterdir():
        assert file.read_bytes() == (second / file.name).read_bytes()
    for split, count in [("development", 100), ("heldout", 24)]:
        rows = [json.loads(line) for line in (first / f"{split}.chat.jsonl").read_text().splitlines()]
        assert len(rows) == count
        assert all(row["split"] == split for row in rows)
        assert all(row["messages"][-1]["role"] == "tool" for row in rows)


def test_report_escapes_untrusted_values_and_counts_imports():
    task = load_tasks()[0]
    result = evaluate(task, reference_calls(public_task(task)), "<script>alert(1)</script>", "<bad>")
    report = render_report(summarize([result]), [result])
    assert "<script>" not in report and "&lt;script&gt;" in report
    assert "1 development tasks" in report and "1 evaluated trajectories" in report


def test_empty_import_report_is_honest(tmp_path):
    path = tmp_path / "empty.jsonl"
    path.write_text("")
    report = export(import_records(path), tmp_path / "output")
    assert report["overall"]["candidates"] == 0
    assert report["overall"]["acceptance_rate"] is None


@pytest.mark.parametrize("task", [t for t in load_tasks() if t["family"] == "hold_release"], ids=lambda t: t["id"])
def test_hold_release_requires_requested_intermediate_state(task):
    calls = reference_calls(public_task(task))
    quantity = "units" if task["schema"] == "heldout" else "quantity"
    item = "item" if task["schema"] == "heldout" else "sku"
    wrong_count = copy.deepcopy(calls)
    for call in wrong_count:
        call["arguments"][quantity] += 1
    wrong_item = copy.deepcopy(calls)
    spare = next(sku for sku in task["initial"]["available"] if "SPARE" in sku)
    for call in wrong_item:
        call["arguments"][item] = spare
    for candidate in (wrong_count, wrong_item):
        result = evaluate(task, candidate, "wrong", "wrong")
        assert result["executable"]
        assert result["final"] == task["goal"]
        assert result["reasons"] == ["required_state_not_reached"]


def test_methodology_matches_imported_and_reference_only_sources(tmp_path):
    reference_only = summarize(reference_records("development", negatives=False))
    assert set(reference_only["by_source"]) == {"reference_planner"}
    assert "any included" in reference_only["methodology"]
    path = tmp_path / "import.jsonl"
    path.write_text(json.dumps({"task_id": "development-000", "calls": []}) + "\n")
    imported = summarize(import_records(path))
    assert "Fixed reference planner" not in imported["methodology"]
    assert set(imported["by_source"]) == {"external_candidate"}
