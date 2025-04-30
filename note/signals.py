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
    检查数据库中的所有文章，更新站点地图，保留原有URL，确保格式正确且没有重复项
    """
    sitemap_path = os.path.join(settings.BASE_DIR, 'sitemap-0.xml')
    
    try:
        # 创建一个新的站点地图根元素
        root = ET.Element('urlset')
        root.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        root.set('xmlns:news', 'http://www.google.com/schemas/sitemap-news/0.9')
        root.set('xmlns:xhtml', 'http://www.w3.org/1999/xhtml')
        root.set('xmlns:mobile', 'http://www.google.com/schemas/sitemap-mobile/1.0')
        root.set('xmlns:image', 'http://www.google.com/schemas/sitemap-image/1.1')
        root.set('xmlns:video', 'http://www.google.com/schemas/sitemap-video/1.1')
        
        # 存储已添加的URL，用于去重
        added_urls = set()
        
        # 如果站点地图文件存在，读取现有URL
        if os.path.exists(sitemap_path):
            try:
                # 解析现有的站点地图
                tree = ET.parse(sitemap_path)
                old_root = tree.getroot()
                
                # 复制现有的URL到新的站点地图
                for url_element in old_root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                    loc_element = url_element.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc_element is not None and loc_element.text:
                        url = loc_element.text
                        
                        # 如果URL已经添加过，跳过
                        if url in added_urls:
                            continue
                        
                        # 复制URL元素到新的站点地图
                        new_url_element = ET.SubElement(root, 'url')
                        
                        # 复制loc元素
                        new_loc = ET.SubElement(new_url_element, 'loc')
                        new_loc.text = url
                        added_urls.add(url)
                        
                        # 复制lastmod元素
                        lastmod_element = url_element.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
                        if lastmod_element is not None and lastmod_element.text:
                            new_lastmod = ET.SubElement(new_url_element, 'lastmod')
                            new_lastmod.text = lastmod_element.text
                        
                        # 复制changefreq元素
                        changefreq_element = url_element.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq')
                        if changefreq_element is not None and changefreq_element.text:
                            new_changefreq = ET.SubElement(new_url_element, 'changefreq')
                            new_changefreq.text = changefreq_element.text
                        
                        # 复制priority元素
                        priority_element = url_element.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}priority')
                        if priority_element is not None and priority_element.text:
                            new_priority = ET.SubElement(new_url_element, 'priority')
                            new_priority.text = priority_element.text
                
                print(f"已从现有站点地图中复制 {len(added_urls)} 个URL")
            except Exception as e:
                print(f"解析现有站点地图时出错: {e}")
        
        # 确保首页URL存在
        if 'https://heartwellness.app' not in added_urls:
            add_url_to_sitemap(root, 'https://heartwellness.app', priority='1.0')
            added_urls.add('https://heartwellness.app')
        
        # 获取数据库中的所有文章
        Article = apps.get_model('note', 'Article')
        articles = Article.objects.all()
        
        # 为每篇文章添加URL（如果尚未添加）
        articles_added = 0
        for article in articles:
            article_url = f"https://heartwellness.app/knowledge/{article.id}"
            if article_url not in added_urls:
                add_url_to_sitemap(
                    root, 
                    article_url, 
                    lastmod=article.updated_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                    priority='0.9'
                )
                added_urls.add(article_url)
                articles_added += 1
        
        print(f"已添加 {articles_added} 篇新文章到站点地图")
        
        # 创建XML树并保存
        tree = ET.ElementTree(root)
        
        # 使用minidom来格式化XML，使其具有正确的缩进和换行
        from xml.dom import minidom
        xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        
        # 写入文件
        with open(sitemap_path, 'w', encoding='UTF-8') as f:
            f.write(xmlstr)
            
        print(f"站点地图已更新，共包含 {len(added_urls)} 个URL")
            
    except Exception as e:
        print(f"更新站点地图时出错: {e}")

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