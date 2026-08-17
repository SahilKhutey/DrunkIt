"""Identity service entrypoint using faccp_platform runtime."""

from faccp_platform.runtime.service import create_service_app

app = create_service_app(
    name="identity-service",
    version="0.1.0",
)
