<script>
  import { onMount } from 'svelte';
  import RtpiEvents from './pages/RtpiEvents.svelte';
  import DunholmeConsultations from './pages/DunholmeConsultations.svelte';
  import PeeringdbIxGb from './pages/PeeringdbIxGb.svelte';
  import PeeringdbFacilitiesGb from './pages/PeeringdbFacilitiesGb.svelte';
  import PlanitDatacentres from './pages/PlanitDatacentres.svelte';
  import PlanitRenewables from './pages/PlanitRenewables.svelte';

  let currentPath = window.location.hash.slice(1) || '/events';

  onMount(() => {
    const handleHashChange = () => {
      currentPath = window.location.hash.slice(1) || '/events';
    };
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  });
</script>

<nav>
  <a href="#/events" class:active={currentPath === '/events'}>RTPI Events</a>
  <a href="#/dunholme" class:active={currentPath === '/dunholme'}>Dunholme Consultations</a>
  <a href="#/peeringdb" class:active={currentPath === '/peeringdb'}>PeeringDB IX (GB)</a>
  <a href="#/peeringdb-fac" class:active={currentPath === '/peeringdb-fac'}>PeeringDB Facilities (GB)</a>
  <a href="#/planit-dc" class:active={currentPath === '/planit-dc'}>PlanIt Data Centres</a>
  <a href="#/planit-renew" class:active={currentPath === '/planit-renew'}>PlanIt Renewables</a>
  <span class="spacer"></span>
  <a href="#/events" class="brand">Web Scraper Dashboard</a>
  
</nav>

<main>
  {#if currentPath === '/events'}
    <RtpiEvents />
  {:else if currentPath === '/dunholme'}
    <DunholmeConsultations />
  {:else if currentPath === '/peeringdb'}
    <PeeringdbIxGb />
  {:else if currentPath === '/peeringdb-fac'}
    <PeeringdbFacilitiesGb />
  {:else if currentPath === '/planit-dc'}
    <PlanitDatacentres />
  {:else if currentPath === '/planit-renew'}
    <PlanitRenewables />
  {:else}
    <p>Page not found.</p>
  {/if}
</main>

<style>
  nav {
    display: flex;
    gap: 16px;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid #eee;
    position: sticky;
    top: 0;
    background: white;
    z-index: 10;
  }
  nav a {
    text-decoration: none;
    color: #333;
  }
  nav a.active {
    font-weight: 600;
    color: #0d6efd;
  }
  nav .brand {
    margin-left: auto;
    color: #666;
    font-size: 0.9rem;
  }
  main {
    padding: 16px;
  }
  .spacer { flex: 1; }
  
</style>
