"""
Example: Using the refactored status monitor with multiple providers
"""
import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from adapters.registry import AdapterRegistry
from adapters.openai_adapter import OpenAIAdapter
from adapters.bolna_adapter import BolnaAdapter
from adapters.claude_adapter import ClaudeAdapter
from core.watcher import Watcher


async def demo_single_adapter():
    """Demo: Using a single adapter directly"""
    print("=" * 80)
    print("Demo 1: Direct Adapter Usage")
    print("=" * 80)
    
    # Use Bolna adapter directly
    adapter = BolnaAdapter()
    
    # Fetch latest incidents
    incidents = await adapter.fetch_latest_incidents_async(limit=1)
    
    for incident in incidents:
        print(f"\nRaw incident data:")
        print(f"  ID: {incident['id']}")
        print(f"  Title: {incident['title']}")
        print(f"  Link: {incident['link']}")
        
        # Process incident to get formatted output
        processed = await adapter.process_incident_async(incident)
        
        print(f"\nProcessed incident(s):")
        for proc in processed:
            print(f"  Group: {proc['group']}")
            print(f"  Component: {proc['component']}")
            print(f"  Time: {proc['time_created']}")
            print(f"  Status: {proc['status_message']}")


async def demo_monitoring_with_custom_poll():
    """Demo: Monitor specific providers with custom poll interval"""
    print("\n" + "=" * 80)
    print("Demo 2: Custom Monitoring Setup")
    print("=" * 80)
    
    # Create registry and add only specific providers
    registry = AdapterRegistry()
    registry.register_adapter("bolna", BolnaAdapter)
    registry.register_adapter("claude", ClaudeAdapter)
    
    # Create watcher with custom poll interval
    watcher = Watcher(registry, poll_interval=30)
    
    print("\nMonitoring Bolna and Claude with 30s interval...")
    print("Press Ctrl+C to stop\n")
    
    # This would run indefinitely - we'll just check once for demo
    await watcher.check_incidents()


async def demo_all_providers():
    """Demo: Monitor all providers"""
    print("\n" + "=" * 80)
    print("Demo 3: Monitoring All Providers")
    print("=" * 80)
    
    # Register all available adapters
    registry = AdapterRegistry()
    registry.register_adapter("openai", OpenAIAdapter)
    registry.register_adapter("bolna", BolnaAdapter)
    registry.register_adapter("claude", ClaudeAdapter)
    
    print(f"\nRegistered providers: {list(registry.list_adapters())}")
    
    # Create watcher
    watcher = Watcher(registry, poll_interval=15)
    
    print("\nChecking all providers for incidents...\n")
    await watcher.check_incidents()


async def demo_rss_parsing_strategies():
    """Demo: Show different RSS parsing strategies"""
    print("\n" + "=" * 80)
    print("Demo 4: RSS Parsing Strategies")
    print("=" * 80)
    
    from utils.rss_parser import RSSParser, HTMLIncidentParser
    
    # Strategy 1: Parse RSS feed
    print("\nStrategy 1: Fetching RSS feed...")
    parser = RSSParser()
    incidents = await parser.fetch_rss_feed_async(
        "https://status.bolna.ai/feed.rss", 
        max_items=1
    )
    
    if incidents:
        incident = incidents[0]
        print(f"  Title: {incident['title']}")
        print(f"  Link: {incident['link']}")
        
        # Strategy 2: Extract services from RSS description
        print("\nStrategy 2: Extracting from RSS description...")
        services = parser.extract_services_from_html(incident['description'])
        print(f"  Services from description: {services or 'None found'}")
        
        # Strategy 3: Parse incident page
        print("\nStrategy 3: Parsing incident detail page...")
        html_parser = HTMLIncidentParser()
        services = await html_parser.get_affected_services_async(
            incident['link'], 
            parser_type="bolna"
        )
        print(f"  Services from page: {services}")


async def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("Status Monitor - Usage Examples")
    print("=" * 80)
    
    # Demo 1: Direct adapter usage
    await demo_single_adapter()
    
    # Demo 2: Custom monitoring setup
    await demo_monitoring_with_custom_poll()
    
    # Demo 3: Monitor all providers
    await demo_all_providers()
    
    # Demo 4: RSS parsing strategies
    await demo_rss_parsing_strategies()
    
    print("\n" + "=" * 80)
    print("All demos completed!")
    print("=" * 80)
    print("\nTo start continuous monitoring, run:")
    print("  cd status-monitor && python3 src/main.py")
    print()


if __name__ == "__main__":
    asyncio.run(main())
