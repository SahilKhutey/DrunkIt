import uuid
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:12]}"
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RequestMetrics:

    def __init__(self):
        self.requests = 0
        self.errors = 0
        self.total_latency = 0.0

    def record(self, latency: float, error: bool = False):
        self.requests += 1
        self.total_latency += latency
        if error:
            self.errors += 1

    @property
    def average_latency( self) -> float:
        if not self.requests:
            return 0.0
        return self.total_latency / self.requests

    @property
    def error_rate(self) -> float:
        if not self.requests:
            return 0.0
        return self.errors / self.requests
