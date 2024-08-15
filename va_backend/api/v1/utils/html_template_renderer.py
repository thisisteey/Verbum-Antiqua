#!/usr/bin/python3
"""Module for rendering HTML templates with dynamic content"""
import os
from jinja2 import Template


def render_html_template(template_name, **context):
    """Generates an HTML string from a template and context"""
    template_path = os.path.join(
        'api', 'v1', 'templates', f'{template_name}.html'
    )
    rendered_html = ''
    if os.path.isfile(template_path):
        frontend_domain = os.getenv('FRONTEND_DOMAIN')
        context['frontend_domain'] = frontend_domain
        with open(template_path) as file:
            doc = Template(file.read())
            rendered_html = doc.render(**context)
    return rendered_html
