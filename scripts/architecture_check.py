"""Architecture Drift & Contract Consistency Audit Script."""

import os
import sys
import yaml


def check_contracts(root_dir: str) -> bool:
    print("Checking Platform Contracts & Architecture Drift...")
    contracts_dir = os.path.join(root_dir, "contracts")
    if not os.path.exists(contracts_dir):
        print("ERROR: contracts/ directory missing")
        return False

    reg_path = os.path.join(contracts_dir, "events", "registry.yaml")
    if not os.path.exists(reg_path):
        print("ERROR: contracts/events/registry.yaml missing")
        return False

    db_path = os.path.join(contracts_dir, "database-ownership.yaml")
    if not os.path.exists(db_path):
        print("ERROR: contracts/database-ownership.yaml missing")
        return False

    with open(db_path, "r", encoding="utf-8") as f:
        db_manifest = yaml.safe_load(f)

    print(f"Loaded Database Ownership Manifest: {len(db_manifest.get('services', {}))} services registered.")

    with open(reg_path, "r", encoding="utf-8") as f:
        reg_manifest = yaml.safe_load(f)

    events = reg_manifest.get("events", [])
    print(f"Loaded Event Registry: {len(events)} canonical events registered.")

    all_passed = True
    for ev in events:
        schema_rel = ev.get("schema")
        schema_path = os.path.join(contracts_dir, "events", schema_rel)
        if not os.path.exists(schema_path):
            print(f"ERROR: Schema file missing for event {ev.get('type')}: {schema_path}")
            all_passed = False

    if all_passed:
        print("SUCCESS: All architecture drift & contract validation checks passed cleanly!")
    return all_passed


if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    success = check_contracts(root)
    sys.exit(0 if success else 1)
