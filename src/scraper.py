import asyncio
import aiohttp
from datetime import datetime
from bs4 import BeautifulSoup

from credentials import Credentials
from credentials import Token
from provider import Provider


class Scraper:
    """
    A class to represent a web scraper.
    """

    def __init__(self, base_url, credentials: Credentials):
        """
        Initialize the Scraper with a base URL and credentials.

        :param base_url: The base URL for the API.
        :param credentials: The credentials for authentication.
        """
        self.base_url = base_url
        self.credentials = credentials
        self.providers = []
        self.run_start = datetime.now()
        self.run_end = None

    async def _post_run(self, session: aiohttp.ClientSession) -> None:
        """
        Post the scraping run to the API.

        :param session: The aiohttp session
        :return: None
        """
        self.run_end = datetime.now()
        json_body = {
            "start_time": self.run_start.isoformat(),
            "end_time": self.run_end.isoformat(),
        }
        async with session.post(
            f"{self.base_url}/scraping_runs", json=json_body
        ) as response:
            await response.text()

    async def _fetch_providers(self, session: aiohttp.ClientSession) -> None:
        """
        Fetch all providers from the API.

        :param session: The aiohttp session
        :return: None
        """
        async with session.get(f"{self.base_url}/scraping_runs/providers") as response:
            if response.status == 200:
                self.providers = await response.json()
            else:
                raise Exception(f"Failed to fetch providers: {response.status}")

    async def _get_provider(self, session: aiohttp.ClientSession, id: int) -> Provider:
        """
        Fetch a provider by id.

        :param session: The aiohttp session
        :param id: The provider id to fetch
        :return: A Provider object with the provider data
        """
        async with session.get(f"{self.base_url}/providers/{id}") as response:
            if response.status == 200:
                return Provider(**await response.json())
            else:
                raise Exception(f"Failed to fetch provider {id}: {response.status}")

    async def _add_price_for_provider(
        self, session: aiohttp.ClientSession, provider_id: int, price: float
    ) -> bool:
        """
        Add a price for a provider.

        :param session: The aiohttp session
        :param provider_id: The provider id to add the price for
        :param price: The price to add for the provider
        :return: True if the price was added successfully, False otherwise
        """
        url = f"{self.base_url}/providers/{provider_id}/prices"
        json_price = {"price": price}
        async with session.post(url, json=json_price) as response:
            return response.status in {200, 201}

    @staticmethod
    def _sanitize_price_string(price_string: str) -> float:
        """
        Sanitize the price string. Remove all non-numeric characters and convert to float.

        :param price_string: String representation of the price.
        :return: The price as a float without any non-numeric characters and currency symbols
        """
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

    async def _handle_scraping(self, session: aiohttp.ClientSession) -> None:
        """
        Scrape all providers. This is the main scraping loop.

        :param session: The aiohttp session
        :return: None
        """

        tasks = [
            self._scrape_provider(session, provider) for provider in self.providers
        ]
        await asyncio.gather(*tasks)

    async def _scrape_provider(
        self, session: aiohttp.ClientSession, provider: dict
    ) -> None:
        """
        Scrape a single provider.

        :param session: The aiohttp session
        :param provider: The provider to scrape
        :return: None
        """

        provider_obj = await self._get_provider(session, provider["id"])

        # Scrape the provider's website
        async with session.get(provider_obj.url) as response:
            if response.status != 200:
                print(
                    f"Failed to scrape provider {provider_obj.name}, status: {response.status}"
                )
                return

            # Parse the HTML response
            body = await response.text()
            document = BeautifulSoup(body, "html.parser")
            element = document.select_one(provider_obj.html_element)

            # Extract the price from the HTML element and add it to the API
            if element:
                price_string = element.get_text()
                try:
                    price = self._sanitize_price_string(price_string)
                    if price > 0 and await self._add_price_for_provider(
                        session, provider_obj.id, price
                    ):
                        # Update the last accessed time for the provider
                        await session.put(
                            f"{self.base_url}/providers/{provider_obj.id}/last_accessed"
                        )
                        print(f"Price added for provider: {provider_obj.name}")
                    else:
                        print(f"Failed to add price for provider: {provider_obj.name}")
                except Exception as e:
                    print(
                        f"Error processing price for provider {provider_obj.name}: {e}"
                    )
            else:
                print(f"No price found for provider {provider_obj.name}")

    async def _set_token(self, json: dict[str, str]) -> None:
        """
        Set the token from the JSON response.

        :param json: The JSON response from the API
        :return: None
        """
        # Set the token from the JSON response
        self.credentials.token = Token(
            access_token=json["access_token"], token_type=json["token_type"]
        )

    async def _get_token(self, session: aiohttp.ClientSession) -> None:
        """
        Get the token from the API. This is used to authenticate the scraper.

        :param session: The aiohttp session
        :return: None
        """
        url = f"{self.base_url}/auth/login"
        json_data = {
            "client_id": self.credentials.client_id,
            "client_secret": self.credentials.client_secret,
        }

        # Make a POST request to the API to get the token
        async with session.post(url, json=json_data) as response:
            if response.status == 200:
                await self._set_token(await response.json())
            else:
                raise Exception(
                    f"Failed to get token: {response.status}, {await response.json()}"
                )

    async def _configure_client(self):
        """
        Configure the aiohttp client with the token.

        :return: aiohttp.ClientSession
        """
        return aiohttp.ClientSession(
            headers={
                "Authorization": f"{self.credentials.token.token_type} {self.credentials.token.access_token}"
            }
        )

    async def run(self):
        """
        Run the scraper.

        :return: None
        """
        # Set the start time of the run
        self.run_start = datetime.now()

        # Create a new aiohttp session
        async with aiohttp.ClientSession() as session:
            # Get the token
            await self._get_token(session)

            # Create a new session with the token
            auth_session = await self._configure_client()
            async with auth_session:
                await self._fetch_providers(auth_session)
                await self._handle_scraping(auth_session)
                await self._post_run(auth_session)
