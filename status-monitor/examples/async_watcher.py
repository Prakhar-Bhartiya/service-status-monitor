import asyncio
import sys
import os

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.adapters.registry import AdapterRegistry
from src.adapters.openai_adapter import OpenAIAdapter
from src.core.watcher import Watcher
from src.config.settings import Settings

async def main():
    # Initialize registry and register adapters
    registry = AdapterRegistry()
    registry.register_adapter("openai", OpenAIAdapter)
    
    # Create watcher with registry
    settings = Settings()
    watcher = Watcher(registry, poll_interval=settings.POLL_INTERVAL)
    
    print("Starting async watcher for service updates...")
    print(f"Registered adapters: {list(registry.list_adapters())}")
    print(f"Poll interval: {settings.POLL_INTERVAL}s\n")
    
    await watcher.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())