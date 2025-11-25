<script>
  import { onMount } from 'svelte';

  export let map = null;
  export let renewablesLayer = null;
  export let dataCentresLayer = null;
  export let repdSolarLayer = null;
  export let repdWindLayer = null;
  export let repdBatteryLayer = null;

  let showRenewables = true;
  let showDataCentres = true;
  let showREPDSolar = true;
  let showREPDWind = true;
  let showREPDBattery = true;

  function toggleRenewables() {
    if (renewablesLayer && map) {
      if (showRenewables) {
        map.addLayer(renewablesLayer);
      } else {
        map.removeLayer(renewablesLayer);
      }
    }
  }

  function toggleDataCentres() {
    if (dataCentresLayer && map) {
      if (showDataCentres) {
        map.addLayer(dataCentresLayer);
      } else {
        map.removeLayer(dataCentresLayer);
      }
    }
  }

  function toggleREPDSolar() {
    if (repdSolarLayer && map) {
      if (showREPDSolar) {
        map.addLayer(repdSolarLayer);
      } else {
        map.removeLayer(repdSolarLayer);
      }
    }
  }

  function toggleREPDWind() {
    if (repdWindLayer && map) {
      if (showREPDWind) {
        map.addLayer(repdWindLayer);
      } else {
        map.removeLayer(repdWindLayer);
      }
    }
  }

  function toggleREPDBattery() {
    if (repdBatteryLayer && map) {
      if (showREPDBattery) {
        map.addLayer(repdBatteryLayer);
      } else {
        map.removeLayer(repdBatteryLayer);
      }
    }
  }

  onMount(() => {
    // Control is created, ready to use
  });
</script>

<div class="layer-control">
  <h3>Layers</h3>
  <label class="layer-item">
    <input
      type="checkbox"
      bind:checked={showRenewables}
      on:change={toggleRenewables}
    />
    <span>Renewables</span>
  </label>
  <label class="layer-item">
    <input
      type="checkbox"
      bind:checked={showDataCentres}
      on:change={toggleDataCentres}
    />
    <span>Data Centres</span>
  </label>
  <label class="layer-item">
    <input
      type="checkbox"
      bind:checked={showREPDSolar}
      on:change={toggleREPDSolar}
    />
    <span class="solar-label">☀️ Solar PV</span>
  </label>
  <label class="layer-item">
    <input
      type="checkbox"
      bind:checked={showREPDWind}
      on:change={toggleREPDWind}
    />
    <span class="wind-label">💨 Wind Onshore</span>
  </label>
  <label class="layer-item">
    <input
      type="checkbox"
      bind:checked={showREPDBattery}
      on:change={toggleREPDBattery}
    />
    <span class="battery-label">🔋 Battery</span>
  </label>
</div>

<style>
  .layer-control {
    position: absolute;
    top: 10px;
    right: 10px;
    background: white;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    z-index: 1000;
    min-width: 180px;
  }

  h3 {
    margin: 0 0 10px 0;
    font-size: 14px;
    font-weight: 600;
    color: #333;
  }

  .layer-item {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    padding: 5px 0;
    font-size: 14px;
  }

  .layer-item:hover {
    color: var(--primary-color);
  }

  input[type="checkbox"] {
    cursor: pointer;
  }
</style>
