// ESPN API Integration for Live Sports Data
// This module handles all ESPN API calls and data processing

class ESPNApi {
    constructor() {
        this.baseUrl = 'https://site.api.espn.com/apis/site/v2/sports';
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
    }

    // Get available leagues
    static async getLeagues() {
        // Return available leagues (ESPN API supports these)
        return ['MLB', 'NFL', 'NBA', 'NHL'];
    }

    // Get scores for a specific league and date
    static async getScores(league, date = new Date()) {
        try {
            const api = window.espnApi || new ESPNApi();
            
            switch(league) {
                case 'MLB':
                    return await api.getMLBScores(date);
                case 'NFL':
                    return await api.getNFLScores(date);
                case 'NBA':
                    return await api.getNBAScores(date);
                case 'NHL':
                    return await api.getNHLScores(date);
                default:
                    return [];
            }
        } catch (error) {
            console.error(`Error getting scores for ${league}:`, error);
            return [];
        }
    }

    // Get standings for a specific league
    static async getStandings(league) {
        try {
            const api = window.espnApi || new ESPNApi();
            
            switch(league) {
                case 'MLB':
                    return await api.getMLBStandings();
                case 'NFL':
                    return await api.getNFLStandings();
                case 'NBA':
                    return await api.getNBAStandings();
                case 'NHL':
                    return await api.getNHLStandings();
                default:
                    return [];
            }
        } catch (error) {
            console.error(`Error getting standings for ${league}:`, error);
            return [];
        }
    }

    // Get news for a specific league
    static async getNews(league) {
        try {
            const api = window.espnApi || new ESPNApi();
            return await api.getNewsForLeague(league);
        } catch (error) {
            console.error(`Error getting news for ${league}:`, error);
            return [];
        }
    }

    // Get game details
    static async getGameDetails(gameId, configuredDetails) {
        try {
            const api = window.espnApi || new ESPNApi();
            return await api.getGameDetailsById(gameId, configuredDetails);
        } catch (error) {
            console.error(`Error getting game details for ${gameId}:`, error);
            return { name: 'Game Details', status: 'Error loading details' };
        }
    }

    // Generic fetch with caching and error handling
    async fetchWithCache(url, cacheKey, forceRefresh = false) {
        const now = Date.now();
        
        // Check cache first
        if (!forceRefresh && this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (now - cached.timestamp < this.cacheTimeout) {
                return cached.data;
            }
        }

        try {
            console.log(`Fetching: ${url}`);
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Cache the result
            this.cache.set(cacheKey, {
                data: data,
                timestamp: now
            });
            
            return data;
        } catch (error) {
            console.error(`API Error for ${cacheKey}:`, error);
            
            // Return cached data if available, even if expired
            if (this.cache.has(cacheKey)) {
                console.log(`Returning stale cache for ${cacheKey}`);
                return this.cache.get(cacheKey).data;
            }
            
            throw error;
        }
    }

    // Get MLB standings
    async getMLBStandings() {
        const url = `${this.baseUrl}/baseball/mlb/standings`;
        const data = await this.fetchWithCache(url, 'mlb-standings');
        
        return this.processStandingsData(data);
    }

    // Process standings data into consistent format
    processStandingsData(data) {
        const standings = [];
        
        if (data && data.children) {
            data.children.forEach(conference => {
                if (conference.children) {
                    conference.children.forEach(division => {
                        const divisionName = division.name;
                        
                        if (division.standings && division.standings.entries) {
                            division.standings.entries.forEach(entry => {
                                const team = entry.team;
                                const stats = entry.stats;
                                
                                standings.push({
                                    team: team.displayName,
                                    abbreviation: team.abbreviation,
                                    wins: stats.find(s => s.name === 'wins')?.value || 0,
                                    losses: stats.find(s => s.name === 'losses')?.value || 0,
                                    winPercent: parseFloat(stats.find(s => s.name === 'winPercent')?.value || 0),
                                    gamesBehind: stats.find(s => s.name === 'gamesBehind')?.displayValue || '0',
                                    division: divisionName,
                                    logo: team.logo
                                });
                            });
                        }
                    });
                }
            });
        }
        
        return standings;
    }

    // Get today's MLB scores
    async getMLBScores() {
        const today = new Date().toISOString().split('T')[0].replace(/-/g, '');
        const url = `${this.baseUrl}/baseball/mlb/scoreboard?dates=${today}`;
        const data = await this.fetchWithCache(url, `mlb-scores-${today}`);
        
        return this.processScoresData(data);
    }

