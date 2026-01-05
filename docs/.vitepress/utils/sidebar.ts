import fs from 'fs'
import path from 'path'

interface SidebarItem {
  text: string
  link?: string
  items?: SidebarItem[]
  collapsed?: boolean
}

/**
 * 生成侧边栏配置
 * @param locale 语言代码 ('zh' 或 'en')
 */
export function generateSidebar(locale: string): SidebarItem[] {
  const articlesDir = path.resolve(__dirname, `../../${locale}/articles`)

  // 如果目录不存在，返回空数组
  if (!fs.existsSync(articlesDir)) {
    return []
  }

  // 读取所有markdown文件
  const files = fs.readdirSync(articlesDir)
    .filter(file => file.endsWith('.md'))
    .sort()

  // 按章节分组
  const chapters = new Map<string, SidebarItem[]>()

  files.forEach(file => {
    // 解析文件名: 001_1.1 Claude Code是什么.md
    const match = file.match(/^(\d+)_([\d.]+)\s+(.+)\.md$/)
    if (!match) return

    const [, , sectionNumber, title] = match
    const chapterNumber = sectionNumber.split('.')[0]

    if (!chapters.has(chapterNumber)) {
      chapters.set(chapterNumber, [])
    }

    chapters.get(chapterNumber)!.push({
      text: `${sectionNumber} ${title}`,
      link: `/${locale}/articles/${file.replace('.md', '')}`
    })
  })

  // 转换为VitePress侧边栏格式
  const sidebar: SidebarItem[] = []

  // 章节标题映射（中文）
  const chapterTitles: Record<string, { zh: string; en: string }> = {
    '1': { zh: '第一章：入门指南', en: 'Chapter 1: Getting Started' },
    '2': { zh: '第二章：核心功能', en: 'Chapter 2: Core Features' },
    '3': { zh: '第三章：高级特性', en: 'Chapter 3: Advanced Features' },
    '4': { zh: '第四章：实战应用', en: 'Chapter 4: Practical Applications' },
    '5': { zh: '第五章：进阶技巧', en: 'Chapter 5: Advanced Techniques' },
    '6': { zh: '第六章：最佳实践', en: 'Chapter 6: Best Practices' },
    '7': { zh: '第七章：性能优化', en: 'Chapter 7: Performance Optimization' },
    '8': { zh: '第八章：问题排查', en: 'Chapter 8: Troubleshooting' },
    '9': { zh: '第九章：企业应用', en: 'Chapter 9: Enterprise Applications' },
    '10': { zh: '第十章：扩展开发', en: 'Chapter 10: Extension Development' }
  }

  Array.from(chapters.keys())
    .sort((a, b) => parseInt(a) - parseInt(b))
    .forEach(chapter => {
      const title = chapterTitles[chapter]
      sidebar.push({
        text: locale === 'zh' ? (title?.zh || `第${chapter}章`) : (title?.en || `Chapter ${chapter}`),
        items: chapters.get(chapter)!,
        collapsed: false
      })
    })

  return sidebar
}
