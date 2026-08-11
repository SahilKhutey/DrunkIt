import time
from typing import List, Dict, Tuple

# Sliding window in-memory history of recent sensitive actions: (user_id, resource_id, action, timestamp)
SOD_ACTION_HISTORY: List[Tuple[str, str, str, float]] = []

SOD_WINDOW_SECONDS = 900.0  # 15 minutes

def record_user_action(user_id: str, resource_id: str, action: str):
    now = time.time()
    SOD_ACTION_HISTORY.append((user_id, resource_id, action, now))
    _cleanup_old_actions(now)

def check_sod_violation(user_id: str, resource_id: str, new_action: str) -> Tuple[bool, str]:
    now = time.time()
    _cleanup_old_actions(now)

    # Sensitive action pairs that cannot be performed by the same user on the same resource within 15 mins
    conflict_pairs = [
        ("CREATE", "APPROVE"),
        ("INITIATE", "APPROVE"),
        ("APPROVE_LICENSE", "ACTIVATE_RETAILER"),
        ("APPROVE", "EXECUTE"),
        ("REQUEST_REFUND", "APPROVE_REFUND")
    ]

    for (uid, rid, past_action, ts) in SOD_ACTION_HISTORY:
        if uid == user_id and rid == resource_id:
            for act_a, act_b in conflict_pairs:
                if (past_action == act_a and new_action == act_b) or (past_action == act_b and new_action == act_a):
                    return True, f"SoD Violation: User {user_id} performed '{past_action}' on resource {resource_id} within 15 minutes and cannot perform '{new_action}'"

    return False, ""

def _cleanup_old_actions(now: float):
    global SOD_ACTION_HISTORY
    cutoff = now - SOD_WINDOW_SECONDS
    SOD_ACTION_HISTORY = [item for item in SOD_ACTION_HISTORY if item[3] >= cutoff]
