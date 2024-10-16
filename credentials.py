from dataclasses import dataclass


@dataclass
class Token:
    """
    Represents an JWT token.
    """

    access_token: str
    token_type: str


@dataclass
class Credentials:
    """
    Represents the credentials used for authentication.
    """

    client_id: str
    client_secret: str
    token: Token | None = None
