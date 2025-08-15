// ESPN API Integration for Live Sports Data
// This module handles all ESPN API calls and data processing

class ESPNApi {
    constructor() {
        this.baseUrl = 'https://site.api.espn.com/apis/site/v2/sports';
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
    }

    // Core fetch method with caching and error handling
    async fetchWithCache(url, cacheKey, timeout = 10000) {
        // Check cache first
        const cached = this.cache.get(cacheKey);
        if (cached && (Date.now() - cached.timestamp) < this.cacheTimeout) {
            return cached.data;
        }

        try {
            console.log(`Fetching: ${url}`);
            
            // Create abort controller for timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);

            const response = await fetch(url, {
                signal: controller.signal,
                headers: {
                    'User-Agent': 'Sports Scores Web App'
                }
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            // Cache the response
            this.cache.set(cacheKey, {
                data: data,
                timestamp: Date.now()
            });

            return data;
        } catch (error) {
            console.error(`API Error for ${cacheKey}:`, error);
            
            // Return cached data if available, even if expired
            const cached = this.cache.get(cacheKey);
            if (cached) {
                console.log(`Using stale cache for ${cacheKey}`);
                return cached.data;
            }
            
            throw error;
        }
    }

    // Get available leagues
    async getLeagues() {
        return ['MLB', 'NFL', 'NBA', 'NHL'];
    }

    // Get games/scores for a specific league and date
    async getScores(league, date) {
        const dateStr = date.toISOString().split('T')[0].replace(/-/g, '');
        let url, cacheKey;

        switch (league.toUpperCase()) {
            case 'MLB':
                url = `${this.baseUrl}/baseball/mlb/scoreboard?dates=${dateStr}`;
                cacheKey = `mlb-scores-${dateStr}`;
                break;
            case 'NFL':
                url = `${this.baseUrl}/football/nfl/scoreboard?dates=${dateStr}`;
                cacheKey = `nfl-scores-${dateStr}`;
                break;
            case 'NBA':
                url = `${this.baseUrl}/basketball/nba/scoreboard?dates=${dateStr}`;
                cacheKey = `nba-scores-${dateStr}`;
                break;
            case 'NHL':
                url = `${this.baseUrl}/hockey/nhl/scoreboard?dates=${dateStr}`;
                cacheKey = `nhl-scores-${dateStr}`;
                break;
            default:
                throw new Error(`Unsupported league: ${league}`);
        }

        const data = await this.fetchWithCache(url, cacheKey);
        return this.processScoreboardData(data, league);
    }

    // Process scoreboard data into consistent format
    processScoreboardData(data, league) {
        if (!data || !data.events) {
            return [];
        }

        return data.events.map(event => {
            const competition = event.competitions?.[0];
            const competitors = competition?.competitors || [];
            const status = competition?.status;

            // Get team information
            const teams = competitors.map(comp => ({
                name: comp.team?.displayName || 'Unknown Team',
                abbreviation: comp.team?.abbreviation || '',
                score: comp.score || '0',
                record: comp.records?.[0]?.summary || '',
                isWinner: comp.winner || false
            }));

            return {
                id: event.id,
                name: event.name || `${teams[0]?.name || ''} vs ${teams[1]?.name || ''}`,
                shortName: event.shortName || '',
                date: event.date,
                status: {
                    type: status?.type?.name || 'unknown',
                    description: status?.type?.description || 'Unknown',
                    detail: status?.type?.detail || '',
                    shortDetail: status?.type?.shortDetail || '',
                    completed: status?.type?.completed || false
                },
                teams: teams,
                venue: competition?.venue?.fullName || '',
                league: league.toUpperCase(),
                broadcasts: competition?.broadcasts || []
            };
        });
    }

    // Get game details by ID
    async getGameDetailsById(gameId, league) {
        let url, cacheKey;
        
        switch (league.toUpperCase()) {
            case 'MLB':
                url = `${this.baseUrl}/baseball/mlb/summary?event=${gameId}`;
                cacheKey = `mlb-game-${gameId}`;
                break;
            case 'NFL':
                url = `${this.baseUrl}/football/nfl/summary?event=${gameId}`;
                cacheKey = `nfl-game-${gameId}`;
                break;
            case 'NBA':
                url = `${this.baseUrl}/basketball/nba/summary?event=${gameId}`;
                cacheKey = `nba-game-${gameId}`;
                break;
            case 'NHL':
                url = `${this.baseUrl}/hockey/nhl/summary?event=${gameId}`;
                cacheKey = `nhl-game-${gameId}`;
                break;
            default:
                throw new Error(`Unsupported league: ${league}`);
        }

        const data = await this.fetchWithCache(url, cacheKey);
        return this.processGameDetails(data, league);
    }

    // Process game details into consistent format
    processGameDetails(data, league) {
        const header = data.header || {};
        const competition = header.competitions?.[0] || {};
        const competitors = competition.competitors || [];
        
        const details = {
            name: header.league?.name || league,
            gameTitle: competitors.map(c => c.team?.displayName).join(' vs ') || 'Game',
            status: competition.status?.type?.description || '',
            venue: competition.venue?.fullName || '',
            date: header.competitions?.[0]?.date || '',
            weather: competition.weather?.displayValue || '',
            attendance: competition.attendance || '',
            officials: competition.officials || [],
            broadcasts: competition.broadcasts || []
        };

        // Add sport-specific data
        if (league.toUpperCase() === 'MLB' && data.plays) {
            details.innings = this.processBaseballInnings(data.plays);
        } else if (league.toUpperCase() === 'NFL' && data.drives) {
            details.drives = this.processFootballDrives(data.drives);
        }

        return details;
    }

    // Process baseball innings from plays data
    processBaseballInnings(plays) {
        if (!Array.isArray(plays)) return [];

        const inningsMap = {};
        plays.forEach(play => {
            const inningNum = play.inning || 0;
            const half = play.halfInning || 'unknown';
            
            if (!inningsMap[inningNum]) {
                inningsMap[inningNum] = { number: inningNum };
            }
            
            if (!inningsMap[inningNum][half]) {
                inningsMap[inningNum][half] = {
                    batters: [],
                    score: `${play.awayScore || 0}-${play.homeScore || 0}`
                };
            }
            
            inningsMap[inningNum][half].batters.push({
                name: play.batter?.athlete?.displayName || 'Unknown Batter',
                result: play.result || 'Unknown'
            });
            
            if (play.pitcher?.athlete?.displayName) {
                inningsMap[inningNum][half].pitcher = play.pitcher.athlete.displayName;
            }
        });

        return Object.values(inningsMap);
    }

    // Process football drives data
    processFootballDrives(drives) {
        if (!Array.isArray(drives)) return [];

        return drives.map(drive => ({
            id: drive.id,
            quarter: drive.period || 0,
            team: drive.team?.displayName || 'Unknown Team',
            plays: drive.plays?.length || 0,
            yards: drive.yards || 0,
            timeOfPossession: drive.timeOfPossession || '',
            result: drive.result || 'Unknown'
        }));
    }

    // Get standings for a league
    async getStandings(league) {
        let url, cacheKey;
        
        switch (league.toUpperCase()) {
            case 'MLB':
                url = `${this.baseUrl}/baseball/mlb/standings`;
                cacheKey = 'mlb-standings';
                break;
            case 'NFL':
                url = `${this.baseUrl}/football/nfl/standings`;
                cacheKey = 'nfl-standings';
                break;
            case 'NBA':
                url = `${this.baseUrl}/basketball/nba/standings`;
                cacheKey = 'nba-standings';
                break;
            case 'NHL':
                url = `${this.baseUrl}/hockey/nhl/standings`;
                cacheKey = 'nhl-standings';
                break;
            default:
                throw new Error(`Unsupported league: ${league}`);
        }

        const data = await this.fetchWithCache(url, cacheKey);
        return this.processStandingsData(data, league);
    }

    // Process standings data into consistent format
    processStandingsData(data, league) {
        if (!data || !data.children) return [];

        const standings = [];
        data.children.forEach(division => {
            const divisionName = division.name || 'Unknown Division';
            const teams = division.standings?.entries || [];
            
            teams.forEach((entry, index) => {
                const team = entry.team || {};
                const stats = entry.stats || [];
                
                const wins = this.findStat(stats, 'wins') || '0';
                const losses = this.findStat(stats, 'losses') || '0';
                const winPercent = this.findStat(stats, 'winPercent') || '0.000';
                const gamesBehind = this.findStat(stats, 'gamesBehind') || '0';
                
                standings.push({
                    division: divisionName,
                    rank: index + 1,
                    team: team.displayName || 'Unknown Team',
                    abbreviation: team.abbreviation || '',
                    wins: wins,
                    losses: losses,
                    winPercent: winPercent,
                    gamesBehind: gamesBehind,
                    logo: team.logo || ''
                });
            });
        });

        return standings;
    }

    // Helper to find a specific stat by name
    findStat(stats, statName) {
        const stat = stats.find(s => s.name === statName);
        return stat ? stat.displayValue : null;
    }

    // Get news headlines for a league
    async getNews(league) {
        let url, cacheKey;
        
        switch (league.toUpperCase()) {
            case 'MLB':
                url = `${this.baseUrl}/baseball/mlb/news`;
                cacheKey = 'mlb-news';
                break;
            case 'NFL':
                url = `${this.baseUrl}/football/nfl/news`;
                cacheKey = 'nfl-news';
                break;
            case 'NBA':
                url = `${this.baseUrl}/basketball/nba/news`;
                cacheKey = 'nba-news';
                break;
            case 'NHL':
                url = `${this.baseUrl}/hockey/nhl/news`;
                cacheKey = 'nhl-news';
                break;
            default:
                throw new Error(`Unsupported league: ${league}`);
        }

        const data = await this.fetchWithCache(url, cacheKey);
        return this.processNewsData(data);
    }

    // Process news data into consistent format
    processNewsData(data) {
        if (!data || !data.articles) return [];

        return data.articles.slice(0, 10).map(article => ({
            headline: article.headline || 'No headline',
            description: article.description || '',
            published: article.published || '',
            source: article.source || 'ESPN',
            url: article.links?.web?.href || ''
        }));
    }

    // Clear cache
    clearCache() {
        this.cache.clear();
    }
}

// Export for use in other modules
window.ESPNApi = ESPNApi;