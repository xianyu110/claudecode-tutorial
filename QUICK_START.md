# Claude Code教程网站 - 快速开始指南

**预计时间**: 30-60分钟
**难度级别**: 中等
**前置条件**: Node.js 18+, Git, GitHub账号

---

## Step 1: 环境检查 (5分钟)

```bash
# 检查Node.js版本
node --version  # 应输出 v18.x.x 或更高

# 检查pnpm
pnpm --version  # 应输出 8.x.x 或更高

# 如果未安装pnpm
npm install -g pnpm

# 检查Git
git --version
```

---

## Step 2: 项目初始化 (5分钟)

### 方式A: 从当前项目升级 (推荐)

```bash
# 进入项目目录
cd D:/Cursor编程/claudecode-tutorial

# 初始化Git (如果尚未初始化)
git status  # 如果显示fatal,则执行下面的行
git init

# 安装VitePress和依赖
pnpm install -D vitepress vue typescript
pnpm add minisearch gray-matter

# 创建项目结构
mkdir -p docs/.vitepress/theme/styles
mkdir -p docs/.vitepress/utils
mkdir -p docs/zh
mkdir -p docs/en
mkdir -p docs/public
mkdir -p scripts
```

### 方式B: 创建新项目

```bash
# 使用官方初始化脚本
npm create vitepress@latest

# 按提示选择:
# ✔ Project name: › ./docs
# ✔ Language: › JavaScript
```

---

## Step 3: 基本配置 (10分钟)

### 3.1 创建VitePress配置

**文件**: `docs/.vitepress/config.ts`

```typescript
import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Claude Code教程',
  description: '全面深入的Claude Code开发指南',
  lang: 'zh-CN',

  themeConfig: {
    logo: '/logo.png',
    nav: [
      { text: '首页', link: '/' },
      { text: '教程', link: '/zh/' },
      { text: '社区', link: 'https://github.com' }
    ],

    sidebar: {
      '/zh/': [
        {
          text: '第1章 基础概念',
          items: [
            { text: '1.1 Claude Code是什么', link: '/zh/1.1' },
            { text: '1.2 核心优势', link: '/zh/1.2' }
          ]
        }
      ]
    },

    appearance: 'auto', // 自动暗黑模式
    lastUpdated: true,

    search: {
      provider: 'local'
    }
  },

  head: [
    ['meta', { name: 'viewport', content: 'width=device-width, initial-scale=1.0' }],
    ['meta', { name: 'keywords', content: 'Claude Code, AI编程' }],
    ['link', { rel: 'icon', href: '/favicon.ico' }]
  ]
})
```

### 3.2 创建主题配置

**文件**: `docs/.vitepress/theme/index.ts`

```typescript
import { defineConfig } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import './styles/index.css'

export default {
  ...DefaultTheme,
  // 在这里可以添加自定义组件
}
```

### 3.3 创建全局样式

**文件**: `docs/.vitepress/theme/styles/index.css`

```css
:root {
  --vp-c-brand: #0066cc;
  --vp-c-brand-dark: #4488ff;
}

/* 自定义样式 */
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
```

### 3.4 创建package.json脚本

**文件**: `package.json`

```json
{
  "name": "claudecode-tutorial",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vitepress dev docs",
    "build": "vitepress build docs",
    "preview": "vitepress preview docs",
    "migrate": "ts-node scripts/migrate.ts"
  },
  "devDependencies": {
    "typescript": "^5.x",
    "vitepress": "^1.5.x",
    "vue": "^3.5.x"
  },
  "dependencies": {
    "gray-matter": "^4.x",
    "minisearch": "^6.x"
  }
}
```

---

## Step 4: 数据迁移 (15分钟)

### 4.1 创建迁移脚本

**文件**: `scripts/migrate.ts`

```typescript
import { readFileSync, writeFileSync, mkdirSync, readdirSync } from 'fs'
import * as path from 'path'
import * as matter from 'gray-matter'

const ARTICLES_DIR = 'articles'
const TARGET_DIR = 'docs/zh'
const METADATA_FILE = 'metadata.json'

async function migrate() {
  // 读取元数据
  const metadata = JSON.parse(readFileSync(METADATA_FILE, 'utf-8'))

  console.log(`开始迁移 ${metadata.length} 篇文章...`)

  // 创建目录
  mkdirSync(TARGET_DIR, { recursive: true })

  let count = 0
  for (const item of metadata) {
    const sourceFile = path.join(ARTICLES_DIR, item.filename)
    const content = readFileSync(sourceFile, 'utf-8')

    // 解析frontmatter
    const { data: fm, content: body } = matter.default(content)

    // 补充SEO元数据
    const frontmatter = {
      title: item.title,
      description: body.substring(0, 160),
      date: item.scraped_at,
      index: item.index,
      ...fm
    }

    // 生成新文件
    const filename = path.join(TARGET_DIR, item.filename)
    const newContent = matter.default.stringify(body, frontmatter)
    writeFileSync(filename, newContent, 'utf-8')

    count++
    if (count % 50 === 0) {
      console.log(`  ✓ 已迁移 ${count}/${metadata.length}`)
    }
  }

  console.log(`✅ 迁移完成! 共${count}篇文章`)
}

migrate().catch(console.error)
```

### 4.2 执行迁移

```bash
# 安装ts-node
pnpm add -D ts-node

# 执行迁移
pnpm exec ts-node scripts/migrate.ts

# 验证迁移结果
ls docs/zh/ | wc -l  # 应输出207
```

---

## Step 5: 生成搜索索引 (10分钟)

### 5.1 创建搜索索引生成脚本

**文件**: `scripts/generate-search-index.ts`

