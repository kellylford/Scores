import sys
import webbrowser
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton, QLabel,
    QHBoxLayout, QCheckBox, QDialog, QMessageBox, QTextEdit, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QTreeWidget, QTreeWidgetItem,
    QTabWidget, QSplitter
)
from PyQt6.QtCore import Qt, QTimer
import espn_api

class ConfigDialog(QDialog):
    def __init__(self, details, selected, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Game Details")
        self.layout = QVBoxLayout()
        self.checkboxes = {}
        for detail in details:
            cb = QCheckBox(detail)
            cb.setChecked(detail in selected)
            self.layout.addWidget(cb)
            self.checkboxes[detail] = cb
        btn = QPushButton("OK")
        btn.clicked.connect(self.accept)
        self.layout.addWidget(btn)
        self.setLayout(self.layout)
    def get_selected(self):
        return [d for d, cb in self.checkboxes.items() if cb.isChecked()]

class SportsScoresApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sports Scores (ESPN)")
        self.resize(600, 400)
        self.stack = []
        self.config = {}
        self.news_headlines = []
        self.current_date = datetime.now().date()  # Track current date for scores
        for l in espn_api.get_leagues():
            self.config[l] = ["name", "status", "competitors"]  # Default details
        self.init_home()
        self.show()

    def clear_layout(self):
        for i in reversed(range(self.layout().count())):
            w = self.layout().itemAt(i).widget()
            if w:
                w.deleteLater()

    def init_home(self):
        self.setLayout(QVBoxLayout())
        self.clear_layout()
        self.stack = []
        self.league_list = QListWidget()
        for league in espn_api.get_leagues():
            self.league_list.addItem(league)
        self.league_list.itemActivated.connect(self.open_league)
        self.layout().addWidget(QLabel("Select a League:"))
        self.layout().addWidget(self.league_list)
        self.set_nav_buttons()
        # Use timer to ensure focus is set after UI updates complete
        QTimer.singleShot(50, lambda: self.league_list.setFocus())

    def open_league(self, item):
        league = item.text()
        self.stack.append(("home", None))
        self.clear_layout()
        self.current_league = league
        self.current_date = datetime.now().date()  # Reset to today when opening league
        self.scores_list = QListWidget()
        
        # Add date navigation label
        self.date_label = QLabel()
        self.layout().addWidget(self.date_label)
        
        self.layout().addWidget(QLabel(f"Scores for {league}:"))
        self.layout().addWidget(self.scores_list)
        self.set_nav_buttons(refresh=True, date_nav=True)
        self.scores_list.itemActivated.connect(self.open_scores_item)
        self.load_scores()
        # Use timer to ensure focus is set after UI updates complete
        QTimer.singleShot(50, lambda: self.scores_list.setFocus())

    def load_scores(self):
        self.scores_list.clear()
        
        # Update date label
        date_str = self.current_date.strftime("%A, %B %d, %Y")
        self.date_label.setText(f"Date: {date_str}")
        
        # Get scores for the current date
        scores = espn_api.get_scores(self.current_league, self.current_date)
        # Get news headlines separately (now returns full news objects)
        self.news_headlines = espn_api.get_news(self.current_league)
        
        if not scores:
            self.scores_list.addItem(f"No games scheduled for {date_str}")
        else:
            for score in scores:
                display = score["name"]
                
                # Add scores if available
                if "teams" in score and score["teams"]:
                    team_scores = []
                    for team in score["teams"]:
                        if team.get("score"):
                            team_scores.append(f"{team['abbreviation']} {team['score']}")
                    if team_scores:
                        display += f" ({' - '.join(team_scores)})"
                
                # Add timing/status info
                if "start_time" in score and score["start_time"]:
                    if not any(team.get("score") for team in score.get("teams", [])):
                        # Only show start time if no scores available
                        display += f" - {score['start_time']}"
                    else:
                        # Show status (like "Bot 3rd") if game is in progress
                        display += f" - {score['start_time']}"
                
                self.scores_list.addItem(display)
                self.scores_list.item(self.scores_list.count()-1).setData(Qt.ItemDataRole.UserRole, score["id"])
        
        # Add a single News entry at the end if headlines exist
        if self.news_headlines:
            news_count = len(self.news_headlines)
            self.scores_list.addItem(f"--- News ({news_count} stories) ---")
            self.scores_list.item(self.scores_list.count()-1).setData(Qt.ItemDataRole.UserRole, "__news__")
        
        # Add standings entry for MLB
        if self.current_league == "MLB":
            self.scores_list.addItem("--- Standings ---")
            self.scores_list.item(self.scores_list.count()-1).setData(Qt.ItemDataRole.UserRole, "__standings__")

    def open_scores_item(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data == "__news__":
            self.show_news_dialog()
        elif data == "__standings__":
            self.show_standings_dialog()
        else:
            # Open game details for selected game
            game_id = item.data(Qt.ItemDataRole.UserRole)
            self.stack.append(("league", self.current_league))
            self.clear_layout()
            self.current_game_id = game_id
            self.details_list = QListWidget()
            self.layout().addWidget(QLabel("Game Details:"))
            self.layout().addWidget(self.details_list)
            self.set_nav_buttons(refresh=True, config=True)
            self.load_game_details()
            # Use timer to ensure focus is set after UI updates complete
            QTimer.singleShot(50, lambda: self.details_list.setFocus())

    def show_news_dialog(self):
        if not self.news_headlines:
            QMessageBox.information(self, "News", "No news headlines available for this league.")
            return
            
        dlg = QDialog(self)
        dlg.setWindowTitle(f"News Headlines - {self.current_league}")
        dlg.resize(700, 500)
        layout = QVBoxLayout()
        
        # Create a list for news headlines that can be selected
        news_list = QListWidget()
        for i, news_item in enumerate(self.news_headlines):
            if isinstance(news_item, dict):
                headline = news_item.get("headline", "No headline")
                # Show author if available
                byline = news_item.get("byline", "")
                if byline:
                    display_text = f"{headline}\n  by {byline}"
                else:
                    display_text = headline
                news_list.addItem(display_text)
                news_list.item(i).setData(Qt.ItemDataRole.UserRole, news_item)
            else:
                # Handle old format (just strings)
                news_list.addItem(str(news_item))
                news_list.item(i).setData(Qt.ItemDataRole.UserRole, {"headline": str(news_item), "web_url": ""})
        
        # Connect double-click to open story
        news_list.itemDoubleClicked.connect(self.open_news_story)
        layout.addWidget(QLabel("Double-click a headline to open the full story in your browser:"))
        layout.addWidget(news_list)
        
        # Add buttons
        btn_layout = QHBoxLayout()
        
        open_btn = QPushButton("Open Selected Story")
        open_btn.clicked.connect(lambda: self.open_selected_news_story(news_list))
        btn_layout.addWidget(open_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        dlg.setLayout(layout)
        
        # Set focus to the news list
        news_list.setFocus()
        dlg.exec()
    
    def open_news_story(self, item):
        """Open a news story in the default web browser"""
        news_data = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(news_data, dict) and news_data.get("web_url"):
            webbrowser.open(news_data["web_url"])
        else:
            QMessageBox.information(self, "No Link", "No web link available for this story.")
    
    def open_selected_news_story(self, news_list):
        """Open the currently selected news story"""
        current_item = news_list.currentItem()
        if current_item:
            self.open_news_story(current_item)
        else:
            QMessageBox.information(self, "No Selection", "Please select a news story first.")

    def show_standings_dialog(self):
        """Show current MLB standings in an accessible table format"""
        standings_data = espn_api.get_standings(self.current_league)
        
        if not standings_data:
            QMessageBox.information(self, "Standings", f"No standings data available for {self.current_league}.")
            return
        
        dlg = QDialog(self)
        dlg.setWindowTitle(f"{self.current_league} Standings")
        dlg.resize(900, 600)
        layout = QVBoxLayout()
        
        # Create accessible table
        table = QTableWidget()
        
        # Set up table headers
        headers = ["Team", "W", "L", "Win %", "GB", "Division"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(standings_data))
        
        # Populate table
        for row, team_data in enumerate(standings_data):
            team_name = team_data.get("team_name", "")
            
            # Team name
            team_item = QTableWidgetItem(team_name)
            table.setItem(row, 0, team_item)
            
            # Wins - include team name in accessible description
            wins_item = QTableWidgetItem(str(team_data.get("wins", "")))
            wins_item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, f"{team_name} wins")
            table.setItem(row, 1, wins_item)
            
            # Losses - include team name in accessible description
            losses_item = QTableWidgetItem(str(team_data.get("losses", "")))
            losses_item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, f"{team_name} losses")
            table.setItem(row, 2, losses_item)
            
            # Win percentage - include team name in accessible description
            win_pct_item = QTableWidgetItem(team_data.get("win_percentage", ""))
            win_pct_item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, f"{team_name} win percentage")
            table.setItem(row, 3, win_pct_item)
            
            # Games back - include team name in accessible description
            gb_item = QTableWidgetItem(team_data.get("games_back", ""))
            gb_item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, f"{team_name} games back")
            table.setItem(row, 4, gb_item)
            
            # Division - include team name in accessible description
            div_item = QTableWidgetItem(team_data.get("division", ""))
            div_item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, f"{team_name} division")
            table.setItem(row, 5, div_item)
        
        # Make table accessible
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Hide row numbers/vertical headers
        table.verticalHeader().setVisible(False)
        
        # Auto-resize columns to content
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Team name column stretches
        
        # Don't sort here - data is already sorted by division and position in the API
        
        layout.addWidget(QLabel(f"Current {self.current_league} Standings:"))
        layout.addWidget(table)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)
        
        dlg.setLayout(layout)
        
        # Set focus to the table for keyboard navigation
        table.setFocus()
        dlg.exec()

    def load_game_details(self):
        self.details_list.clear()
        raw_details = espn_api.get_game_details(self.current_league, self.current_game_id)
        
        # Get meaningful information - ensure we always get a dict
        details = espn_api.extract_meaningful_game_info(raw_details)
        if details is None:
            details = {}
        
        # Display teams and records
        if 'teams' in details:
            for team in details['teams']:
                home_away = " (Home)" if team['home_away'] == 'home' else " (Away)"
                self.details_list.addItem(f"{team['name']}{home_away}")
                self.details_list.addItem(f"  Record: {team['record']}")
        
        # Game status and timing
        if 'status' in details:
            self.details_list.addItem(f"Status: {details['status']}")
        
        # Score information
        if 'scores' in details and details['scores']:
            score_display = " - ".join(details['scores'])
            self.details_list.addItem(f"Score: {score_display}")
        
        if 'detailed_status' in details and details['detailed_status'] != 'N/A':
            self.details_list.addItem(f"Game Time: {details['detailed_status']}")
        
        # Venue information
        if 'venue' in details:
            venue_info = details['venue']
            if 'venue_city' in details and details['venue_city'] != 'Unknown':
                venue_info += f" ({details['venue_city']}"
                if 'venue_state' in details and details['venue_state']:
                    venue_info += f", {details['venue_state']}"
                venue_info += ")"
            self.details_list.addItem(f"Venue: {venue_info}")
        
        # Weather
        if 'weather' in details:
            weather_display = details['weather']
            if 'temperature' in details:
                weather_display += f", {details['temperature']}"
            self.details_list.addItem(f"Weather: {weather_display}")
        
        # Betting information
        if 'betting_line' in details:
            self.details_list.addItem(f"Betting Line: {details['betting_line']}")
        if 'over_under' in details:
            self.details_list.addItem(f"Over/Under: {details['over_under']}")
        
        # Broadcast info
        if 'broadcast' in details:
            self.details_list.addItem(f"TV: {details['broadcast']}")
        
        # Injuries
        if 'injuries' in details:
            self.details_list.addItem(f"Injuries: {details['injuries']}")
        
        # Show configurable details if any are selected
        config_fields = self.config.get(self.current_league, [])
        valid_fields = ["boxscore", "leaders", "standings", "odds", "injuries", "broadcasts", "news", "gameInfo"]
        
        # Filter out any invalid field names that might have gotten into config
        config_fields = [field for field in config_fields if field in valid_fields]
        
        if config_fields:
            self.details_list.addItem("--- Additional Details ---")
            for field in config_fields:
                value = raw_details.get(field, "N/A")
                if value == "N/A" or not value:
                    self.details_list.addItem(f"{field}: No data available")
                else:
                    # Check if this is complex data that should be navigable
                    if field in ["standings", "leaders", "boxscore", "injuries", "news"]:
                        # Check if there's actual data to navigate
                        has_data = False
                        if field == "standings" and isinstance(value, (list, dict)):
                            has_data = len(value) > 0 if isinstance(value, list) else bool(value.get("entries"))
                        elif field == "leaders" and isinstance(value, dict):
                            has_data = len(value) > 0
                        elif field == "boxscore" and isinstance(value, dict):
                            has_data = bool(value.get("teams") or value.get("players"))
                        elif field == "injuries" and isinstance(value, list):
                            has_data = len(value) > 0
                        elif field == "news" and isinstance(value, (list, dict)):
                            has_data = len(value) > 0 if isinstance(value, list) else bool(value.get("articles"))
                        
                        if has_data:
                            # Make it selectable for navigation
                            item_text = f"{field.title()}: Press Enter to view details"
                            self.details_list.addItem(item_text)
                            # Store the field name and raw data for navigation
                            list_item_widget = self.details_list.item(self.details_list.count() - 1)
                            if list_item_widget:
                                list_item_widget.setData(Qt.ItemDataRole.UserRole, {"field": field, "data": value})
                        else:
                            formatted_value = espn_api.format_complex_data(field, value)
                            self.details_list.addItem(f"{field}: {formatted_value}")
                    else:
                        # Use enhanced formatting for simple data
                        formatted_value = espn_api.format_complex_data(field, value)
                        # Handle multi-line content
                        if '\n' in formatted_value:
                            self.details_list.addItem(f"{field}:")
                            for line in formatted_value.split('\n'):
                                if line.strip():
                                    self.details_list.addItem(f"  {line}")
                        else:
                            self.details_list.addItem(f"{field}: {formatted_value}")
        
        # Connect item activation for detailed navigation
        try:
            self.details_list.itemActivated.disconnect()
        except:
            pass
        self.details_list.itemActivated.connect(self.open_detail_data)

    def open_detail_data(self, item):
        """Open detailed view for complex data like standings, leaders, etc."""
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return
            
        field_name = data.get("field")
        field_data = data.get("data")
        
        if not field_name or not field_data:
            return
            
        # Create a dialog for detailed data display
        dlg = QDialog(self)
        dlg.setWindowTitle(f"{field_name.title()} Details")
        dlg.resize(800, 600)
        layout = QVBoxLayout()
        
        if field_name == "standings" and isinstance(field_data, list):
            self.show_standings_table(layout, field_data)
        elif field_name == "leaders" and isinstance(field_data, dict):
            self.show_leaders_data(layout, field_data)
        elif field_name == "boxscore" and isinstance(field_data, dict):
            self.show_boxscore_data(layout, field_data)
        elif field_name == "injuries" and isinstance(field_data, list):
            self.show_injuries_list(layout, field_data)
        elif field_name == "news" and isinstance(field_data, list):
            self.show_news_list(layout, field_data)
        else:
            # Fallback to formatted text
            text_widget = QTextEdit()
            text_widget.setPlainText(espn_api.format_complex_data(field_name, field_data))
            text_widget.setReadOnly(True)
            layout.addWidget(text_widget)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)
        
        dlg.setLayout(layout)
        dlg.exec()

    def show_standings_table(self, layout, standings_data):
        """Display standings in a table format"""
        table = QTableWidget()
        
        if not standings_data:
            layout.addWidget(QLabel("No standings data available"))
            return
        
        # Handle different ESPN data structures
        data_to_process = standings_data
        if isinstance(standings_data, dict):
            if "entries" in standings_data:
                data_to_process = standings_data["entries"]
            elif "children" in standings_data:
                data_to_process = standings_data["children"]
            else:
                # Try to extract teams from any nested structure
                for key, value in standings_data.items():
                    if isinstance(value, list) and value:
                        data_to_process = value
                        break
        
        if not isinstance(data_to_process, list) or not data_to_process:
            layout.addWidget(QLabel("No standings data found"))
            return
            
        # Set up table structure with more comprehensive headers
        headers = ["Rank", "Team", "Wins", "Losses", "Win %", "GB", "Streak", "Record"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(data_to_process))
        
        # Populate table with enhanced data extraction
        for row, team_data in enumerate(data_to_process):
            if isinstance(team_data, dict):
                team = team_data.get("team", {})
                name = team.get("displayName", team.get("name", team.get("abbreviation", "Unknown")))
                
                # Try different ways to get stats
                stats = team_data.get("stats", [])
                record = team_data.get("record", "")
                
                # Initialize stat values
                wins = "N/A"
                losses = "N/A"
                win_pct = "N/A"
                games_behind = "N/A"
                streak = "N/A"
                
                # Extract stats from various possible formats
                if isinstance(stats, list):
                    for stat in stats:
                        if isinstance(stat, dict):
                            stat_name = stat.get("name", "").lower()
                            value = stat.get("value", stat.get("displayValue", ""))
                            if "wins" in stat_name or stat_name == "w":
                                wins = str(value)
                            elif "losses" in stat_name or stat_name == "l":
                                losses = str(value)
                            elif "winpercent" in stat_name or "pct" in stat_name or stat_name == "pct":
                                win_pct = str(value)
                            elif "gamesbehind" in stat_name or stat_name == "gb":
                                games_behind = str(value)
                            elif "streak" in stat_name:
                                streak = str(value)
                elif isinstance(stats, dict):
                    wins = str(stats.get("wins", stats.get("w", "N/A")))
                    losses = str(stats.get("losses", stats.get("l", "N/A")))
                    win_pct = str(stats.get("winPercent", stats.get("pct", "N/A")))
                    games_behind = str(stats.get("gamesBehind", stats.get("gb", "N/A")))
                    streak = str(stats.get("streak", "N/A"))
                
                # If we don't have individual stats, try to parse record string
                if wins == "N/A" and losses == "N/A" and record:
                    if "-" in str(record):
                        parts = str(record).split("-")
                        if len(parts) >= 2:
                            wins = parts[0].strip()
                            losses = parts[1].strip()
                
                rank = str(row + 1)
                display_record = record if record else f"{wins}-{losses}" if wins != "N/A" and losses != "N/A" else "N/A"
                
                # Set table items with accessibility descriptions
                rank_item = QTableWidgetItem(rank)
                rank_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Rank {rank}")
                table.setItem(row, 0, rank_item)
                
                team_item = QTableWidgetItem(name)
                team_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Team: {name}")
                table.setItem(row, 1, team_item)
                
                wins_item = QTableWidgetItem(wins)
                wins_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Wins: {wins}")
                table.setItem(row, 2, wins_item)
                
                losses_item = QTableWidgetItem(losses)
                losses_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Losses: {losses}")
                table.setItem(row, 3, losses_item)
                
                pct_item = QTableWidgetItem(win_pct)
                pct_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Win percentage: {win_pct}")
                table.setItem(row, 4, pct_item)
                
                gb_item = QTableWidgetItem(games_behind)
                gb_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Games behind: {games_behind}")
                table.setItem(row, 5, gb_item)
                
                streak_item = QTableWidgetItem(streak)
                streak_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Streak: {streak}")
                table.setItem(row, 6, streak_item)
                
                record_item = QTableWidgetItem(display_record)
                record_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Record: {display_record}")
                table.setItem(row, 7, record_item)
        
        # Enhanced table accessibility and functionality
        table.horizontalHeader().setStretchLastSection(True)
        table.resizeColumnsToContents()
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSortingEnabled(True)  # Enable column sorting
        table.setAccessibleName("Team Standings Table")
        table.setAccessibleDescription("Table showing team standings with wins, losses, percentages and rankings")
        
        # Set initial focus and keyboard navigation
        table.setFocus()
        table.selectRow(0)  # Select first row for easier navigation
        
        layout.addWidget(QLabel("Team Standings (use arrow keys to navigate, Enter to select):"))
        layout.addWidget(table)

    def show_leaders_data(self, layout, leaders_data):
        """Display leaders in a structured tree format for better accessibility"""
        if not leaders_data:
            layout.addWidget(QLabel("No leaders data available"))
            return
            
        tree_widget = QTreeWidget()
        tree_widget.setHeaderLabels(["Category/Player", "Team", "Statistic", "Value"])
        tree_widget.setAccessibleName("Statistical Leaders Tree")
        tree_widget.setAccessibleDescription("Tree view of statistical leaders organized by category")
        
        for category, leader_info in leaders_data.items():
            # Create category parent item
            category_item = QTreeWidgetItem([category.upper(), "", "", ""])
            category_item.setData(0, Qt.ItemDataRole.AccessibleTextRole, f"Category: {category.upper()}")
            tree_widget.addTopLevelItem(category_item)
            
            leaders = []
            if isinstance(leader_info, dict):
                if "leaders" in leader_info:
                    leaders = leader_info["leaders"]
                elif "athletes" in leader_info:
                    leaders = leader_info["athletes"]
            elif isinstance(leader_info, list):
                leaders = leader_info
                
            if leaders:
                for i, leader in enumerate(leaders[:10]):  # Top 10 leaders
                    if isinstance(leader, dict):
                        athlete = leader.get("athlete", {})
                        name = athlete.get("displayName", athlete.get("name", "Unknown"))
                        value = leader.get("value", leader.get("displayValue", "N/A"))
                        
                        # Get team info
                        team = athlete.get("team", {})
                        team_abbr = team.get("abbreviation", team.get("displayName", ""))
                        
                        # Get statistic type/name if available
                        stat_type = leader.get("type", {}).get("displayName", "") if leader.get("type") else ""
                        if not stat_type:
                            stat_type = leader.get("name", category)
                        
                        # Create child item
                        rank = str(i + 1)
                        player_item = QTreeWidgetItem([
                            f"{rank}. {name}", 
                            team_abbr, 
                            stat_type, 
                            str(value)
                        ])
                        
                        # Set accessibility data for each column
                        player_item.setData(0, Qt.ItemDataRole.AccessibleTextRole, f"Rank {rank}: {name}")
                        player_item.setData(1, Qt.ItemDataRole.AccessibleTextRole, f"Team: {team_abbr}")
                        player_item.setData(2, Qt.ItemDataRole.AccessibleTextRole, f"Statistic: {stat_type}")
                        player_item.setData(3, Qt.ItemDataRole.AccessibleTextRole, f"Value: {value}")
                        
                        category_item.addChild(player_item)
            else:
                # Add "No data" child
                no_data_item = QTreeWidgetItem(["No data available", "", "", ""])
                no_data_item.setData(0, Qt.ItemDataRole.AccessibleTextRole, "No data available")
                category_item.addChild(no_data_item)
        
        # Expand all categories by default for better accessibility
        tree_widget.expandAll()
        
        # Auto-resize columns
        for i in range(tree_widget.columnCount()):
            tree_widget.resizeColumnToContents(i)
        
        # Set initial focus
        tree_widget.setFocus()
        if tree_widget.topLevelItemCount() > 0:
            tree_widget.setCurrentItem(tree_widget.topLevelItem(0))
        
        layout.addWidget(QLabel("Statistical Leaders (use arrow keys to navigate, +/- to expand/collapse):"))
        layout.addWidget(tree_widget)

    def show_boxscore_data(self, layout, boxscore_data):
        """Display boxscore in tabbed table format for better organization"""
        
        # Handle ESPN's complex boxscore structure
        players_data = None
        teams_data = None
        
        if isinstance(boxscore_data, dict):
            # Get players data - this is where the actual statistics are
            if "players" in boxscore_data:
                players_data = boxscore_data["players"]
            
            # Also try to get team data if available
            if "teams" in boxscore_data:
                teams_data = boxscore_data["teams"]
            elif "boxscore" in boxscore_data and isinstance(boxscore_data["boxscore"], dict):
                nested_boxscore = boxscore_data["boxscore"]
                teams_data = nested_boxscore.get("teams", [])
                if not players_data:
                    players_data = nested_boxscore.get("players", [])
        
        if not teams_data and not players_data:
            layout.addWidget(QLabel("No boxscore data found"))
            return
        
        tab_widget = QTabWidget()
        tab_widget.setAccessibleName("Boxscore Tabs")
        tab_widget.setAccessibleDescription("Tabbed view of team and player statistics")
        
        # Player Statistics Tab - this is the main content for baseball
        if players_data:
            # Baseball typically has two teams (home/away) with player stats
            for team_idx, team_players in enumerate(players_data):
                if isinstance(team_players, dict) and "statistics" in team_players:
                    team_name = f"Team {team_idx + 1}"
                    
                    # Try to get team name if available
                    if "team" in team_players:
                        team_info = team_players["team"]
                        if isinstance(team_info, dict):
                            team_name = team_info.get("displayName", team_info.get("name", team_name))
                    
                    player_tab = QWidget()
                    player_layout = QVBoxLayout()
                    
                    # Create table for player statistics
                    player_table = QTableWidget()
                    
                    # Get statistics array
                    statistics = team_players.get("statistics", [])
                    if not statistics:
                        player_layout.addWidget(QLabel(f"No statistics available for {team_name}"))
                        player_tab.setLayout(player_layout)
                        tab_widget.addTab(player_tab, team_name)
                        continue
                    
                    # Extract player data from first statistic group
                    stat_group = statistics[0] if statistics else {}
                    athletes = stat_group.get("athletes", [])
                    
                    if not athletes:
                        player_layout.addWidget(QLabel(f"No player data available for {team_name}"))
                        player_tab.setLayout(player_layout)
                        tab_widget.addTab(player_tab, team_name)
                        continue
                    
                    # Set up table headers - basic baseball stats
                    headers = ["Player", "Position", "AB", "R", "H", "RBI", "BB", "SO", "AVG"]
                    player_table.setColumnCount(len(headers))
                    player_table.setHorizontalHeaderLabels(headers)
                    player_table.setRowCount(len(athletes))
                    
                    # Populate table with player statistics
                    for row, athlete_data in enumerate(athletes):
                        if isinstance(athlete_data, dict):
                            athlete = athlete_data.get("athlete", {})
                            name = athlete.get("displayName", "Unknown Player")
                            
                            # Get position
                            position = ""
                            if "position" in athlete:
                                pos_info = athlete["position"]
                                if isinstance(pos_info, dict):
                                    position = pos_info.get("abbreviation", pos_info.get("name", ""))
                                else:
                                    position = str(pos_info)
                            
                            # Extract statistics - ESPN stores these in various formats
                            stats = athlete_data.get("stats", [])
                            
                            # Initialize stat values
                            at_bats = "0"
                            runs = "0"
                            hits = "0"
                            rbis = "0"
                            walks = "0"
                            strikeouts = "0"
                            avg = ".000"
                            
                            # Parse statistics - they can be in different formats
                            if isinstance(stats, list):
                                for stat in stats:
                                    if isinstance(stat, (int, float, str)):
                                        # Simple numeric stats in order
                                        pass  # We'll handle this if we see this pattern
                                    elif isinstance(stat, dict):
                                        # Named statistics
                                        stat_name = stat.get("name", "").lower()
                                        value = str(stat.get("value", stat.get("displayValue", "0")))
                                        
                                        if "atbat" in stat_name or stat_name == "ab":
                                            at_bats = value
                                        elif "run" in stat_name and "rbi" not in stat_name:
                                            runs = value
                                        elif "hit" in stat_name and "rbi" not in stat_name:
                                            hits = value
                                        elif "rbi" in stat_name:
                                            rbis = value
                                        elif "walk" in stat_name or "bb" in stat_name:
                                            walks = value
                                        elif "strikeout" in stat_name or "so" in stat_name or "k" in stat_name:
                                            strikeouts = value
                                        elif "avg" in stat_name or "average" in stat_name:
                                            avg = value
                            elif isinstance(stats, dict):
                                # Direct stat dictionary
                                at_bats = str(stats.get("atBats", stats.get("AB", stats.get("ab", "0"))))
                                runs = str(stats.get("runs", stats.get("R", stats.get("r", "0"))))
                                hits = str(stats.get("hits", stats.get("H", stats.get("h", "0"))))
                                rbis = str(stats.get("RBIs", stats.get("RBI", stats.get("rbi", "0"))))
                                walks = str(stats.get("walks", stats.get("BB", stats.get("bb", "0"))))
                                strikeouts = str(stats.get("strikeouts", stats.get("SO", stats.get("so", stats.get("K", "0")))))
                                avg = str(stats.get("avg", stats.get("average", stats.get("battingAverage", ".000"))))
                            
                            # Set table items with accessibility
                            name_item = QTableWidgetItem(name)
                            name_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Player: {name}")
                            player_table.setItem(row, 0, name_item)
                            
                            pos_item = QTableWidgetItem(position)
                            pos_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Position: {position}")
                            player_table.setItem(row, 1, pos_item)
                            
                            ab_item = QTableWidgetItem(at_bats)
                            ab_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"At bats: {at_bats}")
                            player_table.setItem(row, 2, ab_item)
                            
                            r_item = QTableWidgetItem(runs)
                            r_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Runs: {runs}")
                            player_table.setItem(row, 3, r_item)
                            
                            h_item = QTableWidgetItem(hits)
                            h_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Hits: {hits}")
                            player_table.setItem(row, 4, h_item)
                            
                            rbi_item = QTableWidgetItem(rbis)
                            rbi_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"RBIs: {rbis}")
                            player_table.setItem(row, 5, rbi_item)
                            
                            bb_item = QTableWidgetItem(walks)
                            bb_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Walks: {walks}")
                            player_table.setItem(row, 6, bb_item)
                            
                            so_item = QTableWidgetItem(strikeouts)
                            so_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Strikeouts: {strikeouts}")
                            player_table.setItem(row, 7, so_item)
                            
                            avg_item = QTableWidgetItem(avg)
                            avg_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Batting average: {avg}")
                            player_table.setItem(row, 8, avg_item)
                    
                    # Configure table
                    player_table.resizeColumnsToContents()
                    player_table.setAlternatingRowColors(True)
                    player_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
                    player_table.setAccessibleName(f"{team_name} Player Statistics")
                    player_table.setAccessibleDescription(f"Player statistics for {team_name}")
                    
                    player_layout.addWidget(QLabel(f"{team_name} - Player Statistics:"))
                    player_layout.addWidget(player_table)
                    player_tab.setLayout(player_layout)
                    tab_widget.addTab(player_tab, team_name)
        
        # Team Summary Tab (if team data available or we can derive it from players)
        if teams_data or players_data:
            team_tab = QWidget()
            team_layout = QVBoxLayout()
            
            # Create table for team summary statistics
            team_table = QTableWidget()
            
            # Collect all team statistics
            all_team_stats = []
            
            # First try to get data from teams_data
            if teams_data:
                for i, team_data in enumerate(teams_data):
                    if isinstance(team_data, dict):
                        team_info = team_data.get("team", {})
                        team_name = team_info.get("displayName", f"Team {i + 1}")
                        
                        # Extract team-level statistics if available
                        stats = team_data.get("statistics", [])
                        if stats:
                            for stat in stats:
                                if isinstance(stat, dict):
                                    stat_name = stat.get("name", "")
                                    value = stat.get("displayValue", stat.get("value", ""))
                                    if stat_name and value:
                                        all_team_stats.append({
                                            "team": team_name,
                                            "statistic": stat_name,
                                            "value": str(value)
                                        })
            
            # If no team stats found, try to derive meaningful statistics from players_data
            if not all_team_stats and players_data:
                for team_idx, team_players in enumerate(players_data):
                    if isinstance(team_players, dict):
                        team_name = f"Team {team_idx + 1}"
                        
                        # Try to get team name if available
                        if "team" in team_players:
                            team_info = team_players["team"]
                            if isinstance(team_info, dict):
                                team_name = team_info.get("displayName", team_info.get("name", team_name))
                        
                        # Get statistics array
                        statistics = team_players.get("statistics", [])
                        if statistics:
                            stat_group = statistics[0] if statistics else {}
                            athletes = stat_group.get("athletes", [])
                            
                            if athletes:
                                # Calculate team totals from player stats
                                team_at_bats = 0
                                team_runs = 0
                                team_hits = 0
                                team_rbis = 0
                                team_walks = 0
                                team_strikeouts = 0
                                active_players = 0
                                
                                for athlete_data in athletes:
                                    if isinstance(athlete_data, dict):
                                        if athlete_data.get("active", True):
                                            active_players += 1
                                        
                                        # Extract statistics for this player
                                        stats = athlete_data.get("stats", [])
                                        
                                        # Parse player stats and add to team totals
                                        player_ab = 0
                                        player_r = 0
                                        player_h = 0
                                        player_rbi = 0
                                        player_bb = 0
                                        player_so = 0
                                        
                                        if isinstance(stats, list):
                                            for stat in stats:
                                                if isinstance(stat, dict):
                                                    stat_name = stat.get("name", "").lower()
                                                    try:
                                                        value = int(stat.get("value", stat.get("displayValue", "0")))
                                                    except (ValueError, TypeError):
                                                        value = 0
                                                    
                                                    if "atbat" in stat_name or stat_name == "ab":
                                                        player_ab = value
                                                    elif "run" in stat_name and "rbi" not in stat_name:
                                                        player_r = value
                                                    elif "hit" in stat_name and "rbi" not in stat_name:
                                                        player_h = value
                                                    elif "rbi" in stat_name:
                                                        player_rbi = value
                                                    elif "walk" in stat_name or "bb" in stat_name:
                                                        player_bb = value
                                                    elif "strikeout" in stat_name or "so" in stat_name or "k" in stat_name:
                                                        player_so = value
                                        elif isinstance(stats, dict):
                                            try:
                                                player_ab = int(stats.get("atBats", stats.get("AB", stats.get("ab", "0"))))
                                                player_r = int(stats.get("runs", stats.get("R", stats.get("r", "0"))))
                                                player_h = int(stats.get("hits", stats.get("H", stats.get("h", "0"))))
                                                player_rbi = int(stats.get("RBIs", stats.get("RBI", stats.get("rbi", "0"))))
                                                player_bb = int(stats.get("walks", stats.get("BB", stats.get("bb", "0"))))
                                                player_so = int(stats.get("strikeouts", stats.get("SO", stats.get("so", stats.get("K", "0")))))
                                            except (ValueError, TypeError):
                                                pass
                                        
                                        # Add to team totals
                                        team_at_bats += player_ab
                                        team_runs += player_r
                                        team_hits += player_h
                                        team_rbis += player_rbi
                                        team_walks += player_bb
                                        team_strikeouts += player_so
                                
                                # Add team statistics
                                all_team_stats.extend([
                                    {"team": team_name, "statistic": "Total Runs", "value": str(team_runs)},
                                    {"team": team_name, "statistic": "Total Hits", "value": str(team_hits)},
                                    {"team": team_name, "statistic": "Total RBIs", "value": str(team_rbis)},
                                    {"team": team_name, "statistic": "Total At Bats", "value": str(team_at_bats)},
                                    {"team": team_name, "statistic": "Total Walks", "value": str(team_walks)},
                                    {"team": team_name, "statistic": "Total Strikeouts", "value": str(team_strikeouts)},
                                    {"team": team_name, "statistic": "Active Players", "value": str(active_players)},
                                ])
                                
                                # Calculate team batting average
                                if team_at_bats > 0:
                                    team_avg = team_hits / team_at_bats
                                    all_team_stats.append({
                                        "team": team_name, 
                                        "statistic": "Team Batting Average", 
                                        "value": f"{team_avg:.3f}"
                                    })
                                
                                # Calculate on-base percentage approximation
                                if (team_at_bats + team_walks) > 0:
                                    obp = (team_hits + team_walks) / (team_at_bats + team_walks)
                                    all_team_stats.append({
                                        "team": team_name, 
                                        "statistic": "On-Base Percentage", 
                                        "value": f"{obp:.3f}"
                                    })
            
            if all_team_stats:
                # Set up table headers
                headers = ["Team", "Statistic", "Value"]
                team_table.setColumnCount(len(headers))
                team_table.setHorizontalHeaderLabels(headers)
                team_table.setRowCount(len(all_team_stats))
                
                # Populate table with team statistics
                for row, stat_data in enumerate(all_team_stats):
                    # Team name
                    team_item = QTableWidgetItem(stat_data["team"])
                    team_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Team: {stat_data['team']}")
                    team_table.setItem(row, 0, team_item)
                    
                    # Statistic name
                    stat_item = QTableWidgetItem(stat_data["statistic"])
                    stat_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Statistic: {stat_data['statistic']}")
                    team_table.setItem(row, 1, stat_item)
                    
                    # Value
                    value_item = QTableWidgetItem(stat_data["value"])
                    value_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Value: {stat_data['value']}")
                    team_table.setItem(row, 2, value_item)
                
                # Configure table for better accessibility
                team_table.resizeColumnsToContents()
                team_table.setAlternatingRowColors(True)
                team_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
                team_table.setSortingEnabled(True)  # Enable sorting by team or statistic
                team_table.setAccessibleName("Team Summary Statistics")
                team_table.setAccessibleDescription("Table showing team-level statistics for this game")
                
                # Set initial focus
                team_table.setFocus()
                if team_table.rowCount() > 0:
                    team_table.selectRow(0)
                
                team_layout.addWidget(QLabel("Team Performance Summary (use arrow keys to navigate):"))
                team_layout.addWidget(team_table)
            else:
                # Fallback if no team stats are available
                no_data_label = QLabel("No team statistics available for this game")
                no_data_label.setAccessibleName("No Data Message")
                no_data_label.setAccessibleDescription("No team statistics are available for this game")
                team_layout.addWidget(no_data_label)
            
            team_tab.setLayout(team_layout)
            tab_widget.addTab(team_tab, "Team Summary")
        
        # Set focus to first tab
        tab_widget.setCurrentIndex(0)
        tab_widget.setFocus()
        
        layout.addWidget(QLabel("Game Boxscore:"))
        layout.addWidget(tab_widget)

    def show_injuries_list(self, layout, injuries_data):
        """Display injuries in a structured list format with detailed information"""
        if not injuries_data:
            layout.addWidget(QLabel("No injury reports available"))
            return
            
        # Use a table for better organization of injury data
        injuries_table = QTableWidget()
        injuries_table.setColumnCount(5)
        headers = ["Player", "Position", "Team", "Status", "Details"]
        injuries_table.setHorizontalHeaderLabels(headers)
        injuries_table.setRowCount(len(injuries_data))
        injuries_table.setAccessibleName("Injury Reports Table")
        injuries_table.setAccessibleDescription("Table of player injury reports with details")
        
        for row, injury in enumerate(injuries_data):
            if isinstance(injury, dict):
                athlete = injury.get("athlete", {})
                name = athlete.get("displayName", "Unknown Player")
                
                # Get position
                position = ""
                if "position" in athlete:
                    pos_info = athlete["position"]
                    if isinstance(pos_info, dict):
                        position = pos_info.get("abbreviation", pos_info.get("name", ""))
                    else:
                        position = str(pos_info)
                
                # Get team
                team = ""
                if "team" in athlete:
                    team_info = athlete["team"]
                    if isinstance(team_info, dict):
                        team = team_info.get("abbreviation", team_info.get("displayName", ""))
                    else:
                        team = str(team_info)
                
                status = injury.get("status", injury.get("type", "Unknown status"))
                
                # Compile details
                details = []
                if injury.get("details"):
                    details.append(injury["details"])
                if injury.get("description"):
                    details.append(injury["description"])
                if injury.get("date"):
                    details.append(f"Date: {injury['date']}")
                if injury.get("longComment"):
                    details.append(injury["longComment"])
                
                details_text = "; ".join(details) if details else "No additional details"
                
                # Set table items with accessibility descriptions
                name_item = QTableWidgetItem(name)
                name_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Player: {name}")
                injuries_table.setItem(row, 0, name_item)
                
                pos_item = QTableWidgetItem(position)
                pos_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Position: {position}")
                injuries_table.setItem(row, 1, pos_item)
                
                team_item = QTableWidgetItem(team)
                team_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Team: {team}")
                injuries_table.setItem(row, 2, team_item)
                
                status_item = QTableWidgetItem(status)
                status_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Status: {status}")
                injuries_table.setItem(row, 3, status_item)
                
                details_item = QTableWidgetItem(details_text)
                details_item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Details: {details_text}")
                injuries_table.setItem(row, 4, details_item)
        
        # Configure table for better accessibility
        injuries_table.resizeColumnsToContents()
        injuries_table.setAlternatingRowColors(True)
        injuries_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        injuries_table.horizontalHeader().setStretchLastSection(True)  # Stretch details column
        
        # Set initial focus
        injuries_table.setFocus()
        if injuries_table.rowCount() > 0:
            injuries_table.selectRow(0)
        
        layout.addWidget(QLabel("Injury Reports (use arrow keys to navigate):"))
        layout.addWidget(injuries_table)

    def show_news_list(self, layout, news_data):
        """Display news in a structured list format with clickable headlines"""
        if not news_data:
            layout.addWidget(QLabel("No news available"))
            return
            
        news_list = QListWidget()
        news_list.setAccessibleName("News Articles List")
        news_list.setAccessibleDescription("List of news articles - double-click to open in browser")
        
        for i, article in enumerate(news_data):
            if isinstance(article, dict):
                headline = article.get("headline", "No headline")
                description = article.get("description", "")
                byline = article.get("byline", "")
                published = article.get("published", "")
                
                # Create display text with better formatting
                display_text = headline
                
                # Add byline if available
                if byline:
                    display_text += f"\nBy: {byline}"
                
                # Add publication date if available
                if published:
                    try:
                        # Try to format the date better
                        from datetime import datetime
                        if "T" in published:
                            date_obj = datetime.fromisoformat(published.replace("Z", "+00:00"))
                            formatted_date = date_obj.strftime("%B %d, %Y at %I:%M %p")
                            display_text += f"\nPublished: {formatted_date}"
                        else:
                            display_text += f"\nPublished: {published}"
                    except:
                        display_text += f"\nPublished: {published}"
                
                # Add description preview
                if description:
                    preview = description[:150] + "..." if len(description) > 150 else description
                    display_text += f"\n{preview}"
                
                # Create list item
                item = QListWidget.QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, article)
                item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Article {i+1}: {headline}")
                
                # Make it visually distinct
                font = item.font()
                font.setPointSize(font.pointSize() + 1)
                item.setFont(font)
                
                news_list.addItem(item)
        
        # Connect double-click to open articles
        news_list.itemDoubleClicked.connect(self.open_news_article)
        
        # Add instruction label
        instruction_label = QLabel("News Articles (double-click to open in browser, or use Enter key):")
        instruction_label.setAccessibleDescription("List of news articles that can be opened by double-clicking or pressing Enter")
        
        # Set initial focus
        news_list.setFocus()
        if news_list.count() > 0:
            news_list.setCurrentRow(0)
        
        # Add keyboard navigation
        news_list.keyPressEvent = lambda event: self.handle_news_key_press(event, news_list)
        
        layout.addWidget(instruction_label)
        layout.addWidget(news_list)
    
    def open_news_article(self, item):
        """Open a news article in the default web browser"""
        article_data = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(article_data, dict):
            web_url = article_data.get("web_url", article_data.get("links", {}).get("web", {}).get("href", ""))
            if web_url:
                webbrowser.open(web_url)
            else:
                QMessageBox.information(self, "No Link", "No web link available for this article.")
        else:
            QMessageBox.information(self, "No Link", "No web link available for this article.")
    
    def handle_news_key_press(self, event, news_list):
        """Handle keyboard navigation for news list"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            current_item = news_list.currentItem()
            if current_item:
                self.open_news_article(current_item)
        else:
            # Call the original keyPressEvent
            QListWidget.keyPressEvent(news_list, event)

    def open_config(self):
        details = ["boxscore", "leaders", "standings", "odds", "injuries", "broadcasts", "news", "gameInfo"]
        selected = self.config.get(self.current_league, [])
        # Ensure only valid fields are in the selected list
        selected = [field for field in selected if field in details]
        dlg = ConfigDialog(details, selected, self)
        if dlg.exec():
            self.config[self.current_league] = dlg.get_selected()
            self.load_game_details()

    def previous_day(self):
        """Navigate to previous day's scores"""
        self.current_date -= timedelta(days=1)
        self.load_scores()
        # Restore focus after loading
        QTimer.singleShot(50, lambda: self.scores_list.setFocus())
    
    def next_day(self):
        """Navigate to next day's scores"""
        self.current_date += timedelta(days=1)
        self.load_scores()
        # Restore focus after loading
        QTimer.singleShot(50, lambda: self.scores_list.setFocus())
    
    def set_nav_buttons(self, refresh=False, config=False, date_nav=False):
        btn_layout = QHBoxLayout()
        if self.stack:
            back_btn = QPushButton("Back (Alt+B)")
            back_btn.setShortcut("Alt+B")
            back_btn.clicked.connect(self.go_back)
            btn_layout.addWidget(back_btn)
        if date_nav:
            prev_btn = QPushButton("Previous Day (Alt+P)")
            prev_btn.setShortcut("Alt+P")
            prev_btn.clicked.connect(self.previous_day)
            btn_layout.addWidget(prev_btn)
            
            next_btn = QPushButton("Next Day (Alt+N)")
            next_btn.setShortcut("Alt+N")
            next_btn.clicked.connect(self.next_day)
            btn_layout.addWidget(next_btn)
        if refresh:
            refresh_btn = QPushButton("Refresh")
            refresh_btn.clicked.connect(self.refresh)
            btn_layout.addWidget(refresh_btn)
        if config:
            config_btn = QPushButton("Config")
            config_btn.clicked.connect(self.open_config)
            btn_layout.addWidget(config_btn)
        self.layout().addLayout(btn_layout)

    def go_back(self):
        if not self.stack:
            return
        screen, data = self.stack.pop()
        if screen == "home":
            self.init_home()
        elif screen == "league":
            self.open_league_by_name(data)

    def open_league_by_name(self, league):
        self.clear_layout()
        self.current_league = league
        
        # Add date navigation label
        self.date_label = QLabel()
        self.layout().addWidget(self.date_label)
        
        self.scores_list = QListWidget()
        self.layout().addWidget(QLabel(f"Scores for {league}:"))
        self.layout().addWidget(self.scores_list)
        self.set_nav_buttons(refresh=True, date_nav=True)
        self.scores_list.itemActivated.connect(self.open_scores_item)
        self.load_scores()
        # Use timer to ensure focus is set after UI updates complete
        QTimer.singleShot(50, lambda: self.scores_list.setFocus())

    def refresh(self):
        if hasattr(self, "details_list"):
            self.load_game_details()
            # Restore focus after refresh
            QTimer.singleShot(50, lambda: self.details_list.setFocus())
        elif hasattr(self, "scores_list"):
            self.load_scores()
            # Restore focus after refresh
            QTimer.singleShot(50, lambda: self.scores_list.setFocus())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.go_back()
        elif event.modifiers() == Qt.KeyboardModifier.AltModifier:
            if event.key() == Qt.Key.Key_P and hasattr(self, 'current_date'):
                self.previous_day()
            elif event.key() == Qt.Key.Key_N and hasattr(self, 'current_date'):
                self.next_day()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SportsScoresApp()
    sys.exit(app.exec())
