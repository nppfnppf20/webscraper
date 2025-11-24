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
