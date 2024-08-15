#!/usr/bin/python3
"""Module for managing endpoints for user connections"""
import re
import uuid
from fastapi import APIRouter
from sqlalchemy import and_
from datetime import datetime

from ..utils.token_mgt import AuthTokenMngr
from ..database import get_session, User, UserFollowing
from ..utils.pagination import paginate_list
from ..form_types import ConnectionSchema


endpoint = APIRouter(prefix='/api/v1')


@endpoint.get('/followers')
async def get_user_followers(id='', token='', span='12', after='', before=''):
    """Gets and returns the followers of a specified user."""
    api_response = {
        'success': False,
        'message': 'Unable to retrieve followers.'
    }
    if not id:
        return api_response
    auth_token = AuthTokenMngr.convert_token(token)
    curruser_id = auth_token.user_id if auth_token else None
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
        usrflwrs = db_session.query(UserFollowing).filter(
            UserFollowing.following_id == id
        ).all()
        usrflwrs_data = []
        if usrflwrs:
            for usrflwr in usrflwrs:
                user = db_session.query(User).filter(
                    User.id == usrflwr.follower_id
                ).first()
                if not user:
                    continue
                currusrctn = db_session.query(UserFollowing).filter(and_(
                    UserFollowing.follower_id == curruser_id,
                    UserFollowing.following_id == user.id
                )).first()
                flwr_info = {
                    'id': user.id,
                    'name': user.name,
                    'profielPictureId': user.profile_picture_id,
                    'isFollowing': currusrctn is not None
                }
                usrflwrs_data.append(flwr_info)
        api_response = {
            'success': True,
            'data': paginate_list(
                usrflwrs_data,
                span,
                after,
                before,
                True,
                lambda x: x['id']
            )
        }
    finally:
        db_session.close()
    return api_response


@endpoint.get('/followings')
async def get_user_followings(id='', token='', span='12', after='', before=''):
    """Gets and returns users followed by a given user"""
    api_response = {
        'success': False,
        'message': 'Unable to find users followings.'
    }
    if not id:
        return api_response
    auth_token = AuthTokenMngr.convert_token(token)
    currusr_id = auth_token.user_id if auth_token else None
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
        usrflwngs = db_session.query(UserFollowing).filter(
            UserFollowing.follower_id == id
        ).all()
        usrflwngs_data = []
        if usrflwngs:
            for usrflwng in usrflwngs:
                user = db_session.query(User).filter(
                    User.id == usrflwng.following_id
                ).first()
                if not user:
                    continue
                currusrctn = db_session.query(UserFollowing).filter(and_(
                    UserFollowing.follower_id == currusr_id,
                    UserFollowing.following_id == user.id
                )).first()
                flwng_info = {
                    'id': user.id,
                    'name': user.name,
                    'profilePictureId': user.profile_picture_id,
                    'isFollowing': currusrctn is not None
                }
                usrflwngs_data.append(flwng_info)
        api_response = {
            'success': True,
            'data': paginate_list(
                usrflwngs_data,
                span,
                after,
                before,
                False,
                lambda x: x['id']
            )
        }
    finally:
        db_session.close()
    return api_response


@endpoint.put('/follow')
async def toggle_user_follow(body: ConnectionSchema):
    """Toggle the follow status between users"""
    api_response = {
        'success': False,
        'message': 'Unable to follow user.'
    }
    auth_token = AuthTokenMngr.convert_token(body.authToken)
    invalid_conds = [
        auth_token is None,
        auth_token is not None and (auth_token.user_id != body.userId),
        body.userId == body.followId
    ]
    if any(invalid_conds):
        return api_response
    db_session = get_session()
    try:
        currusrctn = db_session.query(UserFollowing).filter(and_(
            UserFollowing.follower_id == auth_token.user_id,
            UserFollowing.following_id == body.followId
        )).first()
        if currusrctn:
            db_session.query(UserFollowing).filter(and_(
                UserFollowing.follower_id == auth_token.user_id,
                UserFollowing.following_id == body.followId
            )).delete(
                synchronize_session=False
            )
            db_session.commit()
            api_response = {
                'success': True,
                'data': {'status': False}
            }
        else:
            new_ctn = UserFollowing(
                id=str(uuid.uuid4()),
                created_on=datetime.utcnow(),
                follower_id=body.userId,
                following_id=body.followId
            )
            db_session.add(new_ctn)
            db_session.commit()
            api_response = {
                'success': True,
                'data': {'status': True}
            }
    except Exception as ex:
        print(ex.args[0])
        db_session.rollback()
    finally:
        db_session.close()
    return api_response
