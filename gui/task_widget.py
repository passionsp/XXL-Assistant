"""任务列表项组件。"""

class TaskWidget:
    def __init__(self, task):
        self.task = task

    def render(self):
        raise NotImplementedError
