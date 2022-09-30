"""
Users router + controller.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.users import (
    OtherUserProfileView,
    TokenBase,
    UserAuthResponse,
    UserCreate,
    UserCredentials,
    UserDetails,
    UserProfile,
    UserProfileUpdate,
)
from app.utils.users import (
    create_new_user,
    get_other_user_data,
    get_user_auth_by_username,
    get_user_profile,
    get_user_profile_view,
    password_is_strong,
    update_user,
    user_subscribes_to,
    user_unsubscribes_from,
    validate_password,
    create_user_token,
)
from app.utils.dependencies import get_current_user

router = APIRouter()

DEFAULT_PAGE_NUMBER = 1
DEFAULT_PAGE_COUNT = 10


@router.get("/")
async def health_check():
    """
    Returns:
        Dict[str, str]: Hello World
    """
    return {"Hello": "World"}


@router.post("/auth", response_model=TokenBase)
async def auth_endpoint(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authentication endpoint, using standard OAuth2 Password authentication procedure.

    Args:
        form_data (OAuth2PasswordRequestForm, optional): Defaults to Depends().

    Raises:
        HTTPException: 400, Incorrect username or password

    Returns:
        TokenBase: Returns an authorization token
    """
    user = await get_user_auth_by_username(username=form_data.username)

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    if not validate_password(
        password=form_data.password, hashed_password=user.hashed_password
    ):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return await create_user_token(user_id=user.id)


@router.post("/sign-up", response_model=UserAuthResponse)
async def create_user(user: UserCreate):
    """
    User registration

    An acceptable password has:
    - Length of at least 10 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character _@$#%&

    Args:
        user (UserCreate): Username and password for registration

    Raises:
        HTTPException: 400 if username exists
        HTTPException: 400 if password is not strong enough

    Returns:
        UserAuthResponse: Basic user details plus authentication details
    """
    db_user = await get_user_auth_by_username(username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    if not password_is_strong(user.password):
        raise HTTPException(status_code=400, detail="Password is not strong enough")

    return await create_new_user(user=user)


@router.post("/update-credentials", response_model=UserAuthResponse)
async def update_credentials(
    new_credentials: UserCredentials,
    current_user: UserDetails = Depends(get_current_user),
):
    """
    Update the current user credentials

    Username must not exist
    Password must be strong enough

    Args:
        user_credentials (UserCredentials): New user credentials
        current_user (UserDetails, optional): Defaults to Depends(get_current_user).

    Returns:
        UserAuthResponse: Basic user details plus authentication details
    """
    if not new_credentials.username == current_user.username:
        db_user = await get_user_auth_by_username(username=new_credentials.username)
        if db_user:
            raise HTTPException(
                status_code=400, detail="That username is used by another user"
            )

    if not password_is_strong(new_credentials.password):
        raise HTTPException(status_code=400, detail="Password is not strong enough")

    return await update_user(current_user, new_credentials)


@router.get("/me/profile", response_model=UserProfile)
async def get_my_user_details(current_user: UserDetails = Depends(get_current_user)):
    """
    Get details about current user

    Args:
        current_user (users.User, optional): Defaults to Depends(get_current_user).

    Returns:
        UserDetails: User details
    """

    return await get_user_profile(user_id=current_user.id)


@router.post("/me/profile", response_model=UserProfile)
async def update_my_user_details(
    profile_update: UserProfileUpdate,
    current_user: UserDetails = Depends(get_current_user),
):
    """
    Update user profile:
    - short biography
    - birth date
    - country
    - city
    - list of interests

    Args:
        profile_update (UserProfileUpdate): Updated user profile
        current_user (UserDetails, optional): Defaults to Depends(get_current_user).
    """
    user_dict = current_user.dict()
    update_dict = profile_update.dict()
    current_user = UserDetails(**{**user_dict, **update_dict})
    return await update_user(current_user, user_interests=profile_update.interests)


@router.get("/users", response_model=List[OtherUserProfileView])
async def get_other_users(
    page: int = DEFAULT_PAGE_NUMBER,
    count: int = DEFAULT_PAGE_COUNT,
    current_user: UserDetails = Depends(get_current_user),
):
    """
    Get other users info.

    The posts per user are only the 5 latest!

    Args:
        page (int, optional): Page of results. Defaults to DEFAULT_PAGE_NUMBER.
        count (int, optional): Max per page. Defaults to DEFAULT_PAGE_COUNT.
        current_user (users.User, optional): Defaults to Depends(get_current_user).
    """
    return await get_other_user_data(current_user.id, page, count)


@router.get("/users/{user_id}", response_model=OtherUserProfileView)
async def user_profile_view(user_id: int):
    """
    Get profile data / view of specific user

    Args:
        user_id (int): Target user
    """
    return await get_user_profile_view(user_id)


@router.get("/users/{user_id}/subscribe")
async def subscribe_to_user(
    user_id: int,
    current_user: UserDetails = Depends(get_current_user),
):
    """
    Subscribe to user

    Args:
        user_id (int): Target user
    """
    await user_subscribes_to(current_user.id, user_id)


@router.get("/users/{user_id}/unsubscribe")
async def unsubscribe_to_user(
    user_id: int,
    current_user: UserDetails = Depends(get_current_user),
):
    """
    Unsubscribe to user

    Args:
        user_id (int): Target user
    """
    await user_unsubscribes_from(current_user.id, user_id)
