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

    def add_arguments(self, parser):
        parser.add_argument(
            '--rebuild',
            action='store_true',
            help='完全重建站点地图，而不是增量更新',
        )

    def handle(self, *args, **options):
        # 获取rebuild参数
        rebuild = options.get('rebuild', False)
        
        # 调用signals.py中的函数
        check_and_update_sitemap(rebuild=rebuild)
        
        if rebuild:
            self.stdout.write(self.style.SUCCESS('站点地图已完全重建'))
        else:
            self.stdout.write(self.style.SUCCESS('站点地图已增量更新')) 