from rest_framework import serializers
from .models import Article


class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["id", "title", "url", "summary", "img", "author", "publish_time"]


class ArticleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = "__all__"
