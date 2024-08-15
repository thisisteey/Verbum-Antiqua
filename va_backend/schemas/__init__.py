#!/usr/bin/python3
"""Module for base model and utility functions"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, TIMESTAMP, String
from datetime import datetime
from sqlalchemy.sql import func, text


Base = declarative_base()


class BaseModel:
    """Base model class with common attributes"""
    id = Column(String(64), unique=True, nullable=False, primary_key=True)
    created_on = Column(TIMESTAMP(True), nullable=False,
                        default=datetime.utcnow())
    updated_on = Column(TIMESTAMP(True), nullable=False,
                        default=datetime.utcnow(), onupdate=datetime.utcnow())

    def __init__(self, **kwargs):
        """Initialize the base model with given attributes"""
        for key, val in kwargs.items():
            setattr(self, key, val)


def create_tsvector(*columns):
    """Create a TSVector column for full-text search"""
    tsvector_exp = columns[0]
    for col in columns[1:]:
        tsvector_exp = func.concat(tsvector_exp, ' ', col)
    return func.to_tsvector(text("'english'"), tsvector_exp)
