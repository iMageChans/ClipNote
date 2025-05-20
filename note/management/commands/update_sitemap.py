from django.core.management.base import BaseCommand
import os
from django.conf import settings
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz
from note.models import Article
from note.signals import check_and_update_sitemap

class Command(BaseCommand):
    help = '更新站点地图，添加所有文章的 URL'

    def handle(self, *args, **options):
        # 直接调用 signals.py 中的函数
        check_and_update_sitemap()
        
        self.stdout.write(self.style.SUCCESS('站点地图已更新')) 