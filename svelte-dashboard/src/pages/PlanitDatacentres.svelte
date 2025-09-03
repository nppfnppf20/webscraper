<script>
  import { onMount } from 'svelte';
  import { fetchPlanitDatacentres } from '../lib/api.js';

  let rows = [];
  let loading = true;
  let error = '';
  let refreshing = false;
  let refreshMsg = '';
  let errorMsg = '';

  async function loadData() {
    loading = true;
    error = '';
    try {
      rows = await fetchPlanitDatacentres();
    } catch (e) {
      error = e?.message || 'Failed to load data';
    } finally {
      loading = false;
    }
  }

  async function refreshPlanit() {
    refreshing = true;
    refreshMsg = '';
    errorMsg = '';
    try {
      const res = await fetch('http://127.0.0.1:8000/api/refresh/planit-dc', { method: 'POST' });
      if (!res.ok) throw new Error(`Refresh failed: ${res.status}`);
      const body = await res.json();
      if (body?.ok) {
        refreshMsg = `Updated ${body.updated} rows in ${body.elapsed_s}s`;
      } else if (body?.error === 'already_running') {
        refreshMsg = 'Already running, try again shortly';
      } else {
        refreshMsg = body?.status || 'Triggered';
      }
      await loadData();
    } catch (e) {
      errorMsg = e?.message || 'Failed to refresh';
    } finally {
      refreshing = false;
    }
  }

  onMount(loadData);
</script>

<div class="toolbar" style="margin: 0 0 12px 0; display: flex; gap: 8px; align-items: center;">
  <button on:click={refreshPlanit} disabled={refreshing || loading}>
    {refreshing ? 'Refreshing…' : 'Refresh'}
  </button>
  {#if refreshMsg}<span style="color: #2d7;">{refreshMsg}</span>{/if}
  {#if errorMsg}<span style="color: #c33;">{errorMsg}</span>{/if}
</div>

{#if loading}
  <p>Loading…</p>
{:else if error}
  <p style="color:red">{error}</p>
{:else}
  <table>
    <thead>
      <tr>
        <th>Authority</th>
        <th>Title</th>
        <th>Start Date</th>
        <th>Status</th>
        <th>Decision</th>
        <th>Link</th>
      </tr>
    </thead>
    <tbody>
      {#each rows as r}
        <tr>
          <td>{r.authority}</td>
          <td title={r.description}>{r.title}</td>
          <td>{r.start_date}</td>
          <td>{r.app_state}</td>
          <td>{r.decision}</td>
          <td>{#if r.link}<a href={r.link} target="_blank" rel="noreferrer">open</a>{/if}</td>
        </tr>
      {/each}
    </tbody>
  </table>
{/if}

<style>
  table { width: 100%; border-collapse: collapse; }
  th, td { border: 1px solid #ddd; padding: 8px; }
  th { background: #f5f5f5; text-align: left; }
  td[title] { max-width: 420px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>

