from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_organizations() -> list:
    return []


@router.post("/")
async def create_organization() -> dict[str, str]:
    return {"message": "created"}
