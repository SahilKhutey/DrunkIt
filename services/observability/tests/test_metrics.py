from services.observability.app.middleware.request_metrics import RequestMetrics


def test_request_metrics_recording():
    m = RequestMetrics()
    m.record(0.100, error=False)
    m.record(0.200, error=True)

    assert m.requests == 2
    assert m.errors == 1
    assert round(m.average_latency, 2) == 0.15
    assert m.error_rate == 0.5
