// Sports Scores Web App - Main Application Logic
// Follows the same navigation structure as the Windows version:
// Home (league selection) → League (scores + date nav) → Game Details

class SportsApp {
    constructor() {
        this.currentView = 'home';
        this.currentLeague = null;
        this.currentDate = new Date();
        this.currentGameId = null;
        this.api = new ESPNApi();
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.setupKeyboardNavigation();
        this.hideLoading();
        await this.showHome();
    }

    setupEventListeners() {
        // Navigation buttons
        document.getElementById('back-to-home').addEventListener('click', () => this.showHome());
        document.getElementById('back-to-scores').addEventListener('click', () => this.showLeague(this.currentLeague));
        document.getElementById('refresh-scores').addEventListener('click', () => this.refreshScores());
        document.getElementById('refresh-game').addEventListener('click', () => this.refreshGameDetails());
        
        // Date navigation
        document.getElementById('prev-date').addEventListener('click', () => this.changeDate(-1));
        document.getElementById('next-date').addEventListener('click', () => this.changeDate(1));
        
        // Modal close buttons
        document.getElementById('close-news').addEventListener('click', () => this.hideNewsModal());
        document.getElementById('close-standings').addEventListener('click', () => this.hideStandingsModal());
        
        // Close modals on escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideAllModals();
            }
        });
    }

    setupKeyboardNavigation() {
        // Enhanced keyboard navigation for lists
        document.addEventListener('keydown', (e) => {
            const activeList = document.querySelector('.option-list:not(.hidden), .details-list:not(.hidden)');
            if (!activeList) return;
            
            const items = Array.from(activeList.querySelectorAll('li'));
            const currentIndex = items.findIndex(item => item.classList.contains('focused'));
            
            switch(e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    this.focusListItem(items, currentIndex + 1);
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    this.focusListItem(items, currentIndex - 1);
                    break;
                case 'Home':
                    e.preventDefault();
                    this.focusListItem(items, 0);
                    break;
                case 'End':
                    e.preventDefault();
                    this.focusListItem(items, items.length - 1);
                    break;
                case 'Enter':
                case ' ':
                    e.preventDefault();
                    const focusedItem = items[currentIndex];
                    if (focusedItem) {
                        focusedItem.click();
                    }
                    break;
            }
        });
    }

    focusListItem(items, index) {
        if (index < 0) index = items.length - 1;
        if (index >= items.length) index = 0;
        
        // Remove focus from all items
        items.forEach(item => item.classList.remove('focused'));
        
        // Add focus to target item
        if (items[index]) {
            items[index].classList.add('focused');
            items[index].scrollIntoView({ block: 'nearest' });
        }
    }

    // Show/Hide utility methods
    showSection(sectionId) {
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.add('hidden');
        });
        document.getElementById(sectionId).classList.remove('hidden');
    }

    showLoading() {
        document.getElementById('loading').classList.remove('hidden');
        document.getElementById('error-message').classList.add('hidden');
    }

    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
    }

    showError(message) {
        console.error(message);
        this.hideLoading();
        document.getElementById('error-text').textContent = message;
        document.getElementById('error-message').classList.remove('hidden');
    }

    hideAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.add('hidden');
        });
    }

    hideNewsModal() {
        document.getElementById('news-modal').classList.add('hidden');
    }

    hideStandingsModal() {
        document.getElementById('standings-modal').classList.add('hidden');
    }

    // Main navigation methods
    async showHome() {
        this.currentView = 'home';
        this.currentLeague = null;
        this.showSection('home-section');
        
        this.showLoading();
        try {
            const leagues = await this.api.getLeagues();
            this.displayLeagues(leagues);
        } catch (error) {
            this.showError('Failed to load leagues: ' + error.message);
        }
        this.hideLoading();
    }

    displayLeagues(leagues) {
        const leagueList = document.getElementById('league-list');
        leagueList.innerHTML = '';
        
        leagues.forEach((league, index) => {
            const li = document.createElement('li');
            li.textContent = league;
            li.tabIndex = 0;
            li.addEventListener('click', () => this.showLeague(league));
            li.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.showLeague(league);
                }
            });
            leagueList.appendChild(li);
        });
        
        // Focus first item
        if (leagueList.firstChild) {
            this.focusListItem([...leagueList.children], 0);
        }
    }

    async showLeague(league) {
        this.currentView = 'league';
        this.currentLeague = league;
        this.showSection('league-section');
        
        document.getElementById('league-title').textContent = `${league} Scores`;
        this.updateDateDisplay();
        
        await this.loadScores();
    }

    async loadScores() {
        this.showLoading();
        try {
            const games = await this.api.getScores(this.currentLeague, this.currentDate);
            this.displayScores(games);
        } catch (error) {
            this.showError('Failed to load scores: ' + error.message);
        }
        this.hideLoading();
    }

    displayScores(games) {
        const scoresList = document.getElementById('scores-list');
        scoresList.innerHTML = '';
        
        if (!games || games.length === 0) {
            const li = document.createElement('li');
            li.textContent = `No games scheduled for ${this.formatDate(this.currentDate)}`;
            li.className = 'no-games';
            scoresList.appendChild(li);
        } else {
            games.forEach(game => {
                const li = document.createElement('li');
                li.textContent = this.formatGameDisplay(game);
                li.tabIndex = 0;
                li.addEventListener('click', () => this.showGameDetails(game.id));
                li.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        this.showGameDetails(game.id);
                    }
                });
                scoresList.appendChild(li);
            });
        }
        
        // Add special options
        this.addSpecialOptions(scoresList);
        
        // Focus first item
        if (scoresList.firstChild) {
            this.focusListItem([...scoresList.children], 0);
        }
    }

    addSpecialOptions(scoresList) {
        // News option
        const newsLi = document.createElement('li');
        newsLi.textContent = '--- News ---';
        newsLi.classList.add('special-option');
        newsLi.tabIndex = 0;
        newsLi.addEventListener('click', () => this.showNewsModal());
        newsLi.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.showNewsModal();
            }
        });
        scoresList.appendChild(newsLi);
        
        // Standings option
        const standingsLi = document.createElement('li');
        standingsLi.textContent = '--- Standings ---';
        standingsLi.classList.add('special-option');
        standingsLi.tabIndex = 0;
        standingsLi.addEventListener('click', () => this.showStandingsModal());
        standingsLi.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.showStandingsModal();
            }
        });
        scoresList.appendChild(standingsLi);
    }

    formatGameDisplay(game) {
        if (!game || !game.teams || game.teams.length < 2) {
            return game.name || 'Unknown Game';
        }
        
        const team1 = game.teams[0];
        const team2 = game.teams[1];
        const status = game.status ? game.status.description : 'Unknown Status';
        
        return `${team1.name} ${team1.score} - ${team2.score} ${team2.name} (${status})`;
    }

    async showGameDetails(gameId) {
        this.currentView = 'game';
        this.currentGameId = gameId;
        this.showSection('game-section');
        
        await this.loadGameDetails();
    }

    async loadGameDetails() {
        this.showLoading();
        try {
            const details = await this.api.getGameDetailsById(this.currentGameId, this.currentLeague);
            this.displayGameDetails(details);
        } catch (error) {
            this.showError('Failed to load game details: ' + error.message);
        }
        this.hideLoading();
    }

    displayGameDetails(details) {
        const detailsList = document.getElementById('game-details-list');
        const gameTitle = document.getElementById('game-title');
        
        gameTitle.textContent = details.gameTitle || details.name || 'Game Details';
        detailsList.innerHTML = '';
        
        // Add basic details
        if (details.status) {
            this.addDetailItem(detailsList, 'Status', details.status);
        }
        if (details.venue) {
            this.addDetailItem(detailsList, 'Venue', details.venue);
        }
        if (details.weather) {
            this.addDetailItem(detailsList, 'Weather', details.weather);
        }
        
        // Add sport-specific details
        if (details.innings && details.innings.length > 0) {
            this.addBaseballDetails(detailsList, details.innings);
        } else if (details.drives && details.drives.length > 0) {
            this.addFootballDetails(detailsList, details.drives);
        }
        
        // Focus first item
        if (detailsList.firstChild) {
            this.focusListItem([...detailsList.children], 0);
        }
    }

    addDetailItem(list, label, value) {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${label}:</strong> ${value}`;
        li.tabIndex = 0;
        list.appendChild(li);
    }

    addBaseballDetails(list, innings) {
        innings.forEach(inning => {
            if (inning.top) {
                this.addInningHalf(list, `Top ${inning.number}`, inning.top);
            }
            if (inning.bottom) {
                this.addInningHalf(list, `Bottom ${inning.number}`, inning.bottom);
            }
        });
    }

    addInningHalf(list, halfLabel, halfData) {
        const li = document.createElement('li');
        li.className = 'inning-half';
        li.tabIndex = 0;
        
        const scoreLabel = halfData.score ? `Score: ${halfData.score}` : '';
        const pitcherLabel = halfData.pitcher ? `Pitcher: ${halfData.pitcher}` : '';
        
        li.innerHTML = `<strong>${halfLabel}</strong> — ${scoreLabel} ${pitcherLabel ? '— ' + pitcherLabel : ''}`;
        
        list.appendChild(li);
    }

    addFootballDetails(list, drives) {
        drives.forEach(quarter => {
            if (quarter.drives && quarter.drives.length > 0) {
                quarter.drives.forEach((drive, index) => {
                    this.addDriveDetail(list, `Q${quarter.number} Drive ${index + 1}`, drive);
                });
            }
        });
    }

    addDriveDetail(list, driveLabel, drive) {
        const li = document.createElement('li');
        li.className = 'drive-detail';
        li.tabIndex = 0;
        li.innerHTML = `<strong>${driveLabel}:</strong> ${drive.description || 'Drive details'}`;
        list.appendChild(li);
    }

    // Modal methods
    async showNewsModal() {
        this.showLoading();
        try {
            const news = await this.api.getNews(this.currentLeague);
            this.displayNews(news);
            document.getElementById('news-modal').classList.remove('hidden');
        } catch (error) {
            this.showError('Failed to load news: ' + error.message);
        }
        this.hideLoading();
    }

    displayNews(newsItems) {
        const newsList = document.getElementById('news-list');
        newsList.innerHTML = '';
        
        if (!newsItems || newsItems.length === 0) {
            const li = document.createElement('li');
            li.textContent = 'No news available';
            newsList.appendChild(li);
            return;
        }
        
        newsItems.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${item.headline}</strong><br><small>${item.description}</small>`;
            li.tabIndex = 0;
            newsList.appendChild(li);
        });
    }

    async showStandingsModal() {
        this.showLoading();
        try {
            const standings = await this.api.getStandings(this.currentLeague);
            this.displayStandings(standings);
            document.getElementById('standings-modal').classList.remove('hidden');
        } catch (error) {
            this.showError('Failed to load standings: ' + error.message);
        }
        this.hideLoading();
    }

    displayStandings(standings) {
        const standingsContent = document.getElementById('standings-content');
        standingsContent.innerHTML = '';
        
        if (!standings || standings.length === 0) {
            standingsContent.innerHTML = '<p>No standings available</p>';
            return;
        }
        
        // Create table
        const table = document.createElement('table');
        table.setAttribute('role', 'table');
        table.setAttribute('aria-label', `${this.currentLeague} Standings`);
        
        // Create header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        headerRow.setAttribute('role', 'row');
        
        ['Team', 'Wins', 'Losses', 'Win %'].forEach(header => {
            const th = document.createElement('th');
            th.setAttribute('role', 'columnheader');
            th.textContent = header;
            headerRow.appendChild(th);
        });
        
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // Create body
        const tbody = document.createElement('tbody');
        standings.forEach(team => {
            const row = document.createElement('tr');
            row.setAttribute('role', 'row');
            
            [team.team, team.wins, team.losses, team.winPercent].forEach(value => {
                const td = document.createElement('td');
                td.setAttribute('role', 'cell');
                td.textContent = value;
                row.appendChild(td);
            });
            
            tbody.appendChild(row);
        });
        
        table.appendChild(tbody);
        standingsContent.appendChild(table);
    }

    // Date navigation methods
    updateDateDisplay() {
        document.getElementById('current-date').textContent = this.formatDate(this.currentDate);
    }

    formatDate(date) {
        return date.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    changeDate(days) {
        const newDate = new Date(this.currentDate);
        newDate.setDate(newDate.getDate() + days);
        this.currentDate = newDate;
        this.updateDateDisplay();
        this.loadScores();
    }

    refreshScores() {
        this.loadScores();
    }

    refreshGameDetails() {
        this.loadGameDetails();
    }
}

// Global retry function for error recovery
function retryLoad() {
    if (window.sportsApp) {
        if (window.sportsApp.currentView === 'home') {
            window.sportsApp.showHome();
        } else if (window.sportsApp.currentView === 'league') {
            window.sportsApp.loadScores();
        } else if (window.sportsApp.currentView === 'game') {
            window.sportsApp.loadGameDetails();
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.sportsApp = new SportsApp();
});

// Handle page visibility changes for performance
document.addEventListener('visibilitychange', () => {
    if (window.sportsApp && !document.hidden) {
        // Optionally refresh data when page becomes visible again
        console.log('Page visible again');
    }
});