class AsaasService:
    base_url = "https://api.asaas.com/v3"

    async def create_checkout(self, customer_id: str, plan_id: str) -> dict:
        return {"checkout_url": "https://sandbox.asaas.com/checkout", "customer_id": customer_id, "plan_id": plan_id}

    async def handle_webhook(self, payload: dict) -> dict:
        return {"processed": True, "event": payload.get("event")}
