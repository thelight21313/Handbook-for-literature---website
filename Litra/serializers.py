from .models import Writers, Works, Facts
import django
from rest_framework.renderers import JSONRenderer
from rest_framework import serializers


class WriterSerializer(serializers.ModelSerializer):
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Writers
        fields = ['id', 'full_name', 'image_url', 'birth_year', 'death_year', 'genre', 'quote', 'biography', 'century', 'is_favorite']

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(id=request.user.id).exists()
        return False


class WorksSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author_name.full_name')
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Works
        fields = ['id', 'genre', 'period', 'cover_image', 'title', 'author_name', 'publication_year', 'description', 'is_favorite']

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(id=request.user.id).exists()
        return False


class FactsSerializer(serializers.ModelSerializer):
    writer_name = serializers.CharField(source='writer.full_name', read_only=True)
    work_title = serializers.CharField(source='work.title', read_only=True)
    is_laked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Facts
        fields = ['id', 'title', 'content', 'category', 'period', 'image_url', 'source', 'writer_name', 'work_title', 'is_featured', 'is_laked', 'likes_count']

    def get_is_laked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.all.count()
        return False

    def get_likes_count(self, obj):
        return obj.likes.count()


class FastTest(serializers.ModelSerializer):
    pass


class PropertyTest(serializers.ModelSerializer):
    pass
