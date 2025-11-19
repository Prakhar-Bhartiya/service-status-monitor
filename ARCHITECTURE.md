# Status Monitor - Architecture Documentation

## Overview

The status monitor system has been designed to support multiple status page providers with different data formats:

1. **OpenAI** - Uses proprietary JSON API
2. **Claude** - Uses RSS feed + HTML parsing (Statuspage.io)
3. **Custom Providers** - Extensible RSS adapter for any RSS-based status page

## Architecture

### Core Design Principles

1. **Adapter Pattern**: Each status page provider has its own adapter implementing the `BaseAdapter` interface
2. **Strategy Pattern**: Different parsing strategies for different providers:
   - JSON-based for OpenAI
   - RSS + HTML parsing for others
3. **DRY Principle**: Shared utilities for RSS parsing and HTML extraction
4. **Extensibility**: Easy to add new providers by extending `RSSAdapter`

### Component Structure

```
status-monitor/
├── src/
│   ├── adapters/
│   │   ├── base.py              # Base adapter interface
│   │   ├── openai_adapter.py    # OpenAI (JSON-based) ✓
│   │   ├── rss_adapter.py       # Generic RSS adapter base ✓
│   │   ├── claude_adapter.py    # Claude-specific adapter ✓
│   │   └── registry.py          # Adapter registration
│   ├── core/
│   │   ├── watcher.py           # Monitors all adapters
│   │   ├── formatter.py         # Output formatting
│   │   └── incident.py          # Incident data class
│   ├── utils/
│   │   ├── rss_parser.py        # RSS & HTML parsing utilities ✓ NEW
│   │   ├── http_client.py       # HTTP utilities
│   │   └── logger.py            # Logging setup
│   └── main.py                  # Entry point
└── test_adapters.py             # Test suite ✓ NEW
```

## Implementation Details

### 1. RSS Parsing Utilities (`utils/rss_parser.py`)

**RSSParser Class**:

- `fetch_rss_feed_async()`: Fetches and parses RSS feeds
- `extract_services_from_html()`: Extracts services from RSS description HTML
- `clean_html()`: Removes HTML tags and cleans text

**HTMLIncidentParser Class**:

- `fetch_incident_page_async()`: Fetches incident detail pages
- `parse_claude_incident()`: Parses Statuspage.io incident pages
- `parse_custom_incident()`: Extensible for custom parsers
- `get_affected_services_async()`: Generic service extraction

### 2. Generic RSS Adapter (`adapters/rss_adapter.py`)

Base class for all RSS-based status pages with a **3-tier fallback strategy**:

```python
class RSSAdapter(BaseAdapter):
    RSS_FEED_URL: str           # Subclass defines
    INCIDENT_PARSER_TYPE: str   # "claude", custom type, or None

    async def process_incident_async(incident):
        # Tier 1: Extract from RSS description HTML (OpenAI-style)
        services = extract_services_from_html(description)
        if services:
            return format_incidents(services)

        # Tier 2: Parse incident detail page (provider-specific)
        if INCIDENT_PARSER_TYPE:
            services = parse_incident_page(link)
            if services:
                return format_incidents(services)

        # Tier 3: Fallback to provider-specific extraction
        services = _extract_fallback_services(incident)
        return format_incidents(services)
```

### 3. Provider-Specific Adapters

#### OpenAI Adapter (Original - Unchanged)

- **Data Source**: JSON API (`https://status.openai.com/api/v2/`)
- **Strategy**:
  1. Fetch components mapping
  2. Fetch incidents
  3. Fetch affected components for each incident
  4. Map component IDs to names
- **No RSS parsing needed**

#### Claude Adapter

```python
class ClaudeAdapter(RSSAdapter):
    RSS_FEED_URL = "https://status.claude.com/history.rss"
    INCIDENT_PARSER_TYPE = "claude"  # Uses Statuspage.io format

    # Fallback: Check for keywords in title
    async def _extract_fallback_services(incident):
        if 'api' in title:
            return ['Claude API']
        # ... other services
```

#### Custom RSS Adapter Example

```python
class CustomAdapter(RSSAdapter):
    RSS_FEED_URL = "https://status.example.com/feed.rss"
    INCIDENT_PARSER_TYPE = None  # Generic parsing

    # Fallback: Check for keywords in title
    async def _extract_fallback_services(incident):
        if 'database' in title:
            return ['Database']
        # ... other services
```

