"""
Generic RSS-based adapter for status page providers
"""
from abc import abstractmethod
from typing import List, Dict
from .base import BaseAdapter
from ..utils.rss_parser import RSSParser, HTMLIncidentParser


class RSSAdapter(BaseAdapter):
    """
    Base adapter for RSS-based status pages.
    Subclasses should define RSS_FEED_URL and implement incident parsing logic.
    """
    
    # Subclasses must define these
    RSS_FEED_URL: str = None
    INCIDENT_PARSER_TYPE: str = None  # "bolna", "claude", or None for generic
    
    def __init__(self):
        self._name = self.__class__.__name__.replace("Adapter", "")
        self.rss_parser = RSSParser()
        self.html_parser = HTMLIncidentParser()
    
    @property
    def name(self) -> str:
        return self._name
    
    async def fetch_latest_incidents_async(self, limit: int = 3) -> List[Dict]:
        """Fetch latest incidents from RSS feed"""
        if not self.RSS_FEED_URL:
            raise NotImplementedError("RSS_FEED_URL must be defined in subclass")
        
        incidents = await self.rss_parser.fetch_rss_feed_async(
            self.RSS_FEED_URL, 
            max_items=limit
        )
        return incidents
    
    async def process_incident_async(self, incident: Dict) -> List[Dict]:
        """
        Process RSS incident and extract affected services.
        
        By default, tries to:
        1. Parse services from RSS description HTML (OpenAI-style)
        2. Fetch incident page and parse with specific parser
        3. Fallback to incident title as service name
        """
        title = incident.get('title', 'Unknown Incident')
        pub_date = incident.get('pub_date', 'Unknown Time')
        link = incident.get('link', '')
        description = incident.get('description', '')
        
        # Strategy 1: Try to extract services from RSS description HTML
        services_from_rss = self.rss_parser.extract_services_from_html(description)
        
        if services_from_rss:
            # Found services in RSS feed directly
            return self._format_incidents(services_from_rss, title, pub_date)
        
        # Strategy 2: Parse incident page if parser type is specified
        if self.INCIDENT_PARSER_TYPE and link and link != 'N/A':
            try:
                services_from_page = await self._parse_incident_page(link)
                if services_from_page:
                    return self._format_incidents(services_from_page, title, pub_date)
            except Exception as e:
                # Log error but continue to fallback
                pass
        
        # Strategy 3: Fallback - use title or custom extraction
        fallback_services = await self._extract_fallback_services(incident)
        return self._format_incidents(fallback_services, title, pub_date)
    
    async def _parse_incident_page(self, url: str) -> List[str]:
        """Parse incident page to extract affected services"""
        return await self.html_parser.get_affected_services_async(
            url, 
            parser_type=self.INCIDENT_PARSER_TYPE
        )
    
    async def _extract_fallback_services(self, incident: Dict) -> List[str]:
        """
        Fallback service extraction. Can be overridden by subclasses.
        Default: returns ["General Service"]
        """
        return ["General Service"]
    
    def _format_incidents(self, services: List[str], title: str, pub_date: str) -> List[Dict]:
        """Format services into incident dictionaries"""
        results = []
        for service in services:
            # Try to separate group and component from service name
            # e.g., "API - Chat Completions" -> group="API", component="Chat Completions"
            if " - " in service:
                parts = service.split(" - ", 1)
                group = parts[0].strip()
                component = parts[1].strip()
            else:
                group = self.name
                component = service
            
            results.append({
                "group": group,
                "component": component,
                "time_created": pub_date,
                "status_message": title
            })
        
        return results
