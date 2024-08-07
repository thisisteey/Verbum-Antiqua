#!/usr/bin/python3
"""Module for PostLike model schema for database representation"""
from sqlalchemy import UniqueConstraint, Column, String, TIMESTAMP, ForeignKey
from datetime import datetime

from . import Base, BaseModel


class PostLike(BaseModel, Base):
    """PostLike model class for like on a post"""
    __tablename__ = 'posts_likes'
    __table_args__ = (
        UniqueConstraint('post_id', 'user_id', name='unique_reaction'))
    id = Column(String(64), unique=True, nullable=False, primary_key=True)
    created_on = Column(TIMESTAMP(True), nullable=False,
                        default=datetime.utcnow())
    post_id = Column(String(64), ForeignKey('posts.id'), nullable=False)
    user_id = Column(String(64), ForeignKey('users.id'), nullable=False)
