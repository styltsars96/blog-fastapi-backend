"""
Users service facade + utilities

Service on top of DBSessionMiddleware from FastAPI
"""
import base64
import hashlib
import secrets
import re
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi_sqlalchemy import db
from sqlalchemy import select, update, func, delete, desc
from pydantic import parse_obj_as

from app.models.users import (
    Interest,
    Token as TokenModel,
    User as UserModel,
    interests_table,
    subscriptions_table,
)
from app.models.posts import Post as PostModel
from app.schemas.users import (
    OtherUserProfileView,
    TokenBase,
    UserCredentials,
    UserDetails,
    UserAuth,
    UserAuthResponse,
    UserCreate,
    UserProfile,
    UserUpdateResponse,
)
from app.utils.posts import get_latest_user_posts


EXPIRATION_WEEKS = 1
RANDOM_LENGTH = 32
ITERATIONS = 260_000
ALGORITHM = "pbkdf2_sha256"

MIN_PASSWORD_LENGTH = 10

DEFAULT_PAGE_COUNT = 5
DEFAULT_PAGE_NUMBER = 1
# Utilities


def get_token_string(length=RANDOM_LENGTH) -> str:
    """get_token_string
    Get/create a random string / token for security purposes

    Args:
        length (int, optional): Defaults to RANDOM_LENGTH.

    Returns:
        str: A random bytes string
    """
    return secrets.token_hex(length)


