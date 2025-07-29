"""
Tkinter Sports Scores Application
Accessible desktop app using Python's native GUI toolkit
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import threading
import time
from datetime import datetime
import webbrowser

class AccessibleTreeview(ttk.Treeview):
    """Enhanced Treeview with better keyboard navigation and accessibility"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_keyboard_navigation()
        self.current_announcements = []
        
    def setup_keyboard_navigation(self):
        """Setup enhanced keyboard navigation"""
        self.bind('<KeyPress>', self.on_key_press)
        self.bind('<FocusIn>', self.on_focus_in)
        self.bind('<FocusOut>', self.on_focus_out)
        
    def on_key_press(self, event):
        """Handle keyboard navigation with announcements"""
        if event.keysym in ['Up', 'Down', 'Left', 'Right', 'Home', 'End']:
            # Schedule announcement after selection change
            self.after(50, self.announce_current_selection)
            
    def on_focus_in(self, event):
        """Announce widget focus"""
        self.announce("Table focused. Use arrow keys to navigate.")
        
    def on_focus_out(self, event):
        """Handle focus leaving widget"""
        pass
        
    def announce_current_selection(self):
        """Announce current row content for screen readers"""
        selection = self.selection()
        if selection:
            item = selection[0]
            values = self.item(item, 'values')
            if values:
                # Create readable announcement
                announcement = f"Row {self.index(item) + 1}: "
                for i, value in enumerate(values):
                    col_name = self['columns'][i] if i < len(self['columns']) else f"Column {i+1}"
                    announcement += f"{col_name}: {value}. "
                self.announce(announcement)
    
    def announce(self, message):
        """Announce message to screen readers via window title (accessible method)"""
        try:
            # Use master window title for announcements (screen readers monitor this)
            root = self.winfo_toplevel()
            original_title = root.title()
            root.title(f"{original_title} - {message}")
            # Restore original title after brief delay
            root.after(2000, lambda: root.title(original_title))
        except:
            pass

