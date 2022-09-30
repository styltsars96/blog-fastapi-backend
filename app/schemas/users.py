"""
Users schema
"""
from datetime import date, datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel, validator, Field

from app.schemas.posts import PostDetailsSchema

# Due to pydantic validators:
# pylint: disable=no-self-argument
# Due to pydantic Config class:
# pylint: disable=too-few-public-methods
# pylint: disable=missing-class-docstring


class Interest(BaseModel):
    """
    Return response data
    """

    id: int
    interest: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class TokenBase(BaseModel):
    """
    Return response data
    """

    token: UUID4 = Field(..., alias="access_token")
    expires: datetime
    token_type: Optional[str] = "bearer"

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    @validator("token")
    def hexlify_token(cls, value):
        """
        Convert UUID to pure hex string
        """
        return value.hex


class UserBase(BaseModel):
    """
    Return response data
    """

    id: int
    username: str

    class Config:
        orm_mode = True


class UserCredentials(BaseModel):
    """
    User credentials update/input
    """

    username: str
    password: str

    class Config:
        orm_mode = True


class UserCreate(UserCredentials):
    """
    Validate request data
    """

    short_biography: str
    birth_date: date
    country: str
    city: str


class UserDetails(UserBase):
    """
    Return User details
    """

    is_active: bool
    short_biography: str = ""
    birth_date: date = ""
    country: str = ""
    city: str = ""


class UserProfileUpdate(BaseModel):
    """
    Update user profile
    """

    short_biography: str = ""
    birth_date: date = ""
    country: str = ""
    city: str = ""
    interests: List[str] = []

    class Config:
        orm_mode = True


class UserProfile(UserDetails):
    """
    Return User profile details
    """

    interests: List[Interest] = []
    subscribers_number: int = 0
    subscriptions_number: int = 0
    posts_number: int = 0


class UserAuthResponse(UserBase):
    """
    Return User authentication response data
    """

    token: TokenBase = {}


class UserUpdateResponse(UserProfile, UserAuthResponse):
    """
    Return all user details
    """


class UserAuth(UserAuthResponse):
    """
    Intermediate user auth details
    """

    hashed_password: str


class OtherUserProfileView(UserBase):
    """
    Profile view of other users
    """

    short_biography: str = ""
    birth_date: date = ""
    country: str = ""
    city: str = ""
    interests: List[Interest] = []
    subscribers_number: int = 0
    posts: List[PostDetailsSchema] = []
