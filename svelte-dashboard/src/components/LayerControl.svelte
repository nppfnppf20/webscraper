<script>
  import { onMount } from 'svelte';

  export let map = null;
  export let renewablesLayer = null;
  export let dataCentresLayer = null;
  export let repdSolarLayer = null;
  export let repdWindLayer = null;
  export let repdBatteryLayer = null;
  export let trpCommercialLayer = null;
  export let trpEnergyLayer = null;
  export let trpResidentialLayer = null;

  let showRenewables = true;
  let showDataCentres = true;
  let showREPDSolar = true;
  let showREPDWind = true;
  let showREPDBattery = true;
  let showTRPCommercial = true;
  let showTRPEnergy = true;
  let showTRPResidential = true;

  let renewablesRootExpanded = true;
  let dataCentresRootExpanded = true;
  let trpRootExpanded = true;
  let repdGroupExpanded = true;

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

  function toggleREPDGroup() {
    repdGroupExpanded = !repdGroupExpanded;
  }

  function toggleRenewablesRoot() {
    renewablesRootExpanded = !renewablesRootExpanded;
  }

  function toggleDataCentresRoot() {
    dataCentresRootExpanded = !dataCentresRootExpanded;
  }

  function toggleTRPRoot() {
    trpRootExpanded = !trpRootExpanded;
  }

  function toggleTRPCommercial() {
    if (trpCommercialLayer && map) {
      if (showTRPCommercial) {
        map.addLayer(trpCommercialLayer);
      } else {
        map.removeLayer(trpCommercialLayer);
      }
    }
  }

  function toggleTRPEnergy() {
    if (trpEnergyLayer && map) {
      if (showTRPEnergy) {
        map.addLayer(trpEnergyLayer);
      } else {
        map.removeLayer(trpEnergyLayer);
      }
    }
  }

  function toggleTRPResidential() {
    if (trpResidentialLayer && map) {
      if (showTRPResidential) {
        map.addLayer(trpResidentialLayer);
      } else {
        map.removeLayer(trpResidentialLayer);
      }
    }
  }

  function toggleAllRenewables() {
    const newState = !allRenewablesChecked;
    showRenewables = newState;
    showREPDSolar = newState;
    showREPDWind = newState;
    showREPDBattery = newState;

    // Apply to map
    if (map) {
      if (newState) {
        if (renewablesLayer) map.addLayer(renewablesLayer);
        if (repdSolarLayer) map.addLayer(repdSolarLayer);
        if (repdWindLayer) map.addLayer(repdWindLayer);
        if (repdBatteryLayer) map.addLayer(repdBatteryLayer);
      } else {
        if (renewablesLayer) map.removeLayer(renewablesLayer);
        if (repdSolarLayer) map.removeLayer(repdSolarLayer);
        if (repdWindLayer) map.removeLayer(repdWindLayer);
        if (repdBatteryLayer) map.removeLayer(repdBatteryLayer);
      }
    }
  }

  function toggleAllDataCentres() {
    const newState = !allDataCentresChecked;
    showDataCentres = newState;

    // Apply to map
    if (map && dataCentresLayer) {
      if (newState) {
        map.addLayer(dataCentresLayer);
      } else {
        map.removeLayer(dataCentresLayer);
      }
    }
  }

  function toggleAllTRP() {
    const newState = !allTRPChecked;
    showTRPCommercial = newState;
    showTRPEnergy = newState;
    showTRPResidential = newState;

    // Apply to map
    if (map) {
      if (newState) {
        if (trpCommercialLayer) map.addLayer(trpCommercialLayer);
        if (trpEnergyLayer) map.addLayer(trpEnergyLayer);
        if (trpResidentialLayer) map.addLayer(trpResidentialLayer);
      } else {
        if (trpCommercialLayer) map.removeLayer(trpCommercialLayer);
        if (trpEnergyLayer) map.removeLayer(trpEnergyLayer);
        if (trpResidentialLayer) map.removeLayer(trpResidentialLayer);
      }
    }
  }

  // Computed properties to determine if all layers in a group are checked
  $: allRenewablesChecked = showRenewables && showREPDSolar && showREPDWind && showREPDBattery;
  $: allDataCentresChecked = showDataCentres;
  $: allTRPChecked = showTRPCommercial && showTRPEnergy && showTRPResidential;

  onMount(() => {
    // Control is created, ready to use
  });
</script>

