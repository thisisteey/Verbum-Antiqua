#!/usr/bin/python3
"""Module for search endpoints, handling posts and user queries"""
import json
import re
from fastapi import APIRouter
from typing import List
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError

from ..database import (
    get_session, User, Comment, Post, PostLike, UserFollowing)
from ..utils.token_mgt import AuthTokenMngr
from ..utils.pagination import paginate_list


endpoint = APIRouter(prefix='/api/v1')


def unique_posts(
        posts: List[Post], posts_seen: List[str], db_session, user_id):
    """Gets and returns a list of uniques posts with user data"""
    results = []
    for post in posts:
        if post.id in posts_seen:
            continue
        posts_seen.append(post.id)
        user = db_session.query(User).filter(User.id == post.user_id).first()
        if not user:
            continue
        comments = db_session.query(Comment).filter(and_(
            Comment.post_id == post.id,
            Comment.comment_id == None
        )).all()
        comments_cnt = len(comments) if comments else 0
        likes = db_session.query(PostLike).filter(
            PostLike.post_id == post.id
        ).all()
        likes_cnt = len(likes) if likes else 0
        is_liked_by_user = False
        if user_id:
            post_dits = db_session.query(PostLike).filter(and_(
                PostLike.post_id == post.id,
                PostLike.user_id == user_id
            )).first()
            if post_dits:
                is_liked_by_user = True
        post_info = {
            'user': {
                'id': user.id,
                'name': user.name,
                'profilePictureId': user.profile_picture_id
            },
            'id': post.id,
            'title': post.title,
            'publishedOn': post.created_on.isoformat(),
            'quotes': json.JSONDecoder().decode(post.content),
            'commentsCount': comments_cnt,
            'likesCount': likes_cnt,
            'isLiked': is_liked_by_user
        }
        results.append(post_info)
    return results


def unique_users(
        users: List[User], users_seen: List[str], db_session, user_id):
    """Gets and returns a list of unique users with following status"""
    results = []
    for user in users:
        if user.id in users_seen:
            continue
        users_seen.append(user.id)
        is_following = False
        if user_id:
            user_ctn = db_session.query(UserFollowing).filter(and_(
                UserFollowing.follower_id == user_id,
                UserFollowing.following_id == user.id
            )).first()
            if user_ctn:
                is_following = True
        user_info = {
            'id': user.id,
            'name': user.name,
            'profilePictureId': user.profile_picture_id,
            'isFollowing': is_following
        }
        results.append(user_info)
    return results


@endpoint.get('/search-posts')
async def search_posts(q='', token='', span='', after='', before=''):
    """Search and find posts based on query string and filters"""
    api_response = {
        'success': False,
        'message': 'Posts search failed.'
    }
    auth_token = AuthTokenMngr.convert_token(token)
    user_id = auth_token.user_id if auth_token is not None else None
    db_session = get_session()
    try:
        span = span.strip()
        if span and re.fullmatch(r'\d+', span) is None:
            api_response = {
                'success': False,
                'message': 'Invalid span type.'
            }
            return api_response
        span = int(span if span else '12')
        query = q.replace('"', '')
        query = query.replace('\'', '').strip()
        if not query:
            return api_response
        query = re.sub(r'\s+', '&', query)
        content_search_res = db_session.query(Post).filter(
            Post.__ts_content__.match(query, postgresql_regconfig='english')
        ).all()
        title_search_res = db_session.query(Post).filter(
            Post.__ts_title__.match(query, postgresql_regconfig='english')
        ).all()
        posts_found = []
        posts_seen_ids = []
        if content_search_res:
            posts_found.extend(
                unique_posts(
                    content_search_res,
                    posts_seen_ids,
                    db_session,
                    user_id
                )
            )
        if title_search_res:
            posts_found.extend(
                unique_posts(
                    title_search_res,
                    posts_seen_ids,
                    db_session,
                    user_id
                )
            )
        api_response = {
            'success': True,
            'data': paginate_list(
                posts_found,
                span,
                after,
                before,
                True,
                lambda x: x['id']
            )
        }
    except SQLAlchemyError:
        api_response = {
            'success': False,
            'message': 'Invalid search query.'
        }
    finally:
        db_session.close()
    return api_response


@endpoint.get('/search-people')
async def search_users(q='', token='', span='', after='', before=''):
    """Search and find users based on query string and filters"""
    api_response = {
        'success': False,
        'message': 'Users search failed.'
    }
    auth_token = AuthTokenMngr.convert_token(token)
    user_id = auth_token.user_id if auth_token is not None else None
    db_session = get_session()
    try:
        span = span.strip()
        if span and re.fullmatch(r'\d+', span) is None:
            api_response = {
                'success': False,
                'message': 'Invalid span type.'
            }
            db_session.close()
            return api_response
        span = int(span if span else '12')
        query = q.replace('"', '')
        query = query.replace('\'', '').strip()
        if not query:
            return api_response
        query = re.sub(r'\s+', '&', query)
        name_search_res = db_session.query(User).filter(
            User.__ts_name__.match(query, postgresql_regconfig='english')
        ).all()
        bio_search_res = db_session.query(User).filter(
            User.__ts_bio__.match(query, postgresql_regconfig='english')
        ).all()
        bio_search_res = []
        users_found = []
        users_seen_ids = []
        if name_search_res:
            users_found.extend(
                unique_users(
                    name_search_res,
                    users_seen_ids,
                    db_session,
                    user_id
                )
            )
        if bio_search_res:
            users_found.extend(
                unique_users(
                    bio_search_res,
                    users_seen_ids,
                    db_session,
                    user_id
                )
            )
        api_response = {
            'success': True,
            'data': paginate_list(
                users_found,
                span,
                after,
                before,
                True,
                lambda x: x['id']
            )
        }
    except SQLAlchemyError:
        api_response = {
            'success': False,
            'message': 'Invalid search query.'
        }
    finally:
        db_session.close()
    return api_response
