from datetime import datetime, timedelta, timezone
from services.governance.app.engine.retention_engine import RetentionEngine


def test_retention_and_legal_hold():
    engine = RetentionEngine()
    subject_id = "user-hold-999"
    created_old = datetime.now(timezone.utc) - timedelta(days=400)

    assert engine.can_delete(subject_id, retention_days=365, created_at=created_old) is True

    engine.add_legal_hold(subject_id)
    assert engine.is_under_legal_hold(subject_id) is True
    assert engine.can_delete(subject_id, retention_days=365, created_at=created_old) is False

    engine.release_legal_hold(subject_id)
    assert engine.can_delete(subject_id, retention_days=365, created_at=created_old) is True
