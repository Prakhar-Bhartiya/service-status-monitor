"""
Bolna status page adapter using RSS feed and HTML parsing
"""
from typing import List, Dict
from .rss_adapter import RSSAdapter


class BolnaAdapter(RSSAdapter):
    """
    Adapter for Bolna status page (Better Stack platform)
    Uses RSS feed + HTML parsing for incident details
    """
    
    RSS_FEED_URL = "https://status.bolna.ai/feed.rss"
    INCIDENT_PARSER_TYPE = "bolna"
    
    def __init__(self):
        super().__init__()
        self._name = "Bolna"
    
    async def _extract_fallback_services(self, incident: Dict) -> List[str]:
        """
        Fallback for Bolna when services can't be extracted from RSS or page.
        Bolna-specific: check for keywords in title
        """
        title = incident.get('title', '').lower()
        
        # Common Bolna services based on their infrastructure
        if 'twilio' in title:
            return ['Twilio']
        elif 'voice' in title:
            return ['Voice Service']
        elif 'api' in title:
            return ['API']
        elif 'webhook' in title:
            return ['Webhooks']
        
        return ["Bolna Platform"]
