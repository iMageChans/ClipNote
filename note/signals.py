from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Article
import os
from django.conf import settings
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz

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
        
        # 创建新的URL元素
        url_element = ET.SubElement(root, 'url')
        
        # 文章的URL格式为 /knowledge/{id} 或 /articles/{id}，根据实际情况调整
        loc = ET.SubElement(url_element, 'loc')
        loc.text = f"https://heartwellness.app/articles/{instance.id}/"
        
        # 添加最后修改时间
        lastmod = ET.SubElement(url_element, 'lastmod')
        lastmod.text = datetime.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        # 添加更新频率
        changefreq = ET.SubElement(url_element, 'changefreq')
        changefreq.text = 'daily'
        
        # 添加优先级
        priority = ET.SubElement(url_element, 'priority')
        priority.text = '0.7'
        
        # 保存更新后的站点地图
        tree.write(sitemap_path, encoding='UTF-8', xml_declaration=True)
        
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