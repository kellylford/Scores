#!/usr/bin/env python3
"""
Fix the StandingsTable creation to include league and expanded parameters
"""

def fix_standings_table():
    lines = []
    with open('scores.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Track whether we're in the StandingsDialog class (not StandingsDetailDialog)
    in_standings_dialog = False
    changes_made = 0
    
    for i, line in enumerate(lines):
        if 'class StandingsDialog(QDialog):' in line:
            in_standings_dialog = True
            print(f'Found StandingsDialog at line {i+1}')
        elif in_standings_dialog and line.strip().startswith('class ') and 'StandingsDialog' not in line:
            in_standings_dialog = False
        elif in_standings_dialog:
            # Fix _create_division_table method
            if 'table = StandingsTable(parent=self, division_name=division_name)' in line:
                print(f'Fixing line {i+1}: {line.strip()}')
                lines[i] = line.replace(
                    'table = StandingsTable(parent=self, division_name=division_name)',
                    'table = StandingsTable(parent=self, division_name=division_name, league=self.league, expanded=self.expanded_view)'
                )
                changes_made += 1
            # Fix _create_single_standings_table method
            elif 'table = StandingsTable(parent=self)' in line and i > 0:
                # Check if we're in the _create_single_standings_table method
                method_context = ''.join(lines[max(0, i-5):i+1])
                if '_create_single_standings_table' in method_context:
                    print(f'Fixing line {i+1}: {line.strip()}')
                    lines[i] = line.replace(
                        'table = StandingsTable(parent=self)',
                        'table = StandingsTable(parent=self, league=self.league, expanded=self.expanded_view)'
                    )
                    changes_made += 1
    
    if changes_made > 0:
        with open('scores.py', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f'Successfully made {changes_made} changes to scores.py')
    else:
        print('No changes needed')

if __name__ == '__main__':
    fix_standings_table()
