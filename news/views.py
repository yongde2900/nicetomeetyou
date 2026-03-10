import time
import logging
from django.conf import settings
from django.views.generic import TemplateView, DetailView
from django_redis import get_redis_connection
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from django.core.cache import cache
from .models import Article
from .serializers import ArticleListSerializer, ArticleDetailSerializer

logger = logging.getLogger(__name__)

LOCK_TTL = 10    # 分散式鎖最長持有秒數
MAX_RETRIES = 10  # 取不到鎖時最多重試次數


class ArticleListView(TemplateView):
    template_name = "news/list.html"


class ArticleDetailView(DetailView):
    model = Article
    template_name = "news/detail.html"
    context_object_name = "article"


class ArticleListAPIView(ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleListSerializer

    def list(self, request, *args, **kwargs):
        page = request.query_params.get("page", 1)
        cache_key = f"articles:page:{page}"
        lock_key = f"lock:articles:page:{page}"

        # 1. Cache hit
        cached = cache.get(cache_key)
        if cached is not None:
            logger.debug("Cache hit: %s", cache_key)
            return Response(cached)

        # 2. Cache miss → 嘗試取得分散式鎖
        redis = get_redis_connection("default")
        acquired = redis.set(lock_key, "1", nx=True, ex=LOCK_TTL)

        if acquired:
            try:
                logger.debug("Lock acquired: %s", lock_key)
                response = super().list(request, *args, **kwargs)
                cache.set(cache_key, response.data, settings.CACHE_TTL)
                return response
            finally:
                redis.delete(lock_key)
        else:
            # 3. 取不到鎖 → 每秒重試讀 cache
            logger.debug("Lock busy, retrying cache: %s", cache_key)
            for i in range(MAX_RETRIES):
                time.sleep(1)
                cached = cache.get(cache_key)
                if cached is not None:
                    logger.debug("Cache ready after %d retry(s)", i + 1)
                    return Response(cached)

            # 重試耗盡仍無 cache，直接打 DB（fallback）
            logger.warning(
                "Cache still empty after %d retries, falling back to DB", MAX_RETRIES)
            return super().list(request, *args, **kwargs)


class ArticleDetailAPIView(RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleDetailSerializer
