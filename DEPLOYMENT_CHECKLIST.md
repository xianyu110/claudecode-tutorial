# Claude Code 教程网站 - 部署实施检查清单

**完成日期**:
**检查人**:
**项目状态**:

---

## 第一阶段：项目初始化

### 1.1 环境准备

- [ ] 安装Node.js 18+ LTS (验证: `node --version`)
- [ ] 安装pnpm 8+ (验证: `pnpm --version`)
- [ ] 安装Git (验证: `git --version`)
- [ ] VS Code编辑器 + VitePress扩展
- [ ] GitHub账号已创建
- [ ] 本地开发机器性能检查 (推荐: 8GB内存, 10GB磁盘)

**验证步骤**:
```bash
node --version    # 应输出 v18.x.x 或更高
pnpm --version    # 应输出 8.x.x 或更高
npm list -g pnpm  # 确认全局安装
```

### 1.2 GitHub仓库初始化

- [ ] 在GitHub创建新仓库 `claudecode-tutorial`
- [ ] 仓库设为公开 (Public)
- [ ] 添加README.md
- [ ] 添加.gitignore (Node.js模板)
- [ ] 添加MIT或Apache 2.0许可证

**验证步骤**:
```bash
git clone https://github.com/yourusername/claudecode-tutorial.git
cd claudecode-tutorial
```

### 1.3 VitePress项目初始化

- [ ] 创建VitePress项目结构:
  ```
  docs/.vitepress/          # VitePress核心
  docs/public/              # 静态资源
  docs/zh/                  # 中文文档
  docs/en/                  # 英文文档 (可选)
  scripts/                  # 自定义脚本
  ```

- [ ] 初始化package.json:
  ```bash
  pnpm init
  ```

- [ ] 安装核心依赖:
  ```bash
  pnpm add -D vitepress vue typescript
  pnpm add minisearch gray-matter
  ```

- [ ] 配置tsconfig.json
- [ ] 配置.editorconfig
- [ ] 首次git提交

**验证步骤**:
```bash
pnpm install --no-frozen-lockfile
ls -la node_modules/vitepress
```

---

## 第二阶段：数据迁移

### 2.1 元数据分析

- [ ] 确认metadata.json完整性:
  - 文章总数: 207篇
  - 必需字段: index, title, url, filename, scraped_at
  - 编码: UTF-8

- [ ] 分析articles/目录:
  - 文件总数: 207个
  - 文件大小: 2.9MB
  - 命名规范: 001_标题.md

**验证脚本**:
```bash
# 统计文件数
find articles -name "*.md" -type f | wc -l  # 应输出207

# 检查文件编码
file articles/*.md | grep UTF-8 | wc -l    # 应接近207

# 检查metadata完整性
python3 -c "import json; m=json.load(open('metadata.json')); print(f'Articles: {len(m)}, Fields: {list(m[0].keys())}')"
```

### 2.2 迁移脚本编写

- [ ] 编写`scripts/migrate.ts`:
  - 读取metadata.json
  - 读取articles/*.md
  - 解析frontmatter
  - 生成enhanced frontmatter
  - 创建docs/zh/chapter*/结构
  - 写入新文件

- [ ] 编写`scripts/generate-sidebar.ts`:
  - 从metadata提取章节信息
  - 生成sidebar配置
  - 输出为sidebar-generated.ts

- [ ] 编写`scripts/generate-search-index.ts`:
  - 扫描所有.md文件
  - 提取标题和摘要
  - 生成minisearch索引
  - 输出search-index.json

- [ ] 测试脚本 (在小样本上):
  ```bash
  # 迁移前备份
  cp -r articles articles.backup
  cp metadata.json metadata.backup.json

  # 执行迁移 (测试5篇)
  pnpm exec ts-node scripts/migrate.ts --limit 5
  ```

### 2.3 执行迁移

- [ ] 创建空的docs/zh/目录结构
- [ ] 运行完整迁移:
  ```bash
  pnpm exec ts-node scripts/migrate.ts
  ```

- [ ] 验证迁移结果:
  - [ ] 207个文件已创建
  - [ ] 所有文件位置正确
  - [ ] frontmatter格式正确
  - [ ] 内容完整无损

