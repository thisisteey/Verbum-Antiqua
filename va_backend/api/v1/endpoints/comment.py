#!/usr/bin/python3
"""Module for managing endpoints for comments on posts"""
import re
import uuid
from fastapi import APIRouter
from sqlalchemy import and_
from datetime import datetime

from ..database import get_session, User, Comment
from ..utils.pagination import paginate_list
from ..form_types import CommentAddSchema, CommentDeleteSchema
from ..utils.token_mgt import AuthTokenMngr


endpoint = APIRouter(prefix='/api/v1')


@endpoint.get('/comment')
async def get_comment(id=''):
    """Gets and returns details of a specific comment"""
    api_response = {
        'success': False,
        'message': 'Comment not found.'
    }
    db_session = get_session()
    try:
        comment = db_session.query(Comment).filter(Comment.id == id).first()
        if comment:
            user = db_session.query(User).filter(
                User.id == comment.user_id
            ).first()
            if not user:
                return api_response
            cmt_rep = db_session.query(Comment).filter(
                Comment.comment_id == comment.id
            ).all()
            replies_cnt = len(cmt_rep) if cmt_rep else 0
            api_response = {
                'success': True,
                'data': {
                    'id': comment.id,
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'profilePictureId': user.profile_picture_id
                    },
                    'createdOn': comment.created_on.isoformat(),
                    'text': comment.content,
                    'postId': comment.post_id,
                    'repliesCount': replies_cnt,
                    'replyTo': comment.comment_id if comment.comment_id else ''
                }
            }
    finally:
        db_session.close()
    return api_response


