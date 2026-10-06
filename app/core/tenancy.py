from fastapi_tenancy import TenancyConfig, TenancyManager
from fastapi_tenancy.dependencies import make_tenant_db_dependency
from fastapi_tenancy.migrations.manager import TenantMigrationManager
from fastapi_tenancy.storage.database import SQLAlchemyTenantStore

from app.core.config import settings


tenancy_config = TenancyConfig(
    database_url=settings.SQLALCHEMY_DATABASE_URI,
    resolution_strategy="header",
    isolation_strategy="database",
    database_url_template=settings.SQLALCHEMY_TENANT_DATABASE_URL_TEMPLATE,
    tenant_header_name=settings.TENANCY_TENANT_HEADER_NAME,
    enable_soft_delete=False,
)

tenant_store = SQLAlchemyTenantStore(settings.SQLALCHEMY_DATABASE_URI)
tenancy_manager = TenancyManager(tenancy_config, tenant_store)
tenant_migration_manager = TenantMigrationManager(
    config=tenancy_config,
    store=tenant_store,
    alembic_cfg_path="alembic_tenants.ini",
)

get_tenant_db = make_tenant_db_dependency(tenancy_manager)
