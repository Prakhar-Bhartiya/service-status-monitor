from abc import ABC, abstractmethod
from typing import List, Dict

class BaseAdapter(ABC):
    """Base adapter interface for status page providers"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name"""
        pass
    
    @abstractmethod
    async def fetch_latest_incidents_async(self, limit: int = 3) -> List[Dict]:
        """Fetch latest incidents from the provider"""
        pass
    
    @abstractmethod
    async def process_incident_async(self, incident: Dict) -> List[Dict]:
        """Process and format incident data"""
        pass