# Fitness应用管理命令操作手册

本手册详细介绍了fitness应用中所有可用的Django管理命令，包括使用方法、参数说明和实际操作示例。

## 📋 命令概览

fitness应用提供以下管理命令：

1. **import_exercises** - 导入健身动作数据
2. **import_youtube_videos** - 为健身动作获取YouTube视频链接
3. **generate_descriptions** - 使用AI生成健身动作详细描述

---

## 🏋️ 1. import_exercises

### 功能描述
从数据文件导入健身动作和身体部位数据，支持自动去重和slug生成。

### 基本语法
```bash
python manage.py import_exercises [options]
```

### 命令选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--file` | string | `fitness/exercises` | 指定要导入的数据文件路径 |
| `--dry-run` | flag | False | 预览模式，不实际导入数据 |
| `--clear` | flag | False | 导入前清空现有数据 |

### 数据文件格式
数据文件应为纯文本格式，每行一个动作，格式：
```
动作名称, 身体部位
```

示例：
```
bench press, chest
squat, legs
deadlift, back
bicep curl, arms
```

### 使用示例

#### 1. 预览导入（推荐先运行）
```bash
python manage.py import_exercises --dry-run
```

#### 2. 从默认文件导入
```bash
python manage.py import_exercises
```

#### 3. 从自定义文件导入
```bash
python manage.py import_exercises --file path/to/your/exercises.txt
```

#### 4. 清空现有数据后重新导入
```bash
python manage.py import_exercises --clear
```

### 导入过程
1. **数据解析**: 读取文件并解析每行数据
2. **去重处理**: 自动移除重复的动作名称
3. **创建身体部位**: 自动创建不存在的身体部位
4. **生成Slug**: 为动作和部位自动生成URL友好的slug
5. **冲突处理**: 对重复slug自动添加数字后缀

### 输出示例
```
正在导入健身动作数据...
文件: fitness/exercises
总行数: 899

正在处理数据...
发现重复动作: 15 个
已移除重复项，剩余: 884 个唯一动作

创建身体部位: abdominals
创建身体部位: abductors
...

导入动作: bench-press (chest)
导入动作: squat (legs)
...

===============================
导入完成!
创建身体部位: 23 个
导入健身动作: 867 个
处理重复项: 17 个
总计处理: 899 行

成功率: 96.4%
```

---

## 🎥 2. import_youtube_videos

### 功能描述
使用YouTube Data API v3自动为健身动作搜索并获取教程视频链接，支持配额管理和断点续传功能。

### 前置要求
- 获取YouTube Data API密钥
- 设置环境变量 `YOUTUBE_API_KEY`

### 基本语法
```bash
python manage.py import_youtube_videos [options]
```

### 命令选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--force` | flag | False | 强制更新已有YouTube链接的动作 |
| `--limit` | int | None | 限制处理的动作数量（用于测试） |
| `--delay` | float | 1.0 | 请求之间的延迟时间（秒） |
| `--dry-run` | flag | False | 预览模式，不实际更新数据库 |
| `--reset-progress` | flag | False | 重置进度，从头开始处理 |
| `--show-progress` | flag | False | 显示当前进度信息 |
| `--max-quota` | int | 9000 | 每日最大配额限制（保留1000作为缓冲） |

### API密钥设置

#### 获取API密钥
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目并启用YouTube Data API v3
3. 创建API密钥

#### 设置环境变量
```bash
# Windows PowerShell
$env:YOUTUBE_API_KEY="your_api_key_here"

# Windows CMD
set YOUTUBE_API_KEY=your_api_key_here

# Linux/macOS
export YOUTUBE_API_KEY="your_api_key_here"
```

### 使用示例

#### 1. 预览模式（推荐先运行）
```bash
python manage.py import_youtube_videos --dry-run --limit 5
```

#### 2. 测试少量数据
```bash
python manage.py import_youtube_videos --limit 10 --delay 2
```

#### 3. 处理所有动作
```bash
python manage.py import_youtube_videos --delay 2
```

#### 4. 强制更新已有链接
```bash
python manage.py import_youtube_videos --force --delay 2
```

#### 5. 查看当前进度
```bash
python manage.py import_youtube_videos --show-progress
```

#### 6. 重置进度重新开始
```bash
python manage.py import_youtube_videos --reset-progress
```

