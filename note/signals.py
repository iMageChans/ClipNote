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
    loc.text = 'https://heartwellness.app'
    lastmod = ET.SubElement(url_element, 'lastmod')
    lastmod.text = datetime.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    changefreq = ET.SubElement(url_element, 'changefreq')
    changefreq.text = 'daily'
    priority = ET.SubElement(url_element, 'priority')
    priority.text = '1.0'
    
    # 创建XML树
    tree = ET.ElementTree(root)
    
    # 保存到文件
    tree.write(sitemap_path, encoding='UTF-8', xml_declaration=True)

def check_and_update_sitemap():
    """
    检查数据库中的所有文章，重建站点地图，确保格式正确且没有重复项
    """
    sitemap_path = os.path.join(settings.BASE_DIR, 'sitemap-0.xml')
    
    try:
        # 创建一个全新的站点地图
        root = ET.Element('urlset')
        root.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        root.set('xmlns:news', 'http://www.google.com/schemas/sitemap-news/0.9')
        root.set('xmlns:xhtml', 'http://www.w3.org/1999/xhtml')
        root.set('xmlns:mobile', 'http://www.google.com/schemas/sitemap-mobile/1.0')
        root.set('xmlns:image', 'http://www.google.com/schemas/sitemap-image/1.1')
        root.set('xmlns:video', 'http://www.google.com/schemas/sitemap-video/1.1')
        
        # 添加首页URL
        add_url_to_sitemap(root, 'https://heartwellness.app', priority='1.0')
        
        # 添加其他重要页面
        important_urls = [
            'https://heartwellness.app/knowledge',
            'https://heartwellness.app/tools',
            'https://heartwellness.app/about',
            'https://heartwellness.app/stories',
        ]
        
        for url in important_urls:
            add_url_to_sitemap(root, url, priority='0.8')
        
        # 获取数据库中的所有文章
        Article = apps.get_model('note', 'Article')
        articles = Article.objects.all()
        
        # 为每篇文章添加URL
        for article in articles:
            article_url = f"https://heartwellness.app/knowledge/{article.id}"
            add_url_to_sitemap(
                root, 
                article_url, 
                lastmod=article.updated_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                priority='0.9'
            )
            print(f"添加文章到站点地图: {article_url}")
        
        # 创建XML树并保存
        tree = ET.ElementTree(root)
        
        # 使用minidom来格式化XML，使其具有正确的缩进和换行
        from xml.dom import minidom
        xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        
        # 写入文件
        with open(sitemap_path, 'w', encoding='UTF-8') as f:
            f.write(xmlstr)
            
        print("站点地图已重建并格式化")
            
    except Exception as e:
        print(f"重建站点地图时出错: {e}")

def add_url_to_sitemap(root, url, lastmod=None, changefreq='daily', priority='0.7'):
    """
    向站点地图添加URL
    """
    url_element = ET.SubElement(root, 'url')
    
    loc = ET.SubElement(url_element, 'loc')
    loc.text = url
    
    if lastmod is None:
        lastmod = datetime.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    
    lastmod_element = ET.SubElement(url_element, 'lastmod')
    lastmod_element.text = lastmod
    
    changefreq_element = ET.SubElement(url_element, 'changefreq')
    changefreq_element.text = changefreq
    
    priority_element = ET.SubElement(url_element, 'priority')
    priority_element.text = priority 