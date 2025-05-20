from django.contrib import admin
from .models import Article
from ckeditor.widgets import CKEditorWidget
from django import forms
import json
from django.utils.html import format_html

class ArticleAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    images_input = forms.CharField(
        label='预览图 (多个URL用逗号分隔)', 
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )
    keywords_input = forms.CharField(
        label='关键词 (多个关键词用逗号分隔)', 
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False
    )
    
    class Meta:
        model = Article
        fields = ['title', 'slug', 'content', 'images_input', 'keywords_input']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 如果是编辑现有对象，则填充字段
        if self.instance and self.instance.pk:
            if hasattr(self.instance, 'get_images'):
                images = self.instance.get_images()
                if images:
                    self.fields['images_input'].initial = ', '.join(images)
            
            if hasattr(self.instance, 'get_keywords'):
                keywords = self.instance.get_keywords()
                if keywords:
                    self.fields['keywords_input'].initial = ', '.join(keywords)
                    print(f"关键词: {keywords}")  # 调试信息
                else:
                    print(f"文章 {self.instance.title} 没有关键词")  # 调试信息
    
    def clean_images_input(self):
        images_input = self.cleaned_data.get('images_input', '')
        if not images_input:
            return []
        
        # 分割并清理URL
        images = [url.strip() for url in images_input.split(',') if url.strip()]
        return images
    
    def clean_keywords_input(self):
        keywords_input = self.cleaned_data.get('keywords_input', '')
        if not keywords_input:
            return []
        
        # 分割并清理关键词
        keywords = [keyword.strip() for keyword in keywords_input.split(',') if keyword.strip()]
        print(f"清理后的关键词: {keywords}")  # 调试信息
        return keywords
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # 设置图片和关键词
        instance.set_images(self.cleaned_data.get('images_input', []))
        instance.set_keywords(self.cleaned_data.get('keywords_input', []))
        
        if commit:
            instance.save()
        
        return instance

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    list_display = ('title', 'display_images', 'display_keywords', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'slug')
    readonly_fields = ('created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}  # 自动根据标题生成 slug
    
    def display_images(self, obj):
        images = obj.get_images()
        if not images:
            return "无图片"
        
        image_html = ""
        for i, img_url in enumerate(images[:3]):  # 只显示前3张
            image_html += f'<img src="{img_url}" width="50" height="50" style="margin-right: 5px;" />'
        
        if len(images) > 3:
            image_html += f"...等{len(images)}张"
            
        return format_html(image_html)
    display_images.short_description = '预览图'
    
    def display_keywords(self, obj):
        keywords = obj.get_keywords()
        if not keywords:
            return "无关键词"
        return ", ".join(keywords)
    display_keywords.short_description = '关键词'
    
    def get_fields(self, request, obj=None):
        fields = ['title', 'slug', 'content', 'images_input', 'keywords_input']
        if obj:  # 如果是编辑现有对象
            fields.extend(['created_at', 'updated_at'])
        return fields
