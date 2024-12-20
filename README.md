# YouTube Video Downloader

一个基于 FastAPI + yt-dlp 的 YouTube 视频下载工具，支持进度显示和视频预览。

## 功能特点

- 支持输入 YouTube 视频链接下载
- 实时显示下载进度
- 支持视频预览播放
- 显示视频详细信息（标题、作者、时长等）
- 支持短链接格式 (youtu.be)

## 技术栈

- FastAPI: Web框架
- yt-dlp: 视频下载工具
- Jinja2: 模板引擎
- TailwindCSS: 样式框架

## 安装步骤

1. 安装依赖：
```

2. 访问网页：
   - 打开浏览器
   - 访问 http://localhost:8000

## 使用指南

1. 支持的视频类型：
   - 普通YouTube视频
   - YouTube Shorts
   - 播放列表（单个视频）

2. 下载步骤：
   - 复制YouTube视频链接
   - 粘贴到输入框
   - 点击"Download"按钮
   - 等待下载完成

3. 进度显示：
   - 实时显示下载进度百分比
   - 显示已下载/总大小
   - 显示下载速度

## 测试指南

1. 环境检查：
   - 确保服务器已停止运行（如果在运行）
   - 清空 downloads 文件夹
   - 重新启动服务器

2. 基础功能测试：
   - 确认页面正常加载
   - 确认下载表单可见
   - 确认进度条显示正常

3. 下载测试流程：
   a. 短视频测试（推荐首选）：
      - 使用YouTube Shorts链接（如：https://youtube.com/shorts/...)
      - 观察进度条显示
      - 验证下载完成后的播放
   
   b. 常规视频测试：
      - 使用较长视频进行测试
      - 验证大文件下载稳定性
      - 检查文件完整性

4. 错误处理测试：
   - 测试无效链接
   - 测试非YouTube链接
   - 测试已删除的视频

## 故障排除

1. 下载失败：
   - 检查网络连接
   - 确认视频链接有效
   - 查看服务器日志

2. 进度显示问题：
   - 刷新页面
   - 重启服务器
   - 清空浏览器缓存

3. 常见错误：
   - "Download failed": 检查视频是否可用
   - "Failed to fetch progress": 检查服务器状态
   - "Could not convert string to float": 重启服务器

## 注意事项

1. 确保有足够的磁盘空间
2. 保持网络连接稳定
3. 遵守YouTube服务条款
4. 仅用于个人用途

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目。

## 许可证

[添加许可证信息]