**验证清单**:
```bash
# 统计迁移后的文件数
find docs/zh -name "*.md" | wc -l  # 应输出207

# 检查frontmatter格式
head -20 docs/zh/chapter1/001_*.md | grep -E "^(title|date|index)"

# 检查是否有遗漏的文件
comm -23 \
  <(find articles -name "*.md" | xargs -I {} basename {} | sort) \
  <(find docs/zh -name "*.md" | xargs -I {} basename {} | sort)
```

### 2.4 生成侧边栏和搜索索引

- [ ] 运行侧边栏生成脚本:
  ```bash
  pnpm exec ts-node scripts/generate-sidebar.ts
  ```

- [ ] 验证sidebar-generated.ts:
  - [ ] 包含所有207篇文章
  - [ ] 章节分组正确
  - [ ] 链接路径有效

- [ ] 运行搜索索引生成:
  ```bash
  pnpm exec ts-node scripts/generate-search-index.ts
  ```

- [ ] 验证search-index.json:
  - [ ] 文件大小合理 (~300-500KB)
  - [ ] 包含所有文章的标题和摘要
  - [ ] JSON格式正确

---

## 第三阶段：VitePress配置

### 3.1 主配置文件

- [ ] 创建`docs/.vitepress/config.ts`
- [ ] 配置基本信息:
  - [ ] title: "Claude Code教程"
  - [ ] description: "全面深入的Claude Code开发指南"
  - [ ] head元标签 (SEO)

- [ ] 配置多语言:
  - [ ] 中文 (zh-CN): /zh/
  - [ ] 英文 (en-US): /en/ (可选)

- [ ] 配置主题:
  - [ ] logo和favicon
  - [ ] 导航栏 (nav)
  - [ ] 侧边栏 (sidebar)
  - [ ] 暗黑模式: appearance: 'auto'

- [ ] 配置搜索:
  - [ ] provider: 'local'
  - [ ] minisearch选项

**验证步骤**:
```bash
# 检查TypeScript编译
pnpm exec tsc --noEmit docs/.vitepress/config.ts
```

### 3.2 主题定制

- [ ] 创建`docs/.vitepress/theme/index.ts`:
  - [ ] 导入VitePress默认主题
  - [ ] 注册自定义组件
  - [ ] 应用全局样式

- [ ] 创建自定义样式:
  - [ ] `docs/.vitepress/theme/styles/vars.css` (CSS变量)
  - [ ] `docs/.vitepress/theme/styles/layout.css` (布局)
  - [ ] `docs/.vitepress/theme/styles/index.css` (全局)

- [ ] 测试暗黑模式:
  - [ ] 浅色主题加载正常
  - [ ] 暗黑主题加载正常
  - [ ] 主题切换按钮出现
  - [ ] localStorage保存选择

### 3.3 Markdown插件配置

- [ ] 配置代码高亮 (Shiki):
  - [ ] light主题: github-light
  - [ ] dark主题: github-dark

- [ ] 配置Markdown扩展:
  - [ ] 表格支持
  - [ ] 任务列表支持
  - [ ] Emoji支持
  - [ ] 代码块行号

**验证步骤**:
```bash
# 验证Markdown渲染
pnpm run build --no-clean 2>&1 | grep -i "markdown\|error"
```

---

## 第四阶段：功能实现

### 4.1 搜索功能

- [ ] minisearch集成:
  - [ ] 创建search-index.json
  - [ ] 创建搜索组件 (Search.vue)
  - [ ] 集成到主题

- [ ] 搜索功能测试:
  - [ ] 输入中文能搜到结果
  - [ ] 模糊搜索工作
  - [ ] 结果点击能导航
  - [ ] 搜索性能 (<100ms)

**测试步骤**:
```bash
# 在dev模式下测试
pnpm run dev

# 在浏览器控制台验证
setTimeout(() => {
  document.querySelector('.search input').value = 'Claude Code'
  document.querySelector('.search input').dispatchEvent(new Event('input'))
}, 1000)
```

### 4.2 国际化配置

- [ ] 创建en/目录结构:
  ```
  docs/en/
  ├── index.md
  ├── guide/
  └── ...
  ```

- [ ] 配置i18n路由 (在config.ts中)
- [ ] 英文导航菜单配置
- [ ] 英文侧边栏生成

- [ ] 国际化测试:
  - [ ] /zh/路径访问中文版本
  - [ ] /en/路径访问英文版本
  - [ ] 语言切换器出现
  - [ ] 搜索适配多语言

