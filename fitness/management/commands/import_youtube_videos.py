from django.core.management.base import BaseCommand
from django.conf import settings
from fitness.models import Exercise
import requests
import time
import urllib.parse
import re
import json
import os
from datetime import datetime, date


class Command(BaseCommand):
    help = '使用YouTube API为健身动作获取教程视频链接，支持配额管理和断点续传'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.progress_file = 'youtube_import_progress.json'
        self.quota_used_today = 0
        self.max_daily_quota = 9000  # 保留1000配额作为缓冲
        self.quota_per_search = 100  # 每次搜索消耗的配额

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
        parser.add_argument(
            '--reset-progress',
            action='store_true',
            help='重置进度，从头开始处理',
        )
        parser.add_argument(
            '--show-progress',
            action='store_true',
            help='显示当前进度信息',
        )
        parser.add_argument(
            '--max-quota',
            type=int,
            default=9000,
            help='每日最大配额限制（默认9000，保留1000作为缓冲）',
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

        self.max_daily_quota = options['max_quota']
        
        # 处理特殊命令
        if options['show_progress']:
            self.show_progress_info()
            return
            
        if options['reset_progress']:
            self.reset_progress()
            self.stdout.write(self.style.SUCCESS('进度已重置'))
            return

        force = options['force']
        limit = options['limit']
        delay = options['delay']
        dry_run = options['dry_run']

        # 加载进度
        progress = self.load_progress()
        self.quota_used_today = progress.get('quota_used_today', 0)
        
        # 检查是否是新的一天
        today = str(date.today())
        if progress.get('last_date') != today:
            self.stdout.write(f'检测到新的一天 ({today})，重置配额计数')
            self.quota_used_today = 0
            progress['last_date'] = today
            progress['quota_used_today'] = 0
            self.save_progress(progress)

        # 检查配额状态
        remaining_quota = self.max_daily_quota - self.quota_used_today
        if remaining_quota <= 0:
            self.stdout.write(
                self.style.ERROR(f'今日配额已用完 ({self.quota_used_today}/{self.max_daily_quota})，请明天继续')
            )
            return

        self.stdout.write(f'今日剩余配额: {remaining_quota} (已用: {self.quota_used_today})')

        # 获取需要处理的动作
        processed_ids = set(progress.get('processed_ids', []))
        
        if force:
            exercises = Exercise.objects.all()
            self.stdout.write(f'强制模式: 将处理所有 {exercises.count()} 个动作')
        else:
            exercises = Exercise.objects.filter(youtube_url__isnull=True) | Exercise.objects.filter(youtube_url='')
            self.stdout.write(f'将处理 {exercises.count()} 个没有YouTube链接的动作')

        # 过滤掉已处理的动作（断点续传）
        if not force and processed_ids:
            unprocessed_exercises = [ex for ex in exercises if ex.id not in processed_ids]
            self.stdout.write(f'发现之前的进度，跳过已处理的 {len(exercises) - len(unprocessed_exercises)} 个动作')
            exercises = unprocessed_exercises
        else:
            exercises = list(exercises)

        if limit:
            exercises = exercises[:limit]
            self.stdout.write(f'限制处理数量为 {limit} 个动作')

        if dry_run:
            self.stdout.write('\n' + '='*50)
            self.stdout.write('DRY RUN 模式 - 将要处理的动作:')
            estimated_quota = len(exercises) * 5 * self.quota_per_search  # 估算每个动作最多5次搜索
            for exercise in exercises:
                status = "已处理" if exercise.id in processed_ids else "待处理"
                self.stdout.write(f'  - {exercise.name} (部位: {exercise.body_part.name}) [{status}]')
            self.stdout.write(f'\n总计: {len(exercises)} 个动作')
            self.stdout.write(f'估算配额需求: {estimated_quota} (当前剩余: {remaining_quota})')
            return

        success_count = progress.get('success_count', 0)
        error_count = progress.get('error_count', 0)
        skipped_count = progress.get('skipped_count', 0)
        total = len(exercises)

        self.stdout.write(f'\n使用模型: YouTube Data API v3')
        self.stdout.write(f'请求延迟: {delay} 秒')
        self.stdout.write(f'最大配额限制: {self.max_daily_quota}')

        for i, exercise in enumerate(exercises, 1):
            # 检查配额是否足够
            if self.quota_used_today >= self.max_daily_quota:
                self.stdout.write(
                    self.style.WARNING(f'\n⚠️  配额已达到每日限制 ({self.max_daily_quota})，停止处理')
                )
                self.stdout.write('明天继续时会从当前位置恢复处理')
                break

            self.stdout.write(f'\n[{i}/{total}] 正在处理: {exercise.slug}')
            self.stdout.write(f'    剩余配额: {self.max_daily_quota - self.quota_used_today}')
            
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
                
                # 记录已处理的动作ID
                processed_ids.add(exercise.id)
                
                # 保存进度
                progress.update({
                    'processed_ids': list(processed_ids),
                    'success_count': success_count,
                    'error_count': error_count,
                    'skipped_count': skipped_count,
                    'quota_used_today': self.quota_used_today,
                    'last_processed': exercise.slug,
                    'last_updated': datetime.now().isoformat()
                })
                self.save_progress(progress)
                
                # 延迟以避免超过API配额
                if i < total:  # 最后一个请求后不需要延迟
                    time.sleep(delay)
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'  ✗ 处理失败: {str(e)}')
                )
                # 即使出错也要记录，避免重复处理
                processed_ids.add(exercise.id)
                
                # 保存进度
                progress.update({
                    'processed_ids': list(processed_ids),
                    'error_count': error_count,
                    'quota_used_today': self.quota_used_today,
                    'last_updated': datetime.now().isoformat()
                })
                self.save_progress(progress)
                
                # 遇到错误时也需要延迟
                time.sleep(delay)

        # 输出统计信息
        self.stdout.write('\n' + '='*60)
        
        if self.quota_used_today >= self.max_daily_quota:
            self.stdout.write(self.style.WARNING('因配额限制而暂停处理!'))
        else:
            self.stdout.write(self.style.SUCCESS('处理完成!'))
            
        self.stdout.write(f'成功获取视频: {success_count} 个')
        self.stdout.write(f'未找到视频: {skipped_count} 个')
        self.stdout.write(f'处理失败: {error_count} 个')
        self.stdout.write(f'本次处理: {len(exercises)} 个')
        self.stdout.write(f'今日使用配额: {self.quota_used_today}/{self.max_daily_quota}')
        
        total_processed = len(processed_ids)
        if total_processed > 0:
            success_rate = (success_count / total_processed) * 100
            self.stdout.write(f'总体成功率: {success_rate:.1f}%')

        # 检查是否还有未处理的动作
        remaining_exercises = Exercise.objects.exclude(id__in=processed_ids).filter(
            youtube_url__isnull=True
        ).count() + Exercise.objects.exclude(id__in=processed_ids).filter(
            youtube_url=''
        ).count()
        
        if remaining_exercises > 0:
            self.stdout.write(f'\n还有 {remaining_exercises} 个动作待处理')
            if self.quota_used_today >= self.max_daily_quota:
                self.stdout.write('明天运行时会自动继续处理剩余动作')
            else:
                self.stdout.write('可以再次运行命令继续处理')

    def search_youtube_video(self, exercise_name, body_part_name, api_key):
        """
        使用YouTube Data API搜索视频，使用多种搜索策略
        """
        # 清理动作名称
        clean_name = self.clean_exercise_name(exercise_name)
        
        # 多种搜索查询策略
        search_queries = [
            f"{clean_name} tutorial",
            f"how to {clean_name}",
            f"{clean_name} exercise",
            f"{clean_name} workout",
        ]
        
        for query in search_queries:
            # 检查配额
            if self.quota_used_today + self.quota_per_search > self.max_daily_quota:
                self.stdout.write('    配额即将用完，停止搜索')
                return None
                
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
            
            # 更新配额使用量
            self.quota_used_today += self.quota_per_search
            
            # 检查是否触发配额限制
            if response.status_code == 403:
                error_data = response.json()
                if 'quotaExceeded' in str(error_data):
                    self.stdout.write('      API配额限制，建议增加延迟时间')
                    return None
            
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
            if 'timeout' in str(e).lower():
                self.stdout.write('      请求超时，建议检查网络连接')
            else:
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

    def load_progress(self):
        """加载进度文件"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                self.stdout.write(self.style.WARNING('进度文件损坏，将重新开始'))
                return self.get_default_progress()
        return self.get_default_progress()

    def save_progress(self, progress):
        """保存进度到文件"""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)
        except IOError as e:
            self.stdout.write(self.style.ERROR(f'保存进度失败: {str(e)}'))

    def get_default_progress(self):
        """获取默认进度结构"""
        return {
            'processed_ids': [],
            'success_count': 0,
            'error_count': 0,
            'skipped_count': 0,
            'quota_used_today': 0,
            'last_date': str(date.today()),
            'last_processed': None,
            'last_updated': datetime.now().isoformat()
        }

    def reset_progress(self):
        """重置进度"""
        if os.path.exists(self.progress_file):
            os.remove(self.progress_file)

    def show_progress_info(self):
        """显示当前进度信息"""
        progress = self.load_progress()
        
        self.stdout.write('='*50)
        self.stdout.write('YouTube导入进度信息')
        self.stdout.write('='*50)
        
        last_date = progress.get('last_date', '无')
        today = str(date.today())
        
        self.stdout.write(f'最后处理日期: {last_date}')
        self.stdout.write(f'今天日期: {today}')
        
        if last_date == today:
            quota_used = progress.get('quota_used_today', 0)
            remaining = self.max_daily_quota - quota_used
            self.stdout.write(f'今日配额使用: {quota_used}/{self.max_daily_quota} (剩余: {remaining})')
        else:
            self.stdout.write('配额已重置（新的一天）')
        
        processed_count = len(progress.get('processed_ids', []))
        success_count = progress.get('success_count', 0)
        error_count = progress.get('error_count', 0)
        skipped_count = progress.get('skipped_count', 0)
        
        self.stdout.write(f'已处理动作: {processed_count} 个')
        self.stdout.write(f'  - 成功: {success_count} 个')
        self.stdout.write(f'  - 失败: {error_count} 个')
        self.stdout.write(f'  - 跳过: {skipped_count} 个')
        
        last_processed = progress.get('last_processed')
        if last_processed:
            self.stdout.write(f'最后处理: {last_processed}')
        
        last_updated = progress.get('last_updated')
        if last_updated:
            self.stdout.write(f'最后更新: {last_updated}')
            
        # 计算剩余动作
        total_exercises = Exercise.objects.filter(
            youtube_url__isnull=True
        ).count() + Exercise.objects.filter(youtube_url='').count()
        
        remaining_exercises = total_exercises - processed_count
        if remaining_exercises > 0:
            self.stdout.write(f'剩余待处理: {remaining_exercises} 个动作')
            estimated_quota = remaining_exercises * 4 * self.quota_per_search
            estimated_days = estimated_quota / self.max_daily_quota
            self.stdout.write(f'估算需要配额: {estimated_quota}')
            self.stdout.write(f'估算需要天数: {estimated_days:.1f} 天')
        else:
            self.stdout.write('所有动作已处理完成') 