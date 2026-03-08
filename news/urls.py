from django.urls import path
from .views import ArticleListView, ArticleDetailView, ArticleListAPIView, ArticleDetailAPIView

urlpatterns = [
    path("", ArticleListView.as_view(), name="article-list"),
    path("news/<int:pk>/", ArticleDetailView.as_view(), name="article-detail"),
    path("api/articles/", ArticleListAPIView.as_view(), name="api-article-list"),
    path("api/articles/<int:pk>/", ArticleDetailAPIView.as_view(), name="api-article-detail"),
]
