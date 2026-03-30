from fastapi import APIRouter

router = APIRouter()


@router.get("/plans")
async def plans() -> list[dict]:
    return [{"id": "starter", "name": "Starter", "amount": 49.0}]


@router.post("/checkout")
async def checkout() -> dict[str, str]:
    return {"checkout_url": "https://sandbox.asaas.com/checkout"}


@router.post("/portal")
async def portal() -> dict[str, str]:
    return {"portal_url": "https://www.asaas.com"}


@router.post("/webhook")
async def webhook(payload: dict) -> dict:
    return {"ok": True, "event": payload.get("event")}


@router.get("/subscription")
async def subscription() -> dict[str, str]:
    return {"status": "PENDING"}
