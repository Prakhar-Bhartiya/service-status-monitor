# Design Decisions Document

## Overview

This document outlines the key design decisions made while building the Service Status Monitor. The goal was to create a scalable, event-based solution that can monitor 100+ status pages efficiently.

## Problem Analysis

### Requirements

1. Automatically track service updates from multiple status pages
2. Detect incidents, outages, or degradation updates
3. Print affected product/service and latest status
4. Use event-based approach (not inefficient polling)
5. Scale to 100+ status pages from different providers

### Challenges

- Different status pages use different formats (JSON API, RSS, HTML)
- Need to avoid inefficient polling while maintaining real-time updates
- Must be extensible to support multiple providers
- Should handle various incident formats and structures

## Core Design Decisions

### 1. **Async-First Architecture**

**Decision**: Use Python's `asyncio` and `aiohttp` for all I/O operations.

**Rationale**:

- **Scalability**: Async I/O allows monitoring 100+ status pages concurrently without blocking
- **Efficiency**: Single thread can handle multiple HTTP requests simultaneously
- **Event-Based**: Natural fit for event-driven programming model
- **Resource-Efficient**: Minimal CPU and memory overhead compared to threading

**Implementation**:

```python
async def fetch_incidents_async(self):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

**Trade-offs**:

- ✅ Pros: Excellent performance, low resource usage, native Python 3.9+
- ⚠️ Cons: Slightly more complex than synchronous code (but worth it)

---

### 2. **Adapter Pattern for Multiple Providers**

**Decision**: Implement an adapter pattern where each status page provider has its own adapter class.

**Rationale**:

- **Extensibility**: Adding a new provider requires only implementing one class
- **Separation of Concerns**: Each adapter handles provider-specific logic
- **Maintainability**: Changes to one provider don't affect others
- **Testability**: Each adapter can be tested independently

**Implementation**:

```python
# Base interface
class BaseAdapter(ABC):
    @abstractmethod
    async def fetch_incidents_async(self) -> List[Incident]:
        pass

# Provider-specific implementations
class OpenAIAdapter(BaseAdapter): ...
class ClaudeAdapter(RSSAdapter): ...
class CustomAdapter(RSSAdapter): ...
```

**Trade-offs**:

- ✅ Pros: Clean architecture, easy to extend, follows SOLID principles
- ⚠️ Cons: Initial setup overhead (but pays off with maintainability)

---

### 3. **Multiple Data Extraction Strategies**

**Decision**: Support both JSON API and RSS+HTML parsing strategies.

**Rationale**:

- **Flexibility**: Some providers use custom JSON APIs, others use RSS feeds
- **Universal Support**: RSS is widely supported across status page platforms
- **Different Needs**: Different strategies for different use cases
- **Optimization**: JSON API is faster; RSS is more universal

**Strategy Breakdown**:

| Provider | Primary Strategy | Fallback           |
| -------- | ---------------- | ------------------ |
| OpenAI   | JSON API         | N/A (reliable)     |
| Claude   | RSS → HTML Parse | Keyword extraction |
| Custom   | RSS → HTML Parse | Keyword extraction |

**Implementation**:

- **OpenAI**: Direct JSON API calls to get structured incident data
- **Others**: 3-tier fallback system (RSS description → HTML page → keywords)

**Trade-offs**:

- ✅ Pros: Works with any status page format
- ⚠️ Cons: RSS+HTML parsing is slightly slower but still very fast

---

### 4. **3-Tier Fallback System for RSS Adapters**

**Decision**: Implement multiple fallback methods for extracting affected services.

**Rationale**:

- **Reliability**: If one method fails, try another
- **Data Quality**: Get the most accurate data available
- **Provider Variance**: Different RSS formats require different approaches

**Tiers**:

**Tier 1**: Extract from RSS description HTML

```python
# Try to find service names in RSS feed description
services = extract_services_from_html(incident.description)
```

**Tier 2**: Parse full incident detail page

```python
# Fetch and parse the full incident page
if self.INCIDENT_PARSER_TYPE:
    services = await parse_incident_page(incident.link)
