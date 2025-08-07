#!/usr/bin/env python3
"""Quick script to fix keyboard navigation in both _configure_table methods"""

import re

def fix_main_py():
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to find _configure_table methods
    pattern = r'(def _configure_table\(self, table: QTableWidget\):\s*"""Configure table appearance and behavior"""\s*table\.setEditTriggers\(QTableWidget\.EditTrigger\.NoEditTriggers\)\s*table\.setSelectionBehavior\(QTableWidget\.SelectionBehavior\.SelectRows\)\s*table\.setAlternatingRowColors\(True\)\s*table\.verticalHeader\(\)\.setVisible\(False\))\s*(header = table\.horizontalHeader\(\))'
    
    # Replacement that adds the missing lines
    replacement = r'\1\n        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)\n        \n        # Enable keyboard navigation\n        table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)\n        table.setTabKeyNavigation(True)\n        \n        \2'
    
    # Apply the replacement
    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    if new_content != content:
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully updated both _configure_table methods")
        return True
    else:
        print("No changes made - pattern might not match")
        return False

if __name__ == "__main__":
    fix_main_py()
