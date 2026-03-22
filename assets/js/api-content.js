// ================= CONFIG =================
const API_BASE = 'http://localhost:8000/api';
const BASE_URL = 'http://localhost:8000';


// ================= IMAGE URL FIX =================
function normalizeMediaUrl(url) {
  if (!url) return '';

  const normalizedUrl = String(url).replace('/uploads/annoucements/', '/uploads/announcements/');

  // If already full URL
  if (normalizedUrl.startsWith('http://') || normalizedUrl.startsWith('https://')) {
    return normalizedUrl;
  }

  // Legacy path (old upload format)
  if (normalizedUrl.startsWith('/content/')) {
    return BASE_URL + '/uploads' + normalizedUrl;
  }

  if (normalizedUrl.startsWith('content/')) {
    return `${BASE_URL}/uploads/${normalizedUrl}`;
  }

  // If starts with /
  if (normalizedUrl.startsWith('/')) {
    return BASE_URL + normalizedUrl;
  }

  // If stored as uploads/content without leading slash
  if (normalizedUrl.startsWith('uploads/')) {
    return `${BASE_URL}/${normalizedUrl}`;
  }

  // If stored like WriteReadData/image.jpg
  if (normalizedUrl.startsWith('WriteReadData/')) {
    return `${BASE_URL}/${normalizedUrl}`;
  }

  // If stored as content/old-style path without leading slash
  if (normalizedUrl.startsWith('content/')) {
    return `${BASE_URL}/uploads/${normalizedUrl}`;
  }

  // fallback (just filename)
  return `${BASE_URL}/WriteReadData/${url}`;
}


// ================= FETCH PAGE CONTENT =================
async function getPageContent(page) {
  try {
    const res = await fetch(`${API_BASE}/content/${page}/display`);
    if (!res.ok) throw new Error(`Failed to load content for ${page}`);
    return await res.json();
  } catch (err) {
    console.error(err);
    return { title: '', description: '', banner_image: '' };
  }
}


// ================= FETCH ALL PAGE SECTIONS =================
async function getPageSections(page) {
  try {
    const res = await fetch(`${API_BASE}/content/${page}`);
    if (!res.ok) throw new Error(`Failed to load page sections for ${page}`);
    return await res.json();
  } catch (err) {
    console.error(err);
    return [];
  }
}

// ================= RENDER HOME PAGE SECTIONS =================
async function renderHomePageSections(page, areaId) {
  const sections = await getPageSections(page);
  const area = document.getElementById(areaId);
  if (!area) return;

  if (!sections.length) {
    area.innerHTML = '';
    return;
  }

  const visibleSections = sections
    .filter(s => s.active)
    .sort((a, b) => (a.order || 0) - (b.order || 0));

  area.innerHTML = visibleSections.map((section, idx) => {
    const delay = (idx * 0.15).toFixed(2);
    return `
      <section class="home-section" style="animation-delay:${delay}s">
        <div class="row align-items-center mb-4">
          <div class="col-md-6">
            <h2>${section.title || ''}</h2>
            <p>${section.description || ''}</p>
            ${section.pdf_file ? `<p><a href="${normalizeMediaUrl(section.pdf_file)}" target="_blank" class="btn btn-outline-primary">Download PDF</a></p>` : ''}
          </div>
          <div class="col-md-6">
            ${section.banner_image ? `<img src="${normalizeMediaUrl(section.banner_image)}" class="img-fluid rounded" alt="${section.title || 'Section image'}" />` : ''}
          </div>
        </div>
      </section>
    `;
  }).join('');
}

// ================= RENDER PAGE CONTENT =================
async function renderPageContent(page, areaId) {
  const data = await getPageContent(page);
  const area = document.getElementById(areaId);
  if (!area) return;

  area.innerHTML = `
    <div class="row">
      <div class="col-12">
        <h2>${data.title || page}</h2>
        <p>${data.description || 'Content is not yet available. Please use CMS to add.'}</p>
      </div>

      ${
        data.banner_image
          ? `<div class="col-12">
               <img src="${normalizeMediaUrl(data.banner_image)}" 
                    alt="${data.title}" 
                    class="img-fluid"/>
             </div>`
          : ''
      }
    </div>
  `;
}

