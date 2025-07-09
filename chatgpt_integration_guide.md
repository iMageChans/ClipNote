# ChatGPT AI内容生成集成指南

## 概述

本系统已成功集成OpenAI ChatGPT API，可以自动为健身动作生成详细的markdown格式描述，并建立关键词映射关系。

## 功能特性

### ✅ 已完成功能

1. **AI内容生成**: 使用ChatGPT API自动生成健身动作详细描述
2. **结构化内容**: 生成标准化的markdown格式内容，包含：
   - What is [动作名称]?
   - [动作名称] Tutorial
   - Common Mistakes
   - Tips for Better Results
   - Muscles Worked
3. **关键词提取**: 自动从生成内容中提取关键词
4. **映射关系**: 创建内容与关键词的映射关系
5. **内容标记**: 标记AI生成的内容以便管理

### 🔧 API功能

- **AI生成标记**: `ai_generated` - 标识内容是否由AI生成
- **关键词列表**: `keywords` - 提取的关键词数组
- **关键词映射**: `keyword_mappings` - 详细的关键词与内容类型映射
- **生成内容**: `description` - markdown格式的详细描述

## 设置步骤

### 1. 获取OpenAI API密钥

1. 访问 [OpenAI API Keys](https://platform.openai.com/api-keys)
2. 登录您的OpenAI账户
3. 点击 "Create new secret key"
4. 为密钥设置名称（如"ClipNote-Fitness"）
5. 复制生成的API密钥（以sk-开头）

### 2. 设置环境变量

#### Windows PowerShell:
```powershell
$env:OPENAI_API_KEY="your_api_key_here"
$env:OPENAI_MODEL="gpt-3.5-turbo"  # 可选，默认为gpt-3.5-turbo
```

#### Windows 命令提示符:
```cmd
set OPENAI_API_KEY=your_api_key_here
set OPENAI_MODEL=gpt-3.5-turbo
```

#### Linux/macOS:
```bash
export OPENAI_API_KEY="your_api_key_here"
export OPENAI_MODEL="gpt-3.5-turbo"
```

#### 永久设置（推荐）:

**Windows:**
1. 右键"此电脑" -> "属性" -> "高级系统设置" -> "环境变量"
2. 在"用户变量"中点击"新建"
3. 变量名：`OPENAI_API_KEY`
4. 变量值：您的API密钥

**Linux/macOS:**
```bash
echo 'export OPENAI_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### 3. 选择模型

支持的模型：
- `gpt-3.5-turbo` - 快速且经济（推荐用于大量内容生成）
- `gpt-4` - 更高质量但更昂贵
- `gpt-4-turbo` - 平衡质量和速度

## 使用方法

### 基本命令

```bash
# 测试模式（推荐先运行）
python manage.py generate_descriptions --dry-run --limit 3

# 生成少量内容进行测试
python manage.py generate_descriptions --limit 5 --delay 3 --extract-keywords

# 生成所有缺失描述的动作
python manage.py generate_descriptions --extract-keywords

# 强制重新生成所有描述
python manage.py generate_descriptions --force --extract-keywords
```

### 命令选项详解

| 选项 | 说明 | 示例 |
|------|------|------|
| `--dry-run` | 仅显示将要处理的动作，不实际生成内容 | `--dry-run` |
| `--limit N` | 限制处理的动作数量 | `--limit 10` |
| `--delay N` | 请求间延迟时间（秒），避免API限制 | `--delay 3` |
| `--force` | 强制重新生成已有描述的动作 | `--force` |
| `--model NAME` | 指定使用的ChatGPT模型 | `--model gpt-4` |
| `--extract-keywords` | 同时提取关键词并创建映射关系 | `--extract-keywords` |

### 生成内容示例

生成的内容将遵循以下结构：

```markdown
# Bench Press

## What is Bench Press?
The bench press is a fundamental upper body strength exercise that primarily targets the chest, shoulders, and triceps...

## Bench Press Tutorial
1. Lie flat on the bench with your feet firmly planted on the ground
2. Grip the barbell with hands slightly wider than shoulder-width apart
3. Lower the bar to your chest in a controlled manner
4. Press the bar back up to the starting position

## Common Mistakes
- Arching the back excessively
- Bouncing the bar off the chest
- Using too wide or too narrow grip
- Not maintaining proper foot placement

## Tips for Better Results
- Focus on controlling the weight throughout the entire range of motion
- Keep your shoulder blades retracted and squeezed together
- Maintain tension in your core throughout the movement
- Use a spotter for heavy weights

## Muscles Worked
**Primary Muscles:**
- Pectoralis major (chest)
- Anterior deltoids (front shoulders)
- Triceps brachii

**Secondary Muscles:**
- Serratus anterior
- Latissimus dorsi (stabilizing)
```

### API调用示例

```javascript
// 获取包含AI生成内容的健身动作
const response = await fetch('/api/exercises/chest/bench-press/');
const exercise = await response.json();

console.log(exercise);
// 输出:
// {
//   "id": 1,
//   "name": "bench press",
//   "slug": "bench-press",
//   "body_part": {
//     "name": "chest",
//     "slug": "chest"
//   },
//   "description": "# Bench Press\n\n## What is Bench Press?\n...",
//   "ai_generated": true,
//   "keywords": ["bench press", "what is bench press", "tutorial", "common mistakes", "tips"],
//   "keyword_mappings": [
//     {
//       "keyword": "what is bench press",
//       "content_type": "what_is",
//       "relevance_score": 1.0
//     },
//     {
//       "keyword": "tutorial",
//       "content_type": "tutorial",
//       "relevance_score": 1.0
//     }
//   ]
// }
```

## 关键词映射系统

### 内容类型分类

系统自动将生成的内容分为以下类型：

1. **what_is**: "What is"类型的介绍内容
2. **tutorial**: 教程和操作步骤
3. **mistakes**: 常见错误
4. **tips**: 改进建议和技巧
5. **muscles**: 肌肉群信息
6. **other**: 其他类型内容

### 关键词提取规则

1. **标题提取**: 从markdown标题（##）中提取关键词
2. **内容分析**: 根据标题内容判断所属类型
3. **基础关键词**: 自动添加动作名称、部位等基础关键词
4. **相关性评分**: 为每个关键词分配0.0-1.0的相关性评分

## API配额和成本管理

### OpenAI API定价（参考）

- **GPT-3.5-Turbo**: ~$0.002/1K tokens
- **GPT-4**: ~$0.03/1K tokens
- **GPT-4-Turbo**: ~$0.01/1K tokens

### 预估成本

每个健身动作描述大约使用1500-2000 tokens：

- **GPT-3.5-Turbo**: 约$0.003-0.004/动作
- **GPT-4**: 约$0.045-0.06/动作
- **GPT-4-Turbo**: 约$0.015-0.02/动作

对于867个动作：
- **GPT-3.5-Turbo**: 约$2.6-3.5
- **GPT-4**: 约$39-52
- **GPT-4-Turbo**: 约$13-17

### 优化建议

1. **使用GPT-3.5-Turbo**: 对于批量生成，质量足够且成本低
2. **分批处理**: 使用`--limit`参数分批生成
3. **增加延迟**: 使用`--delay 3`避免API限制
4. **监控使用**: 定期检查OpenAI账户使用情况

## 数据状态检查

```bash
# 检查当前状态
python manage.py shell -c "
from fitness.models import Exercise
total = Exercise.objects.count()
ai_generated = Exercise.objects.filter(ai_generated=True).count()
no_description = Exercise.objects.filter(description='').count()
print(f'总动作数量: {total}')
print(f'AI生成描述: {ai_generated}')
print(f'无描述: {no_description}')
print(f'待处理: {total - ai_generated}')
"

# 检查关键词映射
python manage.py shell -c "
from fitness.models import ContentKeywordMapping
mappings = ContentKeywordMapping.objects.count()
content_types = ContentKeywordMapping.objects.values('content_type').distinct().count()
print(f'关键词映射总数: {mappings}')
print(f'内容类型数量: {content_types}')
"
```

## 管理界面功能

### Exercise管理界面新增功能

1. **AI标记**: 显示内容是否由AI生成
2. **关键词计数**: 显示关键词映射数量
3. **YouTube状态**: 显示是否有YouTube链接
4. **关键词详情**: 查看详细的关键词映射

### 新增模型管理

1. **ContentKeywordMapping**: 管理关键词映射关系
2. **按类型筛选**: 可按内容类型筛选关键词
3. **相关性评分**: 管理关键词相关性

## 故障排除

### 常见错误

1. **API密钥错误**: 检查环境变量设置
2. **配额超限**: 增加延迟或稍后重试
3. **网络错误**: 检查网络连接
4. **模型不存在**: 确认模型名称正确

### 日志查看

命令会输出详细的处理日志：
- API调用状态
- Token使用情况
- 生成内容预览
- 关键词提取结果
- 成功/失败统计

### 调试模式

```bash
# 查看详细错误信息
python manage.py generate_descriptions --limit 1 --delay 5 -v 2
```

## 前端集成示例

### React组件

```jsx
import React from 'react';
import ReactMarkdown from 'react-markdown';

const ExerciseDescription = ({ exercise }) => {
  return (
    <div className="exercise-description">
      {exercise.ai_generated && (
        <div className="ai-badge">
          🤖 AI生成内容
        </div>
      )}
      
      <ReactMarkdown>
        {exercise.description}
      </ReactMarkdown>
      
      {exercise.keywords && exercise.keywords.length > 0 && (
        <div className="keywords">
          <h4>相关关键词：</h4>
          {exercise.keywords.map((keyword, index) => (
            <span key={index} className="keyword-tag">
              {keyword}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};
```

### CSS样式

```css
.exercise-description {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.ai-badge {
  background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  display: inline-block;
  margin-bottom: 16px;
}

.keyword-tag {
  background: #f0f0f0;
  padding: 4px 8px;
  border-radius: 4px;
  margin: 2px;
  display: inline-block;
  font-size: 12px;
}
```

## 高级用法

### 自定义提示词

如需修改生成内容的结构，可编辑管理命令中的prompt模板。

### 批量更新

```bash
# 每天生成50个描述（避免超出配额）
python manage.py generate_descriptions --limit 50 --extract-keywords --delay 3

# 使用定时任务每日执行
# 在crontab中添加：
# 0 2 * * * cd /path/to/project && python manage.py generate_descriptions --limit 50 --extract-keywords
```

### 质量控制

1. 使用`--dry-run`预览要处理的内容
2. 小批量测试不同模型的效果
3. 定期检查生成内容的质量
4. 必要时手动编辑AI生成的内容

## 安全注意事项

1. **API密钥保护**: 永远不要在代码中硬编码API密钥
2. **成本控制**: 设置OpenAI账户的使用限制
3. **内容审核**: 定期检查生成内容的准确性
4. **备份数据**: 在批量生成前备份数据库

ChatGPT集成已经完全可用，可以大大提高健身动作描述的生产效率！🚀 