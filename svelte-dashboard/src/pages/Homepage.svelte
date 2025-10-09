<script>
  import { onMount } from 'svelte';
  import * as api from '../lib/api.js';

  let loading = true;
  let error = '';
  let refreshing = false;
  let refreshStatus = '';
  let autoRefreshEnabled = true;
  let lastRefreshTime = '';
  let nextAutoRefresh = '';
  let overview = {
    cpd: {},
    consultations: {},
    development: {}
  };

  // Use API functions from the centralized API module
  const fetchRtpiEvents = api.fetchRtpiEvents;
  const fetchDunholmeConsultations = api.fetchWestLindseyConsultations;
  const fetchPeeringdbIx = api.fetchPeeringdbIxGb;
  const fetchPeeringdbFac = api.fetchPeeringdbFacGb;
  const fetchPlanitDatacentres = api.fetchPlanitDatacentres;
  const fetchPlanitRenewables = api.fetchPlanitRenewablesTest2;
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

  // Filter function for medium/large projects and excluding conditions (same as individual pages)
  function filterPlanitProjects(data) {
    return data.filter(project => {
      // Filter for medium and large size only
      const size = (project.app_size || '').toLowerCase();
      const isMediumOrLarge = size.includes('medium') || size.includes('large');

      // Filter out conditions in type column
      const type = (project.app_type || '').toLowerCase();
      const hasConditions = type.includes('condition') || type.includes('discharge');

      return isMediumOrLarge && !hasConditions;
    });
  }

  // Helper function to get time-based counts
  function getTimeCounts(items, dateField = 'start_date') {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const sevenDaysAgo = new Date(today);
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    const thirtyDaysAgo = new Date(today);
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    let todayCount = 0;
    let sevenDayCount = 0;
    let thirtyDayCount = 0;

    items.forEach(item => {
      if (!item[dateField]) return;
      try {
        const itemDate = new Date(item[dateField]);
        const itemDateOnly = new Date(itemDate.getFullYear(), itemDate.getMonth(), itemDate.getDate());

        if (itemDateOnly >= today) todayCount++;
        if (itemDateOnly >= sevenDaysAgo) sevenDayCount++;
        if (itemDateOnly >= thirtyDaysAgo) thirtyDayCount++;
      } catch {
        // Invalid date, skip
      }
    });
    return { todayCount, sevenDayCount, thirtyDayCount };
  }

  // Helper function to get recent items (last 7 days) for display
  function getRecentItems(items, dateField = 'start_date', limit = 3) {
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

  // Auto-refresh management
  const REFRESH_STORAGE_KEY = 'dashboard_last_refresh';
  const REFRESH_INTERVAL = 24 * 60 * 60 * 1000; // 24 hours in milliseconds

  function getLastRefreshTime() {
    try {
      const stored = localStorage.getItem(REFRESH_STORAGE_KEY);
      return stored ? parseInt(stored) : 0;
    } catch {
      return 0;
    }
  }

  function setLastRefreshTime() {
    try {
      localStorage.setItem(REFRESH_STORAGE_KEY, Date.now().toString());
      updateRefreshDisplays();
    } catch {
      // localStorage not available
    }
  }

  function updateRefreshDisplays() {
    const lastRefresh = getLastRefreshTime();
    if (lastRefresh) {
      const lastRefreshDate = new Date(lastRefresh);
      const nextRefreshDate = new Date(lastRefresh + REFRESH_INTERVAL);

      lastRefreshTime = lastRefreshDate.toLocaleString();
      nextAutoRefresh = nextRefreshDate.toLocaleString();
    } else {
      lastRefreshTime = 'Never';
      nextAutoRefresh = 'Not scheduled';
    }
  }

  function shouldAutoRefresh() {
    if (!autoRefreshEnabled) return false;
    const lastRefresh = getLastRefreshTime();
    const now = Date.now();
    return now - lastRefresh >= REFRESH_INTERVAL;
  }

  function toggleAutoRefresh() {
    autoRefreshEnabled = !autoRefreshEnabled;
    if (!autoRefreshEnabled) {
      nextAutoRefresh = 'Disabled';
      lastRefreshTime = lastRefreshTime; // Keep last refresh time
    } else {
      updateRefreshDisplays();
    }
  }

  // Global refresh function
  async function refreshAll(isAutoRefresh = false) {
    if (refreshing) return;

    refreshing = true;
    refreshStatus = isAutoRefresh ? 'Starting automatic daily refresh...' : 'Starting global refresh...';

    const refreshEndpoints = [
      { name: 'RTPI Events', endpoint: '/api/refresh/rtpi' },
      { name: 'West Lindsey', endpoint: '/api/refresh/west-lindsey' },
      { name: 'PeeringDB IX', endpoint: '/api/refresh/peeringdb-ix' },
      { name: 'PeeringDB Facilities', endpoint: '/api/refresh/peeringdb-fac' },
      { name: 'PlanIt Data Centres', endpoint: '/api/refresh/planit-dc' },
      { name: 'PlanIt Renewables', endpoint: '/api/refresh/planit-test2' }
    ];

    let successCount = 0;
    let failCount = 0;

    try {
      for (const refresh of refreshEndpoints) {
        refreshStatus = `Refreshing ${refresh.name}...`;

        try {
          const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';
          const response = await fetch(`${API_BASE.replace('/api', '')}${refresh.endpoint}`, {
            method: 'POST'
          });
          const result = await response.json();

          if (response.ok && result.ok) {
            successCount++;
          } else {
            failCount++;
            console.warn(`Failed to refresh ${refresh.name}:`, result.error);
          }
        } catch (e) {
          failCount++;
          console.error(`Error refreshing ${refresh.name}:`, e);
        }
      }

      // Reload data after all refreshes
      refreshStatus = 'Reloading dashboard data...';
      await loadData();

      // Update last refresh time
      setLastRefreshTime();

      const prefix = isAutoRefresh ? '🔄 Auto-refresh' : '✅ Refresh';
      refreshStatus = `${prefix} complete! ${successCount} successful, ${failCount} failed`;
      setTimeout(() => { refreshStatus = ''; }, 8000);

    } catch (e) {
      refreshStatus = `❌ Refresh failed: ${e.message}`;
      setTimeout(() => { refreshStatus = ''; }, 5000);
    } finally {
      refreshing = false;
    }
  }

  // Load data function (extracted for reuse)
  async function loadData() {
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
      const rtpiTimeCounts = getTimeCounts(rtpiEvents, 'date');
      overview.cpd = {
        rtpiEvents: {
          total: rtpiEvents.length,
          recent: getRecentItems(rtpiEvents, 'date'),
          lastUpdated: rtpiEvents.length > 0 ? 'Recently updated' : 'No data',
          ...rtpiTimeCounts
        }
      };

      // Process TRP Consultation Trackers data
      const consultationTimeCounts = getTimeCounts(dunholmeConsultations, 'createdTime');
      overview.consultations = {
        dunholme: {
          total: dunholmeConsultations.length,
          recent: getRecentItems(dunholmeConsultations, 'createdTime'),
          lastUpdated: dunholmeConsultations.length > 0 ? 'Recently updated' : 'No data',
          ...consultationTimeCounts
        }
      };

      // Process Development Monitoring data
      // Apply filtering to PlanIt data (same as individual pages)
      const filteredDatacentres = filterPlanitProjects(planitDatacentres);
      const filteredRenewables = filterPlanitProjects(planitRenewables);

      const datacentreTimeCounts = getTimeCounts(filteredDatacentres, 'start_date');
      const renewablesTimeCounts = getTimeCounts(filteredRenewables, 'start_date');

      overview.development = {
        peeringdbIx: {
          total: peeringdbIx.length,
          recent: peeringdbIx.slice(0, 3),
          lastUpdated: peeringdbIx.length > 0 ? 'Recently updated' : 'No data',
          // PeeringDB data doesn't have meaningful date fields for time stats
          todayCount: 0,
          sevenDayCount: 0,
          thirtyDayCount: 0
        },
        peeringdbFac: {
          total: peeringdbFac.length,
          recent: peeringdbFac.slice(0, 3),
          lastUpdated: peeringdbFac.length > 0 ? 'Recently updated' : 'No data',
          // PeeringDB data doesn't have meaningful date fields for time stats
          todayCount: 0,
          sevenDayCount: 0,
          thirtyDayCount: 0
        },
        planitDatacentres: {
          total: filteredDatacentres.length,  // Show filtered count
          recent: getRecentItems(filteredDatacentres, 'start_date', 3),
          lastUpdated: planitDatacentres.length > 0 ? 'Recently updated' : 'No data',
          ...datacentreTimeCounts
        },
        planitRenewables: {
          total: filteredRenewables.length,  // Show filtered count
          recent: getRecentItems(filteredRenewables, 'start_date', 3),
          lastUpdated: planitRenewables.length > 0 ? 'Recently updated' : 'No data',
          ...renewablesTimeCounts
        }
      };

    } catch (e) {
      error = e?.message || 'Failed to load overview data';
    }
  }

  // Load all data on component mount
  onMount(async () => {
    try {
      await loadData();

      // Initialize auto-refresh displays
      updateRefreshDisplays();

      // Check if we need to auto-refresh on page load
      if (shouldAutoRefresh()) {
        console.log('Auto-refresh needed, starting refresh...');
        setTimeout(() => refreshAll(true), 2000); // Small delay to let UI load
      }

      // Set up periodic check for auto-refresh (every hour)
      const autoRefreshInterval = setInterval(() => {
        if (shouldAutoRefresh()) {
          console.log('Daily auto-refresh triggered');
          refreshAll(true);
        }
      }, 60 * 60 * 1000); // Check every hour

      // Cleanup interval on component destroy
      return () => clearInterval(autoRefreshInterval);

    } catch (e) {
      error = e?.message || 'Failed to load overview data';
    } finally {
      loading = false;
    }
  });
