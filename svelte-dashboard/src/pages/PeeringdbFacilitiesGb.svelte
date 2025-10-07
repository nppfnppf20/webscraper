<script>
  import { onMount } from 'svelte';
  import { fetchPeeringdbFacGb } from '../lib/api.js';

  let rows = [];
  let loading = true;
  let error = '';
  let refreshing = false;
  let msg = '';

  onMount(async () => {
    try {
      rows = await fetchPeeringdbFacGb();
    } catch (e) {
      error = e?.message || 'Failed to load Facilities data';
    } finally {
      loading = false;
    }
  });

  async function refreshNow() {
    try {
      refreshing = true;
      msg = '';
      const res = await fetch('${API_BASE}/refresh/peeringdb-fac', { method: 'POST' });
      const j = await res.json();
      if (!res.ok || !j.ok) throw new Error(j.error || 'Refresh failed');
      rows = await fetchPeeringdbFacGb();
      msg = `Refreshed (${j.csv}) in ${j.elapsed_s}s, rows: ${j.updated}`;
    } catch (e) {
      msg = e.message || 'Refresh failed';
    } finally {
      refreshing = false;
    }
  }
</script>

<div class="toolbar">
  <button on:click={refreshNow} disabled={refreshing || loading}>{refreshing ? 'Refreshing…' : 'Refresh'}</button>
  {#if msg}<span class="msg">{msg}</span>{/if}
</div>

{#if loading}
  <p>Loading…</p>
{:else if error}
  <p style="color:red">{error}</p>
{:else}
  <table>
    <thead>
      <tr>
        <th>Name</th>
        <th>Address</th>
        <th>City</th>
        <th>Country</th>
        <th>Postcode</th>
      </tr>
    </thead>
    <tbody>
      {#each rows as r}
        <tr>
          <td>{r.name}</td>
          <td>{r.address}</td>
          <td>{r.city}</td>
          <td>{r.country}</td>
          <td>{r.postal_code}</td>
        </tr>
      {/each}
    </tbody>
  </table>
{/if}

<style>
  table { width: 100%; border-collapse: collapse; }
  th, td { border: 1px solid #ddd; padding: 8px; }
  th { background: #f5f5f5; text-align: left; }
  .toolbar { display:flex; align-items:center; gap:12px; margin: 8px 0; }
  .msg { color:#555; font-size: 0.9rem; }
</style>

