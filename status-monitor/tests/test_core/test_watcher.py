import pytest
from src.core.watcher import Watcher
from unittest.mock import patch, AsyncMock

@pytest.fixture
def watcher():
    return Watcher(poll_interval=1)

def test_start_monitoring(watcher):
    with patch.object(watcher, 'fetch_latest_incidents', return_value=[]):
        watcher.start_monitoring()
        assert watcher.is_running is True

def test_stop_monitoring(watcher):
    watcher.start_monitoring()
    watcher.stop_monitoring()
    assert watcher.is_running is False

@patch('src.core.watcher.Watcher.fetch_latest_incidents', return_value=[{'id': '1', 'name': 'Test Incident', 'created_at': '2023-01-01T00:00:00Z'}])
def test_handle_incidents(mock_fetch, watcher):
    watcher.handle_incidents()
    assert len(watcher.incidents) == 1
    assert watcher.incidents[0]['name'] == 'Test Incident'

@patch('src.core.watcher.Watcher.fetch_latest_incidents', new_callable=AsyncMock)
async def test_async_handle_incidents(mock_fetch, watcher):
    mock_fetch.return_value = [{'id': '1', 'name': 'Async Test Incident', 'created_at': '2023-01-01T00:00:00Z'}]
    await watcher.handle_incidents()
    assert len(watcher.incidents) == 1
    assert watcher.incidents[0]['name'] == 'Async Test Incident'