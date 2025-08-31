#!/usr/bin/env python3
"""
Unit tests for NCAA team name display enhancement

Tests that NCAA Football and Basketball show full team names (e.g., "Wisconsin Badgers")
instead of just nicknames (e.g., "Badgers") in the scores list.
"""

import unittest
import unittest.mock
import sys
import os

# Add project root to Python path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

class TestNCAAvTeamNames(unittest.TestCase):
    """Test NCAA team name display enhancement"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_ncaaf_response = {
            "events": [
                {
                    "id": "401628470",
                    "name": "Wisconsin Badgers vs Miami Hurricanes",
                    "competitions": [
                        {
                            "status": {
                                "type": {
                                    "shortDetail": "8/31 - 8:00 PM EDT",
                                    "description": "Scheduled"
                                }
                            },
                            "competitors": [
                                {
                                    "team": {
                                        "id": "275",
                                        "name": "Badgers",
                                        "displayName": "Wisconsin Badgers",
                                        "abbreviation": "WIS"
                                    },
                                    "score": "",
                                    "homeAway": "away"
                                },
                                {
                                    "team": {
                                        "id": "2390",
                                        "name": "Hurricanes",
                                        "displayName": "Miami Hurricanes",
                                        "abbreviation": "MIA"
                                    },
                                    "score": "",
                                    "homeAway": "home"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        self.mock_ncaam_response = {
            "events": [
                {
                    "id": "401587456",
                    "name": "North Carolina Tar Heels vs Duke Blue Devils",
                    "competitions": [
                        {
                            "status": {
                                "type": {
                                    "shortDetail": "3/9 - 7:00 PM EDT",
                                    "description": "Scheduled"
                                }
                            },
                            "competitors": [
                                {
                                    "team": {
                                        "id": "153",
                                        "name": "Tar Heels",
                                        "displayName": "North Carolina Tar Heels",
                                        "abbreviation": "UNC"
                                    },
                                    "score": "",
                                    "homeAway": "away"
                                },
                                {
                                    "team": {
                                        "id": "150",
                                        "name": "Blue Devils",
                                        "displayName": "Duke Blue Devils",
                                        "abbreviation": "DUKE"
                                    },
                                    "score": "",
                                    "homeAway": "home"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        self.mock_nfl_response = {
            "events": [
                {
                    "id": "401671834",
                    "name": "Green Bay Packers vs Minnesota Vikings",
                    "competitions": [
                        {
                            "status": {
                                "type": {
                                    "shortDetail": "9/8 - 1:00 PM EDT",
                                    "description": "Scheduled"
                                }
                            },
                            "competitors": [
                                {
                                    "team": {
                                        "id": "9",
                                        "name": "Packers",
                                        "displayName": "Green Bay Packers",
                                        "abbreviation": "GB"
                                    },
                                    "score": "",
                                    "homeAway": "away"
                                },
                                {
                                    "team": {
                                        "id": "16",
                                        "name": "Vikings",
                                        "displayName": "Minnesota Vikings",
                                        "abbreviation": "MIN"
                                    },
                                    "score": "",
                                    "homeAway": "home"
                                }
                            ]
                        }
                    ]
                }
            ]
        }

    def mock_requests_get(self, url):
        """Mock requests.get to return test data"""
        class MockResponse:
            def __init__(self, json_data, status_code=200):
                self.json_data = json_data
                self.status_code = status_code
            
            def json(self):
                return self.json_data
        
        if "football/college-football" in url:
            return MockResponse(self.mock_ncaaf_response)
        elif "basketball/mens-college-basketball" in url:
            return MockResponse(self.mock_ncaam_response)
        elif "football/nfl" in url:
            return MockResponse(self.mock_nfl_response)
        else:
            return MockResponse({}, 404)

    @unittest.mock.patch('requests.get')
    def test_ncaaf_uses_full_team_names(self, mock_get):
        """Test that NCAAF games show full team names"""
        mock_get.side_effect = self.mock_requests_get
        
        from espn_api import get_scores
        from models.game import GameData
        
        # Get NCAAF scores
        scores = get_scores('NCAAF', week=1)
        self.assertGreater(len(scores), 0, "Should return at least one game")
        
        # Check that team names are full names, not nicknames
        game = GameData(scores[0], 'NCAAF')
        display_text = game.get_display_text()
        
        # Should show "Wisconsin Badgers" not "Badgers"
        self.assertIn("Wisconsin Badgers", display_text, 
                     "NCAAF should show full team name 'Wisconsin Badgers'")
        self.assertIn("Miami Hurricanes", display_text,
                     "NCAAF should show full team name 'Miami Hurricanes'")
        
        # Should not show just the nicknames
        self.assertNotEqual("Badgers vs Hurricanes", display_text.split("(")[0].strip(),
                           "Should not show just nicknames")

    @unittest.mock.patch('requests.get')
    def test_ncaam_uses_full_team_names(self, mock_get):
        """Test that NCAAM games show full team names"""
        mock_get.side_effect = self.mock_requests_get
        
        from espn_api import get_scores
        from models.game import GameData
        
        # Get NCAAM scores
        scores = get_scores('NCAAM')
        self.assertGreater(len(scores), 0, "Should return at least one game")
        
        # Check that team names are full names, not nicknames
        game = GameData(scores[0], 'NCAAM')
        display_text = game.get_display_text()
        
        # Should show "North Carolina Tar Heels" not "Tar Heels"
        self.assertIn("North Carolina Tar Heels", display_text,
                     "NCAAM should show full team name 'North Carolina Tar Heels'")
        self.assertIn("Duke Blue Devils", display_text,
                     "NCAAM should show full team name 'Duke Blue Devils'")

    @unittest.mock.patch('requests.get')
    def test_nfl_unchanged(self, mock_get):
        """Test that NFL games still show nicknames (unchanged behavior)"""
        mock_get.side_effect = self.mock_requests_get
        
        from espn_api import get_scores
        from models.game import GameData
        
        # Get NFL scores
        scores = get_scores('NFL')
        self.assertGreater(len(scores), 0, "Should return at least one game")
        
        # Check that NFL still shows nicknames, not full names
        game = GameData(scores[0], 'NFL')
        display_text = game.get_display_text()
        
        # Should show "Packers" not "Green Bay Packers"
        self.assertIn("Packers", display_text, "NFL should show nickname 'Packers'")
        self.assertIn("Vikings", display_text, "NFL should show nickname 'Vikings'")
        
        # Should NOT show full names for NFL
        self.assertNotIn("Green Bay Packers", display_text,
                        "NFL should not show full name 'Green Bay Packers'")
        self.assertNotIn("Minnesota Vikings", display_text,
                        "NFL should not show full name 'Minnesota Vikings'")

    @unittest.mock.patch('requests.get')
    def test_fallback_behavior(self, mock_get):
        """Test fallback behavior when displayName is missing"""
        # Create response with missing displayName
        mock_response = {
            "events": [
                {
                    "id": "401628470",
                    "name": "Test Game",
                    "competitions": [
                        {
                            "status": {
                                "type": {
                                    "shortDetail": "8/31 - 8:00 PM EDT",
                                    "description": "Scheduled"
                                }
                            },
                            "competitors": [
                                {
                                    "team": {
                                        "id": "275",
                                        "name": "Badgers",
                                        # Missing displayName
                                        "abbreviation": "WIS"
                                    },
                                    "score": "",
                                    "homeAway": "away"
                                },
                                {
                                    "team": {
                                        "id": "2390",
                                        # Missing name and displayName
                                        "abbreviation": "MIA"
                                    },
                                    "score": "",
                                    "homeAway": "home"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response
        
        from espn_api import get_scores
        
        # Get NCAAF scores with missing data
        scores = get_scores('NCAAF', week=1)
        self.assertGreater(len(scores), 0, "Should return at least one game")
        
        teams = scores[0].get('teams', [])
        self.assertEqual(len(teams), 2, "Should have 2 teams")
        
        # Should gracefully fall back to name then abbreviation
        self.assertEqual(teams[0]['name'], "Badgers", "Should fall back to name")
        self.assertEqual(teams[1]['name'], "MIA", "Should fall back to abbreviation")

if __name__ == '__main__':
    unittest.main()