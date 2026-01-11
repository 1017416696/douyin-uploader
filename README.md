# 抖音视频自动上传 Skill

基于 SRT 字幕文件，自动生成爆款标题、描述和标签，并使用 Chrome DevTools MCP 自动上传到抖音。

## 安装

将当前项目文件夹放置在以下位置：

- **macOS/Linux**: `~/.claude/skills/`
- **Windows**: `C:\Users\你的用户名\.claude\skills\`（例如：`C:\Users\penrose\.claude\skills\`）

## 快速开始

### 1. 安装 Chrome DevTools MCP

```bash
claude mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest
```

### 2. 使用 Skill

```
用户: 帮我上传 /path/to/video.srt 到抖音
```

## 目录结构

```
douyin-uploader/
├── SKILL.md              # Skill 主定义文件
├── README.md             # 本文件
└── scripts/
    └── srt_parser.py     # SRT 字幕解析器
```

## 功能特点

- ✅ 自动匹配同名视频文件
- ✅ 解析 SRT 字幕生成内容
- ✅ 自动打开上传页面
- ✅ 自动上传视频文件
- ✅ 自动填写标题、描述、标签
- ✅ Cookie 自动保存，无需重复登录

## 工作流程

1. 用户提供 SRT 文件路径
2. Skill 查找同名视频文件
3. 解析字幕内容
4. 生成爆款标题、描述、标签
5. 使用 Chrome DevTools MCP 打开抖音上传页面
6. 自动上传视频
7. 自动填写表单
8. 用户确认后发布

> 如果没有 srt 字幕文件，可以通过 [VoSub](https://github.com/1017416696/VoSub) 字幕编辑工具，或者直接通过剪映自动生成 srt 字幕文件。


## 支持的视频格式

- QuickTime (.mov) - **优先选择，质量更高**
- MP4 (.mp4)
- AVI (.avi)
- Matroska (.mkv)

**注意**：当同时存在 MP4 和 MOV 格式时，自动选择 MOV 格式上传。

## 抖音创作者中心

- **上传页面**: https://creator.douyin.com/creator-micro/content/publish

## 注意事项

1. **首次登录**：首次需要在打开的浏览器中手动登录抖音
2. **Cookie 保存**：登录后 Cookie 自动保存，下次无需重新登录
3. **内容审核**：发布前请检查生成的内容是否准确
4. **社区规范**：确保上传内容符合抖音社区准则

## 辅助脚本

单独解析 SRT 字幕文件：

```bash
python3 scripts/srt_parser.py video.srt --find-video
```

## 常见问题

### Skill 没有被触发？

确保你的请求中包含关键词："上传抖音"、"发布视频"、"SRT字幕" 等。

### 找不到视频文件？

确保视频文件与 SRT 文件同名（扩展名不同），且在同一目录下。

### MCP 连接失败？

检查 MCP 是否正常安装：
```bash
claude mcp list
```

## 相关资源

- [Awesome Claude Skills](https://github.com/ComposioHQ/awesome-claude-skills) - 精选 Claude Skills 资源列表，更多技能示例和灵感
