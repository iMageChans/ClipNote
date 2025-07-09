# Docker环境变量配置指南

本指南详细说明如何在Docker环境中安全地配置API密钥和其他敏感信息。

## 📋 文件结构

项目现在包含以下环境配置文件：

```
ClipNote/
├── .env                 # 实际环境变量文件 (不提交到Git)
├── .env.example         # 环境变量模板文件 (提交到Git)
├── .gitignore           # Git忽略文件，包含.env保护
├── docker-compose.yaml  # Docker编排文件，使用环境变量
├── Dockerfile           # Docker镜像文件，支持环境变量
└── requirements.txt     # 新增python-decouple依赖
```

## 🔧 配置步骤

### 1. 创建环境变量文件

复制模板文件并填入实际的API密钥：

```bash
# 复制模板文件
cp .env.example .env

# 编辑.env文件，填入真实的API密钥
notepad .env  # Windows
# 或
nano .env     # Linux/macOS
```

### 2. 填入API密钥

编辑`.env`文件，添加您的API密钥：

```bash
# Django配置
DEBUG=True
SECRET_KEY=your-unique-django-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# 数据库配置
DATABASE_URL=sqlite:///db.sqlite3

# OpenAI API配置 (用于ChatGPT集成)
# 请在 https://platform.openai.com/api-keys 获取您的API密钥
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-3.5-turbo

# YouTube API配置 (用于获取视频链接)
# 请在 https://console.cloud.google.com/ 获取您的API密钥
YOUTUBE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 其他配置
DJANGO_SETTINGS_MODULE=ClipNote.settings
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1
```

### 3. 获取API密钥

#### OpenAI API密钥
1. 访问 [OpenAI API Keys](https://platform.openai.com/api-keys)
2. 登录您的OpenAI账户
3. 点击"Create new secret key"
4. 复制生成的密钥（以`sk-`开头）
5. 将密钥粘贴到`.env`文件的`OPENAI_API_KEY`字段

#### YouTube Data API密钥
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用YouTube Data API v3
4. 创建API凭据（API密钥）
5. 将密钥粘贴到`.env`文件的`YOUTUBE_API_KEY`字段

### 4. 生成Django密钥

为生产环境生成安全的Django密钥：

```bash
# 进入Django shell
python manage.py shell

# 生成新的密钥
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

将生成的密钥复制到`.env`文件的`SECRET_KEY`字段。

## 🐳 Docker使用

### 启动服务

```bash
# 构建并启动容器
docker-compose up --build

# 后台运行
docker-compose up -d --build

# 查看日志
docker-compose logs -f
```

### 重新构建

```bash
# 重新构建镜像
docker-compose build --no-cache

# 重启服务
docker-compose restart
```

### 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

## 🔒 安全最佳实践

### 1. 环境变量保护
- ✅ `.env`文件已添加到`.gitignore`，不会被提交到Git
- ✅ 使用`python-decouple`安全读取环境变量
- ✅ Docker配置通过`env_file`读取环境变量
- ❌ 绝不在代码中硬编码API密钥

### 2. 生产环境配置
```bash
# 生产环境.env配置
DEBUG=False
SECRET_KEY=your-super-secure-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
OPENAI_API_KEY=sk-your-production-openai-key
YOUTUBE_API_KEY=your-production-youtube-key
```

### 3. 权限管理
```bash
# 设置.env文件权限 (Linux/macOS)
chmod 600 .env

# 确保只有所有者可以读写
ls -la .env
```

## 🧪 测试配置

### 验证环境变量

在容器中检查环境变量是否正确加载：

```bash
# 进入容器
docker-compose exec web bash

# 检查环境变量
echo $OPENAI_API_KEY
echo $YOUTUBE_API_KEY
echo $DEBUG

# 或在Django shell中检查
python manage.py shell -c "
from django.conf import settings
print('OpenAI API Key:', settings.OPENAI_API_KEY[:10] + '...' if settings.OPENAI_API_KEY else 'Not set')
print('YouTube API Key:', settings.YOUTUBE_API_KEY[:10] + '...' if settings.YOUTUBE_API_KEY else 'Not set')
print('Debug Mode:', settings.DEBUG)
"
```

### 测试API连接

```bash
# 测试OpenAI API连接
docker-compose exec web python manage.py generate_descriptions --dry-run --limit 1

# 测试YouTube API连接
docker-compose exec web python manage.py import_youtube_videos --dry-run --limit 1
```

## 🔄 环境变量更新

### 更新API密钥

1. 编辑`.env`文件
2. 重启Docker服务

```bash
# 更新环境变量后重启
docker-compose restart web
```

### 添加新的环境变量

1. 在`.env`和`.env.example`中添加新变量
2. 更新`docker-compose.yaml`的environment部分
3. 更新`ClipNote/settings.py`以读取新变量
4. 重新构建容器

```bash
docker-compose up --build
```

## 📊 环境变量列表

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `DEBUG` | 否 | True | Django调试模式 |
| `SECRET_KEY` | 是 | - | Django密钥 |
| `ALLOWED_HOSTS` | 否 | localhost,127.0.0.1,0.0.0.0 | 允许的主机 |
| `DATABASE_URL` | 否 | sqlite:///db.sqlite3 | 数据库连接 |
| `OPENAI_API_KEY` | 是 | - | OpenAI API密钥 |
| `OPENAI_MODEL` | 否 | gpt-3.5-turbo | ChatGPT模型 |
| `YOUTUBE_API_KEY` | 是 | - | YouTube API密钥 |
| `DJANGO_SETTINGS_MODULE` | 否 | ClipNote.settings | Django设置模块 |

## ⚠️ 故障排除

### 常见问题

#### 1. API密钥无效
```
错误: Invalid API key provided
解决: 检查.env文件中的API密钥是否正确，确保没有多余的空格
```

#### 2. 环境变量未加载
```
错误: 环境变量为空
解决: 
1. 检查.env文件是否存在
2. 确保docker-compose.yaml中包含env_file配置
3. 重启Docker容器
```

#### 3. 权限问题
```
错误: Permission denied
解决: 检查.env文件权限，确保Docker可以读取
```

### 调试步骤

1. **检查文件是否存在**
   ```bash
   ls -la .env
   ```

2. **验证Docker配置**
   ```bash
   docker-compose config
   ```

3. **检查容器环境变量**
   ```bash
   docker-compose exec web env | grep -E "(OPENAI|YOUTUBE|DEBUG)"
   ```

4. **查看容器日志**
   ```bash
   docker-compose logs web
   ```

## 📚 相关文档

- [Fitness应用管理命令操作手册](fitness/FITNESS_COMMANDS_MANUAL.md)
- [Django环境变量配置](https://docs.djangoproject.com/en/5.0/topics/settings/)
- [Docker Compose环境变量](https://docs.docker.com/compose/environment-variables/)
- [python-decouple文档](https://github.com/henriquebastos/python-decouple)

## 🚀 部署清单

部署到生产环境前请检查：

- [ ] 创建并配置`.env`文件
- [ ] 设置生产级别的`SECRET_KEY`
- [ ] 配置生产域名的`ALLOWED_HOSTS`
- [ ] 设置`DEBUG=False`
- [ ] 验证所有API密钥有效
- [ ] 测试Docker容器启动
- [ ] 验证API连接正常
- [ ] 检查日志无错误信息

---

**重要**: 请确保`.env`文件永远不要提交到版本控制系统！如果意外提交了含有密钥的文件，请立即更换所有API密钥。 