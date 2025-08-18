#!/usr/bin/env python3
"""
Minimal test to debug the statistics table display issue
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTableWidget, QLabel, QPushButton, QTableWidgetItem, QListWidgetItem
from PyQt6.QtCore import Qt
from services.api_service import ApiService

class MinimalStatsTest(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal Statistics Test")
        self.resize(800, 600)
        self.statistics_data = None
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        self.title_label = QLabel("Minimal Statistics Test")
        layout.addWidget(self.title_label)
        
        # Horizontal layout for list and table
        h_layout = QHBoxLayout()
        
        # Left: Stats list
        self.stats_list = QListWidget()
        self.stats_list.setMaximumWidth(300)
        self.stats_list.itemClicked.connect(self.on_stat_selected)
        h_layout.addWidget(self.stats_list)
        
        # Right: Results table
        self.results_table = QTableWidget()
        self.results_table.hide()  # Hide initially
        h_layout.addWidget(self.results_table)
        
        layout.addLayout(h_layout)
        
        # Debug info
        self.debug_label = QLabel("Debug info will appear here")
        layout.addWidget(self.debug_label)
        
        self.setLayout(layout)
    
    def load_data(self):
        """Load statistics data"""
        try:
            print("Loading MLB statistics...")
            self.statistics_data = ApiService.get_statistics("MLB")
            
            if self.statistics_data:
                player_stats = self.statistics_data.get("player_stats", [])
                print(f"Loaded {len(player_stats)} player stat categories")
                
                # Populate stats list
                for category in player_stats:
                    category_name = category.get("category", "Unknown")
                    stats_list = category.get("stats", [])
                    
                    # Group by stat types
                    stat_types = {}
                    for stat in stats_list:
                        stat_name = stat.get("stat_name", "Unknown")
                        if stat_name not in stat_types:
                            stat_types[stat_name] = []
                        stat_types[stat_name].append(stat)
                    
                    # Add each unique stat type
                    for stat_name, stats in stat_types.items():
                        display_name = f"{stat_name} ({category_name})"
                        item = QListWidgetItem(display_name)
                        item.setData(Qt.ItemDataRole.UserRole, {
                            'name': display_name,
                            'category': category_name,
                            'stat_name': stat_name,
                            'data': stats,
                            'type': 'player'
                        })
                        self.stats_list.addItem(item)
                
                self.debug_label.setText(f"Loaded {self.stats_list.count()} statistics")
                print(f"Added {self.stats_list.count()} stats to list")
                
                # Auto-select first item for testing
                if self.stats_list.count() > 0:
                    print("Auto-selecting first statistic for testing...")
                    first_item = self.stats_list.item(0)
                    self.stats_list.setCurrentItem(first_item)
                    self.on_stat_selected(first_item)
                
            else:
                self.debug_label.setText("No data loaded")
                print("No statistics data returned")
                
        except Exception as e:
            self.debug_label.setText(f"Error: {str(e)}")
            print(f"Error loading data: {e}")
            import traceback
            traceback.print_exc()
    
    def on_stat_selected(self, item):
        """Handle stat selection"""
        try:
            stat_info = item.data(Qt.ItemDataRole.UserRole)
            if not stat_info:
                print("No stat_info data in item")
                return
            
            stat_name = stat_info.get('stat_name', 'Unknown')
            data = stat_info.get('data', [])
            
            print(f"\n=== SELECTED STAT: {stat_name} ===")
            print(f"Data count: {len(data)}")
            print(f"First 3 data items: {data[:3]}")
            
            # Clear and setup table
            self.results_table.clear()
            self.results_table.show()
            
            # Sort data safely
            def safe_float_convert(value):
                """Safely convert value to float for sorting"""
                try:
                    # Handle different value formats
                    if isinstance(value, (int, float)):
                        return float(value)
                    
                    value_str = str(value).strip()
                    
                    # Handle empty or None values
                    if not value_str or value_str.lower() in ['none', 'n/a', '']:
                        return 0.0
                    
                    # Handle fraction format like "1-1" (batting average as hits-at bats)
                    if '-' in value_str and value_str.count('-') == 1:
                        parts = value_str.split('-')
                        if len(parts) == 2 and parts[0].strip().isdigit() and parts[1].strip().split(',')[0].strip().isdigit():
                            hits = float(parts[0].strip())
                            at_bats = float(parts[1].strip().split(',')[0].strip())  # Remove trailing text like ", R"
                            return hits / at_bats if at_bats > 0 else 0.0
                    
                    # Handle percentage format like "0.327" or ".327"
                    if '.' in value_str:
                        clean_val = value_str.split(',')[0].strip()  # Remove trailing text
                        return float(clean_val)
                    
                    # Handle plain numbers
                    clean_val = value_str.split(',')[0].strip()  # Remove trailing text
                    if clean_val.replace('.', '').isdigit():
                        return float(clean_val)
                    
                    return 0.0
                    
                except Exception as e:
                    print(f"Warning: Could not convert '{value}' to float: {e}")
                    return 0.0
            
            sorted_data = sorted(data, key=lambda x: safe_float_convert(x.get('value', 0)), reverse=True)
            top_data = sorted_data[:20]  # Top 20 for testing
            
            print(f"Sorted data, showing top {len(top_data)}")
            
            # Setup table
            self.results_table.setRowCount(len(top_data))
            self.results_table.setColumnCount(4)
            self.results_table.setHorizontalHeaderLabels(["Rank", "Player", "Team", stat_name])
            
            # Populate data
            for row, stat in enumerate(top_data):
                rank = str(row + 1)
                player_name = stat.get("player_name", "Unknown")
                team = stat.get("team", "")
                value = str(stat.get("value", ""))
                
                self.results_table.setItem(row, 0, QTableWidgetItem(rank))
                self.results_table.setItem(row, 1, QTableWidgetItem(player_name))
                self.results_table.setItem(row, 2, QTableWidgetItem(team))
                self.results_table.setItem(row, 3, QTableWidgetItem(value))
                
                if row < 3:
                    print(f"Row {row}: {rank}, {player_name}, {team}, {value}")
            
            # Force update
            self.results_table.resizeColumnsToContents()
            self.results_table.update()
            
            self.debug_label.setText(f"Showing {stat_name}: {len(top_data)} players")
            print(f"Table setup complete - Rows: {self.results_table.rowCount()}, Visible: {self.results_table.isVisible()}")
            
        except Exception as e:
            print(f"Error in on_stat_selected: {e}")
            import traceback
            traceback.print_exc()
            self.debug_label.setText(f"Error: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = MinimalStatsTest()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
