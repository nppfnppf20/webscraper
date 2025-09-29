<script>
  import { createEventDispatcher, onMount, afterUpdate } from 'svelte';

  // Props for table configuration
  export let data = [];
  export let columns = [];
  export let isLoading = false;
  export let error = null;
  export let searchPlaceholder = "Search...";
  export let emptyMessage = "No data available";
  export let showSearch = true;
  export let showActions = false;
  export let minWidth = "800px";

  // Table column interface
  export let TableColumn = {
    key: '',
    label: '',
    sortable: false,
    width: '',
    align: 'left', // 'left' | 'center' | 'right'
    className: '',
    render: null, // (value: any, item: any) => string
    colspan: 1,
    rowspan: 1,
    subHeaders: []
  };

  // State
  let searchText = '';
  let sortKey = '';
  let sortDirection = 'asc';
  let displayData = [];

  // Scrollbar synchronization
  let topScrollContainer;
  let tableContainer;

  const dispatch = createEventDispatcher();

  // Helper function to get nested property value
  function getNestedValue(obj, path) {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  }

  // Sorting function
  function setSortKey(key) {
    if (sortKey === key) {
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      sortKey = key;
      sortDirection = 'asc';
    }
  }

  // Reactive data processing
  $: displayData = (() => {
    let result = [...data];

    // Apply search filter
    if (searchText.trim() !== '') {
      const lowercasedFilter = searchText.toLowerCase();
      result = result.filter(item =>
        columns.some(column => {
          const value = getNestedValue(item, column.key);
          return value && String(value).toLowerCase().includes(lowercasedFilter);
        })
      );
    }

    // Apply sorting
    if (sortKey) {
      result.sort((a, b) => {
        const valA = getNestedValue(a, sortKey);
        const valB = getNestedValue(b, sortKey);

        if (valA === null || valA === undefined) return 1;
        if (valB === null || valB === undefined) return -1;

        let comparison = 0;
        const numA = Number(valA);
        const numB = Number(valB);

        if (!isNaN(numA) && !isNaN(numB)) {
          comparison = numA - numB;
        } else if (typeof valA === 'string' && typeof valB === 'string') {
          comparison = valA.localeCompare(valB);
        }

        return sortDirection === 'asc' ? comparison : -comparison;
      });
    }

    return result;
  })();

  // Event handlers
  function handleRowClick(item, index) {
    dispatch('rowClick', { item, index });
  }

  function handleAction(action, item) {
    dispatch('action', { action, item });
  }

  function handleRetry() {
    dispatch('retry');
  }

  // Scroll synchronization
  let isScrolling = false;

  function syncTopScroll() {
    if (tableContainer && topScrollContainer && !isScrolling) {
      isScrolling = true;
      tableContainer.scrollLeft = topScrollContainer.scrollLeft;
      setTimeout(() => { isScrolling = false; }, 10);
    }
  }

  function syncTableScroll() {
    if (tableContainer && topScrollContainer && !isScrolling) {
      isScrolling = true;
      topScrollContainer.scrollLeft = tableContainer.scrollLeft;
      setTimeout(() => { isScrolling = false; }, 10);
    }
  }

  // Update top scrollbar width to match table's actual scrollable width
  function updateTopScrollbarWidth() {
    if (tableContainer && topScrollContainer) {
      const tableScrollWidth = tableContainer.scrollWidth;
      const topScrollContent = topScrollContainer.querySelector('.top-scrollbar-content');
      if (topScrollContent) {
        topScrollContent.style.width = `${tableScrollWidth}px`;
      }
    }
  }

  // Update scrollbar width when component mounts or data changes
  onMount(() => {
    setTimeout(updateTopScrollbarWidth, 100);
  });

  afterUpdate(() => {
    setTimeout(updateTopScrollbarWidth, 100);
  });
</script>

