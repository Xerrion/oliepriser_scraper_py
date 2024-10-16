from dataclasses import dataclass


@dataclass
class Provider:
    """
    Represents an oil provider.
    """
    id: int
    name: str
    url: str
    html_element: str
    last_accessed: str
