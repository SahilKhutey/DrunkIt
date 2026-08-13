from services.observability.app.engine.slo_engine import calculate_availability, calculate_error_budget


def test_slo_calculations():
    avail = calculate_availability(999500, 1000000)
    assert avail == 99.95

    eb = calculate_error_budget(1000000, 99.95)
    assert round(eb) == 500
