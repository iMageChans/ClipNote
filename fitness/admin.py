from django.contrib import admin
from django.utils.html import format_html
from .models import BodyPart, Exercise, ContentKeywordMapping

@admin.register(BodyPart)
class BodyPartAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'body_part', 'ai_generated', 'display_image', 'has_youtube', 'keyword_count', 'created_at')
    list_filter = ('body_part', 'ai_generated', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('image_width', 'image_height', 'generated_keywords', 'keyword_count_detail', 'youtube_embed_preview', 'image_preview', 'created_at', 'updated_at')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'slug', 'body_part')
        }),
        ('内容描述', {
            'fields': ('description', 'ai_generated')
        }),
        ('媒体文件', {
            'fields': ('image_url', 'image_preview', 'image_width', 'image_height', 'youtube_url', 'youtube_embed_preview')
        }),
        ('关键词和映射', {
            'fields': ('generated_keywords', 'keyword_count_detail'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def display_image(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" onerror="this.src=\'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTAiIGhlaWdodD0iNTAiIHZpZXdCb3g9IjAgMCA1MCA1MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjUwIiBoZWlnaHQ9IjUwIiBmaWxsPSIjZjNmNGY2Ii8+CjxwYXRoIGQ9Ik0yNSAyMEM0MS41IDIwIDQ1IDI1IDQ1IDMwVjM1QzQ1IDQwIDQxLjUgNDUgMjUgNDVTNSA0MCA1IDM1VjMwQzUgMjUgOC41IDIwIDI1IDIwWiIgZmlsbD0iIzlmYTZiNyIvPgo8Y2lyY2xlIGN4PSIxOCIgY3k9IjI3IiByPSIzIiBmaWxsPSIjZjNmNGY2Ii8+CjxwYXRoIGQ9Ik0xNSAzNUwyMCAzMEwyNSAzNUwzNSAyNUw0MCAzNSIgc3Ryb2tlPSIjZjNmNGY2IiBzdHJva2Utd2lkdGg9IjIiIGZpbGw9Im5vbmUiLz4KPHN2Zz4K\'" />', obj.image_url)
        return format_html('<span style="color: #999;">无图片</span>')
    display_image.short_description = '预览图'
    
    def has_youtube(self, obj):
        if obj.youtube_url:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_youtube.short_description = 'YouTube'
    
    def keyword_count(self, obj):
        return obj.keyword_mappings.count()
    keyword_count.short_description = '关键词数量'
    
    def keyword_count_detail(self, obj):
        mappings = obj.keyword_mappings.all()
        if not mappings:
            return "无关键词映射"
        
        html = "<ul>"
        for mapping in mappings[:10]:  # 只显示前10个
            html += f"<li><strong>{mapping.content_type}</strong>: {mapping.keyword} (评分: {mapping.relevance_score})</li>"
        if mappings.count() > 10:
            html += f"<li>... 还有 {mappings.count() - 10} 个关键词</li>"
        html += "</ul>"
        return format_html(html)
    keyword_count_detail.short_description = '关键词映射详情'
    
    def youtube_embed_preview(self, obj):
        embed_url = obj.get_youtube_embed_url()
        if embed_url:
            return format_html(
                '<a href="{}" target="_blank">预览嵌入链接</a><br>'
                '<small>{}</small>',
                embed_url, embed_url
            )
        return "无YouTube链接"
    youtube_embed_preview.short_description = 'YouTube嵌入预览'
    
    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<div style="text-align: center;">'
                '<img src="{}" style="max-width: 300px; max-height: 200px; border: 1px solid #ddd; border-radius: 4px;" '
                'onerror="this.style.display=\'none\'; this.nextElementSibling.style.display=\'block\';" />'
                '<div style="display: none; padding: 20px; background: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; color: #666;">'
                '图片加载失败<br><small>请检查URL是否正确</small></div>'
                '<br><small style="color: #666; word-break: break-all;">{}</small>'
                '</div>',
                obj.image_url, obj.image_url
            )
        return format_html('<span style="color: #999;">无图片URL</span>')
    image_preview.short_description = '图片预览'

class ContentKeywordMappingInline(admin.TabularInline):
    model = ContentKeywordMapping
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(ContentKeywordMapping)
class ContentKeywordMappingAdmin(admin.ModelAdmin):
    list_display = ('exercise', 'keyword', 'content_type', 'relevance_score', 'created_at')
    list_filter = ('content_type', 'relevance_score', 'created_at')
    search_fields = ('exercise__name', 'keyword')
    ordering = ('-relevance_score', 'exercise__name')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('exercise')
