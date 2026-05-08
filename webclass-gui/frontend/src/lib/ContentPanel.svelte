<script>
  import { DownloadPDF, GetCacheDir } from '../../wailsjs/go/main/App.js'

  export let node  // 選択されたコンテンツノード

  let loading = false
  let pdfPath = null
  let error = ''

  // ノードが変わったらリセット
  $: if (node) {
    pdfPath = null
    error = ''
    loading = false
  }

  async function openPDF(query, filename) {
    loading = true
    error = ''
    try {
      const cacheDir = await GetCacheDir()
      const savePath = `${cacheDir}/${filename}.pdf`
      await DownloadPDF(query, savePath)
      pdfPath = savePath
    } catch (e) {
      error = 'PDFの取得に失敗しました: ' + e
    } finally {
      loading = false
    }
  }

  function safeFilename(s) {
    return s.replace(/[^a-zA-Z0-9぀-鿿_-]/g, '_')
  }
</script>

<div class="content-panel">
  {#if !node}
    <div class="empty">
      <p>左のツリーから資料を選択してください</p>
    </div>

  {:else if node.type === 'error'}
    <div class="error-view">
      <h2>⚠️ 取得エラー</h2>
      <p>{node.reason}</p>
    </div>

  {:else if node.type === 'unknown'}
    <div class="unknown-view">
      <h2>{node.name}</h2>
      <p>このコンテンツ形式には対応していません。</p>
    </div>

  {:else if node.type === 'assignment'}
    <div class="assignment-view">
      <h2>📝 {node.name}</h2>
      {#if pdfPath}
        <iframe
          title={node.name}
          src="file://{pdfPath}"
          class="pdf-frame"
        ></iframe>
      {:else}
        <button class="btn-primary" on:click={() => openPDF(node.download_query, safeFilename(node.name))} disabled={loading}>
          {loading ? '取得中...' : 'PDFを表示'}
        </button>
        {#if error}<p class="error">{error}</p>{/if}
      {/if}
    </div>

  {:else if node.type === 'textbook'}
    <div class="textbook-view">
      <h2>📄 {node.name}</h2>
      {#if pdfPath}
        <iframe
          title={node.name}
          src="file://{pdfPath}"
          class="pdf-frame"
        ></iframe>
      {:else}
        <ul class="chapter-list">
          {#each node.items as item, i}
            <li>
              <button
                class="chapter-btn"
                on:click={() => openPDF(item.query, safeFilename(node.name + '_' + item.chapter))}
                disabled={loading}
              >
                {item.chapter}
              </button>
            </li>
          {/each}
        </ul>
        {#if loading}<p class="loading">取得中...</p>{/if}
        {#if error}<p class="error">{error}</p>{/if}
      {/if}
    </div>
  {/if}
</div>

<style>
  .content-panel {
    flex: 1;
    height: 100vh;
    background: #0d1117;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .empty {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #4b5563;
    font-size: 0.9rem;
  }

  .assignment-view,
  .textbook-view,
  .error-view,
  .unknown-view {
    padding: 1.5rem 2rem;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  h2 {
    margin: 0;
    font-size: 1.1rem;
    color: #e5e7eb;
    font-weight: 600;
  }

  .pdf-frame {
    flex: 1;
    border: none;
    border-radius: 6px;
    background: #1f2937;
  }

  .btn-primary {
    padding: 0.6rem 1.4rem;
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    align-self: flex-start;
    transition: background 0.2s;
  }

  .btn-primary:hover:not(:disabled) {
    background: #1d4ed8;
  }

  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .chapter-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .chapter-btn {
    display: block;
    width: 100%;
    padding: 0.6rem 0.9rem;
    background: #1f2937;
    color: #d1d5db;
    border: 1px solid #374151;
    border-radius: 6px;
    font-size: 0.87rem;
    text-align: left;
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s;
  }

  .chapter-btn:hover:not(:disabled) {
    background: #374151;
    border-color: #4b5563;
    color: #f3f4f6;
  }

  .chapter-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .error {
    color: #f87171;
    font-size: 0.83rem;
    margin: 0;
  }

  .loading {
    color: #9ca3af;
    font-size: 0.83rem;
    margin: 0;
  }

  .error-view h2 {
    color: #f87171;
  }

  .error-view p,
  .unknown-view p {
    color: #9ca3af;
    font-size: 0.87rem;
  }
</style>
