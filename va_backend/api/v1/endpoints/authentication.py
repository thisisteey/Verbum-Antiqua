#!/usr/bin/python3
"""Module for handling user authentication endpoints"""
import os
import email_validator
import argon2
import uuid
from fastapi import APIRouter
from datetime import datetime
from sqlalchemy import and_

from ..form_types import (
    SignInSchema,
    SignUpSchema,
    PasswordResetSchema,
    PasswordResetRequestSchema
)
from ..database import get_session, User
from ..utils.token_mgt import AuthTokenMngr, ResetTokenMngr
from ..utils.html_template_renderer import render_html_template
from ..utils.mailing import deliver_message


endpoint = APIRouter(prefix='/api/v1')


@endpoint.post('/sign-in')
async def sign_in(body: SignInSchema):
    """Authenticate user sign in and generate an auth token"""
    api_response = {
        'success': False,
        'message': 'User authentication failed.'
    }
    db_session = get_session()
    try:
        email_validator.validate_email(body.email)
        user = db_session.query(User).filter(User.email == body.email).first()
        if user:
            max_attempts = int(os.getenv('APP_MAX_SIGNIN'))
            try:
                if user.signin_trials >= max_attempts:
                    return api_response
                pwdhash = argon2.PasswordHasher()
                pwdhash.verify(user.hashed_password, body.password)
                if user.signin_trials > 1:
                    db_session.query(User).filter(
                        User.email == body.email
                    ).update(
                        {
                            User.updated_on: datetime.utcnow(),
                            User.signin_trials: 1
                        },
                        synchronize_session=False
                    )
                    db_session.commit()
                auth_token = AuthTokenMngr(
                    user_id=user.id,
                    email=user.email,
                    secure_text=user.hashed_password
                )
                api_response = {
                    'success': True,
                    'data': {
                        'userId': user.id,
                        'name': user.name,
                        'authToken': AuthTokenMngr.deconvert_token(auth_token)
                    }
                }
            except argon2.exceptions.VerificationError:
                account_active = user.user_active
                if user.signin_trials + 1 == max_attempts:
                    account_active = False
                db_session.query(User).filter(User.email == body.email).update(
                    {
                        User.updated_on: datetime.utcnow(),
                        User.signin_trials: user.signin_trials + 1,
                        User.user_active: account_active
                    },
                    synchronize_session=False
                )
                db_session.commit()
                if not account_active:
                    deliver_message(
                        body.email,
                        'Your account has been locked',
                        render_html_template(
                            'account_locked',
                            name=user.name
                        )
                    )
    except Exception as ex:
        print(ex.args[0])
        db_session.rollback()
    finally:
        db_session.close()
    return api_response


@endpoint.post('/sign-up')
async def sign_up(body: SignUpSchema):
    """Register new user and send welcome email"""
    api_response = {
        'success': False,
        'message': 'User account creation failed.'
    }
    try:
        email_validator.validate_email(body.email)
        if len(body.name) > 64:
            api_response['message'] = 'User name is too long.'
            return api_response
        db_session = get_session()
        pwdhash = argon2.PasswordHasher()
        try:
            deliver_message(
                body.email,
                'Welcome to Verbum Antiqua',
                render_html_template(
                    'welcome',
                    name=body.name
                )
            )
            phash = pwdhash.hash(body.password)
            gen_id = str(uuid.uuid4())
            currtime = datetime.utcnow()
            new_user = User(
                id=gen_id,
                created_on=currtime,
                updated_on=currtime,
                name=body.name,
                email=body.email,
                hashed_password=phash
            )
            db_session.add(new_user)
            db_session.commit()
            auth_token = AuthTokenMngr(
                user_id=gen_id,
                email=body.email,
                secure_text=phash
            )
            api_response = {
                'success': True,
                'data': {
                    'userId': gen_id,
                    'name': body.name,
                    'authToken': AuthTokenMngr.deconvert_token(auth_token)
                }
            }
        except Exception as ex:
            print(ex.args[0])
            db_session.rollback()
            api_response = {
                'success': False,
                'message': 'User account creation failed.'
            }
        db_session.close()
    except email_validator.EmailNotValidError:
        api_response['message'] = 'Invalid email.'
    return api_response


@endpoint.post('/reset-password')
async def request_reset_password(body: PasswordResetRequestSchema):
    """Generate a password reset token and send reset email"""
    api_response = {
        'success': False,
        'message': 'Reset token creation failed.'
    }
    db_session = get_session()
    try:
        email_validator.validate_email(body.email)
        qryres = db_session.query(User).filter(
            User.email == body.email
        ).first()
        if qryres:
            reset_token = ResetTokenMngr(
                user_id=qryres.user_id,
                email=body.email,
                message='password_reset'
            )
            reset_token_str = ResetTokenMngr.deconvert_token(reset_token)
            db_session.query(User).filter(and_(
                User.id == qryres.user_id,
                User.email == body.email
            )).update(
                {
                    User.user_reset_token: reset_token_str
                },
                synchronize_session=False
            )
            db_session.commit()
            api_response = {
                'success': True,
                'data': {}
            }
            deliver_message(
                body.email,
                'Reset Your Password',
                render_html_template(
                    'password_reset',
                    name=qryres.name,
                    token=reset_token_str
                )
            )
    except Exception as ex:
        print(ex.args[0])
        db_session.rollback()
    finally:
        db_session.close()
    return api_response


@endpoint.put('/reset-password')
async def reset_password(body: PasswordResetSchema):
    """Update user password using reset token"""
    api_response = {
        'success': False,
        'message': 'Password reset failed.'
    }
    db_session = get_session()
    try:
        email_validator.validate_email(body.email)
        user = db_session.query(User).filter(
            User.email == body.email
        ).first()
        reset_token = ResetTokenMngr.convert_token(body.resetToken)
        if not reset_token:
            return api_response
        if reset_token.has_expired():
            api_response = {
                'success': False,
                'message': 'Password reset token has expired.'
            }
            return api_response
        valid_conds = [
            reset_token.email == body.email,
            len(body.password.strip()) > 8,
            reset_token.message == 'password_reset'
        ]
        if all(valid_conds):
            pwdhash = argon2.PasswordHasher()
            phash = pwdhash(body.password)
            db_session.query(User).filter(
                User.email == body.email
            ).update(
                {
                    User.hashed_password: phash,
                    User.user_reset_token: '',
                    User.signin_trials: 1
                },
                synchronize_session=False
            )
            db_session.commit()
            auth_token = AuthTokenMngr(
                user_id=user.id,
                email=body.email,
                secure_text=phash
            )
            api_response = {
                'success': True,
                'data': {
                    'userId': user.id,
                    'name': user.name,
                    'authToken': AuthTokenMngr.deconvert_token(auth_token)
                }
            }
            deliver_message(
                body.email,
                'Your Password Has Been Changed',
                render_html_template(
                    'password_changed',
                    name=user.name
                )
            )
    except Exception as ex:
        print(ex.args[0])
        db_session.rollback()
    finally:
        db_session.close()
    return api_response
