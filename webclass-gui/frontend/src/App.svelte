<script>
  import { onMount } from 'svelte'
  import { CheckCredentials, GetTree } from '../wailsjs/go/main/App.js'
  import Login from './lib/Login.svelte'
  import TreePanel from './lib/TreePanel.svelte'
  import ContentPanel from './lib/ContentPanel.svelte'

  let phase = 'loading'   // 'loading' | 'login' | 'fetching' | 'ready' | 'error'
  let tree = null
  let selected = null
  let fetchError = ''

  onMount(async () => {
    const hasCredentials = await CheckCredentials()
    if (hasCredentials) {
      await fetchTree()
    } else {
      phase = 'login'
    }
  })

  async function fetchTree() {
    phase = 'fetching'
    fetchError = ''
    try {
      tree = await GetTree()
      phase = 'ready'
    } catch (e) {
      fetchError = String(e)
      phase = 'error'
    }
  }

  function onLoginSuccess() {
    fetchTree()
  }

  function onSelect(node) {
    selected = node
  }
</script>

{#if phase === 'loading'}
  <div class="splash">
    <p class="loading-text">起動中...</p>
  </div>

{:else if phase === 'login'}
  <Login onSuccess={onLoginSuccess} />

{:else if phase === 'fetching'}
  <div class="splash">
    <p class="loading-text">WebClass から資料情報を取得中...</p>
    <p class="loading-sub">数分かかることがあります</p>
  </div>

{:else if phase === 'error'}
  <div class="splash">
    <p class="error-text">取得に失敗しました</p>
    <pre class="error-detail">{fetchError}</pre>
    <button class="retry-btn" on:click={fetchTree}>再試行</button>
  </div>

{:else if phase === 'ready'}
  <div class="layout">
    <TreePanel {tree} {selected} {onSelect} />
    <ContentPanel node={selected} />
  </div>
{/if}

<style>
  :global(*, *::before, *::after) {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  :global(body) {
    background: #0d1117;
    color: #d1d5db;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 14px;
    overflow: hidden;
  }

  .layout {
    display: flex;
    height: 100vh;
    overflow: hidden;
  }

  .splash {
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.8rem;
    background: #0d1117;
  }

  .loading-text {
    font-size: 1rem;
    color: #9ca3af;
  }

  .loading-sub {
    font-size: 0.8rem;
    color: #6b7280;
  }

  .error-text {
    font-size: 1rem;
    color: #f87171;
  }

  .error-detail {
    font-size: 0.75rem;
    color: #6b7280;
    max-width: 500px;
    white-space: pre-wrap;
    word-break: break-all;
  }

  .retry-btn {
    padding: 0.5rem 1.2rem;
    background: #374151;
    color: #d1d5db;
    border: 1px solid #4b5563;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: background 0.2s;
  }

  .retry-btn:hover {
    background: #4b5563;
  }
</style>