<div class="data-table-container">
  {#if error}
    <div class="error-message">
      <p>{error}</p>
      <button on:click={handleRetry} class="retry-btn">Retry</button>
    </div>
  {:else if isLoading}
    <div class="loading-message">
      <span class="loading-spinner"></span>
      <p>Loading data...</p>
    </div>
  {:else}
    {#if showSearch}
      <div class="controls-container">
        <input
          type="text"
          bind:value={searchText}
          placeholder={searchPlaceholder}
          class="filter-input"
        />
        <slot name="controls" />
      </div>
    {/if}

    {#if displayData.length === 0 && searchText}
      <div class="empty-state">
        <p>No data matches your search "{searchText}".</p>
      </div>
    {:else if displayData.length === 0}
      <div class="empty-state">
        <p>{emptyMessage}</p>
      </div>
    {:else}
      <!-- Top scrollbar -->
      <div class="top-scrollbar-container" bind:this={topScrollContainer} on:scroll={syncTopScroll}>
        <div class="top-scrollbar-content"></div>
      </div>

      <div class="table-container" bind:this={tableContainer} on:scroll={syncTableScroll}>
        <table class="data-table" style="min-width: {minWidth}">
          <thead>
            <!-- Main headers row -->
            <tr>
              {#each columns as column}
                <th
                  rowspan={column.rowspan || (column.subHeaders ? 1 : 2)}
                  colspan={column.colspan || 1}
                  class={column.className || ''}
                  class:text-center={column.align === 'center'}
                  class:text-right={column.align === 'right'}
                >
                  {#if column.sortable}
                    <button on:click={() => setSortKey(column.key)} class="sort-button">
                      {column.label}
                      {#if sortKey === column.key}
                        <span class="sort-indicator">{sortDirection === 'asc' ? '▲' : '▼'}</span>
                      {/if}
                    </button>
                  {:else}
                    {column.label}
                  {/if}
                </th>
              {/each}

              {#if showActions}
                <th rowspan="2" class="actions-header">Actions</th>
              {/if}
            </tr>

            <!-- Sub-headers row if any column has subHeaders -->
            {#if columns.some(col => col.subHeaders)}
              <tr>
                {#each columns as column}
                  {#if column.subHeaders}
                    {#each column.subHeaders as subHeader}
                      <th
                        class="sub-header {subHeader.className || ''}"
                        class:text-center={subHeader.align === 'center'}
                        class:text-right={subHeader.align === 'right'}
                      >
                        {#if subHeader.sortable}
                          <button on:click={() => setSortKey(subHeader.key)} class="sort-button">
                            {subHeader.label}
                            {#if sortKey === subHeader.key}
                              <span class="sort-indicator">{sortDirection === 'asc' ? '▲' : '▼'}</span>
                            {/if}
                          </button>
                        {:else}
                          {subHeader.label}
                        {/if}
                      </th>
                    {/each}
                  {/if}
                {/each}
              </tr>
            {/if}
          </thead>
          <tbody>
            {#each displayData as item, index}
              <tr on:click={() => handleRowClick(item, index)} class="table-row">
                {#each columns as column}
                  {#if !column.subHeaders}
                    <td
                      class={column.className || ''}
                      class:text-center={column.align === 'center'}
                      class:text-right={column.align === 'right'}
                      style={column.width ? `width: ${column.width}` : ''}
                    >
                      <slot name="cell" {column} {item} {index}>
                        {#if column.render}
                          {@html column.render(getNestedValue(item, column.key), item)}
                        {:else}
                          {getNestedValue(item, column.key) ?? '-'}
                        {/if}
                      </slot>
                    </td>
                  {:else}
                    {#each column.subHeaders as subColumn}
                      <td
                        class="{subColumn.className || ''}"
                        class:text-center={subColumn.align === 'center'}
                        class:text-right={subColumn.align === 'right'}
                        style={subColumn.width ? `width: ${subColumn.width}` : ''}
                      >
                        <slot name="cell" column={subColumn} {item} {index}>
                          {#if subColumn.render}
                            {@html subColumn.render(getNestedValue(item, subColumn.key), item)}
                          {:else}
                            {getNestedValue(item, subColumn.key) ?? '-'}
                          {/if}
                        </slot>
                      </td>
                    {/each}
                  {/if}
                {/each}

                {#if showActions}
                  <td class="actions-cell">
                    <slot name="actions" {item} {index} {handleAction}>
                      <button class="action-btn" on:click|stopPropagation={() => handleAction('edit', item)}>
                        Edit
                      </button>
                      <button class="action-btn delete" on:click|stopPropagation={() => handleAction('delete', item)}>
                        Delete
                      </button>
                    </slot>
                  </td>
                {/if}
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  {/if}
</div>

<style>
  .data-table-container {
    padding: 0;
  }

  .error-message, .loading-message {
    padding: 1rem;
    border-radius: var(--border-radius);
    text-align: center;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
  }

  .error-message {
    background-color: #fed7d7;
    border: 1px solid #feb2b2;
    color: #c53030;
  }

  .loading-message {
    background-color: var(--light-gray);
    border: 1px solid var(--border-color);
    color: var(--text-color);
  }

  .retry-btn {
    padding: 0.5rem 1rem;
    background: #c53030;
    color: white;
    border: none;
    border-radius: var(--border-radius);
    cursor: pointer;
    font-size: 0.9rem;
  }

  .controls-container {
    margin-bottom: 1.5rem;
    display: flex;
    gap: 1rem;
    align-items: center;
  }

  .filter-input {
    padding: 0.75rem 1rem;
    font-size: 0.9rem;
    border-radius: var(--border-radius);
    border: 1px solid var(--border-color);
    width: 100%;
    max-width: 400px;
    background: white;
  }

  .filter-input:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 2px rgba(13, 110, 253, 0.1);
  }

  .empty-state {
    padding: 2rem;
    background-color: var(--light-gray);
    border: 1px dashed var(--border-color);
    border-radius: var(--border-radius);
    text-align: center;
    color: var(--dark-gray);
  }

  .table-container {
    overflow-x: auto;
    overflow-y: hidden;
    border: 1px solid var(--border-color);
    border-top: none;
    border-radius: 0 0 var(--border-radius) var(--border-radius);
    background: white;
    contain: layout style paint;
    will-change: scroll-position;
    transform: translateZ(0);
    overflow-anchor: auto;
    /* Enhanced scrollbar styling */
    scrollbar-width: thin;
    scrollbar-color: #cbd5e0 #f7fafc;
  }

  /* WebKit scrollbar styling for better visibility */
  .table-container::-webkit-scrollbar {
    height: 8px;
  }

  .table-container::-webkit-scrollbar-track {
    background: #f1f5f9;
    border-radius: 4px;
  }

  .table-container::-webkit-scrollbar-thumb {
    background: #cbd5e0;
    border-radius: 4px;
    transition: background 0.2s ease;
  }

  .table-container::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
  }

  .table-container::-webkit-scrollbar-thumb:active {
    background: #64748b;
  }

  /* Top scrollbar styling */
  .top-scrollbar-container {
    overflow-x: auto;
    overflow-y: hidden;
    border: 1px solid var(--border-color);
    border-bottom: none;
    border-radius: var(--border-radius) var(--border-radius) 0 0;
    background: #f8f9fa;
    height: 20px;
    /* Enhanced scrollbar styling - same as table container */
    scrollbar-width: thin;
    scrollbar-color: #cbd5e0 #f7fafc;
  }

  /* Top scrollbar WebKit styling */
  .top-scrollbar-container::-webkit-scrollbar {
    height: 8px;
  }

  .top-scrollbar-container::-webkit-scrollbar-track {
    background: #f1f5f9;
    border-radius: 4px;
  }

  .top-scrollbar-container::-webkit-scrollbar-thumb {
    background: #cbd5e0;
    border-radius: 4px;
    transition: background 0.2s ease;
  }

  .top-scrollbar-container::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
  }

  .top-scrollbar-container::-webkit-scrollbar-thumb:active {
    background: #64748b;
  }

  .top-scrollbar-content {
    height: 1px;
    background: transparent;
  }

  .data-table {
    width: 100%;
    border-collapse: collapse;
  }

  .data-table th,
  .data-table td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
    vertical-align: top;
    font-size: 0.85rem;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }

  .data-table th {
    background-color: var(--light-gray);
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-color);
    vertical-align: middle;
    position: sticky;
    top: 0;
    z-index: 10;
    will-change: transform;
    transform: translateZ(0);
    backface-visibility: hidden;
  }

  .sort-button {
    background: none;
    border: none;
    padding: 0;
    margin: 0;
    font: inherit;
    color: inherit;
    cursor: pointer;
    text-align: left;
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .sort-button:hover {
    color: var(--primary-color);
  }

  .sort-indicator {
    margin-left: 0.5rem;
    font-size: 0.7rem;
    color: var(--primary-color);
  }

  .sub-header {
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    border-top: 1px solid var(--border-color);
    text-align: center;
  }

  .sub-header .sort-button {
    justify-content: center;
  }

  .data-table tbody tr:last-child td {
    border-bottom: none;
  }

  .table-row:hover {
    background-color: var(--light-gray);
    cursor: pointer;
  }

  .text-center {
    text-align: center;
  }

  .text-right {
    text-align: right;
  }

  .divider-left {
    border-left: 1px solid var(--border-color);
  }

  .divider-right {
    border-right: 1px solid var(--border-color);
  }

  .actions-header {
    text-align: center;
    white-space: nowrap;
  }

  .actions-cell {
    text-align: center;
    white-space: nowrap;
  }

  .action-btn {
    display: inline-block;
    padding: 0.4rem 0.8rem;
    margin: 0.2rem 0.2rem 0.2rem 0;
    font-size: 0.85rem;
    font-weight: 500;
    border-radius: var(--border-radius);
    text-decoration: none;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
    border: 1px solid var(--border-color);
    background: white;
    color: var(--text-color);
  }

  .action-btn:last-child {
    margin-right: 0;
  }

  .action-btn:hover {
    background-color: var(--light-gray);
    color: var(--primary-color);
  }

  .action-btn.delete {
    color: #e53e3e;
    border-color: #e53e3e;
  }

  .action-btn.delete:hover {
    background-color: #fed7d7;
    color: #c53030;
  }
</style>