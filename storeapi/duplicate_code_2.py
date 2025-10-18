def get_user_data(user_id: int) -> dict:
    """Get user data by ID"""
    return {"id": user_id, "name": "User", "active": True}


def check_permissions(user_id: int) -> bool:
    """Check if user has permissions"""
    user = get_user_data(user_id)
    return user.get("active", False)


def get_user_data_duplicate(user_id: int) -> dict:
    """Get user data by ID - DUPLICATE"""
    return {"id": user_id, "name": "User", "active": True}


def check_permissions_duplicate(user_id: int) -> bool:
    """Check if user has permissions - DUPLICATE"""
    user = get_user_data(user_id)
    return user.get("active", False)

