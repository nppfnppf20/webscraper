/**
 * Filter renewables records to only those with valid coordinates
 */
export function filterRecordsWithCoordinates(records) {
  return records.filter(record => {
    const lat = parseFloat(record.lat || record.latitude);
    const lng = parseFloat(record.lng || record.longitude);
    return !isNaN(lat) && !isNaN(lng) && lat !== 0 && lng !== 0;
  });
}

/**
 * Create a Leaflet marker for a renewables project
 */
export function createRenewablesMarker(L, record) {
  const lat = parseFloat(record.lat || record.latitude);
  const lng = parseFloat(record.lng || record.longitude);

  const marker = L.marker([lat, lng]);

  // Create popup content
  const popupContent = formatPopupContent(record);
  marker.bindPopup(popupContent);

  return marker;
}

/**
 * Format popup content for a renewables project
 */
export function formatPopupContent(record) {
  const name = record.name || 'Unknown Project';
  const description = record.description || 'No description';
  const address = record.address || 'No address';
  const status = record.app_state || 'Unknown';
  const startDate = record.start_date ? new Date(record.start_date).toLocaleDateString('en-GB') : 'N/A';
  const area = record.area_name || 'Unknown';
  const url = record.url || record.link;

  return `
    <div style="max-width: 300px;">
      <h3 style="margin: 0 0 10px 0; font-size: 14px; font-weight: 600;">${name}</h3>
      <p style="margin: 5px 0; font-size: 12px;"><strong>Area:</strong> ${area}</p>
      <p style="margin: 5px 0; font-size: 12px;"><strong>Status:</strong> ${status}</p>
      <p style="margin: 5px 0; font-size: 12px;"><strong>Start Date:</strong> ${startDate}</p>
      <p style="margin: 5px 0; font-size: 12px;"><strong>Address:</strong> ${address}</p>
      <p style="margin: 5px 0; font-size: 12px;"><strong>Description:</strong> ${description.substring(0, 150)}${description.length > 150 ? '...' : ''}</p>
      ${url ? `<a href="${url}" target="_blank" style="font-size: 12px; color: #007bff;">View on PlanIt →</a>` : ''}
    </div>
  `;
}

/**
 * Apply filtering logic from PlanitRenewablesTest2 page
 */
export function filterRenewables(data) {
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

/**
 * Apply filtering logic for Data Centres (same as renewables)
 */
export function filterDataCentres(data) {
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

/**
 * Create a Leaflet marker for a data centre project (red marker)
 */
export function createDataCentresMarker(L, record) {
  const lat = parseFloat(record.lat || record.latitude);
  const lng = parseFloat(record.lng || record.longitude);

  // Create a red marker icon
  const redIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });

  const marker = L.marker([lat, lng], { icon: redIcon });

  // Create popup content
  const popupContent = formatDataCentresPopupContent(record);
  marker.bindPopup(popupContent);

  return marker;
}

/**
 * Format popup content for a data centre project
 */
export function formatDataCentresPopupContent(record) {
  const name = record.name || 'Unknown Project';
  const description = record.description || 'No description';
  const address = record.address || 'No address';
  const status = record.app_state || 'Unknown';
  const startDate = record.start_date ? new Date(record.start_date).toLocaleDateString('en-GB') : 'N/A';
  const area = record.area_name || 'Unknown';
  const url = record.url || record.link;

  return `
    <div style="max-width: 300px;">
      <h3 style="margin: 0 0 10px 0; font-size: 14px; font-weight: 600; color: #d32f2f;">🏢 ${name}</h3>
      <p style="margin: 5px 0; font-size: 12px;"><strong>Area:</strong> ${area}</p>
      <p style="margin: 5px 0; font-size: 12px;"><strong>Status:</strong> ${status}</p>
      <p style="margin: 5px 0; font-size: 12px;"><strong>Start Date:</strong> ${startDate}</p>
      <p style="margin: 5px 0; font-size: 12px;"><strong>Address:</strong> ${address}</p>
      <p style="margin: 5px 0; font-size: 12px;"><strong>Description:</strong> ${description.substring(0, 150)}${description.length > 150 ? '...' : ''}</p>
      ${url ? `<a href="${url}" target="_blank" style="font-size: 12px; color: #d32f2f;">View on PlanIt →</a>` : ''}
    </div>
  `;
}

