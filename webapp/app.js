/**
 * Sports Scores Web App
 * Vanilla JS SPA — hash-based routing, three view modes, WCAG 2.2 AA
 */

'use strict';

/* ── Constants / Configuration ─────────────────────────────────────────── */

const SPORTS = [
  { key: 'mlb',    name: 'MLB',    fullName: 'Major League Baseball',         sport: 'baseball',   league: 'mlb',                      hasStandings: true,  hasStats: true,  isFootball: false },
  { key: 'nfl',    name: 'NFL',    fullName: 'National Football League',      sport: 'football',   league: 'nfl',                      hasStandings: true,  hasStats: true,  isFootball: true  },
  { key: 'nba',    name: 'NBA',    fullName: 'National Basketball Assoc.',    sport: 'basketball', league: 'nba',                      hasStandings: true,  hasStats: true,  isFootball: false },
  { key: 'nhl',    name: 'NHL',    fullName: 'National Hockey League',        sport: 'hockey',     league: 'nhl',                      hasStandings: true,  hasStats: true,  isFootball: false },
  { key: 'ncaaf',  name: 'NCAAF',  fullName: 'NCAA Football',                 sport: 'football',   league: 'college-football',         hasStandings: true,  hasStats: false, isFootball: true  },
  { key: 'ncaam',  name: 'NCAAM',  fullName: "NCAA Men's Basketball",         sport: 'basketball', league: 'mens-college-basketball',  hasStandings: true,  hasStats: false, isFootball: false },
  { key: 'ncaawb', name: 'NCAAWB', fullName: "NCAA Women's Basketball",       sport: 'basketball', league: 'womens-college-basketball',hasStandings: true,  hasStats: false, isFootball: false },
  { key: 'wnba',   name: 'WNBA',   fullName: "Women's National Basketball",   sport: 'basketball', league: 'wnba',                     hasStandings: true,  hasStats: false, isFootball: false },
  { key: 'ncaah',  name: 'NCAAH',  fullName: "NCAA Men's Hockey",             sport: 'hockey',     league: 'mens-college-hockey',      hasStandings: false, hasStats: false, isFootball: false },
  { key: 'ncaawh', name: 'NCAAWH', fullName: "NCAA Women's Hockey",           sport: 'hockey',     league: 'womens-college-hockey',    hasStandings: false, hasStats: false, isFootball: false },
];

const SOCCER_LEAGUES = [
  { key: 'epl',        name: 'Premier League',   shortName: 'EPL'  },
  { key: 'mls',        name: 'MLS',              shortName: 'MLS'  },
  { key: 'nwsl',       name: 'NWSL',             shortName: 'NWSL' },
  { key: 'laliga',     name: 'La Liga',           shortName: 'ESP'  },
  { key: 'bundesliga', name: 'Bundesliga',        shortName: 'GER'  },
  { key: 'seriea',     name: 'Serie A',           shortName: 'ITA'  },
  { key: 'ligue1',     name: 'Ligue 1',           shortName: 'FRA'  },
  { key: 'ucl',        name: 'Champions League',  shortName: 'UCL'  },
  { key: 'uel',        name: 'Europa League',     shortName: 'UEL'  },
  { key: 'ligamx',     name: 'Liga MX',           shortName: 'MEX'  },
  { key: 'concacaf',   name: 'CONCACAF',          shortName: 'CCL'  },
];

const DEFAULT_SETTINGS = {
  theme: 'system',
  autoRefreshSeconds: 60,
  visibleSports: SPORTS.map(s => s.key),
};

/* ── Application State ──────────────────────────────────────────────────── */

let currentView       = 'home';
let currentSport      = null;
let currentDate       = new Date();
let currentGameView   = 'card';
let currentSection    = 'scores';
let currentGame       = null;
let currentTeam       = null;
let currentSoccerLeague = null;
let currentGolfTour   = 'pga';
let currentFootball   = { seasonType: 2, week: null };
let autoRefreshTimer  = null;
let liveCountdownTimer = null;
let liveCountdownSecs  = 0;
let settings          = loadSettings();

/* ── Settings ───────────────────────────────────────────────────────────── */

function loadSettings() {
  try {
    const raw = localStorage.getItem('sportsScoresSettings');
    if (raw) return Object.assign({}, DEFAULT_SETTINGS, JSON.parse(raw));
  } catch (_) { /* ignore */ }
  return Object.assign({}, DEFAULT_SETTINGS);
}

function saveSettings() {
  try { localStorage.setItem('sportsScoresSettings', JSON.stringify(settings)); } catch (_) { /* ignore */ }
}

function applyTheme() {
  const body = document.body;
  body.classList.remove('dark', 'light');
  if (settings.theme === 'dark')  body.classList.add('dark');
  if (settings.theme === 'light') body.classList.add('light');
}

/* ── Security helpers ───────────────────────────────────────────────────── */

