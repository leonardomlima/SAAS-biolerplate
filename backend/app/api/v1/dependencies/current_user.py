from fastapi import Depends

from app.core.security import oauth2_scheme


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict[str, str]:
    return {"sub": token}
