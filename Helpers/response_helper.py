
import time
from typing import Any


def send_success_response(
    data: Any = None,
    code: int = 200,
    success: bool = True,
    msg: str = "Success"
) -> dict:
    return {
        "code": code,
        "success": success,
        "data": data if data is not None else {},
        "msg": msg,
        "time": int(time.time())
    }


def send_success_paginate_response(
    data: Any = None,
    current_page: int = 1,
    last_page: int = 1,
    per_page: int = 10,
    total: int = 0,
    code: int = 200,
    success: bool = True,
    msg: str = "Success"
) -> dict:
    return {
        "code": code,
        "success": success,
        "data": data if data is not None else [],
        "meta": {
            "current_page": current_page,
            "last_page": last_page,
            "per_page": per_page,
            "total": total
        },
        "msg": msg,
        "time": int(time.time())
    }


def valid_pagination(
    per_page: int,
    page: int,
    max_per_page: int = 100
) -> bool:
    return 1 <= per_page <= max_per_page and page >= 1
