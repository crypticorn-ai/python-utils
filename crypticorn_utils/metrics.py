import prometheus_client as _prometheus_client

registry = _prometheus_client.CollectorRegistry()

HTTP_REQUESTS_COUNT = _prometheus_client.Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code", "auth_type"],
    registry=registry,
)

HTTP_REQUEST_DURATION = _prometheus_client.Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["endpoint", "method"],
    registry=registry,
)

REQUEST_SIZE = _prometheus_client.Histogram(
    "http_request_size_bytes",
    "Size of HTTP request bodies",
    ["method", "endpoint"],
    registry=registry,
)

RESPONSE_SIZE = _prometheus_client.Histogram(
    "http_response_size_bytes",
    "Size of HTTP responses",
    ["method", "endpoint"],
    registry=registry,
)
