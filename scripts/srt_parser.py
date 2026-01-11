#!/usr/bin/env python3
"""
SRT 字幕解析器
用于解析 SRT 字幕文件并提取内容，为抖音视频上传生成标题、描述和标签提供素材。
"""

import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class Subtitle:
    """单个字幕条目"""
    index: int
    start_time: str  # 格式: "00:00:01,000"
    end_time: str    # 格式: "00:00:04,000"
    text: str

    @property
    def start_ms(self) -> int:
        """将开始时间转换为毫秒"""
        return self._time_to_ms(self.start_time)

    @property
    def end_ms(self) -> int:
        """将结束时间转换为毫秒"""
        return self._time_to_ms(self.end_time)

    @staticmethod
    def _time_to_ms(time_str: str) -> int:
        """将 SRT 时间格式转换为毫秒"""
        # 格式: "00:00:01,000"
        match = re.match(r'(\d+):(\d+):(\d+),(\d+)', time_str.strip())
        if match:
            h, m, s, ms = map(int, match.groups())
            return h * 3600000 + m * 60000 + s * 1000 + ms
        return 0


@dataclass
class SRTContent:
    """SRT 文件解析结果"""
    subtitles: List[Subtitle]
    full_text: str
    duration_ms: int
    word_count: int

    def get_summary(self, max_words: int = 200) -> str:
        """获取字幕摘要"""
        words = self.full_text.split()
        if len(words) <= max_words:
            return self.full_text
        return ' '.join(words[:max_words]) + '...'

    def get_key_moments(self, n: int = 5) -> List[str]:
        """获取关键片段（均匀分布的字幕）"""
        if not self.subtitles:
            return []
        if len(self.subtitles) <= n:
            return [s.text for s in self.subtitles]

        step = len(self.subtitles) // n
        return [self.subtitles[i * step].text for i in range(n)]

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'subtitles': [asdict(s) for s in self.subtitles],
            'full_text': self.full_text,
            'duration_ms': self.duration_ms,
            'word_count': self.word_count,
            'summary': self.get_summary(),
            'key_moments': self.get_key_moments()
        }


class SRTParser:
    """SRT 字幕解析器"""

    # SRT 时间戳格式: "00:00:01,000 --> 00:00:04,000"
    TIME_PATTERN = re.compile(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})')

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def parse(self) -> SRTContent:
        """解析 SRT 文件"""
        if not self.file_path.exists():
            raise FileNotFoundError(f"SRT 文件不存在: {self.file_path}")

        content = self.file_path.read_text(encoding='utf-8')
        return self._parse_content(content)

    def _parse_content(self, content: str) -> SRTContent:
        """解析 SRT 内容字符串"""
        subtitles = []
        blocks = re.split(r'\n\s*\n', content.strip())

        for block in blocks:
            if not block.strip():
                continue

            subtitle = self._parse_block(block)
            if subtitle:
                subtitles.append(subtitle)

        if not subtitles:
            raise ValueError("未能解析到任何字幕内容")

        # 计算总时长
        duration_ms = subtitles[-1].end_ms if subtitles else 0

        # 提取全文
        full_text = '\n'.join(s.text for s in subtitles)

        return SRTContent(
            subtitles=subtitles,
            full_text=full_text,
            duration_ms=duration_ms,
            word_count=len(full_text.split())
        )

    def _parse_block(self, block: str) -> Optional[Subtitle]:
        """解析单个字幕块"""
        lines = block.strip().split('\n')
        if len(lines) < 3:
            return None

        try:
            # 第一行是序号
            index = int(lines[0].strip())

            # 第二行是时间戳
            time_match = self.TIME_PATTERN.match(lines[1].strip())
            if not time_match:
                return None

            start_time, end_time = time_match.groups()

            # 剩余行是字幕文本
            text = '\n'.join(lines[2:]).strip()
            # 移除常见的 HTML 标签
            text = re.sub(r'<[^>]+>', '', text)

            return Subtitle(
                index=index,
                start_time=start_time,
                end_time=end_time,
                text=text
            )
        except (ValueError, IndexError):
            return None


def find_video_file(srt_path: str, extensions: List[str] = None) -> Optional[Path]:
    """根据 SRT 文件路径查找同名视频文件

    优先选择 MOV 格式（质量更高），其次是 MP4，最后是其他格式。

    Args:
        srt_path: SRT 文件路径
        extensions: 支持的视频扩展名列表

    Returns:
        视频文件路径，如果未找到则返回 None
    """
    if extensions is None:
        # 按优先级排序：MOV > MP4 > 其他
        extensions = ['.mov', '.mp4', '.avi', '.mkv', '.flv', '.wmv']

    srt_path = Path(srt_path)
    base_name = srt_path.stem  # 获取不带扩展名的文件名
    parent_dir = srt_path.parent

    # 收集所有存在的视频文件
    found_videos = []
    for ext in extensions:
        video_path = parent_dir / f"{base_name}{ext}"
        if video_path.exists():
            found_videos.append(video_path)

    # 按优先级返回第一个找到的视频文件
    if found_videos:
        return found_videos[0]

    return None


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='解析 SRT 字幕文件')
    parser.add_argument('srt_file', help='SRT 字幕文件路径')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    parser.add_argument('--find-video', action='store_true', help='查找同名视频文件')

    args = parser.parse_args()

    try:
        srt_parser = SRTParser(args.srt_file)
        result = srt_parser.parse()

        print(f"📹 SRT 文件解析成功: {args.srt_file}")
        print(f"⏱️  时长: {result.duration_ms / 1000:.1f} 秒")
        print(f"📝 字数: {result.word_count} 字")
        print(f"🎬 字幕条数: {len(result.subtitles)} 条")
        print(f"\n📄 全文预览:")
        print(result.get_summary(300))

        # 查找文件
        video_path = find_video_file(args.srt_file) if args.find_video or args.json else None

        if args.find_video:
            if video_path:
                print(f"\n🎥 找到视频文件: {video_path}")
            else:
                print(f"\n⚠️  未找到同名视频文件")

        if args.json:
            print('\n' + '='*50)
            output_data = result.to_dict()
            # 添加文件查找结果到 JSON 输出
            output_data['files'] = {
                'video': str(video_path) if video_path else None
            }
            print(json.dumps(output_data, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"❌ 解析失败: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
