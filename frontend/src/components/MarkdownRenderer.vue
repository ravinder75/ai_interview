<template>
  <div class="markdown-body space-y-3 font-sans text-xs leading-relaxed text-slate-200">
    <div v-for="(block, idx) in parsedBlocks" :key="idx">
      <!-- Fenced Code Block -->
      <div v-if="block.type === 'code'" class="my-3 rounded-xl overflow-hidden bg-slate-950 border border-slate-800">
        <div class="flex items-center justify-between px-4 py-2 bg-slate-900 border-b border-slate-800 text-[11px] font-mono text-slate-400">
          <span class="font-bold text-indigo-400 uppercase">{{ block.language || 'code' }}</span>
          <button @click="copyCode(block.content)" class="hover:text-white transition flex items-center gap-1 text-[10px]">
            <span>{{ copiedIdx === idx ? '✓ Copied' : 'Copy Code' }}</span>
          </button>
        </div>
        <pre class="p-4 font-mono text-xs text-emerald-400 overflow-x-auto leading-relaxed">{{ block.content }}</pre>
      </div>

      <!-- Heading 1/2/3 -->
      <h3 v-else-if="block.type === 'h2' || block.type === 'h3'" class="text-sm font-bold text-slate-100 mt-4 mb-2 flex items-center gap-2 border-b border-slate-800 pb-1">
        <span class="text-indigo-400 font-bold">#</span>
        <span>{{ block.content }}</span>
      </h3>

      <!-- Comparison Table -->
      <div v-else-if="block.type === 'table'" class="my-3 overflow-x-auto rounded-xl border border-slate-800">
        <table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="bg-slate-900 border-b border-slate-800 text-indigo-300 font-bold">
              <th v-for="(col, cIdx) in block.headers" :key="cIdx" class="p-2.5">{{ col }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, rIdx) in block.rows" :key="rIdx" class="border-b border-slate-800/60 hover:bg-slate-900/40">
              <td v-for="(cell, cIdx) in row" :key="cIdx" class="p-2.5 text-slate-300 font-mono">{{ cell }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Bullet List -->
      <ul v-else-if="block.type === 'ul'" class="space-y-1 list-disc list-inside text-slate-300 pl-2 my-2">
        <li v-for="(item, iIdx) in block.items" :key="iIdx" v-html="formatInlineMarkdown(item)"></li>
      </ul>

      <!-- Numbered List -->
      <ol v-else-if="block.type === 'ol'" class="space-y-1 list-decimal list-inside text-slate-300 pl-2 my-2">
        <li v-for="(item, iIdx) in block.items" :key="iIdx" v-html="formatInlineMarkdown(item)"></li>
      </ol>

      <!-- Standard Paragraph -->
      <p v-else class="text-slate-300 leading-relaxed font-sans" v-html="formatInlineMarkdown(block.content)"></p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  content: string
}>()

const copiedIdx = ref<number | null>(null)

const copyCode = (text: string) => {
  navigator.clipboard.writeText(text)
  copiedIdx.value = 100
  setTimeout(() => { copiedIdx.value = null }, 2000)
}

function formatInlineMarkdown(text: string): string {
  if (!text) return ''
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // Bold
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="text-slate-100 font-bold">$1</strong>')
  // Inline Code
  html = html.replace(/`(.*?)`/g, '<code class="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-emerald-400 font-mono text-[11px]">$1</code>')
  // Blockquote / Practice Answer Callout
  if (html.startsWith('&gt; ')) {
    html = `<blockquote class="border-l-2 border-indigo-500 pl-3 italic text-indigo-200 bg-indigo-500/10 p-2 rounded-r-lg my-2">${html.slice(5)}</blockquote>`
  }
  return html
}

interface ParsedBlock {
  type: 'code' | 'h2' | 'h3' | 'ul' | 'ol' | 'table' | 'paragraph';
  content?: any;
  language?: string;
  items?: string[];
  headers?: string[];
  rows?: string[][];
}

const parsedBlocks = computed<ParsedBlock[]>(() => {
  if (!props.content) return []
  const lines = props.content.split('\n')
  const blocks: ParsedBlock[] = []

  let inCode = false
  let codeLang = ''
  let codeBuffer: string[] = []

  let inTable = false
  let tableHeaders: string[] = []
  let tableRows: string[][] = []

  let inList = false
  let listType: 'ul' | 'ol' = 'ul'
  let listItems: string[] = []

  const flushList = () => {
    if (inList && listItems.length) {
      blocks.push({ type: listType, items: [...listItems] })
      listItems = []
      inList = false
    }
  }

  const flushTable = () => {
    if (inTable && tableHeaders.length) {
      blocks.push({ type: 'table', headers: [...tableHeaders], rows: [...tableRows] })
      tableHeaders = []
      tableRows = []
      inTable = false
    }
  }

  for (let line of lines) {
    const trimmed = line.trim()

    // Fenced Code Block Check
    if (trimmed.startsWith('```')) {
      flushList()
      flushTable()
      if (inCode) {
        blocks.push({ type: 'code', language: codeLang, content: codeBuffer.join('\n') })
        codeBuffer = []
        inCode = false
      } else {
        inCode = true
        codeLang = trimmed.slice(3).trim()
      }
      continue
    }

    if (inCode) {
      codeBuffer.push(line)
      continue
    }

    // Markdown Table Check
    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      flushList()
      if (trimmed.includes('---')) continue // Separator line
      const cells = trimmed.slice(1, -1).split('|').map(c => c.trim())
      if (!inTable) {
        inTable = true
        tableHeaders = cells
      } else {
        tableRows.push(cells)
      }
      continue
    } else {
      flushTable()
    }

    // Headings
    if (trimmed.startsWith('## ') || trimmed.startsWith('# ')) {
      flushList()
      blocks.push({ type: 'h2', content: trimmed.replace(/^#+\s*/, '') })
      continue
    }
    if (trimmed.startsWith('### ')) {
      flushList()
      blocks.push({ type: 'h3', content: trimmed.replace(/^###\s*/, '') })
      continue
    }

    // Bullet Lists
    if (trimmed.startsWith('* ') || trimmed.startsWith('- ')) {
      if (!inList || listType !== 'ul') {
        flushList()
        inList = true
        listType = 'ul'
      }
      listItems.push(trimmed.slice(2))
      continue
    }

    // Numbered Lists
    if (/^\d+\.\s/.test(trimmed)) {
      if (!inList || listType !== 'ol') {
        flushList()
        inList = true
        listType = 'ol'
      }
      listItems.push(trimmed.replace(/^\d+\.\s/, ''))
      continue
    }

    flushList()

    if (trimmed) {
      blocks.push({ type: 'paragraph', content: trimmed })
    }
  }

  if (inCode) {
    blocks.push({ type: 'code', language: codeLang, content: codeBuffer.join('\n') })
  }
  flushList()
  flushTable()

  return blocks
})
</script>
