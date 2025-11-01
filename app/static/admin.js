// Admin map + legend script — safe, robust init and explicit map.invalidateSize()

const DAMAGE_TYPES = {
  pothole: '#ef4444', // red
  waste: '#111827',   // black
  lamp: '#f59e0b',    // gold
  default: '#06b6d4'  // cyan
};

function typeColor(type) {
  if (!type) return DAMAGE_TYPES.default;
  const key = String(type).trim().toLowerCase();
  return DAMAGE_TYPES[key] || DAMAGE_TYPES.default;
}

function initLegend() {
  const legendContainer = document.getElementById('legendList') || document.getElementById('legend') || document.getElementById('legendCard');
  if (!legendContainer) {
    console.warn('Legend container not found');
    return;
  }
  // Clear the list first
  const listEl = legendContainer.id === 'legendCard' 
    ? (legendContainer.querySelector('#legendList') || legendContainer) 
    : legendContainer;
  listEl.innerHTML = '';

  // Define images for each damage type
  const DAMAGE_IMAGES = {
    pothole: '/static/Pothole.png',
    garbage: '/static/Waste.png'
  };

  Object.keys(DAMAGE_IMAGES).forEach(type => {
    const imgSrc = DAMAGE_IMAGES[type];
    
    const div = document.createElement('div');
    div.className = 'legend-item';
    div.style.display = 'flex';
    div.style.alignItems = 'center';
    div.style.gap = '8px';
    div.style.marginBottom = '6px';

    div.innerHTML = `
      <div class="color-box" style="
        width: 20px;
        height: 20px;
        background: url(${imgSrc}) no-repeat center/contain;
        border-radius: 4px;
        border: 1px solid #ccc;
      "></div>
      <div style="text-transform:capitalize; font-size:14px;">${type}</div>
    `;

    listEl.appendChild(div);
  });
}

// markers layer
let markersGroup = null;

// Fetch all reports and plot; backend endpoint expected to be /admin/reports returning array
async function fetchReportsAndPlot(map) {
  try {
    // Get current map center and zoom
    const center = map.getCenter();
    const zoom = map.getZoom();
    
    // Calculate radius based on zoom level (smaller radius when zoomed in)
    const radius_km = Math.max(2, 20 - zoom); // zoom 13 = 7km radius, zoom 18 = 2km radius

    const url = `/api/nearby-damage-point?lat=${center.lat}&lon=${center.lng}&radius_km=${radius_km}`;
    const res = await fetch(url, { mode: 'cors' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (!markersGroup) markersGroup = L.layerGroup().addTo(map);
    markersGroup.clearLayers();

    data.forEach(item => {
      const lat = Number(item.latitude);
      const lon = Number(item.longitude);
      if (Number.isNaN(lat) || Number.isNaN(lon)) return;

      const color = typeColor(item.damage_type);

      let iconUrls = "/static/Pothole.png"
      if(item.damage_type == "Waste") {
         iconUrls = "/static/Waste.png"
      }

      const texturedIcon = L.icon({
        iconUrl: iconUrls,
        iconSize: [28, 28],
        iconAnchor: [14, 14]
      });

      const marker = L.marker([lat, lon], { icon: texturedIcon }).addTo(map);
      const imgUrl = item.image ? new URL(item.image_url, window.location.origin).href : null;
      const dt = item.datetime ? new Date(item.datetime).toLocaleString() : '';

      const popupHtml = `
        ${imgUrl ? `<img src="/${item.image}" class="popup-img" alt="preview">` : ''}
        <div><strong>Type:</strong> ${item.damage_type ?? 'Unknown'}</div>
        <div><strong>Location:</strong> ${lat.toFixed(6)}, ${lon.toFixed(6)}</div>
        <div style="margin-top:6px; font-size:0.85em; color:#374151">${dt}</div>
      `;
      marker.bindPopup(popupHtml, { maxWidth: 280 });
      marker.addTo(markersGroup);
    });

    // Store current view in localStorage
    localStorage.setItem('mapView', JSON.stringify({
      lat: center.lat,
      lng: center.lng,
      zoom: zoom
    }));

  } catch (err) {
    console.error('fetchReportsAndPlot error:', err);
  }
}

function initMap() {
  const mapEl = document.getElementById('map');
  if (!mapEl) {
    console.error('map element not found: #map');
    return null;
  }

  // Try to restore previous view
  let initialView;
  try {
    initialView = JSON.parse(localStorage.getItem('mapView')) || {};
  } catch (e) {
    initialView = {};
  }

  const map = L.map('map', { 
    zoomControl: true,
    center: [
      initialView.lat || 27.7172, 
      initialView.lng || 85.3240
    ],
    zoom: initialView.zoom || 13
  });

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  markersGroup = L.layerGroup().addTo(map);

  // initial load
  fetchReportsAndPlot(map);

  // Debounced refresh on map move
  let moveTimer = null;
  map.on('moveend', () => {
    if (moveTimer) clearTimeout(moveTimer);
    moveTimer = setTimeout(() => fetchReportsAndPlot(map), 300);
  });

  return map;
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  try {
    initLegend();
    const map = initMap();
    if (map) {
      // let layout settle then force Leaflet to recalc
      setTimeout(() => {
        try { map.invalidateSize(true); } catch (e) { /* ignore */ }
      }, 250);
      window.addEventListener('resize', () => { try { map.invalidateSize(true); } catch (e) {} });
    }
  } catch (err) {
    console.error('admin init error', err);
  }
});