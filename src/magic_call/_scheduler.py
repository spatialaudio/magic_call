"""An abstraction around `concurrent.futures.ThreadPoolExecutor`."""
from concurrent.futures import ThreadPoolExecutor as _ThreadPoolExecutor


class Task:
    pass


class Scheduler:

    def __init__(self, max_workers=None):
        self._executor = _ThreadPoolExecutor(max_workers=max_workers)

    def create_task(self, function, *args, **attrs):
        """

        ``*args`` are passed to function ("task" is passed as first argument)

        ``**attrs`` are assigned as attributes to "task"

        """
        # NB: Using circular dependencies will cause deadlock!
        # TODO: dataclass?
        task = Task()
        assert '_dependencies' not in attrs
        for k, v in attrs.items():
            setattr(task, k, v)
        assert not hasattr(task, 'future')
        task.future = self._executor.submit(_wrapper, function, task, *args)
        return task


def _wrapper(function, task, *args):
    # TODO: handle keeping dependencies alive with weak references?
    assert not hasattr(task, '_dependencies')
    task._dependencies = []
    for arg in args:
        if not isinstance(arg, Task):
            continue
        # NB: This waits until all dependencies are done, but it also forces
        #     exceptions to show themselves (for easier debugging).
        arg.future.result()  # The result itself is discarded
        task._dependencies.append(arg)  # Keep dependencies alive
    return function(task, *args)
