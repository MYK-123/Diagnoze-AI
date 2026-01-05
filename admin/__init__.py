#!/bin/env python3

from auth.users import User
from auth.users import ROLE_ADMIN

def is_user_admin(user: User)-> bool:
    return user.role == ROLE_ADMIN

