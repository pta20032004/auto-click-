class CoordinateOutOfBoundError(Exception):
    """
    Exception raised when coordinates are outside the viewport boundaries.
    """
    def __init__(self, x, y, viewport_width, viewport_height):
        self.x = x
        self.y = y
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        super().__init__(
            f"Coordinate ({x}, {y}) is out of viewport bounds "
            f"({viewport_width}x{viewport_height})."
        )

class ActionNotFoundError(Exception):
    """
    Exception raised when a workflow action is not implemented.
    """
    def __init__(self, action_name):
        self.action_name = action_name
        super().__init__(f"Action '{action_name}' is not defined in the automation engine.")