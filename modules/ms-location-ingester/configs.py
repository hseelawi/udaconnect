from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Literal


class Settings(BaseSettings):
    num_location_entries: int = 50
    kafka_topic: str = "geolocation_topic"
    kafka_bootstrap_servers: str = "localhost:9092"
    grpc_server_port: int = 50051
    grpc_client_target: str = "localhost"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def grpc_server_address(self) -> str:
        return f"{self.grpc_client_target}:{self.grpc_server_port}"


settings = Settings()
