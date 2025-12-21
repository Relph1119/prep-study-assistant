from typing import Optional
from api.models.user import User


# 模拟数据库
_FAKE_USERS = {
    1: User(1, "admin", "管理员", "admin"),
    2: User(2, "test_user", "小明", "user"),
}


class UserRepository:
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        return _FAKE_USERS.get(user_id)
