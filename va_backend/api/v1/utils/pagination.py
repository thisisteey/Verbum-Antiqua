#!/usr/bin/python3
"""Module for slicing and extracting list segments (paginating responses)"""
import re


def slice_range(range_str: str, items: list):
    """Slices a list based on a specified range string"""
    if range_str is None:
        return items
    span_match = re.fullmatch(
        r'(?P<size>\d+)(?:,(?P<index>\d+))?',
        range_str
    )
    size = int(span_match.group('size'))
    index = 0
    if span_match.group('index') is not None:
        index = int(span_match.group('index'))
    start = size * index
    end = start + size
    return items[start: end]


def paginate_list(items=[], span=12, after=None, before=None,
                  pop_top=False, key_fxn=lambda x: x['id']):
    """Paginates a list of items with optional key-based filtering"""
    result = []
    if after and before:
        return result
    elif after:
        add_item = False
        count = 0
        for item in items:
            if add_item:
                result.append(item)
                count += 1
                if count == span:
                    break
            elif key_fxn(item):
                add_item = True
    elif before:
        count = 0
        for item in items:
            if key_fxn(item):
                break
            else:
                count += 1
        start = count - (span + 1) if count > (span + 1) else 0
        end = count - 1 if count > 1 else 0
        result = items[start:end]
    else:
        result = items[0:span] if pop_top else items[-span:]
    return result
