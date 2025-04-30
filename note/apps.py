from django.apps import AppConfig


class NoteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'note'
    
    def ready(self):
        import note.signals  # 导入信号模块
        
        # 只在主进程中运行一次
        import os
        if os.environ.get('RUN_MAIN', None) != 'true':
            # 在应用启动时检查站点地图
            from note.signals import check_and_update_sitemap
            check_and_update_sitemap()
