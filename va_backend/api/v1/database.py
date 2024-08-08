#!/usr/bin/python3
"""Module for managing database connections and sessions"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from schemas import Base
from schemas.comment import Comment
from schemas.post import Post
from schemas.post_like import PostLike
from schemas.user import User
from schemas.user_following import UserFollowing


def get_engine():
    """Creates and returns the database engine"""
    db_url = os.getenv('DATABASE_URL')
    engine = create_engine(db_url, pool_pre_ping=True)
    return engine


def init_database():
    """Drops and creates database tables"""
    engine = get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def get_session():
    """Returns a new SQLAlchemy session"""
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)
    session = SessionLocal()
    return session
