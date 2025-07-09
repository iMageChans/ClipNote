from django.core.management.base import BaseCommand
from django.conf import settings
from fitness.models import Exercise
import requests
import time
import urllib.parse
import re


class Command(BaseCommand):
    help = '使用YouTube API为健身动作获取教程视频链接'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制更新已有YouTube链接的动作',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='限制处理的动作数量（用于测试）',
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=1.0,
            help='请求之间的延迟时间（秒），避免超过API配额',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示将要处理的动作，不实际更新数据库',
        )

    def handle(self, *args, **options):
        # 检查API密钥
        api_key = settings.YOUTUBE_API_KEY
        if not api_key:
            self.stdout.write(
                self.style.ERROR('错误: 未设置YouTube API密钥。请设置环境变量 YOUTUBE_API_KEY')
            )
            self.stdout.write('获取API密钥的步骤:')
            self.stdout.write('1. 访问 https://console.developers.google.com/')
            self.stdout.write('2. 创建项目或选择现有项目')
            self.stdout.write('3. 启用 YouTube Data API v3')
            self.stdout.write('4. 创建凭据（API密钥）')
            self.stdout.write('5. 设置环境变量: export YOUTUBE_API_KEY="your_api_key"')
            return

        force = options['force']
        limit = options['limit']
        delay = options['delay']
        dry_run = options['dry_run']

        # 获取需要处理的动作
        if force:
            exercises = Exercise.objects.all()
            self.stdout.write(f'强制模式: 将处理所有 {exercises.count()} 个动作')
        else:
            exercises = Exercise.objects.filter(youtube_url__isnull=True) | Exercise.objects.filter(youtube_url='')
            self.stdout.write(f'将处理 {exercises.count()} 个没有YouTube链接的动作')

        if limit:
            exercises = exercises[:limit]
            self.stdout.write(f'限制处理数量为 {limit} 个动作')

        if dry_run:
            self.stdout.write('\n' + '='*50)
            self.stdout.write('DRY RUN 模式 - 将要处理的动作:')
            for exercise in exercises:
                self.stdout.write(f'  - {exercise.name} (部位: {exercise.body_part.name})')
            self.stdout.write(f'\n总计: {len(exercises)} 个动作')
            return

        success_count = 0
        error_count = 0
        skipped_count = 0
        total = len(exercises)

        for i, exercise in enumerate(exercises, 1):
            self.stdout.write(f'\n[{i}/{total}] 正在处理: {exercise.name}')
            
            try:
                # 搜索YouTube视频
                video_url = self.search_youtube_video(exercise.name, exercise.body_part.name, api_key)
                
                if video_url:
                    # 保存视频链接
                    exercise.youtube_url = video_url
                    exercise.save()
                    success_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ 已保存视频链接: {video_url}')
                    )
                else:
                    skipped_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠ 未找到合适的视频')
                    )
                
                # 延迟以避免超过API配额
                if i < total:  # 最后一个请求后不需要延迟
                    time.sleep(delay)
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'  ✗ 处理失败: {str(e)}')
                )
                # 遇到错误时也需要延迟
                time.sleep(delay)

        # 输出统计信息
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('处理完成!'))
        self.stdout.write(f'成功获取视频: {success_count} 个')
        self.stdout.write(f'未找到视频: {skipped_count} 个')
        self.stdout.write(f'处理失败: {error_count} 个')
        self.stdout.write(f'总计处理: {total} 个')
        
        if total > 0:
            self.stdout.write(f'\n成功率: {(success_count/total)*100:.1f}%')

    def search_youtube_video(self, exercise_name, body_part_name, api_key):
        """
        使用YouTube Data API搜索视频，使用多种搜索策略
        """
        # 清理动作名称
        clean_name = self.clean_exercise_name(exercise_name)
        
        # 多种搜索查询策略
        search_queries = [
            f"{clean_name} tutorial",
            f"{clean_name} exercise",
            f"{clean_name} how to",
            f"{clean_name} {body_part_name} exercise",
            f"{clean_name} workout",
        ]
        
        for query in search_queries:
            self.stdout.write(f'    搜索: "{query}"')
            
            video_url = self.perform_youtube_search(query, api_key)
            if video_url:
                return video_url
            
            # 短暂延迟避免过快请求
            time.sleep(0.5)
        
        return None

    def clean_exercise_name(self, name):
        """
        清理动作名称，使其更适合YouTube搜索
        """
        # 移除括号及其内容
        name = re.sub(r'\([^)]*\)', '', name)
        # 移除常见的前缀/后缀
        name = re.sub(r'^(the\s+|a\s+)', '', name, flags=re.IGNORECASE)
        # 替换连字符为空格
        name = name.replace('-', ' ')
        # 移除多余空格
        name = ' '.join(name.split())
        return name.strip()

    def perform_youtube_search(self, query, api_key):
        """
        执行单次YouTube搜索
        """
        search_url = 'https://www.googleapis.com/youtube/v3/search'
        
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': 3,  # 获取前3个结果
            'order': 'relevance',  # 按相关性排序
            'key': api_key,
            'regionCode': 'US',
            'relevanceLanguage': 'en',
            'videoDuration': 'medium',  # 优先中等长度视频
            'videoDefinition': 'any',
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if 'items' in data and data['items']:
                # 过滤结果，选择最合适的视频
                best_video = self.select_best_video(data['items'], query)
                if best_video:
                    video_id = best_video['id']['videoId']
                    video_url = f'https://www.youtube.com/watch?v={video_id}'
                    video_title = best_video['snippet']['title']
                    
                    self.stdout.write(f'      ✓ 找到: {video_title[:50]}...')
                    return video_url
            
            return None
                
        except requests.exceptions.RequestException as e:
            self.stdout.write(f'      网络请求错误: {str(e)}')
            return None
        except KeyError as e:
            self.stdout.write(f'      API响应格式错误: {str(e)}')
            return None
        except Exception as e:
            self.stdout.write(f'      未知错误: {str(e)}')
            return None

    def select_best_video(self, videos, query):
        """
        从搜索结果中选择最佳视频
        """
        # 评分标准
        for video in videos:
            title = video['snippet']['title'].lower()
            description = video['snippet']['description'].lower()
            
            # 过滤掉不合适的视频
            bad_keywords = ['music', 'song', 'remix', 'playlist', 'compilation']
            if any(keyword in title for keyword in bad_keywords):
                continue
            
            # 优先选择包含 tutorial, exercise, how to 的视频
            good_keywords = ['tutorial', 'exercise', 'how to', 'workout', 'form']
            if any(keyword in title for keyword in good_keywords):
                return video
        
        # 如果没有找到特别好的，返回第一个
        return videos[0] if videos else None 