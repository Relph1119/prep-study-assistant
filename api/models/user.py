from datetime import datetime


class User:
    def __init__(
        self,
        id: int,
        username: str,
        nickname: str,
        role: str,
        is_active: bool = True,
    ):
        self.id = id
        self.username = username
        self.nickname = nickname
        self.role = role
        self.is_active = is_active
        self.created_at = datetime.utcnow()
