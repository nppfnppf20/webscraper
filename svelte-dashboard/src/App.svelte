<script>
  import { onMount } from 'svelte';
  import Homepage from './pages/Homepage.svelte';
  import RtpiEvents from './pages/RtpiEvents.svelte';
  import DunholmeConsultations from './pages/DunholmeConsultations.svelte';
  import PeeringdbIxGb from './pages/PeeringdbIxGb.svelte';
  import PeeringdbFacilitiesGb from './pages/PeeringdbFacilitiesGb.svelte';
  import PlanitDatacentres from './pages/PlanitDatacentres.svelte';
  import PlanitRenewablesTest2 from './pages/PlanitRenewablesTest2.svelte';

  let currentPath = window.location.hash.slice(1) || '/';
  let activeDropdown = null;

  onMount(() => {
    const handleHashChange = () => {
      currentPath = window.location.hash.slice(1) || '/';
    };
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  });

  function toggleDropdown(dropdown) {
    activeDropdown = activeDropdown === dropdown ? null : dropdown;
  }

  function closeDropdowns() {
    activeDropdown = null;
  }
</script>

<nav on:click={closeDropdowns}>
  <!-- CPD/BD Category -->
  <div class="dropdown" class:active={activeDropdown === 'cpd'}>
    <button class="dropdown-toggle" on:click|stopPropagation={() => toggleDropdown('cpd')}>
      CPD/BD
      <span class="dropdown-arrow">▼</span>
    </button>
    {#if activeDropdown === 'cpd'}
      <div class="dropdown-menu">
        <a href="#/events" class:active={currentPath === '/events'} on:click={closeDropdowns}>RTPI Events</a>
      </div>
    {/if}
  </div>

  <!-- TRP Consultation Trackers Category -->
  <div class="dropdown" class:active={activeDropdown === 'consultations'}>
    <button class="dropdown-toggle" on:click|stopPropagation={() => toggleDropdown('consultations')}>
      TRP Consultation Trackers
      <span class="dropdown-arrow">▼</span>
    </button>
    {#if activeDropdown === 'consultations'}
      <div class="dropdown-menu">
        <a href="#/dunholme" class:active={currentPath === '/dunholme'} on:click={closeDropdowns}>Dunholme Consultations</a>
      </div>
    {/if}
  </div>

  <!-- Development Monitoring Category -->
  <div class="dropdown" class:active={activeDropdown === 'development'}>
    <button class="dropdown-toggle" on:click|stopPropagation={() => toggleDropdown('development')}>
      Development Monitoring
      <span class="dropdown-arrow">▼</span>
    </button>
    {#if activeDropdown === 'development'}
      <div class="dropdown-menu">
        <a href="#/peeringdb" class:active={currentPath === '/peeringdb'} on:click={closeDropdowns}>PeeringDB IX (GB)</a>
        <a href="#/peeringdb-fac" class:active={currentPath === '/peeringdb-fac'} on:click={closeDropdowns}>PeeringDB Facilities (GB)</a>
        <a href="#/planit-dc" class:active={currentPath === '/planit-dc'} on:click={closeDropdowns}>PlanIt Data Centres</a>
        <a href="#/planit-test2" class:active={currentPath === '/planit-test2'} on:click={closeDropdowns}>PlanIt Renewables</a>
      </div>
    {/if}
  </div>

  <span class="spacer"></span>
  <a href="#/" class="brand">Web Scraper Dashboard</a>
</nav>

<main>
  {#if currentPath === '/'}
    <Homepage />
  {:else if currentPath === '/events'}
    <RtpiEvents />
  {:else if currentPath === '/dunholme'}
    <DunholmeConsultations />
  {:else if currentPath === '/peeringdb'}
    <PeeringdbIxGb />
  {:else if currentPath === '/peeringdb-fac'}
    <PeeringdbFacilitiesGb />
  {:else if currentPath === '/planit-dc'}
    <PlanitDatacentres />
  {:else if currentPath === '/planit-test2'}
    <PlanitRenewablesTest2 />
  {:else}
    <p>Page not found.</p>
  {/if}
</main>

<style>
  nav {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 2rem;
    background: var(--light-gray);
    border-bottom: 1px solid var(--border-color);
    position: relative;
  }

  .dropdown {
    position: relative;
  }

  .dropdown-toggle {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: none;
    border: none;
    color: var(--text-color);
    font-size: 0.9rem;
    cursor: pointer;
    border-radius: var(--border-radius);
    transition: background-color 0.15s ease-in-out;
  }

  .dropdown-toggle:hover,
  .dropdown.active .dropdown-toggle {
    background-color: rgba(0, 0, 0, 0.05);
  }

  .dropdown-arrow {
    font-size: 0.7rem;
    transition: transform 0.15s ease-in-out;
  }

  .dropdown.active .dropdown-arrow {
    transform: rotate(180deg);
  }

  .dropdown-menu {
    position: absolute;
    top: 100%;
    left: 0;
    min-width: 200px;
    background: white;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    padding: 0.5rem 0;
  }

  .dropdown-menu a {
    display: block;
    padding: 0.75rem 1rem;
    color: var(--text-color);
    text-decoration: none;
    font-size: 0.9rem;
    transition: background-color 0.15s ease-in-out;
  }

  .dropdown-menu a:hover {
    background-color: var(--light-gray);
  }

  .dropdown-menu a.active {
    background-color: var(--primary-color);
    color: white;
  }

  .spacer {
    flex: 1;
  }

  .brand {
    font-weight: 600;
    color: var(--primary-color);
    text-decoration: none;
    font-size: 1.1rem;
  }

  .brand:hover {
    color: var(--primary-color);
  }

  main {
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;
  }

  /* Mobile responsiveness */
  @media (max-width: 768px) {
    nav {
      flex-direction: column;
      align-items: stretch;
      gap: 0.5rem;
      padding: 1rem;
    }

    .dropdown-menu {
      position: static;
      box-shadow: none;
      border: none;
      border-top: 1px solid var(--border-color);
      margin-top: 0.5rem;
    }

    .spacer {
      display: none;
    }

    main {
      padding: 1rem;
    }
  }
</style>