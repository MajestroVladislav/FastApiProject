class UserNotFoundError(Exception):
    """Raised when a user is not found."""
    def __init__(self, user_id: int, message: str = None):
        if not message:
            message = f"User with id {user_id} not found"
        super().__init__(message)
        self.user_id = user_id

class CategoryNotFoundError(Exception):
    """Raised when a category is not found."""
    def __init__(self, category_id: int, message: str = None):
        if not message:
            message = f"Category with id {category_id} not found"
        super().__init__(message)
        self.category_id = category_id

class LocationNotFoundError(Exception):
    """Raised when a location is not found."""
    def __init__(self, location_id: int, message: str = None):
        if not message:
            message = f"Location with id {location_id} not found"
        super().__init__(message)
        self.location_id = location_id