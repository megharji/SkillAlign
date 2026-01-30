from fastapi import HTTPException
from typing import Any, Optional


def ResponseModel(
    *,
    status_code: int = 200,
    status: str = "success",
    message: str = "",
    payload: Optional[Any] = None
):
    return {
        "status_code": status_code,
        "status": status,
        "message": message,
        "data": payload
    }


def Http_Exception(
    *,
    status_code: int = 400,
    status: str = "error",
    message: str = "Something went wrong"
):
    raise HTTPException(
        status_code=status_code,
        detail={
            "status": status,
            "message": message
        }
    )
    

