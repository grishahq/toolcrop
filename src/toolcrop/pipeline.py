"""Evaluate candidates against trusted specs and export auditable records."""

import hashlib
import html
import json
from collections import Counter
from pathlib import Path

from .contracts import execute, tool_schemas, validate_calls
from .generator import CORRUPTIONS, corrupt, reference_calls
from .tasks import load_tasks, public_task
from .validators import check_final_state


def evaluate(task, calls, candidate_id, source):
    """Evaluate real execution; retain reasons and never trust supplied outputs."""
    schema_errors = validate_calls(calls, task["schema"])
    state, trace, execution_errors = execute(task, calls)
    final_errors = check_final_state(task, state, trace)
    reasons = list(dict.fromkeys(execution_errors + final_errors))
    return {
        "candidate_id": candidate_id,
        "task_id": task["id"],
        "split": task["split"],
        "family": task["family"],
        "schema": task["schema"],
        "source": source,
        "request": task["request"],
        "initial": task["initial"],
        "calls": calls,
        "schema_valid": not schema_errors,
        "executable": not execution_errors,
        "accepted": not reasons,
        "reasons": reasons,
        "trace": trace,
        "final": state,
    }


def reference_records(split="all", negatives=True):
    """Evaluate a fixed reference/corruption pool without model credentials."""
    records = []
    for task in load_tasks(split):
        calls = reference_calls(public_task(task))
        records.append(evaluate(task, calls, task["id"] + ":reference", "reference_planner"))
        if negatives:
            for kind in CORRUPTIONS:
                records.append(evaluate(task, corrupt(calls, kind, task["schema"]), task["id"] + ":" + kind, kind))
    return records


def import_records(path, split="development"):
    """Load bounded JSONL candidates. Only task_id and calls are accepted.

    The task registry supplies the request, schemas and oracle, preventing an
    imported candidate from changing its own expected outcome.
    """
    tasks = {t["id"]: t for t in load_tasks(split)}
    if Path(path).stat().st_size > 10_000_000:
        raise ValueError("candidate file exceeds 10 MB limit")
    records = []
    with open(path, encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if number > 10_000:
                raise ValueError("candidate file exceeds 10000 rows")
            candidate = json.loads(line)
            if type(candidate) is not dict or set(candidate) != {"task_id", "calls"}:
                raise ValueError(f"line {number}: expected exactly task_id and calls")
            task_id = candidate["task_id"]
            if type(task_id) is not str or task_id not in tasks:
                raise ValueError(f"line {number}: unknown task in selected split")
            records.append(evaluate(tasks[task_id], candidate["calls"], f"import:{number}", "external_candidate"))
    return records


def summarize(records):
    """Report acceptance separately from schema validity and executability."""

    def group(rows):
        n = len(rows)
        return {
            "candidates": n,
            "schema_valid": sum(r["schema_valid"] for r in rows),
            "executable": sum(r["executable"] for r in rows),
            "accepted": sum(r["accepted"] for r in rows),
            "acceptance_rate": sum(r["accepted"] for r in rows) / n if n else None,
            "executable_success_rate": sum(r["executable"] for r in rows) / n if n else None,
            "rejection_reasons": dict(sorted(Counter(reason for r in rows for reason in r["reasons"]).items())),
        }

    split_reports = {}
    for split in sorted({r["split"] for r in records}):
        rows = [r for r in records if r["split"] == split]
        expected = load_tasks(split)
        accepted_ids = {r["task_id"] for r in rows if r["accepted"]}
        split_reports[split] = {
            **group(rows),
            "task_coverage": {"accepted_unique_tasks": len(accepted_ids), "specified_tasks": len(expected), "rate": len(accepted_ids) / len(expected)},
            "family_coverage": {
                family: len({r["task_id"] for r in rows if r["accepted"] and r["family"] == family}) for family in sorted({t["family"] for t in expected})
            },
        }
    return {
        "format_version": 1,
        "recipe": "inventory-v1",
        "maturity": "experimental",
        "methodology": (
            "Fixed reference planner and any included predefined corruptions; see source counts. No model generation or training experiment."
            if records and all(r["source"] in {"reference_planner", *CORRUPTIONS} for r in records)
            else "Candidates from the sources listed in by_source are executed against fixed trusted tasks. No training experiment is measured."
        ),
        "limits": [
            "124 templated tasks in one toy environment; counts are descriptive, not independent statistical trials.",
            "Held-out tasks have disjoint item identifiers and tool schemas but share task grammar and families.",
            "Offline planner supports both schemas explicitly. This is not evidence of model generalization or quality gain.",
            "Accepted means exact declared final state and required checkpoints were reached without error; policy optimality is not judged.",
        ],
        "overall": group(records),
        "by_split": split_reports,
        "by_source": {source: group([r for r in records if r["source"] == source]) for source in sorted({r["source"] for r in records})},
    }


def chat_record(record):
    """Export actual tool results in a provider-neutral chat representation."""
    messages = [{"role": "user", "content": record["request"]}]
    for i, step in enumerate(record["trace"]):
        call_id = f"call_{i}"
        messages.append(
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": call_id,
                        "type": "function",
                        "function": {"name": step["call"]["name"], "arguments": json.dumps(step["call"]["arguments"], sort_keys=True)},
                    }
                ],
            }
        )
        messages.append({"role": "tool", "tool_call_id": call_id, "content": json.dumps(step["result"], sort_keys=True)})
    return {
        "task_id": record["task_id"],
        "split": record["split"],
        "source": record["source"],
        "initial_state": record["initial"],
        "tools": tool_schemas(record["schema"]),
        "messages": messages,
    }


