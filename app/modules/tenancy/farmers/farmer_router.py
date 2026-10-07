from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import SuccessResponse, default_error_responses, response
from app.core.services.tenant_service import get_tenant_db_from_jwt
from app.modules.tenancy.farmers.dtos import (
    CreateFarmerPayload,
    CreateFarmerResult,
)
from app.modules.tenancy.farmers.farmer_service import farmer_service


farmer_router = APIRouter(prefix="/tenancy/farmers", tags=["tenancy:farmers"])


@farmer_router.post(
    "",
    response_model=SuccessResponse[CreateFarmerResult],
    responses=default_error_responses(),
)
async def create_farmer(
    session: Annotated[AsyncSession, Depends(get_tenant_db_from_jwt)],
    create_farmer_payload: CreateFarmerPayload,
):
    farmer = await farmer_service.create_farmer(session, create_farmer_payload)

    return response(
        data=CreateFarmerResult.model_validate(farmer),
    )
