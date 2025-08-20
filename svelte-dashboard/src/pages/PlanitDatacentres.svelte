<script>
  import { onMount } from 'svelte';
  import { fetchPlanitDatacentres } from '../lib/api.js';

  let rows = [];
  let loading = true;
  let error = '';

  onMount(async () => {
    try {
      rows = await fetchPlanitDatacentres();
    } catch (e) {
      error = e?.message || 'Failed to load data';
    } finally {
      loading = false;
    }
  });
</script>

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

