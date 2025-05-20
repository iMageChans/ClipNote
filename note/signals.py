from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Article
import os
from django.conf import settings
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz
from django.apps import apps

@receiver(post_save, sender=Article)
def update_sitemap(sender, instance, created, **kwargs):
    """
    当新建或更新文章时，更新站点地图
    支持新的 URL 格式（优先使用关键词，然后是 slug，最后是 ID）
    """
    if not created:  # 如果只是更新文章，不是新建，则不更新站点地图
        return
    
    # 直接重建整个站点地图，确保格式一致
    check_and_update_sitemap()

def create_base_sitemap(sitemap_path):
    """
    创建基本的站点地图文件
    """
    root = ET.Element('urlset')
    root.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    root.set('xmlns:news', 'http://www.google.com/schemas/sitemap-news/0.9')
    root.set('xmlns:xhtml', 'http://www.w3.org/1999/xhtml')
    root.set('xmlns:mobile', 'http://www.google.com/schemas/sitemap-mobile/1.0')
    root.set('xmlns:image', 'http://www.google.com/schemas/sitemap-image/1.1')
    root.set('xmlns:video', 'http://www.google.com/schemas/sitemap-video/1.1')
    
    # 添加首页URL
    url_element = ET.SubElement(root, 'url')
    loc = ET.SubElement(url_element, 'loc')
    loc.text = 'https://heartwellness.app/'
    lastmod = ET.SubElement(url_element, 'lastmod')
    lastmod.text = datetime.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    changefreq = ET.SubElement(url_element, 'changefreq')
    changefreq.text = 'daily'
    priority = ET.SubElement(url_element, 'priority')
    priority.text = '1.0'
    
    # 保存站点地图
    tree = ET.ElementTree(root)
    tree.write(sitemap_path, encoding='UTF-8', xml_declaration=True)

def create_original_sitemap(sitemap_path):
    """
    创建包含原始内容的站点地图文件
    """
    original_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:mobile="http://www.google.com/schemas/sitemap-mobile/1.0" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">
