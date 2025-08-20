<script>
  import { onMount } from 'svelte';
  import { fetchRtpiEvents } from '../lib/api';

  let events = [];
  let loading = true;
  let error = '';

  onMount(async () => {
    try {
      events = await fetchRtpiEvents();
    } catch (e) {
      error = e?.message || 'Failed to load events';
    } finally {
      loading = false;
    }
  });
</script>

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
  
</style>