/**
 * Get marker style based on development status
 */
function getStatusMarkerStyle(status) {
  const normalizedStatus = status?.toUpperCase().trim() || 'UNKNOWN';

  // Define styles for each status: color, radius, fillOpacity, weight, dashArray
  const styles = {
    'OPERATIONAL': { color: '#2e7d32', fillColor: '#4caf50', radius: 8, fillOpacity: 0.8, weight: 2, dashArray: null },
    'UNDER CONSTRUCTION': { color: '#f57c00', fillColor: '#ff9800', radius: 8, fillOpacity: 0.8, weight: 2, dashArray: '5,5' },
    'PLANNING PERMISSION GRANTED': { color: '#1976d2', fillColor: '#2196f3', radius: 7, fillOpacity: 0.7, weight: 2, dashArray: null },
    'PLANNING APPLICATION SUBMITTED': { color: '#7b1fa2', fillColor: '#9c27b0', radius: 6, fillOpacity: 0.6, weight: 2, dashArray: '3,3' },
    'PLANNING PERMISSION REFUSED': { color: '#c62828', fillColor: '#f44336', radius: 7, fillOpacity: 0.7, weight: 3, dashArray: null },
    'APPEAL GRANTED': { color: '#00796b', fillColor: '#009688', radius: 7, fillOpacity: 0.7, weight: 2, dashArray: null },
    'APPEAL REFUSED': { color: '#d32f2f', fillColor: '#e57373', radius: 6, fillOpacity: 0.7, weight: 3, dashArray: '10,5' },
    'REVISED': { color: '#455a64', fillColor: '#78909c', radius: 6, fillOpacity: 0.6, weight: 2, dashArray: '2,2' }
  };

  return styles[normalizedStatus] || { color: '#616161', fillColor: '#9e9e9e', radius: 5, fillOpacity: 0.5, weight: 1, dashArray: null };
}

/**
 * Create a Leaflet marker for a REPD Solar project (circle markers with status-based styling)
 */
export function createREPDSolarMarker(L, record) {
  const lat = parseFloat(record.lat);
  const lng = parseFloat(record.lng);
  const status = record['Development Status'];
  const style = getStatusMarkerStyle(status);

  // Use orange base color for solar
  const marker = L.circleMarker([lat, lng], {
    radius: style.radius,
    fillColor: '#ff9800', // Orange for solar
    color: style.color, // Border color based on status
    weight: style.weight,
    opacity: 1,
    fillOpacity: style.fillOpacity,
    dashArray: style.dashArray
  });

  marker.bindPopup(formatREPDPopupContent(record));
  return marker;
}

/**
 * Create a Leaflet marker for a REPD Wind project (circle markers with status-based styling)
 */
export function createREPDWindMarker(L, record) {
  const lat = parseFloat(record.lat);
  const lng = parseFloat(record.lng);
  const status = record['Development Status'];
  const style = getStatusMarkerStyle(status);

  // Use blue base color for wind
  const marker = L.circleMarker([lat, lng], {
    radius: style.radius,
    fillColor: '#2196f3', // Blue for wind
    color: style.color, // Border color based on status
    weight: style.weight,
    opacity: 1,
    fillOpacity: style.fillOpacity,
    dashArray: style.dashArray
  });

  marker.bindPopup(formatREPDPopupContent(record));
  return marker;
}

/**
 * Create a Leaflet marker for a REPD Battery project (circle markers with status-based styling)
 */
