from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy import text

from alembic import context
import app.data.models.tenants as tenant_models
from app.core.config import settings
from app.core.services.tenant_service import tenant_service
from app.data.models.tenants.base import tenant_registry

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = tenant_registry.metadata
_ = tenant_models


def get_targets() -> list[tuple[str, str]]:
    x_arguments = context.get_x_argument(as_dictionary=True)
    tenant_database_name = x_arguments.get("tenant_db")

    if tenant_database_name:
        return [
            (tenant_database_name, settings.build_database_uri(tenant_database_name))
        ]

    configured_url = config.get_main_option("sqlalchemy.url")
    if configured_url and configured_url != "driver://user:pass@localhost/dbname":
        return [("configured_tenant", configured_url)]

    return get_all_tenant_targets()


def get_all_tenant_targets() -> list[tuple[str, str]]:
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        poolclass=pool.NullPool,
    )

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT name FROM tenants ORDER BY id"))
            tenant_names = [row[0] for row in result]
    finally:
        engine.dispose()

    if not tenant_names:
        raise RuntimeError(
            "No tenants found in the shared tenants table. "
            "Create a tenant first or run Alembic with `-x tenant_db=<database_name>`."
        )

    return [
        (
            tenant_name,
            settings.build_database_uri(
                tenant_service.build_tenant_database_name(tenant_name)
            ),
        )
        for tenant_name in tenant_names
    ]


def run_migrations_offline() -> None:
    targets = get_targets()

    if len(targets) != 1:
        raise RuntimeError(
            "Offline tenant migrations require a single target database. "
            "Run Alembic with `-x tenant_db=<database_name>` or set `sqlalchemy.url`."
        )

    _, target_url = targets[0]
    context.configure(
        url=target_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    for tenant_name, target_url in get_targets():
        configuration = dict(config.get_section(config.config_ini_section) or {})
        configuration["sqlalchemy.url"] = target_url

        config.print_stdout(
            f"Migrating tenant '{tenant_name}' with database '{target_url.rsplit('/', 1)[-1]}'"
        )

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