#### 7. 设置自定义配额限制
```bash
python manage.py import_youtube_videos --max-quota 8000 --delay 2
```

### 🔄 配额管理与断点续传

#### 配额管理功能
- **每日配额限制**: 默认9000配额/天（保留1000作为缓冲）
- **自动配额跟踪**: 实时监控配额使用情况
- **智能停止**: 配额用完时自动停止处理
- **每日重置**: 检测到新的一天时自动重置配额计数

#### 断点续传功能
- **进度保存**: 自动保存处理进度到本地文件
- **智能恢复**: 重新运行时自动跳过已处理的动作
- **错误容忍**: 处理失败的动作会被标记，避免重复处理

#### 进度文件
系统会在项目根目录创建 `youtube_import_progress.json` 文件保存进度信息：
```json
{
  "processed_ids": [1, 2, 3, ...],
  "success_count": 150,
  "error_count": 5,
  "skipped_count": 10,
  "quota_used_today": 8500,
  "last_date": "2024-01-15",
  "last_processed": "bench-press",
  "last_updated": "2024-01-15T14:30:00"
}
```

### 搜索策略
系统使用多种搜索关键词组合：
- `"{动作名称} tutorial"`
- `"how to {动作名称}"`
- `"{动作名称} exercise"`
- `"{动作名称} workout"`

### 视频过滤规则
- 视频时长 > 30秒
- 排除音乐相关内容
- 优先选择教程类视频
- 过滤无关内容

### 输出示例

#### 正常处理输出
```
今日剩余配额: 8500 (已用: 1500)
发现之前的进度，跳过已处理的 15 个动作
将处理 849 个没有YouTube链接的动作

使用模型: YouTube Data API v3
请求延迟: 2.0 秒
最大配额限制: 9000

[1/849] 正在处理: bench-press
    剩余配额: 8400
    搜索: "bench press tutorial"
      ✓ 找到: How to Bench Press for Beginners | Proper Form...
  ✓ 已保存视频链接: https://www.youtube.com/watch?v=xxxxx

[2/849] 正在处理: squat
    剩余配额: 8300
    搜索: "squat tutorial"
      ✓ 找到: Perfect Squat Form Tutorial...
  ✓ 已保存视频链接: https://www.youtube.com/watch?v=yyyyy

============================================================
处理完成!
成功获取视频: 820 个
未找到视频: 35 个
处理失败: 9 个
本次处理: 849 个
今日使用配额: 8900/9000
总体成功率: 94.9%

还有 27 个动作待处理
可以再次运行命令继续处理
```

#### 配额用完时的输出
```
今日剩余配额: 200 (已用: 8800)
将处理 150 个没有YouTube链接的动作

[1/150] 正在处理: push-up
    剩余配额: 100
    搜索: "push up tutorial"
      ✓ 找到: Perfect Push Up Form Tutorial...
  ✓ 已保存视频链接: https://www.youtube.com/watch?v=zzzzz

⚠️  配额已达到每日限制 (9000)，停止处理
明天继续时会从当前位置恢复处理

============================================================
因配额限制而暂停处理!
成功获取视频: 1 个
未找到视频: 0 个
处理失败: 0 个
本次处理: 1 个
今日使用配额: 9000/9000
总体成功率: 100.0%

还有 149 个动作待处理
明天运行时会自动继续处理剩余动作
```

#### 进度查看输出
```bash
python manage.py import_youtube_videos --show-progress
```
```
==================================================
YouTube导入进度信息
==================================================
最后处理日期: 2024-01-15
今天日期: 2024-01-15
今日配额使用: 8500/9000 (剩余: 500)
已处理动作: 820 个
  - 成功: 780 个
  - 失败: 15 个
  - 跳过: 25 个
最后处理: deadlift
最后更新: 2024-01-15T14:30:00
剩余待处理: 47 个动作
估算需要配额: 1880
估算需要天数: 0.2 天
```

### API配额管理

#### 配额信息
- **每日免费配额**: 10,000单位
- **搜索操作消耗**: 100单位/次
- **系统默认限制**: 9,000单位/天（保留1,000作为缓冲）
- **建议延迟**: 1-2秒避免过快请求

#### 配额监控
- 实时显示剩余配额
- 自动计算处理能力
- 智能预估完成时间
- 配额用完时自动暂停

