class LDPlayerError(Exception):
    """Base exception for LDPlayer errors"""
    pass

class InstanceError(LDPlayerError):
    """Error related to LDPlayer instances"""
    pass

class AppError(LDPlayerError):
    """Error related to app operations"""
    pass