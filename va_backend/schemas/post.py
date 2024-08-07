#!/usr/bin/python3
"""Module for Post Model schema for database representation"""
from sqlalchemy import Column, String, ForeignKey, TEXT, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import cast, func
from sqlalchemy.dialects import postgresql

from . import Base, BaseModel, create_tsvector


class Post(BaseModel, Base):
    """Post model class for the database"""
    __tablename__ = 'posts'
    user_id = Column(String(64), ForeignKey('users.id'), nullable=False)
    title = Column(String(256), nullable=False, default='', index=True)
    content = Column(TEXT, nullable=False, index=True)
    comments = relationship('Comment', cascade='all, delete, delete-orphan',
                            backref='post')
    likes = relationship('PostLike', cascade='all, delete, delete-orphan',
                         backref='post')
    __ts_content__ = create_tsvector(
        cast(func.coalesce(content, ''), postgresql.TEXT))
    __ts_title__ = create_tsvector(
        cast(func.coalesce(title, ''), postgresql.TEXT))
    __table_args__ = (
        Index('idx_post_text_tsv', __ts_content__, postgresql_using='gin'),
        Index('idx_post_title_tsv', __ts_title__, postgresql_using='gin')
    )
