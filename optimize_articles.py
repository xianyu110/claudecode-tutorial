#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文章排版优化脚本
用于优化 Markdown 文章的格式和排版
"""

import os
import re
import sys
from pathlib import Path

# 设置 stdout 编码为 utf-8，避免 Windows 下的编码问题
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def optimize_markdown(content):
    """优化 Markdown 内容的排版"""
    lines = content.split('\n')
    optimized_lines = []
    in_code_block = False
    code_block_lang = ""
    prev_line_type = None  # 'heading', 'list', 'text', 'empty', 'code'

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 检测代码块
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            if in_code_block:
                # 提取语言标识
                code_block_lang = stripped[3:].strip()

            # 代码块前后添加空行
            if optimized_lines and optimized_lines[-1].strip() != '':
                optimized_lines.append('')
            optimized_lines.append(line)
            prev_line_type = 'code'
            i += 1
            continue

        # 在代码块内，不做处理
        if in_code_block:
            optimized_lines.append(line)
            i += 1
            continue

        # 标题处理
        if stripped.startswith('#'):
            # 标题前后添加空行（除非是文件开头）
            if optimized_lines and optimized_lines[-1].strip() != '':
                optimized_lines.append('')
            optimized_lines.append(line)
            # 标题后添加空行（如果下一行不是空行）
            if i + 1 < len(lines) and lines[i + 1].strip() != '':
                optimized_lines.append('')
            prev_line_type = 'heading'
            i += 1
            continue

        # 列表项处理
        if re.match(r'^\s*[\*\-\+\d\.]\s+', stripped):
            # 如果前一行不是列表项也不是空行，添加空行
            if prev_line_type not in ['list', 'empty'] and optimized_lines:
                optimized_lines.append('')
            optimized_lines.append(line)
            prev_line_type = 'list'
            i += 1
            continue

        # 空行处理 - 移除多余的连续空行
        if stripped == '':
            if not optimized_lines or optimized_lines[-1].strip() != '':
                optimized_lines.append(line)
            prev_line_type = 'empty'
            i += 1
            continue

        # 表格行
        if '|' in stripped and (stripped.startswith('|') or '---|' in stripped):
            optimized_lines.append(line)
            prev_line_type = 'table'
            i += 1
            continue

        # 普通文本
        # 段落前添加空行（如果前一行不是空行且不是列表项）
        if prev_line_type not in ['empty', 'text'] and prev_line_type is not None:
            if optimized_lines and optimized_lines[-1].strip() != '':
                optimized_lines.append('')

        optimized_lines.append(line)
        prev_line_type = 'text'
        i += 1

    return '\n'.join(optimized_lines)


def fix_code_blocks(content):
    """修复代码块标记问题"""
    lines = content.split('\n')
    fixed_lines = []
    in_code_block = False
    skip_mode = False

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 检测孤立的代码块标记（没有语言标识）
        if stripped == '```':
            # 检查是否是错误的代码块（包裹了 Markdown 标题等内容）
            if not in_code_block and i + 1 < len(lines):
                next_line = lines[i + 1].strip()

                # 如果下一行是标题或者空行，这可能是错误的代码块标记
                if next_line.startswith('#') or next_line == '':
                    # 检查后续内容，找到配对的代码块结束标记
                    j = i + 1
                    found_end = False
                    while j < len(lines):
                        if lines[j].strip() == '```':
                            found_end = True
                            # 删除这对错误的代码块标记
                            skip_mode = True
                            i += 1  # 跳过开始标记
                            continue
                        j += 1

                    if found_end:
                        i += 1
                        continue

            in_code_block = not in_code_block

            # 如果是代码块开始，尝试推断语言
            if in_code_block and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                # 根据下一行内容推断语言
                if next_line.startswith('def ') or next_line.startswith('import ') or 'python' in next_line.lower():
                    line = '```python'
                elif next_line.startswith('function ') or next_line.startswith('const ') or next_line.startswith('let ') or next_line.startswith('var '):
                    line = '```javascript'
                elif (next_line.startswith('public ') or next_line.startswith('private ')) and 'class' in next_line:
                    line = '```java'
                elif '{' in next_line and '"' in next_line and ':' in next_line:
                    line = '```json'
                elif next_line.startswith('$') or next_line.startswith('npm ') or next_line.startswith('node ') or next_line.startswith('git '):
                    line = '```bash'
                elif 'http_version' in next_line or 'server_name' in next_line:
                    line = '```nginx'
                elif next_line.startswith('<') and '>' in next_line:
                    line = '```html'

        fixed_lines.append(line)
        i += 1

    return '\n'.join(fixed_lines)


def clean_empty_lines(content):
    """清理多余的空行"""
    # 移除文件开头的空行
    content = content.lstrip('\n')

    # 移除文件结尾多余的空行，只保留一个
    content = content.rstrip('\n') + '\n'

    # 移除连续的多个空行，最多保留两个
    content = re.sub(r'\n{4,}', '\n\n\n', content)

    return content


def optimize_article_file(file_path):
    """优化单个文章文件"""
    try:
        print(f"正在优化: {file_path}")

        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 保存原始内容以便比较
        original_content = content

        # 应用优化
        content = fix_code_blocks(content)
        content = optimize_markdown(content)
        content = clean_empty_lines(content)

        # 只有内容变化时才写入
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] 已优化: {file_path}")
            return True
        else:
            print(f"[SKIP] 无需优化: {file_path}")
            return False

    except Exception as e:
        print(f"[ERROR] 优化失败: {file_path}")
        print(f"  错误: {str(e)}")
        return False


def optimize_all_articles(base_dir, language='zh'):
    """批量优化所有文章"""
    articles_dir = Path(base_dir) / 'docs' / language / 'articles'

    if not articles_dir.exists():
        print(f"错误: 目录不存在 {articles_dir}")
        return

    # 获取所有 Markdown 文件
    md_files = sorted(articles_dir.glob('*.md'))

    print(f"\n开始优化 {len(md_files)} 篇文章...")
    print(f"语言: {language}")
    print(f"目录: {articles_dir}\n")

    optimized_count = 0

    for md_file in md_files:
        if optimize_article_file(md_file):
            optimized_count += 1

    print(f"\n优化完成!")
    print(f"总文章数: {len(md_files)}")
    print(f"已优化: {optimized_count}")
    print(f"无需优化: {len(md_files) - optimized_count}")


if __name__ == '__main__':
    import sys

    # 获取项目根目录
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # 支持命令行参数指定语言
    language = sys.argv[1] if len(sys.argv) > 1 else 'zh'

    optimize_all_articles(base_dir, language)
