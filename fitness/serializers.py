from rest_framework import serializers
from .models import BodyPart, Exercise, ContentKeywordMapping
import markdown
from markdownify import markdownify
import re

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
    
    def _format_markdown_content(self, content):
        """格式化markdown内容，确保换行和列表格式正确"""
        if not content:
            return ""
        
        # 步骤1：分离标题和后面的内容
        content = re.sub(r'(##\s+[^#\n]+?)\s+(\d+\.)', r'\1\n\n\2', content)
        content = re.sub(r'(##\s+[^#\n]+?)\s*(-\s)', r'\1\n\n\2', content)
        
        # 步骤2：确保标题在独立的行上
        content = re.sub(r'(##\s+[^#\n]+?)\s*(?=##|\n|$)', r'\n\1\n', content)
        
        # 步骤3：处理数字列表项 - 每个列表项独立一行
        content = re.sub(r'(\d+)\.\s*([^.]+?\.)\s*(?=\d+\.)', r'\1. \2\n', content)
        
        # 步骤4：处理无序列表项 - 更精确地分离每个列表项
        # 匹配 "- 内容." 模式，后面跟着空格和 "- " 的情况
        content = re.sub(r'(-\s[^-]+?\.)\s*(-\s)', r'\1\n\2', content)
        
        # 步骤5：在标题后添加空行
        content = re.sub(r'(##[^\n]+)\n(?!\n)', r'\1\n\n', content)
        
        # 步骤6：处理剩余的无序列表项格式
        content = re.sub(r'(^|\n)([^-\n]*?)(-\s)', r'\1\2\n\3', content)
        
        # 步骤7：清理多余的空行，但保留段落分隔
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 步骤8：移除开头和结尾的空行
        content = content.strip()
        
        return content

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
                    strip=['script', 'style', 'div']  # 移除script、style和div标签
                )
                
                # 应用自定义格式化
                formatted_content = self._format_markdown_content(markdown_content)
                
                return formatted_content
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