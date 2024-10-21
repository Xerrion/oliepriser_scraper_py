from dataclasses import dataclass


@dataclass
class Provider:
    """
    Represents an oil provider.

    :param id: The unique identifier of the provider.
    :param name: The name of the provider.
    :param url: The URL of the provider's website.
    :param html_element: The HTML element used to scrape data from the provider's website.
    :param last_accessed: The last time the provider's data was accessed.
    """

    id: int
    name: str
    url: str
    html_element: str
    last_accessed: str
