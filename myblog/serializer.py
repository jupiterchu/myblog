from rest_framework import serializers
from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    """文章序列"""


    class Meta:
        model = Article
        fields = ("title", "context", "url", "create_time")