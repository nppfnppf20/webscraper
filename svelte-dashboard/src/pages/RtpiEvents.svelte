<script>
  import { onMount } from 'svelte';
  import { fetchRtpiEvents } from '../lib/api.js';
  import { API_BASE_URL } from '../lib/config.js';

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
      const API_BASE = API_BASE_URL;
      const res = await fetch(`${API_BASE}/refresh/rtpi`, { method: 'POST' });
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
  <button class="button-primary" on:click={refreshNow} disabled={refreshing}>
    {#if refreshing}<span class="loading-spinner"></span>{/if}
    {refreshing ? 'Refreshing…' : 'Refresh'}
  </button>
  {#if msg}<span class="msg">{msg}</span>{/if}
</div>

{#if loading}
  <div class="text-center p-4">
    <span class="loading-spinner"></span>
    <p class="mt-2">Loading events…</p>
  </div>
{:else if error}
  <div class="alert alert-danger">{error}</div>
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
  .toolbar {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 8px 0;
  }
  .msg {
    color: var(--dark-gray);
    font-size: 0.9rem;
  }
</style>

