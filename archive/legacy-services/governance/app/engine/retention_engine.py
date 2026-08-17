from datetime import datetime, timedelta, timezone


class RetentionEngine:

    def __init__(self):
        self.legal_holds: set[str] = set()

    def add_legal_hold(self, subject_id: str):
        self.legal_holds.add(subject_id)

    def release_legal_hold(self, subject_id: str):
        self.legal_holds.discard(subject_id)

    def is_under_legal_hold(self, subject_id: str) -> bool:
        return subject_id in self.legal_holds

    def can_delete(self, subject_id: str, retention_days: int = 365, created_at: datetime | None = None) -> bool:
        if self.is_under_legal_hold(subject_id):
            return False

        if not created_at:
            return False

        now = datetime.now(timezone.utc)
        expiry = created_at + timedelta(days=retention_days)
        return now >= expiry
