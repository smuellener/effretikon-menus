// App State
let currentMenus = [];
let cardOrder = loadOrder(); // persisted restaurant name order

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
    loadMenus();
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

// --- Order persistence (localStorage) ---

const ORDER_KEY = 'effretikon_card_order';

function loadOrder() {
    try {
        return JSON.parse(localStorage.getItem(ORDER_KEY)) || [];
    } catch { return []; }
}

function saveOrder(names) {
    cardOrder = names;
    localStorage.setItem(ORDER_KEY, JSON.stringify(names));
}

function applyOrder(menus) {
    if (!cardOrder.length) return menus;
    const sorted = [...menus].sort((a, b) => {
        const ia = cardOrder.indexOf(a.restaurant);
        const ib = cardOrder.indexOf(b.restaurant);
        if (ia === -1 && ib === -1) return 0;
        if (ia === -1) return 1;
        if (ib === -1) return -1;
        return ia - ib;
    });
    return sorted;
}

// --- Display ---

function displayMenus(menus) {
    restaurantContainer.innerHTML = '';
    
    if (!menus || menus.length === 0) {
        showEmptyState();
        return;
    }
    
    hideEmptyState();
    
    const withMenus = applyOrder(menus.filter(m => m.menus && m.menus.length > 0));
    const withoutMenus = menus.filter(m => !m.menus || m.menus.length === 0);

    withMenus.forEach(menu => {
        restaurantContainer.appendChild(createRestaurantCard(menu, true));
    });

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
        withoutMenus.forEach(menu => grid.appendChild(createRestaurantCard(menu, false)));
    }

    initDragAndDrop();
}

// --- Drag and Drop ---

let dragSrc = null;

function initDragAndDrop() {
    const cards = restaurantContainer.querySelectorAll('.restaurant-card[draggable="true"]');
    cards.forEach(card => {
        card.addEventListener('dragstart', onDragStart);
        card.addEventListener('dragover',  onDragOver);
        card.addEventListener('dragleave', onDragLeave);
        card.addEventListener('drop',      onDrop);
        card.addEventListener('dragend',   onDragEnd);
    });
}

function onDragStart(e) {
    dragSrc = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', this.dataset.restaurant);
}

function onDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    if (this !== dragSrc) this.classList.add('drag-over');
}

function onDragLeave() {
    this.classList.remove('drag-over');
}

function onDrop(e) {
    e.preventDefault();
    this.classList.remove('drag-over');
    if (!dragSrc || dragSrc === this) return;

    // Swap DOM positions
    const parent = this.parentNode;
    const allCards = [...parent.querySelectorAll('.restaurant-card[draggable="true"]')];
    const srcIdx  = allCards.indexOf(dragSrc);
    const destIdx = allCards.indexOf(this);

    if (srcIdx < destIdx) {
        parent.insertBefore(dragSrc, this.nextSibling);
    } else {
        parent.insertBefore(dragSrc, this);
    }

    // Persist new order
    const newOrder = [...parent.querySelectorAll('.restaurant-card[draggable="true"]')]
        .map(c => c.dataset.restaurant);
    saveOrder(newOrder);
}

function onDragEnd() {
    this.classList.remove('dragging');
    restaurantContainer.querySelectorAll('.restaurant-card').forEach(c => {
        c.classList.remove('drag-over');
    });
    dragSrc = null;
}

// Create Restaurant Card
function createRestaurantCard(menuData, draggable) {
    const card = document.createElement('div');
    card.className = 'restaurant-card';
    if (draggable) {
        card.setAttribute('draggable', 'true');
        card.dataset.restaurant = menuData.restaurant;
    }
    
    const icon = getRestaurantIcon(menuData.restaurant);
    const hasMenus = menuData.menus && menuData.menus.length > 0;
    const statusClass = hasMenus ? 'available' : 
                       menuData.status?.includes('nicht erreichbar') ? 'error' : 
                       'unavailable';
    
    const dragHandle = draggable
        ? `<span class="drag-handle" title="Ziehen zum Sortieren">⠿</span>`
        : '';

    card.innerHTML = `
        <div class="restaurant-header">
            <div class="restaurant-title-row">
                ${dragHandle}
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

