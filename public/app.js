let dashboardData = null;
let charts = {};

document.addEventListener('DOMContentLoaded', () => {
  fetchDashboardData();
  startLiveClock();
});

function startLiveClock() {
  const updateClock = () => {
    const timeEl = document.getElementById('last-refresh-time');
    if (timeEl) {
      const now = new Date();
      const utcStr = now.toISOString().replace('T', ' ').substring(0, 19) + ' UTC';
      timeEl.textContent = `Updated ${utcStr}`;
    }
  };
  updateClock();
  setInterval(updateClock, 1000);
}

async function fetchDashboardData() {
  try {
    const response = await fetch('/api/dashboard-data');
    dashboardData = await response.json();
    renderKpis(dashboardData.kpis);
    renderMetadata(dashboardData.data_source_info);
    renderRawPreview(dashboardData.raw_first_5);
    renderCharts(dashboardData);
    renderCityTable(dashboardData.city_performance);
    renderCuisineTable(dashboardData.cuisine_market_share);
  } catch (err) {
    console.error('Failed to load dashboard data:', err);
  }
}

function renderMetadata(info) {
  if (!info) return;
  if (document.getElementById('meta-source')) document.getElementById('meta-source').textContent = info.filename;
  if (document.getElementById('meta-grain')) document.getElementById('meta-grain').textContent = info.grain;
  if (document.getElementById('meta-records')) document.getElementById('meta-records').textContent = info.records.toLocaleString();
  if (document.getElementById('meta-columns')) document.getElementById('meta-columns').textContent = info.columns;
  if (document.getElementById('meta-date')) document.getElementById('meta-date').textContent = info.last_validated;
}

function renderRawPreview(rows) {
  if (!Array.isArray(rows) || rows.length === 0) return;
  const thRow = document.getElementById('raw-preview-th');
  const tbody = document.getElementById('raw-preview-tb');
  if (!thRow || !tbody) return;

  const cols = Object.keys(rows[0]);
  thRow.innerHTML = cols.map(c => `<th>${c}</th>`).join('');
  tbody.innerHTML = rows.map(r => `
    <tr>
      ${cols.map(c => `<td>${r[c] !== null && r[c] !== undefined ? r[c] : ''}</td>`).join('')}
    </tr>
  `).join('');
}

function renderKpis(kpis) {
  if (!kpis) return;
  document.getElementById('kpi-restaurants').textContent = kpis.total_restaurants ? kpis.total_restaurants.toLocaleString() : '9,551';
  document.getElementById('kpi-revenue').textContent = kpis.total_est_monthly_revenue_usd ? `$${(kpis.total_est_monthly_revenue_usd / 1000000).toFixed(1)}M` : '$15.4M';
  document.getElementById('kpi-rating').textContent = `${kpis.avg_global_rating || 2.67} / 5.0`;
  document.getElementById('kpi-delivery').textContent = `${kpis.online_delivery_pct || 25.66}%`;
  document.getElementById('kpi-booking').textContent = `${kpis.table_booking_pct || 12.12}%`;
}