**验证步骤**:
```bash
# 本地测试不同路由
curl http://localhost:5173/zh/ | grep -i "claude code"
curl http://localhost:5173/en/ | grep -i "claude code"
```

### 4.3 SEO优化

- [ ] Sitemap生成:
  - [ ] 创建sitemap.xml生成脚本
  - [ ] 包含所有页面
  - [ ] 设置优先级和更新频率

- [ ] robots.txt配置:
  ```
  User-agent: *
  Allow: /
  Disallow: /.vitepress/
  Sitemap: https://yoursite.com/sitemap.xml
  ```

- [ ] Meta标签验证:
  - [ ] title标签 (50-60字)
  - [ ] description标签 (120-160字)
  - [ ] keywords标签
  - [ ] og:*标签 (社交分享)
  - [ ] twitter:*标签

**验证工具**:
- Google Page Speed Insights
- Screaming Frog SEO Spider
- Ahrefs SEO Toolbar

---

## 第五阶段：本地测试

### 5.1 构建测试

- [ ] 执行开发服务器:
  ```bash
  pnpm run dev
  ```

  验证:
  - [ ] 启动无错误
  - [ ] 首页加载 (<3秒)
  - [ ] 导航菜单正常
  - [ ] 所有文章可访问

- [ ] 执行生产构建:
  ```bash
  pnpm run build
  ```

  验证:
  - [ ] 构建成功 (exit code 0)
  - [ ] 无TypeScript错误
  - [ ] 无未引用资源警告
  - [ ] dist/目录大小 (<50MB)

- [ ] 预览生产构建:
  ```bash
  pnpm run preview
  ```

  验证:
  - [ ] 站点在localhost:4173正常运行
  - [ ] 所有页面可访问
  - [ ] 资源加载完整

### 5.2 功能测试

- [ ] **搜索功能**:
  - [ ] 英文关键词搜索
  - [ ] 中文关键词搜索
  - [ ] 搜索结果准确
  - [ ] 搜索响应速度

- [ ] **主题切换**:
  - [ ] 浅色模式正常显示
  - [ ] 暗黑模式正常显示
  - [ ] 切换流畅无闪烁
  - [ ] 刷新保持选择

- [ ] **语言切换**:
  - [ ] 中文导航可用
  - [ ] 英文导航可用 (如有)
  - [ ] 切换无错误
  - [ ] URL路由正确

- [ ] **导航和链接**:
  - [ ] 首页导航工作
  - [ ] 章节导航正确
  - [ ] 内部链接有效
  - [ ] 外部链接正确

- [ ] **SEO检查**:
  - [ ] 页面title唯一
  - [ ] description完整
  - [ ] h1标签存在
  - [ ] 链接结构合理
  - [ ] 移动端响应式

### 5.3 性能测试

- [ ] **页面加载速度** (Lighthouse):
  - [ ] 首页加载时间 <3秒
  - [ ] 文章页面 <2.5秒
  - [ ] 综合评分 >90分

- [ ] **搜索性能**:
  - [ ] 搜索响应 <100ms
  - [ ] 索引大小 <500KB
  - [ ] 无内存泄漏

- [ ] **构建性能**:
  - [ ] 完整构建 <2分钟
  - [ ] 增量构建 <10秒
  - [ ] 内存占用 <500MB

**性能测试工具**:
```bash
# 使用lighthouse-ci
npm install -g @lhci/cli@latest
lhci collect
lhci upload
lhci assert
```

### 5.4 兼容性测试

浏览器兼容性 (推荐最低版本):
- [ ] Chrome 90+ (VitePress支持)
- [ ] Firefox 88+
- [ ] Safari 14+
- [ ] Edge 90+
- [ ] 移动浏览器 (iOS Safari 14+, Android Chrome 90+)

**测试方式**:
- 使用BrowserStack进行跨浏览器测试
- 开发者工具模拟不同设备

---

## 第六阶段：GitHub Pages部署

### 6.1 GitHub仓库配置

- [ ] 推送所有代码到GitHub:
  ```bash
  git add .
  git commit -m "feat: VitePress setup with 207 articles"
  git push -u origin main
  ```

- [ ] 验证GitHub上的文件:
  - [ ] docs/目录完整
  - [ ] .github/workflows/存在
  - [ ] package.json正确
  - [ ] node_modules已.gitignore

### 6.2 GitHub Actions配置

