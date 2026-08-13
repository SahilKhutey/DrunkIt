def calculate_availability(successful: int, total: int) -> float:
    if total == 0:
        return 100.0
    return (successful / total) * 100.0


def calculate_error_budget(total_requests: int, target_percent: float) -> float:
    allowed_failure_rate = 1.0 - (target_percent / 100.0)
    return total_requests * allowed_failure_rate


class SLOEngine:

    def calculate_availability(self, successful: int, total: int) -> float:
        return calculate_availability(successful, total)

    def calculate_error_budget(self, total_requests: int, target_percent: float) -> float:
        return calculate_error_budget(total_requests, target_percent)
