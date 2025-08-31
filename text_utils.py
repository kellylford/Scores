"""
Text cleaning utilities for ESPN news content.
Handles potential name replacement patterns and other text processing issues.
"""

import re
from typing import Dict, Optional


class ESPNTextProcessor:
    """Processor for cleaning and fixing ESPN news text content"""
    
    def __init__(self):
        # Common patterns that might indicate unresolved player ID replacements
        self.placeholder_patterns = [
            r'\{\{?\w+\}?\}?',        # {{123}} or {123} or {{unknown_player}}
            r'\[\d+\]',               # [123]
            r'#\d{6,}',               # #123456 (long ID numbers)
            r'player_\d+',            # player_123
            r'athlete_\d+',           # athlete_123
            r'\b\d{6,}\b',            # Standalone long numbers (6+ digits)
        ]
    
    def clean_description(self, description: str, article_data: Optional[Dict] = None) -> str:
        """
        Clean article description text, fixing potential name replacement issues.
        
        Args:
            description: The raw description text from ESPN
            article_data: Optional full article data for context
            
        Returns:
            Cleaned description text
        """
        if not description:
            return description
            
        # Check for placeholder patterns
        has_placeholders = False
        for pattern in self.placeholder_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                has_placeholders = True
                break
        
        if not has_placeholders:
            # No issues detected, return as-is
            return description
            
        # If we found placeholder patterns, try to fix them
        cleaned_text = self._attempt_placeholder_resolution(description, article_data)
        
        # If we couldn't resolve placeholders, provide a fallback
        if self._still_has_placeholders(cleaned_text):
            return self._create_fallback_description(description, article_data)
            
        return cleaned_text
    
    def _attempt_placeholder_resolution(self, text: str, article_data: Optional[Dict]) -> str:
        """
        Attempt to resolve placeholder patterns using available article data.
        """
        # Try to extract player names from other parts of the article
        player_names = self._extract_player_names_from_article(article_data) if article_data else []
        
        # Simple pattern replacement for obvious cases
        # This is a basic implementation - could be enhanced with more sophisticated matching
        cleaned_text = text
        
        # Remove obvious placeholder patterns that we can't resolve
        for pattern in self.placeholder_patterns:
            cleaned_text = re.sub(pattern, '[Player Name]', cleaned_text, flags=re.IGNORECASE)
        
        return cleaned_text
    
    def _extract_player_names_from_article(self, article_data: Dict) -> list:
        """
        Extract player names from article categories or other fields.
        """
        player_names = []
        
        # Check categories for athlete information
        categories = article_data.get('categories', [])
        for category in categories:
            if category.get('type') == 'athlete':
                athlete_name = category.get('description', '')
                if athlete_name:
                    player_names.append(athlete_name)
        
        return player_names
    
    def _still_has_placeholders(self, text: str) -> bool:
        """Check if text still contains unresolved placeholder patterns."""
        for pattern in self.placeholder_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _create_fallback_description(self, original_text: str, article_data: Optional[Dict]) -> str:
        """
        Create a fallback description when we can't resolve placeholders.
        """
        headline = article_data.get('headline', '') if article_data else ''
        
        if headline:
            return f"Story details available in full article: {headline}"
        else:
            return "Full story details available in the complete article."


# Global instance for easy use
text_processor = ESPNTextProcessor()
