#!/usr/bin/python3
"""Module containing data models for various API requests"""
from pydantic import BaseModel
from typing import Optional, List


class SignInSchema(BaseModel):
    """Schema for user sign in"""
    email: str
    password: str


class SignUpSchema(BaseModel):
    """Schema for user registration"""
    name: str
    email: str
    password: str


class PasswordResetRequestSchema(BaseModel):
    """Schema for requesting a password reset"""
    email: str


class PasswordResetSchema(BaseModel):
    """Schema for resetting a password"""
    email: str
    password: str
    resetToken: str


class UserDeleteSchema(BaseModel):
    """Schema for deleting a user account"""
    authToken: str
    userId: str


class UserUpdateSchema(BaseModel):
    """Schema for updating a user profile"""
    authToken: str
    userId: str
    name: str
    profilePicture: Optional[str]
    profilePictureId: str
    removeProfilePicture: bool
    email: str
    bio: str


class ConnectionSchema(BaseModel):
    """Schema for creating a user connection"""
    authToken: str
    userId: str
    followId: str


class PostAddSchema(BaseModel):
    """Schema for adding a new post"""
    authToken: str
    userId: str
    title: str
    quotes: List[str]


class PostUpdateSchema(BaseModel):
    """Schema for updating a post"""
    authToken: str
    userId: str
    postId: str
    title: str
    quotes: List[str]


class PostDeleteSchema(BaseModel):
    """Schema for deleting a post"""
    authToken: str
    userId: str
    postId: str


class PostLikeSchema(BaseModel):
    """Schema for liking a post"""
    authToken: str
    userId: str
    postId: str


class CommentAddSchema(BaseModel):
    """Schema for adding a comment"""
    authToken: str
    userId: str
    postId: str
    content: str
    replyTo: Optional[str]


class CommentDeleteSchema(BaseModel):
    """Schema for deleting a comment"""
    authToken: str
    userId: str
    commentId: str
