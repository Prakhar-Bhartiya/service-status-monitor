import pytest

@pytest.fixture(scope="session")
def sample_fixture():
    return {"key": "value"}