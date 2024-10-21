import asyncio
import os

from dotenv import load_dotenv

from credentials import Credentials
from scraper import Scraper


async def main():
    """
    Main entry point for the scraping script.

    This function loads environment variables, creates a Scraper instance,
    and starts a loop that runs the scraper every hour.
    """
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
        print("Scrape finished, sleeping for 1 hour")
        await asyncio.sleep(3600)  # Sleep for 1 hour before the next run


# Entry point for the script
if __name__ == "__main__":
    asyncio.run(main())
