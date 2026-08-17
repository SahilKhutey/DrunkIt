import hashlib
import json


def canonical_json(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def calculate_event_hash(previous_hash: str, event_data: dict) -> str:
    payload = previous_hash + canonical_json(event_data)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def verify_event_chain(previous_hash: str, event_data: dict, expected_hash: str) -> bool:
    actual = calculate_event_hash(previous_hash, event_data)
    return actual == expected_hash
