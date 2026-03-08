from django.views.generic import ListView, DetailView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Article
from .serializers import ArticleListSerializer, ArticleDetailSerializer


class ArticleListView(ListView):
    model = Article
    template_name = "news/list.html"
    context_object_name = "articles"
    paginate_by = 20


class ArticleDetailView(DetailView):
    model = Article
    template_name = "news/detail.html"
    context_object_name = "article"


class ArticleListAPIView(ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleListSerializer


class ArticleDetailAPIView(RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleDetailSerializer
