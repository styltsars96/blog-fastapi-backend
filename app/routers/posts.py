"""
Posts router + controller.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.posts import (
    PostSearchInputsSchema,
    PostDetailsSchema,
    PostResultsSchema,
    PostSchema,
    SubscriptionPostSearchInputsSchema,
)
from app.schemas.users import UserDetails
from app.utils.posts import (
    get_latest_user_posts,
    get_total_posts_count,
    get_latest_posts,
    search_user_posts,
    update_post,
    get_post,
    create_post,
)
from app.utils.dependencies import get_current_user

DEFAULT_PAGE_NUMBER = 1
DEFAULT_PAGE_COUNT = 10


router = APIRouter()


@router.put("/posts", response_model=PostDetailsSchema, status_code=201)
async def create_post_endpoint(
    post: PostSchema, current_user: UserDetails = Depends(get_current_user)
):
    """
    Create a post

    Args:
        post (PostSchema): Post input
        current_user (UserDetails, optional): Defaults to Depends(get_current_user).

    Returns:
        PostDetailsSchema: Post details
    """
    post = await create_post(post, current_user)
    # TODO: WebSocket notification to start from here.
    return post


@router.get("/posts", response_model=PostResultsSchema)
async def get_posts_endpoint(
    page: int = DEFAULT_PAGE_NUMBER, count: int = DEFAULT_PAGE_COUNT
):
    """
    Get a page of latest posts

    Args:
        page (int, optional): Page number. Defaults to 1.

    Returns:
        PostResultsSchema: How many were returned, and results
    """
    total_count = await get_total_posts_count()
    posts = await get_latest_posts(page, count)
    return PostResultsSchema(total_count=total_count, results=posts)


@router.get("/posts/{post_id}", response_model=PostDetailsSchema)
async def get_post_endpoint(post_id: int):
    """
    Get a post by its id

    Args:
        post_id (int): id

    Returns:
        PostDetailsSchema: Post details
    """
    return await get_post(post_id)


@router.post("/posts/{post_id}", response_model=PostDetailsSchema)
async def update_post_endpoint(
    post_id: int,
    post_data: PostSchema,
    current_user: UserDetails = Depends(get_current_user),
):
    """
    Updates post, determined by its id

    Args:
        post_id (int): id
        post_data (PostSchema): All post details
        current_user (_type_, optional): Defaults to Depends(get_current_user).

    Raises:
        HTTPException: 403 Forbidden, no access to post

    Returns:
        PostDetailsSchema: Post details
    """
    post: PostDetailsSchema = await get_post(post_id)
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to modify this post",
        )

    await update_post(post_id=post_id, post=post_data)
    return await get_post(post_id)


@router.get("/users/{user_id}/posts", response_model=List[PostDetailsSchema])
async def get_user_posts(
    user_id: int, page: int = DEFAULT_PAGE_NUMBER, count: int = DEFAULT_PAGE_COUNT
):
    """
    Get the latest posts from specific user.

    Args:
        user_id (int): ID of user
        page (int, optional): Page number. Defaults to DEFAULT_PAGE_NUMBER.
        count (int, optional): How many per page. Defaults to DEFAULT_PAGE_COUNT.
    """
    return await get_latest_user_posts(user_id, page, count)


@router.get("/me/posts", response_model=List[PostDetailsSchema])
async def get_my_posts(
    page: int = DEFAULT_PAGE_NUMBER,
    count: int = DEFAULT_PAGE_COUNT,
    current_user: UserDetails = Depends(get_current_user),
):
    """
    Get current users posts

    Args:
        page (int, optional): Page number. Defaults to DEFAULT_PAGE_NUMBER.
        count (int, optional): How many per page. Defaults to DEFAULT_PAGE_COUNT.
        current_user (_type_, optional): Defaults to Depends(get_current_user).

    Raises:
        HTTPException: 403 Forbidden, no access to post
    """

    return await get_latest_user_posts(current_user.id, page, count)


@router.post("/me/posts", response_model=List[PostDetailsSchema])
async def search_my_posts(
    post_search: PostSearchInputsSchema,
    page: int = DEFAULT_PAGE_NUMBER,
    count: int = DEFAULT_PAGE_COUNT,
    current_user: UserDetails = Depends(get_current_user),
):
    """
    Search current user's posts

    Args:
        post_search (OwnPostSearchInputsSchema): Search parameters
        page (int, optional): Page of results. Defaults to DEFAULT_PAGE_NUMBER.
        count (int, optional): Max number of results per page. Defaults to DEFAULT_PAGE_COUNT.
        current_user (_type_, optional): Defaults to Depends(get_current_user).
    """
    return await search_user_posts(current_user.id, post_search, page, count)


@router.post("/users/{user_id}/posts", response_model=List[PostDetailsSchema])
async def search_another_user_posts(
    user_id: int,
    post_search: PostSearchInputsSchema,
    page: int = DEFAULT_PAGE_NUMBER,
    count: int = DEFAULT_PAGE_COUNT,
):
    """
    Search a user's posts

    Args:
        user_id (int): ID of user
        post_search (OwnPostSearchInputsSchema): Search parameters
        page (int, optional): Page of results. Defaults to DEFAULT_PAGE_NUMBER.
        max_per_page (int, optional): Max number of results per page. Defaults to DEFAULT_PAGE_COUNT.
    """
    return await search_user_posts(user_id, post_search, page, count)


@router.post("/me/subscriptions/posts", response_model=List[PostDetailsSchema])
async def search_subscriptions_for_posts(
    post_search: SubscriptionPostSearchInputsSchema,
    page: int = DEFAULT_PAGE_NUMBER,
    count: int = DEFAULT_PAGE_COUNT,
    current_user: UserDetails = Depends(get_current_user),
):
    """
    Search current user's subscriptions for posts

    Args:
        post_search (SubscriptionPostSearchInputsSchema): _description_
        page (int, optional): _description_. Defaults to DEFAULT_PAGE_NUMBER.
        count (int, optional): _description_. Defaults to DEFAULT_PAGE_COUNT.
        current_user (UserDetails, optional): _description_. Defaults to Depends(get_current_user).
    """

    return await search_user_posts(
        current_user.id,
        PostSearchInputsSchema(**post_search.dict()),
        page,
        count,
        True,
        post_search.usernames_list,
    )
