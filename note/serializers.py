from rest_framework import serializers
from bs4 import BeautifulSoup
from .models import Article

class ArticleListSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    keywords = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'description', 'images', 'keywords', 'url', 'created_at']

    def get_description(self, obj, bs4=None):
        soup = BeautifulSoup(obj.content, 'html.parser')
        text = soup.get_text()
        return text[:100] + '...' if len(text) > 100 else text
    
    def get_images(self, obj):
        return obj.get_images()
    
    def get_keywords(self, obj):
        return obj.get_keywords()
    
    def get_url(self, obj):
        keywords = obj.get_keywords()
        if keywords:
            # 使用第一个关键词作为 URL
            keyword = keywords[0].replace(' ', '-').lower()
            return f"/knowledge/{keyword}"
        elif obj.slug:
            # 如果没有关键词，则使用 slug
            return f"/knowledge/{obj.slug}"
        else:
            # 如果没有关键词和 slug，则使用 ID
            return f"/knowledge/{obj.id}"

class ArticleDetailSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    keywords = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'content', 'description', 'images', 'keywords', 'url', 'created_at', 'updated_at']
    
    def get_description(self, obj, bs4=None):
        soup = BeautifulSoup(obj.content, 'html.parser')
        text = soup.get_text()
        return text[:100] + '...' if len(text) > 100 else text
    
    def get_images(self, obj):
        return obj.get_images()
    
    def get_keywords(self, obj):
        return obj.get_keywords()
    
    def get_url(self, obj):
        keywords = obj.get_keywords()
        if keywords:
            # 使用第一个关键词作为 URL
            keyword = keywords[0].replace(' ', '-').lower()
            return f"/knowledge/{keyword}"
        elif obj.slug:
            # 如果没有关键词，则使用 slug
            return f"/knowledge/{obj.slug}"
        else:
            # 如果没有关键词和 slug，则使用 ID
            return f"/knowledge/{obj.id}"

class ArticleSerializer(serializers.ModelSerializer):
    images = serializers.ListField(child=serializers.CharField(), required=False, source='get_images')
    keywords = serializers.ListField(child=serializers.CharField(), required=False, source='get_keywords')
    
    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'content', 'images', 'keywords', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        images = validated_data.pop('get_images', [])
        keywords = validated_data.pop('get_keywords', [])
        article = Article.objects.create(**validated_data)
        article.set_images(images)
        article.set_keywords(keywords)
        article.save()
        return article
    
    def update(self, instance, validated_data):
        if 'get_images' in validated_data:
            instance.set_images(validated_data.pop('get_images'))
        if 'get_keywords' in validated_data:
            instance.set_keywords(validated_data.pop('get_keywords'))
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance