<script>
  export let tree        // { courses: [...] }
  export let selected    // 現在選択中のノード
  export let onSelect    // (node) => void

  // 展開状態: "course-{i}" / "section-{i}-{j}" をキーに管理
  let expanded = {}

  function toggle(key) {
    expanded[key] = !expanded[key]
  }

  function selectNode(node) {
    onSelect(node)
  }

  function contentIcon(type) {
    switch (type) {
      case 'textbook':    return '📄'
      case 'assignment':  return '📝'
      case 'error':       return '⚠️'
      default:            return '📎'
    }
  }
</script>

<aside class="tree-panel">
  <div class="panel-header">
    <span class="panel-title">時間割</span>
  </div>

  <div class="tree-scroll">
    {#each tree.courses as course, ci}
      <div class="course-node">
        <!-- コース行 -->
        <button
          class="tree-row course-row"
          class:error={!!course.error}
          on:click={() => toggle(`course-${ci}`)}
        >
          <span class="chevron">{expanded[`course-${ci}`] ? '▾' : '▸'}</span>
          <span class="slot-badge">{course.slot || '–'}</span>
          <span class="course-name">{course.name}</span>
        </button>

        {#if expanded[`course-${ci}`]}
          {#if course.error}
            <div class="error-msg">取得エラー: {course.error}</div>
          {:else}
            {#each course.sections as section, si}
              <div class="section-node">
                <!-- セクション行 -->
                <button
                  class="tree-row section-row"
                  on:click={() => toggle(`section-${ci}-${si}`)}
                >
                  <span class="chevron">{expanded[`section-${ci}-${si}`] ? '▾' : '▸'}</span>
                  <span class="section-name">{section.name}</span>
                </button>

                {#if expanded[`section-${ci}-${si}`]}
                  {#each section.contents as content}
                    <button
                      class="tree-row content-row"
                      class:selected={selected === content}
                      on:click={() => selectNode(content)}
                    >
                      <span class="icon">{contentIcon(content.type)}</span>
                      <span class="content-name">{content.name}</span>
                    </button>
                  {/each}
                {/if}
              </div>
            {/each}
          {/if}
        {/if}
      </div>
    {/each}
  </div>
</aside>

<style>
  .tree-panel {
    width: 280px;
    min-width: 220px;
    max-width: 360px;
    height: 100vh;
    background: #111827;
    border-right: 1px solid #1f2937;
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
  }

  .panel-header {
    padding: 0.9rem 1rem;
    border-bottom: 1px solid #1f2937;
    background: #0d1117;
  }

  .panel-title {
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #6b7280;
  }

  .tree-scroll {
    flex: 1;
    overflow-y: auto;
    padding: 0.4rem 0;
  }

  .tree-row {
    display: flex;
    align-items: center;
    width: 100%;
    padding: 0.35rem 0.6rem;
    background: none;
    border: none;
    color: #d1d5db;
    font-size: 0.85rem;
    text-align: left;
    cursor: pointer;
    gap: 0.4rem;
    border-radius: 4px;
    transition: background 0.15s;
    line-height: 1.4;
  }

  .tree-row:hover {
    background: #1f2937;
  }

  .tree-row.selected {
    background: #1e3a5f;
    color: #60a5fa;
  }

  .course-row {
    font-weight: 600;
    color: #e5e7eb;
  }

  .course-row.error {
    color: #f87171;
  }

  .section-row {
    padding-left: 1.4rem;
    color: #9ca3af;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .content-row {
    padding-left: 2.4rem;
    font-size: 0.83rem;
  }

  .chevron {
    font-size: 0.7rem;
    width: 0.8rem;
    flex-shrink: 0;
    color: #6b7280;
  }

  .slot-badge {
    font-size: 0.7rem;
    background: #374151;
    color: #9ca3af;
    padding: 0.05rem 0.35rem;
    border-radius: 3px;
    flex-shrink: 0;
    font-weight: 700;
  }

  .course-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .section-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .content-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .icon {
    flex-shrink: 0;
    font-size: 0.9rem;
  }

  .error-msg {
    padding: 0.4rem 1rem;
    font-size: 0.78rem;
    color: #f87171;
  }
</style>
