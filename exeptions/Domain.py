class UserNotFoundError(Exception):
    def __init__(self, user_id: int, message: str = None):
        if not message:
            message = f"User with id {user_id} not found"
        super().__init__(message)
        self.user_id = user_id

class PostNotFoundError(Exception):
    def __init__(self, post_id: int, message: str = None):
        if not message:
            message = f"Post with id {post_id} not found"
        super().__init__(message)
        self.post_id = post_id

class CategoryNotFoundError(Exception):
    def __init__(self, category_id: int, message: str = None):
        if not message:
            message = f"Category with id {category_id} not found"
        super().__init__(message)
        self.category_id = category_id

class LocationNotFoundError(Exception):
    def __init__(self, location_id: int, message: str = None):
        if not message:
            message = f"Location with id {location_id} not found"
        super().__init__(message)
        self.location_id = location_id

class WrongUserError(Exception):
    def __init__(self, message: str = None):
        if not message:
            message = f"Access denied, invalid user for this operation."
        super().__init__(message)