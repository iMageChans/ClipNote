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
    
    sitemap_path = os.path.join(settings.BASE_DIR, 'sitemap-0.xml')
    
    # 检查站点地图文件是否存在
    if not os.path.exists(sitemap_path):
        # 如果不存在，创建一个基本的站点地图
        create_base_sitemap(sitemap_path)
    
    try:
        # 解析现有的站点地图
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        
        # 检查URL是否已存在
        article_url = f"https://heartwellness.app/knowledge/{instance.id}"
        url_exists = False
        
        for url_element in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
            loc_element = url_element.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
            if loc_element is not None and loc_element.text == article_url:
                url_exists = True
                break
        
        # 如果URL不存在，则添加
        if not url_exists:
            # 创建新的URL元素
            url_element = ET.SubElement(root, 'url')
            
            # 文章的URL格式为 /knowledge/{id}
            loc = ET.SubElement(url_element, 'loc')
            loc.text = article_url
            
            # 添加最后修改时间
            lastmod = ET.SubElement(url_element, 'lastmod')
            lastmod.text = datetime.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            
            # 添加更新频率
            changefreq = ET.SubElement(url_element, 'changefreq')
            changefreq.text = 'daily'
            
            # 添加优先级
            priority = ET.SubElement(url_element, 'priority')
            priority.text = '0.9'
            
            # 保存更新后的站点地图
            tree.write(sitemap_path, encoding='UTF-8', xml_declaration=True)
            print(f"添加文章到站点地图: {article_url}")
        
    except Exception as e:
        print(f"更新站点地图时出错: {e}")

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
    检查数据库中的所有文章，确保它们都在站点地图中，并移除重复项
    """
    sitemap_path = os.path.join(settings.BASE_DIR, 'sitemap-0.xml')
    
    # 如果站点地图不存在，创建一个基本的
    if not os.path.exists(sitemap_path):
        create_base_sitemap(sitemap_path)
        
    try:
        # 解析现有的站点地图
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        
        # 获取站点地图中的所有URL及其元素
        existing_urls = {}
        for url_element in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
            loc_element = url_element.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
            if loc_element is not None and loc_element.text:
                if loc_element.text in existing_urls:
                    # 如果URL已存在，标记为重复
                    existing_urls[loc_element.text].append(url_element)
                else:
                    existing_urls[loc_element.text] = [url_element]
        
        # 移除重复的URL元素
        updated = False
        for url, elements in existing_urls.items():
            if len(elements) > 1:
                # 保留第一个元素，删除其余的
                for element in elements[1:]:
                    root.remove(element)
                updated = True
                print(f"移除重复URL: {url}")
        
        # 获取数据库中的所有文章
        Article = apps.get_model('note', 'Article')
        articles = Article.objects.all()
        
        # 检查每篇文章是否在站点地图中
        for article in articles:
            # 检查两种可能的URL格式
            knowledge_url = f"https://heartwellness.app/knowledge/{article.id}"
            articles_url = f"https://heartwellness.app/articles/{article.id}"
            
            if knowledge_url not in existing_urls and articles_url not in existing_urls:
                # 如果文章不在站点地图中，添加它
                url_element = ET.SubElement(root, 'url')
                
                loc = ET.SubElement(url_element, 'loc')
                loc.text = knowledge_url  # 使用knowledge路径
                
                lastmod = ET.SubElement(url_element, 'lastmod')
                lastmod.text = article.updated_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                
                changefreq = ET.SubElement(url_element, 'changefreq')
                changefreq.text = 'daily'
                
                priority = ET.SubElement(url_element, 'priority')
                priority.text = '0.9'
                
                updated = True
                print(f"添加文章到站点地图: {knowledge_url}")
        
        # 如果有更新，保存站点地图
        if updated:
            tree.write(sitemap_path, encoding='UTF-8', xml_declaration=True)
            print("站点地图已更新")
        else:
            print("站点地图已是最新")
            
    except Exception as e:
        print(f"检查站点地图时出错: {e}") 