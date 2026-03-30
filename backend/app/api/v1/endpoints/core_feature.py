from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def core_feature() -> dict[str, str]:
    return {"feature": "ok"}
