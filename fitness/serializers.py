from rest_framework import serializers
from .models import BodyPart, Exercise, ContentKeywordMapping
import markdown
from markdownify import markdownify

class BodyPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyPart
        fields = ['id', 'name', 'slug', 'description']

class ContentKeywordMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentKeywordMapping
        fields = ['keyword', 'content_type', 'relevance_score']

class ExerciseListSerializer(serializers.ModelSerializer):
    body_part = BodyPartSerializer(read_only=True)
    url = serializers.SerializerMethodField()
    youtube_embed_url = serializers.SerializerMethodField()
    youtube_thumbnail = serializers.SerializerMethodField()
    keywords = serializers.SerializerMethodField()
    
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'slug', 'body_part', 'image_url', 'image_width', 
                 'image_height', 'url', 'youtube_url', 'youtube_embed_url', 
                 'youtube_thumbnail', 'ai_generated', 'keywords', 'created_at']
    
    def get_url(self, obj):
        return f"/api/exercises/{obj.body_part.slug}/{obj.slug}"
    
    def get_youtube_embed_url(self, obj):
        return obj.get_youtube_embed_url()
    
    def get_youtube_thumbnail(self, obj):
        return obj.get_youtube_thumbnail_url()
    
    def get_keywords(self, obj):
        return obj.get_generated_keywords()[:5]  # 只返回前5个关键词

class ExerciseDetailSerializer(serializers.ModelSerializer):
    body_part = BodyPartSerializer(read_only=True)
    url = serializers.SerializerMethodField()
    youtube_embed_url = serializers.SerializerMethodField()
    youtube_thumbnail = serializers.SerializerMethodField()
    youtube_thumbnail_hd = serializers.SerializerMethodField()
    keywords = serializers.SerializerMethodField()
    keyword_mappings = ContentKeywordMappingSerializer(many=True, read_only=True)
    description_html = serializers.SerializerMethodField()
    description_markdown = serializers.SerializerMethodField()
    
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'slug', 'body_part', 'description', 'description_markdown', 
                 'description_html', 'youtube_url', 'youtube_embed_url', 'youtube_thumbnail', 
                 'youtube_thumbnail_hd', 'image_url', 'image_width', 'image_height', 'url', 
                 'ai_generated', 'keywords', 'keyword_mappings', 'created_at', 'updated_at']
    
    def get_url(self, obj):
        return f"/api/exercises/{obj.body_part.slug}/{obj.slug}"
    
    def get_youtube_embed_url(self, obj):
        return obj.get_youtube_embed_url()
    
    def get_youtube_thumbnail(self, obj):
        return obj.get_youtube_thumbnail_url()
    
    def get_youtube_thumbnail_hd(self, obj):
        return obj.get_youtube_thumbnail_url('maxresdefault')
    
    def get_keywords(self, obj):
        return obj.get_generated_keywords()
    
    def get_description_markdown(self, obj):
        """返回标准markdown格式"""
        if obj.description:
            try:
                # 将HTML转换为markdown格式
                markdown_content = markdownify(
                    obj.description,
                    heading_style='ATX',  # 使用 # 格式的标题
                    bullets='-',          # 使用 - 作为列表符号
                    strong_mark='**',     # 使用 ** 作为粗体标记
                    em_mark='*',          # 使用 * 作为斜体标记
                    convert=['b', 'strong', 'i', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img'],
                    strip=['script', 'style']  # 移除script和style标签
                )
                return markdown_content.strip()
            except Exception:
                # 如果转换失败，返回原始HTML内容
                return obj.description
        return ""
    
    def get_description_html(self, obj):
        """返回转换后的HTML格式"""
        if obj.description:
            try:
                # 配置markdown扩展
                html = markdown.markdown(
                    obj.description,
                    extensions=[
                        'markdown.extensions.extra',
                        'markdown.extensions.codehilite',
                        'markdown.extensions.toc'
                    ]
                )
                return html
            except Exception:
                # 如果转换失败，返回原始文本
                return obj.description
        return "" 