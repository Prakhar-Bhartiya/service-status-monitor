"""
Sync watcher example
Main architecture uses async patterns for better scalability.
Please use async_watcher.py for production use.

For educational purposes, this shows how you could adapt
the async adapter to work in a sync context using asyncio.run()
"""
import time
import asyncio
import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.adapters.registry import AdapterRegistry
from src.adapters.openai_adapter import OpenAIAdapter
from src.core.formatter import format_incident

def run_sync_watcher(poll_interval=15):
    """
    Synchronous wrapper around async functionality.
    Not recommended for production - use async_watcher.py instead.
    """
    registry = AdapterRegistry()
    registry.register_adapter("openai", OpenAIAdapter)
    
    last_seen_ids = {}

    print("Starting sync watcher (using async adapters in sync wrapper)")
    print("Note: This is not optimal. Use async_watcher.py for production.\n")

    while True:
        try:
            # Run async check in sync context (not ideal but works for simple cases)
            for adapter_name in registry.list_adapters():
                adapter_class = registry.get_adapter(adapter_name)
                adapter = adapter_class()
                
                # Fetch incidents
                incidents = asyncio.run(adapter.fetch_latest_incidents_async())
                
                for incident in incidents:
                    incident_id = incident.get("id")
                    if incident_id not in last_seen_ids.get(adapter_name, set()):
                        last_seen_ids.setdefault(adapter_name, set()).add(incident_id)
                        
                        # Process incident
                        processed_incidents = asyncio.run(adapter.process_incident_async(incident))
                        for processed in processed_incidents:
                            print(format_incident(processed))
                            
        except Exception as e:
            print(f"Watcher error: {e}")

        time.sleep(poll_interval)

if __name__ == "__main__":
    run_sync_watcher()