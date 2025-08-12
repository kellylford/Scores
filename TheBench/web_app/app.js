// Sports Scores Web App - Main Application Logic
// Handles UI interactions, data display, and accessibility features

class SportsApp {
    constructor() {
        this.currentSection = 'standings';
        this.currentSortColumn = null;
        this.currentSortDirection = 'asc';
        this.updateInterval = null;
        this.keyboardNavigationEnabled = true;
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.setupKeyboardNavigation();
        await this.loadInitialData();
        this.startAutoUpdate();
    }

    setupEventListeners() {
        // Navigation buttons
        document.querySelectorAll('.nav-button').forEach(button => {
            button.addEventListener('click', (e) => {
                this.switchSection(e.target.id.replace('nav-', ''));
            });
        });

        // Division filter
        const divisionSelect = document.getElementById('division-select');
        divisionSelect.addEventListener('change', () => {
            this.filterStandings(divisionSelect.value);
        });

        // Game status filter
        const gameStatusSelect = document.getElementById('game-status-select');
        gameStatusSelect.addEventListener('change', () => {
            this.filterGames(gameStatusSelect.value);
        });

        // Team selection
        const teamSelect = document.getElementById('team-select');
        teamSelect.addEventListener('change', async () => {
            if (teamSelect.value) {
                await this.loadTeamStats(teamSelect.value);
            }
        });

        // Player search
        const playerSearch = document.getElementById('player-search');
        let searchTimeout;
        playerSearch.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.searchPlayers(playerSearch.value);
            }, 300);
        });

        // Table sorting
        this.setupTableSorting();
    }

    setupKeyboardNavigation() {
        // Enhanced keyboard navigation for lists and tables
        document.addEventListener('keydown', (e) => {
            if (!this.keyboardNavigationEnabled) return;

            const activeElement = document.activeElement;
            const isInList = activeElement.closest('.games-list');
            const isInTable = activeElement.closest('.data-table');

            if (isInList) {
                this.handleListNavigation(e, activeElement);
            } else if (isInTable) {
                this.handleTableNavigation(e, activeElement);
            }
        });
    }

    handleListNavigation(e, activeElement) {
        const currentItem = activeElement.closest('.game-item') || activeElement.closest('li');
        if (!currentItem) return;

        const list = currentItem.closest('ul');
        const items = Array.from(list.querySelectorAll('li'));
        const currentIndex = items.indexOf(currentItem);

        let targetIndex = currentIndex;

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                targetIndex = Math.min(currentIndex + 1, items.length - 1);
                break;
            case 'ArrowUp':
                e.preventDefault();
                targetIndex = Math.max(currentIndex - 1, 0);
                break;
            case 'Home':
                e.preventDefault();
                targetIndex = 0;
                break;
            case 'End':
                e.preventDefault();
                targetIndex = items.length - 1;
                break;
            default:
                return;
        }

        if (targetIndex !== currentIndex) {
            const targetItem = items[targetIndex];
            const focusableElement = targetItem.querySelector('button, a, [tabindex]') || targetItem;
            
            // Make item focusable if it isn't already
            if (!focusableElement.hasAttribute('tabindex')) {
                focusableElement.setAttribute('tabindex', '0');
            }
            
            focusableElement.focus();
            
            // Announce to screen readers
            this.announceNavigation(`Item ${targetIndex + 1} of ${items.length}`);
        }
    }

    handleTableNavigation(e, activeElement) {
        const currentCell = activeElement.closest('th, td');
        if (!currentCell) return;

        const table = currentCell.closest('table');
        const currentRow = currentCell.closest('tr');
        const rows = Array.from(table.querySelectorAll('tr'));
        const cells = Array.from(currentRow.querySelectorAll('th, td'));
        
        const rowIndex = rows.indexOf(currentRow);
        const cellIndex = cells.indexOf(currentCell);

        let targetRow = rowIndex;
        let targetCell = cellIndex;

        switch (e.key) {
            case 'ArrowRight':
                e.preventDefault();
                targetCell = Math.min(cellIndex + 1, cells.length - 1);
                break;
            case 'ArrowLeft':
                e.preventDefault();
                targetCell = Math.max(cellIndex - 1, 0);
                break;
            case 'ArrowDown':
                e.preventDefault();
                targetRow = Math.min(rowIndex + 1, rows.length - 1);
                break;
            case 'ArrowUp':
                e.preventDefault();
                targetRow = Math.max(rowIndex - 1, 0);
                break;
            case 'Home':
                e.preventDefault();
                if (e.ctrlKey) {
                    targetRow = 0;
                    targetCell = 0;
                } else {
                    targetCell = 0;
                }
                break;
            case 'End':
                e.preventDefault();
                if (e.ctrlKey) {
                    targetRow = rows.length - 1;
                    targetCell = Array.from(rows[rows.length - 1].querySelectorAll('th, td')).length - 1;
                } else {
                    targetCell = cells.length - 1;
                }
                break;
            default:
                return;
        }

        const targetRowElement = rows[targetRow];
        const targetCells = Array.from(targetRowElement.querySelectorAll('th, td'));
        const targetCellElement = targetCells[Math.min(targetCell, targetCells.length - 1)];

        if (targetCellElement) {
            // Make cell focusable
            if (!targetCellElement.hasAttribute('tabindex')) {
                targetCellElement.setAttribute('tabindex', '0');
            }
            
            targetCellElement.focus();
            
            // Announce cell content to screen readers
            const content = targetCellElement.textContent.trim();
            const header = targetCellElement.closest('table').querySelector(`thead th:nth-child(${targetCell + 1})`);
            const headerText = header ? header.textContent.trim() : '';
            
            this.announceNavigation(`${headerText}: ${content}`);
        }
    }

    setupTableSorting() {
        document.querySelectorAll('.sortable').forEach(header => {
            header.addEventListener('click', () => {
                this.sortTable(header);
            });
            
            header.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.sortTable(header);
                }
            });
        });
    }

    sortTable(headerElement) {
        const table = headerElement.closest('table');
        const headerRow = headerElement.closest('tr');
        const headers = Array.from(headerRow.querySelectorAll('th'));
        const columnIndex = headers.indexOf(headerElement);
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));

        // Determine sort direction
        const currentSort = headerElement.getAttribute('aria-sort');
        let newDirection = 'ascending';
        
        if (currentSort === 'ascending') {
            newDirection = 'descending';
        }

        // Clear all sort indicators
        headers.forEach(h => h.setAttribute('aria-sort', 'none'));
        
        // Set current sort indicator
        headerElement.setAttribute('aria-sort', newDirection);

        // Sort rows
        const sortedRows = rows.sort((a, b) => {
            const aCell = a.querySelectorAll('td, th')[columnIndex];
            const bCell = b.querySelectorAll('td, th')[columnIndex];
            
            if (!aCell || !bCell) return 0;
            
            const aValue = this.parseCellValue(aCell.textContent.trim());
            const bValue = this.parseCellValue(bCell.textContent.trim());
            
            let comparison = 0;
            if (typeof aValue === 'number' && typeof bValue === 'number') {
                comparison = aValue - bValue;
            } else {
                comparison = aValue.toString().localeCompare(bValue.toString());
            }
            
            return newDirection === 'ascending' ? comparison : -comparison;
        });

        // Re-append sorted rows
        sortedRows.forEach(row => tbody.appendChild(row));
        
        // Announce sort to screen readers
        const headerText = headerElement.textContent.replace(/[▲▼]/g, '').trim();
        this.announceNavigation(`Table sorted by ${headerText}, ${newDirection}`);
    }

    parseCellValue(value) {
        // Try to parse as number
        const numValue = parseFloat(value.replace(/[,%$]/g, ''));
        if (!isNaN(numValue)) {
            return numValue;
        }
        
        // Handle special cases
        if (value === '-') return 0;
        if (value.includes('%')) {
            const pctValue = parseFloat(value.replace('%', ''));
            return isNaN(pctValue) ? value : pctValue;
        }
        
        return value;
    }

    async loadInitialData() {
        this.showLoading();
        
        try {
            // Load standings first (default view)
            await this.loadStandings();
            
            // Load teams for team selection dropdown
            await this.loadTeams();
            
            this.hideLoading();
        } catch (error) {
            this.showError('Failed to load initial data', error);
        }
    }

    async loadStandings() {
        try {
            const standings = await window.espnApi.getMLBStandings();
            this.displayStandings(standings);
            this.updateLastUpdateTime('standings');
        } catch (error) {
            console.error('Error loading standings:', error);
            this.showError('Failed to load standings', error);
        }
    }

    displayStandings(standings) {
        const tbody = document.getElementById('standings-tbody');
        tbody.innerHTML = '';

        standings.forEach((team, index) => {
            const row = document.createElement('tr');
            row.setAttribute('role', 'row');
            row.innerHTML = `
                <th role="rowheader" scope="row" tabindex="0" class="team-cell">
                    ${team.team}
                </th>
                <td role="gridcell" tabindex="0" class="numeric-column">${team.wins}</td>
                <td role="gridcell" tabindex="0" class="numeric-column">${team.losses}</td>
                <td role="gridcell" tabindex="0" class="numeric-column">${team.winPercent.toFixed(3)}</td>
                <td role="gridcell" tabindex="0" class="numeric-column">${team.gamesBehind}</td>
                <td role="gridcell" tabindex="0">${team.division}</td>
            `;
            tbody.appendChild(row);
        });

        // Store original data for filtering
        this.standingsData = standings;
    }

    filterStandings(division) {
        if (!this.standingsData) return;

        const filteredData = division === 'all' 
            ? this.standingsData 
            : this.standingsData.filter(team => team.division === division);

        this.displayStandings(filteredData);
        
        // Announce filter change
        const message = division === 'all' 
            ? 'Showing all divisions' 
            : `Filtered to ${division} division, ${filteredData.length} teams`;
        this.announceNavigation(message);
    }

    async loadScores() {
        try {
            const games = await window.espnApi.getMLBScores();
            this.displayScores(games);
            this.updateLastUpdateTime('scores');
        } catch (error) {
            console.error('Error loading scores:', error);
            this.showError('Failed to load scores', error);
        }
    }

    displayScores(games) {
        const gamesList = document.getElementById('games-list');
        gamesList.innerHTML = '';

        if (games.length === 0) {
            const emptyItem = document.createElement('li');
            emptyItem.className = 'game-item';
            emptyItem.innerHTML = `
                <div class="game-info">
                    <p>No games scheduled for today</p>
                </div>
            `;
            gamesList.appendChild(emptyItem);
            return;
        }

        games.forEach((game, index) => {
            const gameItem = document.createElement('li');
            gameItem.className = 'game-item';
            gameItem.setAttribute('tabindex', '0');
            gameItem.setAttribute('role', 'listitem');
            gameItem.setAttribute('aria-label', this.getGameAriaLabel(game));

            const statusClass = game.status.type;
            const statusText = this.getStatusDisplayText(game.status);

            gameItem.innerHTML = `
                <div class="game-team away">
                    <div class="team-name">${game.awayTeam.name}</div>
                    <div class="team-score">${game.awayTeam.score || '0'}</div>
                </div>
                
                <div class="game-info">
                    <div class="game-status ${statusClass}">${statusText}</div>
                    <div class="game-time">${this.formatGameTime(game)}</div>
                </div>
                
                <div class="game-team home">
                    <div class="team-name">${game.homeTeam.name}</div>
                    <div class="team-score">${game.homeTeam.score || '0'}</div>
                </div>
            `;

            gamesList.appendChild(gameItem);
        });

        // Store original data for filtering
        this.gamesData = games;
    }

    getGameAriaLabel(game) {
        const status = this.getStatusDisplayText(game.status);
        if (game.status.completed) {
            return `Final: ${game.awayTeam.name} ${game.awayTeam.score}, ${game.homeTeam.name} ${game.homeTeam.score}`;
        } else if (game.status.type === 'live') {
            return `Live: ${game.awayTeam.name} ${game.awayTeam.score}, ${game.homeTeam.name} ${game.homeTeam.score}, ${status}`;
        } else {
            return `Scheduled: ${game.awayTeam.name} at ${game.homeTeam.name}, ${this.formatGameTime(game)}`;
        }
    }

    getStatusDisplayText(status) {
        switch (status.type) {
            case 'live':
                return status.displayClock || 'Live';
            case 'final':
                return 'Final';
            case 'scheduled':
                return 'Scheduled';
            default:
                return status.type;
        }
    }

    formatGameTime(game) {
        const time = new Date(game.startTime);
        return time.toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            timeZoneName: 'short'
        });
    }

    filterGames(status) {
        if (!this.gamesData) return;

        const filteredData = status === 'all' 
            ? this.gamesData 
            : this.gamesData.filter(game => game.status.type === status);

        this.displayScores(filteredData);
        
        // Announce filter change
        const message = status === 'all' 
            ? 'Showing all games' 
            : `Filtered to ${status} games, ${filteredData.length} games`;
        this.announceNavigation(message);
    }

    async loadTeams() {
        try {
            const teams = await window.espnApi.getMLBTeams();
            this.populateTeamSelect(teams);
            this.teamsData = teams;
        } catch (error) {
            console.error('Error loading teams:', error);
        }
    }

    populateTeamSelect(teams) {
        const teamSelect = document.getElementById('team-select');
        
        // Clear existing options (except the first one)
        while (teamSelect.children.length > 1) {
            teamSelect.removeChild(teamSelect.lastChild);
        }

        teams.forEach(team => {
            const option = document.createElement('option');
            option.value = team.id;
            option.textContent = team.name;
            teamSelect.appendChild(option);
        });
    }

    async loadTeamStats(teamId) {
        try {
            const stats = await window.espnApi.getTeamStats(teamId);
            this.displayTeamStats(stats);
            this.updateLastUpdateTime('teams');
            
            // Show the stats container
            const container = document.getElementById('team-stats-container');
            container.classList.remove('hidden');
        } catch (error) {
            console.error('Error loading team stats:', error);
            this.showError('Failed to load team statistics', error);
        }
    }

    displayTeamStats(stats) {
        const tbody = document.getElementById('team-stats-tbody');
        tbody.innerHTML = '';

        stats.forEach(stat => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <th role="rowheader" scope="row" tabindex="0">${stat.name}</th>
                <td role="gridcell" tabindex="0">${stat.value}</td>
                <td role="gridcell" tabindex="0">${stat.rank || 'N/A'}</td>
            `;
            tbody.appendChild(row);
        });
    }

    async searchPlayers(searchTerm) {
        try {
            const players = await window.espnApi.getPlayerStats(searchTerm);
            this.displayPlayerStats(players);
            this.updateLastUpdateTime('players');
        } catch (error) {
            console.error('Error searching players:', error);
        }
    }

    displayPlayerStats(players) {
        const tbody = document.getElementById('player-stats-tbody');
        tbody.innerHTML = '';

        players.forEach(player => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <th role="rowheader" scope="row" tabindex="0">${player.name}</th>
                <td role="gridcell" tabindex="0">${player.team}</td>
                <td role="gridcell" tabindex="0">${player.position}</td>
                <td role="gridcell" tabindex="0" class="numeric-column">${player.avg}</td>
                <td role="gridcell" tabindex="0" class="numeric-column">${player.homeRuns}</td>
                <td role="gridcell" tabindex="0" class="numeric-column">${player.rbi}</td>
                <td role="gridcell" tabindex="0" class="numeric-column">${player.obp}</td>
            `;
            tbody.appendChild(row);
        });
    }

    switchSection(sectionName) {
        // Update navigation
        document.querySelectorAll('.nav-button').forEach(btn => {
            btn.classList.remove('active');
            btn.setAttribute('aria-pressed', 'false');
        });
        
        const activeButton = document.getElementById(`nav-${sectionName}`);
        activeButton.classList.add('active');
        activeButton.setAttribute('aria-pressed', 'true');

        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.add('hidden');
        });

        // Show target section
        const targetSection = document.getElementById(`${sectionName}-section`);
        targetSection.classList.remove('hidden');

        // Load data if needed
        this.currentSection = sectionName;
        this.loadSectionData(sectionName);

        // Announce section change
        const sectionTitle = targetSection.querySelector('h2').textContent;
        this.announceNavigation(`Switched to ${sectionTitle} section`);
        
        // Focus the section
        targetSection.focus();
    }

    async loadSectionData(sectionName) {
        switch (sectionName) {
            case 'standings':
                if (!this.standingsData) {
                    await this.loadStandings();
                }
                break;
            case 'scores':
                await this.loadScores();
                break;
            case 'teams':
                if (!this.teamsData) {
                    await this.loadTeams();
                }
                break;
            case 'players':
                if (!document.getElementById('player-stats-tbody').hasChildNodes()) {
                    await this.searchPlayers('');
                }
                break;
        }
    }

    startAutoUpdate() {
        // Update scores every 30 seconds if on scores section
        this.updateInterval = setInterval(() => {
            if (this.currentSection === 'scores') {
                this.loadScores();
            }
        }, 30000);
    }

    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    showLoading() {
        document.getElementById('loading').classList.remove('hidden');
        document.getElementById('error-message').classList.add('hidden');
    }

    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
    }

    showError(message, error) {
        console.error(message, error);
        
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('error-text').textContent = `${message}. ${error.message || 'Please try again.'}`;
        document.getElementById('error-message').classList.remove('hidden');
        
        // Announce error to screen readers
        this.announceNavigation(`Error: ${message}`);
    }

    updateLastUpdateTime(section) {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            second: '2-digit'
        });
        
        const updateElement = document.getElementById(`${section}-last-update`);
        if (updateElement) {
            updateElement.textContent = `Last updated: ${timeString}`;
        }
    }

    announceNavigation(message) {
        // Create temporary element for screen reader announcements
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        
        // Remove after announcement
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }
}

// Retry function for error recovery
window.retryLoad = async function() {
    if (window.sportsApp) {
        await window.sportsApp.loadInitialData();
    }
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.sportsApp = new SportsApp();
});

// Handle page visibility changes for performance
document.addEventListener('visibilitychange', () => {
    if (window.sportsApp) {
        if (document.hidden) {
            window.sportsApp.stopAutoUpdate();
        } else {
            window.sportsApp.startAutoUpdate();
        }
    }
});