- [ ] 创建`.github/workflows/deploy.yml`:
  ```yaml
  name: Deploy to GitHub Pages
  on:
    push:
      branches:
        - main
  jobs:
    build:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: pnpm/action-setup@v2
        - uses: actions/setup-node@v4
          with:
            node-version: 18
            cache: pnpm
        - run: pnpm install
        - run: pnpm run build
        - uses: actions/upload-pages-artifact@v2
          with:
            path: docs/.vitepress/dist
    deploy:
      needs: build
      environment:
        name: github-pages
      runs-on: ubuntu-latest
      steps:
        - uses: actions/deploy-pages@v2
  permissions:
    contents: read
    pages: write
    id-token: write
  ```

- [ ] 验证workflow文件:
  - [ ] YAML语法正确
  - [ ] 步骤顺序合理
  - [ ] 权限配置完整

### 6.3 GitHub Pages启用

- [ ] 在仓库Settings中启用Pages:
  - [ ] 进入Settings → Pages
  - [ ] Source选择"GitHub Actions"
  - [ ] 不需要手动选择分支或文件夹

- [ ] 验证Pages配置:
  - [ ] 状态显示"Active"
  - [ ] 站点URL显示 (https://yourusername.github.io/claudecode-tutorial)

### 6.4 首次部署

- [ ] 提交触发Actions:
  ```bash
  git add .github/workflows/deploy.yml
  git commit -m "ci: add GitHub Pages deploy workflow"
  git push origin main
  ```

- [ ] 监控Actions执行:
  - [ ] 进入GitHub仓库 → Actions标签页
  - [ ] 观察最新workflow运行
  - [ ] 等待"build"和"deploy"完成 (~3-5分钟)

- [ ] 验证部署成功:
  - [ ] workflow显示绿色"✓"
  - [ ] 点击Pages deployment annotation查看URL
  - [ ] 访问https://yourusername.github.io/claudecode-tutorial

**常见问题排查**:
```
❌ workflow失败
  → 检查Actions标签页的错误日志
  → 常见原因: Node版本, pnpm安装, 文件路径

❌ Pages显示404
  → 检查GitHub Pages是否启用 (Settings → Pages)
  → 确认Source设置为"GitHub Actions"
  → 等待5分钟后重试 (DNS传播需要时间)

❌ 页面样式缺失
  → 检查config.ts中的base路径 (应为"/claudecode-tutorial/")
  → 清除浏览器缓存
  → 检查dist/中的CSS文件是否存在
```

---

## 第七阶段：自定义域名(可选)

### 7.1 域名配置

- [ ] 在GitHub仓库添加CNAME文件:
  ```bash
  # docs/public/CNAME
  claudecode.tangshuang.net
  ```

- [ ] 将CNAME文件添加到git:
  ```bash
  git add docs/public/CNAME
  git commit -m "feat: add custom domain"
  git push origin main
  ```

### 7.2 DNS配置

根据域名注册商配置DNS记录:

**方式1: 使用A记录 (推荐)**
```
Type: A
Name: @
Value: 185.199.108.153
           185.199.109.153
           185.199.110.153
           185.199.111.153
TTL: 3600
```

**方式2: 使用CNAME**
```
Type: CNAME
Name: www (或子域名)
Value: yourusername.github.io
TTL: 3600
```

### 7.3 GitHub验证

- [ ] 进入Settings → Pages
- [ ] 在"Custom domain"输入框输入域名
- [ ] 点击"Save"
- [ ] GitHub自动验证DNS配置
- [ ] 勾选"Enforce HTTPS" (推荐)

**DNS验证 (需要5-48小时)**:
```bash
# 检查DNS解析
nslookup claudecode.tangshuang.net
dig claudecode.tangshuang.net

# 应该解析到GitHub Pages IP
```

---

## 第八阶段：上线后验证

### 8.1 公开链接测试

- [ ] 在浏览器访问生产链接:
  - [ ] https://yourusername.github.io/claudecode-tutorial (GitHub默认)
  - [ ] https://claudecode.tangshuang.net (自定义域名, 如有)

- [ ] 验证每个功能:
  - [ ] 首页加载正常
  - [ ] 导航菜单工作
  - [ ] 搜索功能可用
  - [ ] 主题切换工作
  - [ ] 所有链接有效
  - [ ] 移动端响应正常

### 8.2 SEO验证

- [ ] 提交至Google Search Console:
  1. 进入https://search.google.com/search-console
  2. 添加属性 (URL前缀: https://yourusername.github.io)
  3. 验证所有权 (HTML文件或DNS)
  4. 提交sitemap.xml
  5. 请求索引抓取

- [ ] Google索引验证:
  ```
  site:yourusername.github.io/claudecode-tutorial
  ```
  应该返回至少207个结果

- [ ] 其他搜索引擎:
  - [ ] Bing Webmaster Tools
  - [ ] 百度搜索资源平台 (如针对中国用户)

### 8.3 性能监控

- [ ] 配置Google Analytics (可选):
  1. 创建GA4属性
  2. 获取测量ID
  3. 添加到config.ts head
  4. 验证数据收集

- [ ] 配置错误监控 (可选):
  - [ ] Sentry (JavaScript错误)
  - [ ] Google Analytics (用户行为)

### 8.4 社交媒体分享测试

- [ ] 测试Open Graph:
  ```bash
  # 使用Open Graph调试工具
  https://developers.facebook.com/tools/debug/
  ```

- [ ] 验证分享显示:
  - [ ] 标题正确
  - [ ] 描述完整
  - [ ] 缩略图显示

### 8.5 最终检查清单

- [ ] 所有文章都能访问
- [ ] 搜索功能正常
- [ ] 主题切换工作
- [ ] 页面加载速度 <3秒
- [ ] SEO元数据完整
- [ ] 手机端显示正常
- [ ] 所有外链有效
- [ ] Analytics正确安装
- [ ] HTTPS已启用
- [ ] 404页面定制 (可选)

---

## 第九阶段：上线后维护

### 9.1 日常监控 (每周)

- [ ] 检查GitHub Actions日志
- [ ] 查看Google Search Console错误
- [ ] 检查Analytics访问量
- [ ] 手动测试主要功能

**监控命令**:
```bash
# 监控部署日志
gh run list -R yourusername/claudecode-tutorial -L 10

# 检查sitemap
curl https://yourusername.github.io/sitemap.xml | head -20

# 检查robots.txt
curl https://yourusername.github.io/robots.txt
```

### 9.2 定期维护 (每月)

- [ ] 更新依赖:
  ```bash
  pnpm update
  pnpm audit
  ```

- [ ] SEO内容审计:
  - [ ] 检查low-ranking页面
  - [ ] 补充keywords长尾词
  - [ ] 优化元描述

- [ ] 性能优化:
  - [ ] Lighthouse重新评分
  - [ ] 检查加载时间
  - [ ] 优化图片大小

### 9.3 季度审查

- [ ] 内容更新计划
- [ ] 新功能需求评估
- [ ] 用户反馈整理
- [ ] 竞品分析

---

## 快速参考

### 常用命令

```bash
# 开发
pnpm run dev              # 启动开发服务器
pnpm run build            # 生产构建
pnpm run preview          # 预览生产构建

# 脚本
pnpm exec ts-node scripts/migrate.ts              # 数据迁移
pnpm exec ts-node scripts/generate-sidebar.ts    # 生成侧边栏
pnpm exec ts-node scripts/generate-search-index  # 生成搜索索引

# Git
git status                # 检查状态
git add .                 # 暂存所有更改
git commit -m "message"   # 提交
git push origin main      # 推送到GitHub
git log --oneline         # 查看提交历史

# 部署
gh run list               # 列出Actions运行
gh run view <run-id>      # 查看运行详情
```

### 故障排查

| 问题 | 可能原因 | 解决方案 |
|------|--------|--------|
| build失败 | Node版本过低 | 升级到18+ |
| Pages 404 | Actions未运行成功 | 检查workflow日志 |
| 搜索不工作 | 索引未生成 | 运行generate-search-index脚本 |
| 样式丢失 | base路径错误 | 检查config.ts中的base配置 |
| 中文显示乱码 | 文件编码问题 | 转换为UTF-8 |

---

## 签收确认

- [ ] 所有测试步骤已完成
- [ ] 所有功能已验证
- [ ] 生产环境已上线
- [ ] 监控已配置
- [ ] 文档已更新
- [ ] 团队已培训

**检查人签名**: _______________
**完成日期**: _______________
**备注**:

---

**文档版本**: 1.0
**最后更新**: 2026-01-05
**有效期**: 长期有效 (定期更新)
