import { API_BASE_URL } from './config.js';

const API_BASE = API_BASE_URL;

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

// Refresh functions
export async function refreshRtpi() {
  const res = await fetch(`${API_BASE}/refresh/rtpi`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to refresh RTPI');
  return res.json();
}

export async function refreshWestLindsey() {
  const res = await fetch(`${API_BASE}/refresh/west-lindsey`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to refresh West Lindsey');
  return res.json();
}

export async function refreshPeeringdbFac() {
  const res = await fetch(`${API_BASE}/refresh/peeringdb-fac`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to refresh PeeringDB Facilities');
  return res.json();
}

export async function refreshPlanitDatacentres() {
  const res = await fetch(`${API_BASE}/refresh/planit-dc`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to refresh PlanIt datacentres');
  return res.json();
}

export async function refreshPlanitRenewables() {
  const res = await fetch(`${API_BASE}/refresh/planit-renew`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to refresh PlanIt renewables');
  return res.json();
}

export async function refreshPlanitRenewablesTest2() {
  const res = await fetch(`${API_BASE}/refresh/planit-test2`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to refresh PlanIt renewables test2');
  return res.json();
}

