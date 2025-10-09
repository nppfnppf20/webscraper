<script>
  import { onMount } from 'svelte';
  import { fetchPlanitRenewables } from '../lib/api.js';

  import { API_BASE_URL } from '../lib/config.js';
  let rows = [];
  let loading = true;
  let error = '';
  let refreshing = false;
  let msg = '';

  onMount(async () => {
    try {
      rows = await fetchPlanitRenewables();
    } catch (e) {
      error = e?.message || 'Failed to load data';
    } finally {
      loading = false;
    }
  });

  async function refreshNow() {
    try {
      refreshing = true;
      msg = '';
      const res = await fetch(`${API_BASE_URL}/refresh/planit-renew`, { method: 'POST' });
      const j = await res.json();
      if (!res.ok || !j.ok) throw new Error(j.error || 'Refresh failed');
      rows = await fetchPlanitRenewables();
      msg = `Refreshed (${j.csv}) in ${j.elapsed_s}s, rows: ${j.updated}`;
    } catch (e) {
      msg = e.message || 'Refresh failed';
    } finally {
      refreshing = false;
    }
  }
</script>

{#if loading}
  <p>Loading…</p>
{:else if error}
  <p style="color:red">{error}</p>
{:else}
  <div class="toolbar">
    <button on:click={refreshNow} disabled={refreshing}>{refreshing ? 'Refreshing…' : 'Refresh'}</button>
    {#if msg}<span class="msg">{msg}</span>{/if}
  </div>
  <table>
    <thead>
      <tr>
        <th>Authority</th>
        <th>Title</th>
        <th>Address</th>
        <th>Postcode</th>
        <th>Start Date</th>
        <th>Type</th>
        <th>Size</th>
        <th>Status</th>
        <th>Status Class</th>
        <th>Decision</th>
        <th>Site Area (ha)</th>
        <th>Lat</th>
        <th>Lng</th>
        <th>Link</th>
      </tr>
    </thead>
    <tbody>
      {#each rows as r}
        <tr>
          <td>{r.authority}</td>
          <td title={r.description}>{r.title}</td>
          <td>{r.address}</td>
          <td>{r.postcode}</td>
          <td>{r.start_date}</td>
          <td>{r.app_type}</td>
          <td>{r.app_size}</td>
          <td>{r.app_state}</td>
          <td>{r.status_class}</td>
          <td>{r.decision}</td>
          <td>{r.site_area_ha}</td>
          <td>{r.lat}</td>
          <td>{r.lng}</td>
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
  .toolbar { display:flex; align-items:center; gap:12px; margin: 8px 0; }
  .msg { color:#555; font-size: 0.9rem; }
</style>

