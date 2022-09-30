"""
Database model for Users.
"""
from __future__ import annotations

from datetime import datetime, date
from typing import List

from sqlalchemy import (
    Table,
    text,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Date,
    ForeignKey,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.common import Base
from app.models.posts import Post

# Association tables (as metadata)

# User interests
interests_table = Table(
    "user_interest",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("interest_id", ForeignKey("interest.id"), primary_key=True),
)


# Subscriptions (self-referential many-to-many)
subscriptions_table = Table(
    "subscriptions",
    Base.metadata,
    Column("subscriber_id", ForeignKey("user.id"), primary_key=True),
    Column("subscription_id", ForeignKey("user.id"), primary_key=True),
)

# pylint: disable=too-few-public-methods
# Main classes / tables of model


class Token(Base):
    """Token

    The database model for user Tokens
    """

    __tablename__ = "token"
    id: int = Column(Integer, primary_key=True)
    token: str = Column(
        UUID(as_uuid=False),
        server_default=text("uuid_generate_v4()"),
        unique=True,
        nullable=False,
        index=True,
    )
    expires: datetime = Column(DateTime())
    user_id: int = Column(Integer, ForeignKey("user.id"))

    user: User = relationship("User")


class Interest(Base):
    """Interest

    The database model for user Interests
    """

    __tablename__ = "interest"
    id: int = Column(Integer, primary_key=True)
    interest: str = Column(String(100), unique=True, index=True)

    def __str__(self) -> str:
        return self.interest


class User(Base):
    """User

    The database model for Users
    """

    __tablename__ = "user"
    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String(100), unique=True, index=True)

    hashed_password: str = Column(String())
    is_active: bool = Column(
        Boolean(), server_default=expression.true(), nullable=False
    )

    short_biography: str = Column(Text())
    birth_date: date = Column(Date)
    country: str = Column(String(100))
    city: str = Column(String(100))

    interests: List[Interest] = relationship("Interest", secondary=interests_table)
    posts: List[Post] = relationship("Post", back_populates="user")
    subscribers: List[User] = relationship(
        "User",
        secondary=subscriptions_table,
        primaryjoin=(id == subscriptions_table.c.subscription_id),
        secondaryjoin=(id == subscriptions_table.c.subscriber_id),
        back_populates="subscriptions",
    )
    subscriptions: List[User] = relationship(
        "User",
        secondary=subscriptions_table,
        primaryjoin=(id == subscriptions_table.c.subscriber_id),
        secondaryjoin=(id == subscriptions_table.c.subscription_id),
        back_populates="subscribers",
    )

    def set_all(self, **kwargs):
        """
        Set all attributes via kwargs
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