```typescript
import { readFileSync, writeFileSync } from 'fs'
import MiniSearch from 'minisearch'
import * as matter from 'gray-matter'
import { globSync } from 'glob'

async function generateIndex() {
  const miniSearch = new MiniSearch({
    fields: ['title', 'content'],
    storeFields: ['title', 'path']
  })

  const files = globSync('docs/zh/**/*.md')
  console.log(`扫描到 ${files.length} 个文件`)

  for (const file of files) {
    const content = readFileSync(file, 'utf-8')
    const { data: fm, content: body } = matter.default(content)

    miniSearch.add({
      id: file,
      title: fm.title || file,
      content: body.substring(0, 500),
      path: '/' + file.replace(/^docs\//, '').replace(/\.md$/, '')
    })
  }

  // 保存索引
  const json = miniSearch.toJSON()
  writeFileSync(
    'docs/.vitepress/search-index.json',
    JSON.stringify(json, null, 2)
  )

  console.log(`✅ 搜索索引生成完成`)
}

generateIndex().catch(console.error)
```

### 5.2 执行索引生成

```bash
pnpm add -D glob
pnpm exec ts-node scripts/generate-search-index.ts
```

---

## Step 6: 本地测试 (10分钟)

```bash
# 启动开发服务器
pnpm run dev

# 输出类似:
# ➜  Local:   http://localhost:5173/
# ➜  press to edit and restart, or `q` to quit
```

### 验证清单

在浏览器打开 http://localhost:5173/

- [ ] 首页加载正常
- [ ] 导航菜单出现
- [ ] 能访问文章列表
- [ ] 搜索框出现
- [ ] 点击搜索能工作
- [ ] 可切换暗黑模式 (如配置)

---

## Step 7: 生产构建 (5分钟)

```bash
# 执行生产构建
pnpm run build

# 预览生产版本
pnpm run preview

# 输出类似:
# ➜  Local: http://localhost:4173/
```

验证生产构建中所有功能都能工作。

---

## Step 8: GitHub部署 (10分钟)

### 8.1 初始化GitHub仓库

```bash
# 如果未初始化
git init
git add .
git commit -m "feat: initial VitePress setup with 207 articles"

# 添加远程仓库
git remote add origin https://github.com/yourusername/claudecode-tutorial.git

# 推送到main分支
git branch -M main
git push -u origin main
```

### 8.2 创建GitHub Actions工作流

**文件**: `.github/workflows/deploy.yml`

```yaml
name: Deploy

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v2
        with:
          version: 8

      - uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: pnpm

      - run: pnpm install

      - run: pnpm run build

      - uses: actions/upload-pages-artifact@v2
        with:
          path: docs/.vitepress/dist

      - uses: actions/deploy-pages@v2
        id: deployment
```

### 8.3 启用GitHub Pages

```bash
# 推送workflow文件
git add .github/
git commit -m "ci: add deploy workflow"
git push origin main
```

然后在GitHub仓库:
1. 进入 **Settings** → **Pages**
2. 源选择 **GitHub Actions**
3. 等待workflow完成 (~3-5分钟)
4. 访问提示的URL

---

## 完成!

### 查看部署结果

访问: `https://yourusername.github.io/claudecode-tutorial`

### 后续可选步骤

1. **配置自定义域名**
   ```bash
   # 添加CNAME文件
   echo "yourdomain.com" > docs/public/CNAME
   ```

2. **添加Google Analytics**
   ```typescript
   // 在config.ts中添加
   head: [
     ['script', { async: true, src: 'https://www.googletagmanager.com/gtag/js?id=GA_ID' }],
     ['script', {}, `window.dataLayer = window.dataLayer || [];
   function gtag(){dataLayer.push(arguments);}
   gtag('js', new Date());
   gtag('config', 'GA_ID');`]
   ]
   ```

3. **启用国际化**
   - 参考`TECHNICAL_SOLUTION.md`中的i18n章节

4. **自定义样式**
   - 编辑`docs/.vitepress/theme/styles/`中的CSS文件

---

## 常见问题

### Q: 构建失败，显示"Cannot find module"

A: 运行 `pnpm install` 确保所有依赖已安装

### Q: Pages显示404

A:
1. 检查Settings → Pages中Source是否设为"GitHub Actions"
2. 等待5分钟让DNS传播
3. 清除浏览器缓存

### Q: 中文显示乱码

A: 确保所有文件编码为UTF-8
```bash
# Linux/Mac
find docs -name "*.md" -exec file {} \; | grep -i "utf-8"
```

### Q: 搜索不工作

A:
1. 运行搜索索引生成脚本: `pnpm exec ts-node scripts/generate-search-index.ts`
2. 检查`docs/.vitepress/search-index.json`是否存在
3. 重新构建: `pnpm run build`

### Q: 想添加更多语言

A: 参考`TECHNICAL_SOLUTION.md`第五部分 5.2 国际化支持

---

## 下一步

- 阅读 `TECHNICAL_SOLUTION.md` 了解完整架构
- 阅读 `DEPLOYMENT_CHECKLIST.md` 了解详细部署步骤
- 参考 VitePress官方文档: https://vitepress.dev/

---

**需要帮助?**
- 查看GitHub Issues: https://github.com/yourusername/claudecode-tutorial/issues
- VitePress讨论: https://github.com/vuejs/vitepress/discussions

**快速命令参考**:
```bash
# 开发
pnpm run dev

# 构建
pnpm run build

# 预览
pnpm run preview

# 迁移数据
pnpm exec ts-node scripts/migrate.ts

# 生成搜索索引
pnpm exec ts-node scripts/generate-search-index.ts

# 提交并部署
git add .
git commit -m "message"
git push origin main
```

祝贺! 你已成功部署Claude Code教程网站! 🎉
