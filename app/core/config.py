from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_HOST: str
    DATABASE_PORT: int = 5432
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"postgresql+psycopg://"
            f"{self.DATABASE_USER}:"
            f"{self.DATABASE_PASSWORD}@"
            f"{self.DATABASE_HOST}:"
            f"{self.DATABASE_PORT}/"
            f"{self.DATABASE_NAME}"
        )


settings = Settings()
