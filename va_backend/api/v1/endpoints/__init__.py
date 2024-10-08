#!/usr/bin/python3
"""Module for handling API endpoints"""
import os
from fastapi import APIRouter
from starlette.responses import FileResponse
from imagekitio import ImageKit


home_endpoint = APIRouter()


@home_endpoint.get('/')
@home_endpoint.get('/api')
@home_endpoint.get('/api/v1')
async def get_welcome():
    """Gets and returns the welcome page and message"""
    api_response = {
        'success': True,
        'data': {
            'message': 'Welcome to the Verbum Antiqua API.'
        }
    }
    return api_response


@home_endpoint.get('/favicon')
@home_endpoint.get('/favicon.ico')
async def serve_favicon():
    """Gets and returns the favicon image"""
    favicon_path = 'api/v1/assets/va_logo.png'
    favicon_content = FileResponse(
        path=favicon_path,
        media_type="image/png"
    )
    return favicon_content


@home_endpoint.get('/api/v1/profile-picture')
async def get_profile_picture(img_id: str):
    """Gets and returns the profile picture for a user"""
    imagekit = ImageKit(
        private_key=os.getenv('IMG_CDN_PRIV_KEY'),
        public_key=os.getenv('IMG_CDN_PUB_KEY'),
        url_endpoint=os.getenv('IMG_CDN_URL_ENDPNT')
    )
    api_response = {
        'success': False,
        'message': 'Image ID is required.'
    }
    if not img_id:
        return api_response
    try:
        img_details = imagekit.get_file_details(img_id)
        img_url = ''
        if hasattr(img_details, 'response') and img_details.response:
            img_url = img_details.response.get('url', '')
        else:
            img_url = getattr(img_details, 'url', '')
        if not img_url:
            raise ValueError('Image URL not found in response')
        #else:
        #    raise ValueError('Invalid response from ImageKit')
        #if hasattr(img_details, 'error') and img_details.error:
        #    raise ValueError(img_details.error.get('message', 'Unknown error'))
        #if img_details['response']:
        #    img_url = img_details['response']['url']
        #if img_details['error']:
        #    raise ValueError(img_details['error']['message'])
        api_response = {
            'success': True,
            'data': {
                'url': img_url
            }
        }
    except Exception as exp:
        api_response = {
            'success': False,
            'message': str(exp)
        }
        #print(f"Error: {exp}")
    return api_response