// ================= NEWS FLASH & NOTIFICATION =================
async function getAnnouncementsFeed() {
  try {
    const res = await fetch(`${API_BASE}/announcements/feed`);
    if (!res.ok) throw new Error('Failed to load announcements feed');
    const data = await res.json();
    return {
      ticker: Array.isArray(data.ticker) ? data.ticker : [],
      whats_new: Array.isArray(data.whats_new) ? data.whats_new : [],
      notification: Array.isArray(data.notification) ? data.notification : [],
      view_all_url: data.view_all_url || '#'
    };
  } catch (err) {
    console.error(err);
    return { ticker: [], whats_new: [], notification: [], view_all_url: '#' };
  }
}

function ensureAnnouncementsStyles() {
  if (document.getElementById('dynamic-announcements-styles')) return;

  const style = document.createElement('style');
  style.id = 'dynamic-announcements-styles';
  style.innerHTML = `
    .dynamic-ticker-row {
      display: flex;
      align-items: stretch;
      gap: 10px;
      margin-bottom: 16px;
    }
    .dynamic-ticker-heading {
      min-width: 150px;
      background: #0f4c81;
      color: #fff;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 10px;
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }
    .dynamic-ticker-viewport {
      flex: 1;
      overflow: hidden;
      border: 1px solid #d8dee9;
      background: #f8fbff;
      position: relative;
      display: flex;
      align-items: center;
    }
    .dynamic-ticker-track {
      display: flex;
      align-items: center;
      gap: 18px;
      white-space: nowrap;
      width: max-content;
      padding: 10px 14px;
      animation: ticker-scroll 35s linear infinite;
    }
    .dynamic-ticker-viewport:hover .dynamic-ticker-track {
      animation-play-state: paused;
    }
    .dynamic-ticker-item {
      color: #123b66;
      text-decoration: none;
      font-size: 14px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .dynamic-ticker-item:hover {
      color: #c0392b;
      text-decoration: underline;
    }
    .dynamic-new-badge {
      background: #d7263d;
      color: #fff;
      font-size: 10px;
      font-weight: 700;
      padding: 1px 6px;
      border-radius: 10px;
      text-transform: uppercase;
    }
    .dynamic-pdf-icon {
      color: #b71c1c;
      font-size: 14px;
    }
    .dynamic-file-size {
      color: #5f6c7b;
      font-size: 12px;
    }
    .dynamic-ticker-view-all {
      min-width: 92px;
      background: #0f4c81;
      color: #fff;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 10px;
      font-weight: 600;
      text-decoration: none;
    }
    .dynamic-ticker-view-all:hover {
      background: #0a3458;
      color: #fff;
      text-decoration: none;
    }
    .dynamic-news-wrapper {
      border: 1px solid #d7deea;
      border-radius: 4px;
      overflow: hidden;
      background: #fff;
    }
    .dynamic-news-tabs {
      display: flex;
      border-bottom: 1px solid #d7deea;
    }
    .dynamic-news-tabs button {
      flex: 1;
      border: 0;
      background: #eef3fb;
      padding: 10px;
      font-weight: 700;
      color: #0f3f6b;
      cursor: pointer;
    }
    .dynamic-news-tabs button.active {
      background: #0f4c81;
      color: #fff;
    }
    .dynamic-news-panel {
      padding: 12px;
      max-height: 280px;
      overflow-y: auto;
    }
    .dynamic-news-list {
      list-style: none;
      margin: 0;
      padding: 0;
    }
    .dynamic-news-item {
      display: flex;
      gap: 8px;
      margin-bottom: 10px;
      line-height: 1.35;
    }
    .dynamic-news-bullet {
      color: #0f4c81;
      font-size: 16px;
      line-height: 1;
      margin-top: 2px;
    }
    .dynamic-news-link {
      color: #193a63;
      text-decoration: none;
    }
    .dynamic-news-link:hover {
      color: #c0392b;
      text-decoration: underline;
    }
    @keyframes ticker-scroll {
      0% { transform: translateX(0); }
      100% { transform: translateX(-50%); }
    }
    @media (max-width: 767px) {
      .dynamic-ticker-row {
        flex-direction: column;
      }
      .dynamic-ticker-heading,
      .dynamic-ticker-view-all {
        min-width: auto;
        width: 100%;
      }
    }
  `;

  document.head.appendChild(style);
}

