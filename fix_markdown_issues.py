#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复 Markdown 文件中的 Vue 模板解析错误

问题类型：
1. 标题行末尾的多余 # 符号
2. 缺少语言标识的代码块
3. 多余的"复制"文本行
4. 语法错误（如 <key<value>）
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class MarkdownFixer:
    """Markdown 文件修复器"""

    def __init__(self, articles_dir: str):
        self.articles_dir = Path(articles_dir)
        self.fixed_files: List[str] = []
        self.error_files: List[Dict] = []
        self.stats = {
            'total_files': 0,
            'fixed_files': 0,
            'heading_fixes': 0,
            'code_block_fixes': 0,
            'copy_text_removes': 0,
            'syntax_fixes': 0
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
        file_fixed = False

        # 1. 修复标题行末尾的多余 #
        content, heading_count = self.fix_heading_hashes(content)
        if heading_count > 0:
            self.stats['heading_fixes'] += heading_count
            file_fixed = True

        # 2. 修复代码块
        content, code_block_count = self.fix_code_blocks(content)
        if code_block_count > 0:
            self.stats['code_block_fixes'] += code_block_count
            file_fixed = True

        # 3. 删除"复制"文本行
        content, copy_count = self.remove_copy_text(content)
        if copy_count > 0:
            self.stats['copy_text_removes'] += copy_count
            file_fixed = True

        # 4. 修复语法错误
        content, syntax_count = self.fix_syntax_errors(content)
        if syntax_count > 0:
            self.stats['syntax_fixes'] += syntax_count
            file_fixed = True

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

    def fix_code_blocks(self, content: str) -> Tuple[str, int]:
        """修复代码块标记"""
        count = 0
        lines = content.split('\n')
        fixed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # 检测可能的代码块开始（缺少语言标识）
            # 模式：前面有空行或特定文本，然后是缩进的代码
            if i > 0 and self.is_code_line(line) and not self.in_code_block(fixed_lines):
                # 检查是否是裸代码块（没有 ``` 标记）
                prev_line = lines[i-1].strip() if i > 0 else ''

                # 如果前一行是空行或者是描述性文本，可能需要添加代码块
                if prev_line == '' or self.is_description_line(prev_line):
                    # 收集连续的代码行
                    code_lines = []
                    j = i
                    while j < len(lines) and (self.is_code_line(lines[j]) or lines[j].strip() == ''):
                        code_lines.append(lines[j])
                        j += 1
                        if lines[j-1].strip() == '' and j < len(lines) and not self.is_code_line(lines[j]):
                            break

                    # 如果收集到了代码行，添加代码块标记
                    if code_lines and any(l.strip() for l in code_lines):
                        lang = self.detect_language(code_lines)
                        fixed_lines.append(f'```{lang}')
                        fixed_lines.extend(code_lines)
                        fixed_lines.append('```')
                        i = j
                        count += 1
                        continue

            fixed_lines.append(line)
            i += 1

        return '\n'.join(fixed_lines), count

    def is_code_line(self, line: str) -> bool:
        """判断是否是代码行"""
        stripped = line.strip()
        if not stripped:
            return False

        # 代码行的特征
        code_indicators = [
            line.startswith('    '),  # 4空格缩进
            line.startswith('\t'),     # tab缩进
            re.match(r'^\s*(class|def|import|from|export|const|let|var|function|if|for|while|#|//|gcloud|kubectl|docker)', line),
            '=' in stripped and not stripped.startswith('#'),
            stripped.endswith(('{', '}', ';', ':', ',', '(', ')')),
            re.match(r'^\s*[\w\-]+:', line),  # YAML style
        ]

        return any(code_indicators)

    def is_description_line(self, line: str) -> bool:
        """判断是否是描述性文本行"""
        return bool(re.match(r'^[#\*\-]|\d+\.', line))

    def in_code_block(self, lines: List[str]) -> bool:
        """检查当前是否在代码块中"""
        code_fence_count = sum(1 for line in lines if line.strip().startswith('```'))
        return code_fence_count % 2 == 1

    def detect_language(self, code_lines: List[str]) -> str:
        """检测代码语言"""
        code = '\n'.join(code_lines)

        # Python
        if re.search(r'\b(def|class|import|from)\b', code):
            return 'python'

        # Bash/Shell
        if re.search(r'\b(gcloud|kubectl|docker|export|echo|cd|ls)\b', code) or code.strip().startswith('#!'):
            return 'bash'

        # JavaScript/TypeScript
        if re.search(r'\b(const|let|var|function|export|import)\b', code) or '=>' in code:
            return 'javascript'

        # YAML
        if re.search(r'^\s*[\w\-]+:\s*$', code, re.MULTILINE):
            return 'yaml'

        # JSON
        if re.search(r'^\s*[{[]', code.strip()):
            return 'json'

        return ''

    def remove_copy_text(self, content: str) -> Tuple[str, int]:
        """删除"复制"文本行"""
        count = 0
        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            # 删除单独的"复制"行
            if line.strip() in ['复制', 'copy', 'Copy']:
                count += 1
                continue
            fixed_lines.append(line)

        return '\n'.join(fixed_lines), count

    def fix_syntax_errors(self, content: str) -> Tuple[str, int]:
        """修复常见语法错误"""
        count = 0

        # 修复 <key<value> 类型的错误
        fixed_content = content

        # 模式1: <key<value> -> <key> <value>
        pattern1 = r'<(\w+)<(\w+)>'
        matches = re.findall(pattern1, fixed_content)
        if matches:
            count += len(matches)
            fixed_content = re.sub(pattern1, r'<\1> <\2>', fixed_content)

        # 模式2: >value> -> > value>
        pattern2 = r'>(\w+)>'
        matches = re.findall(pattern2, fixed_content)
        if matches:
            count += len(matches)
            fixed_content = re.sub(pattern2, r'> \1>', fixed_content)

        return fixed_content, count

    def print_summary(self):
        """打印修复摘要"""
        print("\n" + "="*60)
        print("修复摘要")
        print("="*60)
        print(f"总文件数: {self.stats['total_files']}")
        print(f"已修复文件数: {self.stats['fixed_files']}")
        print(f"标题修复数: {self.stats['heading_fixes']}")
        print(f"代码块修复数: {self.stats['code_block_fixes']}")
        print(f"删除'复制'文本数: {self.stats['copy_text_removes']}")
        print(f"语法错误修复数: {self.stats['syntax_fixes']}")

        if self.error_files:
            print(f"\n错误文件数: {len(self.error_files)}")
            for err in self.error_files:
                print(f"  - {err['file']}: {err['error']}")

        if self.fixed_files:
            print(f"\n已修复的文件列表:")
            for file in self.fixed_files:
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

    fixer = MarkdownFixer(str(articles_dir))
    fixer.fix_all_files()


if __name__ == '__main__':
    main()
