"""
Custom Prometheus collectors for chat completion and RAG observability.

HTTP-level RED metrics (rate/errors/duration per route) come from
prometheus-fastapi-instrumentator; the collectors here add the LLM-specific
dimensions that HTTP metrics cannot see. Keep label cardinality low — never use
per-user or per-request identifiers as labels (those belong in logs).
"""

from prometheus_client import Counter, Histogram

# Latency buckets (seconds) tuned to observed TTFB/generation/retrieval ranges.
_LATENCY_BUCKETS = (0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 13.0, 21.0)

chat_completions_total = Counter(
    "rag_chat_completions_total",
    "Chat completions by model and outcome.",
    labelnames=("model", "outcome"),
)

chat_ttfb_seconds = Histogram(
    "rag_chat_ttfb_seconds",
    "Time to first token from the LLM provider.",
    labelnames=("model",),
    buckets=_LATENCY_BUCKETS,
)

chat_generation_seconds = Histogram(
    "rag_chat_generation_seconds",
    "Full LLM generation duration.",
    labelnames=("model",),
    buckets=_LATENCY_BUCKETS,
)

rag_retrieval_seconds = Histogram(
    "rag_retrieval_seconds",
    "RAG retrieval duration (embedding + vector search).",
    buckets=_LATENCY_BUCKETS,
)

chat_tokens_total = Counter(
    "rag_chat_tokens_total",
    "Tokens processed, by model and kind.",
    labelnames=("model", "kind"),
)

llm_provider_errors_total = Counter(
    "rag_llm_provider_errors_total",
    "Transient LLM provider errors surfaced after the SDK's retries.",
    labelnames=("type",),
)
