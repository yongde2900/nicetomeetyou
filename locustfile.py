"""
QPS Benchmark for NBA News List API

目標：新聞列表 API /api/articles/ 達到 QPS > 100，失敗率 = 0%

執行方式（headless，30秒，110 users，spawn rate 20/s）：
    locust --headless -u 110 -r 20 -t 30s --host http://localhost:8000

或開啟 Web UI 互動調整：
    locust --host http://localhost:8000
    # 瀏覽器開 http://localhost:8089

成功標準：
    - /api/articles/ RPS >= 100
    - 失敗率 = 0%
    - p95 response time < 500ms
"""

from locust import HttpUser, task, constant_throughput, events
import logging

logger = logging.getLogger(__name__)


class NewsListUser(HttpUser):
    """
    每個 user 每秒發 1 個 request（constant_throughput）
    110 users → 理論上限 110 RPS，扣除延遲後目標 >= 100 RPS
    """
    wait_time = constant_throughput(1)

    @task
    def get_news_list(self):
        with self.client.get("/api/articles/", catch_response=True) as res:
            if res.status_code == 200:
                data = res.json()
                if "results" not in data:
                    res.failure("Response missing 'results' field")
            else:
                res.failure(f"Unexpected status: {res.status_code}")


@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    stats = environment.stats.total
    rps = stats.total_rps
    fail_ratio = stats.fail_ratio

    p50 = stats.get_response_time_percentile(0.5)
    p95 = stats.get_response_time_percentile(0.95)
    p99 = stats.get_response_time_percentile(0.99)

    logger.info("=" * 50)
    logger.info(f"Total requests  : {stats.num_requests}")
    logger.info(f"Failures        : {stats.num_failures} ({fail_ratio:.1%})")
    logger.info(f"Avg RPS         : {rps:.1f}")
    logger.info(f"p50 latency     : {p50:.0f}ms")
    logger.info(f"p95 latency     : {p95:.0f}ms")
    logger.info(f"p99 latency     : {p99:.0f}ms")
    logger.info("=" * 50)

    passed = rps >= 100 and fail_ratio == 0 and p95 < 500
    if passed:
        logger.info(
            f"✅ PASS: RPS={rps:.1f} >= 100, failures=0%, p95={p95:.0f}ms < 500ms")
    else:
        reasons = []
        if rps < 100:
            reasons.append(f"RPS={rps:.1f} < 100")
        if fail_ratio > 0:
            reasons.append(f"failures={fail_ratio:.1%}")
        if p95 >= 500:
            reasons.append(f"p95={p95:.0f}ms >= 500ms")
        logger.warning(f"❌ FAIL: {', '.join(reasons)}")
        environment.process_exit_code = 1