</script>

<div class="page-header">
  <div class="header-content">
    <div>
      <h1>Dashboard Overview</h1>
      <p>Recent updates and activity across all monitoring systems</p>
    </div>
    <div class="header-actions">
      <div class="auto-refresh-info">
        <div class="auto-refresh-status">
          <span class="status-label">Auto-refresh:</span>
          <span class="status-value {autoRefreshEnabled ? 'enabled' : 'disabled'}">
            {autoRefreshEnabled ? 'Enabled' : 'Disabled'}
          </span>
        </div>
        <div class="last-refresh">
          <span class="last-label">Last:</span>
          <span class="last-time">{lastRefreshTime}</span>
        </div>
        {#if autoRefreshEnabled}
          <div class="next-refresh">
            <span class="next-label">Next:</span>
            <span class="next-time">{nextAutoRefresh}</span>
          </div>
        {/if}
      </div>
      <div class="button-group">
        <button class="button-secondary" on:click={toggleAutoRefresh}>
          {autoRefreshEnabled ? 'Disable Auto' : 'Enable Auto'}
        </button>
        <button class="button-primary" on:click={() => refreshAll(false)} disabled={refreshing}>
          {#if refreshing}<span class="loading-spinner"></span>{/if}
          {refreshing ? 'Refreshing...' : 'Refresh Now'}
        </button>
      </div>
    </div>
  </div>
  {#if refreshStatus}
    <div class="refresh-status">{@html refreshStatus}</div>
  {/if}
</div>

{#if loading}
  <div class="text-center p-4">
    <span class="loading-spinner"></span>
    <p class="mt-2">Loading overview data…</p>
  </div>
{:else if error}
  <div class="alert alert-danger">{error}</div>
{:else}

  <!-- TRP Consultation Trackers Section -->
  <div class="category-section">
    <h2 class="category-title">TRP Consultation Trackers</h2>

    <div class="overview-cards">
      <div class="overview-card">
        <h3>
          <a href="#/dunholme">Dunholme Consultations</a>
        </h3>
        <p class="last-updated">{overview.consultations.dunholme.lastUpdated}</p>

        <div class="time-stats">
          <div class="time-stat">
            <span class="time-count">{overview.consultations.dunholme.todayCount || 0}</span>
            <span class="time-label">Today</span>
          </div>
          <div class="time-stat">
            <span class="time-count">{overview.consultations.dunholme.sevenDayCount || 0}</span>
            <span class="time-label">7 Days</span>
          </div>
          <div class="time-stat">
            <span class="time-count">{overview.consultations.dunholme.thirtyDayCount || 0}</span>
            <span class="time-label">30 Days</span>
          </div>
        </div>

        {#if overview.consultations.dunholme.recent.length > 0}
          <div class="recent-items">
            <h4>Recent Consultations:</h4>
            {#each overview.consultations.dunholme.recent as consultation}
              <div class="recent-item">
                <div class="item-title">{consultation.consulteeName || 'Untitled Consultation'}</div>
                <div class="item-date">{formatDate(consultation.createdTime)}</div>
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
        </h3>
        <p class="last-updated">{overview.development.peeringdbIx.lastUpdated}</p>

        <div class="time-stats">
          <div class="time-stat">
            <span class="time-count">{overview.development.peeringdbIx.todayCount || 0}</span>
            <span class="time-label">Today</span>
          </div>
          <div class="time-stat">
            <span class="time-count">{overview.development.peeringdbIx.sevenDayCount || 0}</span>
            <span class="time-label">7 Days</span>
          </div>
          <div class="time-stat">
            <span class="time-count">{overview.development.peeringdbIx.thirtyDayCount || 0}</span>
            <span class="time-label">30 Days</span>
          </div>
        </div>
      </div>

      <div class="overview-card">
        <h3>
          <a href="#/peeringdb-fac">PeeringDB Facilities (GB)</a>
        </h3>
        <p class="last-updated">{overview.development.peeringdbFac.lastUpdated}</p>

        <div class="time-stats">
          <div class="time-stat">
            <span class="time-count">{overview.development.peeringdbFac.todayCount || 0}</span>
            <span class="time-label">Today</span>
          </div>
          <div class="time-stat">
            <span class="time-count">{overview.development.peeringdbFac.sevenDayCount || 0}</span>
            <span class="time-label">7 Days</span>
          </div>
          <div class="time-stat">
            <span class="time-count">{overview.development.peeringdbFac.thirtyDayCount || 0}</span>
            <span class="time-label">30 Days</span>
          </div>
        </div>
      </div>

      <div class="overview-card">
        <h3>
          <a href="#/planit-dc">PlanIt Data Centres</a>
        </h3>
        <p class="last-updated">{overview.development.planitDatacentres.lastUpdated}</p>

        <div class="time-stats">
          <div class="time-stat">
            <span class="time-count">{overview.development.planitDatacentres.todayCount || 0}</span>
            <span class="time-label">Today</span>
          </div>
          <div class="time-stat">
            <span class="time-count">{overview.development.planitDatacentres.sevenDayCount || 0}</span>
            <span class="time-label">7 Days</span>
          </div>
          <div class="time-stat">
            <span class="time-count">{overview.development.planitDatacentres.thirtyDayCount || 0}</span>
            <span class="time-label">30 Days</span>
          </div>
        </div>

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
        </h3>
        <p class="last-updated">{overview.development.planitRenewables.lastUpdated}</p>

        <div class="time-stats">
          <div class="time-stat">
            <span class="time-count">{overview.development.planitRenewables.todayCount || 0}</span>
            <span class="time-label">Today</span>
          </div>
          <div class="time-stat">
            <span class="time-count">{overview.development.planitRenewables.sevenDayCount || 0}</span>
            <span class="time-label">7 Days</span>
          </div>
          <div class="time-stat">
            <span class="time-count">{overview.development.planitRenewables.thirtyDayCount || 0}</span>
            <span class="time-label">30 Days</span>
          </div>
        </div>

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

  <!-- CPD/BD Section -->
  <div class="category-section">
    <h2 class="category-title">CPD/BD</h2>

    <div class="overview-cards">
      <div class="overview-card">
        <h3>
          <a href="#/events">RTPI Events</a>
        </h3>
        <p class="last-updated">{overview.cpd.rtpiEvents.lastUpdated}</p>

        <div class="time-stats">
          <div class="time-stat">
            <span class="time-count">{overview.cpd.rtpiEvents.todayCount || 0}</span>
            <span class="time-label">Today</span>
          </div>
          <div class="time-stat">
            <span class="time-count">{overview.cpd.rtpiEvents.sevenDayCount || 0}</span>
            <span class="time-label">7 Days</span>
          </div>
          <div class="time-stat">
            <span class="time-count">{overview.cpd.rtpiEvents.thirtyDayCount || 0}</span>
            <span class="time-label">30 Days</span>
          </div>
        </div>

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

{/if}

<style>
  .page-header {
    margin-bottom: 2rem;
  }

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 2rem;
    margin-bottom: 1rem;
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

  .header-actions {
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 1rem;
  }

  .auto-refresh-info {
    text-align: right;
    font-size: 0.85rem;
  }

  .auto-refresh-status, .last-refresh, .next-refresh {
    margin-bottom: 0.25rem;
  }

  .status-label, .last-label, .next-label {
    color: var(--dark-gray);
    font-weight: 500;
  }

  .status-value.enabled {
    color: #28a745;
    font-weight: 600;
  }

  .status-value.disabled {
    color: #dc3545;
    font-weight: 600;
  }

  .last-time, .next-time {
    color: var(--text-color);
    font-weight: 500;
  }

  .button-group {
    display: flex;
    gap: 0.75rem;
  }

  .button-primary {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
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

  .button-secondary {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    background: white;
    color: var(--primary-color);
    border: 1px solid var(--primary-color);
    border-radius: var(--border-radius);
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease-in-out;
  }

  .button-secondary:hover {
    background: var(--light-gray);
  }

  .loading-spinner {
    display: inline-block;
    width: 1rem;
    height: 1rem;
    border: 2px solid #f3f3f3;
    border-top: 2px solid currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  .refresh-status {
    background: var(--light-gray);
    padding: 0.75rem 1rem;
    border-radius: var(--border-radius);
    font-size: 0.9rem;
    color: var(--text-color);
    border-left: 3px solid var(--primary-color);
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

  .time-stats {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    padding: 0.75rem;
    background: var(--light-gray);
    border-radius: var(--border-radius);
  }

  .time-stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    flex: 1;
  }

  .time-count {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--primary-color);
  }

  .time-label {
    font-size: 0.75rem;
    color: var(--dark-gray);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 500;
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

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .header-content {
      flex-direction: column;
      align-items: flex-start;
      gap: 1rem;
    }

    .header-actions {
      align-items: stretch;
      width: 100%;
    }

    .auto-refresh-info {
      text-align: left;
    }

    .button-group {
      flex-direction: column;
      gap: 0.5rem;
    }

    .overview-cards {
      grid-template-columns: 1fr;
    }

    .time-stats {
      gap: 0.5rem;
    }

    .time-stat {
      gap: 0.125rem;
    }

    .time-count {
      font-size: 1rem;
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