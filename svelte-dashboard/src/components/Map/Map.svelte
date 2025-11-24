<script>
  import { onMount } from 'svelte';
  import { RISK_LEVELS } from '../utils/riskLevels.js';
  import {
    getBuildingRiskLevel,
    getConservationAreaRiskLevel,
    getScheduledMonumentRiskLevel,
    getGreenBeltRiskLevel,
    getAONBRiskLevel,
    getRenewablesRiskLevel
  } from '../utils/mapRiskAssessment.js';
  import {
    createConservationAreasLayer,
    createListedBuildingsLayer,
    createScheduledMonumentsLayer,
    createGreenBeltLayer,
    createAONBLayer,
    createRenewablesLayer
  } from '../utils/layerFactory.js';
  import {
    processScheduledMonuments,
    processRenewablesData,
    filterBuildingsByGrade,
    setLayerData
  } from '../utils/dataProcessor.js';
  import MapControls from './MapControls.svelte';

  /** @type {HTMLDivElement | null} */
  let mapContainer = null;
  /** @type {import('leaflet').Map | null} */
  let map = null;

  /** @type {(geojson: any) => void} */
  export let onPolygonDrawn = (geojson) => {};
  /** @type {Record<string, any> | null} */
  export let heritageData = null;
  /** @type {Record<string, any> | null} */
  export let landscapeData = null;
  /** @type {Record<string, any> | null} */
  export let renewablesData = null;

  $: console.log('🔍 Map received landscapeData:', landscapeData);
  $: console.log('🔍 Map received renewablesData:', renewablesData);
  $: console.log('📋 All Map props:', { heritageData: !!heritageData, landscapeData: !!landscapeData, renewablesData: !!renewablesData });

  // Force browser refresh

  // Map layers
  /** @type {import('leaflet').GeoJSON | null} */
  let conservationAreasLayer = null;
  /** @type {import('leaflet').GeoJSON | null} */
  let listedBuildingsGradeILayer = null;
  /** @type {import('leaflet').GeoJSON | null} */
  let listedBuildingsGradeIIStarLayer = null;
  /** @type {import('leaflet').GeoJSON | null} */
  let listedBuildingsGradeIILayer = null;
  /** @type {import('leaflet').GeoJSON | null} */
  let scheduledMonumentsLayer = null;
  /** @type {import('leaflet').GeoJSON | null} */
  let greenBeltLayer = null;
  let aonbLayer = null;
  /** @type {import('leaflet').GeoJSON | null} */
  let renewablesLayer = null;

  // Controls component reference
  let mapControls = null;

  // Risk level filter state
  /** @type {Record<string, boolean>} */
  let riskFilters = {
    [RISK_LEVELS.SHOWSTOPPER]: true,
    [RISK_LEVELS.EXTREMELY_HIGH_RISK]: true,
    [RISK_LEVELS.HIGH_RISK]: true,
    [RISK_LEVELS.MEDIUM_HIGH_RISK]: true,
    [RISK_LEVELS.MEDIUM_RISK]: true,
    [RISK_LEVELS.MEDIUM_LOW_RISK]: true,
    [RISK_LEVELS.LOW_RISK]: true
  };

  /**
   * Update layer visibility based on current risk filter settings
   */
  function updateLayerVisibility() {
    if (!conservationAreasLayer || !listedBuildingsGradeILayer || !listedBuildingsGradeIIStarLayer ||
        !listedBuildingsGradeIILayer || !scheduledMonumentsLayer) return;

    console.log('🔄 Updating layer visibility...');

    // Refresh layers with current filter settings
    if (heritageData?.conservation_areas) {
      setLayerData(conservationAreasLayer, heritageData.conservation_areas, (r) => ({
        name: r.name,
        riskLevel: getConservationAreaRiskLevel(r)
      }), true, riskFilters);
    }

    if (heritageData?.listed_buildings) {
      // Filter buildings by grade and apply to appropriate layers
      const gradeIBuildings = filterBuildingsByGrade(heritageData.listed_buildings, 'I');
      const gradeIIStarBuildings = filterBuildingsByGrade(heritageData.listed_buildings, 'II*');
      const gradeIIBuildings = filterBuildingsByGrade(heritageData.listed_buildings, 'II');

      setLayerData(listedBuildingsGradeILayer, gradeIBuildings, (r) => ({
        name: r.name,
        grade: r.grade,
        riskLevel: getBuildingRiskLevel(r)
      }), true, riskFilters);

      setLayerData(listedBuildingsGradeIIStarLayer, gradeIIStarBuildings, (r) => ({
        name: r.name,
        grade: r.grade,
        riskLevel: getBuildingRiskLevel(r)
      }), true, riskFilters);

      setLayerData(listedBuildingsGradeIILayer, gradeIIBuildings, (r) => ({
        name: r.name,
        grade: r.grade,
        riskLevel: getBuildingRiskLevel(r)
      }), true, riskFilters);
    }

    if (heritageData?.scheduled_monuments) {
      const monumentsWithGeometry = processScheduledMonuments(heritageData.scheduled_monuments);
      setLayerData(scheduledMonumentsLayer, monumentsWithGeometry, (r) => ({
        name: r.name,
        riskLevel: getScheduledMonumentRiskLevel(r)
      }), true, riskFilters);
    }

    if (landscapeData?.green_belt) {
      setLayerData(greenBeltLayer, landscapeData.green_belt, (r) => ({
        name: r.name || 'Green Belt',
        riskLevel: getGreenBeltRiskLevel(r)
      }), true, riskFilters);
    }

    if (landscapeData?.aonb) {
      setLayerData(aonbLayer, landscapeData.aonb, (r) => ({
        name: r.name || 'AONB',
        riskLevel: getAONBRiskLevel(r)
      }), true, riskFilters);
    }

    // Update renewables layer when risk filters change
    if (renewablesData?.renewables) {
      const renewablesWithGeometry = processRenewablesData(renewablesData.renewables);
      setLayerData(renewablesLayer, renewablesWithGeometry, (r) => ({
        site_name: r.site_name,
        technology_type: r.technology_type,
        installed_capacity_mw: r.installed_capacity_mw,
        development_status_short: r.development_status_short,
        planning_authority: r.planning_authority,
        planning_application_reference: r.planning_application_reference,
        riskLevel: getRenewablesRiskLevel(r)
      }), true, riskFilters);
    }
  }

  onMount(async () => {
    // Lazy-import Leaflet only on client
    const L = (await import('leaflet')).default;
    // Bring in leaflet-draw for side effects (no typings)
    await import('leaflet-draw');

    // Initialize map
    map = L.map(mapContainer).setView([51.505, -0.09], 13);

    const base = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    // Create all layers using factory functions
    conservationAreasLayer = createConservationAreasLayer(L);
    listedBuildingsGradeILayer = createListedBuildingsLayer(L, 'I');
    listedBuildingsGradeIIStarLayer = createListedBuildingsLayer(L, 'II*');
    listedBuildingsGradeIILayer = createListedBuildingsLayer(L, 'II');
    scheduledMonumentsLayer = createScheduledMonumentsLayer(L);
    greenBeltLayer = createGreenBeltLayer(L);
    aonbLayer = createAONBLayer(L);
    renewablesLayer = createRenewablesLayer(L);

    // Create controls using the MapControls component
    if (mapControls) {
      mapControls.createLayerControl(L, base);
      mapControls.createRiskFilterControl(L);
      mapControls.createDrawControl(L, drawnItems, onPolygonDrawn);
    }

    // Ensure tiles render fully if container size changed during mount
    setTimeout(() => {
      map?.invalidateSize();
    }, 0);
  });

  // Reactive data updates for heritage data
  $: if (heritageData?.conservation_areas) {
    console.log('🏛️ First conservation area structure:', heritageData.conservation_areas[0]);
    setLayerData(conservationAreasLayer, heritageData.conservation_areas, (r) => ({
      name: r.name,
      riskLevel: getConservationAreaRiskLevel(r)
    }), true, riskFilters);
  }

  $: if (heritageData?.listed_buildings) {
    // Filter buildings by grade and apply to appropriate layers
    const gradeIBuildings = filterBuildingsByGrade(heritageData.listed_buildings, 'I');
    const gradeIIStarBuildings = filterBuildingsByGrade(heritageData.listed_buildings, 'II*');
    const gradeIIBuildings = filterBuildingsByGrade(heritageData.listed_buildings, 'II');

    setLayerData(listedBuildingsGradeILayer, gradeIBuildings, (r) => ({
      name: r.name,
      grade: r.grade,
      riskLevel: getBuildingRiskLevel(r)
    }), true, riskFilters);

    setLayerData(listedBuildingsGradeIIStarLayer, gradeIIStarBuildings, (r) => ({
      name: r.name,
      grade: r.grade,
      riskLevel: getBuildingRiskLevel(r)
    }), true, riskFilters);

    setLayerData(listedBuildingsGradeIILayer, gradeIIBuildings, (r) => ({
      name: r.name,
      grade: r.grade,
      riskLevel: getBuildingRiskLevel(r)
    }), true, riskFilters);
  }

  $: if (heritageData?.scheduled_monuments) {
    console.log('🏛️ Scheduled monuments data received:', heritageData.scheduled_monuments);
    console.log('🏛️ Scheduled monuments count:', heritageData.scheduled_monuments.length);
    console.log('🔍 First scheduled monument structure:', heritageData.scheduled_monuments[0]);

    const monumentsWithGeometry = processScheduledMonuments(heritageData.scheduled_monuments);

    console.log('🔧 Converted scheduled monuments with geometry:', monumentsWithGeometry[0]);
    setLayerData(scheduledMonumentsLayer, monumentsWithGeometry, (r) => ({
      name: r.name,
      riskLevel: getScheduledMonumentRiskLevel(r)
    }), true, riskFilters);
  }

  // Reactive data updates for landscape data
  $: if (landscapeData?.green_belt) {
    console.log('🟢 Green Belt data received:', landscapeData.green_belt);
    console.log('🟢 Green Belt count:', landscapeData.green_belt.length);
    console.log('🔍 First Green Belt feature structure:', landscapeData.green_belt[0]);
    setLayerData(greenBeltLayer, landscapeData.green_belt, (r) => ({
      name: r.name || 'Green Belt',
      riskLevel: getGreenBeltRiskLevel(r)
    }), false, riskFilters); // false = don't apply risk filter which requires geometry
  }

  $: if (landscapeData?.aonb) {
    console.log('🔵 AONB data received:', landscapeData.aonb);
    console.log('🔵 AONB count:', landscapeData.aonb.length);
    console.log('🔍 First AONB feature structure:', landscapeData.aonb[0]);
    setLayerData(aonbLayer, landscapeData.aonb, (r) => ({
      name: r.name || 'AONB',
      riskLevel: getAONBRiskLevel(r)
    }), true, riskFilters); // true = apply risk filter using geometry
  }

  // Reactive data updates for renewables data
  $: if (renewablesData) {
    console.log('⚡ Full renewables data:', renewablesData);
    console.log('⚡ renewablesData keys:', Object.keys(renewablesData));

    // Check if it has renewables property
    if (renewablesData.renewables) {
      console.log('⚡ Renewables data found:', renewablesData.renewables);
      console.log('⚡ Renewables count:', renewablesData.renewables.length);
      console.log('🔍 First renewables item structure:', renewablesData.renewables[0]);
    } else {
      console.log('❌ No renewables property found in renewablesData');
    }

    const renewablesWithGeometry = processRenewablesData(renewablesData.renewables);

    console.log('🔧 Converted renewables with geometry:', renewablesWithGeometry.length > 0 ? renewablesWithGeometry[0] : 'No renewables data');

    // Debug: Check risk levels before filtering
    if (renewablesWithGeometry.length > 0) {
      console.log('🎯 Checking renewables risk levels:');
      renewablesWithGeometry.forEach((r, i) => {
        const riskLevel = getRenewablesRiskLevel(r);
        console.log(`  [${i}] ${r.site_name}: status="${r.development_status_short}", on_site=${r.on_site}, riskLevel="${riskLevel}"`);
      });
      console.log('🎯 Current risk filters:', riskFilters);
    }

    setLayerData(renewablesLayer, renewablesWithGeometry, (r) => ({
      site_name: r.site_name,
      technology_type: r.technology_type,
      installed_capacity_mw: r.installed_capacity_mw,
      development_status_short: r.development_status_short,
      planning_authority: r.planning_authority,
      planning_application_reference: r.planning_application_reference,
      riskLevel: getRenewablesRiskLevel(r)
    }), true, riskFilters);
  }
</script>

<div bind:this={mapContainer} class="map-container"></div>

<MapControls
  bind:this={mapControls}
  {map}
  {riskFilters}
  onRiskFilterChange={updateLayerVisibility}
  {conservationAreasLayer}
  {listedBuildingsGradeILayer}
  {listedBuildingsGradeIIStarLayer}
  {listedBuildingsGradeIILayer}
  {scheduledMonumentsLayer}
  {greenBeltLayer}
  {aonbLayer}
  {renewablesLayer}
/>

<style>
  .map-container {
    height: 100%;
    width: 100%;
    min-height: 400px;
    position: relative;
  }
</style>