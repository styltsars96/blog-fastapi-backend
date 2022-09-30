"""
Posts service facade + utilities

Service on top of DBSessionMiddleware from FastAPI
"""
from typing import List
from sqlalchemy import desc, func, update
from fastapi_sqlalchemy import db
from pydantic import parse_obj_as

from app.models.posts import Post as PostModel
from app.models.users import User as UserModel, subscriptions_table
from app.schemas.posts import PostSearchInputsSchema, PostSchema, PostDetailsSchema
from app.schemas.users import UserBase


DEFAULT_PAGE_COUNT = 5


# Service


async def create_post(post: PostSchema, user: UserBase) -> PostDetailsSchema:
    """create_post
    User adds a post

    Args:
        post (PostSchema): Post input
        user (UserBase): User basic info

    Returns:
        PostDetailsSchema: _description_
    """
    new_post: PostModel = PostModel(user_id=user.id, **post.dict())

    with db():
        db.session.add(new_post)
        db.session.commit()

        post_details = PostDetailsSchema.from_orm(new_post)
        post_details.user_id = user.id
        post_details.username = user.username
        return post_details


async def get_post(post_id: int) -> PostDetailsSchema:
    """get_post
    Get post by id

    Args:
        post_id (int): ID of post

    Returns:
        _type_: _description_
    """
    with db():
        post: PostModel = db.session.get(PostModel, post_id)
        post_details = PostDetailsSchema.from_orm(post)
        user: UserModel = post.user
        post_details.user_id = user.id
        post_details.username = user.username
        return post_details


async def get_latest_posts(
    page: int, max_per_page: int = DEFAULT_PAGE_COUNT
) -> List[PostDetailsSchema]:
    """get_latest_posts
    Get a page of the latest posts.

    Args:
        page (int): Page number, first page is 1.
        max_per_page (int, optional): Number of elements per page. Defaults to 10.

    Returns:
        List[PostDetailsSchema]: List / page of posts
    """
    page_offset = (page - 1) * max_per_page
    with db():
        db_result = (
            db.session.query(
                PostModel.id,
                PostModel.title,
                PostModel.post_content,
                PostModel.date_published,
                PostModel.user_id,
                UserModel.username,
            )
            .join(PostModel.user)
            .order_by(desc(PostModel.date_published))
            .limit(max_per_page)
            .offset(page_offset)
            .all()
        )
        return parse_obj_as(List[PostDetailsSchema], db_result)


async def get_total_posts_count() -> int:
    """get_posts_count
    Get the number of posts currently available.

    Returns:
        int: Total number of posts
    """
    with db():
        result = db.session.query(func.count(PostModel.id)).scalar()
        return int(result)


async def update_post(post_id: int, post: PostSchema):
    """update_post
    Update a post, given its ID.

    Args:
        post_id (int): Post id
        post (PostSchema): Updated content for post

    Returns:
        _type_: _description_
    """
    query = update(PostModel).where(PostModel.id == post_id).values(**post.dict())
    with db():
        db.session.execute(query)
        db.session.commit()


async def search_user_posts(
    user_id: int,
    search_input: PostSearchInputsSchema,
    page: int = 1,
    max_per_page: int = DEFAULT_PAGE_COUNT,
    subscriptions_mode=False,
    usernames_list: List[str] = [],
) -> List[PostDetailsSchema]:
    """
    Search Posts for a user.

    If subscriptions_mode = True, the search is constrained on
    the subscriptions of the target user. (Target is now current user)

    Args:
        user_id (int): Target user id
        search_input (OwnPostSearchInputsSchema): Search input parameters
        page (int, optional): Page of results. Defaults to 1.
        max_per_page (int, optional): Max number of results per page. Defaults to DEFAULT_PAGE_COUNT.
        subscriptions_mode (bool, optional): Search subscriptions. Defaults to False.
        usernames_list (List[str], optional): For subscriptions_mode only. List of usernames as filters Defaults to [].

    Returns:
        List[PostDetailsSchema]: List of posts
    """
    page_offset = (page - 1) * max_per_page
    with db():
        query = (
            db.session.query(
                PostModel.id,
                PostModel.title,
                PostModel.post_content,
                PostModel.date_published,
                PostModel.user_id,
                UserModel.username,
            )
            .join(PostModel.user)
            .order_by(desc(PostModel.date_published))
        )

        if subscriptions_mode:
            query = query.filter(
                db.session.query(subscriptions_table.c.subscription_id)
                .where(subscriptions_table.c.subscriber_id == user_id)
                .where(PostModel.user_id == subscriptions_table.c.subscription_id)
                .exists()
            )

            if usernames_list:
                query = query.filter(UserModel.username.in_(usernames_list))

        else:
            query = query.where(PostModel.user_id == user_id)

        if search_input.start_date:
            query = query.where(PostModel.date_published >= search_input.start_date)

        if search_input.end_date:
            query = query.where(PostModel.date_published <= search_input.end_date)

        if search_input.title_search:
            query = query.where(
                func.lower(PostModel.title).contains(
                    func.lower(search_input.title_search)
                )
            )

        if search_input.content_search:
            query = query.where(
                func.lower(PostModel.post_content).contains(
                    func.lower(search_input.content_search)
                )
            )

        db_result = query.limit(max_per_page).offset(page_offset).all()
        return parse_obj_as(List[PostDetailsSchema], db_result)


async def get_latest_user_posts(
    user_id: int, page: int = 1, max_per_page: int = DEFAULT_PAGE_COUNT
) -> List[PostDetailsSchema]:
    """
    Get the latest posts for a specific user

    Args:
        user_id (int): ID of target user
        page (int, optional): Page. Defaults to 1.
        max_per_page (int, optional): How many posts a page can have at most. Defaults to DEFAULT_PAGE_COUNT.

    Returns:
        List[PostDetailsSchema]: List of the latest posts
    """
    return await search_user_posts(
        user_id, PostSearchInputsSchema(), page, max_per_page
    )
