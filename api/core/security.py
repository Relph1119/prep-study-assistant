from fastapi import Header, HTTPException, status


def get_current_user(authorization: str = Header(...)):
    """
    模拟 token 解析：
    Authorization: Bearer user_id:role
    """
    try:
        _, token = authorization.split()
        user_id, role = token.split(":")
        return {
            "user_id": int(user_id),
            "role": role,
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
