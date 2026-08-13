from services.security.app.engine.abuse_engine import AccountTakeoverDetector


def test_account_takeover_scoring():
    detector = AccountTakeoverDetector()
    signals = [
        {"signal_type": "NEW_DEVICE"},
        {"signal_type": "PASSWORD_RESET"},
        {"signal_type": "MULTIPLE_FAILED_LOGIN"},
    ]

    score = detector.calculate(signals)
    assert score == 60.0
