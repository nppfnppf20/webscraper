<script>
  import { onMount } from 'svelte';
  import RtpiEvents from './pages/RtpiEvents.svelte';
  import DunholmeConsultations from './pages/DunholmeConsultations.svelte';
  import PeeringdbIxGb from './pages/PeeringdbIxGb.svelte';
  import PeeringdbFacilitiesGb from './pages/PeeringdbFacilitiesGb.svelte';
  import PlanitDatacentres from './pages/PlanitDatacentres.svelte';
  import PlanitRenewables from './pages/PlanitRenewables.svelte';
  import PlanitRenewablesTest2 from './pages/PlanitRenewablesTest2.svelte';

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
  <a href="#/planit-test2" class:active={currentPath === '/planit-test2'}>PlanIt Renewables Test 2</a>
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
  {:else if currentPath === '/planit-test2'}
    <PlanitRenewablesTest2 />
  {:else}
    <p>Page not found.</p>
  {/if}
</main>

