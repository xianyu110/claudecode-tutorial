#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简体中文到繁体中文转换脚本
使用 OpenCC 进行简繁转换，保持代码块、链接、格式不变
"""

import os
import re
import shutil
import sys
from pathlib import Path

# 设置标准输出编码为 UTF-8
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    import opencc
except ImportError:
    print("正在安装 opencc-python-reimplemented...")
    os.system("pip install opencc-python-reimplemented")
    import opencc

def convert_to_traditional(text: str, converter) -> str:
    """
    将文本转换为繁体中文，保护代码块和链接不被转换
    """
    # 保护代码块
    code_blocks = []
    inline_codes = []

    # 提取并保护代码块 ```...```
    def save_code_block(match):
        code_blocks.append(match.group(0))
        return f"<<<CODE_BLOCK_{len(code_blocks)-1}>>>"

    text = re.sub(r'```[\s\S]*?```', save_code_block, text)

    # 提取并保护行内代码 `...`
    def save_inline_code(match):
        inline_codes.append(match.group(0))
        return f"<<<INLINE_CODE_{len(inline_codes)-1}>>>"

    text = re.sub(r'`[^`]+`', save_inline_code, text)

    # 保护URL链接
    urls = []
    def save_url(match):
        urls.append(match.group(0))
        return f"<<<URL_{len(urls)-1}>>>"

    text = re.sub(r'https?://[^\s\)]+', save_url, text)

    # 转换为繁体中文
    text = converter.convert(text)

    # 恢复代码块 - 使用更灵活的匹配方式以处理OpenCC可能修改的占位符
    for i, code_block in enumerate(code_blocks):
        # 首先尝试精确匹配
        placeholder = f"<<<CODE_BLOCK_{i}>>>"
        if placeholder in text:
            text = text.replace(placeholder, code_block)
        else:
            # 如果精确匹配失败，尝试用正则表达式匹配（处理OpenCC可能的转换）
            pattern = f"<<<CODE_BLOCK_{i}>>>.*?(?=\n|$)"
            # 查找并替换占位符及其后面可能跟着的文本
            matches = re.finditer(pattern, text, re.DOTALL | re.MULTILINE)
            for match in matches:
                text = text.replace(match.group(0), code_block)

    # 恢复行内代码
    for i, inline_code in enumerate(inline_codes):
        text = text.replace(f"<<<INLINE_CODE_{i}>>>", inline_code)

    # 恢复URL
    for i, url in enumerate(urls):
        text = text.replace(f"<<<URL_{i}>>>", url)

    return text

def process_markdown_file(src_file: Path, dst_file: Path, converter):
    """处理单个 Markdown 文件"""
    try:
        # 读取源文件（UTF-8 编码）
        with open(src_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 转换为繁体中文
        converted_content = convert_to_traditional(content, converter)

        # 确保目标目录存在
        dst_file.parent.mkdir(parents=True, exist_ok=True)

        # 写入目标文件（UTF-8 编码，无 BOM）
        with open(dst_file, 'w', encoding='utf-8') as f:
            f.write(converted_content)

        print(f"✓ 已转换: {src_file.name}")
        return True
    except Exception as e:
        print(f"✗ 转换失败 {src_file}: {e}")
        return False

def copy_directory_structure(src_dir: Path, dst_dir: Path, converter):
    """
    复制目录结构并转换所有 Markdown 文件
    """
    success_count = 0
    fail_count = 0

    # 创建目标目录
    dst_dir.mkdir(parents=True, exist_ok=True)

    # 遍历源目录
    for root, dirs, files in os.walk(src_dir):
        root_path = Path(root)
        relative_path = root_path.relative_to(src_dir)
        target_root = dst_dir / relative_path

        # 创建目标子目录
        target_root.mkdir(parents=True, exist_ok=True)

        # 处理文件
        for file in files:
            src_file = root_path / file
            dst_file = target_root / file

            if file.endswith('.md'):
                # Markdown 文件：转换内容
                if process_markdown_file(src_file, dst_file, converter):
                    success_count += 1
                else:
                    fail_count += 1
            else:
                # 其他文件：直接复制
                try:
                    shutil.copy2(src_file, dst_file)
                    print(f"✓ 已复制: {file}")
                except Exception as e:
                    print(f"✗ 复制失败 {file}: {e}")
                    fail_count += 1

    return success_count, fail_count

def main():
    """主函数"""
    print("=" * 60)
    print("简体中文 → 繁体中文转换工具")
    print("=" * 60)

    # 初始化 OpenCC 转换器（简体到繁体台湾标准）
    print("\n正在初始化 OpenCC 转换器...")
    converter = opencc.OpenCC('s2twp')  # 简体到繁体（台湾正体，含常用词汇）
    print("✓ OpenCC 转换器初始化成功")

    # 设置路径
    project_root = Path(__file__).parent
    zh_dir = project_root / "docs" / "zh"
    tw_dir = project_root / "docs" / "tw"

    print(f"\n源目录: {zh_dir}")
    print(f"目标目录: {tw_dir}")

    if not zh_dir.exists():
        print(f"\n错误: 源目录不存在: {zh_dir}")
        return

    # 如果目标目录已存在，询问是否覆盖
    if tw_dir.exists():
        print(f"\n警告: 目标目录已存在，将被覆盖")
        shutil.rmtree(tw_dir)

    print("\n开始转换...")
    print("-" * 60)

    # 执行转换
    success_count, fail_count = copy_directory_structure(zh_dir, tw_dir, converter)

    print("-" * 60)
    print(f"\n转换完成!")
    print(f"  成功: {success_count} 个文件")
    print(f"  失败: {fail_count} 个文件")
    print("=" * 60)

if __name__ == "__main__":
    main()
