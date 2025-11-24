<script>
  import { onMount } from 'svelte';

  export let map = null;
  export let renewablesLayer = null;

  let showRenewables = true;

  function toggleRenewables() {
    // showRenewables is already updated by bind:checked
    if (renewablesLayer && map) {
      if (showRenewables) {
        map.addLayer(renewablesLayer);
      } else {
        map.removeLayer(renewablesLayer);
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
