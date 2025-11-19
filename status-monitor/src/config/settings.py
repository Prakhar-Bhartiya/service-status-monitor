import os

class Settings:
    """Configuration settings for the status monitor application."""
    
    # API endpoints
    COMPONENTS_URL = os.getenv("COMPONENTS_URL", "https://status.openai.com/proxy/status.openai.com")
    INCIDENTS_URL = os.getenv("INCIDENTS_URL", "https://status.openai.com/api/v2/incidents.json")
    
    # Polling interval in seconds
    POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 15))
    
    # Log level
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")