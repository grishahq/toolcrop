"""Command-line interface for the offline recipe and external candidates."""

import argparse
import json

from .pipeline import export, import_records, reference_records


def main():
    """Run the reproducible fixture experiment or validate external JSONL."""
    parser = argparse.ArgumentParser(description="Execute tool-use trajectories against independent inventory goals.")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("demo", "validate"):
        action = sub.add_parser(command)
        action.add_argument("--output", default="toolcrop-output")
        action.add_argument("--split", choices=("all", "development", "heldout"), default="all" if command == "demo" else "development")
        if command == "validate":
            action.add_argument("input", help="JSONL rows containing exactly task_id and calls")
        else:
            action.add_argument("--no-negatives", action="store_true")
    args = parser.parse_args()
    try:
        records = reference_records(args.split, not args.no_negatives) if args.command == "demo" else import_records(args.input, args.split)
        report = export(records, args.output)
    except (ValueError, OSError, TypeError, KeyError) as error:
        parser.exit(2, f"toolcrop: {error}\n")
    print(json.dumps({"output": args.output, "overall": report["overall"], "by_split": report["by_split"]}, indent=2))
    return 0