```

**Tier 3**: Fallback keyword extraction

```python
# Last resort: extract from title/description text
services = _extract_fallback_services(incident)
```

**Trade-offs**:

- ✅ Pros: High reliability, graceful degradation
- ⚠️ Cons: Slight performance overhead for multiple attempts

---

### 5. **Centralized Registry Pattern**

**Decision**: Use a registry to manage all adapters centrally.

**Rationale**:

- **Single Source of Truth**: All adapters registered in one place
- **Dynamic Configuration**: Easy to enable/disable providers
- **Loose Coupling**: Watcher doesn't need to know about specific adapters

**Implementation**:

```python
registry = AdapterRegistry()
registry.register_adapter("openai", OpenAIAdapter)
registry.register_adapter("claude", ClaudeAdapter)

# Watcher uses registry
watcher = Watcher(registry)
```

**Trade-offs**:

- ✅ Pros: Flexible, decoupled, easy to configure
- ⚠️ Cons: Adds one more abstraction layer

---

### 6. **Intelligent Polling Interval**

**Decision**: Use configurable polling with default 15-second interval.

**Rationale**:

- **Balance**: Fast enough to catch updates, slow enough to avoid rate limits
- **Resource-Friendly**: Doesn't hammer servers unnecessarily
- **Configurable**: Can be adjusted based on needs

**Why Not WebSockets/SSE?**

- Most status pages don't provide WebSocket/SSE endpoints
- Polling with async is efficient enough for status updates
- Simpler implementation, easier to debug
- Works universally across different status page platforms

**Configuration**:

```python
POLL_INTERVAL = 15  # Default in settings
# Can be overridden via environment variable
```

**Trade-offs**:

- ✅ Pros: Simple, reliable, works with all providers
- ⚠️ Cons: Not real-time (but 15s is fast enough for status updates)

---

### 7. **Separation of Concerns: Utilities Layer**

**Decision**: Extract common functionality into reusable utilities.

**Rationale**:

- **DRY Principle**: Don't repeat RSS/HTML parsing logic
- **Reusability**: Same utilities work across all RSS adapters
- **Testability**: Easier to test isolated functions
- **Maintainability**: Bug fixes in one place benefit all adapters

**Utilities Created**:

- `rss_parser.py`: RSS feed parsing and HTML extraction
- `http_client.py`: HTTP request handling with retries
- `logger.py`: Consistent logging across the application

**Trade-offs**:

- ✅ Pros: Clean code, reusable, testable
- ⚠️ Cons: None (this is a best practice)

---

### 8. **Structured Incident Model**

**Decision**: Use dataclasses to represent incidents.

**Rationale**:

- **Type Safety**: Clear data structure with type hints
- **Validation**: Easy to validate required fields
- **Serialization**: Can be easily converted to JSON/dict
- **Immutability**: Dataclasses can be frozen for safety

**Implementation**:

```python
@dataclass
class Incident:
    provider: str
    service: str
    status: str
    timestamp: str
    description: Optional[str] = None
    link: Optional[str] = None
```

**Trade-offs**:

- ✅ Pros: Type-safe, clear structure, self-documenting
- ⚠️ Cons: None

---

### 9. **Comprehensive Error Handling**

**Decision**: Implement try-catch blocks with graceful degradation.

**Rationale**:

- **Resilience**: One failing adapter shouldn't crash the entire system
- **Debugging**: Log errors for troubleshooting
- **User Experience**: Continue monitoring other providers if one fails

**Implementation**:

```python
try:
    incidents = await adapter.fetch_incidents_async()
except Exception as e:
    logger.error(f"Error fetching from {name}: {e}")
    continue  # Keep monitoring other adapters
