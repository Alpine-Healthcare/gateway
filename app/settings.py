import enum
from pathlib import Path
from tempfile import gettempdir

from pydantic import BaseSettings
from yarl import URL
from dotenv import load_dotenv
import os


load_dotenv()
TEMP_DIR = Path(gettempdir())


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
    # Variables for the database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "sherpa"
    db_pass: str = "sherpa"
    db_base: str = "sherpa"
    db_echo: bool = False

    # OpenAI API key
    open_api_key = os.environ.get("OPENAI_API_KEY")

    # WebAuthn
    rp_id = os.environ.get("RP_ID")
    rp_name = os.environ.get("RP_NAME")
    origin = os.environ.get("ORIGIN")

    #ipfs
    ipfs_url = os.environ.get("IPFS_URL")
    ipfs_ipns_id = os.environ.get("IPFS_IPNS_ID")


    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    class Config:
        env_file = ".env"
        env_prefix = "SHERPA_"
        env_file_encoding = "utf-8"


settings = Settings()
