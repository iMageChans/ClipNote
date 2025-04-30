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
        fields = ['title', 'content', 'images_input', 'keywords_input']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 如果是编辑现有对象，则填充字段
        if self.instance and self.instance.pk:
            if hasattr(self.instance, 'get_images'):
                images = self.instance.get_images()
                if images:
                    self.fields['images_input'].initial = ','.join(images)
            if hasattr(self.instance, 'get_keywords'):
                keywords = self.instance.get_keywords()
                if keywords:
                    self.fields['keywords_input'].initial = ','.join(keywords)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # 处理图片
        images_input = self.cleaned_data.get('images_input', '')
        if images_input:
            images_list = [url.strip() for url in images_input.split(',') if url.strip()]
            instance.set_images(images_list)
        else:
            instance.set_images([])
        
        # 处理关键词
        keywords_input = self.cleaned_data.get('keywords_input', '')
        if keywords_input:
            keywords_list = [keyword.strip() for keyword in keywords_input.split(',') if keyword.strip()]
            instance.set_keywords(keywords_list)
        else:
            instance.set_keywords([])
        
        if commit:
            instance.save()
        return instance

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    list_display = ('title', 'display_images', 'display_keywords', 'created_at')
    search_fields = ('title',)
    readonly_fields = ('created_at', 'updated_at')
    
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
        fields = ['title', 'content', 'images_input', 'keywords_input']
        if obj:  # 如果是编辑现有对象
            fields.extend(['created_at', 'updated_at'])
        return fields
