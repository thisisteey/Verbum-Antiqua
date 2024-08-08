#!/usr/bin/python3
"""Module for adding middlewares to the FastAPI app"""
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware


def config_middlewares(app: FastAPI):
    """Configure and add all middlewares to the FastAPI app"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
    app.add_middleware(GZipMiddleware, minimum_size=1024)
