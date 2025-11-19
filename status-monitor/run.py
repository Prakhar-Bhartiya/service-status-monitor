#!/usr/bin/env python3
"""
Status Monitor - Main Entry Point
Run this script to start monitoring status pages
"""
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
from adapters.registry import AdapterRegistry
from adapters.openai_adapter import OpenAIAdapter
from adapters.bolna_adapter import BolnaAdapter
from adapters.claude_adapter import ClaudeAdapter
from core.watcher import Watcher
from config.settings import Settings


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
    
    print("Starting the service update monitoring...")
    print(f"Registered adapters: {list(registry.list_adapters())}")
    print(f"Poll interval: {settings.POLL_INTERVAL}s\n")
    
    # Run async monitoring
    asyncio.run(watcher.start_monitoring())


if __name__ == "__main__":
    main()
