class StageAlreadyCompletedError(Exception):
    """Raised when advancing or running a work item that is already DONE"""
