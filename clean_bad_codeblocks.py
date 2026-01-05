#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理错误的代码块标记
移除包裹 Markdown 内容的错误代码块标记
"""

import os
import sys
import re
from pathlib import Path

# 设置 stdout 编码为 utf-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def clean_bad_code_blocks(content):
    """清理错误的代码块标记"""
    lines = content.split('\n')
    cleaned_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 检测空代码块标记
        if stripped == '```':
            # 查看前后内容判断是否应该删除
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()

                # 如果下一行是标题或列表，这个代码块标记应该删除
                if next_line.startswith('#') or next_line.startswith('**') or next_line == '':
                    # 查找配对的结束标记
                    j = i + 1
                    found_end = False
                    end_pos = -1

                    while j < len(lines) and j < i + 20:  # 最多向前看20行
                        if lines[j].strip() == '```':
                            found_end = True
                            end_pos = j
                            break
                        # 如果中间有真正的代码块开始，就停止
                        if lines[j].strip().startswith('```') and lines[j].strip() != '```':
                            break
                        j += 1

                    # 如果找到配对的结束标记，删除这一对
                    if found_end and end_pos > 0:
                        # 检查中间内容是否都是 Markdown 而不是代码
                        middle_content = '\n'.join(lines[i+1:end_pos])
                        # 如果中间有标题、列表或其他 Markdown 格式，就删除这对标记
                        if any(re.match(r'^#+\s', l.strip()) or
                               l.strip().startswith('**') or
                               re.match(r'^\s*[\*\-\+\d\.]\s', l.strip())
                               for l in lines[i+1:end_pos]):
                            # 跳过开始标记
                            i += 1
                            # 添加中间内容
                            while i < end_pos:
                                cleaned_lines.append(lines[i])
                                i += 1
                            # 跳过结束标记
                            i += 1
                            continue

        cleaned_lines.append(line)
        i += 1

    return '\n'.join(cleaned_lines)


def fix_code_block_languages(content):
    """修复代码块语言标识"""
    lines = content.split('\n')
    fixed_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # 修复错误的语言标识
        if stripped.startswith('```'):
            lang = stripped[3:].strip()

            # 修复常见错误
            if lang == 'python' and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                # 检查是否实际上是其他语言
                if next_line.startswith('javascript') or next_line.startswith('java'):
                    line = '```' + next_line
                    # 需要跳过下一行
                    if i + 1 < len(lines):
                        lines[i + 1] = ''

        fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def clean_article_file(file_path):
    """清理单个文章文件"""
    try:
        print(f"正在清理: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # 清理错误的代码块
        content = clean_bad_code_blocks(content)
        content = fix_code_block_languages(content)

        # 只有内容变化时才写入
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] 已清理: {file_path}")
            return True
        else:
            print(f"[SKIP] 无需清理: {file_path}")
            return False

    except Exception as e:
        print(f"[ERROR] 清理失败: {file_path}")
        print(f"  错误: {str(e)}")
        return False


def clean_all_articles(base_dir, language='zh'):
    """批量清理所有文章"""
    articles_dir = Path(base_dir) / 'docs' / language / 'articles'

    if not articles_dir.exists():
        print(f"错误: 目录不存在 {articles_dir}")
        return

    md_files = sorted(articles_dir.glob('*.md'))

    print(f"\n开始清理 {len(md_files)} 篇文章...")
    print(f"语言: {language}")
    print(f"目录: {articles_dir}\n")

    cleaned_count = 0

    for md_file in md_files:
        if clean_article_file(md_file):
            cleaned_count += 1

    print(f"\n清理完成!")
    print(f"总文章数: {len(md_files)}")
    print(f"已清理: {cleaned_count}")
    print(f"无需清理: {len(md_files) - cleaned_count}")


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    language = sys.argv[1] if len(sys.argv) > 1 else 'zh'
    clean_all_articles(base_dir, language)