<div class="layer-control">
  <h3>Layers</h3>

  <!-- Renewables Root Folder -->
  <div class="layer-group root-group">
    <div class="layer-group-header root-header">
      <input
        type="checkbox"
        checked={allRenewablesChecked}
        on:change={toggleAllRenewables}
        on:click|stopPropagation
      />
      <span class="group-arrow" class:expanded={renewablesRootExpanded} on:click={toggleRenewablesRoot}>▶</span>
      <span class="group-title" on:click={toggleRenewablesRoot}>Renewables</span>
    </div>

    {#if renewablesRootExpanded}
      <div class="layer-group-content">
        <!-- Planit Renewables Apps -->
        <label class="layer-item">
          <input
            type="checkbox"
            bind:checked={showRenewables}
            on:change={toggleRenewables}
          />
          <span>Planit Renewables Apps</span>
        </label>

        <!-- REPD Renewables Group -->
        <div class="layer-group nested-group">
          <div class="layer-group-header" on:click={toggleREPDGroup}>
            <span class="group-arrow" class:expanded={repdGroupExpanded}>▶</span>
            <span class="group-title">Renewable Energy Dashboard Q3 Oct 25</span>
          </div>

          {#if repdGroupExpanded}
            <div class="layer-group-content">
              <label class="layer-item">
                <input
                  type="checkbox"
                  bind:checked={showREPDSolar}
                  on:change={toggleREPDSolar}
                />
                <span>Solar PV</span>
              </label>
              <label class="layer-item">
                <input
                  type="checkbox"
                  bind:checked={showREPDWind}
                  on:change={toggleREPDWind}
                />
                <span>Wind Onshore</span>
              </label>
              <label class="layer-item">
                <input
                  type="checkbox"
                  bind:checked={showREPDBattery}
                  on:change={toggleREPDBattery}
                />
                <span>Battery</span>
              </label>
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </div>

  <!-- Data Centres Root Folder -->
  <div class="layer-group root-group">
    <div class="layer-group-header root-header">
      <input
        type="checkbox"
        checked={allDataCentresChecked}
        on:change={toggleAllDataCentres}
        on:click|stopPropagation
      />
      <span class="group-arrow" class:expanded={dataCentresRootExpanded} on:click={toggleDataCentresRoot}>▶</span>
      <span class="group-title" on:click={toggleDataCentresRoot}>Data Centres</span>
    </div>

    {#if dataCentresRootExpanded}
      <div class="layer-group-content">
        <label class="layer-item">
          <input
            type="checkbox"
            bind:checked={showDataCentres}
            on:change={toggleDataCentres}
          />
          <span>Planit Data Centre Apps</span>
        </label>
      </div>
    {/if}
  </div>

  <!-- TRP Projects Root Folder -->
  <div class="layer-group root-group">
    <div class="layer-group-header root-header">
      <input
        type="checkbox"
        checked={allTRPChecked}
        on:change={toggleAllTRP}
        on:click|stopPropagation
      />
      <span class="group-arrow" class:expanded={trpRootExpanded} on:click={toggleTRPRoot}>▶</span>
      <span class="group-title" on:click={toggleTRPRoot}>TRP Projects</span>
    </div>

    {#if trpRootExpanded}
      <div class="layer-group-content">
        <label class="layer-item">
          <input
            type="checkbox"
            bind:checked={showTRPCommercial}
            on:change={toggleTRPCommercial}
          />
          <span>Commercial, Economic and Industrial</span>
        </label>
        <label class="layer-item">
          <input
            type="checkbox"
            bind:checked={showTRPEnergy}
            on:change={toggleTRPEnergy}
          />
          <span>Energy, Digital and Infrastructure</span>
        </label>
        <label class="layer-item">
          <input
            type="checkbox"
            bind:checked={showTRPResidential}
            on:change={toggleTRPResidential}
          />
          <span>Residential and Strategic Land</span>
        </label>
      </div>
    {/if}
  </div>
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
    min-width: 220px;
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
    font-size: 13px;
  }

  .layer-item:hover {
    color: var(--primary-color);
  }

  input[type="checkbox"] {
    cursor: pointer;
  }

  .layer-group {
    margin-bottom: 8px;
  }

  .root-group {
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 8px;
  }

  .root-group:last-child {
    border-bottom: none;
  }

  .nested-group {
    margin-top: 6px;
    padding-left: 0;
    border-bottom: none;
  }

  .layer-group-header {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 0;
    font-size: 13px;
    font-weight: 500;
    color: #555;
  }

  .root-header {
    font-weight: 600;
    color: #333;
    font-size: 14px;
  }

  .layer-group-header .group-arrow,
  .layer-group-header .group-title {
    cursor: pointer;
  }

  .layer-group-header .group-arrow:hover,
  .layer-group-header .group-title:hover {
    color: var(--primary-color);
  }

  .group-arrow {
    font-size: 10px;
    transition: transform 0.2s ease-in-out;
    display: inline-block;
  }

  .group-arrow.expanded {
    transform: rotate(90deg);
  }

  .group-title {
    font-size: 12px;
  }

  .root-header .group-title {
    font-size: 13px;
  }

  .layer-group-content {
    padding-left: 18px;
    margin-top: 4px;
  }

  .layer-group-content .layer-item {
    font-size: 12px;
  }

  .nested-group .layer-group-header {
    font-size: 12px;
    font-weight: 500;
  }

  .nested-group .group-title {
    font-size: 11px;
  }
</style>