<url><loc>https://heartwellness.app/knowledge/basics/heart-rate-101</loc><lastmod>2025-03-06T10:46:41.986Z</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>
<url><loc>https://heartwellness.app/api/stories</loc><lastmod>2025-03-06T10:46:41.987Z</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>
<url><loc>https://heartwellness.app/knowledge/basics</loc><lastmod>2025-03-06T10:46:41.987Z</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>
<url><loc>https://heartwellness.app/knowledge/health/meditation-benefits</loc><lastmod>2025-03-06T10:46:41.987Z</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>
<url><loc>https://heartwellness.app/knowledge/basics/normal-ranges</loc><lastmod>2025-03-06T10:46:41.987Z</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>
<url><loc>https://heartwellness.app/knowledge/health/stress-heart</loc><lastmod>2025-03-06T10:46:41.987Z</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>
<url><loc>https://heartwellness.app/knowledge/health/exercise</loc><lastmod>2025-03-06T10:46:41.987Z</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>
<url><loc>https://heartwellness.app/knowledge/health</loc><lastmod>2025-03-06T10:46:41.987Z</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>
<url><loc>https://heartwellness.app/knowledge/health/nutrition</loc><lastmod>2025-03-06T10:46:41.987Z</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>
<url><loc>https://heartwellness.app/knowledge/health/exercise-stress</loc><lastmod>2025-03-06T10:46:41.987Z</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>
<url><loc>https://heartwellness.app/knowledge/health/sleep</loc><lastmod>2025-03-06T10:46:41.987Z</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>
<url><loc>https://heartwellness.app/stories</loc><lastmod>2025-03-06T10:46:41.987Z</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>
<url><loc>https://heartwellness.app/tools/breathing-exercise</loc><lastmod>2025-03-06T10:46:41.987Z</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>
<url><loc>https://heartwellness.app/tools</loc><lastmod>2025-03-06T10:46:41.987Z</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>
<url><loc>https://heartwellness.app</loc><lastmod>2025-03-06T10:46:41.987Z</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>
<url><loc>https://heartwellness.app/tools/stress-test</loc><lastmod>2025-03-06T10:46:41.987Z</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>
<url><loc>https://heartwellness.app/about</loc><lastmod>2025-03-06T10:46:41.987Z</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>
<url><loc>https://heartwellness.app/tools/heart-rate-calculator</loc><lastmod>2025-03-06T10:46:41.987Z</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>
<url><loc>https://heartwellness.app/knowledge/health/high-heart-rate</loc><lastmod>2025-03-06T10:46:41.987Z</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>
</urlset>"""
    
    with open(sitemap_path, 'w', encoding='UTF-8') as f:
        f.write(original_content)
    
    print("已创建包含原始内容的站点地图文件")

def check_and_update_sitemap(rebuild=False):
    """
    检查数据库中的所有文章，确保它们都在站点地图中
    
    参数:
    rebuild -- 如果为True，则完全重建站点地图，而不是仅添加缺失的文章
    """
    sitemap_path = os.path.join(settings.BASE_DIR, 'sitemap-0.xml')
    
    # 如果站点地图不存在，创建一个包含原始内容的站点地图
    if not os.path.exists(sitemap_path) or rebuild:
        # 如果需要重建，则先使用基本结构创建一个新的站点地图
        if rebuild:
            create_base_sitemap(sitemap_path)
        else:
            create_original_sitemap(sitemap_path)
        
        # 如果是重建，则需要继续添加所有文章；否则直接返回
        if not rebuild:
            return
    
    try:
        # 如果是重建，则使用已经创建的基本站点地图
        if rebuild:
            # 解析站点地图XML
            tree = ET.parse(sitemap_path)
            root = tree.getroot()
            
            # 获取数据库中的所有文章
            Article = apps.get_model('note', 'Article')
            articles = Article.objects.all()
            
            # 添加每篇文章到站点地图
            for article in articles:
                # 优先使用关键词，然后是 slug，最后是 ID 构建 URL
                keywords = article.get_keywords()
                if keywords:
                    # 使用第一个关键词作为 URL
                    keyword = keywords[0].replace(' ', '-').lower()
                    article_identifier = keyword
                elif article.slug:
                    article_identifier = article.slug
                else:
                    article_identifier = article.id
                    
                # 使用正确的前端 URL 格式
                article_url = f"https://heartwellness.app/knowledge/{article_identifier}"
                
                # 添加文章到站点地图
                add_url_to_sitemap(
                    root, 
                    article_url, 
                    lastmod=article.updated_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                    changefreq='daily',
                    priority='0.9'
                )
                print(f"添加文章到站点地图: {article_url}")
            
            # 保存站点地图
            tree.write(sitemap_path, encoding='UTF-8', xml_declaration=True)
            print("站点地图已完全重建")
            return
            
        # 如果不是重建，则使用之前的逻辑增量更新
        # 读取现有的站点地图文件内容
        with open(sitemap_path, 'r', encoding='UTF-8') as f:
            content = f.read()
        
        # 提取所有URL
        import re
        url_pattern = r'<loc>(.*?)</loc>'
        existing_urls = set(re.findall(url_pattern, content))
        
        # 获取数据库中的所有文章
        Article = apps.get_model('note', 'Article')
        articles = Article.objects.all()
        
        # 检查每篇文章是否在站点地图中
        new_urls = []
        for article in articles:
            # 优先使用关键词，然后是 slug，最后是 ID 构建 URL
            keywords = article.get_keywords()
            if keywords:
                # 使用第一个关键词作为 URL
                keyword = keywords[0].replace(' ', '-').lower()
                article_identifier = keyword
            elif article.slug:
                article_identifier = article.slug
            else:
                article_identifier = article.id
                
            # 使用正确的前端 URL 格式
            article_url = f"https://heartwellness.app/knowledge/{article_identifier}"
            
            # 检查文章 URL 是否已存在
            # 构建可能的 URL 格式：使用关键词、slug 或 ID
            possible_urls = []
            # 关键词 URL
            for kw in article.get_keywords():
                possible_urls.append(f"https://heartwellness.app/knowledge/{kw.replace(' ', '-').lower()}")
            # Slug URL
            if article.slug:
                possible_urls.append(f"https://heartwellness.app/knowledge/{article.slug}")
            # ID URL
            possible_urls.append(f"https://heartwellness.app/knowledge/{article.id}")
            
            # 检查文章的任何一种 URL 是否已在站点地图中
            article_in_sitemap = any(url in existing_urls for url in possible_urls)
            
            if not article_in_sitemap:
                # 如果文章不在站点地图中，准备添加它
                new_url = f"""<url>
<loc>{article_url}</loc>
<lastmod>{article.updated_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}</lastmod>
<changefreq>daily</changefreq>
<priority>0.9</priority>
</url>"""
                new_urls.append(new_url)
                print(f"添加文章到站点地图: {article_url}")
        
        # 如果有新URL要添加
        if new_urls:
            # 在</urlset>前插入新URL
            updated_content = content.replace('</urlset>', '\n'.join(new_urls) + '\n</urlset>')
            
            # 保存更新后的站点地图
            with open(sitemap_path, 'w', encoding='UTF-8') as f:
                f.write(updated_content)
            
            print("站点地图已更新")
        else:
            print("站点地图已是最新")
            
    except Exception as e:
        print(f"检查站点地图时出错: {e}")
        print("由于错误，站点地图未更新")

def add_url_to_sitemap(root, url, lastmod=None, changefreq='daily', priority='0.7'):
    """
    向站点地图中添加 URL
    """
    url_element = ET.SubElement(root, 'url')
    loc = ET.SubElement(url_element, 'loc')
    loc.text = url
    
    if lastmod:
        lastmod_element = ET.SubElement(url_element, 'lastmod')
        lastmod_element.text = lastmod
    
    changefreq_element = ET.SubElement(url_element, 'changefreq')
    changefreq_element.text = changefreq
    
    priority_element = ET.SubElement(url_element, 'priority')
    priority_element.text = priority 