from django.core.management.base import BaseCommand
from note.models import Article
import json

class Command(BaseCommand):
    help = '修复文章关键词格式'

    def handle(self, *args, **options):
        articles = Article.objects.all()
        count = 0
        
        for article in articles:
            try:
                # 尝试解析关键词
                keywords = json.loads(article.keywords)
                if not isinstance(keywords, list):
                    # 如果不是列表，则转换为列表
                    article.keywords = json.dumps([])
                    article.save(update_fields=['keywords'])
                    count += 1
                    self.stdout.write(f'修复文章 "{article.title}" 的关键词格式')
            except json.JSONDecodeError:
                # 如果解析失败，则重置为空列表
                article.keywords = json.dumps([])
                article.save(update_fields=['keywords'])
                count += 1
                self.stdout.write(f'修复文章 "{article.title}" 的关键词格式')
        
        self.stdout.write(self.style.SUCCESS(f'成功修复 {count} 篇文章的关键词格式')) 