def render_report(report, records):
    """Render a standalone HTML report from measured records, escaping input."""

    def esc(value):
        return html.escape(str(value))

    rows = "".join(
        f"<tr><td>{esc(source)}</td><td>{r['candidates']}</td><td>{r['schema_valid']}</td><td>{r['executable']}</td><td>{r['accepted']}</td></tr>"
        for source, r in report["by_source"].items()
    )
    examples = []
    for source in report["by_source"]:
        r = next(r for r in records if r["source"] == source)
        examples.append(
            f"<details><summary>{esc(r['candidate_id'])}: {'ACCEPT' if r['accepted'] else 'REJECT'}</summary>"
            f"<pre>{esc(json.dumps(r, indent=2))}</pre></details>"
        )
    development_count = len({r["task_id"] for r in records if r["split"] == "development"})
    heldout_count = len({r["task_id"] for r in records if r["split"] == "heldout"})
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>ToolCrop | Inventory execution report</title><style>
body{{font:18px system-ui;background:#0c1720;color:#e7eef3;max-width:1100px;margin:48px auto;padding:0 28px}}
h1{{font-size:46px;letter-spacing:-1px}}h2{{color:#7ce3ba}}p{{line-height:1.6}}table{{width:100%;border-collapse:collapse}}
th,td{{padding:14px;text-align:left;border-bottom:1px solid #34434d}}th{{color:#7ce3ba}}pre{{white-space:pre-wrap;font:13px monospace}}
small{{color:#bccad4}}details{{margin:16px 0;padding:14px;background:#142630}}.pill{{color:#7ce3ba;font-weight:700}}
</style><body><span class="pill">TOOLCROP · EXPERIMENTAL v0.1.0</span><h1>Plausible calls. Executable evidence.</h1>
<p>Inventory recipe · {development_count} development tasks · {heldout_count} held-out tasks · {len(records)} evaluated trajectories.</p>
<p>Schema-only admission keeps <strong>{report["overall"]["schema_valid"]}</strong> candidates. Execution plus independent final-state checks keeps
<strong>{report["overall"]["accepted"]}</strong>. {esc(report["methodology"])}</p>
<h2>Same candidate pool, different checks</h2><table><thead><tr><th>Candidate source</th><th>Total</th>
<th>Schema valid</th><th>Executable</th><th>Goal met</th></tr></thead>
<tbody>{rows}</tbody></table><h2>Coverage and limits</h2><pre>{esc(json.dumps(report["by_split"], indent=2))}</pre>
<p>{esc(" ".join(report["limits"]))}</p><h2>Inspect actual records</h2>{"".join(examples)}
<small>Built on Bespoke Labs Curator. No network, filesystem or shell tools are exposed to candidates.</small></body></html>"""


def export(records, output):
    """Write deterministic JSONL, accepted chat data, reports and checksums."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    report = summarize(records)

    def write_jsonl(name, rows):
        (output / name).write_text("".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")

    write_jsonl("candidates.jsonl", records)
    write_jsonl("accepted.jsonl", [r for r in records if r["accepted"]])
    write_jsonl("rejected.jsonl", [r for r in records if not r["accepted"]])
    for split in ("development", "heldout"):
        write_jsonl(f"{split}.chat.jsonl", [chat_record(r) for r in records if r["accepted"] and r["split"] == split])
    (output / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "report.html").write_text(render_report(report, records), encoding="utf-8")
    names = ["candidates.jsonl", "accepted.jsonl", "rejected.jsonl", "development.chat.jsonl", "heldout.chat.jsonl", "report.json", "report.html"]
    checksums = {name: hashlib.sha256((output / name).read_bytes()).hexdigest() for name in names}
    (output / "checksums.json").write_text(json.dumps(checksums, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
