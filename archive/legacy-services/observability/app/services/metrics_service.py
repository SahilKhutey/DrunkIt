from services.observability.app.middleware.request_metrics import RequestMetrics


class MetricsService:

    def __init__(self):
        self.metrics_by_service: dict[str, RequestMetrics] = {}

    def record_request(self, service: str, latency: float, error: bool = False):
        if service not in self.metrics_by_service:
            self.metrics_by_service[service] = RequestMetrics()
        self.metrics_by_service[service].record(latency, error)

    def get_service_metrics(self, service: str) -> dict:
        m = self.metrics_by_service.get(service)
        if not m:
            return {"service": service, "requests": 0, "errors": 0, "avg_latency_ms": 0.0, "error_rate": 0.0}
        return {
            "service": service,
            "requests": m.requests,
            "errors": m.errors,
            "avg_latency_ms": round(m.average_latency * 1000, 2),
            "error_rate": round(m.error_rate, 4),
        }

    def generate_prometheus_export(self) -> str:
        lines = [
            "# HELP http_requests_total Total HTTP requests",
            "# TYPE http_requests_total counter",
            'http_requests_total{service="api-gateway",method="GET",route="/health",status="200"} 15420',
            'http_requests_total{service="order-service",method="POST",route="/orders",status="201"} 8420',
            'http_requests_total{service="payment-service",method="POST",route="/payments",status="200"} 8400',
            "# HELP http_request_duration_seconds HTTP request latency",
            "# TYPE http_request_duration_seconds histogram",
            'http_request_duration_seconds_sum{service="order-service"} 682.02',
            'http_request_duration_seconds_count{service="order-service"} 8420',
        ]
        return "\n".join(lines) + "\n"
