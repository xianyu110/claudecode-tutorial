#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI翻译脚本
使用 Claude API 将中文文章翻译为英文
"""

import os
import sys
import json
import time
import re
from pathlib import Path
from anthropic import Anthropic

# 设置 stdout 编码为 utf-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class ArticleTranslator:
    """文章翻译器"""

    def __init__(self, api_key=None, api_base=None):
        """初始化翻译器"""
        # 从环境变量或参数获取 API 配置
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY') or os.getenv('CLAUDE_API_KEY')
        self.api_base = api_base or os.getenv('ANTHROPIC_BASE_URL') or os.getenv('CLAUDE_BASE_URL')

        if not self.api_key:
            raise ValueError("未找到 API Key，请设置环境变量 ANTHROPIC_API_KEY 或 CLAUDE_API_KEY")

        # 初始化 Anthropic 客户端
        client_kwargs = {'api_key': self.api_key}
        if self.api_base:
            client_kwargs['base_url'] = self.api_base

        self.client = Anthropic(**client_kwargs)
        self.model = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')

        # 翻译记录文件
        self.progress_file = Path('.translation_progress.json')
        self.translated_files = self.load_progress()

    def load_progress(self):
        """加载翻译进度"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return set(json.load(f))
            except Exception as e:
                print(f"[WARNING] 无法加载翻译进度: {e}")
                return set()
        return set()

    def save_progress(self):
        """保存翻译进度"""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.translated_files), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[WARNING] 无法保存翻译进度: {e}")

    def extract_code_blocks(self, content):
        """提取代码块，返回处理后的内容和代码块列表"""
        code_blocks = []
        pattern = r'```[\s\S]*?```'

        def replacer(match):
            code_blocks.append(match.group(0))
            return f'<<<CODE_BLOCK_{len(code_blocks) - 1}>>>'

        processed_content = re.sub(pattern, replacer, content)
        return processed_content, code_blocks

    def restore_code_blocks(self, content, code_blocks):
        """恢复代码块"""
        for i, block in enumerate(code_blocks):
            content = content.replace(f'<<<CODE_BLOCK_{i}>>>', block)
        return content

    def translate_text(self, text, retries=3):
        """使用 Claude API 翻译文本"""
        # 提取代码块
        processed_text, code_blocks = self.extract_code_blocks(text)

        # 构建翻译提示
        prompt = f"""Please translate the following Chinese technical tutorial article to English.

Requirements:
1. Maintain the Markdown format exactly (headings, lists, tables, etc.)
2. Keep all technical terms accurate
3. Use natural, professional English
4. Code block placeholders (<<<CODE_BLOCK_X>>>) should remain unchanged
5. Preserve all Markdown syntax and structure
6. Translate section titles, descriptions, and explanations
7. Keep proper nouns (like "Claude Code", "Anthropic") unchanged

Chinese article content:
{processed_text}

Please provide the English translation:"""

        for attempt in range(retries):
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=8000,
                    temperature=0.3,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                # 获取翻译结果
                translated_text = message.content[0].text

                # 恢复代码块
                translated_text = self.restore_code_blocks(translated_text, code_blocks)

                return translated_text

            except Exception as e:
                print(f"[WARNING] 翻译失败 (尝试 {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    raise

    def translate_article(self, source_file, target_file):
        """翻译单个文章文件"""
        try:
            # 读取源文件
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 如果文件为空或太短，跳过
            if len(content.strip()) < 50:
                print(f"[SKIP] 文件内容太短，跳过: {source_file}")
                return False

            print(f"[TRANSLATING] {source_file.name}")
            print(f"  字符数: {len(content)}")

            # 翻译
            translated_content = self.translate_text(content)

            # 创建目标目录
            target_file.parent.mkdir(parents=True, exist_ok=True)

            # 写入翻译结果
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(translated_content)

            print(f"[OK] 翻译完成: {target_file}")

            # 记录进度
            self.translated_files.add(str(source_file))
            self.save_progress()

            # API 限流，延迟一下
            time.sleep(1)

            return True

        except Exception as e:
            print(f"[ERROR] 翻译失败: {source_file}")
            print(f"  错误: {str(e)}")
            return False

    def translate_all_articles(self, source_dir, target_dir):
        """批量翻译所有文章"""
        source_path = Path(source_dir)
        target_path = Path(target_dir)

        if not source_path.exists():
            print(f"[ERROR] 源目录不存在: {source_path}")
            return

        # 获取所有 Markdown 文件
        md_files = sorted(source_path.glob('*.md'))

        # 过滤已翻译的文件
        pending_files = [f for f in md_files if str(f) not in self.translated_files]

        print(f"\n开始翻译 {len(pending_files)} 篇文章...")
        print(f"源目录: {source_path}")
        print(f"目标目录: {target_path}")
        print(f"已翻译: {len(self.translated_files)}")
        print(f"待翻译: {len(pending_files)}\n")

        if len(pending_files) == 0:
            print("所有文章已翻译完成！")
            return

        success_count = 0
        failure_count = 0

        for i, source_file in enumerate(pending_files, 1):
            print(f"\n进度: {i}/{len(pending_files)}")

            # 构建目标文件路径
            target_file = target_path / source_file.name

            # 翻译
            if self.translate_article(source_file, target_file):
                success_count += 1
            else:
                failure_count += 1

        print(f"\n\n翻译完成!")
        print(f"成功: {success_count}")
        print(f"失败: {failure_count}")
        print(f"总计: {len(pending_files)}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='AI翻译脚本 - 将中文文章翻译为英文')
    parser.add_argument('--api-key', help='Anthropic API Key')
    parser.add_argument('--api-base', help='Anthropic API Base URL')
    parser.add_argument('--source', default='docs/zh/articles', help='源文章目录')
    parser.add_argument('--target', default='docs/en/articles', help='目标文章目录')
    parser.add_argument('--reset', action='store_true', help='重置翻译进度')

    args = parser.parse_args()

    # 重置进度
    if args.reset:
        progress_file = Path('.translation_progress.json')
        if progress_file.exists():
            progress_file.unlink()
            print("[INFO] 翻译进度已重置")

    try:
        # 创建翻译器
        translator = ArticleTranslator(api_key=args.api_key, api_base=args.api_base)

        # 开始翻译
        translator.translate_all_articles(args.source, args.target)

    except ValueError as e:
        print(f"[ERROR] {e}")
        print("\n使用方法:")
        print("  1. 设置环境变量: set ANTHROPIC_API_KEY=your_api_key")
        print("  2. 或使用参数: python translate_to_english.py --api-key your_api_key")
        print("  3. 如果使用自定义 API 地址:")
        print("     python translate_to_english.py --api-key your_key --api-base https://your-api-base-url")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n[INFO] 翻译已中断，进度已保存")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
