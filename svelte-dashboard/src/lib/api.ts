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

