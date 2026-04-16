// App State
let currentMenus = [];

// DOM Elements
const refreshBtn = document.getElementById('refreshBtn');
const exportBtn = document.getElementById('exportBtn');
const statusBar = document.getElementById('statusBar');
const statusIcon = document.getElementById('statusIcon');
const statusText = document.getElementById('statusText');
const timestamp = document.getElementById('timestamp');
const timestampValue = document.getElementById('timestampValue');
const restaurantContainer = document.getElementById('restaurantContainer');
const loadingSpinner = document.getElementById('loadingSpinner');
const emptyState = document.getElementById('emptyState');

// Restaurant Icons Mapping
const restaurantIcons = {
    'oase': '🌿',
    'villa': '🍕',
    'bellissimo': '🍝',
    'migros': '🛒',
    'default': '🍽️'
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    // Load menus on startup
    loadMenus();
    
    // Event Listeners
    refreshBtn.addEventListener('click', loadMenus);
    exportBtn.addEventListener('click', exportToMarkdown);
});

// Load Menus from API
async function loadMenus() {
    showLoading();
    hideStatus();
    disableButtons();
    
    try {
        const response = await fetch('/api/menus');
        const data = await response.json();
        
        if (data.success) {
            currentMenus = data.menus;
            displayMenus(data.menus);
            updateTimestamp(data.timestamp);
            showStatus('success', '✓', `${data.count} Restaurants geladen`);
        } else {
            throw new Error(data.error || 'Fehler beim Laden');
        }
    } catch (error) {
        console.error('Error loading menus:', error);
        showStatus('error', '✗', `Fehler: ${error.message}`);
        showEmptyState();
    } finally {
        hideLoading();
        enableButtons();
    }
}

// Display Menus
function displayMenus(menus) {
    restaurantContainer.innerHTML = '';
    
    if (!menus || menus.length === 0) {
        showEmptyState();
        return;
    }
    
    hideEmptyState();
    
    const withMenus = menus.filter(m => m.menus && m.menus.length > 0);
    const withoutMenus = menus.filter(m => !m.menus || m.menus.length === 0);

    // Restaurants with menus first
    withMenus.forEach(menu => {
        restaurantContainer.appendChild(createRestaurantCard(menu));
    });

    // Restaurants without menus in a collapsed section at the bottom
    if (withoutMenus.length > 0) {
        const section = document.createElement('details');
        section.className = 'no-menu-section';
        section.innerHTML = `
            <summary class="no-menu-summary">
                <span>🔕 ${withoutMenus.length} Restaurant${withoutMenus.length > 1 ? 's' : ''} ohne aktuelle Online-Menükarte</span>
                <span class="toggle-arrow">▸</span>
            </summary>
            <div class="no-menu-grid" id="noMenuGrid"></div>
        `;
        restaurantContainer.appendChild(section);
        const grid = section.querySelector('#noMenuGrid');
        withoutMenus.forEach(menu => grid.appendChild(createRestaurantCard(menu)));
    }
}

// Create Restaurant Card
function createRestaurantCard(menuData) {
    const card = document.createElement('div');
    card.className = 'restaurant-card';
    
    const icon = getRestaurantIcon(menuData.restaurant);
    const hasMenus = menuData.menus && menuData.menus.length > 0;
    const statusClass = hasMenus ? 'available' : 
                       menuData.status?.includes('nicht erreichbar') ? 'error' : 
                       'unavailable';
    
    card.innerHTML = `
        <div class="restaurant-header">
            <div class="restaurant-title-row">
                <h2 class="restaurant-name">
                    <span class="restaurant-icon">${icon}</span>
                    ${menuData.restaurant}
                </h2>
            </div>
            <span class="status-badge ${statusClass}">${menuData.status || 'Status unbekannt'}</span>
        </div>

        ${hasMenus ? createMenusSection(menuData.menus) : 
          menuData.info ? `<div class="no-menus">${menuData.info}</div>` : 
          '<div class="no-menus">Keine aktuellen Menüs verfügbar</div>'}

        <details class="restaurant-details">
            <summary class="details-toggle">
                <span>ℹ️ Details &amp; Kontakt</span>
                <span class="toggle-arrow">▸</span>
            </summary>
            <div class="details-content">
                <div class="info-row">
                    <span class="info-icon">📍</span>
                    <span class="info-text">${menuData.address || 'Keine Adresse'}</span>
                </div>
                ${menuData.phone ? `
                    <div class="info-row">
                        <span class="info-icon">📞</span>
                        <span class="info-text"><a href="tel:${menuData.phone}">${menuData.phone}</a></span>
                    </div>` : ''}
                ${menuData.price ? `
                    <div class="info-row">
                        <span class="info-icon">💰</span>
                        <span class="info-text">${menuData.price}</span>
                    </div>` : ''}
                ${menuData.website ? `
                    <div class="info-row">
                        <span class="info-icon">🌐</span>
                        <span class="info-text"><a href="${menuData.website}" target="_blank">Website besuchen</a></span>
                    </div>` : ''}
                ${menuData.note ? `
                    <div class="info-row">
                        <span class="info-icon">📝</span>
                        <span class="info-text">${menuData.note}</span>
                    </div>` : ''}
            </div>
        </details>
    `;
    
    return card;
}

