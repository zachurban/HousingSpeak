"""Tests for the HousingLens client."""

from __future__ import annotations

from src.integrations.housing_lens_client import HousingLensClient


class TestHousingLensClientInit:
    def test_default_base_url(self) -> None:
        client = HousingLensClient(base_url="http://test:8001", api_key="key")
        assert client.base_url == "http://test:8001"
        assert client.api_key == "key"

    def test_strips_trailing_slash(self) -> None:
        client = HousingLensClient(base_url="http://test:8001/", api_key="")
        assert client.base_url == "http://test:8001"