#### 最佳实践
1. **首次运行**: 使用`--dry-run`预估配额需求
2. **分批处理**: 设置合理的`--limit`参数
3. **监控进度**: 定期运行`--show-progress`查看状态
4. **配额保护**: 使用`--max-quota`设置安全阈值

---

## 🤖 3. generate_descriptions

### 功能描述
使用OpenAI ChatGPT API为健身动作生成详细的markdown格式描述，包括关键词提取和映射。

### 前置要求
- 获取OpenAI API密钥
- 设置环境变量 `OPENAI_API_KEY`

### 基本语法
```bash
python manage.py generate_descriptions [options]
```

### 命令选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--force` | flag | False | 强制更新已有描述的动作 |
| `--limit` | int | None | 限制处理的动作数量（用于测试） |
| `--delay` | float | 2.0 | 请求之间的延迟时间（秒） |
| `--dry-run` | flag | False | 预览模式，不实际更新数据库 |
| `--model` | string | gpt-3.5-turbo | 指定ChatGPT模型 |
| `--extract-keywords` | flag | False | 同时提取关键词并创建映射关系 |

### API密钥设置

#### 获取API密钥
1. 访问 [OpenAI API Keys](https://platform.openai.com/api-keys)
2. 登录并创建新的API密钥
3. 复制生成的密钥（以sk-开头）

#### 设置环境变量
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-your_api_key_here"
$env:OPENAI_MODEL="gpt-3.5-turbo"  # 可选

# Windows CMD
set OPENAI_API_KEY=sk-your_api_key_here

# Linux/macOS
export OPENAI_API_KEY="sk-your_api_key_here"
```

### 支持的模型
- `gpt-3.5-turbo` - 快速且经济（推荐）
- `gpt-4` - 更高质量但更昂贵
- `gpt-4-turbo` - 平衡质量和速度

### 生成内容结构
生成的markdown内容包含以下部分：
```markdown
# 动作名称

## What is 动作名称?
动作介绍和定义

## 动作名称 Tutorial
详细操作步骤

## Common Mistakes
常见错误列表

## Tips for Better Results
改进建议和技巧

## Muscles Worked
目标肌肉群描述
```

### 使用示例

#### 1. 预览模式（推荐先运行）
```bash
python manage.py generate_descriptions --dry-run --limit 3
```

#### 2. 生成少量内容测试
```bash
python manage.py generate_descriptions --force --limit 5 --delay 3 --extract-keywords
```

#### 3. 生成所有缺失描述
```bash
python manage.py generate_descriptions --extract-keywords --delay 2
```

#### 4. 强制重新生成所有描述
```bash
python manage.py generate_descriptions --force --extract-keywords --delay 2
```

#### 5. 使用GPT-4模型
```bash
python manage.py generate_descriptions --model gpt-4 --limit 10 --delay 3
```

### 关键词提取功能
使用 `--extract-keywords` 选项时，系统会：

1. **提取标题关键词**: 从markdown标题中提取关键词
2. **内容分类**: 自动将内容分为以下类型：
   - `what_is`: 介绍性内容
   - `tutorial`: 教程步骤
   - `mistakes`: 常见错误
   - `tips`: 改进建议
   - `muscles`: 肌肉群信息
   - `other`: 其他内容

3. **映射关系**: 创建关键词与内容类型的映射关系
4. **相关性评分**: 为每个关键词分配0.0-1.0的相关性评分

### 输出示例
```bash
强制模式: 将处理所有 867 个动作
限制处理数量为 5 个动作
使用模型: gpt-3.5-turbo
请求延迟: 3.0 秒
将提取关键词并创建映射关系

[1/5] 正在处理: bench-press
    正在调用ChatGPT API...
    使用tokens: 1847
  ✓ 已生成并保存描述 (1654 字符)
    预览: # Bench Press\n\n## What is Bench Press?\nThe bench press is a fundamental upper body strength exercise...
    提取关键词: 12 个
    关键词: what is bench press, tutorial, common mistakes, tips, muscles worked...

[2/5] 正在处理: squat
    正在调用ChatGPT API...
    使用tokens: 1923
  ✓ 已生成并保存描述 (1789 字符)
    预览: # Squat\n\n## What is Squat?\nThe squat is a compound exercise that targets multiple muscle...
    提取关键词: 14 个
    关键词: what is squat, squat tutorial, common mistakes, tips for better results...

============================================================
处理完成!
成功生成描述: 5 个
生成失败: 0 个
处理错误: 0 个
总计处理: 5 个
提取关键词: 68 个

成功率: 100.0%
```

### 成本估算

#### Token使用量
每个动作描述约使用1500-2000 tokens

#### 成本预估（参考价格）
- **GPT-3.5-Turbo**: ~$0.003-0.004/动作
- **GPT-4**: ~$0.045-0.06/动作
- **GPT-4-Turbo**: ~$0.015-0.02/动作

对于867个动作的总成本：
- **GPT-3.5-Turbo**: 约$2.6-3.5
- **GPT-4**: 约$39-52
- **GPT-4-Turbo**: 约$13-17

---

## 🔄 命令组合使用

### 完整数据初始化流程
```bash
# 1. 导入基础动作数据
python manage.py import_exercises --dry-run  # 预览
python manage.py import_exercises             # 实际导入

# 2. 获取YouTube视频（可选）
python manage.py import_youtube_videos --dry-run --limit 5  # 预览
python manage.py import_youtube_videos --show-progress      # 查看进度
python manage.py import_youtube_videos --delay 2           # 开始处理（支持断点续传）

# 3. 生成AI描述
python manage.py generate_descriptions --dry-run --limit 3  # 预览
python manage.py generate_descriptions --limit 10 --extract-keywords --delay 3  # 测试
python manage.py generate_descriptions --extract-keywords --delay 2  # 批量生成
```

### 数据更新维护
```bash
# 查看YouTube导入进度
python manage.py import_youtube_videos --show-progress

# 继续未完成的YouTube导入
python manage.py import_youtube_videos --delay 2

# 强制重新处理所有YouTube链接
python manage.py import_youtube_videos --reset-progress --force --delay 2

# 重新生成所有描述
python manage.py generate_descriptions --force --extract-keywords --delay 2

# 仅更新缺失的数据
python manage.py import_youtube_videos
python manage.py generate_descriptions --extract-keywords
```

---

## 📊 数据状态检查

### 检查导入状态
```bash
python manage.py shell -c "
from fitness.models import Exercise, BodyPart
print(f'身体部位: {BodyPart.objects.count()}')
print(f'健身动作: {Exercise.objects.count()}')
"
```

### 检查YouTube链接状态
```bash
# 使用Django shell检查
python manage.py shell -c "
from fitness.models import Exercise
total = Exercise.objects.count()
with_youtube = Exercise.objects.exclude(youtube_url='').count()
print(f'总动作: {total}')
print(f'有YouTube链接: {with_youtube}')
print(f'缺失YouTube链接: {total - with_youtube}')
"

# 或使用命令直接查看进度
python manage.py import_youtube_videos --show-progress
```

### 检查AI生成状态
```bash
python manage.py shell -c "
from fitness.models import Exercise
total = Exercise.objects.count()
ai_generated = Exercise.objects.filter(ai_generated=True).count()
print(f'总动作: {total}')
print(f'AI生成描述: {ai_generated}')
print(f'需要生成描述: {total - ai_generated}')
"
```

### 检查关键词映射
```bash
python manage.py shell -c "
from fitness.models import ContentKeywordMapping
mappings = ContentKeywordMapping.objects.count()
types = ContentKeywordMapping.objects.values('content_type').distinct().count()
print(f'关键词映射总数: {mappings}')
print(f'内容类型数量: {types}')
"
```

---

## ⚠️ 故障排除

### 常见错误及解决方案

#### 1. API密钥错误
```
错误: 未设置OpenAI API密钥
解决: 设置环境变量 OPENAI_API_KEY
```

#### 2. 网络连接问题
```
错误: 请求超时，建议检查网络连接
解决: 检查网络连接，增加延迟时间
```

#### 3. API配额限制
```
错误: API配额限制，建议增加延迟时间
解决: 
1. 等待明天配额重置
2. 使用 --show-progress 查看配额使用情况
3. 增加 --delay 参数值
4. 使用 --max-quota 设置更保守的限制
```

#### 4. 文件路径错误
```
错误: 找不到文件 'fitness/exercises'
解决: 检查文件路径，使用 --file 指定正确路径
```

#### 5. 数据库冲突
```
错误: UNIQUE constraint failed
解决: 使用 --clear 选项清空现有数据，或检查重复数据
```

#### 6. 进度文件损坏
```
错误: 进度文件损坏，将重新开始
解决: 
1. 使用 --reset-progress 重置进度
2. 手动删除 youtube_import_progress.json 文件
3. 重新运行命令
```

#### 7. 意外中断处理
```
解决: 重新运行相同命令即可自动恢复进度
注意: 系统会自动跳过已处理的动作
```

### 调试技巧

#### 1. 使用详细输出
```bash
python manage.py command_name -v 2
```

#### 2. 分批处理大量数据
```bash
python manage.py command_name --limit 50
```

#### 3. 增加延迟避免限制
```bash
python manage.py command_name --delay 5
```

#### 4. 使用dry-run预览
```bash
python manage.py command_name --dry-run
```

#### 5. 查看处理进度
```bash
python manage.py import_youtube_videos --show-progress
```

#### 6. 重置进度重新开始
```bash
python manage.py import_youtube_videos --reset-progress
```

#### 5. 查看处理进度
```bash
python manage.py import_youtube_videos --show-progress
```

#### 6. 重置进度重新开始
```bash
python manage.py import_youtube_videos --reset-progress
```

---

## 📈 性能优化建议

### 1. 批量处理策略
- 使用 `--limit` 参数分批处理大量数据
- 根据API配额合理安排处理时间
- 使用 `--delay` 参数避免API限制
- 利用断点续传功能分多天处理大量数据
- 使用 `--show-progress` 监控处理进度

### 2. 成本控制
- 优先使用GPT-3.5-turbo进行批量生成
- 使用 `--dry-run` 预估处理数量
- 监控OpenAI账户使用情况

### 3. 网络优化
- 在网络稳定的环境下运行命令
- 适当增加延迟时间避免超时
- 监控API响应状态

### 4. 数据备份与恢复
- 在大批量操作前备份数据库
- 使用 `--dry-run` 模式验证操作
- 保留原始数据文件
- 定期备份进度文件 `youtube_import_progress.json`
- 使用 `--reset-progress` 时注意保存当前进度

---

## 📝 最佳实践

### 1. 命令执行顺序
1. 先使用 `--dry-run` 预览
2. 小批量测试验证效果
3. 逐步增加处理数量
4. 最后进行批量处理

### 2. 环境变量管理
- 使用环境变量存储API密钥
- 不要在代码中硬编码密钥
- 定期轮换API密钥

### 3. 监控和日志
- 记录命令执行日志
- 监控API使用情况
- 定期检查数据完整性
- 使用 `--show-progress` 定期查看处理状态
- 监控每日配额使用情况

### 4. 错误处理
- 遇到错误时检查网络连接
- 查看详细错误信息
- 必要时联系API服务提供商

---

## 🆘 技术支持

如需技术支持，请提供以下信息：
1. 执行的完整命令
2. 错误信息截图
3. 系统环境信息
4. API配额使用情况
5. 进度文件内容（`youtube_import_progress.json`）
6. 处理中断的时间点和当前进度

### 📋 进度管理最佳实践

#### 日常使用流程
1. **开始前检查**: `python manage.py import_youtube_videos --show-progress`
2. **预览处理**: `python manage.py import_youtube_videos --dry-run --limit 10`
3. **开始处理**: `python manage.py import_youtube_videos --delay 2`
4. **定期监控**: 定时运行 `--show-progress` 查看状态
5. **配额用完**: 等待第二天自动继续

#### 多天处理策略
```bash
# 第一天
python manage.py import_youtube_videos --max-quota 8000 --delay 2

# 第二天继续
python manage.py import_youtube_videos --show-progress  # 查看昨日进度
python manage.py import_youtube_videos --delay 2        # 继续处理

# 如需重新开始
python manage.py import_youtube_videos --reset-progress
```

#### 错误恢复
```bash
# 查看当前状态
python manage.py import_youtube_videos --show-progress

# 继续处理（自动跳过已处理项）
python manage.py import_youtube_videos --delay 2

# 如果需要完全重置
python manage.py import_youtube_videos --reset-progress
```

这样可以更快地定位和解决问题。 