from prometheus_client import Counter, Histogram, Gauge
from starlette_prometheus import metrics, PrometheusMiddleware


# Request metrics

#-----------------------------------------------------------------------------#
# Command processor metrics

process_command_total = Counter(
    "process_command_total",
    "Total number of process_command calls",
    ["status", "type"]  # status: success/error, type: direct/llm-classified
)

process_command_duration_seconds = Histogram(
    "process_command_duration_seconds",
    "Duration of process_command in seconds",
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

llm_classification_duration_seconds = Histogram(
    "llm_classification_duration_seconds",
    "Duration of LLM classification in seconds",
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

llm_data_prep_duration_seconds = Histogram(
    "llm_data_prep_duration_seconds",
    "Duration of LLM data preparation in seconds",
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

llm_inference_command_duration_seconds = Histogram(
    "llm_inference_command_duration_seconds",
    "Duration of LLM inference for command execution in seconds",
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

llm_tokens_total = Counter(
    "llm_tokens_total",
    "Total number of LLM tokens used",
    ["type"]  # type: prompt/completion
)

def setup_metrics(app):
    """Set up Prometheus metrics middleware and endpoints.

    Args:
        app: FastAPI application instance
    """
    # Add Prometheus middleware
    # app.add_middleware(PrometheusMiddleware)

    # Add metrics endpoint
    app.add_route("/metrics", metrics)