def hash_password(password: str, salt: str = None, iterations=ITERATIONS) -> str:
    """hash_password
    Create the hash of the password, using PBKDF2 HMAC.

    Args:
        password (str): The password to be hashed
        salt (str, optional): Cryptographic hash function salt. Defaults to None.

    Returns:
        str: Digest of password
    """
    if salt is None:
        salt = get_token_string()
    password_b64_hash: bytes = hashlib.pbkdf2_hmac(
        ALGORITHM.replace("pbkdf2_", ""),
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    password_b64_hash = base64.b64encode(password_b64_hash).decode("ascii").strip()
    return f"{ALGORITHM}${ITERATIONS}${salt}${password_b64_hash}"


def validate_password(password: str, hashed_password: str) -> bool:
    """validate_password
    Check if the password is correct.

    Utilizes best cryptographic practices.

    Args:
        password (str): The given password to check.
        hashed_password (str): The hashed password.

    Returns:
        bool: True if the password is correct
    """
    if (hashed_password or "").count("$") != 3:
        return False
    algorithm, iterations, salt, b64_hash = hashed_password.split("$", 3)
    iterations = int(iterations)
    assert algorithm == ALGORITHM  # Catch errors due to wrong algorithm
    compare_hash = hash_password(password, salt, iterations)
    return secrets.compare_digest(hashed_password, compare_hash)


def password_is_strong(password: str) -> bool:
    """password_is_strong

    Checks if password is strong enough,
    by meeting the following criteria:
    - Length of at least 10 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character _@$#%&


    Args:
        password (str): Password to be tested

    Returns:
        bool: True if strong enough
    """
    is_strong = False

    # The while clause is just for switch-styled breaking
    while True:
        if len(password) < MIN_PASSWORD_LENGTH:
            is_strong = False
            break
        if not re.search("[a-z]", password):
            is_strong = False
            break
        if not re.search("[A-Z]", password):
            is_strong = False
            break
        if not re.search("[0-9]", password):
            is_strong = False
            break
        if not re.search("[_@$#%&]", password):
            is_strong = False
            break
        # pylint: disable=anomalous-backslash-in-string
        if re.search("\s", password):
            is_strong = False
            break

        is_strong = True
        break

    return is_strong


# Service


async def get_user_by_id(user_id: int) -> UserDetails:
    """get_user_by_id
    Get user details based on their ID

    Args:
        user_id (int): User id

    Returns:
        User: A user instance
    """
    with db():
        return UserDetails.from_orm(db.session.get(UserModel, user_id))


async def get_user_profile(
    user_id: int = None, username: str = None
) -> Optional[UserProfile]:
    """get_user_profile_by_id

    Get all user profile details by user id or username

    Args:
        user_id (int): id. Defaults to None
        username (str): Target username. Defaults to None

    Returns:
        UserProfile: All user details, or None
    """
    if (user_id is None or user_id < 0) and username is None:
        return None

    user: UserModel
    with db():
        if user_id is not None and user_id > 0:
            user = (
                db.session.query(UserModel).where(UserModel.id == user_id).one_or_none()
            )
        else:
            user = (
                db.session.query(UserModel)
                .where(UserModel.username == username)
                .one_or_none()
            )

        user_profile = UserProfile.from_orm(user)

        user_profile.posts_number: int = db.session.execute(
            select(func.count(PostModel.id)).where(PostModel.user_id == user.id)
        ).scalar()
        user_profile.subscribers_number: int = len(user.subscribers)
        user_profile.subscriptions_number: int = len(user.subscriptions)
        return user_profile


async def get_user_auth_by_username(username: str) -> Optional[UserAuth]:
    """get_user_by_username

    Get user auth details based on their username

    Args:
        username (str): username

    Returns:
        User: A user instance
    """
    with db():
        user = (
            db.session.query(UserModel)
            .filter(UserModel.username == username)
            .one_or_none()
        )
        if not user:
            return None

        return UserAuth.from_orm(user)


async def create_user_token(user_id: int) -> TokenBase:
    """create_user_token
    Create a new user authentication token

    Args:
        user_id (int): User ID

    Returns:
        TokenBase: Response containing the authentication token
    """
    new_token = TokenModel(
        expires=datetime.now() + timedelta(weeks=EXPIRATION_WEEKS), user_id=user_id
    )
    with db():
        db.session.add(new_token)
        db.session.commit()
        return TokenBase.from_orm(new_token)


async def create_new_user(user: UserCreate) -> UserAuthResponse:
    """create_new_user

    Create new user

    Args:
        user (UserCreate): The required details from a user.

    Returns:
        UserAuth: Basic user details plus authentication details
    """
    salt = get_token_string()
    user_dict = user.dict()

    del user_dict["password"]
    hashed_password = hash_password(user.password, salt)

    new_user = UserModel(
        **user_dict,
        hashed_password=hashed_password,
        is_active=True,
    )
    with db():
        db.session.add(new_user)
        db.session.commit()
        token = await create_user_token(new_user.id)
        new_user_auth = UserAuthResponse.from_orm(new_user)
        new_user_auth.token = TokenBase.from_orm(token)
        return new_user_auth


async def update_interest(interest: str, user_id: int) -> Interest:
    """
    Check existence of interest, add add new if it does not exist.
    Makes sure the user is associated with the interest.

    Args:
        interest (str): Interest value
        user_id (int): Target user

    Returns:
        Interest: Interest object
    """
    with db():
        fetched_interest: Interest = (
            db.session.query(Interest)
            .filter(Interest.interest == interest)
            .one_or_none()
        )

        if not fetched_interest:
            session = db.session
            fetched_interest = Interest(interest=interest)
            session.add(fetched_interest)
            session.commit()

        association = db.session.execute(
            select(interests_table)
            .where(interests_table.c.user_id == user_id)
            .where(interests_table.c.interest_id == fetched_interest.id)
        ).one_or_none()

        if not association:
            session = db.session
            session.execute(
                interests_table.insert().values(
                    user_id=user_id, interest_id=fetched_interest.id
                )
            )
            session.commit()

        return fetched_interest


async def update_user(
    user_details: UserDetails,
    user_credentials: Optional[UserCredentials] = None,
    user_interests: Optional[List[str]] = None,
) -> UserUpdateResponse:
    """update_user

    Args:
        user_Details (UserDetails): User details
        user_credentials (UserCredentials): New credentials or None. Defaults to None
        user_interests (List[str]): Interests a user expresses. Defaults to None

    Returns:
        UserAuthResponse: Basic user details plus authentication details
    """

    user_dict = user_details.dict()

    del user_dict["id"]

    # Update of user credentials
    if not user_credentials is None:
        salt = get_token_string()
        user_dict["hashed_password"] = hash_password(user_credentials.password, salt)
        user_credentials_dict = user_credentials.dict()
        del user_credentials_dict["password"]
        user_dict = {**user_dict, **user_credentials_dict}

    # Update interest associations if indicated
    if user_interests is not None:
        # Clear previous interest associations
        prep_query = delete(interests_table).where(
            interests_table.c.user_id == user_details.id
        )
        with db():
            db.session.execute(prep_query)
            db.session.commit()
        # Update interests
        for interest in user_interests:
            await update_interest(interest, user_details.id)

    # Main update query
    query = update(UserModel).where(UserModel.id == user_details.id).values(**user_dict)
    with db():
        db.session.execute(query)
        db.session.commit()

        db_user: UserModel = db.session.get(UserModel, user_details.id)
        updatable_user = UserUpdateResponse.from_orm(db_user)

        updatable_user.posts_number: int = db.session.execute(
            select(func.count(PostModel.id)).where(
                PostModel.user_id == updatable_user.id
            )
        ).scalar()

        updatable_user.subscribers_number: int = len(db_user.subscribers)
        updatable_user.subscriptions_number: int = len(db_user.subscriptions)

        token = await create_user_token(updatable_user.id)
        updatable_user.token = TokenBase.from_orm(token)
        return updatable_user


async def get_user_by_token(token: str) -> Optional[UserDetails]:
    """get_user_by_token

    Get user by the given token

    Args:
        token (str): The provided token

    Returns:
        UserProfile: The user's complete details
    """
    with db():
        token_db: Optional[TokenModel] = (
            db.session.query(TokenModel)
            .filter(TokenModel.token == token, TokenModel.expires > datetime.now())
            .one_or_none()
        )
        if not token_db:
            return None
        return UserDetails.from_orm(token_db.user)


async def get_other_user_data(
    current_user_id: int,
    page: int = DEFAULT_PAGE_NUMBER,
    count: int = DEFAULT_PAGE_COUNT,
    specific=False,
) -> List[OtherUserProfileView]:
    """
    Get data about other users

    Will get data about specific user, the "current",
    if specific=True.

    Otherwise other users appear, sorted by popularity, i.e. subscribers.

    Args:
        current_user_id (int): ID of current user
        page (int, optional): Page of results. Defaults to DEFAULT_PAGE_NUMBER.
        count (int, optional): Max number of results per page. Defaults to DEFAULT_PAGE_COUNT.
        specific (bool): If True, searches only for current_user_id. Defaults to False.

    Returns:
        List[OtherUserProfileView]: Data about other users
    """
    page_offset = (page - 1) * count
    with db():
        query = db.session.query(UserModel)

        if specific:
            query = query.where(UserModel.id == current_user_id)
        else:
            scalar = (
                select(func.count(subscriptions_table.c.subscriber_id))
                .where(UserModel.id == subscriptions_table.c.subscription_id)
                .as_scalar()
            )
            query = (
                query.where(UserModel.id != current_user_id)
                .order_by(scalar.desc())
                .limit(count)
                .offset(page_offset)
            )

        db_result = query.all()
        profiles_view = parse_obj_as(List[OtherUserProfileView], db_result)

        for profile in profiles_view:
            profile.posts = await get_latest_user_posts(profile.id, 1, 5)

        return profiles_view


async def get_user_profile_view(user_id: int) -> OtherUserProfileView:
    """
    Get profile view for specific user ID

    Args:
        user_id (int): User ID

    Returns:
        OtherUserProfileView: Data about another user
    """
    return (await get_other_user_data(user_id, specific=True))[0]


async def user_subscribes_to(subscriber_id, target_id):
    """
    User subscribes to another
    """
    query = subscriptions_table.insert().values(
        subscriber_id=subscriber_id, subscription_id=target_id
    )
    with db():
        session = db.session
        session.execute(query)
        session.commit()


async def user_unsubscribes_from(subscriber_id, target_id):
    """
    User unsubscribes from another
    """
    query = (
        delete(subscriptions_table)
        .where(subscriptions_table.c.subscriber_id == subscriber_id)
        .where(subscriptions_table.c.subscription_id == target_id)
    )
    with db():
        session = db.session
        session.execute(query)
        session.commit()
