# YouTube API 设置指南

本文档将帮助您设置YouTube Data API v3来为健身动作自动获取教程视频。

## 步骤1: 创建Google Cloud项目

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 点击"选择项目" -> "新建项目"
3. 输入项目名称（例如："fitness-app"）
4. 点击"创建"

## 步骤2: 启用YouTube Data API v3

1. 在项目控制台中，点击左侧菜单的"API和服务" -> "库"
2. 搜索"YouTube Data API v3"
3. 点击搜索结果中的"YouTube Data API v3"
4. 点击"启用"

## 步骤3: 创建API密钥

1. 点击左侧菜单的"API和服务" -> "凭据"
2. 点击"+ 创建凭据" -> "API密钥"
3. 复制生成的API密钥

## 步骤4: 限制API密钥（推荐）

1. 在创建API密钥后，点击"限制密钥"
2. 在"API限制"部分，选择"限制密钥"
3. 从列表中选择"YouTube Data API v3"
4. 点击"保存"

## 步骤5: 设置环境变量

### Windows (PowerShell):
```powershell
$env:YOUTUBE_API_KEY="您的API密钥"
```

### Windows (命令提示符):
```cmd
set YOUTUBE_API_KEY=您的API密钥
```

### Linux/macOS:
```bash
export YOUTUBE_API_KEY="您的API密钥"
```

### 永久设置（推荐）:

**Windows:**
1. 右键"此电脑" -> "属性" -> "高级系统设置" -> "环境变量"
2. 在"用户变量"中点击"新建"
3. 变量名：`YOUTUBE_API_KEY`
4. 变量值：您的API密钥

**Linux/macOS:**
将以下行添加到 `~/.bashrc` 或 `~/.zshrc`:
```bash
export YOUTUBE_API_KEY="您的API密钥"
```

## 步骤6: 使用管理命令

### 测试模式（推荐先运行）:
```bash
python manage.py import_youtube_videos --dry-run --limit 5
```

### 处理少量数据进行测试:
```bash
python manage.py import_youtube_videos --limit 10 --delay 2
```

### 处理所有数据:
```bash
python manage.py import_youtube_videos
```

### 强制更新已有链接:
```bash
python manage.py import_youtube_videos --force
```

## 命令选项说明

- `--force`: 强制更新已有YouTube链接的动作
- `--limit N`: 限制处理的动作数量（用于测试）
- `--delay N`: 请求之间的延迟时间（秒），默认1秒
- `--dry-run`: 仅显示将要处理的动作，不实际更新数据库

## API配额说明

YouTube Data API v3有免费配额限制：
- 每天10,000个配额单位
- 搜索操作消耗100个配额单位
- 约可进行100次搜索/天

建议：
1. 使用 `--delay 2` 增加延迟避免过快请求
2. 分批处理大量数据
3. 使用 `--limit` 参数进行测试

## 故障排除

### 常见错误：

1. **403 Forbidden**: API密钥无效或未启用API
2. **400 Bad Request**: 搜索查询格式错误
3. **429 Too Many Requests**: 超过API配额限制

### 检查API使用情况：
访问 [Google Cloud Console API配额页面](https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas)

## 示例输出

```
[1/10] 正在处理: bench-press
    搜索: "bench press tutorial"
      ✓ 找到: How to Bench Press for Beginners | Proper Form...
  ✓ 已保存视频链接: https://www.youtube.com/watch?v=xxxxx

============================================================
处理完成!
成功获取视频: 8 个
未找到视频: 1 个
处理失败: 1 个
总计处理: 10 个

成功率: 80.0%
``` 