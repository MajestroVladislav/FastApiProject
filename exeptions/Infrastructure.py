class DatabaseError(Exception):
    def __init__(self, message: str = "Database error"):
        self.message = message
        super().__init__(self.message)

class EntityNotFoundError(DatabaseError):
    def __init__(self, entity_name: str, entity_id: int, message: str = None):
        self.entity_name = entity_name
        self.entity_id = entity_id
        if not message:
            message = f"{entity_name} with id {entity_id} not found"
        super().__init__(message)
        self.entity_name = entity_name
        self.entity_id = entity_id