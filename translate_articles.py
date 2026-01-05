#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI批量翻译脚本
将docs/zh/articles下的中文文章翻译为英文并保存到docs/en/articles
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Optional

# 设置 Windows 控制台编码为 UTF-8
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


class ArticleTranslator:
    """文章翻译器"""

    def __init__(self, api_key: Optional[str] = None, provider: str = "anthropic"):
        """
        初始化翻译器

        Args:
            api_key: API密钥（如果不提供，将从环境变量读取）
            provider: 翻译服务提供商 (anthropic, openai, 或 local)
        """
        self.provider = provider
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")

        self.zh_dir = Path("docs/zh/articles")
        self.en_dir = Path("docs/en/articles")
        self.en_dir.mkdir(parents=True, exist_ok=True)

        # 翻译进度文件
        self.progress_file = Path("translation_progress.json")
        self.load_progress()

        # 初始化翻译客户端
        self.client = None
        if self.provider == "anthropic" and self.api_key:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
                print(f"✓ 使用 Anthropic Claude API")
            except ImportError:
                print("⚠ 未安装 anthropic 库，请运行: pip install anthropic")
        elif self.provider == "openai" and self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                print(f"✓ 使用 OpenAI API")
            except ImportError:
                print("⚠ 未安装 openai 库，请运行: pip install openai")

    def load_progress(self):
        """加载翻译进度"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                self.progress = json.load(f)
        else:
            self.progress = {"translated": [], "failed": []}

    def save_progress(self):
        """保存翻译进度"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)

    def translate_with_anthropic(self, text: str) -> str:
        """使用Anthropic Claude翻译"""
        if not self.client:
            raise ValueError("Anthropic client未初始化")

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8000,
            messages=[
                {
                    "role": "user",
                    "content": f"""请将以下Markdown格式的中文技术文档翻译为英文。要求：
1. 保持Markdown格式不变
2. 保持专业的技术术语翻译
3. 保持代码块、链接、图片等不变
4. 翻译要准确、流畅、专业
5. 保持原文的段落结构

需要翻译的内容：

{text}"""
                }
            ]
        )

        return message.content[0].text

    def translate_with_openai(self, text: str) -> str:
        """使用OpenAI翻译"""
        if not self.client:
            raise ValueError("OpenAI client未初始化")

        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional translator specializing in technical documentation. Translate Chinese to English while maintaining Markdown formatting, code blocks, and technical accuracy."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            max_tokens=8000
        )

        return response.choices[0].message.content

    def translate_text(self, text: str) -> str:
        """翻译文本"""
        if self.provider == "anthropic":
            return self.translate_with_anthropic(text)
        elif self.provider == "openai":
            return self.translate_with_openai(text)
        else:
            raise ValueError(f"不支持的翻译提供商: {self.provider}")

    def translate_article(self, zh_file: Path, retry: int = 3) -> bool:
        """
        翻译单篇文章

        Args:
            zh_file: 中文文章文件路径
            retry: 重试次数

        Returns:
            是否成功
        """
        try:
            # 读取中文文章
            with open(zh_file, 'r', encoding='utf-8') as f:
                zh_content = f.read()

            print(f"\n正在翻译: {zh_file.name}")
            print(f"  文章长度: {len(zh_content)} 字符")

            # 翻译
            for attempt in range(retry):
                try:
                    en_content = self.translate_text(zh_content)
                    break
                except Exception as e:
                    if attempt < retry - 1:
                        print(f"  ⚠ 翻译失败，{3}秒后重试 ({attempt + 1}/{retry}): {str(e)}")
                        time.sleep(3)
                    else:
                        raise

            # 保存英文文章
            en_file = self.en_dir / zh_file.name
            with open(en_file, 'w', encoding='utf-8') as f:
                f.write(en_content)

            print(f"  ✓ 翻译成功: {en_file.name}")

            # 更新进度
            self.progress["translated"].append(zh_file.name)
            if zh_file.name in self.progress["failed"]:
                self.progress["failed"].remove(zh_file.name)
            self.save_progress()

            # 礼貌性延迟
            time.sleep(2)

            return True

        except Exception as e:
            print(f"  ✗ 翻译失败: {zh_file.name}")
            print(f"    错误: {str(e)}")

            # 记录失败
            if zh_file.name not in self.progress["failed"]:
                self.progress["failed"].append(zh_file.name)
            self.save_progress()

            return False

    def translate_all(self, skip_existing: bool = True):
        """翻译所有文章"""
        # 获取所有中文文章
        zh_files = sorted(self.zh_dir.glob("*.md"))
        total = len(zh_files)

        print(f"找到 {total} 篇中文文章")
        print(f"已翻译: {len(self.progress['translated'])} 篇")
        print(f"失败: {len(self.progress['failed'])} 篇")
        print("=" * 60)

        success_count = 0
        failed_count = 0
        skipped_count = 0

        for i, zh_file in enumerate(zh_files, 1):
            # 检查是否已翻译
            if skip_existing and zh_file.name in self.progress["translated"]:
                en_file = self.en_dir / zh_file.name
                if en_file.exists():
                    print(f"[{i}/{total}] ⊙ 跳过已翻译: {zh_file.name}")
                    skipped_count += 1
                    continue

            print(f"\n[{i}/{total}] 翻译进度: {i}/{total} ({i/total*100:.1f}%)")

            if self.translate_article(zh_file):
                success_count += 1
            else:
                failed_count += 1

        # 打印统计
        print("\n" + "=" * 60)
        print("翻译完成！")
        print(f"  成功: {success_count} 篇")
        print(f"  失败: {failed_count} 篇")
        print(f"  跳过: {skipped_count} 篇")
        print(f"  总计: {total} 篇")

        if self.progress["failed"]:
            print(f"\n失败的文章:")
            for filename in self.progress["failed"]:
                print(f"  - {filename}")


def main():
    """主函数"""
    print("=" * 60)
    print("AI批量翻译脚本")
    print("=" * 60)
    print()

    # 检查API密钥
    api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("⚠ 未找到API密钥！")
        print()
        print("请设置环境变量:")
        print("  - ANTHROPIC_API_KEY (推荐，使用Claude API)")
        print("  - OPENAI_API_KEY (备选，使用GPT-4)")
        print()
        print("Windows设置方法:")
        print("  set ANTHROPIC_API_KEY=your-api-key-here")
        print()
        print("Linux/Mac设置方法:")
        print("  export ANTHROPIC_API_KEY=your-api-key-here")
        print()

        # 提供手动输入选项
        choice = input("是否现在输入API密钥？(y/n): ").strip().lower()
        if choice == 'y':
            provider = input("选择提供商 (anthropic/openai) [anthropic]: ").strip() or "anthropic"
            api_key = input(f"请输入{provider.upper()} API密钥: ").strip()
            if not api_key:
                print("未输入API密钥，退出。")
                return
        else:
            print("未设置API密钥，退出。")
            return
    else:
        # 自动检测提供商
        if os.getenv("ANTHROPIC_API_KEY"):
            provider = "anthropic"
        else:
            provider = "openai"
        print(f"✓ 检测到{provider.upper()} API密钥")

    # 创建翻译器
    translator = ArticleTranslator(api_key=api_key, provider=provider)

    # 开始翻译
    print()
    choice = input("开始批量翻译？这可能需要较长时间并产生API费用。(y/n): ").strip().lower()
    if choice == 'y':
        translator.translate_all(skip_existing=True)
    else:
        print("取消翻译。")


if __name__ == "__main__":
    main()
