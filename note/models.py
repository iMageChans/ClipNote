from django.db import models
from ckeditor.fields import RichTextField
import json
from django.utils.text import slugify

class Article(models.Model):
    title = models.CharField('标题', max_length=200)
    content = RichTextField('内容')
    slug = models.SlugField('URL别名', max_length=255, unique=True, blank=True, null=True)
    images = models.TextField('预览图', blank=True, default='[]')
    keywords = models.TextField('关键词', blank=True, default='[]')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # 如果没有提供 slug，则根据标题自动生成
        if not self.slug:
            self.slug = slugify(self.title)
            
            # 确保 slug 唯一
            original_slug = self.slug
            counter = 1
            while Article.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
                
        super().save(*args, **kwargs)

    def get_images(self):
        """返回图片URL列表"""
        try:
            return json.loads(self.images)
        except:
            return []
    
    def set_images(self, value):
        """设置图片URL列表"""
        if isinstance(value, list):
            self.images = json.dumps(value)
        else:
            self.images = json.dumps([])
    
    def get_keywords(self):
        """返回关键词列表"""
        try:
            return json.loads(self.keywords)
        except:
            return []
    
    def set_keywords(self, value):
        """设置关键词列表"""
        if isinstance(value, list):
            self.keywords = json.dumps(value)
        else:
            self.keywords = json.dumps([])

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章管理'

# Create your models here.
