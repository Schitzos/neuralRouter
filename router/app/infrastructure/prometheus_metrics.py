"""
Prometheus metrics implementation
"""
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from typing import Dict, Any


class PrometheusMetrics:
    """Prometheus metrics collector"""
    
    def __init__(self):
        # Request counters
        self.requests_total = Counter(
            'schitzo_requests_total',
            'Total requests processed',
            ['model', 'tier', 'status']
        )
        
        # Classification latency
        self.classification_latency = Histogram(
            'schitzo_classification_latency_ms',
            'Classification latency in milliseconds',
            buckets=[50, 100, 200, 300, 500, 1000, 2000]
        )
        
        # Cost tracking
        self.cost_total = Counter(
            'schitzo_cost_usd_total',
            'Total cost in USD',
            ['model']
        )
        
        # Token tracking
        self.tokens_total = Counter(
            'schitzo_tokens_total',
            'Total tokens consumed',
            ['model', 'type']
        )
        
        # Fallback tracking
        self.fallbacks_total = Counter(
            'schitzo_fallbacks_total',
            'Total fallbacks triggered',
            ['from_model', 'to_model']
        )
    
    def record_request(self, model: str, tier: str, status: str):
        """Record a request"""
        self.requests_total.labels(model=model, tier=tier, status=status).inc()
    
    def record_classification_latency(self, latency_ms: float):
        """Record classification latency"""
        self.classification_latency.observe(latency_ms)
    
    def record_cost(self, model: str, cost: float):
        """Record cost"""
        self.cost_total.labels(model=model).inc(cost)
    
    def record_tokens(self, model: str, input_tokens: int, output_tokens: int):
        """Record token usage"""
        self.tokens_total.labels(model=model, type="input").inc(input_tokens)
        self.tokens_total.labels(model=model, type="output").inc(output_tokens)
    
    def record_fallback(self, from_model: str, to_model: str):
        """Record fallback"""
        self.fallbacks_total.labels(from_model=from_model, to_model=to_model).inc()
    
    def get_metrics(self) -> Response:
        """Get metrics in Prometheus format"""
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )