from sqlalchemy import MetaData
from sqlalchemy.orm import registry
from sqlmodel import SQLModel

tenant_registry = registry(metadata=MetaData())


class TenantSQLModel(SQLModel, registry=tenant_registry):
    __abstract__ = True
