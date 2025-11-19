#!/usr/bin/env python3
"""
Quick test script to verify the status monitor is working
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.adapters.registry import AdapterRegistry
from src.adapters.openai_adapter import OpenAIAdapter
from src.core.watcher import Watcher
from src.config.settings import Settings

async def test_adapter():
    """Test the OpenAI adapter directly"""
    print("=== Testing OpenAI Adapter ===\n")
    
    adapter = OpenAIAdapter()
    
    print(f"Adapter name: {adapter.name}")
    print("Fetching components...")
    components = await adapter.fetch_components_async()
    print(f"Found {len(components)} components")
    
    print("\nFetching latest incidents...")
    incidents = await adapter.fetch_latest_incidents_async(limit=2)
    print(f"Found {len(incidents)} incidents")
    
    if incidents:
        incident = incidents[0]
        print(f"\nProcessing first incident: {incident.get('name')}")
        processed = await adapter.process_incident_async(incident)
        print(f"Processed into {len(processed)} component impacts")
        for p in processed[:2]:  # Show first 2
            print(f"  - {p.get('group')} - {p.get('component')}")
    
    print("\n=== Adapter test complete ===\n")

async def test_watcher_once():
    """Test the watcher for one cycle"""
    print("=== Testing Watcher (one cycle) ===\n")
    
    registry = AdapterRegistry()
    registry.register_adapter("openai", OpenAIAdapter)
    
    settings = Settings()
    watcher = Watcher(registry, poll_interval=settings.POLL_INTERVAL)
    
    print(f"Registered adapters: {list(registry.list_adapters())}")
    print("\nChecking for incidents...\n")
    
    await watcher.check_incidents()
    
    print("\n=== Watcher test complete ===")

async def main():
    print("Status Monitor Test Suite\n")
    print("=" * 50)
    
    try:
        await test_adapter()
        print("\n" + "=" * 50 + "\n")
        await test_watcher_once()
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n" + "=" * 50)
    print("✅ All tests passed!")
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
