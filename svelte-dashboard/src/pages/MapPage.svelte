<script>
  import { onMount } from 'svelte';
  import 'leaflet/dist/leaflet.css';
  import LayerControl from '../components/LayerControl.svelte';
  import { API_BASE_URL } from '../lib/config.js';
  import {
    filterRecordsWithCoordinates,
    createRenewablesMarker,
    filterRenewables
  } from '../utils/mapUtils.js';

  let mapContainer = null;
  let map = null;
  let renewablesLayer = null;
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

      // Create empty renewables layer
      renewablesLayer = L.layerGroup().addTo(map);

      // Fetch renewables data
      const response = await fetch(`${API_BASE_URL}/planit/renewables-test2`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const rawData = await response.json();

      // Apply filtering (medium/large, no conditions)
      const filteredData = filterRenewables(rawData);

      // Filter for records with coordinates
      const recordsWithCoords = filterRecordsWithCoordinates(filteredData);

      console.log(`📍 Loaded ${recordsWithCoords.length} renewables projects with coordinates (out of ${filteredData.length} filtered)`);

      // Create markers for each record
      recordsWithCoords.forEach(record => {
        const marker = createRenewablesMarker(L, record);
        renewablesLayer.addLayer(marker);
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
      <LayerControl {map} {renewablesLayer} />
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
