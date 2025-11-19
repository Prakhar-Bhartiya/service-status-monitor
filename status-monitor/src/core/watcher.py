import asyncio
from typing import Set, Dict
from ..adapters.registry import AdapterRegistry
from .formatter import format_incident
from ..utils.logger import setup_logger

class Watcher:
    def __init__(self, registry: AdapterRegistry, poll_interval: int = 15):
        self.poll_interval = poll_interval
        self.registry = registry
        self.last_seen_ids: Dict[str, Set[str]] = {}
        self.logger = setup_logger(__name__)

    async def start_monitoring(self, poll_interval: int = None):
        """Start monitoring all registered adapters"""
        interval = poll_interval or self.poll_interval
        self.logger.info(f"Starting monitoring with {interval}s interval")
        
        # Fetch and display last 3 updates for each provider at startup
        await self.show_initial_status()
        
        print("\n" + "=" * 80)
        print("🔴 NOW MONITORING LIVE - Watching for new updates...")
        print("=" * 80)
        print()
        
        while True:
            try:
                await self.check_incidents()
            except Exception as e:
                self.logger.error(f"Error in monitoring: {e}")
            await asyncio.sleep(interval)

    async def check_incidents(self):
        """Check for new incidents across all adapters"""
        for adapter_name in self.registry.list_adapters():
            try:
                adapter_class = self.registry.get_adapter(adapter_name)
                adapter = adapter_class()
                
                incidents = await self._fetch_incidents_async(adapter)
                
                for incident in incidents:
                    incident_id = incident.get("id")
                    if incident_id not in self.last_seen_ids.get(adapter_name, set()):
                        self.last_seen_ids.setdefault(adapter_name, set()).add(incident_id)
                        
                        # Process and format the incident
                        processed_incidents = await self._process_incident(adapter, incident)
                        if processed_incidents:
                            print(f"🆕 NEW UPDATE FROM {adapter_name.upper()}:")
                            for processed in processed_incidents:
                                print(format_incident(processed))
                            
            except Exception as e:
                self.logger.error(f"Error checking incidents for {adapter_name}: {e}")

    async def _fetch_incidents_async(self, adapter):
        """Fetch incidents from adapter (make it async-compatible)"""
        # If adapter has async method, use it; otherwise wrap sync method
        if hasattr(adapter, 'fetch_latest_incidents_async'):
            return await adapter.fetch_latest_incidents_async()
        else:
            # Run sync method in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, adapter.fetch_latest_incidents)
    
    async def _process_incident(self, adapter, incident):
        """Process incident with adapter-specific logic"""
        if hasattr(adapter, 'process_incident_async'):
            return await adapter.process_incident_async(incident)
        elif hasattr(adapter, 'process_incident'):
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, adapter.process_incident, incident)
        return [incident]
    
    async def show_initial_status(self):
        """Fetch and display last 3 updates for each provider"""
        print("📋 LAST 3 UPDATES FOR EACH PROVIDER:\n")
        
        for adapter_name in self.registry.list_adapters():
            try:
                adapter_class = self.registry.get_adapter(adapter_name)
                adapter = adapter_class()
                
                incidents = await self._fetch_incidents_async(adapter)
                
                # Display provider header
                print(f"┌─── {adapter_name.upper()} " + "─" * (70 - len(adapter_name)))
                
                if not incidents:
                    print("│  No incidents found")
                else:
                    # Process and show last 3 incidents
                    count = 0
                    for incident in incidents[:3]:  # Only first 3
                        incident_id = incident.get("id")
                        # Track these as already seen
                        self.last_seen_ids.setdefault(adapter_name, set()).add(incident_id)
                        
                        # Process the incident
                        processed_incidents = await self._process_incident(adapter, incident)
                        if processed_incidents:
                            for processed in processed_incidents:
                                # Format nicely
                                formatted = format_incident(processed)
                                # Add indentation for better display
                                lines = formatted.strip().split('\n')
                                for line in lines:
                                    print(f"│  {line}")
                                count += 1
                                if count < min(3, len(incidents)):
                                    print("│")
                
                print(f"└{'─' * 76}\n")
                            
            except Exception as e:
                print(f"┌─── {adapter_name.upper()} " + "─" * (70 - len(adapter_name)))
                print(f"│  ⚠️  Error fetching updates: {e}")
                print(f"└{'─' * 76}\n")
                self.logger.error(f"Error fetching initial status for {adapter_name}: {e}")