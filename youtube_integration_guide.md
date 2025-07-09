# YouTube视频集成使用指南

## 概述

本系统已成功集成YouTube Data API v3，可以自动为健身动作获取教程视频，并提供在网站上播放的完整解决方案。

## 功能特性

### ✅ 已完成功能

1. **自动视频获取**: 使用YouTube API自动搜索每个健身动作的教程视频
2. **智能搜索策略**: 多种搜索关键词组合，提高匹配成功率
3. **视频链接转换**: 自动将YouTube观看链接转换为嵌入链接
4. **缩略图支持**: 提供多种质量的视频缩略图
5. **网站内播放**: YouTube视频可以在您的网站内直接播放

### 🔧 API功能

- **原始YouTube链接**: `youtube_url` - 标准的YouTube观看链接
- **嵌入播放链接**: `youtube_embed_url` - 用于iframe嵌入的链接
- **缩略图**: `youtube_thumbnail` - 标准质量缩略图
- **高清缩略图**: `youtube_thumbnail_hd` - 高清质量缩略图

## 使用方法

### 1. 设置YouTube API密钥

```bash
# Windows PowerShell
$env:YOUTUBE_API_KEY="您的API密钥"

# Linux/macOS
export YOUTUBE_API_KEY="您的API密钥"
```

### 2. 获取YouTube视频

```bash
# 测试模式（推荐先运行）
python manage.py import_youtube_videos --dry-run --limit 5

# 处理少量数据测试
python manage.py import_youtube_videos --limit 10 --delay 2

# 处理所有动作
python manage.py import_youtube_videos

# 强制更新已有链接
python manage.py import_youtube_videos --force
```

### 3. API调用示例

```javascript
// 获取单个健身动作数据
const response = await fetch('/api/exercises/abdominals/ab-crunch-machine/');
const exercise = await response.json();

console.log(exercise);
// 输出:
// {
//   "id": 1,
//   "name": "ab crunch machine",
//   "slug": "ab-crunch-machine",
//   "body_part": {
//     "id": 1,
//     "name": "abdominals",
//     "slug": "abdominals"
//   },
//   "description": "...",
//   "youtube_url": "https://www.youtube.com/watch?v=Ag_9e-dqQqM",
//   "youtube_embed_url": "https://www.youtube.com/embed/Ag_9e-dqQqM",
//   "youtube_thumbnail": "https://img.youtube.com/vi/Ag_9e-dqQqM/hqdefault.jpg",
//   "youtube_thumbnail_hd": "https://img.youtube.com/vi/Ag_9e-dqQqM/maxresdefault.jpg",
//   "url": "/api/exercises/abdominals/ab-crunch-machine"
// }
```

### 4. 前端集成

#### React组件示例

```jsx
import React, { useState } from 'react';

const ExerciseVideoPlayer = ({ exercise }) => {
  const [showVideo, setShowVideo] = useState(false);

  const handlePlayVideo = () => {
    setShowVideo(true);
  };

  return (
    <div className="exercise-card">
      <h3>{exercise.name}</h3>
      
      {!showVideo ? (
        // 显示缩略图
        <div className="thumbnail-container" onClick={handlePlayVideo}>
          <img 
            src={exercise.youtube_thumbnail} 
            alt={`${exercise.name} 教程`}
            className="video-thumbnail"
          />
          <button className="play-button">▶</button>
        </div>
      ) : (
        // 显示视频播放器
        <div className="video-container">
          <iframe
            src={`${exercise.youtube_embed_url}?autoplay=1&rel=0`}
            allowFullScreen
            frameBorder="0"
          />
        </div>
      )}
      
      <div className="exercise-description">
        {exercise.description}
      </div>
    </div>
  );
};
```

#### Vue.js组件示例

```vue
<template>
  <div class="exercise-card">
    <h3>{{ exercise.name }}</h3>
    
    <div v-if="!showVideo" class="thumbnail-container" @click="playVideo">
      <img 
        :src="exercise.youtube_thumbnail" 
        :alt="`${exercise.name} 教程`"
        class="video-thumbnail"
      />
      <button class="play-button">▶</button>
    </div>
    
    <div v-else class="video-container">
      <iframe
        :src="`${exercise.youtube_embed_url}?autoplay=1&rel=0`"
        allowfullscreen
        frameborder="0"
      />
    </div>
    
    <div class="exercise-description" v-html="exercise.description"></div>
  </div>
</template>

<script>
export default {
  props: ['exercise'],
  data() {
    return {
      showVideo: false
    };
  },
  methods: {
    playVideo() {
      this.showVideo = true;
    }
  }
};
</script>
```

### 5. CSS样式示例

```css
.exercise-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.thumbnail-container {
  position: relative;
  cursor: pointer;
}

.video-thumbnail {
  width: 100%;
  height: 200px;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.video-thumbnail:hover {
  transform: scale(1.05);
}

.play-button {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255, 0, 0, 0.8);
  border: none;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  color: white;
  font-size: 20px;
  cursor: pointer;
}

.video-container {
  position: relative;
  width: 100%;
  height: 0;
  padding-bottom: 56.25%; /* 16:9 宽高比 */
}

.video-container iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: none;
}
```

## 管理命令选项

| 选项 | 说明 | 示例 |
|------|------|------|
| `--dry-run` | 仅显示将要处理的动作，不更新数据库 | `--dry-run` |
| `--limit N` | 限制处理的动作数量 | `--limit 50` |
| `--delay N` | 请求间延迟时间（秒） | `--delay 2` |
| `--force` | 强制更新已有YouTube链接 | `--force` |

## API配额管理

- **每日免费配额**: 10,000单位
- **搜索操作消耗**: 100单位/次
- **建议策略**: 
  - 使用`--delay 2`避免过快请求
  - 分批处理大量数据
  - 监控API使用情况

## 数据状态检查

```bash
# 检查当前状态
python manage.py shell -c "
from fitness.models import Exercise
total = Exercise.objects.count()
with_youtube = Exercise.objects.exclude(youtube_url='').exclude(youtube_url__isnull=True).count()
print(f'总动作数量: {total}')
print(f'已有视频: {with_youtube}')
print(f'待处理: {total - with_youtube}')
"
```

## 故障排除

### 常见问题

1. **403 Forbidden**: 检查API密钥是否正确设置
2. **400 Bad Request**: 检查网络连接和搜索查询
3. **429 Too Many Requests**: 超过API配额，等待或增加延迟

### 日志查看

管理命令会输出详细的处理日志，包括：
- 搜索查询
- 找到的视频标题
- 成功/失败统计

## 示例文件

项目中包含 `youtube_player_example.html` 文件，展示了完整的前端集成示例，可直接在浏览器中打开查看效果。

## 安全考虑

1. **API密钥保护**: 永远不要在前端代码中暴露API密钥
2. **环境变量**: 使用环境变量存储敏感信息
3. **HTTPS**: 确保在HTTPS环境下使用YouTube嵌入
4. **内容过滤**: 系统自动过滤不合适的视频内容

## 性能优化建议

1. **懒加载**: 只在用户点击时加载视频
2. **缓存**: 缓存API响应减少重复请求
3. **CDN**: 使用CDN加速缩略图加载
4. **预加载**: 预加载关键视频的缩略图 