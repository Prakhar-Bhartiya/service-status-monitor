import aiohttp
from typing import List, Dict
from .base import BaseAdapter

class OpenAIAdapter(BaseAdapter):
    COMPONENTS_URL = "https://status.openai.com/proxy/status.openai.com"
    INCIDENTS_URL = "https://status.openai.com/api/v2/incidents.json"
    INCIDENT_DETAIL_URL = "https://statuspage.incident.io/proxy/openai-1/incidents/{incident_id}"

    def __init__(self):
        self._name = "OpenAI"
        self.component_map = None

    @property
    def name(self) -> str:
        return self._name

    async def fetch_components_async(self) -> Dict[str, Dict[str, str]]:
        """Fetch and cache component mapping"""
        if self.component_map:
            return self.component_map
            
        async with aiohttp.ClientSession() as session:
            async with session.get(self.COMPONENTS_URL, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
        
        component_dict = {}
        summary = data.get("summary", {})
        structure = summary.get("structure", {})
        items = structure.get("items", [])
        
        for item in items:
            group = item.get("group", {})
            group_name = group.get("name", "Unknown Group")
            components = group.get("components", [])
            for comp in components:
                comp_id = comp.get("component_id")
                comp_name = comp.get("name", "Unknown Component")
                component_dict[comp_id] = {
                    "group": group_name,
                    "component": comp_name
                }
        
        self.component_map = component_dict
        return component_dict

    async def fetch_latest_incidents_async(self, limit: int = 3) -> List[Dict]:
        """Fetch latest incidents asynchronously"""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.INCIDENTS_URL, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
        
        incidents = data.get("incidents", [])
        return incidents[:limit]

    async def fetch_affected_components_async(self, incident_id: str) -> List[Dict]:
        """Fetch affected components for a specific incident"""
        url = self.INCIDENT_DETAIL_URL.format(incident_id=incident_id)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
        
        incident = data.get("incident", {})
        return incident.get("component_impacts", [])

    async def process_incident_async(self, incident: Dict) -> List[Dict]:
        """Process incident and return formatted data for each affected component"""
        component_map = await self.fetch_components_async()
        incident_id = incident.get("id")
        title = incident.get("name")
        created_at = incident.get("created_at")
        
        affected_components = await self.fetch_affected_components_async(incident_id)
        
        results = []
        for impact in affected_components:
            comp_id = impact.get("component_id")
            comp_info = component_map.get(comp_id, {})
            
            results.append({
                "group": comp_info.get("group", "Unknown Group"),
                "component": comp_info.get("component", "Unknown Component"),
                "time_created": created_at,
                "status_message": title
            })
        
        return results if results else [{
            "group": "Unknown",
            "component": "Unknown",
            "time_created": created_at,
            "status_message": title
        }]