export function createREPDBatteryMarker(L, record) {
  const lat = parseFloat(record.lat);
  const lng = parseFloat(record.lng);
  const status = record['Development Status'];
  const style = getStatusMarkerStyle(status);

  // Use violet base color for battery
  const marker = L.circleMarker([lat, lng], {
    radius: style.radius,
    fillColor: '#9c27b0', // Violet for battery
    color: style.color, // Border color based on status
    weight: style.weight,
    opacity: 1,
    fillOpacity: style.fillOpacity,
    dashArray: style.dashArray
  });

  marker.bindPopup(formatREPDPopupContent(record));
  return marker;
}

/**
 * Format popup content for a REPD project
 */
export function formatREPDPopupContent(record) {
  const siteName = record['Site Name'] || 'Unknown Site';
  const operator = record['Operator (or Applicant)'] || 'Unknown';
  const techType = record['Technology Type'] || 'Unknown';
  const capacity = record['Installed Capacity (MWelec)'] || 'N/A';
  const status = record['Development Status'] || 'Unknown';
  const address = record['Address'] || 'No address';
  const county = record['County'] || '';
  const region = record['Region'] || '';
  const operational = record['Operational'] || 'N/A';

  return `
    <div style="max-width: 300px;">
      <h3 style="margin: 0 0 10px 0; font-size: 14px; font-weight: 600; color: #2e7d32;">⚡ ${siteName}</h3>
      <p style="margin: 5px 0; font-size: 12px;"><strong>Operator:</strong> ${operator}</p>
      <p style="margin: 5px 0; font-size: 12px;"><strong>Technology:</strong> ${techType}</p>
      <p style="margin: 5px 0; font-size: 12px;"><strong>Capacity:</strong> ${capacity} MW</p>
      <p style="margin: 5px 0; font-size: 12px;"><strong>Status:</strong> ${status}</p>
      <p style="margin: 5px 0; font-size: 12px;"><strong>Operational:</strong> ${operational}</p>
      <p style="margin: 5px 0; font-size: 12px;"><strong>Location:</strong> ${address}${county ? ', ' + county : ''}${region ? ', ' + region : ''}</p>
    </div>
  `;
}

/**
 * Create a square marker with custom color
 */
function createSquareMarker(L, lat, lng, color, record, popupFormatter) {
  const icon = L.divIcon({
    className: 'square-marker',
    html: `<div style="width: 12px; height: 12px; background-color: ${color}; border: 2px solid #fff; box-shadow: 0 0 4px rgba(0,0,0,0.4);"></div>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
    popupAnchor: [0, -8]
  });

  const marker = L.marker([lat, lng], { icon });
  marker.bindPopup(popupFormatter(record));
  return marker;
}

/**
 * Create a TRP Commercial marker (purple square)
 */
export function createTRPCommercialMarker(L, record) {
  const lat = parseFloat(record.lat);
  const lng = parseFloat(record.lng);
  return createSquareMarker(L, lat, lng, '#9c27b0', record, formatTRPPopupContent);
}

/**
 * Create a TRP Energy marker (teal square)
 */
export function createTRPEnergyMarker(L, record) {
  const lat = parseFloat(record.lat);
  const lng = parseFloat(record.lng);
  return createSquareMarker(L, lat, lng, '#009688', record, formatTRPPopupContent);
}

/**
 * Create a TRP Residential marker (coral square)
 */
export function createTRPResidentialMarker(L, record) {
  const lat = parseFloat(record.lat);
  const lng = parseFloat(record.lng);
  return createSquareMarker(L, lat, lng, '#ff7043', record, formatTRPPopupContent);
}

/**
 * Format popup content for a TRP project
 */
export function formatTRPPopupContent(record) {
  const name = record.name || 'Unknown Project';
  const description = record.description || 'No description';

  return `
    <div style="max-width: 300px;">
      <h3 style="margin: 0 0 10px 0; font-size: 14px; font-weight: 600;">${name}</h3>
      <p style="margin: 5px 0; font-size: 12px;">${description}</p>
    </div>
  `;
}
