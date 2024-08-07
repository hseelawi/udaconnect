from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Literal, Dict


class Settings(BaseSettings):
    db_username: str
    db_password: str
    db_name: str
    db_host: str
    db_port: str
    kafka_topic: str = "geolocation_topic"
    kafka_bootstrap_servers: str = "localhost:9092"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )

    def get_db_params(self) -> Dict[str, str]:
        return {
            "drivername": "postgresql",
            "username": self.db_username,
            "password": self.db_password,
            "host": self.db_host,
            "port": self.db_port,
            "database": self.db_name,
        }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
