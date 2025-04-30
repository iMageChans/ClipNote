from django.core.management.base import BaseCommand
from note.signals import check_and_update_sitemap

class Command(BaseCommand):
    help = '检查并更新站点地图'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始检查并更新站点地图...'))
        check_and_update_sitemap()
        self.stdout.write(self.style.SUCCESS('站点地图检查和更新完成')) 