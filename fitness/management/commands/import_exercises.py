from django.core.management.base import BaseCommand
from fitness.models import BodyPart, Exercise
from django.utils.text import slugify
from django.db import IntegrityError
from django.utils import timezone
import os

class Command(BaseCommand):
    help = '从文本文件导入健身动作数据'

    def clean_name(self, name):
        """清理名称，去除括号并将空格替换为连字符"""
        # 移除括号及其内容
        cleaned = ''
        skip = 0
        for i, char in enumerate(name):
            if char == '(':
                skip += 1
            elif char == ')':
                skip -= 1
            elif skip == 0:
                cleaned += char
        
        # 处理斜杠
        cleaned = cleaned.replace('/', '-')
        # 处理空格
        cleaned = cleaned.strip()
        # 将连续的空格替换为单个连字符
        cleaned = '-'.join(word for word in cleaned.split())
        return cleaned

    def generate_unique_slug(self, name, model_class, counter=1):
        """生成唯一的slug"""
        base_slug = slugify(name)
        slug = base_slug
        while model_class.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def generate_sitemap(self):
        """生成sitemap-exercises.xml文件"""
        current_time = timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        # 获取所有健身动作
        exercises = Exercise.objects.all().order_by('created_at')
        
        # 生成sitemap内容
        sitemap_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:mobile="http://www.google.com/schemas/sitemap-mobile/1.0" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">
<url><loc>https://heartwellness.app/exercises</loc><lastmod>{}</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>'''.format(current_time)
        
        # 为每个健身动作添加URL
        for exercise in exercises:
            exercise_url = f"https://heartwellness.app/exercises/{exercise.slug}"
            lastmod = exercise.updated_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            sitemap_content += f'''
<url><loc>{exercise_url}</loc><lastmod>{lastmod}</lastmod><changefreq>weekly</changefreq><priority>0.6</priority></url>'''
        
        sitemap_content += '''
</urlset>'''
        
        # 写入sitemap文件
        sitemap_path = 'sitemap-exercises.xml'
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        
        self.stdout.write(f'已生成sitemap文件: {sitemap_path}，包含 {exercises.count()} 个健身动作URL')

    def handle(self, *args, **options):
        # 存储已处理的部位和动作，避免重复创建
        body_parts = {}
        processed_exercises = set()
        
        # 读取文件
        with open('fitness/exercises', 'r', encoding='utf-8') as file:
            for line in file:
                # 分割动作名称和部位
                parts = line.strip().split(',')
                if len(parts) != 2:
                    self.stdout.write(self.style.WARNING(f'跳过无效行: {line.strip()}'))
                    continue
                    
                exercise_name, body_part_name = parts
                exercise_name = exercise_name.strip()
                body_part_name = body_part_name.strip()
                
                # 跳过重复的动作
                if exercise_name in processed_exercises:
                    continue
                processed_exercises.add(exercise_name)
                
                # 清理名称
                clean_exercise_name = self.clean_name(exercise_name)
                clean_body_part_name = self.clean_name(body_part_name)
                
                try:
                    # 获取或创建部位
                    if clean_body_part_name not in body_parts:
                        body_part, created = BodyPart.objects.get_or_create(
                            name=body_part_name,
                            defaults={
                                'slug': self.generate_unique_slug(clean_body_part_name, BodyPart),
                                'description': f'{body_part_name}相关的健身动作'
                            }
                        )
                        body_parts[clean_body_part_name] = body_part
                        if created:
                            self.stdout.write(f'创建新部位: {body_part_name}')
                    
                    body_part = body_parts[clean_body_part_name]
                    
                    # 创建健身动作
                    exercise, created = Exercise.objects.get_or_create(
                        name=exercise_name,
                        defaults={
                            'slug': self.generate_unique_slug(clean_exercise_name, Exercise),
                            'body_part': body_part,
                            'description': f'{exercise_name} 是一个针对 {body_part_name} 的训练动作。'
                        }
                    )
                    
                    if created:
                        self.stdout.write(f'创建新动作: {exercise_name} ({body_part_name})')
                
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'处理 {exercise_name} 时出错: {str(e)}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'数据导入完成！\n'
                f'共创建 {len(body_parts)} 个部位和 {len(processed_exercises)} 个动作。'
            )
        )
        
        # 生成sitemap文件
        self.generate_sitemap() 