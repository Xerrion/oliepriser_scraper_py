from dataclasses import dataclass


@dataclass
class Token:
    """
    Represents a JWT token.

    :param access_token: The access token string.
    :param token_type: The token type string, default is "Bearer".
    """

    access_token: str
    token_type: str = "Bearer"


@dataclass
class Credentials:
    """
    Represents the credentials used for authentication.

    :param client_id: The client ID for authentication.
    :param client_secret: The client secret for authentication.
    :param token: The token used for authentication, default is None.
    """

    client_id: str
    client_secret: str
    token: Token | None = None
