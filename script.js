// API endpoint
const API_URL = 'http://localhost:8000/api/news';

// Yangiliklarni yuklash
async function loadNews() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error('Yangiliklarni yuklashda xatolik');
        const news = await response.json();
        renderNews(news);
    } catch (error) {
        console.error('Error loading news:', error);
        showErrorMessage();
    }
}

// Yangiliklarni render qilish
function renderNews(news) {
    const newsGrid = document.getElementById('newsGrid');
    
    if (!news || news.length === 0) {
        newsGrid.innerHTML = `
            <div class="loading">
                <p style="color: #707080; text-align: center; padding: 2rem;">
                    Hozircha yangiliklar mavjud emas
                </p>
            </div>
        `;
        return;
    }

    newsGrid.innerHTML = news.map(item => `
        <div class="news-card" data-id="${item.id}">
            <div class="news-card-image">
                <img src="${item.image || 'https://via.placeholder.com/800x450/1a1a2e/ffffff?text=Xabar+TV'}" 
                     alt="${item.title || 'Yangilik'}" 
                     loading="lazy"
                     onerror="this.src='https://via.placeholder.com/800x450/1a1a2e/ffffff?text=Xabar+TV'">
            </div>
            <div class="news-card-content">
                <span class="news-card-badge">📰 Yangilik</span>
                <h3 class="news-card-title">${escapeHtml(item.title || 'Sarlavhasiz')}</h3>
                <p class="news-card-text">${escapeHtml(item.text || '')}</p>
                <div class="news-card-footer">
                    <span class="news-card-date">${formatDate(item.date)}</span>
                    ${item.telegram_url ? `
                        <a href="${escapeHtml(item.telegram_url)}" target="_blank" class="news-card-telegram">
                            📨 Telegramda ko'rish
                        </a>
                    ` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

// XTML special characters ni escape qilish
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Sanani formatlash
function formatDate(dateString) {
    if (!dateString) return 'Sana ko\'rsatilmagan';
    try {
        const date = new Date(dateString);
        const now = new Date();
        const diff = Math.floor((now - date) / 1000);
        
        if (diff < 60) return 'Hozirgina';
        if (diff < 3600) return `${Math.floor(diff / 60)} daqiqa oldin`;
        if (diff < 86400) return `${Math.floor(diff / 3600)} soat oldin`;
        if (diff < 604800) return `${Math.floor(diff / 86400)} kun oldin`;
        
        return date.toLocaleDateString('uz-UZ', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch {
        return dateString;
    }
}

// Xatolik xabarini ko'rsatish
function showErrorMessage() {
    const newsGrid = document.getElementById('newsGrid');
    newsGrid.innerHTML = `
        <div class="loading">
            <div style="text-align: center; padding: 2rem;">
                <p style="color: #ff6b6b; font-size: 1.2rem; margin-bottom: 1rem;">⚠️ Xatolik yuz berdi</p>
                <p style="color: #707080;">Yangiliklarni yuklashda muammo yuz berdi. Iltimos, qayta urinib ko'ring.</p>
                <button onclick="loadNews()" style="margin-top: 1rem; padding: 0.75rem 2rem; background: linear-gradient(135deg, #ff6b6b, #ffd93d); border: none; border-radius: 50px; color: #000; font-weight: 700; cursor: pointer; transition: transform 0.3s ease;">
                    Qayta yuklash
                </button>
            </div>
        </div>
    `;
}

// WebSocket orqali real-time yangilanishlar
let ws = null;

function connectWebSocket() {
    try {
        // WebSocket ulanish (agar backend qo'llab-quvvatlasa)
        const wsUrl = 'ws://localhost:8000/ws';
        ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
            console.log('WebSocket ulandi');
        };
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'new_news') {
                    loadNews(); // Yangi yangilik kelganda qayta yuklash
                }
            } catch (error) {
                console.error('WebSocket xatolik:', error);
            }
        };
        
        ws.onerror = (error) => {
            console.warn('WebSocket xatolik (normal):', error);
        };
        
        ws.onclose = () => {
            console.log('WebSocket uzildi, 5 soniyadan so\'ng qayta ulanadi');
            setTimeout(connectWebSocket, 5000);
        };
    } catch (error) {
        console.warn('WebSocket ulanish xatolik (normal):', error);
    }
}

// Mobile menyu
document.addEventListener('DOMContentLoaded', () => {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navMenu = document.getElementById('navMenu');
    
    mobileMenuBtn.addEventListener('click', () => {
        mobileMenuBtn.classList.toggle('active');
        navMenu.classList.toggle('active');
    });
    
    // Menyu havolalariga bosilganda yopish
    document.querySelectorAll('.nav-menu a').forEach(link => {
        link.addEventListener('click', () => {
            mobileMenuBtn.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });
    
    // Yangiliklarni yuklash
    loadNews();
    
    // Har 60 soniyada yangilash
    setInterval(loadNews, 60000);
    
    // WebSocket ulanish
    connectWebSocket();
});