"""
Posts schema
"""
from datetime import date, datetime
from typing import List

from pydantic import BaseModel


# Due to pydantic validators:
# pylint: disable=no-self-argument
# Due to pydantic Config class:
# pylint: disable=too-few-public-methods
# pylint: disable=missing-class-docstring


class PostSchema(BaseModel):
    """
    Validate request data
    """

    title: str
    post_content: str

    class Config:
        orm_mode = True


class PostDetailsSchema(PostSchema):
    """
    Return response data
    """

    id: int
    date_published: datetime
    user_id: int = None
    username: str = ""

    class Config:
        orm_mode = True


class PostResultsSchema(BaseModel):
    """
    Return response data
    """

    total_count: int
    results: List[PostDetailsSchema]


class PostSearchInputsSchema(BaseModel):
    """
    Validate search request data
    """

    title_search: str = ""
    start_date: date = None
    end_date: date = None
    content_search: str = ""


class SubscriptionPostSearchInputsSchema(PostSearchInputsSchema):
    """
    Validate search request data
    """

    usernames_list: List[str] = []