// Create Menus Section
function createMenusSection(menus) {
    if (!menus || menus.length === 0) return '';
    
    const menusHtml = menus.map((menu, index) => {
        const priceHtml = menu.price ? `<span class="menu-price">${menu.price}</span>` : '';
        const tagsHtml = (menu.tags && menu.tags.length) 
            ? `<div class="menu-tags">${menu.tags.join(' ')}</div>` : '';
        const detailsHtml = menu.details ? `<div class="menu-details">${menu.details}</div>` : '';
        return `
        <div class="menu-item">
            <div class="menu-item-header">
                <span class="menu-title">${menu.title || `Menü ${index + 1}`}</span>
                ${priceHtml}
            </div>
            <div class="menu-description">${menu.description || 'Keine Details verfügbar'}</div>
            ${detailsHtml}
            ${tagsHtml}
        </div>`;
    }).join('');
    
    return `
        <div class="menus-section">
            <h3 class="menus-title">📋 Heutige Menüs</h3>
            ${menusHtml}
        </div>
    `;
}

// Get Restaurant Icon
function getRestaurantIcon(restaurantName) {
    const name = restaurantName.toLowerCase();
    
    if (name.includes('oase')) return restaurantIcons.oase;
    if (name.includes('villa') || name.includes('barone')) return restaurantIcons.villa;
    if (name.includes('bellissimo')) return restaurantIcons.bellissimo;
    if (name.includes('migros')) return restaurantIcons.migros;
    
    return restaurantIcons.default;
}

// Export to Markdown
async function exportToMarkdown() {
    disableButtons();
    showStatus('info', '⏳', 'Exportiere Menüs...');
    
    try {
        const response = await fetch('/api/export');
        const data = await response.json();
        
        if (data.success) {
            showStatus('success', '✓', `Exportiert nach ${data.filename}`);
        } else {
            throw new Error(data.error || 'Export fehlgeschlagen');
        }
    } catch (error) {
        console.error('Export error:', error);
        showStatus('error', '✗', `Export-Fehler: ${error.message}`);
    } finally {
        enableButtons();
        setTimeout(hideStatus, 3000);
    }
}

// Update Timestamp
function updateTimestamp(isoString) {
    const date = new Date(isoString);
    const formatted = date.toLocaleString('de-CH', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    timestampValue.textContent = formatted;
    timestamp.classList.remove('hidden');
}

// UI Helper Functions
function showLoading() {
    loadingSpinner.classList.remove('hidden');
    restaurantContainer.classList.add('hidden');
    emptyState.classList.add('hidden');
}

function hideLoading() {
    loadingSpinner.classList.add('hidden');
    restaurantContainer.classList.remove('hidden');
}

function showEmptyState() {
    emptyState.classList.remove('hidden');
    restaurantContainer.classList.add('hidden');
}

function hideEmptyState() {
    emptyState.classList.add('hidden');
}

function showStatus(type, icon, text) {
    statusBar.className = `status-bar ${type}`;
    statusIcon.textContent = icon;
    statusText.textContent = text;
    statusBar.classList.remove('hidden');
}

function hideStatus() {
    statusBar.classList.add('hidden');
}

function disableButtons() {
    refreshBtn.disabled = true;
    exportBtn.disabled = true;
}

function enableButtons() {
    refreshBtn.disabled = false;
    exportBtn.disabled = false;
}

// Auto-refresh every 30 minutes (optional)
// setInterval(loadMenus, 30 * 60 * 1000);
