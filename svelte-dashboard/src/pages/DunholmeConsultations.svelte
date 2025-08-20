<script>
  import { onMount } from 'svelte';
  import { fetchWestLindseyApplication, fetchWestLindseyConsultations } from '../lib/api.js';

  let app = {};
  let consultations = [];
  let loading = true;
  let error = '';

  onMount(async () => {
    try {
      const [a, c] = await Promise.all([
        fetchWestLindseyApplication(),
        fetchWestLindseyConsultations()
      ]);
      app = a;
      consultations = c;
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
  <section>
    <h2>Application</h2>
    <div class="grid">
      <div><strong>Reference:</strong> {app.reference}</div>
      <div><strong>Location:</strong> {app.location}</div>
      <div><strong>Ward:</strong> {app.ward}</div>
      <div><strong>Parish:</strong> {app.parish}</div>
      <div><strong>Decision:</strong> {app.decision}</div>
      <div><strong>Received:</strong> {app.receivedDate}</div>
      <div><strong>Valid:</strong> {app.validDate}</div>
      <div><strong>Decision Date:</strong> {app.decisionDate}</div>
    </div>
  </section>

  <section>
    <h2>Consultations</h2>
    <table>
      <thead>
        <tr>
          <th>Consultee</th>
          <th>Opinion</th>
          <th>Published</th>
          <th>Created</th>
          <th>Updated</th>
        </tr>
      </thead>
      <tbody>
        {#each consultations as c}
          <tr>
            <td>{c.consulteeName}</td>
            <td>{c.opinion}</td>
            <td>{c.responsePublished}</td>
            <td>{c.createdTime}</td>
            <td>{c.lastModifiedTime}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </section>
{/if}

<style>
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 8px 16px;
    margin-bottom: 1rem;
  }
  table { width: 100%; border-collapse: collapse; }
  th, td { border: 1px solid #ddd; padding: 8px; }
  th { background: #f5f5f5; text-align: left; }
  h2 { margin: 1rem 0 0.5rem; }
</style>

