/**
 * Zomato Intelligence & Clustering Dashboard - Main JavaScript
 * Created for Priya Sharma's Portfolio & Vercel Deployment
 */

(function () {
  'use strict';

  // Check if data is available
  if (!window.ZOMATO_DATA) {
    console.error('Zomato data is not loaded.');
    return;
  }

  const data = window.ZOMATO_DATA;
  let currentK = 3;
  let currentClusterFilter = 'ALL';
  let currentCuisineFilter = 'ALL';
  let currentSearchQuery = '';
  let currentSort = 'default';

  // Chart Instances
  let elbowChartInstance = null;
  let clusterDistChartInstance = null;
  let costHistChartInstance = null;
  let cuisinesChartInstance = null;
  let ratingsChartInstance = null;
  let topReviewedChartInstance = null;

  // Cluster Theme Names and Colors
  const clusterColorPalette = [
    { name: 'Budget Friendly', color: '#10b981', bg: 'rgba(16, 185, 129, 0.15)', border: 'rgba(16, 185, 129, 0.4)', icon: 'fa-bowl-rice' },
    { name: 'Mid-Range Dining', color: '#3b82f6', bg: 'rgba(59, 130, 246, 0.15)', border: 'rgba(59, 130, 246, 0.4)', icon: 'fa-utensils' },
    { name: 'Premium & Fine Dine', color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.15)', border: 'rgba(245, 158, 11, 0.4)', icon: 'fa-wine-glass' },
    { name: 'Luxury & Exclusive', color: '#a855f7', bg: 'rgba(168, 85, 247, 0.15)', border: 'rgba(168, 85, 247, 0.4)', icon: 'fa-crown' },
    { name: 'Elite Signature', color: '#ec4899', bg: 'rgba(236, 72, 153, 0.15)', border: 'rgba(236, 72, 153, 0.4)', icon: 'fa-gem' },
    { name: 'Ultra Luxury', color: '#06b6d4', bg: 'rgba(6, 182, 212, 0.15)', border: 'rgba(6, 182, 212, 0.4)', icon: 'fa-champagne-glasses' }
  ];

  // DOM Elements
  const kSlider = document.getElementById('k-slider');
  const kBadge = document.getElementById('k-current-badge');
  const kOptimalHint = document.getElementById('k-optimal-hint');
  const pillSilScore = document.getElementById('pill-sil-score');
  const pillSilStatus = document.getElementById('pill-sil-status');
  const pillInertia = document.getElementById('pill-inertia');
  const resetBtn = document.getElementById('reset-cluster-btn');
  const clusterCardsContainer = document.getElementById('cluster-cards-container');
  const clusterChartSubtitle = document.getElementById('cluster-chart-subtitle');

  // Directory Elements
  const searchInput = document.getElementById('search-input');
  const cuisineFilter = document.getElementById('cuisine-filter');
  const sortSelect = document.getElementById('sort-select');
  const clusterPillsContainer = document.getElementById('cluster-filter-pills');
  const resultsCountText = document.getElementById('results-count-text');
  const restaurantsGridContainer = document.getElementById('restaurants-grid-container');

  // Predictor Elements
  const runPredictionBtn = document.getElementById('run-prediction-btn');
  const predCostInput = document.getElementById('pred-cost');
  const predNameInput = document.getElementById('pred-name');
  const predBadge = document.getElementById('pred-badge');
  const predCostDisplay = document.getElementById('pred-cost-display');
  const predRecommendation = document.getElementById('pred-recommendation');

  // Helper: Format Currency
  function formatRupee(amount) {
    return '₹' + Math.round(amount).toLocaleString('en-IN');
  }

  // Initialize
  function init() {
    initCharts();
    updateClusteringUI(currentK);
    renderRestaurantCards();
    setupEventListeners();
  }

  // =========================================================================
  // CHARTS INITIALIZATION
  // =========================================================================
  function initCharts() {
    // 1. Elbow Method Curve
    const elbowCtx = document.getElementById('elbowChart').getContext('2d');
    const elbowKLabels = ['K=2', 'K=3', 'K=4', 'K=5', 'K=6'];
    const elbowInertiaVals = [
      data.cluster_models[2].inertia,
      data.cluster_models[3].inertia,
      data.cluster_models[4].inertia,
      data.cluster_models[5].inertia,
      data.cluster_models[6].inertia
    ];

    elbowChartInstance = new Chart(elbowCtx, {
      type: 'line',
      data: {
        labels: elbowKLabels,
        datasets: [{
          label: 'Inertia (Within-Cluster Sum of Squares)',
          data: elbowInertiaVals,
          borderColor: '#e23744',
          backgroundColor: 'rgba(226, 55, 68, 0.1)',
          fill: true,
          tension: 0.35,
          pointBackgroundColor: elbowKLabels.map((_, i) => (i === currentK - 2 ? '#ff5a66' : '#ffffff')),
          pointBorderColor: '#e23744',
          pointBorderWidth: 2,
          pointRadius: elbowKLabels.map((_, i) => (i === currentK - 2 ? 8 : 5)),
          pointHoverRadius: 9
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#151c2c',
            titleColor: '#fff',
            bodyColor: '#cbd5e1',
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
            padding: 12
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans' } }
          },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans' } },
            title: { display: true, text: 'Inertia (Error Metric)', color: '#64748b' }
          }
        }
      }
    });

    // 2. Cluster Cost Distribution Chart
    const clusterCtx = document.getElementById('clusterDistChart').getContext('2d');
    clusterDistChartInstance = new Chart(clusterCtx, {
      type: 'bar',
      data: getClusterDistChartData(currentK),
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#151c2c',
            titleColor: '#fff',
            bodyColor: '#cbd5e1',
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
            padding: 12,
            callbacks: {
              label: function (ctx) {
                return `Mean Cost: ₹${ctx.parsed.y} | Count: ${ctx.raw.count} rests`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans' } }
          },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans' } },
            title: { display: true, text: 'Average Cost for Two (₹)', color: '#64748b' }
          }
        }
      }
    });

    // 3. Cost Histogram (EDA)
    const costHistCtx = document.getElementById('costHistChart').getContext('2d');
    costHistChartInstance = new Chart(costHistCtx, {
      type: 'bar',
      data: {
        labels: data.cost_histogram.bins,
        datasets: [{
          label: 'Number of Restaurants',
          data: data.cost_histogram.counts,
          backgroundColor: 'rgba(16, 185, 129, 0.45)',
          borderColor: '#10b981',
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
            backgroundColor: '#151c2c',
            titleColor: '#fff',
            bodyColor: '#cbd5e1',
            padding: 10
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94a3b8', font: { size: 11 } }
          },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94a3b8' },
            title: { display: true, text: 'Restaurant Count', color: '#64748b' }
          }
        }
      }
    });

    // 4. Top Cuisines (EDA)
    const cuisinesCtx = document.getElementById('cuisinesChart').getContext('2d');
    const cuisineLabels = data.cuisine_ranking.map(c => c.cuisine);
    const cuisineCounts = data.cuisine_ranking.map(c => c.count);

    cuisinesChartInstance = new Chart(cuisinesCtx, {
      type: 'bar',
      data: {
        labels: cuisineLabels,
        datasets: [{
          label: 'Restaurants Offering Cuisine',
          data: cuisineCounts,
          backgroundColor: 'rgba(226, 55, 68, 0.5)',
          borderColor: '#e23744',
          borderWidth: 1.5,
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#151c2c',
            titleColor: '#fff',
            bodyColor: '#cbd5e1',
            padding: 10
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94a3b8' }
          },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#cbd5e1', font: { size: 11 } }
          }
        }
      }
    });

    // 5. Ratings Breakdown (EDA)
    const ratingsCtx = document.getElementById('ratingsChart').getContext('2d');
    const ratingLabels = data.rating_distribution.map(r => `${r.star} ★ Stars`);
    const ratingCounts = data.rating_distribution.map(r => r.count);

    ratingsChartInstance = new Chart(ratingsCtx, {
      type: 'doughnut',
      data: {
        labels: ratingLabels,
        datasets: [{
          data: ratingCounts,
          backgroundColor: [
            '#ef4444', // 1 star
            '#f97316', // 2 star
            '#eab308', // 3 star
            '#3b82f6', // 4 star
            '#10b981'  // 5 star
          ],
          borderColor: '#0b0e14',
          borderWidth: 3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: {
          legend: {
            position: 'right',
            labels: {
              color: '#cbd5e1',
              font: { family: 'Plus Jakarta Sans', size: 12 },
              padding: 14
            }
          },
          tooltip: {
            backgroundColor: '#151c2c',
            titleColor: '#fff',
            bodyColor: '#cbd5e1',
            padding: 10
          }
        }
      }
    });

    // 6. Top Reviewed Restaurants (EDA)
    const topReviewedCtx = document.getElementById('topReviewedChart').getContext('2d');
    const topRestLabels = data.top_reviewed.map(r => r.name.length > 18 ? r.name.substring(0, 18) + '...' : r.name);
    const topRestCounts = data.top_reviewed.map(r => r.reviews);

    topReviewedChartInstance = new Chart(topReviewedCtx, {
      type: 'bar',
      data: {
        labels: topRestLabels,
        datasets: [{
          label: 'Total Reviews in Dataset',
          data: topRestCounts,
          backgroundColor: 'rgba(59, 130, 246, 0.5)',
          borderColor: '#3b82f6',
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
            backgroundColor: '#151c2c',
            titleColor: '#fff',
            bodyColor: '#cbd5e1',
            padding: 10
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94a3b8', maxRotation: 45, minRotation: 45, font: { size: 10 } }
          },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94a3b8' },
            title: { display: true, text: 'Review Count', color: '#64748b' }
          }
        }
      }
    });
  }

  // Generate Data for Cluster Distribution Bar Chart
  function getClusterDistChartData(k) {
    const model = data.cluster_models[k];
    const labels = model.clusters.map((c, i) => {
      const paletteItem = clusterColorPalette[i] || clusterColorPalette[clusterColorPalette.length - 1];
      return `${paletteItem.name} (T${i})`;
    });

    const datasetData = model.clusters.map(c => ({
      x: `Cluster ${c.cluster_id}`,
      y: c.mean_cost,
      count: c.count
    }));

    const bgColors = model.clusters.map((_, i) => (clusterColorPalette[i] ? clusterColorPalette[i].color : '#64748b'));

    return {
      labels: labels,
      datasets: [{
        label: 'Mean Cost (₹)',
        data: datasetData,
        backgroundColor: bgColors,
        borderRadius: 8,
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.1)'
      }]
    };
  }

  // =========================================================================
  // UPDATE CLUSTERING UI (ON SLIDER CHANGE)
  // =========================================================================
  function updateClusteringUI(k) {
    currentK = parseInt(k, 10);
    const model = data.cluster_models[currentK];

    // 1. Update Badges & Meters
    kBadge.textContent = `K = ${currentK}`;
    pillSilScore.textContent = model.silhouette.toFixed(3);
    pillInertia.textContent = model.inertia.toFixed(2);

    if (currentK === 3) {
      kOptimalHint.innerHTML = '<i class="fa-solid fa-star"></i> Recommended Elbow Point';
      kOptimalHint.style.color = 'var(--primary-light)';
    } else {
      kOptimalHint.innerHTML = '<i class="fa-solid fa-circle-info"></i> Alternative Grouping';
      kOptimalHint.style.color = 'var(--text-dim)';
    }

    if (model.silhouette >= 0.58) {
      pillSilStatus.innerHTML = '<i class="fa-solid fa-circle-check"></i> Strong Separation';
      pillSilStatus.style.color = 'var(--budget)';
    } else {
      pillSilStatus.innerHTML = '<i class="fa-solid fa-circle-info"></i> Moderate Separation';
      pillSilStatus.style.color = 'var(--mid)';
    }

    clusterChartSubtitle.textContent = `Showing K=${currentK} Tiers`;

    // 2. Update Elbow Chart Highlight
    if (elbowChartInstance) {
      const pointColors = [2, 3, 4, 5, 6].map(val => (val === currentK ? '#ff5a66' : '#ffffff'));
      const pointSizes = [2, 3, 4, 5, 6].map(val => (val === currentK ? 9 : 5));
      elbowChartInstance.data.datasets[0].pointBackgroundColor = pointColors;
      elbowChartInstance.data.datasets[0].pointRadius = pointSizes;
      elbowChartInstance.update();
    }

    // 3. Update Cluster Distribution Chart
    if (clusterDistChartInstance) {
      const newChartData = getClusterDistChartData(currentK);
      clusterDistChartInstance.data = newChartData;
      clusterDistChartInstance.update();
    }

    // 4. Render Dynamic Cluster Cards
    renderClusterCards(model);

    // 5. Update Directory Filter Pills
    renderClusterFilterPills(model);

    // 6. Refresh Restaurant Grid to reflect new clusters
    renderRestaurantCards();
  }

  // Render Cluster Detail Cards
  function renderClusterCards(model) {
    clusterCardsContainer.innerHTML = '';

    model.clusters.forEach((c, idx) => {
      const palette = clusterColorPalette[idx] || clusterColorPalette[clusterColorPalette.length - 1];
      const pct = Math.round((c.count / data.total_restaurants) * 100);

      // Find common cuisines in this cluster
      const restsInCluster = data.restaurants.filter(r => r.clusters[`k${currentK}`] === c.cluster_id);
      const cuisinesInCluster = {};
      restsInCluster.forEach(r => {
        r.cuisines.forEach(cuisine => {
          cuisinesInCluster[cuisine] = (cuisinesInCluster[cuisine] || 0) + 1;
        });
      });
      const topCuisines = Object.entries(cuisinesInCluster)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3)
        .map(x => x[0])
        .join(', ');

      const card = document.createElement('div');
      card.className = 'cluster-info-card';
      card.style.borderTop = `3px solid ${palette.color}`;

      card.innerHTML = `
        <div class="cluster-info-top">
          <span class="cluster-name-badge" style="background: ${palette.bg}; color: ${palette.color}; border: 1px solid ${palette.border};">
            <i class="fa-solid ${palette.icon}"></i> ${palette.name}
          </span>
          <span class="cluster-count">${c.count} places (${pct}%)</span>
        </div>

        <div class="cluster-stat-grid">
          <div>
            <div class="stat-item-lbl">Cost Range</div>
            <div class="stat-item-val">${formatRupee(c.min_cost)} - ${formatRupee(c.max_cost)}</div>
          </div>
          <div>
            <div class="stat-item-lbl">Mean Cost</div>
            <div class="stat-item-val" style="color: ${palette.color};">${formatRupee(c.mean_cost)}</div>
          </div>
        </div>

        <div class="cluster-cuisines-preview">
          <strong style="color: var(--text-main);">Popular:</strong> ${topCuisines || 'Multi-cuisine, Street Food'}
        </div>
      `;

      clusterCardsContainer.appendChild(card);
    });
  }

  // Render Dynamic Cluster Filter Pills for Restaurant Explorer
  function renderClusterFilterPills(model) {
    clusterPillsContainer.innerHTML = '';

    // "All" Button
    const allBtn = document.createElement('button');
    allBtn.className = `filter-pill-btn ${currentClusterFilter === 'ALL' ? 'active' : ''}`;
    allBtn.dataset.cluster = 'ALL';
    allBtn.textContent = 'All Tiers';
    allBtn.addEventListener('click', () => {
      setClusterFilter('ALL');
    });
    clusterPillsContainer.appendChild(allBtn);

    // Button per Cluster
    model.clusters.forEach((c, idx) => {
      const palette = clusterColorPalette[idx] || clusterColorPalette[clusterColorPalette.length - 1];
      const btn = document.createElement('button');
      btn.className = `filter-pill-btn ${currentClusterFilter === String(c.cluster_id) ? 'active' : ''}`;
      btn.dataset.cluster = String(c.cluster_id);
      btn.innerHTML = `<i class="fa-solid ${palette.icon}"></i> ${palette.name}`;
      btn.addEventListener('click', () => {
        setClusterFilter(String(c.cluster_id));
      });
      clusterPillsContainer.appendChild(btn);
    });
  }

  function setClusterFilter(clusterId) {
    currentClusterFilter = clusterId;
    document.querySelectorAll('#cluster-filter-pills .filter-pill-btn').forEach(btn => {
      if (btn.dataset.cluster === clusterId) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
    renderRestaurantCards();
  }

  // =========================================================================
  // RESTAURANT DIRECTORY RENDERING & FILTERING
  // =========================================================================
  function renderRestaurantCards() {
    let list = [...data.restaurants];

    // Filter by Search Query
    if (currentSearchQuery.trim() !== '') {
      const q = currentSearchQuery.toLowerCase().trim();
      list = list.filter(r => {
        const nameMatch = r.name.toLowerCase().includes(q);
        const cuisineMatch = r.cuisines.some(c => c.toLowerCase().includes(q));
        const collMatch = r.collections.some(c => c.toLowerCase().includes(q));
        return nameMatch || cuisineMatch || collMatch;
      });
    }

    // Filter by Cuisine Dropdown
    if (currentCuisineFilter !== 'ALL') {
      list = list.filter(r => r.cuisines.includes(currentCuisineFilter));
    }

    // Filter by Cluster Pill
    if (currentClusterFilter !== 'ALL') {
      const targetClusterId = parseInt(currentClusterFilter, 10);
      list = list.filter(r => r.clusters[`k${currentK}`] === targetClusterId);
    }

    // Sorting
    if (currentSort === 'price-asc') {
      list.sort((a, b) => a.cost - b.cost);
    } else if (currentSort === 'price-desc') {
      list.sort((a, b) => b.cost - a.cost);
    } else if (currentSort === 'rating-desc') {
      list.sort((a, b) => b.rating - a.rating);
    } else if (currentSort === 'reviews-desc') {
      list.sort((a, b) => b.review_count - a.review_count);
    }

    // Update Counter
    resultsCountText.textContent = `Showing ${list.length} of ${data.total_restaurants} restaurants`;

    // Render Cards
    restaurantsGridContainer.innerHTML = '';

    if (list.length === 0) {
      restaurantsGridContainer.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 60px 20px; color: var(--text-dim);">
          <i class="fa-solid fa-utensils" style="font-size: 2.5rem; margin-bottom: 12px; opacity: 0.4;"></i>
          <h3 style="font-size: 1.2rem; color: var(--text-main); margin-bottom: 6px;">No restaurants match your filters</h3>
          <p style="font-size: 0.9rem;">Try clearing the search query or changing cuisine/cluster selection.</p>
        </div>
      `;
      return;
    }

    list.forEach(r => {
      const clusterId = r.clusters[`k${currentK}`];
      const palette = clusterColorPalette[clusterId] || clusterColorPalette[0];

      const card = document.createElement('div');
      card.className = 'restaurant-card';

      // Cuisines Badges
      const cuisineBadgesHtml = r.cuisines.slice(0, 3).map(c => `<span class="cuisine-badge">${c}</span>`).join('');

      card.innerHTML = `
        <div>
          <div class="rest-card-header">
            <h3 class="rest-name">${r.name}</h3>
            <span class="cluster-tag" style="background: ${palette.bg}; color: ${palette.color}; border: 1px solid ${palette.border};">
              <i class="fa-solid ${palette.icon}"></i> ${palette.name}
            </span>
          </div>

          <div class="rest-meta-row">
            <div class="cost-badge">${formatRupee(r.cost)} <small>for two</small></div>
            <div class="rating-pill">
              <i class="fa-solid fa-star"></i> ${r.rating.toFixed(1)}
            </div>
            <span class="reviews-meta">${r.review_count} reviews</span>
          </div>

          <div class="cuisines-list">
            ${cuisineBadgesHtml}
          </div>

          <p class="review-snippet">"${r.sample_review}"</p>
        </div>

        <div class="rest-card-footer">
          <div class="timing-info" title="${r.timings}">
            <i class="fa-regular fa-clock"></i> ${r.timings}
          </div>
          <a href="${r.link}" target="_blank" rel="noopener noreferrer" class="zomato-link-btn">
            View Listing <i class="fa-solid fa-arrow-up-right-from-square"></i>
          </a>
        </div>
      `;

      restaurantsGridContainer.appendChild(card);
    });
  }

  // =========================================================================
  // RESTAURANT CLUSTER PREDICTOR
  // =========================================================================
  function runPredictor() {
    const cost = parseFloat(predCostInput.value);
    const restName = predNameInput.value.trim() || 'New Restaurant';

    if (isNaN(cost) || cost <= 0) {
      alert('Please enter a valid cost amount (e.g. ₹800).');
      return;
    }

    const model = data.cluster_models[currentK];
    let bestCluster = 0;
    let minDistance = Infinity;

    model.clusters.forEach(c => {
      const dist = Math.abs(cost - c.mean_cost);
      if (dist < minDistance) {
        minDistance = dist;
        bestCluster = c.cluster_id;
      }
    });

    const palette = clusterColorPalette[bestCluster] || clusterColorPalette[0];
    const clusterObj = model.clusters[bestCluster];

    predBadge.className = `result-cluster-badge`;
    predBadge.style.background = palette.bg;
    predBadge.style.color = palette.color;
    predBadge.style.border = `1px solid ${palette.border}`;
    predBadge.innerHTML = `<i class="fa-solid ${palette.icon}"></i> ${palette.name} Tier`;

    predCostDisplay.textContent = formatRupee(cost);

    let advice = '';
    if (bestCluster === 0) {
      advice = `Matches the <strong>Budget Dining segment</strong> (Centroid ~${formatRupee(clusterObj.mean_cost)}). Recommended for high-volume quick service, student pocket-friendly menus, and value-combo marketing.`;
    } else if (bestCluster === 1) {
      advice = `Matches the <strong>Mid-Range Dining segment</strong> (Centroid ~${formatRupee(clusterObj.mean_cost)}). Recommended for family dining, corporate weekend buffets, and multi-cuisine casual experiences.`;
    } else {
      advice = `Matches the <strong>Premium & Luxury tier</strong> (Centroid ~${formatRupee(clusterObj.mean_cost)}). Recommended for Zomato Gold table bookings, rooftop cocktail lounges, and curated chef-table experiences.`;
    }

    predRecommendation.innerHTML = `<strong>${restName}</strong> (${formatRupee(cost)}): ${advice}`;

    // Confetti effect
    if (window.confetti) {
      window.confetti({
        particleCount: 50,
        spread: 60,
        origin: { y: 0.8 },
        colors: [palette.color, '#e23744', '#ffffff']
      });
    }
  }

  // =========================================================================
  // EVENT LISTENERS
  // =========================================================================
  function setupEventListeners() {
    // Slider Change
    kSlider.addEventListener('input', (e) => {
      updateClusteringUI(e.target.value);
    });

    // Reset Button
    resetBtn.addEventListener('click', () => {
      kSlider.value = 3;
      updateClusteringUI(3);
    });

    // Search Input
    searchInput.addEventListener('input', (e) => {
      currentSearchQuery = e.target.value;
      renderRestaurantCards();
    });

    // Cuisine Filter
    cuisineFilter.addEventListener('change', (e) => {
      currentCuisineFilter = e.target.value;
      renderRestaurantCards();
    });

    // Sort Select
    sortSelect.addEventListener('change', (e) => {
      currentSort = e.target.value;
      renderRestaurantCards();
    });

    // Predictor Button
    runPredictionBtn.addEventListener('click', runPredictor);
    predCostInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') runPredictor();
    });

    // Smooth Scroll for Nav Links
    document.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', function () {
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        this.classList.add('active');
      });
    });
  }

  // Run on DOM Ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