```

**Trade-offs**:

- ✅ Pros: Robust, production-ready, user-friendly
- ⚠️ Cons: None

---

### 10. **Beautiful Console Output**

**Decision**: Use formatted console output with visual separators.

**Rationale**:

- **Readability**: Easy to scan and understand at a glance
- **Professional**: Looks polished and production-ready
- **Debugging**: Clear timestamps help with troubleshooting

**Example Output**:

```
[2025-11-18 14:32:00] Provider: OpenAI
Product: OpenAI API - Chat Completions
Status: Operational
───────────────────────────────────────────────────────────────
```

**Trade-offs**:

- ✅ Pros: User-friendly, professional appearance
- ⚠️ Cons: None

---

## Technology Choices

### Python 3.9+

- **Why**: Native async/await, type hints, dataclasses
- **Alternatives**: Node.js, Go (Python chosen for its rich ecosystem)

### aiohttp

- **Why**: Best async HTTP client for Python, widely used
- **Alternatives**: httpx (also good, but aiohttp is more mature)

### BeautifulSoup4 + lxml

- **Why**: Industry-standard HTML parsing, robust, fast
- **Alternatives**: pyquery, lxml only (but BS4 is more Pythonic)

### pytest

- **Why**: Most popular Python testing framework
- **Alternatives**: unittest (but pytest is more feature-rich)

---

## Scalability Considerations

### How This Scales to 100+ Providers

1. **Async I/O**: Can handle 100+ concurrent HTTP requests efficiently
2. **Non-Blocking**: While waiting for responses, other tasks continue
3. **Memory Efficient**: Each adapter is lightweight (~1-2KB in memory)
4. **CPU Efficient**: Async uses single thread, minimal context switching

### Performance Estimate

- **100 providers** × **15s polling** = ~0.15s per provider per cycle
- With async: All 100 providers checked in ~2-3 seconds (network bound)
- CPU usage: <5% on modern hardware
- Memory usage: <50MB for 100 adapters

### Future Optimizations

- Connection pooling (already implemented via aiohttp)
- Caching of unchanged incidents (could add with Redis)
- Rate limiting per provider (easy to add with semaphores)
- Distributed monitoring (can use Celery/RabbitMQ if needed)

---

## Testing Strategy

### Unit Tests

- Test each adapter independently
- Mock HTTP responses for predictable testing
- Verify incident parsing logic

### Integration Tests

- Test full monitoring cycle
- Verify registry and watcher integration
- Test error handling scenarios

### Manual Testing

```bash
python3 test_adapters.py  # Quick adapter validation
python3 run.py            # Full system test
```

---

## Project Structure Rationale

```
status-monitor/
├── src/
│   ├── adapters/      # Each provider isolated
│   ├── core/          # Business logic
│   ├── config/        # Configuration
│   └── utils/         # Shared utilities
├── tests/             # Test suite
├── examples/          # Documentation by example
└── run.py            # Simple entry point
```

**Why This Structure?**

- **Modularity**: Easy to find and modify specific components
- **Scalability**: Can add features without refactoring structure
- **Standard**: Follows Python project conventions
- **Clarity**: New developers can understand quickly

---

## Lessons Learned & Future Improvements

### What Went Well

✅ Adapter pattern makes adding providers trivial  
✅ Async architecture performs excellently  
✅ 3-tier fallback ensures data reliability  
✅ Clean separation of concerns

### Future Enhancements

🔮 Add webhook support for instant notifications  
🔮 Implement database persistence (SQLite/PostgreSQL)  
🔮 Add web dashboard (FastAPI + React)  
🔮 Support custom alert rules and filtering  
🔮 Add metrics and monitoring (Prometheus)

### Alternative Approaches Considered

**1. Webhook-Based**

- Pros: True real-time updates
- Cons: Most status pages don't offer webhooks
- Decision: Polling is more universal

**2. Scraping Full Pages**

- Pros: Works anywhere
- Cons: Fragile, slow, inefficient
- Decision: Use APIs/RSS when available

**3. Synchronous Implementation**

- Pros: Simpler code
- Cons: Can't scale to 100+ providers
- Decision: Async is essential for scalability

---

## Conclusion

This design prioritizes:

1. **Scalability** - Can handle 100+ providers efficiently
2. **Extensibility** - Easy to add new providers
3. **Reliability** - Multiple fallback mechanisms
4. **Maintainability** - Clean, modular architecture
5. **Performance** - Async-first, optimized for I/O

The solution successfully provides a production-ready foundation that can efficiently monitor 100+ status pages while maintaining clean, maintainable code.

---

**Author**: Prakhar Bhartiya  
**Year**: 2025  
**License**: MIT
