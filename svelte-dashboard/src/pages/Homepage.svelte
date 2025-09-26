<script>
  import { onMount } from 'svelte';

  let loading = true;
  let error = '';
  let overview = {
    cpd: {},
    consultations: {},
    development: {}
  };

  // API functions to fetch data from each source
  async function fetchRtpiEvents() {
    const response = await fetch('http://127.0.0.1:8000/api/rtpi/events');
    if (!response.ok) throw new Error(`RTPI Events: HTTP ${response.status}`);
    return await response.json();
  }

  async function fetchDunholmeConsultations() {
    const response = await fetch('http://127.0.0.1:8000/api/west-lindsey/consultations');
    if (!response.ok) throw new Error(`Dunholme: HTTP ${response.status}`);
    return await response.json();
  }

  async function fetchPeeringdbIx() {
    const response = await fetch('http://127.0.0.1:8000/api/peeringdb/ix/gb');
    if (!response.ok) throw new Error(`PeeringDB IX: HTTP ${response.status}`);
    return await response.json();
  }

  async function fetchPeeringdbFac() {
    const response = await fetch('http://127.0.0.1:8000/api/peeringdb/fac/gb');
    if (!response.ok) throw new Error(`PeeringDB Facilities: HTTP ${response.status}`);
    return await response.json();
  }

  async function fetchPlanitDatacentres() {
    const response = await fetch('http://127.0.0.1:8000/api/planit/datacentres');
    if (!response.ok) throw new Error(`PlanIt Data Centres: HTTP ${response.status}`);
    return await response.json();
  }

  async function fetchPlanitRenewables() {
    const response = await fetch('http://127.0.0.1:8000/api/planit/renewables-test2');
    if (!response.ok) throw new Error(`PlanIt Renewables: HTTP ${response.status}`);
    return await response.json();
  }

  // Helper function to format dates
  function formatDate(dateStr) {
    if (!dateStr) return '';
    try {
      return new Date(dateStr).toLocaleDateString('en-GB');
    } catch {
      return dateStr;
    }
  }

  // Helper function to get recent items (last 7 days)
  function getRecentItems(items, dateField = 'start_date', limit = 5) {
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

    return items
      .filter(item => {
        if (!item[dateField]) return false;
        try {
          const itemDate = new Date(item[dateField]);
          return itemDate >= sevenDaysAgo;
        } catch {
          return false;
        }
      })
      .sort((a, b) => new Date(b[dateField]) - new Date(a[dateField]))
      .slice(0, limit);
  }

  // Load all data on component mount
  onMount(async () => {
    try {
      // Fetch all data in parallel
      const [
        rtpiEvents,
        dunholmeConsultations,
        peeringdbIx,
        peeringdbFac,
        planitDatacentres,
        planitRenewables
      ] = await Promise.all([
        fetchRtpiEvents().catch(() => []),
        fetchDunholmeConsultations().catch(() => []),
        fetchPeeringdbIx().catch(() => []),
        fetchPeeringdbFac().catch(() => []),
        fetchPlanitDatacentres().catch(() => []),
        fetchPlanitRenewables().catch(() => [])
      ]);

      // Process CPD/BD data
      overview.cpd = {
        rtpiEvents: {
          total: rtpiEvents.length,
          recent: getRecentItems(rtpiEvents, 'date'),
          lastUpdated: rtpiEvents.length > 0 ? 'Recently updated' : 'No data'
        }
      };

      // Process TRP Consultation Trackers data
      overview.consultations = {
        dunholme: {
          total: dunholmeConsultations.length,
          recent: getRecentItems(dunholmeConsultations, 'start_date'),
          lastUpdated: dunholmeConsultations.length > 0 ? 'Recently updated' : 'No data'
        }
      };

      // Process Development Monitoring data
      overview.development = {
        peeringdbIx: {
          total: peeringdbIx.length,
          recent: peeringdbIx.slice(0, 3),
          lastUpdated: peeringdbIx.length > 0 ? 'Recently updated' : 'No data'
        },
        peeringdbFac: {
          total: peeringdbFac.length,
          recent: peeringdbFac.slice(0, 3),
          lastUpdated: peeringdbFac.length > 0 ? 'Recently updated' : 'No data'
        },
        planitDatacentres: {
          total: planitDatacentres.length,
          recent: getRecentItems(planitDatacentres, 'start_date', 3),
          lastUpdated: planitDatacentres.length > 0 ? 'Recently updated' : 'No data'
        },
        planitRenewables: {
          total: planitRenewables.length,
          recent: getRecentItems(planitRenewables, 'start_date', 3),
          lastUpdated: planitRenewables.length > 0 ? 'Recently updated' : 'No data'
        }
      };

    } catch (e) {
      error = e?.message || 'Failed to load overview data';
    } finally {
      loading = false;
    }
  });
</script>

<div class="page-header">
  <h1>Dashboard Overview</h1>
  <p>Recent updates and activity across all monitoring systems</p>
</div>

