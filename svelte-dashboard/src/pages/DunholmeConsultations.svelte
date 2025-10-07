<script>
  import { onMount } from 'svelte';
  import { fetchWestLindseyApplication, fetchWestLindseyConsultations, refreshData } from '../lib/api.js';

  let app = {};
  let consultations = [];
  let loading = true;
  let error = '';
  let refreshing = false;
  let msg = '';

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

  async function refreshNow() {
    try {
      refreshing = true;
      msg = '';
      const j = await refreshData('/api/refresh/west-lindsey');
      if (!j.ok) throw new Error(j.error || 'Refresh failed');
      const [a, c] = await Promise.all([
        fetchWestLindseyApplication(),
        fetchWestLindseyConsultations()
      ]);
      app = a;
      consultations = c;
      msg = `Refreshed (${j.csv}) in ${j.elapsed_s}s, rows: ${j.updated}`;
    } catch (e) {
      msg = e.message || 'Refresh failed';
    } finally {
      refreshing = false;
    }
  }
</script>

<div class="page-header">
  <h1>Dunholme Consultations</h1>
  <p>West Lindsey planning application tracking and consultation responses</p>
</div>

{#if loading}
  <div class="text-center p-4">
    <span class="loading-spinner"></span>
    <p class="mt-2">Loading consultation data…</p>
  </div>
{:else if error}
  <div class="alert alert-danger">{error}</div>
{:else}
  <!-- Application Info Section -->
  <div class="application-section">
    <div class="section-header">
      <h2>Planning Application</h2>
      <div class="status-badge status-{app.decision?.toLowerCase() || 'pending'}">
        {app.decision || 'PENDING'}
      </div>
    </div>

    <div class="application-grid">
      <div class="info-item">
        <span class="info-label">Reference</span>
        <span class="info-value">{app.reference || 'N/A'}</span>
      </div>
      <div class="info-item">
        <span class="info-label">Location</span>
        <span class="info-value">{app.location || 'N/A'}</span>
      </div>
      <div class="info-item">
        <span class="info-label">Ward</span>
        <span class="info-value">{app.ward || 'N/A'}</span>
      </div>
      <div class="info-item">
        <span class="info-label">Parish</span>
        <span class="info-value">{app.parish || 'N/A'}</span>
      </div>
      <div class="info-item">
        <span class="info-label">Received</span>
        <span class="info-value">{app.receivedDate || 'N/A'}</span>
      </div>
      <div class="info-item">
        <span class="info-label">Valid</span>
        <span class="info-value">{app.validDate || 'N/A'}</span>
      </div>
      <div class="info-item">
        <span class="info-label">Decision Date</span>
        <span class="info-value">{app.decisionDate || 'N/A'}</span>
      </div>
    </div>
  </div>

  <!-- Consultations Section -->
  <div class="consultations-section">
    <div class="section-header">
      <h2>Consultation Responses</h2>
      <div class="consultation-count">{consultations.length} responses</div>
    </div>

    <div class="toolbar">
      <button class="button-primary" on:click={refreshNow} disabled={refreshing}>
        {#if refreshing}<span class="loading-spinner"></span>{/if}
        {refreshing ? 'Refreshing…' : 'Refresh Data'}
      </button>
      {#if msg}<span class="msg">{@html msg}</span>{/if}
    </div>
    <div class="table-container">
      <table class="consultations-table">
        <thead>
          <tr>
            <th>Consultee</th>
            <th>Opinion</th>
            <th>Comment</th>
            <th>Published</th>
            <th>Created</th>
            <th>Updated</th>
          </tr>
        </thead>
        <tbody>
          {#each consultations as c}
            <tr>
              <td class="consultee">{c.consulteeName || 'N/A'}</td>
              <td class="opinion">
                {#if c.opinion}
                  <span class="opinion-badge opinion-{c.opinion.toLowerCase().replace(' ', '-')}">{c.opinion}</span>
                {:else}
                  <span class="opinion-badge">N/A</span>
                {/if}
              </td>
              <td class="comment">{c.responseDetailsToPublish || 'No comment provided'}</td>
              <td class="date">{c.responsePublished || 'N/A'}</td>
              <td class="date">{c.createdTime || 'N/A'}</td>
              <td class="date">{c.lastModifiedTime || 'N/A'}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>
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

  .text-center {
    text-align: center;
  }

  .p-4 {
    padding: 2rem;
  }

  .mt-2 {
    margin-top: 0.5rem;
  }

  .loading-spinner {
    display: inline-block;
    width: 1rem;
    height: 1rem;
    border: 2px solid #f3f3f3;
    border-top: 2px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  .alert {
    padding: 1rem;
    border-radius: var(--border-radius);
    margin-bottom: 1rem;
  }

  .alert-danger {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
  }

  /* Application Section */
  .application-section {
    background: white;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    margin-bottom: 2rem;
    overflow: hidden;
  }

  .section-header {
    background: var(--light-gray);
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .section-header h2 {
    margin: 0;
    color: var(--text-color);
    font-size: 1.25rem;
    font-weight: 600;
  }

  .status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
  }

  .status-pending {
    background: #fff3cd;
    color: #856404;
    border: 1px solid #ffeaa7;
  }

  .status-approved {
    background: #d1edff;
    color: #0c5460;
    border: 1px solid #bee5eb;
  }

  .status-refused, .status-rejected {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
  }

  .application-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
    padding: 1.5rem;
  }

  .info-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .info-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--dark-gray);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .info-value {
    font-size: 0.95rem;
    color: var(--text-color);
    font-weight: 500;
  }

  /* Consultations Section */
  .consultations-section {
    background: white;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    overflow: hidden;
  }

  .consultation-count {
    background: var(--primary-color);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 600;
  }

  .toolbar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 1rem 1.5rem;
    background: var(--light-gray);
    border-bottom: 1px solid var(--border-color);
  }

  .button-primary {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: var(--primary-color);
    color: white;
    border: none;
    border-radius: var(--border-radius);
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.15s ease-in-out;
  }

  .button-primary:hover:not(:disabled) {
    background: #0b5ed7;
  }

  .button-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .msg {
    color: var(--dark-gray);
    font-size: 0.9rem;
  }

  /* Table Styling */
  .table-container {
    overflow-x: auto;
  }

  .consultations-table {
    width: 100%;
    border-collapse: collapse;
  }

  .consultations-table th,
  .consultations-table td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
    vertical-align: top;
    font-size: 0.9rem;
  }

  .consultations-table th {
    background: var(--light-gray);
    font-weight: 600;
    color: var(--text-color);
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .consultations-table tbody tr:hover {
    background: #f8f9fa;
  }

  .consultee {
    font-weight: 600;
    color: var(--primary-color);
    min-width: 150px;
  }

  .opinion-badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
    background: #e9ecef;
    color: #495057;
  }

  .opinion-no-objection {
    background: #d1edff;
    color: #0c5460;
  }

  .opinion-objection {
    background: #f8d7da;
    color: #721c24;
  }

  .opinion-support {
    background: #d4edda;
    color: #155724;
  }

  .comment {
    max-width: 400px;
    word-break: break-word;
    line-height: 1.4;
  }

  .date {
    font-size: 0.85rem;
    color: var(--dark-gray);
    min-width: 100px;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  /* Responsive */
  @media (max-width: 768px) {
    .application-grid {
      grid-template-columns: 1fr;
    }

    .section-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.5rem;
    }

    .toolbar {
      flex-direction: column;
      align-items: stretch;
    }
  }
</style>