## Data Flow

### RSS-Based Providers (Claude, Custom)

```
1. Watcher calls adapter.fetch_latest_incidents_async()
   ↓
2. RSSParser.fetch_rss_feed_async(RSS_FEED_URL)
   ↓
3. Returns: [{id, title, link, pub_date, description}, ...]
   ↓
4. For each incident, call adapter.process_incident_async()
   ↓
5. Three-tier service extraction:
   a) Try RSS description HTML (OpenAI format)
   b) Try incident page HTML (provider-specific)
   c) Fallback to keyword matching
   ↓
6. Format incidents with group/component/time/status
   ↓
7. Display formatted output
```

### JSON-Based Provider (OpenAI)

```
1. Watcher calls adapter.fetch_latest_incidents_async()
   ↓
2. Fetch from JSON API
   ↓
3. For each incident, call adapter.process_incident_async()
   ↓
4. Fetch component impacts via separate API call
   ↓
5. Map component IDs to names using cached component map
   ↓
6. Format incidents
   ↓
7. Display formatted output
```

## Key Optimizations

### 1. **Code Reusability**

- Shared RSS parsing logic in `utils/rss_parser.py`
- Generic `RSSAdapter` base class eliminates duplication
- BeautifulSoup parsing utilities for multiple HTML formats

### 2. **Extensibility**

Adding a new RSS-based provider requires only:

```python
class NewProviderAdapter(RSSAdapter):
    RSS_FEED_URL = "https://status.provider.com/feed.rss"
    INCIDENT_PARSER_TYPE = "custom"  # or None for generic

    # Optional: custom fallback
    async def _extract_fallback_services(self, incident):
        # Custom keyword logic
        return ["Service Name"]
```

### 3. **Async Performance**

- All HTTP requests are async (aiohttp)
- Parallel incident processing
- Non-blocking monitoring loop

### 4. **Graceful Degradation**

- 3-tier fallback strategy ensures we always get some data
- Error handling at each level
- Continues monitoring other providers if one fails

### 5. **Separation of Concerns**

- **Adapters**: Provider-specific logic
- **Parsers**: Generic parsing utilities
- **Watcher**: Orchestration and monitoring
- **Formatter**: Output presentation

## Why This Approach?

### OpenAI - JSON API (Original)

- **Reason**: OpenAI provides a well-structured JSON API
- **Advantage**: Direct access to component mappings and detailed incident data
- **Performance**: Fewer HTTP requests, structured data
- **Kept Original**: No need to change what works perfectly

### Others - RSS + HTML (New)

- **Reason**: Most status pages provide RSS feeds (universal standard)
- **Advantage**: Single approach works for many providers
- **BeautifulSoup**: Handles different HTML structures gracefully
- **Fallback Strategy**: Ensures we always extract useful information

### Why Not RSS for OpenAI?

- RSS feed lacks component/service details (only in description HTML)
- JSON API provides better data structure
- Direct component mapping is more reliable

## Testing

Run the test suite:

```bash
cd status-monitor
python3 test_adapters.py
```

Output shows:

- Incidents fetched from each provider
- Services extracted correctly
- Formatted output matches expected format

## Adding New Providers

### For RSS-based providers:

1. **Create new adapter file** (`src/adapters/provider_adapter.py`):

```python
from .rss_adapter import RSSAdapter

class ProviderAdapter(RSSAdapter):
    RSS_FEED_URL = "https://status.provider.com/feed.rss"
    INCIDENT_PARSER_TYPE = None  # or "custom"

    def __init__(self):
        super().__init__()
        self._name = "Provider"
```

2. **If custom HTML parsing needed**, add to `utils/rss_parser.py`:

```python
@staticmethod
def parse_provider_incident(html: str) -> List[str]:
    soup = BeautifulSoup(html, 'html.parser')
    # Custom parsing logic
    return services
```

3. **Register adapter** in `main.py`:

```python
from src.adapters.provider_adapter import ProviderAdapter
registry.register_adapter("provider", ProviderAdapter)
```

### For custom API providers:

Follow the OpenAI adapter pattern - create a new adapter implementing `BaseAdapter` directly.
