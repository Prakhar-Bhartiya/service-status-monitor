from datetime import datetime

def format_incident(incident):
    """
    Format incident for display:
    [2025-11-03 14:32:00] Product: OpenAI API - Chat Completions
    Status: Degraded performance due to upstream issue
    """
    time_created = incident.get("time_created")
    if isinstance(time_created, str):
        # Parse ISO format timestamp from API
        try:
            ts = datetime.fromisoformat(time_created.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M:%S")
        except:
            ts = time_created
    elif isinstance(time_created, datetime):
        ts = time_created.strftime("%Y-%m-%d %H:%M:%S")
    else:
        ts = "Unknown Time"

    product = f"{incident.get('group', 'Unknown Group')} - {incident.get('component', 'Unknown Component')}"
    status_msg = incident.get("status_message", "Unknown Status")

    return f"[{ts}] Product: {product}\nStatus: {status_msg}\n"


def format_incident_list(incidents):
    formatted_incidents = [format_incident(incident) for incident in incidents]
    return "\n".join(formatted_incidents)