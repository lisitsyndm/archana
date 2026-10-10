from enum import Enum


class UserRoles(str, Enum):
    admin = "admin"
    user = "user"
