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
使用YouTube Data API v3自动为健身动作搜索并获取教程视频链接。

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
```
将处理 864 个没有YouTube链接的动作
使用模型: YouTube Data API v3
请求延迟: 2.0 秒

[1/864] 正在处理: bench-press
    搜索: "bench press tutorial"
      ✓ 找到: How to Bench Press for Beginners | Proper Form...
  ✓ 已保存视频链接: https://www.youtube.com/watch?v=xxxxx

[2/864] 正在处理: squat
    搜索: "squat tutorial"
      ✓ 找到: Perfect Squat Form Tutorial...
  ✓ 已保存视频链接: https://www.youtube.com/watch?v=yyyyy

============================================================
处理完成!
成功获取视频: 820 个
未找到视频: 35 个
处理失败: 9 个
总计处理: 864 个

成功率: 94.9%
```

### API配额管理
- **每日免费配额**: 10,000单位
- **搜索操作消耗**: 100单位/次
- **建议延迟**: 1-2秒避免过快请求

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
python manage.py import_youtube_videos --limit 50 --delay 2  # 分批处理

# 3. 生成AI描述
python manage.py generate_descriptions --dry-run --limit 3  # 预览
python manage.py generate_descriptions --limit 10 --extract-keywords --delay 3  # 测试
python manage.py generate_descriptions --extract-keywords --delay 2  # 批量生成
```

### 数据更新维护
```bash
# 强制更新所有YouTube链接
python manage.py import_youtube_videos --force --delay 2

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
python manage.py shell -c "
from fitness.models import Exercise
total = Exercise.objects.count()
with_youtube = Exercise.objects.exclude(youtube_url='').count()
print(f'总动作: {total}')
print(f'有YouTube链接: {with_youtube}')
print(f'缺失YouTube链接: {total - with_youtube}')
"
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
解决: 增加 --delay 参数值，或等待配额重置
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

---

## 📈 性能优化建议

### 1. 批量处理策略
- 使用 `--limit` 参数分批处理大量数据
- 根据API配额合理安排处理时间
- 使用 `--delay` 参数避免API限制

### 2. 成本控制
- 优先使用GPT-3.5-turbo进行批量生成
- 使用 `--dry-run` 预估处理数量
- 监控OpenAI账户使用情况

### 3. 网络优化
- 在网络稳定的环境下运行命令
- 适当增加延迟时间避免超时
- 监控API响应状态

### 4. 数据备份
- 在大批量操作前备份数据库
- 使用 `--dry-run` 模式验证操作
- 保留原始数据文件

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

这样可以更快地定位和解决问题。 