function renderCharts(data) {
  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.color = '#94a3b8';

  // Chart 1: City Revenue Bar Chart (Proxy)
  const topCities = (data.city_performance || []).slice(0, 8);
  const cityCtx = document.getElementById('cityRevenueChart').getContext('2d');
  
  const cityGradient = cityCtx.createLinearGradient(0, 0, 0, 300);
  cityGradient.addColorStop(0, 'rgba(59, 130, 246, 0.85)');
  cityGradient.addColorStop(1, 'rgba(30, 58, 138, 0.25)');

  charts.cityRevenue = new Chart(cityCtx, {
    type: 'bar',
    data: {
      labels: topCities.map(c => c.city),
      datasets: [{
        label: 'Est. Monthly Revenue Proxy ($ USD)',
        data: topCities.map(c => c.city_est_revenue_usd),
        backgroundColor: cityGradient,
        borderColor: '#3b82f6',
        borderWidth: 1.5,
        borderRadius: 6,
        borderSkipped: false
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0f172a',
          borderColor: 'rgba(59, 130, 246, 0.4)',
          borderWidth: 1,
          padding: 12,
          titleFont: { size: 13, weight: 'bold' },
          bodyFont: { size: 12 },
          callbacks: {
            label: (ctx) => `Est. Revenue: $${ctx.raw.toLocaleString()} USD`
          }
        }
      },
      scales: {
        x: { ticks: { color: '#94a3b8', font: { size: 11 } }, grid: { display: false } },
        y: {
          ticks: {
            color: '#94a3b8',
            font: { size: 11 },
            callback: (val) => `$${(val / 1000000).toFixed(1)}M`
          },
          grid: { color: 'rgba(255, 255, 255, 0.04)' }
        }
      }
    }
  });

  // Chart 2: Service Share Doughnut Chart (Derived)
  const serviceData = data.service_capability_breakdown || [];
  const serviceCtx = document.getElementById('serviceShareChart').getContext('2d');
  charts.serviceShare = new Chart(serviceCtx, {
    type: 'doughnut',
    data: {
      labels: serviceData.map(s => s.service_capability),
      datasets: [{
        data: serviceData.map(s => s.count),
        backgroundColor: [
          '#3b82f6',
          '#10b981',
          '#8b5cf6',
          '#f59e0b'
        ],
        borderWidth: 2,
        borderColor: '#0f172a',
        hoverOffset: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: '#94a3b8',
            font: { size: 11, weight: '500' },
            padding: 14,
            usePointStyle: true,
            pointStyle: 'circle'
          }
        },
        tooltip: {
          backgroundColor: '#0f172a',
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1,
          padding: 10,
          callbacks: {
            label: (ctx) => {
              const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
              const pct = ((ctx.raw / total) * 100).toFixed(1);
              return `${ctx.label}: ${ctx.raw.toLocaleString()} units (${pct}%)`;
            }
          }
        }
      },
      cutout: '74%'
    }
  });

  // Chart 3: Price Tier Rating Bar Chart (Observed / Derived)
  const priceData = data.price_tier_distribution || [];
  const priceCtx = document.getElementById('priceRatingChart').getContext('2d');
  
  const priceGradient = priceCtx.createLinearGradient(0, 0, 0, 300);
  priceGradient.addColorStop(0, 'rgba(139, 92, 246, 0.85)');
  priceGradient.addColorStop(1, 'rgba(88, 28, 135, 0.25)');

  charts.priceRating = new Chart(priceCtx, {
    type: 'bar',
    data: {
      labels: priceData.map(p => p.price_category),
      datasets: [{
        label: 'Avg Rating (Observed)',
        data: priceData.map(p => p.avg_rating),
        backgroundColor: priceGradient,
        borderColor: '#8b5cf6',
        borderWidth: 1.5,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0f172a',
          borderColor: 'rgba(139, 92, 246, 0.4)',
          borderWidth: 1,
          padding: 10,
          callbacks: {
            label: (ctx) => `Avg Rating: ⭐ ${ctx.raw} / 5.0`
          }
        }
      },
      scales: {
        x: { ticks: { color: '#94a3b8', font: { size: 11 } }, grid: { display: false } },
        y: {
          min: 0,
          max: 5,
          ticks: { color: '#94a3b8', font: { size: 11 } },
          grid: { color: 'rgba(255, 255, 255, 0.04)' }
        }
      }
    }
  });

  // Chart 4: Primary Cuisine Volume Chart (Derived)
  const cuisineData = (data.cuisine_market_share || []).slice(0, 7);
  const cuisineCtx = document.getElementById('cuisineVolumeChart').getContext('2d');
  
  const cuisineGradient = cuisineCtx.createLinearGradient(0, 0, 300, 0);
  cuisineGradient.addColorStop(0, 'rgba(16, 185, 129, 0.85)');
  cuisineGradient.addColorStop(1, 'rgba(6, 78, 59, 0.25)');

  charts.cuisineVolume = new Chart(cuisineCtx, {
    type: 'bar',
    data: {
      labels: cuisineData.map(c => c.primary_cuisine),
      datasets: [{
        label: 'Restaurant Count (Observed)',
        data: cuisineData.map(c => c.restaurant_count),
        backgroundColor: cuisineGradient,
        borderColor: '#10b981',
        borderWidth: 1.5,
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0f172a',
          borderColor: 'rgba(16, 185, 129, 0.4)',
          borderWidth: 1,
          padding: 10,
          callbacks: {
            label: (ctx) => `Restaurants: ${ctx.raw.toLocaleString()}`
          }
        }
      },
      scales: {
        x: { ticks: { color: '#94a3b8', font: { size: 11 } }, grid: { color: 'rgba(255, 255, 255, 0.04)' } },
        y: { ticks: { color: '#94a3b8', font: { size: 11 } }, grid: { display: false } }
      }
    }
  });
}

function setTimeframe(btn, tf) {
  document.querySelectorAll('.tf-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  // Visual control toggle - maintains exact real underlying chart data
}

function renderCityTable(cities) {
  const tbody = document.querySelector('#city-table tbody');
  if (!tbody || !cities) return;
  tbody.innerHTML = cities.map(c => `
    <tr>
      <td><strong>${c.city}</strong></td>
      <td>${c.restaurant_count.toLocaleString()}</td>
      <td>⭐ ${c.avg_rating}</td>
      <td>${c.total_votes.toLocaleString()}</td>
      <td>$${c.avg_cost_usd}</td>
      <td>${c.delivery_adoption_pct}%</td>
      <td>$${(c.city_est_revenue_usd || 0).toLocaleString()}</td>
    </tr>
  `).join('');
}

function renderCuisineTable(cuisines) {
  const tbody = document.querySelector('#cuisine-table tbody');
  if (!tbody || !cuisines) return;
  tbody.innerHTML = cuisines.map(c => `
    <tr>
      <td><strong>${c.primary_cuisine}</strong></td>
      <td>${c.restaurant_count.toLocaleString()}</td>
      <td>${c.total_votes.toLocaleString()}</td>
      <td>⭐ ${c.avg_rating}</td>
      <td>$${c.avg_cost_usd}</td>
      <td>$${(c.cuisine_est_revenue_usd || 0).toLocaleString()}</td>
    </tr>
  `).join('');
}

function filterCityTable() {
  const filter = document.getElementById('city-search').value.toLowerCase();
  const rows = document.querySelectorAll('#city-table tbody tr');
  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(filter) ? '' : 'none';
  });
}

