from django.core.management.base import BaseCommand
from note.models import Article
from django.utils.text import slugify

class Command(BaseCommand):
    help = '为所有现有文章生成 slug'

    def handle(self, *args, **options):
        articles = Article.objects.filter(slug__isnull=True) | Article.objects.filter(slug='')
        count = articles.count()
        self.stdout.write(self.style.SUCCESS(f'开始为 {count} 篇文章生成 slug...'))
        
        for article in articles:
            # 生成基础 slug
            base_slug = slugify(article.title)
            
            # 确保 slug 唯一
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exclude(id=article.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            article.slug = slug
            article.save(update_fields=['slug'])
            
            self.stdout.write(f'为文章 "{article.title}" 生成 slug: {slug}')
        
        self.stdout.write(self.style.SUCCESS(f'成功为 {count} 篇文章生成 slug')) 