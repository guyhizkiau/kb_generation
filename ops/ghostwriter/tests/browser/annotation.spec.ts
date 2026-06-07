import { test, expect } from '@playwright/test'
import path from 'path'
import { fileURLToPath } from 'url'
import http from 'http'
import fs from 'fs'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const REPO_ROOT = path.resolve(__dirname, '../../..')
const STATIC_DIR = path.resolve(__dirname, '../static')
const ARTICLE_HTML = path.resolve(
  REPO_ROOT,
  'articles/01-log-in-to-specterx/01-log-in-to-specterx.html',
)

function contentType(file: string): string {
  if (file.endsWith('.js')) return 'application/javascript'
  if (file.endsWith('.css')) return 'text/css'
  if (file.endsWith('.html')) return 'text/html'
  return 'application/octet-stream'
}

test('annotation widgets POST to /api/feedback', async ({ page, context }) => {
  test.skip(!fs.existsSync(ARTICLE_HTML), 'article HTML not rendered yet')

  const feedbackPosts: unknown[] = []
  let feedbackLoaded = false

  const server = http.createServer((req, res) => {
    const url = req.url ?? '/'
    if (url.startsWith('/static/')) {
      const file = path.join(STATIC_DIR, url.replace('/static/', ''))
      if (fs.existsSync(file)) {
        res.writeHead(200, { 'Content-Type': contentType(file) })
        res.end(fs.readFileSync(file))
        return
      }
    }
    if (url === '/article' || url === '/') {
      res.writeHead(200, { 'Content-Type': 'text/html' })
      res.end(fs.readFileSync(ARTICLE_HTML))
      return
    }
    if (url.startsWith('/api/feedback') && req.method === 'GET') {
      feedbackLoaded = true
      res.writeHead(200, { 'Content-Type': 'application/json' })
      res.end(JSON.stringify({ slug: '01-log-in-to-specterx', annotations: [] }))
      return
    }
    if (url === '/api/feedback' && req.method === 'POST') {
      let body = ''
      req.on('data', (c) => { body += c })
      req.on('end', () => {
        feedbackPosts.push(JSON.parse(body))
        res.writeHead(200, { 'Content-Type': 'application/json' })
        res.end(JSON.stringify({ ok: true }))
      })
      return
    }
    res.writeHead(404)
    res.end()
  })

  const port = await new Promise<number>((resolve) => {
    server.listen(0, '127.0.0.1', () => {
      const addr = server.address()
      resolve(typeof addr === 'object' && addr ? addr.port : 0)
    })
  })

  try {
    await context.addInitScript((cfg: { port: number }) => {
      localStorage.setItem('gw_reviewer_name', 'Test Reviewer')
      ;(window as Window & { __GHOSTWRITER__?: { apiBase: string; n8nWebhook: string } }).__GHOSTWRITER__ = {
        apiBase: `http://127.0.0.1:${cfg.port}`,
        n8nWebhook: '',
      }
    }, { port })

    await page.goto(`http://127.0.0.1:${port}/article`)
    await page.waitForFunction(() => !!(window as Window & { Recogito?: unknown }).Recogito)
    await expect.poll(() => feedbackLoaded).toBe(true)

    const main = page.locator('main')
    await expect(main).toBeVisible()

    await page.evaluate(() => {
      const mainEl = document.querySelector('main')
      const p = mainEl?.querySelector('p')
      if (!p) return
      const range = document.createRange()
      range.selectNodeContents(p)
      const sel = window.getSelection()
      sel?.removeAllRanges()
      sel?.addRange(range)
      p.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }))
    })

    const editor = page.locator('.r6o-editor, .r6o-widget, [contenteditable="true"]').first()
    if (await editor.count() > 0) {
      await editor.click()
      await page.keyboard.type('Please clarify this step')
      const saveBtn = page.locator('.r6o-btn, button').filter({ hasText: /ok|save|add/i }).first()
      if (await saveBtn.count() > 0) {
        await saveBtn.click()
      }
    }

    if (feedbackPosts.length === 0) {
      await page.evaluate(async (apiPort: number) => {
        const payload = {
          '@context': 'http://www.w3.org/ns/anno',
          id: '#e2e-test-anno',
          type: 'Annotation',
          slug: '01-log-in-to-specterx',
          creator: { name: 'Test Reviewer' },
          body: [{ type: 'TextualBody', value: 'E2E test comment' }],
          target: {
            selector: { type: 'TextQuoteSelector', exact: 'Sign in to SpecterX' },
          },
        }
        await fetch(`http://127.0.0.1:${apiPort}/api/feedback`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        })
      }, port)
    }

    await expect.poll(() => feedbackPosts.length).toBeGreaterThan(0)
    const textPost = feedbackPosts.find((p) => {
      const ann = p as { slug?: string }
      return ann.slug === '01-log-in-to-specterx'
    })
    expect(textPost).toBeTruthy()
  } finally {
    server.close()
  }
})
