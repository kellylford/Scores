// Sports Scores Web App - Following Original GUI Flow
// Flow: Home (select league) -> League (scores + date nav) -> Game Details

class SportsApp {
    constructor() {
        this.currentView = 'home';
        this.currentLeague = null;
        this.currentDate = new Date();
        this.currentGameId = null;
        this.stack = [];
        this.config = {
            'MLB': ['name', 'status', 'competitors'],
            'NFL': ['name', 'status', 'competitors'],
            'NBA': ['name', 'status', 'competitors'],
            'NHL': ['name', 'status', 'competitors']
        };
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.setupKeyboardNavigation();
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
        
        // Configuration
        document.getElementById('configure-details').addEventListener('click', () => this.showConfigModal());
        document.getElementById('save-config').addEventListener('click', () => this.saveConfig());
        document.getElementById('cancel-config').addEventListener('click', () => this.hideConfigModal());
        
        // Modal close buttons
        document.getElementById('close-news').addEventListener('click', () => this.hideNewsModal());
        document.getElementById('close-standings').addEventListener('click', () => this.hideStandingsModal());
        document.getElementById('close-config').addEventListener('click', () => this.hideConfigModal());
        
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

    async showHome() {
        this.currentView = 'home';
        this.stack = [];
        
        this.hideAllSections();
        document.getElementById('home-section').classList.remove('hidden');
        
        // Load leagues
        const leagues = await ESPNApi.getLeagues();
        const leagueList = document.getElementById('league-list');
        leagueList.innerHTML = '';
        
        leagues.forEach(league => {
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
        
        // Focus first league
        if (leagueList.firstChild) {
            this.focusListItem([...leagueList.children], 0);
        }
        
        this.hideLoading();
    }

    async showLeague(league) {
        this.currentView = 'league';
        this.currentLeague = league;
        this.currentDate = new Date(); // Reset to today
        
        this.hideAllSections();
        document.getElementById('league-section').classList.remove('hidden');
        document.getElementById('league-title').textContent = `${league} Scores`;
        
        await this.loadScores();
        this.hideLoading();
    }

    async loadScores() {
        this.showLoading();
        
        // Update date display
        const dateStr = this.currentDate.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        document.getElementById('current-date').textContent = dateStr;
        
        try {
            // Get scores for current date
            const scores = await ESPNApi.getScores(this.currentLeague, this.currentDate);
            const scoresList = document.getElementById('scores-list');
            scoresList.innerHTML = '';
            
            if (!scores || scores.length === 0) {
                const li = document.createElement('li');
                li.textContent = `No games scheduled for ${dateStr}`;
                li.classList.add('no-games');
                scoresList.appendChild(li);
            } else {
                scores.forEach(game => {
                    const li = document.createElement('li');
                    li.textContent = this.formatGameDisplay(game);
                    li.tabIndex = 0;
                    li.dataset.gameId = game.id;
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
            
            // Add News and Standings options for MLB
            if (this.currentLeague === 'MLB') {
                // Add news
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
                
                // Add standings
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
            
            // Focus first item
            if (scoresList.firstChild) {
                this.focusListItem([...scoresList.children], 0);
            }
            
        } catch (error) {
            this.showError('Failed to load scores: ' + error.message);
        }
        
        this.hideLoading();
    }

    formatGameDisplay(game) {
        let display = game.name || 'Game';
        
        // Add scores if available
        if (game.teams && game.teams.length >= 2) {
            const team1 = game.teams[0];
            const team2 = game.teams[1];
            
            if (team1.score !== undefined && team2.score !== undefined) {
                display += ` (${team1.abbreviation} ${team1.score} - ${team2.abbreviation} ${team2.score})`;
            }
        }
        
        // Add status/time
        if (game.status) {
            display += ` - ${game.status}`;
        } else if (game.startTime) {
            display += ` - ${game.startTime}`;
        }
        
        return display;
    }

    async showGameDetails(gameId) {
        this.currentView = 'game';
        this.currentGameId = gameId;
        this.stack.push({ view: 'league', league: this.currentLeague });
        
        this.hideAllSections();
        document.getElementById('game-section').classList.remove('hidden');
        
        await this.loadGameDetails();
        this.hideLoading();
    }

    async loadGameDetails() {
        this.showLoading();
        
        try {
            const gameDetails = await ESPNApi.getGameDetails(this.currentGameId, this.config[this.currentLeague]);
            const detailsList = document.getElementById('game-details-list');
            detailsList.innerHTML = '';
            
            // Set game title
            document.getElementById('game-title').textContent = gameDetails.name || 'Game Details';
            
            // Display configured details
            const configuredDetails = this.config[this.currentLeague] || ['name', 'status', 'competitors'];
            
            configuredDetails.forEach(detailType => {
                if (gameDetails[detailType]) {
                    const li = document.createElement('li');
                    li.innerHTML = `<strong>${this.formatDetailLabel(detailType)}:</strong> ${gameDetails[detailType]}`;
                    detailsList.appendChild(li);
                }
            });
            
            // Focus first detail
            if (detailsList.firstChild) {
                this.focusListItem([...detailsList.children], 0);
            }
            
        } catch (error) {
            this.showError('Failed to load game details: ' + error.message);
        }
        
        this.hideLoading();
    }

    formatDetailLabel(detailType) {
        const labels = {
            'name': 'Game',
            'status': 'Status',
            'competitors': 'Teams',
            'score': 'Score',
            'time': 'Time',
            'venue': 'Venue'
        };
        return labels[detailType] || detailType;
    }

    changeDate(days) {
        const newDate = new Date(this.currentDate);
        newDate.setDate(newDate.getDate() + days);
        this.currentDate = newDate;
        this.loadScores();
    }

    refreshScores() {
        this.loadScores();
    }

    refreshGameDetails() {
        this.loadGameDetails();
    }

    async showNewsModal() {
        try {
            const news = await ESPNApi.getNews(this.currentLeague);
            const newsList = document.getElementById('news-list');
            newsList.innerHTML = '';
            
            news.forEach(article => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <h3>${article.headline}</h3>
                    <p>${article.description || ''}</p>
                    ${article.url ? `<a href="${article.url}" target="_blank">Read more</a>` : ''}
                `;
                newsList.appendChild(li);
            });
            
            document.getElementById('news-modal').classList.remove('hidden');
            document.getElementById('close-news').focus();
            
        } catch (error) {
            this.showError('Failed to load news: ' + error.message);
        }
    }

    async showStandingsModal() {
        try {
            const standings = await ESPNApi.getStandings(this.currentLeague);
            const standingsContent = document.getElementById('standings-content');
            
            // Create standings table
            const table = document.createElement('table');
            table.className = 'standings-table';
            table.innerHTML = `
                <thead>
                    <tr>
                        <th>Team</th>
                        <th>Wins</th>
                        <th>Losses</th>
                        <th>Win %</th>
                    </tr>
                </thead>
                <tbody>
                    ${standings.map(team => `
                        <tr>
                            <td>${team.team}</td>
                            <td>${team.wins}</td>
                            <td>${team.losses}</td>
                            <td>${team.winPercent.toFixed(3)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            `;
            
            standingsContent.innerHTML = '';
            standingsContent.appendChild(table);
            
            document.getElementById('standings-modal').classList.remove('hidden');
            document.getElementById('close-standings').focus();
            
        } catch (error) {
            this.showError('Failed to load standings: ' + error.message);
        }
    }

    showConfigModal() {
        const configOptions = document.getElementById('config-options');
        const availableDetails = ['name', 'status', 'competitors', 'score', 'time', 'venue'];
        const currentConfig = this.config[this.currentLeague] || [];
        
        configOptions.innerHTML = '';
        
        availableDetails.forEach(detail => {
            const div = document.createElement('div');
            div.innerHTML = `
                <label>
                    <input type="checkbox" name="details" value="${detail}" 
                           ${currentConfig.includes(detail) ? 'checked' : ''}>
                    ${this.formatDetailLabel(detail)}
                </label>
            `;
            configOptions.appendChild(div);
        });
        
        document.getElementById('config-modal').classList.remove('hidden');
        document.getElementById('save-config').focus();
    }

    saveConfig() {
        const checkboxes = document.querySelectorAll('#config-options input[name="details"]:checked');
        const selectedDetails = Array.from(checkboxes).map(cb => cb.value);
        
        this.config[this.currentLeague] = selectedDetails;
        this.hideConfigModal();
        
        // Refresh game details if we're viewing them
        if (this.currentView === 'game') {
            this.loadGameDetails();
        }
    }

    hideNewsModal() {
        document.getElementById('news-modal').classList.add('hidden');
    }

    hideStandingsModal() {
        document.getElementById('standings-modal').classList.add('hidden');
    }

    hideConfigModal() {
        document.getElementById('config-modal').classList.add('hidden');
    }

    hideAllModals() {
        this.hideNewsModal();
        this.hideStandingsModal();
        this.hideConfigModal();
    }

    hideAllSections() {
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.add('hidden');
        });
    }

    showLoading() {
        document.getElementById('loading').classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
    }

    showError(message) {
        document.getElementById('error-text').textContent = message;
        document.getElementById('error-message').classList.remove('hidden');
        this.hideLoading();
    }

    hideError() {
        document.getElementById('error-message').classList.add('hidden');
    }
}

// Global retry function
function retryLoad() {
    document.getElementById('error-message').classList.add('hidden');
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
