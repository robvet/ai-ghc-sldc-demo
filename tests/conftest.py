import pytest

from app import storage


@pytest.fixture(autouse=True)
def clear_storage():
    storage.clear()
