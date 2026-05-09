from prometheus_client import Counter, Histogram, Gauge

PIPELINE_STAGE_DURATION = Histogram(
    "pipeline_stage_duration_seconds",
    "Duration of pipeline stage execution in seconds",
    ["stage", "production_id"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 300.0),
)

DECISION_OUTCOME = Counter(
    "decision_outcome_total",
    "Total number of decision outcomes",
    ["decision_type", "outcome"],
)

INTEGRATION_FAILURE = Counter(
    "integration_failure_total",
    "Total number of integration failures",
    ["integration", "error_type"],
)

RENDER_JOB_DURATION = Histogram(
    "render_job_duration_seconds",
    "Duration of render job execution in seconds",
    ["render_engine", "status"],
    buckets=(10.0, 30.0, 60.0, 120.0, 300.0, 600.0, 1800.0, 3600.0),
)

ACTIVE_RENDER_JOBS = Gauge(
    "active_render_jobs",
    "Number of currently active render jobs",
    ["render_engine"],
)

CONTEXT_VERIFICATION_SCORE = Histogram(
    "context_verification_score",
    "Context verification score distribution",
    ["check_type"],
    buckets=(0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0),
)

HUMAN_REVIEW_DURATION = Histogram(
    "human_review_duration_seconds",
    "Duration of human review in seconds",
    ["review_type"],
    buckets=(30.0, 60.0, 120.0, 300.0, 600.0, 1800.0),
)


class MetricsCollector:
    @staticmethod
    def record_stage_duration(stage: str, production_id: str, duration: float):
        PIPELINE_STAGE_DURATION.labels(stage=stage, production_id=production_id).observe(duration)

    @staticmethod
    def record_decision(decision_type: str, outcome: str):
        DECISION_OUTCOME.labels(decision_type=decision_type, outcome=outcome).inc()

    @staticmethod
    def record_integration_failure(integration: str, error_type: str):
        INTEGRATION_FAILURE.labels(integration=integration, error_type=error_type).inc()

    @staticmethod
    def record_render_job_duration(render_engine: str, status: str, duration: float):
        RENDER_JOB_DURATION.labels(render_engine=render_engine, status=status).observe(duration)

    @staticmethod
    def set_active_render_jobs(render_engine: str, count: int):
        ACTIVE_RENDER_JOBS.labels(render_engine=render_engine).set(count)

    @staticmethod
    def record_context_verification(check_type: str, score: float):
        CONTEXT_VERIFICATION_SCORE.labels(check_type=check_type).observe(score)

    @staticmethod
    def record_human_review(review_type: str, duration: float):
        HUMAN_REVIEW_DURATION.labels(review_type=review_type).observe(duration)


metrics_collector = MetricsCollector()