@endpoint.get('/comments-of-post')
async def get_post_comments(id='', span='', after='', before=''):
    """Gets and return all comments made under a post"""
    api_response = {
        'success': False,
        'message': 'Comments not found.'
    }
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
        comments = db_session.query(Comment).filter(and_(
            Comment.post_id == id,
            Comment.comment_id == None
        )).all()
        comments_data = []
        if comments:
            for comment in comments:
                user = db_session.query(User).filter(
                    User.id == comment.user_id
                ).first()
                if not user:
                    continue
                cmt_reps = db_session.query(Comment).filter(and_(
                    Comment.post_id == id,
                    Comment.comment_id == comment.id
                )).all()
                replies_cnt = len(cmt_reps) if cmt_reps else 0
                comment_info = {
                    'id': comment.id,
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'profilePictureId': user.profile_picture_id
                    },
                    'createdOn': comment.created_on.isoformat(),
                    'text': comment.content,
                    'postId': comment.post_id,
                    'repliesCount': replies_cnt,
                    'replyTo': comment.comment_id if comment.comment_id else ''
                }
                comments_data.append(comment_info)
        comments_data.sort(
            key=lambda x: datetime.fromisoformat(x['createdOn'])
        )
        api_response = {
            'success': True,
            'data': paginate_list(
                comments_data,
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


@endpoint.get('/comment-replies')
async def get_comment_replies(id='', span='', after='', before=''):
    """Gets and returns the replies to a specific comment"""
    api_response = {
        'success': False,
        'message': 'Replies to comment not found.'
    }
    if not id:
        return api_response
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
        comments = db_session.query(Comment).filter(
            Comment.comment_id == id
        ).all()
        replies_data = []
        if comments:
            for comment in comments:
                user = db_session.query(User).filter(
                    User.id == comment.user_id
                ).first()
                if not user:
                    continue
                cmt_reps = db_session.query(Comment).filter(and_(
                    Comment.post_id == id,
                    Comment.comment_id == comment.id
                )).all()
                replies_cnt = len(cmt_reps) if cmt_reps else 0
                replies_info = {
                    'id': comment.id,
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'profilePictureId': user.profile_pciture_id
                    },
                    'createdOn': comment.created_on.isoformat(),
                    'text': comment.content,
                    'postId': comment.post_id,
                    'repliesCount': replies_cnt,
                    'replyTo': comment.comment_id if comment.comment_id else ''
                }
                replies_data.append(replies_info)
        replies_data.sort(
            key=lambda x: datetime.fromisoformat(x['createdOn'])
        )
        api_response = {
            'success': True,
            'data': paginate_list(
                replies_data,
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


@endpoint.get('/comments-by-user')
async def get_user_comments(id='', span='', after='', before=''):
    """Gets and returns all comments by a specific user"""
    api_response = {
        'success': False,
        'message': 'User id is required.'
    }
    if not id:
        return api_response
    api_response = {
        'success': False,
        'message': 'Comments for the user not found.'
    }
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
        user = db_session.query(User).filter(User.id == id).first()
        if not user:
            return api_response
        comments = db_session.query(Comment).filter(
            Comment.user_id == id
        ).all()
        comments_data = []
        if comments:
            for comment in comments:
                cmt_reps = db_session.query(Comment).filter(
                    Comment.comment_id == comment.id
                ).all()
                replies_cnt = len(cmt_reps) if cmt_reps else 0
                comments_info = {
                    'id': comment.id,
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'profilePictureId': user.profile_picture_id
                    },
                    'createdOn': comment.created_on.isoformat(),
                    'text': comment.content,
                    'postId': comment.post_id,
                    'repliesCount': replies_cnt,
                    'replyTo': comment.comment_id if comment.comment_id else ''
                }
                comments_data.append(comments_info)
        comments_data.sort(
            key=lambda x: datetime.fromisoformat(x['createdOn'])
        )
        api_response = {
            'success': True,
            'data': paginate_list(
                comments_data,
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


@endpoint.post('/comment')
async def create_comment(body: CommentAddSchema):
    """Creates and adds a new comment to a post"""
    api_response = {
        'success': False,
        'message': 'Unable to add comment.'
    }
    auth_token = AuthTokenMngr.convert_token(body.authToken)
    if auth_token is None or auth_token.user_id != body.userId:
        api_response['message'] = 'Invalid authentication token.'
        return api_response
    if len(body.content) > 384:
        api_response['message'] = 'Comment content is too long.'
        return api_response
    db_session = get_session()
    try:
        reply_id = body.replyTo.strip() if body.replyTo else None
        if reply_id:
            qryres = db_session.query(Comment).filter(and_(
                Comment.id == reply_id,
                Comment.comment_id == None
            )).first()
            if not qryres or qryres.post_id != body.postId:
                db_session.close()
                return api_response
        gen_id = str(uuid.uuid4())
        currdt = datetime.utcnow()
        comment = Comment(
            id=gen_id,
            created_on=currdt,
            post_id=body.postId,
            user_id=body.userId,
            comment_id=reply_id,
            content=body.content
        )
        db_session.add(comment)
        db_session.commit()
        api_response = {
            'success': True,
            'data': {
                'id': gen_id,
                'createdOn': currdt.isoformat(),
                'replyTo': body.replyTo if body.replyTo else '',
                'postId': body.postId,
                'repliesCount': 0
            }
        }
    except Exception as ex:
        print(ex.args[0])
        db_session.rollback()
    finally:
        db_session.close()
    return api_response


@endpoint.delete('/comment')
async def delete_comment(body: CommentDeleteSchema):
    """Delete a specific comment from a post"""
    api_response = {
        'success': False,
        'message': 'Unable to delete comment.'
    }
    auth_token = AuthTokenMngr.convert_token(body.authToken)
    if auth_token is None or auth_token.user_id != body.userId:
        api_response['message'] = 'Invalid authentication token.'
        return api_response
    db_session = get_session()
    try:
        db_session.query(Comment).filter(
            Comment.comment_id == body.commentId
        ).delete(
            synchronize_session=False
        )
        db_session.query(Comment).filter(
            Comment.id == body.commentId
        ).delete(
            synchronize_session=False
        )
        db_session.commit()
        api_response = {
            'success': True,
            'data': {}
        }
    finally:
        db_session.close()
    return api_response
