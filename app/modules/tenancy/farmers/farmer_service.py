from app.data.models.tenants.farmer import Farmer
from app.modules.tenancy.farmers.dtos import CreateFarmerPayload
from sqlalchemy.ext.asyncio import AsyncSession


class FarmerService:
    async def create_farmer(
        self,
        session: AsyncSession,
        create_farmer_payload: CreateFarmerPayload,
    ) -> Farmer:
        farmer = Farmer(
            name=create_farmer_payload.name.strip(),
            is_active=create_farmer_payload.is_active,
        )
        session.add(farmer)
        await session.commit()
        await session.refresh(farmer)

        return farmer


farmer_service = FarmerService()
