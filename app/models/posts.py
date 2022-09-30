"""
Database model for Posts.
"""
# pylint: disable=too-few-public-methods

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.common import Base


class Post(Base):
    """Post

    The database model for Posts
    """

    __tablename__ = "post"
    id: int = Column(Integer, primary_key=True, index=True)
    user_id: int = Column(Integer, ForeignKey("user.id"))
    title: str = Column(String(100))
    date_published: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    post_content: str = Column(String(1000))

    user = relationship("User", back_populates="posts")
