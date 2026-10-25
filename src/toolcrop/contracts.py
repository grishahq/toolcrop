"""Strict, bounded inventory tool contracts. No candidate code is executed."""

import copy

MAX_CALLS = 32
MAX_UNITS = 1000
SCHEMAS = {
    "development": {
        "reserve": {"sku": "str", "quantity": "int"},
        "ship": {"sku": "str", "quantity": "int", "destination": "str"},
        "cancel": {"sku": "str", "quantity": "int"},
    },
    "heldout": {
        "hold_stock": {"item": "str", "units": "int"},
        "dispatch_stock": {"item": "str", "units": "int", "address": "str"},
        "release_stock": {"item": "str", "units": "int"},
    },
}
OPERATIONS = {
    "reserve": "reserve",
    "ship": "ship",
    "cancel": "cancel",
    "hold_stock": "reserve",
    "dispatch_stock": "ship",
    "release_stock": "cancel",
}


def tool_schemas(schema):
    """Return provider-style JSON schemas for the selected environment version."""
    return [
        {
            "type": "function",
            "function": {
                "name": name,
                "description": {
                    "reserve": "Move available stock to reserved stock before shipping.",
                    "ship": "Ship reserved stock to a destination.",
                    "cancel": "Release reserved stock back to available stock.",
                }[OPERATIONS[name]],
                "parameters": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": list(fields),
                    "properties": {
                        key: ({"type": "integer", "minimum": 1, "maximum": MAX_UNITS} if kind == "int" else {"type": "string", "minLength": 1, "maxLength": 80})
                        for key, kind in fields.items()
                    },
                },
            },
        }
        for name, fields in SCHEMAS[schema].items()
    ]


def validate_calls(calls, schema):
    """Reject malformed, unknown or unbounded calls before execution."""
    if type(calls) is not list or not 1 <= len(calls) <= MAX_CALLS:
        return ["calls_must_be_nonempty_bounded_list"]
    errors = []
    for i, call in enumerate(calls):
        if type(call) is not dict or set(call) != {"name", "arguments"}:
            errors.append(f"call_{i}:invalid_call_shape")
            continue
        name, args = call["name"], call["arguments"]
        if type(name) is not str or name not in SCHEMAS[schema]:
            errors.append(f"call_{i}:unavailable_tool")
            continue
        fields = SCHEMAS[schema][name]
        if type(args) is not dict or set(args) != set(fields):
            errors.append(f"call_{i}:wrong_argument_keys")
            continue
        for key, kind in fields.items():
            value = args[key]
            if kind == "int" and (type(value) is not int or not 1 <= value <= MAX_UNITS):
                errors.append(f"call_{i}:{key}:invalid_integer")
            if kind == "str" and (type(value) is not str or not 1 <= len(value) <= 80):
                errors.append(f"call_{i}:{key}:invalid_string")
    return errors


def execute(task, calls):
    """Dispatch a finite allowlist against a private copy of in-memory state."""
    state = copy.deepcopy(task["initial"])
    errors = validate_calls(calls, task["schema"])
    trace = []
    if errors:
        return state, trace, errors
    for i, call in enumerate(calls):
        args = call["arguments"]
        sku = args.get("sku", args.get("item"))
        quantity = args.get("quantity", args.get("units"))
        destination = args.get("destination", args.get("address"))
        op = OPERATIONS[call["name"]]
        if sku not in state["available"]:
            errors.append(f"call_{i}:unknown_item")
            break
        source = "available" if op == "reserve" else "reserved"
        if state[source][sku] < quantity:
            errors.append(f"call_{i}:insufficient_{source}")
            break
        state[source][sku] -= quantity
        if op == "ship":
            shipment = state["shipments"].setdefault(destination, {})
            shipment[sku] = shipment.get(sku, 0) + quantity
        else:
            target = "reserved" if op == "reserve" else "available"
            state[target][sku] += quantity
        trace.append({"call": copy.deepcopy(call), "result": {"ok": True, "state": copy.deepcopy(state)}})
    return state, trace, errors
