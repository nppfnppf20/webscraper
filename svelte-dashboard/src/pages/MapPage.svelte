<script>
  import { onMount } from 'svelte';
  import 'leaflet/dist/leaflet.css';
  import LayerControl from '../components/LayerControl.svelte';
  import { API_BASE_URL } from '../lib/config.js';
  import {
    filterRecordsWithCoordinates,
    createRenewablesMarker,
    filterRenewables,
    createDataCentresMarker,
    filterDataCentres,
    createREPDSolarMarker,
    createREPDWindMarker,
    createREPDBatteryMarker
  } from '../utils/mapUtils.js';

  let mapContainer = null;
  let map = null;
  let renewablesLayer = null;
  let dataCentresLayer = null;
  let repdSolarLayer = null;
  let repdWindLayer = null;
  let repdBatteryLayer = null;
  let loading = true;
  let error = '';

  onMount(async () => {
    try {
      // Import Leaflet dynamically (client-side only)
      const L = (await import('leaflet')).default;

      // Initialize map
      map = L.map(mapContainer).setView([54.5, -2.5], 6); // Center on UK

      // Add OpenStreetMap tile layer
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(map);

      // Create empty layer groups
      renewablesLayer = L.layerGroup().addTo(map);
      dataCentresLayer = L.layerGroup().addTo(map);
      repdSolarLayer = L.layerGroup().addTo(map);
      repdWindLayer = L.layerGroup().addTo(map);
      repdBatteryLayer = L.layerGroup().addTo(map);

      // Fetch renewables data
      const renewablesResponse = await fetch(`${API_BASE_URL}/planit/renewables-test2`);
      if (!renewablesResponse.ok) throw new Error(`HTTP ${renewablesResponse.status}`);
      const renewablesRawData = await renewablesResponse.json();

      // Apply filtering (medium/large, no conditions)
      const renewablesFiltered = filterRenewables(renewablesRawData);

      // Filter for records with coordinates
      const renewablesWithCoords = filterRecordsWithCoordinates(renewablesFiltered);

      console.log(`⚡ Loaded ${renewablesWithCoords.length} renewables projects with coordinates (out of ${renewablesFiltered.length} filtered)`);

      // Create markers for each renewables record
      renewablesWithCoords.forEach(record => {
        const marker = createRenewablesMarker(L, record);
        renewablesLayer.addLayer(marker);
      });

      // Fetch data centres data
      const dataCentresResponse = await fetch(`${API_BASE_URL}/planit/datacentres`);
      if (!dataCentresResponse.ok) throw new Error(`HTTP ${dataCentresResponse.status}`);
      const dataCentresRawData = await dataCentresResponse.json();

      // Apply filtering (medium/large, no conditions)
      const dataCentresFiltered = filterDataCentres(dataCentresRawData);

      // Filter for records with coordinates
      const dataCentresWithCoords = filterRecordsWithCoordinates(dataCentresFiltered);

      console.log(`🏢 Loaded ${dataCentresWithCoords.length} data centres with coordinates (out of ${dataCentresFiltered.length} filtered)`);

      // Create markers for each data centre record
      dataCentresWithCoords.forEach(record => {
        const marker = createDataCentresMarker(L, record);
        dataCentresLayer.addLayer(marker);
      });

      // Fetch REPD data
      const repdResponse = await fetch(`${API_BASE_URL}/repd`);
      if (!repdResponse.ok) throw new Error(`HTTP ${repdResponse.status}`);
      const repdRawData = await repdResponse.json();

      // Filter for records with coordinates
      const repdWithCoords = filterRecordsWithCoordinates(repdRawData);

      // Split by technology type
      const solarProjects = repdWithCoords.filter(r => r['Technology Type'] === 'Solar Photovoltaics');
      const windProjects = repdWithCoords.filter(r => r['Technology Type'] === 'Wind Onshore');
      const batteryProjects = repdWithCoords.filter(r => r['Technology Type'] === 'Battery');

      console.log(`☀️ Loaded ${solarProjects.length} Solar projects`);
      console.log(`💨 Loaded ${windProjects.length} Wind Onshore projects`);
      console.log(`🔋 Loaded ${batteryProjects.length} Battery projects`);

      // Create markers for each technology type
      solarProjects.forEach(record => {
        const marker = createREPDSolarMarker(L, record);
        repdSolarLayer.addLayer(marker);
      });

      windProjects.forEach(record => {
        const marker = createREPDWindMarker(L, record);
        repdWindLayer.addLayer(marker);
      });

      batteryProjects.forEach(record => {
        const marker = createREPDBatteryMarker(L, record);
        repdBatteryLayer.addLayer(marker);
      });

      loading = false;

      // Fix map size after rendering
      setTimeout(() => {
        map?.invalidateSize();
      }, 0);

    } catch (e) {
      error = e?.message || 'Failed to load map data';
      loading = false;
      console.error('Map error:', e);
    }
  });
</script>

<div class="page-container">
  <h1>Map</h1>

  {#if error}
    <div class="error-message">❌ {error}</div>
  {/if}

  <div class="map-wrapper">
    <div bind:this={mapContainer} class="map-container"></div>

    {#if loading}
      <div class="loading-overlay">
        <div class="spinner"></div>
        <p>Loading renewables data...</p>
      </div>
    {/if}

    {#if map && !loading}
      <LayerControl {map} {renewablesLayer} {dataCentresLayer} {repdSolarLayer} {repdWindLayer} {repdBatteryLayer} />
    {/if}
  </div>
</div>

<style>
  .page-container {
    height: calc(100vh - 120px);
    display: flex;
    flex-direction: column;
    padding: 1rem;
  }

  h1 {
    margin: 0 0 1rem 0;
    color: var(--text-color);
  }

  .error-message {
    padding: 1rem;
    background: #fee;
    border: 1px solid #fcc;
    border-radius: 4px;
    color: #c33;
    margin-bottom: 1rem;
  }

  .map-wrapper {
    flex: 1;
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .map-container {
    width: 100%;
    height: 100%;
    min-height: 400px;
  }

  .loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.9);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 2000;
  }

  .spinner {
    width: 50px;
    height: 50px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .loading-overlay p {
    margin-top: 1rem;
    color: var(--text-color);
    font-size: 14px;
  }
</style>