class SportsScoresApp:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_ui()
        self.setup_accessibility()
        self.data_cache = {}
        self.current_sort_column = None
        self.current_sort_reverse = False
        
    def setup_window(self):
        """Configure main window"""
        self.root.title("Sports Scores - Accessible Desktop App")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Configure for high contrast themes
        self.root.configure(bg='#ffffff')
        
        # Ensure window is accessible
        self.root.focus_set()
        
    def setup_ui(self):
        """Create the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="⚾ Sports Scores", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky=tk.W)
        
        # Navigation frame
        nav_frame = ttk.LabelFrame(main_frame, text="Navigation", padding="5")
        nav_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        nav_frame.columnconfigure(4, weight=1)
        
        # Navigation buttons
        self.standings_btn = ttk.Button(nav_frame, text="MLB Standings", 
                                       command=self.show_standings,
                                       takefocus=True)
        self.standings_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.scores_btn = ttk.Button(nav_frame, text="Live Scores", 
                                    command=self.show_scores,
                                    takefocus=True)
        self.scores_btn.grid(row=0, column=1, padx=5)
        
        self.stats_btn = ttk.Button(nav_frame, text="Team Stats", 
                                   command=self.show_stats,
                                   takefocus=True)
        self.stats_btn.grid(row=0, column=2, padx=5)
        
        self.refresh_btn = ttk.Button(nav_frame, text="🔄 Refresh", 
                                     command=self.refresh_data,
                                     takefocus=True)
        self.refresh_btn.grid(row=0, column=3, padx=5)
        
        # Status label
        self.status_label = ttk.Label(nav_frame, text="Ready")
        self.status_label.grid(row=0, column=4, sticky=tk.E)
        
        # Content area
        content_frame = ttk.LabelFrame(main_frame, text="Data View", padding="5")
        content_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)
        
        # Filter frame
        filter_frame = ttk.Frame(content_frame)
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        filter_frame.columnconfigure(2, weight=1)
        
        # Division filter
        ttk.Label(filter_frame, text="Division:").grid(row=0, column=0, sticky=tk.W)
        self.division_var = tk.StringVar(value="All")
        self.division_combo = ttk.Combobox(filter_frame, textvariable=self.division_var,
                                          values=["All", "AL East", "AL Central", "AL West", 
                                                 "NL East", "NL Central", "NL West"],
                                          state="readonly", width=15)
        self.division_combo.grid(row=0, column=1, padx=(5, 15), sticky=tk.W)
        self.division_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
        # Search
        ttk.Label(filter_frame, text="Search:").grid(row=0, column=2, sticky=tk.E, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=20)
        self.search_entry.grid(row=0, column=3, sticky=tk.E)
        self.search_var.trace('w', self.on_search_change)
        
        # Create accessible treeview
        self.tree = AccessibleTreeview(content_frame, show='headings', selectmode='browse')
        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=self.tree.yview)
        v_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(content_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        h_scrollbar.grid(row=2, column=0, sticky=(tk.W, tk.E))
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Info frame
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        info_frame.columnconfigure(1, weight=1)
        
        self.info_label = ttk.Label(info_frame, text="Use arrow keys to navigate table. Press F5 to refresh data.")
        self.info_label.grid(row=0, column=0, sticky=tk.W)
        
        self.last_update_label = ttk.Label(info_frame, text="")
        self.last_update_label.grid(row=0, column=1, sticky=tk.E)
        
    def setup_accessibility(self):
        """Configure accessibility features"""
        # Keyboard shortcuts
        self.root.bind('<F5>', lambda e: self.refresh_data())
        self.root.bind('<Control-r>', lambda e: self.refresh_data())
        self.root.bind('<Alt-1>', lambda e: self.show_standings())
        self.root.bind('<Alt-2>', lambda e: self.show_scores())
        self.root.bind('<Alt-3>', lambda e: self.show_stats())
        
        # Focus management
        self.standings_btn.focus_set()
        
        # Bind table sorting
        self.tree.bind('<Button-1>', self.on_treeview_click)
        self.tree.bind('<Return>', self.on_treeview_activate)
        
    def setup_table_columns(self, columns, headings):
        """Configure table columns with accessibility features"""
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'
        
        for col, heading in zip(columns, headings):
            self.tree.heading(col, text=heading, anchor='w')
            self.tree.column(col, width=120, minwidth=80)
            # Make headers clickable for sorting
            self.tree.heading(col, command=lambda c=col: self.sort_table(c))
    
    def sort_table(self, column):
        """Sort table by column with accessibility announcements"""
        # Toggle sort direction if same column
        if self.current_sort_column == column:
            self.current_sort_reverse = not self.current_sort_reverse
        else:
            self.current_sort_reverse = False
            
        self.current_sort_column = column
        
        # Get all items and sort
        items = [(self.tree.set(item, column), item) for item in self.tree.get_children('')]
        
        # Sort numerically if possible, otherwise alphabetically
        try:
            items.sort(key=lambda x: float(x[0].replace('%', '').replace('-', '0')), 
                      reverse=self.current_sort_reverse)
        except:
            items.sort(key=lambda x: x[0].lower(), reverse=self.current_sort_reverse)
        
        # Rearrange items
        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)
            
        # Update heading to show sort direction
        direction = "↓" if self.current_sort_reverse else "↑"
        for col in self.tree['columns']:
            if col == column:
                self.tree.heading(col, text=f"{self.tree.heading(col, 'text').split()[0]} {direction}")
            else:
                heading_text = self.tree.heading(col, 'text').split()[0]
                self.tree.heading(col, text=heading_text)
        
        # Announce sort
        direction_text = "descending" if self.current_sort_reverse else "ascending"
        self.announce(f"Table sorted by {column} in {direction_text} order")
    
    def on_treeview_click(self, event):
        """Handle treeview clicks"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "heading":
            column = self.tree.identify_column(event.x)
            if column:
                col_name = self.tree['columns'][int(column[1:]) - 1]
                self.sort_table(col_name)
    
    def on_treeview_activate(self, event):
        """Handle Enter key on treeview"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')
            if values:
                # Announce detailed row information
                details = "Selected row details: "
                for i, value in enumerate(values):
                    col_name = self.tree['columns'][i] if i < len(self.tree['columns']) else f"Column {i+1}"
                    details += f"{col_name}: {value}. "
                self.announce(details)
    
    def show_standings(self):
        """Display MLB standings"""
        self.set_status("Loading standings...")
        self.current_view = "standings"
        
        # Setup columns for standings
        columns = ['team', 'wins', 'losses', 'win_pct', 'games_behind', 'division']
        headings = ['Team', 'Wins', 'Losses', 'Win %', 'GB', 'Division']
        self.setup_table_columns(columns, headings)
        
        # Load data in background
        threading.Thread(target=self.load_standings_data, daemon=True).start()
        
    def show_scores(self):
        """Display live scores"""
        self.set_status("Loading scores...")
        self.current_view = "scores"
        
        # Setup columns for scores
        columns = ['game', 'status', 'away_team', 'away_score', 'home_team', 'home_score', 'inning']
        headings = ['Game', 'Status', 'Away Team', 'Away Score', 'Home Team', 'Home Score', 'Inning']
        self.setup_table_columns(columns, headings)
        
        # Load data in background
        threading.Thread(target=self.load_scores_data, daemon=True).start()
        
    def show_stats(self):
        """Display team statistics"""
        self.set_status("Loading team stats...")
        self.current_view = "stats"
        
        # Setup columns for stats
        columns = ['team', 'batting_avg', 'home_runs', 'rbis', 'era', 'wins', 'losses']
        headings = ['Team', 'Batting Avg', 'Home Runs', 'RBIs', 'ERA', 'Wins', 'Losses']
        self.setup_table_columns(columns, headings)
        
        # Load data in background
        threading.Thread(target=self.load_stats_data, daemon=True).start()
    
    def load_standings_data(self):
        """Load standings data from ESPN API"""
        try:
            # Sample data for demonstration (replace with real API call)
            standings_data = [
                ("New York Yankees", "95", "67", ".586", "-", "AL East"),
                ("Houston Astros", "93", "69", ".574", "2.0", "AL West"),
                ("Los Angeles Dodgers", "100", "62", ".617", "-", "NL West"),
                ("Atlanta Braves", "98", "64", ".605", "2.0", "NL East"),
                ("Philadelphia Phillies", "87", "75", ".537", "11.0", "NL East"),
                ("San Diego Padres", "82", "80", ".506", "18.0", "NL West"),
                ("Milwaukee Brewers", "86", "76", ".531", "9.0", "NL Central"),
                ("St. Louis Cardinals", "78", "84", ".481", "17.0", "NL Central"),
            ]
            
            # Update UI on main thread
            self.root.after(0, lambda: self.update_table_data(standings_data))
            self.root.after(0, lambda: self.set_status("Standings loaded"))
            self.root.after(0, lambda: self.update_last_updated())
            
        except Exception as e:
            self.root.after(0, lambda: self.set_status(f"Error loading standings: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load standings: {str(e)}"))
    
    def load_scores_data(self):
        """Load live scores data"""
        try:
            # Sample data for demonstration
            scores_data = [
                ("Game 1", "Final", "Boston Red Sox", "7", "New York Yankees", "9", "9th"),
                ("Game 2", "Live", "Los Angeles Angels", "3", "Houston Astros", "5", "6th"),
                ("Game 3", "Scheduled", "Toronto Blue Jays", "-", "Tampa Bay Rays", "-", "-"),
                ("Game 4", "Final", "Chicago Cubs", "4", "Milwaukee Brewers", "2", "9th"),
                ("Game 5", "Live", "San Francisco Giants", "1", "Los Angeles Dodgers", "3", "4th"),
            ]
            
            self.root.after(0, lambda: self.update_table_data(scores_data))
            self.root.after(0, lambda: self.set_status("Scores loaded"))
            self.root.after(0, lambda: self.update_last_updated())
            
        except Exception as e:
            self.root.after(0, lambda: self.set_status(f"Error loading scores: {str(e)}"))
    
    def load_stats_data(self):
        """Load team statistics data"""
        try:
            # Sample data for demonstration
            stats_data = [
                ("New York Yankees", ".267", "254", "789", "3.72", "95", "67"),
                ("Houston Astros", ".263", "214", "765", "3.38", "93", "69"),
                ("Los Angeles Dodgers", ".249", "212", "724", "3.17", "100", "62"),
                ("Atlanta Braves", ".271", "307", "867", "4.05", "98", "64"),
                ("Philadelphia Phillies", ".252", "234", "743", "4.21", "87", "75"),
            ]
            
            self.root.after(0, lambda: self.update_table_data(stats_data))
            self.root.after(0, lambda: self.set_status("Team stats loaded"))
            self.root.after(0, lambda: self.update_last_updated())
            
        except Exception as e:
            self.root.after(0, lambda: self.set_status(f"Error loading stats: {str(e)}"))
    
    def update_table_data(self, data):
        """Update table with new data"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Insert new data
        for row in data:
            self.tree.insert('', 'end', values=row)
            
        # Store data for filtering
        self.current_data = data
        
        # Announce data update
        self.announce(f"Table updated with {len(data)} rows")
    
    def on_filter_change(self, event=None):
        """Handle division filter change"""
        if not hasattr(self, 'current_data'):
            return
            
        division = self.division_var.get()
        search_term = self.search_var.get().lower()
        
        filtered_data = self.current_data
        
        # Apply division filter
        if division != "All" and self.current_view == "standings":
            filtered_data = [row for row in filtered_data if division in row[-1]]
            
        # Apply search filter
        if search_term:
            filtered_data = [row for row in filtered_data 
                           if any(search_term in str(cell).lower() for cell in row)]
        
        self.update_table_data(filtered_data)
        
        # Announce filter results
        if division != "All" or search_term:
            self.announce(f"Filter applied. Showing {len(filtered_data)} rows")
    
    def on_search_change(self, *args):
        """Handle search text change"""
        # Debounce search
        if hasattr(self, 'search_timer'):
            self.root.after_cancel(self.search_timer)
        self.search_timer = self.root.after(500, self.on_filter_change)
    
    def refresh_data(self):
        """Refresh current data view"""
        if hasattr(self, 'current_view'):
            if self.current_view == "standings":
                self.show_standings()
            elif self.current_view == "scores":
                self.show_scores()
            elif self.current_view == "stats":
                self.show_stats()
        self.announce("Data refreshed")
    
    def set_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
        
    def update_last_updated(self):
        """Update last updated timestamp"""
        now = datetime.now().strftime("%H:%M:%S")
        self.last_update_label.config(text=f"Last updated: {now}")
    
    def announce(self, message):
        """Announce message for screen readers"""
        try:
            original_title = self.root.title()
            self.root.title(f"{original_title} - {message}")
            self.root.after(2000, lambda: self.root.title(original_title))
        except:
            pass
    
    def run(self):
        """Start the application"""
        # Load initial data
        self.show_standings()
        
        # Start main loop
        self.root.mainloop()

def main():
    """Main entry point"""
    app = SportsScoresApp()
    app.run()

if __name__ == "__main__":
    main()
