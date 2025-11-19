"""
RSS Feed and HTML parsing utilities for status page monitoring
"""
import re
import xml.etree.ElementTree as ET
from html import unescape
from typing import List, Dict, Optional
import aiohttp
from bs4 import BeautifulSoup


class RSSParser:
    """Generic RSS feed parser with HTML content extraction"""
    
    @staticmethod
    async def fetch_rss_feed_async(url: str, max_items: int = 3) -> List[Dict]:
        """
        Fetch and parse RSS feed asynchronously
        
        Args:
            url: RSS feed URL
            max_items: Maximum number of items to return
            
        Returns:
            List of incident dictionaries with keys: id, title, link, pub_date, description
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                content = await response.read()
        
        root = ET.fromstring(content)
        items = root.findall('.//item')[:max_items]
        
        incidents = []
        for item in items:
            title = item.find('title')
            link = item.find('link')
            pub_date = item.find('pubDate')
            description = item.find('description')
            guid = item.find('guid')
            
            # Extract incident ID from GUID or link
            incident_id = None
            if guid is not None and guid.text:
                incident_id = guid.text.split('/')[-1]
            elif link is not None and link.text:
                incident_id = link.text.split('/')[-1]
            
            incidents.append({
                'id': incident_id or title.text if title is not None else 'unknown',
                'title': title.text if title is not None else 'N/A',
                'link': link.text if link is not None else 'N/A',
                'pub_date': pub_date.text if pub_date is not None else 'N/A',
                'description': description.text if description is not None else 'N/A'
            })
        
        return incidents
    
    @staticmethod
    def clean_html(html_text: str) -> str:
        """Remove HTML tags and clean up text"""
        if not html_text:
            return "N/A"
        
        # Unescape HTML entities
        text = unescape(html_text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def extract_services_from_html(html_content: str) -> List[str]:
        """
        Extract service names from HTML content (RSS description)
        Works for OpenAI-style RSS feeds with <li>Service (Status)</li> format
        
        Args:
            html_content: HTML string from RSS feed description
            
        Returns:
            List of service names
        """
        if not html_content:
            return []
        
        # Unescape HTML entities
        html = unescape(html_content)
        
        # Look for the "Affected components" section
        # Pattern: <li>Service Name (Status)</li>
        pattern = r'<li>([^(]+)\s*\([^)]+\)</li>'
        matches = re.findall(pattern, html)
        
        services = [service_name.strip() for service_name in matches]
        return services


class HTMLIncidentParser:
    """Parser for extracting incident details from status page HTML"""
    
    @staticmethod
    async def fetch_incident_page_async(url: str) -> str:
        """Fetch incident page HTML content"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                return await response.text()
    
    @staticmethod
    def parse_bolna_incident(html: str) -> List[str]:
        """
        Parse Bolna (Better Stack) incident page for affected services
        
        Args:
            html: HTML content of the incident page
            
        Returns:
            List of affected service names
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Collect all visible text in order
        texts = list(soup.stripped_strings)
        
        affected_services = []
        
        i = 0
        while i < len(texts):
            if texts[i].strip() == "Affected services":
                # Look ahead for the next meaningful text
                j = i + 1
                while j < len(texts):
                    candidate = texts[j].strip()
                    if candidate and candidate not in {"* * *", "*", "Affected services"}:
                        affected_services.append(candidate)
                        break
                    j += 1
                i = j
            else:
                i += 1
        
        # Remove duplicates while preserving order
        seen = set()
        unique_services = []
        for s in affected_services:
            if s not in seen:
                seen.add(s)
                unique_services.append(s)
        
        return unique_services
    
    @staticmethod
    def parse_claude_incident(html: str) -> List[str]:
        """
        Parse Claude incident page for affected services
        
        Args:
            html: HTML content of the incident page
            
        Returns:
            List of affected service names
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try to find a phrase like "This incident affected"
        text_elements = soup.find_all(string=True)
        
        for t in text_elements:
            # Normalize whitespace and lowercase
            normalized = " ".join(t.split()).lower()
            if "this incident affected:" in normalized:
                # Extract substring after colon
                part = t.split(":", 1)[1].strip()
                
                # Parse the comma-separated and "and"-separated list
                # Replace " and " with ", " to handle lists like "A, B, and C"
                part = part.replace(" and ", ", ")
                
                # Split by comma and clean up each service name
                services = [s.strip().rstrip('.') for s in part.split(",")]
                
                # Remove empty strings
                services = [s for s in services if s]
                
                return services
        
        # Fallback to looking at the title
        title_tag = soup.find("h1")
        if title_tag:
            return [title_tag.get_text().strip()]
        
        return ["Unknown Service"]
    
    @staticmethod
    async def get_affected_services_async(url: str, parser_type: str = "bolna") -> List[str]:
        """
        Fetch and parse incident page to extract affected services
        
        Args:
            url: Incident page URL
            parser_type: Type of parser to use ("bolna" or "claude")
            
        Returns:
            List of affected service names
        """
        html = await HTMLIncidentParser.fetch_incident_page_async(url)
        
        if parser_type.lower() == "bolna":
            return HTMLIncidentParser.parse_bolna_incident(html)
        elif parser_type.lower() == "claude":
            return HTMLIncidentParser.parse_claude_incident(html)
        else:
            # Generic fallback - look for title
            soup = BeautifulSoup(html, 'html.parser')
            title_tag = soup.find("h1")
            if title_tag:
                return [title_tag.get_text().strip()]
            return ["Unknown Service"]
