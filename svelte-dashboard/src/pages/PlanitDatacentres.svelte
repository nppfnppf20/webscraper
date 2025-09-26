<script>
  import { onMount } from 'svelte';
  import DataTable from '../components/DataTable.svelte';

  let datacentres = [];
  let loading = true;
  let error = '';
  let refreshing = false;
  let msg = '';

  // API functions
  async function fetchDatacentres() {
    const response = await fetch('http://127.0.0.1:8000/api/planit/datacentres');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  }

  async function refreshDatacentres() {
    const response = await fetch('http://127.0.0.1:8000/api/refresh/planit-dc', { method: 'POST' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  }

  // Filter function for medium/large projects and excluding conditions
  function filterDatacentres(data) {
    return data.filter(project => {
      // Filter for medium and large size only
      const size = (project.app_size || '').toLowerCase();
      const isMediumOrLarge = size.includes('medium') || size.includes('large');

      // Filter out conditions in type column
      const type = (project.app_type || '').toLowerCase();
      const hasConditions = type.includes('condition') || type.includes('discharge');

      return isMediumOrLarge && !hasConditions;
    });
  }

  // Load data on component mount
  onMount(async () => {
    try {
      const rawData = await fetchDatacentres();
      datacentres = filterDatacentres(rawData);
    } catch (e) {
      error = e?.message || 'Failed to load datacentres data';
    } finally {
      loading = false;
    }
  });

  // Refresh function
  async function refreshNow() {
    try {
      refreshing = true;
      msg = '';

      const result = await refreshDatacentres();

      if (!result.ok) {
        throw new Error(result.error || 'Refresh failed');
      }

      // Reload data after successful refresh
      const rawData = await fetchDatacentres();
      datacentres = filterDatacentres(rawData);
      msg = `✅ Refreshed in ${result.elapsed_s}s, found ${datacentres.length} filtered datacentre projects (${result.updated} total)`;

    } catch (e) {
      msg = `❌ ${e.message || 'Refresh failed'}`;
    } finally {
      refreshing = false;
    }
  }

  // Helper function to format dates
  function formatDate(dateStr) {
    if (!dateStr) return '';
    try {
      return new Date(dateStr).toLocaleDateString('en-GB');
    } catch {
      return dateStr;
    }
  }

  // Helper function to get status badge class
  function getStatusClass(status) {
    switch (status?.toLowerCase()) {
      case 'approved': return 'status-success';
      case 'refused': case 'rejected': return 'status-danger';
      case 'pending': return 'status-pending';
      default: return 'status-badge';
    }
  }

  // Helper function to truncate long text
  function truncateText(text, maxLength = 100) {
    if (!text) return '';
    return text.length > maxLength ? text.slice(0, maxLength) + '...' : text;
  }

  // Column definitions for DataTable
  const columns = [
    {
      key: 'name',
      label: 'Name',
      sortable: true,
      width: '20%',
      render: (value, item) => `
        <div class="project-title" title="${value || ''}">
          ${truncateText(value, 80)}
        </div>
      `
    },
    {
      key: 'uid',
      label: 'UID',
      sortable: true,
      width: '8%',
      render: (value) => `<small class="uid">${value || ''}</small>`
    },
    {
      key: 'description',
      label: 'Description',
      sortable: true,
      width: '25%',
      render: (value, item) => `
        <div class="description" title="${value || ''}">
          ${truncateText(value, 120)}
        </div>
      `
    },
    {
      key: 'area_name',
      label: 'Authority',
      sortable: true,
      width: '12%',
      render: (value, item) => value || item.authority || ''
    },
    {
      key: 'address',
      label: 'Address',
      sortable: true,
      width: '15%',
      render: (value) => `<div class="address">${value || ''}</div>`
    },
    {
      key: 'postcode',
      label: 'Postcode',
      sortable: true,
      width: '8%',
      render: (value) => `<small class="postcode">${value || ''}</small>`
    },
    {
      key: 'app_state',
      label: 'Status',
      sortable: true,
      width: '10%',
      render: (value, item) => {
        const status = value || item.status || 'Unknown';
        const statusClass = getStatusClass(status);
        let html = `<span class="status-badge ${statusClass}">${status}</span>`;
        if (item.decision && item.decision !== status) {
          html += `<br><small class="decision">${item.decision}</small>`;
        }
        return html;
      }
    },
    {
      key: 'app_type',
      label: 'Type',
      sortable: true,
      width: '8%',
      render: (value) => value ? `<span class="app-type">${value}</span>` : ''
    },
    {
      key: 'app_size',
      label: 'Size',
      sortable: true,
      width: '8%',
      render: (value) => value ? `<span class="app-size">${value}</span>` : ''
    },
    {
      key: 'start_date',
      label: 'Start Date',
      sortable: true,
      width: '10%',
      render: (value) => formatDate(value)
    },
    {
      key: 'decided_date',
      label: 'Decision Date',
      sortable: true,
      width: '10%',
      render: (value) => formatDate(value)
    },
    {
      key: 'coordinates',
      label: 'Coordinates',
      sortable: false,
      width: '12%',
      render: (value, item) => {
        if (item.lat && item.lng) {
          return `<small class="coordinates">${parseFloat(item.lat).toFixed(4)}, ${parseFloat(item.lng).toFixed(4)}</small>`;
        }
        return '<small class="coordinates">-</small>';
      }
    },
    {
      key: 'link',
      label: 'Link',
      sortable: false,
      width: '8%',
      align: 'center',
      render: (value) => value ? `<a href="${value}" target="_blank" rel="noreferrer" class="link-button">View</a>` : ''
    }
  ];
</script>

<div class="page-header">
  <h1>PlanIt Data Centres</h1>
  <p>Medium/Large data centre projects from last 3 months using official PlanIt API - filtered to exclude conditions</p>
</div>

<div class="toolbar">
  <button class="button-primary" on:click={refreshNow} disabled={refreshing}>
    {#if refreshing}<span class="loading-spinner"></span>{/if}
    {refreshing ? 'Refreshing…' : 'Refresh Data'}
  </button>
  {#if msg}<span class="msg">{@html msg}</span>{/if}
</div>

{#if !loading && !error && datacentres.length > 0}
  {@const statusCounts = datacentres.reduce((acc, r) => { acc[r.app_state || 'Unknown'] = (acc[r.app_state || 'Unknown'] || 0) + 1; return acc; }, {})}
  {@const authorityCounts = datacentres.reduce((acc, r) => { acc[r.area_name || 'Unknown'] = (acc[r.area_name || 'Unknown'] || 0) + 1; return acc; }, {})}

  <div class="results-summary">
    <p><strong>{datacentres.length}</strong> datacentre projects found</p>

    <div class="stats">
      <div class="stat-group">
        <strong>Status:</strong>
        {#each Object.entries(statusCounts).slice(0, 4) as [status, count]}
          <span class="stat-item {getStatusClass(status)}">{status}: {count}</span>
        {/each}
      </div>

      <div class="stat-group">
        <strong>Top Authorities:</strong>
        {#each Object.entries(authorityCounts).slice(0, 3) as [authority, count]}
          <span class="stat-item">{authority}: {count}</span>
        {/each}
      </div>
    </div>
  </div>
{/if}

<DataTable
  data={datacentres}
  {columns}
  {loading}
  {error}
  searchPlaceholder="Search datacentre projects..."
  emptyMessage="No datacentre projects found for the last 3 months. Try refreshing the data."
  showSearch={true}
  showActions={false}
  minWidth="1400px"
/>

<style>
  .page-header {
    margin-bottom: 2rem;
  }

  .page-header h1 {
    color: var(--text-color);
    margin-bottom: 0.5rem;
  }

  .page-header p {
    color: var(--dark-gray);
    font-size: 0.95rem;
    margin: 0;
  }

  .toolbar {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 16px 0;
    padding: 12px;
    background-color: var(--light-gray);
    border-radius: var(--border-radius);
  }

  .msg {
    color: var(--dark-gray);
    font-size: 0.9rem;
  }

  .results-summary {
    background-color: var(--light-gray);
    padding: 1rem;
    border-radius: var(--border-radius);
    margin-bottom: 1rem;
  }

  .stats {
    margin-top: 0.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .stat-group {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
  }

  .stat-item {
    font-size: 0.85rem;
    padding: 0.25rem 0.5rem;
    background-color: rgba(0, 0, 0, 0.05);
    border-radius: 3px;
    white-space: nowrap;
  }

  /* Custom styles for DataTable content */
  :global(.project-title) {
    font-weight: 500;
    color: var(--text-color);
    line-height: 1.3;
  }

  :global(.uid) {
    color: var(--dark-gray);
    font-family: monospace;
    font-size: 0.8rem;
  }

  :global(.description) {
    font-size: 0.9rem;
    line-height: 1.3;
    color: var(--text-color);
  }

  :global(.address) {
    font-size: 0.9rem;
  }

  :global(.postcode) {
    color: var(--dark-gray);
    font-weight: 500;
  }

  :global(.decision) {
    color: var(--dark-gray);
    font-style: italic;
  }

  :global(.coordinates) {
    color: var(--dark-gray);
    font-family: monospace;
    font-size: 0.8rem;
  }

  :global(.app-type), :global(.app-size) {
    font-size: 0.85rem;
    padding: 0.15rem 0.4rem;
    border-radius: 3px;
    background-color: rgba(13, 110, 253, 0.1);
    color: var(--primary-color);
    font-weight: 500;
    display: inline-block;
  }

  :global(.link-button) {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    background-color: var(--primary-color);
    color: white;
    text-decoration: none;
    border-radius: var(--border-radius);
    font-size: 0.85rem;
    transition: background-color 0.15s ease-in-out;
  }

  :global(.link-button:hover) {
    background-color: #0b5ed7;
    color: white;
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .stat-group {
      flex-direction: column;
      align-items: flex-start;
    }

    .toolbar {
      flex-direction: column;
      align-items: stretch;
    }

    .table-container {
      font-size: 0.85rem;
    }
  }
</style>

