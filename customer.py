class Customer:
    """A simple implementation of a person."""
    def __init__(self, task_time):
        self.task_time = task_time
        self.line_length = 0
        self.wait_time = 0

    def __repr__(self):
        return "{} ({})".format(self.wait_time, self.task_time)