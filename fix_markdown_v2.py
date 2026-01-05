#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复 Markdown 文件中的 Vue 模板解析错误 - 改进版本

问题类型：
1. 标题行末尾的多余 # 符号
2. "复制"文本行
3. 语法错误
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class MarkdownFixerV2:
    """Markdown 文件修复器 V2"""

    def __init__(self, articles_dir: str):
        self.articles_dir = Path(articles_dir)
        self.fixed_files: List[str] = []
        self.error_files: List[Dict] = []
        self.stats = {
            'total_files': 0,
            'fixed_files': 0,
            'heading_fixes': 0,
            'copy_text_removes': 0,
            'syntax_fixes': 0,
            'bad_code_fence_fixes': 0
        }

    def fix_all_files(self):
        """修复所有文件"""
        md_files = sorted(self.articles_dir.glob('*.md'))
        self.stats['total_files'] = len(md_files)

        print(f"找到 {len(md_files)} 个 Markdown 文件")

        for md_file in md_files:
            try:
                self.fix_file(md_file)
            except Exception as e:
                self.error_files.append({
                    'file': str(md_file),
                    'error': str(e)
                })
                print(f"[ERROR] 错误: {md_file.name} - {e}")

        self.print_summary()

    def fix_file(self, file_path: Path) -> bool:
        """修复单个文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # 1. 修复标题行末尾的多余 #
        content, heading_count = self.fix_heading_hashes(content)
        if heading_count > 0:
            self.stats['heading_fixes'] += heading_count

        # 2. 删除"复制"文本行
        content, copy_count = self.remove_copy_text(content)
        if copy_count > 0:
            self.stats['copy_text_removes'] += copy_count

        # 3. 修复语法错误
        content, syntax_count = self.fix_syntax_errors(content)
        if syntax_count > 0:
            self.stats['syntax_fixes'] += syntax_count

        # 4. 移除错误的代码围栏（只包含标题的代码块）
        content, bad_fence_count = self.remove_bad_code_fences(content)
        if bad_fence_count > 0:
            self.stats['bad_code_fence_fixes'] += bad_fence_count

        # 只有在内容确实改变时才写入
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.fixed_files.append(str(file_path))
            self.stats['fixed_files'] += 1
            print(f"[OK] 已修复: {file_path.name}")
            return True

        return False

    def fix_heading_hashes(self, content: str) -> Tuple[str, int]:
        """修复标题行末尾的多余 # 符号"""
        count = 0
        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            # 匹配标题行末尾有多余 # 的情况
            # 例如: ## 标题#  或  ### 标题 ##
            match = re.match(r'^(#{1,6})\s+(.+?)\s*#+\s*$', line)
            if match:
                level = match.group(1)
                title = match.group(2).strip()
                fixed_lines.append(f"{level} {title}")
                count += 1
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines), count

    def remove_copy_text(self, content: str) -> Tuple[str, int]:
        """删除"复制"文本行"""
        count = 0
        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            # 删除单独的"复制"行或只有缩进+"复制"的行
            if line.strip() in ['复制', 'copy', 'Copy']:
                count += 1
                continue
            fixed_lines.append(line)

        return '\n'.join(fixed_lines), count

    def fix_syntax_errors(self, content: str) -> Tuple[str, int]:
        """修复常见语法错误"""
        count = 0
        fixed_content = content

        # 修复 <key<value> 类型的错误
        # 模式1: <key<value> -> <key> <value>
        pattern1 = r'<(\w+)<(\w+)>'
        matches = re.findall(pattern1, fixed_content)
        if matches:
            count += len(matches)
            fixed_content = re.sub(pattern1, r'<\1> <\2>', fixed_content)

        # 模式2: >value> -> > value>
        pattern2 = r'>(\w+)>'
        if not re.search(r'```', fixed_content):  # 避免在代码块中误修复
            matches = re.findall(pattern2, fixed_content)
            if matches:
                count += len(matches)
                fixed_content = re.sub(pattern2, r'> \1>', fixed_content)

        return fixed_content, count

    def remove_bad_code_fences(self, content: str) -> Tuple[str, int]:
        """移除错误的代码围栏（只包含标题的代码块）"""
        count = 0
        lines = content.split('\n')
        fixed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # 检测模式: ```\n## 标题\n```
            if line.strip() == '```' and i + 2 < len(lines):
                next_line = lines[i + 1]
                next_next_line = lines[i + 2] if i + 2 < len(lines) else ''

                # 如果下一行是标题，再下一行是 ```，删除这些围栏
                if re.match(r'^#{1,6}\s+', next_line) and next_next_line.strip() == '```':
                    # 只保留标题行
                    fixed_lines.append(next_line)
                    i += 3
                    count += 1
                    continue

                # 检测模式: ```\n### 标题\n``` （中间可能有空行）
                elif re.match(r'^#{1,6}\s+', next_line):
                    # 查找下一个 ```
                    j = i + 2
                    found_closing = False
                    while j < len(lines) and j < i + 5:  # 最多向前看5行
                        if lines[j].strip() == '```':
                            # 检查中间是否只有标题和空行
                            middle_lines = lines[i+1:j]
                            if all(not l.strip() or re.match(r'^#{1,6}\s+', l) for l in middle_lines):
                                # 只保留非空的标题行
                                for ml in middle_lines:
                                    if ml.strip():
                                        fixed_lines.append(ml)
                                i = j + 1
                                count += 1
                                found_closing = True
                                break
                        j += 1

                    if found_closing:
                        continue

            fixed_lines.append(line)
            i += 1

        return '\n'.join(fixed_lines), count

    def print_summary(self):
        """打印修复摘要"""
        print("\n" + "="*60)
        print("修复摘要")
        print("="*60)
        print(f"总文件数: {self.stats['total_files']}")
        print(f"已修复文件数: {self.stats['fixed_files']}")
        print(f"标题修复数: {self.stats['heading_fixes']}")
        print(f"删除'复制'文本数: {self.stats['copy_text_removes']}")
        print(f"语法错误修复数: {self.stats['syntax_fixes']}")
        print(f"错误代码围栏修复数: {self.stats['bad_code_fence_fixes']}")

        if self.error_files:
            print(f"\n错误文件数: {len(self.error_files)}")
            for err in self.error_files:
                print(f"  - {err['file']}: {err['error']}")

        if self.fixed_files:
            print(f"\n已修复的文件列表 (共 {len(self.fixed_files)} 个):")
            for file in sorted(self.fixed_files):
                print(f"  - {Path(file).name}")

        print("="*60)


def main():
    """主函数"""
    # 获取文章目录路径
    script_dir = Path(__file__).parent
    articles_dir = script_dir / 'docs' / 'zh' / 'articles'

    if not articles_dir.exists():
        print(f"错误: 目录不存在: {articles_dir}")
        sys.exit(1)

    print(f"开始修复 {articles_dir} 中的 Markdown 文件...")
    print()

    fixer = MarkdownFixerV2(str(articles_dir))
    fixer.fix_all_files()


if __name__ == '__main__':
    main()
