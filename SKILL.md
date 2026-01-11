---
name: douyin-uploader
description: 自动将视频上传到抖音创作者中心，基于 SRT 字幕生成爆款标题、描述和标签。当用户说"上传抖音"、"发布视频到抖音"、"抖音自动上传"、"SRT字幕上传"或提供 .srt 文件路径时使用此 Skill。
allowed-tools: Read, Bash, AskUserQuestion, mcp__chrome-devtools__new_page, mcp__chrome-devtools__list_pages, mcp__chrome-devtools__select_page, mcp__chrome-devtools__close_page, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__click, mcp__chrome-devtools__fill, mcp__chrome-devtools__fill_form, mcp__chrome-devtools__upload_file, mcp__chrome-devtools__press_key, mcp__chrome-devtools__evaluate_script, mcp__chrome-devtools__wait_for, mcp__chrome-devtools__drag, mcp__chrome-devtools__hover
---

# 抖音视频自动上传 Skill

## 上传页面
https://creator.douyin.com/creator-micro/content/publish

---

## 执行步骤

### Step 1: 准备内容
1. **调用 `srt_parser.py` 解析 SRT 字幕文件**：
   ```bash
   python3 scripts/srt_parser.py "/path/to/video.srt" --json
   ```
   获取字幕的全文、时长、字数等信息

2. 根据解析结果生成：
   - **标题**（15-30字）：基于字幕核心内容提炼
   - **描述**（100-200字）：使用 `full_text` 或 `summary`，整理成要点列表
   - **标签**（5个，格式：`#标签1 #标签2 #标签3 #标签4 #标签5`）

3. 查找同名视频文件（优先 .mov，其次 .mp4）

### Step 2: 上传视频
1. 打开上传页面
2. **直接使用 `upload_file` 上传视频文件**（点击上传区域会触发文件选择器，要避免）
3. **确认视频上传开始**（看到上传进度后立即继续下一步，不要等待上传完成！）

4. **视频上传的同时，并行完成以下操作**：
   - 填写标题
   - 填写描述和标签

### Step 3: 填写内容
使用 `evaluate_script` 一次性设置描述和标签：

```javascript
() => {
  const editor = document.querySelector('[contenteditable="true"]');
  if (editor) {
    editor.innerHTML = `描述内容<br><br>要点1<br>要点2<br>要点3<br><br>#标签1 #标签2 #标签3 #标签4 #标签5`;
    editor.dispatchEvent(new Event('input', { bubbles: true }));
    return 'Success';
  }
  return 'Failed';
}
```

**标签规则**：
- 必须添加 5 个标签
- 格式：`#标签名`，空格分隔
- 推荐：1-2个热门标签 + 3-4个精准相关标签
- 示例：`#效率工具 #AI编程 #编程工具 #Claude #零基础学编程`

### Step 4: 完工
**⚠️ 完工标准：视频开始上传 + 标题/描述/标签填写完成 = 完工！不需要等待上传完成，不需要确认发布，用户会自己处理后续操作。**

---

## 内容生成参考

| 视频类型 | 5个推荐标签 |
|---------|------------|
| AI/编程工具类 | `#效率工具 #AI编程 #零基础学编程 #编程工具 #Claude` |
| 效率/软件类 | `#效率工具 #软件推荐 #APP推荐 #好物分享 #实用工具` |
| 教程/干货类 | `#干货分享 #教程 #知识科普 #学习 #技能提升` |

---

## 视频格式优先级
1. .mov（首选）
2. .mp4
3. .avi
4. .mkv