    // Process scores data
    processScoresData(data) {
        const games = [];
        
        if (data && data.events) {
            data.events.forEach(event => {
                const competition = event.competitions[0];
                const status = competition.status;
                const competitors = competition.competitors;
                
                if (competitors.length >= 2) {
                    const awayTeam = competitors.find(c => c.homeAway === 'away');
                    const homeTeam = competitors.find(c => c.homeAway === 'home');
                    
                    games.push({
                        id: event.id,
                        name: event.name,
                        shortName: event.shortName,
                        status: {
                            type: status.type.name.toLowerCase(),
                            displayClock: status.displayClock,
                            period: status.period,
                            completed: status.type.completed
                        },
                        awayTeam: {
                            name: awayTeam.team.displayName,
                            abbreviation: awayTeam.team.abbreviation,
                            score: awayTeam.score,
                            logo: awayTeam.team.logo
                        },
                        homeTeam: {
                            name: homeTeam.team.displayName,
                            abbreviation: homeTeam.team.abbreviation,
                            score: homeTeam.score,
                            logo: homeTeam.team.logo
                        },
                        startTime: new Date(event.date)
                    });
                }
            });
        }
        
        return games;
    }

    // Get MLB teams list
    async getMLBTeams() {
        const url = `${this.baseUrl}/baseball/mlb/teams`;
        const data = await this.fetchWithCache(url, 'mlb-teams');
        
        return this.processTeamsData(data);
    }

    // Process teams data
    processTeamsData(data) {
        const teams = [];
        
        if (data && data.sports && data.sports[0] && data.sports[0].leagues && data.sports[0].leagues[0]) {
            const league = data.sports[0].leagues[0];
            
            if (league.teams) {
                league.teams.forEach(teamData => {
                    const team = teamData.team;
                    teams.push({
                        id: team.id,
                        name: team.displayName,
                        abbreviation: team.abbreviation,
                        location: team.location,
                        nickname: team.name,
                        logo: team.logos ? team.logos[0]?.href : null,
                        color: team.color,
                        alternateColor: team.alternateColor
                    });
                });
            }
        }
        
        return teams.sort((a, b) => a.name.localeCompare(b.name));
    }

    // Get team statistics
    async getTeamStats(teamId) {
        const url = `${this.baseUrl}/baseball/mlb/teams/${teamId}/statistics`;
        const data = await this.fetchWithCache(url, `team-stats-${teamId}`);
        
        return this.processTeamStatsData(data);
    }

    // Process team stats data
    processTeamStatsData(data) {
        const stats = [];
        
        if (data && data.splits && data.splits.categories) {
            data.splits.categories.forEach(category => {
                if (category.stats) {
                    category.stats.forEach(stat => {
                        stats.push({
                            name: stat.displayName,
                            value: stat.displayValue,
                            rank: stat.rank || null,
                            category: category.displayName
                        });
                    });
                }
            });
        }
        
        return stats;
    }

    // Get player statistics (simplified - ESPN API has limited free access)
    async getPlayerStats(searchTerm = '') {
        // Note: ESPN's free API has limited player stats access
        // This is a simplified version that would work with expanded API access
        const mockPlayers = [
            {
                name: "Aaron Judge",
                team: "NYY",
                position: "RF",
                avg: ".311",
                homeRuns: "62",
                rbi: "131",
                obp: ".425"
            },
            {
                name: "Mookie Betts",
                team: "LAD",
                position: "RF",
                avg: ".269",
                homeRuns: "35",
                rbi: "82",
                obp: ".340"
            },
            {
                name: "José Altuve",
                team: "HOU",
                position: "2B",
                avg: ".300",
                homeRuns: "28",
                rbi: "57",
                obp: ".387"
            },
            {
                name: "Vladimir Guerrero Jr.",
                team: "TOR",
                position: "1B",
                avg: ".274",
                homeRuns: "32",
                rbi: "97",
                obp: ".339"
            },
            {
                name: "Ronald Acuña Jr.",
                team: "ATL",
                position: "OF",
                avg: ".266",
                homeRuns: "41",
                rbi: "106",
                obp: ".351"
            }
        ];
        
        if (searchTerm) {
            return mockPlayers.filter(player => 
                player.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                player.team.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }
        
        return mockPlayers;
    }

    // Clear cache (useful for forcing refresh)
    clearCache() {
        this.cache.clear();
    }

    // Get cache status for debugging
    getCacheStatus() {
        const now = Date.now();
        const status = {};
        
        for (const [key, value] of this.cache.entries()) {
            const age = now - value.timestamp;
            status[key] = {
                age: Math.floor(age / 1000), // in seconds
                expired: age > this.cacheTimeout
            };
        }
        
        return status;
    }
}

// Create global API instance
window.espnApi = new ESPNApi();