{#if loading}
  <div class="text-center p-4">
    <span class="loading-spinner"></span>
    <p class="mt-2">Loading overview data…</p>
  </div>
{:else if error}
  <div class="alert alert-danger">{error}</div>
{:else}

  <!-- CPD/BD Section -->
  <div class="category-section">
    <h2 class="category-title">CPD/BD</h2>

    <div class="overview-cards">
      <div class="overview-card">
        <h3>
          <a href="#/events">RTPI Events</a>
          <span class="count">{overview.cpd.rtpiEvents.total}</span>
        </h3>
        <p class="last-updated">{overview.cpd.rtpiEvents.lastUpdated}</p>

        {#if overview.cpd.rtpiEvents.recent.length > 0}
          <div class="recent-items">
            <h4>Recent Events:</h4>
            {#each overview.cpd.rtpiEvents.recent as event}
              <div class="recent-item">
                <div class="item-title">{event.title || event.name || 'Untitled Event'}</div>
                <div class="item-date">{formatDate(event.date)}</div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  </div>

  <!-- TRP Consultation Trackers Section -->
  <div class="category-section">
    <h2 class="category-title">TRP Consultation Trackers</h2>

    <div class="overview-cards">
      <div class="overview-card">
        <h3>
          <a href="#/dunholme">Dunholme Consultations</a>
          <span class="count">{overview.consultations.dunholme.total}</span>
        </h3>
        <p class="last-updated">{overview.consultations.dunholme.lastUpdated}</p>

        {#if overview.consultations.dunholme.recent.length > 0}
          <div class="recent-items">
            <h4>Recent Consultations:</h4>
            {#each overview.consultations.dunholme.recent as consultation}
              <div class="recent-item">
                <div class="item-title">{consultation.title || consultation.name || 'Untitled Consultation'}</div>
                <div class="item-date">{formatDate(consultation.start_date)}</div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  </div>

  <!-- Development Monitoring Section -->
  <div class="category-section">
    <h2 class="category-title">Development Monitoring</h2>

    <div class="overview-cards">
      <div class="overview-card">
        <h3>
          <a href="#/peeringdb">PeeringDB IX (GB)</a>
          <span class="count">{overview.development.peeringdbIx.total}</span>
        </h3>
        <p class="last-updated">{overview.development.peeringdbIx.lastUpdated}</p>
      </div>

      <div class="overview-card">
        <h3>
          <a href="#/peeringdb-fac">PeeringDB Facilities (GB)</a>
          <span class="count">{overview.development.peeringdbFac.total}</span>
        </h3>
        <p class="last-updated">{overview.development.peeringdbFac.lastUpdated}</p>
      </div>

      <div class="overview-card">
        <h3>
          <a href="#/planit-dc">PlanIt Data Centres</a>
          <span class="count">{overview.development.planitDatacentres.total}</span>
        </h3>
        <p class="last-updated">{overview.development.planitDatacentres.lastUpdated}</p>

        {#if overview.development.planitDatacentres.recent.length > 0}
          <div class="recent-items">
            <h4>Recent Projects:</h4>
            {#each overview.development.planitDatacentres.recent as project}
              <div class="recent-item">
                <div class="item-title">{project.name || project.title || 'Untitled Project'}</div>
                <div class="item-date">{formatDate(project.start_date)}</div>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <div class="overview-card">
        <h3>
          <a href="#/planit-test2">PlanIt Renewables</a>
          <span class="count">{overview.development.planitRenewables.total}</span>
        </h3>
        <p class="last-updated">{overview.development.planitRenewables.lastUpdated}</p>

        {#if overview.development.planitRenewables.recent.length > 0}
          <div class="recent-items">
            <h4>Recent Projects:</h4>
            {#each overview.development.planitRenewables.recent as project}
              <div class="recent-item">
                <div class="item-title">{project.name || project.title || 'Untitled Project'}</div>
                <div class="item-date">{formatDate(project.start_date)}</div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
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

  .category-section {
    margin-bottom: 3rem;
  }

  .category-title {
    color: var(--primary-color);
    font-size: 1.5rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--light-gray);
  }

  .overview-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
  }

  .overview-card {
    background: white;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    transition: box-shadow 0.15s ease-in-out;
  }

  .overview-card:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  .overview-card h3 {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 0 0 0.5rem 0;
    font-size: 1.1rem;
  }

  .overview-card h3 a {
    color: var(--primary-color);
    text-decoration: none;
    font-weight: 600;
  }

  .overview-card h3 a:hover {
    text-decoration: underline;
  }

  .count {
    background: var(--primary-color);
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 600;
  }

  .last-updated {
    color: var(--dark-gray);
    font-size: 0.85rem;
    margin: 0 0 1rem 0;
  }

  .recent-items h4 {
    color: var(--text-color);
    font-size: 0.9rem;
    margin: 0 0 0.75rem 0;
    font-weight: 600;
  }

  .recent-item {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--light-gray);
  }

  .recent-item:last-child {
    border-bottom: none;
  }

  .item-title {
    font-size: 0.9rem;
    color: var(--text-color);
    flex: 1;
    margin-right: 1rem;
    line-height: 1.3;
  }

  .item-date {
    font-size: 0.8rem;
    color: var(--dark-gray);
    white-space: nowrap;
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .overview-cards {
      grid-template-columns: 1fr;
    }

    .recent-item {
      flex-direction: column;
      align-items: flex-start;
    }

    .item-title {
      margin-right: 0;
      margin-bottom: 0.25rem;
    }
  }
</style>