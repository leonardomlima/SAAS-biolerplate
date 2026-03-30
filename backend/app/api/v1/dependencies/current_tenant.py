from fastapi import Request


async def get_current_tenant(request: Request) -> str | None:
    return getattr(request.state, "tenant_id", None)
