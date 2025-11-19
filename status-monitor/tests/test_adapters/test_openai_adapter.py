import pytest
from src.adapters.openai_adapter import OpenAIAdapter
from unittest.mock import patch, AsyncMock

@pytest.fixture
def adapter():
    return OpenAIAdapter()

@patch('src.utils.http_client.get')
def test_fetch_latest_incidents(mock_get, adapter):
    mock_get.return_value.json.return_value = {
        "incidents": [
            {
                "id": "incident_1",
                "name": "Service Degradation",
                "created_at": "2025-11-03T14:32:00Z"
            }
        ]
    }
    
    incidents = adapter.fetch_latest_incidents()
    assert len(incidents) == 1
    assert incidents[0]['id'] == "incident_1"
    assert incidents[0]['name'] == "Service Degradation"

@patch('src.utils.http_client.get')
async def test_fetch_affected_components(mock_get, adapter):
    mock_get.return_value.json.return_value = {
        "incident": {
            "component_impacts": [
                {
                    "component_id": "component_1",
                    "status": "degraded_performance"
                }
            ]
        }
    }
    
    impacts = await adapter.fetch_affected_components("incident_1")
    assert len(impacts) == 1
    assert impacts[0]['component_id'] == "component_1"
    assert impacts[0]['status'] == "degraded_performance"