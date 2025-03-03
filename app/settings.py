import enum
import os

from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv()


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = "0.0.0.0"
    port: int = 8000
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    # Current environment
    environment: str = os.environ.get("ENVIRONMENT", "development")

    log_level: LogLevel = LogLevel.INFO

    # WebAuthn (Passkeys)
    rp_id: str = os.environ.get("RP_ID")
    rp_name: str = os.environ.get("RP_NAME")
    origin: str = os.environ.get("ORIGIN")

    #ipfs
    ipfs_url: str = os.environ.get("IPFS_URL")
    ipfs_ipns_id: str = os.environ.get("IPFS_IPNS_ID")

    #wallet
    marigold_public_key: str = os.environ.get("MARIGOLD_PUBLIC_KEY")
    marigold_private_key: str = os.environ.get("MARIGOLD_PRIVATE_KEY")

    infura_url: str = os.environ.get("INFURA_URL")

    class Config:
        env_file = ".env"
        env_prefix = "GATEWAY_"
        env_file_encoding = "utf-8"


settings = Settings()
