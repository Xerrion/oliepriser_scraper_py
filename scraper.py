import asyncio
import aiohttp
from datetime import datetime
from bs4 import BeautifulSoup

from credentials import Credentials
from credentials import Token
from provider import Provider


class Scraper:
    def __init__(self, base_url, credentials: Credentials):
        self.providers = []
        self.credentials = credentials
        self.base_url = base_url
        self.run_start = datetime.now()
        self.run_end = None
        self.client = aiohttp.ClientSession()

    async def _post_run(self):
        self.run_end = self.run_end or datetime.now()
        json_body = {
            "start_time": self.run_start.isoformat(),
            "end_time": self.run_end.isoformat(),
        }
        async with self.client.post(
            f"{self.base_url}/scraping_runs", json=json_body
        ) as response:
            await response.text()

    async def _fetch_providers(self):
        async with self.client.get(
            f"{self.base_url}/scraping_runs/providers"
        ) as response:
            if response.status == 200:
                self.providers = await response.json()
            else:
                raise Exception("Failed to fetch providers")

    async def _get_provider(self, id):
        async with self.client.get(f"{self.base_url}/providers/{id}") as response:
            if response.status == 200:
                provider = Provider(**await response.json())
                return provider
            else:
                raise Exception("Failed to fetch providers")

    async def add_price_for_provider(self, provider_id, price):
        url = f"{self.base_url}/providers/{provider_id}/prices"
        json_price = {"price": price}
        async with self.client.post(url, json=json_price) as response:
            if response.status == 201 or response.status == 200:
                return True
            return False


    @staticmethod
    def _sanitize_price_string(price_string):
        sanitized = (
            price_string.replace("kr.", "")
            .replace(",-", "")
            .replace(".", "")
            .replace(",", ".")
            .replace(" ", "")
        )
        try:
            return float(sanitized)
        except ValueError as e:
            raise ValueError(f"Failed to parse price: {e}")

    async def _handle_scraping(self):
        tasks = []
        for provider in self.providers:
            tasks.append(self.scrape_provider(provider))
        await asyncio.gather(*tasks)

    async def scrape_provider(self, provider: dict[str, int]):
        provider: Provider = await self._get_provider(provider["id"])

        async with self.client.get(provider.url) as response:
            body = await response.text()
            document = BeautifulSoup(body, "html.parser")
            element = document.select_one(provider.html_element)
            if element:
                price_string = element.get_text()
                try:
                    price = self._sanitize_price_string(price_string)
                    if price > 0:
                        if await self.add_price_for_provider(provider.id, price):
                            print(f"Price added for provider: {provider.name}")
                        else:
                            print(f"Failed to add price for provider: {provider.name}")
                except Exception as e:
                    print(f"Error processing price for provider {provider.name}: {e}")
            else:
                print(f"No price found for provider {provider.name}")

    async def _set_token(self, json) -> None:
        """
        Set the JWT token from the API response.

        :param json: The JSON response from the API authentication endpoint.
        :return: None
        """
        self.credentials.token = Token(
            access_token=json["access_token"], token_type=json["token_type"]
        )

    async def _get_token(self) -> None:
        """
        Get a JWT token from the API.

        :return: None
        """
        url = f"{self.base_url}/auth/login"
        json_data = {
            "client_id": self.credentials.client_id,
            "client_secret": self.credentials.client_secret,
        }
        async with self.client.post(url, json=json_data) as response:
            if response.status == 200:
                await self._set_token(await response.json())
            else:
                error_message = await response.json()

                raise Exception(
                    f'Failed to get token: Status {response.status}, {error_message["error"]}'
                )

    async def _configure_client(self) -> None:
        """
        Configure the aiohttp client with the necessary headers for authentication.

        :return: None
        """
        self.client = aiohttp.ClientSession(
            headers={
                "Authorization": f"{self.credentials.token.token_type} {self.credentials.token.access_token}"
            }
        )

    async def run(self) -> None:
        """
        Run the scraper, fetching providers, scraping prices, and posting the results to the API.

        :return: None
        """

        self.run_start = datetime.now()
        await self._get_token()
        await self._configure_client()
        await self._fetch_providers()
        await self._handle_scraping()
        self.run_end = datetime.now()
        await self._post_run()
        await self.client.close()
