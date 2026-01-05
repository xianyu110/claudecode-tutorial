# Claude Code 教程

> 📚 完整的Claude Code中文教程 - 从入门到精通

[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-blue?logo=github)](https://xianyu110.github.io/claudecode-tutorial/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![VitePress](https://img.shields.io/badge/VitePress-1.6+-green.svg)](https://vitepress.dev/)

## 📖 项目简介

本项目是一个完整的Claude Code教程网站，包含207篇详细文章，全面覆盖Claude Code的各个方面。

### ✨ 特性

- 📱 **响应式设计** - 完美支持桌面和移动设备
- 🌗 **暗黑模式** - 支持浅色/深色主题自动切换
- 🔍 **全文搜索** - 快速查找所需内容
- 🌐 **国际化** - 支持中文和英文（`/zh` 和 `/en` 路由）
- ⚡ **极速加载** - 基于VitePress，构建速度快，页面加载迅速
- 📊 **SEO优化** - 自动生成sitemap，优化搜索引擎收录
- 🚀 **自动部署** - 通过GitHub Actions自动部署到GitHub Pages

## 🚀 快速开始

### 环境要求

- Node.js 18+
- npm 10+

### 安装依赖

```bash
npm install
```

### 本地开发

```bash
npm run docs:dev
```

访问 http://localhost:5173 查看网站

### 构建生产版本

```bash
npm run docs:build
```

### 预览生产版本

```bash
npm run docs:preview
```

## 📂 项目结构

```
claudecode-tutorial/
├── docs/                      # VitePress文档目录
│   ├── .vitepress/           # VitePress配置
│   │   ├── config.ts         # 主配置文件
│   │   └── utils/            # 工具函数
│   │       └── sidebar.ts    # 侧边栏生成器
│   ├── zh/                   # 中文内容
│   │   ├── index.md          # 中文首页
│   │   └── articles/         # 中文文章（207篇）
│   ├── en/                   # 英文内容
│   │   ├── index.md          # 英文首页
│   │   └── articles/         # 英文文章
│   └── public/               # 静态资源
│       └── robots.txt        # 搜索引擎爬虫配置
├── .github/                  # GitHub配置
│   └── workflows/            # GitHub Actions工作流
│       └── deploy.yml        # 自动部署配置
├── scraper.py               # 原始爬虫脚本
├── translate_articles.py    # AI翻译脚本
├── package.json             # Node.js依赖配置
└── requirements.txt         # Python依赖配置
```

## 🌐 国际化

本项目支持中英文双语：

- **中文版本**: `/zh/` 路由
- **英文版本**: `/en/` 路由

### 使用AI翻译文章

如果你想将中文文章翻译为英文，可以使用提供的AI翻译脚本：

#### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

#### 2. 设置API密钥

**使用Anthropic Claude API（推荐）：**

```bash
# Windows
set ANTHROPIC_API_KEY=your-api-key-here

# Linux/Mac
export ANTHROPIC_API_KEY=your-api-key-here
```

**或使用OpenAI API：**

```bash
# Windows
set OPENAI_API_KEY=your-api-key-here

# Linux/Mac
export OPENAI_API_KEY=your-api-key-here
```

#### 3. 运行翻译脚本

```bash
python translate_articles.py
```

脚本特性：
- ✅ 自动翻译所有中文文章为英文
- ✅ 保持Markdown格式不变
- ✅ 自动保存翻译进度
- ✅ 支持断点续传
- ✅ 自动重试失败的翻译

**注意**：翻译207篇文章可能需要较长时间并产生API费用，建议先小批量测试。

## 🚀 部署到GitHub Pages

### 1. 创建GitHub仓库

```bash
git init
git add .
git commit -m "Initial commit: Claude Code tutorial website"
git branch -M main
git remote add origin https://github.com/xianyu110/claudecode-tutorial.git
git push -u origin main
```

### 2. 配置GitHub Pages

1. 进入仓库的 **Settings** > **Pages**
2. 在 **Source** 下选择 **GitHub Actions**
3. 等待自动部署完成

### 3. 访问网站

部署完成后，访问：
```
https://xianyu110.github.io/claudecode-tutorial/
```

### 4. 自定义域名（可选）

如果你有自己的域名：

1. 在 `docs/public/` 创建 `CNAME` 文件
2. 写入你的域名（如：`claudecode.example.com`）
3. 在域名DNS设置中添加CNAME记录指向 `yourusername.github.io`

## 🛠️ 自定义配置

### 修改网站信息

编辑 `docs/.vitepress/config.ts` 文件：

```typescript
export default defineConfig({
  title: '你的网站标题',
  description: '你的网站描述',
  base: '/your-repo-name/',
  // ... 其他配置
})
```

### 修改首页内容

- 中文首页: `docs/zh/index.md`
- 英文首页: `docs/en/index.md`

### 添加Logo

将你的logo图片放到 `docs/public/` 目录，然后在配置文件中引用：

```typescript
themeConfig: {
  logo: '/your-logo.png'
}
```

## 📊 SEO优化

项目已配置以下SEO优化：

- ✅ 自动生成sitemap.xml
- ✅ robots.txt配置
- ✅ Meta标签优化
- ✅ Open Graph标签
- ✅ 语义化HTML结构
- ✅ 响应式设计

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

## 📝 许可协议

本项目基于 [MIT License](LICENSE) 开源。

## 🙏 致谢

- [VitePress](https://vitepress.dev/) - 强大的静态站点生成器
- [Claude Code](https://claude.ai/code) - AI编程助手
- 所有贡献者

## 📧 联系方式

如有问题或建议，请：

- 提交 [Issue](https://github.com/xianyu110/claudecode-tutorial/issues)
- 发起 [Discussion](https://github.com/xianyu110/claudecode-tutorial/discussions)

---

<div align="center">
  <p>用 ❤️ 构建 | Powered by VitePress</p>
  <p>
    <a href="https://xianyu110.github.io/claudecode-tutorial/zh/">中文</a> •
    <a href="https://xianyu110.github.io/claudecode-tutorial/en/">English</a>
  </p>
</div>
