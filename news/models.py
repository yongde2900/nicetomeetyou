from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=512)
    url = models.URLField(unique=True)
    summary = models.TextField(blank=True)
    img = models.URLField(blank=True)
    content = models.TextField(blank=True)
    author = models.CharField(max_length=255, blank=True)
    publish_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-publish_time"]

    def __str__(self):
        return self.title
