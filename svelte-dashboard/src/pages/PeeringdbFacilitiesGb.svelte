<script>
  import { onMount } from 'svelte';
  import { fetchPeeringdbFacGb } from '../lib/api.js';

  let rows = [];
  let loading = true;
  let error = '';

  onMount(async () => {
    try {
      rows = await fetchPeeringdbFacGb();
    } catch (e) {
      error = e?.message || 'Failed to load Facilities data';
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
</style>

