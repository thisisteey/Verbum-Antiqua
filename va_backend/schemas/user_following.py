#!/usr/bin/python3
"""Module for UserFollowing model schema for database representation"""
from sqlalchemy import UniqueConstraint, Column, String, TIMESTAMP, ForeignKey
from datetime import datetime

from . import Base, BaseModel


class UserFollowing(Base):
    """UserFollowing model class to show connection between two users"""
    __tablename__ = 'users_followings'
    __table_args__ = (UniqueConstraint('follower_id', 'following_id',
                                       name='unique_connection'))
    id = Column(String(64), unique=True, nullable=False, primary_key=True)
    created_on = Column(TIMESTAMP(True), nullable=False,
                        default=datetime.utcnow())
    follower_id = Column(String(64), ForeignKey('users.id'), nullable=False)
    following_id = Column(String(64), ForeignKey('users.id'), nullable=False)
