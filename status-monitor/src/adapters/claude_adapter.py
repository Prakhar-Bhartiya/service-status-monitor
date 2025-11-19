"""
Claude status page adapter using RSS feed and HTML parsing
"""
from typing import List, Dict
from .rss_adapter import RSSAdapter


class ClaudeAdapter(RSSAdapter):
    """
    Adapter for Claude/Anthropic status page
    Uses RSS feed + HTML parsing for incident details
    """
    
    RSS_FEED_URL = "https://status.claude.com/history.rss"
    INCIDENT_PARSER_TYPE = "claude"
    
    def __init__(self):
        super().__init__()
        self._name = "Claude"
    
    async def _extract_fallback_services(self, incident: Dict) -> List[str]:
        """
        Fallback for Claude when services can't be extracted from RSS or page.
        Claude-specific: check for keywords in title
        """
        title = incident.get('title', '').lower()
        
        # Common Claude services
        if 'api' in title:
            return ['Claude API']
        elif 'claude.ai' in title or 'web' in title:
            return ['claude.ai']
        elif 'platform' in title:
            return ['platform.claude.com']
        elif 'console' in title:
            return ['Console']
        
        return ["Claude Service"]
