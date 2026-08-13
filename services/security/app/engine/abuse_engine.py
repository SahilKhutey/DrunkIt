class AccountTakeoverDetector:

    def calculate(self, signals: list) -> float:
        signal_types = {getattr(s, "signal_type", s.get("signal_type")) for s in signals}

        score = 0.0
        if "NEW_DEVICE" in signal_types:
            score += 15.0
        if "PASSWORD_RESET" in signal_types:
            score += 20.0
        if "MULTIPLE_FAILED_LOGIN" in signal_types:
            score += 25.0
        if "NEW_PAYMENT_METHOD" in signal_types:
            score += 25.0
        if "UNUSUAL_ORDER_PATTERN" in signal_types:
            score += 20.0

        return min(score, 100.0)
