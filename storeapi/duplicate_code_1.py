def calculate_score(likes: int, dislikes: int) -> float:
    """Calculate video score"""
    if likes + dislikes == 0:
        return 0.0
    return (likes - dislikes) / (likes + dislikes + 1)


def validate_input(data: dict) -> bool:
    """Validate input data"""
    required_fields = ["title", "url"]
    for field in required_fields:
        if field not in data or not data[field]:
            return False
    return True

def calculate_score_duplicate(likes: int, dislikes: int) -> float:
    """Calculate video score - DUPLICATE"""
    if likes + dislikes == 0:
        return 0.0
    return (likes - dislikes) / (likes + dislikes + 1)


def validate_input_duplicate(data: dict) -> bool:
    """Validate input data - DUPLICATE"""
    required_fields = ["title", "url"]
    for field in required_fields:
        if field not in data or not data[field]:
            return False
    return True