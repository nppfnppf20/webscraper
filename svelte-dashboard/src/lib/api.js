// Determine API base URL based on environment
const getApiBase = () => {
  // In production (Render), use the backend service URL
  if (import.meta.env.PROD) {
    return 'https://web-scraper-api.onrender.com/api';
  }
  // In development, use localhost
  return 'http://127.0.0.1:8000/api';
};

const API_BASE = getApiBase();

export async function fetchRtpiEvents() {
  const res = await fetch(`${API_BASE}/rtpi/events`);
  if (!res.ok) throw new Error('Failed to fetch RTPI events');
  return res.json();
}

export async function fetchWestLindseyApplication() {
  const res = await fetch(`${API_BASE}/west-lindsey/application`);
  if (!res.ok) throw new Error('Failed to fetch application');
  return res.json();
}

export async function fetchWestLindseyConsultations() {
  const res = await fetch(`${API_BASE}/west-lindsey/consultations`);
  if (!res.ok) throw new Error('Failed to fetch consultations');
  return res.json();
}

export async function fetchPeeringdbIxGb() {
  const res = await fetch(`${API_BASE}/peeringdb/ix/gb`);
  if (!res.ok) throw new Error('Failed to fetch PeeringDB IX (GB)');
  return res.json();
}

export async function fetchPeeringdbFacGb() {
  const res = await fetch(`${API_BASE}/peeringdb/fac/gb`);
  if (!res.ok) throw new Error('Failed to fetch PeeringDB Facilities (GB)');
  return res.json();
}

export async function fetchPlanitDatacentres() {
  const res = await fetch(`${API_BASE}/planit/datacentres`);
  if (!res.ok) throw new Error('Failed to fetch PlanIt data centres');
  return res.json();
}

export async function fetchPlanitRenewables() {
  const res = await fetch(`${API_BASE}/planit/renewables`);
  if (!res.ok) throw new Error('Failed to fetch PlanIt renewables');
  return res.json();
}

export async function fetchPlanitRenewablesTest2() {
  const res = await fetch(`${API_BASE}/planit/renewables-test2`);
  if (!res.ok) throw new Error('Failed to fetch PlanIt renewables test2');
  return res.json();
}

// Generic refresh function
export async function refreshData(endpoint) {
  const res = await fetch(`${API_BASE.replace('/api', '')}${endpoint}`, { method: 'POST' });
  if (!res.ok) throw new Error(`Failed to refresh ${endpoint}`);
  return res.json();
}

// Export the API_BASE for use in components that need custom URLs
export { API_BASE };

