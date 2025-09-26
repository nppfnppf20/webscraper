<script>
  import { onMount } from 'svelte';

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

{#if loading}
  <div class="text-center p-4">
    <span class="loading-spinner"></span>
    <p class="mt-2">Loading datacentres data…</p>
  </div>
{:else if error}
  <div class="alert alert-danger">{error}</div>
{:else}
  <div class="results-summary">
    <p><strong>{datacentres.length}</strong> datacentre projects found</p>
    {#if datacentres.length > 0}
      {@const statusCounts = datacentres.reduce((acc, r) => { acc[r.app_state || 'Unknown'] = (acc[r.app_state || 'Unknown'] || 0) + 1; return acc; }, {})}
      {@const authorityCounts = datacentres.reduce((acc, r) => { acc[r.area_name || 'Unknown'] = (acc[r.area_name || 'Unknown'] || 0) + 1; return acc; }, {})}

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
    {/if}
  </div>

  {#if datacentres.length > 0}
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>UID</th>
            <th>Description</th>
            <th>Authority</th>
            <th>Address</th>
            <th>Postcode</th>
            <th>Status</th>
            <th>Type</th>
            <th>Size</th>
            <th>Start Date</th>
            <th>Decision Date</th>
            <th>Coordinates</th>
            <th>Link</th>
          </tr>
        </thead>
        <tbody>
          {#each datacentres as project}
            <tr>
              <td>
                <div class="project-title" title={project.name}>
                  {truncateText(project.name, 80)}
                </div>
              </td>
              <td>
                <small class="uid">{project.uid || ''}</small>
              </td>
              <td>
                <div class="description" title={project.description}>
                  {truncateText(project.description, 120)}
                </div>
              </td>
              <td>{project.area_name || project.authority || ''}</td>
              <td>
                <div class="address">
                  {project.address || ''}
                </div>
              </td>
              <td>
                <small class="postcode">{project.postcode || ''}</small>
              </td>
              <td>
                <span class="status-badge {getStatusClass(project.app_state || project.status)}">
                  {project.app_state || project.status || 'Unknown'}
                </span>
                {#if project.decision && project.decision !== (project.app_state || project.status)}
                  <br><small class="decision">{project.decision}</small>
                {/if}
              </td>
              <td>
                {#if project.app_type}
                  <span class="app-type">{project.app_type}</span>
                {/if}
              </td>
              <td>
                {#if project.app_size}
                  <span class="app-size">{project.app_size}</span>
                {/if}
              </td>
              <td>{formatDate(project.start_date)}</td>
              <td>{formatDate(project.decided_date)}</td>
              <td>
                {#if project.lat && project.lng}
                  <small class="coordinates">
                    {parseFloat(project.lat).toFixed(4)}, {parseFloat(project.lng).toFixed(4)}
                  </small>
                {:else}
                  <small class="coordinates">-</small>
                {/if}
              </td>
              <td>
                {#if project.link}
                  <a href={project.link} target="_blank" rel="noreferrer" class="link-button">View</a>
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {:else}
    <div class="alert alert-info">
      No datacentre projects found for the last 3 months. Try refreshing the data.
    </div>
  {/if}
{/if}

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

  .table-container {
    overflow-x: auto;
    border-radius: var(--border-radius);
    border: 1px solid var(--border-color);
  }

  .project-title {
    font-weight: 500;
    color: var(--text-color);
    line-height: 1.3;
  }

  .uid {
    color: var(--dark-gray);
    font-family: monospace;
    font-size: 0.8rem;
  }

  .description {
    font-size: 0.9rem;
    line-height: 1.3;
    color: var(--text-color);
  }

  .address {
    font-size: 0.9rem;
  }

  .postcode {
    color: var(--dark-gray);
    font-weight: 500;
  }

  .decision {
    color: var(--dark-gray);
    font-style: italic;
  }

  .coordinates {
    color: var(--dark-gray);
    font-family: monospace;
    font-size: 0.8rem;
  }

  .app-type, .app-size {
    font-size: 0.85rem;
    padding: 0.15rem 0.4rem;
    border-radius: 3px;
    background-color: rgba(13, 110, 253, 0.1);
    color: var(--primary-color);
    font-weight: 500;
    display: inline-block;
  }

  .link-button {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    background-color: var(--primary-color);
    color: white;
    text-decoration: none;
    border-radius: var(--border-radius);
    font-size: 0.85rem;
    transition: background-color 0.15s ease-in-out;
  }

  .link-button:hover {
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