function escapeHtml(str) {
  if (str == null) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/* ── Screen reader announcements ────────────────────────────────────────── */

function announceToScreenReader(message, assertive = false) {
  const id = assertive ? 'sr-announce-assertive' : 'sr-announce';
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = '';
  setTimeout(() => { el.textContent = message; }, 100);
}

/* ── Date helpers ────────────────────────────────────────────────────────── */

function formatDateForESPN(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}${m}${d}`;
}

function formatDateForDisplay(date) {
  return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
}

function isToday(date) {
  const today = new Date();
  return date.getFullYear() === today.getFullYear()
      && date.getMonth()    === today.getMonth()
      && date.getDate()     === today.getDate();
}

function updateDateDisplays() {
  const display = isToday(currentDate) ? 'Today' : formatDateForDisplay(currentDate);
  document.querySelectorAll('[data-date-display]').forEach(el => { el.textContent = display; });
}

function goToPrevDate() {
  currentDate = new Date(currentDate);
  currentDate.setDate(currentDate.getDate() - 1);
  updateDateDisplays();
  reloadCurrentDateView();
}

function goToNextDate() {
  currentDate = new Date(currentDate);
  currentDate.setDate(currentDate.getDate() + 1);
  updateDateDisplays();
  reloadCurrentDateView();
}

function reloadCurrentDateView() {
  if (currentView === 'scores' && currentSection === 'scores' && currentSport) {
    loadScores(currentSport, currentDate);
  } else if (currentView === 'soccer' && currentSoccerLeague) {
    loadSoccerScores(currentSoccerLeague);
  } else if (currentView === 'soccer') {
    renderSoccerHub();
  }
}

/* ── Date picker modal ───────────────────────────────────────────────────── */

let _datePickerReturn = null;

function openDatePicker() {
  _datePickerReturn = document.activeElement;
  const modal = document.getElementById('date-picker-modal');
  const input = document.getElementById('date-picker-input');
  if (!modal || !input) return;
  // Format date as YYYY-MM-DD for input
  const y = currentDate.getFullYear();
  const m = String(currentDate.getMonth() + 1).padStart(2, '0');
  const d = String(currentDate.getDate()).padStart(2, '0');
  input.value = `${y}-${m}-${d}`;
  modal.hidden = false;
  setTimeout(() => input.focus(), 50);
}

function confirmDatePicker() {
  const input = document.getElementById('date-picker-input');
  if (!input || !input.value) { closeDatePicker(); return; }
  const parts = input.value.split('-');
  if (parts.length !== 3) { closeDatePicker(); return; }
  const newDate = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
  if (!isNaN(newDate.getTime())) {
    currentDate = newDate;
    updateDateDisplays();
    reloadCurrentDateView();
  }
  closeDatePicker();
}

function closeDatePicker() {
  const modal = document.getElementById('date-picker-modal');
  if (modal) modal.hidden = true;
  if (_datePickerReturn) { _datePickerReturn.focus(); _datePickerReturn = null; }
}

/* ── Settings panel ──────────────────────────────────────────────────────── */

let _settingsReturn = null;

function openSettings() {
  _settingsReturn = document.activeElement;
  const panel = document.getElementById('settings-panel');
  if (!panel) return;
  renderSettingsContent();
  panel.hidden = false;
  setTimeout(() => {
    const close = document.getElementById('settings-close');
    if (close) close.focus();
  }, 50);
}

function closeSettings() {
  const panel = document.getElementById('settings-panel');
  if (panel) panel.hidden = true;
  if (_settingsReturn) { _settingsReturn.focus(); _settingsReturn = null; }
}

function renderSettingsContent() {
  const content = document.getElementById('settings-content');
  if (!content) return;
  content.innerHTML = `
    <div class="settings-group">
      <label for="theme-select">Theme</label>
      <select id="theme-select" aria-label="Select theme">
        <option value="system" ${settings.theme === 'system' ? 'selected' : ''}>System default</option>
        <option value="light"  ${settings.theme === 'light'  ? 'selected' : ''}>Light</option>
        <option value="dark"   ${settings.theme === 'dark'   ? 'selected' : ''}>Dark</option>
      </select>
    </div>
    <div class="settings-group">
      <label for="refresh-select">Auto-refresh interval</label>
      <select id="refresh-select" aria-label="Auto-refresh interval">
        <option value="30"  ${settings.autoRefreshSeconds === 30  ? 'selected' : ''}>30 seconds</option>
        <option value="60"  ${settings.autoRefreshSeconds === 60  ? 'selected' : ''}>1 minute</option>
        <option value="300" ${settings.autoRefreshSeconds === 300 ? 'selected' : ''}>5 minutes</option>
        <option value="0"   ${settings.autoRefreshSeconds === 0   ? 'selected' : ''}>Off</option>
      </select>
    </div>`;

  document.getElementById('theme-select').addEventListener('change', e => {
    settings.theme = e.target.value;
    saveSettings();
    applyTheme();
  });
  document.getElementById('refresh-select').addEventListener('change', e => {
    settings.autoRefreshSeconds = parseInt(e.target.value, 10);
    saveSettings();
    startAutoRefresh();
  });
}

/* ── Modal helpers ───────────────────────────────────────────────────────── */

function closeAllModals() {
  closeDatePicker();
  closeSettings();
}

/* ── Auto-refresh ────────────────────────────────────────────────────────── */

function startAutoRefresh() {
  stopAutoRefresh();
  if (settings.autoRefreshSeconds <= 0) return;
  if (currentView === 'scores' && currentSection === 'scores' && currentSport) {
    autoRefreshTimer = setInterval(() => loadScores(currentSport, currentDate), settings.autoRefreshSeconds * 1000);
  } else if (currentView === 'live') {
    startLiveCountdown();
  }
}

function stopAutoRefresh() {
  if (autoRefreshTimer) { clearInterval(autoRefreshTimer); autoRefreshTimer = null; }
  stopLiveCountdown();
}

function startLiveCountdown() {
  if (settings.autoRefreshSeconds <= 0) return;
  liveCountdownSecs = settings.autoRefreshSeconds;
  updateCountdownDisplay();
  liveCountdownTimer = setInterval(() => {
    liveCountdownSecs--;
    updateCountdownDisplay();
    if (liveCountdownSecs <= 0) {
      stopLiveCountdown();
      loadLiveScores();
    }
  }, 1000);
}

function stopLiveCountdown() {
  if (liveCountdownTimer) { clearInterval(liveCountdownTimer); liveCountdownTimer = null; }
  const el = document.getElementById('live-refresh-countdown');
  if (el) el.textContent = '';
}

function updateCountdownDisplay() {
  const el = document.getElementById('live-refresh-countdown');
  if (el && liveCountdownSecs > 0) el.textContent = `Refreshing in ${liveCountdownSecs}s`;
}

/* ── View management ─────────────────────────────────────────────────────── */

function showView(viewId) {
  document.querySelectorAll('.app-view').forEach(v => { v.hidden = true; });
  const view = document.getElementById('view-' + viewId);
  if (view) {
    view.hidden = false;
    // Move focus to first heading in the view for screen readers
    const heading = view.querySelector('h2');
    if (heading) { heading.setAttribute('tabindex', '-1'); heading.focus(); }
  }
  currentView = viewId;
  stopAutoRefresh();
}

/* ── Routing ─────────────────────────────────────────────────────────────── */

function navigate(hash) {
  window.location.hash = hash;
}

function handleRoute() {
  const hash = window.location.hash.slice(1) || 'home';
  const parts = hash.split('/');

  switch (parts[0]) {
    case '':
    case 'home':
      renderHome();
      break;

    case 'scores':
      if (parts[1]) {
        currentSport = parts[1];
        currentSection = 'scores';
        showView('scores');
        updateSubnavTabs('scores');
        updateSportHeading();
        showFootballNav();
        updateDateDisplays();
        loadScores(currentSport, currentDate);
      }
      break;

    case 'game':
      if (parts[1] && parts[2]) {
        currentGame = { sport: parts[1], gameId: parts[2] };
        loadGameDetail(parts[1], parts[2]);
      }
      break;

    case 'schedule':
      if (parts[1] && parts[2]) {
        currentTeam = { sport: parts[1], teamId: parts[2] };
        loadTeamSchedule(parts[1], parts[2]);
      }
      break;

    case 'soccer':
      currentSoccerLeague = parts[1] || null;
      if (currentSoccerLeague) {
        showView('soccer');
        updateDateDisplays();
        loadSoccerScores(currentSoccerLeague);
      } else {
        renderSoccerHub();
      }
      break;

    case 'golf':
      loadGolfHub();
      break;

    case 'live':
      loadLiveScores();
      break;

    default:
      renderHome();
  }
}

/* ── Section switching ───────────────────────────────────────────────────── */

function switchSection(section) {
  currentSection = section;
  updateSubnavTabs(section);
  showFootballNav();

  if (!currentSport) return;

  switch (section) {
    case 'scores':    loadScores(currentSport, currentDate); break;
    case 'standings': loadStandings(currentSport); break;
    case 'news':      loadNews(currentSport); break;
    case 'stats':     loadStatistics(currentSport); break;
  }
  startAutoRefresh();
}

function updateSubnavTabs(section) {
  document.querySelectorAll('.subnav-tab').forEach(tab => {
    const active = tab.dataset.section === section;
    tab.setAttribute('aria-selected', active.toString());
    tab.classList.toggle('active', active);
  });
}

function showFootballNav() {
  const sportConfig = SPORTS.find(s => s.key === currentSport);
  const show = !!(sportConfig && sportConfig.isFootball && currentSection === 'scores');
  const nav = document.getElementById('football-nav');
  if (nav) nav.hidden = !show;
  if (show && currentFootball.week) {
    const wd = document.getElementById('week-display');
    if (wd) wd.textContent = `Week ${currentFootball.week}`;
  }
}

function updateSportHeading() {
  const sportConfig = SPORTS.find(s => s.key === currentSport);
  const heading = document.getElementById('scores-heading');
  if (heading && sportConfig) heading.textContent = sportConfig.fullName;
}

/* ── View mode toggle ────────────────────────────────────────────────────── */

function switchGameView(viewMode) {
  currentGameView = viewMode;
  document.querySelectorAll('.view-mode-btn').forEach(btn => {
    const active = btn.dataset.view === viewMode;
    btn.classList.toggle('active', active);
    btn.setAttribute('aria-pressed', active.toString());
  });
  if (currentView === 'scores' && currentSection === 'scores' && currentSport) {
    loadScores(currentSport, currentDate);
  } else if (currentView === 'soccer' && currentSoccerLeague) {
    loadSoccerScores(currentSoccerLeague);
  }
  announceToScreenReader(`Switched to ${viewMode} view`);
}

function cycleViewMode() {
  const modes = ['card', 'table', 'list'];
  const idx = modes.indexOf(currentGameView);
  switchGameView(modes[(idx + 1) % modes.length]);
}

/* ── API ─────────────────────────────────────────────────────────────────── */

async function apiFetch(endpoint) {
  const response = await fetch('/api/' + endpoint);
  if (!response.ok) throw new Error(`Server error ${response.status}`);
  return response.json();
}

/* ── Loading / error helpers ─────────────────────────────────────────────── */

function showLoading(containerId) {
  const el = document.getElementById(containerId);
  if (el) el.innerHTML = '<div class="loading-spinner" role="status"><span class="visually-hidden">Loading…</span></div>';
}

function showError(containerId, message) {
  const el = document.getElementById(containerId);
  if (el) el.innerHTML = `<div class="error-message" role="alert"><p>Error: ${escapeHtml(message)}</p></div>`;
}

/* ── Status classifiers ──────────────────────────────────────────────────── */

function isLive(game) {
  const s = (game.status || '').toLowerCase();
  if (!s || s === 'scheduled') return false;
  if (s.includes('final') || s.includes('postponed') || s.includes('canceled') || s.includes('cancelled')) return false;
  return true;
}

function isCompleted(game) {
  const s = (game.status || '').toLowerCase();
  return s.includes('final') || s.includes('completed');
}

function isUpcoming(game) {
  return !isLive(game) && !isCompleted(game);
}

function statusClass(game) {
  if (isLive(game)) return 'status-live';
  if (isCompleted(game)) return 'status-final';
  return 'status-upcoming';
}

function displayStatus(game) {
  return escapeHtml(game.status || game.start_time || 'Scheduled');
}

/* ── Hub tile helper ─────────────────────────────────────────────────────── */

function createHubTile(label, icon, onClick) {
  const tile = document.createElement('article');
  tile.className = 'sport-tile hub-tile';
  tile.setAttribute('role', 'listitem');
  tile.setAttribute('tabindex', '0');
  tile.innerHTML = `<span class="hub-icon" aria-hidden="true">${icon}</span><h3>${escapeHtml(label)}</h3>`;
  tile.addEventListener('click', onClick);
  tile.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClick(); } });
  return tile;
}

/* ── Home view ───────────────────────────────────────────────────────────── */

function renderHome() {
  showView('home');
  updateDateDisplays();

  const grid = document.getElementById('sport-grid');
  if (!grid) return;
  grid.innerHTML = '';

  const visible = SPORTS.filter(s => settings.visibleSports.includes(s.key));
  visible.forEach(sport => {
    const tile = document.createElement('article');
    tile.className = 'sport-tile';
    tile.setAttribute('role', 'listitem');
    tile.setAttribute('tabindex', '0');
    tile.innerHTML = `<h3>${escapeHtml(sport.name)}</h3><p>${escapeHtml(sport.fullName)}</p>`;
    tile.addEventListener('click', () => navigate('scores/' + sport.key));
    tile.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); navigate('scores/' + sport.key); }
    });
    grid.appendChild(tile);
  });

  grid.appendChild(createHubTile('Soccer Hub', '⚽', () => navigate('soccer')));
  grid.appendChild(createHubTile('Golf Hub',   '⛳', () => navigate('golf')));
  grid.appendChild(createHubTile('Live Scores','🔴', () => navigate('live')));
}

/* ── Scores view ─────────────────────────────────────────────────────────── */

async function loadScores(sport, date) {
  updateSportHeading();
  showFootballNav();
  showLoading('scores-content');

  try {
    let endpoint = `scores/${sport.toUpperCase()}?date=${formatDateForESPN(date)}`;
    if (currentFootball.week && SPORTS.find(s => s.key === sport)?.isFootball) {
      endpoint += `&week=${currentFootball.week}&seasontype=${currentFootball.seasonType}`;
      const wd = document.getElementById('week-display');
      if (wd) wd.textContent = `Week ${currentFootball.week}`;
    }
    const games = await apiFetch(endpoint);
    renderGames(games, document.getElementById('scores-content'), sport);
  } catch (err) {
    showError('scores-content', err.message);
  }
  startAutoRefresh();
}

function renderGames(games, container, sport) {
  if (!container) return;
  const live      = games.filter(isLive);
  const upcoming  = games.filter(isUpcoming);
  const completed = games.filter(isCompleted);

  container.innerHTML = '';

  if (games.length === 0) {
    container.innerHTML = '<p class="no-games">No games scheduled for this date.</p>';
    return;
  }

  if (currentGameView === 'table') {
    renderTableView(games, live, upcoming, completed, container, sport);
  } else if (currentGameView === 'list') {
    renderListView(games, live, upcoming, completed, container, sport);
  } else {
    renderCardView(games, live, upcoming, completed, container, sport);
  }
}

/* ── Card view ───────────────────────────────────────────────────────────── */

function renderCardView(games, live, upcoming, completed, container, sport) {
  const sections = [
    { label: 'LIVE',     list: live,      cssClass: 'section-live'     },
    { label: 'UPCOMING', list: upcoming,  cssClass: 'section-upcoming' },
    { label: 'FINAL',    list: completed, cssClass: 'section-final'    },
  ];

  sections.forEach(({ label, list, cssClass }) => {
    if (!list.length) return;
    const section = document.createElement('section');
    section.className = `game-section ${cssClass}`;
    const id = `section-hdr-${label.toLowerCase()}`;
    section.setAttribute('aria-labelledby', id);

    const header = document.createElement('h3');
    header.id = id;
    header.className = 'game-section-header';
    header.textContent = label;
    section.appendChild(header);

    const cardList = document.createElement('div');
    cardList.setAttribute('role', 'list');
    cardList.className = 'games-card-list';
    list.forEach(game => cardList.appendChild(createGameCard(game, sport)));
    section.appendChild(cardList);
    container.appendChild(section);
  });
}

function createGameCard(game, sport) {
  const card = document.createElement('article');
  card.className = 'game-card';
  card.setAttribute('role', 'listitem');
  card.setAttribute('tabindex', '0');

  const sc = statusClass(game);
  const awayId   = game.away_team_id;
  const homeId   = game.home_team_id;
  const awayName = escapeHtml(game.away_team || 'Away');
  const homeName = escapeHtml(game.home_team || 'Home');

  const awayHtml = awayId
    ? `<a href="#schedule/${escapeHtml(sport)}/${escapeHtml(awayId)}" class="team-link" aria-label="View ${awayName} schedule">${awayName}</a>`
    : awayName;
  const homeHtml = homeId
    ? `<a href="#schedule/${escapeHtml(sport)}/${escapeHtml(homeId)}" class="team-link" aria-label="View ${homeName} schedule">${homeName}</a>`
    : homeName;

  card.innerHTML = `
    <div class="game-card-teams">
      <div class="team away-team">
        <span class="team-name">${awayHtml}</span>
        <span class="score">${escapeHtml(game.away_score || '')}</span>
      </div>
      <div class="team home-team">
        <span class="team-name">${homeHtml}</span>
        <span class="score">${escapeHtml(game.home_score || '')}</span>
      </div>
    </div>
    <div class="game-card-meta">
      <span class="status-badge ${sc}">${displayStatus(game)}</span>
      ${game.broadcast ? `<span class="broadcast">${escapeHtml(game.broadcast)}</span>` : ''}
    </div>`;

  card.addEventListener('click', e => {
    if (e.target.classList.contains('team-link') || e.target.closest('.team-link')) return;
    navigate(`game/${sport}/${game.id}`);
  });
  card.addEventListener('keydown', e => {
    if (e.key === 'Enter') { e.preventDefault(); navigate(`game/${sport}/${game.id}`); }
  });
  return card;
}

/* ── Table view ──────────────────────────────────────────────────────────── */

function renderTableView(games, live, upcoming, completed, container, sport) {
  const sections = [
    { label: 'LIVE',     list: live      },
    { label: 'UPCOMING', list: upcoming  },
    { label: 'FINAL',    list: completed },
  ].filter(s => s.list.length > 0);

  const wrapper = document.createElement('div');
  wrapper.className = 'table-wrapper';

  const table = document.createElement('table');
  table.className = 'games-table';
  table.setAttribute('aria-label', 'Games');

  const thead = document.createElement('thead');
  thead.innerHTML = `<tr>
    <th scope="col">Status</th>
    <th scope="col">Away</th>
    <th scope="col">Home</th>
    <th scope="col">Score</th>
    <th scope="col">TV</th>
  </tr>`;
  table.appendChild(thead);

  const tbody = document.createElement('tbody');

  sections.forEach(({ label, list }) => {
    list.forEach((game, idx) => {
      const tr = document.createElement('tr');
      tr.className = isLive(game) ? 'row-live' : isCompleted(game) ? 'row-final' : 'row-upcoming';
      tr.setAttribute('tabindex', '0');

      const sc       = statusClass(game);
      const awayId   = game.away_team_id;
      const homeId   = game.home_team_id;
      const awayName = escapeHtml(game.away_team || '');
      const homeName = escapeHtml(game.home_team || '');
      const awayLink = awayId ? `<a href="#schedule/${escapeHtml(sport)}/${escapeHtml(awayId)}" class="team-link">${awayName}</a>` : awayName;
      const homeLink = homeId ? `<a href="#schedule/${escapeHtml(sport)}/${escapeHtml(homeId)}" class="team-link">${homeName}</a>` : homeName;

      tr.innerHTML = `
        <td><span class="status-badge ${sc}">${idx === 0 ? escapeHtml(label) : ''} ${displayStatus(game)}</span></td>
        <td>${awayLink}</td>
        <td>${homeLink}</td>
        <td class="score-cell">${escapeHtml(game.away_score || '—')} – ${escapeHtml(game.home_score || '—')}</td>
        <td>${escapeHtml(game.broadcast || '—')}</td>`;

      tr.addEventListener('click', e => {
        if (e.target.classList.contains('team-link') || e.target.closest('.team-link')) return;
        navigate(`game/${sport}/${game.id}`);
      });
      tr.addEventListener('keydown', e => {
        if (e.key === 'Enter') { e.preventDefault(); navigate(`game/${sport}/${game.id}`); }
      });
      tbody.appendChild(tr);
    });
  });

  table.appendChild(tbody);
  wrapper.appendChild(table);
  container.appendChild(wrapper);
}

/* ── List view ───────────────────────────────────────────────────────────── */

function renderListView(games, live, upcoming, completed, container, sport) {
  const allGames = [...live, ...upcoming, ...completed];

  const listbox = document.createElement('div');
  listbox.setAttribute('role', 'listbox');
  listbox.setAttribute('aria-label', 'Games');
  listbox.setAttribute('tabindex', '0');
  listbox.className = 'games-list';

  allGames.forEach((game, index) => {
    const item = document.createElement('div');
    item.setAttribute('role', 'option');
    item.setAttribute('aria-selected', 'false');
    item.id = `game-item-${index}`;
    item.setAttribute('tabindex', '-1');
    item.className = 'game-list-item';

    const sc    = statusClass(game);
    const score = (game.away_score && game.home_score)
      ? `${escapeHtml(game.away_score)}–${escapeHtml(game.home_score)}`
      : '';

    item.innerHTML = `
      <span class="list-teams">${escapeHtml(game.away_team || '')} @ ${escapeHtml(game.home_team || '')}</span>
      <span class="list-score">${score}</span>
      <span class="status-badge ${sc}">${displayStatus(game)}</span>
      ${game.broadcast ? `<span class="list-tv">${escapeHtml(game.broadcast)}</span>` : ''}`;

    item.addEventListener('click', () => navigate(`game/${sport}/${game.id}`));
    listbox.appendChild(item);
  });

  addListboxNavigation(listbox, (_, index) => {
    if (allGames[index]) navigate(`game/${sport}/${allGames[index].id}`);
  });

  container.appendChild(listbox);
}

/* ── Listbox keyboard navigation ─────────────────────────────────────────── */

function addListboxNavigation(listbox, onActivate) {
  let activeIndex = -1;
  const getItems = () => Array.from(listbox.querySelectorAll('[role="option"]'));

  listbox.addEventListener('keydown', e => {
    const items = getItems();
    if (!items.length) return;
    let next = activeIndex;

    switch (e.key) {
      case 'ArrowDown': next = Math.min(activeIndex + 1, items.length - 1); e.preventDefault(); break;
      case 'ArrowUp':   next = Math.max(activeIndex - 1, 0);               e.preventDefault(); break;
      case 'Home':      next = 0;                e.preventDefault(); break;
      case 'End':       next = items.length - 1; e.preventDefault(); break;
      case 'Enter':
      case ' ':
        if (activeIndex >= 0) onActivate(items[activeIndex], activeIndex);
        e.preventDefault();
        return;
      default: return;
    }

    if (next !== activeIndex) {
      if (activeIndex >= 0) items[activeIndex].setAttribute('aria-selected', 'false');
      activeIndex = next;
      items[activeIndex].setAttribute('aria-selected', 'true');
      items[activeIndex].scrollIntoView({ block: 'nearest' });
      listbox.setAttribute('aria-activedescendant', items[activeIndex].id);
      announceToScreenReader(items[activeIndex].textContent.trim());
    }
  });
}

/* ── Game detail ─────────────────────────────────────────────────────────── */

async function loadGameDetail(sport, gameId) {
  showView('game');
  showLoading('game-content');

  try {
    const details = await apiFetch(`game/${sport.toUpperCase()}/${gameId}`);
    renderGameDetail(details, sport);
  } catch (err) {
    showError('game-content', err.message);
  }
}

function renderGameDetail(details, sport) {
  const container = document.getElementById('game-content');
  container.innerHTML = '';

  renderGameHeader(details, container, sport);

  const comp = details?.header?.competitions?.[0];
  if (comp) {
    renderLinescore(comp, sport, container);
  }
  if (details.boxscore) {
    renderBoxScore(details.boxscore, sport, container);
  }
  if (details.plays && details.plays.length) {
    renderPlayByPlay(details, sport, container);
  }
}

function renderGameHeader(details, container, sport) {
  const comp = details?.header?.competitions?.[0];
  if (!comp) return;

  const competitors = comp.competitors || [];
  const away = competitors.find(c => c.homeAway === 'away') || competitors[0] || {};
  const home = competitors.find(c => c.homeAway === 'home') || competitors[1] || away;

  const awayTeam  = away.team || {};
  const homeTeam  = home.team || {};
  const awayScore = escapeHtml(away.score || '');
  const homeScore = escapeHtml(home.score || '');
  const awayRec   = escapeHtml((away.records || [])[0]?.summary || '');
  const homeRec   = escapeHtml((home.records || [])[0]?.summary || '');

  const statusDesc   = comp.status?.type?.description || '';
  const statusDetail = comp.status?.type?.shortDetail || comp.status?.type?.detail || statusDesc;
  const sc = statusDesc.toLowerCase().includes('final') ? 'status-final'
           : (statusDesc.toLowerCase().includes('progress') || statusDesc.toLowerCase().includes('half')) ? 'status-live'
           : 'status-upcoming';

  const awayName = escapeHtml(awayTeam.displayName || 'Away');
  const homeName = escapeHtml(homeTeam.displayName || 'Home');
  const awayAbbr = escapeHtml(awayTeam.abbreviation || '');
  const homeAbbr = escapeHtml(homeTeam.abbreviation || '');

  document.getElementById('game-heading').textContent = `${awayTeam.abbreviation || 'Away'} @ ${homeTeam.abbreviation || 'Home'}`;

  const header = document.createElement('div');
  header.className = 'game-header';
  header.innerHTML = `
    <div class="matchup-header">
      <div class="matchup-team away">
        <div class="matchup-name">${awayName}</div>
        ${awayRec ? `<div class="matchup-record">${awayRec}</div>` : ''}
        <div class="matchup-score">${awayScore}</div>
      </div>
      <div class="matchup-vs">
        <span class="status-badge ${sc}">${escapeHtml(statusDetail)}</span>
      </div>
      <div class="matchup-team home">
        <div class="matchup-name">${homeName}</div>
        ${homeRec ? `<div class="matchup-record">${homeRec}</div>` : ''}
        <div class="matchup-score">${homeScore}</div>
      </div>
    </div>`;
  container.appendChild(header);
}

function renderLinescore(comp, sport, container) {
  const competitors = comp.competitors || [];
  if (!competitors.length) return;

  const away = competitors.find(c => c.homeAway === 'away') || competitors[0];
  const home = competitors.find(c => c.homeAway === 'home') || competitors[1] || competitors[0];

  const awayLS = (away && away.linescores) ? away.linescores : [];
  const homeLS = (home && home.linescores) ? home.linescores : [];

  if (!awayLS.length && !homeLS.length) return;

  const numPeriods = Math.max(awayLS.length, homeLS.length);
  const labels = getPeriodLabels(sport, numPeriods);

  const section = document.createElement('section');
  section.className = 'linescore-section';
  const h3 = document.createElement('h3');
  h3.textContent = 'Line Score';
  section.appendChild(h3);

  const table = document.createElement('table');
  table.className = 'linescore-table';
  table.setAttribute('aria-label', 'Line score');

  const thead = document.createElement('thead');
  thead.innerHTML = `<tr>
    <th scope="col">Team</th>
    ${labels.map(l => `<th scope="col">${escapeHtml(l)}</th>`).join('')}
    <th scope="col">T</th>
  </tr>`;
  table.appendChild(thead);

  const tbody = document.createElement('tbody');
  [[away, awayLS], [home, homeLS]].forEach(([comp, ls]) => {
    if (!comp) return;
    const team = comp.team || {};
    const abbr = escapeHtml(team.abbreviation || team.displayName || '');
    const total = escapeHtml(comp.score || '');
    const cells = ls.map(p => `<td>${escapeHtml(p.displayValue || '')}</td>`).join('');
    const pad   = numPeriods > ls.length ? `<td></td>`.repeat(numPeriods - ls.length) : '';
    const tr = document.createElement('tr');
    tr.innerHTML = `<th scope="row">${abbr}</th>${cells}${pad}<td><strong>${total}</strong></td>`;
    tbody.appendChild(tr);
  });

  table.appendChild(tbody);
  section.appendChild(table);
  container.appendChild(section);
}

function getPeriodLabels(sport, num) {
  const ot = n => n <= 1 ? 'OT' : `OT${n}`;
  if (sport === 'mlb') return Array.from({ length: num }, (_, i) => String(i + 1));
  if (sport === 'nfl' || sport === 'ncaaf') {
    const base = ['Q1','Q2','Q3','Q4'];
    return [...base, ...Array.from({ length: Math.max(0, num - 4) }, (_, i) => ot(i + 1))].slice(0, num);
  }
  if (['nba','ncaam','ncaawb','wnba'].includes(sport)) {
    const base = ['Q1','Q2','Q3','Q4'];
    return [...base, ...Array.from({ length: Math.max(0, num - 4) }, (_, i) => ot(i + 1))].slice(0, num);
  }
  if (['nhl','ncaah','ncaawh'].includes(sport)) {
    const base = ['P1','P2','P3'];
    return [...base, ...Array.from({ length: Math.max(0, num - 3) }, (_, i) => ot(i + 1))].slice(0, num);
  }
  return Array.from({ length: num }, (_, i) => String(i + 1));
}

function renderBoxScore(boxscore, sport, container) {
  const teams = boxscore.teams || [];
  if (!teams.length) return;

  const firstStats = teams[0]?.statistics || [];
  if (!firstStats.length) return;

  const section = document.createElement('section');
  section.className = 'boxscore-section';
  const h3 = document.createElement('h3');
  h3.textContent = 'Team Stats';
  section.appendChild(h3);

  const table = document.createElement('table');
  table.className = 'boxscore-table';
  table.setAttribute('aria-label', 'Team statistics');

  const thead = document.createElement('thead');
  thead.innerHTML = `<tr>
    <th scope="col">Stat</th>
    ${teams.map(t => `<th scope="col">${escapeHtml(t.team?.abbreviation || 'Team')}</th>`).join('')}
  </tr>`;
  table.appendChild(thead);

  const tbody = document.createElement('tbody');
  firstStats.forEach((stat, idx) => {
    const tr = document.createElement('tr');
    const label = escapeHtml(stat.label || stat.name || '');
    const vals  = teams.map(t => `<td>${escapeHtml((t.statistics[idx] || {}).displayValue || '')}</td>`).join('');
    tr.innerHTML = `<td>${label}</td>${vals}`;
    tbody.appendChild(tr);
  });

  table.appendChild(tbody);
  section.appendChild(table);
  container.appendChild(section);
}

/* ── Play-by-Play ────────────────────────────────────────────────────────── */

let _pbpNodeId = 0;

function makePbpNode(label, children = [], options = {}) {
  const hasChildren = children && children.length > 0;
  return {
    id: `pbp-${++_pbpNodeId}`,
    label,
    children,
    scoring:  options.scoring  || false,
    expanded: options.expanded !== undefined ? options.expanded : !hasChildren,
    cssClass: options.cssClass || '',
  };
}

function pbpExtractClock(clockValue) {
  if (!clockValue) return '';
  if (typeof clockValue === 'string') return clockValue;
  if (typeof clockValue === 'object') {
    return clockValue.displayValue || clockValue.value || clockValue.text || '';
  }
  return '';
}

function pbpParseClock(clockStr) {
  const s = pbpExtractClock(clockStr);
  const m = s.match(/^(\d+):(\d+)/);
  return m ? parseInt(m[1], 10) * 60 + parseInt(m[2], 10) : 0;
}

function pbpSafeInt(v) {
  if (v == null || v === '') return null;
  const n = parseInt(v, 10);
  return isNaN(n) ? null : n;
}

function pbpScoreText(play, awayAbbr, homeAbbr) {
  const away = pbpSafeInt(play.awayScore);
  const home = pbpSafeInt(play.homeScore);
  return (away != null && home != null) ? `${awayAbbr} ${away} - ${homeAbbr} ${home}` : '';
}

function pbpFormatClockPlay(text, clock, play, awayAbbr, homeAbbr) {
  const score = pbpScoreText(play, awayAbbr, homeAbbr);
  if (clock && clock !== '--:--') {
    return score ? `${text} - ${clock} (${score})` : `${text} - ${clock}`;
  }
  return score ? `${text} (${score})` : text;
}

function pbpGetTeamLabels(details) {
  let awayAbbr = 'Away', homeAbbr = 'Home';
  const comp = details?.header?.competitions?.[0];
  if (comp) {
    (comp.competitors || []).forEach(c => {
      const abbr = c?.team?.abbreviation || c?.team?.shortDisplayName || c?.team?.displayName;
      if (!abbr) return;
      if (c.homeAway === 'away') awayAbbr = abbr;
      if (c.homeAway === 'home') homeAbbr = abbr;
    });
  }
  return [awayAbbr, homeAbbr];
}

// ── Baseball ──────────────────────────────────────────────────────────────

function buildBaseballPbpTree(plays, awayAbbr, homeAbbr) {
  const SKIP_PREFIXES = ['Top of the', 'Bottom of the', 'End of the', 'Middle of the'];
  const isSub = p => {
    if (p.summaryType === 'C') return true;
    const t = (p.text || '').toLowerCase();
    return t.includes(' hit for ') || t.includes(' ran for ') || t.includes(' entered for ');
  };

  const inningOrder = [];
  const inningHalves = {};
  for (const play of plays) {
    const pd = play.period || {};
    const num = pd.number || 0;
    const type = (pd.type || '').toLowerCase();
    const label = pd.displayValue || `Inning ${num}`;
    if (!inningHalves[num]) { inningOrder.push(num); inningHalves[num] = { top: [], bottom: [], label }; }
    if (type === 'bottom') inningHalves[num].bottom.push(play);
    else inningHalves[num].top.push(play);
  }

  const runsInHalf = (halfPlays, scoreKey) => {
    const sPlays = halfPlays.filter(p => p.summaryType === 'S');
    if (sPlays.length) return sPlays.reduce((acc, p) => acc + Math.max(0, parseInt(p.scoreValue || 0, 10)), 0);
    const scores = halfPlays.map(p => pbpSafeInt(p[scoreKey])).filter(v => v != null);
    return scores.length >= 2 ? Math.max(0, scores[scores.length - 1] - scores[0]) : 0;
  };

  const buildHalfAtBats = (halfPlays) => {
    const abOrder = [], abGroups = {};
    for (const play of halfPlays) {
      const text = play.text || '';
      if (SKIP_PREFIXES.some(pfx => text.startsWith(pfx))) continue;
      if (play.summaryType === 'I' || (!play.summaryType && !text.trim())) continue;
      const abId = play.atBatId || `_solo_${play.id || abOrder.length}`;
      if (!abGroups[abId]) { abOrder.push(abId); abGroups[abId] = []; }
      abGroups[abId].push(play);
    }
    const nodes = [];
    for (const abId of abOrder) {
      const group = abGroups[abId];
      const changePlays = group.filter(isSub);
      const nonChange   = group.filter(p => !isSub(p));
      for (const cp of changePlays) {
        const txt = (cp.text || '').trim();
        if (txt) nodes.push(makePbpNode(`>> ${txt}`, [], { cssClass: 'pbp-item--sub' }));
      }
      if (!nonChange.length) continue;
      const aPlay      = nonChange.find(p => p.summaryType === 'A') || null;
      const headerText = aPlay?.text || nonChange[0]?.text || 'At-bat';
      const resultPlay = nonChange.find(p => p.summaryType === 'S')
                      || nonChange.find(p => p.summaryType === 'N' && !isSub(p))
                      || null;
      const isScoring  = resultPlay?.summaryType === 'S';
      const resultText = resultPlay?.text || '';
      const pitches    = nonChange.filter(p => p.summaryType === 'P');
      let scoreSuffix  = '';
      if (isScoring) {
        const a = pbpSafeInt(resultPlay?.awayScore), h = pbpSafeInt(resultPlay?.homeScore);
        if (a != null && h != null) scoreSuffix = ` (${awayAbbr} ${a} - ${homeAbbr} ${h})`;
      }
      const prefix   = isScoring ? '⚾ ' : '';
      let mainText   = (resultText && resultText !== headerText)
        ? `${prefix}${headerText}: ${resultText}${scoreSuffix}`
        : `${prefix}${headerText}${scoreSuffix}`;
      if (pitches.length) mainText += `  [${pitches.length}p]`;
      const pitchNodes = pitches.map((pitch, i) =>
        makePbpNode(`Pitch ${i + 1}: ${pitch.text || ''}`, [], {})
      );
      nodes.push(makePbpNode(mainText, pitchNodes, {
        scoring:  isScoring,
        expanded: false,
        cssClass: isScoring ? 'pbp-item--scoring' : '',
      }));
    }
    return nodes;
  };

  return inningOrder.map(num => {
    const { top, bottom, label } = inningHalves[num];
    const topRuns    = runsInHalf(top,    'awayScore');
    const bottomRuns = runsInHalf(bottom, 'homeScore');
    const totalRuns  = topRuns + bottomRuns;
    let scoreText = '';
    for (const play of [...top, ...bottom].reverse()) {
      const a = pbpSafeInt(play.awayScore), h = pbpSafeInt(play.homeScore);
      if (a != null && h != null) { scoreText = `  [${awayAbbr} ${a} - ${homeAbbr} ${h}]`; break; }
    }
    const runParts = [];
    if (topRuns    > 0) runParts.push(`${awayAbbr} ${topRuns}R`);
    if (bottomRuns > 0) runParts.push(`${homeAbbr} ${bottomRuns}R`);
    const inningLabel = runParts.length
      ? `${label} — ${runParts.join(', ')}${scoreText}`
      : `${label}${scoreText}`;
    const children = [];
    if (top.length) {
      const abCount = Math.max(top.filter(p => p.summaryType === 'A').length, 1);
      const badge   = topRuns > 0 ? `  ${topRuns}R` : `  ${abCount} AB`;
      children.push(makePbpNode(`Top — ${awayAbbr} Batting${badge}`, buildHalfAtBats(top), {
        expanded: true, scoring: topRuns > 0, cssClass: topRuns > 0 ? 'pbp-item--scoring-half' : '',
      }));
    }
    if (bottom.length) {
      const abCount = Math.max(bottom.filter(p => p.summaryType === 'A').length, 1);
      const badge   = bottomRuns > 0 ? `  ${bottomRuns}R` : `  ${abCount} AB`;
      children.push(makePbpNode(`Bottom — ${homeAbbr} Batting${badge}`, buildHalfAtBats(bottom), {
        expanded: true, scoring: bottomRuns > 0, cssClass: bottomRuns > 0 ? 'pbp-item--scoring-half' : '',
      }));
    }
    return makePbpNode(inningLabel, children, {
      expanded: true, scoring: totalRuns > 0, cssClass: totalRuns > 0 ? 'pbp-item--scoring-inning' : '',
    });
  });
}

// ── Football ──────────────────────────────────────────────────────────────

function buildFootballPbpTree(plays, awayAbbr, homeAbbr) {
  const driveResult = drivePlays => {
    if (!drivePlays.length) return 'No plays';
    const t = (drivePlays[drivePlays.length - 1]?.text || '').toLowerCase();
    if (t.includes('touchdown'))  return 'Touchdown';
    if (t.includes('field goal')) return 'Field Goal';
    if (t.includes('punt'))       return 'Punt';
    if (t.includes('turnover') || t.includes('interception') || t.includes('fumble')) return 'Turnover';
    if (t.includes('safety'))     return 'Safety';
    if (t.includes('end of quarter') || t.includes('end of half') || t.includes('end of game')) return 'End of Period';
    return `${drivePlays.length} plays`;
  };

  const quarterOrder = [], quarterData = {};
  for (const play of plays) {
    const pd      = play.period || {};
    const display = pd.displayValue || `Q${pd.number || 1}`;
    const dk      = String(play.driveNumber || '');
    const abbr    = play.team?.abbreviation || play.team?.shortDisplayName || play.team?.displayName || '';
    if (!quarterData[display]) { quarterOrder.push(display); quarterData[display] = { driveOrder: [], drives: {}, teamNames: {} }; }
    const qd = quarterData[display];
    if (!qd.drives[dk]) { qd.driveOrder.push(dk); qd.drives[dk] = []; qd.teamNames[dk] = abbr; }
    else if (abbr && !qd.teamNames[dk]) qd.teamNames[dk] = abbr;
    qd.drives[dk].push(play);
  }

  return quarterOrder.map(display => {
    const qd = quarterData[display];
    let quarterScore = '';
    outer: for (const dk of [...qd.driveOrder].reverse()) {
      for (const p of [...qd.drives[dk]].reverse()) {
        const a = pbpSafeInt(p.awayScore), h = pbpSafeInt(p.homeScore);
        if (a != null && h != null) { quarterScore = `  [${awayAbbr} ${a} - ${homeAbbr} ${h}]`; break outer; }
      }
    }
    const driveNodes = qd.driveOrder.map(dk => {
      const drivePlays = qd.drives[dk];
      if (!drivePlays.length) return null;
      const result  = driveResult(drivePlays);
      const scoring = ['Touchdown', 'Field Goal', 'Safety'].includes(result);
      let driveScore = '';
      for (const p of [...drivePlays].reverse()) {
        const a = pbpSafeInt(p.awayScore), h = pbpSafeInt(p.homeScore);
        if (a != null && h != null) { driveScore = `  (${a}-${h})`; break; }
      }
      const prefix     = qd.teamNames[dk] ? `${qd.teamNames[dk]}: ` : 'Drive: ';
      const driveLabel = `${prefix}${result}${driveScore}  (${drivePlays.length} plays)`;
      const playNodes  = drivePlays.map(play => {
        const start  = play.start || {};
        const down   = start.down || 0;
        const dist   = start.distance || 0;
        const poss   = start.possessionText || '';
        const yardEZ = start.yardsToEndzone || 0;
        const statY  = play.statYardage || 0;
        let situation = '';
        if      (yardEZ && yardEZ <= 5)  situation = 'GOAL LINE ';
        else if (yardEZ && yardEZ <= 20) situation = 'RED ZONE ';
        else if (down === 4)             situation = '4TH DOWN ';
        const downText = down
          ? (poss ? `[${situation}${down} & ${dist} from ${poss}] ` : `[${situation}${down} & ${dist}] `)
          : '';
        const yardsPfx = statY > 0 ? `(+${statY} yds) ` : statY < 0 ? `(${statY} yds) ` : '';
        const clock    = pbpExtractClock(play.clock);
        const playText = `${downText}${yardsPfx}${play.text || 'Unknown play'}`;
        const formatted = pbpFormatClockPlay(playText, clock, play, awayAbbr, homeAbbr);
        let cls = '';
        if      (play.scoringPlay)              cls = 'pbp-item--scoring';
        else if (yardEZ && yardEZ <= 5)         cls = 'pbp-item--goalline';
        else if (yardEZ && yardEZ <= 20)        cls = 'pbp-item--redzone';
        return makePbpNode(formatted, [], { scoring: !!play.scoringPlay, cssClass: cls });
      });
      return makePbpNode(driveLabel, playNodes, {
        scoring, expanded: false, cssClass: scoring ? 'pbp-item--scoring-drive' : '',
      });
    }).filter(Boolean);
    return makePbpNode(`${display}${quarterScore}`, driveNodes, { expanded: true });
  });
}

// ── Basketball ────────────────────────────────────────────────────────────

function buildBasketballPbpTree(plays, awayAbbr, homeAbbr) {
  const periodOrder = [], periodGroups = {};
  for (const play of plays) {
    const pd  = play.period || {};
    const num = pd.number || 1;
    if (!periodGroups[num]) { periodOrder.push(num); periodGroups[num] = { plays: [], label: pd.displayValue || String(num) }; }
    periodGroups[num].plays.push(play);
  }
  const ordinalLabel = (num, fallback) => {
    const fl = (fallback || '').toLowerCase();
    if (fl.includes('ot') || fl.includes('overtime') || fl.includes('extra')) {
      const o = num - 4; return o > 1 ? `OT${o}` : 'OT';
    }
    const ord = { 1: '1st', 2: '2nd', 3: '3rd', 4: '4th' };
    if (ord[num]) return `${ord[num]} Quarter`;
    if (num > 4) { const o = num - 4; return o > 1 ? `OT${o}` : 'OT'; }
    return fallback || `Period ${num}`;
  };
  const bbClass = play => {
    const t = (play.text || '').toLowerCase();
    if ((t.includes('makes') || t.includes('made')) && (t.includes('three') || t.includes('3-pt'))) return 'pbp-item--bb-three';
    if ((t.includes('makes') || t.includes('made')) && (t.includes('layup') || t.includes('dunk') || t.includes('tip'))) return 'pbp-item--bb-layup';
    if ((t.includes('makes') || t.includes('made')) && t.includes('free throw')) return 'pbp-item--bb-ft';
    if (t.includes('misses') && (t.includes('three') || t.includes('3-pt'))) return 'pbp-item--bb-miss3';
    if (t.includes('foul') && !t.includes('technical')) return 'pbp-item--bb-foul';
    if (t.includes('technical foul') || t.includes('flagrant')) return 'pbp-item--bb-technical';
    if (t.includes('timeout')) return 'pbp-item--bb-timeout';
    if (t.includes('substitution')) return 'pbp-item--bb-sub';
    return '';
  };
  return periodOrder.map(num => {
    const pg          = periodGroups[num];
    const periodLabel = ordinalLabel(num, pg.label);
    let periodScore   = '';
    for (const p of [...pg.plays].reverse()) {
      const a = pbpSafeInt(p.awayScore), h = pbpSafeInt(p.homeScore);
      if (a != null && h != null) { periodScore = `  [${awayAbbr} ${a} - ${homeAbbr} ${h}]`; break; }
    }
    const sorted    = [...pg.plays].sort((a, b) => pbpParseClock(b.clock) - pbpParseClock(a.clock));
    const playNodes = sorted.map(play => {
      const clock     = pbpExtractClock(play.clock) || '0:00';
      const score     = pbpScoreText(play, awayAbbr, homeAbbr);
      const txt       = (play.text || '').trim().replace(/\s+/g, ' ');
      const formatted = score ? `${txt} - ${clock} (${score})` : `${txt} - ${clock}`;
      return makePbpNode(formatted, [], { scoring: !!play.scoringPlay, cssClass: bbClass(play) });
    });
    return makePbpNode(`${periodLabel}${periodScore}`, playNodes, { expanded: true });
  });
}

// ── Generic (NHL, soccer, others) ─────────────────────────────────────────

function buildGenericPbpTree(plays, awayAbbr, homeAbbr) {
  const periodOrder = [], periodGroups = {};
  for (const play of plays) {
    const pd    = play.period || {};
    const num   = pd.number || 1;
    const label = pd.displayValue || `Period ${num}`;
    const key   = `${num}:${label}`;
    if (!periodGroups[key]) { periodOrder.push(key); periodGroups[key] = { plays: [], label }; }
    periodGroups[key].plays.push(play);
  }
  return periodOrder.map(key => {
    const pg    = periodGroups[key];
    const goals = pg.plays.reduce((acc, p) => acc + Math.max(0, parseInt(p.scoreValue || 0, 10)), 0);
    let periodScore = '';
    for (const p of [...pg.plays].reverse()) {
      const a = pbpSafeInt(p.awayScore), h = pbpSafeInt(p.homeScore);
      if (a != null && h != null) { periodScore = `  [${awayAbbr} ${a} - ${homeAbbr} ${h}]`; break; }
    }
    const goalStr     = goals > 0 ? `  (${goals} goal${goals !== 1 ? 's' : ''})` : '';
    const periodLabel = `${pg.label}${goalStr}${periodScore}`;
    const playNodes   = pg.plays.map(play => {
      const txt   = play.text || 'Unknown play';
      const clock = pbpExtractClock(play.clock);
      const score = pbpScoreText(play, awayAbbr, homeAbbr);
      const formatted = (clock && clock !== '--:--')
        ? (score ? `${txt} - ${clock} (${score})` : `${txt} - ${clock}`)
        : (score ? `${txt} (${score})` : txt);
      const scoring = !!play.scoringPlay || (play.scoreValue || 0) > 0;
      return makePbpNode(formatted, [], { scoring, cssClass: scoring ? 'pbp-item--scoring' : '' });
    });
    return makePbpNode(periodLabel, playNodes, { expanded: true, scoring: goals > 0 });
  });
}

// ── DOM rendering ─────────────────────────────────────────────────────────

function renderPbpNodes(nodes, parentEl, level) {
  for (const node of nodes) {
    const hasChildren = node.children && node.children.length > 0;
    const item = document.createElement('div');
    item.className = 'pbp-item' + (node.cssClass ? ' ' + node.cssClass : '');
    item.setAttribute('role', 'treeitem');
    item.setAttribute('aria-level', String(level + 1));
    item.setAttribute('tabindex', '-1');
    item.style.setProperty('--level', level);
    item.dataset.pbpId = node.id;
    if (hasChildren) item.setAttribute('aria-expanded', node.expanded ? 'true' : 'false');

    const inner = document.createElement('div');
    inner.className = 'pbp-item-inner';
    const toggleOrSpacer = document.createElement('span');
    toggleOrSpacer.setAttribute('aria-hidden', 'true');
    if (hasChildren) {
      toggleOrSpacer.className = 'pbp-toggle';
      toggleOrSpacer.textContent = node.expanded ? '▼' : '▶';
    } else {
      toggleOrSpacer.className = 'pbp-toggle-spacer';
    }
    inner.appendChild(toggleOrSpacer);
    const labelEl = document.createElement('span');
    labelEl.className = 'pbp-label';
    labelEl.textContent = node.label;
    inner.appendChild(labelEl);
    item.appendChild(inner);

    if (hasChildren) {
      const group = document.createElement('div');
      group.setAttribute('role', 'group');
      group.className = 'pbp-children';
      if (!node.expanded) group.hidden = true;
      renderPbpNodes(node.children, group, level + 1);
      item.appendChild(group);
    }
    parentEl.appendChild(item);
  }
}

// ── Keyboard navigation ───────────────────────────────────────────────────

function pbpGetVisibleItems(treeEl) {
  return Array.from(treeEl.querySelectorAll('[role="treeitem"]')).filter(el => {
    let node = el.parentElement;
    while (node && node !== treeEl) {
      if (node.getAttribute('role') === 'group' && node.hidden) return false;
      node = node.parentElement;
    }
    return true;
  });
}

function pbpGetSelected(treeEl) {
  return treeEl.querySelector('[role="treeitem"][aria-selected="true"]');
}

function pbpSetSelected(item, treeEl) {
  const prev = pbpGetSelected(treeEl);
  if (prev) {
    prev.removeAttribute('aria-selected');
    prev.setAttribute('tabindex', '-1');
  }
  if (item) {
    item.setAttribute('aria-selected', 'true');
    item.setAttribute('tabindex', '0');
    item.focus();
  }
}

function pbpToggle(item) {
  const expanded = item.getAttribute('aria-expanded');
  if (expanded === null) return;
  const group  = item.querySelector(':scope > [role="group"]');
  const toggle = item.querySelector(':scope > .pbp-item-inner > .pbp-toggle');
  if (expanded === 'true') {
    item.setAttribute('aria-expanded', 'false');
    if (group)  group.hidden = true;
    if (toggle) toggle.textContent = '▶';
    announceToScreenReader(`Collapsed ${item.querySelector('.pbp-label')?.textContent || ''}`);
  } else {
    item.setAttribute('aria-expanded', 'true');
    if (group)  group.hidden = false;
    if (toggle) toggle.textContent = '▼';
    announceToScreenReader(`Expanded ${item.querySelector('.pbp-label')?.textContent || ''}`);
  }
}

function pbpParentItem(item, treeEl) {
  let node = item.parentElement;
  while (node && node !== treeEl) {
    if (node.getAttribute('role') === 'treeitem') return node;
    node = node.parentElement;
  }
  return null;
}

function attachPbpKeyboard(treeEl) {
  treeEl.addEventListener('keydown', e => {
    const visible = pbpGetVisibleItems(treeEl);
    if (!visible.length) return;
    // Prefer the actually-focused item; fall back to aria-selected or first item
    const active = document.activeElement;
    const current = (active && treeEl.contains(active) && active.getAttribute('role') === 'treeitem')
      ? active
      : (pbpGetSelected(treeEl) || visible[0]);
    const idx     = visible.indexOf(current);

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        if (idx < visible.length - 1) pbpSetSelected(visible[idx + 1], treeEl);
        break;
      case 'ArrowUp':
        e.preventDefault();
        if (idx > 0) pbpSetSelected(visible[idx - 1], treeEl);
        break;
      case 'ArrowRight':
        e.preventDefault();
        if (current.getAttribute('aria-expanded') === 'false') {
          pbpToggle(current);
        } else if (current.getAttribute('aria-expanded') === 'true') {
          const newVisible = pbpGetVisibleItems(treeEl);
          const ni = newVisible.indexOf(current);
          if (ni < newVisible.length - 1) pbpSetSelected(newVisible[ni + 1], treeEl);
        }
        break;
      case 'ArrowLeft':
        e.preventDefault();
        if (current.getAttribute('aria-expanded') === 'true') {
          pbpToggle(current);
        } else {
          const parent = pbpParentItem(current, treeEl);
          if (parent) pbpSetSelected(parent, treeEl);
        }
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        pbpToggle(current);
        break;
      case 'Home':
        e.preventDefault();
        pbpSetSelected(visible[0], treeEl);
        break;
      case 'End':
        e.preventDefault();
        pbpSetSelected(visible[visible.length - 1], treeEl);
        break;
    }
  });

  treeEl.addEventListener('click', e => {
    const item = e.target.closest('[role="treeitem"]');
    if (!item) return;
    pbpSetSelected(item, treeEl);
    pbpToggle(item);
  });
}

// ── Entry point ───────────────────────────────────────────────────────────

function renderPlayByPlay(details, sport, container) {
  const plays = details.plays;
  if (!plays || !plays.length) return;

  const [awayAbbr, homeAbbr] = pbpGetTeamLabels(details);
  const BASKETBALL = ['nba', 'ncaam', 'ncaawb', 'wnba', 'ncaaw'];
  const FOOTBALL   = ['nfl', 'ncaaf'];

  let nodes;
  if (sport === 'mlb') {
    nodes = buildBaseballPbpTree(plays, awayAbbr, homeAbbr);
  } else if (FOOTBALL.includes(sport)) {
    nodes = buildFootballPbpTree(plays, awayAbbr, homeAbbr);
  } else if (BASKETBALL.includes(sport)) {
    nodes = buildBasketballPbpTree(plays, awayAbbr, homeAbbr);
  } else {
    nodes = buildGenericPbpTree(plays, awayAbbr, homeAbbr);
  }
  if (!nodes || !nodes.length) return;

  const section = document.createElement('section');
  section.className = 'pbp-section';
  const h3 = document.createElement('h3');
  h3.textContent = `Play-by-Play (${plays.length} plays)`;
  section.appendChild(h3);

  const treeEl = document.createElement('div');
  treeEl.className = 'pbp-tree';
  treeEl.setAttribute('role', 'tree');
  treeEl.setAttribute('aria-label', 'Play by play');

  _pbpNodeId = 0;
  renderPbpNodes(nodes, treeEl, 0);
  // Give the first item tabindex="0" so Tab enters the tree on the first item
  const firstItem = treeEl.querySelector('[role="treeitem"]');
  if (firstItem) firstItem.setAttribute('tabindex', '0');
  attachPbpKeyboard(treeEl);

  section.appendChild(treeEl);
  container.appendChild(section);
}

/* ── Standings ───────────────────────────────────────────────────────────── */

async function loadStandings(sport) {
  const sportConfig = SPORTS.find(s => s.key === sport);
  if (sportConfig && !sportConfig.hasStandings) {
    document.getElementById('scores-content').innerHTML = '<p class="no-games">Standings not available for this sport.</p>';
    return;
  }
  showLoading('scores-content');
  try {
    const standings = await apiFetch(`standings/${sport.toUpperCase()}`);
    renderStandings(standings, sport);
  } catch (err) {
    showError('scores-content', err.message);
  }
}

function renderStandings(standings, sport) {
  const container = document.getElementById('scores-content');
  container.innerHTML = '';

  if (!standings || !standings.length) {
    container.innerHTML = '<p class="no-games">No standings data available.</p>';
    return;
  }

  // Group by division
  const byDivision = {};
  standings.forEach(team => {
    const div = team.division || 'Standings';
    if (!byDivision[div]) byDivision[div] = [];
    byDivision[div].push(team);
  });

  Object.entries(byDivision).forEach(([divName, teams]) => {
    const divId = 'div-' + divName.replace(/\s+/g, '-').replace(/[^A-Za-z0-9-]/g, '');
    const section = document.createElement('section');
    section.className = 'standings-division';
    section.setAttribute('aria-labelledby', divId);

    const h3 = document.createElement('h3');
    h3.id = divId;
    h3.textContent = divName;
    section.appendChild(h3);

    const table = document.createElement('table');
    table.className = 'standings-table';
    table.setAttribute('aria-label', `${divName} standings`);
    table.innerHTML = `<thead><tr>
      <th scope="col">Team</th>
      <th scope="col">W</th>
      <th scope="col">L</th>
      <th scope="col">PCT</th>
      <th scope="col">GB</th>
      <th scope="col">Streak</th>
    </tr></thead>`;

    const tbody = document.createElement('tbody');
    teams.forEach(team => {
      const tr = document.createElement('tr');
      const tName = escapeHtml(team.team_name || '');
      const teamLink = team.team_id
        ? `<a href="#schedule/${escapeHtml(sport)}/${escapeHtml(team.team_id)}" class="team-link">${tName}</a>`
        : tName;
      tr.innerHTML = `
        <td>${teamLink}</td>
        <td>${escapeHtml(String(team.wins ?? ''))}</td>
        <td>${escapeHtml(String(team.losses ?? ''))}</td>
        <td>${escapeHtml(team.win_percentage || '')}</td>
        <td>${escapeHtml(team.games_back || '—')}</td>
        <td>${escapeHtml(team.streak || '—')}</td>`;
      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    section.appendChild(table);
    container.appendChild(section);
  });
}

/* ── Team schedule ───────────────────────────────────────────────────────── */

async function loadTeamSchedule(sport, teamId, season) {
  showView('schedule');
  showLoading('schedule-content');

  let endpoint = `schedule/${sport.toUpperCase()}/${teamId}`;
  if (season) endpoint += `?season=${encodeURIComponent(season)}`;

  try {
    const schedule = await apiFetch(endpoint);
    renderTeamSchedule(schedule, sport, teamId);
  } catch (err) {
    showError('schedule-content', err.message);
  }
}

function renderTeamSchedule(schedule, sport, teamId) {
  const container = document.getElementById('schedule-content');
  container.innerHTML = '';

  if (!schedule || !schedule.length) {
    container.innerHTML = '<p>No games found for this team and season.</p>';
    return;
  }

  // Update heading
  const first = schedule[0];
  const heading = document.getElementById('schedule-heading');
  if (heading) heading.textContent = (first.opponent ? `Schedule` : 'Team Schedule');

  const wrapper = document.createElement('div');
  wrapper.className = 'table-wrapper';

  const table = document.createElement('table');
  table.className = 'schedule-table';
  table.setAttribute('aria-label', 'Team schedule');
  table.innerHTML = `<thead><tr>
    <th scope="col">Date</th>
    <th scope="col"></th>
    <th scope="col">Opponent</th>
    <th scope="col">Score / Time</th>
    <th scope="col">Venue</th>
  </tr></thead>`;

  const tbody = document.createElement('tbody');
  schedule.forEach(game => {
    const tr = document.createElement('tr');
    if (game.is_today) tr.className = 'today-row';

    const isFinal = (game.status || '').toLowerCase().includes('final');
    const resultOrTime = (isFinal && (game.away_score || game.home_score))
      ? `${escapeHtml(game.away_score || '')} – ${escapeHtml(game.home_score || '')}`
      : escapeHtml(game.time || game.status || 'TBD');

    const statusCls = isFinal ? 'status-final' : 'status-upcoming';

    tr.innerHTML = `
      <td>${escapeHtml(game.date_display || '')}</td>
      <td>${escapeHtml(game.home_away || '')}</td>
      <td>${escapeHtml(game.opponent || '')}</td>
      <td class="${statusCls}">${resultOrTime}</td>
      <td>${escapeHtml(game.venue || '')}</td>`;

    if (game.game_id) {
      tr.style.cursor = 'pointer';
      tr.setAttribute('tabindex', '0');
      tr.addEventListener('click', () => navigate(`game/${sport}/${game.game_id}`));
      tr.addEventListener('keydown', e => { if (e.key === 'Enter') navigate(`game/${sport}/${game.game_id}`); });
    }
    tbody.appendChild(tr);
  });

  table.appendChild(tbody);
  wrapper.appendChild(table);
  container.appendChild(wrapper);
}

/* ── News ────────────────────────────────────────────────────────────────── */

async function loadNews(sport) {
  showLoading('scores-content');
  try {
    const articles = await apiFetch(`news/${sport.toUpperCase()}?limit=20`);
    renderNews(articles, 'scores-content');
  } catch (err) {
    showError('scores-content', err.message);
  }
}

function renderNews(articles, containerId) {
  const container = document.getElementById(containerId);
  container.innerHTML = '';

  if (!articles || !articles.length) {
    container.innerHTML = '<p class="no-games">No news articles available.</p>';
    return;
  }

  const ul = document.createElement('ul');
  ul.className = 'news-list';
  ul.setAttribute('aria-label', 'News articles');

  articles.forEach(article => {
    const li = document.createElement('li');
    li.className = 'news-article';
    const url = escapeHtml(article.web_url || article.mobile_url || '#');
    const headline = escapeHtml(article.headline || 'No headline');
    const desc     = escapeHtml(article.description || '');
    const byline   = article.byline ? `<span class="byline">${escapeHtml(article.byline)}</span>` : '';
    const pubDate  = article.published ? `<time>${escapeHtml(formatPublishedDate(article.published))}</time>` : '';

    li.innerHTML = `
      <article>
        <h3><a href="${url}" target="_blank" rel="noopener noreferrer">${headline}</a></h3>
        ${desc ? `<p class="news-description">${desc}</p>` : ''}
        <footer class="news-meta">${byline}${pubDate}</footer>
      </article>`;
    ul.appendChild(li);
  });

  container.appendChild(ul);
}

function formatPublishedDate(dateStr) {
  if (!dateStr) return '';
  try {
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  } catch (_) { return dateStr; }
}

/* ── Statistics ──────────────────────────────────────────────────────────── */

async function loadStatistics(sport) {
  const sportConfig = SPORTS.find(s => s.key === sport);
  if (sportConfig && !sportConfig.hasStats) {
    document.getElementById('scores-content').innerHTML = '<p class="no-games">Statistics not available for this sport in the web app.</p>';
    return;
  }
  showLoading('scores-content');
  try {
    const data = await apiFetch(`statistics/${sport.toUpperCase()}`);
    renderStatistics(data, 'scores-content');
  } catch (err) {
    showError('scores-content', err.message);
  }
}

function renderStatistics(data, containerId) {
  const container = document.getElementById(containerId);
  container.innerHTML = '';

  const playerStats = Array.isArray(data) ? data : (data?.player_stats || []);
  const teamStats   = data?.team_stats || [];

  if (!playerStats.length && !teamStats.length) {
    container.innerHTML = '<p class="no-games">No statistics data available.</p>';
    return;
  }

  const grid = document.createElement('div');
  grid.className = 'stats-grid';

  const renderCategory = cat => {
    const div = document.createElement('div');
    div.className = 'stats-category';
    const title = document.createElement('div');
    title.className = 'stats-category-title';
    title.textContent = cat.category || cat.category_name || 'Stats';
    div.appendChild(title);

    const stats = cat.stats || cat.leaders || [];
    if (stats.length) {
      const table = document.createElement('table');
      table.className = 'stats-table';
      table.setAttribute('aria-label', title.textContent);
      const tbody = document.createElement('tbody');
      stats.slice(0, 10).forEach(s => {
        const tr = document.createElement('tr');
        const name  = escapeHtml(s.player_name || s.name || s.athlete?.displayName || '');
        const team  = escapeHtml(s.team || '');
        const val   = escapeHtml(s.value || s.displayValue || '');
        tr.innerHTML = `<td>${name}${team ? ` <small style="color:var(--color-text-muted)">${team}</small>` : ''}</td><td>${val}</td>`;
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      div.appendChild(table);
    }
    return div;
  };

  [...playerStats, ...teamStats].forEach(cat => grid.appendChild(renderCategory(cat)));
  container.appendChild(grid);
}

/* ── Soccer Hub ──────────────────────────────────────────────────────────── */

function renderSoccerHub() {
  currentSoccerLeague = null;
  showView('soccer');
  updateDateDisplays();

  const content = document.getElementById('soccer-content');
  content.innerHTML = '';

  const grid = document.createElement('div');
  grid.className = 'soccer-league-grid';
  grid.setAttribute('role', 'list');

  SOCCER_LEAGUES.forEach(league => {
    const tile = document.createElement('article');
    tile.className = 'soccer-league-tile';
    tile.setAttribute('role', 'listitem');
    tile.setAttribute('tabindex', '0');
    tile.innerHTML = `<h3>${escapeHtml(league.name)}</h3><span class="league-abbr">${escapeHtml(league.shortName)}</span>`;
    tile.addEventListener('click',   () => navigate(`soccer/${league.key}`));
    tile.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); navigate(`soccer/${league.key}`); } });
    grid.appendChild(tile);
  });

  content.appendChild(grid);
}

async function loadSoccerScores(leagueKey) {
  currentSoccerLeague = leagueKey;
  showView('soccer');
  updateDateDisplays();

  const container = document.getElementById('soccer-content');
  const leagueInfo = SOCCER_LEAGUES.find(l => l.key === leagueKey);
  showLoading('soccer-content');

  try {
    const games = await apiFetch(`soccer/${leagueKey}?date=${formatDateForESPN(currentDate)}`);

    container.innerHTML = '';

    const backBtn = document.createElement('button');
    backBtn.className = 'back-btn secondary-back';
    backBtn.textContent = '← All Leagues';
    backBtn.setAttribute('aria-label', 'Back to league selection');
    backBtn.addEventListener('click', () => navigate('soccer'));
    container.appendChild(backBtn);

    const heading = document.createElement('h3');
    heading.textContent = leagueInfo ? leagueInfo.name : leagueKey;
    heading.style.cssText = 'margin: 0.5rem 0; font-size: 1.1rem;';
    container.appendChild(heading);

    const gamesDiv = document.createElement('div');
    container.appendChild(gamesDiv);
    renderGames(games, gamesDiv, 'soccer');
  } catch (err) {
    showError('soccer-content', err.message);
  }
}

/* ── Golf Hub ────────────────────────────────────────────────────────────── */

async function loadGolfHub() {
  showView('golf');
  const content = document.getElementById('golf-content');

  content.innerHTML = `
    <div class="golf-tabs" role="tablist" aria-label="Golf tours">
      <button role="tab" aria-selected="${currentGolfTour === 'pga'}" aria-controls="golf-leaderboard" data-tour="pga" class="${currentGolfTour === 'pga' ? 'active' : ''}">PGA Tour</button>
      <button role="tab" aria-selected="${currentGolfTour === 'lpga'}" aria-controls="golf-leaderboard" data-tour="lpga" class="${currentGolfTour === 'lpga' ? 'active' : ''}">LPGA Tour</button>
    </div>
    <div id="golf-leaderboard" role="tabpanel">
      <div class="loading-spinner" role="status"><span class="visually-hidden">Loading…</span></div>
    </div>`;

  content.querySelectorAll('[role="tab"]').forEach(tab => {
    tab.addEventListener('click', () => {
      currentGolfTour = tab.dataset.tour;
      loadGolfHub();
    });
  });

  try {
    const data = await apiFetch(`golf/${currentGolfTour}`);
    renderGolfLeaderboard(data, document.getElementById('golf-leaderboard'));
  } catch (_) {
    const lb = document.getElementById('golf-leaderboard');
    if (lb) lb.innerHTML = '<p class="error-message">Could not load golf leaderboard.</p>';
  }
}

function renderGolfLeaderboard(data, container) {
  if (!container) return;
  container.innerHTML = '';

  const events = data.events || [];
  if (!events.length) {
    container.innerHTML = '<p class="no-games">No active golf events found.</p>';
    return;
  }

  events.forEach(evt => {
    const h3 = document.createElement('h3');
    h3.textContent = escapeHtml(evt.name || 'Tournament');
    h3.style.cssText = 'margin: 0.75rem 0 0.5rem; font-size: 1rem;';
    container.appendChild(h3);

    const comps = evt.competitions || [];
    if (!comps.length) return;
    const competitors = (comps[0].competitors || []).slice(0, 20);
    if (!competitors.length) return;

    const table = document.createElement('table');
    table.className = 'golf-leaderboard';
    table.setAttribute('aria-label', `${evt.name || 'Tournament'} leaderboard`);
    table.innerHTML = `<thead><tr>
      <th scope="col">Pos</th>
      <th scope="col">Player</th>
      <th scope="col">Score</th>
      <th scope="col">Today</th>
    </tr></thead>`;

    const tbody = document.createElement('tbody');
    competitors.forEach(comp => {
      const tr = document.createElement('tr');
      const athlete = comp.athlete || {};
      const pos     = escapeHtml(comp.status?.position?.displayName || comp.status?.position || '');
      const name    = escapeHtml(athlete.displayName || comp.displayName || '');
      const score   = escapeHtml(comp.score?.displayValue || comp.score || '');
      const linescores = comp.linescores || [];
      const today   = linescores.length ? escapeHtml(linescores[linescores.length - 1]?.displayValue || '') : '';
      tr.innerHTML = `<td>${pos}</td><td>${name}</td><td>${score}</td><td>${today}</td>`;
      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    container.appendChild(table);
  });
}

/* ── Live Scores ─────────────────────────────────────────────────────────── */

async function loadLiveScores() {
  showView('live');
  showLoading('live-content');
  stopAutoRefresh();

  try {
    const games = await apiFetch('live');
    renderLiveScores(games);
  } catch (err) {
    showError('live-content', err.message);
  }

  if (settings.autoRefreshSeconds > 0) startLiveCountdown();
}

function renderLiveScores(games) {
  const container = document.getElementById('live-content');
  container.innerHTML = '';

  if (!games || !games.length) {
    container.innerHTML = '<p class="no-games">No live games right now.</p>';
    return;
  }

  const byLeague = {};
  games.forEach(game => {
    const k = game.league || 'Other';
    if (!byLeague[k]) byLeague[k] = [];
    byLeague[k].push(game);
  });

  Object.entries(byLeague).forEach(([league, leagueGames]) => {
    const section = document.createElement('section');
    section.className = 'game-section section-live';
    const h3 = document.createElement('h3');
    h3.className = 'game-section-header';
    h3.textContent = league;
    section.appendChild(h3);

    const list = document.createElement('div');
    list.setAttribute('role', 'list');
    list.className = 'games-card-list';

    leagueGames.forEach(game => {
      const card = document.createElement('article');
      card.className = 'game-card live-game-card';
      card.setAttribute('role', 'listitem');

      const teams = game.teams || [];
      const t0 = teams[0] || {};
      const t1 = teams[1] || {};

      card.innerHTML = `
        <div class="game-card-teams">
          <div class="team"><span class="team-name">${escapeHtml(t0.name || '')}</span><span class="score">${escapeHtml(t0.score || '')}</span></div>
          <div class="team"><span class="team-name">${escapeHtml(t1.name || '')}</span><span class="score">${escapeHtml(t1.score || '')}</span></div>
        </div>
        <div class="game-card-meta">
          <span class="status-badge status-live">${escapeHtml(game.status || 'Live')}</span>
          ${game.recent_play ? `<span class="recent-play">${escapeHtml(game.recent_play)}</span>` : ''}
        </div>`;

      if (game.id) {
        card.setAttribute('tabindex', '0');
        card.style.cursor = 'pointer';
        const sportKey = (game.league || 'nfl').toLowerCase();
        card.addEventListener('click',   () => navigate(`game/${sportKey}/${game.id}`));
        card.addEventListener('keydown', e => { if (e.key === 'Enter') navigate(`game/${sportKey}/${game.id}`); });
      }
      list.appendChild(card);
    });

    section.appendChild(list);
    container.appendChild(section);
  });
}

/* ── Keyboard shortcuts ──────────────────────────────────────────────────── */

function handleKeyboardShortcut(e) {
  if (e.altKey) {
    switch (e.key.toLowerCase()) {
      case 'h': navigate('home');      e.preventDefault(); break;
      case 'v': cycleViewMode();       e.preventDefault(); break;
      case 'g': openSettings();        e.preventDefault(); break;
    }
  }
  if (e.key === 'Escape') {
    const anyModalOpen = !document.getElementById('date-picker-modal').hidden
                      || !document.getElementById('settings-panel').hidden;
    if (anyModalOpen) { closeAllModals(); e.preventDefault(); }
  }
}

/* ── Event listeners setup ───────────────────────────────────────────────── */

function setupEventListeners() {
  // Header buttons
  document.getElementById('home-btn')?.addEventListener('click', () => navigate('home'));
  document.getElementById('settings-btn')?.addEventListener('click', openSettings);

  // Date nav — home view
  document.getElementById('prev-date-btn')?.addEventListener('click', goToPrevDate);
  document.getElementById('next-date-btn')?.addEventListener('click', goToNextDate);
  document.getElementById('current-date-btn')?.addEventListener('click', openDatePicker);

  // Date nav — scores view (class-based, multiple instances)
  document.querySelectorAll('.prev-date-btn-scores').forEach(b => b.addEventListener('click', goToPrevDate));
  document.querySelectorAll('.next-date-btn-scores').forEach(b => b.addEventListener('click', goToNextDate));
  document.querySelectorAll('.date-display-scores').forEach(b => b.addEventListener('click', openDatePicker));

  // Date nav — soccer view
  document.querySelectorAll('.prev-date-btn-soccer').forEach(b => b.addEventListener('click', goToPrevDate));
  document.querySelectorAll('.next-date-btn-soccer').forEach(b => b.addEventListener('click', goToNextDate));
  document.querySelectorAll('.date-display-soccer').forEach(b => b.addEventListener('click', openDatePicker));

  // View mode toggle
  document.querySelectorAll('.view-mode-btn').forEach(btn => {
    btn.addEventListener('click', () => switchGameView(btn.dataset.view));
  });

  // Sub-nav tabs
  document.querySelectorAll('.subnav-tab').forEach(tab => {
    tab.addEventListener('click', () => switchSection(tab.dataset.section));
  });

  // Football nav
  document.getElementById('season-type-select')?.addEventListener('change', e => {
    currentFootball.seasonType = parseInt(e.target.value, 10);
    currentFootball.week = null;
    const wd = document.getElementById('week-display');
    if (wd) wd.textContent = '';
    if (currentSport) loadScores(currentSport, currentDate);
  });

  document.getElementById('prev-week-btn')?.addEventListener('click', () => {
    if (currentFootball.week == null) currentFootball.week = 1;
    if (currentFootball.week > 1) {
      currentFootball.week--;
      if (currentSport) loadScores(currentSport, currentDate);
    }
  });

  document.getElementById('next-week-btn')?.addEventListener('click', () => {
    currentFootball.week = (currentFootball.week == null ? 1 : currentFootball.week) + 1;
    if (currentSport) loadScores(currentSport, currentDate);
  });

  // Back button delegation
  document.addEventListener('click', e => {
    const btn = e.target.closest('.back-btn[data-target]');
    if (!btn) return;
    const target = btn.dataset.target;
    if (target === 'home') navigate('home');
    else if (target === 'scores' && currentSport) navigate(`scores/${currentSport}`);
  });

  // Date picker modal
  document.getElementById('date-picker-ok')?.addEventListener('click', confirmDatePicker);
  document.getElementById('date-picker-cancel')?.addEventListener('click', closeDatePicker);
  document.getElementById('date-picker-input')?.addEventListener('keydown', e => {
    if (e.key === 'Enter') confirmDatePicker();
    if (e.key === 'Escape') closeDatePicker();
  });
  document.getElementById('date-picker-modal')?.addEventListener('click', e => {
    if (e.target === e.currentTarget) closeDatePicker();
  });

  // Settings
  document.getElementById('settings-close')?.addEventListener('click', closeSettings);
  document.getElementById('settings-panel')?.addEventListener('click', e => {
    if (e.target === e.currentTarget) closeSettings();
  });

  // Live refresh button
  document.getElementById('live-refresh-btn')?.addEventListener('click', loadLiveScores);

  // Global keyboard shortcuts
  document.addEventListener('keydown', handleKeyboardShortcut);

  // Hash change
  window.addEventListener('hashchange', handleRoute);
}

/* ── Service Worker ──────────────────────────────────────────────────────── */

function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/service-worker.js').catch(() => { /* silent */ });
    });
  }
}

/* ── Init ────────────────────────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
  applyTheme();
  setupEventListeners();
  registerServiceWorker();
  handleRoute();
});
