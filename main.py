import asyncio
import os

from dotenv import load_dotenv

from credentials import Credentials
from scraper import Scraper


async def main():
    # Load environment variables from .env file
    load_dotenv()

    base_api_url = os.getenv("BASE_API_URL")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    # Create a new Scraper instance
    credentials = Credentials(client_id, client_secret)
    scraper = Scraper(base_api_url, credentials)

    # Start the scraping loop
    while True:
        print("Starting scraping run")
        await scraper.run()  # Run the scraper
        print("Scrape finished, sleeping for 60 seconds")
        await asyncio.sleep(60)  # Sleep for 60 seconds before the next run


# Entry point for the script
if __name__ == "__main__":
    asyncio.run(main())
