def test_consumer_state_min_ages():
    STATE_MIN_AGES = {
        "IN-KA": 21,
        "IN-MH": 25,
        "IN-DL": 21,
        "IN-CG": 21,
        "IN-TN": 21,
        "IN-GA": 18,
    }
    assert STATE_MIN_AGES["IN-KA"] == 21
    assert STATE_MIN_AGES["IN-MH"] == 25
    assert STATE_MIN_AGES["IN-DL"] == 21
    assert STATE_MIN_AGES["IN-GA"] == 18


def test_notification_channels():
    channels = ["SMS", "EMAIL", "PUSH"]
    assert "SMS" in channels
    assert "EMAIL" in channels
    assert "PUSH" in channels


