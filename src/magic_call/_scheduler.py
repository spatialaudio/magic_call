"""An abstraction around concurrent.futures.ThreadPoolExecutor."""
from concurrent.futures import ThreadPoolExecutor


class Task:
    pass


class Scheduler:

    def __init__(self, max_workers=None):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def list_of_futures2future_of_list(self, futures):
        return self.executor.submit(
                lambda futures: [f.result() for f in futures],
                futures)

    def create_task(self, function, *args, **kwargs):
        """

        *args are passed to function ("task" is passed as first argument)

        **kwargs are assigned as attributes to "task"

        """
        # NB: Using circular dependencies will cause deadlock!
        # TODO: dataclass?
        task = Task()
        for k, v in kwargs.items():
            setattr(task, k, v)
        assert not hasattr(task, 'future')
        task.future = self.executor.submit(wrap_task, function, task, *args)
        return task


def wrap_task(function, task, *args, **kwargs):
    assert not hasattr(task, '_dependencies')
    task._dependencies = []
    assert '_dependencies' not in kwargs
    for arg in args:
        if not isinstance(arg, Task):
            continue
        # NB: This waits until all dependencies are done, but it also forces
        #     exceptions to show themselves (for easier debugging).
        arg.future.result()  # The result itself is discarded
        task._dependencies.append(arg)  # Keep dependencies alive
    return function(task, *args)
