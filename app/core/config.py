from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    DATABASE_HOST: str
    DATABASE_PORT: int = 5432
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    TENANCY_TENANT_HEADER_NAME: str = "X-Tenant-ID"

    JWT_SECRET: str
    JWT_EXPIRES_IN: int

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    def build_database_uri(self, database_name: str) -> str:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.DATABASE_USER,
            password=self.DATABASE_PASSWORD,
            host=self.DATABASE_HOST,
            port=self.DATABASE_PORT,
            database=database_name,
        ).render_as_string(hide_password=False)

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.build_database_uri(self.DATABASE_NAME)

    @property
    def SQLALCHEMY_TENANT_DATABASE_URL_TEMPLATE(self) -> str:
        return self.build_database_uri("{database_name}")


settings = Settings()
