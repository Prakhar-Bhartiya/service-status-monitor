"""
Test script to verify all adapters work correctly
"""
import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from adapters.openai_adapter import OpenAIAdapter
from adapters.bolna_adapter import BolnaAdapter
from adapters.claude_adapter import ClaudeAdapter
from core.formatter import format_incident


async def test_adapter(adapter_class, adapter_name):
    """Test a single adapter"""
    print(f"\n{'='*80}")
    print(f"Testing {adapter_name} Adapter")
    print(f"{'='*80}\n")
    
    try:
        adapter = adapter_class()
        
        # Fetch latest incidents
        print(f"Fetching latest incidents from {adapter_name}...")
        incidents = await adapter.fetch_latest_incidents_async(limit=2)
        
        if not incidents:
            print(f"No incidents found for {adapter_name}")
            return
        
        print(f"Found {len(incidents)} incident(s)\n")
        
        # Process each incident
        for i, incident in enumerate(incidents, 1):
            print(f"--- Incident {i} ---")
            print(f"ID: {incident.get('id', 'N/A')}")
            print(f"Title: {incident.get('title', incident.get('name', 'N/A'))}")
            
            # Process incident to get formatted output
            processed = await adapter.process_incident_async(incident)
            
            if processed:
                print(f"\nFormatted Output:")
                for proc in processed:
                    print(format_incident(proc))
            
            print()
        
        print(f"✓ {adapter_name} adapter working correctly!\n")
        
    except Exception as e:
        print(f"✗ Error testing {adapter_name} adapter: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run tests for all adapters"""
    print("=" * 80)
    print("Status Monitor - Adapter Test Suite")
    print("=" * 80)
    
    # Test OpenAI adapter (JSON-based)
    await test_adapter(OpenAIAdapter, "OpenAI")
    
    # Test Bolna adapter (RSS + HTML)
    await test_adapter(BolnaAdapter, "Bolna")
    
    # Test Claude adapter (RSS + HTML)
    await test_adapter(ClaudeAdapter, "Claude")
    
    print("\n" + "=" * 80)
    print("All adapter tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
