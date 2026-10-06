from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import app.data.models.tenants as tenant_models
from app.data.models.tenants.base import tenant_registry

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = tenant_registry.metadata
_ = tenant_models


def get_url() -> str:
    x_arguments = context.get_x_argument(as_dictionary=True)
    configured_attributes = config.attributes
    target_url = configured_attributes.get("url") or x_arguments.get("url")

    if target_url:
        return str(target_url)

    configured_url = config.get_main_option("sqlalchemy.url")
    if configured_url and configured_url != "driver://user:pass@localhost/dbname":
        return configured_url

    raise RuntimeError(
        "Tenant migration database URL is not configured. "
        "Pass it with fastapi-tenancy's migration manager or set `sqlalchemy.url`."
    )


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = dict(config.get_section(config.config_ini_section) or {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
