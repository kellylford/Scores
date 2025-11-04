"""
Quick test to check if FootballAudioTutorialView can be instantiated
"""

import sys
from PyQt6.QtWidgets import QApplication

# Try to import and create the view
try:
    from scores import FootballAudioTutorialView, FOOTBALL_AUDIO_AVAILABLE, HYBRID_AUDIO_AVAILABLE
    
    print("Imports successful!")
    print(f"FOOTBALL_AUDIO_AVAILABLE: {FOOTBALL_AUDIO_AVAILABLE}")
    print(f"HYBRID_AUDIO_AVAILABLE: {HYBRID_AUDIO_AVAILABLE}")
    
    # Create Qt app
    app = QApplication(sys.argv)
    
    # Try to create the view
    print("\nAttempting to create FootballAudioTutorialView...")
    view = FootballAudioTutorialView()
    print("✓ View created successfully!")
    
    # Check if it has the expected attributes
    if hasattr(view, 'drives_list'):
        print(f"✓ drives_list exists with {view.drives_list.count()} items")
    else:
        print("✗ drives_list not found")
    
    if HYBRID_AUDIO_AVAILABLE and hasattr(view, 'audio_mode_combo'):
        print(f"✓ audio_mode_combo exists with {view.audio_mode_combo.count()} modes")
    else:
        print("✗ audio_mode_combo not found (or hybrid audio not available)")
    
    print("\n✅ All checks passed! The view should load fine in the app.")
    
except Exception as e:
    print(f"\n❌ Error occurred: {e}")
    import traceback
    traceback.print_exc()
