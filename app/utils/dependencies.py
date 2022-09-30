"""
OAuth2 Password Bearer Dependency setup
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.utils.users import get_user_by_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """get_current_user
    Get current user based on authentication token.

    Args:
        token (str, optional): Defaults to Depends(oauth2_scheme).

    Raises:
        HTTPException: if unauthorized (401)
        HTTPException: if inactive / generic auth error (400)

    Returns:
        UserDetails: Details of user with given token
    """
    user = await get_user_by_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user
