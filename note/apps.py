from django.apps import AppConfig
import os
import sys


class NoteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'note'
    
    def ready(self):
        import note.signals  # 导入信号模块
        
        # 只在主进程中运行一次
        # 检查是否是通过命令行运行的，而不是由自动重载器运行的
        if 'runserver' in sys.argv:
            # 使用环境变量来防止在自动重载时重复执行
            if os.environ.get('RUN_MAIN') != 'true':
                print("正在检查并更新站点地图...")
                from note.signals import check_and_update_sitemap
                check_and_update_sitemap()