function escapeHtml(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function isPdfItem(item) {
  const url = (item.pdf_url || item.link || '').toLowerCase();
  return url.includes('.pdf');
}

function resolveAnnouncementLink(rawLink) {
  const link = String(rawLink || '').trim();
  if (!link || link === '#') return '#';
  if (link.startsWith('javascript:')) return '#';
  if (link.startsWith('/')) return `${BASE_URL}${link}`;
  if (link.startsWith('uploads/')) return `${BASE_URL}/${link}`;
  return link;
}

function renderAnnouncementItem(item) {
  const title = escapeHtml(item.title || item.message || 'Untitled');
  const link = resolveAnnouncementLink(item.link || item.pdf_url || '#');
  const newBadge = item.is_new ? '<span class="dynamic-new-badge">NEW</span>' : '';
  const pdfMeta = isPdfItem(item)
    ? `<i class="fas fa-file-pdf dynamic-pdf-icon" aria-hidden="true"></i><span class="dynamic-file-size">${escapeHtml(item.file_size || '')}</span>`
    : '';

  return `
    <a class="dynamic-ticker-item" href="${escapeHtml(link)}" target="_blank" rel="noopener noreferrer" title="${title}">
      <span>${title}</span>
      ${newBadge}
      ${pdfMeta}
    </a>
  `;
}

async function renderNewsTicker(areaId) {
  const area = document.getElementById(areaId);
  if (!area) return;

  const feed = await getAnnouncementsFeed();
  const tickerContainer = area.querySelector('#ticker-items');
  
  if (!tickerContainer) return;
  
  if (!feed.ticker || feed.ticker.length === 0) {
    tickerContainer.innerHTML = '<div class="ticker-item">No updates available right now.</div>';
    return;
  }

  const createItemHTML = (item) => {
    const title = escapeHtml(item.title || 'Untitled');
    const link = resolveAnnouncementLink(item.link || item.pdf_url || '#');
    const newBadge = item.is_new ? '<span class="ticker-badge-new">NEW</span>' : '';
    const pdfIcon = isPdfItem(item) ? '<i class="fas fa-file-pdf ticker-pdf-icon"></i>' : '';
    const fileSize = item.file_size ? `<span class="ticker-filesize">${escapeHtml(item.file_size)}</span>` : '';
    
    return `
      <div class="ticker-item">
        <a href="${escapeHtml(link)}" target="_blank" rel="noopener noreferrer">${title}</a>
        ${newBadge}
        ${pdfIcon}
        ${fileSize}
      </div>
    `;
  };

  // Create items and duplicate for seamless scrolling
  const singleLoop = feed.ticker.map(createItemHTML).join('');
  const tickerHTML = singleLoop + singleLoop; // Duplicate for continuous scroll effect

  tickerContainer.innerHTML = tickerHTML;
}

async function renderWhatsNewSection(areaId) {
  const area = document.getElementById(areaId);
  if (!area) return;

  const feed = await getAnnouncementsFeed();
  const itemsContainer = area.querySelector('#whats-new-items');
  
  if (!itemsContainer) return;

  const whatsNewItems = (feed.whats_new && feed.whats_new.length) ? feed.whats_new : [];
  
  if (whatsNewItems.length === 0) {
    itemsContainer.innerHTML = '<p class="text-muted">No announcements at this time.</p>';
    return;
  }

  const itemsHTML = whatsNewItems.map(item => {
    const title = escapeHtml(item.title || 'Untitled');
    const link = resolveAnnouncementLink(item.link || item.pdf_url || '#');
    const newBadge = item.is_new ? '<span class="whats-new-badge-new">NEW</span>' : '';
    const pdfIcon = isPdfItem(item) ? '<i class="fas fa-file-pdf whats-new-pdf-icon"></i>' : '';
    const fileSize = item.file_size ? `<span class="whats-new-filesize">(${escapeHtml(item.file_size)})</span>` : '';
    
    return `
      <li class="whats-new-item">
        <a href="${escapeHtml(link)}" target="_blank" rel="noopener noreferrer" class="whats-new-title">${title}</a>
        <span class="whats-new-meta">
          ${newBadge}
          ${pdfIcon}
          ${fileSize}
        </span>
      </li>
    `;
  }).join('');

  itemsContainer.innerHTML = `<ul>${itemsHTML}</ul>`;
}

function renderNewsListItem(item) {
  const title = escapeHtml(item.title || item.message || 'Untitled');
  const link = resolveAnnouncementLink(item.link || item.pdf_url || '#');
  const newBadge = item.is_new ? '<span class="dynamic-new-badge">NEW</span>' : '';
  const pdfMeta = isPdfItem(item)
    ? ` <i class="fas fa-file-pdf dynamic-pdf-icon" aria-hidden="true"></i> <span class="dynamic-file-size">${escapeHtml(item.file_size || '')}</span>`
    : '';

  return `
    <li class="dynamic-news-item">
      <span class="dynamic-news-bullet">•</span>
      <div>
        <a class="dynamic-news-link" href="${escapeHtml(link)}" target="_blank" rel="noopener noreferrer">${title}</a>
        ${newBadge}
        ${pdfMeta}
      </div>
    </li>
  `;
}

async function renderNewsFlashNotification(areaId) {
  ensureAnnouncementsStyles();
  const area = document.getElementById(areaId);
  if (!area) return;

  const feed = await getAnnouncementsFeed();
  if (!feed.whats_new.length && !feed.notification.length) {
    area.innerHTML = '<p>No news/update found.</p>';
    return;
  }

  const whatsNewItems = feed.whats_new.length ? feed.whats_new : feed.notification;
  const notificationItems = feed.notification.length ? feed.notification : feed.whats_new;

  area.innerHTML = `
    <div class="dynamic-news-wrapper">
      <nav class="dynamic-news-tabs" aria-label="Updates tabs">
        <button type="button" class="active" data-tab="whats-new">What's New</button>
        <button type="button" data-tab="notification">Notification</button>
      </nav>
      <div id="whats-new" class="dynamic-news-panel">
        <ul class="dynamic-news-list">
          ${whatsNewItems.map(renderNewsListItem).join('')}
        </ul>
      </div>
      <div id="notification" class="dynamic-news-panel" style="display:none;">
        <ul class="dynamic-news-list">
          ${notificationItems.map(renderNewsListItem).join('')}
        </ul>
      </div>
    </div>
  `;

  area.querySelectorAll('.dynamic-news-tabs button').forEach(btn => {
    btn.addEventListener('click', () => {
      area.querySelectorAll('.dynamic-news-tabs button').forEach(button => button.classList.remove('active'));
      area.querySelectorAll('.dynamic-news-panel').forEach(panel => {
        panel.style.display = 'none';
      });

      btn.classList.add('active');
      const targetTab = btn.dataset.tab;
      const panel = area.querySelector(targetTab === 'whats-new' ? '#whats-new' : '#notification');
      if (panel) {
        panel.style.display = 'block';
      }
    });
  });
}


// ================= STAFF =================
async function renderStaffCards(areaId) {
  const area = document.getElementById(areaId);
  if (!area) return;

  try {
    const res = await fetch(`${API_BASE}/staff`);
    if (!res.ok) throw new Error('Staff fetch failed');

    const staff = await res.json();

    if (!staff.length) {
      area.innerHTML = '<p>No staff data available right now.</p>';
      return;
    }

    area.innerHTML = staff.map(item => `
      <div class="staff-card">
        <img src="${normalizeMediaUrl(item.photo_url) || 'images/default-staff.png'}"
             alt="${escapeHtml(item.name || 'Staff')}"
             class="staff-img">
        <h5>${escapeHtml(item.name || '')}</h5>
        <div class="staff-role">${escapeHtml(item.designation || item.role || '')}</div>
        <p class="staff-department">${escapeHtml(item.department || '')}</p>
        ${item.contact ? `<div class="staff-contact">${escapeHtml(item.contact)}</div>` : ''}
      </div>
    `).join('');

  } catch (err) {
    console.error(err);
    area.innerHTML = '<p>Could not load staff data.</p>';
  }
}


// ================= ACADEMIC CALENDAR =================
async function renderAcademicCalendar(areaId) {
  const area = document.getElementById(areaId);
  if (!area) return;

  try {
    const res = await fetch(`${API_BASE}/calendar`);
    if (!res.ok) throw new Error('Calendar fetch failed');
    const rows = await res.json();

    if (!rows.length) {
      area.innerHTML = '<tr><td colspan="3">No academic calendar entries available.</td></tr>';
      return;
    }

    area.innerHTML = rows.map(row => `
      <tr>
        <td>${escapeHtml(row.month || '')}</td>
        <td>${escapeHtml(row.activity || '')}</td>
        <td>${escapeHtml(row.details || '')}</td>
      </tr>
    `).join('');
  } catch (err) {
    console.error(err);
    area.innerHTML = '<tr><td colspan="3">Could not load academic calendar.</td></tr>';
  }
}


// ================= EVENTS =================
function ensureEventStyles() {
  if (document.getElementById('dynamic-event-styles')) return;

  const style = document.createElement('style');
  style.id = 'dynamic-event-styles';
  style.innerHTML = `
    .gov-hero {
      width: 100%;
      margin-bottom: 22px;
      border-top: 1px solid #d6dfeb;
      border-bottom: 1px solid #d6dfeb;
      background: #ecf2f8;
      position: relative;
    }
    .gov-hero .carousel-item img {
      width: 100%;
      height: min(62vh, 620px);
      min-height: 280px;
      object-fit: cover;
      object-position: center;
      display: block;
    }
    .gov-hero-caption {
      position: absolute;
      left: 18px;
      right: 18px;
      bottom: 18px;
      background: rgba(8, 32, 57, 0.68);
      color: #fff;
      padding: 10px 14px;
      border-left: 4px solid #ff9f1a;
      max-width: 740px;
    }
    .gov-hero-caption h3 {
      margin: 0;
      font-size: 20px;
      font-weight: 700;
      line-height: 1.25;
    }
    .gov-hero-caption p {
      margin: 6px 0 0;
      font-size: 14px;
      line-height: 1.4;
      opacity: 0.95;
    }
    .gov-event-card {
      background: #fff;
      border: 1px solid #d8e0eb;
      border-radius: 4px;
      overflow: hidden;
      height: 100%;
      box-shadow: 0 6px 20px rgba(22, 40, 56, 0.08);
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      cursor: pointer;
    }
    .gov-event-card:hover {
      transform: translateY(-6px);
      box-shadow: 0 12px 24px rgba(22, 40, 56, 0.15);
    }
    .gov-event-image {
      width: 100%;
      height: 230px;
      object-fit: cover;
      background: #f3f5f8;
    }
    .gov-event-body {
      padding: 14px;
    }
    .gov-event-title {
      font-size: 20px;
      line-height: 1.35;
      margin-bottom: 8px;
      color: #1a2f4a;
      font-weight: 700;
    }
    .gov-event-summary {
      color: #334a61;
      font-size: 16px;
      line-height: 1.45;
      display: -webkit-box;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 3;
      overflow: hidden;
      min-height: 4.2em;
    }
    .gov-events-actions {
      display: flex;
      justify-content: center;
      margin-top: 14px;
    }
    .gov-view-all-btn,
    .gov-load-more-btn {
      background: #0d5f96;
      color: #fff;
      border: 0;
      text-decoration: none;
      padding: 10px 18px;
      font-weight: 600;
      border-radius: 4px;
      transition: background 0.22s ease;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }
    .gov-view-all-btn:hover,
    .gov-load-more-btn:hover {
      background: #084a78;
      color: #fff;
      text-decoration: none;
    }
    .gov-home-events-wrap {
      border: 1px solid #d8e0eb;
      border-radius: 6px;
      padding: 10px;
      background: #f7fbff;
      overflow: hidden;
    }
    .gov-home-events-viewport {
      overflow: hidden;
      position: relative;
    }
    .gov-home-events-track {
      display: flex;
      gap: 16px;
      width: max-content;
      animation: gov-events-scroll 26s linear infinite;
      will-change: transform;
      padding: 2px;
    }
    .gov-home-events-track.is-static {
      width: max-content;
      justify-content: flex-start;
      flex-wrap: nowrap;
      animation: gov-events-marquee 18s linear infinite;
    }
    .gov-home-events-wrap:hover .gov-home-events-track {
      animation-play-state: paused;
    }
    .gov-home-event-item {
      width: min(260px, 72vw);
      flex: 0 0 auto;
    }
    .gov-home-event-item .gov-event-image {
      height: 170px;
    }
    .gov-home-event-item .gov-event-title {
      font-size: 17px;
    }
    .gov-home-event-item .gov-event-summary {
      font-size: 14px;
      min-height: 3.6em;
    }
    @keyframes gov-events-scroll {
      from { transform: translateX(0); }
      to { transform: translateX(-50%); }
    }
    @keyframes gov-events-marquee {
      from { transform: translateX(100%); }
      to { transform: translateX(-100%); }
    }
    .custom-modal {
      opacity: 0;
      transition: opacity 0.25s ease;
    }
    .custom-modal.is-open {
      opacity: 1;
    }
    .modal-content-box {
      transform: scale(0.94);
      opacity: 0;
      transition: transform 0.24s ease, opacity 0.24s ease;
    }
    .custom-modal.is-open .modal-content-box {
      transform: scale(1);
      opacity: 1;
    }
    @media (max-width: 768px) {
      .gov-hero .carousel-item img {
        height: 42vh;
      }
      .gov-hero-caption {
        left: 10px;
        right: 10px;
        bottom: 10px;
      }
      .gov-hero-caption h3 {
        font-size: 16px;
      }
      .gov-event-image {
        height: 210px;
      }
      .gov-home-event-item {
        width: min(240px, 84vw);
      }
    }
  `;

  document.head.appendChild(style);
}

async function renderHomeHeroSlider(areaId) {
  ensureEventStyles();
  const area = document.getElementById(areaId);
  if (!area) return;

  try {
    const res = await fetch(`${API_BASE}/events?category=home_slider`);
    if (!res.ok) throw new Error('Home slider fetch failed');

    let items = await res.json();
    if (!items.length) {
      const fallbackRes = await fetch(`${API_BASE}/events?category=achievement,event`);
      if (fallbackRes.ok) {
        items = (await fallbackRes.json()).slice(0, 5);
      }
    }

    if (!items.length) {
      area.innerHTML = '';
      return;
    }

    const sliderId = 'homeHeroCarousel';

    area.innerHTML = `
      <section class="gov-hero">
        <div id="${sliderId}" class="carousel slide" data-bs-ride="carousel" data-bs-interval="4500">
          <div class="carousel-indicators">
            ${items.map((_, idx) => `<button type="button" data-bs-target="#${sliderId}" data-bs-slide-to="${idx}" ${idx === 0 ? 'class="active" aria-current="true"' : ''} aria-label="Slide ${idx + 1}"></button>`).join('')}
          </div>
          <div class="carousel-inner">
            ${items.map((item, idx) => `
              <div class="carousel-item ${idx === 0 ? 'active' : ''}">
                <img src="${escapeHtml(normalizeMediaUrl(item.image_url))}" alt="${escapeHtml(item.title || 'Home slide')}" loading="lazy">
                <div class="gov-hero-caption">
                  <h3>${escapeHtml(item.title || '')}</h3>
                  ${item.short_description ? `<p>${escapeHtml(item.short_description)}</p>` : ''}
                </div>
              </div>
            `).join('')}
          </div>
          <button class="carousel-control-prev" type="button" data-bs-target="#${sliderId}" data-bs-slide="prev">
            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Previous</span>
          </button>
          <button class="carousel-control-next" type="button" data-bs-target="#${sliderId}" data-bs-slide="next">
            <span class="carousel-control-next-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Next</span>
          </button>
        </div>
      </section>
    `;
  } catch (err) {
    console.error(err);
    area.innerHTML = '';
  }
}

function buildEventCardMarkup(ev, cardClass = '', cardId = '') {
  const idAttr = cardId ? ` id="${cardId}"` : '';
  return `
    <article${idAttr} class="gov-event-card ${cardClass}">
      <img class="gov-event-image" src="${escapeHtml(normalizeMediaUrl(ev.image_url) || 'images/default-banner.jpg')}" alt="${escapeHtml(ev.title || 'Event image')}" loading="lazy">
      <div class="gov-event-body">
        <h4 class="gov-event-title">${escapeHtml(ev.title || 'Untitled')}</h4>
        <p class="gov-event-summary">${escapeHtml(ev.short_description || ev.full_description || '')}</p>
      </div>
    </article>
  `;
}

async function renderEventList(areaId, options = {}) {
  ensureEventStyles();
  const area = document.getElementById(areaId);
  if (!area) return;

  const mode = options.mode === 'home' ? 'home' : 'full';
  const pageSize = Number(options.pageSize) > 0 ? Number(options.pageSize) : 8;
  const homeLimit = Number(options.limit) > 0 ? Number(options.limit) : 6;
  const viewAllUrl = options.viewAllUrl || 'achievments and events.html';

  try {
    const res = await fetch(`${API_BASE}/events?category=achievement,event`);
    if (!res.ok) throw new Error('Events fetch failed');

    const payload = await res.json();
    const events = Array.isArray(payload) ? payload : [];

    if (!events.length) {
      area.innerHTML = '<div class="col-12"><p>No achievements or events available right now.</p></div>';
      return;
    }

    if (mode === 'home') {
      const latest = events.slice(0, homeLimit);
      const shouldLoop = latest.length >= 5;
      const renderItems = shouldLoop ? latest.concat(latest) : latest;

      area.innerHTML = `
        <div class="gov-home-events-wrap">
          <div class="gov-home-events-viewport">
            <div class="gov-home-events-track ${shouldLoop ? '' : 'is-static'}" id="home-events-track">
              ${renderItems.map((ev, idx) => `<div class="gov-home-event-item" data-home-idx="${idx % latest.length}">${buildEventCardMarkup(ev)}</div>`).join('')}
            </div>
          </div>
          <div class="gov-events-actions">
            <a class="gov-view-all-btn" href="${escapeHtml(viewAllUrl)}">View All</a>
          </div>
        </div>
      `;

      area.querySelectorAll('.gov-home-event-item').forEach(node => {
        const idx = Number(node.getAttribute('data-home-idx') || 0);
        const card = node.querySelector('.gov-event-card');
        const item = latest[idx];
        if (card) {
          card.addEventListener('click', () => showEventModal(item));
        }
      });
      return;
    }

    let visibleCount = Math.min(pageSize, events.length);

    const renderGrid = () => {
      const visibleItems = events.slice(0, visibleCount);
      area.innerHTML = visibleItems.map(ev => `
        <div class="col-lg-3 col-md-6 mb-4">
          ${buildEventCardMarkup(ev, '', `event-item-${ev.id}`)}
        </div>
      `).join('');

      visibleItems.forEach(ev => {
        const card = document.getElementById(`event-item-${ev.id}`);
        if (card) {
          card.addEventListener('click', () => showEventModal(ev));
        }
      });

      const wrapper = area.parentElement;
      if (!wrapper) return;
      let actions = wrapper.querySelector('.gov-events-actions');

      if (visibleCount < events.length) {
        if (!actions) {
          actions = document.createElement('div');
          actions.className = 'gov-events-actions';
          wrapper.appendChild(actions);
        }
        actions.innerHTML = '<button type="button" class="gov-load-more-btn">Load More</button>';
        const btn = actions.querySelector('.gov-load-more-btn');
        if (btn) {
          btn.addEventListener('click', () => {
            visibleCount = Math.min(visibleCount + pageSize, events.length);
            renderGrid();
          });
        }
      } else if (actions) {
        actions.remove();
      }
    };

    renderGrid();

  } catch (err) {
    console.error(err);
    area.innerHTML = '<p>Could not load events.</p>';
  }
}


// ================= EVENT MODAL =================
function showEventModal(event) {
  ensureEventStyles();
  const modal = document.getElementById('eventModal');
  if (!modal) return;

  const modalTitle = document.getElementById('modalTitle');
  const modalImage = document.getElementById('modalImage');
  const modalDescription = document.getElementById('modalDescription');

  modalTitle.innerText = event.title || 'Untitled';
  modalImage.src = normalizeMediaUrl(event.image_url) || '';
  modalDescription.innerText = event.full_description || event.short_description || '';

  modal.style.display = 'block';
  requestAnimationFrame(() => {
    modal.classList.add('is-open');
  });
  document.body.style.overflow = 'hidden';
}


// ================= CLOSE MODAL =================
function hideEventModal() {
  const modal = document.getElementById('eventModal');
  if (!modal) return;

  modal.classList.remove('is-open');
  setTimeout(() => {
    modal.style.display = 'none';
  }, 220);
  document.body.style.overflow = '';
}