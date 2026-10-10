from core.user_roles import UserRoles


class UserData:
    def __init__(self, ID: str, Roles: UserRoles):
        self.ID = ID
        self.Roles = Roles
