import aiohttp
from typing import Any, Dict

class HttpClient:
    @staticmethod
    async def get(url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()

    @staticmethod
    async def post(url: str, json: Dict[str, Any] = None) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json) as response:
                response.raise_for_status()
                return await response.json()