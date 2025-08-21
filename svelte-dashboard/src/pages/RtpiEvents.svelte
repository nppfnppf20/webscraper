<script>
  import { onMount } from 'svelte';
  import { fetchRtpiEvents } from '../lib/api.js';

  let events = [];
  let loading = true;
  let error = '';
  let refreshing = false;
  let msg = '';

  onMount(async () => {
    try {
      events = await fetchRtpiEvents();
    } catch (e) {
      error = e?.message || 'Failed to load events';
    } finally {
      loading = false;
    }
  });

  async function refreshNow() {
    try {
      refreshing = true;
      msg = '';
      const res = await fetch('http://127.0.0.1:8000/api/refresh/rtpi', { method: 'POST' });
      const j = await res.json();
      if (!res.ok || !j.ok) throw new Error(j.error || 'Refresh failed');
      events = await fetchRtpiEvents();
      msg = `Refreshed (${j.csv}) in ${j.elapsed_s}s, rows: ${j.updated}`;
    } catch (e) {
      msg = e.message || 'Refresh failed';
    } finally {
      refreshing = false;
    }
  }
</script>

<div class="toolbar">
  <button on:click={refreshNow} disabled={refreshing}>{refreshing ? 'Refreshing…' : 'Refresh'}</button>
  {#if msg}<span class="msg">{msg}</span>{/if}
</div>

{#if loading}
  <p>Loading events…</p>
{:else if error}
  <p style="color:red">{error}</p>
{:else}
  <table>
    <thead>
      <tr>
        <th>Title</th>
        <th>Date</th>
        <th>Region</th>
        <th>Category</th>
        <th>Price</th>
      </tr>
    </thead>
    <tbody>
      {#each events as e}
        <tr>
          <td><a href={e.url} target="_blank" rel="noreferrer">{e.title}</a></td>
          <td>{e.date}</td>
          <td>{e.region}</td>
          <td>{e.category}</td>
          <td>{e.price}</td>
        </tr>
      {/each}
    </tbody>
  </table>
{/if}

<style>
  table { width: 100%; border-collapse: collapse; }
  th, td { border: 1px solid #ddd; padding: 8px; }
  th { background: #f5f5f5; text-align: left; }
  a { color: #0d6efd; text-decoration: none; }
  a:hover { text-decoration: underline; }
  p { margin: 1rem 0; }
  .toolbar { display:flex; align-items:center; gap:12px; margin: 8px 0; }
  .msg { color:#555; font-size: 0.9rem; }
  
</style>

