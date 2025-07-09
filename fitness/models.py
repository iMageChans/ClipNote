from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
import re
import json

# Create your models here.

class BodyPart(models.Model):
    """健身部位分类"""
    name = models.CharField('部位名称', max_length=100)
    slug = models.SlugField('URL别名', max_length=100, unique=True, blank=True)
    description = models.TextField('描述', blank=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = '健身部位'
        verbose_name_plural = '健身部位管理'

class Exercise(models.Model):
    """健身动作"""
    name = models.CharField('动作名称', max_length=200)
    slug = models.SlugField('URL别名', max_length=200, unique=True, blank=True)
    body_part = models.ForeignKey(BodyPart, on_delete=models.CASCADE, related_name='exercises', verbose_name='锻炼部位')
    description = RichTextField('动作描述')
    youtube_url = models.URLField('YouTube视频链接', blank=True)
    image = models.ImageField('动作图片', upload_to='exercises/%Y/%m/', blank=True)
    image_width = models.PositiveIntegerField('图片宽度', null=True, blank=True)
    image_height = models.PositiveIntegerField('图片高度', null=True, blank=True)
    generated_keywords = models.TextField('生成内容关键词', blank=True, default='[]', help_text='JSON格式存储生成内容的关键词')
    ai_generated = models.BooleanField('AI生成内容', default=False, help_text='标记是否由AI生成描述')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_youtube_embed_url(self):
        """
        将YouTube观看链接转换为嵌入链接
        支持多种YouTube URL格式
        """
        if not self.youtube_url:
            return None
            
        # 支持的YouTube URL格式:
        # https://www.youtube.com/watch?v=VIDEO_ID
        # https://youtu.be/VIDEO_ID
        # https://www.youtube.com/embed/VIDEO_ID
        
        youtube_regex = re.compile(
            r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:watch\?v=|embed/)|youtu\.be/)([a-zA-Z0-9_-]{11})'
        )
        
        match = youtube_regex.search(self.youtube_url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/embed/{video_id}"
        
        return None
    
    def get_youtube_thumbnail_url(self, quality='hqdefault'):
        """
        获取YouTube视频缩略图
        质量选项: default, mqdefault, hqdefault, sddefault, maxresdefault
        """
        if not self.youtube_url:
            return None
            
        youtube_regex = re.compile(
            r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:watch\?v=|embed/)|youtu\.be/)([a-zA-Z0-9_-]{11})'
        )
        
        match = youtube_regex.search(self.youtube_url)
        if match:
            video_id = match.group(1)
            return f"https://img.youtube.com/vi/{video_id}/{quality}.jpg"
        
        return None
    
    def get_generated_keywords(self):
        """返回生成内容的关键词列表"""
        try:
            return json.loads(self.generated_keywords)
        except:
            return []
    
    def set_generated_keywords(self, keywords):
        """设置生成内容的关键词列表"""
        if isinstance(keywords, list):
            self.generated_keywords = json.dumps(keywords, ensure_ascii=False)
        else:
            self.generated_keywords = json.dumps([], ensure_ascii=False)
    
    def extract_keywords_from_description(self):
        """从描述中提取关键词"""
        if not self.description:
            return []
        
        # 提取markdown标题作为关键词
        import re
        headers = re.findall(r'^#+\s*(.+)$', self.description, re.MULTILINE)
        
        # 清理标题，移除markdown符号
        keywords = []
        for header in headers:
            clean_header = re.sub(r'[#*_`]', '', header).strip()
            if clean_header and len(clean_header) > 2:
                keywords.append(clean_header.lower())
        
        # 添加动作名称相关的关键词
        exercise_keywords = [
            self.name.lower(),
            self.body_part.name.lower() if self.body_part else '',
            'exercise', 'workout', 'fitness', 'training'
        ]
        
        keywords.extend([k for k in exercise_keywords if k])
        
        # 去重并返回
        return list(set(keywords))
    
    class Meta:
        verbose_name = '健身动作'
        verbose_name_plural = '健身动作管理'

class ContentKeywordMapping(models.Model):
    """内容关键词映射表"""
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='keyword_mappings', verbose_name='健身动作')
    keyword = models.CharField('关键词', max_length=100)
    content_type = models.CharField('内容类型', max_length=50, choices=[
        ('what_is', 'What is'),
        ('tutorial', 'Tutorial'),
        ('mistakes', 'Common Mistakes'),
        ('tips', 'Tips for Better Results'),
        ('muscles', 'Muscles Worked'),
        ('other', 'Other')
    ])
    relevance_score = models.FloatField('相关性评分', default=1.0, help_text='0.0-1.0之间的相关性评分')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    def __str__(self):
        return f"{self.exercise.name} - {self.keyword} ({self.content_type})"
    
    class Meta:
        verbose_name = '内容关键词映射'
        verbose_name_plural = '内容关键词映射管理'
        unique_together = ['exercise', 'keyword', 'content_type']
