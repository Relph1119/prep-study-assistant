from fastapi import APIRouter, Depends, HTTPException, status
from api.schemas.user import UserOut
from api.repository.user_repo import UserRepository
from api.core.security import get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/{user_id}", response_model=UserOut)
def get_user_detail(
    user_id: int,
    current_user: dict = Depends(get_current_user),
):
    # 权限校验
    if current_user["role"] != "admin" and current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )

    user = UserRepository.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user
