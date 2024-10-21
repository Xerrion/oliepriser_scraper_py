import os
import aiohttp
import pytest
from dotenv import load_dotenv


@pytest.mark.asyncio
async def test_hello_world():
    load_dotenv()

    base_url = os.getenv("BASE_API_URL")
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url) as response:
            assert response.status == 200
            text = await response.text()
            assert text == "Hello, world!"
