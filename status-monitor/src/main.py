import asyncio
from .adapters.registry import AdapterRegistry
from .adapters.openai_adapter import OpenAIAdapter
from .adapters.bolna_adapter import BolnaAdapter
from .adapters.claude_adapter import ClaudeAdapter
from .core.watcher import Watcher
from .config.settings import Settings

def main():
    # Initialize registry and register adapters
    registry = AdapterRegistry()
    
    # OpenAI uses custom JSON-based API (not RSS)
    registry.register_adapter("openai", OpenAIAdapter)
    
    # Bolna and Claude use RSS feeds with HTML parsing
    registry.register_adapter("bolna", BolnaAdapter)
    registry.register_adapter("claude", ClaudeAdapter)
    
    # Create watcher with registry
    settings = Settings()
    watcher = Watcher(registry, poll_interval=settings.POLL_INTERVAL)
    
    print("=" * 80)
    print("🔍 SERVICE STATUS MONITOR")
    print("=" * 80)
    print(f"Registered providers: {', '.join(list(registry.list_adapters()))}")
    print(f"Poll interval: {settings.POLL_INTERVAL}s")
    print("=" * 80)
    print()
    
    # Run async monitoring
    asyncio.run(watcher.start_monitoring())

if __name__ == "__main__":
    main()