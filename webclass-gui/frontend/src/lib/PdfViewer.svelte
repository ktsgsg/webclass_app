<script>
  import { onMount, onDestroy } from 'svelte'
  import * as pdfjsLib from 'pdfjs-dist'
  import workerUrl from 'pdfjs-dist/build/pdf.worker.mjs?url'

  pdfjsLib.GlobalWorkerOptions.workerSrc = workerUrl

  export let bytes  // Uint8Array

  let container
  let pdfDoc = null
  let renderError = ''

  async function render() {
    renderError = ''
    if (!bytes || !container) return
    container.innerHTML = ''
    try {
      const loadingTask = pdfjsLib.getDocument({
        data: bytes.slice(),
        standardFontDataUrl: '/standard_fonts/',
        cMapUrl: '/cmaps/',
        cMapPacked: true,
      })
      pdfDoc = await loadingTask.promise
      for (let i = 1; i <= pdfDoc.numPages; i++) {
        const page = await pdfDoc.getPage(i)
        const viewport = page.getViewport({ scale: 1.5 })
        const canvas = document.createElement('canvas')
        canvas.width = viewport.width
        canvas.height = viewport.height
        canvas.className = 'pdf-page'
        container.appendChild(canvas)
        await page.render({
          canvasContext: canvas.getContext('2d'),
          viewport,
          canvas,
        }).promise
      }
    } catch (e) {
      renderError = String(e)
    }
  }

  $: if (bytes && container) render()

  onDestroy(() => {
    if (pdfDoc) pdfDoc.destroy()
  })
</script>

<div class="pdf-viewer" bind:this={container}>
  {#if renderError}
    <p class="err">PDF描画エラー: {renderError}</p>
  {/if}
</div>

<style>
  .pdf-viewer {
    flex: 1;
    overflow-y: auto;
    background: #1f2937;
    border-radius: 6px;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.6rem;
  }

  :global(.pdf-page) {
    max-width: 100%;
    height: auto;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
    background: white;
  }

  .err {
    color: #f87171;
    font-size: 0.85rem;
  }
</style>