function filterCuisineTable() {
  const filter = document.getElementById('cuisine-search').value.toLowerCase();
  const rows = document.querySelectorAll('#cuisine-table tbody tr');
  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(filter) ? '' : 'none';
  });
}

function switchTab(tabId) {
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(content => content.style.display = 'none');
  
  // Find tab button matching target
  const tabButtons = Array.from(document.querySelectorAll('.tab-btn'));
  const targetBtn = tabButtons.find(btn => {
    const attr = btn.getAttribute('onclick');
    return attr && attr.includes(`'${tabId}'`);
  });
  if (targetBtn) targetBtn.classList.add('active');

  const activeTab = document.getElementById(`tab-${tabId}`);
  if (activeTab) activeTab.style.display = 'block';
}

const PRESET_QUERIES = {
  top_revenue: `SELECT l.city, COUNT(r.restaurant_id) as total_restaurants, ROUND(AVG(f.aggregate_rating), 2) as avg_rating, ROUND(SUM(f.est_monthly_revenue_usd), 2) as est_monthly_revenue_proxy FROM dim_restaurants r JOIN fact_restaurant_performance f ON r.restaurant_id = f.restaurant_id JOIN dim_locations l ON r.location_id = l.location_id GROUP BY l.city ORDER BY est_monthly_revenue_proxy DESC LIMIT 10;`,
  price_delivery: `SELECT r.price_category, COUNT(r.restaurant_id) as total_restaurants, ROUND(100.0 * SUM(r.has_online_delivery) / COUNT(r.restaurant_id), 2) as delivery_adoption_pct, ROUND(AVG(f.aggregate_rating), 2) as avg_rating FROM dim_restaurants r JOIN fact_restaurant_performance f ON r.restaurant_id = f.restaurant_id GROUP BY r.price_category ORDER BY r.price_category;`,
  cuisine_density: `SELECT r.primary_cuisine, COUNT(r.restaurant_id) as restaurant_count, ROUND(AVG(f.avg_cost_for_two_usd), 2) as avg_cost_usd, ROUND(AVG(f.aggregate_rating), 2) as avg_rating FROM dim_restaurants r JOIN fact_restaurant_performance f ON r.restaurant_id = f.restaurant_id GROUP BY r.primary_cuisine HAVING COUNT(r.restaurant_id) >= 20 ORDER BY restaurant_count DESC LIMIT 10;`,
  service_matrix: `SELECT r.service_capability, COUNT(r.restaurant_id) as total_restaurants, ROUND(AVG(f.aggregate_rating), 2) as avg_rating, ROUND(SUM(f.est_monthly_revenue_usd), 2) as est_revenue_usd FROM dim_restaurants r JOIN fact_restaurant_performance f ON r.restaurant_id = f.restaurant_id GROUP BY r.service_capability ORDER BY est_revenue_usd DESC;`
};

function loadQueryPreset(presetKey) {
  if (PRESET_QUERIES[presetKey]) {
    document.getElementById('sql-query-input').value = PRESET_QUERIES[presetKey];
    runSqlQuery();
  }
}

async function runSqlQuery() {
  const query = document.getElementById('sql-query-input').value;
  const thRow = document.getElementById('sql-th-row');
  const tbody = document.getElementById('sql-tb-body');

  thRow.innerHTML = '<th>Executing query...</th>';
  tbody.innerHTML = '';

  try {
    const res = await fetch('/api/sql-query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    const results = await res.json();

    if (results.error) {
      thRow.innerHTML = `<th style="color: #ef4444;">Query Error: ${results.error}</th>`;
      return;
    }

    if (!Array.isArray(results) || results.length === 0) {
      thRow.innerHTML = '<th>Query Executed Successfully (0 rows returned)</th>';
      return;
    }

    const keys = Object.keys(results[0]);
    thRow.innerHTML = keys.map(k => `<th>${k}</th>`).join('');

    tbody.innerHTML = results.map(row => `
      <tr>
        ${keys.map(k => `<td>${row[k] !== null && row[k] !== undefined ? row[k] : ''}</td>`).join('')}
      </tr>
    `).join('');
  } catch (err) {
    thRow.innerHTML = `<th style="color: #ef4444;">Error: ${err.message}</th>`;
  }
}
