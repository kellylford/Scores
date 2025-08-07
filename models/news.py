from typing import Dict, Union

class NewsData:
    """Data model for news articles"""
    def __init__(self, raw_data: Union[Dict, str]):
        if isinstance(raw_data, dict):
            self.headline = raw_data.get("headline", raw_data.get("title", "No headline"))
            self.description = raw_data.get("description", "")
            self.web_url = raw_data.get("web_url") or raw_data.get("links", {}).get("web", {}).get("href", "")
            self.mobile_url = raw_data.get("mobile_url") or raw_data.get("links", {}).get("mobile", {}).get("href", "")
            self.published = raw_data.get("published", "")
            self.byline = raw_data.get("byline", "")
        else:
            self.headline = str(raw_data)
            self.description = ""
            self.web_url = ""
            self.mobile_url = ""
            self.published = ""
            self.byline = ""

    def get_display_text(self) -> str:
        display_text = self.headline
        if self.byline:
            display_text += f" | {self.byline}"
        if self.published:
            display_text += f" | {self.published[:10]}"
        if self.description:
            display_text += f"\n  {self.description[:100]}{'...' if len(self.description) > 100 else ''}"
        return display_text

    def has_web_url(self) -> bool:
        return bool(self.web_url)
