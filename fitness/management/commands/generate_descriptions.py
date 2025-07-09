from django.core.management.base import BaseCommand
from django.conf import settings
from fitness.models import Exercise, ContentKeywordMapping
import requests
import time
import re


class Command(BaseCommand):
    help = '使用ChatGPT API为健身动作生成详细描述并提取关键词映射'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制更新已有描述的动作',
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
            default=2.0,
            help='请求之间的延迟时间（秒），避免超过API配额',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示将要处理的动作，不实际更新数据库',
        )
        parser.add_argument(
            '--model',
            type=str,
            default=None,
            help='指定ChatGPT模型 (gpt-3.5-turbo, gpt-4, gpt-4-turbo)',
        )
        parser.add_argument(
            '--extract-keywords',
            action='store_true',
            help='同时提取关键词并创建映射关系',
        )

    def handle(self, *args, **options):
        # 检查API密钥
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            self.stdout.write(
                self.style.ERROR('错误: 未设置OpenAI API密钥。请设置环境变量 OPENAI_API_KEY')
            )
            self.stdout.write('获取API密钥的步骤:')
            self.stdout.write('1. 访问 https://platform.openai.com/api-keys')
            self.stdout.write('2. 登录您的OpenAI账户')
            self.stdout.write('3. 点击 "Create new secret key"')
            self.stdout.write('4. 复制生成的API密钥')
            self.stdout.write('5. 设置环境变量: set OPENAI_API_KEY=your_api_key')
            return

        model = options['model'] or settings.OPENAI_MODEL

        force = options['force']
        limit = options['limit']
        delay = options['delay']
        dry_run = options['dry_run']
        extract_keywords = options['extract_keywords']

        # 获取需要处理的动作
        if force:
            exercises = Exercise.objects.all()
            self.stdout.write(f'强制模式: 将处理所有 {exercises.count()} 个动作')
        else:
            exercises = Exercise.objects.filter(description__isnull=True) | Exercise.objects.filter(description='')
            self.stdout.write(f'将处理 {exercises.count()} 个没有描述的动作')

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

        self.stdout.write(f'使用模型: {model}')
        self.stdout.write(f'请求延迟: {delay} 秒')
        if extract_keywords:
            self.stdout.write('将提取关键词并创建映射关系')

        success_count = 0
        error_count = 0
        skipped_count = 0
        keyword_count = 0
        total = len(exercises)

        for i, exercise in enumerate(exercises, 1):
            self.stdout.write(f'\n[{i}/{total}] 正在处理: {exercise.name}')
            
            try:
                # 生成动作描述
                description = self.generate_exercise_description(exercise.name, model, api_key)
                
                if description:
                    # 保存描述
                    exercise.description = description
                    exercise.ai_generated = True
                    exercise.save()
                    success_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ 已生成并保存描述 ({len(description)} 字符)')
                    )
                    
                    # 显示生成内容的预览
                    preview = description[:100].replace('\n', ' ')
                    self.stdout.write(f'    预览: {preview}...')
                    
                    # 提取关键词并创建映射
                    if extract_keywords:
                        keywords = self.extract_and_save_keywords(exercise, description)
                        if keywords:
                            keyword_count += len(keywords)
                            self.stdout.write(f'    提取关键词: {len(keywords)} 个')
                            self.stdout.write(f'    关键词: {", ".join(keywords[:5])}...')
                        
                else:
                    skipped_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠ 生成描述失败')
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
        self.stdout.write(f'成功生成描述: {success_count} 个')
        self.stdout.write(f'生成失败: {skipped_count} 个')
        self.stdout.write(f'处理错误: {error_count} 个')
        self.stdout.write(f'总计处理: {total} 个')
        
        if extract_keywords and keyword_count > 0:
            self.stdout.write(f'提取关键词: {keyword_count} 个')
        
        if total > 0:
            self.stdout.write(f'\n成功率: {(success_count/total)*100:.1f}%')

    def generate_exercise_description(self, exercise_name, model, api_key):
        """
        使用requests直接调用OpenAI API生成健身动作描述
        """
        # 构建提示词
        prompt = f"""Generate {exercise_name} content, including:
- What is {exercise_name}?
- {exercise_name} Tutorial
- Common Mistakes
- Tips for Better Results
- Muscles Worked
Generate content directly, do not reply with other useless information."""

        try:
            self.stdout.write(f'    正在调用ChatGPT API...')
            
            # 直接使用requests调用OpenAI API
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': model,
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a professional fitness trainer and expert. Generate comprehensive, accurate, and practical fitness exercise descriptions in markdown format. Use proper markdown headers (##), lists, and emphasis. Structure the content with clear sections: What is [exercise]?, Tutorial, Common Mistakes, Tips for Better Results, and Muscles Worked.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 2000,
                'temperature': 0.7,
                'top_p': 1.0,
                'frequency_penalty': 0.0,
                'presence_penalty': 0.0
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'choices' in result and result['choices']:
                    content = result['choices'][0]['message']['content'].strip()
                    
                    # 清理和格式化内容
                    content = self.clean_and_format_content(content, exercise_name)
                    
                    # 记录使用的tokens
                    if 'usage' in result:
                        tokens_used = result['usage']['total_tokens']
                        self.stdout.write(f'    使用tokens: {tokens_used}')
                    
                    return content
                else:
                    self.stdout.write(f'    API响应格式错误')
                    return None
            else:
                error_info = response.json() if response.content else {}
                if response.status_code == 401:
                    self.stdout.write(f'    API密钥无效或已过期')
                elif response.status_code == 429:
                    self.stdout.write(f'    API配额限制，建议增加延迟时间')
                else:
                    self.stdout.write(f'    API错误 {response.status_code}: {error_info}')
                return None
                
        except requests.exceptions.Timeout:
            self.stdout.write(f'    请求超时，建议检查网络连接')
            return None
        except requests.exceptions.RequestException as e:
            self.stdout.write(f'    网络错误: {str(e)}')
            return None
        except Exception as e:
            self.stdout.write(f'    未知错误: {str(e)}')
            return None

    def clean_and_format_content(self, content, exercise_name):
        """
        清理和格式化生成的内容
        """
        # 移除可能的多余空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 确保标题格式正确（保持二级标题）
        content = re.sub(r'^#{1,6}\s*(.+)$', r'## \1', content, flags=re.MULTILINE)
        
        # 如果内容没有主标题，添加一个
        if not content.startswith('#'):
            content = f"# {exercise_name.title()}\n\n{content}"
        
        # 确保列表格式正确
        content = re.sub(r'^\s*[-•]\s*', '- ', content, flags=re.MULTILINE)
        content = re.sub(r'^\s*\d+\.\s*', lambda m: f"{m.group().strip()} ", content, flags=re.MULTILINE)
        
        # 移除开头和结尾的引号或其他包装符号
        content = content.strip('"\'`')
        
        return content.strip()

    def extract_and_save_keywords(self, exercise, description):
        """
        从生成的描述中提取关键词并保存映射关系
        """
        try:
            # 提取markdown标题作为关键词
            headers = re.findall(r'^##\s*(.+)$', description, re.MULTILINE)
            
            # 分析不同类型的内容
            content_mapping = {
                'what_is': ['what is', 'definition', 'about'],
                'tutorial': ['tutorial', 'how to', 'steps', 'technique', 'form'],
                'mistakes': ['mistakes', 'errors', 'avoid', 'common'],
                'tips': ['tips', 'better', 'improve', 'advice'],
                'muscles': ['muscles', 'worked', 'target', 'primary', 'secondary']
            }
            
            keywords = []
            
            # 清除现有的关键词映射
            ContentKeywordMapping.objects.filter(exercise=exercise).delete()
            
            for header in headers:
                clean_header = re.sub(r'[#*_`]', '', header).strip().lower()
                
                # 确定内容类型
                content_type = 'other'
                for type_key, type_keywords in content_mapping.items():
                    if any(keyword in clean_header for keyword in type_keywords):
                        content_type = type_key
                        break
                
                # 创建关键词映射
                if clean_header and len(clean_header) > 2:
                    ContentKeywordMapping.objects.create(
                        exercise=exercise,
                        keyword=clean_header,
                        content_type=content_type,
                        relevance_score=1.0
                    )
                    keywords.append(clean_header)
            
            # 添加基础关键词
            base_keywords = [
                (exercise.name.lower(), 'other'),
                (exercise.body_part.name.lower() if exercise.body_part else '', 'muscles'),
                ('exercise', 'other'),
                ('workout', 'other'),
                ('fitness', 'other'),
                ('training', 'other')
            ]
            
            for keyword, content_type in base_keywords:
                if keyword and keyword not in keywords:
                    ContentKeywordMapping.objects.get_or_create(
                        exercise=exercise,
                        keyword=keyword,
                        content_type=content_type,
                        defaults={'relevance_score': 0.8}
                    )
                    keywords.append(keyword)
            
            # 保存关键词到Exercise模型
            exercise.set_generated_keywords(keywords)
            exercise.save()
            
            return keywords
            
        except Exception as e:
            self.stdout.write(f'    关键词提取失败: {str(e)}')
            return []
