#!/usr/bin/python3
from sqlalchemy import Column, String, TEXT, Integer, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, cast
from sqlalchemy.dialects import postgresql

from . import Base, BaseModel, create_tsvector


class User(BaseModel, Base):
    """User model class with fields and full-text search vectors"""
    __tablename__ = 'users'
    email = Column(String(320), nullable=False, unique=True, index=True)
    name = Column(String(64))
    bio = Column(String(384), default='')
    profile_picture_id = Column(TEXT, nullable=False, default='')
    hashed_password = Column(TEXT, nullable=False)
    signin_trials = Column(Integer, nullable=False, default=0)
    user_active = Column(Boolean, default=True)
    user_reset_token = Column(TEXT, nullable=True, default='')
    posts = relationship('Post', cascade='all, delete, delete-orphan',
                         backref='user')
    comments = relationship('Comment', cascade='all, delete, delete-orphan',
                            backref='user')
    __ts_name__ = create_tsvector(
        cast(func.coalesce(name, ''), postgresql.TEXT))
    __ts_bio__ = create_tsvector(
        cast(func.coalesce(bio, ''), postgresql.TEXT))
    __table_args__ = (
        Index('idx_user_name_tsv', __ts_name__, postgresql_using='gin'),
        Index('idx_user_bio_tsv', __ts_bio__, postgresql_using='gin')
    )
